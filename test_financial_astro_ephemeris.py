import pandas as pd
import swisseph as swe
from financial_astro_ephemeris import (
    build_exact_longitude_map,
    configure_ephemeris,
    fetch_planetary_longitude_single,
    sidereal_house_cusps,
)


def test_true_node_is_not_double_ayanamsa_adjusted() -> None:
    timestamp = pd.Timestamp("2025-05-28T16:30:00Z")
    configure_ephemeris()
    jd = swe.julday(2025, 5, 28, 16.5)
    expected = float(swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360.0)
    actual = fetch_planetary_longitude_single("RAHU", timestamp, "sidereal", "geo")
    assert actual is not None
    assert abs(actual - expected) < 1e-9


def test_sidereal_houses_use_extended_sidereal_api() -> None:
    timestamp = pd.Timestamp("2025-05-28T16:30:00Z")
    configure_ephemeris()
    jd = swe.julday(2025, 5, 28, 16.5)
    expected, _ = swe.houses_ex(jd, 35.6762, 139.6503, b"O", swe.FLG_SIDEREAL)
    actual = sidereal_house_cusps(timestamp, 35.6762, 139.6503)
    assert abs(actual[1] - float(expected[0])) < 1e-9


def test_exact_longitude_map_requests_every_timestamp_without_fill() -> None:
    index = pd.date_range("2025-01-01", periods=4, freq="30min", tz="UTC")
    calls: list[pd.DatetimeIndex] = []

    def fake_fetch(planet, dates, astrology_method="sidereal", coordinate_system="geo"):
        requested = pd.DatetimeIndex(dates)
        calls.append(requested)
        return pd.Series(range(len(requested)), index=requested, dtype=float)

    result = build_exact_longitude_map(["SATURN"], index, fetch_fn=fake_fetch)

    assert len(calls) == 1
    assert calls[0].equals(index)
    assert result["SATURN"].tolist() == [0.0, 1.0, 2.0, 3.0]
