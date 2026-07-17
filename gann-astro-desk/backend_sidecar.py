from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import signal
import sys
import threading
import time
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


SIDECAR_CONTRACT = "GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1"
SUPPORT_SERVICE_DELAY_SECONDS = 8.0


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gann Astro Desk managed backend sidecar")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--codex-port", type=int, default=0)
    return parser.parse_args(arguments)


def run_sidecar(arguments: list[str] | None = None) -> None:
    sidecar_started_at = time.perf_counter()
    startup_phases: dict[str, float] = {}

    def mark_startup_phase(name: str) -> None:
        startup_phases[name] = round((time.perf_counter() - sidecar_started_at) * 1000, 2)

    options = parse_arguments(arguments)
    if not (1 <= options.port <= 65535):
        raise ValueError("Backend port must be between 1 and 65535")
    codex_port = options.codex_port or available_port()
    if not (1 <= codex_port <= 65535):
        raise ValueError("Codex port must be between 1 and 65535")

    paths = runtime_paths()
    prepare_environment(paths, codex_port)
    mark_startup_phase("environment_ready")
    backend_path = (
        paths.bundle_root / "backend"
        if getattr(sys, "frozen", False)
        else Path(__file__).parent / "backend"
    )
    sys.path.insert(0, str(backend_path))

    ollama_process: Any = None
    ollama_logs: list[Any] = []
    codex_process: Any = None
    codex_logs: list[Any] = []
    backend_server: Any = None
    http_server: Any = None
    support_thread: threading.Thread | None = None
    support_lock = threading.Lock()
    shutdown_once = threading.Event()

    def request_shutdown() -> None:
        if shutdown_once.is_set():
            return
        shutdown_once.set()
        if http_server is not None:
            http_server.shutdown()

    def watch_parent_pipe() -> None:
        stream = sys.stdin
        if stream is None:
            return
        try:
            for line in stream:
                if line.strip().lower() == "shutdown":
                    request_shutdown()
                    return
            request_shutdown()
        except (OSError, ValueError):
            request_shutdown()

    def signal_shutdown(_signum: int, _frame: Any) -> None:
        threading.Thread(target=request_shutdown, daemon=True).start()

    def launch_support_services() -> None:
        nonlocal codex_logs, codex_process, ollama_logs, ollama_process
        next_codex_process, next_codex_logs = start_codex_bridge(paths, codex_port)
        if shutdown_once.is_set():
            stop_process(next_codex_process)
            close_handles(next_codex_logs)
            return
        with support_lock:
            codex_process = next_codex_process
            codex_logs = next_codex_logs
        if backend_server is not None:
            backend_server.runtime_diagnostics.record_lifecycle(
                "support_service_started",
                service="codex_bridge",
                started=next_codex_process is not None,
            )
        if shutdown_once.wait(SUPPORT_SERVICE_DELAY_SECONDS):
            return
        next_ollama_process, next_ollama_logs = start_local_ollama(paths)
        if shutdown_once.is_set():
            stop_process(next_ollama_process)
            close_handles(next_ollama_logs)
            return
        with support_lock:
            ollama_process = next_ollama_process
            ollama_logs = next_ollama_logs
        if backend_server is not None:
            backend_server.runtime_diagnostics.record_lifecycle(
                "support_service_started",
                service="local_ollama",
                started=next_ollama_process is not None,
            )

    try:
        backend_server = importlib.import_module("server")
        mark_startup_phase("backend_imported")
        from werkzeug.serving import make_server

        logging.getLogger("werkzeug").setLevel(logging.WARNING)
        http_server = make_server("127.0.0.1", options.port, backend_server.app, threaded=True)
        mark_startup_phase("http_ready")
        backend_server.runtime_diagnostics.set_startup_timings(
            startup_phases,
            {
                "supportServicesDeferred": True,
                "executionAllowed": False,
            },
        )
        for signal_name in ("SIGINT", "SIGTERM"):
            signal_value = getattr(signal, signal_name, None)
            if signal_value is not None:
                signal.signal(signal_value, signal_shutdown)
        threading.Thread(target=watch_parent_pipe, daemon=True).start()
        print(
            json.dumps(
                {
                    "contract": SIDECAR_CONTRACT,
                    "status": "ready",
                    "baseUrl": f"http://127.0.0.1:{options.port}",
                    "pid": os.getpid(),
                    "startupMs": startup_phases["http_ready"],
                    "executionAllowed": False,
                },
                separators=(",", ":"),
            ),
            flush=True,
        )
        support_thread = threading.Thread(
            target=launch_support_services,
            name="gann-support-services",
            daemon=True,
        )
        support_thread.start()
        http_server.serve_forever()
    finally:
        shutdown_once.set()
        if backend_server is not None:
            backend_server.runtime_diagnostics.record_lifecycle("sidecar_shutdown_requested")
        if http_server is not None:
            http_server.server_close()
        if backend_server is not None:
            stop_backend_services(backend_server)
        if support_thread is not None:
            support_thread.join(timeout=3)
        with support_lock:
            stop_process(codex_process)
            stop_process(ollama_process)
            close_handles(codex_logs)
            close_handles(ollama_logs)


def main() -> int:
    freeze_support()
    if len(sys.argv) > 1 and sys.argv[1] == "--gann-worker":
        try:
            run_worker_mode()
            return 0
        except Exception:
            traceback.print_exc()
            return 1
    try:
        run_sidecar()
        return 0
    except Exception:
        details = traceback.format_exc()
        try:
            paths = runtime_paths()
            paths.logs_dir.mkdir(parents=True, exist_ok=True)
            (paths.logs_dir / "backend_sidecar_fatal.log").write_text(details, encoding="utf-8")
        except Exception:
            pass
        print(details, file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
