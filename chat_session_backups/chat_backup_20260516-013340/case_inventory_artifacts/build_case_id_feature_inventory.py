from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from build_trade_candidates_from_touches import (
    aspect_family,
    duration_bucket,
    expand_scoring_bodies,
    hit_dignity_context,
    hit_strength,
    normalize_body,
    pair_bodies,
    comparable_aspect_name,
    NATURAL_PLANET_BIAS,
)


DEFAULT_DB = Path(r"C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite")
DEFAULT_TOUCH_LOG = Path(
    r"C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv"
)
DEFAULT_CANDIDATES = Path(
    r"C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv"
)
DEFAULT_OUTPUT = Path(r"C:\Users\ADMIN\PycharmProjects\case_id_feature_inventory_transitsign.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build one row per annotation case_id with CSV occurrence counts, "
            "astrology/scoring details, and trading outcome summaries."
        )
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--touch-log", type=Path, default=DEFAULT_TOUCH_LOG)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def read_cases(db_path: Path) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        cases = pd.read_sql_query(
            """
            SELECT
                case_id,
                source_event_id,
                pair_key,
                aspect,
                aspect_label,
                window_start_ist,
                window_end_ist,
                timeframe,
                source_csv,
                context_json,
                created_at_utc
            FROM aspect_cases
            ORDER BY case_id
            """,
            conn,
        )
    return cases


def safe_json_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, float) and np.isnan(value):
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except Exception:
        return []
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return []


def first_present(rows: pd.DataFrame, column: str, fallback: Any = "") -> Any:
    if column not in rows.columns:
        return fallback
    series = rows[column].dropna()
    if series.empty:
        return fallback
    for value in series:
        if str(value).strip() and str(value).strip().lower() not in {"nan", "none", "nat"}:
            return value
    return fallback


def mean_present(rows: pd.DataFrame, column: str) -> float | None:
    if column not in rows.columns:
        return None
    numeric = pd.to_numeric(rows[column], errors="coerce").dropna()
    if numeric.empty:
        return None
    return float(numeric.mean())


def count_values(rows: pd.DataFrame, column: str) -> str:
    if column not in rows.columns or rows.empty:
        return ""
    values = rows[column].dropna().astype(str).str.strip()
    values = values[(values != "") & (~values.str.lower().isin({"nan", "none", "nat"}))]
    if values.empty:
        return ""
    counts = Counter(values)
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def natural_class(body: Any) -> str:
    normalized = normalize_body(body)
    if normalized == "AVG(ALL)":
        return "mixed_classical"
    bias = float(NATURAL_PLANET_BIAS.get(normalized, 0.0))
    if bias > 0:
        return "benefic"
    if bias < 0:
        return "malefic"
    return "neutral_or_unknown"


def natural_bias(body: Any) -> float:
    return float(NATURAL_PLANET_BIAS.get(normalize_body(body), 0.0))


def scoped_hits(raw_hits: Any, pair_key: Any, aspect: Any) -> list[dict[str, Any]]:
    hits = safe_json_list(raw_hits)
    bodies = expand_scoring_bodies(pair_bodies(pair_key))
    aspect_name = comparable_aspect_name(aspect)
    if bodies:
        body_hits = [
            hit
            for hit in hits
            if normalize_body(hit.get("transit_planet")) in bodies
        ]
        aspect_hits = [
            hit
            for hit in body_hits
            if aspect_name and comparable_aspect_name(hit.get("aspect")) == aspect_name
        ]
        hits = aspect_hits or body_hits
    return [hit for hit in hits if hit_strength(hit) > 0]


def dignity_summary(raw_hits: Any, pair_key: Any, aspect: Any) -> dict[str, Any]:
    hits = scoped_hits(raw_hits, pair_key, aspect)
    component_labels: Counter[str] = Counter()
    planet_natures: Counter[str] = Counter()
    hit_pairs: list[str] = []
    dignity_pairs: list[str] = []
    for hit in hits:
        transit = normalize_body(hit.get("transit_planet"))
        natal = normalize_body(hit.get("natal_planet"))
        dignity = hit_dignity_context(hit)
        natal_label = str(dignity["natal_dignity_label"])
        transit_label = str(dignity["transit_dignity_label"])
        component_labels[natal_label] += 1
        if str(hit.get("transit_sign", "")).strip():
            component_labels[transit_label] += 1
        for body in (transit, natal):
            planet_natures[natural_class(body)] += 1
        hit_pairs.append(f"{transit}>{natal}:{str(hit.get('aspect', '')).strip()}")
        dignity_pairs.append(
            f"{transit}>{natal}:natal_{natal_label}_{dignity['natal_dignity_virupa']:.0f}V"
            + (
                f"/transit_{transit_label}_{dignity['transit_dignity_virupa']:.0f}V"
                if str(hit.get("transit_sign", "")).strip()
                else ""
            )
        )
    return {
        "relevant_hit_count": len(hits),
        "dignity_label_counts": "; ".join(
            f"{key}={component_labels[key]}" for key in sorted(component_labels)
        ),
        "enemy_component_count": int(component_labels.get("enemy", 0)),
        "debilitation_component_count": int(component_labels.get("debilitation", 0)),
        "unknown_dignity_component_count": int(component_labels.get("unknown", 0)),
        "benefic_component_count": int(planet_natures.get("benefic", 0)),
        "malefic_component_count": int(planet_natures.get("malefic", 0)),
        "neutral_or_unknown_component_count": int(planet_natures.get("neutral_or_unknown", 0)),
        "hit_pairs": "; ".join(hit_pairs[:12]),
        "dignity_pairs": "; ".join(dignity_pairs[:12]),
    }


def parse_context_json(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def row_value(case: pd.Series, raw_rows: pd.DataFrame, cand_rows: pd.DataFrame, column: str, default: Any = "") -> Any:
    value = first_present(cand_rows, column, None)
    if value is not None:
        return value
    value = first_present(raw_rows, column, None)
    if value is not None:
        return value
    context = parse_context_json(case.get("context_json"))
    return context.get(column, default)


def build_inventory(cases: pd.DataFrame, touch_log: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    raw_groups = {event_id: group for event_id, group in touch_log.groupby("event_id", sort=False)}
    cand_groups = {event_id: group for event_id, group in candidates.groupby("event_id", sort=False)}

    records: list[dict[str, Any]] = []
    for _, case in cases.iterrows():
        event_id = str(case["source_event_id"])
        raw_rows = raw_groups.get(event_id, pd.DataFrame())
        cand_rows = cand_groups.get(event_id, pd.DataFrame())
        pair_key = case.get("pair_key")
        aspect = case.get("aspect")
        bodies = str(pair_key or "").split("|")
        b1 = bodies[0] if len(bodies) > 0 else row_value(case, raw_rows, cand_rows, "b1")
        b2 = bodies[1] if len(bodies) > 1 else row_value(case, raw_rows, cand_rows, "b2")

        quote_summary = dignity_summary(row_value(case, raw_rows, cand_rows, "tn_hits_json"), pair_key, aspect)
        base_summary = dignity_summary(row_value(case, raw_rows, cand_rows, "base_tn_hits_json"), pair_key, aspect)
        timeframe_counts = cand_rows["chart_timeframe"].value_counts() if "chart_timeframe" in cand_rows.columns and not cand_rows.empty else pd.Series(dtype=int)
        ml_counts = cand_rows["ml_outcome"].value_counts() if "ml_outcome" in cand_rows.columns and not cand_rows.empty else pd.Series(dtype=int)
        potential_trade_count = int(pd.to_numeric(cand_rows.get("potential_trade", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not cand_rows.empty else 0
        ignored_count = int(pd.to_numeric(cand_rows.get("ignore_trade", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not cand_rows.empty else 0
        win_count = int(ml_counts.get("WIN", 0))
        loss_count = int(ml_counts.get("LOSS", 0))
        win_loss_total = win_count + loss_count

        record = {
            "case_id": int(case["case_id"]),
            "source_event_id": event_id,
            "pair_key": pair_key,
            "b1": b1,
            "b1_natural_class": natural_class(b1),
            "b1_natural_bias": natural_bias(b1),
            "b2": b2,
            "b2_natural_class": natural_class(b2),
            "b2_natural_bias": natural_bias(b2),
            "pair_nature_summary": f"{natural_class(b1)} + {natural_class(b2)}",
            "aspect": aspect,
            "aspect_label": case.get("aspect_label"),
            "aspect_family": row_value(case, raw_rows, cand_rows, "aspect_family", aspect_family(aspect)) or aspect_family(aspect),
            "window_start_ist": case.get("window_start_ist"),
            "window_end_ist": case.get("window_end_ist"),
            "case_timeframe_bucket": case.get("timeframe"),
            "csv_occurrence_count": int(len(cand_rows)),
            "csv_m30_count": int(timeframe_counts.get("m30", 0)),
            "csv_hourly_count": int(timeframe_counts.get("hourly", 0)),
            "csv_daily_count": int(timeframe_counts.get("daily", 0)),
            "csv_timeframes_present": "; ".join(str(x) for x in sorted(timeframe_counts.index.astype(str))) if len(timeframe_counts) else "",
            "potential_trade_count": potential_trade_count,
            "ignored_trade_count": ignored_count,
            "ml_win_count": win_count,
            "ml_loss_count": loss_count,
            "ml_ignore_count": int(ml_counts.get("IGNORE", 0)),
            "ml_win_rate": float(win_count / win_loss_total) if win_loss_total else np.nan,
            "ml_outcome_counts": count_values(cand_rows, "ml_outcome"),
            "close_action_counts": count_values(cand_rows, "close_action"),
            "signal_direction_counts": count_values(cand_rows, "signal_direction"),
            "trade_category_counts": count_values(cand_rows, "trade_category"),
            "ignore_reason_counts": count_values(cand_rows, "ignore_reason"),
            "avg_signed_return_pct": mean_present(cand_rows, "signed_return_pct"),
            "avg_mfe_pct": mean_present(cand_rows, "mfe_pct"),
            "avg_mae_pct": mean_present(cand_rows, "mae_pct"),
            "event_duration_minutes": row_value(case, raw_rows, cand_rows, "event_duration_minutes"),
            "duration_bucket": row_value(case, raw_rows, cand_rows, "duration_bucket", duration_bucket(row_value(case, raw_rows, cand_rows, "event_duration_minutes"))),
            "event_orb_deg": row_value(case, raw_rows, cand_rows, "event_orb_deg"),
            "event_orb_limit_deg": row_value(case, raw_rows, cand_rows, "event_orb_limit_deg"),
            "event_orb_strength": row_value(case, raw_rows, cand_rows, "event_orb_strength"),
            "event_bphs_strength": row_value(case, raw_rows, cand_rows, "event_bphs_strength"),
            "event_bphs_virupa": row_value(case, raw_rows, cand_rows, "event_bphs_virupa"),
            "shadbala_tag": row_value(case, raw_rows, cand_rows, "shadbala_tag"),
            "shadbala_avg": row_value(case, raw_rows, cand_rows, "shadbala_avg"),
            "moon_nakshatra": row_value(case, raw_rows, cand_rows, "moon_nakshatra"),
            "aspect_regime_active_count": row_value(case, raw_rows, cand_rows, "aspect_regime_active_count"),
            "aspect_regime_signature": row_value(case, raw_rows, cand_rows, "aspect_regime_signature"),
            "touch_kind": row_value(case, raw_rows, cand_rows, "touch_kind"),
            "touch_planets": row_value(case, raw_rows, cand_rows, "touch_planets"),
            "touch_identity_count": row_value(case, raw_rows, cand_rows, "touch_identity_count"),
            "touch_identity_1_text": row_value(case, raw_rows, cand_rows, "touch_identity_1_text"),
            "touch_identity_2_text": row_value(case, raw_rows, cand_rows, "touch_identity_2_text"),
            "jyotish_hypothesis_direction": row_value(case, raw_rows, cand_rows, "jyotish_hypothesis_direction"),
            "jyotish_net_score": row_value(case, raw_rows, cand_rows, "jyotish_net_score"),
            "jyotish_conflict_score": row_value(case, raw_rows, cand_rows, "jyotish_conflict_score"),
            "doctrine_hypothesis_direction": row_value(case, raw_rows, cand_rows, "doctrine_hypothesis_direction"),
            "doctrine_net_score": row_value(case, raw_rows, cand_rows, "doctrine_net_score"),
            "doctrine_conflict_score": row_value(case, raw_rows, cand_rows, "doctrine_conflict_score"),
            "doctrine_dignity_virupa_avg": row_value(case, raw_rows, cand_rows, "doctrine_dignity_virupa_avg"),
            "doctrine_dominant_dignity": row_value(case, raw_rows, cand_rows, "doctrine_dominant_dignity"),
            "fx_hypothesis_direction": row_value(case, raw_rows, cand_rows, "fx_hypothesis_direction"),
            "fx_pair_net_score": row_value(case, raw_rows, cand_rows, "fx_pair_net_score"),
            "fx_pair_conflict_ratio": row_value(case, raw_rows, cand_rows, "fx_pair_conflict_ratio"),
            "fx_doctrine_hypothesis_direction": row_value(case, raw_rows, cand_rows, "fx_doctrine_hypothesis_direction"),
            "fx_doctrine_pair_net_score": row_value(case, raw_rows, cand_rows, "fx_doctrine_pair_net_score"),
            "fx_doctrine_pair_conflict_ratio": row_value(case, raw_rows, cand_rows, "fx_doctrine_pair_conflict_ratio"),
            "fx_doctrine_base_dignity_virupa_avg": row_value(case, raw_rows, cand_rows, "fx_doctrine_base_dignity_virupa_avg"),
            "fx_doctrine_quote_dignity_virupa_avg": row_value(case, raw_rows, cand_rows, "fx_doctrine_quote_dignity_virupa_avg"),
            "fx_doctrine_dominant_base_hit": row_value(case, raw_rows, cand_rows, "fx_doctrine_dominant_base_hit"),
            "fx_doctrine_dominant_quote_hit": row_value(case, raw_rows, cand_rows, "fx_doctrine_dominant_quote_hit"),
            "fx_doctrine_dominant_base_dignity": row_value(case, raw_rows, cand_rows, "fx_doctrine_dominant_base_dignity"),
            "fx_doctrine_dominant_quote_dignity": row_value(case, raw_rows, cand_rows, "fx_doctrine_dominant_quote_dignity"),
            "fx_doctrine_rule_layer_total_strength": row_value(case, raw_rows, cand_rows, "fx_doctrine_rule_layer_total_strength"),
            "rule_layer_ignore_hint": row_value(case, raw_rows, cand_rows, "rule_layer_ignore_hint"),
            "quote_relevant_hit_count": quote_summary["relevant_hit_count"],
            "quote_dignity_label_counts": quote_summary["dignity_label_counts"],
            "quote_enemy_component_count": quote_summary["enemy_component_count"],
            "quote_debilitation_component_count": quote_summary["debilitation_component_count"],
            "quote_unknown_dignity_component_count": quote_summary["unknown_dignity_component_count"],
            "quote_benefic_component_count": quote_summary["benefic_component_count"],
            "quote_malefic_component_count": quote_summary["malefic_component_count"],
            "quote_hit_pairs": quote_summary["hit_pairs"],
            "quote_dignity_pairs": quote_summary["dignity_pairs"],
            "base_relevant_hit_count": base_summary["relevant_hit_count"],
            "base_dignity_label_counts": base_summary["dignity_label_counts"],
            "base_enemy_component_count": base_summary["enemy_component_count"],
            "base_debilitation_component_count": base_summary["debilitation_component_count"],
            "base_unknown_dignity_component_count": base_summary["unknown_dignity_component_count"],
            "base_benefic_component_count": base_summary["benefic_component_count"],
            "base_malefic_component_count": base_summary["malefic_component_count"],
            "base_hit_pairs": base_summary["hit_pairs"],
            "base_dignity_pairs": base_summary["dignity_pairs"],
        }
        records.append(record)
    return pd.DataFrame(records)


def main() -> None:
    args = parse_args()
    cases = read_cases(args.db)
    touch_log = pd.read_csv(args.touch_log, low_memory=False)
    candidates = pd.read_csv(args.candidates, low_memory=False)
    inventory = build_inventory(cases, touch_log, candidates)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    inventory.to_csv(args.output_csv, index=False)
    print(f"Wrote {args.output_csv}")
    print(f"rows={len(inventory)}")
    print("csv_occurrence_count distribution:")
    print(inventory["csv_occurrence_count"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
