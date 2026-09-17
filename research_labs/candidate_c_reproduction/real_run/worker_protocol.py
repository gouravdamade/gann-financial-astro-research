"""Canonical, outcome-blind IPC primitives for the RUN1-R2 workers."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


IPC_SCHEMA_VERSION = "MO_R4A_CANDIDATE_C_RUN1_R2_WORKER_IPC_V1"
WORKER_ROLES = frozenset({"EVALUATOR_A", "EVALUATOR_B", "V2_COMPARATOR"})


class WorkerProtocolError(ValueError):
    """Raised when a controller/worker payload is not canonical or complete."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest().upper()


def canonical_loads(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkerProtocolError("worker IPC must be UTF-8 JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise WorkerProtocolError("worker IPC must use the frozen canonical JSON encoding")
    return value


def request_without_ticket(request: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(request)
    result.pop("authorizationTicket", None)
    return result


def request_hash(request: Mapping[str, Any]) -> str:
    return sha256(request_without_ticket(request))


def response_hash(response: Mapping[str, Any]) -> str:
    result = dict(response)
    result.pop("responseHash", None)
    return sha256(result)


def validate_request_shape(request: Mapping[str, Any], expected_role: str | None = None) -> None:
    required = {
        "schemaVersion", "runSessionId", "workerRole", "requestId", "executionIntent",
        "runtimeManifestHash", "populationHash", "rowUniverseHash", "inputPayloadHash",
        "authorizationTicket", "payload",
    }
    if set(request) != required:
        raise WorkerProtocolError("worker request does not match the frozen envelope")
    if request["schemaVersion"] != IPC_SCHEMA_VERSION or request["workerRole"] not in WORKER_ROLES:
        raise WorkerProtocolError("worker request has an unrecognized schema or role")
    if expected_role is not None and request["workerRole"] != expected_role:
        raise WorkerProtocolError("worker request role does not match this entrypoint")
    if not all(isinstance(request[key], str) and request[key] for key in required - {"payload", "authorizationTicket"}):
        raise WorkerProtocolError("worker request contains an invalid required identity")
    if not isinstance(request["payload"], dict) or not isinstance(request["authorizationTicket"], dict):
        raise WorkerProtocolError("worker request payload or authorization ticket is malformed")
    if request["inputPayloadHash"] != sha256(request["payload"]):
        raise WorkerProtocolError("worker request payload hash does not bind its payload")


def validate_response_shape(response: Mapping[str, Any], request: Mapping[str, Any]) -> None:
    required = {
        "schemaVersion", "runSessionId", "workerRole", "requestId", "requestHash",
        "runtimeVerificationStatus", "runtimeRootIdentity", "importPathVerificationStatus",
        "outputRowCount", "outputPayload", "responseHash",
    }
    if set(response) != required:
        raise WorkerProtocolError("worker response does not match the frozen envelope")
    if response["schemaVersion"] != IPC_SCHEMA_VERSION:
        raise WorkerProtocolError("worker response schema mismatch")
    for key in ("runSessionId", "workerRole", "requestId"):
        if response[key] != request[key]:
            raise WorkerProtocolError(f"worker response {key} does not bind its request")
    if response["requestHash"] != request_hash(request):
        raise WorkerProtocolError("worker response request hash mismatch")
    if response["responseHash"] != response_hash(response):
        raise WorkerProtocolError("worker response self-hash mismatch")
    if not isinstance(response["outputRowCount"], int) or response["outputRowCount"] < 0:
        raise WorkerProtocolError("worker response row count is invalid")
    if not isinstance(response["outputPayload"], dict):
        raise WorkerProtocolError("worker response output payload is invalid")
