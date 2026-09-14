"""Synthetic-only tests for the one-attempt S4-A1 acquisition boundary."""

from __future__ import annotations

import ast
import io
import json
import lzma
import struct
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import market_data_acquisition_s4_a1 as acquisition


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _synthetic_valid_payload() -> bytes:
    native_records = b"".join(
        (
            struct.pack(">IIIff", 0, 158_123, 158_120, 1.25, 0.5),
            struct.pack(">IIIff", 86_399_999, 158_200, 158_200, 0.0, 3.5),
        )
    )
    return lzma.compress(native_records, format=lzma.FORMAT_ALONE)


class FakeTransport:
    def __init__(self, payload: bytes, overrides: dict[str, object] | None = None, *, content_length_delta: int = 0) -> None:
        self.payload = payload
        self.overrides = overrides or {}
        self.content_length_delta = content_length_delta
        self.calls: list[tuple[str, str, str]] = []

    def get_exact_partition(self, *, bucket: str, key: str, request_payer: str) -> acquisition.TransportObject:
        self.calls.append((bucket, key, request_payer))
        action = self.overrides.get(key)
        if isinstance(action, Exception):
            raise action
        payload = action if isinstance(action, bytes) else self.payload
        return acquisition.TransportObject(
            body=io.BytesIO(payload),
            content_length=len(payload) + self.content_length_delta,
            provider_metadata={"HTTPStatusCode": 200, "ContentLength": len(payload), "ETag": "synthetic"},
        )


class MarketDataAcquisitionS4A1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = _synthetic_valid_payload()
        self.authorization = acquisition.build_acquisition_authorization(PROJECT_ROOT)

    def _run(self, transport: FakeTransport, private_root: Path, *, authorization: dict[str, object] | None = None, execute: bool = True) -> acquisition.AcquisitionRun:
        return acquisition.acquire_authorized_partitions(
            project_root=PROJECT_ROOT,
            private_root=private_root,
            transport=transport,
            execute_authorized_acquisition=execute,
            authorization=authorization or self.authorization,
        )

    def test_preaccess_authorization_and_exact_plan_are_frozen(self) -> None:
        _, partitions = acquisition.validate_preaccess(PROJECT_ROOT, self.authorization)
        self.assertEqual(tuple(item["requestIdentity"]["key"] for item in partitions), acquisition.EXPECTED_KEYS)
        self.assertEqual(len(partitions), 15)
        self.assertEqual(self.authorization["acquisitionAuthorizationHash"], acquisition._canonical_hash({key: value for key, value in self.authorization.items() if key != "acquisitionAuthorizationHash"}))
        self.assertEqual(self.authorization["acquisitionModuleSha256"], acquisition.acquisition_module_sha256())
        self.assertTrue(self.authorization["sdkVersions"]["boto3"])
        self.assertTrue(self.authorization["sdkVersions"]["botocore"])
        self.assertFalse(self.authorization["outcomeUnlocked"])
        self.assertFalse(self.authorization["executionAllowed"])

    def test_successful_mock_run_requests_only_the_frozen_keys_and_freezes_before_parse(self) -> None:
        transport = FakeTransport(self.payload)
        events: list[str] = []
        original_parse = acquisition._parse_frozen_raw

        def observing_parse(partition: dict[str, object], raw_path: Path, parsed_path: Path) -> tuple[int, str, str, str]:
            self.assertTrue(raw_path.exists())
            self.assertGreater(raw_path.stat().st_size, 0)
            events.append("parse_after_raw_finalized")
            return original_parse(partition, raw_path, parsed_path)

        with tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            private_root = Path(temporary)
            with mock.patch.object(acquisition, "_parse_frozen_raw", side_effect=observing_parse):
                run = self._run(transport, private_root)
            self.assertEqual(run.status, "ACQUISITION_CAPTURED_AND_PROVENANCE_FROZEN_ANALYSIS_LOCKED")
            self.assertEqual(run.get_object_call_count, 15)
            self.assertEqual([call[1] for call in transport.calls], list(acquisition.EXPECTED_KEYS))
            self.assertTrue(all(call[0] == acquisition.BUCKET and call[2] == acquisition.REQUEST_PAYER for call in transport.calls))
            self.assertEqual(events, ["parse_after_raw_finalized"] * 15)
            self.assertTrue(all(record["byteLength"] == len(self.payload) for record in run.records))
            self.assertTrue(all(record["parsedRecordCount"] == 2 for record in run.records))
            self.assertTrue(all(record["rawSha256"] for record in run.records))
            self.assertTrue(all(record["parsedTicksSha256"] for record in run.records))
            self.assertTrue(all((private_root / "mo_r4a_s4_a1" / "raw" / str(record["logicalRawCaptureName"])).exists() for record in run.records))
            self.assertTrue(all((private_root / "mo_r4a_s4_a1" / "parsed" / str(record["logicalParsedCaptureName"])).exists() for record in run.records))
            manifest = acquisition.build_raw_manifest(run, self.authorization)
            self.assertNotIn(str(private_root), json.dumps(manifest))
            firewall = acquisition.build_outcome_firewall_audit(run, manifest["rawAcquisitionManifestHash"])
            self.assertTrue(firewall["outcomeAccessFlags"]["PRICE_DATA_READ"])
            self.assertFalse(any(value for name, value in firewall["outcomeAccessFlags"].items() if name != "PRICE_DATA_READ"))

    def test_missing_key_continues_without_inventing_a_file(self) -> None:
        missing_key = acquisition.EXPECTED_KEYS[3]
        transport = FakeTransport(self.payload, {missing_key: acquisition.TransportFailure("MISSING_DOCUMENTED_DAILY_KEY", "synthetic 404", status_code=404, missing=True)})
        with tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            run = self._run(transport, Path(temporary))
        self.assertEqual(run.status, "ACQUISITION_CAPTURED_AND_PROVENANCE_FROZEN_ANALYSIS_LOCKED")
        self.assertEqual(run.get_object_call_count, 15)
        record = run.records[3]
        self.assertEqual(record["acquisitionDisposition"], "MISSING_DOCUMENTED_DAILY_KEY_NO_TICKS")
        self.assertIsNone(record["rawSha256"])
        self.assertEqual(record["parsedRecordCount"], 0)

    def test_terminal_transport_failures_stop_without_retry(self) -> None:
        cases = (
            acquisition.TransportFailure("AccessDenied", "synthetic", status_code=403),
            acquisition.TransportFailure("ExpiredToken", "synthetic", status_code=403),
            acquisition.TransportFailure("NETWORK_TIMEOUT", "synthetic"),
            acquisition.TransportFailure("HTTP_500", "synthetic", status_code=500),
        )
        for failure in cases:
            with self.subTest(failure=failure.code), tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
                transport = FakeTransport(self.payload, {acquisition.EXPECTED_KEYS[0]: failure})
                run = self._run(transport, Path(temporary))
                self.assertEqual(run.status, "ACQUISITION_ATTEMPT_INCOMPLETE_CENTRAL_REVIEW_REQUIRED")
                self.assertEqual(run.get_object_call_count, 1)
                self.assertEqual(len(transport.calls), 1)
                self.assertEqual(run.terminal_error_code, failure.code)

    def test_zero_byte_and_length_mismatch_are_terminal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            transport = FakeTransport(b"")
            with mock.patch.object(acquisition, "_parse_frozen_raw") as parser_mock:
                run = self._run(transport, Path(temporary))
            parser_mock.assert_not_called()
            self.assertEqual(run.terminal_error_code, "SUCCESSFUL_ZERO_BYTE_RESPONSE_ACQUISITION_INCOMPLETE")
            self.assertEqual(run.get_object_call_count, 1)
        with tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            transport = FakeTransport(self.payload, content_length_delta=1)
            run = self._run(transport, Path(temporary))
            self.assertEqual(run.terminal_error_code, "PROVIDER_CONTENT_LENGTH_MISMATCH")
            self.assertEqual(run.get_object_call_count, 1)

    def test_frozen_parser_rejects_every_invalid_compressed_variant_without_fallback(self) -> None:
        alternate = lzma.compress(struct.pack(">IIIff", 0, 158_123, 158_120, 1.0, 1.0), format=lzma.FORMAT_XZ)
        variants = {
            "corrupt": b"not-a-compressed-stream",
            "truncated": self.payload[:-4],
            "garbage": self.payload + b"garbage",
            "second_alone": self.payload + self.payload,
            "xz": alternate,
        }
        for name, raw in variants.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
                run = self._run(FakeTransport(raw), Path(temporary))
                self.assertEqual(run.status, "ACQUISITION_ATTEMPT_INCOMPLETE_CENTRAL_REVIEW_REQUIRED")
                self.assertEqual(run.terminal_error_code, "FROZEN_PARSER_REJECTED_REAL_PROVIDER_CAPTURE_REVIEW_REQUIRED")
                self.assertEqual(run.get_object_call_count, 1)

    def test_storage_and_journal_conflicts_fail_closed(self) -> None:
        _, partitions = acquisition.validate_preaccess(PROJECT_ROOT, self.authorization)
        first = partitions[0]
        with self.subTest("preexisting_attempt_started"), tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            private_root = Path(temporary)
            journal = acquisition._journal_path(private_root, acquisition.deterministic_request_id(first))
            acquisition._atomic_write_json(journal, {"status": "ATTEMPT_STARTED"})
            transport = FakeTransport(self.payload)
            with self.assertRaisesRegex(acquisition.AcquisitionError, "ATTEMPT_STATUS_UNKNOWN_REVIEW_REQUIRED"):
                self._run(transport, private_root)
            self.assertEqual(transport.calls, [])
        with self.subTest("existing_finalized_raw"), tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            private_root = Path(temporary)
            raw = private_root / "mo_r4a_s4_a1" / "raw" / acquisition._logical_capture_name(first, "bi5")
            acquisition._atomic_write_bytes(raw, b"synthetic prior bytes")
            transport = FakeTransport(self.payload)
            with self.assertRaisesRegex(acquisition.AcquisitionError, "EXISTING_FINALIZED_CAPTURE_CONFLICT"):
                self._run(transport, private_root)
            self.assertEqual(transport.calls, [])
        with self.subTest("storage_write_failure"), tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            private_root = Path(temporary)
            blocking_path = private_root / "mo_r4a_s4_a1" / "raw"
            blocking_path.parent.mkdir(parents=True, exist_ok=True)
            blocking_path.write_bytes(b"not a directory")
            run = self._run(FakeTransport(self.payload), private_root)
            self.assertEqual(run.terminal_error_code, "EXTERNAL_STORAGE_WRITE_FAILED")
            self.assertEqual(run.get_object_call_count, 1)

    def test_revision_identity_and_non_execution_gates_are_fail_closed(self) -> None:
        record = {"requestId": "stable", "rawSha256": "A" * 64}
        with self.assertRaisesRegex(acquisition.AcquisitionError, "PROVIDER_REVISION_CONFLICT"):
            acquisition.assert_same_request_raw_identity((record, {**record, "rawSha256": "B" * 64}))
        with tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            transport = FakeTransport(self.payload)
            with self.assertRaisesRegex(acquisition.AcquisitionError, "EXECUTION_FLAG_REQUIRED"):
                self._run(transport, Path(temporary), execute=False)
            self.assertEqual(transport.calls, [])
        with tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            bad = dict(self.authorization)
            bad["partitionPlanHash"] = "0" * 64
            transport = FakeTransport(self.payload)
            with self.assertRaisesRegex(acquisition.AcquisitionError, "AUTHORIZATION_HASH_MISMATCH|AUTHORIZATION_MISMATCH"):
                self._run(transport, Path(temporary), authorization=bad)
            self.assertEqual(transport.calls, [])
        with tempfile.TemporaryDirectory(prefix="mo-r4a-s4-a1-") as temporary:
            transport = FakeTransport(self.payload)
            original_verify_plan = acquisition._verify_plan

            def altered_verify_plan(plan: dict[str, object]) -> tuple[dict[str, object], ...]:
                partitions = list(original_verify_plan(plan))
                altered = dict(partitions[0])
                altered["requestIdentity"] = {**altered["requestIdentity"], "key": "USDJPY/2025/02/99_ticks.bi5"}
                return tuple([altered, *partitions[1:]])

            with mock.patch.object(acquisition, "_verify_plan", side_effect=altered_verify_plan):
                altered_authorization = acquisition.build_acquisition_authorization(PROJECT_ROOT)
                with self.assertRaisesRegex(acquisition.AcquisitionError, "UNEXPECTED_PARTITION_KEY"):
                    self._run(transport, Path(temporary), authorization=altered_authorization)
            self.assertEqual(transport.calls, [])

    def test_sdk_retry_policy_and_static_outcome_firewall(self) -> None:
        self.assertEqual(acquisition.SDK_RETRY_CONFIG["total_max_attempts"], 1)
        self.assertEqual(acquisition.SDK_RETRY_CONFIG["mode"], "standard")
        client_config = acquisition.build_botocore_config()
        self.assertEqual(client_config.region_name, acquisition.REGION)
        self.assertEqual(client_config.retries["total_max_attempts"], 1)
        self.assertEqual(client_config.retries["mode"], "standard")
        source = Path(acquisition.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name.split(".")[0]
            for node in tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".")[0]
            for node in tree.body
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertFalse(imported & {"outcome_analysis_s3", "outcome_analysis_s3r1", "math", "statistics"})
        for forbidden in ("math.log", "H_observed", "pExact", "clusterBalanced", "survival"):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("get_object(", source.split("class Boto3ExactPartitionTransport", 1)[0])
        self.assertNotIn("list_objects", source.lower())
        self.assertNotIn("head_object", source.lower())

    def test_provider_metadata_is_json_safe_without_retaining_credentials_or_paths(self) -> None:
        metadata = acquisition._safe_metadata({
            "HTTPStatusCode": 200,
            "LastModified": datetime(2025, 3, 24, 0, 0, tzinfo=timezone.utc),
            "Ignored": "not admitted",
        })
        self.assertEqual(metadata, {"HTTPStatusCode": 200, "LastModified": "2025-03-24T00:00:00+00:00"})
        json.dumps(metadata, sort_keys=True)

    def test_provenance_builders_hold_outcome_locks_and_no_private_path(self) -> None:
        run = acquisition.AcquisitionRun(
            records=(
                {
                    "requestId": "one", "providerPartitionId": "partition", "transportStatus": "GET_OBJECT_SUCCESS",
                    "rawSha256": "A" * 64, "parsedTicksSha256": "B" * 64, "parsedRecordCount": 2,
                },
            ),
            provider_access_performed=True,
            price_data_mechanically_parsed=True,
            status="ACQUISITION_CAPTURED_AND_PROVENANCE_FROZEN_ANALYSIS_LOCKED",
            terminal_error_code=None,
            terminal_error_detail=None,
            requested_key_count=15,
            get_object_call_count=15,
        )
        manifest = acquisition.build_raw_manifest(run, self.authorization)
        firewall = acquisition.build_outcome_firewall_audit(run, manifest["rawAcquisitionManifestHash"])
        _, gate = acquisition.build_freeze_or_exception_gate(run, manifest, firewall)
        self.assertEqual(manifest["rawAcquisitionManifestHash"], acquisition._canonical_hash({key: value for key, value in manifest.items() if key != "rawAcquisitionManifestHash"}))
        self.assertTrue(firewall["outcomeAccessFlags"]["PRICE_DATA_READ"])
        self.assertFalse(firewall["outcomeDataRead"])
        self.assertFalse(firewall["executionAllowed"])
        self.assertFalse(gate["outcomeUnlocked"])
        self.assertFalse(gate["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
