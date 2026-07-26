from __future__ import annotations

from jhora_witness_capture_assembler import (
    DEFAULT_EVIDENCE_DIR,
    assemble_witness_rows,
)
from jhora_witness_protocol import MEASURES, validate_witness_rows
from pyjhora_external_strength_export import FIXTURES, PLANETS


def test_locked_jhora_capture_assembles_complete_valid_ledger() -> None:
    rows, checks = assemble_witness_rows(DEFAULT_EVIDENCE_DIR)

    assert len(rows) == len(FIXTURES) * len(PLANETS) * len(MEASURES)
    assert len(checks) == len(FIXTURES) * len(PLANETS)
    assert validate_witness_rows(rows) == []
    assert all(row["jhora_value_virupa"] for row in rows)
    assert all(row["status"] == "captured_locked_manual_jhora" for row in rows)
    assert {
        (check["planet"], check["total_excluded_components"])
        for check in checks
        if check["total_excluded_components"]
    } == {("SUN", "chesta"), ("MOON", "chesta")}
    assert max(
        abs(float(check["component_residual_virupa"])) for check in checks
    ) <= 0.04
    assert max(abs(float(check["rupas_residual_virupa"])) for check in checks) <= 0.31
