"""XE1 isolated evidence-role and modifier-ablation research service.

This module intentionally has no dependency on price, source doctrine, SBC,
Fields, Auto Suggest, ML, MT5, or execution.  It compiles only immutable,
versioned experimental observations into a transparent categorical state vector.
"""

from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping


EXPERIMENT_CONTRACT = "XE1_EXPERIMENTAL_EVIDENCE_LAB_V1"
PROFILE_CONTRACT = "XE1_EXPERIMENTAL_PROFILE_V1"
TRIAL_LEDGER_CONTRACT = "XE1_EXPERIMENTAL_TRIAL_LEDGER_V1"
PROFILE_ID = "XE1_EVIDENCE_ROLE_MODIFIER_ABLATION_V1"
XE1_SOURCE_BASELINE_COMMIT = "36bea0ba321503d809c3f88a22d06dc517809a2c"
OBSERVATION_FIXTURE = (
    Path("research_labs") / "experimental_evidence" / "fixtures" / "xe1_evidence_observations_v1.json"
)
TRIAL_LEDGER_FIXTURE = (
    Path("research_labs") / "experimental_evidence" / "fixtures" / "xe1_trial_ledger_v1.json"
)
ALLOWED_DATASET_STATUSES = frozenset({"SYNTHETIC", "TOUCHED_DEV", "MANUAL"})
ALLOWED_VALUE_TYPES = frozenset(
    {"SCALAR", "SIGNED_SCALAR", "CATEGORY", "BOOLEAN_GATE", "TUPLE_SET", "INTERVAL", "UNKNOWN"}
)
ALLOWED_ROLES = frozenset(
    {"SIGN", "MAGNITUDE", "MODIFIER", "GATE", "CONTEXT", "ACTIVATION", "UNCERTAINTY", "REGIME"}
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
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest().upper()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"XE1 fixture must be an object: {path.name}")
    return value


def _fixture(root: Path) -> dict[str, Any]:
    value = _read_json(root / OBSERVATION_FIXTURE)
    if value.get("contract") != "XE1_EVIDENCE_OBSERVATION_FIXTURE_V1":
        raise ValueError("XE1 observation fixture has an unsupported contract")
    observations = value.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("XE1 observation fixture is empty")
    for observation in observations:
        _validate_observation(observation)
    return value


def _trial_fixture(root: Path) -> dict[str, Any]:
    value = _read_json(root / TRIAL_LEDGER_FIXTURE)
    if value.get("contract") != TRIAL_LEDGER_CONTRACT:
        raise ValueError("XE1 trial ledger fixture has an unsupported contract")
    entries = value.get("entries")
    if not isinstance(entries, list):
        raise ValueError("XE1 trial ledger entries must be a list")
    return value


def _validate_observation(value: Any) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("XE1 observation must be an object")
    required = {
        "observationId", "eventId", "causalEventId", "causalClassification", "derivationRole",
        "timestampUtc", "sourceProfileId", "featureKey", "rawUnit", "valueType",
        "sourceSemantic", "sourceStatus", "provenance", "unknownReasons",
    }
    missing = sorted(key for key in required if key not in value)
    if missing:
        raise ValueError(f"XE1 observation is missing required fields: {', '.join(missing)}")
    if value.get("valueType") not in ALLOWED_VALUE_TYPES:
        raise ValueError(f"XE1 observation has unsupported value type: {value.get('valueType')}")
    if value.get("valueType") == "SIGNED_SCALAR" and not isinstance(value.get("rawValue"), (int, float)):
        raise ValueError("XE1 signed scalar observation requires a numeric raw value")
    if not isinstance(value.get("provenance"), list) or not isinstance(value.get("unknownReasons"), list):
        raise ValueError("XE1 observation provenance and unknownReasons must be lists")


def _bindings() -> list[dict[str, Any]]:
    return [
        {
            "featureKey": "synthetic_positive_direct",
            "role": "SIGN",
            "transformId": "XE1_BASE_DIRECTIONAL_V1",
            "parameters": {},
            "assignmentOrigin": "XE1_SYNTHETIC_FIXTURE",
            "marketDomain": "NONE",
            "experimentalStatus": "SYNTHETIC_DEMONSTRATION",
        },
        {
            "featureKey": "synthetic_positive_derived_axis",
            "role": "SIGN",
            "transformId": "XE1_BASE_DIRECTIONAL_V1",
            "parameters": {},
            "assignmentOrigin": "XE1_SYNTHETIC_FIXTURE",
            "marketDomain": "NONE",
            "experimentalStatus": "DERIVED_CHILD_NON_VOTING",
        },
        {
            "featureKey": "synthetic_negative_direct",
            "role": "SIGN",
            "transformId": "XE1_BASE_DIRECTIONAL_V1",
            "parameters": {},
            "assignmentOrigin": "XE1_SYNTHETIC_FIXTURE",
            "marketDomain": "NONE",
            "experimentalStatus": "SYNTHETIC_DEMONSTRATION",
        },
        {
            "featureKey": "synthetic_modifier_z",
            "role": "MODIFIER",
            "transformId": "XE1_BOUNDED_EXP_MULTIPLIER_V1",
            "parameters": {"beta": 0.65, "mMin": 0.5, "mMax": 1.5},
            "assignmentOrigin": "XE1_SYNTHETIC_FIXTURE",
            "marketDomain": "NONE",
            "experimentalStatus": "SYNTHETIC_DEMONSTRATION",
        },
        {
            "featureKey": "synthetic_gate_inactive",
            "role": "GATE",
            "transformId": "XE1_BOOLEAN_GATE_V1",
            "parameters": {},
            "assignmentOrigin": "XE1_SYNTHETIC_FIXTURE",
            "marketDomain": "NONE",
            "experimentalStatus": "SYNTHETIC_DEMONSTRATION",
        },
        {
            "featureKey": "synthetic_ambiguous_direction",
            "role": "SIGN",
            "transformId": "XE1_BASE_DIRECTIONAL_V1",
            "parameters": {},
            "assignmentOrigin": "XE1_SYNTHETIC_FIXTURE",
            "marketDomain": "NONE",
            "experimentalStatus": "AMBIGUOUS_CAUSE_FAIL_CLOSED",
        },
        {
            "featureKey": "synthetic_unknown_context",
            "role": "UNCERTAINTY",
            "transformId": "XE1_UNKNOWN_PRESERVATION_V1",
            "parameters": {},
            "assignmentOrigin": "XE1_SYNTHETIC_FIXTURE",
            "marketDomain": "NONE",
            "experimentalStatus": "SYNTHETIC_DEMONSTRATION",
        },
    ]


def _profile() -> dict[str, Any]:
    profile = {
        "contract": PROFILE_CONTRACT,
        "schemaVersion": 1,
        "profileId": PROFILE_ID,
        "codeCommit": XE1_SOURCE_BASELINE_COMMIT,
        "bindings": _bindings(),
        "causalAggregationPolicy": "XE1_ONE_DIRECTIONAL_VOTE_PER_CAUSAL_GROUP_V1",
        "oscillatorProjectionId": "XE1_CATEGORICAL_STATE_VECTOR_V1",
        "timingKernelId": None,
        "pairPolicy": {"enabled": False, "contract": "XE1_PAIR_ADAPTER_OPTIONAL_V1"},
        "datasetStatus": "SYNTHETIC",
        "trialLedgerPolicy": "XE1_IMMUTABLE_TRIAL_LEDGER_V1",
        "executionAllowed": False,
    }
    profile["profileHash"] = _sha256({key: value for key, value in profile.items() if key != "profileHash"})
    return profile


def _binding_by_feature(profile: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    bindings = profile.get("bindings")
    if not isinstance(bindings, list):
        raise ValueError("XE1 profile bindings must be a list")
    result: dict[str, Mapping[str, Any]] = {}
    for binding in bindings:
        if not isinstance(binding, Mapping) or binding.get("role") not in ALLOWED_ROLES:
            raise ValueError("XE1 profile has an invalid role binding")
        key = binding.get("featureKey")
        if not isinstance(key, str) or not key or key in result:
            raise ValueError("XE1 profile bindings require unique feature keys")
        result[key] = binding
    return result


def _bounded_exp_multiplier(z: float | None, *, beta: float, m_min: float, m_max: float) -> dict[str, Any]:
    if not (math.isfinite(beta) and math.isfinite(m_min) and math.isfinite(m_max)):
        raise ValueError("XE1 modifier parameters must be finite")
    if m_min < 0 or m_max < m_min:
        raise ValueError("XE1 modifier bounds are invalid")
    if z is None:
        return {"status": "UNKNOWN", "value": None, "reason": "MODIFIER_INPUT_UNKNOWN"}
    if not math.isfinite(z):
        return {"status": "UNKNOWN", "value": None, "reason": "MODIFIER_INPUT_NOT_FINITE"}
    value = min(m_max, max(m_min, math.exp(beta * z)))
    return {"status": "KNOWN", "value": value, "reason": None}


def _transform_value(raw: float, transform_id: str, modifier: Mapping[str, Any]) -> tuple[float | None, str | None]:
    if transform_id == "XE1_BASE_DIRECTIONAL_V1":
        return raw, None
    if transform_id == "XE1_BOUNDED_EXP_MULTIPLIER_V1":
        multiplier = modifier.get("value")
        if modifier.get("status") != "KNOWN" or not isinstance(multiplier, (int, float)):
            return None, "MODIFIER_INPUT_UNKNOWN"
        return raw * float(multiplier), None
    if transform_id == "XE1_SEPARATE_CHANNEL_V1":
        # This ablation deliberately retains the raw directional channel.
        return raw, None
    if transform_id == "XE1_INTERACTION_V1":
        z = modifier.get("z")
        if not isinstance(z, (int, float)):
            return None, "INTERACTION_INPUT_UNKNOWN"
        gamma = 0.35
        return raw + gamma * raw * float(z), None
    raise ValueError(f"XE1 transform is not recognized: {transform_id}")


def _state_vector(contributions: list[dict[str, Any]]) -> dict[str, Any]:
    active = [float(item["value"]) for item in contributions if isinstance(item.get("value"), (int, float))]
    positive = sum(max(value, 0.0) for value in active)
    negative = sum(max(-value, 0.0) for value in active)
    activity = positive + negative
    # A non-directional context or modifier is not an unknown directional cause.
    unknown_groups = [
        item for item in contributions
        if item.get("status") in {"UNKNOWN_DIRECTIONAL", "AMBIGUOUS_CAUSE_FAIL_CLOSED"}
    ]
    if activity <= 0:
        return {
            "state": "UNKNOWN_NO_ACTIVE_EVIDENCE",
            "positive": positive,
            "negative": negative,
            "directionalRaw": 0.0,
            "activity": 0.0,
            "directionalNormalized": None,
            "conflictLinear": None,
            "conflictQuad": None,
            "conflictEntropy": None,
            "unknownGroupCount": len(unknown_groups),
        }
    balance = (positive - negative) / activity
    if positive > 0 and negative > 0:
        state = "MIXED"
    elif positive > 0:
        state = "SUPPORTIVE"
    elif negative > 0:
        state = "ADVERSE"
    else:
        state = "NEUTRAL"
    probability = positive / activity
    entropy = 0.0 if probability in (0.0, 1.0) else -(
        probability * math.log(probability) + (1 - probability) * math.log(1 - probability)
    ) / math.log(2)
    return {
        "state": state,
        "positive": positive,
        "negative": negative,
        "directionalRaw": positive - negative,
        "activity": activity,
        "directionalNormalized": balance,
        "conflictLinear": 2 * min(positive, negative) / activity,
        "conflictQuad": 4 * positive * negative / (activity * activity),
        "conflictEntropy": entropy,
        "unknownGroupCount": len(unknown_groups),
    }


def _compile_snapshot(
    observations: list[dict[str, Any]], profile: Mapping[str, Any], transform_id: str
) -> dict[str, Any]:
    bindings = _binding_by_feature(profile)
    modifier_observation = next(
        (item for item in observations if item.get("featureKey") == "synthetic_modifier_z"), None
    )
    z = modifier_observation.get("rawValue") if isinstance(modifier_observation, Mapping) else None
    raw_modifier = _bounded_exp_multiplier(
        float(z) if isinstance(z, (int, float)) else None,
        beta=0.65,
        m_min=0.5,
        m_max=1.5,
    )
    modifier = {**raw_modifier, "z": z}
    groups: dict[str, list[dict[str, Any]]] = {}
    for observation in observations:
        groups.setdefault(str(observation["causalEventId"]), []).append(observation)

    contributions: list[dict[str, Any]] = []
    for causal_event_id, group in sorted(groups.items()):
        sign_items = [item for item in group if bindings[item["featureKey"]]["role"] == "SIGN"]
        derived = [item for item in sign_items if item.get("causalClassification") == "DERIVED_CHILD" or item.get("derivationRole") != "PRIMARY_EVIDENCE"]
        ambiguous = [item for item in sign_items if item.get("causalClassification") == "AMBIGUOUS"]
        direct = [item for item in sign_items if item not in derived and item not in ambiguous]
        base = {
            "causalEventId": causal_event_id,
            "sourceObservationIds": [str(item["observationId"]) for item in group],
            "derivedChildIds": [str(item["observationId"]) for item in derived],
            "causalClassification": "SHARED_CAUSE" if derived and direct else str(group[0]["causalClassification"]),
            "value": None,
            "status": "UNKNOWN",
            "reason": None,
        }
        if ambiguous:
            contributions.append({**base, "status": "AMBIGUOUS_CAUSE_FAIL_CLOSED", "reason": "MULTI_PASS_OR_MULTI_CAUSE_UNRESOLVED"})
            continue
        if not direct:
            contributions.append({**base, "status": "NON_DIRECTIONAL_OR_DERIVED_ONLY", "reason": "DERIVED_CHILD_NEVER_INDEPENDENT_VOTE" if derived else "NO_SIGN_ROLE"})
            continue
        if len(direct) != 1:
            contributions.append({**base, "status": "AMBIGUOUS_CAUSE_FAIL_CLOSED", "reason": "MULTIPLE_PRIMARY_DIRECTIONAL_OBSERVATIONS"})
            continue
        raw = direct[0].get("rawValue")
        if not isinstance(raw, (int, float)) or not math.isfinite(float(raw)):
            contributions.append({**base, "status": "UNKNOWN", "reason": "DIRECTIONAL_RAW_VALUE_UNKNOWN"})
            continue
        value, reason = _transform_value(float(raw), transform_id, modifier)
        contributions.append({
            **base,
            "sourceObservationId": direct[0]["observationId"],
            "value": value,
            "status": "ACTIVE" if value is not None else "UNKNOWN",
            "reason": reason,
            "rawDirectionalValue": float(raw),
        })

    vector = _state_vector(contributions)
    known_directional = len([item for item in contributions if item.get("status") == "ACTIVE"])
    unresolved_directional = len([item for item in contributions if item.get("status") in {"UNKNOWN", "AMBIGUOUS_CAUSE_FAIL_CLOSED"}])
    quality = known_directional / (known_directional + unresolved_directional) if known_directional + unresolved_directional else None
    return {
        "transformId": transform_id,
        "modifier": {
            "family": "POSITIVE_MULTIPLIER" if transform_id == "XE1_BOUNDED_EXP_MULTIPLIER_V1" else (
                "SEPARATE_CHANNEL" if transform_id == "XE1_SEPARATE_CHANNEL_V1" else (
                    "INTERACTION" if transform_id == "XE1_INTERACTION_V1" else "BASE"
                )
            ),
            "contract": transform_id,
            "parameters": {"beta": 0.65, "mMin": 0.5, "mMax": 1.5},
            "z": z,
            "status": modifier["status"],
            "value": modifier["value"],
            "nonSignFlipGuaranteed": transform_id == "XE1_BOUNDED_EXP_MULTIPLIER_V1",
            "reason": modifier["reason"],
        },
        "causalContributions": contributions,
        "stateVector": vector,
        "quality": {
            "knownDirectionalGroups": known_directional,
            "unresolvedDirectionalGroups": unresolved_directional,
            "confidence": quality,
            "confidenceUse": "DISPLAY_ONLY_SEPARATE_FROM_DIRECTIONAL_EVIDENCE",
            "confidenceMultipliesEvidence": False,
        },
        "experimentalOscillator": {
            "contract": "XE1_CATEGORICAL_STATE_VECTOR_V1",
            "state": vector["state"],
            "displayValue": vector["directionalNormalized"],
            "magnitudeState": "EXPERIMENTAL_NOT_FINANCIALLY_VALIDATED",
            "marketForecast": False,
            "executionAllowed": False,
        },
    }


def build_experimental_profile(project_root: Path) -> dict[str, Any]:
    _fixture(project_root)
    profile = _profile()
    return {
        "contract": EXPERIMENT_CONTRACT,
        "codeCommit": profile["codeCommit"],
        "profile": profile,
        "availableDataModes": ["SYNTHETIC", "TOUCHED_DEV", "MANUAL"],
        "availableTransforms": [
            "XE1_BASE_DIRECTIONAL_V1",
            "XE1_BOUNDED_EXP_MULTIPLIER_V1",
            "XE1_SEPARATE_CHANNEL_V1",
            "XE1_INTERACTION_V1",
        ],
        "guardrails": deepcopy(GUARDRAILS),
    }


def build_experimental_snapshot(project_root: Path, payload: Mapping[str, Any] | None) -> dict[str, Any]:
    request = dict(payload or {})
    unexpected = sorted(set(request) - {"profileId", "dataMode", "transformId"})
    if unexpected:
        raise ValueError(f"XE1 snapshot request contains unsupported fields: {', '.join(unexpected)}")
    if request.get("profileId", PROFILE_ID) != PROFILE_ID:
        raise ValueError("XE1 only accepts its isolated experimental profile")
    data_mode = str(request.get("dataMode", "SYNTHETIC"))
    if data_mode not in ALLOWED_DATASET_STATUSES:
        raise ValueError("XE1 dataMode is not supported")
    transform_id = str(request.get("transformId", "XE1_BOUNDED_EXP_MULTIPLIER_V1"))
    if transform_id not in {
        "XE1_BASE_DIRECTIONAL_V1", "XE1_BOUNDED_EXP_MULTIPLIER_V1", "XE1_SEPARATE_CHANNEL_V1", "XE1_INTERACTION_V1"
    }:
        raise ValueError("XE1 transformId is not supported")
    profile = _profile()
    fixture = _fixture(project_root)
    observations = deepcopy(fixture["observations"])
    if data_mode in {"MANUAL", "TOUCHED_DEV"}:
        observations = []
    compilation = _compile_snapshot(observations, profile, transform_id)
    input_status = {
        "MANUAL": "MANUAL_INPUT_REQUIRED",
        "TOUCHED_DEV": "TOUCHED_DEV_INPUT_NOT_CONFIGURED",
    }.get(data_mode, "NOT_APPLICABLE")
    return {
        "contract": EXPERIMENT_CONTRACT,
        "schemaVersion": 1,
        "codeCommit": profile["codeCommit"],
        "snapshotId": _sha256({"profileHash": profile["profileHash"], "dataMode": data_mode, "transformId": transform_id, "observations": observations}),
        "profile": profile,
        "dataMode": data_mode,
        "datasetStatus": data_mode,
        "datasetLabel": "EXPLORATORY_TOUCHED" if data_mode == "TOUCHED_DEV" else data_mode,
        "rawObservations": observations,
        "rawEvidenceImmutable": True,
        "manualInputStatus": input_status,
        **compilation,
        "guardrails": deepcopy(GUARDRAILS),
    }


def compare_experimental_transforms(project_root: Path, payload: Mapping[str, Any] | None) -> dict[str, Any]:
    request = dict(payload or {})
    data_mode = str(request.get("dataMode", "SYNTHETIC"))
    results = []
    for transform_id in (
        "XE1_BASE_DIRECTIONAL_V1",
        "XE1_BOUNDED_EXP_MULTIPLIER_V1",
        "XE1_SEPARATE_CHANNEL_V1",
        "XE1_INTERACTION_V1",
    ):
        snapshot = build_experimental_snapshot(
            project_root,
            {"profileId": PROFILE_ID, "dataMode": data_mode, "transformId": transform_id},
        )
        results.append({
            "transformId": transform_id,
            "stateVector": snapshot["stateVector"],
            "modifier": snapshot["modifier"],
            "quality": snapshot["quality"],
        })
    return {
        "contract": "XE1_TRANSFORM_COMPARISON_V1",
        "codeCommit": _profile()["codeCommit"],
        "profileId": PROFILE_ID,
        "profileHash": _profile()["profileHash"],
        "dataMode": data_mode,
        "comparisons": results,
        "guardrails": deepcopy(GUARDRAILS),
    }


def build_trial_ledger(project_root: Path) -> dict[str, Any]:
    fixture = _trial_fixture(project_root)
    entries: list[dict[str, Any]] = []
    for raw in fixture["entries"]:
        entry = deepcopy(raw)
        entry["experimentProfileHash"] = _profile()["profileHash"]
        entry["entryHash"] = _sha256(entry)
        entries.append(entry)
    return {
        "contract": TRIAL_LEDGER_CONTRACT,
        "codeCommit": _profile()["codeCommit"],
        "profileHash": _profile()["profileHash"],
        "ledgerId": fixture["ledgerId"],
        "entries": entries,
        "datasetGovernance": {
            "APRIL_2025_STATUS": "TOUCHED_DEV",
            "pristineHoldoutUsed": False,
            "exploratoryControlsLabel": "EXPLORATORY_TOUCHED",
        },
        "guardrails": deepcopy(GUARDRAILS),
    }


def compile_pair_relative_adapter(base: Mapping[str, Any], quote: Mapping[str, Any]) -> dict[str, Any]:
    """Read-only XE1 adapter; not the Fields pair formula and never SBC fusion."""
    base_value = base.get("directionalNormalized")
    quote_value = quote.get("directionalNormalized")
    base_quality = base.get("confidence")
    quote_quality = quote.get("confidence")
    if not isinstance(base_value, (int, float)) or not isinstance(quote_value, (int, float)):
        return {
            "contract": "XE1_PAIR_RELATIVE_EXPERIMENTAL_ADAPTER_V1",
            "state": "UNKNOWN_SIDE_EVIDENCE",
            "pairDisplay": None,
            "quality": None,
            "sbcUsed": False,
            "executionAllowed": False,
        }
    quality = min(float(base_quality), float(quote_quality)) if isinstance(base_quality, (int, float)) and isinstance(quote_quality, (int, float)) else None
    return {
        "contract": "XE1_PAIR_RELATIVE_EXPERIMENTAL_ADAPTER_V1",
        "state": "KNOWN",
        "pairDisplay": max(-1.0, min(1.0, (float(base_value) - float(quote_value)) / 2.0)),
        "quality": quality,
        "sbcUsed": False,
        "executionAllowed": False,
    }
