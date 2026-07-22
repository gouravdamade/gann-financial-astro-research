from __future__ import annotations

from decimal import Decimal

import pytest

from research_labs.trailokya_arghya.reconcile import (
    ArghyaExecutionLockedError,
    PASS_1972_PATH,
    _load_cells,
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
    assert report["independent_worked_witness"] is None
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


def test_profile_and_price_api_fail_closed() -> None:
    profile = load_reconciliation_profile()
    assert profile["execution_allowed"] is False
    assert profile["market_mapping_allowed"] is False
    assert profile["source_lineage"]["independent_worked_witness"] is None
    with pytest.raises(ArghyaExecutionLockedError, match="Direct predicted price is blocked"):
        refuse_predicted_price(reference_value=100, availability_index=23)
