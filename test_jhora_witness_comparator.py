from __future__ import annotations

from jhora_witness_comparator import (
    build_comparison_rows,
    build_independent_drik_rows,
    comparison_summary,
)


def test_locked_witness_comparison_has_expected_fixed_tolerance_result() -> None:
    rows = build_comparison_rows()
    summary = comparison_summary(rows)

    assert len(rows) == 245
    assert summary["toleranceVirupa"] == 0.5
    assert summary["overall"]["pass"] == 108
    assert summary["overall"]["fail"] == 137
    assert {
        measure: (result["pass"], result["fail"])
        for measure, result in summary["byMeasure"].items()
    } == {
        "sthana": (33, 2),
        "kaala": (0, 35),
        "dig": (19, 16),
        "chesta": (12, 23),
        "naisargika": (35, 0),
        "drik": (9, 26),
        "total": (0, 35),
    }


def test_independent_drik_rows_fail_closed_without_pyjhora_values() -> None:
    rows = build_independent_drik_rows()

    assert len(rows) == 35
    assert sum(row["pass_fail"] == "pass" for row in rows) == 9
    assert sum(row["pass_fail"] == "fail" for row in rows) == 26
    assert all("Independent Jagannatha Hora" in row["external_source"] for row in rows)
    assert all("no PyJHora values used" in row["notes"] for row in rows)
