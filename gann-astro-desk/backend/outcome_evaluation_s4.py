"""Outcome evaluator frozen in O1; real captures are never read by this module at import."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Iterator, Mapping, Sequence


MILESTONE = "MO-R4A-S4-O1"
SCHEMA_VERSION = 1
USDJPY_NATIVE_DIVISOR = 1000
NUMERIC_PRECISION = 50
NUMERIC_ROUNDING = ROUND_HALF_EVEN
RESULT_CONTRACT = "MO_R4A_S4_REAL_OUTCOME_EVALUATION_RESULT_V1"
FREEZE_HASHES = {
    "preregistrationHash": "23564E1F41C441EC1FB98B3FBD025F43643AEF75C27AD080550F7DCB7D64F272",
    "primaryPopulationHash": "7F3CB6DE622A71FDA7F66E89BDAE2D0B7E3228E94BCAC403220DB17CF2686317",
    "overlapClustersHash": "6D4968B9C7DB7B912FFF2567088AECFEE7AC00C5329BD0245E6BDE3A6613CC0E",
    "analysisPlanInvarianceAuditHash": "C53F5EB8C6ADAB19D090A834FBCFABA6D9207ADC9640C6E08CD8534D137748F9",
    "analysisIntervalSetHash": "3A76939D2597AAE4742587738846987E82EBC73F1A47730F6809303634122465",
    "acquisitionManifestHash": "FA336FA0577EB2EC5917E8811BF1918326E130091D56CF7948C401F5405AA71E",
    "acquisitionFreezeGateHash": "8F800EC0222ECE728E3D78D4F96E65F7FE7DCF7B7C85E1EF72EEEDAB7461804F",
    "aggregateCaptureHash": "F1488479ED7F963F517A0C6BD1FEF393882628A5BFE35B3795A31E8CC119044D",
    "astraDispositionHash": "BD7A31104BD339DE032C124A85D1A868021523EFD764789827BFD93371D04D78",
    "parserContractHash": "18259325D9C8B245C05F4ECF596AD86395406A485E58DF3DF18C6B638C86BABE",
    "acquisitionContractHash": "BE4C378E368956F46F69D004D0C7522B32EA784C15894106B98DA8AA9A983CAC",
    "partitionPlanHash": "5C39D983DD11288B24ABCF0E17F38C862A6B3B283CC68ABC3377C3324BBD738D",
    "acquisitionSourceSha256": "2448FD3B63FB85645F966609B377AB2C3DDF22CC240BDEBFDCFAB5257832B90A",
    "parserSourceSha256": "F3D49AFBC055D9C1CF2E513194C9A98C8D55769FF974343B99A4D00EE4A35BC8",
}
EXPECTED_OUTCOME_AUTHORIZATION = "CENTRAL_REVIEW_FOR_S4_OUTCOME_EXECUTION_UNLOCK"
PARSED_FIELDS = frozenset(
    {"partitionId", "recordIndex", "timestampUtc", "askNative", "bidNative", "askVolumeBitsHex", "bidVolumeBitsHex"}
)
VOLUME_BITS_PATTERN = re.compile(r"^[0-9A-F]{8}$")
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")
UTC_MILLISECOND_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")

EXPECTED_DIRECTION = {
    ("USD", "SUPPORTIVE"): "UP",
    ("USD", "ADVERSE"): "DOWN",
    ("JPY", "SUPPORTIVE"): "DOWN",
    ("JPY", "ADVERSE"): "UP",
}
EXPECTED_Q = {"UP": 1, "DOWN": -1}
HORIZON_DAYS = {"ACTUAL": 0, "MINUS_7": -7, "PLUS_7": 7}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATHS = {
    "preregistration": Path("configs/research/machine_interpretation/outcome_analysis_preregistration_s3r1_r3_r2_v1.json"),
    "acquisitionContract": Path("configs/research/machine_interpretation/market_data_acquisition_contract_s3r1_r3_r2_v1.json"),
    "parserContract": Path("configs/research/machine_interpretation/dukascopy_tick_parser_contract_s3r1_r3_r2_v1.json"),
    "population": Path("status/audits/mo_r4a_s3r1_r3_r2_primary_analysis_population.json"),
    "clusters": Path("status/audits/mo_r4a_s3r1_r3_r2_overlap_clusters.json"),
    "invariance": Path("status/audits/mo_r4a_s3r1_r3_r2_analysis_plan_invariance_audit.json"),
    "partitionPlan": Path("status/audits/mo_r4a_s3r1_r2_provider_partition_plan.json"),
    "manifest": Path("status/audits/mo_r4a_s4_a1_market_data_raw_acquisition_manifest.json"),
    "freezeGate": Path("status/acceptance/mo_r4a_s4_a1_acquisition_freeze_gate.json"),
    "astraDisposition": Path("status/audits/mo_r4a_s4_a1_a2_astra_acquisition_provenance_audit_disposition.json"),
}


class S4EvaluationError(ValueError):
    """Typed fail-closed error without embedding market values in its message."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(f"{code}: {detail}" if detail else code)


@dataclass(frozen=True)
class FrozenStudy:
    primary_events: tuple[dict[str, Any], ...]
    all_events: tuple[dict[str, Any], ...]
    intervals: tuple[dict[str, Any], ...]
    clusters: tuple[dict[str, Any], ...]
    partitions: tuple[dict[str, Any], ...]
    manifest_records: tuple[dict[str, Any], ...]
    input_hashes: dict[str, str]


@dataclass(frozen=True)
class ParsedTick:
    partition_id: str
    record_index: int
    timestamp_utc: datetime
    ask_native: int
    bid_native: int


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _self_hash(value: Mapping[str, Any], key: str, expected: str, label: str) -> str:
    observed = value.get(key)
    computed = _sha256(_canonical_bytes({name: item for name, item in value.items() if name != key}))
    if observed != expected or computed != expected:
        raise S4EvaluationError("FROZEN_INPUT_HASH_MISMATCH", label)
    return computed


def _read_artifact(root: Path, name: str) -> dict[str, Any]:
    try:
        value = json.loads((root / ARTIFACT_PATHS[name]).read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise S4EvaluationError("FROZEN_INPUT_UNAVAILABLE", name) from exc
    if not isinstance(value, dict):
        raise S4EvaluationError("FROZEN_INPUT_SCHEMA_INVALID", name)
    return value


def _utc_datetime(value: object, *, error_code: str = "FROZEN_INTERVAL_INVALID") -> datetime:
    if not isinstance(value, str) or not UTC_PATTERN.fullmatch(value):
        raise S4EvaluationError(error_code, "timestamp must be an explicit UTC instant")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise S4EvaluationError(error_code, "timestamp is not a valid UTC instant") from exc
    if parsed.utcoffset() != timedelta(0):
        raise S4EvaluationError(error_code, "timestamp must be UTC")
    return parsed.astimezone(timezone.utc)


def _daily_key(day: date) -> str:
    return f"USDJPY/{day.year:04d}/{day.month - 1:02d}/{day.day:02d}_ticks.bi5"


def _interval_body_hash(intervals: Sequence[Mapping[str, Any]]) -> str:
    return _sha256(_canonical_bytes(list(intervals)))


def _verify_aggregate(records: Sequence[Mapping[str, Any]]) -> str:
    body = {
        "orderedPartitionRecords": [
            {key: record[key] for key in ("providerPartitionId", "transportStatus", "rawSha256", "parsedTicksSha256", "parsedRecordCount")}
            for record in records
        ]
    }
    return _sha256(_canonical_bytes(body))


def _validate_population(population: Mapping[str, Any]) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    all_rows = population.get("allFrozenRows")
    primary = population.get("primaryMarketScorableRows")
    counts = population.get("populationCounts")
    if not isinstance(all_rows, list) or not isinstance(primary, list) or not isinstance(counts, dict):
        raise S4EvaluationError("FROZEN_POPULATION_SCHEMA_INVALID")
    if len(all_rows) != 24 or len({row.get("eventId") for row in all_rows}) != 24:
        raise S4EvaluationError("FROZEN_POPULATION_IDENTITY_MISMATCH")
    expected_counts = {
        "frozenEventCount": 24,
        "directionalCount": 14,
        "primaryMarketScorableCount": 13,
        "structuralWeekendExclusionCount": 1,
        "neutralCount": 3,
        "unknownAbstainCount": 7,
        "usdPrimaryCount": 5,
        "jpyPrimaryCount": 8,
        "usdSupportivePrimaryCount": 1,
        "usdAdversePrimaryCount": 4,
        "jpySupportivePrimaryCount": 7,
        "jpyAdversePrimaryCount": 1,
    }
    if any(counts.get(key) != value for key, value in expected_counts.items()):
        raise S4EvaluationError("FROZEN_POPULATION_COUNTS_MISMATCH")
    observed_counts = {
        "directionalCount": sum(row.get("pressureState") in ("SUPPORTIVE", "ADVERSE") for row in all_rows),
        "neutralCount": sum(row.get("pressureState") == "NEUTRAL" for row in all_rows),
        "unknownAbstainCount": sum(row.get("analysisDisposition") == "ABSTAIN_UNKNOWN_NOT_DIRECTIONAL" for row in all_rows),
        "structuralWeekendExclusionCount": sum(row.get("analysisDisposition") == "PRIMARY_NONTRADING_WEEKEND_EXCLUSION" for row in all_rows),
    }
    if any(observed_counts[key] != expected_counts[key] for key in observed_counts):
        raise S4EvaluationError("FROZEN_POPULATION_CLASSIFICATION_MISMATCH")
    primary_ids = {row.get("eventId") for row in primary}
    if len(primary) != 13 or len(primary_ids) != 13:
        raise S4EvaluationError("FROZEN_PRIMARY_POPULATION_MISMATCH")
    expected_primary = {row["eventId"] for row in all_rows if row.get("analysisDisposition") == "PRIMARY_DIRECTIONAL"}
    if primary_ids != expected_primary:
        raise S4EvaluationError("FROZEN_PRIMARY_MEMBERSHIP_MISMATCH")
    for row in primary:
        side = row.get("sideIdentity")
        label = row.get("pressureState")
        expected = EXPECTED_DIRECTION.get((side, label))
        if expected is None or row.get("validationExpectedPairDirection") != expected:
            raise S4EvaluationError("FROZEN_DIRECTION_MAPPING_MISMATCH")
        if row.get("identityStatus") != "SINGLE_PASS_VERIFIED":
            raise S4EvaluationError("FROZEN_EVENT_IDENTITY_NOT_VERIFIED")
    return tuple(dict(row) for row in primary), tuple(dict(row) for row in all_rows)


def _validate_intervals(
    intervals: object, primary_events: Sequence[Mapping[str, Any]], interval_hash: str
) -> tuple[dict[str, Any], ...]:
    if not isinstance(intervals, list) or len(intervals) != 39 or _interval_body_hash(intervals) != interval_hash:
        raise S4EvaluationError("FROZEN_INTERVAL_SET_MISMATCH")
    by_id: dict[tuple[str, str], dict[str, Any]] = {}
    event_ids = {event["eventId"] for event in primary_events}
    expected_counts = {"ACTUAL": 13, "MINUS_7": 13, "PLUS_7": 13}
    counts = {horizon: 0 for horizon in HORIZON_DAYS}
    for interval in intervals:
        if not isinstance(interval, dict):
            raise S4EvaluationError("FROZEN_INTERVAL_SCHEMA_INVALID")
        event_id = interval.get("eventId")
        horizon = interval.get("horizon")
        if event_id not in event_ids or horizon not in HORIZON_DAYS or interval.get("intervalId") != f"{event_id}::{horizon}":
            raise S4EvaluationError("FROZEN_INTERVAL_IDENTITY_MISMATCH")
        key = (event_id, horizon)
        if key in by_id:
            raise S4EvaluationError("FROZEN_INTERVAL_DUPLICATE")
        start = _utc_datetime(interval.get("applyingStartUtc"))
        end = _utc_datetime(interval.get("separatingEndUtc"))
        if start >= end or interval.get("halfOpen") is not True:
            raise S4EvaluationError("FROZEN_INTERVAL_BOUNDARY_INVALID")
        if interval.get("durationSeconds") != int((end - start).total_seconds()):
            raise S4EvaluationError("FROZEN_INTERVAL_DURATION_MISMATCH")
        if interval.get("sideIdentity") not in ("USD", "JPY") or interval.get("frozenLabel") not in ("SUPPORTIVE", "ADVERSE"):
            raise S4EvaluationError("FROZEN_INTERVAL_DIRECTIONAL_INPUT_INVALID")
        source_event = next((event for event in primary_events if event["eventId"] == event_id), None)
        if source_event is None or interval.get("sideIdentity") != source_event.get("sideIdentity") or interval.get("frozenLabel") != source_event.get("pressureState"):
            raise S4EvaluationError("FROZEN_INTERVAL_EVENT_BINDING_MISMATCH")
        by_id[key] = dict(interval)
        counts[horizon] += 1
    if counts != expected_counts or len(by_id) != 39:
        raise S4EvaluationError("FROZEN_INTERVAL_HORIZON_COUNTS_MISMATCH")
    if set(by_id) != {(event["eventId"], horizon) for event in primary_events for horizon in HORIZON_DAYS}:
        raise S4EvaluationError("FROZEN_INTERVAL_COVERAGE_MISMATCH")
    for event in primary_events:
        event_id = event["eventId"]
        actual = by_id[(event_id, "ACTUAL")]
        actual_start = _utc_datetime(actual["applyingStartUtc"])
        actual_end = _utc_datetime(actual["separatingEndUtc"])
        for horizon, shift_days in HORIZON_DAYS.items():
            current = by_id[(event_id, horizon)]
            expected_start = actual_start + timedelta(days=shift_days)
            expected_end = actual_end + timedelta(days=shift_days)
            if _utc_datetime(current["applyingStartUtc"]) != expected_start or _utc_datetime(current["separatingEndUtc"]) != expected_end:
                raise S4EvaluationError("FROZEN_SHIFTED_INTERVAL_MISMATCH")
            for field in ("sideIdentity", "frozenLabel", "durationSeconds"):
                if current.get(field) != actual.get(field):
                    raise S4EvaluationError("FROZEN_SHIFTED_INTERVAL_METADATA_MISMATCH")
            if current.get("shiftCalendarDays") != shift_days:
                raise S4EvaluationError("FROZEN_SHIFTED_INTERVAL_OFFSET_MISMATCH")
    return tuple(dict(interval) for interval in intervals)


def _validate_clusters(clusters: Mapping[str, Any], primary_events: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    rows = clusters.get("clusters")
    if not isinstance(rows, list) or [row.get("clusterId") for row in rows] != ["C1", "C2", "C3", "C4"]:
        raise S4EvaluationError("FROZEN_CLUSTER_SCHEMA_INVALID")
    if [row.get("memberCount") for row in rows] != [5, 1, 2, 5]:
        raise S4EvaluationError("FROZEN_CLUSTER_SIZES_MISMATCH")
    members = [event_id for row in rows for event_id in row.get("memberEventIds", [])]
    expected = [event["eventId"] for event in primary_events]
    if len(members) != 13 or len(set(members)) != 13 or set(members) != set(expected):
        raise S4EvaluationError("FROZEN_CLUSTER_MEMBERSHIP_MISMATCH")
    return tuple(dict(row) for row in rows)


def _validate_partition_plan(
    plan: Mapping[str, Any], intervals: Sequence[Mapping[str, Any]], expected_hash: str
) -> tuple[dict[str, Any], ...]:
    partitions = plan.get("partitions")
    if not isinstance(partitions, list) or len(partitions) != 15:
        raise S4EvaluationError("FROZEN_PARTITION_PLAN_MISMATCH")
    by_key: dict[str, dict[str, Any]] = {}
    for item in partitions:
        if not isinstance(item, dict):
            raise S4EvaluationError("FROZEN_PARTITION_SCHEMA_INVALID")
        start = _utc_datetime(item.get("nativeStartUtc"), error_code="FROZEN_PARTITION_SCHEMA_INVALID")
        end = _utc_datetime(item.get("nativeEndUtc"), error_code="FROZEN_PARTITION_SCHEMA_INVALID")
        key = item.get("requestIdentity", {}).get("key")
        if end - start != timedelta(days=1) or item.get("instrument") != "USDJPY" or key != _daily_key(start.date()):
            raise S4EvaluationError("FROZEN_PARTITION_IDENTITY_MISMATCH")
        if key in by_key:
            raise S4EvaluationError("FROZEN_PARTITION_DUPLICATE")
        by_key[key] = dict(item)
    if len(by_key) != 15:
        raise S4EvaluationError("FROZEN_PARTITION_PLAN_MISMATCH")
    relevant_days: set[date] = set()
    for interval in intervals:
        cursor = _utc_datetime(interval["applyingStartUtc"]).replace(hour=0, minute=0, second=0, microsecond=0)
        end = _utc_datetime(interval["separatingEndUtc"])
        while cursor < end:
            relevant_days.add(cursor.date())
            cursor += timedelta(days=1)
    if {_daily_key(day) for day in relevant_days} - set(by_key):
        raise S4EvaluationError("FROZEN_PARTITION_INTERVAL_COVERAGE_MISMATCH")
    # Bind to the committed canonical plan identity, not a reconstructed variant.
    if plan.get("providerPartitionPlanHash") != expected_hash:
        raise S4EvaluationError("FROZEN_PARTITION_PLAN_HASH_MISMATCH")
    return tuple(dict(item) for item in partitions)


def _validate_manifest(
    manifest: Mapping[str, Any], partitions: Sequence[Mapping[str, Any]], expected_hash: str, expected_aggregate: str
) -> tuple[dict[str, Any], ...]:
    if manifest.get("rawAcquisitionManifestHash") != expected_hash:
        raise S4EvaluationError("ACQUISITION_MANIFEST_HASH_MISMATCH")
    rows = manifest.get("partitionRecords")
    if not isinstance(rows, list) or len(rows) != 15:
        raise S4EvaluationError("ACQUISITION_MANIFEST_PARTITION_COUNT_MISMATCH")
    if manifest.get("getObjectCallCount") != 15 or manifest.get("executionCommit") != "ade2d4f8208eddd0f90168b76c92565f369ce7ac":
        raise S4EvaluationError("ACQUISITION_MANIFEST_EXECUTION_BINDING_MISMATCH")
    seen_names: set[str] = set()
    for row, partition in zip(rows, partitions):
        identity = partition["requestIdentity"]
        name = row.get("logicalParsedCaptureName")
        if (
            row.get("providerPartitionId") != partition.get("providerPartitionId")
            or row.get("nativeStartUtc") != partition.get("nativeStartUtc")
            or row.get("nativeEndUtc") != partition.get("nativeEndUtc")
            or row.get("instrument") != "USDJPY"
            or row.get("transportStatus") != "GET_OBJECT_SUCCESS"
            or row.get("acquisitionDisposition") != "SUCCESSFUL_RAW_AND_FROZEN_PARSED_CAPTURE"
            or row.get("requestParameters") != {
                "bucket": identity.get("bucket"), "key": identity.get("key"),
                "region": identity.get("region"), "requestPayer": identity.get("requestPayer"),
            }
            or not isinstance(name, str)
            or Path(name).name != name
            or not name.endswith(".jsonl")
            or name in seen_names
            or not isinstance(row.get("parsedTicksSha256"), str)
            or not re.fullmatch(r"[0-9A-F]{64}", row["parsedTicksSha256"])
            or not isinstance(row.get("parsedRecordCount"), int)
            or isinstance(row.get("parsedRecordCount"), bool)
            or row["parsedRecordCount"] < 1
        ):
            raise S4EvaluationError("ACQUISITION_MANIFEST_PARTITION_BINDING_MISMATCH")
        seen_names.add(name)
    if _verify_aggregate(rows) != expected_aggregate:
        raise S4EvaluationError("ACQUISITION_AGGREGATE_HASH_MISMATCH")
    return tuple(dict(row) for row in rows)


def load_frozen_study(project_root: Path = PROJECT_ROOT) -> FrozenStudy:
    """Validate committed study identities without touching private captures."""
    root = Path(project_root).resolve()
    prereg = _read_artifact(root, "preregistration")
    acquisition = _read_artifact(root, "acquisitionContract")
    parser_contract = _read_artifact(root, "parserContract")
    population = _read_artifact(root, "population")
    cluster_artifact = _read_artifact(root, "clusters")
    invariance = _read_artifact(root, "invariance")
    plan = _read_artifact(root, "partitionPlan")
    manifest = _read_artifact(root, "manifest")
    gate = _read_artifact(root, "freezeGate")
    astra = _read_artifact(root, "astraDisposition")

    identities = {
        "preregistrationHash": _self_hash(prereg, "preregistrationHash", FREEZE_HASHES["preregistrationHash"], "preregistration"),
        "acquisitionContractHash": _self_hash(acquisition, "marketDataAcquisitionContractHash", FREEZE_HASHES["acquisitionContractHash"], "acquisition contract"),
        "parserContractHash": _self_hash(parser_contract, "parserContractHash", FREEZE_HASHES["parserContractHash"], "parser contract"),
        "primaryPopulationHash": _self_hash(population, "primaryPopulationHash", FREEZE_HASHES["primaryPopulationHash"], "primary population"),
        "overlapClustersHash": _self_hash(cluster_artifact, "overlapClustersHash", FREEZE_HASHES["overlapClustersHash"], "clusters"),
        "analysisPlanInvarianceHash": _self_hash(invariance, "analysisPlanInvarianceAuditHash", FREEZE_HASHES["analysisPlanInvarianceAuditHash"], "analysis plan invariance"),
        "partitionPlanHash": _self_hash(plan, "providerPartitionPlanHash", FREEZE_HASHES["partitionPlanHash"], "partition plan"),
        "acquisitionManifestHash": _self_hash(manifest, "rawAcquisitionManifestHash", FREEZE_HASHES["acquisitionManifestHash"], "acquisition manifest"),
        "acquisitionFreezeGateHash": _self_hash(gate, "acquisitionFreezeGateHash", FREEZE_HASHES["acquisitionFreezeGateHash"], "acquisition freeze gate"),
        "astraDispositionHash": _self_hash(astra, "astraAcquisitionAuditDispositionHash", FREEZE_HASHES["astraDispositionHash"], "Astra disposition"),
    }
    intervals = acquisition.get("frozenIntervalSet", {}).get("intervals")
    identities["analysisIntervalSetHash"] = _interval_body_hash(intervals) if isinstance(intervals, list) else ""
    if identities["analysisIntervalSetHash"] != FREEZE_HASHES["analysisIntervalSetHash"]:
        raise S4EvaluationError("FROZEN_INTERVAL_SET_HASH_MISMATCH")
    if any(
        (
            population.get("preregistrationHash") != FREEZE_HASHES["preregistrationHash"],
            cluster_artifact.get("primaryPopulationHash") != FREEZE_HASHES["primaryPopulationHash"],
            invariance.get("preregistrationHash") != FREEZE_HASHES["preregistrationHash"],
            invariance.get("primaryPopulationHash") != FREEZE_HASHES["primaryPopulationHash"],
            invariance.get("overlapClustersHash") != FREEZE_HASHES["overlapClustersHash"],
            prereg.get("marketDataAcquisitionContractHash") != FREEZE_HASHES["acquisitionContractHash"],
            prereg.get("providerPartitionPlanHash") != FREEZE_HASHES["partitionPlanHash"],
        )
    ):
        raise S4EvaluationError("PREREGISTRATION_BINDING_MISMATCH")
    if acquisition.get("parserContractHash") != FREEZE_HASHES["parserContractHash"] or acquisition.get("parserSourceSha256") != parser_contract.get("parserSourceSha256"):
        raise S4EvaluationError("PARSER_BINDING_MISMATCH")
    parser_source = root / "gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3_r2.py"
    acquisition_source = root / "gann-astro-desk/backend/market_data_acquisition_s4_a1.py"
    if _sha256_file(parser_source) != FREEZE_HASHES["parserSourceSha256"] or _sha256_file(acquisition_source) != FREEZE_HASHES["acquisitionSourceSha256"]:
        raise S4EvaluationError("FROZEN_SOURCE_SHA_MISMATCH")
    identities["parserSourceSha256"] = FREEZE_HASHES["parserSourceSha256"]
    identities["acquisitionSourceSha256"] = FREEZE_HASHES["acquisitionSourceSha256"]
    if gate.get("outcomeUnlocked") is not False or gate.get("S4OutcomeAnalysisAllowed") is not False or gate.get("executionAllowed") is not False:
        raise S4EvaluationError("ACQUISITION_FREEZE_GATE_NOT_LOCKED")
    if gate.get("rawAcquisitionManifestHash") != FREEZE_HASHES["acquisitionManifestHash"] or gate.get("aggregateCaptureHash") != FREEZE_HASHES["aggregateCaptureHash"]:
        raise S4EvaluationError("ACQUISITION_FREEZE_GATE_BINDING_MISMATCH")
    identities["aggregateCaptureHash"] = FREEZE_HASHES["aggregateCaptureHash"]
    if astra.get("verdict") != "ACQUISITION_PROVENANCE_AUDIT_PASS" or astra.get("outcomeUnlocked") is not False:
        raise S4EvaluationError("ASTRA_ACQUISITION_AUDIT_NOT_PASS")
    if astra.get("nextGate") != EXPECTED_OUTCOME_AUTHORIZATION or astra.get("executionAllowed") is not False:
        raise S4EvaluationError("ASTRA_NEXT_GATE_MISMATCH")
    firewall = astra.get("outcomeFirewall", {})
    if firewall.get("OUTCOME_DATA_READ") is not False or firewall.get("S4OutcomeAnalysisPerformed") is not False:
        raise S4EvaluationError("ASTRA_OUTCOME_FIREWALL_NOT_LOCKED")

    primary, all_events = _validate_population(population)
    validated_intervals = _validate_intervals(intervals, primary, FREEZE_HASHES["analysisIntervalSetHash"])
    validated_clusters = _validate_clusters(cluster_artifact, primary)
    validated_partitions = _validate_partition_plan(plan, validated_intervals, FREEZE_HASHES["partitionPlanHash"])
    manifest_records = _validate_manifest(
        manifest, validated_partitions, FREEZE_HASHES["acquisitionManifestHash"], FREEZE_HASHES["aggregateCaptureHash"]
    )
    if sum(row["parsedRecordCount"] for row in manifest_records) != 3_947_368:
        raise S4EvaluationError("ACQUISITION_PARSED_TOTAL_MISMATCH")
    return FrozenStudy(primary, all_events, validated_intervals, validated_clusters, validated_partitions, manifest_records, identities)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise S4EvaluationError("PARSED_JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> None:
    raise S4EvaluationError("PARSED_JSON_NONFINITE_VALUE")


def _parse_tick_line(line: bytes, expected_partition_id: str, expected_day: date, expected_index: int) -> ParsedTick:
    if not line.endswith(b"\n") or line.endswith(b"\r\n"):
        raise S4EvaluationError("PARSED_JSONL_CANONICALIZATION_INVALID")
    try:
        record = json.loads(line, object_pairs_hook=_strict_object, parse_constant=_reject_json_constant)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise S4EvaluationError("PARSED_JSONL_SYNTAX_INVALID") from exc
    if not isinstance(record, dict) or set(record) != PARSED_FIELDS:
        raise S4EvaluationError("PARSED_RECORD_SCHEMA_INVALID")
    if _canonical_bytes(record) + b"\n" != line:
        raise S4EvaluationError("PARSED_JSONL_CANONICALIZATION_INVALID")
    if record.get("partitionId") != expected_partition_id:
        raise S4EvaluationError("PARSED_PARTITION_ID_MISMATCH")
    index = record.get("recordIndex")
    if not isinstance(index, int) or isinstance(index, bool) or index != expected_index:
        raise S4EvaluationError("PARSED_RECORD_ORDER_INVALID")
    timestamp_text = record.get("timestampUtc")
    if not isinstance(timestamp_text, str) or not UTC_MILLISECOND_PATTERN.fullmatch(timestamp_text):
        raise S4EvaluationError("DATA_TIMESTAMP_INVALID", "parsed timestamp must use canonical UTC millisecond form")
    timestamp = _utc_datetime(timestamp_text, error_code="DATA_TIMESTAMP_INVALID")
    if timestamp.date() != expected_day:
        raise S4EvaluationError("PARSED_TIMESTAMP_OUTSIDE_PARTITION")
    ask = record.get("askNative")
    bid = record.get("bidNative")
    if any(not isinstance(value, int) or isinstance(value, bool) for value in (ask, bid)):
        raise S4EvaluationError("PARSED_QUOTE_SCHEMA_INVALID")
    for field in ("askVolumeBitsHex", "bidVolumeBitsHex"):
        value = record.get(field)
        if not isinstance(value, str) or not VOLUME_BITS_PATTERN.fullmatch(value):
            raise S4EvaluationError("PARSED_VOLUME_SCHEMA_INVALID")
    return ParsedTick(expected_partition_id, index, timestamp, ask, bid)


def _iter_parsed_file(path: Path, partition_id: str, day: date) -> Iterator[ParsedTick]:
    previous_timestamp: datetime | None = None
    with path.open("rb") as stream:
        for expected_index, line in enumerate(stream):
            tick = _parse_tick_line(line, partition_id, day, expected_index)
            if previous_timestamp is not None and tick.timestamp_utc < previous_timestamp:
                raise S4EvaluationError("PARSED_RECORD_ORDER_INVALID")
            previous_timestamp = tick.timestamp_utc
            yield tick


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _validate_parsed_root(parsed_root: Path, manifest_records: Sequence[Mapping[str, Any]], project_root: Path) -> dict[str, Path]:
    root = parsed_root.resolve()
    project = project_root.resolve()
    if root == project or root.is_relative_to(project):
        raise S4EvaluationError("UNSAFE_PRIVATE_CAPTURE_ROOT")
    try:
        entries = list(root.iterdir())
    except OSError as exc:
        raise S4EvaluationError("PARSED_CAPTURE_ROOT_UNAVAILABLE") from exc
    expected_names = {str(record["logicalParsedCaptureName"]) for record in manifest_records}
    if any(entry.is_symlink() or not entry.is_file() for entry in entries) or {entry.name for entry in entries} != expected_names:
        raise S4EvaluationError("UNLISTED_OR_MISSING_PARSED_CAPTURE")
    return {name: root / name for name in expected_names}


def _verify_all_capture_hashes(paths: Mapping[str, Path], manifest_records: Sequence[Mapping[str, Any]]) -> None:
    expected = {str(row["logicalParsedCaptureName"]): str(row["parsedTicksSha256"]) for row in manifest_records}
    if set(paths) != set(expected):
        raise S4EvaluationError("UNLISTED_OR_MISSING_PARSED_CAPTURE")
    for name in sorted(expected):
        if _sha256_file(paths[name]) != expected[name]:
            raise S4EvaluationError("PARSED_CAPTURE_HASH_MISMATCH", name)


class _IntervalAccumulator:
    def __init__(self, interval: Mapping[str, Any]) -> None:
        self.interval = interval
        self.start = _utc_datetime(interval["applyingStartUtc"])
        self.end = _utc_datetime(interval["separatingEndUtc"])
        self.first: ParsedTick | None = None
        self.last: ParsedTick | None = None
        self.distinct_valid_timestamps = 0
        self.conflict = False
        self.invalid_quote = False
        self._current_timestamp: datetime | None = None
        self._current_quote: tuple[int, int] | None = None

    def add(self, tick: ParsedTick) -> None:
        if not self.start <= tick.timestamp_utc < self.end:
            return
        quote = (tick.bid_native, tick.ask_native)
        if self._current_timestamp == tick.timestamp_utc:
            if self._current_quote != quote:
                self.conflict = True
            return
        self._current_timestamp = tick.timestamp_utc
        self._current_quote = quote
        bid, ask = quote
        if bid <= 0 or ask <= 0 or ask < bid:
            self.invalid_quote = True
            return
        if self.first is None:
            self.first = tick
        self.last = tick
        self.distinct_valid_timestamps += 1

    def finish(self) -> dict[str, Any]:
        interval = self.interval
        side = str(interval["sideIdentity"])
        label = str(interval["frozenLabel"])
        expected_direction = EXPECTED_DIRECTION[(side, label)]
        base = {
            "intervalId": interval["intervalId"],
            "eventId": interval["eventId"],
            "horizon": interval["horizon"],
            "sideIdentity": side,
            "frozenLabel": label,
            "expectedDirection": expected_direction,
            "scorable": False,
            "status": "DATA_UNSCORABLE",
            "startTimestampUtc": None,
            "endTimestampUtc": None,
            "logReturn": None,
            "hit": None,
        }
        if self.conflict:
            base["status"] = "DATA_CONFLICT_UNSCORABLE"
            return base
        if self.invalid_quote:
            base["status"] = "DATA_NUMERIC_INVALID_UNSCORABLE"
            return base
        if self.distinct_valid_timestamps < 2 or self.first is None or self.last is None:
            return base
        try:
            start_mid = _native_midpoint(self.first.bid_native, self.first.ask_native)
            end_mid = _native_midpoint(self.last.bid_native, self.last.ask_native)
            with localcontext() as context:
                context.prec = NUMERIC_PRECISION
                context.rounding = NUMERIC_ROUNDING
                value = (end_mid / start_mid).ln()
            if not value.is_finite():
                raise ArithmeticError
        except (ArithmeticError, ValueError, InvalidOperation):
            base["status"] = "DATA_NUMERIC_INVALID_UNSCORABLE"
            return base
        q = EXPECTED_Q[expected_direction]
        signed = value * q
        hit = int(signed > 0)
        base.update(
            {
                "scorable": True,
                "status": "ZERO_MOVE" if value == 0 else "SCORED",
                "startTimestampUtc": _format_utc(self.first.timestamp_utc),
                "endTimestampUtc": _format_utc(self.last.timestamp_utc),
                "logReturn": _decimal_text(value),
                "hit": hit,
            }
        )
        return base


def _native_midpoint(bid_native: int, ask_native: int) -> Decimal:
    """Price=(bid+ask)/(2*1000), using exact Decimal arithmetic; divisor cancels in log return."""
    if bid_native <= 0 or ask_native <= 0 or ask_native < bid_native:
        raise InvalidOperation
    with localcontext() as context:
        context.prec = NUMERIC_PRECISION
        context.rounding = NUMERIC_ROUNDING
        value = (Decimal(bid_native) + Decimal(ask_native)) / Decimal(2 * USDJPY_NATIVE_DIVISOR)
    if not value.is_finite() or value <= 0:
        raise InvalidOperation
    return value


def _decimal_text(value: Decimal) -> str:
    if not value.is_finite():
        raise S4EvaluationError("DATA_NUMERIC_INVALID_UNSCORABLE")
    return format(value, "f")


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def score_interval(interval: Mapping[str, Any], ticks: Iterable[ParsedTick]) -> dict[str, Any]:
    """Score one synthetic or already-validated interval stream with half-open bounds."""
    accumulator = _IntervalAccumulator(interval)
    previous: datetime | None = None
    for tick in ticks:
        if previous is not None and tick.timestamp_utc < previous:
            raise S4EvaluationError("PARSED_RECORD_ORDER_INVALID")
        previous = tick.timestamp_utc
        accumulator.add(tick)
    return accumulator.finish()


def _interval_dates(interval: Mapping[str, Any]) -> Iterator[date]:
    cursor = _utc_datetime(interval["applyingStartUtc"]).replace(hour=0, minute=0, second=0, microsecond=0)
    end = _utc_datetime(interval["separatingEndUtc"])
    while cursor < end:
        yield cursor.date()
        cursor += timedelta(days=1)


def evaluate_interval_streams(study: FrozenStudy, parsed_root: Path, project_root: Path = PROJECT_ROOT) -> tuple[dict[str, Any], ...]:
    """Internal deterministic interval adapter; caller must verify hashes before invoking."""
    paths = _validate_parsed_root(parsed_root, study.manifest_records, project_root)
    # Integrity pass over every file finishes before any JSONL line is interpreted.
    _verify_all_capture_hashes(paths, study.manifest_records)
    partitions_by_day = {
        _utc_datetime(partition["nativeStartUtc"]).date(): partition
        for partition in study.partitions
    }
    intervals_by_day: dict[date, list[Mapping[str, Any]]] = {}
    for interval in study.intervals:
        for day in _interval_dates(interval):
            if day not in partitions_by_day:
                raise S4EvaluationError("FROZEN_PARTITION_INTERVAL_COVERAGE_MISMATCH")
            intervals_by_day.setdefault(day, []).append(interval)
    accumulators = {interval["intervalId"]: _IntervalAccumulator(interval) for interval in study.intervals}
    for record, partition in zip(study.manifest_records, study.partitions):
        day = _utc_datetime(partition["nativeStartUtc"]).date()
        partition_id = partition["requestIdentity"]["key"]
        path = paths[record["logicalParsedCaptureName"]]
        parsed_count = 0
        for tick in _iter_parsed_file(path, partition_id, day):
            parsed_count += 1
            for interval in intervals_by_day.get(day, ()):
                accumulators[interval["intervalId"]].add(tick)
        if parsed_count != record["parsedRecordCount"]:
            raise S4EvaluationError("PARSED_RECORD_COUNT_MISMATCH", str(record["logicalParsedCaptureName"]))
    return tuple(accumulators[interval["intervalId"]].finish() for interval in study.intervals)


def _ratio(numerator: int, denominator: int) -> str:
    with localcontext() as context:
        context.prec = NUMERIC_PRECISION
        context.rounding = NUMERIC_ROUNDING
        return _decimal_text(Decimal(numerator) / Decimal(denominator))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _validate_interval_results(study: FrozenStudy, interval_results: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    if len(interval_results) != 39:
        raise S4EvaluationError("EVALUATION_INTERVAL_COUNT_MISMATCH")
    expected = {interval["intervalId"]: interval for interval in study.intervals}
    by_id: dict[str, dict[str, Any]] = {}
    for result in interval_results:
        if not isinstance(result, Mapping) or result.get("intervalId") not in expected:
            raise S4EvaluationError("EVALUATION_INTERVAL_IDENTITY_MISMATCH")
        interval_id = str(result["intervalId"])
        if interval_id in by_id:
            raise S4EvaluationError("EVALUATION_INTERVAL_DUPLICATE")
        source = expected[interval_id]
        if any(result.get(field) != source.get(field) for field in ("eventId", "horizon", "sideIdentity", "frozenLabel")):
            raise S4EvaluationError("EVALUATION_INTERVAL_BINDING_MISMATCH")
        expected_direction = EXPECTED_DIRECTION[(source["sideIdentity"], source["frozenLabel"])]
        if result.get("expectedDirection") != expected_direction:
            raise S4EvaluationError("EVALUATION_DIRECTION_MISMATCH")
        if result.get("scorable") is True:
            if result.get("status") not in ("SCORED", "ZERO_MOVE") or type(result.get("hit")) is not int or result.get("hit") not in (0, 1) or not isinstance(result.get("logReturn"), str):
                raise S4EvaluationError("EVALUATION_RESULT_SCHEMA_INVALID")
            try:
                ret = Decimal(result["logReturn"])
            except InvalidOperation as exc:
                raise S4EvaluationError("EVALUATION_RESULT_SCHEMA_INVALID") from exc
            if not ret.is_finite() or (result["status"] == "ZERO_MOVE") != (ret == 0):
                raise S4EvaluationError("EVALUATION_RESULT_SCHEMA_INVALID")
            interval_start = _utc_datetime(source["applyingStartUtc"])
            interval_end = _utc_datetime(source["separatingEndUtc"])
            if any(not isinstance(result.get(field), str) or not UTC_MILLISECOND_PATTERN.fullmatch(result[field]) for field in ("startTimestampUtc", "endTimestampUtc")):
                raise S4EvaluationError("EVALUATION_RESULT_SCHEMA_INVALID")
            start_tick = _utc_datetime(result.get("startTimestampUtc"), error_code="EVALUATION_RESULT_SCHEMA_INVALID")
            end_tick = _utc_datetime(result.get("endTimestampUtc"), error_code="EVALUATION_RESULT_SCHEMA_INVALID")
            if not interval_start <= start_tick < end_tick < interval_end:
                raise S4EvaluationError("EVALUATION_ENDPOINT_OUTSIDE_INTERVAL")
            should_hit = int(EXPECTED_Q[expected_direction] * ret > 0)
            if result["hit"] != should_hit:
                raise S4EvaluationError("EVALUATION_HIT_RETURN_MISMATCH")
        elif result.get("scorable") is False:
            if (
                result.get("status") not in ("DATA_UNSCORABLE", "DATA_CONFLICT_UNSCORABLE", "DATA_NUMERIC_INVALID_UNSCORABLE")
                or result.get("hit") is not None
                or result.get("logReturn") is not None
                or result.get("startTimestampUtc") is not None
                or result.get("endTimestampUtc") is not None
            ):
                raise S4EvaluationError("EVALUATION_RESULT_SCHEMA_INVALID")
        else:
            raise S4EvaluationError("EVALUATION_RESULT_SCHEMA_INVALID")
        by_id[interval_id] = dict(result)
    if set(by_id) != set(expected):
        raise S4EvaluationError("EVALUATION_INTERVAL_COVERAGE_MISMATCH")
    return by_id


def _permutation_result(
    primary: Sequence[Mapping[str, Any]], actual_by_event: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    def frozen_label(row: Mapping[str, Any]) -> Any:
        return row.get("frozenLabel", row.get("pressureState"))

    side_rows = {
        side: [row for row in primary if row["sideIdentity"] == side]
        for side in ("USD", "JPY")
    }
    usd_supportive_count = sum(frozen_label(row) == "SUPPORTIVE" for row in side_rows["USD"])
    jpy_supportive_count = sum(frozen_label(row) == "SUPPORTIVE" for row in side_rows["JPY"])
    if (len(side_rows["USD"]), usd_supportive_count, len(side_rows["JPY"]), jpy_supportive_count) != (5, 1, 8, 7):
        raise S4EvaluationError("PERMUTATION_LABEL_COUNTS_MISMATCH")
    event_ids = {row["eventId"] for row in primary}
    if set(actual_by_event) != event_ids or any(
        row.get("scorable") is not True
        or row.get("status") not in ("SCORED", "ZERO_MOVE")
        or type(row.get("hit")) is not int
        or row.get("hit") not in (0, 1)
        or not isinstance(row.get("logReturn"), str)
        for row in actual_by_event.values()
    ):
        raise S4EvaluationError("PERMUTATION_ACTUAL_ROWS_INVALID")
    for event in primary:
        result = actual_by_event[event["eventId"]]
        label = frozen_label(event)
        direction = EXPECTED_DIRECTION[(event["sideIdentity"], label)]
        try:
            ret = Decimal(result["logReturn"])
        except InvalidOperation as exc:
            raise S4EvaluationError("PERMUTATION_ACTUAL_ROWS_INVALID") from exc
        if (
            not ret.is_finite()
            or result.get("eventId") != event["eventId"]
            or result.get("sideIdentity") != event["sideIdentity"]
            or result.get("frozenLabel") != label
            or result.get("expectedDirection") != direction
            or result.get("hit") != int(EXPECTED_Q[direction] * ret > 0)
            or (result.get("status") == "ZERO_MOVE") != (ret == 0)
        ):
            raise S4EvaluationError("PERMUTATION_ACTUAL_ROWS_INVALID")
    assignments: list[dict[str, Any]] = []
    observed_supportive = {
        side: tuple(row["eventId"] for row in side_rows[side] if frozen_label(row) == "SUPPORTIVE")
        for side in ("USD", "JPY")
    }
    observed_index: int | None = None
    for usd_set, jpy_set in product(
        combinations([row["eventId"] for row in side_rows["USD"]], usd_supportive_count),
        combinations([row["eventId"] for row in side_rows["JPY"]], jpy_supportive_count),
    ):
        supportive = {"USD": set(usd_set), "JPY": set(jpy_set)}
        permutation_hits = 0
        for side, rows in side_rows.items():
            for row in rows:
                label = "SUPPORTIVE" if row["eventId"] in supportive[side] else "ADVERSE"
                expected_direction = EXPECTED_DIRECTION[(side, label)]
                q = EXPECTED_Q[expected_direction]
                actual_return = Decimal(actual_by_event[row["eventId"]]["logReturn"])
                permutation_hits += int(q * actual_return > 0)
        assignment = {
            "usdSupportiveEventIds": list(usd_set),
            "jpySupportiveEventIds": list(jpy_set),
            "permutationHitCount": permutation_hits,
        }
        if set(usd_set) == set(observed_supportive["USD"]) and set(jpy_set) == set(observed_supportive["JPY"]):
            observed_index = len(assignments)
        assignments.append(assignment)
    if len(assignments) != 40 or observed_index is None:
        raise S4EvaluationError("PERMUTATION_UNIVERSE_INVALID")
    observed = sum(int(actual_by_event[event_id]["hit"]) for event_id in event_ids)
    histogram = [
        {"hitCount": value, "assignmentCount": sum(item["permutationHitCount"] == value for item in assignments)}
        for value in range(14)
    ]
    tail = sum(item["permutationHitCount"] >= observed for item in assignments)
    return {
        "assignmentCount": 40,
        "observedAssignmentIndex": observed_index,
        "observedHitCount": observed,
        "allAssignments": assignments,
        "histogram": histogram,
        "inclusiveTailCount": tail,
        "pExact": _ratio(tail, 40),
    }


def _cluster_result(
    clusters: Sequence[Mapping[str, Any]], hits: Mapping[str, int]
) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    rates: list[Fraction] = []
    for cluster in clusters:
        event_ids = list(cluster["memberEventIds"])
        count = sum(hits[event_id] for event_id in event_ids)
        rate = Fraction(count, len(event_ids))
        rates.append(rate)
        summaries.append(
            {
                "clusterId": cluster["clusterId"],
                "eventCount": len(event_ids),
                "hitCount": count,
                "hitRateFraction": _fraction_text(rate),
                "hitRate": _ratio(rate.numerator, rate.denominator),
            }
        )
    balanced = sum(rates, Fraction(0, 1)) / 4
    return {
        "clusterCount": 4,
        "clusters": summaries,
        "equalWeightedHitRateFraction": _fraction_text(balanced),
        "equalWeightedHitRate": _ratio(balanced.numerator, balanced.denominator),
        "secondaryPValue": None,
    }


def _side_descriptives(primary: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for side, denominator in (("USD", 5), ("JPY", 8)):
        rows = [row for row in primary if row["sideIdentity"] == side]
        with localcontext() as context:
            context.prec = NUMERIC_PRECISION
            context.rounding = NUMERIC_ROUNDING
            signed_returns = [Decimal(row["logReturn"]) * EXPECTED_Q[row["expectedDirection"]] for row in rows]
            mean = sum(signed_returns, Decimal(0)) / Decimal(denominator)
            ordered = sorted(signed_returns)
            middle = len(ordered) // 2
            med = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / Decimal(2)
        hits = sum(int(row["hit"]) for row in rows)
        output[side] = {
            "hitCount": hits,
            "eventCount": denominator,
            "hitRate": _ratio(hits, denominator),
            "meanExpectedSignedLogReturn": _decimal_text(mean),
            "medianExpectedSignedLogReturn": _decimal_text(med),
            "classification": "DESCRIPTIVE_ONLY",
        }
    return output


def _timing_result(by_id: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int | None] = {}
    for horizon in HORIZON_DAYS:
        rows = [row for row in by_id.values() if row["horizon"] == horizon]
        if len(rows) != 13 or not all(row["scorable"] for row in rows):
            counts[horizon] = None
        else:
            counts[horizon] = sum(int(row["hit"]) for row in rows)
    if any(value is None for value in counts.values()):
        status = "TIMING_DIAGNOSTIC_INCOMPLETE"
    elif counts["ACTUAL"] > counts["MINUS_7"] and counts["ACTUAL"] > counts["PLUS_7"]:
        status = "TIMING_SPECIFICITY_DEMONSTRATED_WITHIN_PREREGISTERED_DIAGNOSTIC"
    else:
        status = "TIMING_SPECIFICITY_NOT_DEMONSTRATED"
    return {"status": status, "hitCounts": counts, "secondaryPValue": None}


def _build_result_body(study: FrozenStudy, interval_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_id = _validate_interval_results(study, interval_results)
    actual = [by_id[f"{event['eventId']}::ACTUAL"] for event in study.primary_events]
    actual_complete = len(actual) == 13 and all(row["scorable"] for row in actual)
    timing = _timing_result(by_id)
    if not actual_complete:
        primary_result = {
            "status": "PRIMARY_EVALUATION_INVALID_DATA_INCOMPLETE",
            "scorableEventCount": sum(row["scorable"] for row in actual),
            "denominator": 13,
            "observedHitCount": None,
            "primaryHitRate": None,
        }
        permutation = {"assignmentCount": 40, "observedAssignmentIndex": None, "observedHitCount": None, "allAssignments": [], "histogram": [], "inclusiveTailCount": None, "pExact": None}
        cluster = {"clusterCount": 4, "clusters": [], "equalWeightedHitRateFraction": None, "equalWeightedHitRate": None, "secondaryPValue": None}
        sides = {side: {"hitCount": None, "eventCount": count, "hitRate": None, "meanExpectedSignedLogReturn": None, "medianExpectedSignedLogReturn": None, "classification": "DESCRIPTIVE_ONLY_INVALID_PRIMARY"} for side, count in (("USD", 5), ("JPY", 8))}
        survival = "PRIMARY_EVALUATION_INVALID_DATA_INCOMPLETE"
    else:
        hits = {row["eventId"]: int(row["hit"]) for row in actual}
        observed = sum(hits.values())
        hit_rate = Fraction(observed, 13)
        primary_result = {
            "status": "COMPLETE",
            "scorableEventCount": 13,
            "denominator": 13,
            "observedHitCount": observed,
            "primaryHitRate": _ratio(hit_rate.numerator, hit_rate.denominator),
        }
        permutation = _permutation_result(study.primary_events, {row["eventId"]: row for row in actual})
        cluster = _cluster_result(study.clusters, hits)
        sides = _side_descriptives(actual)
        p_exact = Fraction(int(permutation["inclusiveTailCount"]), 40)
        cluster_numerator, cluster_denominator = cluster["equalWeightedHitRateFraction"].split("/")
        cluster_rate = Fraction(int(cluster_numerator), int(cluster_denominator))
        survival = _survival_decision(True, hit_rate, p_exact, cluster_rate)
    return {
        "contract": RESULT_CONTRACT,
        "schemaVersion": SCHEMA_VERSION,
        "implementationMilestone": MILESTONE,
        "frozenInputHashes": dict(study.input_hashes),
        "intervalResults": [dict(by_id[interval["intervalId"]]) for interval in study.intervals],
        "primary": primary_result,
        "permutation": permutation,
        "clusterBalanced": cluster,
        "sideDescriptives": sides,
        "timing": timing,
        "survivalStatus": survival,
        "interpretationBoundary": "ASSOCIATION_UNDER_PREREGISTERED_CONDITIONAL_WITHIN_SIDE_PERMUTATION_NULL_IN_THIS_FIXED_PILOT",
        "executionFlags": {
            "outcomeDataRead": True,
            "outcomeUnlocked": True,
            "executionAllowed": False,
            "autoSuggest": False,
            "ml": False,
            "mt5": False,
        },
    }


RESULT_TOP_FIELDS = frozenset(
    {
        "contract", "schemaVersion", "implementationMilestone", "frozenInputHashes", "intervalResults",
        "primary", "permutation", "clusterBalanced", "sideDescriptives", "timing", "survivalStatus",
        "interpretationBoundary", "executionFlags", "resultHash",
    }
)
INTERVAL_RESULT_FIELDS = frozenset(
    {"intervalId", "eventId", "horizon", "sideIdentity", "frozenLabel", "expectedDirection", "scorable", "status", "startTimestampUtc", "endTimestampUtc", "logReturn", "hit"}
)


def validate_result_schema(result: Mapping[str, Any]) -> None:
    """Strict structural validator: missing and additional fields both fail closed."""
    if set(result) != RESULT_TOP_FIELDS:
        raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID")
    if result.get("contract") != RESULT_CONTRACT or result.get("schemaVersion") != SCHEMA_VERSION:
        raise S4EvaluationError("RESULT_SCHEMA_VERSION_INVALID")
    if not isinstance(result.get("frozenInputHashes"), dict) or not isinstance(result.get("intervalResults"), list):
        raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID")
    if any(set(row) != INTERVAL_RESULT_FIELDS for row in result["intervalResults"]):
        raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID")
    expected_nested = {
        "primary": {"status", "scorableEventCount", "denominator", "observedHitCount", "primaryHitRate"},
        "permutation": {"assignmentCount", "observedAssignmentIndex", "observedHitCount", "allAssignments", "histogram", "inclusiveTailCount", "pExact"},
        "clusterBalanced": {"clusterCount", "clusters", "equalWeightedHitRateFraction", "equalWeightedHitRate", "secondaryPValue"},
        "timing": {"status", "hitCounts", "secondaryPValue"},
        "executionFlags": {"outcomeDataRead", "outcomeUnlocked", "executionAllowed", "autoSuggest", "ml", "mt5"},
    }
    for key, fields in expected_nested.items():
        value = result.get(key)
        if not isinstance(value, dict) or set(value) != fields:
            raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID", key)
    if set(result["sideDescriptives"]) != {"USD", "JPY"}:
        raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID", "sideDescriptives")
    for side in ("USD", "JPY"):
        if set(result["sideDescriptives"][side]) != {"hitCount", "eventCount", "hitRate", "meanExpectedSignedLogReturn", "medianExpectedSignedLogReturn", "classification"}:
            raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID", "sideDescriptives")
    flags = result["executionFlags"]
    if any(flags.get(key) is not False for key in ("executionAllowed", "autoSuggest", "ml", "mt5")):
        raise S4EvaluationError("RESULT_EXECUTION_LOCK_INVALID")
    if any(set(row) != {"assignmentCount", "hitCount"} for row in result["permutation"]["histogram"]):
        raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID", "permutation.histogram")
    if any(set(row) != {"usdSupportiveEventIds", "jpySupportiveEventIds", "permutationHitCount"} for row in result["permutation"]["allAssignments"]):
        raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID", "permutation.allAssignments")
    if any(set(row) != {"clusterId", "eventCount", "hitCount", "hitRateFraction", "hitRate"} for row in result["clusterBalanced"]["clusters"]):
        raise S4EvaluationError("RESULT_SCHEMA_FIELDS_INVALID", "clusterBalanced.clusters")
    if result.get("resultHash") != result_hash(result):
        raise S4EvaluationError("RESULT_HASH_MISMATCH")


def result_hash(result: Mapping[str, Any]) -> str:
    body = {key: value for key, value in result.items() if key != "resultHash"}
    return _sha256(_canonical_bytes(body))


def _survival_decision(primary_complete: bool, hit_rate: Fraction, p_exact: Fraction, cluster_rate: Fraction) -> str:
    if not primary_complete:
        return "PRIMARY_EVALUATION_INVALID_DATA_INCOMPLETE"
    if hit_rate > Fraction(1, 2) and p_exact <= Fraction(1, 10) and cluster_rate > Fraction(1, 2):
        return "PILOT_ASSOCIATION_SURVIVED"
    return "PILOT_ASSOCIATION_NOT_SURVIVED"


def build_result(study: FrozenStudy, interval_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    body = _build_result_body(study, interval_results)
    result = {**body, "resultHash": result_hash(body)}
    validate_result_schema(result)
    if result_hash(result) != result["resultHash"]:
        raise S4EvaluationError("RESULT_HASH_MISMATCH")
    return result


def evaluate_frozen_captures(
    project_root: Path,
    private_capture_root: Path,
    *,
    outcome_access_authorized: bool = False,
) -> dict[str, Any]:
    """Future O2 entry point. It refuses to open parsed captures until explicitly authorized."""
    if outcome_access_authorized is not True:
        raise S4EvaluationError("OUTCOME_ACCESS_NOT_AUTHORIZED", EXPECTED_OUTCOME_AUTHORIZATION)
    root = Path(project_root).resolve()
    private_root = Path(private_capture_root).resolve()
    if private_root == root or private_root.is_relative_to(root):
        raise S4EvaluationError("UNSAFE_PRIVATE_CAPTURE_ROOT")
    study = load_frozen_study(root)
    parsed_root = private_root / "mo_r4a_s4_a1" / "parsed"
    intervals = evaluate_interval_streams(study, parsed_root, root)
    return build_result(study, intervals)
