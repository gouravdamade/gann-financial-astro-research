"""Focused pre-data regressions for the EMP0-R3-R1 one-shot contract seal."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from .authorization import EmpiricalAuthorizationError, _AUTHORIZATION_REQUIRED_FIELDS
from .canonical import self_hash
from .execution import EmpiricalExecutionError, execute_emp2_once
from .market_contract import MarketContractError, validate_market_admission_record, validate_market_snapshot
from .runtime import R3_R1_PATHS, validate_empirical_authorization_for_runtime, verify_emp0_r3_r1_runtime
from .test_emp0_r3 import _admission, _authorization, _synthetic_snapshot


ROOT = Path(__file__).resolve().parents[2]


def _rehash(record: dict[str, Any], field: str) -> dict[str, Any]:
    record[field] = self_hash(record, field)
    return record


def _copy_runtime_fixture(target: Path) -> None:
    shutil.copytree(ROOT / "research_labs", target / "research_labs")
    shutil.copytree(ROOT / "status", target / "status")


def _validated_records() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    snapshot = _synthetic_snapshot()
    admission = _admission(snapshot)
    authorization = _authorization(snapshot, admission)
    return snapshot, admission, authorization


def test_public_emp2_signature_has_only_canonical_root_inputs():
    assert tuple(inspect.signature(execute_emp2_once).parameters) == (
        "repo_root",
        "market_snapshot_record",
        "market_admission_record",
        "authorization_record",
    )


def test_public_execution_writes_only_canonical_root_and_replay_fails(tmp_path, monkeypatch):
    from . import execution

    fixture_root = tmp_path / "synthetic-repository"
    _copy_runtime_fixture(fixture_root)
    snapshot, admission, authorization = _validated_records()
    monkeypatch.setattr(
        execution,
        "deterministic_permutation_test",
        lambda observations, horizon, tokens: {
            "status": "PREREGISTERED_STATISTICAL_RESULT",
            "statistic": 0.25,
            "pRaw": 0.2,
            "permutationCount": 4999,
        },
    )

    result = execute_emp2_once(fixture_root, snapshot, admission, authorization)
    result_path = fixture_root / "status/research/mo_r4a_candidate_c_emp2_market_association_result_v1.json"
    assert result_path.exists()
    assert result["authorizationRecordHash"] == authorization["authorizationRecordHash"]
    with pytest.raises(EmpiricalExecutionError, match="EMPIRICAL_FIRST_RESULT_ALREADY_EXISTS"):
        execute_emp2_once(fixture_root, snapshot, admission, authorization)
    with pytest.raises(TypeError):
        execute_emp2_once(fixture_root, snapshot, admission, authorization, output_root=tmp_path / "elsewhere")


def test_authorization_contract_exactly_matches_executable_required_fields():
    runtime = verify_emp0_r3_r1_runtime(ROOT)
    contract = json.loads((ROOT / R3_R1_PATHS["authorization"]).read_text(encoding="utf-8"))
    assert contract["extraFieldsAllowed"] is False
    assert set(contract["requiredFields"]) == _AUTHORIZATION_REQUIRED_FIELDS
    snapshot, admission, authorization = _validated_records()
    validated_snapshot = validate_market_snapshot(snapshot)
    validated_admission = validate_market_admission_record(
        admission,
        validated_snapshot,
        expected_snapshot_schema_hash=runtime.market_snapshot_schema_hash,
        expected_market_data_admission_contract_hash=runtime.market_data_admission_contract_hash,
    )
    for field in _AUTHORIZATION_REQUIRED_FIELDS:
        invalid = deepcopy(authorization)
        invalid.pop(field)
        with pytest.raises(EmpiricalAuthorizationError):
            validate_empirical_authorization_for_runtime(ROOT, validated_snapshot, validated_admission, invalid)
    invalid = deepcopy(authorization)
    invalid["unregisteredProvenance"] = "not permitted by the frozen R3-R1 schema"
    _rehash(invalid, "authorizationRecordHash")
    with pytest.raises(EmpiricalAuthorizationError, match="unregistered fields"):
        validate_empirical_authorization_for_runtime(ROOT, validated_snapshot, validated_admission, invalid)


def test_authorization_rejects_wrong_admission_contract_and_all_switch_violations():
    runtime = verify_emp0_r3_r1_runtime(ROOT)
    snapshot, admission, authorization = _validated_records()
    validated_snapshot = validate_market_snapshot(snapshot)
    validated_admission = validate_market_admission_record(
        admission,
        validated_snapshot,
        expected_snapshot_schema_hash=runtime.market_snapshot_schema_hash,
        expected_market_data_admission_contract_hash=runtime.market_data_admission_contract_hash,
    )
    for field, value in (
        ("marketAdmissionRecordContractHash", "D" * 64),
        ("authorized", False),
        ("oneShotExecutionIntent", False),
        ("marketOutcomeAccess", False),
        ("providerRequeryAllowed", True),
        ("postHocTuningAllowed", True),
        ("sourceEligibilityChangesAllowed", True),
        ("newHorizonsAllowed", True),
        ("newSourceStatesAllowed", True),
    ):
        invalid = deepcopy(authorization)
        invalid[field] = value
        _rehash(invalid, "authorizationRecordHash")
        with pytest.raises(EmpiricalAuthorizationError):
            validate_empirical_authorization_for_runtime(ROOT, validated_snapshot, validated_admission, invalid)


@pytest.mark.parametrize(
    "legacy_fields",
    [
        ("emp0R2MarketSnapshotSchemaHash", "emp0R2MarketDataAdmissionContractHash"),
        ("emp0R3MarketSnapshotSchemaHash", "emp0R3MarketDataAdmissionContractHash"),
    ],
)
def test_new_admission_rejects_predecessor_r2_and_r3_binding_names(legacy_fields):
    runtime = verify_emp0_r3_r1_runtime(ROOT)
    snapshot, admission, _ = _validated_records()
    invalid = deepcopy(admission)
    schema_field, contract_field = legacy_fields
    invalid[schema_field] = invalid.pop("emp0R3R1MarketSnapshotSchemaHash")
    invalid[contract_field] = invalid.pop("emp0R3R1MarketDataAdmissionContractHash")
    _rehash(invalid, "admissionRecordHash")
    with pytest.raises(MarketContractError, match="missing required fields"):
        validate_market_admission_record(
            invalid,
            validate_market_snapshot(snapshot),
            expected_snapshot_schema_hash=runtime.market_snapshot_schema_hash,
            expected_market_data_admission_contract_hash=runtime.market_data_admission_contract_hash,
        )
    invalid = deepcopy(admission)
    invalid[schema_field] = "E" * 64
    invalid[contract_field] = "F" * 64
    _rehash(invalid, "admissionRecordHash")
    with pytest.raises(MarketContractError, match="unregistered fields"):
        validate_market_admission_record(
            invalid,
            validate_market_snapshot(snapshot),
            expected_snapshot_schema_hash=runtime.market_snapshot_schema_hash,
            expected_market_data_admission_contract_hash=runtime.market_data_admission_contract_hash,
        )
