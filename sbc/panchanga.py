from __future__ import annotations

from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from panchanga_doctrine import (
    PANCHANGA_RULE_ID,
    PANCHANGA_SOURCE_STATUS,
    WEEKDAY_LORDS,
    karana_context,
    tithi_context,
    yoga_context,
)

from .enums import VaraBoundary
from .ephemeris import SwissEphemerisProvider
from .models import AstroSettings, GeoLocation, PanchangaSettings, PanchangaState, VaraState
from .nakshatra import sbc_memberships


_TITHI_GROUPS = ("NANDA", "BHADRA", "JAYA", "RIKTA", "PURNA")
_CIVIL_VARA_RULE_ID = "SBC_VARA_CIVIL_MIDNIGHT_V1"
_SUNRISE_VARA_RULE_ID = "SBC_VARA_SUNRISE_SWISSEPH_V1"


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Panchanga timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _vara(
    at_utc: datetime,
    settings: PanchangaSettings,
    astro_settings: AstroSettings,
    location: GeoLocation,
    provider: SwissEphemerisProvider,
) -> VaraState:
    timestamp = _aware_utc(at_utc)
    zone = ZoneInfo(settings.timezone)
    local_timestamp = timestamp.astimezone(zone)
    if settings.vara_boundary is VaraBoundary.CIVIL_MIDNIGHT:
        effective_date = local_timestamp.date()
        boundary_local = datetime.combine(effective_date, time.min, tzinfo=zone)
        boundary_utc = boundary_local.astimezone(timezone.utc)
        algorithm = _CIVIL_VARA_RULE_ID
    else:
        boundary_utc = provider.sunrise_at_or_before(timestamp, location, astro_settings)
        effective_date = boundary_utc.astimezone(zone).date()
        algorithm = settings.sunrise_algorithm
    weekday = int(effective_date.weekday())
    return VaraState(
        weekday=effective_date.strftime("%A"),
        weekday_lord=WEEKDAY_LORDS[weekday],
        effective_local_date=effective_date.isoformat(),
        boundary_mode=settings.vara_boundary,
        boundary_at_utc=boundary_utc,
        timezone=settings.timezone,
        algorithm=algorithm,
        status=PANCHANGA_SOURCE_STATUS,
    )


def _moon_phase(tithi_index: int) -> str:
    if tithi_index == 15:
        return "FULL_MOON_TITHI"
    if tithi_index == 30:
        return "NEW_MOON_TITHI"
    return "WAXING" if tithi_index < 15 else "WANING"


def build_panchanga(
    at_utc: datetime,
    sun_longitude_deg: float,
    moon_longitude_deg: float,
    panchanga_settings: PanchangaSettings,
    astro_settings: AstroSettings,
    location: GeoLocation,
    provider: SwissEphemerisProvider,
) -> PanchangaState:
    tithi = tithi_context(sun_longitude_deg, moon_longitude_deg)
    phase_angle = float(tithi["phase_angle_deg"])
    tithi_index = int(tithi["tithi_index"])
    karana = karana_context(phase_angle)
    yoga = yoga_context(sun_longitude_deg, moon_longitude_deg)
    moon_memberships = sbc_memberships(
        moon_longitude_deg,
        panchanga_settings.abhijit_policy,
        panchanga_settings.abhijit_interval,
    )
    sun_memberships = sbc_memberships(
        sun_longitude_deg,
        panchanga_settings.abhijit_policy,
        panchanga_settings.abhijit_interval,
    )
    vara = _vara(at_utc, panchanga_settings, astro_settings, location, provider)
    vara_rule = _CIVIL_VARA_RULE_ID if panchanga_settings.vara_boundary is VaraBoundary.CIVIL_MIDNIGHT else _SUNRISE_VARA_RULE_ID
    return PanchangaState(
        phase_angle_deg=phase_angle,
        tithi_index=tithi_index,
        tithi_name=str(tithi["tithi_name"]),
        tithi_group=_TITHI_GROUPS[((tithi_index - 1) % 15) % 5],
        paksha=str(tithi["paksha"]),
        moon_phase=_moon_phase(tithi_index),
        karana_index=int(karana["karana_index"]),
        karana_name=str(karana["karana_name"]),
        yoga_angle_deg=float(yoga["yoga_angle_deg"]),
        yoga_index=int(yoga["yoga_index"]),
        yoga_name=str(yoga["yoga_name"]),
        moon_nakshatra=moon_memberships[0],
        sun_nakshatra=sun_memberships[0],
        vara=vara,
        rule_ids=(PANCHANGA_RULE_ID, vara_rule),
        status=PANCHANGA_SOURCE_STATUS,
    )
