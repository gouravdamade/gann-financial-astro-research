from datetime import datetime, timezone
from pathlib import Path

import pytest

from jhora_kaala_formula_profile_reconciliation import (
    DEFAULT_DOCTRINE_CONFIG,
    DEFAULT_VISIBLE_COMPARISON,
    astronomical_midnight_context,
    ayana_from_bphs_khanda,
    ayana_from_kranti,
    bphs_ayana_bhuja_deg,
    bphs_ayana_khanda_yoga_deg,
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


def test_bphs_ayana_bhuja_khanda_boundaries() -> None:
    expected_bhuja = {
        0.0: 0.0,
        30.0: 30.0,
        60.0: 60.0,
        90.0: 90.0,
        180.0: 0.0,
        270.0: 90.0,
        360.0: 0.0,
    }
    for longitude, expected in expected_bhuja.items():
        assert bphs_ayana_bhuja_deg(longitude) == pytest.approx(expected)
    assert bphs_ayana_khanda_yoga_deg(0.0) == pytest.approx(0.0)
    assert bphs_ayana_khanda_yoga_deg(30.0) == pytest.approx(45.0)
    assert bphs_ayana_khanda_yoga_deg(60.0) == pytest.approx(78.0)
    assert bphs_ayana_khanda_yoga_deg(90.0) == pytest.approx(90.0)
    with pytest.raises(ValueError):
        bphs_ayana_khanda_yoga_deg(90.1)

    assert ayana_from_bphs_khanda("SUN", 90.0) == pytest.approx(120.0)
    assert ayana_from_bphs_khanda("SUN", 270.0) == pytest.approx(0.0)
    assert ayana_from_bphs_khanda("MOON", 90.0) == pytest.approx(0.0)
    assert ayana_from_bphs_khanda("MOON", 270.0) == pytest.approx(60.0)
    assert ayana_from_bphs_khanda("MERCURY", 270.0) == pytest.approx(60.0)


def test_astronomical_midnight_uses_adjacent_sunset_and_sunrise() -> None:
    event_lmt = datetime(
        2025,
        3,
        7,
        23,
        18,
        36,
        72000,
        tzinfo=timezone.utc,
    )
    result = astronomical_midnight_context(
        event_lmt=event_lmt,
        longitude=139.6503,
        latitude=35.6762,
    )

    assert result["selectedMidnightLmtHour"] == pytest.approx(24.176859683)
    assert result["distanceFromMidnightHours"] == pytest.approx(0.866839683)
    assert result["dayStrengthVirupa"] == pytest.approx(4.334198413)
    assert result["previousSunsetLmtHour"] < 0.0
    assert result["nextSunriseLmtHour"] > 24.0


def test_locked_profile_results_and_hora_boundary() -> None:
    rows, boundary, midnight = build_rows(
        visible=read_visible_values(DEFAULT_VISIBLE_COMPARISON),
        config_path=DEFAULT_DOCTRINE_CONFIG,
    )
    summary = summarize_profiles(rows)

    assert len(rows) == 5 * 7 * 8
    assert summary["nathonnatha_lmt_source"]["pass"] == 11
    assert summary["nathonnatha_lmt_source"]["maeVirupa"] == pytest.approx(
        1.484554286
    )
    assert summary["nathonnatha_astronomical_midnight"]["pass"] == 11
    assert summary["nathonnatha_astronomical_midnight"][
        "maeVirupa"
    ] == pytest.approx(1.59189241)
    assert summary["hora_astronomical_sunrise"]["pass"] == 35
    assert summary["hora_variable_day_night"]["pass"] == 27
    assert summary["ayana_actual_declination"]["pass"] == 13
    assert summary["ayana_tropical_projection"]["pass"] == 30
    assert summary["ayana_tropical_projection"]["recentPass"] == 28
    assert summary["ayana_tropical_projection"]["historicalPass"] == 2
    assert summary["ayana_bphs_ch27_khanda_source"]["pass"] == 25
    assert summary["ayana_bphs_ch27_khanda_source"][
        "maeVirupa"
    ] == pytest.approx(0.376257605)
    assert summary["ayana_bphs_ch27_khanda_source"][
        "maxErrorVirupa"
    ] == pytest.approx(1.720463737)
    assert summary["ayana_bphs_ch27_khanda_source"]["recentPass"] == 24
    assert summary["ayana_bphs_ch27_khanda_source"]["historicalPass"] == 1

    case_8 = boundary["case_8_event_start"]
    assert case_8["currentLord"] == "MOON"
    assert case_8["jhoraLord"] == "MOON"
    assert case_8["gapMinutes"] == pytest.approx(3.436256)
    assert midnight["case_8_event_start"]["dayStrengthVirupa"] == pytest.approx(
        4.334198413
    )


def test_published_worked_tables_are_corroborative() -> None:
    summary = worked_example_summary()
    nathonnatha = summary["nathonnatha"]

    assert Path(summary["source"]["path"]).name.endswith("jaya-sekhar.txt")
    assert len(summary["source"]["sha256"]) == 64
    assert nathonnatha[0]["calculatedDayVirupa"] == pytest.approx(26.083333)
    assert nathonnatha[1]["calculatedNightVirupa"] == pytest.approx(40.190733)
    assert summary["ayana"]["maeVirupa"] == pytest.approx(0.416975643)
    assert summary["ayana"]["maxErrorVirupa"] == pytest.approx(1.097644)
    assert summary["ayanaBphs"]["maeVirupa"] == pytest.approx(0.5738205)
    assert summary["ayanaBphs"]["maxErrorVirupa"] == pytest.approx(1.576816)
