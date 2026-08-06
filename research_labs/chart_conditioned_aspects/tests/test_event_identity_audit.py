from __future__ import annotations

from datetime import datetime, timedelta, timezone

from chart_conditioned_aspects.founder_chart_registry import load_founder_chart_identity_records
from chart_conditioned_aspects.profiles import load_research_profiles
from chart_conditioned_aspects.transits.chart_conditioned_event_compiler import (
    compile_chart_conditioned_transit_event_range_for_test,
)
from chart_conditioned_aspects.transits.event_identity_audit import (
    audit_continuous_orb_window,
    verify_event_identity,
)


UTC = timezone.utc
ORIGIN = datetime(2025, 4, 1, tzinfo=UTC)


def _hours(at: datetime) -> float:
    return (at - ORIGIN).total_seconds() / 3600.0


def _direct_wrap_longitude(body: str, at: datetime) -> float:
    return (357.0 + _hours(at)) % 360.0


def _two_pass_retrograde_longitude(body: str, at: datetime) -> float:
    hours = _hours(at)
    return (90.0 + 0.25 * (hours - 2.0) * (hours - 6.0)) % 360.0


def _three_pass_station_loop_longitude(body: str, at: datetime) -> float:
    hours = _hours(at)
    return (90.0 + 0.1 * (hours - 2.0) * (hours - 4.0) * (hours - 6.0)) % 360.0


def _station_without_exact_longitude(body: str, at: datetime) -> float:
    hours = _hours(at)
    return (90.0 + 1.0 + 0.125 * (hours - 4.0) ** 2) % 360.0


def test_simple_direct_pass_and_angular_wrap_are_single_pass_verified() -> None:
    result = audit_continuous_orb_window(
        transit_body="MOON",
        natal_longitude=0.0,
        exact_angle_deg=0.0,
        max_orb_deg=3.0,
        applying_start_utc=ORIGIN,
        separating_end_utc=ORIGIN + timedelta(hours=6),
        longitude=_direct_wrap_longitude,
    )

    assert result["status"] == "SINGLE_PASS_VERIFIED"
    assert len(result["candidateExactPasses"]) == 1
    assert result["candidateExactPasses"][0]["exactUtc"] == "2025-04-01T03:00:00Z"
    assert result["boundaryVerification"]["valid"] is True
    assert result["motionPhaseAtExact"]["phase"] == "DIRECT"


def test_retrograde_two_pass_window_fails_closed_as_multi_pass() -> None:
    result = audit_continuous_orb_window(
        transit_body="MERCURY",
        natal_longitude=0.0,
        exact_angle_deg=90.0,
        max_orb_deg=3.0,
        applying_start_utc=ORIGIN,
        separating_end_utc=ORIGIN + timedelta(hours=8),
        longitude=_two_pass_retrograde_longitude,
    )

    assert result["status"] == "MULTI_PASS_EVENT_IDENTITY_UNRESOLVED"
    assert len(result["candidateExactPasses"]) == 2
    assert result["stationOrMotionReversalTimestamps"]
    assert "MULTIPLE_EXACT_CANDIDATES_IN_ONE_CONTINUOUS_ORB_WINDOW" in result["reasons"]


def test_three_pass_station_loop_is_never_collapsed_into_one_identity() -> None:
    result = audit_continuous_orb_window(
        transit_body="MERCURY",
        natal_longitude=0.0,
        exact_angle_deg=90.0,
        max_orb_deg=3.0,
        applying_start_utc=ORIGIN + timedelta(minutes=30),
        separating_end_utc=ORIGIN + timedelta(hours=7, minutes=30),
        longitude=_three_pass_station_loop_longitude,
    )

    assert result["status"] == "MULTI_PASS_EVENT_IDENTITY_UNRESOLVED"
    assert len(result["candidateExactPasses"]) == 3


def test_station_without_exactness_is_explicit_boundary_verification_failure() -> None:
    result = audit_continuous_orb_window(
        transit_body="MERCURY",
        natal_longitude=0.0,
        exact_angle_deg=90.0,
        max_orb_deg=3.0,
        applying_start_utc=ORIGIN,
        separating_end_utc=ORIGIN + timedelta(hours=8),
        longitude=_station_without_exact_longitude,
    )

    assert result["status"] == "BOUNDARY_VERIFICATION_FAILED"
    assert result["stationOrMotionReversalTimestamps"]
    assert result["candidateExactPasses"] == []


def test_exact_pass_close_to_window_boundary_is_still_detected() -> None:
    def fast_longitude(body: str, at: datetime) -> float:
        return (357.0 + (at - ORIGIN).total_seconds() * 0.1) % 360.0

    result = audit_continuous_orb_window(
        transit_body="MOON",
        natal_longitude=0.0,
        exact_angle_deg=0.0,
        max_orb_deg=3.0,
        applying_start_utc=ORIGIN,
        separating_end_utc=ORIGIN + timedelta(minutes=1),
        longitude=fast_longitude,
    )

    assert result["status"] == "SINGLE_PASS_VERIFIED"
    assert result["candidateExactPasses"][0]["exactUtc"] == "2025-04-01T00:00:30Z"


def test_verification_reproduces_immutable_compiler_hash_without_polarity_inputs() -> None:
    identity = load_founder_chart_identity_records()[0]
    compiled = compile_chart_conditioned_transit_event_range_for_test(
        identity=identity,
        range_start_utc="2025-04-01T00:00:00Z",
        range_end_utc="2025-04-01T12:00:00Z",
        longitude=lambda body, at: 0.0 if at.year < 1900 else _direct_wrap_longitude(body, at),
        profiles=load_research_profiles(),
        body_universe=("MOON",),
        boundary_search_padding_days=2,
    )
    event = next(item for item in compiled["events"] if item["aspectType"] == "conjunction")

    result = verify_event_identity(
        event=event,
        natal_longitude=0.0,
        longitude=lambda body, at: 0.0 if at.year < 1900 else _direct_wrap_longitude(body, at),
        expected_instrument_identity=identity.chart.instrument_id,
        expected_chart_id=identity.chart.chart_id,
        expected_chart_hypothesis_id=identity.chart_hypothesis_id,
    )

    assert result["status"] == "SINGLE_PASS_VERIFIED"
    assert result["checks"]["eventHashReproduces"] is True
    assert result["checks"]["eventIdMatchesHash"] is True
    assert result["checks"]["acceptedChartIdentityMatches"] is True
