"""Regression contract for the outcome-blind MO-R4A-S2 bridge freeze."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "gann-astro-desk" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import blinded_market_bridge_s2 as s2  # noqa: E402


class BlindedMarketBridgeS2Test(unittest.TestCase):
    """Keep S2 bounded to the one approved compound-state bridge family."""

    def setUp(self) -> None:
        self.registry_path = (
            PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "experimental_market_hypothesis_registry_s2_v1.json"
        )
        self.schema_path = self.registry_path.with_suffix(".schema.json")
        self.p0_registry_path = (
            PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "experimental_market_hypothesis_registry_v1.json"
        )

    def _mutated_registry_path(self, mutate) -> Path:
        raw = json.loads(self.registry_path.read_text(encoding="utf-8"))
        mutate(raw)
        for entry in raw["entries"]:
            entry["hypothesisHash"] = s2._canonical_hash(s2._hypothesis_decision_content(entry))
        raw["registryHash"] = s2._canonical_hash({key: value for key, value in raw.items() if key != "registryHash"})
        temporary = tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False)
        try:
            temporary.write(json.dumps(raw, indent=2) + "\n")
            return Path(temporary.name)
        finally:
            temporary.close()

    def test_schema_registry_and_p0_history_are_exact(self) -> None:
        raw = json.loads(self.registry_path.read_text(encoding="utf-8"))
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(raw))
        hypothesis_schema = schema["$defs"]["hypothesis"]
        self.assertFalse(hypothesis_schema["additionalProperties"])
        self.assertEqual(
            set(hypothesis_schema["required"]),
            set(raw["entries"][0]),
        )
        self.assertEqual(
            set(hypothesis_schema["required"]),
            set(raw["entries"][1]),
        )

        p0_raw = json.loads(self.p0_registry_path.read_text(encoding="utf-8"))
        self.assertEqual("EMPTY_NO_AUTHORIZED_MARKET_BRIDGES", p0_raw["registryStatus"])
        self.assertEqual([], p0_raw["entries"])

        registry = s2.load_s2_hypothesis_registry(self.registry_path)
        self.assertEqual(s2.S2_HYPOTHESIS_REGISTRY_CONTRACT, registry.raw["contract"])
        self.assertEqual(s2.S2_EXPECTED_STARTING_MASTER, registry.raw["startingMaster"])
        self.assertEqual(s2.S2_EXPECTED_LEDGER_HASH, registry.raw["upstreamSourceLedgerHash"])
        self.assertEqual(s2.S2_EXPECTED_COVERAGE_HASH, registry.raw["upstreamCoverageHash"])
        self.assertEqual(set(s2.S2_SIDES), set(registry.entries_by_side))
        self.assertEqual(set(s2.S2_HYPOTHESIS_IDS.values()), {entry.hypothesis_id for entry in registry.entries_by_side.values()})
        self.assertTrue(all(value is False for value in registry.raw["guardrails"].values()))

    def test_exact_primary_operator_state_map_and_side_local_binding(self) -> None:
        registry = s2.load_s2_hypothesis_registry(self.registry_path)
        expected_map = {
            "GREAT_FRIEND": "SUPPORTIVE",
            "FRIEND": "SUPPORTIVE",
            "NEUTRAL": "NEUTRAL",
            "ENEMY": "ADVERSE",
            "GREAT_ENEMY": "ADVERSE",
        }
        for side, entry in registry.entries_by_side.items():
            self.assertEqual(s2.S2_HYPOTHESIS_IDS[side], entry.hypothesis_id)
            self.assertEqual([s2.S2_PRIMARY_OPERATOR_ID], entry.raw["inputOperatorIds"])
            self.assertEqual(s2.S2_PRIMARY_OPERATOR_ID, entry.raw["primaryInputOperatorId"])
            self.assertEqual("1", entry.raw["primaryInputOperatorVersion"])
            self.assertEqual(expected_map, entry.state_map)
            self.assertIsNone(entry.raw["signedUnitIfConfigured"])
            self.assertFalse(entry.raw["magnitudeConfigured"])
            self.assertFalse(entry.raw["productionAdmission"])

    def test_real_event_freeze_has_expected_coverage_and_no_financial_promotion(self) -> None:
        freeze = s2.build_s2_blinded_prediction_freeze(PROJECT_ROOT)
        self.assertEqual(s2.S2_PREDICTION_FREEZE_CONTRACT, freeze["contract"])
        self.assertEqual(24, len(freeze["predictions"]))
        self.assertEqual(24, len(set(freeze["frozenEventOrder"])))
        self.assertEqual(
            {
                "eventCount": 24,
                "usdEventCount": 12,
                "jpyEventCount": 12,
                "singlePassVerifiedCount": 24,
                "bridgeEligibleCount": 17,
                "abstentionCount": 7,
                "supportiveCount": 9,
                "adverseCount": 5,
                "neutralCount": 3,
                "unknownCount": 7,
                "overallAstrologyUnknownCount": 24,
            },
            freeze["summary"],
        )
        self.assertEqual(
            [
                {"sideIdentity": "USD", "eventCount": 12, "bridgeEligibleCount": 8, "abstentionCount": 4, "supportiveCount": 2, "adverseCount": 4, "neutralCount": 2, "unknownCount": 4},
                {"sideIdentity": "JPY", "eventCount": 12, "bridgeEligibleCount": 9, "abstentionCount": 3, "supportiveCount": 7, "adverseCount": 1, "neutralCount": 1, "unknownCount": 3},
            ],
            freeze["perSide"],
        )
        self.assertTrue(all(row["identityStatus"] == "SINGLE_PASS_VERIFIED" for row in freeze["predictions"]))
        self.assertTrue(all(row["signedUnit"] is None for row in freeze["predictions"]))
        self.assertTrue(all(row["magnitudeConfigured"] is False for row in freeze["predictions"]))
        self.assertTrue(
            all(
                row["overallAstrologicalCompositionStatus"] == "NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT"
                and row["overallAstrologicalInterpretation"] == "UNKNOWN_ASTRO_STATE"
                for row in freeze["predictions"]
            )
        )
        self.assertTrue(all(value is False for value in freeze["guardrails"].values()))
        self.assertFalse(freeze["reviewStoreRead"])
        self.assertFalse(freeze["founderDecisionRead"])
        self.assertFalse(freeze["priceDataRead"])
        self.assertFalse(freeze["outcomeDataRead"])

    def test_unknown_compound_state_abstains_without_fallback(self) -> None:
        freeze = s2.build_s2_blinded_prediction_freeze(PROJECT_ROOT)
        unresolved = [row for row in freeze["predictions"] if row["sourceOperatorInput"]["outputState"] == "UNKNOWN"]
        self.assertEqual(7, len(unresolved))
        for row in unresolved:
            self.assertFalse(row["bridgeApplied"])
            self.assertEqual("UNKNOWN_MORE_EVIDENCE_REQUIRED", row["currencyPressureState"])
            self.assertEqual("COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED", row["abstentionReason"])
            self.assertEqual(s2.S2_PRIMARY_OPERATOR_ID, row["primaryInputOperatorId"])
        neutral = [row for row in freeze["predictions"] if row["sourceOperatorInput"]["outputState"] == "NEUTRAL"]
        self.assertEqual(3, len(neutral))
        self.assertTrue(all(row["bridgeApplied"] and row["currencyPressureState"] == "NEUTRAL" for row in neutral))

    def test_invariance_audit_rejects_changed_real_event_identity(self) -> None:
        freeze = s2.build_s2_blinded_prediction_freeze(PROJECT_ROOT)
        audit = s2.build_s2_invariance_audit(PROJECT_ROOT, prediction_freeze=freeze)
        self.assertTrue(audit["summary"]["allEventIdentitiesUnchanged"])
        self.assertTrue(audit["summary"]["allAstronomySnapshotsUnchanged"])
        self.assertTrue(audit["summary"]["allOverallSourceCompositionUnchanged"])

        changed = copy.deepcopy(freeze)
        changed["predictions"][0]["eventHash"] = "0" * 64
        changed["predictionFreezeHash"] = s2._canonical_hash({key: value for key, value in changed.items() if key != "predictionFreezeHash"})
        with self.assertRaises(s2.BlindedMarketBridgeS2Error):
            s2.build_s2_invariance_audit(PROJECT_ROOT, prediction_freeze=changed)

    def test_registry_rejects_unapproved_side_or_secondary_operator(self) -> None:
        malformed_paths: list[Path] = []
        try:
            malformed_paths.append(self._mutated_registry_path(lambda raw: raw["entries"][1].update({"targetSide": "USD"})))
            malformed_paths.append(
                self._mutated_registry_path(
                    lambda raw: raw["entries"][0].update(
                        {"inputOperatorIds": [s2.S2_PRIMARY_OPERATOR_ID, "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1"]}
                    )
                )
            )
            for path in malformed_paths:
                with self.assertRaises(s2.BlindedMarketBridgeS2Error):
                    s2.load_s2_hypothesis_registry(path)
        finally:
            for path in malformed_paths:
                path.unlink(missing_ok=True)

    def test_registry_rejects_outcome_seen_or_guardrail_release(self) -> None:
        malformed_paths: list[Path] = []
        try:
            malformed_paths.append(self._mutated_registry_path(lambda raw: raw["entries"][0].update({"outcomeDataSeenAtCreation": True})))
            malformed_paths.append(self._mutated_registry_path(lambda raw: raw["guardrails"].update({"executionAllowed": True})))
            for path in malformed_paths:
                with self.assertRaises(s2.BlindedMarketBridgeS2Error):
                    s2.load_s2_hypothesis_registry(path)
        finally:
            for path in malformed_paths:
                path.unlink(missing_ok=True)

    def test_materialized_artifacts_are_deterministic_and_do_not_create_signed_outputs(self) -> None:
        artifacts = s2.write_s2_artifacts(PROJECT_ROOT)
        freeze = json.loads(artifacts["predictionFreeze"].read_text(encoding="utf-8"))
        audit = json.loads(artifacts["invarianceAudit"].read_text(encoding="utf-8"))
        acceptance = json.loads(artifacts["acceptance"].read_text(encoding="utf-8"))
        self.assertEqual(freeze["predictionFreezeHash"], audit["predictionFreezeHash"])
        self.assertEqual(freeze["predictionFreezeHash"], acceptance["predictionFreezeHash"])
        self.assertEqual(audit["invarianceAuditHash"], acceptance["invarianceAuditHash"])
        self.assertFalse(acceptance["executionAllowed"])
        self.assertEqual("CENTRAL_REVIEW_REQUIRED_BEFORE_S3_PREREGISTRATION", acceptance["s3Prerequisite"])
        self.assertIn("signedUnit=null", artifacts["reviewTable"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
