from __future__ import annotations

import pytest

from chart_conditioned_aspects.transits import adapt_explicit_tn_event


def payload() -> dict[str, object]:
    return {
        "event_id": "TN-1",
        "event_contract": "EXPLICIT_TN_EVENT_V1",
        "event_scope": "TN",
        "event_transit_body": "SATURN",
        "event_natal_body": "MOON",
        "event_role_resolution_status": "explicit",
        "chart_id": "ORG-TAURUS",
        "aspect_type": "square",
        "observed_separation_deg": 90.4,
        "event_timestamp_utc": "2026-07-22T12:00:00+00:00",
        "evidence_available_at_utc": "2026-07-22T12:00:00+00:00",
    }


def test_adapter_accepts_explicit_tn_and_recomputes_orb(profiles) -> None:
    raw = payload()
    raw["applying"] = "false"
    event = adapt_explicit_tn_event(raw, profiles)
    assert event.transit_body == "SATURN"
    assert event.natal_target == "MOON"
    assert event.orb_deg == pytest.approx(0.4)
    assert event.applying is False


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("event_scope", "TT", "explicit TN"),
        (
            "event_role_resolution_status",
            "inferred_from_peak_snapshot_min_orb",
            "inferred",
        ),
        ("observed_separation_deg", 97.0, "exceeds"),
    ],
)
def test_adapter_rejects_wrong_scope_roles_or_orb(
    profiles, field, value, message
) -> None:
    raw = payload()
    raw[field] = value
    with pytest.raises(ValueError, match=message):
        adapt_explicit_tn_event(raw, profiles)


def test_adapter_rejects_retrospective_fields_at_any_depth(profiles) -> None:
    raw = payload()
    raw["metadata"] = {"future_return": 2.4}
    with pytest.raises(ValueError, match="forbidden"):
        adapt_explicit_tn_event(raw, profiles)
