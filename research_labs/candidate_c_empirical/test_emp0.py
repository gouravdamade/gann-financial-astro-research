"""Synthetic-only EMP0-R2 integrity, authorization, and test-cell regression."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from math import isclose, log
from pathlib import Path

import pytest

from .canonical import self_hash
from .market_contract import MarketContractError, validate_market_admission_record, validate_market_snapshot
from .multiplicity import benjamini_hochberg, holm_bonferroni
from .returns import extract_forward_log_return
from .statistics import ALLOWED_HORIZON_SECONDS, StatisticalContractError, circular_shifted_observations, deterministic_monthly_offsets, deterministic_permutation_test, market_eligible_testable


ROOT = Path(__file__).resolve().parents[2]
RAW_HASH = "A" * 64
SCHEMA_HASH = "B" * 64
CONTRACT_HASH = "C" * 64


def self_hashed(document: dict, field: str) -> dict:
    document[field] = self_hash(document, field)
    return document


def quote(timestamp: str, bid: float = 150.0, ask: float = 150.2) -> dict:
    return {"timestampUtc": timestamp, "bid": bid, "ask": ask}


def synthetic_snapshot(quotes: list[dict] | None = None) -> dict:
    snapshot = {
        "providerId": "SYNTHETIC_PROVIDER_IDENTITY",
        "datasetId": "SYNTHETIC_IMMUTABLE_DATASET",
        "instrumentId": "FX_SPOT_USDJPY",
        "timezone": "UTC",
        "resolutionSeconds": 60,
        "coverageStartUtc": "2025-05-01T01:58:38Z",
        "coverageEndUtc": "2025-08-01T23:20:56Z",
        "rawArtifactHashes": {"synthetic.raw": RAW_HASH},
        "quotes": quotes or [quote("2025-05-01T01:58:38Z"), quote("2025-08-01T23:20:56Z", 151.0, 151.2)],
    }
    snapshot["quoteCount"] = len(snapshot["quotes"])
    return self_hashed(snapshot, "marketSnapshotHash")


def observations(*, side: str = "USD", slot: str = "C02", horizon: int | None = 86400) -> list[dict]:
    rows = []
    for index, (state, result) in enumerate((("A", 0.0), ("A", 0.0), ("B", 2.0), ("B", 2.0))):
        row = {"eventId": f"SYNTHETIC_EVENT_{index}", "sideIdentity": side, "canonicalRowSlotId": slot, "exactUtc": f"2025-05-{index + 1:02d}T00:00:00Z", "stateTokenCanonicalJson": state, "logReturn": result}
        if horizon is not None:
            row["horizonSeconds"] = horizon
        rows.append(row)
    return rows


def admission_record(snapshot, schema_hash: str = SCHEMA_HASH, contract_hash: str = CONTRACT_HASH) -> dict:
    record = {
        "schemaVersion": "SYNTHETIC_MARKET_ADMISSION_V1", "admissionId": "SYNTHETIC_ADMISSION", "admitted": True,
        "marketSnapshotHash": snapshot.market_snapshot_hash, "providerId": snapshot.provider_id,
        "datasetId": snapshot.dataset_id, "instrumentId": snapshot.instrument_id,
        "coverageStartUtc": snapshot.coverage_start_utc, "coverageEndUtc": snapshot.coverage_end_utc,
        "resolutionSeconds": snapshot.resolution_seconds, "rawArtifactHashes": dict(snapshot.raw_artifact_hashes),
        "emp0R3R1MarketSnapshotSchemaHash": schema_hash, "emp0R3R1MarketDataAdmissionContractHash": contract_hash,
    }
    return self_hashed(record, "admissionRecordHash")


def test_historical_source_snapshot_and_eligibility_remain_frozen():
    snapshot = json.loads((ROOT / "status/research/mo_r4a_candidate_c_emp0_canonical_source_state_snapshot_v1.json").read_text())
    eligibility = json.loads((ROOT / "status/research/mo_r4a_candidate_c_emp0_source_state_eligibility_v1.json").read_text())
    assert snapshot["canonicalSourceStateSnapshotHash"] == "9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284"
    assert snapshot["populationEventCount"] == 645 and snapshot["canonicalSourceStateRowCount"] == 5160
    assert eligibility["sourceStateEligibilityHash"] == "ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1"
    assert len(eligibility["cells"]) == 16 and sum(cell["sourceTestable"] for cell in eligibility["cells"]) == 8


@pytest.mark.parametrize("field", ["providerId", "datasetId", "instrumentId", "timezone", "resolutionSeconds", "coverageStartUtc", "coverageEndUtc", "rawArtifactHashes", "quoteCount", "quotes", "marketSnapshotHash"])
def test_snapshot_required_fields_and_self_hash_are_executable(field):
    snapshot = synthetic_snapshot()
    if field == "marketSnapshotHash":
        snapshot.pop(field)
    else:
        snapshot.pop(field)
        snapshot["marketSnapshotHash"] = self_hash(snapshot, "marketSnapshotHash")
    with pytest.raises(MarketContractError):
        validate_market_snapshot(snapshot)


@pytest.mark.parametrize("mutation", [
    lambda value: value["quotes"][0].update(bid=149.0),
    lambda value: value.update(providerId="MUTATED_PROVIDER"),
    lambda value: value["rawArtifactHashes"].update({"synthetic.raw": "F" * 64}),
])
def test_snapshot_hash_covers_all_provenance_and_quote_content(mutation):
    snapshot = synthetic_snapshot()
    mutation(snapshot)
    with pytest.raises(MarketContractError, match="marketSnapshotHash mismatch"):
        validate_market_snapshot(snapshot)


def test_snapshot_coverage_count_hashes_and_input_immutability():
    snapshot = synthetic_snapshot([quote("2025-05-01T01:58:38Z"), quote("2025-05-01T01:58:38Z"), quote("2025-08-01T23:20:56Z")])
    original = deepcopy(snapshot)
    validated = validate_market_snapshot(snapshot)
    assert snapshot == original and validated.raw_quote_count == 3 and validated.admitted_quote_count == 2
    for field, value in (("coverageStartUtc", "2025-05-01T01:58:39Z"), ("coverageEndUtc", "2025-08-01T23:20:55Z"), ("quoteCount", 1)):
        invalid = deepcopy(snapshot)
        invalid[field] = value
        invalid["marketSnapshotHash"] = self_hash(invalid, "marketSnapshotHash")
        with pytest.raises(MarketContractError):
            validate_market_snapshot(invalid)
    for raw_hashes in ({}, {"": RAW_HASH}, {"a": "a" * 64}, {"a": "Z" * 64}):
        invalid = deepcopy(snapshot)
        invalid["rawArtifactHashes"] = raw_hashes
        invalid["marketSnapshotHash"] = self_hash(invalid, "marketSnapshotHash")
        with pytest.raises(MarketContractError):
            validate_market_snapshot(invalid)


def test_snapshot_rejects_outside_coverage_and_bad_coverage_order():
    invalid = synthetic_snapshot([quote("2025-05-01T01:58:37Z")])
    with pytest.raises(MarketContractError):
        validate_market_snapshot(invalid)
    invalid = synthetic_snapshot()
    invalid["coverageStartUtc"] = "2025-05-01T01:58:38+00:00"
    invalid["marketSnapshotHash"] = self_hash(invalid, "marketSnapshotHash")
    with pytest.raises(MarketContractError):
        validate_market_snapshot(invalid)
    invalid = synthetic_snapshot()
    invalid["coverageStartUtc"], invalid["coverageEndUtc"] = invalid["coverageEndUtc"], invalid["coverageStartUtc"]
    invalid["marketSnapshotHash"] = self_hash(invalid, "marketSnapshotHash")
    with pytest.raises(MarketContractError):
        validate_market_snapshot(invalid)


def test_admission_record_binds_exact_validated_snapshot_and_contracts():
    snapshot = validate_market_snapshot(synthetic_snapshot())
    record = admission_record(snapshot)
    validated = validate_market_admission_record(record, snapshot, expected_snapshot_schema_hash=SCHEMA_HASH, expected_market_data_admission_contract_hash=CONTRACT_HASH)
    assert validated.market_snapshot_hash == snapshot.market_snapshot_hash
    for field, value in (("marketSnapshotHash", "F" * 64), ("providerId", "OTHER"), ("rawArtifactHashes", {"synthetic.raw": "F" * 64}), ("emp0R3R1MarketSnapshotSchemaHash", "G" * 64)):
        invalid = deepcopy(record)
        invalid[field] = value
        invalid["admissionRecordHash"] = self_hash(invalid, "admissionRecordHash")
        with pytest.raises(MarketContractError):
            validate_market_admission_record(invalid, snapshot, expected_snapshot_schema_hash=SCHEMA_HASH, expected_market_data_admission_contract_hash=CONTRACT_HASH)
    invalid = deepcopy(record)
    invalid["providerId"] = "MUTATED_WITHOUT_REHASH"
    with pytest.raises(MarketContractError, match="admissionRecordHash mismatch"):
        validate_market_admission_record(invalid, snapshot, expected_snapshot_schema_hash=SCHEMA_HASH, expected_market_data_admission_contract_hash=CONTRACT_HASH)


def test_test_cell_and_horizon_contracts_reject_cross_hypothesis_inputs():
    rows = observations()
    tokens = {"A", "B"}
    assert set(ALLOWED_HORIZON_SECONDS) == {3600, 21600, 86400}
    for horizon in sorted(ALLOWED_HORIZON_SECONDS):
        adapted = [{**row, "horizonSeconds": horizon} for row in rows]
        assert deterministic_permutation_test(adapted, horizon, tokens)["permutationCount"] == 4999
    with pytest.raises(StatisticalContractError, match="UNREGISTERED_HORIZON"):
        deterministic_permutation_test(rows, 7200, tokens)
    mixed_side = rows + [{**rows[0], "eventId": "J", "sideIdentity": "JPY"}]
    with pytest.raises(StatisticalContractError, match="MIXED_OR_INVALID_SIDE"):
        deterministic_permutation_test(mixed_side, 86400, tokens)
    mixed_slot = rows + [{**rows[0], "eventId": "C03", "canonicalRowSlotId": "C03"}]
    with pytest.raises(StatisticalContractError, match="MIXED_ROW_SLOT"):
        deterministic_permutation_test(mixed_slot, 86400, tokens)


def test_temporal_null_zero_month_global_identity_bound_and_determinism():
    rows = observations()
    rows += [{**row, "eventId": f"JUNE_{index}", "exactUtc": f"2025-06-{index + 1:02d}T00:00:00Z"} for index, row in enumerate(observations())]
    offsets = deterministic_monthly_offsets(rows, 86400, 1)
    assert any(value != 0 for value in offsets.values())
    calls = []
    def resolver(*args):
        calls.append(args[-1])
        return 0 if args[-1] == 0 else (1 if args[3] == "2025-05" else 0)
    offsets = deterministic_monthly_offsets(rows, 86400, 2, offset_resolver=resolver)
    assert offsets[("USD", "2025-05")] == 1 and offsets[("USD", "2025-06")] == 0
    assert calls[:2] == [0, 0] and calls[2:] == [1, 1]
    with pytest.raises(StatisticalContractError, match="TEMPORAL_NULL_GENERATION_FAILURE"):
        deterministic_monthly_offsets(rows, 86400, 3, offset_resolver=lambda *_: 0, max_attempts=3)
    with pytest.raises(StatisticalContractError, match="NO_NONTRIVIAL_TEMPORAL_SHIFT_AVAILABLE"):
        deterministic_monthly_offsets([observations()[0]], 86400, 1)
    first = deterministic_permutation_test(rows, 86400, {"A", "B"})
    second = deterministic_permutation_test(rows, 86400, {"A", "B"})
    assert first["nullStatistics"] == second["nullStatistics"] and isclose(first["pRaw"] * 5000, round(first["pRaw"] * 5000))
    shifted = circular_shifted_observations(rows, 86400, {"A", "B"}, 1)
    assert {row["eventId"]: row["logReturn"] for row in shifted} == {row["eventId"]: row["logReturn"] for row in rows}
    assert Counter(row["stateTokenCanonicalJson"] for row in shifted if row["exactUtc"].startswith("2025-05")) == Counter(row["stateTokenCanonicalJson"] for row in rows if row["exactUtc"].startswith("2025-05"))


def test_validated_snapshot_is_deeply_immutable():
    validated = validate_market_snapshot(synthetic_snapshot())
    with pytest.raises((AttributeError, TypeError)):
        validated.quotes[0].bid = 149.0
    with pytest.raises(TypeError):
        validated.raw_artifact_hashes[0] = ("other", "B" * 64)


def test_return_and_multiplicity_contracts_remain_unchanged():
    quotes = validate_market_snapshot(synthetic_snapshot([quote("2025-05-01T01:58:38Z", 99, 101), quote("2025-05-01T02:58:38Z", 110, 112)])).quotes
    result = extract_forward_log_return("2025-05-01T01:58:38Z", 3600, quotes)
    assert isclose(result["logReturn"], log(111 / 100))
    assert holm_bonferroni({"a": 0.01, "b": 0.04, "c": 0.04}) == {"a": 0.03, "b": 0.08, "c": 0.08}
    assert benjamini_hochberg({"a": 0.01, "b": 0.04, "c": 0.04}) == {"a": 0.03, "b": 0.04, "c": 0.04}
    assert market_eligible_testable(observations() * 20, {"A", "B"})
