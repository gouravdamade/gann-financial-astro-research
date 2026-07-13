from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

import pandas as pd


TRIAL_CONTRACT = "GANN_FROZEN_PROSPECTIVE_SHADOW_TRIAL_V1"
TRIAL_GATE_CONFIGURATION = {
    "minimumWatchClusters": 100,
    "minimumCoverage": 0.10,
    "wilsonLowerMustExceed": 0.50,
    "twoSidedPBelow": 0.05,
    "meanSignedReturnMustExceedPct": 0.0,
    "minimumCalendarMonths": 4,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest().upper()


def _utc_timestamp(value: Any, label: str) -> pd.Timestamp:
    try:
        parsed = pd.Timestamp(value)
    except Exception as exc:
        raise ValueError(f"{label} is not a valid timestamp") from exc
    if pd.isna(parsed) or parsed.tzinfo is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.tz_convert("UTC")


def trial_descriptor(
    decision_payload: Mapping[str, Any],
    *,
    ledger_contract: str,
    outcome_contract: str,
    gate_configuration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    packet = decision_payload.get("packet") or {}
    artifact = decision_payload.get("artifactEvidence") or {}
    capture_key = decision_payload.get("captureKey") or {}
    raw_embedded = decision_payload.get("trialIdentity")
    if raw_embedded is not None and not isinstance(raw_embedded, Mapping):
        raise ValueError("embedded prospective trial identity must be an object")
    embedded = raw_embedded or {}
    raw_gate = embedded.get("gateConfiguration") or gate_configuration or TRIAL_GATE_CONFIGURATION
    if not isinstance(raw_gate, Mapping):
        raise ValueError("prospective gate configuration must be an object")
    gate = dict(raw_gate)
    identity = {
        "contract": TRIAL_CONTRACT,
        "ledgerContract": ledger_contract,
        "decisionContract": decision_payload.get("contract"),
        "packetContract": packet.get("contract"),
        "engineVersion": packet.get("engineVersion"),
        "policyVersion": packet.get("policyVersion"),
        "astronomyContract": artifact.get("astronomyContract"),
        "symbol": str(packet.get("symbol") or "").upper(),
        "timeframe": str(capture_key.get("timeframe") or "").upper(),
        "outcomeContract": outcome_contract,
        "horizonHours": decision_payload.get("horizonHours"),
        "gateConfiguration": gate,
    }
    required = (
        "decisionContract",
        "packetContract",
        "engineVersion",
        "policyVersion",
        "astronomyContract",
        "symbol",
        "timeframe",
        "horizonHours",
    )
    missing = [name for name in required if identity.get(name) in {None, ""}]
    if missing:
        raise ValueError(f"prospective trial identity is incomplete: {', '.join(missing)}")
    descriptor = {
        **identity,
        "gateConfigurationSha256": _fingerprint(gate),
        "trialId": _fingerprint(identity),
    }
    if embedded:
        if embedded.get("trialId") != descriptor["trialId"]:
            raise ValueError("embedded prospective trial ID does not match its decision packet")
        if embedded.get("gateConfigurationSha256") != descriptor["gateConfigurationSha256"]:
            raise ValueError("embedded prospective gate fingerprint does not match its configuration")
    return descriptor


def trial_summary(
    decisions: list[dict[str, Any]],
    outcomes: Mapping[str, dict[str, Any]],
    observed_at: Any,
    *,
    ledger_contract: str,
    outcome_contract: str,
    manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    now = _utc_timestamp(observed_at, "trial observed_at")
    manifest_gate = dict((manifest or {}).get("gateConfiguration") or TRIAL_GATE_CONFIGURATION)
    gate_hash = _fingerprint(manifest_gate)
    if not decisions:
        return {
            "contract": TRIAL_CONTRACT,
            "status": "awaiting_first_decision",
            "trialId": None,
            "policyLocked": False,
            "integrityValid": True,
            "cohortCount": 0,
            "gateConfiguration": manifest_gate,
            "gateConfigurationSha256": gate_hash,
            "firstCapturedAtUtc": None,
            "lastCapturedAtUtc": None,
            "nextOutcomeDueTimeUtc": None,
            "lastOutcomeDueTimeUtc": None,
            "dueOutcomeCount": 0,
            "notYetDueOutcomeCount": 0,
            "observedAtUtc": now.isoformat(),
            "cohorts": [],
        }

    grouped: dict[str, list[dict[str, Any]]] = {}
    descriptors: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        descriptor = trial_descriptor(
            decision,
            ledger_contract=ledger_contract,
            outcome_contract=outcome_contract,
            gate_configuration=manifest_gate if not decision.get("trialIdentity") else None,
        )
        trial_id = str(descriptor["trialId"])
        descriptors[trial_id] = descriptor
        grouped.setdefault(trial_id, []).append(decision)

    cohorts: list[dict[str, Any]] = []
    for trial_id, items in grouped.items():
        descriptor = descriptors[trial_id]
        captures = sorted(
            _utc_timestamp(item["capturedAtUtc"], "capturedAtUtc") for item in items
        )
        settled_count = sum(1 for item in items if str(item["shadowId"]) in outcomes)
        cohorts.append(
            {
                **{
                    key: value
                    for key, value in descriptor.items()
                    if key != "gateConfiguration"
                },
                "decisionCount": len(items),
                "settledDecisionCount": settled_count,
                "pendingOutcomeCount": len(items) - settled_count,
                "firstCapturedAtUtc": captures[0].isoformat(),
                "lastCapturedAtUtc": captures[-1].isoformat(),
            }
        )

    all_captures = sorted(
        _utc_timestamp(item["capturedAtUtc"], "capturedAtUtc") for item in decisions
    )
    all_due = sorted(
        _utc_timestamp(item["labelDueTimeUtc"], "labelDueTimeUtc") for item in decisions
    )
    pending_due = sorted(
        _utc_timestamp(item["labelDueTimeUtc"], "labelDueTimeUtc")
        for item in decisions
        if str(item["shadowId"]) not in outcomes
    )
    first_descriptor = dict(manifest or descriptors[next(iter(grouped))])
    manifest_trial_id = str(first_descriptor.get("trialId") or "")
    integrity_valid = len(grouped) == 1 and manifest_trial_id in grouped
    return {
        "contract": TRIAL_CONTRACT,
        "status": "frozen_policy_cohort" if integrity_valid else "mixed_policy_cohorts_blocked",
        "trialId": first_descriptor["trialId"],
        "policyLocked": integrity_valid,
        "integrityValid": integrity_valid,
        "cohortCount": len(grouped),
        "decisionContract": first_descriptor["decisionContract"],
        "packetContract": first_descriptor["packetContract"],
        "engineVersion": first_descriptor["engineVersion"],
        "policyVersion": first_descriptor["policyVersion"],
        "astronomyContract": first_descriptor["astronomyContract"],
        "symbol": first_descriptor["symbol"],
        "timeframe": first_descriptor["timeframe"],
        "outcomeContract": first_descriptor["outcomeContract"],
        "horizonHours": first_descriptor["horizonHours"],
        "gateConfiguration": manifest_gate,
        "gateConfigurationSha256": gate_hash,
        "manifestIdentitySha256": first_descriptor.get("manifestIdentitySha256"),
        "establishedAtUtc": first_descriptor.get("establishedAtUtc"),
        "seedShadowId": first_descriptor.get("seedShadowId"),
        "manifestSource": first_descriptor.get("manifestSource"),
        "firstCapturedAtUtc": all_captures[0].isoformat(),
        "lastCapturedAtUtc": all_captures[-1].isoformat(),
        "nextOutcomeDueTimeUtc": pending_due[0].isoformat() if pending_due else None,
        "lastOutcomeDueTimeUtc": all_due[-1].isoformat(),
        "dueOutcomeCount": sum(1 for due in pending_due if due <= now),
        "notYetDueOutcomeCount": sum(1 for due in pending_due if due > now),
        "observedAtUtc": now.isoformat(),
        "cohorts": cohorts,
    }
