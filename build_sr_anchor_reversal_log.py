from __future__ import annotations

import argparse
import json
from typing import Any, Optional

import numpy as np
import pandas as pd


try:
    from pytz import timezone
except Exception:
    timezone = None


import swisseph as swe

from doctrine_config import configure_swiss_ephemeris_sidereal
from financial_astro_ephemeris import build_exact_longitude_map, fetch_planetary_longitude


IST = "Asia/Kolkata"
UTC = "UTC"
DOCTRINE_AYANAMSA = configure_swiss_ephemeris_sidereal(swe)
TOP_RANK = 0.90
BOTTOM_RANK = 0.10
DEFAULT_HARMONICS = (0.12, 0.18)
DEFAULT_N_VALUES = (1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8)
DEFAULT_DEGREES = (360, 180, 90, 45)
DEFAULT_PLANETS = ("SUN", "MOON", "VENUS", "MERCURY", "JUPITER", "SATURN", "MARS")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build an event-level log where the nearest canonical planetary SR line "
            "is used as a line-relative anchor and reversals are measured before/"
            "during/after each event."
        )
    )
    parser.add_argument(
        "--events",
        default=r"D:\PycharmProjects\astro_training_data_ipo_tokyo_18890211.parquet",
        help="Event parquet (JDML-style output with sr_snapshot_json).",
    )
    parser.add_argument(
        "--price",
        default=r"D:\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
        help="USDJPY OHLC parquet indexed by datetime.",
    )
    parser.add_argument(
        "--output",
        default=r"D:\PycharmProjects\sr_anchor_reversal_log_ipo_tokyo_18890211.csv",
        help="Event-level output CSV.",
    )
    parser.add_argument(
        "--summary",
        default=r"D:\PycharmProjects\sr_anchor_reversal_summary_ipo_tokyo_18890211.csv",
        help="Family-level summary CSV.",
    )
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--before-hours", type=float, default=24.0)
    parser.add_argument("--after-hours", type=float, default=24.0)
    parser.add_argument("--lookback-hours", type=int, default=12)
    parser.add_argument(
        "--include-natal",
        action="store_true",
        default=False,
        help="Include natal events instead of dropping is_natal=true rows.",
    )
    # Kept for compatibility with prior scripts; reserved for future filtering.
    parser.add_argument("--min-valid-window", type=int, default=8)
    return parser.parse_args()


def to_ist_series(ts: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(ts, errors="coerce")
    if parsed.dt.tz is None:
        if timezone is None:
            raise RuntimeError("pytz is required for timestamp conversion.")
        return parsed.dt.tz_localize(IST)
    return parsed.dt.tz_convert(IST)


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


def parse_identity_from_snapshot(value: Any) -> Optional[tuple]:
    snap = safe_json(value)
    if not isinstance(snap, dict):
        return None
    line = snap.get("nearest_line")
    if not isinstance(line, dict):
        return None
    ident = line.get("identity")
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


def parse_sr_config(value: Any) -> dict[str, Any]:
    cfg = safe_json(value)
    if not isinstance(cfg, dict):
        cfg = {}
    return {
        "planets": _parse_str_list(cfg.get("planets"), DEFAULT_PLANETS),
        "harmonics": _parse_float_list(cfg.get("harmonics"), DEFAULT_HARMONICS),
        "n_values": _parse_float_list(cfg.get("n_values"), DEFAULT_N_VALUES),
        "degrees": _parse_float_list(cfg.get("degrees"), DEFAULT_DEGREES),
        "price_zone": _parse_float(cfg.get("price_zone"), 0.16),
        "moon_factor": _parse_float(cfg.get("moon_factor"), 1.8),
        "epsilon": _parse_float(cfg.get("epsilon"), 0.30),
        "band_pct": _parse_float(cfg.get("band_pct"), 0.01),
    }


def _parse_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


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
            v = float(item)
            out.append(v)
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


def pct(a: float, b: float) -> float:
    if not np.isfinite(a) or not np.isfinite(b) or b == 0.0:
        return np.nan
    return (a - b) / b * 100.0


def direction_from_value(v: float, min_move_pct: float = 0.0) -> str:
    if not np.isfinite(v):
        return "NA"
    if v > min_move_pct:
        return "UP"
    if v < -min_move_pct:
        return "DOWN"
    return "FLAT"


def nearest_idx(ts: pd.DatetimeIndex, target: pd.Timestamp) -> int:
    if ts.empty:
        return -1
    return int(ts.get_indexer([target], method="nearest")[0])


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

    valid = np.isfinite(low_s) & np.isfinite(high_s) & np.isfinite(close_s) & np.isfinite(line_s)
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
        raise RuntimeError("No transit/interval events to process.")

    events["timestamp"] = to_ist_series(events["timestamp"])
    events = events[events["timestamp"].notna()].copy()

    price = pd.read_parquet(args.price).sort_index()
    if price.index.tz is None:
        price.index = price.index.tz_localize(UTC)
    price = price.tz_convert(IST)
    if price.empty:
        raise RuntimeError("Price data is empty.")

    # Intersect period first to avoid unneeded celestial computations.
    event_min = events["timestamp"].min() - pd.Timedelta(hours=args.before_hours)
    event_max = events["timestamp"].max() + pd.Timedelta(hours=args.after_hours)
    price = price[(price.index >= event_min) & (price.index <= event_max)].copy()
    if price.empty:
        raise RuntimeError("No price overlap with event windows.")

    events = events[(events["timestamp"] >= price.index.min()) & (events["timestamp"] <= price.index.max())].copy()
    if events.empty:
        raise RuntimeError("No events fall in price overlap range.")

    events["duration_minutes"] = pd.to_numeric(events["duration_minutes"], errors="coerce")
    events["duration_minutes"] = events["duration_minutes"].fillna(60.0)
    events["event_end"] = events["timestamp"] + pd.to_timedelta(events["duration_minutes"], unit="m")
    events["before_hours"] = float(args.before_hours)
    events["after_hours"] = float(args.after_hours)
    events["lookback_hours"] = int(args.lookback_hours)

    events["before_ts"] = events["timestamp"] - pd.Timedelta(hours=args.before_hours)
    events["after_ts"] = events["event_end"] + pd.Timedelta(hours=args.after_hours)
    events["anchor_identity"] = events["sr_snapshot_json"].apply(parse_identity_from_snapshot)

    # Fallback identity from sr_config if snapshot identity is missing.
    missing_mask = events["anchor_identity"].isna()
    if missing_mask.any():
        # keep all to avoid skipping rows that still may be recovered.
        print(f"Recovering identities for {int(missing_mask.sum())} events without sr_snapshot identity.")

    events["sr_config_parsed"] = events["sr_config_json"].apply(parse_sr_config)

    # Map event times to price indices.
    timestamps = price.index
    events["idx_start"] = timestamps.get_indexer(events["timestamp"].to_numpy(), method="nearest")
    events["idx_end"] = timestamps.get_indexer(events["event_end"].to_numpy(), method="nearest")
    events["idx_before"] = timestamps.get_indexer(events["before_ts"].to_numpy(), method="nearest")
    events["idx_after"] = timestamps.get_indexer(events["after_ts"].to_numpy(), method="nearest")

    # Filter rows with valid positional mapping.
    valid_pos = (
        (events["idx_start"] >= 0)
        & (events["idx_end"] >= 0)
        & (events["idx_before"] >= 0)
        & (events["idx_after"] >= 0)
        & (events["idx_after"] > events["idx_start"])
        & (events["idx_end"] >= events["idx_start"])
    )
    events = events[valid_pos].copy()
    if events.empty:
        raise RuntimeError("No events with valid price index mapping.")

    # Candidate planets from all identities + config.
    needed_planets = set(DEFAULT_PLANETS)
    for cfg in events["sr_config_parsed"]:
        needed_planets.update(cfg.get("planets", DEFAULT_PLANETS))
    for ident in events["anchor_identity"].dropna():
        needed_planets.add(str(ident[0]).upper())
    needed_planets = sorted(p for p in needed_planets if p)

    print("Building adaptive longitude map for", len(needed_planets), "planets...")
    lon_map = build_exact_longitude_map(
        planets=needed_planets,
        full_timestamps=timestamps,
        fetch_fn=fetch_planetary_longitude,
        astrology_method="sidereal",
        coordinate_system="geo",
    )

    # Build lines for every unique anchor identity.
    unique_identities = sorted({x for x in events["anchor_identity"] if x is not None})
    line_map: dict[tuple[str, str, float, float, int], np.ndarray] = {}
    for ident in unique_identities:
        planet = ident[0]
        if planet not in lon_map or lon_map[planet] is None or lon_map[planet].empty:
            continue
        line_map[ident] = line_from_identity_series(lon_map[planet], ident)

    # Resolve fallback identities by nearest computed line at event start.
    if missing_mask.any() or events["anchor_identity"].isna().any():
        unresolved = events["anchor_identity"].isna()
        if unresolved.any():
            print(f"Attempting config-based nearest-line fallback for {int(unresolved.sum())} events.")
            for i, row in events[unresolved].iterrows():
                cfg = row["sr_config_parsed"]
                idx = int(row["idx_start"])
                close_now = float(price.iloc[idx]["close"])
                if not np.isfinite(close_now):
                    continue

                best = None
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
                                    dist = abs(line_val - close_now)
                                    if best_abs is None or dist < best_abs:
                                        best_abs = dist
                                        best = (str(planet), mode, float(harmonic), float(n_value), int(degree))
                if best is not None:
                    events.at[i, "anchor_identity"] = best
                    line_map[best] = (
                        line_from_identity_series(lon_map[best[0]], best)
                        if best not in line_map
                        else line_map[best]
                    )

    # Re-filter for resolved anchor ids where line map exists.
    events = events[events["anchor_identity"].notna()].copy()
    if events.empty:
        raise RuntimeError("No events with resolved anchor identity.")

    events["pair_key"] = [
        "|".join(sorted((str(a).upper(), str(b).upper())))
        for a, b in zip(events["b1"], events["b2"], strict=False)
    ]

    # Ensure all unresolved identities are built.
    for ident in set(events["anchor_identity"]):
        if ident not in line_map:
            planet = ident[0]
            if planet in lon_map:
                line_map[ident] = line_from_identity_series(lon_map[planet], ident)

    # Keep only rows with available full line arrays.
    has_line = [
        ident in line_map and len(line_map[ident]) == len(price)
        for ident in events["anchor_identity"]
    ]
    events = events[has_line].copy()
    if events.empty:
        raise RuntimeError("No events with buildable anchor SR lines.")

    open_arr = pd.to_numeric(price["open"], errors="coerce").to_numpy(dtype=float)
    high_arr = pd.to_numeric(price["high"], errors="coerce").to_numpy(dtype=float)
    low_arr = pd.to_numeric(price["low"], errors="coerce").to_numpy(dtype=float)
    close_arr = pd.to_numeric(price["close"], errors="coerce").to_numpy(dtype=float)

    rows = []
    for _, row in events.iterrows():
        idx_start = int(row["idx_start"])
        idx_end = int(row["idx_end"])
        idx_before = int(row["idx_before"])
        idx_after = int(row["idx_after"])

        if idx_start < 0 or idx_end < 0 or idx_before < 0 or idx_after < 0:
            continue
        if idx_end < idx_start or idx_before > idx_start or idx_after < idx_end:
            continue

        cfg = row["sr_config_parsed"]
        ident = row["anchor_identity"]
        if not isinstance(ident, tuple) or len(ident) != 5:
            continue

        line_arr = line_map.get(ident)
        if line_arr is None:
            continue

        open_arr_idx = open_arr[idx_start]
        close_start = float(close_arr[idx_start])
        close_end = float(close_arr[idx_end])
        close_before = float(close_arr[idx_before])
        close_after = float(close_arr[idx_after])
        if not (
            np.isfinite(close_start)
            and np.isfinite(close_end)
            and np.isfinite(close_before)
            and np.isfinite(close_after)
        ):
            continue

        line_start = float(line_arr[idx_start])
        line_end = float(line_arr[idx_end])
        line_before = float(line_arr[idx_before])
        line_after = float(line_arr[idx_after])
        if not (
            np.isfinite(line_start)
            and np.isfinite(line_end)
            and np.isfinite(line_before)
            and np.isfinite(line_after)
        ):
            continue

        # Price behavior windows
        ret_before = pct(close_start, close_before)
        ret_during = pct(close_end, close_start)
        ret_after = pct(close_after, close_end)

        # Line-relative residuals
        res_start = close_start - line_start
        res_end = close_end - line_end
        res_before = close_before - line_before
        res_after = close_after - line_after
        d_res_during = res_end - res_start
        d_res_after = res_after - res_end

        line_residual_abs = abs(res_start)
        dist_pct = line_residual_abs / close_start if close_start != 0 else np.nan

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
            if rank >= TOP_RANK:
                nearest_side_line = "top"
            elif rank <= BOTTOM_RANK:
                nearest_side_line = "bottom"
            else:
                nearest_side_line = "none"
        else:
            nearest_side_line = "none"

        # Reversal labels
        line_reversal_after = (
            (nearest_side_line == "top" and d_res_after < 0)
            or (nearest_side_line == "bottom" and d_res_after > 0)
        )
        line_reversal_event = (
            (res_start > 0 and res_end < 0)
            or (res_start < 0 and res_end > 0)
        )
        dir_change_pre_post = (
            direction_from_value(ret_before) not in ("NA", "FLAT")
            and direction_from_value(ret_after) not in ("NA", "FLAT")
            and direction_from_value(ret_before) != direction_from_value(ret_after)
        )

        y_sr_reaction = str(row.get("y_sr_reaction", "NA"))
        row_out = {
            "event_id": row.get("event_id"),
            "timestamp": row.get("timestamp"),
            "event_end": row.get("event_end"),
            "before_hours": float(args.before_hours),
            "after_hours": float(args.after_hours),
            "lookback_hours": int(args.lookback_hours),
            "interval": row.get("interval"),
            "ticker": row.get("ticker"),
            "pair_key": row.get("pair_key"),
            "b1": row.get("b1"),
            "b2": row.get("b2"),
            "aspect": row.get("aspect"),
            "duration_minutes": float(row.get("duration_minutes", 0.0)),
            "anchor_planet": ident[0],
            "anchor_mode": ident[1],
            "anchor_harmonic": float(ident[2]),
            "anchor_n_value": float(ident[3]),
            "anchor_degree": int(ident[4]),
            "anchor_identity_text": line_identity_text(ident),
            "anchor_line_start": float(line_start),
            "anchor_line_end": float(line_end),
            "anchor_line_before": float(line_before),
            "anchor_line_after": float(line_after),
            "anchor_line_dist_abs": float(line_residual_abs),
            "anchor_line_dist_pct": float(dist_pct),
            "anchor_line_dist_sign": 1 if res_start > 0 else (-1 if res_start < 0 else 0),
            "nearest_sr_price_snapshot": parse_sr_line_price_at_event(row.get("sr_snapshot_json")),
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
            "nearest_side_line": nearest_side_line,
            "line_residual_start": float(res_start),
            "line_residual_end": float(res_end),
            "line_residual_before": float(res_before),
            "line_residual_after": float(res_after),
            "delta_residual_during": float(d_res_during),
            "delta_residual_after": float(d_res_after),
            "res_rank": rank,
            "close_before": float(close_before),
            "close_start": float(close_start),
            "close_end": float(close_end),
            "close_after": float(close_after),
            "open_start": float(open_arr_idx),
            "ret_before_pct": float(ret_before),
            "ret_during_pct": float(ret_during),
            "ret_after_pct": float(ret_after),
            "ret_before_dir": direction_from_value(ret_before),
            "ret_during_dir": direction_from_value(ret_during),
            "ret_after_dir": direction_from_value(ret_after),
            "dir_change_pre_post": int(bool(dir_change_pre_post)),
            "line_reversal_after": int(bool(line_reversal_after)),
            "line_reversal_during": int(bool(line_reversal_event)),
            "y_sr_reaction": y_sr_reaction,
            "shadbala_tag": row.get("shadbala_tag"),
            "avg_shadbala": row.get("avg_shadbala"),
            "closeness": row.get("closeness"),
            "retro_count": row.get("retro_count"),
            "sign_combo": row.get("sign_combo"),
            "relationship_score": row.get("relationship_score"),
            "idx_start": idx_start,
            "idx_end": idx_end,
            "idx_before": idx_before,
            "idx_after": idx_after,
            "sr_nearest_dist_pct": row.get("sr_nearest_dist_pct"),
            "sr_above_flag": row.get("sr_above_flag"),
            "sr_cluster_count": row.get("sr_cluster_count"),
            "sr_gap_pct": row.get("sr_gap_pct"),
            "sr_bandwidth_pct": row.get("sr_bandwidth_pct"),
        }
        rows.append(row_out)

    if not rows:
        raise RuntimeError("No rows generated after event/line filtering.")

    out = pd.DataFrame(rows)
    out = out.sort_values(["timestamp", "pair_key"]).reset_index(drop=True)
    out.to_csv(args.output, index=False)

    # Family summary for quick evidence checks.
    summary_rows = []
    for (pair_key, aspect), sub in out.groupby(["pair_key", "aspect"], dropna=False):
        top_mask = sub["nearest_side_line"].eq("top")
        bottom_mask = sub["nearest_side_line"].eq("bottom")
        summary_rows.append(
            {
                "pair_key": pair_key,
                "aspect": aspect,
                "events": int(len(sub)),
                "line_reversal_after_rate": float(pd.to_numeric(sub["line_reversal_after"], errors="coerce").mean()),
                "line_touch_after_rate": float(pd.to_numeric(sub["line_touch_after"], errors="coerce").mean()),
                "line_touch_during_rate": float(pd.to_numeric(sub["line_touch_during"], errors="coerce").mean()),
                "dir_change_pre_post_rate": float(pd.to_numeric(sub["dir_change_pre_post"], errors="coerce").mean()),
                "mean_ret_before_pct": float(pd.to_numeric(sub["ret_before_pct"], errors="coerce").mean()),
                "mean_ret_during_pct": float(pd.to_numeric(sub["ret_during_pct"], errors="coerce").mean()),
                "mean_ret_after_pct": float(pd.to_numeric(sub["ret_after_pct"], errors="coerce").mean()),
                "top_events": int(top_mask.sum()),
                "bottom_events": int(bottom_mask.sum()),
                "top_reversal_rate": float(
                    pd.to_numeric(sub.loc[top_mask, "line_reversal_after"], errors="coerce").mean()
                    if top_mask.any()
                    else np.nan
                ),
                "bottom_reversal_rate": float(
                    pd.to_numeric(sub.loc[bottom_mask, "line_reversal_after"], errors="coerce").mean()
                    if bottom_mask.any()
                    else np.nan
                ),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary = summary.sort_values(["events", "line_reversal_after_rate"], ascending=[False, False]).reset_index(drop=True)
    summary.to_csv(args.summary, index=False)

    print("Generated rows:", len(out))
    print("Saved:", args.output)
    print("Saved summary:", args.summary)


if __name__ == "__main__":
    main()
