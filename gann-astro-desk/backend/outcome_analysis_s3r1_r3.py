"""MO-R4A-S3R1-R3 source adjudication and offline-parser successor.

R3 closes the LZMA framing from public technical documentation only.  It never
contacts a provider, accepts market/outcome input, or evaluates the experiment.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import dukascopy_tick_parser_s3r1_r3 as parser
import outcome_analysis_s3 as s3
import outcome_analysis_s3r1_r1 as r1
import outcome_analysis_s3r1_r2 as r2


S3R1_R3_MILESTONE = "MO-R4A-S3R1-R3"
S3R1_R3_SCHEMA_VERSION = 1
S3R1_R3_AUTHORED_AT_UTC = "2026-09-11T00:00:00Z"
S3R1_R3_EXPECTED_STARTING_MASTER = "9880979058e51d9fe15bd9c31b3044df35386dac"

S3R1_R3_ADJUDICATION_CONTRACT = "MO_R4A_S3R1_R3_DUKASCOPY_LZMA_FRAMING_ADJUDICATION_V1"
S3R1_R3_SOURCE_LOCK_CONTRACT = "MO_R4A_S3R1_R3_DUKASCOPY_PROTOCOL_SOURCE_LOCK_V1"
S3R1_R3_PARSER_CONTRACT = parser.PARSER_CONTRACT
S3R1_R3_ACQUISITION_CONTRACT = "MO_R4A_S3R1_R3_MARKET_DATA_ACQUISITION_CONTRACT_V1"
S3R1_R3_PREREGISTRATION_CONTRACT = "MO_R4A_S3R1_R3_OUTCOME_ANALYSIS_PREREGISTRATION_V1"
S3R1_R3_PRIMARY_POPULATION_CONTRACT = "MO_R4A_S3R1_R3_PRIMARY_ANALYSIS_POPULATION_V1"
S3R1_R3_OVERLAP_CLUSTERS_CONTRACT = "MO_R4A_S3R1_R3_OVERLAP_CLUSTERS_V1"
S3R1_R3_INVARIANCE_CONTRACT = "MO_R4A_S3R1_R3_ANALYSIS_PLAN_INVARIANCE_AUDIT_V1"
S3R1_R3_CORE_CONTRACT = "MO_R4A_S3R1_R3_FROZEN_ANALYSIS_PACKAGE_V1"
S3R1_R3_ACCEPTANCE_CONTRACT = "MO_R4A_S3R1_R3_OUTCOME_ANALYSIS_PREREGISTRATION_ACCEPTANCE_V1"

HISTORICAL_R2_PROTOCOL_EVIDENCE_HASH = "4D5322F005B97EFCAB31F3F2E0AACDE2C0167B8BCF04ECD632626D1F0610CBD1"
HISTORICAL_R2_SOURCE_LOCK_HASH = "394AE5B524C6090199040BA8201C384DD4AF000FDE72ED9880753DBB7736B3C3"
HISTORICAL_R2_PARTITION_PLAN_HASH = "5C39D983DD11288B24ABCF0E17F38C862A6B3B283CC68ABC3377C3324BBD738D"
HISTORICAL_R2_ACQUISITION_HASH = "A1C2129E9395C9850A66A595F3529563AFBDA14E10C8F0B7DBB3A78897ECF500"
HISTORICAL_R2_PREREGISTRATION_HASH = "BAF10DF4B71D53361B07F417752864EF26F7BEC5572EA4DAB71F5287C1959DF5"
HISTORICAL_R2_POPULATION_HASH = "DA997F393CC324FCCFF24259C9F2A259F65BA08E59C4348825B14FF4324F3A1E"
HISTORICAL_R2_CLUSTERS_HASH = "C5F90F8845785C0DCE001C670494B7074166EEBA7BF94611E687CA0382DFB4FC"
HISTORICAL_R2_INVARIANCE_HASH = "0365BFD41C3CC370601FC58234661B3323965C3FFC3AC7643D8782F31CE1332A"
HISTORICAL_R2_CORE_HASH = "3C28D0A0C21FED0C9C295F76B23E5EFBA9FEB0CCA54B89484D2B8E489AFE5AF1"
HISTORICAL_R2_ACCEPTANCE_HASH = "6952B8AAE0AEABDBD7CB2324F4E674D12BC712EA239883C730E669DB782923FB"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"

DEFAULT_ADJUDICATION_PATH = MACHINE_INTERPRETATION_ROOT / "dukascopy_lzma_framing_adjudication_s3r1_r3_v1.json"
DEFAULT_SOURCE_LOCK_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_protocol_source_lock.json"
DEFAULT_PARSER_CONTRACT_PATH = MACHINE_INTERPRETATION_ROOT / "dukascopy_tick_parser_contract_s3r1_r3_v1.json"
DEFAULT_ACQUISITION_PATH = MACHINE_INTERPRETATION_ROOT / "market_data_acquisition_contract_s3r1_r3_v1.json"
DEFAULT_PREREGISTRATION_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r3_v1.json"
DEFAULT_SCHEMA_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r3_v1.schema.json"
DEFAULT_PRIMARY_POPULATION_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_primary_analysis_population.json"
DEFAULT_OVERLAP_CLUSTERS_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_overlap_clusters.json"
DEFAULT_INVARIANCE_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r3_analysis_plan_invariance_audit.json"
DEFAULT_CORE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r3_frozen_analysis_package.json"
DEFAULT_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r3_outcome_analysis_preregistration.json"
DEFAULT_REPORT_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S3R1_R3_LZMA_FRAMING_ADJUDICATION.md"
PARSER_SOURCE_PATH = Path(parser.__file__).resolve()

DUKASCOPY_ES_EXPORT_URL = "https://www.dukascopy.com/wiki/es/development/data-export/"
DUKASCOPY_FR_EXPORT_URL = "https://www.dukascopy.com/wiki/fr/development/data-export/"
PYTHON_LZMA_URL = "https://docs.python.org/3/library/lzma.html"
LIBLZMA_CONTAINER_URL = "https://tukaani.org/xz/liblzma-api/container_8h.html"
PYTHON_DOCS_VERSION = "Python 3.14.7 documentation"
ACCESS_FLAGS = tuple(r1.ACCESS_FLAGS)
EXPECTED_UPSTREAM_HASHES = copy.deepcopy(r1.EXPECTED_UPSTREAM_HASHES)


class OutcomeAnalysisS3R1R3Error(ValueError):
    """Raised when R3 would depart from immutable science or parser provenance."""


def _canonical_hash(value: Any) -> str:
    return s3._canonical_hash(value)


def _without_hash(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    return {name: copy.deepcopy(item) for name, item in value.items() if name != key}


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise OutcomeAnalysisS3R1R3Error(f"Unable to load {label}: {path}") from exc
    if not isinstance(value, dict):
        raise OutcomeAnalysisS3R1R3Error(f"{label} must be a JSON object")
    return value


def _all_false_flags() -> dict[str, bool]:
    return {flag: False for flag in ACCESS_FLAGS}


def _require_exact(value: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    if dict(value) != dict(expected):
        raise OutcomeAnalysisS3R1R3Error(f"{label} does not match a fresh immutable rebuild")


def _assert_hash(value: Mapping[str, Any], hash_key: str, expected_hash: str, label: str) -> None:
    if value.get(hash_key) != expected_hash or _canonical_hash(_without_hash(value, hash_key)) != expected_hash:
        raise OutcomeAnalysisS3R1R3Error(f"Historical R2 {label} no longer has its accepted hash")


def _historical_r2_components(root: Path) -> dict[str, dict[str, Any]]:
    paths = {
        "protocolEvidence": root / r2.DEFAULT_PROTOCOL_EVIDENCE_PATH.relative_to(r2.PROJECT_ROOT),
        "sourceLock": root / r2.DEFAULT_SOURCE_LOCK_PATH.relative_to(r2.PROJECT_ROOT),
        "partitionPlan": root / r2.DEFAULT_PARTITION_PLAN_PATH.relative_to(r2.PROJECT_ROOT),
        "acquisition": root / r2.DEFAULT_ACQUISITION_PATH.relative_to(r2.PROJECT_ROOT),
        "preregistration": root / r2.DEFAULT_PREREGISTRATION_PATH.relative_to(r2.PROJECT_ROOT),
        "population": root / r2.DEFAULT_PRIMARY_POPULATION_PATH.relative_to(r2.PROJECT_ROOT),
        "clusters": root / r2.DEFAULT_OVERLAP_CLUSTERS_PATH.relative_to(r2.PROJECT_ROOT),
        "invariance": root / r2.DEFAULT_INVARIANCE_PATH.relative_to(r2.PROJECT_ROOT),
        "core": root / r2.DEFAULT_CORE_PATH.relative_to(r2.PROJECT_ROOT),
        "acceptance": root / r2.DEFAULT_ACCEPTANCE_PATH.relative_to(r2.PROJECT_ROOT),
    }
    components = {name: _read_json(path, f"historical {name}") for name, path in paths.items()}
    expected = {
        "protocolEvidence": ("protocolEvidenceHash", HISTORICAL_R2_PROTOCOL_EVIDENCE_HASH),
        "sourceLock": ("protocolSourceLockHash", HISTORICAL_R2_SOURCE_LOCK_HASH),
        "partitionPlan": ("providerPartitionPlanHash", HISTORICAL_R2_PARTITION_PLAN_HASH),
        "acquisition": ("marketDataAcquisitionContractHash", HISTORICAL_R2_ACQUISITION_HASH),
        "preregistration": ("preregistrationHash", HISTORICAL_R2_PREREGISTRATION_HASH),
        "population": ("primaryPopulationHash", HISTORICAL_R2_POPULATION_HASH),
        "clusters": ("overlapClustersHash", HISTORICAL_R2_CLUSTERS_HASH),
        "invariance": ("analysisPlanInvarianceAuditHash", HISTORICAL_R2_INVARIANCE_HASH),
        "core": ("analysisCoreManifestHash", HISTORICAL_R2_CORE_HASH),
        "acceptance": ("acceptanceManifestHash", HISTORICAL_R2_ACCEPTANCE_HASH),
    }
    for name, value in components.items():
        hash_key, expected_hash = expected[name]
        _assert_hash(value, hash_key, expected_hash, name)
    return components


def _require_r2_predecessor(root: Path) -> dict[str, dict[str, Any]]:
    r2.validate_s3r1_r2_artifacts(root)
    historical = _historical_r2_components(root)
    if historical["core"].get("upstreamHashes") != EXPECTED_UPSTREAM_HASHES:
        raise OutcomeAnalysisS3R1R3Error("S2R1-R1 upstream hashes changed")
    return historical


def _source_record(
    source_id: str,
    *,
    url: str,
    title: str,
    authority: str,
    locator: str,
    facts: list[str],
    role: str,
) -> dict[str, Any]:
    return {
        "sourceId": source_id,
        "url": url,
        "title": title,
        "sourceAuthority": authority,
        "retrievedAtUtc": S3R1_R3_AUTHORED_AT_UTC,
        "locator": locator,
        "factsSupported": facts,
        "role": role,
    }


def build_lzma_framing_adjudication() -> dict[str, Any]:
    """Record direct documentation facts and the bounded cross-source deduction."""

    sources = [
        _source_record(
            "DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_ES",
            url=DUKASCOPY_ES_EXPORT_URL,
            title="Datos historicos de precios",
            authority="OFFICIAL_DUKASCOPY_CURRENT_TECHNICAL_DOCUMENTATION",
            locator="current page lines 577-650; compression at 582; Python decoder at 613-646",
            facts=["DUKASCOPY_EXCLUDES_XZ", "DUKASCOPY_SAMPLE_USES_DEFAULT_LZMA_DECOMPRESS"],
            role="CONTROLLING_PROVIDER_DOCUMENTATION",
        ),
        _source_record(
            "DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_FR",
            url=DUKASCOPY_FR_EXPORT_URL,
            title="Donnees historiques de prix",
            authority="OFFICIAL_DUKASCOPY_CURRENT_TECHNICAL_DOCUMENTATION",
            locator="current page corresponding daily BI5 decoding section and Python sample",
            facts=["CROSS_LANGUAGE_CORROBORATION_OF_DAILY_BI5_DECODER"],
            role="SAME_PUBLISHER_CORROBORATION_NOT_INDEPENDENT_AUTHORITY",
        ),
        _source_record(
            "PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE",
            url=PYTHON_LZMA_URL,
            title=PYTHON_DOCS_VERSION + " lzma",
            authority="OFFICIAL_PYTHON_RUNTIME_DOCUMENTATION",
            locator="L109-118, L159-165, L226-245",
            facts=[
                "PYTHON_DEFAULT_EQUALS_FORMAT_AUTO",
                "PYTHON_FORMAT_AUTO_ACCEPTS_XZ",
                "PYTHON_FORMAT_AUTO_ACCEPTS_FORMAT_ALONE",
                "PYTHON_FORMAT_AUTO_REJECTS_FORMAT_RAW",
                "PYTHON_FORMAT_RAW_REQUIRES_EXPLICIT_FILTER_CHAIN",
                "PYTHON_FORMAT_ALONE_IS_LEGACY_LZMA_CONTAINER",
            ],
            role="CONTROLLING_RUNTIME_SEMANTICS",
        ),
        _source_record(
            "LIBLZMA_XZ_CONTAINER_REFERENCE",
            url=LIBLZMA_CONTAINER_URL,
            title="liblzma container.h File Reference",
            authority="OFFICIAL_LIBLZMA_PROJECT_DOCUMENTATION",
            locator="container format API reference; consulted as terminology corroboration",
            facts=["CONTAINER_TERMINOLOGY_CORROBORATION"],
            role="CORROBORATIVE_ONLY",
        ),
    ]
    matrix = [
        {
            "factId": "DUKASCOPY_EXCLUDES_XZ",
            "sourceId": sources[0]["sourceId"],
            "sourceAuthority": sources[0]["sourceAuthority"],
            "locator": "L582",
            "evidence": "Direct provider prose calls the payload an LZMA stream and explicitly says it is not the .xz container format.",
            "evidenceKind": "DIRECT_SOURCE_FACT",
            "status": "SUPPORTED",
        },
        {
            "factId": "DUKASCOPY_SAMPLE_USES_DEFAULT_LZMA_DECOMPRESS",
            "sourceId": sources[0]["sourceId"],
            "sourceAuthority": sources[0]["sourceAuthority"],
            "locator": "L613-646, especially L629",
            "evidence": "The documented daily BI5 Python decoder reads compressed bytes and calls lzma.decompress(compressed) without format or filters.",
            "evidenceKind": "DIRECT_SOURCE_FACT",
            "status": "SUPPORTED",
        },
        {
            "factId": "PYTHON_DEFAULT_EQUALS_FORMAT_AUTO",
            "sourceId": sources[2]["sourceId"],
            "sourceAuthority": sources[2]["sourceAuthority"],
            "locator": "L159-165",
            "evidence": "The official function signature gives lzma.decompress(data, format=FORMAT_AUTO, memlimit=None, filters=None).",
            "evidenceKind": "DIRECT_SOURCE_FACT",
            "status": "SUPPORTED",
        },
        {
            "factId": "PYTHON_FORMAT_AUTO_ACCEPTS_XZ",
            "sourceId": sources[2]["sourceId"],
            "sourceAuthority": sources[2]["sourceAuthority"],
            "locator": "L241-245",
            "evidence": "FORMAT_AUTO detects the container and decompresses .xz and .lzma files.",
            "evidenceKind": "DIRECT_SOURCE_FACT",
            "status": "SUPPORTED",
        },
        {
            "factId": "PYTHON_FORMAT_AUTO_ACCEPTS_FORMAT_ALONE",
            "sourceId": sources[2]["sourceId"],
            "sourceAuthority": sources[2]["sourceAuthority"],
            "locator": "L233-245",
            "evidence": "Python defines FORMAT_ALONE as the legacy .lzma container and says FORMAT_AUTO decompresses .lzma files.",
            "evidenceKind": "CROSS_REFERENCE_WITHIN_OFFICIAL_RUNTIME_DOCUMENTATION",
            "status": "SUPPORTED",
        },
        {
            "factId": "PYTHON_FORMAT_AUTO_REJECTS_FORMAT_RAW",
            "sourceId": sources[2]["sourceId"],
            "sourceAuthority": sources[2]["sourceAuthority"],
            "locator": "L238-245",
            "evidence": "Python states data in FORMAT_RAW cannot be decompressed using FORMAT_AUTO.",
            "evidenceKind": "DIRECT_SOURCE_FACT",
            "status": "SUPPORTED",
        },
        {
            "factId": "PYTHON_FORMAT_RAW_REQUIRES_EXPLICIT_FILTER_CHAIN",
            "sourceId": sources[2]["sourceId"],
            "sourceAuthority": sources[2]["sourceAuthority"],
            "locator": "L117-118 and L238-239",
            "evidence": "Python requires a custom filter chain when the raw format is used for decompression.",
            "evidenceKind": "DIRECT_SOURCE_FACT",
            "status": "SUPPORTED",
        },
        {
            "factId": "PYTHON_FORMAT_ALONE_IS_LEGACY_LZMA_CONTAINER",
            "sourceId": sources[2]["sourceId"],
            "sourceAuthority": sources[2]["sourceAuthority"],
            "locator": "L233-236",
            "evidence": "Python names FORMAT_ALONE as the legacy .lzma container format.",
            "evidenceKind": "DIRECT_SOURCE_FACT",
            "status": "SUPPORTED",
        },
    ]
    candidates = [
        {
            "format": "FORMAT_XZ",
            "compatibleWithDukascopyProse": False,
            "compatibleWithOfficialPythonSample": True,
            "compatibleWithPythonRuntimeSpecification": True,
            "requiresUnknownParameters": False,
            "finalDisposition": "ELIMINATED",
            "reason": "Direct Dukascopy wording excludes the .xz container.",
        },
        {
            "format": "FORMAT_ALONE",
            "compatibleWithDukascopyProse": True,
            "compatibleWithOfficialPythonSample": True,
            "compatibleWithPythonRuntimeSpecification": True,
            "requiresUnknownParameters": False,
            "finalDisposition": "SELECTED_BY_CROSS_SOURCE_TECHNICAL_DEDUCTION",
            "reason": "After direct exclusion of XZ and documented incompatibility of RAW with the sample's default call, legacy .lzma is the only FORMAT_AUTO-compatible format remaining.",
        },
        {
            "format": "FORMAT_RAW",
            "compatibleWithDukascopyProse": "NATURAL_LANGUAGE_RAW_IS_NOT_A_PYTHON_API_ASSERTION",
            "compatibleWithOfficialPythonSample": False,
            "compatibleWithPythonRuntimeSpecification": False,
            "requiresUnknownParameters": True,
            "finalDisposition": "ELIMINATED",
            "reason": "FORMAT_RAW requires a filter chain and cannot be decoded by the documented default FORMAT_AUTO call; no source supplies a filter chain.",
        },
    ]
    body = {
        "contract": S3R1_R3_ADJUDICATION_CONTRACT,
        "schemaVersion": S3R1_R3_SCHEMA_VERSION,
        "milestone": S3R1_R3_MILESTONE,
        "supersedesProtocolEvidenceHash": HISTORICAL_R2_PROTOCOL_EVIDENCE_HASH,
        "question": "Which exact Python LZMA framing must decode the selected daily BI5 product without fallback or provider-byte probing?",
        "sourceRecords": sources,
        "premiseMatrix": matrix,
        "terminologyDistinction": {
            "naturalLanguage": "Dukascopy's natural-language raw LZMA wording means LZMA bytes outside the XZ container in this adjudication record.",
            "pythonApi": "Python FORMAT_RAW is a separate API format requiring an explicit filter chain and is not inferred from the natural-language phrase.",
            "status": "DISTINGUISHED_NOT_EQUIVALENT",
        },
        "candidateFormats": candidates,
        "eliminatedFormats": ["FORMAT_XZ", "FORMAT_RAW"],
        "selectedFormat": "PYTHON_LZMA_FORMAT_ALONE",
        "selectedPythonConstant": "lzma.FORMAT_ALONE",
        "filterChainRequired": False,
        "filterChain": [],
        "adjudicationStatus": "COMPRESSION_FRAMING_SOURCE_ADJUDICATED",
        "decisionKind": "CROSS_SOURCE_TECHNICAL_DEDUCTION",
        "uniqueConclusionReason": "The provider excludes XZ; Python excludes RAW from the documented default call; the remaining default-compatible legacy .lzma container is FORMAT_ALONE.",
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
    }
    return {**body, "lzmaFramingAdjudicationHash": _canonical_hash(body)}


def parser_source_sha256(parser_source_path: Path = PARSER_SOURCE_PATH) -> str:
    return hashlib.sha256(Path(parser_source_path).read_bytes()).hexdigest().upper()


def build_parser_contract(adjudication: Mapping[str, Any] | None = None) -> dict[str, Any]:
    expected_adjudication = build_lzma_framing_adjudication()
    if adjudication is not None:
        _require_exact(adjudication, expected_adjudication, "lzma framing adjudication")
    source_hash = parser_source_sha256()
    body = {
        "contract": S3R1_R3_PARSER_CONTRACT,
        "schemaVersion": S3R1_R3_SCHEMA_VERSION,
        "milestone": S3R1_R3_MILESTONE,
        "product": r2.PROVIDER_PRODUCT,
        "instrument": parser.USDJPY_SYMBOL,
        "compression": {
            "framing": parser.COMPRESSION_FRAMING,
            "pythonConstant": "lzma.FORMAT_ALONE",
            "productionCall": "lzma.decompress(raw_bytes, format=lzma.FORMAT_ALONE)",
            "fallbackFormatsAllowed": False,
            "sourceHash": expected_adjudication["lzmaFramingAdjudicationHash"],
        },
        "recordLayout": {
            "recordSizeBytes": parser.RECORD_SIZE_BYTES,
            "structFormat": parser.RECORD_STRUCT_FORMAT,
            "byteOrder": "BIG_ENDIAN",
            "fields": ["millisecondsFromUtcDayStart", "askNative", "bidNative", "askVolumeFloat32", "bidVolumeFloat32"],
            "alignmentPolicy": "RAW_RECORD_ALIGNMENT_INVALID",
        },
        "timestampRule": {
            "nativeType": "uint32",
            "unit": "milliseconds",
            "base": "UTC_NATIVE_PARTITION_DAY_START",
            "formula": "timestampUtc = nativeStartUtc + timedelta(milliseconds=millisecondsFromUtcDayStart)",
            "validRange": "0 <= millisecondsFromUtcDayStart < 86400000",
            "invalidStatus": "NATIVE_TIMESTAMP_OUT_OF_PARTITION",
        },
        "priceRule": {
            "symbol": parser.USDJPY_SYMBOL,
            "scaleDenominator": parser.USDJPY_SCALE_DENOMINATOR,
            "formula": "bid = bidNative / 1000; ask = askNative / 1000",
            "validity": "bidNative > 0 and askNative > 0 and askNative >= bidNative",
            "invalidStatus": "NATIVE_QUOTE_INVALID",
        },
        "volumeHandling": {
            "decoded": "IEEE_754_FLOAT32",
            "rawBitPreservation": "UPPERCASE_HEX_OF_THE_FOUR_NATIVE_VOLUME_BYTES",
            "useForFurtherAnalysis": "NOT_USED_BY_THIS_PARSER",
        },
        "recordOrder": "PRESERVE_NATIVE_RECORD_INDEX_AND_ORDER_NO_DEDUPLICATION",
        "canonicalSerialization": {
            "representation": parser.CANONICAL_SERIALIZATION,
            "fields": ["partitionId", "recordIndex", "timestampUtc", "askNative", "bidNative", "askVolumeBitsHex", "bidVolumeBitsHex"],
            "timestampFormat": "YYYY-MM-DDTHH:MM:SS.mmmZ",
            "parsedTicksSha256": "SHA256_OF_CANONICAL_UTF8_JSON_LINES",
        },
        "syntheticFixtureMethodology": {
            "designation": "SYNTHETIC_NOT_PROVIDER_DATA",
            "storage": "IN_MEMORY_TEST_GENERATION_ONLY",
            "partitionDate": "2030-01-01",
            "scenarioIds": [
                "VALID_SINGLE_RECORD",
                "VALID_MULTI_RECORD_BOUNDARY_OFFSETS",
                "WRONG_ALTERNATE_CONTAINER",
                "CORRUPTED_COMPRESSED_STREAM",
                "ZERO_RAW_PAYLOAD",
                "ZERO_DECODED_RECORDS",
                "NINETEEN_BYTE_DECODED_PAYLOAD",
                "TRAILING_BYTE_DECODED_PAYLOAD",
                "OUT_OF_PARTITION_MILLISECOND_OFFSET",
                "ASK_BELOW_BID",
                "ZERO_BID",
                "EQUAL_ASK_BID",
                "UNSUPPORTED_SYMBOL",
                "INVALID_PARTITION_DATE",
            ],
        },
        "errorStatuses": [
            "UNSUPPORTED_SYMBOL",
            "INVALID_PARTITION_DATE",
            "INVALID_RAW_BYTES",
            "ZERO_BYTE_PAYLOAD_ACQUISITION_INCOMPLETE",
            "COMPRESSION_FORMAT_MISMATCH",
            "COMPRESSION_DECODE_FAILED",
            "ZERO_DECODED_RECORDS_ACQUISITION_INCOMPLETE",
            "RAW_RECORD_ALIGNMENT_INVALID",
            "NATIVE_TIMESTAMP_OUT_OF_PARTITION",
            "NATIVE_QUOTE_INVALID",
        ],
        "networkAccess": False,
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
        "sourceFactCoverage": {
            "compressionFraming": "DUKASCOPY_EXCLUDES_XZ + DUKASCOPY_SAMPLE_USES_DEFAULT_LZMA_DECOMPRESS + PYTHON_FORMAT_AUTO_REJECTS_FORMAT_RAW",
            "recordSizeAndEndian": "R2_RECORD_LAYOUT",
            "timestampBaseAndUnit": "R2_TIMESTAMP_RECONSTRUCTION",
            "usdJpyDivisor": "R2_USDJPY_SCALE",
        },
        "parserSourceSha256": source_hash,
    }
    return {**body, "parserContractHash": _canonical_hash(body)}


def build_source_lock(adjudication: Mapping[str, Any] | None = None) -> dict[str, Any]:
    expected_adjudication = build_lzma_framing_adjudication()
    if adjudication is not None:
        _require_exact(adjudication, expected_adjudication, "lzma framing adjudication")
    body = {
        "contract": S3R1_R3_SOURCE_LOCK_CONTRACT,
        "schemaVersion": S3R1_R3_SCHEMA_VERSION,
        "milestone": S3R1_R3_MILESTONE,
        "supersedesProtocolSourceLockHash": HISTORICAL_R2_SOURCE_LOCK_HASH,
        "lzmaFramingAdjudicationHash": expected_adjudication["lzmaFramingAdjudicationHash"],
        "sources": expected_adjudication["sourceRecords"],
        "factsSupported": [item["factId"] for item in expected_adjudication["premiseMatrix"]],
        "adjudicationStatus": expected_adjudication["adjudicationStatus"],
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
    }
    return {**body, "protocolSourceLockHash": _canonical_hash(body)}


def build_market_data_acquisition_contract(
    resource_root: Path = PROJECT_ROOT,
    *,
    adjudication: Mapping[str, Any] | None = None,
    source_lock: Mapping[str, Any] | None = None,
    parser_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    _require_r2_predecessor(root)
    expected_adjudication = build_lzma_framing_adjudication()
    expected_lock = build_source_lock(expected_adjudication)
    expected_parser = build_parser_contract(expected_adjudication)
    if adjudication is not None:
        _require_exact(adjudication, expected_adjudication, "lzma framing adjudication")
    if source_lock is not None:
        _require_exact(source_lock, expected_lock, "R3 protocol source lock")
    if parser_contract is not None:
        _require_exact(parser_contract, expected_parser, "parser contract")
    body = copy.deepcopy(r2.build_market_data_acquisition_contract(root))
    body.pop("marketDataAcquisitionContractHash", None)
    body.update(
        {
            "contract": S3R1_R3_ACQUISITION_CONTRACT,
            "schemaVersion": S3R1_R3_SCHEMA_VERSION,
            "milestone": S3R1_R3_MILESTONE,
            "status": "PRE_REQUEST_ACQUISITION_PROTOCOL_FULLY_FROZEN_PROVIDER_NOT_ACCESSED",
            "supersedesContract": r2.S3R1_R2_ACQUISITION_CONTRACT,
            "supersedesHash": HISTORICAL_R2_ACQUISITION_HASH,
            "protocolSourceLockHash": expected_lock["protocolSourceLockHash"],
            "lzmaFramingAdjudicationHash": expected_adjudication["lzmaFramingAdjudicationHash"],
            "compression": {
                "status": "COMPRESSION_FRAMING_SOURCE_ADJUDICATED",
                "compressionFraming": parser.COMPRESSION_FRAMING,
                "pythonConstant": "lzma.FORMAT_ALONE",
                "filterChainRequired": False,
                "filterChain": [],
                "parserUseAuthorized": True,
            },
            "parser": {
                "status": "OFFLINE_SOURCE_BOUND_PARSER_FROZEN",
                "module": "gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3.py",
                "parserContractHash": expected_parser["parserContractHash"],
                "parserSourceSha256": expected_parser["parserSourceSha256"],
                "offlineOnlyWhenAuthorized": True,
                "networkAccess": False,
                "productFormat": parser.COMPRESSION_FRAMING,
            },
            "providerProtocolFullyClosed": True,
            "providerAccessPerformed": False,
            "marketOutcomeRead": False,
            "outcomeUnlockAllowed": False,
        }
    )
    if body["nativePartitioning"]["uniqueProviderPartitionCount"] != 15 or body["frozenIntervalSet"]["totalCount"] != 39:
        raise OutcomeAnalysisS3R1R3Error("R3 must preserve the R2 39-window/15-partition plan")
    return {**body, "marketDataAcquisitionContractHash": _canonical_hash(body)}


def build_s3r1_r3_preregistration(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    _require_r2_predecessor(root)
    adjudication = build_lzma_framing_adjudication()
    parser_contract = build_parser_contract(adjudication)
    source_lock = build_source_lock(adjudication)
    acquisition = build_market_data_acquisition_contract(
        root, adjudication=adjudication, source_lock=source_lock, parser_contract=parser_contract
    )
    body = copy.deepcopy(r2.build_s3r1_r2_preregistration(root))
    body.pop("preregistrationHash", None)
    body.update(
        {
            "contract": S3R1_R3_PREREGISTRATION_CONTRACT,
            "schemaVersion": S3R1_R3_SCHEMA_VERSION,
            "milestone": S3R1_R3_MILESTONE,
            "startingMaster": S3R1_R3_EXPECTED_STARTING_MASTER,
            "preregistrationAuthoredAtUtc": S3R1_R3_AUTHORED_AT_UTC,
            "status": "S3R1_R3_DUKASCOPY_LZMA_AND_PARSER_FREEZE_COMPLETE_TARGETED_ASTRA_REAUDIT_REQUIRED",
            "nextGate": "INDEPENDENT_CENTRAL_REVIEW_BEFORE_TARGETED_ASTRA_PRE_OUTCOME_REAUDIT",
            "supersedesPreregistrationContract": r2.S3R1_R2_PREREGISTRATION_CONTRACT,
            "supersedesPreregistrationHash": HISTORICAL_R2_PREREGISTRATION_HASH,
            "providerProtocolClosureReason": "LZMA_FORMAT_ALONE_UNIQUELY_ADJUDICATED_BY_DUKASCOPY_AND_PYTHON_DOCUMENTATION",
            "lzmaFramingAdjudicationHash": adjudication["lzmaFramingAdjudicationHash"],
            "parserContractHash": parser_contract["parserContractHash"],
            "parserSourceSha256": parser_contract["parserSourceSha256"],
            "marketDataAcquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
            "protocolSourceLockHash": source_lock["protocolSourceLockHash"],
            "providerPartitionPlanHash": HISTORICAL_R2_PARTITION_PLAN_HASH,
            "scientificDesignChanged": False,
        }
    )
    return {**body, "preregistrationHash": _canonical_hash(body)}


def build_s3r1_r3_schema(preregistration: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = copy.deepcopy(preregistration) if preregistration is not None else build_s3r1_r3_preregistration(PROJECT_ROOT)
    schema = r2.build_s3r1_r2_schema(payload)
    schema["title"] = "MO-R4A-S3R1-R3 frozen pre-request acquisition preregistration"
    return schema


def _successor_from_r2(
    value: Mapping[str, Any],
    *,
    contract: str,
    milestone: str,
    hash_key: str,
    supersedes_contract_key: str,
    supersedes_hash_key: str,
    predecessor_hash: str,
    updates: Mapping[str, Any],
) -> dict[str, Any]:
    body = copy.deepcopy(value)
    body.pop(hash_key, None)
    body.update(
        {
            "contract": contract,
            "schemaVersion": S3R1_R3_SCHEMA_VERSION,
            "milestone": milestone,
            supersedes_contract_key: value["contract"],
            supersedes_hash_key: predecessor_hash,
            **copy.deepcopy(dict(updates)),
        }
    )
    return {**body, hash_key: _canonical_hash(body)}


def build_s3r1_r3_primary_population(resource_root: Path = PROJECT_ROOT, *, preregistration: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    expected_preregistration = build_s3r1_r3_preregistration(root)
    if preregistration is not None:
        _require_exact(preregistration, expected_preregistration, "R3 preregistration")
    base = r2.build_s3r1_r2_primary_population(root)
    return _successor_from_r2(
        base,
        contract=S3R1_R3_PRIMARY_POPULATION_CONTRACT,
        milestone=S3R1_R3_MILESTONE,
        hash_key="primaryPopulationHash",
        supersedes_contract_key="supersedesPrimaryPopulationContract",
        supersedes_hash_key="supersedesPrimaryPopulationHash",
        predecessor_hash=HISTORICAL_R2_POPULATION_HASH,
        updates={
            "preregistrationHash": expected_preregistration["preregistrationHash"],
            "scientificRowsUnchanged": True,
            "protocolClosureDoesNotChangePopulation": True,
        },
    )


def build_s3r1_r3_overlap_clusters(resource_root: Path = PROJECT_ROOT, *, population: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    expected_population = build_s3r1_r3_primary_population(root)
    if population is not None:
        _require_exact(population, expected_population, "R3 primary population")
    base = r2.build_s3r1_r2_overlap_clusters(root)
    return _successor_from_r2(
        base,
        contract=S3R1_R3_OVERLAP_CLUSTERS_CONTRACT,
        milestone=S3R1_R3_MILESTONE,
        hash_key="overlapClustersHash",
        supersedes_contract_key="supersedesOverlapClustersContract",
        supersedes_hash_key="supersedesOverlapClustersHash",
        predecessor_hash=HISTORICAL_R2_CLUSTERS_HASH,
        updates={
            "primaryPopulationHash": expected_population["primaryPopulationHash"],
            "scientificClustersUnchanged": True,
            "protocolClosureDoesNotChangeClusters": True,
        },
    )


def build_s3r1_r3_invariance_audit(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    expected_preregistration = build_s3r1_r3_preregistration(root)
    expected_population = build_s3r1_r3_primary_population(root, preregistration=expected_preregistration)
    expected_clusters = build_s3r1_r3_overlap_clusters(root, population=expected_population)
    if preregistration is not None:
        _require_exact(preregistration, expected_preregistration, "R3 preregistration")
    if population is not None:
        _require_exact(population, expected_population, "R3 primary population")
    if clusters is not None:
        _require_exact(clusters, expected_clusters, "R3 overlap clusters")
    base = r2.build_s3r1_r2_invariance_audit(root)
    base.pop("parserNotImplementedWhileConflictOpen", None)
    return _successor_from_r2(
        base,
        contract=S3R1_R3_INVARIANCE_CONTRACT,
        milestone=S3R1_R3_MILESTONE,
        hash_key="analysisPlanInvarianceAuditHash",
        supersedes_contract_key="supersedesInvarianceAuditContract",
        supersedes_hash_key="supersedesInvarianceAuditHash",
        predecessor_hash=HISTORICAL_R2_INVARIANCE_HASH,
        updates={
            "preregistrationHash": expected_preregistration["preregistrationHash"],
            "primaryPopulationHash": expected_population["primaryPopulationHash"],
            "overlapClustersHash": expected_clusters["overlapClustersHash"],
            "providerProtocolDoesNotChangeScientificDesign": True,
            "offlineParserSourceBound": True,
            "syntheticFixtureOnly": True,
        },
    )


def compute_analysis_core_manifest_hash(value: Mapping[str, Any]) -> str:
    return _canonical_hash(_without_hash(value, "analysisCoreManifestHash"))


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
        "contract": S3R1_R3_CORE_CONTRACT,
        "schemaVersion": S3R1_R3_SCHEMA_VERSION,
        "milestone": S3R1_R3_MILESTONE,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": preregistration["preregistrationHash"],
        "primaryPopulationHash": population["primaryPopulationHash"],
        "overlapClustersHash": clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
        "protocolSourceLockHash": source_lock["protocolSourceLockHash"],
        "providerPartitionPlanHash": HISTORICAL_R2_PARTITION_PLAN_HASH,
        "lzmaFramingAdjudicationHash": adjudication["lzmaFramingAdjudicationHash"],
        "parserContractHash": parser_contract["parserContractHash"],
        "parserSourceSha256": parser_contract["parserSourceSha256"],
    }
    return {**body, "analysisCoreManifestHash": _canonical_hash(body)}


def build_s3r1_r3_acceptance_manifest(
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
    expected_adjudication = build_lzma_framing_adjudication()
    expected_lock = build_source_lock(expected_adjudication)
    expected_parser = build_parser_contract(expected_adjudication)
    expected_acquisition = build_market_data_acquisition_contract(
        root, adjudication=expected_adjudication, source_lock=expected_lock, parser_contract=expected_parser
    )
    expected_preregistration = build_s3r1_r3_preregistration(root)
    expected_population = build_s3r1_r3_primary_population(root, preregistration=expected_preregistration)
    expected_clusters = build_s3r1_r3_overlap_clusters(root, population=expected_population)
    expected_invariance = build_s3r1_r3_invariance_audit(
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
        "lzma framing adjudication": (adjudication, expected_adjudication),
        "R3 source lock": (source_lock, expected_lock),
        "parser contract": (parser_contract, expected_parser),
        "R3 acquisition": (acquisition, expected_acquisition),
        "R3 preregistration": (preregistration, expected_preregistration),
        "R3 population": (population, expected_population),
        "R3 clusters": (clusters, expected_clusters),
        "R3 invariance": (invariance, expected_invariance),
        "R3 core": (core, expected_core),
    }
    for label, (provided, expected) in supplied.items():
        if provided is not None:
            _require_exact(provided, expected, label)
    body = {
        "contract": S3R1_R3_ACCEPTANCE_CONTRACT,
        "schemaVersion": S3R1_R3_SCHEMA_VERSION,
        "milestone": S3R1_R3_MILESTONE,
        "status": "S3R1_R3_DUKASCOPY_LZMA_AND_PARSER_FREEZE_COMPLETE_TARGETED_ASTRA_REAUDIT_REQUIRED",
        "branch": "BRANCH_A_PROTOCOL_FULLY_CLOSED",
        "nextGate": "INDEPENDENT_CENTRAL_REVIEW_BEFORE_TARGETED_ASTRA_PRE_OUTCOME_REAUDIT",
        "startingMaster": S3R1_R3_EXPECTED_STARTING_MASTER,
        "supersedesAcceptanceManifestContract": r2.S3R1_R2_ACCEPTANCE_CONTRACT,
        "supersedesAcceptanceManifestHash": HISTORICAL_R2_ACCEPTANCE_HASH,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": expected_preregistration["preregistrationHash"],
        "primaryPopulationHash": expected_population["primaryPopulationHash"],
        "overlapClustersHash": expected_clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": expected_invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": expected_acquisition["marketDataAcquisitionContractHash"],
        "protocolSourceLockHash": expected_lock["protocolSourceLockHash"],
        "providerPartitionPlanHash": HISTORICAL_R2_PARTITION_PLAN_HASH,
        "lzmaFramingAdjudicationHash": expected_adjudication["lzmaFramingAdjudicationHash"],
        "parserContractHash": expected_parser["parserContractHash"],
        "parserSourceSha256": expected_parser["parserSourceSha256"],
        "analysisCoreManifestHash": expected_core["analysisCoreManifestHash"],
        "activeBlockers": ["OUTCOME_UNLOCK_NOT_AUTHORIZED", "TARGETED_ASTRA_REAUDIT_NOT_PERFORMED"],
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


def _validate_parser_source() -> None:
    source = PARSER_SOURCE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    blocked = {"boto3", "botocore", "requests", "urllib", "httpx", "aiohttp", "socket", "ccxt", "yfinance"}
    imported: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    if imported & blocked:
        raise OutcomeAnalysisS3R1R3Error("Parser imports forbidden network-capable module(s)")
    if "lzma.FORMAT_ALONE" not in source:
        raise OutcomeAnalysisS3R1R3Error("Parser must use the explicit adjudicated format")
    if any(name in source for name in ("lzma.FORMAT_AUTO", "lzma.FORMAT_RAW", "lzma.FORMAT_XZ")):
        raise OutcomeAnalysisS3R1R3Error("Parser must not contain alternate production format paths")


def validate_s3r1_r3_artifacts(resource_root: Path = PROJECT_ROOT) -> None:
    root = Path(resource_root).resolve()
    _validate_parser_source()
    adjudication = build_lzma_framing_adjudication()
    source_lock = build_source_lock(adjudication)
    parser_contract = build_parser_contract(adjudication)
    acquisition = build_market_data_acquisition_contract(
        root, adjudication=adjudication, source_lock=source_lock, parser_contract=parser_contract
    )
    preregistration = build_s3r1_r3_preregistration(root)
    population = build_s3r1_r3_primary_population(root, preregistration=preregistration)
    clusters = build_s3r1_r3_overlap_clusters(root, population=population)
    invariance = build_s3r1_r3_invariance_audit(
        root, preregistration=preregistration, population=population, clusters=clusters
    )
    core = build_analysis_core_manifest(
        preregistration, population, clusters, invariance, acquisition, source_lock, adjudication, parser_contract
    )
    acceptance = build_s3r1_r3_acceptance_manifest(
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
    r1.validate_json_schema_instance(preregistration, build_s3r1_r3_schema(preregistration))
    if adjudication["adjudicationStatus"] != "COMPRESSION_FRAMING_SOURCE_ADJUDICATED":
        raise OutcomeAnalysisS3R1R3Error("R3 requires a unique supported compression conclusion")
    if parser_contract["parserSourceSha256"] != parser_source_sha256():
        raise OutcomeAnalysisS3R1R3Error("Parser source hash no longer matches the parser contract")
    if acquisition["parser"]["parserContractHash"] != parser_contract["parserContractHash"]:
        raise OutcomeAnalysisS3R1R3Error("Acquisition parser binding changed")
    if acceptance["outcomeUnlocked"] or any(acceptance["outcomeAccessFlags"].values()):
        raise OutcomeAnalysisS3R1R3Error("R3 must retain every outcome-access lock")


def write_s3r1_r3_artifacts(resource_root: Path = PROJECT_ROOT, *, outcome_source: object | None = None) -> dict[str, Path]:
    if outcome_source is not None:
        raise OutcomeAnalysisS3R1R3Error("R3 cannot accept a provider, market file, tick source, or outcome")
    root = Path(resource_root).resolve()
    adjudication = build_lzma_framing_adjudication()
    source_lock = build_source_lock(adjudication)
    parser_contract = build_parser_contract(adjudication)
    acquisition = build_market_data_acquisition_contract(
        root, adjudication=adjudication, source_lock=source_lock, parser_contract=parser_contract
    )
    preregistration = build_s3r1_r3_preregistration(root)
    schema = build_s3r1_r3_schema(preregistration)
    population = build_s3r1_r3_primary_population(root, preregistration=preregistration)
    clusters = build_s3r1_r3_overlap_clusters(root, population=population)
    invariance = build_s3r1_r3_invariance_audit(
        root, preregistration=preregistration, population=population, clusters=clusters
    )
    core = build_analysis_core_manifest(
        preregistration, population, clusters, invariance, acquisition, source_lock, adjudication, parser_contract
    )
    acceptance = build_s3r1_r3_acceptance_manifest(
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
    artifacts = {
        "adjudication": root / DEFAULT_ADJUDICATION_PATH.relative_to(PROJECT_ROOT),
        "sourceLock": root / DEFAULT_SOURCE_LOCK_PATH.relative_to(PROJECT_ROOT),
        "parserContract": root / DEFAULT_PARSER_CONTRACT_PATH.relative_to(PROJECT_ROOT),
        "acquisition": root / DEFAULT_ACQUISITION_PATH.relative_to(PROJECT_ROOT),
        "preregistration": root / DEFAULT_PREREGISTRATION_PATH.relative_to(PROJECT_ROOT),
        "schema": root / DEFAULT_SCHEMA_PATH.relative_to(PROJECT_ROOT),
        "population": root / DEFAULT_PRIMARY_POPULATION_PATH.relative_to(PROJECT_ROOT),
        "clusters": root / DEFAULT_OVERLAP_CLUSTERS_PATH.relative_to(PROJECT_ROOT),
        "invariance": root / DEFAULT_INVARIANCE_PATH.relative_to(PROJECT_ROOT),
        "core": root / DEFAULT_CORE_PATH.relative_to(PROJECT_ROOT),
        "acceptance": root / DEFAULT_ACCEPTANCE_PATH.relative_to(PROJECT_ROOT),
        "report": root / DEFAULT_REPORT_PATH.relative_to(PROJECT_ROOT),
    }
    values = {
        "adjudication": adjudication,
        "sourceLock": source_lock,
        "parserContract": parser_contract,
        "acquisition": acquisition,
        "preregistration": preregistration,
        "schema": schema,
        "population": population,
        "clusters": clusters,
        "invariance": invariance,
        "core": core,
        "acceptance": acceptance,
    }
    for name, value in values.items():
        _write_json(artifacts[name], value)
    artifacts["report"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["report"].write_text(
        render_report(adjudication, source_lock, parser_contract, acquisition, preregistration, population, core, acceptance),
        encoding="utf-8",
    )
    return artifacts


def render_report(
    adjudication: Mapping[str, Any],
    source_lock: Mapping[str, Any],
    parser_contract: Mapping[str, Any],
    acquisition: Mapping[str, Any],
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    core: Mapping[str, Any],
    acceptance: Mapping[str, Any],
) -> str:
    matrix_rows = "\n".join(
        f"| `{row['factId']}` | {row['sourceId']} | {row['locator']} | {row['evidence']} | {row['status']} |"
        for row in adjudication["premiseMatrix"]
    )
    candidate_rows = "\n".join(
        f"| `{row['format']}` | {row['compatibleWithDukascopyProse']} | {row['compatibleWithOfficialPythonSample']} | {row['compatibleWithPythonRuntimeSpecification']} | {row['finalDisposition']} |"
        for row in adjudication["candidateFormats"]
    )
    return "\n".join(
        [
            "# MO-R4A-S3R1-R3 Dukascopy LZMA Framing Adjudication",
            "",
            "## Result",
            "",
            "R2 correctly stopped before parsing. R3 resolves its one protocol blocker without provider access or market bytes. Dukascopy excludes the XZ container while its official daily decoder uses default `lzma.decompress(compressed)`. Python documents that default as `FORMAT_AUTO`, which accepts XZ and legacy `.lzma` but rejects `FORMAT_RAW`; raw mode also requires an explicit filter chain. The unique surviving framing is therefore `lzma.FORMAT_ALONE`. This is a cross-source technical deduction, not a direct claim that Dukascopy names Python's constant.",
            "",
            "## Source Matrix",
            "",
            "| Question | Source | Locator | Short evidence | Status |",
            "| --- | --- | --- | --- | --- |",
            matrix_rows,
            "",
            "## Candidate Formats",
            "",
            "| Format | Provider prose compatible | Official sample compatible | Python runtime compatible | Disposition |",
            "| --- | --- | --- | --- | --- |",
            candidate_rows,
            "",
            "The natural-language phrase `raw LZMA` is not equated with Python `FORMAT_RAW`. Python's API definition rules FORMAT_RAW out for the documented no-filter default call.",
            "",
            "## Offline Parser",
            "",
            f"The parser is `gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3.py`, source SHA-256 `{parser_contract['parserSourceSha256']}`, and accepts caller-supplied bytes only. Its single production call is `{parser_contract['compression']['productionCall']}`. It decodes `>IIIff` 20-byte records, preserves record order and volume byte identities, and hashes canonical UTF-8 JSON Lines with sorted keys and millisecond UTC timestamps. The `{len(parser_contract['syntheticFixtureMethodology']['scenarioIds'])}` documented fixtures are generated in memory from invented 2030 values and are `SYNTHETIC_NOT_PROVIDER_DATA`.",
            "",
            "## Frozen Lineage",
            "",
            f"R2 acquisition `{HISTORICAL_R2_ACQUISITION_HASH}` is historical and unchanged. R3 acquisition `{acquisition['marketDataAcquisitionContractHash']}`, source lock `{source_lock['protocolSourceLockHash']}`, adjudication `{adjudication['lzmaFramingAdjudicationHash']}`, parser contract `{parser_contract['parserContractHash']}`, preregistration `{preregistration['preregistrationHash']}`, population `{population['primaryPopulationHash']}`, core `{core['analysisCoreManifestHash']}`, and acceptance `{acceptance['acceptanceManifestHash']}` bind the successor without hash cycles.",
            "",
            "## Invariance And Firewall",
            "",
            "The 24 identities, 14 directional rows, 13 primary rows, 39 analytical windows, 15 native daily partitions, four clusters, and 40-state null remain unchanged. The exhaustive 8192 binary-vector and 2744 timing checks remain required by the focused suite. No provider object was requested, no market or outcome data was read, and every outcome-access flag remains false. R3 performs no scoring, product work, package build, or execution.",
            "",
            "## Next Gate",
            "",
            "`INDEPENDENT_CENTRAL_REVIEW_BEFORE_TARGETED_ASTRA_PRE_OUTCOME_REAUDIT`. The parser freeze alone does not unlock outcomes, provider access, S4, or execution.",
            "",
        ]
    )
