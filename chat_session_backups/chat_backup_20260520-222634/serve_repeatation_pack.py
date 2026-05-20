from __future__ import annotations

import argparse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial


DEFAULT_PACK_DIR = Path(
    r"C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548"
)


class NoCacheRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


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
