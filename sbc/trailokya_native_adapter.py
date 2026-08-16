"""Source-native Trailokya Dipika 1972 board and enumerated Vedha adapter.

The held 28-row target map is the authority for target identity and ordering.
The 81-cell board in this module is only a source-backed visual projection and
mapping aid.  Nothing here creates a score, polarity, market interpretation,
or execution path.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from .chakra_lab import ChakraLabEngine, ChakraLabRequest
from .models import to_primitive


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAILOKYA_PROFILE_ID = "SBC_TRAILOKYA_1972_V1"
BOARD_CONTRACT = "TRAILOKYA_1972_NATIVE_AKHANDA_81_BOARD_V1"
TARGET_CONTRACT = "TRAILOKYA_1972_ENUMERATED_NAKSHATRA_TARGETS_V1"
EXPANSION_CONTRACT = "TRAILOKYA_1972_DERIVED_SEMANTIC_TARGET_EXPANSIONS_V1"
NATIVE_GRID_PROFILE_ID = "trailokya_1972_native_akhanda_81_v1"
SOURCE_ID = "TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN"

_TRAILOKYA_ROOT = PROJECT_ROOT / "configs" / "sbc" / "trailokya"
_CONSTRUCTION_PATH = _TRAILOKYA_ROOT / "trailokya_1972_chakra_construction_v1.yaml"
_TARGET_MAP_PATH = _TRAILOKYA_ROOT / "trailokya_1972_vedha_target_map_v1.yaml"
_EXPANSION_PATH = _TRAILOKYA_ROOT / "trailokya_1972_special_expansion_rules_v1.yaml"

_RASHIS = frozenset({
    "ARIES", "TAURUS", "GEMINI", "CANCER", "LEO", "VIRGO", "LIBRA",
    "SCORPIO", "SAGITTARIUS", "CAPRICORN", "AQUARIUS", "PISCES",
})
_VOWELS = frozenset({
    "A", "AA", "I", "II", "U", "UU", "VOCALIC_R", "LONG_VOCALIC_R",
    "VOCALIC_L", "LONG_VOCALIC_L", "E", "AI", "O", "AU", "ANUSVARA", "VISARGA",
})
_TITHI_PREFIXES = ("NANDA_", "BHADRA_", "RIKTA_", "JAYA_", "PURNA_")
_FIXED_BODIES = frozenset({"SUN", "MOON", "RAHU", "KETU"})


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Trailokya source fixture is missing: {path.name}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Trailokya source fixture must be a mapping: {path.name}")
    return raw


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def _required_contract(raw: Mapping[str, Any], expected: str, label: str) -> None:
    if raw.get("contractId") != expected:
        raise ValueError(f"{label} contract mismatch")
    if raw.get("sourceStatus") not in {"SOURCE_CLOSED", None}:
        raise ValueError(f"{label} is not source closed")


def _split_target(value: Any) -> tuple[str, str]:
    text = str(value or "")
    if ":" not in text:
        raise ValueError(f"Trailokya target token is malformed: {text}")
    target_type, target_value = text.split(":", 1)
    if not target_type or not target_value:
        raise ValueError(f"Trailokya target token is malformed: {text}")
    return target_type, target_value


def _cell_layer(value: str, construction: Mapping[str, Any]) -> str:
    if value in _RASHIS:
        return "RASHI"
    if value in _VOWELS:
        return "VOWEL"
    if value.startswith(_TITHI_PREFIXES):
        return "TITHI_WEEKDAY_COLOCATION"
    if value == "PURNA_SATURDAY":
        return "CENTER_PURNA"
    if value in construction.get("aksharaTokenRegistry", {}):
        return "NAME_INITIAL"
    return "NAKSHATRA"


def _source_literal(value: str, construction: Mapping[str, Any]) -> str:
    token = construction.get("aksharaTokenRegistry", {}).get(value)
    if isinstance(token, dict) and token.get("literalDevanagari"):
        return str(token["literalDevanagari"])
    return value


def _normalized_display(value: str, construction: Mapping[str, Any]) -> str:
    token = construction.get("aksharaTokenRegistry", {}).get(value)
    if isinstance(token, dict) and token.get("normalizedDisplay"):
        return str(token["normalizedDisplay"])
    return value.replace("_", " ").title()


def load_trailokya_native_profile() -> dict[str, Any]:
    """Load the immutable source-backed board without consulting generic grids."""
    construction = _read_yaml(_CONSTRUCTION_PATH)
    target_map = _read_yaml(_TARGET_MAP_PATH)
    expansions = _read_yaml(_EXPANSION_PATH)
    _required_contract(construction, BOARD_CONTRACT, "Trailokya native board")
    _required_contract(target_map, TARGET_CONTRACT, "Trailokya target map")
    _required_contract(expansions, EXPANSION_CONTRACT, "Trailokya expansion map")
    orientation = construction.get("orientation", {})
    if orientation.get("authorVisible") != {"east": "TOP", "west": "BOTTOM", "north": "LEFT", "south": "RIGHT"}:
        raise ValueError("Trailokya author orientation is not source-closed")
    projection = construction.get("cellProjection")
    if not isinstance(projection, list) or len(projection) != 9 or any(not isinstance(row, list) or len(row) != 9 for row in projection):
        raise ValueError("Trailokya board must contain exactly nine 9-cell rows")

    cells: list[dict[str, Any]] = []
    for row_index, row in enumerate(projection, start=1):
        for column_index, raw_value in enumerate(row, start=1):
            value = str(raw_value)
            layer = _cell_layer(value, construction)
            cell = {
                "coordinate": {"row": row_index, "column": column_index, "label": f"{row_index}:{column_index}"},
                "sourceLiteral": _source_literal(value, construction),
                "canonicalToken": value,
                "normalizedDisplay": _normalized_display(value, construction),
                "layer": layer,
                "sourceStatus": "SOURCE_CLOSED",
                "printedPage": 1,
                "scanPage": 13,
            }
            cells.append(cell)
    if len(cells) != 81:
        raise ValueError("Trailokya native board must contain 81 source cells")
    rows = target_map.get("rows")
    if not isinstance(rows, list) or len(rows) != 28:
        raise ValueError("Trailokya source map must contain all 28 rows")
    return {
        "contract": "TRAILOKYA_1972_NATIVE_SOURCE_PROFILE_V1",
        "schemaVersion": 1,
        "profileId": TRAILOKYA_PROFILE_ID,
        "sourceId": SOURCE_ID,
        "board": {
            "contract": BOARD_CONTRACT,
            "gridProfileId": NATIVE_GRID_PROFILE_ID,
            "fixtureHash": _sha256_path(_CONSTRUCTION_PATH),
            "orientation": orientation,
            "cells": cells,
            "cellCount": len(cells),
            "sourceStatus": "SOURCE_CLOSED",
        },
        "targetAuthority": {
            "contract": TARGET_CONTRACT,
            "fixtureHash": _sha256_path(_TARGET_MAP_PATH),
            "rowCount": len(rows),
            "mode": "ENUMERATED_SOURCE_ROWS",
            "frontContract": "SINGLE_OPPOSITE_OUTER_NAKSHATRA_ONLY",
        },
        "expansions": {"contract": EXPANSION_CONTRACT, "fixtureHash": _sha256_path(_EXPANSION_PATH)},
        "readiness": {
            "nativeBoardTrustedForVisualProjection": True,
            "genericGridFallbackAllowed": False,
            "runtimePromotionAuthorized": False,
            "marketMappingAllowed": False,
            "executionAllowed": False,
        },
        "guardrails": _guardrails(),
    }


def _guardrails() -> dict[str, bool]:
    return {
        "readOnly": True,
        "enumeratedSourceAuthority": True,
        "genericGridFallbackAllowed": False,
        "naturalPlanetPolarityUsed": False,
        "scoreAggregationUsed": False,
        "marketDirectionInferred": False,
        "fieldsInfluenceAllowed": False,
        "autoSuggestInfluenceAllowed": False,
        "mlAllowed": False,
        "mt5Allowed": False,
        "executionAllowed": False,
    }


def _target_cell(profile: Mapping[str, Any], target_type: str, value: str) -> tuple[dict[str, Any] | None, str]:
    matches = [
        cell for cell in profile["board"]["cells"]
        if cell["layer"] == target_type and cell["canonicalToken"] == value
    ]
    if target_type == "TITHI_GROUP":
        matches = [
            cell for cell in profile["board"]["cells"]
            if (cell["layer"] == "TITHI_WEEKDAY_COLOCATION" and cell["canonicalToken"].startswith(f"{value}_"))
            or (value == "PURNA" and cell["layer"] == "CENTER_PURNA")
        ]
    if len(matches) > 1:
        # The board remains available for audit, but an ambiguous glyph is not
        # permitted to acquire a chosen coordinate by convention or symmetry.
        return None, "AMBIGUOUS_SOURCE_PROJECTION"
    if not matches:
        return None, "SEMANTIC_NO_PHYSICAL_CELL"
    return matches[0], "AVAILABLE"


def _context_reach(target_type: str, value: str, target_context: Mapping[str, Any] | None) -> str:
    if target_context is None:
        return "UNKNOWN"
    values = target_context.get(target_type)
    if values is None:
        return "UNKNOWN"
    if isinstance(values, str):
        known = {values}
    elif isinstance(values, (list, tuple, set, frozenset)):
        known = {str(item) for item in values}
    else:
        return "UNKNOWN"
    return "REACHED" if value in known else "NOT_REACHED"


def _row_for(profile: Mapping[str, Any], source_nakshatra: str) -> dict[str, Any]:
    target_map = _read_yaml(_TARGET_MAP_PATH)
    rows = [item for item in target_map.get("rows", []) if item.get("source") == source_nakshatra]
    if len(rows) != 1:
        raise ValueError(f"SOURCE_ROW_UNAVAILABLE:{source_nakshatra}")
    return rows[0]


def _direct_target(profile: Mapping[str, Any], source: str, direction: str, index: int, encoded: Any, row: Mapping[str, Any], event_id: str, target_context: Mapping[str, Any] | None) -> dict[str, Any]:
    target_type, value = _split_target(encoded)
    cell, mapping_state = _target_cell(profile, target_type, value)
    return {
        "targetId": _canonical_hash({"sourceEventId": event_id, "kind": "DIRECT", "direction": direction, "index": index, "type": target_type, "value": value}),
        "sourceEventId": event_id,
        "causalVedhaEventId": event_id,
        "sourceNakshatra": source,
        "direction": direction,
        "sourceOrderedIndex": index,
        "targetType": target_type,
        "canonicalToken": value,
        "isDerived": False,
        "derivedFromTargetId": None,
        "derivationRuleId": None,
        "physicalCell": cell["coordinate"] if cell else None,
        "mappingState": mapping_state,
        "reachState": _context_reach(target_type, value, target_context),
        "sourceLocator": {"verse": row.get("verse"), "scanPage": row.get("scanPage"), "printedPage": row.get("printedPage"), "auditStatus": row.get("auditStatus")},
    }


def _derived_target(profile: Mapping[str, Any], direct: Mapping[str, Any], target_type: str, value: str, rule_id: str, target_context: Mapping[str, Any] | None) -> dict[str, Any]:
    cell, mapping_state = _target_cell(profile, target_type, value)
    event_id = str(direct["sourceEventId"])
    return {
        "targetId": _canonical_hash({"sourceEventId": event_id, "kind": "DERIVED", "from": direct["targetId"], "rule": rule_id, "type": target_type, "value": value}),
        "sourceEventId": event_id,
        "causalVedhaEventId": event_id,
        "sourceNakshatra": direct["sourceNakshatra"],
        "direction": direct["direction"],
        "sourceOrderedIndex": direct["sourceOrderedIndex"],
        "targetType": target_type,
        "canonicalToken": value,
        "isDerived": True,
        "derivedFromTargetId": direct["targetId"],
        "derivationRuleId": rule_id,
        "physicalCell": cell["coordinate"] if cell else None,
        "mappingState": mapping_state,
        "reachState": _context_reach(target_type, value, target_context),
        "sourceLocator": direct["sourceLocator"],
    }


def _expanded_targets(profile: Mapping[str, Any], directs: list[dict[str, Any]], target_context: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    expansions = _read_yaml(_EXPANSION_PATH)
    rules = {str(rule.get("id")): rule for rule in expansions.get("rules", []) if isinstance(rule, dict)}
    derived: list[dict[str, Any]] = []
    pairs = rules.get("TD1972_V48_PAIRED_UNWRITTEN_AKSHARA", {}).get("pairs", [])
    pair_lookup: dict[str, str] = {}
    for pair in pairs:
        if isinstance(pair, list) and len(pair) == 2:
            left, right = pair
            if isinstance(left, dict) and isinstance(right, dict):
                pair_lookup[str(left.get("canonicalToken"))] = str(right.get("canonicalToken"))
                pair_lookup[str(right.get("canonicalToken"))] = str(left.get("canonicalToken"))
    triplet_lookup = {
        str(item.get("representative", {}).get("canonicalToken")): [str(value.get("canonicalToken")) for value in item.get("derived", []) if isinstance(value, dict)]
        for item in rules.get("TD1972_V49_V50_TRIPLET_AKSHARA", {}).get("triplets", [])
        if isinstance(item, dict)
    }
    vowel_lookup: dict[str, str] = {}
    for pair in rules.get("TD1972_V51_VOWEL_COHIT", {}).get("vowelPairs", []):
        if isinstance(pair, list) and len(pair) == 2:
            vowel_lookup[str(pair[0])] = str(pair[1])
            vowel_lookup[str(pair[1])] = str(pair[0])
    for direct in directs:
        value = str(direct["canonicalToken"])
        if direct["targetType"] == "NAME_INITIAL":
            if value in pair_lookup:
                derived.append(_derived_target(profile, direct, "NAME_INITIAL", pair_lookup[value], "TD1972_V48_PAIRED_UNWRITTEN_AKSHARA", target_context))
            for derived_value in triplet_lookup.get(value, []):
                derived.append(_derived_target(profile, direct, "NAME_INITIAL", derived_value, "TD1972_V49_V50_TRIPLET_AKSHARA", target_context))
        if direct["targetType"] == "VOWEL" and value in vowel_lookup:
            derived.append(_derived_target(profile, direct, "VOWEL", vowel_lookup[value], "TD1972_V51_VOWEL_COHIT", target_context))
    boundary = str((target_context or {}).get("boundaryPada") or "")
    corner_cases = rules.get("TD1972_V52_CORNER_PADA_PURNA_COHIT", {}).get("cornerCases", [])
    if boundary and directs:
        for case in corner_cases:
            if not isinstance(case, dict) or case.get("boundary") != boundary:
                continue
            derived.append(_derived_target(profile, directs[0], "VOWEL", str(case.get("vowel")), "TD1972_V52_CORNER_PADA_PURNA_COHIT", target_context))
            derived.append(_derived_target(profile, directs[0], "TITHI_GROUP", "PURNA", "TD1972_V52_CORNER_PADA_PURNA_COHIT", target_context))
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for target in derived:
        key = (str(target["derivedFromTargetId"]), str(target["targetType"]), str(target["canonicalToken"]))
        if key not in seen:
            seen.add(key)
            unique.append(target)
    return unique


def resolve_trailokya_targets(source_nakshatra: str, direction: str, target_context: Mapping[str, Any] | None = None, source_profile: str = TRAILOKYA_PROFILE_ID) -> dict[str, Any]:
    """Resolve source-ordered targets.  Enumerated rows always win over geometry."""
    if source_profile != TRAILOKYA_PROFILE_ID:
        raise ValueError("TRAILOKYA_SOURCE_PROFILE_REQUIRED")
    source = str(source_nakshatra or "").upper()
    selected_direction = str(direction or "").upper()
    if selected_direction not in {"LEFT", "FRONT", "RIGHT"}:
        raise ValueError("TRAILOKYA_DIRECTION_REQUIRED")
    profile = load_trailokya_native_profile()
    row = _row_for(profile, source)
    raw_targets = row.get(selected_direction.lower())
    if selected_direction == "FRONT":
        raw_targets = [raw_targets]
    if not isinstance(raw_targets, list) or not raw_targets:
        return {
            "contract": "TRAILOKYA_1972_ENUMERATED_TARGET_RESOLUTION_V1",
            "sourceProfileId": TRAILOKYA_PROFILE_ID,
            "sourceNakshatra": source,
            "direction": selected_direction,
            "status": "BLOCKED_SOURCE_ROW_UNAVAILABLE",
            "directTargets": [], "derivedTargets": [], "allTargets": [],
            "guardrails": _guardrails(),
        }
    event_id = _canonical_hash({"contract": TARGET_CONTRACT, "source": source, "direction": selected_direction, "verse": row.get("verse")})
    directs = [_direct_target(profile, source, selected_direction, index, encoded, row, event_id, target_context) for index, encoded in enumerate(raw_targets, start=1)]
    if selected_direction == "FRONT" and len(directs) != 1:
        raise ValueError("TRAILOKYA_FRONT_MUST_HAVE_ONE_ENUMERATED_TARGET")
    derived = _expanded_targets(profile, directs, target_context)
    direct_values = {(item["targetType"], item["canonicalToken"]) for item in directs}
    derived = [item for item in derived if (item["targetType"], item["canonicalToken"]) not in direct_values]
    return {
        "contract": "TRAILOKYA_1972_ENUMERATED_TARGET_RESOLUTION_V1",
        "sourceProfileId": TRAILOKYA_PROFILE_ID,
        "targetAuthority": "ENUMERATED_SOURCE_ROWS",
        "sourceNakshatra": source,
        "direction": selected_direction,
        "sourceEventId": event_id,
        "causalVedhaEventId": event_id,
        "sourceRow": {"verse": row.get("verse"), "scanPage": row.get("scanPage"), "printedPage": row.get("printedPage"), "auditStatus": row.get("auditStatus")},
        "status": "SOURCE_ROW_RESOLVED",
        "directTargets": directs,
        "derivedTargets": derived,
        "allTargets": [*directs, *derived],
        "geometryDiagnostic": {"status": "GEOMETRY_DIAGNOSTIC_NOT_REQUESTED", "authoritativeResult": "SOURCE_ROW_WINS"},
        "guardrails": _guardrails(),
    }


def _native_snapshot(request: ChakraLabRequest, engine: ChakraLabEngine) -> dict[str, Any]:
    profile = load_trailokya_native_profile()
    context = engine.source_context(request)
    foundation = context["foundation"]
    identity = {
        "contract": "TRAILOKYA_1972_NATIVE_SOURCE_SNAPSHOT_V1",
        "asOfUtc": context["as_of_utc"].isoformat(),
        "foundation": foundation.snapshot_id,
        "board": profile["board"]["fixtureHash"],
        "actors": to_primitive(context["actor_readiness"]),
    }
    return {
        "contract": "TRAILOKYA_1972_NATIVE_SOURCE_SNAPSHOT_V1",
        "snapshotId": _canonical_hash(identity),
        "asOfUtc": context["as_of_utc"].isoformat(),
        "requestedAtLocal": context["requested_at_local"].isoformat(),
        "foundationSnapshotId": foundation.snapshot_id,
        "targetContext": to_primitive(context["target_context"]),
        "positionContext": to_primitive(context["position_context"]),
        "actorReadiness": to_primitive(context["actor_readiness"]),
        "board": profile["board"],
        "guardrails": _guardrails(),
    }


def build_trailokya_native_snapshot(request: ChakraLabRequest, *, engine: ChakraLabEngine | None = None) -> dict[str, Any]:
    if request.vedha_profile_id != TRAILOKYA_PROFILE_ID:
        raise ValueError("TRAILOKYA_SOURCE_PROFILE_REQUIRED")
    if request.grid_profile_id != NATIVE_GRID_PROFILE_ID:
        raise ValueError("TRAILOKYA_SOURCE_NATIVE_GRID_ADAPTER_REQUIRED")
    return _native_snapshot(request, engine or ChakraLabEngine())
