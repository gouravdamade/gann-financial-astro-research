from __future__ import annotations

import argparse
import csv
import json
import math
import re
from datetime import datetime
from pathlib import Path

from jhora_fixture_file import require_exact_fixture_times
from jhora_kaala_formula_profile_reconciliation import (
    AYANA_OBLIQUITY_DEG,
    ayana_from_kranti,
    projected_kranti_deg,
)
from jhora_witness_protocol import (
    FIXTURES,
    JHORA_EXE_SHA256,
    JHORA_VERSION,
    PLANETS,
    require_pinned_jhora,
    settings_json,
    settings_sha256,
    sha256,
)


WITNESS_CONTRACT = "GANN_JHORA_KAALA_INTERMEDIATE_WITNESS_V1"
HORA_SAMPLE_ID = "case_8_event_start"
AYANA_SAMPLE_ID = "gann_reference_tokyo"
HORA_KIND = "hora_sunrise_boundary"
AYANA_KIND = "ayana_historical_intermediate"
HORA_EVIDENCE_VIEW = "visible_case8_sunrise_and_hora_award"
AYANA_EVIDENCE_VIEW = "visible_historical_tropical_longitude_or_kranti"
CAPTURED_STATUS = "captured_visible_jhora_kaala_intermediate"
EVIDENCE_BUNDLE_CONTRACT = (
    "GANN_JHORA_VISIBLE_HORA_BOUNDARY_EVIDENCE_V1"
)
TOLERANCE_VIRUPA = 0.5
VISIBLE_TIME_PATTERN = re.compile(
    r"^(?P<hour>\d{1,2}):(?P<minute>[0-5]\d):"
    r"(?P<second>[0-5]\d(?:\.\d+)?)$"
)
DEFAULT_HORA_TEMPLATE = Path(
    r"D:\PycharmProjects\jhora_hora_boundary_witness_template_20260729.csv"
)
DEFAULT_AYANA_TEMPLATE = Path(
    r"D:\PycharmProjects\jhora_ayana_intermediate_witness_template_20260729.csv"
)
DEFAULT_KAALA_WITNESS = Path(
    r"D:\PycharmProjects\status\evidence\jhora_kaala_witness_20260727"
    r"\jhora_kaala_profile_comparison_20260727.csv"
)

FIXTURE_BY_ID = {fixture.sample_id: fixture for fixture in FIXTURES}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create or validate visible Jagannatha Hora intermediate-input "
            "witnesses for the case-8 Hora boundary and historical Ayana."
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
    parser.add_argument(
        "--hora-template",
        type=Path,
        default=DEFAULT_HORA_TEMPLATE,
    )
    parser.add_argument(
        "--ayana-template",
        type=Path,
        default=DEFAULT_AYANA_TEMPLATE,
    )
    parser.add_argument("--validate-hora", type=Path)
    parser.add_argument("--validate-ayana", type=Path)
    parser.add_argument(
        "--kaala-witness",
        type=Path,
        default=DEFAULT_KAALA_WITNESS,
    )
    return parser.parse_args()


def _base_row(
    *,
    sample_id: str,
    planet: str,
    witness_kind: str,
    evidence_view: str,
) -> dict[str, str]:
    fixture = FIXTURE_BY_ID[sample_id]
    return {
        "contract": WITNESS_CONTRACT,
        "witness_kind": witness_kind,
        "sample_id": fixture.sample_id,
        "local_iso": fixture.local_iso,
        "timezone": fixture.timezone,
        "latitude": f"{fixture.latitude:.6f}",
        "longitude": f"{fixture.longitude:.6f}",
        "location": fixture.location,
        "planet": planet,
        "jhora_version": JHORA_VERSION,
        "jhora_exe_sha256": JHORA_EXE_SHA256,
        "settings_json": settings_json(),
        "settings_sha256": settings_sha256(),
        "evidence_view": evidence_view,
        "evidence_path": "",
        "evidence_sha256": "",
        "reviewer": "",
        "captured_at_utc": "",
        "status": "pending_visible_jhora_kaala_intermediate_capture",
        "notes": "",
    }


def hora_template_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for planet in PLANETS:
        row = _base_row(
            sample_id=HORA_SAMPLE_ID,
            planet=planet,
            witness_kind=HORA_KIND,
            evidence_view=HORA_EVIDENCE_VIEW,
        )
        row.update(
            {
                "jhora_sunrise_lmt_display": "",
                "jhora_sunrise_lmt_hour": "",
                "jhora_hora_lord": "",
                "jhora_hora_virupa": "",
            }
        )
        rows.append(row)
    return rows


def ayana_template_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for planet in PLANETS:
        row = _base_row(
            sample_id=AYANA_SAMPLE_ID,
            planet=planet,
            witness_kind=AYANA_KIND,
            evidence_view=AYANA_EVIDENCE_VIEW,
        )
        row.update(
            {
                "jhora_tropical_longitude_deg": "",
                "jhora_kranti_deg": "",
                "jhora_ayana_virupa": "",
            }
        )
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def witness_gate_summary(
    *,
    hora_path: Path,
    ayana_path: Path,
    kaala_witness_path: Path,
) -> dict[str, object]:
    inputs = {
        "hora": {
            "path": str(hora_path),
            "sha256": sha256(hora_path) if hora_path.is_file() else None,
        },
        "ayana": {
            "path": str(ayana_path),
            "sha256": sha256(ayana_path) if ayana_path.is_file() else None,
        },
        "lockedKaala": {
            "path": str(kaala_witness_path),
            "sha256": (
                sha256(kaala_witness_path)
                if kaala_witness_path.is_file()
                else None
            ),
        },
    }
    base: dict[str, object] = {
        "contract": WITNESS_CONTRACT,
        "required": True,
        "status": "blocked_missing_visible_kaala_intermediate_witness",
        "evidenceComplete": False,
        "formulaCertified": False,
        "productionChangeAllowed": False,
        "horaRows": 0,
        "ayanaRows": 0,
        "horaEvidenceComplete": False,
        "ayanaEvidenceComplete": False,
        "formulaIssues": [],
        "issues": [],
        "inputs": inputs,
    }
    if not kaala_witness_path.is_file():
        base["issues"] = ["missing locked visible Kaala witness"]
        return base

    hora_rows = read_csv(hora_path) if hora_path.is_file() else []
    ayana_rows = read_csv(ayana_path) if ayana_path.is_file() else []
    base["horaRows"] = len(hora_rows)
    base["ayanaRows"] = len(ayana_rows)
    hora_pending = (
        not hora_path.is_file()
        or (
            len(hora_rows) == len(PLANETS)
            and all(
                str(row.get("status") or "").startswith("pending_")
                for row in hora_rows
            )
        )
    )
    ayana_pending = (
        not ayana_path.is_file()
        or (
            len(ayana_rows) == len(PLANETS)
            and all(
                str(row.get("status") or "").startswith("pending_")
                for row in ayana_rows
            )
        )
    )
    if hora_pending and ayana_pending:
        base["status"] = (
            "blocked_pending_visible_kaala_intermediate_witness"
        )
        return base

    locked_rows = read_csv(kaala_witness_path)
    issues: list[str] = []
    if not hora_pending:
        issues.extend(
            f"hora: {issue}"
            for issue in validate_hora_rows(hora_rows, locked_rows)
        )
    if not ayana_pending:
        issues.extend(
            f"ayana: {issue}"
            for issue in validate_ayana_observation_rows(
                ayana_rows,
                locked_rows,
            )
        )
    base["issues"] = issues
    if issues:
        base["status"] = "blocked_invalid_visible_kaala_intermediate_witness"
        return base

    base["horaEvidenceComplete"] = not hora_pending
    base["ayanaEvidenceComplete"] = not ayana_pending
    formula_issues = (
        []
        if ayana_pending
        else [
            f"ayana: {issue}"
            for issue in ayana_formula_reconciliation_issues(ayana_rows)
        ]
    )
    base["formulaIssues"] = formula_issues
    if hora_pending or ayana_pending:
        pending_label = (
            "hora"
            if hora_pending and not ayana_pending
            else "ayana"
        )
        base["status"] = (
            f"blocked_pending_visible_{pending_label}_intermediate_witness"
        )
        return base
    base["status"] = (
        "visible_packet_complete_formula_candidate_rejected"
        if formula_issues
        else "visible_packet_complete_not_formula_certified"
    )
    base["evidenceComplete"] = True
    return base


def _valid_utc_timestamp(raw: str) -> bool:
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def evidence_bundle_issues(path: Path) -> list[str]:
    if path.suffix.lower() != ".json":
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"evidence bundle cannot be read: {exc}"]
    if payload.get("contract") != EVIDENCE_BUNDLE_CONTRACT:
        return ["evidence bundle has an unsupported contract"]
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["evidence bundle has no source files"]
    issues: list[str] = []
    for source_number, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            issues.append(
                f"evidence bundle source {source_number} is not an object"
            )
            continue
        source_path = Path(str(source.get("path") or "").strip())
        source_hash = str(source.get("sha256") or "").strip().upper()
        if not str(source.get("purpose") or "").strip():
            issues.append(
                f"evidence bundle source {source_number} has no purpose"
            )
        if not source_path.is_file():
            issues.append(
                f"evidence bundle source {source_number} is missing"
            )
        elif sha256(source_path) != source_hash:
            issues.append(
                f"evidence bundle source {source_number} hash mismatch"
            )
    return issues


def _float_value(
    row: dict[str, str],
    field: str,
    row_number: int,
    issues: list[str],
) -> float | None:
    raw = str(row.get(field) or "").strip()
    if not raw:
        issues.append(f"row {row_number}: {field} is missing")
        return None
    try:
        value = float(raw)
    except ValueError:
        issues.append(f"row {row_number}: {field} is not numeric")
        return None
    if not math.isfinite(value):
        issues.append(f"row {row_number}: {field} is not finite")
        return None
    return value


def _optional_float(
    row: dict[str, str],
    field: str,
    row_number: int,
    issues: list[str],
) -> float | None:
    raw = str(row.get(field) or "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        issues.append(f"row {row_number}: {field} is not numeric")
        return None
    if not math.isfinite(value):
        issues.append(f"row {row_number}: {field} is not finite")
        return None
    return value


def _validate_provenance(
    rows: list[dict[str, str]],
    *,
    sample_id: str,
    witness_kind: str,
    evidence_view: str,
) -> list[str]:
    expected = {(sample_id, planet) for planet in PLANETS}
    seen: set[tuple[str, str]] = set()
    issues: list[str] = []
    locked_json = settings_json()
    locked_hash = settings_sha256()
    for row_number, row in enumerate(rows, start=2):
        key = (
            str(row.get("sample_id") or "").strip(),
            str(row.get("planet") or "").strip().upper(),
        )
        if key in seen:
            issues.append(f"row {row_number}: duplicate witness key {key}")
            continue
        seen.add(key)
        if key not in expected:
            issues.append(f"row {row_number}: unknown witness key {key}")
        if row.get("contract") != WITNESS_CONTRACT:
            issues.append(f"row {row_number}: wrong witness contract")
        if row.get("witness_kind") != witness_kind:
            issues.append(f"row {row_number}: wrong witness kind")
        if row.get("jhora_version") != JHORA_VERSION:
            issues.append(f"row {row_number}: wrong JHora version")
        if row.get("jhora_exe_sha256") != JHORA_EXE_SHA256:
            issues.append(f"row {row_number}: wrong JHora executable hash")
        if (
            row.get("settings_json") != locked_json
            or row.get("settings_sha256") != locked_hash
        ):
            issues.append(f"row {row_number}: locked settings mismatch")
        if row.get("evidence_view") != evidence_view:
            issues.append(f"row {row_number}: wrong visible evidence view")
        evidence_path = Path(str(row.get("evidence_path") or "").strip())
        evidence_hash = str(row.get("evidence_sha256") or "").strip().upper()
        if not evidence_path.is_file():
            issues.append(f"row {row_number}: witness evidence file is missing")
        elif sha256(evidence_path) != evidence_hash:
            issues.append(f"row {row_number}: witness evidence hash mismatch")
        else:
            issues.extend(
                f"row {row_number}: {issue}"
                for issue in evidence_bundle_issues(evidence_path)
            )
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


def locked_kaala_values(
    rows: list[dict[str, str]],
    *,
    sample_id: str,
    measure: str,
) -> dict[str, float]:
    output: dict[str, float] = {}
    for row in rows:
        if (
            str(row.get("sample_id") or "").strip() == sample_id
            and str(row.get("measure") or "").strip().lower() == measure
        ):
            planet = str(row.get("planet") or "").strip().upper()
            output[planet] = float(row["jhora_value_virupa"])
    return output


def visible_time_to_decimal_hour(value: str) -> float:
    text = str(value or "").strip()
    match = VISIBLE_TIME_PATTERN.fullmatch(text)
    if not match:
        raise ValueError("visible time must use H:MM:SS or HH:MM:SS")
    hour = int(match.group("hour"))
    minute = int(match.group("minute"))
    second = float(match.group("second"))
    if hour >= 24:
        raise ValueError("visible time hour must be inside [0, 24)")
    return hour + minute / 60.0 + second / 3600.0


def validate_hora_rows(
    rows: list[dict[str, str]],
    locked_rows: list[dict[str, str]],
) -> list[str]:
    issues = _validate_provenance(
        rows,
        sample_id=HORA_SAMPLE_ID,
        witness_kind=HORA_KIND,
        evidence_view=HORA_EVIDENCE_VIEW,
    )
    locked = locked_kaala_values(
        locked_rows,
        sample_id=HORA_SAMPLE_ID,
        measure="hora",
    )
    if set(locked) != set(PLANETS):
        issues.append("locked case-8 Hora witness is incomplete")
        return issues

    sunrise_display_values: list[float] = []
    sunrise_values: list[float] = []
    lords: set[str] = set()
    awards: dict[str, float] = {}
    for row_number, row in enumerate(rows, start=2):
        sunrise_display = str(
            row.get("jhora_sunrise_lmt_display") or ""
        ).strip()
        try:
            sunrise_display_hour = visible_time_to_decimal_hour(
                sunrise_display
            )
        except ValueError as exc:
            issues.append(
                f"row {row_number}: invalid visible sunrise: {exc}"
            )
            sunrise_display_hour = None
        if sunrise_display_hour is not None:
            sunrise_display_values.append(sunrise_display_hour)
        sunrise = _float_value(
            row,
            "jhora_sunrise_lmt_hour",
            row_number,
            issues,
        )
        if sunrise is not None:
            if not 0.0 <= sunrise < 24.0:
                issues.append(
                    f"row {row_number}: sunrise LMT hour is outside [0, 24)"
                )
            sunrise_values.append(sunrise)
            if (
                sunrise_display_hour is not None
                and abs(sunrise - sunrise_display_hour) > 0.5 / 3600.0
            ):
                issues.append(
                    f"row {row_number}: decimal sunrise does not match the "
                    "visible JHora time"
                )
        lord = str(row.get("jhora_hora_lord") or "").strip().upper()
        if lord not in PLANETS:
            issues.append(f"row {row_number}: invalid Hora lord {lord!r}")
        else:
            lords.add(lord)
        award = _float_value(
            row,
            "jhora_hora_virupa",
            row_number,
            issues,
        )
        planet = str(row.get("planet") or "").strip().upper()
        if award is not None and planet in PLANETS:
            awards[planet] = award
            if abs(award - locked[planet]) > TOLERANCE_VIRUPA:
                issues.append(
                    f"row {row_number}: Hora award differs from locked visible "
                    f"JHora by more than {TOLERANCE_VIRUPA} virupa"
                )

    if sunrise_values and max(sunrise_values) - min(sunrise_values) > 1e-9:
        issues.append("Hora rows do not share one visible sunrise input")
    if (
        sunrise_display_values
        and max(sunrise_display_values) - min(sunrise_display_values) > 1e-9
    ):
        issues.append("Hora rows do not share one visible sunrise display")
    if len(lords) != 1:
        issues.append("Hora rows do not share one visible Hora lord")
    winners = [
        planet for planet, value in awards.items() if abs(value - 60.0) <= 1e-9
    ]
    non_binary = [
        planet
        for planet, value in awards.items()
        if min(abs(value), abs(value - 60.0)) > 1e-9
    ]
    if non_binary:
        issues.append(
            "Hora award must be visibly categorical 0/60 for every planet"
        )
    if len(winners) != 1:
        issues.append("Hora witness must contain exactly one 60-virupa winner")
    elif len(lords) == 1 and winners[0] != next(iter(lords)):
        issues.append("visible Hora lord does not match the 60-virupa winner")
    return issues


def validate_ayana_rows(
    rows: list[dict[str, str]],
    locked_rows: list[dict[str, str]],
) -> list[str]:
    issues = validate_ayana_observation_rows(rows, locked_rows)
    issues.extend(ayana_formula_reconciliation_issues(rows))
    return issues


def validate_ayana_observation_rows(
    rows: list[dict[str, str]],
    locked_rows: list[dict[str, str]],
) -> list[str]:
    issues = _validate_provenance(
        rows,
        sample_id=AYANA_SAMPLE_ID,
        witness_kind=AYANA_KIND,
        evidence_view=AYANA_EVIDENCE_VIEW,
    )
    locked = locked_kaala_values(
        locked_rows,
        sample_id=AYANA_SAMPLE_ID,
        measure="ayana",
    )
    if set(locked) != set(PLANETS):
        issues.append("locked historical Ayana witness is incomplete")
        return issues

    for row_number, row in enumerate(rows, start=2):
        planet = str(row.get("planet") or "").strip().upper()
        longitude = _optional_float(
            row,
            "jhora_tropical_longitude_deg",
            row_number,
            issues,
        )
        kranti = _optional_float(
            row,
            "jhora_kranti_deg",
            row_number,
            issues,
        )
        ayana = _float_value(
            row,
            "jhora_ayana_virupa",
            row_number,
            issues,
        )
        if longitude is None and kranti is None:
            issues.append(
                f"row {row_number}: visible tropical longitude or Kranti is "
                "required"
            )
            continue
        if longitude is not None and not 0.0 <= longitude < 360.0:
            issues.append(
                f"row {row_number}: tropical longitude is outside [0, 360)"
            )
        if kranti is not None and abs(kranti) > AYANA_OBLIQUITY_DEG + 0.5:
            issues.append(f"row {row_number}: Kranti is outside physical range")
        if ayana is not None and planet in locked:
            if abs(ayana - locked[planet]) > TOLERANCE_VIRUPA:
                issues.append(
                    f"row {row_number}: Ayana differs from locked visible "
                    f"JHora by more than {TOLERANCE_VIRUPA} virupa"
                )
    return issues


def ayana_formula_reconciliation_issues(
    rows: list[dict[str, str]],
) -> list[str]:
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        planet = str(row.get("planet") or "").strip().upper()
        longitude = _optional_float(
            row,
            "jhora_tropical_longitude_deg",
            row_number,
            issues,
        )
        kranti = _optional_float(
            row,
            "jhora_kranti_deg",
            row_number,
            issues,
        )
        ayana = _float_value(
            row,
            "jhora_ayana_virupa",
            row_number,
            issues,
        )
        candidate_krantis: list[tuple[str, float]] = []
        if longitude is not None and 0.0 <= longitude < 360.0:
            candidate_krantis.append(
                ("visible tropical longitude", projected_kranti_deg(longitude))
            )
        if kranti is not None:
            candidate_krantis.append(("visible Kranti", kranti))
        if ayana is None or planet not in PLANETS:
            continue
        for source_label, candidate_kranti in candidate_krantis:
            candidate_ayana = ayana_from_kranti(planet, candidate_kranti)
            if abs(candidate_ayana - ayana) > TOLERANCE_VIRUPA:
                issues.append(
                    f"row {row_number}: Ayana reconstructed from "
                    f"{source_label} differs by "
                    f"{abs(candidate_ayana - ayana):.6f} virupa"
                )
    return issues


def main() -> int:
    args = parse_args()
    require_pinned_jhora(args.jhora_exe)
    require_exact_fixture_times()
    if not args.validate_hora and not args.validate_ayana:
        write_csv(args.hora_template, hora_template_rows())
        write_csv(args.ayana_template, ayana_template_rows())
        print(
            json.dumps(
                {
                    "contract": WITNESS_CONTRACT,
                    "status": "templates_created_pending_visible_capture",
                    "horaTemplate": str(args.hora_template),
                    "ayanaTemplate": str(args.ayana_template),
                    "horaRows": len(hora_template_rows()),
                    "ayanaRows": len(ayana_template_rows()),
                },
                indent=2,
            )
        )
        return 0

    if not args.kaala_witness.is_file():
        raise FileNotFoundError(
            f"locked visible Kaala witness is missing: {args.kaala_witness}"
        )
    locked_rows = read_csv(args.kaala_witness)
    issues: list[str] = []
    if args.validate_hora:
        issues.extend(
            f"hora: {issue}"
            for issue in validate_hora_rows(
                read_csv(args.validate_hora),
                locked_rows,
            )
        )
    if args.validate_ayana:
        issues.extend(
            f"ayana: {issue}"
            for issue in validate_ayana_rows(
                read_csv(args.validate_ayana),
                locked_rows,
            )
        )
    complete_packet = bool(args.validate_hora and args.validate_ayana)
    status = (
        "valid_complete_visible_intermediate_packet"
        if complete_packet and not issues
        else (
            "valid_partial_visible_intermediate_packet"
            if not issues
            else "invalid_visible_intermediate_packet"
        )
    )
    print(
        json.dumps(
            {
                "contract": WITNESS_CONTRACT,
                "status": status,
                "completePacket": complete_packet,
                "productionChangeAllowed": False,
                "issues": issues,
            },
            indent=2,
        )
    )
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
