from pathlib import Path

import pytest

from jhora_kaala_formula_profile_reconciliation import (
    DEFAULT_DOCTRINE_CONFIG,
    DEFAULT_VISIBLE_COMPARISON,
    ayana_from_kranti,
    build_rows,
    nathonnatha_from_hour,
    projected_kranti_deg,
    read_visible_values,
    summarize_profiles,
    worked_example_summary,
)


def test_visible_formula_matrix_is_complete() -> None:
    values = read_visible_values(DEFAULT_VISIBLE_COMPARISON)

    assert len(values) == 5 * 7 * 3
    assert values[("case_8_event_start", "MOON", "hora")] == 60.0
    assert values[("case_8_event_start", "SATURN", "hora")] == 0.0


def test_nathonnatha_source_hour_symmetry() -> None:
    assert nathonnatha_from_hour("SUN", 12.0) == 60.0
    assert nathonnatha_from_hour("MOON", 12.0) == 0.0
    assert nathonnatha_from_hour("SUN", 0.0) == 0.0
    assert nathonnatha_from_hour("MOON", 0.0) == 60.0
    assert nathonnatha_from_hour("MERCURY", 4.0) == 60.0


def test_projected_kranti_uses_tropical_longitude() -> None:
    assert projected_kranti_deg(0.0) == pytest.approx(0.0)
    assert projected_kranti_deg(90.0) == pytest.approx(23.45)
    assert projected_kranti_deg(270.0) == pytest.approx(-23.45)
    assert ayana_from_kranti("SUN", 23.45) == pytest.approx(120.0)
    assert ayana_from_kranti("MOON", -23.45) == pytest.approx(60.0)


def test_locked_profile_results_and_hora_boundary() -> None:
    rows, boundary = build_rows(
        visible=read_visible_values(DEFAULT_VISIBLE_COMPARISON),
        config_path=DEFAULT_DOCTRINE_CONFIG,
    )
    summary = summarize_profiles(rows)

    assert len(rows) == 5 * 7 * 6
    assert summary["nathonnatha_lmt_source"]["pass"] == 11
    assert summary["nathonnatha_lmt_source"]["maeVirupa"] == pytest.approx(
        1.484554286
    )
    assert summary["hora_astronomical_sunrise"]["pass"] == 35
    assert summary["hora_variable_day_night"]["pass"] == 27
    assert summary["ayana_actual_declination"]["pass"] == 13
    assert summary["ayana_tropical_projection"]["pass"] == 30
    assert summary["ayana_tropical_projection"]["recentPass"] == 28
    assert summary["ayana_tropical_projection"]["historicalPass"] == 2

    case_8 = boundary["case_8_event_start"]
    assert case_8["currentLord"] == "MOON"
    assert case_8["jhoraLord"] == "MOON"
    assert case_8["gapMinutes"] == pytest.approx(3.436256)


def test_published_worked_tables_are_corroborative() -> None:
    summary = worked_example_summary()
    nathonnatha = summary["nathonnatha"]

    assert Path(summary["source"]["path"]).name.endswith("jaya-sekhar.txt")
    assert len(summary["source"]["sha256"]) == 64
    assert nathonnatha[0]["calculatedDayVirupa"] == pytest.approx(26.083333)
    assert nathonnatha[1]["calculatedNightVirupa"] == pytest.approx(40.190733)
    assert summary["ayana"]["maeVirupa"] == pytest.approx(0.416975643)
    assert summary["ayana"]["maxErrorVirupa"] == pytest.approx(1.097644)
