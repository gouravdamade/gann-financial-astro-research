from __future__ import annotations

import json
from unittest.mock import patch

import pandas as pd
import pytest

from build_trade_candidates_from_touches import evidence_state_for_side, score_currency_pair_for_row
from decision_engine import ENGINE
from test_decision_engine import SCORES, event_fixture, price_fixture, touch_fixture


def hit(
    *,
    strength: float = 1.0,
    natal_house: int | None = 1,
    natal_sign: str | None = "ARIES",
    transit_sign: str | None = "LEO",
) -> dict[str, object]:
    value: dict[str, object] = {
        "transit_planet": "SUN",
        "natal_planet": "MARS",
        "aspect": "trine",
        "bphs_strength": strength,
    }
    if natal_house is not None:
        value["natal_house"] = natal_house
    if natal_sign is not None:
        value["natal_sign"] = natal_sign
    if transit_sign is not None:
        value["transit_sign"] = transit_sign
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


def live_touch(base: object, quote: object) -> dict[str, object]:
    return {
        "event_id": "event-live-1",
        "event_family_key": "TN::MERCURY->MARS::trine",
        "pair_key": "SUN|MARS",
        "aspect": "trine",
        "touch_time_local": "2026-07-02T10:00:00+00:00",
        "touch_kind": "nearest_line",
        "touch_price": 150.05,
        "touch_planets": "SUN",
        "base_tn_hits_json": base,
        "tn_hits_json": quote,
        "base_reference_label": "USD",
        "quote_reference_label": "JPY",
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


def test_missing_natal_sign_is_partial_and_ineligible() -> None:
    result = score_currency_pair_for_row(
        scoring_row(
            json.dumps([hit(natal_sign=None)]),
            json.dumps([hit()]),
        )
    )
    assert result["fx_base_evidence_state"] == "PARTIAL"
    assert result["fx_pair_direction_eligible"] is False
    assert "unresolved_evidence_fields" in result["fx_base_evidence_reason"]


def test_missing_transit_sign_is_partial_and_ineligible() -> None:
    result = score_currency_pair_for_row(
        scoring_row(
            json.dumps([hit(transit_sign=None)]),
            json.dumps([hit()]),
        )
    )
    assert result["fx_base_evidence_state"] == "PARTIAL"
    assert result["fx_pair_direction_eligible"] is False
    assert "unresolved_evidence_fields" in result["fx_base_evidence_reason"]


def test_usd_complete_jpy_missing_natal_sign_abstains() -> None:
    touch = live_touch(
        json.dumps([hit()]),
        json.dumps([hit(natal_sign=None)]),
    )
    scores = score_currency_pair_for_row(pd.Series(touch))
    assert scores["fx_base_evidence_state"] == "KNOWN"
    assert scores["fx_quote_evidence_state"] == "PARTIAL"
    assert scores["fx_pair_direction_eligible"] is False
    with patch("decision_engine.score_currency_pair_for_row", return_value=scores):
        packet = ENGINE.live_inference_packet(
            event=event_fixture(),
            touch=touch,
            price=price_fixture(),
            decision_time="2026-07-02T12:30:00+00:00",
            timeframe="H1",
        )
    assert packet["status"] == "abstain"
    assert packet["decision"]["action"] == "ABSTAIN"


def test_jpy_complete_usd_missing_transit_sign_abstains() -> None:
    touch = live_touch(
        json.dumps([hit(transit_sign=None)]),
        json.dumps([hit()]),
    )
    scores = score_currency_pair_for_row(pd.Series(touch))
    assert scores["fx_base_evidence_state"] == "PARTIAL"
    assert scores["fx_quote_evidence_state"] == "KNOWN"
    assert scores["fx_pair_direction_eligible"] is False
    with patch("decision_engine.score_currency_pair_for_row", return_value=scores):
        packet = ENGINE.live_inference_packet(
            event=event_fixture(),
            touch=touch,
            price=price_fixture(),
            decision_time="2026-07-02T12:30:00+00:00",
            timeframe="H1",
        )
    assert packet["status"] == "abstain"
    assert packet["decision"]["action"] == "ABSTAIN"


def test_fully_resolved_scoring_fixture_preserves_exact_scores_and_direction() -> None:
    base = hit(strength=2.0, natal_house=2, natal_sign="ARIES", transit_sign="LEO")
    quote = hit(strength=1.0, natal_house=8, natal_sign="SCORPIO", transit_sign="PISCES")
    result = score_currency_pair_for_row(scoring_row(json.dumps([base]), json.dumps([quote])))

    assert result["fx_base_net_score"] == pytest.approx(1.65)
    assert result["fx_quote_net_score"] == pytest.approx(-1.075)
    assert result["fx_pair_net_score"] == pytest.approx(2.725)
    assert result["fx_hypothesis_direction"] == "BULLISH"
    assert result["fx_doctrine_base_net_score"] == pytest.approx(2.0625)
    assert result["fx_doctrine_quote_net_score"] == pytest.approx(-0.940625)
    assert result["fx_doctrine_pair_net_score"] == pytest.approx(3.003125)
    assert result["fx_doctrine_hypothesis_direction"] == "BULLISH"
    assert result["fx_pair_direction_eligible"] is True


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
