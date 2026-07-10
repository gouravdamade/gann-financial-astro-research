from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from ashtakavarga_lab.dasha import DASHA_YEARS, antardasha_periods, dasha_at, mahadasha_periods
from ashtakavarga_lab.kas import corrected_event_worksheet, event_houses, inverse_aspect_points


ROOT = Path(__file__).resolve().parents[1]


class CorrectedKasWorksheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(
            (ROOT / "fixtures" / "kas_lesson7_marriage_corrected.json").read_text(encoding="utf-8")
        )
        cls.report = corrected_event_worksheet(
            cls.fixture["bav"],
            cls.fixture["planet_signs"],
            cls.fixture["lagna_sign"],
            cls.fixture["house_b"],
        )

    def test_event_house_rotation(self):
        self.assertEqual(event_houses(7), self.fixture["expected"]["event_houses"])

    def test_corrected_lesson7_rows(self):
        mapping = {
            "row3": "row3_basic_strength",
            "row5": "row5_four_ten_transfer",
            "row8": "row8_de_bonus",
            "row12": "row12_house_aspects",
            "row16": "row16_planet_aspects",
            "row17": "row17_final_strength",
        }
        for expected_name, actual_name in mapping.items():
            self.assertEqual(self.report[actual_name], self.fixture["expected"][expected_name], expected_name)
        self.assertEqual(self.report["ranking"], self.fixture["expected"]["ranking"])

    def test_corrections_are_auditable(self):
        transfers = {(item["donor"], item["recipient"]) for item in self.report["four_ten_audit"]}
        self.assertEqual(transfers, {("JUPITER", "SUN"), ("JUPITER", "SATURN")})
        jupiter_house = next(item for item in self.report["house_aspect_audit"] if item["planet"] == "JUPITER")
        self.assertTrue(jupiter_house["own_house_exemption"])
        venus_aspect = next(item for item in self.report["planet_aspect_audit"] if item["target"] == "VENUS")
        self.assertTrue(venus_aspect["de_lord_exemption"])

    def test_inverse_aspect_has_exact_four_neutral(self):
        self.assertEqual([inverse_aspect_points(value) for value in range(9)], [8, 7, 6, 5, 0, -5, -6, -7, -8])


class VimshottariTests(unittest.TestCase):
    def test_cycle_lengths_and_antardasha_partition(self):
        birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
        periods = mahadasha_periods(birth, moon_longitude=0.0, cycles=1)
        self.assertEqual([item["lord"] for item in periods], list(DASHA_YEARS))
        self.assertAlmostEqual(sum((item["end"] - item["start"]).days for item in periods) / 365.2425, 120, places=1)
        antars = antardasha_periods(periods[0])
        self.assertEqual(len(antars), 9)
        self.assertEqual(antars[0]["start"], periods[0]["start"])
        self.assertEqual(antars[-1]["end"], periods[0]["end"])
        self.assertTrue(all(len(item["sectors"]) == 3 for item in antars))

    def test_lookup_returns_sector_without_selecting_delay_rule(self):
        birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
        result = dasha_at(birth, 0.0, birth)
        self.assertIn(result["sector"]["label"], {"no_delay", "moderate_delay", "full_delay"})


if __name__ == "__main__":
    unittest.main()
