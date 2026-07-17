from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


PYJHORA_VERSION = "4.8.7"
PYJHORA_WHEEL_SHA256 = "D8D8014573A38DDEFEDCAE57D3B8D84687CAC2AD31BB5B1DD70D945906A4D54D"
PLANETS = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")
STRENGTH_PREFIXES = (
    "shadbala_implemented_total_virupa.",
    "drik_bala_virupa.",
)
BVRAMAN_DRIK_EXPECTED = (15.86, -21.73, 0.95, 15.64, -16.04, 18.47, 7.21)
BVRAMAN_DRIK_TOLERANCE = 0.05


@dataclass(frozen=True)
class Fixture:
    sample_id: str
    local_iso: str
    timezone: str
    latitude: float
    longitude: float
    location: str


FIXTURES = (
    Fixture(
        "case_8_event_start",
        "2025-03-07T19:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    Fixture(
        "case_43_event_start",
        "2025-04-04T02:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    Fixture(
        "case_103_event_start",
        "2025-05-15T22:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    Fixture(
        "case_127_sr_touch_start",
        "2025-05-28T22:00:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    Fixture(
        "gann_reference_tokyo",
        "1889-02-11T00:00:00",
        "Asia/Tokyo",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export hash-pinned PyJHora Shadbala/Drik values for Gate 3."
    )
    parser.add_argument(
        "--pyjhora-root",
        type=Path,
        default=Path(r"D:\GannFinancialAstro\external_validators\pyjhora_4_8_7"),
    )
    parser.add_argument(
        "--wheel",
        type=Path,
        default=Path(
            r"D:\GannFinancialAstro\external_validators\wheels"
            r"\pyjhora-4.8.7-py3-none-any.whl"
        ),
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(r"D:\PycharmProjects\astro_external_validation_template_20260718.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_external_strength_values_20260718.csv"),
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def metadata_version(pyjhora_root: Path) -> str:
    candidates = list(pyjhora_root.glob("PyJHora-*.dist-info/METADATA"))
    if len(candidates) != 1:
        raise RuntimeError("Expected exactly one PyJHora METADATA file.")
    for line in candidates[0].read_text(encoding="utf-8").splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("PyJHora METADATA has no Version field.")


def require_pinned_install(pyjhora_root: Path, wheel: Path) -> str:
    if not pyjhora_root.is_dir():
        raise FileNotFoundError(f"PyJHora root does not exist: {pyjhora_root}")
    if not wheel.is_file():
        raise FileNotFoundError(f"PyJHora wheel does not exist: {wheel}")
    version = metadata_version(pyjhora_root)
    if version != PYJHORA_VERSION:
        raise RuntimeError(f"Expected PyJHora {PYJHORA_VERSION}, found {version}.")
    digest = sha256(wheel)
    if digest != PYJHORA_WHEEL_SHA256:
        raise RuntimeError(f"PyJHora wheel hash mismatch: {digest}")
    return digest


def civil_time_parts(fixture: Fixture) -> tuple[tuple[int, int, int], tuple[int, int, int], float]:
    local = datetime.fromisoformat(fixture.local_iso).replace(tzinfo=ZoneInfo(fixture.timezone))
    offset = local.utcoffset()
    if offset is None:
        raise RuntimeError(f"Timezone has no UTC offset for {fixture.sample_id}.")
    return (
        (local.year, local.month, local.day),
        (local.hour, local.minute, local.second),
        offset.total_seconds() / 3600.0,
    )


def assert_bvraman_reference(utils: Any, strength: Any, drik: Any) -> list[float]:
    drik.set_ayanamsa_mode("RAMAN")
    jd = utils.julian_day_number((1918, 10, 16), (14, 22, 16))
    place = drik.Place("Bangalore B.V. Raman reference", 13.0, 77 + 35 / 60, 5.5)
    actual = [float(value) for value in strength._drik_bala(jd, place)]
    deltas = [abs(value - expected) for value, expected in zip(actual, BVRAMAN_DRIK_EXPECTED)]
    if len(actual) != len(BVRAMAN_DRIK_EXPECTED) or max(deltas) > BVRAMAN_DRIK_TOLERANCE:
        raise RuntimeError(
            "PyJHora B.V. Raman Drik reference failed: "
            f"actual={actual}, expected={list(BVRAMAN_DRIK_EXPECTED)}, deltas={deltas}"
        )
    return actual


def calculate_strengths(pyjhora_root: Path) -> dict[tuple[str, str], float]:
    sys.path.insert(0, str(pyjhora_root))
    from jhora import utils
    from jhora.horoscope.chart import strength
    from jhora.panchanga import drik

    assert_bvraman_reference(utils, strength, drik)
    values: dict[tuple[str, str], float] = {}
    for fixture in FIXTURES:
        date_parts, time_parts, utc_offset_hours = civil_time_parts(fixture)
        drik.set_ayanamsa_mode("RAMAN")
        jd = utils.julian_day_number(date_parts, time_parts)
        place = drik.Place(
            fixture.location,
            fixture.latitude,
            fixture.longitude,
            utc_offset_hours,
        )
        drik_values = [float(value) for value in strength._drik_bala(jd, place)]
        shadbala_values = [float(value) for value in strength.shad_bala(jd, place)[6]]
        if len(drik_values) != len(PLANETS) or len(shadbala_values) != len(PLANETS):
            raise RuntimeError(f"Unexpected PyJHora strength vector for {fixture.sample_id}.")
        for index, planet in enumerate(PLANETS):
            values[(fixture.sample_id, f"shadbala_implemented_total_virupa.{planet}")] = (
                shadbala_values[index]
            )
            values[(fixture.sample_id, f"drik_bala_virupa.{planet}")] = drik_values[index]
    return values


def merge_strength_rows(
    rows: list[dict[str, str]],
    values: dict[tuple[str, str], float],
    source: str,
) -> tuple[list[dict[str, str]], int]:
    expected_keys = {
        (fixture.sample_id, f"{prefix}{planet}")
        for fixture in FIXTURES
        for prefix in STRENGTH_PREFIXES
        for planet in PLANETS
    }
    if set(values) != expected_keys:
        missing = sorted(expected_keys - set(values))
        extra = sorted(set(values) - expected_keys)
        raise RuntimeError(f"Strength matrix mismatch: missing={missing}, extra={extra}")

    updated = 0
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for original in rows:
        row = dict(original)
        key = (row.get("sample_id", ""), row.get("feature_key", ""))
        if key in values:
            if key in seen:
                raise RuntimeError(f"Duplicate strength row in template: {key}")
            seen.add(key)
            row["external_expected_value"] = f"{values[key]:.9f}"
            row["external_source"] = source
            row["pass_fail"] = "pending_gate_comparison"
            base_note = str(row.get("notes") or "").split(" | numeric delta=", 1)[0]
            row["notes"] = (
                f"{base_note} | Independent PyJHora Raman-mode export; "
                "shad_bala()[6] total or private _drik_bala() value."
            )
            updated += 1
        result.append(row)
    if seen != expected_keys:
        raise RuntimeError(f"Template is missing strength rows: {sorted(expected_keys - seen)}")
    return result, updated


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"CSV has no header: {path}")
        return list(reader.fieldnames), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    wheel_hash = require_pinned_install(args.pyjhora_root, args.wheel)
    fieldnames, rows = read_csv(args.template)
    values = calculate_strengths(args.pyjhora_root)
    source = (
        f"PyJHora {PYJHORA_VERSION} Tier B isolated export; Raman ayanamsa; "
        f"wheel sha256 {wheel_hash}; event civil timezone; Tokyo reference coordinates"
    )
    merged, updated = merge_strength_rows(rows, values, source)
    if updated != len(FIXTURES) * len(PLANETS) * len(STRENGTH_PREFIXES):
        raise RuntimeError(f"Expected 70 strength updates, wrote {updated}.")
    write_csv(args.output, fieldnames, merged)
    print(
        json.dumps(
            {
                "contract": "GANN_PYJHORA_EXTERNAL_STRENGTH_EXPORT_V1",
                "pyjhoraVersion": PYJHORA_VERSION,
                "wheelSha256": wheel_hash,
                "ayanamsa": "RAMAN",
                "fixtures": len(FIXTURES),
                "strengthRows": updated,
                "output": str(args.output.resolve()),
                "outputSha256": sha256(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
