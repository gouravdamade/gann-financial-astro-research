"""Focused, network-free checks for EMP1 market-only acquisition helpers."""

from __future__ import annotations

from datetime import date, datetime, timezone
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ACQUIRE = _load("candidate_c_emp1_acquire_market_data", "tools/research/candidate_c_emp1_acquire_market_data.py")
BUILD = _load("candidate_c_emp1_build_market_snapshot", "tools/research/candidate_c_emp1_build_market_snapshot.py")


def test_zero_indexed_dukascopy_month_path_uses_april_for_may() -> None:
    assert ACQUIRE.date_key(date(2025, 5, 1)) == "USDJPY/2025/04/01_ticks.bi5"
    assert ACQUIRE.date_key(date(2025, 8, 1)) == "USDJPY/2025/07/01_ticks.bi5"


def test_saturday_is_recorded_as_a_documented_closure_without_provider_call(tmp_path: Path) -> None:
    record = ACQUIRE.acquire_one(None, date(2025, 5, 3), tmp_path, {})
    assert record["status"] == "DOCUMENTED_WEEKEND_MARKET_CLOSED_NO_PROVIDER_OBJECT_REQUESTED"
    assert record["closureReason"] == "DOCUMENTED_FX_SATURDAY_MARKET_CLOSURE"
    assert not list(tmp_path.iterdir())


def test_snapshot_prefix_preserves_canonical_key_order_without_self_hash() -> None:
    prefix = BUILD.snapshot_prefix(include_hash=None, quote_count=3)
    assert prefix == (
        '{"coverageEndUtc":"2025-08-01T23:20:56Z","coverageStartUtc":"2025-05-01T01:58:38Z",'
        '"datasetId":"DUKASCOPY_USDJPY_DAILY_TICKS_BI5","instrumentId":"FX_SPOT_USDJPY",'
        '"providerId":"DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE",'
        '"quoteCount":3,"quotes":['
    )


def test_documented_weekend_gap_is_distinct_from_an_intraday_interquote_interval() -> None:
    friday = datetime(2025, 5, 2, 20, 59, tzinfo=timezone.utc)
    sunday = datetime(2025, 5, 4, 21, 0, tzinfo=timezone.utc)
    intraday = datetime(2025, 5, 2, 21, 5, tzinfo=timezone.utc)
    assert BUILD.is_documented_weekend_gap(friday, sunday)
    assert not BUILD.is_documented_weekend_gap(friday, intraday)
