"""Focused MO-R4A-S3R1-R1 correction and acquisition-contract tests."""

from __future__ import annotations

import copy
import itertools
import json
import math
import os
import sys
import unittest
from datetime import datetime, timezone
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
import outcome_analysis_s3r1 as historical_s3r1  # noqa: E402
import outcome_analysis_s3r1_r1 as s3r1_r1  # noqa: E402


class OutcomeAnalysisS3R1R1Tests(unittest.TestCase):
    """R1 fixes are independently derived, outcome-blind, and fail closed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.acquisition = s3r1_r1.build_market_data_acquisition_contract(PROJECT_ROOT)
        cls.preregistration = s3r1_r1.build_s3r1_r1_preregistration(PROJECT_ROOT)
        cls.population = s3r1_r1.build_s3r1_r1_primary_population(PROJECT_ROOT)
        cls.clusters = s3r1_r1.build_s3r1_r1_overlap_clusters(PROJECT_ROOT, population=cls.population)
        cls.invariance = s3r1_r1.build_s3r1_r1_invariance_audit(
            PROJECT_ROOT,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
        )
        cls.core = s3r1_r1.build_analysis_core_manifest(
            cls.preregistration,
            cls.population,
            cls.clusters,
            cls.invariance,
            cls.acquisition,
        )
        cls.acceptance = s3r1_r1.build_s3r1_r1_acceptance_manifest(
            PROJECT_ROOT,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
            invariance=cls.invariance,
            core=cls.core,
            acquisition_contract=cls.acquisition,
        )
        cls.disposition = s3r1_r1.build_s3r1_r1_astra_disposition(PROJECT_ROOT)
        cls.artifacts = s3r1_r1.write_s3r1_r1_artifacts(PROJECT_ROOT)

    def _ticks(self, *rows: tuple[str, object, object]) -> list[dict[str, object]]:
        return [{"timestampUtc": timestamp, "bid": bid, "ask": ask} for timestamp, bid, ask in rows]

    @staticmethod
    def _rehash(value: dict[str, object], key: str) -> dict[str, object]:
        value[key] = s3r1_r1._canonical_hash(s3r1_r1._without_hash(value, key))
        return value

    def test_successor_files_match_builders_and_predecessor_hashes_remain_immutable(self) -> None:
        expected = {
            "acquisition": self.acquisition,
            "preregistration": self.preregistration,
            "population": self.population,
            "clusters": self.clusters,
            "invariance": self.invariance,
            "core": self.core,
            "acceptance": self.acceptance,
            "disposition": self.disposition,
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                path = self.artifacts[name]
                self.assertEqual(json.loads(path.read_text(encoding="utf-8")), value)
        old_expected = {
            "preregistration": s3r1_r1.HISTORICAL_S3R1_PREREGISTRATION_HASH,
            "population": s3r1_r1.HISTORICAL_S3R1_PRIMARY_POPULATION_HASH,
            "clusters": s3r1_r1.HISTORICAL_S3R1_OVERLAP_CLUSTERS_HASH,
            "invariance": s3r1_r1.HISTORICAL_S3R1_INVARIANCE_HASH,
            "core": s3r1_r1.HISTORICAL_S3R1_CORE_HASH,
        }
        old_paths = {
            "preregistration": historical_s3r1.DEFAULT_PREREGISTRATION_PATH,
            "population": historical_s3r1.DEFAULT_PRIMARY_POPULATION_PATH,
            "clusters": historical_s3r1.DEFAULT_OVERLAP_CLUSTERS_PATH,
            "invariance": historical_s3r1.DEFAULT_INVARIANCE_PATH,
            "core": historical_s3r1.DEFAULT_CORE_MANIFEST_PATH,
        }
        old_keys = {
            "preregistration": "preregistrationHash",
            "population": "primaryPopulationHash",
            "clusters": "overlapClustersHash",
            "invariance": "analysisPlanInvarianceAuditHash",
            "core": "analysisCoreManifestHash",
        }
        for name, path in old_paths.items():
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(value[old_keys[name]], old_expected[name])
            self.assertEqual(s3._canonical_hash({key: item for key, item in value.items() if key != old_keys[name]}), old_expected[name])

    def test_acceptance_rejects_stale_and_rehashed_component_attacks(self) -> None:
        # A: removed row with the stale hash; B: removed row with a fresh hash.
        stale = copy.deepcopy(self.population)
        stale["primaryMarketScorableRows"].pop()
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, population=stale)
        rehashed = copy.deepcopy(stale)
        self._rehash(rehashed, "primaryPopulationHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, population=rehashed)

        # C: altered accounting with a self-consistent hash is still rejected.
        altered_count = copy.deepcopy(self.population)
        altered_count["populationCounts"]["primaryMarketScorableCount"] = 12
        self._rehash(altered_count, "primaryPopulationHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, population=altered_count)

        # D: a malicious cluster payload cannot be admitted by rehashing it.
        malicious_clusters = copy.deepcopy(self.clusters)
        malicious_clusters["clusters"][0]["memberEventIds"] = ["MALICIOUS_EVENT"]
        self._rehash(malicious_clusters, "overlapClustersHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, clusters=malicious_clusters)

        # E: a changed event identity is rejected even with a self-consistent hash.
        altered_event = copy.deepcopy(self.population)
        altered_event["primaryMarketScorableRows"][0]["eventId"] = "ALTERED_EVENT_ID"
        self._rehash(altered_event, "primaryPopulationHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, population=altered_event)

        # F: an altered frozen interval is not admitted by rehashing it.
        altered_interval = copy.deepcopy(self.acquisition)
        altered_interval["frozenIntervalSet"]["intervals"][0]["separatingEndUtc"] = "2030-01-01T00:00:00Z"
        self._rehash(altered_interval, "marketDataAcquisitionContractHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, acquisition_contract=altered_interval)

        # G: validation direction and invariance rows are independently protected.
        altered_mapping = copy.deepcopy(self.preregistration)
        altered_mapping["validationMapping"]["USD_SUPPORTIVE"] = "DOWN"
        self._rehash(altered_mapping, "preregistrationHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, preregistration=altered_mapping)
        altered_invariance = copy.deepcopy(self.invariance)
        altered_invariance["rows"][0]["eventHashUnchanged"] = False
        self._rehash(altered_invariance, "analysisPlanInvarianceAuditHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, invariance=altered_invariance)

        # H: mismatched acquisition binding and malformed core are rejected.
        mismatched_core = copy.deepcopy(self.core)
        mismatched_core["marketDataAcquisitionContractHash"] = "A" * 64
        self._rehash(mismatched_core, "analysisCoreManifestHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, core=mismatched_core)
        malformed_core = copy.deepcopy(self.core)
        malformed_core["contract"] = "MALFORMED_CORE_CONTRACT"
        self._rehash(malformed_core, "analysisCoreManifestHash")
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, core=malformed_core)

        # I: the historical core is stale for R1; fresh derivation succeeds.
        old_core = json.loads(historical_s3r1.DEFAULT_CORE_MANIFEST_PATH.read_text(encoding="utf-8"))
        with self.assertRaises(s3r1_r1.OutcomeAnalysisS3R1R1Error):
            s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT, core=old_core)
        fresh = s3r1_r1.build_s3r1_r1_acceptance_manifest(PROJECT_ROOT)
        self.assertEqual(fresh, self.acceptance)
        self.assertEqual(fresh["analysisCoreManifestHash"], self.core["analysisCoreManifestHash"])
        self.assertEqual(fresh["populationAccounting"], self.population["populationCounts"])

    def test_historical_acceptance_builder_rebuilds_supplied_core(self) -> None:
        old_core = historical_s3r1.build_analysis_core_manifest(
            historical_s3r1.build_s3r1_preregistration(PROJECT_ROOT),
            historical_s3r1.build_s3r1_primary_population(PROJECT_ROOT),
            historical_s3r1.build_s3r1_overlap_clusters(PROJECT_ROOT),
            historical_s3r1.build_s3r1_invariance_audit(PROJECT_ROOT),
        )
        old_core["preregistrationHash"] = "A" * 64
        old_core = self._rehash(old_core, "analysisCoreManifestHash")
        with self.assertRaises(historical_s3r1.OutcomeAnalysisS3R1Error):
            historical_s3r1.build_s3r1_acceptance_manifest(PROJECT_ROOT, core=old_core)

    def test_numeric_matrix_uses_stable_midpoint_and_preserves_zero_move(self) -> None:
        up = s3r1_r1.score_synthetic_interval_s3r1_r1(
            self._ticks(("2030-01-01T00:00:00Z", 100, 100), ("2030-01-01T00:01:00Z", 101, 101)),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T00:02:00Z",
            validation_expected_pair_direction="UP",
        )
        down = s3r1_r1.score_synthetic_interval_s3r1_r1(
            self._ticks(("2030-01-01T00:00:00Z", 101, 101), ("2030-01-01T00:01:00Z", 100, 100)),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T00:02:00Z",
            validation_expected_pair_direction="DOWN",
        )
        zero = s3r1_r1.score_synthetic_interval_s3r1_r1(
            self._ticks(("2030-01-01T00:00:00Z", 100, 100), ("2030-01-01T00:01:00Z", 100, 100)),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T00:02:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual((up["realizedDirection"], up["hit"]), ("UP", 1))
        self.assertEqual((down["realizedDirection"], down["hit"]), ("DOWN", 1))
        self.assertEqual((zero["realizedDirection"], zero["hit"]), ("ZERO_MOVE", 0))

        max_value = float.fromhex("0x1.fffffffffffffp+1023")
        large = s3r1_r1.score_synthetic_interval_s3r1_r1(
            self._ticks(("2030-01-01T00:00:00Z", 1.0, max_value), ("2030-01-01T00:01:00Z", 1.0, max_value / 2)),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T00:02:00Z",
            validation_expected_pair_direction="DOWN",
        )
        self.assertTrue(math.isfinite(large["startMidpoint"]))
        self.assertTrue(math.isfinite(large["endMidpoint"]))
        self.assertTrue(math.isfinite(large["logReturn"]))

        tiny = s3r1_r1.score_synthetic_interval_s3r1_r1(
            self._ticks(("2030-01-01T00:00:00Z", 1e-300, 1e-300), ("2030-01-01T00:01:00Z", 2e-300, 2e-300)),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T00:02:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(tiny["realizedDirection"], "UP")
        self.assertTrue(math.isfinite(tiny["logReturn"]))

    def test_numeric_invalidity_matrix_never_becomes_zero_move(self) -> None:
        for field in ("bid", "ask"):
            for invalid in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(field=field, invalid=invalid):
                    bad_bid = invalid if field == "bid" else 1.0
                    bad_ask = invalid if field == "ask" else 1.0
                    result = s3r1_r1.score_synthetic_interval_s3r1_r1(
                        self._ticks(("2030-01-01T00:00:00Z", bad_bid, bad_ask), ("2030-01-01T00:01:00Z", 1, 1)),
                        applying_start_utc="2030-01-01T00:00:00Z",
                        separating_end_utc="2030-01-01T00:02:00Z",
                        validation_expected_pair_direction="UP",
                    )
                    self.assertEqual(result["dataStatus"], "DATA_NUMERIC_INVALID_UNSCORABLE")
                    self.assertNotEqual(result.get("realizedDirection"), "ZERO_MOVE")
        derived_nonfinite = s3._numeric_return_or_invalid(
            s3.CanonicalTick(datetime(2030, 1, 1, tzinfo=timezone.utc), -float.fromhex("0x1.fffffffffffffp+1023"), float.fromhex("0x1.fffffffffffffp+1023"), 0),
            s3.CanonicalTick(datetime(2030, 1, 1, tzinfo=timezone.utc), 1.0, 1.0, 1),
        )
        self.assertEqual(derived_nonfinite[1], "NONFINITE_DERIVED_MIDPOINT")
        self.assertEqual(self.preregistration["numericInvalidityPolicy"]["invalidStatus"], "DATA_NUMERIC_INVALID_UNSCORABLE")
        self.assertFalse(self.preregistration["numericInvalidityPolicy"]["denominatorShrinkAllowed"])

    def test_interval_scoped_conflict_and_price_policy(self) -> None:
        start = "2030-01-01T00:00:00Z"
        end = "2030-01-01T01:00:00Z"
        inside_conflict = self._ticks(
            ("2030-01-01T00:10:00Z", 100, 100.2),
            ("2030-01-01T00:30:00Z", 101, 101.2),
            ("2030-01-01T00:30:00Z", 101.1, 101.3),
        )
        result = s3r1_r1.score_synthetic_interval_s3r1_r1(
            inside_conflict,
            applying_start_utc=start,
            separating_end_utc=end,
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(result["dataStatus"], "DATA_CONFLICT_UNSCORABLE")

        outside_bad = self._ticks(
            ("2029-12-31T23:00:00Z", -1, -1),
            ("2030-01-01T00:10:00Z", 100, 100.2),
            ("2030-01-01T00:30:00Z", 101, 101.2),
            ("2030-01-01T01:00:00Z", float("nan"), float("nan")),
        )
        result = s3r1_r1.score_synthetic_interval_s3r1_r1(
            outside_bad,
            applying_start_utc=start,
            separating_end_utc=end,
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(result["dataStatus"], "SCORABLE_SYNTHETIC_ONLY")

        before_and_after_conflicts = self._ticks(
            ("2029-12-31T23:00:00Z", 10, 10),
            ("2029-12-31T23:00:00Z", 11, 11),
            ("2030-01-01T00:10:00Z", 100, 100),
            ("2030-01-01T00:30:00Z", 100, 100),
            ("2030-01-01T01:00:00Z", 20, 20),
            ("2030-01-01T01:00:00Z", 21, 21),
        )
        result = s3r1_r1.score_synthetic_interval_s3r1_r1(
            before_and_after_conflicts,
            applying_start_utc=start,
            separating_end_utc=end,
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(result["dataStatus"], "SCORABLE_SYNTHETIC_ONLY")

        with self.assertRaises(s3.SyntheticTickInputError):
            s3r1_r1.score_synthetic_interval_s3r1_r1(
                self._ticks(("not-a-timestamp", -1, -1), ("2030-01-01T00:10:00Z", 100, 100), ("2030-01-01T00:30:00Z", 101, 101)),
                applying_start_utc=start,
                separating_end_utc=end,
                validation_expected_pair_direction="UP",
            )

    def test_half_open_edges_duplicates_and_minimum_tick_rules(self) -> None:
        selected = self._ticks(
            ("2029-12-31T23:59:59Z", 9, 9),
            ("2030-01-01T00:00:00Z", 100, 100),
            ("2030-01-01T00:00:00Z", 100, 100),
            ("2030-01-01T00:30:00Z", 101, 101),
            ("2030-01-01T01:00:00Z", 999, 999),
        )
        result = s3r1_r1.score_synthetic_interval_s3r1_r1(
            selected,
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(result["selectedTickCount"], 2)
        self.assertEqual(result["endTickUtc"], "2030-01-01T00:30:00Z")
        one = s3r1_r1.score_synthetic_interval_s3r1_r1(
            self._ticks(("2030-01-01T00:00:00Z", 100, 100)),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(one["dataStatus"], "DATA_UNSCORABLE")
        two = s3r1_r1.score_synthetic_interval_s3r1_r1(
            self._ticks(("2030-01-01T00:00:00Z", 100, 100), ("2030-01-01T00:01:00Z", 100, 100)),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(two["dataStatus"], "SCORABLE_SYNTHETIC_ONLY")

    def test_acquisition_contract_has_exact_39_frozen_intervals_without_provider_access(self) -> None:
        frozen = self.acquisition["frozenIntervalSet"]
        self.assertEqual((frozen["actualCount"], frozen["minus7Count"], frozen["plus7Count"], frozen["totalCount"]), (13, 13, 13, 39))
        self.assertEqual(len(frozen["intervals"]), 39)
        self.assertEqual(self.acquisition["status"], "PARTIALLY_RESOLVED_OUTCOME_UNLOCK_BLOCKED")
        self.assertFalse(self.acquisition["providerAccessPerformed"])
        self.assertFalse(self.acquisition["marketOutcomeRead"])
        self.assertFalse(self.acquisition["executionAllowed"])
        self.assertFalse(self.acquisition["revisionPolicy"]["manualRepairAllowed"])
        self.assertFalse(self.acquisition["revisionPolicy"]["fallbackProviderAllowed"])
        self.assertFalse(self.acquisition["revisionPolicy"]["substitutionAllowed"])
        self.assertFalse(self.acquisition["revisionPolicy"]["outcomeDrivenRetryAllowed"])
        for field in ("rawBytesSha256", "parsedTicksSha256", "rawRetention"):
            self.assertEqual(self.acquisition["futureCaptureRequirements"][field], "REQUIRED_AT_OUTCOME_PHASE" if field != "rawRetention" else "RETAIN_UNCHANGED_FOR_AUDIT")
        self.assertNotIn("logReturn", json.dumps(self.acquisition, sort_keys=True))
        self.assertNotIn("startMidpoint", json.dumps(self.acquisition, sort_keys=True))

    def test_acquisition_shift_rows_preserve_identity_label_side_and_duration(self) -> None:
        intervals = self.acquisition["frozenIntervalSet"]["intervals"]
        by_horizon = {horizon: [row for row in intervals if row["horizon"] == horizon] for horizon in ("ACTUAL", "MINUS_7", "PLUS_7")}
        self.assertEqual([len(by_horizon[key]) for key in by_horizon], [13, 13, 13])
        for actual, minus7, plus7 in zip(by_horizon["ACTUAL"], by_horizon["MINUS_7"], by_horizon["PLUS_7"], strict=True):
            for shifted, days in ((minus7, -7), (plus7, 7)):
                self.assertEqual(shifted["eventId"], actual["eventId"])
                self.assertEqual(shifted["sideIdentity"], actual["sideIdentity"])
                self.assertEqual(shifted["frozenLabel"], actual["frozenLabel"])
                self.assertEqual(shifted["durationSeconds"], actual["durationSeconds"])
                self.assertEqual(shifted["shiftCalendarDays"], days)
        self.assertTrue(all(row["halfOpen"] for row in intervals))

    def test_successor_population_and_statistical_plan_remain_frozen(self) -> None:
        self.assertEqual(self.population["populationCounts"]["frozenEventCount"], 24)
        self.assertEqual(self.population["populationCounts"]["primaryMarketScorableCount"], 13)
        self.assertEqual(len(s3.enumerate_within_side_label_assignments(self.population["primaryMarketScorableRows"])), 40)
        self.assertEqual(tuple(row["eventId"] for row in self.population["primaryMarketScorableRows"]), s3.EXPECTED_PRIMARY_EVENT_ORDER)
        self.assertEqual(tuple(cluster["clusterId"] for cluster in self.clusters["clusters"]), ("C1", "C2", "C3", "C4"))
        self.assertEqual(self.preregistration["timeShiftDiagnostics"]["shiftsCalendarDays"], [-7, 7])
        self.assertEqual(self.preregistration["primaryStatistic"]["hitDefinition"], "hit_i=1 if q_i*r_i>0 else 0")
        self.assertEqual(self.preregistration["exactPermutation"]["assignmentCount"], 40)
        self.assertFalse(self.preregistration["amendmentAndStopping"]["marketOutcomeInS3Artifacts"])

    def test_schema_hash_disposition_and_acceptance_fail_closed(self) -> None:
        schema = json.loads(self.artifacts["schema"].read_text(encoding="utf-8"))
        s3r1_r1.validate_json_schema_instance(self.preregistration, schema)
        s3r1_r1.validate_s3r1_r1_preregistration(self.preregistration, PROJECT_ROOT)
        s3r1_r1.validate_s3r1_r1_primary_population(self.population, PROJECT_ROOT)
        s3r1_r1.validate_s3r1_r1_overlap_clusters(self.clusters, PROJECT_ROOT)
        s3r1_r1.validate_s3r1_r1_invariance_audit(self.invariance, PROJECT_ROOT)
        s3r1_r1.validate_market_data_acquisition_contract(self.acquisition, PROJECT_ROOT)
        s3r1_r1.validate_analysis_core_manifest(self.core, PROJECT_ROOT)
        s3r1_r1.validate_s3r1_r1_acceptance_manifest(self.acceptance, PROJECT_ROOT)
        self.assertEqual(self.acceptance["status"], "PRE_OUTCOME_ACQUISITION_CONTRACT_INCOMPLETE")
        self.assertEqual(self.acceptance["nextGate"], "CENTRAL_REVIEW")
        self.assertEqual(self.disposition["verdict"], "PRE_OUTCOME_CORRECTION_REQUIRED")
        self.assertEqual(self.disposition["branch"], "BRANCH_B")
        self.assertEqual(
            [finding["findingType"] for finding in self.disposition["findings"]],
            [
                "HIGH_ACCEPTANCE_VALIDATION_BYPASS",
                "MEDIUM_NUMERICAL_INVALIDITY",
                "MEDIUM_PRE_REQUEST_ACQUISITION_REQUIREMENTS",
            ],
        )
        self.assertTrue(all(value is False for value in self.acceptance["outcomeAccessFlags"].values()))
        self.assertFalse(self.acceptance["executionAllowed"])

    def test_exhaustive_binary_vectors_and_timing_status_are_deterministic(self) -> None:
        # Exhaust the 13-bit hit-vector space without attaching any market data.
        observed_sums = {sum(bits) for bits in itertools.product((0, 1), repeat=13)}
        self.assertEqual(len(observed_sums), 14)
        self.assertEqual(2**13, 8192)
        timing_results = {
            s3r1_r1.s3r1.timing_specificity_status(actual_hit_count=actual, minus7_hit_count=minus7, plus7_hit_count=plus7)
            for actual in range(14)
            for minus7 in range(14)
            for plus7 in range(14)
        }
        self.assertEqual(len(timing_results), 2)

    def test_no_provider_outcome_or_s4_path_is_present(self) -> None:
        source = (BACKEND_ROOT / "outcome_analysis_s3r1_r1.py").read_text(encoding="utf-8")
        self.assertNotIn("requests", source)
        self.assertNotIn("yfinance", source)
        self.assertNotIn("ccxt", source)
        self.assertNotIn("outcome_analysis_s4", source)
        for value in (self.acquisition, self.preregistration, self.population, self.clusters, self.invariance, self.core, self.acceptance, self.disposition):
            serialized = json.dumps(value, sort_keys=True)
            self.assertNotIn('"logReturn":', serialized)
            self.assertNotIn('"startMidpoint":', serialized)
            self.assertNotIn('"endMidpoint":', serialized)
        self.assertFalse((BACKEND_ROOT / "outcome_analysis_s4.py").exists())


if __name__ == "__main__":
    unittest.main()
