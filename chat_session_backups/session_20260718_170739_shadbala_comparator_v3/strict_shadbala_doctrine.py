from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta, timezone
from typing import Any

import numpy as np
import swisseph as swe

from drik_bala_engine import (
    DRIK_ENGINE_RULE_ID,
    DRIK_ENGINE_STATUS,
    DRIK_NATURE_RULE_ID,
    DRIK_NORMALIZATION_DIVISOR,
    DRIK_NORMALIZATION_RULE_ID,
    DRIK_SPECIAL_ASPECT_RULE_ID,
    base_aspect_strength_virupa,
    calculate_drik_bala,
    classify_planet_natures,
    special_aspect_bonus_virupa,
)
from shadbala_doctrine import (
    CLASSICAL_PLANETS,
    MOOLATRIKONA_SIGNS,
    NATURAL_RELATIONSHIPS,
    OWN_SIGNS,
    SIGN_LORDS,
    dignity_for_planet_in_sign,
    minimum_shadbala_total_virupa,
    normalize_body,
    normalize_sign,
)


STRICT_SHADBALA_RULE_ID = (
    "STRICT_SHADBALA_V7_NAMED_FORMULA_DIAGNOSTICS_PROVISIONAL"
)
STRICT_DRIK_RULE_ID = DRIK_ENGINE_RULE_ID
STRICT_SHADBALA_STATUS = (
    "provisional_bphs_source_profile_with_named_shared_input_diagnostics_pending_jhora_witness"
)
STRICT_DRIK_STATUS = DRIK_ENGINE_STATUS
SAPTAVARGAJA_RULE_ID = "BPHS_CH27_SAPTAVARGA_COMPOUND_RELATION_V2"
SAPTAVARGAJA_COMPARATOR_RULE_ID = "PYJHORA_4_8_7_SAPTAVARGA_COMPATIBILITY_PROFILE_V1"
OJAYUGMA_RULE_ID = "OJAYUGMA_ODD_EVEN_RASHI_NAVAMSA_V1"
KAALA_RULE_ID = "BPHS_CH27_KAALA_ASTRONOMICAL_SUNRISE_AHARGANA_V2"
CHESTA_RULE_ID = "BPHS_CH27_CHESTA_MEAN_TRUE_LONGITUDE_V3_PROVISIONAL"
CHESTA_MOTION_RULE_ID = "BPHS_CH27_EIGHT_MOTION_STATE_DIAGNOSTIC_V1"
CHESTA_PYJHORA_COMPARATOR_RULE_ID = (
    "PYJHORA_4_8_7_EPOCH_TABLE_LINEAR_CHESTA_COMPATIBILITY_V1"
)
YUDDHA_RULE_ID = "BPHS_CH27_YUDDHA_FAIL_CLOSED_V3"

SIGN_INDEX = {
    "ARIES": 0,
    "TAURUS": 1,
    "GEMINI": 2,
    "CANCER": 3,
    "LEO": 4,
    "VIRGO": 5,
    "LIBRA": 6,
    "SCORPIO": 7,
    "SAGITTARIUS": 8,
    "CAPRICORN": 9,
    "AQUARIUS": 10,
    "PISCES": 11,
}
SIGN_NAMES = tuple(SIGN_INDEX.keys())
EXALTATION_DEGREES = {
    "SUN": 10.0,
    "MOON": 33.0,
    "MARS": 298.0,
    "MERCURY": 165.0,
    "JUPITER": 95.0,
    "VENUS": 357.0,
    "SATURN": 200.0,
}
NAISARGIKA_VIRUPA = {
    "SUN": 60.0,
    "MOON": 51.43,
    "MARS": 17.14,
    "MERCURY": 25.71,
    "JUPITER": 34.29,
    "VENUS": 42.86,
    "SATURN": 8.57,
}
KENDRA_HOUSES = {1, 4, 7, 10}
PANAPARA_HOUSES = {2, 5, 8, 11}
APOKLIMA_HOUSES = {3, 6, 9, 12}
MALE_PLANETS = {"SUN", "MARS", "JUPITER"}
FEMALE_PLANETS = {"MOON", "VENUS"}
NEUTER_PLANETS = {"MERCURY", "SATURN"}
DIG_MAX_HOUSE = {
    "SUN": 10,
    "MARS": 10,
    "MOON": 4,
    "VENUS": 4,
    "JUPITER": 1,
    "MERCURY": 1,
    "SATURN": 7,
}
# Paksha Bala retains the source-aligned natural classification. Drik V2 uses
# its separate phase- and association-aware classification engine.
NATURAL_MALEFICS = {"SUN", "MARS", "SATURN"}
NATURAL_BENEFICS = {"JUPITER", "VENUS", "MERCURY"}
SAPTAVARGAJA_SOURCE_VIRUPA_BY_DIGNITY = {
    "moolatrikona": 45.0,
    "own": 30.0,
    "great_friend": 20.0,
    "friend": 15.0,
    "neutral": 10.0,
    "enemy": 4.0,
    "great_enemy": 2.0,
    "unknown": np.nan,
}
SAPTAVARGAJA_PYJHORA_VIRUPA_BY_DIGNITY = {
    "moolatrikona": 45.0,
    "own": 30.0,
    "great_friend": 22.5,
    "friend": 15.0,
    "neutral": 7.5,
    "enemy": 3.75,
    "great_enemy": 1.875,
    "unknown": np.nan,
}
SAPTAVARGAJA_SOURCE_PROFILE = "bphs_ch27_source"
SAPTAVARGAJA_PYJHORA_PROFILE = "pyjhora_4_8_7_compatibility"
MOOLATRIKONA_LONGITUDE_RANGES = {
    "SUN": (120.0, 140.0),
    "MOON": (33.0, 60.0),
    "MARS": (0.0, 12.0),
    "MERCURY": (166.0, 170.0),
    "JUPITER": (240.0, 250.0),
    "VENUS": (180.0, 195.0),
    "SATURN": (300.0, 320.0),
}
TEMPORARY_FRIEND_POSITIONS = {2, 3, 4, 10, 11, 12}
MOON_VENUS_OJAYUGMA_PLANETS = {"MOON", "VENUS"}
WEEKDAY_LORDS = ("MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "SUN")
CHALDEAN_HORA_ORDER = ("SATURN", "JUPITER", "MARS", "SUN", "VENUS", "MERCURY", "MOON")
TRIBHAGA_DAY_LORDS = ("MERCURY", "SUN", "SATURN")
TRIBHAGA_NIGHT_LORDS = ("MOON", "VENUS", "MARS")
AYANA_NORTH_STRONG = {"SUN", "MARS", "JUPITER", "VENUS"}
AYANA_SOUTH_STRONG = {"MOON", "SATURN"}
YUDDHA_PLANETS = {"MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"}
CHESTA_REFERENCE_SPEED = {
    "MARS": 0.524,
    "MERCURY": 1.6,
    "JUPITER": 0.083,
    "VENUS": 1.25,
    "SATURN": 0.033,
}
CHESTA_PLANET_IDS = {
    "MARS": swe.MARS,
    "MERCURY": swe.MERCURY,
    "JUPITER": swe.JUPITER,
    "VENUS": swe.VENUS,
    "SATURN": swe.SATURN,
}
AHARGANA_ANCHOR_DATE = date(1860, 1, 1)
AHARGANA_AT_ANCHOR = 714_404_108_573
AHARGANA_WEEKDAY_LORDS = {
    0: "SATURN",
    1: "SUN",
    2: "MOON",
    3: "MARS",
    4: "MERCURY",
    5: "JUPITER",
    6: "VENUS",
}
AYANA_OBLIQUITY_DEG = 23.0 + (27.0 / 60.0)


def normalize_longitude(value: Any) -> float | None:
    try:
        lon = float(value) % 360.0
    except (TypeError, ValueError):
        return None
    if not np.isfinite(lon):
        return None
    return lon


def circular_separation(a: Any, b: Any) -> float | None:
    left = normalize_longitude(a)
    right = normalize_longitude(b)
    if left is None or right is None:
        return None
    diff = abs((left - right) % 360.0)
    return min(diff, 360.0 - diff)


def forward_angle(from_lon: Any, to_lon: Any) -> float | None:
    left = normalize_longitude(from_lon)
    right = normalize_longitude(to_lon)
    if left is None or right is None:
        return None
    return (right - left) % 360.0


def circular_midpoint(a: Any, b: Any) -> float | None:
    left = normalize_longitude(a)
    right = normalize_longitude(b)
    if left is None or right is None:
        return None
    signed_delta = ((right - left + 180.0) % 360.0) - 180.0
    return (left + (signed_delta / 2.0)) % 360.0


def sign_from_lon(lon: Any) -> str:
    value = normalize_longitude(lon)
    if value is None:
        return ""
    return SIGN_NAMES[int(value // 30.0) % 12]


def sign_index_from_lon(lon: Any) -> int | None:
    value = normalize_longitude(lon)
    if value is None:
        return None
    return int(value // 30.0) % 12


def sign_name_from_index(index: int) -> str:
    return SIGN_NAMES[int(index) % 12]


def degree_in_sign(lon: Any) -> float | None:
    value = normalize_longitude(lon)
    if value is None:
        return None
    return value % 30.0


def exaltation_bala_virupa(planet: Any, lon: Any) -> float:
    body = normalize_body(planet)
    exalt_lon = EXALTATION_DEGREES.get(body)
    value = normalize_longitude(lon)
    if exalt_lon is None or value is None:
        return np.nan
    debil_lon = (float(exalt_lon) + 180.0) % 360.0
    sep = circular_separation(value, debil_lon)
    if sep is None:
        return np.nan
    return float(max(0.0, min(60.0, sep / 3.0)))


def whole_sign_house(lon: Any, asc_lon: Any) -> int | None:
    sign = normalize_longitude(lon)
    asc = normalize_longitude(asc_lon)
    if sign is None or asc is None:
        return None
    sign_idx = int(sign // 30.0)
    asc_idx = int(asc // 30.0)
    return ((sign_idx - asc_idx) % 12) + 1


def d1_rashi_sign(lon: Any) -> str:
    return sign_from_lon(lon)


def d2_hora_sign(lon: Any) -> str:
    sign_idx = sign_index_from_lon(lon)
    deg = degree_in_sign(lon)
    if sign_idx is None or deg is None:
        return ""
    odd = sign_idx % 2 == 0
    if odd:
        return "LEO" if deg < 15.0 else "CANCER"
    return "CANCER" if deg < 15.0 else "LEO"


def d3_drekkana_sign(lon: Any) -> str:
    sign_idx = sign_index_from_lon(lon)
    deg = degree_in_sign(lon)
    if sign_idx is None or deg is None:
        return ""
    part = int(deg // 10.0)
    return sign_name_from_index(sign_idx + (part * 4))


def d7_saptamsa_sign(lon: Any) -> str:
    sign_idx = sign_index_from_lon(lon)
    deg = degree_in_sign(lon)
    if sign_idx is None or deg is None:
        return ""
    part = min(6, int(deg / (30.0 / 7.0)))
    start = sign_idx if sign_idx % 2 == 0 else sign_idx + 6
    return sign_name_from_index(start + part)


def d9_navamsa_sign(lon: Any) -> str:
    sign_idx = sign_index_from_lon(lon)
    deg = degree_in_sign(lon)
    if sign_idx is None or deg is None:
        return ""
    part = min(8, int(deg / (30.0 / 9.0)))
    sign_mod = sign_idx % 3
    if sign_mod == 0:
        start = sign_idx
    elif sign_mod == 1:
        start = sign_idx + 8
    else:
        start = sign_idx + 4
    return sign_name_from_index(start + part)


def d12_dwadasamsa_sign(lon: Any) -> str:
    sign_idx = sign_index_from_lon(lon)
    deg = degree_in_sign(lon)
    if sign_idx is None or deg is None:
        return ""
    part = min(11, int(deg / 2.5))
    return sign_name_from_index(sign_idx + part)


def d30_trimsamsa_sign(lon: Any) -> str:
    sign_idx = sign_index_from_lon(lon)
    deg = degree_in_sign(lon)
    if sign_idx is None or deg is None:
        return ""
    odd = sign_idx % 2 == 0
    if odd:
        intervals = [
            (5.0, "ARIES"),
            (10.0, "AQUARIUS"),
            (18.0, "SAGITTARIUS"),
            (25.0, "GEMINI"),
            (30.0, "LIBRA"),
        ]
    else:
        intervals = [
            (5.0, "TAURUS"),
            (12.0, "VIRGO"),
            (20.0, "PISCES"),
            (25.0, "CAPRICORN"),
            (30.0, "SCORPIO"),
        ]
    for limit, sign in intervals:
        if deg < limit:
            return sign
    return intervals[-1][1]


def saptavarga_signs(lon: Any) -> dict[str, str]:
    return {
        "D1": d1_rashi_sign(lon),
        "D2": d2_hora_sign(lon),
        "D3": d3_drekkana_sign(lon),
        "D7": d7_saptamsa_sign(lon),
        "D9": d9_navamsa_sign(lon),
        "D12": d12_dwadasamsa_sign(lon),
        "D30": d30_trimsamsa_sign(lon),
    }


def temporary_relation(planet_sign: str, lord_sign: str) -> str:
    start = SIGN_INDEX.get(normalize_sign(planet_sign))
    end = SIGN_INDEX.get(normalize_sign(lord_sign))
    if start is None or end is None:
        return "unknown"
    position = ((end - start) % 12) + 1
    return "friend" if position in TEMPORARY_FRIEND_POSITIONS else "enemy"


def compound_relation(natural: str, temporary: str) -> str:
    if natural == "friend" and temporary == "friend":
        return "great_friend"
    if natural == "friend" and temporary == "enemy":
        return "neutral"
    if natural == "neutral" and temporary == "friend":
        return "friend"
    if natural == "neutral" and temporary == "enemy":
        return "enemy"
    if natural == "enemy" and temporary == "friend":
        return "neutral"
    if natural == "enemy" and temporary == "enemy":
        return "great_enemy"
    return "unknown"


def natural_relation_to_lord(planet: Any, lord: Any) -> str:
    body = normalize_body(planet)
    sign_lord = normalize_body(lord)
    if body == sign_lord:
        return "own"
    relationships = NATURAL_RELATIONSHIPS.get(body, {})
    if sign_lord in relationships.get("friend", set()):
        return "friend"
    if sign_lord in relationships.get("enemy", set()):
        return "enemy"
    if sign_lord in relationships.get("neutral", set()):
        return "neutral"
    return "unknown"


def in_moolatrikona_range(planet: Any, longitude: Any) -> bool:
    body = normalize_body(planet)
    value = normalize_longitude(longitude)
    limits = MOOLATRIKONA_LONGITUDE_RANGES.get(body)
    return bool(value is not None and limits is not None and limits[0] <= value < limits[1])


def saptavargaja_dignity(
    planet: Any,
    varga_sign: Any,
    d1_planet_sign: Any,
    longitudes: dict[str, float],
    *,
    varga: str,
    d1_longitude: Any,
    profile: str = SAPTAVARGAJA_SOURCE_PROFILE,
) -> dict[str, Any]:
    body = normalize_body(planet)
    sign = normalize_sign(varga_sign)
    if body not in CLASSICAL_PLANETS or sign not in SIGN_LORDS:
        return {"label": "unknown", "virupa": np.nan, "sign_lord": SIGN_LORDS.get(sign, ""), "relation": "unknown"}
    if profile == SAPTAVARGAJA_SOURCE_PROFILE:
        weights = SAPTAVARGAJA_SOURCE_VIRUPA_BY_DIGNITY
        is_moolatrikona = varga == "D1" and in_moolatrikona_range(body, d1_longitude)
    elif profile == SAPTAVARGAJA_PYJHORA_PROFILE:
        weights = SAPTAVARGAJA_PYJHORA_VIRUPA_BY_DIGNITY
        is_moolatrikona = varga == "D1" and sign == MOOLATRIKONA_SIGNS.get(body)
    else:
        raise ValueError(f"Unsupported Saptavargaja profile: {profile}")
    if is_moolatrikona:
        label = "moolatrikona"
        relation = "own"
    elif sign in OWN_SIGNS.get(body, set()):
        label = "own"
        relation = "own"
    else:
        lord = SIGN_LORDS.get(sign, "")
        natural = natural_relation_to_lord(body, lord)
        lord_sign = sign_from_lon(longitudes.get(lord))
        temp = temporary_relation(d1_planet_sign, lord_sign)
        label = compound_relation(natural, temp)
        relation = label
    return {
        "label": label,
        "virupa": float(weights.get(label, np.nan)),
        "sign_lord": SIGN_LORDS.get(sign, ""),
        "relation": relation,
        "profile": profile,
    }


def saptavargaja_bala(
    planet: Any,
    lon: Any,
    longitudes: dict[str, float],
    *,
    profile: str = SAPTAVARGAJA_SOURCE_PROFILE,
) -> dict[str, Any]:
    body = normalize_body(planet)
    value = normalize_longitude(lon)
    if body not in CLASSICAL_PLANETS or value is None:
        return {
            "saptavargaja_virupa": np.nan,
            "saptavarga_details": [],
            "profile": profile,
        }
    d1_sign = sign_from_lon(value)
    details: list[dict[str, Any]] = []
    total = 0.0
    for varga, sign in saptavarga_signs(value).items():
        dignity = saptavargaja_dignity(
            body,
            sign,
            d1_sign,
            longitudes,
            varga=varga,
            d1_longitude=value,
            profile=profile,
        )
        virupa = dignity.get("virupa", np.nan)
        if np.isfinite(float(virupa)):
            total += float(virupa)
        details.append(
            {
                "varga": varga,
                "sign": sign,
                "label": dignity.get("label", "unknown"),
                "virupa": round(float(virupa), 6) if np.isfinite(float(virupa)) else None,
                "profile": profile,
            }
        )
    return {
        "saptavargaja_virupa": float(total),
        "saptavarga_details": details,
        "profile": profile,
    }


def ojayugma_bala_virupa(planet: Any, lon: Any) -> float:
    body = normalize_body(planet)
    rashi_idx = sign_index_from_lon(lon)
    navamsa = d9_navamsa_sign(lon)
    navamsa_idx = SIGN_INDEX.get(navamsa)
    if body not in CLASSICAL_PLANETS or rashi_idx is None or navamsa_idx is None:
        return np.nan
    wants_even = body in MOON_VENUS_OJAYUGMA_PLANETS
    rashi_even = rashi_idx % 2 == 1
    navamsa_even = navamsa_idx % 2 == 1
    return float((15.0 if rashi_even == wants_even else 0.0) + (15.0 if navamsa_even == wants_even else 0.0))


def kendradi_bala_virupa(house: int | None) -> float:
    if house in KENDRA_HOUSES:
        return 60.0
    if house in PANAPARA_HOUSES:
        return 30.0
    if house in APOKLIMA_HOUSES:
        return 15.0
    return np.nan


def drekkana_bala_virupa(planet: Any, lon: Any) -> float:
    body = normalize_body(planet)
    value = normalize_longitude(lon)
    if value is None:
        return np.nan
    degree_in_sign = value % 30.0
    drekkana = int(degree_in_sign // 10.0) + 1
    if body in MALE_PLANETS and drekkana == 1:
        return 15.0
    if body in NEUTER_PLANETS and drekkana == 2:
        return 15.0
    if body in FEMALE_PLANETS and drekkana == 3:
        return 15.0
    return 0.0


def sthana_bala_from_longitudes(
    planet: Any,
    lon: Any,
    longitudes: dict[str, float],
    asc_lon: Any,
    *,
    profile: str = SAPTAVARGAJA_SOURCE_PROFILE,
) -> dict[str, Any]:
    body = normalize_body(planet)
    value = normalize_longitude(lon)
    if body not in CLASSICAL_PLANETS or value is None:
        return {"total_virupa": np.nan, "profile": profile}
    house = whole_sign_house(value, asc_lon)
    saptavargaja = saptavargaja_bala(
        body,
        value,
        longitudes,
        profile=profile,
    )
    parts = {
        "uchcha_virupa": exaltation_bala_virupa(body, value),
        "saptavargaja_virupa": saptavargaja.get(
            "saptavargaja_virupa",
            np.nan,
        ),
        "ojayugma_virupa": ojayugma_bala_virupa(body, value),
        "kendradi_virupa": kendradi_bala_virupa(house),
        "drekkana_virupa": drekkana_bala_virupa(body, value),
    }
    complete = all(np.isfinite(float(item)) for item in parts.values())
    return {
        **parts,
        "total_virupa": (
            float(sum(float(item) for item in parts.values()))
            if complete
            else np.nan
        ),
        "house": house,
        "profile": profile,
        "complete": complete,
        "saptavarga_details": saptavargaja.get("saptavarga_details", []),
    }


def _timestamp_to_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        if hasattr(value, "to_pydatetime"):
            dt = value.to_pydatetime()
        elif isinstance(value, datetime):
            dt = value
        else:
            text = str(value).strip()
            if not text:
                return None
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def local_mean_datetime(timestamp: Any, geo_lon: Any = None) -> datetime | None:
    dt = _timestamp_to_datetime(timestamp)
    if dt is None:
        return None
    try:
        lon = float(geo_lon)
    except (TypeError, ValueError):
        lon = 0.0
    return dt + timedelta(hours=lon / 15.0)


def decimal_hour(value: datetime) -> float:
    return (
        value.hour
        + (value.minute / 60.0)
        + (value.second / 3600.0)
        + (value.microsecond / 3_600_000_000.0)
    )


def julian_day_ut(value: datetime) -> float:
    utc = value.astimezone(timezone.utc)
    return float(
        swe.julday(
            utc.year,
            utc.month,
            utc.day,
            decimal_hour(utc),
            swe.GREG_CAL,
        )
    )


def datetime_from_julian_day_ut(jd_ut: float) -> datetime:
    year, month, day, hour = swe.revjul(float(jd_ut), swe.GREG_CAL)
    midnight = datetime(
        int(year),
        int(month),
        int(day),
        tzinfo=timezone.utc,
    )
    return midnight + timedelta(hours=float(hour))


def sunrise_sunset_lmt_for_date(
    local_date: date,
    geo_lon: Any,
    geo_lat: Any,
) -> tuple[float, float, str]:
    try:
        lon = float(geo_lon)
        lat = float(geo_lat)
    except (TypeError, ValueError):
        return 6.0, 18.0, "fallback_0600_1800_missing_coordinates"
    if not np.isfinite(lon) or not np.isfinite(lat) or not -90.0 <= lat <= 90.0:
        return 6.0, 18.0, "fallback_0600_1800_invalid_coordinates"
    local_midnight = datetime(
        local_date.year,
        local_date.month,
        local_date.day,
        tzinfo=timezone.utc,
    )
    search_start_utc = local_midnight - timedelta(hours=lon / 15.0)
    try:
        rise_result, rise_times = swe.rise_trans(
            julian_day_ut(search_start_utc),
            swe.SUN,
            swe.CALC_RISE,
            (lon, lat, 0.0),
            0.0,
            0.0,
            swe.FLG_SWIEPH,
        )
        set_result, set_times = swe.rise_trans(
            julian_day_ut(search_start_utc),
            swe.SUN,
            swe.CALC_SET,
            (lon, lat, 0.0),
            0.0,
            0.0,
            swe.FLG_SWIEPH,
        )
    except (swe.Error, ValueError):
        return 6.0, 18.0, "fallback_0600_1800_swiss_ephemeris_error"
    if int(rise_result) != 0 or int(set_result) != 0:
        return 6.0, 18.0, "fallback_0600_1800_polar_or_unavailable"
    rise_lmt = datetime_from_julian_day_ut(float(rise_times[0])) + timedelta(hours=lon / 15.0)
    set_lmt = datetime_from_julian_day_ut(float(set_times[0])) + timedelta(hours=lon / 15.0)
    sunrise = (rise_lmt - local_midnight).total_seconds() / 3600.0
    sunset = (set_lmt - local_midnight).total_seconds() / 3600.0
    if not 0.0 <= sunrise < 24.0 or not 0.0 <= sunset < 24.0:
        return 6.0, 18.0, "fallback_0600_1800_out_of_range"
    return float(sunrise), float(sunset), "swiss_ephemeris_apparent_solar_rise_set_lmt"


def astronomical_sunrise_sunset_lmt(
    timestamp: Any,
    geo_lon: Any,
    geo_lat: Any,
) -> tuple[float, float, str]:
    lmt = local_mean_datetime(timestamp, geo_lon)
    if lmt is None:
        return 6.0, 18.0, "fallback_0600_1800_missing_timestamp"
    return sunrise_sunset_lmt_for_date(lmt.date(), geo_lon, geo_lat)


def nathonnatha_bala_virupa(planet: Any, timestamp: Any, geo_lon: Any = None) -> float:
    body = normalize_body(planet)
    lmt = local_mean_datetime(timestamp, geo_lon)
    if body not in CLASSICAL_PLANETS or lmt is None:
        return np.nan
    ghatis = (lmt.hour + (lmt.minute / 60.0) + (lmt.second / 3600.0) + (lmt.microsecond / 3_600_000_000.0)) * 2.5
    nata = abs(30.0 - ghatis)
    if body in {"MOON", "MARS", "SATURN"}:
        return float(max(0.0, min(60.0, 2.0 * nata)))
    if body in {"SUN", "JUPITER", "VENUS"}:
        return float(max(0.0, min(60.0, 60.0 - (2.0 * nata))))
    if body == "MERCURY":
        return 60.0
    return np.nan


def paksha_bala_virupa(planet: Any, sun_lon: Any, moon_lon: Any) -> float:
    body = normalize_body(planet)
    sun = normalize_longitude(sun_lon)
    moon = normalize_longitude(moon_lon)
    if body not in CLASSICAL_PLANETS or sun is None or moon is None:
        return np.nan
    phase = (moon - sun) % 360.0
    bright_strength = (phase / 3.0) if phase <= 180.0 else ((360.0 - phase) / 3.0)
    bright_strength = max(0.0, min(60.0, bright_strength))
    if body == "MOON":
        return float(2.0 * bright_strength)
    if body in NATURAL_BENEFICS:
        return float(bright_strength)
    return float(60.0 - bright_strength)


def tribhaga_bala_virupa(
    planet: Any,
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
    sunset_hour: float = 18.0,
) -> float:
    body = normalize_body(planet)
    lmt = local_mean_datetime(timestamp, geo_lon)
    if body not in CLASSICAL_PLANETS or lmt is None:
        return np.nan
    if body == "JUPITER":
        return 60.0
    hour = lmt.hour + (lmt.minute / 60.0) + (lmt.second / 3600.0)
    sunrise = float(sunrise_hour)
    sunset = float(sunset_hour)
    is_day = sunrise <= hour < sunset
    if is_day:
        span = max(0.1, sunset - sunrise)
        part = min(2, int((hour - sunrise) / (span / 3.0)))
        lord = TRIBHAGA_DAY_LORDS[part]
    else:
        night_span = max(0.1, 24.0 - sunset + sunrise)
        elapsed = (hour - sunset) if hour >= sunset else (hour + 24.0 - sunset)
        part = min(2, int(elapsed / (night_span / 3.0)))
        lord = TRIBHAGA_NIGHT_LORDS[part]
    return 60.0 if body == lord else 0.0


def weekday_lord_for_lmt(timestamp: Any, geo_lon: Any = None) -> str:
    lmt = local_mean_datetime(timestamp, geo_lon)
    if lmt is None:
        return ""
    return WEEKDAY_LORDS[lmt.weekday()]


def ahargana_day_date(
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
) -> date | None:
    lmt = local_mean_datetime(timestamp, geo_lon)
    if lmt is None:
        return None
    day_date = lmt.date()
    if decimal_hour(lmt) < float(sunrise_hour):
        day_date -= timedelta(days=1)
    return day_date


def ahargana_index(
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
) -> int | None:
    day_date = ahargana_day_date(timestamp, geo_lon, sunrise_hour)
    if day_date is None:
        return None
    return int(AHARGANA_AT_ANCHOR + (day_date - AHARGANA_ANCHOR_DATE).days)


def ahargana_lords(
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
) -> dict[str, Any]:
    value = ahargana_index(timestamp, geo_lon, sunrise_hour)
    if value is None:
        return {"ahargana": None, "abda": "", "masa": "", "dina": ""}
    abda_remainder = (((value // 360) * 3) + 1) % 7
    masa_remainder = (((value // 30) * 2) + 1) % 7
    dina_remainder = value % 7
    return {
        "ahargana": value,
        "abda": AHARGANA_WEEKDAY_LORDS[abda_remainder],
        "masa": AHARGANA_WEEKDAY_LORDS[masa_remainder],
        "dina": AHARGANA_WEEKDAY_LORDS[dina_remainder],
    }


def vara_bala_virupa(
    planet: Any,
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
) -> float:
    lord = ahargana_lords(timestamp, geo_lon, sunrise_hour)["dina"]
    return 45.0 if normalize_body(planet) == lord else 0.0


def hora_lord_for_lmt(
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
    geo_lat: Any = None,
) -> str:
    lmt = local_mean_datetime(timestamp, geo_lon)
    if lmt is None:
        return ""
    current_hour = decimal_hour(lmt)
    start_hour = float(sunrise_hour)
    if current_hour < start_hour:
        previous_sunrise, _previous_sunset, status = sunrise_sunset_lmt_for_date(
            lmt.date() - timedelta(days=1),
            geo_lon,
            geo_lat,
        )
        if status.startswith("swiss_ephemeris"):
            start_hour = previous_sunrise
        elapsed = current_hour + 24.0 - start_hour
    else:
        elapsed = current_hour - start_hour
    day_lord = ahargana_lords(timestamp, geo_lon, sunrise_hour)["dina"]
    if day_lord not in CHALDEAN_HORA_ORDER:
        return ""
    start_idx = CHALDEAN_HORA_ORDER.index(day_lord)
    elapsed_hours = int(math.floor(elapsed))
    return CHALDEAN_HORA_ORDER[(start_idx + elapsed_hours) % 7]


def hora_bala_virupa(
    planet: Any,
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
    geo_lat: Any = None,
) -> float:
    lord = hora_lord_for_lmt(timestamp, geo_lon, sunrise_hour, geo_lat)
    return 60.0 if normalize_body(planet) == lord else 0.0


def abda_masa_lords(
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
) -> tuple[str, str]:
    lords = ahargana_lords(timestamp, geo_lon, sunrise_hour)
    return str(lords["abda"]), str(lords["masa"])


def abda_bala_virupa(
    planet: Any,
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
) -> float:
    abda, _ = abda_masa_lords(timestamp, geo_lon, sunrise_hour)
    return 15.0 if normalize_body(planet) == abda else 0.0


def masa_bala_virupa(
    planet: Any,
    timestamp: Any,
    geo_lon: Any = None,
    sunrise_hour: float = 6.0,
) -> float:
    _, masa = abda_masa_lords(timestamp, geo_lon, sunrise_hour)
    return 30.0 if normalize_body(planet) == masa else 0.0


def ayana_bala_virupa(planet: Any, declination_deg: Any) -> float:
    body = normalize_body(planet)
    try:
        dec = float(declination_deg)
    except (TypeError, ValueError):
        return np.nan
    if body not in CLASSICAL_PLANETS or not np.isfinite(dec):
        return np.nan
    if body in AYANA_NORTH_STRONG:
        value = max(
            0.0,
            (AYANA_OBLIQUITY_DEG + dec) * 60.0 / (2.0 * AYANA_OBLIQUITY_DEG),
        )
        return 2.0 * value if body == "SUN" else value
    if body in AYANA_SOUTH_STRONG:
        return float(
            max(
                0.0,
                (AYANA_OBLIQUITY_DEG - dec) * 60.0 / (2.0 * AYANA_OBLIQUITY_DEG),
            )
        )
    if body == "MERCURY":
        return float(
            max(
                0.0,
                (AYANA_OBLIQUITY_DEG + abs(dec))
                * 60.0
                / (2.0 * AYANA_OBLIQUITY_DEG),
            )
        )
    return np.nan


def yuddha_bala_virupa(planet: Any, longitudes: dict[str, float], latitudes: dict[str, float] | None = None) -> tuple[float, str]:
    body = normalize_body(planet)
    if body not in YUDDHA_PLANETS:
        return 0.0, "not_applicable_luminary_or_node"
    value = normalize_longitude(longitudes.get(body))
    if value is None:
        return np.nan, "missing_longitude"
    latitudes = latitudes or {}
    for other in YUDDHA_PLANETS:
        if other == body:
            continue
        other_lon = normalize_longitude(longitudes.get(other))
        if other_lon is None:
            continue
        sep = circular_separation(value, other_lon)
        if sep is None or sep > 1.0:
            continue
        return np.nan, f"yuddha_candidate_vs_{other.lower()}_uncertified_fail_closed"
    return 0.0, "no_graha_yuddha_candidate_within_1deg"


def kaala_bala_components(
    planet: Any,
    timestamp: Any,
    geo_lon: Any,
    geo_lat: Any,
    sun_lon: Any,
    moon_lon: Any,
    declination_deg: Any,
    longitudes: dict[str, float],
    latitudes: dict[str, float] | None = None,
    sunrise_hour: float | None = None,
    sunset_hour: float | None = None,
) -> dict[str, Any]:
    body = normalize_body(planet)
    if body not in CLASSICAL_PLANETS:
        return {}
    if sunrise_hour is None or sunset_hour is None:
        calculated_sunrise, calculated_sunset, solar_time_status = (
            astronomical_sunrise_sunset_lmt(timestamp, geo_lon, geo_lat)
        )
        resolved_sunrise = calculated_sunrise if sunrise_hour is None else float(sunrise_hour)
        resolved_sunset = calculated_sunset if sunset_hour is None else float(sunset_hour)
    else:
        resolved_sunrise = float(sunrise_hour)
        resolved_sunset = float(sunset_hour)
        solar_time_status = "caller_supplied_sunrise_sunset_lmt"
    lords = ahargana_lords(timestamp, geo_lon, resolved_sunrise)
    yuddha, yuddha_status = yuddha_bala_virupa(body, longitudes, latitudes)
    parts = {
        "nathonnatha_virupa": nathonnatha_bala_virupa(body, timestamp, geo_lon),
        "paksha_virupa": paksha_bala_virupa(body, sun_lon, moon_lon),
        "tribhaga_virupa": tribhaga_bala_virupa(
            body,
            timestamp,
            geo_lon,
            resolved_sunrise,
            resolved_sunset,
        ),
        "abda_virupa": abda_bala_virupa(
            body,
            timestamp,
            geo_lon,
            resolved_sunrise,
        ),
        "masa_virupa": masa_bala_virupa(
            body,
            timestamp,
            geo_lon,
            resolved_sunrise,
        ),
        "vara_virupa": vara_bala_virupa(
            body,
            timestamp,
            geo_lon,
            resolved_sunrise,
        ),
        "hora_virupa": hora_bala_virupa(
            body,
            timestamp,
            geo_lon,
            resolved_sunrise,
            geo_lat,
        ),
        "ayana_virupa": ayana_bala_virupa(body, declination_deg),
        "yuddha_virupa": yuddha,
        "yuddha_status": yuddha_status,
        "sunrise_lmt_hour": resolved_sunrise,
        "sunset_lmt_hour": resolved_sunset,
        "solar_time_status": solar_time_status,
        "ahargana": lords["ahargana"],
        "abda_lord": lords["abda"],
        "masa_lord": lords["masa"],
        "dina_lord": lords["dina"],
        "hora_lord": hora_lord_for_lmt(
            timestamp,
            geo_lon,
            resolved_sunrise,
            geo_lat,
        ),
    }
    seven_keys = [
        "nathonnatha_virupa",
        "paksha_virupa",
        "tribhaga_virupa",
        "abda_virupa",
        "masa_virupa",
        "vara_virupa",
        "hora_virupa",
    ]
    nine_keys = seven_keys + ["ayana_virupa", "yuddha_virupa"]
    seven_complete = all(np.isfinite(float(parts[key])) for key in seven_keys)
    nine_complete = all(np.isfinite(float(parts[key])) for key in nine_keys)
    parts["kaala_7_virupa"] = (
        float(sum(float(parts[key]) for key in seven_keys))
        if seven_complete
        else np.nan
    )
    parts["kaala_9_virupa"] = (
        float(sum(float(parts[key]) for key in nine_keys))
        if nine_complete
        else np.nan
    )
    parts["kaala_7_profile"] = "jaya_seven_factor_interpretation"
    parts["kaala_9_profile"] = "bphs_ch27_nine_factor_conventional"
    parts["kaala_complete"] = bool(nine_complete)
    return parts


def chesta_motion_state_bala_virupa(
    planet: Any,
    speed_deg_day: Any,
) -> tuple[float, str]:
    body = normalize_body(planet)
    if body not in CHESTA_REFERENCE_SPEED:
        return np.nan, "unsupported_planet"
    try:
        speed = float(speed_deg_day)
    except (TypeError, ValueError):
        return np.nan, "missing_speed"
    if not np.isfinite(speed):
        return np.nan, "missing_speed"
    ref = CHESTA_REFERENCE_SPEED[body]
    if speed < 0:
        return 60.0, "vakra_retrograde_speed_diagnostic"
    ratio = abs(speed) / ref if ref else np.nan
    if not np.isfinite(ratio):
        return np.nan, "bad_speed_reference"
    if ratio < 0.15:
        return 15.0, "vikala_near_station_speed_diagnostic"
    if ratio < 0.50:
        return 30.0, "mandatara_very_slow_direct_speed_diagnostic"
    if ratio < 0.90:
        return 15.0, "manda_slow_direct_speed_diagnostic"
    if ratio <= 1.25:
        return 7.5, "sama_normal_direct_speed_diagnostic"
    if ratio <= 1.75:
        return 45.0, "chara_fast_direct_speed_diagnostic"
    return 30.0, "atichara_very_fast_direct_speed_diagnostic"


def chesta_mean_true_context(
    planet: Any,
    timestamp: Any,
    true_longitude: Any,
    sun_longitude: Any,
) -> dict[str, Any]:
    body = normalize_body(planet)
    true_lon = normalize_longitude(true_longitude)
    sun_sidereal = normalize_longitude(sun_longitude)
    dt = _timestamp_to_datetime(timestamp)
    if body not in CHESTA_PLANET_IDS:
        return {"virupa": np.nan, "status": "unsupported_planet"}
    if dt is None or true_lon is None or sun_sidereal is None:
        return {"virupa": np.nan, "status": "missing_timestamp_or_longitude"}
    jd_ut = julian_day_ut(dt)
    jd_et = jd_ut + float(swe.deltat(jd_ut))
    try:
        tropical_sun = float(
            swe.calc_ut(
                jd_ut,
                swe.SUN,
                swe.FLG_SWIEPH | swe.FLG_SPEED,
            )[0][0]
        )
        ayanamsa = (tropical_sun - sun_sidereal) % 360.0
        earth_mean_tropical = float(
            swe.get_orbital_elements(
                jd_et,
                swe.EARTH,
                swe.FLG_SWIEPH,
            )[9]
        )
        planet_mean_tropical = float(
            swe.get_orbital_elements(
                jd_et,
                CHESTA_PLANET_IDS[body],
                swe.FLG_SWIEPH,
            )[9]
        )
    except (swe.Error, ValueError, IndexError):
        return {"virupa": np.nan, "status": "swiss_ephemeris_mean_longitude_unavailable"}
    mean_sun = (earth_mean_tropical + 180.0 - ayanamsa) % 360.0
    mean_planet = (planet_mean_tropical - ayanamsa) % 360.0
    mean_true_midpoint = circular_midpoint(mean_planet, true_lon)
    if mean_true_midpoint is None:
        return {"virupa": np.nan, "status": "mean_true_midpoint_unavailable"}
    seegrocha = mean_planet if body in {"MERCURY", "VENUS"} else mean_sun
    separation = circular_separation(seegrocha, mean_true_midpoint)
    if separation is None:
        return {"virupa": np.nan, "status": "seegrocha_separation_unavailable"}
    return {
        "virupa": float(separation / 3.0),
        "status": "bphs_mean_true_seegrocha_swiss_osculating_model_provisional",
        "model": "SWISSEPH_OSCULATING_MEAN_LONGITUDE_V1",
        "ayanamsa_inferred_deg": float(ayanamsa),
        "mean_sun_sidereal_deg": float(mean_sun),
        "mean_planet_sidereal_deg": float(mean_planet),
        "mean_true_midpoint_sidereal_deg": float(mean_true_midpoint),
        "seegrocha_sidereal_deg": float(seegrocha),
        "separation_deg": float(separation),
    }


def chesta_pyjhora_epoch_compatibility_from_inputs(
    planet: Any,
    true_longitude: Any,
    mean_sun_longitude: Any,
    mean_planet_longitude: Any,
) -> dict[str, Any]:
    body = normalize_body(planet)
    true_lon = normalize_longitude(true_longitude)
    mean_sun = normalize_longitude(mean_sun_longitude)
    mean_planet = normalize_longitude(mean_planet_longitude)
    if body not in CHESTA_PLANET_IDS:
        return {
            "virupa": np.nan,
            "status": "structural_not_applicable_luminary_or_node",
            "profile": CHESTA_PYJHORA_COMPARATOR_RULE_ID,
        }
    if true_lon is None or mean_sun is None or mean_planet is None:
        return {
            "virupa": np.nan,
            "status": "missing_shared_formula_input",
            "profile": CHESTA_PYJHORA_COMPARATOR_RULE_ID,
        }
    if body in {"MERCURY", "VENUS"}:
        seegrocha = mean_planet
        midpoint_mean = mean_sun
    else:
        seegrocha = mean_sun
        midpoint_mean = mean_planet
    # PyJHora 4.8.7 intentionally uses this linear midpoint and absolute
    # difference. It is retained only as a named compatibility diagnostic.
    mean_true_midpoint = 0.5 * (true_lon + midpoint_mean)
    reduced_chesta_kendra = abs(seegrocha - mean_true_midpoint)
    return {
        "virupa": float(reduced_chesta_kendra / 3.0),
        "status": "pyjhora_epoch_table_linear_formula_compatibility",
        "profile": CHESTA_PYJHORA_COMPARATOR_RULE_ID,
        "true_longitude_deg": true_lon,
        "mean_sun_longitude_deg": mean_sun,
        "mean_planet_longitude_deg": mean_planet,
        "midpoint_mean_longitude_deg": midpoint_mean,
        "mean_true_midpoint_linear_deg": mean_true_midpoint,
        "seegrocha_longitude_deg": seegrocha,
        "reduced_chesta_kendra_deg": reduced_chesta_kendra,
    }


def chesta_bala_virupa(
    planet: Any,
    speed_deg_day: Any,
    ayana_virupa: Any = None,
    paksha_virupa: Any = None,
    *,
    timestamp: Any = None,
    true_longitude: Any = None,
    sun_longitude: Any = None,
) -> tuple[float, str]:
    body = normalize_body(planet)
    if body == "SUN":
        try:
            value = float(ayana_virupa)
        except (TypeError, ValueError):
            value = np.nan
        return (value, "sun_chesta_equals_ayana") if np.isfinite(value) else (np.nan, "sun_missing_ayana")
    if body == "MOON":
        try:
            value = float(paksha_virupa)
        except (TypeError, ValueError):
            value = np.nan
        return (value, "moon_chesta_equals_paksha") if np.isfinite(value) else (np.nan, "moon_missing_paksha")
    context = chesta_mean_true_context(
        body,
        timestamp,
        true_longitude,
        sun_longitude,
    )
    return float(context["virupa"]), str(context["status"])


def dig_bala_virupa(planet: Any, lon: Any, house_cusps: dict[int, float] | None, asc_lon: Any) -> float:
    body = normalize_body(planet)
    max_house = DIG_MAX_HOUSE.get(body)
    value = normalize_longitude(lon)
    if max_house is None or value is None:
        return np.nan
    if house_cusps and max_house in house_cusps:
        max_point = normalize_longitude(house_cusps.get(max_house))
    else:
        asc = normalize_longitude(asc_lon)
        if asc is None:
            return np.nan
        max_point = (asc + ((max_house - 1) * 30.0)) % 360.0
    weak_point = (float(max_point) + 180.0) % 360.0
    sep = circular_separation(value, weak_point)
    if sep is None:
        return np.nan
    return float(max(0.0, min(60.0, sep / 3.0)))


def drik_base_strength_virupa(angle: Any) -> float:
    return base_aspect_strength_virupa(angle)


def drik_special_bonus_virupa(planet: Any, angle: Any) -> float:
    return special_aspect_bonus_virupa(planet, angle)


def drik_aspector_sign(
    planet: Any,
    sun_lon: Any,
    moon_lon: Any,
    longitudes: dict[str, float] | None = None,
) -> int:
    body = normalize_body(planet)
    values = dict(longitudes or {})
    if normalize_longitude(sun_lon) is not None:
        values["SUN"] = float(sun_lon)
    if normalize_longitude(moon_lon) is not None:
        values["MOON"] = float(moon_lon)
    nature = classify_planet_natures(values, sun_lon=sun_lon, moon_lon=moon_lon).get(body)
    if nature is not None:
        return 1 if nature.nature == "benefic" else -1
    return 0


def strict_drik_bala_for_planet(
    target: Any,
    longitudes: dict[str, float],
    sun_lon: Any,
    moon_lon: Any,
) -> dict[str, Any]:
    result = calculate_drik_bala(
        target,
        longitudes,
        sun_lon=sun_lon,
        moon_lon=moon_lon,
    ).to_dict()
    if not result["available"]:
        return {
            "drik_bala_virupa": np.nan,
            "normalized_net_unrounded_virupa": np.nan,
            "benefic_virupa": np.nan,
            "malefic_virupa": np.nan,
            "raw_net_virupa": np.nan,
            "benefic_raw_virupa": np.nan,
            "malefic_raw_virupa": np.nan,
            "normalization_divisor": DRIK_NORMALIZATION_DIVISOR,
            "aspector_natures": result["aspector_natures"],
            "aspects": result["contributions"],
        }
    return {
        "drik_bala_virupa": result["drik_bala_virupa"],
        "normalized_net_unrounded_virupa": result["normalized_net_unrounded_virupa"],
        "benefic_virupa": result["benefic_virupa"],
        "malefic_virupa": result["malefic_virupa"],
        "raw_net_virupa": result["raw_net_virupa"],
        "benefic_raw_virupa": result["benefic_raw_virupa"],
        "malefic_raw_virupa": result["malefic_raw_virupa"],
        "normalization_divisor": result["normalization_divisor"],
        "aspector_natures": result["aspector_natures"],
        "aspects": result["contributions"],
    }


def shadbala_components_for_planet(
    planet: Any,
    lon: Any,
    longitudes: dict[str, float],
    asc_lon: Any,
    house_cusps: dict[int, float] | None,
    sun_lon: Any,
    moon_lon: Any,
    timestamp: Any = None,
    geo_lon: Any = None,
    speeds: dict[str, float] | None = None,
    latitudes: dict[str, float] | None = None,
    declinations: dict[str, float] | None = None,
    geo_lat: Any = None,
) -> dict[str, Any]:
    body = normalize_body(planet)
    value = normalize_longitude(lon)
    if body not in CLASSICAL_PLANETS or value is None:
        return {}
    sign = sign_from_lon(value)
    dignity = dignity_for_planet_in_sign(body, sign)
    house = whole_sign_house(value, asc_lon)
    drik = strict_drik_bala_for_planet(body, longitudes, sun_lon, moon_lon)
    sthana_source = sthana_bala_from_longitudes(
        body,
        value,
        longitudes,
        asc_lon,
        profile=SAPTAVARGAJA_SOURCE_PROFILE,
    )
    sthana_comparator_context = sthana_bala_from_longitudes(
        body,
        value,
        longitudes,
        asc_lon,
        profile=SAPTAVARGAJA_PYJHORA_PROFILE,
    )
    uchcha = float(sthana_source["uchcha_virupa"])
    saptavargaja = {
        "saptavargaja_virupa": sthana_source["saptavargaja_virupa"],
        "saptavarga_details": sthana_source["saptavarga_details"],
        "profile": sthana_source["profile"],
    }
    saptavargaja_comparator = {
        "saptavargaja_virupa": sthana_comparator_context[
            "saptavargaja_virupa"
        ],
        "profile": sthana_comparator_context["profile"],
    }
    ojayugma = float(sthana_source["ojayugma_virupa"])
    kendradi = float(sthana_source["kendradi_virupa"])
    drekkana = float(sthana_source["drekkana_virupa"])
    dig = dig_bala_virupa(body, value, house_cusps, asc_lon)
    kaala = kaala_bala_components(
        body,
        timestamp,
        geo_lon,
        geo_lat,
        sun_lon,
        moon_lon,
        (declinations or {}).get(body, np.nan),
        longitudes,
        latitudes,
    )
    chesta, chesta_status = chesta_bala_virupa(
        body,
        (speeds or {}).get(body, np.nan),
        ayana_virupa=kaala.get("ayana_virupa", np.nan),
        paksha_virupa=kaala.get("paksha_virupa", np.nan),
        timestamp=timestamp,
        true_longitude=value,
        sun_longitude=sun_lon,
    )
    chesta_motion, chesta_motion_status = chesta_motion_state_bala_virupa(
        body,
        (speeds or {}).get(body, np.nan),
    )
    sthana_partial = float(sthana_source["total_virupa"])
    sthana_comparator = float(sthana_comparator_context["total_virupa"])
    implemented_values = [
        NAISARGIKA_VIRUPA.get(body, np.nan),
        uchcha,
        saptavargaja.get("saptavargaja_virupa", np.nan),
        ojayugma,
        kendradi,
        drekkana,
        dig,
        drik.get("drik_bala_virupa", np.nan),
        kaala.get("kaala_9_virupa", np.nan),
        chesta,
    ]
    implemented_complete = all(
        value is not None and np.isfinite(float(value))
        for value in implemented_values
    )
    implemented_total = (
        float(sum(float(value) for value in implemented_values))
        if implemented_complete
        else np.nan
    )
    minimum = minimum_shadbala_total_virupa(body)
    ratio = (
        implemented_total / float(minimum)
        if minimum and np.isfinite(implemented_total)
        else np.nan
    )
    return {
        "body": body,
        "sign": sign,
        "house": house if house is not None else "",
        "naisargika_virupa": NAISARGIKA_VIRUPA.get(body, np.nan),
        "uchcha_virupa": uchcha,
        "saptavargaja_virupa": saptavargaja.get("saptavargaja_virupa", np.nan),
        "saptavarga_details": saptavargaja.get("saptavarga_details", []),
        "saptavargaja_profile": saptavargaja.get("profile", ""),
        "saptavargaja_comparator_virupa": saptavargaja_comparator.get(
            "saptavargaja_virupa",
            np.nan,
        ),
        "saptavargaja_comparator_profile": saptavargaja_comparator.get(
            "profile",
            "",
        ),
        "ojayugma_virupa": ojayugma,
        "kendradi_virupa": kendradi,
        "drekkana_virupa": drekkana,
        "sthana_partial_virupa": sthana_partial,
        "sthana_comparator_virupa": sthana_comparator,
        "dig_virupa": dig,
        "drik_virupa": drik.get("drik_bala_virupa", np.nan),
        "drik_benefic_virupa": drik.get("benefic_virupa", np.nan),
        "drik_malefic_virupa": drik.get("malefic_virupa", np.nan),
        "drik_raw_net_virupa": drik.get("raw_net_virupa", np.nan),
        "drik_benefic_raw_virupa": drik.get("benefic_raw_virupa", np.nan),
        "drik_malefic_raw_virupa": drik.get("malefic_raw_virupa", np.nan),
        "drik_normalization_divisor": drik.get(
            "normalization_divisor",
            DRIK_NORMALIZATION_DIVISOR,
        ),
        "nathonnatha_virupa": kaala.get("nathonnatha_virupa", np.nan),
        "paksha_virupa": kaala.get("paksha_virupa", np.nan),
        "tribhaga_virupa": kaala.get("tribhaga_virupa", np.nan),
        "abda_virupa": kaala.get("abda_virupa", np.nan),
        "masa_virupa": kaala.get("masa_virupa", np.nan),
        "vara_virupa": kaala.get("vara_virupa", np.nan),
        "hora_virupa": kaala.get("hora_virupa", np.nan),
        "ayana_virupa": kaala.get("ayana_virupa", np.nan),
        "yuddha_virupa": kaala.get("yuddha_virupa", np.nan),
        "kaala_7_virupa": kaala.get("kaala_7_virupa", np.nan),
        "kaala_9_virupa": kaala.get("kaala_9_virupa", np.nan),
        "kaala_7_profile": kaala.get("kaala_7_profile", ""),
        "kaala_9_profile": kaala.get("kaala_9_profile", ""),
        "kaala_complete": kaala.get("kaala_complete", False),
        "sunrise_lmt_hour": kaala.get("sunrise_lmt_hour", np.nan),
        "sunset_lmt_hour": kaala.get("sunset_lmt_hour", np.nan),
        "solar_time_status": kaala.get("solar_time_status", ""),
        "ahargana": kaala.get("ahargana", ""),
        "abda_lord": kaala.get("abda_lord", ""),
        "masa_lord": kaala.get("masa_lord", ""),
        "dina_lord": kaala.get("dina_lord", ""),
        "hora_lord": kaala.get("hora_lord", ""),
        "chesta_virupa": chesta,
        "chesta_motion_state_virupa": chesta_motion,
        "chesta_motion_state_status": chesta_motion_status,
        "chesta_effective_double_virupa": (
            2.0 * float(chesta)
            if body in CHESTA_REFERENCE_SPEED and np.isfinite(float(chesta))
            else np.nan
        ),
        "chesta_effective_motion_added_virupa": (
            float(chesta) + float(chesta_motion)
            if body in CHESTA_REFERENCE_SPEED
            and np.isfinite(float(chesta))
            and np.isfinite(float(chesta_motion))
            else np.nan
        ),
        "implemented_total_virupa": implemented_total,
        "implemented_total_complete": implemented_complete,
        "minimum_total_virupa": minimum if minimum is not None else np.nan,
        "implemented_total_ratio": ratio,
        "dignity_label": dignity.get("dignity_label", ""),
        "dignity_virupa": dignity.get("dignity_virupa", np.nan),
        "drik_aspects": drik.get("aspects", []),
        "drik_aspector_natures": drik.get("aspector_natures", []),
        "chesta_status": chesta_status,
        "yuddha_status": kaala.get("yuddha_status", ""),
    }


def aggregate_components(components: list[dict[str, Any]]) -> dict[str, Any]:
    if not components:
        return {}
    out: dict[str, Any] = {"body": "AVG(ALL)"}
    keys = [
        "naisargika_virupa",
        "uchcha_virupa",
        "saptavargaja_virupa",
        "saptavargaja_comparator_virupa",
        "ojayugma_virupa",
        "kendradi_virupa",
        "drekkana_virupa",
        "sthana_partial_virupa",
        "sthana_comparator_virupa",
        "dig_virupa",
        "drik_virupa",
        "drik_benefic_virupa",
        "drik_malefic_virupa",
        "drik_raw_net_virupa",
        "drik_benefic_raw_virupa",
        "drik_malefic_raw_virupa",
        "drik_normalization_divisor",
        "nathonnatha_virupa",
        "paksha_virupa",
        "tribhaga_virupa",
        "abda_virupa",
        "masa_virupa",
        "vara_virupa",
        "hora_virupa",
        "ayana_virupa",
        "yuddha_virupa",
        "kaala_7_virupa",
        "kaala_9_virupa",
        "chesta_virupa",
        "chesta_motion_state_virupa",
        "chesta_effective_double_virupa",
        "chesta_effective_motion_added_virupa",
        "implemented_total_virupa",
        "minimum_total_virupa",
        "implemented_total_ratio",
        "dignity_virupa",
    ]
    for key in keys:
        values = [float(item[key]) for item in components if key in item and np.isfinite(float(item[key]))]
        out[key] = float(sum(values) / len(values)) if values else np.nan
    out["house"] = ""
    out["sign"] = ""
    out["dignity_label"] = "avg_all"
    out["drik_aspects"] = []
    out["drik_aspector_natures"] = []
    out["saptavarga_details"] = []
    out["saptavargaja_profile"] = SAPTAVARGAJA_SOURCE_PROFILE
    out["saptavargaja_comparator_profile"] = SAPTAVARGAJA_PYJHORA_PROFILE
    out["kaala_7_profile"] = "jaya_seven_factor_interpretation"
    out["kaala_9_profile"] = "bphs_ch27_nine_factor_conventional"
    out["kaala_complete"] = all(bool(item.get("kaala_complete")) for item in components)
    out["implemented_total_complete"] = all(
        bool(item.get("implemented_total_complete"))
        for item in components
    )
    if not out["kaala_complete"]:
        out["kaala_9_virupa"] = np.nan
    if not out["implemented_total_complete"]:
        out["implemented_total_virupa"] = np.nan
        out["implemented_total_ratio"] = np.nan
    out["solar_time_status"] = "avg_all_component_context"
    out["chesta_motion_state_status"] = "avg_all_component_mean"
    out["chesta_status"] = "avg_all_component_mean"
    out["yuddha_status"] = "avg_all_component_mean"
    return out


def components_for_body(
    body: Any,
    longitudes: dict[str, float],
    asc_lon: Any,
    house_cusps: dict[int, float] | None,
    timestamp: Any = None,
    geo_lon: Any = None,
    speeds: dict[str, float] | None = None,
    latitudes: dict[str, float] | None = None,
    declinations: dict[str, float] | None = None,
    geo_lat: Any = None,
) -> dict[str, Any]:
    name = normalize_body(body)
    sun_lon = longitudes.get("SUN")
    moon_lon = longitudes.get("MOON")
    if name in {"AVG(ALL)", "AVG_ALL", "ALL"}:
        members = [
            shadbala_components_for_planet(
                planet,
                longitudes.get(planet),
                longitudes,
                asc_lon,
                house_cusps,
                sun_lon,
                moon_lon,
                timestamp,
                geo_lon,
                speeds,
                latitudes,
                declinations,
                geo_lat,
            )
            for planet in CLASSICAL_PLANETS
            if longitudes.get(planet) is not None
        ]
        return aggregate_components([item for item in members if item])
    return shadbala_components_for_planet(
        name,
        longitudes.get(name),
        longitudes,
        asc_lon,
        house_cusps,
        sun_lon,
        moon_lon,
        timestamp,
        geo_lon,
        speeds,
        latitudes,
        declinations,
        geo_lat,
    )


def prefix_components(prefix: str, components: dict[str, Any]) -> dict[str, Any]:
    if not components:
        return {}
    mapping = {
        "body": "strict_body",
        "sign": "strict_sign",
        "house": "strict_whole_sign_house",
        "naisargika_virupa": "strict_naisargika_virupa",
        "uchcha_virupa": "strict_uchcha_bala_virupa",
        "saptavargaja_virupa": "strict_saptavargaja_bala_virupa",
        "saptavargaja_comparator_virupa": "strict_saptavargaja_comparator_bala_virupa",
        "ojayugma_virupa": "strict_ojayugma_bala_virupa",
        "kendradi_virupa": "strict_kendradi_bala_virupa",
        "drekkana_virupa": "strict_drekkana_bala_virupa",
        "sthana_partial_virupa": "strict_sthana_partial_virupa",
        "sthana_comparator_virupa": "strict_sthana_comparator_virupa",
        "dig_virupa": "strict_dig_bala_virupa",
        "drik_virupa": "strict_drik_bala_virupa",
        "drik_benefic_virupa": "strict_drik_benefic_virupa",
        "drik_malefic_virupa": "strict_drik_malefic_virupa",
        "drik_raw_net_virupa": "strict_drik_raw_net_virupa",
        "drik_benefic_raw_virupa": "strict_drik_benefic_raw_virupa",
        "drik_malefic_raw_virupa": "strict_drik_malefic_raw_virupa",
        "drik_normalization_divisor": "strict_drik_normalization_divisor",
        "nathonnatha_virupa": "strict_nathonnatha_bala_virupa",
        "paksha_virupa": "strict_paksha_bala_virupa",
        "tribhaga_virupa": "strict_tribhaga_bala_virupa",
        "abda_virupa": "strict_abda_bala_virupa",
        "masa_virupa": "strict_masa_bala_virupa",
        "vara_virupa": "strict_vara_bala_virupa",
        "hora_virupa": "strict_hora_bala_virupa",
        "ayana_virupa": "strict_ayana_bala_virupa",
        "yuddha_virupa": "strict_yuddha_bala_virupa",
        "kaala_7_virupa": "strict_kaala_7_bala_virupa",
        "kaala_9_virupa": "strict_kaala_9_bala_virupa",
        "chesta_virupa": "strict_chesta_bala_virupa",
        "chesta_motion_state_virupa": "strict_chesta_motion_state_bala_virupa",
        "chesta_effective_double_virupa": "strict_chesta_effective_double_virupa",
        "chesta_effective_motion_added_virupa": "strict_chesta_effective_motion_added_virupa",
        "implemented_total_virupa": "strict_shadbala_implemented_total_virupa",
        "minimum_total_virupa": "strict_shadbala_minimum_total_virupa",
        "implemented_total_ratio": "strict_shadbala_implemented_total_ratio",
        "dignity_label": "strict_dignity_label",
        "dignity_virupa": "strict_dignity_virupa",
        "chesta_status": "strict_chesta_status",
        "chesta_motion_state_status": "strict_chesta_motion_state_status",
        "yuddha_status": "strict_yuddha_status",
        "solar_time_status": "strict_kaala_solar_time_status",
        "sunrise_lmt_hour": "strict_kaala_sunrise_lmt_hour",
        "sunset_lmt_hour": "strict_kaala_sunset_lmt_hour",
        "ahargana": "strict_kaala_ahargana",
        "abda_lord": "strict_kaala_abda_lord",
        "masa_lord": "strict_kaala_masa_lord",
        "dina_lord": "strict_kaala_dina_lord",
        "hora_lord": "strict_kaala_hora_lord",
        "kaala_complete": "strict_kaala_complete",
        "implemented_total_complete": "strict_shadbala_implemented_total_complete",
        "saptavargaja_profile": "strict_saptavargaja_profile",
        "saptavargaja_comparator_profile": "strict_saptavargaja_comparator_profile",
        "kaala_7_profile": "strict_kaala_7_profile",
        "kaala_9_profile": "strict_kaala_9_profile",
    }
    out = {f"{prefix}_{dst}": components.get(src, "") for src, dst in mapping.items()}
    out[f"{prefix}_strict_drik_aspects_json"] = json.dumps(components.get("drik_aspects", []), ensure_ascii=True)
    out[f"{prefix}_strict_drik_aspector_natures_json"] = json.dumps(
        components.get("drik_aspector_natures", []),
        ensure_ascii=True,
    )
    out[f"{prefix}_strict_saptavarga_details_json"] = json.dumps(components.get("saptavarga_details", []), ensure_ascii=True)
    return out


def event_strict_shadbala_context(
    b1: Any,
    b2: Any,
    longitudes: dict[str, float],
    asc_lon: Any,
    house_cusps: dict[int, float] | None = None,
    timestamp: Any = None,
    geo_lon: Any = None,
    speeds: dict[str, float] | None = None,
    latitudes: dict[str, float] | None = None,
    declinations: dict[str, float] | None = None,
    geo_lat: Any = None,
) -> dict[str, Any]:
    b1_components = components_for_body(
        b1,
        longitudes,
        asc_lon,
        house_cusps,
        timestamp,
        geo_lon,
        speeds,
        latitudes,
        declinations,
        geo_lat,
    )
    b2_components = components_for_body(
        b2,
        longitudes,
        asc_lon,
        house_cusps,
        timestamp,
        geo_lon,
        speeds,
        latitudes,
        declinations,
        geo_lat,
    )
    out: dict[str, Any] = {}
    out.update(prefix_components("event_b1", b1_components))
    out.update(prefix_components("event_b2", b2_components))
    for suffix in [
        "strict_drik_bala_virupa",
        "strict_drik_benefic_virupa",
        "strict_drik_malefic_virupa",
        "strict_drik_raw_net_virupa",
        "strict_drik_benefic_raw_virupa",
        "strict_drik_malefic_raw_virupa",
        "strict_saptavargaja_bala_virupa",
        "strict_ojayugma_bala_virupa",
        "strict_kaala_9_bala_virupa",
        "strict_chesta_bala_virupa",
        "strict_shadbala_implemented_total_virupa",
        "strict_shadbala_implemented_total_ratio",
    ]:
        values = [
            out.get(f"event_b1_{suffix}"),
            out.get(f"event_b2_{suffix}"),
        ]
        numeric: list[float] = []
        for value in values:
            try:
                converted = float(value)
            except (TypeError, ValueError):
                continue
            if np.isfinite(converted):
                numeric.append(converted)
        out[f"event_{suffix}_avg"] = float(sum(numeric) / len(numeric)) if numeric else np.nan
    out["event_strict_shadbala_rule_id"] = STRICT_SHADBALA_RULE_ID
    out["event_strict_drik_rule_id"] = STRICT_DRIK_RULE_ID
    out["event_strict_shadbala_status"] = STRICT_SHADBALA_STATUS
    out["event_strict_drik_status"] = STRICT_DRIK_STATUS
    out["event_strict_drik_normalization_rule_id"] = DRIK_NORMALIZATION_RULE_ID
    out["event_strict_drik_nature_rule_id"] = DRIK_NATURE_RULE_ID
    out["event_strict_drik_special_aspect_rule_id"] = DRIK_SPECIAL_ASPECT_RULE_ID
    out["event_strict_drik_normalization_divisor"] = DRIK_NORMALIZATION_DIVISOR
    out["event_strict_shadbala_missing_components"] = (
        "certified_graha_yuddha_disc_diameter_method|independent_jhora_component_witness|"
        "chesta_mean_longitude_model_crosscheck|ishta_kashta_phala"
    )
    out["event_strict_shadbala_component_rule_ids"] = "|".join(
        [SAPTAVARGAJA_RULE_ID, OJAYUGMA_RULE_ID, KAALA_RULE_ID, CHESTA_RULE_ID, YUDDHA_RULE_ID]
    )
    out["event_strict_shadbala_decision_notes"] = (
        "Rahu/Ketu excluded from Shadbala totals; AVG(ALL) is a seven-classical-planets component mean; "
        "Drik uses a transparent six-contribution ledger, divide-by-four normalization, waxing/waning Moon, "
        "Mercury sign-association classification, and range-based Mars/Jupiter/Saturn special aspects; "
        "Saptavargaja uses a BPHS source profile while the PyJHora weight profile is comparator-only; "
        "Moon Paksha and Chesta are doubled/source-linked and Sun Ayana is doubled; "
        "Kaala uses Swiss Ephemeris sunrise/sunset, a published 1860 Ahargana anchor, and sunrise day boundaries; "
        "non-luminary Chesta uses a source-structured mean/true longitude model while motion-state buckets remain diagnostic; "
        "Yuddha candidates fail closed until the disc-diameter doctrine is independently certified."
    )
    return out
