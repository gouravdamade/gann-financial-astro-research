from __future__ import annotations

import os
from pathlib import Path

import pytest

from jhora_kaala_intermediate_witness_protocol import PLANETS
from jhora_tropical_position_transcription import (
    TRANSCRIPTION_CONTRACT,
    read_visible_tropical_positions,
)


def _external_witness() -> Path:
    raw = str(os.environ.get("JHORA_WITNESS_CSV") or "").strip()
    if not raw:
        pytest.skip("SKIPPED_WITH_REASON: set JHORA_WITNESS_CSV to validate a local external witness")
    path = Path(raw).expanduser().resolve()
    if not path.is_file():
        pytest.skip(f"SKIPPED_WITH_REASON: JHORA_WITNESS_CSV does not exist: {path}")
    return path


def test_external_visible_tropical_witness_when_explicitly_supplied() -> None:
    path = _external_witness()
    # The established witness layout is <repo>/status/evidence/<bundle>/<csv>.
    repo_root = path.parents[3]
    rows = read_visible_tropical_positions(path, repo_root=repo_root)

    assert len(rows) == len(PLANETS)
    assert {row["planet"] for row in rows} == set(PLANETS)
    assert {row["contract"] for row in rows} == {TRANSCRIPTION_CONTRACT}
