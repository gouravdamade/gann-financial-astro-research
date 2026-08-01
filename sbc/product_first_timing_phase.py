from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Any, Iterable


PRODUCT_FIRST_TIMING_PHASE_CONTRACT = "PROJECT_CONVENTION_TIMING_PHASE_V0"
PROJECT_CONVENTION_EXPERIMENTAL = "PROJECT_CONVENTION_EXPERIMENTAL"
PHASE_SPAN_RADIANS = (3 * math.pi) / 4
SAFE_MARGIN_RADIANS = math.pi / 12
RESULTANT_FLOOR_UNITS = 0.25
RELATIVE_RESULTANT_FLOOR = 0.15


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
    if abs(seconds) <= 30:
        return "EXACT"
    return "APPLYING" if seconds < 0 else "SEPARATING"


def compile_product_first_timing_phase(
    *,
    enabled: bool,
    as_of_utc: datetime | str,
    aspects: Iterable[dict[str, Any]],
    contributions: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Compile the product timing geometry without creating a market signal.

    This is the backend mirror of the fixed Product First phase visual. Inputs
    are supplied by the reviewed SBC snapshot; the result is deterministic,
    timestamp-safe and carries no vote or execution authority.
    """
    guardrails = {
        "voteWeight": 0,
        "directionalContribution": 0,
        "fusionCoefficient": 0,
        "executionAllowed": False,
        "automaticOrderPlacement": False,
        "financiallyValidated": False,
    }
    base = {
        "contract": PRODUCT_FIRST_TIMING_PHASE_CONTRACT,
        "classification": PROJECT_CONVENTION_EXPERIMENTAL,
        "enabled": bool(enabled),
        "marketDirection": "ABSTAIN",
        "guardrails": guardrails,
    }
    if not enabled:
        return {
            **base,
            "state": "UNKNOWN",
            "directionalInterpretation": "NOT_AVAILABLE",
            "calculationId": None,
            "activeEvents": [], "vectors": [], "unknownVectorCount": 0,
            "realUnits": None, "imaginaryUnits": None, "resultantUnits": None,
            "grossUnits": None, "coherence": None, "conflict": None,
            "collectivePhaseRadians": None, "resultantFloorUnits": None, "safeSector": False,
        }

    as_of = _utc(as_of_utc)
    normalized_aspects: list[dict[str, Any]] = []
    for aspect in aspects:
        start, exact, end = _utc(aspect["startUtc"]), _utc(aspect["exactUtc"]), _utc(aspect["endUtc"])
        if start > exact or exact > end:
            raise ValueError("timing phase event must satisfy start <= exact <= end")
        if start <= as_of <= end:
            half_window = max(1.0, (end - start).total_seconds() / 2.0)
            phase = PHASE_SPAN_RADIANS * _clamp((as_of - exact).total_seconds() / half_window, -1.0, 1.0)
            normalized_aspects.append({
                "eventId": str(aspect["eventId"]),
                "label": str(aspect["label"]),
                "startUtc": start.isoformat(), "exactUtc": exact.isoformat(), "endUtc": end.isoformat(),
                "lifecycle": _lifecycle(as_of, exact), "halfWindowSeconds": half_window,
                "timingPhaseRadians": phase,
                "safeSector": abs(phase) < math.pi / 2 - SAFE_MARGIN_RADIANS,
            })
    active_events = sorted(normalized_aspects, key=lambda event: (event["startUtc"], event["eventId"]))
    normalized_contributions = list(contributions)
    resolved = [item for item in normalized_contributions if item.get("signedGuidanceUnits") is not None]
    if not active_events:
        return {
            **base,
            "state": "UNKNOWN", "directionalInterpretation": "NOT_AVAILABLE",
            "calculationId": _canonical_hash({"contract": PRODUCT_FIRST_TIMING_PHASE_CONTRACT, "asOfUtc": as_of.isoformat(), "activeEvents": []}),
            "activeEvents": [], "vectors": [], "unknownVectorCount": len(normalized_contributions),
            "realUnits": None, "imaginaryUnits": None, "resultantUnits": None,
            "grossUnits": None, "coherence": None, "conflict": None,
            "collectivePhaseRadians": None, "resultantFloorUnits": None, "safeSector": False,
        }

    vectors: list[dict[str, Any]] = []
    for event in active_events:
        for index, contribution in enumerate(resolved):
            signed = float(contribution["signedGuidanceUnits"])
            polarity = "SUPPORTIVE" if signed >= 0 else "ADVERSE"
            source_phase = 0.0 if polarity == "SUPPORTIVE" else math.pi
            total_phase = source_phase + event["timingPhaseRadians"]
            vectors.append({
                "vectorId": f'{event["eventId"]}:{contribution.get("body", "UNKNOWN")}:{contribution.get("target", "UNKNOWN")}:{index}',
                "eventId": event["eventId"], "eventLabel": event["label"],
                "body": str(contribution.get("body", "UNKNOWN")), "target": str(contribution.get("target", "UNKNOWN")),
                "sourcePolarity": polarity, "sourcePhaseRadians": source_phase,
                "timingPhaseRadians": event["timingPhaseRadians"], "totalPhaseRadians": total_phase,
                "magnitudeUnits": abs(signed), "realUnits": abs(signed) * math.cos(total_phase),
                "imaginaryUnits": abs(signed) * math.sin(total_phase),
                "lifecycle": event["lifecycle"], "safeSector": event["safeSector"],
            })
    real_units = sum(vector["realUnits"] for vector in vectors)
    imaginary_units = sum(vector["imaginaryUnits"] for vector in vectors)
    resultant_units = math.hypot(real_units, imaginary_units)
    gross_units = sum(vector["magnitudeUnits"] for vector in vectors)
    resultant_floor = max(RESULTANT_FLOOR_UNITS, gross_units * RELATIVE_RESULTANT_FLOOR)
    near_zero = not vectors or resultant_units < resultant_floor
    safe_sector = all(event["safeSector"] for event in active_events)
    state = "RESULTANT_NEAR_ZERO" if near_zero else ("PROJECT_CONVENTION_GEOMETRY" if safe_sector else "NON_DIRECTIONAL_TIMING_GEOMETRY")
    identity = {"contract": PRODUCT_FIRST_TIMING_PHASE_CONTRACT, "asOfUtc": as_of.isoformat(), "activeEvents": active_events, "vectors": vectors}
    return {
        **base, "state": state,
        "directionalInterpretation": "SUPPRESSED" if safe_sector and not near_zero else "NOT_AVAILABLE",
        "calculationId": _canonical_hash(identity), "activeEvents": active_events, "vectors": vectors,
        "unknownVectorCount": (len(normalized_contributions) - len(resolved)) * len(active_events),
        "realUnits": real_units, "imaginaryUnits": imaginary_units, "resultantUnits": resultant_units,
        "grossUnits": gross_units, "coherence": resultant_units / gross_units if gross_units else None,
        "conflict": 1 - resultant_units / gross_units if gross_units else None,
        "collectivePhaseRadians": None if near_zero else math.atan2(imaginary_units, real_units),
        "resultantFloorUnits": resultant_floor, "safeSector": safe_sector,
    }
