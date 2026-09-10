"""Outcome-blind regression contract for the Saravali-lineage S2R1 successor."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
BACKEND_ROOT = PROJECT_ROOT / "gann-astro-desk" / "backend"
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
for root in (PROJECT_ROOT, PROJECT_ROOT / "gann-astro-desk", BACKEND_ROOT, LAB_ROOT, INSTRUMENT_SBC_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

import blinded_market_bridge_s2r1 as s2r1  # noqa: E402


class BlindedMarketBridgeS2R1Tests(unittest.TestCase):
    """The successor may rebind source lineage but cannot inspect outcomes or add bridges."""

    def setUp(self) -> None:
        self.registry_path = (
            PROJECT_ROOT / "configs" / "research" / "machine_interpretation" / "experimental_market_hypothesis_registry_s2r1_v1.json"
        )

    def test_registry_is_exactly_two_side_local_successors_and_preserves_history(self) -> None:
        raw_registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        schema = json.loads(self.registry_path.with_suffix(".schema.json").read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(raw_registry))
        self.assertFalse(schema["$defs"]["hypothesis"]["additionalProperties"])
        self.assertEqual(set(schema["$defs"]["hypothesis"]["required"]), set(raw_registry["entries"][0]))
        registry = s2r1._load_registry(self.registry_path)
        self.assertEqual(registry.raw["historicalS2RegistryHash"], s2r1.HISTORICAL_S2_REGISTRY_HASH)
        self.assertEqual(registry.raw["historicalS2PredictionFreezeHash"], s2r1.HISTORICAL_S2_FREEZE_HASH)
        self.assertEqual(set(registry.entries_by_side), {"USD", "JPY"})
        self.assertEqual({entry.hypothesis_id for entry in registry.entries_by_side.values()}, set(s2r1.S2R1_HYPOTHESIS_IDS.values()))
        for side, entry in registry.entries_by_side.items():
            self.assertEqual(entry.raw["supersedesHypothesisId"], {
                "USD": "H-MO-S2-COMPOUND-REL-DIRECT-USD-V1",
                "JPY": "H-MO-S2-COMPOUND-REL-DIRECT-JPY-V1",
            }[side])
            self.assertEqual(entry.raw["inputOperatorIds"], ["BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1"])
            self.assertEqual(entry.raw["stateMap"], s2r1.s2.S2_STATE_MAP)
            self.assertIsNone(entry.raw["signedUnitIfConfigured"])
            self.assertFalse(entry.raw["magnitudeConfigured"])
            self.assertFalse(entry.raw["productionAdmission"])
        self.assertTrue(all(value is False for value in registry.raw["guardrails"].values()))

    def test_successor_freeze_is_24_event_side_local_and_keeps_all_locks(self) -> None:
        freeze = s2r1.build_s2r1_blinded_prediction_freeze(PROJECT_ROOT)
        self.assertEqual(freeze["contract"], s2r1.S2R1_PREDICTION_FREEZE_CONTRACT)
        self.assertEqual(
            freeze["summary"],
            {
                "eventCount": 24,
                "usdEventCount": 12,
                "jpyEventCount": 12,
                "singlePassVerifiedCount": 24,
                "bridgeEligibleCount": 17,
                "directionalCount": 14,
                "abstentionCount": 7,
                "supportiveCount": 9,
                "adverseCount": 5,
                "neutralCount": 3,
                "unknownCount": 7,
                "overallAstrologyUnknownCount": 24,
            },
        )
        self.assertEqual(len(freeze["predictions"]), 24)
        self.assertEqual(len(set(freeze["frozenEventOrder"])), 24)
        for row in freeze["predictions"]:
            self.assertEqual(row["identityStatus"], "SINGLE_PASS_VERIFIED")
            self.assertIsNone(row["signedUnit"])
            self.assertFalse(row["magnitudeConfigured"])
            self.assertEqual(row["overallAstrologicalCompositionStatus"], "NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT")
            self.assertEqual(row["overallAstrologicalInterpretation"], "UNKNOWN_ASTRO_STATE")
            self.assertFalse(row["priceDataRead"])
            self.assertFalse(row["outcomeDataSeen"])
            self.assertFalse(row["executionAllowed"])
            self.assertEqual(row["primaryInputOperatorId"], "BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1")
        self.assertTrue(all(value is False for value in freeze["guardrails"].values()))
        self.assertFalse(freeze["reviewStoreRead"])
        self.assertFalse(freeze["founderDecisionRead"])
        self.assertFalse(freeze["priceDataRead"])
        self.assertFalse(freeze["outcomeDataRead"])

    def test_lineage_diff_has_all_24_rows_and_surfaces_zero_pilot_changes(self) -> None:
        freeze = s2r1.build_s2r1_blinded_prediction_freeze(PROJECT_ROOT)
        reconciliation = s2r1.build_s2r1_lineage_reconciliation(PROJECT_ROOT, successor_freeze=freeze)
        self.assertEqual(reconciliation["branchTaken"], "B")
        self.assertEqual(reconciliation["comparisonSummary"], {
            "rowCount": 49,
            "comparableDirectedPairCount": 42,
            "agreementCount": 41,
            "conflictCount": 1,
            "notComparableCount": 7,
            "unresolvedCount": 0,
        })
        self.assertEqual(reconciliation["pilotRelevantConflicts"], [])
        self.assertEqual(len(reconciliation["eventDiff"]), 24)
        self.assertEqual(reconciliation["summary"]["changedCompoundEventCount"], 0)
        self.assertEqual(reconciliation["summary"]["changedPredictionCount"], 0)
        self.assertEqual(reconciliation["summary"]["unchangedPredictionCount"], 24)
        for row in reconciliation["eventDiff"]:
            self.assertEqual(row["historicalS2CompoundState"], row["correctedCompoundState"])
            self.assertEqual(row["historicalS2PressureState"], row["correctedPressureState"])
            self.assertEqual(row["historicalBridgeApplied"], row["correctedBridgeApplied"])
            self.assertFalse(row["predictionChanged"])
            self.assertEqual(row["historicalS2NaturalSource"]["operatorId"], "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1")
            self.assertEqual(row["correctedNaturalSource"]["operatorId"], "SARAVALI_NATURAL_RELATIONSHIP_V1")
            self.assertEqual(row["oldNaturalRelationshipOperator"], "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1")
            self.assertEqual(row["newNaturalRelationshipOperator"], "SARAVALI_NATURAL_RELATIONSHIP_V1")
            self.assertFalse(row["compoundStateChanged"])
            self.assertTrue(row["sourceLineageChanged"])
            self.assertFalse(row["eventIdentityChanged"])
            self.assertFalse(row["astronomyChanged"])

    def test_materialized_artifacts_are_deterministic_and_require_central_review(self) -> None:
        first = s2r1.write_s2r1_artifacts(PROJECT_ROOT)
        first_bytes = {name: path.read_bytes() for name, path in first.items()}
        second = s2r1.write_s2r1_artifacts(PROJECT_ROOT)
        self.assertEqual(first_bytes, {name: path.read_bytes() for name, path in second.items()})
        freeze = json.loads(first["predictionFreeze"].read_text(encoding="utf-8"))
        audit = json.loads(first["invarianceAudit"].read_text(encoding="utf-8"))
        reconciliation = json.loads(first["reconciliation"].read_text(encoding="utf-8"))
        acceptance = json.loads(first["acceptance"].read_text(encoding="utf-8"))
        self.assertEqual(audit["predictionFreezeHash"], freeze["predictionFreezeHash"])
        self.assertEqual(reconciliation["successorS2PredictionFreezeHash"], freeze["predictionFreezeHash"])
        self.assertEqual(acceptance["predictionFreezeHash"], freeze["predictionFreezeHash"])
        self.assertEqual(acceptance["invarianceAuditHash"], audit["invarianceAuditHash"])
        self.assertEqual(acceptance["lineageReconciliationHash"], reconciliation["lineageReconciliationHash"])
        self.assertEqual(acceptance["status"], "S2_SOURCE_LINEAGE_RECONCILED_AND_BLINDED_REFREEZE_COMPLETE_CENTRAL_REVIEW_REQUIRED")
        self.assertEqual(acceptance["nextGate"], "INDEPENDENT_CENTRAL_REVIEW_BEFORE_MO_R4A_S3")
        self.assertFalse(acceptance["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
