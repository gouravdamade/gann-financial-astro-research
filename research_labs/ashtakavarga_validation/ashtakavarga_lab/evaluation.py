from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


TIMESTAMP_CANDIDATES = ("time", "timestamp", "datetime", "date", "timestamp_utc")


def load_price(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    frame = pd.read_parquet(source) if source.suffix.lower() in {".parquet", ".pq"} else pd.read_csv(source)
    if isinstance(frame.index, pd.DatetimeIndex):
        frame = frame.reset_index()
    timestamp_column = next((name for name in TIMESTAMP_CANDIDATES if name in frame.columns), None)
    if timestamp_column is None:
        raise ValueError(f"Could not find a timestamp column in {source}; columns={list(frame.columns)}")
    required = {"open", "close"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Price file must contain {sorted(required)}")
    timestamps = pd.to_datetime(frame[timestamp_column], utc=True, errors="coerce")
    work = frame.assign(timestamp_utc=timestamps).dropna(subset=["timestamp_utc", "open", "close"])
    work = work.set_index("timestamp_utc").sort_index()
    daily = work.resample("1D").agg(open=("open", "first"), close=("close", "last"))
    return daily.dropna().reset_index()


def load_evidence(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    frame = pd.read_parquet(source) if source.suffix.lower() in {".parquet", ".pq"} else pd.read_csv(source)
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    return frame.dropna(subset=["timestamp_utc", "profile_id"]).copy()


def pair_feature_frame(
    evidence: pd.DataFrame,
    base_profile: str,
    quote_profile: str,
) -> pd.DataFrame:
    value_columns = ["seven_planet_sav_total", "jupiter_saturn_own_bav_sum"]
    filtered = evidence[evidence["profile_id"].isin([base_profile, quote_profile])].copy()
    if set(filtered["profile_id"].unique()) != {base_profile, quote_profile}:
        raise ValueError("Evidence is missing the requested base or quote profile")
    pivot = filtered.pivot(index="timestamp_utc", columns="profile_id", values=value_columns)
    out = pd.DataFrame(index=pivot.index)
    out["sav_base"] = pivot[("seven_planet_sav_total", base_profile)]
    out["sav_quote"] = pivot[("seven_planet_sav_total", quote_profile)]
    out["sav_diff"] = out["sav_base"] - out["sav_quote"]
    out["js_base"] = pivot[("jupiter_saturn_own_bav_sum", base_profile)]
    out["js_quote"] = pivot[("jupiter_saturn_own_bav_sum", quote_profile)]
    out["js_diff"] = out["js_base"] - out["js_quote"]
    return out.reset_index()


def prepare_dataset(
    price: pd.DataFrame,
    evidence: pd.DataFrame,
    base_profile: str,
    quote_profile: str,
    horizons: list[int],
) -> pd.DataFrame:
    features = pair_feature_frame(evidence, base_profile, quote_profile)
    merged = price.merge(features, on="timestamp_utc", how="inner").sort_values("timestamp_utc").reset_index(drop=True)
    for horizon in horizons:
        if int(horizon) < 1:
            raise ValueError("Horizons must be positive trading-day counts")
        merged[f"return_{horizon}d"] = merged["close"].shift(-(int(horizon) - 1)) / merged["open"] - 1.0
        merged[f"past_return_{horizon}d"] = merged["close"].shift(1) / merged["close"].shift(int(horizon) + 1) - 1.0
    return merged


def _safe_corr(left: pd.Series, right: pd.Series) -> float:
    if left.nunique(dropna=True) < 2 or right.nunique(dropna=True) < 2:
        return 0.0
    value = left.corr(right)
    return 0.0 if pd.isna(value) else float(value)


def _wilson_interval(successes: int, observations: int, z: float = 1.959963984540054) -> tuple[float, float] | None:
    if observations <= 0:
        return None
    p = successes / observations
    denominator = 1.0 + z * z / observations
    center = (p + z * z / (2.0 * observations)) / denominator
    margin = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * observations)) / observations) / denominator
    return center - margin, center + margin


def _folds(length: int, count: int, initial_fraction: float, gap: int) -> list[tuple[np.ndarray, np.ndarray]]:
    initial = max(1, int(length * float(initial_fraction)))
    available = length - initial
    test_size = max(1, available // int(count))
    folds = []
    for fold in range(int(count)):
        train_end = initial + fold * test_size
        test_start = train_end + int(gap)
        test_end = length if fold == int(count) - 1 else min(length, test_start + test_size)
        if test_start >= test_end:
            continue
        folds.append((np.arange(0, train_end), np.arange(test_start, test_end)))
    return folds


def walk_forward_report(
    dataset: pd.DataFrame,
    horizons: list[int],
    fold_count: int = 5,
    initial_train_fraction: float = 0.5,
) -> dict[str, Any]:
    results = []
    for horizon in horizons:
        for feature in ("sav_diff", "js_diff", f"past_return_{int(horizon)}d"):
            target = f"return_{int(horizon)}d"
            work = dataset[["timestamp_utc", feature, target]].dropna().reset_index(drop=True)
            fold_rows = []
            for fold_id, (train_index, test_index) in enumerate(
                _folds(len(work), fold_count, initial_train_fraction, gap=int(horizon))
            ):
                train = work.iloc[train_index]
                test = work.iloc[test_index]
                learned_orientation = 1 if _safe_corr(train[feature], train[target]) >= 0 else -1
                for mapping, orientation in (("fixed_positive", 1), ("learned_train_only", learned_orientation)):
                    nonzero = test[feature] != 0
                    scored = test[nonzero].copy()
                    if scored.empty:
                        continue
                    descriptive_prediction = np.sign(scored[feature].to_numpy(dtype=float)) * orientation
                    descriptive_actual = np.sign(scored[target].to_numpy(dtype=float))
                    non_overlapping = scored.iloc[:: int(horizon)].copy()
                    prediction = np.sign(non_overlapping[feature].to_numpy(dtype=float)) * orientation
                    actual = np.sign(non_overlapping[target].to_numpy(dtype=float))
                    strategy_return = prediction * non_overlapping[target].to_numpy(dtype=float)
                    hit_count = int(np.sum(prediction == actual))
                    fold_rows.append(
                        {
                            "fold": fold_id + 1,
                            "mapping": mapping,
                            "orientation": orientation,
                            "train_end": train["timestamp_utc"].max().isoformat(),
                            "test_start": scored["timestamp_utc"].min().isoformat(),
                            "test_end": scored["timestamp_utc"].max().isoformat(),
                            "observations": int(len(scored)),
                            "descriptive_hit_rate_overlapping": float(np.mean(descriptive_prediction == descriptive_actual)),
                            "non_overlapping_observations": int(len(non_overlapping)),
                            "hit_count": hit_count,
                            "hit_rate": float(np.mean(prediction == actual)),
                            "mean_strategy_return_pct": float(np.mean(strategy_return) * 100.0),
                            "sum_strategy_return_pct": float(np.sum(strategy_return) * 100.0),
                        }
                    )
            for mapping in ("fixed_positive", "learned_train_only"):
                selected = [row for row in fold_rows if row["mapping"] == mapping]
                total_observations = sum(row["non_overlapping_observations"] for row in selected)
                hit_count = sum(row["hit_count"] for row in selected)
                weighted_hit = hit_count / total_observations if total_observations else None
                interval = _wilson_interval(hit_count, total_observations)
                z_score = (
                    (hit_count - total_observations / 2.0) / math.sqrt(total_observations / 4.0)
                    if total_observations
                    else None
                )
                results.append(
                    {
                        "feature": feature,
                        "horizon_trading_days": int(horizon),
                        "mapping": mapping,
                        "folds": selected,
                        "fold_count": len(selected),
                        "non_overlapping_observations": total_observations,
                        "hit_count": hit_count,
                        "weighted_hit_rate": weighted_hit,
                        "hit_rate_wilson_95_low": interval[0] if interval else None,
                        "hit_rate_wilson_95_high": interval[1] if interval else None,
                        "hit_rate_normal_pvalue_vs_50": math.erfc(abs(z_score) / math.sqrt(2.0)) if z_score is not None else None,
                        "median_fold_mean_strategy_return_pct": (
                            float(np.median([row["mean_strategy_return_pct"] for row in selected])) if selected else None
                        ),
                        "positive_mean_return_folds": sum(
                            row["mean_strategy_return_pct"] > 0 for row in selected
                        ),
                    }
                )
    return {
        "status": "exploratory_no_costs_no_promotion",
        "trade_signal_enabled": False,
        "method": "expanding_chronological_folds_with_horizon_gap",
        "dataset_rows": int(len(dataset)),
        "start": dataset["timestamp_utc"].min().isoformat() if len(dataset) else None,
        "end": dataset["timestamp_utc"].max().isoformat() if len(dataset) else None,
        "results": results,
        "limitations": [
            "outside-calculator certification is incomplete",
            "transaction costs and slippage are not included",
            "multiple-testing correction and randomized placebos are pending",
            "reference-chart choices are hypotheses",
            "price momentum is a simple comparison baseline, not a production strategy",
            "results cannot be used by the main trading pipeline",
        ],
    }
