from __future__ import annotations

from ..profiles import ResearchProfiles


def compile_yoga_context(
    profiles: ResearchProfiles,
) -> tuple[tuple[object, ...], tuple[str, ...]]:
    if profiles.graph.get("yoga_edges_enabled"):
        raise ValueError("Milestone 1 does not permit uncertified yoga edges")
    return (), ("YOGA_EDGES_DISABLED_PENDING_SOURCE_CERTIFICATION",)
