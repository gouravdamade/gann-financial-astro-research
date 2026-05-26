from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial


DEFAULT_PACK_DIR = Path(
    r"C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548"
)
PROJECT_ROOT = Path(__file__).resolve().parent


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
