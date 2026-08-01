from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Any, Iterable


PRODUCT_FIRST_TIMING_PHASE_CONTRACT = "PROJECT_CONVENTION_TIMING_PHASE_V1"
PROJECT_CONVENTION_EXPERIMENTAL = "PROJECT_CONVENTION_EXPERIMENTAL"
PHASE_SPAN_RADIANS = (3 * math.pi) / 4
SAFE_MARGIN_RADIANS = math.pi / 12
EXACT_TOLERANCE_SECONDS = 30.0


def _utc(value: datetime | str) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timing phase timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _lifecycle(as_of: datetime, exact: datetime) -> str:
    seconds = (as_of - exact).total_seconds()
    if abs(seconds) <= EXACT_TOLERANCE_SECONDS:
        return "EXACT"
    return "APPLYING" if seconds < 0 else "SEPARATING"


def _guardrails() -> dict[str, object]:
    return {
        "voteWeight": 0,
        "directionalContribution": 0,
        "fusionCoefficient": 0,
        "executionAllowed": False,
        "automaticOrderPlacement": False,
        "financiallyValidated": False,
    }


def _empty(*, enabled: bool, unknown_vector_count: int = 0) -> dict[str, Any]:
    return {
        "contract": PRODUCT_FIRST_TIMING_PHASE_CONTRACT,
        "classification": PROJECT_CONVENTION_EXPERIMENTAL,
        "enabled": bool(enabled),
        "state": "UNKNOWN",
        "marketDirection": "ABSTAIN",
        "directionalInterpretation": "NOT_AVAILABLE",
        "calculationId": None,
        "activeEvents": [],
        "vectors": [],
        "unknownVectorCount": unknown_vector_count,
        "unlinkedResolvedContributionCount": 0,
        "aggregateWithheld": True,
        "aggregateWithheldReason": None,
        "sourceGapId": None,
        "realUnits": None,
        "imaginaryUnits": None,
        "resultantUnits": None,
        "grossUnits": None,
        "coherence": None,
        "conflict": None,
        "collectivePhaseRadians": None,
        "resultantFloorUnits": None,
        "safeSector": False,
        "guardrails": _guardrails(),
    }


def _event_phase(as_of: datetime, aspect: dict[str, Any]) -> dict[str, Any]:
    start, exact, end = _utc(aspect["startUtc"]), _utc(aspect["exactUtc"]), _utc(aspect["endUtc"])
    applying_window = (exact - start).total_seconds()
    separating_window = (end - exact).total_seconds()
    event = {
        "eventId": str(aspect["eventId"]),
        "label": str(aspect["label"]),
        "startUtc": start.isoformat(),
        "exactUtc": exact.isoformat(),
        "endUtc": end.isoformat(),
        "applyingWindowSeconds": applying_window if applying_window > 0 else None,
        "separatingWindowSeconds": separating_window if separating_window > 0 else None,
        "symmetricTimingDeclared": False,
    }
    if applying_window <= 0 or separating_window <= 0:
        return {
            **event,
            "lifecycle": "UNKNOWN",
            "normalizedLifecycleProgress": None,
            "timingPhaseRadians": None,
            "safeSector": False,
        }
    lifecycle = _lifecycle(as_of, exact)
    if lifecycle == "EXACT":
        normalized = 0.0
    elif lifecycle == "APPLYING":
        normalized = _clamp((as_of - exact).total_seconds() / applying_window, -1.0, 0.0)
    else:
        normalized = _clamp((as_of - exact).total_seconds() / separating_window, 0.0, 1.0)
    phase = PHASE_SPAN_RADIANS * normalized
    return {
        **event,
        "lifecycle": lifecycle,
        "normalizedLifecycleProgress": normalized,
        "timingPhaseRadians": phase,
        "safeSector": abs(phase) < math.pi / 2 - SAFE_MARGIN_RADIANS,
    }


def compile_product_first_timing_phase(
    *,
    enabled: bool,
    as_of_utc: datetime | str,
    aspects: Iterable[dict[str, Any]],
    contributions: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Compile independent event lifecycle geometry without a market signal.

    There is no approved contribution-event link profile. This mirror therefore
    keeps event timing geometry observable but refuses to construct or expose
    the previous Cartesian aggregate interference values.
    """
    if not enabled:
        return _empty(enabled=False)

    as_of = _utc(as_of_utc)
    normalized_contributions = list(contributions)
    unknown_count = sum(item.get("signedGuidanceUnits") is None for item in normalized_contributions)
    active_events: list[dict[str, Any]] = []
    for aspect in aspects:
        start, end = _utc(aspect["startUtc"]), _utc(aspect["endUtc"])
        if start <= as_of <= end:
            active_events.append(_event_phase(as_of, aspect))
    active_events.sort(key=lambda event: (event["startUtc"], event["eventId"]))
    if not active_events:
        return _empty(enabled=True, unknown_vector_count=unknown_count)

    calculation_id = _canonical_hash({
        "contract": PRODUCT_FIRST_TIMING_PHASE_CONTRACT,
        "asOfUtc": as_of.isoformat(),
        "linkProfile": "MISSING",
        "activeEvents": active_events,
    })
    if any(event["lifecycle"] == "UNKNOWN" for event in active_events):
        return {
            **_empty(enabled=True, unknown_vector_count=unknown_count),
            "state": "UNKNOWN_INVALID_EVENT_WINDOW",
            "calculationId": calculation_id,
            "activeEvents": active_events,
            "aggregateWithheldReason": "One or more active events has an undeclared zero-length applying or separating span. Its lifecycle geometry fails closed as unknown.",
        }

    resolved_count = sum(item.get("signedGuidanceUnits") is not None for item in normalized_contributions)
    return {
        **_empty(enabled=True, unknown_vector_count=unknown_count),
        "state": "UNLINKED_EVENT_GEOMETRY",
        "calculationId": calculation_id,
        "activeEvents": active_events,
        "unlinkedResolvedContributionCount": resolved_count,
        "aggregateWithheldReason": "EVENT_CONTRIBUTION_LINK_PROFILE_MISSING: active event lifecycle geometry is visible, but aggregate interference is withheld because no causal contribution-event mapping has been declared.",
        "sourceGapId": "EVENT_CONTRIBUTION_LINK_PROFILE_MISSING",
        "safeSector": all(event["safeSector"] for event in active_events),
    }
