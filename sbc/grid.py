from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .config import load_source_register
from .models import to_primitive


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GRID_PROFILE_ROOT = PROJECT_ROOT / "configs" / "sbc" / "grids"

GRID_PROFILE_KEYS = {
    "schema_version",
    "grid_profile_id",
    "grid_form",
    "status",
    "authority",
    "selection_policy",
    "compile_enabled",
    "blocked_reason",
    "dimensions",
    "orientation",
    "witness_sets",
    "certified_layers",
    "entries",
    "unresolved_layers",
    "blocked_capabilities",
    "notes",
}
DIMENSION_KEYS = {"rows", "columns"}
ORIENTATION_KEYS = {
    "coordinate_basis",
    "row_direction",
    "column_direction",
    "cardinal_binding",
    "comparison_transform",
}
WITNESS_SET_KEYS = {"witness_set_id", "evidence_status", "citations"}
CITATION_KEYS = {"source_id", "locator", "witness_role", "transform_to_profile"}
ENTRY_KEYS = {"row", "column", "layer", "value", "witness_set_id"}
UNRESOLVED_LAYER_KEYS = {"layer", "expected_count", "reason", "witness_set_id"}

SELECTION_POLICY = "EXPLICIT_ONLY"
SUPPORTED_TRANSFORMS = {
    "IDENTITY",
    "ROTATE_CCW_90",
    "ROTATE_CW_90",
    "ROTATE_180",
    "NONE",
}
ALLOWED_ENTRY_LAYERS = {"NAKSHATRA", "RASHI", "TITHI_GROUP", "WEEKDAY"}

SBC_NAKSHATRAS_28 = (
    "KRITTIKA",
    "ROHINI",
    "MRIGASHIRA",
    "ARDRA",
    "PUNARVASU",
    "PUSHYA",
    "ASHLESHA",
    "MAGHA",
    "PURVA_PHALGUNI",
    "UTTARA_PHALGUNI",
    "HASTA",
    "CHITRA",
    "SWATI",
    "VISHAKHA",
    "ANURADHA",
    "JYESHTHA",
    "MULA",
    "PURVA_ASHADHA",
    "UTTARA_ASHADHA",
    "ABHIJIT",
    "SHRAVANA",
    "DHANISHTHA",
    "SHATABHISHA",
    "PURVA_BHADRAPADA",
    "UTTARA_BHADRAPADA",
    "REVATI",
    "ASHWINI",
    "BHARANI",
)
SBC_RASHIS_12 = (
    "VRISHABHA",
    "MITHUNA",
    "KARKA",
    "SIMHA",
    "KANYA",
    "TULA",
    "VRISCHIKA",
    "DHANUS",
    "MAKARA",
    "KUMBHA",
    "MEENA",
    "MESHA",
)
SBC_TITHI_GROUPS_5 = ("NANDA", "BHADRA", "JAYA", "RIKTA", "PURNA")
WEEKDAYS_7 = (
    "SUNDAY",
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
)

CERTIFIED_LAYER_VALUES = {
    "NAKSHATRA": frozenset(SBC_NAKSHATRAS_28),
    "RASHI": frozenset(SBC_RASHIS_12),
    "TITHI_GROUP": frozenset(SBC_TITHI_GROUPS_5),
    "WEEKDAY": frozenset(WEEKDAYS_7),
}


class GridProfileBlockedError(ValueError):
    """Raised when a source profile exists only to record a research block."""


@dataclass(frozen=True)
class GridCitation:
    source_id: str
    locator: str
    witness_role: str
    transform_to_profile: str


@dataclass(frozen=True)
class GridWitnessSet:
    witness_set_id: str
    evidence_status: str
    citations: tuple[GridCitation, ...]


@dataclass(frozen=True)
class GridEntry:
    row: int
    column: int
    layer: str
    value: str
    witness_set_id: str
    citations: tuple[GridCitation, ...]
    evidence_status: str


@dataclass(frozen=True)
class UnresolvedGridLayer:
    layer: str
    expected_count: int
    reason: str
    witness_set_id: str
    citations: tuple[GridCitation, ...]


@dataclass(frozen=True)
class GridProfileDefinition:
    grid_profile_id: str
    profile_hash: str
    grid_form: str
    status: str
    authority: str
    selection_policy: str
    compile_enabled: bool
    blocked_reason: str | None
    rows: int
    columns: int
    orientation: dict[str, str]
    witness_sets: tuple[GridWitnessSet, ...]
    certified_layers: tuple[str, ...]
    entries: tuple[GridEntry, ...]
    unresolved_layers: tuple[UnresolvedGridLayer, ...]
    blocked_capabilities: tuple[str, ...]
    raw: dict[str, Any]


@dataclass(frozen=True)
class GridCell:
    row: int
    column: int
    entries: tuple[GridEntry, ...]


@dataclass(frozen=True)
class CompiledGrid:
    schema_version: str
    grid_profile_id: str
    profile_hash: str
    grid_form: str
    status: str
    rows: int
    columns: int
    orientation: dict[str, str]
    cells: tuple[GridCell, ...]
    certified_layers: tuple[str, ...]
    unresolved_layers: tuple[UnresolvedGridLayer, ...]
    source_ids: tuple[str, ...]
    complete: bool
    blocked_capabilities: tuple[str, ...]

    def cell(self, row: int, column: int) -> GridCell:
        if not (1 <= row <= self.rows and 1 <= column <= self.columns):
            raise IndexError(
                f"grid coordinate is outside {self.rows}x{self.columns}: ({row}, {column})"
            )
        return self.cells[(row - 1) * self.columns + column - 1]

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return loaded


def _reject_unknown(mapping: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ValueError(f"Unknown {label} fields: {', '.join(unknown)}")


def _required_text(mapping: dict[str, Any], key: str, label: str) -> str:
    value = str(mapping.get(key, "")).strip()
    if not value:
        raise ValueError(f"{label} requires {key}")
    return value


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def rotate_coordinate(
    row: int, column: int, size: int, transform: str
) -> tuple[int, int]:
    if not (1 <= row <= size and 1 <= column <= size):
        raise ValueError(f"coordinate outside {size}x{size}: ({row}, {column})")
    if transform == "IDENTITY":
        return row, column
    if transform == "ROTATE_CCW_90":
        return size + 1 - column, row
    if transform == "ROTATE_CW_90":
        return column, size + 1 - row
    if transform == "ROTATE_180":
        return size + 1 - row, size + 1 - column
    raise ValueError(f"unsupported coordinate transform: {transform}")


def _validate_layer_coverage(
    certified_layers: tuple[str, ...], entries: tuple[GridEntry, ...]
) -> None:
    for layer in certified_layers:
        expected = CERTIFIED_LAYER_VALUES[layer]
        actual = [entry.value for entry in entries if entry.layer == layer]
        if len(actual) != len(set(actual)):
            raise ValueError(f"certified layer {layer} contains duplicate values")
        if frozenset(actual) != expected:
            missing = sorted(expected - frozenset(actual))
            extra = sorted(frozenset(actual) - expected)
            raise ValueError(
                f"certified layer {layer} coverage mismatch; missing={missing}, extra={extra}"
            )


def validate_grid_profile(
    raw: dict[str, Any],
    source_register: dict[str, Any] | None = None,
) -> GridProfileDefinition:
    _reject_unknown(raw, GRID_PROFILE_KEYS, "grid profile")
    if int(raw.get("schema_version", 0)) != 1:
        raise ValueError("grid profile schema_version must be 1")

    profile_id = _required_text(raw, "grid_profile_id", "grid profile")
    grid_form = _required_text(raw, "grid_form", profile_id)
    status = _required_text(raw, "status", profile_id)
    authority = _required_text(raw, "authority", profile_id)
    selection_policy = _required_text(raw, "selection_policy", profile_id)
    if selection_policy != SELECTION_POLICY:
        raise ValueError("grid profiles must use EXPLICIT_ONLY selection")
    compile_enabled = bool(raw.get("compile_enabled", False))
    blocked_reason_raw = raw.get("blocked_reason")
    blocked_reason = (
        str(blocked_reason_raw).strip() if blocked_reason_raw is not None else None
    )

    dimensions = raw.get("dimensions")
    orientation_raw = raw.get("orientation")
    if not isinstance(dimensions, dict) or not isinstance(orientation_raw, dict):
        raise ValueError("dimensions and orientation must be mappings")
    _reject_unknown(dimensions, DIMENSION_KEYS, "grid dimension")
    _reject_unknown(orientation_raw, ORIENTATION_KEYS, "grid orientation")
    rows = int(dimensions.get("rows", 0))
    columns = int(dimensions.get("columns", 0))
    expected_dimensions = {"SBC_81_CELL": (9, 9), "SBC_64_CELL": (8, 8)}
    if (
        grid_form not in expected_dimensions
        or (rows, columns) != expected_dimensions[grid_form]
    ):
        raise ValueError(
            f"{grid_form} requires dimensions {expected_dimensions.get(grid_form)}"
        )
    orientation = {
        key: _required_text(orientation_raw, key, "grid orientation")
        for key in ORIENTATION_KEYS
    }
    if orientation["comparison_transform"] not in SUPPORTED_TRANSFORMS:
        raise ValueError("unsupported grid comparison_transform")

    register = source_register or load_source_register()
    known_source_ids = {str(item["source_id"]) for item in register["sources"]}
    witness_sets_raw = raw.get("witness_sets")
    if not isinstance(witness_sets_raw, list):
        raise ValueError("witness_sets must be a list")
    witness_sets: list[GridWitnessSet] = []
    witness_by_id: dict[str, GridWitnessSet] = {}
    for witness_raw in witness_sets_raw:
        if not isinstance(witness_raw, dict):
            raise ValueError("every witness set must be a mapping")
        _reject_unknown(witness_raw, WITNESS_SET_KEYS, "witness set")
        witness_id = _required_text(witness_raw, "witness_set_id", "witness set")
        if witness_id in witness_by_id:
            raise ValueError(f"duplicate witness_set_id: {witness_id}")
        evidence_status = _required_text(witness_raw, "evidence_status", witness_id)
        citations_raw = witness_raw.get("citations")
        if not isinstance(citations_raw, list) or not citations_raw:
            raise ValueError(f"{witness_id} requires citations")
        citations: list[GridCitation] = []
        for citation_raw in citations_raw:
            if not isinstance(citation_raw, dict):
                raise ValueError("every citation must be a mapping")
            _reject_unknown(citation_raw, CITATION_KEYS, "grid citation")
            source_id = _required_text(citation_raw, "source_id", "grid citation")
            if source_id not in known_source_ids:
                raise ValueError(f"grid profile has unresolved source ID: {source_id}")
            transform = _required_text(citation_raw, "transform_to_profile", source_id)
            if transform not in SUPPORTED_TRANSFORMS:
                raise ValueError(f"unsupported citation transform: {transform}")
            citations.append(
                GridCitation(
                    source_id=source_id,
                    locator=_required_text(citation_raw, "locator", source_id),
                    witness_role=_required_text(
                        citation_raw, "witness_role", source_id
                    ),
                    transform_to_profile=transform,
                )
            )
        witness = GridWitnessSet(witness_id, evidence_status, tuple(citations))
        witness_sets.append(witness)
        witness_by_id[witness_id] = witness

    certified_raw = raw.get("certified_layers")
    if not isinstance(certified_raw, list):
        raise ValueError("certified_layers must be a list")
    certified_layers = tuple(str(layer).strip().upper() for layer in certified_raw)
    if len(certified_layers) != len(set(certified_layers)):
        raise ValueError("certified_layers contains duplicates")
    unknown_layers = sorted(set(certified_layers) - ALLOWED_ENTRY_LAYERS)
    if unknown_layers:
        raise ValueError(f"unsupported certified layers: {', '.join(unknown_layers)}")

    entries_raw = raw.get("entries")
    if not isinstance(entries_raw, list):
        raise ValueError("entries must be a list")
    entries: list[GridEntry] = []
    seen_entries: set[tuple[int, int, str, str]] = set()
    single_value_cells: set[tuple[int, int, str]] = set()
    for entry_raw in entries_raw:
        if not isinstance(entry_raw, dict):
            raise ValueError("every grid entry must be a mapping")
        _reject_unknown(entry_raw, ENTRY_KEYS, "grid entry")
        row = int(entry_raw.get("row", 0))
        column = int(entry_raw.get("column", 0))
        if not (1 <= row <= rows and 1 <= column <= columns):
            raise ValueError(f"grid entry outside {rows}x{columns}: ({row}, {column})")
        layer = _required_text(entry_raw, "layer", "grid entry").upper()
        value = _required_text(entry_raw, "value", "grid entry").upper()
        if layer not in ALLOWED_ENTRY_LAYERS:
            raise ValueError(f"unsupported grid entry layer: {layer}")
        witness_id = _required_text(entry_raw, "witness_set_id", "grid entry")
        witness = witness_by_id.get(witness_id)
        if witness is None:
            raise ValueError(f"grid entry references unknown witness set: {witness_id}")
        entry_key = (row, column, layer, value)
        if entry_key in seen_entries:
            raise ValueError(f"duplicate grid entry: {entry_key}")
        seen_entries.add(entry_key)
        cell_layer = (row, column, layer)
        if layer != "WEEKDAY" and cell_layer in single_value_cells:
            raise ValueError(f"multiple {layer} values in cell ({row}, {column})")
        single_value_cells.add(cell_layer)
        entries.append(
            GridEntry(
                row=row,
                column=column,
                layer=layer,
                value=value,
                witness_set_id=witness_id,
                citations=witness.citations,
                evidence_status=witness.evidence_status,
            )
        )

    unresolved_raw = raw.get("unresolved_layers")
    if not isinstance(unresolved_raw, list):
        raise ValueError("unresolved_layers must be a list")
    unresolved_layers: list[UnresolvedGridLayer] = []
    seen_unresolved: set[str] = set()
    for item_raw in unresolved_raw:
        if not isinstance(item_raw, dict):
            raise ValueError("every unresolved layer must be a mapping")
        _reject_unknown(item_raw, UNRESOLVED_LAYER_KEYS, "unresolved layer")
        layer = _required_text(item_raw, "layer", "unresolved layer").upper()
        if layer in seen_unresolved:
            raise ValueError(f"duplicate unresolved layer: {layer}")
        seen_unresolved.add(layer)
        expected_count = int(item_raw.get("expected_count", 0))
        if expected_count <= 0:
            raise ValueError(f"{layer} expected_count must be positive")
        witness_id = _required_text(item_raw, "witness_set_id", layer)
        witness = witness_by_id.get(witness_id)
        if witness is None:
            raise ValueError(
                f"unresolved layer references unknown witness set: {witness_id}"
            )
        unresolved_layers.append(
            UnresolvedGridLayer(
                layer=layer,
                expected_count=expected_count,
                reason=_required_text(item_raw, "reason", layer),
                witness_set_id=witness_id,
                citations=witness.citations,
            )
        )

    blocked_capabilities_raw = raw.get("blocked_capabilities")
    if not isinstance(blocked_capabilities_raw, list) or not blocked_capabilities_raw:
        raise ValueError("blocked_capabilities must be a non-empty list")
    blocked_capabilities = tuple(
        str(item).strip().upper() for item in blocked_capabilities_raw
    )
    if any(not item for item in blocked_capabilities) or len(
        blocked_capabilities
    ) != len(set(blocked_capabilities)):
        raise ValueError("blocked_capabilities must contain unique non-empty values")

    entries_tuple = tuple(
        sorted(
            entries, key=lambda item: (item.row, item.column, item.layer, item.value)
        )
    )
    if compile_enabled:
        if grid_form != "SBC_81_CELL":
            raise ValueError("only the partial 81-cell topology fixture may compile")
        if blocked_reason:
            raise ValueError("compile-enabled profiles cannot have blocked_reason")
        if not certified_layers:
            raise ValueError("compile-enabled grid requires certified layers")
        _validate_layer_coverage(certified_layers, entries_tuple)
    else:
        if entries_tuple:
            raise ValueError("blocked grid profiles cannot contain executable entries")
        if not blocked_reason:
            raise ValueError("blocked grid profile requires blocked_reason")

    overlap = set(certified_layers) & seen_unresolved
    if overlap:
        raise ValueError(
            f"layers cannot be both certified and unresolved: {sorted(overlap)}"
        )

    return GridProfileDefinition(
        grid_profile_id=profile_id,
        profile_hash=_canonical_hash(raw),
        grid_form=grid_form,
        status=status,
        authority=authority,
        selection_policy=selection_policy,
        compile_enabled=compile_enabled,
        blocked_reason=blocked_reason,
        rows=rows,
        columns=columns,
        orientation=orientation,
        witness_sets=tuple(witness_sets),
        certified_layers=certified_layers,
        entries=entries_tuple,
        unresolved_layers=tuple(unresolved_layers),
        blocked_capabilities=blocked_capabilities,
        raw=raw,
    )


def load_grid_profile(
    profile_id: str, profile_root: Path | None = None
) -> GridProfileDefinition:
    root = profile_root or GRID_PROFILE_ROOT
    path = root / f"{profile_id}.yaml"
    raw = _load_yaml(path)
    if str(raw.get("grid_profile_id", "")) != profile_id:
        raise ValueError(f"grid profile filename/id mismatch: {path}")
    return validate_grid_profile(raw)


def compile_grid(
    profile: str | GridProfileDefinition,
    profile_root: Path | None = None,
) -> CompiledGrid:
    definition = (
        load_grid_profile(profile, profile_root)
        if isinstance(profile, str)
        else profile
    )
    if not definition.compile_enabled:
        raise GridProfileBlockedError(
            f"{definition.grid_profile_id} is blocked: {definition.blocked_reason}"
        )
    by_cell: dict[tuple[int, int], list[GridEntry]] = {}
    for entry in definition.entries:
        by_cell.setdefault((entry.row, entry.column), []).append(entry)
    cells = tuple(
        GridCell(
            row=row,
            column=column,
            entries=tuple(
                sorted(
                    by_cell.get((row, column), []),
                    key=lambda item: (item.layer, item.value),
                )
            ),
        )
        for row in range(1, definition.rows + 1)
        for column in range(1, definition.columns + 1)
    )
    source_ids = tuple(
        sorted(
            {
                citation.source_id
                for witness in definition.witness_sets
                for citation in witness.citations
            }
        )
    )
    return CompiledGrid(
        schema_version="SBC_GRID_FIXTURE_V1",
        grid_profile_id=definition.grid_profile_id,
        profile_hash=definition.profile_hash,
        grid_form=definition.grid_form,
        status=definition.status,
        rows=definition.rows,
        columns=definition.columns,
        orientation=definition.orientation,
        cells=cells,
        certified_layers=definition.certified_layers,
        unresolved_layers=definition.unresolved_layers,
        source_ids=source_ids,
        complete=not definition.unresolved_layers,
        blocked_capabilities=definition.blocked_capabilities,
    )
