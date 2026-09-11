"""Focused MO-R4A-S3R1-R3 framing, parser, and frozen-plan tests."""

from __future__ import annotations

import ast
import copy
import itertools
import json
import lzma
import os
import struct
import sys
import unittest
from datetime import date, datetime
from decimal import Decimal
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

import dukascopy_tick_parser_s3r1_r3 as parser  # noqa: E402
import outcome_analysis_s3 as s3  # noqa: E402
import outcome_analysis_s3r1_r1 as r1  # noqa: E402
import outcome_analysis_s3r1_r2 as r2  # noqa: E402
import outcome_analysis_s3r1_r3 as r3  # noqa: E402


def _synthetic_payload(*records: tuple[int, int, int, float, float], format_value: int = lzma.FORMAT_ALONE) -> bytes:
    """Invented 2030-only records, never provider bytes or market observations."""

    decoded = b"".join(struct.pack(">IIIff", *record) for record in records)
    return lzma.compress(decoded, format=format_value)


class OutcomeAnalysisS3R1R3Tests(unittest.TestCase):
    """R3 is source-bound, synthetic-only, and keeps every outcome lock closed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.artifacts = r3.write_s3r1_r3_artifacts(PROJECT_ROOT)
        cls.adjudication = r3.build_lzma_framing_adjudication()
        cls.source_lock = r3.build_source_lock(cls.adjudication)
        cls.parser_contract = r3.build_parser_contract(cls.adjudication)
        cls.acquisition = r3.build_market_data_acquisition_contract(
            PROJECT_ROOT,
            adjudication=cls.adjudication,
            source_lock=cls.source_lock,
            parser_contract=cls.parser_contract,
        )
        cls.preregistration = r3.build_s3r1_r3_preregistration(PROJECT_ROOT)
        cls.population = r3.build_s3r1_r3_primary_population(PROJECT_ROOT, preregistration=cls.preregistration)
        cls.clusters = r3.build_s3r1_r3_overlap_clusters(PROJECT_ROOT, population=cls.population)
        cls.invariance = r3.build_s3r1_r3_invariance_audit(
            PROJECT_ROOT,
            preregistration=cls.preregistration,
            population=cls.population,
            clusters=cls.clusters,
        )
        cls.core = r3.build_analysis_core_manifest(
            cls.preregistration,
            cls.population,
            cls.clusters,
            cls.invariance,
            cls.acquisition,
            cls.source_lock,
            cls.adjudication,
            cls.parser_contract,
        )
        cls.acceptance = r3.build_s3r1_r3_acceptance_manifest(
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

    @staticmethod
    def _without_hash(value: dict[str, object], key: str) -> dict[str, object]:
        return {name: item for name, item in value.items() if name != key}

    def test_authoritative_premises_uniquely_select_format_alone(self) -> None:
        facts = {item["factId"]: item for item in self.adjudication["premiseMatrix"]}
        expected = {
            "DUKASCOPY_EXCLUDES_XZ",
            "DUKASCOPY_SAMPLE_USES_DEFAULT_LZMA_DECOMPRESS",
            "PYTHON_DEFAULT_EQUALS_FORMAT_AUTO",
            "PYTHON_FORMAT_AUTO_ACCEPTS_XZ",
            "PYTHON_FORMAT_AUTO_ACCEPTS_FORMAT_ALONE",
            "PYTHON_FORMAT_AUTO_REJECTS_FORMAT_RAW",
            "PYTHON_FORMAT_RAW_REQUIRES_EXPLICIT_FILTER_CHAIN",
            "PYTHON_FORMAT_ALONE_IS_LEGACY_LZMA_CONTAINER",
        }
        self.assertEqual(set(facts), expected)
        self.assertTrue(all(item["status"] == "SUPPORTED" for item in facts.values()))
        self.assertEqual(self.adjudication["selectedFormat"], "PYTHON_LZMA_FORMAT_ALONE")
        self.assertEqual(self.adjudication["selectedPythonConstant"], "lzma.FORMAT_ALONE")
        self.assertEqual(self.adjudication["adjudicationStatus"], "COMPRESSION_FRAMING_SOURCE_ADJUDICATED")
        self.assertEqual(self.adjudication["decisionKind"], "CROSS_SOURCE_TECHNICAL_DEDUCTION")
        candidates = {item["format"]: item for item in self.adjudication["candidateFormats"]}
        self.assertEqual(candidates["FORMAT_XZ"]["finalDisposition"], "ELIMINATED")
        self.assertEqual(candidates["FORMAT_RAW"]["finalDisposition"], "ELIMINATED")
        self.assertEqual(candidates["FORMAT_ALONE"]["finalDisposition"], "SELECTED_BY_CROSS_SOURCE_TECHNICAL_DEDUCTION")
        self.assertEqual(self.source_lock["adjudicationStatus"], self.adjudication["adjudicationStatus"])

    def test_parser_decodes_synthetic_records_with_exact_native_identities(self) -> None:
        raw = _synthetic_payload(
            (0, 158_123, 158_120, 1.25, 0.5),
            (86_399_999, 158_200, 158_200, -0.0, 3.5),
        )
        records = parser.parse_daily_bi5(raw, partition_date_utc=date(2030, 1, 1))
        self.assertEqual(len(records), 2)
        self.assertEqual([record.record_index for record in records], [0, 1])
        self.assertEqual(records[0].partition_id, "USDJPY/2030/00/01_ticks.bi5")
        self.assertEqual(parser.format_timestamp_utc(records[0].timestamp_utc), "2030-01-01T00:00:00.000Z")
        self.assertEqual(parser.format_timestamp_utc(records[1].timestamp_utc), "2030-01-01T23:59:59.999Z")
        self.assertEqual((records[0].bid, records[0].ask), (Decimal("158.12"), Decimal("158.123")))
        self.assertEqual(records[0].ask_volume_bits_hex, struct.pack(">f", 1.25).hex().upper())
        self.assertEqual(records[1].bid_volume_bits_hex, struct.pack(">f", 3.5).hex().upper())
        canonical = parser.canonical_parsed_tick_json_lines(records)
        self.assertTrue(canonical.endswith(b"\n"))
        self.assertEqual(canonical, parser.canonical_parsed_tick_json_lines(records))
        self.assertEqual(parser.parsed_ticks_sha256(records), parser.parsed_ticks_sha256(records))
        decoded_lines = [json.loads(line) for line in canonical.decode("utf-8").splitlines()]
        self.assertEqual(decoded_lines[0]["timestampUtc"], "2030-01-01T00:00:00.000Z")
        self.assertNotIn("askVolume", decoded_lines[0])

    def test_parser_rejects_wrong_framing_and_corruption_without_fallback(self) -> None:
        record = (1_000, 158_123, 158_120, 1.0, 2.0)
        wrong_framing = _synthetic_payload(record, format_value=lzma.FORMAT_XZ)
        with self.assertRaisesRegex(parser.DukascopyTickParserError, "COMPRESSION_FORMAT_MISMATCH"):
            parser.parse_daily_bi5(wrong_framing, partition_date_utc=date(2030, 1, 1))
        with self.assertRaisesRegex(parser.DukascopyTickParserError, "COMPRESSION_DECODE_FAILED"):
            parser.parse_daily_bi5(b"not synthetic compressed data", partition_date_utc=date(2030, 1, 1))
        source = (BACKEND_ROOT / "dukascopy_tick_parser_s3r1_r3.py").read_text(encoding="utf-8")
        self.assertIn("lzma.FORMAT_ALONE", source)
        self.assertNotIn("lzma.FORMAT_AUTO", source)
        self.assertNotIn("lzma.FORMAT_RAW", source)
        self.assertNotIn("lzma.FORMAT_XZ", source)

    def test_parser_rejects_invalid_native_payload_conditions(self) -> None:
        cases = [
            (b"", "ZERO_BYTE_PAYLOAD_ACQUISITION_INCOMPLETE"),
            (lzma.compress(b"", format=lzma.FORMAT_ALONE), "ZERO_DECODED_RECORDS_ACQUISITION_INCOMPLETE"),
            (lzma.compress(b"x" * 19, format=lzma.FORMAT_ALONE), "RAW_RECORD_ALIGNMENT_INVALID"),
            (lzma.compress(b"x" * 21, format=lzma.FORMAT_ALONE), "RAW_RECORD_ALIGNMENT_INVALID"),
            (_synthetic_payload((86_400_000, 158_123, 158_120, 1.0, 1.0)), "NATIVE_TIMESTAMP_OUT_OF_PARTITION"),
            (_synthetic_payload((0, 158_119, 158_120, 1.0, 1.0)), "NATIVE_QUOTE_INVALID"),
            (_synthetic_payload((0, 158_120, 0, 1.0, 1.0)), "NATIVE_QUOTE_INVALID"),
        ]
        for raw, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(parser.DukascopyTickParserError) as context:
                    parser.parse_daily_bi5(raw, partition_date_utc=date(2030, 1, 1))
                self.assertEqual(context.exception.code, code)
        equal = parser.parse_daily_bi5(_synthetic_payload((0, 158_120, 158_120, 1.0, 1.0)), partition_date_utc=date(2030, 1, 1))
        self.assertEqual((equal[0].ask_native, equal[0].bid_native), (158_120, 158_120))
        with self.assertRaisesRegex(parser.DukascopyTickParserError, "UNSUPPORTED_SYMBOL"):
            parser.parse_daily_bi5(_synthetic_payload((0, 158_120, 158_120, 1.0, 1.0)), partition_date_utc=date(2030, 1, 1), symbol="EURUSD")
        with self.assertRaisesRegex(parser.DukascopyTickParserError, "INVALID_PARTITION_DATE"):
            parser.parse_daily_bi5(_synthetic_payload((0, 158_120, 158_120, 1.0, 1.0)), partition_date_utc=datetime(2030, 1, 1))

    def test_parser_is_offline_and_scientifically_blind(self) -> None:
        source = (BACKEND_ROOT / "dukascopy_tick_parser_s3r1_r3.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertFalse(imports & {"boto3", "botocore", "requests", "urllib", "httpx", "aiohttp", "socket", "ccxt", "yfinance"})
        lowered = source.lower()
        for token in ("supportive", "adverse", "validationexpectedpairdirection", "pexact", "cluster", "astrology", "usd pressure", "jpy pressure"):
            self.assertNotIn(token, lowered)
        self.assertFalse(list(PROJECT_ROOT.rglob("*.bi5")))

    def test_source_fact_coverage_and_parser_hash_are_bound(self) -> None:
        coverage = self.parser_contract["sourceFactCoverage"]
        self.assertEqual(set(coverage), {"compressionFraming", "recordSizeAndEndian", "timestampBaseAndUnit", "usdJpyDivisor"})
        self.assertEqual(self.parser_contract["syntheticFixtureMethodology"]["designation"], "SYNTHETIC_NOT_PROVIDER_DATA")
        self.assertEqual(len(self.parser_contract["syntheticFixtureMethodology"]["scenarioIds"]), 14)
        self.assertEqual(self.parser_contract["parserSourceSha256"], r3.parser_source_sha256())
        source_copy = (BACKEND_ROOT / "dukascopy_tick_parser_s3r1_r3.py").read_bytes() + b"\n# synthetic mutation\n"
        candidate = PROJECT_ROOT / ".parser-hash-mutation-synthetic.py"
        try:
            candidate.write_bytes(source_copy)
            self.assertNotEqual(self.parser_contract["parserSourceSha256"], r3.parser_source_sha256(candidate))
        finally:
            candidate.unlink(missing_ok=True)

    def test_hashes_are_sensitive_to_every_r3_binding_and_acceptance_rebuilds(self) -> None:
        parser_body = self._without_hash(copy.deepcopy(self.parser_contract), "parserContractHash")
        for field, mutate in (
            ("framing", lambda value: value["compression"].update({"framing": "OTHER"})),
            ("size", lambda value: value["recordLayout"].update({"recordSizeBytes": 21})),
            ("layout", lambda value: value["recordLayout"].update({"structFormat": "OTHER"})),
            ("timestamp", lambda value: value["timestampRule"].update({"unit": "seconds"})),
            ("divisor", lambda value: value["priceRule"].update({"scaleDenominator": 100_000})),
            ("serialization", lambda value: value["canonicalSerialization"].update({"representation": "OTHER"})),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(parser_body)
                mutate(changed)
                self.assertNotEqual(s3._canonical_hash(changed), self.parser_contract["parserContractHash"])
        acquisition_body = self._without_hash(copy.deepcopy(self.acquisition), "marketDataAcquisitionContractHash")
        for field in ("lzmaFramingAdjudicationHash",):
            changed = copy.deepcopy(acquisition_body)
            changed[field] = "A" * 64
            self.assertNotEqual(s3._canonical_hash(changed), self.acquisition["marketDataAcquisitionContractHash"])
        for section, field in (("parser", "parserContractHash"), ("parser", "parserSourceSha256"), ("compression", "compressionFraming")):
            changed = copy.deepcopy(acquisition_body)
            changed[section][field] = "A" * 64
            self.assertNotEqual(s3._canonical_hash(changed), self.acquisition["marketDataAcquisitionContractHash"])
        core_body = self._without_hash(copy.deepcopy(self.core), "analysisCoreManifestHash")
        for field in ("lzmaFramingAdjudicationHash", "parserContractHash", "parserSourceSha256"):
            changed = copy.deepcopy(core_body)
            changed[field] = "A" * 64
            self.assertNotEqual(s3._canonical_hash(changed), self.core["analysisCoreManifestHash"])
        tampered = copy.deepcopy(self.parser_contract)
        tampered["parserSourceSha256"] = "A" * 64
        with self.assertRaises(r3.OutcomeAnalysisS3R1R3Error):
            r3.build_s3r1_r3_acceptance_manifest(PROJECT_ROOT, parser_contract=tampered)

    def test_r2_science_and_partitions_remain_exactly_unchanged(self) -> None:
        r2_population = r2.build_s3r1_r2_primary_population(PROJECT_ROOT)
        r2_clusters = r2.build_s3r1_r2_overlap_clusters(PROJECT_ROOT)
        r2_acquisition = r2.build_market_data_acquisition_contract(PROJECT_ROOT)
        self.assertEqual(self.population["allFrozenRows"], r2_population["allFrozenRows"])
        self.assertEqual(self.population["primaryMarketScorableRows"], r2_population["primaryMarketScorableRows"])
        self.assertEqual(self.population["populationCounts"], r2_population["populationCounts"])
        self.assertEqual(self.clusters["clusters"], r2_clusters["clusters"])
        self.assertEqual(self.acquisition["frozenIntervalSet"], r2_acquisition["frozenIntervalSet"])
        self.assertEqual(self.acquisition["nativePartitioning"]["uniqueProviderPartitionCount"], 15)
        self.assertEqual(self.acquisition["frozenIntervalSet"]["totalCount"], 39)
        self.assertFalse(self.preregistration["scientificDesignChanged"])

    @staticmethod
    def _direction_for_hit(row: dict[str, object], hit: int) -> str:
        expected = str(row["validationExpectedPairDirection"])
        return expected if hit else ("DOWN" if expected == "UP" else "UP")

    def test_exhaustive_8192_vector_reference_matches_production(self) -> None:
        rows = self.population["primaryMarketScorableRows"]
        by_side = {side: [row for row in rows if row["sideIdentity"] == side] for side in ("USD", "JPY")}
        assignments = []
        for usd_supportive in itertools.combinations(range(5), 1):
            usd = {row["eventId"]: "SUPPORTIVE" if index in usd_supportive else "ADVERSE" for index, row in enumerate(by_side["USD"])}
            for jpy_supportive in itertools.combinations(range(8), 7):
                jpy = {row["eventId"]: "SUPPORTIVE" if index in jpy_supportive else "ADVERSE" for index, row in enumerate(by_side["JPY"])}
                assignments.append({**usd, **jpy})
        observed = {row["eventId"]: row["pressureState"] for row in rows}
        mapping = {("USD", "SUPPORTIVE"): "UP", ("USD", "ADVERSE"): "DOWN", ("JPY", "SUPPORTIVE"): "DOWN", ("JPY", "ADVERSE"): "UP"}
        mismatches = 0
        for bits in itertools.product((0, 1), repeat=13):
            realized = {row["eventId"]: self._direction_for_hit(row, bit) for row, bit in zip(rows, bits, strict=True)}
            reference_h = sum(mapping[(row["sideIdentity"], observed[row["eventId"]])] == realized[row["eventId"]] for row in rows)
            reference_p = sum(
                sum(mapping[(row["sideIdentity"], labels[row["eventId"]])] == realized[row["eventId"]] for row in rows) >= reference_h
                for labels in assignments
            ) / len(assignments)
            hit_by_event = {row["eventId"]: bit for row, bit in zip(rows, bits, strict=True)}
            reference_cluster = sum(
                sum(hit_by_event[event_id] for event_id in cluster["memberEventIds"]) / len(cluster["memberEventIds"])
                for cluster in s3.derive_overlap_clusters(rows)
            ) / 4
            reference_survival = "PILOT_ASSOCIATION_SURVIVED" if reference_h / 13 > 0.5 and reference_p <= 0.1 and reference_cluster > 0.5 else "PILOT_ASSOCIATION_NOT_SURVIVED"
            production = s3.exact_one_sided_permutation(rows, realized)
            production_cluster = s3.cluster_balanced_hit_rate(rows, hit_by_event)
            production_survival = s3.primary_survival_status(
                all_primary_validly_scorable=True,
                primary_hit_rate=production["observedHitCount"] / 13,
                exact_p_value=production["oneSidedPExact"],
                cluster_balanced_rate=production_cluster,
            )
            mismatches += int((production["observedHitCount"], production["oneSidedPExact"], production_cluster, production_survival) != (reference_h, reference_p, reference_cluster, reference_survival))
        self.assertEqual(mismatches, 0)

    def test_exhaustive_2744_timing_reference_matches_production(self) -> None:
        mismatches = 0
        for actual, minus7, plus7 in itertools.product(range(14), repeat=3):
            production = r1.s3r1.timing_specificity_status(
                actual_hit_count=actual,
                minus7_hit_count=minus7,
                plus7_hit_count=plus7,
            )
            reference = "TIMING_SPECIFICITY_DEMONSTRATED_WITHIN_PREREGISTERED_DIAGNOSTIC" if actual > minus7 and actual > plus7 else "TIMING_SPECIFICITY_NOT_DEMONSTRATED"
            mismatches += int(production != reference)
        self.assertEqual(mismatches, 0)

    def test_artifacts_schema_and_all_outcome_locks_are_deterministic(self) -> None:
        expected = {
            "adjudication": self.adjudication,
            "sourceLock": self.source_lock,
            "parserContract": self.parser_contract,
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
        r1.validate_json_schema_instance(self.preregistration, json.loads(self.artifacts["schema"].read_text(encoding="utf-8")))
        r3.validate_s3r1_r3_artifacts(PROJECT_ROOT)
        self.assertEqual(self.acceptance["branch"], "BRANCH_A_PROTOCOL_FULLY_CLOSED")
        self.assertFalse(self.acceptance["providerAccessPerformed"])
        self.assertFalse(self.acceptance["marketOutcomeRead"])
        self.assertFalse(self.acceptance["executionAllowed"])
        self.assertFalse(self.acceptance["outcomeUnlocked"])
        self.assertTrue(all(value is False for value in self.acceptance["outcomeAccessFlags"].values()))
        with self.assertRaises(r3.OutcomeAnalysisS3R1R3Error):
            r3.write_s3r1_r3_artifacts(PROJECT_ROOT, outcome_source=object())
        self.assertEqual(self.artifacts, r3.write_s3r1_r3_artifacts(PROJECT_ROOT))


if __name__ == "__main__":
    unittest.main()
