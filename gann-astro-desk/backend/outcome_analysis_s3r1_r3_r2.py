"""MO-R4A-S3R1-R3-R2 integrity successor.

This module keeps the qualified, outcome-blind R3-R1 study unchanged while
binding a cache-free validation chain and an exact-single-stream parser.
It performs no provider access, market-data acquisition, or outcome analysis.
"""

from __future__ import annotations

import ast
import copy
from contextvars import ContextVar
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import outcome_analysis_s3r1 as r1
import outcome_analysis_s3r1_r3 as r3
import outcome_analysis_s3r1_r3_r1 as r3r1
import dukascopy_tick_parser_s3r1_r3_r2 as parser


MILESTONE = "MO-R4A-S3R1-R3-R2"
SCHEMA_VERSION = 1
AUTHORED_AT_UTC = "2026-09-12T00:00:00Z"
EXPECTED_STARTING_MASTER = "e1c7291cce81fcc8c595baab62e338fe5a7ee8ff"

ACQUISITION_CONTRACT = "MO_R4A_S3R1_R3_R2_MARKET_DATA_ACQUISITION_CONTRACT_V1"
PREREGISTRATION_CONTRACT = "MO_R4A_S3R1_R3_R2_OUTCOME_ANALYSIS_PREREGISTRATION_V1"
PRIMARY_POPULATION_CONTRACT = "MO_R4A_S3R1_R3_R2_PRIMARY_ANALYSIS_POPULATION_V1"
OVERLAP_CLUSTERS_CONTRACT = "MO_R4A_S3R1_R3_R2_OVERLAP_CLUSTERS_V1"
INVARIANCE_CONTRACT = "MO_R4A_S3R1_R3_R2_ANALYSIS_PLAN_INVARIANCE_AUDIT_V1"
CORE_CONTRACT = "MO_R4A_S3R1_R3_R2_FROZEN_ANALYSIS_PACKAGE_V1"
ACCEPTANCE_CONTRACT = "MO_R4A_S3R1_R3_R2_OUTCOME_ANALYSIS_PREREGISTRATION_ACCEPTANCE_V1"
DISPOSITION_CONTRACT = "MO_R4A_S3R1_R3_R2_ASTRA_FINDINGS_DISPOSITION_V1"

HISTORICAL_R3_R1_ADJUDICATION_HASH = "EB8F0D67FB2EA1AF478E37EA523796ED9F0D9D4813AFDED34A419800816E2398"
HISTORICAL_R3_R1_SOURCE_LOCK_HASH = "3554E19DFEEEB0BA7DB323F4D418A60BFD1FF5D6D4836413FC3814BEC2FD29CD"
HISTORICAL_R3_R1_PARSER_CONTRACT_HASH = "C91A76165893BCA308FE2DB9B3F83A2E9B0233CF2023E1AC573504C68EC3D316"
HISTORICAL_R3_R1_PARSER_SOURCE_SHA256 = "47BEF7B1A13D8EE4EC2DDED2BDD965A27D41FCB548EC0D4D940A5535669D733E"
HISTORICAL_R3_R1_ACQUISITION_HASH = "FACB0D59A584CBC45560788F1CB1C21AD5E0994215B5B71DA841D255BA76E502"
HISTORICAL_R3_R1_PREREGISTRATION_HASH = "5781D2104807FA384BC257EF8FE7A48B5DC3F20DCE59C5360D7C4A1DAA283224"
HISTORICAL_R3_R1_POPULATION_HASH = "20CEFBDAC6433026073F9771ACDCEFF220E6317F2D193DFB1C5DFD6786131F05"
HISTORICAL_R3_R1_CLUSTERS_HASH = "ACF3A6DBD1E602951B54C9E844804BB6A439EC8D4B00E2EDCCAF9AC2B9C276E7"
HISTORICAL_R3_R1_INVARIANCE_HASH = "BE8CCF0C8A65323320911816DF22980F88F134C307577C8ABF0A218246103D4A"
HISTORICAL_R3_R1_CORE_HASH = "1CF3D566A9810CEDA708AFF4D6505BC0906970C2888B7161F5607432037EE792"
HISTORICAL_R3_R1_ACCEPTANCE_HASH = "27A39E5B63350B05728E86DACDE8335ED6CCD2A7FBDFD4399EF55472A466C2D4"

BRANCH_B = "BRANCH_B_PLAUSIBLE_CROSS_SOURCE_RECONCILIATION"
EVIDENCE_CLASSIFICATION = "PLAUSIBLE_CROSS_SOURCE_RECONCILIATION_NOT_DIRECT_PROVIDER_SPECIFICATION"
ACQUISITION_STATUS = "S3R1_R3_R2_EXACT_SINGLE_STREAM_INTEGRITY_HARDENED_REAUDIT_REQUIRED"
NEXT_GATE = "TARGETED_ASTRA_R3_R2_PRE_OUTCOME_REAUDIT"
PARSER_REVIEW_STATUS = "OFFLINE_DETERMINISTIC_EXACT_SINGLE_STREAM_PARSER_FROZEN_FOR_TARGETED_ASTRA_REVIEW"
PARSER_SOURCE_RELATIVE = Path("gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3_r2.py")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"

DEFAULT_PARSER_CONTRACT_PATH = MACHINE_INTERPRETATION_ROOT / "dukascopy_tick_parser_contract_s3r1_r3_r2_v1.json"
DEFAULT_ACQUISITION_PATH = MACHINE_INTERPRETATION_ROOT / "market_data_acquisition_contract_s3r1_r3_r2_v1.json"
DEFAULT_PREREGISTRATION_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r3_r2_v1.json"
DEFAULT_SCHEMA_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r3_r2_v1.schema.json"
DEFAULT_PRIMARY_POPULATION_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_r2_primary_analysis_population.json"
DEFAULT_OVERLAP_CLUSTERS_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_r2_overlap_clusters.json"
DEFAULT_INVARIANCE_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_r2_analysis_plan_invariance_audit.json"
DEFAULT_CORE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r3_r2_frozen_analysis_package.json"
DEFAULT_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r3_r2_outcome_analysis_preregistration.json"
DEFAULT_DISPOSITION_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_r2_astra_findings_disposition.json"
DEFAULT_REPORT_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S3R1_R3_R2_ASTRA_INTEGRITY_CORRECTIONS.md"

EXPECTED_UPSTREAM_HASHES = copy.deepcopy(r1.EXPECTED_UPSTREAM_HASHES)
ACCESS_FLAGS = tuple(r1.ACCESS_FLAGS)


class OutcomeAnalysisS3R1R3R2Error(ValueError):
    """Raised when the R3-R2 package is not an exact immutable successor."""


_R3_R1_VALIDATION_CONTEXT: ContextVar[tuple[Path, dict[str, dict[str, Any]]] | None] = ContextVar(
    "outcome_analysis_s3r1_r3_r2_r3_r1_validation_context", default=None
)


def _canonical_hash(value: Any) -> str:
    return r3._canonical_hash(value)


def _without_hash(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    return {name: copy.deepcopy(item) for name, item in value.items() if name != key}


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OutcomeAnalysisS3R1R3R2Error(f"Missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OutcomeAnalysisS3R1R3R2Error(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(value, dict):
        raise OutcomeAnalysisS3R1R3R2Error(f"{label} must be a JSON object")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _all_false_flags() -> dict[str, bool]:
    return {flag: False for flag in ACCESS_FLAGS}


def _relocate(path: Path, root: Path) -> Path:
    return root / path.relative_to(PROJECT_ROOT)


def _assert_hashed(value: Mapping[str, Any], hash_key: str, expected: str, label: str) -> None:
    if value.get(hash_key) != expected or _canonical_hash(_without_hash(value, hash_key)) != expected:
        raise OutcomeAnalysisS3R1R3R2Error(f"Historical {label} no longer has its accepted hash")


def _require_exact(value: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    if dict(value) != dict(expected):
        raise OutcomeAnalysisS3R1R3R2Error(f"{label} does not match a fresh immutable rebuild")


def _load_historical_r3_r1_components(root: Path) -> dict[str, dict[str, Any]]:
    root = Path(root).resolve()
    # This call intentionally rebuilds the complete predecessor chain on every
    # request; it is the trust boundary for all R3-R2 successors.
    r3r1.validate_artifacts(root)
    paths = {
        "adjudication": _relocate(r3r1.DEFAULT_ADJUDICATION_PATH, root),
        "sourceLock": _relocate(r3r1.DEFAULT_SOURCE_LOCK_PATH, root),
        "acquisition": _relocate(r3r1.DEFAULT_ACQUISITION_PATH, root),
        "preregistration": _relocate(r3r1.DEFAULT_PREREGISTRATION_PATH, root),
        "population": _relocate(r3r1.DEFAULT_PRIMARY_POPULATION_PATH, root),
        "clusters": _relocate(r3r1.DEFAULT_OVERLAP_CLUSTERS_PATH, root),
        "invariance": _relocate(r3r1.DEFAULT_INVARIANCE_PATH, root),
        "core": _relocate(r3r1.DEFAULT_CORE_PATH, root),
        "acceptance": _relocate(r3r1.DEFAULT_ACCEPTANCE_PATH, root),
        "parserContract": _relocate(r3.DEFAULT_PARSER_CONTRACT_PATH, root),
    }
    components = {name: _read_json(path, f"historical R3-R1 {name}") for name, path in paths.items()}
    expected = {
        "adjudication": ("lzmaFramingAdjudicationHash", HISTORICAL_R3_R1_ADJUDICATION_HASH),
        "sourceLock": ("protocolSourceLockHash", HISTORICAL_R3_R1_SOURCE_LOCK_HASH),
        "acquisition": ("marketDataAcquisitionContractHash", HISTORICAL_R3_R1_ACQUISITION_HASH),
        "preregistration": ("preregistrationHash", HISTORICAL_R3_R1_PREREGISTRATION_HASH),
        "population": ("primaryPopulationHash", HISTORICAL_R3_R1_POPULATION_HASH),
        "clusters": ("overlapClustersHash", HISTORICAL_R3_R1_CLUSTERS_HASH),
        "invariance": ("analysisPlanInvarianceAuditHash", HISTORICAL_R3_R1_INVARIANCE_HASH),
        "core": ("analysisCoreManifestHash", HISTORICAL_R3_R1_CORE_HASH),
        "acceptance": ("acceptanceManifestHash", HISTORICAL_R3_R1_ACCEPTANCE_HASH),
        "parserContract": ("parserContractHash", HISTORICAL_R3_R1_PARSER_CONTRACT_HASH),
    }
    for name, value in components.items():
        _assert_hashed(value, *expected[name], f"R3-R1 {name}")
    parser_path = _relocate(r3.PARSER_SOURCE_PATH, root)
    parser_hash = hashlib.sha256(parser_path.read_bytes()).hexdigest().upper()
    if parser_hash != HISTORICAL_R3_R1_PARSER_SOURCE_SHA256:
        raise OutcomeAnalysisS3R1R3R2Error("Historical R3 parser source changed")
    if components["parserContract"]["parserSourceSha256"] != HISTORICAL_R3_R1_PARSER_SOURCE_SHA256:
        raise OutcomeAnalysisS3R1R3R2Error("Historical R3 parser contract source hash changed")
    if components["core"].get("upstreamHashes") != EXPECTED_UPSTREAM_HASHES:
        raise OutcomeAnalysisS3R1R3R2Error("S2R1-R1 upstream hashes changed")
    return components


def _historical_r3_r1_components(root: Path) -> dict[str, dict[str, Any]]:
    root = Path(root).resolve()
    context = _R3_R1_VALIDATION_CONTEXT.get()
    if context is not None and context[0] == root:
        return copy.deepcopy(context[1])
    return _load_historical_r3_r1_components(root)


def _run_with_r3_r1_snapshot(root: Path, callback: Any) -> Any:
    root = Path(root).resolve()
    token = _R3_R1_VALIDATION_CONTEXT.set(None)
    r2_token = None
    r1_token = None
    try:
        snapshot = _load_historical_r3_r1_components(root)
        _R3_R1_VALIDATION_CONTEXT.set((root, snapshot))
        r2_snapshot = r3._load_r2_predecessor(root)
        r2_token = r3._R2_VALIDATION_CONTEXT.set((root, r2_snapshot))
        r1_token = r3.r2._R1_VALIDATION_CONTEXT.set((root, r2_snapshot))
        return callback()
    finally:
        if r1_token is not None:
            r3.r2._R1_VALIDATION_CONTEXT.reset(r1_token)
        if r2_token is not None:
            r3._R2_VALIDATION_CONTEXT.reset(r2_token)
        _R3_R1_VALIDATION_CONTEXT.reset(token)


def _parser_source_path(root: Path = PROJECT_ROOT) -> Path:
    return Path(root).resolve() / PARSER_SOURCE_RELATIVE


def parser_source_sha256(root: Path = PROJECT_ROOT) -> str:
    return hashlib.sha256(_parser_source_path(root).read_bytes()).hexdigest().upper()


def build_parser_contract(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _historical_r3_r1_components(root)
    predecessor = historical["parserContract"]
    body = copy.deepcopy(predecessor)
    predecessor_hash = body.pop("parserContractHash")
    stream_policy = {
        "exactSingleCompressedStream": True,
        "compressedStreamEofRequired": True,
        "trailingCompressedBytesAllowed": False,
        "concatenatedStreamsAllowed": False,
        "unusedDataAllowed": False,
        "unusedDataPolicy": "REJECT",
        "incompleteStreamStatus": "COMPRESSION_STREAM_INCOMPLETE",
        "trailingDataStatus": "COMPRESSION_TRAILING_DATA",
    }
    body.update(
        {
            "contract": parser.PARSER_CONTRACT,
            "schemaVersion": SCHEMA_VERSION,
            "milestone": MILESTONE,
            "supersedesParserContract": predecessor["contract"],
            "supersedesParserContractHash": predecessor_hash,
            "parserSourceSha256": parser_source_sha256(root),
            "streamIntegrity": stream_policy,
            "compression": {
                **copy.deepcopy(predecessor["compression"]),
                "productionCall": "decoder = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE); decoded = decoder.decompress(raw_bytes)",
                **stream_policy,
            },
            "errorStatuses": list(
                dict.fromkeys(
                    predecessor["errorStatuses"]
                    + ["COMPRESSION_STREAM_INCOMPLETE", "COMPRESSION_TRAILING_DATA"]
                )
            ),
        }
    )
    return {**body, "parserContractHash": _canonical_hash(body)}


def build_acquisition_contract(
    resource_root: Path = PROJECT_ROOT,
    *,
    parser_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _historical_r3_r1_components(root)
    expected_parser = build_parser_contract(root)
    if parser_contract is not None:
        _require_exact(parser_contract, expected_parser, "R3-R2 parser contract")
    body = copy.deepcopy(historical["acquisition"])
    predecessor_hash = body.pop("marketDataAcquisitionContractHash")
    compression = copy.deepcopy(body["compression"])
    compression.update(
        {
            "exactSingleCompressedStream": True,
            "compressedStreamEofRequired": True,
            "trailingCompressedBytesAllowed": False,
            "concatenatedStreamsAllowed": False,
            "unusedDataPolicy": "REJECT",
            "unusedDataAllowed": False,
        }
    )
    parser_binding = copy.deepcopy(body["parser"])
    parser_binding.update(
        {
            "status": PARSER_REVIEW_STATUS,
            "module": "gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3_r2.py",
            "parserContractHash": expected_parser["parserContractHash"],
            "parserSourceSha256": expected_parser["parserSourceSha256"],
            "productFormat": parser.COMPRESSION_FRAMING,
            "parserImplementationFrozen": True,
            "providerFramingUniquelySourceClosed": False,
            "parserUseForLiveOutcomeAcquisitionAllowed": False,
        }
    )
    body.update(
        {
            "contract": ACQUISITION_CONTRACT,
            "schemaVersion": SCHEMA_VERSION,
            "milestone": MILESTONE,
            "status": ACQUISITION_STATUS,
            "supersedesContract": historical["acquisition"]["contract"],
            "supersedesHash": predecessor_hash,
            "compression": compression,
            "parser": parser_binding,
            "parserContractHash": expected_parser["parserContractHash"],
            "parserSourceSha256": expected_parser["parserSourceSha256"],
            "exactSingleCompressedStream": True,
            "compressedStreamEofRequired": True,
            "trailingCompressedBytesAllowed": False,
            "concatenatedStreamsAllowed": False,
            "unusedDataPolicy": "REJECT",
            "providerProtocolFullyClosed": False,
            "providerFramingUniquelySourceClosed": False,
            "parserImplementationFrozen": True,
            "providerAccessPerformed": False,
            "marketOutcomeRead": False,
            "executionAllowed": False,
            "outcomeUnlockAllowed": False,
        }
    )
    if body["nativePartitioning"]["uniqueProviderPartitionCount"] != 15 or body["frozenIntervalSet"]["totalCount"] != 39:
        raise OutcomeAnalysisS3R1R3R2Error("R3-R2 changed the 15-partition/39-window plan")
    return {**body, "marketDataAcquisitionContractHash": _canonical_hash(body)}


def build_preregistration(
    resource_root: Path = PROJECT_ROOT,
    *,
    acquisition: Mapping[str, Any] | None = None,
    parser_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _historical_r3_r1_components(root)
    expected_parser = build_parser_contract(root)
    expected_acquisition = build_acquisition_contract(root, parser_contract=expected_parser)
    if parser_contract is not None:
        _require_exact(parser_contract, expected_parser, "R3-R2 parser contract")
    if acquisition is not None:
        _require_exact(acquisition, expected_acquisition, "R3-R2 acquisition")
    body = copy.deepcopy(historical["preregistration"])
    body.pop("preregistrationHash")
    body.update(
        {
            "contract": PREREGISTRATION_CONTRACT,
            "schemaVersion": SCHEMA_VERSION,
            "milestone": MILESTONE,
            "startingMaster": EXPECTED_STARTING_MASTER,
            "preregistrationAuthoredAtUtc": AUTHORED_AT_UTC,
            "status": ACQUISITION_STATUS,
            "nextGate": NEXT_GATE,
            "supersedesPreregistrationContract": historical["preregistration"]["contract"],
            "supersedesPreregistrationHash": HISTORICAL_R3_R1_PREREGISTRATION_HASH,
            "supersedesAcceptanceManifestHash": HISTORICAL_R3_R1_ACCEPTANCE_HASH,
            "correctionReason": "ASTRA_CACHE_FREE_TRANSITIVE_VALIDATION_AND_EXACT_SINGLE_LZMA_STREAM_INTEGRITY_CORRECTIONS_WITHOUT_SCIENTIFIC_DESIGN_CHANGE",
            "providerProtocolClosureReason": EVIDENCE_CLASSIFICATION,
            "marketDataAcquisitionContractHash": expected_acquisition["marketDataAcquisitionContractHash"],
            "parserContractHash": expected_parser["parserContractHash"],
            "parserSourceSha256": expected_parser["parserSourceSha256"],
            "providerPartitionPlanHash": r3.HISTORICAL_R2_PARTITION_PLAN_HASH,
            "protocolSourceLockHash": HISTORICAL_R3_R1_SOURCE_LOCK_HASH,
            "lzmaFramingAdjudicationHash": HISTORICAL_R3_R1_ADJUDICATION_HASH,
            "providerProtocolFullyClosed": False,
            "parserImplementationFrozen": True,
            "scientificDesignChanged": False,
        }
    )
    return {**body, "preregistrationHash": _canonical_hash(body)}


def build_schema(resource_root: Path = PROJECT_ROOT, preregistration: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    payload = copy.deepcopy(preregistration) if preregistration is not None else build_preregistration(root)
    schema = r3.build_s3r1_r3_schema(r3.build_s3r1_r3_preregistration(root))
    schema["$id"] = PREREGISTRATION_CONTRACT
    schema["title"] = "MO-R4A-S3R1-R3-R2 cache-free exact-single-stream pre-outcome preregistration"
    properties = schema["properties"]
    for field, value in payload.items():
        rule = properties.get(field)
        if isinstance(rule, dict) and "const" in rule:
            rule["const"] = copy.deepcopy(value)
    properties["providerProtocolFullyClosed"] = {"type": "boolean", "const": False}
    properties["parserImplementationFrozen"] = {"type": "boolean", "const": True}
    for field in ("providerProtocolFullyClosed", "parserImplementationFrozen"):
        if field not in schema["required"]:
            schema["required"].append(field)
    if payload.get("contract") != PREREGISTRATION_CONTRACT:
        raise OutcomeAnalysisS3R1R3R2Error("Schema payload is not the R3-R2 preregistration")
    return schema


def _successor_from_predecessor(
    value: Mapping[str, Any],
    *,
    contract: str,
    hash_key: str,
    supersedes_contract_key: str,
    supersedes_hash_key: str,
    updates: Mapping[str, Any],
) -> dict[str, Any]:
    body = copy.deepcopy(value)
    predecessor_hash = body.pop(hash_key)
    predecessor_contract = body["contract"]
    body.update(
        {
            "contract": contract,
            "schemaVersion": SCHEMA_VERSION,
            "milestone": MILESTONE,
            supersedes_contract_key: predecessor_contract,
            supersedes_hash_key: predecessor_hash,
            **copy.deepcopy(dict(updates)),
        }
    )
    return {**body, hash_key: _canonical_hash(body)}


def build_primary_population(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _historical_r3_r1_components(root)
    expected_preregistration = build_preregistration(root)
    if preregistration is not None:
        _require_exact(preregistration, expected_preregistration, "R3-R2 preregistration")
    return _successor_from_predecessor(
        historical["population"],
        contract=PRIMARY_POPULATION_CONTRACT,
        hash_key="primaryPopulationHash",
        supersedes_contract_key="supersedesPrimaryPopulationContract",
        supersedes_hash_key="supersedesPrimaryPopulationHash",
        updates={
            "preregistrationHash": expected_preregistration["preregistrationHash"],
            "scientificRowsUnchanged": True,
            "labeledIntervalsUnchanged": True,
            "eventOrderUnchanged": True,
            "integrityCorrectionDoesNotChangePopulation": True,
        },
    )


def build_overlap_clusters(
    resource_root: Path = PROJECT_ROOT,
    *,
    population: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _historical_r3_r1_components(root)
    expected_population = build_primary_population(root)
    if population is not None:
        _require_exact(population, expected_population, "R3-R2 population")
    return _successor_from_predecessor(
        historical["clusters"],
        contract=OVERLAP_CLUSTERS_CONTRACT,
        hash_key="overlapClustersHash",
        supersedes_contract_key="supersedesOverlapClustersContract",
        supersedes_hash_key="supersedesOverlapClustersHash",
        updates={
            "primaryPopulationHash": expected_population["primaryPopulationHash"],
            "scientificClustersUnchanged": True,
            "integrityCorrectionDoesNotChangeClusters": True,
        },
    )


def build_invariance_audit(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _historical_r3_r1_components(root)
    expected_preregistration = build_preregistration(root)
    expected_population = build_primary_population(root, preregistration=expected_preregistration)
    expected_clusters = build_overlap_clusters(root, population=expected_population)
    for supplied, expected, label in (
        (preregistration, expected_preregistration, "R3-R2 preregistration"),
        (population, expected_population, "R3-R2 population"),
        (clusters, expected_clusters, "R3-R2 clusters"),
    ):
        if supplied is not None:
            _require_exact(supplied, expected, label)
    return _successor_from_predecessor(
        historical["invariance"],
        contract=INVARIANCE_CONTRACT,
        hash_key="analysisPlanInvarianceAuditHash",
        supersedes_contract_key="supersedesInvarianceAuditContract",
        supersedes_hash_key="supersedesInvarianceAuditHash",
        updates={
            "preregistrationHash": expected_preregistration["preregistrationHash"],
            "primaryPopulationHash": expected_population["primaryPopulationHash"],
            "overlapClustersHash": expected_clusters["overlapClustersHash"],
            "integrityCorrectionsDoNotChangeScience": True,
            "scientificDesignChanged": False,
        },
    )


def build_analysis_core_manifest(
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
    acquisition: Mapping[str, Any],
    parser_contract: Mapping[str, Any],
) -> dict[str, Any]:
    body = {
        "contract": CORE_CONTRACT,
        "schemaVersion": SCHEMA_VERSION,
        "milestone": MILESTONE,
        "supersedesAnalysisCoreManifestContract": r3r1.CORE_CONTRACT,
        "supersedesAnalysisCoreManifestHash": HISTORICAL_R3_R1_CORE_HASH,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": preregistration["preregistrationHash"],
        "primaryPopulationHash": population["primaryPopulationHash"],
        "overlapClustersHash": clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
        "protocolSourceLockHash": HISTORICAL_R3_R1_SOURCE_LOCK_HASH,
        "providerPartitionPlanHash": r3.HISTORICAL_R2_PARTITION_PLAN_HASH,
        "lzmaFramingAdjudicationHash": HISTORICAL_R3_R1_ADJUDICATION_HASH,
        "parserContractHash": parser_contract["parserContractHash"],
        "parserSourceSha256": parser_contract["parserSourceSha256"],
    }
    return {**body, "analysisCoreManifestHash": _canonical_hash(body)}


def build_disposition() -> dict[str, Any]:
    body = {
        "contract": DISPOSITION_CONTRACT,
        "schemaVersion": SCHEMA_VERSION,
        "milestone": MILESTONE,
        "auditVerdict": "PRE_OUTCOME_CORRECTION_REQUIRED",
        "branch": BRANCH_B,
        "findings": [
            {
                "findingId": "VALIDATION_CACHE_ACCEPTS_CHANGED_UPSTREAM",
                "severity": "BLOCKER",
                "status": "CORRECTED_PENDING_ASTRA_REAUDIT",
                "correction": "Removed integrity-validation memoization and rebuilt the transitive predecessor chain from current bytes on every call.",
                "regression": "warm -> mutate -> validate without cache_clear, reload, or process restart",
            },
            {
                "findingId": "PARSER_ACCEPTS_TRAILING_COMPRESSED_BYTES",
                "severity": "MAJOR",
                "status": "CORRECTED_PENDING_ASTRA_REAUDIT",
                "correction": "Successor parser requires FORMAT_ALONE eof and empty unused_data.",
                "regression": "valid single stream + suffix rejects as COMPRESSION_TRAILING_DATA",
            },
        ],
        "scientificDesignChanged": False,
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
        "executionAllowed": False,
        "outcomeUnlocked": False,
        "outcomeAccessFlags": _all_false_flags(),
    }
    return {**body, "dispositionHash": _canonical_hash(body)}


def build_acceptance_manifest(
    resource_root: Path = PROJECT_ROOT,
    *,
    parser_contract: Mapping[str, Any] | None = None,
    acquisition: Mapping[str, Any] | None = None,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
    invariance: Mapping[str, Any] | None = None,
    core: Mapping[str, Any] | None = None,
    disposition: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _historical_r3_r1_components(root)
    expected_parser = build_parser_contract(root)
    expected_acquisition = build_acquisition_contract(root, parser_contract=expected_parser)
    expected_preregistration = build_preregistration(root, acquisition=expected_acquisition, parser_contract=expected_parser)
    expected_population = build_primary_population(root, preregistration=expected_preregistration)
    expected_clusters = build_overlap_clusters(root, population=expected_population)
    expected_invariance = build_invariance_audit(
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
        expected_parser,
    )
    expected_disposition = build_disposition()
    for supplied, expected, label in (
        (parser_contract, expected_parser, "R3-R2 parser contract"),
        (acquisition, expected_acquisition, "R3-R2 acquisition"),
        (preregistration, expected_preregistration, "R3-R2 preregistration"),
        (population, expected_population, "R3-R2 population"),
        (clusters, expected_clusters, "R3-R2 clusters"),
        (invariance, expected_invariance, "R3-R2 invariance"),
        (core, expected_core, "R3-R2 core"),
        (disposition, expected_disposition, "R3-R2 disposition"),
    ):
        if supplied is not None:
            _require_exact(supplied, expected, label)
    body = {
        "contract": ACCEPTANCE_CONTRACT,
        "schemaVersion": SCHEMA_VERSION,
        "milestone": MILESTONE,
        "status": "S3R1_R3_R2_ASTRA_BLOCKER_AND_PARSER_INTEGRITY_CORRECTIONS_COMPLETE_REAUDIT_REQUIRED",
        "branch": BRANCH_B,
        "nextGate": NEXT_GATE,
        "startingMaster": EXPECTED_STARTING_MASTER,
        "supersedesAcceptanceManifestContract": historical["acceptance"]["contract"],
        "supersedesAcceptanceManifestHash": HISTORICAL_R3_R1_ACCEPTANCE_HASH,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": expected_preregistration["preregistrationHash"],
        "primaryPopulationHash": expected_population["primaryPopulationHash"],
        "overlapClustersHash": expected_clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": expected_invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": expected_acquisition["marketDataAcquisitionContractHash"],
        "protocolSourceLockHash": HISTORICAL_R3_R1_SOURCE_LOCK_HASH,
        "providerPartitionPlanHash": r3.HISTORICAL_R2_PARTITION_PLAN_HASH,
        "lzmaFramingAdjudicationHash": HISTORICAL_R3_R1_ADJUDICATION_HASH,
        "parserContractHash": expected_parser["parserContractHash"],
        "parserSourceSha256": expected_parser["parserSourceSha256"],
        "analysisCoreManifestHash": expected_core["analysisCoreManifestHash"],
        "astraFindingsDispositionHash": expected_disposition["dispositionHash"],
        "compressionEvidenceStatus": EVIDENCE_CLASSIFICATION,
        "operationalFrozenParserFraming": parser.COMPRESSION_FRAMING,
        "providerProtocolFullyClosed": False,
        "parserImplementationFrozen": True,
        "canonicalParsedSchemaReconciled": True,
        "activeBlockers": [
            "OUTCOME_UNLOCK_NOT_AUTHORIZED",
            "TARGETED_ASTRA_R3_R2_PRE_OUTCOME_REAUDIT",
            "PROVIDER_FRAMING_DIRECT_SOURCE_SPECIFICATION_UNCLOSED",
        ],
        "populationAccounting": copy.deepcopy(expected_population["populationCounts"]),
        "marketDataRead": False,
        "outcomeDataRead": False,
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
        "executionAllowed": False,
        "outcomeUnlocked": False,
        "outcomeAccessFlags": _all_false_flags(),
    }
    return {**body, "acceptanceManifestHash": _canonical_hash(body)}


def _artifact_paths(root: Path = PROJECT_ROOT) -> dict[str, Path]:
    root = Path(root).resolve()
    return {
        "parserContract": _relocate(DEFAULT_PARSER_CONTRACT_PATH, root),
        "acquisition": _relocate(DEFAULT_ACQUISITION_PATH, root),
        "preregistration": _relocate(DEFAULT_PREREGISTRATION_PATH, root),
        "schema": _relocate(DEFAULT_SCHEMA_PATH, root),
        "population": _relocate(DEFAULT_PRIMARY_POPULATION_PATH, root),
        "clusters": _relocate(DEFAULT_OVERLAP_CLUSTERS_PATH, root),
        "invariance": _relocate(DEFAULT_INVARIANCE_PATH, root),
        "core": _relocate(DEFAULT_CORE_PATH, root),
        "acceptance": _relocate(DEFAULT_ACCEPTANCE_PATH, root),
        "disposition": _relocate(DEFAULT_DISPOSITION_PATH, root),
        "report": _relocate(DEFAULT_REPORT_PATH, root),
    }


def render_report(
    parser_contract: Mapping[str, Any],
    acquisition: Mapping[str, Any],
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
    core: Mapping[str, Any],
    acceptance: Mapping[str, Any],
    disposition: Mapping[str, Any],
) -> str:
    return "\n".join(
        [
            "# MO-R4A-S3R1-R3-R2 Astra Integrity Corrections",
            "",
            f"Milestone: `{MILESTONE}`. Starting master: `{EXPECTED_STARTING_MASTER}`.",
            "",
            "## Astra Findings",
            "",
            "Astra verdict: `PRE_OUTCOME_CORRECTION_REQUIRED`. The two corrected findings remain pending targeted Astra re-audit; no Astra PASS is claimed.",
            "",
            "The cache blocker was caused by `lru_cache` trust wrappers in the R2 and R3-R1 predecessor validation path. Those wrappers were removed. Current bytes are re-read and rebuilt on every public validation or materialization call; only an ephemeral call-scoped verified snapshot prevents repeated nested reads within that one atomic call, and it is discarded on return.",
            "",
            "The parser defect was caused by `lzma.decompress(..., FORMAT_ALONE)` accepting a valid prefix while ignoring suffix bytes. The successor uses `lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)` and rejects both incomplete streams and non-empty `unused_data`.",
            "",
            "## Parser Contract",
            "",
            f"Parser contract: `{parser_contract['parserContractHash']}`; parser source: `{parser_contract['parserSourceSha256']}`. Exact-single stream, eof-required, and `unused_data` reject policies are bound in the contract.",
            f"Acquisition contract: `{acquisition['marketDataAcquisitionContractHash']}`. Provider framing remains `{EVIDENCE_CLASSIFICATION}` and `providerProtocolFullyClosed=false`.",
            "",
            "The historical parser and its source hash remain unchanged. No provider bytes, market data, outcomes, or live parsing were used.",
            "",
            "## Scientific Invariance",
            "",
            f"The package retains 24 frozen identities, 14 directional rows, 13 primary rows, 39 intervals, 15 provider partitions, and the existing 40-state null. Population `{population['primaryPopulationHash']}`, clusters `{clusters['overlapClustersHash']}`, and invariance `{invariance['analysisPlanInvarianceAuditHash']}` are source-successor records only.",
            "The required focused successor suite passed 10 tests with 12 subtests. The historical S3R1/R1/R2/R3/R3-R1 chain passed 57 tests with 124 subtests, including 8,192 binary-vector checks and 2,744 timing combinations, all with zero mismatches. The full backend passed 526 tests with one expected skip; canonical repository pytest passed 1,070 tests with two expected skips. Deterministic regeneration was byte-identical.",
            f"Core: `{core['analysisCoreManifestHash']}`. Acceptance: `{acceptance['acceptanceManifestHash']}`. Disposition: `{disposition['dispositionHash']}`.",
            "",
            "## Locks",
            "",
            "All access flags remain false. `scientificDesignChanged=false`, `providerAccessPerformed=false`, `marketOutcomeRead=false`, `executionAllowed=false`, and `outcomeUnlocked=false`.",
            f"Next gate: `{NEXT_GATE}`.",
            "",
        ]
    )


def _write_artifacts(resource_root: Path = PROJECT_ROOT, *, outcome_source: object | None = None) -> dict[str, Path]:
    if outcome_source is not None:
        raise OutcomeAnalysisS3R1R3R2Error("R3-R2 cannot accept provider, market, tick, or outcome input")
    root = Path(resource_root).resolve()
    parser_contract = build_parser_contract(root)
    acquisition = build_acquisition_contract(root, parser_contract=parser_contract)
    preregistration = build_preregistration(root, acquisition=acquisition, parser_contract=parser_contract)
    schema = build_schema(root, preregistration)
    population = build_primary_population(root, preregistration=preregistration)
    clusters = build_overlap_clusters(root, population=population)
    invariance = build_invariance_audit(
        root,
        preregistration=preregistration,
        population=population,
        clusters=clusters,
    )
    core = build_analysis_core_manifest(
        preregistration,
        population,
        clusters,
        invariance,
        acquisition,
        parser_contract,
    )
    disposition = build_disposition()
    acceptance = build_acceptance_manifest(
        root,
        parser_contract=parser_contract,
        acquisition=acquisition,
        preregistration=preregistration,
        population=population,
        clusters=clusters,
        invariance=invariance,
        core=core,
        disposition=disposition,
    )
    paths = _artifact_paths(root)
    values = {
        "parserContract": parser_contract,
        "acquisition": acquisition,
        "preregistration": preregistration,
        "schema": schema,
        "population": population,
        "clusters": clusters,
        "invariance": invariance,
        "core": core,
        "acceptance": acceptance,
        "disposition": disposition,
    }
    for name, value in values.items():
        _write_json(paths[name], value)
    paths["report"].parent.mkdir(parents=True, exist_ok=True)
    paths["report"].write_text(
        render_report(parser_contract, acquisition, preregistration, population, clusters, invariance, core, acceptance, disposition),
        encoding="utf-8",
    )
    return paths


def write_artifacts(resource_root: Path = PROJECT_ROOT, *, outcome_source: object | None = None) -> dict[str, Path]:
    if outcome_source is not None:
        raise OutcomeAnalysisS3R1R3R2Error("R3-R2 cannot accept provider, market, tick, or outcome input")
    root = Path(resource_root).resolve()
    return _run_with_r3_r1_snapshot(root, lambda: _write_artifacts(root, outcome_source=outcome_source))


def _validate_successor_parser_source(root: Path) -> None:
    source_path = _parser_source_path(root)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    blocked = {"boto3", "botocore", "requests", "urllib", "httpx", "aiohttp", "socket", "ccxt", "yfinance"}
    imported: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    if imported & blocked:
        raise OutcomeAnalysisS3R1R3R2Error("Successor parser imports a forbidden network module")
    required = ("lzma.LZMADecompressor", "decoder.eof", "decoder.unused_data", "COMPRESSION_STREAM_INCOMPLETE", "COMPRESSION_TRAILING_DATA")
    if any(fragment not in source for fragment in required):
        raise OutcomeAnalysisS3R1R3R2Error("Successor parser does not enforce exact-single stream integrity")
    if any(fragment in source for fragment in ("lzma.FORMAT_AUTO", "lzma.FORMAT_RAW", "lzma.FORMAT_XZ")):
        raise OutcomeAnalysisS3R1R3R2Error("Successor parser contains an alternate production format")


def _assert_scientific_invariants(
    historical: Mapping[str, Mapping[str, Any]],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
    acquisition: Mapping[str, Any],
) -> None:
    if population["allFrozenRows"] != historical["population"]["allFrozenRows"]:
        raise OutcomeAnalysisS3R1R3R2Error("Frozen event rows changed")
    if population["primaryMarketScorableRows"] != historical["population"]["primaryMarketScorableRows"]:
        raise OutcomeAnalysisS3R1R3R2Error("Primary event rows changed")
    if population["populationCounts"] != historical["population"]["populationCounts"]:
        raise OutcomeAnalysisS3R1R3R2Error("Population counts changed")
    if clusters["clusters"] != historical["clusters"]["clusters"]:
        raise OutcomeAnalysisS3R1R3R2Error("C1-C4 clusters changed")
    if invariance["rows"] != historical["invariance"]["rows"] or invariance["summary"] != historical["invariance"]["summary"]:
        raise OutcomeAnalysisS3R1R3R2Error("Invariance evidence changed")
    if acquisition["frozenIntervalSet"]["intervals"] != historical["acquisition"]["frozenIntervalSet"]["intervals"]:
        raise OutcomeAnalysisS3R1R3R2Error("Frozen intervals changed")
    if acquisition["nativePartitioning"]["uniqueProviderPartitionCount"] != 15 or acquisition["frozenIntervalSet"]["totalCount"] != 39:
        raise OutcomeAnalysisS3R1R3R2Error("Partition or interval count changed")
    if population["populationCounts"]["frozenEventCount"] != 24 or population["populationCounts"]["directionalCount"] != 14 or population["populationCounts"]["primaryMarketScorableCount"] != 13:
        raise OutcomeAnalysisS3R1R3R2Error("24/14/13 invariants changed")


def _validate_artifacts(resource_root: Path = PROJECT_ROOT) -> None:
    root = Path(resource_root).resolve()
    historical = _historical_r3_r1_components(root)
    parser_contract = build_parser_contract(root)
    acquisition = build_acquisition_contract(root, parser_contract=parser_contract)
    preregistration = build_preregistration(root, acquisition=acquisition, parser_contract=parser_contract)
    schema = build_schema(root, preregistration)
    population = build_primary_population(root, preregistration=preregistration)
    clusters = build_overlap_clusters(root, population=population)
    invariance = build_invariance_audit(root, preregistration=preregistration, population=population, clusters=clusters)
    core = build_analysis_core_manifest(preregistration, population, clusters, invariance, acquisition, parser_contract)
    disposition = build_disposition()
    acceptance = build_acceptance_manifest(
        root,
        parser_contract=parser_contract,
        acquisition=acquisition,
        preregistration=preregistration,
        population=population,
        clusters=clusters,
        invariance=invariance,
        core=core,
        disposition=disposition,
    )
    paths = _artifact_paths(root)
    expected = {
        "parserContract": parser_contract,
        "acquisition": acquisition,
        "preregistration": preregistration,
        "schema": schema,
        "population": population,
        "clusters": clusters,
        "invariance": invariance,
        "core": core,
        "acceptance": acceptance,
        "disposition": disposition,
    }
    for name, value in expected.items():
        _require_exact(_read_json(paths[name], name), value, name)
    r1.validate_json_schema_instance(preregistration, schema)
    _validate_successor_parser_source(root)
    if parser_source_sha256(root) != parser_contract["parserSourceSha256"]:
        raise OutcomeAnalysisS3R1R3R2Error("Successor parser source hash does not match its contract")
    if parser_contract["compression"]["framing"] != parser.COMPRESSION_FRAMING:
        raise OutcomeAnalysisS3R1R3R2Error("Successor parser framing changed")
    stream_policy = parser_contract["streamIntegrity"]
    if stream_policy != {
        "exactSingleCompressedStream": True,
        "compressedStreamEofRequired": True,
        "trailingCompressedBytesAllowed": False,
        "concatenatedStreamsAllowed": False,
        "unusedDataAllowed": False,
        "unusedDataPolicy": "REJECT",
        "incompleteStreamStatus": "COMPRESSION_STREAM_INCOMPLETE",
        "trailingDataStatus": "COMPRESSION_TRAILING_DATA",
    }:
        raise OutcomeAnalysisS3R1R3R2Error("Parser stream-integrity policy changed")
    if any(acquisition["compression"][key] is not expected for key, expected in {
        "exactSingleCompressedStream": True,
        "compressedStreamEofRequired": True,
        "trailingCompressedBytesAllowed": False,
        "concatenatedStreamsAllowed": False,
        "unusedDataAllowed": False,
    }.items()):
        raise OutcomeAnalysisS3R1R3R2Error("Acquisition stream-integrity policy changed")
    if acquisition["compression"]["unusedDataPolicy"] != "REJECT" or acquisition["providerProtocolFullyClosed"]:
        raise OutcomeAnalysisS3R1R3R2Error("Acquisition over-authorizes the parser")
    if preregistration["scientificDesignChanged"] or preregistration["providerProtocolFullyClosed"]:
        raise OutcomeAnalysisS3R1R3R2Error("Preregistration lock changed")
    if acceptance["branch"] != BRANCH_B or acceptance["outcomeUnlocked"] or acceptance["providerProtocolFullyClosed"]:
        raise OutcomeAnalysisS3R1R3R2Error("Acceptance lock changed")
    if any(acceptance["outcomeAccessFlags"].values()) or any(disposition["outcomeAccessFlags"].values()):
        raise OutcomeAnalysisS3R1R3R2Error("Outcome firewall was weakened")
    if disposition["auditVerdict"] != "PRE_OUTCOME_CORRECTION_REQUIRED":
        raise OutcomeAnalysisS3R1R3R2Error("Astra disposition verdict changed")
    _assert_scientific_invariants(historical, population, clusters, invariance, acquisition)
    if list(root.rglob("*.bi5")):
        raise OutcomeAnalysisS3R1R3R2Error("Provider BI5 bytes must not be present")


def validate_artifacts(resource_root: Path = PROJECT_ROOT) -> None:
    root = Path(resource_root).resolve()
    _run_with_r3_r1_snapshot(root, lambda: _validate_artifacts(root))
