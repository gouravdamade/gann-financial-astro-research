"""Compatibility route for the superseded Trailokya geometry endpoint.

TN1 retired the historic generic-grid traversal. Callers retained from older
desktop candidates receive a native source snapshot, while target identity is
resolved only through :mod:`sbc.trailokya_native_adapter`.
"""
from __future__ import annotations

from typing import Any

from .chakra_lab import ChakraLabEngine, ChakraLabRequest
from .trailokya_native_adapter import (
    NATIVE_GRID_PROFILE_ID,
    TRAILOKYA_PROFILE_ID,
    build_trailokya_native_snapshot,
)


def build_trailokya_source_only_geometry(
    request: ChakraLabRequest,
    *,
    engine: ChakraLabEngine | None = None,
) -> dict[str, Any]:
    """Return native source context without a generic grid or target walk."""
    if request.vedha_profile_id != TRAILOKYA_PROFILE_ID:
        raise ValueError("Trailokya source-only geometry requires vedhaProfileId=SBC_TRAILOKYA_1972_V1")
    if request.grid_profile_id != NATIVE_GRID_PROFILE_ID:
        raise ValueError(
            "TRAILOKYA_SOURCE_NATIVE_GRID_ADAPTER_REQUIRED: source-only geometry "
            "cannot borrow a Phaladeepika or normalized generic grid profile"
        )
    return {
        "contract": "SBC_TRAILOKYA_1972_SOURCE_ONLY_GEOMETRY_V1",
        "schemaVersion": 2,
        "nativeSnapshot": build_trailokya_native_snapshot(request, engine=engine),
        "deprecated": "Use TRAILOKYA_1972_ENUMERATED_TARGET_RESOLUTION_V1 for target identity.",
        "guardrails": {
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
        },
    }
