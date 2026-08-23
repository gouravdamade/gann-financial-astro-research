from __future__ import annotations

import json
from pathlib import Path
import unittest

import yaml

from cgvo_service import _s1a_fixtures, build_cgvo_status


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CgvoS1aSourceFixtureTests(unittest.TestCase):
    def test_all_s1a_yaml_fixtures_parse_and_are_read_only(self) -> None:
        paths = [
            "VARAHAMIHIRA_ASTRONOMICAL_FRAME_V1.yaml",
            "VARAHAMIHIRA_LUNAR_MONTH_PROFILE_V1.yaml",
            "VARAHAMIHIRA_ECLIPSE_ASPECT_PROFILE_V1.yaml",
            "VARAHAMIHIRA_FIRMAMENT_GEOMETRY_V1.yaml",
            "CGVO_S1_READINESS_MATRIX_V1.yaml",
        ]
        for filename in paths:
            payload = yaml.safe_load((PROJECT_ROOT / "configs" / "research" / "cgvo" / filename).read_text(encoding="utf-8"))
            self.assertIsInstance(payload, dict)
            self.assertFalse(str(payload).lower().find("d:\\") >= 0)
        self.assertFalse(build_cgvo_status(PROJECT_ROOT)["guardrails"]["executionAllowed"])

    def test_partition_contains_all_twelve_rasis_without_tropical_substitution(self) -> None:
        frame = _s1a_fixtures(PROJECT_ROOT)["frame"]
        self.assertEqual(frame["sourceAuthority"], "CLOSED_ROOT_SOURCE")
        self.assertFalse(frame["tropicalSeasonFrameAuthorizedForRasi"])
        self.assertEqual(len(frame["partition"]), 12)
        self.assertEqual(frame["partition"][0], {
            "rasi": "MESHA", "segments": ["ASHWINI 1-4", "BHARANI 1-4", "KRITTIKA 1"],
        })
        self.assertEqual(frame["partition"][4]["rasi"], "SIMHA")
        self.assertEqual(frame["partition"][8]["rasi"], "DHANUS")
        candidate = frame["absoluteFrameCandidates"][0]
        self.assertFalse(candidate["defaultAuthorized"])
        self.assertEqual(candidate["prohibitedAliases"], ["LAHIRI", "RAMAN", "TROPICAL"])

    def test_aspect_and_firmament_source_contracts_preserve_null_scalars_and_unknown_classifier(self) -> None:
        fixtures = _s1a_fixtures(PROJECT_ROOT)
        aspect = fixtures["aspect"]
        self.assertEqual(aspect["sourceStatus"], "CLOSED_SAME_AUTHOR_DELEGATED_SOURCE")
        self.assertEqual(aspect["ordinarySignFractions"]["3"], 0.25)
        self.assertEqual(aspect["ordinarySignFractions"]["7"], 1.0)
        self.assertEqual(aspect["specialFullAspects"]["SATURN"], [3, 10])
        self.assertEqual(aspect["maximumGeometryRole"], "GEOMETRY_SNAPSHOT_ONLY")
        self.assertEqual(aspect["sourcePhaseActivationStatus"], "UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED")
        self.assertIsNone(aspect["effectMagnitudeMultiplier"])
        self.assertIsNone(aspect["jupiterMitigationCoefficient"])
        firmament = fixtures["firmament"]
        self.assertEqual(firmament["sourceStatus"], "COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED")
        self.assertEqual(firmament["classicalSection"], "UNKNOWN")
        self.assertFalse(firmament["sourceCertifiedClassifier"])
        lunar = fixtures["lunarMonth"]
        self.assertEqual(lunar["intercalationGuard"]["contract"], "SANKRANTI_COUNT_FAIL_CLOSED_V1")
        self.assertEqual(lunar["intercalationGuard"]["unresolvedResult"], "UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED")
        self.assertEqual(lunar["baseSystem"], "PURNIMANTA")
        self.assertEqual(lunar["monthNaming"]["runtimeAlgorithm"], "NEXT_FULL_MOON_NAKSHATRA_LOOKUP_V1")
        self.assertFalse(lunar["monthNaming"]["sourceClosed"])
        self.assertEqual(lunar["boundarySemantics"]["sourceStatus"], "UNKNOWN_SOURCE_BOUNDARY_NOT_CLOSED")
        self.assertEqual(lunar["historicalTimeAndLocality"]["localityRole"], "SOURCE_DAY_PROVENANCE_ONLY")
        self.assertFalse(lunar["historicalTimeAndLocality"]["changesMonthMembership"])
        self.assertEqual(lunar["intercalationTerms"]["adhimasa"]["sourceStatus"], "ROOT_TERM_RECORDED")
        self.assertEqual(lunar["intercalationTerms"]["avama"]["kshayaEquivalenceStatus"], "UNKNOWN_NOT_ASSERTED")
        self.assertEqual(lunar["intercalationTerms"]["kshaya"]["runtimeClassification"], "NOT_ASSIGNED")
        self.assertEqual(lunar["intercalationGuard"]["sourceAuthority"], "NOT_A_COMPLETE_HISTORICAL_INTERCALATION_OPERATOR")

    def test_calendar_r1_machine_profile_preserves_unknown_historical_edges(self) -> None:
        path = PROJECT_ROOT / "configs" / "research" / "cgvo" / "cgvo_calendar_r1_lunar_month_profile_v1.json"
        profile = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(profile["status"], "HISTORICAL_OPERATOR_PARTIAL_FAIL_CLOSED")
        self.assertEqual(profile["monthBasis"]["value"], "PURNIMANTA")
        self.assertFalse(profile["monthBasis"]["sourceClosed"])
        self.assertFalse(profile["monthNaming"]["sourceClosed"])
        self.assertEqual(profile["boundary"]["historicalBoundary"], "UNKNOWN_SOURCE_BOUNDARY_NOT_CLOSED")
        self.assertEqual(profile["timeAndLocality"]["localityRole"], "SOURCE_DAY_PROVENANCE_ONLY")
        self.assertEqual(profile["intercalation"]["adhika"]["historicalClassification"], "NOT_SOURCE_CLOSED")
        self.assertEqual(profile["intercalation"]["avama"]["kshayaEquivalence"], "UNKNOWN_NOT_ASSERTED")
        self.assertEqual(profile["intercalation"]["kshaya"]["runtimeHandling"], "NOT_ASSIGNED")
        self.assertEqual(profile["mode1"]["ordinaryCaseAdmission"], "NOT_ELIGIBLE_CURRENTLY")
        case_results = {item["caseId"]: item["observedRuntimeResult"] for item in profile["historicalAuditCases"]}
        self.assertEqual(case_results["INTERCALATION_GUARD_2023_07_29"], "UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED")
        self.assertEqual(case_results["TWO_INGRESS_1822_12_20"], "UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED")
        self.assertFalse(profile["guardrails"]["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
