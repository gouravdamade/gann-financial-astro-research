from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import unittest

import swisseph as swe
import yaml

from cgvo_service import (
    CgvoRequestError,
    VARAHAMIHIRA_CHITRA_FRAME_ID,
    _chitra_180_offset,
    _s1b_fixtures,
    build_cgvo_s1b_source_audit,
    build_cgvo_status,
    build_cgvo_workbench,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CgvoS1bSourceAuditTests(unittest.TestCase):
    def test_s1b_source_ledgers_parse_and_keep_all_product_paths_locked(self) -> None:
        names = [
            "VARAHAMIHIRA_ABSOLUTE_FRAME_AUDIT_V1.yaml",
            "VARAHAMIHIRA_ABSOLUTE_FRAME_AUDIT_V2.yaml",
            "PANCHASIDDHANTIKA_FIXED_STAR_SOURCE_LEDGER_V1.yaml",
            "VARAHAMIHIRA_SOLAR_ECLIPSE_PHASE_MAPPING_V1.yaml",
            "VARAHAMIHIRA_LUNAR_ECLIPSE_PHASE_MAPPING_V1.yaml",
            "VARAHAMIHIRA_FIRMAMENT_SOURCE_ADJUDICATION_V2.yaml",
            "CGVO_S1B_READINESS_MATRIX_V1.yaml",
            "CGVO_S1B_R1_READINESS_MATRIX.yaml",
        ]
        for name in names:
            payload = yaml.safe_load((PROJECT_ROOT / "configs" / "research" / "cgvo" / name).read_text(encoding="utf-8"))
            self.assertIsInstance(payload, dict)
            self.assertNotIn("d:\\", str(payload).lower())
            self.assertFalse(payload["guardrails"]["executionAllowed"])

    def test_explicit_chitra_candidates_do_not_replace_the_existing_selected_frame(self) -> None:
        fixtures = _s1b_fixtures(PROJECT_ROOT)
        audit = fixtures["absoluteFrameAudit"]
        self.assertEqual(audit["currentActiveCandidate"]["profileId"], VARAHAMIHIRA_CHITRA_FRAME_ID)
        self.assertFalse(audit["currentActiveCandidate"]["defaultAuthorized"])
        candidate_ids = [item["profileId"] for item in audit["candidateProfiles"]]
        self.assertEqual(candidate_ids[:5], [
            "CHITRA_180_APPARENT_TRUE_EQUINOX",
            "CHITRA_180_APPARENT_MEAN_EQUINOX",
            "CHITRA_180_TRUE_GEOMETRIC_TRUE_EQUINOX",
            "CHITRA_180_TRUE_NOABERR_NODEFL",
            "CHITRA_180_TRUE_NOABERR_NODEFL_MEAN_EQUINOX",
        ])
        with self.assertRaisesRegex(CgvoRequestError, "absoluteFrameProfileId"):
            build_cgvo_workbench(PROJECT_ROOT, {
                "eventType": "SOLAR", "globalMaxUtc": "2027-08-02T10:06:41Z",
                "absoluteFrameProfileId": "CHITRA_180_TRUE_GEOMETRIC_TRUE_EQUINOX",
                "latitude": 23.1765, "longitude": 75.7885, "timezone": "Asia/Kolkata",
            })

    def test_modern_audit_is_epoch_explicit_and_refuses_magha_averaging(self) -> None:
        output = build_cgvo_s1b_source_audit(PROJECT_ROOT)
        self.assertEqual(len(output["epochs"]), 8)
        self.assertFalse(output["maghaComparison"]["crossAnchorAverageAllowed"])
        for epoch in output["epochs"]:
            profiles = {record["profileId"]: record for record in epoch["profiles"]}
            self.assertEqual(len(profiles), 6)
            apparent = profiles["CHITRA_180_APPARENT_TRUE_EQUINOX"]
            self.assertEqual(apparent["calculationStatus"], "MODERN_AUDIT_CALCULATED")
            self.assertIsNotNone(apparent["spicaTropicalLongitudeDeg"])
            self.assertIsNotNone(apparent["derivedZeroMeshaDeg"])
            self.assertEqual(apparent["requestedFlags"], swe.FLG_SWIEPH)
            self.assertEqual(apparent["returnedFlags"], swe.FLG_SWIEPH)
            magha = profiles["PANCHASIDDHANTIKA_MAGHA_ANCHOR"]
            self.assertEqual(magha["calculationStatus"], "SOURCE_TABLE_NOT_TRANSFORMED")
            self.assertEqual(magha["sourceTablePolarLongitudeDeg"], 126.0)
            self.assertIsNone(magha["derivedZeroMeshaDeg"])
        self.assertEqual(output["maghaComparison"]["status"], "SOURCE_TABLE_ACQUIRED_MODERN_TRANSFORMATION_UNRESOLVED")
        self.assertEqual(output["maghaComparison"]["chitraMinusMaghaPolarLongitudeArcMinutes"], 3290)
        current_offset = _chitra_180_offset(datetime(2025, 1, 1, tzinfo=timezone.utc))
        apparent_2025 = next(item for item in output["epochs"] if item["atUtc"] == "2025-01-01T00:00:00Z")["profiles"]
        selected = next(item for item in apparent_2025 if item["profileId"] == "CHITRA_180_APPARENT_TRUE_EQUINOX")
        self.assertAlmostEqual(selected["derivedZeroMeshaDeg"], current_offset, places=6)

    def test_truepos_profiles_report_the_exact_returned_swiss_flags(self) -> None:
        output = build_cgvo_s1b_source_audit(PROJECT_ROOT)
        profiles = {record["profileId"]: record for record in output["epochs"][-1]["profiles"]}
        true_geometric = profiles["CHITRA_180_TRUE_GEOMETRIC_TRUE_EQUINOX"]
        expected_true_flags = swe.FLG_SWIEPH | swe.FLG_TRUEPOS | swe.FLG_NOABERR | swe.FLG_NOGDEFL
        self.assertEqual(true_geometric["requestedFlags"], swe.FLG_SWIEPH | swe.FLG_TRUEPOS)
        self.assertEqual(true_geometric["returnedFlags"], expected_true_flags)
        explicit_astrometric = profiles["CHITRA_180_TRUE_NOABERR_NODEFL"]
        self.assertEqual(explicit_astrometric["returnedFlags"], expected_true_flags)
        mean_true = profiles["CHITRA_180_TRUE_NOABERR_NODEFL_MEAN_EQUINOX"]
        self.assertEqual(mean_true["returnedFlags"], expected_true_flags | swe.FLG_NONUT)
        fixture_profiles = {item["profileId"]: item for item in _s1b_fixtures(PROJECT_ROOT)["absoluteFrameAudit"]["candidateProfiles"]}
        self.assertEqual(fixture_profiles["CHITRA_180_TRUE_GEOMETRIC_TRUE_EQUINOX"]["nutationHandling"], "INCLUDED")
        self.assertEqual(fixture_profiles["CHITRA_180_TRUE_GEOMETRIC_TRUE_EQUINOX"]["aberrationHandling"], "EXCLUDED_BY_RETURNED_FLAG")

    def test_panchasiddhantika_ledger_records_raw_table_values_without_modern_anchor_inference(self) -> None:
        ledger = _s1b_fixtures(PROJECT_ROOT)["panchasiddhantikaFixedStarLedger"]
        self.assertEqual(ledger["source"]["pdfPageCount"], 330)
        self.assertEqual(ledger["source"]["sourceBytePolicy"], "PRIVATE_NOT_TRACKED")
        records = {record["name"]: record for record in ledger["fixedStarTable"]["records"]}
        self.assertEqual(records["MAGHA"]["polarLongitudeDeg"], 126.0)
        self.assertEqual(records["CHITRA"]["polarLongitudeDeg"], 180.83333333333334)
        self.assertEqual(ledger["rawSourceComparisonOnly"]["chitraMinusMaghaPolarLongitudeArcMinutes"], 3290)
        self.assertIn("SOURCE_ANCHOR_AVERAGING", ledger["rawSourceComparisonOnly"]["forbidden"])
        self.assertFalse(ledger["guardrails"]["runtimeSelectable"])
        self.assertFalse(ledger["guardrails"]["executionAllowed"])

    def test_solar_and_lunar_phase_ledgers_are_separate_and_fail_closed(self) -> None:
        fixtures = _s1b_fixtures(PROJECT_ROOT)
        solar = fixtures["solarPhaseMapping"]
        lunar = fixtures["lunarPhaseMapping"]
        self.assertIn("C1", solar["modernCandidateLabels"])
        self.assertIn("C4", solar["modernCandidateLabels"])
        self.assertNotIn("P1", solar["modernCandidateLabels"])
        self.assertIn("P1", lunar["modernCandidateLabels"])
        self.assertIn("U4", lunar["modernCandidateLabels"])
        self.assertNotIn("C1", lunar["modernCandidateLabels"])
        for fixture in (solar, lunar):
            phase = fixture["phaseActivation"]
            self.assertEqual(phase["status"], "UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED")
            self.assertIsNone(phase["commencement"])
            self.assertIsNone(phase["conclusion"])
            self.assertIsNone(phase["effectActivated"])
            self.assertIsNone(phase["jupiterMitigationActivated"])
            self.assertIsNone(fixture["guardrails"]["numericalEffectMultiplier"])
            self.assertIsNone(fixture["guardrails"]["jupiterMitigationCoefficient"])

    def test_firmament_remains_raw_geometry_without_downstream_classifier(self) -> None:
        adjudication = _s1b_fixtures(PROJECT_ROOT)["firmamentAdjudication"]
        self.assertEqual(adjudication["adjudication"]["status"], "COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED")
        self.assertEqual(adjudication["adjudication"]["classicalSection"], "UNKNOWN")
        self.assertFalse(adjudication["adjudication"]["sourceCertifiedClassifier"])
        self.assertFalse(adjudication["adjudication"]["downstreamUseAllowed"])
        status = build_cgvo_status(PROJECT_ROOT)
        self.assertEqual(status["milestone"], "CGVO-G3-D1")
        self.assertEqual(status["milestones"]["astronomy"], "CGVO-S1B-R1")
        self.assertEqual(status["milestones"]["geography"], "CGVO-G2-R1A")
        self.assertEqual(status["milestones"]["siteVisibility"], "CGVO-G3-D1")
        self.assertFalse(status["guardrails"]["executionAllowed"])
        self.assertFalse(status["s1bSourceAudit"]["firmamentAdjudication"]["sourceCertifiedClassifier"])


if __name__ == "__main__":
    unittest.main()
