"""Unsigned, provenance-first multi-oscillator event activity service.

This service deliberately sits on top of the canonical chart-conditioned event
compiler. It describes event presence only: an event contributes one unit on
its half-open applying-to-separating interval. The result is not a score,
polarity, magnitude, forecast, or pair-relative field.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from chart_conditioned_transit_event_service import (
    APPROVED_ASPECT_PROFILE_ID,
    build_chart_conditioned_transit_event_range,
)


MO_ACTIVITY_CONTRIBUTION_CONTRACT = "MO_ACTIVITY_CONTRIBUTION_V1"
MO_ACTIVITY_RANGE_CONTRACT = "MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1"
MO_ACTIVITY_SIDE_CONTRACT = "MO_UNSIGNED_EVENT_ACTIVITY_SIDE_V1"
MO_EVIDENCE_MODE = "EXPLORATORY_UNSIGNED"
MO_EVENT_UNIVERSE_PROFILE_ID = APPROVED_ASPECT_PROFILE_ID
MO_BODY_UNIVERSE = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
    "RAHU",
    "KETU",
)
MO_ASPECT_TYPES = ("CONJUNCTION", "SEXTILE", "SQUARE", "TRINE", "OPPOSITION")

REQUEST_KEYS = {
    "rangeStartUtc",
    "rangeEndUtc",
    "sideIdentities",
    "aspectProfileId",
}
SUPPORTED_SIDES = ("USD", "JPY")


def _parse_utc(value: str, field_name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty UTC ISO timestamp")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _event_bounds(event: Mapping[str, Any]) -> tuple[datetime, datetime]:
    start = _parse_utc(str(event.get("applyingStartUtc") or ""), "event.applyingStartUtc")
    end = _parse_utc(str(event.get("separatingEndUtc") or ""), "event.separatingEndUtc")
    if start >= end:
        raise ValueError(f"event {event.get('eventId')!r} has an invalid half-open activity interval")
    return start, end


def _grouped_counts(events: list[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    by_body: dict[str, int] = {}
    by_aspect: dict[str, int] = {}
    for event in events:
        body = str(event.get("transitBody") or "UNKNOWN")
        aspect = str(event.get("aspectType") or "UNKNOWN")
        by_body[body] = by_body.get(body, 0) + 1
        by_aspect[aspect] = by_aspect.get(aspect, 0) + 1
    return {
        "byTransitBody": dict(sorted(by_body.items())),
        "byAspectType": dict(sorted(by_aspect.items())),
    }


def _compile_activity_intervals(
    *,
    side_identity: str,
    range_start: datetime,
    range_end: datetime,
    event_range: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[Mapping[str, Any]]]:
    events = [event for event in event_range.get("events", []) if isinstance(event, Mapping)]
    overlapping: list[Mapping[str, Any]] = []
    boundaries = {range_start, range_end}
    for event in events:
        if event.get("polarity") is not None or event.get("magnitude") is not None:
            raise ValueError("canonical event compiler returned signed or magnitude data")
        event_start, event_end = _event_bounds(event)
        if event_end <= range_start or event_start >= range_end:
            continue
        overlapping.append(event)
        boundaries.add(max(range_start, event_start))
        boundaries.add(min(range_end, event_end))

    ordered_boundaries = sorted(boundaries)
    intervals: list[dict[str, Any]] = []
    unknown_reasons = [str(reason) for reason in event_range.get("unknownReasons", []) if reason]
    if event_range.get("rejectedEvents"):
        unknown_reasons.append("EVENT_COMPILER_REJECTED_EVENTS_PRESENT")
    coverage = "UNKNOWN" if unknown_reasons else "KNOWN"
    unknown_reason = " | ".join(unknown_reasons) if unknown_reasons else None
    for left, right in zip(ordered_boundaries, ordered_boundaries[1:]):
        if left >= right:
            continue
        active_ids: list[str] = []
        for event in overlapping:
            event_start, event_end = _event_bounds(event)
            if event_start <= left < event_end:
                event_id = str(event.get("eventId") or "")
                if event_id:
                    active_ids.append(event_id)
        active_ids.sort()
        interval_id = f"MOI_{side_identity}_{_utc_iso(left).replace('-', '').replace(':', '').replace('.', '')}_{_utc_iso(right).replace('-', '').replace(':', '').replace('.', '')}"
        intervals.append(
            {
                "intervalId": interval_id,
                "startUtc": _utc_iso(left),
                "endUtc": _utc_iso(right),
                "rawActiveEventCount": len(active_ids),
                "contributingEventIds": active_ids,
                "coverage": coverage,
                "unknownReason": unknown_reason,
            }
        )
    return intervals, overlapping


def _compile_side(
    *,
    side_identity: str,
    range_start_utc: str,
    range_end_utc: str,
    aspect_profile_id: str,
) -> dict[str, Any]:
    range_start = _parse_utc(range_start_utc, "rangeStartUtc")
    range_end = _parse_utc(range_end_utc, "rangeEndUtc")
    if range_start >= range_end:
        raise ValueError("rangeStartUtc must be earlier than rangeEndUtc")
    event_range = build_chart_conditioned_transit_event_range(
        {
            "sideIdentity": side_identity,
            "rangeStartUtc": _utc_iso(range_start),
            "rangeEndUtc": _utc_iso(range_end),
            "aspectProfileId": aspect_profile_id,
        }
    )
    intervals, overlapping_events = _compile_activity_intervals(
        side_identity=side_identity,
        range_start=range_start,
        range_end=range_end,
        event_range=event_range,
    )
    event_universe_hash = str(event_range.get("generatorHash") or "")
    unknown_reasons = [str(reason) for reason in event_range.get("unknownReasons", []) if reason]
    if event_range.get("rejectedEvents"):
        unknown_reasons.append("EVENT_COMPILER_REJECTED_EVENTS_PRESENT")
    return {
        "contract": MO_ACTIVITY_SIDE_CONTRACT,
        "schemaVersion": 1,
        "evidenceMode": MO_EVIDENCE_MODE,
        "sideIdentity": side_identity,
        "instrumentIdentity": f"FX_CURRENCY:{side_identity}",
        "chartId": event_range.get("chartId"),
        "chartHypothesisId": event_range.get("chartHypothesisId"),
        "rangeStartUtc": _utc_iso(range_start),
        "rangeEndUtc": _utc_iso(range_end),
        "eventUniverseProfileId": MO_EVENT_UNIVERSE_PROFILE_ID,
        "eventUniverseProfileHash": event_universe_hash,
        "bodyUniverse": list(MO_BODY_UNIVERSE),
        "aspectProfile": {
            "profileId": aspect_profile_id,
            "aspectTypes": list(MO_ASPECT_TYPES),
            "maxOrbDeg": 3.0,
            "directionPolicy": "GEOMETRY_ONLY",
            "doctrineStatus": "EXPERIMENTAL_GEOMETRY_PROFILE",
        },
        "astronomy": {
            "astronomyContract": event_range.get("astronomyContract"),
            "historicalCivilTimeConversionPolicy": event_range.get("historicalCivilTimeConversionPolicy"),
            "ephemerisProvider": event_range.get("ephemerisProvider"),
            "ephemerisVersion": event_range.get("ephemerisVersion"),
            "ayanamsha": event_range.get("ayanamsha"),
            "nodePolicy": event_range.get("nodePolicy"),
            "generatorVersion": event_range.get("generatorVersion"),
            "generatorHash": event_universe_hash,
        },
        "events": [dict(event) for event in overlapping_events],
        "activityIntervals": intervals,
        "sourceEventCount": len(event_range.get("events", [])),
        "eligibleEventCount": len(overlapping_events),
        "rejectedEventCount": len(event_range.get("rejectedEvents", [])),
        "groupedCounts": _grouped_counts(overlapping_events),
        "coverage": "UNKNOWN" if unknown_reasons else "KNOWN",
        "unknownReason": " | ".join(unknown_reasons) if unknown_reasons else None,
        "guardrails": {
            "readOnly": True,
            "unsigned": True,
            "nonPredictive": True,
            "polarityAssigned": False,
            "magnitudeAssigned": False,
            "priceDataRead": False,
            "priceOutcomeRead": False,
            "sbcRead": False,
            "llmRead": False,
            "executionAllowed": False,
            "automaticOrderPlacement": False,
            "pairDifferenceComputed": False,
            "normalizationUsed": False,
            "smoothingUsed": False,
        },
    }


def build_multi_oscillator_activity_range(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build exact unsigned activity intervals for the accepted USD/JPY sides."""
    if not isinstance(payload, Mapping):
        raise ValueError("multi-oscillator activity request must be an object")
    unknown = sorted(set(payload) - REQUEST_KEYS)
    if unknown:
        raise ValueError("Unknown multi-oscillator activity request field(s): " + ", ".join(unknown))
    aspect_profile_id = str(payload.get("aspectProfileId") or "")
    if aspect_profile_id != APPROVED_ASPECT_PROFILE_ID:
        raise ValueError(f"unsupported event universe profile: {aspect_profile_id or '<missing>'}")
    side_identities = payload.get("sideIdentities")
    if (
        not isinstance(side_identities, list)
        or len(side_identities) != len(SUPPORTED_SIDES)
        or not all(isinstance(side, str) for side in side_identities)
        or sorted(side_identities) != sorted(SUPPORTED_SIDES)
    ):
        raise ValueError("sideIdentities must contain exactly USD and JPY")
    range_start = _parse_utc(str(payload.get("rangeStartUtc") or ""), "rangeStartUtc")
    range_end = _parse_utc(str(payload.get("rangeEndUtc") or ""), "rangeEndUtc")
    if range_start >= range_end:
        raise ValueError("rangeStartUtc must be earlier than rangeEndUtc")

    fields = {
        side: _compile_side(
            side_identity=side,
            range_start_utc=_utc_iso(range_start),
            range_end_utc=_utc_iso(range_end),
            aspect_profile_id=aspect_profile_id,
        )
        for side in SUPPORTED_SIDES
    }
    generator_hashes = sorted(str(fields[side]["eventUniverseProfileHash"]) for side in SUPPORTED_SIDES)
    return {
        "contract": MO_ACTIVITY_RANGE_CONTRACT,
        "schemaVersion": 1,
        "evidenceMode": MO_EVIDENCE_MODE,
        "contributionContract": MO_ACTIVITY_CONTRIBUTION_CONTRACT,
        "rangeStartUtc": _utc_iso(range_start),
        "rangeEndUtc": _utc_iso(range_end),
        "sideIdentities": list(SUPPORTED_SIDES),
        "eventUniverse": {
            "profileId": MO_EVENT_UNIVERSE_PROFILE_ID,
            "profileHash": generator_hashes[0] if generator_hashes and len(set(generator_hashes)) == 1 else generator_hashes,
            "bodyUniverse": list(MO_BODY_UNIVERSE),
            "aspectTypes": list(MO_ASPECT_TYPES),
            "maxOrbDeg": 3.0,
            "directionPolicy": "GEOMETRY_ONLY",
            "doctrineStatus": "EXPERIMENTAL_GEOMETRY_PROFILE",
        },
        "fields": fields,
        "guardrails": {
            "readOnly": True,
            "unsigned": True,
            "nonPredictive": True,
            "polarityAssigned": False,
            "magnitudeAssigned": False,
            "priceDataRead": False,
            "priceOutcomeRead": False,
            "sbcRead": False,
            "llmRead": False,
            "executionAllowed": False,
            "automaticOrderPlacement": False,
            "pairDifferenceComputed": False,
            "normalizationUsed": False,
            "smoothingUsed": False,
        },
    }


__all__ = [
    "MO_ACTIVITY_CONTRIBUTION_CONTRACT",
    "MO_ACTIVITY_RANGE_CONTRACT",
    "build_multi_oscillator_activity_range",
]
