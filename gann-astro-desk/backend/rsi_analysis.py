from __future__ import annotations

import math
from statistics import median
from typing import Any, Iterable

import pandas as pd


RSI_EVIDENCE_CONTRACT = "GANN_RSI_EVIDENCE_V1"
RSI_METHODOLOGY_VERSION = "wilder_smoothed_close_v1"
DEFAULT_RSI_LEVELS = (30.0, 50.0, 70.0)


def _utc(value: Any) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _number(value: Any, digits: int = 3) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number, digits) if math.isfinite(number) else None


def _validated_frame(candles: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for candle in candles:
        try:
            timestamp = pd.to_datetime(int(candle["time"]), unit="s", utc=True)
            close = float(candle["close"])
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        if not math.isfinite(close):
            continue
        rows.append({"time": timestamp, "close": close})
    if not rows:
        raise ValueError("No valid close-price candles are available for RSI analysis")
    return (
        pd.DataFrame(rows)
        .drop_duplicates("time", keep="last")
        .sort_values("time")
        .reset_index(drop=True)
    )


def _bar_seconds(frame: pd.DataFrame, timeframe: str) -> int:
    differences = frame["time"].diff().dropna().dt.total_seconds()
    positive = [int(value) for value in differences if math.isfinite(value) and value > 0]
    if positive:
        return max(60, int(median(positive)))
    return {
        "M30": 1800,
        "H1": 3600,
        "H4": 14400,
        "D1": 86400,
        "W1": 604800,
    }.get(timeframe.upper(), 3600)


def normalize_rsi_levels(levels: Iterable[Any] | None) -> tuple[float, ...]:
    output: list[float] = []
    for value in levels or DEFAULT_RSI_LEVELS:
        try:
            level = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(level) or level < 0 or level > 100:
            continue
        rounded = round(level, 3)
        if rounded not in output:
            output.append(rounded)
    return tuple(sorted(output)) or DEFAULT_RSI_LEVELS


def wilder_rsi_values(closes: Iterable[Any], period: int = 14) -> list[float | None]:
    if period < 2 or period > 200:
        raise ValueError("RSI period must be between 2 and 200")
    values = [float(value) for value in closes]
    if any(not math.isfinite(value) for value in values):
        raise ValueError("RSI closes must be finite numbers")
    result: list[float | None] = [None] * len(values)
    if len(values) <= period:
        return result
    deltas = [values[index] - values[index - 1] for index in range(1, len(values))]
    average_gain = sum(max(delta, 0.0) for delta in deltas[:period]) / period
    average_loss = sum(max(-delta, 0.0) for delta in deltas[:period]) / period

    def score(gain: float, loss: float) -> float:
        if gain == 0 and loss == 0:
            return 50.0
        if loss == 0:
            return 100.0
        if gain == 0:
            return 0.0
        relative_strength = gain / loss
        return 100.0 - (100.0 / (1.0 + relative_strength))

    result[period] = score(average_gain, average_loss)
    for index in range(period + 1, len(values)):
        delta = deltas[index - 1]
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)
        average_gain = ((average_gain * (period - 1)) + gain) / period
        average_loss = ((average_loss * (period - 1)) + loss) / period
        result[index] = score(average_gain, average_loss)
    return result


def _zone(value: float | None) -> str:
    if value is None:
        return "unavailable"
    if value >= 70:
        return "at_or_above_70"
    if value <= 30:
        return "at_or_below_30"
    if value >= 50:
        return "above_midline"
    return "below_midline"


def build_rsi_evidence(
    detail: dict[str, Any],
    annotation_id: str | None = None,
    *,
    period: int = 14,
    levels: Iterable[Any] | None = None,
) -> dict[str, Any]:
    if period < 2 or period > 200:
        raise ValueError("RSI period must be between 2 and 200")
    event = detail.get("event") if isinstance(detail.get("event"), dict) else {}
    chart = detail.get("chart") if isinstance(detail.get("chart"), dict) else {}
    frame = _validated_frame(chart.get("candles") if isinstance(chart.get("candles"), list) else [])
    timeframe = str(chart.get("timeframe") or "H1").upper()
    symbol = str(chart.get("symbol") or "USDJPY").upper()
    bar_seconds = _bar_seconds(frame, timeframe)
    if not event.get("startIso") or not event.get("endIso"):
        raise ValueError("Event startIso and endIso are required for timestamp-safe RSI analysis")
    event_start = _utc(event.get("startIso"))
    event_end = _utc(event.get("endIso"))
    selected_annotation = next(
        (
            item
            for item in detail.get("annotations", [])
            if isinstance(item, dict) and str(item.get("annotationId")) == str(annotation_id)
        ),
        None,
    )
    annotation_time = selected_annotation.get("anchorTimeUtc") if selected_annotation else None
    cutoff = _utc(annotation_time) if annotation_time else event_end
    normalized_levels = normalize_rsi_levels(levels)
    values = wilder_rsi_values(frame["close"].tolist(), period)

    records: list[dict[str, Any]] = []
    for row, value in zip(frame.itertuples(index=False), values, strict=True):
        close_time = _utc(row.time) + pd.Timedelta(seconds=bar_seconds)
        records.append(
            {
                "barOpenTime": _utc(row.time),
                "barCloseTime": close_time,
                "close": float(row.close),
                "value": value,
            }
        )
    closed_at_cutoff = [record for record in records if record["barCloseTime"] <= cutoff]
    available = [record for record in closed_at_cutoff if record["value"] is not None]
    focus = available[-1] if available else None
    event_records = [
        record
        for record in available
        if record["barOpenTime"] < event_end
        and record["barCloseTime"] > event_start
    ]
    crossings: list[dict[str, Any]] = []
    for previous, current in zip(available, available[1:]):
        if current["barCloseTime"] <= event_start or current["barOpenTime"] >= event_end:
            continue
        previous_value = float(previous["value"])
        current_value = float(current["value"])
        for level in normalized_levels:
            direction = "up" if previous_value < level <= current_value else "down" if previous_value > level >= current_value else ""
            if direction:
                crossings.append(
                    {
                        "level": level,
                        "direction": direction,
                        "time": current["barCloseTime"].isoformat(),
                        "from": _number(previous_value),
                        "to": _number(current_value),
                    }
                )
    focus_value = float(focus["value"]) if focus else None
    nearest_level = min(normalized_levels, key=lambda level: abs(level - focus_value)) if focus_value is not None else None
    event_values = [float(record["value"]) for record in event_records]
    return {
        "contract": RSI_EVIDENCE_CONTRACT,
        "methodologyVersion": RSI_METHODOLOGY_VERSION,
        "eventId": str(event.get("eventId") or ""),
        "symbol": symbol,
        "timeframe": timeframe,
        "source": "close",
        "period": period,
        "levels": list(normalized_levels),
        "barSeconds": bar_seconds,
        "eventStart": event_start.isoformat(),
        "eventEnd": event_end.isoformat(),
        "analysisCutoff": cutoff.isoformat(),
        "selectedAnnotationId": str(annotation_id or ""),
        "closedBarCountAtCutoff": len(closed_at_cutoff),
        "warmupBarsRequired": period + 1,
        "ready": focus is not None,
        "focus": None
        if focus is None
        else {
            "barOpenTime": focus["barOpenTime"].isoformat(),
            "barCloseTime": focus["barCloseTime"].isoformat(),
            "close": _number(focus["close"], 5),
            "value": _number(focus_value),
            "zone": _zone(focus_value),
            "nearestLevel": nearest_level,
            "distanceToNearestLevel": _number(focus_value - nearest_level) if nearest_level is not None else None,
        },
        "eventWindow": {
            "sampleCount": len(event_values),
            "startValue": _number(event_values[0]) if event_values else None,
            "endValue": _number(event_values[-1]) if event_values else None,
            "minimum": _number(min(event_values)) if event_values else None,
            "maximum": _number(max(event_values)) if event_values else None,
            "change": _number(event_values[-1] - event_values[0]) if len(event_values) >= 2 else None,
            "crossings": crossings,
        },
        "guardrails": {
            "analysisOnly": True,
            "closedBarsOnlyAtCutoff": True,
            "wilderMethodExplicit": True,
            "levelTouchIsNotReversalProof": True,
            "consumedByLiveInference": False,
            "consumedByShadowLedger": False,
            "executionAllowed": False,
        },
    }
