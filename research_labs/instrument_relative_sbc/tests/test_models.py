from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from instrument_relative_sbc import (
    AksharaMapping,
    InfluenceContribution,
    RuleRecord,
    SourceCitation,
)


NOW = datetime(2026, 7, 18, tzinfo=timezone.utc)
CLASSICAL = SourceCitation(
    source_id="SOURCE",
    title="Classical source",
    source_tier="classical_text",
    locator="chapter 1, verse 1",
)


def test_verified_rule_requires_locator_and_reviewer() -> None:
    no_locator = SourceCitation(
        source_id="SOURCE",
        title="Classical source",
        source_tier="classical_text",
    )
    with pytest.raises(ValueError, match="source locators"):
        RuleRecord(
            rule_id="RULE",
            rule_family="sbc_vedha",
            profile_id="classical",
            status="verified",
            source_citations=(no_locator,),
            normalized_condition={},
            normalized_effect={},
            confidence=1.0,
            reviewer="human",
            verified_at=NOW,
        )


def test_llm_akshara_requires_named_human_reviewer() -> None:
    with pytest.raises(ValueError, match="human reviewer"):
        AksharaMapping(
            raw_name="USD",
            spoken_form="you ess dee",
            candidate_akshara="U",
            mapping_method="llm_suggestion",
            language="English",
            confidence=0.5,
            review_status="accepted",
            valid_from=date(2026, 1, 1),
        )

    reviewed = AksharaMapping(
        raw_name="USD",
        spoken_form="you ess dee",
        candidate_akshara="U",
        mapping_method="llm_suggestion",
        language="English",
        confidence=0.5,
        review_status="accepted",
        valid_from=date(2026, 1, 1),
        reviewer="human-reviewer",
    )
    assert reviewed.review_status == "accepted"


def test_unknown_contribution_cannot_silently_become_zero() -> None:
    with pytest.raises(ValueError, match="silently become a number"):
        InfluenceContribution(
            contribution_id="C1",
            instrument_id="currency:USD",
            timestamp_utc=NOW,
            event_id="E1",
            target_type="akshara",
            target_value="U",
            rule_id="R1",
            rule_profile_id="experimental",
            semantic_effect="unknown",
            raw_polarity="unknown",
            intensity=1.0,
            relevance=1.0,
            mapping_confidence=1.0,
            source_confidence=1.0,
            signed_value=0.0,
            explanation="unknown is missing, not neutral",
            provenance=(CLASSICAL,),
        )


def test_signed_contribution_must_equal_declared_factors() -> None:
    contribution = InfluenceContribution(
        contribution_id="C1",
        instrument_id="currency:USD",
        timestamp_utc=NOW,
        event_id="E1",
        target_type="akshara",
        target_value="U",
        rule_id="R1",
        rule_profile_id="experimental",
        semantic_effect="supportive_for_target",
        raw_polarity=1,
        intensity=0.8,
        relevance=0.5,
        mapping_confidence=0.5,
        source_confidence=0.5,
        signed_value=0.1,
        explanation="factor product",
        provenance=(CLASSICAL,),
    )
    assert contribution.signed_value == 0.1
