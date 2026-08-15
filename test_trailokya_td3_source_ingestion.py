"""Exact, static checks for bounded Trailokya TD3 source records."""
from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent / "configs" / "sbc" / "trailokya"
PRIMARY_HASH = "1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194"


def _load(name: str) -> dict:
    value = yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_td3_foundation_keeps_candidate_rulers_and_strength_layers_exact() -> None:
    foundation = _load("trailokya_1972_arghya_foundation_v1.yaml")
    assert foundation["source"]["sha256"] == PRIMARY_HASH
    candidates = foundation["records"][2]["candidates"]
    assert candidates == {
        "DESA": ["RAHU", "SATURN", "JUPITER"], "MANDALA": ["KETU", "SUN", "VENUS"],
        "STHANA": ["MOON", "MARS", "MERCURY"], "YEAR": ["RAHU", "KETU", "SATURN", "JUPITER"],
        "MONTH": ["MARS", "SUN", "MERCURY", "VENUS"], "DAY": ["MOON"],
        "DHATU": ["SATURN", "RAHU", "MARS"], "MULA": ["KETU", "VENUS", "SUN"],
        "JIVA": ["MERCURY", "MOON", "JUPITER"],
    }
    assert foundation["records"][4]["basePadas"] == {"OWN": "4/4", "FRIEND": "3/4", "NEUTRAL": "2/4", "ENEMY": "1/4"}
    assert foundation["executionAllowed"] is False


def test_td3_viswa_is_arghya_scoped_and_not_a_generic_score() -> None:
    viswa = _load("trailokya_1972_arghya_viswa_v1.yaml")
    relation = viswa["records"][0]
    assert relation["beneficFractions"] == {"SELF": "4/4", "FRIEND": "3/4", "NEUTRAL": "2/4", "ENEMY": "1/4"}
    assert relation["maleficFractions"] == {"SELF": "1/4", "FRIEND": "2/4", "NEUTRAL": "3/4", "ENEMY": "4/4"}
    assert viswa["records"][1]["rule"] == "GEOMETRIC_VEDHA_WITHOUT_REQUIRED_ZODIACAL_ASPECT_HAS_NO_ARGHYA_RESULT"
    assert viswa["records"][3]["universalReducer"] == "PROHIBITED"
    assert viswa["executionAllowed"] is False


def test_td3_commodity_ledger_is_exactly_28_rows_and_stays_non_market() -> None:
    ledger = _load("trailokya_1972_nakshatra_commodity_ledger_v1.yaml")
    entries = ledger["entries"]
    assert [(entry["verse"], entry["nakshatra"], entry["direction"], entry["duration"]) for entry in entries] == [
        (379, "KRITTIKA", "SOUTH", "8_MONTHS"), (380, "ROHINI", "EAST", "7_DAYS"),
        (381, "MRIGASHIRSHA", "NORTH", "60_DAYS"), (382, "ARDRA", "WEST", "1_MONTH"),
        (383, "PUNARVASU", "NORTH", "2_MONTHS"), (384, "PUSHYA", "SOUTH", "8_MONTHS"),
        (385, "ASHLESHA", "WEST", "1_MONTH"), (386, "MAGHA", "SOUTH", "8_MONTHS"),
        (387, "PURVA_PHALGUNI", "SOUTH", "8_MONTHS"), (388, "UTTARA_PHALGUNI", "NORTH", "2_MONTHS"),
        (389, "HASTA", "NORTH", "2_MONTHS"), (390, "CHITRA", "NORTH", "2_MONTHS"),
        (391, "SWATI", "NORTH", "7_DAYS"), (392, "VISHAKHA", "SOUTH", "8_MONTHS"),
        (393, "ANURADHA", "EAST", "7_DAYS"), (394, "JYESHTHA", "EAST", "7_DAYS"),
        (395, "MULA", "WEST", "1_MONTH"), (396, "PURVA_ASHADHA", "WEST", "1_MONTH"),
        (397, "UTTARA_ASHADHA", "EAST", "7_DAYS"), (398, "ABHIJIT", "EAST", "7_DAYS"),
        (399, "SHRAVANA", "EAST", "7_DAYS"), (400, "DHANISHTHA", "EAST", "7_DAYS"),
        (401, "SHATABHISHA", "WEST", "1_MONTH"), (402, "PURVA_BHADRAPADA", "SOUTH", "8_MONTHS"),
        (403, "UTTARA_BHADRAPADA", "WEST", "1_MONTH"), (404, "REVATI", "WEST", "1_MONTH"),
        (405, "ASHVINI", "NORTH", "2_MONTHS"), (406, "BHARANI", "SOUTH", "8_MONTHS"),
    ]
    assert ledger["status"] == "FINANCIAL_HYPOTHESIS_LEDGER_ONLY"
    assert "FX_MAPPING" in ledger["prohibitedUses"]
    assert ledger["executionAllowed"] is False
    assert [entry["locator"]["printedPage"] for entry in entries] == [
        87, 87, 87, 88, 88, 88, 88, 88, 89, 89, 89, 89, 89, 90,
        90, 90, 90, 90, 91, 91, 91, 91, 91, 91, 92, 92, 92, 92,
    ]


def test_td3_audit_locks_and_descriptive_material_remain_non_runtime() -> None:
    audit = _load("trailokya_1972_td3_source_audit_v1.yaml")
    assert audit["auditedPassages"]["descriptiveMaterial"]["status"] == "DESCRIPTIVE_ONLY_NOT_COMPUTATIONAL"
    assert all(value is False for value in audit["locks"].values())
    assert "TD3_COMMODITY_RECORDS_MUST_NOT_BE_MAPPED_TO_FX_OR_MARKET_POLARITY" in audit["nonMergeRules"]
