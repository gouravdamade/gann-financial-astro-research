from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from decision_engine import (
    DECISION_PACKET_CONTRACT,
    ENGINE,
    ENGINE_VERSION,
    LIVE_INFERENCE,
    POLICY_VERSION,
)


DEFAULT_EVENTS = Path(r"D:\PycharmProjects\astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet")
DEFAULT_TOUCHES = Path(
    r"D:\PycharmProjects\aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv"
)
DEFAULT_PRICE = Path(r"D:\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet")
DEFAULT_OUTPUT_DIR = Path(
    r"D:\GannFinancialAstro\validation\timestamp_safe_decision_v1_20260713"
)
DEFAULT_REPORT = Path(r"D:\PycharmProjects\timestamp_safe_decision_walk_forward_20260713.md")

TIMEFRAME_MINUTES = {"M30": 30, "H1": 60, "H4": 240, "D1": 1440}
VALID_LABELS = {"UP", "DOWN"}
OBSERVED_LABEL_COLUMNS = {
    "after72_time_local",
    "close_after72",
    "ret_after_72h_dir",
    "ret_after_72h_pct",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Purged/embargoed evaluation of timestamp-safe decision packets."
    )
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--touches", type=Path, default=DEFAULT_TOUCHES)
    parser.add_argument("--price", type=Path, default=DEFAULT_PRICE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--timeframe", choices=sorted(TIMEFRAME_MINUTES), default="H1")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--initial-train-frac", type=float, default=0.40)
    parser.add_argument("--embargo-hours", type=float, default=72.0)
    parser.add_argument("--min-train-clusters", type=int, default=100)
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def timeframe_delta(timeframe: str) -> pd.Timedelta:
    normalized = str(timeframe or "").strip().upper()
    if normalized not in TIMEFRAME_MINUTES:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    return pd.Timedelta(minutes=TIMEFRAME_MINUTES[normalized])


def touch_close_decision_time(touch_time: Any, timeframe: str) -> pd.Timestamp:
    parsed = pd.Timestamp(touch_time)
    if pd.isna(parsed) or parsed.tzinfo is None:
        raise ValueError("touch time must include a UTC offset")
    return parsed.tz_convert("UTC") + timeframe_delta(timeframe)


def purged_embargo_training_rows(
    history: pd.DataFrame,
    test_start_time: pd.Timestamp,
    embargo: pd.Timedelta,
) -> tuple[pd.DataFrame, pd.Timestamp, int]:
    cutoff = pd.Timestamp(test_start_time).tz_convert("UTC") - embargo
    eligible = history[history["label_available_time_utc"] <= cutoff].copy()
    return eligible, cutoff, int(len(history) - len(eligible))


def chronological_fold_windows(
    frame: pd.DataFrame,
    folds: int,
    initial_train_frac: float,
) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    if not 0.0 < initial_train_frac < 1.0:
        raise ValueError("initial_train_frac must be between zero and one")
    unique_times = pd.DatetimeIndex(frame["decision_time_utc"].dropna().sort_values().unique())
    if len(unique_times) < 2:
        return []
    initial_count = max(1, int(math.ceil(len(unique_times) * initial_train_frac)))
    test_times = unique_times[initial_count:]
    if len(test_times) == 0:
        return []
    chunks = [chunk for chunk in np.array_split(test_times, max(1, folds)) if len(chunk)]
    return [(pd.Timestamp(chunk[0]), pd.Timestamp(chunk[-1])) for chunk in chunks]


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return float("nan"), float("nan")
    proportion = successes / total
    denominator = 1.0 + (z * z / total)
    centre = proportion + (z * z / (2.0 * total))
    spread = z * math.sqrt(
        (proportion * (1.0 - proportion) / total) + (z * z / (4.0 * total * total))
    )
    return (centre - spread) / denominator, (centre + spread) / denominator


def exact_binomial_two_sided_pvalue(successes: int, total: int) -> float:
    if total <= 0:
        return float("nan")
    denominator = 2**total
    lower = sum(math.comb(total, index) for index in range(0, successes + 1)) / denominator
    upper = sum(math.comb(total, index) for index in range(successes, total + 1)) / denominator
    return float(min(1.0, 2.0 * min(lower, upper)))


def balanced_direction_accuracy(watches: pd.DataFrame) -> float:
    recalls: list[float] = []
    for label in ("UP", "DOWN"):
        subset = watches[watches["observed_direction"] == label]
        if len(subset):
            recalls.append(float(subset["hit"].mean()))
    return float(np.mean(recalls)) if len(recalls) == 2 else float("nan")


def majority_direction(frame: pd.DataFrame) -> str:
    cluster_labels = consistent_cluster_labels(frame)
    counts = cluster_labels["observed_direction"].value_counts()
    up = int(counts.get("UP", 0))
    down = int(counts.get("DOWN", 0))
    if up == down:
        return "ABSTAIN"
    return "UP" if up > down else "DOWN"


def consistent_cluster_labels(frame: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for decision_time, group in frame.groupby("decision_time_utc", sort=True):
        labels = sorted(set(group["observed_direction"]) & VALID_LABELS)
        if len(labels) != 1:
            continue
        records.append(
            {
                "decision_time_utc": decision_time,
                "observed_direction": labels[0],
                "observed_return_pct": float(
                    pd.to_numeric(group["observed_return_pct"], errors="coerce").mean()
                ),
                "label_available_time_utc": group["label_available_time_utc"].max(),
                "event_count": int(len(group)),
            }
        )
    return pd.DataFrame(records)


def cluster_decisions(frame: pd.DataFrame, training_majority: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for decision_time, group in frame.groupby("decision_time_utc", sort=True):
        labels = sorted(set(group["observed_direction"]) & VALID_LABELS)
        watch_directions = sorted(
            set(group.loc[group["packet_status"] == "watch", "predicted_direction"])
            & {"bullish", "bearish"}
        )
        observed = labels[0] if len(labels) == 1 else "MIXED"
        if len(watch_directions) == 1:
            predicted = watch_directions[0]
            status = "watch"
        elif len(watch_directions) > 1:
            predicted = "abstain"
            status = "abstain_conflicting_packets"
        else:
            predicted = "abstain"
            status = "abstain"
        observed_return = float(pd.to_numeric(group["observed_return_pct"], errors="coerce").mean())
        predicted_label = {"bullish": "UP", "bearish": "DOWN"}.get(predicted)
        hit = bool(predicted_label == observed) if predicted_label and observed in VALID_LABELS else None
        signed_return = None
        if predicted == "bullish":
            signed_return = observed_return
        elif predicted == "bearish":
            signed_return = -observed_return
        records.append(
            {
                "decision_time_utc": decision_time,
                "label_available_time_utc": group["label_available_time_utc"].max(),
                "event_count": int(len(group)),
                "watch_packet_count": int((group["packet_status"] == "watch").sum()),
                "packet_status": status,
                "predicted_direction": predicted,
                "observed_direction": observed,
                "observed_return_pct": observed_return,
                "hit": hit,
                "signed_return_pct": signed_return,
                "training_majority_direction": training_majority,
                "training_majority_hit": (
                    bool(training_majority == observed)
                    if training_majority in VALID_LABELS and observed in VALID_LABELS
                    else None
                ),
            }
        )
    return pd.DataFrame(records)


def prediction_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    valid = frame[frame["observed_direction"].isin(VALID_LABELS)].copy()
    watches = valid[valid["packet_status"] == "watch"].copy()
    watches["hit"] = watches["hit"].astype(bool)
    total = int(len(valid))
    watch_count = int(len(watches))
    hits = int(watches["hit"].sum()) if watch_count else 0
    low, high = wilson_interval(hits, watch_count)
    majority_values = pd.to_numeric(valid["training_majority_hit"], errors="coerce").dropna()
    watch_majority = pd.to_numeric(watches["training_majority_hit"], errors="coerce").dropna()
    signed = pd.to_numeric(watches["signed_return_pct"], errors="coerce").dropna()
    return {
        "eligible": total,
        "watches": watch_count,
        "abstentions": int(total - watch_count),
        "coverage": float(watch_count / total) if total else float("nan"),
        "hits": hits,
        "misses": int(watch_count - hits),
        "hit_rate": float(hits / watch_count) if watch_count else float("nan"),
        "hit_rate_wilson_95_low": low,
        "hit_rate_wilson_95_high": high,
        "balanced_direction_accuracy": balanced_direction_accuracy(watches),
        "binomial_two_sided_p_vs_50": exact_binomial_two_sided_pvalue(hits, watch_count),
        "training_majority_hit_rate_all": (
            float(majority_values.mean()) if len(majority_values) else float("nan")
        ),
        "training_majority_hit_rate_watch_subset": (
            float(watch_majority.mean()) if len(watch_majority) else float("nan")
        ),
        "selective_lift_vs_training_majority": (
            float((hits / watch_count) - watch_majority.mean())
            if watch_count and len(watch_majority)
            else float("nan")
        ),
        "mean_signed_72h_return_pct": float(signed.mean()) if len(signed) else float("nan"),
        "median_signed_72h_return_pct": float(signed.median()) if len(signed) else float("nan"),
    }


def load_inputs(
    events_path: Path,
    touches_path: Path,
    price_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    events = pd.read_parquet(events_path).copy()
    touches = pd.read_csv(touches_path).copy()
    price = pd.read_parquet(price_path).copy().sort_index()
    for column in ("timestamp", "event_end"):
        events[column] = pd.to_datetime(events[column], errors="coerce", utc=True)
    for column in ("touch_time_local", "after72_time_local"):
        touches[column] = pd.to_datetime(touches[column], errors="coerce", utc=True)
    if price.index.tz is None:
        price.index = price.index.tz_localize("UTC")
    else:
        price.index = price.index.tz_convert("UTC")
    return events, touches, price


def build_packet_frame(
    events: pd.DataFrame,
    touches: pd.DataFrame,
    price: pd.DataFrame,
    timeframe: str,
) -> tuple[pd.DataFrame, list[dict[str, Any]], list[dict[str, Any]]]:
    event_map = {
        str(row["event_id"]): row
        for _, row in events.drop_duplicates("event_id", keep="first").iterrows()
    }
    records: list[dict[str, Any]] = []
    packets: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []
    artifact = {
        "artifactId": "corrected_usdjpy_tn_baseline_20250301_20260310",
        "label": "Corrected USDJPY TN baseline evaluation",
        "symbol": "USDJPY",
        "sourceTimeframe": timeframe,
        "parameters": {"priceSourceId": "versioned_baseline"},
    }
    for _, touch in touches.iterrows():
        event_id = str(touch.get("event_id") or "")
        event = event_map.get(event_id)
        if event is None:
            quarantined.append({"event_id": event_id, "reason": "event_not_found"})
            continue
        try:
            decision_time = touch_close_decision_time(touch.get("touch_time_local"), timeframe)
            label_time = pd.Timestamp(touch.get("after72_time_local"))
            if pd.isna(label_time) or label_time.tzinfo is None:
                raise ValueError("label availability time is missing or timezone-naive")
            # after72_time_local is the target bar's open timestamp. Its close is
            # the first instant when close_after72 and the stored direction exist.
            label_time = label_time.tz_convert("UTC") + timeframe_delta(timeframe)
            observed_direction = str(touch.get("ret_after_72h_dir") or "").upper()
            observed_return = float(touch.get("ret_after_72h_pct"))
            if observed_direction not in VALID_LABELS:
                raise ValueError(f"unsupported observed label: {observed_direction or 'missing'}")
            if not np.isfinite(observed_return):
                raise ValueError("observed return is missing")
            if label_time <= decision_time:
                raise ValueError("observed label was already available by decision time")
            packet = ENGINE.live_inference_packet(
                event=event,
                touch=touch,
                price=price,
                decision_time=decision_time,
                timeframe=timeframe,
                artifact=artifact,
            )
            forbidden = set(packet["featureAudit"]["forbiddenFieldsPresentButExcluded"])
            if not OBSERVED_LABEL_COLUMNS.issubset(forbidden):
                missing = sorted(OBSERVED_LABEL_COLUMNS - forbidden)
                raise ValueError(f"label exclusion audit is incomplete: {missing}")
            if packet["mode"] != LIVE_INFERENCE or packet["outcome"] is not None:
                raise ValueError("packet is not a label-free live inference packet")
            if not packet["guardrails"]["timestampSafe"] or not packet["guardrails"]["noLookahead"]:
                raise ValueError("packet failed timestamp/no-lookahead guardrails")
            source_max = packet["times"].get("sourceDataMaxTime")
            if source_max and pd.Timestamp(source_max) > decision_time:
                raise ValueError("packet price evidence exceeds decision time")
        except Exception as exc:
            quarantined.append({"event_id": event_id, "reason": str(exc)})
            continue

        predicted = str(packet["decision"]["direction"])
        predicted_label = {"bullish": "UP", "bearish": "DOWN"}.get(predicted)
        hit = bool(predicted_label == observed_direction) if predicted_label else None
        signed_return = None
        if predicted == "bullish":
            signed_return = observed_return
        elif predicted == "bearish":
            signed_return = -observed_return
        records.append(
            {
                "event_id": event_id,
                "family_key": str(event.get("event_family_key") or ""),
                "decision_time_utc": decision_time,
                "label_available_time_utc": label_time,
                "packet_id": packet["packetId"],
                "packet_status": packet["status"],
                "packet_action": packet["decision"]["action"],
                "predicted_direction": predicted,
                "raw_direction": packet["evidence"].get("fx_hypothesis_direction", "UNKNOWN"),
                "doctrine_direction": packet["evidence"].get(
                    "fx_doctrine_hypothesis_direction", "UNKNOWN"
                ),
                "observed_direction": observed_direction,
                "observed_return_pct": observed_return,
                "hit": hit,
                "signed_return_pct": signed_return,
                "forbidden_label_fields_excluded": True,
                "source_data_max_time": packet["times"].get("sourceDataMaxTime"),
            }
        )
        packets.append(packet)
    frame = pd.DataFrame(records)
    if not frame.empty:
        frame = frame.sort_values(["decision_time_utc", "event_id"], ignore_index=True)
    return frame, packets, quarantined


def evaluate_walk_forward(
    frame: pd.DataFrame,
    folds: int,
    initial_train_frac: float,
    embargo: pd.Timedelta,
    min_train_clusters: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    windows = chronological_fold_windows(frame, folds, initial_train_frac)
    fold_records: list[dict[str, Any]] = []
    oos_rows: list[pd.DataFrame] = []
    oos_clusters: list[pd.DataFrame] = []
    skipped: list[dict[str, Any]] = []
    for fold_index, (test_start, test_end) in enumerate(windows, start=1):
        history = frame[frame["decision_time_utc"] < test_start].copy()
        train, cutoff, purged_count = purged_embargo_training_rows(history, test_start, embargo)
        train_clusters = consistent_cluster_labels(train)
        test = frame[
            (frame["decision_time_utc"] >= test_start)
            & (frame["decision_time_utc"] <= test_end)
        ].copy()
        if len(train_clusters) < min_train_clusters or test.empty:
            skipped.append(
                {
                    "fold": fold_index,
                    "reason": "minimum training clusters not met" if len(train_clusters) < min_train_clusters else "empty test",
                    "train_clusters": int(len(train_clusters)),
                    "test_rows": int(len(test)),
                }
            )
            continue
        majority = majority_direction(train)
        test["fold"] = fold_index
        test["training_majority_direction"] = majority
        test["training_majority_hit"] = test["observed_direction"] == majority
        clusters = cluster_decisions(test, majority)
        clusters["fold"] = fold_index
        cluster_metrics = prediction_metrics(clusters)
        row_metrics = prediction_metrics(test)
        fold_records.append(
            {
                "fold": fold_index,
                "test_start": test_start,
                "test_end": test_end,
                "embargo_cutoff": cutoff,
                "history_rows": int(len(history)),
                "purged_or_embargoed_history_rows": purged_count,
                "train_rows": int(len(train)),
                "train_clusters": int(len(train_clusters)),
                "test_rows": int(len(test)),
                "test_clusters": int(len(clusters)),
                "training_majority_direction": majority,
                **{f"cluster_{key}": value for key, value in cluster_metrics.items()},
                **{f"row_{key}": value for key, value in row_metrics.items()},
            }
        )
        oos_rows.append(test)
        oos_clusters.append(clusters)
    fold_frame = pd.DataFrame(fold_records)
    row_frame = pd.concat(oos_rows, ignore_index=True) if oos_rows else pd.DataFrame()
    cluster_frame = pd.concat(oos_clusters, ignore_index=True) if oos_clusters else pd.DataFrame()
    aggregate = {
        "primary_cluster_metrics": prediction_metrics(cluster_frame) if len(cluster_frame) else {},
        "secondary_row_metrics": prediction_metrics(row_frame) if len(row_frame) else {},
        "folds_completed": int(len(fold_frame)),
        "folds_skipped": skipped,
    }
    return fold_frame, row_frame, cluster_frame, aggregate


def statistical_gate(aggregate: dict[str, Any], fold_frame: pd.DataFrame) -> dict[str, Any]:
    metrics = aggregate.get("primary_cluster_metrics") or {}
    positive_return_folds = int(
        (pd.to_numeric(fold_frame.get("cluster_mean_signed_72h_return_pct"), errors="coerce") > 0).sum()
    ) if len(fold_frame) else 0
    criteria = {
        "minimum_100_watch_clusters": int(metrics.get("watches") or 0) >= 100,
        "coverage_at_least_10_percent": float(metrics.get("coverage") or 0.0) >= 0.10,
        "wilson_95_lower_above_50_percent": float(
            metrics.get("hit_rate_wilson_95_low") or 0.0
        ) > 0.50,
        "two_sided_binomial_p_below_0_05": float(
            metrics.get("binomial_two_sided_p_vs_50") or 1.0
        ) < 0.05,
        "at_least_four_completed_folds": int(aggregate.get("folds_completed") or 0) >= 4,
        "positive_mean_signed_return_in_four_folds": positive_return_folds >= 4,
    }
    return {
        "status": "passed_retrospective_statistical_gate" if all(criteria.values()) else "failed_retrospective_statistical_gate",
        "criteria": criteria,
        "positive_return_folds": positive_return_folds,
        "execution_gate": "blocked",
        "execution_blockers": [
            "not_an_untouched_prospective_holdout",
            "external_shadbala_drik_certification_pending",
            "mt5_execution_not_authorized",
        ],
    }


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(value).isoformat()
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def percent(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{numeric * 100:.2f}%" if np.isfinite(numeric) else "n/a"


def report_markdown(summary: dict[str, Any]) -> str:
    metrics = summary["aggregate"]["primary_cluster_metrics"]
    row_metrics = summary["aggregate"]["secondary_row_metrics"]
    gate = summary["gate"]
    fold_lines = [
        "| Fold | Train clusters | Purged | Test clusters | Watches | Hit rate | Mean signed 72h |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for fold in summary["fold_metrics"]:
        fold_lines.append(
            "| {fold} | {train} | {purged} | {test} | {watches} | {hit} | {signed:.4f}% |".format(
                fold=fold["fold"],
                train=fold["train_clusters"],
                purged=fold["purged_or_embargoed_history_rows"],
                test=fold["test_clusters"],
                watches=fold["cluster_watches"],
                hit=percent(fold["cluster_hit_rate"]),
                signed=float(fold["cluster_mean_signed_72h_return_pct"]),
            )
        )
    criteria_lines = [
        f"- [{'x' if passed else ' '}] {name.replace('_', ' ')}"
        for name, passed in gate["criteria"].items()
    ]
    return "\n".join(
        [
            "# Timestamp-Safe Decision Walk-Forward Evaluation",
            "",
            f"Generated: {summary['generated_at_utc']}",
            "",
            "## Frozen Contract",
            "",
            f"- Packet: `{DECISION_PACKET_CONTRACT}`",
            f"- Engine: `{ENGINE_VERSION}`",
            f"- Policy: `{POLICY_VERSION}`",
            "- Decision time: selected SR-touch candle close.",
            "- Label time: close of the stored 72-hour target bar; its open timestamp is not treated as outcome availability.",
            f"- Embargo after label availability: {summary['config']['embargo_hours']:.1f} hours.",
            "- Primary unit: one unique decision timestamp, consolidating simultaneous event rows.",
            "- Frozen policy uses no fitted parameter and test labels never enter decision packets.",
            f"- Event source SHA-256: `{summary['inputs']['events_sha256']}`",
            f"- Touch source SHA-256: `{summary['inputs']['touches_sha256']}`",
            f"- Price source SHA-256: `{summary['inputs']['price_sha256']}`",
            "",
            "## Primary Out-of-Sample Result",
            "",
            f"- Eligible decision clusters: {metrics['eligible']}",
            f"- Watch clusters: {metrics['watches']} ({percent(metrics['coverage'])} coverage)",
            f"- Directional hits: {metrics['hits']} / {metrics['watches']} ({percent(metrics['hit_rate'])})",
            f"- Wilson 95% interval: {percent(metrics['hit_rate_wilson_95_low'])} to {percent(metrics['hit_rate_wilson_95_high'])}",
            f"- Balanced direction accuracy: {percent(metrics['balanced_direction_accuracy'])}",
            f"- Exact two-sided binomial p vs 50%: {metrics['binomial_two_sided_p_vs_50']:.6f}",
            f"- Training-majority hit rate on the same watch clusters: {percent(metrics['training_majority_hit_rate_watch_subset'])}",
            f"- Selective lift: {percent(metrics['selective_lift_vs_training_majority'])}",
            f"- Mean signed 72h return (descriptive, no costs): {metrics['mean_signed_72h_return_pct']:.4f}%",
            "",
            "## Fold Stability",
            "",
            *fold_lines,
            "",
            "## Secondary Row-Level Diagnostic",
            "",
            f"- Eligible event rows: {row_metrics['eligible']}",
            f"- Watches: {row_metrics['watches']} ({percent(row_metrics['coverage'])} coverage)",
            f"- Hit rate: {percent(row_metrics['hit_rate'])}",
            "- Row metrics are secondary because simultaneous astrological events can share one market outcome.",
            "",
            "## Predeclared Statistical Gate",
            "",
            f"Status: **{gate['status']}**",
            "",
            *criteria_lines,
            "",
            "## Interpretation",
            "",
            "This is a purged chronological retrospective evaluation, not an untouched prospective trial. "
            "It can reject a weak policy, but it cannot authorize live orders. The execution gate remains "
            "blocked regardless of the statistical result until prospective shadow evidence, external "
            "astrology-component certification, and explicit MT5 execution authorization all exist.",
            "",
            "No transaction costs, spread, slippage, position sizing, entry, exit, or P/L execution logic "
            "is claimed by this watch/abstain evaluation.",
            "",
        ]
    )


def main() -> None:
    args = parse_args()
    events, touches, price = load_inputs(args.events, args.touches, args.price)
    frame, packets, quarantined = build_packet_frame(
        events,
        touches,
        price,
        args.timeframe,
    )
    if len(frame) < 100:
        raise SystemExit(f"Not enough valid timestamp-safe rows: {len(frame)}")
    fold_frame, row_frame, cluster_frame, aggregate = evaluate_walk_forward(
        frame,
        folds=int(args.folds),
        initial_train_frac=float(args.initial_train_frac),
        embargo=pd.Timedelta(hours=float(args.embargo_hours)),
        min_train_clusters=int(args.min_train_clusters),
    )
    if fold_frame.empty:
        raise SystemExit("No purged walk-forward folds met the minimum training requirement.")
    gate = statistical_gate(aggregate, fold_frame)
    summary = {
        "contract": "GANN_TIMESTAMP_SAFE_WALK_FORWARD_EVALUATION_V1",
        "generated_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "packet_contract": DECISION_PACKET_CONTRACT,
        "engine_version": ENGINE_VERSION,
        "policy_version": POLICY_VERSION,
        "config": {
            "timeframe": args.timeframe,
            "folds_requested": int(args.folds),
            "initial_train_fraction": float(args.initial_train_frac),
            "embargo_hours": float(args.embargo_hours),
            "min_train_clusters": int(args.min_train_clusters),
            "primary_unit": "unique_decision_timestamp_cluster",
            "decision_time_rule": "touch_bar_close",
            "label_availability_rule": "after72_time_local",
        },
        "inputs": {
            "events": str(args.events.resolve()),
            "events_sha256": file_sha256(args.events),
            "touches": str(args.touches.resolve()),
            "touches_sha256": file_sha256(args.touches),
            "price": str(args.price.resolve()),
            "price_sha256": file_sha256(args.price),
        },
        "rows": {
            "touch_rows": int(len(touches)),
            "valid_packet_rows": int(len(frame)),
            "quarantined_rows": int(len(quarantined)),
            "oos_rows": int(len(row_frame)),
            "oos_clusters": int(len(cluster_frame)),
        },
        "aggregate": aggregate,
        "fold_metrics": json_ready(fold_frame.to_dict(orient="records")),
        "gate": gate,
        "limitations": [
            "retrospective_chronological_not_untouched_prospective",
            "policy_and_doctrine_were_developed_before_this_report",
            "simultaneous_events_share_market_outcomes_primary_metrics_are_clustered",
            "no_transaction_cost_or_execution_model",
            "external_shadbala_drik_certification_pending",
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_dir / "all_packet_rows.csv", index=False)
    row_frame.to_csv(args.output_dir / "oos_event_rows.csv", index=False)
    cluster_frame.to_csv(args.output_dir / "oos_decision_clusters.csv", index=False)
    fold_frame.to_csv(args.output_dir / "fold_metrics.csv", index=False)
    (args.output_dir / "quarantined_rows.json").write_text(
        json.dumps(json_ready(quarantined), indent=2), encoding="utf-8"
    )
    with (args.output_dir / "decision_packets.jsonl").open("w", encoding="utf-8") as handle:
        for packet in packets:
            handle.write(json.dumps(json_ready(packet), sort_keys=True) + "\n")
    ready_summary = json_ready(summary)
    (args.output_dir / "summary.json").write_text(
        json.dumps(ready_summary, indent=2), encoding="utf-8"
    )
    args.report.write_text(report_markdown(ready_summary), encoding="utf-8")
    print(json.dumps({
        "output_dir": str(args.output_dir),
        "report": str(args.report),
        "rows": ready_summary["rows"],
        "primary_cluster_metrics": ready_summary["aggregate"]["primary_cluster_metrics"],
        "gate": ready_summary["gate"],
    }, indent=2))


if __name__ == "__main__":
    main()
