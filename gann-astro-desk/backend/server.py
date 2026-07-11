from __future__ import annotations

import atexit
import os
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


@app.get("/api/chart")
def chart() -> Any:
    try:
        payload = repository.chart_payload(
            start=request.args.get("start"),
            end=request.args.get("end"),
            symbol=request.args.get("symbol", "USDJPY"),
            timeframe=request.args.get("timeframe", "H1"),
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
