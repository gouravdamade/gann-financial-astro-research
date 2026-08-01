from datetime import datetime, timedelta, timezone

from sbc.product_first_timing_phase import compile_product_first_timing_phase


UTC = timezone.utc


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


def test_timing_phase_keeps_each_overlapping_event_independent():
    as_of = datetime(2026, 8, 1, 12, tzinfo=UTC)
    compiled = compile_product_first_timing_phase(
        enabled=True,
        as_of_utc=as_of,
        aspects=[
            {"eventId": "one", "label": "First", "startUtc": as_of - timedelta(hours=2), "exactUtc": as_of - timedelta(minutes=30), "endUtc": as_of + timedelta(hours=1)},
            {"eventId": "two", "label": "Second", "startUtc": as_of - timedelta(hours=1), "exactUtc": as_of + timedelta(minutes=15), "endUtc": as_of + timedelta(hours=2)},
        ],
        contributions=[{"body": "SUN", "target": "A", "signedGuidanceUnits": 2.0}],
    )
    assert [event["eventId"] for event in compiled["activeEvents"]] == ["one", "two"]
    assert {vector["eventId"] for vector in compiled["vectors"]} == {"one", "two"}
    assert compiled["marketDirection"] == "ABSTAIN"
    assert compiled["calculationId"]
