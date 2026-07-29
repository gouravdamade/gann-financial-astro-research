from __future__ import annotations

from pathlib import Path

from jhora_sthana_subcomponent_witness_protocol import (
    CAPTURED_STATUS,
    STHANA_SUBCOMPONENTS,
    read_csv,
    sha256,
    validate_against_top_level_sthana,
    validate_witness_rows,
    witness_template_rows,
)


TOP_LEVEL_WITNESS = (
    Path(__file__).parent
    / "status"
    / "evidence"
    / "jhora_shadbala_20260723"
    / "jhora_shadbala_witness_completed_20260726.csv"
)


def test_template_is_complete_and_pending() -> None:
    rows = witness_template_rows()

    assert len(rows) == 175
    assert {
        row["sthana_subcomponent"] for row in rows
    } == set(STHANA_SUBCOMPONENTS)
    assert any(
        "visible witness value is missing" in issue
        for issue in validate_witness_rows(rows)
    )


def test_visible_complete_witness_can_validate(tmp_path: Path) -> None:
    evidence = tmp_path / "visible-sthana-breakdown.png"
    evidence.write_bytes(b"locked visible witness")
    evidence_hash = sha256(evidence)
    top_level_rows = read_csv(TOP_LEVEL_WITNESS)
    sthana_totals = {
        (row["sample_id"], row["planet"]): float(row["jhora_value_virupa"])
        for row in top_level_rows
        if row["measure"] == "sthana"
    }
    rows = witness_template_rows()
    for row in rows:
        total = sthana_totals[(row["sample_id"], row["planet"])]
        row["jhora_value_virupa"] = str(total / len(STHANA_SUBCOMPONENTS))
        row["evidence_path"] = str(evidence)
        row["evidence_sha256"] = evidence_hash
        row["reviewer"] = "independent visible capture"
        row["captured_at_utc"] = "2026-07-29T08:30:00Z"
        row["status"] = CAPTURED_STATUS

    assert validate_witness_rows(rows) == []
    assert validate_against_top_level_sthana(rows, top_level_rows) == []


def test_inferred_values_cannot_hide_top_level_mismatch(tmp_path: Path) -> None:
    evidence = tmp_path / "visible-sthana-breakdown.png"
    evidence.write_bytes(b"locked visible witness")
    evidence_hash = sha256(evidence)
    rows = witness_template_rows()
    for row in rows:
        row["jhora_value_virupa"] = "0"
        row["evidence_path"] = str(evidence)
        row["evidence_sha256"] = evidence_hash
        row["reviewer"] = "independent visible capture"
        row["captured_at_utc"] = "2026-07-29T08:30:00Z"
        row["status"] = CAPTURED_STATUS

    issues = validate_against_top_level_sthana(rows, read_csv(TOP_LEVEL_WITNESS))

    assert len(issues) == 35
    assert all("differs from locked top-level Sthana" in issue for issue in issues)
