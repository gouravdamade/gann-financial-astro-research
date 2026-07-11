from __future__ import annotations

import atexit
import os
from datetime import datetime, timezone
from typing import Any

from flask import Flask, jsonify, request

from mt5_gateway import Mt5Gateway
from repository import AstroRepository


app = Flask(__name__)
repository = AstroRepository()
gateway = Mt5Gateway(
    symbol=os.environ.get("GANN_ASTRO_MT5_SYMBOL", "USDJPY"),
    autoconnect=os.environ.get("GANN_ASTRO_MT5_AUTOCONNECT", "1") != "0",
)
gateway.start()
atexit.register(gateway.stop)


def list_argument(name: str) -> tuple[str, ...]:
    values: list[str] = []
    for raw in request.args.getlist(name):
        values.extend(item.strip() for item in raw.split(",") if item.strip())
    return tuple(dict.fromkeys(values))


def optional_float_argument(name: str) -> float | None:
    value = str(request.args.get(name) or "").strip()
    return float(value) if value else None


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


@app.after_request
def add_headers(response: Any) -> Any:
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5173"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/api/<path:_path>", methods=["OPTIONS"])
def options_route(_path: str) -> Any:
    return ("", 204)


@app.get("/api/health")
def health() -> Any:
    return jsonify({"ok": True, "data": repository.health(), "mt5": gateway.status()})


@app.get("/api/mt5/status")
def mt5_status() -> Any:
    return jsonify({"ok": True, "mt5": gateway.status()})


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


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("GANN_ASTRO_BACKEND_PORT", "8788")),
        debug=False,
        use_reloader=False,
        threaded=True,
    )
