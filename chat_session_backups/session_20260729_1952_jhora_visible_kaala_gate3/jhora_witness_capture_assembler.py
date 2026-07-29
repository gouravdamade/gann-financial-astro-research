from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from jhora_fixture_file import require_exact_fixture_times
from jhora_witness_protocol import sha256, validate_witness_rows, witness_template_rows
from pyjhora_external_strength_export import PLANETS, SHADBALA_COMPONENTS


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = (
    REPO_ROOT / "status" / "evidence" / "jhora_shadbala_20260723"
)
DEFAULT_OUTPUT = (
    DEFAULT_EVIDENCE_DIR / "jhora_shadbala_witness_completed_20260726.csv"
)
COMPONENT_COLUMNS = {
    "sthana": 2,
    "kaala": 3,
    "dig": 4,
    "chesta": 5,
    "drik": 6,
    "naisargika": 7,
}
TOTAL_EXCLUDED_COMPONENTS = {
    "SUN": frozenset({"chesta"}),
    "MOON": frozenset({"chesta"}),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assemble the locked JHora witness ledger from captured tables."
    )
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--reviewer",
        default="OpenAI Codex local GUI capture",
    )
    return parser.parse_args()


def _planet_rows(path: Path, minimum_columns: int) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        columns = line.split()
        if not columns:
            continue
        planet = columns[0].upper()
        if planet not in PLANETS:
            continue
        if len(columns) < minimum_columns:
            raise ValueError(
                f"{path}: {planet} row has {len(columns)} columns; "
                f"expected at least {minimum_columns}"
            )
        rows[planet] = columns
    missing = sorted(set(PLANETS) - set(rows))
    extra = sorted(set(rows) - set(PLANETS))
    if missing or extra:
        raise ValueError(f"{path}: planet matrix mismatch: missing={missing}, extra={extra}")
    return rows


def parse_breakup(path: Path) -> dict[str, dict[str, float]]:
    source_rows = _planet_rows(path, minimum_columns=8)
    parsed: dict[str, dict[str, float]] = {}
    for planet, columns in source_rows.items():
        parsed[planet] = {
            "rupas": float(columns[1]),
            **{
                component: float(columns[column])
                for component, column in COMPONENT_COLUMNS.items()
            },
        }
    return parsed


def parse_summary(path: Path) -> dict[str, float]:
    source_rows = _planet_rows(path, minimum_columns=6)
    return {planet: float(columns[1]) for planet, columns in source_rows.items()}


def _relative_evidence_path(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def _captured_at_utc(path: Path) -> str:
    return (
        datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _raw_accessibility_source(
    evidence_dir: Path,
    sample_id: str,
    table: str,
    normalized_text: Path,
) -> Path:
    captures = sorted(
        evidence_dir.glob(
            f"{sample_id}_shadbala_{table}_accessibility_exact_*.txt"
        )
    )
    if len(captures) > 1:
        raise ValueError(
            f"{sample_id}: multiple exact {table} accessibility captures: "
            f"{captures}"
        )
    return captures[0] if captures else normalized_text


def assemble_witness_rows(
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
    reviewer: str = "OpenAI Codex local GUI capture",
) -> tuple[list[dict[str, str]], list[dict[str, float | str]]]:
    require_exact_fixture_times()
    rows = witness_template_rows()
    fixture_values: dict[str, dict[str, dict[str, float]]] = {}
    fixture_evidence: dict[str, dict[str, Path]] = {}
    consistency_checks: list[dict[str, float | str]] = []

    sample_ids = {row["sample_id"] for row in rows}
    for sample_id in sorted(sample_ids):
        breakup_text = evidence_dir / f"{sample_id}_shadbala_breakup_locked.txt"
        summary_text = evidence_dir / f"{sample_id}_shadbala_summary_locked.txt"
        breakup_image = evidence_dir / f"{sample_id}_shadbala_breakup_locked.jpg"
        summary_image = evidence_dir / f"{sample_id}_shadbala_summary_locked.jpg"
        required = (breakup_text, summary_text, breakup_image, summary_image)
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"{sample_id}: missing locked evidence: {missing}")

        breakup = parse_breakup(breakup_text)
        totals = parse_summary(summary_text)
        fixture_values[sample_id] = {}
        fixture_evidence[sample_id] = {
            "breakup_text": breakup_text,
            "breakup_image": breakup_image,
            "breakup_raw": _raw_accessibility_source(
                evidence_dir,
                sample_id,
                "breakup",
                breakup_text,
            ),
            "summary_text": summary_text,
            "summary_image": summary_image,
            "summary_raw": _raw_accessibility_source(
                evidence_dir,
                sample_id,
                "summary",
                summary_text,
            ),
        }
        for planet in PLANETS:
            excluded_components = TOTAL_EXCLUDED_COMPONENTS.get(planet, frozenset())
            component_total = sum(
                breakup[planet][name]
                for name in SHADBALA_COMPONENTS
                if name not in excluded_components
            )
            reported_total = totals[planet]
            component_residual = reported_total - component_total
            rupas_residual = reported_total - breakup[planet]["rupas"] * 60.0
            if abs(component_residual) > 0.04:
                raise ValueError(
                    f"{sample_id} {planet}: rounded component sum differs from "
                    f"reported total by {component_residual:.4f} virupa"
                )
            if abs(rupas_residual) > 0.31:
                raise ValueError(
                    f"{sample_id} {planet}: rounded rupa value differs from "
                    f"reported total by {rupas_residual:.4f} virupa"
                )
            fixture_values[sample_id][planet] = {
                **{name: breakup[planet][name] for name in SHADBALA_COMPONENTS},
                "total": reported_total,
            }
            consistency_checks.append(
                {
                    "sample_id": sample_id,
                    "planet": planet,
                    "total_excluded_components": ",".join(
                        sorted(excluded_components)
                    ),
                    "component_residual_virupa": round(component_residual, 6),
                    "rupas_residual_virupa": round(rupas_residual, 6),
                }
            )

    for row in rows:
        sample_id = row["sample_id"]
        planet = row["planet"]
        measure = row["measure"]
        is_total = measure == "total"
        evidence_image = fixture_evidence[sample_id][
            "summary_image" if is_total else "breakup_image"
        ]
        evidence_text = fixture_evidence[sample_id][
            "summary_text" if is_total else "breakup_text"
        ]
        raw_accessibility = fixture_evidence[sample_id][
            "summary_raw" if is_total else "breakup_raw"
        ]
        row["jhora_value_virupa"] = f"{fixture_values[sample_id][planet][measure]:.2f}"
        row["evidence_path"] = _relative_evidence_path(evidence_image)
        row["evidence_sha256"] = sha256(evidence_image)
        row["reviewer"] = reviewer
        row["captured_at_utc"] = _captured_at_utc(evidence_image)
        row["status"] = "captured_locked_manual_jhora"
        row["notes"] = (
            "Copied directly from the pinned JHora 8.0 table under locked settings; "
            f"normalized table={_relative_evidence_path(evidence_text)}; "
            f"normalized_table_sha256={sha256(evidence_text)}; "
            f"raw accessibility table={_relative_evidence_path(raw_accessibility)}; "
            f"raw_accessibility_sha256={sha256(raw_accessibility)}"
        )

    issues = validate_witness_rows(rows)
    if issues:
        raise ValueError(f"assembled witness ledger is invalid: {issues}")
    return rows, consistency_checks


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    rows, checks = assemble_witness_rows(args.evidence_dir, args.reviewer)
    write_rows(args.output, rows)
    print(
        json.dumps(
            {
                "status": "valid",
                "rows": len(rows),
                "fixtures": len({row["sample_id"] for row in rows}),
                "output": str(args.output.resolve()),
                "output_sha256": sha256(args.output),
                "max_component_residual_virupa": max(
                    abs(float(check["component_residual_virupa"])) for check in checks
                ),
                "max_rupas_residual_virupa": max(
                    abs(float(check["rupas_residual_virupa"])) for check in checks
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
