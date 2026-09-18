"""Exact fake-only bid/ask midpoint return extraction for EMP0."""

from __future__ import annotations

from datetime import timedelta
from math import log
from typing import Any, Mapping, Sequence

from .market_contract import FrozenMarketQuote, parse_utc


QUOTE_TOLERANCE_SECONDS = 60


Quote = FrozenMarketQuote | Mapping[str, Any]


def _timestamp(quote: Quote) -> str:
    return quote.timestamp_utc if isinstance(quote, FrozenMarketQuote) else str(quote["timestampUtc"])


def _bid(quote: Quote) -> float:
    return quote.bid if isinstance(quote, FrozenMarketQuote) else float(quote["bid"])


def _ask(quote: Quote) -> float:
    return quote.ask if isinstance(quote, FrozenMarketQuote) else float(quote["ask"])


def _first_quote_at_or_after(quotes: Sequence[Quote], anchor: str, tolerance_seconds: int = QUOTE_TOLERANCE_SECONDS) -> Quote | None:
    anchor_time = parse_utc(anchor)
    deadline = anchor_time + timedelta(seconds=tolerance_seconds)
    for quote in quotes:
        quote_time = parse_utc(_timestamp(quote))
        if quote_time < anchor_time:
            continue
        if quote_time <= deadline:
            return quote
        return None
    return None


def midpoint(quote: Quote) -> float:
    return (_bid(quote) + _ask(quote)) / 2.0


def extract_forward_log_return(event_exact_utc: str, horizon_seconds: int, quotes: Sequence[Quote]) -> dict[str, Any]:
    """Use first quote at/after t and t+H; never interpolate or substitute."""

    event_time = parse_utc(event_exact_utc)
    p0_quote = _first_quote_at_or_after(quotes, event_exact_utc)
    horizon_anchor = (event_time + timedelta(seconds=horizon_seconds)).isoformat().replace("+00:00", "Z")
    ph_quote = _first_quote_at_or_after(quotes, horizon_anchor)
    if p0_quote is None or ph_quote is None:
        return {"status": "MARKET_QUOTE_UNAVAILABLE", "eventExactUtc": event_exact_utc, "horizonSeconds": horizon_seconds}
    p0, ph = midpoint(p0_quote), midpoint(ph_quote)
    return {
        "status": "MARKET_RETURN_AVAILABLE",
        "eventExactUtc": event_exact_utc,
        "horizonSeconds": horizon_seconds,
        "p0TimestampUtc": _timestamp(p0_quote),
        "phTimestampUtc": _timestamp(ph_quote),
        "p0": p0,
        "ph": ph,
        "logReturn": log(ph / p0),
    }
