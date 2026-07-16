from __future__ import annotations

import math


SUPPORTED_CHART_TIMEFRAMES = ("M30", "H1", "H4", "D1", "W1")
ASPECT_DURATION_MODES = ("auto", "manual")
TIMEFRAME_BAR_MINUTES = {
    "M30": 30.0,
    "H1": 60.0,
    "H4": 240.0,
    "D1": 1440.0,
    "W1": 10080.0,
}


def normalize_aspect_duration_mode(value: object) -> str:
    normalized = str(value or "auto").strip().lower()
    if normalized not in ASPECT_DURATION_MODES:
        raise ValueError(f"unsupported aspect duration mode: {value}")
    return normalized


def effective_aspect_min_duration_minutes(
    timeframe: str,
    mode: object = "auto",
    requested_minutes: object = 0.0,
) -> float:
    normalized_timeframe = str(timeframe or "").strip().upper()
    if normalized_timeframe not in TIMEFRAME_BAR_MINUTES:
        raise ValueError(f"unsupported chart timeframe: {timeframe}")
    normalized_mode = normalize_aspect_duration_mode(mode)
    if normalized_mode == "auto":
        return TIMEFRAME_BAR_MINUTES[normalized_timeframe]
    try:
        requested = float(requested_minutes or 0.0)
    except (TypeError, ValueError) as exc:
        raise ValueError("manual aspect minimum duration must be numeric") from exc
    if not math.isfinite(requested) or requested < 0:
        raise ValueError("manual aspect minimum duration must be finite and non-negative")
    return requested
