"""Load and validate the frozen Candidate C P0-R1 contracts for Evaluator B."""

from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .canonical import canonical_hash, canonical_hash_without_field, sha256_bytes, sha256_file
from .models import FrozenContracts


class FrozenContractError(RuntimeError):
    """Raised when a frozen Candidate C dependency does not validate."""


BASELINE_COMMIT = "35f6319aa0a984756c5b59bbd88c6ac8a0b5c7ea"

_MANIFEST_PATH = Path("status/research/mo_r4a_candidate_c_p0_population_manifest_v1.json")
_SNAPSHOT_PATH = Path("status/research/mo_r4a_candidate_c_p0_shared_astronomy_inputs_v1.json")
_BINDINGS_PATH = Path("status/research/mo_r4a_candidate_c_p0_component_input_bindings_v1.json")
_PREREG_PATH = Path("status/research/mo_r4a_candidate_c_p0_preregistration_v1.json")
_S1_PATH = Path("configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s1r1_v1.json")
_S2_PATH = Path("configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s2r1_r1_saravali_adjudicated_v1.json")
_UNRESOLVED_PATH = Path("configs/research/machine_interpretation/source_operators/source_operator_unresolved_dependencies_v1.json")

_RAW_HASHES = {
    _S1_PATH: "4C7D0C4C1A366287A05DD70E9638A27585516240B24C3AEEBFA91889F22E86E8",
    _S2_PATH: "985DA1ECD2FF6631D9624541CEA27F69AC4620207EFE4C6CD79790263E3FAF01",
    _UNRESOLVED_PATH: "16292D6655B3BC4BEFEC2A7A39B91C4649F2AF01248020AA1629E7FF56A0D7C6",
}


def _read_json(root: Path, relative_path: Path) -> dict[str, Any]:
    path = root / relative_path
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FrozenContractError(f"cannot load frozen JSON {relative_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FrozenContractError(f"frozen JSON {relative_path} must contain an object")
    return value


def _require_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise FrozenContractError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _validate_self_hash(label: str, document: dict[str, Any], field: str) -> None:
    declared = document.get(field)
    if not isinstance(declared, str):
        raise FrozenContractError(f"{label} has no {field}")
    actual = canonical_hash_without_field(document, field)
    _require_equal(f"{label}.{field}", actual, declared)


def _validate_raw_hash(root: Path, relative_path: Path, expected: str) -> None:
    path = root / relative_path
    if not path.is_file():
        raise FrozenContractError(f"missing frozen source artifact: {relative_path}")
    actual = sha256_file(path)
    if actual == expected:
        return
    normalized = sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    if normalized == expected:
        return
    _require_equal(f"{relative_path} raw SHA-256", actual, expected)


def _sanitized_copy(document: dict[str, Any], omitted_key: str) -> dict[str, Any]:
    result = copy.deepcopy(document)
    result.pop(omitted_key, None)
    return result


def _validate_artifact_declarations(root: Path, preregistration: dict[str, Any], bindings: dict[str, Any]) -> None:
    declarations: dict[Path, str] = dict(_RAW_HASHES)
    for profile in preregistration.get("sourceProfiles", []):
        for artifact in profile.get("repositoryArtifacts", []):
            path = Path(artifact["path"])
            declarations[path] = artifact["sha256"]
    supporting = []
    for component in bindings.get("componentInputBindings", []):
        contract = component.get("supportingInputContract")
        if contract:
            supporting.append(contract)
    for contract in supporting:
        declarations[Path(contract["path"])] = contract["sha256"]
    for relative_path, expected in declarations.items():
        _validate_raw_hash(root, relative_path, expected)


def _validate_population_identity(manifest: dict[str, Any]) -> None:
    population = manifest.get("population")
    if not isinstance(population, list):
        raise FrozenContractError("population manifest population must be an array")
    _require_equal("populationEventCount", manifest.get("populationEventCount"), 645)
    _require_equal("population array length", len(population), 645)
    _require_equal("exactPopulationHash", canonical_hash(population), manifest.get("exactPopulationHash"))


def _validate_expected_row_identity(bindings: dict[str, Any]) -> None:
    cardinality = bindings.get("outputCardinality", {})
    row_keys = cardinality.get("expectedRowKeyUniverse")
    if not isinstance(row_keys, list):
        raise FrozenContractError("expected row-key universe must be an array")
    _require_equal("expected row-key count", len(row_keys), 5160)
    _require_equal(
        "expectedRowKeyUniverseHash",
        canonical_hash(row_keys),
        cardinality.get("expectedRowKeyUniverseHash"),
    )


def _validate_contracts(root: Path) -> FrozenContracts:
    manifest = _read_json(root, _MANIFEST_PATH)
    snapshot = _read_json(root, _SNAPSHOT_PATH)
    bindings = _read_json(root, _BINDINGS_PATH)
    preregistration = _read_json(root, _PREREG_PATH)
    s1 = _read_json(root, _S1_PATH)
    s2 = _read_json(root, _S2_PATH)
    unresolved = _read_json(root, _UNRESOLVED_PATH)

    _validate_self_hash("population manifest", manifest, "populationManifestHash")
    _validate_self_hash("shared astronomy snapshot", snapshot, "sharedAstronomyInputSnapshotHash")
    _validate_self_hash("component bindings", bindings, "componentInputBindingsHash")
    _validate_self_hash("preregistration", preregistration, "p0PreregistrationHash")
    _validate_population_identity(manifest)
    _require_equal("shared snapshot event count", len(snapshot.get("events", [])), 645)
    _require_equal("snapshot population hash", snapshot["populationBinding"]["exactPopulationHash"], manifest["exactPopulationHash"])
    _require_equal("snapshot manifest hash", snapshot["populationBinding"]["populationManifestHash"], manifest["populationManifestHash"])
    _require_equal("snapshot hash", snapshot["sharedAstronomyInputSnapshotHash"], "F5CC39224D61D01D74B1C43EF838D3EDCA7999E11CE878B06EE115BAA2802915")
    _require_equal("manifest hash", manifest["populationManifestHash"], "0B384FF0131BF19EFB842A3D4AEE4F7D1F9A923469281A65D6326B76CC39A092")
    _require_equal("population hash", manifest["exactPopulationHash"], "A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6")
    _require_equal("shared snapshot event array length", len(snapshot["events"]), 645)

    _require_equal("bindings hash", bindings["componentInputBindingsHash"], "D3219C1E6A8B7C791064F50E2CF23C211D4DE859AA73978B689C97E650DF5985")
    _require_equal("applicability matrix hash", canonical_hash(bindings["applicabilityMatrix"]), "5C0E627294579FA9C41C5E19B791ED489FFDE2D2700D21AC7AE4C3530C91F4B4")
    _require_equal("binding unknown taxonomy identity", bindings["unknownTaxonomyDisposition"]["taxonomyHash"], "1B1F6DFF937398F34E787CED256800BC6879D1ABCE989918A24B92DC8E7332B3")
    _validate_expected_row_identity(bindings)
    _require_equal("expected row count", bindings["outputCardinality"]["expectedRowCount"], 5160)
    _require_equal("row templates per event", bindings["outputCardinality"]["rowTemplatesPerEvent"], 8)
    _require_equal("output schema hash", canonical_hash_without_field(preregistration["outputSchema"], "schemaHash"), "DDBE5164FF93A8A1982891AD24CD40367C2A0F4F0FAA0CDAD0289A74D92A33BC")
    _require_equal("preregistration hash", preregistration["p0PreregistrationHash"], "5A15DA738B4C349E3C251F0C000960955D955E370F51CC313E52F8D5851C1961")
    _require_equal("unknown taxonomy hash", canonical_hash_without_field(preregistration["unknownTaxonomy"], "taxonomyHash"), "1B1F6DFF937398F34E787CED256800BC6879D1ABCE989918A24B92DC8E7332B3")
    _require_equal("preregistration population manifest identity", preregistration["requiredFreezeIdentities"]["populationManifestHash"], manifest["populationManifestHash"])
    _require_equal("preregistration population identity", preregistration["requiredFreezeIdentities"]["exactPopulationHash"], manifest["exactPopulationHash"])
    _require_equal("preregistration snapshot identity", preregistration["requiredFreezeIdentities"]["sharedAstronomyInputSnapshotHash"], snapshot["sharedAstronomyInputSnapshotHash"])
    _require_equal("preregistration bindings identity", preregistration["requiredFreezeIdentities"]["componentInputBindingsHash"], bindings["componentInputBindingsHash"])
    _require_equal("preregistration applicability identity", preregistration["requiredFreezeIdentities"]["applicabilityMatrixHash"], bindings["applicabilityMatrixHash"] if "applicabilityMatrixHash" in bindings else canonical_hash(bindings["applicabilityMatrix"]))
    _validate_artifact_declarations(root, preregistration, bindings)

    _require_equal("S1 ledger bytes", sha256_file(root / _S1_PATH), _RAW_HASHES[_S1_PATH])
    _require_equal("S2 ledger bytes", sha256_file(root / _S2_PATH), _RAW_HASHES[_S2_PATH])
    _require_equal("unresolved registry bytes", sha256_file(root / _UNRESOLVED_PATH), _RAW_HASHES[_UNRESOLVED_PATH])
    _require_equal("unresolved registry contract", unresolved.get("contract"), "MO_R4A_S1_SOURCE_OPERATOR_UNRESOLVED_DEPENDENCY_REGISTRY_V1")
    _require_equal("unresolved registry execution lock", unresolved["guardrails"]["executionAllowed"], False)
    if not isinstance(s1.get("operators"), list) or not isinstance(s2.get("operators"), list):
        raise FrozenContractError("source ledgers must contain operator arrays")
    operators: dict[str, dict[str, Any]] = {}
    operator_artifacts: dict[str, str] = {}
    for operator in s1["operators"]:
        operator_id = operator.get("operatorId")
        if isinstance(operator_id, str):
            operators[operator_id] = operator
            operator_artifacts[operator_id] = _S1_PATH.as_posix()
    for operator in s2["operators"]:
        operator_id = operator.get("operatorId")
        if operator_id == "SARAVALI_NATURAL_RELATIONSHIP_V1":
            operators[operator_id] = operator
            operator_artifacts[operator_id] = _S2_PATH.as_posix()

    component_specs = {item["componentId"]: item for item in bindings["componentInputBindings"]}
    for component_id, component in component_specs.items():
        for operator_id in component.get("operatorIds", []):
            if operator_id not in operators:
                raise FrozenContractError(f"missing operator bound to {component_id}: {operator_id}")
    unknown = frozenset(bindings["unknownTaxonomyDisposition"]["allowedUnknownReasonCodes"])
    source_profiles = {profile["sourceProfileId"]: profile for profile in preregistration["sourceProfiles"]}
    if set(source_profiles) != {
        "TRAILOKYA_DIPIKA_1972",
        "BJ_SARAVALI_CROSS_TEXT_CONTRACTS_AS_SEPARATE_PROFILES",
    }:
        raise FrozenContractError("unexpected Candidate C source profile set")
    for profile_id, expected_hash in preregistration["requiredFreezeIdentities"]["sourceProfileContractHashes"].items():
        _require_equal(
            f"source profile contract hash for {profile_id}",
            source_profiles[profile_id]["sourceProfileContractHash"],
            expected_hash,
        )

    sanitized_bindings = _sanitized_copy(bindings, "expectedRowKeyUniverse")
    sanitized_bindings["outputCardinality"].pop("expectedRowKeyUniverse", None)
    return FrozenContracts(
        repository_root=str(root),
        preregistration=copy.deepcopy(preregistration),
        bindings=sanitized_bindings,
        shared_astronomy_metadata=_sanitized_copy(snapshot, "events"),
        population_manifest_metadata=_sanitized_copy(manifest, "population"),
        source_profiles=copy.deepcopy(source_profiles),
        component_specs=copy.deepcopy(component_specs),
        operators=copy.deepcopy(operators),
        operator_artifacts=copy.deepcopy(operator_artifacts),
        unknown_reason_codes=unknown,
        expected_row_count=5160,
        row_templates_per_event=8,
        real_frozen_population_read=True,
        real_frozen_population_artifact_read_for_validation=True,
        real_frozen_population_exposed_to_evaluator=False,
        real_frozen_population_arrays_exposed_to_evaluation_path=False,
        real_frozen_population_evaluated=False,
        real_candidate_c_output_produced=False,
        real_candidate_c_output_inspected=False,
        real_candidate_c_output_row_count=0,
        execution_allowed=False,
    )


@lru_cache(maxsize=4)
def _cached_contracts(root_string: str) -> FrozenContracts:
    return _validate_contracts(Path(root_string))


def load_frozen_contracts(repository_root: str | Path | None = None) -> FrozenContracts:
    """Validate frozen dependencies and return an array-free contract object."""

    root = Path(repository_root) if repository_root is not None else Path(__file__).resolve().parents[3]
    root = root.resolve()
    return _cached_contracts(str(root))
