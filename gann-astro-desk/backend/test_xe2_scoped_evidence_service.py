from __future__ import annotations

import copy
import unittest
from pathlib import Path

from xe2_scoped_evidence_service import (
    PROFILE_ID,
    TRANSFORMS,
    _compile_from_fixture_for_test,
    _fixture,
    build_xe2_profile,
    build_xe2_snapshot,
    build_xe2_trial_ledger,
    compare_xe2_transforms,
    resolve_modifier_scope,
)


class Xe2ScopedEvidenceServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]

    def test_real_astronomical_inputs_are_hash_linked_single_pass_and_unsigned(self) -> None:
        fixture = _fixture(self.root)
        self.assertEqual(fixture["datasetGovernance"]["datasetStatus"], "TOUCHED_DEV")
        self.assertFalse(fixture["datasetGovernance"]["marketOutcomeRead"])
        self.assertEqual(fixture["astronomySource"]["directionPolicy"], "ASPECT_GEOMETRY_NEVER_SUPPLIES_DIRECTION_BY_ITSELF")
        self.assertEqual(len(fixture["events"]), 4)
        for event in fixture["events"]:
            identity = event["eventIdentity"]
            self.assertEqual(identity["identityStatus"], "SINGLE_PASS_VERIFIED")
            self.assertEqual(identity["transitBody"], "MOON")
            self.assertTrue(identity["eventHash"])
            self.assertNotIn("reviewedPolarity", identity)
            self.assertIsInstance(identity["speedDegPerDay"], float)

    def test_profile_blocks_real_signed_evidence_price_and_execution(self) -> None:
        profile = build_xe2_profile(self.root)
        self.assertEqual(profile["profile"]["profileId"], PROFILE_ID)
        self.assertEqual(profile["realEvidenceAdmission"]["reviewedSignedEvidence"], "NOT_ADMITTED_NONE_EXISTS")
        self.assertFalse(profile["guardrails"]["priceDataRead"])
        self.assertFalse(profile["guardrails"]["priceOutcomeRead"])
        self.assertFalse(profile["guardrails"]["sbcRead"])
        self.assertFalse(profile["guardrails"]["fieldsPath"])
        self.assertFalse(profile["guardrails"]["executionAllowed"])

    def test_raw_observations_remain_immutable_and_synthetic_signs_are_labelled(self) -> None:
        first = build_xe2_snapshot(self.root, {"transformId": TRANSFORMS[0]})
        second = build_xe2_snapshot(self.root, {"transformId": TRANSFORMS[1]})
        self.assertTrue(first["rawEvidenceImmutable"])
        self.assertEqual(first["rawObservations"], second["rawObservations"])
        signs = [item for item in first["rawObservations"] if item["role"] == "SYNTHETIC_SIGN_TEST_ONLY"]
        self.assertEqual(len(signs), 4)
        self.assertTrue(all(item["sourceStatus"] == "SYNTHETIC_TEST_ONLY" for item in signs))
        self.assertEqual(first["marketDirectionStatus"], "BLOCKED_NO_REAL_SIGNED_EVIDENCE")

    def test_m0_and_m1_are_scoped_and_heterogeneous_speed_changes_only_test_vector(self) -> None:
        base = build_xe2_snapshot(self.root, {"transformId": TRANSFORMS[0]})
        multiplier = build_xe2_snapshot(self.root, {"transformId": TRANSFORMS[1]})
        self.assertNotEqual(
            base["syntheticStateVector"]["syntheticNormalized"],
            multiplier["syntheticStateVector"]["syntheticNormalized"],
        )
        self.assertTrue(all(item["scope"]["scopeStatus"] == "BOUND" for item in multiplier["causalContributions"]))
        self.assertTrue(all(item["scope"]["globalDefaultApplied"] is False for item in multiplier["causalContributions"]))
        for item in multiplier["causalContributions"]:
            self.assertGreater(item["multiplierOrInteraction"], 0)
            self.assertGreaterEqual(item["value"] * item["rawSyntheticSignTestValue"], 0)

    def test_equal_modifier_reduces_to_base_and_unknown_modifier_affects_only_target(self) -> None:
        fixture = _fixture(self.root)
        equal = copy.deepcopy(fixture)
        reference = equal["normalization"]["referenceSpeedDegPerDay"]
        for event in equal["events"]:
            event["eventIdentity"]["speedDegPerDay"] = reference
        base = _compile_from_fixture_for_test(equal, TRANSFORMS[0])
        multiplier = _compile_from_fixture_for_test(equal, TRANSFORMS[1])
        self.assertEqual(base["syntheticStateVector"]["syntheticNormalized"], multiplier["syntheticStateVector"]["syntheticNormalized"])

        unknown = copy.deepcopy(fixture)
        unknown["events"][0]["eventIdentity"]["speedDegPerDay"] = None
        compiled = _compile_from_fixture_for_test(unknown, TRANSFORMS[1])
        self.assertEqual(compiled["causalContributions"][0]["status"], "UNKNOWN_TARGET_ONLY")
        self.assertTrue(all(item["status"] == "ACTIVE" for item in compiled["causalContributions"][1:]))

    def test_m2_preserves_sign_channel_and_m3_m4_do_not_add_votes(self) -> None:
        base = build_xe2_snapshot(self.root, {"transformId": TRANSFORMS[0]})
        separate = build_xe2_snapshot(self.root, {"transformId": TRANSFORMS[2]})
        interaction = build_xe2_snapshot(self.root, {"transformId": TRANSFORMS[3]})
        gate = build_xe2_snapshot(self.root, {"transformId": TRANSFORMS[4]})
        self.assertEqual(base["syntheticStateVector"], separate["syntheticStateVector"])
        self.assertTrue(all(item["separateChannelValue"] is not None for item in separate["causalContributions"]))
        self.assertNotEqual(base["syntheticStateVector"]["syntheticNormalized"], interaction["syntheticStateVector"]["syntheticNormalized"])
        self.assertEqual(len(gate["causalContributions"]), len(base["causalContributions"]))
        self.assertTrue(all(item["contextGate"] == 1.0 for item in gate["causalContributions"]))

    def test_unscoped_modifier_is_rejected_without_global_fallback(self) -> None:
        rejected = resolve_modifier_scope({"observationId": "unscoped"}, "XE2_CAUSE_TEST")
        self.assertEqual(rejected["scopeStatus"], "REJECTED_UNSCOPED")
        self.assertFalse(rejected["globalDefaultApplied"])
        mismatch = resolve_modifier_scope(
            {"observationId": "wrong", "targetScope": {"type": "CAUSAL_EVENT_ID", "causalEventId": "OTHER"}},
            "XE2_CAUSE_TEST",
        )
        self.assertEqual(mismatch["scopeStatus"], "REJECTED_UNSCOPED")

    def test_no_client_evidence_injection_and_trial_ledger_has_no_outcome_evaluation(self) -> None:
        with self.assertRaises(ValueError):
            build_xe2_snapshot(self.root, {"observations": []})
        with self.assertRaises(ValueError):
            build_xe2_snapshot(self.root, {"profileId": "SBC_TRAILOKYA_1972_V1"})
        comparison = compare_xe2_transforms(self.root, {})
        self.assertEqual(len(comparison["comparisons"]), 5)
        self.assertTrue(all(item["marketDirectionStatus"] == "BLOCKED_NO_REAL_SIGNED_EVIDENCE" for item in comparison["comparisons"]))
        ledger = build_xe2_trial_ledger(self.root)
        self.assertEqual(ledger["datasetGovernance"]["datasetStatus"], "TOUCHED_DEV")
        self.assertTrue(all(item["result"] == "NOT_EVALUATED" for item in ledger["entries"]))
        self.assertTrue(all(item["marketOutcomeRead"] is False for item in ledger["entries"]))


if __name__ == "__main__":
    unittest.main()
