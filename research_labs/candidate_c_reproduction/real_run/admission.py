"""Truthful admission and identity checks for the frozen Candidate C population."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .canonical import canonical_hash, self_hash


REAL_ADMISSION_MARKER = "REAL_FROZEN_CANDIDATE_C_P0_R1"
EXPECTED_EVENT_COUNT = 645
EXPECTED_ROW_COUNT = 5160
EXPECTED_POPULATION_HASH = "A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6"
EXPECTED_MANIFEST_HASH = "0B384FF0131BF19EFB842A3D4AEE4F7D1F9A923469281A65D6326B76CC39A092"
EXPECTED_SNAPSHOT_HASH = "F5CC39224D61D01D74B1C43EF838D3EDCA7999E11CE878B06EE115BAA2802915"
EXPECTED_BINDINGS_HASH = "D3219C1E6A8B7C791064F50E2CF23C211D4DE859AA73978B689C97E650DF5985"
EXPECTED_ROW_KEY_HASH = "6AC975EE4DA32A3872399C68F514BA19E63FFAC5F565018A2DF15CECA27A4580"

MANIFEST_PATH = Path("status/research/mo_r4a_candidate_c_p0_population_manifest_v1.json")
SNAPSHOT_PATH = Path("status/research/mo_r4a_candidate_c_p0_shared_astronomy_inputs_v1.json")
BINDINGS_PATH = Path("status/research/mo_r4a_candidate_c_p0_component_input_bindings_v1.json")


class RealPopulationAdmissionError(ValueError):
    """Raised when a frozen RUN1 input identity or shape is not admissible."""


@dataclass(frozen=True)
class AdmittedRealPopulation:
    """Validated frozen inputs, intentionally unevaluated by this layer."""

    events: tuple[Mapping[str, Any], ...]
    manifest: Mapping[str, Any]
    snapshot: Mapping[str, Any]
    bindings: Mapping[str, Any]


def _read_json(root: Path, relative_path: Path) -> dict[str, Any]:
    try:
        value = json.loads((root / relative_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RealPopulationAdmissionError(f"cannot load frozen RUN1 input {relative_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RealPopulationAdmissionError(f"frozen RUN1 input is not an object: {relative_path}")
    return value


def _require(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise RealPopulationAdmissionError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _identity(event: Mapping[str, Any]) -> tuple[str, str]:
    event_id = event.get("eventId")
    event_hash = event.get("eventHash")
    if not isinstance(event_id, str) or not event_id or not isinstance(event_hash, str) or not event_hash:
        raise RealPopulationAdmissionError("frozen event has no usable event identity")
    return event_id, event_hash


def _validate_event_pair(manifest_event: Mapping[str, Any], snapshot_event: Mapping[str, Any]) -> None:
    _require("event identity", _identity(snapshot_event), _identity(manifest_event))
    for field in ("sideIdentity", "exactUtc"):
        _require(f"event {field}", snapshot_event.get(field), manifest_event.get(field))
    roles = snapshot_event.get("eventRoles")
    if not isinstance(roles, Mapping):
        raise RealPopulationAdmissionError("snapshot event has no roles")
    _require("transit role", roles.get("sourceBody"), manifest_event.get("transitBody"))
    _require("natal role", roles.get("targetBody"), manifest_event.get("natalTarget"))
    if roles.get("sourceRole") != "TRANSIT_BODY" or roles.get("targetRole") != "NATAL_TARGET":
        raise RealPopulationAdmissionError("snapshot event role semantics are not frozen Candidate C roles")


def _validate_snapshot_event(event: Mapping[str, Any]) -> None:
    required = (
        "eventId", "eventHash", "sideIdentity", "chartIdentity", "exactUtc", "eventRoles",
        "transitPositionAtExactUtc", "natalTargetPositionAtFrozenChartUtc", "sunPositionAtExactUtc",
        "moonPositionAtExactUtc", "planetaryPositionsAtExactUtc",
    )
    missing = [field for field in required if field not in event]
    if missing:
        raise RealPopulationAdmissionError(f"snapshot event is missing required fields: {missing}")
    _identity(event)
    positions = event["planetaryPositionsAtExactUtc"]
    if not isinstance(positions, list) or len(positions) != 9:
        raise RealPopulationAdmissionError("snapshot event must retain the frozen nine-body positions")


def load_and_validate_real_population(root: Path | str | None = None) -> AdmittedRealPopulation:
    """Read real frozen inputs for identity, structure, and adapter validation only."""

    repository_root = Path(root) if root is not None else Path(__file__).resolve().parents[3]
    repository_root = repository_root.resolve()
    manifest = _read_json(repository_root, MANIFEST_PATH)
    snapshot = _read_json(repository_root, SNAPSHOT_PATH)
    bindings = _read_json(repository_root, BINDINGS_PATH)

    _require("population manifest self-hash", self_hash(manifest, "populationManifestHash"), EXPECTED_MANIFEST_HASH)
    _require("shared astronomy snapshot self-hash", self_hash(snapshot, "sharedAstronomyInputSnapshotHash"), EXPECTED_SNAPSHOT_HASH)
    _require("component bindings self-hash", self_hash(bindings, "componentInputBindingsHash"), EXPECTED_BINDINGS_HASH)
    population = manifest.get("population")
    events = snapshot.get("events")
    if not isinstance(population, list) or not isinstance(events, list):
        raise RealPopulationAdmissionError("frozen manifest and snapshot arrays are required")
    _require("population event count", len(population), EXPECTED_EVENT_COUNT)
    _require("snapshot event count", len(events), EXPECTED_EVENT_COUNT)
    _require("manifest declared event count", manifest.get("populationEventCount"), EXPECTED_EVENT_COUNT)
    _require("population hash", canonical_hash(population), EXPECTED_POPULATION_HASH)
    _require("manifest declared population hash", manifest.get("exactPopulationHash"), EXPECTED_POPULATION_HASH)
    _require("snapshot population hash", snapshot.get("populationBinding", {}).get("exactPopulationHash"), EXPECTED_POPULATION_HASH)
    _require("snapshot manifest hash", snapshot.get("populationBinding", {}).get("populationManifestHash"), EXPECTED_MANIFEST_HASH)
    _require("row-key universe hash", canonical_hash(bindings.get("outputCardinality", {}).get("expectedRowKeyUniverse")), EXPECTED_ROW_KEY_HASH)
    _require("expected row count", bindings.get("outputCardinality", {}).get("expectedRowCount"), EXPECTED_ROW_COUNT)
    _require("row templates per event", bindings.get("outputCardinality", {}).get("rowTemplatesPerEvent"), 8)

    manifest_by_id = {_identity(item)[0]: item for item in population if isinstance(item, Mapping)}
    if len(manifest_by_id) != EXPECTED_EVENT_COUNT:
        raise RealPopulationAdmissionError("population manifest event IDs are missing or duplicated")
    admitted: list[Mapping[str, Any]] = []
    for event in events:
        if not isinstance(event, Mapping):
            raise RealPopulationAdmissionError("shared astronomy snapshot contains a non-object event")
        _validate_snapshot_event(event)
        event_id, _ = _identity(event)
        manifest_event = manifest_by_id.get(event_id)
        if manifest_event is None:
            raise RealPopulationAdmissionError("shared astronomy event is absent from the frozen manifest")
        _validate_event_pair(manifest_event, event)
        admitted.append(dict(event))
    if len({_identity(event)[0] for event in admitted}) != EXPECTED_EVENT_COUNT:
        raise RealPopulationAdmissionError("shared astronomy event IDs are duplicated")
    return AdmittedRealPopulation(tuple(admitted), manifest, snapshot, bindings)
