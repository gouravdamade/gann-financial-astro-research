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
from pyjhora_external_strength_export import SHADBALA_COMPONENTS
from strict_shadbala_doctrine import components_for_body


COMPARATOR_CONTRACT = "GANN_SHADBALA_COMPONENT_COMPARATOR_V2"
LOCAL_COMPONENT_FIELDS = {
    "sthana": "sthana_comparator_virupa",
    "kaala": "kaala_9_virupa",
    "dig": "dig_virupa",
    "chesta": "chesta_virupa",
    "naisargika": "naisargika_virupa",
    "drik": "drik_virupa",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare local Shadbala components with a pinned PyJHora export."
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
        "--output",
        type=Path,
        default=Path(r"D:\PycharmProjects\shadbala_component_residuals_20260718.csv"),
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


def calculate_local_component_values(
    config_path: Path,
) -> dict[tuple[str, str, str], float]:
    config = load_doctrine_config(config_path)
    configure_swiss_ephemeris_sidereal(swe, config)
    values: dict[tuple[str, str, str], float] = {}
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
        houses = sidereal_house_cusps(jd_ut, sample.latitude, sample.longitude)
        asc_lon = houses[1]
        for planet in CLASSICAL_PLANETS:
            components = components_for_body(
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
            for component, field in LOCAL_COMPONENT_FIELDS.items():
                value = float(components[field])
                if not math.isfinite(value):
                    raise RuntimeError(
                        f"Non-finite local {component} value for {sample.sample_id}/{planet}."
                    )
                values[(sample.sample_id, planet, component)] = value
    return values


def read_external_components(
    path: Path,
) -> tuple[dict[tuple[str, str, str], float], str]:
    values: dict[tuple[str, str, str], float] = {}
    source = ""
    with path.open(newline="", encoding="utf-8") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            key = (
                str(row.get("sample_id") or "").strip(),
                str(row.get("planet") or "").strip().upper(),
                str(row.get("component") or "").strip().lower(),
            )
            if key in values:
                raise RuntimeError(f"Duplicate external component row {row_number}: {key}")
            try:
                value = float(str(row.get("external_value_virupa") or "").strip())
            except ValueError as exc:
                raise RuntimeError(
                    f"Invalid external component value at row {row_number}: {key}"
                ) from exc
            if not math.isfinite(value):
                raise RuntimeError(f"Non-finite external component at row {row_number}: {key}")
            values[key] = value
            row_source = str(row.get("source") or "").strip()
            if not row_source:
                raise RuntimeError(f"Missing external source at row {row_number}: {key}")
            if source and row_source != source:
                raise RuntimeError("External component rows contain mixed source declarations.")
            source = row_source
    return values, source


def expected_component_keys() -> set[tuple[str, str, str]]:
    return {
        (sample.sample_id, planet, component)
        for sample in SAMPLES
        for planet in CLASSICAL_PLANETS
        for component in SHADBALA_COMPONENTS
    }


def compare_component_matrices(
    local: dict[tuple[str, str, str], float],
    external: dict[tuple[str, str, str], float],
    *,
    tolerance: float,
    source: str,
) -> list[dict[str, str]]:
    expected = expected_component_keys()
    for label, matrix in (("local", local), ("external", external)):
        if set(matrix) != expected:
            missing = sorted(expected - set(matrix))
            extra = sorted(set(matrix) - expected)
            raise RuntimeError(f"{label} component matrix mismatch: missing={missing}, extra={extra}")
    rows: list[dict[str, str]] = []
    for key in sorted(expected):
        local_value = float(local[key])
        external_value = float(external[key])
        signed_delta = local_value - external_value
        absolute_delta = abs(signed_delta)
        rows.append(
            {
                "sample_id": key[0],
                "planet": key[1],
                "component": key[2],
                "local_value_virupa": f"{local_value:.9f}",
                "external_value_virupa": f"{external_value:.9f}",
                "signed_delta_virupa": f"{signed_delta:.9f}",
                "absolute_delta_virupa": f"{absolute_delta:.9f}",
                "tolerance_virupa": f"{float(tolerance):.9f}",
                "pass_fail": "pass" if absolute_delta <= tolerance else "fail",
                "external_source": source,
            }
        )
    return rows


def residual_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    groups: dict[str, list[float]] = defaultdict(list)
    pass_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        component = row["component"]
        groups[component].append(float(row["absolute_delta_virupa"]))
        pass_counts[component] += row["pass_fail"] == "pass"
    return {
        component: {
            "rows": len(values),
            "pass": pass_counts[component],
            "fail": len(values) - pass_counts[component],
            "meanAbsoluteResidualVirupa": sum(values) / len(values),
            "maxAbsoluteResidualVirupa": max(values),
        }
        for component, values in sorted(groups.items())
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    summary: dict[str, Any],
    *,
    external_path: Path,
    source: str,
) -> None:
    worst = sorted(
        rows,
        key=lambda row: float(row["absolute_delta_virupa"]),
        reverse=True,
    )[:15]
    lines = [
        "# Shadbala Component Reconciliation",
        "",
        f"Contract: `{COMPARATOR_CONTRACT}`",
        "",
        "This is a diagnostic Tier B comparison. It does not certify a doctrine or",
        "authorize execution. Source-profile formulas remain distinct from named",
        "comparator compatibility profiles.",
        "",
        f"- External matrix: `{external_path}`",
        f"- External SHA-256: `{sha256(external_path)}`",
        f"- External source: `{source}`",
        f"- Rows: `{len(rows)}`",
        f"- Passed: `{sum(row['pass_fail'] == 'pass' for row in rows)}`",
        f"- Failed: `{sum(row['pass_fail'] == 'fail' for row in rows)}`",
        "",
        "## Component Summary",
        "",
        "| Component | Pass | Fail | Mean absolute residual | Maximum residual |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for component, values in summary.items():
        lines.append(
            f"| {component} | {values['pass']} | {values['fail']} | "
            f"{values['meanAbsoluteResidualVirupa']:.6f} | "
            f"{values['maxAbsoluteResidualVirupa']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Largest Residuals",
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
    if any(
        row["sample_id"] == "gann_reference_tokyo"
        and row["planet"] == "JUPITER"
        and row["component"] == "sthana"
        and row["pass_fail"] == "fail"
        for row in rows
    ):
        lines.extend(
            [
                "",
                "## Boundary Sensitivity",
                "",
                "- The sole Sthana compatibility failure is the 1889 Tokyo Jupiter fixture.",
                "  Local Swiss Ephemeris places Jupiter at 249.992006 degrees while PyJHora",
                "  places it at 250.002277 degrees. That 0.010271-degree difference crosses",
                "  an exact divisional boundary and changes D3, D9, D12, and D30 assignments.",
                "  It is retained as a boundary-instability witness, not forced to pass.",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation Lock",
            "",
            "- A failed component identifies a formula/profile disagreement; it is not repaired by widening tolerance.",
            "- Sthana uses the named PyJHora compatibility profile here; production retains the BPHS source weights and degree-bounded D1 Moolatrikona.",
            "- Dig compares against PyJHora `_dig_bala(method=2)`, its bounded circular-distance implementation, not the package default method that can exceed 60 virupa.",
            "- Kaala and Chesta residuals remain diagnostic because the production source profiles intentionally reject known unbounded or structurally incomplete comparator behavior.",
            "- PyJHora is a secondary comparator. Jagannatha Hora or a reproducible worked example remains required.",
            "- Where legitimate source variants disagree, preserve separate named profiles instead of silently blending them.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.tolerance < 0:
        raise ValueError("Tolerance must be non-negative.")
    local = calculate_local_component_values(args.doctrine_config)
    external, source = read_external_components(args.external_components)
    rows = compare_component_matrices(
        local,
        external,
        tolerance=args.tolerance,
        source=source,
    )
    summary = residual_summary(rows)
    write_csv(args.output, rows)
    write_report(
        args.report,
        rows,
        summary,
        external_path=args.external_components,
        source=source,
    )
    print(
        json.dumps(
            {
                "contract": COMPARATOR_CONTRACT,
                "rows": len(rows),
                "pass": sum(row["pass_fail"] == "pass" for row in rows),
                "fail": sum(row["pass_fail"] == "fail" for row in rows),
                "summary": summary,
                "output": str(args.output.resolve()),
                "outputSha256": sha256(args.output),
                "report": str(args.report.resolve()),
                "reportSha256": sha256(args.report),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
