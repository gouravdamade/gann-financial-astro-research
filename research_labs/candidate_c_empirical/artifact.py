"""Canonical first-result artifact construction and atomic write primitives."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .canonical import canonical_json_bytes, self_hash


RESULT_RELATIVE_PATH = Path("status/research/mo_r4a_candidate_c_emp2_market_association_result_v1.json")


class EmpiricalResultArtifactError(ValueError):
    """Raised for a result self-hash or first-result write violation."""


def finalize_result(document: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(document)
    result["resultSelfHash"] = self_hash(result, "resultSelfHash")
    return result


def verify_result(document: Mapping[str, Any]) -> None:
    if not isinstance(document.get("resultSelfHash"), str) or self_hash(dict(document), "resultSelfHash") != document["resultSelfHash"]:
        raise EmpiricalResultArtifactError("EMPIRICAL_RESULT_SELF_HASH_INVALID")


def write_first_result(output_root: Path | str, document: Mapping[str, Any]) -> Path:
    """Atomically write the one immutable result, refusing replay before replacement."""

    verify_result(document)
    target = Path(output_root).resolve() / RESULT_RELATIVE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise EmpiricalResultArtifactError("EMPIRICAL_FIRST_RESULT_ALREADY_EXISTS")
    descriptor, temporary_name = tempfile.mkstemp(prefix=".emp2-result-", suffix=".json", dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_json_bytes(dict(document)))
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary_name, target)
        except FileExistsError as exc:
            raise EmpiricalResultArtifactError("EMPIRICAL_FIRST_RESULT_ALREADY_EXISTS") from exc
        finally:
            Path(temporary_name).unlink(missing_ok=True)
    except OSError as exc:
        Path(temporary_name).unlink(missing_ok=True)
        raise EmpiricalResultArtifactError("EMPIRICAL_FIRST_RESULT_ATOMIC_WRITE_FAILED") from exc
    return target
