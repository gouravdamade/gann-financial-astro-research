from datetime import datetime, timedelta, timezone

from sbc.product_first_timing_phase import (
    PRODUCT_FIRST_TIMING_PHASE_CONTRACT,
    compile_product_first_timing_phase,
)


UTC = timezone.utc


def event(event_id: str, start: datetime, exact: datetime, end: datetime) -> dict[str, str]:
    return {
        "eventId": event_id,
        "label": event_id,
        "startUtc": start.isoformat(),
        "exactUtc": exact.isoformat(),
        "endUtc": end.isoformat(),
    }


def test_timing_phase_is_disabled_and_fail_closed_by_default():
    compiled = compile_product_first_timing_phase(
        enabled=False,
        as_of_utc=datetime(2026, 8, 1, tzinfo=UTC),
        aspects=[],
        contributions=[],
    )
    assert compiled["marketDirection"] == "ABSTAIN"
    assert compiled["guardrails"]["executionAllowed"] is False
    assert compiled["vectors"] == []
    assert compiled["state"] == "UNKNOWN"


def test_asymmetric_windows_use_independent_normalization():
    exact = datetime(2026, 8, 1, 12, tzinfo=UTC)
    aspect_data = event("asymmetric", exact - timedelta(seconds=100), exact, exact + timedelta(seconds=80))
    applying = compile_product_first_timing_phase(
        enabled=True,
        as_of_utc=exact - timedelta(seconds=50),
        aspects=[aspect_data],
        contributions=[{"body": "SUN", "signedGuidanceUnits": 2.0}],
    )
    separating = compile_product_first_timing_phase(
        enabled=True,
        as_of_utc=exact + timedelta(seconds=40),
        aspects=[aspect_data],
        contributions=[{"body": "SUN", "signedGuidanceUnits": 2.0}],
    )
    assert applying["contract"] == PRODUCT_FIRST_TIMING_PHASE_CONTRACT
    assert applying["activeEvents"][0]["normalizedLifecycleProgress"] == -0.5
    assert separating["activeEvents"][0]["normalizedLifecycleProgress"] == 0.5
    assert applying["activeEvents"][0]["symmetricTimingDeclared"] is False
    assert applying["state"] == "UNLINKED_EVENT_GEOMETRY"
    assert applying["aggregateWithheld"] is True
    assert applying["vectors"] == []
    assert applying["realUnits"] is None


def test_overlaps_keep_lifecycles_but_do_not_cartesian_expand_contributions():
    as_of = datetime(2026, 8, 1, 12, tzinfo=UTC)
    compiled = compile_product_first_timing_phase(
        enabled=True,
        as_of_utc=as_of,
        aspects=[
            event("one", as_of - timedelta(hours=2), as_of - timedelta(minutes=30), as_of + timedelta(hours=1)),
            event("two", as_of - timedelta(hours=1), as_of + timedelta(minutes=15), as_of + timedelta(hours=2)),
        ],
        contributions=[{"body": "SUN", "signedGuidanceUnits": 2.0}, {"body": "MOON", "signedGuidanceUnits": None}],
    )
    assert [item["eventId"] for item in compiled["activeEvents"]] == ["one", "two"]
    assert compiled["vectors"] == []
    assert compiled["unlinkedResolvedContributionCount"] == 1
    assert compiled["unknownVectorCount"] == 1
    assert compiled["sourceGapId"] == "EVENT_CONTRIBUTION_LINK_PROFILE_MISSING"
    assert compiled["marketDirection"] == "ABSTAIN"


def test_invalid_zero_length_span_fails_closed():
    exact = datetime(2026, 8, 1, 12, tzinfo=UTC)
    compiled = compile_product_first_timing_phase(
        enabled=True,
        as_of_utc=exact,
        aspects=[event("invalid", exact, exact, exact + timedelta(minutes=1))],
        contributions=[],
    )
    assert compiled["state"] == "UNKNOWN_INVALID_EVENT_WINDOW"
    assert compiled["activeEvents"][0]["lifecycle"] == "UNKNOWN"
    assert compiled["calculationId"]
    assert compiled["marketDirection"] == "ABSTAIN"


def test_no_active_events_stays_unknown_and_abstains():
    now = datetime(2026, 8, 1, 12, tzinfo=UTC)
    compiled = compile_product_first_timing_phase(
        enabled=True,
        as_of_utc=now,
        aspects=[event("later", now + timedelta(minutes=1), now + timedelta(minutes=2), now + timedelta(minutes=3))],
        contributions=[],
    )
    assert compiled["state"] == "UNKNOWN"
    assert compiled["activeEvents"] == []
    assert compiled["calculationId"] is None
    assert compiled["marketDirection"] == "ABSTAIN"
