"""EMP0 source-only and FAKE_MARKET_ regression coverage."""

from __future__ import annotations

from collections import Counter
from math import isclose, log
from pathlib import Path

import pytest

from .market_contract import MarketContractError, validate_fake_market_snapshot, validate_market_snapshot
from .multiplicity import benjamini_hochberg, holm_bonferroni
from .returns import extract_forward_log_return
from .source_state import build_source_state_eligibility, build_source_state_snapshot
from .statistics import PERMUTATION_COUNT, StatisticalContractError, between_state_explained_variance, circular_shifted_observations, deterministic_monthly_offsets, deterministic_permutation_test, market_eligible_testable, run_authorized_market_analysis


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def snapshot():
    return build_source_state_snapshot(ROOT)


@pytest.fixture(scope="module")
def eligibility(snapshot):
    return build_source_state_eligibility(snapshot)


def fake_snapshot(quotes, resolution=60):
    return {"providerId": "FAKE_MARKET_PROVIDER", "datasetId": "FAKE_MARKET_DATASET", "instrumentId": "FX_SPOT_USDJPY", "timezone": "UTC", "resolutionSeconds": resolution, "quotes": quotes}


def synthetic_admitted_snapshot(quotes, resolution=60):
    return {"providerId": "SYNTHETIC_ADMITTED_PROVIDER", "datasetId": "SYNTHETIC_IMMUTABLE_DATASET", "instrumentId": "FX_SPOT_USDJPY", "timezone": "UTC", "resolutionSeconds": resolution, "quotes": quotes}


def quote(timestamp, bid=150.0, ask=150.2):
    return {"timestampUtc": timestamp, "bid": bid, "ask": ask}


def fake_observations(values):
    return [{"eventId": f"FAKE_SOURCE_{index}", "sideIdentity": "USD", "canonicalRowSlotId": "{\\\"componentId\\\":\\\"C01\\\"}", "exactUtc": f"2025-05-{index + 1:02d}T00:00:00Z", "stateTokenCanonicalJson": state, "logReturn": result} for index, (state, result) in enumerate(values)]


def test_source_snapshot_preserves_frozen_population_and_projection(snapshot):
    records = snapshot["sourceStateRecords"]
    assert snapshot["populationEventCount"] == 645
    assert len(records) == 5160
    assert snapshot["rowSlotsPerEvent"] == 8
    assert snapshot["aBSemanticProjectionAgreement"] is True
    assert len({record["eventId"] for record in records}) == 645
    assert len({(record["eventId"], record["canonicalRowSlotId"]) for record in records}) == 5160


def test_source_states_keep_slots_sides_values_and_abstention(snapshot):
    records = snapshot["sourceStateRecords"]
    slots = {record["canonicalRowSlotId"] for record in records}
    assert len(slots) == 8
    assert {record["sideIdentity"] for record in records} == {"USD", "JPY"}
    assert all(set(record["rowSlot"]) == {"sourceProfile", "componentId", "sourceContractId", "operatorId"} for record in records)
    assert all("aspectType" not in record for record in records)
    values = [record for record in records if record["outputStatus"] == "VALUE"]
    unknowns = [record for record in records if record["outputStatus"] == "UNKNOWN"]
    assert all(set(record["stateToken"]) == {"outputStatus", "sourceValue"} for record in values)
    assert all(record["inferentialDisposition"] == "VALUE_STATE_CANDIDATE" for record in values)
    assert all(record["inferentialDisposition"] == "SOURCE_UNKNOWN_ABSTAIN" and "stateToken" not in record for record in unknowns)


def test_eligibility_is_source_only_and_rare_states_are_not_merged(eligibility):
    assert eligibility["minStateCount"] == 20
    assert eligibility["minTotalTestCount"] == 60
    assert eligibility["unknownDisposition"] == "SOURCE_UNKNOWN_ABSTAIN"
    assert len(eligibility["cells"]) == 16
    for cell in eligibility["cells"]:
        assert all(item["count"] < 20 and item["disposition"] == "RARE_VALUE_STATE_DESCRIPTIVE_ONLY" for item in cell["rareValueStates"])
        assert all(item["count"] >= 20 for item in cell["eligibleValueStates"])
        assert cell["unknownCount"] == sum(cell["unknownReasonCounts"].values())
    c07 = [cell for cell in eligibility["cells"] if cell["rowSlot"]["componentId"] == "C07_INDIVIDUAL_SOURCE_RECORDS_NO_STACKING"]
    assert c07 and all(not cell["sourceTestable"] and cell["nonTestableReason"] == "NOT_EMPIRICALLY_TESTABLE_SOURCE_ABSTENTION" for cell in c07)


def test_protected_drsti_alias_contract_is_preserved(snapshot):
    ordinary = [record for record in snapshot["sourceStateRecords"] if record["operatorId"] == "SARAVALI_4_32_ORDINARY_DRSTI_V1" and record["outputStatus"] == "VALUE"]
    assert ordinary
    values = {record["sourceValue"] for record in ordinary}
    assert {"1/4", "1/2", "3/4", "FULL"} <= values
    assert not values.intersection({"DRSTI_1_4", "DRSTI_1_2", "DRSTI_3_4", "DRSTI_FULL"})


def test_valid_fake_bid_ask_and_duplicate_deduplication_passes():
    quotes = validate_fake_market_snapshot(fake_snapshot([quote("2025-05-01T00:00:00Z"), quote("2025-05-01T00:00:00Z"), quote("2025-05-01T00:01:00Z")]))
    assert len(quotes) == 2


def test_provider_neutral_core_accepts_a_future_admitted_identity_without_provider_access():
    quotes = validate_market_snapshot(synthetic_admitted_snapshot([quote("2025-05-01T00:00:00Z")]))
    assert quotes == [{"timestampUtc": "2025-05-01T00:00:00Z", "bid": 150.0, "ask": 150.2}]
    with pytest.raises(MarketContractError):
        validate_fake_market_snapshot(synthetic_admitted_snapshot([]))


@pytest.mark.parametrize("quotes", [[quote("2025-05-01T00:00:00Z", 151, 150)], [quote("2025-05-01T00:00:00Z", 0, 150)], [quote("2025-05-01T00:00:00+05:30")], [quote("2025-05-01T00:00:00Z"), quote("2025-05-01T00:00:00Z", 149, 150.2)]])
def test_invalid_fake_market_schema_rejects(quotes):
    with pytest.raises(MarketContractError):
        validate_fake_market_snapshot(fake_snapshot(quotes))


def test_coarse_fake_market_resolution_rejects():
    with pytest.raises(MarketContractError):
        validate_fake_market_snapshot(fake_snapshot([], resolution=61))


def test_return_anchors_tolerance_and_no_interpolation():
    quotes = validate_fake_market_snapshot(fake_snapshot([
        quote("2025-05-01T00:00:59Z", 99, 101), quote("2025-05-01T00:01:00Z", 100, 102),
        quote("2025-05-01T01:00:00Z", 110, 112),
    ]))
    result = extract_forward_log_return("2025-05-01T00:00:00Z", 3600, quotes)
    assert result["p0TimestampUtc"] == "2025-05-01T00:00:59Z"
    assert result["phTimestampUtc"] == "2025-05-01T01:00:00Z"
    assert isclose(result["logReturn"], log(111 / 100))
    unavailable = extract_forward_log_return("2025-05-01T00:02:00Z", 3600, quotes)
    assert unavailable["status"] == "MARKET_QUOTE_UNAVAILABLE"


def test_between_state_statistic_and_deterministic_null():
    equal = fake_observations([("A", 0.0), ("A", 2.0), ("B", 0.0), ("B", 2.0)])
    separated = fake_observations([("A", 0.0), ("A", 0.0), ("B", 2.0), ("B", 2.0)])
    assert between_state_explained_variance(equal) == 0.0
    assert between_state_explained_variance(separated) > 0
    first = deterministic_permutation_test(separated, 86400)
    second = deterministic_permutation_test(separated, 86400)
    assert first["permutationCount"] == PERMUTATION_COUNT
    assert first["nullStatistics"] == second["nullStatistics"] and first["pRaw"] == second["pRaw"]
    assert isclose(first["pRaw"] * 5000, round(first["pRaw"] * 5000))


def test_generic_core_is_reusable_but_the_market_execution_wrapper_requires_future_authorization():
    observations = [{**item, "eventId": item["eventId"].replace("FAKE_SOURCE", "SYNTHETIC_EVENT")} for item in fake_observations([("A", 0.0), ("A", 0.0), ("B", 2.0), ("B", 2.0)])]
    assert deterministic_permutation_test(observations, 86400)["status"] == "PREREGISTERED_STATISTICAL_RESULT"
    with pytest.raises(StatisticalContractError, match="outcomeAnalysisAuthorized"):
        run_authorized_market_analysis(observations, 86400, {})
    authorized = {
        "outcomeAnalysisAuthorized": True,
        "marketSnapshotAdmitted": True,
        "marketSnapshotHash": "SYNTHETIC_SNAPSHOT_HASH",
        "analysisImplementationManifestHash": "SYNTHETIC_MANIFEST_HASH",
    }
    assert run_authorized_market_analysis(observations, 86400, authorized)["status"] == "PREREGISTERED_STATISTICAL_RESULT"


def test_circular_shifts_preserve_counts_and_month_strata_without_side_inversion():
    observations = fake_observations([("A", 0.0), ("A", 1.0), ("B", 2.0), ("B", 3.0)])
    observations += [{**item, "eventId": item["eventId"].replace("FAKE_SOURCE", "FAKE_SOURCE_JPY"), "sideIdentity": "JPY"} for item in observations]
    shifted = circular_shifted_observations(observations, 86400, 1)
    assert Counter(item["stateTokenCanonicalJson"] for item in shifted if item["sideIdentity"] == "USD") == Counter(item["stateTokenCanonicalJson"] for item in observations if item["sideIdentity"] == "USD")
    assert Counter(item["stateTokenCanonicalJson"] for item in shifted if item["sideIdentity"] == "JPY") == Counter(item["stateTokenCanonicalJson"] for item in observations if item["sideIdentity"] == "JPY")
    assert all(item["sideIdentity"] in {"USD", "JPY"} for item in shifted)


def test_temporal_null_allows_zero_in_an_individual_month_but_excludes_global_identity():
    observations = fake_observations([("A", 0.0), ("B", 1.0), ("A", 2.0), ("B", 3.0)])
    observations += [{**item, "eventId": f"FAKE_SOURCE_JUNE_{index}", "exactUtc": f"2025-06-{index + 1:02d}T00:00:00Z"} for index, item in enumerate(fake_observations([("A", 0.0), ("B", 1.0), ("A", 2.0), ("B", 3.0)]))]
    vectors = [deterministic_monthly_offsets(observations, 86400, index) for index in range(1, 32)]
    assert all(any(offset != 0 for offset in vector.values()) for vector in vectors)
    assert any(any(offset == 0 for offset in vector.values()) for vector in vectors)


def test_multiplicity_and_sample_gates():
    raw = {"a": 0.01, "b": 0.04, "c": 0.04}
    assert holm_bonferroni(raw) == {"a": 0.03, "b": 0.08, "c": 0.08}
    assert benjamini_hochberg(raw) == {"a": 0.03, "b": 0.04, "c": 0.04}
    observations = fake_observations([("A", 0.0)] * 20 + [("B", 1.0)] * 40)
    assert market_eligible_testable(observations, {"A", "B"})
    assert not market_eligible_testable(observations[:-1], {"A", "B"})
    assert not market_eligible_testable(fake_observations([("A", 0.0)] * 20 + [("B", 1.0)] * 19), {"A", "B"})
