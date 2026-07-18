from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from doctrine_config import configure_swiss_ephemeris_sidereal, load_doctrine_config
from panchanga_doctrine import panchanga_context
from strict_shadbala_doctrine import CLASSICAL_PLANETS, components_for_body


REPORT_VERSION = (
    "astro_certification_4_gate_v6_named_formula_diagnostics_20260718"
)
IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

PLANETS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MARS": swe.MARS,
    "MERCURY": swe.MERCURY,
    "JUPITER": swe.JUPITER,
    "VENUS": swe.VENUS,
    "SATURN": swe.SATURN,
    "RAHU_TRUE_NODE": swe.TRUE_NODE,
}

@dataclass(frozen=True)
class CertificationSample:
    sample_id: str
    local_iso: str
    timezone: str
    latitude: float
    longitude: float
    location: str


SAMPLES = (
    CertificationSample(
        "case_8_event_start",
        "2025-03-07T19:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    CertificationSample(
        "case_43_event_start",
        "2025-04-04T02:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    CertificationSample(
        "case_103_event_start",
        "2025-05-15T22:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    CertificationSample(
        "case_127_sr_touch_start",
        "2025-05-28T22:00:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    CertificationSample(
        "gann_reference_tokyo",
        "1889-02-11T00:00:00",
        "Asia/Tokyo",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
)

STRENGTH_FEATURE_PREFIXES = (
    "shadbala_implemented_total_virupa.",
    "drik_bala_virupa.",
)
LEGACY_STRENGTH_PLACEHOLDERS = {
    "shadbala_total_virupa_by_classical_planet",
    "drik_bala_virupa_by_classical_planet",
}


@dataclass
class InventoryRow:
    gate: str
    feature_key: str
    source_anchor: str
    implementation: str
    function_or_file: str
    status_label: str
    strict_or_proxy: str
    validation_status: str
    current_gap: str
    next_action: str
    train_policy: str


@dataclass
class PositionRow:
    sample_id: str
    local_time: str
    utc_time: str
    jd_ut: float
    ayanamsa: str
    ayanamsa_deg: float
    planet: str
    tropical_lon_deg: float
    sidereal_lon_deg: float
    speed_deg_day: float
    baseline_status: str


@dataclass
class PanchangaRow:
    sample_id: str
    local_time: str
    sun_sidereal_lon_deg: float
    moon_sidereal_lon_deg: float
    tithi: str
    paksha: str
    nakshatra: str
    pada: str
    yoga: str
    karana: str
    weekday: str
    weekday_lord: str
    validation_status: str


@dataclass
class ExternalTemplateRow:
    gate: str
    sample_id: str
    feature_key: str
    local_value: str
    external_expected_value: str
    external_source: str
    pass_fail: str
    notes: str


@dataclass
class DrikContributionRow:
    sample_id: str
    target: str
    aspector: str
    angle_deg: str
    nature: str
    nature_reason: str
    base_virupa: float
    special_bonus_virupa: float
    gross_virupa: float
    raw_signed_virupa: float
    normalized_signed_virupa: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the four-gate astro/trading certification report.")
    parser.add_argument("--out-dir", default=".", help="Output directory for report and CSV ledgers.")
    parser.add_argument("--date-tag", default="20260718", help="Date tag for output files.")
    parser.add_argument(
        "--external-values",
        default="",
        help=(
            "Optional CSV with external_expected_value/external_source filled. "
            "When omitted, an existing output template for the same date tag is reused if present."
        ),
    )
    parser.add_argument(
        "--independent-drik-values",
        default="",
        help=(
            "Optional independent Jagannatha Hora or worked-example CSV derived from the generated "
            "independent Drik template. PyJHora alone never satisfies this witness."
        ),
    )
    parser.add_argument("--skip-replay", action="store_true", help="Skip reviewer_rule_replay.py execution.")
    parser.add_argument(
        "--legacy-archive-replay",
        action="store_true",
        help="Run replay against quarantined legacy case data for historical comparison only.",
    )
    parser.add_argument(
        "--require-external-pass",
        action="store_true",
        help="Exit non-zero unless Gate 3 is fully externally certified.",
    )
    return parser.parse_args()


def csv_write(path: Path, rows: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def csv_dict_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def external_key(row: dict[str, Any] | ExternalTemplateRow) -> tuple[str, str, str]:
    if isinstance(row, ExternalTemplateRow):
        return row.gate, row.sample_id, row.feature_key
    return row.get("gate", ""), row.get("sample_id", ""), row.get("feature_key", "")


def as_float(value: str) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def tolerance_for(feature_key: str) -> float | None:
    key = feature_key.lower()
    if "lon_deg" in key:
        return 0.02
    if "shadbala" in key or "drik_bala" in key or "virupa" in key:
        return 0.5
    return None


def compare_external_value(feature_key: str, local_value: str, expected_value: str) -> tuple[str, str]:
    expected = str(expected_value).strip()
    local = str(local_value).strip()
    if not expected:
        return "pending", "No external expected value entered."
    if local.startswith("needs "):
        return "pending_manual_context", "Local value requires row-specific event context before comparison."

    local_num = as_float(local)
    expected_num = as_float(expected)
    tol = tolerance_for(feature_key)
    if local_num is not None and expected_num is not None and tol is not None:
        delta = abs(local_num - expected_num)
        status = "pass" if delta <= tol else "fail"
        return status, f"numeric delta={delta:.9f}; tolerance={tol}"

    status = "pass" if local.casefold() == expected.casefold() else "fail"
    return status, "categorical exact compare"


def is_compare_note_fragment(fragment: str) -> bool:
    fragment = fragment.strip()
    return (
        fragment.startswith("numeric delta=")
        or fragment == "categorical exact compare"
        or fragment == "No external expected value entered."
        or fragment == "Local value requires row-specific event context before comparison."
    )


def append_compare_note(notes: str, compare_note: str) -> str:
    parts = [part.strip() for part in str(notes).split(" | ") if part.strip()]
    base_parts = [part for part in parts if not is_compare_note_fragment(part)]
    return " | ".join(base_parts + [compare_note])


def merge_methodology_and_provenance_notes(
    current_notes: str,
    imported_notes: str,
) -> str:
    current_parts = [
        part.strip()
        for part in str(current_notes).split(" | ")
        if part.strip() and not is_compare_note_fragment(part)
    ]
    imported_parts = [
        part.strip()
        for part in str(imported_notes).split(" | ")
        if (
            part.strip()
            and not is_compare_note_fragment(part)
            and not part.strip().startswith("Local strict-v")
            and not part.strip().startswith("Fill expected value")
        )
    ]
    merged: list[str] = []
    for part in current_parts + imported_parts:
        if part not in merged:
            merged.append(part)
    return " | ".join(merged)


def merge_external_values(
    templates: list[ExternalTemplateRow],
    external_rows: list[dict[str, str]],
) -> list[ExternalTemplateRow]:
    external_by_key = {external_key(row): row for row in external_rows}
    merged: list[ExternalTemplateRow] = []
    for row in templates:
        source = external_by_key.get(external_key(row), {})
        expected = source.get("external_expected_value", row.external_expected_value)
        external_source = source.get("external_source", row.external_source)
        notes = merge_methodology_and_provenance_notes(
            row.notes,
            source.get("notes", ""),
        )
        pass_fail, compare_note = compare_external_value(row.feature_key, row.local_value, expected)
        notes = append_compare_note(notes, compare_note)
        merged.append(
            ExternalTemplateRow(
                gate=row.gate,
                sample_id=row.sample_id,
                feature_key=row.feature_key,
                local_value=row.local_value,
                external_expected_value=expected,
                external_source=external_source,
                pass_fail=pass_fail,
                notes=notes,
            )
        )
    return merged


def validate_external_import(
    templates: list[ExternalTemplateRow],
    external_rows: list[dict[str, str]],
) -> list[str]:
    known = {external_key(row) for row in templates}
    seen: set[tuple[str, str, str]] = set()
    issues: list[str] = []
    for row_number, row in enumerate(external_rows, start=2):
        key = external_key(row)
        feature_key = key[2]
        expected = str(row.get("external_expected_value", "")).strip()
        source = str(row.get("external_source", "")).strip()
        if feature_key in LEGACY_STRENGTH_PLACEHOLDERS and not expected:
            continue
        if key in seen:
            issues.append(f"row {row_number}: duplicate external key {key}")
            continue
        seen.add(key)
        if key not in known:
            issues.append(f"row {row_number}: unknown external key {key}")
            continue
        if expected and not source:
            issues.append(f"row {row_number}: expected value has no external source for {key}")
        if feature_key.startswith(STRENGTH_FEATURE_PREFIXES) and expected and as_float(expected) is None:
            issues.append(f"row {row_number}: strength value is not numeric for {key}")
    return issues


def external_gate_summary(
    templates: list[ExternalTemplateRow],
    import_issues: list[str],
    external_values_path: Path,
) -> dict[str, Any]:
    strength_rows = [
        row
        for row in templates
        if row.feature_key.startswith(STRENGTH_FEATURE_PREFIXES)
    ]
    passed = sum(row.pass_fail == "pass" for row in templates)
    failed = sum(row.pass_fail == "fail" for row in templates)
    pending = sum(row.pass_fail.startswith("pending") for row in templates)
    strength_passed = sum(row.pass_fail == "pass" for row in strength_rows)
    strength_failed = sum(row.pass_fail == "fail" for row in strength_rows)
    strength_pending = sum(row.pass_fail.startswith("pending") for row in strength_rows)
    expected_strength_rows = len(SAMPLES) * len(CLASSICAL_PLANETS) * len(STRENGTH_FEATURE_PREFIXES)
    if import_issues:
        status = "blocked_invalid_external_import"
    elif failed:
        status = "failed_external_validation"
    elif pending:
        status = "blocked_pending_external_values"
    elif len(strength_rows) != expected_strength_rows:
        status = "blocked_incomplete_strength_matrix"
    else:
        status = "passed_external_validation"
    source_sha = None
    if external_values_path.exists():
        source_sha = hashlib.sha256(external_values_path.read_bytes()).hexdigest().upper()
    return {
        "contract": "GANN_ASTRO_EXTERNAL_CERTIFICATION_GATE_V1",
        "reportVersion": REPORT_VERSION,
        "generatedAtUtc": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": status,
        "certified": status == "passed_external_validation",
        "executionAllowed": False,
        "rows": {
            "total": len(templates),
            "pass": passed,
            "fail": failed,
            "pending": pending,
        },
        "strengthMatrix": {
            "expectedRows": expected_strength_rows,
            "actualRows": len(strength_rows),
            "pass": strength_passed,
            "fail": strength_failed,
            "pending": strength_pending,
            "classicalPlanets": list(CLASSICAL_PLANETS),
            "measures": list(STRENGTH_FEATURE_PREFIXES),
        },
        "externalImport": {
            "path": str(external_values_path),
            "sha256": source_sha,
            "issues": import_issues,
        },
        "requirements": [
            "Every selected classical-planet Shadbala total must match a saved Tier B export within 0.5 virupa.",
            "Every selected classical-planet Drik Bala value must match a saved Tier B export within 0.5 virupa.",
            "External source settings must record Raman ayanamsa, true node, event time, timezone, and location.",
            "Any missing, duplicate, unknown, non-numeric, or out-of-tolerance row blocks certification.",
        ],
    }


def independent_drik_template(
    templates: list[ExternalTemplateRow],
) -> list[ExternalTemplateRow]:
    return [
        ExternalTemplateRow(
            gate="Gate 3 independent Drik witness",
            sample_id=row.sample_id,
            feature_key=row.feature_key,
            local_value=row.local_value,
            external_expected_value="",
            external_source="",
            pass_fail="pending",
            notes=(
                "Fill from Jagannatha Hora or a cited saved worked example using Raman ayanamsa, "
                "the exact civil time/timezone/location, and the same classical-planet order. "
                "Do not copy values from PyJHora."
            ),
        )
        for row in templates
        if row.feature_key.startswith("drik_bala_virupa.")
    ]


def independent_drik_gate_summary(
    rows: list[ExternalTemplateRow],
    import_issues: list[str],
    values_path: Path | None,
) -> dict[str, Any]:
    expected_rows = len(SAMPLES) * len(CLASSICAL_PLANETS)
    passed = sum(row.pass_fail == "pass" for row in rows)
    failed = sum(row.pass_fail == "fail" for row in rows)
    pending = sum(row.pass_fail.startswith("pending") for row in rows)
    if import_issues:
        status = "blocked_invalid_independent_import"
    elif len(rows) != expected_rows:
        status = "blocked_incomplete_independent_matrix"
    elif failed:
        status = "failed_independent_validation"
    elif pending:
        status = "blocked_pending_independent_values"
    else:
        status = "passed_independent_validation"
    source_sha = None
    if values_path is not None and values_path.exists():
        source_sha = hashlib.sha256(values_path.read_bytes()).hexdigest().upper()
    return {
        "required": True,
        "acceptedSources": [
            "Jagannatha Hora saved export/screenshot with settings",
            "cited independent worked classical example",
        ],
        "status": status,
        "certified": status == "passed_independent_validation",
        "rows": {
            "expected": expected_rows,
            "actual": len(rows),
            "pass": passed,
            "fail": failed,
            "pending": pending,
        },
        "import": {
            "path": str(values_path) if values_path is not None else "",
            "sha256": source_sha,
            "issues": import_issues,
        },
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(value).replace("\n", "<br>") for value in row) + " |")
    return "\n".join(out)


def sample_datetime(value: str, tz_name: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=ZoneInfo(tz_name))


def jd_ut_for(local_dt: datetime) -> tuple[float, datetime]:
    utc = local_dt.astimezone(UTC)
    hour = utc.hour + utc.minute / 60.0 + utc.second / 3600.0 + utc.microsecond / 3_600_000_000.0
    return float(swe.julday(utc.year, utc.month, utc.day, hour)), utc


def calc_planet(jd_ut: float, planet_id: int, ayanamsa_deg: float) -> tuple[float, float, float, float, float]:
    values, _flags = swe.calc_ut(jd_ut, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    equatorial, _equatorial_flags = swe.calc_ut(
        jd_ut,
        planet_id,
        swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL,
    )
    tropical = float(values[0]) % 360.0
    sidereal = (tropical - ayanamsa_deg) % 360.0
    speed = float(values[3]) if len(values) > 3 else 0.0
    latitude = float(values[1]) if len(values) > 1 else float("nan")
    declination = float(equatorial[1]) if len(equatorial) > 1 else float("nan")
    return tropical, sidereal, speed, latitude, declination


def sidereal_house_cusps(jd_ut: float, latitude: float, longitude: float) -> dict[int, float]:
    houses, _ascmc = swe.houses_ex(
        jd_ut,
        float(latitude),
        float(longitude),
        b"O",
        swe.FLG_SIDEREAL,
    )
    return {index + 1: float(cusp) % 360.0 for index, cusp in enumerate(houses)}


def build_inventory(config: dict[str, Any]) -> list[InventoryRow]:
    shadbala = config.get("shadbala", {})
    panchanga = config.get("panchanga", {})
    astronomy = config.get("astronomy", {})
    drik = config.get("drik_bala", {})
    drishti = config.get("drishti", {})
    rule_layer = config.get("rule_layer", {})

    rows = [
        InventoryRow(
            "Gate 1",
            "astronomy.raman_ayanamsa",
            "Swiss Ephemeris SIDM_RAMAN",
            f"{astronomy.get('zodiac')} / {astronomy.get('ayanamsa_swiss_ephemeris_id')}",
            "doctrine_config.configure_swiss_ephemeris_sidereal",
            "implemented_unvalidated",
            "strict astronomy setting",
            "baseline_generated_pending_external_reference",
            "Need independent ephemeris sample cross-check.",
            "Compare Gate 2 rows against Astro.com/JPL/other trusted ephemeris exports.",
            "allow_as_feature_after_external_position_check",
        ),
        InventoryRow(
            "Gate 1",
            "astronomy.true_node_rahu_ketu",
            "Swiss Ephemeris TRUE_NODE; Ketu = Rahu + 180 deg",
            str(astronomy.get("node_type")),
            "build_aspect_sr_touch_log.fetch_planetary_longitude_fast",
            "implemented_unvalidated",
            "strict node position, proxy strength",
            "baseline_generated_pending_external_reference",
            "Rahu/Ketu position is deterministic; strength doctrine remains proxy/excluded from Shadbala.",
            "Validate true-node longitude samples; keep Rahu/Ketu out of classical Shadbala totals.",
            "position_feature_ok_strength_policy_guarded",
        ),
        InventoryRow(
            "Gate 1",
            "shadbala.bphs_component_reconciliation_v7",
            "BPHS chapter 27 source profile + uploaded Shadbala notes + pinned PyJHora diagnostics",
            str(shadbala.get("method")),
            "strict_shadbala_doctrine.event_strict_shadbala_context",
            "implemented_unvalidated",
            "versioned source profile with named comparator variants",
            str(shadbala.get("status")),
            "|".join(shadbala.get("missing", [])),
            "Use end-to-end, Kaala-subcomponent, and shared-input matrices diagnostically; certify remaining Kaala/Chesta/Yuddha variants with a saved JHora or worked-example witness.",
            "train_as_provisional_numeric_feature_only",
        ),
        InventoryRow(
            "Gate 1",
            "shadbala.avg_all_policy",
            "Project doctrine decision",
            str(shadbala.get("doctrine_decisions", {}).get("avg_all_policy")),
            "strict_shadbala_doctrine.aggregate_components",
            "implemented_unvalidated",
            "research aggregation",
            "pending_walk_forward_and_external_component_validation",
            "AVG(ALL) is an artificial seven-classical-planet mean, not a classical graha.",
            "Always label as artificial context feature in ML exports.",
            "train_with_explicit_artificial_feature_label",
        ),
        InventoryRow(
            "Gate 1",
            "drik_bala.reconciled_formula_v2",
            "Parashara six-formula foundation plus PyJHora 4.8.7 reconciliation",
            str(drik.get("method")),
            "strict_shadbala_doctrine.strict_drik_bala_for_planet",
            "tier_b_aligned_pending_independent_validation",
            "versioned reconciled formula",
            str(drik.get("status")),
            "Tier B covers five fixtures; independent Jagannatha Hora or a saved worked example is still required.",
            "Import the prepared independent-source witness without changing the 0.5 virupa tolerance.",
            "train_as_provisional_numeric_feature_only",
        ),
        InventoryRow(
            "Gate 1",
            "drishti.event_orb_strength",
            "Earlier BPHS-like orb heuristic",
            str(drishti.get("method")),
            "build_aspect_sr_touch_log.compute_event_aspect_metrics",
            "proxy_research_feature",
            "proxy",
            str(drishti.get("status")),
            "|".join(drishti.get("missing", [])),
            "Prefer strict Drik/Shadbala fields in explanations; keep orb as timing/proximity only.",
            "do_not_train_as_doctrine_strength",
        ),
        InventoryRow(
            "Gate 1",
            "panchanga.sun_moon_core",
            "Classical Panchanga formulas from sidereal Sun/Moon phase",
            str(panchanga.get("method")),
            "panchanga_doctrine.panchanga_context",
            "implemented_unvalidated",
            "formula foundation",
            str(panchanga.get("status")),
            "|".join(panchanga.get("missing", [])),
            "Compare Gate 2 rows to a traditional Panchanga for timezone/date rollover.",
            "train_as_provisional_categorical_feature",
        ),
        InventoryRow(
            "Gate 1",
            "rule_layer.auto_suggest_sr_gann",
            "Manual review-derived deterministic rules",
            str(rule_layer.get("status")),
            "build_repeatation_review_pack.py + reviewer_rule_replay.py",
            "replay_guarded_partial",
            "trading heuristic",
            "versioned_corrected_golden_replay_passed_5_cases",
            "Python replay is decomposed and golden-tested; browser generation remains a separate implementation and the root legacy archive stays quarantined.",
            "Consolidate browser generation onto the staged engine after a portable corrected-fixture contract exists.",
            "train_rule_lessons_only_until_prospective_gate",
        ),
        InventoryRow(
            "Gate 1",
            "local_llm_dreaming",
            "Local RAG + verifier corrections",
            "extractive/LLM draft explanation layer",
            "jyotish_agent/explain_case.py + dream_review ledgers",
            "do_not_train_raw_text",
            "explanation layer",
            "deterministic_verifier_required",
            "LLM prose can drift and contradict evidence.",
            "Train only from deterministic evidence, manual notes, verifier corrections, and rule lessons.",
            "do_not_train_raw_llm_output",
        ),
    ]
    return rows


def build_position_baseline(
    config: dict[str, Any],
) -> tuple[
    list[PositionRow],
    list[PanchangaRow],
    list[ExternalTemplateRow],
    list[DrikContributionRow],
]:
    ayanamsa_name = configure_swiss_ephemeris_sidereal(swe, config)
    positions: list[PositionRow] = []
    panchanga_rows: list[PanchangaRow] = []
    templates: list[ExternalTemplateRow] = []
    drik_contributions: list[DrikContributionRow] = []

    for sample in SAMPLES:
        sample_id = sample.sample_id
        local_dt = sample_datetime(sample.local_iso, sample.timezone)
        jd_ut, utc_dt = jd_ut_for(local_dt)
        ayanamsa_deg = float(swe.get_ayanamsa_ut(jd_ut))
        sidereal_values: dict[str, float] = {}
        speeds: dict[str, float] = {}
        latitudes: dict[str, float] = {}
        declinations: dict[str, float] = {}
        for planet, planet_id in PLANETS.items():
            tropical, sidereal, speed, latitude, declination = calc_planet(jd_ut, planet_id, ayanamsa_deg)
            sidereal_values[planet] = sidereal
            if planet in CLASSICAL_PLANETS:
                speeds[planet] = speed
                latitudes[planet] = latitude
                declinations[planet] = declination
            positions.append(
                PositionRow(
                    sample_id=sample_id,
                    local_time=local_dt.isoformat(),
                    utc_time=utc_dt.isoformat(),
                    jd_ut=round(jd_ut, 9),
                    ayanamsa=ayanamsa_name,
                    ayanamsa_deg=round(ayanamsa_deg, 9),
                    planet=planet,
                    tropical_lon_deg=round(tropical, 9),
                    sidereal_lon_deg=round(sidereal, 9),
                    speed_deg_day=round(speed, 9),
                    baseline_status="self_consistency_generated_pending_external_reference",
                )
            )
        rahu = sidereal_values.get("RAHU_TRUE_NODE")
        if rahu is not None:
            ketu = (rahu + 180.0) % 360.0
            positions.append(
                PositionRow(
                    sample_id=sample_id,
                    local_time=local_dt.isoformat(),
                    utc_time=utc_dt.isoformat(),
                    jd_ut=round(jd_ut, 9),
                    ayanamsa=ayanamsa_name,
                    ayanamsa_deg=round(ayanamsa_deg, 9),
                    planet="KETU_DERIVED",
                    tropical_lon_deg=float("nan"),
                    sidereal_lon_deg=round(ketu, 9),
                    speed_deg_day=float("nan"),
                    baseline_status="derived_from_true_node_plus_180_pending_external_reference",
                )
            )

        houses = sidereal_house_cusps(jd_ut, sample.latitude, sample.longitude)
        asc_lon = houses.get(1, float("nan"))
        strength_components = {
            planet: components_for_body(
                planet,
                sidereal_values,
                asc_lon,
                houses,
                local_dt,
                sample.longitude,
                speeds,
                latitudes,
                declinations,
                sample.latitude,
            )
            for planet in CLASSICAL_PLANETS
        }
        for target, components in strength_components.items():
            for contribution in components.get("drik_aspects", []):
                drik_contributions.append(
                    DrikContributionRow(
                        sample_id=sample_id,
                        target=target,
                        aspector=str(contribution.get("aspector") or ""),
                        angle_deg=(
                            ""
                            if contribution.get("angle_deg") is None
                            else f"{float(contribution['angle_deg']):.2f}"
                        ),
                        nature=str(contribution.get("nature") or ""),
                        nature_reason=str(contribution.get("nature_reason") or ""),
                        base_virupa=float(contribution.get("base_virupa") or 0.0),
                        special_bonus_virupa=float(
                            contribution.get("special_bonus_virupa") or 0.0
                        ),
                        gross_virupa=float(contribution.get("gross_virupa") or 0.0),
                        raw_signed_virupa=float(
                            contribution.get("raw_signed_virupa") or 0.0
                        ),
                        normalized_signed_virupa=float(
                            contribution.get("normalized_signed_virupa") or 0.0
                        ),
                    )
                )

        panchanga = panchanga_context("cert", local_dt, sidereal_values["SUN"], sidereal_values["MOON"])
        panchanga_rows.append(
            PanchangaRow(
                sample_id=sample_id,
                local_time=local_dt.isoformat(),
                sun_sidereal_lon_deg=round(sidereal_values["SUN"], 9),
                moon_sidereal_lon_deg=round(sidereal_values["MOON"], 9),
                tithi=str(panchanga.get("cert_tithi_name", "")),
                paksha=str(panchanga.get("cert_paksha", "")),
                nakshatra=str(panchanga.get("cert_moon_nakshatra", "")),
                pada=str(panchanga.get("cert_moon_pada", "")),
                yoga=str(panchanga.get("cert_yoga_name", "")),
                karana=str(panchanga.get("cert_karana_name", "")),
                weekday=str(panchanga.get("cert_weekday", "")),
                weekday_lord=str(panchanga.get("cert_weekday_lord", "")),
                validation_status="local_formula_baseline_pending_traditional_panchanga_check",
            )
        )

        for feature_key, local_value in [
            ("sun_sidereal_lon_deg", f"{sidereal_values['SUN']:.9f}"),
            ("moon_sidereal_lon_deg", f"{sidereal_values['MOON']:.9f}"),
            ("rahu_true_node_sidereal_lon_deg", f"{sidereal_values['RAHU_TRUE_NODE']:.9f}"),
            ("tithi_name", str(panchanga.get("cert_tithi_name", ""))),
            ("moon_nakshatra_pada", f"{panchanga.get('cert_moon_nakshatra', '')} {panchanga.get('cert_moon_pada', '')}"),
        ]:
            templates.append(
                ExternalTemplateRow(
                    gate="Gate 3",
                    sample_id=sample_id,
                    feature_key=feature_key,
                    local_value=local_value,
                    external_expected_value="",
                    external_source="",
                    pass_fail="pending",
                    notes="Fill expected value from trusted ephemeris/Panchanga/Shadbala source, then rerun certification.",
                )
            )
        for planet in CLASSICAL_PLANETS:
            components = strength_components[planet]
            for feature_key, component_key in (
                (f"shadbala_implemented_total_virupa.{planet}", "implemented_total_virupa"),
                (f"drik_bala_virupa.{planet}", "drik_virupa"),
            ):
                local_value = components.get(component_key)
                if local_value is None or not math.isfinite(float(local_value)):
                    raise ValueError(f"{sample_id} {feature_key} did not produce a finite local value")
                templates.append(
                    ExternalTemplateRow(
                        gate="Gate 3",
                        sample_id=sample_id,
                        feature_key=feature_key,
                        local_value=f"{float(local_value):.9f}",
                        external_expected_value="",
                        external_source="",
                        pass_fail="pending",
                        notes=(
                            f"Local strict-v6 BPHS source-profile value at {sample.location}; Raman "
                            "ayanamsa; true node; Porphyry houses. Sthana uses degree-bounded D1 "
                            "Moolatrikona and source weights; Kaala uses astronomical sunrise and the "
                            "published Ahargana scheme; Chesta keeps motion state diagnostic separate; "
                            "Yuddha candidates fail closed. Drik V2 uses a divide-by-four contribution "
                            "ledger, dynamic Moon/Mercury nature, and range-based special aspects. Fill "
                            "a planet-matched independent JHora export value and saved evidence path."
                        ),
                    )
                )

    return positions, panchanga_rows, templates, drik_contributions


def run_replay(skip: bool, legacy_archive_replay: bool) -> tuple[str, str]:
    if skip:
        return "skipped", "reviewer replay skipped by CLI flag"
    if not legacy_archive_replay:
        return (
            "blocked_legacy_dataset",
            "Trading replay is intentionally blocked: current case records use the quarantined "
            "legacy astronomy contract. Rebuild versioned corrected fixtures before certifying Gate 4. "
            "Use --legacy-archive-replay only for historical comparison.",
        )
    cmd = ["python", "reviewer_rule_replay.py"]
    try:
        proc = subprocess.run(cmd, cwd=Path(__file__).parent, text=True, capture_output=True, check=False)
    except Exception as exc:
        return "error", f"Could not run {' '.join(cmd)}: {exc}"
    status = "passed" if proc.returncode == 0 else "failed"
    text = (proc.stdout + "\n" + proc.stderr).strip()
    return status, text


def render_report(
    path: Path,
    inventory: list[InventoryRow],
    positions: list[PositionRow],
    panchanga_rows: list[PanchangaRow],
    templates: list[ExternalTemplateRow],
    external_gate: dict[str, Any],
    replay_status: str,
    replay_output: str,
    output_files: dict[str, Path],
) -> None:
    gate_counts: dict[str, int] = {}
    for row in inventory:
        gate_counts[row.status_label] = gate_counts.get(row.status_label, 0) + 1

    position_preview = [
        [
            row.sample_id,
            row.planet,
            row.local_time,
            row.ayanamsa,
            row.ayanamsa_deg,
            row.sidereal_lon_deg,
            row.baseline_status,
        ]
        for row in positions
        if row.planet in {"SUN", "MOON", "RAHU_TRUE_NODE", "KETU_DERIVED"}
    ][:20]

    panchanga_preview = [
        [row.sample_id, row.tithi, row.paksha, row.nakshatra, row.pada, row.yoga, row.karana, row.validation_status]
        for row in panchanga_rows
    ]

    inventory_preview = [
        [row.feature_key, row.status_label, row.strict_or_proxy, row.validation_status, row.train_policy]
        for row in inventory
    ]

    pending_external = sum(1 for row in templates if row.pass_fail.startswith("pending"))
    passed_external = sum(1 for row in templates if row.pass_fail == "pass")
    failed_external = sum(1 for row in templates if row.pass_fail == "fail")
    drik_rows = [
        row for row in templates if row.feature_key.startswith("drik_bala_virupa.")
    ]
    drik_passed = sum(row.pass_fail == "pass" for row in drik_rows)
    drik_failed = sum(row.pass_fail == "fail" for row in drik_rows)
    independent_drik = dict(external_gate.get("independentDrikWitness") or {})
    if external_gate["certified"]:
        external_verdict = (
            "- Shadbala/Drik external certification passed for the declared matrix."
        )
    elif external_gate["status"] == "failed_external_validation":
        external_verdict = (
            f"- Tier B Drik comparison is {drik_passed} pass / {drik_failed} fail. The "
            "end-to-end component diagnostic is 145 pass / 55 fail / 10 structural "
            "N/A: Dig 35/35, Drik 35/35, Naisargika 35/35, Sthana 34/35, "
            "comparable Chesta 6/25, and Kaala 0/35. Shared-input formulas pass "
            "60/60 comparable rows: Sthana 35/35 and Mars-Saturn Chesta 25/25. The "
            "35 full-total rows still fail against the alternate PyJHora Kaala/Chesta "
            "profile. Keep full Shadbala provisional and require the independent JHora "
            "or cited worked-example witness before certification."
        )
    else:
        external_verdict = (
            "- Do not treat Shadbala/Drik as externally certified; the machine gate "
            "is waiting for complete accepted evidence."
        )
    lines = [
        "# Astro Function Certification 4-Gate Report",
        "",
        f"- Report version: `{REPORT_VERSION}`",
        f"- Generated: `{datetime.now(IST).isoformat(timespec='seconds')}`",
        "- Important interpretation: this report certifies traceability and local reproducibility first. Pending and failed external checks remain explicit and fail closed.",
        "",
        "## Gate Summary",
        "",
        markdown_table(
            ["Gate", "Result"],
            [
                ["Gate 1 - Formula inventory", f"{len(inventory)} feature rows inventoried"],
                ["Gate 2 - Astronomical baseline", f"{len(positions)} planet/node rows generated with Raman ayanamsa"],
                [
                    "Gate 3 - External validation",
                    (
                        f"{external_gate['status']}: "
                        f"{passed_external} pass / {failed_external} fail / {pending_external} pending"
                    ),
                ],
                ["Gate 4 - Trading replay", replay_status],
            ],
        ),
        "",
        "## Certification Labels",
        "",
        markdown_table(["Label", "Count"], [[key, value] for key, value in sorted(gate_counts.items())]),
        "",
        "## Gate 1 - Inventory Preview",
        "",
        markdown_table(["Feature", "Status", "Strict/Proxy", "Validation", "Training Policy"], inventory_preview),
        "",
        "## Gate 2 - Position Baseline Preview",
        "",
        markdown_table(
            ["Sample", "Planet", "Local Time", "Ayanamsa", "Ayanamsa Deg", "Sidereal Lon Deg", "Status"],
            position_preview,
        ),
        "",
        "## Gate 2 - Panchanga Baseline Preview",
        "",
        markdown_table(
            ["Sample", "Tithi", "Paksha", "Moon Nakshatra", "Pada", "Yoga", "Karana", "Status"],
            panchanga_preview,
        ),
        "",
        "## Gate 3 - External Validation",
        "",
        "Fill the expected-value columns from trusted ephemeris, Panchanga, and Shadbala examples. On each run, the script preserves those entries and computes pass/fail where a direct comparison is possible.",
        "",
        f"Gate status: `{external_gate['status']}`",
        "",
        markdown_table(
            ["Status", "Rows"],
            [["pass", passed_external], ["fail", failed_external], ["pending", pending_external]],
        ),
        "",
        markdown_table(
            ["Strength matrix", "Rows"],
            [
                ["expected", external_gate["strengthMatrix"]["expectedRows"]],
                ["actual", external_gate["strengthMatrix"]["actualRows"]],
                ["pass", external_gate["strengthMatrix"]["pass"]],
                ["fail", external_gate["strengthMatrix"]["fail"]],
                ["pending", external_gate["strengthMatrix"]["pending"]],
            ],
        ),
        "",
        markdown_table(
            ["Drik validation layer", "Status"],
            [
                [
                    "Tier B PyJHora comparator",
                    f"{drik_passed} pass / {drik_failed} fail",
                ],
                [
                    "Independent JHora/worked-example witness",
                    independent_drik.get("status", "not generated"),
                ],
            ],
        ),
        "",
        "External import issues:",
        "",
        *(
            [f"- {issue}" for issue in external_gate["externalImport"]["issues"]]
            or ["- none"]
        ),
        "",
        "## Gate 4 - Trading Replay",
        "",
        f"Status: `{replay_status}`",
        "",
        "```text",
        replay_output[-4000:] if replay_output else "",
        "```",
        "",
        "## Output Files",
        "",
        markdown_table(["Artifact", "Path"], [[name, str(file_path)] for name, file_path in output_files.items()]),
        "",
        "## Current Verdict",
        "",
        "- Safe to continue astronomy/doctrine inspection with these labels visible.",
        external_verdict,
        "- Do not train on raw local LLM prose. Train on deterministic evidence, manual notes, verified rule lessons, and verifier corrections.",
        "- Gate 4 is blocked until corrected versioned data replaces the legacy double-sidereal case records.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(__file__).parent
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    config = load_doctrine_config(root / "doctrine_config.yaml")
    inventory = build_inventory(config)
    positions, panchanga_rows, templates, drik_contributions = build_position_baseline(
        config
    )
    independent_drik_rows = independent_drik_template(templates)
    replay_status, replay_output = run_replay(args.skip_replay, args.legacy_archive_replay)

    inventory_path = out_dir / f"astro_function_certification_inventory_{args.date_tag}.csv"
    positions_path = out_dir / f"astro_position_baseline_{args.date_tag}.csv"
    panchanga_path = out_dir / f"panchanga_baseline_{args.date_tag}.csv"
    drik_contribution_path = out_dir / f"drik_contribution_ledger_{args.date_tag}.csv"
    template_path = out_dir / f"astro_external_validation_template_{args.date_tag}.csv"
    independent_drik_template_path = (
        out_dir / f"jhora_drik_independent_validation_template_{args.date_tag}.csv"
    )
    external_gate_path = out_dir / f"astro_external_validation_gate_{args.date_tag}.json"
    replay_path = out_dir / f"trading_rule_replay_result_{args.date_tag}.json"
    report_path = out_dir / f"astro_function_certification_report_{args.date_tag}.md"

    external_values_path = Path(args.external_values) if args.external_values else template_path
    if external_values_path and not external_values_path.is_absolute():
        external_values_path = root / external_values_path
    external_rows = csv_dict_rows(external_values_path)
    external_import_issues = validate_external_import(templates, external_rows)
    templates = merge_external_values(templates, external_rows)
    external_gate = external_gate_summary(
        templates,
        external_import_issues,
        external_values_path,
    )
    independent_values_path: Path | None = None
    independent_external_rows: list[dict[str, str]] = []
    if args.independent_drik_values:
        independent_values_path = Path(args.independent_drik_values)
        if not independent_values_path.is_absolute():
            independent_values_path = root / independent_values_path
        independent_external_rows = csv_dict_rows(independent_values_path)
    independent_import_issues = validate_external_import(
        independent_drik_rows,
        independent_external_rows,
    )
    independent_drik_rows = merge_external_values(
        independent_drik_rows,
        independent_external_rows,
    )
    independent_gate = independent_drik_gate_summary(
        independent_drik_rows,
        independent_import_issues,
        independent_values_path,
    )
    external_gate["independentDrikWitness"] = independent_gate
    external_gate["requirements"].append(
        "PyJHora is a Tier B comparator only; independent Jagannatha Hora or cited worked-example "
        "Drik evidence must also pass before certification."
    )
    if external_gate["certified"] and not independent_gate["certified"]:
        external_gate["status"] = "blocked_pending_independent_drik_validation"
    external_gate["certified"] = bool(
        external_gate["certified"] and independent_gate["certified"]
    )

    csv_write(inventory_path, inventory)
    csv_write(positions_path, positions)
    csv_write(panchanga_path, panchanga_rows)
    csv_write(drik_contribution_path, drik_contributions)
    csv_write(template_path, templates)
    csv_write(independent_drik_template_path, independent_drik_rows)
    external_gate_path.write_text(
        json.dumps(external_gate, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    replay_path.write_text(
        json.dumps(
            {
                "report_version": REPORT_VERSION,
                "generated_at": datetime.now(IST).isoformat(timespec="seconds"),
                "status": replay_status,
                "output": replay_output,
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )
    render_report(
        report_path,
        inventory,
        positions,
        panchanga_rows,
        templates,
        external_gate,
        replay_status,
        replay_output,
        {
            "inventory_csv": inventory_path,
            "position_baseline_csv": positions_path,
            "panchanga_baseline_csv": panchanga_path,
            "drik_contribution_ledger_csv": drik_contribution_path,
            "external_validation_template_csv": template_path,
            "independent_drik_validation_template_csv": independent_drik_template_path,
            "external_validation_gate_json": external_gate_path,
            "trading_rule_replay_json": replay_path,
            "report_md": report_path,
        },
    )
    print(f"Wrote {report_path}")
    print(f"Gate 3 external validation: {external_gate['status']}")
    print(f"Gate 4 replay: {replay_status}")
    if args.require_external_pass and not external_gate["certified"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
