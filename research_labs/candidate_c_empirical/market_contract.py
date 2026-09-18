"""Fake-only validation for the frozen future bid/ask snapshot contract."""

from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from typing import Any, Mapping


MAX_RESOLUTION_SECONDS = 60


class MarketContractError(ValueError):
    """Raised for a future-snapshot schema violation."""


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise MarketContractError("timestamp must be an unambiguous UTC Z string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MarketContractError("timestamp is not ISO-8601 UTC") from exc
    if parsed.tzinfo != timezone.utc:
        raise MarketContractError("timestamp must resolve exactly to UTC")
    return parsed


def validate_fake_market_snapshot(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Validate synthetic bid/ask data; EMP0 never admits a real provider snapshot."""

    provider, dataset = snapshot.get("providerId"), snapshot.get("datasetId")
    if not isinstance(provider, str) or not provider.startswith("FAKE_MARKET_"):
        raise MarketContractError("EMP0 validator accepts FAKE_MARKET_ providers only")
    if not isinstance(dataset, str) or not dataset.startswith("FAKE_MARKET_"):
        raise MarketContractError("EMP0 validator accepts FAKE_MARKET_ datasets only")
    if snapshot.get("instrumentId") != "FX_SPOT_USDJPY":
        raise MarketContractError("instrument must be FX_SPOT_USDJPY")
    if snapshot.get("timezone") != "UTC":
        raise MarketContractError("snapshot timezone must be UTC")
    resolution = snapshot.get("resolutionSeconds")
    if not isinstance(resolution, int) or resolution <= 0 or resolution > MAX_RESOLUTION_SECONDS:
        raise MarketContractError("resolution must be an integer of 60 seconds or finer")
    quotes = snapshot.get("quotes")
    if not isinstance(quotes, list):
        raise MarketContractError("quotes must be a list")
    deduped: dict[datetime, dict[str, Any]] = {}
    for quote in quotes:
        if not isinstance(quote, Mapping):
            raise MarketContractError("quote must be an object")
        timestamp = parse_utc(quote.get("timestampUtc"))
        bid, ask = quote.get("bid"), quote.get("ask")
        if isinstance(bid, bool) or isinstance(ask, bool) or not isinstance(bid, (int, float)) or not isinstance(ask, (int, float)):
            raise MarketContractError("bid and ask must be finite numbers")
        bid, ask = float(bid), float(ask)
        if not isfinite(bid) or not isfinite(ask) or bid <= 0 or ask <= 0 or ask < bid:
            raise MarketContractError("bid/ask must be positive finite values with ask >= bid")
        normalized = {"timestampUtc": quote["timestampUtc"], "bid": bid, "ask": ask}
        existing = deduped.get(timestamp)
        if existing is not None and existing != normalized:
            raise MarketContractError("MARKET_DATA_SNAPSHOT_INVALID: conflicting timestamp duplicate")
        deduped[timestamp] = normalized
    return [deduped[key] for key in sorted(deduped)]
