"""Truthful representation adapter for frozen Candidate C inputs to Evaluator A's core."""

from __future__ import annotations

from typing import Any, Mapping

from .admission import REAL_ADMISSION_MARKER, RealPopulationAdmissionError


ADAPTER_ID = "MO_R4A_CANDIDATE_C_RUN1_REAL_TO_A_V1"


def adapt_real_event_for_a(event: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve frozen fields and label the input as real, never synthetic."""

    adapted = dict(event)
    adapted["_realRunAdmissionKind"] = REAL_ADMISSION_MARKER
    return adapted


def validate_adapter_a(event: Mapping[str, Any]) -> dict[str, Any]:
    """Use A's frozen shape validation helpers without entering its synthetic wrapper."""

    from ..evaluator_a import evaluator as frozen_a

    if event.get("_realRunAdmissionKind") != REAL_ADMISSION_MARKER:
        raise RealPopulationAdmissionError("A adapter requires the truthful real RUN1 admission marker")
    if event.get("_evaluatorInputKind") == "SYNTHETIC_ONLY":
        raise RealPopulationAdmissionError("real RUN1 input must never be labelled SYNTHETIC_ONLY")
    roles = event.get("eventRoles")
    if not isinstance(roles, Mapping):
        raise RealPopulationAdmissionError("A adapter requires frozen event roles")
    source = roles.get("sourceBody")
    target = roles.get("targetBody")
    if source not in frozen_a.EVENT_BODIES or target not in frozen_a.EVENT_BODIES:
        raise RealPopulationAdmissionError("A adapter has an unsupported source or target body")
    if roles.get("sourceRole") != "TRANSIT_BODY" or roles.get("targetRole") != "NATAL_TARGET":
        raise RealPopulationAdmissionError("A adapter role semantics are not frozen")
    transit = frozen_a._position(event, "transitPositionAtExactUtc", source)
    natal = frozen_a._position(event, "natalTargetPositionAtFrozenChartUtc", target)
    sun = frozen_a._position(event, "sunPositionAtExactUtc", "SUN")
    moon = frozen_a._position(event, "moonPositionAtExactUtc", "MOON")
    planetary = event.get("planetaryPositionsAtExactUtc")
    if not isinstance(planetary, list) or len(planetary) != len(frozen_a.EVENT_BODIES):
        raise RealPopulationAdmissionError("A adapter requires the frozen nine-body set")
    bodies: set[str] = set()
    for position in planetary:
        if not isinstance(position, Mapping) or position.get("body") in bodies:
            raise RealPopulationAdmissionError("A adapter has duplicate or malformed frozen planetary positions")
        body = position.get("body")
        frozen_a._position({"position": position}, "position", body if isinstance(body, str) else None)
        bodies.add(str(body))
    if bodies != set(frozen_a.EVENT_BODIES):
        raise RealPopulationAdmissionError("A adapter does not retain exactly the frozen body set")
    return {"event": event, "sourceBody": source, "targetBody": target, "transit": transit, "natal": natal, "sun": sun, "moon": moon}
