from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from sbc.grid import (
    ALLOWED_ENTRY_LAYERS,
    SBC_NAME_INITIALS_20,
    SBC_VOWELS_16,
    compile_grid,
    load_grid_profile,
    validate_grid_profile,
)


PROFILE_ID = "sbc_81_rotation_normalized_partial_v1"

VOWEL_FIXTURE = (
    (1, 1, "A", "अ", "a"),
    (1, 9, "AA", "आ", "aa"),
    (9, 9, "I", "इ", "i"),
    (9, 1, "II", "ई", "ii"),
    (2, 2, "U", "उ", "u"),
    (2, 8, "UU", "ऊ", "uu"),
    (8, 8, "VOCALIC_R", "ऋ", "r"),
    (8, 2, "LONG_VOCALIC_R", "ॠ", "rr"),
    (3, 3, "VOCALIC_L", "ऌ", "l"),
    (3, 7, "LONG_VOCALIC_L", "ॡ", "ll"),
    (7, 7, "E", "ए", "e"),
    (7, 3, "AI", "ऐ", "ai"),
    (4, 4, "O", "ओ", "o"),
    (4, 6, "AU", "औ", "au"),
    (6, 6, "ANUSVARA", "अं", "am"),
    (6, 4, "VISARGA", "अः", "ah"),
)

NAME_INITIAL_FIXTURE = (
    (2, 3, "A", "अ", "a"),
    (2, 4, "VA", "व", "va"),
    (2, 5, "KA", "क", "ka"),
    (2, 6, "HA", "ह", "ha"),
    (2, 7, "DDA", "ड", "dda"),
    (3, 8, "MA", "म", "ma"),
    (4, 8, "TTA", "ट", "tta"),
    (5, 8, "PA", "प", "pa"),
    (6, 8, "RA", "र", "ra"),
    (7, 8, "TA", "त", "ta"),
    (8, 7, "NA", "न", "na"),
    (8, 6, "YA", "य", "ya"),
    (8, 5, "BHA", "भ", "bha"),
    (8, 4, "JA", "ज", "ja"),
    (8, 3, "KHA", "ख", "kha"),
    (7, 2, "GA", "ग", "ga"),
    (6, 2, "SA", "स", "sa"),
    (5, 2, "DA", "द", "da"),
    (4, 2, "CHA", "च", "cha"),
    (3, 2, "LA", "ल", "la"),
)


def _entry(grid, row: int, column: int, layer: str):
    matches = [
        entry for entry in grid.cell(row, column).entries if entry.layer == layer
    ]
    assert len(matches) == 1
    return matches[0]


def test_page_certified_vowels_have_exact_nested_corner_positions() -> None:
    grid = compile_grid(PROFILE_ID)
    actual = []
    for row, column, token, glyph, transliteration in VOWEL_FIXTURE:
        entry = _entry(grid, row, column, "VOWEL")
        actual.append(entry.value)
        assert entry.value == token
        assert entry.glyph == glyph
        assert entry.transliteration == transliteration
        assert entry.semantic_role == "SANSKRIT_VOWEL"
    assert tuple(actual) == SBC_VOWELS_16


def test_name_initial_ring_has_exact_positions_and_source_order() -> None:
    grid = compile_grid(PROFILE_ID)
    actual = []
    for row, column, token, glyph, transliteration in NAME_INITIAL_FIXTURE:
        entry = _entry(grid, row, column, "NAME_INITIAL")
        actual.append(entry.value)
        assert entry.value == token
        assert entry.glyph == glyph
        assert entry.transliteration == transliteration
    assert tuple(actual) == SBC_NAME_INITIALS_20


def test_source_labeled_consonant_ring_exposes_its_vowel_exception() -> None:
    grid = compile_grid(PROFILE_ID)
    first = _entry(grid, 2, 3, "NAME_INITIAL")
    assert first.value == "A"
    assert first.glyph == "अ"
    assert first.semantic_role == "VOWEL_EXCEPTION_IN_NAME_INITIAL_RING"
    remaining = [
        entry
        for cell in grid.cells
        for entry in cell.entries
        if entry.layer == "NAME_INITIAL" and entry.value != "A"
    ]
    assert len(remaining) == 19
    assert all(entry.semantic_role == "CONSONANT_NAME_INITIAL" for entry in remaining)


def test_every_letter_entry_has_both_held_page_witnesses() -> None:
    grid = compile_grid(PROFILE_ID)
    letters = [
        entry
        for cell in grid.cells
        for entry in cell.entries
        if entry.layer in {"VOWEL", "NAME_INITIAL"}
    ]
    assert len(letters) == 36
    assert all(
        entry.witness_set_id == "LETTER_LAYERS_TRANSCRIPTION_CERTIFIED"
        for entry in letters
    )
    assert all(
        entry.evidence_status
        == "TWO_WITNESS_PAGE_CERTIFIED_TRANSCRIPTION_AGREEMENT_AFTER_ROTATION"
        for entry in letters
    )
    assert all(len(entry.citations) == 2 for entry in letters)
    assert all(
        {citation.source_id for citation in entry.citations}
        == {
            "PHALADEEPIKA_1937_SBC_EDITOR_SUPPLEMENT",
            "SANJAY_RATH_CRUX_1998_SBC_FIGURE",
        }
        for entry in letters
    )


def test_letter_fields_fail_closed_on_missing_or_misclassified_data() -> None:
    definition = load_grid_profile(PROFILE_ID)
    raw = copy.deepcopy(definition.raw)
    vowel = next(entry for entry in raw["entries"] if entry["layer"] == "VOWEL")
    del vowel["glyph"]
    with pytest.raises(ValueError, match="require glyph"):
        validate_grid_profile(raw)

    raw = copy.deepcopy(definition.raw)
    initial_a = next(
        entry
        for entry in raw["entries"]
        if entry["layer"] == "NAME_INITIAL" and entry["value"] == "A"
    )
    initial_a["semantic_role"] = "CONSONANT_NAME_INITIAL"
    with pytest.raises(ValueError, match="VOWEL_EXCEPTION_IN_NAME_INITIAL_RING"):
        validate_grid_profile(raw)

    raw = copy.deepcopy(definition.raw)
    structural = next(
        entry for entry in raw["entries"] if entry["layer"] == "NAKSHATRA"
    )
    structural["glyph"] = "x"
    with pytest.raises(ValueError, match="cannot carry letter transcription"):
        validate_grid_profile(raw)


def test_json_schema_and_runtime_accept_the_same_entry_layers() -> None:
    schema_path = (
        Path(__file__).resolve().parent
        / "configs"
        / "sbc"
        / "schemas"
        / "grid-profile.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    entries_schema = schema["properties"]["entries"]["items"]
    certified_schema = schema["properties"]["certified_layers"]
    assert set(entries_schema["properties"]["layer"]["enum"]) == (ALLOWED_ENTRY_LAYERS)
    assert set(certified_schema["items"]["enum"]) == ALLOWED_ENTRY_LAYERS
    assert set(entries_schema["allOf"][0]["then"]["required"]) == {
        "glyph",
        "transliteration",
        "semantic_role",
    }


def test_letter_certification_does_not_unlock_orientation_or_trading() -> None:
    grid = compile_grid(PROFILE_ID)
    assert grid.complete is False
    assert tuple(item.layer for item in grid.unresolved_layers) == (
        "CARDINAL_ORIENTATION",
    )
    assert "CARDINAL_ORIENTATION" in grid.blocked_capabilities
    assert "TRADES" in grid.blocked_capabilities
    assert "MT5_EXECUTION" in grid.blocked_capabilities
    encoded = json.dumps(grid.to_dict(), ensure_ascii=False).lower()
    for forbidden in ("bullish", "bearish", "entry_price", "order_send"):
        assert forbidden not in encoded
