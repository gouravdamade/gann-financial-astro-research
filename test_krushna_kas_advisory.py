from __future__ import annotations

import unittest

from krushna_kas_advisory import KrushnaKasAdvisoryEngine


class KrushnaKasAdvisoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = KrushnaKasAdvisoryEngine().advisory_at("2025-04-04T00:00:00Z")

    def test_all_twelve_houses_are_reported(self):
        self.assertEqual(len(self.result["house_votes"]), 12)
        self.assertEqual(
            self.result["bullish_house_count"]
            + self.result["bearish_house_count"]
            + self.result["neutral_house_count"],
            12,
        )

    def test_every_execution_and_learning_path_is_locked(self):
        self.assertEqual(self.result["evidence_only"], 1)
        for key in (
            "trade_signal_enabled",
            "trade_override_allowed",
            "auto_suggest_input",
            "ml_training_input",
            "mt5_input",
        ):
            self.assertEqual(self.result[key], 0, key)

    def test_advisory_is_labeled_as_uncertified(self):
        self.assertEqual(self.result["status"], "experimental_suggestion_only")
        self.assertEqual(self.result["validation_status"], "first_usdjpy_run_no_robust_edge")
        self.assertIn(self.result["suggestion"], {"BULLISH", "BEARISH", "MIXED", "NEUTRAL"})


if __name__ == "__main__":
    unittest.main()
