from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from sbc.config import load_profile
from sbc.enums import VaraBoundary
from sbc.models import GeoLocation
from sbc.panchanga import build_panchanga


LOCATION = GeoLocation(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata")


class FakeSunriseProvider:
    def __init__(self, boundary: datetime) -> None:
        self.boundary = boundary

    def sunrise_at_or_before(self, *_args: object, **_kwargs: object) -> datetime:
        return self.boundary


def test_panchanga_formula_foundation_and_civil_vara() -> None:
    profile = load_profile("sbc_raman_foundation_v1")
    state = build_panchanga(
        datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc),
        0.0,
        0.0,
        profile.panchanga_settings,
        profile.astro_settings,
        LOCATION,
        FakeSunriseProvider(datetime(2026, 7, 17, 0, 0, tzinfo=timezone.utc)),
    )
    assert state.tithi_index == 1
    assert state.tithi_name == "Pratipada"
    assert state.tithi_group == "NANDA"
    assert state.karana_name == "Kimstughna"
    assert state.yoga_name == "Vishkambha"
    assert state.moon_nakshatra.name == "Ashwini"
    assert state.vara.weekday == "Friday"
    assert state.vara.weekday_lord == "VENUS"


def test_sunrise_vara_uses_effective_local_date_from_boundary() -> None:
    profile = load_profile("sbc_raman_foundation_v1")
    panchanga_settings = replace(profile.panchanga_settings, vara_boundary=VaraBoundary.SUNRISE_BASED)
    state = build_panchanga(
        datetime(2026, 7, 17, 0, 0, tzinfo=timezone.utc),
        10.0,
        20.0,
        panchanga_settings,
        profile.astro_settings,
        LOCATION,
        FakeSunriseProvider(datetime(2026, 7, 16, 0, 30, tzinfo=timezone.utc)),
    )
    assert state.vara.effective_local_date == "2026-07-16"
    assert state.vara.weekday == "Thursday"
    assert state.vara.weekday_lord == "JUPITER"
    assert state.vara.boundary_mode is VaraBoundary.SUNRISE_BASED
