from __future__ import annotations

import atexit
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, Response, abort, g, jsonify, request, send_from_directory

from chart_layouts import (
    LayoutRevisionConflict,
    delete_chart_layout,
    delete_drawing_template,
    get_chart_layout,
    list_chart_layouts,
    list_drawing_templates,
    save_chart_layout,
    save_drawing_template,
)
from generation import GenerationJobManager
from local_jyotish import LocalJyotishService
from mt5_gateway import Mt5Gateway
from prospective_refresh import ProspectiveArtifactRefreshSupervisor
from repository import AstroRepository
from runtime_diagnostics import RuntimeDiagnostics
from shadow_ledger import ShadowLedgerSupervisor
from workspace_preferences import read_workspace_preferences, update_workspace_preferences


app = Flask(__name__)
repository = AstroRepository()
runtime_diagnostics = RuntimeDiagnostics(
    repository.paths.annotation_db.parent / "logs" / "runtime_diagnostics.jsonl"
)
generation_manager = GenerationJobManager(repository, diagnostics=runtime_diagnostics)
gateway = Mt5Gateway(
    symbol=os.environ.get("GANN_ASTRO_MT5_SYMBOL", "USDJPY"),
    autoconnect=os.environ.get("GANN_ASTRO_MT5_AUTOCONNECT", "1") != "0",
)
gateway.start()
shadow_ledger = ShadowLedgerSupervisor(
    repository,
    gateway,
    autostart=os.environ.get("GANN_ASTRO_SHADOW_AUTOSTART", "1") != "0",
    poll_seconds=float(os.environ.get("GANN_ASTRO_SHADOW_POLL_SECONDS", "30")),
)
prospective_refresh = ProspectiveArtifactRefreshSupervisor(
    repository,
    gateway,
    generation_manager,
    shadow_ledger,
    autostart=os.environ.get("GANN_ASTRO_REFRESH_AUTOSTART", "1") != "0",
    poll_seconds=float(os.environ.get("GANN_ASTRO_REFRESH_POLL_SECONDS", "20")),
    lookback_days=int(os.environ.get("GANN_ASTRO_REFRESH_LOOKBACK_DAYS", "14")),
    close_grace_seconds=int(os.environ.get("GANN_ASTRO_REFRESH_CLOSE_GRACE_SECONDS", "90")),
    diagnostics=runtime_diagnostics,
)
local_jyotish = LocalJyotishService(repository, diagnostics=runtime_diagnostics)
atexit.register(gateway.stop)
atexit.register(generation_manager.stop)
atexit.register(shadow_ledger.stop)
atexit.register(prospective_refresh.stop)


def list_argument(name: str) -> tuple[str, ...]:
    values: list[str] = []
    for raw in request.args.getlist(name):
        values.extend(item.strip() for item in raw.split(",") if item.strip())
    return tuple(dict.fromkeys(values))


def optional_float_argument(name: str) -> float | None:
    value = str(request.args.get(name) or "").strip()
    return float(value) if value else None


def required_offset_datetime(value: Any, label: str) -> datetime:
    text = str(value or "").strip().replace("Z", "+00:00")
    if not text:
        raise ValueError(f"{label} is required")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed


def bool_argument(name: str) -> bool:
    return str(request.args.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def chart_filter_arguments() -> dict[str, Any]:
    return {
        "transit_bodies": list_argument("transitBody"),
        "natal_bodies": list_argument("natalBody"),
        "aspects": list_argument("aspect"),
        "excluded_family_keys": list_argument("excludeFamily"),
        "only_touched": bool_argument("onlyTouched"),
        "min_duration_minutes": optional_float_argument("minDurationMinutes") or 0.0,
        "max_duration_minutes": optional_float_argument("maxDurationMinutes"),
    }


@app.before_request
def start_request_timer() -> None:
    g.runtime_started_at = time.perf_counter()


@app.after_request
def add_headers(response: Any) -> Any:
    started_at = getattr(g, "runtime_started_at", None)
    if (
        started_at is not None
        and request.method != "OPTIONS"
        and not request.path.startswith("/api/runtime-diagnostics")
    ):
        route = request.url_rule.rule if request.url_rule is not None else request.path
        runtime_diagnostics.record(
            f"http:{request.method} {route}",
            (time.perf_counter() - started_at) * 1000,
            ok=response.status_code < 500,
            details={"status": response.status_code},
        )
    response.headers["Access-Control-Allow-Origin"] = os.environ.get(
        "GANN_ASTRO_ALLOWED_ORIGIN", "http://127.0.0.1:5173"
    )
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/api/<path:_path>", methods=["OPTIONS"])
def options_route(_path: str) -> Any:
    return ("", 204)


@app.get("/api/health")
def health() -> Any:
    return jsonify(
        {
            "ok": True,
            "data": repository.health(),
            "mt5": gateway.status(),
            "prospectiveRefresh": prospective_refresh.status(),
        }
    )


@app.get("/api/runtime-diagnostics")
def get_runtime_diagnostics() -> Any:
    return jsonify({"ok": True, "diagnostics": runtime_diagnostics.snapshot()})


@app.post("/api/runtime-diagnostics/frontend")
def record_frontend_diagnostic() -> Any:
    payload = request.get_json(silent=True) or {}
    allowed_names = {
        "app_bootstrap",
        "artifact_activation",
        "chart_apply",
        "chart_initial_render",
        "chart_live_refresh",
        "layout_restore",
    }
    name = str(payload.get("name") or "").strip()
    if name not in allowed_names:
        return jsonify({"ok": False, "error": "Unsupported frontend diagnostic name"}), 400
    try:
        duration_ms = float(payload.get("durationMs"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "durationMs must be numeric"}), 400
    if not 0 <= duration_ms <= 10 * 60 * 1000:
        return jsonify({"ok": False, "error": "durationMs is outside the accepted range"}), 400
    runtime_diagnostics.record(
        f"frontend:{name}",
        duration_ms,
        ok=bool(payload.get("ok", True)),
    )
    return jsonify(
        {
            "ok": True,
            "recorded": name,
            "guardrails": {"executionAllowed": False},
        }
    )


@app.get("/api/mt5/status")
def mt5_status() -> Any:
    return jsonify({"ok": True, "mt5": gateway.status()})


@app.get("/api/workspace-preferences")
def get_workspace_preferences() -> Any:
    return jsonify({"ok": True, "preferences": read_workspace_preferences(repository)})


@app.put("/api/workspace-preferences")
def put_workspace_preferences() -> Any:
    payload = request.get_json(silent=True) or {}
    try:
        preferences = update_workspace_preferences(repository, payload)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify({"ok": True, "preferences": preferences})


@app.get("/api/mt5/bars")
def mt5_bars() -> Any:
    try:
        bars = gateway.bars(
            symbol=request.args.get("symbol", "USDJPY"),
            timeframe=request.args.get("timeframe", "H1"),
            count=int(request.args.get("count", "500")),
        )
        return jsonify({"ok": True, "candles": bars, "mt5": gateway.status()})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.get("/api/mt5/history-snapshots")
def mt5_history_snapshots() -> Any:
    promoted = {
        item.get("sourceSnapshotId"): item["priceSourceId"]
        for item in repository.list_price_sources()
        if item.get("sourceSnapshotId")
    }
    snapshots = gateway.list_history_snapshots(
        repository.paths.market_snapshots_dir, request.args.get("limit", 100)
    )
    for snapshot in snapshots:
        snapshot["promotedPriceSourceId"] = promoted.get(snapshot.get("snapshotId"))
    return jsonify(
        {
            "ok": True,
            "snapshots": snapshots,
        }
    )


@app.post("/api/mt5/history-snapshots")
def create_mt5_history_snapshot() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        snapshot = gateway.save_history_snapshot(
            str(payload.get("symbol") or gateway.symbol),
            str(payload.get("timeframe") or "H1"),
            required_offset_datetime(payload.get("start"), "start"),
            required_offset_datetime(payload.get("end"), "end"),
            repository.paths.market_snapshots_dir,
        )
        return jsonify({"ok": True, "snapshot": snapshot}), 201
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.post("/api/mt5/history-snapshots/<snapshot_id>/promote")
def promote_mt5_history_snapshot(snapshot_id: str) -> Any:
    try:
        payload = request.get_json(force=True, silent=True) or {}
        price_source = repository.promote_history_snapshot(
            snapshot_id,
            str(payload.get("label") or "").strip() or None,
        )
        return jsonify({"ok": True, "priceSource": price_source}), 201
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/price-sources")
def price_sources() -> Any:
    return jsonify({"ok": True, "priceSources": repository.list_price_sources()})


@app.get("/api/parameters/schema")
def parameter_schema() -> Any:
    return jsonify({"ok": True, "schema": repository.parameter_schema()})


@app.get("/api/parameter-profiles")
def parameter_profiles() -> Any:
    return jsonify({"ok": True, "profiles": repository.list_parameter_profiles()})


@app.post("/api/parameter-profiles")
def save_parameter_profile() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        return jsonify({"ok": True, "profile": repository.save_parameter_profile(payload)})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.delete("/api/parameter-profiles/<profile_id>")
def delete_parameter_profile(profile_id: str) -> Any:
    return jsonify({"ok": repository.delete_parameter_profile(profile_id)})


@app.get("/api/chart-layouts")
def chart_layouts() -> Any:
    rows = list_chart_layouts(
        repository,
        workspace_kind=request.args.get("workspaceKind"),
        symbol=request.args.get("symbol"),
        timeframe=request.args.get("timeframe"),
        family_key=request.args.get("familyKey"),
    )
    return jsonify({"ok": True, "layouts": rows})


@app.get("/api/chart-layouts/<layout_id>")
def chart_layout(layout_id: str) -> Any:
    try:
        return jsonify({"ok": True, "layout": get_chart_layout(repository, layout_id)})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404


@app.post("/api/chart-layouts")
def upsert_chart_layout() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        layout = save_chart_layout(repository, payload)
        return jsonify({"ok": True, "layout": layout}), 201
    except LayoutRevisionConflict as exc:
        return jsonify({"ok": False, "error": str(exc)}), 409
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.delete("/api/chart-layouts/<layout_id>")
def remove_chart_layout(layout_id: str) -> Any:
    deleted = delete_chart_layout(repository, layout_id)
    return jsonify({"ok": deleted}), 200 if deleted else 404


@app.get("/api/drawing-templates")
def drawing_templates() -> Any:
    return jsonify({"ok": True, "templates": list_drawing_templates(repository)})


@app.post("/api/drawing-templates")
def upsert_drawing_template() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        template = save_drawing_template(repository, payload)
        return jsonify({"ok": True, "template": template}), 201
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.delete("/api/drawing-templates/<template_id>")
def remove_drawing_template(template_id: str) -> Any:
    deleted = delete_drawing_template(repository, template_id)
    return jsonify({"ok": deleted}), 200 if deleted else 404


@app.get("/api/generation/jobs")
def generation_jobs() -> Any:
    return jsonify({"ok": True, "jobs": generation_manager.list_jobs(request.args.get("limit", 30))})


@app.get("/api/generation/jobs/<job_id>")
def generation_job(job_id: str) -> Any:
    try:
        return jsonify({"ok": True, "job": generation_manager.get_job(job_id)})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404


@app.post("/api/generation/jobs")
def create_generation_job() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        return jsonify({"ok": True, "job": generation_manager.create_job(payload)})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/generation/jobs/<job_id>/cancel")
def cancel_generation_job(job_id: str) -> Any:
    try:
        return jsonify({"ok": True, "job": generation_manager.cancel_job(job_id)})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404


@app.get("/api/data-artifacts")
def data_artifacts() -> Any:
    return jsonify({"ok": True, "artifacts": repository.list_data_artifacts()})


@app.post("/api/data-artifacts/<artifact_id>/activate")
def activate_data_artifact(artifact_id: str) -> Any:
    try:
        return jsonify({"ok": True, "artifact": repository.activate_artifact(artifact_id)})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/chart")
def chart() -> Any:
    try:
        symbol = request.args.get("symbol", "USDJPY")
        timeframe = request.args.get("timeframe", "H1")
        source = str(request.args.get("source") or "research").strip().lower()
        filters = chart_filter_arguments()
        if source == "live":
            bars = gateway.bars(
                symbol=symbol,
                timeframe=timeframe,
                count=int(request.args.get("liveBarCount", "500")),
            )
            start_iso = datetime.fromtimestamp(bars[0]["time"], tz=timezone.utc).isoformat()
            end_iso = datetime.fromtimestamp(bars[-1]["time"], tz=timezone.utc).isoformat()
            if symbol.upper() == "USDJPY":
                payload = repository.chart_payload(
                    start=start_iso,
                    end=end_iso,
                    symbol=symbol,
                    timeframe=timeframe,
                    **filters,
                )
            else:
                payload = {
                    "symbol": symbol.upper(),
                    "timeframe": timeframe.upper(),
                    "start": start_iso,
                    "end": end_iso,
                    "aspects": [],
                    "srLines": [],
                    "astronomyContract": "NO_CORRECTED_EVENT_SOURCE_FOR_SYMBOL",
                    "parametersApplied": filters,
                    "artifact": {
                        "artifactId": f"live:{symbol.upper()}",
                        "label": f"MT5 live {symbol.upper()}",
                        "symbol": symbol.upper(),
                        "mode": "TN",
                        "sourceTimeframe": timeframe.upper(),
                        "eventsPath": "",
                        "touchLogPath": "",
                        "pricePath": "MT5",
                        "parameters": {},
                        "astronomyContract": "NO_CORRECTED_EVENT_SOURCE_FOR_SYMBOL",
                        "eventCount": 0,
                        "touchCount": 0,
                        "dateStart": start_iso,
                        "dateEnd": end_iso,
                        "isActive": True,
                        "createdAtUtc": None,
                        "builtIn": True,
                    },
                }
            payload["candles"] = bars
            payload["dataSource"] = "mt5_live"
            payload["generatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            return jsonify({"ok": True, "chart": payload})
        payload = repository.chart_payload(
            start=request.args.get("start"),
            end=request.args.get("end"),
            symbol=symbol,
            timeframe=timeframe,
            **filters,
        )
        return jsonify({"ok": True, "chart": payload})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/families/<path:family_key>")
def family(family_key: str) -> Any:
    try:
        payload = repository.family_payload(family_key, request.args.get("eventId"))
        return jsonify({"ok": True, "family": payload})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404


@app.get("/api/events/<event_id>")
def event_detail(event_id: str) -> Any:
    try:
        return jsonify({"ok": True, "detail": repository.event_detail(event_id)})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404


@app.post("/api/decisions")
def decision_packet() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        mode = str(payload.get("mode") or "live_inference").strip().lower()
        if mode != "live_inference":
            raise ValueError("The native API accepts live_inference only; research replay stays in the reviewer")
        event_id = str(payload.get("eventId") or "").strip()
        if not event_id:
            raise ValueError("eventId is required")
        raw_decision_time = payload.get("decisionTime")
        decision_time = (
            required_offset_datetime(raw_decision_time, "decisionTime")
            if raw_decision_time
            else datetime.now(timezone.utc)
        )
        packet = repository.live_decision_packet(event_id, decision_time)
        return jsonify({"ok": True, "decision": packet})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/shadow-ledger")
def shadow_ledger_snapshot() -> Any:
    try:
        limit = max(1, min(int(request.args.get("limit", "100")), 500))
        snapshot = shadow_ledger.snapshot(limit)
        snapshot["refresh"] = prospective_refresh.status()
        return jsonify({"ok": True, "shadow": snapshot})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.post("/api/shadow-ledger/scan")
def shadow_ledger_scan() -> Any:
    try:
        snapshot = shadow_ledger.scan_once()
        snapshot["refresh"] = prospective_refresh.status()
        return jsonify({"ok": True, "shadow": snapshot})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.get("/api/prospective-refresh")
def prospective_refresh_status() -> Any:
    return jsonify({"ok": True, "refresh": prospective_refresh.status()})


@app.post("/api/prospective-refresh/run")
def request_prospective_refresh() -> Any:
    return jsonify({"ok": True, "refresh": prospective_refresh.request_refresh()}), 202


@app.get("/api/local-jyotish/health")
def local_jyotish_health() -> Any:
    return jsonify({"ok": True, "localJyotish": local_jyotish.health()})


@app.post("/api/local-jyotish/analyze")
def local_jyotish_analyze() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        draft = local_jyotish.analyze(
            str(payload.get("eventId") or ""),
            str(payload.get("question") or ""),
            str(payload.get("annotationId") or "").strip() or None,
        )
        return jsonify({"ok": True, "draft": draft})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.post("/api/events/<event_id>/review")
def occurrence_review(event_id: str) -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        event = repository.set_occurrence_progress(event_id, str(payload.get("status") or ""))
        return jsonify({"ok": True, "event": event})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/annotations")
def annotations() -> Any:
    rows = repository.list_annotations(
        event_id=request.args.get("eventId"),
        family_key=request.args.get("familyKey"),
    )
    return jsonify({"ok": True, "annotations": rows})


@app.post("/api/annotations")
def save_annotation() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        return jsonify({"ok": True, "annotation": repository.save_annotation(payload)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.delete("/api/annotations/<annotation_id>")
def delete_annotation(annotation_id: str) -> Any:
    return jsonify({"ok": repository.delete_annotation(annotation_id)})


@app.post("/api/snapshots")
def save_snapshot() -> Any:
    try:
        payload = request.get_json(force=True, silent=False)
        path = repository.save_snapshot(str(payload.get("dataUrl") or ""))
        return jsonify({"ok": True, "path": str(path)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/codex/context")
def codex_context() -> Any:
    event_id = str(request.args.get("eventId") or "")
    if not event_id:
        return jsonify({"ok": False, "error": "eventId is required"}), 400
    try:
        payload = repository.codex_context(event_id, request.args.get("annotationId"))
        return jsonify({"ok": True, "context": payload})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404


@app.get("/api/codex/thread")
def codex_thread() -> Any:
    scope_key = str(request.args.get("scopeKey") or "")
    return jsonify({"ok": True, "threadId": repository.get_codex_thread(scope_key) if scope_key else None})


@app.post("/api/codex/thread")
def save_codex_thread() -> Any:
    payload = request.get_json(force=True, silent=False)
    scope_key = str(payload.get("scopeKey") or "").strip()
    thread_id = str(payload.get("threadId") or "").strip()
    if not scope_key or not thread_id:
        return jsonify({"ok": False, "error": "scopeKey and threadId are required"}), 400
    repository.save_codex_thread(scope_key, thread_id)
    return jsonify({"ok": True})


def codex_bridge_url(path: str) -> str:
    base = str(os.environ.get("GANN_ASTRO_CODEX_URL") or "http://127.0.0.1:8789").rstrip("/")
    return f"{base}/{path.lstrip('/')}"


def proxy_codex(path: str, method: str) -> Any:
    body = request.get_data() if method != "GET" else None
    upstream = Request(
        codex_bridge_url(path),
        data=body,
        method=method,
        headers={"Content-Type": request.headers.get("Content-Type", "application/json")},
    )
    try:
        with urlopen(upstream, timeout=180) as response:
            return Response(
                response.read(),
                status=response.status,
                content_type=response.headers.get("Content-Type", "application/json"),
            )
    except HTTPError as exc:
        return Response(
            exc.read(),
            status=exc.code,
            content_type=exc.headers.get("Content-Type", "application/json"),
        )
    except URLError as exc:
        return jsonify({"ok": False, "error": f"Codex bridge unavailable: {exc.reason}"}), 503


@app.get("/codex-api/health")
def codex_proxy_health() -> Any:
    return proxy_codex("health", "GET")


@app.post("/codex-api/chat")
def codex_proxy_chat() -> Any:
    return proxy_codex("chat", "POST")


def frontend_dist() -> Path | None:
    configured = str(os.environ.get("GANN_ASTRO_FRONTEND_DIST") or "").strip()
    if not configured:
        return None
    root = Path(configured).expanduser().resolve()
    return root if (root / "index.html").is_file() else None


@app.get("/")
def desktop_index() -> Any:
    root = frontend_dist()
    if root is None:
        return jsonify({"ok": True, "service": "gann-astro-desk-backend"})
    return send_from_directory(root, "index.html")


@app.get("/<path:asset_path>")
def desktop_asset(asset_path: str) -> Any:
    root = frontend_dist()
    if root is None:
        abort(404)
    candidate = (root / asset_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        abort(404)
    if candidate.is_file():
        return send_from_directory(root, asset_path)
    return send_from_directory(root, "index.html")


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("GANN_ASTRO_BACKEND_PORT", "8788")),
        debug=False,
        use_reloader=False,
        threaded=True,
    )
