from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import swisseph as swe

from astro_function_certification import (
    CLASSICAL_PLANETS,
    PLANETS,
    SAMPLES,
    calc_planet,
    jd_ut_for,
    sample_datetime,
    sidereal_house_cusps,
)
from doctrine_config import configure_swiss_ephemeris_sidereal, load_doctrine_config
from financial_astro_ephemeris import configure_ephemeris
from pyjhora_external_strength_export import (
    KAALA_SUBCOMPONENTS,
    SHADBALA_COMPONENTS,
)
from strict_shadbala_doctrine import (
    SAPTAVARGAJA_JHORA_VISIBLE_PROFILE,
    SAPTAVARGAJA_PYJHORA_PROFILE,
    SAPTAVARGAJA_SOURCE_PROFILE,
    chesta_pyjhora_epoch_compatibility_from_inputs,
    components_for_body,
    sthana_bala_from_longitudes,
)


COMPARATOR_CONTRACT = "GANN_SHADBALA_COMPONENT_COMPARATOR_V3"
LOCAL_COMPONENT_FIELDS = {
    "sthana": "sthana_comparator_virupa",
    "kaala": "kaala_9_virupa",
    "dig": "dig_virupa",
    "chesta": "chesta_virupa",
    "naisargika": "naisargika_virupa",
    "drik": "drik_virupa",
}
LOCAL_SOURCE_COMPONENT_FIELDS = {
    **LOCAL_COMPONENT_FIELDS,
    "sthana": "sthana_partial_virupa",
}
LOCAL_KAALA_FIELDS = {
    "nathonnatha": "nathonnatha_virupa",
    "paksha": "paksha_virupa",
    "tribhaga": "tribhaga_virupa",
    "abda": "abda_virupa",
    "masa": "masa_virupa",
    "vara": "vara_virupa",
    "hora": "hora_virupa",
    "ayana": "ayana_virupa",
    "yuddha": "yuddha_virupa",
    "total": "kaala_9_virupa",
}
STRUCTURAL_COMPONENT_DIFFERENCES = {
    ("chesta", "SUN"): (
        "BPHS source profile uses Sun Chesta = Ayana; PyJHora returns zero."
    ),
    ("chesta", "MOON"): (
        "BPHS source profile uses Moon Chesta = Paksha; PyJHora returns zero."
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare source-profile Shadbala with pinned PyJHora end-to-end, "
            "subcomponent, and shared-input formula evidence."
        )
    )
    parser.add_argument(
        "--doctrine-config",
        type=Path,
        default=Path(r"D:\PycharmProjects\doctrine_config.yaml"),
    )
    parser.add_argument(
        "--external-components",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_shadbala_components_20260718.csv"),
    )
    parser.add_argument(
        "--external-kaala",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_kaala_subcomponents_20260718.csv"),
    )
    parser.add_argument(
        "--external-formula-inputs",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_shadbala_formula_inputs_20260718.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(r"D:\PycharmProjects\shadbala_component_residuals_20260718.csv"),
    )
    parser.add_argument(
        "--kaala-output",
        type=Path,
        default=Path(r"D:\PycharmProjects\shadbala_kaala_subcomponent_residuals_20260718.csv"),
    )
    parser.add_argument(
        "--formula-output",
        type=Path,
        default=Path(r"D:\PycharmProjects\shadbala_formula_compatibility_residuals_20260718.csv"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(r"D:\PycharmProjects\shadbala_component_reconciliation_20260718.md"),
    )
    parser.add_argument("--tolerance", type=float, default=0.5)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _sample_contexts(config_path: Path) -> list[dict[str, Any]]:
    config = load_doctrine_config(config_path)
    configure_ephemeris()
    configure_swiss_ephemeris_sidereal(swe, config)
    contexts: list[dict[str, Any]] = []
    for sample in SAMPLES:
        local_dt = sample_datetime(sample.local_iso, sample.timezone)
        jd_ut, _utc_dt = jd_ut_for(local_dt)
        ayanamsa_deg = float(swe.get_ayanamsa_ut(jd_ut))
        sidereal_values: dict[str, float] = {}
        speeds: dict[str, float] = {}
        latitudes: dict[str, float] = {}
        declinations: dict[str, float] = {}
        for planet, planet_id in PLANETS.items():
            _tropical, sidereal, speed, latitude, declination = calc_planet(
                jd_ut,
                planet_id,
                ayanamsa_deg,
            )
            sidereal_values[planet] = sidereal
            if planet in CLASSICAL_PLANETS:
                speeds[planet] = speed
                latitudes[planet] = latitude
                declinations[planet] = declination
        houses = sidereal_house_cusps(
            jd_ut,
            sample.latitude,
            sample.longitude,
        )
        contexts.append(
            {
                "sample": sample,
                "local_dt": local_dt,
                "longitudes": sidereal_values,
                "speeds": speeds,
                "latitudes": latitudes,
                "declinations": declinations,
                "houses": houses,
                "asc_lon": houses[1],
            }
        )
    return contexts


def calculate_local_component_values(
    config_path: Path,
) -> dict[tuple[str, str, str], float]:
    return _calculate_local_component_values(config_path, LOCAL_COMPONENT_FIELDS)


def calculate_local_source_component_values(
    config_path: Path,
) -> dict[tuple[str, str, str], float]:
    return _calculate_local_component_values(
        config_path,
        LOCAL_SOURCE_COMPONENT_FIELDS,
    )


def _calculate_local_component_values(
    config_path: Path,
    fields: dict[str, str],
) -> dict[tuple[str, str, str], float]:
    values: dict[tuple[str, str, str], float] = {}
    for context in _sample_contexts(config_path):
        sample = context["sample"]
        for planet in CLASSICAL_PLANETS:
            components = components_for_body(
                planet,
                context["longitudes"],
                context["asc_lon"],
                context["houses"],
                context["local_dt"],
                sample.longitude,
                context["speeds"],
                context["latitudes"],
                context["declinations"],
                sample.latitude,
            )
            for component, field in fields.items():
                value = float(components[field])
                if not math.isfinite(value):
                    raise RuntimeError(
                        f"Non-finite local {component} value for "
                        f"{sample.sample_id}/{planet}."
                    )
                values[(sample.sample_id, planet, component)] = value
    return values


def calculate_local_kaala_values(
    config_path: Path,
) -> dict[tuple[str, str, str], float]:
    values: dict[tuple[str, str, str], float] = {}
    for context in _sample_contexts(config_path):
        sample = context["sample"]
        for planet in CLASSICAL_PLANETS:
            components = components_for_body(
                planet,
                context["longitudes"],
                context["asc_lon"],
                context["houses"],
                context["local_dt"],
                sample.longitude,
                context["speeds"],
                context["latitudes"],
                context["declinations"],
                sample.latitude,
            )
            for measure, field in LOCAL_KAALA_FIELDS.items():
                value = float(components[field])
                if not math.isfinite(value):
                    raise RuntimeError(
                        f"Non-finite local Kaala {measure} value for "
                        f"{sample.sample_id}/{planet}."
                    )
                values[(sample.sample_id, planet, measure)] = value
    return values


def calculate_sthana_subcomponent_values(
    config_path: Path,
    *,
    profile: str = SAPTAVARGAJA_SOURCE_PROFILE,
) -> dict[tuple[str, str, str], float]:
    if profile not in {
        SAPTAVARGAJA_SOURCE_PROFILE,
        SAPTAVARGAJA_PYJHORA_PROFILE,
        SAPTAVARGAJA_JHORA_VISIBLE_PROFILE,
    }:
        raise ValueError(f"Unsupported Sthana comparison profile: {profile}")
    values: dict[tuple[str, str, str], float] = {}
    fields = {
        "uchcha": "uchcha_virupa",
        "saptavargaja": "saptavargaja_virupa",
        "ojayugma": "ojayugma_virupa",
        "kendradi": "kendradi_virupa",
        "drekkana": "drekkana_virupa",
    }
    for context in _sample_contexts(config_path):
        sample = context["sample"]
        for planet in CLASSICAL_PLANETS:
            components = sthana_bala_from_longitudes(
                planet,
                context["longitudes"][planet],
                context["longitudes"],
                context["asc_lon"],
                profile=profile,
            )
            for component, field in fields.items():
                value = float(components[field])
                if not math.isfinite(value):
                    raise RuntimeError(
                        f"Non-finite local Sthana {component} value for "
                        f"{sample.sample_id}/{planet}."
                    )
                values[(sample.sample_id, planet, component)] = value
    return values


def _read_numeric_matrix(
    path: Path,
    *,
    key_field: str,
) -> tuple[dict[tuple[str, str, str], float], str]:
    values: dict[tuple[str, str, str], float] = {}
    source = ""
    with path.open(newline="", encoding="utf-8") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            key = (
                str(row.get("sample_id") or "").strip(),
                str(row.get("planet") or "").strip().upper(),
                str(row.get(key_field) or "").strip().lower(),
            )
            if key in values:
                raise RuntimeError(f"Duplicate external row {row_number}: {key}")
            try:
                value = float(
                    str(row.get("external_value_virupa") or "").strip()
                )
            except ValueError as exc:
                raise RuntimeError(
                    f"Invalid external value at row {row_number}: {key}"
                ) from exc
            if not math.isfinite(value):
                raise RuntimeError(
                    f"Non-finite external value at row {row_number}: {key}"
                )
            values[key] = value
            row_source = str(row.get("source") or "").strip()
            if not row_source:
                raise RuntimeError(
                    f"Missing external source at row {row_number}: {key}"
                )
            if source and row_source != source:
                raise RuntimeError(
                    "External rows contain mixed source declarations."
                )
            source = row_source
    return values, source


def read_external_components(
    path: Path,
) -> tuple[dict[tuple[str, str, str], float], str]:
    return _read_numeric_matrix(path, key_field="component")


def read_external_kaala(
    path: Path,
) -> tuple[dict[tuple[str, str, str], float], str]:
    return _read_numeric_matrix(path, key_field="measure")


def read_formula_inputs(path: Path) -> tuple[list[dict[str, str]], str]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    expected = len(SAMPLES) * len(CLASSICAL_PLANETS)
    if len(rows) != expected:
        raise RuntimeError(
            f"Formula-input matrix must contain {expected} rows, got {len(rows)}."
        )
    source = ""
    seen: set[tuple[str, str]] = set()
    for row_number, row in enumerate(rows, start=2):
        key = (
            str(row.get("sample_id") or "").strip(),
            str(row.get("planet") or "").strip().upper(),
        )
        if key in seen:
            raise RuntimeError(
                f"Duplicate formula-input row {row_number}: {key}"
            )
        seen.add(key)
        row_source = str(row.get("source") or "").strip()
        if not row_source:
            raise RuntimeError(
                f"Missing formula-input source at row {row_number}: {key}"
            )
        if source and row_source != source:
            raise RuntimeError(
                "Formula-input rows contain mixed source declarations."
            )
        source = row_source
    return rows, source


def expected_component_keys() -> set[tuple[str, str, str]]:
    return {
        (sample.sample_id, planet, component)
        for sample in SAMPLES
        for planet in CLASSICAL_PLANETS
        for component in SHADBALA_COMPONENTS
    }


def expected_kaala_keys() -> set[tuple[str, str, str]]:
    return {
        (sample.sample_id, planet, measure)
        for sample in SAMPLES
        for planet in CLASSICAL_PLANETS
        for measure in KAALA_SUBCOMPONENTS
    }


def _compare_matrices(
    local: dict[tuple[str, str, str], float],
    external: dict[tuple[str, str, str], float],
    *,
    expected: set[tuple[str, str, str]],
    tolerance: float,
    source: str,
    key_label: str,
    structural_differences: dict[tuple[str, str], str] | None = None,
) -> list[dict[str, str]]:
    for label, matrix in (("local", local), ("external", external)):
        if set(matrix) != expected:
            missing = sorted(expected - set(matrix))
            extra = sorted(set(matrix) - expected)
            raise RuntimeError(
                f"{label} {key_label} matrix mismatch: "
                f"missing={missing}, extra={extra}"
            )
    structural_differences = structural_differences or {}
    rows: list[dict[str, str]] = []
    for key in sorted(expected):
        local_value = float(local[key])
        external_value = float(external[key])
        structural_reason = structural_differences.get((key[2], key[1]), "")
        if structural_reason:
            signed_delta = ""
            absolute_delta = ""
            status = "structural_n_a"
        else:
            signed = local_value - external_value
            absolute = abs(signed)
            signed_delta = f"{signed:.9f}"
            absolute_delta = f"{absolute:.9f}"
            status = "pass" if absolute <= tolerance else "fail"
        rows.append(
            {
                "sample_id": key[0],
                "planet": key[1],
                key_label: key[2],
                "local_value_virupa": f"{local_value:.9f}",
                "external_value_virupa": f"{external_value:.9f}",
                "signed_delta_virupa": signed_delta,
                "absolute_delta_virupa": absolute_delta,
                "tolerance_virupa": f"{float(tolerance):.9f}",
                "pass_fail": status,
                "comparison_reason": (
                    structural_reason
                    if structural_reason
                    else "numeric_within_tolerance"
                    if status == "pass"
                    else "numeric_outside_tolerance"
                ),
                "external_source": source,
            }
        )
    return rows


def compare_component_matrices(
    local: dict[tuple[str, str, str], float],
    external: dict[tuple[str, str, str], float],
    *,
    tolerance: float,
    source: str,
) -> list[dict[str, str]]:
    return _compare_matrices(
        local,
        external,
        expected=expected_component_keys(),
        tolerance=tolerance,
        source=source,
        key_label="component",
        structural_differences=STRUCTURAL_COMPONENT_DIFFERENCES,
    )


def compare_kaala_matrices(
    local: dict[tuple[str, str, str], float],
    external: dict[tuple[str, str, str], float],
    *,
    tolerance: float,
    source: str,
) -> list[dict[str, str]]:
    return _compare_matrices(
        local,
        external,
        expected=expected_kaala_keys(),
        tolerance=tolerance,
        source=source,
        key_label="measure",
    )


def calculate_shared_formula_values(
    rows: list[dict[str, str]],
) -> tuple[
    dict[tuple[str, str, str], float],
    dict[tuple[str, str, str], float],
]:
    local: dict[tuple[str, str, str], float] = {}
    external: dict[tuple[str, str, str], float] = {}
    for row in rows:
        sample_id = str(row["sample_id"]).strip()
        planet = str(row["planet"]).strip().upper()
        longitudes_raw = json.loads(row["classical_longitudes_json"])
        longitudes = {
            str(key).upper(): float(value)
            for key, value in longitudes_raw.items()
        }
        sthana = sthana_bala_from_longitudes(
            planet,
            float(row["planet_longitude_deg"]),
            longitudes,
            float(row["ascendant_longitude_deg"]),
            profile=SAPTAVARGAJA_PYJHORA_PROFILE,
        )
        local[(sample_id, planet, "sthana")] = float(sthana["total_virupa"])
        external[(sample_id, planet, "sthana")] = math.nan
        mean_sun = str(row.get("mean_sun_longitude_deg") or "").strip()
        mean_planet = str(row.get("mean_planet_longitude_deg") or "").strip()
        chesta = chesta_pyjhora_epoch_compatibility_from_inputs(
            planet,
            row["chesta_true_longitude_deg"],
            mean_sun if mean_sun else None,
            mean_planet if mean_planet else None,
        )
        local[(sample_id, planet, "chesta")] = float(chesta["virupa"])
        external[(sample_id, planet, "chesta")] = float(
            row["external_chesta_virupa"]
        )
    return local, external


def compare_shared_formula_matrices(
    local: dict[tuple[str, str, str], float],
    external: dict[tuple[str, str, str], float],
    external_components: dict[tuple[str, str, str], float],
    *,
    tolerance: float,
    source: str,
) -> list[dict[str, str]]:
    expected = {
        (sample.sample_id, planet, component)
        for sample in SAMPLES
        for planet in CLASSICAL_PLANETS
        for component in ("sthana", "chesta")
    }
    for key in expected:
        if key[2] == "sthana":
            external[key] = external_components[key]
    structural = {
        ("chesta", "SUN"): (
            "PyJHora epoch-table Chesta vector has no Sun formula."
        ),
        ("chesta", "MOON"): (
            "PyJHora epoch-table Chesta vector has no Moon formula."
        ),
    }
    return _compare_matrices(
        local,
        external,
        expected=expected,
        tolerance=tolerance,
        source=source,
        key_label="formula",
        structural_differences=structural,
    )


def residual_summary(
    rows: list[dict[str, str]],
    *,
    group_field: str = "component",
) -> dict[str, Any]:
    groups: dict[str, list[float]] = defaultdict(list)
    row_counts: dict[str, int] = defaultdict(int)
    pass_counts: dict[str, int] = defaultdict(int)
    fail_counts: dict[str, int] = defaultdict(int)
    structural_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        group = row[group_field]
        row_counts[group] += 1
        status = row["pass_fail"]
        if status == "structural_n_a":
            structural_counts[group] += 1
            continue
        groups[group].append(float(row["absolute_delta_virupa"]))
        pass_counts[group] += status == "pass"
        fail_counts[group] += status == "fail"
    return {
        group: {
            "rows": row_counts[group],
            "comparable": len(groups[group]),
            "pass": pass_counts[group],
            "fail": fail_counts[group],
            "structuralNA": structural_counts[group],
            "meanAbsoluteResidualVirupa": (
                sum(groups[group]) / len(groups[group])
                if groups[group]
                else None
            ),
            "maxAbsoluteResidualVirupa": (
                max(groups[group]) if groups[group] else None
            ),
        }
        for group in sorted(row_counts)
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _matrix_totals(rows: list[dict[str, str]]) -> dict[str, int]:
    return {
        "rows": len(rows),
        "comparable": sum(
            row["pass_fail"] in {"pass", "fail"} for row in rows
        ),
        "pass": sum(row["pass_fail"] == "pass" for row in rows),
        "fail": sum(row["pass_fail"] == "fail" for row in rows),
        "structuralNA": sum(
            row["pass_fail"] == "structural_n_a" for row in rows
        ),
    }


def _append_summary_table(
    lines: list[str],
    summary: dict[str, Any],
    *,
    label: str,
) -> None:
    lines.extend(
        [
            f"## {label}",
            "",
            "| Measure | Comparable | Pass | Fail | Structural N/A | "
            "Mean absolute residual | Maximum residual |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for measure, values in summary.items():
        mean = values["meanAbsoluteResidualVirupa"]
        maximum = values["maxAbsoluteResidualVirupa"]
        lines.append(
            f"| {measure} | {values['comparable']} | {values['pass']} | "
            f"{values['fail']} | {values['structuralNA']} | "
            f"{mean:.6f} | {maximum:.6f} |"
            if mean is not None and maximum is not None
            else (
                f"| {measure} | {values['comparable']} | {values['pass']} | "
                f"{values['fail']} | {values['structuralNA']} | n/a | n/a |"
            )
        )
    lines.append("")


def write_report(
    path: Path,
    component_rows: list[dict[str, str]],
    component_summary: dict[str, Any],
    kaala_rows: list[dict[str, str]],
    kaala_summary: dict[str, Any],
    formula_rows: list[dict[str, str]],
    formula_summary: dict[str, Any],
    *,
    external_component_path: Path,
    external_kaala_path: Path,
    external_formula_path: Path,
    source: str,
) -> None:
    component_totals = _matrix_totals(component_rows)
    kaala_totals = _matrix_totals(kaala_rows)
    formula_totals = _matrix_totals(formula_rows)
    numeric_component_rows = [
        row for row in component_rows if row["pass_fail"] != "structural_n_a"
    ]
    worst = sorted(
        numeric_component_rows,
        key=lambda row: float(row["absolute_delta_virupa"]),
        reverse=True,
    )[:15]
    lines = [
        "# Shadbala Component Reconciliation",
        "",
        f"Contract: `{COMPARATOR_CONTRACT}`",
        "",
        "This is a diagnostic Tier B comparison. It does not certify a doctrine or",
        "authorize execution. It reports three matrices separately so formula",
        "agreement cannot be confused with source-doctrine certification.",
        "",
        f"- Component matrix SHA-256: `{sha256(external_component_path)}`",
        f"- Kaala matrix SHA-256: `{sha256(external_kaala_path)}`",
        f"- Shared-input matrix SHA-256: `{sha256(external_formula_path)}`",
        f"- External source: `{source}`",
        "",
        "## Matrix Totals",
        "",
        "| Matrix | Rows | Comparable | Pass | Fail | Structural N/A |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| End-to-end components | {component_totals['rows']} | "
        f"{component_totals['comparable']} | {component_totals['pass']} | "
        f"{component_totals['fail']} | {component_totals['structuralNA']} |",
        f"| Kaala subcomponents | {kaala_totals['rows']} | "
        f"{kaala_totals['comparable']} | {kaala_totals['pass']} | "
        f"{kaala_totals['fail']} | {kaala_totals['structuralNA']} |",
        f"| Shared-input formulas | {formula_totals['rows']} | "
        f"{formula_totals['comparable']} | {formula_totals['pass']} | "
        f"{formula_totals['fail']} | {formula_totals['structuralNA']} |",
        "",
    ]
    _append_summary_table(
        lines,
        component_summary,
        label="End-to-End Component Summary",
    )
    _append_summary_table(
        lines,
        kaala_summary,
        label="Kaala Subcomponent Summary",
    )
    _append_summary_table(
        lines,
        formula_summary,
        label="Shared-Input Formula Summary",
    )
    lines.extend(
        [
            "## Largest End-to-End Numeric Residuals",
            "",
            "| Sample | Planet | Component | Local | External | Signed delta |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in worst:
        lines.append(
            f"| {row['sample_id']} | {row['planet']} | {row['component']} | "
            f"{float(row['local_value_virupa']):.6f} | "
            f"{float(row['external_value_virupa']):.6f} | "
            f"{float(row['signed_delta_virupa']):+.6f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Lock",
            "",
            "- Sun and Moon Chesta are structural N/A rows: the BPHS source profile "
            "assigns Ayana/Paksha while PyJHora's epoch-table vector returns zero.",
            "- Mars-Saturn shared-input Chesta checks only whether our compatibility "
            "helper reproduces PyJHora's epoch-table linear formula. It does not "
            "replace the production Swiss osculating source profile.",
            "- Shared-input Sthana removes ephemeris drift by feeding both formulas "
            "the same PyJHora longitudes and ascendant.",
            "- Kaala remains decomposed into nine contributors plus total; disagreement "
            "must be resolved contributor by contributor, never by widening tolerance.",
            "- PyJHora is a secondary comparator. Jagannatha Hora or a reproducible "
            "worked example remains the independent deciding witness.",
            "- No comparator result authorizes Auto Suggest, ML training, or live orders.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.tolerance < 0:
        raise ValueError("Tolerance must be non-negative.")
    local_components = calculate_local_component_values(args.doctrine_config)
    external_components, source = read_external_components(
        args.external_components
    )
    component_rows = compare_component_matrices(
        local_components,
        external_components,
        tolerance=args.tolerance,
        source=source,
    )
    local_kaala = calculate_local_kaala_values(args.doctrine_config)
    external_kaala, kaala_source = read_external_kaala(args.external_kaala)
    if kaala_source != source:
        raise RuntimeError("Component and Kaala sources do not match.")
    kaala_rows = compare_kaala_matrices(
        local_kaala,
        external_kaala,
        tolerance=args.tolerance,
        source=source,
    )
    formula_inputs, formula_source = read_formula_inputs(
        args.external_formula_inputs
    )
    if formula_source != source:
        raise RuntimeError("Component and shared-input sources do not match.")
    local_formula, external_formula = calculate_shared_formula_values(
        formula_inputs
    )
    formula_rows = compare_shared_formula_matrices(
        local_formula,
        external_formula,
        external_components,
        tolerance=args.tolerance,
        source=source,
    )
    component_summary = residual_summary(component_rows)
    kaala_summary = residual_summary(kaala_rows, group_field="measure")
    formula_summary = residual_summary(formula_rows, group_field="formula")
    write_csv(args.output, component_rows)
    write_csv(args.kaala_output, kaala_rows)
    write_csv(args.formula_output, formula_rows)
    write_report(
        args.report,
        component_rows,
        component_summary,
        kaala_rows,
        kaala_summary,
        formula_rows,
        formula_summary,
        external_component_path=args.external_components,
        external_kaala_path=args.external_kaala,
        external_formula_path=args.external_formula_inputs,
        source=source,
    )
    result = {
        "contract": COMPARATOR_CONTRACT,
        "components": _matrix_totals(component_rows),
        "kaalaSubcomponents": _matrix_totals(kaala_rows),
        "sharedInputFormulas": _matrix_totals(formula_rows),
        "componentSummary": component_summary,
        "kaalaSummary": kaala_summary,
        "formulaSummary": formula_summary,
        "output": str(args.output.resolve()),
        "outputSha256": sha256(args.output),
        "kaalaOutput": str(args.kaala_output.resolve()),
        "kaalaOutputSha256": sha256(args.kaala_output),
        "formulaOutput": str(args.formula_output.resolve()),
        "formulaOutputSha256": sha256(args.formula_output),
        "report": str(args.report.resolve()),
        "reportSha256": sha256(args.report),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
