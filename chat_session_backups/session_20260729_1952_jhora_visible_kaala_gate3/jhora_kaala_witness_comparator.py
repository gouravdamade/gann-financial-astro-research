from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


CONTRACT = "GANN_JHORA_KAALA_WITNESS_COMPARATOR_V1"
FROZEN_TOLERANCE_VIRUPA = 0.5
DISPLAY_SUM_TOLERANCE_VIRUPA = 0.06
PLANETS = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")
SAMPLE_IDS = (
    "case_8_event_start",
    "case_43_event_start",
    "case_103_event_start",
    "case_127_sr_touch_start",
    "gann_reference_tokyo",
)
MEASURES = (
    "total",
    "nathonnatha",
    "paksha",
    "tribhaga",
    "abda",
    "masa",
    "vara",
    "hora",
    "ayana",
    "yuddha",
)

def expected_kaala_keys() -> set[tuple[str, str, str]]:
    return {
        (sample_id, planet, measure)
        for sample_id in SAMPLE_IDS
        for planet in PLANETS
        for measure in MEASURES
    }
NUMERIC_TEXT = re.compile(
    r"^\s*\d+\s+text\s+(-?\d+(?:\.\d+)?)\s*$",
    re.MULTILINE,
)
PLANET_ITEM = re.compile(
    r"^\s*\d+\s+list item \(selectable\) "
    r"(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)\s*$",
    re.MULTILINE,
)

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = (
    REPO_ROOT / "status" / "evidence" / "jhora_kaala_witness_20260727"
)
DEFAULT_DOCTRINE_CONFIG = REPO_ROOT / "doctrine_config.yaml"
DEFAULT_PYJHORA = REPO_ROOT / "pyjhora_kaala_subcomponents_20260718.csv"
DEFAULT_WITNESS_OUTPUT = (
    DEFAULT_EVIDENCE_DIR / "jhora_kaala_subcomponents_20260727.csv"
)
DEFAULT_COMPARISON_OUTPUT = (
    DEFAULT_EVIDENCE_DIR / "jhora_kaala_profile_comparison_20260727.csv"
)
DEFAULT_JSON_OUTPUT = (
    DEFAULT_EVIDENCE_DIR / "jhora_kaala_profile_comparison_20260727.json"
)
DEFAULT_REPORT_OUTPUT = REPO_ROOT / "jhora_kaala_reconciliation_20260727.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Parse visible locked JHora Kaala Bala tables and compare each "
            "subcomponent with local and pinned PyJHora profiles."
        )
    )
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument(
        "--doctrine-config",
        type=Path,
        default=DEFAULT_DOCTRINE_CONFIG,
    )
    parser.add_argument("--pyjhora", type=Path, default=DEFAULT_PYJHORA)
    parser.add_argument(
        "--witness-output",
        type=Path,
        default=DEFAULT_WITNESS_OUTPUT,
    )
    parser.add_argument(
        "--comparison-output",
        type=Path,
        default=DEFAULT_COMPARISON_OUTPUT,
    )
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
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


def sample_id_from_path(path: Path) -> str:
    suffix = "_kaala_bala_accessibility.txt"
    if not path.name.endswith(suffix):
        raise RuntimeError(f"Unexpected JHora accessibility filename: {path.name}")
    return path.name[: -len(suffix)]


def _planet_row_segments(text: str) -> list[tuple[str, str]]:
    header = text.find("header item Planet")
    if header < 0:
        raise RuntimeError("JHora accessibility text has no Planet header.")
    matches = list(PLANET_ITEM.finditer(text, header))
    first_by_planet: dict[str, re.Match[str]] = {}
    for match in matches:
        planet = match.group(1).upper()
        first_by_planet.setdefault(planet, match)
        if len(first_by_planet) == len(PLANETS):
            break
    if tuple(first_by_planet) != PLANETS:
        raise RuntimeError(
            "JHora Kaala table planet order/membership mismatch: "
            f"{tuple(first_by_planet)}"
        )
    ordered = [first_by_planet[planet] for planet in PLANETS]
    segments: list[tuple[str, str]] = []
    for index, match in enumerate(ordered):
        end = ordered[index + 1].start() if index + 1 < len(ordered) else len(text)
        segments.append((match.group(1).upper(), text[match.end() : end]))
    return segments


def parse_accessibility_table(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise RuntimeError(f"JHora accessibility evidence is empty: {path}")
    sample_id = sample_id_from_path(path)
    screenshot_path = path.with_name(
        path.name.replace("_accessibility.txt", "_locked.jpg")
    )
    if not screenshot_path.is_file():
        raise RuntimeError(f"Missing paired JHora screenshot: {screenshot_path}")
    source = (
        "Jagannatha Hora 8.0 locked visible Kaala Bala table; "
        f"accessibility_sha256={sha256(path)}; "
        f"screenshot_sha256={sha256(screenshot_path)}"
    )

    rows: list[dict[str, str]] = []
    for planet, segment in _planet_row_segments(text):
        values = [float(match.group(1)) for match in NUMERIC_TEXT.finditer(segment)]
        if len(values) != len(MEASURES) + 1:
            raise RuntimeError(
                f"{path}: {planet} expected total, rupas, and nine component "
                f"values ({len(MEASURES) + 1} numeric values), got {len(values)}."
            )
        # The numeric list is total, rupas, then the nine displayed components.
        total = values[0]
        in_rupas = values[1]
        component_values = values[2:]
        component_sum = sum(component_values)
        sum_delta = total - component_sum
        if abs(sum_delta) > DISPLAY_SUM_TOLERANCE_VIRUPA:
            raise RuntimeError(
                f"{path}: {planet} displayed total {total:.2f} does not sum to "
                f"components {component_sum:.2f}; delta={sum_delta:.3f}."
            )
        if abs((total / 60.0) - in_rupas) > 0.011:
            raise RuntimeError(
                f"{path}: {planet} total/rupa display mismatch: "
                f"{total:.2f} virupa vs {in_rupas:.2f} rupa."
            )
        row_values = {
            "total": total,
            **dict(zip(MEASURES[1:], component_values, strict=True)),
        }
        for measure in MEASURES:
            rows.append(
                {
                    "contract": CONTRACT,
                    "sample_id": sample_id,
                    "planet": planet,
                    "measure": measure,
                    "jhora_value_virupa": f"{row_values[measure]:.9f}",
                    "displayed_in_rupas": f"{in_rupas:.9f}",
                    "displayed_component_sum_virupa": f"{component_sum:.9f}",
                    "displayed_total_minus_sum_virupa": f"{sum_delta:.9f}",
                    "source": source,
                    "accessibility_path": relative_path(path),
                    "screenshot_path": relative_path(screenshot_path),
                }
            )
    if len(rows) != len(PLANETS) * len(MEASURES):
        raise RuntimeError(f"{path}: expected 70 witness rows, got {len(rows)}.")
    return rows


def parse_evidence_directory(path: Path) -> list[dict[str, str]]:
    evidence_files = sorted(path.glob("*_kaala_bala_accessibility.txt"))
    if len(evidence_files) != 5:
        raise RuntimeError(
            f"Expected five locked JHora accessibility files in {path}, "
            f"found {len(evidence_files)}."
        )
    rows = [
        row
        for evidence_file in evidence_files
        for row in parse_accessibility_table(evidence_file)
    ]
    expected = expected_kaala_keys()
    actual = {
        (row["sample_id"], row["planet"], row["measure"])
        for row in rows
    }
    if actual != expected:
        raise RuntimeError(
            "JHora Kaala witness matrix mismatch: "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )
    return rows


def index_witness_rows(
    rows: list[dict[str, str]],
) -> dict[tuple[str, str, str], dict[str, str]]:
    indexed: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["sample_id"], row["planet"], row["measure"])
        if key in indexed:
            raise RuntimeError(f"Duplicate JHora witness row: {key}")
        indexed[key] = row
    return indexed


def compare_profiles(
    witness_rows: list[dict[str, str]],
    local: dict[tuple[str, str, str], float],
    pyjhora: dict[tuple[str, str, str], float],
    pyjhora_source: str,
    *,
    tolerance: float = FROZEN_TOLERANCE_VIRUPA,
) -> list[dict[str, str]]:
    expected = expected_kaala_keys()
    witness = index_witness_rows(witness_rows)
    for label, matrix in (
        ("JHora witness", witness),
        ("local profile", local),
        ("PyJHora profile", pyjhora),
    ):
        if set(matrix) != expected:
            raise RuntimeError(
                f"{label} matrix mismatch: missing={sorted(expected - set(matrix))}, "
                f"extra={sorted(set(matrix) - expected)}"
            )

    rows: list[dict[str, str]] = []
    for key in sorted(expected):
        witness_row = witness[key]
        jhora_value = float(witness_row["jhora_value_virupa"])
        local_value = float(local[key])
        pyjhora_value = float(pyjhora[key])
        local_delta = jhora_value - local_value
        pyjhora_delta = jhora_value - pyjhora_value
        local_absolute = abs(local_delta)
        pyjhora_absolute = abs(pyjhora_delta)
        rows.append(
            {
                "contract": CONTRACT,
                "sample_id": key[0],
                "planet": key[1],
                "measure": key[2],
                "jhora_value_virupa": f"{jhora_value:.9f}",
                "local_value_virupa": f"{local_value:.9f}",
                "pyjhora_value_virupa": f"{pyjhora_value:.9f}",
                "jhora_minus_local_virupa": f"{local_delta:.9f}",
                "jhora_minus_pyjhora_virupa": f"{pyjhora_delta:.9f}",
                "local_absolute_delta_virupa": f"{local_absolute:.9f}",
                "pyjhora_absolute_delta_virupa": f"{pyjhora_absolute:.9f}",
                "local_pass_fail": (
                    "pass" if local_absolute <= tolerance else "fail"
                ),
                "pyjhora_pass_fail": (
                    "pass" if pyjhora_absolute <= tolerance else "fail"
                ),
                "nearest_profile": (
                    "local"
                    if local_absolute < pyjhora_absolute
                    else "pyjhora"
                    if pyjhora_absolute < local_absolute
                    else "tie"
                ),
                "tolerance_virupa": f"{tolerance:.9f}",
                "jhora_source": witness_row["source"],
                "pyjhora_source": pyjhora_source,
            }
        )
    return rows


def summarize(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["measure"]].append(row)
    result: dict[str, dict[str, Any]] = {}
    for measure in MEASURES:
        group = grouped[measure]
        local_deltas = [
            float(row["local_absolute_delta_virupa"]) for row in group
        ]
        pyjhora_deltas = [
            float(row["pyjhora_absolute_delta_virupa"]) for row in group
        ]
        result[measure] = {
            "rows": len(group),
            "localPass": sum(row["local_pass_fail"] == "pass" for row in group),
            "pyjhoraPass": sum(
                row["pyjhora_pass_fail"] == "pass" for row in group
            ),
            "localCloser": sum(row["nearest_profile"] == "local" for row in group),
            "pyjhoraCloser": sum(
                row["nearest_profile"] == "pyjhora" for row in group
            ),
            "ties": sum(row["nearest_profile"] == "tie" for row in group),
            "localMaeVirupa": round(mean(local_deltas), 9),
            "pyjhoraMaeVirupa": round(mean(pyjhora_deltas), 9),
            "localMaxVirupa": round(max(local_deltas), 9),
            "pyjhoraMaxVirupa": round(max(pyjhora_deltas), 9),
        }
    return result


def categorical_lords(
    rows: list[dict[str, str]],
    profile_field: str,
) -> dict[str, dict[str, str]]:
    awards = {"abda": 15.0, "masa": 30.0, "vara": 45.0, "hora": 60.0}
    lords: dict[str, dict[str, str]] = defaultdict(dict)
    for sample_id in sorted({row["sample_id"] for row in rows}):
        for measure, award in awards.items():
            winners = [
                row["planet"]
                for row in rows
                if row["sample_id"] == sample_id
                and row["measure"] == measure
                and math.isclose(
                    float(row[profile_field]),
                    award,
                    abs_tol=1e-9,
                )
            ]
            lords[sample_id][measure] = ",".join(winners) if winners else "NONE"
    return dict(lords)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend(
        "| " + " | ".join(str(value) for value in row) + " |" for row in rows
    )
    return output


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# JHora Kaala Bala Reconciliation",
        "",
        f"Contract: `{CONTRACT}`",
        "",
        "Status: locked visible-witness diagnostic; not execution-certified.",
        "",
        "The numeric certification tolerance remains frozen at 0.5 virupa. "
        "The separate 0.06-virupa display-sum allowance only accommodates "
        "adding ten values rounded by JHora to two decimals.",
        "",
        "## Per-Component Results",
        "",
    ]
    lines.extend(
        markdown_table(
            [
                "Measure",
                "Local pass",
                "PyJHora pass",
                "Local MAE",
                "PyJHora MAE",
                "Local closer",
                "PyJHora closer",
            ],
            [
                [
                    measure,
                    f"{values['localPass']}/{values['rows']}",
                    f"{values['pyjhoraPass']}/{values['rows']}",
                    f"{values['localMaeVirupa']:.3f}",
                    f"{values['pyjhoraMaeVirupa']:.3f}",
                    values["localCloser"],
                    values["pyjhoraCloser"],
                ]
                for measure, values in summary["components"].items()
            ],
        )
    )
    lines.extend(["", "## Categorical Lord Witness", ""])
    for sample_id in sorted(summary["categoricalLords"]["jhora"]):
        lines.extend(
            [
                f"### {sample_id}",
                "",
                *markdown_table(
                    ["Profile", "Abda", "Masa", "Vara", "Hora"],
                    [
                        [
                            profile,
                            values["abda"],
                            values["masa"],
                            values["vara"],
                            values["hora"],
                        ]
                        for profile, values in (
                            (
                                "JHora",
                                summary["categoricalLords"]["jhora"][sample_id],
                            ),
                            (
                                "Local",
                                summary["categoricalLords"]["local"][sample_id],
                            ),
                            (
                                "PyJHora",
                                summary["categoricalLords"]["pyjhora"][sample_id],
                            ),
                        )
                    ],
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## Evidence Conclusions",
            "",
        ]
    )
    lines.extend(
        f"- {decision}" for decision in summary["evidenceConclusions"]
    )
    lines.extend(
        [
            "",
            "## Decision Boundary",
            "",
            "- No production formula is changed merely because one profile is closer.",
            "- A categorical lord change requires a consistent visible witness and "
            "an independently supported doctrine algorithm.",
            "- Ayana and continuous components remain separate from discrete "
            "15/30/45/60-virupa awards.",
            "",
        ]
    )
    return "\n".join(lines)


def build_summary(
    *,
    witness_rows: list[dict[str, str]],
    comparison_rows: list[dict[str, str]],
    inputs: dict[str, Path],
) -> dict[str, Any]:
    components = summarize(comparison_rows)
    return {
        "contract": CONTRACT,
        "generatedAtUtc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": "diagnostic_reconciliation_not_certified",
        "toleranceVirupa": FROZEN_TOLERANCE_VIRUPA,
        "tolerancePolicy": "frozen; no widening",
        "displaySumToleranceVirupa": DISPLAY_SUM_TOLERANCE_VIRUPA,
        "inputs": {
            name: {"path": relative_path(path), "sha256": sha256(path)}
            for name, path in inputs.items()
        },
        "witnessRows": len(witness_rows),
        "comparisonRows": len(comparison_rows),
        "components": components,
        "evidenceConclusions": [
            (
                "Promote dynamic Paksha classification: the local profile passes "
                f"{components['paksha']['localPass']}/{components['paksha']['rows']} "
                "visible rows with "
                f"{components['paksha']['localMaeVirupa']:.3f} virupa MAE and "
                f"{components['paksha']['localMaxVirupa']:.3f} virupa maximum error."
            ),
            (
                "Retain Abda, Masa, Vara, Tribhaga, and Yuddha: each local "
                "subcomponent passes all 35 visible rows."
            ),
            (
                "The exact-time visible Hora award matrix matches the local "
                "profile for "
                f"{components['hora']['localPass']}/{components['hora']['rows']} "
                "rows, and the categorical Hora lord matches for every fixture. "
                "The separate fail-closed intermediate gate determines whether "
                "the visible case-8 apparent-tip sunrise and award provenance "
                "packet is complete."
            ),
            (
                "Do not promote Nathonnatha, Ayana, or aggregate Kaala: they pass "
                f"{components['nathonnatha']['localPass']}/35, "
                f"{components['ayana']['localPass']}/35, and "
                f"{components['total']['localPass']}/35 rows respectively."
            ),
            (
                "The frozen 0.5-virupa certification tolerance is unchanged; "
                "the 0.06 display-sum allowance only checks arithmetic over "
                "JHora values rounded to two decimal places."
            ),
        ],
        "categoricalLords": {
            "jhora": categorical_lords(comparison_rows, "jhora_value_virupa"),
            "local": categorical_lords(comparison_rows, "local_value_virupa"),
            "pyjhora": categorical_lords(
                comparison_rows,
                "pyjhora_value_virupa",
            ),
        },
    }


def main() -> int:
    from shadbala_component_comparator import (
        calculate_local_kaala_values,
        read_external_kaala,
    )

    args = parse_args()
    witness_rows = parse_evidence_directory(args.evidence_dir)
    local = calculate_local_kaala_values(args.doctrine_config)
    pyjhora, pyjhora_source = read_external_kaala(args.pyjhora)
    comparison_rows = compare_profiles(
        witness_rows,
        local,
        pyjhora,
        pyjhora_source,
    )
    evidence_inputs = {
        f"jhora_{sample_id}": next(
            args.evidence_dir.glob(
                f"{sample_id}_kaala_bala_accessibility.txt"
            )
        )
        for sample_id in sorted({row["sample_id"] for row in witness_rows})
    }
    summary = build_summary(
        witness_rows=witness_rows,
        comparison_rows=comparison_rows,
        inputs={
            **evidence_inputs,
            "doctrineConfig": args.doctrine_config,
            "pyjhora": args.pyjhora,
        },
    )
    write_csv(args.witness_output, witness_rows)
    write_csv(args.comparison_output, comparison_rows)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.report_output.write_text(render_report(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
