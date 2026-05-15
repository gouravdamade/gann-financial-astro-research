from __future__ import annotations

import argparse
import html
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from aspect_annotation_store import (
    DEFAULT_PRICE_PATHS,
    calculate_trade_prices,
    load_price_frame,
    suggested_price_timeframe,
)


DEFAULT_DB = Path(r"C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite")
DEFAULT_TOUCH_LOG = Path(
    r"C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv"
)
DEFAULT_PRICE = Path(r"C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet")
DEFAULT_REVIEW_FOCUS = Path(r"C:\Users\ADMIN\PycharmProjects\manual_case_review_focus_transitsign_20260516_0145.csv")
DEFAULT_EXPORT_ROOT = Path(r"C:\Users\ADMIN\Desktop\doc")
_PRICE_COVERAGE_CACHE: dict[Path, tuple[pd.Timestamp, pd.Timestamp] | None] = {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export one repeatation/recurrent aspect family as a review pack: "
            "real chart snapshots, marker templates, full-window pips, and an index page."
        )
    )
    parser.add_argument("--case-id", type=int, required=True, help="Seed case_id whose same pair/aspect group should be exported.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--touch-log", type=Path, default=DEFAULT_TOUCH_LOG)
    parser.add_argument("--price", type=Path, default=DEFAULT_PRICE)
    parser.add_argument("--review-focus", type=Path, default=DEFAULT_REVIEW_FOCUS)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--export-max-lines", type=int, default=60)
    parser.add_argument("--case-context-hours", type=float, default=72.0)
    parser.add_argument("--skip-chart-export", action="store_true", help="Only rebuild the index/template from existing chart files.")
    return parser.parse_args()


def h(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def slugify(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return text or "repeatation"


def command_quote(value: Any) -> str:
    return '"' + str(value).replace('"', '\\"') + '"'


def read_case_group(db_path: Path, case_id: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        seed = conn.execute(
            """
            SELECT case_id, source_event_id, pair_key, aspect, aspect_label,
                   window_start_ist, window_end_ist, timeframe, source_csv
            FROM aspect_cases
            WHERE case_id = ?
            """,
            (int(case_id),),
        ).fetchone()
        if seed is None:
            raise SystemExit(f"No aspect case found for case_id={case_id}.")
        rows = conn.execute(
            """
            SELECT case_id, source_event_id, pair_key, aspect, aspect_label,
                   window_start_ist, window_end_ist, timeframe, source_csv
            FROM aspect_cases
            WHERE pair_key = ?
              AND aspect = ?
            ORDER BY window_start_ist, case_id
            """,
            (seed["pair_key"], seed["aspect"]),
        ).fetchall()
    return dict(seed), [dict(row) for row in rows]


def load_focus_rows(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    df = pd.read_csv(path, low_memory=False)
    if "case_id" not in df.columns:
        return {}
    return {int(row["case_id"]): dict(row) for _, row in df.iterrows()}


def chart_command(args: argparse.Namespace, case_id: int, output_dir: Path) -> list[str]:
    return [
        sys.executable,
        str(Path(__file__).resolve().with_name("sr_touch_lazy_dashboard.py")),
        "--touch-log",
        str(args.touch_log),
        "--price",
        str(chart_price_path(args, case_id)),
        "--export-case-chart",
        "--case-id",
        str(case_id),
        "--case-timeframe",
        "auto",
        "--export-dir",
        str(output_dir),
        "--export-max-lines",
        str(int(args.export_max_lines)),
        "--case-context-hours",
        str(float(args.case_context_hours)),
    ]


def export_chart(args: argparse.Namespace, case: dict[str, Any], output_dir: Path) -> tuple[Path, Path, int]:
    html_path = output_dir / f"aspect_review_case_{int(case['case_id'])}_chart.html"
    csv_path = output_dir / f"aspect_review_case_{int(case['case_id'])}_chart_visible.csv"
    if not args.skip_chart_export or not html_path.exists() or not csv_path.exists():
        subprocess.run(chart_command(args, int(case["case_id"]), output_dir), cwd=Path(__file__).resolve().parent, check=True)
    inject_marker_ui(html_path, case)
    visible_rows = 0
    if csv_path.exists():
        try:
            visible_rows = len(pd.read_csv(csv_path, low_memory=False))
        except Exception:
            visible_rows = 0
    return html_path, csv_path, visible_rows


def marker_ui_script(case: dict[str, Any]) -> str:
    case_id = int(case["case_id"])
    timeframe = price_timeframe_for_case(case)
    window_start = str(case["window_start_ist"])
    window_end = str(case["window_end_ist"])
    pair_key = str(case["pair_key"])
    aspect = str(case["aspect"])
    metadata = {
        "caseId": case_id,
        "priceTimeframe": timeframe,
        "windowStart": window_start,
        "windowEnd": window_end,
        "pairKey": pair_key,
        "aspect": aspect,
    }
    metadata_json = json.dumps(metadata)
    return f"""
<script id="repeatation-marker-ui-script">
(function () {{
  var meta = {metadata_json};
  if (window.__repeatationMarkerUiAttached) return;
  window.__repeatationMarkerUiAttached = true;
  function ready(fn) {{
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }}
  ready(function () {{
    var gd = document.querySelector('.js-plotly-plot');
    if (!gd || !window.Plotly) return;
    var state = {{
      tool: 'trade_start',
      tradeStart: null,
      tradeEnd: null,
      ignoreStart: null,
      ignoreEnd: null,
      lastPoint: null
    }};
    function esc(value) {{
      return String(value == null ? '' : value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}
    function shellQuote(value) {{
      return '"' + String(value == null ? '' : value).replace(/"/g, '\\\\\\"') + '"';
    }}
    function pad(n) {{ return String(n).padStart(2, '0'); }}
    function toIST(value) {{
      if (!value) return '';
      var raw = String(value);
      if (/\\d{{4}}-\\d{{2}}-\\d{{2}}[ T]\\d{{2}}:\\d{{2}}/.test(raw) && raw.indexOf('+05:30') !== -1) {{
        return raw.replace('T', ' ').replace(/\\.\\d+/, '').slice(0, 19) + '+05:30';
      }}
      var d = new Date(value);
      if (isNaN(d.getTime()) && typeof value === 'number') d = new Date(value);
      if (isNaN(d.getTime())) return raw;
      var parts = new Intl.DateTimeFormat('en-GB', {{
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }}).formatToParts(d).reduce(function (acc, part) {{
        acc[part.type] = part.value;
        return acc;
      }}, {{}});
      return parts.year + '-' + parts.month + '-' + parts.day + ' ' + parts.hour + ':' + parts.minute + ':' + parts.second + '+05:30';
    }}
    function fmtPoint(point) {{
      if (!point) return 'not set';
      var price = Number(point.y);
      return toIST(point.x) + (Number.isFinite(price) ? ' @ ' + price.toFixed(3) : '');
    }}
    function pointFromPlotly(eventData) {{
      if (!eventData || !eventData.points || !eventData.points.length) return null;
      var p = eventData.points[0];
      var y = p.y;
      if (y == null && p.close != null) y = p.close;
      if (y == null && p.high != null && p.low != null) y = (Number(p.high) + Number(p.low)) / 2;
      return {{ x: p.x, y: y, source: 'plotly_click' }};
    }}
    function axisValue(axis, pixel) {{
      if (!axis) return null;
      if (typeof axis.p2d === 'function') return axis.p2d(pixel);
      if (typeof axis.p2c === 'function') return axis.p2c(pixel);
      return null;
    }}
    function pointFromMouse(evt) {{
      if (!gd._fullLayout || !gd._fullLayout.xaxis || !gd._fullLayout.yaxis) return null;
      var xa = gd._fullLayout.xaxis;
      var ya = gd._fullLayout.yaxis;
      var rect = gd.getBoundingClientRect();
      var plotX = evt.clientX - rect.left - xa._offset;
      var plotY = evt.clientY - rect.top - ya._offset;
      if (plotX < 0 || plotX > xa._length || plotY < 0 || plotY > ya._length) return null;
      return {{ x: axisValue(xa, plotX), y: axisValue(ya, plotY), source: 'chart_click' }};
    }}
    function sortPoints(a, b) {{
      if (!a || !b) return [a, b];
      return Date.parse(a.x) <= Date.parse(b.x) ? [a, b] : [b, a];
    }}
    function setTool(tool) {{
      state.tool = tool;
      panel.querySelectorAll('[data-tool]').forEach(function (button) {{
        button.classList.toggle('active', button.getAttribute('data-tool') === tool);
      }});
    }}
    function place(point) {{
      if (!point || !point.x) return;
      point.placedAt = Date.now();
      state.lastPoint = point;
      if (state.tool === 'trade_start') state.tradeStart = point;
      if (state.tool === 'trade_end') state.tradeEnd = point;
      if (state.tool === 'ignore_start') state.ignoreStart = point;
      if (state.tool === 'ignore_end') state.ignoreEnd = point;
      drawMarkers();
      render();
    }}
    function markerShapes() {{
      var shapes = (gd.layout && Array.isArray(gd.layout.shapes) ? gd.layout.shapes : [])
        .filter(function (shape) {{ return !(shape && String(shape.name || '').indexOf('repeatation-marker') === 0); }});
      function axisRange(axisName) {{
        var axis = gd._fullLayout && gd._fullLayout[axisName];
        return axis && Array.isArray(axis.range) ? axis.range : null;
      }}
      function xAround(x, fraction) {{
        var range = axisRange('xaxis') || [meta.windowStart, meta.windowEnd];
        var start = Date.parse(range[0]);
        var end = Date.parse(range[1]);
        var center = Date.parse(x);
        if (!Number.isFinite(start) || !Number.isFinite(end) || !Number.isFinite(center) || start === end) return [x, x];
        var half = Math.abs(end - start) * (fraction || 0.006);
        return [new Date(center - half).toISOString(), new Date(center + half).toISOString()];
      }}
      function yAround(y, fraction) {{
        var range = axisRange('yaxis');
        var center = Number(y);
        if (!range || !Number.isFinite(center)) return [y, y];
        var start = Number(range[0]);
        var end = Number(range[1]);
        if (!Number.isFinite(start) || !Number.isFinite(end) || start === end) return [y, y];
        var half = Math.abs(end - start) * (fraction || 0.018);
        return [center - half, center + half];
      }}
      function crosshair(point, color, dash, name) {{
        if (!point) return;
        var xs = xAround(point.x, 0.006);
        var ys = yAround(point.y, 0.018);
        var line = {{ color: color, width: 2.5, dash: dash || 'solid' }};
        shapes.push({{
          type: 'line',
          name: name + '-v',
          xref: 'x',
          yref: 'y',
          x0: point.x,
          x1: point.x,
          y0: ys[0],
          y1: ys[1],
          line: line,
          layer: 'above'
        }});
        shapes.push({{
          type: 'line',
          name: name + '-h',
          xref: 'x',
          yref: 'y',
          x0: xs[0],
          x1: xs[1],
          y0: point.y,
          y1: point.y,
          line: line,
          layer: 'above'
        }});
        shapes.push({{
          type: 'circle',
          name: name + '-ring',
          xref: 'x',
          yref: 'y',
          x0: xs[0],
          x1: xs[1],
          y0: ys[0],
          y1: ys[1],
          fillcolor: 'rgba(0,0,0,0)',
          line: {{ color: color, width: 1.5, dash: dash || 'solid' }},
          layer: 'above'
        }});
      }}
      crosshair(state.tradeStart, '#22c55e', 'solid', 'repeatation-marker-trade-start');
      crosshair(state.tradeEnd, '#ef4444', 'solid', 'repeatation-marker-trade-end');
      crosshair(state.ignoreStart, '#f97316', 'dash', 'repeatation-marker-ignore-start');
      crosshair(state.ignoreEnd, '#f97316', 'dash', 'repeatation-marker-ignore-end');
      if (state.ignoreStart && state.ignoreEnd) {{
        var pair = sortPoints(state.ignoreStart, state.ignoreEnd);
        shapes.push({{
          type: 'rect',
          name: 'repeatation-marker-ignore-region',
          xref: 'x',
          yref: 'paper',
          x0: pair[0].x,
          x1: pair[1].x,
          y0: 0,
          y1: 1,
          fillcolor: 'rgba(249,115,22,0.12)',
          line: {{ color: 'rgba(249,115,22,0.9)', width: 2, dash: 'dash' }},
          layer: 'above'
        }});
      }}
      return shapes;
    }}
    function drawMarkers() {{
      Plotly.relayout(gd, {{ shapes: markerShapes() }});
    }}
    function noteText() {{
      return panel.querySelector('#repeatation-note').value.trim();
    }}
    function noteType() {{
      return panel.querySelector('#repeatation-note-type').value.trim() || 'general';
    }}
    function outcome() {{
      return panel.querySelector('#repeatation-outcome').value;
    }}
    function tradeCommand() {{
      if (!state.tradeStart || !state.tradeEnd) return '';
      var pair = sortPoints(state.tradeStart, state.tradeEnd);
      return 'python .\\\\aspect_annotation_store.py --add-trade-annotation'
        + ' --case-id ' + meta.caseId
        + ' --trade-start ' + shellQuote(toIST(pair[0].x))
        + ' --trade-end ' + shellQuote(toIST(pair[1].x))
        + ' --outcome-label ' + outcome()
        + ' --price-timeframe ' + meta.priceTimeframe
        + ' --why ' + shellQuote(noteText() || 'manual repeatation trade marker');
    }}
    function ignoreCommand() {{
      if (!state.ignoreStart || !state.ignoreEnd) return '';
      var pair = sortPoints(state.ignoreStart, state.ignoreEnd);
      return 'python .\\\\aspect_annotation_store.py --mark-ignore-region'
        + ' --case-id ' + meta.caseId
        + ' --region-start ' + shellQuote(toIST(pair[0].x))
        + ' --region-end ' + shellQuote(toIST(pair[1].x))
        + ' --why ' + shellQuote(noteText() || 'manual repeatation ignore marker');
    }}
    function ruleCommand() {{
      if (!noteText()) return '';
      return 'python .\\\\aspect_annotation_store.py --add-rule-note'
        + ' --case-id ' + meta.caseId
        + ' --note-type ' + shellQuote(noteType())
        + ' --note ' + shellQuote(noteText());
    }}
    function commandBlock(label, command) {{
      if (!command) return '<div class="muted">' + label + ': place required markers / note first</div>';
      return '<label>' + label + '</label><pre>' + esc(command) + '</pre><button data-copy="' + esc(command) + '">Copy ' + label + '</button>';
    }}
    function render() {{
      panel.querySelector('#repeatation-last').textContent = fmtPoint(state.lastPoint);
      panel.querySelector('#repeatation-trade-start').textContent = fmtPoint(state.tradeStart);
      panel.querySelector('#repeatation-trade-end').textContent = fmtPoint(state.tradeEnd);
      panel.querySelector('#repeatation-ignore-start').textContent = fmtPoint(state.ignoreStart);
      panel.querySelector('#repeatation-ignore-end').textContent = fmtPoint(state.ignoreEnd);
      panel.querySelector('#repeatation-commands').innerHTML =
        commandBlock('Trade', tradeCommand())
        + commandBlock('Ignore', ignoreCommand())
        + commandBlock('Rule note', ruleCommand());
      panel.querySelectorAll('[data-copy]').forEach(function (button) {{
        button.addEventListener('click', function () {{
          navigator.clipboard.writeText(button.getAttribute('data-copy') || '');
          button.textContent = 'Copied';
          setTimeout(function () {{ button.textContent = 'Copy'; }}, 1200);
        }});
      }});
    }}
    function clearMarkers() {{
      state.tradeStart = null;
      state.tradeEnd = null;
      state.ignoreStart = null;
      state.ignoreEnd = null;
      state.lastPoint = null;
      drawMarkers();
      render();
    }}
    function downloadMarkers() {{
      var payload = {{
        case_id: meta.caseId,
        pair_key: meta.pairKey,
        aspect: meta.aspect,
        trade_start_ist: state.tradeStart ? toIST(state.tradeStart.x) : '',
        trade_end_ist: state.tradeEnd ? toIST(state.tradeEnd.x) : '',
        ignore_start_ist: state.ignoreStart ? toIST(state.ignoreStart.x) : '',
        ignore_end_ist: state.ignoreEnd ? toIST(state.ignoreEnd.x) : '',
        outcome_label: outcome(),
        note_type: noteType(),
        note: noteText(),
        trade_command: tradeCommand(),
        ignore_command: ignoreCommand(),
        rule_note_command: ruleCommand()
      }};
      var blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'case_' + meta.caseId + '_repeatation_markers.json';
      a.click();
      URL.revokeObjectURL(url);
    }}
    var panel = document.createElement('aside');
    panel.id = 'repeatation-marker-panel';
    panel.className = 'collapsed';
    panel.innerHTML = ''
      + '<div class="rm-head"><div><div class="rm-title">Markers</div><div class="rm-mini">case ' + esc(meta.caseId) + '</div></div><button id="repeatation-toggle" type="button" title="Expand marker drawer">Open</button></div>'
      + '<div class="rm-body">'
      + '<div class="rm-sub">case_id=' + esc(meta.caseId) + ' | ' + esc(meta.pairKey) + ' ' + esc(meta.aspect) + '</div>'
      + '<div class="rm-sub">Window: ' + esc(meta.windowStart) + ' -> ' + esc(meta.windowEnd) + '</div>'
      + '<div class="rm-tools">'
      + '<button data-tool="trade_start">Trade start</button>'
      + '<button data-tool="trade_end">Trade end</button>'
      + '<button data-tool="ignore_start">Ignore start</button>'
      + '<button data-tool="ignore_end">Ignore end</button>'
      + '</div>'
      + '<div class="rm-grid"><span>Last click</span><b id="repeatation-last">not set</b><span>Trade start</span><b id="repeatation-trade-start">not set</b><span>Trade end</span><b id="repeatation-trade-end">not set</b><span>Ignore start</span><b id="repeatation-ignore-start">not set</b><span>Ignore end</span><b id="repeatation-ignore-end">not set</b></div>'
      + '<label>Outcome</label><select id="repeatation-outcome"><option value="bullish">bullish</option><option value="bearish">bearish</option><option value="sideways">sideways</option><option value="unclear">unclear</option></select>'
      + '<label>Note type</label><input id="repeatation-note-type" value="manual_repeatation_note">'
      + '<label>Notes / why</label><textarea id="repeatation-note" placeholder="Why this start/end or ignore marker?"></textarea>'
      + '<div class="rm-actions"><button id="repeatation-clear">Clear markers</button><button id="repeatation-download">Download JSON</button></div>'
      + '<div id="repeatation-commands"></div>'
      + '</div>';
    var style = document.createElement('style');
    style.textContent = ''
      + '#repeatation-marker-panel{{position:fixed;right:12px;top:14px;z-index:9999;width:min(360px,calc(100vw - 24px));max-height:88vh;overflow:auto;background:#0f172a;color:#e5e7eb;border:1px solid #475569;border-radius:8px;box-shadow:0 12px 34px rgba(0,0,0,.38);font:12px/1.35 Arial,sans-serif;padding:10px;transition:width .18s ease,opacity .18s ease;}}'
      + '#repeatation-marker-panel.collapsed{{width:132px;overflow:hidden;opacity:.92;}}'
      + '#repeatation-marker-panel .rm-head{{display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-title{{font-weight:700;font-size:14px;margin-bottom:1px;}}'
      + '#repeatation-marker-panel .rm-mini{{color:#93c5fd;font-size:11px;}}'
      + '#repeatation-marker-panel.collapsed .rm-body{{display:none;}}'
      + '#repeatation-marker-panel .rm-sub{{color:#cbd5e1;margin-bottom:6px;}}'
      + '#repeatation-marker-panel label{{display:block;margin:8px 0 3px;color:#bfdbfe;font-weight:600;}}'
      + '#repeatation-marker-panel button,#repeatation-marker-panel select,#repeatation-marker-panel input,#repeatation-marker-panel textarea{{font:12px Arial,sans-serif;border-radius:5px;border:1px solid #64748b;background:#111827;color:#e5e7eb;}}'
      + '#repeatation-marker-panel button{{padding:5px 8px;cursor:pointer;}}'
      + '#repeatation-marker-panel button.active{{background:#2563eb;border-color:#60a5fa;}}'
      + '#repeatation-marker-panel select,#repeatation-marker-panel input,#repeatation-marker-panel textarea{{width:100%;box-sizing:border-box;padding:6px;}}'
      + '#repeatation-marker-panel textarea{{height:64px;resize:vertical;}}'
      + '#repeatation-marker-panel pre{{white-space:pre-wrap;background:#020617;color:#dbeafe;border:1px solid #1e293b;border-radius:5px;padding:6px;margin:3px 0 5px;max-height:120px;overflow:auto;}}'
      + '#repeatation-marker-panel .rm-tools,#repeatation-marker-panel .rm-actions{{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0;}}'
      + '#repeatation-marker-panel .rm-grid{{display:grid;grid-template-columns:88px 1fr;gap:4px 8px;background:#111827;border:1px solid #1e293b;border-radius:6px;padding:8px;}}'
      + '#repeatation-marker-panel .rm-grid span{{color:#94a3b8;}}'
      + '#repeatation-marker-panel .muted{{color:#94a3b8;margin:6px 0;}}';
    document.head.appendChild(style);
    document.body.appendChild(panel);
    function setCollapsed(collapsed) {{
      panel.classList.toggle('collapsed', collapsed);
      var toggle = panel.querySelector('#repeatation-toggle');
      toggle.textContent = collapsed ? 'Open' : 'Hide';
      toggle.setAttribute('title', collapsed ? 'Expand marker drawer' : 'Collapse marker drawer');
    }}
    panel.querySelector('#repeatation-toggle').addEventListener('click', function () {{
      setCollapsed(!panel.classList.contains('collapsed'));
    }});
    panel.querySelectorAll('[data-tool]').forEach(function (button) {{
      button.addEventListener('click', function () {{ setTool(button.getAttribute('data-tool')); }});
    }});
    panel.querySelector('#repeatation-clear').addEventListener('click', clearMarkers);
    panel.querySelector('#repeatation-download').addEventListener('click', downloadMarkers);
    panel.querySelector('#repeatation-note').addEventListener('input', render);
    panel.querySelector('#repeatation-note-type').addEventListener('input', render);
    panel.querySelector('#repeatation-outcome').addEventListener('change', render);
    gd.on('plotly_click', function (eventData) {{
      place(pointFromPlotly(eventData));
    }});
    gd.addEventListener('click', function (evt) {{
      if (evt.target && panel.contains(evt.target)) return;
      if (state.lastPoint && Date.now() - (state.lastPoint.placedAt || 0) < 80) return;
      var point = pointFromMouse(evt);
      if (point) place(point);
    }});
    setTool('trade_start');
    render();
  }});
}}());
</script>
"""


def inject_marker_ui(html_path: Path, case: dict[str, Any]) -> None:
    if not html_path.exists():
        return
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    script = marker_ui_script(case)
    if "id=\"repeatation-marker-ui-script\"" in text:
        text = re.sub(
            r"\n?<script id=\"repeatation-marker-ui-script\">.*?</script>",
            lambda _match: "\n" + script,
            text,
            count=1,
            flags=re.DOTALL,
        )
        html_path.write_text(text, encoding="utf-8")
        return
    if "</body>" in text:
        text = text.replace("</body>", script + "\n</body>", 1)
    else:
        text += script
    html_path.write_text(text, encoding="utf-8")


def price_timeframe_for_case(case: dict[str, Any]) -> str:
    class Rowish:
        def __getitem__(self, key: str) -> Any:
            return case.get(key)

    suggested = suggested_price_timeframe(Rowish())
    start, end = case_bounds(case, context_hours=0.0)
    if price_covers(DEFAULT_PRICE_PATHS[suggested], start, end):
        return suggested
    if suggested != "h1" and price_covers(DEFAULT_PRICE_PATHS["h1"], start, end):
        return "h1"
    return suggested


def chart_price_path(args: argparse.Namespace, case_or_id: dict[str, Any] | int) -> Path:
    if Path(args.price) != DEFAULT_PRICE:
        return Path(args.price)
    case = case_or_id if isinstance(case_or_id, dict) else None
    if case is None:
        _, rows = read_case_group(args.db, int(case_or_id))
        case = next((row for row in rows if int(row["case_id"]) == int(case_or_id)), None)
    if not case:
        return DEFAULT_PRICE
    start, end = case_bounds(case, context_hours=float(args.case_context_hours))
    if price_covers(DEFAULT_PRICE, start, end):
        return DEFAULT_PRICE
    if price_covers(DEFAULT_PRICE_PATHS["h1"], start, end):
        return DEFAULT_PRICE_PATHS["h1"]
    return DEFAULT_PRICE


def case_bounds(case: dict[str, Any], context_hours: float) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = pd.Timestamp(str(case["window_start_ist"]))
    end = pd.Timestamp(str(case["window_end_ist"]))
    if start.tzinfo is None:
        start = start.tz_localize("Asia/Kolkata")
    else:
        start = start.tz_convert("Asia/Kolkata")
    if end.tzinfo is None:
        end = end.tz_localize("Asia/Kolkata")
    else:
        end = end.tz_convert("Asia/Kolkata")
    delta = pd.Timedelta(hours=float(context_hours or 0.0))
    return start - delta, end + delta


def price_coverage(path: Path) -> tuple[pd.Timestamp, pd.Timestamp] | None:
    path = Path(path)
    if path not in _PRICE_COVERAGE_CACHE:
        if not path.exists():
            _PRICE_COVERAGE_CACHE[path] = None
        else:
            price = pd.read_parquet(path, columns=[]).sort_index()
            if len(price.index) == 0:
                _PRICE_COVERAGE_CACHE[path] = None
            else:
                idx = price.index
                if idx.tz is None:
                    idx = idx.tz_localize("UTC")
                idx = idx.tz_convert("Asia/Kolkata")
                _PRICE_COVERAGE_CACHE[path] = (pd.Timestamp(idx.min()), pd.Timestamp(idx.max()))
    return _PRICE_COVERAGE_CACHE[path]


def price_covers(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> bool:
    coverage = price_coverage(path)
    if coverage is None:
        return False
    return coverage[0] <= start and coverage[1] >= end


def full_window_trade_stats(case: dict[str, Any]) -> dict[str, Any]:
    timeframe = price_timeframe_for_case(case)
    price = load_price_frame(DEFAULT_PRICE_PATHS[timeframe])
    bullish = calculate_trade_prices(
        price,
        trade_start_ist=str(case["window_start_ist"]),
        trade_end_ist=str(case["window_end_ist"]),
        outcome_label="bullish",
    )
    bearish = calculate_trade_prices(
        price,
        trade_start_ist=str(case["window_start_ist"]),
        trade_end_ist=str(case["window_end_ist"]),
        outcome_label="bearish",
    )
    return {
        "price_timeframe": timeframe,
        "full_window_entry_price": bullish["entry_price"],
        "full_window_exit_price": bullish["exit_price"],
        "full_window_bullish_pips": bullish["pips"],
        "full_window_bullish_mfe_pips": bullish["mfe_pips"],
        "full_window_bullish_mae_pips": bullish["mae_pips"],
        "full_window_bearish_pips": bearish["pips"],
        "full_window_bearish_mfe_pips": bearish["mfe_pips"],
        "full_window_bearish_mae_pips": bearish["mae_pips"],
        "full_window_direction": "bullish" if bullish["pips"] > 0 else "bearish" if bullish["pips"] < 0 else "flat",
    }


def annotation_command(case: dict[str, Any], outcome: str = "<bullish|bearish|sideways|unclear>") -> str:
    timeframe = price_timeframe_for_case(case)
    return (
        "python .\\aspect_annotation_store.py --add-trade-annotation "
        f"--case-id {int(case['case_id'])} "
        f"--trade-start {command_quote('<marker_start_ist>')} "
        f"--trade-end {command_quote('<marker_end_ist>')} "
        f"--outcome-label {outcome} "
        f"--price-timeframe {timeframe} "
        f"--why {command_quote('<why this marker placement>')}"
    )


def ignore_command(case: dict[str, Any]) -> str:
    return (
        "python .\\aspect_annotation_store.py --mark-ignore-region "
        f"--case-id {int(case['case_id'])} "
        f"--region-start {command_quote('<ignore_start_ist>')} "
        f"--region-end {command_quote('<ignore_end_ist>')} "
        f"--why {command_quote('<why ignored>')}"
    )


def rule_note_command(case: dict[str, Any]) -> str:
    return (
        "python .\\aspect_annotation_store.py --add-rule-note "
        f"--case-id {int(case['case_id'])} "
        "--note-type <note_type> "
        f"--note {command_quote('<rule note / ML learning note>')}"
    )


def render_index(seed: dict[str, Any], rows: list[dict[str, Any]], output_dir: Path) -> str:
    table_rows = []
    for row in rows:
        chart_name = Path(str(row.get("chart_html", ""))).name
        visible_name = Path(str(row.get("chart_visible_csv", ""))).name
        table_rows.append(
            f"""
            <tr>
              <td>{h(row['case_id'])}</td>
              <td>{h(row['window_start_ist'])}<br>{h(row['window_end_ist'])}</td>
              <td>{h(row.get('timeframe'))}</td>
              <td>{h(row.get('visible_rows'))}</td>
              <td>{h(row.get('full_window_direction'))}</td>
              <td>{h(row.get('full_window_bullish_pips'))}</td>
              <td>{h(row.get('full_window_bearish_pips'))}</td>
              <td>{h(row.get('group_script_direction_mode'))}</td>
              <td>{h(row.get('probable_factor_tags'))}</td>
              <td><a href="{h(chart_name)}">chart</a><br><a href="{h(visible_name)}">visible csv</a></td>
              <td><pre>{h(row.get('trade_command'))}</pre></td>
              <td><pre>{h(row.get('ignore_command'))}</pre></td>
              <td><pre>{h(row.get('rule_note_command'))}</pre></td>
            </tr>
            """
        )
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Repeatation Review Pack - case {h(seed['case_id'])}</title>
  <style>
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 18px 24px; background: #111827; color: #f8fafc; }}
    main {{ padding: 20px 24px 36px; }}
    table {{ border-collapse: collapse; width: 100%; background: white; font-size: 12px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; vertical-align: top; }}
    th {{ background: #e5e7eb; position: sticky; top: 0; z-index: 1; }}
    pre {{ margin: 0; white-space: pre-wrap; max-width: 360px; font-size: 11px; }}
    .meta {{ display: flex; gap: 18px; flex-wrap: wrap; margin-top: 8px; color: #d1d5db; }}
    .note {{ max-width: 1100px; line-height: 1.45; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <header>
    <h1>Repeatation Review Pack</h1>
    <div>{h(seed['pair_key'])} :: {h(seed['aspect'])}</div>
    <div class="meta">
      <span>seed case_id={h(seed['case_id'])}</span>
      <span>repeatations={len(rows)}</span>
      <span>folder={h(output_dir)}</span>
    </div>
  </header>
  <main>
    <p class="note">
      Open each chart link and expand the small <b>Markers</b> drawer. Choose trade start,
      trade end, ignore start, or ignore end, then click the chart to place a crosshair marker at the
      selected time/price. The chart overlays crosshair markers/ignore regions and generates Python
      commands for saving trade annotations, ignore regions, and rule notes. The annotation command
      auto-calculates entry, exit, pips, MFE, and MAE from the selected price timeframe.
    </p>
    <table>
      <thead>
        <tr>
          <th>Case</th><th>Window IST</th><th>TF</th><th>Visible Rows</th>
          <th>Full Window Direction</th><th>Bullish Pips</th><th>Bearish Pips</th>
          <th>Script Group Bias</th><th>Probable Factor Tags</th><th>Snapshot</th>
          <th>Trade Marker Command</th><th>Ignore Marker Command</th><th>Rule Note Command</th>
        </tr>
      </thead>
      <tbody>
        {''.join(table_rows)}
      </tbody>
    </table>
  </main>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    seed, cases = read_case_group(args.db, args.case_id)
    stamp = pd.Timestamp.now(tz="Asia/Kolkata").strftime("%Y%m%d_%H%M%S")
    group_slug = slugify(f"{seed['pair_key']}_{seed['aspect']}")
    output_dir = args.export_root / f"repeatation_review_case_{int(seed['case_id'])}_{group_slug}_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    focus_rows = load_focus_rows(args.review_focus)

    records: list[dict[str, Any]] = []
    for idx, case in enumerate(cases, start=1):
        print(f"[{idx}/{len(cases)}] exporting case_id={case['case_id']} {case['window_start_ist']}")
        html_path, csv_path, visible_rows = export_chart(args, case, output_dir)
        stats = full_window_trade_stats(case)
        focus = focus_rows.get(int(case["case_id"]), {})
        record = {
            **case,
            **stats,
            "visible_rows": visible_rows,
            "chart_html": str(html_path),
            "chart_visible_csv": str(csv_path),
            "trade_command": annotation_command(case),
            "ignore_command": ignore_command(case),
            "rule_note_command": rule_note_command(case),
            "same_aspect_group_key": focus.get("same_aspect_group_key", f"{seed['pair_key']} :: {seed['aspect']}"),
            "same_aspect_group_size": focus.get("same_aspect_group_size", len(cases)),
            "group_script_direction_mode": focus.get("group_script_direction_mode", ""),
            "group_fx_doctrine_directions": focus.get("group_fx_doctrine_directions", ""),
            "group_ml_outcomes": focus.get("group_ml_outcomes", ""),
            "probable_factor_tags": focus.get("probable_factor_tags", ""),
            "probable_factor_note": focus.get("probable_factor_note", ""),
        }
        records.append(record)

    marker_template = output_dir / "repeatation_marker_template.csv"
    pd.DataFrame(records).to_csv(marker_template, index=False)
    index_path = output_dir / "repeatation_review_index.html"
    index_path.write_text(render_index(seed, records, output_dir), encoding="utf-8")
    print(f"Wrote marker template: {marker_template}")
    print(f"Wrote index: {index_path}")
    print(f"repeatation_count={len(records)}")


if __name__ == "__main__":
    main()
