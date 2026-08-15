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
    assert magnitude["isolatedResultModifiers"]["rules"]["SWIFT"]["numericalFactor"] == "NOT_STATED_AS_1_0"
    assert magnitude["isolatedResultModifiers"]["combinationPolicy"] == "NOT_SOURCE_CLOSED"


def test_friendship_dignity_and_node_records_match_the_bounded_source_contract() -> None:
    magnitude = _load("trailokya_1972_vedha_magnitude_v1.yaml")
    assert magnitude["friendshipMatrix"]["MOON"]["enemies"] == []
    assert magnitude["friendshipMatrix"]["MERCURY"]["enemies"] == ["MOON"]
    assert magnitude["dignity"]["planets"]["MARS"] == {
        "exaltationSign": "CAPRICORN", "debilitationSign": "CANCER", "paramoccaDegrees": 28
    }
    assert magnitude["dignity"]["samaSthanaNotEquivalentTo"] == "SAMA_RELATIONSHIP"
    assert magnitude["nodes"]["RAHU"]["resultsAndNatureLike"] == "SATURN"
    assert magnitude["nodes"]["KETU"]["relationship"]["withOtherPlanets"] == "ENEMY"


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
    assert latta["offsets"]["SUN"] == {"direction": "FORWARD", "offset": 12}
    assert latta["offsets"]["FULL_MOON"] == {"direction": "BACKWARD", "offset": 22}
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
