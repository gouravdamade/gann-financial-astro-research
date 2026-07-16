from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest
import swisseph as swe

from sbc.config import load_profile
from sbc.enums import Ayanamsha
from sbc.ephemeris import SwissEphemerisProvider
from sbc.models import GeoLocation


DELHI = GeoLocation(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata", altitude_m=216.0)
MOMENT = datetime(2026, 7, 17, 6, 30, tzinfo=timezone.utc)


def _circular_distance(left: float, right: float) -> float:
    return abs((left - right + 180.0) % 360.0 - 180.0)


def test_raman_positions_record_speed_flags_and_ketu_provenance() -> None:
    settings = load_profile("sbc_raman_foundation_v1").astro_settings
    positions = SwissEphemerisProvider().positions(MOMENT, ("SUN", "MOON", "RAHU", "KETU"), settings, DELHI)
    by_body = {item.body: item for item in positions}
    assert by_body["SUN"].ayanamsha is Ayanamsha.RAMAN
    assert by_body["SUN"].evidence.returned_flags & swe.FLG_SPEED
    assert by_body["SUN"].evidence.calculation_mode in {"SWISSEPH", "MOSHIER_FALLBACK"}
    assert isinstance(by_body["MOON"].longitude_speed_deg_per_day, float)
    assert _circular_distance(by_body["KETU"].longitude_deg, by_body["RAHU"].longitude_deg) == pytest.approx(180.0)
    assert by_body["KETU"].derived_from == "RAHU_PLUS_180_DEG"


def test_raman_and_lahiri_are_separate_explicit_calculations() -> None:
    primary = load_profile("sbc_raman_foundation_v1").astro_settings
    comparison = replace(primary, ayanamsha=Ayanamsha.LAHIRI)
    provider = SwissEphemerisProvider()
    raman = provider.positions(MOMENT, ("SATURN",), primary, DELHI)[0]
    lahiri = provider.positions(MOMENT, ("SATURN",), comparison, DELHI)[0]
    assert _circular_distance(raman.longitude_deg, lahiri.longitude_deg) > 0.25


def test_naive_timestamp_is_rejected() -> None:
    settings = load_profile("sbc_raman_foundation_v1").astro_settings
    with pytest.raises(ValueError, match="timezone-aware"):
        SwissEphemerisProvider().positions(datetime(2026, 7, 17, 6, 30), ("SUN",), settings, DELHI)


def test_sunrise_contract_returns_a_plausible_local_morning() -> None:
    settings = load_profile("sbc_raman_foundation_v1").astro_settings
    sunrise_utc = SwissEphemerisProvider().sunrise_for_local_date(date(2026, 7, 17), DELHI, settings)
    sunrise_local = sunrise_utc.astimezone(ZoneInfo("Asia/Kolkata"))
    assert sunrise_local.date() == date(2026, 7, 17)
    assert 4 <= sunrise_local.hour <= 8
