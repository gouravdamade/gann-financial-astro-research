from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_INVENTORY = Path(r"D:\PycharmProjects\case_id_feature_inventory_transitsign_20260516_0132.csv")
DEFAULT_OUTPUT = Path(r"D:\PycharmProjects\manual_case_review_sheet_transitsign_20260516_0145.csv")
DEFAULT_FOCUS_OUTPUT = Path(
    r"D:\PycharmProjects\manual_case_review_focus_transitsign_20260516_0145.csv"
)

MANUAL_COLUMNS = [
    "review_status",
    "manual_direction_label",
    "manual_behavior_label",
    "manual_trade_action",
    "manual_confidence",
    "manual_reason_tags",
    "manual_notes",
    "reviewed_by",
    "reviewed_at_ist",
]

MANUAL_COLUMN_HINTS = {
    "review_status": "blank | reviewed | revisit",
    "manual_direction_label": "bullish | bearish | sideways | mixed | unclear",
    "manual_behavior_label": "clean_followthrough | reversal | choppy | fakeout | no_trade | unclear",
    "manual_trade_action": "take_long | take_short | avoid | wait | study_more",
    "manual_confidence": "low | medium | high",
    "manual_reason_tags": "semicolon tags, e.g. enemy_sign; multiple_aspects; low_shadbala",
    "manual_notes": "free-form human observation for future ML/rule mining",
    "reviewed_by": "your name/initials",
    "reviewed_at_ist": "YYYY-MM-DD HH:MM IST",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a manual review sheet from the case_id feature inventory. "
            "The output keeps one row per case_id, adds recurrence summaries, "
            "probable factor tags, and blank human review columns."
        )
    )
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-focus-csv", type=Path, default=DEFAULT_FOCUS_OUTPUT)
    return parser.parse_args()


def text_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and np.isnan(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "nat"}:
        return ""
    return text


def numeric_value(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except Exception:
        return default
    if not np.isfinite(parsed):
        return default
    return parsed


def parse_counts(text: Any) -> Counter[str]:
    counts: Counter[str] = Counter()
    raw = text_value(text)
    if not raw:
        return counts
    for part in raw.split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        try:
            counts[key.strip()] += int(float(value.strip()))
        except Exception:
            continue
    return counts


def join_counts(values: pd.Series) -> str:
    counts: Counter[str] = Counter()
    for value in values:
        counts.update(parse_counts(value))
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def direction_counts(values: pd.Series) -> str:
    clean = [text_value(value) for value in values]
    clean = [value for value in clean if value]
    counts = Counter(clean)
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def mode_value(values: pd.Series) -> str:
    clean = [text_value(value) for value in values]
    clean = [value for value in clean if value]
    if not clean:
        return ""
    counts = Counter(clean)
    return counts.most_common(1)[0][0]


def observed_return_bias(value: Any) -> str:
    signed = numeric_value(value, default=np.nan)
    if not np.isfinite(signed):
        return ""
    if signed > 0.05:
        return "bullish_return"
    if signed < -0.05:
        return "bearish_return"
    return "flat_or_small_return"


def probable_factor_tags(row: pd.Series) -> list[str]:
    tags: list[str] = []
    if numeric_value(row.get("csv_occurrence_count")) <= 0:
        tags.append("not_in_current_candidate_csv")
    if numeric_value(row.get("csv_occurrence_count")) >= 2:
        tags.append("repeated_across_timeframes")
    if numeric_value(row.get("same_aspect_group_size")) >= 10:
        tags.append("high_recurrence_group")
    if numeric_value(row.get("aspect_regime_active_count")) >= 2:
        tags.append("multiple_active_aspects")
    if numeric_value(row.get("aspect_regime_active_count")) >= 4:
        tags.append("crowded_regime")
    if numeric_value(row.get("fx_doctrine_pair_conflict_ratio")) >= 0.45:
        tags.append("high_fx_doctrine_conflict")
    if numeric_value(row.get("fx_pair_conflict_ratio")) >= 0.45:
        tags.append("high_legacy_fx_conflict")
    shadbala = numeric_value(row.get("shadbala_avg"), default=np.nan)
    if np.isfinite(shadbala):
        if shadbala < 50:
            tags.append("low_shadbala")
        elif shadbala >= 57:
            tags.append("strong_shadbala")
    if numeric_value(row.get("quote_enemy_component_count")) > 0:
        tags.append("quote_enemy_sign")
    if numeric_value(row.get("base_enemy_component_count")) > 0:
        tags.append("base_enemy_sign")
    if numeric_value(row.get("quote_debilitation_component_count")) > 0:
        tags.append("quote_debilitation")
    if numeric_value(row.get("base_debilitation_component_count")) > 0:
        tags.append("base_debilitation")
    if numeric_value(row.get("quote_unknown_dignity_component_count")) > 0 or numeric_value(row.get("base_unknown_dignity_component_count")) > 0:
        tags.append("unknown_outer_or_node_dignity")
    if "malefic + malefic" in text_value(row.get("pair_nature_summary")):
        tags.append("malefic_pair")
    if "mixed_classical" in text_value(row.get("pair_nature_summary")):
        tags.append("avg_all_composite")
    if text_value(row.get("duration_bucket")) == "position_gt_5d":
        tags.append("long_duration_gt_5d")
    elif text_value(row.get("duration_bucket")) == "swing_1d_to_5d":
        tags.append("swing_duration_1d_to_5d")
    if text_value(row.get("aspect_family")) == "hard":
        tags.append("hard_aspect")
    elif text_value(row.get("aspect_family")) == "soft":
        tags.append("soft_aspect")
    if "WIN=" in text_value(row.get("ml_outcome_counts")) and "LOSS=" in text_value(row.get("ml_outcome_counts")):
        tags.append("mixed_candidate_outcomes")
    return tags


def probable_factor_note(row: pd.Series) -> str:
    parts: list[str] = []
    shadbala = text_value(row.get("shadbala_avg"))
    if shadbala:
        parts.append(f"shadbala_avg={float(shadbala):.2f}")
    for label, column in [
        ("quote_dignity", "quote_dignity_label_counts"),
        ("base_dignity", "base_dignity_label_counts"),
        ("fx_doctrine", "fx_doctrine_hypothesis_direction"),
        ("fx_doctrine_net", "fx_doctrine_pair_net_score"),
        ("fx_conflict", "fx_doctrine_pair_conflict_ratio"),
        ("regime_active", "aspect_regime_active_count"),
        ("ml", "ml_outcome_counts"),
    ]:
        value = text_value(row.get(column))
        if value:
            parts.append(f"{label}={value}")
    return " | ".join(parts)


def build_review_sheet(inventory: pd.DataFrame) -> pd.DataFrame:
    df = inventory.copy()
    df["same_aspect_group_key"] = df["pair_key"].astype(str) + " :: " + df["aspect"].astype(str)

    grouped = df.groupby("same_aspect_group_key", sort=False)
    group_summary = grouped.agg(
        same_aspect_group_size=("case_id", "count"),
        group_csv_occurrence_total=("csv_occurrence_count", "sum"),
        group_m30_total=("csv_m30_count", "sum"),
        group_hourly_total=("csv_hourly_count", "sum"),
        group_daily_total=("csv_daily_count", "sum"),
        group_avg_shadbala=("shadbala_avg", "mean"),
        group_avg_fx_doctrine_net=("fx_doctrine_pair_net_score", "mean"),
        group_avg_fx_doctrine_conflict=("fx_doctrine_pair_conflict_ratio", "mean"),
        group_avg_return_pct=("avg_signed_return_pct", "mean"),
    ).reset_index()
    group_summary["group_ml_outcomes"] = grouped["ml_outcome_counts"].apply(join_counts).values
    group_summary["group_close_actions"] = grouped["close_action_counts"].apply(join_counts).values
    group_summary["group_fx_doctrine_directions"] = grouped["fx_doctrine_hypothesis_direction"].apply(direction_counts).values
    group_summary["group_script_direction_mode"] = grouped["fx_doctrine_hypothesis_direction"].apply(mode_value).values

    df = df.merge(group_summary, on="same_aspect_group_key", how="left")
    df["script_observed_return_bias"] = df["avg_signed_return_pct"].apply(observed_return_bias)
    df["probable_factor_tags"] = df.apply(lambda row: "; ".join(probable_factor_tags(row)), axis=1)
    df["probable_factor_note"] = df.apply(probable_factor_note, axis=1)

    for column in MANUAL_COLUMNS:
        df[column] = ""
    df["manual_column_hints"] = ""
    for idx, column in enumerate(MANUAL_COLUMNS):
        if idx < len(df):
            df.loc[df.index[idx], "manual_column_hints"] = f"{column}: {MANUAL_COLUMN_HINTS[column]}"

    ordered_columns = [
        "case_id",
        "same_aspect_group_key",
        "same_aspect_group_size",
        "group_script_direction_mode",
        "group_fx_doctrine_directions",
        "group_ml_outcomes",
        "group_close_actions",
        "group_csv_occurrence_total",
        "group_m30_total",
        "group_hourly_total",
        "group_daily_total",
        "group_avg_shadbala",
        "group_avg_fx_doctrine_net",
        "group_avg_fx_doctrine_conflict",
        "group_avg_return_pct",
        *MANUAL_COLUMNS,
        "manual_column_hints",
        "probable_factor_tags",
        "probable_factor_note",
        "script_observed_return_bias",
        "pair_key",
        "b1",
        "b1_natural_class",
        "b1_natural_bias",
        "b2",
        "b2_natural_class",
        "b2_natural_bias",
        "pair_nature_summary",
        "aspect",
        "aspect_label",
        "aspect_family",
        "window_start_ist",
        "window_end_ist",
        "case_timeframe_bucket",
        "csv_occurrence_count",
        "csv_m30_count",
        "csv_hourly_count",
        "csv_daily_count",
        "csv_timeframes_present",
        "potential_trade_count",
        "ignored_trade_count",
        "ml_win_count",
        "ml_loss_count",
        "ml_ignore_count",
        "ml_win_rate",
        "ml_outcome_counts",
        "close_action_counts",
        "signal_direction_counts",
        "trade_category_counts",
        "ignore_reason_counts",
        "avg_signed_return_pct",
        "avg_mfe_pct",
        "avg_mae_pct",
        "event_duration_minutes",
        "duration_bucket",
        "event_orb_deg",
        "event_orb_limit_deg",
        "event_orb_strength",
        "event_bphs_strength",
        "event_bphs_virupa",
        "shadbala_tag",
        "shadbala_avg",
        "moon_nakshatra",
        "aspect_regime_active_count",
        "aspect_regime_signature",
        "touch_kind",
        "touch_planets",
        "touch_identity_count",
        "touch_identity_1_text",
        "touch_identity_2_text",
        "jyotish_hypothesis_direction",
        "jyotish_net_score",
        "jyotish_conflict_score",
        "doctrine_hypothesis_direction",
        "doctrine_net_score",
        "doctrine_conflict_score",
        "doctrine_dignity_virupa_avg",
        "doctrine_dominant_dignity",
        "fx_hypothesis_direction",
        "fx_pair_net_score",
        "fx_pair_conflict_ratio",
        "fx_doctrine_hypothesis_direction",
        "fx_doctrine_pair_net_score",
        "fx_doctrine_pair_conflict_ratio",
        "fx_doctrine_base_dignity_virupa_avg",
        "fx_doctrine_quote_dignity_virupa_avg",
        "fx_doctrine_dominant_base_hit",
        "fx_doctrine_dominant_quote_hit",
        "fx_doctrine_dominant_base_dignity",
        "fx_doctrine_dominant_quote_dignity",
        "fx_doctrine_rule_layer_total_strength",
        "rule_layer_ignore_hint",
        "quote_relevant_hit_count",
        "quote_dignity_label_counts",
        "quote_enemy_component_count",
        "quote_debilitation_component_count",
        "quote_unknown_dignity_component_count",
        "quote_benefic_component_count",
        "quote_malefic_component_count",
        "quote_hit_pairs",
        "quote_dignity_pairs",
        "base_relevant_hit_count",
        "base_dignity_label_counts",
        "base_enemy_component_count",
        "base_debilitation_component_count",
        "base_unknown_dignity_component_count",
        "base_benefic_component_count",
        "base_malefic_component_count",
        "base_hit_pairs",
        "base_dignity_pairs",
        "source_event_id",
    ]
    return df[[column for column in ordered_columns if column in df.columns]]


def build_focus_sheet(review: pd.DataFrame) -> pd.DataFrame:
    focus_columns = [
        "case_id",
        "same_aspect_group_key",
        "same_aspect_group_size",
        "group_script_direction_mode",
        "group_fx_doctrine_directions",
        "group_ml_outcomes",
        "group_avg_return_pct",
        "review_status",
        "manual_direction_label",
        "manual_behavior_label",
        "manual_trade_action",
        "manual_confidence",
        "manual_reason_tags",
        "manual_notes",
        "probable_factor_tags",
        "probable_factor_note",
        "script_observed_return_bias",
        "pair_nature_summary",
        "aspect_family",
        "window_start_ist",
        "window_end_ist",
        "csv_occurrence_count",
        "csv_m30_count",
        "csv_hourly_count",
        "csv_daily_count",
        "ml_outcome_counts",
        "close_action_counts",
        "avg_signed_return_pct",
        "shadbala_avg",
        "shadbala_tag",
        "event_bphs_virupa",
        "aspect_regime_active_count",
        "fx_doctrine_hypothesis_direction",
        "fx_doctrine_pair_net_score",
        "fx_doctrine_pair_conflict_ratio",
        "fx_doctrine_dominant_base_dignity",
        "fx_doctrine_dominant_quote_dignity",
        "quote_dignity_label_counts",
        "base_dignity_label_counts",
        "quote_enemy_component_count",
        "base_enemy_component_count",
        "quote_debilitation_component_count",
        "base_debilitation_component_count",
        "touch_planets",
        "touch_identity_1_text",
        "touch_identity_2_text",
        "source_event_id",
    ]
    return review[[column for column in focus_columns if column in review.columns]].copy()


def main() -> None:
    args = parse_args()
    inventory = pd.read_csv(args.inventory, low_memory=False)
    review = build_review_sheet(inventory)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    review.to_csv(args.output_csv, index=False)
    focus = build_focus_sheet(review)
    args.output_focus_csv.parent.mkdir(parents=True, exist_ok=True)
    focus.to_csv(args.output_focus_csv, index=False)
    print(f"Wrote {args.output_csv}")
    print(f"Wrote {args.output_focus_csv}")
    print(f"rows={len(review)}")
    print(f"columns={len(review.columns)}")
    print(f"focus_columns={len(focus.columns)}")
    print(f"recurrence_groups={review['same_aspect_group_key'].nunique()}")
    print("same_aspect_group_size distribution:")
    print(review["same_aspect_group_size"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
