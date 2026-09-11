"""MO-R4A-S3R1-R3-R1 qualification and canonical-schema successor.

This module preserves the R3 parser and scientific package while qualifying
the provider-framing claim and reconciling the future parsed-tick hash schema.
It is documentation and offline-contract work only; it never accesses a
provider, market bytes, or outcomes.
"""

from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import dukascopy_tick_parser_s3r1_r3 as parser
import outcome_analysis_s3r1_r3 as r3
import outcome_analysis_s3r1_r1 as r1


MILESTONE = "MO-R4A-S3R1-R3-R1"
SCHEMA_VERSION = 1
AUTHORED_AT_UTC = "2026-09-11T00:00:00Z"
EXPECTED_STARTING_MASTER = "0be4ff3e69471e851249ccbc3581118ca3d9c411"

ADJUDICATION_CONTRACT = "MO_R4A_S3R1_R3_R1_DUKASCOPY_LZMA_FRAMING_ADJUDICATION_V1"
SOURCE_LOCK_CONTRACT = "MO_R4A_S3R1_R3_R1_DUKASCOPY_PROTOCOL_SOURCE_LOCK_V1"
ACQUISITION_CONTRACT = "MO_R4A_S3R1_R3_R1_MARKET_DATA_ACQUISITION_CONTRACT_V1"
PREREGISTRATION_CONTRACT = "MO_R4A_S3R1_R3_R1_OUTCOME_ANALYSIS_PREREGISTRATION_V1"
PRIMARY_POPULATION_CONTRACT = "MO_R4A_S3R1_R3_R1_PRIMARY_ANALYSIS_POPULATION_V1"
OVERLAP_CLUSTERS_CONTRACT = "MO_R4A_S3R1_R3_R1_OVERLAP_CLUSTERS_V1"
INVARIANCE_CONTRACT = "MO_R4A_S3R1_R3_R1_ANALYSIS_PLAN_INVARIANCE_AUDIT_V1"
CORE_CONTRACT = "MO_R4A_S3R1_R3_R1_FROZEN_ANALYSIS_PACKAGE_V1"
ACCEPTANCE_CONTRACT = "MO_R4A_S3R1_R3_R1_OUTCOME_ANALYSIS_PREREGISTRATION_ACCEPTANCE_V1"

HISTORICAL_R3_ADJUDICATION_HASH = "0F8F61572764E898F1D3F0E8676412A3770A45920FCFCB6A0AEDD9126C88855B"
HISTORICAL_R3_SOURCE_LOCK_HASH = "B36E946F45607B8900FA2A451DC8262C1ADB6A592850A0DAAEF04A5BD18D0314"
HISTORICAL_R3_PARSER_CONTRACT_HASH = "C91A76165893BCA308FE2DB9B3F83A2E9B0233CF2023E1AC573504C68EC3D316"
HISTORICAL_R3_PARSER_SOURCE_SHA256 = "47BEF7B1A13D8EE4EC2DDED2BDD965A27D41FCB548EC0D4D940A5535669D733E"
HISTORICAL_R3_ACQUISITION_HASH = "87D0716EFE9C0D655BB9F3C3D5DE5DBB8E6BED6B164F757F67665DB16D1E09E3"
HISTORICAL_R3_PREREGISTRATION_HASH = "DA05644AD7321F7EB5AEFC348B3672A0241C39AEC6DAEDCD46B12E275BCC8A04"
HISTORICAL_R3_POPULATION_HASH = "D2F60D5592DD4E5904079538D2938218037567626976211F794F710A87E83294"
HISTORICAL_R3_CLUSTERS_HASH = "BFE18D06940DA0B39C1D49739F97D8446412F61FC34B512C3DFC471D8AEAE6C7"
HISTORICAL_R3_INVARIANCE_HASH = "00B70974E5FA1F0A95DA5FDBED92C31A0576E33FACF64E9A7EDE839989EA27F1"
HISTORICAL_R3_CORE_HASH = "C98FCE359846C7BAE786F8AA99E60925CA26178B533C035126CFC7BC07339A99"
HISTORICAL_R3_ACCEPTANCE_HASH = "38903C4C086AEF928D490AF5F67EAC3C16E101812221E13D4BED036F1AF46C90"

BRANCH_B_STATUS = "FORMAT_ALONE_PLAUSIBLE_CROSS_SOURCE_RECONCILIATION_AWAITING_INDEPENDENT_ASTRA_DISPOSITION"
BRANCH_B_ACQUISITION_STATUS = "PLAUSIBLE_CROSS_SOURCE_RECONCILIATION_NOT_DIRECT_PROVIDER_SPECIFICATION"
BRANCH_B_PREREGISTRATION_STATUS = "S3R1_R3_R1_COMPRESSION_EVIDENCE_QUALIFIED_AND_CANONICAL_SCHEMA_RECONCILED_TARGETED_ASTRA_REAUDIT_REQUIRED"
BRANCH_B_ACCEPTANCE_STATUS = "S3R1_R3_R1_COMPRESSION_EVIDENCE_QUALIFIED_AND_CANONICAL_SCHEMA_RECONCILED_TARGETED_ASTRA_REAUDIT_REQUIRED"
BRANCH_B = "BRANCH_B_PLAUSIBLE_CROSS_SOURCE_RECONCILIATION"
NEXT_GATE = "TARGETED_ASTRA_PRE_OUTCOME_REAUDIT_WITH_COMPRESSION_UNCERTAINTY_EXPLICIT"
PARSER_REVIEW_STATUS = "OFFLINE_DETERMINISTIC_PARSER_FROZEN_FOR_TARGETED_ASTRA_REVIEW"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"

DEFAULT_ADJUDICATION_PATH = MACHINE_INTERPRETATION_ROOT / "dukascopy_lzma_framing_adjudication_s3r1_r3_r1_v1.json"
DEFAULT_SOURCE_LOCK_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_r1_protocol_source_lock.json"
DEFAULT_ACQUISITION_PATH = MACHINE_INTERPRETATION_ROOT / "market_data_acquisition_contract_s3r1_r3_r1_v1.json"
DEFAULT_PREREGISTRATION_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r3_r1_v1.json"
DEFAULT_SCHEMA_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r3_r1_v1.schema.json"
DEFAULT_PRIMARY_POPULATION_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_r1_primary_analysis_population.json"
DEFAULT_OVERLAP_CLUSTERS_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_r1_overlap_clusters.json"
DEFAULT_INVARIANCE_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_r1_analysis_plan_invariance_audit.json"
DEFAULT_CORE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r3_r1_frozen_analysis_package.json"
DEFAULT_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r3_r1_outcome_analysis_preregistration.json"
DEFAULT_REPORT_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S3R1_R3_R1_ADJUDICATION_QUALIFICATION_AND_SCHEMA_RECONCILIATION.md"


class OutcomeAnalysisS3R1R3R1Error(ValueError):
    """Raised when a successor would depart from the frozen lineage."""


def _canonical_hash(value: Any) -> str:
    return r3._canonical_hash(value)


def _without_hash(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    return {name: copy.deepcopy(item) for name, item in value.items() if name != key}


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise OutcomeAnalysisS3R1R3R1Error(f"Unable to load {label}: {path}") from exc
    if not isinstance(value, dict):
        raise OutcomeAnalysisS3R1R3R1Error(f"{label} must be a JSON object")
    return value


def _require_exact(value: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    if dict(value) != dict(expected):
        raise OutcomeAnalysisS3R1R3R1Error(f"{label} does not match the deterministic successor rebuild")


def _require_hashed(path: Path, hash_key: str, expected_hash: str, label: str) -> dict[str, Any]:
    value = _read_json(path, label)
    if value.get(hash_key) != expected_hash or _canonical_hash(_without_hash(value, hash_key)) != expected_hash:
        raise OutcomeAnalysisS3R1R3R1Error(f"Historical {label} hash changed")
    return value


def _relocate(path: Path, root: Path) -> Path:
    return root / path.relative_to(r3.PROJECT_ROOT)


def _historical_r3_paths(root: Path) -> dict[str, Path]:
    return {
        "adjudication": _relocate(r3.DEFAULT_ADJUDICATION_PATH, root),
        "sourceLock": _relocate(r3.DEFAULT_SOURCE_LOCK_PATH, root),
        "parserContract": _relocate(r3.DEFAULT_PARSER_CONTRACT_PATH, root),
        "acquisition": _relocate(r3.DEFAULT_ACQUISITION_PATH, root),
        "preregistration": _relocate(r3.DEFAULT_PREREGISTRATION_PATH, root),
        "population": _relocate(r3.DEFAULT_PRIMARY_POPULATION_PATH, root),
        "clusters": _relocate(r3.DEFAULT_OVERLAP_CLUSTERS_PATH, root),
        "invariance": _relocate(r3.DEFAULT_INVARIANCE_PATH, root),
        "core": _relocate(r3.DEFAULT_CORE_PATH, root),
        "acceptance": _relocate(r3.DEFAULT_ACCEPTANCE_PATH, root),
    }


def _historical_r3_components(root: Path = PROJECT_ROOT) -> dict[str, dict[str, Any]]:
    paths = _historical_r3_paths(root)
    expected = {
        "adjudication": ("lzmaFramingAdjudicationHash", HISTORICAL_R3_ADJUDICATION_HASH),
        "sourceLock": ("protocolSourceLockHash", HISTORICAL_R3_SOURCE_LOCK_HASH),
        "parserContract": ("parserContractHash", HISTORICAL_R3_PARSER_CONTRACT_HASH),
        "acquisition": ("marketDataAcquisitionContractHash", HISTORICAL_R3_ACQUISITION_HASH),
        "preregistration": ("preregistrationHash", HISTORICAL_R3_PREREGISTRATION_HASH),
        "population": ("primaryPopulationHash", HISTORICAL_R3_POPULATION_HASH),
        "clusters": ("overlapClustersHash", HISTORICAL_R3_CLUSTERS_HASH),
        "invariance": ("analysisPlanInvarianceAuditHash", HISTORICAL_R3_INVARIANCE_HASH),
        "core": ("analysisCoreManifestHash", HISTORICAL_R3_CORE_HASH),
        "acceptance": ("acceptanceManifestHash", HISTORICAL_R3_ACCEPTANCE_HASH),
    }
    return {
        name: _require_hashed(path, *expected[name], name)
        for name, path in paths.items()
    }


def _historical_r3_fingerprint(root: Path) -> tuple[str, ...]:
    paths = (*_historical_r3_paths(root).values(), _relocate(r3.PARSER_SOURCE_PATH, root))
    return tuple(hashlib.sha256(path.read_bytes()).hexdigest().upper() for path in paths)


@lru_cache(maxsize=4)
def _validated_historical_r3(root_string: str, fingerprint: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    root = Path(root_string)
    r3.validate_s3r1_r3_artifacts(root)
    components = _historical_r3_components(root)
    parser_path = _relocate(r3.PARSER_SOURCE_PATH, root)
    parser_hash = hashlib.sha256(parser_path.read_bytes()).hexdigest().upper()
    if parser_hash != HISTORICAL_R3_PARSER_SOURCE_SHA256:
        raise OutcomeAnalysisS3R1R3R1Error("R3 parser source changed")
    if components["parserContract"]["parserSourceSha256"] != HISTORICAL_R3_PARSER_SOURCE_SHA256:
        raise OutcomeAnalysisS3R1R3R1Error("R3 parser contract source hash changed")
    return components


def _require_historical_r3(root: Path = PROJECT_ROOT) -> dict[str, dict[str, Any]]:
    root = Path(root).resolve()
    fingerprint = _historical_r3_fingerprint(root)
    return copy.deepcopy(_validated_historical_r3(str(root), fingerprint))


def _source_claim_matrix() -> list[dict[str, Any]]:
    return [
        {
            "claim": "Dukascopy excludes XZ",
            "evidenceClass": "DIRECT_PROVIDER_FACT",
            "source": "DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_ES",
            "supported": True,
            "interpretiveStep": "None; provider prose excludes the .xz container.",
            "residualUncertainty": "The natural-language raw-LZMA wording does not name a Python framing constant.",
        },
        {
            "claim": "Official sample uses default lzma.decompress",
            "evidenceClass": "DIRECT_PROVIDER_FACT",
            "source": "DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_ES",
            "supported": True,
            "interpretiveStep": "The sample supplies no format or filter chain.",
            "residualUncertainty": "The sample does not explicitly identify FORMAT_ALONE.",
        },
        {
            "claim": "Python default equals FORMAT_AUTO",
            "evidenceClass": "DIRECT_RUNTIME_FACT",
            "source": "PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE",
            "supported": True,
            "interpretiveStep": "None; this is the documented function default.",
            "residualUncertainty": "Runtime semantics do not establish provider intent.",
        },
        {
            "claim": "FORMAT_AUTO accepts XZ and legacy LZMA",
            "evidenceClass": "DIRECT_RUNTIME_FACT",
            "source": "PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE",
            "supported": True,
            "interpretiveStep": "None; this is the documented format detection behavior.",
            "residualUncertainty": "XZ is independently excluded by the provider wording.",
        },
        {
            "claim": "FORMAT_AUTO rejects RAW",
            "evidenceClass": "DIRECT_RUNTIME_FACT",
            "source": "PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE",
            "supported": True,
            "interpretiveStep": "None; raw mode needs an explicit filter chain.",
            "residualUncertainty": "Provider natural-language raw does not necessarily mean Python FORMAT_RAW.",
        },
        {
            "claim": "FORMAT_ALONE is the legacy .lzma container",
            "evidenceClass": "DIRECT_RUNTIME_FACT",
            "source": "PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE",
            "supported": True,
            "interpretiveStep": "None; this is the documented runtime meaning.",
            "residualUncertainty": "No provider-owned source directly maps BI5 to FORMAT_ALONE.",
        },
        {
            "claim": "Dukascopy directly names FORMAT_ALONE",
            "evidenceClass": "DIRECT_PROVIDER_FACT",
            "source": "OFFICIAL_DUKASCOPY_DOCUMENTATION_SEARCH",
            "supported": False,
            "interpretiveStep": "No direct provider statement was found in the searched official material.",
            "residualUncertainty": "Provider framing identity remains unclosed pending Astra or stronger source evidence.",
        },
        {
            "claim": "FORMAT_ALONE remains the operational candidate",
            "evidenceClass": "CROSS_SOURCE_TECHNICAL_RECONCILIATION",
            "source": "DUKASCOPY_AND_PYTHON_DOCUMENTATION",
            "supported": True,
            "interpretiveStep": "Retain the only candidate compatible with the current exclusion/default reasoning.",
            "residualUncertainty": "This is not unique provider-source closure.",
        },
    ]


def build_lzma_framing_adjudication() -> dict[str, Any]:
    historical = r3.build_lzma_framing_adjudication()
    if historical["lzmaFramingAdjudicationHash"] != HISTORICAL_R3_ADJUDICATION_HASH:
        raise OutcomeAnalysisS3R1R3R1Error("R3 adjudication rebuild no longer matches its historical hash")
    body = copy.deepcopy(historical)
    body.pop("lzmaFramingAdjudicationHash", None)
    body.update(
        {
            "contract": ADJUDICATION_CONTRACT,
            "schemaVersion": SCHEMA_VERSION,
            "milestone": MILESTONE,
            "supersedesAdjudicationContract": historical["contract"],
            "supersedesAdjudicationHash": HISTORICAL_R3_ADJUDICATION_HASH,
            "historicalR3Reasoning": {
                "adjudicationStatus": historical["adjudicationStatus"],
                "decisionKind": historical["decisionKind"],
                "selectedFormat": historical["selectedFormat"],
                "sourceHash": HISTORICAL_R3_ADJUDICATION_HASH,
            },
            "sourceClaimMatrix": _source_claim_matrix(),
            "evidenceClassification": "PLAUSIBLE_CROSS_SOURCE_RECONCILIATION_NOT_DIRECT_PROVIDER_SPECIFICATION",
            "directProviderFacts": [
                "DUKASCOPY_EXCLUDES_XZ",
                "DUKASCOPY_SAMPLE_USES_DEFAULT_LZMA_DECOMPRESS",
            ],
            "directRuntimeFacts": [
                "PYTHON_DEFAULT_EQUALS_FORMAT_AUTO",
                "PYTHON_FORMAT_AUTO_ACCEPTS_XZ",
                "PYTHON_FORMAT_AUTO_ACCEPTS_FORMAT_ALONE",
                "PYTHON_FORMAT_AUTO_REJECTS_FORMAT_RAW",
                "PYTHON_FORMAT_RAW_REQUIRES_EXPLICIT_FILTER_CHAIN",
                "PYTHON_FORMAT_ALONE_IS_LEGACY_LZMA_CONTAINER",
            ],
            "crossSourceTechnicalReconciliation": [
                "XZ is eliminated by direct provider wording.",
                "Python FORMAT_RAW is incompatible with the documented no-filter default call.",
                "FORMAT_ALONE remains the frozen operational candidate.",
            ],
            "residualAmbiguity": [
                "Dukascopy does not directly name lzma.FORMAT_ALONE in the searched official material.",
                "The provider phrase raw LZMA is not treated as Python FORMAT_RAW.",
                "No real BI5 bytes may be used to settle this pre-Astra uncertainty.",
            ],
            "newAuthoritativeEvidenceFound": False,
            "dukascopyDirectlyNamesFormatAlone": False,
            "selectedOperationalParserFraming": parser.COMPRESSION_FRAMING,
            "providerFramingUniquelySourceClosed": False,
            "providerProtocolFullyClosed": False,
            "suitableForIndependentAstraReview": True,
            "adjudicationStatus": BRANCH_B_STATUS,
            "decisionKind": "CROSS_SOURCE_TECHNICAL_RECONCILIATION_WITH_EXPLICIT_RESIDUAL_AMBIGUITY",
            "uniqueConclusionReason": "FORMAT_ALONE remains the only frozen operational candidate under the current cross-source reconciliation, but provider intent is not directly source-specified.",
            "providerAccessPerformed": False,
            "marketOutcomeRead": False,
        }
    )
    for candidate in body["candidateFormats"]:
        if candidate["format"] == "FORMAT_ALONE":
            candidate["finalDisposition"] = "FROZEN_CANDIDATE_PLAUSIBLE_CROSS_SOURCE_RECONCILIATION"
    return {**body, "lzmaFramingAdjudicationHash": _canonical_hash(body)}


def build_source_lock(adjudication: Mapping[str, Any] | None = None) -> dict[str, Any]:
    expected = build_lzma_framing_adjudication()
    if adjudication is not None:
        _require_exact(adjudication, expected, "R3-R1 adjudication")
    body = {
        "contract": SOURCE_LOCK_CONTRACT,
        "schemaVersion": SCHEMA_VERSION,
        "milestone": MILESTONE,
        "supersedesProtocolSourceLockContract": r3.S3R1_R3_SOURCE_LOCK_CONTRACT,
        "supersedesProtocolSourceLockHash": HISTORICAL_R3_SOURCE_LOCK_HASH,
        "lzmaFramingAdjudicationHash": expected["lzmaFramingAdjudicationHash"],
        "sources": copy.deepcopy(expected["sourceRecords"]),
        "factsSupported": copy.deepcopy(expected["directProviderFacts"] + expected["directRuntimeFacts"]),
        "adjudicationStatus": expected["adjudicationStatus"],
        "evidenceClassification": expected["evidenceClassification"],
        "sourceClaimMatrix": copy.deepcopy(expected["sourceClaimMatrix"]),
        "providerFramingUniquelySourceClosed": False,
        "providerProtocolFullyClosed": False,
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
    }
    return {**body, "protocolSourceLockHash": _canonical_hash(body)}


def _canonical_hash_record_definition(parser_contract: Mapping[str, Any]) -> dict[str, Any]:
    canonical = parser_contract["canonicalSerialization"]
    return {
        "fields": copy.deepcopy(canonical["fields"]),
        "timestampFormat": canonical["timestampFormat"],
        "serialization": canonical["representation"],
        "hash": canonical["parsedTicksSha256"],
    }


def build_market_data_acquisition_contract(
    resource_root: Path = PROJECT_ROOT,
    *,
    adjudication: Mapping[str, Any] | None = None,
    source_lock: Mapping[str, Any] | None = None,
    parser_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _require_historical_r3(root)
    expected_adjudication = build_lzma_framing_adjudication()
    expected_lock = build_source_lock(expected_adjudication)
    expected_parser = r3.build_parser_contract()
    if expected_parser["parserContractHash"] != HISTORICAL_R3_PARSER_CONTRACT_HASH:
        raise OutcomeAnalysisS3R1R3R1Error("Parser contract changed during R3-R1")
    if adjudication is not None:
        _require_exact(adjudication, expected_adjudication, "R3-R1 adjudication")
    if source_lock is not None:
        _require_exact(source_lock, expected_lock, "R3-R1 source lock")
    if parser_contract is not None:
        _require_exact(parser_contract, expected_parser, "historical parser contract")
    body = copy.deepcopy(historical["acquisition"])
    body.pop("marketDataAcquisitionContractHash", None)
    canonical = _canonical_hash_record_definition(expected_parser)
    body.pop("canonicalTickSchema", None)
    body.update(
        {
            "contract": ACQUISITION_CONTRACT,
            "schemaVersion": SCHEMA_VERSION,
            "milestone": MILESTONE,
            "status": "PRE_REQUEST_ACQUISITION_PROTOCOL_FROZEN_FRAMING_CANDIDATE_AWAITING_ASTRA",
            "supersedesContract": historical["acquisition"]["contract"],
            "supersedesHash": HISTORICAL_R3_ACQUISITION_HASH,
            "protocolSourceLockHash": expected_lock["protocolSourceLockHash"],
            "lzmaFramingAdjudicationHash": expected_adjudication["lzmaFramingAdjudicationHash"],
            "compression": {
                "status": BRANCH_B_ACQUISITION_STATUS,
                "evidenceStatus": BRANCH_B_ACQUISITION_STATUS,
                "compressionFraming": parser.COMPRESSION_FRAMING,
                "operationalFrozenCandidate": parser.COMPRESSION_FRAMING,
                "pythonConstant": "lzma.FORMAT_ALONE",
                "filterChainRequired": False,
                "filterChain": [],
                "parserUseAuthorized": False,
                "parserUseForLiveOutcomeAcquisitionAllowed": False,
                "parserImplementationFrozen": True,
                "providerFramingUniquelySourceClosed": False,
            },
            "parser": {
                "status": PARSER_REVIEW_STATUS,
                "module": "gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3.py",
                "parserContractHash": expected_parser["parserContractHash"],
                "parserSourceSha256": expected_parser["parserSourceSha256"],
                "offlineOnlyWhenAuthorized": True,
                "networkAccess": False,
                "productFormat": parser.COMPRESSION_FRAMING,
                "parserImplementationFrozen": True,
                "providerFramingUniquelySourceClosed": False,
                "parserUseForLiveOutcomeAcquisitionAllowed": False,
            },
            "canonicalParsedTickHashRecord": canonical,
            "nonCanonicalInspectionFields": {
                "fields": ["askVolumeDecodedFloat32", "bidVolumeDecodedFloat32"],
                "status": "NOT_INCLUDED_IN_PARSED_TICKS_HASH",
            },
            "parsedCapturePolicy": {
                "canonicalRecordSchema": "canonicalParsedTickHashRecord",
                "parsedTicksSha256": canonical["hash"],
                "rawByteHashRequiredBeforeParse": True,
                "outcomeScoringAllowed": False,
            },
            "providerProtocolFullyClosed": False,
            "providerFramingUniquelySourceClosed": False,
            "parserImplementationFrozen": True,
            "providerAccessPerformed": False,
            "marketOutcomeRead": False,
            "outcomeUnlockAllowed": False,
        }
    )
    body["rawCapturePolicy"]["futureManifestParsedTicksHashDefinition"] = "canonicalParsedTickHashRecord"
    body["rawCapturePolicy"]["futureManifestParsedTicksHashAlgorithm"] = canonical["hash"]
    body["futureRawAcquisitionManifest"] = {
        "contract": "MO_R4A_S4_MARKET_DATA_RAW_ACQUISITION_MANIFEST_V1",
        "requiredFields": copy.deepcopy(body["rawCapturePolicy"]["requiredFutureManifestFields"]),
        "parsedTicksSha256": canonical["hash"],
        "parsedTicksSha256Definition": "canonicalParsedTickHashRecord",
    }
    if body["nativePartitioning"]["uniqueProviderPartitionCount"] != 15 or body["frozenIntervalSet"]["totalCount"] != 39:
        raise OutcomeAnalysisS3R1R3R1Error("R3-R1 changed the 15-partition/39-window plan")
    return {**body, "marketDataAcquisitionContractHash": _canonical_hash(body)}


def build_preregistration(
    resource_root: Path = PROJECT_ROOT,
    *,
    adjudication: Mapping[str, Any] | None = None,
    source_lock: Mapping[str, Any] | None = None,
    acquisition: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _require_historical_r3(root)
    expected_adjudication = build_lzma_framing_adjudication()
    expected_lock = build_source_lock(expected_adjudication)
    expected_parser = historical["parserContract"]
    expected_acquisition = build_market_data_acquisition_contract(
        root, adjudication=expected_adjudication, source_lock=expected_lock, parser_contract=expected_parser
    )
    if adjudication is not None:
        _require_exact(adjudication, expected_adjudication, "R3-R1 adjudication")
    if source_lock is not None:
        _require_exact(source_lock, expected_lock, "R3-R1 source lock")
    if acquisition is not None:
        _require_exact(acquisition, expected_acquisition, "R3-R1 acquisition")
    body = copy.deepcopy(historical["preregistration"])
    body.pop("preregistrationHash", None)
    body.update(
        {
            "contract": PREREGISTRATION_CONTRACT,
            "schemaVersion": SCHEMA_VERSION,
            "milestone": MILESTONE,
            "startingMaster": EXPECTED_STARTING_MASTER,
            "preregistrationAuthoredAtUtc": AUTHORED_AT_UTC,
            "status": BRANCH_B_PREREGISTRATION_STATUS,
            "nextGate": NEXT_GATE,
            "supersedesPreregistrationContract": historical["preregistration"]["contract"],
            "supersedesPreregistrationHash": HISTORICAL_R3_PREREGISTRATION_HASH,
            "supersedesAcceptanceManifestHash": HISTORICAL_R3_ACCEPTANCE_HASH,
            "correctionReason": "LZMA_EVIDENCE_QUALIFICATION_AND_CANONICAL_PARSED_SCHEMA_RECONCILIATION_WITHOUT_SCIENTIFIC_DESIGN_CHANGE",
            "providerProtocolClosureReason": BRANCH_B_ACQUISITION_STATUS,
            "lzmaFramingAdjudicationHash": expected_adjudication["lzmaFramingAdjudicationHash"],
            "protocolSourceLockHash": expected_lock["protocolSourceLockHash"],
            "marketDataAcquisitionContractHash": expected_acquisition["marketDataAcquisitionContractHash"],
            "parserContractHash": expected_parser["parserContractHash"],
            "parserSourceSha256": expected_parser["parserSourceSha256"],
            "providerPartitionPlanHash": r3.HISTORICAL_R2_PARTITION_PLAN_HASH,
            "providerProtocolFullyClosed": False,
            "parserImplementationFrozen": True,
            "scientificDesignChanged": False,
        }
    )
    return {**body, "preregistrationHash": _canonical_hash(body)}


def build_schema(preregistration: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = copy.deepcopy(preregistration) if preregistration is not None else build_preregistration(PROJECT_ROOT)
    schema = r3.build_s3r1_r3_schema(r3.build_s3r1_r3_preregistration(PROJECT_ROOT))
    schema["$id"] = PREREGISTRATION_CONTRACT
    schema["title"] = "MO-R4A-S3R1-R3-R1 qualified pre-outcome acquisition preregistration"
    properties = schema["properties"]
    properties["contract"]["const"] = PREREGISTRATION_CONTRACT
    properties["milestone"]["const"] = MILESTONE
    properties["startingMaster"]["const"] = EXPECTED_STARTING_MASTER
    properties["status"]["const"] = BRANCH_B_PREREGISTRATION_STATUS
    properties["nextGate"]["const"] = NEXT_GATE
    # The successor keeps the historical schema shape, but its lineage and
    # evidence hashes intentionally point at the R3 predecessor and the new
    # R3-R1 qualification artifacts.  Refresh every top-level const from the
    # payload so inherited R2/R3 values cannot survive in the successor schema.
    for field, rule in properties.items():
        if field in payload and isinstance(rule, dict) and "const" in rule:
            rule["const"] = copy.deepcopy(payload[field])
    properties["providerProtocolFullyClosed"] = {"type": "boolean", "const": False}
    properties["parserImplementationFrozen"] = {"type": "boolean", "const": True}
    for field in ("providerProtocolFullyClosed", "parserImplementationFrozen"):
        if field not in schema["required"]:
            schema["required"].append(field)
    if payload.get("contract") != PREREGISTRATION_CONTRACT:
        raise OutcomeAnalysisS3R1R3R1Error("Schema payload is not the R3-R1 preregistration")
    return schema


def _successor_from_r3(
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


def build_primary_population(resource_root: Path = PROJECT_ROOT, *, preregistration: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _require_historical_r3(root)
    expected_preregistration = build_preregistration(root)
    if preregistration is not None:
        _require_exact(preregistration, expected_preregistration, "R3-R1 preregistration")
    return _successor_from_r3(
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
            "protocolQualificationDoesNotChangePopulation": True,
        },
    )


def build_overlap_clusters(resource_root: Path = PROJECT_ROOT, *, population: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _require_historical_r3(root)
    expected_population = build_primary_population(root)
    if population is not None:
        _require_exact(population, expected_population, "R3-R1 primary population")
    return _successor_from_r3(
        historical["clusters"],
        contract=OVERLAP_CLUSTERS_CONTRACT,
        hash_key="overlapClustersHash",
        supersedes_contract_key="supersedesOverlapClustersContract",
        supersedes_hash_key="supersedesOverlapClustersHash",
        updates={
            "primaryPopulationHash": expected_population["primaryPopulationHash"],
            "scientificClustersUnchanged": True,
            "protocolQualificationDoesNotChangeClusters": True,
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
    historical = _require_historical_r3(root)
    expected_preregistration = build_preregistration(root)
    expected_population = build_primary_population(root, preregistration=expected_preregistration)
    expected_clusters = build_overlap_clusters(root, population=expected_population)
    if preregistration is not None:
        _require_exact(preregistration, expected_preregistration, "R3-R1 preregistration")
    if population is not None:
        _require_exact(population, expected_population, "R3-R1 primary population")
    if clusters is not None:
        _require_exact(clusters, expected_clusters, "R3-R1 overlap clusters")
    return _successor_from_r3(
        historical["invariance"],
        contract=INVARIANCE_CONTRACT,
        hash_key="analysisPlanInvarianceAuditHash",
        supersedes_contract_key="supersedesInvarianceAuditContract",
        supersedes_hash_key="supersedesInvarianceAuditHash",
        updates={
            "preregistrationHash": expected_preregistration["preregistrationHash"],
            "primaryPopulationHash": expected_population["primaryPopulationHash"],
            "overlapClustersHash": expected_clusters["overlapClustersHash"],
            "lzmaEvidenceReclassificationDoesNotChangeScience": True,
            "canonicalParsedSchemaCorrectionDoesNotChangeScience": True,
            "parserSourceUnchanged": True,
            "providerPartitionPlanUnchanged": True,
            "nativePartitionCountUnchanged": True,
            "analysisWindowCountUnchanged": True,
            "withinSidePermutationUniverseUnchanged": True,
            "providerProtocolDoesNotChangeScientificDesign": True,
            "offlineParserSourceBound": True,
            "syntheticFixtureOnly": True,
            "scientificDesignChanged": False,
        },
    )


def build_analysis_core_manifest(
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
    acquisition: Mapping[str, Any],
    source_lock: Mapping[str, Any],
    adjudication: Mapping[str, Any],
    parser_contract: Mapping[str, Any],
) -> dict[str, Any]:
    body = {
        "contract": CORE_CONTRACT,
        "schemaVersion": SCHEMA_VERSION,
        "milestone": MILESTONE,
        "upstreamHashes": copy.deepcopy(r3.EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": preregistration["preregistrationHash"],
        "primaryPopulationHash": population["primaryPopulationHash"],
        "overlapClustersHash": clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
        "protocolSourceLockHash": source_lock["protocolSourceLockHash"],
        "providerPartitionPlanHash": r3.HISTORICAL_R2_PARTITION_PLAN_HASH,
        "lzmaFramingAdjudicationHash": adjudication["lzmaFramingAdjudicationHash"],
        "parserContractHash": parser_contract["parserContractHash"],
        "parserSourceSha256": parser_contract["parserSourceSha256"],
    }
    return {**body, "analysisCoreManifestHash": _canonical_hash(body)}


def build_acceptance_manifest(
    resource_root: Path = PROJECT_ROOT,
    *,
    adjudication: Mapping[str, Any] | None = None,
    source_lock: Mapping[str, Any] | None = None,
    parser_contract: Mapping[str, Any] | None = None,
    acquisition: Mapping[str, Any] | None = None,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
    invariance: Mapping[str, Any] | None = None,
    core: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    historical = _require_historical_r3(root)
    expected_adjudication = build_lzma_framing_adjudication()
    expected_lock = build_source_lock(expected_adjudication)
    expected_parser = historical["parserContract"]
    expected_acquisition = build_market_data_acquisition_contract(
        root, adjudication=expected_adjudication, source_lock=expected_lock, parser_contract=expected_parser
    )
    expected_preregistration = build_preregistration(
        root, adjudication=expected_adjudication, source_lock=expected_lock, acquisition=expected_acquisition
    )
    expected_population = build_primary_population(root, preregistration=expected_preregistration)
    expected_clusters = build_overlap_clusters(root, population=expected_population)
    expected_invariance = build_invariance_audit(
        root, preregistration=expected_preregistration, population=expected_population, clusters=expected_clusters
    )
    expected_core = build_analysis_core_manifest(
        expected_preregistration,
        expected_population,
        expected_clusters,
        expected_invariance,
        expected_acquisition,
        expected_lock,
        expected_adjudication,
        expected_parser,
    )
    supplied = {
        "R3-R1 adjudication": (adjudication, expected_adjudication),
        "R3-R1 source lock": (source_lock, expected_lock),
        "historical parser contract": (parser_contract, expected_parser),
        "R3-R1 acquisition": (acquisition, expected_acquisition),
        "R3-R1 preregistration": (preregistration, expected_preregistration),
        "R3-R1 population": (population, expected_population),
        "R3-R1 clusters": (clusters, expected_clusters),
        "R3-R1 invariance": (invariance, expected_invariance),
        "R3-R1 core": (core, expected_core),
    }
    for label, (provided, expected) in supplied.items():
        if provided is not None:
            _require_exact(provided, expected, label)
    body = {
        "contract": ACCEPTANCE_CONTRACT,
        "schemaVersion": SCHEMA_VERSION,
        "milestone": MILESTONE,
        "status": BRANCH_B_ACCEPTANCE_STATUS,
        "branch": BRANCH_B,
        "nextGate": NEXT_GATE,
        "startingMaster": EXPECTED_STARTING_MASTER,
        "supersedesAcceptanceManifestContract": historical["acceptance"]["contract"],
        "supersedesAcceptanceManifestHash": HISTORICAL_R3_ACCEPTANCE_HASH,
        "upstreamHashes": copy.deepcopy(r3.EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": expected_preregistration["preregistrationHash"],
        "primaryPopulationHash": expected_population["primaryPopulationHash"],
        "overlapClustersHash": expected_clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": expected_invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": expected_acquisition["marketDataAcquisitionContractHash"],
        "protocolSourceLockHash": expected_lock["protocolSourceLockHash"],
        "providerPartitionPlanHash": r3.HISTORICAL_R2_PARTITION_PLAN_HASH,
        "lzmaFramingAdjudicationHash": expected_adjudication["lzmaFramingAdjudicationHash"],
        "parserContractHash": expected_parser["parserContractHash"],
        "parserSourceSha256": expected_parser["parserSourceSha256"],
        "analysisCoreManifestHash": expected_core["analysisCoreManifestHash"],
        "compressionEvidenceStatus": expected_adjudication["evidenceClassification"],
        "operationalFrozenParserFraming": parser.COMPRESSION_FRAMING,
        "providerProtocolFullyClosed": False,
        "parserImplementationFrozen": True,
        "canonicalParsedSchemaReconciled": True,
        "activeBlockers": ["OUTCOME_UNLOCK_NOT_AUTHORIZED", "TARGETED_ASTRA_REAUDIT_NOT_PERFORMED", "PROVIDER_FRAMING_DIRECT_SOURCE_SPECIFICATION_UNCLOSED"],
        "populationAccounting": copy.deepcopy(expected_population["populationCounts"]),
        "marketDataRead": False,
        "outcomeDataRead": False,
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
        "executionAllowed": False,
        "outcomeUnlocked": False,
        "outcomeAccessFlags": {flag: False for flag in r1.ACCESS_FLAGS},
    }
    return {**body, "acceptanceManifestHash": _canonical_hash(body)}


def _artifact_paths(root: Path = PROJECT_ROOT) -> dict[str, Path]:
    root = Path(root).resolve()
    return {
        "adjudication": _relocate(DEFAULT_ADJUDICATION_PATH, root),
        "sourceLock": _relocate(DEFAULT_SOURCE_LOCK_PATH, root),
        "acquisition": _relocate(DEFAULT_ACQUISITION_PATH, root),
        "preregistration": _relocate(DEFAULT_PREREGISTRATION_PATH, root),
        "schema": _relocate(DEFAULT_SCHEMA_PATH, root),
        "population": _relocate(DEFAULT_PRIMARY_POPULATION_PATH, root),
        "clusters": _relocate(DEFAULT_OVERLAP_CLUSTERS_PATH, root),
        "invariance": _relocate(DEFAULT_INVARIANCE_PATH, root),
        "core": _relocate(DEFAULT_CORE_PATH, root),
        "acceptance": _relocate(DEFAULT_ACCEPTANCE_PATH, root),
        "report": _relocate(DEFAULT_REPORT_PATH, root),
    }


def render_report(
    adjudication: Mapping[str, Any],
    source_lock: Mapping[str, Any],
    acquisition: Mapping[str, Any],
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
    core: Mapping[str, Any],
    acceptance: Mapping[str, Any],
) -> str:
    claim_rows = "\n".join(
        f"| {row['claim']} | {row['evidenceClass']} | {row['source']} | {row['supported']} | {row['interpretiveStep']} | {row['residualUncertainty']} |"
        for row in adjudication["sourceClaimMatrix"]
    )
    old_fields = [
        "timestampUtc",
        "bidNative",
        "askNative",
        "bidVolumeMillionsBaseCurrency",
        "askVolumeMillionsBaseCurrency",
        "recordIndex",
    ]
    new_fields = acquisition["canonicalParsedTickHashRecord"]["fields"]
    return "\n".join(
        [
            "# MO-R4A-S3R1-R3-R1 Adjudication Qualification And Schema Reconciliation",
            "",
            "## Central Review Findings",
            "",
            f"R3 remains historical at `{HISTORICAL_R3_ADJUDICATION_HASH}`. Its cross-source elimination reasoning is retained, but its provider-framing certainty is qualified. The current official Dukascopy material does not directly name `lzma.FORMAT_ALONE`; no stronger provider-owned evidence was found. The active state is `{adjudication['adjudicationStatus']}`.",
            "",
            "## Evidence Classification",
            "",
            f"Branch: `{acceptance['branch']}`. Direct provider facts, direct runtime facts, and cross-source technical reconciliation are separated below.",
            "",
            "| Claim | Evidence class | Source | Supported | Interpretive step | Residual uncertainty |",
            "| --- | --- | --- | --- | --- | --- |",
            claim_rows,
            "",
            "No searched official Dukascopy source directly names `FORMAT_ALONE`. The natural-language phrase raw LZMA is not equated with Python `FORMAT_RAW`. `PYTHON_LZMA_FORMAT_ALONE` remains the single frozen operational candidate, but `providerFramingUniquelySourceClosed=false`.",
            "",
            "## Canonical Parsed-Tick Schema",
            "",
            f"The R3 acquisition artifact used the inconsistent fields `{old_fields}` and serialization `UTF8_JSON_LINES_SORTED_KEYS_ONE_OBJECT_PER_CANONICAL_TICK_TRAILING_LF`.",
            f"The R3-R1 acquisition successor now declares exactly `{new_fields}` under `canonicalParsedTickHashRecord`.",
            f"Serialization is `{acquisition['canonicalParsedTickHashRecord']['serialization']}` with timestamp `{acquisition['canonicalParsedTickHashRecord']['timestampFormat']}` and `{acquisition['canonicalParsedTickHashRecord']['hash']}`.",
            "Decoded float volumes remain available only as non-canonical inspection fields and are explicitly excluded from `parsedTicksSha256`.",
            "The future S4 manifest keeps `rawSha256`, `parserContractHash`, `parserSourceSha256`, `parsedRecordCount`, `parsedTicksSha256`, `firstTimestampUtc`, and `lastTimestampUtc`; its parsed hash points to `canonicalParsedTickHashRecord`.",
            "",
            "## Parser And Science",
            "",
            f"Parser source is unchanged at `{HISTORICAL_R3_PARSER_SOURCE_SHA256}`. Parser contract is reused unchanged at `{HISTORICAL_R3_PARSER_CONTRACT_HASH}`. No fallback format, trial decompression, filter guessing, provider access, or real payload validation was added.",
            f"The 24 identities, 14 directional rows, 13 primary rows, 39 analytical windows, 15 native daily partitions, C1-C4 clusters, and 40-state within-side permutation universe remain unchanged. The R3-R1 invariance audit is `{invariance['analysisPlanInvarianceAuditHash']}`.",
            "",
            "## Lineage Hashes",
            "",
            f"R3-R1 adjudication `{adjudication['lzmaFramingAdjudicationHash']}`; source lock `{source_lock['protocolSourceLockHash']}`; acquisition `{acquisition['marketDataAcquisitionContractHash']}`; preregistration `{preregistration['preregistrationHash']}`; population `{population['primaryPopulationHash']}`; clusters `{clusters['overlapClustersHash']}`; invariance `{invariance['analysisPlanInvarianceAuditHash']}`; core `{core['analysisCoreManifestHash']}`; acceptance `{acceptance['acceptanceManifestHash']}`.",
            "",
            "## Validation",
            "",
            "Focused source tests cover Branch B honesty, historical hash immutability, exact canonical schema equality, independent canonical bytes and hash recomputation, decoded-float exclusion, schema validation, mutation rejection, 8192-vector equality, 2744 timing equality, and the outcome firewall.",
            "",
            "All provider, market, outcome, review, scoring, Auto Suggest, ML, MT5, production, and execution flags remain false. The next gate is `TARGETED_ASTRA_PRE_OUTCOME_REAUDIT_WITH_COMPRESSION_UNCERTAINTY_EXPLICIT`.",
            "",
        ]
    )


def write_artifacts(resource_root: Path = PROJECT_ROOT, *, outcome_source: object | None = None) -> dict[str, Path]:
    if outcome_source is not None:
        raise OutcomeAnalysisS3R1R3R1Error("R3-R1 cannot accept provider, market, tick, or outcome input")
    root = Path(resource_root).resolve()
    adjudication = build_lzma_framing_adjudication()
    source_lock = build_source_lock(adjudication)
    parser_contract = _historical_r3_components(root)["parserContract"]
    acquisition = build_market_data_acquisition_contract(
        root, adjudication=adjudication, source_lock=source_lock, parser_contract=parser_contract
    )
    preregistration = build_preregistration(
        root, adjudication=adjudication, source_lock=source_lock, acquisition=acquisition
    )
    schema = build_schema(preregistration)
    population = build_primary_population(root, preregistration=preregistration)
    clusters = build_overlap_clusters(root, population=population)
    invariance = build_invariance_audit(
        root, preregistration=preregistration, population=population, clusters=clusters
    )
    core = build_analysis_core_manifest(
        preregistration, population, clusters, invariance, acquisition, source_lock, adjudication, parser_contract
    )
    acceptance = build_acceptance_manifest(
        root,
        adjudication=adjudication,
        source_lock=source_lock,
        parser_contract=parser_contract,
        acquisition=acquisition,
        preregistration=preregistration,
        population=population,
        clusters=clusters,
        invariance=invariance,
        core=core,
    )
    artifacts = _artifact_paths(root)
    for name, value in {
        "adjudication": adjudication,
        "sourceLock": source_lock,
        "acquisition": acquisition,
        "preregistration": preregistration,
        "schema": schema,
        "population": population,
        "clusters": clusters,
        "invariance": invariance,
        "core": core,
        "acceptance": acceptance,
    }.items():
        _write_json(artifacts[name], value)
    artifacts["report"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["report"].write_text(
        render_report(adjudication, source_lock, acquisition, preregistration, population, clusters, invariance, core, acceptance),
        encoding="utf-8",
    )
    return artifacts


def _validate_canonical_schema(parser_contract: Mapping[str, Any], acquisition: Mapping[str, Any]) -> None:
    expected = _canonical_hash_record_definition(parser_contract)
    if acquisition.get("canonicalTickSchema") is not None:
        raise OutcomeAnalysisS3R1R3R1Error("R3-R1 acquisition retained the inconsistent canonicalTickSchema")
    if acquisition.get("canonicalParsedTickHashRecord") != expected:
        raise OutcomeAnalysisS3R1R3R1Error("Acquisition canonical parsed-tick schema does not match parser contract")
    if acquisition["parsedCapturePolicy"]["canonicalRecordSchema"] != "canonicalParsedTickHashRecord":
        raise OutcomeAnalysisS3R1R3R1Error("Parsed capture policy does not point to the canonical record")
    if acquisition["futureRawAcquisitionManifest"]["parsedTicksSha256Definition"] != "canonicalParsedTickHashRecord":
        raise OutcomeAnalysisS3R1R3R1Error("Future manifest uses a competing parsed hash definition")
    if acquisition["futureRawAcquisitionManifest"]["parsedTicksSha256"] != expected["hash"]:
        raise OutcomeAnalysisS3R1R3R1Error("Future manifest parsed hash algorithm differs from parser contract")
    if acquisition["nonCanonicalInspectionFields"]["status"] != "NOT_INCLUDED_IN_PARSED_TICKS_HASH":
        raise OutcomeAnalysisS3R1R3R1Error("Decoded volume exclusion is not explicit")


def validate_artifacts(resource_root: Path = PROJECT_ROOT) -> None:
    root = Path(resource_root).resolve()
    historical = _require_historical_r3(root)
    parser_contract = historical["parserContract"]
    if parser_contract["parserContractHash"] != HISTORICAL_R3_PARSER_CONTRACT_HASH:
        raise OutcomeAnalysisS3R1R3R1Error("Parser contract is not the unchanged R3 contract")
    adjudication = build_lzma_framing_adjudication()
    source_lock = build_source_lock(adjudication)
    acquisition = build_market_data_acquisition_contract(
        root, adjudication=adjudication, source_lock=source_lock, parser_contract=parser_contract
    )
    preregistration = build_preregistration(
        root, adjudication=adjudication, source_lock=source_lock, acquisition=acquisition
    )
    schema = build_schema(preregistration)
    population = build_primary_population(root, preregistration=preregistration)
    clusters = build_overlap_clusters(root, population=population)
    invariance = build_invariance_audit(
        root, preregistration=preregistration, population=population, clusters=clusters
    )
    core = build_analysis_core_manifest(
        preregistration, population, clusters, invariance, acquisition, source_lock, adjudication, parser_contract
    )
    acceptance = build_acceptance_manifest(
        root,
        adjudication=adjudication,
        source_lock=source_lock,
        parser_contract=parser_contract,
        acquisition=acquisition,
        preregistration=preregistration,
        population=population,
        clusters=clusters,
        invariance=invariance,
        core=core,
    )
    actual = _artifact_paths(root)
    for name, value in {
        "adjudication": adjudication,
        "sourceLock": source_lock,
        "acquisition": acquisition,
        "preregistration": preregistration,
        "population": population,
        "clusters": clusters,
        "invariance": invariance,
        "core": core,
        "acceptance": acceptance,
    }.items():
        _require_exact(_read_json(actual[name], name), value, name)
    actual_schema = _read_json(actual["schema"], "schema")
    _require_exact(actual_schema, schema, "schema")
    r1.validate_json_schema_instance(preregistration, schema)
    _validate_canonical_schema(parser_contract, acquisition)
    if adjudication["adjudicationStatus"] != BRANCH_B_STATUS or adjudication["providerProtocolFullyClosed"]:
        raise OutcomeAnalysisS3R1R3R1Error("Branch B provider-framing qualification is missing")
    if acquisition["providerProtocolFullyClosed"] or acquisition["compression"]["parserUseForLiveOutcomeAcquisitionAllowed"]:
        raise OutcomeAnalysisS3R1R3R1Error("Acquisition contract over-authorizes the parser")
    if preregistration["providerProtocolFullyClosed"] or preregistration["scientificDesignChanged"]:
        raise OutcomeAnalysisS3R1R3R1Error("Preregistration has an invalid Branch B or scientific state")
    if acceptance["branch"] != BRANCH_B or acceptance["providerProtocolFullyClosed"] or acceptance["outcomeUnlocked"]:
        raise OutcomeAnalysisS3R1R3R1Error("Acceptance manifest is not the qualified locked Branch B state")
    if any(acceptance["outcomeAccessFlags"].values()):
        raise OutcomeAnalysisS3R1R3R1Error("Outcome firewall was weakened")
    if hashlib.sha256(_relocate(r3.PARSER_SOURCE_PATH, root).read_bytes()).hexdigest().upper() != HISTORICAL_R3_PARSER_SOURCE_SHA256:
        raise OutcomeAnalysisS3R1R3R1Error("Parser source changed")
    if list(root.rglob("*.bi5")):
        raise OutcomeAnalysisS3R1R3R1Error("Provider BI5 bytes must not be present")
