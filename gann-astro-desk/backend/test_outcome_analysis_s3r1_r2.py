"""Focused MO-R4A-S3R1-R2 provider-protocol and frozen-plan tests."""

from __future__ import annotations

import copy
import itertools
import json
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]).resolve()
BACKEND_ROOT = PROJECT_ROOT / "gann-astro-desk" / "backend"
for root in (
    PROJECT_ROOT,
    PROJECT_ROOT / "gann-astro-desk",
    BACKEND_ROOT,
    PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects",
    PROJECT_ROOT / "research_labs" / "instrument_relative_sbc",
):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

import outcome_analysis_s3 as s3  # noqa: E402
import outcome_analysis_s3r1_r1 as r1  # noqa: E402
import outcome_analysis_s3r1_r2 as r2  # noqa: E402


class OutcomeAnalysisS3R1R2Tests(unittest.TestCase):
    """R2 source research remains outcome-blind and fails closed on ambiguity."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.artifacts = r2.write_s3r1_r2_artifacts(PROJECT_ROOT)
        cls.evidence = r2.build_protocol_evidence()
        cls.lock = r2.build_source_lock(cls.evidence)
        cls.plan = r2.build_provider_partition_plan(PROJECT_ROOT)
        cls.acquisition = r2.build_market_data_acquisition_contract(
            PROJECT_ROOT,
            protocol_evidence=cls.evidence,
            source_lock=cls.lock,
            partition_plan=cls.plan,
        )
        cls.preregistration = r2.build_s3r1_r2_preregistration(PROJECT_ROOT)
        cls.population = r2.build_s3r1_r2_primary_population(PROJECT_ROOT)
        cls.clusters = r2.build_s3r1_r2_overlap_clusters(PROJECT_ROOT, population=cls.population)
        cls.invariance = r2.build_s3r1_r2_invariance_audit(
            PROJECT_ROOT,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
        )
        cls.core = r2.build_analysis_core_manifest(
            cls.preregistration,
            cls.population,
            cls.clusters,
            cls.invariance,
            cls.acquisition,
            cls.lock,
            cls.plan,
        )
        cls.acceptance = r2.build_s3r1_r2_acceptance_manifest(
            PROJECT_ROOT,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
            invariance=cls.invariance,
            acquisition=cls.acquisition,
            source_lock=cls.lock,
            partition_plan=cls.plan,
            core=cls.core,
        )

    @staticmethod
    def _without_hash(value: dict[str, object], key: str) -> dict[str, object]:
        return {name: item for name, item in value.items() if name != key}

    def test_artifacts_are_deterministic_and_historical_r1_hashes_remain_exact(self) -> None:
        expected = {
            "protocolEvidence": self.evidence,
            "sourceLock": self.lock,
            "partitionPlan": self.plan,
            "acquisition": self.acquisition,
            "preregistration": self.preregistration,
            "population": self.population,
            "clusters": self.clusters,
            "invariance": self.invariance,
            "core": self.core,
            "acceptance": self.acceptance,
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(json.loads(self.artifacts[name].read_text(encoding="utf-8")), value)
        historical = {
            r1.DEFAULT_ACQUISITION_PATH: ("marketDataAcquisitionContractHash", r2.HISTORICAL_R1_ACQUISITION_HASH),
            r1.DEFAULT_PREREGISTRATION_PATH: ("preregistrationHash", r2.HISTORICAL_R1_PREREGISTRATION_HASH),
            r1.DEFAULT_PRIMARY_POPULATION_PATH: ("primaryPopulationHash", r2.HISTORICAL_R1_POPULATION_HASH),
            r1.DEFAULT_OVERLAP_CLUSTERS_PATH: ("overlapClustersHash", r2.HISTORICAL_R1_CLUSTERS_HASH),
            r1.DEFAULT_INVARIANCE_PATH: ("analysisPlanInvarianceAuditHash", r2.HISTORICAL_R1_INVARIANCE_HASH),
            r1.DEFAULT_CORE_MANIFEST_PATH: ("analysisCoreManifestHash", r2.HISTORICAL_R1_CORE_HASH),
            r1.DEFAULT_ACCEPTANCE_PATH: ("acceptanceManifestHash", r2.HISTORICAL_R1_ACCEPTANCE_HASH),
        }
        for path, (hash_key, expected_hash) in historical.items():
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(value[hash_key], expected_hash)
            self.assertEqual(s3._canonical_hash(self._without_hash(value, hash_key)), expected_hash)
        self.assertEqual(self.core["upstreamHashes"], r2.EXPECTED_UPSTREAM_HASHES)

    def test_protocol_evidence_is_explicit_about_the_single_parser_blocker(self) -> None:
        facts = {fact["factId"]: fact for fact in self.evidence["criticalFacts"]}
        self.assertEqual(self.evidence["selectedProviderProduct"], r2.PROVIDER_PRODUCT)
        self.assertEqual(self.evidence["criticalUnresolvedFactIds"], ["COMPRESSION_WRAPPER"])
        self.assertEqual(facts["COMPRESSION_WRAPPER"]["status"], "PROTOCOL_SOURCE_CONFLICT")
        self.assertFalse(facts["COMPRESSION_WRAPPER"]["machineUseAuthorized"])
        self.assertIn("raw LZMA", facts["COMPRESSION_WRAPPER"]["quotedOrParaphrasedEvidence"])
        self.assertIn("lzma.decompress", facts["COMPRESSION_WRAPPER"]["conflictingEvidence"])
        self.assertEqual(self.lock["sourceConflict"]["status"], "PROTOCOL_SOURCE_CONFLICT")
        self.assertFalse(self.evidence["providerProtocolFullyClosed"])
        self.assertEqual(self.acquisition["parser"]["status"], "NOT_IMPLEMENTED_PROTOCOL_SOURCE_CONFLICT")
        self.assertFalse((BACKEND_ROOT / "dukascopy_tick_parser_s3r1_r2.py").exists())

    def test_daily_partition_plan_exactly_covers_39_windows_with_deduplication(self) -> None:
        intervals = self.acquisition["frozenIntervalSet"]["intervals"]
        self.assertEqual((len(intervals), self.plan["analysisIntervalCount"]), (39, 39))
        self.assertEqual(
            {horizon: sum(item["horizon"] == horizon for item in intervals) for horizon in ("ACTUAL", "MINUS_7", "PLUS_7")},
            {"ACTUAL": 13, "MINUS_7": 13, "PLUS_7": 13},
        )
        self.assertEqual(self.plan["uniqueProviderPartitionCount"], 15)
        partition_ids = [item["providerPartitionId"] for item in self.plan["partitions"]]
        self.assertEqual(len(partition_ids), len(set(partition_ids)))
        self.assertTrue(any(len(item["analysisIntervalIdsCovered"]) > 1 for item in self.plan["partitions"]))
        covered = {interval_id for item in self.plan["partitions"] for interval_id in item["analysisIntervalIdsCovered"]}
        self.assertEqual(covered, {item["intervalId"] for item in intervals})
        expected_days = set()
        for interval in intervals:
            interval_start = datetime.fromisoformat(interval["applyingStartUtc"].replace("Z", "+00:00"))
            interval_end = datetime.fromisoformat(interval["separatingEndUtc"].replace("Z", "+00:00"))
            day = interval_start.replace(hour=0, minute=0, second=0, microsecond=0)
            while day < interval_end:
                expected_days.add(day)
                day += timedelta(days=1)
        self.assertEqual(
            {datetime.fromisoformat(item["nativeStartUtc"].replace("Z", "+00:00")) for item in self.plan["partitions"]},
            expected_days,
        )
        for partition in self.plan["partitions"]:
            start = datetime.fromisoformat(partition["nativeStartUtc"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(partition["nativeEndUtc"].replace("Z", "+00:00"))
            self.assertEqual((start.tzinfo, start.hour, start.minute, start.second), (timezone.utc, 0, 0, 0))
            self.assertEqual(end - start, timedelta(days=1))
            self.assertEqual(partition["requestIdentity"]["key"], f"USDJPY/{start.year:04d}/{start.month - 1:02d}/{start.day:02d}_ticks.bi5")
            self.assertEqual(partition["requestIdentity"]["requestPayer"], "requester")
            for interval_id in partition["analysisIntervalIdsCovered"]:
                interval = next(item for item in intervals if item["intervalId"] == interval_id)
                interval_start = datetime.fromisoformat(interval["applyingStartUtc"].replace("Z", "+00:00"))
                interval_end = datetime.fromisoformat(interval["separatingEndUtc"].replace("Z", "+00:00"))
                self.assertLess(start, interval_end)
                self.assertLess(interval_start, end)

    def test_scientific_population_labels_intervals_and_clusters_are_unchanged(self) -> None:
        r1_population = r1.build_s3r1_r1_primary_population(PROJECT_ROOT)
        r1_clusters = r1.build_s3r1_r1_overlap_clusters(PROJECT_ROOT, population=r1_population)
        r1_acquisition = r1.build_market_data_acquisition_contract(PROJECT_ROOT)
        self.assertEqual(self.population["populationCounts"], r1_population["populationCounts"])
        self.assertEqual(self.population["allFrozenRows"], r1_population["allFrozenRows"])
        self.assertEqual(self.population["primaryMarketScorableRows"], r1_population["primaryMarketScorableRows"])
        self.assertEqual(self.clusters["clusters"], r1_clusters["clusters"])
        self.assertEqual(self.acquisition["frozenIntervalSet"]["intervals"], r1_acquisition["frozenIntervalSet"]["intervals"])
        self.assertEqual({item["eventId"] for item in self.acquisition["frozenIntervalSet"]["intervals"]}, {item["eventId"] for item in r1_population["primaryMarketScorableRows"]})
        self.assertNotIn("TN_BD340A6100B173B5F254EDC1", {item["eventId"] for item in self.acquisition["frozenIntervalSet"]["intervals"]})
        self.assertTrue(all(item["analysisDisposition"] == "PRIMARY_DIRECTIONAL" for item in self.acquisition["frozenIntervalSet"]["intervals"]))
        self.assertFalse(self.preregistration["scientificDesignChanged"])
        self.assertTrue(self.invariance["providerProtocolDoesNotChangeScientificDesign"])

    def test_contract_and_core_hashes_are_sensitive_to_every_new_binding(self) -> None:
        mutations = (
            ("provider", lambda value: value["provider"].update({"product": "OTHER"})),
            ("partition", lambda value: value["nativePartitioning"].update({"type": "OTHER"})),
            ("compression", lambda value: value["compression"].update({"documentedAlgorithm": "OTHER"})),
            ("record", lambda value: value["binaryRecordLayout"].update({"recordSizeBytes": 21})),
            ("timestamp", lambda value: value["timestampEncoding"].update({"unit": "seconds"})),
            ("scale", lambda value: value["priceEncoding"].update({"scaleDenominator": 100000})),
            ("parser", lambda value: value["parser"].update({"parserSourceSha256": "A" * 64})),
            ("retry", lambda value: value["retryPolicy"].update({"maxAttempts": 2})),
            ("revision", lambda value: value["revisionPolicy"].update({"scoreableAfterConflict": True})),
            ("plan", lambda value: value.update({"providerPartitionPlanHash": "A" * 64})),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                changed = copy.deepcopy(self.acquisition)
                changed.pop("marketDataAcquisitionContractHash")
                mutate(changed)
                self.assertNotEqual(s3._canonical_hash(changed), self.acquisition["marketDataAcquisitionContractHash"])
        core_body = self._without_hash(copy.deepcopy(self.core), "analysisCoreManifestHash")
        for field in ("marketDataAcquisitionContractHash", "protocolSourceLockHash", "providerPartitionPlanHash"):
            with self.subTest(field=field):
                changed = copy.deepcopy(core_body)
                changed[field] = "A" * 64
                self.assertNotEqual(s3._canonical_hash(changed), self.core["analysisCoreManifestHash"])
        self.assertNotIn("acceptanceManifestHash", self.core)

    @staticmethod
    def _direction_for_hit(row: dict[str, object], hit: int) -> str:
        expected = str(row["validationExpectedPairDirection"])
        if hit:
            return expected
        return "DOWN" if expected == "UP" else "UP"

    @staticmethod
    def _reference_permutation(rows: list[dict[str, object]], realized: dict[str, str]) -> tuple[int, float]:
        by_side = {side: [row for row in rows if row["sideIdentity"] == side] for side in ("USD", "JPY")}
        assignments: list[dict[str, str]] = []
        for usd_supportive in itertools.combinations(range(5), 1):
            usd = {row["eventId"]: "SUPPORTIVE" if index in usd_supportive else "ADVERSE" for index, row in enumerate(by_side["USD"])}
            for jpy_supportive in itertools.combinations(range(8), 7):
                jpy = {row["eventId"]: "SUPPORTIVE" if index in jpy_supportive else "ADVERSE" for index, row in enumerate(by_side["JPY"])}
                assignments.append({**usd, **jpy})
        observed_labels = {row["eventId"]: row["pressureState"] for row in rows}
        mapping = {
            ("USD", "SUPPORTIVE"): "UP",
            ("USD", "ADVERSE"): "DOWN",
            ("JPY", "SUPPORTIVE"): "DOWN",
            ("JPY", "ADVERSE"): "UP",
        }

        def hits(labels: dict[str, str]) -> int:
            return sum(mapping[(str(row["sideIdentity"]), labels[str(row["eventId"])])] == realized[str(row["eventId"])] for row in rows)

        observed_h = hits(observed_labels)
        return observed_h, sum(hits(labels) >= observed_h for labels in assignments) / len(assignments)

    def test_exhaustive_8192_vector_reference_matches_production(self) -> None:
        rows = self.population["primaryMarketScorableRows"]
        mismatches = 0
        checked = 0
        clusters = s3.derive_overlap_clusters(rows)
        for bits in itertools.product((0, 1), repeat=13):
            realized = {str(row["eventId"]): self._direction_for_hit(row, bit) for row, bit in zip(rows, bits, strict=True)}
            production = s3.exact_one_sided_permutation(rows, realized)
            reference_h, reference_p = self._reference_permutation(rows, realized)
            hit_by_event = {str(row["eventId"]): bit for row, bit in zip(rows, bits, strict=True)}
            reference_cluster = sum(
                sum(hit_by_event[event_id] for event_id in cluster["memberEventIds"]) / len(cluster["memberEventIds"])
                for cluster in clusters
            ) / len(clusters)
            reference_survival = (
                "PILOT_ASSOCIATION_SURVIVED"
                if reference_h / 13 > 0.5 and reference_p <= 0.1 and reference_cluster > 0.5
                else "PILOT_ASSOCIATION_NOT_SURVIVED"
            )
            production_cluster = s3.cluster_balanced_hit_rate(rows, hit_by_event)
            production_survival = s3.primary_survival_status(
                all_primary_validly_scorable=True,
                primary_hit_rate=production["observedHitCount"] / 13,
                exact_p_value=production["oneSidedPExact"],
                cluster_balanced_rate=production_cluster,
            )
            if (
                production["observedHitCount"],
                production["observedHitCount"] / 13,
                production["oneSidedPExact"],
                production_cluster,
                production_survival,
            ) != (reference_h, reference_h / 13, reference_p, reference_cluster, reference_survival):
                mismatches += 1
            checked += 1
        self.assertEqual((checked, mismatches), (8192, 0))

    def test_exhaustive_2744_timing_reference_matches_production(self) -> None:
        checked = 0
        mismatches = 0
        for actual, minus7, plus7 in itertools.product(range(14), repeat=3):
            production = r1.s3r1.timing_specificity_status(
                actual_hit_count=actual,
                minus7_hit_count=minus7,
                plus7_hit_count=plus7,
            )
            reference = (
                "TIMING_SPECIFICITY_DEMONSTRATED_WITHIN_PREREGISTERED_DIAGNOSTIC"
                if actual > minus7 and actual > plus7
                else "TIMING_SPECIFICITY_NOT_DEMONSTRATED"
            )
            mismatches += int(production != reference)
            checked += 1
        self.assertEqual((checked, mismatches), (2744, 0))

    def test_branch_b_keeps_all_access_and_execution_locks_false(self) -> None:
        self.assertEqual(self.acceptance["status"], "S3R1_R2_PROVIDER_PROTOCOL_INCOMPLETE_OUTCOME_UNLOCK_BLOCKED")
        self.assertEqual(self.acceptance["nextGate"], "CENTRAL_REVIEW_PROVIDER_PROTOCOL_GAP")
        self.assertFalse(self.acceptance["providerAccessPerformed"])
        self.assertFalse(self.acceptance["marketOutcomeRead"])
        self.assertFalse(self.acceptance["executionAllowed"])
        self.assertFalse(self.acceptance["outcomeUnlocked"])
        self.assertTrue(all(value is False for value in self.acceptance["outcomeAccessFlags"].values()))
        for payload in (self.evidence, self.lock, self.plan, self.acquisition, self.preregistration, self.population, self.clusters, self.invariance, self.core, self.acceptance):
            serialized = json.dumps(payload, sort_keys=True)
            self.assertNotIn('"logReturn":', serialized)
            self.assertNotIn('"startMidpoint":', serialized)
            self.assertNotIn('"endMidpoint":', serialized)
        source = (BACKEND_ROOT / "outcome_analysis_s3r1_r2.py").read_text(encoding="utf-8")
        self.assertNotIn("import boto3", source)
        self.assertNotIn("import requests", source)
        self.assertNotIn("outcome_analysis_s4", source)
        self.assertEqual(
            self.acquisition["rawCapturePolicy"]["requiredFutureManifestFields"],
            [
                "requestId", "providerProduct", "instrument", "providerPartitionId", "nativeStartUtc", "nativeEndUtc",
                "requestParameters", "retrievedAtUtc", "transportStatus", "providerMetadata", "byteLength", "rawSha256",
                "parserContractHash", "parserSourceSha256", "parsedRecordCount", "parsedTicksSha256", "firstTimestampUtc",
                "lastTimestampUtc", "acquisitionDisposition",
            ],
        )
        with self.assertRaises(r2.OutcomeAnalysisS3R1R2Error):
            r2.write_s3r1_r2_artifacts(PROJECT_ROOT, outcome_source=object())

    def test_schema_and_validator_are_strict_and_repeatable(self) -> None:
        schema = json.loads(self.artifacts["schema"].read_text(encoding="utf-8"))
        r1.validate_json_schema_instance(self.preregistration, schema)
        r2.validate_s3r1_r2_artifacts(PROJECT_ROOT)
        mutation = copy.deepcopy(self.preregistration)
        mutation["scientificDesignChanged"] = True
        with self.assertRaises(r1.OutcomeAnalysisS3R1R1Error):
            r1.validate_json_schema_instance(mutation, schema)
        second = r2.write_s3r1_r2_artifacts(PROJECT_ROOT)
        self.assertEqual(self.artifacts, second)


if __name__ == "__main__":
    unittest.main()
