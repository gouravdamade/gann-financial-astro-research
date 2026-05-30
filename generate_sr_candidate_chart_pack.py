from __future__ import annotations

import argparse
import html
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PROJECT_DIR = Path(r"D:\Trading_Algo\New folder")
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from adaptive_ephemeris_engine import build_adaptive_longitude_map
from JDML4 import fetch_planetary_longitude, swe
from doctrine_config import configure_swiss_ephemeris_sidereal


IST = "Asia/Kolkata"
UTC = "UTC"
DOCTRINE_AYANAMSA = configure_swiss_ephemeris_sidereal(swe)


@dataclass(frozen=True)
class ChartSpec:
    slug: str
    title: str
    event_id: str
    analysis_note: str


CHART_SPECS: tuple[ChartSpec, ...] = (
    ChartSpec(
        slug="jupiter_moon_opposition_bullish_72h",
        title="Jupiter-Moon Opposition: bullish 72h sample",
        event_id="99ea7b0234cfe01f46149ea4db14bfc60aefc261791db82ee4c4b5ebe6c01a84",
        analysis_note="Holdout-positive family. This sample also had line_touch_after=True.",
    ),
    ChartSpec(
        slug="mercury_moon_conjunction_bullish_72h",
        title="Mercury-Moon Conjunction: bullish 72h sample",
        event_id="18d27e1c8196215f40846bde23157fa7cd8db70a61345e26a3134f2d3afbf142",
        analysis_note="Holdout-positive family. This sample had line_touch_during=True.",
    ),
    ChartSpec(
        slug="moon_saturn_sextile_bullish_24h_72h",
        title="Moon-Saturn Sextile: bullish sample",
        event_id="4a8567ff3339faf0ed299e478ab93d228050545e94a9de706ca568fac9222907",
        analysis_note="24h holdout-stable family. This sample had line_touch_during=True.",
    ),
    ChartSpec(
        slug="moon_sun_sextile_bearish_72h",
        title="Moon-Sun Sextile: bearish 72h sample",
        event_id="b98b145a4adf639043b1a8f9aff777b7c2ba243894bc48953a0ef332e5d87767",
        analysis_note="Holdout-negative family on 72h horizon.",
    ),
    ChartSpec(
        slug="mars_moon_opposition_reversal_case",
        title="Mars-Moon Opposition: reversal sample",
        event_id="0aea75e611ecabdb70e2035cb9ae8d91eef039475b31dfa1291eb95d99ad0e7a",
        analysis_note="Pair/aspect reversal candidate from the SR analysis.",
    ),
)


ASPECT_COLORS = {
    "conjunction": "#0f8b8d",
    "opposition": "#d1495b",
    "trine": "#4f772d",
    "square": "#6c757d",
    "sextile": "#f77f00",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an HTML chart pack for selected SR candidate events."
    )
    parser.add_argument(
        "--input",
        default=r"D:\PycharmProjects\planetary_pair_aspect_market_log_sr.csv",
        help="Input SR event CSV.",
    )
    parser.add_argument(
        "--price",
        default=r"D:\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
        help="Hourly MT5 OHLC parquet.",
    )
    parser.add_argument(
        "--output-dir",
        default=r"D:\PycharmProjects\astro_sr_chart_pack",
        help="Directory for generated HTML charts.",
    )
    parser.add_argument(
        "--hours-before",
        type=int,
        default=72,
        help="Hours of context before event start.",
    )
    parser.add_argument(
        "--hours-after",
        type=int,
        default=96,
        help="Hours of context after event end.",
    )
    return parser.parse_args()


def to_ist(value: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(value, errors="coerce")
    if parsed.dt.tz is None:
        parsed = parsed.dt.tz_localize(UTC)
    return parsed.dt.tz_convert(IST)


def load_events(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    bool_cols = [
        "line_touch_before",
        "line_touch_during",
        "line_touch_after",
        "line_break_up_before",
        "line_break_up_during",
        "line_break_up_after",
        "line_break_down_before",
        "line_break_down_during",
        "line_break_down_after",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].map(lambda x: str(x).strip().lower() in {"1", "true", "yes"})

    for col in [
        "event_time_local",
        "event_time_utc",
        "event_window_start_local",
        "event_window_end_local",
        "timestamp_local",
        "timestamp_utc",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    numeric_cols = [
        "ret_during_pct",
        "ret_after_24h_pct",
        "ret_after_72h_pct",
        "anchor_harmonic",
        "anchor_n_value",
        "anchor_degree",
        "anchor_line_start",
        "anchor_line_end",
        "anchor_line_before",
        "anchor_line_after",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_price(path: str) -> pd.DataFrame:
    price = pd.read_parquet(path).sort_index()
    if price.index.tz is None:
        price.index = price.index.tz_localize(UTC)
    price = price.tz_convert(IST)
    price.columns = [str(c).lower() for c in price.columns]
    required = {"open", "high", "low", "close"}
    missing = sorted(required - set(price.columns))
    if missing:
        raise RuntimeError(f"Missing OHLC columns in price data: {missing}")
    return price


def sibling_mode(mode: str) -> str:
    return "mirror" if str(mode).lower() == "direct" else "direct"


def line_from_identity(
    longitude_series: pd.Series,
    mode: str,
    harmonic: float,
    n_value: float,
    degree: int,
) -> pd.Series:
    base = float(harmonic) * float(n_value) * float(degree)
    lon = longitude_series.astype(float)
    if str(mode).lower() == "mirror":
        return base + float(harmonic) * (360.0 - lon)
    return base + float(harmonic) * lon


def pick_events(events: pd.DataFrame) -> list[tuple[ChartSpec, pd.Series]]:
    picked: list[tuple[ChartSpec, pd.Series]] = []
    for spec in CHART_SPECS:
        sub = events[events["event_id"].astype(str) == spec.event_id].copy()
        if sub.empty:
            raise RuntimeError(f"Event id not found in SR log: {spec.event_id}")
        picked.append((spec, sub.iloc[0]))
    return picked


def build_same_pair_aspect_panel(events: pd.DataFrame, pair_key: str, start_ts: pd.Timestamp, end_ts: pd.Timestamp, selected_event_id: str) -> pd.DataFrame:
    sub = events[
        (events["pair_key"] == pair_key)
        & (events["event_time_local"] >= start_ts)
        & (events["event_time_local"] <= end_ts)
    ].copy()
    sub = sub.sort_values("event_time_local").reset_index(drop=True)
    sub["is_selected"] = sub["event_id"].astype(str) == str(selected_event_id)
    return sub


def figure_for_event(
    row: pd.Series,
    spec: ChartSpec,
    events: pd.DataFrame,
    price: pd.DataFrame,
    hours_before: int,
    hours_after: int,
) -> go.Figure:
    event_start = pd.Timestamp(row["event_time_local"])
    event_end = pd.Timestamp(row["event_window_end_local"])
    start_ts = event_start - pd.Timedelta(hours=hours_before)
    end_ts = event_end + pd.Timedelta(hours=hours_after)

    price_slice = price[(price.index >= start_ts) & (price.index <= end_ts)].copy()
    if price_slice.empty:
        raise RuntimeError(f"No price data in chart window for event {row['event_id']}")

    anchor_planet = str(row["anchor_planet"]).upper()
    harmonic = float(row["anchor_harmonic"])
    n_value = float(row["anchor_n_value"])
    degree = int(row["anchor_degree"])
    anchor_mode = str(row["anchor_mode"]).lower()
    mirror_mode = sibling_mode(anchor_mode)

    lon_map = build_adaptive_longitude_map(
        planets=[anchor_planet],
        full_timestamps=price_slice.index,
        fetch_fn=fetch_planetary_longitude,
        astrology_method="sidereal",
        coordinate_system="geo",
    )
    longitude = lon_map[anchor_planet]
    anchor_line = line_from_identity(longitude, anchor_mode, harmonic, n_value, degree)
    sibling_line = line_from_identity(longitude, mirror_mode, harmonic, n_value, degree)

    pair_events = build_same_pair_aspect_panel(events, str(row["pair_key"]), start_ts, end_ts, str(row["event_id"]))

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.78, 0.22],
        subplot_titles=(
            f"{spec.title} | {row['pair_key']} {row['aspect']}",
            "Aspect timing for the same pair",
        ),
    )

    fig.add_trace(
        go.Candlestick(
            x=price_slice.index,
            open=price_slice["open"],
            high=price_slice["high"],
            low=price_slice["low"],
            close=price_slice["close"],
            name="USDJPY H1",
            increasing_line_color="#1b998b",
            decreasing_line_color="#d1495b",
            showlegend=True,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=anchor_line.index,
            y=anchor_line.values,
            mode="lines",
            name=f"Anchor line: {anchor_planet} {anchor_mode}",
            line=dict(color="#1d4ed8", width=2.5),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=sibling_line.index,
            y=sibling_line.values,
            mode="lines",
            name=f"Sibling line: {anchor_planet} {mirror_mode}",
            line=dict(color="#f59e0b", width=1.6, dash="dot"),
        ),
        row=1,
        col=1,
    )

    fig.add_vrect(
        x0=event_start,
        x1=event_end,
        fillcolor="rgba(245,158,11,0.18)",
        line_width=0,
        row="all",
        col=1,
    )
    fig.add_vline(x=event_start + pd.Timedelta(hours=24), line_color="#16a34a", line_dash="dash", row="all", col=1)
    fig.add_vline(x=event_start + pd.Timedelta(hours=72), line_color="#7c3aed", line_dash="dash", row="all", col=1)

    fig.add_trace(
        go.Scatter(
            x=[event_start, event_end],
            y=[
                price_slice.iloc[price_slice.index.get_indexer([event_start], method="nearest")[0]]["close"],
                price_slice.iloc[price_slice.index.get_indexer([event_end], method="nearest")[0]]["close"],
            ],
            mode="markers+text",
            text=["start", "end"],
            textposition="top center",
            marker=dict(size=10, color="#111827", symbol=["diamond", "x"]),
            name="Event window",
        ),
        row=1,
        col=1,
    )

    if not pair_events.empty:
        for aspect_name, sub in pair_events.groupby("aspect", dropna=False, sort=False):
            color = ASPECT_COLORS.get(str(aspect_name), "#374151")
            marker_sizes = [16 if v else 10 for v in sub["is_selected"]]
            marker_symbols = ["star" if v else "circle" for v in sub["is_selected"]]
            fig.add_trace(
                go.Scatter(
                    x=sub["event_time_local"],
                    y=sub["aspect"],
                    mode="markers+text",
                    text=[str(v).split("|")[0] if sel else "" for v, sel in zip(sub["pair_key"], sub["is_selected"], strict=False)],
                    textposition="top center",
                    marker=dict(size=marker_sizes, color=color, symbol=marker_symbols, line=dict(width=1, color="#111827")),
                    name=f"Aspect: {aspect_name}",
                    hovertemplate=(
                        "Aspect: %{y}<br>"
                        "Time: %{x}<br>"
                        f"Pair: {html.escape(str(row['pair_key']))}<br>"
                        "<extra></extra>"
                    ),
                    showlegend=True,
                ),
                row=2,
                col=1,
            )

    annotation_lines = [
        spec.analysis_note,
        f"Event start: {event_start}",
        f"Event end: {event_end}",
        f"Anchor: {anchor_planet} {anchor_mode} h={harmonic:g} n={n_value:g} d={degree}",
        f"Returns: during={float(row['ret_during_pct']):.3f}% | +24h={float(row['ret_after_24h_pct']):.3f}% | +72h={float(row['ret_after_72h_pct']):.3f}%",
        f"Flags: touch_during={bool(row['line_touch_during'])} | touch_after={bool(row['line_touch_after'])} | line_reversal_after={int(row['line_reversal_after'])}",
    ]

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.005,
        y=1.10,
        text="<br>".join(html.escape(line) for line in annotation_lines),
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.90)",
        bordercolor="#9ca3af",
        borderwidth=1,
        font=dict(size=11, color="#111827"),
    )

    fig.update_layout(
        template="plotly_white",
        width=1500,
        height=900,
        margin=dict(l=50, r=40, t=120, b=50),
        title=dict(
            text=(
                f"{spec.title}<br>"
                f"<sup>{row['pair_key']} {row['aspect']} | selected event id: {row['event_id']}</sup>"
            ),
            x=0.01,
            xanchor="left",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0),
        xaxis_rangeslider_visible=False,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.18)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.18)", row=1, col=1)
    fig.update_yaxes(type="category", row=2, col=1)
    return fig


def write_index(output_dir: Path, manifest: pd.DataFrame) -> None:
    rows = []
    for row in manifest.itertuples(index=False):
        rows.append(
            "<tr>"
            f"<td><a href='{html.escape(row.file_name)}'>{html.escape(row.title)}</a></td>"
            f"<td>{html.escape(str(row.pair_key))}</td>"
            f"<td>{html.escape(str(row.aspect))}</td>"
            f"<td>{html.escape(str(row.event_time_local))}</td>"
            f"<td>{float(row.ret_after_24h_pct):.3f}%</td>"
            f"<td>{float(row.ret_after_72h_pct):.3f}%</td>"
            f"<td>{html.escape(str(row.analysis_note))}</td>"
            "</tr>"
        )
    body = "\n".join(rows)
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SR Candidate Chart Pack</title>
  <style>
    body {{
      font-family: Georgia, 'Times New Roman', serif;
      margin: 24px;
      color: #111827;
      background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }}
    h1 {{
      margin-bottom: 6px;
    }}
    p {{
      max-width: 900px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      background: rgba(255,255,255,0.92);
    }}
    th, td {{
      border: 1px solid #cbd5e1;
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #dbeafe;
    }}
    a {{
      color: #1d4ed8;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <h1>SR Candidate Chart Pack</h1>
  <p>Each chart shows price, the exact SR anchor line used by the analysis, the sibling direct/mirror line for the same planet identity, and aspect timings for the same pair within the displayed window.</p>
  <table>
    <thead>
      <tr>
        <th>Chart</th>
        <th>Pair</th>
        <th>Aspect</th>
        <th>Event Time</th>
        <th>+24h</th>
        <th>+72h</th>
        <th>Why This Chart</th>
      </tr>
    </thead>
    <tbody>
      {body}
    </tbody>
  </table>
</body>
</html>"""
    (output_dir / "index.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    events = load_events(args.input)
    price = load_price(args.price)
    selected = pick_events(events)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, Any]] = []
    for spec, row in selected:
        fig = figure_for_event(
            row=row,
            spec=spec,
            events=events,
            price=price,
            hours_before=args.hours_before,
            hours_after=args.hours_after,
        )
        file_name = f"{spec.slug}.html"
        fig.write_html(str(output_dir / file_name), include_plotlyjs=True)
        manifest_rows.append(
            {
                "file_name": file_name,
                "title": spec.title,
                "event_id": row["event_id"],
                "pair_key": row["pair_key"],
                "aspect": row["aspect"],
                "event_time_local": row["event_time_local"],
                "ret_after_24h_pct": row["ret_after_24h_pct"],
                "ret_after_72h_pct": row["ret_after_72h_pct"],
                "analysis_note": spec.analysis_note,
            }
        )

    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(output_dir / "manifest.csv", index=False)
    write_index(output_dir, manifest)

    print(f"Saved chart pack: {output_dir}")
    print(f"Saved index: {output_dir / 'index.html'}")
    print(f"Saved manifest: {output_dir / 'manifest.csv'}")


if __name__ == "__main__":
    main()
