from __future__ import annotations

from shadbala_component_comparator import (
    compare_component_matrices,
    expected_component_keys,
    residual_summary,
)


def complete_matrix(value: float) -> dict[tuple[str, str, str], float]:
    return {key: value for key in expected_component_keys()}


def test_component_comparator_is_complete_numeric_and_strict() -> None:
    local = complete_matrix(10.0)
    external = complete_matrix(10.0)
    changed = sorted(external)[0]
    external[changed] = 10.51

    rows = compare_component_matrices(
        local,
        external,
        tolerance=0.5,
        source="pinned comparator",
    )

    assert len(rows) == 5 * 7 * 6
    assert sum(row["pass_fail"] == "fail" for row in rows) == 1
    failed = next(row for row in rows if row["pass_fail"] == "fail")
    assert (failed["sample_id"], failed["planet"], failed["component"]) == changed


def test_component_summary_keeps_each_component_separate() -> None:
    local = complete_matrix(10.0)
    external = complete_matrix(10.0)
    rows = compare_component_matrices(
        local,
        external,
        tolerance=0.5,
        source="pinned comparator",
    )

    summary = residual_summary(rows)

    assert set(summary) == {"sthana", "kaala", "dig", "chesta", "naisargika", "drik"}
    assert all(item["rows"] == 35 for item in summary.values())
    assert all(item["pass"] == 35 for item in summary.values())


def test_component_comparator_rejects_incomplete_matrix() -> None:
    local = complete_matrix(10.0)
    external = complete_matrix(10.0)
    external.pop(next(iter(external)))

    try:
        compare_component_matrices(
            local,
            external,
            tolerance=0.5,
            source="pinned comparator",
        )
    except RuntimeError as exc:
        assert "external component matrix mismatch" in str(exc)
    else:
        raise AssertionError("Incomplete external matrix must fail closed.")
