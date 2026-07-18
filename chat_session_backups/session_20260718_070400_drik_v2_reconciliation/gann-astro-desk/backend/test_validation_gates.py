from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validation_gates import build_validation_gate_matrix, load_external_gate


def shadow_snapshot(status: str) -> dict:
    return {
        "summary": {
            "gateStatus": status,
            "watchClusterCount": 12,
            "calendarMonthCount": 2,
            "coverage": 0.2,
            "wilson95Lower": 0.48,
            "twoSidedBinomialP": 0.2,
            "meanSigned72hReturnPct": 0.01,
            "chain": {"valid": True, "entryCount": 20},
            "trial": {
                "trialId": "TRIAL",
                "integrityValid": True,
                "cohortCount": 1,
                "progress": {
                    "watchClusters": {"current": 12, "target": 100},
                    "calendarMonths": {"current": 2, "target": 4},
                },
            },
        }
    }


def candle_snapshot() -> dict:
    return {
        "model": {
            "artifactId": "candle-v1",
            "retrospectiveGate": {
                "status": "failed",
                "primaryCandidate": "named_pattern_logistic_v1",
                "promotionAuthorized": False,
            },
        }
    }


def passed_external_gate() -> dict:
    return {
        "contract": "GANN_ASTRO_EXTERNAL_CERTIFICATION_GATE_V1",
        "status": "passed_external_validation",
        "certified": True,
        "executionAllowed": False,
        "rows": {"total": 95, "pass": 95, "fail": 0, "pending": 0},
        "strengthMatrix": {
            "expectedRows": 70,
            "actualRows": 70,
            "pass": 70,
            "fail": 0,
            "pending": 0,
        },
        "independentDrikWitness": {
            "status": "passed_independent_validation",
            "certified": True,
            "rows": {
                "expected": 35,
                "actual": 35,
                "pass": 35,
                "fail": 0,
                "pending": 0,
            },
        },
    }


class ValidationGateMatrixTest(unittest.TestCase):
    def test_missing_external_gate_blocks_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            matrix = build_validation_gate_matrix(
                Path(tmp),
                shadow_snapshot("collecting_prospective_shadow_evidence"),
                candle_snapshot(),
                historical_contract="historical-v1",
                historical_status="failed_retrospective_statistical_gate",
                historical_report="report.md",
            )
        self.assertEqual(matrix["overallStatus"], "research_only_blocked")
        self.assertFalse(matrix["executionAllowed"])
        self.assertIn("external_astrology", matrix["blockingGateIds"])
        self.assertIn("retrospective_policy", matrix["blockingGateIds"])
        self.assertIn("prospective_shadow", matrix["blockingGateIds"])
        self.assertIn("execution_authorization", matrix["blockingGateIds"])

    def test_all_research_prerequisites_can_pass_without_unlocking_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "astro_external_validation_gate_20260718.json"
            path.write_text(json.dumps(passed_external_gate()), encoding="utf-8")
            matrix = build_validation_gate_matrix(
                Path(tmp),
                shadow_snapshot("passed_prospective_statistical_gate"),
                candle_snapshot(),
                historical_contract="historical-v1",
                historical_status="passed_retrospective_statistical_gate",
                historical_report="report.md",
            )
        self.assertTrue(matrix["prerequisitesPassed"])
        self.assertEqual(
            matrix["overallStatus"],
            "prerequisites_passed_execution_still_locked",
        )
        self.assertFalse(matrix["executionAllowed"])
        self.assertEqual(matrix["blockingGateIds"], ["execution_authorization"])

    def test_external_gate_internal_counts_are_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "astro_external_validation_gate_20260718.json"
            payload = passed_external_gate()
            payload["strengthMatrix"]["pending"] = 1
            path.write_text(json.dumps(payload), encoding="utf-8")
            loaded = load_external_gate(Path(tmp))
        self.assertFalse(loaded["certified"])
        self.assertIn("incomplete", loaded["reason"].lower())

    def test_external_gate_requires_separate_independent_drik_witness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "astro_external_validation_gate_20260718.json"
            payload = passed_external_gate()
            payload.pop("independentDrikWitness")
            path.write_text(json.dumps(payload), encoding="utf-8")
            loaded = load_external_gate(Path(tmp))
        self.assertFalse(loaded["certified"])
        self.assertIn("independent drik witness", loaded["reason"].lower())


if __name__ == "__main__":
    unittest.main()
