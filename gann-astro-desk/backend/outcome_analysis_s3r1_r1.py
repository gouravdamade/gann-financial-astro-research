"""MO-R4A-S3R1-R1 pre-outcome corrections and acquisition contract.

This successor keeps the S3R1 event population and scientific design frozen
while hardening acceptance validation and synthetic diagnostic data handling.
It deliberately contains no provider client, market-data reader, outcome
loader, S4 evaluator, or product integration.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import outcome_analysis_s3 as s3
import outcome_analysis_s3r1 as s3r1


S3R1_R1_PREREGISTRATION_CONTRACT = "MO_R4A_S3R1_R1_OUTCOME_ANALYSIS_PREREGISTRATION_V1"
S3R1_R1_PRIMARY_POPULATION_CONTRACT = "MO_R4A_S3R1_R1_PRIMARY_ANALYSIS_POPULATION_V1"
S3R1_R1_OVERLAP_CLUSTERS_CONTRACT = "MO_R4A_S3R1_R1_OVERLAP_CLUSTERS_V1"
S3R1_R1_INVARIANCE_AUDIT_CONTRACT = "MO_R4A_S3R1_R1_ANALYSIS_PLAN_INVARIANCE_AUDIT_V1"
S3R1_R1_CORE_MANIFEST_CONTRACT = "MO_R4A_S3R1_R1_FROZEN_ANALYSIS_PACKAGE_V1"
S3R1_R1_ACCEPTANCE_CONTRACT = "MO_R4A_S3R1_R1_OUTCOME_ANALYSIS_PREREGISTRATION_ACCEPTANCE_V1"
S3R1_R1_ACQUISITION_CONTRACT = "MO_R4A_S3R1_R1_MARKET_DATA_ACQUISITION_CONTRACT_V1"
S3R1_R1_DISPOSITION_CONTRACT = "MO_R4A_S3R1_R1_ASTRA_FINDINGS_DISPOSITION_V1"
S3R1_R1_SCHEMA_VERSION = 1
S3R1_R1_MILESTONE = "MO-R4A-S3R1-R1"
S3R1_R1_EXPECTED_STARTING_MASTER = "ba06e61a8575c2e7ebe75f51fcf575740a37e029"
S3R1_R1_AUTHORED_AT_UTC = "2026-09-11T00:00:00Z"
S3R1_R1_TIMESTAMP_SEMANTICS = "DECLARATIVE_FROZEN_METADATA_NOT_GIT_COMMIT_CHRONOLOGY"

HISTORICAL_S3R1_PREREGISTRATION_HASH = "CBE8E351C1F57E5717343E92D71C1CFDBFB49C0829FF2430BD5CDA3CECD7F444"
HISTORICAL_S3R1_PRIMARY_POPULATION_HASH = "DAFA64956255F7AD2F91108DD08E488ED4026CC2CE488F3F37861EA82A49C73E"
HISTORICAL_S3R1_OVERLAP_CLUSTERS_HASH = "4FE7315F4C30E61A4E40158A3D41E8B36A89957A44BAD8C3E4D7FBFFA3580057"
HISTORICAL_S3R1_INVARIANCE_HASH = "8062FF0C752D35C5D2D9A144BCD35686DAD5E4F88CA64FB4E66BE356B0409974"
HISTORICAL_S3R1_CORE_HASH = "7AC7DE6EA59278B89E76B80E1EC0A46A8707AB4EAE4E95DFE7E627C56420D7BE"
HISTORICAL_S3R1_ACCEPTANCE_HASH = "79ED3C79B4F913C4B23500CF18EEFDF4EED6B53B37A7ACE5548B34074FDA4F7A"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"

DEFAULT_ACQUISITION_PATH = MACHINE_INTERPRETATION_ROOT / "market_data_acquisition_contract_s3r1_r1_v1.json"
DEFAULT_PREREGISTRATION_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r1_v1.json"
DEFAULT_SCHEMA_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r1_v1.schema.json"
DEFAULT_PRIMARY_POPULATION_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r1_primary_analysis_population.json"
DEFAULT_OVERLAP_CLUSTERS_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r1_overlap_clusters.json"
DEFAULT_INVARIANCE_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r1_analysis_plan_invariance_audit.json"
DEFAULT_CORE_MANIFEST_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r1_frozen_analysis_package.json"
DEFAULT_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r1_outcome_analysis_preregistration.json"
DEFAULT_DISPOSITION_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r1_astra_findings_disposition.json"
DEFAULT_REPORT_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S3R1_R1_ASTRA_PRE_OUTCOME_CORRECTIONS.md"

EXPECTED_UPSTREAM_HASHES = copy.deepcopy(s3r1.EXPECTED_UPSTREAM_HASHES)
ACCESS_FLAGS = tuple(s3r1.ACCESS_FLAGS)


class OutcomeAnalysisS3R1R1Error(ValueError):
    """Raised when an R1 artifact is not an exact immutable successor."""


def _canonical_hash(value: Any) -> str:
    return s3._canonical_hash(value)


def _without_hash(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    return {name: copy.deepcopy(item) for name, item in value.items() if name != key}


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OutcomeAnalysisS3R1R1Error(f"Missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OutcomeAnalysisS3R1R1Error(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(value, dict):
        raise OutcomeAnalysisS3R1R1Error(f"{label} must be a JSON object")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _all_false_flags() -> dict[str, bool]:
    return {key: False for key in ACCESS_FLAGS}


def _assert_hash(value: Any, label: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789ABCDEF" for char in value):
        raise OutcomeAnalysisS3R1R1Error(f"{label} must be an uppercase SHA-256")


def _historical_s3r1_components(root: Path) -> dict[str, dict[str, Any]]:
    """Prove the predecessor package is unchanged before deriving its successor."""

    paths = {
        "preregistration": root / s3r1.DEFAULT_PREREGISTRATION_PATH.relative_to(s3r1.PROJECT_ROOT),
        "population": root / s3r1.DEFAULT_PRIMARY_POPULATION_PATH.relative_to(s3r1.PROJECT_ROOT),
        "clusters": root / s3r1.DEFAULT_OVERLAP_CLUSTERS_PATH.relative_to(s3r1.PROJECT_ROOT),
        "invariance": root / s3r1.DEFAULT_INVARIANCE_PATH.relative_to(s3r1.PROJECT_ROOT),
        "core": root / s3r1.DEFAULT_CORE_MANIFEST_PATH.relative_to(s3r1.PROJECT_ROOT),
        "acceptance": root / s3r1.DEFAULT_ACCEPTANCE_PATH.relative_to(s3r1.PROJECT_ROOT),
    }
    values = {name: _read_json(path, f"historical S3R1 {name}") for name, path in paths.items()}
    expected_hashes = {
        "preregistration": ("preregistrationHash", HISTORICAL_S3R1_PREREGISTRATION_HASH),
        "population": ("primaryPopulationHash", HISTORICAL_S3R1_PRIMARY_POPULATION_HASH),
        "clusters": ("overlapClustersHash", HISTORICAL_S3R1_OVERLAP_CLUSTERS_HASH),
        "invariance": ("analysisPlanInvarianceAuditHash", HISTORICAL_S3R1_INVARIANCE_HASH),
        "core": ("analysisCoreManifestHash", HISTORICAL_S3R1_CORE_HASH),
        "acceptance": ("acceptanceManifestHash", HISTORICAL_S3R1_ACCEPTANCE_HASH),
    }
    for name, value in values.items():
        key, expected = expected_hashes[name]
        if value.get(key) != expected or _canonical_hash(_without_hash(value, key)) != expected:
            raise OutcomeAnalysisS3R1R1Error(f"historical S3R1 {name} no longer has its accepted hash")
    return values


def _historical_derived_components(root: Path) -> dict[str, dict[str, Any]]:
    """Independently regenerate the predecessor components for equality checks."""

    preregistration = s3r1.build_s3r1_preregistration(root)
    population = s3r1.build_s3r1_primary_population(root)
    clusters = s3r1.build_s3r1_overlap_clusters(root, population=population)
    invariance = s3r1.build_s3r1_invariance_audit(root, preregistration=preregistration, population=population, clusters=clusters)
    core = s3r1.build_analysis_core_manifest(preregistration, population, clusters, invariance)
    return {
        "preregistration": preregistration,
        "population": population,
        "clusters": clusters,
        "invariance": invariance,
        "core": core,
    }


def _assert_predecessor_components(root: Path) -> dict[str, dict[str, Any]]:
    historical = _historical_s3r1_components(root)
    derived = _historical_derived_components(root)
    for name, value in derived.items():
        if value != historical[name]:
            raise OutcomeAnalysisS3R1R1Error(f"historical S3R1 {name} differs from its immutable builder")
    return historical


def _interval_record(row: Mapping[str, Any], *, horizon: str, shift_days: int) -> dict[str, Any]:
    if shift_days:
        shifted = s3.shift_primary_interval(row, shift_days)
    else:
        shifted = {
            "applyingStartUtc": row["applyingStartUtc"],
            "separatingEndUtc": row["separatingEndUtc"],
        }
    start = s3._parse_utc(shifted["applyingStartUtc"], "acquisition applyingStartUtc")
    end = s3._parse_utc(shifted["separatingEndUtc"], "acquisition separatingEndUtc")
    return {
        "intervalId": f"{row['eventId']}::{horizon}",
        "eventId": row["eventId"],
        "horizon": horizon,
        "shiftCalendarDays": shift_days,
        "sideIdentity": row["sideIdentity"],
        "frozenLabel": row["pressureState"],
        "analysisDisposition": row["analysisDisposition"],
        "applyingStartUtc": shifted["applyingStartUtc"],
        "separatingEndUtc": shifted["separatingEndUtc"],
        "durationSeconds": int((end - start).total_seconds()),
        "halfOpen": True,
    }


def build_market_data_acquisition_contract(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Declare the later request contract without accessing a provider."""

    root = Path(resource_root).resolve()
    predecessor = _assert_predecessor_components(root)
    rows = predecessor["population"]["primaryMarketScorableRows"]
    intervals = [
        _interval_record(row, horizon="ACTUAL", shift_days=0)
        for row in rows
    ]
    intervals.extend(_interval_record(row, horizon="MINUS_7", shift_days=-7) for row in rows)
    intervals.extend(_interval_record(row, horizon="PLUS_7", shift_days=7) for row in rows)
    if len(intervals) != 39:
        raise OutcomeAnalysisS3R1R1Error("Acquisition contract must contain exactly 39 frozen intervals")
    body = {
        "contract": S3R1_R1_ACQUISITION_CONTRACT,
        "schemaVersion": S3R1_R1_SCHEMA_VERSION,
        "milestone": S3R1_R1_MILESTONE,
        "status": "PARTIALLY_RESOLVED_OUTCOME_UNLOCK_BLOCKED",
        "providerIdentity": "DUKASCOPY_HISTORICAL_USDJPY_TICK_SERVICE",
        "productIdentifier": "DUKASCOPY_HISTORICAL_USDJPY_TICK_SERVICE",
        "instrument": "USDJPY",
        "symbol": "USDJPY",
        "quoteConvention": "JPY_PER_USD",
        "timeScale": "UTC",
        "requestPartitioning": {
            "rule": "ONE_EXACT_REQUEST_SCOPE_PER_FROZEN_EVENT_INTERVAL_AND_HORIZON",
            "boundaries": "[applyingStartUtc, separatingEndUtc)",
            "partitionCount": 39,
            "partitionDerivation": "DETERMINISTIC_FROM_FROZEN_PRIMARY_ROWS_AND_EXACT_MINUS7_PLUS7_SHIFTS",
            "providerSpecificPagination": "UNRESOLVED_PENDING_PROVIDER_PROTOCOL_CLOSURE",
        },
        "rawTransport": {
            "protocol": "UNRESOLVED_PENDING_PROVIDER_PROTOCOL_CLOSURE",
            "compression": "UNRESOLVED_PENDING_PROVIDER_PROTOCOL_CLOSURE",
            "recordFormat": "TICK_RECORD_REQUIRED",
            "rawResponseRetention": "REQUIRED_AT_OUTCOME_PHASE",
        },
        "timestampEncoding": {
            "inputField": "timestampUtc",
            "requiredEncoding": "EXPLICIT_ISO8601_UTC",
            "malformedTimestamp": "MALFORMED_TIMESTAMP_INPUT_ERROR",
            "providerEpochOrTextEncoding": "UNRESOLVED_PENDING_PROVIDER_PROTOCOL_CLOSURE",
        },
        "priceEncoding": {
            "fields": ["bid", "ask"],
            "providerPrecision": "UNRESOLVED_PENDING_PROVIDER_PROTOCOL_CLOSURE",
            "finitePositive": True,
            "askGreaterThanOrEqualBid": True,
            "midpointFormula": "bid + (ask - bid) / 2",
        },
        "parser": {
            "identity": "UNRESOLVED_PENDING_PROVIDER_PROTOCOL_CLOSURE",
            "version": "UNRESOLVED_PENDING_PROVIDER_PROTOCOL_CLOSURE",
            "sourceHash": "REQUIRED_AT_OUTCOME_PHASE",
        },
        "duplicateAndConflictPolicy": {
            "identicalDuplicate": "DEDUPLICATE_WITHOUT_AVERAGING",
            "conflictingSameTimestampInScope": "DATA_CONFLICT_UNSCORABLE",
            "outsideScopeConflict": "IRRELEVANT_TO_THIS_INTERVAL",
            "sourceOrderResolution": False,
        },
        "revisionPolicy": {
            "providerRevisionPolicy": "UNRESOLVED_PENDING_PROVIDER_PROTOCOL_CLOSURE",
            "manualRepairAllowed": False,
            "fallbackProviderAllowed": False,
            "substitutionAllowed": False,
            "outcomeDrivenRetryAllowed": False,
            "dataRevisionAfterCapture": "REQUIRES_NEW_REVIEWED_ACQUISITION_RECORD",
        },
        "futureCaptureRequirements": {
            "rawBytesSha256": "REQUIRED_AT_OUTCOME_PHASE",
            "parsedTicksSha256": "REQUIRED_AT_OUTCOME_PHASE",
            "rawRetention": "RETAIN_UNCHANGED_FOR_AUDIT",
            "retrievalMetadata": "REQUIRED_AT_OUTCOME_PHASE",
        },
        "frozenIntervalSet": {
            "actualCount": 13,
            "minus7Count": 13,
            "plus7Count": 13,
            "totalCount": len(intervals),
            "eventIdsPreserved": True,
            "sideAndLabelPreserved": True,
            "durationPreserved": True,
            "intervals": intervals,
        },
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
        "executionAllowed": False,
    }
    return {**body, "marketDataAcquisitionContractHash": _canonical_hash(body)}


def build_s3r1_r1_preregistration(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_predecessor_components(root)
    historical = predecessor["preregistration"]
    acquisition = build_market_data_acquisition_contract(root)
    body = copy.deepcopy(historical)
    body.pop("preregistrationHash", None)
    body.update(
        {
            "contract": S3R1_R1_PREREGISTRATION_CONTRACT,
            "schemaVersion": S3R1_R1_SCHEMA_VERSION,
            "milestone": S3R1_R1_MILESTONE,
            "startingMaster": S3R1_R1_EXPECTED_STARTING_MASTER,
            "preregistrationAuthoredAtUtc": S3R1_R1_AUTHORED_AT_UTC,
            "timestampSemantics": S3R1_R1_TIMESTAMP_SEMANTICS,
            "status": "S3R1_R1_CODE_CORRECTIONS_COMPLETE_ACQUISITION_CONTRACT_INCOMPLETE",
            "nextGate": "CENTRAL_REVIEW_PROVIDER_CONTRACT_CLOSURE_REQUIRED",
            "supersedesPreregistrationContract": historical["contract"],
            "supersedesPreregistrationHash": HISTORICAL_S3R1_PREREGISTRATION_HASH,
            "supersedesAcceptanceManifestHash": HISTORICAL_S3R1_ACCEPTANCE_HASH,
            "correctionReason": "ASTRA_PRE_OUTCOME_CORRECTIONS_WITHOUT_SCIENTIFIC_DESIGN_CHANGE",
            "marketDataAcquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
            "numericInvalidityPolicy": {
                "stableMidpointFormula": "bid + (ask - bid) / 2",
                "stableLogReturnFormula": "log(endMidpoint) - log(startMidpoint)",
                "finiteChecks": ["bid", "ask", "midpoint", "startLog", "endLog", "logReturn"],
                "invalidStatus": "DATA_NUMERIC_INVALID_UNSCORABLE",
                "zeroMoveRequiresFiniteExactZero": True,
                "denominatorShrinkAllowed": False,
            },
            "intervalScopedConflictPolicy": {
                "selection": "[applyingStartUtc, separatingEndUtc)",
                "timestampValidation": "PARSE_ALL_TIMESTAMPS_AND_FAIL_TYPED_ON_MALFORMED",
                "outsideInvalidPrice": "IGNORED_FOR_THIS_INTERVAL",
                "outsideConflict": "IGNORED_FOR_THIS_INTERVAL",
                "insideConflict": "DATA_CONFLICT_UNSCORABLE",
                "outsideIntervalRescueAllowed": False,
            },
            "astraCorrectionLineage": {
                "auditVerdict": "PRE_OUTCOME_CORRECTION_REQUIRED",
                "highFinding": "ACCEPTANCE_BUILDER_SUPPLIED_COMPONENT_BYPASS",
                "mediumFindings": ["NUMERIC_INVALIDITY", "INTERVAL_SCOPED_DATA_QUALITY", "ACQUISITION_CONTRACT_CLOSURE"],
                "scientificDesignChanged": False,
                "marketOutcomeRead": False,
            },
        }
    )
    return {**body, "preregistrationHash": _canonical_hash(body)}


def build_s3r1_r1_schema(preregistration: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = copy.deepcopy(preregistration) if preregistration is not None else build_s3r1_r1_preregistration(PROJECT_ROOT)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": S3R1_R1_PREREGISTRATION_CONTRACT,
        "title": S3R1_R1_PREREGISTRATION_CONTRACT,
        **s3r1._schema_for_value(payload),
    }


def validate_json_schema_instance(value: Any, schema: Mapping[str, Any], path: str = "$") -> None:
    try:
        s3r1.validate_json_schema_instance(value, schema, path)
    except s3r1.OutcomeAnalysisS3R1Error as exc:
        raise OutcomeAnalysisS3R1R1Error(str(exc)) from exc


def _require_exact(value: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    if dict(value) != dict(expected):
        raise OutcomeAnalysisS3R1R1Error(f"{label} does not match a fresh immutable rebuild")


def validate_s3r1_r1_preregistration(value: Mapping[str, Any], resource_root: Path = PROJECT_ROOT) -> None:
    expected = build_s3r1_r1_preregistration(resource_root)
    validate_json_schema_instance(value, build_s3r1_r1_schema(expected))
    _require_exact(value, expected, "S3R1-R1 preregistration")


def build_s3r1_r1_primary_population(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_predecessor_components(root)
    historical = predecessor["population"]
    preregistration = build_s3r1_r1_preregistration(root)
    body = copy.deepcopy(historical)
    body.pop("primaryPopulationHash", None)
    body.update(
        {
            "contract": S3R1_R1_PRIMARY_POPULATION_CONTRACT,
            "schemaVersion": S3R1_R1_SCHEMA_VERSION,
            "milestone": S3R1_R1_MILESTONE,
            "supersedesPrimaryPopulationContract": historical["contract"],
            "supersedesPrimaryPopulationHash": HISTORICAL_S3R1_PRIMARY_POPULATION_HASH,
            "preregistrationHash": preregistration["preregistrationHash"],
        }
    )
    return {**body, "primaryPopulationHash": _canonical_hash(body)}


def validate_s3r1_r1_primary_population(value: Mapping[str, Any], resource_root: Path = PROJECT_ROOT) -> None:
    _require_exact(value, build_s3r1_r1_primary_population(resource_root), "S3R1-R1 primary population")


def build_s3r1_r1_overlap_clusters(
    resource_root: Path = PROJECT_ROOT,
    *,
    population: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_predecessor_components(root)
    historical = predecessor["clusters"]
    primary_population = copy.deepcopy(population) if population is not None else build_s3r1_r1_primary_population(root)
    derived = s3.derive_overlap_clusters(primary_population["primaryMarketScorableRows"])
    if derived != historical["clusters"]:
        raise OutcomeAnalysisS3R1R1Error("S3R1-R1 overlap derivation changed the accepted four clusters")
    body = copy.deepcopy(historical)
    body.pop("overlapClustersHash", None)
    body.update(
        {
            "contract": S3R1_R1_OVERLAP_CLUSTERS_CONTRACT,
            "schemaVersion": S3R1_R1_SCHEMA_VERSION,
            "milestone": S3R1_R1_MILESTONE,
            "supersedesOverlapClustersContract": historical["contract"],
            "supersedesOverlapClustersHash": HISTORICAL_S3R1_OVERLAP_CLUSTERS_HASH,
            "primaryPopulationHash": primary_population["primaryPopulationHash"],
        }
    )
    return {**body, "overlapClustersHash": _canonical_hash(body)}


def validate_s3r1_r1_overlap_clusters(value: Mapping[str, Any], resource_root: Path = PROJECT_ROOT) -> None:
    _require_exact(value, build_s3r1_r1_overlap_clusters(resource_root), "S3R1-R1 overlap clusters")


def build_s3r1_r1_invariance_audit(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_predecessor_components(root)
    historical = predecessor["invariance"]
    prereg = copy.deepcopy(preregistration) if preregistration is not None else build_s3r1_r1_preregistration(root)
    primary_population = copy.deepcopy(population) if population is not None else build_s3r1_r1_primary_population(root)
    overlap_clusters = copy.deepcopy(clusters) if clusters is not None else build_s3r1_r1_overlap_clusters(root, population=primary_population)
    old = s3r1.build_s3r1_invariance_audit(root)
    if old != historical:
        raise OutcomeAnalysisS3R1R1Error("historical S3R1 invariance audit changed during R1 derivation")
    body = copy.deepcopy(historical)
    body.pop("analysisPlanInvarianceAuditHash", None)
    body.update(
        {
            "contract": S3R1_R1_INVARIANCE_AUDIT_CONTRACT,
            "schemaVersion": S3R1_R1_SCHEMA_VERSION,
            "milestone": S3R1_R1_MILESTONE,
            "supersedesInvarianceAuditContract": historical["contract"],
            "supersedesInvarianceAuditHash": HISTORICAL_S3R1_INVARIANCE_HASH,
            "preregistrationHash": prereg["preregistrationHash"],
            "primaryPopulationHash": primary_population["primaryPopulationHash"],
            "overlapClustersHash": overlap_clusters["overlapClustersHash"],
        }
    )
    return {**body, "analysisPlanInvarianceAuditHash": _canonical_hash(body)}


def validate_s3r1_r1_invariance_audit(value: Mapping[str, Any], resource_root: Path = PROJECT_ROOT) -> None:
    _require_exact(value, build_s3r1_r1_invariance_audit(resource_root), "S3R1-R1 invariance audit")


def compute_analysis_core_manifest_hash(
    upstream_hashes: Mapping[str, str],
    preregistration_hash: str,
    primary_population_hash: str,
    overlap_clusters_hash: str,
    analysis_plan_invariance_audit_hash: str,
    market_data_acquisition_contract_hash: str,
) -> str:
    body = {
        "contract": S3R1_R1_CORE_MANIFEST_CONTRACT,
        "schemaVersion": S3R1_R1_SCHEMA_VERSION,
        "milestone": S3R1_R1_MILESTONE,
        "upstreamHashes": dict(upstream_hashes),
        "preregistrationHash": preregistration_hash,
        "primaryPopulationHash": primary_population_hash,
        "overlapClustersHash": overlap_clusters_hash,
        "analysisPlanInvarianceAuditHash": analysis_plan_invariance_audit_hash,
        "marketDataAcquisitionContractHash": market_data_acquisition_contract_hash,
    }
    return _canonical_hash(body)


def build_analysis_core_manifest(
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
    acquisition_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    acquisition = copy.deepcopy(acquisition_contract) if acquisition_contract is not None else build_market_data_acquisition_contract(PROJECT_ROOT)
    for value, key in (
        (preregistration, "preregistrationHash"),
        (population, "primaryPopulationHash"),
        (clusters, "overlapClustersHash"),
        (invariance, "analysisPlanInvarianceAuditHash"),
        (acquisition, "marketDataAcquisitionContractHash"),
    ):
        if value.get(key) != _canonical_hash(_without_hash(value, key)):
            raise OutcomeAnalysisS3R1R1Error(f"Invalid S3R1-R1 component hash: {key}")
    if preregistration.get("marketDataAcquisitionContractHash") != acquisition["marketDataAcquisitionContractHash"]:
        raise OutcomeAnalysisS3R1R1Error("Preregistration and acquisition contract hashes differ")
    body = {
        "contract": S3R1_R1_CORE_MANIFEST_CONTRACT,
        "schemaVersion": S3R1_R1_SCHEMA_VERSION,
        "milestone": S3R1_R1_MILESTONE,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": preregistration["preregistrationHash"],
        "primaryPopulationHash": population["primaryPopulationHash"],
        "overlapClustersHash": clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
    }
    return {
        **body,
        "analysisCoreManifestHash": compute_analysis_core_manifest_hash(
            body["upstreamHashes"],
            body["preregistrationHash"],
            body["primaryPopulationHash"],
            body["overlapClustersHash"],
            body["analysisPlanInvarianceAuditHash"],
            body["marketDataAcquisitionContractHash"],
        ),
    }


def build_s3r1_r1_core_manifest(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    acquisition = build_market_data_acquisition_contract(root)
    preregistration = build_s3r1_r1_preregistration(root)
    population = build_s3r1_r1_primary_population(root)
    clusters = build_s3r1_r1_overlap_clusters(root, population=population)
    invariance = build_s3r1_r1_invariance_audit(root, preregistration=preregistration, population=population, clusters=clusters)
    return build_analysis_core_manifest(preregistration, population, clusters, invariance, acquisition)


def validate_analysis_core_manifest(value: Mapping[str, Any], resource_root: Path = PROJECT_ROOT) -> None:
    _require_exact(value, build_s3r1_r1_core_manifest(resource_root), "S3R1-R1 analysis core")


def build_s3r1_r1_acceptance_manifest(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
    invariance: Mapping[str, Any] | None = None,
    core: Mapping[str, Any] | None = None,
    acquisition_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    _assert_predecessor_components(root)
    expected_acquisition = build_market_data_acquisition_contract(root)
    expected_preregistration = build_s3r1_r1_preregistration(root)
    expected_population = build_s3r1_r1_primary_population(root)
    expected_clusters = build_s3r1_r1_overlap_clusters(root, population=expected_population)
    expected_invariance = build_s3r1_r1_invariance_audit(
        root,
        preregistration=expected_preregistration,
        population=expected_population,
        clusters=expected_clusters,
    )
    expected_core = build_analysis_core_manifest(
        expected_preregistration,
        expected_population,
        expected_clusters,
        expected_invariance,
        expected_acquisition,
    )
    supplied_components = (
        (acquisition_contract, expected_acquisition, "acquisition contract"),
        (preregistration, expected_preregistration, "preregistration"),
        (population, expected_population, "population"),
        (clusters, expected_clusters, "clusters"),
        (invariance, expected_invariance, "invariance"),
        (core, expected_core, "core"),
    )
    for supplied, expected, label in supplied_components:
        if supplied is not None:
            _require_exact(supplied, expected, f"Supplied S3R1-R1 {label}")
    body = {
        "contract": S3R1_R1_ACCEPTANCE_CONTRACT,
        "schemaVersion": S3R1_R1_SCHEMA_VERSION,
        "milestone": S3R1_R1_MILESTONE,
        "status": "PRE_OUTCOME_ACQUISITION_CONTRACT_INCOMPLETE",
        "nextGate": "CENTRAL_REVIEW",
        "startingMaster": S3R1_R1_EXPECTED_STARTING_MASTER,
        "supersedesAcceptanceManifestContract": s3r1.S3R1_ACCEPTANCE_CONTRACT,
        "supersedesAcceptanceManifestHash": HISTORICAL_S3R1_ACCEPTANCE_HASH,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": expected_preregistration["preregistrationHash"],
        "primaryPopulationHash": expected_population["primaryPopulationHash"],
        "overlapClustersHash": expected_clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": expected_invariance["analysisPlanInvarianceAuditHash"],
        "analysisCoreManifestHash": expected_core["analysisCoreManifestHash"],
        "marketDataAcquisitionContractHash": expected_acquisition["marketDataAcquisitionContractHash"],
        "acquisitionStatus": expected_acquisition["status"],
        "populationAccounting": copy.deepcopy(expected_population["populationCounts"]),
        "marketDataRead": False,
        "outcomeDataRead": False,
        "executionAllowed": False,
        "outcomeAccessFlags": _all_false_flags(),
    }
    return {**body, "acceptanceManifestHash": _canonical_hash(body)}


def validate_s3r1_r1_acceptance_manifest(value: Mapping[str, Any], resource_root: Path = PROJECT_ROOT) -> None:
    _require_exact(value, build_s3r1_r1_acceptance_manifest(resource_root), "S3R1-R1 acceptance")


def build_s3r1_r1_astra_disposition(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    preregistration = build_s3r1_r1_preregistration(root)
    acquisition = build_market_data_acquisition_contract(root)
    body = {
        "contract": S3R1_R1_DISPOSITION_CONTRACT,
        "schemaVersion": S3R1_R1_SCHEMA_VERSION,
        "milestone": S3R1_R1_MILESTONE,
        "verdict": "PRE_OUTCOME_CORRECTION_REQUIRED",
        "branch": "BRANCH_B",
        "findings": [
            {
                "findingId": "ASTRA_S3R1_ACCEPTANCE_BUILDER_SUPPLIED_CORE_BYPASS",
                "findingType": "HIGH_ACCEPTANCE_VALIDATION_BYPASS",
                "severity": "HIGH",
                "status": "CORRECTED",
                "affectedCode": "outcome_analysis_s3r1.build_s3r1_acceptance_manifest",
                "correction": "Freshly rebuild and compare every supplied component before acceptance accounting.",
                "regression": "Astra mutation matrix A-F",
                "scientificDesignChanged": False,
                "marketOutcomeRead": False,
            },
            {
                "findingId": "ASTRA_S3R1_NUMERIC_INVALIDITY",
                "findingType": "MEDIUM_NUMERICAL_INVALIDITY",
                "severity": "MEDIUM",
                "status": "CORRECTED",
                "affectedCode": "outcome_analysis_s3 and outcome_analysis_s3r1 synthetic evaluator",
                "correction": "Stable midpoint and log subtraction with finite checks and DATA_NUMERIC_INVALID_UNSCORABLE.",
                "regression": "Numeric invalidity matrix",
                "scientificDesignChanged": False,
                "marketOutcomeRead": False,
            },
            {
                "findingId": "ASTRA_S3R1_ACQUISITION_CONTRACT_REQUIREMENTS",
                "findingType": "MEDIUM_PRE_REQUEST_ACQUISITION_REQUIREMENTS",
                "severity": "MEDIUM",
                "status": "PARTIALLY_RESOLVED_OUTCOME_UNLOCK_BLOCKED",
                "affectedCode": "S3R1-R1 pre-request acquisition contract",
                "correction": "Declare exact frozen intervals and all required capture fields; leave provider-specific protocol unresolved.",
                "regression": "Acquisition contract matrix",
                "scientificDesignChanged": False,
                "marketOutcomeRead": False,
            },
        ],
        "acquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
        "acquisitionNextGate": "CENTRAL_REVIEW_PROVIDER_CONTRACT_CLOSURE_REQUIRED",
        "scientificDesignChanged": False,
        "marketOutcomeRead": False,
        "outcomeAccessFlags": _all_false_flags(),
        "executionAllowed": False,
        "preregistrationHash": preregistration["preregistrationHash"],
    }
    return {**body, "dispositionHash": _canonical_hash(body)}


def validate_market_data_acquisition_contract(value: Mapping[str, Any], resource_root: Path = PROJECT_ROOT) -> None:
    _require_exact(value, build_market_data_acquisition_contract(resource_root), "S3R1-R1 acquisition contract")


def write_s3r1_r1_artifacts(resource_root: Path = PROJECT_ROOT, *, outcome_source: object | None = None) -> dict[str, Path]:
    if outcome_source is not None:
        raise OutcomeAnalysisS3R1R1Error("S3R1-R1 materialization cannot accept a provider, market file, tick source, or outcome")
    root = Path(resource_root).resolve()
    acquisition = build_market_data_acquisition_contract(root)
    preregistration = build_s3r1_r1_preregistration(root)
    population = build_s3r1_r1_primary_population(root)
    clusters = build_s3r1_r1_overlap_clusters(root, population=population)
    invariance = build_s3r1_r1_invariance_audit(root, preregistration=preregistration, population=population, clusters=clusters)
    core = build_analysis_core_manifest(preregistration, population, clusters, invariance, acquisition)
    acceptance = build_s3r1_r1_acceptance_manifest(
        root,
        preregistration=preregistration,
        population=population,
        clusters=clusters,
        invariance=invariance,
        core=core,
        acquisition_contract=acquisition,
    )
    disposition = build_s3r1_r1_astra_disposition(root)
    artifacts = {
        "acquisition": root / DEFAULT_ACQUISITION_PATH.relative_to(PROJECT_ROOT),
        "preregistration": root / DEFAULT_PREREGISTRATION_PATH.relative_to(PROJECT_ROOT),
        "schema": root / DEFAULT_SCHEMA_PATH.relative_to(PROJECT_ROOT),
        "population": root / DEFAULT_PRIMARY_POPULATION_PATH.relative_to(PROJECT_ROOT),
        "clusters": root / DEFAULT_OVERLAP_CLUSTERS_PATH.relative_to(PROJECT_ROOT),
        "invariance": root / DEFAULT_INVARIANCE_PATH.relative_to(PROJECT_ROOT),
        "core": root / DEFAULT_CORE_MANIFEST_PATH.relative_to(PROJECT_ROOT),
        "acceptance": root / DEFAULT_ACCEPTANCE_PATH.relative_to(PROJECT_ROOT),
        "disposition": root / DEFAULT_DISPOSITION_PATH.relative_to(PROJECT_ROOT),
        "report": root / DEFAULT_REPORT_PATH.relative_to(PROJECT_ROOT),
    }
    _write_json(artifacts["acquisition"], acquisition)
    _write_json(artifacts["preregistration"], preregistration)
    _write_json(artifacts["schema"], build_s3r1_r1_schema(preregistration))
    _write_json(artifacts["population"], population)
    _write_json(artifacts["clusters"], clusters)
    _write_json(artifacts["invariance"], invariance)
    _write_json(artifacts["core"], core)
    _write_json(artifacts["acceptance"], acceptance)
    _write_json(artifacts["disposition"], disposition)
    artifacts["report"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["report"].write_text(render_s3r1_r1_report(acquisition, preregistration, population, core, acceptance, disposition), encoding="utf-8")
    return artifacts


def render_s3r1_r1_report(
    acquisition: Mapping[str, Any],
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    core: Mapping[str, Any],
    acceptance: Mapping[str, Any],
    disposition: Mapping[str, Any],
) -> str:
    counts = population["populationCounts"]
    return "\n".join(
        [
            "# MO-R4A-S3R1-R1 Astra Pre-Outcome Corrections",
            "",
            "This is an outcome-blind successor to S3R1. It corrects acceptance validation, synthetic numeric handling, and interval-scoped data-quality semantics without reading market outcomes or changing the frozen scientific design.",
            "",
            f"Astra disposition: `{disposition['verdict']}`; acquisition branch: `{disposition['branch']}`.",
            f"Historical S3R1 preregistration: `{HISTORICAL_S3R1_PREREGISTRATION_HASH}`",
            f"S3R1-R1 preregistration: `{preregistration['preregistrationHash']}`",
            f"Acquisition contract: `{acquisition['marketDataAcquisitionContractHash']}`",
            f"Analysis core: `{core['analysisCoreManifestHash']}`",
            f"Acceptance: `{acceptance['acceptanceManifestHash']}`",
            "",
            "## Frozen Population",
            "",
            f"The predecessor population remains {counts['frozenEventCount']} identities: 12 USD, 12 JPY, 14 directional, 13 primary market-scorable, one Saturday UTC exclusion, three NEUTRAL, and seven abstentions. The exact 40-state within-side permutation universe and -7/+7 timing diagnostic are unchanged.",
            "",
            "## Corrections",
            "",
            "Acceptance now independently rebuilds and compares every supplied component, including a supplied core. A component that is internally rehashed but differs from the immutable derivation is rejected.",
            "",
            "Synthetic diagnostics use a finite stable midpoint and `log(endMidpoint) - log(startMidpoint)`. Invalid numeric inputs are `DATA_NUMERIC_INVALID_UNSCORABLE`; exact finite zero alone remains `ZERO_MOVE`.",
            "",
            "Quote conflicts are judged within the half-open interval only. Outside-scope invalid prices and conflicts do not poison that interval, while every timestamp is still parsed and malformed timestamps raise a typed input error. No outside tick rescues an interval.",
            "",
            "## Acquisition Gate",
            "",
            f"The contract declares exactly {acquisition['frozenIntervalSet']['totalCount']} intervals ({acquisition['frozenIntervalSet']['actualCount']} actual, {acquisition['frozenIntervalSet']['minus7Count']} minus 7 days, {acquisition['frozenIntervalSet']['plus7Count']} plus 7 days) and requires future raw/parsed hashes and raw retention. Provider-specific transport, pagination, encoding, precision, parser identity, and revision protocol remain unresolved. Acceptance is therefore `{acceptance['status']}` and does not unlock outcome access.",
            "",
            "All outcome-access flags remain false. No provider call, price/outcome read, S4 evaluator, report, cache, UI, score, polarity, Auto Suggest, ML, MT5, or execution path is present.",
            "",
        ]
    )


def score_synthetic_interval_s3r1_r1(
    ticks: Iterable[Mapping[str, Any]],
    *,
    applying_start_utc: str,
    separating_end_utc: str,
    validation_expected_pair_direction: str,
) -> dict[str, Any]:
    """Expose the corrected synthetic evaluator under the R1 contract."""

    return s3r1.score_synthetic_interval_s3r1(
        ticks,
        applying_start_utc=applying_start_utc,
        separating_end_utc=separating_end_utc,
        validation_expected_pair_direction=validation_expected_pair_direction,
    )
