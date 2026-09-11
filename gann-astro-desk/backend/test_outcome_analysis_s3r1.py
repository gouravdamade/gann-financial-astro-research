"""Integrity and synthetic-only regression contract for MO-R4A-S3R1."""

from __future__ import annotations

import copy
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

import outcome_analysis_s3 as s3  # noqa: E402
import outcome_analysis_s3r1 as s3r1  # noqa: E402


class OutcomeAnalysisS3R1Tests(unittest.TestCase):
    """The S3R1 package stays outcome-blind while becoming mutation-resistant."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.preregistration = s3r1.build_s3r1_preregistration(PROJECT_ROOT)
        cls.population = s3r1.build_s3r1_primary_population(PROJECT_ROOT)
        cls.clusters = s3r1.build_s3r1_overlap_clusters(PROJECT_ROOT, population=cls.population)
        cls.invariance = s3r1.build_s3r1_invariance_audit(
            PROJECT_ROOT,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
        )
        cls.core = s3r1.build_analysis_core_manifest(cls.preregistration, cls.population, cls.clusters, cls.invariance)
        cls.acceptance = s3r1.build_s3r1_acceptance_manifest(
            PROJECT_ROOT,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
            invariance=cls.invariance,
            core=cls.core,
        )
        cls.artifacts = {
            "preregistration": s3r1.DEFAULT_PREREGISTRATION_PATH,
            "schema": s3r1.DEFAULT_SCHEMA_PATH,
            "population": s3r1.DEFAULT_PRIMARY_POPULATION_PATH,
            "clusters": s3r1.DEFAULT_OVERLAP_CLUSTERS_PATH,
            "invariance": s3r1.DEFAULT_INVARIANCE_PATH,
            "core": s3r1.DEFAULT_CORE_MANIFEST_PATH,
            "acceptance": s3r1.DEFAULT_ACCEPTANCE_PATH,
        }

    def _ticks(self, *rows: tuple[str, float, float]) -> list[dict[str, object]]:
        return [{"timestampUtc": timestamp, "bid": bid, "ask": ask} for timestamp, bid, ask in rows]

    def test_checked_in_successor_artifacts_match_builders(self) -> None:
        expected = {
            "preregistration": self.preregistration,
            "population": self.population,
            "clusters": self.clusters,
            "invariance": self.invariance,
            "core": self.core,
            "acceptance": self.acceptance,
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertTrue(self.artifacts[name].is_file())
                self.assertEqual(json.loads(self.artifacts[name].read_text(encoding="utf-8")), value)
        schema = json.loads(self.artifacts["schema"].read_text(encoding="utf-8"))
        s3r1.validate_json_schema_instance(self.preregistration, schema)
        s3r1.validate_s3r1_preregistration(self.preregistration)

    def test_nested_schema_is_closed_and_exact(self) -> None:
        schema = json.loads(self.artifacts["schema"].read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(self.preregistration))

        def visit(node: object, path: str = "$") -> None:
            self.assertIsInstance(node, dict, path)
            if not isinstance(node, dict):
                return
            if node.get("type") == "object":
                self.assertIs(node.get("additionalProperties"), False, path)
                self.assertEqual(set(node.get("required", [])), set(node.get("properties", {})), path)
                for key, child in node.get("properties", {}).items():
                    visit(child, f"{path}.{key}")
            if node.get("type") == "array":
                self.assertEqual(node["minItems"], node["maxItems"], path)
                self.assertIn("uniqueItems", node, path)
                self.assertEqual(node.get("items"), False, path)
                for index, child in enumerate(node.get("prefixItems", [])):
                    visit(child, f"{path}[{index}]")

        visit(schema)

    def test_upstream_hashes_and_frozen_timestamp_are_exact(self) -> None:
        self.assertEqual(self.preregistration["upstreamHashes"], s3r1.EXPECTED_UPSTREAM_HASHES)
        self.assertEqual(self.preregistration["preregistrationAuthoredAtUtc"], "2026-09-11T00:00:00Z")
        self.assertEqual(
            self.preregistration["timestampSemantics"],
            "DECLARATIVE_FROZEN_METADATA_NOT_GIT_COMMIT_CHRONOLOGY",
        )
        self.assertNotIn("createdAtUtc", self.preregistration)
        s3r1._assert_historical_s3_is_unchanged(PROJECT_ROOT)

    def test_strict_schema_rejects_36_nested_mutations(self) -> None:
        mutations: list[tuple[str, object]] = []

        def add(name: str, mutate: object) -> None:
            value = copy.deepcopy(self.preregistration)
            mutate(value)
            mutations.append((name, value))

        add("top-level unknown property", lambda value: value.update({"unexpected": True}))
        add("contract", lambda value: value.__setitem__("contract", "OTHER"))
        add("schema version", lambda value: value.__setitem__("schemaVersion", 2))
        add("milestone", lambda value: value.__setitem__("milestone", "MO-R4A-S4"))
        add("starting master", lambda value: value.__setitem__("startingMaster", "0" * 40))
        add("status", lambda value: value.__setitem__("status", "COMPLETE"))
        add("next gate", lambda value: value.__setitem__("nextGate", "S4"))
        add("upstream unknown property", lambda value: value["upstreamHashes"].update({"other": "A" * 64}))
        add("upstream hash", lambda value: value["upstreamHashes"].__setitem__("ledger", "A" * 64))
        add("frozen pilot unknown property", lambda value: value["frozenPilot"].update({"other": 1}))
        add("market provider", lambda value: value["marketDataSource"].__setitem__("provider", "OTHER"))
        add("market required field", lambda value: value["marketDataSource"]["requiredFields"].__setitem__(0, "price"))
        add("market fallback", lambda value: value["marketDataSource"].__setitem__("fallbackProviderAllowed", True))
        add("interval boundary", lambda value: value["primaryInterval"].__setitem__("halfOpen", False))
        add("interval return formula", lambda value: value["primaryInterval"].__setitem__("returnFormula", "close-open"))
        add("signed unit", lambda value: value["validationMapping"].__setitem__("signedUnitCreated", True))
        add("unknown policy", lambda value: value["zeroAndAbstentionPolicy"].__setitem__("unknown", "SCORE"))
        add("weekend event", lambda value: value["weekendExclusion"].__setitem__("eventId", "OTHER"))
        add("weekend boundary", lambda value: value["weekendExclusion"]["intervalUtc"].__setitem__(1, "2025-04-05T12:34:36Z"))
        add("weekend resample", lambda value: value["weekendExclusion"].__setitem__("resampleOrExtendAllowed", True))
        add("overlap rule", lambda value: value["overlapClusters"].__setitem__("overlapRule", "a.start <= b.end"))
        add("touching overlap", lambda value: value["overlapClusters"].__setitem__("touchingBoundaryIsOverlap", True))
        add("cluster identity", lambda value: value["overlapClusters"]["primaryClusters"].__setitem__(0, "C0"))
        add("hit definition", lambda value: value["primaryStatistic"].__setitem__("hitDefinition", "q-r >= 0"))
        add("primary statistic unknown property", lambda value: value["primaryStatistic"].update({"twoSided": True}))
        add("permutation count", lambda value: value["exactPermutation"].__setitem__("assignmentCount", 41))
        add("permutation side scope", lambda value: value["exactPermutation"].__setitem__("sideLocalOnly", False))
        add("permutation cross-side", lambda value: value["exactPermutation"].__setitem__("noCrossSidePermutation", False))
        add("permutation timestamp", lambda value: value["exactPermutation"].__setitem__("noTimestampPermutation", False))
        add("secondary descriptive row", lambda value: value["secondaryDescriptive"].__setitem__(0, "outcome"))
        add("time shift values", lambda value: value["timeShiftDiagnostics"]["shiftsCalendarDays"].__setitem__(0, -6))
        add("time shift status", lambda value: value["timeShiftDiagnostics"].__setitem__("timingSpecificityFlag", "DEMONSTRATED"))
        add("time shift completeness", lambda value: value["timeShiftDiagnostics"].__setitem__("strictComparison", False))
        add("multiplicity count", lambda value: value["multiplicity"].__setitem__("primaryInferentialTestCount", 2))
        add("survival denominator", lambda value: value["survivalRule"].__setitem__("denominatorShrinkAllowed", True))
        add("amendment execution", lambda value: value["amendmentAndStopping"].__setitem__("executionAllowed", True))

        self.assertEqual(len(mutations), 36)
        schema = json.loads(self.artifacts["schema"].read_text(encoding="utf-8"))
        for name, value in mutations:
            with self.subTest(name=name):
                with self.assertRaises(s3r1.OutcomeAnalysisS3R1Error):
                    s3r1.validate_json_schema_instance(value, schema)

    def test_runtime_validator_rejects_semantic_mutations(self) -> None:
        mutations: list[tuple[str, object]] = []

        def changed(name: str, mutate: object) -> None:
            value = copy.deepcopy(self.preregistration)
            mutate(value)
            mutations.append((name, value))

        changed("hash", lambda value: value.__setitem__("preregistrationHash", "A" * 64))
        changed("protected access", lambda value: value["outcomeAccessFlags"].__setitem__("PRICE_DATA_READ", True))
        changed("provider access", lambda value: value["marketDataSource"].__setitem__("s3ProviderAccessAllowed", True))
        changed("timestamp semantics", lambda value: value.__setitem__("timestampSemantics", "GIT_TIME"))
        changed("null cross-side exchangeability", lambda value: value["permutationNullAssumption"].__setitem__("crossSideExchangeability", True))
        changed("time diagnostic p value", lambda value: value["timeShiftDiagnostics"].__setitem__("secondaryPValueAllowed", True))
        for name, value in mutations:
            with self.subTest(name=name):
                with self.assertRaises(s3r1.OutcomeAnalysisS3R1Error):
                    s3r1.validate_s3r1_preregistration(value)

    def test_analysis_core_hash_is_acyclic_and_sensitive_to_all_inputs(self) -> None:
        self.assertNotIn("acceptanceManifestHash", self.core)
        self.assertEqual(
            self.core["analysisCoreManifestHash"],
            s3r1.compute_analysis_core_manifest_hash(
                self.core["upstreamHashes"],
                self.core["preregistrationHash"],
                self.core["primaryPopulationHash"],
                self.core["overlapClustersHash"],
                self.core["analysisPlanInvarianceAuditHash"],
            ),
        )
        baseline = {
            "upstreamHashes": self.core["upstreamHashes"],
            "preregistrationHash": self.core["preregistrationHash"],
            "primaryPopulationHash": self.core["primaryPopulationHash"],
            "overlapClustersHash": self.core["overlapClustersHash"],
            "analysisPlanInvarianceAuditHash": self.core["analysisPlanInvarianceAuditHash"],
        }
        for key in baseline["upstreamHashes"]:
            upstream = copy.deepcopy(baseline["upstreamHashes"])
            upstream[key] = "A" * 64
            with self.subTest(input=key):
                self.assertNotEqual(
                    self.core["analysisCoreManifestHash"],
                    s3r1.compute_analysis_core_manifest_hash(
                        upstream,
                        baseline["preregistrationHash"],
                        baseline["primaryPopulationHash"],
                        baseline["overlapClustersHash"],
                        baseline["analysisPlanInvarianceAuditHash"],
                    ),
                )
        for key in ("preregistrationHash", "primaryPopulationHash", "overlapClustersHash", "analysisPlanInvarianceAuditHash"):
            changed = dict(baseline)
            changed[key] = "B" * 64
            with self.subTest(input=key):
                self.assertNotEqual(
                    self.core["analysisCoreManifestHash"],
                    s3r1.compute_analysis_core_manifest_hash(
                        changed["upstreamHashes"],
                        changed["preregistrationHash"],
                        changed["primaryPopulationHash"],
                        changed["overlapClustersHash"],
                        changed["analysisPlanInvarianceAuditHash"],
                    ),
                )
        self.assertEqual(self.acceptance["analysisCoreManifestHash"], self.core["analysisCoreManifestHash"])

    def test_population_clusters_and_null_assumption_remain_frozen(self) -> None:
        self.assertEqual(
            self.population["populationCounts"],
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
        self.assertEqual(tuple(cluster["clusterId"] for cluster in self.clusters["clusters"]), ("C1", "C2", "C3", "C4"))
        null = self.preregistration["permutationNullAssumption"]
        self.assertEqual(null["identifier"], "CONDITIONAL_WITHIN_SIDE_LABEL_EXCHANGEABILITY_NULL")
        self.assertEqual((null["usdPositions"], null["usdSupportiveLabels"]), (5, 1))
        self.assertEqual((null["jpyPositions"], null["jpySupportiveLabels"]), (8, 7))
        self.assertFalse(null["crossSideExchangeability"])
        self.assertFalse(null["randomizedExperimentClaim"])
        rows = self.population["primaryMarketScorableRows"]
        assignments = s3.enumerate_within_side_label_assignments(rows)
        self.assertEqual(len(assignments), 40)
        self.assertIn({row["eventId"]: row["pressureState"] for row in rows}, assignments)
        usd_ids = {row["eventId"] for row in rows if row["sideIdentity"] == "USD"}
        jpy_ids = {row["eventId"] for row in rows if row["sideIdentity"] == "JPY"}
        for assignment in assignments:
            self.assertEqual(sum(assignment[key] == "SUPPORTIVE" for key in usd_ids), 1)
            self.assertEqual(sum(assignment[key] == "SUPPORTIVE" for key in jpy_ids), 7)

    def test_timing_specificity_is_deterministic_and_diagnostic_only(self) -> None:
        self.assertEqual(
            s3r1.timing_specificity_status(actual_hit_count=8, minus7_hit_count=7, plus7_hit_count=6),
            "TIMING_SPECIFICITY_DEMONSTRATED_WITHIN_PREREGISTERED_DIAGNOSTIC",
        )
        self.assertEqual(
            s3r1.timing_specificity_status(actual_hit_count=7, minus7_hit_count=7, plus7_hit_count=6),
            "TIMING_SPECIFICITY_NOT_DEMONSTRATED",
        )
        self.assertEqual(
            s3r1.timing_specificity_status(actual_hit_count=8, minus7_hit_count=None, plus7_hit_count=6),
            "TIMING_DIAGNOSTIC_INCOMPLETE",
        )
        self.assertEqual(
            s3r1.timing_specificity_status(actual_hit_count=8, minus7_hit_count=7, plus7_hit_count=6, plus7_complete=False),
            "TIMING_DIAGNOSTIC_INCOMPLETE",
        )
        self.assertTrue(self.preregistration["timeShiftDiagnostics"]["doesNotAffectPrimarySurvival"])

    def test_synthetic_ticks_keep_half_open_conflict_and_no_rescue_rules(self) -> None:
        result = s3r1.score_synthetic_interval_s3r1(
            self._ticks(
                ("2030-01-01T00:00:00Z", 100.0, 100.2),
                ("2030-01-01T00:30:00Z", 101.0, 101.2),
                ("2030-01-01T01:00:00Z", 200.0, 200.2),
                ("2030-01-01T01:30:00Z", 300.0, 300.2),
            ),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(result["dataStatus"], "SCORABLE_SYNTHETIC_ONLY")
        self.assertEqual((result["startTickUtc"], result["endTickUtc"]), ("2030-01-01T00:00:00Z", "2030-01-01T00:30:00Z"))
        self.assertFalse(result["outsideIntervalRescueUsed"])

        outside_only = s3r1.score_synthetic_interval_s3r1(
            self._ticks(
                ("2029-12-31T23:59:00Z", 100.0, 100.2),
                ("2030-01-01T00:30:00Z", 101.0, 101.2),
                ("2030-01-01T01:00:00Z", 102.0, 102.2),
            ),
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(outside_only["dataStatus"], "DATA_UNSCORABLE")
        self.assertEqual(outside_only["selectedTickCount"], 1)
        self.assertFalse(outside_only["outsideIntervalRescueUsed"])

        conflict_ticks = self._ticks(
            ("2030-01-01T00:00:00Z", 100.0, 100.2),
            ("2030-01-01T00:30:00Z", 101.0, 101.2),
            ("2030-01-01T00:30:00Z", 101.1, 101.3),
        )
        with self.assertRaises(s3r1.ConflictingSyntheticTickError):
            s3r1.canonicalize_synthetic_ticks_s3r1(conflict_ticks)
        conflict = s3r1.score_synthetic_interval_s3r1(
            conflict_ticks,
            applying_start_utc="2030-01-01T00:00:00Z",
            separating_end_utc="2030-01-01T01:00:00Z",
            validation_expected_pair_direction="UP",
        )
        self.assertEqual(conflict["dataStatus"], "DATA_CONFLICT_UNSCORABLE")
        self.assertEqual(conflict["reason"], "CONFLICTING_QUOTES_AT_SAME_TIMESTAMP")
        deduped = s3r1.canonicalize_synthetic_ticks_s3r1(self._ticks(
            ("2030-01-01T00:00:00Z", 100.0, 100.2),
            ("2030-01-01T00:00:00Z", 100.0, 100.2),
            ("2030-01-01T00:30:00Z", 101.0, 101.2),
        ))
        self.assertEqual(len(deduped), 2)

    def test_invariance_audit_proves_exact_24_event_lineage(self) -> None:
        self.assertEqual(len(self.invariance["rows"]), 24)
        self.assertTrue(self.invariance["summary"]["allEventIdentitiesUnchanged"])
        self.assertTrue(self.invariance["summary"]["allExactUtcUnchanged"])
        self.assertTrue(self.invariance["summary"]["allApplyingStartUtcUnchanged"])
        self.assertTrue(self.invariance["summary"]["allSeparatingEndUtcUnchanged"])
        self.assertTrue(self.invariance["summary"]["s2HypothesisSemanticsUnchanged"])
        self.assertFalse(self.invariance["summary"]["marketOutcomeInS3R1Artifacts"])
        self.assertTrue(all(row["eventHashUnchanged"] and row["exactUtcUnchanged"] and row["s2HypothesisSemanticsUnchanged"] for row in self.invariance["rows"]))

    def test_acceptance_and_all_successor_payloads_keep_access_disabled(self) -> None:
        payloads = [self.preregistration, self.population, self.clusters, self.invariance, self.core, self.acceptance]
        for payload in payloads:
            with self.subTest(contract=payload["contract"]):
                serialized = json.dumps(payload, sort_keys=True)
                self.assertNotIn('"logReturn"', serialized)
                self.assertNotIn('"startMidpoint"', serialized)
                self.assertNotIn('"endMidpoint"', serialized)
                if "outcomeAccessFlags" in payload:
                    self.assertEqual(payload["outcomeAccessFlags"], s3r1._all_false_flags())
        self.assertFalse(self.acceptance["marketDataRead"])
        self.assertFalse(self.acceptance["outcomeDataRead"])
        self.assertFalse(self.acceptance["executionAllowed"])
        self.assertFalse(self.preregistration["amendmentAndStopping"]["marketOutcomeInS3Artifacts"])

    def test_materialization_is_deterministic_and_rejects_outcome_attachment(self) -> None:
        before = {name: path.read_bytes() for name, path in self.artifacts.items()}
        materialized = s3r1.write_s3r1_artifacts(PROJECT_ROOT)
        after = {name: path.read_bytes() for name, path in self.artifacts.items()}
        self.assertEqual(before, after)
        self.assertEqual(set(materialized), {"preregistration", "schema", "population", "clusters", "invariance", "core", "acceptance", "report"})
        with self.assertRaises(s3r1.OutcomeAnalysisS3R1Error):
            s3r1.write_s3r1_artifacts(PROJECT_ROOT, outcome_source="provider")

    def test_s3r1_has_no_s4_module_or_provider_integration(self) -> None:
        self.assertFalse((BACKEND_ROOT / "outcome_analysis_s4.py").exists())
        source = (BACKEND_ROOT / "outcome_analysis_s3r1.py").read_text(encoding="utf-8")
        self.assertNotIn("requests", source)
        self.assertNotIn("yfinance", source)
        self.assertNotIn("ccxt", source)
        self.assertNotIn("outcome_analysis_s4", source)


if __name__ == "__main__":
    unittest.main()
