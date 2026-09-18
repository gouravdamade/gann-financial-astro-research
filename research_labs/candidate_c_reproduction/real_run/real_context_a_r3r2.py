"""Successor-owned truthful context adapter for frozen Evaluator A templates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class RealAContextError(ValueError):
    """Raised for an invalid real-shaped input before any source evaluation."""


def build_real_a_context(event: Mapping[str, Any], frozen_evaluator: Any) -> dict[str, Any]:
    """Match the frozen template context without calling its synthetic gate."""

    if event.get("_evaluatorInputKind") == "SYNTHETIC_ONLY":
        raise RealAContextError("truthful real adapter refuses synthetic relabelling")
    if not isinstance(event.get("eventId"), str) or not isinstance(event.get("eventHash"), str):
        raise RealAContextError("event identity is required")
    roles = event.get("eventRoles")
    if not isinstance(roles, Mapping) or roles.get("sourceRole") != "TRANSIT_BODY" or roles.get("targetRole") != "NATAL_TARGET":
        raise RealAContextError("frozen transit/natal role semantics are required")
    bodies = frozen_evaluator.EVENT_BODIES
    signs = frozen_evaluator.SIGN_NAMES
    source, target = roles.get("sourceBody"), roles.get("targetBody")
    if source not in bodies or target not in bodies:
        raise RealAContextError("source and target must be frozen body identities")

    def position(field: str, expected: str | None = None) -> Mapping[str, Any]:
        value = event.get(field)
        if not isinstance(value, Mapping) or value.get("body") not in bodies or (expected and value.get("body") != expected):
            raise RealAContextError(f"invalid body at {field}")
        if signs.get(value.get("signIndex")) != value.get("sign"):
            raise RealAContextError(f"inconsistent sign at {field}")
        speed = value.get("siderealLongitudeSpeedDegPerDay")
        if isinstance(speed, bool) or not isinstance(speed, (int, float)):
            raise RealAContextError(f"non-numeric frozen speed at {field}")
        return value

    transit = position("transitPositionAtExactUtc", source)
    natal = position("natalTargetPositionAtFrozenChartUtc", target)
    sun = position("sunPositionAtExactUtc", "SUN")
    moon = position("moonPositionAtExactUtc", "MOON")
    planetary = event.get("planetaryPositionsAtExactUtc")
    if not isinstance(planetary, Sequence) or isinstance(planetary, (str, bytes)) or len(planetary) != len(bodies):
        raise RealAContextError("nine-body population is incomplete")
    seen: set[str] = set()
    for item in planetary:
        if not isinstance(item, Mapping) or item.get("body") in seen:
            raise RealAContextError("nine-body population has invalid or duplicate bodies")
        position_value = dict(item)
        if position_value.get("body") not in bodies or signs.get(position_value.get("signIndex")) != position_value.get("sign"):
            raise RealAContextError("nine-body position has inconsistent sign")
        speed = position_value.get("siderealLongitudeSpeedDegPerDay")
        if isinstance(speed, bool) or not isinstance(speed, (int, float)):
            raise RealAContextError("nine-body position has non-numeric frozen speed")
        seen.add(str(position_value["body"]))
    if seen != set(bodies):
        raise RealAContextError("nine-body set differs from frozen evaluator set")
    return {"event": event, "sourceBody": source, "targetBody": target, "transit": transit, "natal": natal, "sun": sun, "moon": moon}
