from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from build_aspect_sr_touch_log import (
    BASE_REFERENCE_DATE_DEFAULT,
    BASE_REFERENCE_LAT_DEFAULT,
    BASE_REFERENCE_LON_DEFAULT,
    BASE_REFERENCE_TIME_DEFAULT,
    BASE_REFERENCE_TZ_DEFAULT,
    IST,
    REFERENCE_LAT_DEFAULT,
    REFERENCE_LON_DEFAULT,
    REFERENCE_TZ_DEFAULT,
    build_reference_context,
    fetch_planetary_longitude_fast,
)
from padmanabhan_timing_doctrine import (
    CLASSICAL_TRANSIT_PLANETS,
    NODE_PLANETS,
    doctrine_metadata,
    flatten_pair_timing,
    flatten_reference_timing,
    pair_timing_context,
    reference_timing_context,
)


DEFAULT_INPUT = (
    r"D:\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_"
    r"usdjpy_basequote_all_durations_transitsign.csv"
)
DEFAULT_OUTPUT = (
    r"D:\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_"
    r"usdjpy_basequote_all_durations_transitsign_padmanabhan_v1.csv"
)
TIMING_PREFIXES = (
    "event_padmanabhan_",
    "event_base_padmanabhan_",
    "event_quote_padmanabhan_",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Attach source-bounded Padmanabhan Gochara/Dasha evidence to an existing touch or switch CSV "
            "without changing its touch IDs, price rows, labels, or legacy scores."
        )
    )
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
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
    return parser.parse_args()


def evaluation_time_column(df: pd.DataFrame) -> str:
    for column in ("event_best_time_local", "event_time_local", "event_window_start_local", "touch_time_local"):
        if column in df.columns and df[column].notna().any():
            return column
    raise ValueError("Input needs event_best_time_local, event_time_local, event_window_start_local, or touch_time_local.")


def event_key_column(df: pd.DataFrame) -> str:
    for column in ("event_id", "source_event_id"):
        if column in df.columns and df[column].notna().any():
            return column
    raise ValueError("Input needs event_id or source_event_id so repeated timeframe rows share one timing calculation.")


def build_reference_contexts(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    planets = tuple(dict.fromkeys(CLASSICAL_TRANSIT_PLANETS + NODE_PLANETS))
    quote = build_reference_context(
        date_text=args.ipo_date,
        time_text=args.ipo_time,
        tz_name=args.reference_tz,
        lat=float(args.reference_lat),
        lon=float(args.reference_lon),
        planets=planets,
        label=str(args.quote_reference_label),
    )
    base = build_reference_context(
        date_text=args.base_reference_date,
        time_text=args.base_reference_time,
        tz_name=args.base_reference_tz,
        lat=float(args.base_reference_lat),
        lon=float(args.base_reference_lon),
        planets=planets,
        label=str(args.base_reference_label),
    )
    return quote, base


def event_timing_rows(df: pd.DataFrame, args: argparse.Namespace) -> tuple[str, pd.DataFrame]:
    key_col = event_key_column(df)
    time_col = evaluation_time_column(df)
    events = df[[key_col, time_col]].copy()
    events[key_col] = events[key_col].astype(str)
    events["_evaluation_time"] = pd.to_datetime(events[time_col], errors="coerce", utc=True)
    events = events.dropna(subset=["_evaluation_time"])
    conflicts = events.groupby(key_col, sort=False)["_evaluation_time"].nunique()
    bad = conflicts[conflicts > 1]
    if not bad.empty:
        raise ValueError(f"{len(bad)} event ids map to more than one evaluation time; refusing ambiguous enrichment.")
    events = events.drop_duplicates(subset=[key_col], keep="first").sort_values("_evaluation_time").reset_index(drop=True)
    if events.empty:
        raise ValueError("No valid event evaluation times were found.")
    index = pd.DatetimeIndex(events["_evaluation_time"]).tz_convert(IST)
    planets = tuple(dict.fromkeys(CLASSICAL_TRANSIT_PLANETS + NODE_PLANETS))
    longitude_map = {
        planet: fetch_planetary_longitude_fast(planet, index, astrology_method="sidereal", coordinate_system="geo")
        for planet in planets
    }
    quote_reference, base_reference = build_reference_contexts(args)
    records: list[dict[str, Any]] = []
    metadata = doctrine_metadata()
    for position, event in events.iterrows():
        transit_longitudes = {
            planet: float(series.iloc[position]) % 360.0
            for planet, series in longitude_map.items()
            if position < len(series) and np.isfinite(float(series.iloc[position]))
        }
        event_time = index[position]
        quote = reference_timing_context(
            reference_label=str(quote_reference.get("reference_label", "JPY")),
            reference_time=quote_reference.get("reference_dt"),
            natal_longitudes=quote_reference.get("timing_longitudes", {}),
            transit_longitudes=transit_longitudes,
            event_time=event_time,
            natal_shadbala_totals=quote_reference.get("strict_shadbala_totals", {}),
        )
        base = reference_timing_context(
            reference_label=str(base_reference.get("reference_label", "USD")),
            reference_time=base_reference.get("reference_dt"),
            natal_longitudes=base_reference.get("timing_longitudes", {}),
            transit_longitudes=transit_longitudes,
            event_time=event_time,
            natal_shadbala_totals=base_reference.get("strict_shadbala_totals", {}),
        )
        record: dict[str, Any] = {key_col: str(event[key_col]), "event_padmanabhan_evaluation_time_local": event_time}
        record.update(metadata)
        record.update(flatten_reference_timing("event_quote_padmanabhan", quote))
        record.update(flatten_reference_timing("event_base_padmanabhan", base))
        record.update(flatten_pair_timing("event_padmanabhan", pair_timing_context(base, quote)))
        records.append(record)
    return key_col, pd.DataFrame.from_records(records)


def enrich(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    key_col, timing = event_timing_rows(df, args)
    drop_cols = [
        column
        for column in df.columns
        if column == "event_padmanabhan_evaluation_time_local"
        or any(column.startswith(prefix) for prefix in TIMING_PREFIXES)
    ]
    base = df.drop(columns=drop_cols, errors="ignore").copy()
    base[key_col] = base[key_col].astype(str)
    out = base.merge(timing, on=key_col, how="left", validate="many_to_one")
    missing = int(out["event_padmanabhan_pair_prosperity_index_i"].isna().sum())
    if missing:
        raise RuntimeError(f"Enrichment left {missing} rows without a pair timing index.")
    return out


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    df = pd.read_csv(input_path, low_memory=False)
    original_rows = len(df)
    original_touch_ids = df["touch_id"].astype(str).tolist() if "touch_id" in df.columns else None
    out = enrich(df, args)
    if len(out) != original_rows:
        raise RuntimeError(f"Row count changed during enrichment: {original_rows} -> {len(out)}")
    if original_touch_ids is not None and out["touch_id"].astype(str).tolist() != original_touch_ids:
        raise RuntimeError("touch_id order or values changed during enrichment.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    print(f"Rows preserved: {len(out)}")
    print(f"Columns: {len(df.columns)} -> {len(out.columns)}")
    print(f"Events enriched: {out[event_key_column(out)].nunique()}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
