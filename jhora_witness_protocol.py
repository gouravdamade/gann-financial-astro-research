from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from pyjhora_external_strength_export import FIXTURES, PLANETS, SHADBALA_COMPONENTS


WITNESS_CONTRACT = "GANN_JHORA_SHADBALA_WITNESS_V1"
JHORA_VERSION = "8.0.0.0"
JHORA_EXE_SHA256 = "3DDBE5FB0458AD1F0AD91B002C7EFB8BBA9F08891D3F46190ABA97D570B17908"
JHORA_DOWNLOAD_SHA256 = "10A291F8F69FBB9AB8C4EC88F8D804FD227FB23E0F4375706C30BA0043B72339"
JHORA_SOURCE_URL = "https://vedicastrologer.org/jh/index.htm"
MEASURES = SHADBALA_COMPONENTS + ("total",)
LOCKED_SETTINGS = {
    "planetary_model": "Drik Siddhanta",
    "ayanamsa": "Raman",
    "coordinate_center": "geocentric",
    "planetary_positions": "apparent",
    "node": "true node",
    "house_system": "Sripathi/Porphyry",
    "ascendant_house_position": "middle of first house",
    "sunrise_definition": "apparent rise of tip",
    "day_boundary": "sunrise",
    "special_aspects": "Parasara",
    "relationship_scope": "relevant divisional chart",
    "relationship_type": "compound",
    "hora_variant": "Parasara default",
    "drekkana_variant": "Parasara default",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or validate the locked Jagannatha Hora witness ledger."
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
        "--template",
        type=Path,
        default=Path(r"D:\PycharmProjects\jhora_shadbala_witness_template_20260718.csv"),
    )
    parser.add_argument("--validate", type=Path)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def settings_json() -> str:
    return json.dumps(LOCKED_SETTINGS, sort_keys=True, separators=(",", ":"))


def settings_sha256() -> str:
    return hashlib.sha256(settings_json().encode("ascii")).hexdigest().upper()


def require_pinned_jhora(executable: Path) -> str:
    if not executable.is_file():
        raise FileNotFoundError(f"Jagannatha Hora executable not found: {executable}")
    digest = sha256(executable)
    if digest != JHORA_EXE_SHA256:
        raise RuntimeError(
            f"Jagannatha Hora executable hash mismatch: expected "
            f"{JHORA_EXE_SHA256}, got {digest}"
        )
    return digest


def witness_template_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    locked = settings_json()
    locked_hash = settings_sha256()
    for fixture in FIXTURES:
        for planet in PLANETS:
            for measure in MEASURES:
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
                        "measure": measure,
                        "jhora_value_virupa": "",
                        "jhora_version": JHORA_VERSION,
                        "jhora_exe_sha256": JHORA_EXE_SHA256,
                        "settings_json": locked,
                        "settings_sha256": locked_hash,
                        "evidence_path": "",
                        "evidence_sha256": "",
                        "reviewer": "",
                        "captured_at_utc": "",
                        "status": "pending_manual_jhora_capture",
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


def validate_witness_rows(rows: list[dict[str, str]]) -> list[str]:
    expected = {
        (fixture.sample_id, planet, measure)
        for fixture in FIXTURES
        for planet in PLANETS
        for measure in MEASURES
    }
    seen: set[tuple[str, str, str]] = set()
    issues: list[str] = []
    locked_json = settings_json()
    locked_hash = settings_sha256()
    for row_number, row in enumerate(rows, start=2):
        key = (
            str(row.get("sample_id") or "").strip(),
            str(row.get("planet") or "").strip().upper(),
            str(row.get("measure") or "").strip().lower(),
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
        if row.get("settings_json") != locked_json or row.get("settings_sha256") != locked_hash:
            issues.append(f"row {row_number}: locked settings mismatch")
        raw_value = str(row.get("jhora_value_virupa") or "").strip()
        if not raw_value:
            continue
        try:
            value = float(raw_value)
        except ValueError:
            issues.append(f"row {row_number}: non-numeric witness value")
            continue
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
        if not str(row.get("captured_at_utc") or "").strip():
            issues.append(f"row {row_number}: capture timestamp is missing")
    if seen != expected:
        issues.append(
            f"witness matrix mismatch: missing={sorted(expected - seen)}, "
            f"extra={sorted(seen - expected)}"
        )
    return issues


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    args = parse_args()
    executable_hash = require_pinned_jhora(args.jhora_exe)
    if args.validate:
        issues = validate_witness_rows(read_csv(args.validate))
        print(
            json.dumps(
                {
                    "contract": WITNESS_CONTRACT,
                    "status": "valid" if not issues else "invalid",
                    "issues": issues,
                    "rows": len(read_csv(args.validate)),
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
                "status": "template_created_pending_manual_capture",
                "jhoraExecutable": str(args.jhora_exe.resolve()),
                "jhoraExecutableSha256": executable_hash,
                "downloadSha256": JHORA_DOWNLOAD_SHA256,
                "officialSource": JHORA_SOURCE_URL,
                "settings": LOCKED_SETTINGS,
                "settingsSha256": settings_sha256(),
                "rows": len(witness_template_rows()),
                "template": str(args.template.resolve()),
                "templateSha256": sha256(args.template),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
