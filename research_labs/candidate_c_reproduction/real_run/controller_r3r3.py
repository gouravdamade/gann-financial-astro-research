"""Authorization-ready one-shot controller; R3R3 invokes it with FAKE data only."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence
from uuid import uuid4

from .admission import EXPECTED_EVENT_COUNT, EXPECTED_POPULATION_HASH, EXPECTED_ROW_COUNT, EXPECTED_ROW_KEY_HASH, load_and_validate_real_population
from .artifacts_r3r3 import verify_artifact, write_first_artifact
from .authorization_record_r3r3 import ValidatedRealRunAuthorization, validate_external_authorization
from .canonical import canonical_hash
from .contract_bundle_r3r2 import verify_bundle
from .real_v2_bridge_r3r2 import bridge_event, bridge_population_identity
from .audit_r3r3_r1 import (
    MismatchAccountingError, RowUniverseValidationError, fake_expected_universe,
    mismatch_counts_by_class, validate_complete_row_universe,
)
from .worker_protocol_r3r3 import IPC_SCHEMA_VERSION, issue_ticket, new_ephemeral_session_secret, new_session_id, protocol_bytes, request_hash


REAL_RESULT_PATHS = {
    "EVALUATOR_A": "status/research/mo_r4a_candidate_c_run1_evaluator_a_real_output_v1.json",
    "EVALUATOR_B": "status/research/mo_r4a_candidate_c_run1_evaluator_b_real_output_v1.json",
    "V2_COMPARISON": "status/research/mo_r4a_candidate_c_run1_ab_comparison_result_v1.json",
}
FUTURE_RESULT_PATHS = tuple(REAL_RESULT_PATHS.values())
RUNTIME_MANIFEST_PATH = Path("status/research/mo_r4a_candidate_c_run1_r3r3_runtime_manifest_v1.json")
WORKERS = {"EVALUATOR_A": "worker_a_r3r3.py", "EVALUATOR_B": "worker_b_r3r3.py", "V2_COMPARATOR": "worker_v2_r3r3.py"}
REAL_READ_SCOPE = "IDENTITY_STRUCTURE_ADAPTER_AUTHORIZATION_BUNDLE_AND_REAL_V2_BRIDGE_VALIDATION_ONLY"


class ControllerR3R3Error(RuntimeError):
    pass


def _root(root: Path | str) -> Path: return Path(root).resolve()

def _manifest(root: Path) -> dict[str, Any]:
    document = json.loads((root / RUNTIME_MANIFEST_PATH).read_text(encoding="utf-8"))
    declared = document.pop("runtimeManifestHash")
    if declared != canonical_hash(document): raise ControllerR3R3Error("R3R3 runtime manifest self-hash mismatch")
    document["runtimeManifestHash"] = declared
    return document

def _order(events: Sequence[Mapping[str, Any]]) -> str:
    return canonical_hash([{"eventId": item["eventId"], "eventHash": item["eventHash"]} for item in events])

def future_result_paths_are_unpopulated(root: Path | str) -> bool:
    return all(not path.exists() for path in resolved_result_paths(root).values())

def resolved_result_paths(root: Path | str) -> dict[str, Path]:
    base = _root(root)
    return {role: base / relative for role, relative in REAL_RESULT_PATHS.items()}

def structural_real_preflight(root: Path | str, population: Any) -> dict[str, Any]:
    bundle = verify_bundle(root); bridge, bridge_hash = bridge_population_identity(population.events)
    return {"realFrozenPopulationRead": True, "realFrozenPopulationReadScope": REAL_READ_SCOPE, "populationCount": len(population.events), "populationHash": population.manifest["exactPopulationHash"], "populationOrderHash": _order(population.events), "rowUniverseHash": EXPECTED_ROW_KEY_HASH, "realV2BridgePopulationHash": bridge_hash, "realV2BridgeCount": len(bridge), "bundleManifestHash": bundle["bundleManifestHash"], "realFrozenPopulationEvaluated": False, "realCandidateCOutputProduced": False, "realCandidateCOutputInspected": False, "realCandidateCOutputRowCount": 0, "realComparisonExecuted": False}

def expected_bindings(root: Path | str) -> dict[str, Any]:
    base, runtime, bundle = _root(root), _manifest(_root(root)), verify_bundle(root)
    freeze_commit = subprocess.run(["git", "-C", str(base), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    return {"R3R3ImplementationCommit": runtime["controllerImplementationCommit"], "R3R3FreezeCommit": freeze_commit, "R3R3FinalExecutionContractHash": runtime["finalExecutionContractHash"], "R3R3RuntimeManifestHash": runtime["runtimeManifestHash"], "bundleManifestHash": bundle["bundleManifestHash"], "canonicalGitBundleAggregateHash": bundle["canonicalGitBundleAggregateHash"], "loaderViewBundleAggregateHash": bundle["loaderViewBundleAggregateHash"], "dependencyInventoryHash": bundle["dependencyInventoryHash"], "renderedPathsHash": bundle["renderedPathsHash"], "populationHash": EXPECTED_POPULATION_HASH, "populationOrderHash": runtime["populationOrderHash"], "rowUniverseHash": EXPECTED_ROW_KEY_HASH, "realV2BridgeHash": runtime["realV2BridgeHash"], "realV2BridgePopulationHash": runtime["realV2BridgePopulationHash"], "aProtectedIdentity": runtime["aProtectedIdentity"], "bProtectedIdentity": runtime["bProtectedIdentity"], "v2ProtectedIdentity": runtime["v2ProtectedIdentity"]}

def _ticket_claims(role: str, request: Mapping[str, Any], runtime: Mapping[str, Any], bindings: Mapping[str, Any], *, test_only: bool, authorization_hash: str, extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    entry = runtime["runtimeRoots"][role]
    claims = {"testOnly": test_only, "authorizationRecordHash": authorization_hash, "runSessionId": request["runSessionId"], "workerRole": role, "requestId": request["requestId"], "requestHash": request_hash(request), "payloadHash": request["payloadHash"], "populationHash": bindings["populationHash"], "populationOrderHash": bindings["populationOrderHash"], "rowUniverseHash": bindings["rowUniverseHash"], "bundleManifestHash": bindings["bundleManifestHash"], "canonicalGitBundleAggregateHash": bindings["canonicalGitBundleAggregateHash"], "loaderViewBundleAggregateHash": bindings["loaderViewBundleAggregateHash"], "targetProtectedCommit": entry["protectedCommit"], "targetProtectedIdentity": bindings[{"EVALUATOR_A": "aProtectedIdentity", "EVALUATOR_B": "bProtectedIdentity", "V2_COMPARATOR": "v2ProtectedIdentity"}[role]], "oneShotExecutionIntent": True}
    if extra: claims.update(extra)
    return claims

def _request(role: str, payload: Mapping[str, Any], *, session: str, runtime: Mapping[str, Any], bindings: Mapping[str, Any], secret: str, test_only: bool, authorization_hash: str, extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    request = {"schemaVersion": IPC_SCHEMA_VERSION, "runSessionId": session, "workerRole": role, "requestId": f"{role}_{uuid4().hex}", "executionIntent": "FAKE_SUBPROCESS_DRY_RUN" if test_only else "ONE_SHOT_AUTHORIZED_REAL_REPRODUCTION", "runtimeManifestHash": runtime["runtimeManifestHash"], "payloadHash": canonical_hash(payload), "authorizationTicket": {}, "payload": dict(payload)}
    claims = _ticket_claims(role, request, runtime, bindings, test_only=test_only, authorization_hash=authorization_hash, extra=extra)
    request["authorizationTicket"] = issue_ticket(secret=secret, claims=claims)
    return request

def _run_worker(root: Path, role: str, runtime_root: Path, contract_root: Path, request: Mapping[str, Any], secret: str) -> dict[str, Any]:
    environment = {**os.environ, "PYTHONPATH": "", "RUN1_R3R3_SESSION_SECRET": secret}
    completed = subprocess.run([sys.executable, "-I", "-B", str(root / "tools/research/candidate_c_run1" / WORKERS[role]), "--runtime-root", str(runtime_root), "--contract-input-root", str(contract_root), "--runtime-manifest", str(root / RUNTIME_MANIFEST_PATH)], input=protocol_bytes(request), capture_output=True, env=environment, timeout=240)
    if completed.returncode != 0: raise ControllerR3R3Error(f"{role} worker crashed: {completed.stderr.decode(errors='replace')}")
    raw = completed.stdout.rstrip(b"\n")
    try: response = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise ControllerR3R3Error("worker stdout is not JSON") from exc
    if protocol_bytes(response) != raw or response.get("workerRole") != role or response.get("requestHash") != request_hash(request): raise ControllerR3R3Error("worker stdout violates canonical IPC")
    if response.get("runtimeVerificationStatus") == "FAILED": raise ControllerR3R3Error(str(response.get("outputPayload")))
    response["stderr"] = completed.stderr.decode("utf-8", errors="replace")
    return response

def _group(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    answer: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows: answer.setdefault(str(row["eventId"]), []).append(row)
    if any(len(value) != 8 for value in answer.values()): raise ControllerR3R3Error("worker did not return exactly eight rows per event")
    return answer

def _artifact(role: str, response: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], universe: Mapping[str, Any], *, session: str, auth_hash: str, runtime: Mapping[str, Any], bindings: Mapping[str, Any]) -> dict[str, Any]:
    return {"schemaVersion": "MO_R4A_CANDIDATE_C_RUN1_R3R3_RAW_OUTPUT_V1", "milestone": "MO-R4A-CANDIDATE-C-RUN1-R3R3", "runSessionId": session, "authorizationRecordHash": auth_hash, "workerRole": role, "workerRequestHash": response["requestHash"], "workerResponseHash": response["responseHash"], "workerImplementationHash": runtime["workerImplementationHashes"][role], "protectedScientificCommit": runtime["runtimeRoots"][role]["protectedCommit"], "protectedScientificIdentity": bindings[{"EVALUATOR_A": "aProtectedIdentity", "EVALUATOR_B": "bProtectedIdentity"}[role]], "runtimeManifestHash": runtime["runtimeManifestHash"], "bundleManifestHash": bindings["bundleManifestHash"], "canonicalGitBundleAggregateHash": bindings["canonicalGitBundleAggregateHash"], "loaderViewBundleAggregateHash": bindings["loaderViewBundleAggregateHash"], "populationHash": bindings["populationHash"], "populationOrderHash": bindings["populationOrderHash"], "rowUniverseHash": bindings["rowUniverseHash"], **universe, "rowCount": len(rows), "rows": list(rows)}

def _execute(root: Path, *, events: Sequence[Mapping[str, Any]], expected_universe: Sequence[Mapping[str, Any]], bindings: Mapping[str, Any], runtime_roots: Mapping[str, Path], contract_root: Path, output_root: Path, test_only: bool, authorization_hash: str) -> dict[str, Any]:
    runtime = _manifest(root); secret, session = new_ephemeral_session_secret(), new_session_id(); bridge, _ = bridge_population_identity(events)
    a_request = _request("EVALUATOR_A", {"events": list(events)}, session=session, runtime=runtime, bindings=bindings, secret=secret, test_only=test_only, authorization_hash=authorization_hash)
    paths = resolved_result_paths(output_root)
    a_response = _run_worker(root, "EVALUATOR_A", runtime_roots["EVALUATOR_A"], contract_root, a_request, secret); a_rows = a_response["outputPayload"]["result"]; _group(a_rows)
    a_universe = validate_complete_row_universe(a_rows, expected_universe, expected_hash=bindings["rowUniverseHash"])
    a_artifact = write_first_artifact(paths["EVALUATOR_A"], _artifact("EVALUATOR_A", a_response, a_rows, a_universe, session=session, auth_hash=authorization_hash, runtime=runtime, bindings=bindings))
    if not verify_artifact(a_artifact): raise ControllerR3R3Error("A artifact self-hash verification failed")
    b_request = _request("EVALUATOR_B", {"events": list(events)}, session=session, runtime=runtime, bindings=bindings, secret=secret, test_only=test_only, authorization_hash=authorization_hash)
    b_response = _run_worker(root, "EVALUATOR_B", runtime_roots["EVALUATOR_B"], contract_root, b_request, secret); b_rows = b_response["outputPayload"]["result"]; _group(b_rows)
    b_universe = validate_complete_row_universe(b_rows, expected_universe, expected_hash=bindings["rowUniverseHash"])
    b_artifact = write_first_artifact(paths["EVALUATOR_B"], _artifact("EVALUATOR_B", b_response, b_rows, b_universe, session=session, auth_hash=authorization_hash, runtime=runtime, bindings=bindings))
    if not verify_artifact(b_artifact): raise ControllerR3R3Error("B artifact self-hash verification failed")
    a_by, b_by = _group(a_rows), _group(b_rows)
    extra = {"aRawArtifactHash": a_artifact["artifactSelfHash"], "bRawArtifactHash": b_artifact["artifactSelfHash"], "realV2BridgeHash": bindings["realV2BridgeHash"], "realV2BridgePopulationHash": bindings["realV2BridgePopulationHash"]}
    v2_payload = {"fixtures": bridge, "aRowsByEvent": a_by, "bRowsByEvent": b_by}
    v2_request = _request("V2_COMPARATOR", v2_payload, session=session, runtime=runtime, bindings=bindings, secret=secret, test_only=test_only, authorization_hash=authorization_hash, extra=extra)
    v2_response = _run_worker(root, "V2_COMPARATOR", runtime_roots["V2_COMPARATOR"], contract_root, v2_request, secret); result = v2_response["outputPayload"]["result"]
    mismatches = result["mismatches"]
    counts = mismatch_counts_by_class(mismatches)
    total = len(mismatches)
    exact = total == 0
    if sum(counts.values()) != total: raise ControllerR3R3Error("mismatch accounting invariant failed")
    comparison = write_first_artifact(paths["V2_COMPARISON"], {"schemaVersion": "MO_R4A_CANDIDATE_C_RUN1_R3R3_COMPARISON_V1", "milestone": "MO-R4A-CANDIDATE-C-RUN1-R3R3", "runSessionId": session, "authorizationRecordHash": authorization_hash, "runtimeManifestHash": runtime["runtimeManifestHash"], "bundleManifestHash": bindings["bundleManifestHash"], "canonicalGitBundleAggregateHash": bindings["canonicalGitBundleAggregateHash"], "loaderViewBundleAggregateHash": bindings["loaderViewBundleAggregateHash"], "populationHash": bindings["populationHash"], "populationOrderHash": bindings["populationOrderHash"], "rowUniverseHash": bindings["rowUniverseHash"], **extra, "v2WorkerRequestHash": v2_response["requestHash"], "v2WorkerResponseHash": v2_response["responseHash"], "v2WorkerImplementationHash": runtime["workerImplementationHashes"]["V2_COMPARATOR"], "v2ProtectedImplementationCommit": runtime["runtimeRoots"]["V2_COMPARATOR"]["protectedCommit"], "v2ProtectedScientificIdentity": bindings["v2ProtectedIdentity"], "v2ProjectionBlobHash": "4B4828FF09494EA3EAE8ACF57B0004177E6507B8ED8A198871F861E60C2AAF5E", "v2SemanticProjectionHash": bindings["v2ProtectedIdentity"], "v2ProtectedPathSetHash": runtime["fullV2ProtectedPathSetHash"], "aRawRowCount": len(a_rows), "bRawRowCount": len(b_rows), "aProjectedRowCount": result["projectedARowCount"], "bProjectedRowCount": result["projectedBRowCount"], "semanticRowsCompared": result["semanticRowsCompared"], "totalMismatches": total, "mismatchCountsByClass": counts, "mismatchRecords": mismatches, "exactAgreement": exact, "result": "REAL_SOURCE_REPRODUCTION_SEMANTIC_AGREEMENT" if exact else "REAL_SOURCE_REPRODUCTION_SEMANTIC_MISMATCH"})
    return {"runSessionId": session, "a": a_response, "b": b_response, "v2": v2_response, "aArtifact": a_artifact, "bArtifact": b_artifact, "comparison": comparison}

def run_fake_dry_run(root: Path | str, events: Sequence[Mapping[str, Any]], *, runtime_roots: Mapping[str, Path], temp_root: Path) -> dict[str, Any]:
    base, runtime = _root(root), _manifest(_root(root)); bundle = verify_bundle(root)
    if len(events) < 3 or any(not str(event.get("eventId", "")).startswith("FAKE_REAL_RUN1_") for event in events): raise ControllerR3R3Error("fake dry run requires three FAKE_REAL_RUN1 events")
    fake_hash, fake_order = canonical_hash(list(events)), _order(events)
    frozen_universe = json.loads((Path(bundle["loaderView"]) / "status/research/mo_r4a_candidate_c_p0_component_input_bindings_v1.json").read_text(encoding="utf-8"))["outputCardinality"]["expectedRowKeyUniverse"]
    expected_universe = fake_expected_universe(frozen_universe=frozen_universe, fake_event_ids=[str(event["eventId"]) for event in events])
    bindings = {"populationHash": fake_hash, "populationOrderHash": fake_order, "rowUniverseHash": canonical_hash(expected_universe), "bundleManifestHash": bundle["bundleManifestHash"], "canonicalGitBundleAggregateHash": bundle["canonicalGitBundleAggregateHash"], "loaderViewBundleAggregateHash": bundle["loaderViewBundleAggregateHash"], "realV2BridgeHash": runtime["realV2BridgeHash"], "realV2BridgePopulationHash": canonical_hash([bridge_event(event) for event in events]), "aProtectedIdentity": runtime["aProtectedIdentity"], "bProtectedIdentity": runtime["bProtectedIdentity"], "v2ProtectedIdentity": runtime["v2ProtectedIdentity"]}
    return _execute(base, events=events, expected_universe=expected_universe, bindings=bindings, runtime_roots=runtime_roots, contract_root=Path(bundle["loaderView"]), output_root=temp_root, test_only=True, authorization_hash="TEST_ONLY_NOT_REAL_AUTHORIZATION")

def run_authorized_real_population(authorization_record: Mapping[str, Any] | None, *, controller_root: Path | str, a_runtime_root: Path, b_runtime_root: Path, v2_runtime_root: Path, contract_bundle_root: Path | str) -> dict[str, Any]:
    base = _root(controller_root); bindings = expected_bindings(base); authorization: ValidatedRealRunAuthorization = validate_external_authorization(authorization_record, bindings)
    if not future_result_paths_are_unpopulated(base): raise ControllerR3R3Error("a first-result path already exists; no resume-as-success")
    population = load_and_validate_real_population(contract_bundle_root)
    if len(population.events) != EXPECTED_EVENT_COUNT or population.manifest["exactPopulationHash"] != EXPECTED_POPULATION_HASH or _order(population.events) != bindings["populationOrderHash"]: raise ControllerR3R3Error("frozen real population identity mismatch")
    return _execute(base, events=population.events, expected_universe=population.bindings["outputCardinality"]["expectedRowKeyUniverse"], bindings=bindings, runtime_roots={"EVALUATOR_A": a_runtime_root, "EVALUATOR_B": b_runtime_root, "V2_COMPARATOR": v2_runtime_root}, contract_root=Path(verify_bundle(base)["loaderView"]), output_root=base, test_only=False, authorization_hash=authorization.authorization_hash)
