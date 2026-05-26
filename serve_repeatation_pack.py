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

from aspect_annotation_store import add_rule_lesson, connect, initialize_database


DEFAULT_PACK_DIR = Path(
    r"C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548"
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
        if endpoint == "/api/dream_review":
            self._handle_dream_review()
            return
        if endpoint == "/api/save_rule_lesson":
            self._handle_save_rule_lesson()
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

        db_path = PROJECT_ROOT / "gann_aspect_annotations.sqlite"
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    directory = args.directory.resolve()
    if not directory.exists():
        raise SystemExit(f"Review pack directory does not exist: {directory}")
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
