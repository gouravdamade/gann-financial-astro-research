from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from jhora_witness_protocol import (
    JHORA_EXE_SHA256,
    JHORA_SOURCE_URL,
    JHORA_VERSION,
    LOCKED_SETTINGS,
    PLANETS,
    FIXTURES,
    require_pinned_jhora,
    settings_json,
    settings_sha256,
    sha256,
)


WITNESS_CONTRACT = "GANN_JHORA_STHANA_SUBCOMPONENT_WITNESS_V1"
STHANA_SUBCOMPONENTS = (
    "uchcha",
    "saptavargaja",
    "ojayugma",
    "kendradi",
    "drekkana",
)
EVIDENCE_VIEW = "visible_sthana_subcomponent_breakdown"
CAPTURED_STATUS = "captured_visible_jhora_subcomponent"
DEFAULT_TEMPLATE = Path(
    r"D:\PycharmProjects\jhora_sthana_subcomponent_witness_template_20260729.csv"
)
DEFAULT_TOP_LEVEL_WITNESS = Path(
    r"D:\PycharmProjects\status\evidence\jhora_shadbala_20260723"
    r"\jhora_shadbala_witness_completed_20260726.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create or validate a visible Jagannatha Hora Sthana-subcomponent "
            "witness. Inferred or reverse-engineered values are rejected."
        )
    )
    parser.add_argument(
        "--jhora-exe",
        type=Path,
        default=Path(
            r"D:\GannFinancialAstro\external_validators"
            r"\jagannatha_hora_8_0\app\bin\jhora.exe"
        ),
    )
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--validate", type=Path)
    parser.add_argument(
        "--top-level-witness",
        type=Path,
        default=DEFAULT_TOP_LEVEL_WITNESS,
    )
    return parser.parse_args()


def witness_template_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    locked = settings_json()
    locked_hash = settings_sha256()
    for fixture in FIXTURES:
        for planet in PLANETS:
            for component in STHANA_SUBCOMPONENTS:
                rows.append(
                    {
                        "contract": WITNESS_CONTRACT,
                        "sample_id": fixture.sample_id,
                        "local_iso": fixture.local_iso,
                        "timezone": fixture.timezone,
                        "latitude": f"{fixture.latitude:.6f}",
                        "longitude": f"{fixture.longitude:.6f}",
                        "location": fixture.location,
                        "planet": planet,
                        "sthana_subcomponent": component,
                        "jhora_value_virupa": "",
                        "jhora_version": JHORA_VERSION,
                        "jhora_exe_sha256": JHORA_EXE_SHA256,
                        "settings_json": locked,
                        "settings_sha256": locked_hash,
                        "evidence_view": EVIDENCE_VIEW,
                        "evidence_path": "",
                        "evidence_sha256": "",
                        "reviewer": "",
                        "captured_at_utc": "",
                        "status": "pending_visible_jhora_subcomponent_capture",
                        "notes": "",
                    }
                )
    return rows


def write_template(path: Path) -> None:
    rows = witness_template_rows()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _valid_utc_timestamp(raw: str) -> bool:
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate_witness_rows(rows: list[dict[str, str]]) -> list[str]:
    expected = {
        (fixture.sample_id, planet, component)
        for fixture in FIXTURES
        for planet in PLANETS
        for component in STHANA_SUBCOMPONENTS
    }
    seen: set[tuple[str, str, str]] = set()
    issues: list[str] = []
    locked_json = settings_json()
    locked_hash = settings_sha256()
    for row_number, row in enumerate(rows, start=2):
        key = (
            str(row.get("sample_id") or "").strip(),
            str(row.get("planet") or "").strip().upper(),
            str(row.get("sthana_subcomponent") or "").strip().lower(),
        )
        if key in seen:
            issues.append(f"row {row_number}: duplicate witness key {key}")
            continue
        seen.add(key)
        if key not in expected:
            issues.append(f"row {row_number}: unknown witness key {key}")
        if row.get("contract") != WITNESS_CONTRACT:
            issues.append(f"row {row_number}: wrong witness contract")
        if row.get("jhora_version") != JHORA_VERSION:
            issues.append(f"row {row_number}: wrong JHora version")
        if row.get("jhora_exe_sha256") != JHORA_EXE_SHA256:
            issues.append(f"row {row_number}: wrong JHora executable hash")
        if (
            row.get("settings_json") != locked_json
            or row.get("settings_sha256") != locked_hash
        ):
            issues.append(f"row {row_number}: locked settings mismatch")
        if row.get("evidence_view") != EVIDENCE_VIEW:
            issues.append(f"row {row_number}: evidence is not a visible breakdown")
        raw_value = str(row.get("jhora_value_virupa") or "").strip()
        if not raw_value:
            issues.append(f"row {row_number}: visible witness value is missing")
        else:
            try:
                value = float(raw_value)
            except ValueError:
                issues.append(f"row {row_number}: non-numeric witness value")
            else:
                if not math.isfinite(value):
                    issues.append(f"row {row_number}: non-finite witness value")
        evidence_path = Path(str(row.get("evidence_path") or "").strip())
        evidence_hash = str(row.get("evidence_sha256") or "").strip().upper()
        if not evidence_path.is_file():
            issues.append(f"row {row_number}: witness evidence file is missing")
        elif sha256(evidence_path) != evidence_hash:
            issues.append(f"row {row_number}: witness evidence hash mismatch")
        if not str(row.get("reviewer") or "").strip():
            issues.append(f"row {row_number}: witness reviewer is missing")
        captured_at = str(row.get("captured_at_utc") or "").strip()
        if not _valid_utc_timestamp(captured_at):
            issues.append(f"row {row_number}: valid capture timestamp is missing")
        if row.get("status") != CAPTURED_STATUS:
            issues.append(f"row {row_number}: witness is not marked captured")
    if seen != expected:
        issues.append(
            f"witness matrix mismatch: missing={sorted(expected - seen)}, "
            f"extra={sorted(seen - expected)}"
        )
    return issues


def validate_against_top_level_sthana(
    rows: list[dict[str, str]],
    top_level_rows: list[dict[str, str]],
    tolerance_virupa: float = 0.5,
) -> list[str]:
    expected_totals: dict[tuple[str, str], float] = {}
    for row in top_level_rows:
        if str(row.get("measure") or "").strip().lower() != "sthana":
            continue
        key = (
            str(row.get("sample_id") or "").strip(),
            str(row.get("planet") or "").strip().upper(),
        )
        expected_totals[key] = float(row["jhora_value_virupa"])

    observed: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        raw_value = str(row.get("jhora_value_virupa") or "").strip()
        if not raw_value:
            continue
        try:
            value = float(raw_value)
        except ValueError:
            continue
        if not math.isfinite(value):
            continue
        key = (
            str(row.get("sample_id") or "").strip(),
            str(row.get("planet") or "").strip().upper(),
        )
        observed[key].append(value)

    issues: list[str] = []
    expected_keys = {
        (fixture.sample_id, planet)
        for fixture in FIXTURES
        for planet in PLANETS
    }
    if set(expected_totals) != expected_keys:
        issues.append("top-level Sthana witness matrix is incomplete or unexpected")
        return issues
    for key in sorted(expected_keys):
        values = observed.get(key, [])
        if len(values) != len(STHANA_SUBCOMPONENTS):
            issues.append(f"{key}: visible Sthana subcomponent set is incomplete")
            continue
        delta = abs(sum(values) - expected_totals[key])
        if delta > tolerance_virupa:
            issues.append(
                f"{key}: subcomponent sum differs from locked top-level Sthana "
                f"by {delta:.6f} virupa"
            )
    return issues


def main() -> int:
    args = parse_args()
    executable_hash = require_pinned_jhora(args.jhora_exe)
    if args.validate:
        rows = read_csv(args.validate)
        issues = validate_witness_rows(rows)
        if not args.top_level_witness.is_file():
            issues.append(
                f"locked top-level witness is missing: {args.top_level_witness}"
            )
        else:
            issues.extend(
                validate_against_top_level_sthana(
                    rows,
                    read_csv(args.top_level_witness),
                )
            )
        print(
            json.dumps(
                {
                    "contract": WITNESS_CONTRACT,
                    "status": "valid" if not issues else "invalid",
                    "issues": issues,
                    "rows": len(rows),
                },
                indent=2,
            )
        )
        return 0 if not issues else 1

    write_template(args.template)
    print(
        json.dumps(
            {
                "contract": WITNESS_CONTRACT,
                "status": "template_created_pending_visible_capture",
                "jhoraExecutable": str(args.jhora_exe.resolve()),
                "jhoraExecutableSha256": executable_hash,
                "officialSource": JHORA_SOURCE_URL,
                "lockedSettings": LOCKED_SETTINGS,
                "settingsSha256": settings_sha256(),
                "requiredRows": len(witness_template_rows()),
                "template": str(args.template.resolve()),
                "templateSha256": sha256(args.template),
                "topLevelWitness": str(args.top_level_witness.resolve()),
                "inferredValuesAllowed": False,
                "executionAllowed": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
