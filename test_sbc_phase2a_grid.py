from __future__ import annotations

import copy
import json

import pytest

from sbc.grid import (
    SBC_NAKSHATRAS_28,
    SBC_RASHIS_12,
    GridProfileBlockedError,
    compile_grid,
    load_grid_profile,
    rotate_coordinate,
    validate_grid_profile,
)


PROFILE_ID = "sbc_81_rotation_normalized_partial_v1"


def _values(grid, row: int, column: int, layer: str) -> tuple[str, ...]:
    return tuple(
        entry.value for entry in grid.cell(row, column).entries if entry.layer == layer
    )


def test_partial_81_cell_fixture_is_explicit_reproducible_and_incomplete() -> None:
    definition = load_grid_profile(PROFILE_ID)
    first = compile_grid(definition)
    second = compile_grid(PROFILE_ID)
    assert definition.selection_policy == "EXPLICIT_ONLY"
    assert (
        definition.orientation["cardinal_binding"]
        == "UNRESOLVED_SOURCE_ROTATION_CONFLICT"
    )
    assert first.profile_hash == second.profile_hash
    assert first.rows == first.columns == 9
    assert len(first.cells) == 81
    assert first.complete is False
    assert set(first.certified_layers) == {
        "NAKSHATRA",
        "RASHI",
        "TITHI_GROUP",
        "WEEKDAY",
        "VOWEL",
        "NAME_INITIAL",
    }
    assert {item.layer for item in first.unresolved_layers} == {"CARDINAL_ORIENTATION"}
    assert "DEFAULT_PROFILE_SELECTION" in first.blocked_capabilities
    assert "TRADES" in first.blocked_capabilities


def test_outer_ring_has_all_28_nakshatras_in_source_figure_order() -> None:
    grid = compile_grid(PROFILE_ID)
    coordinates = (
        *((1, column) for column in range(2, 9)),
        *((row, 9) for row in range(2, 9)),
        *((9, column) for column in range(8, 1, -1)),
        *((row, 1) for row in range(8, 1, -1)),
    )
    actual = tuple(
        _values(grid, row, column, "NAKSHATRA")[0] for row, column in coordinates
    )
    assert actual == SBC_NAKSHATRAS_28
    assert _values(grid, 1, 1, "NAKSHATRA") == ()
    assert _values(grid, 1, 9, "NAKSHATRA") == ()
    assert _values(grid, 9, 1, "NAKSHATRA") == ()
    assert _values(grid, 9, 9, "NAKSHATRA") == ()


def test_rashi_ring_and_center_cross_match_the_page_fixtures() -> None:
    grid = compile_grid(PROFILE_ID)
    rashi_coordinates = (
        (3, 3),
        (3, 4),
        (3, 5),
        (4, 7),
        (5, 7),
        (6, 7),
        (7, 5),
        (7, 4),
        (7, 3),
        (6, 3),
        (5, 3),
        (4, 3),
    )
    rashis = tuple(
        _values(grid, row, column, "RASHI")[0] for row, column in rashi_coordinates
    )
    assert rashis == SBC_RASHIS_12

    assert _values(grid, 4, 5, "TITHI_GROUP") == ("NANDA",)
    assert _values(grid, 4, 5, "WEEKDAY") == ("SUNDAY", "TUESDAY")
    assert _values(grid, 5, 6, "TITHI_GROUP") == ("BHADRA",)
    assert _values(grid, 5, 6, "WEEKDAY") == ("MONDAY", "WEDNESDAY")
    assert _values(grid, 6, 5, "TITHI_GROUP") == ("JAYA",)
    assert _values(grid, 6, 5, "WEEKDAY") == ("THURSDAY",)
    assert _values(grid, 5, 4, "TITHI_GROUP") == ("RIKTA",)
    assert _values(grid, 5, 4, "WEEKDAY") == ("FRIDAY",)
    assert _values(grid, 5, 5, "TITHI_GROUP") == ("PURNA",)
    assert _values(grid, 5, 5, "WEEKDAY") == ("SATURDAY",)


def test_phaladeepika_cardinal_plate_is_rotation_normalized_not_silently_equated() -> (
    None
):
    grid = compile_grid(PROFILE_ID)
    plate_samples = {
        (2, 9): "KRITTIKA",
        (8, 9): "ASHLESHA",
        (9, 8): "MAGHA",
        (9, 2): "VISHAKHA",
        (8, 1): "ANURADHA",
        (2, 1): "SHRAVANA",
        (1, 2): "DHANISHTHA",
        (1, 8): "BHARANI",
    }
    for plate_coordinate, expected in plate_samples.items():
        row, column = rotate_coordinate(*plate_coordinate, 9, "ROTATE_CCW_90")
        assert _values(grid, row, column, "NAKSHATRA") == (expected,)
    assert grid.orientation["comparison_transform"] == "ROTATE_CCW_90"


def test_every_compiled_entry_resolves_page_citations() -> None:
    grid = compile_grid(PROFILE_ID)
    entries = [entry for cell in grid.cells for entry in cell.entries]
    assert entries
    assert all(len(entry.citations) == 2 for entry in entries)
    assert all(citation.locator for entry in entries for citation in entry.citations)
    assert set(grid.source_ids) == {
        "PHALADEEPIKA_1937_SBC_EDITOR_SUPPLEMENT",
        "SANJAY_RATH_CRUX_1998_SBC_FIGURE",
    }


def test_64_cell_metadata_loads_but_compilation_is_blocked() -> None:
    definition = load_grid_profile("sbc_64_blocked_v1")
    assert definition.grid_form == "SBC_64_CELL"
    assert definition.compile_enabled is False
    assert definition.entries == ()
    with pytest.raises(GridProfileBlockedError, match="page-certified 64-cell mapping"):
        compile_grid(definition)


def test_grid_validator_rejects_source_and_coverage_drift() -> None:
    raw = copy.deepcopy(load_grid_profile(PROFILE_ID).raw)
    raw["witness_sets"][0]["citations"][0]["source_id"] = "UNREGISTERED_SOURCE"
    with pytest.raises(ValueError, match="unresolved source ID"):
        validate_grid_profile(raw)

    raw = copy.deepcopy(load_grid_profile(PROFILE_ID).raw)
    raw["entries"] = [
        entry for entry in raw["entries"] if entry.get("value") != "KRITTIKA"
    ]
    with pytest.raises(ValueError, match="coverage mismatch"):
        validate_grid_profile(raw)

    raw = copy.deepcopy(load_grid_profile(PROFILE_ID).raw)
    raw["entries"][0]["layer"] = "VEDHA"
    with pytest.raises(ValueError, match="unsupported grid entry layer"):
        validate_grid_profile(raw)


def test_partial_grid_contains_no_market_opinion_or_execution_payload() -> None:
    encoded = json.dumps(compile_grid(PROFILE_ID).to_dict(), sort_keys=True).lower()
    for forbidden in ("bullish", "bearish", "entry_price", "profit_pips", "order_send"):
        assert forbidden not in encoded
