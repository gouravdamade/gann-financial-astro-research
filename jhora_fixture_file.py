from __future__ import annotations

import argparse
from datetime import datetime, time
from pathlib import Path
from typing import Iterable

from pyjhora_external_strength_export import FIXTURES


JHD_TIME_LINE_INDEX = 3
DEFAULT_FIXTURE_DIR = (
    Path(__file__).resolve().parent
    / "status"
    / "evidence"
    / "jhora_kaala_witness_20260727"
)
FIXTURE_FILENAMES = {
    "case_8_event_start": "case_8_event_start_locked.jhd",
    "case_43_event_start": "case_43_event_start_locked.jhd",
    "case_103_event_start": "case_103_event_start_locked.jhd",
    "case_127_sr_touch_start": "case_127_sr_touch_start_locked.jhd",
    "gann_reference_tokyo": "gann_reference_tokyo_locked.jhd",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate or correct JHora .jhd packed clock fields against the "
            "locked Gate-3 fixture timestamps."
        )
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Correct only the packed clock line in mismatched fixture files.",
    )
    return parser.parse_args()


def format_jhd_packed_time(value: time) -> str:
    """Encode HH:MM:SS as JHora's HH.MMSS packed decimal text."""
    if value.tzinfo is not None:
        raise ValueError("JHora packed local time must be timezone-naive")
    packed_digits = (
        f"{value.minute:02d}"
        f"{value.second:02d}"
        f"{value.microsecond:06d}"
    )
    return f"{value.hour}.{packed_digits:<015}"


def parse_jhd_packed_time(raw: str) -> time:
    value = raw.strip()
    if not value or value.startswith("-"):
        raise ValueError(f"invalid JHora packed time: {raw!r}")
    hour_text, separator, fraction = value.partition(".")
    if not separator:
        fraction = ""
    digits = "".join(character for character in fraction if character.isdigit())
    digits = digits.ljust(10, "0")
    hour = int(hour_text)
    minute = int(digits[:2])
    second = int(digits[2:4])
    microsecond = int(digits[4:10])
    return time(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
    )


def expected_fixture_time(local_iso: str) -> time:
    return datetime.fromisoformat(local_iso).time()


def fixture_time(path: Path) -> time:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) <= JHD_TIME_LINE_INDEX:
        raise ValueError(f"JHora fixture is truncated: {path}")
    return parse_jhd_packed_time(lines[JHD_TIME_LINE_INDEX])


def validate_fixture_time(
    path: Path,
    *,
    sample_id: str,
    local_iso: str,
) -> list[str]:
    if not path.is_file():
        return [f"{sample_id}: missing JHora fixture {path}"]
    expected = expected_fixture_time(local_iso)
    try:
        observed = fixture_time(path)
    except ValueError as exc:
        return [f"{sample_id}: {exc}"]
    if observed != expected:
        return [
            (
                f"{sample_id}: JHora fixture clock {observed.isoformat()} "
                f"does not match locked local time {expected.isoformat()} "
                f"in {path}"
            )
        ]
    return []


def audit_fixture_times(fixture_dir: Path = DEFAULT_FIXTURE_DIR) -> list[str]:
    issues: list[str] = []
    fixtures_by_id = {fixture.sample_id: fixture for fixture in FIXTURES}
    if set(fixtures_by_id) != set(FIXTURE_FILENAMES):
        missing = sorted(set(fixtures_by_id) - set(FIXTURE_FILENAMES))
        extra = sorted(set(FIXTURE_FILENAMES) - set(fixtures_by_id))
        issues.append(
            f"JHora fixture filename map mismatch: missing={missing}, extra={extra}"
        )
    for sample_id, filename in FIXTURE_FILENAMES.items():
        fixture = fixtures_by_id.get(sample_id)
        if fixture is None:
            continue
        issues.extend(
            validate_fixture_time(
                fixture_dir / filename,
                sample_id=sample_id,
                local_iso=fixture.local_iso,
            )
        )
    return issues


def rewrite_fixture_time(path: Path, local_iso: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) <= JHD_TIME_LINE_INDEX:
        raise ValueError(f"JHora fixture is truncated: {path}")
    lines[JHD_TIME_LINE_INDEX] = format_jhd_packed_time(
        expected_fixture_time(local_iso)
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def rewrite_mismatched_fixture_times(
    fixture_dir: Path = DEFAULT_FIXTURE_DIR,
) -> list[Path]:
    rewritten: list[Path] = []
    fixtures_by_id = {fixture.sample_id: fixture for fixture in FIXTURES}
    for sample_id, filename in FIXTURE_FILENAMES.items():
        fixture = fixtures_by_id[sample_id]
        path = fixture_dir / filename
        if validate_fixture_time(
            path,
            sample_id=sample_id,
            local_iso=fixture.local_iso,
        ):
            rewrite_fixture_time(path, fixture.local_iso)
            rewritten.append(path)
    return rewritten


def require_exact_fixture_times(
    fixture_dir: Path = DEFAULT_FIXTURE_DIR,
) -> None:
    issues = audit_fixture_times(fixture_dir)
    if issues:
        raise RuntimeError("\n".join(issues))


def _display_paths(paths: Iterable[Path]) -> list[str]:
    return [str(path.resolve()) for path in paths]


def main() -> int:
    args = parse_args()
    rewritten: list[Path] = []
    if args.rewrite:
        rewritten = rewrite_mismatched_fixture_times(args.fixture_dir)
    issues = audit_fixture_times(args.fixture_dir)
    print(
        {
            "status": "valid" if not issues else "invalid",
            "fixtureDir": str(args.fixture_dir.resolve()),
            "rewritten": _display_paths(rewritten),
            "issues": issues,
        }
    )
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
