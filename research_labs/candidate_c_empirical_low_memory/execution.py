"""Additive bounded-memory EMP2 executor, sealed but not authorized in R1-R1."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from research_labs.candidate_c_empirical.artifact import RESULT_RELATIVE_PATH, finalize_result, write_first_result
from research_labs.candidate_c_empirical.execution import (
    MIN_STATE_COUNT,
    MIN_TOTAL_COUNT,
    EmpiricalExecutionError,
    _eligibility_map,
    _family,
    _test_id,
)
from research_labs.candidate_c_empirical.multiplicity import benjamini_hochberg, holm_bonferroni
from research_labs.candidate_c_empirical.runtime import R3_R1_PATHS, validate_empirical_authorization_for_runtime
from research_labs.candidate_c_empirical.statistics import StatisticalContractError, deterministic_permutation_test

from .market_stream import (
    LowMemoryMarketError,
    ReturnRequest,
    StreamingQuote,
    _artifact_map,
    _iter_partition_quotes,
    resolve_forward_log_returns,
    validate_emp1_raw_market_stream,
    validate_streamed_admission_record,
)
from .runtime import MARKET_SNAPSHOT_HASH, LowMemorySuccessorRuntime, verify_emp2_r1_r1_low_memory_runtime


class LowMemoryExecutionError(ValueError):
    """Raised before or during the sealed bounded-memory empirical execution path."""


def _checkout_commit(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "GIT_CHECKOUT_UNAVAILABLE"


def _require_first_result_absent(root: Path) -> None:
    if (root / RESULT_RELATIVE_PATH).exists():
        raise LowMemoryExecutionError("EMPIRICAL_FIRST_RESULT_ALREADY_EXISTS")


def _return_requests(runtime: LowMemorySuccessorRuntime) -> tuple[list[ReturnRequest], dict[tuple[int, int], str]]:
    eligible = _eligibility_map(runtime.frozen_runtime.source_eligibility)
    requests: list[ReturnRequest] = []
    ids: dict[tuple[int, int], str] = {}
    for index, record in enumerate(runtime.frozen_runtime.source_snapshot["sourceStateRecords"]):
        key = (record.get("sideIdentity"), record.get("canonicalRowSlotId"))
        if key not in eligible or record.get("stateTokenCanonicalJson") not in set(eligible[key]):
            continue
        for horizon in (3600, 21600, 86400):
            request_id = f"EMP2::{index}::{horizon}"
            ids[(index, horizon)] = request_id
            requests.append(ReturnRequest(request_id, str(record["exactUtc"]), horizon))
    return requests, ids


def _observations_for_row(
    source_records: list[Mapping[str, Any]],
    side: str,
    slot: str,
    tokens: tuple[str, ...],
    horizon: int,
    returns: Mapping[str, Mapping[str, Any]],
    request_ids: Mapping[tuple[int, int], str],
) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int], int]:
    source_counts = Counter({token: 0 for token in tokens})
    market_counts = Counter({token: 0 for token in tokens})
    observations: list[dict[str, Any]] = []
    unavailable = 0
    allowed = set(tokens)
    for index, record in enumerate(source_records):
        if record.get("sideIdentity") != side or record.get("canonicalRowSlotId") != slot:
            continue
        token = record.get("stateTokenCanonicalJson")
        if token not in allowed:
            continue
        source_counts[token] += 1
        request_id = request_ids.get((index, horizon))
        outcome = returns.get(request_id) if request_id is not None else None
        if not outcome or outcome.get("status") != "MARKET_RETURN_AVAILABLE":
            unavailable += 1
            continue
        market_counts[token] += 1
        observations.append({
            "eventId": record["eventId"], "sideIdentity": side, "canonicalRowSlotId": slot,
            "exactUtc": record["exactUtc"], "stateTokenCanonicalJson": token,
            "horizonSeconds": horizon, "logReturn": outcome["logReturn"],
        })
    return observations, dict(source_counts), dict(market_counts), unavailable


def _result_document(
    root: Path,
    runtime: LowMemorySuccessorRuntime,
    authorization: Any,
    snapshot: Any,
    admission: Any,
    quote_stream: Iterable[StreamingQuote],
) -> dict[str, Any]:
    # Source records are intentionally traversed only after runtime, market, and authorization validation.
    requests, request_ids = _return_requests(runtime)
    returns = resolve_forward_log_returns(requests, quote_stream)
    eligibility = _eligibility_map(runtime.frozen_runtime.source_eligibility)
    ledger = json.loads((root / R3_R1_PATHS["ledger"]).read_text(encoding="utf-8"))
    records = runtime.frozen_runtime.source_snapshot["sourceStateRecords"]
    rows: list[dict[str, Any]] = []
    for entry in ledger["entries"]:
        side, slot, horizon = entry["sideIdentity"], entry["canonicalRowSlotId"], entry["horizonSeconds"]
        tokens = eligibility[(side, slot)]
        observations, source_counts, market_counts, unavailable = _observations_for_row(records, side, slot, tokens, horizon, returns, request_ids)
        retained = tuple(token for token in tokens if market_counts[token] >= MIN_STATE_COUNT)
        row: dict[str, Any] = {
            "testId": _test_id(side, slot, horizon), "sideIdentity": side, "canonicalRowSlotId": slot,
            "horizonSeconds": horizon, "horizonRole": entry["horizonRole"],
            "sourceEligibleStateCount": len(tokens), "sourceEligibleEventCount": sum(source_counts.values()),
            "sourceEligibleStates": list(tokens), "marketReturnAvailableCount": len(observations),
            "marketUnavailableCount": unavailable, "perStateSourceCount": source_counts,
            "perStateMarketAdmissibleCount": market_counts, "retainedMarketEligibleStates": list(retained),
            "retainedMarketEligibleEventCount": sum(market_counts[token] for token in retained),
            "statistic": None, "pRaw": None, "pAdjusted": None, "multiplicityMethod": None, "familyId": None,
        }
        if not observations:
            row["status"] = "MARKET_QUOTE_UNAVAILABLE_FOR_ALL_ELIGIBLE_STATES"
        elif len(retained) < 2 or sum(market_counts[token] for token in retained) < MIN_TOTAL_COUNT:
            row["status"] = "INSUFFICIENT_MARKET_ELIGIBLE_SAMPLE"
        else:
            filtered = [item for item in observations if item["stateTokenCanonicalJson"] in set(retained)]
            try:
                outcome = deterministic_permutation_test(filtered, horizon, set(retained))
            except StatisticalContractError as exc:
                row["status"] = str(exc)
            else:
                if outcome["status"] == "PREREGISTERED_STATISTICAL_RESULT":
                    row.update({"status": "EXECUTED", "statistic": outcome["statistic"], "pRaw": outcome["pRaw"], "permutationCount": outcome["permutationCount"]})
                else:
                    row["status"] = outcome["status"]
        rows.append(row)
    primary = {row["testId"]: row["pRaw"] for row in rows if row["status"] == "EXECUTED" and row["horizonSeconds"] == 86400}
    secondary = {row["testId"]: row["pRaw"] for row in rows if row["status"] == "EXECUTED" and row["horizonSeconds"] in {3600, 21600}}
    primary_adjusted, secondary_adjusted = holm_bonferroni(primary), benjamini_hochberg(secondary)
    for row in rows:
        if row["testId"] in primary_adjusted:
            row.update({"pAdjusted": primary_adjusted[row["testId"]], "multiplicityMethod": "HOLM_BONFERRONI", "familyId": "PRIMARY_ALL_EXECUTED_24H"})
        if row["testId"] in secondary_adjusted:
            row.update({"pAdjusted": secondary_adjusted[row["testId"]], "multiplicityMethod": "BENJAMINI_HOCHBERG", "familyId": "SECONDARY_ALL_EXECUTED_1H_6H"})
    frozen = runtime.frozen_runtime
    return finalize_result({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP2_MARKET_ASSOCIATION_RESULT_V1", "milestone": "MO-R4A-CANDIDATE-C-EMP2",
        "executionId": f"EMP2::{authorization.authorization_id}", "executionCheckoutCommit": _checkout_commit(root),
        "authorizationId": authorization.authorization_id, "authorizationRecordHash": authorization.authorization_record_hash,
        "EMP0R3R1AcceptanceRecordHash": frozen.acceptance_record_hash,
        "EMP0R3R1AnalysisImplementationManifestHash": frozen.analysis_manifest_hash,
        "EMP0R3R1PreregistrationHash": frozen.preregistration_hash,
        "EMP0R3R1TemporalNullContractHash": frozen.temporal_null_contract_hash,
        "EMP0R3R1EmpiricalExecutionContractHash": frozen.execution_contract_hash,
        "EMP0R3R1TestLedgerContractHash": frozen.test_ledger_contract_hash,
        "EMP0R3R1ResultSchemaHash": frozen.result_schema_hash,
        "canonicalSourceStateSnapshotHash": frozen.canonical_source_state_snapshot_hash,
        "sourceStateEligibilityHash": frozen.source_state_eligibility_hash,
        "marketSnapshotHash": snapshot.market_snapshot_hash, "marketAdmissionRecordHash": admission.admission_record_hash,
        "providerId": snapshot.provider_id, "datasetId": snapshot.dataset_id, "instrumentId": snapshot.instrument_id,
        "marketCoverageStartUtc": snapshot.coverage_start_utc, "marketCoverageEndUtc": snapshot.coverage_end_utc,
        "marketRawArtifactHashes": dict(snapshot.raw_artifact_hashes), "testLedgerEntryCount": 24, "testLedger": rows,
        "primaryFamily": _family("PRIMARY_ALL_EXECUTED_24H", "HOLM_BONFERRONI", "alpha", 0.05, primary, primary_adjusted),
        "secondaryFamily": _family("SECONDARY_ALL_EXECUTED_1H_6H", "BENJAMINI_HOCHBERG", "q", 0.10, secondary, secondary_adjusted),
        "scientificRetryCount": 0, "marketDirectionAssigned": False, "sourceWeightsAssigned": False,
        "usdJpySideSignMappingAssigned": False, "postHocTuningPerformed": False, "providerRequeryPerformed": False,
        "interpretationBoundary": "EMPIRICAL_ASSOCIATION_DISCOVERY_NOT_FORECAST_OR_TRADING_VALIDATION", "resultSelfHash": None,
    })


def _execute_low_memory_with_verified_inputs_for_test(
    repo_root: Path | str,
    runtime: LowMemorySuccessorRuntime,
    snapshot: Any,
    admission: Any,
    authorization: Any,
    quote_stream_factory: Callable[[], Iterable[StreamingQuote]],
    result_root: Path | str,
) -> dict[str, Any]:
    """Synthetic-only seam. Public production execution never accepts these inputs."""

    root, target_root = Path(repo_root).resolve(), Path(result_root).resolve()
    _require_first_result_absent(target_root)
    document = _result_document(root, runtime, authorization, snapshot, admission, quote_stream_factory())
    write_first_result(target_root, document)
    return document


def execute_emp2_low_memory_once(
    repo_root: Path | str,
    private_raw_dir: Path | str,
    market_admission_record: Mapping[str, Any],
    authorization_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Future canonical entry point. R1-R1 does not authorize calling it with real data."""

    root = Path(repo_root).resolve()
    _require_first_result_absent(root)
    runtime = verify_emp2_r1_r1_low_memory_runtime(root)
    if dict(market_admission_record) != dict(runtime.admission):
        raise LowMemoryExecutionError("LOW_MEMORY_MARKET_ADMISSION_INPUT_MISMATCH")
    try:
        snapshot = validate_emp1_raw_market_stream(root, private_raw_dir, runtime.inventory, runtime.admission, expected_snapshot_hash=MARKET_SNAPSHOT_HASH)
        admission = validate_streamed_admission_record(
            snapshot, market_admission_record,
            expected_snapshot_schema_hash=runtime.frozen_runtime.market_snapshot_schema_hash,
            expected_market_data_admission_contract_hash=runtime.frozen_runtime.market_data_admission_contract_hash,
        )
        authorization = validate_empirical_authorization_for_runtime(root, snapshot, admission, authorization_record)
    except (LowMemoryMarketError, ValueError) as exc:
        raise LowMemoryExecutionError(str(exc)) from exc
    artifacts, _ = _artifact_map(runtime.inventory, runtime.admission)
    return _execute_low_memory_with_verified_inputs_for_test(
        root, runtime, snapshot, admission, authorization,
        lambda: _iter_partition_quotes(root, Path(private_raw_dir), artifacts, verify_raw_hashes=True, observe_rss=None), root,
    )
