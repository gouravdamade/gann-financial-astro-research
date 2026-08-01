import unittest

from sbc.visualization_modes import VISUALIZATION_MODE_IDS, visualization_mode_contract


class VisualizationModeContractTests(unittest.TestCase):
    def test_modes_remain_non_execution(self) -> None:
        for mode in VISUALIZATION_MODE_IDS:
            contract = visualization_mode_contract(mode)
            self.assertFalse(contract["guardrails"]["executionAllowed"])
            self.assertFalse(contract["guardrails"]["automaticOrderPlacement"])

    def test_calibrated_mode_does_not_invent_parameters(self) -> None:
        contract = visualization_mode_contract("CALIBRATED_RESEARCH")
        self.assertEqual(contract["evidenceStatus"], "SOURCE_MISSING")
        self.assertEqual(contract["profile"]["parameterCount"], 0)

    def test_baseline_has_no_timing_geometry(self) -> None:
        contract = visualization_mode_contract("SOURCE_ONLY_BASELINE")
        self.assertTrue(contract["allowFixedPhasor"])
        self.assertFalse(contract["allowTimingGeometry"])

