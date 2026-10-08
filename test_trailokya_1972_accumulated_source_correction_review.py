"""Deterministic source-contract tests for the accumulated Trailokya correction gate.

These tests inspect static evidence/source contracts only. They must not import
runtime guidance, market, scoring, Fields, provider/outcome, MT5, or execution paths.
"""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
TRAILOKYA = ROOT / "configs" / "sbc" / "trailokya"


def _load(name: str) -> dict:
    data = yaml.safe_load((TRAILOKYA / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_v343_is_scoped_later_moon_fruition_not_a_generic_duration_kernel() -> None:
    rule = _load("trailokya_1972_vedha_result_ripening_v1.yaml")
    assert rule["status"] == "SOURCE_CLOSED_SCOPED_ONLY"
    v343 = rule["rule"]
    assert v343["id"] == "TD1972_V343_LATER_MOON_VEDHA_FRUITION"
    assert v343["classification"] == "SOURCE_EXPLICIT_POST_TRIGGER_PERSISTENCE"
    assert v343["initialTrigger"]["targetDomain"] == ["TITHI", "NAKSHATRA", "VOWEL", "RASHI", "AKSHARA"]
    assert v343["fruitionTrigger"]["event"] == "LATER_MOON_VEDHA"
    assert v343["fruitionTrigger"]["identityConstraint"] == "SAME_FIVEFOLD_SBC_IDENTITY_AS_PRIOR_VEDHA"
    assert v343["fruitionTrigger"]["fruitionTime"] == "THAT_MOON_VEDHA_DAY"
    assert v343["maximumLatentInterval"] == "NOT_STATED"
    assert v343["continuousEfficacyWhileWaiting"] == "NOT_STATED"
    assert v343["postFruitionDuration"] == "NOT_STATED"
    assert v343["fixedDuration"] == "NOT_AUTHORIZED"
    assert v343["applyingExactSeparatingKernel"] == "NOT_AUTHORIZED"
    assert rule["runtimeBehaviorChanged"] is False
    assert rule["executionAllowed"] is False


def test_commodity_duration_owner_is_scoped_and_mrigashirsha_root_is_preserved() -> None:
    ledger = _load("trailokya_1972_nakshatra_commodity_ledger_v1.yaml")
    semantics = ledger["durationSemantics"]
    assert semantics["decision"] == "SOURCE_CORRECTION_ACCEPTED_WITH_PROVENANCE_NOTE"
    assert semantics["durationOwner"] == "DIRECTIONAL_COMMODITY_RESULT_AFTER_NAMED_NAKSHATRA_VEDHA"
    assert semantics["genericEventDuration"] == "NOT_AUTHORIZED"
    assert semantics["astronomicalResidenceDurationEquivalent"] is False
    assert semantics["mriga"] == {
        "rootLiteral": "60_DAYS",
        "hindiCommentaryGloss": "2_MONTHS",
        "normalizationPolicy": "PRESERVE_ROOT_LITERAL_DO_NOT_NORMALIZE_TO_MONTHS",
    }
    mriga = next(item for item in ledger["entries"] if item["verse"] == 381)
    assert mriga["nakshatra"] == "MRIGASHIRSHA"
    assert mriga["duration"] == "60_DAYS"
    assert ledger["runtimeBehaviorChanged"] is False
    assert ledger["executionAllowed"] is False


def test_central_review_preserves_temporal_non_inheritance_and_all_locks() -> None:
    review = _load("trailokya_1972_accumulated_source_correction_review_v1.yaml")
    assert review["gate"] == "TRAILOKYA_1972_ACCUMULATED_SOURCE_CORRECTION_REVIEW"
    assert review["items"]["A_ATICARA_JUPITER_LITERAL"]["decision"] == "SOURCE_CORRECTION_ACCEPTED"
    assert review["items"]["B_LATTA_COUNTING_ORIGIN"]["decision"] == "SOURCE_CORRECTION_ACCEPTED_WITH_PROVENANCE_NOTE"
    assert review["items"]["C_LATTA_APPLICABILITY"]["decision"] == "SOURCE_CORRECTION_ACCEPTED"
    assert review["items"]["D_VEDHA_RESULT_RIPENING_V343"]["decision"] == "SOURCE_CORRECTION_ACCEPTED"
    assert review["items"]["E_COMMODITY_DURATIONS"]["decision"] == "SOURCE_CORRECTION_ACCEPTED_WITH_PROVENANCE_NOTE"
    assert review["items"]["F_TEMPORAL_NON_INHERITANCE"]["decision"] == "SOURCE_CORRECTION_ACCEPTED_WITH_PROVENANCE_NOTE"

    preserve = review["items"]["F_TEMPORAL_NON_INHERITANCE"]["preserve"]
    assert preserve == {
        "GEOMETRIC_EVENT_INTERVAL_V1": "ENGINEERING_MAPPING",
        "APPLICATION_EXACT_SEPARATION_EFFICACY_V1": "SOURCE_SILENT_GENERICALLY",
        "TRAILOKYA_PERSISTENCE_DURATION": "FAMILY_SPECIFIC_ONLY",
        "DURATION_TO_TEMPORAL_SCALE_HYPOTHESIS_V1": "NOT_SOURCE_AUTHORIZED_GENERIC",
    }
    assert set(review["items"]["F_TEMPORAL_NON_INHERITANCE"]["prohibitedDerivations"]) == {
        "DECAY",
        "HALF_LIFE",
        "SMOOTHING",
        "WAVE_PERIOD",
        "TEMPORAL_NORMALIZATION",
        "REPEATED_HIT_AMPLIFICATION",
        "NESTED_WAVE_INHERITANCE",
    }
    assert all(value is False for value in review["scopeLocks"].values())
    assert review["nextGate"] == {
        "id": "ARGHYA_FULL_WORKED_CALCULATION_RECONSTRUCTION",
        "status": "NOT_STARTED_BY_THIS_REVIEW",
    }
