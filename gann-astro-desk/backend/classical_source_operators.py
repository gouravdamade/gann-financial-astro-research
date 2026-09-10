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
from copy import deepcopy
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
CLASSICAL_SOURCE_OPERATOR_S1R1_LEDGER_CONTRACT = "MO_R4A_S1R1_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1"
CLASSICAL_SOURCE_OPERATOR_S1R1_R1_LEDGER_CONTRACT = "MO_R4A_S1R1_R1_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1"
CLASSICAL_SOURCE_OPERATOR_S2R1_LEDGER_CONTRACT = "MO_R4A_S2R1_SARAVALI_LINEAGE_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1"
CLASSICAL_SOURCE_OPERATOR_S2R1_R1_LEDGER_CONTRACT = "MO_R4A_S2R1_R1_SARAVALI_ADJUDICATED_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1"
CLASSICAL_SOURCE_OPERATOR_S1R1_PROVENANCE_CONTRACT = "MO_R4A_S1R1_CLASSICAL_SOURCE_OPERATOR_PROVENANCE_HARDENING_V1"
CLASSICAL_SOURCE_OPERATOR_S1R1_R1_PROVENANCE_CONTRACT = "MO_R4A_S1R1_R1_BRIHAT_JATAKA_II13_LOCATOR_CORRECTION_V1"
CLASSICAL_SOURCE_OPERATOR_OUTPUT_CONTRACT = "MO_R4A_S1_CLASSICAL_SOURCE_OPERATOR_OUTPUT_V1"
CLASSICAL_SOURCE_OPERATOR_COVERAGE_CONTRACT = "MO_R4A_S1_REAL_24_SOURCE_OPERATOR_COVERAGE_V1"
CLASSICAL_SOURCE_OPERATOR_S1R1_COVERAGE_CONTRACT = "MO_R4A_S1R1_REAL_24_SOURCE_OPERATOR_COVERAGE_V1"
CLASSICAL_SOURCE_OPERATOR_S1R1_R1_COVERAGE_CONTRACT = "MO_R4A_S1R1_R1_REAL_24_SOURCE_OPERATOR_COVERAGE_V1"
CLASSICAL_SOURCE_OPERATOR_S2R1_COVERAGE_CONTRACT = "MO_R4A_S2R1_REAL_24_SOURCE_OPERATOR_COVERAGE_V1"
CLASSICAL_SOURCE_OPERATOR_S2R1_R1_COVERAGE_CONTRACT = "MO_R4A_S2R1_R1_REAL_24_SOURCE_OPERATOR_COVERAGE_V1"
CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION = 1
_SOURCE_LAYER_LEDGER_CONTRACTS = frozenset(
    {
        CLASSICAL_SOURCE_OPERATOR_S1R1_LEDGER_CONTRACT,
        CLASSICAL_SOURCE_OPERATOR_S1R1_R1_LEDGER_CONTRACT,
        CLASSICAL_SOURCE_OPERATOR_S2R1_LEDGER_CONTRACT,
        CLASSICAL_SOURCE_OPERATOR_S2R1_R1_LEDGER_CONTRACT,
    }
)
_SOURCE_LAYER_COVERAGE_CONTRACTS = frozenset(
    {
        CLASSICAL_SOURCE_OPERATOR_S1R1_COVERAGE_CONTRACT,
        CLASSICAL_SOURCE_OPERATOR_S1R1_R1_COVERAGE_CONTRACT,
        CLASSICAL_SOURCE_OPERATOR_S2R1_COVERAGE_CONTRACT,
        CLASSICAL_SOURCE_OPERATOR_S2R1_R1_COVERAGE_CONTRACT,
    }
)
EXPLORATORY_UNSIGNED_MODE = "EXPLORATORY_UNSIGNED"
UNKNOWN_CURRENCY_DIRECTION = "UNKNOWN_MORE_EVIDENCE_REQUIRED"
NO_MARKET_BRIDGE = "NO_AUTHORIZED_MARKET_BRIDGE"
MAGNITUDE_NOT_CONFIGURED = "MAGNITUDE_NOT_CONFIGURED"
NO_COMPOSITION_CONTRACT = "NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_OPERATOR_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "source_operators"
DEFAULT_LEDGER_PATH = SOURCE_OPERATOR_ROOT / "classical_source_operator_ledger_v1.json"
DEFAULT_S1R1_PROVENANCE_PATH = SOURCE_OPERATOR_ROOT / "classical_source_operator_provenance_hardening_s1r1_v1.json"
DEFAULT_S1R1_R1_CORRECTION_PATH = SOURCE_OPERATOR_ROOT / "classical_source_operator_s1r1_r1_brihat_jataka_ii13_locator_correction_v1.json"
DEFAULT_S2R1_SARAVALI_RECONCILIATION_PATH = (
    SOURCE_OPERATOR_ROOT / "mo_r4a_s2r1_saravali_relationship_lineage_reconciliation_v1.json"
)
DEFAULT_S2R1_LEDGER_PATH = SOURCE_OPERATOR_ROOT / "classical_source_operator_ledger_s2r1_saravali_lineage_v1.json"
DEFAULT_S2R1_R1_ADJUDICATION_PATH = (
    SOURCE_OPERATOR_ROOT / "mo_r4a_s2r1_r1_saravali_relationship_orientation_pagination_adjudication_v1.json"
)
DEFAULT_S2R1_R1_LEDGER_PATH = SOURCE_OPERATOR_ROOT / "classical_source_operator_ledger_s2r1_r1_saravali_adjudicated_v1.json"
DEFAULT_S1R1_R1_COVERAGE_PATH = PROJECT_ROOT / "status" / "audits" / "mo_r4a_s1r1_r1_real_24_source_operator_coverage.json"
DEFAULT_S2R1_COVERAGE_PATH = PROJECT_ROOT / "status" / "audits" / "mo_r4a_s2r1_real_24_source_operator_coverage.json"
DEFAULT_S2R1_R1_COVERAGE_PATH = PROJECT_ROOT / "status" / "audits" / "mo_r4a_s2r1_r1_real_24_source_operator_coverage.json"
DEFAULT_UNRESOLVED_PATH = SOURCE_OPERATOR_ROOT / "source_operator_unresolved_dependencies_v1.json"
DEFAULT_CROSS_TEXT_PATH = SOURCE_OPERATOR_ROOT / "source_operator_cross_text_matrix_v1.json"

_S1R1_PROVENANCE_CHANGE_REASONS = {
    "TRAILOKYA_1972_NATURAL_PLANET_CLASS_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator.",
    "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator.",
    "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1": "Replaces the generic central-audit cross-text claim with separate Brihat Jataka II.18 and Saravali 4.30 root locators.",
    "BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1": "Separates Bhatotpala commentary following Brihat Jataka II.18 from Saravali 4.31 root evidence for the five-state table.",
    "SARAVALI_4_32_ORDINARY_DRSTI_V1": "Binds the Sanskrit root and the known Santhanam translation mismatch separately, while retaining distinct Brihat Jataka and Trailokya corroboration.",
    "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1": "Replaces the cross-text audit summary with distinct Brihat Jataka, Saravali, and retained Trailokya page locators.",
    "TRAILOKYA_1972_DIGNITY_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator.",
    "TRAILOKYA_1972_STHANA_BALA_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator.",
    "TRAILOKYA_1972_STHANA_PHALA_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator.",
    "TRAILOKYA_1972_V166_INDIVIDUAL_MODIFIER_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator.",
    "TRAILOKYA_1972_STHULA_MOTION_CLASS_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator.",
    "BJ_SARAVALI_DIK_BALA_CONDITION_V1": "Replaces the generic central-audit cardinal-strength claim with Brihat Jataka II.19 and Saravali 4.35 root locators.",
    "SARAVALI_POSITIONAL_STRENGTH_COMPONENTS_V1": "Makes the missing individual source locator explicit and retains the record as partial and non-executable.",
    "SARAVALI_NAISARGIKA_STRENGTH_V1": "Removes unsupported cross-text precision and retains the historical source-audit record as partial and non-executable.",
    "TRAILOKYA_1972_GRAHA_LATTA_BOUNDARY_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator without promoting Latta.",
    "TRAILOKYA_1972_ARGHYA_VISWA_BOUNDARY_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator without promoting Arghya.",
    "TRAILOKYA_1972_CONTEXT_RESOLUTION_BOUNDARY_V1": "Converts the existing Trailokya page lock from a prose locator into a structured root/commentary locator.",
}

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
    source_locators = operator.get("sourceLocators")
    if isinstance(source_locators, list) and source_locators:
        if not all(isinstance(locator, dict) for locator in source_locators):
            raise ClassicalSourceOperatorError(f"Invalid structured source locators: {operator['operatorId']}")
        return [dict(locator) for locator in source_locators]
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
    if ledger.get("contract") not in {
        CLASSICAL_SOURCE_OPERATOR_LEDGER_CONTRACT,
        *_SOURCE_LAYER_LEDGER_CONTRACTS,
    }:
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
        if ledger.get("contract") in _SOURCE_LAYER_LEDGER_CONTRACTS:
            _validate_s1r1_source_locators(operator, status)
        if bool(operator["marketDirectionAuthorized"]) or bool(operator["marketMagnitudeAuthorized"]):
            raise ClassicalSourceOperatorError(f"Market authorization is prohibited: {identity[0]}")
        if operator["rootOrCommentary"] == "COMMENTARY_ONLY" and "ROOT" in str(operator["sourceFamily"]):
            raise ClassicalSourceOperatorError(f"Commentary-only operator cannot claim root source family: {identity[0]}")
        if status in {"SOURCE_PARTIAL", "SOURCE_UNRESOLVED", "SOURCE_SILENT"} and (
            bool(operator["modeOneEligible"]) or bool(operator["machineEvaluable"])
        ):
            raise ClassicalSourceOperatorError(f"Unresolved operator cannot claim executable source closure: {identity[0]}")


def _validate_s1r1_source_locators(operator: Mapping[str, Any], status: str) -> None:
    """Require S1R1's source-layer boundary without inventing missing locators."""

    required_fields = {
        "sourceFamily",
        "witnessId",
        "witnessRole",
        "sourceLayer",
        "chapter",
        "verse",
        "printedPage",
        "scanPage",
        "repositoryReference",
        "propositionRole",
        "provenanceStatus",
    }
    locators = operator.get("sourceLocators")
    if not isinstance(locators, list) or not locators:
        raise ClassicalSourceOperatorError(f"S1R1 operator lacks structured source locators: {operator['operatorId']}")
    for locator in locators:
        if not isinstance(locator, dict):
            raise ClassicalSourceOperatorError(f"S1R1 locator is not an object: {operator['operatorId']}")
        missing = required_fields - set(locator)
        if missing:
            raise ClassicalSourceOperatorError(
                f"S1R1 locator lacks fields for {operator['operatorId']}: {sorted(missing)}"
            )
        exact = locator["provenanceStatus"] == "SOURCE_CLOSED_EXACT_PAGE_IMAGE"
        layer = str(locator["sourceLayer"])
        witness = str(locator["witnessId"])
        role = str(locator["propositionRole"])
        if exact and (not str(locator["printedPage"]).strip() or not str(locator["scanPage"]).strip()):
            raise ClassicalSourceOperatorError(f"Exact S1R1 locator lacks page binding: {operator['operatorId']}")
        if exact and (("CENTRAL" in witness and "AUDIT" in witness) or layer == "HISTORICAL_CENTRAL_AUDIT"):
            raise ClassicalSourceOperatorError(
                f"Central-audit history cannot satisfy exact source provenance: {operator['operatorId']}"
            )
        if layer in {"SANTHANAM_TRANSLATION", "SANTHANAM_COMMENTARY"} and "ROOT" in role:
            raise ClassicalSourceOperatorError(
                f"Santhanam layer cannot be relabeled as Saravali root: {operator['operatorId']}"
            )
        if layer == "BHATTOPALA_COMMENTARY" and "BRIHAT_JATAKA_ROOT" in role:
            raise ClassicalSourceOperatorError(
                f"Bhatotpala commentary cannot be relabeled as Brihat Jataka root: {operator['operatorId']}"
            )
    if status.startswith("SOURCE_CLOSED") and not any(
        locator["provenanceStatus"] == "SOURCE_CLOSED_EXACT_PAGE_IMAGE" for locator in locators
    ):
        raise ClassicalSourceOperatorError(f"Source-closed S1R1 operator lacks exact source provenance: {operator['operatorId']}")


def load_source_operator_ledger(path: Path = DEFAULT_LEDGER_PATH) -> dict[str, Any]:
    ledger = _read_json(path, "classical source operator ledger")
    validate_source_operator_ledger(ledger)
    return ledger


def _load_s1r1_provenance_hardening(path: Path) -> dict[str, Any]:
    hardening = _read_json(path, "S1R1 source provenance hardening")
    if hardening.get("contract") != CLASSICAL_SOURCE_OPERATOR_S1R1_PROVENANCE_CONTRACT:
        raise ClassicalSourceOperatorError("Unsupported S1R1 source provenance hardening contract")
    records = hardening.get("operatorProvenance")
    if not isinstance(records, list) or len(records) != 17:
        raise ClassicalSourceOperatorError("S1R1 provenance hardening requires exactly 17 operator records")
    identities = [(record.get("operatorId"), record.get("operatorVersion")) for record in records]
    if len(set(identities)) != len(identities):
        raise ClassicalSourceOperatorError("S1R1 provenance hardening contains duplicate operator identities")
    return hardening


def _load_s1r1_r1_locator_correction(path: Path) -> dict[str, Any]:
    correction = _read_json(path, "S1R1-R1 Bṛhat Jātaka II.13 locator correction")
    if correction.get("contract") != CLASSICAL_SOURCE_OPERATOR_S1R1_R1_PROVENANCE_CONTRACT:
        raise ClassicalSourceOperatorError("Unsupported S1R1-R1 locator correction contract")
    if correction.get("schemaVersion") != CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION:
        raise ClassicalSourceOperatorError("Unsupported S1R1-R1 locator correction version")
    if correction.get("milestone") != "MO-R4A-S1R1-R1":
        raise ClassicalSourceOperatorError("S1R1-R1 locator correction has an unexpected milestone")
    if not str(correction.get("baseS1R1LedgerCanonicalHash", "")):
        raise ClassicalSourceOperatorError("S1R1-R1 locator correction lacks its S1R1 base ledger hash")
    witness = correction.get("sourceWitness")
    if not isinstance(witness, dict) or not witness.get("witnessId") or not witness.get("artifactSha256"):
        raise ClassicalSourceOperatorError("S1R1-R1 locator correction lacks its verified source witness")
    findings = correction.get("sourceVerification", {}).get("pageFindings")
    if findings != [
        {"scanPage": "43", "printedPage": "31"},
        {"scanPage": "44", "printedPage": "32"},
    ]:
        raise ClassicalSourceOperatorError("S1R1-R1 locator correction has unexpected page verification findings")
    corrections = correction.get("corrections")
    expected_ids = {
        "SARAVALI_4_32_ORDINARY_DRSTI_V1",
        "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1",
    }
    if not isinstance(corrections, list) or len(corrections) != len(expected_ids):
        raise ClassicalSourceOperatorError("S1R1-R1 locator correction must contain exactly two corrections")
    identities = {item.get("operatorId") for item in corrections if isinstance(item, dict)}
    if identities != expected_ids:
        raise ClassicalSourceOperatorError("S1R1-R1 locator correction IDs do not match the affected operators")
    for item in corrections:
        if item.get("operatorVersion") != "1":
            raise ClassicalSourceOperatorError("S1R1-R1 locator correction only supports operator version 1")
        if not isinstance(item.get("priorLocator"), dict) or not isinstance(item.get("correctedLocator"), dict):
            raise ClassicalSourceOperatorError("S1R1-R1 locator correction requires prior and corrected locators")
        if item["priorLocator"].get("sourceFamily") != "BRIHAT_JATAKA":
            raise ClassicalSourceOperatorError("S1R1-R1 correction may only target the Bṛhat Jātaka locator")
        if item["correctedLocator"].get("sourceFamily") != "BRIHAT_JATAKA":
            raise ClassicalSourceOperatorError("S1R1-R1 correction must retain the Bṛhat Jātaka source family")
        if item["correctedLocator"].get("printedPage") != "31-32" or item["correctedLocator"].get("scanPage") != "43-44":
            raise ClassicalSourceOperatorError("S1R1-R1 correction must bind printed pp.31-32 to scan pp.43-44")
    return correction


def build_s1r1_provenance_hardened_ledger(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Bind the historical S1 ledger to S1R1 provenance without changing source rules."""

    root = Path(resource_root).resolve()
    base = load_source_operator_ledger(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_LEDGER_PATH.name
    )
    hardening = _load_s1r1_provenance_hardening(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_S1R1_PROVENANCE_PATH.name
    )
    expected_base_hash = str(hardening.get("baseLedgerCanonicalHash", ""))
    actual_base_hash = _canonical_hash(base)
    if expected_base_hash != actual_base_hash:
        raise ClassicalSourceOperatorError("S1R1 provenance hardening is not bound to the historical S1 ledger hash")

    hardened = deepcopy(base)
    hardened.update(
        {
            "contract": CLASSICAL_SOURCE_OPERATOR_S1R1_LEDGER_CONTRACT,
            "ledgerId": "CLASSICAL_SOURCE_OPERATOR_LEDGER_S1R1_V1",
            "milestone": "MO-R4A-S1R1",
            "sourceAuditStatus": "PROVENANCE_HARDENED_FOR_MO_R4A_S1R1_INPUT",
            "provenanceHardening": {
                "contract": hardening["contract"],
                "baseLedgerCanonicalHash": expected_base_hash,
                "historicalS1LedgerPreserved": True,
            },
        }
    )
    by_identity = {
        (str(operator["operatorId"]), str(operator["operatorVersion"])): operator
        for operator in hardened["operators"]
    }
    for record in hardening["operatorProvenance"]:
        identity = (str(record["operatorId"]), str(record["operatorVersion"]))
        target = by_identity.get(identity)
        if target is None:
            raise ClassicalSourceOperatorError(f"S1R1 provenance references unknown operator: {identity}")
        if target["sourceStatus"] != record["sourceStatusBefore"]:
            raise ClassicalSourceOperatorError(f"S1R1 provenance source-status baseline mismatch: {identity[0]}")
        target.update(record["operatorPatch"])
        if target["sourceStatus"] != record["sourceStatusAfter"]:
            raise ClassicalSourceOperatorError(f"S1R1 provenance source-status patch mismatch: {identity[0]}")
    if set(by_identity) != {
        (str(record["operatorId"]), str(record["operatorVersion"]))
        for record in hardening["operatorProvenance"]
    }:
        raise ClassicalSourceOperatorError("S1R1 provenance does not cover every S1 operator")
    validate_source_operator_ledger(hardened)
    return hardened


def build_s1r1_r1_corrected_ledger(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Apply only the verified II.13 page-pair correction to the S1R1 successor."""

    root = Path(resource_root).resolve()
    s1r1 = build_s1r1_provenance_hardened_ledger(root)
    correction = _load_s1r1_r1_locator_correction(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_S1R1_R1_CORRECTION_PATH.name
    )
    expected_base_hash = str(correction["baseS1R1LedgerCanonicalHash"])
    actual_base_hash = _canonical_hash(s1r1)
    if expected_base_hash != actual_base_hash:
        raise ClassicalSourceOperatorError("S1R1-R1 locator correction is not bound to the pre-correction S1R1 ledger hash")

    corrected = deepcopy(s1r1)
    corrected.update(
        {
            "contract": CLASSICAL_SOURCE_OPERATOR_S1R1_R1_LEDGER_CONTRACT,
            "ledgerId": "CLASSICAL_SOURCE_OPERATOR_LEDGER_S1R1_R1_V1",
            "milestone": "MO-R4A-S1R1-R1",
            "sourceAuditStatus": "BRIHAT_JATAKA_II13_LOCATOR_CORRECTED_FOR_MO_R4A_S1R1_R1_INPUT",
            "provenanceHardening": {
                "contract": correction["contract"],
                "baseS1R1LedgerCanonicalHash": expected_base_hash,
                "historicalS1LedgerCanonicalHash": s1r1["provenanceHardening"]["baseLedgerCanonicalHash"],
                "historicalS1LedgerPreserved": True,
                "preCorrectionS1R1Preserved": True,
                "correctionCount": len(correction["corrections"]),
            },
        }
    )
    by_identity = {
        (str(operator["operatorId"]), str(operator["operatorVersion"])): operator
        for operator in corrected["operators"]
    }
    for item in correction["corrections"]:
        identity = (str(item["operatorId"]), str(item["operatorVersion"]))
        target = by_identity.get(identity)
        if target is None:
            raise ClassicalSourceOperatorError(f"S1R1-R1 correction references unknown operator: {identity}")
        locators = target.get("sourceLocators")
        if not isinstance(locators, list):
            raise ClassicalSourceOperatorError(f"S1R1-R1 target lacks structured locators: {identity[0]}")
        matches = [index for index, locator in enumerate(locators) if locator == item["priorLocator"]]
        if len(matches) != 1:
            raise ClassicalSourceOperatorError(
                f"S1R1-R1 correction expected one exact prior locator for {identity[0]}, found {len(matches)}"
            )
        locators[matches[0]] = deepcopy(item["correctedLocator"])
        prior_text = item.get("priorVerseOrLocator")
        corrected_text = item.get("correctedVerseOrLocator")
        if prior_text is not None or corrected_text is not None:
            if target["verseOrLocator"] != prior_text:
                raise ClassicalSourceOperatorError(f"S1R1-R1 prose locator baseline mismatch: {identity[0]}")
            target["verseOrLocator"] = corrected_text
    if set(by_identity) != {
        (str(operator["operatorId"]), str(operator["operatorVersion"]))
        for operator in s1r1["operators"]
    }:
        raise ClassicalSourceOperatorError("S1R1-R1 correction changed the operator identity set")
    validate_source_operator_ledger(corrected)
    return corrected


def _load_s2r1_saravali_relationship_source(path: Path) -> dict[str, Any]:
    """Load the page-image-derived Saravali relationship closure, never a substitute text."""

    source = _read_json(path, "S2R1 Saravali relationship source closure")
    if source.get("contract") != "MO_R4A_S2R1_SARAVALI_NATURAL_RELATIONSHIP_SOURCE_CLOSURE_V1":
        raise ClassicalSourceOperatorError("Unsupported S2R1 Saravali relationship source closure contract")
    if source.get("schemaVersion") != CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION:
        raise ClassicalSourceOperatorError("Unsupported S2R1 Saravali relationship source closure version")
    witness = source.get("saravaliWitness")
    if not isinstance(witness, dict) or (
        witness.get("witnessId"),
        witness.get("artifactSha256"),
    ) != (
        "SARAVALI_RANJAN_SANTHANAM_1983_HELD_PARTIAL",
        "3BFD4F7F717798F87B7EFD6FA5A3DE2E28E7E09FC2520F0F05AE12B2E1BF9A58",
    ):
        raise ClassicalSourceOperatorError("S2R1 Saravali closure is not bound to the verified held witness")
    if witness.get("sourceBytesTracked") is not False:
        raise ClassicalSourceOperatorError("S2R1 Saravali source bytes must remain outside the repository")
    operator = source.get("saravaliNaturalRelationshipOperator")
    if not isinstance(operator, dict) or operator.get("operatorId") != "SARAVALI_NATURAL_RELATIONSHIP_V1":
        raise ClassicalSourceOperatorError("S2R1 Saravali closure lacks its natural-relationship operator")
    required_locator_layers = {"SARAVALI_ROOT", "SANTHANAM_TRANSLATION"}
    locators = operator.get("sourceLocators")
    if not isinstance(locators, list) or {item.get("sourceLayer") for item in locators if isinstance(item, dict)} != required_locator_layers:
        raise ClassicalSourceOperatorError("S2R1 Saravali relationship must retain separate root and translation locators")
    root_locators = [item for item in locators if item.get("sourceLayer") == "SARAVALI_ROOT"]
    if len(root_locators) != 1 or (
        root_locators[0].get("chapter"),
        root_locators[0].get("verse"),
        root_locators[0].get("printedPage"),
        root_locators[0].get("scanPage"),
        root_locators[0].get("provenanceStatus"),
    ) != ("4", "28-29", "56", "60", "SOURCE_CLOSED_EXACT_PAGE_IMAGE"):
        raise ClassicalSourceOperatorError("S2R1 Saravali root relationship locator is not the verified page-image binding")
    translation = [item for item in locators if item.get("sourceLayer") == "SANTHANAM_TRANSLATION"]
    if len(translation) != 1 or "ROOT" in str(translation[0].get("propositionRole", "")):
        raise ClassicalSourceOperatorError("S2R1 Saravali translation cannot substitute for the Sanskrit root")
    if any(item.get("sourceLayer") == "SANTHANAM_COMMENTARY" for item in locators):
        raise ClassicalSourceOperatorError("S2R1 Saravali relationship closure cannot substitute commentary for the root")
    matrix = operator.get("rule", {}).get("friendshipMatrix")
    if not isinstance(matrix, dict) or set(matrix) != RELATIONSHIP_BODIES:
        raise ClassicalSourceOperatorError("S2R1 Saravali relationship matrix must close exactly the seven source bodies")
    for body, row in matrix.items():
        if not isinstance(row, dict) or set(row) != {"friends", "neutral", "enemies"}:
            raise ClassicalSourceOperatorError(f"S2R1 Saravali relationship row is invalid: {body}")
        members = [member for category in ("friends", "neutral", "enemies") for member in row[category]]
        if body in members or len(members) != 6 or set(members) != RELATIONSHIP_BODIES - {body}:
            raise ClassicalSourceOperatorError(f"S2R1 Saravali relationship row is not a closed non-self partition: {body}")
    return source


def build_s2r1_saravali_lineage_ledger(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Append the verified Saravali root matrix without mutating prior ledgers."""

    root = Path(resource_root).resolve()
    historical = build_s1r1_r1_corrected_ledger(root)
    source = _load_s2r1_saravali_relationship_source(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_S2R1_SARAVALI_RECONCILIATION_PATH.name
    )
    expected_historical_hash = str(source.get("historicalS1R1R1LedgerCanonicalHash", ""))
    actual_historical_hash = _canonical_hash(historical)
    if expected_historical_hash != actual_historical_hash:
        raise ClassicalSourceOperatorError("S2R1 Saravali closure is not bound to the final historical source ledger")

    successor = deepcopy(historical)
    successor.update(
        {
            "contract": CLASSICAL_SOURCE_OPERATOR_S2R1_LEDGER_CONTRACT,
            "ledgerId": "CLASSICAL_SOURCE_OPERATOR_LEDGER_S2R1_SARAVALI_LINEAGE_V1",
            "milestone": "MO-R4A-S2R1",
            "sourceAuditStatus": "SARAVALI_NATURAL_RELATIONSHIP_ROOT_CLOSED_LINEAGE_RECONCILED",
            "sourceLineageReconciliation": {
                "contract": source["contract"],
                "historicalS1R1R1LedgerCanonicalHash": actual_historical_hash,
                "saravaliWitnessId": source["saravaliWitness"]["witnessId"],
                "saravaliWitnessSha256": source["saravaliWitness"]["artifactSha256"],
                "branchTaken": "B",
                "historicalLedgerPreserved": True,
                "saravaliNaturalRelationshipAdded": True,
            },
        }
    )
    if any(item.get("operatorId") == "SARAVALI_NATURAL_RELATIONSHIP_V1" for item in successor["operators"]):
        raise ClassicalSourceOperatorError("S2R1 successor cannot overwrite an existing Saravali natural-relationship operator")
    successor["operators"].append(deepcopy(source["saravaliNaturalRelationshipOperator"]))
    validate_source_operator_ledger(successor)
    return successor


def _load_s2r1_r1_saravali_adjudication(path: Path) -> dict[str, Any]:
    """Load the direct-page-image Saravali orientation and pagination adjudication."""

    source = _read_json(path, "S2R1-R1 Saravali orientation adjudication")
    if source.get("contract") != "MO_R4A_S2R1_R1_SARAVALI_RELATIONSHIP_ORIENTATION_PAGINATION_ADJUDICATION_V1":
        raise ClassicalSourceOperatorError("Unsupported S2R1-R1 Saravali adjudication contract")
    if source.get("schemaVersion") != CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION:
        raise ClassicalSourceOperatorError("Unsupported S2R1-R1 Saravali adjudication version")
    if source.get("branchTaken") != "B" or source.get("sourceDoctrineChanged") is not False:
        raise ClassicalSourceOperatorError("S2R1-R1 Saravali adjudication has an unsupported source branch")
    witness = source.get("saravaliWitness")
    if not isinstance(witness, Mapping) or (
        witness.get("witnessId"),
        witness.get("artifactSha256"),
        witness.get("sourceBytesTracked"),
        witness.get("verificationMethod"),
    ) != (
        "SARAVALI_RANJAN_SANTHANAM_1983_HELD_PARTIAL",
        "3BFD4F7F717798F87B7EFD6FA5A3DE2E28E7E09FC2520F0F05AE12B2E1BF9A58",
        False,
        "DIRECT_PAGE_IMAGE_INSPECTION_TWO_PASS",
    ):
        raise ClassicalSourceOperatorError("S2R1-R1 adjudication is not bound to the verified held witness")
    page_records = source.get("pageRecords")
    expected_pages = {
        ("60", "56"): {"28", "29", "30"},
        ("61", "57"): {"30", "31", "32", "33"},
        ("62", "58"): {"32", "33", "34", "35"},
    }
    actual_pages = {
        (str(record.get("pdfImage")), str(record.get("visiblePrintedPage"))): set(record.get("versesPresent", []))
        for record in page_records if isinstance(record, Mapping)
    } if isinstance(page_records, list) else {}
    if actual_pages != expected_pages:
        raise ClassicalSourceOperatorError("S2R1-R1 Saravali page-image pagination is not exact")
    separation = source.get("rootTranslationCommentarySeparation")
    if not isinstance(separation, Mapping) or (
        separation.get("rootControlsNaturalRelationship"),
        separation.get("translationRole"),
        separation.get("commentaryUsedToResolveRelationshipOrientation"),
    ) != (
        True,
        "SEPARATE_LEXICAL_CROSS_CHECK_NOT_GRAMMATICAL_SUBSTITUTE",
        False,
    ):
        raise ClassicalSourceOperatorError("S2R1-R1 adjudication collapses root, translation, or commentary")
    neutrality = source.get("neutralityRule")
    if not isinstance(neutrality, Mapping) or (
        neutrality.get("sourceLayer"),
        neutrality.get("verse"),
        neutrality.get("directOrInferred"),
        neutrality.get("machineExecutable"),
    ) != ("SARAVALI_ROOT", "29", "EXPLICIT_ROOT_RULE", True):
        raise ClassicalSourceOperatorError("S2R1-R1 neutrality rule is not source-closed in the root")
    matrix = source.get("adjudicatedMatrix")
    if not isinstance(matrix, Mapping) or set(matrix) != RELATIONSHIP_BODIES:
        raise ClassicalSourceOperatorError("S2R1-R1 Saravali matrix does not close the seven source bodies")
    for body, row in matrix.items():
        if not isinstance(row, Mapping) or set(row) != {"friends", "neutral", "enemies"}:
            raise ClassicalSourceOperatorError(f"S2R1-R1 Saravali matrix row is invalid: {body}")
        members = [member for category in ("friends", "neutral", "enemies") for member in row[category]]
        if body in members or len(members) != 6 or set(members) != RELATIONSHIP_BODIES - {body}:
            raise ClassicalSourceOperatorError(f"S2R1-R1 Saravali matrix row is not a closed non-self partition: {body}")
    mandatory = source.get("orientationEvidence", {}).get("mandatoryCells")
    expected_mandatory = {
        ("MARS", "MERCURY", "ENEMY"),
        ("MERCURY", "MARS", "ENEMY"),
        ("MERCURY", "MOON", "ENEMY"),
        ("MOON", "MERCURY", "FRIEND"),
    }
    actual_mandatory = {
        (str(row.get("sourceBody")), str(row.get("targetBody")), str(row.get("state")))
        for row in mandatory if isinstance(row, Mapping)
    } if isinstance(mandatory, list) else set()
    if actual_mandatory != expected_mandatory:
        raise ClassicalSourceOperatorError("S2R1-R1 mandatory Mercury/Mars/Moon cells are not independently recorded")
    corrections = source.get("paginationCorrections")
    expected_corrections = {
        ("SARAVALI_4_32_ORDINARY_DRSTI_V1", "SARAVALI_ROOT", "32-33", "57", "61"),
        ("CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1", "SARAVALI_ROOT", "32-33", "57", "61"),
    }
    actual_corrections = {
        (
            str(row.get("operatorId")),
            str(row.get("sourceLayer")),
            str(row.get("verse")),
            str(row.get("adjudicated", {}).get("printedPage")),
            str(row.get("adjudicated", {}).get("scanPage")),
        )
        for row in corrections if isinstance(row, Mapping)
    } if isinstance(corrections, list) else set()
    if actual_corrections != expected_corrections:
        raise ClassicalSourceOperatorError("S2R1-R1 Saravali pagination corrections are incomplete")
    return source


def _relationship_matrix_state(matrix: Mapping[str, Any], source: str, target: str) -> str:
    if source == target:
        return "UNKNOWN"
    row = matrix[source]
    for state, category in (("FRIEND", "friends"), ("NEUTRAL", "neutral"), ("ENEMY", "enemies")):
        if target in row[category]:
            return state
    raise ClassicalSourceOperatorError(f"Saravali adjudication lacks a state for {source} -> {target}")


def _replace_saravali_root_locator(
    operator: dict[str, Any],
    *,
    verse: str,
    printed_page: str,
    scan_page: str,
) -> None:
    root_locators = [
        locator for locator in operator["sourceLocators"]
        if locator.get("sourceLayer") == "SARAVALI_ROOT" and locator.get("verse") == verse
    ]
    if len(root_locators) != 1:
        raise ClassicalSourceOperatorError(f"S2R1-R1 cannot identify one Saravali root locator for {operator['operatorId']}")
    locator = root_locators[0]
    if (locator.get("printedPage"), locator.get("scanPage")) != ("58", "62"):
        raise ClassicalSourceOperatorError(f"S2R1-R1 pagination baseline mismatch for {operator['operatorId']}")
    locator["printedPage"] = printed_page
    locator["scanPage"] = scan_page
    locator["repositoryReference"] = (
        "MO-R4A-S2R1-R1 direct page-image adjudication; Sanskrit root is printed p.57 / PDF image 61; "
        "source bytes are not tracked"
    )


def build_s2r1_r1_saravali_adjudicated_ledger(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Create the S2R1-R1 successor without mutating the historical S2R1 ledger."""

    root = Path(resource_root).resolve()
    historical = build_s2r1_saravali_lineage_ledger(root)
    source = _load_s2r1_r1_saravali_adjudication(
        root / "configs" / "research" / "machine_interpretation" / "source_operators" / DEFAULT_S2R1_R1_ADJUDICATION_PATH.name
    )
    expected_historical_hash = str(source.get("historicalS2R1", {}).get("ledgerHash", ""))
    if expected_historical_hash != _canonical_hash(historical):
        raise ClassicalSourceOperatorError("S2R1-R1 adjudication is not bound to immutable historical S2R1")
    successor = deepcopy(historical)
    successor.update(
        {
            "contract": CLASSICAL_SOURCE_OPERATOR_S2R1_R1_LEDGER_CONTRACT,
            "ledgerId": "CLASSICAL_SOURCE_OPERATOR_LEDGER_S2R1_R1_SARAVALI_ADJUDICATED_V1",
            "milestone": "MO-R4A-S2R1-R1",
            "sourceAuditStatus": "SARAVALI_RELATIONSHIP_ORIENTATION_AND_PAGINATION_ADJUDICATED",
            "sourceLineageReconciliation": {
                **deepcopy(historical["sourceLineageReconciliation"]),
                "adjudicationContract": source["contract"],
                "historicalS2R1LedgerCanonicalHash": _canonical_hash(historical),
                "branchTaken": source["branchTaken"],
                "relationshipOrientationDurablyClosed": True,
                "printedPaginationDurablyClosed": True,
                "sourceDoctrineChanged": False,
                "evaluatorMathematicsChanged": False,
            },
        }
    )
    by_id = {operator["operatorId"]: operator for operator in successor["operators"]}
    natural = by_id.get("SARAVALI_NATURAL_RELATIONSHIP_V1")
    if natural is None:
        raise ClassicalSourceOperatorError("S2R1-R1 successor lacks Saravali natural relationship")
    natural["rule"]["friendshipMatrix"] = deepcopy(source["adjudicatedMatrix"])
    natural["directSourceClaim"] = (
        "The Sanskrit root directly closes the directed seven-planet natural relationship matrix under the "
        "source-body-to-target orientation adjudicated in MO-R4A-S2R1-R1. A body neither named friend nor "
        "enemy is neutral; self and node relationships are not stated."
    )
    natural["sourceLocators"][0]["repositoryReference"] = (
        "MO-R4A-S2R1-R1 direct page-image orientation adjudication; source bytes are not tracked"
    )
    for operator_id in ("SARAVALI_4_32_ORDINARY_DRSTI_V1", "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1"):
        _replace_saravali_root_locator(by_id[operator_id], verse="32-33", printed_page="57", scan_page="61")
        by_id[operator_id]["verseOrLocator"] = by_id[operator_id]["verseOrLocator"].replace(
            "Saravali 4.32-33 Sanskrit root, printed p.58 / scan p.62",
            "Saravali 4.32-33 Sanskrit root, printed p.57 / scan p.61",
        ).replace(
            "Saravali 4.32-33, printed p.58 / scan p.62",
            "Saravali 4.32-33, printed p.57 / scan p.61",
        )
    validate_source_operator_ledger(successor)
    return successor


def build_s1r1_source_provenance_audit(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Render all 17 historical-to-hardened provenance changes as an audit record."""

    root = Path(resource_root).resolve()
    baseline = load_source_operator_ledger(
        root / "configs" / "research" / "machine_interpretation" / "source_operators" / DEFAULT_LEDGER_PATH.name
    )
    hardening = _load_s1r1_provenance_hardening(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_S1R1_PROVENANCE_PATH.name
    )
    hardened = build_s1r1_provenance_hardened_ledger(root)
    baseline_by_identity = {
        (str(operator["operatorId"]), str(operator["operatorVersion"])): operator
        for operator in baseline["operators"]
    }
    hardened_by_identity = {
        (str(operator["operatorId"]), str(operator["operatorVersion"])): operator
        for operator in hardened["operators"]
    }
    rows: list[dict[str, Any]] = []
    for record in hardening["operatorProvenance"]:
        identity = (str(record["operatorId"]), str(record["operatorVersion"]))
        previous = baseline_by_identity[identity]
        current = hardened_by_identity[identity]
        locators = deepcopy(current["sourceLocators"])
        rows.append(
            {
                "operatorId": identity[0],
                "operatorVersion": identity[1],
                "previousSourceLocator": previous["verseOrLocator"],
                "previousSourceLayer": previous["rootOrCommentary"],
                "newSourceLocators": locators,
                "sourceLayers": sorted({str(locator["sourceLayer"]) for locator in locators}),
                "witnessIds": sorted({str(locator["witnessId"]) for locator in locators}),
                "sourceStatusBefore": record["sourceStatusBefore"],
                "sourceStatusAfter": record["sourceStatusAfter"],
                "reasonForChange": _S1R1_PROVENANCE_CHANGE_REASONS[identity[0]],
                "evaluatorMathematicsChanged": False,
                "eventOutputSemanticsChanged": False,
            }
        )
    if set(_S1R1_PROVENANCE_CHANGE_REASONS) != set(item["operatorId"] for item in rows):
        raise ClassicalSourceOperatorError("S1R1 provenance audit reasons do not cover every operator")
    return {
        "contract": "MO_R4A_S1R1_SOURCE_PROVENANCE_AUDIT_V1",
        "schemaVersion": 1,
        "milestone": "MO-R4A-S1R1",
        "historicalS1LedgerCanonicalHash": _canonical_hash(baseline),
        "provenanceHardenedLedgerCanonicalHash": _canonical_hash(hardened),
        "operatorCount": len(rows),
        "historicalS1LedgerPreserved": True,
        "rows": rows,
        "summary": {
            "evaluatorMathematicsChanged": False,
            "eventOutputSemanticsChanged": False,
            "sourceClosedExactLocatorCount": sum(
                1
                for row in rows
                for locator in row["newSourceLocators"]
                if locator["provenanceStatus"] == "SOURCE_CLOSED_EXACT_PAGE_IMAGE"
            ),
            "explicitlyUnboundLocatorCount": sum(
                1
                for row in rows
                for locator in row["newSourceLocators"]
                if locator["provenanceStatus"] == "EXACT_SOURCE_LOCATOR_NOT_DURABLY_BOUND"
            ),
        },
    }


def build_s1r1_r1_source_provenance_audit(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Audit the two source-locator changes from S1R1 to S1R1-R1."""

    root = Path(resource_root).resolve()
    correction = _load_s1r1_r1_locator_correction(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_S1R1_R1_CORRECTION_PATH.name
    )
    before = build_s1r1_provenance_hardened_ledger(root)
    after = build_s1r1_r1_corrected_ledger(root)
    before_by_identity = {
        (str(operator["operatorId"]), str(operator["operatorVersion"])): operator
        for operator in before["operators"]
    }
    after_by_identity = {
        (str(operator["operatorId"]), str(operator["operatorVersion"])): operator
        for operator in after["operators"]
    }
    if set(before_by_identity) != set(after_by_identity) or len(after_by_identity) != 17:
        raise ClassicalSourceOperatorError("S1R1-R1 provenance audit changed the 17-operator identity set")

    rows: list[dict[str, Any]] = []
    for item in correction["corrections"]:
        identity = (str(item["operatorId"]), str(item["operatorVersion"]))
        previous = before_by_identity[identity]
        current = after_by_identity[identity]
        previous_non_provenance = deepcopy(previous)
        current_non_provenance = deepcopy(current)
        previous_non_provenance.pop("sourceLocators", None)
        current_non_provenance.pop("sourceLocators", None)
        previous_non_provenance.pop("verseOrLocator", None)
        current_non_provenance.pop("verseOrLocator", None)
        if previous_non_provenance != current_non_provenance:
            raise ClassicalSourceOperatorError(f"S1R1-R1 changed non-provenance operator data: {identity[0]}")
        rows.append(
            {
                "operatorId": identity[0],
                "operatorVersion": identity[1],
                "sourceStatusBefore": previous["sourceStatus"],
                "sourceStatusAfter": current["sourceStatus"],
                "priorLocator": deepcopy(item["priorLocator"]),
                "correctedLocator": deepcopy(item["correctedLocator"]),
                "priorVerseOrLocator": previous["verseOrLocator"],
                "correctedVerseOrLocator": current["verseOrLocator"],
                "changedFields": [
                    "sourceLocators",
                    *( ["verseOrLocator"] if previous["verseOrLocator"] != current["verseOrLocator"] else [] ),
                ],
                "rootCommentarySeparated": bool(correction["sourceVerification"]["rootCommentarySeparated"]),
                "evaluatorMathematicsChanged": False,
                "eventOutputSemanticsChanged": False,
            }
        )
    return {
        "contract": "MO_R4A_S1R1_R1_SOURCE_PROVENANCE_AUDIT_V1",
        "schemaVersion": 1,
        "milestone": "MO-R4A-S1R1-R1",
        "sourceWitness": deepcopy(correction["sourceWitness"]),
        "sourceVerification": deepcopy(correction["sourceVerification"]),
        "preCorrectionS1R1LedgerCanonicalHash": _canonical_hash(before),
        "correctedS1R1R1LedgerCanonicalHash": _canonical_hash(after),
        "operatorCount": len(after_by_identity),
        "affectedOperatorCount": len(rows),
        "historicalS1R1AuditPreserved": True,
        "rows": rows,
        "summary": {
            "allOperatorIdentitiesUnchanged": True,
            "allOtherOperatorFieldsUnchanged": True,
            "changedFieldsRestrictedToSourceProvenance": True,
            "evaluatorMathematicsChanged": False,
            "eventOutputSemanticsChanged": False,
            "rootCommentarySeparated": False,
            "correctionStatus": "LOCATOR_CORRECTION_COMPLETE_CENTRAL_REVIEW_REQUIRED",
        },
    }


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


def evaluate_saravali_natural_relationship(
    source_body: str,
    target_body: str,
    *,
    ledger: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate only the root-bound Saravali 4.28-29 seven-planet matrix."""

    source_ledger = ledger or build_s2r1_saravali_lineage_ledger()
    operator = _operator(source_ledger, "SARAVALI_NATURAL_RELATIONSHIP_V1")
    source = _body(source_body, "Saravali relationship source body")
    target = _body(target_body, "Saravali relationship target body")
    snapshot = {"sourceBody": source, "targetBody": target}
    if source not in RELATIONSHIP_BODIES or target not in RELATIONSHIP_BODIES:
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_SARAVALI",),
            explanation="Saravali 4.28-29 closes no natural-relationship cell for nodes or other unsupported bodies.",
            conditions_missing=("CLASSICAL_SEVEN_PLANET_RELATIONSHIP_INPUT",),
        )
    if source == target:
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("SARAVALI_SELF_RELATIONSHIP_NOT_STATED",),
            explanation="Saravali 4.28-29 does not state a natural self-relationship; it is not normalized to neutrality.",
        )
    row = operator["rule"]["friendshipMatrix"][source]
    if target in row["friends"]:
        state = "FRIEND"
    elif target in row["neutral"]:
        state = "NEUTRAL"
    elif target in row["enemies"]:
        state = "ENEMY"
    else:  # The source-closure validator above makes this branch fail-closed only.
        return _unresolved_output(
            operator,
            input_snapshot=snapshot,
            output_state="UNKNOWN",
            dependencies=("SARAVALI_RELATIONSHIP_CELL_NOT_SOURCE_CLOSED",),
            explanation="No admitted Saravali relationship cell covers this body pair.",
        )
    return _source_output(
        operator,
        input_snapshot=snapshot,
        output_state=state,
        explanation=f"Saravali 4.28-29 gives the source-specific natural relationship {source} to {target} as {state}.",
        conditions_satisfied=("SARAVALI_4_28_TO_4_29_SEVEN_PLANET_MATRIX",),
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
    uses_saravali_relationship_lineage = ledger.get("contract") in {
        CLASSICAL_SOURCE_OPERATOR_S2R1_LEDGER_CONTRACT,
        CLASSICAL_SOURCE_OPERATOR_S2R1_R1_LEDGER_CONTRACT,
    }
    relationship = (
        evaluate_saravali_natural_relationship(transit, natal, ledger=ledger)
        if uses_saravali_relationship_lineage
        else evaluate_trailokya_natural_relationship(transit, natal, ledger=ledger)
    )
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
        "SARAVALI_NATURAL_RELATIONSHIP_V1"
        if uses_saravali_relationship_lineage
        else "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1",
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


def build_real_source_operator_coverage_report(
    resource_root: Path = PROJECT_ROOT,
    *,
    source_ledger: Mapping[str, Any] | None = None,
    milestone: str = "MO-R4A-S1",
    coverage_contract: str = CLASSICAL_SOURCE_OPERATOR_COVERAGE_CONTRACT,
) -> dict[str, Any]:
    """Bind source operators to frozen identities without reading review or market data."""

    root = Path(resource_root).resolve()
    ledger = source_ledger or load_source_operator_ledger(
        root
        / "configs"
        / "research"
        / "machine_interpretation"
        / "source_operators"
        / DEFAULT_LEDGER_PATH.name
    )
    validate_source_operator_ledger(ledger)
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
        "contract": coverage_contract,
        "schemaVersion": CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION,
        "milestone": milestone,
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


def _coverage_events(coverage: Mapping[str, Any]) -> list[dict[str, Any]]:
    sides = coverage.get("sides")
    if not isinstance(sides, list):
        raise ClassicalSourceOperatorError("Source coverage lacks sides")
    events = [event for side in sides for event in side.get("events", [])]
    if len(events) != 24:
        raise ClassicalSourceOperatorError("Source coverage must contain exactly 24 frozen events")
    return events


def build_s2r1_relationship_matrix_comparison(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Compare full directed seven-planet matrices without collapsing self pairs."""

    root = Path(resource_root).resolve()
    historical = build_s1r1_r1_corrected_ledger(root)
    successor = build_s2r1_saravali_lineage_ledger(root)
    ordered_bodies = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")
    rows: list[dict[str, Any]] = []
    for source in ordered_bodies:
        for target in ordered_bodies:
            historical_output = evaluate_trailokya_natural_relationship(source, target, ledger=historical)
            saravali_output = evaluate_saravali_natural_relationship(source, target, ledger=successor)
            if source == target:
                relationship_status = "NOT_COMPARABLE"
                reason = "Neither source contract states a self-relationship; both remain UNKNOWN."
            elif historical_output["outputState"] == saravali_output["outputState"]:
                relationship_status = "AGREEMENT"
                reason = "Both source-specific directed cells have the same categorical state."
            else:
                relationship_status = "CONFLICT"
                reason = "The two source-specific directed cells differ and remain separately recorded."
            rows.append(
                {
                    "sourceBody": source,
                    "targetBody": target,
                    "historicalTrailokyaState": historical_output["outputState"],
                    "saravaliState": saravali_output["outputState"],
                    "relationshipStatus": relationship_status,
                    "reason": reason,
                }
            )
    statuses = [row["relationshipStatus"] for row in rows]
    if statuses.count("AGREEMENT") != 41 or statuses.count("CONFLICT") != 1 or statuses.count("NOT_COMPARABLE") != 7:
        raise ClassicalSourceOperatorError("Saravali/Trailokya matrix comparison has unexpected lineage results")
    conflict = next(row for row in rows if row["relationshipStatus"] == "CONFLICT")
    if conflict != {
        "sourceBody": "MERCURY",
        "targetBody": "MARS",
        "historicalTrailokyaState": "NEUTRAL",
        "saravaliState": "ENEMY",
        "relationshipStatus": "CONFLICT",
        "reason": "The two source-specific directed cells differ and remain separately recorded.",
    }:
        raise ClassicalSourceOperatorError("Saravali/Trailokya comparison did not preserve the verified Mercury to Mars conflict")
    return {
        "contract": "MO_R4A_S2R1_SARAVALI_TRAILOKYA_NATURAL_RELATIONSHIP_MATRIX_COMPARISON_V1",
        "schemaVersion": CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION,
        "historicalTrailokyaOperatorId": "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1",
        "saravaliOperatorId": "SARAVALI_NATURAL_RELATIONSHIP_V1",
        "historicalS1R1R1LedgerCanonicalHash": _canonical_hash(historical),
        "successorS2R1LedgerCanonicalHash": _canonical_hash(successor),
        "comparisonRows": rows,
        "comparisonSummary": {
            "rowCount": len(rows),
            "comparableDirectedPairCount": 42,
            "agreementCount": statuses.count("AGREEMENT"),
            "conflictCount": statuses.count("CONFLICT"),
            "notComparableCount": statuses.count("NOT_COMPARABLE"),
            "unresolvedCount": 0,
        },
    }


def build_s2r1_r1_relationship_matrix_comparison(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Compare the adjudicated Saravali matrix with Trailokya without assuming the outcome."""

    root = Path(resource_root).resolve()
    historical = build_s1r1_r1_corrected_ledger(root)
    successor = build_s2r1_r1_saravali_adjudicated_ledger(root)
    ordered_bodies = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")
    rows: list[dict[str, Any]] = []
    for source in ordered_bodies:
        for target in ordered_bodies:
            trailokya = evaluate_trailokya_natural_relationship(source, target, ledger=historical)
            saravali = evaluate_saravali_natural_relationship(source, target, ledger=successor)
            if source == target:
                relationship_status = "NOT_COMPARABLE"
                reason = "Neither source contract states a self-relationship; both remain UNKNOWN."
            elif trailokya["outputState"] == "UNKNOWN" or saravali["outputState"] == "UNKNOWN":
                relationship_status = "UNRESOLVED"
                reason = "At least one directed source cell is not closed."
            elif trailokya["outputState"] == saravali["outputState"]:
                relationship_status = "AGREEMENT"
                reason = "Both source-specific directed cells have the same categorical state."
            else:
                relationship_status = "CONFLICT"
                reason = "The two source-specific directed cells differ and remain separately recorded."
            rows.append(
                {
                    "sourceBody": source,
                    "targetBody": target,
                    "historicalTrailokyaState": trailokya["outputState"],
                    "saravaliState": saravali["outputState"],
                    "relationshipStatus": relationship_status,
                    "reason": reason,
                }
            )
    statuses = [row["relationshipStatus"] for row in rows]
    if len(rows) != 49 or statuses.count("NOT_COMPARABLE") != 7 or statuses.count("UNRESOLVED") != 0:
        raise ClassicalSourceOperatorError("S2R1-R1 Saravali/Trailokya comparison is not a complete directed matrix")
    return {
        "contract": "MO_R4A_S2R1_R1_SARAVALI_TRAILOKYA_NATURAL_RELATIONSHIP_MATRIX_COMPARISON_V1",
        "schemaVersion": CLASSICAL_SOURCE_OPERATOR_SCHEMA_VERSION,
        "historicalTrailokyaOperatorId": "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1",
        "saravaliOperatorId": "SARAVALI_NATURAL_RELATIONSHIP_V1",
        "historicalS1R1R1LedgerCanonicalHash": _canonical_hash(historical),
        "successorS2R1R1LedgerCanonicalHash": _canonical_hash(successor),
        "comparisonRows": rows,
        "comparisonSummary": {
            "rowCount": len(rows),
            "comparableDirectedPairCount": sum(row["relationshipStatus"] in {"AGREEMENT", "CONFLICT"} for row in rows),
            "agreementCount": statuses.count("AGREEMENT"),
            "conflictCount": statuses.count("CONFLICT"),
            "notComparableCount": statuses.count("NOT_COMPARABLE"),
            "unresolvedCount": statuses.count("UNRESOLVED"),
        },
    }


def build_s2r1_real_24_source_operator_coverage(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Rebind the frozen S1R1-R1 snapshot to Saravali without recomputing astronomy."""

    root = Path(resource_root).resolve()
    historical = _read_json(root / DEFAULT_S1R1_R1_COVERAGE_PATH.relative_to(PROJECT_ROOT), "historical S1R1-R1 source coverage")
    historical_body = {key: deepcopy(value) for key, value in historical.items() if key != "sourceOperatorCoverageHash"}
    if (
        historical.get("contract"),
        historical.get("sourceOperatorCoverageHash"),
        _canonical_hash(historical_body),
    ) != (
        CLASSICAL_SOURCE_OPERATOR_S1R1_R1_COVERAGE_CONTRACT,
        "359C905C6CF7792F6782E53552CEBCC9D43A63E93EC375E8314ABE795445A2AD",
        "359C905C6CF7792F6782E53552CEBCC9D43A63E93EC375E8314ABE795445A2AD",
    ):
        raise ClassicalSourceOperatorError("S2R1 requires the exact historical S1R1-R1 source coverage")
    successor_ledger = build_s2r1_saravali_lineage_ledger(root)
    report = deepcopy(historical)
    report.update(
        {
            "contract": CLASSICAL_SOURCE_OPERATOR_S2R1_COVERAGE_CONTRACT,
            "milestone": "MO-R4A-S2R1",
            "sourceOperatorLedgerContract": successor_ledger["contract"],
            "sourceOperatorLedgerCanonicalHash": _canonical_hash(successor_ledger),
            "sourceLineageRebinding": {
                "historicalCoverageHash": historical["sourceOperatorCoverageHash"],
                "historicalLedgerHash": historical["sourceOperatorLedgerCanonicalHash"],
                "astronomyRecomputed": False,
                "eventUniverseRegenerated": False,
                "relationshipSourceReboundFrom": "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1",
                "relationshipSourceReboundTo": "SARAVALI_NATURAL_RELATIONSHIP_V1",
            },
        }
    )
    report.pop("sourceOperatorCoverageHash", None)
    for side in report["sides"]:
        for event in side["events"]:
            snapshot = event["astronomySnapshot"]
            outputs, applicable = _event_operator_outputs(snapshot, successor_ledger)
            composition = compose_source_operator_outputs(outputs)
            event["operatorOutputs"] = outputs
            event["applicableOperatorIds"] = applicable
            event["evaluatedOperatorIds"] = composition["evaluatedOperatorIds"]
            event["unresolvedOperatorIds"] = composition["unresolvedOperatorIds"]
            event["sourceCoverageStatus"] = _coverage_status(outputs)
            event["astrologicalCompositionStatus"] = composition["compositionStatus"]
            event["astrologicalInterpretationState"] = composition["astrologicalInterpretationState"]
    events = _coverage_events(report)
    if not all(event["identityStatus"] == "SINGLE_PASS_VERIFIED" for event in events):
        raise ClassicalSourceOperatorError("S2R1 source coverage requires 24 single-pass-verified identities")
    report["summary"] = {
        **report["summary"],
        "sourceOperatorNoneCount": sum(event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_NONE" for event in events),
        "sourceOperatorPartialCount": sum(event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_PARTIAL" for event in events),
        "sourceOperatorSubstantialCount": sum(
            event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_SUBSTANTIAL" for event in events
        ),
        "astrologyUnknownCount": sum(event["astrologicalInterpretationState"] == "UNKNOWN_ASTRO_STATE" for event in events),
        "astrologyMixedCount": sum(event["astrologicalInterpretationState"] == "MIXED_ASTRO_STATE" for event in events),
        "astrologySourceStateCount": sum(
            event["astrologicalInterpretationState"]
            in {"SUPPORTIVE_ASTRO_STATE", "ADVERSE_ASTRO_STATE", "NEUTRAL_ASTRO_STATE"}
            for event in events
        ),
    }
    body = deepcopy(report)
    return {**body, "sourceOperatorCoverageHash": _canonical_hash(body)}


def build_s2r1_r1_real_24_source_operator_coverage(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Rebind immutable S2R1 coverage to the adjudicated source lineage only."""

    root = Path(resource_root).resolve()
    historical = _read_json(root / DEFAULT_S2R1_COVERAGE_PATH.relative_to(PROJECT_ROOT), "historical S2R1 source coverage")
    historical_body = {key: deepcopy(value) for key, value in historical.items() if key != "sourceOperatorCoverageHash"}
    if (
        historical.get("contract"),
        historical.get("sourceOperatorCoverageHash"),
        _canonical_hash(historical_body),
    ) != (
        CLASSICAL_SOURCE_OPERATOR_S2R1_COVERAGE_CONTRACT,
        "B22F42E78D20858045AE98F0010355E1E8895C60F1DD49570230ECC5B2C7F62A",
        "B22F42E78D20858045AE98F0010355E1E8895C60F1DD49570230ECC5B2C7F62A",
    ):
        raise ClassicalSourceOperatorError("S2R1-R1 requires the exact immutable S2R1 source coverage")
    successor_ledger = build_s2r1_r1_saravali_adjudicated_ledger(root)
    report = deepcopy(historical)
    report.update(
        {
            "contract": CLASSICAL_SOURCE_OPERATOR_S2R1_R1_COVERAGE_CONTRACT,
            "milestone": "MO-R4A-S2R1-R1",
            "sourceOperatorLedgerContract": successor_ledger["contract"],
            "sourceOperatorLedgerCanonicalHash": _canonical_hash(successor_ledger),
            "sourceLineageRebinding": {
                "historicalCoverageHash": historical["sourceOperatorCoverageHash"],
                "historicalLedgerHash": historical["sourceOperatorLedgerCanonicalHash"],
                "astronomyRecomputed": False,
                "eventUniverseRegenerated": False,
                "relationshipSourceReboundFrom": "SARAVALI_NATURAL_RELATIONSHIP_V1",
                "relationshipSourceReboundTo": "SARAVALI_NATURAL_RELATIONSHIP_V1",
                "sourceAdjudication": "MO_R4A_S2R1_R1_SARAVALI_RELATIONSHIP_ORIENTATION_PAGINATION_ADJUDICATION_V1",
                "sourceDoctrineChanged": False,
                "evaluatorMathematicsChanged": False,
            },
        }
    )
    report.pop("sourceOperatorCoverageHash", None)
    for side in report["sides"]:
        for event in side["events"]:
            outputs, applicable = _event_operator_outputs(event["astronomySnapshot"], successor_ledger)
            composition = compose_source_operator_outputs(outputs)
            event["operatorOutputs"] = outputs
            event["applicableOperatorIds"] = applicable
            event["evaluatedOperatorIds"] = composition["evaluatedOperatorIds"]
            event["unresolvedOperatorIds"] = composition["unresolvedOperatorIds"]
            event["sourceCoverageStatus"] = _coverage_status(outputs)
            event["astrologicalCompositionStatus"] = composition["compositionStatus"]
            event["astrologicalInterpretationState"] = composition["astrologicalInterpretationState"]
    events = _coverage_events(report)
    if len(events) != 24 or not all(event["identityStatus"] == "SINGLE_PASS_VERIFIED" for event in events):
        raise ClassicalSourceOperatorError("S2R1-R1 source coverage requires all 24 frozen verified identities")
    report["summary"] = {
        **report["summary"],
        "sourceOperatorNoneCount": sum(event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_NONE" for event in events),
        "sourceOperatorPartialCount": sum(event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_PARTIAL" for event in events),
        "sourceOperatorSubstantialCount": sum(event["sourceCoverageStatus"] == "SOURCE_OPERATOR_COVERAGE_SUBSTANTIAL" for event in events),
        "astrologyUnknownCount": sum(event["astrologicalInterpretationState"] == "UNKNOWN_ASTRO_STATE" for event in events),
        "astrologyMixedCount": sum(event["astrologicalInterpretationState"] == "MIXED_ASTRO_STATE" for event in events),
        "astrologySourceStateCount": sum(
            event["astrologicalInterpretationState"] in {"SUPPORTIVE_ASTRO_STATE", "ADVERSE_ASTRO_STATE", "NEUTRAL_ASTRO_STATE"}
            for event in events
        ),
    }
    body = deepcopy(report)
    return {**body, "sourceOperatorCoverageHash": _canonical_hash(body)}


def write_s2r1_source_lineage_artifacts(resource_root: Path = PROJECT_ROOT) -> dict[str, Path]:
    """Materialize the successor ledger and coverage from frozen source-only inputs."""

    root = Path(resource_root).resolve()
    artifacts = {
        "ledger": root / "configs" / "research" / "machine_interpretation" / "source_operators" / DEFAULT_S2R1_LEDGER_PATH.name,
        "coverage": root / "status" / "audits" / DEFAULT_S2R1_COVERAGE_PATH.name,
    }
    payloads = {
        "ledger": build_s2r1_saravali_lineage_ledger(root),
        "coverage": build_s2r1_real_24_source_operator_coverage(root),
    }
    for name, path in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[name], ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return artifacts


def write_s2r1_r1_source_lineage_artifacts(resource_root: Path = PROJECT_ROOT) -> dict[str, Path]:
    """Materialize the post-adjudication source ledger and coverage without touching S2R1."""

    root = Path(resource_root).resolve()
    artifacts = {
        "ledger": root / DEFAULT_S2R1_R1_LEDGER_PATH.relative_to(PROJECT_ROOT),
        "coverage": root / DEFAULT_S2R1_R1_COVERAGE_PATH.relative_to(PROJECT_ROOT),
    }
    payloads = {
        "ledger": build_s2r1_r1_saravali_adjudicated_ledger(root),
        "coverage": build_s2r1_r1_real_24_source_operator_coverage(root),
    }
    for name, path in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[name], ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return artifacts


def render_real_source_operator_coverage_markdown(report: Mapping[str, Any]) -> str:
    if report.get("contract") not in {
        CLASSICAL_SOURCE_OPERATOR_COVERAGE_CONTRACT,
        *_SOURCE_LAYER_COVERAGE_CONTRACTS,
    }:
        raise ClassicalSourceOperatorError("Cannot render an unsupported source-operator coverage report")
    summary = report["summary"]
    lines = [
        f"# {report['milestone']} Real 24 Event Source-Operator Coverage",
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


def build_s1r1_rebinding_identity_comparison(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Compare S1 and S1R1 without treating provenance changes as event changes."""

    def operator_outputs_without_provenance(outputs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        """Keep every evaluator result field while removing locator-only presentation metadata."""

        normalized: list[dict[str, Any]] = []
        for output in outputs:
            item = deepcopy(dict(output))
            item.pop("sourceFamily", None)
            item.pop("sourceLocators", None)
            measurement = item.get("sourceMeasurement")
            if isinstance(measurement, dict):
                measurement.pop("sourceLocator", None)
            normalized.append(item)
        return normalized

    root = Path(resource_root).resolve()
    baseline = build_real_source_operator_coverage_report(root)
    hardened_ledger = build_s1r1_provenance_hardened_ledger(root)
    rebound = build_real_source_operator_coverage_report(
        root,
        source_ledger=hardened_ledger,
        milestone="MO-R4A-S1R1",
        coverage_contract=CLASSICAL_SOURCE_OPERATOR_S1R1_COVERAGE_CONTRACT,
    )
    identity_fields = (
        "eventId",
        "eventHash",
        "sideIdentity",
        "transitBody",
        "natalTarget",
        "aspectType",
        "exactUtc",
        "identityStatus",
        "inputPolicy",
    )
    semantic_fields = (
        "applicableOperatorIds",
        "evaluatedOperatorIds",
        "unresolvedOperatorIds",
        "sourceCoverageStatus",
        "astrologicalCompositionStatus",
        "astrologicalInterpretationState",
        "marketBridgeStatus",
        "currencyDirectionStatus",
        "magnitudeStatus",
        "mode",
    )
    before_events = [event for side in baseline["sides"] for event in side["events"]]
    after_events = [event for side in rebound["sides"] for event in side["events"]]
    if len(before_events) != 24 or len(after_events) != 24:
        raise ClassicalSourceOperatorError("S1R1 identity comparison requires exactly 24 events per side-by-side report")
    comparisons: list[dict[str, Any]] = []
    for before, after in zip(before_events, after_events, strict=True):
        identity_before = {key: before[key] for key in identity_fields}
        identity_after = {key: after[key] for key in identity_fields}
        semantic_before = {key: before[key] for key in semantic_fields}
        semantic_after = {key: after[key] for key in semantic_fields}
        event_without_outputs_before = deepcopy(before)
        event_without_outputs_after = deepcopy(after)
        event_without_outputs_before.pop("operatorOutputs", None)
        event_without_outputs_after.pop("operatorOutputs", None)
        operator_semantics_unchanged = operator_outputs_without_provenance(before["operatorOutputs"]) == operator_outputs_without_provenance(
            after["operatorOutputs"]
        )
        comparisons.append(
            {
                "eventId": before["eventId"],
                "identityBefore": identity_before,
                "identityAfter": identity_after,
                "identityUnchanged": identity_before == identity_after,
                "astronomySnapshotUnchanged": before["astronomySnapshot"] == after["astronomySnapshot"],
                "evaluationSemanticsUnchanged": semantic_before == semantic_after,
                "eventFieldsOutsideOperatorOutputsUnchanged": event_without_outputs_before == event_without_outputs_after,
                "operatorOutputSemanticsUnchanged": operator_semantics_unchanged,
                "changedReportBytesRestrictedToProvenanceOrHash": (
                    before["operatorOutputs"] != after["operatorOutputs"]
                    and before["eventHash"] == after["eventHash"]
                    and event_without_outputs_before == event_without_outputs_after
                    and operator_semantics_unchanged
                ),
            }
        )
    if not all(
        item["identityUnchanged"]
        and item["astronomySnapshotUnchanged"]
        and item["evaluationSemanticsUnchanged"]
        and item["eventFieldsOutsideOperatorOutputsUnchanged"]
        and item["operatorOutputSemanticsUnchanged"]
        and item["changedReportBytesRestrictedToProvenanceOrHash"]
        for item in comparisons
    ):
        raise ClassicalSourceOperatorError("S1R1 provenance rebinding changed immutable event data or evaluation semantics")
    return {
        "contract": "MO_R4A_S1R1_IMMUTABLE_EVENT_REBINDING_COMPARISON_V1",
        "schemaVersion": 1,
        "milestone": "MO-R4A-S1R1",
        "historicalS1LedgerCanonicalHash": baseline["sourceOperatorLedgerCanonicalHash"],
        "provenanceHardenedLedgerCanonicalHash": rebound["sourceOperatorLedgerCanonicalHash"],
        "historicalS1CoverageHash": baseline["sourceOperatorCoverageHash"],
        "provenanceHardenedCoverageHash": rebound["sourceOperatorCoverageHash"],
        "eventCount": len(comparisons),
        "usdEventCount": rebound["summary"]["usdEventCount"],
        "jpyEventCount": rebound["summary"]["jpyEventCount"],
        "singlePassVerifiedCount": rebound["summary"]["singlePassVerifiedCount"],
        "identityFields": list(identity_fields),
        "comparisons": comparisons,
        "summary": {
            "allIdentityBearingFieldsUnchanged": True,
            "allAstronomySnapshotsUnchanged": True,
            "allEvaluationSemanticsUnchanged": True,
            "allEventFieldsOutsideOperatorOutputsUnchanged": True,
            "allOperatorOutputSemanticsUnchanged": True,
            "reportChangesRestrictedToProvenanceOrHash": True,
            "marketHypothesisRegistryEntriesCreated": 0,
            "realPolarityCount": 0,
            "marketMagnitude": MAGNITUDE_NOT_CONFIGURED,
            "outcomeDataRead": False,
            "executionAllowed": False,
        },
    }


def build_s1r1_r1_rebinding_identity_comparison(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Prove that the S1R1-R1 rebinding changes only provenance and hashes."""

    def operator_outputs_without_provenance(outputs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for output in outputs:
            item = deepcopy(dict(output))
            item.pop("sourceFamily", None)
            item.pop("sourceLocators", None)
            measurement = item.get("sourceMeasurement")
            if isinstance(measurement, dict):
                measurement.pop("sourceLocator", None)
            normalized.append(item)
        return normalized

    root = Path(resource_root).resolve()
    before_ledger = build_s1r1_provenance_hardened_ledger(root)
    after_ledger = build_s1r1_r1_corrected_ledger(root)
    before = build_real_source_operator_coverage_report(
        root,
        source_ledger=before_ledger,
        milestone="MO-R4A-S1R1",
        coverage_contract=CLASSICAL_SOURCE_OPERATOR_S1R1_COVERAGE_CONTRACT,
    )
    after = build_real_source_operator_coverage_report(
        root,
        source_ledger=after_ledger,
        milestone="MO-R4A-S1R1-R1",
        coverage_contract=CLASSICAL_SOURCE_OPERATOR_S1R1_R1_COVERAGE_CONTRACT,
    )
    identity_fields = (
        "eventId",
        "eventHash",
        "sideIdentity",
        "transitBody",
        "natalTarget",
        "aspectType",
        "exactUtc",
        "identityStatus",
        "inputPolicy",
    )
    semantic_fields = (
        "applicableOperatorIds",
        "evaluatedOperatorIds",
        "unresolvedOperatorIds",
        "sourceCoverageStatus",
        "astrologicalCompositionStatus",
        "astrologicalInterpretationState",
        "marketBridgeStatus",
        "currencyDirectionStatus",
        "magnitudeStatus",
        "mode",
    )
    before_events = [event for side in before["sides"] for event in side["events"]]
    after_events = [event for side in after["sides"] for event in side["events"]]
    if len(before_events) != 24 or len(after_events) != 24:
        raise ClassicalSourceOperatorError("S1R1-R1 identity comparison requires exactly 24 events")
    comparisons: list[dict[str, Any]] = []
    for previous, current in zip(before_events, after_events, strict=True):
        identity_before = {key: previous[key] for key in identity_fields}
        identity_after = {key: current[key] for key in identity_fields}
        semantic_before = {key: previous[key] for key in semantic_fields}
        semantic_after = {key: current[key] for key in semantic_fields}
        previous_without_outputs = deepcopy(previous)
        current_without_outputs = deepcopy(current)
        previous_without_outputs.pop("operatorOutputs", None)
        current_without_outputs.pop("operatorOutputs", None)
        operator_semantics_unchanged = operator_outputs_without_provenance(previous["operatorOutputs"]) == operator_outputs_without_provenance(
            current["operatorOutputs"]
        )
        comparisons.append(
            {
                "eventId": previous["eventId"],
                "identityBefore": identity_before,
                "identityAfter": identity_after,
                "identityUnchanged": identity_before == identity_after,
                "astronomySnapshotUnchanged": previous["astronomySnapshot"] == current["astronomySnapshot"],
                "evaluationSemanticsUnchanged": semantic_before == semantic_after,
                "eventFieldsOutsideOperatorOutputsUnchanged": previous_without_outputs == current_without_outputs,
                "operatorOutputSemanticsUnchanged": operator_semantics_unchanged,
                "changedReportBytesRestrictedToProvenanceOrHash": (
                    previous["operatorOutputs"] != current["operatorOutputs"]
                    and previous["eventHash"] == current["eventHash"]
                    and previous_without_outputs == current_without_outputs
                    and operator_semantics_unchanged
                ),
            }
        )
    if not all(
        item["identityUnchanged"]
        and item["astronomySnapshotUnchanged"]
        and item["evaluationSemanticsUnchanged"]
        and item["eventFieldsOutsideOperatorOutputsUnchanged"]
        and item["operatorOutputSemanticsUnchanged"]
        and item["changedReportBytesRestrictedToProvenanceOrHash"]
        for item in comparisons
    ):
        raise ClassicalSourceOperatorError("S1R1-R1 changed immutable event data or evaluation semantics")
    return {
        "contract": "MO_R4A_S1R1_R1_IMMUTABLE_EVENT_REBINDING_COMPARISON_V1",
        "schemaVersion": 1,
        "milestone": "MO-R4A-S1R1-R1",
        "preCorrectionS1R1LedgerCanonicalHash": before["sourceOperatorLedgerCanonicalHash"],
        "correctedS1R1R1LedgerCanonicalHash": after["sourceOperatorLedgerCanonicalHash"],
        "preCorrectionS1R1CoverageHash": before["sourceOperatorCoverageHash"],
        "correctedS1R1R1CoverageHash": after["sourceOperatorCoverageHash"],
        "eventCount": len(comparisons),
        "usdEventCount": after["summary"]["usdEventCount"],
        "jpyEventCount": after["summary"]["jpyEventCount"],
        "singlePassVerifiedCount": after["summary"]["singlePassVerifiedCount"],
        "identityFields": list(identity_fields),
        "comparisons": comparisons,
        "summary": {
            "allIdentityBearingFieldsUnchanged": True,
            "allAstronomySnapshotsUnchanged": True,
            "allEvaluationSemanticsUnchanged": True,
            "allEventFieldsOutsideOperatorOutputsUnchanged": True,
            "allOperatorOutputSemanticsUnchanged": True,
            "reportChangesRestrictedToProvenanceOrHash": True,
            "marketHypothesisRegistryEntriesCreated": 0,
            "realPolarityCount": 0,
            "marketMagnitude": MAGNITUDE_NOT_CONFIGURED,
            "outcomeDataRead": False,
            "executionAllowed": False,
        },
    }


def write_real_source_operator_coverage_artifacts(
    *,
    resource_root: Path = PROJECT_ROOT,
    json_path: Path,
    markdown_path: Path,
    source_ledger: Mapping[str, Any] | None = None,
    milestone: str = "MO-R4A-S1",
    coverage_contract: str = CLASSICAL_SOURCE_OPERATOR_COVERAGE_CONTRACT,
) -> dict[str, Any]:
    """Write deterministic audit artifacts only to explicit caller-owned paths."""

    report = build_real_source_operator_coverage_report(
        resource_root,
        source_ledger=source_ledger,
        milestone=milestone,
        coverage_contract=coverage_contract,
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_real_source_operator_coverage_markdown(report), encoding="utf-8")
    return report
