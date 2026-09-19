"""The frozen public EMP2 orchestration path; it accepts raw future records only."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from .artifact import finalize_result, write_first_result
from .market_contract import MarketContractError, validate_market_admission_record, validate_market_snapshot
from .multiplicity import benjamini_hochberg, holm_bonferroni
from .returns import extract_forward_log_return
from .runtime import R3_R1_PATHS, FrozenRuntimeError, validate_empirical_authorization_for_runtime, verify_emp0_r3_r1_runtime
from .statistics import StatisticalContractError, deterministic_permutation_test


MIN_STATE_COUNT = 20
MIN_TOTAL_COUNT = 60


class EmpiricalExecutionError(ValueError):
    """Raised before or during the one immutable empirical result construction."""


def _test_id(side: str, slot: str, horizon: int) -> str:
    return f"EMP2::{side}::{slot}::{horizon}"


def _checkout_commit(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "GIT_CHECKOUT_UNAVAILABLE"


def _eligibility_map(eligibility: Mapping[str, Any]) -> dict[tuple[str, str], tuple[str, ...]]:
    result: dict[tuple[str, str], tuple[str, ...]] = {}
    for cell in eligibility["cells"]:
        if cell.get("sourceTestable") is True:
            result[(cell["sideIdentity"], cell["canonicalRowSlotId"])] = tuple(item["stateTokenCanonicalJson"] for item in cell["eligibleValueStates"])
    if len(result) != 8:
        raise EmpiricalExecutionError("FROZEN_SOURCE_ELIGIBILITY_INVALID")
    return result


def _observations_for_row(
    source_records: list[Mapping[str, Any]], side: str, slot: str, tokens: tuple[str, ...], horizon: int, quotes: Any,
) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int], int]:
    source_counts = Counter({token: 0 for token in tokens})
    market_counts = Counter({token: 0 for token in tokens})
    observations: list[dict[str, Any]] = []
    unavailable = 0
    allowed = set(tokens)
    for record in source_records:
        if record.get("sideIdentity") != side or record.get("canonicalRowSlotId") != slot:
            continue
        token = record.get("stateTokenCanonicalJson")
        if token not in allowed:
            continue
        source_counts[token] += 1
        extracted = extract_forward_log_return(record["exactUtc"], horizon, quotes)
        if extracted["status"] != "MARKET_RETURN_AVAILABLE":
            unavailable += 1
            continue
        market_counts[token] += 1
        observations.append({"eventId": record["eventId"], "sideIdentity": side, "canonicalRowSlotId": slot, "exactUtc": record["exactUtc"], "stateTokenCanonicalJson": token, "horizonSeconds": horizon, "logReturn": extracted["logReturn"]})
    return observations, dict(source_counts), dict(market_counts), unavailable


def _family(family_id: str, method: str, threshold_key: str, threshold: float, raw: Mapping[str, float], adjusted: Mapping[str, float]) -> dict[str, Any]:
    return {"familyId": family_id, "method": method, threshold_key: threshold, "executedTestCount": len(raw), "testIds": sorted(raw), "rawPValues": {key: raw[key] for key in sorted(raw)}, "adjustedPValues": {key: adjusted[key] for key in sorted(adjusted)}}


def _execute_emp2_once_to_root_for_test(
    repo_root: Path | str,
    market_snapshot_record: Mapping[str, Any],
    market_admission_record: Mapping[str, Any],
    authorization_record: Mapping[str, Any],
    result_root: Path | str,
) -> dict[str, Any]:
    """Private test seam; production must use ``execute_emp2_once`` only."""

    root = Path(repo_root).resolve()
    runtime = verify_emp0_r3_r1_runtime(root)
    target_root = Path(result_root).resolve()
    target = target_root / "status/research/mo_r4a_candidate_c_emp2_market_association_result_v1.json"
    if target.exists():
        raise EmpiricalExecutionError("EMPIRICAL_FIRST_RESULT_ALREADY_EXISTS")
    try:
        snapshot = validate_market_snapshot(market_snapshot_record)
        admission = validate_market_admission_record(market_admission_record, snapshot, expected_snapshot_schema_hash=runtime.market_snapshot_schema_hash, expected_market_data_admission_contract_hash=runtime.market_data_admission_contract_hash)
        authorization = validate_empirical_authorization_for_runtime(root, snapshot, admission, authorization_record)
    except (MarketContractError, FrozenRuntimeError, ValueError) as exc:
        raise EmpiricalExecutionError(str(exc)) from exc
    eligibility = _eligibility_map(runtime.source_eligibility)
    ledger_contract = json.loads((root / R3_R1_PATHS["ledger"]).read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for ledger_entry in ledger_contract["entries"]:
        side, slot, horizon = ledger_entry["sideIdentity"], ledger_entry["canonicalRowSlotId"], ledger_entry["horizonSeconds"]
        tokens = eligibility[(side, slot)]
        observations, source_counts, market_counts, unavailable = _observations_for_row(runtime.source_snapshot["sourceStateRecords"], side, slot, tokens, horizon, snapshot.quotes)
        retained = tuple(token for token in tokens if market_counts[token] >= MIN_STATE_COUNT)
        row: dict[str, Any] = {"testId": _test_id(side, slot, horizon), "sideIdentity": side, "canonicalRowSlotId": slot, "horizonSeconds": horizon, "horizonRole": ledger_entry["horizonRole"], "sourceEligibleStateCount": len(tokens), "sourceEligibleEventCount": sum(source_counts.values()), "sourceEligibleStates": list(tokens), "marketReturnAvailableCount": len(observations), "marketUnavailableCount": unavailable, "perStateSourceCount": source_counts, "perStateMarketAdmissibleCount": market_counts, "retainedMarketEligibleStates": list(retained), "retainedMarketEligibleEventCount": sum(market_counts[token] for token in retained), "statistic": None, "pRaw": None, "pAdjusted": None, "multiplicityMethod": None, "familyId": None}
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
    primary_raw = {row["testId"]: row["pRaw"] for row in rows if row["status"] == "EXECUTED" and row["horizonSeconds"] == 86400}
    secondary_raw = {row["testId"]: row["pRaw"] for row in rows if row["status"] == "EXECUTED" and row["horizonSeconds"] in {3600, 21600}}
    primary_adjusted, secondary_adjusted = holm_bonferroni(primary_raw), benjamini_hochberg(secondary_raw)
    for row in rows:
        if row["testId"] in primary_adjusted:
            row.update({"pAdjusted": primary_adjusted[row["testId"]], "multiplicityMethod": "HOLM_BONFERRONI", "familyId": "PRIMARY_ALL_EXECUTED_24H"})
        if row["testId"] in secondary_adjusted:
            row.update({"pAdjusted": secondary_adjusted[row["testId"]], "multiplicityMethod": "BENJAMINI_HOCHBERG", "familyId": "SECONDARY_ALL_EXECUTED_1H_6H"})
    document = finalize_result({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP2_MARKET_ASSOCIATION_RESULT_V1", "milestone": "MO-R4A-CANDIDATE-C-EMP2", "executionId": f"EMP2::{authorization.authorization_id}", "executionCheckoutCommit": _checkout_commit(root), "authorizationId": authorization.authorization_id, "authorizationRecordHash": authorization.authorization_record_hash, "EMP0R3R1AcceptanceRecordHash": runtime.acceptance_record_hash, "EMP0R3R1AnalysisImplementationManifestHash": runtime.analysis_manifest_hash, "EMP0R3R1PreregistrationHash": runtime.preregistration_hash, "EMP0R3R1TemporalNullContractHash": runtime.temporal_null_contract_hash, "EMP0R3R1EmpiricalExecutionContractHash": runtime.execution_contract_hash, "EMP0R3R1TestLedgerContractHash": runtime.test_ledger_contract_hash, "EMP0R3R1ResultSchemaHash": runtime.result_schema_hash, "canonicalSourceStateSnapshotHash": runtime.canonical_source_state_snapshot_hash, "sourceStateEligibilityHash": runtime.source_state_eligibility_hash, "marketSnapshotHash": snapshot.market_snapshot_hash, "marketAdmissionRecordHash": admission.admission_record_hash, "providerId": snapshot.provider_id, "datasetId": snapshot.dataset_id, "instrumentId": snapshot.instrument_id, "marketCoverageStartUtc": snapshot.coverage_start_utc, "marketCoverageEndUtc": snapshot.coverage_end_utc, "marketRawArtifactHashes": dict(snapshot.raw_artifact_hashes), "testLedgerEntryCount": 24, "testLedger": rows, "primaryFamily": _family("PRIMARY_ALL_EXECUTED_24H", "HOLM_BONFERRONI", "alpha", 0.05, primary_raw, primary_adjusted), "secondaryFamily": _family("SECONDARY_ALL_EXECUTED_1H_6H", "BENJAMINI_HOCHBERG", "q", 0.10, secondary_raw, secondary_adjusted), "scientificRetryCount": 0, "marketDirectionAssigned": False, "sourceWeightsAssigned": False, "usdJpySideSignMappingAssigned": False, "postHocTuningPerformed": False, "providerRequeryPerformed": False, "interpretationBoundary": "EMPIRICAL_ASSOCIATION_DISCOVERY_NOT_FORECAST_OR_TRADING_VALIDATION", "resultSelfHash": None})
    write_first_result(target_root, document)
    return document


def execute_emp2_once(
    repo_root: Path | str,
    market_snapshot_record: Mapping[str, Any],
    market_admission_record: Mapping[str, Any],
    authorization_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Run the future EMP2 process only at its canonical verified-repository root."""

    root = Path(repo_root).resolve()
    return _execute_emp2_once_to_root_for_test(root, market_snapshot_record, market_admission_record, authorization_record, root)
