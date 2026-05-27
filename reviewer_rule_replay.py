from __future__ import annotations

import argparse
import base64
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
    gann_anchor_side: str | None = None
    min_case_window_sr_touches: int | None = None


EXPECTATIONS: dict[int, ReplayExpectation] = {
    127: ReplayExpectation(
        case_id=127,
        start_rule="first_case_window_sr_line_touch",
        start_ist="2025-05-28T22:00:00+05:30",
        end_ist="2025-05-28T23:30:00+05:30",
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
    for trace in traces:
        if not trace_looks_like_marker(trace):
            continue
        xs = decode_array(trace.get("x")) or trace.get("x") or []
        for index in range(len(xs)):
            point = chart_marker_point(trace, index)
            if not point:
                continue
            key = f"{round(iso_ms(point['x']) / 60000)}:{point['y']:.4f}"
            if seen.get(key) and not point["is_selected_case_touch"]:
                continue
            if seen.get(key) and point["is_selected_case_touch"]:
                out = [item for item in out if f"{round(iso_ms(item['x']) / 60000)}:{item['y']:.4f}" != key]
            seen[key] = True
            out.append(point)
    return sorted(out, key=lambda p: iso_ms(p["x"]))


def collect_candles(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candles: list[dict[str, Any]] = []
    for trace in traces:
        if str(trace.get("type") or "").lower() != "candlestick":
            continue
        xs = decode_array(trace.get("x")) or trace.get("x") or []
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


def sr_line_value_at(trace: dict[str, Any], time_ms: int) -> float | None:
    xs = decode_array(trace.get("x")) or trace.get("x") or []
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


def collect_case_window_sr_touches(
    traces: list[dict[str, Any]],
    case: dict[str, Any],
    touch_band_pips: float = 3.0,
) -> list[dict[str, Any]]:
    candles = collect_candles(traces)
    start = iso_ms(str(case["window_start_ist"]))
    end = iso_ms(str(case["window_end_ist"]))
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


def case_metadata_from_template(pack_dir: Path, case_id: int) -> dict[str, Any]:
    import csv

    path = pack_dir / "repeatation_marker_template.csv"
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["case_id"]) == int(case_id):
                return row
    raise ValueError(f"case_id={case_id} not found in {path}")


def replay_case_127(pack_dir: Path) -> dict[str, Any]:
    case_id = 127
    html_path = pack_dir / f"aspect_review_case_{case_id}_chart.html"
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    traces = plotly_data(html_text)
    case = case_metadata_from_template(pack_dir, case_id)
    markers = collect_markers(traces)
    selected = [
        marker
        for marker in markers
        if marker["is_selected_case_touch"]
        and iso_ms(case["window_start_ist"]) <= iso_ms(marker["x"]) <= iso_ms(case["window_end_ist"])
    ]
    touches = collect_case_window_sr_touches(traces, case, touch_band_pips=3.0)
    if not touches:
        raise AssertionError("case 127 expected at least one selected-window SR touch")
    start = touches[0]
    later_markers = [marker for marker in markers if iso_ms(marker["x"]) > iso_ms(start["x"])]
    end = later_markers[0] if later_markers else None
    return {
        "case_id": case_id,
        "start_rule": "first_case_window_sr_line_touch",
        "start": start,
        "end": end,
        "selected_hardcoded_reference": selected[0] if selected else None,
        "case_window_sr_touch_count": len(touches),
    }


def assert_case_127(pack_dir: Path) -> dict[str, Any]:
    expected = EXPECTATIONS[127]
    replay = replay_case_127(pack_dir)
    start = replay["start"]
    end = replay["end"]
    failures: list[str] = []
    if replay["start_rule"] != expected.start_rule:
        failures.append(f"start_rule {replay['start_rule']} != {expected.start_rule}")
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
