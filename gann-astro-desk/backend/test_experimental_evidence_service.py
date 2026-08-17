from __future__ import annotations

import copy
import unittest
from pathlib import Path

from experimental_evidence_service import (
    PROFILE_ID,
    _bounded_exp_multiplier,
    _compile_snapshot,
    _fixture,
    _profile,
    build_experimental_profile,
    build_experimental_snapshot,
    build_trial_ledger,
    compare_experimental_transforms,
    compile_pair_relative_adapter,
)


class ExperimentalEvidenceServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]

    def test_profile_is_isolated_and_execution_is_impossible(self) -> None:
        profile = build_experimental_profile(self.root)
        self.assertEqual(profile["profile"]["profileId"], PROFILE_ID)
        self.assertRegex(profile["profile"]["codeCommit"], r"^[0-9a-f]{40}$")
        self.assertFalse(profile["profile"]["executionAllowed"])
        self.assertFalse(profile["guardrails"]["executionAllowed"])
        self.assertFalse(profile["guardrails"]["priceDataRead"])
        self.assertFalse(profile["guardrails"]["sbcRead"])
        self.assertEqual(profile["profile"]["datasetStatus"], "SYNTHETIC")

    def test_raw_observations_are_immutable_across_transform_changes(self) -> None:
        first = build_experimental_snapshot(self.root, {"transformId": "XE1_BASE_DIRECTIONAL_V1"})
        second = build_experimental_snapshot(self.root, {"transformId": "XE1_BOUNDED_EXP_MULTIPLIER_V1"})
        self.assertTrue(first["rawEvidenceImmutable"])
        self.assertEqual(first["codeCommit"], first["profile"]["codeCommit"])
        self.assertEqual(first["profile"]["profileHash"], second["profile"]["profileHash"])
        self.assertEqual(first["rawObservations"], second["rawObservations"])
        self.assertNotEqual(first["stateVector"]["directionalRaw"], second["stateVector"]["directionalRaw"])

    def test_positive_modifier_is_bounded_and_cannot_flip_sign(self) -> None:
        neutral = _bounded_exp_multiplier(0.4, beta=0.0, m_min=0.5, m_max=1.5)
        amplified = _bounded_exp_multiplier(0.4, beta=0.65, m_min=0.5, m_max=1.5)
        self.assertEqual(neutral["value"], 1.0)
        self.assertGreaterEqual(amplified["value"], 0.5)
        self.assertLessEqual(amplified["value"], 1.5)
        self.assertGreater(1.0 * amplified["value"], 0)
        self.assertLess(-1.0 * amplified["value"], 0)
        self.assertIsNone(_bounded_exp_multiplier(None, beta=0.65, m_min=0.5, m_max=1.5)["value"])

    def test_derived_child_shares_cause_and_never_votes_twice(self) -> None:
        snapshot = build_experimental_snapshot(self.root, {"transformId": "XE1_BASE_DIRECTIONAL_V1"})
        contribution = next(item for item in snapshot["causalContributions"] if item["causalEventId"] == "XE1_CAUSE_POSITIVE")
        self.assertEqual(contribution["causalClassification"], "SHARED_CAUSE")
        self.assertEqual(contribution["value"], 1.0)
        self.assertEqual(contribution["derivedChildIds"], ["XE1_OBS_POSITIVE_DERIVED_V1"])
        self.assertEqual(snapshot["stateVector"]["positive"], 1.0)

    def test_ambiguous_cause_fails_closed_and_unknown_never_becomes_zero(self) -> None:
        snapshot = build_experimental_snapshot(self.root, {})
        ambiguous = next(item for item in snapshot["causalContributions"] if item["causalEventId"] == "XE1_CAUSE_AMBIGUOUS")
        self.assertEqual(ambiguous["status"], "AMBIGUOUS_CAUSE_FAIL_CLOSED")
        self.assertIsNone(ambiguous["value"])
        self.assertGreater(snapshot["stateVector"]["unknownGroupCount"], 0)

    def test_no_active_evidence_keeps_conflict_unknown(self) -> None:
        snapshot = build_experimental_snapshot(self.root, {"dataMode": "MANUAL"})
        self.assertEqual(snapshot["stateVector"]["state"], "UNKNOWN_NO_ACTIVE_EVIDENCE")
        self.assertIsNone(snapshot["stateVector"]["directionalNormalized"])
        self.assertIsNone(snapshot["stateVector"]["conflictLinear"])
        self.assertEqual(snapshot["manualInputStatus"], "MANUAL_INPUT_REQUIRED")

    def test_touched_development_mode_is_explicitly_empty_until_observations_are_admitted(self) -> None:
        snapshot = build_experimental_snapshot(self.root, {"dataMode": "TOUCHED_DEV"})
        self.assertEqual(snapshot["datasetLabel"], "EXPLORATORY_TOUCHED")
        self.assertEqual(snapshot["rawObservations"], [])
        self.assertEqual(snapshot["manualInputStatus"], "TOUCHED_DEV_INPUT_NOT_CONFIGURED")
        self.assertEqual(snapshot["stateVector"]["state"], "UNKNOWN_NO_ACTIVE_EVIDENCE")

    def test_gate_is_three_state_context_not_direction(self) -> None:
        snapshot = build_experimental_snapshot(self.root, {})
        gate = next(item for item in snapshot["rawObservations"] if item["featureKey"] == "synthetic_gate_inactive")
        self.assertEqual(gate["valueType"], "BOOLEAN_GATE")
        self.assertIs(gate["rawValue"], False)
        self.assertNotIn(gate["observationId"], [
            item.get("sourceObservationId") for item in snapshot["causalContributions"]
        ])

    def test_confidence_is_separate_from_directional_evidence(self) -> None:
        snapshot = build_experimental_snapshot(self.root, {})
        self.assertFalse(snapshot["quality"]["confidenceMultipliesEvidence"])
        self.assertEqual(snapshot["quality"]["confidenceUse"], "DISPLAY_ONLY_SEPARATE_FROM_DIRECTIONAL_EVIDENCE")

    def test_pair_adapter_is_optional_and_preserves_unknown_side(self) -> None:
        known = compile_pair_relative_adapter(
            {"directionalNormalized": 0.8, "confidence": 0.9},
            {"directionalNormalized": -0.2, "confidence": 0.6},
        )
        self.assertEqual(known["pairDisplay"], 0.5)
        self.assertEqual(known["quality"], 0.6)
        self.assertFalse(known["sbcUsed"])
        unknown = compile_pair_relative_adapter({"directionalNormalized": None}, {"directionalNormalized": 0.3})
        self.assertEqual(unknown["state"], "UNKNOWN_SIDE_EVIDENCE")
        self.assertIsNone(unknown["pairDisplay"])

    def test_transform_comparison_and_trial_governance_are_explicit(self) -> None:
        comparison = compare_experimental_transforms(self.root, {"dataMode": "TOUCHED_DEV"})
        self.assertEqual(len(comparison["comparisons"]), 4)
        self.assertFalse(comparison["guardrails"]["executionAllowed"])
        ledger = build_trial_ledger(self.root)
        self.assertEqual(comparison["profileHash"], ledger["profileHash"])
        self.assertEqual(comparison["codeCommit"], ledger["codeCommit"])
        self.assertEqual(ledger["datasetGovernance"]["APRIL_2025_STATUS"], "TOUCHED_DEV")
        self.assertFalse(ledger["datasetGovernance"]["pristineHoldoutUsed"])
        self.assertTrue(all(entry["immutableAfterEvaluation"] for entry in ledger["entries"]))
        self.assertTrue(all(entry["entryHash"] for entry in ledger["entries"]))

    def test_frontend_cannot_supply_evidence_or_load_source_mode(self) -> None:
        with self.assertRaises(ValueError):
            build_experimental_snapshot(self.root, {"profileId": "SBC_TRAILOKYA_1972_V1"})
        with self.assertRaises(ValueError):
            build_experimental_snapshot(self.root, {"observations": []})

    def test_fixture_is_not_mutated_by_compilation(self) -> None:
        fixture = _fixture(self.root)
        before = copy.deepcopy(fixture)
        _compile_snapshot(fixture["observations"], _profile(), "XE1_BOUNDED_EXP_MULTIPLIER_V1")
        self.assertEqual(fixture, before)


if __name__ == "__main__":
    unittest.main()
