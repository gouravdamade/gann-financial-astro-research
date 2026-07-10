from __future__ import annotations

import unittest

from ashtakavarga_lab.config import load_config, profile
from ashtakavarga_lab.ephemeris import configure, natal_context
from ashtakavarga_lab.evidence import build_daily_evidence, natal_tables


class EphemerisEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        configure(cls.config)

    def test_reference_natal_tables_validate(self):
        for profile_id in ("usd_reference", "jpy_reference", "btc_van_nuys"):
            table = natal_tables(self.config, profile_id)
            self.assertTrue(table["validation"]["passed"])
            self.assertEqual(sum(table["sav"]), 337)

    def test_ascendant_is_present_and_sign_bounded(self):
        context = natal_context("usd_reference", profile(self.config, "usd_reference"))
        self.assertIn("LAGNA", context["signs"])
        self.assertTrue(1 <= context["signs"]["LAGNA"] <= 12)

    def test_daily_evidence_is_profile_separated_and_non_trading(self):
        frame = build_daily_evidence(
            self.config,
            ["usd_reference", "jpy_reference"],
            "2025-01-01",
            "2025-01-04",
        )
        self.assertEqual(len(frame), 6)
        self.assertEqual(set(frame["profile_id"]), {"usd_reference", "jpy_reference"})
        self.assertEqual(set(frame["trade_signal_enabled"]), {0})
        self.assertTrue(frame["seven_planet_sav_total"].between(0, 392).all())


if __name__ == "__main__":
    unittest.main()
