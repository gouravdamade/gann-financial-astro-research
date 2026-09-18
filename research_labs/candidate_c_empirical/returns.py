"""Exact fake-only bid/ask midpoint return extraction for EMP0."""

from __future__ import annotations

from datetime import timedelta
from math import log
from typing import Any, Mapping, Sequence

from .market_contract import parse_utc


QUOTE_TOLERANCE_SECONDS = 60


def _first_quote_at_or_after(quotes: Sequence[Mapping[str, Any]], anchor: str, tolerance_seconds: int = QUOTE_TOLERANCE_SECONDS) -> Mapping[str, Any] | None:
    anchor_time = parse_utc(anchor)
    deadline = anchor_time + timedelta(seconds=tolerance_seconds)
    for quote in quotes:
        quote_time = parse_utc(str(quote["timestampUtc"]))
        if quote_time < anchor_time:
            continue
        if quote_time <= deadline:
            return quote
        return None
    return None


def midpoint(quote: Mapping[str, Any]) -> float:
    return (float(quote["bid"]) + float(quote["ask"])) / 2.0


def extract_forward_log_return(event_exact_utc: str, horizon_seconds: int, quotes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
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
        "p0TimestampUtc": p0_quote["timestampUtc"],
        "phTimestampUtc": ph_quote["timestampUtc"],
        "p0": p0,
        "ph": ph,
        "logReturn": log(ph / p0),
    }
