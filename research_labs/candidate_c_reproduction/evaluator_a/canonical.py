"""Canonical JSON and hash helpers owned by Evaluator A."""

from __future__ import annotations

import hashlib
import json
from typing import Any


HASH_CONVENTION = (
    "SHA-256 uppercase hex of UTF-8 canonical JSON: ensure_ascii=true, "
    "sort_keys=true, separators=(',',':')."
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest().upper()


def bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def without_field(record: dict[str, Any], field: str) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != field}


def verify_self_hash(record: dict[str, Any], field: str, expected: str) -> None:
    actual = canonical_hash(without_field(record, field))
    recorded = record.get(field)
    if recorded != expected or actual != expected:
        raise ValueError(f"{field} mismatch: recorded={recorded!r}, actual={actual!r}, expected={expected!r}")
