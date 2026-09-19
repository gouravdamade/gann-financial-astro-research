"""Repository-bound EMP0-R3-R1 runtime identity and authorization validation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .authorization import (
    _EmpiricalAuthorizationExpectedBindings,
    _ValidatedEmpiricalAuthorization,
    _validate_empirical_execution_authorization,
)
from .canonical import self_hash
from .market_contract import ValidatedMarketAdmissionRecord, ValidatedMarketSnapshot


SOURCE_SNAPSHOT_PATH = "status/research/mo_r4a_candidate_c_emp0_canonical_source_state_snapshot_v1.json"
SOURCE_ELIGIBILITY_PATH = "status/research/mo_r4a_candidate_c_emp0_source_state_eligibility_v1.json"
R3_R1_PATHS = {
    "manifest": "status/research/mo_r4a_candidate_c_emp0_r3_r1_analysis_implementation_manifest_v1.json",
    "preregistration": "status/research/mo_r4a_candidate_c_emp0_r3_r1_market_association_preregistration_v1.json",
    "temporal": "status/research/mo_r4a_candidate_c_emp0_r3_r1_temporal_null_contract_v1.json",
    "execution": "status/research/mo_r4a_candidate_c_emp0_r3_r1_empirical_execution_contract_v1.json",
    "authorization": "status/research/mo_r4a_candidate_c_emp0_r3_r1_empirical_authorization_contract_v1.json",
    "result_schema": "status/research/mo_r4a_candidate_c_emp0_r3_r1_emp2_result_schema_v1.json",
    "ledger": "status/research/mo_r4a_candidate_c_emp0_r2_future_test_ledger_contract_v1.json",
    "market_schema": "status/research/mo_r4a_candidate_c_emp0_r3_r1_market_snapshot_schema_v1.json",
    "market_contract": "status/research/mo_r4a_candidate_c_emp0_r3_r1_market_data_admission_contract_v1.json",
    "admission_contract": "status/research/mo_r4a_candidate_c_emp0_r3_r1_market_admission_record_contract_v1.json",
    "runtime": "status/research/mo_r4a_candidate_c_emp0_r3_r1_runtime_identity_contract_v1.json",
    "acceptance": "status/acceptance/mo_r4a_candidate_c_emp0_r3_r1_pre_data_one_shot_result_root_contract_seal_freeze.json",
}
SOURCE_SNAPSHOT_HASH = "9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284"
SOURCE_ELIGIBILITY_HASH = "ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1"
R2_LEDGER_HASH = "91322F3A5759A6BDDA3C87CDDFDDC3A70F9E27A58CC15327AEA45F1C04B0DDAA"


class FrozenRuntimeError(ValueError):
    """Raised before any empirical calculation when a frozen identity is invalid."""


@dataclass(frozen=True)
class FrozenEmpiricalRuntimeIdentity:
    implementation_commit: str
    acceptance_record_hash: str
    analysis_manifest_hash: str
    preregistration_hash: str
    temporal_null_contract_hash: str
    execution_contract_hash: str
    authorization_contract_hash: str
    result_schema_hash: str
    test_ledger_contract_hash: str
    market_snapshot_schema_hash: str
    market_data_admission_contract_hash: str
    market_admission_record_contract_hash: str
    canonical_source_state_snapshot_hash: str
    source_state_eligibility_hash: str
    source_snapshot: Mapping[str, Any]
    source_eligibility: Mapping[str, Any]


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FrozenRuntimeError(f"EMP0_R3_RUNTIME_INVALID: cannot load {path}") from exc
    if not isinstance(value, dict):
        raise FrozenRuntimeError(f"EMP0_R3_RUNTIME_INVALID: {path} is not a JSON object")
    return value


def _verify_self_hash(document: Mapping[str, Any], field: str, label: str) -> str:
    actual = document.get(field)
    if not isinstance(actual, str) or self_hash(dict(document), field) != actual:
        raise FrozenRuntimeError(f"EMP0_R3_RUNTIME_INVALID: {label} self-hash mismatch")
    return actual


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _source_shape(snapshot: Mapping[str, Any], eligibility: Mapping[str, Any], ledger: Mapping[str, Any]) -> None:
    if snapshot.get("canonicalSourceStateSnapshotHash") != SOURCE_SNAPSHOT_HASH:
        raise FrozenRuntimeError("EMP0_R3_RUNTIME_INVALID: historical source snapshot identity mismatch")
    if self_hash(dict(snapshot), "canonicalSourceStateSnapshotHash") != SOURCE_SNAPSHOT_HASH:
        raise FrozenRuntimeError("EMP0_R3_RUNTIME_INVALID: historical source snapshot self-hash mismatch")
    if snapshot.get("populationEventCount") != 645 or snapshot.get("canonicalSourceStateRowCount") != 5160:
        raise FrozenRuntimeError("EMP0_R3_RUNTIME_INVALID: historical source snapshot shape mismatch")
    if eligibility.get("sourceStateEligibilityHash") != SOURCE_ELIGIBILITY_HASH:
        raise FrozenRuntimeError("EMP0_R3_RUNTIME_INVALID: historical eligibility identity mismatch")
    if self_hash(dict(eligibility), "sourceStateEligibilityHash") != SOURCE_ELIGIBILITY_HASH:
        raise FrozenRuntimeError("EMP0_R3_RUNTIME_INVALID: historical eligibility self-hash mismatch")
    cells = eligibility.get("cells")
    if not isinstance(cells, list) or len(cells) != 16 or sum(cell.get("sourceTestable") is True for cell in cells) != 8:
        raise FrozenRuntimeError("EMP0_R3_RUNTIME_INVALID: historical eligibility shape mismatch")
    if ledger.get("testLedgerContractHash") != R2_LEDGER_HASH or self_hash(dict(ledger), "testLedgerContractHash") != R2_LEDGER_HASH:
        raise FrozenRuntimeError("EMP0_R3_RUNTIME_INVALID: frozen ledger hash mismatch")
    if ledger.get("futureTestLedgerEntryCount") != 24 or len(ledger.get("entries", [])) != 24:
        raise FrozenRuntimeError("EMP0_R3_RUNTIME_INVALID: frozen ledger shape mismatch")


def verify_emp0_r3_r1_runtime(repo_root: Path | str) -> FrozenEmpiricalRuntimeIdentity:
    """Verify all fixed EMP0-R3-R1 contracts and protected implementation bytes."""

    root = Path(repo_root).resolve()
    documents = {name: _read(root / relative) for name, relative in R3_R1_PATHS.items()}
    fields = {
        "manifest": "analysisImplementationManifestHash",
        "preregistration": "marketAssociationPreregistrationHash",
        "temporal": "temporalNullContractHash",
        "execution": "empiricalExecutionContractHash",
        "authorization": "empiricalAuthorizationContractHash",
        "result_schema": "resultSchemaHash",
        "ledger": "testLedgerContractHash",
        "market_schema": "marketSnapshotSchemaHash",
        "market_contract": "marketDataAdmissionContractHash",
        "admission_contract": "marketAdmissionRecordContractHash",
        "runtime": "runtimeIdentityContractHash",
        "acceptance": "acceptanceRecordHash",
    }
    hashes = {name: _verify_self_hash(document, fields[name], name) for name, document in documents.items()}
    snapshot = _read(root / SOURCE_SNAPSHOT_PATH)
    eligibility = _read(root / SOURCE_ELIGIBILITY_PATH)
    _source_shape(snapshot, eligibility, documents["ledger"])
    manifest = documents["manifest"]
    implementation_hashes = manifest.get("implementationHashes")
    if not isinstance(implementation_hashes, dict) or not implementation_hashes:
        raise FrozenRuntimeError("EMP0_R3_R1_RUNTIME_INVALID: missing implementation hashes")
    package = root / "research_labs/candidate_c_empirical"
    for name, expected in implementation_hashes.items():
        if _sha256(package / name) != expected:
            raise FrozenRuntimeError(f"EMP0_R3_R1_RUNTIME_INVALID: protected implementation byte mismatch for {name}")
    test_hashes = manifest.get("testSourceHashes")
    if not isinstance(test_hashes, dict) or not test_hashes:
        raise FrozenRuntimeError("EMP0_R3_R1_RUNTIME_INVALID: missing protected test hashes")
    for name, expected in test_hashes.items():
        if _sha256(package / name) != expected:
            raise FrozenRuntimeError(f"EMP0_R3_R1_RUNTIME_INVALID: protected test byte mismatch for {name}")
    contract = documents["runtime"]
    expected_contract = {
        "analysisManifestHash": hashes["manifest"], "preregistrationHash": hashes["preregistration"],
        "temporalNullContractHash": hashes["temporal"], "executionContractHash": hashes["execution"],
        "authorizationContractHash": hashes["authorization"], "resultSchemaHash": hashes["result_schema"],
        "testLedgerContractHash": hashes["ledger"], "marketSnapshotSchemaHash": hashes["market_schema"],
        "marketDataAdmissionContractHash": hashes["market_contract"], "marketAdmissionRecordContractHash": hashes["admission_contract"],
        "canonicalSourceStateSnapshotHash": SOURCE_SNAPSHOT_HASH, "sourceStateEligibilityHash": SOURCE_ELIGIBILITY_HASH,
    }
    for field, expected in expected_contract.items():
        if contract.get(field) != expected:
            raise FrozenRuntimeError(f"EMP0_R3_R1_RUNTIME_INVALID: runtime contract binding mismatch for {field}")
    return FrozenEmpiricalRuntimeIdentity(
        implementation_commit=str(manifest["implementationCommit"]), acceptance_record_hash=hashes["acceptance"],
        analysis_manifest_hash=hashes["manifest"], preregistration_hash=hashes["preregistration"],
        temporal_null_contract_hash=hashes["temporal"], execution_contract_hash=hashes["execution"],
        authorization_contract_hash=hashes["authorization"], result_schema_hash=hashes["result_schema"],
        test_ledger_contract_hash=hashes["ledger"], market_snapshot_schema_hash=hashes["market_schema"],
        market_data_admission_contract_hash=hashes["market_contract"], market_admission_record_contract_hash=hashes["admission_contract"],
        canonical_source_state_snapshot_hash=SOURCE_SNAPSHOT_HASH, source_state_eligibility_hash=SOURCE_ELIGIBILITY_HASH,
        source_snapshot=snapshot, source_eligibility=eligibility,
    )


def validate_empirical_authorization_for_runtime(
    repo_root: Path | str,
    validated_market_snapshot: ValidatedMarketSnapshot,
    validated_market_admission: ValidatedMarketAdmissionRecord,
    authorization_record: Mapping[str, Any],
) -> _ValidatedEmpiricalAuthorization:
    """Derive authorization expectations only from verified runtime and supplied market identities."""

    runtime = verify_emp0_r3_r1_runtime(repo_root)
    expected = _EmpiricalAuthorizationExpectedBindings(
        runtime.implementation_commit, runtime.acceptance_record_hash, runtime.analysis_manifest_hash,
        runtime.preregistration_hash, runtime.temporal_null_contract_hash, runtime.execution_contract_hash,
        runtime.result_schema_hash, runtime.test_ledger_contract_hash, runtime.canonical_source_state_snapshot_hash,
        runtime.source_state_eligibility_hash, validated_market_snapshot.market_snapshot_hash,
        validated_market_admission.admission_record_hash, runtime.market_snapshot_schema_hash,
        runtime.market_data_admission_contract_hash, runtime.market_admission_record_contract_hash,
    )
    return _validate_empirical_execution_authorization(authorization_record, expected)
