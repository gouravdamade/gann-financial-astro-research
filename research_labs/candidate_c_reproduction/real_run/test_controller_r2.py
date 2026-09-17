"""RUN1-R2 isolated-runtime tests using only explicitly fake events."""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path

import pytest

from research_labs.candidate_c_reproduction.comparator_ab.projection import _canonical_source_value
from research_labs.candidate_c_reproduction.real_run.controller_r2 import (
    FUTURE_RESULT_PATHS,
    build_request,
    frozen_real_event_ids,
    load_runtime_manifest,
    run_fake_worker,
    run_real_population,
)
from research_labs.candidate_c_reproduction.real_run.worker_authorization import (
    WorkerAuthorizationError,
    issue_production_ticket,
)
from research_labs.candidate_c_reproduction.real_run.worker_protocol import canonical_json_bytes, request_hash
from research_labs.candidate_c_reproduction.real_run.test_real_run_harness import fake_real_event


ROOT = Path(__file__).resolve().parents[3]
RUNTIME_ROOTS = {
    "EVALUATOR_A": Path(r"D:\PycharmProjects-cgvo-candidate-c-run1-r2-a-runtime"),
    "EVALUATOR_B": Path(r"D:\PycharmProjects-cgvo-candidate-c-run1-r2-b-runtime"),
    "V2_COMPARATOR": Path(r"D:\PycharmProjects-cgvo-candidate-c-run1-r2-v2-runtime"),
}
CONTRACT_INPUT_ROOT = Path(os.environ.get("RUN1_R2_CONTRACT_INPUT_ROOT", r"D:\PycharmProjects-cgvo-candidate-c-run1-r1-worktree"))


def _event() -> dict[str, object]:
    value = fake_real_event()
    value["_evaluatorInputKind"] = "SYNTHETIC_ONLY"
    return value


def _fixture() -> dict[str, object]:
    return {
        "fixtureId": "FAKE_REAL_RUN1_FIXTURE", "fixtureFamily": "RUN1_R2_FAKE", "sourceBody": "MARS",
        "targetBody": "JUPITER", "sourceSignIndex": 3, "targetSignIndex": 5, "sunSignIndex": 1,
        "coverageTags": ["FAKE_ONLY"], "semanticFixtureIdentityHash": "FAKE_REAL_RUN1_FIXTURE_HASH",
    }


def _require_runtime(role: str) -> Path:
    path = RUNTIME_ROOTS[role]
    if not path.is_dir():
        pytest.skip(f"clean detached {role} runtime root is unavailable")
    return path


def _require_contract_input_root() -> Path:
    if not CONTRACT_INPUT_ROOT.is_dir():
        pytest.skip("independently verified Candidate C source-input snapshot is unavailable")
    return CONTRACT_INPUT_ROOT


def test_manifest_protects_the_actual_v2_transitive_import_path() -> None:
    manifest = load_runtime_manifest(ROOT)
    files = manifest["runtimeRoots"]["V2_COMPARATOR"]["protectedFiles"]
    assert len(files) == 18
    assert {entry["path"] for entry in files} >= {
        "research_labs/candidate_c_reproduction/comparator_ab/comparator.py",
        "research_labs/candidate_c_reproduction/comparator_ab/projection.py",
        "research_labs/candidate_c_reproduction/comparator_ab/models.py",
        "research_labs/candidate_c_reproduction/comparator_ab/canonical.py",
    }


def test_canonical_request_hash_is_stable_and_production_ticket_is_unavailable() -> None:
    manifest = load_runtime_manifest(ROOT)
    request = build_request(role="EVALUATOR_A", payload={"event": _event()}, manifest=manifest, secret="a" * 64, real_event_ids=frozen_real_event_ids(ROOT), run_session_id="TEST_SESSION_ONE", request_id="TEST_REQUEST_ONE")
    assert request_hash(request) == request_hash(deepcopy(request))
    assert canonical_json_bytes(request) == canonical_json_bytes(deepcopy(request))
    with pytest.raises(WorkerAuthorizationError):
        issue_production_ticket()


def test_fake_a_and_b_workers_verify_import_and_execute_in_their_own_processes() -> None:
    input_root = _require_contract_input_root()
    a = run_fake_worker(role="EVALUATOR_A", runtime_root=_require_runtime("EVALUATOR_A"), contract_input_root=input_root, payload={"event": _event()}, root=ROOT)
    b = run_fake_worker(role="EVALUATOR_B", runtime_root=_require_runtime("EVALUATOR_B"), contract_input_root=input_root, payload={"event": _event()}, root=ROOT)
    for response in (a, b):
        assert response["runtimeVerificationStatus"] == "VERIFIED_SAME_PROCESS"
        assert response["importPathVerificationStatus"] == "VERIFIED_DESIGNATED_ROOT"
        assert response["outputRowCount"] == 8
        identity = response["runtimeRootIdentity"]
        assert identity["pid"] == identity["verificationPid"] == identity["executionPid"]
        assert identity["pid"] != response["controllerPid"]
    assert a["runtimeRootIdentity"]["pid"] != b["runtimeRootIdentity"]["pid"]


def test_fake_outputs_reach_the_verified_v2_worker_without_real_comparison() -> None:
    input_root = _require_contract_input_root()
    a = run_fake_worker(role="EVALUATOR_A", runtime_root=_require_runtime("EVALUATOR_A"), contract_input_root=input_root, payload={"event": _event()}, root=ROOT)
    b = run_fake_worker(role="EVALUATOR_B", runtime_root=_require_runtime("EVALUATOR_B"), contract_input_root=input_root, payload={"event": _event()}, root=ROOT)
    payload = {"eventIds": ["FAKE_REAL_RUN1_001"], "fixture": _fixture(), "aRows": a["outputPayload"]["result"], "bRows": b["outputPayload"]["result"]}
    response = run_fake_worker(role="V2_COMPARATOR", runtime_root=_require_runtime("V2_COMPARATOR"), contract_input_root=input_root, payload=payload, root=ROOT)
    assert response["runtimeVerificationStatus"] == "VERIFIED_SAME_PROCESS"
    assert response["outputPayload"]["result"]["projectedARowCount"] == 8
    assert response["outputPayload"]["result"]["projectedBRowCount"] == 8
    assert response["runtimeRootIdentity"]["pid"] != response["controllerPid"]


def test_worker_refuses_wrong_root_and_real_event_ticket_path() -> None:
    response = run_fake_worker(role="EVALUATOR_A", runtime_root=_require_runtime("EVALUATOR_B"), contract_input_root=_require_contract_input_root(), payload={"event": _event()}, root=ROOT)
    assert response["runtimeVerificationStatus"] == "FAILED"
    manifest = load_runtime_manifest(ROOT)
    actual_event_id = next(iter(frozen_real_event_ids(ROOT)))
    realish = _event() | {"eventId": actual_event_id}
    with pytest.raises(WorkerAuthorizationError):
        build_request(role="EVALUATOR_A", payload={"event": realish}, manifest=manifest, secret="b" * 64, real_event_ids=frozen_real_event_ids(ROOT))


def test_real_execution_and_result_paths_remain_closed() -> None:
    with pytest.raises(Exception, match="REAL_CANDIDATE_C_RUN_AUTHORIZED=false"):
        run_real_population()
    assert all(not (ROOT / path).exists() for path in FUTURE_RESULT_PATHS)


def test_v2_only_uses_explicit_drsti_aliases() -> None:
    assert _canonical_source_value("SARAVALI_4_32_ORDINARY_DRSTI_V1", "DRSTI_1_4") == "1/4"
    assert _canonical_source_value("SARAVALI_4_32_ORDINARY_DRSTI_V1", "DRSTI_9_9") == "DRSTI_9_9"
