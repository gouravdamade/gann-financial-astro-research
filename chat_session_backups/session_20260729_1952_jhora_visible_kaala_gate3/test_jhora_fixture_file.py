from __future__ import annotations

from datetime import time
from pathlib import Path

from jhora_fixture_file import (
    audit_fixture_times,
    fixture_time,
    format_jhd_packed_time,
    parse_jhd_packed_time,
    rewrite_fixture_time,
)


def _fixture_text(packed_time: str) -> str:
    return "\n".join(
        (
            "3",
            "7",
            "2025",
            packed_time,
            "-5.300000",
            "-139.390180",
            "35.405720",
            "0.000000",
            "-5.500000",
            "-5.500000",
            "0",
            "271",
            "Tokyo",
            "Massachusetts,^USA",
            "1",
            "1013.250000",
            "20.000000",
            "0",
            "",
        )
    )


def test_jhora_packed_clock_is_not_decimal_hours() -> None:
    assert parse_jhd_packed_time("19.500000000000000") == time(19, 50)
    assert parse_jhd_packed_time("19.300000000000000") == time(19, 30)
    assert format_jhd_packed_time(time(19, 30)) == "19.300000000000000"


def test_rewrite_fixture_time_preserves_non_time_lines(tmp_path: Path) -> None:
    path = tmp_path / "case_8_event_start_locked.jhd"
    original = _fixture_text("19.500000000000000")
    path.write_text(original, encoding="utf-8")

    rewrite_fixture_time(path, "2025-03-07T19:30:00")

    rewritten = path.read_text(encoding="utf-8")
    assert fixture_time(path) == time(19, 30)
    assert rewritten.replace(
        "19.300000000000000", "19.500000000000000"
    ) == original


def test_audit_reports_locked_clock_mismatches(tmp_path: Path) -> None:
    filenames = {
        "case_8_event_start_locked.jhd": "19.500000000000000",
        "case_43_event_start_locked.jhd": "2.300000000000000",
        "case_103_event_start_locked.jhd": "22.300000000000000",
        "case_127_sr_touch_start_locked.jhd": "22.000000000000000",
        "gann_reference_tokyo_locked.jhd": "0.000000000000000",
    }
    for filename, packed_time in filenames.items():
        (tmp_path / filename).write_text(
            _fixture_text(packed_time),
            encoding="utf-8",
        )

    issues = audit_fixture_times(tmp_path)

    assert len(issues) == 1
    assert "case_8_event_start" in issues[0]
    assert "19:50:00" in issues[0]
    assert "19:30:00" in issues[0]
