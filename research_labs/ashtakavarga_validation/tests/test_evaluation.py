from __future__ import annotations

import unittest

import pandas as pd

from ashtakavarga_lab.evaluation import pair_feature_frame, prepare_dataset, walk_forward_report


class EvaluationTests(unittest.TestCase):
    def evidence(self):
        rows = []
        for index, ts in enumerate(pd.date_range("2020-01-01", periods=100, freq="1D", tz="UTC")):
            rows.extend(
                [
                    {
                        "timestamp_utc": ts,
                        "profile_id": "base",
                        "seven_planet_sav_total": 200 + index % 5,
                        "jupiter_saturn_own_bav_sum": 9 + index % 2,
                    },
                    {
                        "timestamp_utc": ts,
                        "profile_id": "quote",
                        "seven_planet_sav_total": 196,
                        "jupiter_saturn_own_bav_sum": 8,
                    },
                ]
            )
        return pd.DataFrame(rows)

    def test_pair_feature_difference(self):
        frame = pair_feature_frame(self.evidence(), "base", "quote")
        self.assertEqual(frame.iloc[0]["sav_diff"], 4)
        self.assertEqual(frame.iloc[0]["js_diff"], 1)

    def test_walk_forward_is_expanding_and_non_trading(self):
        dates = pd.date_range("2020-01-01", periods=100, freq="1D", tz="UTC")
        price = pd.DataFrame(
            {
                "timestamp_utc": dates,
                "open": [100 + index for index in range(100)],
                "close": [100.5 + index for index in range(100)],
            }
        )
        dataset = prepare_dataset(price, self.evidence(), "base", "quote", [1, 5])
        report = walk_forward_report(dataset, [1, 5], fold_count=3, initial_train_fraction=0.5)
        self.assertFalse(report["trade_signal_enabled"])
        self.assertGreater(len(report["results"]), 0)
        for result in report["results"]:
            for fold in result["folds"]:
                self.assertLess(fold["train_end"], fold["test_start"])


if __name__ == "__main__":
    unittest.main()
