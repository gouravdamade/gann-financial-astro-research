"""Canonical, fail-if-exists durable artifacts for the future authorized run."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .canonical import canonical_json_bytes, self_hash


class ArtifactWriteError(FileExistsError):
    pass


def write_first_artifact(path: Path | str, document: Mapping[str, Any], *, field: str = "artifactSelfHash") -> dict[str, Any]:
    target = Path(path)
    if target.exists():
        raise ArtifactWriteError(f"first-result path already exists: {target}")
    value = dict(document)
    value[field] = self_hash(value, field)
    data = canonical_json_bytes(value)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.parent / f".{target.name}.{uuid4().hex}.tmp"
    try:
        with temporary.open("xb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        if target.exists():
            raise ArtifactWriteError(f"first-result path already exists: {target}")
        os.replace(temporary, target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    if target.read_bytes() != data or self_hash(value, field) != value[field]:
        raise ArtifactWriteError("atomic artifact verification failed")
    return value


def verify_artifact(document: Mapping[str, Any], *, field: str = "artifactSelfHash") -> bool:
    return document.get(field) == self_hash(dict(document), field)
