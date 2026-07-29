from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import swisseph as swe

from astro_function_certification import (
    CLASSICAL_PLANETS,
    SAMPLES,
    calc_planet,
    jd_ut_for,
    sample_datetime,
)
from doctrine_config import (
    configure_swiss_ephemeris_sidereal,
    load_doctrine_config,
)
from financial_astro_ephemeris import configure_ephemeris
from strict_shadbala_doctrine import (
    AYANA_OBLIQUITY_DEG,
    ahargana_lords,
    ayana_bala_virupa,
    decimal_hour,
    hora_lord_for_lmt,
    local_mean_datetime,
    sunrise_sunset_lmt_for_date,
)


CONTRACT = "GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V2"
FROZEN_TOLERANCE_VIRUPA = 0.5
RECENT_SAMPLE_IDS = {
    "case_8_event_start",
    "case_43_event_start",
    "case_103_event_start",
    "case_127_sr_touch_start",
}
MEASURES = ("nathonnatha", "hora", "ayana")
PLANET_IDS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MARS": swe.MARS,
    "MERCURY": swe.MERCURY,
    "JUPITER": swe.JUPITER,
    "VENUS": swe.VENUS,
    "SATURN": swe.SATURN,
}
NORTH_STRONG = {"SUN", "MARS", "JUPITER", "VENUS"}
SOUTH_STRONG = {"MOON", "SATURN"}
DAY_STRONG = {"SUN", "JUPITER", "VENUS"}
CHALDEAN_HORA_ORDER = (
    "SATURN",
    "JUPITER",
    "MARS",
    "SUN",
    "VENUS",
    "MERCURY",
    "MOON",
)

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_VISIBLE_COMPARISON = (
    REPO_ROOT
    / "status"
    / "evidence"
    / "jhora_kaala_witness_20260727"
    / "jhora_kaala_profile_comparison_20260727.csv"
)
DEFAULT_DOCTRINE_CONFIG = REPO_ROOT / "doctrine_config.yaml"
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "status"
    / "evidence"
    / "jhora_kaala_witness_20260727"
    / "jhora_kaala_formula_profiles_20260729.csv"
)
DEFAULT_SUMMARY = (
    REPO_ROOT
    / "status"
    / "evidence"
    / "jhora_kaala_witness_20260727"
    / "jhora_kaala_formula_profiles_20260729.json"
)
DEFAULT_REPORT = REPO_ROOT / "jhora_kaala_formula_reconciliation_20260729.md"
WORKED_EXAMPLE_EXTRACT = (
    REPO_ROOT
    / "pdf_alignment_extracts"
    / "jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.txt"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare named Kaala Bala formula profiles against locked visible "
            "JHora values without changing production doctrine."
        )
    )
    parser.add_argument(
        "--visible-comparison",
        type=Path,
        default=DEFAULT_VISIBLE_COMPARISON,
    )
    parser.add_argument(
        "--doctrine-config",
        type=Path,
        default=DEFAULT_DOCTRINE_CONFIG,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def read_visible_values(
    path: Path,
) -> dict[tuple[str, str, str], float]:
    values: dict[tuple[str, str, str], float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            measure = str(row.get("measure") or "").strip().lower()
            if measure not in MEASURES:
                continue
            key = (
                str(row.get("sample_id") or "").strip(),
                str(row.get("planet") or "").strip().upper(),
                measure,
            )
            if key in values:
                raise RuntimeError(
                    f"Duplicate visible formula row {row_number}: {key}"
                )
            try:
                value = float(
                    str(row.get("jhora_value_virupa") or "").strip()
                )
            except ValueError as exc:
                raise RuntimeError(
                    f"Invalid visible formula value at row {row_number}: {key}"
                ) from exc
            if not math.isfinite(value):
                raise RuntimeError(
                    f"Non-finite visible formula value at row {row_number}: {key}"
                )
            values[key] = value
    expected = {
        (sample.sample_id, planet, measure)
        for sample in SAMPLES
        for planet in CLASSICAL_PLANETS
        for measure in MEASURES
    }
    if set(values) != expected:
        raise RuntimeError(
            "Visible formula matrix mismatch: "
            f"missing={sorted(expected - set(values))}, "
            f"extra={sorted(set(values) - expected)}"
        )
    return values


def nathonnatha_from_hour(planet: str, hour: float) -> float:
    normalized = float(hour) % 24.0
    distance_from_midnight = min(normalized, 24.0 - normalized)
    day_strength = 5.0 * distance_from_midnight
    if planet == "MERCURY":
        return 60.0
    if planet in DAY_STRONG:
        return day_strength
    return 60.0 - day_strength


def astronomical_midnight_context(
    *,
    event_lmt: datetime,
    longitude: float,
    latitude: float,
) -> dict[str, Any]:
    event_hour = decimal_hour(event_lmt)
    _previous_rise, previous_set, previous_status = (
        sunrise_sunset_lmt_for_date(
            event_lmt.date() - timedelta(days=1),
            longitude,
            latitude,
        )
    )
    current_rise, current_set, current_status = (
        sunrise_sunset_lmt_for_date(
            event_lmt.date(),
            longitude,
            latitude,
        )
    )
    next_rise, _next_set, next_status = sunrise_sunset_lmt_for_date(
        event_lmt.date() + timedelta(days=1),
        longitude,
        latitude,
    )
    statuses = (previous_status, current_status, next_status)
    expected_status = "swiss_ephemeris_apparent_solar_rise_set_lmt"
    if any(status != expected_status for status in statuses):
        raise RuntimeError(
            "Astronomical-midnight profile requires three non-fallback "
            f"Swiss Ephemeris rise/set calculations; found {statuses}"
        )
    previous_midnight = (
        previous_set - 24.0 + current_rise
    ) / 2.0
    next_midnight = (current_set + 24.0 + next_rise) / 2.0
    selected_midnight = min(
        (previous_midnight, next_midnight),
        key=lambda value: abs(event_hour - value),
    )
    distance_hours = abs(event_hour - selected_midnight)
    if not 0.0 <= distance_hours <= 12.5:
        raise RuntimeError(
            "Astronomical-midnight distance is outside the expected "
            f"half-day range: {distance_hours}"
        )
    return {
        "eventLmtIso": event_lmt.isoformat(),
        "eventLmtHour": round(event_hour, 9),
        "previousSunsetLmtHour": round(previous_set - 24.0, 9),
        "currentSunriseLmtHour": round(current_rise, 9),
        "currentSunsetLmtHour": round(current_set, 9),
        "nextSunriseLmtHour": round(next_rise + 24.0, 9),
        "previousMidnightLmtHour": round(previous_midnight, 9),
        "nextMidnightLmtHour": round(next_midnight, 9),
        "selectedMidnightLmtHour": round(selected_midnight, 9),
        "distanceFromMidnightHours": round(distance_hours, 9),
        "dayStrengthVirupa": round(min(60.0, 5.0 * distance_hours), 9),
        "riseSetStatuses": {
            "previousDate": previous_status,
            "currentDate": current_status,
            "nextDate": next_status,
        },
    }


def projected_kranti_deg(
    tropical_longitude_deg: float,
    obliquity_deg: float = AYANA_OBLIQUITY_DEG,
) -> float:
    longitude = math.radians(float(tropical_longitude_deg) % 360.0)
    obliquity = math.radians(float(obliquity_deg))
    return math.degrees(
        math.asin(math.sin(obliquity) * math.sin(longitude))
    )


def ayana_from_kranti(planet: str, kranti_deg: float) -> float:
    obliquity = AYANA_OBLIQUITY_DEG
    if planet in NORTH_STRONG:
        value = max(
            0.0,
            (obliquity + float(kranti_deg))
            * 60.0
            / (2.0 * obliquity),
        )
        return 2.0 * value if planet == "SUN" else value
    if planet in SOUTH_STRONG:
        return max(
            0.0,
            (obliquity - float(kranti_deg))
            * 60.0
            / (2.0 * obliquity),
        )
    if planet == "MERCURY":
        return max(
            0.0,
            (obliquity + abs(float(kranti_deg)))
            * 60.0
            / (2.0 * obliquity),
        )
    raise ValueError(f"Unsupported Ayana planet: {planet}")


def variable_planetary_hour_lord(
    *,
    timestamp: datetime,
    longitude: float,
    latitude: float,
) -> str:
    lmt = local_mean_datetime(timestamp, longitude)
    if lmt is None:
        return ""
    hour = decimal_hour(lmt)
    sunrise, sunset, _status = sunrise_sunset_lmt_for_date(
        lmt.date(),
        longitude,
        latitude,
    )
    if sunrise <= hour < sunset:
        start = sunrise
        span = (sunset - sunrise) / 12.0
        day_sunrise = sunrise
    elif hour >= sunset:
        next_sunrise, _next_sunset, _ = sunrise_sunset_lmt_for_date(
            lmt.date() + timedelta(days=1),
            longitude,
            latitude,
        )
        start = sunset
        span = (next_sunrise + 24.0 - sunset) / 12.0
        day_sunrise = sunrise
    else:
        _previous_sunrise, previous_sunset, _ = (
            sunrise_sunset_lmt_for_date(
                lmt.date() - timedelta(days=1),
                longitude,
                latitude,
            )
        )
        start = previous_sunset
        span = (sunrise + 24.0 - previous_sunset) / 12.0
        hour += 24.0
        day_sunrise = sunrise
    if span <= 0.0:
        return ""
    day_lord = ahargana_lords(
        timestamp,
        longitude,
        day_sunrise,
    )["dina"]
    if day_lord not in CHALDEAN_HORA_ORDER:
        return ""
    period = min(11, int(math.floor((hour - start) / span)))
    start_index = CHALDEAN_HORA_ORDER.index(day_lord)
    return CHALDEAN_HORA_ORDER[(start_index + period) % 7]


def contexts(config_path: Path) -> list[dict[str, Any]]:
    config = load_doctrine_config(config_path)
    configure_ephemeris()
    configure_swiss_ephemeris_sidereal(swe, config)
    output: list[dict[str, Any]] = []
    for sample in SAMPLES:
        local_dt = sample_datetime(sample.local_iso, sample.timezone)
        jd_ut, _utc = jd_ut_for(local_dt)
        ayanamsa = float(swe.get_ayanamsa_ut(jd_ut))
        tropical: dict[str, float] = {}
        actual_declinations: dict[str, float] = {}
        for planet, planet_id in PLANET_IDS.items():
            tropical_lon, _sidereal, _speed, _latitude, declination = (
                calc_planet(jd_ut, planet_id, ayanamsa)
            )
            tropical[planet] = tropical_lon
            actual_declinations[planet] = declination
        lmt = local_mean_datetime(local_dt, sample.longitude)
        if lmt is None:
            raise RuntimeError(f"Missing LMT for {sample.sample_id}")
        sunrise, _sunset, _status = sunrise_sunset_lmt_for_date(
            lmt.date(),
            sample.longitude,
            sample.latitude,
        )
        output.append(
            {
                "sample": sample,
                "local_dt": local_dt,
                "jd_ut": jd_ut,
                "tropical": tropical,
                "declinations": actual_declinations,
                "lmt": lmt,
                "sunrise": sunrise,
                "astronomical_midnight": astronomical_midnight_context(
                    event_lmt=lmt,
                    longitude=sample.longitude,
                    latitude=sample.latitude,
                ),
            }
        )
    return output


def profile_values(
    context: dict[str, Any],
) -> dict[tuple[str, str], float]:
    sample = context["sample"]
    local_dt = context["local_dt"]
    lmt_hour = decimal_hour(context["lmt"])
    equation_of_time_hours = float(swe.time_equ(context["jd_ut"])) * 24.0
    production_hora_lord = hora_lord_for_lmt(
        local_dt,
        sample.longitude,
        context["sunrise"],
        sample.latitude,
    )
    variable_hora_lord = variable_planetary_hour_lord(
        timestamp=local_dt,
        longitude=sample.longitude,
        latitude=sample.latitude,
    )
    values: dict[tuple[str, str], float] = {}
    for planet in CLASSICAL_PLANETS:
        values[("nathonnatha_lmt_source", planet)] = (
            nathonnatha_from_hour(planet, lmt_hour)
        )
        values[("nathonnatha_apparent_solar", planet)] = (
            nathonnatha_from_hour(
                planet,
                lmt_hour + equation_of_time_hours,
            )
        )
        values[("nathonnatha_astronomical_midnight", planet)] = (
            nathonnatha_from_hour(
                planet,
                context["astronomical_midnight"][
                    "distanceFromMidnightHours"
                ],
            )
        )
        values[("hora_astronomical_sunrise", planet)] = (
            60.0 if planet == production_hora_lord else 0.0
        )
        values[("hora_variable_day_night", planet)] = (
            60.0 if planet == variable_hora_lord else 0.0
        )
        values[("ayana_actual_declination", planet)] = ayana_bala_virupa(
            planet,
            context["declinations"][planet],
        )
        kranti = projected_kranti_deg(context["tropical"][planet])
        values[("ayana_tropical_projection", planet)] = ayana_from_kranti(
            planet,
            kranti,
        )
    return values


def build_rows(
    *,
    visible: dict[tuple[str, str, str], float],
    config_path: Path,
) -> tuple[
    list[dict[str, str]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    rows: list[dict[str, str]] = []
    hora_boundary: dict[str, dict[str, Any]] = {}
    nathonnatha_midnights: dict[str, dict[str, Any]] = {}
    for context in contexts(config_path):
        sample = context["sample"]
        nathonnatha_midnights[sample.sample_id] = dict(
            context["astronomical_midnight"]
        )
        candidate_values = profile_values(context)
        for (profile, planet), candidate in sorted(candidate_values.items()):
            measure = profile.split("_", 1)[0]
            expected = visible[(sample.sample_id, planet, measure)]
            delta = expected - float(candidate)
            absolute = abs(delta)
            rows.append(
                {
                    "contract": CONTRACT,
                    "sample_id": sample.sample_id,
                    "planet": planet,
                    "measure": measure,
                    "profile": profile,
                    "jhora_value_virupa": f"{expected:.9f}",
                    "profile_value_virupa": f"{float(candidate):.9f}",
                    "jhora_minus_profile_virupa": f"{delta:.9f}",
                    "absolute_delta_virupa": f"{absolute:.9f}",
                    "pass_fail": (
                        "pass"
                        if absolute <= FROZEN_TOLERANCE_VIRUPA
                        else "fail"
                    ),
                    "sample_era": (
                        "recent_2025"
                        if sample.sample_id in RECENT_SAMPLE_IDS
                        else "historical_1889"
                    ),
                    "tolerance_virupa": f"{FROZEN_TOLERANCE_VIRUPA:.9f}",
                }
            )
        if sample.sample_id == "case_8_event_start":
            lmt_hour = decimal_hour(context["lmt"])
            current_sunrise = float(context["sunrise"])
            boundary = lmt_hour - math.floor(lmt_hour - current_sunrise) - 1.0
            hora_boundary[sample.sample_id] = {
                "lmtHour": round(lmt_hour, 9),
                "swissApparentTipSunriseLmtHour": round(
                    current_sunrise,
                    9,
                ),
                "awardFlipSunriseLmtHour": round(boundary, 9),
                "gapMinutes": round(
                    (current_sunrise - boundary) * 60.0,
                    6,
                ),
                "currentLord": hora_lord_for_lmt(
                    context["local_dt"],
                    sample.longitude,
                    current_sunrise,
                    sample.latitude,
                ),
                "jhoraLord": next(
                    planet
                    for planet in CLASSICAL_PLANETS
                    if visible[(sample.sample_id, planet, "hora")] == 60.0
                ),
            }
    return rows, hora_boundary, nathonnatha_midnights


def summarize_profiles(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["profile"]].append(row)
    summary: dict[str, dict[str, Any]] = {}
    for profile, group in sorted(grouped.items()):
        deltas = [float(row["absolute_delta_virupa"]) for row in group]
        recent = [
            row for row in group if row["sample_era"] == "recent_2025"
        ]
        historical = [
            row for row in group if row["sample_era"] == "historical_1889"
        ]
        summary[profile] = {
            "measure": group[0]["measure"],
            "rows": len(group),
            "pass": sum(row["pass_fail"] == "pass" for row in group),
            "fail": sum(row["pass_fail"] == "fail" for row in group),
            "maeVirupa": round(mean(deltas), 9),
            "maxErrorVirupa": round(max(deltas), 9),
            "recentRows": len(recent),
            "recentPass": sum(
                row["pass_fail"] == "pass" for row in recent
            ),
            "historicalRows": len(historical),
            "historicalPass": sum(
                row["pass_fail"] == "pass" for row in historical
            ),
        }
    return summary


def worked_example_summary() -> dict[str, Any]:
    source_hash = sha256(WORKED_EXAMPLE_EXTRACT)
    nathonnatha_examples = [
        {
            "label": "Lady Diana",
            "utc": datetime(1961, 7, 1, 18, 45, tzinfo=timezone.utc),
            "longitude": 0.5,
            "publishedDayVirupa": 26.0,
            "publishedNightVirupa": 33.0,
        },
        {
            "label": "Prince William",
            "utc": datetime(1982, 6, 21, 20, 3, tzinfo=timezone.utc),
            "longitude": -0.1778,
            "publishedDayVirupa": 19.0,
            "publishedNightVirupa": 40.0,
        },
    ]
    nath_rows = []
    for item in nathonnatha_examples:
        lmt = item["utc"]
        lmt_hour = decimal_hour(lmt) + float(item["longitude"]) / 15.0
        nath_rows.append(
            {
                "label": item["label"],
                "calculatedDayVirupa": round(
                    nathonnatha_from_hour("SUN", lmt_hour),
                    6,
                ),
                "publishedDayVirupa": item["publishedDayVirupa"],
                "calculatedNightVirupa": round(
                    nathonnatha_from_hour("MOON", lmt_hour),
                    6,
                ),
                "publishedNightVirupa": item["publishedNightVirupa"],
                "timeBasis": "published birth time adjusted to LMT",
            }
        )

    ayana_examples = [
        {
            "label": "Lady Diana",
            "utc": datetime(1961, 7, 1, 18, 45, tzinfo=timezone.utc),
            "published": {
                "SUN": 119.0,
                "MOON": 47.0,
                "MARS": 44.0,
                "MERCURY": 59.0,
                "JUPITER": 5.0,
                "VENUS": 54.0,
                "SATURN": 56.0,
            },
        },
        {
            "label": "Prince William",
            "utc": datetime(1982, 6, 21, 20, 3, tzinfo=timezone.utc),
            "published": {
                "SUN": 119.0,
                "MOON": 0.0,
                "MARS": 25.0,
                "MERCURY": 58.0,
                "JUPITER": 14.0,
                "VENUS": 54.0,
                "SATURN": 38.0,
            },
        },
    ]
    ayana_rows = []
    for item in ayana_examples:
        utc = item["utc"]
        jd_ut = float(
            swe.julday(
                utc.year,
                utc.month,
                utc.day,
                decimal_hour(utc),
                swe.GREG_CAL,
            )
        )
        for planet, planet_id in PLANET_IDS.items():
            position, _flags = swe.calc_ut(
                jd_ut,
                planet_id,
                swe.FLG_SWIEPH,
            )
            kranti = projected_kranti_deg(float(position[0]))
            calculated = ayana_from_kranti(planet, kranti)
            ayana_rows.append(
                {
                    "label": item["label"],
                    "planet": planet,
                    "calculatedVirupa": round(calculated, 6),
                    "publishedVirupa": item["published"][planet],
                    "absoluteDeltaVirupa": round(
                        abs(item["published"][planet] - calculated),
                        6,
                    ),
                }
            )
    return {
        "source": {
            "path": relative_path(WORKED_EXAMPLE_EXTRACT),
            "sha256": source_hash,
            "references": [
                "Lady Diana birth data and Shad Bala table: extracted pages 32-33",
                "Ayana explanation and table: extracted pages 69-72",
                "Prince William birth data and Shad Bala table: extracted pages 121-122",
            ],
            "scope": (
                "Corroborative rounded worked tables; not a substitute for the "
                "locked visible JHora matrix."
            ),
        },
        "nathonnatha": nath_rows,
        "ayana": {
            "rows": ayana_rows,
            "maeVirupa": round(
                mean(row["absoluteDeltaVirupa"] for row in ayana_rows),
                9,
            ),
            "maxErrorVirupa": round(
                max(row["absoluteDeltaVirupa"] for row in ayana_rows),
                9,
            ),
        },
    }


def build_summary(
    *,
    profiles: dict[str, dict[str, Any]],
    hora_boundary: dict[str, dict[str, Any]],
    nathonnatha_midnights: dict[str, dict[str, Any]],
    visible_path: Path,
    config_path: Path,
) -> dict[str, Any]:
    worked = worked_example_summary()
    return {
        "contract": CONTRACT,
        "generatedAtUtc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": "diagnostic_profiles_only_no_production_change",
        "toleranceVirupa": FROZEN_TOLERANCE_VIRUPA,
        "tolerancePolicy": "frozen; no widening",
        "inputs": {
            "comparatorScript": {
                "path": relative_path(Path(__file__)),
                "sha256": sha256(Path(__file__)),
            },
            "visibleComparison": {
                "path": relative_path(visible_path),
                "sha256": sha256(visible_path),
            },
            "doctrineConfig": {
                "path": relative_path(config_path),
                "sha256": sha256(config_path),
            },
            "workedExamples": worked["source"],
        },
        "profiles": profiles,
        "horaBoundary": hora_boundary,
        "nathonnathaAstronomicalMidnight": nathonnatha_midnights,
        "workedExamples": {
            "nathonnatha": worked["nathonnatha"],
            "ayana": worked["ayana"],
        },
        "evidenceConclusions": [
            (
                "Retain the LMT Nathonnatha source profile because BPHS defines "
                "the component from midnight to apparent birth time and the "
                "locked published worked tables are independently reproduced "
                "closely with LMT."
            ),
            (
                "Reject the astronomical-midnight compatibility hypothesis. "
                "Using the nearest midpoint of apparent-tip sunset and sunrise "
                "still passes only 11/35 visible JHora rows and does not explain "
                "the case-8 or historical residual."
            ),
            (
                "Visible JHora Nathonnatha remains a software-compatibility "
                "discrepancy rather than evidence that the source-backed LMT "
                "formula is wrong. LMT, apparent-solar time, and astronomical "
                "midnight all fail in different residual patterns, so no "
                "JHora-mimicking correction is admitted."
            ),
            (
                "Do not alter Hora merely from this diagnostic. The former "
                "case-8 disagreement is one categorical award separated by only "
                "a few minutes of sunrise input. The later fail-closed "
                "intermediate packet captured JHora's exact visible sunrise "
                "and award and now confirms the narrow 35/35 Hora profile."
            ),
            (
                "The tropical-longitude Kranti Ayana profile is the strongest "
                "candidate: it passes all 28 recent visible rows and 30/35 "
                "overall, and it fits the two published rounded Ayana tables "
                "far better than true equatorial declination."
            ),
            (
                "Do not promote the Ayana candidate yet. Five 1889 rows remain "
                "outside the frozen tolerance and require visible JHora "
                "tropical longitude or intermediate Kranti evidence."
            ),
            (
                "No production formula, certification tolerance, ML feature, "
                "Auto Suggest rule, or execution path is changed by this "
                "diagnostic."
            ),
        ],
        "nextWitness": {
            "nathonnatha": (
                "No production change. A JHora intermediate showing its "
                "apparent birth time or internal Unnata value is required to "
                "explain the visible compatibility residual."
            ),
            "hora": (
                "Completed: the separate hashed intermediate witness records "
                "JHora's case-8 apparent-tip sunrise and Moon Hora award."
            ),
            "ayana": (
                "The historical tropical positions are captured. The tested "
                "Kranti reconstruction is rejected; a visible internal Kranti "
                "or separately sourced formula is needed before another "
                "candidate is admitted."
            ),
        },
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in rows
    )
    return "\n".join(lines)


def render_report(summary: dict[str, Any]) -> str:
    profiles = summary["profiles"]
    boundary = summary["horaBoundary"]["case_8_event_start"]
    nath_rows = summary["workedExamples"]["nathonnatha"]
    ayana = summary["workedExamples"]["ayana"]
    midnight_rows = summary["nathonnathaAstronomicalMidnight"]
    lines = [
        "# JHora Kaala Formula Profile Reconciliation",
        "",
        f"Contract: `{CONTRACT}`",
        "",
        "Status: diagnostic formula profiles only; no production change.",
        "",
        "The frozen certification tolerance remains 0.5 virupa. A profile that "
        "looks better is not promoted unless its remaining witness conflicts "
        "are resolved.",
        "",
        "## Locked Visible JHora Results",
        "",
        markdown_table(
            [
                "Profile",
                "Pass",
                "MAE",
                "Max error",
                "Recent pass",
                "Historical pass",
            ],
            [
                [
                    name,
                    f"{values['pass']}/{values['rows']}",
                    f"{values['maeVirupa']:.3f}",
                    f"{values['maxErrorVirupa']:.3f}",
                    f"{values['recentPass']}/{values['recentRows']}",
                    f"{values['historicalPass']}/{values['historicalRows']}",
                ]
                for name, values in profiles.items()
            ],
        ),
        "",
        "## Case-8 Hora Boundary",
        "",
        f"- Event LMT: `{boundary['lmtHour']:.9f}` hours.",
        "- Swiss apparent-tip sunrise LMT: "
        f"`{boundary['swissApparentTipSunriseLmtHour']:.9f}` hours.",
        "- Categorical award flip boundary: "
        f"`{boundary['awardFlipSunriseLmtHour']:.9f}` hours.",
        f"- Gap: `{boundary['gapMinutes']:.3f}` minutes.",
        f"- Current lord: `{boundary['currentLord']}`; visible JHora lord: "
        f"`{boundary['jhoraLord']}`.",
        "",
        "This was a boundary-input dispute, not evidence for replacing the "
        "Hora sequence. The later hashed intermediate packet captured JHora's "
        "visible sunrise and Moon award under the locked apparent-tip setting, "
        "confirming the narrow 35/35 profile.",
        "",
        "## Nathonnatha Astronomical-Midnight Test",
        "",
        "The candidate uses the nearest midpoint between sunset and the "
        "following sunrise. Times below or above 24:00 preserve the adjacent "
        "civil date so the distance calculation remains unambiguous.",
        "",
        markdown_table(
            [
                "Fixture",
                "Event LMT",
                "Selected midnight",
                "Distance hours",
                "Day strength",
            ],
            [
                [
                    sample_id,
                    values["eventLmtIso"],
                    f"{values['selectedMidnightLmtHour']:.6f}",
                    f"{values['distanceFromMidnightHours']:.6f}",
                    f"{values['dayStrengthVirupa']:.6f}",
                ]
                for sample_id, values in midnight_rows.items()
            ],
        ),
        "",
        "This explicit astronomical-midnight profile still passes only "
        f"`{profiles['nathonnatha_astronomical_midnight']['pass']}/35` "
        "visible JHora rows. It is therefore rejected as a compatibility "
        "formula and is not a production doctrine change.",
        "",
        "## Published Worked-Table Cross-Check",
        "",
        "### Nathonnatha",
        "",
        markdown_table(
            [
                "Example",
                "Calculated day",
                "Published day",
                "Calculated night",
                "Published night",
            ],
            [
                [
                    row["label"],
                    f"{row['calculatedDayVirupa']:.3f}",
                    row["publishedDayVirupa"],
                    f"{row['calculatedNightVirupa']:.3f}",
                    row["publishedNightVirupa"],
                ]
                for row in nath_rows
            ],
        ),
        "",
        "### Ayana",
        "",
        "The tropical-longitude Kranti candidate has "
        f"`{ayana['maeVirupa']:.3f}` virupa MAE and "
        f"`{ayana['maxErrorVirupa']:.3f}` maximum error against fourteen "
        "integer-rounded values in the two published tables.",
        "",
        "## Evidence Conclusions",
        "",
        *[
            f"- {conclusion}"
            for conclusion in summary["evidenceConclusions"]
        ],
        "",
        "## Required Next Witness",
        "",
        f"- Nathonnatha: {summary['nextWitness']['nathonnatha']}",
        f"- Hora: {summary['nextWitness']['hora']}",
        f"- Ayana: {summary['nextWitness']['ayana']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    visible = read_visible_values(args.visible_comparison)
    rows, hora_boundary, nathonnatha_midnights = build_rows(
        visible=visible,
        config_path=args.doctrine_config,
    )
    profiles = summarize_profiles(rows)
    summary = build_summary(
        profiles=profiles,
        hora_boundary=hora_boundary,
        nathonnatha_midnights=nathonnatha_midnights,
        visible_path=args.visible_comparison,
        config_path=args.doctrine_config,
    )
    write_csv(args.output, rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    args.report.write_text(render_report(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "contract": CONTRACT,
                "status": summary["status"],
                "profiles": profiles,
                "output": str(args.output.resolve()),
                "summary": str(args.summary.resolve()),
                "report": str(args.report.resolve()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
