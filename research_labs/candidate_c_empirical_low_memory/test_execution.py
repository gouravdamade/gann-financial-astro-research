"""Synthetic-only old/new equivalence tests for the low-memory EMP2 executor."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from research_labs.candidate_c_empirical import execution as historical_execution
from research_labs.candidate_c_empirical.canonical import self_hash
from research_labs.candidate_c_empirical.market_contract import validate_market_admission_record, validate_market_snapshot
from research_labs.candidate_c_empirical.runtime import R3_R1_PATHS

from .execution import (
    LowMemoryExecutionError,
    _execute_low_memory_with_verified_inputs_for_test,
    execute_emp2_low_memory_once,
)
from .market_stream import StreamingQuote
from .runtime import verify_emp2_r1_r1_low_memory_runtime


ROOT = Path(__file__).resolve().parents[2]
TOKEN_A = '"SYNTHETIC_A"'
TOKEN_B = '"SYNTHETIC_B"'


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _hash(document: dict[str, Any], field: str) -> dict[str, Any]:
    document[field] = self_hash(document, field)
    return document


def _ledger_pairs() -> list[tuple[str, str]]:
    ledger = json.loads((ROOT / R3_R1_PATHS["ledger"]).read_text(encoding="utf-8"))
    return sorted({(entry["sideIdentity"], entry["canonicalRowSlotId"]) for entry in ledger["entries"]})


def _synthetic_runtime(*, per_state: int, zero_variance: bool = False) -> SimpleNamespace:
    records: list[dict[str, Any]] = []
    start = datetime(2025, 5, 1, 2, 0, tzinfo=timezone.utc)
    cells = []
    for pair_index, (side, slot) in enumerate(_ledger_pairs()):
        cells.append({"sideIdentity": side, "canonicalRowSlotId": slot, "sourceTestable": True, "eligibleValueStates": [{"stateTokenCanonicalJson": TOKEN_A}, {"stateTokenCanonicalJson": TOKEN_B}]})
        for token_index, token in enumerate((TOKEN_A, TOKEN_B)):
            for ordinal in range(per_state):
                sequence = len(records)
                records.append({
                    "eventId": f"SYNTHETIC-{pair_index}-{token_index}-{ordinal}",
                    "sideIdentity": side,
                    "canonicalRowSlotId": slot,
                    "stateTokenCanonicalJson": token,
                    "exactUtc": _utc(start + timedelta(seconds=sequence)),
                    "syntheticOutcomeClass": "FLAT" if zero_variance else token,
                })
    frozen = SimpleNamespace(
        acceptance_record_hash="A" * 64,
        analysis_manifest_hash="B" * 64,
        preregistration_hash="C" * 64,
        temporal_null_contract_hash="D" * 64,
        execution_contract_hash="E" * 64,
        test_ledger_contract_hash="F" * 64,
        result_schema_hash="0" * 64,
        canonical_source_state_snapshot_hash="1" * 64,
        source_state_eligibility_hash="2" * 64,
        market_snapshot_schema_hash="3" * 64,
        market_data_admission_contract_hash="4" * 64,
        market_admission_record_contract_hash="5" * 64,
        source_snapshot={"sourceStateRecords": records},
        source_eligibility={"cells": cells},
    )
    return SimpleNamespace(frozen_runtime=frozen)


def _quotes(runtime: SimpleNamespace, *, omit_p0: bool = False, omit_ph: bool = False) -> list[dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {
        "2025-05-01T01:58:38.000Z": {"timestampUtc": "2025-05-01T01:58:38.000Z", "bid": 150.0, "ask": 150.02},
        "2025-08-01T23:20:56.000Z": {"timestampUtc": "2025-08-01T23:20:56.000Z", "bid": 150.0, "ask": 150.02},
    }
    for record in runtime.frozen_runtime.source_snapshot["sourceStateRecords"]:
        event = datetime.fromisoformat(record["exactUtc"].replace("Z", "+00:00"))
        if not omit_p0:
            quotes[_utc(event)] = {"timestampUtc": _utc(event), "bid": 150.0, "ask": 150.02}
        for horizon in (3600, 21600, 86400):
            if omit_ph:
                continue
            value = 150.0 if record["syntheticOutcomeClass"] == "FLAT" else (151.0 if record["stateTokenCanonicalJson"] == TOKEN_A else 149.0)
            at = _utc(event + timedelta(seconds=horizon))
            quotes[at] = {"timestampUtc": at, "bid": value, "ask": value + 0.02}
    return sorted(quotes.values(), key=lambda item: item["timestampUtc"])


def _market_records(quotes: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], Any, Any]:
    snapshot = {
        "providerId": "SYNTHETIC_MARKET_PROVIDER", "datasetId": "SYNTHETIC_MARKET_DATASET", "instrumentId": "FX_SPOT_USDJPY",
        "timezone": "UTC", "resolutionSeconds": 1, "coverageStartUtc": "2025-05-01T01:58:38Z",
        "coverageEndUtc": "2025-08-01T23:20:56Z", "rawArtifactHashes": {"SYNTHETIC": "A" * 64},
        "quoteCount": len(quotes), "quotes": quotes, "marketSnapshotHash": None,
    }
    _hash(snapshot, "marketSnapshotHash")
    validated_snapshot = validate_market_snapshot(snapshot)
    admission = {
        "schemaVersion": "SYNTHETIC_ADMISSION_V1", "admissionId": "SYNTHETIC_ADMISSION", "admitted": True,
        "marketSnapshotHash": validated_snapshot.market_snapshot_hash, "providerId": validated_snapshot.provider_id,
        "datasetId": validated_snapshot.dataset_id, "instrumentId": validated_snapshot.instrument_id,
        "coverageStartUtc": validated_snapshot.coverage_start_utc, "coverageEndUtc": validated_snapshot.coverage_end_utc,
        "resolutionSeconds": validated_snapshot.resolution_seconds, "rawArtifactHashes": dict(validated_snapshot.raw_artifact_hashes),
        "emp0R3R1MarketSnapshotSchemaHash": "3" * 64, "emp0R3R1MarketDataAdmissionContractHash": "4" * 64,
        "admissionRecordHash": None,
    }
    _hash(admission, "admissionRecordHash")
    validated_admission = validate_market_admission_record(admission, validated_snapshot, expected_snapshot_schema_hash="3" * 64, expected_market_data_admission_contract_hash="4" * 64)
    stream_snapshot = SimpleNamespace(
        market_snapshot_hash=validated_snapshot.market_snapshot_hash, provider_id=validated_snapshot.provider_id,
        dataset_id=validated_snapshot.dataset_id, instrument_id=validated_snapshot.instrument_id,
        coverage_start_utc=validated_snapshot.coverage_start_utc, coverage_end_utc=validated_snapshot.coverage_end_utc,
        resolution_seconds=validated_snapshot.resolution_seconds, raw_artifact_hashes=validated_snapshot.raw_artifact_hashes,
    )
    return snapshot, admission, stream_snapshot, validated_admission


def _stream(quotes: list[dict[str, Any]]) -> list[StreamingQuote]:
    return [StreamingQuote(str(item["timestampUtc"]), float(item["bid"]), float(item["ask"])) for item in quotes]


def _equivalent_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runtime: SimpleNamespace, quotes: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    snapshot, admission, stream_snapshot, validated_admission = _market_records(quotes)
    authorization = SimpleNamespace(authorization_id="SYNTHETIC_AUTH", authorization_record_hash="6" * 64)
    monkeypatch.setattr(historical_execution, "verify_emp0_r3_r1_runtime", lambda root: runtime.frozen_runtime)
    monkeypatch.setattr(historical_execution, "validate_empirical_authorization_for_runtime", lambda *args: authorization)
    old = historical_execution._execute_emp2_once_to_root_for_test(ROOT, snapshot, admission, {"synthetic": True}, tmp_path / "old")
    new = _execute_low_memory_with_verified_inputs_for_test(
        ROOT, runtime, stream_snapshot, validated_admission, authorization, lambda: _stream(quotes), tmp_path / "new",
    )
    return old, new


def _assert_semantic_equivalence(old: dict[str, Any], new: dict[str, Any]) -> None:
    assert old == new
    assert len(old["testLedger"]) == len(new["testLedger"]) == 24
    for field in (
        "testId", "sideIdentity", "canonicalRowSlotId", "horizonSeconds", "horizonRole", "sourceEligibleStateCount",
        "sourceEligibleEventCount", "sourceEligibleStates", "marketReturnAvailableCount", "marketUnavailableCount",
        "perStateSourceCount", "perStateMarketAdmissibleCount", "retainedMarketEligibleStates",
        "retainedMarketEligibleEventCount", "status", "statistic", "pRaw", "pAdjusted", "multiplicityMethod", "familyId",
    ):
        assert [row.get(field) for row in old["testLedger"]] == [row.get(field) for row in new["testLedger"]]
    assert old["primaryFamily"] == new["primaryFamily"]
    assert old["secondaryFamily"] == new["secondaryFamily"]


def test_public_successor_signature_has_only_frozen_production_inputs() -> None:
    assert tuple(inspect.signature(execute_emp2_low_memory_once).parameters) == (
        "repo_root", "private_raw_dir", "market_admission_record", "authorization_record",
    )


def test_successor_runtime_binds_accepted_market_layer_and_frozen_parser() -> None:
    runtime = verify_emp2_r1_r1_low_memory_runtime(ROOT)
    assert runtime.successor_manifest_hash
    assert runtime.successor_runtime_contract_hash
    assert runtime.parser_hash == "F3D49AFBC055D9C1CF2E513194C9A98C8D55769FF974343B99A4D00EE4A35BC8"


def test_synthetic_full_24_row_old_new_equivalence_uses_real_permutation_and_multiplicity(tmp_path, monkeypatch) -> None:
    runtime = _synthetic_runtime(per_state=30)
    old, new = _equivalent_results(tmp_path, monkeypatch, runtime, _quotes(runtime))
    _assert_semantic_equivalence(old, new)
    assert old["primaryFamily"]["executedTestCount"] == 8
    assert old["secondaryFamily"]["executedTestCount"] == 16
    assert {row["status"] for row in old["testLedger"]} == {"EXECUTED"}


@pytest.mark.parametrize(
    ("per_state", "zero_variance", "omit_p0", "omit_ph", "expected_status"),
    [
        (20, False, True, False, "MARKET_QUOTE_UNAVAILABLE_FOR_ALL_ELIGIBLE_STATES"),
        (20, False, False, True, "MARKET_QUOTE_UNAVAILABLE_FOR_ALL_ELIGIBLE_STATES"),
        (19, False, False, False, "INSUFFICIENT_MARKET_ELIGIBLE_SAMPLE"),
        (30, True, False, False, "ZERO_OUTCOME_VARIANCE_NOT_TESTABLE"),
    ],
)
def test_synthetic_edge_statuses_match_historical_executor(tmp_path, monkeypatch, per_state, zero_variance, omit_p0, omit_ph, expected_status) -> None:
    runtime = _synthetic_runtime(per_state=per_state, zero_variance=zero_variance)
    old, new = _equivalent_results(tmp_path, monkeypatch, runtime, _quotes(runtime, omit_p0=omit_p0, omit_ph=omit_ph))
    _assert_semantic_equivalence(old, new)
    assert {row["status"] for row in old["testLedger"]} == {expected_status}


def test_successor_rejects_existing_canonical_result_before_market_or_source_work(tmp_path, monkeypatch) -> None:
    target = tmp_path / "status/research/mo_r4a_candidate_c_emp2_market_association_result_v1.json"
    target.parent.mkdir(parents=True)
    target.write_text("{}", encoding="utf-8")
    with pytest.raises(LowMemoryExecutionError, match="EMPIRICAL_FIRST_RESULT_ALREADY_EXISTS"):
        execute_emp2_low_memory_once(tmp_path, tmp_path, {}, {})
