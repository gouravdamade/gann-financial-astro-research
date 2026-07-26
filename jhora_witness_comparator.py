from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from astro_function_certification import append_compare_note, compare_external_value
from jhora_witness_protocol import (
    JHORA_EXE_SHA256,
    JHORA_VERSION,
    WITNESS_CONTRACT,
    read_csv,
    sha256,
    validate_witness_rows,
)
from pyjhora_external_strength_export import FIXTURES, PLANETS, SHADBALA_COMPONENTS


REPO_ROOT = Path(__file__).resolve().parent
EVIDENCE_DIR = REPO_ROOT / "status" / "evidence" / "jhora_shadbala_20260723"
DEFAULT_WITNESS = (
    EVIDENCE_DIR / "jhora_shadbala_witness_completed_20260726.csv"
)
DEFAULT_COMPONENTS = REPO_ROOT / "pyjhora_shadbala_components_20260718.csv"
DEFAULT_TOTALS = REPO_ROOT / "pyjhora_external_strength_values_20260718.csv"
DEFAULT_DRIK_TEMPLATE = (
    REPO_ROOT / "jhora_drik_independent_validation_template_20260718.csv"
)
DEFAULT_COMPARISON_CSV = (
    EVIDENCE_DIR / "jhora_pyjhora_component_comparison_20260726.csv"
)
DEFAULT_COMPARISON_JSON = (
    EVIDENCE_DIR / "jhora_pyjhora_component_comparison_20260726.json"
)
DEFAULT_DRIK_OUTPUT = (
    EVIDENCE_DIR / "jhora_drik_independent_validation_values_20260726.csv"
)
FROZEN_TOLERANCE_VIRUPA = 0.5
MEASURES = SHADBALA_COMPONENTS + ("total",)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the locked JHora Shadbala witness with the pinned PyJHora "
            "export and build the independent Drik gate input."
        )
    )
    parser.add_argument("--witness", type=Path, default=DEFAULT_WITNESS)
    parser.add_argument("--components", type=Path, default=DEFAULT_COMPONENTS)
    parser.add_argument("--totals", type=Path, default=DEFAULT_TOTALS)
    parser.add_argument("--drik-template", type=Path, default=DEFAULT_DRIK_TEMPLATE)
    parser.add_argument("--comparison-csv", type=Path, default=DEFAULT_COMPARISON_CSV)
    parser.add_argument(
        "--comparison-json", type=Path, default=DEFAULT_COMPARISON_JSON
    )
    parser.add_argument("--drik-output", type=Path, default=DEFAULT_DRIK_OUTPUT)
    return parser.parse_args()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def _expected_keys() -> set[tuple[str, str, str]]:
    return {
        (fixture.sample_id, planet, measure)
        for fixture in FIXTURES
        for planet in PLANETS
        for measure in MEASURES
    }


def _pyjhora_values(
    components_path: Path,
    totals_path: Path,
) -> dict[tuple[str, str, str], tuple[float, str]]:
    values: dict[tuple[str, str, str], tuple[float, str]] = {}
    component_rows = _read_csv(components_path)
    for row_number, row in enumerate(component_rows, start=2):
        key = (
            row["sample_id"].strip(),
            row["planet"].strip().upper(),
            row["component"].strip().lower(),
        )
        if key in values:
            raise ValueError(f"{components_path}: row {row_number}: duplicate {key}")
        values[key] = (
            float(row["external_value_virupa"]),
            row["source"].strip(),
        )

    total_prefix = "shadbala_implemented_total_virupa."
    for row_number, row in enumerate(_read_csv(totals_path), start=2):
        feature_key = row["feature_key"].strip()
        if not feature_key.startswith(total_prefix):
            continue
        key = (
            row["sample_id"].strip(),
            feature_key.removeprefix(total_prefix).upper(),
            "total",
        )
        if key in values:
            raise ValueError(f"{totals_path}: row {row_number}: duplicate {key}")
        values[key] = (
            float(row["external_expected_value"]),
            row["external_source"].strip(),
        )

    expected = _expected_keys()
    if set(values) != expected:
        raise ValueError(
            "PyJHora comparison matrix mismatch: "
            f"missing={sorted(expected - set(values))}, "
            f"extra={sorted(set(values) - expected)}"
        )
    return values


def build_comparison_rows(
    witness_path: Path = DEFAULT_WITNESS,
    components_path: Path = DEFAULT_COMPONENTS,
    totals_path: Path = DEFAULT_TOTALS,
) -> list[dict[str, str]]:
    witness_rows = read_csv(witness_path)
    issues = validate_witness_rows(witness_rows)
    if issues:
        raise ValueError(f"locked JHora witness is invalid: {issues}")
    pyjhora = _pyjhora_values(components_path, totals_path)

    rows: list[dict[str, str]] = []
    for witness in witness_rows:
        key = (
            witness["sample_id"].strip(),
            witness["planet"].strip().upper(),
            witness["measure"].strip().lower(),
        )
        jhora_value = float(witness["jhora_value_virupa"])
        pyjhora_value, pyjhora_source = pyjhora[key]
        signed_delta = jhora_value - pyjhora_value
        absolute_delta = abs(signed_delta)
        rows.append(
            {
                "contract": "GANN_JHORA_PYJHORA_COMPARISON_V1",
                "sample_id": key[0],
                "planet": key[1],
                "measure": key[2],
                "jhora_value_virupa": f"{jhora_value:.9f}",
                "pyjhora_value_virupa": f"{pyjhora_value:.9f}",
                "signed_delta_virupa": f"{signed_delta:.9f}",
                "absolute_delta_virupa": f"{absolute_delta:.9f}",
                "tolerance_virupa": f"{FROZEN_TOLERANCE_VIRUPA:.1f}",
                "pass_fail": (
                    "pass"
                    if absolute_delta <= FROZEN_TOLERANCE_VIRUPA
                    else "fail"
                ),
                "jhora_evidence_path": witness["evidence_path"],
                "jhora_evidence_sha256": witness["evidence_sha256"],
                "pyjhora_source": pyjhora_source,
                "notes": (
                    "Locked independent JHora GUI witness versus pinned PyJHora "
                    "Tier B export; diagnostic comparison only; no tolerance widening."
                ),
            }
        )
    if len(rows) != len(_expected_keys()):
        raise ValueError(f"comparison row count mismatch: {len(rows)}")
    return rows


def comparison_summary(
    rows: list[dict[str, str]],
    witness_path: Path = DEFAULT_WITNESS,
    components_path: Path = DEFAULT_COMPONENTS,
    totals_path: Path = DEFAULT_TOTALS,
) -> dict[str, object]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["measure"]].append(row)

    def summarize(group: list[dict[str, str]]) -> dict[str, object]:
        deltas = [float(row["absolute_delta_virupa"]) for row in group]
        passes = sum(row["pass_fail"] == "pass" for row in group)
        return {
            "rows": len(group),
            "pass": passes,
            "fail": len(group) - passes,
            "meanAbsoluteDeltaVirupa": round(mean(deltas), 9),
            "maxAbsoluteDeltaVirupa": round(max(deltas), 9),
        }

    overall = summarize(rows)
    return {
        "contract": "GANN_JHORA_PYJHORA_COMPARISON_V1",
        "generatedAtUtc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": "diagnostic_disagreement",
        "toleranceVirupa": FROZEN_TOLERANCE_VIRUPA,
        "tolerancePolicy": "frozen; not widened for certification",
        "jhora": {
            "contract": WITNESS_CONTRACT,
            "version": JHORA_VERSION,
            "executableSha256": JHORA_EXE_SHA256,
            "witnessPath": _relative(witness_path),
            "witnessSha256": sha256(witness_path),
        },
        "pyjhora": {
            "componentsPath": _relative(components_path),
            "componentsSha256": sha256(components_path),
            "totalsPath": _relative(totals_path),
            "totalsSha256": sha256(totals_path),
        },
        "overall": overall,
        "byMeasure": {
            measure: summarize(grouped[measure])
            for measure in MEASURES
        },
        "certificationInterpretation": (
            "The locked independent JHora witness does not certify the PyJHora "
            "profile. Component differences require doctrine/profile "
            "reconciliation; they must not be hidden by tolerance widening."
        ),
    }


def build_independent_drik_rows(
    witness_path: Path = DEFAULT_WITNESS,
    template_path: Path = DEFAULT_DRIK_TEMPLATE,
) -> list[dict[str, str]]:
    witness_rows = read_csv(witness_path)
    issues = validate_witness_rows(witness_rows)
    if issues:
        raise ValueError(f"locked JHora witness is invalid: {issues}")
    witness_drik = {
        (row["sample_id"], row["planet"]): row
        for row in witness_rows
        if row["measure"] == "drik"
    }
    expected_keys = {
        (fixture.sample_id, planet)
        for fixture in FIXTURES
        for planet in PLANETS
    }
    if set(witness_drik) != expected_keys:
        raise ValueError("JHora Drik witness matrix is incomplete")

    template_rows = _read_csv(template_path)
    if len(template_rows) != len(expected_keys):
        raise ValueError(
            f"independent Drik template row count mismatch: {len(template_rows)}"
        )
    witness_digest = sha256(witness_path)
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row_number, template in enumerate(template_rows, start=2):
        feature_key = template["feature_key"].strip()
        prefix = "drik_bala_virupa."
        if not feature_key.startswith(prefix):
            raise ValueError(
                f"{template_path}: row {row_number}: unexpected feature {feature_key}"
            )
        key = (
            template["sample_id"].strip(),
            feature_key.removeprefix(prefix).upper(),
        )
        if key in seen:
            raise ValueError(f"{template_path}: row {row_number}: duplicate {key}")
        seen.add(key)
        witness = witness_drik[key]
        expected_value = witness["jhora_value_virupa"]
        pass_fail, compare_note = compare_external_value(
            feature_key,
            template["local_value"],
            expected_value,
        )
        provenance = (
            f"Independent Jagannatha Hora {JHORA_VERSION} locked GUI witness; "
            f"contract={WITNESS_CONTRACT}; "
            f"witness={_relative(witness_path)}; "
            f"witness_sha256={witness_digest}; "
            f"row_evidence={witness['evidence_path']}; "
            f"row_evidence_sha256={witness['evidence_sha256']}"
        )
        rows.append(
            {
                "gate": template["gate"],
                "sample_id": key[0],
                "feature_key": feature_key,
                "local_value": template["local_value"],
                "external_expected_value": expected_value,
                "external_source": provenance,
                "pass_fail": pass_fail,
                "notes": append_compare_note(
                    "Independent JHora value entered from locked manual witness; "
                    "no PyJHora values used and no tolerance widening.",
                    compare_note,
                ),
            }
        )
    if seen != expected_keys:
        raise ValueError(
            "independent Drik output matrix mismatch: "
            f"missing={sorted(expected_keys - seen)}, "
            f"extra={sorted(seen - expected_keys)}"
        )
    return rows


def main() -> int:
    args = parse_args()
    comparison_rows = build_comparison_rows(
        args.witness,
        args.components,
        args.totals,
    )
    summary = comparison_summary(
        comparison_rows,
        args.witness,
        args.components,
        args.totals,
    )
    drik_rows = build_independent_drik_rows(args.witness, args.drik_template)

    _write_csv(args.comparison_csv, comparison_rows)
    args.comparison_json.parent.mkdir(parents=True, exist_ok=True)
    args.comparison_json.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_csv(args.drik_output, drik_rows)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "comparison": summary["overall"],
                "byMeasure": summary["byMeasure"],
                "comparisonCsv": str(args.comparison_csv.resolve()),
                "comparisonJson": str(args.comparison_json.resolve()),
                "independentDrik": {
                    "rows": len(drik_rows),
                    "pass": sum(row["pass_fail"] == "pass" for row in drik_rows),
                    "fail": sum(row["pass_fail"] == "fail" for row in drik_rows),
                    "output": str(args.drik_output.resolve()),
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
