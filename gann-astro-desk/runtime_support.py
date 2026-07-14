from __future__ import annotations

import importlib
import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


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
    packaged_corpus = paths.project_root / "jyotish" / "corpus_chunks.jsonl"
    source_corpus = paths.project_root / "jyotish_agent" / "corpus_chunks.jsonl"
    corpus = packaged_corpus if packaged_corpus.is_file() else source_corpus
    if corpus.is_file():
        os.environ["GANN_ASTRO_JYOTISH_CORPUS"] = str(corpus)
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


def ollama_ready() -> bool:
    endpoint = str(os.environ.get("GANN_ASTRO_OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")
    try:
        with urlopen(f"{endpoint}/api/tags", timeout=1.0) as response:
            return response.status == 200
    except (URLError, TimeoutError, OSError):
        return False


def start_local_ollama(paths: RuntimePaths) -> tuple[subprocess.Popen[Any] | None, list[Any]]:
    if ollama_ready():
        return None, []
    configured = str(os.environ.get("GANN_ASTRO_OLLAMA_EXE") or "").strip()
    executable = Path(configured).expanduser().resolve() if configured else Path(r"D:\Ollama\app\ollama.exe")
    if not executable.is_file():
        return None, []
    environment = os.environ.copy()
    model_root = Path(str(environment.get("OLLAMA_MODELS") or r"D:\Ollama\models"))
    if model_root.is_dir():
        environment["OLLAMA_MODELS"] = str(model_root)
    stdout = (paths.logs_dir / "local_jyotish_ollama.log").open("a", encoding="utf-8")
    stderr = (paths.logs_dir / "local_jyotish_ollama_error.log").open("a", encoding="utf-8")
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(
        [str(executable), "serve"],
        cwd=executable.parent,
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


def stop_backend_services(backend_server: Any) -> None:
    for name in ("prospective_refresh", "shadow_ledger", "gateway", "generation_manager"):
        service = getattr(backend_server, name, None)
        if service is not None:
            service.stop()


def close_handles(handles: list[Any]) -> None:
    for handle in handles:
        handle.close()
