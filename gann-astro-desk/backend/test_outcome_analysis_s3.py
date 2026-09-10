"""Synthetic-only regression contract for the MO-R4A-S3 preregistration."""

from __future__ import annotations

import json
import os
import sys
import unittest
from datetime import datetime
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

import outcome_analysis_s3 as s3  # noqa: E402


class OutcomeAnalysisS3Tests(unittest.TestCase):
    """S3 freezes a synthetic-testable analysis plan without reading outcomes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.preregistration = s3.build_outcome_analysis_preregistration(PROJECT_ROOT)
        cls.population = s3.build_primary_analysis_population(PROJECT_ROOT)
        cls.clusters = s3.build_overlap_clusters(PROJECT_ROOT, population=cls.population)

    def _ticks(self, *rows: tuple[str, float, float]) -> list[dict[str, object]]:
        return [{"timestampUtc": timestamp, "bid": bid, "ask": ask} for timestamp, bid, ask in rows]

    def test_preregistration_binds_all_six_upstream_hashes_and_strict_schema(self) -> None:
        checked_in = json.loads(s3.DEFAULT_PREREGISTRATION_PATH.read_text(encoding="utf-8"))
        schema = json.loads(s3.DEFAULT_PREREGISTRATION_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked_in, self.preregistration)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(checked_in))
        self.assertEqual(checked_in["upstreamHashes"], s3.EXPECTED_UPSTREAM_HASHES)
        self.assertEqual(checked_in["status"], "OUTCOME_ANALYSIS_PREREGISTRATION_COMPLETE_CENTRAL_REVIEW_REQUIRED")
        self.assertEqual(checked_in["nextGate"], "INDEPENDENT_CENTRAL_REVIEW_BEFORE_ASTRA_PRE_OUTCOME_AUDIT")
        s3.validate_preregistration(checked_in)

    def test_preregistration_freezes_provider_contract_without_provider_access(self) -> None:
        source = self.preregistration["marketDataSource"]
        self.assertEqual(source["provider"], "DUKASCOPY_HISTORICAL_USDJPY_TICK_SERVICE")
        self.assertEqual(source["instrument"], "USDJPY")
        self.assertEqual(source["quoteConvention"], "JPY_PER_USD")
        self.assertEqual(source["timestampConvention"], "UTC_ONLY")
        self.assertFalse(source["fallbackProviderAllowed"])
        self.assertFalse(source["s3ProviderAccessAllowed"])
        self.assertFalse(self.preregistration["validationMapping"]["signedUnitCreated"])
        self.assertFalse(self.preregistration["validationMapping"]["pairRawCreated"])
        self.assertFalse(self.preregistration["validationMapping"]["pairDisplayCreated"])

    def test_population_is_24_14_13_1_3_7_and_contains_the_exact_primary_ids(self) -> None:
        counts = self.population["populationCounts"]
        self.assertEqual(
            counts,
            {
                "frozenEventCount": 24,
                "directionalCount": 14,
                "primaryMarketScorableCount": 13,
                "structuralWeekendExclusionCount": 1,
                "neutralCount": 3,
                "unknownAbstainCount": 7,
                "usdPrimaryCount": 5,
                "jpyPrimaryCount": 8,
                "usdSupportivePrimaryCount": 1,
                "usdAdversePrimaryCount": 4,
                "jpySupportivePrimaryCount": 7,
                "jpyAdversePrimaryCount": 1,
            },
        )
        self.assertEqual(tuple(row["eventId"] for row in self.population["primaryMarketScorableRows"]), s3.EXPECTED_PRIMARY_EVENT_ORDER)
        self.assertEqual(
            [(row["sideIdentity"], row["pressureState"]) for row in self.population["primaryMarketScorableRows"]],
            [
                ("JPY", "SUPPORTIVE"), ("JPY", "SUPPORTIVE"), ("JPY", "SUPPORTIVE"),
                ("USD", "SUPPORTIVE"), ("JPY", "SUPPORTIVE"), ("JPY", "SUPPORTIVE"),
                ("USD", "ADVERSE"), ("JPY", "SUPPORTIVE"), ("USD", "ADVERSE"),
                ("JPY", "SUPPORTIVE"), ("JPY", "ADVERSE"), ("USD", "ADVERSE"), ("USD", "ADVERSE"),
            ],
        )
        self.assertEqual(len({row["eventHash"] for row in self.population["allFrozenRows"]}), 24)
        self.assertTrue(all(row["identityStatus"] == "SINGLE_PASS_VERIFIED" for row in self.population["allFrozenRows"]))

    def test_weekend_exclusion_is_retained_but_not_replaced_or_scored(self) -> None:
        exclusion = self.population["structuralExclusion"]
        self.assertEqual(exclusion["eventId"], "TN_BD340A6100B173B5F254EDC1")
        self.assertEqual(exclusion["analysisDisposition"], "PRIMARY_NONTRADING_WEEKEND_EXCLUSION")
        self.assertEqual((exclusion["applyingStartUtc"], exclusion["separatingEndUtc"]), ("2025-04-05T01:45:04Z", "2025-04-05T12:34:35Z"))
        self.assertEqual(datetime.fromisoformat(exclusion["applyingStartUtc"].replace("Z", "+00:00")).weekday(), 5)
        self.assertEqual(datetime.fromisoformat(exclusion["separatingEndUtc"].replace("Z", "+00:00")).weekday(), 5)
        self.assertNotIn(exclusion["eventId"], {row["eventId"] for row in self.population["primaryMarketScorableRows"]})

    def test_validation_mapping_keeps_neutral_and_unknown_out_of_primary_directional_scoring(self) -> None:
        self.assertEqual(s3._validation_expected_pair_direction("USD", "SUPPORTIVE"), "UP")
        self.assertEqual(s3._validation_expected_pair_direction("USD", "ADVERSE"), "DOWN")
        self.assertEqual(s3._validation_expected_pair_direction("JPY", "SUPPORTIVE"), "DOWN")
        self.assertEqual(s3._validation_expected_pair_direction("JPY", "ADVERSE"), "UP")
        self.assertEqual(s3._validation_expected_pair_direction("USD", "NEUTRAL"), "NO_DIRECTIONAL_PREDICTION")
        self.assertEqual(s3._validation_expected_pair_direction("JPY", "UNKNOWN_MORE_EVIDENCE_REQUIRED"), "ABSTAIN")
        neutral_rows = [row for row in self.population["allFrozenRows"] if row["pressureState"] == "NEUTRAL"]
        unknown_rows = [row for row in self.population["allFrozenRows"] if row["pressureState"] == "UNKNOWN_MORE_EVIDENCE_REQUIRED"]
        self.assertTrue(all(row["analysisDisposition"] == "CATEGORICAL_NEUTRAL_NOT_DIRECTIONAL" for row in neutral_rows))
        self.assertTrue(all(row["analysisDisposition"] == "ABSTAIN_UNKNOWN_NOT_DIRECTIONAL" for row in unknown_rows))

    def test_half_open_tick_selection_uses_first_inside_and_last_before_end(self) -> None:
        result = s3.score_synthetic_interval(
            self._ticks(
                ("2025-04-01T00:00:00Z", 100.0, 102.0),
                ("2025-04-01T00:30:00Z", 104.0, 106.0),
                ("2025-04-01T01:00:00Z", 110.0, 112.0),
                ("2025-04-01T01:30:00Z", 200.0, 202.0),
            ),
            applying_start_utc="2025-04-01T00:00:00Z",
            separating_end_utc="2025-04-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(result["dataStatus"], "SCORABLE_SYNTHETIC_ONLY")
        self.assertEqual(result["startTickUtc"], "2025-04-01T00:00:00Z")
        self.assertEqual(result["endTickUtc"], "2025-04-01T00:30:00Z")
        self.assertEqual((result["startMidpoint"], result["endMidpoint"]), (101.0, 105.0))
        self.assertEqual(result["realizedDirection"], "UP")
        self.assertEqual(result["hit"], 1)
        self.assertFalse(result["outsideIntervalRescueUsed"])

    def test_no_outside_interval_rescue_and_same_timestamp_are_unscorable(self) -> None:
        outside_only = s3.score_synthetic_interval(
            self._ticks(
                ("2025-03-31T23:59:00Z", 100.0, 100.0),
                ("2025-04-01T00:30:00Z", 101.0, 101.0),
                ("2025-04-01T01:00:00Z", 102.0, 102.0),
            ),
            applying_start_utc="2025-04-01T00:00:00Z",
            separating_end_utc="2025-04-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(outside_only["dataStatus"], "DATA_UNSCORABLE")
        self.assertEqual(outside_only["selectedTickCount"], 1)
        self.assertFalse(outside_only["outsideIntervalRescueUsed"])
        same_timestamp = s3.score_synthetic_interval(
            self._ticks(
                ("2025-04-01T00:30:00Z", 100.0, 100.0),
                ("2025-04-01T00:30:00Z", 101.0, 101.0),
            ),
            applying_start_utc="2025-04-01T00:00:00Z",
            separating_end_utc="2025-04-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(same_timestamp["dataStatus"], "DATA_UNSCORABLE")
        self.assertEqual(same_timestamp["reason"], "START_AND_END_TICK_SHARE_TIMESTAMP")

    def test_synthetic_return_sign_and_zero_move_rules(self) -> None:
        positive = s3.score_synthetic_interval(
            self._ticks(("2025-04-01T00:00:00Z", 100, 100), ("2025-04-01T00:01:00Z", 101, 101)),
            applying_start_utc="2025-04-01T00:00:00Z", separating_end_utc="2025-04-01T00:02:00Z", validation_expected_pair_direction="UP",
        )
        negative = s3.score_synthetic_interval(
            self._ticks(("2025-04-01T00:00:00Z", 101, 101), ("2025-04-01T00:01:00Z", 100, 100)),
            applying_start_utc="2025-04-01T00:00:00Z", separating_end_utc="2025-04-01T00:02:00Z", validation_expected_pair_direction="DOWN",
        )
        zero = s3.score_synthetic_interval(
            self._ticks(("2025-04-01T00:00:00Z", 100, 100), ("2025-04-01T00:01:00Z", 100, 100)),
            applying_start_utc="2025-04-01T00:00:00Z", separating_end_utc="2025-04-01T00:02:00Z", validation_expected_pair_direction="UP",
        )
        self.assertEqual((positive["realizedDirection"], positive["hit"]), ("UP", 1))
        self.assertEqual((negative["realizedDirection"], negative["hit"]), ("DOWN", 1))
        self.assertEqual((zero["realizedDirection"], zero["hit"]), ("ZERO_MOVE", 0))

    def test_malformed_ticks_are_rejected_and_identical_duplicates_are_deduplicated(self) -> None:
        with self.assertRaises(s3.OutcomeAnalysisS3Error):
            s3.canonicalize_synthetic_ticks(self._ticks(("2025-04-01T00:00:00Z", -1, 1)))
        with self.assertRaises(s3.OutcomeAnalysisS3Error):
            s3.canonicalize_synthetic_ticks(self._ticks(("2025-04-01T00:00:00Z", 2, 1)))
        ticks = s3.canonicalize_synthetic_ticks(self._ticks(
            ("2025-04-01T00:00:00Z", 100, 101),
            ("2025-04-01T00:00:00Z", 100, 101),
            ("2025-04-01T00:00:00Z", 101, 102),
        ))
        self.assertEqual(len(ticks), 2)
        self.assertEqual([tick.source_index for tick in ticks], [0, 2])

    def test_half_open_overlap_clusters_match_the_frozen_transitive_geometry(self) -> None:
        self.assertEqual(tuple((row["clusterId"], tuple(row["memberEventIds"]), row["earliestStartUtc"], row["latestEndUtc"]) for row in self.clusters["clusters"]), s3.EXPECTED_CLUSTERS)
        touching_left = {"applyingStartUtc": "2025-01-01T00:00:00Z", "separatingEndUtc": "2025-01-01T01:00:00Z"}
        touching_right = {"applyingStartUtc": "2025-01-01T01:00:00Z", "separatingEndUtc": "2025-01-01T02:00:00Z"}
        self.assertFalse(s3.intervals_overlap(touching_left, touching_right))
        derived = s3.derive_overlap_clusters([
            {**touching_left, "eventId": "A"}, {**touching_right, "eventId": "B"},
        ])
        self.assertEqual([cluster["memberCount"] for cluster in derived], [1, 1])

    def test_exact_null_contains_observed_assignment_and_has_40_side_local_assignments(self) -> None:
        rows = self.population["primaryMarketScorableRows"]
        assignments = s3.enumerate_within_side_label_assignments(rows)
        self.assertEqual(len(assignments), 40)
        observed = {row["eventId"]: row["pressureState"] for row in rows}
        self.assertIn(observed, assignments)
        result = s3.exact_one_sided_permutation(rows, {row["eventId"]: "UP" for row in rows})
        self.assertEqual(result["assignmentCount"], 40)
        self.assertTrue(result["observedAssignmentIncluded"])
        self.assertEqual(len(result["permutationHitCounts"]), 40)
        self.assertEqual(sum(result["permutationHitHistogram"].values()), 40)
        self.assertGreaterEqual(result["oneSidedPExact"], 0.0)
        self.assertLessEqual(result["oneSidedPExact"], 1.0)

    def test_cluster_metric_equal_weights_clusters_and_shifts_preserve_duration_and_clock(self) -> None:
        rows = self.population["primaryMarketScorableRows"]
        first_cluster_ids = set(self.clusters["clusters"][0]["memberEventIds"])
        hit_by_event = {row["eventId"]: int(row["eventId"] in first_cluster_ids) for row in rows}
        self.assertEqual(s3.cluster_balanced_hit_rate(rows, hit_by_event), 0.25)
        sample = rows[0]
        for shift in (-7, 7):
            shifted = s3.shift_primary_interval(sample, shift)
            original_duration = datetime.fromisoformat(sample["separatingEndUtc"].replace("Z", "+00:00")) - datetime.fromisoformat(sample["applyingStartUtc"].replace("Z", "+00:00"))
            shifted_duration = datetime.fromisoformat(shifted["separatingEndUtc"].replace("Z", "+00:00")) - datetime.fromisoformat(shifted["applyingStartUtc"].replace("Z", "+00:00"))
            self.assertEqual(original_duration, shifted_duration)
            self.assertEqual(shifted["applyingStartUtc"][11:], sample["applyingStartUtc"][11:])

    def test_survival_rule_never_shrinks_the_primary_denominator(self) -> None:
        self.assertEqual(
            s3.primary_survival_status(all_primary_validly_scorable=False, primary_hit_rate=None, exact_p_value=None, cluster_balanced_rate=None),
            "PRIMARY_EVALUATION_INVALID_DATA_INCOMPLETE",
        )
        self.assertEqual(
            s3.primary_survival_status(all_primary_validly_scorable=True, primary_hit_rate=8 / 13, exact_p_value=0.1, cluster_balanced_rate=0.75),
            "PILOT_ASSOCIATION_SURVIVED",
        )
        self.assertEqual(
            s3.primary_survival_status(all_primary_validly_scorable=True, primary_hit_rate=0.5, exact_p_value=0.1, cluster_balanced_rate=0.75),
            "PILOT_ASSOCIATION_NOT_SURVIVED",
        )

    def test_materialization_is_deterministic_and_rejects_outcome_attachment(self) -> None:
        first = s3.materialize_s3_artifacts(PROJECT_ROOT)
        first_bytes = {name: path.read_bytes() for name, path in first.items()}
        second = s3.materialize_s3_artifacts(PROJECT_ROOT)
        self.assertEqual(first_bytes, {name: path.read_bytes() for name, path in second.items()})
        with self.assertRaises(s3.OutcomeAccessBlockedError):
            s3.materialize_s3_artifacts(PROJECT_ROOT, outcome_source=Path("D:/private/April-2025-USDJPY-ticks.csv"))
        with self.assertRaises(s3.OutcomeAccessBlockedError):
            s3.materialize_s3_artifacts(PROJECT_ROOT, outcome_source="https://example.invalid/USDJPY")

    def test_no_s3_artifact_contains_a_scored_market_outcome_or_enables_a_lock(self) -> None:
        paths = s3.materialize_s3_artifacts(PROJECT_ROOT)
        for key in ("preregistration", "population", "clusters", "invariance", "acceptance"):
            raw = json.loads(paths[key].read_text(encoding="utf-8"))
            serialized = json.dumps(raw, sort_keys=True)
            self.assertNotIn('"logReturn"', serialized)
            self.assertNotIn('"startMidpoint"', serialized)
            self.assertNotIn('"endMidpoint"', serialized)
            flags = raw["outcomeAccessFlags"]
            self.assertEqual(set(flags), set(s3.OUTCOME_ACCESS_FLAGS))
            self.assertTrue(all(value is False for value in flags.values()))
        self.assertFalse(json.loads(paths["acceptance"].read_text(encoding="utf-8"))["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
