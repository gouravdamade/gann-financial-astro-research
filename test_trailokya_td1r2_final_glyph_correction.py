"""Regression gates for the two final TD1 source-glyph corrections."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "configs" / "sbc" / "trailokya"


def _load(name: str) -> dict:
    return yaml.safe_load((SOURCE_DIR / name).read_text(encoding="utf-8"))


def test_verse_48_keeps_the_retroflex_ssa_pair_and_never_pa_kha() -> None:
    pair = _load("trailokya_1972_special_expansion_rules_v1.yaml")["rules"][0]["pairs"][2]
    assert [(item["literalDevanagari"], item["canonicalToken"]) for item in pair] == [
        ("ष", "SSA_RETROFLEX"), ("ख", "KHA"),
    ]
    assert [item["canonicalToken"] for item in pair] != ["PA", "KHA"]


def test_jyeshtha_left_is_source_restored_to_visarga() -> None:
    rows = _load("trailokya_1972_vedha_target_map_v1.yaml")["rows"]
    jyeshtha = next(row for row in rows if row["source"] == "JYESHTHA")
    assert jyeshtha["left"] == [
        "NAME_INITIAL:YA", "RASHI:SAGITTARIUS", "VOWEL:VISARGA",
        "RASHI:PISCES", "NAME_INITIAL:CHA", "NAKSHATRA:ASHVINI",
    ]
    assert "VOWEL:ANUSVARA" not in jyeshtha["left"]
    assert jyeshtha["auditStatus"] == "TD1R2_SOURCE_RESTORED"


def test_anusvara_and_visarga_remain_distinct_in_each_contract_role() -> None:
    expansions = _load("trailokya_1972_special_expansion_rules_v1.yaml")
    assert expansions["rules"][2]["vowelPairs"][-1] == ["ANUSVARA", "VISARGA"]
    assert "ANUSVARA" != "VISARGA"
    correction = _load("trailokya_1972_td1r2_final_glyph_correction_v1.yaml")
    assert correction["corrections"][1]["corrected"] == "VISARGA"
    assert correction["historicalImpact"]["TD1R1_ADJUDICATION_TO_ANUSVARA_WAS_INCORRECT"] is True


def test_final_correction_preserves_all_product_and_execution_locks() -> None:
    correction = _load("trailokya_1972_td1r2_final_glyph_correction_v1.yaml")
    assert correction["startingCommit"] == "a829e3bf5e8733ef943f354c1bf575fc7b9a04a7"
    assert correction["controllingSource"]["sha256"] == "1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194"
    assert correction["readingWitness"]["sha256"] == "19CC2387C6C6B80E9A1F5A63BB9A71090A10FB17F3BD8BB56058210667F61ED8"
    assert correction["historicalImpact"]["runtimeBehaviorChanged"] is False
    assert correction["historicalImpact"]["productUIChanged"] is False
    assert correction["locks"]["executionAllowed"] is False
    assert set(correction["locks"]["prohibitedUses"]) == {
        "POLARITY", "SCORE_AGGREGATION", "PRICE_MAPPING", "FIELDS_POLARITY",
        "AUTO_SUGGEST", "ML", "MT5", "EXECUTION",
    }
    assert correction["finalTrustState"] == {
        "TRAILOKYA_NATIVE_TARGET_MAP_TRUSTED_FOR_SOURCE_CONTRACT": True,
        "TD1_TRANSLATION_SOURCE_CONTRACT_CLOSED": True,
        "READY_FOR_TD2_TRANSLATION": True,
        "nextSourceRange": "1972 scan pages 52-62 / printed pages 36-46",
    }
