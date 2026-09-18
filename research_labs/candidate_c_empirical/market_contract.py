"""In-memory immutable market-snapshot and admission-record validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
import re
from typing import Any, Mapping

from .canonical import self_hash


MAX_RESOLUTION_SECONDS = 60
REQUIRED_COVERAGE_START_UTC = "2025-05-01T01:58:38Z"
REQUIRED_COVERAGE_END_UTC = "2025-08-01T23:20:56Z"
_SHA256 = re.compile(r"^[0-9A-F]{64}$")


class MarketContractError(ValueError):
    """Raised for a snapshot or admission-record contract violation."""


@dataclass(frozen=True)
class FrozenMarketQuote:
    """Deeply immutable normalized quote value used after snapshot validation."""

    timestamp_utc: str
    bid: float
    ask: float


@dataclass(frozen=True)
class ValidatedMarketSnapshot:
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
    quotes: tuple[FrozenMarketQuote, ...]


@dataclass(frozen=True)
class ValidatedMarketAdmissionRecord:
    admission_id: str
    admission_record_hash: str
    market_snapshot_hash: str


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: timestamp must be an explicit UTC Z string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: timestamp is not ISO-8601 UTC") from exc
    if parsed.tzinfo != timezone.utc:
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: timestamp must resolve exactly to UTC")
    return parsed


def _require_hash(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise MarketContractError(f"MARKET_DATA_SNAPSHOT_INVALID: {field} must be uppercase SHA-256 hex")
    return value


def _validate_raw_artifact_hashes(value: Any) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, Mapping) or not value:
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: rawArtifactHashes must be a non-empty mapping")
    normalized: list[tuple[str, str]] = []
    for artifact_id, artifact_hash in value.items():
        if not isinstance(artifact_id, str) or not artifact_id.strip():
            raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: rawArtifactHashes keys must be non-empty strings")
        normalized.append((artifact_id, _require_hash(artifact_hash, "rawArtifactHashes value")))
    return tuple(sorted(normalized))


def validate_market_snapshot(snapshot: Mapping[str, Any]) -> ValidatedMarketSnapshot:
    """Validate a supplied canonical snapshot without provider or file access."""

    required_fields = {
        "providerId", "datasetId", "instrumentId", "timezone", "resolutionSeconds",
        "coverageStartUtc", "coverageEndUtc", "rawArtifactHashes", "quoteCount",
        "quotes", "marketSnapshotHash",
    }
    missing = sorted(required_fields - set(snapshot))
    if missing:
        raise MarketContractError(f"MARKET_DATA_SNAPSHOT_INVALID: missing required fields {missing}")
    expected_hash = _require_hash(snapshot["marketSnapshotHash"], "marketSnapshotHash")
    if self_hash(dict(snapshot), "marketSnapshotHash") != expected_hash:
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: marketSnapshotHash mismatch")
    provider, dataset = snapshot["providerId"], snapshot["datasetId"]
    if not isinstance(provider, str) or not provider.strip():
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: providerId must be non-empty")
    if not isinstance(dataset, str) or not dataset.strip():
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: datasetId must be non-empty")
    if snapshot["instrumentId"] != "FX_SPOT_USDJPY":
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: instrument must be FX_SPOT_USDJPY")
    if snapshot["timezone"] != "UTC":
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: timezone must be UTC")
    resolution = snapshot["resolutionSeconds"]
    if isinstance(resolution, bool) or not isinstance(resolution, int) or not 1 <= resolution <= MAX_RESOLUTION_SECONDS:
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: resolutionSeconds must be an integer from 1 through 60")
    coverage_start, coverage_end = parse_utc(snapshot["coverageStartUtc"]), parse_utc(snapshot["coverageEndUtc"])
    if coverage_start > coverage_end:
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: coverageStartUtc must be <= coverageEndUtc")
    if coverage_start > parse_utc(REQUIRED_COVERAGE_START_UTC) or coverage_end < parse_utc(REQUIRED_COVERAGE_END_UTC):
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: Candidate C required coverage is incomplete")
    raw_hashes = _validate_raw_artifact_hashes(snapshot["rawArtifactHashes"])
    quotes = snapshot["quotes"]
    if not isinstance(quotes, list):
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: quotes must be an array")
    if isinstance(snapshot["quoteCount"], bool) or not isinstance(snapshot["quoteCount"], int) or snapshot["quoteCount"] != len(quotes):
        raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: quoteCount must equal raw quotes array length")
    deduped: dict[datetime, FrozenMarketQuote] = {}
    for quote in quotes:
        if not isinstance(quote, Mapping):
            raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: quote must be an object")
        if not {"timestampUtc", "bid", "ask"}.issubset(quote):
            raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: quote requires timestampUtc, bid, and ask")
        timestamp = parse_utc(quote["timestampUtc"])
        if timestamp < coverage_start or timestamp > coverage_end:
            raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: quote timestamp is outside declared coverage")
        bid, ask = quote["bid"], quote["ask"]
        if isinstance(bid, bool) or isinstance(ask, bool) or not isinstance(bid, (int, float)) or not isinstance(ask, (int, float)):
            raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: bid and ask must be numeric")
        bid, ask = float(bid), float(ask)
        if not isfinite(bid) or not isfinite(ask) or bid <= 0 or ask <= 0 or ask < bid:
            raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: bid/ask must be positive finite values with ask >= bid")
        normalized = FrozenMarketQuote(timestamp_utc=quote["timestampUtc"], bid=bid, ask=ask)
        previous = deduped.get(timestamp)
        if previous is not None and previous != normalized:
            raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: conflicting timestamp duplicate")
        deduped[timestamp] = normalized
    admitted_quotes = tuple(deduped[key] for key in sorted(deduped))
    return ValidatedMarketSnapshot(
        market_snapshot_hash=expected_hash,
        provider_id=provider,
        dataset_id=dataset,
        instrument_id=snapshot["instrumentId"],
        coverage_start_utc=snapshot["coverageStartUtc"],
        coverage_end_utc=snapshot["coverageEndUtc"],
        resolution_seconds=resolution,
        raw_artifact_hashes=raw_hashes,
        raw_quote_count=snapshot["quoteCount"],
        admitted_quote_count=len(admitted_quotes),
        quotes=admitted_quotes,
    )


def validate_market_admission_record(
    record: Mapping[str, Any],
    snapshot: ValidatedMarketSnapshot,
    *,
    expected_snapshot_schema_hash: str,
    expected_market_data_admission_contract_hash: str,
) -> ValidatedMarketAdmissionRecord:
    """Validate a future self-hashed admission record against one snapshot."""

    required = {
        "schemaVersion", "admissionId", "admitted", "marketSnapshotHash", "providerId", "datasetId",
        "instrumentId", "coverageStartUtc", "coverageEndUtc", "resolutionSeconds", "rawArtifactHashes",
        "admissionRecordHash",
    }
    snapshot_schema_field = "emp0R3MarketSnapshotSchemaHash" if "emp0R3MarketSnapshotSchemaHash" in record else "emp0R2MarketSnapshotSchemaHash"
    admission_contract_field = "emp0R3MarketDataAdmissionContractHash" if "emp0R3MarketDataAdmissionContractHash" in record else "emp0R2MarketDataAdmissionContractHash"
    missing = sorted((required | {snapshot_schema_field, admission_contract_field}) - set(record))
    if missing:
        raise MarketContractError(f"MARKET_ADMISSION_RECORD_INVALID: missing required fields {missing}")
    expected_hash = _require_hash(record["admissionRecordHash"], "admissionRecordHash")
    if self_hash(dict(record), "admissionRecordHash") != expected_hash:
        raise MarketContractError("MARKET_ADMISSION_RECORD_INVALID: admissionRecordHash mismatch")
    if record["admitted"] is not True:
        raise MarketContractError("MARKET_ADMISSION_RECORD_INVALID: admitted must be true")
    bindings = {
        "marketSnapshotHash": snapshot.market_snapshot_hash,
        "providerId": snapshot.provider_id,
        "datasetId": snapshot.dataset_id,
        "instrumentId": snapshot.instrument_id,
        "coverageStartUtc": snapshot.coverage_start_utc,
        "coverageEndUtc": snapshot.coverage_end_utc,
        "resolutionSeconds": snapshot.resolution_seconds,
    }
    for field, expected in bindings.items():
        if record[field] != expected:
            raise MarketContractError(f"MARKET_ADMISSION_RECORD_INVALID: {field} does not bind the validated snapshot")
    if tuple(sorted(_validate_raw_artifact_hashes(record["rawArtifactHashes"]))) != snapshot.raw_artifact_hashes:
        raise MarketContractError("MARKET_ADMISSION_RECORD_INVALID: rawArtifactHashes do not bind the validated snapshot")
    if record[snapshot_schema_field] != expected_snapshot_schema_hash:
        raise MarketContractError("MARKET_ADMISSION_RECORD_INVALID: market snapshot schema binding mismatch")
    if record[admission_contract_field] != expected_market_data_admission_contract_hash:
        raise MarketContractError("MARKET_ADMISSION_RECORD_INVALID: market admission contract binding mismatch")
    if not isinstance(record["admissionId"], str) or not record["admissionId"].strip():
        raise MarketContractError("MARKET_ADMISSION_RECORD_INVALID: admissionId must be non-empty")
    return ValidatedMarketAdmissionRecord(record["admissionId"], expected_hash, snapshot.market_snapshot_hash)
