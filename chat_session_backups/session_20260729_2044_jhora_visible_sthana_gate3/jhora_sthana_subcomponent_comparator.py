from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from jhora_sthana_subcomponent_witness_protocol import (
    DEFAULT_TOP_LEVEL_WITNESS,
    STHANA_SUBCOMPONENTS,
    WITNESS_CONTRACT,
    read_csv,
    sha256,
    validate_against_top_level_sthana,
    validate_witness_rows,
)
from jhora_witness_protocol import FIXTURES, PLANETS
from shadbala_component_comparator import (
    calculate_sthana_subcomponent_values,
)
from strict_shadbala_doctrine import (
    SAPTAVARGAJA_JHORA_VISIBLE_PROFILE,
    SAPTAVARGAJA_PYJHORA_PROFILE,
    SAPTAVARGAJA_SOURCE_PROFILE,
)


CONTRACT = "GANN_JHORA_STHANA_SUBCOMPONENT_COMPARATOR_V1"
FROZEN_TOLERANCE_VIRUPA = 0.5
PROFILE_IDS = {
    "source": SAPTAVARGAJA_SOURCE_PROFILE,
    "pyjhora": SAPTAVARGAJA_PYJHORA_PROFILE,
    "jhora_visible": SAPTAVARGAJA_JHORA_VISIBLE_PROFILE,
}
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = (
    REPO_ROOT / "status" / "evidence" / "jhora_sthana_subcomponents_20260729"
)
DEFAULT_WITNESS = (
    DEFAULT_EVIDENCE_DIR
    / "jhora_sthana_subcomponent_witness_completed_20260729.csv"
)
DEFAULT_COMPARISON = (
    DEFAULT_EVIDENCE_DIR
    / "jhora_sthana_subcomponent_profile_comparison_20260729.csv"
)
DEFAULT_SUMMARY = (
    DEFAULT_EVIDENCE_DIR
    / "jhora_sthana_subcomponent_profile_comparison_20260729.json"
)
DEFAULT_REPORT = REPO_ROOT / "jhora_sthana_reconciliation_20260729.md"
DEFAULT_DOCTRINE_CONFIG = REPO_ROOT / "doctrine_config.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the locked visible JHora Sthana breakdown with the "
            "classical-source, PyJHora, and JHora-visible local profiles."
        )
    )
    parser.add_argument("--witness", type=Path, default=DEFAULT_WITNESS)
    parser.add_argument(
        "--top-level-witness",
        type=Path,
        default=DEFAULT_TOP_LEVEL_WITNESS,
    )
    parser.add_argument(
        "--doctrine-config",
        type=Path,
        default=DEFAULT_DOCTRINE_CONFIG,
    )
    parser.add_argument("--comparison", type=Path, default=DEFAULT_COMPARISON)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def expected_keys() -> set[tuple[str, str, str]]:
    return {
        (fixture.sample_id, planet, component)
        for fixture in FIXTURES
        for planet in PLANETS
        for component in STHANA_SUBCOMPONENTS
    }


def witness_matrix(
    witness_path: Path,
    top_level_path: Path,
) -> tuple[
    dict[tuple[str, str, str], float],
    dict[tuple[str, str, str], dict[str, str]],
]:
    rows = read_csv(witness_path)
    issues = validate_witness_rows(rows)
    issues.extend(
        validate_against_top_level_sthana(rows, read_csv(top_level_path))
    )
    if issues:
        raise RuntimeError(f"Visible JHora Sthana witness is invalid: {issues}")
    values: dict[tuple[str, str, str], float] = {}
    evidence: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (
            row["sample_id"].strip(),
            row["planet"].strip().upper(),
            row["sthana_subcomponent"].strip().lower(),
        )
        values[key] = float(row["jhora_value_virupa"])
        evidence[key] = row
    if set(values) != expected_keys():
        raise RuntimeError("Visible JHora Sthana witness matrix is incomplete.")
    return values, evidence


def build_comparison_rows(
    witness_path: Path = DEFAULT_WITNESS,
    top_level_path: Path = DEFAULT_TOP_LEVEL_WITNESS,
    doctrine_config: Path = DEFAULT_DOCTRINE_CONFIG,
) -> list[dict[str, str]]:
    witness, evidence = witness_matrix(witness_path, top_level_path)
    profiles = {
        label: calculate_sthana_subcomponent_values(
            doctrine_config,
            profile=profile_id,
        )
        for label, profile_id in PROFILE_IDS.items()
    }
    for label, values in profiles.items():
        if set(values) != expected_keys():
            raise RuntimeError(f"{label} Sthana matrix is incomplete.")

    rows: list[dict[str, str]] = []
    for key in sorted(expected_keys()):
        external = witness[key]
        row: dict[str, str] = {
            "contract": CONTRACT,
            "sample_id": key[0],
            "planet": key[1],
            "sthana_subcomponent": key[2],
            "jhora_value_virupa": f"{external:.9f}",
            "tolerance_virupa": f"{FROZEN_TOLERANCE_VIRUPA:.9f}",
            "jhora_evidence_path": evidence[key]["evidence_path"],
            "jhora_evidence_sha256": evidence[key]["evidence_sha256"],
        }
        nearest_label = ""
        nearest_delta: float | None = None
        for label, values in profiles.items():
            local = float(values[key])
            signed = local - external
            absolute = abs(signed)
            row[f"{label}_profile_id"] = PROFILE_IDS[label]
            row[f"{label}_value_virupa"] = f"{local:.9f}"
            row[f"{label}_signed_delta_virupa"] = f"{signed:.9f}"
            row[f"{label}_absolute_delta_virupa"] = f"{absolute:.9f}"
            row[f"{label}_pass_fail"] = (
                "pass"
                if absolute <= FROZEN_TOLERANCE_VIRUPA
                else "fail"
            )
            if nearest_delta is None or absolute < nearest_delta:
                nearest_label = label
                nearest_delta = absolute
            elif absolute == nearest_delta:
                nearest_label = "tie"
        row["nearest_profile"] = nearest_label
        rows.append(row)
    return rows


def _metric(values: list[float], passes: int) -> dict[str, Any]:
    return {
        "rows": len(values),
        "pass": passes,
        "fail": len(values) - passes,
        "maeVirupa": round(mean(values), 9),
        "maxErrorVirupa": round(max(values), 9),
    }


def summarize_profile(
    rows: list[dict[str, str]],
    label: str,
) -> dict[str, Any]:
    components: dict[str, dict[str, Any]] = {}
    for component in STHANA_SUBCOMPONENTS:
        group = [
            row
            for row in rows
            if row["sthana_subcomponent"] == component
        ]
        deltas = [
            float(row[f"{label}_absolute_delta_virupa"])
            for row in group
        ]
        passes = sum(
            row[f"{label}_pass_fail"] == "pass" for row in group
        )
        components[component] = _metric(deltas, passes)

    observed: dict[tuple[str, str], float] = defaultdict(float)
    external: dict[tuple[str, str], float] = defaultdict(float)
    for row in rows:
        key = (row["sample_id"], row["planet"])
        observed[key] += float(row[f"{label}_value_virupa"])
        external[key] += float(row["jhora_value_virupa"])
    total_deltas = [
        abs(observed[key] - external[key]) for key in sorted(external)
    ]
    total_passes = sum(
        delta <= FROZEN_TOLERANCE_VIRUPA for delta in total_deltas
    )
    return {
        "profileId": PROFILE_IDS[label],
        "components": components,
        "total": _metric(total_deltas, total_passes),
    }


def build_summary(
    rows: list[dict[str, str]],
    *,
    witness_path: Path,
    top_level_path: Path,
    doctrine_config: Path,
) -> dict[str, Any]:
    profiles = {
        label: summarize_profile(rows, label) for label in PROFILE_IDS
    }
    return {
        "contract": CONTRACT,
        "generatedAtUtc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": "visible_witness_reconciled_diagnostic_only",
        "witnessContract": WITNESS_CONTRACT,
        "witnessRows": len(rows),
        "comparisonRows": len(rows),
        "toleranceVirupa": FROZEN_TOLERANCE_VIRUPA,
        "tolerancePolicy": "frozen; no widening",
        "productionProfile": SAPTAVARGAJA_SOURCE_PROFILE,
        "productionChangeAllowed": False,
        "sourceCertified": False,
        "financiallyValidated": False,
        "executionAllowed": False,
        "profiles": profiles,
        "inputs": {
            "witness": {
                "path": str(witness_path.resolve()),
                "sha256": sha256(witness_path),
            },
            "topLevelWitness": {
                "path": str(top_level_path.resolve()),
                "sha256": sha256(top_level_path),
            },
            "doctrineConfig": {
                "path": str(doctrine_config.resolve()),
                "sha256": sha256(doctrine_config),
            },
        },
        "evidenceConclusions": [
            (
                "Uchcha, Ojayugma, Kendradi, and Drekkana each match visible "
                "JHora in all 35 locked rows."
            ),
            (
                "The BPHS-labeled source Saptavargaja weight profile remains "
                "a distinct doctrine and does not match the JHora table."
            ),
            (
                "The PyJHora profile fails one Saturn row because it treats "
                "all Aquarius as Moolatrikona instead of respecting Saturn's "
                "degree-bounded Moolatrikona range."
            ),
            (
                "The named JHora-visible profile combines JHora's observed "
                "weights with degree-bounded D1 Moolatrikona and matches the "
                "complete visible matrix. It remains diagnostic only."
            ),
        ],
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# JHora Sthana Bala Reconciliation",
        "",
        f"Contract: `{CONTRACT}`",
        "",
        "Status: visible-witness diagnostic; production and execution remain locked.",
        "",
        "The numeric tolerance is frozen at 0.5 virupa. No tolerance was widened",
        "and no component was inferred from a top-level residual.",
        "",
        "## Profile Results",
        "",
        "| Profile | Component | Pass | Fail | MAE | Maximum error |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for label, values in summary["profiles"].items():
        for component, metric in values["components"].items():
            lines.append(
                f"| {label} | {component} | {metric['pass']} | "
                f"{metric['fail']} | {metric['maeVirupa']:.6f} | "
                f"{metric['maxErrorVirupa']:.6f} |"
            )
        total = values["total"]
        lines.append(
            f"| {label} | total | {total['pass']} | {total['fail']} | "
            f"{total['maeVirupa']:.6f} | "
            f"{total['maxErrorVirupa']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            *[
                f"- {conclusion}"
                for conclusion in summary["evidenceConclusions"]
            ],
            "",
            "The visible JHora profile is a compatibility witness, not a claim",
            "that JHora's Saptavargaja weights supersede the separately cited",
            "classical source profile. Source certification, financial validation,",
            "and live execution remain separate fail-closed gates.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    rows = build_comparison_rows(
        args.witness,
        args.top_level_witness,
        args.doctrine_config,
    )
    summary = build_summary(
        rows,
        witness_path=args.witness,
        top_level_path=args.top_level_witness,
        doctrine_config=args.doctrine_config,
    )
    write_csv(args.comparison, rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "contract": CONTRACT,
                "status": summary["status"],
                "witnessRows": len(rows),
                "profiles": summary["profiles"],
                "comparison": str(args.comparison.resolve()),
                "summary": str(args.summary.resolve()),
                "report": str(args.report.resolve()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
