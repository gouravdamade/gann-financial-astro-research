"""Source-contract checks for the bounded Trailokya TD2R extraction.

These tests intentionally inspect static evidence records only.  They must not
instantiate a guidance engine, an Arghya calculation, or any market path.
"""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
TRAILOKYA = ROOT / "configs" / "sbc" / "trailokya"
PRIMARY_HASH = "1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194"


def _load(name: str) -> dict:
    data = yaml.safe_load((TRAILOKYA / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_td2_contracts_use_the_controlling_1972_witness_and_stay_locked() -> None:
    for name in (
        "trailokya_1972_vedha_magnitude_v1.yaml",
        "trailokya_1972_context_resolution_v1.yaml",
        "trailokya_1972_graha_latta_v1.yaml",
    ):
        contract = _load(name)
        assert contract["source"]["sha256"] == PRIMARY_HASH
        assert contract["source"]["citationAuthority"] == "ORIGINAL_1972_PAGE_IMAGE_ONLY"
        assert contract["runtimeBehaviorChanged"] is False
        assert contract["executionAllowed"] is False


def test_sthana_bala_phala_and_isolated_v166_records_remain_distinct() -> None:
    magnitude = _load("trailokya_1972_vedha_magnitude_v1.yaml")
    semantic = {item["id"]: item for item in magnitude["semantics"]}
    assert semantic["TD1972_V161_STHANA_BALA_FRACTIONS"]["values"] == {
        "OWN": "4/4", "FRIEND": "3/4", "SAMA_RELATIONSHIP": "2/4", "ENEMY": "1/4"
    }
    assert semantic["TD1972_V162_BALA_AND_PHALA_ARE_DISTINCT"]["rule"] == "BALA_IS_NOT_PHALA"
    assert semantic["TD1972_V163_SAUMYA_STHANA_PHALA"]["values"] == {
        "OWN": 20, "FRIEND": 15, "SAMA_RELATIONSHIP": 10, "ENEMY": 5
    }
    assert semantic["TD1972_V164_KRURA_STHANA_PHALA"]["values"] == {
        "OWN": 5, "FRIEND": 10, "SAMA_RELATIONSHIP": 15, "ENEMY": 20
    }
    assert semantic["TD1972_V165_STHANA_TO_VEDHA_RESULT_BRIDGE"]["rule"] == (
        "OBTAINED_PLANETARY_STHANA_PHALA_IS_THE_SOURCE_RESULT_MAGNITUDE_FOR_THE_STRUCK_TARGET"
    )
    assert magnitude["isolatedResultModifiers"]["rules"] == {
        "RETROGRADE": {"sourceResultFactor": 2, "sourceStatus": "SOURCE_CLOSED"},
        "EXALTATION": {"sourceResultFactor": 3, "sourceStatus": "SOURCE_CLOSED"},
        "SWIFT": {
            "sourceResult": "BASE_SOURCE_RESULT",
            "numericalFactor": "NOT_STATED_AS_1_0",
            "sourceStatus": "SOURCE_CLOSED",
        },
        "DEBILITATION": {"sourceResultFactor": 0.5, "sourceStatus": "SOURCE_CLOSED"},
    }
    assert magnitude["isolatedResultModifiers"]["combinationPolicy"] == "NOT_SOURCE_CLOSED"


def test_friendship_dignity_and_node_records_match_the_bounded_source_contract() -> None:
    magnitude = _load("trailokya_1972_vedha_magnitude_v1.yaml")
    assert magnitude["friendshipMatrix"] == {
        "locator": {
            "scanPage": 55,
            "printedPage": 39,
            "verses": "168-171",
            "layer": "ROOT_VERSE_AND_HINDI_COMMENTARY",
        },
        "SUN": {"friends": ["MOON", "MARS", "JUPITER"], "neutral": ["MERCURY"], "enemies": ["VENUS", "SATURN"]},
        "MOON": {"friends": ["SUN", "MERCURY"], "neutral": ["MARS", "JUPITER", "VENUS", "SATURN"], "enemies": []},
        "MARS": {"friends": ["SUN", "MOON", "JUPITER"], "neutral": ["VENUS", "SATURN"], "enemies": ["MERCURY"]},
        "MERCURY": {"friends": ["SUN", "VENUS"], "neutral": ["MARS", "JUPITER", "SATURN"], "enemies": ["MOON"]},
        "JUPITER": {"friends": ["SUN", "MOON", "MARS"], "neutral": ["SATURN"], "enemies": ["MERCURY", "VENUS"]},
        "VENUS": {"friends": ["MERCURY", "SATURN"], "neutral": ["MARS", "JUPITER"], "enemies": ["SUN", "MOON"]},
        "SATURN": {"friends": ["MERCURY", "VENUS"], "neutral": ["JUPITER"], "enemies": ["SUN", "MOON", "MARS"]},
        "sourceStatus": "SOURCE_CLOSED",
    }
    assert magnitude["signLords"] == {
        "locator": {
            "scanPage": 56,
            "printedPage": 40,
            "verses": "172-174",
            "layer": "ROOT_VERSE_AND_HINDI_COMMENTARY",
        },
        "ARIES": "MARS", "TAURUS": "VENUS", "GEMINI": "MERCURY", "CANCER": "MOON",
        "LEO": "SUN", "VIRGO": "MERCURY", "LIBRA": "VENUS", "SCORPIO": "MARS",
        "SAGITTARIUS": "JUPITER", "CAPRICORN": "SATURN", "AQUARIUS": "SATURN", "PISCES": "JUPITER",
        "sourceStatus": "SOURCE_CLOSED",
    }
    assert magnitude["dignity"]["planets"] == {
        "SUN": {"exaltationSign": "ARIES", "debilitationSign": "LIBRA", "paramoccaDegrees": 10},
        "MOON": {"exaltationSign": "TAURUS", "debilitationSign": "SCORPIO", "paramoccaDegrees": 3},
        "MARS": {"exaltationSign": "CAPRICORN", "debilitationSign": "CANCER", "paramoccaDegrees": 28},
        "MERCURY": {"exaltationSign": "VIRGO", "debilitationSign": "PISCES", "paramoccaDegrees": 15},
        "JUPITER": {"exaltationSign": "CANCER", "debilitationSign": "CAPRICORN", "paramoccaDegrees": 5},
        "VENUS": {"exaltationSign": "PISCES", "debilitationSign": "VIRGO", "paramoccaDegrees": 27},
        "SATURN": {"exaltationSign": "LIBRA", "debilitationSign": "ARIES", "paramoccaDegrees": 20},
    }
    assert magnitude["dignity"]["samaSthanaNotEquivalentTo"] == "SAMA_RELATIONSHIP"
    assert magnitude["nodes"]["RAHU"] == {
        "locator": {"scanPages": [57, 58], "printedPages": [41, 42], "verse": 178, "layer": "ROOT_VERSE_AND_HINDI_COMMENTARY"},
        "ownSign": "VIRGO", "exaltationSign": "GEMINI", "debilitationSign": "SAGITTARIUS", "resultsAndNatureLike": "SATURN",
    }
    assert magnitude["nodes"]["KETU"] == {
        "locator": {"scanPage": 58, "printedPage": 42, "verse": 179, "layer": "ROOT_VERSE_AND_HINDI_COMMENTARY"},
        "ownSign": "PISCES", "exaltationSign": "SAGITTARIUS", "debilitationSign": "GEMINI", "resultsLike": "RAHU",
        "relationship": {"mutualWithRahu": "FRIEND", "withOtherPlanets": "ENEMY"},
    }


def test_contexts_are_explicitly_scoped_and_not_a_generic_resolver() -> None:
    context = _load("trailokya_1972_context_resolution_v1.yaml")
    by_id = {item["id"]: item for item in context["contexts"]}
    assert by_id["TD1972_V146_MERCURY_RESULT_OVERRIDE"]["scope"] == "MERCURY_ONLY_PREVIOUS_AUSPICIOUS_RESULT_OVERRIDE"
    assert by_id["TD1972_V213_PRASHNA_LAGNA"]["scope"] == "PRASHNA_ONLY"
    assert by_id["TD1972_V209_WAR_FIRST_MOVER"]["scope"] == "WAR_ONLY"
    assert by_id["TD1972_V220_TO_V223_UBHAYATO_VEDHA"]["arithmetic"] == "NOT_STATED"
    assert by_id["TD1972_V246_COUNTRY_COMMODITY"]["prohibitedSubstitute"] == "TD2A_PHALA_COMPARISON_SHORTCUT"
    assert "TD1972_CONTEXT_RULES_ARE_NOT_A_GENERIC_RESOLVER" in context["unresolved"]


def test_latta_offsets_are_27_star_ordinal_rules_without_an_invented_origin() -> None:
    latta = _load("trailokya_1972_graha_latta_v1.yaml")
    assert latta["topology"] == {
        "eventType": "LATTA", "nakshatras": "ASHVINI_THROUGH_REVATI", "count": 27,
        "abhijit": "EXCLUDED", "geometry": "FORWARD_BACKWARD_ORDINAL_ONLY",
        "notEquivalentTo": ["LEFT_FRONT_RIGHT_VEDHA", "TD1_SEMANTIC_EXPANSIONS"],
        "countingOrigin": "UNRESOLVED",
    }
    assert latta["offsets"] == {
        "locator": {"scanPage": 75, "printedPage": 59, "verses": "261-262", "layer": "ROOT_VERSE_AND_HINDI_COMMENTARY"},
        "SUN": {"direction": "FORWARD", "offset": 12},
        "MARS": {"direction": "FORWARD", "offset": 3},
        "JUPITER": {"direction": "FORWARD", "offset": 6},
        "SATURN": {"direction": "FORWARD", "offset": 8},
        "MERCURY": {"direction": "BACKWARD", "offset": 7},
        "VENUS": {"direction": "BACKWARD", "offset": 5},
        "RAHU": {"direction": "BACKWARD", "offset": 9},
        "KETU": {"direction": "BACKWARD", "offset": 9},
        "FULL_MOON": {"direction": "BACKWARD", "offset": 22},
        "sourceStatus": "SOURCE_CLOSED",
    }
    assert latta["moonQualification"]["diminishedMoon"] == "NOT_ESTABLISHED_IN_HELD_LATTA_PASSAGE"
    assert "TD1972_LATTA_COUNTING_ORIGIN_UNRESOLVED" in latta["unresolved"]


def test_latta_outcomes_are_descriptive_and_the_upagraha_case_is_named_only() -> None:
    latta = _load("trailokya_1972_graha_latta_v1.yaml")
    assert latta["descriptivePlanetResults"]["sourceStatus"] == "SOURCE_CLOSED_DESCRIPTIVE_ONLY"
    assert latta["sunLattaOccupantTable"]["sourceStatus"] == "SOURCE_CLOSED_DESCRIPTIVE_ONLY"
    compound = latta["upagrahaCompound"]
    assert compound["requiredConditions"] == ["UPAGRAHA", "LATTA", "KRURA"]
    assert compound["MARGI"] == "DISEASE"
    assert compound["RETROGRADE"] == "DEATH"


def test_td2_readiness_preserves_all_fail_closed_boundaries() -> None:
    readiness = _load("trailokya_1972_td2_readiness.yaml")
    assert readiness["TD2_SOURCE_AUDIT_COMPLETE"] is True
    assert readiness["TD1972_VEDHA_MAGNITUDE_SOURCE_CONTRACT_TRUSTED"] is True
    assert readiness["TD1972_CONTEXT_RESOLUTION_SOURCE_CONTRACT_TRUSTED"] is True
    assert readiness["TD1972_GRAHA_LATTA_SOURCE_CONTRACT_TRUSTED"] is True
    assert readiness["TD1972_RUNTIME_PROMOTION"] == "NOT_AUTHORIZED"
    assert readiness["TD1972_EXECUTION_ALLOWED"] is False
    assert readiness["readyForTD3ArghyaWorkedReconstruction"] is False


def test_td2_audit_says_no_runtime_or_market_capability_was_added() -> None:
    audit = _load("trailokya_1972_td2_source_audit_v1.yaml")
    assert audit["auditedPassages"]["magnitude"]["status"] == "SOURCE_CLOSED"
    assert audit["auditedPassages"]["latta"]["status"] == "SOURCE_CLOSED_WITH_UNRESOLVED_COUNTING_ORIGIN"
    assert all(value is False for value in audit["locks"].values())
    assert "TD2_20_15_10_5_VEDHA_PHALA_MUST_NOT_BE_MERGED_WITH_LATER_ARGHYA_VISWA_OR_VIMSOPAKA" in audit["nonMergeRules"]
