"""Independent truthful representation adapter for Evaluator B's frozen core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .admission import REAL_ADMISSION_MARKER, RealPopulationAdmissionError


ADAPTER_ID = "MO_R4A_CANDIDATE_C_RUN1_REAL_TO_B_V1"


@dataclass(frozen=True)
class RealCandidateCEvent:
    """A real frozen event shape consumed by B's unchanged component functions."""

    event_id: str
    event_hash: str
    side_identity: str
    chart_identity: str
    exact_utc: str
    event_roles: dict[str, str]
    transit_position: dict[str, Any]
    natal_target_position: dict[str, Any]
    sun_position: dict[str, Any]
    moon_position: dict[str, Any]
    planetary_positions: dict[str, dict[str, Any]]

    def input_identity(self) -> dict[str, Any]:
        return {
            "eventId": self.event_id,
            "eventHash": self.event_hash,
            "sideIdentity": self.side_identity,
            "chartIdentity": self.chart_identity,
            "exactUtc": self.exact_utc,
            "eventRoles": dict(self.event_roles),
            "transitPositionAtExactUtc": dict(self.transit_position),
            "natalTargetPositionAtFrozenChartUtc": dict(self.natal_target_position),
            "sunPositionAtExactUtc": dict(self.sun_position),
            "moonPositionAtExactUtc": dict(self.moon_position),
            "planetaryPositionsAtExactUtc": {body: dict(position) for body, position in self.planetary_positions.items()},
        }


def adapt_real_event_for_b(event: Mapping[str, Any]) -> RealCandidateCEvent:
    """Adapt only schema representation; retain every frozen scientific input."""

    from ..evaluator_b.models import SyntheticInputError, SyntheticEvent

    if event.get("_realRunAdmissionKind") != REAL_ADMISSION_MARKER:
        raise RealPopulationAdmissionError("B adapter requires the truthful real RUN1 admission marker")
    if event.get("_evaluatorInputKind") == "SYNTHETIC_ONLY":
        raise RealPopulationAdmissionError("real RUN1 input must never be labelled SYNTHETIC_ONLY")
    b_mapping = dict(event)
    b_mapping.pop("_realRunAdmissionKind", None)
    b_mapping["chartIdentity"] = str(event.get("chartIdentity", {}).get("chartId", ""))
    roles = event.get("eventRoles")
    if not isinstance(roles, Mapping):
        raise RealPopulationAdmissionError("B adapter requires frozen event roles")
    b_mapping["eventRoles"] = {"sourceBody": roles.get("sourceBody"), "targetBody": roles.get("targetBody")}
    b_mapping["planetaryPositionsAtExactUtc"] = {
        str(position.get("body")): dict(position)
        for position in event.get("planetaryPositionsAtExactUtc", [])
        if isinstance(position, Mapping)
    }
    try:
        validated = SyntheticEvent.from_mapping(b_mapping)
    except SyntheticInputError as exc:
        raise RealPopulationAdmissionError(f"B adapter shape validation failed: {exc}") from exc
    return RealCandidateCEvent(
        event_id=validated.event_id,
        event_hash=validated.event_hash,
        side_identity=validated.side_identity,
        chart_identity=validated.chart_identity,
        exact_utc=validated.exact_utc,
        event_roles=dict(validated.event_roles),
        transit_position=dict(validated.transit_position),
        natal_target_position=dict(validated.natal_target_position),
        sun_position=dict(validated.sun_position),
        moon_position=dict(validated.moon_position),
        planetary_positions={body: dict(position) for body, position in validated.planetary_positions.items()},
    )
