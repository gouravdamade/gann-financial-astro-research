"""Outcome-blind controller for isolated RUN1-R2 fake-worker probes only."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping
from uuid import uuid4

from .admission import load_and_validate_real_population
from .authorization import RealCandidateCRunNotAuthorized
from .worker_authorization import issue_test_ticket, new_ephemeral_session_secret
from .worker_protocol import IPC_SCHEMA_VERSION, canonical_json_bytes, sha256, validate_response_shape


RUNTIME_MANIFEST_PATH = Path("status/research/mo_r4a_candidate_c_run1_r2_isolated_runtime_manifest_v1.json")
WORKER_SCRIPTS = {
    "EVALUATOR_A": Path("tools/research/candidate_c_run1/worker_a.py"),
    "EVALUATOR_B": Path("tools/research/candidate_c_run1/worker_b.py"),
    "V2_COMPARATOR": Path("tools/research/candidate_c_run1/worker_v2.py"),
}
FUTURE_RESULT_PATHS = (
    "status/research/mo_r4a_candidate_c_run1_evaluator_a_real_output_v1.json",
    "status/research/mo_r4a_candidate_c_run1_evaluator_b_real_output_v1.json",
    "status/research/mo_r4a_candidate_c_run1_ab_comparison_result_v1.json",
)


class ControllerR2Error(RuntimeError):
    """Raised when a fake-only worker probe does not satisfy the frozen IPC."""


def _root(root: Path | str | None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parents[3]


def load_runtime_manifest(root: Path | str | None = None) -> dict[str, Any]:
    path = _root(root) / RUNTIME_MANIFEST_PATH
    value = json.loads(path.read_text(encoding="utf-8"))
    declared = value.pop("runtimeManifestHash")
    if declared != sha256(value):
        raise ControllerR2Error("R2 runtime manifest self-hash mismatch")
    value["runtimeManifestHash"] = declared
    return value


def frozen_real_event_ids(root: Path | str | None = None) -> frozenset[str]:
    population = load_and_validate_real_population(_root(root))
    return frozenset(str(event["eventId"]) for event in population.events)


def build_request(
    *, role: str, payload: Mapping[str, Any], manifest: Mapping[str, Any], secret: str,
    real_event_ids: Iterable[str], run_session_id: str | None = None, request_id: str | None = None,
) -> dict[str, Any]:
    event_ids = [str(payload["event"]["eventId"])] if role != "V2_COMPARATOR" else [str(item) for item in payload["eventIds"]]
    request = {
        "schemaVersion": IPC_SCHEMA_VERSION, "runSessionId": run_session_id or f"TEST_SESSION_{uuid4().hex}",
        "workerRole": role, "requestId": request_id or f"TEST_REQUEST_{uuid4().hex}",
        "executionIntent": "FAKE_ISOLATED_RUNTIME_PROBE", "runtimeManifestHash": manifest["runtimeManifestHash"],
        "populationHash": manifest["populationIdentity"]["populationHash"],
        "rowUniverseHash": manifest["populationIdentity"]["rowUniverseHash"],
        "inputPayloadHash": sha256(payload), "authorizationTicket": {}, "payload": dict(payload),
    }
    request["authorizationTicket"] = issue_test_ticket(
        secret=secret, role=role, run_session_id=request["runSessionId"], request_id=request["requestId"],
        event_ids=event_ids, input_payload_hash=request["inputPayloadHash"], population_hash=request["populationHash"],
        target_implementation_commit=manifest["runtimeRoots"][role]["protectedCommit"], real_event_ids=real_event_ids,
    )
    return request


def run_fake_worker(
    *, role: str, runtime_root: Path | str, payload: Mapping[str, Any], root: Path | str | None = None,
    contract_input_root: Path | str, secret: str | None = None, real_event_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    controller_root = _root(root)
    manifest = load_runtime_manifest(controller_root)
    session_secret = secret or new_ephemeral_session_secret()
    request = build_request(role=role, payload=payload, manifest=manifest, secret=session_secret, real_event_ids=real_event_ids if real_event_ids is not None else frozen_real_event_ids(controller_root))
    env = {**os.environ, "RUN1_R2_TEST_TICKET_SECRET": session_secret, "PYTHONPATH": ""}
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str(controller_root / WORKER_SCRIPTS[role]), "--runtime-root", str(Path(runtime_root).resolve()), "--contract-input-root", str(Path(contract_input_root).resolve()), "--runtime-manifest", str(controller_root / RUNTIME_MANIFEST_PATH)],
        input=canonical_json_bytes(request), capture_output=True, env=env, timeout=120,
    )
    if completed.returncode != 0:
        raise ControllerR2Error(f"worker process crashed: {completed.stderr.decode('utf-8', errors='replace')}")
    stdout = completed.stdout.rstrip(b"\n")
    try:
        response = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ControllerR2Error("worker stdout is not protocol JSON") from exc
    if canonical_json_bytes(response) != stdout:
        raise ControllerR2Error("worker stdout contains noncanonical protocol output")
    validate_response_shape(response, request)
    response["controllerPid"] = os.getpid()
    response["stderr"] = completed.stderr.decode("utf-8", errors="replace")
    return response


def run_real_population(*_args: Any, **_kwargs: Any) -> None:
    raise RealCandidateCRunNotAuthorized("REAL_CANDIDATE_C_RUN_AUTHORIZED=false; RUN1-R2 exposes no real execution path")
