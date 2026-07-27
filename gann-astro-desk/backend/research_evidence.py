from __future__ import annotations

import math
from typing import Any, Mapping, Sequence


RESEARCH_EVIDENCE_CONTRACT = "GANN_RESEARCH_EVIDENCE_PACKET_V1"
RESEARCH_EVIDENCE_CHANNELS = (
    "direction",
    "activation",
    "conflict",
    "confidence",
)
RESEARCH_EVIDENCE_STATUSES = {
    "MEASURED",
    "UNKNOWN",
    "NOT_APPLICABLE",
    "BLOCKED",
}


def _finite_optional(value: Any, label: str) -> float | None:
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite or null")
    return number


def _normalize_channel(name: str, raw: Mapping[str, Any]) -> dict[str, Any]:
    status = str(raw.get("status") or "").strip().upper()
    if status not in RESEARCH_EVIDENCE_STATUSES:
        raise ValueError(f"{name} uses unsupported evidence status: {status or '(blank)'}")
    value = _finite_optional(raw.get("value"), f"{name} value")
    if status != "MEASURED" and value is not None:
        raise ValueError(f"{name} may carry a numeric value only when status is MEASURED")
    reason = str(raw.get("reason") or "").strip()
    if status != "MEASURED" and not reason:
        raise ValueError(f"{name} requires a reason when it is not measured")
    return {
        "status": status,
        "value": value,
        "unit": str(raw.get("unit") or "").strip() or None,
        "label": str(raw.get("label") or name.replace("_", " ").title()).strip(),
        "reason": reason or None,
    }


def build_research_evidence_packet(
    *,
    source_family: str,
    source_profile_id: str,
    calculation_version: str,
    observed_at_unix: int,
    role: str,
    channels: Mapping[str, Mapping[str, Any]],
    descriptors: Sequence[Mapping[str, Any]] = (),
    provenance: Mapping[str, Any] | None = None,
    unknown_reasons: Sequence[str] = (),
) -> dict[str, Any]:
    if set(channels) != set(RESEARCH_EVIDENCE_CHANNELS):
        raise ValueError("research evidence must define direction, activation, conflict, and confidence")
    timestamp = int(observed_at_unix)
    if timestamp <= 0:
        raise ValueError("observed_at_unix must be a positive Unix timestamp")

    normalized_descriptors: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for raw in descriptors:
        key = str(raw.get("key") or "").strip()
        if not key or key in seen_keys:
            raise ValueError("evidence descriptor keys must be non-empty and unique")
        seen_keys.add(key)
        value = raw.get("value")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"descriptor {key} must be finite")
        normalized_descriptors.append(
            {
                "key": key,
                "label": str(raw.get("label") or key.replace("_", " ").title()).strip(),
                "value": value,
                "unit": str(raw.get("unit") or "").strip() or None,
                "status": str(raw.get("status") or "OBSERVED").strip().upper(),
            }
        )

    return {
        "contract": RESEARCH_EVIDENCE_CONTRACT,
        "sourceFamily": str(source_family).strip().upper(),
        "sourceProfileId": str(source_profile_id).strip(),
        "calculationVersion": str(calculation_version).strip(),
        "observedAtUnix": timestamp,
        "role": str(role).strip().upper(),
        "channels": {
            name: _normalize_channel(name, channels[name])
            for name in RESEARCH_EVIDENCE_CHANNELS
        },
        "descriptors": normalized_descriptors,
        "unknownReasons": [
            reason
            for item in unknown_reasons
            if (reason := str(item).strip())
        ],
        "provenance": dict(provenance or {}),
        "empiricalCoefficient": 0.0,
        "guardrails": {
            "timestampSafe": True,
            "researchOnly": True,
            "consumedByLiveInference": False,
            "consumedByAutoSuggest": False,
            "consumedByOfficialMlNotes": False,
            "executionAllowed": False,
        },
    }


def build_context_only_evidence_packet(
    *,
    source_family: str,
    source_profile_id: str,
    calculation_version: str,
    observed_at_unix: int,
    descriptors: Sequence[Mapping[str, Any]],
    provenance: Mapping[str, Any] | None = None,
    reason: str,
) -> dict[str, Any]:
    channels = {
        name: {
            "status": "NOT_APPLICABLE",
            "value": None,
            "unit": None,
            "label": name.replace("_", " ").title(),
            "reason": reason,
        }
        for name in RESEARCH_EVIDENCE_CHANNELS
    }
    return build_research_evidence_packet(
        source_family=source_family,
        source_profile_id=source_profile_id,
        calculation_version=calculation_version,
        observed_at_unix=observed_at_unix,
        role="CONTEXT_ONLY",
        channels=channels,
        descriptors=descriptors,
        provenance=provenance,
    )
