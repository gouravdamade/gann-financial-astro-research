from __future__ import annotations

import argparse
import importlib
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(r"C:\Users\ADMIN\Desktop\Trading_Algo\New folder")
IST = "Asia/Kolkata"
UTC = "UTC"

DEFAULT_SELECTED_ASPECTS = {
    "graha": [
        "conjunction",
        "opposition",
        "drishti_3",
        "drishti_4",
        "drishti_5",
        "drishti_8",
        "drishti_9",
        "drishti_10",
    ],
    "rashi": [
        "rashi_movable",
        "rashi_fixed",
        "rashi_dual",
    ],
    "both": [
        "conjunction",
        "opposition",
        "drishti_3",
        "drishti_4",
        "drishti_5",
        "drishti_8",
        "drishti_9",
        "drishti_10",
        "rashi_movable",
        "rashi_fixed",
        "rashi_dual",
    ],
    "orb": [
        "conjunction_orb",
        "square",
        "trine",
        "opposition_orb",
    ],
}
AVG_ALL_LABEL = "AVG(ALL)"
AVG_ALL_PLANETS = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO")
CORE7_DEFAULT_TEXT = "Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu, AVG(all)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild the astro dataset through JDML4 using an IPO reference chart "
            "and, by default, all transit planet pairs."
        )
    )
    parser.add_argument("--ticker", default="USDJPY")
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--start-date", default="2010-01-01")
    parser.add_argument("--end-date", default="2026-12-31")
    parser.add_argument("--future-end-date", default=None)
    parser.add_argument("--analysis-mode", default="natal", choices=["transit", "natal"])
    parser.add_argument("--reference-chart-type", default="ipo", choices=["none", "ipo", "country", "custom"])
    parser.add_argument("--coordinate-system", default="geo", choices=["geo", "helio"])
    parser.add_argument("--astrology-method", default="sidereal", choices=["sidereal", "tropical"])
    parser.add_argument("--degree-values", default="360,180,90,45")
    parser.add_argument("--harmonics", default="0.12,0.18")
    parser.add_argument("--n-values", default="1.2,1.3,1.4,1.5,1.6,1.7,1.8")
    parser.add_argument(
        "--celestial-bodies",
        default=CORE7_DEFAULT_TEXT,
        help="Transit bodies to compare against reference chart in transit-to-natal mode.",
    )
    parser.add_argument(
        "--aspect-mode",
        default="graha",
        choices=["graha", "rashi", "both", "orb"],
        help="Aspect engine to use when rebuilding the event dataset.",
    )
    parser.add_argument(
        "--selected-aspects",
        default="",
        help="Comma-separated aspect keys. If omitted, defaults are chosen from --aspect-mode.",
    )
    parser.add_argument("--exclude-planets", default="")
    parser.add_argument("--ipo-date", default="1889-02-11")
    parser.add_argument("--ipo-time", default="00:00")
    parser.add_argument("--hq-city", default="Tokyo")
    parser.add_argument("--hq-country", default="Japan")
    parser.add_argument("--manual-coords", default="")
    parser.add_argument(
        "--natal-celestial-bodies",
        default=CORE7_DEFAULT_TEXT,
    )
    parser.add_argument(
        "--output-file",
        default=str(Path(r"C:\Users\ADMIN\PycharmProjects") / "astro_training_data_ipo_tokyo_18890211.parquet"),
    )
    parser.add_argument(
        "--signal-file",
        default=str(Path(r"C:\Users\ADMIN\PycharmProjects") / "direction_trade_signals_ipo_tokyo_18890211.parquet"),
    )
    parser.add_argument(
        "--price-parquet",
        default=str(Path(r"C:\Users\ADMIN\PycharmProjects") / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet"),
        help="Optional local OHLC parquet used instead of live MT5/Yahoo fetch inside JDML4.",
    )
    parser.add_argument(
        "--use-default-exclusions",
        action="store_true",
        default=False,
        help="Keep JDML4 default excluded interaction pairs. Default behavior clears them for all-pairs mode.",
    )
    return parser.parse_args()


def load_jdml4():
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))
    return importlib.import_module("JDML4")


def patch_avg_all_parser(jdml4: object) -> None:
    original = jdml4.parse_celestial_input_simple

    def patched(input_str, coordinate_system="geo"):
        entries = original(input_str, coordinate_system=coordinate_system)
        patched_entries: list[dict[str, object]] = []
        for entry in entries:
            if str(entry.get("type", "")).lower() != "avg":
                patched_entries.append(entry)
                continue
            display_name = str(entry.get("display_name", "")).strip().upper()
            planets = [str(p).strip().upper() for p in entry.get("planets", []) if str(p).strip()]
            if display_name == AVG_ALL_LABEL or set(planets) == set(AVG_ALL_PLANETS):
                patched_entries.append(
                    {
                        "type": "avg",
                        "planets": list(AVG_ALL_PLANETS),
                        "display_name": AVG_ALL_LABEL,
                    }
                )
            else:
                patched_entries.append(entry)
        return patched_entries

    jdml4.parse_celestial_input_simple = patched


def resolve_selected_aspects(aspect_mode: str, selected_aspects_text: str) -> list[str]:
    raw = [a.strip() for a in str(selected_aspects_text or "").split(",") if a.strip()]
    if raw:
        return raw
    return list(DEFAULT_SELECTED_ASPECTS.get(str(aspect_mode).strip().lower(), DEFAULT_SELECTED_ASPECTS["graha"]))


def build_local_fetch_fn(price_parquet: str):
    price_path = Path(price_parquet)
    if not price_path.exists():
        raise FileNotFoundError(f"Local price parquet not found: {price_path}")

    raw = pd.read_parquet(price_path).sort_index()
    idx = raw.index
    if idx.tz is None:
        idx = idx.tz_localize(UTC)
    idx = idx.tz_convert(IST)
    raw.index = idx

    lower_cols = {str(c).lower(): c for c in raw.columns}
    required = {"open", "high", "low", "close"}
    missing = required - set(lower_cols.keys())
    if missing:
        raise RuntimeError(f"Local price parquet missing OHLC columns: {sorted(missing)}")

    frame = pd.DataFrame(index=raw.index)
    frame["Open"] = pd.to_numeric(raw[lower_cols["open"]], errors="coerce")
    frame["High"] = pd.to_numeric(raw[lower_cols["high"]], errors="coerce")
    frame["Low"] = pd.to_numeric(raw[lower_cols["low"]], errors="coerce")
    frame["Close"] = pd.to_numeric(raw[lower_cols["close"]], errors="coerce")
    frame = frame.dropna(subset=["Open", "High", "Low", "Close"])

    def _fetch_stock_data(_ticker: str, start_datetime, end_datetime, _interval: str):
        start_dt = pd.to_datetime(start_datetime)
        end_dt = pd.to_datetime(end_datetime)
        if start_dt.tzinfo is None:
            start_dt = start_dt.tz_localize(IST)
        else:
            start_dt = start_dt.tz_convert(IST)
        if end_dt.tzinfo is None:
            end_dt = end_dt.tz_localize(IST)
        else:
            end_dt = end_dt.tz_convert(IST)
        return frame[(frame.index >= start_dt) & (frame.index <= end_dt)].copy()

    return _fetch_stock_data


def canonical_pair(a: object, b: object) -> str:
    left = str(a or "").strip().upper()
    right = str(b or "").strip().upper()
    if left <= right:
        return f"{left}|{right}"
    return f"{right}|{left}"


def merge_overlapping_event_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or not {"timestamp", "duration_minutes", "aspect", "b1", "b2"}.issubset(df.columns):
        return df.copy()

    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
    work = work.dropna(subset=["timestamp"]).copy()
    work["duration_minutes"] = pd.to_numeric(work["duration_minutes"], errors="coerce").fillna(60.0)
    work["event_end"] = work["timestamp"] + pd.to_timedelta(work["duration_minutes"], unit="m")
    work["pair_key"] = [canonical_pair(a, b) for a, b in zip(work["b1"], work["b2"], strict=False)]
    if "is_natal" not in work.columns:
        work["is_natal"] = False
    work["is_natal"] = work["is_natal"].astype(bool)
    if "closeness" not in work.columns:
        work["closeness"] = 0.0
    work["closeness"] = pd.to_numeric(work["closeness"], errors="coerce").fillna(0.0)

    work = work.sort_values(
        ["pair_key", "aspect", "is_natal", "timestamp", "event_end", "closeness"],
        ascending=[True, True, True, True, True, False],
    ).reset_index(drop=True)

    merged_rows: list[pd.Series] = []
    current_rows: list[pd.Series] = []
    current_key: tuple[str, str, bool] | None = None
    current_start: pd.Timestamp | None = None
    current_end: pd.Timestamp | None = None

    def flush_group() -> None:
        nonlocal current_rows, current_key, current_start, current_end, merged_rows
        if not current_rows:
            return
        rep = max(current_rows, key=lambda r: (float(r.get("closeness", 0.0)), -pd.Timestamp(r["timestamp"]).value))
        rep = rep.copy()
        rep["timestamp"] = current_start
        rep["event_end"] = current_end
        rep["duration_minutes"] = float((pd.Timestamp(current_end) - pd.Timestamp(current_start)).total_seconds() / 60.0)
        merged_rows.append(rep)
        current_rows = []
        current_key = None
        current_start = None
        current_end = None

    for _, row in work.iterrows():
        row_key = (str(row["pair_key"]), str(row["aspect"]), bool(row["is_natal"]))
        row_start = pd.Timestamp(row["timestamp"])
        row_end = pd.Timestamp(row["event_end"])
        if current_key is None:
            current_key = row_key
            current_rows = [row]
            current_start = row_start
            current_end = row_end
            continue

        if row_key == current_key and row_start <= pd.Timestamp(current_end):
            current_rows.append(row)
            if row_end > pd.Timestamp(current_end):
                current_end = row_end
            if row_start < pd.Timestamp(current_start):
                current_start = row_start
            continue

        flush_group()
        current_key = row_key
        current_rows = [row]
        current_start = row_start
        current_end = row_end

    flush_group()

    out = pd.DataFrame(merged_rows)
    if out.empty:
        return out
    out = out.drop(columns=["pair_key", "event_end"], errors="ignore")
    return out.reset_index(drop=True)


def main() -> None:
    args = parse_args()
    jdml4 = load_jdml4()
    patch_avg_all_parser(jdml4)

    # Point outputs to explicit files so the Desktop project is not overwritten by accident.
    jdml4.PARQUET_LOG_FILE = str(Path(args.output_file))
    jdml4.DIRECTION_SIGNAL_FILE = str(Path(args.signal_file))
    jdml4.DIRECTION_MODEL_FILE = str(PROJECT_DIR / "direction_hourly_model_v2.pkl")
    jdml4.DIRECTION_FAMILY_RANK_FILE = str(PROJECT_DIR / "event_effect_ranking_tag.csv")

    # JDML4 appends to existing parquet logs. Remove prior generated outputs first so reruns stay schema-clean.
    for generated_path in (Path(args.output_file), Path(args.signal_file)):
        if generated_path.exists():
            generated_path.unlink()

    if not args.use_default_exclusions:
        jdml4.EXCLUDED_INTERACTION_PAIRS = set()

    if args.price_parquet:
        jdml4.is_valid_ticker = lambda _ticker: True
        jdml4.fetch_stock_data = build_local_fetch_fn(args.price_parquet)

    if args.future_end_date:
        future_end_date = args.future_end_date
    else:
        end_dt = datetime.fromisoformat(args.end_date)
        future_end_date = (end_dt + timedelta(days=32)).date().isoformat()

    selected_aspects = resolve_selected_aspects(args.aspect_mode, args.selected_aspects)
    if not selected_aspects:
        raise ValueError("selected-aspects cannot be empty")

    fig, err, _, _ = jdml4.update_chart(
        submit_clicks=1,
        reset_clicks=0,
        analysis_mode=args.analysis_mode,
        ticker=args.ticker,
        interval=args.interval,
        start_date=args.start_date,
        end_date=args.end_date,
        future_end_date=future_end_date,
        coordinate_system=args.coordinate_system,
        astrology_method=args.astrology_method,
        degree_values=args.degree_values,
        celestial_bodies=args.celestial_bodies,
        exclude_planets=args.exclude_planets,
        harmonics=args.harmonics,
        n_values=args.n_values,
        selected_aspects=selected_aspects,
        aspect_mode=args.aspect_mode,
        ipo_date=args.ipo_date,
        ipo_time=args.ipo_time,
        hq_city=args.hq_city,
        hq_country=args.hq_country,
        manual_coords=args.manual_coords,
        natal_celestial_bodies=args.natal_celestial_bodies,
        reference_chart_type=args.reference_chart_type,
        stored_data=None,
    )

    if err:
        raise RuntimeError(f"JDML4 update_chart failed: {err}")
    if fig is None:
        raise RuntimeError("JDML4 returned no figure")

    out_path = Path(args.output_file)
    if not out_path.exists():
        raise RuntimeError(f"Expected output file not found: {out_path}")

    df = pd.read_parquet(out_path)
    before_rows = len(df)
    df = merge_overlapping_event_rows(df)
    if len(df) != before_rows:
        df.to_parquet(out_path, index=False)
        print(f"Merged overlapping same-pair windows: {before_rows} -> {len(df)} rows")
    print("Dataset rows:", len(df))
    if not df.empty:
        print("Date range:", df["timestamp"].min(), "->", df["timestamp"].max())
        if "is_natal" in df.columns:
            print("Transit rows:", int((~df["is_natal"].astype(bool)).sum()))
        if "aspect" in df.columns:
            print("Aspect counts:")
            print(df["aspect"].value_counts().to_string())
        if "b1" in df.columns and "b2" in df.columns:
            pair_count = (
                pd.Series(["|".join(sorted([str(a).upper(), str(b).upper()])) for a, b in zip(df["b1"], df["b2"], strict=False)])
                .nunique()
            )
            print("Unique unordered pairs:", int(pair_count))


if __name__ == "__main__":
    main()
