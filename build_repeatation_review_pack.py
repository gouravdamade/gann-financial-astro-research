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


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DB = PROJECT_ROOT / "gann_aspect_annotations.sqlite"
DEFAULT_TOUCH_LOG = PROJECT_ROOT / "aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv"
DEFAULT_PRICE = PROJECT_ROOT / "usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet"
DEFAULT_REVIEW_FOCUS = PROJECT_ROOT / "manual_case_review_focus_transitsign_20260516_0145.csv"
DEFAULT_EXPORT_ROOT = Path(r"D:\GannFinancialAstro\doc")
REPEATATION_UI_VERSION = "repeatation_ui_20260529_mixed_sr_verifier_v56"
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


def parse_rule_note_fields(note_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in str(note_text or "").split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        fields[key.strip().lower()] = value.strip()
    return fields


def load_case_family_rules(db_path: Path, seed: dict[str, Any]) -> list[dict[str, Any]]:
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                n.note_id,
                n.case_id AS seed_case_id,
                c.pair_key,
                c.aspect,
                n.note_type,
                n.note_text,
                n.created_at_utc
            FROM rule_notes n
            JOIN aspect_cases c ON c.case_id = n.case_id
            WHERE c.pair_key = ?
              AND c.aspect = ?
            ORDER BY n.created_at_utc, n.note_id
            """,
            (seed["pair_key"], seed["aspect"]),
        ).fetchall()
    rules: list[dict[str, Any]] = []
    for row in rows:
        note_text = str(row["note_text"] or "")
        fields = parse_rule_note_fields(note_text)
        scope = fields.get("scope", "")
        if "case_family" not in scope and not str(row["note_type"] or "").startswith("family_"):
            continue
        rules.append(
            {
                "note_id": int(row["note_id"]),
                "seed_case_id": int(row["seed_case_id"]),
                "family_key": f"{row['pair_key']}::{row['aspect']}",
                "pair_key": str(row["pair_key"]),
                "aspect": str(row["aspect"]),
                "note_type": str(row["note_type"] or ""),
                "scope": scope or "case_family",
                "status": fields.get("status", "provisional"),
                "rule_type": fields.get("type", str(row["note_type"] or "")),
                "label": fields.get("ml_label") or fields.get("label") or fields.get("rule_label") or "",
                "direction": fields.get("direction", ""),
                "note_text": note_text,
                "created_at_utc": str(row["created_at_utc"] or ""),
            }
        )
    return rules


def load_ml_notes(db_path: Path, seed: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                n.note_id,
                n.case_id AS seed_case_id,
                c.pair_key,
                c.aspect,
                n.note_type,
                n.note_text,
                n.created_at_utc
            FROM rule_notes n
            JOIN aspect_cases c ON c.case_id = n.case_id
            WHERE c.pair_key = ?
              AND c.aspect = ?
            ORDER BY n.created_at_utc, n.note_id
            """,
            (seed["pair_key"], seed["aspect"]),
        ).fetchall()
    notes_by_case: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        note_text = str(row["note_text"] or "")
        fields = parse_rule_note_fields(note_text)
        note_type = str(row["note_type"] or "")
        rule_type = fields.get("type", "")
        scope = fields.get("scope", "")
        label = fields.get("ml_label") or fields.get("label") or fields.get("rule_label") or note_type
        if "case_family" in scope or note_type.startswith("family_"):
            continue
        is_ml_note = (
            "ml" in note_type.lower()
            or rule_type.lower().startswith("ml")
            or "ml_label" in fields
            or "ml" in label.lower()
        )
        if not is_ml_note:
            continue
        note = {
            "note_id": int(row["note_id"]),
            "seed_case_id": int(row["seed_case_id"]),
            "family_key": f"{row['pair_key']}::{row['aspect']}",
            "pair_key": str(row["pair_key"]),
            "aspect": str(row["aspect"]),
            "note_type": note_type,
            "scope": fields.get("scope", ""),
            "status": fields.get("status", ""),
            "rule_type": rule_type,
            "label": label,
            "direction": fields.get("direction", ""),
            "note_text": note_text,
            "fields": fields,
            "created_at_utc": str(row["created_at_utc"] or ""),
        }
        notes_by_case.setdefault(int(row["seed_case_id"]), []).append({**note, "match_scope": "this case"})
    return notes_by_case


def load_rule_lessons(db_path: Path, seed: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    family_key = f"{seed['pair_key']}::{seed['aspect']}"
    try:
        with sqlite3.connect(str(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT lesson_id, case_id, family_key, lesson_key, conflict_type, old_rule,
                       new_rule, winner_rule, outcome_label, status, lesson_text,
                       astro_hints_json, created_at_utc, updated_at_utc
                FROM rule_lessons
                WHERE family_key = ?
                ORDER BY updated_at_utc DESC, lesson_id DESC
                """,
                (family_key,),
            ).fetchall()
    except sqlite3.OperationalError:
        return {}
    lessons_by_case: dict[int, list[dict[str, Any]]] = {}
    family_lessons: list[dict[str, Any]] = []
    for row in rows:
        try:
            astro_hints = json.loads(row["astro_hints_json"] or "[]")
        except Exception:
            astro_hints = []
        lesson = {
            "lesson_id": int(row["lesson_id"]),
            "case_id": int(row["case_id"]),
            "family_key": str(row["family_key"] or ""),
            "lesson_key": str(row["lesson_key"] or ""),
            "conflict_type": str(row["conflict_type"] or ""),
            "old_rule": str(row["old_rule"] or ""),
            "new_rule": str(row["new_rule"] or ""),
            "winner_rule": str(row["winner_rule"] or ""),
            "outcome_label": str(row["outcome_label"] or ""),
            "status": str(row["status"] or ""),
            "lesson_text": str(row["lesson_text"] or ""),
            "astro_hints": astro_hints,
            "created_at_utc": str(row["created_at_utc"] or ""),
            "updated_at_utc": str(row["updated_at_utc"] or ""),
        }
        lessons_by_case.setdefault(int(row["case_id"]), []).append({**lesson, "match_scope": "this case"})
        family_lessons.append({**lesson, "match_scope": "case family"})
    if family_lessons:
        lessons_by_case[0] = family_lessons
    for case_id in {int(seed["case_id"]), *lessons_by_case.keys()}:
        if case_id == 0:
            continue
        merged = list(lessons_by_case.get(case_id, []))
        seen = {int(item["lesson_id"]) for item in merged}
        for item in family_lessons[:12]:
            if int(item["lesson_id"]) in seen:
                continue
            merged.append(item)
            seen.add(int(item["lesson_id"]))
        if merged:
            lessons_by_case[case_id] = merged
    return lessons_by_case


def load_completed_reviews(db_path: Path, seed: dict[str, Any]) -> dict[int, dict[str, Any]]:
    family_key = f"{seed['pair_key']}::{seed['aspect']}"
    try:
        with sqlite3.connect(str(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT *
                FROM completed_reviews
                WHERE family_key = ?
                ORDER BY updated_at_utc DESC, review_id DESC
                """,
                (family_key,),
            ).fetchall()
    except sqlite3.OperationalError:
        return {}
    out: dict[int, dict[str, Any]] = {}
    json_fields = {
        "auto_suggestion_json": "auto_suggestion",
        "marker_ml_note_json": "marker_ml_note",
        "rule_impact_json": "rule_impact",
    }
    for row in rows:
        item = {key: row[key] for key in row.keys()}
        for source_key, target_key in json_fields.items():
            raw = item.pop(source_key, "")
            try:
                item[target_key] = json.loads(raw or "{}")
            except Exception:
                item[target_key] = {}
        try:
            out[int(row["case_id"])] = item
        except Exception:
            continue
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
        "fullWindowEntryPrice": case.get("full_window_entry_price", ""),
        "fullWindowExitPrice": case.get("full_window_exit_price", ""),
        "repeatationIndex": int(case.get("repeatation_index", 1)),
        "repeatationCount": int(case.get("repeatation_count", 1)),
        "previousHref": str(case.get("previous_chart_href", "")),
        "nextHref": str(case.get("next_chart_href", "")),
        "reviewerHref": str(case.get("reviewer_href", "repeatation_reviewer.html")),
        "traitGuideHref": html_cache_href("trait_guide.html"),
        "uiVersion": REPEATATION_UI_VERSION,
        "specialTraits": case.get("special_traits", {}),
        "appliedFamilyRules": case.get("applied_family_rules", []),
        "mlNotes": case.get("ml_notes", []),
        "ruleLessons": case.get("rule_lessons", []),
        "completedReview": case.get("completed_review", None),
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
  function waitForPlotlyGraph(fn, attempt) {{
    attempt = attempt || 0;
    var gd = document.querySelector('.js-plotly-plot');
    var plotlyApi = window.Plotly;
    if (gd) {{
      if (!plotlyApi) {{
        plotlyApi = {{
          relayout: function () {{
            return Promise.resolve();
          }}
        }};
      }}
      fn(gd, plotlyApi);
      return;
    }}
    if (attempt < 120) {{
      window.setTimeout(function () {{ waitForPlotlyGraph(fn, attempt + 1); }}, 250);
      return;
    }}
    var fallbackGd = document.querySelector('.plotly-graph-div');
    if (fallbackGd) {{
      console.warn('Repeatation marker UI could not attach because Plotly was not ready.');
    }}
  }}
  ready(function () {{
    waitForPlotlyGraph(function (gd, plotlyApi) {{
    var Plotly = plotlyApi;
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
      mlDraft: null,
      dreamReview: null,
      lessonSave: null,
      reviewSave: null,
      replayImpact: null,
      completedReview: meta.completedReview || null,
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
      profit: '#a78bfa',
      gann: '#f59e0b',
      gannAnchor: '#f97316'
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
    function candidateAuditItem(role, status, point, reason) {{
      if (!point) return null;
      var price = Number(point.y);
      var extras = [];
      if (Number.isFinite(Number(point.sr_price))) extras.push('SR ' + Number(point.sr_price).toFixed(3));
      if (Number.isFinite(Number(point.touch_gap_pips))) extras.push('gap ' + Number(point.touch_gap_pips).toFixed(1) + ' pips');
      if (Number.isFinite(Number(point.touch_band_pips))) extras.push('band ' + Number(point.touch_band_pips).toFixed(1) + ' pips');
      if (point.touch_side) extras.push(String(point.touch_side).replace(/_/g, ' '));
      if (point.fan_ratio_label) extras.push('fan ' + point.fan_ratio_label);
      if (Number.isFinite(Number(point.gann_epsilon_pips))) extras.push('epsilon ' + Number(point.gann_epsilon_pips).toFixed(1) + ' pips');
      return {{
        role: role || '',
        status: status || '',
        x: point.x,
        y: Number.isFinite(price) ? Number(price.toFixed(3)) : point.y,
        source: point.source || '',
        label: point.markerLabel || point.traceName || '',
        reason: reason || '',
        extras: extras.join(' | ')
      }};
    }}
    function traceLooksLikeMarker(trace) {{
      var mode = String(trace && trace.mode || '').toLowerCase();
      var name = String(trace && trace.name || '').toLowerCase();
      return mode.indexOf('markers') !== -1 || name.indexOf('touch') !== -1 || name.indexOf('interaction') !== -1;
    }}
    function traceLooksLikeZone(trace) {{
      if (!trace || trace.visible === false || !trace.x || !trace.y) return false;
      var fill = String(trace.fill || '').toLowerCase();
      var name = String(trace.name || '').toLowerCase();
      var label = '';
      if (trace.customdata && trace.customdata.length) {{
        label = customDataLabel(arrayValue(trace.customdata, 0)).toLowerCase();
      }}
      return fill === 'toself'
        && (name.indexOf('window') !== -1
          || name.indexOf('zone') !== -1
          || label.indexOf('aspect_window') !== -1
          || label.indexOf('regime') !== -1);
    }}
    function traceLooksLikeAspectWindow(trace) {{
      if (!trace || trace.visible === false || !trace.x || !trace.y) return false;
      var fill = String(trace.fill || '').toLowerCase();
      if (fill !== 'toself') return false;
      var name = String(trace.name || '').toLowerCase();
      var label = '';
      if (trace.customdata && trace.customdata.length) {{
        label = customDataLabel(arrayValue(trace.customdata, 0)).toLowerCase();
      }}
      if (label.indexOf('regime') !== -1 || name.indexOf('regime') !== -1) return false;
      return label.indexOf('aspect_window') !== -1
        || name.indexOf('aspect') !== -1
        || name.indexOf('window') !== -1;
    }}
    function traceLooksLikeSrLine(trace) {{
      if (!trace || trace.visible === false || !trace.x || !trace.y) return false;
      var type = String(trace.type || '').toLowerCase();
      var mode = String(trace.mode || '').toLowerCase();
      var fill = String(trace.fill || '').toLowerCase();
      var name = String(trace.name || '').toLowerCase();
      if (type !== 'scatter' || mode.indexOf('lines') === -1 || fill) return false;
      if (name.indexOf('selected case') !== -1 || name.indexOf('gann') !== -1) return false;
      return Number(trace.x.length || 0) > 1;
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
      if (false && values && values.dtype && values.bdata && typeof atob === 'function') {{
        if (!values._repeatationDecoded) {{
          var bytes = Uint8Array.from(atob(values.bdata), function (ch) {{ return ch.charCodeAt(0); }});
          var view = new DataView(bytes.buffer);
          var dtype = String(values.dtype || '').toLowerCase();
          var decoded = [];
          if (dtype === 'f8' || dtype === 'float64') {{
            for (var i = 0; i + 8 <= bytes.length; i += 8) decoded.push(view.getFloat64(i, true));
          }} else if (dtype === 'f4' || dtype === 'float32') {{
            for (var j = 0; j + 4 <= bytes.length; j += 4) decoded.push(view.getFloat32(j, true));
          }} else if (dtype === 'i4' || dtype === 'int32') {{
            for (var k = 0; k + 4 <= bytes.length; k += 4) decoded.push(view.getInt32(k, true));
          }} else if (dtype === 'u4' || dtype === 'uint32') {{
            for (var m = 0; m + 4 <= bytes.length; m += 4) decoded.push(view.getUint32(m, true));
          }}
          values._repeatationDecoded = decoded;
        }}
        return values._repeatationDecoded[index];
      }}
      if (values && values.dtype && values.bdata) {{
        if (!values._repeatationDecoded) {{
          var alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
          var raw = String(values.bdata || '').replace(/=+$/, '');
          var bytesPlain = [];
          var bufferBits = 0;
          var bitCount = 0;
          for (var bi = 0; bi < raw.length; bi += 1) {{
            var val = alphabet.indexOf(raw[bi]);
            if (val < 0) continue;
            bufferBits = (bufferBits << 6) | val;
            bitCount += 6;
            if (bitCount >= 8) {{
              bitCount -= 8;
              bytesPlain.push((bufferBits >> bitCount) & 255);
            }}
          }}
          function readFloat64LE(offset) {{
            var b0 = bytesPlain[offset] || 0;
            var b1 = bytesPlain[offset + 1] || 0;
            var b2 = bytesPlain[offset + 2] || 0;
            var b3 = bytesPlain[offset + 3] || 0;
            var b4 = bytesPlain[offset + 4] || 0;
            var b5 = bytesPlain[offset + 5] || 0;
            var b6 = bytesPlain[offset + 6] || 0;
            var b7 = bytesPlain[offset + 7] || 0;
            var sign = (b7 & 128) ? -1 : 1;
            var exponent = ((b7 & 127) << 4) | (b6 >> 4);
            var fraction = (b6 & 15) * Math.pow(2, 48)
              + b5 * Math.pow(2, 40)
              + b4 * Math.pow(2, 32)
              + b3 * Math.pow(2, 24)
              + b2 * Math.pow(2, 16)
              + b1 * Math.pow(2, 8)
              + b0;
            if (exponent === 0) return sign * Math.pow(2, -1022) * (fraction / Math.pow(2, 52));
            if (exponent === 2047) return fraction ? NaN : sign * Infinity;
            return sign * Math.pow(2, exponent - 1023) * (1 + fraction / Math.pow(2, 52));
          }}
          var dtypePlain = String(values.dtype || '').toLowerCase();
          var decodedPlain = [];
          if (dtypePlain === 'f8' || dtypePlain === 'float64') {{
            for (var fi = 0; fi + 8 <= bytesPlain.length; fi += 8) decodedPlain.push(readFloat64LE(fi));
          }}
          values._repeatationDecoded = decodedPlain;
        }}
        return values._repeatationDecoded[index];
      }}
      if (typeof values.length === 'number') return values[index];
      return null;
    }}
    var parsedPlotlyTraces = null;
    function parseBracketedJson(text, startIndex) {{
      var depth = 0;
      var inString = false;
      var escaped = false;
      for (var i = startIndex; i < text.length; i += 1) {{
        var ch = text[i];
        if (inString) {{
          if (escaped) escaped = false;
          else if (ch === '\\\\') escaped = true;
          else if (ch === '"') inString = false;
          continue;
        }}
        if (ch === '"') inString = true;
        else if (ch === '[') depth += 1;
        else if (ch === ']') {{
          depth -= 1;
          if (depth === 0) return text.slice(startIndex, i + 1);
        }}
      }}
      return '';
    }}
    function parsePlotlyTracesFromHtml() {{
      if (parsedPlotlyTraces) return parsedPlotlyTraces;
      parsedPlotlyTraces = [];
      var scripts = Array.prototype.slice.call(document.scripts || []);
      for (var s = 0; s < scripts.length; s += 1) {{
        var text = scripts[s].textContent || '';
        var plotIndex = text.indexOf('Plotly.newPlot');
        if (plotIndex === -1) continue;
        var arrayStart = text.indexOf('[', plotIndex);
        if (arrayStart === -1) continue;
        var jsonText = parseBracketedJson(text, arrayStart);
        if (!jsonText) continue;
        try {{
          var traces = JSON.parse(jsonText);
          if (Array.isArray(traces) && traces.length) {{
            parsedPlotlyTraces = traces;
            return parsedPlotlyTraces;
          }}
        }} catch (err) {{}}
      }}
      return parsedPlotlyTraces;
    }}
    function chartTraces() {{
      var parsed = parsePlotlyTracesFromHtml();
      if (Array.isArray(parsed) && parsed.length) return parsed;
      if (gd && Array.isArray(gd._fullData) && gd._fullData.length) return gd._fullData;
      if (gd && Array.isArray(gd.data) && gd.data.length) return gd.data;
      return [];
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
      var traces = chartTraces();
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
    function collectCandles() {{
      var traces = chartTraces();
      var candles = [];
      traces.forEach(function (trace) {{
        if (String(trace && trace.type || '').toLowerCase() !== 'candlestick') return;
        var len = Number((trace.x && trace.x.length) || 0);
        for (var i = 0; i < len; i += 1) {{
          var x = arrayValue(trace.x, i);
          var t = Date.parse(x);
          var high = Number(arrayValue(trace.high, i));
          var low = Number(arrayValue(trace.low, i));
          var close = Number(arrayValue(trace.close, i));
          var open = Number(arrayValue(trace.open, i));
          if (!Number.isFinite(t) || !Number.isFinite(high) || !Number.isFinite(low) || !Number.isFinite(close)) continue;
          candles.push({{ x: x, t: t, open: open, high: high, low: low, close: close }});
        }}
      }});
      return candles.sort(function (a, b) {{ return a.t - b.t; }});
    }}
    function timeframeMinutes() {{
      return String(meta.priceTimeframe || '').toLowerCase() === 'h1' ? 60 : 30;
    }}
    function candleMs() {{
      return timeframeMinutes() * 60 * 1000;
    }}
    function candleAtOrAfter(candles, timeMs) {{
      if (!Array.isArray(candles) || !Number.isFinite(timeMs)) return null;
      var interval = candleMs();
      var nearest = candles.reduce(function (best, c) {{
          var dist = Math.abs(c.t - timeMs);
          return !best || dist < best.dist ? {{ candle: c, dist: dist }} : best;
        }}, null);
      return candles.find(function (c) {{ return c.t >= timeMs - interval * 0.25; }})
        || (nearest ? nearest.candle : null);
    }}
    function candlePricePointAt(timeMs, label, source) {{
      var candle = candleAtOrAfter(collectCandles(), timeMs);
      if (candle) {{
        return {{
          x: candle.x,
          y: Number.isFinite(Number(candle.open)) ? candle.open : candle.close,
          source: source || 'auto_market_boundary',
          markerLabel: label || 'market boundary at candle open'
        }};
      }}
      return {{
        x: new Date(timeMs).toISOString(),
        y: numericMeta('fullWindowEntryPrice'),
        source: source || 'auto_market_boundary',
        markerLabel: label || 'market boundary'
      }};
    }}
    function collectZoneBoundaries() {{
      var traces = chartTraces();
      var zones = [];
      var seen = {{}};
      traces.forEach(function (trace, curveNumber) {{
        if (!traceLooksLikeZone(trace)) return;
        var times = [];
        var len = Number(trace.x.length || 0);
        for (var i = 0; i < len; i += 1) {{
          var t = Date.parse(arrayValue(trace.x, i));
          if (Number.isFinite(t)) times.push(t);
        }}
        if (!times.length) return;
        var startTime = Math.min.apply(null, times);
        var endTime = Math.max.apply(null, times);
        if (!Number.isFinite(startTime) || !Number.isFinite(endTime) || startTime === endTime) return;
        var label = customDataLabel(arrayValue(trace.customdata, 0)) || String(trace.name || 'shaded zone');
        var id = Math.round(startTime / 60000) + ':' + Math.round(endTime / 60000) + ':' + label;
        if (seen[id]) return;
        seen[id] = true;
        var startPoint = candlePricePointAt(startTime, 'next shaded zone start: ' + label, 'auto_zone_boundary');
        startPoint.zoneStart = new Date(startTime).toISOString();
        startPoint.zoneEnd = new Date(endTime).toISOString();
        startPoint.traceName = trace.name || '';
        startPoint.curveNumber = curveNumber;
        startPoint.markerLabel = 'next shaded zone start: ' + label;
        zones.push(startPoint);
      }});
      return zones.sort(function (a, b) {{ return markerTime(a) - markerTime(b); }});
    }}
    function collectAspectWindows() {{
      var windows = [];
      var seen = {{}};
      chartTraces().forEach(function (trace, curveNumber) {{
        if (!traceLooksLikeAspectWindow(trace)) return;
        var times = [];
        var len = Number(trace.x.length || 0);
        for (var i = 0; i < len; i += 1) {{
          var t = Date.parse(arrayValue(trace.x, i));
          if (Number.isFinite(t)) times.push(t);
        }}
        if (!times.length) return;
        var startTime = Math.min.apply(null, times);
        var endTime = Math.max.apply(null, times);
        if (!Number.isFinite(startTime) || !Number.isFinite(endTime) || startTime === endTime) return;
        var label = customDataLabel(arrayValue(trace.customdata, 0)) || String(trace.name || 'aspect window');
        var id = startTime + '|' + endTime + '|' + label;
        if (seen[id]) return;
        seen[id] = true;
        windows.push({{
          start: startTime,
          end: endTime,
          label: String(label || '').replace(/<[^>]*>/g, ' ').replace(/\\s+/g, ' ').trim().slice(0, 120),
          curveNumber: curveNumber
        }});
      }});
      return windows.sort(function (a, b) {{ return a.start - b.start; }});
    }}
    function multiAspectOverlapEvidence(candles, aspectWindows) {{
      var caseStart = Date.parse(meta.windowStart);
      var caseEnd = Date.parse(meta.windowEnd);
      var interval = candleMs();
      var evidence = {{
        active: false,
        definition: 'multiple aspect = at least one reviewed candle has two or more aspect windows overlapping it',
        min_required_aspects: 2,
        min_required_candles: 1,
        candle_minutes: timeframeMinutes(),
        qualifying_candle_count: 0,
        max_overlap_count: 0,
        first_qualifying_candle: null
      }};
      if (!Number.isFinite(caseStart) || !Number.isFinite(caseEnd)) return evidence;
      (candles || []).forEach(function (c) {{
        if (!c || !Number.isFinite(c.t)) return;
        var candleStart = c.t;
        var candleEnd = c.t + interval;
        if (candleEnd <= caseStart || candleStart >= caseEnd) return;
        var overlaps = (aspectWindows || []).filter(function (win) {{
          if (!win || !Number.isFinite(win.start) || !Number.isFinite(win.end)) return false;
          return win.start < candleEnd && win.end > candleStart;
        }});
        if (overlaps.length > evidence.max_overlap_count) evidence.max_overlap_count = overlaps.length;
        if (overlaps.length >= 2) {{
          evidence.qualifying_candle_count += 1;
          if (!evidence.first_qualifying_candle) {{
            evidence.first_qualifying_candle = {{
              x: c.x,
              overlap_count: overlaps.length,
              event_labels: overlaps.slice(0, 6).map(function (win) {{ return win.label; }})
            }};
          }}
        }}
      }});
      evidence.active = evidence.qualifying_candle_count >= 1;
      return evidence;
    }}
    function srLineValueAt(trace, timeMs) {{
      var len = Number((trace.x && trace.x.length) || 0);
      var bestIndex = -1;
      var bestDist = Infinity;
      for (var i = 0; i < len; i += 1) {{
        var t = Date.parse(arrayValue(trace.x, i));
        if (!Number.isFinite(t)) continue;
        var dist = Math.abs(t - timeMs);
        if (dist < bestDist) {{
          bestDist = dist;
          bestIndex = i;
        }}
      }}
      if (bestIndex < 0) return null;
      var y = Number(arrayValue(trace.y, bestIndex));
      return Number.isFinite(y) ? y : null;
    }}
    function collectSrLineTouches(referencePoint, selectedOutcome) {{
      var entryTime = markerTime(referencePoint);
      var entryPrice = Number(referencePoint && referencePoint.y);
      if (!Number.isFinite(entryTime) || !Number.isFinite(entryPrice)) return [];
      var direction = selectedOutcome || outcome();
      var traces = chartTraces();
      var candles = collectCandles();
      var clearancePips = srGeometryEpsilonPips(referencePoint);
      var touchPad = Math.max(clearancePips, 2) / 100;
      var start = Date.parse(meta.windowStart);
      var minTime = Number.isFinite(start) ? Math.max(entryTime, start) : entryTime;
      var out = [];
      traces.forEach(function (trace, curveNumber) {{
        if (!traceLooksLikeSrLine(trace)) return;
        var label = String(trace.name || 'SR line').replace(/\\s+/g, ' ').trim();
        var previousSide = null;
        for (var i = 0; i < candles.length; i += 1) {{
          var c = candles[i];
          if (!c || !Number.isFinite(c.t) || c.t < minTime) continue;
          var sr = srLineValueAt(trace, c.t);
          if (!Number.isFinite(sr)) continue;
          if (direction === 'bearish' && sr >= entryPrice - touchPad) continue;
          if (direction === 'bullish' && sr <= entryPrice + touchPad) continue;
          var side = c.close >= sr ? 1 : -1;
          var touched = c.low <= sr + touchPad && c.high >= sr - touchPad;
          var crossed = previousSide != null && side !== previousSide;
          previousSide = side;
          if (!touched && !crossed) continue;
          out.push({{
            x: c.x,
            y: sr,
            source: 'auto_sr_line_touch',
            traceName: trace.name || '',
            curveNumber: curveNumber,
            pointNumber: i,
            markerLabel: label + ' SR touch'
          }});
          break;
        }}
      }});
      return uniqueMarkers(out);
    }}
    function collectCaseWindowSrTouches() {{
      var traces = chartTraces();
      var candles = collectCandles();
      var start = Date.parse(meta.windowStart);
      var end = Date.parse(meta.windowEnd);
      if (!Number.isFinite(start) || !Number.isFinite(end)) return [];
      var referencePoint = caseEntryPoint('case window entry/open price');
      var clearancePips = srGeometryEpsilonPips(referencePoint);
      var touchBandPips = Math.max(clearancePips, 3);
      var touchPad = touchBandPips / 100;
      var out = [];
      traces.forEach(function (trace, curveNumber) {{
        if (!traceLooksLikeSrLine(trace)) return;
        var label = String(trace.name || 'SR line').replace(/\\s+/g, ' ').trim();
        candles.forEach(function (c, candleIndex) {{
          if (!c || !Number.isFinite(c.t) || c.t < start || c.t > end) return;
          var sr = srLineValueAt(trace, c.t);
          if (!Number.isFinite(sr)) return;
          var highGap = Math.abs(c.high - sr);
          var lowGap = Math.abs(c.low - sr);
          var closeGap = Math.abs(c.close - sr);
          var rangeGap = c.low <= sr && c.high >= sr ? 0 : Math.min(highGap, lowGap, closeGap);
          if (rangeGap > touchPad) return;
          var useTop = highGap <= lowGap;
          var y = useTop ? c.high : c.low;
          if (!Number.isFinite(y)) y = sr;
          out.push({{
            x: c.x,
            y: Number(y.toFixed(3)),
            sr_price: Number(sr.toFixed(6)),
            source: 'auto_selected_case_sr_touch',
            traceName: trace.name || '',
            curveNumber: curveNumber,
            pointNumber: candleIndex,
            markerLabel: label + ' selected-case SR touch',
            touch_gap_pips: Number((rangeGap * 100).toFixed(2)),
            touch_band_pips: Number(touchBandPips.toFixed(1)),
            touch_side: useTop ? 'top_wick' : 'bottom_wick',
            gann_anchor_side: useTop ? 'top' : 'bottom'
          }});
        }});
      }});
      return uniqueMarkers(out).sort(function (a, b) {{
        var dt = markerTime(a) - markerTime(b);
        if (dt !== 0) return dt;
        return Number(a.touch_gap_pips || 0) - Number(b.touch_gap_pips || 0);
      }});
    }}
    function gannFanForStart(startPoint, selectedOutcome, reason) {{
      var direction = selectedOutcome || outcome();
      var outcomeDirectionSign = direction === 'bearish' ? -1 : (direction === 'bullish' ? 1 : 0);
      if (!startPoint || !Number.isFinite(outcomeDirectionSign) || outcomeDirectionSign === 0) return null;
      var startTime = markerTime(startPoint);
      if (!Number.isFinite(startTime)) return null;
      var candles = collectCandles();
      var candle = candleAtOrAfter(candles, startTime);
      if (!candle) return null;
      var anchorSide = String(startPoint.gann_anchor_side || '').toLowerCase();
      var fanDirectionSign = anchorSide === 'top' ? -1 : (anchorSide === 'bottom' ? 1 : outcomeDirectionSign);
      var anchorPrice = anchorSide === 'top' ? candle.high : (anchorSide === 'bottom' ? candle.low : (fanDirectionSign < 0 ? candle.high : candle.low));
      if (!Number.isFinite(anchorPrice)) return null;
      return {{
        active: true,
        direction: direction,
        fan_direction: fanDirectionSign < 0 ? 'bearish' : 'bullish',
        direction_sign: fanDirectionSign,
        anchor: {{
          x: candle.x,
          y: Number(anchorPrice.toFixed(3)),
          source: anchorSide === 'top' ? 'gann_fan_top_wick' : (anchorSide === 'bottom' ? 'gann_fan_bottom_wick' : (fanDirectionSign < 0 ? 'gann_fan_top_wick' : 'gann_fan_bottom_wick')),
          markerLabel: anchorSide === 'top' ? 'Gann fan top wick anchor' : (anchorSide === 'bottom' ? 'Gann fan bottom wick anchor' : (fanDirectionSign < 0 ? 'Gann fan top wick anchor' : 'Gann fan bottom wick anchor'))
        }},
        anchor_candle: {{
          x: candle.x,
          open: Number(candle.open.toFixed(3)),
          high: Number(candle.high.toFixed(3)),
          low: Number(candle.low.toFixed(3)),
          close: Number(candle.close.toFixed(3))
        }},
        anchor_rule: fanDirectionSign < 0
          ? 'top wick anchor: bearish/downward fan projection'
          : 'bottom wick anchor: bullish/upward fan projection',
        timeframe_minutes: timeframeMinutes(),
        base_pips_per_candle: 1,
        ratios: [
          {{ label: '1x4', slope: 0.25 }},
          {{ label: '1x2', slope: 0.5 }},
          {{ label: '1x1', slope: 1 }},
          {{ label: '2x1', slope: 2 }},
          {{ label: '4x1', slope: 4 }}
        ],
        reason: reason || 'auto suggestion start marker'
      }};
    }}
    function gannFanLineValueAt(fan, ratioLabel, timeMs) {{
      if (!fan || !fan.anchor || !ratioLabel || !Number.isFinite(timeMs)) return null;
      var anchorTime = markerTime(fan.anchor);
      var anchorPrice = Number(fan.anchor.y);
      var directionSign = Number(fan.direction_sign || 0);
      if (!Number.isFinite(anchorTime) || !Number.isFinite(anchorPrice) || !directionSign || timeMs < anchorTime) return null;
      var ratio = (Array.isArray(fan.ratios) ? fan.ratios : []).find(function (item) {{
        return String(item.label || '') === String(ratioLabel);
      }});
      if (!ratio || !Number.isFinite(Number(ratio.slope))) return null;
      var elapsedCandles = (timeMs - anchorTime) / candleMs();
      return anchorPrice + directionSign * elapsedCandles * Number(fan.base_pips_per_candle || 1) * Number(ratio.slope) / 100;
    }}
    function secondFromBottomGannRatio(fan) {{
      if (!fan) return null;
      var directionSign = Number(fan.direction_sign || 0);
      if (directionSign < 0) {{
        return {{ label: '2x1', explanation: 'bearish/top-wick fan: 4x1 is lowest, 2x1 is second from bottom' }};
      }}
      if (directionSign > 0) {{
        return {{ label: '1x2', explanation: 'bullish/bottom-wick fan: 1x4 is lowest, 1x2 is second from bottom' }};
      }}
      return null;
    }}
    function gannFanSecondFromBottomTouch(fan, startPoint, multiAspectEvidence) {{
      if (!multiAspectEvidence || !multiAspectEvidence.active) return null;
      if (!fan || !fan.active || !fan.anchor) return null;
      var targetRatio = secondFromBottomGannRatio(fan);
      if (!targetRatio) return null;
      var startTime = markerTime(startPoint || fan.anchor);
      if (!Number.isFinite(startTime)) return null;
      var epsilonPips = 0.5;
      var epsilonPrice = epsilonPips / 100;
      var candles = collectCandles();
      var interval = candleMs();
      for (var i = 0; i < candles.length; i += 1) {{
        var c = candles[i];
        if (!c || !Number.isFinite(c.t) || c.t <= startTime + interval * 0.25) continue;
        var lineY = gannFanLineValueAt(fan, targetRatio.label, c.t);
        if (!Number.isFinite(lineY)) continue;
        var touched = c.low <= lineY + epsilonPrice && c.high >= lineY - epsilonPrice;
        if (!touched) continue;
        var closeGap = Math.abs(Number(c.close) - lineY);
        var highGap = Math.abs(Number(c.high) - lineY);
        var lowGap = Math.abs(Number(c.low) - lineY);
        var bestGap = Math.min(closeGap, highGap, lowGap);
        return {{
          x: c.x,
          y: Number(lineY.toFixed(3)),
          source: 'auto_gann_fan_second_from_bottom_touch',
          traceName: 'Gann fan',
          markerLabel: 'Gann fan 2nd-from-bottom touch (' + targetRatio.label + ')',
          fan_ratio_label: targetRatio.label,
          fan_line_rank: 'second_from_bottom',
          fan_rule_explanation: targetRatio.explanation,
          gann_epsilon_pips: epsilonPips,
          touch_gap_pips: Number((bestGap * 100).toFixed(2)),
          multi_aspect_gate: true
        }};
      }}
      return null;
    }}
    function refreshGannFanFromTradeStart(reason) {{
      if (!state.autoSuggestion || !state.tradeStart) return;
      state.autoSuggestion.gann_fan = gannFanForStart(state.tradeStart, outcome(), reason);
    }}
    function showGannFan() {{
      if (!state.autoSuggestion || !state.tradeStart) {{
        autoSuggestTrade();
        return;
      }}
      refreshGannFanFromTradeStart('manual gann fan refresh');
      drawMarkers();
      render();
      saveDraft();
      updateSaveStatus(state.autoSuggestion && state.autoSuggestion.gann_fan ? 'gann fan refreshed' : 'gann fan unavailable: check trade start/outcome');
    }}
    function atrPipsAt(candles, timeMs, period) {{
      var before = (candles || []).filter(function (c) {{ return Number.isFinite(c.t) && c.t <= timeMs; }});
      if (before.length < 2) return null;
      var trs = [];
      for (var i = 1; i < before.length; i += 1) {{
        var c = before[i];
        var prev = before[i - 1];
        var tr = Math.max(c.high - c.low, Math.abs(c.high - prev.close), Math.abs(c.low - prev.close));
        if (Number.isFinite(tr)) trs.push(tr * 100);
      }}
      var sample = trs.slice(-Math.max(1, period || 14));
      if (!sample.length) return null;
      return sample.reduce(function (sum, value) {{ return sum + value; }}, 0) / sample.length;
    }}
    function breakThresholdPips(candles, timeMs) {{
      var base = String(meta.priceTimeframe || '').toLowerCase() === 'h1' ? 8 : 5;
      var atr = atrPipsAt(candles, timeMs, 14);
      var threshold = Number.isFinite(atr) ? Math.max(base, 0.25 * atr) : base;
      return {{
        base_pips: base,
        atr14_pips: Number.isFinite(atr) ? Number(atr.toFixed(1)) : null,
        threshold_pips: Number(threshold.toFixed(1)),
        method: 'max(' + base + ' pips, 0.25 * ATR14)'
      }};
    }}
    function srGeometryEpsilonPips(referencePoint) {{
      var timeMs = markerTime(referencePoint);
      var atr = Number.isFinite(timeMs) ? atrPipsAt(collectCandles(), timeMs, 14) : null;
      var epsilon = Number.isFinite(atr) ? Math.max(1.5, Math.min(5, 0.05 * atr)) : 1.5;
      return Number(epsilon.toFixed(1));
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
      copy.source = copy.source || 'chart_marker';
      copy.autoSuggested = true;
      copy.autoRole = role;
      return copy;
    }}
    function wickEntryPointForStart(startPoint, selectedOutcome, reason) {{
      var direction = selectedOutcome || outcome();
      var directionSign = direction === 'bearish' ? -1 : (direction === 'bullish' ? 1 : 0);
      var startTime = markerTime(startPoint);
      if (!startPoint || !Number.isFinite(directionSign) || directionSign === 0 || !Number.isFinite(startTime)) return null;
      var candle = candleAtOrAfter(collectCandles(), startTime);
      if (!candle) return null;
      var y = directionSign < 0 ? candle.high : candle.low;
      if (!Number.isFinite(y)) return null;
      return {{
        x: candle.x,
        y: Number(y.toFixed(3)),
        source: directionSign < 0 ? 'auto_wick_entry_top' : 'auto_wick_entry_bottom',
        traceName: startPoint.traceName || '',
        curveNumber: startPoint.curveNumber,
        pointNumber: startPoint.pointNumber,
        markerLabel: directionSign < 0
          ? 'wick entry: bearish top wick from selected-case marker candle'
          : 'wick entry: bullish bottom wick from selected-case marker candle',
        reference_marker: serialPoint(startPoint),
        reason: reason || 'selected-case marker is at SR; use candle wick as executable entry'
      }};
    }}
    function nearestChartMarker(plotX, plotY, thresholdPx) {{
      var xa = gd._fullLayout && gd._fullLayout.xaxis;
      var ya = gd._fullLayout && gd._fullLayout.yaxis;
      var traces = chartTraces();
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
    function appliedRule(label) {{
      var rules = Array.isArray(meta.appliedFamilyRules) ? meta.appliedFamilyRules : [];
      return rules.find(function (rule) {{
        return String(rule.label || '').toLowerCase() === String(label || '').toLowerCase();
      }}) || null;
    }}
    function numericMeta(name) {{
      var value = Number(meta[name]);
      return Number.isFinite(value) ? value : null;
    }}
    function caseEntryPoint(label) {{
      var price = numericMeta('fullWindowEntryPrice');
      if (price == null) return null;
      return {{
        x: meta.windowStart,
        y: price,
        source: 'auto_case_window_entry',
        markerLabel: label || 'case window entry/open price',
        placedAt: Date.now()
      }};
    }}
    function uniqueMarkers(points) {{
      var out = [];
      var seen = {{}};
      (points || []).forEach(function (point) {{
        if (!point) return;
        var id = markerIdentity(point);
        if (seen[id]) return;
        seen[id] = true;
        out.push(point);
      }});
      return out.sort(function (a, b) {{ return markerTime(a) - markerTime(b); }});
    }}
    function attributionBoundaryAfter(markers, afterTime, minGapMs) {{
      var windowEnd = Date.parse(meta.windowEnd);
      var minTime = Math.max(
        Number.isFinite(Number(afterTime)) ? Number(afterTime) : 0,
        Number.isFinite(windowEnd) ? windowEnd : 0
      ) + (minGapMs || 0);
      return uniqueMarkers(markers).find(function (point) {{
        var t = markerTime(point);
        if (!Number.isFinite(t) || t < minTime) return false;
        if (point.isSelectedCaseTouch) return false;
        if (point.source === 'auto_case_window_entry') return false;
        return true;
      }}) || null;
    }}
    function zoneBoundaryAfter(zones, afterTime, minGapMs) {{
      var windowStart = Date.parse(meta.windowStart);
      var windowEnd = Date.parse(meta.windowEnd);
      var minTime = (Number.isFinite(Number(afterTime)) ? Number(afterTime) : 0) + (minGapMs || 0);
      return (zones || []).find(function (point) {{
        var t = markerTime(point);
        if (!Number.isFinite(t) || t < minTime) return false;
        if (Number.isFinite(windowStart) && Number.isFinite(windowEnd) && t >= windowStart && t <= windowEnd) return false;
        return true;
      }}) || null;
    }}
    function earliestTimedPoint(points) {{
      return (points || []).filter(function (point) {{
        return point && Number.isFinite(markerTime(point));
      }}).sort(function (a, b) {{
        return markerTime(a) - markerTime(b);
      }})[0] || null;
    }}
    function sortPoints(a, b) {{
      if (!a || !b) return [a, b];
      return Date.parse(a.x) <= Date.parse(b.x) ? [a, b] : [b, a];
    }}
    function isChartMarkerPoint(point) {{
      return point && (point.source === 'chart_marker' || point.source === 'auto_sr_line_touch');
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
      if (key === 'tradeStart') refreshGannFanFromTradeStart(point.autoSuggested ? 'auto suggestion start marker' : 'manual trade start adjustment');
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
        sr_price: point.sr_price,
        touch_gap_pips: point.touch_gap_pips,
        touch_band_pips: point.touch_band_pips,
        touch_side: point.touch_side || '',
        gann_anchor_side: point.gann_anchor_side || '',
        fan_ratio_label: point.fan_ratio_label || '',
        fan_line_rank: point.fan_line_rank || '',
        fan_rule_explanation: point.fan_rule_explanation || '',
        gann_epsilon_pips: point.gann_epsilon_pips,
        multi_aspect_gate: !!point.multi_aspect_gate,
        isSelectedCaseTouch: !!point.isSelectedCaseTouch,
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
      function chartIsoFromMs(ms) {{
        if (!Number.isFinite(ms)) return '';
        var shifted = new Date(ms + 5.5 * 60 * 60 * 1000);
        return shifted.toISOString().replace('Z', '+05:30');
      }}
      function xAround(x, fraction) {{
        var range = axisRange('xaxis') || [meta.windowStart, meta.windowEnd];
        var start = Date.parse(range[0]);
        var end = Date.parse(range[1]);
        var center = Date.parse(x);
        if (!Number.isFinite(start) || !Number.isFinite(end) || !Number.isFinite(center) || start === end) return [x, x];
        var half = Math.abs(end - start) * (fraction || 0.006);
        return [chartIsoFromMs(center - half), chartIsoFromMs(center + half)];
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
      function gannFanEndTime(fan) {{
        var candles = collectCandles();
        var anchorTime = Date.parse(fan && fan.anchor && fan.anchor.x);
        var range = axisRange('xaxis') || [];
        var rangeEnd = Date.parse(range[1]);
        var candleEnd = candles.length ? candles[candles.length - 1].t : NaN;
        var endTime = Math.max(
          Number.isFinite(rangeEnd) ? rangeEnd : 0,
          Number.isFinite(candleEnd) ? candleEnd : 0,
          Number.isFinite(anchorTime) ? anchorTime + candleMs() * 24 : 0
        );
        if (!Number.isFinite(anchorTime) || endTime <= anchorTime) endTime = anchorTime + candleMs() * 24;
        return endTime;
      }}
      function drawGannFan() {{
        var fan = state.autoSuggestion && state.autoSuggestion.gann_fan;
        if (!fan || !fan.active || !fan.anchor) return;
        var anchorTime = Date.parse(fan.anchor.x);
        var anchorPrice = Number(fan.anchor.y);
        var directionSign = Number(fan.direction_sign || 0);
        var anchorSource = String((fan.anchor && fan.anchor.source) || '').toLowerCase();
        if (anchorSource.indexOf('top') !== -1) directionSign = -1;
        if (anchorSource.indexOf('bottom') !== -1) directionSign = 1;
        fan.direction_sign = directionSign;
        fan.fan_direction = directionSign < 0 ? 'bearish' : 'bullish';
        if (!Number.isFinite(anchorTime) || !Number.isFinite(anchorPrice) || !directionSign) return;
        var endTime = gannFanEndTime(fan);
        var elapsedCandles = (endTime - anchorTime) / candleMs();
        var basePips = Number(fan.base_pips_per_candle || 1);
        var ratios = Array.isArray(fan.ratios) ? fan.ratios : [];
        var anchorXs = xAround(fan.anchor.x, 0.0045);
        var anchorYs = yAround(anchorPrice, 0.013);
        var anchorDotXs = xAround(fan.anchor.x, 0.0024);
        var anchorDotYs = yAround(anchorPrice, 0.007);
        shapes.push({{
          type: 'circle',
          name: 'repeatation-marker-gann-anchor-ring',
          xref: 'x',
          yref: 'y',
          x0: anchorXs[0],
          x1: anchorXs[1],
          y0: anchorYs[0],
          y1: anchorYs[1],
          fillcolor: 'rgba(249,115,22,0.12)',
          line: {{ color: 'rgba(254,243,199,0.95)', width: 1.5 }},
          layer: 'above'
        }});
        shapes.push({{
          type: 'circle',
          name: 'repeatation-marker-gann-anchor-dot',
          xref: 'x',
          yref: 'y',
          x0: anchorDotXs[0],
          x1: anchorDotXs[1],
          y0: anchorDotYs[0],
          y1: anchorDotYs[1],
          fillcolor: 'rgba(249,115,22,0.96)',
          line: {{ color: 'rgba(15,23,42,0.95)', width: 0.8 }},
          layer: 'above'
        }});
        ratios.forEach(function (ratio) {{
          var slope = Number(ratio.slope);
          if (!Number.isFinite(slope)) return;
          var y1 = anchorPrice + directionSign * elapsedCandles * basePips * slope / 100;
          shapes.push({{
            type: 'line',
            name: 'repeatation-marker-gann-' + String(ratio.label || '').toLowerCase(),
            xref: 'x',
            yref: 'y',
            x0: fan.anchor.x,
            x1: chartIsoFromMs(endTime),
            y0: anchorPrice,
            y1: y1,
            line: {{
              color: ratio.label === '1x1' ? 'rgba(251,191,36,0.90)' : 'rgba(245,158,11,0.52)',
              width: ratio.label === '1x1' ? 1.6 : 1.05,
              dash: ratio.label === '1x1' ? 'solid' : 'dot'
            }},
            layer: 'above'
          }});
        }});
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
      drawGannFan();
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
      function markerLabel(point, label, color, bg, ax, ay, strong) {{
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
          arrowhead: strong ? 2 : 1,
          arrowsize: strong ? 1.15 : 0.8,
          arrowwidth: strong ? 2.4 : 1.2,
          arrowcolor: strong ? hexToRgba(color, 0.96) : 'rgba(248,250,252,0.72)',
          ax: ax,
          ay: ay,
          bgcolor: bg,
          bordercolor: color,
          borderwidth: strong ? 1.5 : 1,
          borderpad: strong ? 4 : 3,
          font: {{ color: '#f8fafc', size: strong ? 11 : 10 }},
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
      if (!panel.classList.contains('collapsed')) {{
        markerLabel(state.tradeStart, 'Start', MARKER_COLORS.tradeStart, 'rgba(8,47,73,0.42)', -118, -76, true);
        markerLabel(state.tradeEnd, 'End', MARKER_COLORS.tradeEnd, 'rgba(113,63,18,0.42)', 118, 54, true);
        markerLabel(state.ignoreStart, 'Ignore start', MARKER_COLORS.ignore, 'rgba(88,28,135,0.34)', -50, 36);
        markerLabel(state.ignoreEnd, 'Ignore end', MARKER_COLORS.ignore, 'rgba(88,28,135,0.34)', 50, 36);
      }}
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
    function autoOutcomeFromSuggestion(suggestion) {{
      if (!suggestion) return '';
      var fan = suggestion.gann_fan || {{}};
      var fanDirection = fan.fan_direction || suggestion.auto_outcome || '';
      if (suggestion.end_rule === 'gann_second_from_bottom_touch_multi_aspect'
        && ['bullish', 'bearish'].indexOf(fanDirection) !== -1) {{
        return fanDirection;
      }}
      return '';
    }}
    function setAutoOutcome(value, reason) {{
      if (['bullish', 'bearish'].indexOf(value) === -1) return;
      setOutcome(value);
      state.outcomeTouched = false;
      if (state.autoSuggestion) {{
        state.autoSuggestion.auto_outcome = value;
        state.autoSuggestion.auto_outcome_reason = reason || '';
      }}
    }}
    function signedPipsForPoints(start, end, selectedOutcome) {{
      if (!start || !end) return null;
      var entry = Number(start.y);
      var exit = Number(end.y);
      if (!Number.isFinite(entry) || !Number.isFinite(exit)) return null;
      var rawPips = (exit - entry) * 100;
      var direction = selectedOutcome || outcome();
      return direction === 'bearish' ? -rawPips : rawPips;
    }}
    function signedPipsText(value) {{
      return Number.isFinite(Number(value)) ? (Number(value) >= 0 ? '+' : '') + Number(value).toFixed(1) + ' pips' : '';
    }}
    function srGeometryForPoint(point, referencePoint, selectedOutcome) {{
      var ref = Number(referencePoint && referencePoint.y);
      var y = Number(point && point.y);
      if (!Number.isFinite(ref) || !Number.isFinite(y)) return null;
      var diffPips = (y - ref) * 100;
      var epsilonPips = srGeometryEpsilonPips(referencePoint);
      var position = Math.abs(diffPips) <= epsilonPips ? 'same_as_entry' : (diffPips < 0 ? 'below_entry' : 'above_entry');
      var direction = selectedOutcome || outcome();
      var role = 'neutral';
      if (position === 'below_entry') role = direction === 'bearish' ? 'support/target' : 'support/entry';
      if (position === 'above_entry') role = direction === 'bearish' ? 'resistance/entry' : 'resistance/target';
      if (position === 'same_as_entry') role = 'at SR / use marker flow';
      return {{
        position: position,
        role: role,
        reference_price: ref,
        sr_price: y,
        distance_pips: diffPips,
        epsilon_pips: epsilonPips,
        label: 'SR is ' + (position === 'below_entry' ? 'below entry' : (position === 'above_entry' ? 'above entry' : 'at entry within ' + epsilonPips + ' pips')) + ': ' + role
      }};
    }}
    function candleLabel(candle) {{
      return candle && candle.x ? toIST(candle.x) + ' close ' + Number(candle.close).toFixed(3) : '';
    }}
    function breakConfirmationForGeometry(geometry, srPoint, referencePoint, selectedOutcome) {{
      if (!geometry || !srPoint || !referencePoint) return null;
      var role = String(geometry.role || '');
      if (role.indexOf('target') === -1) {{
        return {{
          status: 'not_applicable',
          label: 'Break confirmation not needed for this SR role.',
          reason: 'This SR is being treated as an entry/rejection area, not a target barrier.'
        }};
      }}
      var direction = selectedOutcome || outcome();
      var sr = Number(srPoint.y);
      var startTime = markerTime(referencePoint);
      if (!Number.isFinite(sr) || !Number.isFinite(startTime)) return null;
      var candles = collectCandles();
      var threshold = breakThresholdPips(candles, startTime);
      var thresholdPrice = threshold.threshold_pips / 100;
      var after = candles.filter(function (c) {{ return c.t >= startTime; }});
      var breakCandle = null;
      var retestCandle = null;
      var continuationCandle = null;
      var continuationStep = Math.max(2, threshold.threshold_pips / 2) / 100;
      if (direction === 'bearish' && geometry.position === 'below_entry') {{
        var breakLine = sr - thresholdPrice;
        breakCandle = after.find(function (c) {{ return c.close <= breakLine; }}) || null;
        if (breakCandle) {{
          var afterBreak = after.filter(function (c) {{ return c.t > breakCandle.t; }});
          retestCandle = afterBreak.find(function (c) {{
            return c.high >= sr - thresholdPrice && c.close < sr;
          }}) || null;
          if (retestCandle) {{
            continuationCandle = afterBreak.find(function (c) {{
              return c.t > retestCandle.t && (c.close <= retestCandle.close - continuationStep || c.low < retestCandle.low);
            }}) || null;
          }}
        }}
        return {{
          status: breakCandle && retestCandle && continuationCandle ? 'confirmed' : (breakCandle ? 'break_candidate' : 'not_confirmed'),
          label: breakCandle && retestCandle && continuationCandle
            ? 'Support break confirmed'
            : 'Support break not confirmed',
          threshold_pips: threshold.threshold_pips,
          base_pips: threshold.base_pips,
          atr14_pips: threshold.atr14_pips,
          method: threshold.method,
          sr_price: sr,
          break_line: Number(breakLine.toFixed(3)),
          break_candle: candleLabel(breakCandle),
          retest_candle: candleLabel(retestCandle),
          continuation_candle: candleLabel(continuationCandle),
          break_time: breakCandle ? breakCandle.x : '',
          retest_time: retestCandle ? retestCandle.x : '',
          continuation_time: continuationCandle ? continuationCandle.x : '',
          reason: breakCandle
            ? (retestCandle && continuationCandle
              ? 'Close broke below SR by threshold, then retest failed and price continued lower.'
              : 'Close broke below threshold, but retest/fail/continuation is not complete.')
            : 'No candle closed far enough below support. Wick/touch alone does not count.'
        }};
      }}
      if (direction === 'bullish' && geometry.position === 'above_entry') {{
        var breakLineUp = sr + thresholdPrice;
        breakCandle = after.find(function (c) {{ return c.close >= breakLineUp; }}) || null;
        if (breakCandle) {{
          var afterBreakUp = after.filter(function (c) {{ return c.t > breakCandle.t; }});
          retestCandle = afterBreakUp.find(function (c) {{
            return c.low <= sr + thresholdPrice && c.close > sr;
          }}) || null;
          if (retestCandle) {{
            continuationCandle = afterBreakUp.find(function (c) {{
              return c.t > retestCandle.t && (c.close >= retestCandle.close + continuationStep || c.high > retestCandle.high);
            }}) || null;
          }}
        }}
        return {{
          status: breakCandle && retestCandle && continuationCandle ? 'confirmed' : (breakCandle ? 'break_candidate' : 'not_confirmed'),
          label: breakCandle && retestCandle && continuationCandle
            ? 'Resistance break confirmed'
            : 'Resistance break not confirmed',
          threshold_pips: threshold.threshold_pips,
          base_pips: threshold.base_pips,
          atr14_pips: threshold.atr14_pips,
          method: threshold.method,
          sr_price: sr,
          break_line: Number(breakLineUp.toFixed(3)),
          break_candle: candleLabel(breakCandle),
          retest_candle: candleLabel(retestCandle),
          continuation_candle: candleLabel(continuationCandle),
          break_time: breakCandle ? breakCandle.x : '',
          retest_time: retestCandle ? retestCandle.x : '',
          continuation_time: continuationCandle ? continuationCandle.x : '',
          reason: breakCandle
            ? (retestCandle && continuationCandle
              ? 'Close broke above SR by threshold, then retest held and price continued higher.'
              : 'Close broke above threshold, but retest/hold/continuation is not complete.')
            : 'No candle closed far enough above resistance. Wick/touch alone does not count.'
        }};
      }}
      return {{
        status: 'not_applicable',
        label: 'Break confirmation not applicable',
        reason: 'Current direction and SR geometry do not form a target-barrier breakout check.'
      }};
    }}
    function tradeProfit() {{
      if (!state.tradeStart || !state.tradeEnd) return null;
      var entry = Number(state.tradeStart.y);
      var exit = Number(state.tradeEnd.y);
      if (!Number.isFinite(entry) || !Number.isFinite(exit)) return null;
      var rawPips = (exit - entry) * 100;
      var selected = outcome();
      var signedPips = signedPipsForPoints(state.tradeStart, state.tradeEnd, selected);
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
    function autoCandidateInspectorHtml(s) {{
      var items = Array.isArray(s && s.candidate_audit) ? s.candidate_audit.filter(Boolean) : [];
      if (!items.length) return '';
      var rows = items.slice(0, 18).map(function (item) {{
        var price = Number(item.y);
        var status = String(item.status || '');
        return '<tr class="rm-candidate-' + esc(status.replace(/[^a-z0-9_-]/gi, '').toLowerCase()) + '">'
          + '<td><b>' + esc(item.role || '') + '</b><div class="rm-table-sub">' + esc(status || '') + '</div></td>'
          + '<td>' + esc(toIST(item.x)) + (Number.isFinite(price) ? '<div class="rm-table-sub">@ ' + esc(price.toFixed(3)) + '</div>' : '') + '</td>'
          + '<td>' + esc(item.reason || '') + (item.extras ? '<div class="rm-table-sub">' + esc(item.extras) + '</div>' : '') + '</td>'
          + '</tr>';
      }}).join('');
      return '<details class="rm-candidates" open>'
        + '<summary>Auto Suggest candidates <span>' + esc(String(items.length)) + '</span></summary>'
        + '<table class="rm-candidate-table"><thead><tr><th>Role</th><th>Point</th><th>Why</th></tr></thead><tbody>'
        + rows
        + '</tbody></table>'
        + '<div class="rm-table-sub">This is the deterministic decision trail. It shows what the script chose and what it rejected.</div>'
        + '</details>';
    }}
    function autoSuggestionHtml() {{
      if (!state.autoSuggestion) return '<div class="rm-auto muted">Auto Suggest has not been run for this repeatation.</div>';
      var s = state.autoSuggestion;
      var geometry = s.sr_geometry
        ? '<div><b>SR geometry</b>: ' + esc(s.sr_geometry.label || '') + ' (' + esc(signedPipsText(s.sr_geometry.distance_pips)) + ' from entry)</div>'
        : '';
      if (s.sr_geometry_epsilon_pips) {{
        geometry += '<div class="rm-table-sub">At-SR band: within +/-' + esc(Number(s.sr_geometry_epsilon_pips).toFixed(1))
          + ' pips uses normal marker flow; outside that band can trigger support/resistance barrier logic.</div>';
      }}
      if (s.barrier_sr_geometry && s.sr_geometry && Math.abs(Number(s.barrier_sr_geometry.sr_price) - Number(s.sr_geometry.sr_price)) > 0.0001) {{
        geometry += '<div class="rm-table-sub">First barrier checked: '
          + esc(Number(s.barrier_sr_geometry.sr_price).toFixed(3))
          + ' (' + esc(signedPipsText(s.barrier_sr_geometry.distance_pips)) + ' from entry)</div>';
      }}
      if (s.attribution_boundary) {{
        geometry += '<div class="rm-table-sub">Attribution boundary stop: '
          + esc(toIST(s.attribution_boundary.x))
          + (Number.isFinite(Number(s.attribution_boundary.y)) ? ' @ ' + esc(Number(s.attribution_boundary.y).toFixed(3)) : '')
          + ' before next event/zone takes over.</div>';
      }}
      if (s.next_shaded_zone_boundary) {{
        geometry += '<div class="rm-table-sub">Next shaded zone boundary: '
          + esc(toIST(s.next_shaded_zone_boundary.x))
          + (Number.isFinite(Number(s.next_shaded_zone_boundary.y)) ? ' @ market open ' + esc(Number(s.next_shaded_zone_boundary.y).toFixed(3)) : '')
          + '.</div>';
      }}
      if (s.global_exit_boundary) {{
        geometry += '<div class="rm-table-sub">Global exit chosen: '
          + esc(toIST(s.global_exit_boundary.x))
          + (Number.isFinite(Number(s.global_exit_boundary.y)) ? ' @ ' + esc(Number(s.global_exit_boundary.y).toFixed(3)) : '')
          + ' from first SR touch / next shaded zone / next hardcoded marker, whichever appeared first.</div>';
      }}
      if (Array.isArray(s.sr_line_touch_candidates) && s.sr_line_touch_candidates.length) {{
        geometry += '<div class="rm-table-sub">SR line touches detected: '
          + esc(String(s.sr_line_touch_candidates.length))
          + ' candidate(s), including line touches that do not have a hardcoded dot.</div>';
      }}
      if (Array.isArray(s.case_window_sr_touch_candidates) && s.case_window_sr_touch_candidates.length) {{
        geometry += '<div class="rm-table-sub">Case-window SR touch candidates: '
          + esc(String(s.case_window_sr_touch_candidates.length))
          + ' candidate(s); first wick touch inside the tight SR band is preferred over a later confluence dot.</div>';
      }}
      var tracking = '';
      if (s.outcome_tracking) {{
        tracking = '<div><b>Rule tracking</b>: rule ' + esc(signedPipsText(s.outcome_tracking.rule_signed_pips))
          + ' vs old default ' + esc(signedPipsText(s.outcome_tracking.default_signed_pips))
          + ' | difference ' + esc(signedPipsText(s.outcome_tracking.delta_signed_pips)) + '</div>';
      }}
      var breakHtml = '';
      if (s.break_confirmation) {{
        var b = s.break_confirmation;
        var thresholdText = Number.isFinite(Number(b.threshold_pips))
          ? ' threshold ' + Number(b.threshold_pips).toFixed(1) + ' pips'
            + (Number.isFinite(Number(b.atr14_pips)) ? ' (ATR14 ' + Number(b.atr14_pips).toFixed(1) + ')' : '')
          : '';
        breakHtml = '<div><b>Break confirmation</b>: ' + esc(b.label || b.status || '')
          + esc(thresholdText)
          + (b.break_line ? ' | break close line ' + esc(Number(b.break_line).toFixed(3)) : '')
          + '</div><div class="rm-table-sub">' + esc(b.reason || '') + '</div>';
      }}
      var fanHtml = '';
      if (s.gann_fan && s.gann_fan.active) {{
        var fan = s.gann_fan;
        var source = String((fan.anchor && fan.anchor.source) || '').toLowerCase();
        var wick = source.indexOf('top') !== -1 ? 'top wick' : (source.indexOf('bottom') !== -1 ? 'bottom wick' : (fan.direction === 'bearish' ? 'top wick' : 'bottom wick'));
        var projection = source.indexOf('top') !== -1 ? 'bearish' : (source.indexOf('bottom') !== -1 ? 'bullish' : (fan.fan_direction || fan.direction || ''));
        fanHtml = '<div><b>Gann fan</b>: anchored at ' + esc(wick)
          + ' ' + esc(toIST(fan.anchor && fan.anchor.x))
          + ' @ ' + esc(Number(fan.anchor && fan.anchor.y).toFixed(3))
          + '; projection ' + esc(projection)
          + '</div><div class="rm-table-sub">Scale: 1x1 = '
          + esc(fan.base_pips_per_candle || 1)
          + ' pip per ' + esc(fan.timeframe_minutes || timeframeMinutes()) + ' minute candle; fan stays data-based during zoom/pan.</div>';
      }}
      return '<div class="rm-auto ' + esc(s.confidence || '') + '">'
        + '<div><b>Auto suggestion</b><span>' + esc(s.confidence || 'unknown') + '</span></div>'
        + '<div>' + esc(s.reason || '') + '</div>'
        + geometry
        + tracking
        + breakHtml
        + fanHtml
        + autoCandidateInspectorHtml(s)
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
    function appliedFamilyRulesHtml() {{
      var rules = Array.isArray(meta.appliedFamilyRules) ? meta.appliedFamilyRules : [];
      if (!rules.length) return '<div class="rm-rules muted">No applied family rules yet.</div>';
      var rows = rules.map(function (rule) {{
        var title = rule.label || rule.rule_type || rule.note_type || 'family rule';
        var note = rule.note_text || '';
        var shortNote = note.length > 360 ? note.slice(0, 357) + '...' : note;
        return '<div class="rm-rule-item">'
          + '<div><b>' + esc(title) + '</b><span>' + esc(rule.status || 'provisional') + '</span></div>'
          + '<div class="rm-table-sub">scope=' + esc(rule.scope || 'case_family') + ' | seed case=' + esc(rule.seed_case_id || '') + ' | family=' + esc(rule.family_key || '') + '</div>'
          + '<div>' + esc(shortNote) + '</div>'
          + '</div>';
      }}).join('');
      return '<div class="rm-rules"><div><b>Applied family rules</b><span>' + esc(rules.length) + '</span></div>' + rows + '</div>';
    }}
    function mlNotePrettyText(note) {{
      var fields = note && note.fields && typeof note.fields === 'object' ? note.fields : null;
      var text = String((note && note.note_text) || '').trim();
      var rows = [];
      if (fields) {{
        var preferred = [
          'learning',
          'trade_implication',
          'astro_reasons',
          'rule_note',
          'context',
          'trigger',
          'break_confirmation',
          'gann_fan',
          'label',
          'ml_label'
        ];
        var used = {{}};
        rows = preferred.filter(function (key) {{ return fields[key]; }}).map(function (key) {{
          used[key] = true;
          return '<li><b>' + esc(key.replace(/_/g, ' ')) + '</b>: ' + esc(fields[key]) + '</li>';
        }});
        Object.keys(fields).filter(function (key) {{
          return !used[key] && ['scope', 'status', 'type', 'rule_label', 'family', 'seed_case_id'].indexOf(key) < 0;
        }}).slice(0, 12).forEach(function (key) {{
          rows.push('<li><b>' + esc(key.replace(/_/g, ' ')) + '</b>: ' + esc(fields[key]) + '</li>');
        }});
      }}
      var fieldHtml = rows.length ? '<ul>' + rows.join('') + '</ul>' : '';
      if (!text) return fieldHtml || '<div class="muted">No note body saved.</div>';
      var bodyParts = text.split(/\\n\\s*\\n/).map(function (part) {{ return part.trim(); }}).filter(Boolean);
      var bodyText = bodyParts.length > 1 ? bodyParts.slice(1).join('\\n\\n') : text;
      return fieldHtml + '<div class="rm-ml-note-body">' + esc(bodyText) + '</div>';
    }}
    function currentMarkerMlNote() {{
      var result = tradeProfit();
      if (!result || !state.tradeStart || !state.tradeEnd) return null;
      var s = state.autoSuggestion || {{}};
      var startLabel = state.tradeStart.markerLabel || state.tradeStart.traceName || state.tradeStart.source || 'manual marker';
      var endLabel = state.tradeEnd.markerLabel || state.tradeEnd.traceName || state.tradeEnd.source || 'manual marker';
      var geometry = s.sr_geometry || s.default_marker_flow_sr_geometry || null;
      var breakInfo = s.break_confirmation || null;
      var hints = topAstroHintLabels();
      var source = state.autoSuggestion ? 'auto_suggest_or_adjusted_markers' : 'manual_markers';
      var lines = [
        'scope=current_marker_draft/local',
        'status=live_autosaved_not_db_committed',
        'type=marker_ml_note',
        'case_id=' + meta.caseId,
        'family=' + meta.pairKey + '::' + meta.aspect,
        'outcome=' + result.outcomeLabel,
        'signed_pips=' + result.signedPips.toFixed(1),
        'raw_pips=' + result.rawPips.toFixed(1),
        'trade_result=' + result.status,
        'entry=' + toIST(state.tradeStart.x) + ' @ ' + result.entry.toFixed(3),
        'exit=' + toIST(state.tradeEnd.x) + ' @ ' + result.exit.toFixed(3),
        'start_source=' + startLabel,
        'end_source=' + endLabel
      ];
      if (s.start_rule || s.end_rule) {{
        lines.push('auto_rules=' + String(s.start_rule || 'manual_start') + ' -> ' + String(s.end_rule || 'manual_end'));
      }}
      if (s.reason) lines.push('auto_reason=' + String(s.reason));
      if (geometry && geometry.label) {{
        lines.push('sr_geometry=' + geometry.label + ' | distance=' + signedPipsText(geometry.distance_pips));
      }}
      if (breakInfo && breakInfo.label) {{
        lines.push('break_confirmation=' + breakInfo.label + ' | ' + String(breakInfo.reason || ''));
      }}
      if (s.gann_fan_exit_rule_status) {{
        lines.push('gann_fan_exit_status=' + String(s.gann_fan_exit_rule_status));
      }}
      if (s.multi_aspect_overlap_evidence) {{
        lines.push('multi_aspect_gate=' + (s.multi_aspect_overlap_evidence.active ? 'active' : 'inactive'));
      }}
      if (s.outcome_tracking) lines.push('rule_vs_default=' + JSON.stringify(s.outcome_tracking));
      if (hints.length) lines.push('astro_hints=' + hints.join(' | '));
      if (noteText()) lines.push('reviewer_note=' + noteText());
      return {{
        note_id: 'live-marker',
        seed_case_id: meta.caseId,
        note_type: 'current_marker_ml_note',
        label: 'Current marker ML note',
        match_scope: source,
        status: 'live_autosaved_not_db_committed',
        fields: {{
          pips: result.signedPips.toFixed(1),
          outcome: result.outcomeLabel,
          trade_result: result.status,
          start_rule: s.start_rule || 'manual_start',
          end_rule: s.end_rule || 'manual_end',
          sr_geometry: geometry && geometry.label ? geometry.label : '',
          break_confirmation: breakInfo && breakInfo.label ? breakInfo.label : '',
          gann_fan_exit_status: s.gann_fan_exit_rule_status || ''
        }},
        note_text: lines.join('\\n'),
        created_at_utc: new Date().toISOString()
      }};
    }}
    function mlNotesHtml() {{
      var notes = Array.isArray(meta.mlNotes) ? meta.mlNotes : [];
      var liveNote = currentMarkerMlNote();
      var allNotes = liveNote ? [liveNote].concat(notes) : notes;
      if (!allNotes.length) return '<details class="rm-ml-notes"><summary>ML Notes <span>0</span></summary><div class="muted">Place trade start/end or run Auto Suggest to create a live marker ML note.</div></details>';
      var rows = allNotes.map(function (note) {{
        var title = note.label || note.note_type || 'ML note';
        var scope = note.match_scope || note.scope || 'saved note';
        return '<div class="rm-ml-note-item">'
          + '<div><b>' + esc(title) + '</b><span>' + esc(scope) + '</span></div>'
          + '<div class="rm-table-sub">note_id=' + esc(note.note_id || '') + ' | source case=' + esc(note.seed_case_id || '') + ' | type=' + esc(note.note_type || '') + '</div>'
          + mlNotePrettyText(note)
          + '</div>';
      }}).join('');
      return '<details class="rm-ml-notes" open><summary>ML Notes <span>' + esc(allNotes.length) + '</span></summary>'
        + '<div class="rm-table-sub">Live marker notes are draft evidence from current start/end, P/L, rule path, and chart evidence. Permanent official ML notes are created/edited only by Codex after Review Complete queues a task.</div>'
        + rows + '</details>';
    }}
    function topAstroHintLabels() {{
      var traits = meta.specialTraits && Array.isArray(meta.specialTraits.traits) ? meta.specialTraits.traits : [];
      return traits.slice(0, 8).map(function (trait) {{
        var tags = Array.isArray(trait.tags) && trait.tags.length ? ' [' + trait.tags.join(', ') + ']' : '';
        return String(trait.label || trait.key || '') + tags;
      }}).filter(Boolean);
    }}
    function currentLessonDraft() {{
      var s = state.autoSuggestion || null;
      if (!s) return null;
      var endRule = String(s.end_rule || '');
      var breakStatus = s.break_confirmation && s.break_confirmation.status;
      var conflictType = 'boundary_choice';
      var oldRule = 'default_marker_to_next_marker';
      var newRule = 'use_current_auto_suggestion_boundary_logic';
      if (endRule.indexOf('confirmed_break_next_') === 0) {{
        conflictType = 'sr_touch_exit_vs_confirmed_break_hold';
        oldRule = 'close_at_first_sr_touch';
        newRule = 'if first SR has confirmed break/retest/continuation, treat SR as passed barrier and exit at next context boundary';
      }} else if (endRule === 'global_first_sr_touch_target') {{
        conflictType = 'support_target_exit_without_confirmed_break_hold';
        oldRule = 'hold_to_next_aspect_or_shaded_zone';
        newRule = 'close at first SR touch when break confirmation is not sufficient';
      }} else if (endRule.indexOf('global_next_') === 0) {{
        conflictType = 'first_context_boundary_exit';
        oldRule = 'hold_to_later_sr_target';
        newRule = 'close at first context boundary before attribution changes';
      }}
      var hints = topAstroHintLabels();
      var parts = [
        'case_id=' + meta.caseId + ' family=' + meta.pairKey + '::' + meta.aspect,
        'conflict=' + conflictType,
        'old_rule=' + oldRule,
        'new_rule=' + newRule,
        'winner=' + (endRule || 'unknown'),
        'outcome=' + outcome(),
        'auto_reason=' + String(s.reason || ''),
        'break_status=' + String(breakStatus || ''),
        'sr_geometry=' + String((s.sr_geometry && s.sr_geometry.label) || ''),
        'rule_tracking=' + (s.outcome_tracking ? JSON.stringify(s.outcome_tracking) : 'n/a')
      ];
      if (hints.length) parts.push('astro_hints=' + hints.join(' | '));
      return {{
        case_id: meta.caseId,
        family_key: String(meta.pairKey || '') + '::' + String(meta.aspect || ''),
        lesson_key: conflictType + '|' + String(s.applied_family_rule || '') + '|' + endRule,
        conflict_type: conflictType,
        old_rule: oldRule,
        new_rule: newRule,
        winner_rule: endRule || 'unknown',
        outcome_label: outcome(),
        status: 'provisional',
        lesson_text: parts.join('\\n'),
        astro_hints: hints,
        auto_suggestion: s,
        verifier_report: verifyReasonText(),
        dream_review: state.dreamReview || null
      }};
    }}
    function ruleLessonsHtml() {{
      var saved = Array.isArray(meta.ruleLessons) ? meta.ruleLessons : [];
      var draft = currentLessonDraft();
      var rows = [];
      if (draft) {{
        rows.push('<div class="rm-lesson-draft"><div><b>Current lesson draft</b><span>' + esc(draft.conflict_type) + '</span></div><pre>' + esc(draft.lesson_text.slice(0, 1800)) + '</pre></div>');
      }} else {{
        rows.push('<div class="muted">Run Auto Suggest to draft a rule-conflict lesson.</div>');
      }}
      if (state.lessonSave) {{
        rows.push('<div class="' + (state.lessonSave.ok ? 'rm-verifier-pass' : 'rm-warning') + '">' + esc(state.lessonSave.message || state.lessonSave.error || '') + '</div>');
      }}
      saved.slice(0, 10).forEach(function (item) {{
        rows.push('<div class="rm-lesson-item">'
          + '<div><b>' + esc(item.conflict_type || item.lesson_key || 'lesson') + '</b><span>' + esc(item.match_scope || item.status || '') + '</span></div>'
          + '<div class="rm-table-sub">lesson_id=' + esc(item.lesson_id || '') + ' | case=' + esc(item.case_id || '') + ' | winner=' + esc(item.winner_rule || '') + '</div>'
          + '<div>' + esc(String(item.lesson_text || '').slice(0, 700)) + '</div>'
          + '</div>');
      }});
      return '<details class="rm-lessons" open><summary>Rule Conflict Lessons <span>' + esc(saved.length) + ' saved</span></summary>'
        + '<div class="rm-table-sub">Training ledger for rule conflicts: SR touch vs confirmed break, shaded-zone boundary, attribution boundary, and similar decisions.</div>'
        + rows.join('')
        + '</details>';
    }}
    function completeReviewPayload() {{
      var result = tradeProfit();
      if (!result || !state.tradeStart || !state.tradeEnd) return null;
      return {{
        case_id: meta.caseId,
        family_key: String(meta.pairKey || '') + '::' + String(meta.aspect || ''),
        pair_key: meta.pairKey,
        aspect: meta.aspect,
        price_timeframe: meta.priceTimeframe,
        outcome_label: outcome(),
        trade_start: serialPoint(state.tradeStart),
        trade_end: serialPoint(state.tradeEnd),
        trade_start_ist: state.tradeStart ? toIST(state.tradeStart.x) : '',
        trade_end_ist: state.tradeEnd ? toIST(state.tradeEnd.x) : '',
        trade_profit: result,
        auto_suggestion: state.autoSuggestion || {{}},
        current_marker_ml_note: currentMarkerMlNote(),
        reviewer_note: noteText(),
        review_status: 'complete',
        rule_version: meta.uiVersion || ''
      }};
    }}
    function impactSummaryHtml(impact) {{
      if (!impact || typeof impact !== 'object') return '<div class="muted">No replay impact summary yet.</div>';
      var affected = Array.isArray(impact.affected_or_needs_replay) ? impact.affected_or_needs_replay : [];
      var rows = affected.slice(0, 12).map(function (item) {{
        var storedPips = item.stored_pips != null ? item.stored_pips : item.old_signed_pips;
        var replayedPips = item.replayed_pips != null ? item.replayed_pips : (item.new_signed_pips != null ? item.new_signed_pips : item.current_pips);
        var deltaPips = item.pips_delta != null ? item.pips_delta : item.delta_signed_pips;
        var oldStart = item.stored_start_rule || item.old_start_rule || '';
        var oldEnd = item.stored_end_rule || item.old_end_rule || '';
        var newStart = item.replayed_start_rule || item.current_start_rule || item.new_start_rule || '';
        var newEnd = item.replayed_end_rule || item.current_end_rule || item.new_end_rule || '';
        return '<div class="rm-review-impact-item">'
          + '<b>case ' + esc(item.case_id || '') + '</b>'
          + '<div class="rm-table-sub">stored ' + esc(storedPips != null ? storedPips : '') + ' pips'
          + (replayedPips != null ? ' | replay ' + esc(replayedPips) + ' pips' : '')
          + (deltaPips != null ? ' | delta ' + esc(deltaPips) : '')
          + ' | ' + esc(item.reason || 'needs replay check') + '</div>'
          + '<div>old: ' + esc(oldStart + ' -> ' + oldEnd) + '</div>'
          + '<div>replay: ' + esc(newStart + ' -> ' + newEnd) + '</div>'
          + '</div>';
      }}).join('');
      return '<div class="rm-table-sub">' + esc(impact.message || '') + '</div>'
        + '<div class="rm-table-sub">mode=' + esc(impact.mode || 'rule_path')
        + ' | previous reviewed=' + esc(impact.previous_reviewed_count || impact.reviewed_count || 0)
        + ' | stable=' + esc(impact.same_rule_path_count || impact.unchanged_count || 0)
        + ' | affected=' + esc(impact.affected_count != null ? impact.affected_count : affected.length) + '</div>'
        + (impact.official_note_policy ? '<div class="rm-table-sub">' + esc(impact.official_note_policy) + '</div>' : '')
        + (impact.replay_error ? '<div class="rm-warning">Replay fallback: ' + esc(impact.replay_error) + '</div>' : '')
        + rows;
    }}
    function completedReviewHtml() {{
      var saved = state.completedReview || meta.completedReview || null;
      var result = tradeProfit();
      var status = state.reviewSave;
      var body = '';
      if (status) {{
        var taskIds = Array.isArray(status.codex_task_ids) ? status.codex_task_ids : [];
        body += '<div class="' + (status.ok ? 'rm-verifier-pass' : 'rm-warning') + '">'
          + esc(status.message || status.error || '')
          + (status.review_id ? ' #' + esc(status.review_id) : '')
          + '</div>';
        if (taskIds.length) {{
          body += '<div class="rm-table-sub">Codex official ML-note task queued: #' + esc(taskIds.join(', #')) + '</div>';
        }}
      }}
      if (saved) {{
        body += '<div><b>Completed review</b><span>' + esc(saved.review_status || 'complete') + '</span></div>'
          + '<div class="rm-table-sub">review_id=' + esc(saved.review_id || '') + ' | updated=' + esc(saved.updated_at_utc || '') + '</div>'
          + '<div>Saved P/L: <b>' + esc(saved.signed_pips != null ? Number(saved.signed_pips).toFixed(1) : '') + ' pips</b></div>'
          + '<div class="rm-table-sub">rules: ' + esc((saved.start_rule || '') + ' -> ' + (saved.end_rule || '')) + '</div>';
      }} else {{
        body += '<div><b>Review not completed</b><span>open</span></div>'
          + '<div class="rm-table-sub">Run Auto Suggest or place start/end, confirm P/L, then click Review Complete to write this recurrence into the training ledger.</div>';
      }}
      if (result) {{
        body += '<div class="rm-table-sub">current marker result: ' + esc(result.outcomeLabel) + ' ' + esc(result.signedPipsText) + ' pips</div>';
      }}
      body += '<div class="rm-table-sub">Official ML notes are Codex-owned: this page queues evidence; Codex reviews and writes/corrects the permanent note.</div>';
      var impact = (state.replayImpact || (saved && saved.rule_impact) || (status && status.impact_summary) || null);
      body += '<details class="rm-review-impact" open><summary>Replay impact</summary>' + impactSummaryHtml(impact) + '</details>';
      return '<div class="rm-review">' + body + '</div>';
    }}
    function mlDraftHtml() {{
      if (!state.mlDraft) return '<div class="rm-draft muted">No local draft generated yet.</div>';
      var title = state.mlDraft.ok ? 'Local Draft ML Reason' : 'Local Draft Failed';
      var body = state.mlDraft.markdown || state.mlDraft.error || '';
      return '<details class="rm-draft" open><summary>' + esc(title) + '</summary>'
        + '<div class="rm-table-sub">' + esc(state.mlDraft.path || '') + '</div>'
        + '<pre>' + esc(body.slice(0, 9000)) + '</pre>'
        + '</details>';
    }}
    function mlNotesPlainText() {{
      var notes = Array.isArray(meta.mlNotes) ? meta.mlNotes : [];
      var liveNote = currentMarkerMlNote();
      if (liveNote) notes = [liveNote].concat(notes);
      return notes.map(function (note) {{
        var fields = note && note.fields && typeof note.fields === 'object' ? JSON.stringify(note.fields) : '';
        return [
          note && note.label,
          note && note.note_type,
          note && note.note_text,
          fields
        ].filter(Boolean).join('\\n');
      }}).join('\\n\\n');
    }}
    function verifierEvidence() {{
      var result = tradeProfit();
      var s = state.autoSuggestion || {{}};
      var sr = s.sr_geometry || {{}};
      var barrier = s.barrier_sr_geometry || {{}};
      var breakInfo = s.break_confirmation || {{}};
      return {{
        outcome: outcome(),
        trade_result: result,
        auto_reason: s.reason || '',
        family_rule: s.applied_family_rule || '',
        sr_position: sr.position || '',
        sr_role: sr.role || '',
        sr_label: sr.label || '',
        sr_distance_pips: sr.distance_pips,
        barrier_position: barrier.position || '',
        barrier_role: barrier.role || '',
        barrier_label: barrier.label || '',
        mixed_sr_references: !!(sr.position && barrier.position && sr.position !== barrier.position),
        break_status: breakInfo.status || '',
        break_label: breakInfo.label || '',
        attribution_boundary: s.attribution_boundary || null,
        global_exit_boundary: s.global_exit_boundary || null,
        sr_touch_count: Array.isArray(s.sr_line_touch_candidates) ? s.sr_line_touch_candidates.length : 0
      }};
    }}
    function addVerifierIssue(list, severity, title, detail) {{
      list.push({{ severity: severity, title: title, detail: detail }});
    }}
    function hasAny(text, needles) {{
      return needles.some(function (needle) {{ return text.indexOf(needle) >= 0; }});
    }}
    function verifyReasonText() {{
      var draftText = String((state.mlDraft && (state.mlDraft.markdown || state.mlDraft.error)) || '');
      var notesText = mlNotesPlainText();
      var combined = (draftText + '\\n\\n' + notesText).toLowerCase();
      var draftLower = draftText.toLowerCase();
      var analysisLower = draftLower;
      var analysisStart = analysisLower.indexOf('## deterministic plain-english analysis');
      if (analysisStart >= 0) {{
        analysisLower = analysisLower.slice(analysisStart);
        var analysisEnd = analysisLower.indexOf('## local llm commentary');
        if (analysisEnd < 0) analysisEnd = analysisLower.indexOf('## deterministic case evidence');
        if (analysisEnd > 0) analysisLower = analysisLower.slice(0, analysisEnd);
      }}
      var evidence = verifierEvidence();
      var issues = [];
      var checks = [];
      if (!draftText.trim()) {{
        addVerifierIssue(issues, 'info', 'No draft to verify yet', 'Click Draft ML Reason after Auto Suggest. Stored ML notes are still checked for doctrine caveats.');
      }} else {{
        checks.push('Local draft text present');
      }}
      if (state.autoSuggestion) checks.push('Auto Suggest evidence available');
      else addVerifierIssue(issues, 'missing', 'Auto Suggest not available', 'Run Auto Suggest first so the verifier can check SR geometry, break confirmation, attribution boundary, and rule-vs-default evidence.');
      if (draftText && draftLower.indexOf('deterministic plain-english analysis') < 0) {{
        addVerifierIssue(issues, 'missing', 'Draft lacks deterministic section', 'The draft should include deterministic analysis before any local LLM commentary.');
      }}
      var expectedBearish = evidence.outcome === 'bearish' || /bearish/.test(String(evidence.family_rule + ' ' + evidence.auto_reason).toLowerCase());
      var expectedBullish = evidence.outcome === 'bullish' || /bullish/.test(String(evidence.family_rule + ' ' + evidence.auto_reason).toLowerCase());
      if (draftText && expectedBearish && hasAny(analysisLower, ['bullish bias', 'bullish case', 'upward bias', 'expected upward'])) {{
        addVerifierIssue(issues, 'contradiction', 'Direction conflict', 'Evidence says this review is bearish, but the draft uses bullish-bias language.');
      }}
      if (draftText && expectedBullish && hasAny(analysisLower, ['bearish bias', 'bearish case', 'downward bias', 'expected downward', 'probable reason this can be bearish'])) {{
        addVerifierIssue(issues, 'contradiction', 'Direction conflict', 'Evidence says this review is bullish, but the draft uses bearish-bias language.');
      }}
      if (evidence.trade_result && Number.isFinite(Number(evidence.trade_result.signedPips))) {{
        checks.push('Live P/L checked: ' + evidence.trade_result.signedPipsText + ' pips for ' + evidence.trade_result.outcomeLabel);
        if (Number(evidence.trade_result.signedPips) > 0 && hasAny(draftLower, ['adverse move', 'loss trade', 'negative p/l'])) {{
          addVerifierIssue(issues, 'contradiction', 'P/L conflict', 'Live trade result is favorable, but the draft describes it as adverse or losing.');
        }}
      }}
      if (evidence.sr_position === 'below_entry') {{
        checks.push('SR geometry checked: below entry means ' + (evidence.sr_role || 'support-side geometry'));
        if (hasAny(analysisLower, ['sr is above', 'resistance above', 'upper sr target', 'upper barrier'])
          && evidence.barrier_position !== 'above_entry'
          && !hasAny(analysisLower, ['not above', 'reference geometry', 'marker-flow', 'final sr geometry', 'final exit geometry'])) {{
          addVerifierIssue(issues, 'contradiction', 'SR geometry conflict', 'Auto Suggest says SR is below entry, but the draft talks as if the relevant SR is above/resistance.');
        }}
      }}
      if (evidence.sr_position === 'above_entry') {{
        checks.push('SR geometry checked: above entry means ' + (evidence.sr_role || 'resistance-side geometry'));
        if (hasAny(analysisLower, ['sr is below', 'support below', 'lower sr target', 'lower barrier'])
          && evidence.barrier_position !== 'below_entry'
          && !hasAny(analysisLower, ['not below', 'reference geometry', 'marker-flow', 'first barrier', 'barrier checked'])) {{
          addVerifierIssue(issues, 'contradiction', 'SR geometry conflict', 'Auto Suggest says SR is above entry, but the draft talks as if the relevant SR is below/support.');
        }}
      }}
      if (evidence.mixed_sr_references) {{
        checks.push('Mixed SR references checked: final geometry is ' + evidence.sr_label + '; first barrier/reference is ' + evidence.barrier_label);
      }}
      if (evidence.break_status === 'confirmed') {{
        checks.push('Break confirmation checked: confirmed');
        var noConfirmationPhrase = draftLower.indexOf('without break confirmation') >= 0;
        var cautionaryConfirmationRule = noConfirmationPhrase && (
          draftLower.indexOf('do not chase') >= 0 ||
          draftLower.indexOf('unless a candle closes') >= 0 ||
          draftLower.indexOf('require price/sr confirmation') >= 0
        );
        if (hasAny(draftLower, ['no clean break', 'did not break', 'failed to break']) || (noConfirmationPhrase && !cautionaryConfirmationRule)) {{
          addVerifierIssue(issues, 'contradiction', 'Break-confirmation conflict', 'Evidence says break/retest/continuation is confirmed, but the draft says the break failed or was missing.');
        }}
      }} else if (evidence.break_status && evidence.break_status !== 'not_applicable') {{
        checks.push('Break confirmation checked: ' + evidence.break_status);
        if (hasAny(draftLower, ['break confirmed', 'confirmed support break', 'confirmed resistance break'])) {{
          addVerifierIssue(issues, 'contradiction', 'Break-confirmation conflict', 'Evidence does not show a confirmed break, but the draft claims one.');
        }}
      }}
      if (evidence.attribution_boundary && draftText && !hasAny(draftLower, ['attribution boundary', 'next hardcoded marker', 'next event', 'new zone'])) {{
        addVerifierIssue(issues, 'missing', 'Missing attribution boundary', 'Auto Suggest stops at a later event/zone boundary, but the draft does not mention attribution control.');
      }}
      if (evidence.global_exit_boundary && draftText && !hasAny(draftLower, ['global exit', 'first sr touch', 'sr touch', 'next shaded zone', 'whichever appeared first'])) {{
        addVerifierIssue(issues, 'missing', 'Missing global-exit rule', 'Auto Suggest used the first boundary among SR touch, shaded zone, and hardcoded marker; the draft should say that.');
      }}
      if (evidence.sr_touch_count > 0) checks.push('SR-line touch candidates checked: ' + evidence.sr_touch_count);
      var syntheticAvg = String(meta.pairKey || '').toUpperCase().indexOf('AVG(ALL)') >= 0;
      var nonClassicalAspect = String(meta.aspect || '').toLowerCase().indexOf('square') >= 0;
      if ((syntheticAvg || nonClassicalAspect) && combined.indexOf('bphs-like orb strength') >= 0 && combined.indexOf('0.0') >= 0) {{
        addVerifierIssue(issues, 'caution', 'BPHS-like orb field is not proof', 'AVG(ALL) is synthetic and square is not a clean classical BPHS graha-drishti measure. Treat 0.0 as not-applicable/low-confidence, not as a real doctrinal zero.');
      }}
      if (draftText && hasAny(draftLower, ['economic indicators', 'investor sentiment', 'market conditions']) && !hasAny(draftLower, ['not in evidence', 'missing citation'])) {{
        addVerifierIssue(issues, 'unsupported', 'Generic market claim', 'The draft mentions macro/sentiment style reasons that are not present in this case evidence.');
      }}
      var contradictionCount = issues.filter(function (i) {{ return i.severity === 'contradiction'; }}).length;
      var seriousCount = issues.filter(function (i) {{ return i.severity === 'missing' || i.severity === 'unsupported'; }}).length;
      var cautionCount = issues.filter(function (i) {{ return i.severity === 'caution'; }}).length;
      var verdict = contradictionCount ? 'contradiction found' : (seriousCount || cautionCount ? 'partly verified' : 'verified');
      return {{
        verdict: verdict,
        issues: issues,
        checks: checks,
        evidence: evidence
      }};
    }}
    function mlVerifierHtml() {{
      var report = verifyReasonText();
      var issueRows = report.issues.length
        ? report.issues.map(function (item) {{
            return '<div class="rm-verifier-issue ' + esc(item.severity) + '"><b>' + esc(item.title) + '</b><span>' + esc(item.severity) + '</span><div>' + esc(item.detail) + '</div></div>';
          }}).join('')
        : '<div class="rm-verifier-pass">No contradictions found against current deterministic evidence.</div>';
      var checkRows = report.checks.length
        ? '<ul>' + report.checks.slice(0, 8).map(function (item) {{ return '<li>' + esc(item) + '</li>'; }}).join('') + '</ul>'
        : '<div class="muted">Run Auto Suggest and Draft ML Reason for stronger checks.</div>';
      return '<details class="rm-verifier" open><summary>Reason verifier <span>' + esc(report.verdict) + '</span></summary>'
        + '<div class="rm-table-sub">Rule-based truth gate for local draft and saved ML notes. It does not decide Jyotish doctrine; it catches evidence conflicts before ML training.</div>'
        + issueRows
        + '<div class="rm-verifier-checks"><b>Checks run</b>' + checkRows + '</div>'
        + '</details>';
    }}
    function dreamReviewHtml() {{
      if (!state.dreamReview) {{
        return '<div class="rm-dream muted">Dream review runs after Draft ML Reason.</div>';
      }}
      var status = state.dreamReview.status || (state.dreamReview.ok ? 'done' : 'failed');
      var title = state.dreamReview.ok === false ? 'Dream Review Failed' : 'Dream Review';
      var issueCount = Array.isArray(state.dreamReview.issues) ? state.dreamReview.issues.length : 0;
      var appliedCount = Array.isArray(state.dreamReview.applied) ? state.dreamReview.applied.length : 0;
      var reviewCount = Array.isArray(state.dreamReview.needs_review) ? state.dreamReview.needs_review.length : 0;
      var rows = [];
      if (state.dreamReview.message) rows.push('<div>' + esc(state.dreamReview.message) + '</div>');
      if (state.dreamReview.error) rows.push('<div class="rm-warning">' + esc(state.dreamReview.error) + '</div>');
      if (appliedCount) rows.push('<div><b>Auto-corrected:</b> ' + esc(appliedCount) + ' stale deterministic note(s).</div>');
      if (reviewCount) rows.push('<div><b>Queued:</b> ' + esc(reviewCount) + ' item(s) need Codex review-agent correction.</div>');
      if (state.dreamReview.codex_agent_result) {{
        var agent = state.dreamReview.codex_agent_result || {{}};
        var processed = Array.isArray(agent.processed) ? agent.processed : [];
        rows.push('<div><b>Codex review-agent:</b> processed ' + esc(agent.processed_count || processed.length || 0) + ' queued task(s) immediately.</div>');
        if (processed.length) {{
          rows.push('<ul>' + processed.slice(0, 6).map(function (item) {{
            return '<li>task ' + esc(item.task_id || '') + ': ' + esc(item.action || item.status || '') + '</li>';
          }}).join('') + '</ul>');
        }}
      }}
      if (state.dreamReview.codex_agent_error) rows.push('<div class="rm-warning">Codex review-agent error: ' + esc(state.dreamReview.codex_agent_error) + '</div>');
      if (state.dreamReview.report_path) rows.push('<div class="rm-table-sub">' + esc(state.dreamReview.report_path) + '</div>');
      return '<details class="rm-dream" open><summary>' + esc(title) + ' <span>' + esc(status) + ' | issues ' + esc(issueCount) + '</span></summary>'
        + '<div class="rm-table-sub">Triggered by Draft ML Reason. Applies only narrow deterministic corrections; ambiguous conflicts are queued for Codex review-agent correction.</div>'
        + (rows.length ? rows.join('') : '<div>Dream review completed.</div>')
        + '</details>';
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
    function draftQuestion() {{
      var result = tradeProfit();
      var pieces = [
        'Explain case ' + meta.caseId + ' ' + meta.pairKey + ' ' + meta.aspect + ' for ML review.',
        'Use deterministic case evidence as ground truth.',
        'Explain probable astro/trading reasons, SR geometry, rule status, and ML features to test.'
      ];
      if (state.autoSuggestion) pieces.push('Auto Suggest summary: ' + JSON.stringify(state.autoSuggestion));
      if (result) pieces.push('Current manual/auto trade result: ' + result.outcomeLabel + ' ' + result.signedPipsText + ' pips; entry=' + result.entry.toFixed(3) + '; exit=' + result.exit.toFixed(3));
      if (noteText()) pieces.push('Reviewer note: ' + noteText().slice(0, 900));
      return pieces.join('\\n');
    }}
    function draftMlReason() {{
      var button = panel.querySelector('#repeatation-draft-ml-reason');
      var status = panel.querySelector('#repeatation-draft-ml-status');
      button.disabled = true;
      status.textContent = 'drafting locally...';
      state.mlDraft = {{ ok: true, markdown: 'Drafting local ML reason for case ' + meta.caseId + '...' }};
      state.dreamReview = null;
      render();
      fetch('/api/draft_ml_reason', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ case_id: meta.caseId, question: draftQuestion() }})
      }})
        .then(function (res) {{ return res.json().then(function (data) {{ data.http_status = res.status; return data; }}); }})
        .then(function (data) {{
          state.mlDraft = data;
          status.textContent = data.ok ? 'local draft ready' : 'local draft failed';
          render();
          if (data.ok) runDreamReview();
        }})
        .catch(function (err) {{
          state.mlDraft = {{ ok: false, error: String(err && err.message ? err.message : err) }};
          status.textContent = 'local draft failed';
          render();
        }})
        .finally(function () {{
          button.disabled = false;
        }});
    }}
    function dreamReviewPayload() {{
      return {{
        case_id: meta.caseId,
        family: String(meta.pairKey || '') + '::' + String(meta.aspect || ''),
        pair_key: meta.pairKey,
        aspect: meta.aspect,
        window_start: meta.windowStart,
        window_end: meta.windowEnd,
        price_timeframe: meta.priceTimeframe,
        draft_path: state.mlDraft && state.mlDraft.path,
        draft_markdown: state.mlDraft && state.mlDraft.markdown,
        verifier_report: verifyReasonText(),
        auto_suggestion: state.autoSuggestion,
        trade_result: tradeProfit(),
        reviewer_note: noteText(),
        ml_notes: meta.mlNotes || []
      }};
    }}
    function runDreamReview() {{
      state.dreamReview = {{ ok: true, status: 'running', message: 'Dream review checking draft against deterministic evidence...' }};
      render();
      fetch('/api/dream_review', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(dreamReviewPayload())
      }})
        .then(function (res) {{ return res.json().then(function (data) {{ data.http_status = res.status; return data; }}); }})
        .then(function (data) {{
          state.dreamReview = data;
          render();
        }})
        .catch(function (err) {{
          state.dreamReview = {{ ok: false, status: 'failed', error: String(err && err.message ? err.message : err) }};
          render();
        }});
    }}
    function saveRuleLesson() {{
      var draft = currentLessonDraft();
      if (!draft) {{
        state.lessonSave = {{ ok: false, error: 'Run Auto Suggest before saving a rule lesson.' }};
        render();
        return;
      }}
      state.lessonSave = {{ ok: true, message: 'saving lesson...' }};
      render();
      fetch('/api/save_rule_lesson', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(draft)
      }})
        .then(function (res) {{ return res.json().then(function (data) {{ data.http_status = res.status; return data; }}); }})
        .then(function (data) {{
          state.lessonSave = data;
          if (data.ok) {{
            if (!Array.isArray(meta.ruleLessons)) meta.ruleLessons = [];
            var existing = meta.ruleLessons.find(function (item) {{ return String(item.lesson_id) === String(data.lesson_id); }});
            if (!existing) {{
              meta.ruleLessons.unshift({{
                lesson_id: data.lesson_id,
                case_id: draft.case_id,
                family_key: draft.family_key,
                lesson_key: draft.lesson_key,
                conflict_type: draft.conflict_type,
                old_rule: draft.old_rule,
                new_rule: draft.new_rule,
                winner_rule: draft.winner_rule,
                outcome_label: draft.outcome_label,
                status: draft.status,
                lesson_text: draft.lesson_text,
                astro_hints: draft.astro_hints,
                match_scope: 'this case'
              }});
            }}
            state.lessonSave.message = data.message + ' #' + data.lesson_id;
          }}
          render();
        }})
        .catch(function (err) {{
          state.lessonSave = {{ ok: false, error: String(err && err.message ? err.message : err) }};
          render();
        }});
    }}
    function completeReview() {{
      var payload = completeReviewPayload();
      if (!payload) {{
        state.reviewSave = {{ ok: false, error: 'Place trade start and trade end before completing review.' }};
        render();
        return;
      }}
      state.reviewSave = {{ ok: true, message: 'saving completed review...' }};
      render();
      fetch('/api/complete_review', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(payload)
      }})
        .then(function (res) {{ return res.json().then(function (data) {{ data.http_status = res.status; return data; }}); }})
        .then(function (data) {{
          state.reviewSave = data;
          if (data.ok) {{
            state.replayImpact = data.impact_summary || null;
            state.completedReview = {{
              review_id: data.review_id,
              case_id: meta.caseId,
              family_key: payload.family_key,
              pair_key: payload.pair_key,
              aspect: payload.aspect,
              price_timeframe: payload.price_timeframe,
              outcome_label: payload.outcome_label,
              trade_start_ist: payload.trade_start_ist,
              trade_end_ist: payload.trade_end_ist,
              entry_price: payload.trade_profit.entry,
              exit_price: payload.trade_profit.exit,
              signed_pips: payload.trade_profit.signedPips,
              raw_pips: payload.trade_profit.rawPips,
              review_status: payload.review_status,
              rule_version: payload.rule_version,
              start_rule: (payload.auto_suggestion || {{}}).start_rule || '',
              end_rule: (payload.auto_suggestion || {{}}).end_rule || '',
              auto_suggestion: payload.auto_suggestion,
              marker_ml_note: payload.current_marker_ml_note,
              rule_impact: data.impact_summary || null,
              codex_task_ids: data.codex_task_ids || [],
              reviewer_note: payload.reviewer_note,
              updated_at_utc: new Date().toISOString()
            }};
            meta.completedReview = state.completedReview;
            updateSaveStatus('completed review saved to DB');
          }}
          render();
          saveDraft();
        }})
        .catch(function (err) {{
          state.reviewSave = {{ ok: false, error: String(err && err.message ? err.message : err) }};
          render();
        }});
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
      panel.querySelector('#repeatation-applied-rules').innerHTML = appliedFamilyRulesHtml();
      panel.querySelector('#repeatation-ml-notes').innerHTML = mlNotesHtml();
      panel.querySelector('#repeatation-rule-lessons').innerHTML = ruleLessonsHtml();
      panel.querySelector('#repeatation-completed-review').innerHTML = completedReviewHtml();
      panel.querySelector('#repeatation-ml-verifier').innerHTML = mlVerifierHtml();
      panel.querySelector('#repeatation-dream-review').innerHTML = dreamReviewHtml();
      panel.querySelector('#repeatation-ml-draft').innerHTML = mlDraftHtml();
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
        current_marker_ml_note: currentMarkerMlNote(),
        review_save: state.reviewSave,
        replay_impact: state.replayImpact,
        completed_review: state.completedReview,
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
      state.reviewSave = draft.review_save || null;
      state.replayImpact = draft.replay_impact || null;
      state.completedReview = draft.completed_review || meta.completedReview || null;
      state.outcomeTouched = !!draft.outcome_touched;
      setIgnoreTypes(Array.isArray(draft.selected_ignore_types) ? draft.selected_ignore_types : [], false);
      state.annotations = Array.isArray(draft.ml_annotations) ? draft.ml_annotations : [];
      state.lastPoint = restorePoint(draft.last_point) || state.tradeStart || state.tradeEnd || state.ignoreStart || state.ignoreEnd;
      var restoredOutcome = draft.outcome_label || defaultOutcome();
      if (!state.outcomeTouched && Number(draft.version || 1) < 2 && restoredOutcome === 'bullish' && defaultOutcome() !== 'bullish') {{
        restoredOutcome = defaultOutcome();
      }}
      setOutcome(restoredOutcome);
      var restoredAutoOutcome = autoOutcomeFromSuggestion(state.autoSuggestion);
      if (restoredAutoOutcome) {{
        setAutoOutcome(restoredAutoOutcome, 'Restored Gann fan auto-suggested trade direction.');
      }}
      if (state.autoSuggestion && state.tradeStart && !state.autoSuggestion.gann_fan) refreshGannFanFromTradeStart('restored auto suggestion start marker');
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
      state.reviewSave = null;
      state.replayImpact = null;
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
      var zones = collectZoneBoundaries();
      var candles = collectCandles();
      var aspectWindows = collectAspectWindows();
      var multiAspectEvidence = multiAspectOverlapEvidence(candles, aspectWindows);
      var selected = markers.filter(function (point) {{ return point.isSelectedCaseTouch; }});
      var windowMarkers = markers.filter(pointInCaseWindow);
      var caseWindowSrTouches = collectCaseWindowSrTouches();
      var firstCaseWindowSrTouch = caseWindowSrTouches[0] || null;
      var defaultStart = firstCaseWindowSrTouch || selected[0] || windowMarkers[0] || markers[0];
      var defaultStartTime = markerTime(defaultStart);
      var minGapMs = 60000;
      var defaultEnd = markers.find(function (point) {{
        return markerTime(point) > defaultStartTime + minGapMs;
      }});
      var supportBarrierRule = appliedRule('bearish_bias_support_barrier');
      var entryPoint = caseEntryPoint('case window entry/open price');
      var defaultStartGeometry = srGeometryForPoint(defaultStart, entryPoint, outcome());
      var useDefaultMarkerFlow = defaultStartGeometry && defaultStartGeometry.position === 'same_as_entry';
      if (supportBarrierRule && outcome() === 'bearish' && entryPoint && !useDefaultMarkerFlow) {{
        var entryTime = markerTime(entryPoint);
        var entryPrice = Number(entryPoint.y);
        var clearancePips = srGeometryEpsilonPips(entryPoint);
        var clearancePrice = clearancePips / 100;
        var srLineTouches = collectSrLineTouches(entryPoint, outcome());
        var targetCandidates = uniqueMarkers(selected.concat(windowMarkers).concat(markers).concat(srLineTouches)).filter(function (point) {{
          var t = markerTime(point);
          var y = Number(point && point.y);
          return Number.isFinite(t)
            && Number.isFinite(y)
            && t >= entryTime
            && y < entryPrice - clearancePrice;
        }});
        var firstBarrier = targetCandidates[0] || null;
        var barrierGeometry = srGeometryForPoint(firstBarrier, entryPoint, outcome());
        var barrierBreakConfirmation = breakConfirmationForGeometry(barrierGeometry, firstBarrier, entryPoint, outcome());
        var zoneBoundary = zoneBoundaryAfter(zones, entryTime, minGapMs);
        var attributionBoundary = attributionBoundaryAfter(markers, entryTime, minGapMs);
        var barrierConfirmedBreak = barrierBreakConfirmation && barrierBreakConfirmation.status === 'confirmed';
        var target = barrierConfirmedBreak
          ? (earliestTimedPoint([zoneBoundary, attributionBoundary]) || firstBarrier)
          : earliestTimedPoint([firstBarrier, zoneBoundary, attributionBoundary]);
        var endRule = target ? 'global_first_boundary_after_entry' : 'not_found';
        if (barrierConfirmedBreak && target && zoneBoundary && markerIdentity(target) === markerIdentity(zoneBoundary)) {{
          endRule = 'confirmed_break_next_shaded_zone_boundary';
        }} else if (barrierConfirmedBreak && target && attributionBoundary && markerIdentity(target) === markerIdentity(attributionBoundary)) {{
          endRule = 'confirmed_break_next_hardcoded_marker_boundary';
        }} else if (target && firstBarrier && markerIdentity(target) === markerIdentity(firstBarrier)) {{
          endRule = 'global_first_sr_touch_target';
        }} else if (target && zoneBoundary && markerIdentity(target) === markerIdentity(zoneBoundary)) {{
          endRule = 'global_next_shaded_zone_boundary';
        }} else if (target && attributionBoundary && markerIdentity(target) === markerIdentity(attributionBoundary)) {{
          endRule = 'global_next_hardcoded_marker_boundary';
        }}
        var familyGannFan = gannFanForStart(entryPoint, outcome(), 'family rule case-window entry');
        var familyGannExit = gannFanSecondFromBottomTouch(familyGannFan, entryPoint, multiAspectEvidence);
        var gannExitUsed = false;
        if (familyGannExit && (!target || markerTime(familyGannExit) < markerTime(target))) {{
          target = familyGannExit;
          endRule = 'gann_second_from_bottom_touch_multi_aspect';
          gannExitUsed = true;
        }}
        var ruleConfidence = target ? (selected.indexOf(target) !== -1 ? 'rule clean' : 'rule fallback') : 'incomplete';
        var ruleReason = 'Applied family rule bearish_bias_support_barrier, but no lower hardcoded SR/marker was found after the case-window entry. Review manually.';
        if (target) {{
          if (endRule === 'gann_second_from_bottom_touch_multi_aspect') {{
            ruleReason = 'Applied provisional Gann fan exit because the multi-aspect gate passed: at least one reviewed candle had two or more aspect windows overlapping it. Close at the second-from-bottom fan-line touch before other boundaries.';
          }} else if (endRule === 'confirmed_break_next_shaded_zone_boundary') {{
            ruleReason = 'Applied family rule bearish_bias_support_barrier plus confirmed-break logic: first lower SR was broken/retested, so close at the next shaded-zone boundary before a new regime takes over.';
          }} else if (endRule === 'confirmed_break_next_hardcoded_marker_boundary') {{
            ruleReason = 'Applied family rule bearish_bias_support_barrier plus confirmed-break logic: first lower SR was broken/retested, so close at the next hardcoded marker before attribution changes.';
          }} else if (endRule === 'global_first_sr_touch_target') {{
            ruleReason = 'Applied family rule bearish_bias_support_barrier plus global exit rule: close at the first lower SR touch because SR is the first clean boundary after entry.';
          }} else if (endRule === 'global_next_shaded_zone_boundary') {{
            ruleReason = 'Applied family rule bearish_bias_support_barrier plus global exit rule: close at the first subsequent shaded zone boundary before entering a new event/regime context.';
          }} else if (endRule === 'global_next_hardcoded_marker_boundary') {{
            ruleReason = 'Applied family rule bearish_bias_support_barrier plus global exit rule: close at the first later hardcoded marker before entering uncharted attribution.';
          }} else {{
            ruleReason = 'Applied family rule bearish_bias_support_barrier plus global exit rule: close at whichever deterministic boundary comes first after entry: SR touch, next shaded zone, or next hardcoded marker.';
          }}
        }}
        var geometry = srGeometryForPoint(target, entryPoint, outcome());
        var breakConfirmation = barrierBreakConfirmation;
        var ruleSignedPips = signedPipsForPoints(entryPoint, target, outcome());
        var defaultSignedPips = signedPipsForPoints(defaultStart, defaultEnd, outcome());
        var tracking = (ruleSignedPips != null && defaultSignedPips != null) ? {{
          rule_signed_pips: Number(ruleSignedPips.toFixed(1)),
          default_signed_pips: Number(defaultSignedPips.toFixed(1)),
          delta_signed_pips: Number((ruleSignedPips - defaultSignedPips).toFixed(1)),
          default_start_rule: selected[0] ? 'first_selected_case_touch' : (windowMarkers[0] ? 'first_marker_inside_case_window' : 'first_visible_marker'),
          default_end_rule: defaultEnd ? 'next_later_hardcoded_marker' : 'not_found'
        }} : null;
        var ruleCandidateAudit = [
          candidateAuditItem('start', 'chosen', entryPoint, 'Family rule starts from the case-window entry/open price.'),
          candidateAuditItem('old default start', 'reference', defaultStart, 'Old marker-flow start used only for rule-vs-default tracking.'),
          candidateAuditItem('first SR target', target && firstBarrier && markerIdentity(target) === markerIdentity(firstBarrier) ? 'chosen' : 'checked', firstBarrier, barrierConfirmedBreak ? 'First lower SR was checked, but confirmed break logic can extend to the next attribution boundary.' : 'First lower SR is the clean target unless another earlier boundary appears.'),
          candidateAuditItem('next shaded zone', target && zoneBoundary && markerIdentity(target) === markerIdentity(zoneBoundary) ? 'chosen' : 'checked', zoneBoundary, 'Boundary where a later shaded regime/window starts; used to avoid entering new attribution territory.'),
          candidateAuditItem('next hardcoded marker', target && attributionBoundary && markerIdentity(target) === markerIdentity(attributionBoundary) ? 'chosen' : 'checked', attributionBoundary, 'Next chart marker after the case window; used when it appears before/at the next attribution change.'),
          candidateAuditItem('gann fan 2nd-from-bottom exit', gannExitUsed ? 'chosen' : (familyGannExit ? 'checked' : (multiAspectEvidence.active ? 'not found' : 'blocked')), familyGannExit || entryPoint, multiAspectEvidence.active ? 'Eligible because multiple-aspect gate passed: at least one candle has two or more aspect windows overlapping. Uses 2x1 for bearish/top-wick fans and 1x2 for bullish/bottom-wick fans.' : 'Blocked: no reviewed candle had two or more aspect windows overlapping.'),
          candidateAuditItem('old default end', 'reference', defaultEnd, 'Old marker-flow end used only for rule-vs-default tracking.')
        ].filter(Boolean);
        setTool('', false);
        state.autoSuggestion = {{
          active: !!target,
          confidence: ruleConfidence,
          reason: ruleReason,
          applied_family_rule: 'bearish_bias_support_barrier',
          barrier_sr_geometry: barrierGeometry,
          attribution_boundary: serialPoint(attributionBoundary),
          next_shaded_zone_boundary: serialPoint(zoneBoundary),
          global_exit_boundary: serialPoint(target),
          multi_aspect_overlap_evidence: multiAspectEvidence,
          gann_fan: familyGannFan,
          gann_fan_exit_candidate: serialPoint(familyGannExit),
          gann_fan_exit_rule_status: familyGannExit ? 'provisional_review_required' : (multiAspectEvidence.active ? 'eligible_but_no_touch_found' : 'blocked_no_multi_aspect_overlap'),
          sr_line_touch_candidates: srLineTouches.map(serialPoint),
          candidate_audit: ruleCandidateAudit,
          debug_counts: {{
            markers: markers.length,
            zones: zones.length,
            sr_line_touches: srLineTouches.length,
            target_candidates: targetCandidates.length
          }},
          sr_geometry: geometry,
          break_confirmation: breakConfirmation,
          sr_geometry_epsilon_pips: clearancePips,
          outcome_tracking: tracking,
          marker_count: markers.length,
          selected_case_marker_count: selected.length,
          start_rule: 'family_rule_case_window_entry_open_price',
          end_rule: target ? endRule : 'not_found',
          manual_override: false,
          overridden_keys: [],
          created_at: new Date().toISOString()
        }};
        setStatePoint('tradeStart', autoSuggestedPoint(entryPoint, 'auto_trade_start_family_rule'));
        if (target) setStatePoint('tradeEnd', autoSuggestedPoint(target, 'auto_trade_end_family_rule'));
        drawMarkers();
        render();
        saveDraft();
        updateSaveStatus(target ? 'auto suggested using applied family SR rule' : 'auto suggested entry only; no lower SR marker found');
        return;
      }}
      var start = defaultStart;
      var wickStart = null;
      var defaultFlowGeometry = srGeometryForPoint(defaultEnd, defaultStart, outcome());
      var defaultFlowAtSr = defaultFlowGeometry && defaultFlowGeometry.position === 'same_as_entry';
      if (!firstCaseWindowSrTouch && selected[0] && defaultFlowAtSr && (outcome() === 'bullish' || outcome() === 'bearish')) {{
        wickStart = wickEntryPointForStart(defaultStart, outcome(), 'selected-case marker is at SR / entry band');
        if (wickStart) start = wickStart;
      }}
      var startTime = markerTime(start);
      var end = defaultEnd;
      var confidence = firstCaseWindowSrTouch ? 'clean' : (selected[0] ? 'clean' : (windowMarkers[0] ? 'fallback' : 'weak'));
      var reason = firstCaseWindowSrTouch
        ? 'Start used the first actual SR-line wick touch inside the selected case window; end used the next later hardcoded marker/confluence boundary.'
        : (selected[0]
          ? 'Start used the first selected-case hardcoded touch; end used the next later hardcoded marker.'
          : (windowMarkers[0]
            ? 'No selected-case touch marker was found, so start used the first marker inside the case window; end used the next later marker.'
            : 'No marker inside the case window was found, so start used the first visible marker; review carefully.'));
      if (!end) {{
        confidence = 'incomplete';
        reason += ' No later marker was found for trade end.';
      }}
      if (wickStart) {{
        reason = 'Selected-case hardcoded marker is at the SR/entry band, so Auto Suggest used the candle wick as executable entry and kept the hardcoded marker as signal/reference. '
          + reason;
      }}
      var markerFlowGannFan = gannFanForStart(start, outcome(), 'marker-flow auto suggestion start');
      var markerFlowGannExit = gannFanSecondFromBottomTouch(markerFlowGannFan, start, multiAspectEvidence);
      var markerFlowGannExitUsed = false;
      var markerFlowOriginalEnd = end;
      var endRule = end ? 'next_later_hardcoded_marker' : 'not_found';
      if (markerFlowGannExit && (!end || markerTime(markerFlowGannExit) < markerTime(end))) {{
        end = markerFlowGannExit;
        endRule = 'gann_second_from_bottom_touch_multi_aspect';
        markerFlowGannExitUsed = true;
        confidence = confidence === 'incomplete' ? 'rule fallback' : confidence;
        reason = 'Provisional Gann fan exit won because the multi-aspect gate passed: at least one reviewed candle had two or more aspect windows overlapping it. '
          + reason;
      }}
      var effectiveOutcome = outcome();
      var autoOutcomeReason = '';
      if (markerFlowGannExitUsed && markerFlowGannFan && ['bullish', 'bearish'].indexOf(markerFlowGannFan.fan_direction) !== -1) {{
        effectiveOutcome = markerFlowGannFan.fan_direction;
        autoOutcomeReason = 'Gann fan exit controls trade direction: top-wick/down fan is bearish, bottom-wick/up fan is bullish.';
        setOutcome(effectiveOutcome);
        state.outcomeTouched = false;
      }}
      var markerCandidateAudit = [];
      if (firstCaseWindowSrTouch) {{
        markerCandidateAudit.push(candidateAuditItem('start', 'chosen', firstCaseWindowSrTouch, 'Earliest wick touch inside the selected case window and tight SR band.'));
        caseWindowSrTouches.slice(1, 6).forEach(function (point) {{
          markerCandidateAudit.push(candidateAuditItem('start', 'rejected', point, 'Later SR wick touch; earlier valid touch already won.'));
        }});
        if (selected[0]) markerCandidateAudit.push(candidateAuditItem('hardcoded confluence', 'reference', selected[0], 'Exported selected-case dot is later; kept as reference/end boundary, not start.'));
      }} else if (wickStart) {{
        markerCandidateAudit.push(candidateAuditItem('start', 'chosen', wickStart, 'Hardcoded marker sat at the SR/entry band, so the candle wick became executable entry.'));
        markerCandidateAudit.push(candidateAuditItem('hardcoded confluence', 'reference', defaultStart, 'Original hardcoded marker kept as signal/reference.'));
      }} else if (selected[0]) {{
        markerCandidateAudit.push(candidateAuditItem('start', 'chosen', selected[0], 'First exported selected-case hardcoded touch.'));
      }} else if (windowMarkers[0]) {{
        markerCandidateAudit.push(candidateAuditItem('start', 'chosen', windowMarkers[0], 'No selected-case dot; first marker inside the case window wins.'));
      }} else {{
        markerCandidateAudit.push(candidateAuditItem('start', 'chosen', markers[0], 'No in-window marker; first visible marker is a weak fallback.'));
      }}
      markerCandidateAudit.push(candidateAuditItem('end', end ? 'chosen' : 'missing', end, markerFlowGannExitUsed ? 'Provisional Gann fan second-from-bottom line touch won under the multiple-aspect gate.' : 'First later hardcoded marker after the chosen start.'));
      markerCandidateAudit.push(candidateAuditItem('gann fan 2nd-from-bottom exit', markerFlowGannExitUsed ? 'chosen' : (markerFlowGannExit ? 'checked' : (multiAspectEvidence.active ? 'not found' : 'blocked')), markerFlowGannExit || start, multiAspectEvidence.active ? 'Eligible because multiple-aspect gate passed: at least one candle has two or more aspect windows overlapping. Uses 2x1 for bearish/top-wick fans and 1x2 for bullish/bottom-wick fans.' : 'Blocked: no reviewed candle had two or more aspect windows overlapping.'));
      markerCandidateAudit.push(candidateAuditItem('old marker-flow end', 'reference', markerFlowOriginalEnd, 'Original next-later hardcoded marker before the provisional Gann fan exit check.'));
      setTool('', false);
      state.autoSuggestion = {{
        active: !!(start && end),
        confidence: confidence,
        reason: reason,
        marker_count: markers.length,
        selected_case_marker_count: selected.length,
        sr_geometry: srGeometryForPoint(end, start, effectiveOutcome),
        break_confirmation: breakConfirmationForGeometry(srGeometryForPoint(end, start, effectiveOutcome), end, start, effectiveOutcome),
        default_marker_flow_sr_geometry: defaultFlowGeometry,
        reference_start_marker: (wickStart || firstCaseWindowSrTouch) ? serialPoint(selected[0] || defaultStart) : null,
        case_window_sr_touch_candidates: caseWindowSrTouches.map(serialPoint),
        multi_aspect_overlap_evidence: multiAspectEvidence,
        gann_fan: markerFlowGannFan,
        gann_fan_exit_candidate: serialPoint(markerFlowGannExit),
        gann_fan_exit_rule_status: markerFlowGannExit ? 'provisional_review_required' : (multiAspectEvidence.active ? 'eligible_but_no_touch_found' : 'blocked_no_multi_aspect_overlap'),
        candidate_audit: markerCandidateAudit,
        start_rule: firstCaseWindowSrTouch ? 'first_case_window_sr_line_touch' : (wickStart ? 'wick_entry_from_selected_case_sr_marker' : (selected[0] ? 'first_selected_case_touch' : (windowMarkers[0] ? 'first_marker_inside_case_window' : 'first_visible_marker'))),
        end_rule: endRule,
        auto_outcome: effectiveOutcome,
        auto_outcome_reason: autoOutcomeReason,
        manual_override: false,
        overridden_keys: [],
        created_at: new Date().toISOString()
      }};
      if (autoOutcomeReason) setAutoOutcome(effectiveOutcome, autoOutcomeReason);
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
        current_marker_ml_note: currentMarkerMlNote(),
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
      + '<div class="rm-actions"><button id="repeatation-auto-suggest" type="button">Auto Suggest</button><button id="repeatation-show-gann" type="button">Show Gann Fan</button><span class="rm-status-inline">family rule if available; otherwise marker -> next marker</span></div>'
      + '<div id="repeatation-auto-summary"></div>'
      + '<div class="rm-actions"><button id="repeatation-ignore-trade" type="button">Ignore Trade</button><span id="repeatation-ignore-trade-status" class="rm-status-inline">Ignore Trade is off</span></div>'
      + '<div class="rm-grid"><span>Last click</span><b id="repeatation-last">not set</b><span>Trade start</span><b id="repeatation-trade-start">not set</b><span>Trade end</span><b id="repeatation-trade-end">not set</b><span>Ignore start</span><b id="repeatation-ignore-start">not set</b><span>Ignore end</span><b id="repeatation-ignore-end">not set</b></div>'
      + '<div id="repeatation-profit-summary"></div>'
      + '<div id="repeatation-applied-rules"></div>'
      + '<div id="repeatation-ml-notes"></div>'
      + '<div id="repeatation-rule-lessons"></div>'
      + '<div class="rm-actions"><button id="repeatation-save-rule-lesson" type="button">Save Rule Lesson</button><span class="rm-status-inline">logs current conflict for ML</span></div>'
      + '<div id="repeatation-completed-review"></div>'
      + '<div class="rm-actions"><button id="repeatation-complete-review" type="button">Review Complete</button><span class="rm-status-inline">locks this recurrence into training ledger</span></div>'
      + '<div class="rm-actions"><button id="repeatation-draft-ml-reason" type="button">Draft ML Reason</button><span id="repeatation-draft-ml-status" class="rm-status-inline">uses local Ollama/RAG if server is running</span></div>'
      + '<div id="repeatation-ml-verifier"></div>'
      + '<div id="repeatation-dream-review"></div>'
      + '<div id="repeatation-ml-draft"></div>'
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
      + '#repeatation-marker-panel .rm-candidates{{background:#07111f;border:1px solid #1e3a5f;border-radius:6px;padding:6px;margin:7px 0;color:#cbd5e1;}}'
      + '#repeatation-marker-panel .rm-candidates summary{{cursor:pointer;color:#bae6fd;font-weight:700;display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-candidates summary span{{color:#fde68a;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-candidate-table{{width:100%;border-collapse:collapse;font-size:10px;margin-top:5px;}}'
      + '#repeatation-marker-panel .rm-candidate-table th,#repeatation-marker-panel .rm-candidate-table td{{border:1px solid #1e293b;padding:4px;vertical-align:top;}}'
      + '#repeatation-marker-panel .rm-candidate-table th{{color:#bfdbfe;background:#0f172a;text-align:left;}}'
      + '#repeatation-marker-panel .rm-candidate-chosen td{{background:rgba(34,197,94,0.10);}}'
      + '#repeatation-marker-panel .rm-candidate-rejected td{{background:rgba(248,113,113,0.08);}}'
      + '#repeatation-marker-panel .rm-candidate-reference td,#repeatation-marker-panel .rm-candidate-checked td{{background:rgba(148,163,184,0.06);}}'
      + '#repeatation-marker-panel .rm-strength{{background:#07111f;border:1px solid #38bdf8;border-radius:6px;padding:7px;margin:6px 0;color:#cbd5e1;}}'
      + '#repeatation-marker-panel .rm-strength>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#bfdbfe;}}'
      + '#repeatation-marker-panel .rm-strength span{{color:#67e8f9;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-strength-item{{border-top:1px solid #1e3a5f;padding-top:5px;margin-top:5px;}}'
      + '#repeatation-marker-panel .rm-strength-item>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-rules{{background:#102016;border:1px solid #22c55e;border-radius:6px;padding:7px;margin:6px 0;color:#d1fae5;}}'
      + '#repeatation-marker-panel .rm-rules>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#bbf7d0;}}'
      + '#repeatation-marker-panel .rm-rules span{{color:#fde68a;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-rule-item{{border-top:1px solid #14532d;padding-top:5px;margin-top:5px;}}'
      + '#repeatation-marker-panel .rm-rule-item>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-ml-notes{{background:#111827;border:1px solid #a855f7;border-radius:6px;padding:7px;margin:6px 0;color:#ddd6fe;}}'
      + '#repeatation-marker-panel .rm-ml-notes summary{{cursor:pointer;color:#f5d0fe;font-weight:700;display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-ml-notes summary span{{color:#fde68a;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-ml-note-item{{border-top:1px solid #581c87;padding-top:5px;margin-top:5px;}}'
      + '#repeatation-marker-panel .rm-ml-note-item>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#f0abfc;}}'
      + '#repeatation-marker-panel .rm-ml-note-item span{{color:#fde68a;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-ml-note-item ul{{margin:5px 0 0 16px;padding:0;}}'
      + '#repeatation-marker-panel .rm-ml-note-item li{{margin:3px 0;}}'
      + '#repeatation-marker-panel .rm-ml-note-body{{white-space:pre-wrap;background:#020617;border:1px solid #312e81;border-radius:5px;padding:6px;margin-top:6px;color:#e9d5ff;max-height:220px;overflow:auto;}}'
      + '#repeatation-marker-panel .rm-lessons{{background:#101827;border:1px solid #14b8a6;border-radius:6px;padding:7px;margin:6px 0;color:#ccfbf1;}}'
      + '#repeatation-marker-panel .rm-lessons summary{{cursor:pointer;color:#99f6e4;font-weight:700;display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-lessons summary span,.rm-lesson-item span,.rm-lesson-draft span{{color:#fde68a;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-lesson-item,.rm-lesson-draft{{border-top:1px solid #115e59;padding-top:5px;margin-top:5px;}}'
      + '#repeatation-marker-panel .rm-lesson-item>div:first-child,.rm-lesson-draft>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#ccfbf1;}}'
      + '#repeatation-marker-panel .rm-review{{background:#07140f;border:1px solid #22c55e;border-radius:6px;padding:7px;margin:6px 0;color:#dcfce7;}}'
      + '#repeatation-marker-panel .rm-review>div:first-child{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#bbf7d0;}}'
      + '#repeatation-marker-panel .rm-review span{{color:#fde68a;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-review-impact{{background:#020617;border:1px solid #14532d;border-radius:5px;padding:6px;margin-top:6px;}}'
      + '#repeatation-marker-panel .rm-review-impact summary{{cursor:pointer;color:#bbf7d0;font-weight:700;}}'
      + '#repeatation-marker-panel .rm-review-impact-item{{border-top:1px solid #14532d;padding-top:5px;margin-top:5px;color:#d1fae5;}}'
      + '#repeatation-marker-panel .rm-draft{{background:#07111f;border:1px solid #38bdf8;border-radius:6px;padding:7px;margin:6px 0;color:#dbeafe;}}'
      + '#repeatation-marker-panel .rm-draft summary{{cursor:pointer;color:#bae6fd;font-weight:700;}}'
      + '#repeatation-marker-panel .rm-draft pre{{max-height:280px;border-color:#164e63;color:#e0f2fe;}}'
      + '#repeatation-marker-panel .rm-verifier{{background:#111827;border:1px solid #22d3ee;border-radius:6px;padding:7px;margin:6px 0;color:#cffafe;}}'
      + '#repeatation-marker-panel .rm-verifier summary{{cursor:pointer;color:#a5f3fc;font-weight:700;display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-verifier summary span{{color:#fde68a;font-size:11px;}}'
      + '#repeatation-marker-panel .rm-verifier-issue{{border-top:1px solid #164e63;padding-top:5px;margin-top:5px;}}'
      + '#repeatation-marker-panel .rm-verifier-issue>b{{color:#fef3c7;}}'
      + '#repeatation-marker-panel .rm-verifier-issue span{{float:right;font-size:10px;text-transform:uppercase;color:#fde68a;}}'
      + '#repeatation-marker-panel .rm-verifier-issue.contradiction{{color:#fecaca;border-color:#7f1d1d;}}'
      + '#repeatation-marker-panel .rm-verifier-issue.unsupported,#repeatation-marker-panel .rm-verifier-issue.missing{{color:#fed7aa;border-color:#7c2d12;}}'
      + '#repeatation-marker-panel .rm-verifier-issue.caution{{color:#fde68a;border-color:#713f12;}}'
      + '#repeatation-marker-panel .rm-verifier-pass{{border-top:1px solid #164e63;margin-top:6px;padding-top:6px;color:#bbf7d0;}}'
      + '#repeatation-marker-panel .rm-verifier-checks{{border-top:1px solid #164e63;margin-top:6px;padding-top:6px;color:#bae6fd;}}'
      + '#repeatation-marker-panel .rm-verifier-checks ul{{margin:5px 0 0 16px;padding:0;color:#cffafe;}}'
      + '#repeatation-marker-panel .rm-dream{{background:#111827;border:1px solid #f97316;border-radius:6px;padding:7px;margin:6px 0;color:#fed7aa;}}'
      + '#repeatation-marker-panel .rm-dream summary{{cursor:pointer;color:#fdba74;font-weight:700;display:flex;align-items:center;justify-content:space-between;gap:8px;}}'
      + '#repeatation-marker-panel .rm-dream summary span{{color:#fef3c7;font-size:11px;}}'
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
      drawMarkers();
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
    panel.querySelector('#repeatation-show-gann').addEventListener('click', showGannFan);
    panel.querySelector('#repeatation-save-rule-lesson').addEventListener('click', saveRuleLesson);
    panel.querySelector('#repeatation-complete-review').addEventListener('click', completeReview);
    panel.querySelector('#repeatation-draft-ml-reason').addEventListener('click', draftMlReason);
    panel.querySelector('#repeatation-ignore-trade').addEventListener('click', markIgnoreTrade);
    panel.querySelector('#repeatation-add-ignore-signal').addEventListener('click', function () {{ addAnnotation('ignore_signal'); }});
    panel.querySelector('#repeatation-add-rule-note').addEventListener('click', function () {{ addAnnotation('rule_note'); }});
    panel.querySelector('#repeatation-clear-annotations').addEventListener('click', clearAnnotations);
    panel.querySelector('#repeatation-reset-cursor').addEventListener('click', resetCursorState);
    panel.querySelector('#repeatation-download').addEventListener('click', downloadMarkers);
    panel.querySelector('#repeatation-note').addEventListener('input', function () {{ render(); saveDraft(); }});
    panel.querySelector('#repeatation-note-type').addEventListener('input', function () {{ render(); saveDraft(); }});
    setOutcome(defaultOutcome());
    panel.querySelector('#repeatation-outcome').addEventListener('change', function () {{ state.outcomeTouched = true; refreshGannFanFromTradeStart('outcome changed'); drawMarkers(); render(); saveDraft(); }});
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
    family_rules = load_case_family_rules(args.db, seed)
    ml_notes_by_case = load_ml_notes(args.db, seed)
    lessons_by_case = load_rule_lessons(args.db, seed)
    completed_reviews_by_case = load_completed_reviews(args.db, seed)
    for case in cases:
        stats = stats_by_case[int(case["case_id"])]
        case.update(stats)
        direction = str(stats.get("full_window_direction", "") or "").strip().lower()
        case["default_outcome"] = direction if direction in {"bullish", "bearish"} else "unclear"
        case["special_traits"] = special_traits_by_case.get(int(case["case_id"]), {})
        case["applied_family_rules"] = family_rules
        case["ml_notes"] = ml_notes_by_case.get(int(case["case_id"]), ml_notes_by_case.get(0, []))
        case["rule_lessons"] = lessons_by_case.get(int(case["case_id"]), lessons_by_case.get(0, []))
        case["completed_review"] = completed_reviews_by_case.get(int(case["case_id"]))

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
                "applied_family_rules",
                "ml_notes",
                "rule_lessons",
                "completed_review",
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
            "applied_family_rules_json": json.dumps(case.get("applied_family_rules", []), ensure_ascii=False),
            "ml_notes_json": json.dumps(case.get("ml_notes", []), ensure_ascii=False),
            "rule_lessons_json": json.dumps(case.get("rule_lessons", []), ensure_ascii=False),
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
