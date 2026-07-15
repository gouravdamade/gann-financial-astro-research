from __future__ import annotations

import math
from statistics import median
from typing import Any

import pandas as pd


CANDLESTICK_EVIDENCE_CONTRACT = "GANN_CANDLESTICK_EVIDENCE_V1"
METHODOLOGY_VERSION = "transparent_ohlc_geometry_v1"
PIP_FACTOR_BY_SYMBOL = {"USDJPY": 100.0}


def _number(value: Any, digits: int = 5) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number, digits) if math.isfinite(number) else None


def _utc(value: Any) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _validated_frame(candles: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for candle in candles:
        try:
            timestamp = pd.to_datetime(int(candle["time"]), unit="s", utc=True)
            open_ = float(candle["open"])
            high = float(candle["high"])
            low = float(candle["low"])
            close = float(candle["close"])
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        values = (open_, high, low, close)
        if not all(math.isfinite(item) for item in values):
            continue
        if high < max(open_, close) or low > min(open_, close) or high < low:
            continue
        rows.append(
            {
                "time": timestamp,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": int(candle.get("volume") or 0),
            }
        )
    if not rows:
        raise ValueError("No valid OHLC candles are available for candlestick analysis")
    return pd.DataFrame(rows).drop_duplicates("time", keep="last").sort_values("time").reset_index(drop=True)


def _bar_seconds(frame: pd.DataFrame, timeframe: str) -> int:
    differences = frame["time"].diff().dropna().dt.total_seconds()
    positive = [int(value) for value in differences if math.isfinite(value) and value > 0]
    if positive:
        return max(60, int(median(positive)))
    return {"M30": 1800, "H1": 3600, "H4": 14400, "D1": 86400}.get(timeframe.upper(), 3600)


def _true_ranges(frame: pd.DataFrame) -> list[float]:
    output: list[float] = []
    previous_close: float | None = None
    for row in frame.itertuples(index=False):
        candidates = [float(row.high) - float(row.low)]
        if previous_close is not None:
            candidates.extend(
                [abs(float(row.high) - previous_close), abs(float(row.low) - previous_close)]
            )
        output.append(max(candidates))
        previous_close = float(row.close)
    return output


def _trend_before(frame: pd.DataFrame, index: int, atr: float) -> tuple[str, float]:
    prior = frame.iloc[max(0, index - 5) : index]
    if len(prior) < 3:
        return "insufficient", 0.0
    delta = float(prior.iloc[-1]["close"] - prior.iloc[0]["close"])
    scale = max(float(atr), float(prior["high"].sub(prior["low"]).median()), 1e-9)
    strength = delta / scale
    if strength >= 0.25:
        return "up", strength
    if strength <= -0.25:
        return "down", strength
    return "sideways", strength


def _pattern(
    name: str,
    bias: str,
    basis: str,
    context: str,
) -> dict[str, str]:
    return {"name": name, "hypothesisBias": bias, "basis": basis, "context": context}


def _patterns_for_bar(
    frame: pd.DataFrame,
    index: int,
    *,
    body: float,
    candle_range: float,
    upper: float,
    lower: float,
    body_fraction: float,
    trend: str,
    median_body: float,
) -> list[dict[str, str]]:
    row = frame.iloc[index]
    open_ = float(row["open"])
    close = float(row["close"])
    direction = "bullish" if close > open_ else "bearish" if close < open_ else "neutral"
    patterns: list[dict[str, str]] = []
    if body_fraction <= 0.10:
        patterns.append(_pattern("doji", "neutral", "body <= 10% of range", "indecision geometry"))
    if body_fraction <= 0.30 and upper >= 0.25 * candle_range and lower >= 0.25 * candle_range:
        patterns.append(
            _pattern("spinning_top", "neutral", "small body with two material wicks", "indecision geometry")
        )
    if body_fraction >= 0.90:
        patterns.append(
            _pattern("marubozu_like", direction, "body >= 90% of range", "strong close-location geometry")
        )
    if body_fraction >= 0.60 and body >= 1.5 * max(median_body, 1e-9):
        patterns.append(
            _pattern(
                f"long_{direction}_body",
                direction,
                "body >= 60% of range and 1.5x prior median body",
                "relative expansion geometry",
            )
        )
    wick_floor = max(body, candle_range * 0.03)
    if lower >= 2.0 * wick_floor and upper <= 0.20 * candle_range:
        bias = "bullish" if trend == "down" else "bearish" if trend == "up" else "neutral"
        context = "hammer context" if trend == "down" else "hanging-man context" if trend == "up" else "trend unconfirmed"
        patterns.append(_pattern("long_lower_wick", bias, "lower wick >= 2x body; short upper wick", context))
    if upper >= 2.0 * wick_floor and lower <= 0.20 * candle_range:
        bias = "bearish" if trend == "up" else "bullish" if trend == "down" else "neutral"
        context = "shooting-star context" if trend == "up" else "inverted-hammer context" if trend == "down" else "trend unconfirmed"
        patterns.append(_pattern("long_upper_wick", bias, "upper wick >= 2x body; short lower wick", context))
    if index <= 0:
        return patterns
    prior = frame.iloc[index - 1]
    prior_open = float(prior["open"])
    prior_close = float(prior["close"])
    prior_body = abs(prior_close - prior_open)
    if body > 0 and prior_body > 0:
        if close > open_ and prior_close < prior_open and open_ <= prior_close and close >= prior_open:
            patterns.append(
                _pattern("bullish_body_engulfing", "bullish", "current real body engulfs prior bearish body", f"pre-trend {trend}")
            )
        if close < open_ and prior_close > prior_open and open_ >= prior_close and close <= prior_open:
            patterns.append(
                _pattern("bearish_body_engulfing", "bearish", "current real body engulfs prior bullish body", f"pre-trend {trend}")
            )
    if float(row["high"]) <= float(prior["high"]) and float(row["low"]) >= float(prior["low"]):
        patterns.append(_pattern("inside_bar", "neutral", "range is inside prior range", "compression geometry"))
    if float(row["high"]) >= float(prior["high"]) and float(row["low"]) <= float(prior["low"]):
        patterns.append(_pattern("outside_bar", direction, "range contains prior range", "range expansion geometry"))
    return patterns


def _records(frame: pd.DataFrame, bar_seconds: int, pip_factor: float) -> list[dict[str, Any]]:
    true_ranges = _true_ranges(frame)
    records: list[dict[str, Any]] = []
    for index, row in frame.iterrows():
        open_ = float(row["open"])
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        candle_range = max(high - low, 1e-9)
        body = abs(close - open_)
        upper = high - max(open_, close)
        lower = min(open_, close) - low
        prior = frame.iloc[max(0, index - 20) : index]
        prior_bodies = [abs(float(item.close) - float(item.open)) for item in prior.itertuples(index=False)]
        median_body = median(prior_bodies) if prior_bodies else body
        atr_values = true_ranges[max(0, index - 13) : index + 1]
        atr = sum(atr_values) / len(atr_values)
        prior_atr_values = true_ranges[max(0, index - 14) : index]
        prior_atr = sum(prior_atr_values) / len(prior_atr_values) if prior_atr_values else atr
        trend, trend_strength = _trend_before(frame, index, prior_atr)
        patterns = _patterns_for_bar(
            frame,
            index,
            body=body,
            candle_range=candle_range,
            upper=upper,
            lower=lower,
            body_fraction=body / candle_range,
            trend=trend,
            median_body=median_body,
        )
        start = pd.Timestamp(row["time"])
        records.append(
            {
                "startTime": start.isoformat(),
                "closeTime": (start + pd.Timedelta(seconds=bar_seconds)).isoformat(),
                "open": _number(open_),
                "high": _number(high),
                "low": _number(low),
                "close": _number(close),
                "direction": "bullish" if close > open_ else "bearish" if close < open_ else "flat",
                "rangePips": _number(candle_range * pip_factor, 2),
                "bodyPips": _number(body * pip_factor, 2),
                "bodyFraction": _number(body / candle_range, 4),
                "upperWickFraction": _number(upper / candle_range, 4),
                "lowerWickFraction": _number(lower / candle_range, 4),
                "closeLocation": _number((close - low) / candle_range, 4),
                "atr14Pips": _number(atr * pip_factor, 2),
                "preTrend": trend,
                "preTrendStrengthAtr": _number(trend_strength, 3),
                "patterns": patterns,
            }
        )
    return records


def _window_summary(records: list[dict[str, Any]], pip_factor: float) -> dict[str, Any]:
    if not records:
        return {"barCount": 0, "movePips": None, "high": None, "low": None, "patterns": []}
    patterns = [
        {"time": record["closeTime"], **pattern}
        for record in records
        for pattern in record["patterns"]
    ]
    return {
        "barCount": len(records),
        "open": records[0]["open"],
        "high": max(float(record["high"]) for record in records),
        "low": min(float(record["low"]) for record in records),
        "close": records[-1]["close"],
        "movePips": _number((float(records[-1]["close"]) - float(records[0]["open"])) * pip_factor, 2),
        "patterns": patterns,
    }


def build_candlestick_evidence(
    detail: dict[str, Any],
    annotation_id: str | None = None,
) -> dict[str, Any]:
    event = detail.get("event") if isinstance(detail.get("event"), dict) else {}
    chart = detail.get("chart") if isinstance(detail.get("chart"), dict) else {}
    frame = _validated_frame(chart.get("candles") if isinstance(chart.get("candles"), list) else [])
    timeframe = str(chart.get("timeframe") or "H1").upper()
    symbol = str(chart.get("symbol") or "USDJPY").upper()
    pip_factor = PIP_FACTOR_BY_SYMBOL.get(symbol, 1.0)
    bar_seconds = _bar_seconds(frame, timeframe)
    records = _records(frame, bar_seconds, pip_factor)
    if not event.get("startIso") or not event.get("endIso"):
        raise ValueError("Event startIso and endIso are required for timestamp-safe analysis")
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
    for record in records:
        record["_start"] = _utc(record["startTime"])
        record["_close"] = _utc(record["closeTime"])
    closed_at_cutoff = [record for record in records if record["_close"] <= cutoff]
    event_records = [
        record
        for record in records
        if record["_start"] < event_end
        and record["_close"] > event_start
        and record["_close"] <= cutoff
    ]
    focus = closed_at_cutoff[-1] if closed_at_cutoff else None
    hindsight_records = [record for record in records if record["_close"] > cutoff][:6]
    event_summary = _window_summary(event_records, pip_factor)
    hindsight_summary = _window_summary(hindsight_records, pip_factor)
    reference_price = float(focus["close"]) if focus else None
    if reference_price is not None and hindsight_records:
        hindsight_summary.update(
            {
                "referencePrice": _number(reference_price),
                "closeMoveFromCutoffPips": _number(
                    (float(hindsight_records[-1]["close"]) - reference_price) * pip_factor, 2
                ),
                "maxUpFromCutoffPips": _number(
                    (max(float(record["high"]) for record in hindsight_records) - reference_price) * pip_factor,
                    2,
                ),
                "maxDownFromCutoffPips": _number(
                    (min(float(record["low"]) for record in hindsight_records) - reference_price) * pip_factor,
                    2,
                ),
            }
        )
    for record in records:
        record.pop("_start", None)
        record.pop("_close", None)
    return {
        "contract": CANDLESTICK_EVIDENCE_CONTRACT,
        "methodologyVersion": METHODOLOGY_VERSION,
        "eventId": str(event.get("eventId") or ""),
        "symbol": symbol,
        "timeframe": timeframe,
        "barSeconds": bar_seconds,
        "eventStart": event_start.isoformat(),
        "eventEnd": event_end.isoformat(),
        "analysisCutoff": cutoff.isoformat(),
        "selectedAnnotationId": str(annotation_id or ""),
        "closedBarCountAtCutoff": len(closed_at_cutoff),
        "focusBar": focus,
        "eventWindow": event_summary,
        "hindsight": {
            "available": bool(hindsight_records),
            "label": "Retrospective only; unavailable at the analysis cutoff",
            **hindsight_summary,
        },
        "guardrails": {
            "analysisOnly": True,
            "closedBarsOnlyAtCutoff": True,
            "hindsightSeparated": True,
            "patternIsNotTradeSignal": True,
            "consumedByLiveInference": False,
            "consumedByShadowLedger": False,
            "executionAllowed": False,
        },
    }
