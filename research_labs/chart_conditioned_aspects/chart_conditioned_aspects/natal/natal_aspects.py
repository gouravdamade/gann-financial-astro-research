from __future__ import annotations

from itertools import combinations

from ..models import GraphEdge, NatalChartSnapshot
from ..profiles import ResearchProfiles
from .dignity import zodiac_sign


def angular_distance(left: float, right: float) -> float:
    directed = abs((float(left) - float(right)) % 360.0)
    return min(directed, 360.0 - directed)


def compile_conjunction_edges(
    snapshot: NatalChartSnapshot,
    profiles: ResearchProfiles,
) -> tuple[GraphEdge, ...]:
    orb_limit = float(profiles.graph["conjunction_orb_deg"])
    edges: list[GraphEdge] = []
    for (left, left_lon), (right, right_lon) in combinations(
        snapshot.planet_longitudes, 2
    ):
        distance = angular_distance(left_lon, right_lon)
        if distance <= orb_limit:
            edges.append(
                GraphEdge(
                    source=f"PLANET:{left}",
                    target=f"PLANET:{right}",
                    edge_type="CONJUNCTION",
                    status="CONFIGURED_ANGULAR_GEOMETRY",
                    orb_deg=distance,
                    evidence_refs=(str(profiles.graph["profile_id"]),),
                )
            )
    return tuple(edges)


def compile_dispositor_edges(
    snapshot: NatalChartSnapshot,
    profiles: ResearchProfiles,
) -> tuple[GraphEdge, ...]:
    sequence = tuple(str(item).upper() for item in profiles.lordship["sign_sequence"])
    rulers = {
        str(sign).upper(): str(ruler).upper()
        for sign, ruler in profiles.lordship["sign_rulers"].items()
    }
    available = {planet for planet, _ in snapshot.planet_longitudes}
    edges: list[GraphEdge] = []
    for planet, longitude in snapshot.planet_longitudes:
        ruler = rulers[zodiac_sign(longitude, sequence)]
        if ruler == planet or ruler not in available:
            continue
        edges.append(
            GraphEdge(
                source=f"PLANET:{planet}",
                target=f"PLANET:{ruler}",
                edge_type="DISPOSITOR",
                status="DETERMINISTIC_SIGN_RULER_PROFILE",
                evidence_refs=(str(profiles.lordship["profile_id"]),),
            )
        )
    return tuple(edges)
