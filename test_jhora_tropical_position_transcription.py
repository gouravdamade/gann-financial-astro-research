from __future__ import annotations

import csv
from pathlib import Path

import pytest

from jhora_kaala_intermediate_witness_protocol import PLANETS
from jhora_tropical_position_transcription import (
    TRANSCRIPTION_CONTRACT,
    TranscriptionValidationError,
    ayana_capture_inputs,
    read_visible_tropical_positions,
)


REPO_ROOT = Path(__file__).resolve().parent
TRANSCRIPTION = (
    REPO_ROOT
    / "status"
    / "evidence"
    / "jhora_kaala_witness_20260727"
    / "gann_reference_tokyo_tropical_positions_visible_20260729.csv"
)
LOCKED_KAALA = (
    REPO_ROOT
    / "status"
    / "evidence"
    / "jhora_kaala_witness_20260727"
    / "jhora_kaala_profile_comparison_20260727.csv"
)


def test_locked_visible_tropical_transcription_is_complete() -> None:
    rows = read_visible_tropical_positions(TRANSCRIPTION)

    assert len(rows) == len(PLANETS)
    assert {row["planet"] for row in rows} == set(PLANETS)
    assert {row["contract"] for row in rows} == {TRANSCRIPTION_CONTRACT}
    assert {row["tropical_longitude_deg"] for row in rows} == {
        "322.131",
        "81.945",
        "354.856",
        "331.016",
        "270.854",
        "8.536",
        "136.496",
    }


def test_transcription_builds_ayana_capture_inputs_from_visible_sources() -> None:
    capture = ayana_capture_inputs(TRANSCRIPTION, LOCKED_KAALA)
    values = capture["values"]

    assert Path(capture["evidence_path"]).is_file()
    assert set(values) == set(PLANETS)
    assert values["SUN"]["tropical_longitude_deg"] == "322.131"
    assert values["SUN"]["ayana_virupa"] == pytest.approx(25.95)


def test_transcription_rejects_evidence_hash_drift(tmp_path: Path) -> None:
    with TRANSCRIPTION.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    rows[0]["position_evidence_sha256"] = "0" * 64
    path = tmp_path / "tampered.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(TranscriptionValidationError, match="hash mismatch"):
        read_visible_tropical_positions(path)
