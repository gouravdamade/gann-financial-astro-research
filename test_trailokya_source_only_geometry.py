"""Regression coverage for the TN1 Trailokya source-only compatibility route."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from sbc.chakra_lab import ChakraLabActorSelection, ChakraLabRequest
from sbc.models import GeoLocation
from sbc.trailokya_native_adapter import NATIVE_GRID_PROFILE_ID, TRAILOKYA_PROFILE_ID
from sbc.trailokya_source_only_geometry import build_trailokya_source_only_geometry


def _request(*actors: ChakraLabActorSelection) -> ChakraLabRequest:
    return ChakraLabRequest(
        at=datetime(2026, 7, 17, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
        location=GeoLocation(28.6139, 77.2090, "Asia/Kolkata", 216.0),
        bodies=("SUN", "MOON", "JUPITER"),
        actors=actors,
        grid_profile_id=NATIVE_GRID_PROFILE_ID,
        vedha_profile_id=TRAILOKYA_PROFILE_ID,
    )


def test_native_adapter_requires_the_explicit_source_profile() -> None:
    request = _request(ChakraLabActorSelection(body="SUN"))
    wrong_profile = ChakraLabRequest(
        **{**request.__dict__, "vedha_profile_id": "phaladeepika_editor_vedha_guidance_v1"}
    )

    with pytest.raises(ValueError, match="requires vedhaProfileId"):
        build_trailokya_source_only_geometry(wrong_profile)


def test_generic_grid_fallback_remains_fail_closed() -> None:
    request = _request(ChakraLabActorSelection(body="MOON"))
    generic_grid = ChakraLabRequest(
        **{**request.__dict__, "grid_profile_id": "sbc_81_rotation_normalized_partial_v1"}
    )

    with pytest.raises(ValueError, match="TRAILOKYA_SOURCE_NATIVE_GRID_ADAPTER_REQUIRED"):
        build_trailokya_source_only_geometry(generic_grid)


def test_explicit_native_grid_returns_a_read_only_score_free_snapshot() -> None:
    payload = build_trailokya_source_only_geometry(
        _request(ChakraLabActorSelection(body="JUPITER", motion_class="MEAN"))
    )

    assert payload["contract"] == "SBC_TRAILOKYA_1972_SOURCE_ONLY_GEOMETRY_V1"
    assert payload["nativeSnapshot"]["board"]["gridProfileId"] == NATIVE_GRID_PROFILE_ID
    assert payload["nativeSnapshot"]["board"]["cellCount"] == 81
    assert payload["guardrails"]["categoricalGeometryOnly"] is True
    assert payload["guardrails"]["scoreAggregationUsed"] is False
    assert payload["guardrails"]["marketDirectionInferred"] is False
    assert payload["guardrails"]["executionAllowed"] is False
