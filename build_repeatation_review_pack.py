from __future__ import annotations

import argparse
import html
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from aspect_annotation_store import (
    DEFAULT_PRICE_PATHS,
    calculate_trade_prices,
    load_price_frame,
    suggested_price_timeframe,
)
from doctrine_config import append_doctrine_metadata


DEFAULT_DB = Path(r"C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite")
DEFAULT_TOUCH_LOG = Path(
    r"C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv"
)
DEFAULT_PRICE = Path(r"C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet")
DEFAULT_REVIEW_FOCUS = Path(r"C:\Users\ADMIN\PycharmProjects\manual_case_review_focus_transitsign_20260516_0145.csv")
DEFAULT_EXPORT_ROOT = Path(r"C:\Users\ADMIN\Desktop\doc")
REPEATATION_UI_VERSION = "repeatation_ui_20260522_svg_plotly_v21"
_PRICE_COVERAGE_CACHE: dict[Path, tuple[pd.Timestamp, pd.Timestamp] | None] = {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export one repeatation/recurrent aspect family as a review pack: "
            "real chart snapshots, marker templates, full-window pips, and an index page."
        )
    )
    parser.add_argument("--case-id", type=int, required=True, help="Seed case_id whose same pair/aspect group should be exported.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--touch-log", type=Path, default=DEFAULT_TOUCH_LOG)
    parser.add_argument("--price", type=Path, default=DEFAULT_PRICE)
    parser.add_argument("--review-focus", type=Path, default=DEFAULT_REVIEW_FOCUS)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--export-max-lines", type=int, default=60)
    parser.add_argument("--case-context-hours", type=float, default=72.0)
    parser.add_argument("--skip-chart-export", action="store_true", help="Only rebuild the index/template from existing chart files.")
    return parser.parse_args()


def h(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def slugify(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return text or "repeatation"


def command_quote(value: Any) -> str:
    return '"' + str(value).replace('"', '\\"') + '"'


def html_cache_href(name: str) -> str:
    return f"{name}?v={REPEATATION_UI_VERSION}"


def read_case_group(db_path: Path, case_id: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        seed = conn.execute(
            """
            SELECT case_id, source_event_id, pair_key, aspect, aspect_label,
                   window_start_ist, window_end_ist, timeframe, source_csv
            FROM aspect_cases
            WHERE case_id = ?
            """,
            (int(case_id),),
        ).fetchone()
        if seed is None:
            raise SystemExit(f"No aspect case found for case_id={case_id}.")
        rows = conn.execute(
            """
            SELECT case_id, source_event_id, pair_key, aspect, aspect_label,
                   window_start_ist, window_end_ist, timeframe, source_csv
            FROM aspect_cases
            WHERE pair_key = ?
              AND aspect = ?
            ORDER BY window_start_ist, case_id
            """,
            (seed["pair_key"], seed["aspect"]),
        ).fetchall()
    return dict(seed), [dict(row) for row in rows]


def load_focus_rows(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    df = pd.read_csv(path, low_memory=False)
    if "case_id" not in df.columns:
        return {}
    return {int(row["case_id"]): dict(row) for _, row in df.iterrows()}


def clean_value(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    text = str(value).strip()
    return "" if text.lower() in {"", "nan", "none", "null"} else text


def numeric_value(value: Any) -> float | None:
    try:
        out = float(value)
    except Exception:
        return None
    return out if pd.notna(out) else None


def trait_row_for_events(touch_log: Path, cases: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if not touch_log.exists():
        return {}
    event_ids = {clean_value(case.get("source_event_id")) for case in cases}
    event_ids.discard("")
    if not event_ids:
        return {}
    df = pd.read_csv(touch_log, low_memory=False)
    df = append_doctrine_metadata(df)
    if "event_id" not in df.columns:
        return {}
    sub = df[df["event_id"].astype(str).isin(event_ids)].copy()
    if sub.empty:
        return {}
    sort_cols = [col for col in ["event_id", "edge_score", "touch_time_local"] if col in sub.columns]
    if sort_cols:
        ascending = [True] + [False if col == "edge_score" else True for col in sort_cols[1:]]
        sub = sub.sort_values(sort_cols, ascending=ascending)
    rows: dict[str, dict[str, Any]] = {}
    for event_id, group in sub.groupby(sub["event_id"].astype(str), sort=False):
        rows[str(event_id)] = dict(group.iloc[0])
    return rows


def duration_bucket(minutes: float | None) -> str:
    if minutes is None:
        return ""
    if minutes <= 120:
        return "short_duration"
    if minutes <= 240:
        return "medium_duration"
    return "long_duration"


def numeric_bucket(name: str, value: float | None, low: float, high: float) -> str:
    if value is None:
        return ""
    if value <= low:
        return f"{name}_low"
    if value >= high:
        return f"{name}_high"
    return f"{name}_mid"


def trait_label(key: str) -> str:
    return key.replace("_", " ")


PLAIN_TRAIT_NAMES = {
    "shadbala_avg": "Old strength score",
    "tn_score_total": "Quote-side pressure score",
    "base_tn_score_total": "Base-side pressure score",
    "edge_score": "Overall setup score",
    "event_orb_deg": "Aspect distance from exact",
    "event_sthana_dignity_virupa_avg": "Basic planet strength",
    "event_strict_drik_bala_virupa_avg": "Aspect pressure strength",
    "event_strict_saptavargaja_bala_virupa_avg": "Multi-chart planet strength",
    "event_strict_ojayugma_bala_virupa_avg": "Odd/even sign strength",
    "event_strict_kaala_9_bala_virupa_avg": "Timing strength",
    "event_strict_chesta_bala_virupa_avg": "Motion strength",
    "event_strict_shadbala_implemented_total_virupa_avg": "Total planet strength",
    "event_strict_shadbala_implemented_total_ratio_avg": "Strength vs minimum",
}
PLAIN_CATEGORICAL_NAMES = {
    "event_b1_sign_relation": "Planet 1 sign relationship",
    "event_b2_sign_relation": "Planet 2 sign relationship",
    "event_b1_sthana_dignity_label": "Planet 1 sign strength",
    "event_b2_sthana_dignity_label": "Planet 2 sign strength",
    "event_b1_strict_dignity_label": "Planet 1 strict strength",
    "event_b2_strict_dignity_label": "Planet 2 strict strength",
    "event_b1_strict_sign": "Planet 1 sign",
    "event_b2_strict_sign": "Planet 2 sign",
    "event_weekday_lord": "Weekday planet",
    "event_tithi_name": "Lunar day",
    "event_paksha": "Moon phase half",
    "event_karana_name": "Karana",
    "event_yoga_name": "Yoga",
    "event_moon_nakshatra": "Moon zone",
    "event_sun_nakshatra": "Sun zone",
    "touch_planets": "Touched planet lines",
    "aspect_regime_active_count": "Nearby event count",
}


FEATURE_HELP = {
    "event_b1_sign_relation": "Friend/enemy relationship between planet 1 and the sign it occupies.",
    "event_b2_sign_relation": "Friend/enemy relationship between planet 2 and the sign it occupies.",
    "event_b1_sthana_dignity_label": "Whether planet 1 is in own, friendly, enemy, exalted, or weak sign condition.",
    "event_b2_sthana_dignity_label": "Whether planet 2 is in own, friendly, enemy, exalted, or weak sign condition.",
    "event_b1_strict_whole_sign_house": "House location for planet 1 in the event chart.",
    "event_b2_strict_whole_sign_house": "House location for planet 2 in the event chart.",
    "event_b1_house_quality": "Plain-language house group for planet 1.",
    "event_b2_house_quality": "Plain-language house group for planet 2.",
    "aspect_regime_active_count": "How many other event windows are active nearby. More overlap means less clean attribution.",
    "event_weekday_lord": "Planet linked with the weekday at event time.",
    "event_tithi_name": "Lunar day at event time.",
    "event_paksha": "Waxing or waning Moon half.",
    "event_moon_nakshatra": "Moon background zone at event time.",
}


def bucket_word(bucket: str) -> str:
    if bucket.endswith("_low"):
        return "low"
    if bucket.endswith("_high"):
        return "high"
    if bucket.endswith("_mid"):
        return "middle"
    return ""


def house_quality(house: float | int | None) -> str:
    if house is None:
        return ""
    try:
        value = int(float(house))
    except Exception:
        return ""
    if value in {1, 4, 5, 7, 9, 10}:
        return "supportive/angular-or-luck house"
    if value in {3, 6, 10, 11}:
        return "growth/action house"
    if value in {6, 8, 12}:
        return "difficult/hidden house"
    if value in {2, 7}:
        return "money/relationship pressure house"
    return "neutral house"


def feature_category_for_key(key: str) -> str:
    base = str(key or "").split(":", 1)[0]
    if any(part in base for part in ["dignity", "relation", "strict_sign", "house_quality", "whole_sign_house", "natal_house", "natal_sign"]):
        return "sign / house"
    if any(part in base for part in ["shadbala", "drik", "saptavargaja", "ojayugma", "kaala", "chesta", "sthana"]):
        return "planet strength"
    if any(part in base for part in ["weekday", "tithi", "paksha", "karana", "yoga", "nakshatra", "pada", "new_moon", "full_moon"]):
        return "timing / moon calendar"
    if any(part in base for part in ["regime", "orb", "duration"]):
        return "overlap / cleanliness"
    if any(part in base for part in ["touch", "tn_", "base_tn", "edge_score", "score"]):
        return "market-score context"
    return "other context"


def plain_categorical_label(col: str, value: str, fallback_prefix: str) -> str:
    label = PLAIN_CATEGORICAL_NAMES.get(col, fallback_prefix)
    cleaned = str(value).replace("_", " ").strip()
    return f"{label}: {cleaned}"


def numeric_trait_token(key: str, label: str, value: float | None, low: float, high: float) -> dict[str, Any] | None:
    bucket = numeric_bucket(key, value, low, high)
    if not bucket or value is None:
        return None
    plain = PLAIN_TRAIT_NAMES.get(key, label)
    bucket_name = bucket_word(bucket)
    return {
        "key": f"{key}:{bucket}",
        "label": f"{plain}: {value:.2f} ({bucket_name})",
        "plain_name": plain,
        "value": round(float(value), 4),
        "low_cutoff": float(low),
        "high_cutoff": float(high),
        "bucket": bucket_name,
        "category": feature_category_for_key(key),
        "help": FEATURE_HELP.get(key, ""),
    }


def strength_item(row: dict[str, Any], key: str, label: str, low: float, high: float, help_text: str) -> dict[str, Any] | None:
    value = numeric_value(row.get(key))
    if value is None:
        return None
    token = numeric_trait_token(key, label, value, low, high)
    if token is None:
        return None
    token["help"] = help_text
    return token


def event_strength_summary(row: dict[str, Any]) -> list[dict[str, Any]]:
    if not row:
        return []
    items = [
        strength_item(
            row,
            "event_strict_shadbala_implemented_total_virupa_avg",
            "Total planet strength",
            240.0,
            480.0,
            "Overall strength from the implemented Shadbala parts. Higher means the planet signal is stronger.",
        ),
        strength_item(
            row,
            "event_strict_shadbala_implemented_total_ratio_avg",
            "Strength vs minimum",
            0.70,
            1.25,
            "Total strength divided by the expected minimum. Above 1.00 means above minimum.",
        ),
        strength_item(
            row,
            "event_strict_saptavargaja_bala_virupa_avg",
            "Multi-chart planet strength",
            80.0,
            180.0,
            "Strength checked across several chart divisions. Higher means more repeated support.",
        ),
        strength_item(
            row,
            "event_strict_kaala_9_bala_virupa_avg",
            "Timing strength",
            80.0,
            220.0,
            "Whether the event time gives the planets more force. Higher means stronger timing support.",
        ),
        strength_item(
            row,
            "event_strict_drik_bala_virupa_avg",
            "Aspect pressure strength",
            -40.0,
            30.0,
            "Pressure from other planets. Negative leans stressful/downward; positive leans supportive/upward.",
        ),
        strength_item(
            row,
            "event_strict_chesta_bala_virupa_avg",
            "Motion strength",
            5.0,
            35.0,
            "Slow, stopped, or backward-moving planets can act more strongly in this rule.",
        ),
    ]
    return [item for item in items if item]


def event_trait_tokens(row: dict[str, Any]) -> list[dict[str, Any]]:
    if not row:
        return []
    raw: list[dict[str, Any]] = []
    for col, prefix in [
        ("shadbala_tag", "shadbala"),
        ("shadbala_doctrine_status", "shadbala status"),
        ("event_b1_sthana_dignity_label", "event b1 dignity"),
        ("event_b2_sthana_dignity_label", "event b2 dignity"),
        ("event_b1_sign_relation", "event b1 sign relation"),
        ("event_b2_sign_relation", "event b2 sign relation"),
        ("event_doctrine_feature_status", "doctrine feature status"),
        ("event_strict_shadbala_status", "strict shadbala status"),
        ("event_strict_drik_status", "strict drik status"),
        ("event_strict_shadbala_missing_components", "strict shadbala validation gap"),
        ("event_strict_shadbala_component_rule_ids", "strict shadbala rule ids"),
        ("event_b1_strict_chesta_status", "event b1 chesta"),
        ("event_b2_strict_chesta_status", "event b2 chesta"),
        ("event_b1_strict_yuddha_status", "event b1 yuddha"),
        ("event_b2_strict_yuddha_status", "event b2 yuddha"),
        ("event_b1_strict_dignity_label", "event b1 strict dignity"),
        ("event_b2_strict_dignity_label", "event b2 strict dignity"),
        ("event_b1_strict_sign", "event b1 strict sign"),
        ("event_b2_strict_sign", "event b2 strict sign"),
        ("event_panchanga_status", "panchanga status"),
        ("event_weekday", "weekday"),
        ("event_weekday_lord", "weekday lord"),
        ("event_tithi_name", "tithi"),
        ("event_paksha", "paksha"),
        ("event_karana_name", "karana"),
        ("event_yoga_name", "yoga"),
        ("event_moon_nakshatra", "moon nakshatra"),
        ("event_sun_nakshatra", "sun nakshatra"),
        ("touch_planets", "touch planets"),
        ("touch_planet_1_natal_sign", "touch planet 1 sign"),
        ("touch_planet_2_natal_sign", "touch planet 2 sign"),
        ("tn_primary_transit_planet", "primary transit"),
        ("tn_primary_natal_planet", "primary natal"),
        ("tn_primary_aspect", "primary aspect"),
        ("tn_primary_natal_sign", "primary natal sign"),
        ("base_tn_primary_transit_planet", "base primary transit"),
        ("base_tn_primary_natal_planet", "base primary natal"),
        ("base_tn_primary_aspect", "base primary aspect"),
        ("base_tn_primary_natal_sign", "base primary natal sign"),
    ]:
        value = clean_value(row.get(col))
        if value:
            raw.append(
                {
                    "key": f"{col}:{value}",
                    "label": plain_categorical_label(col, value, prefix),
                    "category": feature_category_for_key(col),
                    "help": FEATURE_HELP.get(col, ""),
                }
            )
    for col, prefix in [
        ("touch_planet_1_natal_house", "touch planet 1 house"),
        ("touch_planet_2_natal_house", "touch planet 2 house"),
        ("tn_primary_natal_house", "primary natal house"),
        ("base_tn_primary_natal_house", "base primary natal house"),
        ("aspect_regime_active_count", "active regime count"),
        ("event_moon_pada", "moon pada"),
        ("event_sun_pada", "sun pada"),
        ("event_tithi_changed_flag", "tithi changed"),
        ("event_karana_changed_flag", "karana changed"),
        ("event_yoga_changed_flag", "yoga changed"),
        ("event_moon_nakshatra_changed_flag", "moon nakshatra changed"),
        ("event_moon_pada_changed_flag", "moon pada changed"),
        ("event_weekday_changed_flag", "weekday changed"),
        ("event_near_new_moon_flag", "near new moon"),
        ("event_near_full_moon_flag", "near full moon"),
    ]:
        value = numeric_value(row.get(col))
        if value is not None:
            raw.append(
                {
                    "key": f"{col}:{int(value)}",
                    "label": plain_categorical_label(col, str(int(value)), prefix),
                    "category": feature_category_for_key(col),
                    "help": FEATURE_HELP.get(col, ""),
                }
            )
    for col, label in [
        ("event_b1_strict_whole_sign_house", "Planet 1 house"),
        ("event_b2_strict_whole_sign_house", "Planet 2 house"),
    ]:
        value = numeric_value(row.get(col))
        quality = house_quality(value)
        if value is not None:
            raw.append(
                {
                    "key": f"{col}:{int(value)}",
                    "label": f"{label}: {int(value)}",
                    "category": "sign / house",
                    "help": FEATURE_HELP.get(col, ""),
                }
            )
        if quality:
            quality_key = col.replace("strict_whole_sign_house", "house_quality")
            raw.append(
                {
                    "key": f"{quality_key}:{quality}",
                    "label": f"{label} group: {quality}",
                    "category": "sign / house",
                    "help": FEATURE_HELP.get(quality_key, ""),
                }
            )
    dur = duration_bucket(numeric_value(row.get("event_duration_minutes")))
    if dur:
        minutes = numeric_value(row.get("event_duration_minutes"))
        raw.append(
            {
                "key": f"event_duration:{dur}",
                "label": f"Event length: {minutes:.0f} minutes ({trait_label(dur).replace('event duration ', '')})"
                if minutes is not None
                else trait_label(dur),
                "category": "overlap / cleanliness",
                "help": "How long this event window stayed active.",
            }
        )
    for key, label, low, high in [
        ("shadbala_avg", "shadbala", 54.0, 59.0),
        ("tn_score_total", "TN score", 3.0, 5.0),
        ("base_tn_score_total", "base TN score", 3.0, 5.0),
        ("edge_score", "edge score", 0.20, 0.75),
        ("event_orb_deg", "event orb", 45.0, 75.0),
        ("event_sthana_dignity_virupa_avg", "event sthana dignity", 8.0, 30.0),
        ("event_strict_drik_bala_virupa_avg", "strict drik", -40.0, 30.0),
        ("event_strict_saptavargaja_bala_virupa_avg", "strict saptavargaja", 80.0, 180.0),
        ("event_strict_ojayugma_bala_virupa_avg", "strict ojayugma", 5.0, 25.0),
        ("event_strict_kaala_9_bala_virupa_avg", "strict kaala", 80.0, 220.0),
        ("event_strict_chesta_bala_virupa_avg", "strict chesta", 5.0, 35.0),
        ("event_strict_shadbala_implemented_total_virupa_avg", "strict shadbala v1 total", 240.0, 480.0),
        ("event_strict_shadbala_implemented_total_ratio_avg", "strict shadbala ratio", 0.70, 1.25),
    ]:
        token = numeric_trait_token(key, label, numeric_value(row.get(key)), low, high)
        if token:
            raw.append(token)
    seen = set()
    tokens = []
    for item in raw:
        norm = re.sub(r"\s+", " ", str(item.get("key", ""))).strip()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        token = dict(item)
        token["key"] = norm
        tokens.append(token)
    return tokens


def compute_special_traits(
    cases: list[dict[str, Any]],
    stats_by_case: dict[int, dict[str, Any]],
    touch_rows_by_event: dict[str, dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    case_tokens: dict[int, list[dict[str, Any]]] = {}
    token_cases: dict[str, set[int]] = {}
    token_payloads: dict[str, dict[str, Any]] = {}
    pips_by_case: dict[int, float] = {}
    for case in cases:
        case_id = int(case["case_id"])
        event_id = clean_value(case.get("source_event_id"))
        tokens = event_trait_tokens(touch_rows_by_event.get(event_id, {}))
        case_tokens[case_id] = tokens
        for token in tokens:
            token_cases.setdefault(token["key"], set()).add(case_id)
            token_payloads[token["key"]] = token
        pips_by_case[case_id] = float(stats_by_case.get(case_id, {}).get("full_window_bullish_pips") or 0.0)
    group_pips = list(pips_by_case.values())
    group_avg = sum(group_pips) / len(group_pips) if group_pips else 0.0
    bullish_count = sum(1 for value in group_pips if value > 0)
    bearish_count = sum(1 for value in group_pips if value < 0)
    total = max(1, len(cases))
    out: dict[int, dict[str, Any]] = {}
    for case in cases:
        case_id = int(case["case_id"])
        scored: list[dict[str, Any]] = []
        for token in case_tokens.get(case_id, []):
            peers = sorted(token_cases.get(token["key"], set()))
            peer_pips = [pips_by_case[peer] for peer in peers if peer in pips_by_case]
            avg = sum(peer_pips) / len(peer_pips) if peer_pips else 0.0
            positives = sum(1 for value in peer_pips if value > 0)
            negatives = sum(1 for value in peer_pips if value < 0)
            delta = avg - group_avg
            tags: list[str] = []
            if len(peers) >= max(2, total // 4) and abs(delta) >= 8.0:
                tags.append("direction linked")
            if len(peers) <= 2:
                tags.append("rare")
            elif len(peers) >= max(3, int(total * 0.60)):
                tags.append("common")
            if positives and not negatives:
                tags.append("only bullish samples")
            elif negatives and not positives:
                tags.append("only bearish samples")
            if not tags:
                tags.append("context")
            scored.append(
                {
                    "key": token["key"],
                    "label": token_payloads.get(token["key"], token).get("label", token["label"]),
                    "plain_name": token_payloads.get(token["key"], token).get("plain_name", ""),
                    "value": token_payloads.get(token["key"], token).get("value", ""),
                    "low_cutoff": token_payloads.get(token["key"], token).get("low_cutoff", ""),
                    "high_cutoff": token_payloads.get(token["key"], token).get("high_cutoff", ""),
                    "bucket": token_payloads.get(token["key"], token).get("bucket", ""),
                    "category": token_payloads.get(token["key"], token).get(
                        "category", feature_category_for_key(token["key"])
                    ),
                    "help": token_payloads.get(token["key"], token).get("help", ""),
                    "tags": tags,
                    "occurrences": len(peers),
                    "repeatation_count": total,
                    "avg_bullish_pips": round(avg, 1),
                    "group_avg_bullish_pips": round(group_avg, 1),
                    "delta_vs_group_pips": round(delta, 1),
                    "bullish_samples": positives,
                    "bearish_samples": negatives,
                    "peer_case_ids": peers[:12],
                }
            )
        scored.sort(
            key=lambda item: (
                0 if "direction linked" in item["tags"] else 1,
                0 if "rare" in item["tags"] else 1,
                -abs(float(item["delta_vs_group_pips"])),
                -int(item["occurrences"]),
            )
        )
        evidence = sorted(
            scored,
            key=lambda item: (
                str(item.get("category", "")),
                0 if "direction linked" in item["tags"] else 1,
                0 if "rare" in item["tags"] else 1,
                -abs(float(item["delta_vs_group_pips"])),
                str(item.get("label", "")),
            ),
        )
        out[case_id] = {
            "method": "These are pattern clues from the same repeated setup. They compare what happened after similar cases. They are useful hints, not proof.",
            "strength_summary": event_strength_summary(touch_rows_by_event.get(clean_value(case.get("source_event_id")), {})),
            "astro_feature_evidence": evidence[:120],
            "group_repeatation_count": total,
            "group_bullish_count": bullish_count,
            "group_bearish_count": bearish_count,
            "group_avg_bullish_pips": round(group_avg, 1),
            "case_full_window_bullish_pips": round(pips_by_case.get(case_id, 0.0), 1),
            "case_full_window_direction": stats_by_case.get(case_id, {}).get("full_window_direction", ""),
            "traits": scored[:10],
        }
    return out


def chart_command(args: argparse.Namespace, case_id: int, output_dir: Path) -> list[str]:
    return [
        sys.executable,
        str(Path(__file__).resolve().with_name("sr_touch_lazy_dashboard.py")),
        "--touch-log",
        str(args.touch_log),
        "--price",
        str(chart_price_path(args, case_id)),
        "--export-case-chart",
        "--case-id",
        str(case_id),
        "--case-timeframe",
        "auto",
        "--export-dir",
        str(output_dir),
        "--export-max-lines",
        str(int(args.export_max_lines)),
        "--case-context-hours",
        str(float(args.case_context_hours)),
    ]


def export_chart(args: argparse.Namespace, case: dict[str, Any], output_dir: Path) -> tuple[Path, Path, int]:
    html_path = output_dir / f"aspect_review_case_{int(case['case_id'])}_chart.html"
    csv_path = output_dir / f"aspect_review_case_{int(case['case_id'])}_chart_visible.csv"
    if not args.skip_chart_export or not html_path.exists() or not csv_path.exists():
        subprocess.run(chart_command(args, int(case["case_id"]), output_dir), cwd=Path(__file__).resolve().parent, check=True)
    inject_marker_ui(html_path, case)
    visible_rows = 0
    if csv_path.exists():
        try:
            visible_rows = len(pd.read_csv(csv_path, low_memory=False))
        except Exception:
            visible_rows = 0
    return html_path, csv_path, visible_rows


def marker_ui_script(case: dict[str, Any]) -> str:
    case_id = int(case["case_id"])
    timeframe = price_timeframe_for_case(case)
    window_start = str(case["window_start_ist"])
    window_end = str(case["window_end_ist"])
    pair_key = str(case["pair_key"])
    aspect = str(case["aspect"])
    metadata = {
        "caseId": case_id,
        "priceTimeframe": timeframe,
        "windowStart": window_start,
        "windowEnd": window_end,
        "pairKey": pair_key,
        "aspect": aspect,
        "defaultOutcome": str(case.get("default_outcome", "bullish") or "bullish"),
        "repeatationIndex": int(case.get("repeatation_index", 1)),
        "repeatationCount": int(case.get("repeatation_count", 1)),
        "previousHref": str(case.get("previous_chart_href", "")),
        "nextHref": str(case.get("next_chart_href", "")),
        "reviewerHref": str(case.get("reviewer_href", "repeatation_reviewer.html")),
        "traitGuideHref": html_cache_href("trait_guide.html"),
        "specialTraits": case.get("special_traits", {}),
    }
    metadata_json = json.dumps(metadata)
    return f"""
<script id="repeatation-marker-ui-script">
(function () {{
  var meta = {metadata_json};
  if (window.__repeatationMarkerUiAttached) return;
  window.__repeatationMarkerUiAttached = true;
  function ready(fn) {{
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }}
  ready(function () {{
    var gd = document.querySelector('.js-plotly-plot');
    if (!gd || !window.Plotly) return;
    var state = {{
      tool: 'trade_start',
      tradeStart: null,
      tradeEnd: null,
      ignoreStart: null,
      ignoreEnd: null,
      tradeIgnored: false,
      selectedIgnoreTypes: [],
      annotations: [],
      autoSuggestion: null,
      outcomeTouched: false,
      lastPoint: null,
      draftLoaded: false
    }};
    var storageKey = 'repeatation-marker-draft:v1:case:' + meta.caseId + ':' + meta.priceTimeframe;
    var LEGACY_IGNORE_TRADE_NOTE = 'ignore trade: nearby/overlapping aspect/event contaminates case behavior';
    var IGNORE_SIGNAL_DEFINITIONS = {{
      ignore_trade_nearby_event: 'Another aspect or event is close enough to the reviewed case window that attribution is not clean.',
      ignore_trade_event_too_short: 'The aspect window is too short relative to the chart timeframe, spread, or noise to judge a reliable trade.',
      nearby_aspect: 'A separate aspect/event starts or ends near the reviewed window but does not materially overlap it.',
      overlapping_aspect: 'A separate aspect/event overlaps the reviewed window and may be driving the same candles.',
      crowded_regime: 'Several aspect windows, SR lines, or regime zones are active together, so the isolated case_id effect is unclear.',
      bad_price_data: 'Candles are missing, stale, misaligned, outside available data coverage, or otherwise unsuitable for annotation.',
      abnormal_candle: 'A candle spike/gap/one-off move dominates the result and may not represent the aspect behavior.',
      session_gap: 'Market close, weekend, rollover, or session transition interrupts clean start/end interpretation.',
      no_clear_reaction: 'Price does not show a distinguishable directional reaction inside the reviewed window.',
      manual_skip: 'Reviewer intentionally excludes this recurrence for a specific reason written in the note.'
    }};
    var RULE_SCOPE_DEFINITIONS = {{
      global: 'Applies across all case families and future charts only after later validation.',
      case_family: 'Applies to this recurring pair_key/aspect family across its repeatations.',
      case_id: 'Applies only to the current case_id recurrence.',
      local_window: 'Applies only to the marked or visible local chart window.'
    }};
    var RULE_TYPE_DEFINITIONS = {{
      behavior_rule: 'Observed normal directional behavior for this setup.',
      exception_rule: 'Condition where the setup behaves differently from its usual direction.',
      confidence_rule: 'Condition that should raise or lower confidence without necessarily flipping direction.',
      dignity_rule: 'Planetary dignity, sign, shadbala, benefic/malefic, enemy/friend, or related astrological strength note.',
      regime_rule: 'Multiple active aspects, crowded regime, duration bucket, or timing context note.',
      sr_rule: 'Support/resistance planetary line, touch, rejection, break, or confluence note.',
      ml_feature_hint: 'Reviewer hint that a feature should be engineered or tested in walk-forward validation.'
    }};
    var MARKER_COLORS = {{
      tradeStart: '#38bdf8',
      tradeEnd: '#fbbf24',
      ignore: '#c084fc',
      profit: '#a78bfa'
    }};
    function esc(value) {{
      return String(value == null ? '' : value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}
    function shellQuote(value) {{
      return '"' + String(value == null ? '' : value).replace(/"/g, '\\\\\\"') + '"';
    }}
    function hexToRgba(hex, alpha) {{
      var value = String(hex || '').replace('#', '');
      if (value.length !== 6) return 'rgba(148,163,184,' + alpha + ')';
      var r = parseInt(value.slice(0, 2), 16);
      var g = parseInt(value.slice(2, 4), 16);
      var b = parseInt(value.slice(4, 6), 16);
      return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';
    }}
    function pad(n) {{ return String(n).padStart(2, '0'); }}
    function toIST(value) {{
      if (!value) return '';
      var raw = String(value);
      if (/\\d{{4}}-\\d{{2}}-\\d{{2}}[ T]\\d{{2}}:\\d{{2}}/.test(raw) && raw.indexOf('+05:30') !== -1) {{
        return raw.replace('T', ' ').replace(/\\.\\d+/, '').slice(0, 19) + '+05:30';
      }}
      var d = new Date(value);
      if (isNaN(d.getTime()) && typeof value === 'number') d = new Date(value);
      if (isNaN(d.getTime())) return raw;
      var parts = new Intl.DateTimeFormat('en-GB', {{
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }}).formatToParts(d).reduce(function (acc, part) {{
        acc[part.type] = part.value;
        return acc;
      }}, {{}});
      return parts.year + '-' + parts.month + '-' + parts.day + ' ' + parts.hour + ':' + parts.minute + ':' + parts.second + '+05:30';
    }}
    function fmtPoint(point) {{
      if (!point) return 'not set';
      var price = Number(point.y);
      return toIST(point.x) + (Number.isFinite(price) ? ' @ ' + price.toFixed(3) : '');
    }}
    function traceLooksLikeMarker(trace) {{
      var mode = String(trace && trace.mode || '').toLowerCase();
      var name = String(trace && trace.name || '').toLowerCase();
      return mode.indexOf('markers') !== -1 || name.indexOf('touch') !== -1 || name.indexOf('interaction') !== -1;
    }}
    function customDataLabel(customdata) {{
      if (!customdata) return '';
      if (Array.isArray(customdata)) {{
        return String(customdata[4] || customdata[5] || customdata[0] || '').slice(0, 160);
      }}
      return String(customdata).slice(0, 160);
    }}
    function axisPixel(axis, value) {{
      if (!axis) return null;
      if (typeof axis.d2p === 'function') return axis.d2p(value);
      if (typeof axis.d2c === 'function' && typeof axis.c2p === 'function') return axis.c2p(axis.d2c(value));
      if (typeof axis.l2p === 'function' && typeof axis.d2l === 'function') return axis.l2p(axis.d2l(value));
      return null;
    }}
    function arrayValue(values, index) {{
      if (!values) return null;
      if (Array.isArray(values)) return values[index];
      if (typeof values.length === 'number') return values[index];
      return null;
    }}
    function chartMarkerPoint(trace, curveNumber, pointNumber, fallbackLabel) {{
      var x = arrayValue(trace && trace.x, pointNumber);
      var y = arrayValue(trace && trace.y, pointNumber);
      if (y == null) return null;
      return {{
        x: x,
        y: y,
        source: 'chart_marker',
        traceName: trace.name || '',
        curveNumber: curveNumber,
        pointNumber: pointNumber,
        markerLabel: customDataLabel(arrayValue(trace.customdata, pointNumber)) || String(fallbackLabel || arrayValue(trace.text, pointNumber) || '').replace(/<[^>]*>/g, ' ').replace(/\\s+/g, ' ').trim().slice(0, 160)
      }};
    }}
    function markerTime(point) {{
      var value = Date.parse(point && point.x);
      return Number.isFinite(value) ? value : NaN;
    }}
    function markerIdentity(point) {{
      var t = markerTime(point);
      var y = Number(point && point.y);
      return (Number.isFinite(t) ? Math.round(t / 60000) : String(point && point.x)) + ':' + (Number.isFinite(y) ? y.toFixed(4) : '');
    }}
    function collectChartMarkers() {{
      var traces = Array.isArray(gd._fullData) ? gd._fullData : (Array.isArray(gd.data) ? gd.data : []);
      var out = [];
      var seen = {{}};
      traces.forEach(function (trace, curveNumber) {{
        if (!traceLooksLikeMarker(trace) || trace.visible === false || !trace.x || !trace.y) return;
        var traceName = String(trace.name || '');
        var isSelectedCaseTouch = traceName.toLowerCase().indexOf('selected case touch') !== -1;
        var len = Number(trace.x.length || 0);
        for (var i = 0; i < len; i += 1) {{
          var point = chartMarkerPoint(trace, curveNumber, i);
          if (!point || !Number.isFinite(markerTime(point))) continue;
          point.isSelectedCaseTouch = isSelectedCaseTouch;
          point.autoCandidate = true;
          point.markerLabel = point.markerLabel || traceName;
          var id = markerIdentity(point);
          if (seen[id] && !isSelectedCaseTouch) continue;
          if (seen[id] && isSelectedCaseTouch) {{
            out = out.filter(function (item) {{ return markerIdentity(item) !== id; }});
          }}
          seen[id] = true;
          out.push(point);
        }}
      }});
      return out.sort(function (a, b) {{ return markerTime(a) - markerTime(b); }});
    }}
    function pointInCaseWindow(point) {{
      var t = markerTime(point);
      var start = Date.parse(meta.windowStart);
      var end = Date.parse(meta.windowEnd);
      if (!Number.isFinite(t) || !Number.isFinite(start) || !Number.isFinite(end)) return false;
      return t >= start && t <= end;
    }}
    function autoSuggestedPoint(point, role) {{
      var copy = Object.assign({{}}, point || {{}});
      copy.source = 'chart_marker';
      copy.autoSuggested = true;
      copy.autoRole = role;
      return copy;
    }}
    function nearestChartMarker(plotX, plotY, thresholdPx) {{
      var xa = gd._fullLayout && gd._fullLayout.xaxis;
      var ya = gd._fullLayout && gd._fullLayout.yaxis;
      var traces = Array.isArray(gd._fullData) ? gd._fullData : (Array.isArray(gd.data) ? gd.data : []);
      var best = null;
      traces.forEach(function (trace, curveNumber) {{
        if (!traceLooksLikeMarker(trace) || !trace.visible || !trace.x || !trace.y) return;
        var len = Number(trace.x.length || 0);
        for (var i = 0; i < len; i += 1) {{
          var x = arrayValue(trace.x, i);
          var y = arrayValue(trace.y, i);
          if (x == null || y == null) continue;
          var px = axisPixel(xa, x);
          var py = axisPixel(ya, y);
          if (!Number.isFinite(px) || !Number.isFinite(py)) continue;
          var dist = Math.hypot(px - plotX, py - plotY);
          if (dist <= (thresholdPx || 32) && (!best || dist < best.dist)) {{
            best = {{ dist: dist, point: chartMarkerPoint(trace, curveNumber, i) }};
          }}
        }}
      }});
      return best && best.point ? best.point : null;
    }}
    function pointFromPlotly(eventData) {{
      if (!eventData || !eventData.points || !eventData.points.length) return null;
      var p = eventData.points[0];
      var y = p.y;
      if (y == null && p.close != null) y = p.close;
      if (y == null && p.high != null && p.low != null) y = (Number(p.high) + Number(p.low)) / 2;
      var trace = p.data || p.fullData || {{}};
      var isMarker = traceLooksLikeMarker(trace);
      if (isMarker) {{
        var adopted = chartMarkerPoint(trace, p.curveNumber, p.pointNumber, p.text);
        if (adopted) return adopted;
      }}
      return {{
        x: p.x,
        y: y,
        source: isMarker ? 'chart_marker' : 'plotly_click',
        traceName: trace.name || '',
        curveNumber: p.curveNumber,
        pointNumber: p.pointNumber,
        markerLabel: customDataLabel(p.customdata) || String(p.text || '').replace(/<[^>]*>/g, ' ').replace(/\\s+/g, ' ').trim().slice(0, 160)
      }};
    }}
    function axisValue(axis, pixel) {{
      if (!axis) return null;
      if (typeof axis.p2d === 'function') return axis.p2d(pixel);
      if (typeof axis.p2c === 'function') return axis.p2c(pixel);
      return null;
    }}
    function pointFromMouse(evt) {{
      return pointFromMouseAt(evt, true);
    }}
    function pointFromMouseAt(evt, useMagnet) {{
      if (!gd._fullLayout || !gd._fullLayout.xaxis || !gd._fullLayout.yaxis) return null;
      var xa = gd._fullLayout.xaxis;
      var ya = gd._fullLayout.yaxis;
      var rect = gd.getBoundingClientRect();
      var plotX = evt.clientX - rect.left - xa._offset;
      var plotY = evt.clientY - rect.top - ya._offset;
      if (plotX < 0 || plotX > xa._length || plotY < 0 || plotY > ya._length) return null;
      var marker = useMagnet !== false ? nearestChartMarker(plotX, plotY, 34) : null;
      if (marker) return marker;
      return {{ x: axisValue(xa, plotX), y: axisValue(ya, plotY), source: 'chart_click' }};
    }}
    function yAxisMidpoint() {{
      var axis = gd._fullLayout && gd._fullLayout.yaxis;
      var range = axis && Array.isArray(axis.range) ? axis.range : null;
      if (!range) return null;
      var start = Number(range[0]);
      var end = Number(range[1]);
      if (!Number.isFinite(start) || !Number.isFinite(end)) return null;
      return (start + end) / 2;
    }}
    function caseWindowPoint(x, source) {{
      return {{
        x: x,
        y: yAxisMidpoint(),
        source: source || 'case_window_ignore_trade',
        placedAt: Date.now()
      }};
    }}
    function sortPoints(a, b) {{
      if (!a || !b) return [a, b];
      return Date.parse(a.x) <= Date.parse(b.x) ? [a, b] : [b, a];
    }}
    function isChartMarkerPoint(point) {{
      return point && point.source === 'chart_marker';
    }}
    function activeStateKey() {{
      if (state.tool === 'trade_start') return 'tradeStart';
      if (state.tool === 'trade_end') return 'tradeEnd';
      if (state.tool === 'ignore_start') return 'ignoreStart';
      if (state.tool === 'ignore_end') return 'ignoreEnd';
      return '';
    }}
    function markerRefs() {{
      return [
        {{ key: 'tradeStart', point: state.tradeStart }},
        {{ key: 'tradeEnd', point: state.tradeEnd }},
        {{ key: 'ignoreStart', point: state.ignoreStart }},
        {{ key: 'ignoreEnd', point: state.ignoreEnd }}
      ];
    }}
    function markerDistancePx(evt, point) {{
      if (!point || isChartMarkerPoint(point) || !gd._fullLayout || !gd._fullLayout.xaxis || !gd._fullLayout.yaxis) return Infinity;
      var xa = gd._fullLayout.xaxis;
      var ya = gd._fullLayout.yaxis;
      var rect = gd.getBoundingClientRect();
      var plotX = evt.clientX - rect.left - xa._offset;
      var plotY = evt.clientY - rect.top - ya._offset;
      var px = axisPixel(xa, point.x);
      var py = axisPixel(ya, point.y);
      if (!Number.isFinite(px) || !Number.isFinite(py)) return Infinity;
      return Math.hypot(px - plotX, py - plotY);
    }}
    function nearestManualMarkerRef(evt, thresholdPx) {{
      var best = null;
      markerRefs().forEach(function (ref) {{
        var dist = markerDistancePx(evt, ref.point);
        if (dist <= (thresholdPx || 22) && (!best || dist < best.dist)) best = {{ key: ref.key, dist: dist }};
      }});
      return best;
    }}
    function setStatePoint(key, point) {{
      if (!key || !point) return;
      if (state.autoSuggestion && state.autoSuggestion.active && (key === 'tradeStart' || key === 'tradeEnd') && !point.autoSuggested) {{
        state.autoSuggestion.manual_override = true;
        if (state.autoSuggestion.overridden_keys.indexOf(key) === -1) state.autoSuggestion.overridden_keys.push(key);
      }}
      point.placedAt = Date.now();
      state[key] = point;
      state.lastPoint = point;
      if (key === 'ignoreStart' || key === 'ignoreEnd') state.tradeIgnored = false;
    }}
    function setTool(tool, persist) {{
      state.tool = tool;
      panel.querySelectorAll('[data-tool]').forEach(function (button) {{
        button.classList.toggle('active', button.getAttribute('data-tool') === tool);
      }});
      if (persist !== false) saveDraft();
    }}
    function place(point) {{
      if (!point || !point.x) return;
      var key = activeStateKey();
      if (!key) return;
      setStatePoint(key, point);
      setTool('', false);
      drawMarkers();
      render();
      saveDraft();
    }}
    function serialPoint(point) {{
      if (!point) return null;
      return {{
        x: point.x,
        y: point.y,
        source: point.source || 'draft_restore',
        traceName: point.traceName || '',
        curveNumber: point.curveNumber,
        pointNumber: point.pointNumber,
        markerLabel: point.markerLabel || '',
        autoSuggested: !!point.autoSuggested,
        autoRole: point.autoRole || ''
      }};
    }}
    function restorePoint(point) {{
      if (!point || !point.x) return null;
      return {{
        x: point.x,
        y: point.y,
        source: point.source || 'draft_restore',
        traceName: point.traceName || '',
        curveNumber: point.curveNumber,
        pointNumber: point.pointNumber,
        markerLabel: point.markerLabel || '',
        autoSuggested: !!point.autoSuggested,
        autoRole: point.autoRole || '',
        placedAt: 0
      }};
    }}
    function markerShapes() {{
      var shapes = (gd.layout && Array.isArray(gd.layout.shapes) ? gd.layout.shapes : [])
        .filter(function (shape) {{ return !(shape && String(shape.name || '').indexOf('repeatation-marker') === 0); }});
      function axisRange(axisName) {{
        var axis = gd._fullLayout && gd._fullLayout[axisName];
        return axis && Array.isArray(axis.range) ? axis.range : null;
      }}
      function xAround(x, fraction) {{
        var range = axisRange('xaxis') || [meta.windowStart, meta.windowEnd];
        var start = Date.parse(range[0]);
        var end = Date.parse(range[1]);
        var center = Date.parse(x);
        if (!Number.isFinite(start) || !Number.isFinite(end) || !Number.isFinite(center) || start === end) return [x, x];
        var half = Math.abs(end - start) * (fraction || 0.006);
        return [new Date(center - half).toISOString(), new Date(center + half).toISOString()];
      }}
      function yAround(y, fraction) {{
        var range = axisRange('yaxis');
        var center = Number(y);
        if (!range || !Number.isFinite(center)) return [y, y];
        var start = Number(range[0]);
        var end = Number(range[1]);
        if (!Number.isFinite(start) || !Number.isFinite(end) || start === end) return [y, y];
        var half = Math.abs(end - start) * (fraction || 0.018);
        return [center - half, center + half];
      }}
      function crosshair(point, color, dash, name) {{
        if (!point || !point.x || !Number.isFinite(Number(point.y))) return;
        var isTrade = name.indexOf('trade') !== -1;
        function plusShape(sizeX, sizeY, width, fillAlpha) {{
          var xs = xAround(point.x, sizeX);
          var ys = yAround(point.y, sizeY);
          var line = {{ color: color, width: width, dash: dash || 'solid' }};
          shapes.push({{
            type: 'line',
            name: name + '-plus-v',
            xref: 'x',
            yref: 'y',
            x0: point.x,
            x1: point.x,
            y0: ys[0],
            y1: ys[1],
            line: line,
            layer: 'above'
          }});
          shapes.push({{
            type: 'line',
            name: name + '-plus-h',
            xref: 'x',
            yref: 'y',
            x0: xs[0],
            x1: xs[1],
            y0: point.y,
            y1: point.y,
            line: line,
            layer: 'above'
          }});
          if (fillAlpha) {{
            var haloXs = xAround(point.x, sizeX * 1.35);
            var haloYs = yAround(point.y, sizeY * 1.35);
            shapes.push({{
              type: 'circle',
              name: name + '-plus-glow',
              xref: 'x',
              yref: 'y',
              x0: haloXs[0],
              x1: haloXs[1],
              y0: haloYs[0],
              y1: haloYs[1],
              fillcolor: hexToRgba(color, fillAlpha),
              line: {{ color: 'rgba(248,250,252,0.55)', width: 0.7 }},
              layer: 'above'
            }});
          }}
        }}
        if (isChartMarkerPoint(point)) {{
          plusShape(isTrade ? 0.0048 : 0.004, isTrade ? 0.014 : 0.012, isTrade ? 1.8 : 1.5, isTrade ? '0.10' : '0.08');
          return;
        }}
        plusShape(isTrade ? 0.0028 : 0.0023, isTrade ? 0.007 : 0.006, isTrade ? 1.25 : 1.15, isTrade ? '0.05' : '');
      }}
      crosshair(state.tradeStart, MARKER_COLORS.tradeStart, 'solid', 'repeatation-marker-trade-start');
      crosshair(state.tradeEnd, MARKER_COLORS.tradeEnd, 'solid', 'repeatation-marker-trade-end');
      crosshair(state.ignoreStart, MARKER_COLORS.ignore, 'dash', 'repeatation-marker-ignore-start');
      crosshair(state.ignoreEnd, MARKER_COLORS.ignore, 'dash', 'repeatation-marker-ignore-end');
      if (state.ignoreStart && state.ignoreEnd) {{
        var pair = sortPoints(state.ignoreStart, state.ignoreEnd);
        shapes.push({{
          type: 'rect',
          name: 'repeatation-marker-ignore-region',
          xref: 'x',
          yref: 'paper',
          x0: pair[0].x,
          x1: pair[1].x,
          y0: 0,
          y1: 1,
          fillcolor: 'rgba(192,132,252,0.12)',
          line: {{ color: 'rgba(192,132,252,0.9)', width: 2, dash: 'dash' }},
          layer: 'above'
        }});
      }}
      return shapes;
    }}
    function markerAnnotations() {{
      var annotations = (gd.layout && Array.isArray(gd.layout.annotations) ? gd.layout.annotations : [])
        .filter(function (ann) {{ return !(ann && String(ann.name || '').indexOf('repeatation-marker') === 0); }});
      function shortTime(point) {{
        var ist = toIST(point && point.x);
        return ist ? ist.slice(5, 16) : '';
      }}
      function markerLabel(point, label, color, bg, ax, ay) {{
        if (!point || !point.x || !Number.isFinite(Number(point.y))) return;
        var price = Number(point.y);
        annotations.push({{
          name: 'repeatation-marker-' + label.toLowerCase().replace(/\\s+/g, '-') + '-label',
          xref: 'x',
          yref: 'y',
          x: point.x,
          y: point.y,
          text: '<b>' + esc(label) + '</b><br>' + esc(shortTime(point)) + (Number.isFinite(price) ? ' @ ' + price.toFixed(3) : ''),
          showarrow: true,
          arrowhead: 1,
          arrowsize: 0.8,
          arrowwidth: 1.2,
          arrowcolor: 'rgba(248,250,252,0.72)',
          ax: ax,
          ay: ay,
          bgcolor: bg,
          bordercolor: color,
          borderwidth: 1,
          borderpad: 3,
          font: {{ color: '#f8fafc', size: 10 }},
          align: 'left'
        }});
      }}
      function tradeProfitLabel() {{
        var result = tradeProfit();
        if (!result) return;
        annotations.push({{
          name: 'repeatation-marker-profit-label',
          xref: 'paper',
          yref: 'paper',
          x: 0.012,
          y: 0.975,
          text: '<b>Trade result</b><br>' + esc(result.outcomeLabel) + ' ' + esc(result.signedPipsText) + ' pips<br>' + esc(result.status),
          showarrow: false,
          xanchor: 'left',
          yanchor: 'top',
          bgcolor: 'rgba(88,28,135,0.42)',
          bordercolor: MARKER_COLORS.profit,
          borderwidth: 1,
          borderpad: 3,
          font: {{ color: '#f8fafc', size: 10 }},
          align: 'left'
        }});
      }}
      markerLabel(state.tradeStart, 'Start', MARKER_COLORS.tradeStart, 'rgba(8,47,73,0.46)', -44, -38);
      markerLabel(state.tradeEnd, 'End', MARKER_COLORS.tradeEnd, 'rgba(113,63,18,0.46)', 44, -38);
      markerLabel(state.ignoreStart, 'Ignore start', MARKER_COLORS.ignore, 'rgba(88,28,135,0.38)', -50, 36);
      markerLabel(state.ignoreEnd, 'Ignore end', MARKER_COLORS.ignore, 'rgba(88,28,135,0.38)', 50, 36);
      tradeProfitLabel();
      return annotations;
    }}
    function drawMarkers() {{
      Plotly.relayout(gd, {{ shapes: markerShapes(), annotations: markerAnnotations() }});
    }}
    function noteText() {{
      return panel.querySelector('#repeatation-note').value.trim();
    }}
    function valueOf(selector, fallback) {{
      var node = panel.querySelector(selector);
      return node ? String(node.value || fallback || '').trim() : (fallback || '');
    }}
    function labelFromKey(key) {{
      return String(key || '').replace(/_/g, ' ');
    }}
    function definitionRows(keys, definitions) {{
      return (keys || []).map(function (key) {{
        return {{
          key: key,
          label: labelFromKey(key),
          definition: definitions[key] || ''
        }};
      }});
    }}
    function buildIgnoreNoteBlock(types) {{
      if (!types || !types.length) return '';
      return 'Ignore signals:\\n' + types.map(function (key) {{
        return '- ' + labelFromKey(key) + ': ' + (IGNORE_SIGNAL_DEFINITIONS[key] || '');
      }}).join('\\n');
    }}
    function stripIgnoreNoteBlock(text) {{
      var raw = String(text || '');
      if (raw.indexOf('Ignore signals:\\n') !== 0) return raw;
      var splitAt = raw.indexOf('\\n\\n');
      return splitAt === -1 ? '' : raw.slice(splitAt + 2);
    }}
    function cleanLegacyIgnoreTradeNote(text) {{
      return String(text || '')
        .replace(new RegExp('(?:^|\\\\n)\\\\s*' + LEGACY_IGNORE_TRADE_NOTE.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&') + '\\\\s*(?=\\\\n|$)', 'g'), '\\n')
        .replace(/\\n{{3,}}/g, '\\n\\n')
        .trim();
    }}
    function syncIgnoreNotes() {{
      var noteNode = panel.querySelector('#repeatation-note');
      if (!noteNode) return;
      var custom = cleanLegacyIgnoreTradeNote(stripIgnoreNoteBlock(noteNode.value));
      var block = buildIgnoreNoteBlock(state.selectedIgnoreTypes);
      noteNode.value = block ? block + (custom ? '\\n\\n' + custom : '') : custom;
    }}
    function toggleIgnoreType(key) {{
      var found = state.selectedIgnoreTypes.indexOf(key);
      if (found === -1) state.selectedIgnoreTypes.push(key);
      else state.selectedIgnoreTypes.splice(found, 1);
      syncIgnoreNotes();
      render();
      saveDraft();
    }}
    function setIgnoreTypes(keys, syncNote) {{
      state.selectedIgnoreTypes = (keys || []).filter(function (key, index, arr) {{
        return key && arr.indexOf(key) === index && IGNORE_SIGNAL_DEFINITIONS[key];
      }});
      if (syncNote !== false) syncIgnoreNotes();
    }}
    function ignoreWhy() {{
      if (state.tradeIgnored) return noteText();
      return noteText() || 'manual repeatation ignore marker';
    }}
    function noteType() {{
      return panel.querySelector('#repeatation-note-type').value.trim() || 'general';
    }}
    function outcome() {{
      return panel.querySelector('#repeatation-outcome').value;
    }}
    function defaultOutcome() {{
      var value = String(meta.defaultOutcome || 'bullish').toLowerCase();
      if (['bullish', 'bearish', 'sideways', 'unclear'].indexOf(value) === -1) return 'bullish';
      return value;
    }}
    function setOutcome(value) {{
      panel.querySelector('#repeatation-outcome').value = value || defaultOutcome();
    }}
    function tradeProfit() {{
      if (!state.tradeStart || !state.tradeEnd) return null;
      var entry = Number(state.tradeStart.y);
      var exit = Number(state.tradeEnd.y);
      if (!Number.isFinite(entry) || !Number.isFinite(exit)) return null;
      var rawPips = (exit - entry) * 100;
      var selected = outcome();
      var signedPips = selected === 'bearish' ? -rawPips : rawPips;
      var status = signedPips > 0 ? 'favorable move' : (signedPips < 0 ? 'adverse move' : 'flat move');
      return {{
        entry: entry,
        exit: exit,
        rawPips: rawPips,
        signedPips: signedPips,
        signedPipsText: (signedPips >= 0 ? '+' : '') + signedPips.toFixed(1),
        rawPipsText: (rawPips >= 0 ? '+' : '') + rawPips.toFixed(1),
        outcomeLabel: selected,
        status: status,
        midPrice: (entry + exit) / 2
      }};
    }}
    function autoSuggestionHtml() {{
      if (!state.autoSuggestion) return '<div class="rm-auto muted">Auto Suggest has not been run for this repeatation.</div>';
      var s = state.autoSuggestion;
      return '<div class="rm-auto ' + esc(s.confidence || '') + '">'
        + '<div><b>Auto suggestion</b><span>' + esc(s.confidence || 'unknown') + '</span></div>'
        + '<div>' + esc(s.reason || '') + '</div>'
        + (s.manual_override ? '<div class="rm-warning">Manual override recorded: add a Rule Note explaining why.</div>' : '')
        + '</div>';
    }}
    var TRAIT_TAG_DEFINITIONS = {{
      'direction linked': 'This clue has repeatedly shown a clear lean in this same setup. The average result is at least 8 pips away from the group average.',
      'rare': 'This clue appears only 1 or 2 times. Treat it as a possible exception, not a rule.',
      'common': 'This clue appears in most repeats. It is background context, not a special edge by itself.',
      'only bullish samples': 'Every repeat with this clue moved upward for the full window.',
      'only bearish samples': 'Every repeat with this clue moved downward for the full window.',
      'context': 'Useful background clue, but not strong enough yet to call directional.'
    }};
    var TRAIT_FIELD_DEFINITIONS = {{
      event_duration: 'How long this setup stayed active. Short means fewer candles; long means more time for other events to interfere.',
      event_orb_deg: 'How far the aspect is from exact. Smaller usually means cleaner. Middle means not tight and not very loose.',
      shadbala_avg: 'Older planet-strength score kept for comparison.',
      event_sthana_dignity_virupa_avg: 'Basic strength of the involved planets. Higher means the planets are in a more supportive position.',
      event_strict_drik_bala_virupa_avg: 'Pressure from other planets. Negative leans stressful/downward; positive leans supportive/upward.',
      event_strict_saptavargaja_bala_virupa_avg: 'Planet strength checked across several chart divisions. Higher means stronger repeated support.',
      event_strict_ojayugma_bala_virupa_avg: 'A simple odd/even sign strength check. Higher means this condition supports the planet more.',
      event_strict_kaala_9_bala_virupa_avg: 'Timing strength. Higher means the event happens at a time that gives the planets more force.',
      event_strict_chesta_bala_virupa_avg: 'Motion strength. A slow, stopped, or backward-moving planet can act more strongly.',
      event_strict_shadbala_implemented_total_virupa_avg: 'Overall planet strength from all implemented parts. Higher means stronger planet signal.',
      event_strict_shadbala_implemented_total_ratio_avg: 'Overall strength compared with the minimum expected strength. Above 1.00 means above minimum.',
      edge_score: 'Overall setup score from the chart/scoring system. Higher means the setup looked stronger to the script.',
      tn_score_total: 'Quote-side pressure score. In USDJPY, this is the JPY side.',
      base_tn_score_total: 'Base-side pressure score. In USDJPY, this is the USD side.',
      aspect_regime_active_count: 'How many other event windows are active nearby. More overlap means harder to know which event moved price.',
      touch_planets: 'Which planet lines price touched near this event.',
      event_paksha: 'Moon phase half. Waxing means growing Moon; waning means shrinking Moon.',
      event_tithi_name: 'Lunar day name at the event time.',
      event_moon_nakshatra: 'Moon background zone at the event time.',
      event_weekday_lord: 'Planet linked with that weekday.'
    }};
    function traitBaseKey(trait) {{
      var key = String((trait && trait.key) || '').split(':')[0];
      return key || String((trait && trait.label) || '').replace(/\\s+/g, '_').toLowerCase();
    }}
    function traitFieldExplanation(trait) {{
      var base = traitBaseKey(trait);
      if (TRAIT_FIELD_DEFINITIONS[base]) return TRAIT_FIELD_DEFINITIONS[base];
      var label = String((trait && trait.label) || '').toLowerCase();
      if (label.indexOf('middle') > -1 || label.indexOf(' mid') > -1) return 'Middle means the number is between the low and high cutoffs.';
      if (label.indexOf('high') > -1) return 'High means the number is at or above the high cutoff.';
      if (label.indexOf('low') > -1) return 'Low means the number is at or below the low cutoff.';
      return 'A clue from this event compared with the same repeated setup.';
    }}
    function traitNumberLine(trait) {{
      var value = Number(trait.value);
      var low = Number(trait.low_cutoff);
      var high = Number(trait.high_cutoff);
      if (!Number.isFinite(value) || !Number.isFinite(low) || !Number.isFinite(high)) return '';
      return 'Value ' + value.toFixed(2) + ' | low <= ' + low.toFixed(2) + ' | high >= ' + high.toFixed(2);
    }}
    function traitTagExplanation(tags) {{
      return (tags || []).map(function (tag) {{
        return tag + ': ' + (TRAIT_TAG_DEFINITIONS[tag] || 'Trait ranking tag.');
      }}).join(' ');
    }}
    function strengthSummaryHtml(data) {{
      var items = Array.isArray(data.strength_summary) ? data.strength_summary : [];
      if (!items.length) return '';
      var rows = items.map(function (item) {{
        var value = Number(item.value);
        var low = Number(item.low_cutoff);
        var high = Number(item.high_cutoff);
        var valueText = Number.isFinite(value) ? value.toFixed(2) : '';
        var cutoffText = Number.isFinite(low) && Number.isFinite(high)
          ? 'low <= ' + low.toFixed(2) + ' | high >= ' + high.toFixed(2)
          : '';
        return '<div class="rm-strength-item">'
          + '<div><b>' + esc(item.plain_name || item.label || '') + '</b><span>' + esc(item.bucket || '') + '</span></div>'
          + '<div class="rm-trait-number">Value ' + esc(valueText) + (cutoffText ? ' | ' + esc(cutoffText) : '') + '</div>'
          + '<div class="rm-trait-explain">' + esc(item.help || traitFieldExplanation(item)) + '</div>'
          + '</div>';
      }}).join('');
      return '<div class="rm-strength">'
        + '<div><b>Planet strength</b><span>always shown</span></div>'
        + '<div class="rm-trait-method">This block is fixed. It does not disappear when ranked traits change.</div>'
        + rows
        + '</div>';
    }}
    function astroFeatureEvidenceHtml(data) {{
      var items = Array.isArray(data.astro_feature_evidence) ? data.astro_feature_evidence : [];
      if (!items.length) return '';
      var groups = {{}};
      items.forEach(function (item) {{
        var category = item.category || 'other context';
        if (!groups[category]) groups[category] = [];
        groups[category].push(item);
      }});
      var order = ['sign / house', 'planet strength', 'timing / moon calendar', 'overlap / cleanliness', 'market-score context', 'other context'];
      var groupHtml = order.filter(function (category) {{ return groups[category] && groups[category].length; }}).map(function (category) {{
        var rows = groups[category].slice(0, 24).map(function (item) {{
          var tags = Array.isArray(item.tags) ? item.tags.join(', ') : '';
          var avg = Number(item.avg_bullish_pips);
          var groupAvg = Number(item.group_avg_bullish_pips);
          var delta = Number(item.delta_vs_group_pips);
          var resultText = (Number.isFinite(avg) ? 'avg ' + avg.toFixed(1) + ' pips' : '')
            + (Number.isFinite(delta) ? ' | ' + (delta >= 0 ? '+' : '') + delta.toFixed(1) + ' vs group' : '')
            + (Number.isFinite(groupAvg) ? ' | group ' + groupAvg.toFixed(1) : '');
          var splitText = 'bullish ' + esc(item.bullish_samples || 0) + ' / bearish ' + esc(item.bearish_samples || 0);
          var numberLine = traitNumberLine(item);
          return '<tr title="' + esc(item.help || traitFieldExplanation(item)) + '">'
            + '<td>' + esc(item.label || item.key || '') + (numberLine ? '<div class="rm-table-sub">' + esc(numberLine) + '</div>' : '') + '</td>'
            + '<td>' + esc(item.occurrences || 0) + '/' + esc(item.repeatation_count || '') + '<div class="rm-table-sub">' + splitText + '</div></td>'
            + '<td>' + esc(resultText) + '</td>'
            + '<td>' + esc(tags) + '</td>'
            + '</tr>';
        }}).join('');
        return '<div class="rm-evidence-group"><div class="rm-evidence-title">' + esc(category) + '</div>'
          + '<table class="rm-evidence-table"><thead><tr><th>Feature</th><th>Repeats</th><th>Result</th><th>Tag</th></tr></thead><tbody>'
          + rows
          + '</tbody></table></div>';
      }}).join('');
      return '<details class="rm-evidence" open>'
        + '<summary>All astro feature comparison</summary>'
        + '<div class="rm-trait-method">Full current-case feature evidence, not just the top ranked hints. Negative pips lean bearish; positive pips lean bullish.</div>'
        + groupHtml
        + '</details>';
    }}
    function specialTraitsHtml() {{
      var data = meta.specialTraits || {{}};
      var traits = Array.isArray(data.traits) ? data.traits : [];
      var strengthHtml = strengthSummaryHtml(data);
      var evidenceHtml = astroFeatureEvidenceHtml(data);
      if (!traits.length) return strengthHtml + evidenceHtml + '<div class="rm-traits muted">No trait hints available for this recurrence yet.</div>';
      var rows = traits.slice(0, 6).map(function (trait) {{
        var tagList = Array.isArray(trait.tags) ? trait.tags : [];
        var tags = tagList.join(', ');
        var delta = Number(trait.delta_vs_group_pips);
        var deltaText = Number.isFinite(delta) ? (delta >= 0 ? '+' : '') + delta.toFixed(1) + ' pips vs group' : '';
        var explanation = traitFieldExplanation(trait);
        var tagHelp = traitTagExplanation(tagList);
        var numberLine = traitNumberLine(trait);
        return '<div class="rm-trait-item" title="' + esc(explanation + ' ' + tagHelp) + '">'
          + '<div><b>' + esc(trait.label || trait.key || '') + '</b><span title="' + esc(tagHelp) + '">' + esc(tags) + '</span></div>'
          + '<div>' + esc(trait.occurrences) + '/' + esc(trait.repeatation_count) + ' repeatations'
          + (deltaText ? ' | ' + esc(deltaText) : '')
          + '</div>'
          + (numberLine ? '<div class="rm-trait-number">' + esc(numberLine) + '</div>' : '')
          + '<div class="rm-trait-explain">' + esc(explanation) + '</div>'
          + '</div>';
      }}).join('');
      return strengthHtml + '<div class="rm-traits">'
        + '<div><b>ML trait hints</b><span>' + esc(data.case_full_window_direction || '') + ' ' + esc(data.case_full_window_bullish_pips || '') + ' pips</span></div>'
        + '<div><a class="rm-guide-link" href="' + esc(meta.traitGuideHref || 'trait_guide.html') + '" target="_blank" rel="noopener">Open trait guide</a></div>'
        + '<div class="rm-trait-method">' + esc(data.method || '') + '</div>'
        + rows
        + '</div>' + evidenceHtml;
    }}
    function profitHtml() {{
      var result = tradeProfit();
      if (!result) return '<div class="rm-profit muted">Select trade start and trade end to calculate live pips.</div>';
      return '<div class="rm-profit">'
        + '<div><b>Live trade result</b><span>' + esc(result.outcomeLabel) + '</span></div>'
        + '<div class="rm-profit-value">' + esc(result.signedPipsText) + ' pips</div>'
        + '<div>Entry ' + esc(result.entry.toFixed(3)) + ' -> Exit ' + esc(result.exit.toFixed(3)) + ' | raw move ' + esc(result.rawPipsText) + ' pips</div>'
        + '<div>' + esc(result.status) + '</div>'
        + '</div>';
    }}
    function tradeCommand() {{
      if (!state.tradeStart || !state.tradeEnd) return '';
      var pair = sortPoints(state.tradeStart, state.tradeEnd);
      return 'python .\\\\aspect_annotation_store.py --add-trade-annotation'
        + ' --case-id ' + meta.caseId
        + ' --trade-start ' + shellQuote(toIST(pair[0].x))
        + ' --trade-end ' + shellQuote(toIST(pair[1].x))
        + ' --outcome-label ' + outcome()
        + ' --price-timeframe ' + meta.priceTimeframe
        + ' --why ' + shellQuote(noteText() || 'manual repeatation trade marker');
    }}
    function ignoreCommand() {{
      if (!state.ignoreStart || !state.ignoreEnd) return '';
      var why = ignoreWhy();
      if (state.tradeIgnored && !why) return '';
      var pair = sortPoints(state.ignoreStart, state.ignoreEnd);
      return 'python .\\\\aspect_annotation_store.py --mark-ignore-region'
        + ' --case-id ' + meta.caseId
        + ' --region-start ' + shellQuote(toIST(pair[0].x))
        + ' --region-end ' + shellQuote(toIST(pair[1].x))
        + ' --why ' + shellQuote(why);
    }}
    function ruleCommand() {{
      if (!noteText()) return '';
      return 'python .\\\\aspect_annotation_store.py --add-rule-note'
        + ' --case-id ' + meta.caseId
        + ' --note-type ' + shellQuote(noteType())
        + ' --note ' + shellQuote(noteText());
    }}
    function commandBlock(label, command) {{
      if (!command) return '<div class="muted">' + label + ': place required markers / note first</div>';
      return '<label>' + label + '</label><pre>' + esc(command) + '</pre><button data-copy="' + esc(command) + '">Copy ' + label + '</button>';
    }}
    function annotationContext() {{
      var ignorePair = state.ignoreStart && state.ignoreEnd ? sortPoints(state.ignoreStart, state.ignoreEnd) : null;
      var tradePair = state.tradeStart && state.tradeEnd ? sortPoints(state.tradeStart, state.tradeEnd) : null;
      return {{
        last_point: serialPoint(state.lastPoint),
        trade_start: serialPoint(tradePair ? tradePair[0] : state.tradeStart),
        trade_end: serialPoint(tradePair ? tradePair[1] : state.tradeEnd),
        ignore_start: serialPoint(ignorePair ? ignorePair[0] : state.ignoreStart),
        ignore_end: serialPoint(ignorePair ? ignorePair[1] : state.ignoreEnd),
        trade_ignored: state.tradeIgnored,
        window_start: meta.windowStart,
        window_end: meta.windowEnd
      }};
    }}
    function annotationRow(kind) {{
      var note = noteText();
      if (!note) {{
        updateSaveStatus('note required before adding ML annotation');
        return null;
      }}
      if (kind === 'ignore_signal' && !state.ignoreStart && !state.ignoreEnd && !state.tradeIgnored) {{
        updateSaveStatus('place ignore markers or use Ignore Trade first');
        return null;
      }}
      if (kind === 'ignore_signal' && !state.selectedIgnoreTypes.length) {{
        updateSaveStatus('select at least one ignore signal type');
        return null;
      }}
      var ignoreDefinitions = definitionRows(state.selectedIgnoreTypes, IGNORE_SIGNAL_DEFINITIONS);
      var ruleType = valueOf('#repeatation-rule-type', 'behavior_rule');
      var ruleScope = valueOf('#repeatation-rule-scope', 'case_family');
      return {{
        id: 'ann-' + Date.now() + '-' + Math.floor(Math.random() * 10000),
        kind: kind,
        scope: kind === 'ignore_signal' ? 'local_window' : ruleScope,
        scope_definition: kind === 'ignore_signal' ? RULE_SCOPE_DEFINITIONS.local_window : RULE_SCOPE_DEFINITIONS[ruleScope],
        type: kind === 'ignore_signal' ? state.selectedIgnoreTypes.join(';') : ruleType,
        types: kind === 'ignore_signal' ? state.selectedIgnoreTypes.slice() : [ruleType],
        type_definitions: kind === 'ignore_signal' ? ignoreDefinitions : definitionRows([ruleType], RULE_TYPE_DEFINITIONS),
        note_type: noteType(),
        note: note,
        case_id: meta.caseId,
        pair_key: meta.pairKey,
        aspect: meta.aspect,
        price_timeframe: meta.priceTimeframe,
        created_at: new Date().toISOString(),
        context: annotationContext()
      }};
    }}
    function addAnnotation(kind) {{
      var row = annotationRow(kind);
      if (!row) return;
      state.annotations.push(row);
      render();
      saveDraft();
      updateSaveStatus(kind === 'ignore_signal' ? 'ignore signal added for ML' : 'rule note added for ML');
    }}
    function clearAnnotations() {{
      state.annotations = [];
      render();
      saveDraft();
      updateSaveStatus('ML annotations cleared');
    }}
    function deleteAnnotation(id) {{
      state.annotations = state.annotations.filter(function (item) {{ return item && item.id !== id; }});
      render();
      saveDraft();
      updateSaveStatus('ML annotation removed');
    }}
    function annotationLedgerHtml() {{
      if (!state.annotations.length) return '<div class="muted">No ML annotations yet</div>';
      return state.annotations.map(function (item, index) {{
        var typeLabel = (item.types || [item.type]).map(labelFromKey).join(', ');
        return '<div class="rm-ledger-item">'
          + '<div><b>' + esc(index + 1) + '. ' + esc(labelFromKey(item.kind)) + '</b> <span>' + esc(labelFromKey(item.scope)) + ' / ' + esc(typeLabel) + '</span></div>'
          + '<div>' + esc(item.note) + '</div>'
          + '<button data-delete-annotation="' + esc(item.id) + '" type="button">Remove</button>'
          + '</div>';
      }}).join('');
    }}
    function ignoreTypeButtonsHtml() {{
      return Object.keys(IGNORE_SIGNAL_DEFINITIONS).map(function (key) {{
        var active = state.selectedIgnoreTypes.indexOf(key) !== -1;
        return '<button type="button" class="rm-chip ' + (active ? 'active' : '') + '" data-ignore-type="' + esc(key) + '" title="' + esc(IGNORE_SIGNAL_DEFINITIONS[key]) + '">' + esc(labelFromKey(key)) + '</button>';
      }}).join('');
    }}
    function selectedIgnoreDefinitionsHtml() {{
      if (!state.selectedIgnoreTypes.length) return '<div class="muted">Select one or more ignore signal types; each selection adds a point to Notes / why.</div>';
      return state.selectedIgnoreTypes.map(function (key) {{
        return '<div><b>' + esc(labelFromKey(key)) + '</b>: ' + esc(IGNORE_SIGNAL_DEFINITIONS[key]) + '</div>';
      }}).join('');
    }}
    function navLink(label, href, className) {{
      if (!href) return '<span class="rm-soft disabled">' + esc(label) + '</span>';
      return '<a class="rm-soft ' + esc(className || '') + '" href="' + esc(href) + '">' + esc(label) + '</a>';
    }}
    function render() {{
      panel.querySelector('#repeatation-last').textContent = fmtPoint(state.lastPoint);
      panel.querySelector('#repeatation-trade-start').textContent = fmtPoint(state.tradeStart);
      panel.querySelector('#repeatation-trade-end').textContent = fmtPoint(state.tradeEnd);
      panel.querySelector('#repeatation-ignore-start').textContent = fmtPoint(state.ignoreStart);
      panel.querySelector('#repeatation-ignore-end').textContent = fmtPoint(state.ignoreEnd);
      panel.querySelector('#repeatation-ignore-trade-status').textContent = state.tradeIgnored
        ? 'Ignore Trade is ON for this case window'
        : 'Ignore Trade is off';
      panel.querySelector('#repeatation-ignore-trade').classList.toggle('active', state.tradeIgnored);
      panel.querySelector('#repeatation-profit-summary').innerHTML = profitHtml();
      panel.querySelector('#repeatation-auto-summary').innerHTML = autoSuggestionHtml();
      panel.querySelector('#repeatation-special-traits').innerHTML = specialTraitsHtml();
      panel.querySelector('#repeatation-ignore-type-buttons').innerHTML = ignoreTypeButtonsHtml();
      panel.querySelector('#repeatation-ignore-definitions').innerHTML = selectedIgnoreDefinitionsHtml();
      panel.querySelector('#repeatation-commands').innerHTML =
        commandBlock('Trade', tradeCommand())
        + commandBlock(state.tradeIgnored ? 'Ignore trade' : 'Ignore', ignoreCommand())
        + commandBlock('Rule note', ruleCommand());
      panel.querySelector('#repeatation-annotation-ledger').innerHTML = annotationLedgerHtml();
      panel.querySelectorAll('[data-copy]').forEach(function (button) {{
        button.addEventListener('click', function () {{
          navigator.clipboard.writeText(button.getAttribute('data-copy') || '');
          button.textContent = 'Copied';
          setTimeout(function () {{ button.textContent = 'Copy'; }}, 1200);
        }});
      }});
      panel.querySelectorAll('[data-delete-annotation]').forEach(function (button) {{
        button.addEventListener('click', function () {{
          deleteAnnotation(button.getAttribute('data-delete-annotation') || '');
        }});
      }});
      panel.querySelectorAll('[data-ignore-type]').forEach(function (button) {{
        button.addEventListener('click', function () {{
          toggleIgnoreType(button.getAttribute('data-ignore-type') || '');
        }});
      }});
      updateSaveStatus();
    }}
    function draftPayload() {{
      return {{
        version: 2,
        saved_at: new Date().toISOString(),
        case_id: meta.caseId,
        pair_key: meta.pairKey,
        aspect: meta.aspect,
        price_timeframe: meta.priceTimeframe,
        window_start: meta.windowStart,
        window_end: meta.windowEnd,
        collapsed: panel.classList.contains('collapsed'),
        tool: state.tool,
        trade_start: serialPoint(state.tradeStart),
        trade_end: serialPoint(state.tradeEnd),
        ignore_start: serialPoint(state.ignoreStart),
        ignore_end: serialPoint(state.ignoreEnd),
        trade_ignored: state.tradeIgnored,
        auto_suggestion: state.autoSuggestion,
        selected_ignore_types: state.selectedIgnoreTypes,
        ml_annotations: state.annotations,
        last_point: serialPoint(state.lastPoint),
        outcome_label: outcome(),
        outcome_touched: state.outcomeTouched,
        note_type: noteType(),
        note: noteText()
      }};
    }}
    function saveDraft() {{
      if (!panel || !window.localStorage) return;
      try {{
        var payload = draftPayload();
        window.localStorage.setItem(storageKey, JSON.stringify(payload));
        state.lastSavedAt = payload.saved_at;
        updateSaveStatus();
      }} catch (err) {{
        updateSaveStatus('autosave unavailable');
      }}
    }}
    function hasDraftableContent() {{
      return !!(state.tradeStart || state.tradeEnd || state.ignoreStart || state.ignoreEnd || state.tradeIgnored || state.annotations.length || noteText() || state.draftLoaded);
    }}
    function loadDraft() {{
      if (!window.localStorage) return null;
      try {{
        var raw = window.localStorage.getItem(storageKey);
        return raw ? JSON.parse(raw) : null;
      }} catch (err) {{
        return null;
      }}
    }}
    function restoreDraft() {{
      var draft = loadDraft();
      if (!draft) return false;
      state.tradeStart = restorePoint(draft.trade_start);
      state.tradeEnd = restorePoint(draft.trade_end);
      state.ignoreStart = restorePoint(draft.ignore_start);
      state.ignoreEnd = restorePoint(draft.ignore_end);
      state.tradeIgnored = !!draft.trade_ignored;
      state.autoSuggestion = draft.auto_suggestion || null;
      state.outcomeTouched = !!draft.outcome_touched;
      setIgnoreTypes(Array.isArray(draft.selected_ignore_types) ? draft.selected_ignore_types : [], false);
      state.annotations = Array.isArray(draft.ml_annotations) ? draft.ml_annotations : [];
      state.lastPoint = restorePoint(draft.last_point) || state.tradeStart || state.tradeEnd || state.ignoreStart || state.ignoreEnd;
      var restoredOutcome = draft.outcome_label || defaultOutcome();
      if (!state.outcomeTouched && Number(draft.version || 1) < 2 && restoredOutcome === 'bullish' && defaultOutcome() !== 'bullish') {{
        restoredOutcome = defaultOutcome();
      }}
      setOutcome(restoredOutcome);
      panel.querySelector('#repeatation-note-type').value = draft.note_type || 'manual_repeatation_note';
      panel.querySelector('#repeatation-note').value = draft.note || '';
      if (state.selectedIgnoreTypes.length) syncIgnoreNotes();
      setCollapsed(draft.collapsed !== false, false);
      setTool('', false);
      state.draftLoaded = true;
      state.lastSavedAt = draft.saved_at || '';
      drawMarkers();
      render();
      return true;
    }}
    function clearSavedDraft() {{
      try {{
        window.localStorage.removeItem(storageKey);
      }} catch (err) {{}}
      state.tradeStart = null;
      state.tradeEnd = null;
      state.ignoreStart = null;
      state.ignoreEnd = null;
      state.tradeIgnored = false;
      state.autoSuggestion = null;
      state.selectedIgnoreTypes = [];
      state.annotations = [];
      state.outcomeTouched = false;
      state.lastPoint = null;
      state.draftLoaded = false;
      state.lastSavedAt = '';
      setOutcome(defaultOutcome());
      panel.querySelector('#repeatation-note-type').value = 'manual_repeatation_note';
      panel.querySelector('#repeatation-note').value = '';
      setTool('', false);
      drawMarkers();
      render();
      updateSaveStatus('local draft cleared');
    }}
    function updateSaveStatus(message) {{
      if (!panel) return;
      var node = panel.querySelector('#repeatation-save-status');
      if (!node) return;
      if (message) {{
        node.textContent = message;
        return;
      }}
      if (state.lastSavedAt) {{
        node.textContent = (state.draftLoaded ? 'Draft restored; ' : '') + 'autosaved locally ' + new Date(state.lastSavedAt).toLocaleString();
      }} else {{
        node.textContent = 'Autosaves locally after first edit';
      }}
    }}
    function clearMarkers() {{
      state.tradeStart = null;
      state.tradeEnd = null;
      state.ignoreStart = null;
      state.ignoreEnd = null;
      state.tradeIgnored = false;
      state.autoSuggestion = null;
      state.lastPoint = null;
      setTool('', false);
      drawMarkers();
      render();
      saveDraft();
    }}
    function autoSuggestTrade() {{
      var markers = collectChartMarkers();
      if (!markers.length) {{
        state.autoSuggestion = {{
          active: false,
          confidence: 'no marker',
          reason: 'No hardcoded chart markers were available in this chart.',
          manual_override: false,
          overridden_keys: [],
          created_at: new Date().toISOString()
        }};
        render();
        saveDraft();
        updateSaveStatus('auto suggest: no hardcoded chart markers found');
        return;
      }}
      var selected = markers.filter(function (point) {{ return point.isSelectedCaseTouch; }});
      var windowMarkers = markers.filter(pointInCaseWindow);
      var start = selected[0] || windowMarkers[0] || markers[0];
      var startTime = markerTime(start);
      var minGapMs = 60000;
      var end = markers.find(function (point) {{
        return markerTime(point) > startTime + minGapMs;
      }});
      var confidence = selected[0] ? 'clean' : (windowMarkers[0] ? 'fallback' : 'weak');
      var reason = selected[0]
        ? 'Start used the first selected-case hardcoded touch; end used the next later hardcoded marker.'
        : (windowMarkers[0]
          ? 'No selected-case touch marker was found, so start used the first marker inside the case window; end used the next later marker.'
          : 'No marker inside the case window was found, so start used the first visible marker; review carefully.');
      if (!end) {{
        confidence = 'incomplete';
        reason += ' No later marker was found for trade end.';
      }}
      setTool('', false);
      state.autoSuggestion = {{
        active: !!(start && end),
        confidence: confidence,
        reason: reason,
        marker_count: markers.length,
        selected_case_marker_count: selected.length,
        start_rule: selected[0] ? 'first_selected_case_touch' : (windowMarkers[0] ? 'first_marker_inside_case_window' : 'first_visible_marker'),
        end_rule: end ? 'next_later_hardcoded_marker' : 'not_found',
        manual_override: false,
        overridden_keys: [],
        created_at: new Date().toISOString()
      }};
      if (start) setStatePoint('tradeStart', autoSuggestedPoint(start, 'auto_trade_start'));
      if (end) setStatePoint('tradeEnd', autoSuggestedPoint(end, 'auto_trade_end'));
      drawMarkers();
      render();
      saveDraft();
      updateSaveStatus(end ? 'auto suggested trade start/end from hardcoded markers' : 'auto suggested start only; no later end marker found');
    }}
    function markIgnoreTrade() {{
      state.ignoreStart = caseWindowPoint(meta.windowStart, 'case_window_ignore_trade_start');
      state.ignoreEnd = caseWindowPoint(meta.windowEnd, 'case_window_ignore_trade_end');
      state.tradeIgnored = true;
      var nextTypes = state.selectedIgnoreTypes.slice();
      if (nextTypes.indexOf('ignore_trade_nearby_event') === -1) nextTypes.unshift('ignore_trade_nearby_event');
      setIgnoreTypes(nextTypes, true);
      if (!panel.querySelector('#repeatation-note-type').value.trim()) panel.querySelector('#repeatation-note-type').value = 'ignore_trade_nearby_event';
      setTool('', false);
      drawMarkers();
      render();
      saveDraft();
    }}
    function resetCursorState() {{
      [document.documentElement, document.body, gd, gd.closest('.plot-container'), gd.querySelector('.draglayer'), gd.querySelector('.svg-container')].forEach(function (node) {{
        if (node && node.style) node.style.cursor = '';
      }});
      gd.querySelectorAll('[style*="cursor"]').forEach(function (node) {{
        if (node && node.style) node.style.cursor = '';
      }});
      try {{
        if (window.getSelection) window.getSelection().removeAllRanges();
      }} catch (err) {{}}
      if (document.activeElement && document.activeElement.blur && !panel.contains(document.activeElement)) {{
        document.activeElement.blur();
      }}
      updateSaveStatus('cursor reset without reloading');
    }}
    function downloadMarkers() {{
      var payload = {{
        case_id: meta.caseId,
        pair_key: meta.pairKey,
        aspect: meta.aspect,
        trade_start_ist: state.tradeStart ? toIST(state.tradeStart.x) : '',
        trade_end_ist: state.tradeEnd ? toIST(state.tradeEnd.x) : '',
        ignore_start_ist: state.ignoreStart ? toIST(state.ignoreStart.x) : '',
        ignore_end_ist: state.ignoreEnd ? toIST(state.ignoreEnd.x) : '',
        trade_ignored: state.tradeIgnored,
        auto_suggestion: state.autoSuggestion,
        selected_ignore_types: state.selectedIgnoreTypes,
        ml_annotations: state.annotations,
        trade_profit: tradeProfit(),
        annotation_definitions: {{
          ignore_signal_types: IGNORE_SIGNAL_DEFINITIONS,
          rule_scopes: RULE_SCOPE_DEFINITIONS,
          rule_types: RULE_TYPE_DEFINITIONS
        }},
        outcome_label: outcome(),
        note_type: noteType(),
        note: noteText(),
        trade_command: tradeCommand(),
        ignore_command: ignoreCommand(),
        rule_note_command: ruleCommand()
      }};
      var blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'case_' + meta.caseId + '_repeatation_markers.json';
      a.click();
      URL.revokeObjectURL(url);
    }}
    var panel = document.createElement('aside');
    panel.id = 'repeatation-marker-panel';
    panel.className = 'collapsed';
    panel.innerHTML = ''
      + '<div class="rm-head"><div><div class="rm-title">Markers</div><div class="rm-mini">case ' + esc(meta.caseId) + '</div></div><button id="repeatation-toggle" type="button" title="Expand marker drawer">Open</button></div>'
      + '<div class="rm-body">'
      + '<div class="rm-sub">case_id=' + esc(meta.caseId) + ' | ' + esc(meta.pairKey) + ' ' + esc(meta.aspect) + '</div>'
      + '<div class="rm-sub">Window: ' + esc(meta.windowStart) + ' -> ' + esc(meta.windowEnd) + '</div>'
      + '<div class="rm-nav"><span>Repeatation ' + esc(meta.repeatationIndex) + ' / ' + esc(meta.repeatationCount) + '</span>'
      + navLink('Previous', meta.previousHref, 'prev')
      + navLink('Next', meta.nextHref, 'next')
      + navLink('All', meta.reviewerHref, 'all')
      + '</div>'
      + '<div class="rm-tools">'
      + '<button data-tool="trade_start">Trade start</button>'
      + '<button data-tool="trade_end">Trade end</button>'
      + '<button data-tool="ignore_start">Ignore start</button>'
      + '<button data-tool="ignore_end">Ignore end</button>'
      + '</div>'
      + '<div class="rm-actions"><button id="repeatation-auto-suggest" type="button">Auto Suggest</button><span class="rm-status-inline">hardcoded marker start -> next marker end</span></div>'
      + '<div id="repeatation-auto-summary"></div>'
      + '<div class="rm-actions"><button id="repeatation-ignore-trade" type="button">Ignore Trade</button><span id="repeatation-ignore-trade-status" class="rm-status-inline">Ignore Trade is off</span></div>'
      + '<div class="rm-grid"><span>Last click</span><b id="repeatation-last">not set</b><span>Trade start</span><b id="repeatation-trade-start">not set</b><span>Trade end</span><b id="repeatation-trade-end">not set</b><span>Ignore start</span><b id="repeatation-ignore-start">not set</b><span>Ignore end</span><b id="repeatation-ignore-end">not set</b></div>'
      + '<div id="repeatation-profit-summary"></div>'
      + '<div id="repeatation-special-traits"></div>'
      + '<label>Outcome</label><select id="repeatation-outcome"><option value="bullish">bullish</option><option value="bearish">bearish</option><option value="sideways">sideways</option><option value="unclear">unclear</option></select>'
      + '<label>Note type</label><input id="repeatation-note-type" value="manual_repeatation_note">'
      + '<label>Notes / why</label><textarea id="repeatation-note" placeholder="Why this start/end or ignore marker?"></textarea>'
      + '<label>Ignore signal types</label><div id="repeatation-ignore-type-buttons" class="rm-chip-grid"></div><div id="repeatation-ignore-definitions" class="rm-def-list"></div>'
      + '<label>Rule scope / type</label><div class="rm-row"><select id="repeatation-rule-scope"><option value="case_family">case_family</option><option value="case_id">case_id</option><option value="local_window">local_window</option><option value="global">global</option></select><select id="repeatation-rule-type"><option value="behavior_rule">behavior_rule</option><option value="exception_rule">exception_rule</option><option value="confidence_rule">confidence_rule</option><option value="dignity_rule">dignity_rule</option><option value="regime_rule">regime_rule</option><option value="sr_rule">sr_rule</option><option value="ml_feature_hint">ml_feature_hint</option></select></div>'
      + '<div class="rm-actions"><button id="repeatation-add-ignore-signal" type="button">Add Ignore Signal</button><button id="repeatation-add-rule-note" type="button">Add Rule Note</button><button id="repeatation-clear-annotations" type="button">Clear ML Notes</button></div>'
      + '<label>ML annotation ledger</label><div id="repeatation-annotation-ledger"></div>'
      + '<div class="rm-actions"><button id="repeatation-clear">Clear markers</button><button id="repeatation-clear-draft">Clear saved draft</button><button id="repeatation-reset-cursor">Reset Cursor</button><button id="repeatation-download">Download JSON</button></div>'
      + '<div id="repeatation-save-status" class="rm-status">Autosaves locally after first edit</div>'
      + '<div id="repeatation-commands"></div>'
      + '</div>';
    var style = document.createElement('style');
    style.textContent = ''
      + '#repeatation-marker-panel{{position:fixed;right:12px;top:14px;z-index:9999;width:min(360px,calc(100vw - 24px));max-height:88vh;overflow:auto;background:#0f172a;color:#e5e7eb;border:1px solid #475569;border-radius:8px;box-shadow:0 12px 34px rgba(0,0,0,.38);font:12px/1.35 Arial,sans-serif;padding:10px;transition:width .18s ease,opacity .18s ease;}}'
      + '#repeatation-marker-panel.collapsed{{width:132px;overflow:hidden;opacity:.92;}}'
      + '#repeatation-marker-panel .rm-head{{display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-title{{font-weight:700;font-size:14px;margin-bottom:1px;}}'
      + '#repeatation-marker-panel .rm-mini{{color:#93c5fd;font-size:11px;}}'
      + '#repeatation-marker-panel.collapsed .rm-body{{display:none;}}'
      + '#repeatation-marker-panel .rm-sub{{color:#cbd5e1;margin-bottom:6px;}}'
      + '#repeatation-marker-panel .rm-nav{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:7px 0;color:#cbd5e1;}}'
      + '#repeatation-marker-panel .rm-soft{{display:inline-flex;align-items:center;justify-content:center;min-height:24px;padding:3px 7px;border:1px solid #64748b;border-radius:5px;background:#111827;color:#e5e7eb;text-decoration:none;}}'
      + '#repeatation-marker-panel .rm-soft.disabled{{opacity:.45;pointer-events:none;}}'
      + '#repeatation-marker-panel label{{display:block;margin:8px 0 3px;color:#bfdbfe;font-weight:600;}}'
      + '#repeatation-marker-panel button,#repeatation-marker-panel select,#repeatation-marker-panel input,#repeatation-marker-panel textarea{{font:12px Arial,sans-serif;border-radius:5px;border:1px solid #64748b;background:#111827;color:#e5e7eb;}}'
      + '#repeatation-marker-panel button{{padding:5px 8px;cursor:pointer;}}'
      + '#repeatation-marker-panel button.active{{background:#2563eb;border-color:#60a5fa;}}'
      + '#repeatation-marker-panel #repeatation-ignore-trade.active{{background:#f97316;border-color:#fdba74;color:#111827;font-weight:700;}}'
      + '#repeatation-marker-panel select,#repeatation-marker-panel input,#repeatation-marker-panel textarea{{width:100%;box-sizing:border-box;padding:6px;}}'
      + '#repeatation-marker-panel textarea{{height:64px;resize:vertical;}}'
      + '#repeatation-marker-panel pre{{white-space:pre-wrap;background:#020617;color:#dbeafe;border:1px solid #1e293b;border-radius:5px;padding:6px;margin:3px 0 5px;max-height:120px;overflow:auto;}}'
      + '#repeatation-marker-panel .rm-tools,#repeatation-marker-panel .rm-actions{{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0;}}'
      + '#repeatation-marker-panel .rm-row{{display:grid;grid-template-columns:1fr 1fr;gap:6px;}}'
      + '#repeatation-marker-panel .rm-chip-grid{{display:flex;gap:5px;flex-wrap:wrap;margin:5px 0;}}'
      + '#repeatation-marker-panel .rm-chip{{font-size:11px;padding:4px 7px;}}'
      + '#repeatation-marker-panel .rm-chip.active{{background:#f97316;border-color:#fdba74;color:#111827;font-weight:700;}}'
      + '#repeatation-marker-panel .rm-def-list{{color:#cbd5e1;background:#020617;border:1px solid #1e293b;border-radius:5px;padding:6px;margin:5px 0;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-def-list div{{margin:3px 0;}}'
      + '#repeatation-marker-panel .rm-grid{{display:grid;grid-template-columns:88px 1fr;gap:4px 8px;background:#111827;border:1px solid #1e293b;border-radius:6px;padding:8px;}}'
      + '#repeatation-marker-panel .rm-grid span{{color:#94a3b8;}}'
      + '#repeatation-marker-panel .rm-profit{{background:#111827;border:1px solid #334155;border-radius:6px;padding:8px;margin:8px 0;color:#cbd5e1;}}'
      + '#repeatation-marker-panel .rm-profit>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#bfdbfe;}}'
      + '#repeatation-marker-panel .rm-profit span{{color:#fde68a;}}'
      + '#repeatation-marker-panel .rm-profit-value{{font-size:18px;font-weight:700;color:#fef3c7;margin:4px 0;}}'
      + '#repeatation-marker-panel .rm-auto{{background:#020617;border:1px solid #334155;border-radius:6px;padding:7px;margin:6px 0;color:#cbd5e1;}}'
      + '#repeatation-marker-panel .rm-auto>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#bfdbfe;}}'
      + '#repeatation-marker-panel .rm-auto span{{color:#fde68a;}}'
      + '#repeatation-marker-panel .rm-auto.clean{{border-color:#38bdf8;}}'
      + '#repeatation-marker-panel .rm-auto.fallback,.rm-auto.weak,.rm-auto.incomplete{{border-color:#fbbf24;}}'
      + '#repeatation-marker-panel .rm-warning{{color:#fbbf24;margin-top:4px;}}'
      + '#repeatation-marker-panel .rm-strength{{background:#07111f;border:1px solid #38bdf8;border-radius:6px;padding:7px;margin:6px 0;color:#cbd5e1;}}'
      + '#repeatation-marker-panel .rm-strength>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#bfdbfe;}}'
      + '#repeatation-marker-panel .rm-strength span{{color:#67e8f9;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-strength-item{{border-top:1px solid #1e3a5f;padding-top:5px;margin-top:5px;}}'
      + '#repeatation-marker-panel .rm-strength-item>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-evidence{{background:#020617;border:1px solid #334155;border-radius:6px;padding:7px;margin:6px 0;color:#cbd5e1;}}'
      + '#repeatation-marker-panel .rm-evidence summary{{cursor:pointer;color:#bfdbfe;font-weight:700;}}'
      + '#repeatation-marker-panel .rm-evidence-group{{margin-top:8px;}}'
      + '#repeatation-marker-panel .rm-evidence-title{{color:#fde68a;font-weight:700;margin:4px 0;}}'
      + '#repeatation-marker-panel .rm-evidence-table{{width:100%;border-collapse:collapse;font-size:10.5px;}}'
      + '#repeatation-marker-panel .rm-evidence-table th,#repeatation-marker-panel .rm-evidence-table td{{border:1px solid #1e293b;padding:4px;vertical-align:top;}}'
      + '#repeatation-marker-panel .rm-evidence-table th{{color:#bfdbfe;background:#0f172a;text-align:left;}}'
      + '#repeatation-marker-panel .rm-table-sub{{color:#94a3b8;font-size:10px;margin-top:2px;}}'
      + '#repeatation-marker-panel .rm-traits{{background:#020617;border:1px solid #334155;border-radius:6px;padding:7px;margin:6px 0;color:#cbd5e1;}}'
      + '#repeatation-marker-panel .rm-traits>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#bfdbfe;}}'
      + '#repeatation-marker-panel .rm-traits span{{color:#fde68a;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-guide-link{{display:inline-flex;margin:4px 0 2px;color:#93c5fd;text-decoration:underline;text-underline-offset:2px;}}'
      + '#repeatation-marker-panel .rm-trait-method{{color:#94a3b8;font-size:11px;margin:4px 0 6px;}}'
      + '#repeatation-marker-panel .rm-trait-item{{border-top:1px solid #1e293b;padding-top:5px;margin-top:5px;}}'
      + '#repeatation-marker-panel .rm-trait-item>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-trait-number{{color:#f8fafc;font-size:11px;margin-top:2px;}}'
      + '#repeatation-marker-panel .rm-trait-explain{{color:#93a4b8;font-size:11px;margin-top:2px;}}'
      + '#repeatation-marker-panel .rm-ledger-item{{background:#020617;border:1px solid #334155;border-radius:5px;padding:6px;margin:5px 0;}}'
      + '#repeatation-marker-panel .rm-ledger-item span{{color:#93c5fd;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-ledger-item button{{margin-top:5px;padding:3px 6px;}}'
      + '#repeatation-marker-panel .rm-status{{color:#93c5fd;margin:7px 0;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-status-inline{{align-self:center;color:#fed7aa;font-size:11px;}}'
      + '#repeatation-marker-panel .muted{{color:#94a3b8;margin:6px 0;}}'
      + '.hoverlayer .hovertext path{{fill-opacity:.38!important;stroke-opacity:.55!important;}}'
      + '.hoverlayer .hovertext text{{fill-opacity:.86!important;}}';
    document.head.appendChild(style);
    document.body.appendChild(panel);
    function setCollapsed(collapsed, persist) {{
      panel.classList.toggle('collapsed', collapsed);
      var toggle = panel.querySelector('#repeatation-toggle');
      toggle.textContent = collapsed ? 'Open' : 'Hide';
      toggle.setAttribute('title', collapsed ? 'Expand marker drawer' : 'Collapse marker drawer');
      if (persist !== false) saveDraft();
    }}
    function isPanelOrPlotlyControl(evt) {{
      var target = evt && evt.target;
      if (!target || !target.closest) return false;
      return !!target.closest('#repeatation-marker-panel,.modebar,.modebar-container,[data-title],button,a,input,select,textarea');
    }}
    function setDefaultPanMode() {{
      try {{
        Plotly.relayout(gd, {{ dragmode: 'pan' }});
      }} catch (err) {{}}
    }}
    panel.querySelector('#repeatation-toggle').addEventListener('click', function () {{
      setCollapsed(!panel.classList.contains('collapsed'));
    }});
    panel.querySelectorAll('[data-tool]').forEach(function (button) {{
      button.addEventListener('click', function () {{
        var tool = button.getAttribute('data-tool');
        setTool(state.tool === tool ? '' : tool);
      }});
    }});
    panel.querySelector('#repeatation-clear').addEventListener('click', clearMarkers);
    panel.querySelector('#repeatation-clear-draft').addEventListener('click', clearSavedDraft);
    panel.querySelector('#repeatation-auto-suggest').addEventListener('click', autoSuggestTrade);
    panel.querySelector('#repeatation-ignore-trade').addEventListener('click', markIgnoreTrade);
    panel.querySelector('#repeatation-add-ignore-signal').addEventListener('click', function () {{ addAnnotation('ignore_signal'); }});
    panel.querySelector('#repeatation-add-rule-note').addEventListener('click', function () {{ addAnnotation('rule_note'); }});
    panel.querySelector('#repeatation-clear-annotations').addEventListener('click', clearAnnotations);
    panel.querySelector('#repeatation-reset-cursor').addEventListener('click', resetCursorState);
    panel.querySelector('#repeatation-download').addEventListener('click', downloadMarkers);
    panel.querySelector('#repeatation-note').addEventListener('input', function () {{ render(); saveDraft(); }});
    panel.querySelector('#repeatation-note-type').addEventListener('input', function () {{ render(); saveDraft(); }});
    setOutcome(defaultOutcome());
    panel.querySelector('#repeatation-outcome').addEventListener('change', function () {{ state.outcomeTouched = true; drawMarkers(); render(); saveDraft(); }});
    panel.querySelector('#repeatation-rule-scope').addEventListener('change', saveDraft);
    panel.querySelector('#repeatation-rule-type').addEventListener('change', saveDraft);
    window.addEventListener('beforeunload', function () {{
      if (hasDraftableContent()) saveDraft();
    }});
    window.setInterval(function () {{
      if (hasDraftableContent()) saveDraft();
    }}, 2000);
    gd.addEventListener('mousedown', function (evt) {{
      if (isPanelOrPlotlyControl(evt)) return;
      var ref = nearestManualMarkerRef(evt, 20);
      if (ref) state.draggingMarkerKey = ref.key;
      else if (activeStateKey()) state.pendingMarkerClick = true;
      else return;
      state.suppressNextClick = true;
      evt.preventDefault();
      evt.stopImmediatePropagation();
    }}, true);
    window.addEventListener('mousemove', function (evt) {{
      if (!state.draggingMarkerKey) return;
      var point = pointFromMouseAt(evt, false);
      if (!point) return;
      setStatePoint(state.draggingMarkerKey, point);
      drawMarkers();
      render();
      evt.preventDefault();
    }}, true);
    window.addEventListener('mouseup', function (evt) {{
      if (!state.draggingMarkerKey && !state.pendingMarkerClick) return;
      if (state.draggingMarkerKey) {{
        state.draggingMarkerKey = '';
        saveDraft();
      }} else if (state.pendingMarkerClick) {{
        var point = pointFromMouse(evt);
        if (point) place(point);
      }}
      state.pendingMarkerClick = false;
      state.suppressNextClick = true;
      saveDraft();
      evt.preventDefault();
      evt.stopImmediatePropagation();
    }}, true);
    gd.addEventListener('click', function (evt) {{
      if (isPanelOrPlotlyControl(evt)) return;
      if (!state.suppressNextClick) return;
      state.suppressNextClick = false;
      evt.preventDefault();
      evt.stopImmediatePropagation();
    }}, true);
    if (!restoreDraft()) {{
      setTool('', false);
      render();
    }}
    setDefaultPanMode();
  }});
}}());
</script>
"""


def inject_marker_ui(html_path: Path, case: dict[str, Any]) -> None:
    if not html_path.exists():
        return
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    script = marker_ui_script(case)
    if "id=\"repeatation-marker-ui-script\"" in text:
        text = re.sub(
            r"\n?<script id=\"repeatation-marker-ui-script\">.*?</script>",
            lambda _match: "\n" + script,
            text,
            count=1,
            flags=re.DOTALL,
        )
        html_path.write_text(text, encoding="utf-8")
        return
    if "</body>" in text:
        text = text.replace("</body>", script + "\n</body>", 1)
    else:
        text += script
    html_path.write_text(text, encoding="utf-8")


def price_timeframe_for_case(case: dict[str, Any]) -> str:
    class Rowish:
        def __getitem__(self, key: str) -> Any:
            return case.get(key)

    suggested = suggested_price_timeframe(Rowish())
    start, end = case_bounds(case, context_hours=0.0)
    if price_covers(DEFAULT_PRICE_PATHS[suggested], start, end):
        return suggested
    if suggested != "h1" and price_covers(DEFAULT_PRICE_PATHS["h1"], start, end):
        return "h1"
    return suggested


def chart_price_path(args: argparse.Namespace, case_or_id: dict[str, Any] | int) -> Path:
    if Path(args.price) != DEFAULT_PRICE:
        return Path(args.price)
    case = case_or_id if isinstance(case_or_id, dict) else None
    if case is None:
        _, rows = read_case_group(args.db, int(case_or_id))
        case = next((row for row in rows if int(row["case_id"]) == int(case_or_id)), None)
    if not case:
        return DEFAULT_PRICE
    start, end = case_bounds(case, context_hours=float(args.case_context_hours))
    if price_covers(DEFAULT_PRICE, start, end):
        return DEFAULT_PRICE
    if price_covers(DEFAULT_PRICE_PATHS["h1"], start, end):
        return DEFAULT_PRICE_PATHS["h1"]
    return DEFAULT_PRICE


def case_bounds(case: dict[str, Any], context_hours: float) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = pd.Timestamp(str(case["window_start_ist"]))
    end = pd.Timestamp(str(case["window_end_ist"]))
    if start.tzinfo is None:
        start = start.tz_localize("Asia/Kolkata")
    else:
        start = start.tz_convert("Asia/Kolkata")
    if end.tzinfo is None:
        end = end.tz_localize("Asia/Kolkata")
    else:
        end = end.tz_convert("Asia/Kolkata")
    delta = pd.Timedelta(hours=float(context_hours or 0.0))
    return start - delta, end + delta


def price_coverage(path: Path) -> tuple[pd.Timestamp, pd.Timestamp] | None:
    path = Path(path)
    if path not in _PRICE_COVERAGE_CACHE:
        if not path.exists():
            _PRICE_COVERAGE_CACHE[path] = None
        else:
            price = pd.read_parquet(path, columns=[]).sort_index()
            if len(price.index) == 0:
                _PRICE_COVERAGE_CACHE[path] = None
            else:
                idx = price.index
                if idx.tz is None:
                    idx = idx.tz_localize("UTC")
                idx = idx.tz_convert("Asia/Kolkata")
                _PRICE_COVERAGE_CACHE[path] = (pd.Timestamp(idx.min()), pd.Timestamp(idx.max()))
    return _PRICE_COVERAGE_CACHE[path]


def price_covers(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> bool:
    coverage = price_coverage(path)
    if coverage is None:
        return False
    return coverage[0] <= start and coverage[1] >= end


def full_window_trade_stats(case: dict[str, Any]) -> dict[str, Any]:
    timeframe = price_timeframe_for_case(case)
    price = load_price_frame(DEFAULT_PRICE_PATHS[timeframe])
    bullish = calculate_trade_prices(
        price,
        trade_start_ist=str(case["window_start_ist"]),
        trade_end_ist=str(case["window_end_ist"]),
        outcome_label="bullish",
    )
    bearish = calculate_trade_prices(
        price,
        trade_start_ist=str(case["window_start_ist"]),
        trade_end_ist=str(case["window_end_ist"]),
        outcome_label="bearish",
    )
    return {
        "price_timeframe": timeframe,
        "full_window_entry_price": bullish["entry_price"],
        "full_window_exit_price": bullish["exit_price"],
        "full_window_bullish_pips": bullish["pips"],
        "full_window_bullish_mfe_pips": bullish["mfe_pips"],
        "full_window_bullish_mae_pips": bullish["mae_pips"],
        "full_window_bearish_pips": bearish["pips"],
        "full_window_bearish_mfe_pips": bearish["mfe_pips"],
        "full_window_bearish_mae_pips": bearish["mae_pips"],
        "full_window_direction": "bullish" if bullish["pips"] > 0 else "bearish" if bullish["pips"] < 0 else "flat",
    }


def annotation_command(case: dict[str, Any], outcome: str = "<bullish|bearish|sideways|unclear>") -> str:
    timeframe = price_timeframe_for_case(case)
    return (
        "python .\\aspect_annotation_store.py --add-trade-annotation "
        f"--case-id {int(case['case_id'])} "
        f"--trade-start {command_quote('<marker_start_ist>')} "
        f"--trade-end {command_quote('<marker_end_ist>')} "
        f"--outcome-label {outcome} "
        f"--price-timeframe {timeframe} "
        f"--why {command_quote('<why this marker placement>')}"
    )


def ignore_command(case: dict[str, Any]) -> str:
    return (
        "python .\\aspect_annotation_store.py --mark-ignore-region "
        f"--case-id {int(case['case_id'])} "
        f"--region-start {command_quote('<ignore_start_ist>')} "
        f"--region-end {command_quote('<ignore_end_ist>')} "
        f"--why {command_quote('<why ignored>')}"
    )


def rule_note_command(case: dict[str, Any]) -> str:
    return (
        "python .\\aspect_annotation_store.py --add-rule-note "
        f"--case-id {int(case['case_id'])} "
        "--note-type <note_type> "
        f"--note {command_quote('<rule note / ML learning note>')}"
    )


def attach_repeatation_navigation(cases: list[dict[str, Any]]) -> None:
    total = len(cases)
    for idx, case in enumerate(cases):
        prev_case = cases[idx - 1] if idx > 0 else None
        next_case = cases[idx + 1] if idx + 1 < total else None
        case["repeatation_index"] = idx + 1
        case["repeatation_count"] = total
        case["previous_chart_href"] = (
            html_cache_href(f"aspect_review_case_{int(prev_case['case_id'])}_chart.html") if prev_case else ""
        )
        case["next_chart_href"] = (
            html_cache_href(f"aspect_review_case_{int(next_case['case_id'])}_chart.html") if next_case else ""
        )
        case["reviewer_href"] = html_cache_href("repeatation_reviewer.html")


def render_trait_guide() -> str:
    rows = [
        ("Aspect distance from exact", "How far the setup is from perfect alignment. Example: value 51.36, low <= 45, high >= 75 means this one is in the middle zone. Smaller is usually cleaner."),
        ("direction linked", "This clue has repeatedly leaned one way in the same setup. Rule used here: average result is at least 8 pips away from the group average."),
        ("rare", "This clue appears only 1 or 2 times. Treat it as a possible exception, not a rule."),
        ("common", "This clue appears in most repeats. It is background context, not a special edge by itself."),
        ("only bullish samples", "Every repeat with this clue moved upward for the full window."),
        ("only bearish samples", "Every repeat with this clue moved downward for the full window."),
        ("x/y repeatations", "How many repeats in this same setup also have the same clue."),
        ("pips vs group", "Average result for repeats with this clue minus the family average. Negative leans bearish; positive leans bullish."),
        ("active regime count", "How many other event windows are active nearby. More overlap means it is harder to know which event moved price."),
        ("Basic planet strength", "Simple planet strength. Higher means the involved planets are in a more supportive position."),
        ("Aspect pressure strength", "Pressure from other planets. Negative leans stressful/downward; positive leans supportive/upward."),
        ("Multi-chart planet strength", "Planet strength checked across several chart divisions. Higher means stronger repeated support."),
        ("Timing strength", "Whether the event happens at a time that gives the planets more force. Higher means stronger timing support."),
        ("Motion strength", "Slow, stopped, or backward-moving planets can act more strongly in this rule."),
        ("Total planet strength", "Overall planet strength from all implemented parts. Higher means a stronger planet signal."),
        ("Strength vs minimum", "Overall strength divided by expected minimum. Above 1.00 means above minimum."),
        ("Base/quote pressure score", "In USDJPY, base means USD and quote means JPY. The script compares both sides."),
        ("touch planets", "Which planet lines price touched near this event."),
    ]
    row_html = "\n".join(
        f"<tr><td>{h(term)}</td><td>{h(desc)}</td></tr>"
        for term, desc in rows
    )
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>ML Trait Guide</title>
  <style>
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #0f172a; color: #e5e7eb; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 26px; }}
    h1 {{ margin: 0 0 8px; font-size: 24px; }}
    p {{ color: #cbd5e1; line-height: 1.55; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; margin-top: 18px; }}
    th, td {{ border: 1px solid #334155; padding: 10px; vertical-align: top; }}
    th {{ background: #1e293b; color: #bfdbfe; text-align: left; }}
    td:first-child {{ width: 260px; color: #fde68a; font-weight: 700; }}
    .note {{ border: 1px solid #334155; border-radius: 8px; padding: 12px; background: #020617; }}
  </style>
</head>
<body>
  <main>
    <h1>ML Trait Guide</h1>
    <p class="note">
      These hints compare the current repeat against other repeats of the same setup.
      They are pattern clues, not proof. Use them to decide what to inspect and what rule or exception note to write.
    </p>
    <table>
      <thead><tr><th>Term</th><th>Meaning</th></tr></thead>
      <tbody>{row_html}</tbody>
    </table>
  </main>
</body>
</html>
"""


def render_index(seed: dict[str, Any], rows: list[dict[str, Any]], output_dir: Path) -> str:
    table_rows = []
    for row in rows:
        chart_name = Path(str(row.get("chart_html", ""))).name
        visible_name = Path(str(row.get("chart_visible_csv", ""))).name
        table_rows.append(
            f"""
            <tr>
              <td>{h(row['case_id'])}</td>
              <td>{h(row['window_start_ist'])}<br>{h(row['window_end_ist'])}</td>
              <td>{h(row.get('timeframe'))}</td>
              <td>{h(row.get('visible_rows'))}</td>
              <td>{h(row.get('full_window_direction'))}</td>
              <td>{h(row.get('full_window_bullish_pips'))}</td>
              <td>{h(row.get('full_window_bearish_pips'))}</td>
              <td>{h(row.get('group_script_direction_mode'))}</td>
              <td>{h(row.get('probable_factor_tags'))}</td>
              <td>{h(row.get('special_trait_summary'))}</td>
              <td><a href="{h(html_cache_href(chart_name))}">chart</a><br><a href="{h(visible_name)}">visible csv</a></td>
              <td><pre>{h(row.get('trade_command'))}</pre></td>
              <td><pre>{h(row.get('ignore_command'))}</pre></td>
              <td><pre>{h(row.get('rule_note_command'))}</pre></td>
            </tr>
            """
        )
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Repeatation Review Pack - case {h(seed['case_id'])}</title>
  <style>
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 18px 24px; background: #111827; color: #f8fafc; }}
    main {{ padding: 20px 24px 36px; }}
    table {{ border-collapse: collapse; width: 100%; background: white; font-size: 12px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; vertical-align: top; }}
    th {{ background: #e5e7eb; position: sticky; top: 0; z-index: 1; }}
    pre {{ margin: 0; white-space: pre-wrap; max-width: 360px; font-size: 11px; }}
    .meta {{ display: flex; gap: 18px; flex-wrap: wrap; margin-top: 8px; color: #d1d5db; }}
    .note {{ max-width: 1100px; line-height: 1.45; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <header>
    <h1>Repeatation Review Pack</h1>
    <div>{h(seed['pair_key'])} :: {h(seed['aspect'])}</div>
    <div class="meta">
      <span>seed case_id={h(seed['case_id'])}</span>
      <span>repeatations={len(rows)}</span>
      <span>folder={h(output_dir)}</span>
    </div>
  </header>
  <main>
    <p class="note"><a href="{h(html_cache_href('repeatation_reviewer.html'))}"><b>Open single repeatation reviewer</b></a></p>
    <p class="note">
      Open each chart link and expand the small <b>Markers</b> drawer. Choose trade start,
      trade end, ignore start, or ignore end, then click the chart to place a crosshair marker at the
      selected time/price. Use <b>Ignore Trade</b> when a nearby/overlapping event contaminates the
      whole case window, then keep the Why note specific enough for ML/script review. Use
      <b>Add Ignore Signal</b> and <b>Add Rule Note</b> to build a structured ML annotation ledger
      from what you see on the chart; entries include scope, type, note, and marker context in the
      downloaded JSON. Use <b>Reset Cursor</b> if browser annotation mode leaves the page cursor
      visually stuck after disabling annotations. The chart overlays crosshair markers/ignore regions
      and generates Python commands for saving trade annotations, ignore regions, and rule notes. The annotation command
      auto-calculates entry, exit, pips, MFE, and MAE from the selected price timeframe. In-progress
      marker drafts autosave in the browser for each case and restore after reloads as long as local
      browser site data remains available.
    </p>
    <table>
      <thead>
        <tr>
          <th>Case</th><th>Window IST</th><th>TF</th><th>Visible Rows</th>
          <th>Full Window Direction</th><th>Bullish Pips</th><th>Bearish Pips</th>
          <th>Script Group Bias</th><th>Probable Factor Tags</th><th>Special Trait Hints</th><th>Snapshot</th>
          <th>Trade Marker Command</th><th>Ignore Marker Command</th><th>Rule Note Command</th>
        </tr>
      </thead>
      <tbody>
        {''.join(table_rows)}
      </tbody>
    </table>
  </main>
</body>
</html>
"""


def render_reviewer_shell(seed: dict[str, Any], rows: list[dict[str, Any]], output_dir: Path) -> str:
    first_chart = Path(str(rows[0].get("chart_html", ""))).name if rows else ""
    nav_rows = []
    for idx, row in enumerate(rows, start=1):
        chart_name = Path(str(row.get("chart_html", ""))).name
        direction = str(row.get("full_window_direction", "") or "")
        pips = row.get("full_window_bullish_pips", "")
        nav_rows.append(
            f"""
            <a class="case-link" href="{h(html_cache_href(chart_name))}" target="chartFrame">
              <span class="case-index">{idx}</span>
              <span>
                <b>case {h(row.get('case_id'))}</b>
                <small>{h(row.get('window_start_ist'))}</small>
                <small>{h(direction)} {h(pips)} pips</small>
              </span>
            </a>
            """
        )
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Repeatation Reviewer - case {h(seed['case_id'])}</title>
  <style>
    html, body {{ height: 100%; margin: 0; background: #0f172a; color: #e5e7eb; font-family: Segoe UI, Arial, sans-serif; }}
    body {{ display: grid; grid-template-columns: 280px 1fr; }}
    aside {{ border-right: 1px solid #334155; background: #111827; overflow: auto; }}
    header {{ padding: 14px 14px 10px; border-bottom: 1px solid #334155; }}
    h1 {{ font-size: 16px; margin: 0 0 6px; }}
    .meta {{ color: #cbd5e1; font-size: 12px; line-height: 1.45; }}
    .case-list {{ padding: 8px; display: grid; gap: 6px; }}
    .case-link {{ display: grid; grid-template-columns: 28px 1fr; gap: 8px; align-items: start; color: #e5e7eb; text-decoration: none; border: 1px solid #334155; border-radius: 6px; padding: 8px; background: #0f172a; }}
    .case-link:hover, .case-link:focus {{ border-color: #60a5fa; background: #172554; outline: none; }}
    .case-index {{ display: inline-flex; width: 24px; height: 24px; align-items: center; justify-content: center; border-radius: 999px; background: #1d4ed8; font-size: 12px; }}
    b {{ display: block; font-size: 13px; margin-bottom: 3px; }}
    small {{ display: block; color: #94a3b8; font-size: 11px; line-height: 1.35; }}
    main {{ min-width: 0; min-height: 0; }}
    iframe {{ width: 100%; height: 100%; border: 0; background: #0f172a; }}
  </style>
</head>
<body>
  <aside>
    <header>
      <h1>Repeatation Reviewer</h1>
      <div class="meta">
        seed case_id={h(seed['case_id'])}<br>
        {h(seed['pair_key'])} :: {h(seed['aspect'])}<br>
        repeatations={len(rows)}
      </div>
    </header>
    <nav class="case-list">
      {''.join(nav_rows)}
    </nav>
  </aside>
  <main>
    <iframe name="chartFrame" src="{h(html_cache_href(first_chart))}" title="Repeatation chart"></iframe>
  </main>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    seed, cases = read_case_group(args.db, args.case_id)
    attach_repeatation_navigation(cases)
    stamp = pd.Timestamp.now(tz="Asia/Kolkata").strftime("%Y%m%d_%H%M%S")
    group_slug = slugify(f"{seed['pair_key']}_{seed['aspect']}")
    output_dir = args.export_root / f"repeatation_review_case_{int(seed['case_id'])}_{group_slug}_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    focus_rows = load_focus_rows(args.review_focus)
    stats_by_case = {int(case["case_id"]): full_window_trade_stats(case) for case in cases}
    touch_rows_by_event = trait_row_for_events(args.touch_log, cases)
    special_traits_by_case = compute_special_traits(cases, stats_by_case, touch_rows_by_event)
    for case in cases:
        stats = stats_by_case[int(case["case_id"])]
        direction = str(stats.get("full_window_direction", "") or "").strip().lower()
        case["default_outcome"] = direction if direction in {"bullish", "bearish"} else "unclear"
        case["special_traits"] = special_traits_by_case.get(int(case["case_id"]), {})

    records: list[dict[str, Any]] = []
    for idx, case in enumerate(cases, start=1):
        print(f"[{idx}/{len(cases)}] exporting case_id={case['case_id']} {case['window_start_ist']}")
        html_path, csv_path, visible_rows = export_chart(args, case, output_dir)
        stats = stats_by_case[int(case["case_id"])]
        focus = focus_rows.get(int(case["case_id"]), {})
        export_case = {
            key: value
            for key, value in case.items()
            if key
            not in {
                "repeatation_index",
                "repeatation_count",
                "previous_chart_href",
                "next_chart_href",
                "reviewer_href",
                "special_traits",
            }
        }
        record = {
            **export_case,
            **stats,
            "visible_rows": visible_rows,
            "chart_html": str(html_path),
            "chart_visible_csv": str(csv_path),
            "trade_command": annotation_command(case),
            "ignore_command": ignore_command(case),
            "rule_note_command": rule_note_command(case),
            "same_aspect_group_key": focus.get("same_aspect_group_key", f"{seed['pair_key']} :: {seed['aspect']}"),
            "same_aspect_group_size": focus.get("same_aspect_group_size", len(cases)),
            "group_script_direction_mode": focus.get("group_script_direction_mode", ""),
            "group_fx_doctrine_directions": focus.get("group_fx_doctrine_directions", ""),
            "group_ml_outcomes": focus.get("group_ml_outcomes", ""),
            "probable_factor_tags": focus.get("probable_factor_tags", ""),
            "probable_factor_note": focus.get("probable_factor_note", ""),
            "special_trait_summary": "; ".join(
                f"{trait.get('label')} [{', '.join(trait.get('tags', []))}]"
                for trait in case.get("special_traits", {}).get("traits", [])[:4]
            ),
            "special_trait_json": json.dumps(case.get("special_traits", {}), ensure_ascii=False),
        }
        records.append(record)

    marker_template = output_dir / "repeatation_marker_template.csv"
    pd.DataFrame(records).to_csv(marker_template, index=False)
    index_path = output_dir / "repeatation_review_index.html"
    index_path.write_text(render_index(seed, records, output_dir), encoding="utf-8")
    reviewer_path = output_dir / "repeatation_reviewer.html"
    reviewer_path.write_text(render_reviewer_shell(seed, records, output_dir), encoding="utf-8")
    guide_path = output_dir / "trait_guide.html"
    guide_path.write_text(render_trait_guide(), encoding="utf-8")
    print(f"Wrote marker template: {marker_template}")
    print(f"Wrote index: {index_path}")
    print(f"Wrote reviewer: {reviewer_path}")
    print(f"Wrote trait guide: {guide_path}")
    print(f"repeatation_count={len(records)}")


if __name__ == "__main__":
    main()
