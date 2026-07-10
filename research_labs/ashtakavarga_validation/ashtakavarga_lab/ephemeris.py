from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from .constants import PLANETS
from .core import sign_from_longitude


BODY_IDS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MARS": swe.MARS,
    "MERCURY": swe.MERCURY,
    "JUPITER": swe.JUPITER,
    "VENUS": swe.VENUS,
    "SATURN": swe.SATURN,
}


def configure(config: dict[str, Any]) -> None:
    ayanamsa = str(config.get("doctrine", {}).get("ayanamsa", "Raman")).strip().lower()
    if ayanamsa != "raman":
        raise ValueError(f"Version 1 supports only the isolated Raman adaptation, got {ayanamsa!r}")
    swe.set_sid_mode(swe.SIDM_RAMAN)
    for candidate in config.get("ephemeris", {}).get("search_paths", []):
        path = Path(str(candidate))
        if path.exists():
            swe.set_ephe_path(str(path))
            break


def parse_local_datetime(profile: dict[str, Any]) -> datetime:
    local = datetime.fromisoformat(str(profile["local_datetime"]))
    if local.tzinfo is not None:
        return local
    return local.replace(tzinfo=ZoneInfo(str(profile["timezone"])))


def julian_day_ut(value: datetime) -> float:
    utc = value.astimezone(timezone.utc)
    hour = utc.hour + utc.minute / 60.0 + utc.second / 3600.0 + utc.microsecond / 3_600_000_000.0
    return float(swe.julday(utc.year, utc.month, utc.day, hour))


def sidereal_longitudes(value: datetime) -> dict[str, float]:
    jd = julian_day_ut(value)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return {
        planet: float(swe.calc_ut(jd, BODY_IDS[planet], flags)[0][0] % 360.0)
        for planet in PLANETS
    }


def sidereal_ascendant(value: datetime, latitude: float, longitude: float) -> float:
    jd = julian_day_ut(value)
    _, ascmc = swe.houses_ex(jd, float(latitude), float(longitude), b"P", swe.FLG_SIDEREAL)
    return float(ascmc[0] % 360.0)


def natal_context(profile_id: str, profile: dict[str, Any]) -> dict[str, Any]:
    local = parse_local_datetime(profile)
    longitudes = sidereal_longitudes(local)
    ascendant = sidereal_ascendant(local, float(profile["latitude"]), float(profile["longitude"]))
    signs = {planet: sign_from_longitude(lon) for planet, lon in longitudes.items()}
    signs["LAGNA"] = sign_from_longitude(ascendant)
    return {
        "profile_id": profile_id,
        "label": str(profile.get("label", profile_id)),
        "status": str(profile.get("status", "")),
        "local_datetime": local.isoformat(),
        "utc_datetime": local.astimezone(timezone.utc).isoformat(),
        "timezone": str(profile["timezone"]),
        "latitude": float(profile["latitude"]),
        "longitude": float(profile["longitude"]),
        "location": str(profile.get("location", "")),
        "longitudes": longitudes,
        "ascendant_longitude": ascendant,
        "signs": signs,
    }


def transit_signs(value: datetime) -> dict[str, int]:
    return {planet: sign_from_longitude(lon) for planet, lon in sidereal_longitudes(value).items()}
