"""R4-T2 deterministic fixtures for the narrow Trailokya geometry path."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sbc.chakra_lab import ChakraLabActorSelection, ChakraLabRequest
from sbc.models import GeoLocation
from sbc.trailokya_source_only_geometry import (
    CONTRACT,
    TRAILOKYA_NATIVE_GRID_PROFILE_ID,
    TRAILOKYA_PROFILE_ID,
    build_trailokya_source_only_geometry,
    summarize_target_reach,
)
from sbc.vedha import MotionClass


def _request(*actors: ChakraLabActorSelection) -> ChakraLabRequest:
    return ChakraLabRequest(
        at=datetime(2026, 7, 17, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
        location=GeoLocation(28.6139, 77.2090, "Asia/Kolkata", 216.0),
        bodies=("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"),
        actors=actors,
        vedha_profile_id=TRAILOKYA_PROFILE_ID,
    )


def test_fixed_bodies_emit_all_three_rays_without_nature_or_scores() -> None:
    request = _request(ChakraLabActorSelection(body="SUN"))
    try:
        build_trailokya_source_only_geometry(request)
    except ValueError as exc:
        assert "TRAILOKYA_SOURCE_NATIVE_GRID_ADAPTER_REQUIRED" in str(exc)
    else:
        raise AssertionError("a non-native grid must not render Trailokya source geometry")


def test_all_variable_motion_states_map_to_the_approved_single_ray() -> None:
    expected = {
        MotionClass.RETROGRADE: "RIGHT",
        MotionClass.DIRECT_SWIFT: "LEFT",
        MotionClass.MEAN: "FRONT",
    }
    from sbc.trailokya_source_only_geometry import _directions_for_actor

    for motion, direction in expected.items():
        directions, unavailable, _reason = _directions_for_actor("MARS", motion.value)
        assert unavailable is None
        assert [item.value for item in directions] == [direction]


def test_missing_or_invalid_variable_motion_fails_closed() -> None:
    from sbc.trailokya_source_only_geometry import _directions_for_actor

    assert _directions_for_actor("SATURN", None)[1] == "MOTION_REQUIRED"
    assert _directions_for_actor("SATURN", "UNSPECIFIED")[1] == "MOTION_REQUIRED"


def test_only_explicit_trailokya_profile_is_allowed() -> None:
    request = _request(ChakraLabActorSelection(body="MOON"))
    request = ChakraLabRequest(**{**request.__dict__, "vedha_profile_id": "phaladeepika_editor_vedha_guidance_v1"})
    try:
        build_trailokya_source_only_geometry(request)
    except ValueError as exc:
        assert "requires vedhaProfileId" in str(exc)
    else:
        raise AssertionError("wrong profile must fail closed")


def test_source_native_adapter_absence_fails_closed_not_to_a_legacy_grid() -> None:
    request = _request(ChakraLabActorSelection(body="MOON"))
    request = ChakraLabRequest(**{**request.__dict__, "grid_profile_id": TRAILOKYA_NATIVE_GRID_PROFILE_ID})
    try:
        build_trailokya_source_only_geometry(request)
    except FileNotFoundError as exc:
        assert TRAILOKYA_NATIVE_GRID_PROFILE_ID in str(exc)
    else:
        raise AssertionError("the absent source-native grid adapter must fail closed")


def test_target_reach_summary_preserves_known_and_unknown_mapping_states() -> None:
    assert summarize_target_reach((
        {"reachState": "REACHED"},
        {"reachState": "NOT_REACHED"},
    )) == "REACHED"
    assert summarize_target_reach((
        {"reachState": "NOT_REACHED"},
        {"reachState": "NOT_REACHED"},
    )) == "NOT_REACHED"
    assert summarize_target_reach((
        {"reachState": "UNKNOWN"},
        {"reachState": "UNKNOWN"},
    )) == "UNKNOWN"
    assert summarize_target_reach((
        {"reachState": "NOT_REACHED"},
        {"reachState": "UNKNOWN"},
    )) == "PARTIAL_UNKNOWN"
