"""Bounded-memory market verification and future quote resolution.

This module is deliberately market-only.  It does not import Candidate C source
state data, does not construct real event anchors, and has no provider client.
It reads only caller-supplied private raw BI5 partitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import hashlib
import importlib
import json
from math import isfinite, log
from pathlib import Path
import sys
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence


PROVIDER_ID = "DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE"
DATASET_ID = "DUKASCOPY_USDJPY_DAILY_TICKS_BI5"
INSTRUMENT_ID = "FX_SPOT_USDJPY"
COVERAGE_START_UTC = "2025-05-01T01:58:38Z"
COVERAGE_END_UTC = "2025-08-01T23:20:56Z"
RESOLUTION_SECONDS = 1
EXPECTED_RAW_ARTIFACT_COUNT = 80
EXPECTED_RAW_QUOTE_COUNT = 7_888_953
EXPECTED_ADMITTED_QUOTE_COUNT = 7_880_695
QUOTE_TOLERANCE_SECONDS = 60


class LowMemoryMarketError(ValueError):
    """Raised for a market-only raw-data or quote-resolution contract failure."""


@dataclass(frozen=True)
class StreamingQuote:
    timestamp_utc: str
    bid: float
    ask: float


@dataclass(frozen=True)
class StreamingValidatedMarketSnapshot:
    """The validated metadata contract, intentionally without a quote collection."""

    market_snapshot_hash: str
    provider_id: str
    dataset_id: str
    instrument_id: str
    coverage_start_utc: str
    coverage_end_utc: str
    resolution_seconds: int
    raw_artifact_hashes: tuple[tuple[str, str], ...]
    raw_quote_count: int
    admitted_quote_count: int
    exact_duplicate_count: int
    peak_rss_bytes: int | None


@dataclass(frozen=True)
class QuoteRequest:
    request_id: str
    anchor_utc: str


@dataclass(frozen=True)
class ReturnRequest:
    request_id: str
    event_exact_utc: str
    horizon_seconds: int


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _self_hash(document: Mapping[str, Any], field: str) -> str:
    payload = dict(document)
    payload.pop(field, None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest().upper()


def _parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: timestamp must be an explicit UTC Z string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: timestamp is not ISO-8601 UTC") from exc
    if parsed.tzinfo != timezone.utc:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: timestamp must resolve exactly to UTC")
    return parsed


def _timestamp_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _snapshot_prefix(quote_count: int) -> str:
    fields = [
        ("coverageEndUtc", COVERAGE_END_UTC),
        ("coverageStartUtc", COVERAGE_START_UTC),
        ("datasetId", DATASET_ID),
        ("instrumentId", INSTRUMENT_ID),
        ("providerId", PROVIDER_ID),
        ("quoteCount", quote_count),
    ]
    return "{" + ",".join(f"{canonical_json(key)}:{canonical_json(value)}" for key, value in fields) + ',"quotes":['


def _snapshot_suffix(raw_hashes: Mapping[str, str]) -> str:
    return "]" + "," + ",".join((
        f'"rawArtifactHashes":{canonical_json(dict(raw_hashes))}',
        f'"resolutionSeconds":{RESOLUTION_SECONDS}',
        '"timezone":"UTC"',
    )) + "}"


def _quote_json(quote: StreamingQuote) -> str:
    return canonical_json({"ask": quote.ask, "bid": quote.bid, "timestampUtc": quote.timestamp_utc})


def _load_parser(repo_root: Path) -> tuple[Callable[..., str], Callable[..., tuple[Any, ...]]]:
    backend = str(repo_root / "gann-astro-desk" / "backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)
    module = importlib.import_module("dukascopy_tick_parser_s3r1_r3_r2")
    return module.format_timestamp_utc, module.parse_daily_bi5


def _artifact_map(inventory: Mapping[str, Any], admission: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    if _self_hash(inventory, "rawArtifactInventoryHash") != inventory.get("rawArtifactInventoryHash"):
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: raw artifact inventory self-hash mismatch")
    artifacts = inventory.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != EXPECTED_RAW_ARTIFACT_COUNT:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: raw artifact inventory must contain exactly 80 objects")
    expected = admission.get("rawArtifactHashes")
    if not isinstance(expected, Mapping) or len(expected) != EXPECTED_RAW_ARTIFACT_COUNT:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: admission must bind exactly 80 raw artifact hashes")
    observed: dict[str, str] = {}
    normalized: list[dict[str, Any]] = []
    for item in artifacts:
        if not isinstance(item, Mapping):
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: artifact inventory entry is not an object")
        artifact_id, raw_hash = item.get("artifactId"), item.get("sha256")
        if not isinstance(artifact_id, str) or not isinstance(raw_hash, str) or artifact_id in observed:
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: artifact identity/hash is invalid or duplicated")
        if expected.get(artifact_id) != raw_hash:
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: inventory/admission raw hash binding mismatch")
        if not isinstance(item.get("originalFilename"), str) or not isinstance(item.get("partitionDateUtc"), str):
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: artifact filename or partition date is missing")
        if not isinstance(item.get("byteCount"), int) or item["byteCount"] <= 0:
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: artifact byte count is invalid")
        observed[artifact_id] = raw_hash
        normalized.append(dict(item))
    if observed != dict(expected):
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: missing or unexpected raw artifact identity")
    return sorted(normalized, key=lambda item: (item["partitionDateUtc"], item["artifactId"])), observed


def _iter_partition_quotes(
    repo_root: Path,
    raw_dir: Path,
    artifacts: Sequence[Mapping[str, Any]],
    *,
    verify_raw_hashes: bool,
    observe_rss: Callable[[], int] | None,
) -> Iterator[StreamingQuote]:
    format_timestamp_utc, parse_daily_bi5 = _load_parser(repo_root)
    for item in artifacts:
        raw_path = raw_dir / str(item["originalFilename"])
        if not raw_path.is_file():
            raise LowMemoryMarketError(f"LOW_MEMORY_MARKET_INVALID: missing raw artifact {raw_path.name}")
        if raw_path.stat().st_size != item["byteCount"]:
            raise LowMemoryMarketError(f"LOW_MEMORY_MARKET_INVALID: byte count mismatch for {raw_path.name}")
        raw_bytes = raw_path.read_bytes()
        if verify_raw_hashes and hashlib.sha256(raw_bytes).hexdigest().upper() != item["sha256"]:
            raise LowMemoryMarketError(f"LOW_MEMORY_MARKET_INVALID: SHA-256 mismatch for {raw_path.name}")
        if observe_rss is not None:
            observe_rss()
        records = parse_daily_bi5(raw_bytes, partition_date_utc=date.fromisoformat(str(item["partitionDateUtc"])))
        for record in records:
            if observe_rss is not None and record.record_index % 10_000 == 0:
                observe_rss()
            yield StreamingQuote(
                timestamp_utc=format_timestamp_utc(record.timestamp_utc),
                bid=record.bid_native / 1000,
                ask=record.ask_native / 1000,
            )
        del records
        del raw_bytes


def _inspect_quote_stream(quotes: Iterable[StreamingQuote]) -> tuple[int, int, int]:
    coverage_start, coverage_end = _parse_utc(COVERAGE_START_UTC), _parse_utc(COVERAGE_END_UTC)
    raw_count = admitted_count = exact_duplicate_count = 0
    previous: StreamingQuote | None = None
    previous_time: datetime | None = None
    for quote in quotes:
        timestamp = _parse_utc(quote.timestamp_utc)
        if not isfinite(quote.bid) or not isfinite(quote.ask) or quote.bid <= 0 or quote.ask <= 0 or quote.ask < quote.bid:
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: invalid bid/ask")
        if previous_time is not None:
            if timestamp < previous_time:
                raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: chronological reversal")
            if timestamp == previous_time:
                if quote != previous:
                    raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: conflicting same-timestamp quote")
                exact_duplicate_count += 1
        if coverage_start <= timestamp <= coverage_end:
            admitted_count += 1
        raw_count += 1
        previous, previous_time = quote, timestamp
    if not raw_count:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: no parsed quotes")
    return raw_count, admitted_count, exact_duplicate_count


def _canonical_stream_hash(quotes: Iterable[StreamingQuote], quote_count: int, raw_hashes: Mapping[str, str]) -> tuple[str, int]:
    coverage_start, coverage_end = _parse_utc(COVERAGE_START_UTC), _parse_utc(COVERAGE_END_UTC)
    digest = hashlib.sha256()
    digest.update(_snapshot_prefix(quote_count).encode("utf-8"))
    emitted = 0
    for quote in quotes:
        timestamp = _parse_utc(quote.timestamp_utc)
        if not coverage_start <= timestamp <= coverage_end:
            continue
        if emitted:
            digest.update(b",")
        digest.update(_quote_json(quote).encode("utf-8"))
        emitted += 1
    if emitted != quote_count:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: canonical quote count changed between passes")
    digest.update(_snapshot_suffix(raw_hashes).encode("utf-8"))
    return digest.hexdigest().upper(), emitted


def canonical_snapshot_hash_from_quotes(quotes: Iterable[StreamingQuote], raw_hashes: Mapping[str, str], *, quote_count: int) -> str:
    """Canonical semantic hash helper for bounded synthetic equivalence fixtures."""

    return _canonical_stream_hash(quotes, quote_count, raw_hashes)[0]


def inspect_market_quotes(quotes: Iterable[StreamingQuote]) -> tuple[int, int, int]:
    """Validate a chronologically ordered quote stream without storing it."""

    return _inspect_quote_stream(quotes)


def validate_emp1_raw_market_stream(
    repo_root: Path | str,
    raw_dir: Path | str,
    inventory: Mapping[str, Any],
    admission: Mapping[str, Any],
    *,
    expected_snapshot_hash: str,
    observe_rss: Callable[[], int] | None = None,
) -> StreamingValidatedMarketSnapshot:
    """Reproduce EMP1's canonical market identity without retaining all quotes."""

    root, private_raw_dir = Path(repo_root).resolve(), Path(raw_dir)
    artifacts, raw_hashes = _artifact_map(inventory, admission)
    raw_count, admitted_count, exact_duplicate_count = _inspect_quote_stream(
        _iter_partition_quotes(root, private_raw_dir, artifacts, verify_raw_hashes=True, observe_rss=observe_rss)
    )
    if raw_count != EXPECTED_RAW_QUOTE_COUNT or admitted_count != EXPECTED_ADMITTED_QUOTE_COUNT:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: frozen EMP1 quote count mismatch")
    semantic_hash, emitted_count = _canonical_stream_hash(
        _iter_partition_quotes(root, private_raw_dir, artifacts, verify_raw_hashes=True, observe_rss=observe_rss),
        admitted_count,
        raw_hashes,
    )
    if semantic_hash != expected_snapshot_hash:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: canonical marketSnapshotHash mismatch")
    if admission.get("marketSnapshotHash") != semantic_hash:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: admission marketSnapshotHash mismatch")
    if admission.get("providerId") != PROVIDER_ID or admission.get("datasetId") != DATASET_ID or admission.get("instrumentId") != INSTRUMENT_ID:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: admission market identity mismatch")
    if admission.get("coverageStartUtc") != COVERAGE_START_UTC or admission.get("coverageEndUtc") != COVERAGE_END_UTC:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: admission coverage mismatch")
    if admission.get("resolutionSeconds") != RESOLUTION_SECONDS:
        raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: admission resolution mismatch")
    peak_rss = observe_rss() if observe_rss is not None else None
    return StreamingValidatedMarketSnapshot(
        market_snapshot_hash=semantic_hash,
        provider_id=PROVIDER_ID,
        dataset_id=DATASET_ID,
        instrument_id=INSTRUMENT_ID,
        coverage_start_utc=COVERAGE_START_UTC,
        coverage_end_utc=COVERAGE_END_UTC,
        resolution_seconds=RESOLUTION_SECONDS,
        raw_artifact_hashes=tuple(sorted(raw_hashes.items())),
        raw_quote_count=raw_count,
        admitted_quote_count=emitted_count,
        exact_duplicate_count=exact_duplicate_count,
        peak_rss_bytes=peak_rss,
    )


def validate_streamed_admission_record(snapshot: StreamingValidatedMarketSnapshot, admission: Mapping[str, Any], *, expected_snapshot_schema_hash: str, expected_market_data_admission_contract_hash: str) -> Any:
    """Use the frozen admission validator with metadata-equivalent streaming output."""

    from research_labs.candidate_c_empirical.market_contract import validate_market_admission_record

    return validate_market_admission_record(
        admission,
        snapshot,
        expected_snapshot_schema_hash=expected_snapshot_schema_hash,
        expected_market_data_admission_contract_hash=expected_market_data_admission_contract_hash,
    )


def resolve_quote_requests(requests: Sequence[QuoteRequest], quotes: Iterable[StreamingQuote]) -> dict[str, StreamingQuote | None]:
    """Resolve first quote at/after each anchor, bounded by the frozen 60 seconds."""

    prepared: list[tuple[datetime, datetime, str]] = []
    request_ids: set[str] = set()
    for request in requests:
        if request.request_id in request_ids:
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: duplicate quote request ID")
        anchor = _parse_utc(request.anchor_utc)
        prepared.append((anchor, anchor + timedelta(seconds=QUOTE_TOLERANCE_SECONDS), request.request_id))
        request_ids.add(request.request_id)
    prepared.sort(key=lambda item: (item[0], item[2]))
    resolved: dict[str, StreamingQuote | None] = {}
    index = 0
    previous_time: datetime | None = None
    for quote in quotes:
        quote_time = _parse_utc(quote.timestamp_utc)
        if previous_time is not None and quote_time < previous_time:
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: resolver quote chronology reversal")
        previous_time = quote_time
        while index < len(prepared) and prepared[index][1] < quote_time:
            resolved[prepared[index][2]] = None
            index += 1
        while index < len(prepared) and prepared[index][0] <= quote_time <= prepared[index][1]:
            resolved[prepared[index][2]] = quote
            index += 1
    while index < len(prepared):
        resolved[prepared[index][2]] = None
        index += 1
    return resolved


def resolve_forward_log_returns(requests: Sequence[ReturnRequest], quotes: Iterable[StreamingQuote]) -> dict[str, dict[str, Any]]:
    """Future-execution skeleton with frozen P0/PH selection and return semantics."""

    quote_requests: list[QuoteRequest] = []
    horizons: dict[str, str] = {}
    seen: set[str] = set()
    for request in requests:
        if request.request_id in seen or request.horizon_seconds <= 0:
            raise LowMemoryMarketError("LOW_MEMORY_MARKET_INVALID: return request ID or horizon is invalid")
        event_time = _parse_utc(request.event_exact_utc)
        quote_requests.extend((
            QuoteRequest(f"{request.request_id}::P0", request.event_exact_utc),
            QuoteRequest(f"{request.request_id}::PH", _timestamp_text(event_time + timedelta(seconds=request.horizon_seconds))),
        ))
        horizons[request.request_id] = request.event_exact_utc
        seen.add(request.request_id)
    selected = resolve_quote_requests(quote_requests, quotes)
    results: dict[str, dict[str, Any]] = {}
    for request in requests:
        p0_quote, ph_quote = selected[f"{request.request_id}::P0"], selected[f"{request.request_id}::PH"]
        if p0_quote is None or ph_quote is None:
            results[request.request_id] = {"status": "MARKET_QUOTE_UNAVAILABLE", "eventExactUtc": request.event_exact_utc, "horizonSeconds": request.horizon_seconds}
            continue
        p0, ph = (p0_quote.bid + p0_quote.ask) / 2.0, (ph_quote.bid + ph_quote.ask) / 2.0
        results[request.request_id] = {
            "status": "MARKET_RETURN_AVAILABLE",
            "eventExactUtc": request.event_exact_utc,
            "horizonSeconds": request.horizon_seconds,
            "p0TimestampUtc": p0_quote.timestamp_utc,
            "phTimestampUtc": ph_quote.timestamp_utc,
            "p0": p0,
            "ph": ph,
            "logReturn": log(ph / p0),
        }
    return results
