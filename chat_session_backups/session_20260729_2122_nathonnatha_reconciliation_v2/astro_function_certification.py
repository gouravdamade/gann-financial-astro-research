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
    "astro_certification_4_gate_v14_visible_sthana_packet_20260729"
)
KAALA_CAPTURE_ASSISTANT_CONTRACT = "GANN_JHORA_KAALA_CAPTURE_ASSISTANT_V1"
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
    parser.add_argument("--date-tag", default="20260729", help="Date tag for output files.")
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
    parser.add_argument(
        "--jhora-kaala-summary",
        default=(
            "status/evidence/jhora_kaala_witness_20260727/"
            "jhora_kaala_profile_comparison_20260727.json"
        ),
        help=(
            "Locked visible JHora Kaala comparison summary. The report promotes "
            "only explicitly supported subcomponents and keeps aggregate Kaala "
            "fail closed."
        ),
    )
    parser.add_argument(
        "--jhora-sthana-summary",
        default=(
            "status/evidence/jhora_sthana_subcomponents_20260729/"
            "jhora_sthana_subcomponent_profile_comparison_20260729.json"
        ),
        help=(
            "Locked visible JHora Sthana subcomponent comparison. It may "
            "admit individual compatibility findings but never silently "
            "replace the production source profile."
        ),
    )
    parser.add_argument(
        "--jhora-kaala-formula-summary",
        default=(
            "status/evidence/jhora_kaala_witness_20260727/"
            "jhora_kaala_formula_profiles_20260729.json"
        ),
        help=(
            "Diagnostic Hora, Nathonnatha, and Ayana formula-profile comparison. "
            "This evidence documents candidates and blockers only; it never "
            "promotes a production formula."
        ),
    )
    parser.add_argument(
        "--jhora-hora-intermediate-witness",
        default=(
            "status/evidence/jhora_kaala_intermediate_20260729/"
            "jhora_hora_boundary_witness_completed.csv"
        ),
        help=(
            "Completed visible case-8 JHora sunrise and Hora-award witness. "
            "A missing or invalid packet keeps the machine gate blocked."
        ),
    )
    parser.add_argument(
        "--jhora-ayana-intermediate-witness",
        default=(
            "status/evidence/jhora_kaala_intermediate_20260729/"
            "jhora_ayana_intermediate_witness_completed.csv"
        ),
        help=(
            "Completed visible historical JHora tropical-longitude or Kranti "
            "witness. A missing or invalid packet keeps the machine gate blocked."
        ),
    )
    parser.add_argument(
        "--jhora-kaala-visible-values",
        default=(
            "status/evidence/jhora_kaala_witness_20260727/"
            "jhora_kaala_profile_comparison_20260727.csv"
        ),
        help="Locked visible JHora Kaala comparison used to bind intermediates.",
    )
    parser.add_argument(
        "--jhora-shadbala-reconciliation",
        default=(
            "status/evidence/jhora_shadbala_20260723/"
            "jhora_doctrine_reconciliation_20260726.json"
        ),
        help=(
            "Locked local-versus-JHora reconciliation summary. The report admits "
            "only components that pass every locked row at the frozen tolerance."
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


def visible_kaala_gate_summary(summary_path: Path) -> dict[str, Any]:
    source_sha = None
    if summary_path.exists():
        source_sha = hashlib.sha256(summary_path.read_bytes()).hexdigest().upper()
    base = {
        "required": True,
        "status": "blocked_missing_visible_kaala_witness",
        "certified": False,
        "aggregateKaalaCertified": False,
        "promotedComponents": [],
        "retainedValidatedComponents": [],
        "provisionalComponents": [
            "hora",
            "nathonnatha",
            "ayana",
            "total",
        ],
        "input": {
            "path": str(summary_path),
            "sha256": source_sha,
            "issues": [],
        },
    }
    if not summary_path.exists():
        base["input"]["issues"].append("visible Kaala witness summary is missing")
        return base
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        base["status"] = "blocked_invalid_visible_kaala_witness"
        base["input"]["issues"].append(f"cannot read visible Kaala witness: {exc}")
        return base

    components = dict(payload.get("components") or {})
    expected_rows = len(SAMPLES) * len(CLASSICAL_PLANETS)
    required = (
        "abda",
        "masa",
        "vara",
        "tribhaga",
        "yuddha",
        "paksha",
        "hora",
        "nathonnatha",
        "ayana",
        "total",
    )
    missing = sorted(set(required).difference(components))
    comparison_rows = int(payload.get("comparisonRows") or 0)
    if missing:
        base["input"]["issues"].append(
            "missing Kaala components: " + ", ".join(missing)
        )
    if comparison_rows != expected_rows * len(required):
        base["input"]["issues"].append(
            f"expected {expected_rows * len(required)} comparison rows; "
            f"found {comparison_rows}"
        )
    if base["input"]["issues"]:
        base["status"] = "blocked_incomplete_visible_kaala_witness"
        return base

    retained = ("abda", "masa", "vara", "tribhaga", "yuddha")
    retained_ok = all(
        int(components[name].get("rows") or 0) == expected_rows
        and int(components[name].get("localPass") or 0) == expected_rows
        for name in retained
    )
    paksha = dict(components["paksha"])
    paksha_max = paksha.get("localMaxVirupa")
    paksha_ok = (
        int(paksha.get("rows") or 0) == expected_rows
        and int(paksha.get("localPass") or 0) == expected_rows
        and paksha_max is not None
        and float(paksha_max) <= 0.5
    )
    base.update(
        {
            "status": (
                "partial_component_validation"
                if retained_ok and paksha_ok
                else "failed_visible_kaala_component_validation"
            ),
            "witnessRows": int(payload.get("witnessRows") or 0),
            "comparisonRows": comparison_rows,
            "toleranceVirupa": float(payload.get("toleranceVirupa") or 0.5),
            "promotedComponents": ["paksha"] if paksha_ok else [],
            "retainedValidatedComponents": list(retained) if retained_ok else [],
            "provisionalComponents": [
                name
                for name in ("hora", "nathonnatha", "ayana", "total")
                if int(components[name].get("localPass") or 0) < expected_rows
            ],
            "components": {
                name: {
                    "rows": int(components[name].get("rows") or 0),
                    "localPass": int(components[name].get("localPass") or 0),
                    "localMaeVirupa": float(
                        components[name].get("localMaeVirupa") or 0.0
                    ),
                    "localMaxVirupa": float(
                        components[name].get("localMaxVirupa") or 0.0
                    ),
                }
                for name in required
            },
        }
    )
    return base


def visible_sthana_gate_summary(summary_path: Path) -> dict[str, Any]:
    source_sha = None
    if summary_path.exists():
        source_sha = hashlib.sha256(summary_path.read_bytes()).hexdigest().upper()
    base = {
        "required": True,
        "status": "blocked_missing_visible_sthana_witness",
        "independentWitnessComplete": False,
        "compatibilityAligned": False,
        "sourceCertified": False,
        "financiallyValidated": False,
        "productionChangeAllowed": False,
        "executionAllowed": False,
        "sourceAlignedComponents": [],
        "sourceDivergentComponents": [],
        "input": {
            "path": str(summary_path),
            "sha256": source_sha,
            "issues": [],
        },
    }
    if not summary_path.exists():
        base["input"]["issues"].append(
            "visible Sthana witness summary is missing"
        )
        return base
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        base["status"] = "blocked_invalid_visible_sthana_witness"
        base["input"]["issues"].append(
            f"cannot read visible Sthana witness: {exc}"
        )
        return base

    expected_contract = "GANN_JHORA_STHANA_SUBCOMPONENT_COMPARATOR_V1"
    if payload.get("contract") != expected_contract:
        base["input"]["issues"].append(
            f"expected contract {expected_contract}; "
            f"found {payload.get('contract')!r}"
        )
    expected_status = "visible_witness_reconciled_diagnostic_only"
    if payload.get("status") != expected_status:
        base["input"]["issues"].append(
            f"expected status {expected_status}; "
            f"found {payload.get('status')!r}"
        )
    expected_witness_contract = (
        "GANN_JHORA_STHANA_SUBCOMPONENT_WITNESS_V1"
    )
    if payload.get("witnessContract") != expected_witness_contract:
        base["input"]["issues"].append(
            f"expected witness contract {expected_witness_contract}; "
            f"found {payload.get('witnessContract')!r}"
        )
    tolerance = payload.get("toleranceVirupa")
    if tolerance is None or not math.isclose(
        float(tolerance), 0.5, rel_tol=0.0, abs_tol=1e-12
    ):
        base["input"]["issues"].append(
            f"expected frozen 0.5-virupa tolerance; found {tolerance!r}"
        )
    if payload.get("tolerancePolicy") != "frozen; no widening":
        base["input"]["issues"].append(
            "visible Sthana tolerance policy is not frozen"
        )
    expected_production_profile = "bphs_ch27_source"
    if payload.get("productionProfile") != expected_production_profile:
        base["input"]["issues"].append(
            f"expected production profile {expected_production_profile}; "
            f"found {payload.get('productionProfile')!r}"
        )
    for flag in (
        "productionChangeAllowed",
        "sourceCertified",
        "financiallyValidated",
        "executionAllowed",
    ):
        if payload.get(flag) is not False:
            base["input"]["issues"].append(
                f"{flag} must remain explicitly false"
            )

    locked_inputs: dict[str, dict[str, Any]] = {}
    raw_inputs = dict(payload.get("inputs") or {})
    for input_name in ("witness", "topLevelWitness", "doctrineConfig"):
        metadata = dict(raw_inputs.get(input_name) or {})
        raw_path = str(metadata.get("path") or "").strip()
        expected_sha = str(metadata.get("sha256") or "").strip().upper()
        locked_input = {
            "path": raw_path,
            "expectedSha256": expected_sha or None,
            "actualSha256": None,
        }
        locked_inputs[input_name] = locked_input
        if not raw_path or not expected_sha:
            base["input"]["issues"].append(
                f"{input_name} locked input path/hash is missing"
            )
            continue
        input_path = Path(raw_path)
        if not input_path.is_absolute():
            input_path = summary_path.parent / input_path
        locked_input["path"] = str(input_path)
        if not input_path.exists() or not input_path.is_file():
            base["input"]["issues"].append(
                f"{input_name} locked input is missing: {input_path}"
            )
            continue
        actual_sha = hashlib.sha256(input_path.read_bytes()).hexdigest().upper()
        locked_input["actualSha256"] = actual_sha
        if actual_sha != expected_sha:
            base["input"]["issues"].append(
                f"{input_name} locked input SHA-256 mismatch"
            )
    base["lockedInputs"] = locked_inputs

    expected_rows = len(SAMPLES) * len(CLASSICAL_PLANETS)
    expected_comparison_rows = expected_rows * 5
    if int(payload.get("witnessRows") or 0) != expected_comparison_rows:
        base["input"]["issues"].append(
            f"expected {expected_comparison_rows} visible witness rows"
        )
    if int(payload.get("comparisonRows") or 0) != expected_comparison_rows:
        base["input"]["issues"].append(
            f"expected {expected_comparison_rows} comparison rows"
        )

    components = {
        "uchcha",
        "saptavargaja",
        "ojayugma",
        "kendradi",
        "drekkana",
    }
    raw_profiles = dict(payload.get("profiles") or {})
    expected_profile_ids = {
        "source": "bphs_ch27_source",
        "pyjhora": "pyjhora_4_8_7_compatibility",
        "jhora_visible": "jhora_8_visible_compatibility",
    }
    expected_profiles = set(expected_profile_ids)
    missing_profiles = sorted(expected_profiles.difference(raw_profiles))
    if missing_profiles:
        base["input"]["issues"].append(
            "missing Sthana profiles: " + ", ".join(missing_profiles)
        )
    normalized_profiles: dict[str, dict[str, Any]] = {}
    for profile_name in sorted(expected_profiles):
        profile = dict(raw_profiles.get(profile_name) or {})
        if not profile:
            continue
        if profile.get("profileId") != expected_profile_ids[profile_name]:
            base["input"]["issues"].append(
                f"{profile_name} profile id must be "
                f"{expected_profile_ids[profile_name]}"
            )
        raw_components = dict(profile.get("components") or {})
        missing_components = sorted(components.difference(raw_components))
        if missing_components:
            base["input"]["issues"].append(
                f"{profile_name} missing components: "
                + ", ".join(missing_components)
            )
        normalized_components: dict[str, dict[str, Any]] = {}
        for component in sorted(components):
            values = dict(raw_components.get(component) or {})
            if not values:
                continue
            rows = int(values.get("rows") or 0)
            passed = int(values.get("pass") or 0)
            failed = int(values.get("fail") or 0)
            if rows != expected_rows or passed + failed != rows:
                base["input"]["issues"].append(
                    f"{profile_name}/{component} must contain "
                    f"{expected_rows} complete pass/fail rows"
                )
            normalized_components[component] = {
                "rows": rows,
                "pass": passed,
                "fail": failed,
                "maeVirupa": float(values.get("maeVirupa") or 0.0),
                "maxErrorVirupa": float(
                    values.get("maxErrorVirupa") or 0.0
                ),
            }
        total = dict(profile.get("total") or {})
        total_rows = int(total.get("rows") or 0)
        total_passed = int(total.get("pass") or 0)
        total_failed = int(total.get("fail") or 0)
        if (
            total_rows != expected_rows
            or total_passed + total_failed != total_rows
        ):
            base["input"]["issues"].append(
                f"{profile_name}/total must contain "
                f"{expected_rows} complete pass/fail rows"
            )
        normalized_profiles[profile_name] = {
            "profileId": str(profile.get("profileId") or ""),
            "components": normalized_components,
            "total": {
                "rows": total_rows,
                "pass": total_passed,
                "fail": total_failed,
                "maeVirupa": float(total.get("maeVirupa") or 0.0),
                "maxErrorVirupa": float(
                    total.get("maxErrorVirupa") or 0.0
                ),
            },
        }

    if base["input"]["issues"]:
        base["status"] = "blocked_incomplete_visible_sthana_witness"
        base["profiles"] = normalized_profiles
        return base

    visible = normalized_profiles["jhora_visible"]
    compatibility_aligned = all(
        values["pass"] == expected_rows
        and values["maxErrorVirupa"] <= 0.5
        for values in visible["components"].values()
    ) and (
        visible["total"]["pass"] == expected_rows
        and visible["total"]["maxErrorVirupa"] <= 0.5
    )
    source_components = normalized_profiles["source"]["components"]
    source_aligned = sorted(
        name
        for name, values in source_components.items()
        if values["pass"] == expected_rows
        and values["maxErrorVirupa"] <= 0.5
    )
    base.update(
        {
            "status": (
                "visible_component_matrix_aligned_diagnostic_only"
                if compatibility_aligned
                else "failed_visible_sthana_component_validation"
            ),
            "independentWitnessComplete": True,
            "compatibilityAligned": compatibility_aligned,
            "witnessRows": int(payload["witnessRows"]),
            "comparisonRows": int(payload["comparisonRows"]),
            "toleranceVirupa": float(tolerance),
            "productionProfile": str(
                payload.get("productionProfile") or ""
            ),
            "jhoraCompatibleProfile": visible["profileId"],
            "sourceAlignedComponents": source_aligned,
            "sourceDivergentComponents": sorted(
                components.difference(source_aligned)
            ),
            "profiles": normalized_profiles,
            "evidenceConclusions": list(
                payload.get("evidenceConclusions") or []
            ),
        }
    )
    return base


def kaala_capture_assistant_summary(root: Path) -> dict[str, Any]:
    script = root / "jhora_kaala_capture_assistant.py"
    launcher = root / "Launch_JHora_Kaala_Capture_Assistant.cmd"

    def descriptor(path: Path) -> dict[str, Any]:
        return {
            "path": str(path),
            "available": path.is_file(),
            "sha256": (
                hashlib.sha256(path.read_bytes()).hexdigest().upper()
                if path.is_file()
                else None
            ),
        }

    script_descriptor = descriptor(script)
    launcher_descriptor = descriptor(launcher)
    return {
        "contract": KAALA_CAPTURE_ASSISTANT_CONTRACT,
        "available": (
            script_descriptor["available"]
            and launcher_descriptor["available"]
        ),
        "script": script_descriptor,
        "launcher": launcher_descriptor,
        "defaultOutputs": {
            "hora": str(
                root
                / "status"
                / "evidence"
                / "jhora_kaala_intermediate_20260729"
                / "jhora_hora_boundary_witness_completed.csv"
            ),
            "ayana": str(
                root
                / "status"
                / "evidence"
                / "jhora_kaala_intermediate_20260729"
                / "jhora_ayana_intermediate_witness_completed.csv"
            ),
        },
        "readsJHoraAutomatically": False,
        "infersAstrologicalValues": False,
        "overwritesPendingTemplates": False,
        "productionChangeAllowed": False,
        "executionAllowed": False,
    }


def kaala_formula_profile_gate_summary(summary_path: Path) -> dict[str, Any]:
    source_sha = None
    if summary_path.exists():
        source_sha = hashlib.sha256(summary_path.read_bytes()).hexdigest().upper()
    base = {
        "required": True,
        "status": "blocked_missing_kaala_formula_profiles",
        "certified": False,
        "productionChangeAllowed": False,
        "profiles": {},
        "horaBoundary": {},
        "workedExamples": {},
        "evidenceConclusions": [],
        "lockedInputs": {},
        "input": {
            "path": str(summary_path),
            "sha256": source_sha,
            "issues": [],
        },
    }
    if not summary_path.exists():
        base["input"]["issues"].append(
            "Kaala formula-profile reconciliation summary is missing"
        )
        return base
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        base["status"] = "blocked_invalid_kaala_formula_profiles"
        base["input"]["issues"].append(
            f"cannot read Kaala formula-profile reconciliation: {exc}"
        )
        return base

    expected_contract = "GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V2"
    if payload.get("contract") != expected_contract:
        base["input"]["issues"].append(
            f"expected contract {expected_contract}; "
            f"found {payload.get('contract')!r}"
        )
    tolerance = payload.get("toleranceVirupa")
    if tolerance is None or not math.isclose(
        float(tolerance), 0.5, rel_tol=0.0, abs_tol=1e-12
    ):
        base["input"]["issues"].append(
            f"expected frozen 0.5-virupa tolerance; found {tolerance!r}"
        )

    locked_inputs: dict[str, dict[str, Any]] = {}
    raw_inputs = dict(payload.get("inputs") or {})
    for input_name in (
        "comparatorScript",
        "visibleComparison",
        "doctrineConfig",
        "workedExamples",
    ):
        metadata = dict(raw_inputs.get(input_name) or {})
        raw_path = str(metadata.get("path") or "").strip()
        expected_sha = str(metadata.get("sha256") or "").strip().upper()
        locked_input = {
            "path": raw_path,
            "expectedSha256": expected_sha or None,
            "actualSha256": None,
        }
        locked_inputs[input_name] = locked_input
        if not raw_path or not expected_sha:
            base["input"]["issues"].append(
                f"{input_name} locked input path/hash is missing"
            )
            continue
        input_path = Path(raw_path)
        if not input_path.is_absolute():
            input_path = Path(__file__).resolve().parent / input_path
        locked_input["path"] = str(input_path)
        if not input_path.exists() or not input_path.is_file():
            base["input"]["issues"].append(
                f"{input_name} locked input is missing: {input_path}"
            )
            continue
        actual_sha = hashlib.sha256(input_path.read_bytes()).hexdigest().upper()
        locked_input["actualSha256"] = actual_sha
        if actual_sha != expected_sha:
            base["input"]["issues"].append(
                f"{input_name} locked input SHA-256 mismatch"
            )
    base["lockedInputs"] = locked_inputs

    required_profiles = {
        "nathonnatha_lmt_source": "nathonnatha",
        "nathonnatha_apparent_solar": "nathonnatha",
        "nathonnatha_astronomical_midnight": "nathonnatha",
        "hora_astronomical_sunrise": "hora",
        "hora_variable_day_night": "hora",
        "ayana_actual_declination": "ayana",
        "ayana_tropical_projection": "ayana",
    }
    raw_profiles = dict(payload.get("profiles") or {})
    missing_profiles = sorted(set(required_profiles).difference(raw_profiles))
    if missing_profiles:
        base["input"]["issues"].append(
            "missing formula profiles: " + ", ".join(missing_profiles)
        )

    normalized_profiles: dict[str, dict[str, Any]] = {}
    for name, expected_measure in required_profiles.items():
        values = dict(raw_profiles.get(name) or {})
        if not values:
            continue
        rows = int(values.get("rows") or 0)
        passed = int(values.get("pass") or 0)
        failed = int(values.get("fail") or 0)
        recent_rows = int(values.get("recentRows") or 0)
        historical_rows = int(values.get("historicalRows") or 0)
        if values.get("measure") != expected_measure:
            base["input"]["issues"].append(
                f"{name} measure must be {expected_measure}"
            )
        if rows != 35 or passed + failed != rows:
            base["input"]["issues"].append(
                f"{name} must contain 35 complete pass/fail rows"
            )
        if recent_rows + historical_rows != rows:
            base["input"]["issues"].append(
                f"{name} recent and historical row counts must sum to {rows}"
            )
        normalized_profiles[name] = {
            "measure": str(values.get("measure") or ""),
            "rows": rows,
            "pass": passed,
            "fail": failed,
            "maeVirupa": float(values.get("maeVirupa") or 0.0),
            "maxErrorVirupa": float(values.get("maxErrorVirupa") or 0.0),
            "recentRows": recent_rows,
            "recentPass": int(values.get("recentPass") or 0),
            "historicalRows": historical_rows,
            "historicalPass": int(values.get("historicalPass") or 0),
        }

    boundary = dict(
        (payload.get("horaBoundary") or {}).get("case_8_event_start") or {}
    )
    required_boundary = {
        "gapMinutes",
        "currentLord",
        "jhoraLord",
        "swissApparentTipSunriseLmtHour",
        "awardFlipSunriseLmtHour",
    }
    if not required_boundary.issubset(boundary):
        base["input"]["issues"].append(
            "case-8 Hora sunrise-boundary evidence is incomplete"
        )

    if base["input"]["issues"]:
        base["status"] = "blocked_incomplete_kaala_formula_profiles"
        base["profiles"] = normalized_profiles
        return base

    base.update(
        {
            "status": "diagnostic_profiles_only_no_production_change",
            "toleranceVirupa": float(tolerance),
            "tolerancePolicy": str(payload.get("tolerancePolicy") or ""),
            "profiles": normalized_profiles,
            "horaBoundary": {"case_8_event_start": boundary},
            "workedExamples": dict(payload.get("workedExamples") or {}),
            "evidenceConclusions": list(
                payload.get("evidenceConclusions") or []
            ),
            "nextWitnesses": [
                (
                    "Nathonnatha needs a visible JHora apparent-birth-time or "
                    "internal Unnata intermediate before any compatibility "
                    "formula can be admitted."
                ),
                (
                    "Hora's exact visible sunrise and Moon award are already "
                    "captured and confirm its narrow 35/35 profile."
                ),
                (
                    "Ayana's visible historical tropical positions are "
                    "captured; the rejected reconstruction now requires an "
                    "internal Kranti or separately sourced formula."
                ),
            ],
        }
    )
    return base


def shadbala_component_witness_gate_summary(
    summary_path: Path,
) -> dict[str, Any]:
    source_sha = None
    if summary_path.exists():
        source_sha = hashlib.sha256(summary_path.read_bytes()).hexdigest().upper()
    base = {
        "required": True,
        "status": "blocked_missing_component_witness",
        "independentWitnessComplete": False,
        "sourceCertified": False,
        "financiallyValidated": False,
        "executionAllowed": False,
        "witnessAlignedTopLevel": [],
        "provisionalTopLevel": [],
        "witnessAlignedKaalaSubcomponents": [],
        "provisionalKaalaSubcomponents": [],
        "fullShadbalaCertified": False,
        "drikCertified": False,
        "input": {
            "path": str(summary_path),
            "sha256": source_sha,
            "issues": [],
        },
    }
    if not summary_path.exists():
        base["input"]["issues"].append(
            "JHora Shadbala reconciliation summary is missing"
        )
        return base
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        base["status"] = "blocked_invalid_component_witness"
        base["input"]["issues"].append(
            f"cannot read JHora Shadbala reconciliation: {exc}"
        )
        return base

    if payload.get("contract") != "GANN_JHORA_DOCTRINE_RECONCILIATION_V3":
        base["status"] = "blocked_stale_component_witness_contract"
        base["input"]["issues"].append(
            "expected GANN_JHORA_DOCTRINE_RECONCILIATION_V3"
        )
        return base

    expected_top_level = {
        "sthana",
        "kaala",
        "dig",
        "chesta",
        "naisargika",
        "drik",
        "total",
    }
    top_level = dict(payload.get("topLevel") or {})
    missing = sorted(expected_top_level.difference(top_level))
    if missing:
        base["input"]["issues"].append(
            "missing top-level Shadbala measures: " + ", ".join(missing)
        )
    expected_rows = len(SAMPLES) * len(CLASSICAL_PLANETS)
    for name, values in top_level.items():
        if name not in expected_top_level:
            base["input"]["issues"].append(
                f"unexpected top-level Shadbala measure: {name}"
            )
            continue
        if int(values.get("rows") or 0) != expected_rows:
            base["input"]["issues"].append(
                f"{name} expected {expected_rows} rows"
            )
    component_gate = dict(payload.get("componentCertification") or {})
    if not component_gate:
        base["input"]["issues"].append(
            "componentCertification decision ledger is missing"
        )
    if base["input"]["issues"]:
        base["status"] = "blocked_incomplete_component_witness"
        return base

    aligned_top_level = sorted(
        name
        for name, values in top_level.items()
        if int(values.get("localPass") or 0) == expected_rows
        and float(values.get("localMaxAbsoluteDeltaVirupa") or 0.0) <= 0.5
    )
    declared_top_level = sorted(
        component_gate.get("witnessAlignedTopLevel") or []
    )
    if aligned_top_level != declared_top_level:
        base["status"] = "blocked_component_witness_decision_mismatch"
        base["input"]["issues"].append(
            "derived and declared top-level witness-aligned components differ"
        )
        return base
    provisional_top_level = sorted(
        component_gate.get("provisionalTopLevel") or []
    )
    if (
        set(declared_top_level).intersection(provisional_top_level)
        or set(declared_top_level).union(provisional_top_level)
        != expected_top_level
    ):
        base["status"] = "blocked_component_witness_partition_mismatch"
        base["input"]["issues"].append(
            "top-level aligned/provisional component partition is invalid"
        )
        return base
    expected_kaala = {
        "abda",
        "masa",
        "vara",
        "hora",
        "tribhaga",
        "paksha",
        "nathonnatha",
        "ayana",
        "yuddha",
        "total",
    }
    aligned_kaala = sorted(
        component_gate.get("witnessAlignedKaalaSubcomponents") or []
    )
    provisional_kaala = sorted(
        component_gate.get("provisionalKaalaSubcomponents") or []
    )
    if (
        set(aligned_kaala).intersection(provisional_kaala)
        or set(aligned_kaala).union(provisional_kaala) != expected_kaala
    ):
        base["status"] = "blocked_component_witness_partition_mismatch"
        base["input"]["issues"].append(
            "Kaala aligned/provisional component partition is invalid"
        )
        return base
    witness_complete = bool(
        component_gate.get("independentWitnessComplete")
    )
    if not witness_complete:
        base["status"] = "blocked_incomplete_independent_witness"
        base["input"]["issues"].append(
            "independent witness is not marked complete"
        )
        return base
    full_certified = bool(component_gate.get("fullShadbalaCertified")) and (
        set(declared_top_level) == expected_top_level
    )
    drik_certified = bool(component_gate.get("drikCertified")) and (
        "drik" in declared_top_level
    )

    base.update(
        {
            "status": "partial_independent_witness_alignment",
            "independentWitnessComplete": witness_complete,
            "witnessAlignedTopLevel": declared_top_level,
            "provisionalTopLevel": provisional_top_level,
            "witnessAlignedKaalaSubcomponents": aligned_kaala,
            "provisionalKaalaSubcomponents": provisional_kaala,
            "fullShadbalaCertified": full_certified,
            "drikCertified": drik_certified,
            "topLevel": {
                name: {
                    "rows": int(values.get("rows") or 0),
                    "pass": int(values.get("localPass") or 0),
                    "fail": int(values.get("localFail") or 0),
                    "maeVirupa": float(
                        values.get("localMeanAbsoluteDeltaVirupa") or 0.0
                    ),
                    "maxErrorVirupa": float(
                        values.get("localMaxAbsoluteDeltaVirupa") or 0.0
                    ),
                    "witnessAligned": name in declared_top_level,
                }
                for name, values in sorted(top_level.items())
            },
        }
    )
    return base


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
            "shadbala.bphs_component_reconciliation_v9",
            "BPHS chapter 27 source profile + locked JHora Kaala witness + pinned PyJHora diagnostics",
            str(shadbala.get("method")),
            "strict_shadbala_doctrine.event_strict_shadbala_context",
            "implemented_unvalidated",
            "versioned source profile with named comparator variants",
            str(shadbala.get("status")),
            "|".join(shadbala.get("missing", [])),
            "Use the locked JHora reconciliation and visible Kaala matrix: dynamic Paksha passes 35/35 and is promoted; Hora, Nathonnatha, Ayana, aggregate Kaala, non-luminary Chesta, and full total remain provisional.",
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
            "failed_independent_validation",
            "versioned reconciled formula",
            "tier_b_pyjhora_aligned_independent_jhora_disagrees_9_of_35",
            "The locked JHora 8.0 witness is complete, but only 9 of 35 Drik rows match within the frozen 0.5-virupa tolerance.",
            "Reconcile the PyJHora/local and JHora aspect, relationship, and contribution profiles; do not widen tolerance.",
            "exclude_from_certified_ml_features_keep_research_diagnostic",
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
                            f"Local strict-v9 BPHS source-profile value at {sample.location}; Raman "
                            "ayanamsa; true node; Porphyry houses. Sthana uses degree-bounded D1 "
                            "Moolatrikona and source weights; Kaala uses astronomical sunrise and the "
                            "published Ahargana scheme; displayed Sun/Moon Chesta is excluded from the "
                            "total to prevent Ayana/Paksha double counting, and motion state remains diagnostic; "
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
    independent_rows = dict(independent_drik.get("rows") or {})
    independent_passed = int(independent_rows.get("pass") or 0)
    independent_failed = int(independent_rows.get("fail") or 0)
    visible_kaala = dict(external_gate.get("visibleKaalaWitness") or {})
    visible_components = dict(visible_kaala.get("components") or {})
    visible_kaala_rows = [
        [
            name,
            values.get("localPass", 0),
            values.get("rows", 0),
            values.get("localMaeVirupa", ""),
            values.get("localMaxVirupa", ""),
        ]
        for name, values in sorted(visible_components.items())
    ]
    visible_sthana = dict(
        external_gate.get("visibleSthanaWitness") or {}
    )
    visible_sthana_rows: list[list[Any]] = []
    for profile_name, profile in sorted(
        dict(visible_sthana.get("profiles") or {}).items()
    ):
        for component, values in sorted(
            dict(profile.get("components") or {}).items()
        ):
            visible_sthana_rows.append(
                [
                    profile_name,
                    component,
                    values.get("pass", 0),
                    values.get("rows", 0),
                    f"{float(values.get('maeVirupa') or 0.0):.3f}",
                    f"{float(values.get('maxErrorVirupa') or 0.0):.3f}",
                ]
            )
        total = dict(profile.get("total") or {})
        visible_sthana_rows.append(
            [
                profile_name,
                "total",
                total.get("pass", 0),
                total.get("rows", 0),
                f"{float(total.get('maeVirupa') or 0.0):.3f}",
                f"{float(total.get('maxErrorVirupa') or 0.0):.3f}",
            ]
        )
    formula_profiles = dict(
        external_gate.get("kaalaFormulaProfiles") or {}
    )
    intermediate_witness = dict(
        external_gate.get("kaalaIntermediateWitness") or {}
    )
    capture_assistant = dict(
        intermediate_witness.get("captureAssistant") or {}
    )
    hora_evidence_complete = bool(
        intermediate_witness.get("horaEvidenceComplete")
    )
    ayana_evidence_complete = bool(
        intermediate_witness.get("ayanaEvidenceComplete")
    )
    intermediate_evidence_complete = bool(
        intermediate_witness.get("evidenceComplete")
    )
    formula_issue_count = len(
        list(intermediate_witness.get("formulaIssues") or [])
    )
    hora_boundary_note = (
        "The separate visible packet is complete and binds JHora's exact LMT "
        "sunrise, Moon Hora lord, and all seven awards. This supports the "
        "narrow Hora witness but does not certify aggregate Kaala or full "
        "Shadbala."
        if hora_evidence_complete
        else (
            "A visible JHora sunrise/intermediate witness is required before "
            "changing Hora."
        )
    )
    ayana_candidate_note = (
        "The seven-planet historical observation is provenance-complete. Its "
        f"{formula_issue_count} above-tolerance reconstruction residuals reject "
        "the tested formula candidate without discarding the external evidence "
        "or widening tolerance."
        if ayana_evidence_complete
        else (
            "The tropical-Kranti Ayana candidate matches all 28 recent rows and "
            "30/35 overall, but only 2/7 historical rows. It remains a candidate "
            "until the required visible historical intermediates are captured."
        )
    )
    intermediate_status_note = (
        "Both hashed visible packets are complete. Valid observations remain "
        "separate from formula certification, and production changes stay "
        "disabled while formula residuals remain."
        if intermediate_evidence_complete
        else (
            "Missing, pending, or invalid visible packets keep production "
            "changes disabled."
        )
    )
    formula_profile_values = dict(formula_profiles.get("profiles") or {})
    formula_profile_labels = {
        "nathonnatha_lmt_source": "Nathonnatha - current LMT",
        "nathonnatha_apparent_solar": "Nathonnatha - apparent solar",
        "nathonnatha_astronomical_midnight": (
            "Nathonnatha - astronomical midnight"
        ),
        "hora_astronomical_sunrise": "Hora - current sunrise award",
        "hora_variable_day_night": "Hora - variable day/night hours",
        "ayana_actual_declination": "Ayana - current actual declination",
        "ayana_tropical_projection": "Ayana - tropical Kranti candidate",
    }
    formula_profile_rows = [
        [
            formula_profile_labels.get(name, name),
            values.get("pass", 0),
            values.get("rows", 0),
            f"{float(values.get('maeVirupa') or 0.0):.3f}",
            (
                f"{values.get('recentPass', 0)}/"
                f"{values.get('recentRows', 0)}"
            ),
            (
                f"{values.get('historicalPass', 0)}/"
                f"{values.get('historicalRows', 0)}"
            ),
        ]
        for name, values in formula_profile_values.items()
    ]
    hora_boundary = dict(
        (formula_profiles.get("horaBoundary") or {}).get(
            "case_8_event_start"
        )
        or {}
    )
    component_witness = dict(
        external_gate.get("shadbalaComponentWitness") or {}
    )
    top_level_components = dict(component_witness.get("topLevel") or {})
    top_level_component_rows = [
        [
            name,
            values.get("pass", 0),
            values.get("rows", 0),
            f"{float(values.get('maeVirupa') or 0.0):.3f}",
            f"{float(values.get('maxErrorVirupa') or 0.0):.3f}",
            "witness aligned"
            if values.get("witnessAligned")
            else "provisional",
        ]
        for name, values in sorted(top_level_components.items())
    ]
    sthana_witness = dict(top_level_components.get("sthana") or {})
    kaala_witness = dict(top_level_components.get("kaala") or {})
    total_witness = dict(top_level_components.get("total") or {})
    aligned_kaala = set(
        component_witness.get("witnessAlignedKaalaSubcomponents") or []
    )
    hora_status_text = (
        "Hora is independently witness-aligned at 35/35, while Nathonnatha, "
        "Ayana, and aggregate Kaala remain provisional. "
        if "hora" in aligned_kaala
        else (
            "Hora, Nathonnatha, Ayana, and aggregate Kaala remain provisional. "
        )
    )
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
            "locked local-versus-JHora reconciliation excludes displayed Sun/Moon "
            "Chesta from the total and promotes dynamic Paksha after 35/35 visible "
            "subcomponent matches. The actual production source profile, rather "
            "than the separately named PyJHora-compatible Sthana profile, is used "
            f"for this gate: Sthana passes {sthana_witness.get('pass', 0)}/"
            f"{sthana_witness.get('rows', 35)} and full total passes "
            f"{total_witness.get('pass', 0)}/{total_witness.get('rows', 35)} "
            f"with {float(total_witness.get('maeVirupa') or 0.0):.3f} virupa "
            "mean absolute error. Top-level local Kaala passes "
            f"{kaala_witness.get('pass', 0)}/{kaala_witness.get('rows', 35)} "
            f"with {float(kaala_witness.get('maeVirupa') or 0.0):.3f} virupa "
            f"mean absolute error; {hora_status_text}The "
            f"completed independent JHora Drik witness passes "
            f"{independent_passed}/35 and fails {independent_failed}/35. Keep full "
            "Shadbala and Drik excluded from certified ML/execution until the "
            "doctrine profiles are explicitly reconciled."
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
        "### Visible JHora Kaala Witness",
        "",
        (
            f"Status: `{visible_kaala.get('status', 'not generated')}`. "
            "This evidence can validate individual Kaala subcomponents; it does "
            "not certify aggregate Kaala or full Shadbala."
        ),
        "",
        markdown_table(
            ["Component", "Local pass", "Rows", "MAE virupa", "Max error virupa"],
            visible_kaala_rows,
        )
        if visible_kaala_rows
        else "No complete visible Kaala witness was loaded.",
        "",
        "### Visible JHora Sthana Witness",
        "",
        (
            f"Status: `{visible_sthana.get('status', 'not generated')}`. "
            "The 175-row visible matrix identifies component-level agreement "
            "without inferring residuals. A JHora-compatible diagnostic "
            "profile does not silently replace the separately cited "
            "production source profile."
        ),
        "",
        markdown_table(
            [
                "Profile",
                "Component",
                "Pass",
                "Rows",
                "MAE virupa",
                "Max error virupa",
            ],
            visible_sthana_rows,
        )
        if visible_sthana_rows
        else "No complete visible Sthana witness was loaded.",
        "",
        (
            "Source-aligned components: "
            + ", ".join(
                visible_sthana.get("sourceAlignedComponents") or []
            )
            + ". Source-divergent components: "
            + ", ".join(
                visible_sthana.get("sourceDivergentComponents") or []
            )
            + "."
        ),
        "",
        "### Kaala Formula Profile Reconciliation",
        "",
        (
            f"Status: `{formula_profiles.get('status', 'not generated')}`. "
            "These profiles diagnose the remaining Hora, Nathonnatha, and "
            "Ayana differences. They do not change production formulas, widen "
            "the frozen tolerance, certify aggregate Kaala, or authorize ML "
            "or execution use."
        ),
        "",
        markdown_table(
            [
                "Profile",
                "Pass",
                "Rows",
                "MAE virupa",
                "Recent pass",
                "Historical pass",
            ],
            formula_profile_rows,
        )
        if formula_profile_rows
        else "No complete Kaala formula-profile reconciliation was loaded.",
        "",
        (
            "Case 8 Hora boundary: current lord "
            f"`{hora_boundary.get('currentLord', 'unknown')}`, visible JHora "
            f"lord `{hora_boundary.get('jhoraLord', 'unknown')}`; the award "
            "flips across only "
            f"`{float(hora_boundary.get('gapMinutes') or 0.0):.3f}` minutes "
            f"of sunrise input. {hora_boundary_note}"
        ),
        "",
        ayana_candidate_note,
        "",
        (
            "Intermediate witness status: "
            f"`{intermediate_witness.get('status', 'not generated')}` "
            f"({intermediate_witness.get('horaRows', 0)} Hora rows; "
            f"{intermediate_witness.get('ayanaRows', 0)} Ayana rows). "
            f"{intermediate_status_note}"
        ),
        "",
        (
            "Guided capture assistant: "
            f"`{'available' if capture_assistant.get('available') else 'missing'}`. "
            "It records reviewer-visible values, hashes the selected evidence, "
            "validates all seven planets, and cannot read JHora automatically, "
            "infer astrology values, overwrite capture templates, or "
            "unlock execution."
        ),
        "",
        "### Shadbala Component Admission Boundary",
        "",
        (
            f"Status: `{component_witness.get('status', 'not generated')}`. "
            "Independent witness alignment requires every one of the 35 locked "
            "rows to pass at 0.5 virupa. It does not establish source "
            "certification, financial validation, or execution permission."
        ),
        "",
        markdown_table(
            [
                "Top-level component",
                "Pass",
                "Rows",
                "MAE virupa",
                "Max error virupa",
                "Admission",
            ],
            top_level_component_rows,
        )
        if top_level_component_rows
        else "No complete top-level Shadbala component witness was loaded.",
        "",
        (
            "Witness-aligned Kaala subcomponents: "
            + ", ".join(
                component_witness.get(
                    "witnessAlignedKaalaSubcomponents", []
                )
            )
            + "."
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
    visible_kaala_path = Path(args.jhora_kaala_summary)
    if not visible_kaala_path.is_absolute():
        visible_kaala_path = root / visible_kaala_path
    visible_kaala_gate = visible_kaala_gate_summary(visible_kaala_path)
    visible_sthana_path = Path(args.jhora_sthana_summary)
    if not visible_sthana_path.is_absolute():
        visible_sthana_path = root / visible_sthana_path
    visible_sthana_gate = visible_sthana_gate_summary(
        visible_sthana_path
    )
    kaala_formula_path = Path(args.jhora_kaala_formula_summary)
    if not kaala_formula_path.is_absolute():
        kaala_formula_path = root / kaala_formula_path
    kaala_formula_gate = kaala_formula_profile_gate_summary(
        kaala_formula_path
    )
    hora_intermediate_path = Path(args.jhora_hora_intermediate_witness)
    if not hora_intermediate_path.is_absolute():
        hora_intermediate_path = root / hora_intermediate_path
    ayana_intermediate_path = Path(args.jhora_ayana_intermediate_witness)
    if not ayana_intermediate_path.is_absolute():
        ayana_intermediate_path = root / ayana_intermediate_path
    kaala_visible_values_path = Path(args.jhora_kaala_visible_values)
    if not kaala_visible_values_path.is_absolute():
        kaala_visible_values_path = root / kaala_visible_values_path
    from jhora_kaala_intermediate_witness_protocol import (
        witness_gate_summary as kaala_intermediate_witness_gate_summary,
    )

    kaala_intermediate_gate = kaala_intermediate_witness_gate_summary(
        hora_path=hora_intermediate_path,
        ayana_path=ayana_intermediate_path,
        kaala_witness_path=kaala_visible_values_path,
    )
    kaala_intermediate_gate["captureAssistant"] = (
        kaala_capture_assistant_summary(root)
    )
    shadbala_reconciliation_path = Path(args.jhora_shadbala_reconciliation)
    if not shadbala_reconciliation_path.is_absolute():
        shadbala_reconciliation_path = root / shadbala_reconciliation_path
    component_witness_gate = shadbala_component_witness_gate_summary(
        shadbala_reconciliation_path
    )
    external_gate["independentDrikWitness"] = independent_gate
    external_gate["visibleKaalaWitness"] = visible_kaala_gate
    external_gate["visibleSthanaWitness"] = visible_sthana_gate
    external_gate["kaalaFormulaProfiles"] = kaala_formula_gate
    external_gate["kaalaIntermediateWitness"] = kaala_intermediate_gate
    external_gate["shadbalaComponentWitness"] = component_witness_gate
    external_gate["requirements"].append(
        "PyJHora is a Tier B comparator only; independent Jagannatha Hora or cited worked-example "
        "Drik evidence must also pass before certification."
    )
    external_gate["requirements"].append(
        "Visible JHora Kaala evidence may promote an individual subcomponent only "
        "when all 35 rows pass at the frozen 0.5-virupa tolerance; aggregate Kaala "
        "and full Shadbala remain uncertified until their complete matrices pass."
    )
    external_gate["requirements"].append(
        "Visible JHora Sthana evidence must contain all 175 hashed component "
        "rows and reconcile to the locked top-level matrix. A complete "
        "compatibility profile remains diagnostic unless the separately cited "
        "source doctrine also passes; no silent production replacement is "
        "allowed."
    )
    external_gate["requirements"].append(
        "Kaala formula-profile reconciliation is diagnostic only. Candidate "
        "profiles cannot alter production until every locked row passes and "
        "the relevant visible JHora intermediate inputs are captured."
    )
    external_gate["requirements"].append(
        "Hora and historical Ayana candidates require a complete visible, "
        "hashed JHora intermediate-input packet. Missing or invalid packets keep "
        "production formula changes disabled; valid observations do not override "
        "a failed formula reconciliation."
    )
    external_gate["requirements"].append(
        "Top-level Shadbala component admission is row-complete and fail-closed. "
        "Independent witness alignment never implies source certification, "
        "financial validation, or execution permission."
    )
    if external_gate["certified"] and not independent_gate["certified"]:
        external_gate["status"] = "blocked_pending_independent_drik_validation"
    elif external_gate["certified"] and not component_witness_gate[
        "fullShadbalaCertified"
    ]:
        external_gate["status"] = (
            "blocked_partial_shadbala_component_witness"
        )
    external_gate["certified"] = bool(
        external_gate["certified"]
        and independent_gate["certified"]
        and component_witness_gate["fullShadbalaCertified"]
        and component_witness_gate["drikCertified"]
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
