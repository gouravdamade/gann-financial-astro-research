from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import dash
from dash import Input, Output, State, dcc, html, no_update
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PROJECT_DIR = Path(r"C:\Users\ADMIN\Desktop\Trading_Algo\New folder")
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from adaptive_ephemeris_engine import build_adaptive_longitude_map
from JDML4 import fetch_planetary_longitude, swe
from doctrine_config import configure_swiss_ephemeris_sidereal


IST = "Asia/Kolkata"
UTC = "UTC"
DOCTRINE_AYANAMSA = configure_swiss_ephemeris_sidereal(swe)
ZONE_SOURCE_OPTIONS = [
    ("holdout_24h", "Holdout 24h"),
    ("holdout_72h", "Holdout 72h"),
    ("anchor_24h", "Anchor Broad 24h"),
    ("anchor_72h", "Anchor Broad 72h"),
    ("reversal_24h", "Reversal"),
]
ZONE_TYPE_OPTIONS = [
    ("bullish", "Bullish"),
    ("bearish", "Bearish"),
    ("reversal", "Reversal"),
]
ZONE_COLORS = {
    "bullish": "rgba(16,185,129,0.18)",
    "bearish": "rgba(220,38,38,0.18)",
    "reversal": "rgba(245,158,11,0.22)",
}
MARKER_COLORS = {
    "bullish": "#10b981",
    "bearish": "#dc2626",
    "reversal": "#f59e0b",
}
DEFAULT_DETAIL_DAYS = 90
SELECTED_LINE_COLOR = "#2563eb"
SELECTED_SIBLING_COLOR = "#f97316"
ALL_FILTER_VALUE = "__ALL__"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch a lazy-scrolling SR dashboard with reactive zones."
    )
    parser.add_argument(
        "--events",
        default=r"C:\Users\ADMIN\PycharmProjects\planetary_pair_aspect_market_log_sr.csv",
    )
    parser.add_argument(
        "--price",
        default=r"C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
    )
    parser.add_argument(
        "--report-dir",
        default=r"C:\Users\ADMIN\PycharmProjects\astro_sr_analysis_report",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8062)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def to_ist_series(ts: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(ts, errors="coerce")
    if parsed.dt.tz is None:
        parsed = parsed.dt.tz_localize(UTC)
    return parsed.dt.tz_convert(IST)


def normalize_bool(value: Any) -> bool | None:
    if pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes"}:
        return True
    if text in {"0", "false", "no"}:
        return False
    return None


def load_price(path: str) -> pd.DataFrame:
    price = pd.read_parquet(path).sort_index()
    if price.index.tz is None:
        price.index = price.index.tz_localize(UTC)
    price = price.tz_convert(IST)
    price.columns = [str(c).lower() for c in price.columns]
    required = {"open", "high", "low", "close"}
    missing = sorted(required - set(price.columns))
    if missing:
        raise RuntimeError(f"Missing OHLC columns: {missing}")
    return price


def load_events(path: str, price: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(path)
    dt_cols = [
        "event_time_local",
        "event_window_start_local",
        "event_window_end_local",
        "timestamp_local",
        "event_time_utc",
        "event_window_start_utc",
        "event_window_end_utc",
    ]
    for col in dt_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in [
        "ret_during_pct",
        "ret_after_24h_pct",
        "ret_after_72h_pct",
        "anchor_harmonic",
        "anchor_n_value",
        "anchor_degree",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["line_touch_before", "line_touch_during", "line_touch_after", "line_reversal_after"]:
        if col in df.columns:
            df[col] = df[col].map(normalize_bool)

    df["event_time_local"] = to_ist_series(df["event_time_local"])
    df["event_window_start_local"] = to_ist_series(df["event_window_start_local"])
    df["event_window_end_local"] = to_ist_series(df["event_window_end_local"])
    df["event_label"] = df["pair_key"].astype(str) + " | " + df["aspect"].astype(str)

    nearest_idx = price.index.get_indexer(df["event_time_local"], method="nearest")
    valid_mask = nearest_idx >= 0
    df = df.loc[valid_mask].copy()
    nearest_idx = nearest_idx[valid_mask]
    df["event_price"] = price["close"].to_numpy()[nearest_idx]
    return df.reset_index(drop=True)


def load_report_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    for col in ["line_touch_after", "line_touch_during"]:
        if col in df.columns:
            df[col] = df[col].map(normalize_bool)
    return df


def select_rules(report_dir: Path) -> pd.DataFrame:
    rules: list[dict[str, Any]] = []
    hold24 = load_report_csv(report_dir / "sr_holdout_24h.csv")
    hold72 = load_report_csv(report_dir / "sr_holdout_72h.csv")
    broad = load_report_csv(report_dir / "sr_broad_scan_qmax.csv")
    reversal = load_report_csv(report_dir / "sr_pair_aspect_reversal.csv")

    def add_holdout(df: pd.DataFrame, source_group: str, horizon_hours: int, top_n: int) -> None:
        if df.empty:
            return
        subset = df[
            (pd.to_numeric(df.get("sign_match"), errors="coerce") == 1)
            & (pd.to_numeric(df.get("p_test"), errors="coerce") < 0.20)
            & df["features"].isin(
                [
                    "pair_key|aspect",
                    "pair_key|aspect|line_touch_after",
                    "pair_key|aspect|line_touch_during",
                ]
            )
        ].copy()
        subset = subset.sort_values(["p_test", "n_test"], ascending=[True, False]).head(top_n)
        for _, row in subset.iterrows():
            lift = float(row["test_lift"])
            zone_kind = "bullish" if lift > 0 else "bearish"
            rules.append(
                {
                    "source_group": source_group,
                    "target": "dir_after_24h" if horizon_hours == 24 else "dir_after_72h",
                    "horizon_hours": horizon_hours,
                    "zone_kind": zone_kind,
                    "zone_label": f"{zone_kind.title()} {horizon_hours}h",
                    "priority_score": abs(lift),
                    "rule_quality": float(row["p_test"]),
                    "reason": (
                        f"{source_group} | {row['features']} | "
                        f"test_lift={lift:.3f} | p={float(row['p_test']):.3f}"
                    ),
                    "pair_key": row.get("pair_key"),
                    "aspect": row.get("aspect"),
                    "line_touch_after": row.get("line_touch_after"),
                    "line_touch_during": row.get("line_touch_during"),
                    "anchor_planet": row.get("anchor_planet"),
                    "anchor_mode": row.get("anchor_mode"),
                }
            )

    def add_anchor_rules(target: str, source_group: str, top_n: int) -> None:
        if broad.empty:
            return
        subset = broad[
            (broad["target"] == target)
            & (pd.to_numeric(broad["q_dir"], errors="coerce") < 0.25)
            & (broad["features"] == "anchor_planet|anchor_mode|line_touch_after")
        ].copy()
        subset = subset.sort_values(["q_dir", "p_dir"], ascending=[True, True]).head(top_n)
        horizon = 24 if target == "dir_after_24h" else 72
        for _, row in subset.iterrows():
            lift = float(row["lift_vs_baseline"])
            zone_kind = "bullish" if lift > 0 else "bearish"
            rules.append(
                {
                    "source_group": source_group,
                    "target": target,
                    "horizon_hours": horizon,
                    "zone_kind": zone_kind,
                    "zone_label": f"{zone_kind.title()} {horizon}h",
                    "priority_score": abs(lift),
                    "rule_quality": float(row["q_dir"]),
                    "reason": (
                        f"{source_group} | anchor={row.get('anchor_planet')} {row.get('anchor_mode')} "
                        f"| touch_after={row.get('line_touch_after')} | lift={lift:.3f} | q={float(row['q_dir']):.3f}"
                    ),
                    "pair_key": row.get("pair_key"),
                    "aspect": row.get("aspect"),
                    "line_touch_after": row.get("line_touch_after"),
                    "line_touch_during": row.get("line_touch_during"),
                    "anchor_planet": row.get("anchor_planet"),
                    "anchor_mode": row.get("anchor_mode"),
                }
            )

    def add_reversal_rules(df: pd.DataFrame) -> None:
        if df.empty:
            return
        subset = df[pd.to_numeric(df["q_dir"], errors="coerce") < 0.25].copy()
        subset = subset.sort_values(["q_dir", "p_dir"], ascending=[True, True]).head(8)
        for _, row in subset.iterrows():
            rules.append(
                {
                    "source_group": "reversal_24h",
                    "target": "line_reversal_after",
                    "horizon_hours": 24,
                    "zone_kind": "reversal",
                    "zone_label": "Reversal 24h",
                    "priority_score": abs(float(row["lift_vs_baseline"])),
                    "rule_quality": float(row["q_dir"]),
                    "reason": (
                        f"reversal_24h | {row.get('pair_key')} {row.get('aspect')} | "
                        f"lift={float(row['lift_vs_baseline']):.3f} | q={float(row['q_dir']):.3f}"
                    ),
                    "pair_key": row.get("pair_key"),
                    "aspect": row.get("aspect"),
                    "line_touch_after": row.get("line_touch_after"),
                    "line_touch_during": row.get("line_touch_during"),
                    "anchor_planet": row.get("anchor_planet"),
                    "anchor_mode": row.get("anchor_mode"),
                }
            )

    add_holdout(hold24, "holdout_24h", 24, 10)
    add_holdout(hold72, "holdout_72h", 72, 10)
    add_anchor_rules("dir_after_24h", "anchor_24h", 10)
    add_anchor_rules("dir_after_72h", "anchor_72h", 10)
    add_reversal_rules(reversal)
    return pd.DataFrame(rules).drop_duplicates().reset_index(drop=True)


def event_matches_rule(event_row: pd.Series, rule_row: pd.Series) -> bool:
    for col in ["pair_key", "aspect", "anchor_planet", "anchor_mode"]:
        value = rule_row.get(col)
        if pd.notna(value) and str(value) != "":
            if str(event_row.get(col)) != str(value):
                return False
    for col in ["line_touch_after", "line_touch_during"]:
        value = rule_row.get(col)
        if value is not None and not pd.isna(value):
            if normalize_bool(event_row.get(col)) != bool(value):
                return False
    return True


def build_zone_table(events: pd.DataFrame, rules: pd.DataFrame) -> pd.DataFrame:
    zone_rows: list[dict[str, Any]] = []
    for _, rule in rules.iterrows():
        matched = events[events.apply(lambda row: event_matches_rule(row, rule), axis=1)].copy()
        if matched.empty:
            continue
        for _, row in matched.iterrows():
            zone_end = row["event_window_end_local"] + pd.Timedelta(hours=int(rule["horizon_hours"]))
            edge_score = float(rule["priority_score"]) * max(0.05, 1.0 - min(float(rule["rule_quality"]), 1.0))
            score_label = f"{rule['zone_label']} | score={edge_score:.3f}"
            hover_lines = [
                f"Zone: {rule['zone_label']}",
                f"Event: {row['pair_key']} {row['aspect']}",
                f"Start: {row['event_window_start_local']}",
                f"End: {row['event_window_end_local']}",
                f"Reactive zone end: {zone_end}",
                f"Anchor: {row['anchor_planet']} {row['anchor_mode']} h={float(row['anchor_harmonic']):g} n={float(row['anchor_n_value']):g} d={int(row['anchor_degree'])}",
                f"Returns: during={float(row['ret_during_pct']):.3f}% | +24h={float(row['ret_after_24h_pct']):.3f}% | +72h={float(row['ret_after_72h_pct']):.3f}%",
                f"Flags: touch_during={bool(row['line_touch_during'])} | touch_after={bool(row['line_touch_after'])} | reversal_after={int(bool(row['line_reversal_after']))}",
                f"Edge score: {edge_score:.3f}",
                f"Reason: {rule['reason']}",
            ]
            zone_rows.append(
                {
                    "event_id": row["event_id"],
                    "pair_key": row["pair_key"],
                    "aspect": row["aspect"],
                    "event_label": row["event_label"],
                    "event_time_local": row["event_time_local"],
                    "event_window_start_local": row["event_window_start_local"],
                    "event_window_end_local": row["event_window_end_local"],
                    "zone_start": row["event_window_start_local"],
                    "zone_end": zone_end,
                    "event_price": row["event_price"],
                    "zone_kind": rule["zone_kind"],
                    "zone_label": rule["zone_label"],
                    "source_group": rule["source_group"],
                    "target": rule["target"],
                    "priority_score": float(rule["priority_score"]),
                    "rule_quality": float(rule["rule_quality"]),
                    "edge_score": edge_score,
                    "score_label": score_label,
                    "reason": rule["reason"],
                    "hover_text": "<br>".join(hover_lines),
                    "anchor_planet": row["anchor_planet"],
                    "anchor_mode": row["anchor_mode"],
                    "anchor_harmonic": row["anchor_harmonic"],
                    "anchor_n_value": row["anchor_n_value"],
                    "anchor_degree": row["anchor_degree"],
                    "ret_after_24h_pct": row["ret_after_24h_pct"],
                    "ret_after_72h_pct": row["ret_after_72h_pct"],
                    "ret_during_pct": row["ret_during_pct"],
                    "line_touch_after": row["line_touch_after"],
                    "line_touch_during": row["line_touch_during"],
                    "line_reversal_after": row["line_reversal_after"],
                }
            )
    zone_df = pd.DataFrame(zone_rows)
    if zone_df.empty:
        raise RuntimeError("No reactive zones were generated from the analysis rules.")
    zone_df = (
        zone_df.sort_values(["event_time_local", "priority_score"], ascending=[True, False])
        .drop_duplicates(subset=["event_id", "reason"])
        .reset_index(drop=True)
    )
    return zone_df


def line_identity(row: pd.Series) -> tuple[str, str, float, float, int]:
    return (
        str(row["anchor_planet"]).upper(),
        str(row["anchor_mode"]).lower(),
        float(row["anchor_harmonic"]),
        float(row["anchor_n_value"]),
        int(row["anchor_degree"]),
    )


def sibling_identity(identity: tuple[str, str, float, float, int]) -> tuple[str, str, float, float, int]:
    planet, mode, harmonic, n_value, degree = identity
    sibling_mode = "mirror" if mode == "direct" else "direct"
    return planet, sibling_mode, harmonic, n_value, degree


def line_key_text(identity: tuple[str, str, float, float, int]) -> str:
    planet, mode, harmonic, n_value, degree = identity
    return f"{planet} {mode} h={harmonic:g} n={n_value:g} d={degree}"


def line_from_identity(lon_series: pd.Series, identity: tuple[str, str, float, float, int]) -> pd.Series:
    _, mode, harmonic, n_value, degree = identity
    base = float(harmonic) * float(n_value) * float(degree)
    lon = lon_series.astype(float)
    if mode == "mirror":
        return base + float(harmonic) * (360.0 - lon)
    return base + float(harmonic) * lon


def event_hover_text(row: pd.Series) -> str:
    return "<br>".join(
        [
            f"Zone: {row.get('zone_label', 'NA')}",
            f"Event: {row['pair_key']} {row['aspect']}",
            f"Time: {row['event_time_local']}",
            f"Anchor: {row['anchor_planet']} {row['anchor_mode']} h={float(row['anchor_harmonic']):g} n={float(row['anchor_n_value']):g} d={int(row['anchor_degree'])}",
            f"Returns: during={float(row['ret_during_pct']):.3f}% | +24h={float(row['ret_after_24h_pct']):.3f}% | +72h={float(row['ret_after_72h_pct']):.3f}%",
            f"Flags: touch_during={bool(row['line_touch_during'])} | touch_after={bool(row['line_touch_after'])} | reversal_after={int(bool(row['line_reversal_after']))}",
            f"Reason: {row['reason']}",
        ]
    )


def parse_overview_range(relayout_data: dict[str, Any] | None, price: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    if not relayout_data:
        end = price.index.max()
        start = end - pd.Timedelta(days=DEFAULT_DETAIL_DAYS)
        return start, end
    if "xaxis.range[0]" in relayout_data and "xaxis.range[1]" in relayout_data:
        start = pd.to_datetime(relayout_data["xaxis.range[0]"])
        end = pd.to_datetime(relayout_data["xaxis.range[1]"])
        return start.tz_convert(IST) if start.tzinfo else start.tz_localize(IST), end.tz_convert(IST) if end.tzinfo else end.tz_localize(IST)
    if "xaxis.range" in relayout_data and isinstance(relayout_data["xaxis.range"], list):
        start = pd.to_datetime(relayout_data["xaxis.range"][0])
        end = pd.to_datetime(relayout_data["xaxis.range"][1])
        return start.tz_convert(IST) if start.tzinfo else start.tz_localize(IST), end.tz_convert(IST) if end.tzinfo else end.tz_localize(IST)
    end = price.index.max()
    start = end - pd.Timedelta(days=DEFAULT_DETAIL_DAYS)
    return start, end


def apply_zone_filters(
    zones: pd.DataFrame,
    selected_sources: list[str],
    selected_types: list[str],
    pair_filter: str | None,
    aspect_filter: str | None,
) -> pd.DataFrame:
    filt = zones[
        zones["source_group"].isin(selected_sources)
        & zones["zone_kind"].isin(selected_types)
    ].copy()
    if pair_filter and pair_filter != ALL_FILTER_VALUE:
        filt = filt[filt["pair_key"] == pair_filter]
    if aspect_filter and aspect_filter != ALL_FILTER_VALUE:
        filt = filt[filt["aspect"] == aspect_filter]
    return filt


def make_overview_figure(
    price: pd.DataFrame,
    zones: pd.DataFrame,
    selected_sources: list[str],
    selected_types: list[str],
    pair_filter: str | None = None,
    aspect_filter: str | None = None,
    selected_event_id: str | None = None,
) -> go.Figure:
    filt = apply_zone_filters(zones, selected_sources, selected_types, pair_filter, aspect_filter)
    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=price.index,
            y=price["close"],
            mode="lines",
            name="USDJPY close",
            line=dict(color="#0f172a", width=1),
            hovertemplate="Time: %{x}<br>Close: %{y:.3f}<extra></extra>",
        )
    )
    for zone_label, sub in filt.groupby("zone_label", dropna=False, sort=False):
        fig.add_trace(
            go.Scattergl(
                x=sub["event_time_local"],
                y=sub["event_price"],
                mode="markers",
                name=str(zone_label),
                marker=dict(size=7, color=[MARKER_COLORS.get(str(v), "#6b7280") for v in sub["zone_kind"]], symbol="diamond"),
                text=sub["hover_text"],
                customdata=sub["event_id"],
                hovertemplate="%{text}<extra></extra>",
            )
        )
    if selected_event_id:
        selected = zones[zones["event_id"].astype(str) == str(selected_event_id)].copy()
        if not selected.empty:
            row = selected.sort_values(["priority_score", "event_time_local"], ascending=[False, False]).iloc[0]
            fig.add_trace(
                go.Scattergl(
                    x=[row["event_time_local"]],
                    y=[row["event_price"]],
                    mode="markers+text",
                    name="Selected event",
                    marker=dict(size=12, color="#111827", symbol="star"),
                    text=[row["zone_label"]],
                    textposition="top center",
                    customdata=[row["event_id"]],
                    hovertemplate=row["hover_text"] + "<extra></extra>",
                )
            )

    end = price.index.max()
    start = end - pd.Timedelta(days=DEFAULT_DETAIL_DAYS)
    fig.update_layout(
        template="plotly_white",
        height=320,
        margin=dict(l=45, r=25, t=45, b=35),
        title="Full History Overview",
        xaxis=dict(
            rangeslider=dict(visible=True),
            range=[start, end],
            showgrid=True,
            gridcolor="rgba(148,163,184,0.18)",
        ),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.18)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0),
        uirevision="overview-static",
    )
    return fig


def build_zone_polygon(zone_row: pd.Series, y0: float, y1: float) -> go.Scatter:
    xs = [
        zone_row["zone_start"],
        zone_row["zone_start"],
        zone_row["zone_end"],
        zone_row["zone_end"],
        zone_row["zone_start"],
    ]
    ys = [y0, y1, y1, y0, y0]
    return go.Scatter(
        x=xs,
        y=ys,
        mode="lines",
        line=dict(color="rgba(0,0,0,0)"),
        fill="toself",
        fillcolor=ZONE_COLORS.get(str(zone_row["zone_kind"]), "rgba(107,114,128,0.18)"),
        hoveron="fills",
        text=zone_row["hover_text"],
        hovertemplate="%{text}<extra></extra>",
        name=f"{zone_row['zone_kind']} zone",
        showlegend=False,
    )


def build_detail_figure(
    price: pd.DataFrame,
    zones: pd.DataFrame,
    selected_sources: list[str],
    selected_types: list[str],
    pair_filter: str | None,
    aspect_filter: str | None,
    relayout_data: dict[str, Any] | None,
    selected_event_id: str | None,
    max_lines: int,
) -> tuple[go.Figure, pd.DataFrame]:
    window_start, window_end = parse_overview_range(relayout_data, price)
    filtered_zones = apply_zone_filters(zones, selected_sources, selected_types, pair_filter, aspect_filter)
    selected_zone = None
    if selected_event_id:
        selected_candidates = filtered_zones[filtered_zones["event_id"].astype(str) == str(selected_event_id)].copy()
        if not selected_candidates.empty:
            selected_zone = selected_candidates.sort_values(
                ["priority_score", "event_time_local"], ascending=[False, False]
            ).iloc[0]
            span = window_end - window_start
            if pd.isna(span) or span <= pd.Timedelta(0):
                span = pd.Timedelta(days=DEFAULT_DETAIL_DAYS)
            half = span / 2
            center = pd.Timestamp(selected_zone["event_time_local"])
            window_start = center - half
            window_end = center + half
    price_window = price[(price.index >= window_start) & (price.index <= window_end)].copy()
    if price_window.empty:
        price_window = price.tail(24 * DEFAULT_DETAIL_DAYS).copy()
        window_start = price_window.index.min()
        window_end = price_window.index.max()

    visible = filtered_zones[
        (filtered_zones["zone_end"] >= window_start)
        & (filtered_zones["zone_start"] <= window_end)
    ].copy()
    if selected_zone is not None and str(selected_zone["event_id"]) not in set(visible["event_id"].astype(str)):
        visible = pd.concat([visible, selected_zone.to_frame().T], ignore_index=True)
    visible = visible.sort_values(["priority_score", "event_time_local"], ascending=[False, True]).reset_index(drop=True)

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.80, 0.20],
        subplot_titles=("Price, planetary lines, reactive zones", "Aspect strip for visible reactive events"),
    )
    fig.add_trace(
        go.Candlestick(
            x=price_window.index,
            open=price_window["open"],
            high=price_window["high"],
            low=price_window["low"],
            close=price_window["close"],
            name="USDJPY H1",
            increasing_line_color="#1b998b",
            decreasing_line_color="#d1495b",
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    price_min = float(price_window["low"].min())
    price_max = float(price_window["high"].max())
    pad = (price_max - price_min) * 0.08 if price_max > price_min else 0.5
    y0 = price_min - pad
    y1 = price_max + pad

    for _, zone_row in visible.iterrows():
        fig.add_trace(build_zone_polygon(zone_row, y0, y1), row=1, col=1)

    unique_lines = visible.assign(identity=visible.apply(line_identity, axis=1)).drop_duplicates(subset=["identity"])
    selected_line_ids: list[tuple[str, str, float, float, int]] = []
    if selected_zone is not None:
        sel_identity = line_identity(selected_zone)
        selected_line_ids = [sel_identity, sibling_identity(sel_identity)]
    regular_line_ids = [identity for identity in unique_lines["identity"].tolist() if identity not in selected_line_ids]
    line_ids = selected_line_ids + regular_line_ids[: max(0, int(max_lines) - len(selected_line_ids))]

    line_long_map: dict[str, pd.Series] = {}
    if line_ids:
        planets = sorted({identity[0] for identity in line_ids})
        line_long_map = build_adaptive_longitude_map(
            planets=planets,
            full_timestamps=price_window.index,
            fetch_fn=fetch_planetary_longitude,
            astrology_method="sidereal",
            coordinate_system="geo",
        )
    for identity in line_ids:
        planet = identity[0]
        if planet not in line_long_map:
            continue
        lon_slice = line_long_map[planet].reindex(price_window.index)
        line_series = line_from_identity(lon_slice, identity)
        is_selected_identity = identity in selected_line_ids
        line_style: dict[str, Any] = {
            "width": 3 if is_selected_identity else 2,
            "dash": "dot" if identity[1] == "mirror" else "solid",
        }
        if is_selected_identity:
            line_style["color"] = SELECTED_LINE_COLOR if identity[1] == "direct" else SELECTED_SIBLING_COLOR
        fig.add_trace(
            go.Scatter(
                x=price_window.index,
                y=line_series.values,
                mode="lines",
                name=("Selected " if is_selected_identity else "") + line_key_text(identity),
                line=line_style,
                hovertemplate=f"{line_key_text(identity)}<br>Time: %{{x}}<br>Value: %{{y:.3f}}<extra></extra>",
            ),
            row=1,
            col=1,
        )

    if not visible.empty:
        fig.add_trace(
            go.Scatter(
                x=visible["event_time_local"],
                y=visible["event_price"],
                mode="markers",
                name="Reactive events",
                marker=dict(
                    size=10,
                    color=[MARKER_COLORS.get(str(v), "#6b7280") for v in visible["zone_kind"]],
                    symbol="diamond",
                    line=dict(width=1, color="#111827"),
                ),
                text=visible["hover_text"],
                customdata=visible["event_id"],
                hovertemplate="%{text}<extra></extra>",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=visible["event_time_local"],
                y=visible["event_label"],
                mode="markers",
                marker=dict(
                    size=11,
                    color=[MARKER_COLORS.get(str(v), "#6b7280") for v in visible["zone_kind"]],
                    symbol="circle",
                    line=dict(width=1, color="#111827"),
                ),
                text=visible["hover_text"],
                customdata=visible["event_id"],
                hovertemplate="%{text}<extra></extra>",
                name="Aspects",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    if selected_zone is not None:
        family = zones[
            (zones["pair_key"] == selected_zone["pair_key"])
            & (zones["aspect"] == selected_zone["aspect"])
            & (zones["event_time_local"] >= window_start)
            & (zones["event_time_local"] <= window_end)
        ].copy()
        family = family.sort_values("event_time_local").drop_duplicates(subset=["event_id"])
        if not family.empty:
            fig.add_trace(
                go.Scatter(
                    x=family["event_time_local"],
                    y=family["event_label"],
                    mode="markers",
                    marker=dict(size=9, color="#475569", symbol="circle-open"),
                    customdata=family["event_id"],
                    text=family.apply(event_hover_text, axis=1),
                    hovertemplate="%{text}<extra></extra>",
                    name="Selected family",
                    showlegend=False,
                ),
                row=2,
                col=1,
            )
        fig.add_trace(
            go.Scatter(
                x=[selected_zone["event_time_local"]],
                y=[selected_zone["event_price"]],
                mode="markers+text",
                marker=dict(size=15, color="#111827", symbol="star", line=dict(width=1, color="#f8fafc")),
                text=[selected_zone["zone_label"]],
                textposition="top center",
                customdata=[selected_zone["event_id"]],
                hovertemplate=selected_zone["hover_text"] + "<extra></extra>",
                name="Selected event",
            ),
            row=1,
            col=1,
        )
        fig.add_vrect(
            x0=selected_zone["event_window_start_local"],
            x1=selected_zone["event_window_end_local"],
            fillcolor="rgba(37,99,235,0.10)",
            line_color=SELECTED_LINE_COLOR,
            line_width=1,
            row="all",
            col=1,
        )

    fig.update_layout(
        template="plotly_white",
        height=920,
        margin=dict(l=45, r=25, t=70, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0),
        xaxis_rangeslider_visible=False,
        uirevision="detail-static",
        title=(
            f"Visible window: {window_start.strftime('%Y-%m-%d %H:%M')} to "
            f"{window_end.strftime('%Y-%m-%d %H:%M')} | zones={len(visible)}"
            + (
                f" | selected={selected_zone['pair_key']} {selected_zone['aspect']} @ {selected_zone['event_time_local']}"
                if selected_zone is not None
                else ""
            )
        ),
    )
    fig.update_yaxes(range=[y0, y1], row=1, col=1, showgrid=True, gridcolor="rgba(148,163,184,0.18)")
    fig.update_yaxes(type="category", row=2, col=1, showgrid=True, gridcolor="rgba(148,163,184,0.12)")
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.18)")
    return fig, visible


def build_zone_summary_table(visible: pd.DataFrame) -> html.Div:
    if visible.empty:
        return html.Div("No reactive zones in the current window.", style={"padding": "10px"})

    rows = []
    preview = visible.sort_values(["event_time_local", "priority_score"], ascending=[False, False]).head(20)
    for _, row in preview.iterrows():
        rows.append(
            html.Tr(
                [
                    html.Td(str(row["event_time_local"])),
                    html.Td(str(row["pair_key"])),
                    html.Td(str(row["aspect"])),
                    html.Td(str(row["zone_label"])),
                    html.Td(str(row["source_group"])),
                    html.Td(f"{float(row['edge_score']):.3f}"),
                    html.Td(f"{float(row['ret_after_24h_pct']):.3f}%"),
                    html.Td(f"{float(row['ret_after_72h_pct']):.3f}%"),
                    html.Td(str(row["reason"])),
                ]
            )
        )

    return html.Div(
        [
            html.H4("Visible Reactive Zones"),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Time"),
                                html.Th("Pair"),
                                html.Th("Aspect"),
                                html.Th("Label"),
                                html.Th("Source"),
                                html.Th("Score"),
                                html.Th("+24h"),
                                html.Th("+72h"),
                                html.Th("Reason"),
                            ]
                        )
                    ),
                    html.Tbody(rows),
                ],
                style={"width": "100%", "borderCollapse": "collapse"},
            ),
        ],
        style={"overflowX": "auto", "padding": "8px 0"},
    )


def build_family_event_table(
    visible: pd.DataFrame,
    selected_event_id: str | None,
    pair_filter: str | None,
    aspect_filter: str | None,
) -> html.Div:
    family = pd.DataFrame()
    if selected_event_id:
        selected = visible[visible["event_id"].astype(str) == str(selected_event_id)].copy()
        if not selected.empty:
            row = selected.sort_values(["priority_score", "event_time_local"], ascending=[False, False]).iloc[0]
            family = visible[
                (visible["pair_key"] == row["pair_key"])
                & (visible["aspect"] == row["aspect"])
            ].copy()
    elif pair_filter and pair_filter != ALL_FILTER_VALUE:
        family = visible[visible["pair_key"] == pair_filter].copy()
        if aspect_filter and aspect_filter != ALL_FILTER_VALUE:
            family = family[family["aspect"] == aspect_filter].copy()
    elif aspect_filter and aspect_filter != ALL_FILTER_VALUE:
        family = visible[visible["aspect"] == aspect_filter].copy()

    if family.empty:
        return html.Div("No focused family list for the current filters/window.", style={"padding": "10px"})

    rows = []
    preview = family.sort_values(["event_time_local", "edge_score"], ascending=[False, False]).head(30)
    for _, row in preview.iterrows():
        rows.append(
            html.Tr(
                [
                    html.Td("Selected" if selected_event_id and str(row["event_id"]) == str(selected_event_id) else ""),
                    html.Td(str(row["event_time_local"])),
                    html.Td(str(row["pair_key"])),
                    html.Td(str(row["aspect"])),
                    html.Td(str(row["zone_label"])),
                    html.Td(f"{float(row['edge_score']):.3f}"),
                    html.Td(f"{float(row['ret_after_24h_pct']):.3f}%"),
                    html.Td(f"{float(row['ret_after_72h_pct']):.3f}%"),
                ]
            )
        )

    return html.Div(
        [
            html.H4("Focused Family Events"),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Flag"),
                                html.Th("Time"),
                                html.Th("Pair"),
                                html.Th("Aspect"),
                                html.Th("Label"),
                                html.Th("Score"),
                                html.Th("+24h"),
                                html.Th("+72h"),
                            ]
                        )
                    ),
                    html.Tbody(rows),
                ],
                style={"width": "100%", "borderCollapse": "collapse"},
            ),
        ],
        style={"overflowX": "auto", "padding": "8px 0"},
    )


def build_app(price: pd.DataFrame, zones: pd.DataFrame) -> dash.Dash:
    app = dash.Dash(__name__)
    default_sources = [value for value, _ in ZONE_SOURCE_OPTIONS]
    default_types = [value for value, _ in ZONE_TYPE_OPTIONS]
    pair_options = [{"label": "All pairs", "value": ALL_FILTER_VALUE}] + [
        {"label": pair, "value": pair}
        for pair in sorted(zones["pair_key"].dropna().astype(str).unique())
    ]
    aspect_options = [{"label": "All aspects", "value": ALL_FILTER_VALUE}] + [
        {"label": aspect, "value": aspect}
        for aspect in sorted(zones["aspect"].dropna().astype(str).unique())
    ]

    app.layout = html.Div(
        [
            html.H2("SR Reactive Dashboard"),
            html.P(
                "Scroll the overview chart to move through history. "
                "The detail chart updates with candles, anchor planetary lines, and hoverable reactive zones."
            ),
            dcc.Store(id="selected-event-store"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Zone Sources"),
                            dcc.Checklist(
                                id="zone-source-checklist",
                                options=[{"label": label, "value": value} for value, label in ZONE_SOURCE_OPTIONS],
                                value=default_sources,
                                inline=True,
                            ),
                        ],
                        style={"marginBottom": "10px"},
                    ),
                    html.Div(
                        [
                            html.Label("Zone Types"),
                            dcc.Checklist(
                                id="zone-type-checklist",
                                options=[{"label": label, "value": value} for value, label in ZONE_TYPE_OPTIONS],
                                value=default_types,
                                inline=True,
                            ),
                        ],
                        style={"marginBottom": "10px"},
                    ),
                    html.Div(
                        [
                            html.Label("Pair Filter"),
                            dcc.Dropdown(
                                id="pair-filter-dropdown",
                                options=pair_options,
                                value=ALL_FILTER_VALUE,
                                clearable=False,
                            ),
                        ],
                        style={"marginBottom": "10px"},
                    ),
                    html.Div(
                        [
                            html.Label("Aspect Filter"),
                            dcc.Dropdown(
                                id="aspect-filter-dropdown",
                                options=aspect_options,
                                value=ALL_FILTER_VALUE,
                                clearable=False,
                            ),
                        ],
                        style={"marginBottom": "10px"},
                    ),
                    html.Div(
                        [
                            html.Label("Max planetary lines in detail view"),
                            dcc.Slider(
                                id="max-lines-slider",
                                min=1,
                                max=10,
                                step=1,
                                value=6,
                                marks={i: str(i) for i in range(1, 11)},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Button("Clear selected event", id="clear-selection-btn", n_clicks=0),
                            html.Button("Export visible window", id="export-window-btn", n_clicks=0, style={"marginLeft": "8px"}),
                            html.Div(id="selected-event-info", style={"marginTop": "8px"}),
                            html.Div(id="export-status", style={"marginTop": "8px"}),
                        ],
                        style={"marginTop": "12px"},
                    )
                ],
                style={"background": "#f8fafc", "padding": "12px 14px", "border": "1px solid #cbd5e1"},
            ),
            dcc.Graph(
                id="overview-graph",
                figure=make_overview_figure(price, zones, default_sources, default_types),
                config={"displaylogo": False, "scrollZoom": True},
            ),
            dcc.Graph(
                id="detail-graph",
                config={"displaylogo": False, "scrollZoom": True},
            ),
            html.Div(id="zone-summary"),
            html.Div(id="family-event-list"),
        ],
        style={"maxWidth": "1700px", "margin": "0 auto", "padding": "14px"},
    )

    @app.callback(
        Output("selected-event-store", "data"),
        Input("overview-graph", "clickData"),
        Input("detail-graph", "clickData"),
        Input("clear-selection-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_selected_event(
        overview_click: dict[str, Any] | None,
        detail_click: dict[str, Any] | None,
        clear_clicks: int,
    ) -> str | None:
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == "clear-selection-btn":
            return None
        click_data = overview_click if trigger_id == "overview-graph" else detail_click
        if not click_data or not click_data.get("points"):
            return no_update
        event_id = click_data["points"][0].get("customdata")
        if isinstance(event_id, (list, tuple)):
            event_id = event_id[0] if event_id else None
        if event_id is None or str(event_id).strip() == "":
            return no_update
        return str(event_id)

    @app.callback(
        Output("overview-graph", "figure"),
        Input("zone-source-checklist", "value"),
        Input("zone-type-checklist", "value"),
        Input("pair-filter-dropdown", "value"),
        Input("aspect-filter-dropdown", "value"),
        Input("selected-event-store", "data"),
    )
    def update_overview(
        selected_sources: list[str],
        selected_types: list[str],
        pair_filter: str | None,
        aspect_filter: str | None,
        selected_event_id: str | None,
    ) -> go.Figure:
        selected_sources = selected_sources or default_sources
        selected_types = selected_types or default_types
        return make_overview_figure(
            price,
            zones,
            selected_sources,
            selected_types,
            pair_filter,
            aspect_filter,
            selected_event_id,
        )

    @app.callback(
        Output("detail-graph", "figure"),
        Output("zone-summary", "children"),
        Output("selected-event-info", "children"),
        Output("family-event-list", "children"),
        Input("overview-graph", "relayoutData"),
        Input("zone-source-checklist", "value"),
        Input("zone-type-checklist", "value"),
        Input("pair-filter-dropdown", "value"),
        Input("aspect-filter-dropdown", "value"),
        Input("max-lines-slider", "value"),
        Input("selected-event-store", "data"),
    )
    def update_detail(
        relayout_data: dict[str, Any] | None,
        selected_sources: list[str],
        selected_types: list[str],
        pair_filter: str | None,
        aspect_filter: str | None,
        max_lines: int,
        selected_event_id: str | None,
    ) -> tuple[go.Figure, html.Div, html.Div, html.Div]:
        selected_sources = selected_sources or default_sources
        selected_types = selected_types or default_types
        fig, visible = build_detail_figure(
            price=price,
            zones=zones,
            selected_sources=selected_sources,
            selected_types=selected_types,
            pair_filter=pair_filter,
            aspect_filter=aspect_filter,
            relayout_data=relayout_data,
            selected_event_id=selected_event_id,
            max_lines=int(max_lines or 6),
        )
        info = "No event locked."
        if selected_event_id:
            selected = zones[zones["event_id"].astype(str) == str(selected_event_id)].copy()
            if not selected.empty:
                row = selected.sort_values(["priority_score", "event_time_local"], ascending=[False, False]).iloc[0]
                info = (
                    f"Selected event: {row['pair_key']} {row['aspect']} | {row['zone_label']} | "
                    f"{row['event_time_local']} | anchor={row['anchor_planet']} {row['anchor_mode']}"
                )
        family_list = build_family_event_table(visible, selected_event_id, pair_filter, aspect_filter)
        return fig, build_zone_summary_table(visible), html.Div(info), family_list

    @app.callback(
        Output("export-status", "children"),
        Input("export-window-btn", "n_clicks"),
        State("overview-graph", "relayoutData"),
        State("zone-source-checklist", "value"),
        State("zone-type-checklist", "value"),
        State("pair-filter-dropdown", "value"),
        State("aspect-filter-dropdown", "value"),
        State("max-lines-slider", "value"),
        State("selected-event-store", "data"),
        prevent_initial_call=True,
    )
    def export_visible_window(
        n_clicks: int,
        relayout_data: dict[str, Any] | None,
        selected_sources: list[str],
        selected_types: list[str],
        pair_filter: str | None,
        aspect_filter: str | None,
        max_lines: int,
        selected_event_id: str | None,
    ) -> html.Div:
        selected_sources = selected_sources or default_sources
        selected_types = selected_types or default_types
        fig, visible = build_detail_figure(
            price=price,
            zones=zones,
            selected_sources=selected_sources,
            selected_types=selected_types,
            pair_filter=pair_filter,
            aspect_filter=aspect_filter,
            relayout_data=relayout_data,
            selected_event_id=selected_event_id,
            max_lines=int(max_lines or 6),
        )
        export_dir = Path(r"C:\Users\ADMIN\PycharmProjects\astro_sr_exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        stamp = pd.Timestamp.now(tz=IST).strftime("%Y%m%d_%H%M%S")
        pair_part = "all" if not pair_filter or pair_filter == ALL_FILTER_VALUE else str(pair_filter).replace("|", "_")
        aspect_part = "all" if not aspect_filter or aspect_filter == ALL_FILTER_VALUE else str(aspect_filter)
        base = f"visible_{stamp}_{pair_part}_{aspect_part}"
        html_path = export_dir / f"{base}.html"
        csv_path = export_dir / f"{base}.csv"
        fig.write_html(str(html_path), include_plotlyjs=True)
        visible.to_csv(csv_path, index=False)
        message = f"Saved HTML: {html_path} | Saved CSV: {csv_path}"
        try:
            png_path = export_dir / f"{base}.png"
            fig.write_image(str(png_path))
            message += f" | Saved PNG: {png_path}"
        except Exception:
            pass
        return html.Div(message)

    return app


def main() -> None:
    args = parse_args()
    report_dir = Path(args.report_dir)
    price = load_price(args.price)
    events = load_events(args.events, price)
    rules = select_rules(report_dir)
    zones = build_zone_table(events, rules)

    print(f"Loaded price bars: {len(price)}")
    print(f"Loaded events: {len(events)}")
    print(f"Selected reactive rules: {len(rules)}")
    print(f"Reactive zones: {len(zones)}")
    print(f"Dashboard URL: http://{args.host}:{args.port}")

    app = build_app(price, zones)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
