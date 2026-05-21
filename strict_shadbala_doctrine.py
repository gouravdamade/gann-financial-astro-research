from __future__ import annotations

import json
from typing import Any

import numpy as np

from shadbala_doctrine import (
    CLASSICAL_PLANETS,
    DEBILITATION_SIGNS,
    EXALTATION_SIGNS,
    SHADBALA_MINIMUM_TOTAL_VIRUPA,
    dignity_for_planet_in_sign,
    minimum_shadbala_total_virupa,
    normalize_body,
    normalize_sign,
)


STRICT_SHADBALA_RULE_ID = "STRICT_SHADBALA_V2_PARTIAL_COMPONENTS"
STRICT_DRIK_RULE_ID = "PARASHARA_SRIPATI_DRIK_BALA_SIX_FORMULA_V1"
STRICT_SHADBALA_STATUS = "partial_high_confidence_components_pending_saptavargaja_kaala_chesta_yuddha"
STRICT_DRIK_STATUS = "strict_formula_signed_natural_benefic_malefic"

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
NATURAL_MALEFICS = {"SUN", "MARS", "SATURN"}
NATURAL_BENEFICS = {"JUPITER", "VENUS", "MERCURY"}
DRIK_SPECIAL_BONUS = {
    "JUPITER": {120: 30.0, 240: 30.0},
    "SATURN": {60: 45.0, 270: 45.0},
    "MARS": {90: 15.0, 210: 15.0},
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
    try:
        d = float(angle) % 360.0
    except (TypeError, ValueError):
        return 0.0
    if d < 30.0 or d > 300.0:
        return 0.0
    if d <= 60.0:
        return 0.5 * (d - 30.0)
    if d <= 90.0:
        return 15.0 + (d - 60.0)
    if d <= 120.0:
        return 45.0 - 0.5 * (d - 90.0)
    if d <= 150.0:
        return 30.0 - (d - 120.0)
    if d <= 180.0:
        return 2.0 * (d - 150.0)
    if d <= 300.0:
        return 60.0 - 0.5 * (d - 180.0)
    return 0.0


def drik_special_bonus_virupa(planet: Any, angle: Any) -> float:
    body = normalize_body(planet)
    try:
        d = float(angle) % 360.0
    except (TypeError, ValueError):
        return 0.0
    bonuses = DRIK_SPECIAL_BONUS.get(body, {})
    bonus = 0.0
    for exact_angle, value in bonuses.items():
        if abs(d - float(exact_angle)) < 1e-9:
            bonus = max(bonus, float(value))
    return bonus


def drik_aspector_sign(planet: Any, sun_lon: Any, moon_lon: Any) -> int:
    body = normalize_body(planet)
    if body in NATURAL_MALEFICS:
        return -1
    if body in NATURAL_BENEFICS:
        return 1
    if body == "MOON":
        sun = normalize_longitude(sun_lon)
        moon = normalize_longitude(moon_lon)
        if sun is None or moon is None:
            return 1
        phase = (moon - sun) % 360.0
        return 1 if phase <= 180.0 else -1
    return 0


def strict_drik_bala_for_planet(
    target: Any,
    longitudes: dict[str, float],
    sun_lon: Any,
    moon_lon: Any,
) -> dict[str, Any]:
    target_body = normalize_body(target)
    target_lon = longitudes.get(target_body)
    if target_lon is None or target_body not in CLASSICAL_PLANETS:
        return {"drik_bala_virupa": np.nan, "benefic_virupa": np.nan, "malefic_virupa": np.nan, "aspects": []}
    benefic = 0.0
    malefic = 0.0
    aspects: list[dict[str, Any]] = []
    for aspector in CLASSICAL_PLANETS:
        if aspector == target_body:
            continue
        aspector_lon = longitudes.get(aspector)
        if aspector_lon is None:
            continue
        angle = forward_angle(aspector_lon, target_lon)
        if angle is None:
            continue
        base = drik_base_strength_virupa(angle)
        bonus = drik_special_bonus_virupa(aspector, round(angle))
        strength = float(base + bonus)
        if strength <= 0.0:
            continue
        sign = drik_aspector_sign(aspector, sun_lon, moon_lon)
        signed = strength * sign
        if signed >= 0:
            benefic += signed
        else:
            malefic += signed
        aspects.append(
            {
                "from": aspector,
                "angle_deg": round(float(angle), 6),
                "base_virupa": round(float(base), 6),
                "special_bonus_virupa": round(float(bonus), 6),
                "signed_virupa": round(float(signed), 6),
            }
        )
    return {
        "drik_bala_virupa": float(benefic + malefic),
        "benefic_virupa": float(benefic),
        "malefic_virupa": float(malefic),
        "aspects": aspects,
    }


def shadbala_components_for_planet(
    planet: Any,
    lon: Any,
    longitudes: dict[str, float],
    asc_lon: Any,
    house_cusps: dict[int, float] | None,
    sun_lon: Any,
    moon_lon: Any,
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
    kendradi = kendradi_bala_virupa(house)
    drekkana = drekkana_bala_virupa(body, value)
    dig = dig_bala_virupa(body, value, house_cusps, asc_lon)
    sthana_partial_values = [uchcha, kendradi, drekkana]
    sthana_partial = float(sum(v for v in sthana_partial_values if np.isfinite(float(v))))
    implemented_values = [
        NAISARGIKA_VIRUPA.get(body, np.nan),
        uchcha,
        kendradi,
        drekkana,
        dig,
        drik.get("drik_bala_virupa", np.nan),
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
        "kendradi_virupa": kendradi,
        "drekkana_virupa": drekkana,
        "sthana_partial_virupa": sthana_partial,
        "dig_virupa": dig,
        "drik_virupa": drik.get("drik_bala_virupa", np.nan),
        "drik_benefic_virupa": drik.get("benefic_virupa", np.nan),
        "drik_malefic_virupa": drik.get("malefic_virupa", np.nan),
        "implemented_total_virupa": implemented_total,
        "minimum_total_virupa": minimum if minimum is not None else np.nan,
        "implemented_total_ratio": ratio,
        "dignity_label": dignity.get("dignity_label", ""),
        "dignity_virupa": dignity.get("dignity_virupa", np.nan),
        "drik_aspects": drik.get("aspects", []),
    }


def aggregate_components(components: list[dict[str, Any]]) -> dict[str, Any]:
    if not components:
        return {}
    out: dict[str, Any] = {"body": "AVG(ALL)"}
    keys = [
        "naisargika_virupa",
        "uchcha_virupa",
        "kendradi_virupa",
        "drekkana_virupa",
        "sthana_partial_virupa",
        "dig_virupa",
        "drik_virupa",
        "drik_benefic_virupa",
        "drik_malefic_virupa",
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
    return out


def components_for_body(
    body: Any,
    longitudes: dict[str, float],
    asc_lon: Any,
    house_cusps: dict[int, float] | None,
) -> dict[str, Any]:
    name = normalize_body(body)
    sun_lon = longitudes.get("SUN")
    moon_lon = longitudes.get("MOON")
    if name in {"AVG(ALL)", "AVG_ALL", "ALL"}:
        members = [
            shadbala_components_for_planet(planet, longitudes.get(planet), longitudes, asc_lon, house_cusps, sun_lon, moon_lon)
            for planet in CLASSICAL_PLANETS
            if longitudes.get(planet) is not None
        ]
        return aggregate_components([item for item in members if item])
    return shadbala_components_for_planet(name, longitudes.get(name), longitudes, asc_lon, house_cusps, sun_lon, moon_lon)


def prefix_components(prefix: str, components: dict[str, Any]) -> dict[str, Any]:
    if not components:
        return {}
    mapping = {
        "body": "strict_body",
        "sign": "strict_sign",
        "house": "strict_whole_sign_house",
        "naisargika_virupa": "strict_naisargika_virupa",
        "uchcha_virupa": "strict_uchcha_bala_virupa",
        "kendradi_virupa": "strict_kendradi_bala_virupa",
        "drekkana_virupa": "strict_drekkana_bala_virupa",
        "sthana_partial_virupa": "strict_sthana_partial_virupa",
        "dig_virupa": "strict_dig_bala_virupa",
        "drik_virupa": "strict_drik_bala_virupa",
        "drik_benefic_virupa": "strict_drik_benefic_virupa",
        "drik_malefic_virupa": "strict_drik_malefic_virupa",
        "implemented_total_virupa": "strict_shadbala_implemented_total_virupa",
        "minimum_total_virupa": "strict_shadbala_minimum_total_virupa",
        "implemented_total_ratio": "strict_shadbala_implemented_total_ratio",
        "dignity_label": "strict_dignity_label",
        "dignity_virupa": "strict_dignity_virupa",
    }
    out = {f"{prefix}_{dst}": components.get(src, "") for src, dst in mapping.items()}
    out[f"{prefix}_strict_drik_aspects_json"] = json.dumps(components.get("drik_aspects", []), ensure_ascii=True)
    return out


def event_strict_shadbala_context(
    b1: Any,
    b2: Any,
    longitudes: dict[str, float],
    asc_lon: Any,
    house_cusps: dict[int, float] | None = None,
) -> dict[str, Any]:
    b1_components = components_for_body(b1, longitudes, asc_lon, house_cusps)
    b2_components = components_for_body(b2, longitudes, asc_lon, house_cusps)
    out: dict[str, Any] = {}
    out.update(prefix_components("event_b1", b1_components))
    out.update(prefix_components("event_b2", b2_components))
    for suffix in [
        "strict_drik_bala_virupa",
        "strict_drik_benefic_virupa",
        "strict_drik_malefic_virupa",
        "strict_shadbala_implemented_total_virupa",
        "strict_shadbala_implemented_total_ratio",
    ]:
        values = [
            out.get(f"event_b1_{suffix}"),
            out.get(f"event_b2_{suffix}"),
        ]
        numeric = [float(value) for value in values if value is not None and np.isfinite(float(value))]
        out[f"event_{suffix}_avg"] = float(sum(numeric) / len(numeric)) if numeric else np.nan
    out["event_strict_shadbala_rule_id"] = STRICT_SHADBALA_RULE_ID
    out["event_strict_drik_rule_id"] = STRICT_DRIK_RULE_ID
    out["event_strict_shadbala_status"] = STRICT_SHADBALA_STATUS
    out["event_strict_drik_status"] = STRICT_DRIK_STATUS
    out["event_strict_shadbala_missing_components"] = (
        "saptavargaja_bala|ojayugma_bala|full_kaala_bala|chesta_bala|yuddha_bala"
    )
    return out
