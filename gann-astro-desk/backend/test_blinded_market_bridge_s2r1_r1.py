"""Outcome-blind regression contract for the Saravali-adjudicated S2R1-R1 successor."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
BACKEND_ROOT = PROJECT_ROOT / "gann-astro-desk" / "backend"
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
for root in (PROJECT_ROOT, PROJECT_ROOT / "gann-astro-desk", BACKEND_ROOT, LAB_ROOT, INSTRUMENT_SBC_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

import blinded_market_bridge_s2r1_r1 as successor  # noqa: E402


class BlindedMarketBridgeS2R1R1Tests(unittest.TestCase):
    """A source pagination/orientation correction cannot authorize market behavior."""

    def setUp(self) -> None:
        self.registry_path = (
            PROJECT_ROOT
            / "configs"
            / "research"
            / "machine_interpretation"
            / "experimental_market_hypothesis_registry_s2r1_r1_v1.json"
        )

    def test_registry_is_two_side_local_successors_with_historical_bindings(self) -> None:
        raw = json.loads(self.registry_path.read_text(encoding="utf-8"))
        schema = json.loads(self.registry_path.with_suffix(".schema.json").read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(raw))
        self.assertFalse(schema["$defs"]["hypothesis"]["additionalProperties"])
        self.assertEqual(set(schema["$defs"]["hypothesis"]["required"]), set(raw["entries"][0]))
        registry = successor._load_registry(self.registry_path)
        self.assertEqual(registry.raw["historicalS2R1RegistryHash"], successor.HISTORICAL_S2R1_REGISTRY_HASH)
        self.assertEqual(registry.raw["historicalS2R1PredictionFreezeHash"], successor.HISTORICAL_S2R1_FREEZE_HASH)
        self.assertEqual(registry.registry_hash, "D76E208F52511BD8B5380BB32049B0C47275261443E587E3E09184E439FF3110")
        self.assertEqual(set(registry.entries_by_side), {"USD", "JPY"})
        self.assertEqual({entry.hypothesis_id for entry in registry.entries_by_side.values()}, set(successor.S2R1_R1_HYPOTHESIS_IDS.values()))
        self.assertTrue(all(value is False for value in registry.raw["guardrails"].values()))

    def test_24_event_freeze_is_outcome_blind_and_preserves_exact_states(self) -> None:
        with patch.object(successor.operators, "configure_ephemeris", side_effect=AssertionError("S2R1-R1 must not regenerate astronomy")) as ephemeris:
            freeze = successor.build_s2r1_r1_blinded_prediction_freeze(PROJECT_ROOT)
        ephemeris.assert_not_called()
        self.assertEqual(freeze["predictionFreezeHash"], "83F1456271B510468A0DF28C66AD705318CD06F5D5B5E0566F6DE05FA06CF71D")
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
        for row in freeze["predictions"]:
            self.assertEqual(row["identityStatus"], "SINGLE_PASS_VERIFIED")
            self.assertFalse(row["priceDataRead"])
            self.assertFalse(row["outcomeDataSeen"])
            self.assertFalse(row["executionAllowed"])
            self.assertIsNone(row["signedUnit"])
            self.assertFalse(row["magnitudeConfigured"])
            self.assertEqual(row["overallAstrologicalInterpretation"], "UNKNOWN_ASTRO_STATE")

    def test_lineage_reconciliation_has_no_real_event_state_or_prediction_change(self) -> None:
        freeze = successor.build_s2r1_r1_blinded_prediction_freeze(PROJECT_ROOT)
        reconciliation = successor.build_s2r1_r1_lineage_reconciliation(PROJECT_ROOT, successor_freeze=freeze)
        self.assertEqual(reconciliation["comparisonSummary"], {"rowCount": 49, "comparableDirectedPairCount": 42, "agreementCount": 41, "conflictCount": 1, "notComparableCount": 7, "unresolvedCount": 0})
        self.assertEqual(reconciliation["pilotRelevantConflicts"], [])
        self.assertEqual(reconciliation["summary"]["changedNaturalStateCount"], 0)
        self.assertEqual(reconciliation["summary"]["changedCompoundEventCount"], 0)
        self.assertEqual(reconciliation["summary"]["changedPredictionCount"], 0)
        self.assertEqual(reconciliation["summary"]["unchangedPredictionCount"], 24)
        for row in reconciliation["eventDiff"]:
            self.assertEqual(row["oldNaturalRelationshipState"], row["newNaturalRelationshipState"])
            self.assertFalse(row["compoundStateChanged"])
            self.assertFalse(row["predictionChanged"])
            self.assertFalse(row["eventIdentityChanged"])
            self.assertFalse(row["astronomyChanged"])

    def test_materialized_artifacts_are_deterministic_and_require_central_review(self) -> None:
        first = successor.write_s2r1_r1_artifacts(PROJECT_ROOT)
        first_bytes = {name: path.read_bytes() for name, path in first.items()}
        second = successor.write_s2r1_r1_artifacts(PROJECT_ROOT)
        self.assertEqual(first_bytes, {name: path.read_bytes() for name, path in second.items()})
        freeze = json.loads(first["predictionFreeze"].read_text(encoding="utf-8"))
        audit = json.loads(first["invarianceAudit"].read_text(encoding="utf-8"))
        reconciliation = json.loads(first["reconciliation"].read_text(encoding="utf-8"))
        acceptance = json.loads(first["acceptance"].read_text(encoding="utf-8"))
        self.assertEqual(audit["predictionFreezeHash"], freeze["predictionFreezeHash"])
        self.assertEqual(reconciliation["successorS2R1R1PredictionFreezeHash"], freeze["predictionFreezeHash"])
        self.assertEqual(acceptance["predictionFreezeHash"], freeze["predictionFreezeHash"])
        self.assertEqual(acceptance["invarianceAuditHash"], audit["invarianceAuditHash"])
        self.assertEqual(acceptance["lineageReconciliationHash"], reconciliation["lineageReconciliationHash"])
        self.assertEqual(acceptance["status"], "S2R1_R1_SOURCE_ADJUDICATED_AND_BLINDED_FREEZE_COMPLETE_CENTRAL_REVIEW_REQUIRED")
        self.assertEqual(acceptance["nextGate"], "INDEPENDENT_CENTRAL_REVIEW_BEFORE_MO_R4A_S3")
        self.assertFalse(acceptance["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
