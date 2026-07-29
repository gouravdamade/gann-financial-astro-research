from __future__ import annotations

import copy
from pathlib import Path

import pytest

from jhora_kaala_capture_assistant import (
    ASSISTANT_CONTRACT,
    CAPTURE_NOTE,
    CaptureValidationError,
    assemble_hora_capture_rows,
    export_ayana_packet,
    export_hora_packet,
    packet_status,
)
from jhora_kaala_formula_profile_reconciliation import ayana_from_kranti
from jhora_kaala_intermediate_witness_protocol import (
    AYANA_SAMPLE_ID,
    DEFAULT_AYANA_TEMPLATE,
    DEFAULT_HORA_TEMPLATE,
    DEFAULT_KAALA_WITNESS,
    HORA_SAMPLE_ID,
    PLANETS,
    locked_kaala_values,
    read_csv,
    write_csv,
)
from jhora_witness_protocol import sha256


CAPTURE_TIME = "2026-07-29T10:00:00Z"
REVIEWER = "Human JHora reviewer"


def _evidence(tmp_path: Path) -> Path:
    path = tmp_path / "uncropped_jhora_evidence.png"
    path.write_bytes(b"visible-jhora-test-evidence")
    return path


def _hora_awards(locked_rows: list[dict[str, str]]) -> dict[str, float]:
    return locked_kaala_values(
        locked_rows,
        sample_id=HORA_SAMPLE_ID,
        measure="hora",
    )


def _hora_lord(awards: dict[str, float]) -> str:
    winners = [
        planet for planet, value in awards.items() if value == pytest.approx(60)
    ]
    assert len(winners) == 1
    return winners[0]


def _combined_locked_witness(tmp_path: Path) -> tuple[Path, dict[str, float]]:
    rows = copy.deepcopy(read_csv(DEFAULT_KAALA_WITNESS))
    ayana_values = {
        planet: ayana_from_kranti(planet, 0.0) for planet in PLANETS
    }
    for row in rows:
        if (
            row["sample_id"] == AYANA_SAMPLE_ID
            and row["measure"] == "ayana"
        ):
            row["jhora_value_virupa"] = f"{ayana_values[row['planet']]:.12g}"
    path = tmp_path / "combined_locked_kaala.csv"
    write_csv(path, rows)
    return path, ayana_values


def test_hora_capture_binds_visible_evidence_without_mutating_template(
    tmp_path: Path,
) -> None:
    template = read_csv(DEFAULT_HORA_TEMPLATE)
    original = copy.deepcopy(template)
    locked = read_csv(DEFAULT_KAALA_WITNESS)
    awards = _hora_awards(locked)
    evidence = _evidence(tmp_path)

    rows = assemble_hora_capture_rows(
        template,
        evidence_path=evidence,
        reviewer=REVIEWER,
        sunrise_lmt_display="6:07:30",
        hora_lord=_hora_lord(awards),
        awards=awards,
        captured_at_utc=CAPTURE_TIME,
    )

    assert template == original
    assert len(rows) == len(PLANETS)
    assert {row["jhora_sunrise_lmt_display"] for row in rows} == {
        "6:07:30"
    }
    assert {row["jhora_sunrise_lmt_hour"] for row in rows} == {"6.125"}
    assert {row["evidence_path"] for row in rows} == {
        str(evidence.resolve())
    }
    assert {row["evidence_sha256"] for row in rows} == {sha256(evidence)}
    assert {row["captured_at_utc"] for row in rows} == {CAPTURE_TIME}
    assert {row["notes"] for row in rows} == {CAPTURE_NOTE}


def test_complete_assistant_packet_passes_existing_fail_closed_gate(
    tmp_path: Path,
) -> None:
    evidence = _evidence(tmp_path)
    locked_path, ayana_values = _combined_locked_witness(tmp_path)
    locked_rows = read_csv(locked_path)
    awards = _hora_awards(locked_rows)
    hora_output = tmp_path / "hora_completed.csv"
    ayana_output = tmp_path / "ayana_completed.csv"

    hora_result = export_hora_packet(
        evidence_path=evidence,
        reviewer=REVIEWER,
        sunrise_lmt_display="6:07:30",
        hora_lord=_hora_lord(awards),
        awards=awards,
        output_path=hora_output,
        locked_kaala_path=locked_path,
        captured_at_utc=CAPTURE_TIME,
    )
    ayana_result = export_ayana_packet(
        evidence_path=evidence,
        reviewer=REVIEWER,
        values={
            planet: {
                "tropical_longitude_deg": "",
                "kranti_deg": 0.0,
                "ayana_virupa": ayana_values[planet],
            }
            for planet in PLANETS
        },
        output_path=ayana_output,
        locked_kaala_path=locked_path,
        captured_at_utc=CAPTURE_TIME,
    )
    gate = packet_status(
        hora_path=hora_output,
        ayana_path=ayana_output,
        locked_kaala_path=locked_path,
    )

    assert hora_result["contract"] == ASSISTANT_CONTRACT
    assert ayana_result["contract"] == ASSISTANT_CONTRACT
    assert gate["status"] == "visible_packet_complete_not_formula_certified"
    assert gate["evidenceComplete"] is True
    assert gate["formulaCertified"] is False
    assert gate["productionChangeAllowed"] is False


def test_visible_ayana_observation_is_preserved_when_formula_candidate_fails(
    tmp_path: Path,
) -> None:
    evidence = _evidence(tmp_path)
    locked_rows = read_csv(DEFAULT_KAALA_WITNESS)
    locked = locked_kaala_values(
        locked_rows,
        sample_id=AYANA_SAMPLE_ID,
        measure="ayana",
    )
    output = tmp_path / "ayana_observed_formula_mismatch.csv"

    result = export_ayana_packet(
        evidence_path=evidence,
        reviewer=REVIEWER,
        values={
            planet: {
                "tropical_longitude_deg": 0.0,
                "kranti_deg": "",
                "ayana_virupa": locked[planet],
            }
            for planet in PLANETS
        },
        output_path=output,
        captured_at_utc=CAPTURE_TIME,
    )

    assert output.is_file()
    assert result["status"] == (
        "valid_ayana_observation_written_formula_candidate_rejected"
    )
    assert result["formulaIssues"]


def test_rejected_capture_does_not_write_completed_packet(
    tmp_path: Path,
) -> None:
    evidence = _evidence(tmp_path)
    locked = read_csv(DEFAULT_KAALA_WITNESS)
    awards = _hora_awards(locked)
    awards["SUN"] = 60.0
    output = tmp_path / "must_not_exist.csv"

    with pytest.raises(CaptureValidationError):
        export_hora_packet(
            evidence_path=evidence,
            reviewer=REVIEWER,
            sunrise_lmt_display="6:07:30",
            hora_lord="SUN",
            awards=awards,
            output_path=output,
            captured_at_utc=CAPTURE_TIME,
        )

    assert not output.exists()


def test_assistant_refuses_to_overwrite_pending_templates(
    tmp_path: Path,
) -> None:
    evidence = _evidence(tmp_path)
    locked = read_csv(DEFAULT_KAALA_WITNESS)
    awards = _hora_awards(locked)

    with pytest.raises(
        ValueError,
        match="may not overwrite the pending template",
    ):
        export_hora_packet(
            evidence_path=evidence,
            reviewer=REVIEWER,
            sunrise_lmt_display="6:07:30",
            hora_lord=_hora_lord(awards),
            awards=awards,
            output_path=DEFAULT_HORA_TEMPLATE,
            template_path=DEFAULT_HORA_TEMPLATE,
            captured_at_utc=CAPTURE_TIME,
        )

    assert DEFAULT_AYANA_TEMPLATE.is_file()
