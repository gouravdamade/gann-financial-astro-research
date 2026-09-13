"""Focused tests for MO-R4A-S3R1-R3-R2 integrity corrections."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import lzma
import os
import shutil
import struct
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
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

import dukascopy_tick_parser_s3r1_r3 as historical_parser  # noqa: E402
import dukascopy_tick_parser_s3r1_r3_r2 as parser  # noqa: E402
import outcome_analysis_s3r1_r1 as r1  # noqa: E402
import outcome_analysis_s3r1_r2 as r2  # noqa: E402
import outcome_analysis_s3r1_r3 as r3  # noqa: E402
import outcome_analysis_s3r1_r3_r1 as r3r1  # noqa: E402
import outcome_analysis_s3r1_r3_r2 as r3r2  # noqa: E402


PREDICTION_FREEZE_RELATIVE = Path("status/audits/mo_r4a_s2r1_r1_blinded_market_bridge_prediction_freeze.json")
HISTORICAL_PARSER_SHA256 = "47BEF7B1A13D8EE4EC2DDED2BDD965A27D41FCB548EC0D4D940A5535669D733E"


def _synthetic_payload(*records: tuple[int, int, int, float, float], format_value: int = lzma.FORMAT_ALONE) -> bytes:
    decoded = b"".join(struct.pack(">IIIff", *record) for record in records)
    return lzma.compress(decoded, format=format_value)


def _copy_contract_tree(destination: Path) -> None:
    for relative in (Path("configs/research"), Path("status/audits"), Path("status/acceptance")):
        shutil.copytree(PROJECT_ROOT / relative, destination / relative)
    for relative in (
        Path("gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3.py"),
        Path("gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3_r2.py"),
    ):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_ROOT / relative, target)


def _mutate_prediction_freeze(path: Path) -> None:
    freeze = json.loads(path.read_text(encoding="utf-8"))
    prediction = freeze["predictions"][0]
    shifted = datetime.fromisoformat(prediction["applyingStartUtc"].replace("Z", "+00:00")) + timedelta(seconds=1)
    prediction["applyingStartUtc"] = shifted.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prediction_body = {key: copy.deepcopy(value) for key, value in prediction.items() if key != "eventPredictionHash"}
    prediction["eventPredictionHash"] = r3r2._canonical_hash(prediction_body)
    freeze_body = {key: copy.deepcopy(value) for key, value in freeze.items() if key != "predictionFreezeHash"}
    freeze["predictionFreezeHash"] = r3r2._canonical_hash(freeze_body)
    path.write_text(json.dumps(freeze, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


class OutcomeAnalysisS3R1R3R2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = r3r2.write_artifacts(PROJECT_ROOT)
        r3r2.validate_artifacts(PROJECT_ROOT)
        cls.parser_contract = json.loads(cls.paths["parserContract"].read_text(encoding="utf-8"))
        cls.acquisition = json.loads(cls.paths["acquisition"].read_text(encoding="utf-8"))
        cls.preregistration = json.loads(cls.paths["preregistration"].read_text(encoding="utf-8"))
        cls.schema = json.loads(cls.paths["schema"].read_text(encoding="utf-8"))
        cls.population = json.loads(cls.paths["population"].read_text(encoding="utf-8"))
        cls.clusters = json.loads(cls.paths["clusters"].read_text(encoding="utf-8"))
        cls.invariance = json.loads(cls.paths["invariance"].read_text(encoding="utf-8"))
        cls.core = json.loads(cls.paths["core"].read_text(encoding="utf-8"))
        cls.acceptance = json.loads(cls.paths["acceptance"].read_text(encoding="utf-8"))
        cls.disposition = json.loads(cls.paths["disposition"].read_text(encoding="utf-8"))

    def test_clean_validation_is_repeatable_without_stateful_drift(self) -> None:
        for _ in range(3):
            r3r2.validate_artifacts(PROJECT_ROOT)
        first = {name: path.read_bytes() for name, path in self.paths.items()}
        r3r2.write_artifacts(PROJECT_ROOT)
        second = {name: path.read_bytes() for name, path in self.paths.items()}
        self.assertEqual(first, second)

    def test_filesystem_mutation_is_rejected_then_exact_restore_recovers(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mo-r4a-s3r1-r3-r2-cache-") as temporary:
            root = Path(temporary)
            _copy_contract_tree(root)
            r3r2.validate_artifacts(root)
            freeze_path = root / PREDICTION_FREEZE_RELATIVE
            original = freeze_path.read_bytes()
            _mutate_prediction_freeze(freeze_path)
            with self.assertRaises(ValueError) as context:
                r3r2.validate_artifacts(root)
            message = str(context.exception).lower()
            self.assertTrue(any(token in message for token in ("prediction", "freeze", "upstream", "immutable")))
            freeze_path.write_bytes(original)
            r3r2.validate_artifacts(root)

    def test_second_integrity_critical_predecessor_mutation_is_rejected_and_restored(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mo-r4a-s3r1-r3-r2-predecessor-") as temporary:
            root = Path(temporary)
            _copy_contract_tree(root)
            r3r2.validate_artifacts(root)
            predecessor = root / "status/acceptance/mo_r4a_s3r1_r3_r1_outcome_analysis_preregistration.json"
            original = predecessor.read_bytes()
            predecessor_payload = json.loads(original)
            predecessor_payload["executionAllowed"] = True
            predecessor.write_text(json.dumps(predecessor_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                r3r2.validate_artifacts(root)
            predecessor.write_bytes(original)
            r3r2.validate_artifacts(root)

    def test_no_persistent_integrity_validation_cache_remains(self) -> None:
        for module in (r2, r3r1, r3r2):
            source = Path(module.__file__).read_text(encoding="utf-8")
            self.assertNotIn("from functools import lru_cache", source)
            self.assertNotIn("from functools import cache", source)
            self.assertNotIn("@lru_cache", source)
            self.assertNotIn("@cache", source)
        self.assertNotIn("_assert_r1_predecessor_cached", Path(r2.__file__).read_text(encoding="utf-8"))
        self.assertNotIn("_validated_historical_r3", Path(r3r1.__file__).read_text(encoding="utf-8"))
        self.assertNotIn("cache" + "_clear", Path(__file__).read_text(encoding="utf-8"))

    def test_successor_contract_binds_parser_and_preserves_scientific_invariants(self) -> None:
        self.assertEqual(self.parser_contract["contract"], parser.PARSER_CONTRACT)
        self.assertEqual(self.parser_contract["parserSourceSha256"], r3r2.parser_source_sha256(PROJECT_ROOT))
        self.assertEqual(hashlib.sha256((BACKEND_ROOT / "dukascopy_tick_parser_s3r1_r3.py").read_bytes()).hexdigest().upper(), HISTORICAL_PARSER_SHA256)
        self.assertEqual(self.parser_contract["streamIntegrity"]["exactSingleCompressedStream"], True)
        self.assertEqual(self.parser_contract["streamIntegrity"]["compressedStreamEofRequired"], True)
        self.assertEqual(self.parser_contract["streamIntegrity"]["unusedDataAllowed"], False)
        self.assertEqual(self.parser_contract["streamIntegrity"]["unusedDataPolicy"], "REJECT")
        self.assertEqual(self.acquisition["nativePartitioning"]["uniqueProviderPartitionCount"], 15)
        self.assertEqual(self.acquisition["frozenIntervalSet"]["totalCount"], 39)
        self.assertEqual(self.population["populationCounts"]["frozenEventCount"], 24)
        self.assertEqual(self.population["populationCounts"]["directionalCount"], 14)
        self.assertEqual(self.population["populationCounts"]["primaryMarketScorableCount"], 13)
        self.assertEqual(self.population["populationCounts"], self.acceptance["populationAccounting"])
        self.assertFalse(self.preregistration["scientificDesignChanged"])
        self.assertFalse(self.acceptance["providerProtocolFullyClosed"])
        self.assertFalse(self.acceptance["outcomeUnlocked"])
        self.assertFalse(self.acceptance["executionAllowed"])
        self.assertTrue(all(value is False for value in self.acceptance["outcomeAccessFlags"].values()))

    def test_successor_parser_accepts_one_stream_and_rejects_every_suffix_shape(self) -> None:
        valid = _synthetic_payload((1_000, 158_123, 158_120, 1.0, 2.0))
        suffix_cases = {
            "garbage": valid + b"garbage",
            "zero": valid + b"\x00",
            "xz": valid + lzma.compress(b"suffix", format=lzma.FORMAT_XZ),
            "second_alone": valid + valid,
            "arbitrary_record_bytes": valid + (b"x" * 20),
        }
        records = parser.parse_daily_bi5(valid, partition_date_utc=date(2030, 1, 1))
        self.assertEqual(len(records), 1)
        for label, payload in suffix_cases.items():
            with self.subTest(label=label):
                with self.assertRaises(parser.DukascopyTickParserError) as context:
                    parser.parse_daily_bi5(payload, partition_date_utc=date(2030, 1, 1))
                self.assertEqual(context.exception.code, "COMPRESSION_TRAILING_DATA")

    def test_successor_parser_classifies_incomplete_corrupt_xz_only_and_zero_payloads(self) -> None:
        valid = _synthetic_payload((1_000, 158_123, 158_120, 1.0, 2.0))
        corrupt = bytearray(valid)
        corrupt[15] ^= 1
        cases = {
            "truncated": (valid[:-1], "COMPRESSION_STREAM_INCOMPLETE"),
            "corrupt": (bytes(corrupt), "COMPRESSION_DECODE_FAILED"),
            "xz_only": (lzma.compress(b"x", format=lzma.FORMAT_XZ), "COMPRESSION_FORMAT_MISMATCH"),
            "zero": (b"", "ZERO_BYTE_PAYLOAD_ACQUISITION_INCOMPLETE"),
        }
        for label, (payload, expected_code) in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(parser.DukascopyTickParserError) as context:
                    parser.parse_daily_bi5(payload, partition_date_utc=date(2030, 1, 1))
                self.assertEqual(context.exception.code, expected_code)

    def test_valid_successor_output_matches_historical_parser_and_prefix_attack_differs(self) -> None:
        valid = _synthetic_payload(
            (0, 158_123, 158_120, 1.25, 0.5),
            (86_399_999, 158_200, 158_200, 0.0, 3.5),
        )
        historical = historical_parser.parse_daily_bi5(valid, partition_date_utc=date(2030, 1, 1))
        successor = parser.parse_daily_bi5(valid, partition_date_utc=date(2030, 1, 1))
        attributes = ("partition_id", "record_index", "timestamp_utc", "ask_native", "bid_native", "ask_volume_bits_hex", "bid_volume_bits_hex")
        self.assertEqual([[getattr(row, field) for field in attributes] for row in historical], [[getattr(row, field) for field in attributes] for row in successor])
        self.assertEqual(historical_parser.canonical_parsed_tick_json_lines(historical), parser.canonical_parsed_tick_json_lines(successor))
        self.assertEqual(historical_parser.parsed_ticks_sha256(historical), parser.parsed_ticks_sha256(successor))
        self.assertEqual(len(historical_parser.parse_daily_bi5(valid + b"garbage", partition_date_utc=date(2030, 1, 1))), 2)
        with self.assertRaises(parser.DukascopyTickParserError) as context:
            parser.parse_daily_bi5(valid + b"garbage", partition_date_utc=date(2030, 1, 1))
        self.assertEqual(context.exception.code, "COMPRESSION_TRAILING_DATA")

    def test_schema_mutations_and_firewall_are_fail_closed(self) -> None:
        for field, value in (
            ("parserContractHash", "0" * 64),
            ("parserSourceSha256", "0" * 64),
            ("providerProtocolFullyClosed", True),
        ):
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.preregistration)
                mutated[field] = value
                with self.assertRaises(r1.OutcomeAnalysisS3R1R1Error):
                    r1.validate_json_schema_instance(mutated, self.schema)
        for source in (
            Path(r2.__file__).read_text(encoding="utf-8"),
            Path(r3.__file__).read_text(encoding="utf-8"),
            Path(r3r1.__file__).read_text(encoding="utf-8"),
            Path(r3r2.__file__).read_text(encoding="utf-8"),
        ):
            tree = ast.parse(source)
            imports = {
                alias.name.split(".")[0]
                for node in tree.body
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            self.assertFalse(imports & {"boto3", "botocore", "requests", "urllib", "httpx", "aiohttp", "socket", "ccxt", "yfinance"})

    def test_no_provider_bytes_and_outcome_firewall_flags_are_present(self) -> None:
        self.assertFalse(list(PROJECT_ROOT.rglob("*.bi5")))
        self.assertFalse(self.acquisition["providerAccessPerformed"])
        self.assertFalse(self.acquisition["marketOutcomeRead"])
        self.assertFalse(self.acquisition["executionAllowed"])
        self.assertFalse(self.acceptance["providerAccessPerformed"])
        self.assertFalse(self.acceptance["marketOutcomeRead"])
        self.assertFalse(self.acceptance["executionAllowed"])
        self.assertFalse(self.disposition["scientificDesignChanged"])
        self.assertFalse(self.disposition["providerAccessPerformed"])
        self.assertFalse(self.disposition["marketOutcomeRead"])
        self.assertFalse(self.disposition["executionAllowed"])
        self.assertTrue(all(value is False for value in self.disposition["outcomeAccessFlags"].values()))


if __name__ == "__main__":
    unittest.main()
