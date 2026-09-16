"""Load and validate the immutable P0/P0-R1 inputs for Evaluator A.

This module reads source contracts and frozen metadata only.  It deliberately
does not import the repository's historical operator implementation and it
does not expose the frozen event or population arrays to the evaluator.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .canonical import bytes_hash, canonical_hash, verify_self_hash


BASE_COMMIT = "35f6319aa0a984756c5b59bbd88c6ac8a0b5c7ea"
EXPERIMENT_ID = "R6_CANDIDATE_C_SOURCE_PROFILED_UNSIGNED_REPRODUCTION_AND_ABSTENTION"

P0_SNAPSHOT_PATH = "status/research/mo_r4a_candidate_c_p0_shared_astronomy_inputs_v1.json"
P0_BINDINGS_PATH = "status/research/mo_r4a_candidate_c_p0_component_input_bindings_v1.json"
P0_PREREGISTRATION_PATH = "status/research/mo_r4a_candidate_c_p0_preregistration_v1.json"
P0_MANIFEST_PATH = "status/research/mo_r4a_candidate_c_p0_population_manifest_v1.json"
S1_LEDGER_PATH = "configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s1r1_v1.json"
S2_SARAVALI_LEDGER_PATH = "configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s2r1_r1_saravali_adjudicated_v1.json"
UNKNOWN_REGISTRY_PATH = "configs/research/machine_interpretation/source_operators/source_operator_unresolved_dependencies_v1.json"

EXPECTED_P0_MANIFEST_HASH = "0B384FF0131BF19EFB842A3D4AEE4F7D1F9A923469281A65D6326B76CC39A092"
EXPECTED_P0_SNAPSHOT_HASH = "F5CC39224D61D01D74B1C43EF838D3EDCA7999E11CE878B06EE115BAA2802915"
EXPECTED_P0_BINDINGS_HASH = "D3219C1E6A8B7C791064F50E2CF23C211D4DE859AA73978B689C97E650DF5985"
EXPECTED_P0_PREREGISTRATION_HASH = "5A15DA738B4C349E3C251F0C000960955D955E370F51CC313E52F8D5851C1961"
EXPECTED_APPLICABILITY_HASH = "5C0E627294579FA9C41C5E19B791ED489FFDE2D2700D21AC7AE4C3530C91F4B4"
EXPECTED_ROW_KEY_UNIVERSE_HASH = "6AC975EE4DA32A3872399C68F514BA19E63FFAC5F565018A2DF15CECA27A4580"
EXPECTED_OUTPUT_SCHEMA_HASH = "DDBE5164FF93A8A1982891AD24CD40367C2A0F4F0FAA0CDAD0289A74D92A33BC"
EXPECTED_UNKNOWN_TAXONOMY_HASH = "1B1F6DFF937398F34E787CED256800BC6879D1ABCE989918A24B92DC8E7332B3"
EXPECTED_EXACT_POPULATION_HASH = "A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6"
EXPECTED_S1_LEDGER_BYTES_HASH = "4C7D0C4C1A366287A05DD70E9638A27585516240B24C3AEEBFA91889F22E86E8"
EXPECTED_S2_LEDGER_BYTES_HASH = "985DA1ECD2FF6631D9624541CEA27F69AC4620207EFE4C6CD79790263E3FAF01"
EXPECTED_UNKNOWN_REGISTRY_BYTES_HASH = "16292D6655B3BC4BEFEC2A7A39B91C4649F2AF01248020AA1629E7FF56A0D7C6"


class FrozenContractError(ValueError):
    """Raised when an immutable dependency is missing or has changed."""


@dataclass(frozen=True)
class FrozenContracts:
    """Validated contracts without the real event or population arrays."""

    snapshot_metadata: Mapping[str, Any]
    population_metadata: Mapping[str, Any]
    bindings: Mapping[str, Any]
    preregistration: Mapping[str, Any]
    operators: Mapping[str, Mapping[str, Any]]
    operator_artifacts: Mapping[str, Mapping[str, Any]]
    profile_contract_hashes: Mapping[str, str]
    allowed_unknown_codes: frozenset[str]
    expected_row_keys: tuple[Mapping[str, Any], ...]
    dependency_hashes: Mapping[str, str]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _read_json(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FrozenContractError(f"cannot load frozen JSON {relative_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FrozenContractError(f"frozen JSON must be an object: {relative_path}")
    return value


def _raw_hash(root: Path, relative_path: str) -> str:
    try:
        return bytes_hash((root / relative_path).read_bytes())
    except OSError as exc:
        raise FrozenContractError(f"cannot hash dependency {relative_path}: {exc}") from exc


def _hash_candidates(root: Path, relative_path: str) -> tuple[str, ...]:
    try:
        data = (root / relative_path).read_bytes()
    except OSError as exc:
        raise FrozenContractError(f"cannot hash dependency {relative_path}: {exc}") from exc
    exact = bytes_hash(data)
    normalized = bytes_hash(data.replace(b"\r\n", b"\n"))
    return tuple(dict.fromkeys((exact, normalized)))


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise FrozenContractError(f"{label} mismatch: {actual!r} != {expected!r}")


def _verify_artifact(root: Path, artifact: Mapping[str, Any], hashes: dict[str, str]) -> None:
    relative_path = artifact.get("path")
    expected = artifact.get("sha256")
    if not isinstance(relative_path, str) or not isinstance(expected, str):
        raise FrozenContractError("repository artifact must contain path and sha256")
    candidates = _hash_candidates(root, relative_path)
    if expected not in candidates:
        raise FrozenContractError(f"artifact hash for {relative_path} does not match recorded bytes: {candidates!r} != {expected!r}")
    hashes[relative_path] = expected


def _operator_index(ledger: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    operators = ledger.get("operators")
    if not isinstance(operators, list):
        raise FrozenContractError("source ledger operators must be a list")
    indexed: dict[str, Mapping[str, Any]] = {}
    for operator in operators:
        if not isinstance(operator, Mapping) or not isinstance(operator.get("operatorId"), str):
            raise FrozenContractError("source ledger contains an invalid operator")
        operator_id = str(operator["operatorId"])
        if operator_id in indexed:
            raise FrozenContractError(f"duplicate source operator: {operator_id}")
        indexed[operator_id] = operator
    return indexed


def load_frozen_contracts(root: Path | None = None) -> FrozenContracts:
    """Validate all P0-R1 identities before returning source rules.

    The snapshot and manifest are parsed only for self-hash and population
    identity validation.  Their event arrays are removed before this function
    returns, and the real-evaluation entry point is independently blocked.
    """

    project_root = (root or _project_root()).resolve()
    snapshot = _read_json(project_root, P0_SNAPSHOT_PATH)
    bindings = _read_json(project_root, P0_BINDINGS_PATH)
    preregistration = _read_json(project_root, P0_PREREGISTRATION_PATH)
    manifest = _read_json(project_root, P0_MANIFEST_PATH)
    s1_ledger = _read_json(project_root, S1_LEDGER_PATH)
    s2_ledger = _read_json(project_root, S2_SARAVALI_LEDGER_PATH)
    unknown_registry = _read_json(project_root, UNKNOWN_REGISTRY_PATH)

    verify_self_hash(snapshot, "sharedAstronomyInputSnapshotHash", EXPECTED_P0_SNAPSHOT_HASH)
    verify_self_hash(bindings, "componentInputBindingsHash", EXPECTED_P0_BINDINGS_HASH)
    verify_self_hash(preregistration, "p0PreregistrationHash", EXPECTED_P0_PREREGISTRATION_HASH)
    verify_self_hash(manifest, "populationManifestHash", EXPECTED_P0_MANIFEST_HASH)

    _require_equal(preregistration.get("experimentId"), EXPERIMENT_ID, "experiment ID")
    _require_equal(preregistration.get("requiredFreezeIdentities", {}).get("populationManifestHash"), EXPECTED_P0_MANIFEST_HASH, "preregistration manifest hash")
    _require_equal(preregistration.get("requiredFreezeIdentities", {}).get("exactPopulationHash"), EXPECTED_EXACT_POPULATION_HASH, "preregistration population hash")
    _require_equal(canonical_hash(manifest.get("population")), EXPECTED_EXACT_POPULATION_HASH, "population hash")
    _require_equal(len(snapshot.get("events", [])), 645, "shared snapshot event count")
    _require_equal(manifest.get("populationEventCount"), 645, "population manifest event count")
    _require_equal(snapshot.get("populationBinding", {}).get("populationEventCount"), 645, "snapshot population count")
    _require_equal(bindings.get("populationBinding", {}).get("populationEventCount"), 645, "binding population count")

    required = preregistration.get("requiredFreezeIdentities")
    if not isinstance(required, Mapping):
        raise FrozenContractError("preregistration requiredFreezeIdentities is missing")
    _require_equal(required.get("sharedAstronomyInputSnapshotHash"), EXPECTED_P0_SNAPSHOT_HASH, "required snapshot hash")
    _require_equal(required.get("componentInputBindingsHash"), EXPECTED_P0_BINDINGS_HASH, "required binding hash")
    _require_equal(required.get("applicabilityMatrixHash"), EXPECTED_APPLICABILITY_HASH, "required applicability hash")
    _require_equal(required.get("expectedRowKeyUniverseHash"), EXPECTED_ROW_KEY_UNIVERSE_HASH, "required row-key hash")
    _require_equal(required.get("outputSchemaHash"), EXPECTED_OUTPUT_SCHEMA_HASH, "required output schema hash")
    _require_equal(required.get("unknownTaxonomyHash"), EXPECTED_UNKNOWN_TAXONOMY_HASH, "required UNKNOWN taxonomy hash")
    _require_equal(canonical_hash(bindings.get("applicabilityMatrix")), EXPECTED_APPLICABILITY_HASH, "applicability matrix hash")

    output_cardinality = bindings.get("outputCardinality")
    if not isinstance(output_cardinality, Mapping):
        raise FrozenContractError("output cardinality block is missing")
    expected_row_keys_value = output_cardinality.get("expectedRowKeyUniverse")
    if not isinstance(expected_row_keys_value, list):
        raise FrozenContractError("expected row-key universe is missing")
    _require_equal(len(expected_row_keys_value), 5160, "expected row-key count")
    _require_equal(canonical_hash(expected_row_keys_value), EXPECTED_ROW_KEY_UNIVERSE_HASH, "expected row-key universe hash")
    row_key_tuples = [canonical_hash(item) for item in expected_row_keys_value]
    if len(set(row_key_tuples)) != len(row_key_tuples):
        raise FrozenContractError("expected row-key universe contains duplicates")

    taxonomy = preregistration.get("unknownTaxonomy")
    if not isinstance(taxonomy, Mapping):
        raise FrozenContractError("UNKNOWN taxonomy is missing")
    _require_equal(canonical_hash({key: value for key, value in taxonomy.items() if key != "taxonomyHash"}), EXPECTED_UNKNOWN_TAXONOMY_HASH, "UNKNOWN taxonomy hash")
    allowed_unknown_codes_value = taxonomy.get("allowedUnknownReasonCodes")
    if not isinstance(allowed_unknown_codes_value, list) or not all(isinstance(code, str) for code in allowed_unknown_codes_value):
        raise FrozenContractError("UNKNOWN taxonomy codes are invalid")
    if len(set(allowed_unknown_codes_value)) != len(allowed_unknown_codes_value):
        raise FrozenContractError("UNKNOWN taxonomy codes are not unique")
    _require_equal(unknown_registry.get("contract"), "MO_R4A_S1_SOURCE_OPERATOR_UNRESOLVED_DEPENDENCY_REGISTRY_V1", "UNKNOWN registry contract")

    dependency_hashes: dict[str, str] = {
        P0_SNAPSHOT_PATH: EXPECTED_P0_SNAPSHOT_HASH,
        P0_BINDINGS_PATH: EXPECTED_P0_BINDINGS_HASH,
        P0_PREREGISTRATION_PATH: EXPECTED_P0_PREREGISTRATION_HASH,
        P0_MANIFEST_PATH: EXPECTED_P0_MANIFEST_HASH,
        UNKNOWN_REGISTRY_PATH: EXPECTED_UNKNOWN_REGISTRY_BYTES_HASH,
    }
    if EXPECTED_UNKNOWN_REGISTRY_BYTES_HASH not in _hash_candidates(project_root, UNKNOWN_REGISTRY_PATH):
        raise FrozenContractError("UNKNOWN registry bytes hash does not match the checked-out artifact")
    if EXPECTED_S1_LEDGER_BYTES_HASH not in _hash_candidates(project_root, S1_LEDGER_PATH):
        raise FrozenContractError("S1 ledger bytes hash does not match the checked-out artifact")
    if EXPECTED_S2_LEDGER_BYTES_HASH not in _hash_candidates(project_root, S2_SARAVALI_LEDGER_PATH):
        raise FrozenContractError("S2 Saravali ledger bytes hash does not match the checked-out artifact")
    dependency_hashes[S1_LEDGER_PATH] = EXPECTED_S1_LEDGER_BYTES_HASH
    dependency_hashes[S2_SARAVALI_LEDGER_PATH] = EXPECTED_S2_LEDGER_BYTES_HASH

    profile_entries = preregistration.get("sourceProfiles")
    required_profile_hashes = required.get("sourceProfileContractHashes")
    if not isinstance(profile_entries, list) or not isinstance(required_profile_hashes, Mapping):
        raise FrozenContractError("source profile bindings are missing")
    profile_contract_hashes: dict[str, str] = {}
    for profile in profile_entries:
        if not isinstance(profile, Mapping):
            raise FrozenContractError("source profile entry is invalid")
        profile_id = profile.get("sourceProfileId")
        recorded_hash = profile.get("sourceProfileContractHash")
        if not isinstance(profile_id, str) or not isinstance(recorded_hash, str):
            raise FrozenContractError("source profile identity is invalid")
        _require_equal(recorded_hash, required_profile_hashes.get(profile_id), f"source profile hash for {profile_id}")
        profile_contract_hashes[profile_id] = recorded_hash
        artifacts = profile.get("repositoryArtifacts")
        if not isinstance(artifacts, list):
            raise FrozenContractError(f"source profile artifacts are missing: {profile_id}")
        for artifact in artifacts:
            if not isinstance(artifact, Mapping):
                raise FrozenContractError(f"source profile artifact is invalid: {profile_id}")
            _verify_artifact(project_root, artifact, dependency_hashes)

    profile_manifest_entries = manifest.get("sourceProfiles")
    if not isinstance(profile_manifest_entries, list):
        raise FrozenContractError("population manifest source profiles are missing")
    manifest_profiles = {item.get("sourceProfileId"): item.get("sourceProfileContractHash") for item in profile_manifest_entries if isinstance(item, Mapping)}
    _require_equal(manifest_profiles, profile_contract_hashes, "population/profile identity")

    s1_index = _operator_index(s1_ledger)
    s2_index = _operator_index(s2_ledger)
    _require_equal(s1_ledger.get("contract"), "MO_R4A_S1R1_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1", "S1 ledger contract")
    _require_equal(s2_ledger.get("contract"), "MO_R4A_S2R1_R1_SARAVALI_ADJUDICATED_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1", "S2 ledger contract")
    operators: dict[str, Mapping[str, Any]] = dict(s1_index)
    operator_artifacts: dict[str, Mapping[str, Any]] = {
        operator_id: {
            "path": S1_LEDGER_PATH,
            "sha256": EXPECTED_S1_LEDGER_BYTES_HASH,
            "contractId": s1_ledger.get("contract"),
            "ledgerId": s1_ledger.get("ledgerId"),
        }
        for operator_id in s1_index
    }
    saravali_natural_id = "SARAVALI_NATURAL_RELATIONSHIP_V1"
    if saravali_natural_id not in s2_index:
        raise FrozenContractError("S2 ledger does not contain Saravali natural relationship")
    operators[saravali_natural_id] = s2_index[saravali_natural_id]
    operator_artifacts[saravali_natural_id] = {
        "path": S2_SARAVALI_LEDGER_PATH,
        "sha256": EXPECTED_S2_LEDGER_BYTES_HASH,
        "contractId": s2_ledger.get("contract"),
        "ledgerId": s2_ledger.get("ledgerId"),
    }

    component_bindings = bindings.get("componentInputBindings")
    if not isinstance(component_bindings, list):
        raise FrozenContractError("component input bindings are missing")
    for binding in component_bindings:
        if not isinstance(binding, Mapping):
            raise FrozenContractError("component binding is invalid")
        for operator_id in binding.get("operatorIds", []):
            if operator_id not in operators:
                raise FrozenContractError(f"component binding references unknown operator: {operator_id}")
    c04 = next((item for item in component_bindings if item.get("componentId") == "C04_COMPOUND_RELATIONSHIP"), None)
    if not isinstance(c04, Mapping):
        raise FrozenContractError("C04 binding is missing")
    supporting = c04.get("supportingInputContract")
    if not isinstance(supporting, Mapping):
        raise FrozenContractError("C04 Saravali supporting contract is missing")
    _require_equal(supporting.get("operatorId"), saravali_natural_id, "C04 supporting operator")
    _require_equal(supporting.get("path"), S2_SARAVALI_LEDGER_PATH, "C04 supporting path")
    _require_equal(supporting.get("sha256"), EXPECTED_S2_LEDGER_BYTES_HASH, "C04 supporting hash")

    snapshot_metadata = dict(snapshot)
    snapshot_metadata.pop("events", None)
    population_metadata = dict(manifest)
    population_metadata.pop("population", None)
    return FrozenContracts(
        snapshot_metadata=snapshot_metadata,
        population_metadata=population_metadata,
        bindings=bindings,
        preregistration=preregistration,
        operators=operators,
        operator_artifacts=operator_artifacts,
        profile_contract_hashes=profile_contract_hashes,
        allowed_unknown_codes=frozenset(allowed_unknown_codes_value),
        expected_row_keys=tuple(dict(item) for item in expected_row_keys_value),
        dependency_hashes=dependency_hashes,
    )
