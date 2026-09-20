#!/usr/bin/env python3
"""Render Git-safe records for the EMP2-R1 market-only successor freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_hash(document: dict[str, Any], field: str) -> str:
    payload = dict(document)
    payload.pop(field, None)
    return hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_record(path: Path, document: dict[str, Any], field: str) -> str:
    document[field] = canonical_hash(document, field)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(document, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
    return document[field]


def main() -> int:
    root = Path.cwd()
    private_report = read_json(Path(r"D:\GannFinancialAstro\sources\private\candidate_c_emp1\canonical\mo_r4a_candidate_c_emp2_r1_market_stream_validation_v1.json"))
    admission = read_json(root / "status/research/mo_r4a_candidate_c_emp1_market_admission_record_v1.json")
    inventory = read_json(root / "status/research/mo_r4a_candidate_c_emp1_raw_market_artifact_inventory_v1.json")
    implementation_paths = [
        "research_labs/candidate_c_empirical_low_memory/__init__.py",
        "research_labs/candidate_c_empirical_low_memory/market_stream.py",
        "tools/research/candidate_c_emp2_r1_market_only_verify.py",
        "tools/research/candidate_c_emp2_r1_render_freeze_records.py",
    ]
    test_paths = ["research_labs/candidate_c_empirical_low_memory/test_market_stream.py"]
    implementation_hashes = {path: sha256(root / path) for path in implementation_paths}
    test_hashes = {path: sha256(root / path) for path in test_paths}
    status_dir = root / "status/research"
    manifest = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP2_R1_LOW_MEMORY_IMPLEMENTATION_MANIFEST_V1",
        "milestone": "MO-R4A-CANDIDATE-C-EMP2-R1-OUTCOME-BLIND-LOW-MEMORY-EXECUTION-SUCCESSOR",
        "predecessorEMP1FreezeCommit": "5aaa58b09b4c2f10631fda32adde33a3593a06d1",
        "R3R1PreregistrationHash": "5BBFB4E26D994CB4A9F56AFB4E2BDF8006865B6D91196C089AB48D47418A08F0",
        "R3R1TemporalNullContractHash": "132650D597ED401CC42E474E38A0753368632C8F98D5E1C02B6E54C9ACF37FC6",
        "R3R1EmpiricalExecutionContractHash": "7E28FD346DC9012FEC6CBDFF86B987666D9F49BCA289504BB1C6B070F2069CE0",
        "R3R1ResultSchemaHash": "6EA5374BCA96ED7D865F428FA0F647F2F02BC40B8424DDDBDB9938F862D3C71B",
        "R3R1TestLedgerContractHash": "91322F3A5759A6BDDA3C87CDDFDDC3A70F9E27A58CC15327AEA45F1C04B0DDAA",
        "canonicalSourceStateSnapshotHash": "9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284",
        "sourceStateEligibilityHash": "ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1",
        "marketSnapshotHash": private_report["marketSnapshotHash"],
        "marketAdmissionRecordHash": admission["admissionRecordHash"],
        "rawArtifactInventoryHash": inventory["rawArtifactInventoryHash"],
        "implementationFileHashes": implementation_hashes,
        "testFileHashes": test_hashes,
        "scientificContractChanged": False,
        "marketDatasetChanged": False,
        "marketSnapshotChanged": False,
        "sourceDatasetChanged": False,
        "eligibilityChanged": False,
        "outcomeDefinitionChanged": False,
        "statisticalMethodChanged": False,
        "multiplicityChanged": False,
        "executionImplementationChanged": True,
        "changeReason": "MEMORY_BOUNDED_SEMANTICS_PRESERVING_EXECUTION_SUCCESSOR",
        "manifestHash": None,
    }
    manifest_hash = write_record(status_dir / "mo_r4a_candidate_c_emp2_r1_low_memory_implementation_manifest_v1.json", manifest, "manifestHash")
    runtime_contract = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP2_R1_LOW_MEMORY_RUNTIME_CONTRACT_V1",
        "milestone": manifest["milestone"],
        "implementationManifestHash": manifest_hash,
        "marketValidation": "RAW_BI5_PARTITION_STREAMING_CANONICAL_SNAPSHOT_REPRODUCTION",
        "quoteSelection": "FIRST_QUOTE_AT_OR_AFTER_ANCHOR_WITHIN_60_SECONDS",
        "p0phDefinition": "MIDPOINT_BID_PLUS_ASK_DIVIDED_BY_TWO",
        "returnDefinition": "NATURAL_LOG_OF_PH_DIVIDED_BY_P0",
        "sourceEventAccessBeforeAuthorization": False,
        "realCandidateCEventAnchorsAccessed": False,
        "providerRequeryAllowed": False,
        "executionAuthorized": False,
        "marketSnapshotHash": private_report["marketSnapshotHash"],
        "marketAdmissionRecordHash": admission["admissionRecordHash"],
        "rawArtifactInventoryHash": inventory["rawArtifactInventoryHash"],
        "runtimeContractHash": None,
    }
    runtime_hash = write_record(status_dir / "mo_r4a_candidate_c_emp2_r1_low_memory_runtime_contract_v1.json", runtime_contract, "runtimeContractHash")
    acceptance = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP2_R1_OUTCOME_BLIND_LOW_MEMORY_EXECUTION_SUCCESSOR_ACCEPTANCE_V1",
        "milestone": manifest["milestone"],
        "predecessorEMP1FreezeCommit": manifest["predecessorEMP1FreezeCommit"],
        "implementationManifestHash": manifest_hash,
        "runtimeContractHash": runtime_hash,
        "marketSnapshotHash": private_report["marketSnapshotHash"],
        "marketAdmissionRecordHash": private_report["marketAdmissionRecordHash"],
        "rawArtifactInventoryHash": inventory["rawArtifactInventoryHash"],
        "rawArtifactCount": private_report["rawArtifactCount"],
        "rawQuoteCount": private_report["rawQuoteCount"],
        "admittedQuoteCount": private_report["admittedQuoteCount"],
        "peakRssBytes": private_report["peakRssBytes"],
        "peakRssBelowFourGiB": private_report["peakRssBelowFourGiB"],
        "oldProtectedRuntimeChanged": False,
        "realCandidateCEventTimestampsAccessed": False,
        "realP0Computed": False,
        "realPHComputed": False,
        "realReturnsComputed": False,
        "realStatisticsComputed": False,
        "publicEMP2ExecutionPerformed": False,
        "providerCallCount": 0,
        "scientificRetryCount": 0,
        "marketDirectionAssigned": False,
        "sourceWeightsAssigned": False,
        "usdJpySideSignMappingAssigned": False,
        "executionAllowed": False,
        "nextGate": "CENTRAL_REVIEW_CANDIDATE_C_EMP2_R1_OUTCOME_BLIND_LOW_MEMORY_EXECUTION_SUCCESSOR",
        "acceptanceHash": None,
    }
    acceptance_hash = write_record(root / "status/acceptance/mo_r4a_candidate_c_emp2_r1_outcome_blind_low_memory_execution_successor.json", acceptance, "acceptanceHash")
    print(json.dumps({"manifestHash": manifest_hash, "runtimeContractHash": runtime_hash, "acceptanceHash": acceptance_hash}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
