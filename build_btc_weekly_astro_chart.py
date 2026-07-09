from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PROJECT_ROOT = Path(__file__).resolve().parent
LEGACY_PROJECT = Path(r"D:\Trading_Algo\New folder")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if LEGACY_PROJECT.exists() and str(LEGACY_PROJECT) not in sys.path:
    sys.path.insert(0, str(LEGACY_PROJECT))

import swisseph as swe

from doctrine_config import configure_swiss_ephemeris_sidereal, doctrine_ayanamsa_name


IST = "Asia/Kolkata"
UTC = timezone.utc
GENESIS_UTC = pd.Timestamp("2009-01-03 18:15:05", tz="UTC")
DEFAULT_DEGREE_SCALES = (360.0, 180.0)
DEFAULT_OUTPUT_ROOT = Path(r"D:\GannFinancialAstro\doc")
BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

BODY_IDS = {
    "SUN": swe.SUN,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
    "RAHU": swe.TRUE_NODE,
    "URANUS": swe.URANUS,
    "NEPTUNE": swe.NEPTUNE,
    "PLUTO": swe.PLUTO,
}
BODY_ORDER = ("SUN", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "RAHU", "KETU", "URANUS", "NEPTUNE", "PLUTO")
SLOW_BODY_ORDER = ("MARS", "JUPITER", "SATURN", "RAHU", "KETU", "URANUS", "NEPTUNE", "PLUTO")
ASPECTS = {
    "conjunction_orb": {"angle": 0.0, "orb": 1.5, "color": "rgba(34,211,238,0.14)"},
    "square": {"angle": 90.0, "orb": 1.0, "color": "rgba(248,113,113,0.13)"},
    "trine": {"angle": 120.0, "orb": 1.0, "color": "rgba(74,222,128,0.13)"},
    "opposition_orb": {"angle": 180.0, "orb": 1.5, "color": "rgba(251,191,36,0.13)"},
}
LINE_COLORS = {
    "SUN": "#facc15",
    "MERCURY": "#38bdf8",
    "VENUS": "#fb7185",
    "MARS": "#ef4444",
    "JUPITER": "#22c55e",
    "SATURN": "#94a3b8",
    "RAHU": "#a855f7",
    "KETU": "#84cc16",
    "URANUS": "#06b6d4",
    "NEPTUNE": "#6366f1",
    "PLUTO": "#f97316",
}


@dataclass(frozen=True)
class PlaceHypothesis:
    label: str
    city: str
    tz: str
    lat: float
    lon: float
    rationale: str
    source_url: str


PLACE_HYPOTHESES = {
    "van_nuys": PlaceHypothesis(
        label="Van Nuys / Los Angeles hypothesis",
        city="Van Nuys, California, USA",
        tz="America/Los_Angeles",
        lat=34.1899,
        lon=-118.4514,
        rationale=(
            "Astrologer Astral Harmony discusses Van Nuys/Southern California as a Bitcoin origin hypothesis. "
            "This is unverified, so houses/angles are experimental."
        ),
        source_url="https://astralharmony.com/blog/astrology-bitcoin-series-part-two/",
    ),
    "london": PlaceHypothesis(
        label="London / Times headline hypothesis",
        city="London, England",
        tz="Europe/London",
        lat=51.5074,
        lon=-0.1278,
        rationale="Common astrology-market hypothesis using the Times headline embedded in the Genesis block.",
        source_url="https://www.yourastrogenes.com/post/the-astrology-of-bitcoin-part-i-birth-chart",
    ),
    "dublin": PlaceHypothesis(
        label="Dublin neutral-place hypothesis",
        city="Dublin, Ireland",
        tz="Europe/Dublin",
        lat=53.3498,
        lon=-6.2603,
        rationale="AstroConnexions uses Dublin while noting Bitcoin has no confirmed physical birth place.",
        source_url="https://astroconnexions.com/bitcoin/bitcoin-the-astrology/",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build BTC weekly chart with natal/transit astrology overlays.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--place", choices=sorted(PLACE_HYPOTHESES), default="van_nuys")
    parser.add_argument("--start", default="2017-08-01", help="UTC start date. Binance spot BTCUSDT begins Aug 2017.")
    parser.add_argument("--end", default=(pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=8)).strftime("%Y-%m-%d"))
    parser.add_argument("--aspect-end", default="2030-01-31", help="UTC date through which future astro windows are calculated.")
    parser.add_argument("--n-values", default="30,40,50,60,70,80,90,100,110,120,130,140,150")
    parser.add_argument("--factors", default="1.6,1.8")
    parser.add_argument("--degree-scales", default="360,180")
    parser.add_argument("--min-window-days", type=float, default=21.0)
    parser.add_argument("--max-sr-lines", type=int, default=360)
    parser.add_argument("--max-aspect-windows", type=int, default=1000)
    parser.add_argument(
        "--aspect-classification-csv",
        default="auto",
        help="Path to btc_aspect_effectiveness_summary.csv. Use 'auto' for latest output, or 'none' to disable noise filtering.",
    )
    return parser.parse_args()


def parse_float_list(text: str) -> list[float]:
    return [float(part.strip()) for part in str(text).split(",") if part.strip()]


def configure_ephemeris() -> None:
    configure_swiss_ephemeris_sidereal(swe)
    for path in [
        Path(r"D:\Trading_Algo\Desktop_Trading_Algo_root_legacy_20260530\sweph"),
        Path(r"D:\Trading_Algo\New folder\sweph"),
        Path(r"D:\PycharmProjects\sweph"),
    ]:
        if path.exists():
            swe.set_ephe_path(str(path))
            return


def utc_timestamp_ms(value: pd.Timestamp) -> int:
    return int(value.tz_convert("UTC").timestamp() * 1000)


def fetch_binance_weekly(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    rows: list[list[Any]] = []
    cursor = utc_timestamp_ms(start)
    end_ms = utc_timestamp_ms(end)
    while cursor < end_ms:
        url = (
            f"{BINANCE_KLINES_URL}?symbol=BTCUSDT&interval=1w"
            f"&startTime={cursor}&endTime={end_ms}&limit=1000"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            batch = json.load(response)
        if not batch:
            break
        rows.extend(batch)
        last_open = int(batch[-1][0])
        next_cursor = last_open + 7 * 24 * 60 * 60 * 1000
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        if len(batch) < 1000:
            break
    if not rows:
        raise RuntimeError("No Binance BTCUSDT weekly candles returned.")
    frame = pd.DataFrame(
        rows,
        columns=[
            "open_time_ms",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time_ms",
            "quote_asset_volume",
            "trade_count",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )
    for col in ["open", "high", "low", "close", "volume", "quote_asset_volume"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["open_time_utc"] = pd.to_datetime(frame["open_time_ms"], unit="ms", utc=True)
    frame["close_time_utc"] = pd.to_datetime(frame["close_time_ms"], unit="ms", utc=True)
    frame["open_time_ist"] = frame["open_time_utc"].dt.tz_convert(IST)
    frame["close_time_ist"] = frame["close_time_utc"].dt.tz_convert(IST)
    frame = frame.drop_duplicates("open_time_utc").sort_values("open_time_utc")
    frame = frame[(frame["open_time_utc"] >= start) & (frame["open_time_utc"] <= end)].reset_index(drop=True)
    return frame


def jd_ut(ts: pd.Timestamp) -> float:
    dt = ts.tz_convert("UTC").to_pydatetime()
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0 + dt.microsecond / 3_600_000_000.0
    return float(swe.julday(dt.year, dt.month, dt.day, hour))


def planet_lon(body: str, ts: pd.Timestamp) -> float:
    body = body.upper()
    if body == "KETU":
        return (planet_lon("RAHU", ts) + 180.0) % 360.0
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    try:
        return float(swe.calc_ut(jd_ut(ts), BODY_IDS[body], flags)[0][0] % 360.0)
    except Exception:
        flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        return float(swe.calc_ut(jd_ut(ts), BODY_IDS[body], flags)[0][0] % 360.0)


def angle_delta(a: float, b: float) -> float:
    return abs(((float(a) - float(b) + 180.0) % 360.0) - 180.0)


def aspect_delta(transit_lon: float, natal_lon: float, angle: float) -> float:
    return abs(((float(transit_lon) - float(natal_lon) - float(angle) + 180.0) % 360.0) - 180.0)


def birth_chart(place: PlaceHypothesis) -> dict[str, Any]:
    natal = {body: planet_lon(body, GENESIS_UTC) for body in BODY_ORDER}
    jd = jd_ut(GENESIS_UTC)
    try:
        houses, ascmc = swe.houses(jd, float(place.lat), float(place.lon))
        ayan = float(swe.get_ayanamsa_ut(jd))
        asc = (float(ascmc[0]) - ayan) % 360.0
        mc = (float(ascmc[1]) - ayan) % 360.0
    except Exception:
        asc = np.nan
        mc = np.nan
    return {
        "genesis_utc": GENESIS_UTC.isoformat(),
        "genesis_ist": GENESIS_UTC.tz_convert(IST).isoformat(),
        "place": place.__dict__,
        "ayanamsa": doctrine_ayanamsa_name(),
        "natal_longitudes": natal,
        "asc_sidereal": asc,
        "mc_sidereal": mc,
    }


def build_daily_transits(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    idx = pd.date_range(start.normalize(), end.normalize(), freq="1D", tz="UTC")
    records = []
    for ts in idx:
        row = {"ts_utc": ts, "ts_ist": ts.tz_convert(IST)}
        for body in BODY_ORDER:
            row[body] = planet_lon(body, ts)
        records.append(row)
    return pd.DataFrame.from_records(records)


def build_weekly_transits(price: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ts in price["open_time_utc"]:
        row = {"open_time_utc": ts, "open_time_ist": ts.tz_convert(IST)}
        for body in BODY_ORDER:
            row[body] = planet_lon(body, ts)
        rows.append(row)
    return pd.DataFrame.from_records(rows)


def build_aspect_windows(
    daily: pd.DataFrame,
    natal: dict[str, float],
    min_days: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for transit_body in BODY_ORDER:
        if transit_body == "MOON":
            continue
        for natal_body, natal_lon in natal.items():
            if natal_body == "MOON":
                continue
            if {transit_body, natal_body} == {"RAHU", "KETU"}:
                continue
            series = daily[transit_body].astype(float)
            for aspect_name, spec in ASPECTS.items():
                delta = series.map(lambda lon: aspect_delta(lon, natal_lon, spec["angle"]))
                active = delta <= float(spec["orb"])
                if not active.any():
                    continue
                start_ix = None
                for ix, is_active in enumerate(active.tolist() + [False]):
                    if is_active and start_ix is None:
                        start_ix = ix
                    elif not is_active and start_ix is not None:
                        end_ix = ix - 1
                        sub_delta = delta.iloc[start_ix : end_ix + 1]
                        peak_ix = int(sub_delta.idxmin())
                        start_ts = daily.iloc[start_ix]["ts_utc"]
                        end_ts = daily.iloc[end_ix]["ts_utc"] + pd.Timedelta(days=1)
                        duration = (end_ts - start_ts).total_seconds() / 86400.0
                        if duration >= min_days:
                            rows.append(
                                {
                                    "transit_body": transit_body,
                                    "natal_body": natal_body,
                                    "aspect": aspect_name,
                                    "aspect_angle": spec["angle"],
                                    "orb_limit": spec["orb"],
                                    "start_utc": start_ts,
                                    "end_utc": end_ts,
                                    "start_ist": start_ts.tz_convert(IST),
                                    "end_ist": end_ts.tz_convert(IST),
                                    "peak_utc": daily.iloc[peak_ix]["ts_utc"],
                                    "peak_ist": daily.iloc[peak_ix]["ts_utc"].tz_convert(IST),
                                    "peak_orb_deg": float(sub_delta.min()),
                                    "duration_days": duration,
                                    "label": f"{transit_body}->{natal_body} {aspect_name}",
                                }
                            )
                        start_ix = None
    out = pd.DataFrame.from_records(rows)
    if out.empty:
        return out
    return out.sort_values(["start_utc", "duration_days", "peak_orb_deg"], ascending=[True, False, True]).reset_index(drop=True)


def add_family_key(windows: pd.DataFrame) -> pd.DataFrame:
    if windows.empty:
        return windows
    out = windows.copy()
    out["family_key"] = (
        out["transit_body"].astype(str) + "|" + out["natal_body"].astype(str) + "::" + out["aspect"].astype(str)
    )
    return out


def latest_aspect_classification_csv(output_root: Path) -> Path | None:
    candidates = sorted(
        output_root.glob("btc_aspect_effectiveness_*/btc_aspect_effectiveness_summary.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def filter_noise_aspect_windows(
    windows: pd.DataFrame,
    classification_arg: str,
    output_root: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    windows = add_family_key(windows)
    meta: dict[str, Any] = {
        "classification_filter": "disabled",
        "classification_csv": "",
        "noise_families_excluded": 0,
        "windows_before_noise_filter": int(len(windows)),
        "windows_after_noise_filter": int(len(windows)),
    }
    if windows.empty or str(classification_arg).lower() == "none":
        return windows, meta
    path: Path | None
    if str(classification_arg).lower() == "auto":
        path = latest_aspect_classification_csv(output_root)
    else:
        path = Path(classification_arg)
    if path is None or not path.exists():
        meta["classification_filter"] = "missing"
        return windows, meta
    summary = pd.read_csv(path)
    if "family_key" not in summary.columns or "classification" not in summary.columns:
        meta["classification_filter"] = "invalid_missing_columns"
        meta["classification_csv"] = str(path)
        return windows, meta
    noise_families = set(summary.loc[summary["classification"] == "noise", "family_key"].astype(str))
    if not noise_families:
        meta.update(
            {
                "classification_filter": "active_no_noise_families",
                "classification_csv": str(path),
            }
        )
        return windows, meta
    filtered = windows[~windows["family_key"].astype(str).isin(noise_families)].reset_index(drop=True)
    meta.update(
        {
            "classification_filter": "active_excluding_noise",
            "classification_csv": str(path),
            "noise_families_excluded": int(len(noise_families)),
            "noise_windows_excluded": int(len(windows) - len(filtered)),
            "windows_after_noise_filter": int(len(filtered)),
        }
    )
    return filtered, meta


def sr_level(lon: float, factor: float, n_value: float, mode: str, degree_scale: float) -> float:
    src_lon = (360.0 - lon) if mode == "mirror" else lon
    return float(factor) * float(n_value) * float(degree_scale) + float(factor) * float(src_lon)


def select_sr_lines_for_chart(sr_lines: pd.DataFrame, max_sr_lines: int) -> pd.DataFrame:
    if sr_lines.empty:
        return sr_lines
    ranked = sr_lines.sort_values(["touch_count", "min_distance_usd"], ascending=[False, True])
    if max_sr_lines <= 0 or len(ranked) <= max_sr_lines:
        return ranked
    # Preserve coverage across higher n-values and both degree scales, then fill by strongest historical touch.
    required = (
        ranked.groupby(["body", "degree_scale", "n_value"], as_index=False, group_keys=False)
        .head(1)
        .sort_values(["n_value", "degree_scale", "body"])
    )
    if len(required) >= max_sr_lines:
        return required.head(max_sr_lines)
    fill = ranked[~ranked.index.isin(required.index)].head(max_sr_lines - len(required))
    return pd.concat([required, fill], ignore_index=False).drop_duplicates("identity")


def build_sr_lines(
    price: pd.DataFrame,
    weekly_transits: pd.DataFrame,
    n_values: list[float],
    factors: list[float],
    degree_scales: list[float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    price_low = float(price["low"].min())
    price_high = float(price["high"].max())
    price_pad_low = price_low * 0.70
    price_pad_high = price_high * 1.80
    line_rows: list[dict[str, Any]] = []
    touch_rows: list[dict[str, Any]] = []
    for body in BODY_ORDER:
        lon_series = weekly_transits[body].astype(float).to_numpy()
        for mode in ("direct", "mirror"):
            for factor in factors:
                for n_value in n_values:
                    for degree_scale in degree_scales:
                        levels = np.array(
                            [sr_level(lon, factor, n_value, mode, degree_scale) for lon in lon_series],
                            dtype=float,
                        )
                        if np.nanmax(levels) < price_pad_low or np.nanmin(levels) > price_pad_high:
                            continue
                        ident = f"{body} {mode} f={factor:g} n={n_value:g} d={degree_scale:g}"
                        distance = np.minimum.reduce(
                            [
                                np.abs(price["high"].to_numpy(dtype=float) - levels),
                                np.abs(price["low"].to_numpy(dtype=float) - levels),
                                np.abs(price["close"].to_numpy(dtype=float) - levels),
                            ]
                        )
                        atr_proxy = (price["high"] - price["low"]).rolling(14, min_periods=3).mean().bfill().to_numpy(dtype=float)
                        touch_band = np.maximum(0.025 * price["close"].to_numpy(dtype=float), 0.20 * atr_proxy)
                        touched = (
                            (price["low"].to_numpy(dtype=float) <= levels)
                            & (price["high"].to_numpy(dtype=float) >= levels)
                        ) | (distance <= touch_band)
                        touch_count = int(np.nansum(touched))
                        min_distance = float(np.nanmin(distance))
                        latest_level = float(levels[-1])
                        line_rows.append(
                            {
                                "identity": ident,
                                "body": body,
                                "mode": mode,
                                "factor": factor,
                                "n_value": n_value,
                                "degree_scale": degree_scale,
                                "touch_count": touch_count,
                                "min_distance_usd": min_distance,
                                "latest_level": latest_level,
                                "level_min": float(np.nanmin(levels)),
                                "level_max": float(np.nanmax(levels)),
                            }
                        )
                        if touch_count:
                            hit_idx = np.where(touched)[0]
                            for ix in hit_idx:
                                touch_rows.append(
                                    {
                                        "identity": ident,
                                        "body": body,
                                        "mode": mode,
                                        "factor": factor,
                                        "n_value": n_value,
                                        "degree_scale": degree_scale,
                                        "time_utc": price.iloc[ix]["open_time_utc"],
                                        "time_ist": price.iloc[ix]["open_time_ist"],
                                        "level": float(levels[ix]),
                                        "open": float(price.iloc[ix]["open"]),
                                        "high": float(price.iloc[ix]["high"]),
                                        "low": float(price.iloc[ix]["low"]),
                                        "close": float(price.iloc[ix]["close"]),
                                        "distance_usd": float(distance[ix]),
                                    }
                                )
    return pd.DataFrame(line_rows), pd.DataFrame(touch_rows)


def active_window_counts(price: pd.DataFrame, windows: pd.DataFrame) -> pd.Series:
    counts = []
    for ts in price["open_time_utc"]:
        if windows.empty:
            counts.append(0)
        else:
            counts.append(int(((windows["start_utc"] <= ts) & (windows["end_utc"] >= ts)).sum()))
    return pd.Series(counts, index=price.index)


def make_chart(
    price: pd.DataFrame,
    weekly_transits: pd.DataFrame,
    windows: pd.DataFrame,
    sr_lines: pd.DataFrame,
    metadata: dict[str, Any],
    max_sr_lines: int,
    max_aspect_windows: int,
) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.82, 0.18],
        subplot_titles=("BTCUSDT weekly with astrological overlays", "Active transit-to-natal aspect windows"),
    )
    x = price["open_time_ist"]
    fig.add_trace(
        go.Candlestick(
            x=x,
            open=price["open"],
            high=price["high"],
            low=price["low"],
            close=price["close"],
            name="BTCUSDT weekly",
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444",
            increasing_fillcolor="#22c55e",
            decreasing_fillcolor="#ef4444",
        ),
        row=1,
        col=1,
    )
    price = price.copy()
    price["ma20"] = price["close"].rolling(20, min_periods=4).mean()
    price["ma50"] = price["close"].rolling(50, min_periods=10).mean()
    fig.add_trace(go.Scatter(x=x, y=price["ma20"], name="20W MA", line=dict(color="#38bdf8", width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=price["ma50"], name="50W MA", line=dict(color="#f59e0b", width=1.2)), row=1, col=1)

    bull_windows = [
        ("2017 peak tail (Binance data starts)", "2017-08-14", "2018-01-08", "rgba(251,146,60,0.08)"),
        ("2020-21 bull run", "2020-03-09", "2021-11-15", "rgba(34,197,94,0.08)"),
        ("2022-current cycle", "2022-11-21", metadata["price_end_ist"][:10], "rgba(59,130,246,0.08)"),
    ]
    for label, start, end, color in bull_windows:
        fig.add_vrect(
            x0=pd.Timestamp(start, tz=IST),
            x1=pd.Timestamp(end, tz=IST),
            fillcolor=color,
            line_width=0,
            layer="below",
            annotation_text=label,
            annotation_position="top left",
            row=1,
            col=1,
        )

    if not sr_lines.empty:
        selected_lines = select_sr_lines_for_chart(sr_lines, max_sr_lines)
        price_times = weekly_transits["open_time_ist"]
        for _, line in selected_lines.iterrows():
            body = str(line["body"])
            mode = str(line["mode"])
            factor = float(line["factor"])
            n_value = float(line["n_value"])
            degree_scale = float(line["degree_scale"])
            levels = [
                sr_level(float(lon), factor, n_value, mode, degree_scale)
                for lon in weekly_transits[body].astype(float)
            ]
            fig.add_trace(
                go.Scatter(
                    x=price_times,
                    y=levels,
                    mode="lines",
                    name=str(line["identity"]),
                    showlegend=False,
                    line=dict(
                        color=LINE_COLORS.get(body, "#94a3b8"),
                        width=0.8 if int(line["touch_count"]) else 0.45,
                        dash="solid" if mode == "direct" else "dot",
                    ),
                    opacity=0.42 if int(line["touch_count"]) else 0.18,
                    hovertemplate=(
                        f"{line['identity']}<br>"
                        "Level=%{y:.2f}<br>%{x}<extra></extra>"
                    ),
                ),
                row=1,
                col=1,
            )

    drawn_windows = windows.head(max_aspect_windows) if not windows.empty else windows
    y_marker = float(price["high"].max()) * 0.94
    for _, row in drawn_windows.iterrows():
        spec = ASPECTS.get(str(row["aspect"]), {})
        fig.add_vrect(
            x0=row["start_ist"],
            x1=row["end_ist"],
            fillcolor=spec.get("color", "rgba(148,163,184,0.10)"),
            line_width=0,
            layer="below",
            row=1,
            col=1,
        )
    if not drawn_windows.empty:
        fig.add_trace(
            go.Scatter(
                x=drawn_windows["peak_ist"],
                y=[y_marker] * len(drawn_windows),
                mode="markers",
                name="Filtered astro windows >= 7d",
                showlegend=False,
                marker=dict(size=8, color="#e0f2fe", symbol="triangle-down", line=dict(width=0.6, color="#0f172a")),
                customdata=np.stack(
                    [
                        drawn_windows["label"].astype(str),
                        drawn_windows["duration_days"].round(1).astype(str),
                        drawn_windows["peak_orb_deg"].round(3).astype(str),
                    ],
                    axis=-1,
                ),
                hovertemplate="%{customdata[0]}<br>Duration=%{customdata[1]} days<br>Peak orb=%{customdata[2]} deg<br>%{x}<extra></extra>",
            ),
            row=1,
            col=1,
        )

    chart_start_ist = pd.Timestamp(price["open_time_ist"].min()).tz_convert(IST).normalize()
    aspect_end_ist = pd.Timestamp(metadata["aspect_end_ist"]).tz_convert(IST).normalize()
    density_times = pd.date_range(chart_start_ist, aspect_end_ist, freq="7D")
    density_axis = pd.DataFrame(
        {
            "open_time_ist": density_times,
            "open_time_utc": density_times.tz_convert("UTC"),
        }
    )
    counts = active_window_counts(density_axis, windows)
    fig.add_trace(
        go.Bar(x=density_axis["open_time_ist"], y=counts, name="Active astro windows", marker_color="#8b5cf6", opacity=0.75),
        row=2,
        col=1,
    )

    place = metadata["place"]
    subtitle = (
        f"Genesis: {metadata['genesis_utc']} UTC / {metadata['genesis_ist']} IST | "
        f"Place hypothesis: {place['city']} | Ayanamsa: {metadata['ayanamsa']}"
    )
    fig.update_layout(
        title=f"Bitcoin weekly astro research chart<br><sup>{subtitle}</sup>",
        template="plotly_dark",
        autosize=True,
        height=980,
        margin=dict(l=65, r=35, t=110, b=45),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        xaxis_rangeslider_visible=False,
        hovermode="closest",
        hoverdistance=24,
        spikedistance=-1,
    )
    fig.update_xaxes(showspikes=False)
    fig.update_yaxes(showspikes=False)
    fig.update_yaxes(title_text="BTCUSDT", type="log", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_xaxes(title_text="IST", row=2, col=1)
    fig.update_xaxes(
        range=[chart_start_ist, aspect_end_ist],
        row=1,
        col=1,
    )
    fig.update_xaxes(
        range=[chart_start_ist, aspect_end_ist],
        row=2,
        col=1,
    )
    note = (
        f"Filters: Moon skipped; transit Rahu<->Ketu pair skipped; aspect windows under {metadata['min_window_days']:g} days removed. "
        f"SR grid uses n={metadata['n_values']}, f={metadata['factors']}, d={metadata['degree_scales']}."
    )
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.01,
        y=0.99,
        text=note,
        showarrow=False,
        align="left",
        bgcolor="rgba(15,23,42,0.72)",
        bordercolor="rgba(148,163,184,0.55)",
        font=dict(size=11),
    )
    return fig


def write_readme(output_dir: Path, metadata: dict[str, Any], windows: pd.DataFrame, sr_lines: pd.DataFrame) -> None:
    place = metadata["place"]
    text = f"""# BTC Weekly Astro Chart

Generated: {metadata['generated_at_ist']}

Chart: `btc_weekly_astro_chart.html`

## Assumptions

- BTC price source: Binance spot `BTCUSDT` weekly klines.
- Price candle range: `{metadata['chart_start_ist']}` to `{metadata['price_end_ist']}` in IST.
- Astro window range: `{metadata['chart_start_ist']}` to `{metadata['aspect_end_ist']}` in IST.
- Genesis block timestamp: `{metadata['genesis_utc']}` UTC = `{metadata['genesis_ist']}` IST.
- Primary place hypothesis: `{place['city']}`.
- Place status: unverified; used only as an experimental astrological anchor.
- Ayanamsa: `{metadata['ayanamsa']}`.
- Moon is excluded.
- Rahu/Ketu interaction with each other is excluded.
- Aspect windows shorter than `{metadata['min_window_days']}` days are excluded.
- Noise aspect filter: `{metadata['filters']['noise_aspect_families']['classification_filter']}`.
- Noise families excluded from chart overlays: `{metadata['filters']['noise_aspect_families'].get('noise_families_excluded', 0)}`.
- SR grid uses `n={metadata['n_values']}`, `f={metadata['factors']}`, and `d={metadata['degree_scales']}`.

## Outputs

- `btc_weekly_price_binance.csv`
- `btc_weekly_astro_windows.csv` ({len(windows)} chart-visible filtered windows)
- `btc_weekly_astro_windows_all.csv` (all generated windows before noise-family exclusion)
- `btc_weekly_sr_lines.csv` ({len(sr_lines)} candidate lines inside/near price range)
- `btc_weekly_sr_touches.csv`
- `btc_weekly_metadata.json`

## Source Notes

- Blockstream documents the Genesis block timestamp as `2009-01-03 18:15:05 UTC`.
- AstroConnexions explicitly says Bitcoin's location is open to question and uses Dublin.
- YourAstroGenes uses London based on the Times headline hypothesis.
- Astral Harmony lists London, New York, Sydney, and Van Nuys hypotheses; this run uses Van Nuys as the experimental place choice.
"""
    (output_dir / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    configure_ephemeris()
    place = PLACE_HYPOTHESES[args.place]
    start = pd.Timestamp(args.start, tz="UTC")
    end = pd.Timestamp(args.end, tz="UTC")
    aspect_end = pd.Timestamp(args.aspect_end, tz="UTC")
    if aspect_end < end:
        raise ValueError("--aspect-end must be on or after --end so future astro windows cover the full chart.")
    n_values = parse_float_list(args.n_values)
    factors = parse_float_list(args.factors)
    degree_scales = parse_float_list(args.degree_scales)
    stamp = pd.Timestamp.now(tz=IST).strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root)
    output_dir = output_root / f"btc_weekly_astro_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    price = fetch_binance_weekly(start, end)
    daily = build_daily_transits(price["open_time_utc"].min(), aspect_end)
    weekly_transits = build_weekly_transits(price)
    metadata = birth_chart(place)
    windows_all = build_aspect_windows(daily, metadata["natal_longitudes"], args.min_window_days)
    windows, classification_meta = filter_noise_aspect_windows(
        windows_all,
        args.aspect_classification_csv,
        output_root,
    )
    metadata.update(
        {
            "generated_at_ist": pd.Timestamp.now(tz=IST).isoformat(),
            "chart_start_ist": price["open_time_ist"].min().isoformat(),
            "chart_end_ist": aspect_end.tz_convert(IST).isoformat(),
            "price_end_ist": price["open_time_ist"].max().isoformat(),
            "aspect_end_ist": aspect_end.tz_convert(IST).isoformat(),
            "n_values": n_values,
            "factors": factors,
            "degree_scales": degree_scales,
            "min_window_days": args.min_window_days,
            "filters": {
                "skip_moon": True,
                "skip_rahu_ketu_pair": True,
                "min_window_days": args.min_window_days,
                "noise_aspect_families": classification_meta,
            },
            "alternate_place_hypotheses": {
                key: value.__dict__ for key, value in PLACE_HYPOTHESES.items() if key != args.place
            },
            "sources": [
                "https://help.blockstream.com/education/glossary/genesis-block",
                "https://astroconnexions.com/bitcoin/bitcoin-the-astrology/",
                "https://www.yourastrogenes.com/post/the-astrology-of-bitcoin-part-i-birth-chart",
                "https://astralharmony.com/blog/astrology-bitcoin-series-part-two/",
                "https://api.binance.com/api/v3/klines",
            ],
        }
    )

    sr_lines, sr_touches = build_sr_lines(price, weekly_transits, n_values, factors, degree_scales)
    fig = make_chart(price, weekly_transits, windows, sr_lines, metadata, args.max_sr_lines, args.max_aspect_windows)

    price.to_csv(output_dir / "btc_weekly_price_binance.csv", index=False)
    daily.to_csv(output_dir / "btc_daily_transit_longitudes.csv", index=False)
    weekly_transits.to_csv(output_dir / "btc_weekly_transit_longitudes.csv", index=False)
    add_family_key(windows_all).to_csv(output_dir / "btc_weekly_astro_windows_all.csv", index=False)
    windows.to_csv(output_dir / "btc_weekly_astro_windows.csv", index=False)
    sr_lines.to_csv(output_dir / "btc_weekly_sr_lines.csv", index=False)
    sr_touches.to_csv(output_dir / "btc_weekly_sr_touches.csv", index=False)
    (output_dir / "btc_weekly_metadata.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    write_readme(output_dir, metadata, windows, sr_lines)
    html_path = output_dir / "btc_weekly_astro_chart.html"
    fig.write_html(
        html_path,
        include_plotlyjs=True,
        full_html=True,
        config={"responsive": True},
        post_script=(
            "Plotly.relayout('{plot_id}', {"
            "'hovermode':'closest',"
            "'spikedistance':-1,"
            "'xaxis.showspikes':false,"
            "'xaxis2.showspikes':false,"
            "'yaxis.showspikes':false,"
            "'yaxis2.showspikes':false"
            "});"
        ),
    )

    print(f"Wrote: {html_path}")
    print(f"Output dir: {output_dir}")
    print(f"Weekly candles: {len(price)}")
    print(f"Filtered astro windows >= {args.min_window_days:g}d: {len(windows)}")
    print(f"SR candidate lines in/near price range: {len(sr_lines)}")
    print(f"SR touches: {len(sr_touches)}")


if __name__ == "__main__":
    main()
