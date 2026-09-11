"""Offline-only parser for the source-adjudicated daily USDJPY BI5 format.

This module accepts caller-supplied bytes only.  It deliberately contains no
provider client, credential handling, downloader, or outcome-facing behavior.
"""

from __future__ import annotations

import hashlib
import json
import lzma
import struct
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Iterable


PARSER_CONTRACT = "MO_R4A_S3R1_R3_DUKASCOPY_DAILY_BI5_OFFLINE_PARSER_V1"
COMPRESSION_FRAMING = "PYTHON_LZMA_FORMAT_ALONE"
RECORD_STRUCT_FORMAT = ">IIIff"
RECORD_SIZE_BYTES = 20
USDJPY_SYMBOL = "USDJPY"
USDJPY_SCALE_DENOMINATOR = 1000
MILLISECONDS_PER_DAY = 86_400_000
CANONICAL_SERIALIZATION = "UTF8_JSON_LINES_SORTED_KEYS_NO_INSIGNIFICANT_WHITESPACE_ONE_RECORD_PER_LINE_TRAILING_LF"
_ALTERNATE_CONTAINER_MAGIC = b"\xfd7zXZ\x00"


class DukascopyTickParserError(ValueError):
    """A fail-closed decoding or native-record contract violation."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class ParsedDailyTick:
    """One native record with exact integers and IEEE-754 volume byte identities."""

    partition_id: str
    record_index: int
    timestamp_utc: datetime
    ask_native: int
    bid_native: int
    ask_volume: float
    bid_volume: float
    ask_volume_bits_hex: str
    bid_volume_bits_hex: str

    @property
    def ask(self) -> Decimal:
        return Decimal(self.ask_native) / Decimal(USDJPY_SCALE_DENOMINATOR)

    @property
    def bid(self) -> Decimal:
        return Decimal(self.bid_native) / Decimal(USDJPY_SCALE_DENOMINATOR)

    def canonical_record(self) -> dict[str, object]:
        return {
            "askNative": self.ask_native,
            "askVolumeBitsHex": self.ask_volume_bits_hex,
            "bidNative": self.bid_native,
            "bidVolumeBitsHex": self.bid_volume_bits_hex,
            "partitionId": self.partition_id,
            "recordIndex": self.record_index,
            "timestampUtc": format_timestamp_utc(self.timestamp_utc),
        }


def _partition_start_utc(partition_date_utc: date | datetime) -> datetime:
    if isinstance(partition_date_utc, datetime):
        if partition_date_utc.tzinfo is None or partition_date_utc.utcoffset() != timedelta(0):
            raise DukascopyTickParserError("INVALID_PARTITION_DATE", "datetime partition date must be timezone-aware UTC")
        value = partition_date_utc.astimezone(timezone.utc)
        if value.time() != time.min:
            raise DukascopyTickParserError("INVALID_PARTITION_DATE", "datetime partition date must be UTC midnight")
        return value
    if isinstance(partition_date_utc, date):
        return datetime.combine(partition_date_utc, time.min, tzinfo=timezone.utc)
    raise DukascopyTickParserError("INVALID_PARTITION_DATE", "partition date must be a date or UTC-midnight datetime")


def partition_id_for_date(partition_date_utc: date | datetime, *, symbol: str = USDJPY_SYMBOL) -> str:
    start = _partition_start_utc(partition_date_utc)
    if symbol != USDJPY_SYMBOL:
        raise DukascopyTickParserError("UNSUPPORTED_SYMBOL", "the frozen parser accepts USDJPY only")
    return f"{symbol}/{start.year:04d}/{start.month - 1:02d}/{start.day:02d}_ticks.bi5"


def format_timestamp_utc(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise DukascopyTickParserError("INVALID_CANONICAL_TIMESTAMP", "timestamp must be timezone-aware UTC")
    utc = value.astimezone(timezone.utc)
    if utc.microsecond % 1000:
        raise DukascopyTickParserError("INVALID_CANONICAL_TIMESTAMP", "timestamp must have millisecond precision")
    return f"{utc:%Y-%m-%dT%H:%M:%S}.{utc.microsecond // 1000:03d}Z"


def canonical_parsed_tick_json_lines(records: Iterable[ParsedDailyTick]) -> bytes:
    """Return the frozen, locale-independent parsed-record representation."""

    lines = [
        json.dumps(record.canonical_record(), ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        for record in records
    ]
    return ("".join(f"{line}\n" for line in lines)).encode("utf-8")


def parsed_ticks_sha256(records: Iterable[ParsedDailyTick]) -> str:
    return hashlib.sha256(canonical_parsed_tick_json_lines(records)).hexdigest().upper()


def _decompress_single_frozen_format(raw_bytes: bytes) -> bytes:
    if not raw_bytes:
        raise DukascopyTickParserError(
            "ZERO_BYTE_PAYLOAD_ACQUISITION_INCOMPLETE",
            "a supplied zero-byte payload is not the documented missing-key no-tick representation",
        )
    if raw_bytes.startswith(_ALTERNATE_CONTAINER_MAGIC):
        raise DukascopyTickParserError(
            "COMPRESSION_FORMAT_MISMATCH",
            "the supplied bytes identify a container outside the frozen daily BI5 framing",
        )
    try:
        return lzma.decompress(raw_bytes, format=lzma.FORMAT_ALONE)
    except lzma.LZMAError as exc:
        raise DukascopyTickParserError("COMPRESSION_DECODE_FAILED", "frozen LZMA decompression failed") from exc


def parse_daily_bi5(
    raw_bytes: bytes,
    *,
    partition_date_utc: date | datetime,
    symbol: str = USDJPY_SYMBOL,
) -> tuple[ParsedDailyTick, ...]:
    """Decode one caller-supplied daily partition in the single frozen format."""

    if not isinstance(raw_bytes, bytes):
        raise DukascopyTickParserError("INVALID_RAW_BYTES", "raw_bytes must be bytes")
    partition_start = _partition_start_utc(partition_date_utc)
    partition_id = partition_id_for_date(partition_start, symbol=symbol)
    decompressed = _decompress_single_frozen_format(raw_bytes)
    if not decompressed:
        raise DukascopyTickParserError(
            "ZERO_DECODED_RECORDS_ACQUISITION_INCOMPLETE",
            "a decoded empty stream is not a valid no-tick partition",
        )
    if len(decompressed) % RECORD_SIZE_BYTES:
        raise DukascopyTickParserError(
            "RAW_RECORD_ALIGNMENT_INVALID",
            f"decoded payload length {len(decompressed)} is not a multiple of {RECORD_SIZE_BYTES}",
        )

    partition_end = partition_start + timedelta(days=1)
    records: list[ParsedDailyTick] = []
    for record_index, offset in enumerate(range(0, len(decompressed), RECORD_SIZE_BYTES)):
        record_bytes = decompressed[offset : offset + RECORD_SIZE_BYTES]
        milliseconds, ask_native, bid_native, ask_volume, bid_volume = struct.unpack(RECORD_STRUCT_FORMAT, record_bytes)
        if not 0 <= milliseconds < MILLISECONDS_PER_DAY:
            raise DukascopyTickParserError(
                "NATIVE_TIMESTAMP_OUT_OF_PARTITION",
                f"record {record_index} has millisecond offset {milliseconds}",
            )
        timestamp_utc = partition_start + timedelta(milliseconds=milliseconds)
        if not partition_start <= timestamp_utc < partition_end:
            raise DukascopyTickParserError(
                "NATIVE_TIMESTAMP_OUT_OF_PARTITION",
                f"record {record_index} reconstructed outside the native day",
            )
        if bid_native <= 0 or ask_native <= 0 or ask_native < bid_native:
            raise DukascopyTickParserError(
                "NATIVE_QUOTE_INVALID",
                f"record {record_index} has ask={ask_native} and bid={bid_native}",
            )
        records.append(
            ParsedDailyTick(
                partition_id=partition_id,
                record_index=record_index,
                timestamp_utc=timestamp_utc,
                ask_native=ask_native,
                bid_native=bid_native,
                ask_volume=ask_volume,
                bid_volume=bid_volume,
                ask_volume_bits_hex=record_bytes[12:16].hex().upper(),
                bid_volume_bits_hex=record_bytes[16:20].hex().upper(),
            )
        )
    return tuple(records)
