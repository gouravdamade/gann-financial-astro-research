from __future__ import annotations

from typing import Any

import pandas as pd


PANCHANGA_RULE_ID = "PANCHANGA_SIDEREAL_SUN_MOON_V1"
PANCHANGA_METHOD = "deterministic_sidereal_sun_moon"
PANCHANGA_SOURCE_STATUS = "formula_foundation_pending_traditional_validation"

NAKSHATRA_NAMES = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)

TITHI_NAMES = (
    "Pratipada",
    "Dvitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dvadashi",
    "Trayodashi",
    "Chaturdashi",
    "Purnima",
    "Pratipada",
    "Dvitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dvadashi",
    "Trayodashi",
    "Chaturdashi",
    "Amavasya",
)

YOGA_NAMES = (
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shoola",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyana",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
)

MOVABLE_KARANAS = ("Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti")
WEEKDAY_LORDS = {
    0: "MOON",
    1: "MARS",
    2: "MERCURY",
    3: "JUPITER",
    4: "VENUS",
    5: "SATURN",
    6: "SUN",
}
NAKSHATRA_WIDTH = 360.0 / 27.0
NAKSHATRA_PADA_WIDTH = NAKSHATRA_WIDTH / 4.0


def normalize_longitude(value: Any) -> float | None:
    try:
        lon = float(value) % 360.0
    except (TypeError, ValueError):
        return None
    if pd.isna(lon):
        return None
    return lon


def nakshatra_pada(value: Any) -> dict[str, Any]:
    lon = normalize_longitude(value)
    if lon is None:
        return {"index": "", "name": "", "pada": ""}
    index0 = min(26, int(lon // NAKSHATRA_WIDTH))
    offset = lon - (index0 * NAKSHATRA_WIDTH)
    pada = min(4, int(offset // NAKSHATRA_PADA_WIDTH) + 1)
    return {"index": index0 + 1, "name": NAKSHATRA_NAMES[index0], "pada": pada}


def tithi_context(sun_lon: Any, moon_lon: Any) -> dict[str, Any]:
    sun = normalize_longitude(sun_lon)
    moon = normalize_longitude(moon_lon)
    if sun is None or moon is None:
        return {"phase_angle_deg": "", "tithi_index": "", "tithi_name": "", "paksha": ""}
    phase = (moon - sun) % 360.0
    index0 = min(29, int(phase // 12.0))
    return {
        "phase_angle_deg": round(phase, 6),
        "tithi_index": index0 + 1,
        "tithi_name": TITHI_NAMES[index0],
        "paksha": "Shukla" if index0 < 15 else "Krishna",
    }


def karana_context(phase_angle_deg: Any) -> dict[str, Any]:
    try:
        phase = float(phase_angle_deg) % 360.0
    except (TypeError, ValueError):
        return {"karana_index": "", "karana_name": ""}
    if pd.isna(phase):
        return {"karana_index": "", "karana_name": ""}
    index = min(60, int(phase // 6.0) + 1)
    if index == 1:
        name = "Kimstughna"
    elif index == 58:
        name = "Shakuni"
    elif index == 59:
        name = "Chatushpada"
    elif index == 60:
        name = "Naga"
    else:
        name = MOVABLE_KARANAS[(index - 2) % len(MOVABLE_KARANAS)]
    return {"karana_index": index, "karana_name": name}


def yoga_context(sun_lon: Any, moon_lon: Any) -> dict[str, Any]:
    sun = normalize_longitude(sun_lon)
    moon = normalize_longitude(moon_lon)
    if sun is None or moon is None:
        return {"yoga_angle_deg": "", "yoga_index": "", "yoga_name": ""}
    angle = (sun + moon) % 360.0
    index0 = min(26, int(angle // NAKSHATRA_WIDTH))
    return {"yoga_angle_deg": round(angle, 6), "yoga_index": index0 + 1, "yoga_name": YOGA_NAMES[index0]}


def weekday_context(timestamp: Any) -> dict[str, Any]:
    try:
        ts = pd.Timestamp(timestamp)
    except Exception:
        return {"weekday": "", "weekday_lord": ""}
    if pd.isna(ts):
        return {"weekday": "", "weekday_lord": ""}
    if ts.tzinfo is not None:
        ts = ts.tz_convert("Asia/Kolkata")
    weekday = int(ts.weekday())
    return {"weekday": ts.day_name(), "weekday_lord": WEEKDAY_LORDS.get(weekday, "")}


def panchanga_context(prefix: str, timestamp: Any, sun_lon: Any, moon_lon: Any) -> dict[str, Any]:
    tithi = tithi_context(sun_lon, moon_lon)
    karana = karana_context(tithi.get("phase_angle_deg"))
    yoga = yoga_context(sun_lon, moon_lon)
    weekday = weekday_context(timestamp)
    moon_nak = nakshatra_pada(moon_lon)
    sun_nak = nakshatra_pada(sun_lon)
    phase = tithi.get("phase_angle_deg")
    near_new = ""
    near_full = ""
    if isinstance(phase, (int, float)):
        near_new = int(min(float(phase), 360.0 - float(phase)) <= 12.0)
        near_full = int(abs(float(phase) - 180.0) <= 12.0)
    return {
        f"{prefix}_panchanga_method": PANCHANGA_METHOD,
        f"{prefix}_panchanga_rule_ids": PANCHANGA_RULE_ID,
        f"{prefix}_panchanga_status": PANCHANGA_SOURCE_STATUS,
        f"{prefix}_weekday": weekday["weekday"],
        f"{prefix}_weekday_lord": weekday["weekday_lord"],
        f"{prefix}_lunar_phase_angle_deg": tithi["phase_angle_deg"],
        f"{prefix}_tithi_index": tithi["tithi_index"],
        f"{prefix}_tithi_name": tithi["tithi_name"],
        f"{prefix}_paksha": tithi["paksha"],
        f"{prefix}_karana_index": karana["karana_index"],
        f"{prefix}_karana_name": karana["karana_name"],
        f"{prefix}_yoga_angle_deg": yoga["yoga_angle_deg"],
        f"{prefix}_yoga_index": yoga["yoga_index"],
        f"{prefix}_yoga_name": yoga["yoga_name"],
        f"{prefix}_moon_nakshatra_index": moon_nak["index"],
        f"{prefix}_moon_nakshatra": moon_nak["name"],
        f"{prefix}_moon_pada": moon_nak["pada"],
        f"{prefix}_sun_nakshatra_index": sun_nak["index"],
        f"{prefix}_sun_nakshatra": sun_nak["name"],
        f"{prefix}_sun_pada": sun_nak["pada"],
        f"{prefix}_near_new_moon_flag": near_new,
        f"{prefix}_near_full_moon_flag": near_full,
    }


def panchanga_change_flags(
    prefix: str,
    start_context: dict[str, Any],
    end_context: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "weekday": "weekday",
        "tithi": "tithi_index",
        "karana": "karana_index",
        "yoga": "yoga_index",
        "moon_nakshatra": "moon_nakshatra_index",
        "moon_pada": "moon_pada",
    }
    out: dict[str, Any] = {}
    for label, suffix in checks.items():
        start_value = start_context.get(f"{prefix}_start_{suffix}", "")
        end_value = end_context.get(f"{prefix}_end_{suffix}", "")
        if start_value == "" or end_value == "":
            out[f"{prefix}_{label}_changed_flag"] = ""
        else:
            out[f"{prefix}_{label}_changed_flag"] = int(str(start_value) != str(end_value))
    return out
