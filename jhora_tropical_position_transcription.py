from __future__ import annotations

import csv
import math
from datetime import datetime
from pathlib import Path

from jhora_kaala_intermediate_witness_protocol import (
    AYANA_SAMPLE_ID,
    PLANETS,
    locked_kaala_values,
    read_csv,
)
from jhora_witness_protocol import sha256


TRANSCRIPTION_CONTRACT = "GANN_JHORA_TROPICAL_POSITION_TRANSCRIPTION_V1"
REPO_ROOT = Path(__file__).resolve().parent
REQUIRED_EVIDENCE_FIELDS = (
    ("position_evidence_path", "position_evidence_sha256"),
    ("tropical_mode_evidence_path", "tropical_mode_evidence_sha256"),
    ("raman_restored_evidence_path", "raman_restored_evidence_sha256"),
)


class TranscriptionValidationError(ValueError):
    def __init__(self, issues: list[str]) -> None:
        self.issues = issues
        super().__init__("\n".join(issues))


def _resolved_evidence_path(raw: str, repo_root: Path) -> Path:
    path = Path(raw.strip())
    return path if path.is_absolute() else repo_root / path


def _finite_number(
    row: dict[str, str],
    field: str,
    row_number: int,
    issues: list[str],
) -> float | None:
    raw = str(row.get(field) or "").strip()
    try:
        value = float(raw)
    except ValueError:
        issues.append(f"row {row_number}: {field} is not numeric")
        return None
    if not math.isfinite(value):
        issues.append(f"row {row_number}: {field} is not finite")
        return None
    return value


def validate_visible_tropical_position_rows(
    rows: list[dict[str, str]],
    *,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    issues: list[str] = []
    seen: set[str] = set()
    evidence_bindings: dict[str, set[tuple[str, str]]] = {
        path_field: set() for path_field, _ in REQUIRED_EVIDENCE_FIELDS
    }
    reviewers: set[str] = set()
    timestamps: set[str] = set()

    for row_number, row in enumerate(rows, start=2):
        if row.get("contract") != TRANSCRIPTION_CONTRACT:
            issues.append(f"row {row_number}: wrong transcription contract")
        if row.get("sample_id") != AYANA_SAMPLE_ID:
            issues.append(f"row {row_number}: wrong sample id")
        planet = str(row.get("planet") or "").strip().upper()
        if planet not in PLANETS:
            issues.append(f"row {row_number}: invalid planet {planet!r}")
        elif planet in seen:
            issues.append(f"row {row_number}: duplicate planet {planet}")
        else:
            seen.add(planet)

        longitude = _finite_number(
            row,
            "tropical_longitude_deg",
            row_number,
            issues,
        )
        latitude = _finite_number(
            row,
            "tropical_latitude_deg",
            row_number,
            issues,
        )
        if longitude is not None and not 0.0 <= longitude < 360.0:
            issues.append(
                f"row {row_number}: tropical longitude is outside [0, 360)"
            )
        if latitude is not None and abs(latitude) > 90.0:
            issues.append(
                f"row {row_number}: tropical latitude is outside [-90, 90]"
            )

        for path_field, hash_field in REQUIRED_EVIDENCE_FIELDS:
            raw_path = str(row.get(path_field) or "").strip()
            raw_hash = str(row.get(hash_field) or "").strip().upper()
            if not raw_path:
                issues.append(f"row {row_number}: {path_field} is missing")
                continue
            evidence = _resolved_evidence_path(raw_path, repo_root)
            if not evidence.is_file():
                issues.append(
                    f"row {row_number}: evidence file is missing: {evidence}"
                )
                continue
            if sha256(evidence) != raw_hash:
                issues.append(
                    f"row {row_number}: {path_field} hash mismatch"
                )
            evidence_bindings[path_field].add(
                (str(evidence.resolve()), raw_hash)
            )

        reviewer = str(row.get("reviewer") or "").strip()
        if not reviewer:
            issues.append(f"row {row_number}: reviewer is missing")
        else:
            reviewers.add(reviewer)
        captured_at = str(row.get("captured_at_utc") or "").strip()
        try:
            parsed = datetime.fromisoformat(
                captured_at.replace("Z", "+00:00")
            )
        except ValueError:
            parsed = None
        if (
            parsed is None
            or parsed.tzinfo is None
            or parsed.utcoffset() is None
        ):
            issues.append(
                f"row {row_number}: captured_at_utc is not timezone-aware"
            )
        else:
            timestamps.add(captured_at)

    if seen != set(PLANETS):
        issues.append(
            "planet matrix mismatch: "
            f"missing={sorted(set(PLANETS) - seen)}, "
            f"extra={sorted(seen - set(PLANETS))}"
        )
    for field, bindings in evidence_bindings.items():
        if len(bindings) != 1:
            issues.append(
                f"{field} must bind all seven rows to one visible file"
            )
    if len(reviewers) != 1:
        issues.append("all rows must share one reviewer")
    if len(timestamps) != 1:
        issues.append("all rows must share one capture timestamp")
    return issues


def read_visible_tropical_positions(
    path: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    issues = validate_visible_tropical_position_rows(
        rows,
        repo_root=repo_root,
    )
    if issues:
        raise TranscriptionValidationError(issues)
    return rows


def ayana_capture_inputs(
    transcription_path: Path,
    locked_kaala_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    rows = read_visible_tropical_positions(
        transcription_path,
        repo_root=repo_root,
    )
    locked = locked_kaala_values(
        read_csv(locked_kaala_path),
        sample_id=AYANA_SAMPLE_ID,
        measure="ayana",
    )
    if set(locked) != set(PLANETS):
        raise ValueError("locked historical Ayana matrix is incomplete")

    first = rows[0]
    evidence_path = _resolved_evidence_path(
        first["position_evidence_path"],
        repo_root,
    )
    values = {
        row["planet"].strip().upper(): {
            "tropical_longitude_deg": row["tropical_longitude_deg"],
            "tropical_latitude_deg": row["tropical_latitude_deg"],
            "kranti_deg": "",
            "ayana_virupa": locked[row["planet"].strip().upper()],
        }
        for row in rows
    }
    return {
        "evidence_path": evidence_path,
        "reviewer": first["reviewer"].strip(),
        "captured_at_utc": first["captured_at_utc"].strip(),
        "values": values,
    }
