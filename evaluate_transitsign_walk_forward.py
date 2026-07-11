from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DEFAULT_INPUT = Path(
    r"D:\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet"
)
DEFAULT_OUTPUT_DIR = Path(r"D:\PycharmProjects\walk_forward_eval_transitsign_20260511")

EXCLUDED_EXACT = {
    "ml_outcome",
    "close_action",
    "close_reason",
    "close_time_utc",
    "close_price",
    "signed_return_pct",
    "mfe_pct",
    "mae_pct",
    "ignore_reason",
    "ignore_trade",
    "potential_trade",
    "close_after72",
    "after72_time_local",
    "ret_after_72h_pct",
    "ret_after_72h_dir",
    "edge_score",
    "hover_text",
    "touch_id",
    "event_id",
    # Candidate timestamps currently identify the bar open while these values
    # include information from inside/at the close of that same bar. Keep them
    # out until signal_time, decision_time and fill_time are stored separately.
    "open_touch",
    "high_touch",
    "low_touch",
    "close_touch",
    "entry_price",
}
EXCLUDED_PREFIXES = (
    "delta_",
    "y_",
    "ml_",
)
EXCLUDED_SUBSTRINGS = (
    "_json",
    "source_reference_time",
    "reference_time_ist",
    "cluster_end_time",
    "event_window_end",
    "aspect_regime_end",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purged walk-forward evaluation for transitsign trade candidates.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--initial-train-frac", type=float, default=0.40)
    parser.add_argument("--horizon-hours", type=float, default=72.0)
    parser.add_argument("--min-train-rows", type=int, default=200)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def safe_one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=5)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def is_feature_column(col: str) -> bool:
    if col in EXCLUDED_EXACT:
        return False
    lower = col.lower()
    if any(lower.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    if any(part in lower for part in EXCLUDED_SUBSTRINGS):
        return False
    if lower.endswith("_utc") or lower.endswith("_local"):
        return False
    if lower.endswith("_time") or lower.endswith("_time_tz"):
        return False
    return True


def load_candidates(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    df = df.copy()
    df["entry_time_utc"] = pd.to_datetime(df["entry_time_utc"], errors="coerce", utc=True)
    df["close_time_utc"] = pd.to_datetime(df["close_time_utc"], errors="coerce", utc=True)
    df = df[df["ml_outcome"].isin(["WIN", "LOSS"])].copy()
    df = df[df["entry_time_utc"].notna() & df["close_time_utc"].notna()].copy()
    df["target_win"] = df["ml_outcome"].map({"LOSS": 0, "WIN": 1}).astype(int)
    return df.sort_values(["entry_time_utc", "chart_timeframe", "touch_id"]).reset_index(drop=True)


def choose_features(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    candidates = [c for c in df.columns if is_feature_column(c)]
    numeric_cols: list[str] = []
    categorical_cols: list[str] = []
    for col in candidates:
        if col == "target_win":
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_bool_dtype(series):
            if series.notna().sum() > 0:
                numeric_cols.append(col)
            continue
        unique = series.fillna("").astype(str).nunique(dropna=False)
        if 1 < unique <= 60:
            categorical_cols.append(col)
    return numeric_cols, categorical_cols


def make_preprocessor(numeric_cols: list[str], categorical_cols: list[str]) -> ColumnTransformer:
    numeric_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", safe_one_hot_encoder()),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ],
        remainder="drop",
    )


def fold_slices(df: pd.DataFrame, folds: int, initial_train_frac: float) -> list[tuple[int, int]]:
    n = len(df)
    initial = max(1, int(n * initial_train_frac))
    remaining = max(0, n - initial)
    fold_size = max(1, int(np.ceil(remaining / max(1, folds))))
    out: list[tuple[int, int]] = []
    for start in range(initial, n, fold_size):
        stop = min(start + fold_size, n)
        if stop > start:
            out.append((start, stop))
    return out[:folds]


def model_specs(random_state: int) -> dict[str, Any]:
    return {
        "dummy_most_frequent": DummyClassifier(strategy="most_frequent"),
        "logistic_l2_balanced": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            solver="liblinear",
            random_state=random_state,
        ),
        "random_forest_balanced": RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=8,
            max_depth=5,
            class_weight="balanced_subsample",
            random_state=random_state,
            n_jobs=-1,
        ),
    }


def purged_training_rows(
    history: pd.DataFrame,
    test_start_time: pd.Timestamp,
    horizon: pd.Timedelta,
) -> tuple[pd.DataFrame, pd.Timestamp]:
    purge_cutoff = pd.Timestamp(test_start_time) - horizon
    train = history[history["close_time_utc"] <= purge_cutoff].copy()
    return train, purge_cutoff


def summarize_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=[1],
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "win_precision": float(precision[0]),
        "win_recall": float(recall[0]),
        "win_f1": float(f1[0]),
        "pred_win_rate": float(np.mean(y_pred == 1)),
    }


def direction_stats(df: pd.DataFrame, col: str) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for value, group in df.groupby(col, dropna=False):
        wins = group["target_win"].astype(int)
        out[str(value)] = {
            "rows": int(len(group)),
            "win_rate": float(wins.mean()) if len(group) else float("nan"),
        }
    return out


def main() -> None:
    args = parse_args()
    df = load_candidates(args.input)
    if len(df) < 100:
        raise SystemExit(f"Not enough WIN/LOSS candidates for walk-forward evaluation: {len(df)}")

    folds = fold_slices(df, int(args.folds), float(args.initial_train_frac))
    if not folds:
        raise SystemExit("No chronological folds could be created.")
    feature_reference = df.iloc[: folds[0][0]].copy()
    numeric_cols, categorical_cols = choose_features(feature_reference)
    specs = model_specs(int(args.random_state))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fold_records: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []

    for fold_idx, (test_start, test_stop) in enumerate(folds, start=1):
        test = df.iloc[test_start:test_stop].copy()
        test_start_time = test["entry_time_utc"].min()
        horizon = pd.Timedelta(hours=float(args.horizon_hours))
        train, purge_cutoff = purged_training_rows(df.iloc[:test_start].copy(), test_start_time, horizon)
        if len(train) < int(args.min_train_rows) or test.empty:
            continue

        y_train = train["target_win"].to_numpy(dtype=int)
        y_test = test["target_win"].to_numpy(dtype=int)
        for model_name, estimator in specs.items():
            preprocessor = make_preprocessor(numeric_cols, categorical_cols)
            pipe = Pipeline([("preprocess", preprocessor), ("model", estimator)])
            pipe.fit(train[numeric_cols + categorical_cols], y_train)
            pred = pipe.predict(test[numeric_cols + categorical_cols]).astype(int)
            proba = None
            if hasattr(pipe, "predict_proba"):
                try:
                    proba = pipe.predict_proba(test[numeric_cols + categorical_cols])[:, 1]
                except Exception:
                    proba = None
            metrics = summarize_predictions(y_test, pred)
            record = {
                "fold": fold_idx,
                "model": model_name,
                "train_rows": int(len(train)),
                "test_rows": int(len(test)),
                "test_start": str(test["entry_time_utc"].min()),
                "test_end": str(test["entry_time_utc"].max()),
                "purge_cutoff": str(purge_cutoff),
                "test_win_rate": float(np.mean(y_test == 1)),
                **metrics,
            }
            fold_records.append(record)
            pred_frame = test[
                [
                    "chart_timeframe",
                    "touch_id",
                    "entry_time_utc",
                    "ml_outcome",
                    "fx_hypothesis_direction",
                    "fx_doctrine_hypothesis_direction",
                    "fx_pair_net_score",
                    "fx_doctrine_pair_net_score",
                ]
            ].copy()
            pred_frame["fold"] = fold_idx
            pred_frame["model"] = model_name
            pred_frame["pred_win"] = pred
            if proba is not None:
                pred_frame["pred_win_proba"] = proba
            prediction_frames.append(pred_frame)

    if not fold_records:
        raise SystemExit("No folds met the minimum train/test requirements.")

    fold_df = pd.DataFrame(fold_records)
    pred_df = pd.concat(prediction_frames, ignore_index=True) if prediction_frames else pd.DataFrame()
    model_summary = (
        fold_df.groupby("model")
        .agg(
            folds=("fold", "count"),
            test_rows=("test_rows", "sum"),
            accuracy=("accuracy", "mean"),
            balanced_accuracy=("balanced_accuracy", "mean"),
            win_precision=("win_precision", "mean"),
            win_recall=("win_recall", "mean"),
            win_f1=("win_f1", "mean"),
            pred_win_rate=("pred_win_rate", "mean"),
            test_win_rate=("test_win_rate", "mean"),
        )
        .reset_index()
        .sort_values(["balanced_accuracy", "accuracy"], ascending=False)
    )

    eligible = df[df["ml_outcome"].isin(["WIN", "LOSS"])].copy()
    summary = {
        "input": str(args.input),
        "rows_total_win_loss": int(len(df)),
        "time_range": {
            "start": str(df["entry_time_utc"].min()),
            "end": str(df["entry_time_utc"].max()),
        },
        "features": {
            "numeric": len(numeric_cols),
            "categorical": len(categorical_cols),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
        },
        "folds": fold_records,
        "model_summary": model_summary.to_dict(orient="records"),
        "rule_direction_win_rates": {
            "fx_hypothesis_direction": direction_stats(eligible, "fx_hypothesis_direction"),
            "fx_doctrine_hypothesis_direction": direction_stats(eligible, "fx_doctrine_hypothesis_direction"),
        },
        "purge_rule": (
            "expanding walk-forward; train rows must close at or before test_start minus horizon_hours; "
            "same-bar OHLC/entry-price and future/outcome columns are excluded"
        ),
        "research_warning": (
            "Feature count remains large relative to sample size. Results are exploratory until a preregistered "
            "availability-timestamped feature manifest and untouched holdout are used."
        ),
    }

    fold_path = args.output_dir / "fold_metrics.csv"
    pred_path = args.output_dir / "predictions.csv"
    summary_path = args.output_dir / "summary.json"
    model_summary_path = args.output_dir / "model_summary.csv"
    fold_df.to_csv(fold_path, index=False)
    pred_df.to_csv(pred_path, index=False)
    model_summary.to_csv(model_summary_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    print(json.dumps({
        "rows_total_win_loss": int(len(df)),
        "folds": int(fold_df["fold"].nunique()),
        "outputs": {
            "summary": str(summary_path),
            "model_summary": str(model_summary_path),
            "fold_metrics": str(fold_path),
            "predictions": str(pred_path),
        },
        "model_summary": summary["model_summary"],
        "rule_direction_win_rates": summary["rule_direction_win_rates"],
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
