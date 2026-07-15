from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from candlestick_agent.usdjpy_walk_forward import (
    DEFAULT_CONTRACT_PATH,
    PATTERN_FEATURE_COLUMNS,
    RAW_FEATURE_COLUMNS,
    build_decision_dataset,
    evaluate_walk_forward,
    load_contract,
    load_price_source,
    probability_support_diagnostics,
    purged_training_rows,
    strategy_metrics,
)


def synthetic_price(rows: int = 120, *, spread_points: float = 0.0) -> pd.DataFrame:
    index = pd.date_range("2020-01-01T00:00:00Z", periods=rows, freq="h")
    step = np.sin(np.arange(rows) / 3.0) * 0.025 + np.cos(np.arange(rows) / 11.0) * 0.01
    close = 145.0 + np.cumsum(step)
    open_ = np.concatenate(([145.0], close[:-1]))
    high = np.maximum(open_, close) + 0.025 + (np.arange(rows) % 3) * 0.002
    low = np.minimum(open_, close) - 0.023 - (np.arange(rows) % 4) * 0.002
    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "tick_volume": np.arange(rows) + 100,
            "spread": np.full(rows, spread_points),
            "real_volume": np.zeros(rows),
        },
        index=index,
    )


def lab_contract() -> dict:
    contract = load_contract(DEFAULT_CONTRACT_PATH)
    contract = copy.deepcopy(contract)
    contract["decision"]["holdingBars"] = 3
    contract["splits"]["folds"] = 3
    contract["splits"]["initialTrainFraction"] = 0.5
    contract["splits"]["embargoBars"] = 3
    contract["promotionGate"]["bootstrapSamples"] = 50
    return contract


class UsdJpyWalkForwardTests(unittest.TestCase):
    def test_dataset_uses_next_bar_entry_and_frozen_costs(self) -> None:
        contract = lab_contract()
        dataset = build_decision_dataset(synthetic_price(96), contract)
        self.assertEqual(len(dataset), 96 - 21 - 3)
        self.assertTrue((dataset["entry_time"] >= dataset["feature_available_time"]).all())
        self.assertTrue((dataset["label_available_time"] > dataset["entry_time"]).all())
        self.assertTrue(np.allclose(dataset["future_spread_pips"], 1.0))
        self.assertTrue(np.allclose(dataset["future_total_cost_pips"], 1.4))
        first = dataset.iloc[0]
        source = synthetic_price(96)
        decision_index = int(first["source_row_number"])
        self.assertEqual(first["future_entry_price"], source.iloc[decision_index + 1]["open"])
        self.assertEqual(first["future_exit_price"], source.iloc[decision_index + 3]["close"])

    def test_decision_features_are_prefix_invariant(self) -> None:
        contract = lab_contract()
        full = build_decision_dataset(synthetic_price(110), contract)
        prefix = build_decision_dataset(synthetic_price(72), contract)
        source_row = 40
        full_row = full.loc[full["source_row_number"] == source_row].iloc[0]
        prefix_row = prefix.loc[prefix["source_row_number"] == source_row].iloc[0]
        columns = [
            *RAW_FEATURE_COLUMNS,
            *PATTERN_FEATURE_COLUMNS,
            "body_momentum_signal",
            "momentum_5bar_signal",
            "raw_wick_reversal_signal",
            "named_pattern_rule_signal",
            "pattern_bias_json",
        ]
        for column in columns:
            if isinstance(full_row[column], (float, np.floating)):
                self.assertAlmostEqual(full_row[column], prefix_row[column], places=10)
            else:
                self.assertEqual(full_row[column], prefix_row[column])

    def test_purge_and_embargo_use_label_availability(self) -> None:
        contract = lab_contract()
        dataset = build_decision_dataset(synthetic_price(110), contract)
        test_start_index = 40
        test_start = pd.Timestamp(dataset.iloc[test_start_index]["feature_available_time"])
        train, cutoff, removed = purged_training_rows(
            dataset,
            test_start_index,
            test_start,
            pd.Timedelta(hours=3),
        )
        self.assertGreater(removed, 0)
        self.assertLessEqual(pd.Timestamp(train["label_available_time"].max()), cutoff)

    def test_walk_forward_folds_are_chronological_and_locked(self) -> None:
        contract = lab_contract()
        dataset = build_decision_dataset(synthetic_price(180), contract)
        result = evaluate_walk_forward(dataset, contract)
        self.assertEqual(len(result["fold_diagnostics"]), 3)
        for fold in result["fold_diagnostics"]:
            self.assertLessEqual(
                pd.Timestamp(fold["max_train_label_available"]),
                pd.Timestamp(fold["purge_cutoff"]),
            )
            self.assertLess(
                pd.Timestamp(fold["max_train_label_available"]),
                pd.Timestamp(fold["test_start"]),
            )
        promotion = result["promotion"]
        self.assertFalse(promotion["coordinator_authorized"])
        self.assertFalse(promotion["execution_authorized"])

    def test_strategy_metrics_charge_round_trip_cost(self) -> None:
        frame = pd.DataFrame(
            {
                "future_gross_long_pips": [2.0, -1.0],
                "future_total_cost_pips": [1.4, 1.4],
            }
        )
        metrics = strategy_metrics(frame, np.array([1, -1]))
        self.assertEqual(metrics["trades"], 2)
        self.assertAlmostEqual(metrics["mean_net_pips_per_trade"], 0.1, places=10)

    def test_zero_signal_probability_support_is_explained(self) -> None:
        contract = lab_contract()
        frame = pd.DataFrame(
            {
                "fold": [1, 1, 2, 2],
                "probability_up_named_pattern_logistic_v1": [0.48, 0.49, 0.51, 0.52],
                "signal_named_pattern_logistic_v1": [0, 0, 0, 0],
            }
        )
        diagnostics = probability_support_diagnostics(
            frame,
            "named_pattern_logistic_v1",
            contract,
        )
        self.assertEqual(diagnostics["short_signals"], 0)
        self.assertEqual(diagnostics["long_signals"], 0)
        self.assertEqual(diagnostics["abstentions"], 4)
        self.assertIn("deterministic abstention", diagnostics["explanation"])

    def test_source_hash_mismatch_is_rejected(self) -> None:
        contract = lab_contract()
        contract["source"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "prices.parquet"
            synthetic_price(40).to_parquet(path)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                load_price_source(path, contract)

    def test_contract_cannot_enable_execution(self) -> None:
        contract = lab_contract()
        contract["promotionGate"]["executionAuthorization"] = True
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "contract.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Execution authorization"):
                load_contract(path)


if __name__ == "__main__":
    unittest.main()
