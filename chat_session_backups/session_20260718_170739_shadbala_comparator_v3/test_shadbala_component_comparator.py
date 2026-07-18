from __future__ import annotations

from shadbala_component_comparator import (
    compare_component_matrices,
    compare_kaala_matrices,
    expected_component_keys,
    expected_kaala_keys,
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
    assert sum(row["pass_fail"] == "structural_n_a" for row in rows) == 10
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
    assert summary["chesta"]["comparable"] == 25
    assert summary["chesta"]["pass"] == 25
    assert summary["chesta"]["structuralNA"] == 10
    assert all(
        item["pass"] == 35
        for component, item in summary.items()
        if component != "chesta"
    )


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


def test_kaala_comparator_keeps_ten_measures_separate() -> None:
    local = {key: 12.0 for key in expected_kaala_keys()}
    external = dict(local)
    changed = sorted(external)[-1]
    external[changed] = 13.0

    rows = compare_kaala_matrices(
        local,
        external,
        tolerance=0.5,
        source="pinned comparator",
    )
    summary = residual_summary(rows, group_field="measure")

    assert len(rows) == 5 * 7 * 10
    assert sum(row["pass_fail"] == "fail" for row in rows) == 1
    assert set(summary) == {
        "abda",
        "ayana",
        "hora",
        "masa",
        "nathonnatha",
        "paksha",
        "total",
        "tribhaga",
        "vara",
        "yuddha",
    }
