from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

try:
    from pytz import timezone
except Exception:  # pragma: no cover
    timezone = None

PROJECT_DIR = Path(r"D:\\Trading_Algo\\New folder")
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from adaptive_ephemeris_engine import build_adaptive_longitude_map
from JDML4 import fetch_planetary_longitude, swe
from doctrine_config import configure_swiss_ephemeris_sidereal

IST = "Asia/Kolkata"
UTC = "UTC"
DOCTRINE_AYANAMSA = configure_swiss_ephemeris_sidereal(swe)
DEFAULT_HARMONICS = (0.12, 0.18)
DEFAULT_N_VALUES = (1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8)
DEFAULT_DEGREES = (360, 180, 90, 45)
DEFAULT_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "JUPITER", "SATURN", "MARS")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a row-level planetary pair/aspect market log with before/during/after\n"
            "line-relative metrics using JDML4 SR pivots."
        )
    )
    parser.add_argument(
        "--events",
        default=r"D:\\PycharmProjects\\astro_training_data_ipo_tokyo_18890211.parquet",
        help="Input event parquet",
    )
    parser.add_argument(
        "--price",
        default=r"D:\\PycharmProjects\\usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
        help="Hourly USDJPY OHLC parquet from MT5",
    )
    parser.add_argument(
        "--output",
        default=r"D:\\PycharmProjects\\planetary_pair_aspect_market_log_sr.csv",
        help="Output CSV path",
    )
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--before-hours", type=float, default=24.0)
    parser.add_argument("--after-hours", type=float, default=24.0)
    parser.add_argument("--after-hours-72", type=float, default=72.0)
    parser.add_argument(
        "--lookback-hours",
        type=int,
        default=12,
        help="Bars used only for optional nearest-side classification in summary metrics",
    )
    parser.add_argument(
        "--include-natal",
        action="store_true",
        default=False,
        help="Include natal events instead of dropping is_natal=true rows.",
    )
    return parser.parse_args()


def to_ist_series(ts: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(ts, errors="coerce")
    if parsed.dt.tz is None:
        if timezone is None:
            raise RuntimeError("pytz is required for timestamp conversion.")
        parsed = parsed.dt.tz_localize(IST)
    return parsed.dt.tz_convert(IST)


def to_utc_series(ts: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(ts, errors="coerce")
    if parsed.dt.tz is None:
        if timezone is None:
            raise RuntimeError("pytz is required for timestamp conversion.")
        parsed = parsed.dt.tz_localize(IST)
    return parsed.dt.tz_convert(UTC)


def safe_json(value: Any) -> Any:
    if isinstance(value, dict) or isinstance(value, list):
        return value
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed
    except Exception:
        return {}


def _parse_float_list(value: Any, default: Any) -> tuple[float, ...]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            value = parsed
        except Exception:
            value = []
    if value is None:
        return tuple(default)
    if not isinstance(value, (list, tuple)):
        return tuple(default)
    out: list[float] = []
    for item in value:
        try:
            out.append(float(item))
        except Exception:
            continue
    return tuple(out) if out else tuple(default)


def _parse_str_list(value: Any, default: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            value = parsed
        except Exception:
            value = []
    if value is None:
        return tuple(default)
    if not isinstance(value, (list, tuple)):
        return tuple(default)
    out: list[str] = []
    for item in value:
        txt = str(item).strip().upper()
        if txt:
            out.append(txt)
    return tuple(out) if out else tuple(default)


def parse_sr_config(value: Any) -> dict[str, Any]:
    cfg = safe_json(value)
    if not isinstance(cfg, dict):
        cfg = {}
    return {
        "planets": _parse_str_list(cfg.get("planets"), DEFAULT_PLANETS),
        "harmonics": _parse_float_list(cfg.get("harmonics"), DEFAULT_HARMONICS),
        "n_values": _parse_float_list(cfg.get("n_values"), DEFAULT_N_VALUES),
        "degrees": _parse_float_list(cfg.get("degrees"), DEFAULT_DEGREES),
        "price_zone": float(cfg.get("price_zone", 0.16)),
        "moon_factor": float(cfg.get("moon_factor", 1.8)),
        "epsilon": float(cfg.get("epsilon", 0.30)),
        "band_pct": float(cfg.get("band_pct", 0.01)),
    }


def parse_identity_from_snapshot(value: Any) -> Optional[tuple]:
    snap = safe_json(value)
    if not isinstance(snap, dict):
        return None
    nearest = snap.get("nearest_line")
    if not isinstance(nearest, dict):
        return None
    ident = nearest.get("identity")
    if not isinstance(ident, dict):
        return None
    try:
        planet = str(ident.get("planet", "")).upper().strip()
        mode = str(ident.get("mode", "")).strip().lower()
        harmonic = float(ident.get("harmonic"))
        n_value = float(ident.get("n_value"))
        degree = int(float(ident.get("degree")))
        if not planet or mode not in {"direct", "mirror"}:
            return None
        return planet, mode, harmonic, n_value, degree
    except Exception:
        return None


def parse_sr_line_price_at_event(value: Any) -> Optional[float]:
    snap = safe_json(value)
    if not isinstance(snap, dict):
        return None
    nearest = snap.get("nearest_line")
    if isinstance(nearest, dict):
        price = nearest.get("price")
        try:
            if price is None:
                return None
            p = float(price)
            return p if np.isfinite(p) else None
        except Exception:
            return None
    return None


def line_from_identity_series(
    lon_series: pd.Series, identity: tuple[str, str, float, float, int]
) -> np.ndarray:
    planet, mode, harmonic, n_value, degree = identity
    h = float(harmonic)
    base = h * float(degree) * float(n_value)
    lon = lon_series.to_numpy(dtype=float, copy=False)
    if mode == "mirror":
        return base + h * (360.0 - lon)
    return base + h * lon


def line_identity_text(identity: tuple[str, str, float, float, int]) -> str:
    planet, mode, harmonic, n_value, degree = identity
    return f"{planet}|{mode}|h{harmonic:g}|n{n_value:g}|d{int(degree)}"


def canonical_pair(a: str, b: str) -> str:
    a = str(a).strip().upper()
    b = str(b).strip().upper()
    return f"{a}|{b}" if a <= b else f"{b}|{a}"


def build_close_lookup(price_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    price_cols = {"open", "high", "low", "close"}
    missing = price_cols - set(price_df.columns.str.lower())
    if missing:
        raise RuntimeError(f"Missing OHLC columns in price data: {sorted(missing)}")

    frame = pd.DataFrame(index=price_df.index)
    frame["open"] = pd.to_numeric(price_df["open"], errors="coerce")
    frame["high"] = pd.to_numeric(price_df["high"], errors="coerce")
    frame["low"] = pd.to_numeric(price_df["low"], errors="coerce")
    frame["close"] = pd.to_numeric(price_df["close"], errors="coerce")

    idx = frame.index.view("int64")
    return (
        idx,
        frame["open"].to_numpy(dtype="float64"),
        frame["high"].to_numpy(dtype="float64"),
        frame["low"].to_numpy(dtype="float64"),
        frame["close"].to_numpy(dtype="float64"),
    )


def pct(c0: float, c1: float) -> float:
    if not np.isfinite(c0) or not np.isfinite(c1) or c0 == 0.0:
        return np.nan
    return (c1 - c0) / c0 * 100.0


def direction_from_change(change: float, min_move_pct: float = 0.0) -> str:
    if not np.isfinite(change):
        return "NA"
    if change > min_move_pct:
        return "UP"
    if change < -min_move_pct:
        return "DOWN"
    return "FLAT"


def window_interaction(
    low_arr: np.ndarray,
    high_arr: np.ndarray,
    close_arr: np.ndarray,
    line_arr: np.ndarray,
    i0: int,
    i1: int,
    zone: float,
) -> dict[str, Any]:
    if i0 > i1:
        i0, i1 = i1, i0

    seg_slice = slice(i0, i1 + 1)
    low_s = low_arr[seg_slice]
    high_s = high_arr[seg_slice]
    close_s = close_arr[seg_slice]
    line_s = line_arr[seg_slice]

    valid = (
        np.isfinite(low_s)
        & np.isfinite(high_s)
        & np.isfinite(close_s)
        & np.isfinite(line_s)
    )
    if not np.any(valid):
        return {
            "touched": False,
            "broke_up": False,
            "broke_down": False,
            "min_distance": np.nan,
            "min_distance_bar": np.nan,
            "bars": 0,
        }

    low_v = low_s[valid]
    high_v = high_s[valid]
    close_v = close_s[valid]
    line_v = line_s[valid]

    dist = np.minimum(np.abs(high_v - line_v), np.abs(low_v - line_v))
    min_dist = float(np.min(dist))
    min_idx = int(np.argmin(dist))
    min_abs_idx = int(np.nonzero(valid)[0][min_idx])
    return {
        "touched": bool(min_dist <= zone),
        "broke_up": bool(np.any(close_v > line_v)),
        "broke_down": bool(np.any(close_v < line_v)),
        "min_distance": min_dist,
        "min_distance_bar": min_abs_idx,
        "bars": int(np.count_nonzero(valid)),
    }


def rank_within_lookback(arr: np.ndarray, center_idx: int, lookback: int) -> float:
    s = max(0, center_idx - lookback)
    win = arr[s : center_idx + 1]
    valid = np.isfinite(win)
    if not np.any(valid):
        return np.nan
    win = win[valid]
    ref = arr[center_idx]
    if not np.isfinite(ref):
        return np.nan
    return float(np.mean(win <= ref))


def main() -> None:
    args = parse_args()

    events = pd.read_parquet(args.events)
    if "is_natal" in events.columns and not args.include_natal:
        events = events[~events["is_natal"].astype(bool)].copy()
    if "interval" in events.columns:
        events = events[events["interval"].astype(str).str.lower() == args.interval.lower()].copy()
    if events.empty:
        raise RuntimeError("No events after transit/interval filtering.")

    start_local = to_ist_series(events["timestamp"])
    start_utc = to_utc_series(events["timestamp"])
    events = events.copy()
    events["timestamp"] = start_local
    events["timestamp_utc"] = start_utc
    duration = pd.to_numeric(events["duration_minutes"], errors="coerce")
    end_local = start_local + pd.to_timedelta(duration, unit="m")
    end_utc = start_utc + pd.to_timedelta(duration, unit="m")

    before_td = pd.Timedelta(hours=float(args.before_hours))
    after_td = pd.Timedelta(hours=float(args.after_hours))
    after72_td = pd.Timedelta(hours=float(args.after_hours_72))

    before_start = start_local - before_td
    before_start_utc = start_utc - before_td
    after_start = end_local
    after_start_utc = end_utc
    after_end = after_start + after_td
    after_end_utc = after_start_utc + after_td
    after72_end = after_start + after72_td
    after72_end_utc = after_start_utc + after72_td

    events["event_end"] = end_local
    events["event_end_utc"] = end_utc
    events["duration_minutes"] = duration.fillna(60.0)
    events["before_ts"] = before_start
    events["before_ts_utc"] = before_start_utc
    events["after_ts"] = after_end
    events["after_ts_utc"] = after_end_utc
    events["after72_ts"] = after72_end
    events["after72_ts_utc"] = after72_end_utc
    events["before_hours"] = float(args.before_hours)
    events["after_hours"] = float(args.after_hours)
    events["after72_hours"] = float(args.after_hours_72)

    events["anchor_identity"] = events["sr_snapshot_json"].apply(parse_identity_from_snapshot)
    events["sr_config_parsed"] = events["sr_config_json"].apply(parse_sr_config)

    price = pd.read_parquet(args.price).sort_index()
    if price.index.tz is None:
        price.index = price.index.tz_localize(UTC)
    price = price.tz_convert(IST)
    if price.empty:
        raise RuntimeError("Price data is empty.")

    event_min = events["timestamp"].min() - before_td - pd.Timedelta(hours=1)
    event_max = events["event_end"].max() + after72_td + pd.Timedelta(hours=1)
    price = price[(price.index >= event_min) & (price.index <= event_max)].copy()
    if price.empty:
        raise RuntimeError("No price overlap with event windows.")

    events = events[(events["timestamp"] >= price.index.min()) & (events["event_end"] <= price.index.max())].copy()
    if events.empty:
        raise RuntimeError("No events fall in price overlap range.")

    ts = price.index
    _, open_arr, high_arr, low_arr, close_arr = build_close_lookup(price)

    timestamps = price.index
    events["idx_start"] = timestamps.get_indexer(events["timestamp"].to_numpy(), method="nearest")
    events["idx_end"] = timestamps.get_indexer(events["event_end"].to_numpy(), method="nearest")
    events["idx_before"] = timestamps.get_indexer(events["before_ts"].to_numpy(), method="nearest")
    events["idx_after"] = timestamps.get_indexer(events["after_ts"].to_numpy(), method="nearest")
    events["idx_after72"] = timestamps.get_indexer(events["after72_ts"].to_numpy(), method="nearest")

    valid_pos = (
        (events["idx_start"] >= 0)
        & (events["idx_end"] >= 0)
        & (events["idx_before"] >= 0)
        & (events["idx_after"] >= 0)
        & (events["idx_after72"] >= 0)
        & (events["idx_after"] > events["idx_start"])
        & (events["idx_end"] >= events["idx_start"])
        & (events["idx_after"] >= events["idx_end"])
        & (events["idx_after72"] >= events["idx_end"])
        & (events["idx_before"] <= events["idx_start"])
    )
    events = events[valid_pos].copy()
    if events.empty:
        raise RuntimeError("No events with valid price index mapping.")

    needed_planets = set(DEFAULT_PLANETS)
    for cfg in events["sr_config_parsed"]:
        needed_planets.update(cfg.get("planets", DEFAULT_PLANETS))
    for ident in events["anchor_identity"].dropna():
        if isinstance(ident, tuple) and len(ident) == 5:
            needed_planets.add(str(ident[0]).upper())
    needed_planets = sorted(p for p in needed_planets if p)

    print(f"Building adaptive longitude map for {len(needed_planets)} planets...")
    lon_map = build_adaptive_longitude_map(
        planets=needed_planets,
        full_timestamps=ts,
        fetch_fn=fetch_planetary_longitude,
        astrology_method="sidereal",
        coordinate_system="geo",
    )

    unique_identities = sorted({x for x in events["anchor_identity"] if isinstance(x, tuple) and len(x) == 5})
    line_map: dict[tuple[str, str, float, float, int], np.ndarray] = {}
    for ident in unique_identities:
        planet = ident[0]
        if planet not in lon_map or lon_map[planet] is None or lon_map[planet].empty:
            continue
        line_map[ident] = line_from_identity_series(lon_map[planet], ident)

    unresolved = events["anchor_identity"].isna()
    if unresolved.any():
        print(f"Attempting SR-identity fallback for {int(unresolved.sum())} events.")
        for i, row in events[unresolved].iterrows():
            cfg = row["sr_config_parsed"]
            idx = int(row["idx_start"])
            close_now = float(close_arr[idx])
            if not np.isfinite(close_now):
                continue

            best: Optional[tuple] = None
            best_abs = None

            for planet in cfg.get("planets", DEFAULT_PLANETS):
                lon_s = lon_map.get(planet)
                if lon_s is None or lon_s.empty:
                    continue
                lon_val = float(lon_s.iloc[idx])
                if not np.isfinite(lon_val):
                    continue

                for harmonic in cfg.get("harmonics", DEFAULT_HARMONICS):
                    for n_value in cfg.get("n_values", DEFAULT_N_VALUES):
                        for degree in cfg.get("degrees", DEFAULT_DEGREES):
                            base = float(harmonic) * int(degree) * float(n_value)
                            direct = base + float(harmonic) * lon_val
                            mirror = base + float(harmonic) * (360.0 - lon_val)
                            for mode, line_val in (("direct", direct), ("mirror", mirror)):
                                dist = abs(float(line_val) - close_now)
                                if best_abs is None or dist < best_abs:
                                    best_abs = dist
                                    best = (str(planet), mode, float(harmonic), float(n_value), int(degree))

            if best is not None:
                events.at[i, "anchor_identity"] = best
                if best not in line_map and best[0] in lon_map:
                    line_map[best] = line_from_identity_series(lon_map[best[0]], best)

    events = events[events["anchor_identity"].notna()].copy()
    if events.empty:
        raise RuntimeError("No events with resolved SR anchor identity.")

    for ident in set(events["anchor_identity"]):
        if isinstance(ident, tuple) and ident not in line_map:
            planet = ident[0]
            if planet in lon_map:
                line_map[ident] = line_from_identity_series(lon_map[planet], ident)

    has_line = [
        isinstance(ident, tuple)
        and len(ident) == 5
        and ident in line_map
        and len(line_map[ident]) == len(price)
        for ident in events["anchor_identity"]
    ]
    events = events[has_line].copy()
    if events.empty:
        raise RuntimeError("No events with buildable SR lines on price span.")

    rows = []
    for _, row in events.iterrows():
        idx_start = int(row["idx_start"])
        idx_end = int(row["idx_end"])
        idx_before = int(row["idx_before"])
        idx_after = int(row["idx_after"])
        idx_after72 = int(row["idx_after72"])

        ident = row["anchor_identity"]
        if not isinstance(ident, tuple) or len(ident) != 5:
            continue

        line_arr = line_map.get(ident)
        if line_arr is None:
            continue

        close_before = float(close_arr[idx_before])
        close_start = float(close_arr[idx_start])
        close_end = float(close_arr[idx_end])
        close_after = float(close_arr[idx_after])
        close_after72 = float(close_arr[idx_after72])

        if not all(np.isfinite([close_before, close_start, close_end, close_after, close_after72])):
            continue

        open_arr_val = float(open_arr[idx_start])
        high_arr_val = float(high_arr[idx_start])
        low_arr_val = float(low_arr[idx_start])

        line_start = float(line_arr[idx_start])
        line_end = float(line_arr[idx_end])
        line_before = float(line_arr[idx_before])
        line_after = float(line_arr[idx_after])

        if not all(np.isfinite([line_start, line_end, line_before, line_after])):
            continue

        ret_before = pct(close_before, close_start)
        ret_during = pct(close_start, close_end)
        ret_after = pct(close_end, close_after)
        ret_after72 = pct(close_end, close_after72)

        res_start = close_start - line_start
        res_end = close_end - line_end
        res_before = close_before - line_before
        res_after = close_after - line_after

        d_res_during = res_end - res_start
        d_res_after = res_after - res_end

        nearest = parse_sr_line_price_at_event(row.get("sr_snapshot_json"))
        sr_dist_abs = np.nan
        sr_dist_pct = np.nan
        if nearest is not None and np.isfinite(nearest) and close_start != 0:
            sr_dist_abs = abs(close_start - float(nearest))
            sr_dist_pct = sr_dist_abs / close_start

        cfg = row["sr_config_parsed"]
        zone = float(cfg.get("price_zone", 0.16))
        if ident[0] == "MOON":
            zone *= float(cfg.get("moon_factor", 1.8))
        zone = abs(zone)

        inter_before = window_interaction(
            low_arr, high_arr, close_arr, line_arr, idx_before, idx_start, zone
        )
        inter_during = window_interaction(
            low_arr, high_arr, close_arr, line_arr, idx_start, idx_end, zone
        )
        inter_after = window_interaction(
            low_arr, high_arr, close_arr, line_arr, idx_end, idx_after, zone
        )

        rank = rank_within_lookback(close_arr - line_arr, idx_start, int(args.lookback_hours))
        if np.isfinite(rank):
            nearest_side = "top" if rank >= 0.90 else ("bottom" if rank <= 0.10 else "none")
        else:
            nearest_side = "none"

        line_reversal_after = (
            (nearest_side == "top" and d_res_after < 0)
            or (nearest_side == "bottom" and d_res_after > 0)
        )
        line_reversal_event = (
            (res_start > 0 and res_end < 0)
            or (res_start < 0 and res_end > 0)
        )

        row_out = {
            "event_id": row.get("event_id"),
            "event_time_local": row.get("timestamp"),
            "event_time_utc": row.get("timestamp_utc"),
            "pair_key": canonical_pair(row.get("b1"), row.get("b2")),
            "b1": row.get("b1"),
            "b2": row.get("b2"),
            "aspect": row.get("aspect"),
            "timestamp_local": row.get("timestamp"),
            "timestamp_utc": row.get("timestamp_utc"),
            "shadbala_tag": row.get("shadbala_tag", "NA"),
            "moon_nakshatra": row.get("moon_nakshatra", "NA"),
            "duration_minutes": float(row.get("duration_minutes", 0.0)),
            "event_window_start_local": row.get("timestamp"),
            "event_window_end_local": row.get("event_end"),
            "event_window_duration_minutes": row.get("duration_minutes"),
            "before_hours": float(args.before_hours),
            "after_hours": float(args.after_hours),
            "after_hours_72": float(args.after_hours_72),
            "event_window_start_utc": row.get("timestamp_utc"),
            "event_window_end_utc": row.get("event_end_utc"),
            "before_start_utc": row.get("before_ts_utc"),
            "before_end_utc": row.get("timestamp_utc"),
            "during_start_utc": row.get("timestamp_utc"),
            "during_end_utc": row.get("event_end_utc"),
            "after_start_utc": row.get("event_end_utc"),
            "after_end_utc": row.get("after_ts_utc"),
            "after72_end_utc": row.get("after72_ts_utc"),
            "close_before_start": close_before,
            "close_before_end": close_start,
            "close_during_start": close_start,
            "close_during_end": close_end,
            "close_after_start": close_end,
            "close_after_end": close_after,
            "close_after72_end": close_after72,
            "open_start": open_arr_val,
            "high_start": high_arr_val,
            "low_start": low_arr_val,
            "ret_before_24h_pct": ret_before,
            "ret_before_dir": direction_from_change(ret_before),
            "ret_during_pct": ret_during,
            "ret_after_24h_pct": ret_after,
            "ret_after_24h_dir": direction_from_change(ret_after),
            "ret_after_72h_pct": ret_after72,
            "ret_after_72h_dir": direction_from_change(ret_after72),
            "y_dir_1d": row.get("y_dir_1d"),
            "y_sr_reaction": row.get("y_sr_reaction"),
            "delta_1d": row.get("delta_1d"),
            "delta_3d": row.get("delta_3d"),
            "delta_7d": row.get("delta_7d"),
            "shadbala_avg": row.get("avg_shadbala"),
            "sr_nearest_line_price": nearest,
            "sr_nearest_dist_pct_event": row.get("sr_nearest_dist_pct"),
            "sr_nearest_dist_abs_event": sr_dist_abs,
            "sr_nearest_dist_pct_event_abs": abs(sr_dist_pct) if np.isfinite(sr_dist_pct) else np.nan,
            "sr_above_flag": row.get("sr_above_flag"),
            "sr_cluster_count": row.get("sr_cluster_count"),
            "sr_gap_pct": row.get("sr_gap_pct"),
            "sr_bandwidth_pct": row.get("sr_bandwidth_pct"),
            "anchor_planet": ident[0],
            "anchor_mode": ident[1],
            "anchor_harmonic": float(ident[2]),
            "anchor_n_value": float(ident[3]),
            "anchor_degree": int(ident[4]),
            "anchor_identity_text": line_identity_text(ident),
            "anchor_line_start": line_start,
            "anchor_line_end": line_end,
            "anchor_line_before": line_before,
            "anchor_line_after": line_after,
            "anchor_line_dist_abs": abs(res_start),
            "anchor_line_dist_pct": abs(res_start) / close_start if close_start != 0 else np.nan,
            "anchor_line_dist_sign": 1 if res_start > 0 else (-1 if res_start < 0 else 0),
            "line_touch_before": inter_before["touched"],
            "line_touch_during": inter_during["touched"],
            "line_touch_after": inter_after["touched"],
            "line_min_dist_before": inter_before["min_distance"],
            "line_min_dist_during": inter_during["min_distance"],
            "line_min_dist_after": inter_after["min_distance"],
            "line_break_up_before": inter_before["broke_up"],
            "line_break_up_during": inter_during["broke_up"],
            "line_break_up_after": inter_after["broke_up"],
            "line_break_down_before": inter_before["broke_down"],
            "line_break_down_during": inter_during["broke_down"],
            "line_break_down_after": inter_after["broke_down"],
            "line_touch_bars_before": inter_before["bars"],
            "line_touch_bars_during": inter_during["bars"],
            "line_touch_bars_after": inter_after["bars"],
            "nearest_side_line": nearest_side,
            "line_residual_start": res_start,
            "line_residual_end": res_end,
            "line_residual_before": res_before,
            "line_residual_after": res_after,
            "delta_residual_during": d_res_during,
            "delta_residual_after": d_res_after,
            "line_reversal_after": int(bool(line_reversal_after)),
            "line_reversal_during": int(bool(line_reversal_event)),
        }
        rows.append(row_out)

    if not rows:
        raise RuntimeError("No rows generated after SR-anchor filtering.")

    out = pd.DataFrame(rows)
    out = out.sort_values(["event_time_utc", "pair_key"]).reset_index(drop=True)
    out.to_csv(args.output, index=False)

    print("Created rows:", len(out))
    print("Saved:", args.output)


if __name__ == "__main__":
    main()
