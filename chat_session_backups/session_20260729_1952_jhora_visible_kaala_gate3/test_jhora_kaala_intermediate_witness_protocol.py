from __future__ import annotations

import json
from pathlib import Path

from jhora_kaala_formula_profile_reconciliation import (
    AYANA_OBLIQUITY_DEG,
    NORTH_STRONG,
    SOUTH_STRONG,
)
from jhora_kaala_intermediate_witness_protocol import (
    CAPTURED_STATUS,
    EVIDENCE_BUNDLE_CONTRACT,
    ayana_template_rows,
    evidence_bundle_issues,
    hora_template_rows,
    locked_kaala_values,
    read_csv,
    sha256,
    validate_ayana_rows,
    validate_hora_rows,
    witness_gate_summary,
    write_csv,
)


KAALA_WITNESS = (
    Path(__file__).parent
    / "status"
    / "evidence"
    / "jhora_kaala_witness_20260727"
    / "jhora_kaala_profile_comparison_20260727.csv"
)


def _complete_provenance(rows: list[dict[str, str]], evidence: Path) -> None:
    evidence_hash = sha256(evidence)
    for row in rows:
        row["evidence_path"] = str(evidence)
        row["evidence_sha256"] = evidence_hash
        row["reviewer"] = "independent visible capture"
        row["captured_at_utc"] = "2026-07-29T10:00:00Z"
        row["status"] = CAPTURED_STATUS


def _kranti_for_ayana(planet: str, ayana: float) -> float:
    obliquity = AYANA_OBLIQUITY_DEG
    if planet in NORTH_STRONG:
        base = ayana / 2.0 if planet == "SUN" else ayana
        return base * (2.0 * obliquity) / 60.0 - obliquity
    if planet in SOUTH_STRONG:
        return obliquity - ayana * (2.0 * obliquity) / 60.0
    if planet == "MERCURY":
        return ayana * (2.0 * obliquity) / 60.0 - obliquity
    raise AssertionError(f"unsupported test planet {planet}")


def test_templates_are_complete_and_pending() -> None:
    hora_rows = hora_template_rows()
    ayana_rows = ayana_template_rows()

    assert len(hora_rows) == 7
    assert len(ayana_rows) == 7
    assert {row["planet"] for row in hora_rows} == {
        row["planet"] for row in ayana_rows
    }
    assert all(
        row["jhora_sunrise_lmt_display"] == "" for row in hora_rows
    )
    assert all(row["jhora_sunrise_lmt_hour"] == "" for row in hora_rows)
    assert all(
        row["jhora_tropical_longitude_deg"] == "" for row in ayana_rows
    )


def test_evidence_bundle_detects_changed_source(tmp_path: Path) -> None:
    source = tmp_path / "visible-source.jpg"
    source.write_bytes(b"original visible source")
    bundle = tmp_path / "evidence.json"
    bundle.write_text(
        json.dumps(
            {
                "contract": EVIDENCE_BUNDLE_CONTRACT,
                "sources": [
                    {
                        "purpose": "visible source",
                        "path": str(source),
                        "sha256": sha256(source),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    assert evidence_bundle_issues(bundle) == []
    source.write_bytes(b"changed visible source")
    assert evidence_bundle_issues(bundle) == [
        "evidence bundle source 1 hash mismatch"
    ]


def test_complete_visible_hora_boundary_can_validate(tmp_path: Path) -> None:
    evidence = tmp_path / "visible-hora-boundary.png"
    evidence.write_bytes(b"visible locked Hora evidence")
    locked_rows = read_csv(KAALA_WITNESS)
    locked = locked_kaala_values(
        locked_rows,
        sample_id="case_8_event_start",
        measure="hora",
    )
    winner = next(
        planet for planet, value in locked.items() if value == 60.0
    )
    rows = hora_template_rows()
    _complete_provenance(rows, evidence)
    for row in rows:
        row["jhora_sunrise_lmt_display"] = "6:18:36.072"
        row["jhora_sunrise_lmt_hour"] = "6.310020"
        row["jhora_hora_lord"] = winner
        row["jhora_hora_virupa"] = str(locked[row["planet"]])

    assert validate_hora_rows(rows, locked_rows) == []

    rows[0]["jhora_hora_lord"] = "MOON" if winner != "MOON" else "SUN"
    issues = validate_hora_rows(rows, locked_rows)
    assert any("do not share one visible Hora lord" in issue for issue in issues)


def test_complete_visible_ayana_intermediate_can_validate(
    tmp_path: Path,
) -> None:
    evidence = tmp_path / "visible-ayana-intermediate.png"
    evidence.write_bytes(b"visible locked Ayana evidence")
    locked_rows = read_csv(KAALA_WITNESS)
    locked = locked_kaala_values(
        locked_rows,
        sample_id="gann_reference_tokyo",
        measure="ayana",
    )
    rows = ayana_template_rows()
    _complete_provenance(rows, evidence)
    for row in rows:
        planet = row["planet"]
        ayana = locked[planet]
        row["jhora_kranti_deg"] = str(_kranti_for_ayana(planet, ayana))
        row["jhora_ayana_virupa"] = str(ayana)

    assert validate_ayana_rows(rows, locked_rows) == []

    rows[0]["jhora_kranti_deg"] = "0"
    issues = validate_ayana_rows(rows, locked_rows)
    assert any("reconstructed from visible Kranti" in issue for issue in issues)


def test_formula_mismatch_keeps_visible_evidence_complete(
    tmp_path: Path,
) -> None:
    evidence = tmp_path / "visible-ayana-mismatch.png"
    evidence.write_bytes(b"visible locked Ayana mismatch evidence")
    locked_rows = read_csv(KAALA_WITNESS)
    locked = locked_kaala_values(
        locked_rows,
        sample_id="gann_reference_tokyo",
        measure="ayana",
    )
    hora_rows = hora_template_rows()
    ayana_rows = ayana_template_rows()
    _complete_provenance(hora_rows, evidence)
    _complete_provenance(ayana_rows, evidence)
    hora_locked = locked_kaala_values(
        locked_rows,
        sample_id="case_8_event_start",
        measure="hora",
    )
    hora_lord = next(
        planet for planet, value in hora_locked.items() if value == 60.0
    )
    for row in hora_rows:
        row["jhora_sunrise_lmt_display"] = "6:18:36"
        row["jhora_sunrise_lmt_hour"] = "6.31"
        row["jhora_hora_lord"] = hora_lord
        row["jhora_hora_virupa"] = str(hora_locked[row["planet"]])
    for row in ayana_rows:
        row["jhora_tropical_longitude_deg"] = "0"
        row["jhora_ayana_virupa"] = str(locked[row["planet"]])

    hora_path = tmp_path / "hora.csv"
    ayana_path = tmp_path / "ayana.csv"
    write_csv(hora_path, hora_rows)
    write_csv(ayana_path, ayana_rows)
    gate = witness_gate_summary(
        hora_path=hora_path,
        ayana_path=ayana_path,
        kaala_witness_path=KAALA_WITNESS,
    )

    assert gate["status"] == (
        "visible_packet_complete_formula_candidate_rejected"
    )
    assert gate["evidenceComplete"] is True
    assert gate["formulaCertified"] is False
    assert gate["formulaIssues"]
    assert gate["issues"] == []


def test_pending_templates_keep_machine_gate_blocked(tmp_path: Path) -> None:
    hora_path = tmp_path / "hora.csv"
    ayana_path = tmp_path / "ayana.csv"
    write_csv(hora_path, hora_template_rows())
    write_csv(ayana_path, ayana_template_rows())

    gate = witness_gate_summary(
        hora_path=hora_path,
        ayana_path=ayana_path,
        kaala_witness_path=KAALA_WITNESS,
    )

    assert gate["status"] == (
        "blocked_pending_visible_kaala_intermediate_witness"
    )
    assert gate["evidenceComplete"] is False
    assert gate["formulaCertified"] is False
    assert gate["productionChangeAllowed"] is False


def test_completed_ayana_is_preserved_while_hora_remains_pending(
    tmp_path: Path,
) -> None:
    evidence = tmp_path / "visible-ayana.png"
    evidence.write_bytes(b"visible locked Ayana evidence")
    locked_rows = read_csv(KAALA_WITNESS)
    locked = locked_kaala_values(
        locked_rows,
        sample_id="gann_reference_tokyo",
        measure="ayana",
    )
    ayana_rows = ayana_template_rows()
    _complete_provenance(ayana_rows, evidence)
    for row in ayana_rows:
        ayana = locked[row["planet"]]
        row["jhora_kranti_deg"] = str(
            _kranti_for_ayana(row["planet"], ayana)
        )
        row["jhora_ayana_virupa"] = str(ayana)

    hora_path = tmp_path / "hora_pending.csv"
    ayana_path = tmp_path / "ayana_complete.csv"
    write_csv(hora_path, hora_template_rows())
    write_csv(ayana_path, ayana_rows)
    gate = witness_gate_summary(
        hora_path=hora_path,
        ayana_path=ayana_path,
        kaala_witness_path=KAALA_WITNESS,
    )

    assert gate["status"] == (
        "blocked_pending_visible_hora_intermediate_witness"
    )
    assert gate["horaEvidenceComplete"] is False
    assert gate["ayanaEvidenceComplete"] is True
    assert gate["evidenceComplete"] is False
    assert gate["issues"] == []
