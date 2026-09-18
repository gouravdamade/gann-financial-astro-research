"""Artifact constraints for a future one-shot run; R3R2A writes no real output."""

from __future__ import annotations

from pathlib import Path

from .controller_r3r2 import FUTURE_RESULT_PATHS


def future_result_paths_are_unpopulated(root: Path | str) -> bool:
    base = Path(root)
    return all(not (base / relative).exists() for relative in FUTURE_RESULT_PATHS)
