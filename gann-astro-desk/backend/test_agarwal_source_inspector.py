from __future__ import annotations

import json
import unittest
from pathlib import Path

from agarwal_source_inspector import build_agarwal_source_profile


class AgarwalSourceInspectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parents[2]
        cls.profile = build_agarwal_source_profile(cls.project_root)

    def test_profile_is_immutable_geometry_strength_scope(self) -> None:
        profile = self.profile
        self.assertEqual(profile["profileId"], "AGARWAL_2000_GEOMETRY_STRENGTH_INSPECTOR_V1")
        self.assertEqual(profile["geometry"]["contract"], "AGARWAL_PAGE145_CORE_9X9_V1")
        self.assertFalse(profile["executionAllowed"])
        self.assertFalse(profile["guardrails"]["polarityAllowed"])
        self.assertFalse(profile["guardrails"]["scoreAggregationAllowed"])
        self.assertFalse(profile["guardrails"]["fieldsInfluenceAllowed"])
        self.assertFalse(profile["guardrails"]["autoSuggestAllowed"])
        self.assertFalse(profile["guardrails"]["mlAllowed"])

    def test_all_81_cells_and_orientation_come_from_fixture(self) -> None:
        geometry = self.profile["geometry"]
        cells = geometry["cells"]
        self.assertEqual(len(cells), 81)
        self.assertEqual(len({cell["coordinate"]["label"] for cell in cells}), 81)
        self.assertEqual(len({cell["vargaNumber"] for cell in cells}), 81)
        self.assertEqual(geometry["orientation"], {
            "east": "top",
            "west": "bottom",
            "north": "left",
            "south": "right",
        })
        self.assertTrue(all(cell["sourceStatus"] == "SOURCE_CLOSED_TWO_PASS_AGREED" for cell in cells))
        self.assertEqual(geometry["p144Reconciliation"]["status"], "MATCH")

    def test_strength_and_financial_material_remain_source_only(self) -> None:
        strength = self.profile["strengthEvidence"]
        self.assertEqual(len(strength["rows"]), 7)
        self.assertEqual(strength["aggregationStatus"], "SOURCE_RECORD_ONLY_NO_MASTER_SCORE")
        self.assertEqual(self.profile["financialStatus"]["classification"], "FINANCIAL_HYPOTHESIS_LEDGER_ONLY")
        self.assertTrue(all(label in self.profile["financialStatus"]["labels"] for label in (
            "RESEARCH HYPOTHESIS",
            "NOT VALIDATED",
            "NOT FX-MAPPED",
            "NOT EXECUTABLE",
        )))

    def test_vedha_is_explicitly_unavailable_and_no_private_locator_is_exposed(self) -> None:
        self.assertEqual(self.profile["vedhaStatus"], "DEPENDENCY_NOT_READY")
        self.assertEqual(len(self.profile["vedhaDependencies"]), 8)
        serialized = json.dumps(self.profile)
        self.assertNotIn("C:/Users/ADMIN/Desktop", serialized)
        self.assertNotIn("D:/GannFinancialAstro/sources/private", serialized)
        self.assertNotIn("ChiStaBo", serialized)

    def test_sidecar_packages_fixture_adapter_without_private_photographs(self) -> None:
        spec = (Path(__file__).resolve().parents[1] / "packaging" / "gann_backend_sidecar.spec").read_text(encoding="utf-8")
        self.assertIn('"agarwal_source_inspector"', spec)
        self.assertIn('project_root / "configs" / "sbc"', spec)
        self.assertNotIn("1000413731.jpg", spec)
        self.assertNotIn("1000413730.jpg", spec)


if __name__ == "__main__":
    unittest.main()
