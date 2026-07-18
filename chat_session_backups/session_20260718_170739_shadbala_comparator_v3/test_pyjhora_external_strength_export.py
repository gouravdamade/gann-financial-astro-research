from __future__ import annotations

from pyjhora_external_strength_export import (
    FIXTURES,
    KAALA_SUBCOMPONENTS,
    PLANETS,
    SHADBALA_COMPONENTS,
    STRENGTH_PREFIXES,
    component_rows_from_vectors,
    formula_input_row,
    kaala_rows_from_vectors,
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


def test_merge_strength_rows_is_note_idempotent() -> None:
    values = complete_matrix()
    provenance = (
        "Independent PyJHora Raman-mode export; shad_bala()[6] total or "
        "private _drik_bala() value."
    )
    rows = [
        {
            "gate": "Gate 3",
            "sample_id": sample_id,
            "feature_key": feature_key,
            "local_value": "0",
            "external_expected_value": "",
            "external_source": "",
            "pass_fail": "pending",
            "notes": (
                "fixture | No external expected value entered. | "
                f"{provenance} | {provenance}"
            ),
        }
        for sample_id, feature_key in values
    ]

    first, _ = merge_strength_rows(rows, values, "PyJHora test source")
    second, _ = merge_strength_rows(first, values, "PyJHora test source")

    assert second == first
    assert all(row["notes"] == f"fixture | {provenance}" for row in second)


def test_component_rows_preserve_fixed_vector_order() -> None:
    vectors = [
        [component_index * 100 + planet_index for planet_index in range(len(PLANETS))]
        for component_index in range(len(SHADBALA_COMPONENTS))
    ]

    rows = component_rows_from_vectors("fixture", vectors, "pinned source")

    assert len(rows) == len(SHADBALA_COMPONENTS) * len(PLANETS)
    assert rows[0] == {
        "sample_id": "fixture",
        "planet": "SUN",
        "component": "sthana",
        "external_value_virupa": "0.000000000",
        "source": "pinned source",
    }
    assert rows[-1]["component"] == "drik"
    assert rows[-1]["planet"] == "SATURN"
    assert rows[-1]["external_value_virupa"] == "506.000000000"


def test_component_rows_reject_incomplete_vectors() -> None:
    try:
        component_rows_from_vectors("fixture", [[1.0] * len(PLANETS)], "source")
    except RuntimeError as exc:
        assert "Shadbala vectors" in str(exc)
    else:
        raise AssertionError("Incomplete component vectors must fail closed.")


def test_kaala_rows_preserve_all_nine_parts_and_total() -> None:
    vectors = {
        measure: [
            measure_index * 100 + planet_index
            for planet_index in range(len(PLANETS))
        ]
        for measure_index, measure in enumerate(KAALA_SUBCOMPONENTS)
    }

    rows = kaala_rows_from_vectors("fixture", vectors, "pinned source")

    assert len(rows) == len(KAALA_SUBCOMPONENTS) * len(PLANETS)
    assert rows[0]["measure"] == "nathonnatha"
    assert rows[-1]["measure"] == "total"
    assert rows[-1]["planet"] == "SATURN"
    assert rows[-1]["external_value_virupa"] == "906.000000000"


def test_formula_input_row_records_linear_pyjhora_chesta_inputs() -> None:
    row = formula_input_row(
        sample_id="fixture",
        planet="MARS",
        planet_longitude_deg=100.0,
        chesta_true_longitude_deg=95.0,
        ascendant_longitude_deg=20.0,
        classical_longitudes={"MARS": 100.0, "SUN": 10.0},
        mean_sun_longitude_deg=340.0,
        mean_planet_longitude_deg=80.0,
        external_chesta_virupa=84.166666667,
        source="pinned source",
    )

    assert row["seegrocha_longitude_deg"] == "340.000000000000"
    assert row["mean_true_midpoint_linear_deg"] == "87.500000000000"
    assert row["reduced_chesta_kendra_deg"] == "252.500000000000"
    assert row["classical_longitudes_json"] == '{"MARS":100.0,"SUN":10.0}'
