"""XE2 causal-scoped real-astronomy evidence and modifier tournament.

XE2 is deliberately narrower than a prediction engine.  It reads a compact,
hash-linked set of verified astronomical event identities and raw Moon speeds.
The only signed channel in this milestone is a separately labelled synthetic
test fixture.  It is never market evidence, is not inferred from geometry, and
cannot reach price, Fields, SBC, ML, MT5, Auto Suggest, or execution.
"""

from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping


EXPERIMENT_CONTRACT = "XE2_CAUSAL_SCOPED_EVIDENCE_LAB_V1"
PROFILE_CONTRACT = "XE2_CAUSAL_SCOPED_PROFILE_V1"
TRIAL_LEDGER_CONTRACT = "XE2_CAUSAL_SCOPED_MODIFIER_TRIAL_LEDGER_V1"
PROFILE_ID = "XE2_CAUSAL_SCOPED_SPEED_MODIFIER_TOURNAMENT_V1"
XE2_ACCEPTANCE_BASELINE_COMMIT = "ccb4ee5c17dc1cce3f989832ac22196bf07b8806"
OBSERVATION_FIXTURE = Path("research_labs") / "experimental_evidence" / "fixtures" / "xe2_scoped_real_astronomical_observations_v1.json"
TRIAL_LEDGER_FIXTURE = Path("research_labs") / "experimental_evidence" / "fixtures" / "xe2_trial_ledger_v1.json"
TRANSFORMS = (
    "XE2_M0_BASE_SYNTHETIC_SIGN_TEST_V1",
    "XE2_M1_SCOPED_POSITIVE_SPEED_MULTIPLIER_V1",
    "XE2_M2_SPEED_SEPARATE_CHANNEL_V1",
    "XE2_M3_SPEED_INTERACTION_V1",
    "XE2_M4_MOTION_CONTEXT_GATE_V1",
)
GUARDRAILS = {
    "experimental": True,
    "classicalDoctrine": False,
    "priceDataRead": False,
    "priceOutcomeRead": False,
    "sbcRead": False,
    "fieldsPath": False,
    "autoSuggestPath": False,
    "mlPath": False,
    "mt5Path": False,
    "executionAllowed": False,
    "automaticOrderPlacement": False,
    "financiallyValidated": False,
    "marketForecast": False,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest().upper()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"XE2 fixture must be an object: {path.name}")
    return value


def _fixture(root: Path) -> dict[str, Any]:
    value = _read_json(root / OBSERVATION_FIXTURE)
    if value.get("contract") != "XE2_SCOPED_REAL_ASTRONOMICAL_OBSERVATION_FIXTURE_V1":
        raise ValueError("XE2 observation fixture has an unsupported contract")
    governance = value.get("datasetGovernance")
    if not isinstance(governance, Mapping) or governance.get("datasetStatus") != "TOUCHED_DEV":
        raise ValueError("XE2 requires the explicit TOUCHED_DEV governance state")
    if governance.get("marketOutcomeRead") is not False or governance.get("liveMt5Read") is not False:
        raise ValueError("XE2 may not read market outcomes or live MT5")
    source = value.get("astronomySource")
    if not isinstance(source, Mapping) or source.get("directionPolicy") != "ASPECT_GEOMETRY_NEVER_SUPPLIES_DIRECTION_BY_ITSELF":
        raise ValueError("XE2 astronomy source must prohibit geometry-derived direction")
    normalization = value.get("normalization")
    if not isinstance(normalization, Mapping) or not isinstance(normalization.get("referenceSpeedDegPerDay"), (int, float)):
        raise ValueError("XE2 speed normalization requires an explicit astronomical reference")
    events = value.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("XE2 event fixture is empty")
    seen_causes: set[str] = set()
    for event in events:
        _validate_event(event, seen_causes)
    return value


def _validate_event(event: Any, seen_causes: set[str]) -> None:
    if not isinstance(event, Mapping):
        raise ValueError("XE2 event must be an object")
    cause = event.get("causalEventId")
    if not isinstance(cause, str) or not cause or cause in seen_causes:
        raise ValueError("XE2 events require unique causalEventId values")
    seen_causes.add(cause)
    sign = event.get("syntheticSignTestValue")
    if not isinstance(sign, (int, float)) or not math.isfinite(float(sign)):
        raise ValueError("XE2 synthetic sign tests require finite numeric values")
    identity = event.get("eventIdentity")
    required = {
        "eventId", "eventHash", "sideIdentity", "instrumentIdentity", "chartId", "chartHypothesisId",
        "transitBody", "natalTarget", "aspectType", "applyingStartUtc", "exactUtc", "separatingEndUtc",
        "identityStatus", "motionPhaseAtExact", "speedDegPerDay",
    }
    if not isinstance(identity, Mapping) or any(key not in identity for key in required):
        raise ValueError("XE2 event identity is incomplete")
    if identity.get("identityStatus") != "SINGLE_PASS_VERIFIED":
        raise ValueError("XE2 accepts only independently verified single-pass event identities")
    if identity.get("transitBody") != "MOON" or not isinstance(identity.get("speedDegPerDay"), (int, float)):
        raise ValueError("XE2 v1 accepts only Moon events with raw speed values")
    if not (str(identity["applyingStartUtc"]) < str(identity["exactUtc"]) < str(identity["separatingEndUtc"])):
        raise ValueError("XE2 event boundaries must strictly surround exact UTC")


def _trial_fixture(root: Path) -> dict[str, Any]:
    value = _read_json(root / TRIAL_LEDGER_FIXTURE)
    if value.get("contract") != TRIAL_LEDGER_CONTRACT:
        raise ValueError("XE2 trial ledger has an unsupported contract")
    if value.get("datasetGovernance", {}).get("datasetStatus") != "TOUCHED_DEV":
        raise ValueError("XE2 trial ledger must keep April 2025 as TOUCHED_DEV")
    return value


def _profile() -> dict[str, Any]:
    profile = {
        "contract": PROFILE_CONTRACT,
        "schemaVersion": 1,
        "profileId": PROFILE_ID,
        "acceptanceBaselineCommit": XE2_ACCEPTANCE_BASELINE_COMMIT,
        "datasetStatus": "TOUCHED_DEV",
        "profilePurpose": "REAL_ASTRONOMICAL_INPUT_PLUS_SYNTHETIC_SIGN_TEST_ONLY",
        "realSignedEvidenceStatus": "NOT_ADMITTED_NO_REVIEWED_SIGNED_EVIDENCE",
        "causalAggregationPolicy": "XE2_ONE_SYNTHETIC_TEST_SIGN_PER_CAUSAL_EVENT_V1",
        "globalModifierDefaultAllowed": False,
        "modifierScopeRequired": "CAUSAL_EVENT_ID",
        "stackingAllowed": False,
        "executionAllowed": False,
        "transforms": [
            {"transformId": TRANSFORMS[0], "label": "M0 base synthetic sign test", "family": "BASE", "parameters": {}},
            {"transformId": TRANSFORMS[1], "label": "M1 scoped positive speed multiplier", "family": "POSITIVE_SCOPED_MULTIPLIER", "parameters": {"beta": 0.8, "mMin": 0.5, "mMax": 1.5}},
            {"transformId": TRANSFORMS[2], "label": "M2 speed separate channel", "family": "SEPARATE_CHANNEL", "parameters": {}},
            {"transformId": TRANSFORMS[3], "label": "M3 speed interaction", "family": "INTERACTION", "parameters": {"gamma": 0.5}},
            {"transformId": TRANSFORMS[4], "label": "M4 direct-motion context gate", "family": "CONTEXT_GATE", "parameters": {"acceptedMotionPhase": "DIRECT"}},
        ],
    }
    profile["profileHash"] = _sha256({key: value for key, value in profile.items() if key != "profileHash"})
    return profile


def _raw_observations(fixture: Mapping[str, Any]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for event in fixture["events"]:
        identity = event["eventIdentity"]
        cause = event["causalEventId"]
        prefix = f"XE2_OBS_{identity['eventId']}"
        common = {
            "eventId": identity["eventId"],
            "eventHash": identity["eventHash"],
            "causalEventId": cause,
            "targetScope": {"type": "CAUSAL_EVENT_ID", "causalEventId": cause},
            "timestampUtc": identity["exactUtc"],
            "sourceProfileId": "RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1",
            "identityStatus": identity["identityStatus"],
            "provenance": ["USD April 2025 reviewed packet", "identity-integrity manifest", identity["eventHash"]],
            "unknownReasons": [],
        }
        observations.extend([
            {
                **common,
                "observationId": f"{prefix}_REAL_EVENT_V1",
                "featureKey": "real_transit_to_natal_event_identity",
                "role": "CONTEXT",
                "rawValue": f"{identity['transitBody']}:{identity['natalTarget']}:{identity['aspectType']}",
                "rawUnit": "event_identity",
                "valueType": "CATEGORY",
                "sourceSemantic": "REAL_ASTRONOMICAL_EVENT_IDENTITY",
                "sourceStatus": "SOURCE_CLOSED_ASTRONOMICAL_IDENTITY",
                "roleOrigin": "REAL_ASTRONOMICAL_INPUT",
                "marketDomain": "NONE",
            },
            {
                **common,
                "observationId": f"{prefix}_REAL_SPEED_V1",
                "featureKey": "moon_speed_deg_per_day",
                "role": "MODIFIER",
                "rawValue": identity["speedDegPerDay"],
                "rawUnit": "deg/day",
                "valueType": "SCALAR",
                "sourceSemantic": "REAL_ASTRONOMICAL_SPEED",
                "sourceStatus": "SOURCE_CLOSED_ASTRONOMICAL_INPUT",
                "roleOrigin": "REAL_ASTRONOMICAL_INPUT",
                "marketDomain": "NONE",
            },
            {
                **common,
                "observationId": f"{prefix}_REAL_MOTION_V1",
                "featureKey": "moon_motion_phase",
                "role": "GATE",
                "rawValue": identity["motionPhaseAtExact"],
                "rawUnit": "motion_phase",
                "valueType": "CATEGORY",
                "sourceSemantic": "REAL_ASTRONOMICAL_MOTION_CONTEXT",
                "sourceStatus": "SOURCE_CLOSED_ASTRONOMICAL_INPUT",
                "roleOrigin": "REAL_ASTRONOMICAL_INPUT",
                "marketDomain": "NONE",
            },
            {
                **common,
                "observationId": f"{prefix}_SYNTHETIC_SIGN_V1",
                "featureKey": "synthetic_sign_test_only",
                "role": "SYNTHETIC_SIGN_TEST_ONLY",
                "rawValue": event["syntheticSignTestValue"],
                "rawUnit": "synthetic_test_units",
                "valueType": "SIGNED_SCALAR",
                "sourceSemantic": "SYNTHETIC_SIGN_TEST_ONLY_NOT_MARKET_EVIDENCE",
                "sourceStatus": "SYNTHETIC_TEST_ONLY",
                "roleOrigin": "SYNTHETIC_SIGN_TEST_ONLY",
                "marketDomain": "NONE",
            },
        ])
    return observations


def _speed_z(raw_speed: float | None, normalization: Mapping[str, Any]) -> float | None:
    if raw_speed is None or not math.isfinite(raw_speed):
        return None
    reference = float(normalization["referenceSpeedDegPerDay"])
    return (raw_speed - reference) / reference


def apply_xe2_causal_transform(
    *,
    sign_value: float | None,
    raw_speed: float | None,
    motion_phase: str | None,
    transform_id: str,
    normalization: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the frozen XE2 M0-M4 contract to one already-signed event.

    This helper intentionally knows nothing about the source of ``sign_value``.
    XE2 supplies its labelled synthetic fixture; XE3 can supply only a verified,
    outcome-blind reviewed scalar.  The formulas, parameters, causal scope, and
    no-stacking policy remain owned by the XE2 profile.
    """

    if transform_id not in TRANSFORMS:
        raise ValueError("XE2 transformId is not supported")
    if sign_value is None or not math.isfinite(float(sign_value)):
        return {
            "value": None,
            "zSpeed": _speed_z(raw_speed, normalization),
            "multiplierOrInteraction": None,
            "separateChannelValue": None,
            "contextGate": None,
            "reason": "SIGN_NOT_PROJECTABLE",
        }

    sign = float(sign_value)
    z_speed = _speed_z(raw_speed, normalization)
    factor: float | None = None
    separate_channel: float | None = None
    gate: float | None = None
    value: float | None = sign
    reason: str | None = None
    if transform_id == TRANSFORMS[1]:
        if z_speed is None:
            value = None
            reason = "MODIFIER_INPUT_UNKNOWN_TARGET_ONLY"
        else:
            factor = min(1.5, max(0.5, math.exp(0.8 * z_speed)))
            value = sign * factor
    elif transform_id == TRANSFORMS[2]:
        separate_channel = z_speed
    elif transform_id == TRANSFORMS[3]:
        if z_speed is None:
            value = None
            reason = "INTERACTION_INPUT_UNKNOWN_TARGET_ONLY"
        else:
            factor = 1 + 0.5 * z_speed
            if factor <= 0:
                value = None
                reason = "INTERACTION_FACTOR_NON_POSITIVE_FAIL_CLOSED"
            else:
                value = sign * factor
    elif transform_id == TRANSFORMS[4]:
        if motion_phase == "DIRECT":
            gate = 1.0
        else:
            value = None
            reason = "MOTION_CONTEXT_NOT_DIRECT_TARGET_ONLY"
    return {
        "value": value,
        "zSpeed": z_speed,
        "multiplierOrInteraction": factor,
        "separateChannelValue": separate_channel,
        "contextGate": gate,
        "reason": reason,
    }


def resolve_modifier_scope(modifier: Mapping[str, Any], causal_event_id: str) -> dict[str, Any]:
    """Fail closed: a modifier without an exact causal-event target never applies."""
    target = modifier.get("targetScope")
    if not isinstance(target, Mapping) or target.get("type") != "CAUSAL_EVENT_ID":
        return {
            "modifierObservationId": modifier.get("observationId", "UNKNOWN_MODIFIER"),
            "targetCausalEventId": None,
            "scopeType": "UNSCOPED",
            "scopeStatus": "REJECTED_UNSCOPED",
            "globalDefaultApplied": False,
        }
    target_cause = target.get("causalEventId")
    if target_cause != causal_event_id:
        return {
            "modifierObservationId": modifier.get("observationId", "UNKNOWN_MODIFIER"),
            "targetCausalEventId": target_cause,
            "scopeType": "CAUSAL_EVENT_ID",
            "scopeStatus": "REJECTED_UNSCOPED",
            "globalDefaultApplied": False,
        }
    return {
        "modifierObservationId": modifier.get("observationId", "UNKNOWN_MODIFIER"),
        "targetCausalEventId": target_cause,
        "scopeType": "CAUSAL_EVENT_ID",
        "scopeStatus": "BOUND",
        "globalDefaultApplied": False,
    }


def _synthetic_state_vector(contributions: list[dict[str, Any]]) -> dict[str, Any]:
    active = [float(item["value"]) for item in contributions if item.get("status") == "ACTIVE" and isinstance(item.get("value"), (int, float))]
    positive = sum(max(value, 0.0) for value in active)
    negative = sum(max(-value, 0.0) for value in active)
    activity = positive + negative
    if activity <= 0:
        return {
            "state": "UNKNOWN_NO_SYNTHETIC_SIGN_TEST",
            "positive": 0.0,
            "negative": 0.0,
            "syntheticRaw": None,
            "syntheticNormalized": None,
            "activity": 0.0,
            "conflict": None,
            "unknownCauseCount": len([item for item in contributions if item.get("status") != "ACTIVE"]),
        }
    return {
        "state": "SYNTHETIC_SIGN_TEST_ONLY",
        "positive": positive,
        "negative": negative,
        "syntheticRaw": positive - negative,
        "syntheticNormalized": (positive - negative) / activity,
        "activity": activity,
        "conflict": 2 * min(positive, negative) / activity,
        "unknownCauseCount": len([item for item in contributions if item.get("status") != "ACTIVE"]),
    }


def _compile_snapshot(fixture: Mapping[str, Any], profile: Mapping[str, Any], transform_id: str) -> dict[str, Any]:
    transform = next((item for item in profile["transforms"] if item["transformId"] == transform_id), None)
    if transform is None:
        raise ValueError("XE2 transformId is not supported")
    normalization = fixture["normalization"]
    scope_bindings: list[dict[str, Any]] = []
    contributions: list[dict[str, Any]] = []
    for event in fixture["events"]:
        identity = event["eventIdentity"]
        cause = event["causalEventId"]
        raw_speed_value = identity.get("speedDegPerDay")
        raw_speed = float(raw_speed_value) if isinstance(raw_speed_value, (int, float)) else None
        sign = float(event["syntheticSignTestValue"])
        speed_observation_id = f"XE2_OBS_{identity['eventId']}_REAL_SPEED_V1"
        motion_observation_id = f"XE2_OBS_{identity['eventId']}_REAL_MOTION_V1"
        scope = resolve_modifier_scope(
            {
                "observationId": speed_observation_id,
                "targetScope": {"type": "CAUSAL_EVENT_ID", "causalEventId": cause},
            },
            cause,
        )
        scope_bindings.append(scope)
        applied = apply_xe2_causal_transform(
            sign_value=sign,
            raw_speed=raw_speed,
            motion_phase=identity["motionPhaseAtExact"],
            transform_id=transform_id,
            normalization=normalization,
        )
        contributions.append({
            "causalEventId": cause,
            "eventId": identity["eventId"],
            "eventHash": identity["eventHash"],
            "timestampUtc": identity["exactUtc"],
            "transitBody": identity["transitBody"],
            "natalTarget": identity["natalTarget"],
            "aspectType": identity["aspectType"],
            "applyingStartUtc": identity["applyingStartUtc"],
            "separatingEndUtc": identity["separatingEndUtc"],
            "identityStatus": identity["identityStatus"],
            "sourceObservationIds": [
                f"XE2_OBS_{identity['eventId']}_REAL_EVENT_V1",
                speed_observation_id,
                motion_observation_id,
                f"XE2_OBS_{identity['eventId']}_SYNTHETIC_SIGN_V1",
            ],
            "syntheticSignObservationId": f"XE2_OBS_{identity['eventId']}_SYNTHETIC_SIGN_V1",
            "rawSyntheticSignTestValue": sign,
            "rawSpeedDegPerDay": raw_speed,
            "speedNormalizationContract": normalization["contract"],
            "zSpeed": applied["zSpeed"],
            "motionPhaseAtExact": identity["motionPhaseAtExact"],
            "scope": scope,
            "multiplierOrInteraction": applied["multiplierOrInteraction"],
            "separateChannelValue": applied["separateChannelValue"],
            "contextGate": applied["contextGate"],
            "value": applied["value"],
            "status": "ACTIVE" if applied["value"] is not None else "UNKNOWN_TARGET_ONLY",
            "reason": applied["reason"],
            "signEvidenceStatus": "SYNTHETIC_SIGN_TEST_ONLY_NOT_MARKET_EVIDENCE",
        })
    vector = _synthetic_state_vector(contributions)
    return {
        "transformId": transform_id,
        "transform": transform,
        "rawObservations": _raw_observations(fixture),
        "scopeBindings": scope_bindings,
        "causalContributions": contributions,
        "syntheticStateVector": vector,
        "marketDirectionStatus": "BLOCKED_NO_REAL_SIGNED_EVIDENCE",
        "marketOutcome": deepcopy(fixture["datasetGovernance"]),
        "rawEvidenceImmutable": True,
    }


def build_xe2_profile(project_root: Path) -> dict[str, Any]:
    _fixture(project_root)
    profile = _profile()
    return {
        "contract": EXPERIMENT_CONTRACT,
        "profile": profile,
        "availableTransforms": list(TRANSFORMS),
        "realEvidenceAdmission": {
            "astronomicalIdentity": "ADMITTED_HASH_LINKED",
            "rawAstronomicalSpeed": "ADMITTED_RAW_UNITS",
            "reviewedSignedEvidence": "NOT_ADMITTED_NONE_EXISTS",
            "syntheticSignChannel": "SYNTHETIC_SIGN_TEST_ONLY",
            "marketDirection": "BLOCKED_NO_REAL_SIGNED_EVIDENCE",
        },
        "guardrails": deepcopy(GUARDRAILS),
    }


def build_xe2_snapshot(project_root: Path, payload: Mapping[str, Any] | None) -> dict[str, Any]:
    request = dict(payload or {})
    unexpected = sorted(set(request) - {"profileId", "transformId"})
    if unexpected:
        raise ValueError(f"XE2 snapshot request contains unsupported fields: {', '.join(unexpected)}")
    if request.get("profileId", PROFILE_ID) != PROFILE_ID:
        raise ValueError("XE2 accepts only its causal-scoped research profile")
    transform_id = str(request.get("transformId", TRANSFORMS[1]))
    fixture = _fixture(project_root)
    profile = _profile()
    compilation = _compile_snapshot(fixture, profile, transform_id)
    snapshot = {
        "contract": EXPERIMENT_CONTRACT,
        "schemaVersion": 1,
        "snapshotId": _sha256({"profileHash": profile["profileHash"], "transformId": transform_id, "fixture": fixture}),
        "profile": profile,
        "datasetStatus": "TOUCHED_DEV",
        "datasetLabel": "TOUCHED DEV - REAL ASTRONOMY + SYNTHETIC SIGN TEST ONLY",
        "astronomySource": deepcopy(fixture["astronomySource"]),
        "normalization": deepcopy(fixture["normalization"]),
        **compilation,
        "guardrails": deepcopy(GUARDRAILS),
    }
    return snapshot


def compare_xe2_transforms(project_root: Path, payload: Mapping[str, Any] | None) -> dict[str, Any]:
    request = dict(payload or {})
    unexpected = sorted(set(request) - {"profileId"})
    if unexpected:
        raise ValueError(f"XE2 transform comparison contains unsupported fields: {', '.join(unexpected)}")
    profile = _profile()
    if request.get("profileId", PROFILE_ID) != PROFILE_ID:
        raise ValueError("XE2 comparison accepts only its causal-scoped profile")
    fixture = _fixture(project_root)
    return {
        "contract": "XE2_CAUSAL_SCOPED_TRANSFORM_COMPARISON_V1",
        "profileId": PROFILE_ID,
        "profileHash": profile["profileHash"],
        "datasetStatus": "TOUCHED_DEV",
        "comparisons": [
            {
                "transformId": transform_id,
                "transform": next(item for item in profile["transforms"] if item["transformId"] == transform_id),
                "syntheticStateVector": _compile_snapshot(fixture, profile, transform_id)["syntheticStateVector"],
                "marketDirectionStatus": "BLOCKED_NO_REAL_SIGNED_EVIDENCE",
            }
            for transform_id in TRANSFORMS
        ],
        "guardrails": deepcopy(GUARDRAILS),
    }


def build_xe2_trial_ledger(project_root: Path) -> dict[str, Any]:
    fixture = _trial_fixture(project_root)
    profile = _profile()
    entries: list[dict[str, Any]] = []
    for item in fixture["entries"]:
        record = {
            **item,
            "profileId": PROFILE_ID,
            "profileHash": profile["profileHash"],
            "datasetStatus": "TOUCHED_DEV",
            "marketOutcomeRead": False,
            "immutableAfterEvaluation": True,
        }
        record["entryHash"] = _sha256(record)
        entries.append(record)
    result = {
        "contract": TRIAL_LEDGER_CONTRACT,
        "ledgerId": fixture["ledgerId"],
        "profileHash": profile["profileHash"],
        "datasetGovernance": deepcopy(fixture["datasetGovernance"]),
        "entries": entries,
        "guardrails": deepcopy(GUARDRAILS),
    }
    result["ledgerHash"] = _sha256({key: value for key, value in result.items() if key != "ledgerHash"})
    return result


def _compile_from_fixture_for_test(fixture: Mapping[str, Any], transform_id: str) -> dict[str, Any]:
    """Test-only deterministic compiler hook; it accepts no HTTP/client payload."""
    return _compile_snapshot(fixture, _profile(), transform_id)
