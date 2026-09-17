"""Ephemeral, fake-only cross-process authorization for RUN1-R2 probes."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Any, Iterable, Mapping

from .worker_protocol import sha256


TEST_EVENT_PREFIX = "FAKE_REAL_RUN1_"
REAL_CANDIDATE_C_RUN_AUTHORIZED = False
TEST_EXECUTION_INTENT = "FAKE_ISOLATED_RUNTIME_PROBE"


class WorkerAuthorizationError(ValueError):
    """Raised before an unbound ticket can reach a worker runtime."""


def new_ephemeral_session_secret() -> str:
    return secrets.token_hex(32)


def _mac(secret: str, claims: Mapping[str, Any]) -> str:
    return hmac.new(secret.encode("ascii"), sha256(claims).encode("ascii"), hashlib.sha256).hexdigest().upper()


def issue_test_ticket(
    *,
    secret: str,
    role: str,
    run_session_id: str,
    request_id: str,
    event_ids: Iterable[str],
    input_payload_hash: str,
    population_hash: str,
    target_implementation_commit: str,
    real_event_ids: Iterable[str],
) -> dict[str, Any]:
    ids = tuple(event_ids)
    forbidden = frozenset(real_event_ids)
    if not ids or any(not event_id.startswith(TEST_EVENT_PREFIX) or event_id in forbidden for event_id in ids):
        raise WorkerAuthorizationError("test-only worker tickets require fake event IDs outside the frozen population")
    claims = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_RUN1_R2_WORKER_TICKET_V1",
        "testOnly": True,
        "executionIntent": TEST_EXECUTION_INTENT,
        "workerRole": role,
        "runSessionId": run_session_id,
        "requestId": request_id,
        "eventIds": list(ids),
        "inputPayloadHash": input_payload_hash,
        "populationHash": population_hash,
        "targetImplementationCommit": target_implementation_commit,
    }
    return {"claims": claims, "mac": _mac(secret, claims)}


def issue_production_ticket(*_args: Any, **_kwargs: Any) -> None:
    raise WorkerAuthorizationError("REAL_CANDIDATE_C_RUN_AUTHORIZED=false; production worker ticket issuance is unavailable")


def validate_test_ticket(
    ticket: Mapping[str, Any],
    *,
    secret: str,
    role: str,
    run_session_id: str,
    request_id: str,
    event_ids: Iterable[str],
    input_payload_hash: str,
    population_hash: str,
    target_implementation_commit: str,
) -> None:
    claims = ticket.get("claims") if isinstance(ticket, Mapping) else None
    mac = ticket.get("mac") if isinstance(ticket, Mapping) else None
    if not isinstance(claims, dict) or not isinstance(mac, str) or not hmac.compare_digest(mac, _mac(secret, claims)):
        raise WorkerAuthorizationError("worker authorization ticket is malformed or untrusted")
    expected = {
        "testOnly": True,
        "executionIntent": TEST_EXECUTION_INTENT,
        "workerRole": role,
        "runSessionId": run_session_id,
        "requestId": request_id,
        "eventIds": list(event_ids),
        "inputPayloadHash": input_payload_hash,
        "populationHash": population_hash,
        "targetImplementationCommit": target_implementation_commit,
    }
    if any(claims.get(key) != value for key, value in expected.items()):
        raise WorkerAuthorizationError("worker authorization ticket does not bind this exact request")
    if any(not isinstance(event_id, str) or not event_id.startswith(TEST_EVENT_PREFIX) for event_id in expected["eventIds"]):
        raise WorkerAuthorizationError("worker authorization is fake-event-only")
