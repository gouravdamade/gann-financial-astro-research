"""Small data models and synthetic input validation for Evaluator B."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Any, Mapping


class SyntheticInputError(ValueError):
    """Raised when a synthetic event cannot satisfy the frozen input schema."""


_POSITION_NAMES = (
    "transitPositionAtExactUtc",
    "natalTargetPositionAtFrozenChartUtc",
    "sunPositionAtExactUtc",
    "moonPositionAtExactUtc",
    "planetaryPositionsAtExactUtc",
)
_POSITION_FIELDS = (
    "body",
    "siderealLongitudeDeg",
    "siderealLongitudeSpeedDegPerDay",
    "sign",
    "signIndex",
)
_FORBIDDEN_TOP_LEVEL_FIELDS = {
    "price",
    "return",
    "marketOutcome",
    "expectedDirection",
    "pairRaw",
    "pairDisplay",
    "marketSign",
    "score",
    "magnitude",
    "polarity",
}


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SyntheticInputError(f"{label} must be an object")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SyntheticInputError(f"{label} must be a non-empty string")
    return value


def _require_number(value: Any, label: str) -> Real:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SyntheticInputError(f"{label} must be numeric")
    return value


def _validate_position(value: Any, label: str, *, require_speed: bool = True) -> dict[str, Any]:
    position = dict(_require_mapping(value, label))
    for field in _POSITION_FIELDS:
        if field not in position:
            raise SyntheticInputError(f"{label}.{field} is required")
    _require_text(position["body"], f"{label}.body")
    _require_text(position["sign"], f"{label}.sign")
    if isinstance(position["signIndex"], bool) or not isinstance(position["signIndex"], int):
        raise SyntheticInputError(f"{label}.signIndex must be an integer")
    if position["signIndex"] < 1 or position["signIndex"] > 12:
        raise SyntheticInputError(f"{label}.signIndex must be in 1..12")
    _require_number(position["siderealLongitudeDeg"], f"{label}.siderealLongitudeDeg")
    if require_speed:
        _require_number(
            position["siderealLongitudeSpeedDegPerDay"],
            f"{label}.siderealLongitudeSpeedDegPerDay",
        )
    return position


@dataclass(frozen=True)
class SyntheticEvent:
    """Validated event-shaped input without any real population container."""

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
    planetary_positions: Any
    extra_fields: frozenset[str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SyntheticEvent":
        source = _require_mapping(value, "event")
        forbidden = sorted(_FORBIDDEN_TOP_LEVEL_FIELDS.intersection(source))
        if forbidden:
            raise SyntheticInputError(f"market or interpretation fields are prohibited: {forbidden}")
        required = (
            "eventId",
            "eventHash",
            "sideIdentity",
            "chartIdentity",
            "exactUtc",
            "eventRoles",
            *_POSITION_NAMES,
        )
        missing = [field for field in required if field not in source]
        if missing:
            raise SyntheticInputError(f"missing required event fields: {missing}")
        roles = dict(_require_mapping(source["eventRoles"], "event.eventRoles"))
        source_body = _require_text(roles.get("sourceBody"), "event.eventRoles.sourceBody")
        target_body = _require_text(roles.get("targetBody"), "event.eventRoles.targetBody")
        if set(roles) != {"sourceBody", "targetBody"}:
            raise SyntheticInputError("event.eventRoles must contain only sourceBody and targetBody")
        transit = _validate_position(source["transitPositionAtExactUtc"], "event.transitPositionAtExactUtc")
        natal = _validate_position(
            source["natalTargetPositionAtFrozenChartUtc"],
            "event.natalTargetPositionAtFrozenChartUtc",
        )
        sun = _validate_position(source["sunPositionAtExactUtc"], "event.sunPositionAtExactUtc")
        moon = _validate_position(source["moonPositionAtExactUtc"], "event.moonPositionAtExactUtc")
        planetary = source["planetaryPositionsAtExactUtc"]
        if not isinstance(planetary, (Mapping, list, tuple)):
            raise SyntheticInputError("event.planetaryPositionsAtExactUtc must be an object or array")
        if isinstance(planetary, (list, tuple)):
            planetary = [dict(_require_mapping(item, "event.planetaryPositionsAtExactUtc[]")) for item in planetary]
        else:
            planetary = {str(key): dict(_require_mapping(item, f"event.planetaryPositionsAtExactUtc.{key}")) for key, item in planetary.items()}
        if source_body != transit["body"]:
            raise SyntheticInputError("eventRoles.sourceBody must match transit position body")
        if target_body != natal["body"]:
            raise SyntheticInputError("eventRoles.targetBody must match natal target position body")
        return cls(
            event_id=_require_text(source["eventId"], "event.eventId"),
            event_hash=_require_text(source["eventHash"], "event.eventHash"),
            side_identity=_require_text(source["sideIdentity"], "event.sideIdentity"),
            chart_identity=_require_text(source["chartIdentity"], "event.chartIdentity"),
            exact_utc=_require_text(source["exactUtc"], "event.exactUtc"),
            event_roles={"sourceBody": source_body, "targetBody": target_body},
            transit_position=transit,
            natal_target_position=natal,
            sun_position=sun,
            moon_position=moon,
            planetary_positions=planetary,
            extra_fields=frozenset(source).difference(required),
        )

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
            "planetaryPositionsAtExactUtc": self.planetary_positions,
        }


@dataclass(frozen=True)
class FrozenContracts:
    """Validated metadata and operators, deliberately without real arrays."""

    repository_root: str
    preregistration: dict[str, Any]
    bindings: dict[str, Any]
    shared_astronomy_metadata: dict[str, Any]
    population_manifest_metadata: dict[str, Any]
    source_profiles: dict[str, dict[str, Any]]
    component_specs: dict[str, dict[str, Any]]
    operators: dict[str, dict[str, Any]]
    operator_artifacts: dict[str, str]
    unknown_reason_codes: frozenset[str]
    expected_row_count: int
    row_templates_per_event: int
    real_frozen_population_read: bool
    real_frozen_population_artifact_read_for_validation: bool
    real_frozen_population_exposed_to_evaluator: bool
    real_frozen_population_arrays_exposed_to_evaluation_path: bool
    real_frozen_population_evaluated: bool
    real_candidate_c_output_produced: bool
    real_candidate_c_output_inspected: bool
    real_candidate_c_output_row_count: int
    execution_allowed: bool
