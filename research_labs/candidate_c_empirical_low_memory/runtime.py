"""Runtime seals for the additive bounded-memory EMP2 successor."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from research_labs.candidate_c_empirical.canonical import self_hash
from research_labs.candidate_c_empirical.runtime import (
    FrozenEmpiricalRuntimeIdentity,
    FrozenRuntimeError,
    verify_emp0_r3_r1_runtime,
)


R1_IMPLEMENTATION_MANIFEST = "status/research/mo_r4a_candidate_c_emp2_r1_low_memory_implementation_manifest_v1.json"
R1_RUNTIME_CONTRACT = "status/research/mo_r4a_candidate_c_emp2_r1_low_memory_runtime_contract_v1.json"
SUCCESSOR_MANIFEST = "status/research/mo_r4a_candidate_c_emp2_r1_r1_low_memory_implementation_manifest_v1.json"
SUCCESSOR_RUNTIME_CONTRACT = "status/research/mo_r4a_candidate_c_emp2_r1_r1_low_memory_runtime_contract_v1.json"
EMP1_INVENTORY = "status/research/mo_r4a_candidate_c_emp1_raw_market_artifact_inventory_v1.json"
EMP1_ADMISSION = "status/research/mo_r4a_candidate_c_emp1_market_admission_record_v1.json"
PARSER_PATH = "gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3_r2.py"

R1_MANIFEST_HASH = "8D558EEDA98C70CFA2C0235FA07AD3B63FBB85F518BBFFF20690A684C43A12F3"
R1_RUNTIME_HASH = "6B150A756944D3500A05B193D7F759B0FC0C8E7F3B707FA8EE639D9D212184C8"
MARKET_SNAPSHOT_HASH = "0F04578F8BB9FE08558889B3BBAC50F19DCE6702093856842B8A12ED32ACCEEC"
MARKET_ADMISSION_HASH = "2EC34D56151E18CE17FC13F47CFB95007B9FDA86BF5F59B3416D65AF9455160A"
RAW_INVENTORY_HASH = "B4D07BF5A960ADF4828271D1F009D769CBB2A3122D0CC172CAB80AC23A040534"


class LowMemoryRuntimeError(ValueError):
    """Raised before a successor can access real empirical source records."""


@dataclass(frozen=True)
class LowMemorySuccessorRuntime:
    frozen_runtime: FrozenEmpiricalRuntimeIdentity
    successor_manifest_hash: str
    successor_runtime_contract_hash: str
    parser_hash: str
    inventory: Mapping[str, Any]
    admission: Mapping[str, Any]


def _read(root: Path, relative: str) -> dict[str, Any]:
    try:
        value = json.loads((root / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LowMemoryRuntimeError(f"LOW_MEMORY_RUNTIME_INVALID: cannot load {relative}") from exc
    if not isinstance(value, dict):
        raise LowMemoryRuntimeError(f"LOW_MEMORY_RUNTIME_INVALID: {relative} is not an object")
    return value


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _verify_record(document: Mapping[str, Any], field: str, label: str) -> str:
    actual = document.get(field)
    if not isinstance(actual, str) or self_hash(dict(document), field) != actual:
        raise LowMemoryRuntimeError(f"LOW_MEMORY_RUNTIME_INVALID: {label} self-hash mismatch")
    return actual


def verify_emp2_r1_r1_low_memory_runtime(repo_root: Path | str) -> LowMemorySuccessorRuntime:
    """Bind the successor, accepted R1 layer, parser, and frozen scientific contracts."""

    root = Path(repo_root).resolve()
    try:
        frozen = verify_emp0_r3_r1_runtime(root)
    except FrozenRuntimeError as exc:
        raise LowMemoryRuntimeError(str(exc)) from exc

    predecessor_manifest = _read(root, R1_IMPLEMENTATION_MANIFEST)
    predecessor_contract = _read(root, R1_RUNTIME_CONTRACT)
    manifest = _read(root, SUCCESSOR_MANIFEST)
    contract = _read(root, SUCCESSOR_RUNTIME_CONTRACT)
    inventory = _read(root, EMP1_INVENTORY)
    admission = _read(root, EMP1_ADMISSION)

    if _verify_record(predecessor_manifest, "manifestHash", "accepted R1 manifest") != R1_MANIFEST_HASH:
        raise LowMemoryRuntimeError("LOW_MEMORY_RUNTIME_INVALID: accepted R1 manifest identity mismatch")
    if _verify_record(predecessor_contract, "runtimeContractHash", "accepted R1 runtime") != R1_RUNTIME_HASH:
        raise LowMemoryRuntimeError("LOW_MEMORY_RUNTIME_INVALID: accepted R1 runtime identity mismatch")
    successor_manifest_hash = _verify_record(manifest, "implementationManifestHash", "successor manifest")
    successor_contract_hash = _verify_record(contract, "runtimeContractHash", "successor runtime")

    bindings = {
        "predecessorR1ImplementationManifestHash": R1_MANIFEST_HASH,
        "predecessorR1RuntimeContractHash": R1_RUNTIME_HASH,
        "marketSnapshotHash": MARKET_SNAPSHOT_HASH,
        "marketAdmissionRecordHash": MARKET_ADMISSION_HASH,
        "rawArtifactInventoryHash": RAW_INVENTORY_HASH,
        "canonicalSourceStateSnapshotHash": frozen.canonical_source_state_snapshot_hash,
        "sourceStateEligibilityHash": frozen.source_state_eligibility_hash,
        "R3R1PreregistrationHash": frozen.preregistration_hash,
        "R3R1TemporalNullContractHash": frozen.temporal_null_contract_hash,
        "R3R1EmpiricalExecutionContractHash": frozen.execution_contract_hash,
        "R3R1ResultSchemaHash": frozen.result_schema_hash,
        "R3R1TestLedgerContractHash": frozen.test_ledger_contract_hash,
    }
    for field, expected in bindings.items():
        if manifest.get(field) != expected:
            raise LowMemoryRuntimeError(f"LOW_MEMORY_RUNTIME_INVALID: successor manifest binding mismatch for {field}")
    if inventory.get("rawArtifactInventoryHash") != RAW_INVENTORY_HASH or self_hash(dict(inventory), "rawArtifactInventoryHash") != RAW_INVENTORY_HASH:
        raise LowMemoryRuntimeError("LOW_MEMORY_RUNTIME_INVALID: raw artifact inventory mismatch")
    if admission.get("admissionRecordHash") != MARKET_ADMISSION_HASH or self_hash(dict(admission), "admissionRecordHash") != MARKET_ADMISSION_HASH:
        raise LowMemoryRuntimeError("LOW_MEMORY_RUNTIME_INVALID: market admission mismatch")

    files = manifest.get("implementationFileHashes")
    tests = manifest.get("testFileHashes")
    if not isinstance(files, Mapping) or not isinstance(tests, Mapping):
        raise LowMemoryRuntimeError("LOW_MEMORY_RUNTIME_INVALID: successor file bindings missing")
    for relative, expected in dict(files).items():
        if not isinstance(relative, str) or not isinstance(expected, str) or _hash(root / relative) != expected:
            raise LowMemoryRuntimeError(f"LOW_MEMORY_RUNTIME_INVALID: successor implementation byte mismatch for {relative}")
    for relative, expected in dict(tests).items():
        if not isinstance(relative, str) or not isinstance(expected, str) or _hash(root / relative) != expected:
            raise LowMemoryRuntimeError(f"LOW_MEMORY_RUNTIME_INVALID: successor test byte mismatch for {relative}")
    parser_hash = manifest.get("dukascopyParserSha256")
    if not isinstance(parser_hash, str) or _hash(root / PARSER_PATH) != parser_hash:
        raise LowMemoryRuntimeError("LOW_MEMORY_RUNTIME_INVALID: frozen Dukascopy parser byte mismatch")

    contract_bindings = {
        "implementationManifestHash": successor_manifest_hash,
        "marketSnapshotHash": MARKET_SNAPSHOT_HASH,
        "marketAdmissionRecordHash": MARKET_ADMISSION_HASH,
        "rawArtifactInventoryHash": RAW_INVENTORY_HASH,
        "dukascopyParserSha256": parser_hash,
        "executionAuthorized": False,
        "providerRequeryAllowed": False,
        "marketDirectionAssigned": False,
        "sourceWeightsAssigned": False,
    }
    for field, expected in contract_bindings.items():
        if contract.get(field) != expected:
            raise LowMemoryRuntimeError(f"LOW_MEMORY_RUNTIME_INVALID: successor runtime binding mismatch for {field}")
    return LowMemorySuccessorRuntime(frozen, successor_manifest_hash, successor_contract_hash, parser_hash, inventory, admission)
