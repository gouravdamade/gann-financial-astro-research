from __future__ import annotations

from drik_bala_engine import (
    DRIK_NORMALIZATION_DIVISOR,
    calculate_drik_bala,
    classify_planet_natures,
    special_aspect_bonus_virupa,
)


def test_special_aspect_bonuses_cover_ranges_not_only_exact_angles() -> None:
    assert special_aspect_bonus_virupa("SATURN", 60.0) == 45.0
    assert special_aspect_bonus_virupa("SATURN", 89.99) == 45.0
    assert special_aspect_bonus_virupa("SATURN", 90.0) == 0.0
    assert special_aspect_bonus_virupa("MARS", 119.99) == 15.0
    assert special_aspect_bonus_virupa("MARS", 120.0) == 0.0
    assert special_aspect_bonus_virupa("JUPITER", 269.99) == 30.0
    assert special_aspect_bonus_virupa("JUPITER", 270.0) == 0.0


def test_moon_nature_follows_waxing_and_waning_phase() -> None:
    waxing = classify_planet_natures(
        {
            "SUN": 10.0,
            "MOON": 150.0,
            "MARS": 220.0,
            "MERCURY": 80.0,
            "JUPITER": 260.0,
            "VENUS": 300.0,
            "SATURN": 330.0,
        }
    )
    waning = classify_planet_natures(
        {
            "SUN": 10.0,
            "MOON": 250.0,
            "MARS": 220.0,
            "MERCURY": 80.0,
            "JUPITER": 260.0,
            "VENUS": 300.0,
            "SATURN": 330.0,
        }
    )
    assert waxing["MOON"].nature == "benefic"
    assert "waxing" in waxing["MOON"].reason
    assert waning["MOON"].nature == "malefic"
    assert "waning" in waning["MOON"].reason


def test_mercury_nature_uses_same_sign_associations_and_nearest_tie_breaker() -> None:
    alone = classify_planet_natures(
        {
            "SUN": 40.0,
            "MOON": 80.0,
            "MARS": 120.0,
            "MERCURY": 10.0,
            "JUPITER": 160.0,
            "VENUS": 200.0,
            "SATURN": 240.0,
        }
    )
    with_malefic = classify_planet_natures(
        {
            "SUN": 12.0,
            "MOON": 80.0,
            "MARS": 120.0,
            "MERCURY": 10.0,
            "JUPITER": 160.0,
            "VENUS": 200.0,
            "SATURN": 240.0,
        }
    )
    tied_nearest_benefic = classify_planet_natures(
        {
            "SUN": 2.0,
            "MOON": 80.0,
            "MARS": 120.0,
            "MERCURY": 10.0,
            "JUPITER": 12.0,
            "VENUS": 200.0,
            "SATURN": 240.0,
        }
    )
    assert alone["MERCURY"].nature == "benefic"
    assert with_malefic["MERCURY"].nature == "malefic"
    assert tied_nearest_benefic["MERCURY"].nature == "benefic"
    assert tied_nearest_benefic["MERCURY"].nearest_tie_breaker == "JUPITER"


def test_drik_result_preserves_six_contribution_audit_ledger_and_raw_values() -> None:
    longitudes = {
        "SUN": 10.0,
        "MOON": 80.0,
        "MARS": 100.0,
        "MERCURY": 160.0,
        "JUPITER": 250.0,
        "VENUS": 300.0,
        "SATURN": 330.0,
    }
    result = calculate_drik_bala("SUN", longitudes)
    assert result.available is True
    assert len(result.contributions) == 6
    assert {item.aspector for item in result.contributions} == {
        "MOON",
        "MARS",
        "MERCURY",
        "JUPITER",
        "VENUS",
        "SATURN",
    }
    assert result.raw_net_virupa == round(
        float(result.benefic_raw_virupa) + float(result.malefic_raw_virupa),
        2,
    )
    assert result.normalized_net_unrounded_virupa == (
        float(result.raw_net_virupa) / DRIK_NORMALIZATION_DIVISOR
    )
    assert result.drik_bala_virupa == round(float(result.normalized_net_unrounded_virupa), 2)
    assert all(item.nature_reason for item in result.contributions)
