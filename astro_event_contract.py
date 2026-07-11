from __future__ import annotations

import json
import math
from typing import Any, Mapping


AVG_ALL_MEMBERS = (
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "URANUS",
    "NEPTUNE",
    "PLUTO",
)

ASPECT_ANGLES = {
    "conjunction": 0.0,
    "conjunction_orb": 0.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
    "opposition_orb": 180.0,
    "drishti_3": 60.0,
    "drishti_4": 90.0,
    "drishti_5": 120.0,
    "drishti_8": 210.0,
    "drishti_9": 240.0,
    "drishti_10": 270.0,
}


def normalize_body(value: Any) -> str:
    return str(value or "").strip().upper()


def parse_json_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return {normalize_body(key): item for key, item in value.items()}
    text = str(value or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    if not isinstance(parsed, Mapping):
        return {}
    return {normalize_body(key): item for key, item in parsed.items()}


def entity_members(name: Any) -> tuple[str, ...]:
    body = normalize_body(name)
    if body == "AVG(ALL)":
        return AVG_ALL_MEMBERS
    if body.startswith("AVG(") and body.endswith(")"):
        inner = body[4:-1].strip()
        if inner in {"ALL", "ALL7"}:
            return AVG_ALL_MEMBERS
        members = tuple(normalize_body(item) for item in inner.split(",") if normalize_body(item))
        return members
    return (body,) if body else ()


def circular_average(values: list[float]) -> float | None:
    finite = [float(value) % 360.0 for value in values if math.isfinite(float(value))]
    if not finite:
        return None
    sin_sum = sum(math.sin(math.radians(value)) for value in finite)
    cos_sum = sum(math.cos(math.radians(value)) for value in finite)
    if abs(sin_sum) < 1e-15 and abs(cos_sum) < 1e-15:
        return None
    return math.degrees(math.atan2(sin_sum, cos_sum)) % 360.0


def entity_longitude(snapshot: Mapping[str, Any], name: Any) -> float | None:
    normalized = {normalize_body(key): value for key, value in snapshot.items()}
    values: list[float] = []
    for member in entity_members(name):
        try:
            value = float(normalized[member])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(value):
            values.append(value)
    if len(values) == 1:
        return values[0] % 360.0
    return circular_average(values)


def directed_angle_delta(left: float, right: float) -> float:
    return (float(right) - float(left)) % 360.0


def aspect_orb(left: float, right: float, aspect: Any) -> tuple[float, float] | None:
    name = str(aspect or "").strip().lower()
    target = ASPECT_ANGLES.get(name)
    if target is None:
        return None
    directed = directed_angle_delta(left, right)
    if target > 180.0:
        return abs(directed - target), directed
    separation = min(directed, 360.0 - directed)
    return abs(separation - target), separation


def event_scope(is_natal: Any) -> str:
    return "TN" if bool(is_natal) else "TT"


def scoped_family_key(pair_key: Any, aspect: Any, scope: Any) -> str:
    scope_name = str(scope or "UNKNOWN").strip().upper() or "UNKNOWN"
    return f"{scope_name}::{str(pair_key or '').strip().upper()}::{str(aspect or '').strip().lower()}"


def resolve_event_roles(event: Mapping[str, Any]) -> dict[str, Any]:
    """Recover transit/natal roles lost when an unordered pair was alphabetically sorted.

    Older JDML4 rows retain transit and natal longitude snapshots but store only sorted
    ``b1``/``b2`` labels. For natal events, evaluate both possible orientations at the
    recorded peak snapshot and select the one with the smaller aspect orb.
    """

    b1 = normalize_body(event.get("b1"))
    b2 = normalize_body(event.get("b2"))
    aspect = str(event.get("aspect") or "").strip().lower()
    is_natal = bool(event.get("is_natal", False))
    scope = event_scope(is_natal)

    if not is_natal:
        return {
            "event_scope": scope,
            "event_transit_body": "",
            "event_natal_body": "",
            "event_role_resolution_status": "not_applicable_transit_transit",
            "event_role_best_orb_deg": None,
            "event_role_alternate_orb_deg": None,
        }

    explicit_transit = normalize_body(event.get("event_transit_body") or event.get("transit_body"))
    explicit_natal = normalize_body(event.get("event_natal_body") or event.get("natal_body"))
    if explicit_transit and explicit_natal:
        return {
            "event_scope": scope,
            "event_transit_body": explicit_transit,
            "event_natal_body": explicit_natal,
            "event_role_resolution_status": "explicit",
            "event_role_best_orb_deg": None,
            "event_role_alternate_orb_deg": None,
        }

    transit_snapshot = parse_json_mapping(event.get("planet_longitudes_json"))
    natal_snapshot = parse_json_mapping(event.get("natal_longitudes_json"))
    candidates: list[tuple[float, str, str]] = []
    for transit_body, natal_body in ((b1, b2), (b2, b1)):
        transit_lon = entity_longitude(transit_snapshot, transit_body)
        natal_lon = entity_longitude(natal_snapshot, natal_body)
        if transit_lon is None or natal_lon is None:
            continue
        result = aspect_orb(transit_lon, natal_lon, aspect)
        if result is not None and math.isfinite(result[0]):
            candidates.append((float(result[0]), transit_body, natal_body))

    if not candidates:
        return {
            "event_scope": scope,
            "event_transit_body": "",
            "event_natal_body": "",
            "event_role_resolution_status": "unresolved_missing_peak_snapshots",
            "event_role_best_orb_deg": None,
            "event_role_alternate_orb_deg": None,
        }

    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    best = candidates[0]
    alternate = candidates[1][0] if len(candidates) > 1 else None
    status = "inferred_from_peak_snapshot_min_orb"
    if b1 == b2:
        status = "same_body_roles_equivalent"
    elif alternate is not None and abs(float(alternate) - best[0]) <= 1e-9:
        status = "ambiguous_equal_orb"
    return {
        "event_scope": scope,
        "event_transit_body": best[1],
        "event_natal_body": best[2],
        "event_role_resolution_status": status,
        "event_role_best_orb_deg": best[0],
        "event_role_alternate_orb_deg": alternate,
    }


def enrich_event_roles_frame(frame: Any) -> Any:
    out = frame.copy()
    if out.empty:
        return out
    resolved = [resolve_event_roles(row) for row in out.to_dict(orient="records")]
    for key in (
        "event_scope",
        "event_transit_body",
        "event_natal_body",
        "event_role_resolution_status",
        "event_role_best_orb_deg",
        "event_role_alternate_orb_deg",
    ):
        out[key] = [item.get(key) for item in resolved]
    return out
