"""Narrow, fail-closed Trailokya 1972 Vedha geometry.

This module deliberately does not instantiate ``VedhaGuidanceEngine``.  Its
output contains rays and categorical target reach only: no planet nature,
modifier, score, polarity, market direction, confidence or price conversion.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .chakra_lab import (
    ChakraLabEngine,
    ChakraLabRequest,
    ChakraLabSnapshot,
    VEDHA_FIXED_BODIES,
    VEDHA_VARIABLE_BODIES,
)
from .grid import CompiledGrid, GridEntry, SBC_NAKSHATRAS_28
from .models import to_primitive
from .vedha import MotionClass, VedhaDirection


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APPROVAL_PATH = PROJECT_ROOT / "configs" / "sbc" / "approved_profiles" / "sbc_trailokya_1972_source_only_geometry_v1.yaml"
TRAILOKYA_PROFILE_ID = "SBC_TRAILOKYA_1972_V1"
CONTRACT = "SBC_TRAILOKYA_1972_SOURCE_ONLY_GEOMETRY_V1"
TARGET_LAYERS = frozenset({"NAKSHATRA", "RASHI", "TITHI_GROUP", "VOWEL", "NAME_INITIAL"})
VARIABLE_DIRECTIONS = {
    MotionClass.RETROGRADE: VedhaDirection.RIGHT,
    MotionClass.DIRECT_SWIFT: VedhaDirection.LEFT,
    MotionClass.MEAN: VedhaDirection.FRONT,
}
FIXED_DIRECTIONS = (VedhaDirection.LEFT, VedhaDirection.FRONT, VedhaDirection.RIGHT)


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def load_approved_profile(path: Path | None = None) -> dict[str, Any]:
    source = path or APPROVAL_PATH
    raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Trailokya approved profile must be a mapping")
    if raw.get("schemaVersion") != "SBC_APPROVED_SOURCE_ONLY_PROFILE_V1":
        raise ValueError("Trailokya approved profile schema mismatch")
    if raw.get("selectedSourceProfile") != TRAILOKYA_PROFILE_ID:
        raise ValueError("Trailokya geometry requires the explicitly selected source profile")
    if raw.get("founderDecision") != "APPROVED_FOR_SOURCE_ONLY_WITH_LIMITS":
        raise ValueError("Trailokya source-only geometry is not founder-approved")
    approved = raw.get("approvedVariables")
    required = {
        "SBC_TD1972_VARIABLE_PLANET_DIRECTION",
        "SBC_TD1972_FIXED_THREE_DIRECTION_BODIES",
        "SBC_TD1972_RAY_EXTENT",
    }
    if not isinstance(approved, list) or {item.get("variableId") for item in approved if isinstance(item, dict)} != required:
        raise ValueError("Trailokya approval record must contain exactly the three approved geometry variables")
    if any(item.get("founderDecision") != "APPROVED_FOR_SOURCE_ONLY_WITH_LIMITS" for item in approved):
        raise ValueError("Trailokya approval record has an unapproved geometry variable")
    limits = raw.get("limits")
    if not isinstance(limits, dict) or not all(
        limits.get(key) is False
        for key in ("directionalWaveAllowed", "naturalPlanetClassAllowed", "numericalModifierAllowed", "executionAllowed", "packagingAllowed")
    ):
        raise ValueError("Trailokya geometry profile must retain all scoring and execution locks")
    return raw


def _source_cell(grid: CompiledGrid, source_nakshatra: str) -> tuple[int, int]:
    matches = [
        (cell.row, cell.column)
        for cell in grid.cells
        for entry in cell.entries
        if entry.layer == "NAKSHATRA" and entry.value == source_nakshatra
    ]
    if len(matches) != 1:
        raise ValueError("SOURCE_NAKSHATRA_MAPPING_UNAVAILABLE")
    row, column = matches[0]
    if (row in {1, grid.rows}) == (column in {1, grid.columns}):
        raise ValueError("SOURCE_NAKSHATRA_NOT_ON_NONCORNER_EDGE")
    return row, column


def _inward_vector(row: int, column: int, rows: int, columns: int) -> tuple[int, int]:
    if row == 1 and 1 < column < columns:
        return 1, 0
    if row == rows and 1 < column < columns:
        return -1, 0
    if column == 1 and 1 < row < rows:
        return 0, 1
    if column == columns and 1 < row < rows:
        return 0, -1
    raise ValueError("FIGURE_RELATIVE_DIRECTION_UNAVAILABLE")


def _entry_target(
    source: str,
    direction: VedhaDirection,
    row: int,
    column: int,
    entry: GridEntry,
    context: dict[str, set[str]],
) -> dict[str, Any]:
    mapping_state = "AVAILABLE" if entry.evidence_status.startswith("TWO_WITNESS") else "UNKNOWN"
    reached = mapping_state == "AVAILABLE" and entry.value in context.get(entry.layer, set())
    return {
        "sourceNakshatra": source,
        "direction": direction.value,
        "row": row,
        "column": column,
        "layer": entry.layer,
        "value": entry.value,
        "semanticRole": entry.semantic_role,
        "witnessSetId": entry.witness_set_id,
        "mappingState": mapping_state,
        "reachState": "REACHED" if reached else ("NOT_REACHED" if mapping_state == "AVAILABLE" else "UNKNOWN"),
        "citations": to_primitive(entry.citations),
    }


def _targets_for_direction(
    grid: CompiledGrid,
    source_nakshatra: str,
    direction: VedhaDirection,
    context: dict[str, set[str]],
) -> tuple[dict[str, Any], ...]:
    source = source_nakshatra.upper()
    if source not in SBC_NAKSHATRAS_28:
        raise ValueError("UNSUPPORTED_SOURCE_NAKSHATRA")
    row, column = _source_cell(grid, source)
    dr, dc = _inward_vector(row, column, grid.rows, grid.columns)
    if direction == VedhaDirection.FRONT:
        current_row, current_column = row, column
        while True:
            next_row, next_column = current_row + dr, current_column + dc
            if not (1 <= next_row <= grid.rows and 1 <= next_column <= grid.columns):
                break
            current_row, current_column = next_row, next_column
        entries = [entry for entry in grid.cell(current_row, current_column).entries if entry.layer == "NAKSHATRA"]
        if len(entries) != 1 or not entries[0].evidence_status.startswith("TWO_WITNESS"):
            raise ValueError("FRONT_TARGET_MAPPING_UNAVAILABLE")
        return (_entry_target(source, direction, current_row, current_column, entries[0], context),)

    left_dr, left_dc = -dc, dr
    step_row, step_column = (dr + left_dr, dc + left_dc) if direction == VedhaDirection.LEFT else (dr - left_dr, dc - left_dc)
    targets: list[dict[str, Any]] = []
    current_row, current_column = row + step_row, column + step_column
    while 1 <= current_row <= grid.rows and 1 <= current_column <= grid.columns:
        for entry in grid.cell(current_row, current_column).entries:
            if entry.layer in TARGET_LAYERS:
                targets.append(_entry_target(source, direction, current_row, current_column, entry, context))
        current_row += step_row
        current_column += step_column
    if not targets:
        raise ValueError("RAY_TARGET_MAPPING_UNAVAILABLE")
    return tuple(targets)


def summarize_target_reach(targets: tuple[dict[str, Any], ...]) -> str:
    """Preserve unknown mappings instead of turning them into a negative hit."""
    states = {str(target.get("reachState") or "UNKNOWN") for target in targets}
    if not states or states == {"UNKNOWN"}:
        return "UNKNOWN"
    if "UNKNOWN" in states:
        return "PARTIAL_UNKNOWN"
    if "REACHED" in states:
        return "REACHED"
    return "NOT_REACHED"


def _directions_for_actor(body: str, motion_class: str | None) -> tuple[tuple[VedhaDirection, ...], str | None, str]:
    if body in VEDHA_FIXED_BODIES:
        return FIXED_DIRECTIONS, None, "TRAILOKYA_FIXED_ALL_THREE_RAYS"
    if body not in VEDHA_VARIABLE_BODIES:
        return (), "OUTSIDE_APPROVED_PROFILE", "body has no approved Trailokya geometry rule"
    if not motion_class:
        return (), "MOTION_REQUIRED", "externally explicit RETROGRADE, DIRECT_SWIFT, or MEAN state is required"
    try:
        motion = MotionClass(motion_class)
    except ValueError:
        return (), "MOTION_REQUIRED", "motion state is not one of the founder-approved explicit research states"
    return (VARIABLE_DIRECTIONS[motion],), None, "TRAILOKYA_EXPLICIT_MOTION_DIRECTION"


def build_trailokya_source_only_geometry(
    request: ChakraLabRequest,
    *,
    engine: ChakraLabEngine | None = None,
) -> dict[str, Any]:
    if request.vedha_profile_id != TRAILOKYA_PROFILE_ID:
        raise ValueError("Trailokya source-only geometry requires vedhaProfileId=SBC_TRAILOKYA_1972_V1")
    approval = load_approved_profile()
    source_id = "TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN"
    snapshot = (engine or ChakraLabEngine()).snapshot_without_guidance(
        request, additional_source_ids=(source_id,)
    )
    context = {item.layer: set(item.values) for item in snapshot.target_context}
    rays: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []
    for actor in snapshot.actor_readiness:
        if not actor.requested:
            continue
        directions, unavailable_code, reason = _directions_for_actor(actor.body, actor.motion_class)
        if unavailable_code:
            unavailable.append({"body": actor.body, "sourceNakshatra": actor.source_nakshatra, "state": unavailable_code, "reason": reason})
            continue
        for direction in directions:
            try:
                targets = _targets_for_direction(snapshot.grid, actor.source_nakshatra, direction, context)
            except ValueError as exc:
                unavailable.append({"body": actor.body, "sourceNakshatra": actor.source_nakshatra, "direction": direction.value, "state": "TARGET_MAPPING_UNAVAILABLE", "reason": str(exc)})
                continue
            rays.append({
                "body": actor.body,
                "sourceNakshatra": actor.source_nakshatra,
                "motionClass": actor.motion_class,
                "direction": direction.value,
                "directionReason": reason,
                "targetReach": summarize_target_reach(targets),
                "targets": targets,
            })
    guardrails = {
        "readOnly": True,
        "categoricalGeometryOnly": True,
        "naturalPlanetPolarityUsed": False,
        "numericalModifiersUsed": False,
        "directionalWaveGenerated": False,
        "scoreAggregationUsed": False,
        "marketDirectionInferred": False,
        "autoSuggestInfluenceAllowed": False,
        "executionAllowed": False,
        "packagingAllowed": False,
    }
    return {
        "contract": CONTRACT,
        "schemaVersion": 1,
        "snapshot": snapshot.to_dict(),
        "approval": {
            "approvedProfileId": approval["approvedProfileId"],
            "profileHash": _canonical_hash(approval),
            "sourceProfileId": approval["selectedSourceProfile"],
            "packetId": approval["packetId"],
            "decisionRecord": approval["decisionRecord"],
            "founderDecision": approval["founderDecision"],
            "pageLocators": {
                "variableDirection": "printed p. 4 / PDF image 20 / verses 12-14",
                "fixedThreeDirections": "printed p. 5 / PDF image 21 / verse 15",
                "rayExtent": "printed p. 5 / PDF image 21 / verses 16-17",
            },
        },
        "rays": rays,
        "unavailable": unavailable,
        "guardrails": guardrails,
    }
