"""Verify the R3R2 dual canonical-Git and loader-compatible input bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping
from functools import lru_cache

from .canonical import canonical_hash, sha256_bytes


BUNDLE_RELATIVE = Path("research_inputs/candidate_c_run1_contract_bundle_v1")
STATUS_MANIFEST_RELATIVE = Path("status/research/mo_r4a_candidate_c_run1_r3r2_contract_input_bundle_manifest_v1.json")
APPROVED_TRANSFORM = "LF_TO_CRLF_RENDERING_V1"
ADMISSION_POLICY = "FROZEN_LOADER_REQUIRED_TEXT_ARTIFACT_EXACT_LF_TO_CRLF_HASH_MATCH_ONLY"
P0_PATHS = (
    "status/research/mo_r4a_candidate_c_p0_population_manifest_v1.json",
    "status/research/mo_r4a_candidate_c_p0_shared_astronomy_inputs_v1.json",
    "status/research/mo_r4a_candidate_c_p0_component_input_bindings_v1.json",
    "status/research/mo_r4a_candidate_c_p0_preregistration_v1.json",
)
LOADER_DECLARED_ARTIFACTS = {
    "configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s1r1_v1.json": "4C7D0C4C1A366287A05DD70E9638A27585516240B24C3AEEBFA91889F22E86E8",
    "configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s2r1_r1_saravali_adjudicated_v1.json": "985DA1ECD2FF6631D9624541CEA27F69AC4620207EFE4C6CD79790263E3FAF01",
    "configs/research/machine_interpretation/source_operators/source_operator_unresolved_dependencies_v1.json": "16292D6655B3BC4BEFEC2A7A39B91C4649F2AF01248020AA1629E7FF56A0D7C6",
}


class BundleVerificationError(ValueError):
    """Raised when a canonical source or compatibility rendering is not exact."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BundleVerificationError(f"cannot read bundle JSON: {path}") from exc
    if not isinstance(value, dict):
        raise BundleVerificationError(f"bundle JSON must be an object: {path}")
    return value


def lf_to_crlf_rendering(source: bytes) -> bytes:
    """Perform the sole authorized byte-level representation transform."""

    if b"\r" in source:
        raise BundleVerificationError("canonical LF source contains a CR byte")
    return source.replace(b"\n", b"\r\n")


def crlf_to_lf_rendering(rendered: bytes) -> bytes:
    if b"\r\n" not in rendered or rendered.replace(b"\r\n", b"").find(b"\r") >= 0:
        raise BundleVerificationError("loader-compatible rendering is not exclusively CRLF")
    return rendered.replace(b"\r\n", b"\n")


def _aggregate(files: list[Mapping[str, Any]], field: str) -> str:
    return canonical_hash([
        {"path": str(item["logicalPath"]), "sha256": str(item[field])}
        for item in sorted(files, key=lambda item: str(item["logicalPath"]))
    ])


def _git_blob(source_root: Path, blob_sha: str) -> bytes:
    result = subprocess.run(["git", "-C", str(source_root), "cat-file", "blob", blob_sha], capture_output=True)
    if result.returncode:
        raise BundleVerificationError(f"cannot resolve declared Git blob: {blob_sha}")
    return result.stdout


@lru_cache(maxsize=None)
def _source_commit_for_path(source_root: Path, logical_path: str) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "-C", str(source_root), "log", "--all", "--format=%H", "-1", "--", logical_path],
        capture_output=True, text=True, check=False,
    )
    commit = result.stdout.strip()
    if not commit:
        raise BundleVerificationError(f"required dependency has no committed provenance: {logical_path}")
    blob = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", f"{commit}:{logical_path}"],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    if not blob:
        raise BundleVerificationError(f"cannot resolve dependency Git blob: {logical_path}")
    return commit, blob


def discover_dependency_inventory(root: Path | str | None = None) -> list[dict[str, Any]]:
    """Enumerate every A/B-declared frozen source input before materialization."""

    source_root = (Path(root) if root is not None else Path(__file__).resolve().parents[3]).resolve()
    prereg = json.loads(_git_blob(source_root, _source_commit_for_path(source_root, P0_PATHS[3])[1]).decode("utf-8"))
    bindings = json.loads(_git_blob(source_root, _source_commit_for_path(source_root, P0_PATHS[2])[1]).decode("utf-8"))
    expected: dict[str, tuple[str, set[str]]] = {
        path: ("", {"A.contract_loader", "B.contract_loader"}) for path in P0_PATHS
    }
    for path, expected_sha in LOADER_DECLARED_ARTIFACTS.items():
        expected[path] = (expected_sha, {"A.contract_loader.constant", "B.contract_loader.constant"})
    for profile in prereg.get("sourceProfiles", []):
        if not isinstance(profile, Mapping):
            raise BundleVerificationError("invalid frozen source profile declaration")
        profile_id = str(profile.get("sourceProfileId", "UNKNOWN"))
        for artifact in profile.get("repositoryArtifacts", []):
            if not isinstance(artifact, Mapping) or not isinstance(artifact.get("path"), str) or not isinstance(artifact.get("sha256"), str):
                raise BundleVerificationError("invalid frozen repository artifact declaration")
            path = str(artifact["path"])
            value, declarations = expected.setdefault(path, (str(artifact["sha256"]), set()))
            if value and value != artifact["sha256"]:
                raise BundleVerificationError(f"conflicting frozen expected hashes for {path}")
            expected[path] = (str(artifact["sha256"]), declarations | {f"preregistration.sourceProfiles[{profile_id}].repositoryArtifacts"})
    for binding in bindings.get("componentInputBindings", []):
        if not isinstance(binding, Mapping):
            continue
        supporting = binding.get("supportingInputContract")
        if isinstance(supporting, Mapping) and isinstance(supporting.get("path"), str) and isinstance(supporting.get("sha256"), str):
            path = str(supporting["path"])
            value, declarations = expected.setdefault(path, (str(supporting["sha256"]), set()))
            if value and value != supporting["sha256"]:
                raise BundleVerificationError(f"conflicting frozen expected hashes for {path}")
            expected[path] = (str(supporting["sha256"]), declarations | {f"componentInputBindings[{binding.get('componentId')}].supportingInputContract"})
    inventory: list[dict[str, Any]] = []
    for path, (historical, declarations) in sorted(expected.items()):
        commit, blob = _source_commit_for_path(source_root, path)
        canonical = _git_blob(source_root, blob)
        canonical_sha = sha256_bytes(canonical)
        if not historical:
            # P0 files are semantic/self-hash identities, not raw loader-byte declarations.
            historical = canonical_sha
        candidate = lf_to_crlf_rendering(canonical) if b"\r" not in canonical and b"\n" in canonical else b""
        if canonical_sha == historical:
            disposition = "IDENTITY_GIT_BYTES"
        elif candidate and sha256_bytes(candidate) == historical:
            disposition = APPROVED_TRANSFORM
        else:
            disposition = "BLOCKED_REPRESENTATION_MISMATCH"
        inventory.append({
            "logicalPath": path, "requiredByA": True, "requiredByB": True,
            "declarationSources": sorted(declarations), "historicalExpectedSha256": historical,
            "sourceCommit": commit, "sourceGitPath": path, "sourceGitBlobSha": blob,
            "canonicalGitBlobSha256": canonical_sha, "canonicalContainsCr": b"\r" in canonical,
            "canonicalLfCount": canonical.count(b"\n"), "candidateLfToCrlfSha256": sha256_bytes(candidate) if candidate else None,
            "representationDisposition": disposition,
        })
    return inventory


def materialize_bundle(root: Path | str | None = None) -> dict[str, Any]:
    """Materialize both bundle views only from discovered committed Git blobs."""

    source_root = (Path(root) if root is not None else Path(__file__).resolve().parents[3]).resolve()
    inventory = discover_dependency_inventory(source_root)
    blocked = [item["logicalPath"] for item in inventory if item["representationDisposition"] == "BLOCKED_REPRESENTATION_MISMATCH"]
    if blocked:
        raise BundleVerificationError(f"frozen dependency mismatch is not an admitted LF-to-CRLF rendering: {blocked}")
    bundle_root = source_root / BUNDLE_RELATIVE
    files: list[dict[str, Any]] = []
    for item in inventory:
        path = item["logicalPath"]
        canonical = _git_blob(source_root, item["sourceGitBlobSha"])
        loader = lf_to_crlf_rendering(canonical) if item["representationDisposition"] == APPROVED_TRANSFORM else canonical
        canonical_path = bundle_root / "canonical_git" / path
        loader_path = bundle_root / "loader_view" / path
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        loader_path.parent.mkdir(parents=True, exist_ok=True)
        canonical_path.write_bytes(canonical)
        loader_path.write_bytes(loader)
        transformed = item["representationDisposition"] == APPROVED_TRANSFORM
        files.append({
            "logicalPath": path, "requiredBy": ["FROZEN_A", "FROZEN_B"], "declarationSources": item["declarationSources"],
            "canonicalGitRelativePath": str(Path("canonical_git") / path).replace("\\\\", "/"),
            "loaderViewRelativePath": str(Path("loader_view") / path).replace("\\\\", "/"),
            "canonicalGit": {"sourceCommit": item["sourceCommit"], "sourceGitPath": path, "sourceGitBlobSha": item["sourceGitBlobSha"], "sha256": item["canonicalGitBlobSha256"], "lineEndingForm": "LF"},
            "loaderView": {"sha256": sha256_bytes(loader), "transformId": item["representationDisposition"], "lineEndingForm": "CRLF" if transformed else "LF"},
            "historicalFrozenExpectedSha256": item["historicalExpectedSha256"],
            "roundTrip": {"exact": crlf_to_lf_rendering(loader) == canonical if transformed else True, "sha256": sha256_bytes(crlf_to_lf_rendering(loader)) if transformed else sha256_bytes(canonical)},
            "renderedBytesAreGitBlob": not transformed, "semanticContentChanged": False,
            "admissionPolicySatisfied": transformed or item["representationDisposition"] == "IDENTITY_GIT_BYTES",
        })
    files.sort(key=lambda item: item["logicalPath"])
    rendered = [item["logicalPath"] for item in files if item["loaderView"]["transformId"] == APPROVED_TRANSFORM]
    manifest: dict[str, Any] = {
        "schemaVersion": "CANDIDATE_C_CONTRACT_INPUT_BUNDLE_R3R2A_MANIFEST_V1", "milestone": "MO-R4A-CANDIDATE-C-RUN1-R3R2A-BOUNDED-LOADER-RENDERING-ADMISSION-AND-PRODUCTION-PATH-RESUME",
        "bundleContractId": "CANDIDATE_C_CONTRACT_INPUT_BUNDLE_V1", "admissionPolicy": ADMISSION_POLICY,
        "fileCount": len(files), "files": files, "renderedPathCount": len(rendered), "renderedPaths": rendered,
        "renderedPathsHash": canonical_hash(rendered),
        "dependencyInventory": inventory, "dependencyInventoryHash": canonical_hash(inventory),
        "canonicalGitBundleAggregateHash": canonical_hash([{"path": item["logicalPath"], "sha256": item["canonicalGit"]["sha256"]} for item in files]),
        "loaderViewBundleAggregateHash": canonical_hash([{"path": item["logicalPath"], "sha256": item["loaderView"]["sha256"]} for item in files]),
    }
    manifest["bundleManifestHash"] = canonical_hash(manifest)
    (bundle_root / "manifest.json").write_bytes(json.dumps(manifest, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    status_path = source_root / STATUS_MANIFEST_RELATIVE
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_bytes(json.dumps(manifest, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return {"bundleRoot": str(bundle_root), "loaderView": str(bundle_root / "loader_view"), **manifest}


def verify_bundle(root: Path | str | None = None) -> dict[str, Any]:
    """Verify both byte views and every approved representation relation."""

    source_root = Path(root) if root is not None else Path(__file__).resolve().parents[3]
    source_root = source_root.resolve()
    bundle_root = source_root / BUNDLE_RELATIVE
    manifest = _read_json(bundle_root / "manifest.json")
    status_manifest = _read_json(source_root / STATUS_MANIFEST_RELATIVE)
    if manifest != status_manifest:
        raise BundleVerificationError("bundle and status manifests do not match exactly")
    declared_hash = manifest.get("bundleManifestHash")
    if not isinstance(declared_hash, str) or canonical_hash({k: v for k, v in manifest.items() if k != "bundleManifestHash"}) != declared_hash:
        raise BundleVerificationError("bundle manifest self-hash mismatch")
    files = manifest.get("files")
    inventory = manifest.get("dependencyInventory")
    if not isinstance(files, list) or not files or not isinstance(inventory, list):
        raise BundleVerificationError("bundle file list is missing")
    if canonical_hash(inventory) != manifest.get("dependencyInventoryHash"):
        raise BundleVerificationError("dependency inventory hash mismatch")
    if any(item.get("representationDisposition") == "BLOCKED_REPRESENTATION_MISMATCH" for item in inventory if isinstance(item, Mapping)):
        raise BundleVerificationError("bundle includes a blocked dependency representation")
    rendered: list[str] = []
    for item in files:
        if not isinstance(item, Mapping):
            raise BundleVerificationError("bundle file entry is malformed")
        logical = str(item.get("logicalPath", ""))
        canonical = bundle_root / str(item.get("canonicalGitRelativePath", ""))
        loader = bundle_root / str(item.get("loaderViewRelativePath", ""))
        canonical_record = item.get("canonicalGit", {})
        loader_record = item.get("loaderView", {})
        source_bytes = _git_blob(source_root, str(canonical_record.get("sourceGitBlobSha", "")))
        if not logical or not canonical.is_file() or not loader.is_file():
            raise BundleVerificationError(f"bundle path is incomplete: {logical}")
        if canonical.read_bytes() != source_bytes:
            raise BundleVerificationError(f"canonical view is not exact Git bytes: {logical}")
        if sha256_bytes(source_bytes) != canonical_record.get("sha256"):
            raise BundleVerificationError(f"canonical Git SHA mismatch: {logical}")
        loader_bytes = loader.read_bytes()
        if sha256_bytes(loader_bytes) != loader_record.get("sha256"):
            raise BundleVerificationError(f"loader view SHA mismatch: {logical}")
        transformed = loader_record.get("transformId") == APPROVED_TRANSFORM
        if transformed:
            rendered.append(logical)
            expected = item.get("historicalFrozenExpectedSha256")
            if sha256_bytes(lf_to_crlf_rendering(source_bytes)) != expected or sha256_bytes(loader_bytes) != expected:
                raise BundleVerificationError(f"loader rendering does not match historical expected bytes: {logical}")
            if crlf_to_lf_rendering(loader_bytes) != source_bytes:
                raise BundleVerificationError(f"loader rendering inverse does not recover Git bytes: {logical}")
            if item.get("renderedBytesAreGitBlob") is not False or item.get("semanticContentChanged") is not False:
                raise BundleVerificationError(f"transformed representation is incorrectly classified: {logical}")
        elif loader_bytes != source_bytes or item.get("renderedBytesAreGitBlob") is not True:
            raise BundleVerificationError(f"identity loader view is not exact canonical bytes: {logical}")
    if rendered != manifest.get("renderedPaths") or len(rendered) != manifest.get("renderedPathCount") or canonical_hash(rendered) != manifest.get("renderedPathsHash"):
        raise BundleVerificationError("rendered path inventory is not sorted and frozen")
    if canonical_hash([{"path": item["logicalPath"], "sha256": item["canonicalGit"]["sha256"]} for item in files]) != manifest.get("canonicalGitBundleAggregateHash"):
        raise BundleVerificationError("canonical bundle aggregate mismatch")
    if canonical_hash([{"path": item["logicalPath"], "sha256": item["loaderView"]["sha256"]} for item in files]) != manifest.get("loaderViewBundleAggregateHash"):
        raise BundleVerificationError("loader-view bundle aggregate mismatch")
    return {"bundleRoot": str(bundle_root), "loaderView": str(bundle_root / "loader_view"), **manifest}


def verify_frozen_loader_acceptance(bundle: Mapping[str, Any], runtime_roots: Mapping[str, Path | str]) -> dict[str, bool]:
    """Run each frozen loader in a clean interpreter against the loader view."""

    loader_view = str(bundle["loaderView"])
    targets = {
        "EVALUATOR_A": "research_labs.candidate_c_reproduction.evaluator_a.contract_loader",
        "EVALUATOR_B": "research_labs.candidate_c_reproduction.evaluator_b.contract_loader",
    }
    results: dict[str, bool] = {}
    for role, module in targets.items():
        root = Path(runtime_roots[role]).resolve()
        probe = (
            "import importlib,sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
            "m=importlib.import_module(sys.argv[2]); m.load_frozen_contracts(Path(sys.argv[3])); print('ACCEPTED')"
        )
        completed = subprocess.run([sys.executable, "-I", "-B", "-c", probe, str(root), module, loader_view], capture_output=True)
        if completed.returncode or completed.stdout.strip() != b"ACCEPTED":
            raise BundleVerificationError(
                f"{role} frozen loader rejected loader_view: {completed.stderr.decode('utf-8', errors='replace').strip()}"
            )
        results[role] = True
    return results
