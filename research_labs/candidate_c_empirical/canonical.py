"""Canonical JSON primitives for EMP0 research records."""

from __future__ import annotations

import hashlib
import json
from typing import Any


HASH_CONVENTION = "SHA-256 uppercase hex of UTF-8 canonical JSON: ensure_ascii=true, sort_keys=true, separators=(',',':')."


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_json_text(value: Any) -> str:
    return canonical_json_bytes(value).decode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest().upper()


def self_hash(document: dict[str, Any], field: str) -> str:
    payload = dict(document)
    payload.pop(field, None)
    return canonical_hash(payload)
