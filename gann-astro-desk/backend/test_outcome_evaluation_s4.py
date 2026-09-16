"""Synthetic-only O1 tests. No private capture root is referenced by this suite."""

from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import outcome_evaluation_s4 as s4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UTC = timezone.utc


def _interval(*, side: str = "USD", label: str = "SUPPORTIVE") -> dict[str, object]:
    return {
        "intervalId": "SYNTH_EVENT::ACTUAL",
        "eventId": "SYNTH_EVENT",
        "horizon": "ACTUAL",
        "sideIdentity": side,
        "frozenLabel": label,
        "applyingStartUtc": "2030-01-01T10:00:00Z",
        "separatingEndUtc": "2030-01-01T11:00:00Z",
        "durationSeconds": 3600,
        "halfOpen": True,
    }


def _tick(second: int, bid: int, ask: int | None = None, *, day: int = 1, index: int = 0) -> s4.ParsedTick:
    base = datetime(2030, 1, day, 10, 0, 0, tzinfo=UTC)
    return s4.ParsedTick(
        "USDJPY/2030/00/01_ticks.bi5",
        index,
        base + timedelta(seconds=second),
        bid if ask is None else ask,
        bid,
    )


def _line(record: dict[str, object]) -> bytes:
    return s4._canonical_bytes(record) + b"\n"


class OutcomeEvaluationS4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.study = s4.load_frozen_study(PROJECT_ROOT)

    def _interval_results(
        self,
        *,
        actual_hits: dict[str, int] | None = None,
        shifted_hit_counts: dict[str, int] | None = None,
        incomplete_interval_id: str | None = None,
    ) -> list[dict[str, object]]:
        actual_hits = actual_hits or {}
        shifted_hit_counts = shifted_hit_counts or {}
        primary_order = [event["eventId"] for event in self.study.primary_events]
        result_rows: list[dict[str, object]] = []
        shifted_seen = {"MINUS_7": 0, "PLUS_7": 0}
        for interval in self.study.intervals:
            horizon = interval["horizon"]
            if horizon == "ACTUAL":
                is_hit = actual_hits.get(interval["eventId"], 0)
            else:
                target = shifted_hit_counts.get(horizon, 0)
                is_hit = int(primary_order.index(interval["eventId"]) < target)
                shifted_seen[horizon] += is_hit
            row: dict[str, object] = {
                "intervalId": interval["intervalId"],
                "eventId": interval["eventId"],
                "horizon": horizon,
                "sideIdentity": interval["sideIdentity"],
                "frozenLabel": interval["frozenLabel"],
                "expectedDirection": s4.EXPECTED_DIRECTION[(interval["sideIdentity"], interval["frozenLabel"])],
                "scorable": True,
                "status": "SCORED",
                "startTimestampUtc": s4._format_utc(s4._utc_datetime(interval["applyingStartUtc"]) + timedelta(seconds=1)),
                "endTimestampUtc": s4._format_utc(s4._utc_datetime(interval["separatingEndUtc"]) - timedelta(seconds=1)),
                "logReturn": "0.01" if s4.EXPECTED_Q[s4.EXPECTED_DIRECTION[(interval["sideIdentity"], interval["frozenLabel"])]] * (1 if is_hit else -1) > 0 else "-0.01",
                "hit": int(is_hit),
            }
            if interval["intervalId"] == incomplete_interval_id:
                row.update({"scorable": False, "status": "DATA_UNSCORABLE", "startTimestampUtc": None, "endTimestampUtc": None, "logReturn": None, "hit": None})
            result_rows.append(row)
        return result_rows

    def _primary_actual_rows(self, hits: dict[str, int]) -> dict[str, dict[str, object]]:
        return {
            row["eventId"]: row
            for row in self._interval_results(actual_hits=hits)
            if row["horizon"] == "ACTUAL"
        }

    def test_frozen_artifacts_bind_exact_population_intervals_and_hashes(self) -> None:
        self.assertEqual(len(self.study.all_events), 24)
        self.assertEqual(len(self.study.primary_events), 13)
        self.assertEqual(len(self.study.intervals), 39)
        self.assertEqual([len(item["memberEventIds"]) for item in self.study.clusters], [5, 1, 2, 5])
        self.assertEqual(len(self.study.partitions), 15)
        self.assertEqual(self.study.input_hashes["astraDispositionHash"], s4.FREEZE_HASHES["astraDispositionHash"])

    def test_start_boundary_is_included_and_end_boundary_is_excluded(self) -> None:
        row = s4.score_interval(_interval(), [_tick(0, 100, 101), _tick(30, 110, 111), _tick(3600, 900, 901)])
        self.assertEqual(row["startTimestampUtc"], "2030-01-01T10:00:00.000Z")
        self.assertEqual(row["endTimestampUtc"], "2030-01-01T10:00:30.000Z")

    def test_first_tick_strictly_after_start_is_selected(self) -> None:
        row = s4.score_interval(_interval(), [_tick(-1, 90), _tick(1, 100), _tick(2, 101)])
        self.assertEqual(row["startTimestampUtc"], "2030-01-01T10:00:01.000Z")

    def test_last_tick_strictly_before_end_is_selected(self) -> None:
        row = s4.score_interval(_interval(), [_tick(1, 100), _tick(3599, 101), _tick(3600, 900)])
        self.assertEqual(row["endTimestampUtc"], "2030-01-01T10:59:59.000Z")

    def test_no_outside_interval_rescue(self) -> None:
        row = s4.score_interval(_interval(), [_tick(-10, 100), _tick(3610, 101)])
        self.assertEqual(row["status"], "DATA_UNSCORABLE")
        self.assertIsNone(row["hit"])

    def test_fewer_than_two_distinct_timestamps_is_unscorable(self) -> None:
        row = s4.score_interval(_interval(), [_tick(1, 100), _tick(1, 100, index=1)])
        self.assertEqual(row["status"], "DATA_UNSCORABLE")

    def test_identical_duplicate_quote_at_same_timestamp_is_deduplicated(self) -> None:
        row = s4.score_interval(_interval(), [_tick(1, 100), _tick(1, 100, index=1), _tick(2, 102, index=2)])
        self.assertTrue(row["scorable"])

    def test_conflicting_quotes_at_same_timestamp_fail_closed(self) -> None:
        row = s4.score_interval(_interval(), [_tick(1, 100), _tick(1, 101, index=1), _tick(2, 102, index=2)])
        self.assertEqual(row["status"], "DATA_CONFLICT_UNSCORABLE")

    def test_conflict_outside_interval_does_not_poison_interval(self) -> None:
        row = s4.score_interval(_interval(), [_tick(-1, 100), _tick(-1, 101, index=1), _tick(1, 102), _tick(2, 103)])
        self.assertTrue(row["scorable"])

    def test_invalid_bid_ask_inside_interval_is_unscorable(self) -> None:
        row = s4.score_interval(_interval(), [_tick(1, 100), _tick(2, 0, 101, index=1)])
        self.assertEqual(row["status"], "DATA_NUMERIC_INVALID_UNSCORABLE")

    def test_malformed_timestamp_fails_with_typed_error(self) -> None:
        record = {"partitionId": "USDJPY/2030/00/01_ticks.bi5", "recordIndex": 0, "timestampUtc": "not-a-time", "askNative": 101, "bidNative": 100, "askVolumeBitsHex": "00000000", "bidVolumeBitsHex": "00000000"}
        with self.assertRaises(s4.S4EvaluationError) as raised:
            s4._parse_tick_line(_line(record), "USDJPY/2030/00/01_ticks.bi5", datetime(2030, 1, 1).date(), 0)
        self.assertEqual(raised.exception.code, "DATA_TIMESTAMP_INVALID")

    def test_zero_return_is_a_directional_miss(self) -> None:
        row = s4.score_interval(_interval(), [_tick(1, 100, 101), _tick(2, 100, 101, index=1)])
        self.assertEqual(row["status"], "ZERO_MOVE")
        self.assertEqual(row["hit"], 0)

    def test_up_hit(self) -> None:
        row = s4.score_interval(_interval(), [_tick(1, 100), _tick(2, 110, index=1)])
        self.assertEqual(row["expectedDirection"], "UP")
        self.assertEqual(row["hit"], 1)

    def test_down_hit(self) -> None:
        row = s4.score_interval(_interval(label="ADVERSE"), [_tick(1, 110), _tick(2, 100, index=1)])
        self.assertEqual(row["expectedDirection"], "DOWN")
        self.assertEqual(row["hit"], 1)

    def test_usd_supportive_mapping(self) -> None:
        self.assertEqual(s4.EXPECTED_DIRECTION[("USD", "SUPPORTIVE")], "UP")

    def test_usd_adverse_mapping(self) -> None:
        self.assertEqual(s4.EXPECTED_DIRECTION[("USD", "ADVERSE")], "DOWN")

    def test_jpy_supportive_mapping(self) -> None:
        self.assertEqual(s4.EXPECTED_DIRECTION[("JPY", "SUPPORTIVE")], "DOWN")

    def test_jpy_adverse_mapping(self) -> None:
        self.assertEqual(s4.EXPECTED_DIRECTION[("JPY", "ADVERSE")], "UP")

    def test_midpoint_uses_divisor_1000_and_fixed_decimal_logarithm(self) -> None:
        midpoint = s4._native_midpoint(100_000, 101_000)
        self.assertEqual(midpoint, s4.Decimal("100.5"))
        self.assertEqual(s4.NUMERIC_PRECISION, 50)
        self.assertEqual(s4.NUMERIC_ROUNDING, s4.ROUND_HALF_EVEN)

    def test_exact_40_side_local_permutation_assignments(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4._permutation_result(self.study.primary_events, self._primary_actual_rows(hits))
        self.assertEqual(result["assignmentCount"], 40)
        self.assertEqual(len(result["allAssignments"]), 40)

    def test_observed_assignment_is_included(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4._permutation_result(self.study.primary_events, self._primary_actual_rows(hits))
        self.assertGreaterEqual(result["observedAssignmentIndex"], 0)
        self.assertLess(result["observedAssignmentIndex"], 40)

    def test_permutation_tail_is_inclusive(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4._permutation_result(self.study.primary_events, self._primary_actual_rows(hits))
        expected_tail = sum(row["permutationHitCount"] >= result["observedHitCount"] for row in result["allAssignments"])
        self.assertEqual(result["inclusiveTailCount"], expected_tail)
        self.assertEqual(result["pExact"], s4._ratio(expected_tail, 40))

    def test_zero_move_is_retained_as_a_permutation_miss(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        rows = self._primary_actual_rows(hits)
        first_event = self.study.primary_events[0]["eventId"]
        rows[first_event].update({"status": "ZERO_MOVE", "logReturn": "0", "hit": 0})
        result = s4._permutation_result(self.study.primary_events, rows)
        self.assertEqual(result["observedHitCount"], 12)

    def test_primary_denominator_is_always_13_on_incomplete_data(self) -> None:
        rows = self._interval_results(actual_hits={event["eventId"]: 1 for event in self.study.primary_events}, incomplete_interval_id=self.study.primary_events[0]["eventId"] + "::ACTUAL")
        result = s4.build_result(self.study, rows)
        self.assertEqual(result["primary"]["denominator"], 13)
        self.assertEqual(result["primary"]["status"], "PRIMARY_EVALUATION_INVALID_DATA_INCOMPLETE")
        self.assertIsNone(result["primary"]["observedHitCount"])
        self.assertIsNone(result["permutation"]["pExact"])

    def test_c1_through_c4_membership_is_exact_and_complete(self) -> None:
        members = [item for cluster in self.study.clusters for item in cluster["memberEventIds"]]
        self.assertEqual([cluster["clusterId"] for cluster in self.study.clusters], ["C1", "C2", "C3", "C4"])
        self.assertEqual(len(members), 13)
        self.assertEqual(len(set(members)), 13)
        self.assertEqual(set(members), {event["eventId"] for event in self.study.primary_events})

    def test_cluster_balancing_gives_each_cluster_equal_weight(self) -> None:
        c2_event = self.study.clusters[1]["memberEventIds"][0]
        result = s4._cluster_result(self.study.clusters, {event["eventId"]: int(event["eventId"] == c2_event) for event in self.study.primary_events})
        self.assertEqual(result["equalWeightedHitRateFraction"], "1/4")
        self.assertEqual(result["equalWeightedHitRate"], "0.25")

    def test_timing_requires_actual_strictly_greater_than_both_shifts(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4.build_result(self.study, self._interval_results(actual_hits=hits, shifted_hit_counts={"MINUS_7": 8, "PLUS_7": 7}))
        self.assertEqual(result["timing"]["status"], "TIMING_SPECIFICITY_DEMONSTRATED_WITHIN_PREREGISTERED_DIAGNOSTIC")

    def test_timing_tie_is_not_demonstrated(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4.build_result(self.study, self._interval_results(actual_hits=hits, shifted_hit_counts={"MINUS_7": 13, "PLUS_7": 2}))
        self.assertEqual(result["timing"]["status"], "TIMING_SPECIFICITY_NOT_DEMONSTRATED")

    def test_timing_incomplete_if_any_shifted_event_is_unscorable(self) -> None:
        interval_id = self.study.primary_events[0]["eventId"] + "::PLUS_7"
        result = s4.build_result(self.study, self._interval_results(actual_hits={event["eventId"]: 1 for event in self.study.primary_events}, incomplete_interval_id=interval_id))
        self.assertEqual(result["timing"]["status"], "TIMING_DIAGNOSTIC_INCOMPLETE")

    def test_survival_rule_passes_only_when_all_frozen_thresholds_pass(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4.build_result(self.study, self._interval_results(actual_hits=hits))
        self.assertEqual(result["survivalStatus"], "PILOT_ASSOCIATION_SURVIVED")

    def test_survival_fails_when_p_exact_exceeds_point_one(self) -> None:
        self.assertEqual(s4._survival_decision(True, Fraction(1, 1), Fraction(5, 40), Fraction(1, 1)), "PILOT_ASSOCIATION_NOT_SURVIVED")

    def test_exact_half_hit_rate_fails_strict_survival_boundary(self) -> None:
        self.assertEqual(s4._survival_decision(True, Fraction(1, 2), Fraction(1, 40), Fraction(1, 1)), "PILOT_ASSOCIATION_NOT_SURVIVED")

    def test_exact_half_cluster_rate_fails_strict_survival_boundary(self) -> None:
        self.assertEqual(s4._survival_decision(True, Fraction(1, 1), Fraction(1, 40), Fraction(1, 2)), "PILOT_ASSOCIATION_NOT_SURVIVED")

    def test_p_exact_equal_to_point_one_is_inclusive(self) -> None:
        self.assertEqual(s4._survival_decision(True, Fraction(1, 1), Fraction(1, 10), Fraction(1, 1)), "PILOT_ASSOCIATION_SURVIVED")

    def test_incomplete_primary_forces_invalid_survival_status(self) -> None:
        self.assertEqual(s4._survival_decision(False, Fraction(1, 1), Fraction(0, 1), Fraction(1, 1)), "PRIMARY_EVALUATION_INVALID_DATA_INCOMPLETE")

    def test_result_hash_is_deterministic(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        left = s4.build_result(self.study, self._interval_results(actual_hits=hits))
        right = s4.build_result(self.study, self._interval_results(actual_hits=hits))
        self.assertEqual(left["resultHash"], right["resultHash"])
        self.assertEqual(left["resultHash"], s4.result_hash(left))

    def test_parsed_capture_hash_mismatch_rejected_before_jsonl_parse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            capture = root / "capture.jsonl"
            capture.write_bytes(b"not parsed because hash is wrong")
            row = {"logicalParsedCaptureName": capture.name, "parsedTicksSha256": "0" * 64}
            with self.assertRaises(s4.S4EvaluationError) as raised:
                s4._verify_all_capture_hashes({capture.name: capture}, [row])
            self.assertEqual(raised.exception.code, "PARSED_CAPTURE_HASH_MISMATCH")

    def test_all_parsed_capture_hashes_precede_any_jsonl_parse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            project = base / "repo"
            parsed = base / "private" / "mo_r4a_s4_a1" / "parsed"
            project.mkdir()
            parsed.mkdir(parents=True)
            records = []
            for item in self.study.manifest_records:
                name = item["logicalParsedCaptureName"]
                (parsed / name).write_bytes(b"synthetic hash mismatch; never parse")
                records.append({**item, "parsedTicksSha256": "0" * 64})
            study = replace(self.study, manifest_records=tuple(records))
            with patch.object(s4, "_parse_tick_line") as parser:
                with self.assertRaises(s4.S4EvaluationError) as raised:
                    s4.evaluate_interval_streams(study, parsed, project)
            self.assertEqual(raised.exception.code, "PARSED_CAPTURE_HASH_MISMATCH")
            parser.assert_not_called()

    def test_parsed_record_count_must_match_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            project = base / "repo"
            parsed = base / "private" / "mo_r4a_s4_a1" / "parsed"
            project.mkdir()
            parsed.mkdir(parents=True)
            empty_hash = s4._sha256(b"")
            records = []
            for item in self.study.manifest_records:
                name = item["logicalParsedCaptureName"]
                (parsed / name).write_bytes(b"")
                records.append({**item, "parsedTicksSha256": empty_hash, "parsedRecordCount": 1})
            study = replace(self.study, manifest_records=tuple(records))
            with self.assertRaises(s4.S4EvaluationError) as raised:
                s4.evaluate_interval_streams(study, parsed, project)
            self.assertEqual(raised.exception.code, "PARSED_RECORD_COUNT_MISMATCH")

    def test_unexpected_partition_rejected(self) -> None:
        plan = {"providerPartitionPlanHash": s4.FREEZE_HASHES["partitionPlanHash"], "partitions": list(self.study.partitions)}
        altered = deepcopy(plan)
        altered["partitions"].append(deepcopy(altered["partitions"][0]))
        with self.assertRaises(s4.S4EvaluationError):
            s4._validate_partition_plan(altered, self.study.intervals, s4.FREEZE_HASHES["partitionPlanHash"])

    def test_unlisted_parsed_file_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            project = base / "repo"
            parsed = base / "private" / "mo_r4a_s4_a1" / "parsed"
            project.mkdir()
            parsed.mkdir(parents=True)
            (parsed / "listed.jsonl").write_bytes(b"")
            (parsed / "extra.jsonl").write_bytes(b"")
            record = {"logicalParsedCaptureName": "listed.jsonl"}
            with self.assertRaises(s4.S4EvaluationError) as raised:
                s4._validate_parsed_root(parsed, [record], project)
            self.assertEqual(raised.exception.code, "UNLISTED_OR_MISSING_PARSED_CAPTURE")

    def test_canonical_record_rejects_extra_fields(self) -> None:
        record = {"partitionId": "USDJPY/2030/00/01_ticks.bi5", "recordIndex": 0, "timestampUtc": "2030-01-01T10:00:00.000Z", "askNative": 101, "bidNative": 100, "askVolumeBitsHex": "00000000", "bidVolumeBitsHex": "00000000", "extra": 1}
        with self.assertRaises(s4.S4EvaluationError):
            s4._parse_tick_line(_line(record), "USDJPY/2030/00/01_ticks.bi5", datetime(2030, 1, 1).date(), 0)

    def test_real_capture_entry_point_refuses_unapproved_access_before_root_read(self) -> None:
        with self.assertRaises(s4.S4EvaluationError) as raised:
            s4.evaluate_frozen_captures(PROJECT_ROOT, Path("Z:/not-a-capture-root"))
        self.assertEqual(raised.exception.code, "OUTCOME_ACCESS_NOT_AUTHORIZED")

    def test_evaluator_has_no_provider_network_or_raw_decoder_imports(self) -> None:
        tree = ast.parse(Path(s4.__file__).read_text(encoding="utf-8"))
        imports = set()
        calls = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
        prohibited = {"boto3", "botocore", "requests", "httpx", "urllib", "socket", "ftplib", "s3fs", "lzma", "struct"}
        self.assertFalse(imports & prohibited)
        self.assertNotIn("parse_daily_bi5", calls)

    def test_result_schema_rejects_missing_and_extra_top_level_fields(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4.build_result(self.study, self._interval_results(actual_hits=hits))
        missing = deepcopy(result)
        missing.pop("primary")
        with self.assertRaises(s4.S4EvaluationError):
            s4.validate_result_schema(missing)
        extra = deepcopy(result)
        extra["unregisteredField"] = True
        with self.assertRaises(s4.S4EvaluationError):
            s4.validate_result_schema(extra)

    def test_result_hash_and_execution_locks_are_validated(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4.build_result(self.study, self._interval_results(actual_hits=hits))
        bad_hash = deepcopy(result)
        bad_hash["resultHash"] = "0" * 64
        with self.assertRaises(s4.S4EvaluationError) as raised_hash:
            s4.validate_result_schema(bad_hash)
        self.assertEqual(raised_hash.exception.code, "RESULT_HASH_MISMATCH")
        unlocked = deepcopy(result)
        unlocked["executionFlags"]["executionAllowed"] = True
        with self.assertRaises(s4.S4EvaluationError) as raised_lock:
            s4.validate_result_schema(unlocked)
        self.assertEqual(raised_lock.exception.code, "RESULT_EXECUTION_LOCK_INVALID")

    def test_result_schema_rejects_missing_and_extra_nested_fields(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        result = s4.build_result(self.study, self._interval_results(actual_hits=hits))
        missing = deepcopy(result)
        missing["primary"].pop("denominator")
        with self.assertRaises(s4.S4EvaluationError):
            s4.validate_result_schema(missing)
        extra = deepcopy(result)
        extra["executionFlags"]["polarity"] = False
        with self.assertRaises(s4.S4EvaluationError):
            s4.validate_result_schema(extra)

    def test_sampled_return_hits_must_match_expected_direction(self) -> None:
        hits = {event["eventId"]: 1 for event in self.study.primary_events}
        rows = self._interval_results(actual_hits=hits)
        rows[0]["hit"] = 0
        with self.assertRaises(s4.S4EvaluationError) as raised:
            s4.build_result(self.study, rows)
        self.assertEqual(raised.exception.code, "EVALUATION_HIT_RETURN_MISMATCH")

    def test_parsed_tick_line_requires_exact_canonical_millisecond_timestamp(self) -> None:
        record = {"partitionId": "USDJPY/2030/00/01_ticks.bi5", "recordIndex": 0, "timestampUtc": "2030-01-01T10:00:00Z", "askNative": 101, "bidNative": 100, "askVolumeBitsHex": "00000000", "bidVolumeBitsHex": "00000000"}
        with self.assertRaises(s4.S4EvaluationError) as raised:
            s4._parse_tick_line(_line(record), "USDJPY/2030/00/01_ticks.bi5", datetime(2030, 1, 1).date(), 0)
        self.assertEqual(raised.exception.code, "DATA_TIMESTAMP_INVALID")


if __name__ == "__main__":
    unittest.main()
