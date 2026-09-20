"""Synthetic-only equivalence checks for the EMP2-R1 low-memory successor."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from research_labs.candidate_c_empirical.canonical import self_hash
from research_labs.candidate_c_empirical.market_contract import validate_market_snapshot
from research_labs.candidate_c_empirical.returns import extract_forward_log_return
from research_labs.candidate_c_empirical_low_memory.market_stream import (
    LowMemoryMarketError,
    QuoteRequest,
    ReturnRequest,
    StreamingQuote,
    StreamingValidatedMarketSnapshot,
    canonical_snapshot_hash_from_quotes,
    inspect_market_quotes,
    resolve_forward_log_returns,
    resolve_quote_requests,
    validate_streamed_admission_record,
)


RAW_HASHES = {"SYNTHETIC_PARTITION": "A" * 64}


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def quote(value: datetime, bid: float = 150.0, ask: float = 150.02) -> dict[str, object]:
    return {"timestampUtc": utc_text(value), "bid": bid, "ask": ask}


def streaming(quotes: list[dict[str, object]]) -> list[StreamingQuote]:
    return [StreamingQuote(timestamp_utc=str(item["timestampUtc"]), bid=float(item["bid"]), ask=float(item["ask"])) for item in quotes]


def snapshot(quotes: list[dict[str, object]]) -> dict[str, object]:
    document: dict[str, object] = {
        "providerId": "DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE",
        "datasetId": "DUKASCOPY_USDJPY_DAILY_TICKS_BI5",
        "instrumentId": "FX_SPOT_USDJPY",
        "timezone": "UTC",
        "resolutionSeconds": 1,
        "coverageStartUtc": "2025-05-01T01:58:38Z",
        "coverageEndUtc": "2025-08-01T23:20:56Z",
        "rawArtifactHashes": RAW_HASHES,
        "quoteCount": len(quotes),
        "quotes": quotes,
        "marketSnapshotHash": None,
    }
    document["marketSnapshotHash"] = self_hash(document, "marketSnapshotHash")
    return document


def old_and_new(event: str, horizon: int, quotes: list[dict[str, object]]) -> tuple[dict[str, object], dict[str, object]]:
    old = extract_forward_log_return(event, horizon, validate_market_snapshot(snapshot(quotes)).quotes)
    new = resolve_forward_log_returns([ReturnRequest("synthetic", event, horizon)], streaming(quotes))["synthetic"]
    return old, new


@pytest.mark.parametrize(
    ("offset_ms", "expect_available"),
    [(0, True), (1, True), (60_000, True), (60_001, False)],
)
def test_low_memory_return_selection_matches_frozen_boundaries(offset_ms: int, expect_available: bool) -> None:
    anchor = datetime(2025, 5, 1, 2, 0, tzinfo=timezone.utc)
    quotes = [
        quote(anchor + timedelta(milliseconds=offset_ms), 150.0, 150.02),
        quote(anchor + timedelta(hours=1, milliseconds=offset_ms), 151.0, 151.02),
    ]
    old, new = old_and_new(utc_text(anchor), 3600, quotes)
    assert old == new
    assert (old["status"] == "MARKET_RETURN_AVAILABLE") is expect_available


def test_low_memory_return_selection_matches_weekend_gap_and_no_quote() -> None:
    friday = datetime(2025, 5, 2, 20, 59, 0, tzinfo=timezone.utc)
    sunday = datetime(2025, 5, 4, 21, 0, 0, tzinfo=timezone.utc)
    old, new = old_and_new(utc_text(friday), 3600, [quote(sunday)])
    assert old == new == {"status": "MARKET_QUOTE_UNAVAILABLE", "eventExactUtc": utc_text(friday), "horizonSeconds": 3600}
    old, new = old_and_new(utc_text(friday), 3600, [])
    assert old == new == {"status": "MARKET_QUOTE_UNAVAILABLE", "eventExactUtc": utc_text(friday), "horizonSeconds": 3600}


def test_low_memory_resolver_matches_all_three_horizons_and_multiple_events() -> None:
    base = datetime(2025, 5, 1, 2, 0, tzinfo=timezone.utc)
    quotes = [quote(base + timedelta(seconds=offset), 150.0 + offset / 1000, 150.02 + offset / 1000) for offset in (0, 60, 3600, 3660, 7200, 7260, 86400, 86460)]
    requests = [
        ReturnRequest("event-a-1h", utc_text(base), 3600),
        ReturnRequest("event-a-6h", utc_text(base), 21600),
        ReturnRequest("event-a-24h", utc_text(base), 86400),
        ReturnRequest("event-b-1h", utc_text(base + timedelta(seconds=60)), 3600),
    ]
    resolved = resolve_forward_log_returns(requests, streaming(quotes))
    for request in requests:
        assert resolved[request.request_id] == extract_forward_log_return(request.event_exact_utc, request.horizon_seconds, validate_market_snapshot(snapshot(quotes)).quotes)


def test_multiple_anchors_can_select_the_same_first_quote() -> None:
    base = datetime(2025, 5, 1, 2, 0, tzinfo=timezone.utc)
    selected = resolve_quote_requests(
        [QuoteRequest("a", utc_text(base)), QuoteRequest("b", utc_text(base + timedelta(milliseconds=500)))],
        [StreamingQuote(utc_text(base + timedelta(seconds=1)), 150.0, 150.02)],
    )
    assert selected["a"] == selected["b"]


def test_identical_duplicate_is_equivalent_but_conflicting_duplicate_is_rejected() -> None:
    base = datetime(2025, 5, 1, 2, 0, tzinfo=timezone.utc)
    quotes = [quote(base), quote(base), quote(base + timedelta(hours=1), 151.0, 151.02)]
    old, new = old_and_new(utc_text(base), 3600, quotes)
    assert old == new
    assert inspect_market_quotes(streaming(quotes))[2] == 1
    conflicting = deepcopy(quotes)
    conflicting[1]["ask"] = 150.03
    with pytest.raises(ValueError):
        validate_market_snapshot(snapshot(conflicting))
    with pytest.raises(LowMemoryMarketError, match="conflicting"):
        inspect_market_quotes(streaming(conflicting))


def test_out_of_order_quote_is_rejected_by_successor_stream() -> None:
    base = datetime(2025, 5, 1, 2, 0, tzinfo=timezone.utc)
    unordered = [StreamingQuote(utc_text(base + timedelta(seconds=1)), 150.0, 150.02), StreamingQuote(utc_text(base), 150.0, 150.02)]
    with pytest.raises(LowMemoryMarketError, match="chronological reversal"):
        inspect_market_quotes(unordered)
    with pytest.raises(LowMemoryMarketError, match="chronology reversal"):
        resolve_quote_requests([QuoteRequest("a", utc_text(base))], unordered)


def test_canonical_quote_stream_hash_matches_frozen_snapshot_hash() -> None:
    start = datetime(2025, 5, 1, 1, 58, 38, tzinfo=timezone.utc)
    end = datetime(2025, 8, 1, 23, 20, 56, tzinfo=timezone.utc)
    quotes = [quote(start), quote(end, 151.0, 151.02)]
    frozen = snapshot(quotes)
    assert canonical_snapshot_hash_from_quotes(streaming(quotes), RAW_HASHES, quote_count=2) == frozen["marketSnapshotHash"]


def test_coverage_boundaries_are_inclusive_for_canonical_quote_stream() -> None:
    start = datetime(2025, 5, 1, 1, 58, 38, tzinfo=timezone.utc)
    end = datetime(2025, 8, 1, 23, 20, 56, tzinfo=timezone.utc)
    assert inspect_market_quotes(streaming([quote(start), quote(end)]))[:2] == (2, 2)


def test_streaming_metadata_uses_the_frozen_admission_validator_without_quotes() -> None:
    quotes = [quote(datetime(2025, 5, 1, 2, 0, tzinfo=timezone.utc))]
    frozen = validate_market_snapshot(snapshot(quotes))
    admission: dict[str, object] = {
        "schemaVersion": "SYNTHETIC_ADMISSION_V1",
        "admissionId": "SYNTHETIC_ADMISSION",
        "admitted": True,
        "marketSnapshotHash": frozen.market_snapshot_hash,
        "providerId": frozen.provider_id,
        "datasetId": frozen.dataset_id,
        "instrumentId": frozen.instrument_id,
        "coverageStartUtc": frozen.coverage_start_utc,
        "coverageEndUtc": frozen.coverage_end_utc,
        "resolutionSeconds": frozen.resolution_seconds,
        "rawArtifactHashes": dict(frozen.raw_artifact_hashes),
        "emp0R3R1MarketSnapshotSchemaHash": "B" * 64,
        "emp0R3R1MarketDataAdmissionContractHash": "C" * 64,
        "admissionRecordHash": None,
    }
    admission["admissionRecordHash"] = self_hash(admission, "admissionRecordHash")
    streamed = StreamingValidatedMarketSnapshot(
        market_snapshot_hash=frozen.market_snapshot_hash,
        provider_id=frozen.provider_id,
        dataset_id=frozen.dataset_id,
        instrument_id=frozen.instrument_id,
        coverage_start_utc=frozen.coverage_start_utc,
        coverage_end_utc=frozen.coverage_end_utc,
        resolution_seconds=frozen.resolution_seconds,
        raw_artifact_hashes=frozen.raw_artifact_hashes,
        raw_quote_count=1,
        admitted_quote_count=1,
        exact_duplicate_count=0,
        peak_rss_bytes=None,
    )
    validated = validate_streamed_admission_record(streamed, admission, expected_snapshot_schema_hash="B" * 64, expected_market_data_admission_contract_hash="C" * 64)
    assert validated.admission_record_hash == admission["admissionRecordHash"]


def test_market_only_successor_has_no_candidate_c_source_state_import() -> None:
    source = (Path(__file__).parent / "market_stream.py").read_text(encoding="utf-8")
    assert "candidate_c_empirical.source_state" not in source
    assert "candidate_c_empirical.runtime" not in source
