"""Independent synthetic-only implementation of the frozen Candidate C rules."""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from .canonical import canonical_json_bytes, sha256_bytes
from .contract_loader import load_frozen_contracts
from .models import FrozenContracts, SyntheticEvent


class RealCandidateCExecutionBlocked(RuntimeError):
    """Candidate C real-population execution is not authorized in B1."""


_OUTPUT_FIELDS = {
    "eventId",
    "sourceProfile",
    "componentId",
    "sourceContractId",
    "inputIdentity",
    "inputIdentityHash",
    "outputStatus",
    "provenance",
    "sourceValue",
    "unknownReasonCode",
}
_SOURCE_PROFILES = {
    "TRAILOKYA_DIPIKA_1972",
    "BJ_SARAVALI_CROSS_TEXT_CONTRACTS_AS_SEPARATE_PROFILES",
}
_SIGN_NAMES = {
    1: "ARIES",
    2: "TAURUS",
    3: "GEMINI",
    4: "CANCER",
    5: "LEO",
    6: "VIRGO",
    7: "LIBRA",
    8: "SCORPIO",
    9: "SAGITTARIUS",
    10: "CAPRICORN",
    11: "AQUARIUS",
    12: "PISCES",
}


def _relative_place(source_sign: int, target_sign: int) -> int:
    return ((target_sign - source_sign) % 12) + 1


def _row_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["eventId"],
        row["sourceProfile"],
        row["componentId"],
        row["sourceContractId"],
        row["provenance"]["operatorId"],
    )


def _operator(contracts: FrozenContracts, operator_id: str) -> Mapping[str, Any]:
    return contracts.operators[operator_id]


def _component(contracts: FrozenContracts, component_id: str) -> Mapping[str, Any]:
    return contracts.component_specs[component_id]


def _make_row(
    event: SyntheticEvent,
    contracts: FrozenContracts,
    component_id: str,
    operator_id: str,
    output_status: str,
    *,
    source_value: Any = None,
    unknown_reason: str | None = None,
) -> dict[str, Any]:
    component = _component(contracts, component_id)
    operator = _operator(contracts, operator_id)
    input_identity = event.input_identity()
    provenance = {
        "sourceProfile": component["sourceProfile"],
        "sourceContractId": operator_id,
        "operatorId": operator_id,
        "operatorVersion": operator.get("operatorVersion"),
        "sourceArtifact": contracts.operator_artifacts[operator_id],
        "sourceStatus": operator.get("sourceStatus"),
        "sourceLocator": operator.get("verseOrLocator"),
    }
    row = {
        "eventId": event.event_id,
        "sourceProfile": component["sourceProfile"],
        "componentId": component_id,
        "sourceContractId": operator_id,
        "inputIdentity": input_identity,
        "inputIdentityHash": sha256_bytes(canonical_json_bytes(input_identity)),
        "outputStatus": output_status,
        "provenance": provenance,
    }
    if output_status == "VALUE":
        row["sourceValue"] = source_value
    else:
        row["unknownReasonCode"] = unknown_reason or "UNKNOWN"
    return row


def _unknown(event: SyntheticEvent, contracts: FrozenContracts, component_id: str, operator_id: str, reason: str) -> dict[str, Any]:
    if reason not in contracts.unknown_reason_codes:
        raise ValueError(f"unknown reason is not in the frozen taxonomy: {reason}")
    return _make_row(event, contracts, component_id, operator_id, "UNKNOWN", unknown_reason=reason)


def _natural_class(event: SyntheticEvent, contracts: FrozenContracts, motion_value: str | None) -> dict[str, Any]:
    component_id = "C01_NATURAL_PLANET_CLASS"
    operator_id = "TRAILOKYA_1972_NATURAL_PLANET_CLASS_V1"
    body = event.event_roles["sourceBody"]
    if body == "MOON":
        return _unknown(event, contracts, component_id, operator_id, "MOON_CONDITION_INPUT_UNAVAILABLE")
    if body == "MERCURY":
        return _unknown(event, contracts, component_id, operator_id, "MERCURY_ASSOCIATION_INPUT_UNAVAILABLE")
    rule = _operator(contracts, operator_id)["rule"]
    if body in rule.get("kruraBodies", []):
        base = "KRURA"
        if motion_value == "RETROGRADE":
            base = "MAHAKRURA"
    elif body in rule.get("saumyaBodies", []):
        base = "SAUMYA"
        if motion_value == "RETROGRADE":
            base = "MAHASHUBHA"
    else:
        return _unknown(event, contracts, component_id, operator_id, "UNKNOWN")
    return _make_row(event, contracts, component_id, operator_id, "VALUE", source_value=base)


def _natural_relationship(
    contracts: FrozenContracts,
    operator_id: str,
    source_body: str,
    target_body: str,
) -> str | None:
    operator = _operator(contracts, operator_id)
    matrix = operator["rule"]["friendshipMatrix"]
    if source_body not in matrix or target_body not in matrix or source_body == target_body:
        return None
    cell = matrix[source_body]
    if target_body in cell.get("friends", []):
        return "FRIEND"
    if target_body in cell.get("enemies", []):
        return "ENEMY"
    if target_body in cell.get("neutral", []):
        return "NEUTRAL"
    return None


def _relationship_row(event: SyntheticEvent, contracts: FrozenContracts) -> dict[str, Any]:
    component_id = "C02_NATURAL_RELATIONSHIP"
    operator_id = "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1"
    source = event.event_roles["sourceBody"]
    target = event.event_roles["targetBody"]
    if source in {"RAHU", "KETU"} or target in {"RAHU", "KETU"}:
        return _unknown(event, contracts, component_id, operator_id, "RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_TRAILOKYA")
    value = _natural_relationship(contracts, operator_id, source, target)
    if value is None:
        return _unknown(event, contracts, component_id, operator_id, "UNKNOWN")
    return _make_row(event, contracts, component_id, operator_id, "VALUE", source_value=value)


def _temporary_value(contracts: FrozenContracts, source_sign: int, target_sign: int) -> tuple[int, str]:
    place = _relative_place(source_sign, target_sign)
    rule = _operator(contracts, "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1")["rule"]
    if place in rule["temporaryFriendPositions"]:
        return place, "TEMPORARY_FRIEND"
    if place in rule["temporaryEnemyPositions"]:
        return place, "TEMPORARY_ENEMY"
    raise ValueError(f"frozen temporary relation has no place {place}")


def _temporary_row(event: SyntheticEvent, contracts: FrozenContracts) -> dict[str, Any]:
    component_id = "C03_TEMPORARY_RELATIONSHIP"
    operator_id = "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1"
    place, value = _temporary_value(
        contracts,
        event.transit_position["signIndex"],
        event.natal_target_position["signIndex"],
    )
    return _make_row(event, contracts, component_id, operator_id, "VALUE", source_value=value)


def _saravali_relationship(contracts: FrozenContracts, source: str, target: str) -> str | None:
    return _natural_relationship(contracts, "SARAVALI_NATURAL_RELATIONSHIP_V1", source, target)


def _compound_row(event: SyntheticEvent, contracts: FrozenContracts) -> dict[str, Any]:
    component_id = "C04_COMPOUND_RELATIONSHIP"
    operator_id = "BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1"
    source = event.event_roles["sourceBody"]
    target = event.event_roles["targetBody"]
    natural = _saravali_relationship(contracts, source, target)
    if natural is None:
        return _unknown(event, contracts, component_id, operator_id, "COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED")
    _, temporary = _temporary_value(
        contracts,
        event.transit_position["signIndex"],
        event.natal_target_position["signIndex"],
    )
    compound_map = _operator(contracts, operator_id)["rule"]["compoundRelationshipMap"]
    value = compound_map.get(f"{natural}:{temporary}")
    if value is None:
        return _unknown(event, contracts, component_id, operator_id, "COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED")
    return _make_row(event, contracts, component_id, operator_id, "VALUE", source_value=value)


def _ordinary_drsti_row(event: SyntheticEvent, contracts: FrozenContracts) -> dict[str, Any]:
    component_id = "C05_ORDINARY_AND_SPECIAL_DRSTI"
    operator_id = "SARAVALI_4_32_ORDINARY_DRSTI_V1"
    place = _relative_place(
        event.transit_position["signIndex"],
        event.natal_target_position["signIndex"],
    )
    fractions = _operator(contracts, operator_id)["rule"]["ordinaryAspectFractions"]
    value = fractions.get(str(place), "NO_STATED_ORDINARY_FRACTION")
    return _make_row(event, contracts, component_id, operator_id, "VALUE", source_value=value)


def _special_drsti_row(event: SyntheticEvent, contracts: FrozenContracts) -> dict[str, Any]:
    component_id = "C05_ORDINARY_AND_SPECIAL_DRSTI"
    operator_id = "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1"
    source = event.event_roles["sourceBody"]
    place = _relative_place(
        event.transit_position["signIndex"],
        event.natal_target_position["signIndex"],
    )
    places = _operator(contracts, operator_id)["rule"]["specialFullAspectPlaces"]
    value = "SPECIAL_FULL_DRSTI" if place in places.get(source, []) else "NO_SPECIAL_FULL_OVERRIDE"
    return _make_row(event, contracts, component_id, operator_id, "VALUE", source_value=value)


def _outer_motion_value(rule: Mapping[str, Any], place: int) -> str | None:
    cases = rule.get("outerPlanetRelativeSun", {})
    for key, value in cases.items():
        if key.isdigit() and int(key) == place:
            return value
        if "-" in key:
            start, end = key.split("-", 1)
            if start.isdigit() and end.isdigit() and int(start) <= place <= int(end):
                return value
    return None


def _inner_motion_value(rule: Mapping[str, Any], place: int) -> str | None:
    cases = rule.get("innerPlanetRelativeSun", {})
    for key, value in cases.items():
        if key.isdigit() and int(key) == place:
            return value
        if "_OR_" in key:
            choices = [part for part in key.split("_OR_") if part.isdigit()]
            if place in {int(choice) for choice in choices}:
                return value
    return None


def _motion_row(event: SyntheticEvent, contracts: FrozenContracts) -> tuple[dict[str, Any], str | None]:
    component_id = "C06_STHULA_MOTION"
    operator_id = "TRAILOKYA_1972_STHULA_MOTION_CLASS_V1"
    body = event.event_roles["sourceBody"]
    rule = _operator(contracts, operator_id)["rule"]
    place = _relative_place(
        event.transit_position["signIndex"],
        event.sun_position["signIndex"],
    )
    if body in rule.get("outerPlanetBodies", []):
        if place == 1:
            return _unknown(event, contracts, component_id, operator_id, "ASTA_DIRECTION_UNKNOWN"), None
        value = _outer_motion_value(rule, place)
    elif body in rule.get("innerPlanetBodies", []):
        value = _inner_motion_value(rule, place)
    else:
        value = None
    if value is None:
        return _unknown(
            event,
            contracts,
            component_id,
            operator_id,
            "MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED",
        ), None
    return _make_row(event, contracts, component_id, operator_id, "VALUE", source_value=value), value


def _individual_record_row(event: SyntheticEvent, contracts: FrozenContracts) -> dict[str, Any]:
    component_id = "C07_INDIVIDUAL_SOURCE_RECORDS_NO_STACKING"
    operator_id = "TRAILOKYA_1972_V166_INDIVIDUAL_MODIFIER_V1"
    return _unknown(event, contracts, component_id, operator_id, "UNKNOWN")


def evaluate_synthetic_event(
    event: Mapping[str, Any] | SyntheticEvent,
    contracts: FrozenContracts | None = None,
) -> list[dict[str, Any]]:
    """Evaluate exactly one synthetic event into the eight frozen row templates."""

    validated_event = event if isinstance(event, SyntheticEvent) else SyntheticEvent.from_mapping(event)
    frozen = contracts or load_frozen_contracts()
    motion_row, motion_value = _motion_row(validated_event, frozen)
    rows = [
        _natural_class(validated_event, frozen, motion_value),
        _relationship_row(validated_event, frozen),
        _temporary_row(validated_event, frozen),
        _compound_row(validated_event, frozen),
        _ordinary_drsti_row(validated_event, frozen),
        _special_drsti_row(validated_event, frozen),
        motion_row,
        _individual_record_row(validated_event, frozen),
    ]
    validate_output_rows(rows, frozen)
    return rows


def evaluate_real_population(*_args: Any, **_kwargs: Any) -> None:
    """Explicitly block any real Candidate C population execution."""

    raise RealCandidateCExecutionBlocked(
        "Evaluator B1 is synthetic-only; real Candidate C population execution is not authorized"
    )


def validate_output_rows(rows: list[Mapping[str, Any]], contracts: FrozenContracts | None = None) -> None:
    """Validate one complete synthetic event batch against the frozen schema."""

    frozen = contracts or load_frozen_contracts()
    if not isinstance(rows, list) or len(rows) != frozen.row_templates_per_event:
        raise ValueError(f"a complete event must contain exactly {frozen.row_templates_per_event} rows")
    seen: set[tuple[Any, ...]] = set()
    component_counts: Counter[str] = Counter()
    event_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("output row must be an object")
        keys = set(row)
        if not keys.issubset(_OUTPUT_FIELDS):
            raise ValueError(f"output contains fields outside the frozen schema: {sorted(keys - _OUTPUT_FIELDS)}")
        required = _OUTPUT_FIELDS - {"sourceValue", "unknownReasonCode"}
        if not required.issubset(keys):
            raise ValueError("output row is missing a required frozen-schema field")
        if row["sourceProfile"] not in _SOURCE_PROFILES:
            raise ValueError("output source profile is not frozen")
        component_id = row["componentId"]
        if component_id not in frozen.component_specs:
            raise ValueError("output component is not admitted")
        component = frozen.component_specs[component_id]
        if row["sourceProfile"] != component["sourceProfile"]:
            raise ValueError("component/profile isolation was violated")
        operator_id = row["provenance"].get("operatorId") if isinstance(row["provenance"], Mapping) else None
        if operator_id not in component.get("operatorIds", []):
            raise ValueError("row operator is not bound to its component")
        if row["sourceContractId"] != operator_id:
            raise ValueError("row source contract and operator identity differ")
        if row["inputIdentityHash"] != sha256_bytes(canonical_json_bytes(row["inputIdentity"])):
            raise ValueError("input identity hash does not validate")
        if row["outputStatus"] not in {"VALUE", "UNKNOWN"}:
            raise ValueError("output status is outside the frozen enum")
        if row["outputStatus"] == "VALUE":
            if "sourceValue" not in row or "unknownReasonCode" in row:
                raise ValueError("VALUE row has invalid value/unknown fields")
        else:
            if "unknownReasonCode" not in row or "sourceValue" in row:
                raise ValueError("UNKNOWN row has invalid value/unknown fields")
            if row["unknownReasonCode"] not in frozen.unknown_reason_codes:
                raise ValueError("UNKNOWN reason is outside the frozen taxonomy")
        event_ids.add(row["eventId"])
        component_counts[component_id] += 1
        key = _row_key(row)
        if key in seen:
            raise ValueError("duplicate frozen row key")
        seen.add(key)
    if len(event_ids) != 1:
        raise ValueError("a complete synthetic batch must contain one event identity")
    expected_components = {
        "C01_NATURAL_PLANET_CLASS": 1,
        "C02_NATURAL_RELATIONSHIP": 1,
        "C03_TEMPORARY_RELATIONSHIP": 1,
        "C04_COMPOUND_RELATIONSHIP": 1,
        "C05_ORDINARY_AND_SPECIAL_DRSTI": 2,
        "C06_STHULA_MOTION": 1,
        "C07_INDIVIDUAL_SOURCE_RECORDS_NO_STACKING": 1,
    }
    if component_counts != expected_components:
        raise ValueError(f"row template counts differ from frozen contract: {component_counts}")


class EvaluatorB:
    """Object wrapper exposing only synthetic evaluation and a blocked population path."""

    def __init__(self, contracts: FrozenContracts | None = None) -> None:
        self.contracts = contracts or load_frozen_contracts()

    def evaluate_event(self, event: Mapping[str, Any] | SyntheticEvent) -> list[dict[str, Any]]:
        return evaluate_synthetic_event(event, self.contracts)

    def evaluate_population(self, *_args: Any, **_kwargs: Any) -> None:
        evaluate_real_population()
