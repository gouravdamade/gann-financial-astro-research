from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "gann-astro-desk" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from candlestick_analysis import METHODOLOGY_VERSION, _records  # noqa: E402


EVALUATION_CONTRACT = "GANN_CANDLESTICK_WALK_FORWARD_CONTRACT_V1"
RESULT_CONTRACT = "GANN_CANDLESTICK_WALK_FORWARD_RESULT_V1"
DEFAULT_CONTRACT_PATH = Path(__file__).with_name("usdjpy_evaluation_contract_v1.json")
DEFAULT_VALIDATION_ROOT = Path(r"D:\GannFinancialAstro\validation")

PATTERN_NAMES = (
    "doji",
    "spinning_top",
    "marubozu_like",
    "long_bullish_body",
    "long_bearish_body",
    "long_lower_wick",
    "long_upper_wick",
    "bullish_body_engulfing",
    "bearish_body_engulfing",
    "inside_bar",
    "outside_bar",
)
RAW_FEATURE_COLUMNS = (
    "body_signed_fraction",
    "upper_wick_fraction",
    "lower_wick_fraction",
    "close_location",
    "range_atr_ratio",
    "pretrend_signed_strength_atr",
    "gap_from_prior_close_atr",
)
PATTERN_FEATURE_COLUMNS = tuple(f"pattern_{name}" for name in PATTERN_NAMES)
STRATEGY_NAMES = (
    "always_long_v1",
    "body_momentum_v1",
    "momentum_5bar_v1",
    "training_majority_v1",
    "raw_wick_reversal_rule_v1",
    "named_pattern_rule_v1",
    "raw_geometry_logistic_v1",
    "named_pattern_logistic_v1",
)
LABEL_COLUMNS = (
    "future_entry_price",
    "future_exit_price",
    "future_gross_long_pips",
    "future_spread_pips",
    "future_total_cost_pips",
    "target_up",
    "entry_time",
    "exit_time",
    "label_available_time",
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sign(value: float, epsilon: float = 1e-12) -> int:
    if value > epsilon:
        return 1
    if value < -epsilon:
        return -1
    return 0


def load_contract(path: Path) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(contract, dict) or contract.get("contract") != EVALUATION_CONTRACT:
        raise ValueError("Unsupported candlestick evaluation contract")
    if contract.get("status") != "retrospective_research_only":
        raise ValueError("Candlestick evaluation contract lost its research-only status")
    if contract.get("geometryMethodologyVersion") != METHODOLOGY_VERSION:
        raise ValueError(
            "Evaluation geometry version does not match the application candlestick methodology"
        )
    decision = contract.get("decision") or {}
    splits = contract.get("splits") or {}
    models = contract.get("models") or {}
    gate = contract.get("promotionGate") or {}
    if int(decision.get("confirmationBars", -1)) != 0:
        raise ValueError("Version 1 freezes confirmationBars at zero")
    if int(decision.get("holdingBars", 0)) <= 0:
        raise ValueError("holdingBars must be positive")
    if not 0.0 < float(splits.get("initialTrainFraction", 0.0)) < 1.0:
        raise ValueError("initialTrainFraction must be between zero and one")
    if int(splits.get("folds", 0)) < 2 or int(splits.get("embargoBars", -1)) < 0:
        raise ValueError("split fold and embargo settings are invalid")
    short_probability = float(models.get("shortProbability", 0.0))
    long_probability = float(models.get("longProbability", 1.0))
    if not 0.0 < short_probability < 0.5 < long_probability < 1.0:
        raise ValueError("Frozen probability thresholds are invalid")
    if gate.get("coordinatorAuthorization") is not False:
        raise ValueError("Coordinator authorization must remain false")
    if gate.get("executionAuthorization") is not False:
        raise ValueError("Execution authorization must remain false")
    return contract


def resolve_source_path(contract: dict[str, Any], project_root: Path) -> Path:
    source = Path(str((contract.get("source") or {}).get("path") or ""))
    return (source if source.is_absolute() else project_root / source).expanduser().resolve()


def load_price_source(path: Path, contract: dict[str, Any]) -> pd.DataFrame:
    expected_sha = str((contract.get("source") or {}).get("sha256") or "").upper()
    actual_sha = file_sha256(path)
    if not expected_sha or actual_sha != expected_sha:
        raise ValueError(
            f"USDJPY source SHA-256 mismatch: expected {expected_sha}, found {actual_sha}"
        )
    frame = pd.read_parquet(path).copy()
    required = {"open", "high", "low", "close"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Price source is missing OHLC columns: {missing}")
    if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.tz is None:
        raise ValueError("Price source must have a timezone-aware DatetimeIndex")
    frame = frame.sort_index()
    frame.index = frame.index.tz_convert("UTC")
    if frame.empty or frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError("Price timestamps must be non-empty, unique, and increasing")
    numeric = frame.loc[:, sorted(required)].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("Price source contains missing or non-finite OHLC values")
    if (numeric["high"] < numeric[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("Price source contains an invalid high")
    if (numeric["low"] > numeric[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("Price source contains an invalid low")
    differences = frame.index.to_series().diff().dropna().dt.total_seconds()
    if differences.empty or int(differences.mode().iloc[0]) != 3600:
        raise ValueError("Version 1 requires H1 source bars")
    return frame


def geometry_records(frame: pd.DataFrame, pip_factor: float) -> list[dict[str, Any]]:
    geometry = pd.DataFrame(
        {
            "time": frame.index,
            "open": frame["open"].to_numpy(dtype=float),
            "high": frame["high"].to_numpy(dtype=float),
            "low": frame["low"].to_numpy(dtype=float),
            "close": frame["close"].to_numpy(dtype=float),
        }
    )
    return _records(geometry, 3600, pip_factor)


def directional_pattern_signal(
    patterns: list[dict[str, Any]],
    allowed_names: set[str] | None = None,
) -> int:
    signals: set[int] = set()
    for pattern in patterns:
        name = str(pattern.get("name") or "")
        if allowed_names is not None and name not in allowed_names:
            continue
        bias = str(pattern.get("hypothesisBias") or "").lower()
        if bias == "bullish":
            signals.add(1)
        elif bias == "bearish":
            signals.add(-1)
    return next(iter(signals)) if len(signals) == 1 else 0


def build_decision_dataset(
    frame: pd.DataFrame,
    contract: dict[str, Any],
) -> pd.DataFrame:
    decision = contract["decision"]
    costs = contract["costs"]
    minimum_history = int(decision["minimumHistoryBars"])
    holding_bars = int(decision["holdingBars"])
    pip_size = float(decision["pipSize"])
    point_size = float(decision["pointSize"])
    pip_factor = 1.0 / pip_size
    fallback_spread = float(costs["fallbackSpreadPips"])
    slippage_per_side = float(costs["slippagePipsPerSide"])
    bar_delta = pd.Timedelta(hours=1)
    records = geometry_records(frame, pip_factor)
    if len(records) != len(frame):
        raise ValueError("Candlestick geometry record count drifted from source bars")

    wick_names = {"long_lower_wick", "long_upper_wick"}
    output: list[dict[str, Any]] = []
    for index in range(minimum_history, len(frame) - holding_bars):
        record = records[index]
        source = frame.iloc[index]
        entry_index = index + 1
        exit_index = index + holding_bars
        entry = frame.iloc[entry_index]
        exit_bar = frame.iloc[exit_index]
        decision_open_time = pd.Timestamp(frame.index[index]).tz_convert("UTC")
        feature_available_time = decision_open_time + bar_delta
        entry_time = pd.Timestamp(frame.index[entry_index]).tz_convert("UTC")
        exit_time = pd.Timestamp(frame.index[exit_index]).tz_convert("UTC") + bar_delta
        if entry_time < feature_available_time:
            raise ValueError("Entry precedes decision-bar close")

        spread_points = pd.to_numeric(pd.Series([entry.get("spread", np.nan)]), errors="coerce").iloc[0]
        observed_spread_pips = (
            float(spread_points) * point_size / pip_size
            if pd.notna(spread_points) and float(spread_points) > 0.0
            else fallback_spread
        )
        total_cost_pips = observed_spread_pips + 2.0 * slippage_per_side
        entry_price = float(entry["open"])
        exit_price = float(exit_bar["close"])
        gross_long_pips = (exit_price - entry_price) / pip_size
        candle_range = max(float(source["high"] - source["low"]), 1e-12)
        signed_body = float(source["close"] - source["open"])
        atr_pips = float(record.get("atr14Pips") or 0.0)
        atr_price = atr_pips * pip_size
        prior_close = float(frame.iloc[index - 1]["close"])
        gap_atr = (float(source["open"]) - prior_close) / max(atr_price, 1e-12)
        patterns = list(record.get("patterns") or [])
        pattern_map = {
            str(item.get("name") or ""): str(item.get("hypothesisBias") or "neutral")
            for item in patterns
        }
        row: dict[str, Any] = {
            "source_row_number": index,
            "decision_bar_open_time": decision_open_time,
            "feature_available_time": feature_available_time,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "label_available_time": exit_time,
            "decision_open": float(source["open"]),
            "decision_high": float(source["high"]),
            "decision_low": float(source["low"]),
            "decision_close": float(source["close"]),
            "body_signed_fraction": signed_body / candle_range,
            "upper_wick_fraction": float(record["upperWickFraction"]),
            "lower_wick_fraction": float(record["lowerWickFraction"]),
            "close_location": float(record["closeLocation"]),
            "range_atr_ratio": float(record["rangePips"]) / max(atr_pips, 1e-12),
            "pretrend_signed_strength_atr": float(record["preTrendStrengthAtr"]),
            "gap_from_prior_close_atr": gap_atr,
            "pretrend": str(record["preTrend"]),
            "body_momentum_signal": sign(signed_body),
            "momentum_5bar_signal": sign(float(source["close"] - frame.iloc[index - 5]["close"])),
            "raw_wick_reversal_signal": directional_pattern_signal(patterns, wick_names),
            "named_pattern_rule_signal": directional_pattern_signal(patterns),
            "named_pattern_count": len(patterns),
            "pattern_bias_json": json.dumps(pattern_map, sort_keys=True, separators=(",", ":")),
            "future_entry_price": entry_price,
            "future_exit_price": exit_price,
            "future_gross_long_pips": gross_long_pips,
            "future_spread_pips": observed_spread_pips,
            "future_total_cost_pips": total_cost_pips,
            "target_up": int(gross_long_pips > 0.0),
        }
        for name in PATTERN_NAMES:
            bias = pattern_map.get(name, "neutral")
            row[f"pattern_{name}"] = int(name in pattern_map)
            row[f"pattern_signal_{name}"] = 1 if bias == "bullish" else -1 if bias == "bearish" else 0
        output.append(row)
    dataset = pd.DataFrame(output)
    if dataset.empty:
        raise ValueError("Price source is too short for the frozen decision contract")
    for column in (
        "decision_bar_open_time",
        "feature_available_time",
        "entry_time",
        "exit_time",
        "label_available_time",
    ):
        dataset[column] = pd.to_datetime(dataset[column], utc=True)
    if (dataset["entry_time"] < dataset["feature_available_time"]).any():
        raise ValueError("Dataset contains an entry before feature availability")
    if (dataset["label_available_time"] <= dataset["entry_time"]).any():
        raise ValueError("Dataset contains a label available before its trade exit")
    return dataset.sort_values("feature_available_time").reset_index(drop=True)


def fold_slices(total_rows: int, folds: int, initial_train_fraction: float) -> list[tuple[int, int]]:
    initial_rows = max(1, int(total_rows * initial_train_fraction))
    remaining = total_rows - initial_rows
    if remaining <= 0:
        return []
    fold_size = int(math.ceil(remaining / folds))
    return [
        (start, min(start + fold_size, total_rows))
        for start in range(initial_rows, total_rows, fold_size)
    ][:folds]


def purged_training_rows(
    dataset: pd.DataFrame,
    test_start_index: int,
    test_start_time: pd.Timestamp,
    embargo: pd.Timedelta,
) -> tuple[pd.DataFrame, pd.Timestamp, int]:
    history = dataset.iloc[:test_start_index].copy()
    cutoff = pd.Timestamp(test_start_time) - embargo
    train = history[history["label_available_time"] <= cutoff].copy()
    return train, cutoff, int(len(history) - len(train))


def probability_signals(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: tuple[str, ...],
    contract: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    y_train = train["target_up"].to_numpy(dtype=int)
    models = contract["models"]
    short_threshold = float(models["shortProbability"])
    long_threshold = float(models["longProbability"])
    if len(np.unique(y_train)) < 2:
        probability = np.full(len(test), float(y_train[0]), dtype=float)
    else:
        pipeline = Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        C=float(models["logisticC"]),
                        class_weight=str(models["classWeight"]),
                        max_iter=2000,
                        random_state=int(models["randomSeed"]),
                        solver="liblinear",
                    ),
                ),
            ]
        )
        pipeline.fit(train.loc[:, features], y_train)
        probability = pipeline.predict_proba(test.loc[:, features])[:, 1]
    signals = np.where(
        probability >= long_threshold,
        1,
        np.where(probability <= short_threshold, -1, 0),
    ).astype(int)
    return probability.astype(float), signals


def strategy_metrics(frame: pd.DataFrame, signal_values: np.ndarray) -> dict[str, Any]:
    signal_array = np.asarray(signal_values, dtype=int)
    if len(signal_array) != len(frame):
        raise ValueError("Strategy signal length does not match evaluation frame")
    active = signal_array != 0
    trades = int(active.sum())
    if trades == 0:
        return {
            "rows": int(len(frame)),
            "trades": 0,
            "coverage": 0.0,
            "hit_rate_net": None,
            "mean_gross_pips_per_trade": None,
            "mean_net_pips_per_trade": None,
            "median_net_pips_per_trade": None,
            "total_net_pips": 0.0,
            "max_drawdown_pips": 0.0,
        }
    gross_long = frame["future_gross_long_pips"].to_numpy(dtype=float)[active]
    costs = frame["future_total_cost_pips"].to_numpy(dtype=float)[active]
    gross_signed = signal_array[active] * gross_long
    net = gross_signed - costs
    cumulative = np.cumsum(net)
    path = np.concatenate(([0.0], cumulative))
    drawdown = np.maximum.accumulate(path) - path
    return {
        "rows": int(len(frame)),
        "trades": trades,
        "coverage": float(trades / len(frame)) if len(frame) else 0.0,
        "hit_rate_net": float(np.mean(net > 0.0)),
        "mean_gross_pips_per_trade": float(np.mean(gross_signed)),
        "mean_net_pips_per_trade": float(np.mean(net)),
        "median_net_pips_per_trade": float(np.median(net)),
        "total_net_pips": float(np.sum(net)),
        "max_drawdown_pips": float(np.max(drawdown)),
    }


def weekly_block_bootstrap(
    frame: pd.DataFrame,
    signal_values: np.ndarray,
    samples: int,
    random_seed: int,
) -> dict[str, Any]:
    signal_array = np.asarray(signal_values, dtype=int)
    active = signal_array != 0
    if not active.any():
        return {"blocks": 0, "samples": samples, "mean": None, "lower95": None, "upper95": None}
    active_frame = frame.loc[active, ["feature_available_time", "future_gross_long_pips", "future_total_cost_pips"]].copy()
    active_frame["net"] = (
        signal_array[active] * active_frame["future_gross_long_pips"].to_numpy(dtype=float)
        - active_frame["future_total_cost_pips"].to_numpy(dtype=float)
    )
    iso = active_frame["feature_available_time"].dt.isocalendar()
    active_frame["week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    blocks = [group["net"].to_numpy(dtype=float) for _, group in active_frame.groupby("week", sort=True)]
    rng = np.random.default_rng(random_seed)
    estimates = np.empty(samples, dtype=float)
    for index in range(samples):
        chosen = rng.integers(0, len(blocks), size=len(blocks))
        sampled = np.concatenate([blocks[item] for item in chosen])
        estimates[index] = float(np.mean(sampled))
    return {
        "blocks": len(blocks),
        "samples": samples,
        "mean": float(np.mean(active_frame["net"])),
        "lower95": float(np.quantile(estimates, 0.025)),
        "upper95": float(np.quantile(estimates, 0.975)),
    }


def probability_support_diagnostics(
    predictions: pd.DataFrame,
    strategy_name: str,
    contract: dict[str, Any],
) -> dict[str, Any]:
    probability_column = f"probability_up_{strategy_name}"
    signal_column = f"signal_{strategy_name}"
    probability = predictions[probability_column].to_numpy(dtype=float)
    signal = predictions[signal_column].to_numpy(dtype=int)
    short_threshold = float(contract["models"]["shortProbability"])
    long_threshold = float(contract["models"]["longProbability"])
    short_signals = int(np.sum(signal == -1))
    long_signals = int(np.sum(signal == 1))
    abstentions = int(np.sum(signal == 0))
    folds: list[dict[str, Any]] = []
    for fold, group in predictions.groupby("fold", sort=True):
        fold_probability = group[probability_column].to_numpy(dtype=float)
        fold_signal = group[signal_column].to_numpy(dtype=int)
        folds.append(
            {
                "fold": int(fold),
                "rows": int(len(group)),
                "minimum_probability_up": float(np.min(fold_probability)),
                "maximum_probability_up": float(np.max(fold_probability)),
                "mean_probability_up": float(np.mean(fold_probability)),
                "short_signals": int(np.sum(fold_signal == -1)),
                "long_signals": int(np.sum(fold_signal == 1)),
                "abstentions": int(np.sum(fold_signal == 0)),
            }
        )
    explanation = "Signals crossed at least one frozen probability threshold."
    if short_signals + long_signals == 0:
        explanation = (
            "No out-of-sample probability crossed the frozen short/long thresholds; "
            "zero trades therefore represent deterministic abstention, not a missing prediction."
        )
    return {
        "strategy": strategy_name,
        "rows": int(len(predictions)),
        "short_probability_threshold": short_threshold,
        "long_probability_threshold": long_threshold,
        "minimum_probability_up": float(np.min(probability)),
        "maximum_probability_up": float(np.max(probability)),
        "mean_probability_up": float(np.mean(probability)),
        "short_signals": short_signals,
        "long_signals": long_signals,
        "abstentions": abstentions,
        "explanation": explanation,
        "folds": folds,
    }


def evaluate_walk_forward(
    dataset: pd.DataFrame,
    contract: dict[str, Any],
) -> dict[str, Any]:
    split_config = contract["splits"]
    folds = fold_slices(
        len(dataset),
        int(split_config["folds"]),
        float(split_config["initialTrainFraction"]),
    )
    if len(folds) != int(split_config["folds"]):
        raise ValueError("Unable to create every frozen chronological fold")
    embargo = pd.Timedelta(hours=int(split_config["embargoBars"]))
    fold_metrics: list[dict[str, Any]] = []
    fold_diagnostics: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []

    for fold_number, (test_start, test_stop) in enumerate(folds, start=1):
        test = dataset.iloc[test_start:test_stop].copy()
        test_start_time = pd.Timestamp(test["feature_available_time"].min())
        train, purge_cutoff, purged_rows = purged_training_rows(
            dataset,
            test_start,
            test_start_time,
            embargo,
        )
        if train.empty or test.empty:
            raise ValueError(f"Fold {fold_number} has an empty train or test partition")
        if pd.Timestamp(train["label_available_time"].max()) > purge_cutoff:
            raise ValueError(f"Fold {fold_number} violates purge/embargo timing")

        raw_probability, raw_signal = probability_signals(
            train,
            test,
            RAW_FEATURE_COLUMNS,
            contract,
        )
        pattern_probability, pattern_signal = probability_signals(
            train,
            test,
            PATTERN_FEATURE_COLUMNS,
            contract,
        )
        majority_signal = 1 if float(train["target_up"].mean()) >= 0.5 else -1
        strategies = {
            "always_long_v1": np.ones(len(test), dtype=int),
            "body_momentum_v1": test["body_momentum_signal"].to_numpy(dtype=int),
            "momentum_5bar_v1": test["momentum_5bar_signal"].to_numpy(dtype=int),
            "training_majority_v1": np.full(len(test), majority_signal, dtype=int),
            "raw_wick_reversal_rule_v1": test["raw_wick_reversal_signal"].to_numpy(dtype=int),
            "named_pattern_rule_v1": test["named_pattern_rule_signal"].to_numpy(dtype=int),
            "raw_geometry_logistic_v1": raw_signal,
            "named_pattern_logistic_v1": pattern_signal,
        }
        prediction = test.copy()
        prediction["fold"] = fold_number
        prediction["probability_up_raw_geometry_logistic_v1"] = raw_probability
        prediction["probability_up_named_pattern_logistic_v1"] = pattern_probability
        for strategy_name in STRATEGY_NAMES:
            values = strategies[strategy_name]
            prediction[f"signal_{strategy_name}"] = values
            fold_metrics.append(
                {
                    "fold": fold_number,
                    "strategy": strategy_name,
                    "train_rows": int(len(train)),
                    "test_start": test_start_time.isoformat(),
                    "test_end": pd.Timestamp(test["feature_available_time"].max()).isoformat(),
                    "purge_cutoff": purge_cutoff.isoformat(),
                    **strategy_metrics(test, values),
                }
            )
        prediction_frames.append(prediction)
        fold_diagnostics.append(
            {
                "fold": fold_number,
                "history_rows_before_purge": int(test_start),
                "train_rows": int(len(train)),
                "purged_or_embargoed_rows": purged_rows,
                "test_rows": int(len(test)),
                "test_start": test_start_time.isoformat(),
                "test_end": pd.Timestamp(test["feature_available_time"].max()).isoformat(),
                "purge_cutoff": purge_cutoff.isoformat(),
                "max_train_label_available": pd.Timestamp(train["label_available_time"].max()).isoformat(),
            }
        )

    predictions = pd.concat(prediction_frames, ignore_index=True)
    metric_frame = pd.DataFrame(fold_metrics)
    strategy_summary: list[dict[str, Any]] = []
    for strategy_name in STRATEGY_NAMES:
        signal_values = predictions[f"signal_{strategy_name}"].to_numpy(dtype=int)
        strategy_summary.append({"strategy": strategy_name, **strategy_metrics(predictions, signal_values)})

    pattern_diagnostics: list[dict[str, Any]] = []
    for pattern_name in PATTERN_NAMES:
        signal_values = predictions[f"pattern_signal_{pattern_name}"].to_numpy(dtype=int)
        metrics = strategy_metrics(predictions, signal_values)
        pattern_diagnostics.append(
            {
                "pattern": pattern_name,
                "occurrences": int(predictions[f"pattern_{pattern_name}"].sum()),
                **metrics,
            }
        )

    strategies = contract["strategies"]
    gate_config = contract["promotionGate"]
    primary_name = str(strategies["primaryCandidate"])
    primary_signal = predictions[f"signal_{primary_name}"].to_numpy(dtype=int)
    primary_active = primary_signal != 0
    primary_metrics = strategy_metrics(predictions, primary_signal)
    matched_baselines: list[dict[str, Any]] = []
    best_baseline_mean = -math.inf
    for baseline_name in strategies["matchedBaselines"]:
        baseline_signal = predictions[f"signal_{baseline_name}"].to_numpy(dtype=int)
        matched_frame = predictions.loc[primary_active].copy()
        matched_signal = baseline_signal[primary_active]
        metrics = strategy_metrics(matched_frame, matched_signal)
        matched_baselines.append({"strategy": baseline_name, **metrics})
        mean_net = metrics.get("mean_net_pips_per_trade")
        if mean_net is not None:
            best_baseline_mean = max(best_baseline_mean, float(mean_net))
    if not math.isfinite(best_baseline_mean):
        best_baseline_mean = 0.0
    primary_mean = primary_metrics.get("mean_net_pips_per_trade")
    matched_lift = float(primary_mean or 0.0) - best_baseline_mean
    positive_folds = int(
        (
            metric_frame.loc[
                metric_frame["strategy"] == primary_name,
                "mean_net_pips_per_trade",
            ].fillna(-math.inf)
            > 0.0
        ).sum()
    )
    bootstrap = weekly_block_bootstrap(
        predictions,
        primary_signal,
        int(gate_config["bootstrapSamples"]),
        int(contract["models"]["randomSeed"]),
    )
    checks = {
        "minimum_primary_trades": int(primary_metrics["trades"])
        >= int(gate_config["minimumPrimaryTrades"]),
        "minimum_positive_folds": positive_folds >= int(gate_config["minimumPositiveFolds"]),
        "minimum_matched_lift": matched_lift
        >= float(gate_config["minimumMatchedLiftPipsPerTrade"]),
        "weekly_block_bootstrap_lower_above_zero": bool(
            bootstrap["lower95"] is not None and float(bootstrap["lower95"]) > 0.0
        ),
        "coordinator_authorization_remains_false": gate_config["coordinatorAuthorization"] is False,
        "execution_authorization_remains_false": gate_config["executionAuthorization"] is False,
    }
    statistical_checks = [
        checks["minimum_primary_trades"],
        checks["minimum_positive_folds"],
        checks["minimum_matched_lift"],
    ]
    if gate_config["requireWeeklyBlockBootstrapLowerAboveZero"]:
        statistical_checks.append(checks["weekly_block_bootstrap_lower_above_zero"])
    gate_passed = all(statistical_checks)
    promotion = {
        "status": "passed_retrospective_gate_only" if gate_passed else "failed_retrospective_gate",
        "primary_candidate": primary_name,
        "primary_metrics": primary_metrics,
        "positive_folds": positive_folds,
        "matched_baselines_on_primary_rows": matched_baselines,
        "best_matched_baseline_mean_net_pips_per_trade": best_baseline_mean,
        "matched_lift_pips_per_trade": matched_lift,
        "weekly_block_bootstrap": bootstrap,
        "checks": checks,
        "coordinator_authorized": False,
        "execution_authorized": False,
    }
    probability_diagnostics = {
        strategy_name: probability_support_diagnostics(predictions, strategy_name, contract)
        for strategy_name in ("raw_geometry_logistic_v1", "named_pattern_logistic_v1")
    }
    return {
        "predictions": predictions,
        "fold_metrics": metric_frame,
        "fold_diagnostics": fold_diagnostics,
        "strategy_summary": pd.DataFrame(strategy_summary),
        "pattern_diagnostics": pd.DataFrame(pattern_diagnostics),
        "probability_diagnostics": probability_diagnostics,
        "promotion": promotion,
    }


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    if frame.empty:
        return ["No rows."]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in frame.loc[:, columns].itertuples(index=False, name=None):
        values: list[str] = []
        for value in row:
            if value is None or (isinstance(value, float) and not math.isfinite(value)):
                values.append("n/a")
            elif isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def render_report(
    dataset: pd.DataFrame,
    result: dict[str, Any],
    contract: dict[str, Any],
    source_path: Path,
    source_sha: str,
) -> str:
    summary = result["strategy_summary"].copy()
    columns = [
        "strategy",
        "trades",
        "coverage",
        "hit_rate_net",
        "mean_net_pips_per_trade",
        "total_net_pips",
        "max_drawdown_pips",
    ]
    promotion = result["promotion"]
    primary_probability = result["probability_diagnostics"][promotion["primary_candidate"]]
    lines = [
        "# USDJPY Candlestick Walk-Forward V1",
        "",
        f"Generated: {utc_now()}",
        "",
        "## Frozen Contract",
        "",
        f"- Contract: `{contract['contract']}`",
        f"- Geometry: `{contract['geometryMethodologyVersion']}`",
        f"- Source: `{source_path}`",
        f"- Source SHA-256: `{source_sha}`",
        f"- Decision rows: {len(dataset):,}",
        f"- Decision range: {dataset['feature_available_time'].min()} to {dataset['feature_available_time'].max()}",
        f"- Entry: {contract['decision']['entryPolicy']}",
        f"- Holding: {contract['decision']['holdingBars']} H1 bars",
        f"- Confirmation bars: {contract['decision']['confirmationBars']}",
        f"- Folds: {contract['splits']['folds']} expanding chronological folds",
        f"- Embargo: {contract['splits']['embargoBars']} H1 bars before each test fold",
        f"- Spread fallback: {contract['costs']['fallbackSpreadPips']} pips",
        f"- Slippage: {contract['costs']['slippagePipsPerSide']} pips per side",
        "",
        "## Out-of-Sample Strategy Results",
        "",
        *markdown_table(summary, columns),
        "",
        "## Predeclared Primary Gate",
        "",
        f"Status: **{promotion['status']}**",
        "",
        f"- Primary candidate: `{promotion['primary_candidate']}`",
        f"- Primary trades: {promotion['primary_metrics']['trades']}",
        f"- Positive folds: {promotion['positive_folds']} / {contract['splits']['folds']}",
        f"- Matched lift: {promotion['matched_lift_pips_per_trade']:.4f} pips/trade",
        f"- Weekly-block 95% interval: {promotion['weekly_block_bootstrap']['lower95']} to {promotion['weekly_block_bootstrap']['upper95']}",
        "",
    ]
    for name, passed in promotion["checks"].items():
        lines.append(f"- [{'x' if passed else ' '}] {name}")
    lines.extend(
        [
            "",
            "## Primary Probability Support",
            "",
            f"- Observed probability range: {primary_probability['minimum_probability_up']:.6f} to {primary_probability['maximum_probability_up']:.6f}",
            f"- Frozen decision thresholds: short <= {primary_probability['short_probability_threshold']:.4f}; long >= {primary_probability['long_probability_threshold']:.4f}",
            f"- Signals: {primary_probability['short_signals']} short, {primary_probability['long_signals']} long, {primary_probability['abstentions']} abstentions",
            f"- Explanation: {primary_probability['explanation']}",
            "",
            "## Interpretation Boundary",
            "",
            "This is retrospective, purged chronological evidence. Adjacent labels overlap and",
            "remain serially dependent, so ordinary independent-trade p-values are not claimed.",
            "Only the predeclared primary candidate participates in the promotion gate; pattern",
            "and alternative-strategy rows are retained as exploratory diagnostics.",
            "",
            "Regardless of the result, coordinator and execution authorization remain false.",
            "The study cannot change Auto Suggest, official ML notes, the prospective shadow",
            "policy, or MT5 execution.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results(
    output_dir: Path,
    dataset: pd.DataFrame,
    result: dict[str, Any],
    contract: dict[str, Any],
    contract_path: Path,
    source_path: Path,
    source_rows: int,
) -> dict[str, Any]:
    output_dir = output_dir.expanduser().resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "decision_rows": output_dir / "decision_rows.parquet",
        "out_of_sample_predictions": output_dir / "out_of_sample_predictions.parquet",
        "fold_metrics": output_dir / "fold_metrics.csv",
        "strategy_summary": output_dir / "strategy_summary.csv",
        "pattern_diagnostics": output_dir / "pattern_diagnostics.csv",
        "fold_diagnostics": output_dir / "fold_diagnostics.json",
        "report": output_dir / "report.md",
    }
    dataset.to_parquet(paths["decision_rows"], index=False)
    result["predictions"].to_parquet(paths["out_of_sample_predictions"], index=False)
    result["fold_metrics"].to_csv(paths["fold_metrics"], index=False)
    result["strategy_summary"].to_csv(paths["strategy_summary"], index=False)
    result["pattern_diagnostics"].to_csv(paths["pattern_diagnostics"], index=False)
    paths["fold_diagnostics"].write_text(
        json.dumps(result["fold_diagnostics"], indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    source_sha = file_sha256(source_path)
    paths["report"].write_text(
        render_report(dataset, result, contract, source_path, source_sha),
        encoding="utf-8",
    )
    artifacts = {
        name: {
            "path": str(path),
            "sha256": file_sha256(path),
            "bytes": path.stat().st_size,
        }
        for name, path in paths.items()
    }
    manifest = {
        "contract": RESULT_CONTRACT,
        "createdAtUtc": utc_now(),
        "researchOnly": True,
        "source": {
            "path": str(source_path),
            "sha256": source_sha,
            "rows": int(source_rows),
        },
        "contractPath": str(contract_path.resolve()),
        "contractSha256": file_sha256(contract_path),
        "evaluatorPath": str(Path(__file__).resolve()),
        "evaluatorSha256": file_sha256(Path(__file__).resolve()),
        "pandasVersion": pd.__version__,
        "numpyVersion": np.__version__,
        "sklearnVersion": sklearn.__version__,
        "geometryMethodologyVersion": METHODOLOGY_VERSION,
        "decisionRows": int(len(dataset)),
        "decisionRange": {
            "start": pd.Timestamp(dataset["feature_available_time"].min()).isoformat(),
            "end": pd.Timestamp(dataset["feature_available_time"].max()).isoformat(),
        },
        "rawFeatureColumns": list(RAW_FEATURE_COLUMNS),
        "patternFeatureColumns": list(PATTERN_FEATURE_COLUMNS),
        "labelColumnsNeverFeatures": list(LABEL_COLUMNS),
        "foldDiagnostics": result["fold_diagnostics"],
        "probabilityDiagnostics": result["probability_diagnostics"],
        "promotion": result["promotion"],
        "guardrails": {
            "consumedByCandlestickRag": False,
            "consumedByJyotishRag": False,
            "consumedByAutoSuggest": False,
            "consumedByOfficialMlNotes": False,
            "consumedByShadowLedger": False,
            "coordinatorAuthorized": False,
            "executionAuthorized": False,
        },
        "warnings": contract["researchWarnings"],
        "artifacts": artifacts,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    return {**manifest, "manifestPath": str(manifest_path)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the frozen timestamp-safe USDJPY H1 candlestick walk-forward lab."
    )
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contract_path = args.contract.expanduser().resolve()
    contract = load_contract(contract_path)
    project_root = args.project_root.expanduser().resolve()
    source_path = (
        args.source.expanduser().resolve()
        if args.source is not None
        else resolve_source_path(contract, project_root)
    )
    output_dir = args.output_dir
    if output_dir is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_VALIDATION_ROOT / f"candlestick_usdjpy_v1_{timestamp}"
    frame = load_price_source(source_path, contract)
    dataset = build_decision_dataset(frame, contract)
    result = evaluate_walk_forward(dataset, contract)
    manifest = write_results(
        output_dir,
        dataset,
        result,
        contract,
        contract_path,
        source_path,
        len(frame),
    )
    print(
        json.dumps(
            {
                "manifest": manifest["manifestPath"],
                "decisionRows": manifest["decisionRows"],
                "promotion": manifest["promotion"],
            },
            indent=2,
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
