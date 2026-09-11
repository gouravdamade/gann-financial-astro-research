"""MO-R4A-S3R1-R2 provider-protocol evidence and pre-outcome successor.

This module intentionally contains no network client, decompressor, market-data
reader, outcome scorer, or S4 evaluator.  It freezes only the public-document
evidence, daily native-partition geometry, and the remaining parser blocker.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import outcome_analysis_s3 as s3
import outcome_analysis_s3r1_r1 as r1


S3R1_R2_MILESTONE = "MO-R4A-S3R1-R2"
S3R1_R2_SCHEMA_VERSION = 1
S3R1_R2_AUTHORED_AT_UTC = "2026-09-11T00:00:00Z"
S3R1_R2_EXPECTED_STARTING_MASTER = "55238d59884973e8530266f2bbd8151b4bf4c486"

S3R1_R2_PROTOCOL_EVIDENCE_CONTRACT = "MO_R4A_S3R1_R2_DUKASCOPY_HISTORICAL_TICK_PROTOCOL_EVIDENCE_V1"
S3R1_R2_SOURCE_LOCK_CONTRACT = "MO_R4A_S3R1_R2_DUKASCOPY_PROTOCOL_SOURCE_LOCK_V1"
S3R1_R2_PARTITION_PLAN_CONTRACT = "MO_R4A_S3R1_R2_PROVIDER_PARTITION_PLAN_V1"
S3R1_R2_ACQUISITION_CONTRACT = "MO_R4A_S3R1_R2_MARKET_DATA_ACQUISITION_CONTRACT_V1"
S3R1_R2_PREREGISTRATION_CONTRACT = "MO_R4A_S3R1_R2_OUTCOME_ANALYSIS_PREREGISTRATION_V1"
S3R1_R2_PRIMARY_POPULATION_CONTRACT = "MO_R4A_S3R1_R2_PRIMARY_ANALYSIS_POPULATION_V1"
S3R1_R2_OVERLAP_CLUSTERS_CONTRACT = "MO_R4A_S3R1_R2_OVERLAP_CLUSTERS_V1"
S3R1_R2_INVARIANCE_CONTRACT = "MO_R4A_S3R1_R2_ANALYSIS_PLAN_INVARIANCE_AUDIT_V1"
S3R1_R2_CORE_CONTRACT = "MO_R4A_S3R1_R2_FROZEN_ANALYSIS_PACKAGE_V1"
S3R1_R2_ACCEPTANCE_CONTRACT = "MO_R4A_S3R1_R2_OUTCOME_ANALYSIS_PREREGISTRATION_ACCEPTANCE_V1"

HISTORICAL_R1_PREREGISTRATION_HASH = "0C9EF14A7216C9BB62E834B865315D67B2603F076FF2BA28AFC32E92CDFC93E2"
HISTORICAL_R1_POPULATION_HASH = "462436AA5F2E57998EE7EA334195FE86D14396169806D8F08064C7BF1CFE567C"
HISTORICAL_R1_CLUSTERS_HASH = "18E34DEABBFA2D99620789347D02FD002C23F36B39D21ED1D9B44702020A308F"
HISTORICAL_R1_INVARIANCE_HASH = "EC40B7D5552A79CE5F8B8A2763686159F0232804A0D75991DDE27B8FB59310DA"
HISTORICAL_R1_ACQUISITION_HASH = "D2E78CECD9743A176E417ACD7A7EAD57EC21167B8708AF2043C9D016E0C2CD70"
HISTORICAL_R1_CORE_HASH = "DCE54CE6FACCEFCF773E3F900691ED2BBB705A1D085CD6B5852B41F1A4CEE7F2"
HISTORICAL_R1_ACCEPTANCE_HASH = "9FF8B14F1A6D48D65BC73069BA3D7EF341A4AC9EEE0783639AE87860CF04D2D7"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"

DEFAULT_PROTOCOL_EVIDENCE_PATH = MACHINE_INTERPRETATION_ROOT / "dukascopy_historical_tick_protocol_evidence_s3r1_r2_v1.json"
DEFAULT_SOURCE_LOCK_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r2_dukascopy_protocol_source_lock.json"
DEFAULT_PARTITION_PLAN_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r2_provider_partition_plan.json"
DEFAULT_ACQUISITION_PATH = MACHINE_INTERPRETATION_ROOT / "market_data_acquisition_contract_s3r1_r2_v1.json"
DEFAULT_PREREGISTRATION_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r2_v1.json"
DEFAULT_SCHEMA_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3r1_r2_v1.schema.json"
DEFAULT_PRIMARY_POPULATION_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r2_primary_analysis_population.json"
DEFAULT_OVERLAP_CLUSTERS_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r2_overlap_clusters.json"
DEFAULT_INVARIANCE_PATH = AUDIT_ROOT / "mo_r4a_s3r1_r2_analysis_plan_invariance_audit.json"
DEFAULT_CORE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r2_frozen_analysis_package.json"
DEFAULT_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3r1_r2_outcome_analysis_preregistration.json"
DEFAULT_REPORT_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S3R1_R2_DUKASCOPY_PROVIDER_PROTOCOL_CLOSURE.md"

OFFICIAL_EXPORT_URL = "https://www.dukascopy.com/wiki/es/development/data-export/"
OFFICIAL_JFOREX_TICKS_URL = "https://www.dukascopy.com/wiki/en/development/strategy-api/historical-data/history-ticks/"
PROVIDER_PRODUCT = "DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE"
BUCKET = "cfg-public-proper-wallaby"
REGION = "eu-west-1"
INSTRUMENT = "USDJPY"
ACCESS_FLAGS = tuple(r1.ACCESS_FLAGS)
EXPECTED_UPSTREAM_HASHES = copy.deepcopy(r1.EXPECTED_UPSTREAM_HASHES)


class OutcomeAnalysisS3R1R2Error(ValueError):
    """Raised when R2 would depart from its frozen predecessor or protocol lock."""


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
        raise OutcomeAnalysisS3R1R2Error(f"Unable to load {label}: {path}") from exc
    if not isinstance(value, dict):
        raise OutcomeAnalysisS3R1R2Error(f"{label} must be a JSON object")
    return value


def _all_false_flags() -> dict[str, bool]:
    return {flag: False for flag in ACCESS_FLAGS}


def _require_exact(value: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    if dict(value) != dict(expected):
        raise OutcomeAnalysisS3R1R2Error(f"{label} does not match a fresh immutable rebuild")


def _assert_component_hash(value: Mapping[str, Any], hash_key: str, expected_hash: str, label: str) -> None:
    if value.get(hash_key) != expected_hash or _canonical_hash(_without_hash(value, hash_key)) != expected_hash:
        raise OutcomeAnalysisS3R1R2Error(f"Historical {label} no longer has its accepted hash")


def _historical_r1_components(root: Path) -> dict[str, dict[str, Any]]:
    paths = {
        "acquisition": root / r1.DEFAULT_ACQUISITION_PATH.relative_to(r1.PROJECT_ROOT),
        "preregistration": root / r1.DEFAULT_PREREGISTRATION_PATH.relative_to(r1.PROJECT_ROOT),
        "population": root / r1.DEFAULT_PRIMARY_POPULATION_PATH.relative_to(r1.PROJECT_ROOT),
        "clusters": root / r1.DEFAULT_OVERLAP_CLUSTERS_PATH.relative_to(r1.PROJECT_ROOT),
        "invariance": root / r1.DEFAULT_INVARIANCE_PATH.relative_to(r1.PROJECT_ROOT),
        "core": root / r1.DEFAULT_CORE_MANIFEST_PATH.relative_to(r1.PROJECT_ROOT),
        "acceptance": root / r1.DEFAULT_ACCEPTANCE_PATH.relative_to(r1.PROJECT_ROOT),
    }
    components = {name: _read_json(path, f"historical S3R1-R1 {name}") for name, path in paths.items()}
    expected = {
        "acquisition": ("marketDataAcquisitionContractHash", HISTORICAL_R1_ACQUISITION_HASH),
        "preregistration": ("preregistrationHash", HISTORICAL_R1_PREREGISTRATION_HASH),
        "population": ("primaryPopulationHash", HISTORICAL_R1_POPULATION_HASH),
        "clusters": ("overlapClustersHash", HISTORICAL_R1_CLUSTERS_HASH),
        "invariance": ("analysisPlanInvarianceAuditHash", HISTORICAL_R1_INVARIANCE_HASH),
        "core": ("analysisCoreManifestHash", HISTORICAL_R1_CORE_HASH),
        "acceptance": ("acceptanceManifestHash", HISTORICAL_R1_ACCEPTANCE_HASH),
    }
    for name, value in components.items():
        hash_key, expected_hash = expected[name]
        _assert_component_hash(value, hash_key, expected_hash, name)
    return components


@lru_cache(maxsize=None)
def _assert_r1_predecessor_cached(root_text: str) -> dict[str, dict[str, Any]]:
    root = Path(root_text)
    historical = _historical_r1_components(root)
    rebuilt_acquisition = r1.build_market_data_acquisition_contract(root)
    rebuilt_prereg = r1.build_s3r1_r1_preregistration(root)
    rebuilt_population = r1.build_s3r1_r1_primary_population(root)
    rebuilt_clusters = r1.build_s3r1_r1_overlap_clusters(root, population=rebuilt_population)
    rebuilt_invariance = r1.build_s3r1_r1_invariance_audit(
        root,
        preregistration=rebuilt_prereg,
        population=rebuilt_population,
        clusters=rebuilt_clusters,
    )
    rebuilt_core = r1.build_analysis_core_manifest(
        rebuilt_prereg, rebuilt_population, rebuilt_clusters, rebuilt_invariance, rebuilt_acquisition
    )
    rebuilt_acceptance = r1.build_s3r1_r1_acceptance_manifest(
        root,
        acquisition_contract=rebuilt_acquisition,
        preregistration=rebuilt_prereg,
        population=rebuilt_population,
        clusters=rebuilt_clusters,
        invariance=rebuilt_invariance,
        core=rebuilt_core,
    )
    rebuilt = {
        "acquisition": rebuilt_acquisition,
        "preregistration": rebuilt_prereg,
        "population": rebuilt_population,
        "clusters": rebuilt_clusters,
        "invariance": rebuilt_invariance,
        "core": rebuilt_core,
        "acceptance": rebuilt_acceptance,
    }
    for name, value in rebuilt.items():
        if historical[name] != value:
            raise OutcomeAnalysisS3R1R2Error(f"Historical S3R1-R1 {name} differs from its immutable builder")
    if historical["core"].get("upstreamHashes") != EXPECTED_UPSTREAM_HASHES:
        raise OutcomeAnalysisS3R1R2Error("S2R1-R1 upstream hashes changed")
    return historical


def _assert_r1_predecessor(root: Path) -> dict[str, dict[str, Any]]:
    """Verify R1 once per resource root, then return an isolated copy."""

    return copy.deepcopy(_assert_r1_predecessor_cached(str(root.resolve())))


def _protocol_fact(
    fact_id: str,
    fact: str,
    *,
    status: str,
    source_tier: str,
    source_title: str,
    source_url: str,
    source_locator: str,
    evidence: str,
    machine_use_authorized: bool,
    conflicting_evidence: str | None = None,
    resolution: str | None = None,
) -> dict[str, Any]:
    return {
        "factId": fact_id,
        "fact": fact,
        "status": status,
        "sourceTier": source_tier,
        "sourceTitle": source_title,
        "sourcePublisher": "Dukascopy",
        "sourceUrl": source_url,
        "sourceAccessDate": "2026-09-11",
        "sourceLocator": source_locator,
        "quotedOrParaphrasedEvidence": evidence,
        "conflictingEvidence": conflicting_evidence,
        "resolution": resolution,
        "machineUseAuthorized": machine_use_authorized,
    }


def build_protocol_evidence() -> dict[str, Any]:
    """Record public technical evidence without contacting a price endpoint."""

    export = "Dukascopy Historical Price Data / Datos historicos de precios"
    jforex = "Dukascopy JForex History ticks"
    facts = [
        _protocol_fact(
            "PRODUCT_IDENTITY",
            "Provider product selected for the future experiment.",
            status="SOURCE_CLOSED",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page lines 577-591 and 783-803",
            evidence="The current Dukascopy page describes daily Dukascopy-style .bi5 tick files in an S3 Requester Pays bucket.",
            machine_use_authorized=True,
            resolution=PROVIDER_PRODUCT,
        ),
        _protocol_fact(
            "TRANSPORT_AND_REQUESTER_PAYS",
            "Future native retrieval transport and payer requirement.",
            status="SOURCE_CLOSED",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page lines 800-819, 876-882, 1051-1055",
            evidence="The official example identifies bucket cfg-public-proper-wallaby, eu-west-1, boto3 S3 access, and RequestPayer=requester.",
            machine_use_authorized=True,
            resolution="AWS_S3_GET_OBJECT_WITH_REQUESTER_PAYS",
        ),
        _protocol_fact(
            "DAILY_PARTITION_KEY",
            "Daily native key grammar and calendar encoding.",
            status="SOURCE_CLOSED",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page lines 579-591, 705-734",
            evidence="The documented daily key is SYMBOL/YEAR/MONTH/DAY_ticks.bi5; month is zero-indexed, and the decoder reconstructs a UTC day start from that date.",
            machine_use_authorized=True,
            resolution="USDJPY/YYYY/MM/DD_ticks.bi5; YYYY four digits; MM 00-11; DD two digits; UTC daily partition",
        ),
        _protocol_fact(
            "MISSING_PARTITION",
            "Meaning of a missing documented daily object.",
            status="SOURCE_CLOSED",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page lines 589-591 and 764-770",
            evidence="The page says there are no empty files and that a missing daily key/FileNotFoundError means no ticks for that day, such as weekends or holidays.",
            machine_use_authorized=True,
            resolution="MISSING_DOCUMENTED_DAILY_KEY_MEANS_NO_TICKS",
        ),
        _protocol_fact(
            "COMPRESSION_WRAPPER",
            "Exact LZMA framing/filter representation needed by an offline parser.",
            status="PROTOCOL_SOURCE_CONFLICT",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page lines 582, 629, 692, 764-770",
            evidence="The prose calls the payload a raw LZMA stream outside an .xz container and warns some libraries need explicit raw mode.",
            conflicting_evidence="The same official page's Python examples call lzma.decompress(compressed) without raw filters or a raw-format declaration; it does not publish the required raw LZMA filter parameters.",
            machine_use_authorized=False,
            resolution="UNRESOLVED_WITHOUT_PROVIDER_CLARIFICATION; no parser admitted",
        ),
        _protocol_fact(
            "RECORD_LAYOUT",
            "Decompressed tick record size, byte order, and field layout.",
            status="SOURCE_CLOSED",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page lines 592-601 and 632-643",
            evidence="Each decompressed tick is a 20-byte big-endian record: uint32 offset, uint32 ask, uint32 bid, float32 ask volume, float32 bid volume.",
            machine_use_authorized=True,
            resolution=">IIIff; offsets 0,4,8,12,16; no partial-record truncation",
        ),
        _protocol_fact(
            "TIMESTAMP_RECONSTRUCTION",
            "Native timestamp type, unit, base, and zone.",
            status="SOURCE_CLOSED",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page lines 597 and 637-650",
            evidence="The uint32 timestamp is milliseconds from the UTC day start, and the documented decoder adds that offset to the reconstructed day start.",
            machine_use_authorized=True,
            resolution="timestampUtc = nativeStartUtc + timedelta(milliseconds=uint32Offset)",
        ),
        _protocol_fact(
            "USDJPY_SCALE",
            "USDJPY point divisor for native integer bid and ask.",
            status="SOURCE_CLOSED",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page lines 602-610 and 668-679",
            evidence="The point-value table and helper list USDJPY among JPY pairs whose point value is 1000.",
            machine_use_authorized=True,
            resolution="canonicalPrice = nativeInteger / 1000",
        ),
        _protocol_fact(
            "EMPTY_OBJECT",
            "Treatment of a successful but zero-byte payload.",
            status="PROJECT_FAIL_CLOSED_POLICY",
            source_tier="TIER_1",
            source_title=export,
            source_url=OFFICIAL_EXPORT_URL,
            source_locator="current page line 591",
            evidence="The source documents no empty files and missing keys as the no-tick representation; it does not define a successful zero-byte object.",
            machine_use_authorized=True,
            resolution="SUCCESSFUL_ZERO_BYTE_RESPONSE_IS_ACQUISITION_INCOMPLETE_NOT_NO_TICKS",
        ),
        _protocol_fact(
            "JFOREX_ALTERNATIVE_REJECTED",
            "Why JForex interval retrieval is not the selected raw-byte product.",
            status="SOURCE_CLOSED",
            source_tier="TIER_2",
            source_title=jforex,
            source_url=OFFICIAL_JFOREX_TICKS_URL,
            source_locator="current page historical tick request semantics",
            evidence="JForex documents inclusive from/to history retrieval rather than a deterministic retained native object with the chosen raw-byte contract.",
            machine_use_authorized=True,
            resolution="REJECTED_FOR_THIS_EXPERIMENT; no mixing with S3 daily-object semantics",
        ),
        _protocol_fact(
            "RETRY_POLICY",
            "Future request retry behavior.",
            status="EXPERIMENT_POLICY_FROZEN",
            source_tier="NOT_APPLICABLE",
            source_title="R2 fail-closed experiment policy",
            source_url="",
            source_locator="R2 acquisition contract",
            evidence="The provider document gives no immutable retry semantics required by this experiment.",
            machine_use_authorized=True,
            resolution="MAX_ATTEMPTS_1; no automatic retry; any later retry requires the same partition identity and an audited new acquisition attempt",
        ),
        _protocol_fact(
            "REVISION_POLICY",
            "Future behavior if successful captures disagree.",
            status="EXPERIMENT_POLICY_FROZEN",
            source_tier="NOT_APPLICABLE",
            source_title="R2 fail-closed experiment policy",
            source_url="",
            source_locator="R2 acquisition contract",
            evidence="No provider object-version semantics were used or assumed by this pre-request milestone.",
            machine_use_authorized=True,
            resolution="DIFFERENT_SUCCESSFUL_RAW_SHA256_FOR_SAME_REQUEST_ID = PROVIDER_REVISION_CONFLICT; neither payload is scoreable until a separately reviewed revision process",
        ),
    ]
    body = {
        "contract": S3R1_R2_PROTOCOL_EVIDENCE_CONTRACT,
        "schemaVersion": S3R1_R2_SCHEMA_VERSION,
        "milestone": S3R1_R2_MILESTONE,
        "providerIdentity": "DUKASCOPY_HISTORICAL_USDJPY_TICK_SERVICE",
        "selectedProviderProduct": PROVIDER_PRODUCT,
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
        "criticalFacts": facts,
        "criticalUnresolvedFactIds": ["COMPRESSION_WRAPPER"],
        "providerProtocolFullyClosed": False,
        "outcomeUnlockBlocked": True,
    }
    return {**body, "protocolEvidenceHash": _canonical_hash(body)}


def build_source_lock(protocol_evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    evidence = copy.deepcopy(protocol_evidence) if protocol_evidence is not None else build_protocol_evidence()
    if evidence.get("protocolEvidenceHash") != _canonical_hash(_without_hash(evidence, "protocolEvidenceHash")):
        raise OutcomeAnalysisS3R1R2Error("Protocol evidence hash is invalid")
    sources = [
        {
            "sourceId": "DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_EXPORT",
            "url": OFFICIAL_EXPORT_URL,
            "publisher": "Dukascopy",
            "title": "Datos historicos de precios",
            "sourceTier": "TIER_1",
            "retrievedAtUtc": S3R1_R2_AUTHORED_AT_UTC,
            "criticalFactIds": [fact["factId"] for fact in evidence["criticalFacts"] if fact["sourceUrl"] == OFFICIAL_EXPORT_URL],
        },
        {
            "sourceId": "DUKASCOPY_JFOREX_HISTORY_TICKS",
            "url": OFFICIAL_JFOREX_TICKS_URL,
            "publisher": "Dukascopy",
            "title": "History ticks",
            "sourceTier": "TIER_2",
            "retrievedAtUtc": S3R1_R2_AUTHORED_AT_UTC,
            "criticalFactIds": ["JFOREX_ALTERNATIVE_REJECTED"],
        },
    ]
    body = {
        "contract": S3R1_R2_SOURCE_LOCK_CONTRACT,
        "schemaVersion": S3R1_R2_SCHEMA_VERSION,
        "milestone": S3R1_R2_MILESTONE,
        "protocolEvidenceHash": evidence["protocolEvidenceHash"],
        "sources": sources,
        "sourceConflict": {
            "status": "PROTOCOL_SOURCE_CONFLICT",
            "factId": "COMPRESSION_WRAPPER",
            "outcomeAccessBlocked": True,
            "requiredResolution": "OFFICIAL_DUKASCOPY_CLARIFICATION_OF_EXACT_LZMA_WRAPPER_AND_RAW_FILTER_PARAMETERS",
        },
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
    }
    return {**body, "protocolSourceLockHash": _canonical_hash(body)}


def _parse_utc(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OutcomeAnalysisS3R1R2Error(f"Invalid UTC {label}: {value}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise OutcomeAnalysisS3R1R2Error(f"{label} must be UTC")
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _daily_partition_key(day_start: datetime) -> str:
    return f"{INSTRUMENT}/{day_start.year:04d}/{day_start.month - 1:02d}/{day_start.day:02d}_ticks.bi5"


def build_provider_partition_plan(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Map frozen analytical windows to deduplicated UTC daily S3 partitions."""

    root = Path(resource_root).resolve()
    predecessor = _assert_r1_predecessor(root)
    intervals = copy.deepcopy(predecessor["acquisition"]["frozenIntervalSet"]["intervals"])
    if len(intervals) != 39 or len({item["intervalId"] for item in intervals}) != 39:
        raise OutcomeAnalysisS3R1R2Error("R2 requires exactly 39 unique frozen analytical intervals")
    by_day: dict[datetime, list[str]] = {}
    for interval in intervals:
        start = _parse_utc(interval["applyingStartUtc"], "analysis interval start")
        end = _parse_utc(interval["separatingEndUtc"], "analysis interval end")
        if start >= end or not interval.get("halfOpen"):
            raise OutcomeAnalysisS3R1R2Error("Frozen analytical interval must be a nonempty half-open UTC range")
        day = start.replace(hour=0, minute=0, second=0, microsecond=0)
        while day < end:
            by_day.setdefault(day, []).append(interval["intervalId"])
            day += timedelta(days=1)
    partitions = []
    for day_start in sorted(by_day):
        day_end = day_start + timedelta(days=1)
        key = _daily_partition_key(day_start)
        partitions.append(
            {
                "providerPartitionId": f"{PROVIDER_PRODUCT}::{INSTRUMENT}::{day_start.date().isoformat()}",
                "providerProduct": PROVIDER_PRODUCT,
                "instrument": INSTRUMENT,
                "nativeStartUtc": _utc_text(day_start),
                "nativeEndUtc": _utc_text(day_end),
                "analysisIntervalIdsCovered": sorted(by_day[day_start]),
                "reasonRequired": "UTC_DAILY_PARTITION_INTERSECTS_ONE_OR_MORE_FROZEN_HALF_OPEN_ANALYSIS_INTERVALS",
                "requestIdentity": {
                    "transport": "AWS_S3_GET_OBJECT_REQUESTER_PAYS",
                    "bucket": BUCKET,
                    "region": REGION,
                    "key": key,
                    "requestPayer": "requester",
                },
            }
        )
    covered = {interval_id for partition in partitions for interval_id in partition["analysisIntervalIdsCovered"]}
    expected = {interval["intervalId"] for interval in intervals}
    if covered != expected:
        raise OutcomeAnalysisS3R1R2Error("Daily provider partition plan does not cover every frozen analysis interval")
    body = {
        "contract": S3R1_R2_PARTITION_PLAN_CONTRACT,
        "schemaVersion": S3R1_R2_SCHEMA_VERSION,
        "milestone": S3R1_R2_MILESTONE,
        "providerProduct": PROVIDER_PRODUCT,
        "providerNativePartitionType": "UTC_DAILY_BI5_OBJECT",
        "partitionBoundarySemantics": "[nativeStartUtc, nativeEndUtc)",
        "analysisIntervalSetHash": _canonical_hash(intervals),
        "analysisIntervalCount": 39,
        "uniqueProviderPartitionCount": len(partitions),
        "partitions": partitions,
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
    }
    return {**body, "providerPartitionPlanHash": _canonical_hash(body)}


def build_market_data_acquisition_contract(
    resource_root: Path = PROJECT_ROOT,
    *,
    protocol_evidence: Mapping[str, Any] | None = None,
    source_lock: Mapping[str, Any] | None = None,
    partition_plan: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_r1_predecessor(root)
    evidence = copy.deepcopy(protocol_evidence) if protocol_evidence is not None else build_protocol_evidence()
    lock = copy.deepcopy(source_lock) if source_lock is not None else build_source_lock(evidence)
    plan = copy.deepcopy(partition_plan) if partition_plan is not None else build_provider_partition_plan(root)
    if evidence.get("protocolEvidenceHash") != _canonical_hash(_without_hash(evidence, "protocolEvidenceHash")):
        raise OutcomeAnalysisS3R1R2Error("Protocol evidence hash is invalid")
    if lock.get("protocolSourceLockHash") != _canonical_hash(_without_hash(lock, "protocolSourceLockHash")):
        raise OutcomeAnalysisS3R1R2Error("Protocol source lock hash is invalid")
    if plan.get("providerPartitionPlanHash") != _canonical_hash(_without_hash(plan, "providerPartitionPlanHash")):
        raise OutcomeAnalysisS3R1R2Error("Provider partition plan hash is invalid")
    intervals = predecessor["acquisition"]["frozenIntervalSet"]["intervals"]
    body = {
        "contract": S3R1_R2_ACQUISITION_CONTRACT,
        "schemaVersion": S3R1_R2_SCHEMA_VERSION,
        "milestone": S3R1_R2_MILESTONE,
        "status": "PRE_REQUEST_PROVIDER_PROTOCOL_INCOMPLETE_OUTCOME_UNLOCK_BLOCKED",
        "supersedesContract": predecessor["acquisition"]["contract"],
        "supersedesHash": HISTORICAL_R1_ACQUISITION_HASH,
        "provider": {
            "identity": "DUKASCOPY_HISTORICAL_USDJPY_TICK_SERVICE",
            "product": PROVIDER_PRODUCT,
            "instrument": INSTRUMENT,
            "symbol": INSTRUMENT,
            "quoteConvention": "JPY_PER_USD",
        },
        "protocolSourceLockHash": lock["protocolSourceLockHash"],
        "protocolEvidenceHash": evidence["protocolEvidenceHash"],
        "analysisIntervalSetHash": _canonical_hash(intervals),
        "providerPartitionPlanHash": plan["providerPartitionPlanHash"],
        "transport": {
            "mechanism": "AWS_S3_GET_OBJECT_REQUESTER_PAYS",
            "bucket": BUCKET,
            "region": REGION,
            "authentication": "AWS_CREDENTIALS_REQUIRED_AT_FUTURE_AUTHORIZED_ACQUISITION",
            "requestPayer": "requester",
            "networkClientImplemented": False,
        },
        "nativePartitioning": {
            "type": "UTC_DAILY_BI5_OBJECT",
            "keyGrammar": "USDJPY/YYYY/MM/DD_ticks.bi5",
            "monthIndexing": "ZERO_BASED_00_TO_11",
            "nativeBoundary": "[UTC midnight, next UTC midnight)",
            "analysisIntervalCount": 39,
            "uniqueProviderPartitionCount": plan["uniqueProviderPartitionCount"],
        },
        "compression": {
            "status": "PROTOCOL_SOURCE_CONFLICT",
            "documentedAlgorithm": "LZMA",
            "wrapperAndFilterParameters": "UNRESOLVED_OFFICIAL_DOCUMENTATION_CONFLICT",
            "parserUseAuthorized": False,
        },
        "binaryRecordLayout": {
            "recordSizeBytes": 20,
            "byteOrder": "BIG_ENDIAN",
            "fields": [
                {"offset": 0, "length": 4, "type": "uint32", "name": "millisecondsFromUtcDayStart"},
                {"offset": 4, "length": 4, "type": "uint32", "name": "askNative"},
                {"offset": 8, "length": 4, "type": "uint32", "name": "bidNative"},
                {"offset": 12, "length": 4, "type": "float32", "name": "askVolumeMillionsBaseCurrency"},
                {"offset": 16, "length": 4, "type": "float32", "name": "bidVolumeMillionsBaseCurrency"},
            ],
            "partialRecordPolicy": "RAW_RECORD_ALIGNMENT_INVALID",
        },
        "timestampEncoding": {
            "nativeType": "uint32",
            "unit": "milliseconds",
            "base": "UTC_NATIVE_PARTITION_DAY_START",
            "formula": "timestampUtc = nativeStartUtc + timedelta(milliseconds=millisecondsFromUtcDayStart)",
            "partitionBoundCheck": "nativeStartUtc <= timestampUtc < nativeEndUtc",
        },
        "priceEncoding": {
            "nativeBidType": "uint32",
            "nativeAskType": "uint32",
            "scaleNumerator": 1,
            "scaleDenominator": 1000,
            "canonicalRepresentation": "NATIVE_UINT32_PLUS_EXACT_RATIONAL_DIVISOR_1000",
            "quoteValidity": "bidNative > 0 and askNative >= bidNative",
        },
        "parser": {
            "status": "NOT_IMPLEMENTED_PROTOCOL_SOURCE_CONFLICT",
            "module": None,
            "parserContractHash": None,
            "parserSourceSha256": None,
            "offlineOnlyWhenAuthorized": True,
            "networkAccess": False,
            "blockedByFactId": "COMPRESSION_WRAPPER",
        },
        "canonicalTickSchema": {
            "fields": ["timestampUtc", "bidNative", "askNative", "bidVolumeMillionsBaseCurrency", "askVolumeMillionsBaseCurrency", "recordIndex"],
            "canonicalSerialization": "UTF8_JSON_LINES_SORTED_KEYS_ONE_OBJECT_PER_CANONICAL_TICK_TRAILING_LF",
            "parsedTicksSha256": "SHA256_OF_CANONICAL_SERIALIZATION",
        },
        "intervalAdapter": {
            "scienceBoundary": "[applyingStartUtc, separatingEndUtc)",
            "providerPartitionFetch": "WHOLE_REQUIRED_UTC_DAILY_PARTITIONS_ONLY",
            "localFilter": "applyingStartUtc <= timestampUtc < separatingEndUtc",
            "requestTimeRoundingOfScientificWindows": False,
        },
        "duplicatePolicy": {
            "identicalRecord": "DEDUPLICATE_WITHOUT_AVERAGING_FOR_SCORING",
            "conflictingSameTimestamp": "DATA_CONFLICT_UNSCORABLE_IN_INTERVAL",
            "sourceOrderResolution": False,
        },
        "conflictPolicy": {
            "differentSuccessfulRawSha256SameRequestId": "PROVIDER_REVISION_CONFLICT",
            "automaticSelectionAfterConflict": False,
            "manualRepairAllowed": False,
            "fallbackProviderAllowed": False,
            "providerSubstitutionAllowed": False,
        },
        "missingPartitionPolicy": "MISSING_DOCUMENTED_DAILY_KEY_MEANS_NO_TICKS",
        "emptyPayloadPolicy": "SUCCESSFUL_ZERO_BYTE_RESPONSE_IS_ACQUISITION_INCOMPLETE_NOT_NO_TICKS",
        "retryPolicy": {
            "maxAttempts": 1,
            "automaticRetry": False,
            "retryableErrors": [],
            "terminalPolicy": "ALL_UNSUCCESSFUL_ATTEMPTS_ARE_RECORDED_AND_REQUIRE_SEPARATE_AUTHORIZED_RETRY_OF_IDENTICAL_REQUEST_ID",
            "outcomeDrivenRetryAllowed": False,
        },
        "revisionPolicy": {
            "providerVersionSemanticsAssumed": False,
            "firstSuccessfulPayload": "RETAINED_AS_PROVISIONAL_RAW_CAPTURE_ONLY",
            "secondDifferentSuccessfulPayload": "PROVIDER_REVISION_CONFLICT",
            "scoreableAfterConflict": False,
            "dataRevisionAfterCapture": "REQUIRES_NEW_REVIEWED_ACQUISITION_RECORD",
        },
        "rawCapturePolicy": {
            "rawSha256": "SHA256_OF_EXACT_RESPONSE_BYTES",
            "retention": "RETAIN_OUTSIDE_GIT_UNCHANGED_PER_PROVIDER_PARTITION",
            "futureManifestContract": "MO_R4A_S4_MARKET_DATA_RAW_ACQUISITION_MANIFEST_V1",
            "requiredFutureManifestFields": [
                "requestId",
                "providerProduct",
                "instrument",
                "providerPartitionId",
                "nativeStartUtc",
                "nativeEndUtc",
                "requestParameters",
                "retrievedAtUtc",
                "transportStatus",
                "providerMetadata",
                "byteLength",
                "rawSha256",
                "parserContractHash",
                "parserSourceSha256",
                "parsedRecordCount",
                "parsedTicksSha256",
                "firstTimestampUtc",
                "lastTimestampUtc",
                "acquisitionDisposition",
            ],
            "providerAccessPerformed": False,
            "marketOutcomeRead": False,
        },
        "parsedCapturePolicy": {
            "parsedTicksSha256": "SHA256_OF_CANONICAL_UTF8_JSON_LINES",
            "rawByteHashRequiredBeforeParse": True,
            "outcomeScoringAllowed": False,
        },
        "storagePolicy": {
            "privateRawBytesInGitAllowed": False,
            "realMarketCsvInGitAllowed": False,
            "realMarketParquetInGitAllowed": False,
            "manualRepairAllowed": False,
        },
        "frozenIntervalSet": {
            "actualCount": 13,
            "minus7Count": 13,
            "plus7Count": 13,
            "totalCount": 39,
            "intervals": copy.deepcopy(intervals),
        },
        "providerAccessPerformed": False,
        "marketOutcomeRead": False,
        "executionAllowed": False,
        "outcomeUnlockAllowed": False,
    }
    return {**body, "marketDataAcquisitionContractHash": _canonical_hash(body)}


def build_s3r1_r2_preregistration(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_r1_predecessor(root)
    acquisition = build_market_data_acquisition_contract(root)
    source_lock = build_source_lock()
    partition_plan = build_provider_partition_plan(root)
    body = copy.deepcopy(predecessor["preregistration"])
    body.pop("preregistrationHash", None)
    body.update(
        {
            "contract": S3R1_R2_PREREGISTRATION_CONTRACT,
            "schemaVersion": S3R1_R2_SCHEMA_VERSION,
            "milestone": S3R1_R2_MILESTONE,
            "startingMaster": S3R1_R2_EXPECTED_STARTING_MASTER,
            "preregistrationAuthoredAtUtc": S3R1_R2_AUTHORED_AT_UTC,
            "status": "S3R1_R2_PROVIDER_PROTOCOL_INCOMPLETE_OUTCOME_UNLOCK_BLOCKED",
            "nextGate": "CENTRAL_REVIEW_PROVIDER_PROTOCOL_GAP",
            "supersedesPreregistrationContract": predecessor["preregistration"]["contract"],
            "supersedesPreregistrationHash": HISTORICAL_R1_PREREGISTRATION_HASH,
            "providerProtocolClosureReason": "DAILY_PARTITION_AND_RECORD_SEMANTICS_SOURCE_CLOSED_BUT_COMPRESSION_WRAPPER_CONFLICT_REMAINS",
            "marketDataAcquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
            "protocolSourceLockHash": source_lock["protocolSourceLockHash"],
            "providerPartitionPlanHash": partition_plan["providerPartitionPlanHash"],
            "scientificDesignChanged": False,
        }
    )
    return {**body, "preregistrationHash": _canonical_hash(body)}


def build_s3r1_r2_schema(preregistration: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = copy.deepcopy(preregistration) if preregistration is not None else build_s3r1_r2_preregistration(PROJECT_ROOT)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": S3R1_R2_PREREGISTRATION_CONTRACT,
        "title": S3R1_R2_PREREGISTRATION_CONTRACT,
        **r1.s3r1._schema_for_value(payload),
    }


def build_s3r1_r2_primary_population(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_r1_predecessor(root)
    preregistration = build_s3r1_r2_preregistration(root)
    body = copy.deepcopy(predecessor["population"])
    body.pop("primaryPopulationHash", None)
    body.update(
        {
            "contract": S3R1_R2_PRIMARY_POPULATION_CONTRACT,
            "schemaVersion": S3R1_R2_SCHEMA_VERSION,
            "milestone": S3R1_R2_MILESTONE,
            "supersedesPrimaryPopulationContract": predecessor["population"]["contract"],
            "supersedesPrimaryPopulationHash": HISTORICAL_R1_POPULATION_HASH,
            "preregistrationHash": preregistration["preregistrationHash"],
            "scientificRowsUnchanged": True,
        }
    )
    return {**body, "primaryPopulationHash": _canonical_hash(body)}


def build_s3r1_r2_overlap_clusters(resource_root: Path = PROJECT_ROOT, *, population: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_r1_predecessor(root)
    selected_population = copy.deepcopy(population) if population is not None else build_s3r1_r2_primary_population(root)
    if s3.derive_overlap_clusters(selected_population["primaryMarketScorableRows"]) != predecessor["clusters"]["clusters"]:
        raise OutcomeAnalysisS3R1R2Error("R2 overlap clusters must remain the exact four R1 clusters")
    body = copy.deepcopy(predecessor["clusters"])
    body.pop("overlapClustersHash", None)
    body.update(
        {
            "contract": S3R1_R2_OVERLAP_CLUSTERS_CONTRACT,
            "schemaVersion": S3R1_R2_SCHEMA_VERSION,
            "milestone": S3R1_R2_MILESTONE,
            "supersedesOverlapClustersContract": predecessor["clusters"]["contract"],
            "supersedesOverlapClustersHash": HISTORICAL_R1_CLUSTERS_HASH,
            "primaryPopulationHash": selected_population["primaryPopulationHash"],
            "scientificClustersUnchanged": True,
        }
    )
    return {**body, "overlapClustersHash": _canonical_hash(body)}


def build_s3r1_r2_invariance_audit(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    predecessor = _assert_r1_predecessor(root)
    selected_prereg = copy.deepcopy(preregistration) if preregistration is not None else build_s3r1_r2_preregistration(root)
    selected_population = copy.deepcopy(population) if population is not None else build_s3r1_r2_primary_population(root)
    selected_clusters = copy.deepcopy(clusters) if clusters is not None else build_s3r1_r2_overlap_clusters(root, population=selected_population)
    body = copy.deepcopy(predecessor["invariance"])
    body.pop("analysisPlanInvarianceAuditHash", None)
    body.update(
        {
            "contract": S3R1_R2_INVARIANCE_CONTRACT,
            "schemaVersion": S3R1_R2_SCHEMA_VERSION,
            "milestone": S3R1_R2_MILESTONE,
            "supersedesInvarianceAuditContract": predecessor["invariance"]["contract"],
            "supersedesInvarianceAuditHash": HISTORICAL_R1_INVARIANCE_HASH,
            "preregistrationHash": selected_prereg["preregistrationHash"],
            "primaryPopulationHash": selected_population["primaryPopulationHash"],
            "overlapClustersHash": selected_clusters["overlapClustersHash"],
            "providerProtocolDoesNotChangeScientificDesign": True,
            "parserNotImplementedWhileConflictOpen": True,
        }
    )
    return {**body, "analysisPlanInvarianceAuditHash": _canonical_hash(body)}


def compute_analysis_core_manifest_hash(
    upstream_hashes: Mapping[str, str],
    preregistration_hash: str,
    population_hash: str,
    clusters_hash: str,
    invariance_hash: str,
    acquisition_hash: str,
    source_lock_hash: str,
    partition_plan_hash: str,
) -> str:
    body = {
        "contract": S3R1_R2_CORE_CONTRACT,
        "schemaVersion": S3R1_R2_SCHEMA_VERSION,
        "milestone": S3R1_R2_MILESTONE,
        "upstreamHashes": dict(upstream_hashes),
        "preregistrationHash": preregistration_hash,
        "primaryPopulationHash": population_hash,
        "overlapClustersHash": clusters_hash,
        "analysisPlanInvarianceAuditHash": invariance_hash,
        "marketDataAcquisitionContractHash": acquisition_hash,
        "protocolSourceLockHash": source_lock_hash,
        "providerPartitionPlanHash": partition_plan_hash,
    }
    return _canonical_hash(body)


def build_analysis_core_manifest(
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    invariance: Mapping[str, Any],
    acquisition: Mapping[str, Any],
    source_lock: Mapping[str, Any],
    partition_plan: Mapping[str, Any],
) -> dict[str, Any]:
    components = (
        (preregistration, "preregistrationHash"),
        (population, "primaryPopulationHash"),
        (clusters, "overlapClustersHash"),
        (invariance, "analysisPlanInvarianceAuditHash"),
        (acquisition, "marketDataAcquisitionContractHash"),
        (source_lock, "protocolSourceLockHash"),
        (partition_plan, "providerPartitionPlanHash"),
    )
    for component, hash_key in components:
        if component.get(hash_key) != _canonical_hash(_without_hash(component, hash_key)):
            raise OutcomeAnalysisS3R1R2Error(f"Invalid R2 component hash: {hash_key}")
    body = {
        "contract": S3R1_R2_CORE_CONTRACT,
        "schemaVersion": S3R1_R2_SCHEMA_VERSION,
        "milestone": S3R1_R2_MILESTONE,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": preregistration["preregistrationHash"],
        "primaryPopulationHash": population["primaryPopulationHash"],
        "overlapClustersHash": clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": acquisition["marketDataAcquisitionContractHash"],
        "protocolSourceLockHash": source_lock["protocolSourceLockHash"],
        "providerPartitionPlanHash": partition_plan["providerPartitionPlanHash"],
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
            body["protocolSourceLockHash"],
            body["providerPartitionPlanHash"],
        ),
    }


def build_s3r1_r2_acceptance_manifest(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
    invariance: Mapping[str, Any] | None = None,
    acquisition: Mapping[str, Any] | None = None,
    source_lock: Mapping[str, Any] | None = None,
    partition_plan: Mapping[str, Any] | None = None,
    core: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    _assert_r1_predecessor(root)
    expected_evidence = build_protocol_evidence()
    expected_lock = build_source_lock(expected_evidence)
    expected_plan = build_provider_partition_plan(root)
    expected_acquisition = build_market_data_acquisition_contract(root, protocol_evidence=expected_evidence, source_lock=expected_lock, partition_plan=expected_plan)
    expected_prereg = build_s3r1_r2_preregistration(root)
    expected_population = build_s3r1_r2_primary_population(root)
    expected_clusters = build_s3r1_r2_overlap_clusters(root, population=expected_population)
    expected_invariance = build_s3r1_r2_invariance_audit(root, preregistration=expected_prereg, population=expected_population, clusters=expected_clusters)
    expected_core = build_analysis_core_manifest(
        expected_prereg, expected_population, expected_clusters, expected_invariance, expected_acquisition, expected_lock, expected_plan
    )
    supplied = (
        (preregistration, expected_prereg, "preregistration"),
        (population, expected_population, "population"),
        (clusters, expected_clusters, "clusters"),
        (invariance, expected_invariance, "invariance"),
        (acquisition, expected_acquisition, "acquisition"),
        (source_lock, expected_lock, "source lock"),
        (partition_plan, expected_plan, "partition plan"),
        (core, expected_core, "core"),
    )
    for provided, expected, label in supplied:
        if provided is not None:
            _require_exact(provided, expected, f"Supplied R2 {label}")
    body = {
        "contract": S3R1_R2_ACCEPTANCE_CONTRACT,
        "schemaVersion": S3R1_R2_SCHEMA_VERSION,
        "milestone": S3R1_R2_MILESTONE,
        "status": "S3R1_R2_PROVIDER_PROTOCOL_INCOMPLETE_OUTCOME_UNLOCK_BLOCKED",
        "branch": "BRANCH_B_INCOMPLETE",
        "nextGate": "CENTRAL_REVIEW_PROVIDER_PROTOCOL_GAP",
        "startingMaster": S3R1_R2_EXPECTED_STARTING_MASTER,
        "supersedesAcceptanceManifestContract": r1.S3R1_R1_ACCEPTANCE_CONTRACT,
        "supersedesAcceptanceManifestHash": HISTORICAL_R1_ACCEPTANCE_HASH,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": expected_prereg["preregistrationHash"],
        "primaryPopulationHash": expected_population["primaryPopulationHash"],
        "overlapClustersHash": expected_clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": expected_invariance["analysisPlanInvarianceAuditHash"],
        "marketDataAcquisitionContractHash": expected_acquisition["marketDataAcquisitionContractHash"],
        "protocolSourceLockHash": expected_lock["protocolSourceLockHash"],
        "providerPartitionPlanHash": expected_plan["providerPartitionPlanHash"],
        "analysisCoreManifestHash": expected_core["analysisCoreManifestHash"],
        "activeBlockers": ["COMPRESSION_WRAPPER_PROTOCOL_SOURCE_CONFLICT"],
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


def validate_s3r1_r2_artifacts(resource_root: Path = PROJECT_ROOT) -> None:
    root = Path(resource_root).resolve()
    evidence = build_protocol_evidence()
    lock = build_source_lock(evidence)
    plan = build_provider_partition_plan(root)
    acquisition = build_market_data_acquisition_contract(root, protocol_evidence=evidence, source_lock=lock, partition_plan=plan)
    prereg = build_s3r1_r2_preregistration(root)
    population = build_s3r1_r2_primary_population(root)
    clusters = build_s3r1_r2_overlap_clusters(root, population=population)
    invariance = build_s3r1_r2_invariance_audit(root, preregistration=prereg, population=population, clusters=clusters)
    core = build_analysis_core_manifest(prereg, population, clusters, invariance, acquisition, lock, plan)
    acceptance = build_s3r1_r2_acceptance_manifest(
        root,
        preregistration=prereg,
        population=population,
        clusters=clusters,
        invariance=invariance,
        acquisition=acquisition,
        source_lock=lock,
        partition_plan=plan,
        core=core,
    )
    schema = build_s3r1_r2_schema(prereg)
    r1.validate_json_schema_instance(prereg, schema)
    if acceptance["status"] != "S3R1_R2_PROVIDER_PROTOCOL_INCOMPLETE_OUTCOME_UNLOCK_BLOCKED":
        raise OutcomeAnalysisS3R1R2Error("R2 must remain Branch B while the compression conflict is open")
    if evidence["providerProtocolFullyClosed"] or acquisition["parser"]["status"] != "NOT_IMPLEMENTED_PROTOCOL_SOURCE_CONFLICT":
        raise OutcomeAnalysisS3R1R2Error("R2 must not imply an authorized parser")


def write_s3r1_r2_artifacts(resource_root: Path = PROJECT_ROOT, *, outcome_source: object | None = None) -> dict[str, Path]:
    if outcome_source is not None:
        raise OutcomeAnalysisS3R1R2Error("S3R1-R2 cannot accept a provider, market file, tick source, or outcome")
    root = Path(resource_root).resolve()
    evidence = build_protocol_evidence()
    lock = build_source_lock(evidence)
    plan = build_provider_partition_plan(root)
    acquisition = build_market_data_acquisition_contract(root, protocol_evidence=evidence, source_lock=lock, partition_plan=plan)
    prereg = build_s3r1_r2_preregistration(root)
    population = build_s3r1_r2_primary_population(root)
    clusters = build_s3r1_r2_overlap_clusters(root, population=population)
    invariance = build_s3r1_r2_invariance_audit(root, preregistration=prereg, population=population, clusters=clusters)
    core = build_analysis_core_manifest(prereg, population, clusters, invariance, acquisition, lock, plan)
    acceptance = build_s3r1_r2_acceptance_manifest(
        root,
        preregistration=prereg,
        population=population,
        clusters=clusters,
        invariance=invariance,
        acquisition=acquisition,
        source_lock=lock,
        partition_plan=plan,
        core=core,
    )
    artifacts = {
        "protocolEvidence": root / DEFAULT_PROTOCOL_EVIDENCE_PATH.relative_to(PROJECT_ROOT),
        "sourceLock": root / DEFAULT_SOURCE_LOCK_PATH.relative_to(PROJECT_ROOT),
        "partitionPlan": root / DEFAULT_PARTITION_PLAN_PATH.relative_to(PROJECT_ROOT),
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
        "protocolEvidence": evidence,
        "sourceLock": lock,
        "partitionPlan": plan,
        "acquisition": acquisition,
        "preregistration": prereg,
        "schema": build_s3r1_r2_schema(prereg),
        "population": population,
        "clusters": clusters,
        "invariance": invariance,
        "core": core,
        "acceptance": acceptance,
    }
    for name, value in values.items():
        _write_json(artifacts[name], value)
    artifacts["report"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["report"].write_text(render_report(evidence, lock, plan, acquisition, prereg, population, core, acceptance), encoding="utf-8")
    return artifacts


def render_report(
    evidence: Mapping[str, Any],
    source_lock: Mapping[str, Any],
    plan: Mapping[str, Any],
    acquisition: Mapping[str, Any],
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    core: Mapping[str, Any],
    acceptance: Mapping[str, Any],
) -> str:
    counts = population["populationCounts"]
    return "\n".join(
        [
            "# MO-R4A-S3R1-R2 Dukascopy Provider Protocol Closure",
            "",
            "## Result",
            "",
            "R2 is a fail-closed Branch B successor. It did not contact a provider or read a market outcome. Dukascopy's current technical page source-closes daily S3 partitioning, the 20-byte record layout, UTC-day offsets, and USDJPY's 1000 divisor. The same page conflicts on the exact LZMA wrapper/filter contract, so no parser or future outcome acquisition is authorized.",
            "",
            "## Provider Decision",
            "",
            f"Selected product: `{PROVIDER_PRODUCT}`. The daily native request identity is `s3://{BUCKET}/USDJPY/YYYY/MM/DD_ticks.bi5` in `{REGION}` with `RequestPayer=requester`; `MM` is zero-indexed. JForex inclusive time-range history is expressly not mixed into this raw-object contract.",
            "",
            "| Question | Final answer | Source tier | Exact source | Confidence/status |",
            "| --- | --- | --- | --- | --- |",
            f"| Provider product | {PROVIDER_PRODUCT} | Tier 1 | {OFFICIAL_EXPORT_URL} | SOURCE_CLOSED |",
            "| Partition granularity | UTC daily .bi5 object | Tier 1 | Current export page lines 579-591 | SOURCE_CLOSED |",
            "| Path/request syntax | USDJPY/YYYY/MM/DD_ticks.bi5; S3 requester-pays | Tier 1 | Current export page lines 584-591, 800-819 | SOURCE_CLOSED |",
            "| Compression | LZMA named, exact wrapper/filter not source-closed | Tier 1 | Current export page lines 582, 629, 692, 768 | PROTOCOL_SOURCE_CONFLICT |",
            "| Record size and byte order | 20 bytes, big endian | Tier 1 | Current export page lines 592-601 | SOURCE_CLOSED |",
            "| Timestamp | uint32 milliseconds from UTC day start | Tier 1 | Current export page lines 597, 637-650 | SOURCE_CLOSED |",
            "| Ask/bid and volumes | uint32 ask, uint32 bid, float32 volumes | Tier 1 | Current export page lines 598-601 | SOURCE_CLOSED |",
            "| USDJPY scale | native integer divided by 1000 | Tier 1 | Current export page lines 602-608, 668-679 | SOURCE_CLOSED |",
            "| Missing partition | documented missing daily key means no ticks | Tier 1 | Current export page lines 589-591 | SOURCE_CLOSED |",
            "| Empty payload | zero-byte success is acquisition-incomplete | Project policy | R2 contract | FAIL_CLOSED |",
            "| Request boundary semantics | whole UTC days; local scientific filter remains half-open | Project policy | R2 contract | FROZEN |",
            "| Retry policy | one attempt, no automatic retry | Project policy | R2 contract | FROZEN |",
            "| Revision policy | differing successful raw hashes cause conflict | Project policy | R2 contract | FROZEN |",
            "",
            "## Native Partition Plan",
            "",
            f"The 39 frozen analytical windows (13 actual, 13 minus seven days, 13 plus seven days) map to `{plan['uniqueProviderPartitionCount']}` unique UTC daily partitions. Shared daily partitions appear once and carry every covered analytical interval ID. The plan contains no response-existence or market-value data.",
            "",
            "## Parser Boundary",
            "",
            "An offline parser is deliberately **not** implemented. The evidence calls the files raw LZMA outside .xz while showing `lzma.decompress` without raw filter parameters. Without a provider-issued wrapper/filter specification, any parser choice would be an unsupported convention. If clarified, the future parser must reject non-20-byte alignment, timestamps outside its native day, nonpositive bid, ask below bid, identical-duplicate ambiguity, and conflicting same-timestamp quotes.",
            "",
            "## Hash Chain And Invariance",
            "",
            f"Historical R1 acquisition remains `{HISTORICAL_R1_ACQUISITION_HASH}`. R2 acquisition is `{acquisition['marketDataAcquisitionContractHash']}`; protocol lock is `{source_lock['protocolSourceLockHash']}`; partition plan is `{plan['providerPartitionPlanHash']}`; preregistration is `{preregistration['preregistrationHash']}`; R2 core is `{core['analysisCoreManifestHash']}`; acceptance is `{acceptance['acceptanceManifestHash']}`.",
            "",
            f"The scientific plan remains unchanged: {counts['frozenEventCount']} frozen identities, {counts['primaryMarketScorableCount']} primary rows, the 40-state conditional null, 39 frozen windows, four clusters, and the original midpoint/return/zero/timing rules. This package contains no market return, hit, p-value, timing result, or real payload hash.",
            "",
            "## Gate",
            "",
            f"Acceptance is `{acceptance['status']}` with next gate `{acceptance['nextGate']}`. `providerAccessPerformed=false`, `marketOutcomeRead=false`, all 16 outcome access flags are false, and `executionAllowed=false`. A targeted Astra audit is not ready while the official compression conflict remains unresolved.",
            "",
        ]
    )
