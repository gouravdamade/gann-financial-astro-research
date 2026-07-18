from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np

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
    DEBILITATION_SIGNS,
    EXALTATION_SIGNS,
    MOOLATRIKONA_SIGNS,
    NATURAL_RELATIONSHIPS,
    OWN_SIGNS,
    SIGN_LORDS,
    dignity_for_planet_in_sign,
    minimum_shadbala_total_virupa,
    normalize_body,
    normalize_sign,
)


STRICT_SHADBALA_RULE_ID = "STRICT_SHADBALA_V5_DRIK_RECONCILED_PROVISIONAL"
STRICT_DRIK_RULE_ID = DRIK_ENGINE_RULE_ID
STRICT_SHADBALA_STATUS = (
    "provisional_source_aligned_drik_tier_b_pending_sunrise_abda_masa_chesta_yuddha_and_independent_validation"
)
STRICT_DRIK_STATUS = DRIK_ENGINE_STATUS
SAPTAVARGAJA_RULE_ID = "SAPTAVARGAJA_PARASHARA_SEVEN_VARGA_COMPOUND_RELATION_V1"
OJAYUGMA_RULE_ID = "OJAYUGMA_ODD_EVEN_RASHI_NAVAMSA_V1"
KAALA_RULE_ID = "KAALA_BALA_NATHONNATHA_PAKSHA_TRIBHAGA_ABDA_MASA_VARA_HORA_AYANA_YUDDHA_V1"
CHESTA_RULE_ID = "CHESTA_BALA_SOURCE_BUCKETS_PROVISIONAL_V2"
YUDDHA_RULE_ID = "YUDDHA_BALA_UNCERTIFIED_EXCLUDED_V2"

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
SAPTAVARGAJA_VIRUPA_BY_DIGNITY = {
    "exaltation": 60.0,
    "moolatrikona": 45.0,
    "own": 30.0,
    "great_friend": 20.0,
    "friend": 15.0,
    "neutral": 10.0,
    "enemy": 4.0,
    "great_enemy": 2.0,
    "debilitation": 0.0,
    "unknown": np.nan,
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


def saptavargaja_dignity(planet: Any, varga_sign: Any, d1_planet_sign: Any, longitudes: dict[str, float]) -> dict[str, Any]:
    body = normalize_body(planet)
    sign = normalize_sign(varga_sign)
    if body not in CLASSICAL_PLANETS or sign not in SIGN_LORDS:
        return {"label": "unknown", "virupa": np.nan, "sign_lord": SIGN_LORDS.get(sign, ""), "relation": "unknown"}
    if sign == DEBILITATION_SIGNS.get(body):
        label = "debilitation"
        relation = "enemy"
    elif sign == EXALTATION_SIGNS.get(body):
        label = "exaltation"
        relation = "friend"
    elif sign == MOOLATRIKONA_SIGNS.get(body):
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
        "virupa": float(SAPTAVARGAJA_VIRUPA_BY_DIGNITY.get(label, np.nan)),
        "sign_lord": SIGN_LORDS.get(sign, ""),
        "relation": relation,
    }


def saptavargaja_bala(planet: Any, lon: Any, longitudes: dict[str, float]) -> dict[str, Any]:
    body = normalize_body(planet)
    value = normalize_longitude(lon)
    if body not in CLASSICAL_PLANETS or value is None:
        return {"saptavargaja_virupa": np.nan, "saptavarga_details": []}
    d1_sign = sign_from_lon(value)
    details: list[dict[str, Any]] = []
    total = 0.0
    for varga, sign in saptavarga_signs(value).items():
        dignity = saptavargaja_dignity(body, sign, d1_sign, longitudes)
        virupa = dignity.get("virupa", np.nan)
        if np.isfinite(float(virupa)):
            total += float(virupa)
        details.append(
            {
                "varga": varga,
                "sign": sign,
                "label": dignity.get("label", "unknown"),
                "virupa": round(float(virupa), 6) if np.isfinite(float(virupa)) else None,
            }
        )
    return {"saptavargaja_virupa": float(total), "saptavarga_details": details}


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
    if body in FEMALE_PLANETS and drekkana == 2:
        return 15.0
    if body in NEUTER_PLANETS and drekkana == 3:
        return 15.0
    return 0.0


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


def vara_bala_virupa(planet: Any, timestamp: Any, geo_lon: Any = None) -> float:
    body = normalize_body(planet)
    lord = weekday_lord_for_lmt(timestamp, geo_lon)
    return 45.0 if body == lord else 0.0


def hora_lord_for_lmt(timestamp: Any, geo_lon: Any = None, sunrise_hour: float = 6.0) -> str:
    lmt = local_mean_datetime(timestamp, geo_lon)
    if lmt is None:
        return ""
    day_lord = WEEKDAY_LORDS[lmt.weekday()]
    start_idx = CHALDEAN_HORA_ORDER.index(day_lord) if day_lord in CHALDEAN_HORA_ORDER else 0
    hour = lmt.hour + (lmt.minute / 60.0) + (lmt.second / 3600.0)
    elapsed_hours = int(math.floor((hour - float(sunrise_hour)) % 24.0))
    return CHALDEAN_HORA_ORDER[(start_idx + elapsed_hours) % 7]


def hora_bala_virupa(planet: Any, timestamp: Any, geo_lon: Any = None, sunrise_hour: float = 6.0) -> float:
    return 60.0 if normalize_body(planet) == hora_lord_for_lmt(timestamp, geo_lon, sunrise_hour) else 0.0


def ahargana_index(timestamp: Any, geo_lon: Any = None) -> int | None:
    lmt = local_mean_datetime(timestamp, geo_lon)
    if lmt is None:
        return None
    epoch = datetime(2000, 1, 1, tzinfo=timezone.utc)
    return int((lmt.replace(tzinfo=timezone.utc) - epoch).total_seconds() // 86400)


def abda_masa_lords(timestamp: Any, geo_lon: Any = None) -> tuple[str, str]:
    index = ahargana_index(timestamp, geo_lon)
    if index is None:
        return "", ""
    abda = WEEKDAY_LORDS[index % 7]
    masa = WEEKDAY_LORDS[(index // 30) % 7]
    return abda, masa


def abda_bala_virupa(planet: Any, timestamp: Any, geo_lon: Any = None) -> float:
    abda, _ = abda_masa_lords(timestamp, geo_lon)
    return 15.0 if normalize_body(planet) == abda else 0.0


def masa_bala_virupa(planet: Any, timestamp: Any, geo_lon: Any = None) -> float:
    _, masa = abda_masa_lords(timestamp, geo_lon)
    return 30.0 if normalize_body(planet) == masa else 0.0


def ayana_bala_virupa(planet: Any, declination_deg: Any) -> float:
    body = normalize_body(planet)
    try:
        dec = float(declination_deg)
    except (TypeError, ValueError):
        return np.nan
    if body not in CLASSICAL_PLANETS or not np.isfinite(dec):
        return np.nan
    normalized = max(-1.0, min(1.0, dec / 24.0))
    if body in AYANA_NORTH_STRONG:
        value = float(max(0.0, min(60.0, 30.0 + (30.0 * normalized))))
        return 2.0 * value if body == "SUN" else value
    if body in AYANA_SOUTH_STRONG:
        return float(max(0.0, min(60.0, 30.0 - (30.0 * normalized))))
    if body == "MERCURY":
        return float(max(0.0, min(60.0, 30.0 + (30.0 * abs(normalized)))))
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
        return 0.0, f"yuddha_candidate_vs_{other.lower()}_uncertified_excluded_from_total"
    return 0.0, "no_graha_yuddha_candidate_within_1deg"


def kaala_bala_components(
    planet: Any,
    timestamp: Any,
    geo_lon: Any,
    sun_lon: Any,
    moon_lon: Any,
    declination_deg: Any,
    longitudes: dict[str, float],
    latitudes: dict[str, float] | None = None,
    sunrise_hour: float = 6.0,
    sunset_hour: float = 18.0,
) -> dict[str, Any]:
    body = normalize_body(planet)
    if body not in CLASSICAL_PLANETS:
        return {}
    yuddha, yuddha_status = yuddha_bala_virupa(body, longitudes, latitudes)
    parts = {
        "nathonnatha_virupa": nathonnatha_bala_virupa(body, timestamp, geo_lon),
        "paksha_virupa": paksha_bala_virupa(body, sun_lon, moon_lon),
        "tribhaga_virupa": tribhaga_bala_virupa(body, timestamp, geo_lon, sunrise_hour, sunset_hour),
        "abda_virupa": abda_bala_virupa(body, timestamp, geo_lon),
        "masa_virupa": masa_bala_virupa(body, timestamp, geo_lon),
        "vara_virupa": vara_bala_virupa(body, timestamp, geo_lon),
        "hora_virupa": hora_bala_virupa(body, timestamp, geo_lon, sunrise_hour),
        "ayana_virupa": ayana_bala_virupa(body, declination_deg),
        "yuddha_virupa": yuddha,
        "yuddha_status": yuddha_status,
    }
    seven_keys = ["nathonnatha_virupa", "paksha_virupa", "tribhaga_virupa", "abda_virupa", "masa_virupa", "vara_virupa", "hora_virupa"]
    nine_keys = seven_keys + ["ayana_virupa", "yuddha_virupa"]
    parts["kaala_7_virupa"] = float(sum(float(parts[k]) for k in seven_keys if np.isfinite(float(parts[k]))))
    parts["kaala_9_virupa"] = float(sum(float(parts[k]) for k in nine_keys if np.isfinite(float(parts[k]))))
    return parts


def chesta_bala_virupa(
    planet: Any,
    speed_deg_day: Any,
    ayana_virupa: Any = None,
    paksha_virupa: Any = None,
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
        return 60.0, "vakra_retrograde"
    ratio = abs(speed) / ref if ref else np.nan
    if not np.isfinite(ratio):
        return np.nan, "bad_speed_reference"
    if ratio < 0.15:
        return 15.0, "vikala_near_station_provisional_speed_bucket"
    if ratio < 0.50:
        return 15.0, "mandatara_slow_direct_provisional_speed_bucket"
    if ratio < 0.90:
        return 30.0, "manda_direct_provisional_speed_bucket"
    if ratio <= 1.25:
        return 7.5, "sama_normal_direct_provisional_speed_bucket"
    if ratio <= 1.75:
        return 45.0, "chara_fast_direct_provisional_speed_bucket"
    return 30.0, "atichara_very_fast_direct_provisional_speed_bucket"


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
) -> dict[str, Any]:
    body = normalize_body(planet)
    value = normalize_longitude(lon)
    if body not in CLASSICAL_PLANETS or value is None:
        return {}
    sign = sign_from_lon(value)
    dignity = dignity_for_planet_in_sign(body, sign)
    house = whole_sign_house(value, asc_lon)
    drik = strict_drik_bala_for_planet(body, longitudes, sun_lon, moon_lon)
    uchcha = exaltation_bala_virupa(body, value)
    saptavargaja = saptavargaja_bala(body, value, longitudes)
    ojayugma = ojayugma_bala_virupa(body, value)
    kendradi = kendradi_bala_virupa(house)
    drekkana = drekkana_bala_virupa(body, value)
    dig = dig_bala_virupa(body, value, house_cusps, asc_lon)
    kaala = kaala_bala_components(
        body,
        timestamp,
        geo_lon,
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
    )
    sthana_partial_values = [uchcha, saptavargaja.get("saptavargaja_virupa", np.nan), ojayugma, kendradi, drekkana]
    sthana_partial = float(sum(v for v in sthana_partial_values if np.isfinite(float(v))))
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
    implemented_total = float(sum(v for v in implemented_values if v is not None and np.isfinite(float(v))))
    minimum = minimum_shadbala_total_virupa(body)
    ratio = implemented_total / float(minimum) if minimum else np.nan
    return {
        "body": body,
        "sign": sign,
        "house": house if house is not None else "",
        "naisargika_virupa": NAISARGIKA_VIRUPA.get(body, np.nan),
        "uchcha_virupa": uchcha,
        "saptavargaja_virupa": saptavargaja.get("saptavargaja_virupa", np.nan),
        "saptavarga_details": saptavargaja.get("saptavarga_details", []),
        "ojayugma_virupa": ojayugma,
        "kendradi_virupa": kendradi,
        "drekkana_virupa": drekkana,
        "sthana_partial_virupa": sthana_partial,
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
        "chesta_virupa": chesta,
        "implemented_total_virupa": implemented_total,
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
        "ojayugma_virupa",
        "kendradi_virupa",
        "drekkana_virupa",
        "sthana_partial_virupa",
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
        "ojayugma_virupa": "strict_ojayugma_bala_virupa",
        "kendradi_virupa": "strict_kendradi_bala_virupa",
        "drekkana_virupa": "strict_drekkana_bala_virupa",
        "sthana_partial_virupa": "strict_sthana_partial_virupa",
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
        "implemented_total_virupa": "strict_shadbala_implemented_total_virupa",
        "minimum_total_virupa": "strict_shadbala_minimum_total_virupa",
        "implemented_total_ratio": "strict_shadbala_implemented_total_ratio",
        "dignity_label": "strict_dignity_label",
        "dignity_virupa": "strict_dignity_virupa",
        "chesta_status": "strict_chesta_status",
        "yuddha_status": "strict_yuddha_status",
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
) -> dict[str, Any]:
    b1_components = components_for_body(b1, longitudes, asc_lon, house_cusps, timestamp, geo_lon, speeds, latitudes, declinations)
    b2_components = components_for_body(b2, longitudes, asc_lon, house_cusps, timestamp, geo_lon, speeds, latitudes, declinations)
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
        "actual_sunrise_sunset|traditional_abda_masa_epoch|full_chesta_mean_true_anomaly|"
        "certified_graha_yuddha|external_canonical_calculator_validation|ishta_kashta_phala"
    )
    out["event_strict_shadbala_component_rule_ids"] = "|".join(
        [SAPTAVARGAJA_RULE_ID, OJAYUGMA_RULE_ID, KAALA_RULE_ID, CHESTA_RULE_ID, YUDDHA_RULE_ID]
    )
    out["event_strict_shadbala_decision_notes"] = (
        "Rahu/Ketu excluded from Shadbala totals; AVG(ALL) is a seven-classical-planets component mean; "
        "Drik uses a transparent six-contribution ledger, divide-by-four normalization, waxing/waning Moon, "
        "Mercury sign-association classification, and range-based Mars/Jupiter/Saturn special aspects; "
        "Moon Paksha and Chesta are doubled/source-linked and Sun Ayana is doubled; "
        "Kaala still uses fixed 06:00/18:00 plus provisional Abda/Masa epochs; "
        "non-luminary Chesta uses provisional speed buckets; Yuddha candidates are detected but score zero until certified."
    )
    return out
