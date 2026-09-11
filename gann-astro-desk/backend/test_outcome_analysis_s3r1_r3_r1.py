"""Focused tests for MO-R4A-S3R1-R3-R1 source-contract successors."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

import dukascopy_tick_parser_s3r1_r3 as parser
import outcome_analysis_s3r1_r3 as r3
import outcome_analysis_s3r1_r3_r1 as r3r1


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_CANONICAL_FIELDS = [
    "partitionId",
    "recordIndex",
    "timestampUtc",
    "askNative",
    "bidNative",
    "askVolumeBitsHex",
    "bidVolumeBitsHex",
]


class OutcomeAnalysisS3R1R3R1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifacts = r3r1.write_artifacts(PROJECT_ROOT)
        r3r1.validate_artifacts(PROJECT_ROOT)
        cls.adjudication = r3r1.build_lzma_framing_adjudication()
        cls.source_lock = r3r1.build_source_lock(cls.adjudication)
        cls.parser_contract = r3r1._historical_r3_components(PROJECT_ROOT)["parserContract"]
        cls.acquisition = r3r1.build_market_data_acquisition_contract(
            PROJECT_ROOT,
            adjudication=cls.adjudication,
            source_lock=cls.source_lock,
            parser_contract=cls.parser_contract,
        )
        cls.preregistration = r3r1.build_preregistration(
            PROJECT_ROOT,
            adjudication=cls.adjudication,
            source_lock=cls.source_lock,
            acquisition=cls.acquisition,
        )
        cls.population = r3r1.build_primary_population(PROJECT_ROOT, preregistration=cls.preregistration)
        cls.clusters = r3r1.build_overlap_clusters(PROJECT_ROOT, population=cls.population)
        cls.invariance = r3r1.build_invariance_audit(
            PROJECT_ROOT,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
        )
        cls.core = r3r1.build_analysis_core_manifest(
            cls.preregistration,
            cls.population,
            cls.clusters,
            cls.invariance,
            cls.acquisition,
            cls.source_lock,
            cls.adjudication,
            cls.parser_contract,
        )
        cls.acceptance = r3r1.build_acceptance_manifest(
            PROJECT_ROOT,
            adjudication=cls.adjudication,
            source_lock=cls.source_lock,
            parser_contract=cls.parser_contract,
            acquisition=cls.acquisition,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
            invariance=cls.invariance,
            core=cls.core,
        )

    def test_branch_b_qualifies_r3_without_reversing_the_operational_candidate(self) -> None:
        self.assertEqual(self.adjudication["adjudicationStatus"], r3r1.BRANCH_B_STATUS)
        self.assertEqual(
            self.adjudication["evidenceClassification"],
            "PLAUSIBLE_CROSS_SOURCE_RECONCILIATION_NOT_DIRECT_PROVIDER_SPECIFICATION",
        )
        self.assertFalse(self.adjudication["newAuthoritativeEvidenceFound"])
        self.assertFalse(self.adjudication["dukascopyDirectlyNamesFormatAlone"])
        self.assertEqual(self.adjudication["selectedOperationalParserFraming"], parser.COMPRESSION_FRAMING)
        self.assertFalse(self.adjudication["providerFramingUniquelySourceClosed"])
        self.assertFalse(self.adjudication["providerProtocolFullyClosed"])
        self.assertFalse(self.acquisition["providerProtocolFullyClosed"])
        self.assertFalse(self.acquisition["compression"]["parserUseForLiveOutcomeAcquisitionAllowed"])
        self.assertEqual(self.acceptance["branch"], r3r1.BRANCH_B)
        self.assertEqual(self.acceptance["nextGate"], r3r1.NEXT_GATE)

    def test_canonical_schema_matches_parser_and_actual_record_keys(self) -> None:
        declared = self.acquisition["canonicalParsedTickHashRecord"]
        self.assertEqual(declared["fields"], EXPECTED_CANONICAL_FIELDS)
        self.assertEqual(declared, r3r1._canonical_hash_record_definition(self.parser_contract))
        self.assertNotIn("canonicalTickSchema", self.acquisition)

        record = parser.ParsedDailyTick(
            partition_id="USDJPY/2030/00/01_ticks.bi5",
            record_index=4,
            timestamp_utc=datetime(2030, 1, 1, 0, 0, 1, 234000, tzinfo=timezone.utc),
            ask_native=157123,
            bid_native=157120,
            ask_volume=1.25,
            bid_volume=0.75,
            ask_volume_bits_hex="3FA00000",
            bid_volume_bits_hex="3F400000",
        )
        canonical_keys = list(record.canonical_record().keys())
        self.assertEqual(tuple(sorted(declared["fields"])), tuple(sorted(canonical_keys)))
        encoded_object = json.loads(parser.canonical_parsed_tick_json_lines([record]).decode("utf-8"))
        self.assertEqual(list(encoded_object.keys()), sorted(declared["fields"]))

    def test_independent_canonical_bytes_and_hash_are_exact(self) -> None:
        record = parser.ParsedDailyTick(
            partition_id="USDJPY/2030/00/01_ticks.bi5",
            record_index=0,
            timestamp_utc=datetime(2030, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            ask_native=157001,
            bid_native=157000,
            ask_volume=2.5,
            bid_volume=1.5,
            ask_volume_bits_hex="40200000",
            bid_volume_bits_hex="3FC00000",
        )
        expected_object = {
            "askNative": 157001,
            "askVolumeBitsHex": "40200000",
            "bidNative": 157000,
            "bidVolumeBitsHex": "3FC00000",
            "partitionId": "USDJPY/2030/00/01_ticks.bi5",
            "recordIndex": 0,
            "timestampUtc": "2030-01-01T00:00:00.000Z",
        }
        expected_line = (json.dumps(expected_object, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        actual = parser.canonical_parsed_tick_json_lines([record])
        self.assertEqual(actual, expected_line)
        self.assertEqual(parser.parsed_ticks_sha256([record]), hashlib.sha256(expected_line).hexdigest().upper())

    def test_decoded_float_volumes_are_excluded_from_the_hash_record(self) -> None:
        record = parser.ParsedDailyTick(
            partition_id="USDJPY/2030/00/01_ticks.bi5",
            record_index=1,
            timestamp_utc=datetime(2030, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
            ask_native=157002,
            bid_native=157001,
            ask_volume=99.5,
            bid_volume=88.5,
            ask_volume_bits_hex="42C70000",
            bid_volume_bits_hex="42B10000",
        )
        keys = set(record.canonical_record())
        self.assertNotIn("ask_volume", keys)
        self.assertNotIn("bid_volume", keys)
        self.assertNotIn("askVolumeDecodedFloat32", keys)
        self.assertNotIn("bidVolumeDecodedFloat32", keys)
        self.assertEqual(
            self.acquisition["nonCanonicalInspectionFields"]["status"],
            "NOT_INCLUDED_IN_PARSED_TICKS_HASH",
        )
        self.assertEqual(
            self.acquisition["nonCanonicalInspectionFields"]["fields"],
            ["askVolumeDecodedFloat32", "bidVolumeDecodedFloat32"],
        )

    def test_single_parsed_hash_definition_is_shared_with_future_manifest(self) -> None:
        parser_serialization = self.parser_contract["canonicalSerialization"]
        canonical = self.acquisition["canonicalParsedTickHashRecord"]
        self.assertEqual(canonical["fields"], parser_serialization["fields"])
        self.assertEqual(canonical["timestampFormat"], parser_serialization["timestampFormat"])
        self.assertEqual(canonical["serialization"], parser_serialization["representation"])
        self.assertEqual(canonical["hash"], parser_serialization["parsedTicksSha256"])
        self.assertEqual(self.acquisition["parsedCapturePolicy"]["parsedTicksSha256"], canonical["hash"])
        self.assertEqual(self.acquisition["rawCapturePolicy"]["futureManifestParsedTicksHashDefinition"], "canonicalParsedTickHashRecord")
        future = self.acquisition["futureRawAcquisitionManifest"]
        self.assertEqual(future["parsedTicksSha256"], canonical["hash"])
        self.assertEqual(future["parsedTicksSha256Definition"], "canonicalParsedTickHashRecord")
        self.assertEqual(future["requiredFields"], self.acquisition["rawCapturePolicy"]["requiredFutureManifestFields"])

    def test_parser_source_and_parser_contract_are_unchanged(self) -> None:
        self.assertEqual(self.parser_contract["parserContractHash"], r3r1.HISTORICAL_R3_PARSER_CONTRACT_HASH)
        source_hash = hashlib.sha256(r3.PARSER_SOURCE_PATH.read_bytes()).hexdigest().upper()
        self.assertEqual(source_hash, r3r1.HISTORICAL_R3_PARSER_SOURCE_SHA256)
        self.assertEqual(self.parser_contract["parserSourceSha256"], r3r1.HISTORICAL_R3_PARSER_SOURCE_SHA256)
        self.assertEqual(r3r1.HISTORICAL_R3_PARSER_SOURCE_SHA256, "47BEF7B1A13D8EE4EC2DDED2BDD965A27D41FCB548EC0D4D940A5535669D733E")

    def test_r3_historical_artifact_hashes_remain_exact(self) -> None:
        historical = r3r1._historical_r3_components(PROJECT_ROOT)
        expected = {
            "adjudication": r3r1.HISTORICAL_R3_ADJUDICATION_HASH,
            "sourceLock": r3r1.HISTORICAL_R3_SOURCE_LOCK_HASH,
            "parserContract": r3r1.HISTORICAL_R3_PARSER_CONTRACT_HASH,
            "acquisition": r3r1.HISTORICAL_R3_ACQUISITION_HASH,
            "preregistration": r3r1.HISTORICAL_R3_PREREGISTRATION_HASH,
            "population": r3r1.HISTORICAL_R3_POPULATION_HASH,
            "clusters": r3r1.HISTORICAL_R3_CLUSTERS_HASH,
            "invariance": r3r1.HISTORICAL_R3_INVARIANCE_HASH,
            "core": r3r1.HISTORICAL_R3_CORE_HASH,
            "acceptance": r3r1.HISTORICAL_R3_ACCEPTANCE_HASH,
        }
        hash_keys = {
            "adjudication": "lzmaFramingAdjudicationHash",
            "sourceLock": "protocolSourceLockHash",
            "parserContract": "parserContractHash",
            "acquisition": "marketDataAcquisitionContractHash",
            "preregistration": "preregistrationHash",
            "population": "primaryPopulationHash",
            "clusters": "overlapClustersHash",
            "invariance": "analysisPlanInvarianceAuditHash",
            "core": "analysisCoreManifestHash",
            "acceptance": "acceptanceManifestHash",
        }
        for name, value in historical.items():
            self.assertEqual(value[hash_keys[name]], expected[name])

    def test_scientific_successors_are_equal_to_r3_in_scientific_content(self) -> None:
        historical = r3r1._historical_r3_components(PROJECT_ROOT)
        self.assertEqual(self.population["allFrozenRows"], historical["population"]["allFrozenRows"])
        self.assertEqual(self.population["primaryMarketScorableRows"], historical["population"]["primaryMarketScorableRows"])
        self.assertEqual(self.population["structuralExclusion"], historical["population"]["structuralExclusion"])
        self.assertEqual(self.population["populationCounts"], historical["population"]["populationCounts"])
        self.assertEqual(self.clusters["clusters"], historical["clusters"]["clusters"])
        self.assertEqual(self.invariance["rows"], historical["invariance"]["rows"])
        self.assertEqual(self.invariance["summary"], historical["invariance"]["summary"])
        self.assertEqual(self.population["populationCounts"]["frozenEventCount"], 24)
        self.assertEqual(self.population["populationCounts"]["directionalCount"], 14)
        self.assertEqual(self.population["populationCounts"]["primaryMarketScorableCount"], 13)
        self.assertEqual(self.acquisition["frozenIntervalSet"]["totalCount"], 39)
        self.assertEqual(self.acquisition["nativePartitioning"]["uniqueProviderPartitionCount"], 15)
        self.assertTrue(self.invariance["lzmaEvidenceReclassificationDoesNotChangeScience"])
        self.assertTrue(self.invariance["canonicalParsedSchemaCorrectionDoesNotChangeScience"])

    def test_stale_or_mutated_successor_components_are_rejected(self) -> None:
        mutated_adjudication = copy.deepcopy(self.adjudication)
        mutated_adjudication["evidenceClassification"] = "UNIQUE_SOURCE_CLOSURE_CONFIRMED"
        with self.assertRaises(r3r1.OutcomeAnalysisS3R1R3R1Error):
            r3r1.build_source_lock(mutated_adjudication)

        mutated_acquisition = copy.deepcopy(self.acquisition)
        mutated_acquisition["canonicalParsedTickHashRecord"]["fields"] = ["timestampUtc"]
        with self.assertRaises(r3r1.OutcomeAnalysisS3R1R3R1Error):
            r3r1.build_preregistration(PROJECT_ROOT, acquisition=mutated_acquisition)

        mutated_core = copy.deepcopy(self.core)
        mutated_core["parserSourceSha256"] = "0" * 64
        with self.assertRaises(r3r1.OutcomeAnalysisS3R1R3R1Error):
            r3r1.build_acceptance_manifest(PROJECT_ROOT, core=mutated_core)

    def test_firewall_and_provider_access_remain_locked(self) -> None:
        self.assertEqual(len(self.preregistration["outcomeAccessFlags"]), 16)
        self.assertTrue(all(value is False for value in self.preregistration["outcomeAccessFlags"].values()))
        self.assertTrue(all(value is False for value in self.acceptance["outcomeAccessFlags"].values()))
        for value in (self.acquisition, self.acceptance):
            self.assertFalse(value["providerAccessPerformed"])
            self.assertFalse(value["marketOutcomeRead"])
            self.assertFalse(value["executionAllowed"])
        self.assertFalse(self.acceptance["outcomeUnlocked"])
        self.assertFalse(self.acceptance["providerProtocolFullyClosed"])

    def test_no_provider_payload_is_materialized(self) -> None:
        self.assertEqual(list(PROJECT_ROOT.rglob("*.bi5")), [])
        source = r3r1.DEFAULT_REPORT_PATH.read_text(encoding="utf-8")
        self.assertIn("No searched official Dukascopy source directly names", source)
        self.assertNotIn("providerProtocolFullyClosed=true", source)


if __name__ == "__main__":
    unittest.main()
