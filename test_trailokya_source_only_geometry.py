"""R4-T2 deterministic fixtures for the narrow Trailokya geometry path."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sbc.chakra_lab import ChakraLabActorSelection, ChakraLabRequest
from sbc.models import GeoLocation
from sbc.trailokya_source_only_geometry import (
    CONTRACT,
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
    report = build_trailokya_source_only_geometry(
        _request(ChakraLabActorSelection(body="SUN"))
    )
    assert report["contract"] == CONTRACT
    assert {ray["direction"] for ray in report["rays"]} == {"LEFT", "FRONT", "RIGHT"}
    assert report["approval"]["founderDecision"] == "APPROVED_FOR_SOURCE_ONLY_WITH_LIMITS"
    assert report["snapshot"]["guidance"] is None
    assert all(value is False for key, value in report["guardrails"].items() if key.endswith("Used") or key.endswith("Generated") or key.endswith("Inferred") or key.endswith("Allowed"))


def test_all_variable_motion_states_map_to_the_approved_single_ray() -> None:
    expected = {
        MotionClass.RETROGRADE: "RIGHT",
        MotionClass.DIRECT_SWIFT: "LEFT",
        MotionClass.MEAN: "FRONT",
    }
    for motion, direction in expected.items():
        report = build_trailokya_source_only_geometry(
            _request(ChakraLabActorSelection(body="MARS", motion_class=motion))
        )
        rays = [ray for ray in report["rays"] if ray["body"] == "MARS"]
        assert [ray["direction"] for ray in rays] == [direction]


def test_missing_or_invalid_variable_motion_fails_closed() -> None:
    missing = build_trailokya_source_only_geometry(_request(ChakraLabActorSelection(body="SATURN")))
    assert not missing["rays"]
    assert missing["unavailable"][0]["state"] == "MOTION_REQUIRED"
    invalid = build_trailokya_source_only_geometry(
        _request(ChakraLabActorSelection(body="SATURN", motion_class="UNSPECIFIED"))
    )
    assert not invalid["rays"]
    assert invalid["unavailable"][0]["state"] == "MOTION_REQUIRED"


def test_only_explicit_trailokya_profile_is_allowed() -> None:
    request = _request(ChakraLabActorSelection(body="MOON"))
    request = ChakraLabRequest(**{**request.__dict__, "vedha_profile_id": "phaladeepika_editor_vedha_guidance_v1"})
    try:
        build_trailokya_source_only_geometry(request)
    except ValueError as exc:
        assert "requires vedhaProfileId" in str(exc)
    else:
        raise AssertionError("wrong profile must fail closed")


def test_missing_target_mapping_is_exposed_as_unavailable_not_approximated(monkeypatch) -> None:
    import sbc.trailokya_source_only_geometry as geometry

    def unavailable(*_args, **_kwargs):
        raise ValueError("TEST_TARGET_MAPPING_MISSING")

    monkeypatch.setattr(geometry, "_targets_for_direction", unavailable)
    report = geometry.build_trailokya_source_only_geometry(
        _request(ChakraLabActorSelection(body="MOON"))
    )
    assert report["rays"] == []
    assert report["unavailable"]
    assert report["unavailable"][0]["state"] == "TARGET_MAPPING_UNAVAILABLE"


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
