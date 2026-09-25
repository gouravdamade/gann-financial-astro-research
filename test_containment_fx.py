from __future__ import annotations

import json
from unittest.mock import patch

import pandas as pd

from build_trade_candidates_from_touches import evidence_state_for_side, score_currency_pair_for_row
from decision_engine import ENGINE
from test_decision_engine import SCORES, event_fixture, price_fixture, touch_fixture


def hit(*, strength: float = 1.0, natal_house: int | None = 1) -> dict[str, object]:
    value: dict[str, object] = {
        "transit_planet": "SUN",
        "natal_planet": "MARS",
        "aspect": "trine",
        "bphs_strength": strength,
    }
    if natal_house is not None:
        value["natal_house"] = natal_house
    return value


def scoring_row(base: object, quote: object) -> pd.Series:
    return pd.Series(
        {
            "pair_key": "SUN|MARS",
            "aspect": "trine",
            "base_tn_hits_json": base,
            "tn_hits_json": quote,
            "base_reference_label": "USD",
            "quote_reference_label": "JPY",
        }
    )


def packet_scores(base_state: str, quote_state: str) -> dict[str, object]:
    return {
        **SCORES,
        "fx_base_reference_available": 0 if base_state == "BLOCKED_MAPPING" else 1,
        "fx_quote_reference_available": 0 if quote_state == "BLOCKED_MAPPING" else 1,
        "fx_base_evidence_state": base_state,
        "fx_quote_evidence_state": quote_state,
        "fx_base_evidence_reason": "test",
        "fx_quote_evidence_reason": "test",
        "fx_pair_direction_eligible": base_state in {"KNOWN", "MIXED"} and quote_state in {"KNOWN", "MIXED"},
        "fx_pair_direction_reason": "test",
    }


def test_valid_zero_evidence_is_known_and_not_absent() -> None:
    result = score_currency_pair_for_row(
        scoring_row(json.dumps([hit(strength=0.0)]), json.dumps([hit(strength=0.0)]))
    )
    assert result["fx_base_evidence_state"] == "KNOWN"
    assert result["fx_quote_evidence_state"] == "KNOWN"
    assert result["fx_pair_direction_eligible"] is True
    assert result["fx_base_scored_hit_count"] == 0
    assert result["fx_pair_net_score"] == 0.0


def test_malformed_and_valid_empty_payloads_are_distinct() -> None:
    valid_quote = json.dumps([hit()])
    malformed = score_currency_pair_for_row(scoring_row("{not-json", valid_quote))
    empty = score_currency_pair_for_row(scoring_row("[]", valid_quote))
    assert malformed["fx_base_evidence_state"] == "PARTIAL"
    assert malformed["fx_base_evidence_reason"] == "payload_invalid_json"
    assert empty["fx_base_evidence_state"] == "UNKNOWN"
    assert empty["fx_base_evidence_reason"] == "valid_empty_evidence"
    assert malformed["fx_pair_direction_eligible"] is False
    assert empty["fx_pair_direction_eligible"] is False


def test_missing_required_factual_field_is_partial() -> None:
    result = score_currency_pair_for_row(scoring_row(json.dumps([hit(natal_house=None)]), json.dumps([hit()])))
    assert result["fx_base_evidence_state"] == "PARTIAL"
    assert "unresolved_evidence_fields" in result["fx_base_evidence_reason"]
    assert result["fx_pair_direction_eligible"] is False


def test_resolved_conflict_is_mixed_and_mixed_plus_known_is_eligible() -> None:
    state, reason = evidence_state_for_side(
        json.dumps([hit()]),
        event_aspect="trine",
        event_bodies={"SUN", "MARS"},
        score={
            "jyotish_hypothesis_direction": "CONFLICT",
            "doctrine_hypothesis_direction": "CONFLICT",
            "jyotish_conflict_score": 1.0,
            "doctrine_conflict_score": 1.0,
        },
    )
    assert state == "MIXED"
    assert reason == "resolved_conflicting_evidence"

    with patch("decision_engine.score_currency_pair_for_row", return_value=packet_scores("MIXED", "KNOWN")):
        packet = ENGINE.live_inference_packet(
            event=event_fixture(),
            touch=touch_fixture(),
            price=price_fixture(),
            decision_time="2026-07-02T12:30:00+00:00",
            timeframe="H1",
        )
    assert packet["status"] == "watch"
    assert packet["guardrails"]["executionAllowed"] is False


def test_incomplete_side_combinations_abstain_before_directional_result() -> None:
    for base_state, quote_state in (
        ("KNOWN", "UNKNOWN"),
        ("UNKNOWN", "KNOWN"),
        ("PARTIAL", "KNOWN"),
        ("KNOWN", "BLOCKED_MAPPING"),
    ):
        with patch(
            "decision_engine.score_currency_pair_for_row",
            return_value=packet_scores(base_state, quote_state),
        ):
            packet = ENGINE.live_inference_packet(
                event=event_fixture(),
                touch=touch_fixture(),
                price=price_fixture(),
                decision_time="2026-07-02T12:30:00+00:00",
                timeframe="H1",
            )
        assert packet["status"] == "abstain"
        assert packet["decision"]["action"] == "ABSTAIN"
        assert "pair_evidence_incomplete" in packet["decision"]["reason"]
        assert packet["guardrails"]["executionAllowed"] is False
