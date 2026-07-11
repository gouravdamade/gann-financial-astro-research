from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial

from aspect_annotation_store import (
    add_rule_lesson,
    connect,
    enqueue_codex_review_task,
    initialize_database,
    list_completed_reviews,
    upsert_completed_review,
)
from codex_review_task_queue import process_pending_tasks
from reviewer_rule_replay import auto_suggest_case, replay_completed_review_impacts


DEFAULT_PACK_DIR = Path(
    r"D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548"
)
PROJECT_ROOT = Path(__file__).resolve().parent
OLLAMA_EXE = Path(r"D:\ollama\app\ollama.exe")
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"


def ollama_available(timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=timeout) as response:
            return int(getattr(response, "status", 0) or 0) < 400
    except (OSError, urllib.error.URLError):
        return False


def ensure_ollama_running() -> dict:
    if ollama_available():
        return {"available": True, "started": False, "message": "Ollama already running"}
    if not OLLAMA_EXE.exists():
        return {"available": False, "started": False, "message": f"Ollama executable not found: {OLLAMA_EXE}"}

    env = os.environ.copy()
    env.setdefault("OLLAMA_MODELS", r"D:\ollama\models")
    log_dir = OLLAMA_EXE.parent.parent
    stdout = open(log_dir / "ollama_stdout.log", "a", encoding="utf-8", errors="replace")
    stderr = open(log_dir / "ollama_stderr.log", "a", encoding="utf-8", errors="replace")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen(
            [str(OLLAMA_EXE), "serve"],
            cwd=str(OLLAMA_EXE.parent),
            env=env,
            stdout=stdout,
            stderr=stderr,
            creationflags=creationflags,
        )
    except Exception as exc:
        return {"available": False, "started": False, "message": f"Could not start Ollama: {exc}"}
    finally:
        stdout.close()
        stderr.close()

    for _ in range(30):
        time.sleep(0.5)
        if ollama_available(timeout=1.5):
            return {"available": True, "started": True, "message": "Ollama started for Draft ML Reason"}
    return {"available": False, "started": True, "message": "Ollama start requested, but API did not become ready"}


class NoCacheRequestHandler(SimpleHTTPRequestHandler):
    annotation_db_path = PROJECT_ROOT / "gann_aspect_annotations.sqlite"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        endpoint = self.path.split("?", 1)[0]
        if endpoint == "/api/auto_suggest":
            self._handle_auto_suggest()
            return
        if endpoint == "/api/dream_review":
            self._handle_dream_review()
            return
        if endpoint == "/api/save_rule_lesson":
            self._handle_save_rule_lesson()
            return
        if endpoint == "/api/complete_review":
            self._handle_complete_review()
            return
        if endpoint != "/api/draft_ml_reason":
            self._send_json(404, {"ok": False, "error": "unknown API endpoint"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            payload = json.loads(raw or "{}")
            case_id = int(payload.get("case_id"))
            question = str(payload.get("question") or "").strip()
            if not question:
                question = f"Explain case {case_id} behavior and propose ML features/rules to test."
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": f"bad request: {exc}"})
            return

        out_path = PROJECT_ROOT / "jyotish_agent" / "case_explanations" / f"case_{case_id}_jyotish_explanation.md"
        llm_runtime = ensure_ollama_running()
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "jyotish_agent" / "explain_case.py"),
            "--case-id",
            str(case_id),
            "--question",
            question,
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            self._send_json(504, {"ok": False, "error": "local explanation timed out"})
            return
        if proc.returncode != 0:
            self._send_json(500, {"ok": False, "error": (proc.stderr or proc.stdout or "explain_case failed")[:4000]})
            return
        try:
            markdown = out_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": f"could not read explanation: {exc}"})
            return
        self._send_json(
            200,
            {
                "ok": True,
                "case_id": case_id,
                "path": str(out_path),
                "markdown": markdown,
                "llm_runtime": llm_runtime,
            },
        )

    def _handle_auto_suggest(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            payload = json.loads(raw or "{}")
            case_id = int(payload.get("case_id"))
            pack_dir = Path(self.directory).resolve()
            replay = auto_suggest_case(pack_dir, case_id)
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": f"auto suggest failed: {exc}"})
            return
        self._send_json(
            200,
            {
                "ok": True,
                "case_id": case_id,
                "engine": "reviewer_rule_replay.auto_suggest_case",
                "engine_mode": "retrospective_review_only",
                "replay": replay,
            },
        )

    def _completed_row_to_dict(self, row) -> dict:
        out = dict(row)
        for key in ("auto_suggestion_json", "marker_ml_note_json", "rule_impact_json"):
            raw = out.pop(key, "") or ""
            out[key.replace("_json", "")] = {}
            if raw:
                try:
                    out[key.replace("_json", "")] = json.loads(raw)
                except Exception:
                    out[key.replace("_json", "")] = {"raw": raw}
        return out

    def _review_impact_summary(self, payload: dict, previous_rows: list, pack_dir: Path | None = None) -> dict:
        auto = payload.get("auto_suggestion") or {}
        current_start_rule = str(auto.get("start_rule") or payload.get("start_rule") or "")
        current_end_rule = str(auto.get("end_rule") or payload.get("end_rule") or "")
        current_version = str(payload.get("rule_version") or "")
        if pack_dir is not None:
            try:
                replay = replay_completed_review_impacts(pack_dir, previous_rows, current_rule_version=current_version)
                replay["current_start_rule"] = current_start_rule
                replay["current_end_rule"] = current_end_rule
                replay["current_rule_version"] = current_version
                replay["previous_reviewed_count"] = replay.get("reviewed_count", len(previous_rows))
                replay["same_rule_path_count"] = replay.get("unchanged_count", 0)
                replay["official_note_policy"] = (
                    "Official ML notes are queued for Codex review; local browser notes are draft evidence only."
                )
                return replay
            except Exception as exc:
                replay_error = str(exc)
        else:
            replay_error = "pack_dir unavailable"
        changed = []
        same = 0
        for row in previous_rows:
            old_start = str(row["start_rule"] or "")
            old_end = str(row["end_rule"] or "")
            old_version = str(row["rule_version"] or "")
            differs = old_start != current_start_rule or old_end != current_end_rule
            version_differs = bool(current_version and old_version and current_version != old_version)
            if differs or version_differs:
                changed.append(
                    {
                        "case_id": int(row["case_id"]),
                        "stored_pips": row["signed_pips"],
                        "stored_start_rule": old_start,
                        "stored_end_rule": old_end,
                        "stored_rule_version": old_version,
                        "current_start_rule": current_start_rule,
                        "current_end_rule": current_end_rule,
                        "current_rule_version": current_version,
                        "reason": "rule path differs" if differs else "rule version differs",
                    }
                )
            else:
                same += 1
        return {
            "mode": "rule_path_fallback",
            "current_start_rule": current_start_rule,
            "current_end_rule": current_end_rule,
            "current_rule_version": current_version,
            "previous_reviewed_count": len(previous_rows),
            "same_rule_path_count": same,
            "affected_or_needs_replay": changed,
            "replay_error": replay_error,
            "official_note_policy": "Official ML notes are queued for Codex review; local browser notes are draft evidence only.",
            "message": (
                "No previous completed reviews in this family yet."
                if not previous_rows
                else f"{len(changed)} previous completed review(s) have a different rule path/version and should be replay-checked."
            ),
        }

    def _enqueue_codex_review_tasks(
        self,
        conn,
        *,
        review_id: int,
        payload: dict,
        impact: dict,
    ) -> list[int]:
        case_id = int(payload.get("case_id"))
        family_key = str(payload.get("family_key") or "")
        task_payload = {
            "review_id": review_id,
            "case_id": case_id,
            "family_key": family_key,
            "completed_review_payload": payload,
            "impact_summary": impact,
            "policy": "official_ml_notes_codex_owned",
            "instruction": (
                "Create or update official ML notes only after checking deterministic evidence, "
                "replay impact, verifier output, manual notes, and rule lessons. Treat local LLM output as draft only."
            ),
        }
        task_ids = [
            enqueue_codex_review_task(
                conn,
                task_type="official_ml_note",
                case_id=case_id,
                family_key=family_key,
                priority="normal",
                source="review_complete",
                trigger_reason="Review Complete saved with start/end markers and P/L.",
                payload=task_payload,
            )
        ]
        affected = impact.get("affected_or_needs_replay") if isinstance(impact, dict) else []
        if isinstance(affected, list) and affected:
            task_ids.append(
                enqueue_codex_review_task(
                    conn,
                    task_type="rule_replay_review",
                    case_id=case_id,
                    family_key=family_key,
                    priority="high",
                    source="historical_resimulation",
                    trigger_reason="Current review/rule replay changed previously completed cases.",
                    payload={
                        "review_id": review_id,
                        "case_id": case_id,
                        "family_key": family_key,
                        "affected_cases": affected,
                        "impact_summary": impact,
                        "instruction": (
                            "Inspect affected prior cases, correct stale official notes if needed, "
                            "and edit deterministic rule code only when replay exposes a real logic contradiction."
                        ),
                    },
                )
            )
        return task_ids

    def _handle_complete_review(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            payload = json.loads(raw or "{}")
            case_id = int(payload.get("case_id"))
            family_key = str(payload.get("family_key") or "").strip()
            if not family_key:
                raise ValueError("family_key is required")
            trade = payload.get("trade_profit") or {}
            auto = payload.get("auto_suggestion") or {}
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": f"bad complete review request: {exc}"})
            return

        db_path = self.annotation_db_path
        try:
            initialize_database(db_path)
            with connect(db_path) as conn:
                previous_rows = [
                    row
                    for row in list_completed_reviews(conn, family_key=family_key, limit=1000)
                    if int(row["case_id"]) != case_id
                ]
                impact = self._review_impact_summary(payload, previous_rows, pack_dir=Path(self.directory))
                review_id, inserted = upsert_completed_review(
                    conn,
                    case_id=case_id,
                    family_key=family_key,
                    pair_key=str(payload.get("pair_key") or ""),
                    aspect=str(payload.get("aspect") or ""),
                    price_timeframe=str(payload.get("price_timeframe") or ""),
                    outcome_label=str(payload.get("outcome_label") or trade.get("outcomeLabel") or ""),
                    trade_start_ist=str(payload.get("trade_start_ist") or ""),
                    trade_end_ist=str(payload.get("trade_end_ist") or ""),
                    entry_price=trade.get("entry"),
                    exit_price=trade.get("exit"),
                    signed_pips=trade.get("signedPips"),
                    raw_pips=trade.get("rawPips"),
                    review_status=str(payload.get("review_status") or "complete"),
                    rule_version=str(payload.get("rule_version") or ""),
                    start_rule=str(auto.get("start_rule") or ""),
                    end_rule=str(auto.get("end_rule") or ""),
                    auto_suggestion_json=json.dumps(auto, ensure_ascii=False, default=str),
                    marker_ml_note_json=json.dumps(payload.get("current_marker_ml_note") or {}, ensure_ascii=False, default=str),
                    rule_impact_json=json.dumps(impact, ensure_ascii=False, default=str),
                    reviewer_note=str(payload.get("reviewer_note") or ""),
                )
                codex_task_ids = self._enqueue_codex_review_tasks(
                    conn,
                    review_id=review_id,
                    payload=payload,
                    impact=impact,
                )
                conn.commit()
                current_rows = list_completed_reviews(conn, family_key=family_key, limit=1000)
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": f"could not complete review: {exc}"})
            return

        self._send_json(
            200,
            {
                "ok": True,
                "review_id": review_id,
                "inserted": inserted,
                "case_id": case_id,
                "message": "review completed" if inserted else "review completion updated",
                "impact_summary": impact,
                "codex_task_ids": codex_task_ids,
                "completed_reviews": [self._completed_row_to_dict(row) for row in current_rows[:50]],
            },
        )

    def _handle_dream_review(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            payload = json.loads(raw or "{}")
            int(payload.get("case_id"))
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": f"bad dream review request: {exc}"})
            return

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(payload, handle, ensure_ascii=False, default=str)
            payload_path = Path(handle.name)
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "jyotish_agent" / "dream_review_agent.py"),
            "--payload",
            str(payload_path),
            "--apply-safe",
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            self._send_json(504, {"ok": False, "error": "dream review timed out"})
            return
        finally:
            try:
                payload_path.unlink(missing_ok=True)
            except Exception:
                pass
        if proc.returncode != 0:
            self._send_json(500, {"ok": False, "error": (proc.stderr or proc.stdout or "dream review failed")[:4000]})
            return
        try:
            result = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": f"could not parse dream review: {exc}", "stdout": proc.stdout[:4000]})
            return
        codex_task_ids: list[int] = []
        if result.get("status") == "queued_for_codex" or result.get("needs_review"):
            try:
                db_path = self.annotation_db_path
                initialize_database(db_path)
                with connect(db_path) as conn:
                    codex_task_ids.append(
                        enqueue_codex_review_task(
                            conn,
                            task_type="dream_review_correction",
                            case_id=int(result.get("case_id") or payload.get("case_id")),
                            family_key=str(result.get("family") or payload.get("family") or ""),
                            priority="high",
                            source="dream_review",
                            trigger_reason=str(result.get("message") or "Dream Review queued a contradiction for Codex review."),
                            payload={
                                "case_id": int(result.get("case_id") or payload.get("case_id")),
                                "family_key": str(result.get("family") or payload.get("family") or ""),
                                "dream_review_payload": payload,
                                "dream_review_result": result,
                                "policy": "dream_review_contradictions_codex_owned",
                                "instruction": (
                                    "Inspect the local draft, verifier evidence, Auto Suggest evidence, current marker ML note, "
                                    "saved official ML note, rule lessons, and dream-review report. If deterministic evidence is clear, "
                                    "replace the official ML note through codex_review_task_queue.py --write-official-note. "
                                    "Treat local LLM text as draft only."
                                ),
                            },
                        )
                    )
                    conn.commit()
            except Exception as exc:
                result["codex_queue_error"] = str(exc)
        if codex_task_ids:
            result["codex_task_ids"] = codex_task_ids
            try:
                result["codex_agent_result"] = process_pending_tasks(
                    self.annotation_db_path,
                    limit=20,
                )
            except Exception as exc:
                result["codex_agent_error"] = str(exc)
        self._send_json(200, result)

    def _handle_save_rule_lesson(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            payload = json.loads(raw or "{}")
            case_id = int(payload.get("case_id"))
            family_key = str(payload.get("family_key") or "").strip()
            lesson_key = str(payload.get("lesson_key") or "").strip()
            conflict_type = str(payload.get("conflict_type") or "").strip()
            lesson_text = str(payload.get("lesson_text") or "").strip()
            if not family_key or not lesson_key or not conflict_type or not lesson_text:
                raise ValueError("case_id, family_key, lesson_key, conflict_type, and lesson_text are required")
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": f"bad rule lesson request: {exc}"})
            return

        db_path = self.annotation_db_path
        try:
            initialize_database(db_path)
            with connect(db_path) as conn:
                lesson_id, inserted = add_rule_lesson(
                    conn,
                    case_id=case_id,
                    family_key=family_key,
                    lesson_key=lesson_key,
                    conflict_type=conflict_type,
                    old_rule=str(payload.get("old_rule") or ""),
                    new_rule=str(payload.get("new_rule") or ""),
                    winner_rule=str(payload.get("winner_rule") or ""),
                    outcome_label=str(payload.get("outcome_label") or ""),
                    status=str(payload.get("status") or "provisional"),
                    lesson_text=lesson_text,
                    astro_hints_json=json.dumps(payload.get("astro_hints") or [], ensure_ascii=False, default=str),
                    auto_suggestion_json=json.dumps(payload.get("auto_suggestion") or {}, ensure_ascii=False, default=str),
                    verifier_json=json.dumps(payload.get("verifier_report") or {}, ensure_ascii=False, default=str),
                    dream_review_json=json.dumps(payload.get("dream_review") or {}, ensure_ascii=False, default=str),
                )
                conn.commit()
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": f"could not save rule lesson: {exc}"})
            return
        self._send_json(
            200,
            {
                "ok": True,
                "lesson_id": lesson_id,
                "inserted": inserted,
                "case_id": case_id,
                "message": "lesson saved" if inserted else "lesson updated",
            },
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a generated repeatation review pack over localhost.")
    parser.add_argument("--directory", type=Path, default=DEFAULT_PACK_DIR, help="Review pack folder to serve.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host.")
    parser.add_argument("--port", type=int, default=8765, help="Bind port.")
    parser.add_argument(
        "--db",
        type=Path,
        default=PROJECT_ROOT / "gann_aspect_annotations.sqlite",
        help="Versioned annotation database used by review APIs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    directory = args.directory.resolve()
    if not directory.exists():
        raise SystemExit(f"Review pack directory does not exist: {directory}")
    NoCacheRequestHandler.annotation_db_path = args.db.resolve()
    handler = partial(NoCacheRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer((args.host, int(args.port)), handler)
    print(f"Serving {directory}")
    print(f"Open http://localhost:{args.port}/repeatation_reviewer.html")
    print(f"Open http://localhost:{args.port}/aspect_review_case_11_chart.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
