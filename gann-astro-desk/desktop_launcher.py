from __future__ import annotations

import ctypes
import importlib
import os
import shutil
import socket
import subprocess
import sys
import threading
import traceback
from dataclasses import dataclass
from multiprocessing import freeze_support
from pathlib import Path
from typing import Any


WORKER_MODULES = {
    "build_corrected_natal_event_source.py": "build_corrected_natal_event_source",
    "build_aspect_sr_touch_log.py": "build_aspect_sr_touch_log",
}


@dataclass(frozen=True)
class RuntimePaths:
    bundle_root: Path
    project_root: Path
    frontend_dist: Path
    data_root: Path
    annotation_db: Path
    logs_dir: Path
    codex_root: Path


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


def run_worker_mode(arguments: list[str] | None = None) -> bool:
    values = list(arguments if arguments is not None else sys.argv[1:])
    if len(values) < 2 or values[0] != "--gann-worker":
        return False
    script_name = Path(values[1]).name
    module_name = WORKER_MODULES.get(script_name)
    if module_name is None:
        raise ValueError(f"Unsupported packaged worker: {script_name}")
    sys.argv = [script_name, *values[2:]]
    module = importlib.import_module(module_name)
    module.main()
    return True


def default_data_root() -> Path:
    configured = str(os.environ.get("GANN_ASTRO_DESKTOP_DATA") or "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    if Path("D:/").exists():
        return Path(r"D:\GannFinancialAstro\app_data")
    local = Path(os.environ.get("LOCALAPPDATA") or Path.home())
    return local / "GannAstroDesk"


def runtime_paths() -> RuntimePaths:
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        bundle_root = Path(str(frozen_root)).resolve()
        project_root = bundle_root
        frontend_dist = bundle_root / "frontend"
        codex_root = bundle_root / "codex"
    else:
        app_root = Path(__file__).resolve().parent
        bundle_root = app_root
        project_root = app_root.parent
        frontend_dist = app_root / "dist"
        codex_root = app_root
    data_root = default_data_root()
    return RuntimePaths(
        bundle_root=bundle_root,
        project_root=project_root,
        frontend_dist=frontend_dist,
        data_root=data_root,
        annotation_db=data_root / "gann_aspect_annotations_raman_v2.sqlite",
        logs_dir=data_root / "logs",
        codex_root=codex_root,
    )


def available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def prepare_environment(paths: RuntimePaths, codex_port: int) -> None:
    paths.data_root.mkdir(parents=True, exist_ok=True)
    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    seed_db = paths.project_root / "gann_aspect_annotations_raman_v2.sqlite"
    if not paths.annotation_db.exists():
        if not seed_db.is_file():
            raise FileNotFoundError(f"Packaged annotation database is missing: {seed_db}")
        shutil.copy2(seed_db, paths.annotation_db)
    os.environ["GANN_ASTRO_PROJECT_ROOT"] = str(paths.project_root)
    os.environ["GANN_ASTRO_ANNOTATION_DB"] = str(paths.annotation_db)
    os.environ["GANN_ASTRO_FRONTEND_DIST"] = str(paths.frontend_dist)
    os.environ["GANN_ASTRO_MARKET_SNAPSHOTS_DIR"] = str(paths.data_root / "market_snapshots")
    os.environ["GANN_ASTRO_PRICE_SOURCES_DIR"] = str(paths.data_root / "price_sources")
    os.environ["GANN_ASTRO_ALLOWED_ORIGIN"] = "*"
    os.environ["GANN_ASTRO_CODEX_URL"] = f"http://127.0.0.1:{codex_port}"
    packaged_ephemeris = paths.project_root / "sweph"
    if packaged_ephemeris.is_dir():
        os.environ["GANN_ASTRO_EPHEMERIS_PATH"] = str(packaged_ephemeris)


def codex_runtime(paths: RuntimePaths) -> tuple[Path | None, Path | None]:
    packaged_node = paths.codex_root / "node.exe"
    packaged_bridge = paths.codex_root / "server" / "codexBridge.mjs"
    if packaged_node.is_file() and packaged_bridge.is_file():
        return packaged_node, packaged_bridge
    source_node = Path(shutil.which("node") or "")
    source_bridge = paths.bundle_root / "server" / "codexBridge.mjs"
    if source_node.is_file() and source_bridge.is_file():
        return source_node, source_bridge
    return None, None


def start_codex_bridge(paths: RuntimePaths, port: int) -> tuple[subprocess.Popen[Any] | None, list[Any]]:
    node, bridge = codex_runtime(paths)
    if node is None or bridge is None:
        return None, []
    stdout = (paths.logs_dir / "codex_bridge.log").open("a", encoding="utf-8")
    stderr = (paths.logs_dir / "codex_bridge_error.log").open("a", encoding="utf-8")
    environment = os.environ.copy()
    environment["GANN_ASTRO_CODEX_PORT"] = str(port)
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(
        [str(node), str(bridge)],
        cwd=bridge.parent,
        env=environment,
        stdout=stdout,
        stderr=stderr,
        creationflags=creationflags,
    )
    return process, [stdout, stderr]


def stop_process(process: subprocess.Popen[Any] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


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
            backend_server.gateway.stop()
            backend_server.generation_manager.stop()
        stop_process(codex_process)
        for handle in codex_logs:
            handle.close()


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
