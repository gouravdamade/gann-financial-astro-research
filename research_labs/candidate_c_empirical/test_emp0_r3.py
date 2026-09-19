"""Synthetic-only EMP0-R3 runtime and future EMP2 execution regression."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from .artifact import RESULT_RELATIVE_PATH, verify_result
from .canonical import self_hash
from .execution import EmpiricalExecutionError, _eligibility_map, _execute_emp2_once_to_root_for_test, execute_emp2_once
from .market_contract import FrozenMarketQuote, validate_market_snapshot
from .runtime import validate_empirical_authorization_for_runtime, verify_emp0_r3_r1_runtime


ROOT = Path(__file__).resolve().parents[2]


def _hashed(document: dict[str, Any], field: str) -> dict[str, Any]:
    document[field] = self_hash(document, field)
    return document


def _synthetic_snapshot() -> dict[str, Any]:
    runtime = verify_emp0_r3_r1_runtime(ROOT)
    eligibility = _eligibility_map(runtime.source_eligibility)
    target_side, target_slot = "USD", next(slot for side, slot in eligibility if side == "USD")
    target_tokens = set(eligibility[(target_side, target_slot)])
    selected = [record for record in runtime.source_snapshot["sourceStateRecords"] if record["sideIdentity"] == target_side and record["canonicalRowSlotId"] == target_slot and record.get("stateTokenCanonicalJson") in target_tokens]
    per_token: dict[str, int] = {token: 0 for token in target_tokens}
    quotes: dict[str, dict[str, Any]] = {}
    for record in selected:
        token = record["stateTokenCanonicalJson"]
        if per_token[token] >= 30:
            continue
        per_token[token] += 1
        quotes.setdefault(record["exactUtc"], {"timestampUtc": record["exactUtc"], "bid": 150.0, "ask": 150.2})
        for horizon in (3600, 21600, 86400):
            from .market_contract import parse_utc
            timestamp = (parse_utc(record["exactUtc"]) + __import__("datetime").timedelta(seconds=horizon)).isoformat().replace("+00:00", "Z")
            quotes.setdefault(timestamp, {"timestampUtc": timestamp, "bid": 150.6, "ask": 150.8})
    quotes.setdefault("2025-05-01T01:58:38Z", {"timestampUtc": "2025-05-01T01:58:38Z", "bid": 150.0, "ask": 150.2})
    quotes.setdefault("2025-08-01T23:20:56Z", {"timestampUtc": "2025-08-01T23:20:56Z", "bid": 150.6, "ask": 150.8})
    snapshot = {"providerId": "SYNTHETIC_MARKET_PROVIDER", "datasetId": "SYNTHETIC_MARKET_DATASET", "instrumentId": "FX_SPOT_USDJPY", "timezone": "UTC", "resolutionSeconds": 60, "coverageStartUtc": "2025-05-01T01:58:38Z", "coverageEndUtc": "2025-08-01T23:20:56Z", "rawArtifactHashes": {"synthetic-market.json": "A" * 64}, "quotes": sorted(quotes.values(), key=lambda item: item["timestampUtc"])}
    snapshot["quoteCount"] = len(snapshot["quotes"])
    return _hashed(snapshot, "marketSnapshotHash")


def _admission(snapshot: dict[str, Any]) -> dict[str, Any]:
    runtime = verify_emp0_r3_r1_runtime(ROOT)
    validated = validate_market_snapshot(snapshot)
    return _hashed({"schemaVersion": "SYNTHETIC_EMP0_R3_R1_ADMISSION_V1", "admissionId": "SYNTHETIC_EMP0_R3_R1_ADMISSION", "admitted": True, "marketSnapshotHash": validated.market_snapshot_hash, "providerId": validated.provider_id, "datasetId": validated.dataset_id, "instrumentId": validated.instrument_id, "coverageStartUtc": validated.coverage_start_utc, "coverageEndUtc": validated.coverage_end_utc, "resolutionSeconds": validated.resolution_seconds, "rawArtifactHashes": dict(validated.raw_artifact_hashes), "emp0R3R1MarketSnapshotSchemaHash": runtime.market_snapshot_schema_hash, "emp0R3R1MarketDataAdmissionContractHash": runtime.market_data_admission_contract_hash, "admissionRecordHash": None}, "admissionRecordHash")


def _authorization(snapshot: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
    runtime = verify_emp0_r3_r1_runtime(ROOT)
    return _hashed({"schemaVersion": "SYNTHETIC_EMP0_R3_R1_AUTHORIZATION_V1", "authorizationId": "SYNTHETIC_EMP0_R3_R1_ONE_SHOT", "authorized": True, "EMP0R3R1ImplementationCommit": runtime.implementation_commit, "EMP0R3R1AcceptanceRecordHash": runtime.acceptance_record_hash, "EMP0R3R1AnalysisImplementationManifestHash": runtime.analysis_manifest_hash, "EMP0R3R1PreregistrationHash": runtime.preregistration_hash, "EMP0R3R1TemporalNullContractHash": runtime.temporal_null_contract_hash, "EMP0R3R1EmpiricalExecutionContractHash": runtime.execution_contract_hash, "EMP0R3R1ResultSchemaHash": runtime.result_schema_hash, "EMP0R3R1TestLedgerContractHash": runtime.test_ledger_contract_hash, "canonicalSourceStateSnapshotHash": runtime.canonical_source_state_snapshot_hash, "sourceStateEligibilityHash": runtime.source_state_eligibility_hash, "marketSnapshotHash": snapshot["marketSnapshotHash"], "marketAdmissionRecordHash": admission["admissionRecordHash"], "marketSnapshotSchemaHash": runtime.market_snapshot_schema_hash, "marketDataAdmissionContractHash": runtime.market_data_admission_contract_hash, "marketAdmissionRecordContractHash": runtime.market_admission_record_contract_hash, "instrumentId": "FX_SPOT_USDJPY", "allowedHorizonSeconds": [3600, 21600, 86400], "permutationCount": 4999, "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE", "primaryMultiplicity": "HOLM_BONFERRONI", "primaryAlpha": 0.05, "secondaryMultiplicity": "BENJAMINI_HOCHBERG", "secondaryQ": 0.10, "oneShotExecutionIntent": True, "marketOutcomeAccess": True, "providerRequeryAllowed": False, "postHocTuningAllowed": False, "sourceEligibilityChangesAllowed": False, "newHorizonsAllowed": False, "newSourceStatesAllowed": False, "authorizationRecordHash": None}, "authorizationRecordHash")


def test_r3_runtime_verifies_source_shape_and_protected_bytes():
    runtime = verify_emp0_r3_r1_runtime(ROOT)
    assert runtime.canonical_source_state_snapshot_hash == "9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284"
    assert runtime.source_state_eligibility_hash == "ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1"
    assert len(_eligibility_map(runtime.source_eligibility)) == 8


def test_r3_authorization_is_runtime_derived_and_rejects_tampered_binding():
    snapshot = _synthetic_snapshot()
    admission = _admission(snapshot)
    authorization = _authorization(snapshot, admission)
    validated_snapshot = validate_market_snapshot(snapshot)
    from .market_contract import validate_market_admission_record
    runtime = verify_emp0_r3_r1_runtime(ROOT)
    validated_admission = validate_market_admission_record(admission, validated_snapshot, expected_snapshot_schema_hash=runtime.market_snapshot_schema_hash, expected_market_data_admission_contract_hash=runtime.market_data_admission_contract_hash)
    assert validate_empirical_authorization_for_runtime(ROOT, validated_snapshot, validated_admission, authorization).authorization_id.startswith("SYNTHETIC")
    bad = deepcopy(authorization)
    bad["EMP0R3R1ResultSchemaHash"] = "B" * 64
    bad = _hashed(bad, "authorizationRecordHash")
    with pytest.raises(ValueError):
        validate_empirical_authorization_for_runtime(ROOT, validated_snapshot, validated_admission, bad)


def test_r3_public_orchestrator_is_raw_authorization_only_and_freezes_first_result(tmp_path, monkeypatch):
    snapshot = _synthetic_snapshot()
    admission = _admission(snapshot)
    authorization = _authorization(snapshot, admission)
    from . import execution
    monkeypatch.setattr(execution, "deterministic_permutation_test", lambda observations, horizon, tokens: {"status": "PREREGISTERED_STATISTICAL_RESULT", "statistic": 0.25, "pRaw": 0.2, "permutationCount": 4999})
    result = _execute_emp2_once_to_root_for_test(ROOT, snapshot, admission, authorization, tmp_path)
    assert len(result["testLedger"]) == 24
    assert result["primaryFamily"]["executedTestCount"] >= 1
    assert result["secondaryFamily"]["executedTestCount"] >= 1
    assert any(row["status"] == "MARKET_QUOTE_UNAVAILABLE_FOR_ALL_ELIGIBLE_STATES" for row in result["testLedger"])
    verify_result(result)
    assert (tmp_path / RESULT_RELATIVE_PATH).exists()
    with pytest.raises(EmpiricalExecutionError, match="EMPIRICAL_FIRST_RESULT_ALREADY_EXISTS"):
        _execute_emp2_once_to_root_for_test(ROOT, snapshot, admission, authorization, tmp_path)
    with pytest.raises(EmpiricalExecutionError):
        execute_emp2_once(ROOT, snapshot, admission, {"authorized": True})


def test_frozen_market_quote_is_not_a_mapping_or_mutable():
    quote = validate_market_snapshot(_synthetic_snapshot()).quotes[0]
    assert isinstance(quote, FrozenMarketQuote)
    with pytest.raises((AttributeError, TypeError)):
        quote.ask = 0.0
