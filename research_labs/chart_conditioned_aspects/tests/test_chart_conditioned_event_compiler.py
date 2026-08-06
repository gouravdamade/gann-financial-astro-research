from __future__ import annotations

from datetime import datetime, timezone

from chart_conditioned_aspects.founder_chart_registry import (
    load_founder_chart_identity_records,
)
from chart_conditioned_aspects.profiles import load_research_profiles
from chart_conditioned_aspects.transits.chart_conditioned_event_compiler import (
    CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT,
    compile_chart_conditioned_transit_event_range_for_test,
)


UTC = timezone.utc
WINDOW_START = datetime(2025, 4, 1, tzinfo=UTC)


def _test_longitude(body: str, at: datetime) -> float:
    """One deterministic moving Moon, with historic natal longitude fixed at zero."""
    if at.year < 1900:
        return 0.0
    hours = (at - WINDOW_START).total_seconds() / 3600.0
    return (356.0 + hours) % 360.0


def _compile() -> dict:
    identity = load_founder_chart_identity_records()[0]
    return compile_chart_conditioned_transit_event_range_for_test(
        identity=identity,
        range_start_utc="2025-04-01T00:00:00Z",
        range_end_utc="2025-04-01T12:00:00Z",
        longitude=_test_longitude,
        profiles=load_research_profiles(),
        body_universe=("MOON",),
        boundary_search_padding_days=2,
    )


def test_compiler_produces_repeatable_complete_tn_event_identities() -> None:
    first = _compile()
    second = _compile()

    assert first["contract"] == CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT
    assert first["events"] == second["events"]
    assert first["generatorHash"] == second["generatorHash"]
    assert first["events"]
    event = next(item for item in first["events"] if item["aspectType"] == "conjunction")
    assert event["eventId"].startswith("TN_")
    assert event["eventHash"]
    assert event["chartId"] == first["chartId"]
    assert event["chartHypothesisId"] == first["chartHypothesisId"]
    assert event["applyingStartUtc"] < event["exactUtc"] < event["separatingEndUtc"]
    assert event["startUtc"] == event["applyingStartUtc"]
    assert event["endUtc"] == event["separatingEndUtc"]
    assert event["polarity"] is None
    assert event["magnitude"] is None
    assert event["financialInterpretation"] is None


def test_compiler_stays_astronomy_only_without_price_or_sbc_dependencies() -> None:
    result = _compile()

    assert result["astronomyContract"] == "RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1"
    assert result["ayanamsha"] == "Raman"
    assert result["nodePolicy"] == "TRUE_NODE_RAHU_KETU_OPPOSITION_V1"
    assert result["guardrails"] == {
        "astronomyOnly": True,
        "polarityAssigned": False,
        "magnitudeAssigned": False,
        "priceDataRead": False,
        "sbcRead": False,
        "llmRead": False,
        "executionAllowed": False,
        "automaticOrderPlacement": False,
    }
