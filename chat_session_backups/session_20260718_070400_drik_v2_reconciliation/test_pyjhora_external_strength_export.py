from __future__ import annotations

from pyjhora_external_strength_export import (
    FIXTURES,
    PLANETS,
    STRENGTH_PREFIXES,
    merge_strength_rows,
)


def complete_matrix() -> dict[tuple[str, str], float]:
    return {
        (fixture.sample_id, f"{prefix}{planet}"): float(index)
        for index, (fixture, prefix, planet) in enumerate(
            (
                (fixture, prefix, planet)
                for fixture in FIXTURES
                for prefix in STRENGTH_PREFIXES
                for planet in PLANETS
            ),
            start=1,
        )
    }


def test_merge_fills_exact_strength_matrix_and_preserves_other_rows() -> None:
    values = complete_matrix()
    rows = [
        {
            "gate": "Gate 3",
            "sample_id": sample_id,
            "feature_key": feature_key,
            "local_value": "0",
            "external_expected_value": "",
            "external_source": "",
            "pass_fail": "pending",
            "notes": "fixture",
        }
        for sample_id, feature_key in values
    ]
    rows.append(
        {
            "gate": "Gate 3",
            "sample_id": "case_8_event_start",
            "feature_key": "tithi_name",
            "local_value": "Navami",
            "external_expected_value": "Navami",
            "external_source": "existing",
            "pass_fail": "pass",
            "notes": "preserve me",
        }
    )

    merged, updated = merge_strength_rows(rows, values, "PyJHora test source")

    assert updated == 70
    assert merged[-1] == rows[-1]
    assert all(
        row["external_source"] == "PyJHora test source"
        for row in merged[:-1]
    )
    assert all(row["external_expected_value"] for row in merged[:-1])
