from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import swisseph as swe

from doctrine_config import configure_swiss_ephemeris_sidereal


IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

BODY_IDS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
    "URANUS": swe.URANUS,
    "NEPTUNE": swe.NEPTUNE,
    "PLUTO": swe.PLUTO,
    "EARTH": swe.EARTH,
    "RAHU": swe.TRUE_NODE,
}

EPHEMERIS_PATH_CANDIDATES = (
    Path(r"D:\Trading_Algo\Desktop_Trading_Algo_root_legacy_20260530\sweph"),
    Path(r"D:\Trading_Algo\New folder\sweph"),
)

_CACHE: dict[tuple[str, str, str, str], pd.Series] = {}


def configure_ephemeris(path: Path | None = None) -> str:
    configure_swiss_ephemeris_sidereal(swe)
    candidates = (path,) if path else EPHEMERIS_PATH_CANDIDATES
    for candidate in candidates:
        if candidate is not None and candidate.exists():
            swe.set_ephe_path(str(candidate))
            return str(candidate)
    return "swisseph_builtin_or_moshier_fallback"


def _utc_timestamp(value: Any) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(IST)
    return timestamp.tz_convert(UTC)


def _jd_ut(value: Any) -> float:
    timestamp = _utc_timestamp(value)
    hour = (
        timestamp.hour
        + timestamp.minute / 60.0
        + timestamp.second / 3600.0
        + timestamp.microsecond / 3_600_000_000.0
    )
    return float(swe.julday(timestamp.year, timestamp.month, timestamp.day, hour))


def _index_digest(index: pd.DatetimeIndex) -> str:
    payload = index.asi8.tobytes() + str(index.tz).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _calc_longitude(body: str, value: Any, astrology_method: str, coordinate_system: str) -> float:
    normalized = str(body or "").strip().upper()
    if normalized == "KETU":
        return (_calc_longitude("RAHU", value, astrology_method, coordinate_system) + 180.0) % 360.0
    planet_id = BODY_IDS.get(normalized)
    if planet_id is None:
        raise ValueError(f"Unknown planet: {body}")
    if coordinate_system == "helio" and normalized in {"MOON", "RAHU"}:
        raise ValueError(f"{normalized} is unavailable in heliocentric mode")

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if str(astrology_method).lower() == "sidereal":
        flags |= swe.FLG_SIDEREAL
    if str(coordinate_system).lower() == "helio":
        flags |= swe.FLG_HELCTR
    jd_ut = _jd_ut(value)
    try:
        result, _ = swe.calc_ut(jd_ut, planet_id, flags)
    except Exception:
        fallback_flags = (flags & ~swe.FLG_SWIEPH) | swe.FLG_MOSEPH
        result, _ = swe.calc_ut(jd_ut, planet_id, fallback_flags)
    return float(result[0]) % 360.0


def fetch_planetary_longitude_single(
    planet_name: str,
    date: Any,
    astrology_method: str = "tropical",
    coordinate_system: str = "geo",
) -> float | None:
    try:
        configure_ephemeris()
        return _calc_longitude(planet_name, date, astrology_method, coordinate_system)
    except Exception:
        return None


def fetch_planetary_longitude(
    planet_name: str,
    dates: Any,
    astrology_method: str = "tropical",
    coordinate_system: str = "geo",
) -> pd.Series:
    index = pd.DatetimeIndex(dates)
    if index.tz is None:
        index = index.tz_localize(IST)
    cache_key = (
        str(planet_name or "").strip().upper(),
        str(astrology_method).lower(),
        str(coordinate_system).lower(),
        _index_digest(index),
    )
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return cached.copy()
    values = [
        _calc_longitude(planet_name, timestamp, astrology_method, coordinate_system)
        for timestamp in index
    ]
    result = pd.Series(np.asarray(values, dtype=float), index=index)
    _CACHE[cache_key] = result
    return result.copy()


def build_exact_longitude_map(
    planets: Any,
    full_timestamps: Any,
    fetch_fn: Any = fetch_planetary_longitude,
    astrology_method: str = "sidereal",
    coordinate_system: str = "geo",
) -> dict[str, pd.Series]:
    """Calculate every requested timestamp; no forward/back fill or future leakage."""

    index = pd.DatetimeIndex(full_timestamps)
    return {
        str(planet): fetch_fn(
            planet,
            index,
            astrology_method=astrology_method,
            coordinate_system=coordinate_system,
        ).reindex(index)
        for planet in planets
    }


def sidereal_house_cusps(
    value: Any,
    latitude: float,
    longitude: float,
    house_system: bytes = b"O",
) -> dict[int, float]:
    configure_ephemeris()
    houses, _ = swe.houses_ex(
        _jd_ut(value),
        float(latitude),
        float(longitude),
        house_system,
        swe.FLG_SIDEREAL,
    )
    return {index + 1: float(cusp) % 360.0 for index, cusp in enumerate(houses)}


def patch_legacy_jdml4_astronomy(module: Any) -> None:
    """Patch the recovery-only JDML4 runtime with the canonical single-sidereal path."""

    module.fetch_planetary_longitude = fetch_planetary_longitude
    module.fetch_planetary_longitude_single = fetch_planetary_longitude_single
    if hasattr(module, "PLANETARY_CACHE"):
        module.PLANETARY_CACHE = {}

    def compute_houses(reference: Any) -> None:
        if not reference.valid or not reference.planets_lon:
            return
        try:
            reference.houses = sidereal_house_cusps(
                reference.dt_ist,
                reference.lat,
                reference.lon,
                house_system=b"O",
            )
        except Exception:
            reference.houses = {}

    module.ReferenceChartEngine.compute_houses = compute_houses
