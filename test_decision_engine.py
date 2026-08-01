from __future__ import annotations

from copy import deepcopy
from unittest.mock import patch

import pandas as pd
import pytest

from decision_engine import (
    CURRENCY_PAIR_EVIDENCE_CONTRACT,
    DECISION_PACKET_CONTRACT,
    ENGINE,
    LIVE_INFERENCE,
    RESEARCH_REPLAY,
    currency_pair_evidence_contract,
    validate_decision_packet,
)


def price_fixture() -> pd.DataFrame:
    index = pd.date_range("2026-07-02T10:00:00Z", periods=3, freq="h")
    return pd.DataFrame(
        {
            "open": [150.0, 150.1, 150.2],
            "high": [150.2, 150.3, 150.4],
            "low": [149.8, 149.9, 150.0],
            "close": [150.1, 150.2, 150.3],
        },
        index=index,
    )


def event_fixture() -> dict:
    return {
        "event_id": "event-live-1",
        "event_family_key": "TN::MERCURY->MARS::trine",
        "event_transit_body": "MERCURY",
        "event_natal_body": "MARS",
        "timestamp": "2026-07-02T09:00:00+00:00",
        "event_end": "2026-07-02T13:00:00+00:00",
        "ticker": "USDJPY",
        "astronomy_contract_version": "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2",
        "case_id": 42,
    }


def touch_fixture() -> dict:
    return {
        "event_id": "event-live-1",
        "event_family_key": "TN::MERCURY->MARS::trine",
        "pair_key": "MARS|MERCURY",
        "aspect": "trine",
        "touch_time_local": "2026-07-02T10:00:00+00:00",
        "touch_kind": "nearest_line",
        "touch_price": 150.05,
        "touch_planets": "JUPITER",
        "tn_hits_json": "[]",
        "base_tn_hits_json": "[]",
        "base_reference_label": "USD",
        "quote_reference_label": "JPY",
        "ret_after_72h_pct": 99.0,
        "ret_after_72h_dir": "UP",
        "close_after72": 999.0,
        "edge_score": 99.0,
    }


SCORES = {
    "fx_hypothesis_direction": "BEARISH",
    "fx_pair_net_score": -0.2,
    "fx_pair_conflict_ratio": 0.0,
    "fx_doctrine_hypothesis_direction": "BEARISH",
    "fx_doctrine_pair_net_score": -0.15,
    "fx_doctrine_pair_conflict_ratio": 0.0,
    "fx_base_scored_hit_count": 1,
    "fx_quote_scored_hit_count": 1,
}


def test_currency_contract_keeps_gross_activation_when_nets_cancel() -> None:
    cancellation_scores = {
        **SCORES,
        "fx_base_reference_available": 1,
        "fx_base_reference_label": "USD reference",
        "fx_quote_reference_label": "JPY reference",
        "fx_doctrine_base_supportive_units": 10.0,
        "fx_doctrine_base_adverse_units": 9.0,
        "fx_doctrine_base_gross_activation_units": 19.0,
        "fx_doctrine_base_net_score": 1.0,
        "fx_doctrine_quote_supportive_units": 8.0,
        "fx_doctrine_quote_adverse_units": 9.0,
        "fx_doctrine_quote_gross_activation_units": 17.0,
        "fx_doctrine_quote_net_score": -1.0,
        "fx_base_candidate_hit_count": 4,
        "fx_quote_candidate_hit_count": 4,
        "fx_base_scored_hit_count": 4,
        "fx_quote_scored_hit_count": 4,
    }
    with patch("decision_engine.score_currency_pair_for_row", return_value=cancellation_scores):
        result = currency_pair_evidence_contract(
            touch_fixture(),
            base_currency="USD",
            quote_currency="JPY",
            evidence_cutoff="2026-07-02T09:00:00+00:00",
        )

    assert result["contract"] == CURRENCY_PAIR_EVIDENCE_CONTRACT
    assert result["status"] == "provisional_research_only"
    assert result["base"]["grossActivationUnits"] == 19.0
    assert result["quote"]["grossActivationUnits"] == 17.0
    assert result["pair"]["commonActivationUnits"] == 18.0
    assert result["pair"]["netDifferenceUnits"] == 2.0
    assert result["pair"]["jointNetStrengthUnits"] == 1.0
    assert result["pair"]["state"] == "KNOWN"


def test_currency_contract_blocks_missing_base_mapping() -> None:
    with patch("decision_engine.score_currency_pair_for_row", return_value={**SCORES, "fx_base_reference_available": 0}):
        result = currency_pair_evidence_contract(
            touch_fixture(),
            base_currency="USD",
            quote_currency="JPY",
            evidence_cutoff="2026-07-02T09:00:00+00:00",
        )

    assert result["status"] == "blocked_mapping"
    assert result["base"]["state"] == "BLOCKED_MAPPING"
    assert result["pair"]["state"] == "UNKNOWN"
    assert result["pair"]["netDifferenceUnits"] is None


def test_live_packet_excludes_future_labels_and_unclosed_bars() -> None:
    first_touch = touch_fixture()
    second_touch = {**first_touch, "ret_after_72h_pct": -88.0, "ret_after_72h_dir": "DOWN"}
    with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
        first = ENGINE.live_inference_packet(
            event=event_fixture(),
            touch=first_touch,
            price=price_fixture(),
            decision_time="2026-07-02T12:30:00+00:00",
            timeframe="H1",
            artifact={"artifactId": "fixture", "symbol": "USDJPY", "parameters": {}},
        )
        second = ENGINE.live_inference_packet(
            event=event_fixture(),
            touch=second_touch,
            price=price_fixture(),
            decision_time="2026-07-02T12:30:00+00:00",
            timeframe="H1",
            artifact={"artifactId": "fixture", "symbol": "USDJPY", "parameters": {}},
        )

    assert first["contract"] == DECISION_PACKET_CONTRACT
    assert first["mode"] == LIVE_INFERENCE
    assert first["status"] == "watch"
    assert first["decision"]["action"] == "WATCH_SHORT"
    assert first["outcome"] is None
    assert first["entry"]["price"] is None
    assert first["exit"]["price"] is None
    assert first["guardrails"]["timestampSafe"] is True
    assert first["guardrails"]["executionAllowed"] is False
    assert first["policyLocks"]["historicalValidationStatus"] == (
        "failed_retrospective_statistical_gate_20260713"
    )
    assert first["policyLocks"]["prospectiveValidationRequired"] is True
    assert first["priceAudit"]["closedBarCount"] == 2
    assert first["priceAudit"]["futureOrUnclosedBarsExcluded"] == 1
    assert first["times"]["sourceDataMaxTime"] == "2026-07-02T12:00:00+00:00"
    assert "ret_after_72h_pct" in first["featureAudit"]["forbiddenFieldsPresentButExcluded"]
    assert "ret_after_72h_pct" not in first["featureAudit"]["consumedFields"]
    assert second["packetId"] == first["packetId"]


def test_live_packet_abstains_before_touch_bar_is_closed() -> None:
    with patch("decision_engine.score_currency_pair_for_row") as scorer:
        packet = ENGINE.live_inference_packet(
            event=event_fixture(),
            touch=touch_fixture(),
            price=price_fixture(),
            decision_time="2026-07-02T10:30:00+00:00",
            timeframe="H1",
        )
    scorer.assert_not_called()
    assert packet["status"] == "abstain"
    assert packet["decision"]["action"] == "ABSTAIN"
    assert "touch_bar_not_closed_by_decision_time" in packet["decision"]["reason"]
    assert packet["guardrails"]["noLookahead"] is True


def test_final_event_bar_can_be_evaluated_only_after_it_closes() -> None:
    event = event_fixture()
    event["event_end"] = "2026-07-02T10:30:00+00:00"
    with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
        packet = ENGINE.live_inference_packet(
            event=event,
            touch=touch_fixture(),
            price=price_fixture(),
            decision_time="2026-07-02T11:00:00+00:00",
            timeframe="H1",
        )
    assert packet["status"] == "watch"
    assert packet["times"]["signalTime"] == "2026-07-02T11:00:00+00:00"
    assert packet["times"]["decisionDeadline"] == "2026-07-02T11:30:00+00:00"


def test_touch_outside_event_window_is_rejected() -> None:
    event = event_fixture()
    touch = touch_fixture()
    touch["touch_time_local"] = "2026-07-02T14:00:00+00:00"
    with patch("decision_engine.score_currency_pair_for_row") as scorer:
        packet = ENGINE.live_inference_packet(
            event=event,
            touch=touch,
            price=price_fixture(),
            decision_time="2026-07-02T14:00:00+00:00",
            timeframe="H1",
        )
    scorer.assert_not_called()
    assert packet["status"] == "abstain"
    assert "touch_time_outside_event_window" in packet["decision"]["reason"]


def test_research_packet_declares_hindsight_and_cannot_be_live() -> None:
    packet = ENGINE.research_replay_packet(
        replay={
            "outcome_label": "bearish",
            "trade_start": {"x": "2026-07-02T10:00:00+00:00", "y": 150.2},
            "trade_end": {"x": "2026-07-02T11:00:00+00:00", "y": 149.9},
            "signed_pips": 30.0,
            "raw_pips": -30.0,
            "start_rule": "observed_start",
            "end_rule": "observed_end",
        },
        case={
            "case_id": 7,
            "source_event_id": "event-research-7",
            "family_key": "TN::MERCURY->MARS::trine",
            "window_start_ist": "2026-07-02T09:00:00+00:00",
            "window_end_ist": "2026-07-02T12:00:00+00:00",
        },
        source_data_max_time="2026-07-02T15:00:00+00:00",
    )

    assert packet["mode"] == RESEARCH_REPLAY
    assert packet["guardrails"]["timestampSafe"] is False
    assert packet["guardrails"]["liveEligible"] is False
    assert packet["guardrails"]["outcomeLabelConsumed"] is True
    assert "known_full_window_outcome_used" in packet["guardrails"]["violations"]


def test_live_validator_rejects_an_injected_outcome() -> None:
    with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
        packet = ENGINE.live_inference_packet(
            event=event_fixture(),
            touch=touch_fixture(),
            price=price_fixture(),
            decision_time="2026-07-02T12:30:00+00:00",
            timeframe="H1",
        )
    tampered = deepcopy(packet)
    tampered["outcome"] = {"label": "WIN"}
    with pytest.raises(ValueError, match="cannot contain an observed outcome"):
        validate_decision_packet(tampered)
