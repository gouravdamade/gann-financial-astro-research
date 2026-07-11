from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from build_btc_weekly_astro_chart import (
    ASPECTS,
    BODY_ORDER,
    GENESIS_UTC,
    IST,
    PLACE_HYPOTHESES,
    birth_chart,
    build_aspect_windows,
    build_daily_transits,
    configure_ephemeris,
    fetch_binance_weekly,
)


DEFAULT_OUTPUT_ROOT = Path(r"D:\GannFinancialAstro\doc")
MACRO_CORE = {"JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"}
CAPRICORN_STELLIUM = {"SUN", "MARS", "PLUTO"}
FAST_INNER = {"MERCURY", "VENUS"}
NODE_SET = {"RAHU", "KETU"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score BTC weekly aspect families against historical turns/trends.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--place", choices=sorted(PLACE_HYPOTHESES), default="van_nuys")
    parser.add_argument("--start", default="2017-08-01")
    parser.add_argument("--end", default=(pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=8)).strftime("%Y-%m-%d"))
    parser.add_argument("--min-window-days", type=float, default=21.0)
    parser.add_argument("--turn-context-weeks", type=int, default=7)
    parser.add_argument("--short-max-weeks", type=float, default=7.0)
    parser.add_argument("--long-min-weeks", type=float, default=8.0)
    parser.add_argument("--move-threshold-pct", type=float, default=5.0)
    return parser.parse_args()


def candle_pattern(row: pd.Series, prior: pd.Series | None) -> str:
    open_ = float(row["open"])
    high = float(row["high"])
    low = float(row["low"])
    close = float(row["close"])
    candle_range = max(high - low, 1e-9)
    body = abs(close - open_)
    upper = high - max(open_, close)
    lower = min(open_, close) - low
    tags: list[str] = []
    if body / candle_range <= 0.10:
        tags.append("doji")
    if lower >= 2.0 * max(body, candle_range * 0.03) and upper <= max(body, candle_range * 0.20):
        tags.append("hammer_like")
    if upper >= 2.0 * max(body, candle_range * 0.03) and lower <= max(body, candle_range * 0.20):
        tags.append("shooting_star_like")
    if close > open_ and body / candle_range >= 0.60:
        tags.append("large_green_body")
    if close < open_ and body / candle_range >= 0.60:
        tags.append("large_red_body")
    if prior is not None:
        p_open = float(prior["open"])
        p_high = float(prior["high"])
        p_low = float(prior["low"])
        p_close = float(prior["close"])
        if close > open_ and p_close < p_open and open_ <= p_close and close >= p_open:
            tags.append("bullish_engulfing")
        if close < open_ and p_close > p_open and open_ >= p_close and close <= p_open:
            tags.append("bearish_engulfing")
        if high <= p_high and low >= p_low:
            tags.append("inside_bar")
        if high >= p_high and low <= p_low:
            tags.append("outside_bar")
    if not tags:
        tags.append("plain_weekly_candle")
    return ";".join(tags)


def research_bucket(transit_body: str, natal_body: str) -> str:
    bodies = {transit_body, natal_body}
    if bodies & {"SATURN", "URANUS"}:
        return "high_priority_saturn_uranus"
    if bodies & {"JUPITER", "NEPTUNE", "PLUTO"}:
        return "macro_core_jupiter_outer"
    if bodies & CAPRICORN_STELLIUM:
        return "btc_capricorn_stellium_related"
    if bodies <= FAST_INNER:
        return "likely_weekly_noise_fast_inner"
    if bodies & NODE_SET:
        return "node_related_experimental"
    return "general_experimental"


def locate_candle(price: pd.DataFrame, ts: pd.Timestamp) -> int | None:
    containing = price[(price["open_time_utc"] <= ts) & (price["close_time_utc"] >= ts)]
    if not containing.empty:
        return int(containing.index[0])
    later = price[price["open_time_utc"] >= ts]
    if not later.empty:
        return int(later.index[0])
    return None


def pct_return(entry: float, exit_: float) -> float:
    if not np.isfinite(entry) or not np.isfinite(exit_) or entry == 0:
        return float("nan")
    return (exit_ / entry - 1.0) * 100.0


def label_return(value: float, threshold: float) -> str:
    if not np.isfinite(value):
        return "not_available"
    if value >= threshold:
        return "bullish"
    if value <= -threshold:
        return "bearish"
    return "flat"


def behavior_signal(evaluation_mode: str, turn_role: str, start_end_direction: str) -> str:
    if evaluation_mode == "turn_timing":
        if turn_role == "trough":
            return "bullish"
        if turn_role == "crest":
            return "bearish"
        if turn_role == "crest_and_trough":
            return "mixed"
        return "no_signal"
    if evaluation_mode == "trend_exposure":
        if start_end_direction in {"bullish", "bearish"}:
            return start_end_direction
        return "no_signal"
    return "no_signal"


def analyze_event(price: pd.DataFrame, row: pd.Series, args: argparse.Namespace) -> dict[str, Any]:
    start_ts = pd.Timestamp(row["start_utc"])
    end_ts = pd.Timestamp(row["end_utc"])
    start_ix = locate_candle(price, start_ts)
    end_ix = locate_candle(price, end_ts)
    if start_ix is None or end_ix is None:
        return {
            "analysis_status": "outside_price_history",
            "family_key": f"{row['transit_body']}|{row['natal_body']}::{row['aspect']}",
        }
    end_ix = min(end_ix, len(price) - 1)
    start_ix = max(0, start_ix)
    if end_ix < start_ix:
        end_ix = start_ix

    prior_start = price.iloc[start_ix - 1] if start_ix > 0 else None
    prior_end = price.iloc[end_ix - 1] if end_ix > 0 else None
    entry_price = float(price.iloc[start_ix]["open"])
    exit_price = float(price.iloc[end_ix]["close"])
    start_end_return_pct = pct_return(entry_price, exit_price)
    duration_days = float(row["duration_days"])
    duration_weeks = duration_days / 7.0

    context = int(args.turn_context_weeks)
    context_start = max(0, start_ix - context)
    context_end = min(len(price) - 1, end_ix + context)
    context_slice = price.iloc[context_start : context_end + 1]
    local_high_pos = int(context_slice["high"].astype(float).values.argmax())
    local_low_pos = int(context_slice["low"].astype(float).values.argmin())
    local_high_ix = int(context_slice.index[local_high_pos])
    local_low_ix = int(context_slice.index[local_low_pos])
    crest_inside = start_ix <= local_high_ix <= end_ix
    trough_inside = start_ix <= local_low_ix <= end_ix
    dist_to_crest_weeks = min(abs(local_high_ix - start_ix), abs(local_high_ix - end_ix)) if not crest_inside else 0
    dist_to_trough_weeks = min(abs(local_low_ix - start_ix), abs(local_low_ix - end_ix)) if not trough_inside else 0

    if duration_weeks <= float(args.short_max_weeks):
        evaluation_mode = "turn_timing"
    elif duration_weeks >= float(args.long_min_weeks):
        evaluation_mode = "trend_exposure"
    else:
        evaluation_mode = "transition_band_logged_only"

    if crest_inside and trough_inside:
        turn_role = "crest_and_trough"
    elif crest_inside:
        turn_role = "crest"
    elif trough_inside:
        turn_role = "trough"
    else:
        turn_role = "no_local_turn_inside"
    direction_label = label_return(start_end_return_pct, float(args.move_threshold_pct))
    signal = behavior_signal(evaluation_mode, turn_role, direction_label)

    return {
        "analysis_status": "ok",
        "family_key": f"{row['transit_body']}|{row['natal_body']}::{row['aspect']}",
        "transit_body": row["transit_body"],
        "natal_body": row["natal_body"],
        "aspect": row["aspect"],
        "research_bucket": research_bucket(str(row["transit_body"]), str(row["natal_body"])),
        "start_utc": row["start_utc"],
        "end_utc": row["end_utc"],
        "start_ist": row["start_ist"],
        "end_ist": row["end_ist"],
        "duration_days": duration_days,
        "duration_weeks": duration_weeks,
        "evaluation_mode": evaluation_mode,
        "entry_time_ist": price.iloc[start_ix]["open_time_ist"],
        "exit_time_ist": price.iloc[end_ix]["close_time_ist"],
        "entry_open": entry_price,
        "exit_close": exit_price,
        "start_end_return_pct": start_end_return_pct,
        "start_end_direction": direction_label,
        "behavior_signal": signal,
        "local_high_time_ist": price.iloc[local_high_ix]["open_time_ist"],
        "local_high": float(price.iloc[local_high_ix]["high"]),
        "local_low_time_ist": price.iloc[local_low_ix]["open_time_ist"],
        "local_low": float(price.iloc[local_low_ix]["low"]),
        "crest_inside_window": bool(crest_inside),
        "trough_inside_window": bool(trough_inside),
        "turn_role": turn_role,
        "distance_to_crest_weeks": int(dist_to_crest_weeks),
        "distance_to_trough_weeks": int(dist_to_trough_weeks),
        "start_candle_pattern": candle_pattern(price.iloc[start_ix], prior_start),
        "end_candle_pattern": candle_pattern(price.iloc[end_ix], prior_end),
        "turn_candle_pattern": candle_pattern(price.iloc[local_high_ix if crest_inside else local_low_ix], None)
        if (crest_inside or trough_inside)
        else "",
        "peak_orb_deg": row.get("peak_orb_deg", np.nan),
    }


def top_patterns(values: pd.Series, limit: int = 3) -> str:
    counter: Counter[str] = Counter()
    for text in values.dropna().astype(str):
        for tag in text.split(";"):
            if tag:
                counter[tag] += 1
    return ", ".join(f"{name}:{count}" for name, count in counter.most_common(limit))


def classify_family(occurrences: int, dominant_rate: float, directional_rate: float) -> tuple[str, str]:
    if occurrences < 3:
        return (
            "inconclusive_low_repeatation",
            "fewer than 3 repeatations; keep logged but do not suppress or promote yet",
        )
    if directional_rate < 0.30:
        return (
            "noise",
            "less than 30% of repeatations produced a clear bullish/bearish behavior",
        )
    if dominant_rate >= 0.70:
        return (
            "promising_candidate",
            "at least 70% of repeatations lean the same bullish/bearish way",
        )
    return (
        "inconclusive",
        "directional behavior exists, but dominance is below 70%; keep for more evidence",
    )


def summarize(events: pd.DataFrame) -> pd.DataFrame:
    ok = events[events["analysis_status"] == "ok"].copy()
    rows: list[dict[str, Any]] = []
    for family, group in ok.groupby("family_key"):
        short = group[group["evaluation_mode"] == "turn_timing"]
        long = group[group["evaluation_mode"] == "trend_exposure"]
        returns = pd.to_numeric(group["start_end_return_pct"], errors="coerce")
        pos_rate = float((returns > 0).mean()) if len(returns) else np.nan
        neg_rate = float((returns < 0).mean()) if len(returns) else np.nan
        consistency = max(pos_rate, neg_rate) if np.isfinite(pos_rate) and np.isfinite(neg_rate) else np.nan
        crest_flags = short["crest_inside_window"].fillna(False).astype(bool)
        trough_flags = short["trough_inside_window"].fillna(False).astype(bool)
        turn_hits = int((crest_flags | trough_flags).sum())
        turn_rate = turn_hits / len(short) if len(short) else np.nan
        long_returns = pd.to_numeric(long["start_end_return_pct"], errors="coerce")
        avg_abs_return = float(returns.abs().mean()) if len(returns.dropna()) else np.nan
        evidence_score = (
            (0.0 if math.isnan(turn_rate) else turn_rate * 45.0)
            + (0.0 if math.isnan(avg_abs_return) else min(avg_abs_return, 80.0) * 0.55)
            + (0.0 if math.isnan(consistency) else consistency * 25.0)
            + min(len(group), 10) * 1.5
        )
        sample_confidence = min(1.0, len(group) / 3.0)
        review_priority_score = evidence_score * sample_confidence
        behavior_counts = group["behavior_signal"].fillna("no_signal").value_counts()
        bullish_count = int(behavior_counts.get("bullish", 0))
        bearish_count = int(behavior_counts.get("bearish", 0))
        mixed_count = int(behavior_counts.get("mixed", 0))
        no_signal_count = int(behavior_counts.get("no_signal", 0))
        dominant_count = max(bullish_count, bearish_count)
        dominant_behavior = "bullish" if bullish_count >= bearish_count else "bearish"
        dominant_rate = dominant_count / len(group) if len(group) else np.nan
        directional_rate = (bullish_count + bearish_count) / len(group) if len(group) else np.nan
        classification, classification_reason = classify_family(
            int(len(group)),
            0.0 if math.isnan(dominant_rate) else dominant_rate,
            0.0 if math.isnan(directional_rate) else directional_rate,
        )
        sample = group.iloc[0]
        rows.append(
            {
                "family_key": family,
                "research_bucket": sample["research_bucket"],
                "occurrences": int(len(group)),
                "classification": classification,
                "classification_reason": classification_reason,
                "dominant_behavior": dominant_behavior,
                "dominant_behavior_rate": dominant_rate,
                "directional_signal_rate": directional_rate,
                "bullish_behavior_count": bullish_count,
                "bearish_behavior_count": bearish_count,
                "mixed_behavior_count": mixed_count,
                "no_signal_count": no_signal_count,
                "sample_confidence": sample_confidence,
                "avg_duration_days": float(pd.to_numeric(group["duration_days"], errors="coerce").mean()),
                "short_turn_windows": int(len(short)),
                "short_turn_hits": turn_hits,
                "short_turn_hit_rate": turn_rate,
                "crest_hits": int(crest_flags.sum()),
                "trough_hits": int(trough_flags.sum()),
                "long_trend_windows": int(len(long)),
                "long_avg_return_pct": float(long_returns.mean()) if len(long_returns.dropna()) else np.nan,
                "long_median_return_pct": float(long_returns.median()) if len(long_returns.dropna()) else np.nan,
                "all_avg_return_pct": float(returns.mean()) if len(returns.dropna()) else np.nan,
                "all_median_return_pct": float(returns.median()) if len(returns.dropna()) else np.nan,
                "directional_consistency_rate": consistency,
                "positive_return_rate": pos_rate,
                "negative_return_rate": neg_rate,
                "avg_abs_return_pct": avg_abs_return,
                "top_start_patterns": top_patterns(group["start_candle_pattern"]),
                "top_end_patterns": top_patterns(group["end_candle_pattern"]),
                "evidence_score": evidence_score,
                "review_priority_score": review_priority_score,
            }
        )
    summary = pd.DataFrame.from_records(rows)
    if summary.empty:
        return summary
    classification_rank = {
        "promising_candidate": 0,
        "inconclusive": 1,
        "inconclusive_low_repeatation": 2,
        "noise": 3,
    }
    summary["classification_rank"] = summary["classification"].map(classification_rank).fillna(9).astype(int)
    return summary.sort_values(
        ["classification_rank", "review_priority_score", "occurrences"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


def write_notes(output_dir: Path, metadata: dict[str, Any], summary: pd.DataFrame) -> None:
    def fmt(value: Any, digits: int = 2) -> str:
        try:
            numeric = float(value)
        except Exception:
            return "n/a"
        if not math.isfinite(numeric):
            return "n/a"
        return f"{numeric:.{digits}f}"

    top = summary.head(20)
    rows = []
    for _, row in top.iterrows():
        rows.append(
            f"| `{row['family_key']}` | {row['occurrences']} | {row['classification']} | "
            f"{row['dominant_behavior']} {fmt(row['dominant_behavior_rate'])} | "
            f"{fmt(row['directional_signal_rate'])} | {row['research_bucket']} | "
            f"{fmt(row['review_priority_score'], 1)} |"
        )
    table = "\n".join(rows)
    text = f"""# BTC Aspect Effectiveness Evidence

Generated: {metadata['generated_at_ist']}

This is an evidence log, not a trading signal. It is meant to reduce chart noise by ranking BTC weekly aspect families against actual historical weekly behavior.

## R&D Starting Priors

- AstroConnexions argues Bitcoin work should focus on transits to radix, mainly Jupiter, Saturn, Uranus, Neptune, and Pluto, and specifically notes Saturn/Uranus themes.
- SG AppDev focuses on Sun-Jupiter aspects plus Sun-to-Saturn/Uranus/Neptune/Pluto dates, then counts historical market-movement occurrences.
- WIRED reports that crypto astrologers disagree on methods, but mentions Saturn natal transits/pullbacks, Bitcoin's Sun/Mars/Pluto Capricorn stellium, and Jupiter/outer-planet combinations.

The script therefore logs all current non-Moon bodies first, then marks a `research_bucket` so we can later suppress lower-value families instead of guessing.

## Evaluation Rules

- Aspect windows shorter than `{metadata['min_window_days']}` days are excluded.
- Windows `<= {metadata['short_max_weeks']}` weeks are evaluated as turn timing: did a local crest or trough occur inside the aspect window, using a +/- `{metadata['turn_context_weeks']}` week context?
- Windows `>= {metadata['long_min_weeks']}` weeks are evaluated as trend exposure: enter at the first weekly candle containing/after aspect start and exit at the candle containing/after aspect end.
- Candlestick comments are simple deterministic labels: doji, hammer-like, shooting-star-like, engulfing, inside/outside bar, large body.
- Family classification:
  - `promising_candidate`: at least 3 repeatations and >= 70% dominance in one bullish/bearish behavior.
  - `inconclusive`: at least 3 repeatations, not noise, but below 70% dominance.
  - `inconclusive_low_repeatation`: fewer than 3 repeatations; kept logged because future data can change the classification.
  - `noise`: at least 3 repeatations and less than 30% clear bullish/bearish behavior.

## Top Evidence Families

| family | occurrences | classification | dominant behavior | directional signal rate | bucket | review priority |
|---|---:|---|---:|---:|---|---:|
{table}

## Outputs

- `btc_aspect_effectiveness_events.csv`: event-level evidence.
- `btc_aspect_effectiveness_summary.csv`: family-level ranking.
- `btc_aspect_promising_candidates.csv`: families meeting the >= 70% dominance rule.
- `btc_aspect_inconclusive_candidates.csv`: inconclusive families, including all repeatations < 3.
- `btc_aspect_noise_candidates.csv`: families excluded from chart overlays.
- `btc_aspect_effectiveness_metadata.json`: assumptions and source URLs.
"""
    (output_dir / "btc_aspect_effectiveness_notes.md").write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    configure_ephemeris()
    place = PLACE_HYPOTHESES[args.place]
    start = pd.Timestamp(args.start, tz="UTC")
    end = pd.Timestamp(args.end, tz="UTC")
    stamp = pd.Timestamp.now(tz=IST).strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_root) / f"btc_aspect_effectiveness_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    price = fetch_binance_weekly(start, end)
    daily = build_daily_transits(price["open_time_utc"].min(), price["open_time_utc"].max())
    metadata = birth_chart(place)
    metadata.update(
        {
            "generated_at_ist": pd.Timestamp.now(tz=IST).isoformat(),
            "price_start_ist": price["open_time_ist"].min().isoformat(),
            "price_end_ist": price["open_time_ist"].max().isoformat(),
            "genesis_utc": GENESIS_UTC.isoformat(),
            "min_window_days": args.min_window_days,
            "turn_context_weeks": args.turn_context_weeks,
            "short_max_weeks": args.short_max_weeks,
            "long_min_weeks": args.long_min_weeks,
            "move_threshold_pct": args.move_threshold_pct,
            "excluded": {
                "moon": True,
                "rahu_ketu_pair": True,
            },
            "aspects": list(ASPECTS.keys()),
            "bodies": list(BODY_ORDER),
            "sources": [
                "https://astroconnexions.com/bitcoin/bitcoin-the-astrology/",
                "https://www.sgappdev.com/cryptoplanetaryaspects.htm",
                "https://www.wired.com/story/crypto-astrologers-predictions/",
            ],
        }
    )

    windows = build_aspect_windows(daily, metadata["natal_longitudes"], args.min_window_days)
    records = [analyze_event(price, row, args) for _, row in windows.iterrows()]
    events = pd.DataFrame.from_records(records)
    summary = summarize(events)

    price.to_csv(output_dir / "btc_weekly_price_binance.csv", index=False)
    windows.to_csv(output_dir / "btc_aspect_windows_historical.csv", index=False)
    events.to_csv(output_dir / "btc_aspect_effectiveness_events.csv", index=False)
    summary.to_csv(output_dir / "btc_aspect_effectiveness_summary.csv", index=False)
    summary[summary["classification"] == "promising_candidate"].to_csv(
        output_dir / "btc_aspect_promising_candidates.csv",
        index=False,
    )
    summary[summary["classification"].isin(["inconclusive", "inconclusive_low_repeatation"])].to_csv(
        output_dir / "btc_aspect_inconclusive_candidates.csv",
        index=False,
    )
    summary[summary["classification"] == "noise"].to_csv(
        output_dir / "btc_aspect_noise_candidates.csv",
        index=False,
    )
    (output_dir / "btc_aspect_effectiveness_metadata.json").write_text(
        json.dumps(metadata, indent=2, default=str),
        encoding="utf-8",
    )
    write_notes(output_dir, metadata, summary)

    print(f"Output dir: {output_dir}")
    print(f"Historical windows >= {args.min_window_days:g}d: {len(windows)}")
    print(f"Analyzed events: {len(events)}")
    print(f"Families: {len(summary)}")
    if not summary.empty:
        counts = summary["classification"].value_counts().to_dict()
        print(f"Classifications: {counts}")
    if not summary.empty:
        print("Top families:")
        print(
            summary[
                [
                    "family_key",
                    "occurrences",
                    "classification",
                    "dominant_behavior",
                    "dominant_behavior_rate",
                    "directional_signal_rate",
                    "review_priority_score",
                ]
            ]
            .head(10)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
