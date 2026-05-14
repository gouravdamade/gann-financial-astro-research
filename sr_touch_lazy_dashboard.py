from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests

PROJECT_DIR = Path(r"C:\Users\ADMIN\Desktop\Trading_Algo\New folder")
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from adaptive_ephemeris_engine import build_adaptive_longitude_map
from JDML4 import fetch_planetary_longitude
from build_trade_candidates_from_touches import (
    aspect_family,
    aspect_stats_from_event_json,
    duration_bucket,
    score_currency_pair_for_row,
    score_transit_natal_hits_for_row,
)
from planetary_sr_engine import DEFAULT_SR_PLANETS

IST = "Asia/Kolkata"
UTC = "UTC"
ALL_FILTER_VALUE = "__ALL__"
DEFAULT_DETAIL_DAYS = 365
APP_BG = "#0f172a"
PANEL_BG = "#111827"
GRID_COLOR = "rgba(148,163,184,0.15)"
PRICE_LINE_COLOR = "#cbd5e1"
CANDLE_UP_LINE = "#34d399"
CANDLE_UP_FILL = "#34d399"
CANDLE_DOWN_LINE = "#f87171"
CANDLE_DOWN_FILL = "#f87171"
TOUCH_CLUSTER_GAP = pd.Timedelta(minutes=65)
SELECTED_LINE_COLOR = "#2563eb"
AVG_ALL_LABEL = "AVG(ALL)"
AVG_ALL_PLANETS = (
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "URANUS",
    "NEPTUNE",
    "PLUTO",
)
AVG_ALL_PLANET_SET = set(AVG_ALL_PLANETS)
SHORT_TERM_EXCLUDED_SLOW_PAIR_BODIES = {"JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"}
SHORT_TERM_EXCLUDED_CONTEXT_PAIR_BODIES = {AVG_ALL_LABEL, "RAHU", "KETU"}

PLANET_COLORS = {
    "MOON": "#60a5fa",
    "MERCURY": "#2dd4bf",
    "VENUS": "#f472b6",
    "SUN": "#fbbf24",
    "MARS": "#fb7185",
    "JUPITER": "#a78bfa",
    "SATURN": "#94a3b8",
    "RAHU": "#f97316",
    "KETU": "#a3e635",
    "URANUS": "#22c55e",
    "NEPTUNE": "#06b6d4",
    "PLUTO": "#38bdf8",
    AVG_ALL_LABEL: "#f8fafc",
}
MARKER_COLORS = {"bullish": "#818cf8", "bearish": "#fbbf24"}
MARKER_SYMBOLS = {"bullish": "triangle-up", "bearish": "triangle-down"}
ZONE_COLORS = {"bullish": "rgba(79,70,229,0.12)", "bearish": "rgba(245,158,11,0.12)"}
ZONE_BORDER_COLORS = {"bullish": "rgba(79,70,229,0.45)", "bearish": "rgba(245,158,11,0.45)"}
REGIME_ZONE_COLORS = {"single": "rgba(59,130,246,0.045)", "overlap": "rgba(245,158,11,0.095)"}
REGIME_ZONE_BORDER_COLORS = {"single": "rgba(96,165,250,0.38)", "overlap": "rgba(251,191,36,0.70)"}
PLOTLY_CHART_CONFIG = {
    "doubleClick": False,
    "displaylogo": False,
}
DETAIL_PANEL_POST_SCRIPT = r"""
(function () {
  var gd = document.getElementById('{plot_id}');
  if (!gd || gd.__srDetailsPanelAttached) return;
  gd.__srDetailsPanelAttached = true;
  var panel = document.createElement('div');
  panel.id = gd.id + '-sr-details-panel';
  panel.style.cssText = 'margin:12px 0 0 0;padding:12px 14px;background:#0b1220;color:#dbeafe;border:1px solid #334155;border-radius:6px;font:13px/1.45 Arial,sans-serif;max-height:360px;overflow:auto;';
  panel.innerHTML = '<b>Details</b><br><span style="color:#94a3b8">Single-click an event, marker, or shaded aspect/regime window to select it and show Quote/JPY details.</span>';
  gd.parentNode.insertBefore(panel, gd.nextSibling);
  var lastPlotlyClickAt = 0;
  var lastPlotlyClickKind = '';
  function unwrapCustomData(customdata) {
    while (Array.isArray(customdata) && customdata.length === 1 && Array.isArray(customdata[0])) {
      customdata = customdata[0];
    }
    return customdata;
  }
  function detailFromCustomData(customdata) {
    customdata = unwrapCustomData(customdata);
    if (Array.isArray(customdata)) {
      if (customdata.length > 1 && customdata[1]) return customdata[1];
      if (customdata.length > 0) return customdata[0];
    }
    return customdata;
  }
  function selectionFromCustomData(customdata) {
    customdata = unwrapCustomData(customdata);
    if (!Array.isArray(customdata) || customdata.length < 4) return null;
    var start = customdata[2];
    var end = customdata[3];
    if (!start || !end) return null;
    return {
      start: start,
      end: end,
      label: customdata[4] || 'Selected event',
      kind: customdata[5] || 'event'
    };
  }
  function formatTs(value) {
    var d = new Date(value);
    if (isNaN(d.getTime())) return String(value);
    return d.toLocaleString('en-GB', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  }
  function clearSelectionDecorations(items, selectedName) {
    if (!Array.isArray(items)) return [];
    return items.filter(function (item) {
      return !(item && item.name === selectedName);
    });
  }
  function disableSelectionPointerEvents() {
    var nodes = gd.querySelectorAll('.shapelayer path, .annotation');
    nodes.forEach(function (node) {
      var text = (node.textContent || '');
      if (
        node.getAttribute('data-index') !== null ||
        text.indexOf('Start') !== -1 ||
        text.indexOf('End') !== -1
      ) {
        node.style.pointerEvents = 'none';
      }
    });
  }
  function setSelectedWindow(selection) {
    var shapes = [];
    if (gd.layout && Array.isArray(gd.layout.shapes)) {
      shapes = clearSelectionDecorations(gd.layout.shapes, 'selected-event-window');
    }
    shapes.push(
      {
        type: 'rect',
        name: 'selected-event-window',
        xref: 'x',
        yref: 'paper',
        x0: selection.start,
        x1: selection.end,
        y0: 0,
        y1: 1,
        fillcolor: 'rgba(239, 68, 68, 0.055)',
        line: {color: 'rgba(248, 113, 113, 1)', width: 4},
        layer: 'above'
      },
      {
        type: 'line',
        name: 'selected-event-window',
        xref: 'x',
        yref: 'paper',
        x0: selection.start,
        x1: selection.start,
        y0: 0,
        y1: 1,
        line: {color: 'rgba(239, 68, 68, 1)', width: 2.5, dash: 'solid'},
        layer: 'above'
      },
      {
        type: 'line',
        name: 'selected-event-window',
        xref: 'x',
        yref: 'paper',
        x0: selection.end,
        x1: selection.end,
        y0: 0,
        y1: 1,
        line: {color: 'rgba(239, 68, 68, 1)', width: 2.5, dash: 'solid'},
        layer: 'above'
      }
    );
    var annotations = [];
    if (gd.layout && Array.isArray(gd.layout.annotations)) {
      annotations = clearSelectionDecorations(gd.layout.annotations, 'selected-event-window');
    }
    annotations.push(
      {
        name: 'selected-event-window',
        xref: 'x',
        yref: 'paper',
        x: selection.start,
        y: 1,
        text: 'Start<br>' + formatTs(selection.start),
        showarrow: true,
        arrowhead: 2,
        ax: -92,
        ay: -32,
        xanchor: 'right',
        align: 'right',
        bgcolor: 'rgba(127, 29, 29, 0.92)',
        bordercolor: 'rgba(248, 113, 113, 1)',
        borderwidth: 1,
        font: {color: '#fee2e2', size: 11}
      },
      {
        name: 'selected-event-window',
        xref: 'x',
        yref: 'paper',
        x: selection.end,
        y: 1,
        text: 'End<br>' + formatTs(selection.end),
        showarrow: true,
        arrowhead: 2,
        ax: 92,
        ay: -32,
        xanchor: 'left',
        align: 'left',
        bgcolor: 'rgba(127, 29, 29, 0.92)',
        bordercolor: 'rgba(248, 113, 113, 1)',
        borderwidth: 1,
        font: {color: '#fee2e2', size: 11}
      }
    );
    Plotly.relayout(gd, {shapes: shapes, annotations: annotations}).then(function () {
      setTimeout(disableSelectionPointerEvents, 0);
    });
  }
  function payloadFromEvent(eventData) {
    if (!eventData || !eventData.points || !eventData.points.length) return null;
    var customdata = eventData.points[0].customdata;
    var selection = selectionFromCustomData(customdata);
    var detail = detailFromCustomData(customdata);
    if (!selection && !detail) return null;
    return {
      selection: selection,
      detail: detail,
      touchedAt: Date.now()
    };
  }
  function payloadFromCustomData(customdata) {
    var selection = selectionFromCustomData(customdata);
    var detail = detailFromCustomData(customdata);
    if (!selection && !detail) return null;
    return {
      selection: selection,
      detail: detail,
      touchedAt: Date.now()
    };
  }
  function applyPayload(payload, updateDetails) {
    if (!payload) return false;
    var selection = payload.selection;
    if (selection) setSelectedWindow(selection);
    if (updateDetails) {
      var detail = payload.detail;
      if (detail) panel.innerHTML = String(detail);
    }
    return Boolean(selection || payload.detail);
  }
  function handleSelectionEvent(eventData) {
    var payload = payloadFromEvent(eventData);
    if (!payload) return;
    if (applyPayload(payload, true)) {
      lastPlotlyClickAt = Date.now();
      lastPlotlyClickKind = payload.selection ? String(payload.selection.kind || '') : '';
    }
  }
  function valueMs(value) {
    if (value === null || value === undefined) return NaN;
    if (typeof value === 'number') return value;
    var ms = Date.parse(value);
    return Number.isFinite(ms) ? ms : NaN;
  }
  function isTraceVisible(trace) {
    return trace && trace.visible !== false && trace.visible !== 'legendonly';
  }
  function axisValue(axis, pixel) {
    if (!axis) return null;
    if (typeof axis.p2d === 'function') return axis.p2d(pixel);
    if (typeof axis.p2c === 'function') return axis.p2c(pixel);
    return null;
  }
  function firstPointPayload(trace) {
    if (!trace || !trace.customdata) return null;
    if (Array.isArray(trace.customdata)) return payloadFromCustomData(trace.customdata[0]);
    return payloadFromCustomData(trace.customdata);
  }
  function fallbackPriority(payload, traceName) {
    var kind = payload && payload.selection ? String(payload.selection.kind || '') : '';
    var isHitbox = String(traceName || '').indexOf('click/hover hitbox') !== -1;
    if (kind === 'aspect_window' && isHitbox) return 0;
    if (kind === 'aspect_window') return 1;
    if (kind === 'touch_event') return 2;
    if (kind === 'regime_zone') return 3;
    if (isHitbox) return 4;
    return 5;
  }
  function isMarkerKind(kind) {
    return kind === 'touch_marker' || kind === 'selected_marker';
  }
  function payloadFromClickPosition(evt) {
    if (!gd._fullLayout || !gd._fullLayout.xaxis || !gd._fullLayout.yaxis) return null;
    var xa = gd._fullLayout.xaxis;
    var ya = gd._fullLayout.yaxis;
    var rect = gd.getBoundingClientRect();
    var plotX = evt.clientX - rect.left - xa._offset;
    var plotY = evt.clientY - rect.top - ya._offset;
    if (plotX < 0 || plotX > xa._length || plotY < 0 || plotY > ya._length) return null;
    var clickedX = axisValue(xa, plotX);
    var clickedY = axisValue(ya, plotY);
    var clickedMs = valueMs(clickedX);
    var clickedYNum = Number(clickedY);
    if (!Number.isFinite(clickedMs) || !Number.isFinite(clickedYNum)) return null;
    var best = null;
    var traces = gd.data || [];
    for (var i = 0; i < traces.length; i += 1) {
      var trace = traces[i];
      if (!isTraceVisible(trace) || !Array.isArray(trace.x) || !Array.isArray(trace.y)) continue;
      var payload = firstPointPayload(trace);
      if (!payload || !payload.selection) continue;
      var xVals = trace.x.map(valueMs).filter(Number.isFinite);
      var yVals = trace.y.map(Number).filter(Number.isFinite);
      if (!xVals.length || !yVals.length) continue;
      var x0 = Math.min.apply(null, xVals);
      var x1 = Math.max.apply(null, xVals);
      var y0 = Math.min.apply(null, yVals);
      var y1 = Math.max.apply(null, yVals);
      if (clickedMs < x0 || clickedMs > x1 || clickedYNum < y0 || clickedYNum > y1) continue;
      var duration = x1 - x0;
      var name = String(trace.name || '');
      var priority = fallbackPriority(payload, name);
      var score = [priority, duration, -i];
      if (
        !best ||
        score[0] < best.score[0] ||
        (score[0] === best.score[0] && score[1] < best.score[1]) ||
        (score[0] === best.score[0] && score[1] === best.score[1] && score[2] < best.score[2])
      ) {
        best = {payload: payload, score: score};
      }
    }
    return best ? best.payload : null;
  }
  gd.on('plotly_click', function (eventData) {
    handleSelectionEvent(eventData);
  });
  gd.addEventListener('click', function (evt) {
    if (Date.now() - lastPlotlyClickAt < 80 && isMarkerKind(lastPlotlyClickKind)) return;
    var payload = payloadFromClickPosition(evt);
    applyPayload(payload, true);
  });
}());
"""

ASPECT_WINDOW_COLORS = {
    "conjunction": "rgba(0,255,0,0.12)",
    "conjunction_orb": "rgba(34,197,94,0.12)",
    "opposition": "rgba(255,0,0,0.12)",
    "opposition_orb": "rgba(147,51,234,0.12)",
    "drishti_3": "rgba(255,165,0,0.12)",
    "drishti_4": "rgba(0,200,255,0.12)",
    "drishti_5": "rgba(180,120,255,0.12)",
    "drishti_8": "rgba(255,99,132,0.12)",
    "drishti_9": "rgba(75,192,192,0.12)",
    "drishti_10": "rgba(255,206,86,0.12)",
    "square": "rgba(255,165,0,0.12)",
    "trine": "rgba(0,0,255,0.12)",
    "sextile": "rgba(255,192,203,0.12)",
}

ASPECT_WINDOW_BORDER_COLORS = {
    "conjunction": "rgba(0,255,0,0.55)",
    "conjunction_orb": "rgba(34,197,94,0.55)",
    "opposition": "rgba(255,0,0,0.55)",
    "opposition_orb": "rgba(147,51,234,0.55)",
    "drishti_3": "rgba(255,165,0,0.55)",
    "drishti_4": "rgba(0,200,255,0.55)",
    "drishti_5": "rgba(180,120,255,0.55)",
    "drishti_8": "rgba(255,99,132,0.55)",
    "drishti_9": "rgba(75,192,192,0.55)",
    "drishti_10": "rgba(255,206,86,0.55)",
    "square": "rgba(255,165,0,0.55)",
    "trine": "rgba(0,0,255,0.55)",
    "sextile": "rgba(255,192,203,0.55)",
}

ASPECT_NAME_LABELS = {
    "conjunction": "Conjunction",
    "conjunction_orb": "Conjunction (ORB)",
    "opposition": "Opposition",
    "opposition_orb": "Opposition (ORB)",
    "drishti_3": "3rd Drishti",
    "drishti_4": "4th Drishti",
    "drishti_5": "5th Drishti",
    "drishti_8": "8th Drishti",
    "drishti_9": "9th Drishti",
    "drishti_10": "10th Drishti",
    "square": "Square",
    "trine": "Trine",
    "sextile": "Sextile",
}

ASPECT_SYSTEM_LABELS = {
    "graha": "Graha Drishti",
    "rashi": "Rashi Drishti",
    "orb": "Western Orb",
    "other": "Other",
}

ASPECT_DISPLAY_ANGLES = {
    "conjunction": 0.0,
    "conjunction_orb": 0.0,
    "opposition": 180.0,
    "opposition_orb": 180.0,
    "drishti_3": 60.0,
    "drishti_4": 90.0,
    "drishti_5": 120.0,
    "drishti_8": 210.0,
    "drishti_9": 240.0,
    "drishti_10": 270.0,
    "square": 90.0,
    "trine": 120.0,
    "sextile": 60.0,
}

ASPECT_DISPLAY_ORBS = {
    "conjunction": 3.0,
    "conjunction_orb": 1.5,
    "opposition": 1.5,
    "opposition_orb": 1.5,
    "drishti_3": 1.5,
    "drishti_4": 1.5,
    "drishti_5": 1.5,
    "drishti_8": 1.5,
    "drishti_9": 1.5,
    "drishti_10": 1.5,
    "square": 1.0,
    "trine": 1.0,
    "sextile": 0.5,
}


def normalize_body_name(name: Any) -> str:
    return str(name or "").strip().upper()


def parse_avg_members(name: Any) -> tuple[str, ...] | None:
    body = normalize_body_name(name)
    if not body.startswith("AVG(") or not body.endswith(")"):
        return None
    inner = body[4:-1].strip()
    if inner in {"ALL", "ALL7"}:
        return AVG_ALL_PLANETS
    parts = tuple(str(p).strip().upper() for p in inner.split(",") if str(p).strip())
    if not parts:
        return None
    if set(parts) == AVG_ALL_PLANET_SET:
        return AVG_ALL_PLANETS
    return parts


def circular_average_series(series_list: list[pd.Series], index: pd.Index) -> pd.Series:
    if not series_list:
        return pd.Series(np.nan, index=index, dtype=np.float64)
    frame = pd.concat([s.reindex(index) for s in series_list], axis=1)
    arr = frame.to_numpy(dtype=np.float64)
    valid = np.isfinite(arr)
    radians = np.deg2rad(np.where(valid, arr, np.nan))
    sin_sum = np.nansum(np.sin(radians), axis=1)
    cos_sum = np.nansum(np.cos(radians), axis=1)
    out = (np.degrees(np.arctan2(sin_sum, cos_sum)) % 360.0).astype(np.float64)
    out[valid.sum(axis=1) == 0] = np.nan
    return pd.Series(out, index=index, dtype=np.float64)


def fetch_planetary_longitude_or_avg(
    planet_name: str,
    dates: pd.DatetimeIndex | pd.Series | list[pd.Timestamp],
    astrology_method: str = "sidereal",
    coordinate_system: str = "geo",
) -> pd.Series:
    idx = pd.DatetimeIndex(dates)
    avg_members = parse_avg_members(planet_name)
    if not avg_members:
        return fetch_planetary_longitude(
            planet_name,
            idx,
            astrology_method=astrology_method,
            coordinate_system=coordinate_system,
        )
    member_series: list[pd.Series] = []
    for member in avg_members:
        try:
            member_series.append(
                fetch_planetary_longitude(
                    member,
                    idx,
                    astrology_method=astrology_method,
                    coordinate_system=coordinate_system,
                )
            )
        except Exception:
            continue
    return circular_average_series(member_series, idx).ffill()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export SR touch chart with enriched hovers.")
    parser.add_argument(
        "--touch-log",
        default=r"C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h.csv",
    )
    parser.add_argument(
        "--price",
        default=r"C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
    )
    parser.add_argument("--export-full-year", action="store_true", help="Export a 1-year history HTML and exit.")
    parser.add_argument(
        "--export-dir",
        default=r"C:\Users\ADMIN\Desktop\doc",
        help="Directory where exported html/csv are saved.",
    )
    parser.add_argument(
        "--export-max-lines",
        type=int,
        default=60,
        help="Maximum SR lines to display. Use 0 to include all visible identities.",
    )
    parser.add_argument(
        "--timeframe",
        choices=["m30", "hourly", "daily", "merged", "switch"],
        default="hourly",
        help="Chart timeframe. M30 uses short aspects, hourly/merged use all durations, daily uses long aspects.",
    )
    parser.add_argument(
        "--hourly-max-aspect-hours",
        type=float,
        default=24.0,
        help="Maximum aspect duration, in hours, included in M30 charts.",
    )
    parser.add_argument(
        "--daily-min-aspect-hours",
        type=float,
        default=24.0,
        help="Minimum aspect duration, in hours, included in daily charts.",
    )
    parser.add_argument("--send-to-telegram", action="store_true", help="Send exported HTML via Telegram.")
    parser.add_argument("--telegram-token", default=os.getenv("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--telegram-chat-id", default=os.getenv("TELEGRAM_CHAT_ID"))
    parser.add_argument(
        "--telegram-legacy-file",
        default=r"C:\Users\ADMIN\Desktop\Trading_Algo\New folder\cw6.py",
        help="Optional legacy telegram script for fallback credentials.",
    )
    return parser.parse_args()


def safe_json(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return {}
    if isinstance(value, float) and not pd.notna(value):
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {}


def parse_sr_config(value: Any) -> dict[str, Any]:
    cfg = safe_json(value)
    if not isinstance(cfg, dict):
        cfg = {}
    return {
        "planets": tuple(str(v).upper() for v in cfg.get("planets", ["MOON", "MERCURY", "VENUS", "SUN", "MARS", "JUPITER", "SATURN", "RAHU", "KETU", "URANUS", "NEPTUNE", "PLUTO", AVG_ALL_LABEL])),
        "harmonics": tuple(float(v) for v in cfg.get("harmonics", [0.12, 0.18])),
        "n_values": tuple(float(v) for v in cfg.get("n_values", [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])),
        "degrees": tuple(int(float(v)) for v in cfg.get("degrees", [360, 180, 90, 45])),
    }


def load_price(path: str) -> pd.DataFrame:
    price = pd.read_parquet(path).sort_index()
    if price.index.tz is None:
        price.index = price.index.tz_localize(UTC)
    price = price.tz_convert(IST)
    price.columns = [str(c).lower() for c in price.columns]
    return price


def infer_price_interval_minutes(price: pd.DataFrame) -> float | None:
    if len(price.index) < 2:
        return None
    diffs = pd.Series(price.index).sort_values().diff().dropna()
    if diffs.empty:
        return None
    return float(diffs.median().total_seconds() / 60.0)


def resample_ohlc(price: pd.DataFrame, rule: str) -> pd.DataFrame:
    agg: dict[str, str] = {}
    for col, fn in (
        ("open", "first"),
        ("high", "max"),
        ("low", "min"),
        ("close", "last"),
        ("tick_volume", "sum"),
        ("real_volume", "sum"),
        ("spread", "mean"),
    ):
        if col in price.columns:
            agg[col] = fn
    resampled = price.resample(rule).agg(agg)
    return resampled.dropna(subset=["open", "high", "low", "close"])


def resample_price_for_timeframe(price: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    interval_minutes = infer_price_interval_minutes(price)
    if timeframe == "m30":
        if interval_minutes is not None and interval_minutes > 30.0:
            raise RuntimeError(
                f"M30 chart needs real 30-minute-or-finer price data; current price file interval is about {interval_minutes:g} minutes."
            )
        if interval_minutes is not None and interval_minutes < 30.0:
            return resample_ohlc(price, "30min")
        return price.copy()
    if timeframe in {"hourly", "merged"}:
        if interval_minutes is not None and interval_minutes < 60.0:
            return resample_ohlc(price, "1h")
        return price.copy()
    if timeframe != "daily":
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    return resample_ohlc(price, "1D")


def pair_body_columns(touches: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    if {"b1", "b2"}.issubset(touches.columns):
        return (
            touches["b1"].fillna("").astype(str).str.strip().str.upper(),
            touches["b2"].fillna("").astype(str).str.strip().str.upper(),
        )
    pair_parts = touches.get("pair_key", pd.Series(index=touches.index, dtype=object)).fillna("").astype(str).str.split("|", n=1, expand=True)
    left = pair_parts[0].astype(str).str.strip().str.upper() if 0 in pair_parts.columns else pd.Series("", index=touches.index)
    right = pair_parts[1].astype(str).str.strip().str.upper() if 1 in pair_parts.columns else pd.Series("", index=touches.index)
    return left, right


def filter_short_term_slow_pairs(touches: pd.DataFrame) -> pd.DataFrame:
    if touches.empty:
        return touches.copy()
    left, right = pair_body_columns(touches)
    slow_left = left.isin(SHORT_TERM_EXCLUDED_SLOW_PAIR_BODIES)
    slow_right = right.isin(SHORT_TERM_EXCLUDED_SLOW_PAIR_BODIES)
    context_left = left.isin(SHORT_TERM_EXCLUDED_CONTEXT_PAIR_BODIES)
    context_right = right.isin(SHORT_TERM_EXCLUDED_CONTEXT_PAIR_BODIES)
    excluded_pair = (slow_left & slow_right) | (context_left & slow_right) | (slow_left & context_right)
    return touches[~excluded_pair].copy()


def filter_touches_for_timeframe(
    touches: pd.DataFrame,
    timeframe: str,
    hourly_max_aspect_hours: float = 24.0,
    daily_min_aspect_hours: float = 24.0,
) -> pd.DataFrame:
    if "event_duration_minutes" not in touches.columns:
        return touches.copy()

    duration = pd.to_numeric(touches["event_duration_minutes"], errors="coerce")
    if timeframe == "merged":
        return touches.copy()
    if timeframe == "m30":
        short = touches[duration.le(float(hourly_max_aspect_hours) * 60.0)].copy()
        return filter_short_term_slow_pairs(short)
    if timeframe == "hourly":
        return filter_short_term_slow_pairs(touches)
    if timeframe == "daily":
        return touches[duration.gt(float(daily_min_aspect_hours) * 60.0)].copy()
    raise ValueError(f"Unsupported timeframe: {timeframe}")


def timeframe_candle_label(timeframe: str) -> str:
    if timeframe == "m30":
        return "USDJPY M30"
    if timeframe == "merged":
        return "USDJPY H1 merged"
    return "USDJPY 1D" if timeframe == "daily" else "USDJPY H1"


def load_touch_log(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    dt_cols = [
        "event_time_local",
        "event_time_utc",
        "event_window_start_local",
        "event_window_end_local",
        "event_window_start_utc",
        "event_window_end_utc",
        "touch_time_local",
        "touch_time_utc",
        "after72_time_local",
        "after72_time_utc",
        "aspect_regime_start_local",
        "aspect_regime_end_local",
        "base_tn_reference_dt_local",
        "base_tn_reference_dt_source",
    ]
    for col in dt_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    numeric_cols = [
        "touch_price",
        "touch_distance_abs",
        "touch_distance_pct",
        "touch_zone",
        "ret_after_72h_pct",
        "open_touch",
        "high_touch",
        "low_touch",
        "close_touch",
        "close_after72",
        "touch_harmonic_1",
        "touch_n_value_1",
        "touch_degree_1",
        "touch_harmonic_2",
        "touch_n_value_2",
        "touch_degree_2",
        "event_pair_sep_deg",
        "event_orb_deg",
        "event_orb_limit_deg",
        "event_orb_strength",
        "event_bphs_strength",
        "event_bphs_virupa",
        "aspect_regime_id",
        "aspect_regime_active_count",
        "tn_primary_orb_deg",
        "tn_primary_orb_limit_deg",
        "tn_primary_score",
        "tn_primary_bphs_strength",
        "tn_primary_bphs_virupa",
        "tn_touch1_score",
        "tn_touch1_bphs_strength",
        "tn_touch2_bphs_strength",
        "base_tn_reference_lat",
        "base_tn_reference_lon",
        "jyotish_bullish_score",
        "jyotish_bearish_score",
        "jyotish_net_score",
        "jyotish_conflict_score",
        "jyotish_scored_hit_count",
        "base_jyotish_bullish_score",
        "base_jyotish_bearish_score",
        "base_jyotish_net_score",
        "base_jyotish_conflict_score",
        "base_jyotish_scored_hit_count",
        "quote_jyotish_bullish_score",
        "quote_jyotish_bearish_score",
        "quote_jyotish_net_score",
        "quote_jyotish_conflict_score",
        "quote_jyotish_scored_hit_count",
        "doctrine_bullish_score",
        "doctrine_bearish_score",
        "doctrine_net_score",
        "doctrine_conflict_score",
        "doctrine_dignity_virupa_avg",
        "doctrine_dignity_strength_factor_avg",
        "base_doctrine_net_score",
        "quote_doctrine_net_score",
        "fx_base_net_score",
        "fx_quote_net_score",
        "fx_pair_net_score",
        "fx_pair_conflict_score",
        "fx_pair_conflict_ratio",
        "fx_base_scored_hit_count",
        "fx_quote_scored_hit_count",
        "fx_rule_layer_total_strength",
        "fx_doctrine_base_net_score",
        "fx_doctrine_quote_net_score",
        "fx_doctrine_pair_net_score",
        "fx_doctrine_pair_conflict_score",
        "fx_doctrine_pair_conflict_ratio",
        "fx_doctrine_base_dignity_virupa_avg",
        "fx_doctrine_quote_dignity_virupa_avg",
        "fx_doctrine_rule_layer_total_strength",
        "dominant_aspect_signed_score",
        "dominant_aspect_abs_score",
        "rule_layer_total_strength",
        "rule_layer_conflict_ratio",
        "sr_confirmation_score",
        "active_hard_aspect_count",
        "active_soft_aspect_count",
        "has_mixed_hard_soft_aspects",
        "event_json_has_moon",
        "event_json_has_outer_or_node",
        "event_json_max_duration_minutes",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "touch_id" not in df.columns:
        df["touch_id"] = df.index.astype(str)
    df["touch_id"] = df["touch_id"].astype(str)

    if "touch_has_moon" in df.columns:
        df["touch_has_moon"] = pd.to_numeric(df["touch_has_moon"], errors="coerce").fillna(0).astype(int)

    if "event_duration_minutes" in df.columns:
        df["event_duration_minutes"] = pd.to_numeric(df["event_duration_minutes"], errors="coerce")

    if {"b1", "b2"}.issubset(df.columns):
        b1 = df["b1"].astype(str).str.strip().str.upper()
        b2 = df["b2"].astype(str).str.strip().str.upper()
        df = df[~b1.eq(b2)].copy()
    if "pair_key" in df.columns:
        pair_parts = df["pair_key"].astype(str).str.split("|", n=1, expand=True)
        if pair_parts.shape[1] == 2:
            left = pair_parts[0].astype(str).str.strip().str.upper()
            right = pair_parts[1].astype(str).str.strip().str.upper()
            df = df[~left.eq(right)].copy()

    # Keep only decisive directional windows
    df = df[df["ret_after_72h_dir"].isin(["UP", "DOWN"])].copy()
    df["zone_kind"] = df["ret_after_72h_dir"].map({"UP": "bullish", "DOWN": "bearish"})
    df["zone_label"] = df["touch_kind"].map({"confluence": "Confluence", "nearest_line": "Nearest Line"}) + " " + df["zone_kind"].str.title() + " 72h"
    df["edge_score"] = pd.to_numeric(df["ret_after_72h_pct"], errors="coerce").abs()
    add_rule_layer_scores(df)
    df["hover_text"] = df.apply(build_hover_text, axis=1)
    df["touch_event_label"] = df["pair_key"].astype(str) + " | " + df["aspect"].astype(str)
    return df.reset_index(drop=True)


def add_rule_layer_scores(df: pd.DataFrame) -> None:
    if df.empty:
        return

    df["aspect_family"] = df.get("aspect", pd.Series(index=df.index, dtype=object)).map(aspect_family)
    df["duration_bucket"] = df.get("event_duration_minutes", pd.Series(index=df.index, dtype=object)).map(duration_bucket)
    df["sr_confirmation_score"] = (
        df.get("touch_kind", pd.Series(index=df.index, dtype=object))
        .fillna("")
        .astype(str)
        .map({"confluence": 1.0, "nearest_line": 0.6})
        .fillna(0.0)
    )

    if "event_aspects_json" in df.columns:
        aspect_stats = pd.DataFrame(df["event_aspects_json"].map(aspect_stats_from_event_json).tolist())
        if not aspect_stats.empty:
            for col in aspect_stats.columns:
                df[col] = aspect_stats[col].values

    scored = pd.DataFrame(df.apply(score_transit_natal_hits_for_row, axis=1).tolist())
    if not scored.empty:
        for col in scored.columns:
            df[col] = scored[col].values
    else:
        df["jyotish_hypothesis_direction"] = "UNKNOWN"
        df["dominant_aspect_id"] = ""
        for col in (
            "jyotish_bullish_score",
            "jyotish_bearish_score",
            "jyotish_net_score",
            "jyotish_conflict_score",
            "jyotish_scored_hit_count",
            "dominant_aspect_signed_score",
            "dominant_aspect_abs_score",
            "doctrine_bullish_score",
            "doctrine_bearish_score",
            "doctrine_net_score",
            "doctrine_conflict_score",
            "doctrine_dignity_virupa_avg",
            "doctrine_dignity_strength_factor_avg",
            "doctrine_dominant_aspect_signed_score",
            "doctrine_dominant_aspect_abs_score",
        ):
            df[col] = 0.0
        df["doctrine_hypothesis_direction"] = "UNKNOWN"
        df["doctrine_dominant_aspect_id"] = ""
        df["doctrine_dominant_dignity"] = ""

    fx_scored = pd.DataFrame(df.apply(score_currency_pair_for_row, axis=1).tolist())
    if not fx_scored.empty:
        for col in fx_scored.columns:
            df[col] = fx_scored[col].values
    else:
        df["fx_hypothesis_direction"] = "UNKNOWN"
        df["fx_pair_net_score"] = 0.0
        df["fx_pair_conflict_score"] = 0.0
        df["fx_pair_conflict_ratio"] = 0.0
        df["fx_doctrine_hypothesis_direction"] = "UNKNOWN"
        df["fx_doctrine_pair_net_score"] = 0.0
        df["fx_doctrine_pair_conflict_score"] = 0.0
        df["fx_doctrine_pair_conflict_ratio"] = 0.0
        df["fx_scoring_notes"] = "base_reference_missing;pair_hypothesis_not_scored"

    event_strength = numeric_series(df, "event_bphs_strength")
    df["geometric_strength_score"] = event_strength
    df["rule_layer_total_strength"] = (
        numeric_series(df, "dominant_aspect_abs_score")
        + 0.35 * event_strength
        + 0.25 * numeric_series(df, "sr_confirmation_score")
    )
    df["fx_rule_layer_total_strength"] = (
        numeric_series(df, "fx_pair_net_score").abs()
        + 0.35 * event_strength
        + 0.25 * numeric_series(df, "sr_confirmation_score")
    )
    df["fx_doctrine_rule_layer_total_strength"] = (
        numeric_series(df, "fx_doctrine_pair_net_score").abs()
        + 0.35 * event_strength
        + 0.25 * numeric_series(df, "sr_confirmation_score")
    )
    total_directional = (
        numeric_series(df, "jyotish_bullish_score")
        + numeric_series(df, "jyotish_bearish_score")
    )
    conflict = numeric_series(df, "jyotish_conflict_score")
    df["rule_layer_conflict_ratio"] = np.where(total_directional > 0.0, conflict / total_directional, 0.0)
    df["rule_layer_notes"] = (
        "heuristic_v1_yen_ipo_tokyo_1889_reference;"
        "uses_transit_natal_house_planet_nature_aspect_family_bphs_sr;"
        "fx_pair_score_is_base_minus_quote_when_base_reference_fields_exist;"
        "doctrine_v1_uses_sign_dignity_friendship_sthana_bala_for_classical_planets;"
        "avg_all_scoring_expands_to_7_classical_planets;"
        "ml_must_validate"
    )


def infer_aspect_system(aspect: Any) -> str:
    name = str(aspect).strip().lower()
    if name.startswith("rashi_"):
        return "rashi"
    if name in {"sextile", "square", "trine", "conjunction_orb", "opposition_orb"}:
        return "orb"
    if name in ASPECT_NAME_LABELS:
        return "graha" if not name.startswith("rashi_") else "rashi"
    return "other"


def _safe_float(value: Any) -> float | None:
    try:
        val = float(value)
    except Exception:
        return None
    if pd.isna(val):
        return None
    return val


def numeric_series(df: pd.DataFrame, col: str, default: float = 0.0) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=float)
    return pd.to_numeric(df[col], errors="coerce").fillna(default)


def _format_float(value: Any) -> str:
    num = _safe_float(value)
    if num is None:
        return "n/a"
    return f"{num:.3f}"


def _format_pct(value: Any) -> str:
    num = _safe_float(value)
    if num is None:
        return "n/a"
    return f"{num:.1%}"


def html_lines(title: str, lines: list[str]) -> str:
    body = "<br>".join(html.escape(str(line)) for line in lines)
    return f"<b>{html.escape(title)}</b><br>{body}"


def format_duration_minutes(value: Any) -> str:
    minutes = _safe_float(value)
    if minutes is None:
        return "n/a"
    total = int(round(minutes))
    days, rem = divmod(total, 1440)
    hours, mins = divmod(rem, 60)
    if days > 0:
        return f"{days}d {hours}h"
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def build_event_hover_lines(row: pd.Series) -> list[str]:
    aspect = row.get("aspect", "")
    aspect_norm = str(aspect).strip().lower()
    aspect_label = str(row.get("aspect_label", "")).strip() or ASPECT_NAME_LABELS.get(aspect_norm, str(aspect_norm))
    pair_key = str(row.get("pair_key", "")).strip()
    event_orb_deg = _safe_float(row.get("event_orb_deg"))
    event_orb_limit = _safe_float(row.get("event_orb_limit_deg"))
    if event_orb_limit is None:
        event_orb_limit = _safe_float(ASPECT_DISPLAY_ORBS.get(aspect_norm))
    event_bphs_strength = _safe_float(row.get("event_bphs_strength"))
    event_bphs_virupa = _safe_float(row.get("event_bphs_virupa"))

    lines = [
        f"Pair: {pair_key}",
        f"Aspect: {aspect_label}",
        f"Duration: {format_duration_minutes(row.get('event_duration_minutes'))}",
    ]
    if event_orb_limit is not None:
        if event_orb_deg is not None:
            lines.append(f"Orb: {event_orb_deg:.3f}deg / {event_orb_limit:.3f}deg")
        else:
            lines.append(f"Orb: +/-{event_orb_limit:.3f}deg")
    if event_bphs_strength is not None:
        virupa_text = f" ({event_bphs_virupa:.1f}/60)" if event_bphs_virupa is not None else ""
        lines.append(f"BPHS-like strength: {event_bphs_strength:.3f}{virupa_text}")
    lines.extend(build_rule_layer_hover_lines(row))
    return lines


def build_rule_layer_hover_lines(row: pd.Series) -> list[str]:
    if "fx_hypothesis_direction" not in row.index:
        return []
    reference_time = str(row.get("reference_time_ist", row.get("tn_reference_dt_local", ""))).strip()
    source_time = str(row.get("source_reference_time", row.get("tn_reference_dt_source", ""))).strip()
    source_tz = str(row.get("source_reference_tz", row.get("tn_reference_source_tz", ""))).strip()
    ref_text = source_time
    if source_tz:
        ref_text = f"{ref_text} {source_tz}".strip()
    if not ref_text and reference_time:
        ref_text = reference_time

    base_label = str(row.get("fx_base_reference_label", row.get("base_reference_label", "USD")) or "USD").strip()
    quote_label = str(row.get("fx_quote_reference_label", row.get("quote_reference_label", "JPY")) or "JPY").strip()
    base_source_time = str(row.get("base_tn_reference_dt_source", "")).strip()
    base_source_tz = str(row.get("base_tn_reference_source_tz", "")).strip()
    base_ref_text = f"{base_source_time} {base_source_tz}".strip()
    if not base_ref_text:
        base_ref_text = str(row.get("base_tn_reference_dt_local", "")).strip()
    lines = [
        "--- USDJPY hypothesis ---",
        f"Pair model: {base_label}/{quote_label} = base score - quote score",
        f"Hypothesis: {str(row.get('fx_hypothesis_direction', 'UNKNOWN'))}",
        (
            "USD/JPY/net/conflict: "
            f"{_format_float(row.get('fx_base_net_score'))} / "
            f"{_format_float(row.get('fx_quote_net_score'))} / "
            f"{_format_float(row.get('fx_pair_net_score'))} / "
            f"{_format_float(row.get('fx_pair_conflict_score'))}"
        ),
        f"Doctrine hypothesis: {str(row.get('fx_doctrine_hypothesis_direction', 'UNKNOWN'))}",
        (
            "Doctrine USD/JPY/net/conflict: "
            f"{_format_float(row.get('fx_doctrine_base_net_score'))} / "
            f"{_format_float(row.get('fx_doctrine_quote_net_score'))} / "
            f"{_format_float(row.get('fx_doctrine_pair_net_score'))} / "
            f"{_format_float(row.get('fx_doctrine_pair_conflict_score'))}"
        ),
        (
            "Dignity avg USD/JPY: "
            f"{_format_float(row.get('fx_doctrine_base_dignity_virupa_avg'))}V / "
            f"{_format_float(row.get('fx_doctrine_quote_dignity_virupa_avg'))}V"
        ),
        f"Conflict ratio: {_format_pct(row.get('fx_pair_conflict_ratio'))}",
        f"Dominant USD hit: {str(row.get('fx_dominant_base_hit', '')).strip() or 'n/a'}",
        f"Dominant JPY hit: {str(row.get('fx_dominant_quote_hit', '')).strip() or 'n/a'}",
        f"Doctrine dominant USD: {str(row.get('fx_doctrine_dominant_base_dignity', '')).strip() or 'n/a'}",
        f"Doctrine dominant JPY: {str(row.get('fx_doctrine_dominant_quote_dignity', '')).strip() or 'n/a'}",
        f"FX absolute strength: {_format_float(row.get('fx_rule_layer_total_strength'))}",
        f"Doctrine FX strength: {_format_float(row.get('fx_doctrine_rule_layer_total_strength'))}",
        "Click for quote/JPY details.",
    ]
    return lines


def build_quote_detail_lines(row: pd.Series) -> list[str]:
    reference_time = str(row.get("reference_time_ist", row.get("tn_reference_dt_local", ""))).strip()
    source_time = str(row.get("source_reference_time", row.get("tn_reference_dt_source", ""))).strip()
    source_tz = str(row.get("source_reference_tz", row.get("tn_reference_source_tz", ""))).strip()
    ref_text = f"{source_time} {source_tz}".strip()
    if not ref_text and reference_time:
        ref_text = reference_time
    return [
        f"Pair: {str(row.get('pair_key', '')).strip()}",
        f"Aspect: {str(row.get('aspect_label', '')).strip() or str(row.get('aspect', '')).strip()}",
        f"Quote reference: {ref_text or 'Yen IPO Tokyo 1889-02-11 00:00 Asia/Tokyo'}",
        f"Quote/JPY hypothesis: {str(row.get('jyotish_hypothesis_direction', 'UNKNOWN'))}",
        (
            "JPY scores B/Bear/Net/Conflict: "
            f"{_format_float(row.get('jyotish_bullish_score'))} / "
            f"{_format_float(row.get('jyotish_bearish_score'))} / "
            f"{_format_float(row.get('jyotish_net_score'))} / "
            f"{_format_float(row.get('jyotish_conflict_score'))}"
        ),
        f"JPY doctrine hypothesis: {str(row.get('doctrine_hypothesis_direction', 'UNKNOWN'))}",
        (
            "JPY doctrine B/Bear/Net/Conflict: "
            f"{_format_float(row.get('doctrine_bullish_score'))} / "
            f"{_format_float(row.get('doctrine_bearish_score'))} / "
            f"{_format_float(row.get('doctrine_net_score'))} / "
            f"{_format_float(row.get('doctrine_conflict_score'))}"
        ),
        f"JPY dignity avg: {_format_float(row.get('doctrine_dignity_virupa_avg'))}V",
        f"JPY dominant hit: {str(row.get('dominant_aspect_id', '')).strip() or 'n/a'}",
        f"JPY dominant strength: {_format_float(row.get('dominant_aspect_abs_score'))}",
        f"JPY doctrine dominant dignity: {str(row.get('doctrine_dominant_dignity', '')).strip() or 'n/a'}",
        f"JPY rule total strength: {_format_float(row.get('rule_layer_total_strength'))}",
        f"JPY conflict ratio: {_format_pct(row.get('rule_layer_conflict_ratio'))}",
        f"Aspect family / duration: {str(row.get('aspect_family', ''))} / {str(row.get('duration_bucket', ''))}",
        f"Active hard/soft: {_format_float(row.get('active_hard_aspect_count'))} / {_format_float(row.get('active_soft_aspect_count'))}",
        "Note: quote/JPY details are diagnostics; USDJPY direction comes from the FX score.",
    ]


def build_event_detail_html(row: pd.Series) -> str:
    return html_lines("Quote/JPY Details", build_quote_detail_lines(row))


def _selection_timestamp(value: Any) -> str:
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return ""
    return pd.Timestamp(ts).isoformat()


def event_selection_customdata(
    row: pd.Series,
    detail_html: str,
    start_col: str,
    end_col: str,
    label: str,
    kind: str,
    identity: str = "",
) -> list[str]:
    return [
        identity or kind,
        detail_html,
        _selection_timestamp(row.get(start_col)),
        _selection_timestamp(row.get(end_col)),
        label,
        kind,
    ]


def build_selection_hitbox_polygon(
    x0: Any,
    x1: Any,
    y0: float,
    y1: float,
    hover_text: str,
    customdata: list[str],
    name: str,
) -> go.Scatter:
    return go.Scatter(
        x=[x0, x0, x1, x1, x0],
        y=[y0, y1, y1, y0, y0],
        mode="lines",
        line=dict(color="rgba(255,255,255,0)", width=0.1),
        fill="toself",
        fillcolor="rgba(255,255,255,0.001)",
        hoveron="fills",
        text=hover_text,
        customdata=[customdata] * 5,
        hovertemplate="%{text}<extra></extra>",
        name=name,
        showlegend=False,
    )


def build_hover_text(row: pd.Series) -> str:
    return "<br>".join(build_event_hover_lines(row))


def build_cluster_hover_text(row: pd.Series) -> str:
    return str(row["hover_text"])


def cluster_touch_rows(touches: pd.DataFrame) -> pd.DataFrame:
    if touches.empty:
        return touches.copy()

    work = touches.copy()
    work["touch_time_local"] = pd.to_datetime(work["touch_time_local"], errors="coerce")
    work["touch_distance_abs"] = pd.to_numeric(work["touch_distance_abs"], errors="coerce")
    work["edge_score"] = pd.to_numeric(work["edge_score"], errors="coerce")

    id1 = work["touch_identity_1_text"].fillna("").astype(str).str.strip()
    id2 = work["touch_identity_2_text"].fillna("").astype(str).str.strip()
    id1 = id1.mask(id1.str.lower().eq("nan"), "")
    id2 = id2.mask(id2.str.lower().eq("nan"), "")
    swap = id2.ne("") & (id1.eq("") | id2.lt(id1))
    work["_identity_key"] = np.where(
        id2.eq(""),
        id1,
        np.where(swap, id2 + "__" + id1, id1 + "__" + id2),
    )
    work["_identity_key"] = pd.Series(work["_identity_key"], index=work.index)
    work["_identity_key"] = work["_identity_key"].mask(work["_identity_key"].eq(""), work["touch_kind"].astype(str))

    touch_price = pd.to_numeric(work["touch_price"], errors="coerce")
    low_touch = pd.to_numeric(work["low_touch"], errors="coerce")
    high_touch = pd.to_numeric(work["high_touch"], errors="coerce")
    work["_contains_touch_price"] = low_touch.le(touch_price) & touch_price.le(high_touch)
    work["_contains_touch_price"] = work["_contains_touch_price"].fillna(False)
    work["_distance_rank"] = work["touch_distance_abs"].fillna(float("inf"))
    work["_edge_rank"] = work["edge_score"].fillna(float("-inf"))

    work = work.sort_values(
        ["event_id", "touch_kind", "_identity_key", "touch_time_local", "_distance_rank"],
        ascending=[True, True, True, True, True],
    ).reset_index(drop=True)

    gap = work["touch_time_local"] - work["touch_time_local"].shift()
    regime_ids = pd.to_numeric(work.get("aspect_regime_id"), errors="coerce")
    same_group_as_prev = (
        work["event_id"].eq(work["event_id"].shift())
        & work["touch_kind"].eq(work["touch_kind"].shift())
        & regime_ids.eq(regime_ids.shift())
        & work["_identity_key"].eq(work["_identity_key"].shift())
        & gap.le(TOUCH_CLUSTER_GAP)
    )
    work["_cluster_id"] = (~same_group_as_prev).cumsum()

    cluster_stats = (
        work.groupby("_cluster_id", sort=False)
        .agg(
            cluster_size=("touch_id", "size"),
            cluster_start_time_local=("touch_time_local", "min"),
            cluster_end_time_local=("touch_time_local", "max"),
        )
        .reset_index()
    )

    clustered = (
        work.sort_values(
            ["_cluster_id", "_contains_touch_price", "_distance_rank", "_edge_rank", "touch_time_local"],
            ascending=[True, False, True, False, True],
        )
        .drop_duplicates("_cluster_id", keep="first")
        .merge(cluster_stats, on="_cluster_id", how="left")
        .sort_values(["touch_time_local", "edge_score"], ascending=[True, False])
        .reset_index(drop=True)
    )
    if clustered.empty:
        return clustered

    clustered["hover_text"] = clustered.apply(build_cluster_hover_text, axis=1)
    return clustered.drop(
        columns=["_identity_key", "_contains_touch_price", "_distance_rank", "_edge_rank", "_cluster_id"],
        errors="ignore",
    )


def apply_filters(
    touches: pd.DataFrame,
    zone_types: list[str],
    touch_kinds: list[str],
    pair_filter: str | None,
    aspect_filter: str | None,
) -> pd.DataFrame:
    subset = touches[touches["zone_kind"].isin(zone_types) & touches["touch_kind"].isin(touch_kinds)].copy()
    if pair_filter and pair_filter != ALL_FILTER_VALUE:
        subset = subset[subset["pair_key"] == pair_filter]
    if aspect_filter and aspect_filter != ALL_FILTER_VALUE:
        subset = subset[subset["aspect"] == aspect_filter]
    return subset


def build_aspect_window_polygon(row: pd.Series, y0: float, y1: float) -> go.Scatter:
    x0 = row["event_window_start_local"]
    x1 = row["event_window_end_local"]
    aspect = str(row.get("aspect", "")).strip().lower()
    aspect_label = str(row.get("aspect_label", "")).strip() or ASPECT_NAME_LABELS.get(aspect, str(row.get("aspect", "")))
    hover_lines = build_event_hover_lines(row)
    detail_html = build_event_detail_html(row)
    customdata = event_selection_customdata(
        row,
        detail_html,
        "event_window_start_local",
        "event_window_end_local",
        f"{str(row.get('pair_key', '')).strip()} {aspect_label}",
        "aspect_window",
        str(row.get("event_id", "")).strip(),
    )
    return go.Scatter(
        x=[x0, x0, x1, x1, x0],
        y=[y0, y1, y1, y0, y0],
        mode="lines",
        line=dict(color=ASPECT_WINDOW_BORDER_COLORS.get(aspect, "rgba(148,163,184,0.55)"), width=1.1),
        fill="toself",
        fillcolor=ASPECT_WINDOW_COLORS.get(aspect, "rgba(148,163,184,0.05)"),
        hoveron="fills",
        text="<br>".join(hover_lines),
        customdata=[customdata] * 5,
        hovertemplate="%{text}<extra></extra>",
        name=f"{aspect_label} window",
        showlegend=False,
    )


def build_aspect_window_hitbox_polygon(row: pd.Series, y0: float, y1: float) -> go.Scatter:
    aspect = str(row.get("aspect", "")).strip().lower()
    aspect_label = str(row.get("aspect_label", "")).strip() or ASPECT_NAME_LABELS.get(aspect, str(row.get("aspect", "")))
    detail_html = build_event_detail_html(row)
    customdata = event_selection_customdata(
        row,
        detail_html,
        "event_window_start_local",
        "event_window_end_local",
        f"{str(row.get('pair_key', '')).strip()} {aspect_label}",
        "aspect_window",
        str(row.get("event_id", "")).strip(),
    )
    return build_selection_hitbox_polygon(
        row["event_window_start_local"],
        row["event_window_end_local"],
        y0,
        y1,
        "<br>".join(build_event_hover_lines(row)),
        customdata,
        f"{aspect_label} click/hover hitbox",
    )


def _score_direction(bullish: float, bearish: float) -> str:
    if bullish <= 0.0 and bearish <= 0.0:
        return "UNKNOWN"
    if bullish > bearish * 1.25:
        return "BULLISH"
    if bearish > bullish * 1.25:
        return "BEARISH"
    return "CONFLICT"


def _fx_direction(net: float, conflict_ratio: float) -> str:
    if not np.isfinite(net):
        return "UNKNOWN"
    if abs(net) <= 0.05:
        return "CONFLICT"
    if conflict_ratio >= 0.45:
        return "CONFLICT"
    return "BULLISH" if net > 0 else "BEARISH"


def _num(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except Exception:
        return default
    return out if np.isfinite(out) else default


def _strongest_row(rows: pd.DataFrame, strength_col: str) -> pd.Series | None:
    if rows.empty or strength_col not in rows.columns:
        return None
    strength = pd.to_numeric(rows[strength_col], errors="coerce").abs().fillna(0.0)
    if strength.max() <= 0.0:
        return None
    return rows.loc[strength.idxmax()]


def event_brief(row: pd.Series) -> str:
    pair = str(row.get("pair_key", "")).strip()
    aspect = str(row.get("aspect_label", "")).strip() or str(row.get("aspect", "")).strip()
    return f"{pair} {aspect}".strip()


def build_regime_zones(aspect_windows: pd.DataFrame) -> pd.DataFrame:
    if aspect_windows.empty:
        return pd.DataFrame()
    required = {"event_window_start_local", "event_window_end_local", "pair_key", "aspect"}
    if not required.issubset(aspect_windows.columns):
        return pd.DataFrame()

    work = aspect_windows.copy()
    work["event_window_start_local"] = pd.to_datetime(work["event_window_start_local"], errors="coerce")
    work["event_window_end_local"] = pd.to_datetime(work["event_window_end_local"], errors="coerce")
    work = work.dropna(subset=["event_window_start_local", "event_window_end_local"])
    work = work[work["event_window_end_local"].gt(work["event_window_start_local"])].copy()
    if work.empty:
        return pd.DataFrame()

    bounds = sorted(set(work["event_window_start_local"].tolist() + work["event_window_end_local"].tolist()))
    zones: list[dict[str, Any]] = []
    for left, right in zip(bounds, bounds[1:], strict=False):
        if pd.Timestamp(right) <= pd.Timestamp(left):
            continue
        active = work[
            work["event_window_start_local"].lt(right)
            & work["event_window_end_local"].gt(left)
        ].copy()
        if active.empty:
            continue

        jy_bull = pd.to_numeric(active.get("jyotish_bullish_score"), errors="coerce").fillna(0.0).sum()
        jy_bear = pd.to_numeric(active.get("jyotish_bearish_score"), errors="coerce").fillna(0.0).sum()
        jy_conflict = min(float(jy_bull), float(jy_bear))
        fx_base = pd.to_numeric(active.get("fx_base_net_score"), errors="coerce").fillna(0.0).sum()
        fx_quote = pd.to_numeric(active.get("fx_quote_net_score"), errors="coerce").fillna(0.0).sum()
        fx_net = pd.to_numeric(active.get("fx_pair_net_score"), errors="coerce").fillna(0.0).sum()
        fx_conflict = pd.to_numeric(active.get("fx_pair_conflict_score"), errors="coerce").fillna(0.0).sum()
        fx_doctrine_base = pd.to_numeric(active.get("fx_doctrine_base_net_score"), errors="coerce").fillna(0.0).sum()
        fx_doctrine_quote = pd.to_numeric(active.get("fx_doctrine_quote_net_score"), errors="coerce").fillna(0.0).sum()
        fx_doctrine_net = pd.to_numeric(active.get("fx_doctrine_pair_net_score"), errors="coerce").fillna(0.0).sum()
        fx_doctrine_conflict = pd.to_numeric(active.get("fx_doctrine_pair_conflict_score"), errors="coerce").fillna(0.0).sum()
        fx_total = (
            pd.to_numeric(active.get("fx_base_net_score"), errors="coerce").fillna(0.0).abs()
            + pd.to_numeric(active.get("fx_quote_net_score"), errors="coerce").fillna(0.0).abs()
        ).sum()
        fx_doctrine_total = (
            pd.to_numeric(active.get("fx_doctrine_base_net_score"), errors="coerce").fillna(0.0).abs()
            + pd.to_numeric(active.get("fx_doctrine_quote_net_score"), errors="coerce").fillna(0.0).abs()
        ).sum()
        fx_conflict_ratio = float(fx_conflict / fx_total) if fx_total > 0.0 else 0.0
        fx_doctrine_conflict_ratio = float(fx_doctrine_conflict / fx_doctrine_total) if fx_doctrine_total > 0.0 else 0.0
        dominant = _strongest_row(active, "dominant_aspect_abs_score")
        fx_dominant = _strongest_row(active, "fx_pair_net_score")
        fx_doctrine_dominant = _strongest_row(active, "fx_doctrine_pair_net_score")
        event_lines = [event_brief(row) for _, row in active.head(10).iterrows()]
        if len(active) > 10:
            event_lines.append(f"... +{len(active) - 10} more")

        zones.append(
            {
                "regime_window_start_local": pd.Timestamp(left),
                "regime_window_end_local": pd.Timestamp(right),
                "regime_active_event_count": int(len(active)),
                "regime_kind": "overlap" if len(active) > 1 else "single",
                "regime_active_events_text": " | ".join(event_lines),
                "regime_jyotish_bullish_score": float(jy_bull),
                "regime_jyotish_bearish_score": float(jy_bear),
                "regime_jyotish_net_score": float(jy_bull - jy_bear),
                "regime_jyotish_conflict_score": float(jy_conflict),
                "regime_jyotish_hypothesis_direction": _score_direction(float(jy_bull), float(jy_bear)),
                "regime_dominant_hit": str(dominant.get("dominant_aspect_id", "")) if dominant is not None else "",
                "regime_dominant_strength": _num(dominant.get("dominant_aspect_abs_score")) if dominant is not None else 0.0,
                "regime_dominant_event": event_brief(dominant) if dominant is not None else "",
                "regime_rule_total_strength": pd.to_numeric(active.get("rule_layer_total_strength"), errors="coerce").fillna(0.0).sum(),
                "regime_fx_base_net_score": float(fx_base),
                "regime_fx_quote_net_score": float(fx_quote),
                "regime_fx_pair_net_score": float(fx_net),
                "regime_fx_pair_conflict_score": float(fx_conflict),
                "regime_fx_pair_conflict_ratio": float(fx_conflict_ratio),
                "regime_fx_hypothesis_direction": _fx_direction(float(fx_net), float(fx_conflict_ratio)) if fx_total > 0.0 else "UNKNOWN",
                "regime_fx_doctrine_base_net_score": float(fx_doctrine_base),
                "regime_fx_doctrine_quote_net_score": float(fx_doctrine_quote),
                "regime_fx_doctrine_pair_net_score": float(fx_doctrine_net),
                "regime_fx_doctrine_pair_conflict_score": float(fx_doctrine_conflict),
                "regime_fx_doctrine_pair_conflict_ratio": float(fx_doctrine_conflict_ratio),
                "regime_fx_doctrine_hypothesis_direction": _fx_direction(float(fx_doctrine_net), float(fx_doctrine_conflict_ratio)) if fx_doctrine_total > 0.0 else "UNKNOWN",
                "regime_fx_dominant_event": event_brief(fx_dominant) if fx_dominant is not None else "",
                "regime_fx_dominant_base_hit": str(fx_dominant.get("fx_dominant_base_hit", "")) if fx_dominant is not None else "",
                "regime_fx_dominant_quote_hit": str(fx_dominant.get("fx_dominant_quote_hit", "")) if fx_dominant is not None else "",
                "regime_fx_doctrine_dominant_event": event_brief(fx_doctrine_dominant) if fx_doctrine_dominant is not None else "",
                "regime_fx_doctrine_dominant_base_dignity": str(fx_doctrine_dominant.get("fx_doctrine_dominant_base_dignity", "")) if fx_doctrine_dominant is not None else "",
                "regime_fx_doctrine_dominant_quote_dignity": str(fx_doctrine_dominant.get("fx_doctrine_dominant_quote_dignity", "")) if fx_doctrine_dominant is not None else "",
                "regime_fx_rule_total_strength": pd.to_numeric(active.get("fx_rule_layer_total_strength"), errors="coerce").fillna(0.0).sum(),
                "regime_fx_doctrine_rule_total_strength": pd.to_numeric(active.get("fx_doctrine_rule_layer_total_strength"), errors="coerce").fillna(0.0).sum(),
            }
        )
    return pd.DataFrame(zones)


def build_regime_zone_hover_lines(row: pd.Series) -> list[str]:
    return [
        "--- Active regime zone ---",
        f"Window: {row.get('regime_window_start_local')} to {row.get('regime_window_end_local')}",
        f"Active events: {int(_num(row.get('regime_active_event_count')))}",
        f"Events: {str(row.get('regime_active_events_text', '')).strip() or 'n/a'}",
        "--- USDJPY regime hypothesis ---",
        "Pair model: USDJPY = base score - quote score",
        f"Hypothesis: {str(row.get('regime_fx_hypothesis_direction', 'UNKNOWN'))}",
        (
            "USD/JPY/net/conflict: "
            f"{_format_float(row.get('regime_fx_base_net_score'))} / "
            f"{_format_float(row.get('regime_fx_quote_net_score'))} / "
            f"{_format_float(row.get('regime_fx_pair_net_score'))} / "
            f"{_format_float(row.get('regime_fx_pair_conflict_score'))}"
        ),
        f"Doctrine hypothesis: {str(row.get('regime_fx_doctrine_hypothesis_direction', 'UNKNOWN'))}",
        (
            "Doctrine USD/JPY/net/conflict: "
            f"{_format_float(row.get('regime_fx_doctrine_base_net_score'))} / "
            f"{_format_float(row.get('regime_fx_doctrine_quote_net_score'))} / "
            f"{_format_float(row.get('regime_fx_doctrine_pair_net_score'))} / "
            f"{_format_float(row.get('regime_fx_doctrine_pair_conflict_score'))}"
        ),
        f"Conflict ratio: {_format_pct(row.get('regime_fx_pair_conflict_ratio'))}",
        f"Dominant event: {str(row.get('regime_fx_dominant_event', '')).strip() or 'n/a'}",
        f"Dominant USD hit: {str(row.get('regime_fx_dominant_base_hit', '')).strip() or 'n/a'}",
        f"Dominant JPY hit: {str(row.get('regime_fx_dominant_quote_hit', '')).strip() or 'n/a'}",
        f"Doctrine dominant event: {str(row.get('regime_fx_doctrine_dominant_event', '')).strip() or 'n/a'}",
        f"Doctrine dominant USD: {str(row.get('regime_fx_doctrine_dominant_base_dignity', '')).strip() or 'n/a'}",
        f"Doctrine dominant JPY: {str(row.get('regime_fx_doctrine_dominant_quote_dignity', '')).strip() or 'n/a'}",
        f"FX absolute strength: {_format_float(row.get('regime_fx_rule_total_strength'))}",
        f"Doctrine FX strength: {_format_float(row.get('regime_fx_doctrine_rule_total_strength'))}",
        "Click for quote/JPY details.",
    ]


def build_regime_zone_detail_lines(row: pd.Series) -> list[str]:
    return [
        f"Window: {row.get('regime_window_start_local')} to {row.get('regime_window_end_local')}",
        f"Active events: {int(_num(row.get('regime_active_event_count')))}",
        f"Events: {str(row.get('regime_active_events_text', '')).strip() or 'n/a'}",
        f"Quote/JPY hypothesis: {str(row.get('regime_jyotish_hypothesis_direction', 'UNKNOWN'))}",
        (
            "JPY scores B/Bear/Net/Conflict: "
            f"{_format_float(row.get('regime_jyotish_bullish_score'))} / "
            f"{_format_float(row.get('regime_jyotish_bearish_score'))} / "
            f"{_format_float(row.get('regime_jyotish_net_score'))} / "
            f"{_format_float(row.get('regime_jyotish_conflict_score'))}"
        ),
        f"JPY dominant hit: {str(row.get('regime_dominant_hit', '')).strip() or 'n/a'}",
        f"Dominant event: {str(row.get('regime_dominant_event', '')).strip() or 'n/a'}",
        f"JPY dominant strength: {_format_float(row.get('regime_dominant_strength'))}",
        f"JPY rule total strength: {_format_float(row.get('regime_rule_total_strength'))}",
        "Note: quote/JPY details are diagnostics; USDJPY direction comes from the FX score.",
    ]


def build_regime_zone_detail_html(row: pd.Series) -> str:
    return html_lines("Quote/JPY Regime Details", build_regime_zone_detail_lines(row))


def build_regime_zone_polygon(row: pd.Series, y0: float, y1: float) -> go.Scatter:
    x0 = row["regime_window_start_local"]
    x1 = row["regime_window_end_local"]
    kind = str(row.get("regime_kind", "single"))
    detail_html = build_regime_zone_detail_html(row)
    customdata = event_selection_customdata(
        row,
        detail_html,
        "regime_window_start_local",
        "regime_window_end_local",
        f"Active regime zone ({kind})",
        "regime_zone",
        "regime_zone",
    )
    return go.Scatter(
        x=[x0, x0, x1, x1, x0],
        y=[y0, y1, y1, y0, y0],
        mode="lines",
        line=dict(color=REGIME_ZONE_BORDER_COLORS.get(kind, "rgba(148,163,184,0.45)"), width=1.4),
        fill="toself",
        fillcolor=REGIME_ZONE_COLORS.get(kind, "rgba(148,163,184,0.05)"),
        hoveron="fills",
        text="<br>".join(build_regime_zone_hover_lines(row)),
        customdata=[customdata] * 5,
        hovertemplate="%{text}<extra></extra>",
        name="Active regime zone",
        showlegend=False,
    )


def build_regime_zone_hitbox_polygon(row: pd.Series, y0: float, y1: float) -> go.Scatter:
    kind = str(row.get("regime_kind", "single"))
    detail_html = build_regime_zone_detail_html(row)
    customdata = event_selection_customdata(
        row,
        detail_html,
        "regime_window_start_local",
        "regime_window_end_local",
        f"Active regime zone ({kind})",
        "regime_zone",
        "regime_zone",
    )
    return build_selection_hitbox_polygon(
        row["regime_window_start_local"],
        row["regime_window_end_local"],
        y0,
        y1,
        "<br>".join(build_regime_zone_hover_lines(row)),
        customdata,
        "Active regime zone click/hover hitbox",
    )


def build_zone_polygon(row: pd.Series, y0: float, y1: float) -> go.Scatter:
    x0 = row["touch_time_local"]
    x1 = row["after72_time_local"]
    zone_kind = str(row["zone_kind"])
    detail_html = build_event_detail_html(row)
    customdata = event_selection_customdata(
        row,
        detail_html,
        "event_window_start_local",
        "event_window_end_local",
        str(row.get("touch_event_label", "")).strip() or str(row.get("zone_label", "")).strip(),
        "touch_event",
        str(row.get("touch_id", "")).strip(),
    )
    return go.Scatter(
        x=[x0, x0, x1, x1, x0],
        y=[y0, y1, y1, y0, y0],
        mode="lines",
        line=dict(color=ZONE_BORDER_COLORS.get(zone_kind, "rgba(107,114,128,0.35)"), width=1),
        fill="toself",
        fillcolor=ZONE_COLORS.get(zone_kind, "rgba(107,114,128,0.18)"),
        hoveron="fills",
        text=row["hover_text"],
        customdata=[customdata] * 5,
        hovertemplate="%{text}<extra></extra>",
        name=row["zone_label"],
        showlegend=False,
    )


def identity_from_columns(row: pd.Series, which: int) -> tuple[str, str, float, float, int] | None:
    planet = str(row.get(f"touch_planet_{which}", "")).strip().upper()
    mode = str(row.get(f"touch_mode_{which}", "")).strip().lower()
    if not planet or not mode:
        return None
    try:
        harmonic = float(row.get(f"touch_harmonic_{which}"))
        n_value = float(row.get(f"touch_n_value_{which}"))
        degree = int(float(row.get(f"touch_degree_{which}")))
    except Exception:
        return None
    return (planet, mode, harmonic, n_value, degree)


def line_from_identity(lon_series: pd.Series, identity: tuple[str, str, float, float, int]) -> pd.Series:
    _, mode, harmonic, n_value, degree = identity
    base = float(harmonic) * float(n_value) * float(degree)
    lon = lon_series.astype(float)
    if mode == "mirror":
        return base + float(harmonic) * (360.0 - lon)
    return base + float(harmonic) * lon


def line_style_for_planet(planet: str) -> dict[str, Any]:
    planet_key = normalize_body_name(planet)
    if planet_key == AVG_ALL_LABEL:
        return {
            "width": 2.35,
            "color": PLANET_COLORS.get(AVG_ALL_LABEL, "#f8fafc"),
            "dash": "longdash",
        }
    return {
        "width": 1.35,
        "color": PLANET_COLORS.get(planet_key, "#64748b"),
        "dash": "solid",
    }


def display_planet_label(planet: str) -> str:
    planet_key = normalize_body_name(planet)
    if planet_key == AVG_ALL_LABEL:
        return "AVG(ALL) 10-planet basket"
    return planet_key


def collect_identities(
    touches: pd.DataFrame,
    max_lines: int,
    excluded_planets: set[str] | None = None,
) -> list[tuple[str, str, float, float, int]]:
    identities: list[tuple[str, str, float, float, int]] = []
    excluded = {normalize_body_name(p) for p in (excluded_planets or set())}
    limit = None if int(max_lines or 0) <= 0 else int(max_lines)
    for _, row in touches.sort_values(["edge_score", "touch_time_local"], ascending=[False, False]).iterrows():
        for which in (1, 2):
            ident = identity_from_columns(row, which)
            if ident is None:
                continue
            if normalize_body_name(ident[0]) in excluded:
                continue
            if ident not in identities:
                identities.append(ident)
            if limit is not None and len(identities) >= limit:
                return identities
    return identities


def filter_touches_to_rendered_identities(
    touches: pd.DataFrame,
    identities: list[tuple[str, str, float, float, int]],
    excluded_planets: set[str] | None = None,
) -> pd.DataFrame:
    if touches.empty or not identities:
        return touches.copy()

    identity_set = set(identities)
    excluded = {normalize_body_name(p) for p in (excluded_planets or set())}

    def row_supported(row: pd.Series) -> bool:
        row_identities = [identity_from_columns(row, which) for which in (1, 2)]
        row_identities = [ident for ident in row_identities if ident is not None]
        if not row_identities:
            return False
        if any(normalize_body_name(ident[0]) in excluded for ident in row_identities):
            return False
        return all(ident in identity_set for ident in row_identities)

    return touches[touches.apply(row_supported, axis=1)].copy()


def build_detail_figure(
    price: pd.DataFrame,
    touches: pd.DataFrame,
    line_limit: int = 60,
    selected_touch_id: str | None = None,
    timeframe: str = "hourly",
) -> tuple[go.Figure, pd.DataFrame]:
    window_end = price.index.max()
    window_start = window_end - pd.Timedelta(days=DEFAULT_DETAIL_DAYS)
    visible = touches.copy()
    if selected_touch_id:
        selected = touches[touches["touch_id"].astype(str) == str(selected_touch_id)].copy()
        if not selected.empty:
            anchor = selected.iloc[0]
            half = pd.Timedelta(days=DEFAULT_DETAIL_DAYS / 2)
            center = pd.Timestamp(anchor["touch_time_local"])
            window_start = center - half
            window_end = center + half

    visible = visible[
        (visible["after72_time_local"] >= window_start) & (visible["touch_time_local"] <= window_end)
    ].copy()
    visible = visible.sort_values(["touch_time_local", "edge_score"], ascending=[True, False]).reset_index(drop=True)
    visible_all = visible.copy()
    price_window = price[(price.index >= window_start) & (price.index <= window_end)].copy()
    if price_window.empty:
        price_window = price.tail(max(5000, line_limit * 200)).copy()

    p_min = float(price_window["low"].min())
    p_max = float(price_window["high"].max())
    pad = (p_max - p_min) * 0.09 if p_max > p_min else 0.5
    y0 = p_min - pad
    y1 = p_max + pad

    fig = go.Figure()
    aspect_window_cols = [
        "event_id",
        "pair_key",
        "aspect",
        "event_window_start_local",
        "event_window_end_local",
    ]
    for extra_col in (
        "aspect_system",
        "aspect_label",
        "event_duration_minutes",
        "event_orb_deg",
        "event_orb_limit_deg",
        "event_bphs_strength",
        "event_bphs_virupa",
        "aspect_family",
        "duration_bucket",
        "active_hard_aspect_count",
        "active_soft_aspect_count",
        "jyotish_hypothesis_direction",
        "jyotish_bullish_score",
        "jyotish_bearish_score",
        "jyotish_net_score",
        "jyotish_conflict_score",
        "jyotish_scored_hit_count",
        "dominant_aspect_id",
        "dominant_aspect_signed_score",
        "dominant_aspect_abs_score",
        "doctrine_hypothesis_direction",
        "doctrine_bullish_score",
        "doctrine_bearish_score",
        "doctrine_net_score",
        "doctrine_conflict_score",
        "doctrine_dignity_virupa_avg",
        "doctrine_dominant_aspect_id",
        "doctrine_dominant_aspect_signed_score",
        "doctrine_dominant_aspect_abs_score",
        "doctrine_dominant_dignity",
        "fx_hypothesis_direction",
        "fx_base_reference_label",
        "fx_quote_reference_label",
        "fx_base_net_score",
        "fx_quote_net_score",
        "fx_pair_net_score",
        "fx_pair_conflict_score",
        "fx_pair_conflict_ratio",
        "fx_dominant_base_hit",
        "fx_dominant_quote_hit",
        "fx_rule_layer_total_strength",
        "fx_doctrine_hypothesis_direction",
        "fx_doctrine_base_net_score",
        "fx_doctrine_quote_net_score",
        "fx_doctrine_pair_net_score",
        "fx_doctrine_pair_conflict_score",
        "fx_doctrine_pair_conflict_ratio",
        "fx_doctrine_base_dignity_virupa_avg",
        "fx_doctrine_quote_dignity_virupa_avg",
        "fx_doctrine_dominant_base_hit",
        "fx_doctrine_dominant_quote_hit",
        "fx_doctrine_dominant_base_dignity",
        "fx_doctrine_dominant_quote_dignity",
        "fx_doctrine_rule_layer_total_strength",
        "rule_layer_total_strength",
        "rule_layer_conflict_ratio",
        "reference_time_ist",
        "source_reference_time",
        "source_reference_tz",
        "base_reference_label",
        "quote_reference_label",
        "base_tn_reference_dt_local",
        "base_tn_reference_dt_source",
        "base_tn_reference_source_tz",
    ):
        if extra_col in visible.columns:
            aspect_window_cols.append(extra_col)
    aspect_windows = (
        visible_all[aspect_window_cols]
        .drop_duplicates()
        .sort_values(["event_window_start_local", "aspect"])
        .reset_index(drop=True)
    )
    for _, row in aspect_windows.iterrows():
        fig.add_trace(build_aspect_window_polygon(row, y0, y1))
    regime_zones = build_regime_zones(aspect_windows)
    for _, row in regime_zones.iterrows():
        fig.add_trace(build_regime_zone_polygon(row, y0, y1))

    fig.add_trace(
        go.Candlestick(
            x=price_window.index,
            open=price_window["open"],
            high=price_window["high"],
            low=price_window["low"],
            close=price_window["close"],
            name=timeframe_candle_label(timeframe),
            increasing_line_color=CANDLE_UP_LINE,
            increasing_fillcolor=CANDLE_UP_FILL,
            decreasing_line_color=CANDLE_DOWN_LINE,
            decreasing_fillcolor=CANDLE_DOWN_FILL,
        )
    )

    # Draw planetary SR lines based on touched identities
    excluded_line_planets = {"MOON"} if timeframe == "daily" else set()
    identities = collect_identities(visible_all, max_lines=line_limit, excluded_planets=excluded_line_planets)
    visible = filter_touches_to_rendered_identities(visible_all, identities, excluded_planets=excluded_line_planets)
    if identities:
        needed_planets = tuple(sorted({identity[0] for identity in identities}))
        lon_map = build_adaptive_longitude_map(
            planets=needed_planets,
            full_timestamps=price_window.index,
            fetch_fn=fetch_planetary_longitude_or_avg,
            astrology_method="sidereal",
            coordinate_system="geo",
        )
        for planet, mode, harmonic, n_value, degree in identities:
            if planet not in lon_map:
                continue
            lon_series = lon_map[planet].reindex(price_window.index)
            line_series = line_from_identity(lon_series, (planet, mode, harmonic, n_value, degree))
            planet_label = display_planet_label(planet)
            line_name = f"{planet_label} {mode} h={harmonic:g} n={n_value:g} d={int(degree)}"
            fig.add_trace(
                go.Scattergl(
                    x=price_window.index,
                    y=line_series.values,
                    mode="lines",
                    line=line_style_for_planet(planet),
                    name=line_name,
                    hovertemplate=f"{line_name}<br>Time: %{{x}}<br>Value: %{{y:.3f}}<extra></extra>",
                    showlegend=False,
                )
            )

    for _, row in aspect_windows.iterrows():
        fig.add_trace(build_aspect_window_hitbox_polygon(row, y0, y1))
    for _, row in regime_zones.iterrows():
        fig.add_trace(build_regime_zone_hitbox_polygon(row, y0, y1))

    if not visible.empty:
        marker_customdata = [
            event_selection_customdata(
                row,
                build_event_detail_html(row),
                "event_window_start_local",
                "event_window_end_local",
                str(row.get("touch_event_label", "")).strip() or str(row.get("zone_label", "")).strip(),
                "touch_marker",
                str(row.get("touch_id", "")).strip(),
            )
            for _, row in visible.iterrows()
        ]
        fig.add_trace(
            go.Scattergl(
                x=visible["touch_time_local"],
                y=visible["touch_price"],
                mode="markers",
                name="Interactions",
                customdata=marker_customdata,
                marker=dict(
                    size=7,
                    color=[MARKER_COLORS.get(v, "#94a3b8") for v in visible["zone_kind"]],
                    symbol=[MARKER_SYMBOLS.get(v, "circle") for v in visible["zone_kind"]],
                    line=dict(color="rgba(255,255,255,0.55)", width=0.7),
                    opacity=0.9,
                ),
                text=visible["hover_text"],
                hovertemplate="%{text}<extra></extra>",
                showlegend=False,
            )
        )

    # Highlight one selected interaction if asked
    if selected_touch_id:
        sel = visible[visible["touch_id"].astype(str) == str(selected_touch_id)]
        if not sel.empty:
            row = sel.iloc[0]
            fig.add_trace(
                go.Scatter(
                    x=[row["touch_time_local"]],
                    y=[row["touch_price"]],
                    mode="markers+text",
                    marker=dict(size=13, color="#111827", symbol="star"),
                    text=[row["zone_label"]],
                    textposition="top center",
                    customdata=[
                        event_selection_customdata(
                            row,
                            build_event_detail_html(row),
                            "event_window_start_local",
                            "event_window_end_local",
                            str(row.get("touch_event_label", "")).strip() or str(row.get("zone_label", "")).strip(),
                            "selected_marker",
                            str(row.get("touch_id", "")).strip(),
                        )
                    ],
                    hovertemplate=row["hover_text"] + "<extra></extra>",
                    showlegend=False,
                )
            )

    fig.update_layout(
        template="plotly_dark",
        height=940,
        margin=dict(l=45, r=25, t=70, b=40),
        xaxis_rangeslider_visible=False,
        paper_bgcolor=APP_BG,
        plot_bgcolor=PANEL_BG,
        hoverlabel=dict(bgcolor="rgba(11, 6, 81, 0.88)", font_size=11, bordercolor="rgba(255,255,255,0.35)"),
        showlegend=False,
        title=(
            f"Visible window (IST): {window_start.strftime('%Y-%m-%d %H:%M')} to {window_end.strftime('%Y-%m-%d %H:%M')} | "
            f"timeframe={timeframe} | interactions={len(visible)} | aspect_windows={len(aspect_windows)} | regime_zones={len(regime_zones)} | mode=visible_touched"
        ),
        uirevision="touch-detail",
    )
    fig.update_yaxes(range=[y0, y1], showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    return fig, visible


def load_token_and_chat(text: str) -> tuple[str | None, str | None]:
    token_match = re.search(r"\bbot_token\s*=\s*['\"]([^'\"]+)['\"]", text)
    chat_match = re.search(r"\bchat_id\s*=\s*['\"]?([0-9]+)['\"]?", text)
    return (token_match.group(1).strip() if token_match else None, chat_match.group(1).strip() if chat_match else None)


def telegram_credentials(args: argparse.Namespace) -> tuple[str | None, str | None]:
    token = (args.telegram_token or "").strip() or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = (args.telegram_chat_id or "").strip() or os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if token and chat_id:
        return token, chat_id
    legacy = Path(args.telegram_legacy_file)
    if legacy.exists():
        try:
            t, c = load_token_and_chat(legacy.read_text(encoding="utf-8", errors="ignore"))
            token = token or (t or "").strip()
            chat_id = chat_id or (c or "").strip()
        except Exception:
            pass
    return (token or None, chat_id or None)


def send_telegram_document(token: str, chat_id: str, file_path: Path, caption: str) -> None:
    if not requests:
        raise RuntimeError("requests is not available.")
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(file_path, "rb") as fh:
        files = {"document": (file_path.name, fh, "text/html")}
        payload = {"chat_id": str(chat_id), "caption": caption}
        resp = requests.post(url, data=payload, files=files, timeout=120)
    if not resp.ok:
        raise RuntimeError(f"Telegram upload failed ({resp.status_code}): {resp.text}")
    data = resp.json()
    if not isinstance(data, dict) or not data.get("ok", False):
        raise RuntimeError(f"Telegram API error: {data}")


def build_user_facing_export_frame(visible: pd.DataFrame) -> pd.DataFrame:
    export_df = visible.copy()
    utc_cols = [col for col in export_df.columns if str(col).lower().endswith("_utc")]
    if utc_cols:
        export_df = export_df.drop(columns=utc_cols, errors="ignore")
    rename_map = {}
    if "tn_reference_dt_local" in export_df.columns:
        rename_map["tn_reference_dt_local"] = "reference_time_ist"
    if "tn_reference_tz" in export_df.columns:
        rename_map["tn_reference_tz"] = "reference_time_tz"
    if "tn_reference_dt_source" in export_df.columns:
        rename_map["tn_reference_dt_source"] = "source_reference_time"
    if "tn_reference_source_tz" in export_df.columns:
        rename_map["tn_reference_source_tz"] = "source_reference_tz"
    if "base_tn_reference_dt_local" in export_df.columns:
        rename_map["base_tn_reference_dt_local"] = "base_reference_time_ist"
    if "base_tn_reference_tz" in export_df.columns:
        rename_map["base_tn_reference_tz"] = "base_reference_time_tz"
    if "base_tn_reference_dt_source" in export_df.columns:
        rename_map["base_tn_reference_dt_source"] = "base_source_reference_time"
    if "base_tn_reference_source_tz" in export_df.columns:
        rename_map["base_tn_reference_source_tz"] = "base_source_reference_tz"
    if rename_map:
        export_df = export_df.rename(columns=rename_map)
    return export_df


def build_full_year_timeframe_figure(
    price: pd.DataFrame,
    touches: pd.DataFrame,
    max_lines: int,
    timeframe: str,
    hourly_max_aspect_hours: float,
    daily_min_aspect_hours: float,
) -> tuple[go.Figure, pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    chart_price = resample_price_for_timeframe(price, timeframe)
    end = chart_price.index.max()
    start = end - pd.Timedelta(days=365)
    visible = apply_filters(touches, ["bullish", "bearish"], ["confluence", "nearest_line"], ALL_FILTER_VALUE, ALL_FILTER_VALUE)
    visible = filter_touches_for_timeframe(
        visible,
        timeframe=timeframe,
        hourly_max_aspect_hours=hourly_max_aspect_hours,
        daily_min_aspect_hours=daily_min_aspect_hours,
    )
    visible = visible[(visible["after72_time_local"] >= pd.Timestamp(start)) & (visible["touch_time_local"] <= pd.Timestamp(end))].copy()
    fig, visible = build_detail_figure(
        price=chart_price[(chart_price.index >= start) & (chart_price.index <= end)].copy(),
        touches=visible,
        line_limit=int(max_lines or 0),
        timeframe=timeframe,
    )
    return fig, visible, start, end


def export_full_year_chart(
    price: pd.DataFrame,
    touches: pd.DataFrame,
    output_dir: str | Path,
    max_lines: int = 60,
    timeframe: str = "hourly",
    hourly_max_aspect_hours: float = 24.0,
    daily_min_aspect_hours: float = 24.0,
) -> tuple[Path, Path, pd.DataFrame]:
    fig, visible, _, _ = build_full_year_timeframe_figure(
        price=price,
        touches=touches,
        max_lines=max_lines,
        timeframe=timeframe,
        hourly_max_aspect_hours=hourly_max_aspect_hours,
        daily_min_aspect_hours=daily_min_aspect_hours,
    )

    export_root = Path(output_dir)
    export_root.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp.now(tz=IST).strftime("%Y%m%d_%H%M%S")
    html_path = export_root / f"sr_touch_full_1year_{timeframe}_{stamp}.html"
    csv_path = export_root / f"sr_touch_full_1year_{timeframe}_{stamp}.csv"
    fig.update_layout(height=980)
    fig.write_html(
        str(html_path),
        include_plotlyjs=True,
        post_script=DETAIL_PANEL_POST_SCRIPT,
        config=PLOTLY_CHART_CONFIG,
    )
    build_user_facing_export_frame(visible).to_csv(csv_path, index=False)
    return html_path, csv_path, visible


def export_switchable_timeframe_chart(
    price: pd.DataFrame,
    touches: pd.DataFrame,
    output_dir: str | Path,
    max_lines: int = 60,
    hourly_max_aspect_hours: float = 24.0,
    daily_min_aspect_hours: float = 24.0,
) -> tuple[Path, Path, pd.DataFrame]:
    combined = go.Figure()
    groups: list[dict[str, Any]] = []
    visible_frames: list[pd.DataFrame] = []
    trace_start = 0
    interval_minutes = infer_price_interval_minutes(price)
    timeframes = ["hourly", "daily"]
    if interval_minutes is not None and interval_minutes <= 30.0:
        timeframes.insert(0, "m30")

    for timeframe in timeframes:
        fig, visible, start, end = build_full_year_timeframe_figure(
            price=price,
            touches=touches,
            max_lines=max_lines,
            timeframe=timeframe,
            hourly_max_aspect_hours=hourly_max_aspect_hours,
            daily_min_aspect_hours=daily_min_aspect_hours,
        )
        if not groups:
            combined.update_layout(fig.layout)

        is_default = timeframe == timeframes[0]
        for trace in fig.data:
            trace.visible = is_default
            combined.add_trace(trace)

        frame = visible.copy()
        frame.insert(0, "chart_timeframe", timeframe)
        visible_frames.append(frame)

        groups.append(
            {
                "timeframe": timeframe,
                "start": trace_start,
                "stop": trace_start + len(fig.data),
                "title": fig.layout.title.text if fig.layout.title else "",
                "yaxis_range": list(fig.layout.yaxis.range) if fig.layout.yaxis.range else None,
                "xaxis_range": [start.isoformat(), end.isoformat()],
                "rows": len(visible),
            }
        )
        trace_start += len(fig.data)

    buttons = []
    total_traces = len(combined.data)
    for group in groups:
        mask = [False] * total_traces
        for idx in range(int(group["start"]), int(group["stop"])):
            mask[idx] = True
        relayout = {
            "title.text": group["title"],
            "xaxis.range": group["xaxis_range"],
        }
        if group["yaxis_range"] is not None:
            relayout["yaxis.range"] = group["yaxis_range"]
        buttons.append(
            {
                "label": f"{str(group['timeframe']).upper()} ({group['rows']})",
                "method": "update",
                "args": [{"visible": mask}, relayout],
            }
        )

    combined.update_layout(
        height=980,
        updatemenus=[
            {
                "type": "buttons",
                "direction": "right",
                "x": 0.01,
                "xanchor": "left",
                "y": 1.08,
                "yanchor": "top",
                "buttons": buttons,
                "bgcolor": "rgba(15,23,42,0.95)",
                "bordercolor": "rgba(148,163,184,0.6)",
                "borderwidth": 1,
                "font": {"color": "#e5e7eb", "size": 12},
                "pad": {"r": 8, "t": 4, "b": 4, "l": 8},
            }
        ],
    )

    export_root = Path(output_dir)
    export_root.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp.now(tz=IST).strftime("%Y%m%d_%H%M%S")
    html_path = export_root / f"sr_touch_full_1year_switch_{stamp}.html"
    csv_path = export_root / f"sr_touch_full_1year_switch_{stamp}.csv"
    combined.write_html(
        str(html_path),
        include_plotlyjs=True,
        post_script=DETAIL_PANEL_POST_SCRIPT,
        config=PLOTLY_CHART_CONFIG,
    )
    all_visible = pd.concat(visible_frames, ignore_index=True) if visible_frames else pd.DataFrame()
    build_user_facing_export_frame(all_visible).to_csv(csv_path, index=False)
    return html_path, csv_path, all_visible


def load_clustered_touch_log(path: str) -> pd.DataFrame:
    source_path = Path(path)
    cache_path = source_path.with_name(f"{source_path.stem}_clustered_v11.parquet")
    if cache_path.exists() and cache_path.stat().st_mtime >= source_path.stat().st_mtime:
        return pd.read_parquet(cache_path)

    raw = load_touch_log(path)
    clustered = cluster_touch_rows(raw)
    clustered.to_parquet(cache_path, index=False)
    return clustered


def main() -> None:
    args = parse_args()
    price = load_price(args.price)
    touches = load_clustered_touch_log(args.touch_log)
    if touches.empty:
        raise RuntimeError("Touch log is empty.")
    cfg = parse_sr_config(touches["sr_config_json"].iloc[0]) if "sr_config_json" in touches.columns and not touches["sr_config_json"].dropna().empty else parse_sr_config(None)
    _ = cfg
    if args.export_full_year:
        if args.timeframe == "switch":
            html_path, csv_path, visible = export_switchable_timeframe_chart(
                price=price,
                touches=touches,
                output_dir=args.export_dir,
                max_lines=int(args.export_max_lines or 0),
                hourly_max_aspect_hours=float(args.hourly_max_aspect_hours),
                daily_min_aspect_hours=float(args.daily_min_aspect_hours),
            )
        else:
            html_path, csv_path, visible = export_full_year_chart(
                price=price,
                touches=touches,
                output_dir=args.export_dir,
                max_lines=int(args.export_max_lines or 0),
                timeframe=args.timeframe,
                hourly_max_aspect_hours=float(args.hourly_max_aspect_hours),
                daily_min_aspect_hours=float(args.daily_min_aspect_hours),
            )
        print(f"Exported HTML: {html_path}")
        print(f"Exported CSV: {csv_path}")
        print(f"Visible rows in export window: {len(visible)}")
        if args.send_to_telegram:
            token, chat_id = telegram_credentials(args)
            if not token or not chat_id:
                raise RuntimeError("Telegram token/chat id not configured.")
            caption = f"USDJPY 1-year SR touch chart {args.timeframe} IST ({pd.Timestamp.now(tz=IST).strftime('%Y-%m-%d %H:%M:%S')})"
            send_telegram_document(token, chat_id, html_path, caption=caption)
            print("Telegram upload complete.")
        return
    raise RuntimeError("Dashboard mode removed in this utility. Use --export-full-year for static output.")


if __name__ == "__main__":
    main()
