from __future__ import annotations

from decimal import Decimal

import pytest

from research_labs.trailokya_arghya.reconcile import (
    ArghyaExecutionLockedError,
    PASS_1972_PATH,
    _load_cells,
    calculate_reference_price_unit,
    evaluate_availability_direction,
    load_reconciliation_profile,
    parse_house_list,
    parse_viswa_kala,
    reconciliation_report,
    refuse_predicted_price,
)


def test_two_same_lineage_passes_reconcile_cell_for_cell() -> None:
    report = reconciliation_report()

    assert report["cells_per_pass"] == 108
    assert report["table_counts"] == {
        "relationship_vedha_viswa": 32,
        "planet_aspect_houses": 36,
        "five_class_vedha_viswa": 40,
    }
    assert report["cross_edition_mismatches"] == []
    assert report["independent_table_witness"]["source_id"].startswith(
        "KRISHNA_RAU_CHOUDHARY"
    )
    assert report["independent_worked_witness"] is None
    assert report["price_formula_certified"] is False
    assert report["execution_allowed"] is False


def test_viswa_kala_and_house_list_notations_are_kept_distinct() -> None:
    assert parse_viswa_kala("11|15") == Decimal("11.25")
    assert parse_viswa_kala("0|48") == Decimal("0.8")
    assert parse_house_list("3|10|7") == (3, 10, 7)
    assert parse_house_list("0") == ()
    with pytest.raises(ValueError):
        parse_viswa_kala("3|10|7")


def test_both_printed_scaling_anomalies_are_preserved_and_flagged() -> None:
    assert reconciliation_report()["source_preserved_anomalies"] == [
        {
            "cell": "relationship_vedha_viswa/three_quarter/malefic_neutral",
            "printed_value": "11|45",
            "proportional_expectation": "11|15",
        },
        {
            "cell": "five_class_vedha_viswa/three_quarter/malefic_4",
            "printed_value": "2|18",
            "proportional_expectation": "2|24",
        },
    ]


def test_independent_readings_never_silently_change_source_cells() -> None:
    report = reconciliation_report()
    findings = {
        item["cell"]: item for item in report["anomaly_witness_assessment"]
    }
    cells = {cell.key: cell for cell in _load_cells(PASS_1972_PATH)}

    assert findings[
        "relationship_vedha_viswa/three_quarter/malefic_neutral"
    ]["source_reading"] == "11|15"
    assert findings[
        "relationship_vedha_viswa/three_quarter/malefic_neutral"
    ]["correction_applied"] is False
    assert cells[
        ("relationship_vedha_viswa", "three_quarter", "malefic_neutral")
    ].raw_token == "11|45"

    assert findings[
        "five_class_vedha_viswa/three_quarter/malefic_4"
    ]["source_reading"] == "2|18"
    assert findings[
        "five_class_vedha_viswa/three_quarter/malefic_4"
    ]["assessment"] == "repeats_non_proportional_printing_unresolved"
    assert cells[
        ("five_class_vedha_viswa", "three_quarter", "malefic_4")
    ].raw_token == "2|18"


def test_planetary_aspect_table_preserves_printed_house_order() -> None:
    cells = {cell.key: cell for cell in _load_cells(PASS_1972_PATH)}

    assert cells[("planet_aspect_houses", "full", "mars")].raw_token == "4|8|7"
    assert cells[("planet_aspect_houses", "full", "saturn")].raw_token == "3|10|7"
    assert cells[("planet_aspect_houses", "half", "jupiter")].raw_token == "0"


def test_direction_only_sanity_fixture_never_becomes_a_price_prediction() -> None:
    result = evaluate_availability_direction(benefic_viswa=3, malefic_viswa=0)

    assert result.availability_index == Decimal("23")
    assert result.interpretation == "abundance_lower_price_pressure"
    assert result.predicted_price is None
    assert result.market_label_allowed is False
    assert result.execution_allowed is False

    scarcity = evaluate_availability_direction(benefic_viswa=0, malefic_viswa=2)
    assert scarcity.availability_index == Decimal("18")
    assert scarcity.interpretation == "scarcity_higher_price_pressure"


def test_witnessed_twentieth_is_exposed_only_as_a_research_unit() -> None:
    unit = calculate_reference_price_unit("2041")

    assert unit.divisor == Decimal("20")
    assert unit.fraction == Decimal("0.05")
    assert unit.percent == Decimal("5")
    assert unit.unit_value == Decimal("102.05")
    assert unit.forecast_allowed is False
    assert unit.execution_allowed is False
    with pytest.raises(ValueError, match="must be positive"):
        calculate_reference_price_unit(0)


def test_dated_silver_example_is_partial_evidence_not_a_formula_certificate() -> None:
    report = reconciliation_report()
    silver = next(
        item
        for item in report["worked_example_evidence"]
        if item["example_id"] == "silver_bombay_1951_05_12_to_1951_05_14"
    )

    assert silver["base_price_printed"] == "2041"
    assert silver["target_price_printed"] == "2011"
    assert silver["observed_direction"] == "lower_price"
    assert silver["direction_consistent_with_abundance_rule"] is True
    assert silver["certifies_price_formula"] is False
    assert silver["reusable_prediction_allowed"] is False
    assert "final_score_to_price_working_page" in silver["missing_evidence"]


def test_profile_and_price_api_fail_closed() -> None:
    profile = load_reconciliation_profile()
    assert profile["execution_allowed"] is False
    assert profile["market_mapping_allowed"] is False
    assert profile["source_lineage"]["independent_worked_witness"] is None
    with pytest.raises(ArghyaExecutionLockedError, match="Direct predicted price is blocked"):
        refuse_predicted_price(reference_value=100, availability_index=23)
