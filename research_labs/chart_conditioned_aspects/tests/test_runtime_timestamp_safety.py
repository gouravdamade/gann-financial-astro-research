from __future__ import annotations

from datetime import timedelta

import pytest

from chart_conditioned_aspects import DynamicContribution
from chart_conditioned_aspects.evaluation import (
    compile_structural_prior,
    evaluate_runtime_event,
)
from chart_conditioned_aspects.transits import adapt_explicit_tn_event

from conftest import NOW, make_structure


def build_case(profiles):
    structure = make_structure(profiles)
    prior = compile_structural_prior(
        structure,
        transit_body="SATURN",
        natal_target="MOON",
        aspect_type="square",
        profiles=profiles,
    )
    event = adapt_explicit_tn_event(
        {
            "event_id": "TN-RUNTIME-1",
            "event_contract": "EXPLICIT_TN_EVENT_V1",
            "event_scope": "TN",
            "event_transit_body": "SATURN",
            "event_natal_body": "MOON",
            "event_role_resolution_status": "explicit",
            "chart_id": structure.chart.chart_id,
            "aspect_type": "square",
            "observed_separation_deg": 90.2,
            "event_timestamp_utc": NOW.isoformat(),
            "evidence_available_at_utc": NOW.isoformat(),
        },
        profiles,
    )
    return structure, prior, event


def contribution(*, available_at, direction="ADVERSE") -> DynamicContribution:
    return DynamicContribution(
        contribution_id=f"DYN-{available_at.isoformat()}",
        available_at_utc=available_at,
        category="TEST_DYNAMIC_EVIDENCE",
        directional_effect=direction,
        activation_effect="MODERATE",
        volatility_effect="ELEVATED",
        reason="Test-only evidence available at the declared timestamp.",
        evidence_refs=("TEST",),
        confidence=0.5,
    )


def test_runtime_rejects_future_evidence(profiles) -> None:
    structure, prior, event = build_case(profiles)
    with pytest.raises(ValueError, match="future dynamic evidence"):
        evaluate_runtime_event(
            event,
            prior,
            structure.graph,
            profiles,
            as_of_utc=NOW,
            dynamic_contributions=(
                contribution(available_at=NOW + timedelta(minutes=1)),
            ),
        )


def test_runtime_preserves_direction_conflict(profiles) -> None:
    structure, prior, event = build_case(profiles)
    result = evaluate_runtime_event(
        event,
        prior,
        structure.graph,
        profiles,
        as_of_utc=NOW,
        dynamic_contributions=(contribution(available_at=NOW),),
    )
    assert prior.directional_prior == "SUPPORTIVE"
    assert result.directional_result == "MIXED"
    assert "DIRECTIONAL_EVIDENCE_CONFLICT_PRESERVED" in result.conflict_flags
    assert result.timestamp_safe is True
    assert result.execution_allowed is False


def test_runtime_cannot_precede_event(profiles) -> None:
    structure, prior, event = build_case(profiles)
    with pytest.raises(ValueError, match="precede the event"):
        evaluate_runtime_event(
            event,
            prior,
            structure.graph,
            profiles,
            as_of_utc=NOW - timedelta(seconds=1),
        )
