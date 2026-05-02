from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a canonical event ledger and pair-aspect summary from the "
            "existing astrology parquet plus the deep market window report."
        )
    )
    parser.add_argument(
        "--events",
        default=r"C:\Users\ADMIN\Desktop\Trading_Algo\New folder\astro_training_data.parquet",
    )
    parser.add_argument(
        "--windows",
        default=(
            r"C:\Users\ADMIN\Desktop\Trading_Algo\New folder"
            r"\transit_impact_deep_report\event_windows_with_regimes.csv"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=r"C:\Users\ADMIN\PycharmProjects\astro_ledger_report",
    )
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--start-date", default="2010-01-01")
    parser.add_argument("--end-date", default="2026-12-31")
    parser.add_argument("--reversal-threshold-pct", type=float, default=0.1)
    parser.add_argument(
        "--include-natal",
        action="store_true",
        default=False,
        help="Include natal events instead of dropping is_natal=true rows.",
    )
    return parser.parse_args()


def safe_json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    if isinstance(value, float) and not np.isfinite(value):
        return []
    text = str(value).strip()
    if not text:
        return []
    try:
        loaded = json.loads(text)
        return loaded if isinstance(loaded, list) else []
    except Exception:
        return []


def canonical_pair(a: Any, b: Any) -> str:
    left = str(a).upper().strip()
    right = str(b).upper().strip()
    return "|".join(sorted((left, right)))


def signed_bucket(value: Any, threshold_pct: float) -> str:
    try:
        number = float(value)
    except Exception:
        return "NA"
    if not np.isfinite(number):
        return "NA"
    if number > threshold_pct:
        return "UP"
    if number < -threshold_pct:
        return "DOWN"
    return "FLAT"


def find_primary_window(row: pd.Series) -> dict[str, Any]:
    target_pair = canonical_pair(row.get("b1", ""), row.get("b2", ""))
    target_aspect = str(row.get("aspect", "")).strip().lower()
    target_start = pd.to_datetime(row.get("timestamp"), errors="coerce")
    candidates: list[dict[str, Any]] = []

    for item in safe_json_list(row.get("event_aspects_json")):
        if not isinstance(item, dict):
            continue
        bodies = item.get("bodies", [])
        if not isinstance(bodies, list) or len(bodies) < 2:
            continue
        pair_key = canonical_pair(bodies[0], bodies[1])
        aspect = str(item.get("aspect", "")).strip().lower()
        if pair_key != target_pair or aspect != target_aspect:
            continue
        start = pd.to_datetime(item.get("start"), errors="coerce")
        end = pd.to_datetime(item.get("end"), errors="coerce")
        duration = item.get("duration_min", np.nan)
        candidates.append(
            {
                "event_window_start": start,
                "event_window_end": end,
                "event_window_duration_min": float(duration) if duration is not None else np.nan,
            }
        )

    if not candidates:
        start = target_start
        duration = pd.to_numeric(pd.Series([row.get("duration_minutes")]), errors="coerce").iloc[0]
        if pd.isna(start) or pd.isna(duration):
            return {
                "event_window_start": pd.NaT,
                "event_window_end": pd.NaT,
                "event_window_duration_min": np.nan,
            }
        return {
            "event_window_start": start,
            "event_window_end": start + pd.Timedelta(minutes=float(duration)),
            "event_window_duration_min": float(duration),
        }

    if pd.notna(target_start):
        exact = [c for c in candidates if pd.notna(c["event_window_start"]) and c["event_window_start"] == target_start]
        if exact:
            return exact[0]

    return candidates[0]


def build_ledger(
    events_df: pd.DataFrame, windows_df: pd.DataFrame, reversal_threshold_pct: float, include_natal: bool
) -> pd.DataFrame:
    df = events_df.copy()
    if "is_natal" in df.columns and not include_natal:
        df = df[~df["is_natal"].astype(bool)].copy()
    if "interval" in df.columns:
        df = df[df["interval"].astype(str).str.lower() == "1h"].copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["pair_key"] = [canonical_pair(a, b) for a, b in zip(df["b1"], df["b2"], strict=False)]
    df["planet_a"] = df["pair_key"].str.split("|").str[0]
    df["planet_b"] = df["pair_key"].str.split("|").str[1]

    window_rows = [find_primary_window(row) for _, row in df.iterrows()]
    window_df = pd.DataFrame(window_rows, index=df.index)
    df = pd.concat([df, window_df], axis=1)

    windows = windows_df.copy()
    windows["event_id"] = windows["event_id"].astype(str)
    df["event_id"] = df["event_id"].astype(str)
    df = df.merge(windows, on="event_id", how="left", suffixes=("", "_deep"))

    df["ret_pre_24h_bucket"] = df["ret_pre_24h_pct"].map(lambda x: signed_bucket(x, reversal_threshold_pct))
    df["ret_post_24h_bucket"] = df["ret_post_24h_pct"].map(lambda x: signed_bucket(x, reversal_threshold_pct))
    df["ret_post_72h_bucket"] = df["ret_post_72h_pct"].map(lambda x: signed_bucket(x, reversal_threshold_pct))
    df["reversal_24h_flag"] = (
        (df["ret_pre_24h_bucket"].isin(["UP", "DOWN"]))
        & (df["ret_post_24h_bucket"].isin(["UP", "DOWN"]))
        & (df["ret_pre_24h_bucket"] != df["ret_post_24h_bucket"])
    ).astype(int)
    df["reversal_72h_flag"] = (
        (df["ret_pre_24h_bucket"].isin(["UP", "DOWN"]))
        & (df["ret_post_72h_bucket"].isin(["UP", "DOWN"]))
        & (df["ret_pre_24h_bucket"] != df["ret_post_72h_bucket"])
    ).astype(int)
    df["overlap_count"] = df["event_aspects_json"].map(lambda x: len(safe_json_list(x)))
    return df


def summarize_family(ledger: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (pair_key, aspect), group in ledger.groupby(["pair_key", "aspect"], dropna=False, sort=True):
        y1 = group["y_dir_1d"].astype(str).str.upper()
        y3 = group["y_dir_3d"].astype(str).str.upper()
        y7 = group["y_dir_7d"].astype(str).str.upper()
        rows.append(
            {
                "pair_key": pair_key,
                "aspect": aspect,
                "samples": len(group),
                "first_event": group["timestamp"].min(),
                "last_event": group["timestamp"].max(),
                "mean_duration_min": float(pd.to_numeric(group["event_window_duration_min"], errors="coerce").mean()),
                "median_duration_min": float(pd.to_numeric(group["event_window_duration_min"], errors="coerce").median()),
                "mean_overlap_count": float(pd.to_numeric(group["overlap_count"], errors="coerce").mean()),
                "up_rate_1d": float((y1 == "UP").mean()),
                "down_rate_1d": float((y1 == "DOWN").mean()),
                "flat_rate_1d": float((y1 == "FLAT").mean()),
                "up_rate_3d": float((y3 == "UP").mean()),
                "down_rate_3d": float((y3 == "DOWN").mean()),
                "up_rate_7d": float((y7 == "UP").mean()),
                "down_rate_7d": float((y7 == "DOWN").mean()),
                "mean_delta_1d_pct": float(pd.to_numeric(group["delta_1d"], errors="coerce").mean()),
                "median_delta_1d_pct": float(pd.to_numeric(group["delta_1d"], errors="coerce").median()),
                "mean_delta_3d_pct": float(pd.to_numeric(group["delta_3d"], errors="coerce").mean()),
                "mean_delta_7d_pct": float(pd.to_numeric(group["delta_7d"], errors="coerce").mean()),
                "mean_ret_pre_24h_pct": float(pd.to_numeric(group["ret_pre_24h_pct"], errors="coerce").mean()),
                "mean_ret_post_24h_pct": float(pd.to_numeric(group["ret_post_24h_pct"], errors="coerce").mean()),
                "median_ret_post_24h_pct": float(pd.to_numeric(group["ret_post_24h_pct"], errors="coerce").median()),
                "mean_ret_post_72h_pct": float(pd.to_numeric(group["ret_post_72h_pct"], errors="coerce").mean()),
                "positive_post24_rate": float((group["ret_post_24h_bucket"] == "UP").mean()),
                "negative_post24_rate": float((group["ret_post_24h_bucket"] == "DOWN").mean()),
                "reversal_24h_rate": float(pd.to_numeric(group["reversal_24h_flag"], errors="coerce").mean()),
                "reversal_72h_rate": float(pd.to_numeric(group["reversal_72h_flag"], errors="coerce").mean()),
                "break_rate": float((group["y_sr_reaction"].astype(str).str.upper() == "BREAK").mean()),
                "bounce_rate": float((group["y_sr_reaction"].astype(str).str.upper() == "BOUNCE").mean()),
                "avg_shadbala": float(pd.to_numeric(group["avg_shadbala"], errors="coerce").mean()),
            }
        )

    return pd.DataFrame(rows).sort_values(["pair_key", "aspect"]).reset_index(drop=True)


def summarize_regime(ledger: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = ledger.groupby(["pair_key", "aspect", "trend_regime", "vol_regime"], dropna=False, sort=True)
    for (pair_key, aspect, trend_regime, vol_regime), group in grouped:
        rows.append(
            {
                "pair_key": pair_key,
                "aspect": aspect,
                "trend_regime": trend_regime,
                "vol_regime": vol_regime,
                "samples": len(group),
                "up_rate_1d": float((group["y_dir_1d"].astype(str).str.upper() == "UP").mean()),
                "down_rate_1d": float((group["y_dir_1d"].astype(str).str.upper() == "DOWN").mean()),
                "mean_ret_post_24h_pct": float(pd.to_numeric(group["ret_post_24h_pct"], errors="coerce").mean()),
                "mean_ret_post_72h_pct": float(pd.to_numeric(group["ret_post_72h_pct"], errors="coerce").mean()),
                "reversal_24h_rate": float(pd.to_numeric(group["reversal_24h_flag"], errors="coerce").mean()),
                "break_rate": float((group["y_sr_reaction"].astype(str).str.upper() == "BREAK").mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["pair_key", "aspect", "trend_regime", "vol_regime"]).reset_index(drop=True)


def write_summary(out_dir: Path, ledger: pd.DataFrame, family: pd.DataFrame) -> None:
    top_counts = family.sort_values(["samples", "pair_key", "aspect"], ascending=[False, True, True]).head(15)
    strongest_positive = family.sort_values(["mean_delta_1d_pct", "samples"], ascending=[False, False]).head(15)
    strongest_negative = family.sort_values(["mean_delta_1d_pct", "samples"], ascending=[True, False]).head(15)

    lines = [
        "=== Event Pair Ledger Summary ===",
        f"Ledger rows: {len(ledger)}",
        f"Date range: {ledger['timestamp'].min()} -> {ledger['timestamp'].max()}",
        f"Unique pair-aspect families: {len(family)}",
        "",
        "Largest families:",
    ]
    lines.extend(
        top_counts[["pair_key", "aspect", "samples", "mean_delta_1d_pct", "reversal_24h_rate"]]
        .to_string(index=False)
        .splitlines()
    )
    lines.extend(["", "Most positive mean 1d families:"])
    lines.extend(
        strongest_positive[["pair_key", "aspect", "samples", "mean_delta_1d_pct", "up_rate_1d", "reversal_24h_rate"]]
        .to_string(index=False)
        .splitlines()
    )
    lines.extend(["", "Most negative mean 1d families:"])
    lines.extend(
        strongest_negative[["pair_key", "aspect", "samples", "mean_delta_1d_pct", "down_rate_1d", "reversal_24h_rate"]]
        .to_string(index=False)
        .splitlines()
    )
    (out_dir / "summary.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    events = pd.read_parquet(args.events)
    windows = pd.read_csv(args.windows)
    ledger = build_ledger(events, windows, args.reversal_threshold_pct, args.include_natal)

    tzinfo = getattr(ledger["timestamp"].dt, "tz", None)
    start = pd.to_datetime(args.start_date)
    end = pd.to_datetime(args.end_date)
    if tzinfo is not None:
        if start.tzinfo is None:
            start = start.tz_localize(tzinfo)
        else:
            start = start.tz_convert(tzinfo)
        if end.tzinfo is None:
            end = end.tz_localize(tzinfo)
        else:
            end = end.tz_convert(tzinfo)
    ledger = ledger[(ledger["timestamp"] >= start) & (ledger["timestamp"] <= end)].copy()
    family = summarize_family(ledger)
    regime = summarize_regime(ledger)

    ledger.to_csv(out_dir / "event_pair_ledger.csv", index=False)
    family.to_csv(out_dir / "event_pair_family_summary.csv", index=False)
    regime.to_csv(out_dir / "event_pair_family_regime_summary.csv", index=False)
    write_summary(out_dir, ledger, family)

    print((out_dir / "summary.txt").read_text(encoding="utf-8"))
    print()
    print("Saved:", out_dir / "event_pair_ledger.csv")
    print("Saved:", out_dir / "event_pair_family_summary.csv")
    print("Saved:", out_dir / "event_pair_family_regime_summary.csv")


if __name__ == "__main__":
    main()
