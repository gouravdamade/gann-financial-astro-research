"""MO-R4A-S3R1 preregistration-integrity successor.

This module hardens the outcome-blind S3 package without changing its
scientific design.  It has no provider client, market-file reader, outcome
loader, or product integration.  Its quote evaluator is limited to synthetic
in-memory inputs for contract tests.
"""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

import outcome_analysis_s3 as s3


S3R1_PREREGISTRATION_CONTRACT = "MO_R4A_S3R1_OUTCOME_ANALYSIS_PREREGISTRATION_V1"
S3R1_PRIMARY_POPULATION_CONTRACT = "MO_R4A_S3R1_PRIMARY_ANALYSIS_POPULATION_V1"
S3R1_OVERLAP_CLUSTERS_CONTRACT = "MO_R4A_S3R1_OVERLAP_CLUSTERS_V1"
S3R1_INVARIANCE_AUDIT_CONTRACT = "MO_R4A_S3R1_ANALYSIS_PLAN_INVARIANCE_AUDIT_V1"
S3R1_CORE_MANIFEST_CONTRACT = "MO_R4A_S3R1_FROZEN_ANALYSIS_PACKAGE_V1"
S3R1_ACCEPTANCE_CONTRACT = "MO_R4A_S3R1_OUTCOME_ANALYSIS_PREREGISTRATION_ACCEPTANCE_V1"
S3R1_SCHEMA_VERSION = 1
S3R1_MILESTONE = "MO-R4A-S3R1"
S3R1_EXPECTED_STARTING_MASTER = "703b1e1e27bb83adb840200f6914316e54b2d27f"
S3R1_AUTHORED_AT_UTC = "2026-09-11T00:00:00Z"
S3R1_TIMESTAMP_SEMANTICS = "DECLARATIVE_FROZEN_METADATA_NOT_GIT_COMMIT_CHRONOLOGY"

HISTORICAL_S3_PREREGISTRATION_HASH = "C4F8B0AC31CE37662A533B9570364894CEC37DD01FE6B68D137FE2C65001A319"
HISTORICAL_S3_PRIMARY_POPULATION_HASH = "8C985371B43E4285664C48D3579B9AD793EC30D56BBED2C7B15067822AFDF970"
HISTORICAL_S3_OVERLAP_CLUSTERS_HASH = "AF6F55E47015C9AB5FBDD61FE90505425F5AD8D506415CD7A511662B0FDAFF1A"
HISTORICAL_S3_INVARIANCE_HASH = "5F5504B042CA3C69526291C570337C951C41267C6577A3B7EB8BAD22B8F74807"
HISTORICAL_S3_ACCEPTANCE_HASH = "155B814F64B9B3C9BB4E0BF57FEC94EDD0423A513D5CB04DAA63D1AB7CBCE1F8"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"

DEFAULT_PREREGISTRATION_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_v1.json"
DEFAULT_SCHEMA_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_v1.schema.json"
DEFAULT_PRIMARY_POPULATION_PATH = AUDIT_ROOT / "mo_r4a_s3r1_primary_analysis_population.json"
DEFAULT_OVERLAP_CLUSTERS_PATH = AUDIT_ROOT / "mo_r4a_s3r1_overlap_clusters.json"
DEFAULT_INVARIANCE_PATH = AUDIT_ROOT / "mo_r4a_s3r1_analysis_plan_invariance_audit.json"
DEFAULT_CORE_MANIFEST_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_frozen_analysis_package.json"
DEFAULT_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_outcome_analysis_preregistration.json"
DEFAULT_REPORT_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S3R1_PREREGISTRATION_INTEGRITY_HARDENING.md"

EXPECTED_UPSTREAM_HASHES = copy.deepcopy(s3.EXPECTED_UPSTREAM_HASHES)
ACCESS_FLAGS = tuple(s3.OUTCOME_ACCESS_FLAGS)


class OutcomeAnalysisS3R1Error(ValueError):
    """Raised when a successor artifact is not an exact S3R1 contract."""


class ConflictingSyntheticTickError(OutcomeAnalysisS3R1Error):
    """Raised internally when a timestamp has conflicting quote values."""

    def __init__(self, timestamp_utc: str) -> None:
        self.timestamp_utc = timestamp_utc
        super().__init__(f"Conflicting synthetic quotes at {timestamp_utc}")


def _canonical_hash(value: Any) -> str:
    return s3._canonical_hash(value)


def _without_hash(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    return {name: copy.deepcopy(item) for name, item in value.items() if name != key}


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OutcomeAnalysisS3R1Error(f"Missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OutcomeAnalysisS3R1Error(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(value, dict):
        raise OutcomeAnalysisS3R1Error(f"{label} must be a JSON object")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _all_false_flags() -> dict[str, bool]:
    return {key: False for key in ACCESS_FLAGS}


def _assert_false_flags(value: Any, label: str) -> None:
    if not isinstance(value, dict) or set(value) != set(ACCESS_FLAGS) or any(item is not False for item in value.values()):
        raise OutcomeAnalysisS3R1Error(f"{label} must contain exactly the 16 false S3 access flags")


def _assert_hash(value: Any, label: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9A-F]{64}", value) is None:
        raise OutcomeAnalysisS3R1Error(f"{label} must be an uppercase SHA-256")


def _assert_historical_s3_is_unchanged(root: Path) -> dict[str, dict[str, Any]]:
    """Read historical S3 evidence only to prove the successor did not mutate it."""

    paths = {
        "preregistration": root / s3.DEFAULT_PREREGISTRATION_PATH.relative_to(s3.PROJECT_ROOT),
        "population": root / s3.DEFAULT_PRIMARY_POPULATION_PATH.relative_to(s3.PROJECT_ROOT),
        "clusters": root / s3.DEFAULT_OVERLAP_CLUSTERS_PATH.relative_to(s3.PROJECT_ROOT),
        "invariance": root / s3.DEFAULT_INVARIANCE_AUDIT_PATH.relative_to(s3.PROJECT_ROOT),
        "acceptance": root / s3.DEFAULT_ACCEPTANCE_PATH.relative_to(s3.PROJECT_ROOT),
    }
    historical = {name: _read_json(path, f"historical S3 {name}") for name, path in paths.items()}
    expected = {
        "preregistration": HISTORICAL_S3_PREREGISTRATION_HASH,
        "population": HISTORICAL_S3_PRIMARY_POPULATION_HASH,
        "clusters": HISTORICAL_S3_OVERLAP_CLUSTERS_HASH,
        "invariance": HISTORICAL_S3_INVARIANCE_HASH,
        "acceptance": HISTORICAL_S3_ACCEPTANCE_HASH,
    }
    hash_keys = {
        "preregistration": "preregistrationHash",
        "population": "primaryPopulationHash",
        "clusters": "overlapClustersHash",
        "invariance": "analysisPlanInvarianceAuditHash",
        "acceptance": "acceptanceManifestHash",
    }
    for name, value in historical.items():
        key = hash_keys[name]
        if value.get(key) != expected[name] or _canonical_hash(_without_hash(value, key)) != expected[name]:
            raise OutcomeAnalysisS3R1Error(f"historical S3 {name} no longer has its accepted hash")
    return historical


def _historical_s3_inputs(root: Path) -> dict[str, dict[str, Any]]:
    """Load the existing S3 package and its immutable S2R1-R1 lineage."""

    historical = _assert_historical_s3_is_unchanged(root)
    upstream = s3.load_verified_s2r1_r1_inputs(root)
    return {**upstream, "s3": historical}


def build_s3r1_preregistration(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Create the S3R1 successor while retaining every accepted S3 design value."""

    root = Path(resource_root).resolve()
    inputs = _historical_s3_inputs(root)
    historical = inputs["s3"]["preregistration"]
    if historical.get("preregistrationHash") != HISTORICAL_S3_PREREGISTRATION_HASH:
        raise OutcomeAnalysisS3R1Error("S3R1 must start from the accepted historical S3 preregistration")
    body = copy.deepcopy(historical)
    body.pop("createdAtUtc", None)
    body.pop("preregistrationHash", None)
    body.update(
        {
            "contract": S3R1_PREREGISTRATION_CONTRACT,
            "schemaVersion": S3R1_SCHEMA_VERSION,
            "milestone": S3R1_MILESTONE,
            "startingMaster": S3R1_EXPECTED_STARTING_MASTER,
            "preregistrationAuthoredAtUtc": S3R1_AUTHORED_AT_UTC,
            "timestampSemantics": S3R1_TIMESTAMP_SEMANTICS,
            "status": "S3R1_PREREGISTRATION_INTEGRITY_HARDENED_AND_COMPOSITE_FREEZE_COMPLETE_CENTRAL_REVIEW_REQUIRED",
            "nextGate": "INDEPENDENT_CENTRAL_REVIEW_BEFORE_ASTRA_PRE_OUTCOME_AUDIT",
            "supersedesPreregistrationContract": historical["contract"],
            "supersedesPreregistrationHash": HISTORICAL_S3_PREREGISTRATION_HASH,
            "supersedesAcceptanceManifestHash": HISTORICAL_S3_ACCEPTANCE_HASH,
            "correctionReason": "PREREGISTRATION_INTEGRITY_HARDENING_WITHOUT_ANALYSIS_DESIGN_CHANGE",
        }
    )
    body["permutationNullAssumption"] = {
        "identifier": "CONDITIONAL_WITHIN_SIDE_LABEL_EXCHANGEABILITY_NULL",
        "statement": "The primary exact test conditions on the observed number of SUPPORTIVE and ADVERSE labels within each currency side. Under the preregistered null, SUPPORTIVE/ADVERSE labels are treated as exchangeable across the frozen primary event positions within USD and independently within JPY. The 40-state universe is therefore an exact enumeration of this conditional permutation null; it is not a claim that the original labels arose from a randomized experiment.",
        "usdPositions": 5,
        "usdSupportiveLabels": 1,
        "jpyPositions": 8,
        "jpySupportiveLabels": 7,
        "crossSideExchangeability": False,
        "randomizedExperimentClaim": False,
        "allowedInference": "ASSOCIATION_UNDER_PREREGISTERED_CONDITIONAL_WITHIN_SIDE_PERMUTATION_NULL_IN_THIS_FIXED_PILOT",
        "prohibitedInference": [
            "CAUSATION",
            "GENERAL_ASTROLOGY_TRUTH",
            "UNIVERSAL_FINANCIAL_VALIDITY",
            "INDEPENDENT_REPLICATION",
            "PRODUCTION_PROFITABILITY",
            "OUT_OF_SAMPLE_FORECASTING",
            "CALIBRATED_PROBABILITY",
        ],
    }
    body["timeShiftDiagnostics"] = {
        "shiftsCalendarDays": [-7, 7],
        "preserve": ["duration", "side", "label", "UTC clock"],
        "sameBoundaryAndReturnRule": True,
        "diagnosticOnly": True,
        "secondaryPValueAllowed": False,
        "timingSpecificityFlag": "TIMING_SPECIFICITY_NOT_DEMONSTRATED",
        "comparisonStatistic": "H_actual compared strictly greater than both H_minus7 and H_plus7",
        "actualHitCount": "H_actual = primary hit count over the 13 actual intervals",
        "minus7HitCount": "H_minus7 = hit count from the same 13 labels on exactly -7 calendar-day intervals",
        "plus7HitCount": "H_plus7 = hit count from the same 13 labels on exactly +7 calendar-day intervals",
        "completenessRule": "All 13 actual and both 13-event shifted sets must be validly scorable; no denominator shrink, replacement, rescue, or alternate horizon",
        "incompleteStatus": "TIMING_DIAGNOSTIC_INCOMPLETE",
        "demonstratedStatus": "TIMING_SPECIFICITY_DEMONSTRATED_WITHIN_PREREGISTERED_DIAGNOSTIC",
        "notDemonstratedStatus": "TIMING_SPECIFICITY_NOT_DEMONSTRATED",
        "strictComparison": True,
        "tieIsNotDemonstrated": True,
        "doesNotAffectPrimarySurvival": True,
    }
    return {**body, "preregistrationHash": _canonical_hash(body)}


def _schema_for_value(value: Any, path: tuple[str, ...] = ()) -> dict[str, Any]:
    """Build a closed JSON Schema for the fixed preregistration payload."""

    if isinstance(value, dict):
        properties = {key: _schema_for_value(item, path + (key,)) for key, item in value.items()}
        return {
            "type": "object",
            "additionalProperties": False,
            "required": list(value),
            "properties": properties,
        }
    if isinstance(value, list):
        schema: dict[str, Any] = {
            "type": "array",
            "minItems": len(value),
            "maxItems": len(value),
            "prefixItems": [_schema_for_value(item, path + (f"[{index}]",)) for index, item in enumerate(value)],
            "items": False,
        }
        schema["uniqueItems"] = len({json.dumps(item, sort_keys=True) for item in value}) == len(value)
        return schema
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "boolean", "const": value}
    if isinstance(value, int):
        return {"type": "integer", "const": value}
    if isinstance(value, float):
        return {"type": "number", "const": value}
    if isinstance(value, str):
        schema = {"type": "string", "const": value}
        if path[:1] == ("upstreamHashes",):
            schema["pattern"] = r"^[0-9A-F]{64}$"
        return schema
    raise OutcomeAnalysisS3R1Error(f"Cannot create strict schema for {path}")


def build_s3r1_schema(preregistration: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = copy.deepcopy(preregistration) if preregistration is not None else build_s3r1_preregistration(PROJECT_ROOT)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "MO_R4A_S3R1_OUTCOME_ANALYSIS_PREREGISTRATION_V1",
        "title": S3R1_PREREGISTRATION_CONTRACT,
        **_schema_for_value(payload),
    }


def _json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_json_schema_instance(value: Any, schema: Mapping[str, Any], path: str = "$") -> None:
    """Validate the draft-2020-12 keywords used by the strict S3R1 schema."""

    expected_type = schema.get("type")
    if expected_type is not None and not _json_type_matches(value, expected_type):
        raise OutcomeAnalysisS3R1Error(f"JSON Schema type mismatch at {path}")
    if "const" in schema and value != schema["const"]:
        raise OutcomeAnalysisS3R1Error(f"JSON Schema const mismatch at {path}")
    if "enum" in schema and value not in schema["enum"]:
        raise OutcomeAnalysisS3R1Error(f"JSON Schema enum mismatch at {path}")
    if isinstance(value, str) and "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
        raise OutcomeAnalysisS3R1Error(f"JSON Schema pattern mismatch at {path}")
    if isinstance(value, dict):
        required = schema.get("required", [])
        if set(required) != set(value):
            raise OutcomeAnalysisS3R1Error(f"JSON Schema object keys mismatch at {path}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is not False or set(properties) != set(required):
            raise OutcomeAnalysisS3R1Error(f"JSON Schema object is not closed at {path}")
        for key, item in value.items():
            validate_json_schema_instance(item, properties[key], f"{path}.{key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", len(value)):
            raise OutcomeAnalysisS3R1Error(f"JSON Schema array length mismatch at {path}")
        if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
            raise OutcomeAnalysisS3R1Error(f"JSON Schema uniqueItems mismatch at {path}")
        prefix_items = schema.get("prefixItems")
        if prefix_items is not None:
            if len(prefix_items) != len(value):
                raise OutcomeAnalysisS3R1Error(f"JSON Schema prefixItems length mismatch at {path}")
            for index, item in enumerate(value):
                validate_json_schema_instance(item, prefix_items[index], f"{path}[{index}]")
        elif schema.get("items") is not False:
            item_schema = schema.get("items", {})
            for index, item in enumerate(value):
                validate_json_schema_instance(item, item_schema, f"{path}[{index}]")


def validate_s3r1_preregistration(preregistration: Mapping[str, Any]) -> None:
    """Fail closed on both schema mutations and semantic/hash mutations."""

    expected = build_s3r1_preregistration(PROJECT_ROOT)
    validate_json_schema_instance(preregistration, build_s3r1_schema(expected))
    if preregistration.get("preregistrationHash") != _canonical_hash(_without_hash(preregistration, "preregistrationHash")):
        raise OutcomeAnalysisS3R1Error("S3R1 preregistration hash is invalid")
    if preregistration.get("upstreamHashes") != EXPECTED_UPSTREAM_HASHES:
        raise OutcomeAnalysisS3R1Error("S3R1 upstream hash bindings changed")
    _assert_false_flags(preregistration["outcomeAccessFlags"], "S3R1 preregistration flags")
    if preregistration["timestampSemantics"] != S3R1_TIMESTAMP_SEMANTICS:
        raise OutcomeAnalysisS3R1Error("S3R1 timestamp semantics changed")
    if preregistration["marketDataSource"]["s3ProviderAccessAllowed"] is not False:
        raise OutcomeAnalysisS3R1Error("S3R1 provider access is not disabled")


def build_s3r1_primary_population(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Re-derive rows through S3 logic, then bind them to the S3R1 preregistration."""

    root = Path(resource_root).resolve()
    inputs = _historical_s3_inputs(root)
    preregistration = build_s3r1_preregistration(root)
    historical_population = inputs["s3"]["population"]
    derived = s3.build_primary_analysis_population(root)
    if derived["populationCounts"] != historical_population["populationCounts"] or derived["primaryMarketScorableRows"] != historical_population["primaryMarketScorableRows"] or derived["allFrozenRows"] != historical_population["allFrozenRows"]:
        raise OutcomeAnalysisS3R1Error("S3R1 population derivation changed the accepted S3 event rows")
    body = {
        "contract": S3R1_PRIMARY_POPULATION_CONTRACT,
        "schemaVersion": S3R1_SCHEMA_VERSION,
        "milestone": S3R1_MILESTONE,
        "supersedesPrimaryPopulationContract": historical_population["contract"],
        "supersedesPrimaryPopulationHash": HISTORICAL_S3_PRIMARY_POPULATION_HASH,
        "preregistrationHash": preregistration["preregistrationHash"],
        "predictionFreezeHash": EXPECTED_UPSTREAM_HASHES["predictionFreezeHash"],
        "populationCounts": copy.deepcopy(derived["populationCounts"]),
        "allFrozenRows": copy.deepcopy(derived["allFrozenRows"]),
        "primaryMarketScorableRows": copy.deepcopy(derived["primaryMarketScorableRows"]),
        "structuralExclusion": copy.deepcopy(derived["structuralExclusion"]),
        "outcomeAccessFlags": _all_false_flags(),
    }
    return {**body, "primaryPopulationHash": _canonical_hash(body)}


def build_s3r1_overlap_clusters(
    resource_root: Path = PROJECT_ROOT,
    *,
    population: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    inputs = _historical_s3_inputs(root)
    primary_population = copy.deepcopy(population) if population is not None else build_s3r1_primary_population(root)
    historical_clusters = inputs["s3"]["clusters"]
    derived = s3.derive_overlap_clusters(primary_population["primaryMarketScorableRows"])
    if derived != historical_clusters["clusters"]:
        raise OutcomeAnalysisS3R1Error("S3R1 overlap derivation changed the accepted four clusters")
    body = {
        "contract": S3R1_OVERLAP_CLUSTERS_CONTRACT,
        "schemaVersion": S3R1_SCHEMA_VERSION,
        "milestone": S3R1_MILESTONE,
        "supersedesOverlapClustersContract": historical_clusters["contract"],
        "supersedesOverlapClustersHash": HISTORICAL_S3_OVERLAP_CLUSTERS_HASH,
        "primaryPopulationHash": primary_population["primaryPopulationHash"],
        "overlapRule": "a.start < b.end and b.start < a.end",
        "touchingBoundaryIsOverlap": False,
        "clusterConstruction": "TRANSITIVE_CONNECTED_COMPONENTS",
        "clusters": copy.deepcopy(derived),
        "outcomeAccessFlags": _all_false_flags(),
    }
    return {**body, "overlapClustersHash": _canonical_hash(body)}


def build_s3r1_invariance_audit(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind every S3R1 event field to the accepted S2R1-R1/S3 snapshot."""

    root = Path(resource_root).resolve()
    inputs = _historical_s3_inputs(root)
    prereg = copy.deepcopy(preregistration) if preregistration is not None else build_s3r1_preregistration(root)
    primary_population = copy.deepcopy(population) if population is not None else build_s3r1_primary_population(root)
    overlap_clusters = copy.deepcopy(clusters) if clusters is not None else build_s3r1_overlap_clusters(root, population=primary_population)
    historical_population = inputs["s3"]["population"]
    historical_invariance = inputs["s3"]["invariance"]
    freeze = inputs["freeze"]
    coverage_rows = [event for side in inputs["coverage"]["sides"] for event in side["events"]]
    predictions = freeze["predictions"]
    old_rows_by_event = {row["eventId"]: row for row in historical_population["allFrozenRows"]}
    prior_audit_rows = {row["eventId"]: row for row in historical_invariance["eventRows"]}
    if len(coverage_rows) != 24 or len(predictions) != 24 or set(old_rows_by_event) != {row["eventId"] for row in predictions}:
        raise OutcomeAnalysisS3R1Error("S3R1 invariance audit requires the exact 24-event predecessor")
    rows: list[dict[str, Any]] = []
    for coverage, prediction in zip(coverage_rows, predictions, strict=True):
        event_id = prediction["eventId"]
        old_row = old_rows_by_event[event_id]
        prior = prior_audit_rows[event_id]
        new_row = next(row for row in primary_population["allFrozenRows"] if row["eventId"] == event_id)
        identity_fields = ("eventId", "eventHash", "sideIdentity", "transitBody", "natalTarget", "aspectType", "exactUtc")
        identity_unchanged = all(prediction.get(key) == coverage.get(key) for key in identity_fields)
        event_hash_unchanged = prediction["eventHash"] == old_row["eventHash"]
        interval_unchanged = all(new_row[key] == old_row[key] for key in ("applyingStartUtc", "exactUtc", "separatingEndUtc"))
        pressure_unchanged = new_row["pressureState"] == old_row["pressureState"]
        primary_unchanged = (event_id in {row["eventId"] for row in primary_population["primaryMarketScorableRows"]}) == (event_id in {row["eventId"] for row in historical_population["primaryMarketScorableRows"]})
        row = {
            "eventId": event_id,
            "eventHash": prediction["eventHash"],
            "exactUtc": prediction["exactUtc"],
            "applyingStartUtc": prediction["applyingStartUtc"],
            "separatingEndUtc": prediction["separatingEndUtc"],
            "identityUnchanged": identity_unchanged,
            "eventHashUnchanged": event_hash_unchanged,
            "astronomySnapshotUnchanged": prediction.get("astronomySnapshot") == coverage.get("astronomySnapshot") and prior["astronomySnapshotUnchanged"],
            "pressureStateUnchanged": pressure_unchanged and prior.get("pressureStateUnchanged") is True,
            "directionalClassificationUnchanged": new_row["analysisDisposition"] == old_row["analysisDisposition"],
            "intervalsUnchanged": interval_unchanged,
            "exactUtcUnchanged": new_row["exactUtc"] == old_row["exactUtc"],
            "primaryMembershipUnchanged": primary_unchanged,
            "weekendExclusionUnchanged": event_id != "TN_BD340A6100B173B5F254EDC1" or new_row["analysisDisposition"] == "PRIMARY_NONTRADING_WEEKEND_EXCLUSION",
            "signedUnitIsNull": prediction.get("signedUnit") is None,
            "magnitudeConfiguredFalse": prediction.get("magnitudeConfigured") is False,
            "pairResultantAbsent": not any(key in prediction for key in ("pairRaw", "pairDisplay", "pairResultant")),
            "sourceDoctrineUnchanged": EXPECTED_UPSTREAM_HASHES["sourceOperatorLedgerHash"] == inputs["coverage"]["sourceOperatorLedgerCanonicalHash"],
            "s2HypothesisSemanticsUnchanged": prediction.get("eventPredictionHash") == old_row.get("eventPredictionHash"),
        }
        rows.append(row)
    if not all(all(value is True for key, value in row.items() if key not in {"eventId", "eventHash", "exactUtc", "applyingStartUtc", "separatingEndUtc"}) for row in rows):
        raise OutcomeAnalysisS3R1Error("S3R1 invariance audit found a changed frozen event field")
    body = {
        "contract": S3R1_INVARIANCE_AUDIT_CONTRACT,
        "schemaVersion": S3R1_SCHEMA_VERSION,
        "milestone": S3R1_MILESTONE,
        "supersedesInvarianceAuditContract": historical_invariance["contract"],
        "supersedesInvarianceAuditHash": HISTORICAL_S3_INVARIANCE_HASH,
        "preregistrationHash": prereg["preregistrationHash"],
        "primaryPopulationHash": primary_population["primaryPopulationHash"],
        "overlapClustersHash": overlap_clusters["overlapClustersHash"],
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "rows": rows,
        "summary": {
            "eventCount": 24,
            "usdEventCount": 12,
            "jpyEventCount": 12,
            "singlePassVerifiedCount": 24,
            "allEventIdentitiesUnchanged": True,
            "allEventHashesUnchanged": True,
            "allExactUtcUnchanged": all(row["exactUtcUnchanged"] for row in rows),
            "allApplyingStartUtcUnchanged": True,
            "allSeparatingEndUtcUnchanged": True,
            "allAstronomySnapshotsUnchanged": True,
            "allPressureStatesUnchanged": True,
            "allDirectionalClassificationsUnchanged": True,
            "sameSaturdayExclusionUnchanged": True,
            "same13PrimaryIdsUnchanged": True,
            "signedUnitNullForAll": True,
            "magnitudeConfiguredFalseForAll": True,
            "pairResultantAbsent": True,
            "sourceDoctrineUnchanged": True,
            "s2HypothesisSemanticsUnchanged": True,
            "sourceOperatorDoctrineChanged": False,
            "marketOutcomeInS3R1Artifacts": False,
        },
        "outcomeAccessFlags": _all_false_flags(),
    }
    return {**body, "analysisPlanInvarianceAuditHash": _canonical_hash(body)}


def compute_analysis_core_manifest_hash(
    upstream_hashes: Mapping[str, str],
    preregistration_hash: str,
    primary_population_hash: str,
    overlap_clusters_hash: str,
    analysis_plan_invariance_audit_hash: str,
) -> str:
    """Hash the acyclic Level-2 analysis-core body."""
    body = {
        "contract": S3R1_CORE_MANIFEST_CONTRACT,
        "schemaVersion": S3R1_SCHEMA_VERSION,
        "milestone": S3R1_MILESTONE,
        "upstreamHashes": dict(upstream_hashes),
        "preregistrationHash": preregistration_hash,
        "primaryPopulationHash": primary_population_hash,
        "overlapClustersHash": overlap_clusters_hash,
        "analysisPlanInvarianceAuditHash": analysis_plan_invariance_audit_hash,
    }
    return _canonical_hash(body)


def build_analysis_core_manifest(
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
) -> dict[str, Any]:
    """Build Level 2 of the acyclic S3R1 hash hierarchy."""

    component_pairs = (
        (preregistration, "preregistrationHash"),
        (population, "primaryPopulationHash"),
        (clusters, "overlapClustersHash"),
        (invariance, "analysisPlanInvarianceAuditHash"),
    )
    for value, key in component_pairs:
        if value.get(key) != _canonical_hash(_without_hash(value, key)):
            raise OutcomeAnalysisS3R1Error(f"Invalid S3R1 component hash: {key}")
    body = {
        "contract": S3R1_CORE_MANIFEST_CONTRACT,
        "schemaVersion": S3R1_SCHEMA_VERSION,
        "milestone": S3R1_MILESTONE,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": preregistration["preregistrationHash"],
        "primaryPopulationHash": population["primaryPopulationHash"],
        "overlapClustersHash": clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": invariance["analysisPlanInvarianceAuditHash"],
    }
    return {
        **body,
        "analysisCoreManifestHash": compute_analysis_core_manifest_hash(
            upstream_hashes=body["upstreamHashes"],
            preregistration_hash=body["preregistrationHash"],
            primary_population_hash=body["primaryPopulationHash"],
            overlap_clusters_hash=body["overlapClustersHash"],
            analysis_plan_invariance_audit_hash=body["analysisPlanInvarianceAuditHash"],
        ),
    }


def build_s3r1_acceptance_manifest(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
    invariance: Mapping[str, Any] | None = None,
    core: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    inputs = _historical_s3_inputs(root)
    # Rebuild every component from the immutable predecessor before accepting
    # caller-supplied values.  A self-consistent but maliciously rehashed
    # component must not become the acceptance package merely because its hash
    # field is internally correct.
    expected_prereg = build_s3r1_preregistration(root)
    expected_population = build_s3r1_primary_population(root)
    expected_clusters = build_s3r1_overlap_clusters(root, population=expected_population)
    expected_audit = build_s3r1_invariance_audit(
        root,
        preregistration=expected_prereg,
        population=expected_population,
        clusters=expected_clusters,
    )
    expected_core = build_analysis_core_manifest(expected_prereg, expected_population, expected_clusters, expected_audit)
    supplied_components = (
        (preregistration, expected_prereg, "preregistration"),
        (population, expected_population, "population"),
        (clusters, expected_clusters, "clusters"),
        (invariance, expected_audit, "invariance"),
        (core, expected_core, "core"),
    )
    for supplied, expected, label in supplied_components:
        if supplied is not None and dict(supplied) != expected:
            raise OutcomeAnalysisS3R1Error(f"Supplied S3R1 {label} does not match a fresh immutable rebuild")
    prereg = expected_prereg
    primary_population = expected_population
    overlap_clusters = expected_clusters
    audit = expected_audit
    core_manifest = expected_core
    historical_acceptance = inputs["s3"]["acceptance"]
    body = {
        "contract": S3R1_ACCEPTANCE_CONTRACT,
        "schemaVersion": S3R1_SCHEMA_VERSION,
        "milestone": S3R1_MILESTONE,
        "status": "S3R1_PREREGISTRATION_INTEGRITY_HARDENED_AND_COMPOSITE_FREEZE_COMPLETE_CENTRAL_REVIEW_REQUIRED",
        "nextGate": "INDEPENDENT_CENTRAL_REVIEW_BEFORE_ASTRA_PRE_OUTCOME_AUDIT",
        "startingMaster": S3R1_EXPECTED_STARTING_MASTER,
        "supersedesAcceptanceManifestContract": historical_acceptance["contract"],
        "supersedesAcceptanceManifestHash": HISTORICAL_S3_ACCEPTANCE_HASH,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": prereg["preregistrationHash"],
        "primaryPopulationHash": primary_population["primaryPopulationHash"],
        "overlapClustersHash": overlap_clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": audit["analysisPlanInvarianceAuditHash"],
        "analysisCoreManifestHash": core_manifest["analysisCoreManifestHash"],
        "populationAccounting": copy.deepcopy(primary_population["populationCounts"]),
        "marketDataRead": False,
        "outcomeDataRead": False,
        "executionAllowed": False,
        "outcomeAccessFlags": _all_false_flags(),
    }
    return {**body, "acceptanceManifestHash": _canonical_hash(body)}


def timing_specificity_status(
    *,
    actual_hit_count: int,
    minus7_hit_count: int | None,
    plus7_hit_count: int | None,
    actual_complete: bool = True,
    minus7_complete: bool = True,
    plus7_complete: bool = True,
) -> str:
    """Apply the frozen strict comparison to synthetic diagnostic counts."""

    if not actual_complete or not minus7_complete or not plus7_complete:
        return "TIMING_DIAGNOSTIC_INCOMPLETE"
    if minus7_hit_count is None or plus7_hit_count is None:
        return "TIMING_DIAGNOSTIC_INCOMPLETE"
    if actual_hit_count > minus7_hit_count and actual_hit_count > plus7_hit_count:
        return "TIMING_SPECIFICITY_DEMONSTRATED_WITHIN_PREREGISTERED_DIAGNOSTIC"
    return "TIMING_SPECIFICITY_NOT_DEMONSTRATED"


def canonicalize_synthetic_ticks_s3r1(ticks: Iterable[Mapping[str, Any]]) -> list[s3.CanonicalTick]:
    """Deduplicate identical quotes but reject conflicting quotes at one UTC time."""

    materialized = list(ticks)
    parsed = [s3._tick_from_mapping(raw, index) for index, raw in enumerate(materialized)]
    quotes_by_timestamp: dict[datetime, set[tuple[float, float]]] = {}
    for tick in parsed:
        quotes_by_timestamp.setdefault(tick.timestamp_utc, set()).add((tick.bid, tick.ask))
    conflicts = [timestamp for timestamp, quotes in quotes_by_timestamp.items() if len(quotes) > 1]
    if conflicts:
        raise ConflictingSyntheticTickError(s3._utc_text(min(conflicts)))
    return s3.canonicalize_synthetic_ticks(materialized)


def score_synthetic_interval_s3r1(
    ticks: Iterable[Mapping[str, Any]],
    *,
    applying_start_utc: str,
    separating_end_utc: str,
    validation_expected_pair_direction: str,
) -> dict[str, Any]:
    """Use the frozen S3 tick rule with S3R1's conflict hardening."""

    start = s3._parse_utc(applying_start_utc, "applying_start_utc")
    end = s3._parse_utc(separating_end_utc, "separating_end_utc")
    if start >= end:
        raise OutcomeAnalysisS3R1Error("Synthetic interval must be a nonempty half-open UTC range")
    q = s3._expected_direction_unit(validation_expected_pair_direction)
    try:
        canonical = s3.canonicalize_synthetic_ticks_in_interval(
            ticks,
            applying_start_utc=start,
            separating_end_utc=end,
        )
    except s3.SyntheticTickConflictError as exc:
        return {
            "dataStatus": "DATA_CONFLICT_UNSCORABLE",
            "reason": "CONFLICTING_QUOTES_AT_SAME_TIMESTAMP",
            "conflictingTimestampUtc": exc.timestamp_utc,
            "outsideIntervalRescueUsed": False,
        }
    except s3.SyntheticTickQuoteError:
        return {
            "dataStatus": "DATA_NUMERIC_INVALID_UNSCORABLE",
            "reason": "INVALID_IN_INTERVAL_QUOTE",
            "selectedTickCount": 0,
            "outsideIntervalRescueUsed": False,
        }
    selected = [tick for tick in canonical if start <= tick.timestamp_utc < end]
    if len(selected) < 2:
        return {
            "dataStatus": "DATA_UNSCORABLE",
            "reason": "FEWER_THAN_TWO_VALID_IN_INTERVAL_TICKS",
            "selectedTickCount": len(selected),
            "outsideIntervalRescueUsed": False,
        }
    first, last = selected[0], selected[-1]
    if first.timestamp_utc == last.timestamp_utc:
        return {
            "dataStatus": "DATA_UNSCORABLE",
            "reason": "START_AND_END_TICK_SHARE_TIMESTAMP",
            "selectedTickCount": len(selected),
            "outsideIntervalRescueUsed": False,
        }
    log_return, numeric_reason = s3._numeric_return_or_invalid(first, last)
    if numeric_reason is not None:
        return {
            "dataStatus": "DATA_NUMERIC_INVALID_UNSCORABLE",
            "reason": numeric_reason,
            "selectedTickCount": len(selected),
            "outsideIntervalRescueUsed": False,
        }
    start_midpoint = first.midpoint
    end_midpoint = last.midpoint
    realized = "UP" if log_return > 0 else "DOWN" if log_return < 0 else "ZERO_MOVE"
    return {
        "dataStatus": "SCORABLE_SYNTHETIC_ONLY",
        "selectedTickCount": len(selected),
        "startTickUtc": s3._utc_text(first.timestamp_utc),
        "endTickUtc": s3._utc_text(last.timestamp_utc),
        "startMidpoint": start_midpoint,
        "endMidpoint": end_midpoint,
        "logReturn": log_return,
        "realizedDirection": realized,
        "hit": int(q * log_return > 0),
        "startAlignmentGapSeconds": (first.timestamp_utc - start).total_seconds(),
        "endAlignmentGapSeconds": (end - last.timestamp_utc).total_seconds(),
        "outsideIntervalRescueUsed": False,
    }


def write_s3r1_artifacts(resource_root: Path = PROJECT_ROOT, *, outcome_source: object | None = None) -> dict[str, Path]:
    """Materialize the successor package only; any outcome attachment is rejected."""

    if outcome_source is not None:
        raise OutcomeAnalysisS3R1Error("S3R1 materialization cannot accept a market provider, outcome file, or tick source")
    root = Path(resource_root).resolve()
    preregistration = build_s3r1_preregistration(root)
    validate_s3r1_preregistration(preregistration)
    population = build_s3r1_primary_population(root)
    clusters = build_s3r1_overlap_clusters(root, population=population)
    invariance = build_s3r1_invariance_audit(root, preregistration=preregistration, population=population, clusters=clusters)
    core = build_analysis_core_manifest(preregistration, population, clusters, invariance)
    acceptance = build_s3r1_acceptance_manifest(root, preregistration=preregistration, population=population, clusters=clusters, invariance=invariance, core=core)
    artifacts = {
        "preregistration": root / DEFAULT_PREREGISTRATION_PATH.relative_to(PROJECT_ROOT),
        "schema": root / DEFAULT_SCHEMA_PATH.relative_to(PROJECT_ROOT),
        "population": root / DEFAULT_PRIMARY_POPULATION_PATH.relative_to(PROJECT_ROOT),
        "clusters": root / DEFAULT_OVERLAP_CLUSTERS_PATH.relative_to(PROJECT_ROOT),
        "invariance": root / DEFAULT_INVARIANCE_PATH.relative_to(PROJECT_ROOT),
        "core": root / DEFAULT_CORE_MANIFEST_PATH.relative_to(PROJECT_ROOT),
        "acceptance": root / DEFAULT_ACCEPTANCE_PATH.relative_to(PROJECT_ROOT),
        "report": root / DEFAULT_REPORT_PATH.relative_to(PROJECT_ROOT),
    }
    _write_json(artifacts["preregistration"], preregistration)
    _write_json(artifacts["schema"], build_s3r1_schema(preregistration))
    _write_json(artifacts["population"], population)
    _write_json(artifacts["clusters"], clusters)
    _write_json(artifacts["invariance"], invariance)
    _write_json(artifacts["core"], core)
    _write_json(artifacts["acceptance"], acceptance)
    artifacts["report"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["report"].write_text(render_s3r1_report(preregistration, population, clusters, invariance, core, acceptance), encoding="utf-8")
    return artifacts


def render_s3r1_report(
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
    core: Mapping[str, Any],
    acceptance: Mapping[str, Any],
) -> str:
    counts = population["populationCounts"]
    lines = [
        "# MO-R4A-S3R1 Preregistration Integrity Hardening",
        "",
        "S3R1 is a successor to the accepted outcome-blind S3 package. The four findings were integrity issues, not scientific-design changes: the nested schema is now closed, one acyclic core hash represents the complete analysis package, time-shift comparison is deterministic, and the conditional permutation-null assumption is explicit.",
        "",
        f"Historical S3 preregistration: `{HISTORICAL_S3_PREREGISTRATION_HASH}`",
        f"S3R1 preregistration: `{preregistration['preregistrationHash']}`",
        f"S3R1 primary population: `{population['primaryPopulationHash']}`",
        f"S3R1 overlap clusters: `{clusters['overlapClustersHash']}`",
        f"S3R1 invariance audit: `{invariance['analysisPlanInvarianceAuditHash']}`",
        f"Analysis core manifest: `{core['analysisCoreManifestHash']}`",
        f"S3R1 acceptance manifest: `{acceptance['acceptanceManifestHash']}`",
        "",
        "## Package And Population",
        "",
        f"The accepted 24-event population remains 24 total ({counts['usdPrimaryCount']} USD and {counts['jpyPrimaryCount']} JPY primary rows after the frozen non-primary rows are accounted for), 14 directional, 13 primary market-scorable, one structural weekend exclusion, three NEUTRAL, and seven abstentions. Side-local primary counts remain USD 5 (1 SUPPORTIVE / 4 ADVERSE) and JPY 8 (7 SUPPORTIVE / 1 ADVERSE).",
        "",
        "The exact excluded event remains `TN_BD340A6100B173B5F254EDC1`, USD SUPPORTIVE, `[2025-04-05T01:45:04Z, 2025-04-05T12:34:35Z)`, complete Saturday UTC. It is retained but never replaced or scored.",
        "",
        "The four connected half-open clusters remain C1=5, C2=1, C3=2, and C4=5. Touching endpoints are not overlap.",
        "",
        "## Hash Hierarchy",
        "",
        "Level 1 consists of the S3R1 preregistration, primary-population, overlap-cluster, and invariance hashes. Level 2 computes `analysisCoreManifestHash` from canonical JSON containing the six S2R1-R1 upstream hashes and those four Level-1 hashes. Level 3 acceptance binds the core hash plus status, next gate, and all false access flags. The acceptance hash is deliberately excluded from the core input, so there is no cycle.",
        "",
        "## Deterministic Diagnostics",
        "",
        "The timing diagnostic uses exactly -7 and +7 calendar days, preserving side, frozen label, UTC clock, duration, half-open boundaries, tick validity, midpoint, and return rules. It is demonstrated only when all actual and shifted sets are complete and `H_actual` is strictly greater than both controls. Any tie is `TIMING_SPECIFICITY_NOT_DEMONSTRATED`; an incomplete shifted set is `TIMING_DIAGNOSTIC_INCOMPLETE`. This status never enters primary survival.",
        "",
        f"The permutation assumption is `{preregistration['permutationNullAssumption']['identifier']}`: labels are conditionally exchangeable within USD and independently within JPY, not randomized in the original experiment. The exact universe remains 40 assignments.",
        "",
        "Timestamp metadata is declarative frozen metadata, not Git chronology or proof of human conception or absence of outcome exposure. The fixed authored timestamp is retained without `datetime.now()` regeneration.",
        "",
        "Conflicting bid/ask records at one UTC timestamp are `DATA_CONFLICT_UNSCORABLE`; they are never averaged or resolved by source order. Identical duplicates may be deduplicated. A primary data conflict later invalidates the 13-event evaluation rather than shrinking its denominator.",
        "",
        "## Boundary And Gate",
        "",
        "No provider client, price/tick/candle/outcome loader, real result, S4 evaluator, Astra run, Founder Review input, SBC path, signed wave, pair resultant, magnitude, score, Auto Suggest, ML, MT5, or execution path exists in S3R1. All 16 access flags remain false. The package is ready for independent central review before the Astra pre-outcome adversarial audit; Astra and S4 remain blocked.",
        "",
    ]
    return "\n".join(lines)
