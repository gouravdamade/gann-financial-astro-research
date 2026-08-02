from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .polarity_catalogue import (
    TargetAwarePolarityCatalogue,
    lookup_target_aware_polarity,
    normalize_instrument_id,
)


POLARITY_RANGE_CONTRACT = "CHART_CONDITIONED_CATEGORICAL_RANGE_V1"
POLARITY_RANGE_SCHEMA_VERSION = 1


def _utc(value: str, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _required(value: Any, field_name: str) -> str:
    token = str(value or "").strip()
    if not token:
        raise ValueError(f"{field_name} is required")
    return token


@dataclass(frozen=True)
class VisibleRangeAspectEvent:
    event_id: str
    start_utc: datetime
    end_utc: datetime
    transit_body: str
    natal_target: str
    aspect_type: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "VisibleRangeAspectEvent":
        start_utc = _utc(str(raw.get("startUtc") or raw.get("start_utc") or ""), "event.startUtc")
        end_utc = _utc(str(raw.get("endUtc") or raw.get("end_utc") or ""), "event.endUtc")
        if end_utc <= start_utc:
            raise ValueError("event.endUtc must be after event.startUtc")
        return cls(
            event_id=_required(raw.get("eventId") or raw.get("event_id"), "event.eventId"),
            start_utc=start_utc,
            end_utc=end_utc,
            transit_body=_required(raw.get("transitBody") or raw.get("transit_body"), "event.transitBody").upper(),
            natal_target=_required(raw.get("natalTarget") or raw.get("natal_target"), "event.natalTarget").upper(),
            aspect_type=_required(raw.get("aspectType") or raw.get("aspect_type"), "event.aspectType").lower(),
        )


def compile_categorical_visible_range(
    catalogue: TargetAwarePolarityCatalogue,
    *,
    instrument_id: str,
    chart_id: str,
    chart_hypothesis_id: str,
    range_start_utc: str,
    range_end_utc: str,
    events: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compile side-chart intervals with unknown gaps, never a numeric oscillator."""
    instrument = normalize_instrument_id(instrument_id)
    if not instrument.startswith("FX_CURRENCY:"):
        raise ValueError("visible categorical ranges require an FX_CURRENCY primary identity")
    start = _utc(range_start_utc, "rangeStartUtc")
    end = _utc(range_end_utc, "rangeEndUtc")
    if end <= start:
        raise ValueError("rangeEndUtc must be after rangeStartUtc")
    normalized_chart = _required(chart_id, "chartId")
    normalized_hypothesis = _required(chart_hypothesis_id, "chartHypothesisId")
    source_events = tuple(VisibleRangeAspectEvent.from_mapping(item) for item in events)
    clipped_events = tuple(
        event for event in source_events if event.end_utc > start and event.start_utc < end
    )
    lookup_by_event = {
        event.event_id: lookup_target_aware_polarity(
            catalogue,
            instrument_id=instrument,
            chart_id=normalized_chart,
            chart_hypothesis_id=normalized_hypothesis,
            transit_body=event.transit_body,
            natal_target=event.natal_target,
            aspect_type=event.aspect_type,
        )
        for event in clipped_events
    }
    boundaries = {start, end}
    for event in clipped_events:
        boundaries.add(max(start, event.start_utc))
        boundaries.add(min(end, event.end_utc))
    ordered = sorted(boundaries)
    intervals = []
    for index, (left, right) in enumerate(zip(ordered, ordered[1:])):
        active = [event for event in clipped_events if event.start_utc <= left and event.end_utc >= right]
        unknown = [event for event in active if lookup_by_event[event.event_id]["lookupState"] != "READY"]
        if not active:
            state, reason = "UNKNOWN", "No side-chart aspect is active in this interval."
            supportive_active = adverse_active = False
        elif unknown:
            state, reason = "UNKNOWN", "At least one active side-chart aspect has no accepted immutable categorical polarity."
            supportive_active = adverse_active = False
        else:
            states = {lookup_by_event[event.event_id]["entry"]["precomputedPolarity"] for event in active}
            supportive_active = bool(states & {"SUPPORTIVE", "MIXED"})
            adverse_active = bool(states & {"ADVERSE", "MIXED"})
            if supportive_active and adverse_active:
                state, reason = "MIXED", "Accepted supportive and adverse side-chart contexts overlap."
            elif supportive_active:
                state, reason = "SUPPORTIVE", "Accepted supportive side-chart context is active."
            elif adverse_active:
                state, reason = "ADVERSE", "Accepted adverse side-chart context is active."
            else:
                state, reason = "NEUTRAL", "Only accepted neutral side-chart contexts are active."
        intervals.append({
            "intervalId": f"{instrument.replace(':', '_')}_{index + 1:04d}",
            "startUtc": _iso(left),
            "endUtc": _iso(right),
            "polarityState": state,
            "supportiveActive": supportive_active,
            "adverseActive": adverse_active,
            "activeEventIds": [event.event_id for event in active],
            "unknownEventIds": [event.event_id for event in unknown],
            "reason": reason,
        })
    return {
        "contract": POLARITY_RANGE_CONTRACT,
        "schemaVersion": POLARITY_RANGE_SCHEMA_VERSION,
        "instrumentId": instrument,
        "sideIdentity": instrument.split(":", 1)[1],
        "chartId": normalized_chart,
        "chartHypothesisId": normalized_hypothesis,
        "rangeStartUtc": _iso(start),
        "rangeEndUtc": _iso(end),
        "sourceEventCount": len(source_events),
        "intervals": intervals,
        "stateContract": "CATEGORICAL_POLARITY_STATE",
        "magnitudeState": "MAGNITUDE_NOT_CONFIGURED",
        "guardrails": {
            "readOnly": True,
            "executionAllowed": False,
            "automaticOrderPlacement": False,
            "financiallyValidated": False,
            "actsAsSbcConfirmation": False,
        },
    }
