from __future__ import annotations

from jhora_witness_protocol import (
    JHORA_EXE_SHA256,
    JHORA_VERSION,
    LOCKED_SETTINGS,
    MEASURES,
    WITNESS_CONTRACT,
    settings_json,
    settings_sha256,
    validate_witness_rows,
    witness_template_rows,
)
from pyjhora_external_strength_export import FIXTURES, PLANETS


def test_witness_template_is_complete_locked_and_pending() -> None:
    rows = witness_template_rows()

    assert len(rows) == len(FIXTURES) * len(PLANETS) * len(MEASURES)
    assert all(row["contract"] == WITNESS_CONTRACT for row in rows)
    assert all(row["jhora_version"] == JHORA_VERSION for row in rows)
    assert all(row["jhora_exe_sha256"] == JHORA_EXE_SHA256 for row in rows)
    assert all(row["settings_json"] == settings_json() for row in rows)
    assert all(row["settings_sha256"] == settings_sha256() for row in rows)
    assert all(row["status"] == "pending_manual_jhora_capture" for row in rows)
    assert LOCKED_SETTINGS["ayanamsa"] == "Raman"
    assert LOCKED_SETTINGS["special_aspects"] == "Parasara"


def test_empty_locked_template_is_valid_pending_evidence() -> None:
    assert validate_witness_rows(witness_template_rows()) == []


def test_entered_value_requires_hashed_evidence_and_reviewer() -> None:
    rows = witness_template_rows()
    rows[0]["jhora_value_virupa"] = "10.0"

    issues = validate_witness_rows(rows)

    assert any("evidence file is missing" in issue for issue in issues)
    assert any("reviewer is missing" in issue for issue in issues)
    assert any("capture timestamp is missing" in issue for issue in issues)
