from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from build_trade_candidates_from_touches import score_currency_pair_for_row


DECISION_PACKET_CONTRACT = "GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1"
ENGINE_VERSION = "timestamp_safe_auto_suggest_v1_1_20260713"
POLICY_VERSION = "fx_doctrine_consensus_watch_only_v1"
VALIDATION_CONTRACT = "GANN_TIMESTAMP_SAFE_WALK_FORWARD_EVALUATION_V1"
VALIDATION_STATUS = "failed_retrospective_statistical_gate_20260713"
VALIDATION_REPORT = "timestamp_safe_decision_walk_forward_20260713.md"
RESEARCH_REPLAY = "research_replay"
LIVE_INFERENCE = "live_inference"

TIMEFRAME_MINUTES = {
    "M30": 30,
    "H1": 60,
    "H4": 240,
    "D1": 1440,
}

LIVE_SCORER_FIELDS = (
    "aspect",
    "pair_key",
    "tn_hits_json",
    "base_tn_hits_json",
    "base_reference_label",
    "quote_reference_label",
)
LIVE_CONTEXT_FIELDS = (
    "event_id",
    "event_scope",
    "event_family_key",
    "event_transit_body",
    "event_natal_body",
    "event_window_start_local",
    "event_window_end_local",
    "event_best_time_local",
    "event_duration_minutes",
    "event_orb_deg",
    "event_orb_limit_deg",
    "event_bphs_like_orb_strength",
    "aspect_regime_active_count",
    "aspect_regime_signature",
    "touch_time_local",
    "touch_kind",
    "touch_price",
    "touch_distance_abs",
    "touch_distance_pct",
    "touch_zone",
    "touch_identity_count",
    "touch_planets",
    "touch_has_moon",
    "touch_line_price_1",
    "touch_line_price_2",
    "touch_planet_1",
    "touch_planet_2",
    "event_strict_shadbala_implemented_total_virupa_avg",
    "event_strict_shadbala_implemented_total_ratio_avg",
    "event_strict_drik_bala_virupa_avg",
    "event_strict_drik_benefic_virupa_avg",
    "event_strict_drik_malefic_virupa_avg",
    "event_strict_chesta_bala_virupa_avg",
    "event_strict_shadbala_status",
    "event_strict_drik_status",
)
LIVE_FEATURE_ALLOWLIST = frozenset((*LIVE_SCORER_FIELDS, *LIVE_CONTEXT_FIELDS))

FORBIDDEN_EXACT_FIELDS = frozenset(
    {
        "default_outcome",
        "edge_score",
        "full_window_direction",
        "ml_outcome",
        "outcome_label",
        "signed_pips",
        "signed_return_pct",
    }
)
FORBIDDEN_PREFIXES = (
    "after72",
    "close_after",
    "full_window_",
    "group_ml_",
    "mfe_",
    "mae_",
    "probable_factor_",
    "ret_after_",
    "rule_lessons",
    "special_trait_",
)


def _mapping(value: Mapping[str, Any] | pd.Series | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, pd.Series):
        return value.to_dict()
    return dict(value)


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _json_safe(value),
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest().upper()


def _timestamp(value: Any, label: str) -> pd.Timestamp:
    if isinstance(value, (int, np.integer)):
        unit = "ms" if abs(int(value)) > 10_000_000_000 else "s"
        parsed = pd.Timestamp(value, unit=unit, tz="UTC")
    else:
        try:
            parsed = pd.Timestamp(value)
        except Exception as exc:
            raise ValueError(f"{label} is not a valid timestamp") from exc
    if pd.isna(parsed):
        raise ValueError(f"{label} is not a valid timestamp")
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.tz_convert("UTC")


def _optional_timestamp(value: Any) -> pd.Timestamp | None:
    if value in (None, ""):
        return None
    try:
        return _timestamp(value, "timestamp")
    except ValueError:
        return None


def _iso(value: pd.Timestamp | None) -> str | None:
    return value.isoformat() if value is not None else None


def _timeframe_delta(timeframe: str) -> pd.Timedelta:
    normalized = str(timeframe or "").strip().upper()
    if normalized not in TIMEFRAME_MINUTES:
        raise ValueError(f"unsupported decision timeframe: {timeframe}")
    return pd.Timedelta(minutes=TIMEFRAME_MINUTES[normalized])


def is_forbidden_live_field(name: str) -> bool:
    normalized = str(name or "").strip().lower()
    return normalized in FORBIDDEN_EXACT_FIELDS or normalized.startswith(FORBIDDEN_PREFIXES)


def sanitize_live_features(
    touch: Mapping[str, Any] | pd.Series | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = _mapping(touch)
    safe = {
        key: _json_safe(raw.get(key))
        for key in LIVE_FEATURE_ALLOWLIST
        if key in raw and not is_forbidden_live_field(key)
    }
    forbidden_present = sorted(key for key in raw if is_forbidden_live_field(key))
    consumed = sorted(key for key in LIVE_SCORER_FIELDS if key in safe)
    return safe, {
        "allowlistVersion": "live_touch_feature_allowlist_v1",
        "consumedFields": consumed,
        "contextFields": sorted(key for key in LIVE_CONTEXT_FIELDS if key in safe),
        "forbiddenFieldsPresentButExcluded": forbidden_present,
        "rawFieldCount": len(raw),
        "allowlistedFieldCount": len(safe),
        "inputFingerprint": _fingerprint(safe),
    }


def closed_price_summary(
    price: pd.DataFrame,
    decision_time: pd.Timestamp,
    timeframe: str,
) -> dict[str, Any]:
    if not isinstance(price, pd.DataFrame) or not isinstance(price.index, pd.DatetimeIndex):
        raise ValueError("price evidence must have a DatetimeIndex")
    if price.index.tz is None:
        raise ValueError("price evidence timestamps must include a UTC offset")
    normalized = price.copy().sort_index()
    normalized.index = normalized.index.tz_convert("UTC")
    if normalized.index.has_duplicates:
        raise ValueError("price evidence timestamps must be unique")
    delta = _timeframe_delta(timeframe)
    closed_mask = normalized.index + delta <= decision_time
    closed = normalized.loc[closed_mask]
    source_max = closed.index.max() + delta if not closed.empty else None
    return {
        "closedBarCount": int(len(closed)),
        "futureOrUnclosedBarsExcluded": int(len(normalized) - len(closed)),
        "sourceDataMaxTime": _iso(source_max),
        "firstClosedBarOpenTime": _iso(closed.index.min()) if not closed.empty else None,
        "lastClosedBarOpenTime": _iso(closed.index.max()) if not closed.empty else None,
    }


def _point_time(point: Mapping[str, Any] | None) -> pd.Timestamp | None:
    if not point:
        return None
    return _optional_timestamp(point.get("x"))


def _point_price(point: Mapping[str, Any] | None) -> float | None:
    if not point:
        return None
    try:
        value = float(point.get("y"))
    except (TypeError, ValueError):
        return None
    return value if np.isfinite(value) else None


def _action(direction: str) -> tuple[str, str]:
    normalized = str(direction or "").strip().upper()
    if normalized in {"BULLISH", "UP", "LONG"}:
        return "WATCH_LONG", "bullish"
    if normalized in {"BEARISH", "DOWN", "SHORT"}:
        return "WATCH_SHORT", "bearish"
    return "ABSTAIN", "abstain"


def validate_decision_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    checked = dict(packet)
    if checked.get("contract") != DECISION_PACKET_CONTRACT:
        raise ValueError("unsupported decision packet contract")
    if checked.get("engineVersion") != ENGINE_VERSION:
        raise ValueError("unsupported decision engine version")
    mode = str(checked.get("mode") or "")
    if mode not in {RESEARCH_REPLAY, LIVE_INFERENCE}:
        raise ValueError("decision mode must be research_replay or live_inference")
    times = checked.get("times") or {}
    event_start = _timestamp(times.get("eventWindowStart"), "eventWindowStart")
    event_end = _timestamp(times.get("eventWindowEnd"), "eventWindowEnd")
    decision_time = _timestamp(times.get("decisionTime"), "decisionTime")
    signal_time = _optional_timestamp(times.get("signalTime"))
    decision_deadline = _optional_timestamp(times.get("decisionDeadline"))
    source_max = _optional_timestamp(times.get("sourceDataMaxTime"))
    guardrails = checked.get("guardrails") or {}
    feature_audit = checked.get("featureAudit") or {}
    consumed = {str(item) for item in feature_audit.get("consumedFields") or []}

    if guardrails.get("executionAllowed") is not False:
        raise ValueError("decision packets cannot enable execution")
    if mode == LIVE_INFERENCE:
        if guardrails.get("timestampSafe") is not True or guardrails.get("noLookahead") is not True:
            raise ValueError("live inference packet is not timestamp safe")
        if guardrails.get("outcomeLabelConsumed") is not False:
            raise ValueError("live inference consumed an outcome label")
        if guardrails.get("futurePricesConsumed") is not False:
            raise ValueError("live inference consumed future prices")
        if times.get("labelAvailableTime") is not None:
            raise ValueError("live inference packet cannot expose a label time")
        if decision_deadline is None or decision_deadline < event_end:
            raise ValueError("live inference packet has an invalid decision deadline")
        if guardrails.get("liveEligible") is True:
            if decision_time < event_start or decision_time > decision_deadline:
                raise ValueError("live inference watch lies outside its decision window")
            if signal_time is None or signal_time > decision_time:
                raise ValueError("live inference watch used an unavailable signal")
        if source_max is not None and source_max > decision_time:
            raise ValueError("live inference price evidence exceeds decision time")
        if times.get("fillTime") is not None or times.get("exitTime") is not None:
            raise ValueError("live inference cannot contain materialized trade times")
        if _mapping(checked.get("entry")).get("price") is not None:
            raise ValueError("live inference cannot contain a fill price")
        if _mapping(checked.get("exit")).get("price") is not None:
            raise ValueError("live inference cannot contain an exit price")
        forbidden_consumed = sorted(name for name in consumed if is_forbidden_live_field(name))
        if forbidden_consumed:
            raise ValueError(f"live inference consumed forbidden fields: {forbidden_consumed}")
        if checked.get("outcome") is not None:
            raise ValueError("live inference packet cannot contain an observed outcome")
    elif guardrails.get("liveEligible") is not False:
        raise ValueError("research replay packet cannot be live eligible")
    return checked


class TimestampSafeDecisionEngine:
    def research_replay_packet(
        self,
        *,
        replay: Mapping[str, Any],
        case: Mapping[str, Any],
        source_data_max_time: Any,
    ) -> dict[str, Any]:
        case_data = _mapping(case)
        replay_data = _mapping(replay)
        start_point = _mapping(replay_data.get("trade_start"))
        end_point = _mapping(replay_data.get("trade_end"))
        signal_time = _timestamp(case_data.get("window_start_ist"), "window_start_ist")
        label_time = _timestamp(case_data.get("window_end_ist"), "window_end_ist")
        source_max = _timestamp(source_data_max_time, "source_data_max_time")
        decision_time = max(source_max, label_time)
        fill_time = _point_time(start_point)
        exit_time = _point_time(end_point)
        action, direction_label = _action(replay_data.get("outcome_label"))
        violations = ["known_full_window_outcome_used", "future_price_path_used"]
        if fill_time is not None and fill_time < decision_time:
            violations.append("suggested_fill_precedes_replay_decision_time")

        packet: dict[str, Any] = {
            "contract": DECISION_PACKET_CONTRACT,
            "engineVersion": ENGINE_VERSION,
            "policyVersion": "retrospective_marker_replay_v1",
            "mode": RESEARCH_REPLAY,
            "status": "observed_replay" if replay_data.get("trade_start") else "abstain",
            "symbol": "USDJPY",
            "eventId": str(case_data.get("source_event_id") or ""),
            "caseId": int(case_data.get("case_id")) if case_data.get("case_id") is not None else None,
            "familyKey": str(case_data.get("family_key") or replay_data.get("family_key") or ""),
            "times": {
                "eventWindowStart": _iso(signal_time),
                "eventWindowEnd": _iso(label_time),
                "signalTime": _iso(signal_time),
                "decisionTime": _iso(decision_time),
                "fillTime": _iso(fill_time),
                "exitTime": _iso(exit_time),
                "labelAvailableTime": _iso(label_time),
                "evidenceCutoff": _iso(decision_time),
                "sourceDataMaxTime": _iso(source_max),
            },
            "decision": {
                "action": action,
                "direction": direction_label,
                "directionSource": "known_full_window_outcome",
                "confidence": "retrospective_only",
                "reason": "Retrospective marker replay may use the completed price path and known outcome.",
            },
            "entry": {
                "state": "observed_replay",
                "rule": replay_data.get("start_rule"),
                "time": _iso(fill_time),
                "price": _point_price(start_point),
            },
            "exit": {
                "state": "observed_replay",
                "rule": replay_data.get("end_rule"),
                "time": _iso(exit_time),
                "price": _point_price(end_point),
            },
            "outcome": {
                "label": direction_label,
                "signedPips": _json_safe(replay_data.get("signed_pips")),
                "rawPips": _json_safe(replay_data.get("raw_pips")),
            },
            "featureAudit": {
                "allowlistVersion": None,
                "consumedFields": ["full_window_direction", "future_chart_candles", "future_markers"],
                "forbiddenFieldsPresentButExcluded": [],
                "inputFingerprint": _fingerprint(
                    {
                        "case_id": case_data.get("case_id"),
                        "outcome": replay_data.get("outcome_label"),
                        "start_rule": replay_data.get("start_rule"),
                        "end_rule": replay_data.get("end_rule"),
                    }
                ),
            },
            "guardrails": {
                "timestampSafe": False,
                "noLookahead": False,
                "outcomeLabelConsumed": True,
                "futurePricesConsumed": True,
                "liveEligible": False,
                "executionAllowed": False,
                "violations": violations,
            },
            "provenance": {
                "source": "reviewer_rule_replay.auto_suggest_case",
                "astronomyContract": "retrospective_pack_metadata",
            },
        }
        packet["packetId"] = _fingerprint(packet)
        return validate_decision_packet(packet)

    def live_inference_packet(
        self,
        *,
        event: Mapping[str, Any] | pd.Series,
        touch: Mapping[str, Any] | pd.Series | None,
        price: pd.DataFrame,
        decision_time: Any,
        timeframe: str,
        artifact: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        event_data = _mapping(event)
        artifact_data = _mapping(artifact)
        decision = _timestamp(decision_time, "decision_time")
        event_start = _timestamp(event_data.get("timestamp"), "event timestamp")
        event_end = _timestamp(event_data.get("event_end"), "event end")
        delta = _timeframe_delta(timeframe)
        decision_deadline = event_end + delta
        safe_features, feature_audit = sanitize_live_features(touch)
        price_audit = closed_price_summary(price, decision, timeframe)
        touch_time = _optional_timestamp(safe_features.get("touch_time_local"))
        signal_time = touch_time + delta if touch_time is not None else None

        reasons: list[str] = []
        scores: dict[str, Any] = {}
        if decision < event_start:
            reasons.append("event_not_started")
        elif decision > decision_deadline:
            reasons.append("event_window_expired")
        if not safe_features:
            reasons.append("no_touch_evidence")
        elif signal_time is None:
            reasons.append("touch_time_missing")
        elif touch_time < event_start or touch_time > event_end:
            reasons.append("touch_time_outside_event_window")
        elif signal_time > decision:
            reasons.append("touch_bar_not_closed_by_decision_time")
        if price_audit["closedBarCount"] <= 0:
            reasons.append("no_closed_price_evidence")

        raw_direction = "UNKNOWN"
        doctrine_direction = "UNKNOWN"
        if not reasons:
            scores = _json_safe(score_currency_pair_for_row(pd.Series(safe_features)))
            raw_direction = str(scores.get("fx_hypothesis_direction") or "UNKNOWN").upper()
            doctrine_direction = str(scores.get("fx_doctrine_hypothesis_direction") or "UNKNOWN").upper()
            if raw_direction not in {"BULLISH", "BEARISH"}:
                reasons.append("raw_fx_direction_conflict_or_unknown")
            if doctrine_direction not in {"BULLISH", "BEARISH"}:
                reasons.append("doctrine_fx_direction_conflict_or_unknown")
            if (
                raw_direction in {"BULLISH", "BEARISH"}
                and doctrine_direction in {"BULLISH", "BEARISH"}
                and raw_direction != doctrine_direction
            ):
                reasons.append("raw_and_doctrine_directions_disagree")

        chosen_direction = doctrine_direction if not reasons else "UNKNOWN"
        action, direction_label = _action(chosen_direction)
        status = "watch" if action in {"WATCH_LONG", "WATCH_SHORT"} else "abstain"
        reason_text = (
            "Closed touch evidence and the raw/doctrine USD-minus-JPY hypotheses agree."
            if status == "watch"
            else "; ".join(dict.fromkeys(reasons)) or "no timestamp-safe signal"
        )
        evidence_summary = {
            key: scores.get(key)
            for key in (
                "fx_hypothesis_direction",
                "fx_pair_net_score",
                "fx_pair_conflict_ratio",
                "fx_doctrine_hypothesis_direction",
                "fx_doctrine_pair_net_score",
                "fx_doctrine_pair_conflict_ratio",
                "fx_base_scored_hit_count",
                "fx_quote_scored_hit_count",
            )
            if key in scores
        }
        evidence_summary.update(
            {
                key: safe_features.get(key)
                for key in (
                    "touch_kind",
                    "touch_planets",
                    "touch_price",
                    "aspect_regime_active_count",
                    "event_orb_deg",
                    "event_strict_shadbala_implemented_total_ratio_avg",
                    "event_strict_drik_bala_virupa_avg",
                )
                if safe_features.get(key) is not None
            }
        )

        packet = {
            "contract": DECISION_PACKET_CONTRACT,
            "engineVersion": ENGINE_VERSION,
            "policyVersion": POLICY_VERSION,
            "mode": LIVE_INFERENCE,
            "status": status,
            "symbol": str(event_data.get("ticker") or artifact_data.get("symbol") or "USDJPY").upper(),
            "eventId": str(event_data.get("event_id") or ""),
            "caseId": (
                int(event_data["case_id"])
                if event_data.get("case_id") is not None and not pd.isna(event_data.get("case_id"))
                else None
            ),
            "familyKey": str(event_data.get("event_family_key") or ""),
            "times": {
                "eventWindowStart": _iso(event_start),
                "eventWindowEnd": _iso(event_end),
                "decisionDeadline": _iso(decision_deadline),
                "signalTime": _iso(signal_time),
                "decisionTime": _iso(decision),
                "fillTime": None,
                "exitTime": None,
                "labelAvailableTime": None,
                "evidenceCutoff": _iso(decision),
                "sourceDataMaxTime": price_audit["sourceDataMaxTime"],
            },
            "decision": {
                "action": action,
                "direction": direction_label,
                "directionSource": "fx_raw_and_doctrine_consensus",
                "confidence": "provisional_uncertified_watch_only",
                "reason": reason_text,
            },
            "entry": {
                "state": "unfilled_plan" if status == "watch" else "not_applicable",
                "rule": "next_market_tick_after_human_or_executor_approval" if status == "watch" else None,
                "time": None,
                "price": None,
            },
            "exit": {
                "state": "contingent_not_materialized" if status == "watch" else "not_applicable",
                "rule": "requires_certified_boundary_policy_after_fill" if status == "watch" else None,
                "time": None,
                "price": None,
            },
            "outcome": None,
            "evidence": evidence_summary,
            "priceAudit": price_audit,
            "featureAudit": feature_audit,
            "guardrails": {
                "timestampSafe": True,
                "noLookahead": True,
                "outcomeLabelConsumed": False,
                "futurePricesConsumed": False,
                "liveEligible": status == "watch",
                "executionAllowed": False,
                "violations": [],
            },
            "policyLocks": {
                "mt5Execution": "disabled",
                "automaticOrderPlacement": False,
                "reviewRulesApplied": [],
                "purgedValidationRequired": True,
                "prospectiveValidationRequired": True,
                "historicalValidationContract": VALIDATION_CONTRACT,
                "historicalValidationStatus": VALIDATION_STATUS,
                "historicalValidationReport": VALIDATION_REPORT,
                "externalAstrologyCertificationRequired": True,
            },
            "provenance": {
                "artifactId": artifact_data.get("artifactId"),
                "artifactLabel": artifact_data.get("label"),
                "astronomyContract": event_data.get("astronomy_contract_version"),
                "priceSourceId": _mapping(artifact_data.get("parameters")).get("priceSourceId"),
                "priceSourceSha256": _mapping(artifact_data.get("parameters")).get("priceSourceSha256"),
                "priceSourceAsOfUtc": _mapping(artifact_data.get("parameters")).get("priceSourceAsOfUtc"),
            },
        }
        packet["packetId"] = _fingerprint(packet)
        return validate_decision_packet(packet)


ENGINE = TimestampSafeDecisionEngine()
