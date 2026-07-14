from __future__ import annotations

import ctypes
import importlib
import sys
import threading
import traceback
from multiprocessing import freeze_support
from pathlib import Path
from typing import Any

from runtime_support import (
    available_port,
    close_handles,
    prepare_environment,
    run_worker_mode,
    runtime_paths,
    start_codex_bridge,
    start_local_ollama,
    stop_backend_services,
    stop_process,
)


class DesktopApi:
    def __init__(self) -> None:
        self._windows: dict[str, Any] = {}
        self._lock = threading.RLock()

    def open_analyze_aspect(self, url: str, title: str, key: str) -> bool:
        import webview

        normalized = str(key or title).strip()[:120]
        with self._lock:
            existing = self._windows.get(normalized)
            if existing is not None:
                try:
                    existing.restore()
                    existing.show()
                    return True
                except Exception:
                    self._windows.pop(normalized, None)
            child = webview.create_window(
                str(title or "Analyze Aspect")[:180],
                str(url),
                js_api=self,
                width=1480,
                height=900,
                min_size=(1080, 700),
                resizable=True,
                background_color="#0c1424",
                text_select=True,
                zoomable=True,
            )
            self._windows[normalized] = child
        return True


def show_fatal_error(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(0, message, "Gann Astro Desk", 0x10)


def run_desktop() -> None:
    paths = runtime_paths()
    codex_port = available_port()
    prepare_environment(paths, codex_port)
    if not paths.frontend_dist.joinpath("index.html").is_file():
        raise FileNotFoundError(f"Built frontend is missing: {paths.frontend_dist}")

    backend_path = (
        paths.bundle_root / "backend"
        if getattr(sys, "frozen", False)
        else Path(__file__).parent / "backend"
    )
    sys.path.insert(0, str(backend_path))
    ollama_process, ollama_logs = start_local_ollama(paths)
    codex_process, codex_logs = start_codex_bridge(paths, codex_port)
    backend_server: Any = None
    http_server: Any = None
    try:
        backend_server = importlib.import_module("server")
        from werkzeug.serving import make_server

        http_server = make_server("127.0.0.1", 0, backend_server.app, threaded=True)
        backend_port = int(http_server.server_port)
        server_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        server_thread.start()

        import webview

        desktop_api = DesktopApi()
        webview.create_window(
            "Gann Astro Desk",
            f"http://127.0.0.1:{backend_port}/",
            js_api=desktop_api,
            width=1480,
            height=920,
            min_size=(1120, 720),
            resizable=True,
            background_color="#0c1424",
            text_select=True,
            zoomable=True,
        )
        webview.start(
            gui="edgechromium",
            debug=False,
            private_mode=False,
            storage_path=str(paths.data_root / "webview"),
        )
    finally:
        if http_server is not None:
            http_server.shutdown()
            http_server.server_close()
        if backend_server is not None:
            stop_backend_services(backend_server)
        stop_process(codex_process)
        stop_process(ollama_process)
        close_handles(codex_logs)
        close_handles(ollama_logs)


def main() -> int:
    freeze_support()
    worker_requested = len(sys.argv) > 1 and sys.argv[1] == "--gann-worker"
    if worker_requested:
        try:
            run_worker_mode()
            return 0
        except Exception:
            traceback.print_exc()
            return 1
    try:
        run_desktop()
        return 0
    except Exception:
        details = traceback.format_exc()
        try:
            paths = runtime_paths()
            paths.logs_dir.mkdir(parents=True, exist_ok=True)
            (paths.logs_dir / "desktop_fatal.log").write_text(details, encoding="utf-8")
        except Exception:
            pass
        show_fatal_error(details[-7000:])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
