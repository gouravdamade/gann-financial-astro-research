from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import swisseph as swe

from aspect_annotation_store import DEFAULT_DB_PATH, initialize_database
from doctrine_config import configure_swiss_ephemeris_sidereal, doctrine_ayanamsa_name


IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")
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
DEFAULT_BODIES = (
    AVG_ALL_LABEL,
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "RAHU",
    "KETU",
)
OUTER_BODIES = ("URANUS", "NEPTUNE", "PLUTO")
ASPECTS = {
    "conjunction_orb": {"angle": 0.0, "orb": 1.5},
    "square": {"angle": 90.0, "orb": 1.0},
    "trine": {"angle": 120.0, "orb": 1.0},
    "opposition_orb": {"angle": 180.0, "orb": 1.5},
}
PLANET_IDS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
    "URANUS": swe.URANUS,
    "NEPTUNE": swe.NEPTUNE,
    "PLUTO": swe.PLUTO,
    "RAHU": swe.TRUE_NODE,
}
SIGNS = (
    "ARIES",
    "TAURUS",
    "GEMINI",
    "CANCER",
    "LEO",
    "VIRGO",
    "LIBRA",
    "SCORPIO",
    "SAGITTARIUS",
    "CAPRICORN",
    "AQUARIUS",
    "PISCES",
)
DEFAULT_EPHEMERIS_PATHS = (
    Path(r"D:\Trading_Algo\Desktop_Trading_Algo_root_legacy_20260530\sweph"),
    Path(r"D:\Trading_Algo\New folder\sweph"),
    Path(r"D:\PycharmProjects\sweph"),
)


@dataclass(frozen=True)
class Window:
    body1: str
    body2: str
    aspect: str
    start: pd.Timestamp
    end: pd.Timestamp
    peak: pd.Timestamp
    peak_sep_deg: float
    peak_orb_delta_deg: float
    orb_limit_deg: float
    b1_lon_peak: float
    b2_lon_peak: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate upcoming sidereal aspect windows without requiring future price data. "
            "The output is intended for pre-review/live planning, not as an order signal by itself."
        )
    )
    parser.add_argument("--start", help="Start datetime/date in IST. Default: now in Asia/Kolkata.")
    parser.add_argument("--days", type=int, default=30, help="Forward horizon in days.")
    parser.add_argument("--end", help="Optional explicit end datetime/date in IST.")
    parser.add_argument("--step-minutes", type=int, default=30)
    parser.add_argument("--min-window-minutes", type=int, default=30)
    parser.add_argument("--bodies", help="Comma-separated body list. Default: AVG(ALL), classical, nodes.")
    parser.add_argument("--include-outer", action="store_true", help="Add Uranus/Neptune/Pluto as standalone bodies.")
    parser.add_argument("--output-csv", type=Path, help="CSV output path.")
    parser.add_argument("--output-json", type=Path, help="JSON output path.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--no-review-context", action="store_true", help="Skip SQLite completed-review enrichment.")
    parser.add_argument("--top", type=int, default=25, help="Rows to print after writing outputs.")
    parser.add_argument("--ephemeris-path", type=Path, help="Optional Swiss Ephemeris file root.")
    return parser.parse_args()


def parse_ist_datetime(value: str | None, default: datetime | None = None) -> datetime:
    if not value:
        return default or datetime.now(IST).replace(second=0, microsecond=0)
    text = value.strip()
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    return dt.astimezone(IST).replace(second=0, microsecond=0)


def configure_ephemeris(ephemeris_path: Path | None) -> str:
    configure_swiss_ephemeris_sidereal(swe)
    path = ephemeris_path
    if path is None:
        path = next((candidate for candidate in DEFAULT_EPHEMERIS_PATHS if candidate.exists()), None)
    if path is not None:
        swe.set_ephe_path(str(path))
        return str(path)
    return "swisseph_default_or_moshier_fallback"


def normalize_body(body: str) -> str:
    text = body.strip().upper()
    if text in {"AVG_ALL", "AVGALL", "AVG(ALL7)"}:
        return AVG_ALL_LABEL
    return text


def body_list(args: argparse.Namespace) -> list[str]:
    if args.bodies:
        bodies = [normalize_body(part) for part in args.bodies.split(",") if part.strip()]
    else:
        bodies = list(DEFAULT_BODIES)
    if args.include_outer:
        for body in OUTER_BODIES:
            if body not in bodies:
                bodies.append(body)
    unknown = [body for body in bodies if body != AVG_ALL_LABEL and body != "KETU" and body not in PLANET_IDS]
    if unknown:
        raise SystemExit(f"Unknown bodies: {', '.join(unknown)}")
    return bodies


def jd_ut_for_timestamp(ts: pd.Timestamp) -> float:
    dt = ts.to_pydatetime().astimezone(UTC)
    return float(swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60 + dt.second / 3600))


def calc_body_longitude(body: str, timestamps: pd.DatetimeIndex) -> pd.Series:
    if body == "KETU":
        rahu = calc_body_longitude("RAHU", timestamps)
        return (rahu + 180.0) % 360.0
    if body == AVG_ALL_LABEL:
        members = [calc_body_longitude(member, timestamps) for member in AVG_ALL_PLANETS]
        return circular_average_frame(pd.concat(members, axis=1))
    planet_id = PLANET_IDS[body]
    values: list[float] = []
    for ts in timestamps:
        jd_ut = jd_ut_for_timestamp(ts)
        values.append(calc_sidereal_lon(jd_ut, planet_id))
    return pd.Series(values, index=timestamps, dtype=float)


def calc_sidereal_lon(jd_ut: float, planet_id: int) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    try:
        return float(swe.calc_ut(jd_ut, planet_id, flags)[0][0] % 360.0)
    except Exception:
        flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        return float(swe.calc_ut(jd_ut, planet_id, flags)[0][0] % 360.0)


def circular_average_frame(frame: pd.DataFrame) -> pd.Series:
    arr = frame.to_numpy(dtype=float)
    radians = np.deg2rad(arr)
    sin_sum = np.nansum(np.sin(radians), axis=1)
    cos_sum = np.nansum(np.cos(radians), axis=1)
    out = np.degrees(np.arctan2(sin_sum, cos_sum)) % 360.0
    return pd.Series(out, index=frame.index, dtype=float)


def angular_sep(a: pd.Series, b: pd.Series) -> np.ndarray:
    diff = np.abs(a.to_numpy(dtype=float) - b.to_numpy(dtype=float)) % 360.0
    return np.minimum(diff, 360.0 - diff)


def pair_key(body1: str, body2: str) -> str:
    return "|".join(sorted((body1, body2)))


def sign_name(lon: float) -> str:
    return SIGNS[int((float(lon) % 360.0) // 30.0)]


def detect_windows(
    body1: str,
    body2: str,
    aspect: str,
    lon1: pd.Series,
    lon2: pd.Series,
    timestamps: pd.DatetimeIndex,
    *,
    step_minutes: int,
    min_window_minutes: int,
) -> list[Window]:
    spec = ASPECTS[aspect]
    sep = angular_sep(lon1, lon2)
    delta = np.abs(sep - float(spec["angle"]))
    hit = delta <= float(spec["orb"])
    indexes = np.flatnonzero(hit)
    if indexes.size == 0:
        return []
    groups = np.split(indexes, np.where(np.diff(indexes) != 1)[0] + 1)
    windows: list[Window] = []
    for group in groups:
        if group.size == 0:
            continue
        start_i = int(group[0])
        end_i = int(group[-1])
        sampled_duration = max(
            step_minutes,
            int((timestamps[end_i] - timestamps[start_i]).total_seconds() // 60),
        )
        if sampled_duration < min_window_minutes:
            continue
        local_delta = delta[group]
        peak_i = int(group[int(np.argmin(local_delta))])
        windows.append(
            Window(
                body1=body1,
                body2=body2,
                aspect=aspect,
                start=timestamps[start_i],
                end=timestamps[end_i],
                peak=timestamps[peak_i],
                peak_sep_deg=float(sep[peak_i]),
                peak_orb_delta_deg=float(delta[peak_i]),
                orb_limit_deg=float(spec["orb"]),
                b1_lon_peak=float(lon1.iloc[peak_i]),
                b2_lon_peak=float(lon2.iloc[peak_i]),
            )
        )
    return windows


def review_context(db_path: Path, family_keys: list[str]) -> dict[str, dict[str, Any]]:
    if not family_keys or not db_path.exists():
        return {}
    initialize_database(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        placeholders = ",".join("?" for _ in family_keys)
        rows = conn.execute(
            f"""
            SELECT
                family_key,
                COUNT(*) AS completed_count,
                SUM(CASE WHEN outcome_label='bullish' THEN 1 ELSE 0 END) AS bullish_count,
                SUM(CASE WHEN outcome_label='bearish' THEN 1 ELSE 0 END) AS bearish_count,
                SUM(CASE WHEN review_status='ignored' THEN 1 ELSE 0 END) AS ignored_count,
                AVG(signed_pips) AS avg_signed_pips
            FROM completed_reviews
            WHERE family_key IN ({placeholders})
            GROUP BY family_key
            """,
            family_keys,
        ).fetchall()
        context = {row["family_key"]: dict(row) for row in rows}
        note_rows = conn.execute(
            f"""
            SELECT cr.family_key, rn.note_text, rn.created_at_utc
            FROM completed_reviews cr
            JOIN rule_notes rn ON rn.case_id = cr.case_id
            WHERE cr.family_key IN ({placeholders})
              AND rn.note_type = 'official_ml_note'
            ORDER BY rn.created_at_utc DESC, rn.note_id DESC
            """,
            family_keys,
        ).fetchall()
        for row in note_rows:
            family = row["family_key"]
            if family not in context:
                context[family] = {"family_key": family}
            if "latest_official_note_excerpt" not in context[family]:
                context[family]["latest_official_note_excerpt"] = note_excerpt(row["note_text"])
        return context
    finally:
        conn.close()


def note_excerpt(text: str, limit: int = 220) -> str:
    clean = " ".join(str(text or "").split())
    return clean[:limit] + ("..." if len(clean) > limit else "")


def rows_from_windows(windows: list[Window], context: dict[str, dict[str, Any]], metadata: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for window in sorted(windows, key=lambda item: (item.start, item.peak_orb_delta_deg, item.body1, item.body2)):
        pkey = pair_key(window.body1, window.body2)
        family = f"{pkey}::{window.aspect}"
        ctx = context.get(family, {})
        duration = max(0, int((window.end - window.start).total_seconds() // 60))
        rows.append(
            {
                "family_key": family,
                "pair_key": pkey,
                "body1": window.body1,
                "body2": window.body2,
                "aspect": window.aspect,
                "start_ist": window.start.isoformat(),
                "end_ist": window.end.isoformat(),
                "peak_ist": window.peak.isoformat(),
                "duration_minutes": duration,
                "peak_sep_deg": round(window.peak_sep_deg, 6),
                "peak_orb_delta_deg": round(window.peak_orb_delta_deg, 6),
                "orb_limit_deg": window.orb_limit_deg,
                "closeness": round(max(0.0, 1.0 - window.peak_orb_delta_deg / max(window.orb_limit_deg, 1e-9)), 4),
                "body1_lon_peak": round(window.b1_lon_peak, 6),
                "body2_lon_peak": round(window.b2_lon_peak, 6),
                "body1_sign": sign_name(window.b1_lon_peak),
                "body2_sign": sign_name(window.b2_lon_peak),
                "family_completed_count": int(ctx.get("completed_count") or 0),
                "family_bullish_count": int(ctx.get("bullish_count") or 0),
                "family_bearish_count": int(ctx.get("bearish_count") or 0),
                "family_ignored_count": int(ctx.get("ignored_count") or 0),
                "family_avg_signed_pips": round(float(ctx["avg_signed_pips"]), 2)
                if ctx.get("avg_signed_pips") is not None
                else "",
                "latest_official_note_excerpt": ctx.get("latest_official_note_excerpt", ""),
                "doctrine_ayanamsa": metadata["ayanamsa"],
                "ephemeris_path": metadata["ephemeris_path"],
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    ephemeris_path = configure_ephemeris(args.ephemeris_path)
    bodies = body_list(args)
    start = parse_ist_datetime(args.start)
    end = parse_ist_datetime(args.end) if args.end else start + timedelta(days=args.days)
    timestamps = pd.date_range(start=start, end=end, freq=f"{int(args.step_minutes)}min", tz=IST)
    if len(timestamps) < 2:
        raise SystemExit("Need at least two timestamps. Increase --days or lower --step-minutes.")

    longitudes = {body: calc_body_longitude(body, timestamps) for body in bodies}
    windows: list[Window] = []
    for i, body1 in enumerate(bodies):
        for body2 in bodies[i + 1 :]:
            for aspect in ASPECTS:
                windows.extend(
                    detect_windows(
                        body1,
                        body2,
                        aspect,
                        longitudes[body1],
                        longitudes[body2],
                        timestamps,
                        step_minutes=int(args.step_minutes),
                        min_window_minutes=int(args.min_window_minutes),
                    )
                )
    families = sorted({f"{pair_key(item.body1, item.body2)}::{item.aspect}" for item in windows})
    context = {} if args.no_review_context else review_context(args.db, families)
    metadata = {"ayanamsa": doctrine_ayanamsa_name(), "ephemeris_path": ephemeris_path}
    frame = rows_from_windows(windows, context, metadata)

    if args.output_csv:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(args.output_csv, index=False)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(frame.to_dict("records"), indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        json.dumps(
            {
                "rows": int(len(frame)),
                "start_ist": start.isoformat(),
                "end_ist": end.isoformat(),
                "step_minutes": int(args.step_minutes),
                "bodies": bodies,
                "ayanamsa": metadata["ayanamsa"],
                "csv": str(args.output_csv) if args.output_csv else "",
                "json": str(args.output_json) if args.output_json else "",
            },
            indent=2,
        )
    )
    if not frame.empty and args.top:
        cols = [
            "family_key",
            "start_ist",
            "end_ist",
            "peak_ist",
            "peak_orb_delta_deg",
            "family_completed_count",
            "family_avg_signed_pips",
        ]
        print(frame[cols].head(int(args.top)).to_string(index=False))


if __name__ == "__main__":
    main()
