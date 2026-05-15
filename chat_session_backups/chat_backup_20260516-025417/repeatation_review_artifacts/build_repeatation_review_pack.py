from __future__ import annotations

import argparse
import html
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
        str(args.price),
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
    visible_rows = 0
    if csv_path.exists():
        try:
            visible_rows = len(pd.read_csv(csv_path, low_memory=False))
        except Exception:
            visible_rows = 0
    return html_path, csv_path, visible_rows


def price_timeframe_for_case(case: dict[str, Any]) -> str:
    class Rowish:
        def __getitem__(self, key: str) -> Any:
            return case.get(key)

    return suggested_price_timeframe(Rowish())


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
      Use each chart link to place your mental/manual start-stop markers. Then copy the trade command,
      replace <code>&lt;marker_start_ist&gt;</code>, <code>&lt;marker_end_ist&gt;</code>, outcome, and note text.
      The existing annotation command auto-calculates entry, exit, pips, MFE, and MAE from the selected price timeframe.
      Ignore regions and rule notes can be added separately; these become the ML learning notes for the repeatation family.
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
