"""Canonical hashing primitives for the frozen Candidate C contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def canonical_json_bytes(value: Any) -> bytes:
    """Return the P0 canonical JSON byte representation."""

    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def canonical_hash_without_field(value: dict[str, Any], field: str) -> str:
    payload = dict(value)
    payload.pop(field, None)
    return canonical_hash(payload)


def aggregate_source_hash(root: Path, relative_paths: Iterable[str]) -> str:
    """Hash a sorted path/hash manifest for an implementation source set.

    The freeze record states this convention explicitly. Paths are repository
    relative POSIX strings and each file is hashed as raw bytes first.
    """

    entries = []
    for relative_path in sorted(set(relative_paths)):
        path = root / Path(relative_path)
        entries.append({"path": relative_path.replace("\\", "/"), "sha256": sha256_file(path)})
    return canonical_hash(entries)
