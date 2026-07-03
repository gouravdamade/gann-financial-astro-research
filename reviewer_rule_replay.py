from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import struct
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_PACK_ROOT = Path(r"D:\GannFinancialAstro\doc")
DEFAULT_PACK_GLOB = "repeatation_review_case_8_avg_all_moon_square_*"


@dataclass(frozen=True)
class ReplayExpectation:
    case_id: int
    start_rule: str
    start_ist: str
    end_ist: str | None = None
    end_rule: str | None = None
    outcome_label: str | None = None
    signed_pips: float | None = None
    gann_anchor_side: str | None = None
    min_case_window_sr_touches: int | None = None


EXPECTATIONS: dict[int, ReplayExpectation] = {
    127: ReplayExpectation(
        case_id=127,
        start_rule="first_case_window_sr_line_touch",
        start_ist="2025-05-28T22:00:00+05:30",
        end_ist="2025-05-28T23:00:00+05:30",
        end_rule="gann_second_from_bottom_touch_multi_aspect",
        outcome_label="bearish",
        signed_pips=4.0,
        gann_anchor_side="top",
        min_case_window_sr_touches=3,
    ),
}


FAMILY_RULE_GUARDS: dict[int, list[str]] = {
    8: [
        "Applied family rule bearish_bias_support_barrier plus confirmed-break logic",
        "next shaded-zone boundary",
        "candidateAuditItem('next shaded zone'",
    ],
    43: [
        "Applied family rule bearish_bias_support_barrier plus confirmed-break logic",
        "next shaded-zone boundary",
        "candidateAuditItem('next shaded zone'",
    ],
    103: [
        "Applied family rule bearish_bias_support_barrier plus global exit rule",
        "first lower SR touch",
        "candidateAuditItem('first SR target'",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic replay/regression checks for the repeatation reviewer. "
            "v1 parses generated Plotly chart data and checks the actively taught cases."
        )
    )
    parser.add_argument("--pack-dir", type=Path, default=None, help="Specific repeatation review pack directory.")
    parser.add_argument("--pack-root", type=Path, default=DEFAULT_PACK_ROOT)
    parser.add_argument("--case-id", type=int, action="append", help="Limit checks to one or more case ids.")
    return parser.parse_args()


def latest_pack(root: Path) -> Path:
    candidates = [p for p in root.glob(DEFAULT_PACK_GLOB) if p.is_dir()]
    if not candidates:
        raise SystemExit(f"No review pack found under {root} matching {DEFAULT_PACK_GLOB}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def iso_ms(value: str) -> int:
    cleaned = str(value).replace("Z", "+00:00")
    if "." in cleaned and "+" not in cleaned.split(".")[-1] and "-" not in cleaned.split(".")[-1]:
        cleaned = cleaned.split(".", 1)[0]
    if re.search(r"\.\d{6}$", cleaned):
        cleaned = cleaned.split(".", 1)[0]
    if re.search(r"T\d{2}:\d{2}:\d{2}$", cleaned):
        cleaned += "+05:30"
    return int(datetime.fromisoformat(cleaned).timestamp() * 1000)


def canonical_ist(value: str) -> str:
    text = str(value)
    if "." in text:
        head, tail = text.split(".", 1)
        if "+" in tail:
            text = head + "+" + tail.split("+", 1)[1]
        elif "-" in tail:
            text = head + "-" + tail.split("-", 1)[1]
        else:
            text = head
    if re.search(r"T\d{2}:\d{2}:\d{2}$", text):
        return text + "+05:30"
    return text


def decode_array(values: Any) -> list[Any]:
    if isinstance(values, list):
        return values
    if not isinstance(values, dict):
        return []
    bdata = values.get("bdata")
    dtype = str(values.get("dtype") or "").lower()
    if not bdata:
        return []
    raw = base64.b64decode(str(bdata))
    if dtype in {"f8", "float64"}:
        return [item[0] for item in struct.iter_unpack("<d", raw)]
    if dtype in {"f4", "float32"}:
        return [item[0] for item in struct.iter_unpack("<f", raw)]
    if dtype in {"i4", "int32"}:
        return [item[0] for item in struct.iter_unpack("<i", raw)]
    if dtype in {"u4", "uint32"}:
        return [item[0] for item in struct.iter_unpack("<I", raw)]
    return []


def array_value(values: Any, index: int) -> Any:
    decoded = decode_array(values)
    if 0 <= index < len(decoded):
        return decoded[index]
    return None


def plotly_data(html_text: str) -> list[dict[str, Any]]:
    match = re.search(r"Plotly\.newPlot\(\s*\"[^\"]+\"\s*,\s*", html_text)
    if not match:
        raise ValueError("Plotly.newPlot data block not found")
    decoder = json.JSONDecoder()
    data, _ = decoder.raw_decode(html_text[match.end() :])
    if not isinstance(data, list):
        raise ValueError("Plotly.newPlot data block is not a list")
    return data


def trace_looks_like_marker(trace: dict[str, Any]) -> bool:
    mode = str(trace.get("mode") or "").lower()
    name = str(trace.get("name") or "").lower()
    trace_type = str(trace.get("type") or "").lower()
    if "markers" not in mode:
        return False
    if trace.get("visible") is False:
        return False
    return (
        "interaction" in name
        or "selected case" in name
        or "touch" in name
        or trace_type == "scattergl"
    )


def trace_looks_like_sr_line(trace: dict[str, Any]) -> bool:
    if trace.get("visible") is False or not trace.get("x") or not trace.get("y"):
        return False
    if str(trace.get("type") or "").lower() != "scatter":
        return False
    if "lines" not in str(trace.get("mode") or "").lower():
        return False
    if str(trace.get("fill") or ""):
        return False
    name = str(trace.get("name") or "").lower()
    if "selected case" in name or "gann" in name:
        return False
    return len(decode_array(trace.get("x")) or trace.get("x") or []) > 1


def custom_data_label(customdata: Any) -> str:
    if isinstance(customdata, list):
        for index in (4, 5, 0):
            if index < len(customdata) and customdata[index]:
                return str(customdata[index])[:160]
    return str(customdata or "")[:160]


def trace_array(values: Any) -> list[Any]:
    decoded = decode_array(values)
    if decoded:
        return decoded
    if isinstance(values, list):
        return values
    return []


def trace_looks_like_zone(trace: dict[str, Any]) -> bool:
    if trace.get("visible") is False or not trace.get("x") or not trace.get("y"):
        return False
    fill = str(trace.get("fill") or "").lower()
    name = str(trace.get("name") or "").lower()
    label = custom_data_label(array_value(trace.get("customdata"), 0)).lower() if trace.get("customdata") else ""
    return fill == "toself" and (
        "window" in name
        or "zone" in name
        or "aspect_window" in label
        or "regime" in label
    )


def trace_looks_like_aspect_window(trace: dict[str, Any]) -> bool:
    if trace.get("visible") is False or not trace.get("x") or not trace.get("y"):
        return False
    if str(trace.get("fill") or "").lower() != "toself":
        return False
    name = str(trace.get("name") or "").lower()
    label = custom_data_label(array_value(trace.get("customdata"), 0)).lower() if trace.get("customdata") else ""
    if "regime" in name or "regime" in label:
        return False
    return "aspect_window" in label or "aspect" in name or "window" in name


def chart_marker_point(trace: dict[str, Any], point_number: int) -> dict[str, Any] | None:
    x = array_value(trace.get("x"), point_number)
    y = array_value(trace.get("y"), point_number)
    if y is None:
        return None
    text = array_value(trace.get("text"), point_number)
    custom = array_value(trace.get("customdata"), point_number)
    label = custom_data_label(custom) or re.sub(r"<[^>]*>", " ", str(text or "")).strip()[:160]
    return {
        "x": canonical_ist(str(x)),
        "y": float(y),
        "trace_name": trace.get("name") or "",
        "marker_label": label,
        "is_selected_case_touch": "selected case touch" in str(trace.get("name") or "").lower(),
    }


def collect_markers(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: dict[str, bool] = {}
    for curve_number, trace in enumerate(traces):
        if not trace_looks_like_marker(trace):
            continue
        xs = trace_array(trace.get("x"))
        is_selected_case_touch = "selected case touch" in str(trace.get("name") or "").lower()
        for index in range(len(xs)):
            point = chart_marker_point(trace, index)
            if not point:
                continue
            point["curveNumber"] = curve_number
            point["pointNumber"] = index
            point["is_selected_case_touch"] = is_selected_case_touch
            point["autoCandidate"] = True
            key = f"{round(iso_ms(point['x']) / 60000)}:{point['y']:.4f}"
            if seen.get(key) and not is_selected_case_touch:
                continue
            if seen.get(key) and is_selected_case_touch:
                out = [item for item in out if f"{round(iso_ms(item['x']) / 60000)}:{item['y']:.4f}" != key]
            seen[key] = True
            out.append(point)
    return sorted(out, key=lambda p: iso_ms(p["x"]))


def collect_candles(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candles: list[dict[str, Any]] = []
    for trace in traces:
        if str(trace.get("type") or "").lower() != "candlestick":
            continue
        xs = trace_array(trace.get("x"))
        for index, x in enumerate(xs):
            high = array_value(trace.get("high"), index)
            low = array_value(trace.get("low"), index)
            close = array_value(trace.get("close"), index)
            open_ = array_value(trace.get("open"), index)
            if None in {high, low, close, open_}:
                continue
            candles.append(
                {
                    "x": canonical_ist(str(x)),
                    "t": iso_ms(str(x)),
                    "open": float(open_),
                    "high": float(high),
                    "low": float(low),
                    "close": float(close),
                }
            )
    return sorted(candles, key=lambda c: c["t"])


def timeframe_minutes(case: dict[str, Any]) -> int:
    return 60 if str(case.get("price_timeframe") or "").lower() == "h1" else 30


def candle_ms(case: dict[str, Any]) -> int:
    return timeframe_minutes(case) * 60 * 1000


def candle_at_or_after(candles: list[dict[str, Any]], time_ms: int, case: dict[str, Any]) -> dict[str, Any] | None:
    if not candles:
        return None
    interval = candle_ms(case)
    for candle in candles:
        if candle["t"] >= time_ms - interval * 0.25:
            return candle
    return min(candles, key=lambda candle: abs(candle["t"] - time_ms))


def candle_price_point_at(
    candles: list[dict[str, Any]],
    time_ms: int,
    case: dict[str, Any],
    label: str,
    source: str = "auto_market_boundary",
) -> dict[str, Any]:
    candle = candle_at_or_after(candles, time_ms, case)
    if candle:
        y = candle["open"] if candle.get("open") is not None else candle["close"]
        return {"x": candle["x"], "y": float(y), "source": source, "marker_label": label}
    return {
        "x": datetime.fromtimestamp(time_ms / 1000).isoformat(),
        "y": safe_float(case.get("full_window_entry_price")),
        "source": source,
        "marker_label": label,
    }


def sr_line_value_at(trace: dict[str, Any], time_ms: int) -> float | None:
    xs = trace_array(trace.get("x"))
    best_index = -1
    best_dist = float("inf")
    for index, x in enumerate(xs):
        try:
            dist = abs(iso_ms(str(x)) - time_ms)
        except Exception:
            continue
        if dist < best_dist:
            best_dist = dist
            best_index = index
    if best_index < 0:
        return None
    y = array_value(trace.get("y"), best_index)
    return float(y) if y is not None else None


def marker_identity(point: dict[str, Any] | None) -> str:
    if not point:
        return ""
    try:
        t_part = str(round(iso_ms(str(point.get("x"))) / 60000))
    except Exception:
        t_part = str(point.get("x") or "")
    y = safe_float(point.get("y"))
    return f"{t_part}:{y:.4f}" if y is not None else f"{t_part}:"


def unique_markers(points: list[dict[str, Any] | None]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for point in points:
        if not point:
            continue
        ident = marker_identity(point)
        if ident in seen:
            continue
        seen.add(ident)
        out.append(point)
    return sorted(out, key=lambda point: iso_ms(str(point["x"])))


def collect_zone_boundaries(traces: list[dict[str, Any]], candles: list[dict[str, Any]], case: dict[str, Any]) -> list[dict[str, Any]]:
    zones: list[dict[str, Any]] = []
    seen: set[str] = set()
    for curve_number, trace in enumerate(traces):
        if not trace_looks_like_zone(trace):
            continue
        times: list[int] = []
        for x in trace_array(trace.get("x")):
            try:
                times.append(iso_ms(str(x)))
            except Exception:
                continue
        if not times:
            continue
        start_time = min(times)
        end_time = max(times)
        if start_time == end_time:
            continue
        label = custom_data_label(array_value(trace.get("customdata"), 0)) or str(trace.get("name") or "shaded zone")
        ident = f"{round(start_time / 60000)}:{round(end_time / 60000)}:{label}"
        if ident in seen:
            continue
        seen.add(ident)
        point = candle_price_point_at(candles, start_time, case, f"next shaded zone start: {label}", "auto_zone_boundary")
        point["zoneStart"] = datetime.fromtimestamp(start_time / 1000).isoformat()
        point["zoneEnd"] = datetime.fromtimestamp(end_time / 1000).isoformat()
        point["traceName"] = trace.get("name") or ""
        point["curveNumber"] = curve_number
        zones.append(point)
    return sorted(zones, key=lambda point: iso_ms(str(point["x"])))


def collect_aspect_windows(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for curve_number, trace in enumerate(traces):
        if not trace_looks_like_aspect_window(trace):
            continue
        times: list[int] = []
        for x in trace_array(trace.get("x")):
            try:
                times.append(iso_ms(str(x)))
            except Exception:
                continue
        if not times:
            continue
        start_time = min(times)
        end_time = max(times)
        if start_time == end_time:
            continue
        label = custom_data_label(array_value(trace.get("customdata"), 0)) or str(trace.get("name") or "aspect window")
        label = re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", label)).strip()[:120]
        ident = f"{start_time}|{end_time}|{label}"
        if ident in seen:
            continue
        seen.add(ident)
        windows.append({"start": start_time, "end": end_time, "label": label, "curveNumber": curve_number})
    return sorted(windows, key=lambda item: item["start"])


def multi_aspect_overlap_evidence(
    candles: list[dict[str, Any]],
    aspect_windows: list[dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any]:
    case_start = iso_ms(str(case["window_start_ist"]))
    case_end = iso_ms(str(case["window_end_ist"]))
    interval = candle_ms(case)
    evidence = {
        "active": False,
        "definition": "multiple aspect = at least one reviewed candle has two or more aspect windows overlapping it",
        "min_required_aspects": 2,
        "min_required_candles": 1,
        "candle_minutes": timeframe_minutes(case),
        "qualifying_candle_count": 0,
        "max_overlap_count": 0,
        "first_qualifying_candle": None,
    }
    for candle in candles:
        candle_start = candle["t"]
        candle_end = candle["t"] + interval
        if candle_end <= case_start or candle_start >= case_end:
            continue
        overlaps = [
            win
            for win in aspect_windows
            if win.get("start") is not None and win.get("end") is not None and win["start"] < candle_end and win["end"] > candle_start
        ]
        evidence["max_overlap_count"] = max(int(evidence["max_overlap_count"]), len(overlaps))
        if len(overlaps) >= 2:
            evidence["qualifying_candle_count"] += 1
            if not evidence["first_qualifying_candle"]:
                evidence["first_qualifying_candle"] = {
                    "x": candle["x"],
                    "overlap_count": len(overlaps),
                    "event_labels": [win["label"] for win in overlaps[:6]],
                }
    evidence["active"] = evidence["qualifying_candle_count"] >= 1
    return evidence


def collect_sr_line_touches(
    traces: list[dict[str, Any]],
    candles: list[dict[str, Any]],
    reference_point: dict[str, Any] | None,
    outcome: str,
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    entry_time = iso_ms(str(reference_point["x"])) if reference_point else 0
    entry_price = safe_float(reference_point.get("y") if reference_point else None)
    if not entry_time or entry_price is None:
        return []
    clearance_pips = sr_geometry_epsilon_pips(candles, reference_point, case)
    touch_pad = max(clearance_pips, 2.0) / 100
    start = iso_ms(str(case["window_start_ist"]))
    min_time = max(entry_time, start)
    out: list[dict[str, Any]] = []
    for curve_number, trace in enumerate(traces):
        if not trace_looks_like_sr_line(trace):
            continue
        label = re.sub(r"\s+", " ", str(trace.get("name") or "SR line")).strip()
        previous_side: int | None = None
        for index, candle in enumerate(candles):
            if candle["t"] < min_time:
                continue
            sr = sr_line_value_at(trace, candle["t"])
            if sr is None:
                continue
            if outcome == "bearish" and sr >= entry_price - touch_pad:
                continue
            if outcome == "bullish" and sr <= entry_price + touch_pad:
                continue
            side = 1 if candle["close"] >= sr else -1
            touched = candle["low"] <= sr + touch_pad and candle["high"] >= sr - touch_pad
            crossed = previous_side is not None and side != previous_side
            previous_side = side
            if not touched and not crossed:
                continue
            out.append(
                {
                    "x": candle["x"],
                    "y": float(sr),
                    "source": "auto_sr_line_touch",
                    "traceName": trace.get("name") or "",
                    "curveNumber": curve_number,
                    "pointNumber": index,
                    "marker_label": f"{label} SR touch",
                }
            )
            break
    return unique_markers(out)


def collect_case_window_sr_touches(
    traces: list[dict[str, Any]],
    case: dict[str, Any],
    touch_band_pips: float | None = None,
) -> list[dict[str, Any]]:
    candles = collect_candles(traces)
    start = iso_ms(str(case["window_start_ist"]))
    end = iso_ms(str(case["window_end_ist"]))
    if touch_band_pips is None:
        reference = case_entry_point(case)
        touch_band_pips = max(sr_geometry_epsilon_pips(candles, reference, case), 3.0)
    touch_pad = touch_band_pips / 100.0
    out: list[dict[str, Any]] = []
    for trace in traces:
        if not trace_looks_like_sr_line(trace):
            continue
        label = re.sub(r"\s+", " ", str(trace.get("name") or "SR line")).strip()
        for candle_index, candle in enumerate(candles):
            if candle["t"] < start or candle["t"] > end:
                continue
            sr_price = sr_line_value_at(trace, candle["t"])
            if sr_price is None:
                continue
            high_gap = abs(candle["high"] - sr_price)
            low_gap = abs(candle["low"] - sr_price)
            close_gap = abs(candle["close"] - sr_price)
            range_gap = 0.0 if candle["low"] <= sr_price <= candle["high"] else min(high_gap, low_gap, close_gap)
            if range_gap > touch_pad:
                continue
            use_top = high_gap <= low_gap
            out.append(
                {
                    "x": candle["x"],
                    "y": round(candle["high"] if use_top else candle["low"], 3),
                    "sr_price": round(sr_price, 6),
                    "touch_gap_pips": round(range_gap * 100, 2),
                    "touch_band_pips": touch_band_pips,
                    "touch_side": "top_wick" if use_top else "bottom_wick",
                    "gann_anchor_side": "top" if use_top else "bottom",
                    "marker_label": f"{label} selected-case SR touch",
                    "point_number": candle_index,
                }
            )
    deduped: dict[str, dict[str, Any]] = {}
    for point in out:
        key = f"{round(iso_ms(point['x']) / 60000)}:{point['y']:.4f}"
        deduped.setdefault(key, point)
    return sorted(deduped.values(), key=lambda p: (iso_ms(p["x"]), p["touch_gap_pips"]))


def safe_float(value: Any) -> float | None:
    try:
        out = float(value)
    except Exception:
        return None
    return out


def case_entry_point(case: dict[str, Any]) -> dict[str, Any] | None:
    price = safe_float(case.get("full_window_entry_price"))
    if price is None:
        return None
    return {
        "x": str(case["window_start_ist"]),
        "y": price,
        "source": "auto_case_window_entry",
        "marker_label": "case window entry/open price",
    }


def signed_pips_for_points(start: dict[str, Any] | None, end: dict[str, Any] | None, outcome: str) -> float | None:
    entry = safe_float(start.get("y") if start else None)
    exit_ = safe_float(end.get("y") if end else None)
    if entry is None or exit_ is None:
        return None
    raw = (exit_ - entry) * 100
    return -raw if str(outcome).lower() == "bearish" else raw


def atr_pips_at(candles: list[dict[str, Any]], time_ms: int, period: int = 14) -> float | None:
    before = [c for c in candles if c["t"] <= time_ms]
    if len(before) < 2:
        return None
    trs: list[float] = []
    for index in range(1, len(before)):
        c = before[index]
        prev = before[index - 1]
        tr = max(c["high"] - c["low"], abs(c["high"] - prev["close"]), abs(c["low"] - prev["close"]))
        trs.append(tr * 100)
    sample = trs[-max(1, period) :]
    return sum(sample) / len(sample) if sample else None


def sr_geometry_epsilon_pips(candles: list[dict[str, Any]], reference_point: dict[str, Any] | None, case: dict[str, Any]) -> float:
    try:
        time_ms = iso_ms(str(reference_point["x"])) if reference_point else 0
    except Exception:
        time_ms = 0
    atr = atr_pips_at(candles, time_ms, 14) if time_ms else None
    epsilon = max(1.5, min(5.0, 0.05 * atr)) if atr is not None else 1.5
    return round(epsilon, 1)


def sr_geometry_for_point(
    point: dict[str, Any] | None,
    reference_point: dict[str, Any] | None,
    outcome: str,
    candles: list[dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any] | None:
    ref = safe_float(reference_point.get("y") if reference_point else None)
    y = safe_float(point.get("y") if point else None)
    if ref is None or y is None:
        return None
    diff_pips = (y - ref) * 100
    epsilon = sr_geometry_epsilon_pips(candles, reference_point, case)
    position = "same_as_entry" if abs(diff_pips) <= epsilon else ("below_entry" if diff_pips < 0 else "above_entry")
    if position == "below_entry":
        role = "support/target" if outcome == "bearish" else "support/entry"
    elif position == "above_entry":
        role = "resistance/entry" if outcome == "bearish" else "resistance/target"
    else:
        role = "at SR / use marker flow"
    label_position = "below entry" if position == "below_entry" else ("above entry" if position == "above_entry" else f"at entry within {epsilon} pips")
    return {
        "position": position,
        "role": role,
        "reference_price": ref,
        "sr_price": y,
        "distance_pips": diff_pips,
        "epsilon_pips": epsilon,
        "label": f"SR is {label_position}: {role}",
    }


def break_threshold_pips(candles: list[dict[str, Any]], time_ms: int, case: dict[str, Any]) -> dict[str, Any]:
    base = 8 if str(case.get("price_timeframe") or "").lower() == "h1" else 5
    atr = atr_pips_at(candles, time_ms, 14)
    threshold = max(base, 0.25 * atr) if atr is not None else base
    return {
        "base_pips": base,
        "atr14_pips": round(atr, 1) if atr is not None else None,
        "threshold_pips": round(threshold, 1),
        "method": f"max({base} pips, 0.25 * ATR14)",
    }


def candle_label(candle: dict[str, Any] | None) -> str:
    return f"{candle['x']} close {candle['close']:.3f}" if candle else ""


def break_confirmation_for_geometry(
    geometry: dict[str, Any] | None,
    sr_point: dict[str, Any] | None,
    reference_point: dict[str, Any] | None,
    outcome: str,
    candles: list[dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any] | None:
    if not geometry or not sr_point or not reference_point:
        return None
    if "target" not in str(geometry.get("role") or ""):
        return {"status": "not_applicable", "label": "Break confirmation not needed for this SR role."}
    sr = safe_float(sr_point.get("y"))
    if sr is None:
        return None
    start_time = iso_ms(str(reference_point["x"]))
    threshold = break_threshold_pips(candles, start_time, case)
    threshold_price = threshold["threshold_pips"] / 100
    after = [c for c in candles if c["t"] >= start_time]
    continuation_step = max(2, threshold["threshold_pips"] / 2) / 100
    break_candle = retest_candle = continuation_candle = None
    if outcome == "bearish" and geometry.get("position") == "below_entry":
        break_line = sr - threshold_price
        break_candle = next((c for c in after if c["close"] <= break_line), None)
        if break_candle:
            after_break = [c for c in after if c["t"] > break_candle["t"]]
            retest_candle = next((c for c in after_break if c["high"] >= sr - threshold_price and c["close"] < sr), None)
            if retest_candle:
                continuation_candle = next(
                    (
                        c
                        for c in after_break
                        if c["t"] > retest_candle["t"]
                        and (c["close"] <= retest_candle["close"] - continuation_step or c["low"] < retest_candle["low"])
                    ),
                    None,
                )
        status = "confirmed" if break_candle and retest_candle and continuation_candle else ("break_candidate" if break_candle else "not_confirmed")
        return {
            "status": status,
            "label": "Support break confirmed" if status == "confirmed" else "Support break not confirmed",
            **threshold,
            "sr_price": sr,
            "break_line": round(break_line, 3),
            "break_candle": candle_label(break_candle),
            "retest_candle": candle_label(retest_candle),
            "continuation_candle": candle_label(continuation_candle),
        }
    if outcome == "bullish" and geometry.get("position") == "above_entry":
        break_line = sr + threshold_price
        break_candle = next((c for c in after if c["close"] >= break_line), None)
        if break_candle:
            after_break = [c for c in after if c["t"] > break_candle["t"]]
            retest_candle = next((c for c in after_break if c["low"] <= sr + threshold_price and c["close"] > sr), None)
            if retest_candle:
                continuation_candle = next(
                    (
                        c
                        for c in after_break
                        if c["t"] > retest_candle["t"]
                        and (c["close"] >= retest_candle["close"] + continuation_step or c["high"] > retest_candle["high"])
                    ),
                    None,
                )
        status = "confirmed" if break_candle and retest_candle and continuation_candle else ("break_candidate" if break_candle else "not_confirmed")
        return {
            "status": status,
            "label": "Resistance break confirmed" if status == "confirmed" else "Resistance break not confirmed",
            **threshold,
            "sr_price": sr,
            "break_line": round(break_line, 3),
            "break_candle": candle_label(break_candle),
            "retest_candle": candle_label(retest_candle),
            "continuation_candle": candle_label(continuation_candle),
        }
    return {"status": "not_applicable", "label": "Break confirmation not applicable"}


def case_metadata_from_template(pack_dir: Path, case_id: int) -> dict[str, Any]:
    path = pack_dir / "repeatation_marker_template.csv"
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["case_id"]) == int(case_id):
                return row
    raise ValueError(f"case_id={case_id} not found in {path}")


def all_case_metadata_from_template(pack_dir: Path) -> dict[int, dict[str, Any]]:
    path = pack_dir / "repeatation_marker_template.csv"
    out: dict[int, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                out[int(row["case_id"])] = row
            except Exception:
                continue
    return out


def parse_json_field(value: Any, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(str(value))
    except Exception:
        return fallback


def applied_rule(case: dict[str, Any], label: str) -> dict[str, Any] | None:
    rules = parse_json_field(case.get("applied_family_rules_json"), [])
    if not isinstance(rules, list):
        return None
    for rule in rules:
        if str(rule.get("label") or "").lower() == label.lower():
            return rule
    return None


def point_time(point: dict[str, Any] | None) -> int:
    if not point:
        return -1
    try:
        return iso_ms(str(point.get("x")))
    except Exception:
        return -1


def zone_boundary_after(zones: list[dict[str, Any]], after_time: int, case: dict[str, Any], min_gap_ms: int) -> dict[str, Any] | None:
    window_start = iso_ms(str(case["window_start_ist"]))
    window_end = iso_ms(str(case["window_end_ist"]))
    min_time = after_time + min_gap_ms
    for point in zones:
        t = point_time(point)
        if t < min_time:
            continue
        if window_start <= t <= window_end:
            continue
        return point
    return None


def attribution_boundary_after(markers: list[dict[str, Any]], after_time: int, case: dict[str, Any], min_gap_ms: int) -> dict[str, Any] | None:
    window_end = iso_ms(str(case["window_end_ist"]))
    min_time = max(after_time, window_end) + min_gap_ms
    for point in unique_markers(markers):
        t = point_time(point)
        if t < min_time:
            continue
        if point.get("is_selected_case_touch"):
            continue
        if point.get("source") == "auto_case_window_entry":
            continue
        return point
    return None


def earliest_timed_point(points: list[dict[str, Any] | None]) -> dict[str, Any] | None:
    valid = [point for point in points if point and point_time(point) >= 0]
    return min(valid, key=point_time) if valid else None


def gann_fan_for_start(
    start_point: dict[str, Any] | None,
    outcome: str,
    candles: list[dict[str, Any]],
    case: dict[str, Any],
    reason: str,
) -> dict[str, Any] | None:
    if not start_point or outcome not in {"bearish", "bullish"}:
        return None
    start_time = point_time(start_point)
    if start_time < 0:
        return None
    candle = candle_at_or_after(candles, start_time, case)
    if not candle:
        return None
    anchor_side = str(start_point.get("gann_anchor_side") or "").lower()
    outcome_sign = -1 if outcome == "bearish" else 1
    direction_sign = -1 if anchor_side == "top" else (1 if anchor_side == "bottom" else outcome_sign)
    anchor_price = candle["high"] if direction_sign < 0 else candle["low"]
    return {
        "active": True,
        "direction": outcome,
        "fan_direction": "bearish" if direction_sign < 0 else "bullish",
        "direction_sign": direction_sign,
        "anchor": {
            "x": candle["x"],
            "y": round(anchor_price, 3),
            "source": "gann_fan_top_wick" if direction_sign < 0 else "gann_fan_bottom_wick",
            "marker_label": "Gann fan top wick anchor" if direction_sign < 0 else "Gann fan bottom wick anchor",
        },
        "anchor_candle": {
            "x": candle["x"],
            "open": round(candle["open"], 3),
            "high": round(candle["high"], 3),
            "low": round(candle["low"], 3),
            "close": round(candle["close"], 3),
        },
        "anchor_rule": "top wick anchor: bearish/downward fan projection"
        if direction_sign < 0
        else "bottom wick anchor: bullish/upward fan projection",
        "timeframe_minutes": timeframe_minutes(case),
        "base_pips_per_candle": 1,
        "ratios": [
            {"label": "1x4", "slope": 0.25},
            {"label": "1x2", "slope": 0.5},
            {"label": "1x1", "slope": 1},
            {"label": "2x1", "slope": 2},
            {"label": "4x1", "slope": 4},
        ],
        "reason": reason,
    }


def gann_fan_line_value_at(fan: dict[str, Any], ratio_label: str, time_ms: int, case: dict[str, Any]) -> float | None:
    anchor = fan.get("anchor") or {}
    anchor_time = point_time(anchor)
    anchor_price = safe_float(anchor.get("y"))
    direction_sign = safe_float(fan.get("direction_sign"))
    if anchor_time < 0 or anchor_price is None or direction_sign is None or time_ms < anchor_time:
        return None
    ratio = next((item for item in fan.get("ratios", []) if str(item.get("label")) == ratio_label), None)
    if not ratio:
        return None
    slope = safe_float(ratio.get("slope"))
    if slope is None:
        return None
    elapsed = (time_ms - anchor_time) / candle_ms(case)
    return anchor_price + direction_sign * elapsed * float(fan.get("base_pips_per_candle") or 1) * slope / 100


def second_from_bottom_gann_ratio(fan: dict[str, Any] | None) -> dict[str, str] | None:
    if not fan:
        return None
    direction = safe_float(fan.get("direction_sign"))
    if direction is None:
        return None
    if direction < 0:
        return {"label": "2x1", "explanation": "bearish/top-wick fan: 4x1 is lowest, 2x1 is second from bottom"}
    if direction > 0:
        return {"label": "1x2", "explanation": "bullish/bottom-wick fan: 1x4 is lowest, 1x2 is second from bottom"}
    return None


def gann_fan_second_from_bottom_touch(
    fan: dict[str, Any] | None,
    start_point: dict[str, Any] | None,
    multi_aspect_evidence: dict[str, Any],
    candles: list[dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any] | None:
    if not multi_aspect_evidence.get("active") or not fan or not fan.get("active"):
        return None
    target_ratio = second_from_bottom_gann_ratio(fan)
    if not target_ratio:
        return None
    start_time = point_time(start_point or fan.get("anchor"))
    if start_time < 0:
        return None
    epsilon_pips = 0.5
    epsilon_price = epsilon_pips / 100
    interval = candle_ms(case)
    for candle in candles:
        if candle["t"] <= start_time + interval * 0.25:
            continue
        line_y = gann_fan_line_value_at(fan, target_ratio["label"], candle["t"], case)
        if line_y is None:
            continue
        if not (candle["low"] <= line_y + epsilon_price and candle["high"] >= line_y - epsilon_price):
            continue
        gaps = [abs(candle["close"] - line_y), abs(candle["high"] - line_y), abs(candle["low"] - line_y)]
        return {
            "x": candle["x"],
            "y": round(line_y, 3),
            "source": "auto_gann_fan_second_from_bottom_touch",
            "traceName": "Gann fan",
            "marker_label": f"Gann fan 2nd-from-bottom touch ({target_ratio['label']})",
            "fan_ratio_label": target_ratio["label"],
            "fan_line_rank": "second_from_bottom",
            "fan_rule_explanation": target_ratio["explanation"],
            "gann_epsilon_pips": epsilon_pips,
            "touch_gap_pips": round(min(gaps) * 100, 2),
            "multi_aspect_gate": True,
        }
    return None


def replay_case_127(pack_dir: Path) -> dict[str, Any]:
    replay = auto_suggest_case(pack_dir, 127)
    auto = replay.get("auto_suggestion") or {}
    touches = auto.get("case_window_sr_touch_candidates") or []
    if not touches:
        raise AssertionError("case 127 expected at least one selected-window SR touch")
    return {
        "case_id": 127,
        "start_rule": replay.get("start_rule"),
        "end_rule": replay.get("end_rule"),
        "start": replay.get("trade_start"),
        "end": replay.get("trade_end"),
        "outcome_label": replay.get("outcome_label"),
        "signed_pips": replay.get("signed_pips"),
        "raw_pips": replay.get("raw_pips"),
        "gann_fan_exit_rule_status": auto.get("gann_fan_exit_rule_status"),
        "case_window_sr_touch_count": len(touches),
    }


def auto_suggest_case(pack_dir: Path, case_id: int) -> dict[str, Any]:
    html_path = pack_dir / f"aspect_review_case_{int(case_id)}_chart.html"
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    traces = plotly_data(html_text)
    case = case_metadata_from_template(pack_dir, case_id)
    outcome = str(case.get("default_outcome") or "").lower()
    if outcome not in {"bullish", "bearish"}:
        outcome = "bearish" if str(case.get("full_window_direction") or "").lower() == "bearish" else "bullish"
    candles = collect_candles(traces)
    markers = collect_markers(traces)
    zones = collect_zone_boundaries(traces, candles, case)
    aspect_windows = collect_aspect_windows(traces)
    multi_aspect = multi_aspect_overlap_evidence(candles, aspect_windows, case)
    selected = [point for point in markers if point.get("is_selected_case_touch")]
    window_start = iso_ms(str(case["window_start_ist"]))
    window_end = iso_ms(str(case["window_end_ist"]))
    window_markers = [point for point in markers if window_start <= point_time(point) <= window_end]
    case_window_sr_touches = collect_case_window_sr_touches(traces, case)
    first_case_window_sr_touch = case_window_sr_touches[0] if case_window_sr_touches else None
    default_start = first_case_window_sr_touch or (selected[0] if selected else (window_markers[0] if window_markers else (markers[0] if markers else None)))
    default_start_time = point_time(default_start)
    min_gap_ms = 60000
    default_end = next((point for point in markers if point_time(point) > default_start_time + min_gap_ms), None)
    entry_point = case_entry_point(case)
    default_start_geometry = sr_geometry_for_point(default_start, entry_point, outcome, candles, case)
    use_default_marker_flow = default_start_geometry and default_start_geometry.get("position") == "same_as_entry"
    support_barrier_rule = applied_rule(case, "bearish_bias_support_barrier")

    start = default_start
    end = default_end
    start_rule = "not_found"
    end_rule = "next_later_hardcoded_marker" if end else "not_found"
    reason = ""
    auto: dict[str, Any] = {}

    if support_barrier_rule and outcome == "bearish" and entry_point and not use_default_marker_flow:
        entry_time = point_time(entry_point)
        entry_price = float(entry_point["y"])
        clearance_pips = sr_geometry_epsilon_pips(candles, entry_point, case)
        clearance_price = clearance_pips / 100
        sr_line_touches = collect_sr_line_touches(traces, candles, entry_point, outcome, case)
        target_candidates = [
            point
            for point in unique_markers(selected + window_markers + markers + sr_line_touches)
            if point_time(point) >= entry_time
            and safe_float(point.get("y")) is not None
            and float(point["y"]) < entry_price - clearance_price
        ]
        first_barrier = target_candidates[0] if target_candidates else None
        barrier_geometry = sr_geometry_for_point(first_barrier, entry_point, outcome, candles, case)
        barrier_break = break_confirmation_for_geometry(barrier_geometry, first_barrier, entry_point, outcome, candles, case)
        zone_boundary = zone_boundary_after(zones, entry_time, case, min_gap_ms)
        attribution_boundary = attribution_boundary_after(markers, entry_time, case, min_gap_ms)
        barrier_confirmed = barrier_break and barrier_break.get("status") == "confirmed"
        target = earliest_timed_point([zone_boundary, attribution_boundary]) if barrier_confirmed else earliest_timed_point([first_barrier, zone_boundary, attribution_boundary])
        if not target and first_barrier:
            target = first_barrier
        end_rule = "global_first_boundary_after_entry" if target else "not_found"
        if barrier_confirmed and target and zone_boundary and marker_identity(target) == marker_identity(zone_boundary):
            end_rule = "confirmed_break_next_shaded_zone_boundary"
        elif barrier_confirmed and target and attribution_boundary and marker_identity(target) == marker_identity(attribution_boundary):
            end_rule = "confirmed_break_next_hardcoded_marker_boundary"
        elif target and first_barrier and marker_identity(target) == marker_identity(first_barrier):
            end_rule = "global_first_sr_touch_target"
        elif target and zone_boundary and marker_identity(target) == marker_identity(zone_boundary):
            end_rule = "global_next_shaded_zone_boundary"
        elif target and attribution_boundary and marker_identity(target) == marker_identity(attribution_boundary):
            end_rule = "global_next_hardcoded_marker_boundary"
        fan = gann_fan_for_start(entry_point, outcome, candles, case, "family rule case-window entry")
        fan_exit = gann_fan_second_from_bottom_touch(fan, entry_point, multi_aspect, candles, case)
        if fan_exit and (not target or point_time(fan_exit) < point_time(target)):
            target = fan_exit
            end_rule = "gann_second_from_bottom_touch_multi_aspect"
        start = entry_point
        end = target
        start_rule = "family_rule_case_window_entry_open_price"
        reason = "family bearish_bias_support_barrier replay"
        auto = {
            "applied_family_rule": "bearish_bias_support_barrier",
            "barrier_sr_geometry": barrier_geometry,
            "break_confirmation": barrier_break,
            "attribution_boundary": attribution_boundary,
            "next_shaded_zone_boundary": zone_boundary,
            "global_exit_boundary": target,
            "multi_aspect_overlap_evidence": multi_aspect,
            "gann_fan_exit_candidate": fan_exit,
            "gann_fan_exit_rule_status": "provisional_review_required"
            if fan_exit
            else ("eligible_but_no_touch_found" if multi_aspect.get("active") else "blocked_no_multi_aspect_overlap"),
            "sr_line_touch_candidates": sr_line_touches,
            "sr_geometry_epsilon_pips": clearance_pips,
        }
    else:
        wick_start = None
        default_flow_geometry = sr_geometry_for_point(default_end, default_start, outcome, candles, case)
        default_flow_at_sr = default_flow_geometry and default_flow_geometry.get("position") == "same_as_entry"
        if not first_case_window_sr_touch and selected and default_flow_at_sr and outcome in {"bullish", "bearish"}:
            candle = candle_at_or_after(candles, point_time(default_start), case)
            if candle:
                direction_sign = -1 if outcome == "bearish" else 1
                wick_start = {
                    "x": candle["x"],
                    "y": round(candle["high"] if direction_sign < 0 else candle["low"], 3),
                    "source": "auto_wick_entry_top" if direction_sign < 0 else "auto_wick_entry_bottom",
                    "traceName": default_start.get("traceName", "") if default_start else "",
                    "marker_label": "wick entry: bearish top wick from selected-case marker candle"
                    if direction_sign < 0
                    else "wick entry: bullish bottom wick from selected-case marker candle",
                }
                start = wick_start
        start_rule = (
            "first_case_window_sr_line_touch"
            if first_case_window_sr_touch
            else (
                "wick_entry_from_selected_case_sr_marker"
                if wick_start
                else ("first_selected_case_touch" if selected else ("first_marker_inside_case_window" if window_markers else "first_visible_marker"))
            )
        )
        fan = gann_fan_for_start(start, outcome, candles, case, "marker-flow auto suggestion start")
        fan_exit = gann_fan_second_from_bottom_touch(fan, start, multi_aspect, candles, case)
        if fan_exit and (not end or point_time(fan_exit) < point_time(end)):
            end = fan_exit
            end_rule = "gann_second_from_bottom_touch_multi_aspect"
        reason = "marker-flow replay"
        auto = {
            "default_marker_flow_sr_geometry": default_flow_geometry,
            "case_window_sr_touch_candidates": case_window_sr_touches,
            "multi_aspect_overlap_evidence": multi_aspect,
            "gann_fan_exit_candidate": fan_exit,
            "gann_fan_exit_rule_status": "provisional_review_required"
            if fan_exit
            else ("eligible_but_no_touch_found" if multi_aspect.get("active") else "blocked_no_multi_aspect_overlap"),
        }

    effective_outcome = outcome
    auto_outcome_reason = ""
    if (
        end_rule == "gann_second_from_bottom_touch_multi_aspect"
        and fan
        and fan.get("fan_direction") in {"bullish", "bearish"}
    ):
        effective_outcome = str(fan["fan_direction"])
        auto_outcome_reason = (
            "Gann fan exit controls trade direction: top-wick/down fan is bearish, "
            "bottom-wick/up fan is bullish."
        )
    signed = signed_pips_for_points(start, end, effective_outcome)
    raw = None
    if start and end and safe_float(start.get("y")) is not None and safe_float(end.get("y")) is not None:
        raw = (float(end["y"]) - float(start["y"])) * 100
    sr_geometry = sr_geometry_for_point(end, start, effective_outcome, candles, case)
    auto.update(
        {
            "active": bool(start and end),
            "confidence": "deterministic_replay",
            "reason": reason,
            "marker_count": len(markers),
            "selected_case_marker_count": len(selected),
            "sr_geometry": sr_geometry,
            "start_rule": start_rule,
            "end_rule": end_rule,
            "auto_outcome": effective_outcome,
            "auto_outcome_reason": auto_outcome_reason,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
    )
    return {
        "case_id": int(case_id),
        "family_key": f"{case.get('pair_key')}::{case.get('aspect')}",
        "outcome_label": effective_outcome,
        "trade_start": start,
        "trade_end": end,
        "entry_price": safe_float(start.get("y") if start else None),
        "exit_price": safe_float(end.get("y") if end else None),
        "signed_pips": round(signed, 1) if signed is not None else None,
        "raw_pips": round(raw, 1) if raw is not None else None,
        "start_rule": start_rule,
        "end_rule": end_rule,
        "auto_suggestion": auto,
    }


def replay_completed_review_impacts(
    pack_dir: Path,
    completed_rows: list[dict[str, Any]],
    current_rule_version: str = "",
    pips_tolerance: float = 0.2,
) -> dict[str, Any]:
    def row_get(row: Any, key: str, default: Any = None) -> Any:
        if isinstance(row, dict):
            return row.get(key, default)
        try:
            return row[key]
        except Exception:
            return default

    affected: list[dict[str, Any]] = []
    unchanged = 0
    failed: list[dict[str, Any]] = []
    for row in completed_rows:
        try:
            case_id = int(row_get(row, "case_id"))
            replay = auto_suggest_case(pack_dir, case_id)
            old_pips = safe_float(row_get(row, "signed_pips"))
            new_pips = safe_float(replay.get("signed_pips"))
            pips_delta = None if old_pips is None or new_pips is None else round(new_pips - old_pips, 1)
            start_changed = str(row_get(row, "start_rule") or "") != str(replay.get("start_rule") or "")
            end_changed = str(row_get(row, "end_rule") or "") != str(replay.get("end_rule") or "")
            pips_changed = pips_delta is not None and abs(pips_delta) > pips_tolerance
            version_changed = bool(
                current_rule_version
                and row_get(row, "rule_version")
                and row_get(row, "rule_version") != current_rule_version
            )
            if start_changed or end_changed or pips_changed or version_changed:
                affected.append(
                    {
                        "case_id": case_id,
                        "stored_pips": old_pips,
                        "replayed_pips": new_pips,
                        "pips_delta": pips_delta,
                        "stored_start_rule": row_get(row, "start_rule") or "",
                        "stored_end_rule": row_get(row, "end_rule") or "",
                        "replayed_start_rule": replay.get("start_rule") or "",
                        "replayed_end_rule": replay.get("end_rule") or "",
                        "stored_rule_version": row_get(row, "rule_version") or "",
                        "current_rule_version": current_rule_version,
                        "reason": ", ".join(
                            [
                                label
                                for label, changed in [
                                    ("start rule changed", start_changed),
                                    ("end rule changed", end_changed),
                                    ("pips changed", pips_changed),
                                    ("rule version changed", version_changed),
                                ]
                                if changed
                            ]
                        ),
                        "replay": replay,
                    }
                )
            else:
                unchanged += 1
        except Exception as exc:
            failed.append({"case_id": row_get(row, "case_id"), "error": str(exc)})
    return {
        "mode": "historical_resimulation",
        "pack_dir": str(pack_dir),
        "reviewed_count": len(completed_rows),
        "unchanged_count": unchanged,
        "affected_count": len(affected),
        "affected_or_needs_replay": affected,
        "failed_count": len(failed),
        "failed": failed,
        "message": (
            "No completed reviews available for historical re-simulation."
            if not completed_rows
            else f"{len(affected)} completed review(s) changed under current deterministic replay."
        ),
    }


def assert_case_127(pack_dir: Path) -> dict[str, Any]:
    expected = EXPECTATIONS[127]
    replay = replay_case_127(pack_dir)
    start = replay["start"]
    end = replay["end"]
    failures: list[str] = []
    if replay["start_rule"] != expected.start_rule:
        failures.append(f"start_rule {replay['start_rule']} != {expected.start_rule}")
    if expected.end_rule and replay.get("end_rule") != expected.end_rule:
        failures.append(f"end_rule {replay.get('end_rule')} != {expected.end_rule}")
    if expected.outcome_label and replay.get("outcome_label") != expected.outcome_label:
        failures.append(f"outcome_label {replay.get('outcome_label')} != {expected.outcome_label}")
    if expected.signed_pips is not None and replay.get("signed_pips") != expected.signed_pips:
        failures.append(f"signed_pips {replay.get('signed_pips')} != {expected.signed_pips}")
    if start["x"] != expected.start_ist:
        failures.append(f"start {start['x']} != {expected.start_ist}")
    if expected.end_ist and (not end or end["x"] != expected.end_ist):
        failures.append(f"end {end and end.get('x')} != {expected.end_ist}")
    if expected.gann_anchor_side and start.get("gann_anchor_side") != expected.gann_anchor_side:
        failures.append(f"gann_anchor_side {start.get('gann_anchor_side')} != {expected.gann_anchor_side}")
    if expected.min_case_window_sr_touches and replay["case_window_sr_touch_count"] < expected.min_case_window_sr_touches:
        failures.append(
            f"case_window_sr_touch_count {replay['case_window_sr_touch_count']} < {expected.min_case_window_sr_touches}"
        )
    if failures:
        raise AssertionError("; ".join(failures))
    return replay


def assert_family_guard_sources(case_id: int, source_text: str) -> None:
    missing = [needle for needle in FAMILY_RULE_GUARDS[case_id] if needle not in source_text]
    if missing:
        raise AssertionError(f"case {case_id} family-rule guard text missing from generator: {missing}")


def main() -> None:
    args = parse_args()
    pack_dir = args.pack_dir or latest_pack(args.pack_root)
    case_filter = set(args.case_id or [])
    results: list[dict[str, Any]] = []

    if not case_filter or 127 in case_filter:
        replay = assert_case_127(pack_dir)
        results.append(
            {
                "case_id": 127,
                "status": "passed",
                "start_rule": replay["start_rule"],
                "start": replay["start"],
                "end": replay["end"],
                "case_window_sr_touch_count": replay["case_window_sr_touch_count"],
            }
        )

    generator_text = Path("build_repeatation_review_pack.py").read_text(encoding="utf-8", errors="ignore")
    for case_id in sorted(FAMILY_RULE_GUARDS):
        if case_filter and case_id not in case_filter:
            continue
        assert_family_guard_sources(case_id, generator_text)
        results.append(
            {
                "case_id": case_id,
                "status": "source_guard_passed",
                "note": "Family-rule teaching case still has expected rule/candidate guard text in generator.",
            }
        )

    print(json.dumps({"pack_dir": str(pack_dir), "results": results}, indent=2))


if __name__ == "__main__":
    main()
