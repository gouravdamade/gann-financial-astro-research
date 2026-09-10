"""Fail-closed classical source operators for the MO-R4A-S1 audit.

This module is a source-contract evaluator, not an astrology-to-market
interpreter. It reads versioned source contracts and binds them to frozen
April 2025 event identities without regenerating those events.

It never reads price, outcomes, a durable Founder Review store, founder
decisions, SBC, the polarity catalogue, or the unsigned multi-oscillator
runtime. Real-event reports always leave currency direction and market
magnitude unknown.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from financial_astro_ephemeris import configure_ephemeris

from chart_conditioned_aspects.founder_chart_registry import load_founder_chart_identity_records
from chart_conditioned_aspects.transits.chart_conditioned_event_compiler import (
    _calculate_sidereal_geocentric_longitude,
)

import machine_assisted_interpretation as machine_interpretation


CLASSICAL_SOURCE_OPERATOR_LEDGER_CONTRACT = "MO_R4A_S1_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1"
CLASSICAL_SOURCE_OPERATOR_OUTPUT_CONTRACT = "MO_R4A_S1_CLASSICAL_SOURCE_OPERATOR_OUTPUT_V1"
CLASSICAL_SOURCE_OPERATOR_COVERAGE_CONTRACT = "MO_R4A_S1_REAL_24_SOURCE_OPERATOR_COVERAGE_V1"
CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION = 1
EXPLORATORY_UNSIGNED_MODE = "EXPLORATORY_UNSIGNED"
UNKNOWN_CURRENCY_DIRECTION = "UNKNOWN_MORE_EVIDENCE_REQUIRED"
NO_MARKET_BRIDGE = "NO_AUTHORIZED_MARKET_BRIDGE"
MAGNITUDE_NOT_CONFIGURED = "MAGNITUDE_NOT_CONFIGURED"
NO_COMPOSITION_CONTRACT = "NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_OPERATOR_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "source_operators"
DEFAULT_LEDGER_PATH = SOURCE_OPERATOR_ROOT / "classical_source_operator_ledger_v1.json"
DEFAULT_UNRESOLVED_PATH = SOURCE_OPERATOR_ROOT / "source_operator_unresolved_dependencies_v1.json"
DEFAULT_CROSS_TEXT_PATH = SOURCE_OPERATOR_ROOT / "source_operator_cross_text_matrix_v1.json"

SIGNS = (
    "ARIES",
    "TAURUS",
    "GEMINI",
    "CANCER",
    "LEO",
    "VIRGO",
    "LIBRA",
    "SCORPIO",
    "SAGITTARIUS",
    "CAPRICORN",
    "AQUARIUS",
    "PISCES",
)
SIGN_INDEX = {sign: index for index, sign in enumerate(SIGNS)}
CLASSICAL_BODIES = frozenset({"SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"})
RELATIONSHIP_BODIES = frozenset({"SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"})

SOURCE_STATUSES = frozenset(
    {
        "SOURCE_CLOSED_EXECUTABLE",
        "SOURCE_CLOSED_CATEGORICAL",
        "SOURCE_CLOSED_DESCRIPTIVE_ONLY",
        "SOURCE_PARTIAL",
        "SOURCE_UNRESOLVED",
        "SOURCE_SILENT",
        "TRANSLATION_EDITORIAL_MISMATCH",
        "COMMENTARY_ONLY",
        "CROSS_TEXT_AGREEMENT",
        "CROSS_TEXT_CONFLICT",
    }
)

REQUIRED_LEDGER_FIELDS = frozenset(
    {
        "operatorId",
        "operatorVersion",
        "sourceFamily",
        "sourceWork",
        "author",
        "witnessId",
        "witnessRole",
        "edition",
        "rootOrCommentary",
        "chapter",
        "verseOrLocator",
        "originalTerm",
        "originalTextOrBoundedExcerptReference",
        "translationOrLiteralSense",
        "directSourceClaim",
        "conditions",
        "exceptions",
        "scope",
        "inputFields",
        "outputFields",
        "operatorType",
        "sourceStatus",
        "machineEvaluable",
        "requiresExternalAstronomy",
        "unresolvedDependencies",
        "knownTranslationIssues",
        "crossTextSupport",
        "crossTextConflict",
        "marketDirectionAuthorized",
        "marketMagnitudeAuthorized",
        "modeOneEligible",
        "prohibitedInterpretations",
    }
)


class ClassicalSourceOperatorError(ValueError):
    """Raised when a source contract or a source-operator input is invalid."""


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ClassicalSourceOperatorError(f"Missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ClassicalSourceOperatorError(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(raw, dict):
        raise ClassicalSourceOperatorError(f"{label} must be a JSON object: {path}")
    return raw


def _string(value: Any, label: str) -> str:
    result = str(value or "").strip().upper()
    if not result:
        raise ClassicalSourceOperatorError(f"{label} is required")
    return result


def _sign(value: Any, label: str) -> str:
    result = _string(value, label)
    if result not in SIGN_INDEX:
        raise ClassicalSourceOperatorError(f"Unsupported {label}: {value!r}")
    return result


def _body(value: Any, label: str) -> str:
    result = _string(value, label)
    if result not in CLASSICAL_BODIES:
        raise ClassicalSourceOperatorError(f"Unsupported {label}: {value!r}")
    return result


def _parse_utc(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ClassicalSourceOperatorError(f"{label} must be explicit ISO UTC") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ClassicalSourceOperatorError(f"{label} must be explicit ISO UTC")
    return parsed.astimezone(timezone.utc)


def _source_locator(operator: Mapping[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "sourceId": str(operator["witnessId"]),
            "edition": str(operator["edition"]),
            "locator": str(operator["verseOrLocator"]),
            "rootOrCommentary": str(operator["rootOrCommentary"]),
        }
    ]


def _unresolved_output(
    operator: Mapping[str, Any],
    *,
    input_snapshot: Mapping[str, Any],
    output_state: str,
    dependencies: Sequence[str],
    explanation: str,
    conditions_missing: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "contract": CLASSICAL_SOURCE_OPERATOR_OUTPUT_CONTRACT,
        "operatorId": operator["operatorId"],
        "operatorVersion": operator["operatorVersion"],
        "sourceFamily": operator["sourceFamily"],
        "status": "SOURCE_UNRESOLVED",
        "inputSnapshot": dict(input_snapshot),
        "outputState": output_state,
        "sourceMeasurement": None,
        "sourceLocators": _source_locator(operator),
        "conditionsSatisfied": [],
        "conditionsMissing": list(conditions_missing),
        "unresolvedDependencies": list(dict.fromkeys(dependencies)),
        "machineEvaluated": False,
        "marketDirectionAuthorized": False,
        "marketMagnitudeAuthorized": False,
        "modeOneEligible": False,
        "explanation": explanation,
    }


def _source_output(
    operator: Mapping[str, Any],
    *,
    input_snapshot: Mapping[str, Any],
    output_state: str,
    explanation: str,
    source_measurement: Mapping[str, Any] | None = None,
    conditions_satisfied: Sequence[str] = (),
    conditions_missing: Sequence[str] = (),
    unresolved_dependencies: Sequence[str] = (),
    status: str | None = None,
) -> dict[str, Any]:
    result_status = status or str(operator["sourceStatus"])
    if result_status not in SOURCE_STATUSES:
        raise ClassicalSourceOperatorError(f"Unsupported operator result status: {result_status}")
    return {
        "contract": CLASSICAL_SOURCE_OPERATOR_OUTPUT_CONTRACT,
        "operatorId": operator["operatorId"],
        "operatorVersion": operator["operatorVersion"],
        "sourceFamily": operator["sourceFamily"],
        "status": result_status,
        "inputSnapshot": dict(input_snapshot),
        "outputState": output_state,
        "sourceMeasurement": dict(source_measurement) if source_measurement else None,
        "sourceLocators": _source_locator(operator),
        "conditionsSatisfied": list(conditions_satisfied),
        "conditionsMissing": list(conditions_missing),
        "unresolvedDependencies": list(dict.fromkeys(unresolved_dependencies)),
        "machineEvaluated": result_status.startswith("SOURCE_CLOSED"),
        "marketDirectionAuthorized": False,
        "marketMagnitudeAuthorized": False,
        "modeOneEligible": bool(operator["modeOneEligible"]) and not unresolved_dependencies,
        "explanation": explanation,
    }


def _measurement(
    *,
    measurement_type: str,
    value: str,
    source_scope: str,
    operator: Mapping[str, Any],
    factor: str | None = None,
) -> dict[str, Any]:
    return {
        "measurementType": measurement_type,
        "value": value,
        "sourceScope": source_scope,
        "sourceOperatorId": operator["operatorId"],
        "sourceLocator": str(operator["verseOrLocator"]),
        "sourceModifierFactor": factor,
        "signedUnit": None,
        "oscillatorMagnitude": None,
        "forecastProbability": None,
        "priceChangeEstimate": None,
    }


def validate_source_operator_ledger(ledger: Mapping[str, Any]) -> None:
    if ledger.get("contract") != CLASSICAL_SOURCE_OPERATOR_LEDGER_CONTRACT:
        raise ClassicalSourceOperatorError("Unsupported classical source operator ledger contract")
    if ledger.get("schemaVersion") != CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION:
        raise ClassicalSourceOperatorError("Unsupported classical source operator ledger version")
    operators = ledger.get("operators")
    if not isinstance(operators, list) or not operators:
        raise ClassicalSourceOperatorError("Source operator ledger must contain operators")
    seen: set[tuple[str, str]] = set()
    for operator in operators:
        if not isinstance(operator, dict):
            raise ClassicalSourceOperatorError("Source operator must be an object")
        missing = REQUIRED_LEDGER_FIELDS - set(operator)
        if missing:
            raise ClassicalSourceOperatorError(
                f"Source operator {operator.get('operatorId')!r} is missing fields: {sorted(missing)}"
            )
        identity = (str(operator["operatorId"]), str(operator["operatorVersion"]))
        if identity in seen:
            raise ClassicalSourceOperatorError(f"Duplicate source operator identity: {identity}")
        seen.add(identity)
        status = str(operator["sourceStatus"])
        if status not in SOURCE_STATUSES:
            raise ClassicalSourceOperatorError(f"Unknown source status for {identity[0]}: {status}")
        if status.startswith("SOURCE_CLOSED") and not str(operator["verseOrLocator"]).strip():
            raise ClassicalSourceOperatorError(f"Source-closed operator lacks a source locator: {identity[0]}")
        if bool(operator["marketDirectionAuthorized"]) or bool(operator["marketMagnitudeAuthorized"]):
            raise ClassicalSourceOperatorError(f"Market authorization is prohibited: {identity[0]}")
        if operator["rootOrCommentary"] == "COMMENTARY_ONLY" and "ROOT" in str(operator["sourceFamily"]):
            raise ClassicalSourceOperatorError(f"Commentary-only operator cannot claim root source family: {identity[0]}")
        if status in {"SOURCE_PARTIAL", "SOURCE_UNRESOLVED", "SOURCE_SILENT"} and (
            bool(operator["modeOneEligible"]) or bool(operator["machineEvaluable"])
        ):
            raise ClassicalSourceOperatorError(f"Unresolved operator cannot claim executable source closure: {identity[0]}")


def load_source_operator_ledger(path: Path = DEFAULT_LEDGER_PATH) -> dict[str, Any]:
    ledger = _read_json(path, "classical source operator ledger")
    validate_source_operator_ledger(ledger)
    return ledger


def load_unresolved_dependency_registry(path: Path = DEFAULT_UNRESOLVED_PATH) -> dict[str, Any]:
    registry = _read_json(path, "classical source operator unresolved dependency registry")
    dependencies = registry.get("dependencies")
    if registry.get("contract") != "MO_R4A_S1_SOURCE_OPERATOR_UNRESOLVED_DEPENDENCY_REGISTRY_V1":
        raise ClassicalSourceOperatorError("Unsupported unresolved dependency registry contract")
    if not isinstance(dependencies, list) or not dependencies:
        raise ClassicalSourceOperatorError("Unresolved dependency registry must contain dependencies")
    ids = [item.get("dependencyId") for item in dependencies if isinstance(item, dict)]
    if len(ids) != len(dependencies) or len(set(ids)) != len(ids):
        raise ClassicalSourceOperatorError("Unresolved dependency registry IDs must be unique")
    required = {
        "MULTI_MODIFIER_STACKING_UNRESOLVED",
        "UNIVERSAL_MULTI_PLANET_PRECEDENCE_NOT_SOURCE_CLOSED",
        "MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED",
        "CONTEXT_SPECIFIC_RESOLVER_REQUIRED",
        "NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT",
        "NO_AUTHORIZED_MARKET_BRIDGE",
        "TRAILOKYA_ARTHA_CONTEXT_NOT_GENERALIZABLE",
        "LATTA_NOT_ORDINARY_VEDHA",
        "ARGHYA_NOT_GENERIC_MARKET_OPERATOR",
    }
    absent = required - set(ids)
    if absent:
        raise ClassicalSourceOperatorError(f"Required unresolved dependencies are absent: {sorted(absent)}")
    return registry


def load_cross_text_matrix(path: Path = DEFAULT_CROSS_TEXT_PATH) -> dict[str, Any]:
    matrix = _read_json(path, "source operator cross-text matrix")
    if matrix.get("contract") != "MO_R4A_S1_SOURCE_OPERATOR_CROSS_TEXT_MATRIX_V1":
        raise ClassicalSourceOperatorError("Unsupported source operator cross-text matrix")
    if not isinstance(matrix.get("topics"), list):
        raise ClassicalSourceOperatorError("Source operator cross-text matrix must contain topics")
    return matrix


def _operator(ledger: Mapping[str, Any], operator_id: str) -> dict[str, Any]:
    matches = [
        candidate
        for candidate in ledger["operators"]
        if isinstance(candidate, dict) and candidate.get("operatorId") == operator_id
    ]
    if len(matches) != 1:
        raise ClassicalSourceOperatorError(f"Expected exactly one source operator: {operator_id}")
    return matches[0]


def relative_place(source_sign: str, target_sign: str) -> int:
    """Return the target's inclusive place from the source sign."""

    source = _sign(source_sign, "source sign")
    target = _sign(target_sign, "target sign")
    return ((SIGN_INDEX[target] - SIGN_INDEX[source]) % 12) + 1


def evaluate_trailokya_natural_relationship(
    source_body: str,
    target_body: str,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1")
    source = _body(source_body, "relationship source body")
    target = _body(target_body, "relationship target body")
    snapshot = {"sourceBody": source, "targetBody": target}
    matrix = operator["rule"]["friendshipMatrix"]
    row = matrix.get(source)
    if source not in RELATIONSHIP_BODIES or target not in RELATIONSHIP_BODIES or not isinstance(row, dict):
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_TRAILOKYA",),
            explanation="Trailokya's admitted friendship table is not closed for this body pair.",
            conditions_missing=("CLASSICAL_SEVEN_PLANET_RELATIONSHIP_INPUT",),
        )
    if target in row["friends"]:
        state = "FRIEND"
    elif target in row["neutral"]:
        state = "NEUTRAL"
    elif target in row["enemies"]:
        state = "ENEMY"
    else:
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("TRAILOKYA_RELATIONSHIP_CELL_NOT_SOURCE_CLOSED",),
            explanation="No admitted Trailokya relationship cell covers this body pair.",
        )
    return _source_output(
        operator,
        input_snapshot=snapshot,
        output_state=state,
        explanation=f"Trailokya's source-specific natural relationship for {source} to {target} is {state}.",
        conditions_satisfied=("TRAILOKYA_1972_V168_TO_V171_MATRIX",),
    )


def evaluate_temporary_relationship(
    source_sign: str,
    target_sign: str,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1")
    source = _sign(source_sign, "temporary relationship source sign")
    target = _sign(target_sign, "temporary relationship target sign")
    place = relative_place(source, target)
    friendly = set(operator["rule"]["temporaryFriendPositions"])
    state = "TEMPORARY_FRIEND" if place in friendly else "TEMPORARY_ENEMY"
    return _source_output(
        operator,
        input_snapshot={"sourceSign": source, "targetSign": target, "relativePlace": place},
        output_state=state,
        explanation=f"The source-audited temporary relationship at relative place {place} is {state}.",
        conditions_satisfied=(f"RELATIVE_PLACE_{place}",),
    )


def evaluate_compound_relationship(
    natural_relationship: str,
    temporary_relationship: str,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1")
    natural = _string(natural_relationship, "natural relationship")
    temporary = _string(temporary_relationship, "temporary relationship")
    mapping = operator["rule"]["compoundRelationshipMap"]
    key = f"{natural}:{temporary}"
    if key not in mapping:
        return _unresolved_output(
            operator,
            input_snapshot={"naturalRelationship": natural, "temporaryRelationship": temporary},
            output_state="UNKNOWN",
            dependencies=("COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED",),
            explanation="Compound relationship requires an admitted natural and temporary relationship state.",
        )
    return _source_output(
        operator,
        input_snapshot={"naturalRelationship": natural, "temporaryRelationship": temporary},
        output_state=str(mapping[key]),
        explanation="The source-defined five-state compound relationship is categorical and has no market sign.",
        conditions_satisfied=("NATURAL_AND_TEMPORARY_RELATIONSHIP_AVAILABLE",),
    )


def evaluate_ordinary_dristi(
    relative_place_value: int,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "SARAVALI_4_32_ORDINARY_DRSTI_V1")
    if type(relative_place_value) is not int or relative_place_value not in range(1, 13):
        return _unresolved_output(
            operator,
            input_snapshot={"relativePlace": relative_place_value},
            output_state="UNKNOWN",
            dependencies=("ORDINARY_DRSTI_RELATIVE_PLACE_INVALID",),
            explanation="An ordinary drsti fraction requires one of twelve relative places.",
        )
    values = operator["rule"]["ordinaryAspectFractions"]
    value = values.get(str(relative_place_value))
    if value is None:
        return _source_output(
            operator,
            input_snapshot={"relativePlace": relative_place_value},
            output_state="NO_STATED_ORDINARY_FRACTION",
            explanation="The admitted ordinary drsti fraction table does not state a fraction for this place.",
            status="SOURCE_CLOSED_CATEGORICAL",
        )
    measurement = _measurement(
        measurement_type="DRSTI_FRACTION",
        value=str(value),
        source_scope="ORDINARY_DRSTI_SOURCE_GEOMETRY",
        operator=operator,
    )
    return _source_output(
        operator,
        input_snapshot={"relativePlace": relative_place_value},
        output_state=f"DRSTI_{str(value).replace('/', '_')}",
        source_measurement=measurement,
        explanation=f"Ordinary drsti at relative place {relative_place_value} has the source fraction {value}.",
        conditions_satisfied=(f"RELATIVE_PLACE_{relative_place_value}",),
    )


def evaluate_special_dristi(
    source_body: str,
    relative_place_value: int,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1")
    body = _body(source_body, "special drsti source body")
    if type(relative_place_value) is not int or relative_place_value not in range(1, 13):
        return _unresolved_output(
            operator,
            input_snapshot={"sourceBody": body, "relativePlace": relative_place_value},
            output_state="UNKNOWN",
            dependencies=("SPECIAL_DRSTI_RELATIVE_PLACE_INVALID",),
            explanation="A special drsti check requires one of twelve relative places.",
        )
    full_places = set(operator["rule"]["specialFullAspectPlaces"].get(body, []))
    if relative_place_value not in full_places:
        return _source_output(
            operator,
            input_snapshot={"sourceBody": body, "relativePlace": relative_place_value},
            output_state="NO_SPECIAL_FULL_OVERRIDE",
            explanation="No source-closed special full drsti override applies at this relative place.",
            status="SOURCE_CLOSED_CATEGORICAL",
        )
    measurement = _measurement(
        measurement_type="DRSTI_FRACTION",
        value="FULL",
        source_scope="SPECIAL_DRSTI_SOURCE_GEOMETRY",
        operator=operator,
    )
    return _source_output(
        operator,
        input_snapshot={"sourceBody": body, "relativePlace": relative_place_value},
        output_state="SPECIAL_FULL_DRSTI",
        source_measurement=measurement,
        explanation=f"{body} has a source-closed special full drsti at relative place {relative_place_value}.",
        conditions_satisfied=(f"{body}_SPECIAL_FULL_{relative_place_value}",),
    )


def evaluate_trailokya_planet_nature(
    body: str,
    *,
    moon_condition: str | None = None,
    mercury_krura_association: bool | None = None,
    motion_state: str | None = None,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_NATURAL_PLANET_CLASS_V1")
    normalized_body = _body(body, "planet nature body")
    snapshot = {
        "body": normalized_body,
        "moonCondition": moon_condition,
        "mercuryKruraAssociation": mercury_krura_association,
        "motionState": motion_state,
    }
    rule = operator["rule"]
    if normalized_body == "MOON" and moon_condition not in {"PurnaSaumya", "KshinaKrura"}:
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="CONDITIONAL",
            dependencies=("MOON_CONDITION_INPUT_UNAVAILABLE",),
            explanation="Trailokya gives Moon a condition-dependent class; the required source condition is unavailable.",
            conditions_missing=("MOON_CONDITION",),
        )
    if normalized_body == "MERCURY" and mercury_krura_association is None:
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="CONDITIONAL",
            dependencies=("MERCURY_ASSOCIATION_INPUT_UNAVAILABLE",),
            explanation="Trailokya gives Mercury an association-dependent class; the admitted association input is unavailable.",
            conditions_missing=("MERCURY_SAME_PADA_OR_NAVAMSHA_KRURA_ASSOCIATION",),
        )
    if normalized_body == "MOON":
        base = "SAUMYA" if moon_condition == "PurnaSaumya" else "KRURA"
    elif normalized_body == "MERCURY":
        base = "KRURA" if mercury_krura_association else "SAUMYA"
    elif normalized_body in rule["kruraBodies"]:
        base = "KRURA"
    else:
        base = "SAUMYA"
    normalized_motion = str(motion_state or "").upper()
    if normalized_motion == "RETROGRADE":
        output = "MAHAKRURA" if base == "KRURA" else "MAHASHUBHA"
        detail = "Retrograde changes Trailokya's categorical intensity only; it is not a numeric market factor."
    elif normalized_motion in {"SWIFT", "SHIGHRA", "ATICARA"}:
        output = base
        detail = "Swift motion retains the source natural class."
    else:
        output = base
        detail = "The base source natural class is categorical."
    return _source_output(
        operator,
        input_snapshot=snapshot,
        output_state=output,
        explanation=detail,
        conditions_satisfied=(f"TRAILOKYA_BASE_CLASS_{base}",),
    )


def evaluate_trailokya_dignity(
    body: str,
    sign: str,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_DIGNITY_V1")
    normalized_body = _body(body, "dignity body")
    normalized_sign = _sign(sign, "dignity sign")
    rule = operator["rule"]
    snapshot = {"body": normalized_body, "sign": normalized_sign}
    node = rule["nodes"].get(normalized_body)
    if isinstance(node, dict):
        if normalized_sign == node["ownSign"]:
            state = "OWN_SIGN"
        elif normalized_sign == node["exaltationSign"]:
            state = "EXALTATION"
        elif normalized_sign == node["debilitationSign"]:
            state = "DEBILITATION"
        else:
            return _source_output(
                operator,
                input_snapshot=snapshot,
                output_state="OTHER_DIGNITY_NOT_COMPOSED",
                explanation="Trailokya's node dignity record is source-closed for own, exaltation, and debilitation only.",
                status="SOURCE_PARTIAL",
                unresolved_dependencies=("TRAILOKYA_NODE_OTHER_SIGN_DIGNITY_NOT_SOURCE_CLOSED",),
            )
        return _source_output(
            operator,
            input_snapshot=snapshot,
            output_state=state,
            explanation=f"Trailokya's node-specific dignity record gives {normalized_body} in {normalized_sign} as {state}.",
            conditions_satisfied=(f"{normalized_body}_{state}",),
        )
    planet = rule["planets"].get(normalized_body)
    if not isinstance(planet, dict):
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("TRAILOKYA_DIGNITY_BODY_UNAVAILABLE",),
            explanation="No admitted Trailokya dignity record covers this body.",
        )
    if normalized_sign == planet["exaltationSign"]:
        state = "EXALTATION"
    elif normalized_sign == planet["debilitationSign"]:
        state = "DEBILITATION"
    elif normalized_sign in planet["samaSthanaSigns"]:
        state = "SAMA_STHANA"
    elif normalized_sign in planet["ownSigns"]:
        state = "OWN_SIGN"
    else:
        return _source_output(
            operator,
            input_snapshot=snapshot,
            output_state="OTHER_DIGNITY_NOT_COMPOSED",
            explanation="This sign is outside Trailokya's admitted own, exaltation, debilitation, and sama-sthana entries.",
            status="SOURCE_PARTIAL",
            unresolved_dependencies=("TRAILOKYA_FULL_DIGNITY_COMPOSITION_NOT_SOURCE_CLOSED",),
        )
    return _source_output(
        operator,
        input_snapshot=snapshot,
        output_state=state,
        explanation=(
            f"Trailokya's dignity record gives {normalized_body} in {normalized_sign} as {state}. "
            "SAMA_STHANA remains distinct from SAMA_GRIHA."
        ),
        conditions_satisfied=(f"{normalized_body}_{state}",),
    )


def evaluate_trailokya_sthana_bala(
    relationship_state: str,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_STHANA_BALA_V1")
    relationship = _string(relationship_state, "sthana bala relationship state")
    values = operator["rule"]["sthanaBalaFractions"]
    if relationship not in values:
        return _unresolved_output(
            operator,
            input_snapshot={"relationshipState": relationship},
            output_state="UNKNOWN",
            dependencies=("TRAILOKYA_STHANA_BALA_RELATIONSHIP_INPUT_UNAVAILABLE",),
            explanation="Trailokya sthana-bala requires OWN, FRIEND, NEUTRAL, or ENEMY relationship state.",
        )
    value = str(values[relationship])
    return _source_output(
        operator,
        input_snapshot={"relationshipState": relationship},
        output_state=f"STHANA_BALA_{value.replace('/', '_')}",
        source_measurement=_measurement(
            measurement_type="STHANA_BALA_FRACTION",
            value=value,
            source_scope="TRAILOKYA_VEDHA",
            operator=operator,
        ),
        explanation="This is Trailokya sthana-bala, structurally distinct from Trailokya sthana-phala.",
        conditions_satisfied=(f"RELATIONSHIP_{relationship}",),
    )


def evaluate_trailokya_sthana_phala(
    nature_state: str,
    relationship_state: str,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_STHANA_PHALA_V1")
    nature = _string(nature_state, "sthana phala nature state")
    relationship = _string(relationship_state, "sthana phala relationship state")
    tables = operator["rule"]["sthanaPhala"]
    table = tables.get(nature)
    if not isinstance(table, dict) or relationship not in table:
        return _unresolved_output(
            operator,
            input_snapshot={"natureState": nature, "relationshipState": relationship},
            output_state="UNKNOWN",
            dependencies=("TRAILOKYA_STHANA_PHALA_INPUT_UNAVAILABLE",),
            explanation="Trailokya sthana-phala requires a source class of SAUMYA or KRURA and a stated relationship.",
        )
    value = str(table[relationship])
    return _source_output(
        operator,
        input_snapshot={"natureState": nature, "relationshipState": relationship},
        output_state=f"STHANA_PHALA_{value}",
        source_measurement=_measurement(
            measurement_type="TRAILOKYA_STHANA_PHALA",
            value=value,
            source_scope="TRAILOKYA_VEDHA",
            operator=operator,
        ),
        explanation=(
            "This is a Trailokya Vedha source result value, not an oscillator magnitude, forecast probability, "
            "or currency direction."
        ),
        conditions_satisfied=(f"{nature}_{relationship}",),
    )


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def evaluate_trailokya_v166_modifier(
    source_measurement: Mapping[str, Any],
    modifiers: Sequence[str],
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_V166_INDIVIDUAL_MODIFIER_V1")
    normalized = tuple(_string(item, "Trailokya modifier") for item in modifiers)
    snapshot = {
        "sourceMeasurement": dict(source_measurement),
        "modifiers": list(normalized),
    }
    if source_measurement.get("measurementType") != "TRAILOKYA_STHANA_PHALA":
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("TRAILOKYA_V166_REQUIRES_STHANA_PHALA_INPUT",),
            explanation="Verse 166 applies to the previously obtained Trailokya sthana/Vedha phala result.",
        )
    if len(normalized) != 1:
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNRESOLVED_MODIFIER_COMBINATION",
            dependencies=("MULTI_MODIFIER_STACKING_UNRESOLVED",),
            explanation="The source closes individual modifiers but does not close their multi-condition composition.",
            conditions_missing=("SINGLE_ISOLATED_MODIFIER",),
        )
    modifier = normalized[0]
    rules = operator["rule"]["individualModifiers"]
    if modifier not in rules:
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("TRAILOKYA_V166_MODIFIER_NOT_SOURCE_CLOSED",),
            explanation="This modifier is not one of the individually source-closed verse-166 conditions.",
        )
    base = Fraction(str(source_measurement["value"]))
    rule = rules[modifier]
    if modifier == "SWIFT":
        result_measurement = {
            **dict(source_measurement),
            "sourceModifierFactor": None,
            "sourceResult": "BASE_SOURCE_RESULT",
        }
        return _source_output(
            operator,
            input_snapshot=snapshot,
            output_state="BASE_SOURCE_RESULT_RETAINED",
            source_measurement=result_measurement,
            explanation="Swift retains the source base result; the source does not state a numerical factor of 1.0.",
            conditions_satisfied=("SWIFT_ISOLATED_MODIFIER",),
        )
    factor = Fraction(str(rule["factor"]))
    result = base * factor
    result_measurement = _measurement(
        measurement_type="TRAILOKYA_STHANA_PHALA",
        value=_fraction_text(result),
        source_scope="TRAILOKYA_VEDHA",
        operator=operator,
        factor=_fraction_text(factor),
    )
    result_measurement["baseSourceMeasurement"] = dict(source_measurement)
    return _source_output(
        operator,
        input_snapshot=snapshot,
        output_state=f"ISOLATED_{modifier}_MODIFIER_APPLIED",
        source_measurement=result_measurement,
        explanation=(
            f"Verse 166 applies the isolated {modifier} source modifier of {_fraction_text(factor)} "
            "within Trailokya Vedha only."
        ),
        conditions_satisfied=(f"{modifier}_ISOLATED_MODIFIER",),
    )


def evaluate_trailokya_motion_class(
    body: str,
    relative_sun_place: int,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_STHULA_MOTION_CLASS_V1")
    normalized_body = _body(body, "motion body")
    snapshot = {"body": normalized_body, "relativeSunPlace": relative_sun_place}
    if type(relative_sun_place) is not int or relative_sun_place not in range(1, 13):
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED",),
            explanation="A Trailokya sthula motion class needs one of twelve relative Sun positions.",
        )
    rule = operator["rule"]
    if normalized_body in rule["outerPlanetBodies"]:
        if relative_sun_place == 1:
            return _source_output(
                operator,
                input_snapshot=snapshot,
                output_state="ASTA_DIRECTION_UNKNOWN",
                explanation="Trailokya names the same-sign/combust Asta context but does not establish a Vedha direction.",
                status="SOURCE_PARTIAL",
                unresolved_dependencies=("MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED",),
            )
        motion = rule["outerPlanetRelativeSun"][str(relative_sun_place)]
    elif normalized_body in rule["innerPlanetBodies"]:
        motion = rule["innerPlanetRelativeSun"].get(str(relative_sun_place))
        if motion is None:
            return _source_output(
                operator,
                input_snapshot=snapshot,
                output_state="UNKNOWN",
                explanation="Trailokya does not permit inheriting the outer-planet table for this unlisted inner-planet case.",
                status="SOURCE_PARTIAL",
                unresolved_dependencies=("MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED",),
            )
    else:
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("MOTION_SOURCE_BODY_UNAVAILABLE", "MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED"),
            explanation="No admitted Trailokya sthula motion table covers this body.",
        )
    direction = rule["motionDirection"][motion]
    return _source_output(
        operator,
        input_snapshot=snapshot,
        output_state=str(motion),
        explanation=f"Trailokya's bounded sthula motion class is {motion}, with source Vedha direction {direction}.",
        conditions_satisfied=(f"RELATIVE_SUN_PLACE_{relative_sun_place}",),
    )


def evaluate_dik_bala_condition(
    body: str,
    direction: str,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "BJ_SARAVALI_DIK_BALA_CONDITION_V1")
    normalized_body = _body(body, "dik bala body")
    normalized_direction = _string(direction, "dik bala direction")
    expected = operator["rule"]["directionByBody"].get(normalized_body)
    if expected is None:
        return _unresolved_output(
            operator,
            input_snapshot={"body": normalized_body, "direction": normalized_direction},
            output_state="UNKNOWN",
            dependencies=("DIK_BALA_BODY_UNAVAILABLE",),
            explanation="No source-audited dik bala assignment covers this body.",
        )
    state = (
        "DIRECTIONAL_STRENGTH_CONDITION_PRESENT"
        if normalized_direction == expected
        else "DIRECTIONAL_STRENGTH_CONDITION_NOT_PRESENT"
    )
    return _source_output(
        operator,
        input_snapshot={"body": normalized_body, "direction": normalized_direction},
        output_state=state,
        explanation="The admitted dik bala rule is categorical; no continuous angular interpolation is authorized.",
        status="SOURCE_CLOSED_CATEGORICAL",
        conditions_satisfied=(f"EXPECTED_DIRECTION_{expected}",) if state.endswith("PRESENT") else (),
    )


def evaluate_latta_source_boundary(
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_GRAHA_LATTA_BOUNDARY_V1")
    return _unresolved_output(
        operator,
        input_snapshot={},
        output_state="NOT_EVALUATED",
        dependencies=("LATTA_NOT_ORDINARY_VEDHA", "TRAILOKYA_LATTA_COUNTING_ORIGIN_UNRESOLVED"),
        explanation="Graha Latta is a separate 27-nakshatra doctrine and is not an ordinary Vedha or event-compiler fallback.",
    )


def evaluate_arghya_source_boundary(
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_ledger = ledger or load_source_operator_ledger()
    operator = _operator(source_ledger, "TRAILOKYA_1972_ARGHYA_VISWA_BOUNDARY_V1")
    return _unresolved_output(
        operator,
        input_snapshot={},
        output_state="NOT_EVALUATED",
        dependencies=("ARGHYA_NOT_GENERIC_MARKET_OPERATOR", "TRAILOKYA_ARTHA_CONTEXT_NOT_GENERALIZABLE"),
        explanation="Arghya Viswa arithmetic is source-scoped historical commodity material and cannot be used as a generic resolver or FX operator.",
    )


def compose_source_operator_outputs(operator_outputs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Preserve source outputs while refusing an unsourced astrology reducer."""

    return {
        "compositionStatus": NO_COMPOSITION_CONTRACT,
        "astrologicalInterpretationState": "UNKNOWN_ASTRO_STATE",
        "evaluatedOperatorIds": [
            str(output["operatorId"])
            for output in operator_outputs
            if bool(output.get("machineEvaluated"))
        ],
        "unresolvedOperatorIds": sorted(
            {
                dependency
                for output in operator_outputs
                for dependency in output.get("unresolvedDependencies", [])
            }
            | {NO_COMPOSITION_CONTRACT}
        ),
        "explanation": (
            "Several source operators may be evaluated, but no admitted source contract composes them into a "
            "supportive, adverse, neutral, or currency-facing state."
        ),
    }


def _sidereal_sign(body: str, moment: datetime) -> str:
    longitude = _calculate_sidereal_geocentric_longitude(body, moment)
    return SIGNS[int(longitude // 30.0) % len(SIGNS)]


def _chart_records_by_id(resource_root: Path) -> dict[str, Any]:
    path = resource_root / "research_labs" / "chart_conditioned_aspects" / "profiles" / "founder_chart_hypotheses_v1.json"
    records = load_founder_chart_identity_records(path)
    return {record.chart.chart_id: record for record in records}


def _event_astronomy_snapshot(event: Mapping[str, str], chart_record: Any) -> dict[str, Any]:
    exact = _parse_utc(event["exactUtc"], "event exact UTC")
    transit_body = _body(event["transitBody"], "event transit body")
    natal_target = _body(event["natalTarget"], "event natal target")
    transit_sign = _sidereal_sign(transit_body, exact)
    natal_sign = _sidereal_sign(natal_target, chart_record.chart.timestamp_utc)
    sun_sign = _sidereal_sign("SUN", exact)
    return {
        "astronomyContract": "RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1",
        "chartId": chart_record.chart.chart_id,
        "chartHypothesisId": chart_record.chart_hypothesis_id,
        "chartHash": chart_record.chart_hash,
        "exactUtc": event["exactUtc"],
        "transitBody": transit_body,
        "natalTarget": natal_target,
        "transitSign": transit_sign,
        "natalSign": natal_sign,
        "transitRelativeNatalPlace": relative_place(transit_sign, natal_sign),
        "transitRelativeSunPlace": relative_place(transit_sign, sun_sign),
    }


def _event_operator_outputs(snapshot: Mapping[str, Any], ledger: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    transit = str(snapshot["transitBody"])
    natal = str(snapshot["natalTarget"])
    relative_natal = int(snapshot["transitRelativeNatalPlace"])
    relationship = evaluate_trailokya_natural_relationship(transit, natal, ledger=ledger)
    temporary = evaluate_temporary_relationship(
        str(snapshot["transitSign"]),
        str(snapshot["natalSign"]),
        ledger=ledger,
    )
    compound = evaluate_compound_relationship(
        str(relationship["outputState"]),
        str(temporary["outputState"]),
        ledger=ledger,
    )
    motion = evaluate_trailokya_motion_class(
        transit,
        int(snapshot["transitRelativeSunPlace"]),
        ledger=ledger,
    )
    nature = evaluate_trailokya_planet_nature(
        transit,
        motion_state=str(motion["outputState"]) if motion["machineEvaluated"] else None,
        ledger=ledger,
    )
    outputs = [
        relationship,
        temporary,
        compound,
        evaluate_ordinary_dristi(relative_natal, ledger=ledger),
        evaluate_special_dristi(transit, relative_natal, ledger=ledger),
        nature,
        evaluate_trailokya_dignity(transit, str(snapshot["transitSign"]), ledger=ledger),
        motion,
        evaluate_latta_source_boundary(ledger=ledger),
        evaluate_arghya_source_boundary(ledger=ledger),
    ]
    structurally_applicable = [
        "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1",
        "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1",
        "BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1",
        "SARAVALI_4_32_ORDINARY_DRSTI_V1",
        "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1",
        "TRAILOKYA_1972_NATURAL_PLANET_CLASS_V1",
        "TRAILOKYA_1972_DIGNITY_V1",
        "TRAILOKYA_1972_STHULA_MOTION_CLASS_V1",
        "TRAILOKYA_1972_STHANA_BALA_V1",
        "TRAILOKYA_1972_STHANA_PHALA_V1",
        "TRAILOKYA_1972_V166_INDIVIDUAL_MODIFIER_V1",
        "TRAILOKYA_1972_GRAHA_LATTA_BOUNDARY_V1",
        "TRAILOKYA_1972_ARGHYA_VISWA_BOUNDARY_V1",
    ]
    return outputs, structurally_applicable


def _coverage_status(outputs: Sequence[Mapping[str, Any]]) -> str:
    closed = sum(1 for output in outputs if str(output.get("status", "")).startswith("SOURCE_CLOSED"))
    if closed == 0:
        return "SOURCE_OPERATOR_COVERAGE_NONE"
    if closed < 4:
        return "SOURCE_OPERATOR_COVERAGE_PARTIAL"
    return "SOURCE_OPERATOR_COVERAGE_SUBSTANTIAL"


def build_real_source_operator_coverage_report(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Bind source operators to frozen identities without reading review or market data."""

    root = Path(resource_root).resolve()
    ledger = load_source_operator_ledger(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_LEDGER_PATH.name
    )
    load_unresolved_dependency_registry(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_UNRESOLVED_PATH.name
    )
    chart_records = _chart_records_by_id(root)
    configure_ephemeris()
    sides: list[dict[str, Any]] = []
    for side in machine_interpretation.founder_review.SIDES:
        baseline = machine_interpretation._identity_only_side_coverage(root, side)
        events: list[dict[str, Any]] = []
        for baseline_event in baseline["events"]:
            event = baseline_event["eventIdentity"]
            chart = chart_records.get(event["chartId"])
            if chart is None:
                raise ClassicalSourceOperatorError(f"No accepted chart record for {event['chartId']}")
            if (
                chart.chart_hypothesis_id != event["chartHypothesisId"]
                or chart.chart.instrument_id != event["instrumentIdentity"]
                or chart.astronomy_contract["contractId"] != event["astronomyContract"]
            ):
                raise ClassicalSourceOperatorError(f"Immutable event/chart contract mismatch for {event['eventId']}")
            snapshot = _event_astronomy_snapshot(event, chart)
            outputs, applicable = _event_operator_outputs(snapshot, ledger)
            composition = compose_source_operator_outputs(outputs)
            events.append(
                {
                    "eventId": event["eventId"],
                    "eventHash": event["eventHash"],
                    "sideIdentity": event["sideIdentity"],
                    "transitBody": event["transitBody"],
                    "natalTarget": event["natalTarget"],
                    "aspectType": event["aspectType"],
                    "exactUtc": event["exactUtc"],
                    "identityStatus": baseline_event["identityStatus"],
                    "inputPolicy": "IMMUTABLE_EVENT_IDENTITY_PLUS_APPROVED_CHART_ASTRONOMY_ONLY",
                    "astronomySnapshot": snapshot,
                    "applicableOperatorIds": applicable,
                    "evaluatedOperatorIds": composition["evaluatedOperatorIds"],
                    "operatorOutputs": outputs,
                    "unresolvedOperatorIds": composition["unresolvedOperatorIds"],
                    "sourceCoverageStatus": _coverage_status(outputs),
                    "astrologicalCompositionStatus": composition["compositionStatus"],
                    "astrologicalInterpretationState": composition["astrologicalInterpretationState"],
                    "marketBridgeStatus": NO_MARKET_BRIDGE,
                    "currencyDirectionStatus": UNKNOWN_CURRENCY_DIRECTION,
                    "magnitudeStatus": MAGNITUDE_NOT_CONFIGURED,
                    "mode": EXPLORATORY_UNSIGNED_MODE,
                    "explanation": (
                        "Classical source operators were evaluated only from immutable event identity and approved "
                        "chart astronomy. No approved composition contract or USD/JPY market bridge exists, so "
                        "currency direction remains unknown."
                    ),
                }
            )
        if len(events) != 12:
            raise ClassicalSourceOperatorError(f"{side} source-operator binding requires exactly 12 events")
        side_record = {
            key: baseline[key]
            for key in (
                "sideIdentity",
                "blankPacketSha256",
                "identityIntegrityManifestSha256",
                "identityAuditSha256",
                "eventCount",
            )
        }
        side_record["events"] = events
        sides.append(side_record)
    all_events = [event for side in sides for event in side["events"]]
    if len(all_events) != 24:
        raise ClassicalSourceOperatorError("Source-operator binding requires exactly 24 frozen events")
    summary = {
        "eventCount": len(all_events),
        "usdEventCount": len(sides[0]["events"]),
        "jpyEventCount": len(sides[1]["events"]),
        "singlePassVerifiedCount": sum(event["identityStatus"] == "SINGLE_PASS_VERIFIED" for event in all_events),
        "sourceOperatorNoneCount": sum(event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_NONE" for event in all_events),
        "sourceOperatorPartialCount": sum(event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_PARTIAL" for event in all_events),
        "sourceOperatorSubstantialCount": sum(
            event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_SUBSTANTIAL" for event in all_events
        ),
        "sourceOperatorCompleteForDeclaredScopeCount": sum(
            event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_COMPLETE_FOR_DECLARED_SCOPE" for event in all_events
        ),
        "astrologyUnknownCount": sum(event["astrologicalInterpretationState"] == "UNKNOWN_ASTRO_STATE" for event in all_events),
        "astrologyMixedCount": sum(event["astrologicalInterpretationState"] == "MIXED_ASTRO_STATE" for event in all_events),
        "astrologySourceStateCount": sum(
            event["astrologicalInterpretationState"]
            in {"SUPPORTIVE_ASTRO_STATE", "ADVERSE_ASTRO_STATE", "NEUTRAL_ASTRO_STATE"}
            for event in all_events
        ),
        "marketBridgeAvailableCount": sum(event["marketBridgeStatus"] != NO_MARKET_BRIDGE for event in all_events),
        "currencyDirectionUnknownCount": sum(
            event["currencyDirectionStatus"] == UNKNOWN_CURRENCY_DIRECTION for event in all_events
        ),
        "magnitudeConfiguredCount": sum(event["magnitudeStatus"] != MAGNITUDE_NOT_CONFIGURED for event in all_events),
    }
    body = {
        "contract": CLASSICAL_SOURCE_OPERATOR_COVERAGE_CONTRACT,
        "schemaVersion": CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION,
        "milestone": "MO-R4A-S1",
        "inputPolicy": "IMMUTABLE_EVENT_IDENTITY_PLUS_APPROVED_CHART_ASTRONOMY_ONLY",
        "reviewStoreRead": False,
        "founderDecisionRead": False,
        "priceOrOutcomeRead": False,
        "eventUniverseRegenerated": False,
        "sourceOperatorLedgerContract": ledger["contract"],
        "sourceOperatorLedgerVersion": ledger["schemaVersion"],
        "sourceOperatorLedgerCanonicalHash": _canonical_hash(ledger),
        "sides": sides,
        "summary": summary,
        "guardrails": {
            "marketHypothesisRegistryReadForEntries": False,
            "marketHypothesisRegistryEntriesCreated": 0,
            "marketBridgeCreated": False,
            "currencyPolarityCreated": False,
            "catalogueAdmission": False,
            "evidenceAdmission": False,
            "priceDataRead": False,
            "outcomeDataRead": False,
            "reviewStoreRead": False,
            "founderDecisionRead": False,
            "sbcRead": False,
            "signedUsdWaveCreated": False,
            "signedJpyWaveCreated": False,
            "signedPairResultantCreated": False,
            "magnitudeConfigured": False,
            "autoSuggestEnabled": False,
            "mlEnabled": False,
            "mt5Enabled": False,
            "executionAllowed": False,
        },
    }
    return {**body, "sourceOperatorCoverageHash": _canonical_hash(body)}


def render_real_source_operator_coverage_markdown(report: Mapping[str, Any]) -> str:
    if report.get("contract") != CLASSICAL_SOURCE_OPERATOR_COVERAGE_CONTRACT:
        raise ClassicalSourceOperatorError("Cannot render an unsupported source-operator coverage report")
    summary = report["summary"]
    lines = [
        "# MO-R4A-S1 Real 24 Event Source-Operator Coverage",
        "",
        "This report binds only frozen event identities to approved chart astronomy and source-operator contracts.",
        "It does not read Founder Review decisions, a durable review store, price, outcomes, SBC, or market data.",
        "",
        f"Coverage hash: {report['sourceOperatorCoverageHash']}",
        f"Ledger canonical hash: {report['sourceOperatorLedgerCanonicalHash']}",
        f"Events: {summary['eventCount']} ({summary['usdEventCount']} USD, {summary['jpyEventCount']} JPY)",
        f"Substantial source coverage: {summary['sourceOperatorSubstantialCount']}",
        f"Astrological interpretation remains unknown: {summary['astrologyUnknownCount']}",
        f"Currency direction remains unknown: {summary['currencyDirectionUnknownCount']}",
        "",
        "| Side | Event ID | Transit to natal | Evaluated source operators | Coverage | Astrology composition | Currency direction |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for side in report["sides"]:
        for event in side["events"]:
            operator_ids = ", ".join(event["evaluatedOperatorIds"])
            lines.append(
                "| "
                + " | ".join(
                    (
                        event["sideIdentity"],
                        event["eventId"],
                        f"{event['transitBody']} to {event['natalTarget']}",
                        operator_ids,
                        event["sourceCoverageStatus"],
                        event["astrologicalCompositionStatus"],
                        event["currencyDirectionStatus"],
                    )
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Explanation",
            "",
            "Several classical rules can be evaluated for each frozen event, including source-specific sign placement,",
            "relationship, and aspect facts where the necessary inputs exist. The admitted texts do not provide one",
            "approved composition rule for these facts, and no approved USD/JPY market bridge exists. The report therefore",
            "does not claim a supportive/adverse astrology state, currency direction, market magnitude, or signed wave.",
            "",
            "A source number, such as an aspect fraction or Trailokya sthana-phala, remains a typed source measurement.",
            "It is not a percentage forecast, oscillator amplitude, or price estimate.",
            "",
        ]
    )
    return "\n".join(lines)


def write_real_source_operator_coverage_artifacts(
    *,
    resource_root: Path = PROJECT_ROOT,
    json_path: Path,
    markdown_path: Path,
) -> dict[str, Any]:
    """Write deterministic audit artifacts only to explicit caller-owned paths."""

    report = build_real_source_operator_coverage_report(resource_root)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_real_source_operator_coverage_markdown(report), encoding="utf-8")
    return report
