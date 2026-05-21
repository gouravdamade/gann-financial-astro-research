from __future__ import annotations

import math

from strict_shadbala_doctrine import (
    aggregate_components,
    chesta_bala_virupa,
    d9_navamsa_sign,
    drik_base_strength_virupa,
    event_strict_shadbala_context,
    nathonnatha_bala_virupa,
    ojayugma_bala_virupa,
    saptavargaja_bala,
    yuddha_bala_virupa,
)


def assert_close(actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if abs(float(actual) - float(expected)) > tolerance:
        raise AssertionError(f"{actual!r} != {expected!r}")


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
    assert len(out["saptavarga_details"]) == 7
    assert out["saptavargaja_virupa"] > 0


def test_nathonnatha_local_mean_time() -> None:
    # 00:00 UTC at 139.6503E is about 09:18 local mean time: day planets are strong, night planets weak.
    sun = nathonnatha_bala_virupa("SUN", "2025-03-07T00:00:00+00:00", 139.6503)
    moon = nathonnatha_bala_virupa("MOON", "2025-03-07T00:00:00+00:00", 139.6503)
    mercury = nathonnatha_bala_virupa("MERCURY", "2025-03-07T00:00:00+00:00", 139.6503)
    assert 45.0 <= sun <= 48.0
    assert 12.0 <= moon <= 15.0
    assert_close(mercury, 60.0)


def test_chesta_and_yuddha_decisions() -> None:
    chesta, status = chesta_bala_virupa("MARS", -0.2)
    assert_close(chesta, 60.0)
    assert status == "retrograde_high_chesta"
    yuddha, ystatus = yuddha_bala_virupa(
        "MARS",
        {"MARS": 100.0, "MERCURY": 100.5, "JUPITER": 240.0, "VENUS": 300.0, "SATURN": 330.0},
        {"MARS": 0.1, "MERCURY": 0.5},
    )
    assert_close(yuddha, 30.0)
    assert "winner" in ystatus


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
    )
    assert math.isfinite(float(ctx["event_b1_strict_saptavargaja_bala_virupa"]))
    assert math.isfinite(float(ctx["event_b1_strict_kaala_9_bala_virupa"]))
    assert "external_canonical_calculator_validation" in ctx["event_strict_shadbala_missing_components"]


def run_all() -> None:
    test_drik_six_formula_checkpoints()
    test_navamsa_and_ojayugma()
    test_saptavargaja_detail_shape()
    test_nathonnatha_local_mean_time()
    test_chesta_and_yuddha_decisions()
    test_avg_all_component_mean_context()


if __name__ == "__main__":
    run_all()
    print("strict shadbala doctrine tests passed")
