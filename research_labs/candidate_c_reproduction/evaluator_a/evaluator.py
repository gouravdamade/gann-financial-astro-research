"""Clean-room Evaluator A for the preregistered Candidate C contracts.

Only synthetic marked events may reach the evaluation functions in this
milestone.  The frozen population entry point is an unconditional guard so
that implementation validation cannot accidentally become a Candidate C run.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .canonical import canonical_hash
from .contract_loader import FrozenContracts, load_frozen_contracts
from .schema import validate_rows


REAL_CANDIDATE_C_EXECUTION_ALLOWED = False

EVENT_BODIES = frozenset({"SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"})
RELATIONSHIP_BODIES = frozenset({"SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"})
SIGN_NAMES = {
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


class EvaluatorAError(ValueError):
    """Raised when a synthetic input or source contract is not admissible."""


class RealCandidateCExecutionBlocked(EvaluatorAError):
    """Raised for every attempt to evaluate the real frozen population."""


def _operator(contracts: FrozenContracts, operator_id: str) -> Mapping[str, Any]:
    try:
        return contracts.operators[operator_id]
    except KeyError as exc:
        raise EvaluatorAError(f"validated contracts do not contain {operator_id}") from exc


def _position(event: Mapping[str, Any], field: str, expected_body: str | None = None) -> Mapping[str, Any]:
    value = event.get(field)
    if not isinstance(value, Mapping):
        raise EvaluatorAError(f"{field} must be a position object")
    body = value.get("body")
    sign = value.get("sign")
    sign_index = value.get("signIndex")
    speed = value.get("siderealLongitudeSpeedDegPerDay")
    if not isinstance(body, str) or body not in EVENT_BODIES:
        raise EvaluatorAError(f"{field}.body is not an admitted body")
    if expected_body is not None and body != expected_body:
        raise EvaluatorAError(f"{field}.body is not {expected_body}")
    if not isinstance(sign, str) or not isinstance(sign_index, int) or SIGN_NAMES.get(sign_index) != sign:
        raise EvaluatorAError(f"{field} has inconsistent sign identity")
    if not isinstance(speed, (int, float)) or isinstance(speed, bool):
        raise EvaluatorAError(f"{field} has no numeric frozen speed input")
    return value


def _validate_event(event: Mapping[str, Any]) -> dict[str, Any]:
    if event.get("_evaluatorInputKind") != "SYNTHETIC_ONLY":
        raise RealCandidateCExecutionBlocked("only explicitly synthetic inputs are admitted before the central run authorization")
    if not isinstance(event.get("eventId"), str) or not event["eventId"]:
        raise EvaluatorAError("eventId must be a non-empty string")
    if not isinstance(event.get("eventHash"), str) or not event["eventHash"]:
        raise EvaluatorAError("eventHash must be a non-empty string")
    roles = event.get("eventRoles")
    if not isinstance(roles, Mapping):
        raise EvaluatorAError("eventRoles are required")
    source = roles.get("sourceBody")
    target = roles.get("targetBody")
    if source not in EVENT_BODIES or target not in EVENT_BODIES:
        raise EvaluatorAError("event roles contain an unsupported body")
    if roles.get("sourceRole") != "TRANSIT_BODY" or roles.get("targetRole") != "NATAL_TARGET":
        raise EvaluatorAError("event roles do not match the frozen source/target contract")
    transit = _position(event, "transitPositionAtExactUtc", source)
    natal = _position(event, "natalTargetPositionAtFrozenChartUtc", target)
    sun = _position(event, "sunPositionAtExactUtc", "SUN")
    moon = _position(event, "moonPositionAtExactUtc", "MOON")
    planetary = event.get("planetaryPositionsAtExactUtc")
    if not isinstance(planetary, Sequence) or isinstance(planetary, (str, bytes)) or len(planetary) != len(EVENT_BODIES):
        raise EvaluatorAError("planetaryPositionsAtExactUtc must contain the frozen nine-body set")
    planetary_bodies: set[str] = set()
    for item in planetary:
        if not isinstance(item, Mapping):
            raise EvaluatorAError("planetaryPositionsAtExactUtc contains a non-object")
        body = item.get("body")
        if body in planetary_bodies:
            raise EvaluatorAError("planetaryPositionsAtExactUtc contains duplicate bodies")
        _position({"position": item}, "position", body if isinstance(body, str) else None)
        planetary_bodies.add(body)
    if planetary_bodies != set(EVENT_BODIES):
        raise EvaluatorAError("planetaryPositionsAtExactUtc does not contain exactly the frozen body set")
    return {
        "event": event,
        "sourceBody": source,
        "targetBody": target,
        "transit": transit,
        "natal": natal,
        "sun": sun,
        "moon": moon,
    }


def _relative_place(source_sign_index: int, target_sign_index: int) -> int:
    if type(source_sign_index) is not int or type(target_sign_index) is not int:
        raise EvaluatorAError("sign indexes must be integers")
    if source_sign_index not in SIGN_NAMES or target_sign_index not in SIGN_NAMES:
        raise EvaluatorAError("sign index is outside the twelve-sign contract")
    return ((target_sign_index - source_sign_index) % 12) + 1


def _provenance(
    contracts: FrozenContracts,
    profile: str,
    operator_id: str,
    *,
    dependencies: Sequence[str] = (),
    supporting: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    operator = _operator(contracts, operator_id)
    artifact = contracts.operator_artifacts[operator_id]
    merged_dependencies = list(dict.fromkeys([*operator.get("unresolvedDependencies", []), *dependencies]))
    provenance: dict[str, Any] = {
        "sourceProfile": profile,
        "sourceProfileContractHash": contracts.profile_contract_hashes[profile],
        "sourceContractId": operator_id,
        "operatorId": operator_id,
        "operatorVersion": str(operator["operatorVersion"]),
        "sourceStatus": str(operator["sourceStatus"]),
        "sourceArtifact": dict(artifact),
        "sourceLocators": [dict(locator) for locator in operator.get("sourceLocators", [])],
        "operatorDependencies": merged_dependencies,
    }
    if supporting is not None:
        provenance["supportingInputContract"] = dict(supporting)
    return provenance


def _row(
    context: Mapping[str, Any],
    contracts: FrozenContracts,
    *,
    profile: str,
    component_id: str,
    operator_id: str,
    consumed_inputs: Mapping[str, Any],
    source_value: Any = None,
    unknown_reason: str | None = None,
    dependencies: Sequence[str] = (),
    supporting: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if (source_value is None) == (unknown_reason is None):
        raise EvaluatorAError("a row must have exactly one of source_value or unknown_reason")
    event = context["event"]
    input_identity = {
        "eventId": event["eventId"],
        "eventHash": event["eventHash"],
        "sourceProfile": profile,
        "componentId": component_id,
        "sourceContractId": operator_id,
        "consumedInputs": dict(consumed_inputs),
    }
    row: dict[str, Any] = {
        "eventId": event["eventId"],
        "sourceProfile": profile,
        "componentId": component_id,
        "sourceContractId": operator_id,
        "inputIdentity": input_identity,
        "inputIdentityHash": canonical_hash(input_identity),
        "outputStatus": "VALUE" if unknown_reason is None else "UNKNOWN",
    }
    if unknown_reason is None:
        row["sourceValue"] = source_value
    else:
        row["unknownReasonCode"] = unknown_reason
    row["provenance"] = _provenance(
        contracts,
        profile,
        operator_id,
        dependencies=dependencies,
        supporting=supporting,
    )
    return row


def _natural_relationship(
    contracts: FrozenContracts,
    operator_id: str,
    source_body: str,
    target_body: str,
) -> tuple[str | None, str | None, tuple[str, ...]]:
    operator = _operator(contracts, operator_id)
    if source_body not in RELATIONSHIP_BODIES or target_body not in RELATIONSHIP_BODIES:
        return None, "RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_TRAILOKYA" if operator_id.startswith("TRAILOKYA") else "RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_SARAVALI", ()
    if source_body == target_body:
        reason = "TRAILOKYA_RELATIONSHIP_CELL_NOT_SOURCE_CLOSED" if operator_id.startswith("TRAILOKYA") else "SARAVALI_SELF_RELATIONSHIP_NOT_STATED"
        if operator_id.startswith("TRAILOKYA"):
            return None, "UNKNOWN", (reason,)
        return None, reason, (reason,)
    matrix = operator.get("rule", {}).get("friendshipMatrix", {})
    row = matrix.get(source_body)
    if not isinstance(row, Mapping):
        return None, "RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_TRAILOKYA" if operator_id.startswith("TRAILOKYA") else "RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_SARAVALI", ()
    for state, category in (("FRIEND", "friends"), ("NEUTRAL", "neutral"), ("ENEMY", "enemies")):
        if target_body in row.get(category, []):
            return state, None, ()
    return None, "UNKNOWN", ()


def _temporary_relationship(contracts: FrozenContracts, source_sign: Mapping[str, Any], target_sign: Mapping[str, Any]) -> tuple[str, int]:
    operator = _operator(contracts, "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1")
    place = _relative_place(source_sign["signIndex"], target_sign["signIndex"])
    friendly = operator["rule"]["temporaryFriendPositions"]
    return ("TEMPORARY_FRIEND" if place in friendly else "TEMPORARY_ENEMY"), place


def _motion_class(context: Mapping[str, Any], contracts: FrozenContracts) -> tuple[str | None, str | None, int]:
    operator = _operator(contracts, "TRAILOKYA_1972_STHULA_MOTION_CLASS_V1")
    body = context["sourceBody"]
    relative_sun_place = _relative_place(context["transit"]["signIndex"], context["sun"]["signIndex"])
    rule = operator["rule"]
    if body in rule["outerPlanetBodies"]:
        if relative_sun_place == 1:
            return None, "ASTA_DIRECTION_UNKNOWN", relative_sun_place
        state = rule["outerPlanetRelativeSun"].get(str(relative_sun_place))
    elif body in rule["innerPlanetBodies"]:
        state = rule["innerPlanetRelativeSun"].get(str(relative_sun_place))
    else:
        state = None
    if state is None:
        return None, "MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED", relative_sun_place
    return str(state), None, relative_sun_place


def _nature_value(context: Mapping[str, Any], contracts: FrozenContracts) -> tuple[str | None, str | None, str | None]:
    body = context["sourceBody"]
    if body == "MOON":
        return None, "MOON_CONDITION_INPUT_UNAVAILABLE", None
    if body == "MERCURY":
        return None, "MERCURY_ASSOCIATION_INPUT_UNAVAILABLE", None
    motion, _motion_reason, _relative_sun_place = _motion_class(context, contracts)
    operator = _operator(contracts, "TRAILOKYA_1972_NATURAL_PLANET_CLASS_V1")
    rule = operator["rule"]
    if body in rule["kruraBodies"]:
        base = "KRURA"
    elif body in rule["saumyaBodies"]:
        base = "SAUMYA"
    else:
        return None, "UNKNOWN", motion
    if motion == "RETROGRADE":
        return ("MAHAKRURA" if base == "KRURA" else "MAHASHUBHA"), None, motion
    if motion in {"SWIFT", "SHIGHRA", "ATICARA"}:
        return base, None, motion
    return base, None, motion


def _evaluate_template(context: Mapping[str, Any], contracts: FrozenContracts, profile: str, component_id: str, operator_id: str) -> dict[str, Any]:
    source = context["sourceBody"]
    target = context["targetBody"]
    transit = context["transit"]
    natal = context["natal"]
    if component_id == "C01_NATURAL_PLANET_CLASS":
        value, reason, motion = _nature_value(context, contracts)
        consumed = {"sourceBody": source, "motionState": motion}
        return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, source_value=value, unknown_reason=reason)
    if component_id == "C02_NATURAL_RELATIONSHIP":
        value, reason, dependencies = _natural_relationship(contracts, operator_id, source, target)
        dependency_list = list(dependencies)
        if reason == "UNKNOWN":
            dependency_list.append("TRAILOKYA_RELATIONSHIP_CELL_NOT_SOURCE_CLOSED")
            reason = "UNKNOWN"
        consumed = {"sourceBody": source, "targetBody": target}
        return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, source_value=value, unknown_reason=reason, dependencies=dependency_list)
    if component_id == "C03_TEMPORARY_RELATIONSHIP":
        value, place = _temporary_relationship(contracts, transit, natal)
        consumed = {"sourceSign": transit["sign"], "targetSign": natal["sign"], "relativePlace": place}
        return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, source_value=value)
    if component_id == "C04_COMPOUND_RELATIONSHIP":
        natural, natural_reason, natural_dependencies = _natural_relationship(contracts, "SARAVALI_NATURAL_RELATIONSHIP_V1", source, target)
        temporary, place = _temporary_relationship(contracts, transit, natal)
        consumed = {
            "sourceBody": source,
            "targetBody": target,
            "sourceSign": transit["sign"],
            "targetSign": natal["sign"],
            "relativePlace": place,
            "naturalRelationship": natural,
            "temporaryRelationship": temporary,
        }
        supporting = contracts.operator_artifacts["SARAVALI_NATURAL_RELATIONSHIP_V1"] | {
            "operatorId": "SARAVALI_NATURAL_RELATIONSHIP_V1",
            "contractId": "MO_R4A_S2R1_R1_SARAVALI_ADJUDICATED_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1",
        }
        if natural is None:
            dependencies = ["COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED", *natural_dependencies]
            if natural_reason and not natural_dependencies:
                dependencies.append(natural_reason)
            return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, unknown_reason="COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED", dependencies=dependencies, supporting=supporting)
        compound_map = _operator(contracts, operator_id)["rule"]["compoundRelationshipMap"]
        state = compound_map.get(f"{natural}:{temporary}")
        if state is None:
            return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, unknown_reason="COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED", supporting=supporting)
        return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, source_value=str(state), supporting=supporting)
    if component_id == "C05_ORDINARY_AND_SPECIAL_DRSTI":
        place = _relative_place(transit["signIndex"], natal["signIndex"])
        consumed = {"sourceBody": source, "sourceSign": transit["sign"], "targetSign": natal["sign"], "relativePlace": place}
        if operator_id == "SARAVALI_4_32_ORDINARY_DRSTI_V1":
            fraction = _operator(contracts, operator_id)["rule"]["ordinaryAspectFractions"].get(str(place))
            value = f"DRSTI_{fraction.replace('/', '_')}" if fraction is not None else "NO_STATED_ORDINARY_FRACTION"
            return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, source_value=value)
        full_places = _operator(contracts, operator_id)["rule"]["specialFullAspectPlaces"].get(source, [])
        value = "SPECIAL_FULL_DRSTI" if place in full_places else "NO_SPECIAL_FULL_OVERRIDE"
        consumed["sourceBody"] = source
        return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, source_value=value)
    if component_id == "C06_STHULA_MOTION":
        value, reason, relative_sun_place = _motion_class(context, contracts)
        consumed = {
            "sourceBody": source,
            "sourceSign": transit["sign"],
            "sunSign": context["sun"]["sign"],
            "relativeSunPlace": relative_sun_place,
            "siderealLongitudeSpeedDegPerDay": transit["siderealLongitudeSpeedDegPerDay"],
        }
        return _row(context, contracts, profile=profile, component_id=component_id, operator_id=operator_id, consumed_inputs=consumed, source_value=value, unknown_reason=reason)
    if component_id == "C07_INDIVIDUAL_SOURCE_RECORDS_NO_STACKING":
        consumed = {"sourceMeasurement": None, "modifiers": []}
        return _row(
            context,
            contracts,
            profile=profile,
            component_id=component_id,
            operator_id=operator_id,
            consumed_inputs=consumed,
            unknown_reason="UNKNOWN",
            dependencies=("TRAILOKYA_V166_REQUIRES_STHANA_PHALA_INPUT",),
        )
    raise EvaluatorAError(f"unsupported frozen component: {component_id}")


def _templates(contracts: FrozenContracts) -> list[tuple[str, str, str]]:
    templates: list[tuple[str, str, str]] = []
    for binding in contracts.bindings["componentInputBindings"]:
        profile = str(binding["sourceProfile"])
        component_id = str(binding["componentId"])
        for operator_id in binding["operatorIds"]:
            templates.append((profile, component_id, str(operator_id)))
    if len(templates) != 8:
        raise EvaluatorAError(f"frozen template count changed: {len(templates)}")
    return templates


def row_keys_for_event(event_id: str, contracts: FrozenContracts) -> list[dict[str, Any]]:
    if not isinstance(event_id, str) or not event_id:
        raise EvaluatorAError("event ID is required to build row keys")
    return [
        {
            "eventId": event_id,
            "sourceProfile": profile,
            "componentId": component_id,
            "sourceContractId": operator_id,
            "operatorId": operator_id,
        }
        for profile, component_id, operator_id in _templates(contracts)
    ]


def evaluate_synthetic_event(event: Mapping[str, Any], contracts: FrozenContracts | None = None) -> list[dict[str, Any]]:
    """Evaluate one explicitly marked synthetic event for implementation tests."""

    frozen = contracts or load_frozen_contracts()
    context = _validate_event(event)
    rows = [
        _evaluate_template(context, frozen, profile, component_id, operator_id)
        for profile, component_id, operator_id in _templates(frozen)
    ]
    validate_rows(rows, row_keys_for_event(str(event["eventId"]), frozen), frozen.allowed_unknown_codes)
    return rows


def validate_population_rows(rows: Sequence[Mapping[str, Any]], contracts: FrozenContracts | None = None) -> None:
    """Validate a future full output without creating or reading one here."""

    frozen = contracts or load_frozen_contracts()
    validate_rows(rows, frozen.expected_row_keys, frozen.allowed_unknown_codes)


def evaluate_frozen_population(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    """The real Candidate C run remains centrally unauthorized."""

    raise RealCandidateCExecutionBlocked(
        "REAL_CANDIDATE_C_EXECUTION_ALLOWED=false; the frozen 645-event population cannot be evaluated in A1"
    )


def evaluate_frozen_snapshot(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return evaluate_frozen_population(*args, **kwargs)
