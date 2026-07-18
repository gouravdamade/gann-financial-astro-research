from __future__ import annotations

import math

from shadbala_doctrine import minimum_shadbala_total_virupa
from strict_shadbala_doctrine import (
    AHARGANA_AT_ANCHOR,
    AYANA_OBLIQUITY_DEG,
    SAPTAVARGAJA_PYJHORA_PROFILE,
    SAPTAVARGAJA_SOURCE_PROFILE,
    ahargana_lords,
    ayana_bala_virupa,
    astronomical_sunrise_sunset_lmt,
    chesta_bala_virupa,
    chesta_motion_state_bala_virupa,
    chesta_pyjhora_epoch_compatibility_from_inputs,
    d9_navamsa_sign,
    drekkana_bala_virupa,
    drik_base_strength_virupa,
    drik_special_bonus_virupa,
    event_strict_shadbala_context,
    nathonnatha_bala_virupa,
    ojayugma_bala_virupa,
    paksha_bala_virupa,
    saptavargaja_bala,
    strict_drik_bala_for_planet,
    tribhaga_bala_virupa,
    yuddha_bala_virupa,
)


def assert_close(actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if abs(float(actual) - float(expected)) > tolerance:
        raise AssertionError(f"{actual!r} != {expected!r}")


def test_bphs_minimum_totals_include_sun_390_virupa() -> None:
    assert_close(minimum_shadbala_total_virupa("SUN"), 390.0)


def test_drik_six_formula_checkpoints() -> None:
    expected = {
        0: 0,
        29: 0,
        30: 0,
        60: 15,
        90: 45,
        120: 30,
        150: 0,
        180: 60,
        210: 45,
        240: 30,
        270: 15,
        300: 0,
        301: 0,
    }
    for angle, value in expected.items():
        assert_close(drik_base_strength_virupa(angle), value)


def test_drik_v2_wrapper_exposes_normalized_and_raw_audit_fields() -> None:
    longitudes = {
        "SUN": 10.0,
        "MOON": 80.0,
        "MARS": 100.0,
        "MERCURY": 160.0,
        "JUPITER": 250.0,
        "VENUS": 300.0,
        "SATURN": 330.0,
    }
    result = strict_drik_bala_for_planet("SUN", longitudes, 10.0, 80.0)
    assert_close(result["normalization_divisor"], 4.0)
    assert_close(
        result["normalized_net_unrounded_virupa"],
        result["raw_net_virupa"] / result["normalization_divisor"],
    )
    assert len(result["aspects"]) == 6
    assert len(result["aspector_natures"]) == 7
    assert drik_special_bonus_virupa("SATURN", 75.0) == 45.0


def test_navamsa_and_ojayugma() -> None:
    assert d9_navamsa_sign(10.0) == "CANCER"
    assert d9_navamsa_sign(40.0) == "ARIES"
    assert d9_navamsa_sign(70.0) == "CAPRICORN"
    assert_close(ojayugma_bala_virupa("SUN", 10.0), 15.0)
    assert_close(ojayugma_bala_virupa("MOON", 40.0), 15.0)
    assert_close(ojayugma_bala_virupa("VENUS", 32.0), 30.0)


def test_saptavargaja_detail_shape() -> None:
    longitudes = {
        "SUN": 10.0,
        "MOON": 40.0,
        "MARS": 100.0,
        "MERCURY": 160.0,
        "JUPITER": 250.0,
        "VENUS": 300.0,
        "SATURN": 330.0,
    }
    out = saptavargaja_bala("SUN", 10.0, longitudes)
    comparator = saptavargaja_bala(
        "SUN",
        10.0,
        longitudes,
        profile=SAPTAVARGAJA_PYJHORA_PROFILE,
    )
    assert len(out["saptavarga_details"]) == 7
    assert out["saptavargaja_virupa"] > 0
    assert out["profile"] == SAPTAVARGAJA_SOURCE_PROFILE
    assert comparator["profile"] == SAPTAVARGAJA_PYJHORA_PROFILE
    assert all(
        detail["label"] not in {"exaltation", "debilitation"}
        for detail in out["saptavarga_details"]
    )


def test_nathonnatha_local_mean_time() -> None:
    # 00:00 UTC at 139.6503E is about 09:18 local mean time: day planets are strong, night planets weak.
    sun = nathonnatha_bala_virupa("SUN", "2025-03-07T00:00:00+00:00", 139.6503)
    moon = nathonnatha_bala_virupa("MOON", "2025-03-07T00:00:00+00:00", 139.6503)
    mercury = nathonnatha_bala_virupa("MERCURY", "2025-03-07T00:00:00+00:00", 139.6503)
    assert 45.0 <= sun <= 48.0
    assert 12.0 <= moon <= 15.0
    assert_close(mercury, 60.0)


def test_tribhaga_permanent_jupiter_and_segment_lords() -> None:
    morning = "2025-03-07T01:00:00+00:00"
    midday = "2025-03-07T05:00:00+00:00"
    assert_close(
        tribhaga_bala_virupa(
            "JUPITER",
            morning,
            0.0,
            6.0,
            18.0,
        ),
        60.0,
    )
    assert_close(
        tribhaga_bala_virupa(
            "JUPITER",
            midday,
            0.0,
            6.0,
            18.0,
        ),
        60.0,
    )
    assert_close(
        tribhaga_bala_virupa(
            "MERCURY",
            "2025-03-07T07:00:00+00:00",
            0.0,
            6.0,
            18.0,
        ),
        60.0,
    )
    assert_close(
        tribhaga_bala_virupa(
            "SUN",
            "2025-03-07T07:00:00+00:00",
            0.0,
            6.0,
            18.0,
        ),
        0.0,
    )


def test_chesta_and_yuddha_decisions() -> None:
    motion, motion_status = chesta_motion_state_bala_virupa("MARS", -0.2)
    assert_close(motion, 60.0)
    assert motion_status == "vakra_retrograde_speed_diagnostic"
    chesta, status = chesta_bala_virupa(
        "MARS",
        -0.2,
        timestamp="2025-03-07T00:00:00+00:00",
        true_longitude=100.0,
        sun_longitude=10.0,
    )
    assert 0.0 <= chesta <= 60.0
    assert "mean_true_seegrocha" in status
    yuddha, ystatus = yuddha_bala_virupa(
        "MARS",
        {"MARS": 100.0, "MERCURY": 100.5, "JUPITER": 240.0, "VENUS": 300.0, "SATURN": 330.0},
        {"MARS": 0.1, "MERCURY": 0.5},
    )
    assert math.isnan(yuddha)
    assert "fail_closed" in ystatus


def test_pyjhora_epoch_chesta_compatibility_uses_linear_formula() -> None:
    mars = chesta_pyjhora_epoch_compatibility_from_inputs(
        "MARS",
        95.0,
        340.0,
        80.0,
    )
    mercury = chesta_pyjhora_epoch_compatibility_from_inputs(
        "MERCURY",
        15.0,
        350.0,
        20.0,
    )
    sun = chesta_pyjhora_epoch_compatibility_from_inputs(
        "SUN",
        10.0,
        20.0,
        30.0,
    )
    assert_close(mars["mean_true_midpoint_linear_deg"], 87.5)
    assert_close(mars["virupa"], abs(340.0 - 87.5) / 3.0)
    assert_close(mercury["mean_true_midpoint_linear_deg"], 182.5)
    assert_close(mercury["virupa"], abs(20.0 - 182.5) / 3.0)
    assert math.isnan(float(sun["virupa"]))
    assert sun["status"].startswith("structural_not_applicable")


def test_source_aligned_drekkana_paksha_ayana_and_luminary_chesta() -> None:
    assert_close(drekkana_bala_virupa("SUN", 5.0), 15.0)
    assert_close(drekkana_bala_virupa("MERCURY", 15.0), 15.0)
    assert_close(drekkana_bala_virupa("SATURN", 15.0), 15.0)
    assert_close(drekkana_bala_virupa("MOON", 25.0), 15.0)
    assert_close(drekkana_bala_virupa("VENUS", 25.0), 15.0)
    assert_close(paksha_bala_virupa("JUPITER", 0.0, 120.0), 40.0)
    assert_close(paksha_bala_virupa("MOON", 0.0, 120.0), 80.0)
    assert_close(ayana_bala_virupa("SUN", AYANA_OBLIQUITY_DEG), 120.0)
    sun_chesta, sun_status = chesta_bala_virupa("SUN", 1.0, ayana_virupa=72.0)
    moon_chesta, moon_status = chesta_bala_virupa("MOON", 13.0, paksha_virupa=84.0)
    assert_close(sun_chesta, 72.0)
    assert_close(moon_chesta, 84.0)
    assert sun_status == "sun_chesta_equals_ayana"
    assert moon_status == "moon_chesta_equals_paksha"


def test_ahargana_anchor_and_astronomical_sunrise() -> None:
    lords = ahargana_lords("1860-01-01T12:00:00+00:00", 0.0, 6.0)
    assert lords == {
        "ahargana": AHARGANA_AT_ANCHOR,
        "abda": "JUPITER",
        "masa": "SATURN",
        "dina": "SUN",
    }
    sunrise, sunset, status = astronomical_sunrise_sunset_lmt(
        "2025-03-07T00:00:00+00:00",
        139.6503,
        35.6762,
    )
    assert 4.0 <= sunrise <= 8.0
    assert 16.0 <= sunset <= 20.0
    assert status == "swiss_ephemeris_apparent_solar_rise_set_lmt"


def test_avg_all_component_mean_context() -> None:
    longitudes = {
        "SUN": 10.0,
        "MOON": 40.0,
        "MARS": 100.0,
        "MERCURY": 160.0,
        "JUPITER": 250.0,
        "VENUS": 300.0,
        "SATURN": 330.0,
    }
    speeds = {planet: 0.1 for planet in longitudes}
    latitudes = {planet: 0.1 for planet in longitudes}
    declinations = {planet: 5.0 for planet in longitudes}
    ctx = event_strict_shadbala_context(
        "AVG(ALL)",
        "MOON",
        longitudes,
        0.0,
        {},
        "2025-03-07T00:00:00+00:00",
        139.6503,
        speeds,
        latitudes,
        declinations,
        35.6762,
    )
    assert math.isfinite(float(ctx["event_b1_strict_saptavargaja_bala_virupa"]))
    assert math.isfinite(float(ctx["event_b1_strict_kaala_9_bala_virupa"]))
    assert "independent_jhora_component_witness" in ctx["event_strict_shadbala_missing_components"]


def run_all() -> None:
    test_bphs_minimum_totals_include_sun_390_virupa()
    test_drik_six_formula_checkpoints()
    test_drik_v2_wrapper_exposes_normalized_and_raw_audit_fields()
    test_navamsa_and_ojayugma()
    test_saptavargaja_detail_shape()
    test_nathonnatha_local_mean_time()
    test_tribhaga_permanent_jupiter_and_segment_lords()
    test_chesta_and_yuddha_decisions()
    test_pyjhora_epoch_chesta_compatibility_uses_linear_formula()
    test_source_aligned_drekkana_paksha_ayana_and_luminary_chesta()
    test_ahargana_anchor_and_astronomical_sunrise()
    test_avg_all_component_mean_context()


if __name__ == "__main__":
    run_all()
    print("strict shadbala doctrine tests passed")
