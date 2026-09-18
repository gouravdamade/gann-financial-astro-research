"""Deterministic, non-evaluating real-event identity bridge for frozen V2."""

from __future__ import annotations

from typing import Any, Mapping

from .canonical import canonical_hash


def bridge_event(event: Mapping[str, Any]) -> dict[str, Any]:
    roles = event.get("eventRoles")
    if not isinstance(roles, Mapping):
        raise ValueError("event roles are required for the V2 identity bridge")
    transit = event.get("transitPositionAtExactUtc", {})
    natal = event.get("natalTargetPositionAtFrozenChartUtc", {})
    sun = event.get("sunPositionAtExactUtc", {})
    if not all(isinstance(item, Mapping) for item in (transit, natal, sun)):
        raise ValueError("event positions are required for the V2 identity bridge")
    event_id, event_hash = event.get("eventId"), event.get("eventHash")
    if not isinstance(event_id, str) or not isinstance(event_hash, str):
        raise ValueError("event identity is required for the V2 identity bridge")
    return {
        "fixtureId": event_id, "semanticFixtureIdentityHash": event_hash,
        "fixtureFamily": "REAL_CANDIDATE_C_RUN1", "sourceBody": roles.get("sourceBody"),
        "targetBody": roles.get("targetBody"), "sourceSignIndex": transit.get("signIndex"),
        "targetSignIndex": natal.get("signIndex"), "sunSignIndex": sun.get("signIndex"),
        "coverageTags": ["REAL_CANDIDATE_C_RUN1"], "optionalAspectType": None,
    }


def bridge_population_identity(events: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...]) -> tuple[list[dict[str, Any]], str]:
    bridge = [bridge_event(event) for event in events]
    if len({entry["fixtureId"] for entry in bridge}) != len(bridge):
        raise ValueError("real V2 bridge aliases event identities")
    return bridge, canonical_hash(bridge)
