from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


LAB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = LAB_ROOT / "lab_config.yaml"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path).resolve() if path is not None else DEFAULT_CONFIG_PATH
    loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {config_path}")
    isolation = loaded.get("isolation", {})
    required_false = (
        "import_main_project_modules",
        "write_main_project_data",
        "trading_enabled",
        "mt5_enabled",
        "auto_suggest_enabled",
        "llm_enabled",
    )
    bad = [key for key in required_false if isolation.get(key) is not False]
    if bad:
        raise ValueError(f"Isolation contract violated by config keys: {bad}")
    return loaded


def profile(config: dict[str, Any], profile_id: str) -> dict[str, Any]:
    profiles = config.get("reference_profiles", {})
    if profile_id not in profiles:
        raise KeyError(f"Unknown profile {profile_id!r}; available={sorted(profiles)}")
    value = profiles[profile_id]
    if not isinstance(value, dict):
        raise ValueError(f"Profile {profile_id!r} must be a mapping")
    return value


def safe_output_path(value: str | Path, config: dict[str, Any]) -> Path:
    path = Path(value)
    resolved = (LAB_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    allowed = [
        (LAB_ROOT / name).resolve()
        for name in config.get("isolation", {}).get("allowed_output_directories", [])
    ]
    if not any(resolved == root or resolved.is_relative_to(root) for root in allowed):
        raise ValueError(f"Output must stay under lab outputs/reports: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved
