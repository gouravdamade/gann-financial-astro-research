from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta, timezone as dt_timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

PROJECT_DIR = Path(r"C:\Users\ADMIN\Desktop\Trading_Algo\New folder")
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from adaptive_ephemeris_engine import build_adaptive_longitude_map
from planetary_sr_engine import DEFAULT_SR_PLANETS
from JDML4 import (
    TS,
    eph,
    swe,
    ReferenceChartEngine,
    get_house_of_planet,
    get_zodiac_sign,
    get_vedic_aspect_angles_for_planet,
    drishti_aspect_name_for_angle,
)


IST = "Asia/Kolkata"
UTC = "UTC"
REFERENCE_TZ_DEFAULT = "Asia/Tokyo"
REFERENCE_LAT_DEFAULT = 35.6762
REFERENCE_LON_DEFAULT = 139.6503
BASE_REFERENCE_DATE_DEFAULT = "1776-07-04"
BASE_REFERENCE_TIME_DEFAULT = "12:00"
BASE_REFERENCE_TZ_DEFAULT = "America/New_York"
BASE_REFERENCE_LAT_DEFAULT = 39.9526
BASE_REFERENCE_LON_DEFAULT = -75.1652
FIXED_TIMEZONE_OFFSETS = {
    "Asia/Kolkata": 330,
    "Asia/Tokyo": 540,
    "UTC": 0,
}
FAST_PLANETS = {"MOON", "MERCURY", "VENUS", "SUN", "MARS"}
SLOW_PLANETS = {"JUPITER", "SATURN"}
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
SR_TOUCH_PLANETS = tuple(DEFAULT_SR_PLANETS) + ("RAHU", "KETU", "URANUS", "NEPTUNE", "PLUTO")
HARD_ASPECTS = {"opposition", "opposition_orb", "square", "drishti_3", "drishti_4", "drishti_10"}
SOFT_ASPECTS = {"conjunction", "conjunction_orb", "trine", "drishti_5", "drishti_8", "drishti_9"}
RASHI_ASPECTS = {"rashi_movable", "rashi_fixed", "rashi_dual"}
ORB_ASPECTS = {"conjunction_orb", "square", "trine", "opposition_orb"}
ORB_SEXTILE_PAIRS = {
    frozenset({"JUPITER", "SATURN"}),
    frozenset({"JUPITER", "MARS"}),
    frozenset({"SATURN", "MARS"}),
}
MARKET_ORB_LIMITS = {
    "conjunction_orb": 1.5,
    "opposition_orb": 1.5,
    "square": 1.0,
    "trine": 1.0,
    "sextile": 0.5,
}
ASPECT_LABELS = {
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
    "rashi_movable": "Rashi Drishti (Movable)",
    "rashi_fixed": "Rashi Drishti (Fixed)",
    "rashi_dual": "Rashi Drishti (Dual)",
    "square": "Square",
    "trine": "Trine",
    "sextile": "Sextile",
}
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
TIGHT_ORB_DEG = 0.50
RASHI_SIGN_TYPES = {1: "movable", 2: "fixed", 3: "dual", 4: "movable", 5: "fixed", 6: "dual", 7: "movable", 8: "fixed", 9: "dual", 10: "movable", 11: "fixed", 12: "dual"}
MOVABLE_SIGNS = {1, 4, 7, 10}
FIXED_SIGNS = {2, 5, 8, 11}
DUAL_SIGNS = {3, 6, 9, 12}


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


def circular_average_degrees(values: list[float] | tuple[float, ...]) -> float:
    vals = [float(v) for v in values if np.isfinite(float(v))]
    if not vals:
        return np.nan
    radians = np.deg2rad(np.asarray(vals, dtype=np.float64))
    sin_sum = float(np.sin(radians).sum())
    cos_sum = float(np.cos(radians).sum())
    return float(np.degrees(np.arctan2(sin_sum, cos_sum)) % 360.0)


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


def _sign_index_from_longitude(lon: float) -> int:
    if not np.isfinite(float(lon)):
        return 0
    return int((float(lon) % 360.0) // 30.0) + 1


def get_rashi_aspected_signs(sign_index: int) -> set[int]:
    sign = int(sign_index)
    kind = RASHI_SIGN_TYPES.get(sign, "unknown")
    if kind == "movable":
        excluded = {(sign % 12) + 1}
        return set(FIXED_SIGNS) - excluded
    if kind == "fixed":
        excluded = {((sign - 2) % 12) + 1}
        return set(MOVABLE_SIGNS) - excluded
    if kind == "dual":
        return set(DUAL_SIGNS) - {sign}
    return set()


def rashi_aspect_targets_for_mode(mode: str) -> dict[int, set[int]]:
    mode = str(mode).strip().lower()
    if mode == "movable":
        return {s: get_rashi_aspected_signs(s) for s in MOVABLE_SIGNS}
    if mode == "fixed":
        return {s: get_rashi_aspected_signs(s) for s in FIXED_SIGNS}
    if mode == "dual":
        return {s: get_rashi_aspected_signs(s) for s in DUAL_SIGNS}
    return {s: set() for s in range(1, 13)}


def is_rashi_aspect_hit(lon1: float, lon2: float, rashi_mode: str) -> bool:
    sign1 = _sign_index_from_longitude(lon1)
    sign2 = _sign_index_from_longitude(lon2)
    if sign1 == 0 or sign2 == 0:
        return False
    target_map = rashi_aspect_targets_for_mode(rashi_mode)
    return (sign2 in target_map.get(sign1, set())) or (sign1 in target_map.get(sign2, set()))


def aspect_system_for_name(aspect_name: str) -> str:
    name = str(aspect_name or "").strip().lower()
    if name.startswith("rashi_"):
        return "rashi"
    if name in ORB_ASPECTS:
        return "orb"
    if name in {"conjunction", "opposition", "drishti_3", "drishti_4", "drishti_5", "drishti_8", "drishti_9", "drishti_10"}:
        return "graha"
    return "other"


def aspect_label_for_name(aspect_name: str) -> str:
    name = str(aspect_name or "").strip().lower()
    return ASPECT_LABELS.get(name, str(aspect_name or ""))


def get_vedic_aspects_for_planet(planet_name: str, aspect_mode: str = "graha") -> dict[str, dict[str, float]]:
    cfg: dict[str, dict[str, float]] = {}
    mode = str(aspect_mode).strip().lower()
    is_avg_body = parse_avg_members(planet_name) is not None
    if mode in {"graha", "both"} and not is_avg_body:
        for angle in get_vedic_aspect_angles_for_planet(planet_name):
            name = drishti_aspect_name_for_angle(angle)
            if name == "conjunction":
                orb = 3.0
            else:
                orb = 1.5
            cfg[name] = {"kind": "graha", "angle": float(angle), "orb": float(orb)}
    if mode == "orb":
        cfg["conjunction_orb"] = {"kind": "orb", "angle": 0.0, "orb": MARKET_ORB_LIMITS["conjunction_orb"]}
        cfg["square"] = {"kind": "orb", "angle": 90.0, "orb": MARKET_ORB_LIMITS["square"]}
        cfg["trine"] = {"kind": "orb", "angle": 120.0, "orb": MARKET_ORB_LIMITS["trine"]}
        cfg["opposition_orb"] = {"kind": "orb", "angle": 180.0, "orb": MARKET_ORB_LIMITS["opposition_orb"]}
    if mode in {"rashi", "both"}:
        cfg["rashi_movable"] = {"kind": "rashi", "mode": "movable", "orb": 1.0}
        cfg["rashi_fixed"] = {"kind": "rashi", "mode": "fixed", "orb": 1.0}
        cfg["rashi_dual"] = {"kind": "rashi", "mode": "dual", "orb": 1.0}
    return cfg
PLANET_KEYS = {
    "MERCURY": "MERCURY",
    "VENUS": "VENUS",
    "MARS": "MARS",
    "JUPITER": "JUPITER_BARYCENTER",
    "SATURN": "SATURN_BARYCENTER",
    "URANUS": "URANUS_BARYCENTER",
    "NEPTUNE": "NEPTUNE_BARYCENTER",
    "PLUTO": "PLUTO_BARYCENTER",
    "SUN": "SUN",
    "MOON": "MOON",
    "EARTH": "EARTH",
}
LONGITUDE_CACHE: dict[tuple[str, str, str, str, str, int], pd.Series] = {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a 72h-only touch log with one row per SR nearest-line/confluence touch "
            "inside the exact aspect window."
        )
    )
    parser.add_argument(
        "--events",
        default=r"C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211.parquet",
    )
    parser.add_argument(
        "--price",
        default=r"C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
    )
    parser.add_argument(
        "--output",
        default=r"C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h.csv",
    )
    parser.add_argument("--interval", default="1h")
    parser.add_argument(
        "--aspect-mode",
        default="graha",
        choices=("graha", "rashi", "both", "orb"),
        help="Aspect calculation mode: graha, rashi, both, or orb.",
    )
    parser.add_argument("--include-natal", action="store_true", default=False)
    parser.add_argument("--ipo-date", default="1889-02-11")
    parser.add_argument("--ipo-time", default="00:00")
    parser.add_argument("--reference-tz", default=REFERENCE_TZ_DEFAULT)
    parser.add_argument("--reference-lat", type=float, default=REFERENCE_LAT_DEFAULT)
    parser.add_argument("--reference-lon", type=float, default=REFERENCE_LON_DEFAULT)
    parser.add_argument("--quote-reference-label", default="JPY")
    parser.add_argument("--base-reference-label", default="USD")
    parser.add_argument("--base-reference-date", default=BASE_REFERENCE_DATE_DEFAULT)
    parser.add_argument("--base-reference-time", default=BASE_REFERENCE_TIME_DEFAULT)
    parser.add_argument("--base-reference-tz", default=BASE_REFERENCE_TZ_DEFAULT)
    parser.add_argument("--base-reference-lat", type=float, default=BASE_REFERENCE_LAT_DEFAULT)
    parser.add_argument("--base-reference-lon", type=float, default=BASE_REFERENCE_LON_DEFAULT)
    parser.add_argument(
        "--disable-base-reference",
        action="store_true",
        help="Do not add base-currency transit-to-natal fields.",
    )
    parser.add_argument(
        "--max-event-days",
        type=float,
        default=5.0,
        help="Exclude aspect events longer than this many days. Use 0 or a negative value for no duration cap.",
    )
    return parser.parse_args()


def merge_overlapping_event_windows(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return events.copy()

    work = (
        events.copy()
        .sort_values(
            ["pair_key", "aspect", "is_natal", "timestamp", "event_end", "duration_minutes"],
            ascending=[True, True, True, True, True, False],
        )
        .reset_index(drop=True)
    )
    merged: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for _, row in work.iterrows():
        row_dict = row.to_dict()
        row_start = pd.Timestamp(row_dict["timestamp"])
        row_end = pd.Timestamp(row_dict["event_end"])
        if current is None:
            current = row_dict
            continue

        same_key = (
            str(current.get("pair_key", "")) == str(row_dict.get("pair_key", ""))
            and str(current.get("aspect", "")) == str(row_dict.get("aspect", ""))
            and bool(current.get("is_natal", False)) == bool(row_dict.get("is_natal", False))
        )
        current_end = pd.Timestamp(current["event_end"])
        if same_key and row_start <= current_end:
            if row_end > current_end:
                current["event_end"] = row_end
            current_start = pd.Timestamp(current["timestamp"])
            if row_start < current_start:
                current["timestamp"] = row_start
                current_start = row_start
            current["duration_minutes"] = float((pd.Timestamp(current["event_end"]) - current_start).total_seconds() / 60.0)
            continue

        merged.append(current)
        current = row_dict

    if current is not None:
        merged.append(current)

    out = pd.DataFrame(merged)
    if out.empty:
        return out
    out["timestamp"] = to_ist_series(out["timestamp"])
    out["event_end"] = to_ist_series(out["event_end"])
    out["duration_minutes"] = (
        (out["event_end"] - out["timestamp"]).dt.total_seconds() / 60.0
    )
    return out.reset_index(drop=True)


def fetch_planetary_longitude_fast(
    planet_name: str,
    dates: pd.DatetimeIndex | pd.Series | list[pd.Timestamp],
    astrology_method: str = "tropical",
    coordinate_system: str = "geo",
) -> pd.Series:
    idx = pd.DatetimeIndex(dates)
    if idx.tz is None:
        idx = idx.tz_localize(IST)
    idx = idx.tz_convert(IST)
    if len(idx) == 0:
        return pd.Series(dtype=np.float64, index=idx)

    planet = normalize_body_name(planet_name)
    avg_members = parse_avg_members(planet)
    if avg_members == AVG_ALL_PLANETS:
        planet = AVG_ALL_LABEL
    elif avg_members:
        planet = f"AVG({', '.join(avg_members)})"
    cache_key = (
        planet,
        str(astrology_method).lower(),
        str(coordinate_system).lower(),
        str(idx[0]),
        str(idx[-1]),
        len(idx),
    )
    cached = LONGITUDE_CACHE.get(cache_key)
    if cached is not None:
        return cached.reindex(idx, method="ffill")

    if avg_members:
        member_series: list[pd.Series] = []
        for member in avg_members:
            try:
                member_series.append(
                    fetch_planetary_longitude_fast(
                        member,
                        idx,
                        astrology_method=astrology_method,
                        coordinate_system=coordinate_system,
                    )
                )
            except Exception:
                continue
        out = circular_average_series(member_series, idx).ffill()
        LONGITUDE_CACHE[cache_key] = out
        return out.reindex(idx, method="ffill")

    if planet in {"RAHU", "KETU"}:
        utc_idx = idx.tz_convert(UTC)
        longs: list[float] = []
        for local_ts, utc_ts in zip(idx, utc_idx, strict=False):
            try:
                hour = (
                    float(utc_ts.hour)
                    + (float(utc_ts.minute) / 60.0)
                    + (float(utc_ts.second) / 3600.0)
                    + (float(utc_ts.microsecond) / 3_600_000_000.0)
                )
                jd_ut = swe.julday(int(utc_ts.year), int(utc_ts.month), int(utc_ts.day), hour)
                flags = swe.FLG_SWIEPH | swe.FLG_SPEED
                if astrology_method == "sidereal":
                    flags |= swe.FLG_SIDEREAL
                node_res = swe.calc_ut(jd_ut, swe.TRUE_NODE, flags=flags)
                lon = float(node_res[0][0]) % 360.0
                if planet == "KETU":
                    lon = (lon + 180.0) % 360.0
                if astrology_method == "sidereal":
                    lon = (lon - swe.get_ayanamsa_ut(float(pd.Timestamp(local_ts).to_julian_date()))) % 360.0
                longs.append(lon)
            except Exception:
                longs.append(np.nan)
        out = pd.Series(longs, index=idx).ffill()
        LONGITUDE_CACHE[cache_key] = out
        return out.reindex(idx, method="ffill")
    if coordinate_system == "helio" and planet == "MOON":
        raise ValueError("Moon not available in heliocentric mode.")

    key = PLANET_KEYS.get(planet)
    if key is None:
        raise ValueError(f"Unknown planet: {planet_name}")

    observer = eph["sun"] if coordinate_system == "helio" else eph["earth"]
    astro_body = eph[key]
    utc_idx = idx.tz_convert(UTC)
    seconds = utc_idx.second.to_numpy(dtype=np.float64) + utc_idx.microsecond.to_numpy(dtype=np.float64) / 1e6
    ts = TS.utc(
        utc_idx.year.to_numpy(dtype=np.int32),
        utc_idx.month.to_numpy(dtype=np.int32),
        utc_idx.day.to_numpy(dtype=np.int32),
        utc_idx.hour.to_numpy(dtype=np.int32),
        utc_idx.minute.to_numpy(dtype=np.int32),
        seconds,
    )
    astrometric = observer.at(ts).observe(astro_body)
    _, ecl_lon, _ = astrometric.ecliptic_latlon(epoch="date")
    lon = np.asarray(ecl_lon.degrees, dtype=np.float64) % 360.0

    if coordinate_system == "geo" and astrology_method == "sidereal":
        julian_dates = idx.to_julian_date().to_numpy(dtype=np.float64)
        ayanamsa = np.array([swe.get_ayanamsa_ut(float(jd)) for jd in julian_dates], dtype=np.float64)
        lon = (lon - ayanamsa) % 360.0

    out = pd.Series(lon, index=idx).ffill()
    LONGITUDE_CACHE[cache_key] = out
    return out.reindex(idx, method="ffill")


def safe_json(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return {}
    if isinstance(value, float) and not np.isfinite(value):
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {}


def _parse_float_list(value: Any, default: tuple[float, ...]) -> tuple[float, ...]:
    if isinstance(value, str):
        value = safe_json(value)
    if not isinstance(value, (list, tuple)):
        return default
    out: list[float] = []
    for item in value:
        try:
            out.append(float(item))
        except Exception:
            continue
    return tuple(out) if out else default


def _parse_int_list(value: Any, default: tuple[int, ...]) -> tuple[int, ...]:
    if isinstance(value, str):
        value = safe_json(value)
    if not isinstance(value, (list, tuple)):
        return default
    out: list[int] = []
    for item in value:
        try:
            out.append(int(float(item)))
        except Exception:
            continue
    return tuple(out) if out else default


def parse_sr_config(value: Any) -> dict[str, Any]:
    cfg = safe_json(value)
    if not isinstance(cfg, dict):
        cfg = {}
    return {
        "planets": tuple(SR_TOUCH_PLANETS) + (AVG_ALL_LABEL,),
        "harmonics": _parse_float_list(cfg.get("harmonics"), (0.12, 0.18)),
        "n_values": _parse_float_list(cfg.get("n_values"), (1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8)),
        "degrees": _parse_int_list(cfg.get("degrees"), (360, 180, 90, 45)),
        "epsilon": float(cfg.get("epsilon", 0.30)),
        "price_zone": float(cfg.get("price_zone", 0.16)),
        "moon_factor": float(cfg.get("moon_factor", 1.8)),
        "band_pct": float(cfg.get("band_pct", 0.01)),
    }


def to_ist_series(ts: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(ts, errors="coerce")
    if parsed.dt.tz is None:
        parsed = parsed.dt.tz_localize(IST)
    return parsed.dt.tz_convert(IST)


def reference_timezone(tz_name: str) -> dt_timezone | ZoneInfo:
    tz_key = str(tz_name or "").strip()
    if tz_key in FIXED_TIMEZONE_OFFSETS:
        return dt_timezone(timedelta(minutes=int(FIXED_TIMEZONE_OFFSETS[tz_key])))
    return ZoneInfo(tz_key)


def parse_reference_datetime(date_text: str, time_text: str, tz_name: str) -> pd.Timestamp:
    ref = pd.Timestamp(f"{str(date_text).strip()} {str(time_text).strip()}")
    source_tz = reference_timezone(tz_name)
    ist_tz = dt_timezone(timedelta(minutes=FIXED_TIMEZONE_OFFSETS["Asia/Kolkata"]))
    if ref.tzinfo is None:
        ref = ref.tz_localize(source_tz)
    else:
        ref = ref.tz_convert(source_tz)
    return ref.tz_convert(ist_tz)


def pct(c0: float, c1: float) -> float:
    if not np.isfinite(c0) or not np.isfinite(c1) or c0 == 0.0:
        return np.nan
    return (c1 - c0) / c0 * 100.0


def direction_from_change(change: float) -> str:
    if not np.isfinite(change):
        return "NA"
    if change > 0:
        return "UP"
    if change < 0:
        return "DOWN"
    return "FLAT"


def canonical_pair(a: Any, b: Any) -> str:
    left = str(a).strip().upper()
    right = str(b).strip().upper()
    return f"{left}|{right}" if left <= right else f"{right}|{left}"


def angular_separation(a: float, b: float) -> float:
    raw = abs((float(a) - float(b)) % 360.0)
    return raw if raw <= 180.0 else 360.0 - raw


def signed_circular_delta(curr: float, prev: float) -> float:
    return float(((float(curr) - float(prev) + 540.0) % 360.0) - 180.0)


def identity_to_dict(identity: tuple[str, str, float, float, int]) -> dict[str, Any]:
    planet, mode, harmonic, n_value, degree = identity
    return {
        "planet": str(planet),
        "mode": str(mode),
        "harmonic": float(harmonic),
        "n_value": float(n_value),
        "degree": int(degree),
    }


def build_aspect_regime_map(
    events: pd.DataFrame,
    active_bar_indices: list[int],
    price_index: pd.DatetimeIndex,
) -> dict[int, dict[str, Any]]:
    if events.empty or not active_bar_indices:
        return {}

    event_ranges: list[tuple[int, int, str]] = []
    for pos, row in events.reset_index(drop=True).iterrows():
        start_idx = int(row.get("idx_start", -1))
        end_idx = int(row.get("idx_end", -1))
        if start_idx < 0 or end_idx < 0:
            continue
        event_key = str(row.get("event_id", "")).strip()
        if not event_key:
            event_key = "|".join(
                [
                    str(row.get("pair_key", "")),
                    str(row.get("aspect", "")),
                    pd.Timestamp(row.get("timestamp")).isoformat(),
                    pd.Timestamp(row.get("event_end")).isoformat(),
                    str(pos),
                ]
            )
        event_ranges.append((min(start_idx, end_idx), max(start_idx, end_idx), event_key))

    regime_members: dict[int, list[int]] = {}
    meta_by_bar: dict[int, dict[str, Any]] = {}
    prev_signature: tuple[str, ...] | None = None
    prev_bar_idx: int | None = None
    regime_id = -1

    for full_idx in active_bar_indices:
        active_events = tuple(
            sorted(
                {
                    event_key
                    for start_idx, end_idx, event_key in event_ranges
                    if start_idx <= int(full_idx) <= end_idx
                }
            )
        )
        if not active_events:
            prev_signature = None
            prev_bar_idx = None
            continue

        if (
            prev_signature != active_events
            or prev_bar_idx is None
            or int(full_idx) != int(prev_bar_idx) + 1
        ):
            regime_id += 1
            regime_members[regime_id] = []

        regime_members[regime_id].append(int(full_idx))
        meta_by_bar[int(full_idx)] = {
            "aspect_regime_id": int(regime_id),
            "aspect_regime_active_count": int(len(active_events)),
            "aspect_regime_signature": " || ".join(active_events),
        }
        prev_signature = active_events
        prev_bar_idx = int(full_idx)

    for current_regime_id, members in regime_members.items():
        if not members:
            continue
        start_ts = price_index[int(members[0])]
        end_ts = price_index[int(members[-1])]
        for full_idx in members:
            meta = meta_by_bar.get(int(full_idx))
            if meta is None:
                continue
            meta["aspect_regime_start_local"] = start_ts
            meta["aspect_regime_end_local"] = end_ts

    return meta_by_bar


def gate_touches_by_regime(out: pd.DataFrame) -> pd.DataFrame:
    if out.empty or "touch_kind" not in out.columns or "aspect_regime_id" not in out.columns:
        return out

    gated_kinds = {"confluence", "nearest_line"}
    subset = out[out["touch_kind"].astype(str).str.lower().isin(gated_kinds)].copy()
    if subset.empty:
        return out

    subset["aspect_regime_id"] = pd.to_numeric(subset["aspect_regime_id"], errors="coerce")
    subset["touch_time_local"] = pd.to_datetime(subset["touch_time_local"], errors="coerce")
    subset["touch_distance_abs"] = pd.to_numeric(subset["touch_distance_abs"], errors="coerce").fillna(float("inf"))
    subset["edge_score"] = pd.to_numeric(subset["ret_after_72h_pct"], errors="coerce").abs().fillna(float("-inf"))

    gated = (
        subset.dropna(subset=["aspect_regime_id", "touch_time_local"])
        .sort_values(
            ["touch_kind", "aspect_regime_id", "touch_time_local", "touch_distance_abs", "edge_score"],
            ascending=[True, True, True, True, False],
        )
        .drop_duplicates(subset=["touch_kind", "aspect_regime_id"], keep="first")
    )
    confluence_regimes = set(
        pd.to_numeric(
            gated.loc[gated["touch_kind"].astype(str).str.lower() == "confluence", "aspect_regime_id"],
            errors="coerce",
        ).dropna().astype(int).tolist()
    )
    if confluence_regimes:
        nearest_mask = gated["touch_kind"].astype(str).str.lower() == "nearest_line"
        same_regime_mask = pd.to_numeric(gated["aspect_regime_id"], errors="coerce").isin(confluence_regimes)
        gated = gated[~(nearest_mask & same_regime_mask)].copy()

    subset_without_regime = subset[subset["aspect_regime_id"].isna()].copy()
    remainder = out[~out["touch_kind"].astype(str).str.lower().isin(gated_kinds)].copy()
    merged = pd.concat([remainder, subset_without_regime, gated], ignore_index=True, sort=False)
    return merged


def gate_repeated_touches_by_price_band(out: pd.DataFrame) -> pd.DataFrame:
    if out.empty or "touch_time_local" not in out.columns or "touch_price" not in out.columns:
        return out

    work = out.copy()
    work["touch_time_local"] = pd.to_datetime(work["touch_time_local"], errors="coerce")
    work["touch_price"] = pd.to_numeric(work["touch_price"], errors="coerce")
    work["touch_zone"] = pd.to_numeric(work.get("touch_zone"), errors="coerce")
    work["edge_score"] = pd.to_numeric(work.get("ret_after_72h_pct"), errors="coerce").abs()
    work = work.sort_values(["touch_time_local", "touch_distance_abs", "edge_score"], ascending=[True, True, False]).reset_index(drop=True)

    keep_rows: list[int] = []
    last_kept_price: float | None = None
    last_kept_zone: float | None = None

    for row_idx, row in work.iterrows():
        price = row.get("touch_price")
        zone = row.get("touch_zone")
        if not np.isfinite(float(price)):
            keep_rows.append(int(row_idx))
            continue

        zone_f = float(zone) if np.isfinite(float(zone)) else 0.0
        if last_kept_price is None:
            keep_rows.append(int(row_idx))
            last_kept_price = float(price)
            last_kept_zone = zone_f
            continue

        rearm_band = max(float(last_kept_zone or 0.0), zone_f)
        if abs(float(price) - float(last_kept_price)) <= rearm_band:
            continue

        keep_rows.append(int(row_idx))
        last_kept_price = float(price)
        last_kept_zone = zone_f

    return work.iloc[keep_rows].copy().reset_index(drop=True)


def gate_one_touch_per_event(out: pd.DataFrame) -> pd.DataFrame:
    if out.empty or "event_id" not in out.columns:
        return out

    work = out.copy()
    work["touch_time_local"] = pd.to_datetime(work["touch_time_local"], errors="coerce")
    work["touch_distance_abs"] = pd.to_numeric(work["touch_distance_abs"], errors="coerce").fillna(float("inf"))
    work["edge_score"] = pd.to_numeric(work.get("ret_after_72h_pct"), errors="coerce").abs().fillna(float("-inf"))
    work["_touch_priority"] = np.where(work["touch_kind"].astype(str).str.lower().eq("confluence"), 0, 1)

    has_event = work["event_id"].notna() & work["event_id"].astype(str).str.strip().ne("")
    with_event = (
        work[has_event]
        .sort_values(
            ["event_id", "_touch_priority", "touch_time_local", "touch_distance_abs", "edge_score"],
            ascending=[True, True, True, True, False],
        )
        .drop_duplicates(subset=["event_id"], keep="first")
    )
    without_event = work[~has_event].copy()
    merged = pd.concat([with_event, without_event], ignore_index=True, sort=False)
    return merged.drop(columns=["_touch_priority"], errors="ignore")


def identity_to_text(identity: tuple[str, str, float, float, int] | None) -> str:
    if identity is None:
        return ""
    planet, mode, harmonic, n_value, degree = identity
    return f"{planet}|{mode}|h{harmonic:g}|n{n_value:g}|d{int(degree)}"


def bar_distance(level: float, high: float, low: float, close: float) -> float:
    return float(min(abs(high - level), abs(low - level), abs(close - level)))


def build_identity_frame(cfg: dict[str, Any]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for planet in cfg["planets"]:
        for harmonic in cfg["harmonics"]:
            for n_value in cfg["n_values"]:
                for degree in cfg["degrees"]:
                    base = float(harmonic) * float(n_value) * float(degree)
                    records.append(
                        {
                            "planet": str(planet),
                            "mode": "direct",
                            "harmonic": float(harmonic),
                            "n_value": float(n_value),
                            "degree": int(degree),
                            "base": base,
                            "mirror": False,
                        }
                    )
                    records.append(
                        {
                            "planet": str(planet),
                            "mode": "mirror",
                            "harmonic": float(harmonic),
                            "n_value": float(n_value),
                            "degree": int(degree),
                            "base": base,
                            "mirror": True,
                        }
                    )
    out = pd.DataFrame.from_records(records)
    out["identity"] = [
        (r["planet"], r["mode"], float(r["harmonic"]), float(r["n_value"]), int(r["degree"]))
        for _, r in out.iterrows()
    ]
    out["identity_text"] = out["identity"].map(identity_to_text)
    return out.reset_index(drop=True)


def build_reference_context(
    *,
    date_text: str,
    time_text: str,
    tz_name: str,
    lat: float,
    lon: float,
    planets: tuple[str, ...],
    label: str,
) -> dict[str, Any]:
    source_tz = reference_timezone(tz_name)
    ist_tz = dt_timezone(timedelta(minutes=FIXED_TIMEZONE_OFFSETS["Asia/Kolkata"]))
    ref_dt_source = pd.Timestamp(f"{str(date_text).strip()} {str(time_text).strip()}")
    if ref_dt_source.tzinfo is None:
        ref_dt_source = ref_dt_source.tz_localize(source_tz)
    else:
        ref_dt_source = ref_dt_source.tz_convert(source_tz)
    ref_dt = ref_dt_source.tz_convert(ist_tz)
    engine = ReferenceChartEngine(
        chart_type="ipo",
        dt_ist=ref_dt.to_pydatetime(),
        lat=float(lat),
        lon=float(lon),
    )
    engine.compute_all()
    natal_longitudes: dict[str, float] = {}
    natal_signs: dict[str, str] = {}
    natal_houses: dict[str, int | None] = {}
    for planet in planets:
        planet_key = normalize_body_name(planet)
        avg_members = parse_avg_members(planet_key)
        if avg_members:
            values = [
                float(engine.planets_lon.get(member))
                for member in avg_members
                if member in engine.planets_lon and np.isfinite(float(engine.planets_lon.get(member)))
            ]
            if not values:
                continue
            lon_f = circular_average_degrees(values)
            store_key = AVG_ALL_LABEL if avg_members == AVG_ALL_PLANETS else planet_key
        else:
            lon = engine.planets_lon.get(planet_key)
            if lon is None or not np.isfinite(float(lon)):
                continue
            lon_f = float(lon)
            store_key = planet_key
        natal_longitudes[store_key] = lon_f
        natal_signs[store_key] = str(get_zodiac_sign(lon_f))
        natal_houses[store_key] = get_house_of_planet(lon_f, engine.houses)
    return {
        "reference_label": str(label),
        "reference_dt": ref_dt,
        "reference_tz": str(IST),
        "reference_source_dt": ref_dt_source,
        "reference_source_tz": str(tz_name),
        "reference_lat": float(lat),
        "reference_lon": float(lon),
        "longitudes": natal_longitudes,
        "signs": natal_signs,
        "houses": natal_houses,
    }


def build_natal_context(args: argparse.Namespace, planets: tuple[str, ...]) -> dict[str, Any]:
    return build_reference_context(
        date_text=args.ipo_date,
        time_text=args.ipo_time,
        tz_name=args.reference_tz,
        lat=float(args.reference_lat),
        lon=float(args.reference_lon),
        planets=planets,
        label=str(args.quote_reference_label),
    )


def prefix_dict(data: dict[str, Any], prefix: str) -> dict[str, Any]:
    return {f"{prefix}{key}": value for key, value in data.items()}


def build_user_facing_touch_log(out: pd.DataFrame) -> pd.DataFrame:
    export_df = out.copy()
    utc_cols = [col for col in export_df.columns if str(col).lower().endswith("_utc")]
    if utc_cols:
        export_df = export_df.drop(columns=utc_cols, errors="ignore")
    rename_map = {
        "tn_reference_dt_local": "reference_time_ist",
        "tn_reference_tz": "reference_time_tz",
        "tn_reference_dt_source": "source_reference_time",
        "tn_reference_source_tz": "source_reference_tz",
        "base_tn_reference_dt_local": "base_reference_time_ist",
        "base_tn_reference_tz": "base_reference_time_tz",
        "base_tn_reference_dt_source": "base_source_reference_time",
        "base_tn_reference_source_tz": "base_source_reference_tz",
    }
    present_map = {src: dst for src, dst in rename_map.items() if src in export_df.columns}
    if present_map:
        export_df = export_df.rename(columns=present_map)
    return export_df


def natal_attrs_for_planet(planet: str | None, natal_ctx: dict[str, Any]) -> dict[str, Any]:
    planet_key = normalize_body_name(planet)
    avg_members = parse_avg_members(planet_key)
    if avg_members == AVG_ALL_PLANETS:
        planet_key = AVG_ALL_LABEL
    house = natal_ctx["houses"].get(planet_key)
    return {
        "lon": float(natal_ctx["longitudes"].get(planet_key, np.nan)),
        "sign": str(natal_ctx["signs"].get(planet_key, "")),
        "house": int(house) if house is not None and pd.notna(house) else np.nan,
        "kendra_flag": int(house in KENDRA_HOUSES) if house is not None else 0,
        "trikona_flag": int(house in TRIKONA_HOUSES) if house is not None else 0,
        "dusthana_flag": int(house in DUSTHANA_HOUSES) if house is not None else 0,
    }


def build_retrograde_flags(lon_map: dict[str, pd.Series], planets: list[str]) -> dict[str, np.ndarray]:
    retro_map: dict[str, np.ndarray] = {}
    for planet in planets:
        arr = lon_map[planet].to_numpy(dtype=np.float64)
        n = len(arr)
        if n == 0:
            retro_map[planet] = np.zeros(0, dtype=bool)
            continue
        if n == 1:
            retro_map[planet] = np.zeros(1, dtype=bool)
            continue
        diffs = np.array([signed_circular_delta(arr[i], arr[i - 1]) for i in range(1, n)], dtype=np.float64)
        speed = np.empty(n, dtype=np.float64)
        speed[0] = diffs[0]
        speed[-1] = diffs[-1]
        if n > 2:
            speed[1:-1] = 0.5 * (diffs[:-1] + diffs[1:])
        retro_map[planet] = speed < 0.0
    return retro_map


def build_natal_feature_builder(
    lon_map: dict[str, pd.Series],
    cfg: dict[str, Any],
    natal_ctx: dict[str, Any],
    aspect_mode: str,
):
    planets = list(cfg["planets"])
    lon_matrix = np.vstack([lon_map[planet].to_numpy(dtype=np.float64) for planet in planets])
    retro_flags = build_retrograde_flags(lon_map, planets)
    retro_matrix = np.vstack([retro_flags[planet].astype(bool) for planet in planets])
    natal_targets = [
        {
            "planet": planet,
            "lon": float(lon),
            "sign": str(natal_ctx["signs"].get(planet, "")),
            "house": natal_ctx["houses"].get(planet),
        }
        for planet, lon in natal_ctx["longitudes"].items()
        if planet in planets and np.isfinite(float(lon))
    ]
    natal_aspects_by_planet = {
        planet: get_vedic_aspects_for_planet(planet, aspect_mode=aspect_mode)
        for planet in planets
    }
    cache: dict[int, dict[str, Any]] = {}

    def compute(idx: int, touch_planets: set[str]) -> dict[str, Any]:
        if idx not in cache:
            hits: list[dict[str, Any]] = []
            for p_idx, transit_planet in enumerate(planets):
                transit_lon = float(lon_matrix[p_idx, idx])
                if not np.isfinite(transit_lon):
                    continue
                transit_retro = int(bool(retro_matrix[p_idx, idx]))
                transit_aspects = natal_aspects_by_planet.get(transit_planet, {})
                for target in natal_targets:
                    sep = angular_separation(transit_lon, target["lon"])
                    for aspect_name, aspect_cfg in transit_aspects.items():
                        kind = str(aspect_cfg.get("kind", "graha"))
                        if kind == "rashi":
                            if not is_rashi_aspect_hit(
                                transit_lon,
                                target["lon"],
                                str(aspect_cfg.get("mode", "")),
                            ):
                                continue
                            orb_deg = 0.0
                            score = 1.0
                        else:
                            orb_deg = abs(sep - float(aspect_cfg["angle"]))
                            orb_limit = float(aspect_cfg["orb"])
                            if orb_deg > orb_limit:
                                continue
                            score = smooth_orb_strength(orb_deg, orb_limit)
                            bphs_strength = bphs_quarter_strength(orb_deg, orb_limit)
                        hits.append(
                            {
                                "transit_planet": transit_planet,
                                "natal_planet": target["planet"],
                                "aspect": aspect_name,
                                "orb_deg": float(orb_deg),
                                "orb_limit_deg": float(aspect_cfg.get("orb", 0.0)),
                                "score": float(score),
                                "bphs_strength": float(bphs_strength if kind != "rashi" else 1.0),
                                "bphs_virupa": float(bphs_virupa_from_strength(bphs_strength if kind != "rashi" else 1.0)),
                                "transit_retro": transit_retro,
                                "transit_lon": float(transit_lon),
                                "transit_sign": str(get_zodiac_sign(transit_lon)),
                                "natal_lon": float(target["lon"]),
                                "natal_sign": target["sign"],
                                "natal_house": int(target["house"]) if target["house"] is not None else np.nan,
                            }
                        )
            cache[idx] = {"hits": hits}

        hits = cache[idx]["hits"]
        primary = None
        if hits:
            primary = max(
                hits,
                key=lambda hit: (
                    float(hit["score"]),
                    int(hit["transit_planet"] in touch_planets),
                    -float(hit["orb_deg"]),
                    str(hit["aspect"]),
                    str(hit["transit_planet"]),
                    str(hit["natal_planet"]),
                ),
            )

        def summarize_for_touch(planet: str | None) -> dict[str, Any]:
            planet_key = str(planet or "").strip().upper()
            if not planet_key:
                return {
                    "active_count": 0,
                    "best_aspect": "",
                    "best_natal_target": "",
                    "min_orb_deg": np.nan,
                    "score": 0.0,
                    "bphs_strength": 0.0,
                }
            sub = [hit for hit in hits if hit["transit_planet"] == planet_key]
            if not sub:
                return {
                    "active_count": 0,
                    "best_aspect": "",
                    "best_natal_target": "",
                    "min_orb_deg": np.nan,
                    "score": 0.0,
                    "bphs_strength": 0.0,
                }
            best = max(sub, key=lambda hit: (float(hit["score"]), -float(hit["orb_deg"])))
            return {
                "active_count": int(len(sub)),
                "best_aspect": str(best["aspect"]),
                "best_natal_target": str(best["natal_planet"]),
                "min_orb_deg": float(min(float(hit["orb_deg"]) for hit in sub)),
                "score": float(sum(float(hit["score"]) for hit in sub)),
                "bphs_strength": float(sum(float(hit["bphs_strength"]) for hit in sub)),
            }

        out = {
            "tn_primary_transit_planet": str(primary["transit_planet"]) if primary else "",
            "tn_primary_natal_planet": str(primary["natal_planet"]) if primary else "",
            "tn_primary_aspect": str(primary["aspect"]) if primary else "",
            "tn_primary_orb_deg": float(primary["orb_deg"]) if primary else np.nan,
            "tn_primary_orb_limit_deg": float(primary["orb_limit_deg"]) if primary else np.nan,
            "tn_primary_score": float(primary["score"]) if primary else 0.0,
            "tn_primary_bphs_strength": float(primary["bphs_strength"]) if primary else 0.0,
            "tn_primary_bphs_virupa": float(primary["bphs_virupa"]) if primary else 0.0,
            "tn_primary_natal_sign": str(primary["natal_sign"]) if primary else "",
            "tn_primary_natal_house": int(primary["natal_house"]) if primary and pd.notna(primary["natal_house"]) else np.nan,
            "tn_primary_transit_retro": int(primary["transit_retro"]) if primary else 0,
            "tn_primary_is_touch_planet_flag": int(primary["transit_planet"] in touch_planets) if primary else 0,
            "tn_active_count": int(len(hits)),
            "tn_active_tight_count": int(sum(float(hit["orb_deg"]) <= TIGHT_ORB_DEG for hit in hits)),
            "tn_active_fast_count": int(sum(hit["transit_planet"] in FAST_PLANETS for hit in hits)),
            "tn_active_slow_count": int(sum(hit["transit_planet"] in SLOW_PLANETS for hit in hits)),
            "tn_active_hard_count": int(sum(hit["aspect"] in HARD_ASPECTS for hit in hits)),
            "tn_active_soft_count": int(sum(hit["aspect"] in SOFT_ASPECTS for hit in hits)),
            "tn_active_rashi_count": int(sum(hit["aspect"] in RASHI_ASPECTS for hit in hits)),
            "tn_active_conj_count": int(sum(hit["aspect"] == "conjunction" for hit in hits)),
            "tn_score_total": float(sum(float(hit["score"]) for hit in hits)),
            "tn_score_fast": float(sum(float(hit["score"]) for hit in hits if hit["transit_planet"] in FAST_PLANETS)),
            "tn_score_slow": float(sum(float(hit["score"]) for hit in hits if hit["transit_planet"] in SLOW_PLANETS)),
            "tn_score_hard": float(sum(float(hit["score"]) for hit in hits if hit["aspect"] in HARD_ASPECTS)),
            "tn_score_soft": float(sum(float(hit["score"]) for hit in hits if hit["aspect"] in SOFT_ASPECTS)),
            "tn_score_rashi": float(sum(float(hit["score"]) for hit in hits if hit["aspect"] in RASHI_ASPECTS)),
            "tn_score_touch_planets": float(sum(float(hit["score"]) for hit in hits if hit["transit_planet"] in touch_planets)),
            "tn_bphs_total": float(sum(float(hit["bphs_strength"]) for hit in hits)),
            "tn_hits_json": json.dumps(hits, ensure_ascii=True),
        }
        return out, summarize_for_touch

    return compute


def build_bar_analyzer(price: pd.DataFrame, lon_map: dict[str, pd.Series], cfg: dict[str, Any]):
    identity_frame = build_identity_frame(cfg)
    planets = list(cfg["planets"])
    planet_to_idx = {planet: i for i, planet in enumerate(planets)}
    planet_idx = identity_frame["planet"].map(planet_to_idx).to_numpy(dtype=np.int16)
    harmonic_arr = identity_frame["harmonic"].to_numpy(dtype=np.float64)
    base_arr = identity_frame["base"].to_numpy(dtype=np.float64)
    mirror_arr = identity_frame["mirror"].to_numpy(dtype=bool)
    planet_arr = identity_frame["planet"].to_numpy()
    identity_arr = identity_frame["identity"].tolist()
    identity_text_arr = identity_frame["identity_text"].to_numpy()
    lon_matrix = np.vstack([lon_map[planet].to_numpy(dtype=np.float64) for planet in planets])

    open_arr = price["open"].to_numpy(dtype=np.float64)
    high_arr = price["high"].to_numpy(dtype=np.float64)
    low_arr = price["low"].to_numpy(dtype=np.float64)
    close_arr = price["close"].to_numpy(dtype=np.float64)

    price_zone = float(cfg["price_zone"])
    moon_factor = float(cfg["moon_factor"])
    epsilon = float(cfg["epsilon"])

    cache: dict[int, list[dict[str, Any]]] = {}

    def compute(idx: int) -> list[dict[str, Any]]:
        if idx in cache:
            return cache[idx]

        high = float(high_arr[idx])
        low = float(low_arr[idx])
        close = float(close_arr[idx])
        if not np.isfinite(high) or not np.isfinite(low) or not np.isfinite(close):
            cache[idx] = []
            return cache[idx]

        lon_values = lon_matrix[planet_idx, idx]
        src_lon = np.where(mirror_arr, 360.0 - lon_values, lon_values)
        line_values = base_arr + harmonic_arr * src_lon
        dist_close = np.abs(line_values - close)
        dist_bar = np.minimum(np.minimum(np.abs(line_values - high), np.abs(line_values - low)), np.abs(line_values - close))

        touches: list[dict[str, Any]] = []

        nearest_ix = int(np.argmin(dist_close))
        nearest_identity = identity_arr[nearest_ix]
        nearest_zone = price_zone * moon_factor if planet_arr[nearest_ix] == "MOON" else price_zone
        nearest_dist = float(dist_bar[nearest_ix])
        if nearest_dist <= nearest_zone:
            touches.append(
                {
                    "touch_kind": "nearest_line",
                    "touch_price": float(line_values[nearest_ix]),
                    "touch_distance_abs": nearest_dist,
                    "touch_distance_pct": nearest_dist / close if close != 0 else np.nan,
                    "touch_zone": float(nearest_zone),
                    "touch_identity_count": 1,
                    "touch_identity_1": nearest_identity,
                    "touch_identity_1_text": identity_text_arr[nearest_ix],
                    "touch_identity_2": None,
                    "touch_identity_2_text": "",
                    "touch_planets": str(planet_arr[nearest_ix]),
                    "touch_identities_json": json.dumps([identity_to_dict(nearest_identity)]),
                    "touch_line_price_1": float(line_values[nearest_ix]),
                    "touch_line_price_2": np.nan,
                    "touch_has_moon": int(planet_arr[nearest_ix] == "MOON"),
                }
            )

        sort_idx = np.argsort(line_values)
        sorted_prices = line_values[sort_idx]
        n = len(sorted_prices)
        for i in range(n):
            left_price = float(sorted_prices[i])
            left_ix = int(sort_idx[i])
            j = i + 1
            while j < n:
                right_price = float(sorted_prices[j])
                if right_price - left_price > epsilon:
                    break
                right_ix = int(sort_idx[j])
                avg_price = (left_price + right_price) / 2.0
                has_moon = planet_arr[left_ix] == "MOON" or planet_arr[right_ix] == "MOON"
                zone = price_zone * moon_factor if has_moon else price_zone
                dist = bar_distance(avg_price, high, low, close)
                if dist <= zone:
                    identity_1 = identity_arr[left_ix]
                    identity_2 = identity_arr[right_ix]
                    touches.append(
                        {
                            "touch_kind": "confluence",
                            "touch_price": float(avg_price),
                            "touch_distance_abs": float(dist),
                            "touch_distance_pct": float(dist / close) if close != 0 else np.nan,
                            "touch_zone": float(zone),
                            "touch_identity_count": 2,
                            "touch_identity_1": identity_1,
                            "touch_identity_1_text": identity_text_arr[left_ix],
                            "touch_identity_2": identity_2,
                            "touch_identity_2_text": identity_text_arr[right_ix],
                            "touch_planets": "|".join(sorted({str(planet_arr[left_ix]), str(planet_arr[right_ix])})),
                            "touch_identities_json": json.dumps([identity_to_dict(identity_1), identity_to_dict(identity_2)]),
                            "touch_line_price_1": float(left_price),
                            "touch_line_price_2": float(right_price),
                            "touch_has_moon": int(has_moon),
                        }
                    )
                j += 1

        cache[idx] = touches
        return touches

    return compute, open_arr, high_arr, low_arr, close_arr


def main() -> None:
    args = parse_args()

    events = pd.read_parquet(args.events)
    if "is_natal" in events.columns and not args.include_natal:
        events = events[~events["is_natal"].astype(bool)].copy()
    if "interval" in events.columns:
        events = events[events["interval"].astype(str).str.lower() == args.interval.lower()].copy()
    if events.empty:
        raise RuntimeError("No events after interval/transit filtering.")

    events = events.copy()
    events["timestamp"] = to_ist_series(events["timestamp"])
    events["duration_minutes"] = pd.to_numeric(events["duration_minutes"], errors="coerce").fillna(60.0)
    events["event_end"] = events["timestamp"] + pd.to_timedelta(events["duration_minutes"], unit="m")
    events["pair_key"] = [canonical_pair(a, b) for a, b in zip(events["b1"], events["b2"], strict=False)]
    events = merge_overlapping_event_windows(events)
    if float(args.max_event_days) > 0.0:
        max_event_minutes = float(args.max_event_days) * 1440.0
        events = events[events["duration_minutes"] <= max_event_minutes].copy()
        if events.empty:
            raise RuntimeError(f"No events remain after applying max-event-days={float(args.max_event_days):g}.")

    price = pd.read_parquet(args.price).sort_index()
    if price.index.tz is None:
        price.index = price.index.tz_localize(UTC)
    price = price.tz_convert(IST)
    price.columns = [str(c).lower() for c in price.columns]
    required = {"open", "high", "low", "close"}
    missing = sorted(required - set(price.columns))
    if missing:
        raise RuntimeError(f"Missing OHLC columns in price data: {missing}")

    max_needed = events["event_end"].max() + pd.Timedelta(hours=72)
    min_needed = events["timestamp"].min()
    price = price[(price.index >= min_needed) & (price.index <= max_needed)].copy()
    if price.empty:
        raise RuntimeError("Price data has no overlap with events.")

    events = events[(events["timestamp"] >= price.index.min()) & (events["event_end"] <= price.index.max())].copy()
    if events.empty:
        raise RuntimeError("No events fully overlap the price range.")

    idx_start = price.index.get_indexer(events["timestamp"].to_numpy(), method="nearest")
    idx_end = price.index.get_indexer(events["event_end"].to_numpy(), method="nearest")
    valid = (idx_start >= 0) & (idx_end >= 0)
    events = events.loc[valid].copy()
    idx_start = idx_start[valid]
    idx_end = idx_end[valid]
    events["idx_start"] = idx_start
    events["idx_end"] = idx_end
    if events.empty:
        raise RuntimeError("No events with valid start/end index mapping.")

    unique_bar_indices = sorted({i for a, b in zip(idx_start, idx_end, strict=False) for i in range(min(a, b), max(a, b) + 1)})
    if not unique_bar_indices:
        raise RuntimeError("No price bars found inside aspect windows.")

    cfg = parse_sr_config(events["sr_config_json"].iloc[0] if "sr_config_json" in events.columns else {})
    analysis_price = price.iloc[unique_bar_indices].copy()
    full_to_analysis_idx = {int(full_idx): int(pos) for pos, full_idx in enumerate(unique_bar_indices)}
    regime_map = build_aspect_regime_map(events, unique_bar_indices, price.index)
    print(f"Analysis bars inside exact aspect windows: {len(analysis_price)} / {len(price)}")
    natal_ctx = build_natal_context(args, cfg["planets"])
    print(
        "Natal reference ready:",
        f"{args.ipo_date} {args.ipo_time} {args.reference_tz}",
        "->",
        f"{natal_ctx['reference_dt'].strftime('%Y-%m-%d %H:%M')} {natal_ctx['reference_tz']}",
        f"lat={float(args.reference_lat):.4f}",
        f"lon={float(args.reference_lon):.4f}",
    )
    base_natal_ctx = None
    if not args.disable_base_reference:
        base_natal_ctx = build_reference_context(
            date_text=args.base_reference_date,
            time_text=args.base_reference_time,
            tz_name=args.base_reference_tz,
            lat=float(args.base_reference_lat),
            lon=float(args.base_reference_lon),
            planets=cfg["planets"],
            label=str(args.base_reference_label),
        )
        print(
            "Base reference ready:",
            f"{args.base_reference_date} {args.base_reference_time} {args.base_reference_tz}",
            "->",
            f"{base_natal_ctx['reference_dt'].strftime('%Y-%m-%d %H:%M:%S')} {base_natal_ctx['reference_tz']}",
            f"lat={float(args.base_reference_lat):.4f}",
            f"lon={float(args.base_reference_lon):.4f}",
        )
    print(f"Building adaptive longitude map for {len(cfg['planets'])} planets on analysis bars...")
    lon_map = build_adaptive_longitude_map(
        planets=list(cfg["planets"]),
        full_timestamps=analysis_price.index,
        fetch_fn=fetch_planetary_longitude_fast,
        astrology_method="sidereal",
        coordinate_system="geo",
    )
    print("Longitude map ready. Building touch analyzer...")
    compute_bar_touches, _, _, _, _ = build_bar_analyzer(analysis_price, lon_map, cfg)
    compute_natal_features = build_natal_feature_builder(lon_map, cfg, natal_ctx, args.aspect_mode)
    compute_base_natal_features = (
        build_natal_feature_builder(lon_map, cfg, base_natal_ctx, args.aspect_mode)
        if base_natal_ctx is not None
        else None
    )

    open_arr = price["open"].to_numpy(dtype=np.float64)
    high_arr = price["high"].to_numpy(dtype=np.float64)
    low_arr = price["low"].to_numpy(dtype=np.float64)
    close_arr = price["close"].to_numpy(dtype=np.float64)

    future72_lookup: dict[int, int] = {}
    if unique_bar_indices:
        touch_times = price.index[unique_bar_indices]
        future_targets = touch_times + pd.Timedelta(hours=72)
        mapped = price.index.get_indexer(future_targets.to_numpy(), method="nearest")
        future72_lookup = {int(idx): int(mapped[pos]) for pos, idx in enumerate(unique_bar_indices)}

    rows: list[dict[str, Any]] = []
    touch_seq = 0
    total = len(events)
    for pos, (_, event) in enumerate(events.iterrows(), start=1):
        if pos == 1 or pos % 250 == 0:
            print(f"Processing events: {pos}/{total}")

        start_idx = int(event["idx_start"])
        end_idx = int(event["idx_end"])
        if end_idx < start_idx:
            start_idx, end_idx = end_idx, start_idx
        event_metrics = compute_event_aspect_metrics(
            event,
            start_idx,
            end_idx,
            full_to_analysis_idx,
            price.index,
            lon_map,
            natal_ctx,
        )

        for bar_idx in range(start_idx, end_idx + 1):
            future72_idx = future72_lookup.get(bar_idx, -1)
            if future72_idx < 0 or future72_idx >= len(price):
                continue

            analysis_idx = full_to_analysis_idx.get(int(bar_idx))
            if analysis_idx is None:
                continue
            touches = compute_bar_touches(analysis_idx)
            if not touches:
                continue

            touch_time = price.index[bar_idx]
            touch_time_utc = touch_time.tz_convert(UTC)
            future72_time = price.index[future72_idx]
            future72_time_utc = future72_time.tz_convert(UTC)
            close_touch = float(close_arr[bar_idx])
            close_after72 = float(close_arr[future72_idx])
            ret_after72 = pct(close_touch, close_after72)

            for touch in touches:
                touch_seq += 1
                identity_1 = touch["touch_identity_1"]
                identity_2 = touch["touch_identity_2"]
                touch_planet_1 = identity_1[0] if identity_1 else ""
                touch_planet_2 = identity_2[0] if identity_2 else ""
                touch_planet_set = {p for p in [touch_planet_1, touch_planet_2] if str(p).strip()}
                natal_features, summarize_for_touch = compute_natal_features(analysis_idx, touch_planet_set)
                base_natal_features: dict[str, Any] = {}
                if compute_base_natal_features is not None:
                    base_natal_features, _ = compute_base_natal_features(analysis_idx, touch_planet_set)
                regime_meta = regime_map.get(int(bar_idx), {})
                natal_touch1 = summarize_for_touch(touch_planet_1)
                natal_touch2 = summarize_for_touch(touch_planet_2)
                touch1_natal = natal_attrs_for_planet(touch_planet_1, natal_ctx)
                touch2_natal = natal_attrs_for_planet(touch_planet_2, natal_ctx)
                event_id = str(event.get("event_id", "")).strip()
                identity_part = touch["touch_identity_1_text"]
                if touch["touch_identity_2_text"]:
                    identity_part = f"{identity_part}__{touch['touch_identity_2_text']}"
                touch_id = "|".join(
                    [
                        event_id or f"evt{pos}",
                        str(bar_idx),
                        str(touch["touch_kind"]),
                        identity_part,
                        str(touch_seq),
                    ]
                )
                row = {
                    "touch_id": touch_id,
                    "event_id": event.get("event_id"),
                    "pair_key": event.get("pair_key"),
                    "b1": event.get("b1"),
                    "b2": event.get("b2"),
                    "aspect": event.get("aspect"),
                    "aspect_system": aspect_system_for_name(event.get("aspect")),
                    "aspect_label": aspect_label_for_name(event.get("aspect")),
                    "aspect_signatures": event.get("aspect_signatures"),
                    "event_aspects_json": event.get("event_aspects_json"),
                    "event_time_local": event.get("timestamp"),
                    "event_time_utc": pd.Timestamp(event.get("timestamp")).tz_convert(UTC),
                    "event_window_start_local": event.get("timestamp"),
                    "event_window_end_local": event.get("event_end"),
                    "event_window_start_utc": pd.Timestamp(event.get("timestamp")).tz_convert(UTC),
                    "event_window_end_utc": pd.Timestamp(event.get("event_end")).tz_convert(UTC),
                    "event_duration_minutes": float(event.get("duration_minutes", 0.0)),
                    "aspect_regime_id": regime_meta.get("aspect_regime_id"),
                    "aspect_regime_active_count": regime_meta.get("aspect_regime_active_count"),
                    "aspect_regime_signature": regime_meta.get("aspect_regime_signature"),
                    "aspect_regime_start_local": regime_meta.get("aspect_regime_start_local"),
                    "aspect_regime_end_local": regime_meta.get("aspect_regime_end_local"),
                    "touch_time_local": touch_time,
                    "touch_time_utc": touch_time_utc,
                    "touch_hour_offset": int(bar_idx - start_idx),
                    "event_pair_sep_deg": event_metrics["event_pair_sep_deg"],
                    "event_orb_deg": event_metrics["event_orb_deg"],
                    "event_orb_limit_deg": event_metrics["event_orb_limit_deg"],
                    "event_orb_strength": event_metrics["event_orb_strength"],
                    "event_bphs_strength": event_metrics["event_bphs_strength"],
                    "event_bphs_virupa": event_metrics["event_bphs_virupa"],
                    "event_best_time_local": event_metrics["event_best_time_local"],
                    "event_best_time_utc": event_metrics["event_best_time_utc"],
                    "event_best_hour_offset": event_metrics["event_best_hour_offset"],
                    "touch_kind": touch["touch_kind"],
                    "touch_price": touch["touch_price"],
                    "touch_distance_abs": touch["touch_distance_abs"],
                    "touch_distance_pct": touch["touch_distance_pct"],
                    "touch_zone": touch["touch_zone"],
                    "touch_identity_count": int(touch["touch_identity_count"]),
                    "touch_identity_1_text": touch["touch_identity_1_text"],
                    "touch_identity_2_text": touch["touch_identity_2_text"],
                    "touch_identities_json": touch["touch_identities_json"],
                    "touch_planets": touch["touch_planets"],
                    "touch_has_moon": int(touch["touch_has_moon"]),
                    "touch_line_price_1": touch["touch_line_price_1"],
                    "touch_line_price_2": touch["touch_line_price_2"],
                    "touch_planet_1": touch_planet_1,
                    "touch_mode_1": identity_1[1] if identity_1 else "",
                    "touch_harmonic_1": float(identity_1[2]) if identity_1 else np.nan,
                    "touch_n_value_1": float(identity_1[3]) if identity_1 else np.nan,
                    "touch_degree_1": int(identity_1[4]) if identity_1 else np.nan,
                    "touch_planet_1_natal_lon": touch1_natal["lon"],
                    "touch_planet_1_natal_sign": touch1_natal["sign"],
                    "touch_planet_1_natal_house": touch1_natal["house"],
                    "touch_planet_1_natal_kendra_flag": int(touch1_natal["kendra_flag"]),
                    "touch_planet_1_natal_trikona_flag": int(touch1_natal["trikona_flag"]),
                    "touch_planet_1_natal_dusthana_flag": int(touch1_natal["dusthana_flag"]),
                    "touch_planet_2": touch_planet_2,
                    "touch_mode_2": identity_2[1] if identity_2 else "",
                    "touch_harmonic_2": float(identity_2[2]) if identity_2 else np.nan,
                    "touch_n_value_2": float(identity_2[3]) if identity_2 else np.nan,
                    "touch_degree_2": int(identity_2[4]) if identity_2 else np.nan,
                    "touch_planet_2_natal_lon": touch2_natal["lon"],
                    "touch_planet_2_natal_sign": touch2_natal["sign"],
                    "touch_planet_2_natal_house": touch2_natal["house"],
                    "touch_planet_2_natal_kendra_flag": int(touch2_natal["kendra_flag"]),
                    "touch_planet_2_natal_trikona_flag": int(touch2_natal["trikona_flag"]),
                    "touch_planet_2_natal_dusthana_flag": int(touch2_natal["dusthana_flag"]),
                    "open_touch": float(open_arr[bar_idx]),
                    "high_touch": float(high_arr[bar_idx]),
                    "low_touch": float(low_arr[bar_idx]),
                    "close_touch": close_touch,
                    "close_after72": close_after72,
                    "after72_time_local": future72_time,
                    "after72_time_utc": future72_time_utc,
                    "ret_after_72h_pct": ret_after72,
                    "ret_after_72h_dir": direction_from_change(ret_after72),
                    "shadbala_tag": event.get("shadbala_tag"),
                    "shadbala_avg": event.get("avg_shadbala"),
                    "moon_nakshatra": event.get("moon_nakshatra"),
                    "delta_1d": event.get("delta_1d"),
                    "delta_3d": event.get("delta_3d"),
                    "delta_7d": event.get("delta_7d"),
                    "sr_config_json": event.get("sr_config_json"),
                    "sr_epsilon": float(cfg["epsilon"]),
                    "sr_price_zone": float(cfg["price_zone"]),
                    "sr_moon_factor": float(cfg["moon_factor"]),
                    "quote_reference_label": str(natal_ctx.get("reference_label", args.quote_reference_label)),
                    "tn_reference_tz": str(natal_ctx["reference_tz"]),
                    "tn_reference_source_tz": str(natal_ctx.get("reference_source_tz", "")),
                    "tn_reference_lat": float(natal_ctx["reference_lat"]),
                    "tn_reference_lon": float(natal_ctx["reference_lon"]),
                    "tn_reference_dt_local": natal_ctx["reference_dt"],
                    "tn_reference_dt_source": natal_ctx.get("reference_source_dt"),
                    "base_reference_label": str(base_natal_ctx.get("reference_label", args.base_reference_label)) if base_natal_ctx else "",
                    "base_tn_reference_tz": str(base_natal_ctx["reference_tz"]) if base_natal_ctx else "",
                    "base_tn_reference_source_tz": str(base_natal_ctx.get("reference_source_tz", "")) if base_natal_ctx else "",
                    "base_tn_reference_lat": float(base_natal_ctx["reference_lat"]) if base_natal_ctx else np.nan,
                    "base_tn_reference_lon": float(base_natal_ctx["reference_lon"]) if base_natal_ctx else np.nan,
                    "base_tn_reference_dt_local": base_natal_ctx["reference_dt"] if base_natal_ctx else pd.NaT,
                    "base_tn_reference_dt_source": base_natal_ctx.get("reference_source_dt") if base_natal_ctx else pd.NaT,
                    "tn_touch1_active_count": int(natal_touch1["active_count"]),
                    "tn_touch1_best_aspect": str(natal_touch1["best_aspect"]),
                    "tn_touch1_best_natal_target": str(natal_touch1["best_natal_target"]),
                    "tn_touch1_min_orb_deg": natal_touch1["min_orb_deg"],
                    "tn_touch1_score": float(natal_touch1["score"]),
                    "tn_touch1_bphs_strength": float(natal_touch1["bphs_strength"]),
                    "tn_touch2_active_count": int(natal_touch2["active_count"]),
                    "tn_touch2_best_aspect": str(natal_touch2["best_aspect"]),
                    "tn_touch2_best_natal_target": str(natal_touch2["best_natal_target"]),
                    "tn_touch2_min_orb_deg": natal_touch2["min_orb_deg"],
                    "tn_touch2_score": float(natal_touch2["score"]),
                    "tn_touch2_bphs_strength": float(natal_touch2["bphs_strength"]),
                }
                row.update(natal_features)
                if base_natal_features:
                    row.update(prefix_dict(base_natal_features, "base_"))
                rows.append(row)

    if not rows:
        raise RuntimeError("No touch rows generated.")

    out = pd.DataFrame(rows)
    if {"b1", "b2"}.issubset(out.columns):
        b1 = out["b1"].astype(str).str.strip().str.upper()
        b2 = out["b2"].astype(str).str.strip().str.upper()
        out = out[~b1.eq(b2)].copy()
    if "pair_key" in out.columns:
        pair_parts = out["pair_key"].astype(str).str.split("|", n=1, expand=True)
        if pair_parts.shape[1] == 2:
            left = pair_parts[0].astype(str).str.strip().str.upper()
            right = pair_parts[1].astype(str).str.strip().str.upper()
            out = out[~left.eq(right)].copy()
    # Final chart selection is event-based: one marker per aspect event,
    # preferring the first confluence if one exists. Regime- and global
    # price-band gates suppress valid first touches of later events, so they
    # are not applied in the final export path.
    out = gate_one_touch_per_event(out)
    out = out.sort_values(["touch_time_local", "pair_key", "aspect", "touch_kind"]).reset_index(drop=True)
    export_out = build_user_facing_touch_log(out)
    export_out.to_csv(args.output, index=False)
    print(f"Generated rows: {len(export_out)}")
    print(f"Saved: {args.output}")

def orb_limit_for_aspect_name(aspect_name: str) -> float:
    name = str(aspect_name or "").strip().lower()
    return float(MARKET_ORB_LIMITS.get(name, 0.0))


def smooth_orb_strength(orb_deg: float, orb_limit: float) -> float:
    if not np.isfinite(float(orb_deg)) or orb_limit <= 0:
        return 0.0
    return float(max(0.0, 1.0 - (float(orb_deg) / float(orb_limit))))


def bphs_quarter_strength(orb_deg: float, orb_limit: float) -> float:
    if not np.isfinite(float(orb_deg)) or orb_limit <= 0:
        return 0.0
    # Use a continuous BPHS-like strength so virupa values are not forced into
    # only a few discrete buckets on the chart.
    return smooth_orb_strength(orb_deg, orb_limit)


def bphs_virupa_from_strength(strength: float) -> float:
    if not np.isfinite(float(strength)):
        return 0.0
    return float(max(0.0, min(60.0, 60.0 * float(strength))))


def event_runtime_config(aspect_name: str) -> dict[str, Any]:
    name = str(aspect_name or "").strip().lower()
    if name in ORB_ASPECTS:
        angle_map = {
            "conjunction_orb": 0.0,
            "square": 90.0,
            "trine": 120.0,
            "opposition_orb": 180.0,
        }
        return {"kind": "orb", "angle": angle_map[name], "orb": orb_limit_for_aspect_name(name)}
    if name.startswith("rashi_"):
        return {"kind": "rashi", "mode": name.replace("rashi_", ""), "orb": 1.0}
    graha_angles = {
        "conjunction": 0.0,
        "opposition": 180.0,
        "drishti_3": 60.0,
        "drishti_4": 90.0,
        "drishti_5": 120.0,
        "drishti_8": 210.0,
        "drishti_9": 240.0,
        "drishti_10": 270.0,
    }
    if name in graha_angles:
        return {"kind": "graha", "angle": graha_angles[name], "orb": 3.0 if name == "conjunction" else 1.5}
    return {"kind": "other", "angle": np.nan, "orb": 0.0}


def compute_event_aspect_metrics(
    event: pd.Series,
    start_idx: int,
    end_idx: int,
    full_to_analysis_idx: dict[int, int],
    price_index: pd.DatetimeIndex,
    lon_map: dict[str, pd.Series],
    natal_ctx: dict[str, Any],
) -> dict[str, Any]:
    aspect_name = str(event.get("aspect", "")).strip().lower()
    cfg = event_runtime_config(aspect_name)
    left_name = str(event.get("b1", "")).strip().upper()
    right_name = str(event.get("b2", "")).strip().upper()

    out = {
        "event_pair_sep_deg": np.nan,
        "event_orb_deg": np.nan,
        "event_orb_limit_deg": np.nan,
        "event_orb_strength": 0.0,
        "event_bphs_strength": 0.0,
        "event_bphs_virupa": 0.0,
        "event_best_time_local": pd.NaT,
        "event_best_time_utc": pd.NaT,
        "event_best_hour_offset": np.nan,
    }

    if cfg["kind"] == "rashi":
        for bar_idx in range(start_idx, end_idx + 1):
            analysis_idx = full_to_analysis_idx.get(int(bar_idx))
            if analysis_idx is None:
                continue
            left_lon = float(lon_map.get(left_name, pd.Series(dtype=float)).iloc[analysis_idx]) if left_name in lon_map else np.nan
            if bool(event.get("is_natal", False)):
                right_lon = float(natal_ctx["longitudes"].get(right_name, np.nan))
            else:
                right_lon = float(lon_map.get(right_name, pd.Series(dtype=float)).iloc[analysis_idx]) if right_name in lon_map else np.nan
            if not np.isfinite(left_lon) or not np.isfinite(right_lon):
                continue
            sep = angular_separation(left_lon, right_lon)
            if is_rashi_aspect_hit(left_lon, right_lon, str(cfg.get("mode", ""))):
                event_time_local = price_index[bar_idx]
                out["event_pair_sep_deg"] = float(sep)
                out["event_orb_deg"] = 0.0
                out["event_orb_limit_deg"] = float(cfg.get("orb", 1.0))
                out["event_orb_strength"] = 1.0
                out["event_bphs_strength"] = 1.0
                out["event_bphs_virupa"] = 60.0
                out["event_best_time_local"] = event_time_local
                out["event_best_time_utc"] = event_time_local.tz_convert(UTC)
                out["event_best_hour_offset"] = int(bar_idx - start_idx)
                break
        return out

    angle = float(cfg.get("angle", np.nan))
    orb_limit = float(cfg.get("orb", 0.0))
    if not np.isfinite(angle):
        return out

    best_orb_deg = np.inf
    best_sep = np.nan
    best_time_local = pd.NaT
    best_hour_offset = np.nan
    for bar_idx in range(start_idx, end_idx + 1):
        analysis_idx = full_to_analysis_idx.get(int(bar_idx))
        if analysis_idx is None:
            continue
        left_lon = float(lon_map.get(left_name, pd.Series(dtype=float)).iloc[analysis_idx]) if left_name in lon_map else np.nan
        if bool(event.get("is_natal", False)):
            right_lon = float(natal_ctx["longitudes"].get(right_name, np.nan))
        else:
            right_lon = float(lon_map.get(right_name, pd.Series(dtype=float)).iloc[analysis_idx]) if right_name in lon_map else np.nan
        if not np.isfinite(left_lon) or not np.isfinite(right_lon):
            continue
        sep = angular_separation(left_lon, right_lon)
        orb_deg = abs(float(sep) - angle)
        if orb_deg < best_orb_deg:
            best_orb_deg = float(orb_deg)
            best_sep = float(sep)
            best_time_local = price_index[bar_idx]
            best_hour_offset = int(bar_idx - start_idx)

    if not np.isfinite(best_orb_deg):
        return out

    orb_strength = smooth_orb_strength(best_orb_deg, orb_limit)
    bphs_strength = bphs_quarter_strength(best_orb_deg, orb_limit)

    out["event_pair_sep_deg"] = float(best_sep)
    out["event_orb_deg"] = float(best_orb_deg)
    out["event_orb_limit_deg"] = float(orb_limit)
    out["event_orb_strength"] = float(orb_strength)
    out["event_bphs_strength"] = float(bphs_strength)
    out["event_bphs_virupa"] = float(bphs_virupa_from_strength(bphs_strength))
    out["event_best_time_local"] = best_time_local
    if pd.notna(best_time_local):
        out["event_best_time_utc"] = best_time_local.tz_convert(UTC)
    out["event_best_hour_offset"] = best_hour_offset
    return out


if __name__ == "__main__":
    main()
