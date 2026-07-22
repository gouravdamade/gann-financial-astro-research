from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from chart_conditioned_aspects import (
    GeoLocation,
    NatalChartSnapshot,
    OrganizationChartHypothesis,
    SourceRef,
    load_research_profiles,
)
from chart_conditioned_aspects.natal import compile_natal_structure


NOW = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
ASTRONOMY_CONTRACT = "RAMAN_SIDEREAL_SWISSEPH_V1"


@pytest.fixture(scope="session")
def profiles():
    return load_research_profiles()


def make_chart(
    *,
    chart_id: str = "ORG-TAURUS",
    time_accuracy: str = "EXACT_TIME",
) -> OrganizationChartHypothesis:
    has_time = time_accuracy in {"EXACT_TIME", "DOCUMENTED_EXCHANGE_OPEN"}
    return OrganizationChartHypothesis(
        chart_id=chart_id,
        instrument_id="TEST.EQUITY",
        entity_id="TEST-ENTITY",
        chart_type="incorporation",
        timestamp_utc=NOW,
        location=GeoLocation(
            name="Mumbai" if has_time else "date-only",
            latitude=19.076 if has_time else None,
            longitude=72.8777 if has_time else None,
        ),
        sources=(
            SourceRef(
                source_id="TEST-FILING",
                locator="fixture",
                evidence_class="EMPIRICAL_MARKET_EVIDENCE",
                status="TEST_PROVENANCE",
                confidence=1.0,
            ),
        ),
        time_accuracy=time_accuracy,  # type: ignore[arg-type]
        ayanamsa="RAMAN",
        house_model="WHOLE_SIGN",
        astronomy_contract=ASTRONOMY_CONTRACT,
        effective_from=date(2020, 1, 1),
        status="ACCEPTED_RESEARCH",
        accepted_by="test-reviewer",
        accepted_at=NOW,
    )


def make_snapshot(
    chart: OrganizationChartHypothesis,
    *,
    ascendant_sign: str | None = "TAURUS",
    conjunction: bool = False,
) -> NatalChartSnapshot:
    longitudes = {
        "SUN": 10.0,
        "MOON": 45.0,
        "MARS": 80.0,
        "MERCURY": 110.0,
        "JUPITER": 295.0 if conjunction else 150.0,
        "VENUS": 200.0,
        "SATURN": 300.0,
    }
    houses = {
        "SUN": 1,
        "MOON": 2,
        "MARS": 3,
        "MERCURY": 4,
        "JUPITER": 5,
        "VENUS": 6,
        "SATURN": 7,
    }
    if not chart.allows_houses:
        houses = {}
        ascendant_sign = None
    return NatalChartSnapshot.from_mappings(
        chart_id=chart.chart_id,
        captured_at_utc=NOW,
        planet_longitudes=longitudes,
        house_placements=houses,
        retrograde_flags={planet: False for planet in longitudes},
        ascendant_sign=ascendant_sign,
        astronomy_contract=ASTRONOMY_CONTRACT,
    )


def make_structure(
    profiles, *, ascendant_sign: str = "TAURUS", conjunction: bool = False
):
    chart = make_chart(chart_id=f"ORG-{ascendant_sign}")
    snapshot = make_snapshot(
        chart, ascendant_sign=ascendant_sign, conjunction=conjunction
    )
    return compile_natal_structure(chart, snapshot, profiles)
