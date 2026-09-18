"""Canonical R3R3 worker tickets and IPC primitives; secrets remain process-local."""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any, Mapping
from uuid import uuid4

from .canonical import canonical_hash, canonical_json_bytes


IPC_SCHEMA_VERSION = "MO_R4A_CANDIDATE_C_RUN1_R3R3_WORKER_IPC_V1"


class WorkerTicketError(PermissionError):
    pass


def new_ephemeral_session_secret() -> str:
    return os.urandom(32).hex()


def new_session_id() -> str:
    return f"RUN1_R3R3_{uuid4().hex}"


def _mac(secret: str, claims: Mapping[str, Any]) -> str:
    return hmac.new(secret.encode("ascii"), canonical_hash(dict(claims)).encode("ascii"), hashlib.sha256).hexdigest().upper()


def issue_ticket(*, secret: str, claims: Mapping[str, Any]) -> dict[str, Any]:
    return {"claims": dict(claims), "mac": _mac(secret, claims)}


def verify_ticket(ticket: Any, *, secret: str, expected: Mapping[str, Any]) -> None:
    if not isinstance(ticket, Mapping) or not isinstance(ticket.get("claims"), Mapping) or not isinstance(ticket.get("mac"), str):
        raise WorkerTicketError("worker ticket is not a signed mapping")
    claims = dict(ticket["claims"])
    if not hmac.compare_digest(str(ticket["mac"]), _mac(secret, claims)):
        raise WorkerTicketError("worker ticket HMAC mismatch")
    if claims != dict(expected):
        raise WorkerTicketError("worker ticket claims do not bind this request")


def request_hash(request: Mapping[str, Any]) -> str:
    value = dict(request); value.pop("authorizationTicket", None)
    return canonical_hash(value)


def response(value: Mapping[str, Any]) -> dict[str, Any]:
    answer = dict(value); answer["responseHash"] = canonical_hash(answer)
    return answer


def protocol_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value)
