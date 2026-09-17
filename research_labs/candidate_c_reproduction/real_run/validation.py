"""Non-evaluating RUN1 structural and source-identity validation."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

from .adapter_b import RealCandidateCEvent
from .canonical import canonical_hash


A_IMPLEMENTATION_COMMIT = "e581c499d3a3872cd88d6d17bf92c39a5c95185b"
B_IMPLEMENTATION_COMMIT = "267885b84e1d796b438b09d73f3fb9792235a41e"
V2_PROJECTION_COMMIT = "52c3b287a70018370e153a77b84c36e6b0dbfb42"
A_IMPLEMENTATION_HASH = "93ECB7BDB684C9F9788F63BADAE8D297453F02557D7BB89DB2621CF9E257DCFB"
A_TEST_HASH = "93BF61F16BB9CF44B44D0F251418D9CFDC7F8E74557556F802B2F9B6D144A25E"
B_IMPLEMENTATION_HASH = "0A3266F754939D2408B4B7646A1E36A1CEC7338EDADE5844E831BCF6EB4CD199"
B_TEST_HASH = "31AA1B525B29AFE4CD206D63A1DA611820D6A87E1C71465645BADEE0B9487CB9"
V2_SEMANTIC_PROJECTION_HASH = "1DDFC3B79EC30913254A2FEA117A97EA1761E42D8681EB5D2CB6B2D698187BED"
V2_PROJECTION_BLOB_HASH = "4B4828FF09494EA3EAE8ACF57B0004177E6507B8ED8A198871F861E60C2AAF5E"
V2_PROJECTION_TEST_HASH = "A2A7CCA8B8687CC8E8D4D4BD15394DFD341A1260A7A7D958BF057959AD3A9FE9"

A_SOURCE_FILES = (
    "research_labs/candidate_c_reproduction/__init__.py",
    "research_labs/candidate_c_reproduction/evaluator_a/__init__.py",
    "research_labs/candidate_c_reproduction/evaluator_a/canonical.py",
    "research_labs/candidate_c_reproduction/evaluator_a/contract_loader.py",
    "research_labs/candidate_c_reproduction/evaluator_a/evaluator.py",
    "research_labs/candidate_c_reproduction/evaluator_a/schema.py",
)
B_SOURCE_FILES = (
    "research_labs/candidate_c_reproduction/__init__.py",
    "research_labs/candidate_c_reproduction/evaluator_b/__init__.py",
    "research_labs/candidate_c_reproduction/evaluator_b/canonical.py",
    "research_labs/candidate_c_reproduction/evaluator_b/contract_loader.py",
    "research_labs/candidate_c_reproduction/evaluator_b/evaluator.py",
    "research_labs/candidate_c_reproduction/evaluator_b/models.py",
)
V2_RUNTIME_FILES = ("research_labs/candidate_c_reproduction/comparator_ab/projection.py",)

# A and B each froze the package initializer. Their historical bytes differ,
# so one checkout cannot truthfully satisfy both frozen source manifests.
RUNTIME_ROOT_A = "EVALUATOR_A_RUNTIME_ROOT"
RUNTIME_ROOT_B = "EVALUATOR_B_RUNTIME_ROOT"
RUNTIME_ROOT_V2 = "V2_PROJECTION_RUNTIME_ROOT"

PROTECTED_RUNTIME_FILES = tuple(
    (path, A_IMPLEMENTATION_COMMIT, RUNTIME_ROOT_A) for path in A_SOURCE_FILES
) + tuple(
    (path, B_IMPLEMENTATION_COMMIT, RUNTIME_ROOT_B) for path in B_SOURCE_FILES
) + tuple((path, V2_PROJECTION_COMMIT, RUNTIME_ROOT_V2) for path in V2_RUNTIME_FILES)

RUNTIME_MODULE_PATHS = {
    "research_labs.candidate_c_reproduction": (
        "research_labs/candidate_c_reproduction/__init__.py",
        RUNTIME_ROOT_A,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_a": (
        "research_labs/candidate_c_reproduction/evaluator_a/__init__.py",
        RUNTIME_ROOT_A,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_a.canonical": (
        "research_labs/candidate_c_reproduction/evaluator_a/canonical.py",
        RUNTIME_ROOT_A,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_a.contract_loader": (
        "research_labs/candidate_c_reproduction/evaluator_a/contract_loader.py",
        RUNTIME_ROOT_A,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_a.evaluator": (
        "research_labs/candidate_c_reproduction/evaluator_a/evaluator.py",
        RUNTIME_ROOT_A,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_a.schema": (
        "research_labs/candidate_c_reproduction/evaluator_a/schema.py",
        RUNTIME_ROOT_A,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_b": (
        "research_labs/candidate_c_reproduction/evaluator_b/__init__.py",
        RUNTIME_ROOT_B,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_b.canonical": (
        "research_labs/candidate_c_reproduction/evaluator_b/canonical.py",
        RUNTIME_ROOT_B,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_b.contract_loader": (
        "research_labs/candidate_c_reproduction/evaluator_b/contract_loader.py",
        RUNTIME_ROOT_B,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_b.evaluator": (
        "research_labs/candidate_c_reproduction/evaluator_b/evaluator.py",
        RUNTIME_ROOT_B,
        False,
    ),
    "research_labs.candidate_c_reproduction.evaluator_b.models": (
        "research_labs/candidate_c_reproduction/evaluator_b/models.py",
        RUNTIME_ROOT_B,
        False,
    ),
    "research_labs.candidate_c_reproduction.comparator_ab.projection": (
        "research_labs/candidate_c_reproduction/comparator_ab/projection.py",
        RUNTIME_ROOT_V2,
        True,
    ),
}


class RealRunValidationError(ValueError):
    """Raised before an unauthorized real execution can reach evaluator logic."""


def _git_blob_bytes(root: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{path}"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RealRunValidationError(f"cannot resolve frozen Git blob {commit}:{path}")
    return result.stdout


def _source_set_hash(root: Path, commit: str, paths: Iterable[str]) -> str:
    entries = [
        {"path": path, "sha256": hashlib.sha256(_git_blob_bytes(root, commit, path)).hexdigest().upper()}
        for path in sorted(paths)
    ]
    return canonical_hash(entries)


def runtime_identity_manifest_entries(repository_root: Path | str) -> list[dict[str, str]]:
    """Return the immutable protected runtime file declaration for RUN1-R1."""

    root = Path(repository_root).resolve()
    return [
        {
            "path": path,
            "protectedCommit": commit,
            "protectedBlobSha256": hashlib.sha256(_git_blob_bytes(root, commit, path)).hexdigest().upper(),
            "runtimeRoot": runtime_root,
            "expectedRuntimePath": f"${{{runtime_root}}}/{path}",
        }
        for path, commit, runtime_root in PROTECTED_RUNTIME_FILES
    ]


def verify_runtime_checkout_against_protected_blobs(
    repository_root: Path | str,
    runtime_roots: Mapping[str, Path | str] | None = None,
) -> list[dict[str, str]]:
    """Require runtime checkout bytes to exactly match the protected Git blobs."""

    source_root = Path(repository_root).resolve()
    roots = {
        RUNTIME_ROOT_A: source_root,
        RUNTIME_ROOT_B: source_root,
        RUNTIME_ROOT_V2: source_root,
        **{name: Path(path).resolve() for name, path in (runtime_roots or {}).items()},
    }
    records: list[dict[str, str]] = []
    for entry in runtime_identity_manifest_entries(source_root):
        runtime_path = roots[entry["runtimeRoot"]] / entry["path"]
        if not runtime_path.is_file():
            raise RealRunValidationError(f"protected runtime file is missing: {entry['path']}")
        runtime_hash = hashlib.sha256(runtime_path.read_bytes()).hexdigest().upper()
        if runtime_hash != entry["protectedBlobSha256"]:
            raise RealRunValidationError(
                f"runtime checkout bytes differ from protected Git blob: {entry['path']}"
            )
        records.append({**entry, "runtimeSha256": runtime_hash})
    return records


def verify_runtime_module_paths(
    repository_root: Path | str,
    runtime_roots: Mapping[str, Path | str] | None = None,
    module_paths: Mapping[str, str | Path] | None = None,
) -> dict[str, str]:
    """Reject imports of protected runtime modules from any unexpected checkout."""

    root = Path(repository_root).resolve()
    resolved: dict[str, str] = {}
    roots = {
        RUNTIME_ROOT_A: root,
        RUNTIME_ROOT_B: root,
        RUNTIME_ROOT_V2: root,
        **{name: Path(path).resolve() for name, path in (runtime_roots or {}).items()},
    }
    for module_name, (relative_path, runtime_root, direct_file_import) in RUNTIME_MODULE_PATHS.items():
        if module_paths is not None:
            actual = Path(module_paths[module_name])
        else:
            # Each protected evaluator runs in its own clean-room checkout.
            # A subprocess proves the interpreter's imported path without
            # co-loading A and B under one package namespace.
            module_probe = (
                "import importlib.util; "
                f"spec = importlib.util.spec_from_file_location({module_name!r}, {str(roots[runtime_root] / relative_path)!r}); "
                "module = importlib.util.module_from_spec(spec); "
                "spec.loader.exec_module(module); "
                "print(module.__file__ or '')"
                if direct_file_import
                else "import importlib; "
                f"module = importlib.import_module({module_name!r}); "
                "print(module.__file__ or '')"
            )
            probe = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    module_probe,
                ],
                check=False,
                capture_output=True,
                cwd=roots[runtime_root],
                env={**os.environ, "PYTHONPATH": str(roots[runtime_root])},
            )
            if probe.returncode != 0:
                raise RealRunValidationError(
                    f"cannot import protected runtime module from {runtime_root}: {module_name}: "
                    f"{probe.stderr.decode('utf-8').strip()}"
                )
            actual = Path(probe.stdout.decode("utf-8").strip())
        expected = (roots[runtime_root] / relative_path).resolve()
        if actual.resolve() != expected:
            raise RealRunValidationError(
                f"protected runtime module resolves outside the expected checkout: {module_name}"
            )
        resolved[module_name] = str(actual.resolve())
    return resolved


def verify_protected_identities(root: Path | str) -> dict[str, str]:
    """Verify exact historical Git blob identities without touching evaluator files."""

    from ..comparator_ab.projection import PROJECTION_CONTRACT

    repository_root = Path(root).resolve()
    a_implementation = _source_set_hash(repository_root, A_IMPLEMENTATION_COMMIT, A_SOURCE_FILES)
    a_test = hashlib.sha256(_git_blob_bytes(repository_root, A_IMPLEMENTATION_COMMIT, "research_labs/candidate_c_reproduction/evaluator_a/test_evaluator_a.py")).hexdigest().upper()
    b_implementation = _source_set_hash(repository_root, B_IMPLEMENTATION_COMMIT, B_SOURCE_FILES)
    b_test = hashlib.sha256(_git_blob_bytes(repository_root, B_IMPLEMENTATION_COMMIT, "research_labs/candidate_c_reproduction/evaluator_b/test_evaluator_b.py")).hexdigest().upper()
    projection = hashlib.sha256(_git_blob_bytes(repository_root, V2_PROJECTION_COMMIT, "research_labs/candidate_c_reproduction/comparator_ab/projection.py")).hexdigest().upper()
    projection_test = hashlib.sha256(_git_blob_bytes(repository_root, V2_PROJECTION_COMMIT, "research_labs/candidate_c_reproduction/comparator_ab/test_comparator_ab.py")).hexdigest().upper()
    expected = {
        "aImplementationHash": A_IMPLEMENTATION_HASH,
        "aTestHash": A_TEST_HASH,
        "bImplementationHash": B_IMPLEMENTATION_HASH,
        "bTestHash": B_TEST_HASH,
        "v2ProjectionBlobHash": V2_PROJECTION_BLOB_HASH,
        "v2ProjectionTestHash": V2_PROJECTION_TEST_HASH,
        "v2SemanticProjectionHash": V2_SEMANTIC_PROJECTION_HASH,
    }
    actual = {
        "aImplementationHash": a_implementation,
        "aTestHash": a_test,
        "bImplementationHash": b_implementation,
        "bTestHash": b_test,
        "v2ProjectionBlobHash": projection,
        "v2ProjectionTestHash": projection_test,
        "v2SemanticProjectionHash": canonical_hash(PROJECTION_CONTRACT),
    }
    if actual != expected:
        raise RealRunValidationError(f"protected frozen identity mismatch: {actual!r}")
    return actual


def validate_adapter_equivalence(a_event: Mapping[str, Any], b_event: RealCandidateCEvent, snapshot_hash: str) -> None:
    """Prove adapter representation parity before any future evaluator invocation."""

    event_id = a_event.get("eventId")
    if event_id != b_event.event_id or a_event.get("eventHash") != b_event.event_hash:
        raise RealRunValidationError("A/B adapters do not refer to the same immutable event identity")
    roles = a_event.get("eventRoles")
    if not isinstance(roles, Mapping):
        raise RealRunValidationError("A adapter has no frozen event roles")
    if roles.get("sourceBody") != b_event.event_roles.get("sourceBody") or roles.get("targetBody") != b_event.event_roles.get("targetBody"):
        raise RealRunValidationError("A/B adapters do not preserve source and target bodies")
    a_transit = a_event.get("transitPositionAtExactUtc", {})
    a_natal = a_event.get("natalTargetPositionAtFrozenChartUtc", {})
    a_sun = a_event.get("sunPositionAtExactUtc", {})
    if not isinstance(a_transit, Mapping) or not isinstance(a_natal, Mapping) or not isinstance(a_sun, Mapping):
        raise RealRunValidationError("A adapter position fields are malformed")
    if a_transit.get("sign") != b_event.transit_position.get("sign") or a_natal.get("sign") != b_event.natal_target_position.get("sign") or a_sun.get("sign") != b_event.sun_position.get("sign"):
        raise RealRunValidationError("A/B adapters do not preserve source, target, and Sun signs")
    if snapshot_hash != "F5CC39224D61D01D74B1C43EF838D3EDCA7999E11CE878B06EE115BAA2802915":
        raise RealRunValidationError("adapter equivalence cannot proceed without the frozen astronomy snapshot identity")


def validate_row_keys(rows: Iterable[Mapping[str, Any]], expected: Iterable[Mapping[str, Any]]) -> None:
    """Reject missing, duplicate, and extra rows without projecting their values."""

    def key(row: Mapping[str, Any]) -> tuple[Any, ...]:
        provenance = row.get("provenance", {})
        operator = provenance.get("operatorId") if isinstance(provenance, Mapping) else None
        return (row.get("eventId"), row.get("sourceProfile"), row.get("componentId"), row.get("sourceContractId"), operator)

    actual_keys = [key(row) for row in rows]
    expected_keys = [key({**row, "provenance": {"operatorId": row.get("operatorId")}}) for row in expected]
    if len(actual_keys) != len(set(actual_keys)):
        raise RealRunValidationError("output rows contain duplicate canonical row keys")
    if set(actual_keys) != set(expected_keys):
        raise RealRunValidationError("output row-key universe has missing or extra keys")
