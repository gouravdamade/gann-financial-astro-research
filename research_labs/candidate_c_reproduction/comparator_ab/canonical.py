"""Canonical serialization shared only by comparator-owned artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


HASH_CONVENTION = "SHA-256 uppercase hex of UTF-8 canonical JSON: ensure_ascii=true, sort_keys=true, separators=(',',':')."


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest().upper()


def bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def source_set_hash(root: Path, relative_paths: Iterable[str]) -> str:
    manifest = [
        {"path": path, "sha256": bytes_hash((root / path).read_bytes())}
        for path in sorted(relative_paths)
    ]
    return canonical_hash(manifest)
