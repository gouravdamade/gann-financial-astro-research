from __future__ import annotations

import json
import random
import unittest
from pathlib import Path

from ashtakavarga_lab.constants import CONTRIBUTORS, EXPECTED_BAV_TOTALS, PLANETS
from ashtakavarga_lab.core import compute_bav, compute_sav, transit_evidence, validate_chart
from ashtakavarga_lab.external_check import compare_external_export
from ashtakavarga_lab.config import load_config


ROOT = Path(__file__).resolve().parents[1]


class CoreTests(unittest.TestCase):
    def fixture(self):
        return json.loads((ROOT / "fixtures" / "bv_raman_standard_horoscope.json").read_text(encoding="utf-8"))

    def test_published_standard_horoscope(self):
        fixture = self.fixture()
        bav = compute_bav(fixture["sign_positions"])
        sav = compute_sav(bav)
        self.assertEqual({planet: list(bav[planet]) for planet in PLANETS}, fixture["expected_bav"])
        self.assertEqual(list(sav), fixture["expected_sav"])

    def test_row_and_grand_totals_do_not_depend_on_chart(self):
        rng = random.Random(42)
        for _ in range(100):
            positions = {body: rng.randint(1, 12) for body in CONTRIBUTORS}
            bav = compute_bav(positions)
            sav = compute_sav(bav)
            self.assertEqual({planet: sum(bav[planet]) for planet in PLANETS}, EXPECTED_BAV_TOTALS)
            self.assertEqual(sum(sav), 337)
            self.assertTrue(validate_chart(bav, sav)["passed"])

    def test_nodes_and_outer_planets_are_rejected(self):
        positions = {body: 1 for body in CONTRIBUTORS}
        positions["RAHU"] = 1
        with self.assertRaises(ValueError):
            compute_bav(positions)

    def test_transit_evidence_uses_own_bav_and_sav(self):
        fixture = self.fixture()
        bav = compute_bav(fixture["sign_positions"])
        sav = compute_sav(bav)
        signs = {planet: index + 1 for index, planet in enumerate(PLANETS)}
        result = transit_evidence(bav, sav, signs)
        expected_sav = sum(sav[index] for index in range(7))
        expected_js = bav["JUPITER"][5] + bav["SATURN"][6]
        self.assertEqual(result["seven_planet_sav_total"], expected_sav)
        self.assertEqual(result["sav_distance_from_196"], expected_sav - 196)
        self.assertEqual(result["jupiter_saturn_own_bav_sum"], expected_js)
        self.assertEqual(result["js_distance_from_8"], expected_js - 8)

    def test_external_calculator_exact_comparison(self):
        payload = {
            "calculator_name": "test fixture",
            "calculator_version": "1",
            "profile_id": "usd_reference",
            "ayanamsa": "Raman",
            "reductions": "unreduced",
        }
        # Use independently calculated local profile values to test the comparator mechanics.
        from ashtakavarga_lab.evidence import natal_tables

        local = natal_tables(load_config(), "usd_reference")
        payload["bav"] = local["bav"]
        payload["sav"] = local["sav"]
        report = compare_external_export(load_config(), payload)
        self.assertTrue(report["passed"])
        self.assertEqual(report["difference_count"], 0)
        payload["bav"] = {planet: list(values) for planet, values in local["bav"].items()}
        payload["bav"]["SUN"][0] += 1
        mismatch = compare_external_export(load_config(), payload)
        self.assertFalse(mismatch["passed"])
        self.assertEqual(mismatch["differences"][0]["planet"], "SUN")
        self.assertEqual(mismatch["differences"][0]["sign"], "ARIES")


if __name__ == "__main__":
    unittest.main()
