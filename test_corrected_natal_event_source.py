import pandas as pd

from build_corrected_natal_event_source import (
    ASTRONOMY_CONTRACT,
    detect_orb_windows,
    parse_entities,
    reference_timestamp,
    stable_event_id,
)
from financial_astro_ephemeris import configure_ephemeris, fetch_planetary_longitude_single


def test_entity_parser_preserves_avg_group_as_one_entity() -> None:
    assert parse_entities("Sun, Moon, AVG(all)") == ("SUN", "MOON", "AVG(ALL)")


def test_orb_window_interpolates_entry_exit_and_uses_minimum_orb_peak() -> None:
    index = pd.date_range("2025-01-01", periods=4, freq="1h", tz="UTC")
    series = pd.Series([87.0, 89.5, 90.2, 92.0], index=index)

    windows = detect_orb_windows(series, 0.0, target_angle=90.0, orb_limit=1.0)

    assert len(windows) == 1
    assert index[0] < windows[0].start < index[1]
    assert index[2] < windows[0].end < index[3]
    assert windows[0].peak == index[2]
    assert abs(windows[0].peak_orb_deg - 0.2) < 1e-12


def test_reference_timestamp_keeps_declared_fixed_tokyo_offset() -> None:
    configure_ephemeris()
    timestamp = reference_timestamp("1889-02-11", "00:00", "+09:00")
    moon = fetch_planetary_longitude_single("MOON", timestamp, "sidereal", "geo")

    assert timestamp.isoformat() == "1889-02-11T00:00:00+09:00"
    assert moon is not None
    assert abs(moon - 61.08767031037019) < 1e-9


def test_event_id_is_scoped_and_role_ordered() -> None:
    start = pd.Timestamp("2025-01-01T00:00:00+05:30")
    end = pd.Timestamp("2025-01-01T02:00:00+05:30")
    forward = stable_event_id("MOON", "SUN", "trine", start, end)
    reversed_roles = stable_event_id("SUN", "MOON", "trine", start, end)

    assert ASTRONOMY_CONTRACT.startswith("RAMAN_SWISSEPH_SINGLE_SIDEREAL_")
    assert forward != reversed_roles
