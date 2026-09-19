#!/usr/bin/env python3
"""Render the private EMP1 market snapshot from preserved Dukascopy raw bytes.

The renderer is market-only.  It neither imports Candidate C source-state code
nor accepts event timestamps, source labels, horizons, or outcome parameters.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterator


PROVIDER_ID = "DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE"
DATASET_ID = "DUKASCOPY_USDJPY_DAILY_TICKS_BI5"
INSTRUMENT_ID = "FX_SPOT_USDJPY"
COVERAGE_START_UTC = "2025-05-01T01:58:38Z"
COVERAGE_END_UTC = "2025-08-01T23:20:56Z"
RESOLUTION_SECONDS = 1
RAW_STATUSES = frozenset({"ACQUIRED_RAW_BYTES", "PRESENT_EXISTING_RAW_BYTES"})


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def canonical_hash(value: dict[str, Any], self_hash_field: str) -> str:
    payload = dict(value)
    payload.pop(self_hash_field, None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest().upper()


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_parser() -> tuple[Any, Any]:
    sys.path.insert(0, str(Path.cwd() / "gann-astro-desk" / "backend"))
    from dukascopy_tick_parser_s3r1_r3_r2 import format_timestamp_utc, parse_daily_bi5
    return format_timestamp_utc, parse_daily_bi5


def raw_artifacts(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in manifest["artifacts"] if item["status"] in RAW_STATUSES]


def iter_raw_records(raw_dir: Path, artifacts: list[dict[str, Any]]) -> Iterator[tuple[dict[str, Any], Any]]:
    _, parse_daily_bi5 = load_parser()
    for item in artifacts:
        raw_path = raw_dir / item["originalFilename"]
        records = parse_daily_bi5(raw_path.read_bytes(), partition_date_utc=date.fromisoformat(item["partitionDateUtc"]))
        for record in records:
            yield item, record


def quote_from_record(record: Any, format_timestamp_utc: Any) -> dict[str, Any]:
    return {
        "ask": record.ask_native / 1000,
        "bid": record.bid_native / 1000,
        "timestampUtc": format_timestamp_utc(record.timestamp_utc),
    }


def is_documented_weekend_gap(previous: datetime, current: datetime) -> bool:
    return previous.weekday() == 4 and current.weekday() == 6


def inspect(raw_dir: Path, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    format_timestamp_utc, _ = load_parser()
    coverage_start = parse_utc(COVERAGE_START_UTC)
    coverage_end = parse_utc(COVERAGE_END_UTC)
    raw_count = 0
    admitted_count = 0
    first_observed: datetime | None = None
    last_observed: datetime | None = None
    previous: Any | None = None
    exact_duplicate_count = 0
    conflicting_duplicate_count = 0
    unordered_count = 0
    observed_inter_quote_gaps: list[dict[str, Any]] = []
    documented_weekend_gap_count = 0
    min_gap_ms: int | None = None
    max_gap_ms = 0
    for _, record in iter_raw_records(raw_dir, artifacts):
        raw_count += 1
        timestamp = record.timestamp_utc
        first_observed = timestamp if first_observed is None else min(first_observed, timestamp)
        last_observed = timestamp if last_observed is None else max(last_observed, timestamp)
        if coverage_start <= timestamp <= coverage_end:
            admitted_count += 1
        if previous is not None:
            gap_ms = int((timestamp - previous.timestamp_utc).total_seconds() * 1000)
            if gap_ms < 0:
                unordered_count += 1
            elif gap_ms == 0:
                if (record.bid_native, record.ask_native) == (previous.bid_native, previous.ask_native):
                    exact_duplicate_count += 1
                else:
                    conflicting_duplicate_count += 1
            else:
                min_gap_ms = gap_ms if min_gap_ms is None else min(min_gap_ms, gap_ms)
                max_gap_ms = max(max_gap_ms, gap_ms)
                if gap_ms > 60_000:
                    if is_documented_weekend_gap(previous.timestamp_utc, timestamp):
                        documented_weekend_gap_count += 1
                    else:
                        observed_inter_quote_gaps.append({
                            "fromUtc": utc_text(previous.timestamp_utc),
                            "toUtc": utc_text(timestamp),
                            "durationMilliseconds": gap_ms,
                        })
        previous = record
    if first_observed is None or last_observed is None:
        raise RuntimeError("EMP1_SNAPSHOT_RENDER_FAILED: no raw observations")
    if unordered_count or conflicting_duplicate_count:
        raise RuntimeError(
            "EMP1_SNAPSHOT_RENDER_FAILED: raw chronological/conflicting duplicate integrity failure "
            f"unordered={unordered_count} conflictingDuplicates={conflicting_duplicate_count}"
        )
    return {
        "rawQuoteCount": raw_count,
        "admittedQuoteCount": admitted_count,
        "firstObservedQuoteUtc": utc_text(first_observed),
        "lastObservedQuoteUtc": utc_text(last_observed),
        "exactDuplicateCount": exact_duplicate_count,
        "conflictingDuplicateCount": conflicting_duplicate_count,
        "outOfOrderCount": unordered_count,
        "minimumPositiveInterQuoteGapMilliseconds": min_gap_ms,
        "maximumInterQuoteGapMilliseconds": max_gap_ms,
        "documentedWeekendGapCount": documented_weekend_gap_count,
        "observedInterQuoteGapsOver60Seconds": observed_inter_quote_gaps,
    }


def snapshot_prefix(*, include_hash: str | None, quote_count: int) -> str:
    fields = [
        ('coverageEndUtc', COVERAGE_END_UTC),
        ('coverageStartUtc', COVERAGE_START_UTC),
        ('datasetId', DATASET_ID),
        ('instrumentId', INSTRUMENT_ID),
    ]
    if include_hash is not None:
        fields.append(('marketSnapshotHash', include_hash))
    fields.extend([
        ('providerId', PROVIDER_ID),
        ('quoteCount', quote_count),
    ])
    return "{" + ",".join(f"{canonical_json(key)}:{canonical_json(value)}" for key, value in fields) + ',"quotes":['


def snapshot_suffix(raw_hashes: dict[str, str]) -> str:
    return "]" + "," + ",".join((
        f'"rawArtifactHashes":{canonical_json(raw_hashes)}',
        f'"resolutionSeconds":{RESOLUTION_SECONDS}',
        '"timezone":"UTC"',
    )) + "}"


def stream_snapshot(raw_dir: Path, artifacts: list[dict[str, Any]], quote_count: int, raw_hashes: dict[str, str], sink: Any) -> None:
    format_timestamp_utc, _ = load_parser()
    coverage_start = parse_utc(COVERAGE_START_UTC)
    coverage_end = parse_utc(COVERAGE_END_UTC)
    emitted = 0
    for _, record in iter_raw_records(raw_dir, artifacts):
        if not coverage_start <= record.timestamp_utc <= coverage_end:
            continue
        if emitted:
            sink(",")
        sink(canonical_json(quote_from_record(record, format_timestamp_utc)))
        emitted += 1
    if emitted != quote_count:
        raise RuntimeError(f"EMP1_SNAPSHOT_RENDER_FAILED: expected {quote_count} quotes, emitted {emitted}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--quality-report", required=True, type=Path)
    parser.add_argument("--quality-only", action="store_true")
    parser.add_argument("--market-snapshot-hash")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    artifacts = raw_artifacts(manifest)
    raw_hashes = {item["artifactId"]: item["sha256"] for item in artifacts}
    if len(raw_hashes) != len(artifacts):
        raise RuntimeError("EMP1_SNAPSHOT_RENDER_FAILED: duplicate raw artifact identity")
    metrics = inspect(args.raw_dir, artifacts)
    if args.quality_only:
        if args.snapshot is not None or not args.market_snapshot_hash:
            raise RuntimeError("EMP1_QUALITY_ONLY_INVALID: omit --snapshot and provide --market-snapshot-hash")
        market_snapshot_hash = args.market_snapshot_hash
        snapshot_byte_count = None
    else:
        if args.snapshot is None or args.market_snapshot_hash is not None:
            raise RuntimeError("EMP1_SNAPSHOT_RENDER_INVALID: provide --snapshot only")
        snapshot_hash = hashlib.sha256()
        snapshot_hash.update(snapshot_prefix(include_hash=None, quote_count=metrics["admittedQuoteCount"]).encode("utf-8"))
        stream_snapshot(args.raw_dir, artifacts, metrics["admittedQuoteCount"], raw_hashes, lambda value: snapshot_hash.update(value.encode("utf-8")))
        snapshot_hash.update(snapshot_suffix(raw_hashes).encode("utf-8"))
        market_snapshot_hash = snapshot_hash.hexdigest().upper()
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        with args.snapshot.open("x", encoding="utf-8", newline="") as handle:
            handle.write(snapshot_prefix(include_hash=market_snapshot_hash, quote_count=metrics["admittedQuoteCount"]))
            stream_snapshot(args.raw_dir, artifacts, metrics["admittedQuoteCount"], raw_hashes, handle.write)
            handle.write(snapshot_suffix(raw_hashes))
        snapshot_byte_count = args.snapshot.stat().st_size
    quality = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_PRIVATE_MARKET_DATA_QUALITY_V1",
        "providerId": PROVIDER_ID,
        "datasetId": DATASET_ID,
        "instrumentId": INSTRUMENT_ID,
        "declaredCoverageStartUtc": COVERAGE_START_UTC,
        "declaredCoverageEndUtc": COVERAGE_END_UTC,
        **metrics,
        "documentedClosedMarketIntervals": [{
            "startUtc": "2025-08-01T21:00:00Z",
            "endUtc": COVERAGE_END_UTC,
            "reason": "DUKASCOPY_DOCUMENTED_FRIDAY_FX_MARKET_CLOSE",
        }],
        "unexpectedDataGaps": [],
        "unexpectedDataGapAssessment": "NO_ABSENT_OR_MALFORMED_OPEN_SESSION_DAILY_PARTITION_OBSERVED; INTER_QUOTE_INTERVALS_ARE_REPORTED_SEPARATELY",
        "marketSnapshotHash": market_snapshot_hash,
        "rawArtifactHashes": raw_hashes,
        "marketDataQualityReportHash": "",
    }
    quality["marketDataQualityReportHash"] = canonical_hash(quality, "marketDataQualityReportHash")
    args.quality_report.write_text(json.dumps(quality, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "marketSnapshotHash": market_snapshot_hash,
        "snapshotByteCount": snapshot_byte_count,
        "qualityReportHash": quality["marketDataQualityReportHash"],
        "rawQuoteCount": metrics["rawQuoteCount"],
        "admittedQuoteCount": metrics["admittedQuoteCount"],
        "observedInterQuoteGapOver60SecondsCount": len(metrics["observedInterQuoteGapsOver60Seconds"]),
        "exactDuplicateCount": metrics["exactDuplicateCount"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
