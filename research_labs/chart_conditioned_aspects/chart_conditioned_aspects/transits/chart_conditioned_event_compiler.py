"""Deterministic transit-to-natal astronomy event compiler.

This module deliberately compiles astronomy geometry only.  It neither reads
market data nor assigns polarity, strength, financial meaning, SBC agreement,
or execution behavior.  Founder review and later evidence admission remain
separate gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Callable, Iterable

import swisseph as swe

from financial_astro_ephemeris import BODY_IDS, configure_ephemeris

from ..founder_chart_registry import FounderChartIdentityRecord, require_founder_chart_identity
from ..models import stable_hash
from ..profiles import ResearchProfiles, load_research_profiles
from .orb_profile import angular_orb, normalized_separation


CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT = "CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1"
EVENT_COMPILER_SCHEMA_VERSION = 1
EVENT_COMPILER_VERSION = "chart_conditioned_transit_event_compiler_v1_20260806"
APPROVED_ASPECT_PROFILE_ID = "ASPECT_STRENGTH_V0"
APPROVED_ASTRONOMY_CONTRACT = "RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1"
EVENT_BOUNDARY_SEARCH_PADDING_DAYS = 180
BOUNDARY_BISECTION_ITERATIONS = 32
EXACT_SEARCH_ITERATIONS = 36

# The source geometry profile has no directional meaning.  This is only the
# available transit/natal body universe for the F2A review packets.
BODY_UNIVERSE = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
    "RAHU",
    "KETU",
)

# Sampling is deliberately tighter for faster bodies.  Boundaries are refined
# against Swiss Ephemeris, so the grid only discovers candidate windows.
SAMPLING_STEP_HOURS = {
    "MOON": 1,
    "SUN": 12,
    "MERCURY": 4,
    "VENUS": 8,
    "MARS": 24,
    "JUPITER": 48,
    "SATURN": 72,
    "RAHU": 24,
    "KETU": 24,
}


def _utc(value: str | datetime, label: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _round_second(value: datetime) -> datetime:
    value = value.astimezone(timezone.utc)
    if value.microsecond >= 500_000:
        value += timedelta(seconds=1)
    return value.replace(microsecond=0)


def _jday_utc(value: datetime) -> float:
    moment = value.astimezone(timezone.utc)
    hour = (
        moment.hour
        + moment.minute / 60.0
        + moment.second / 3600.0
        + moment.microsecond / 3_600_000_000.0
    )
    return float(swe.julday(moment.year, moment.month, moment.day, hour))


def _swiss_version() -> str:
    value = getattr(swe, "version", None) or getattr(swe, "__version__", None)
    return str(value or "pyswisseph_version_unreported")


def _calculate_sidereal_geocentric_longitude(body: str, value: datetime) -> float:
    normalized = str(body).upper()
    if normalized == "KETU":
        return (_calculate_sidereal_geocentric_longitude("RAHU", value) + 180.0) % 360.0
    planet_id = BODY_IDS.get(normalized)
    if planet_id is None:
        raise ValueError(f"unsupported transit/natal body: {body}")
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    result, _ = swe.calc_ut(_jday_utc(value), planet_id, flags)
    return float(result[0]) % 360.0


def _time_grid(start: datetime, end: datetime, hours: int) -> tuple[datetime, ...]:
    points = [start]
    step = timedelta(hours=hours)
    cursor = start
    while cursor + step < end:
        cursor += step
        points.append(cursor)
    if points[-1] != end:
        points.append(end)
    return tuple(points)


def _aspect_contract(
    *,
    aspect_type: str,
    profiles: ResearchProfiles,
) -> dict[str, Any]:
    raw = profiles.aspects.get("aspects", {}).get(aspect_type)
    if not isinstance(raw, dict):
        raise ValueError(f"approved aspect profile does not define {aspect_type}")
    return {
        "profileId": APPROVED_ASPECT_PROFILE_ID,
        "profileHash": profiles.profile_hash,
        "aspectType": aspect_type,
        "exactAngleDeg": float(raw["exact_angle_deg"]),
        "maxOrbDeg": float(raw["max_orb_deg"]),
        "directionPolicy": str(profiles.aspects.get("direction_policy") or ""),
        "doctrineStatus": str(profiles.aspects.get("doctrine_status") or ""),
    }


@dataclass(frozen=True)
class _GeometrySampler:
    natal_longitudes: dict[str, float]
    longitude: Callable[[str, datetime], float]

    def orb(self, transit_body: str, natal_target: str, aspect: dict[str, Any], at: datetime) -> float:
        separation = normalized_separation(
            self.longitude(transit_body, at),
            self.natal_longitudes[natal_target],
        )
        return angular_orb(separation, float(aspect["exactAngleDeg"]))

    def observed_separation(self, transit_body: str, natal_target: str, at: datetime) -> float:
        return normalized_separation(
            self.longitude(transit_body, at),
            self.natal_longitudes[natal_target],
        )


def _refine_boundary(
    *,
    sampler: _GeometrySampler,
    transit_body: str,
    natal_target: str,
    aspect: dict[str, Any],
    left: datetime,
    right: datetime,
) -> datetime:
    """Bisect an inside/outside change; callers verify the bracketing state."""
    max_orb = float(aspect["maxOrbDeg"])
    left_inside = sampler.orb(transit_body, natal_target, aspect, left) <= max_orb
    right_inside = sampler.orb(transit_body, natal_target, aspect, right) <= max_orb
    if left_inside == right_inside:
        raise ValueError("event boundary requires an inside/outside bracket")
    for _ in range(BOUNDARY_BISECTION_ITERATIONS):
        midpoint = left + (right - left) / 2
        midpoint_inside = sampler.orb(transit_body, natal_target, aspect, midpoint) <= max_orb
        if midpoint_inside == left_inside:
            left = midpoint
        else:
            right = midpoint
    return _round_second(left + (right - left) / 2)


def _refine_exact(
    *,
    sampler: _GeometrySampler,
    transit_body: str,
    natal_target: str,
    aspect: dict[str, Any],
    start: datetime,
    end: datetime,
) -> datetime:
    """Find the minimum angular orb in one already bounded event window."""
    left, right = start, end
    for _ in range(EXACT_SEARCH_ITERATIONS):
        span = right - left
        first = left + span / 3
        second = right - span / 3
        first_orb = sampler.orb(transit_body, natal_target, aspect, first)
        second_orb = sampler.orb(transit_body, natal_target, aspect, second)
        if first_orb <= second_orb:
            right = second
        else:
            left = first
    return _round_second(left + (right - left) / 2)


def _event_seed(
    *,
    identity: FounderChartIdentityRecord,
    transit_body: str,
    natal_target: str,
    aspect_type: str,
    start: datetime,
    exact: datetime,
    end: datetime,
    aspect: dict[str, Any],
) -> dict[str, Any]:
    return {
        "eventContract": CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT,
        "sideIdentity": identity.chart.instrument_id.split(":", 1)[1],
        "instrumentIdentity": identity.chart.instrument_id,
        "chartId": identity.chart.chart_id,
        "chartHypothesisId": identity.chart_hypothesis_id,
        "transitBody": transit_body,
        "natalTarget": natal_target,
        "aspectType": aspect_type,
        "applyingStartUtc": _iso(start),
        "exactUtc": _iso(exact),
        "separatingEndUtc": _iso(end),
        "orbContract": aspect,
        "astronomyContract": identity.chart.astronomy_contract,
        "ayanamsha": identity.chart.ayanamsa,
        "nodePolicy": "TRUE_NODE_RAHU_KETU_OPPOSITION_V1",
        "generatorVersion": EVENT_COMPILER_VERSION,
    }


def _compile_pair_events(
    *,
    identity: FounderChartIdentityRecord,
    sampler: _GeometrySampler,
    profiles: ResearchProfiles,
    range_start: datetime,
    range_end: datetime,
    search_start: datetime,
    search_end: datetime,
    body_universe: Iterable[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    aspect_definitions = tuple(
        (name, _aspect_contract(aspect_type=name, profiles=profiles))
        for name in sorted(profiles.aspects.get("aspects", {}))
    )
    bodies = tuple(body_universe)
    for transit_body in bodies:
        grid = _time_grid(search_start, search_end, SAMPLING_STEP_HOURS[transit_body])
        transit_positions = {at: sampler.longitude(transit_body, at) for at in grid}
        for natal_target in bodies:
            for aspect_type, aspect in aspect_definitions:
                max_orb = float(aspect["maxOrbDeg"])
                inside = [
                    angular_orb(
                        normalized_separation(transit_positions[at], sampler.natal_longitudes[natal_target]),
                        float(aspect["exactAngleDeg"]),
                    ) <= max_orb
                    for at in grid
                ]
                index = 0
                while index < len(grid):
                    if not inside[index]:
                        index += 1
                        continue
                    run_start = index
                    while index + 1 < len(grid) and inside[index + 1]:
                        index += 1
                    run_end = index
                    # A complete review identity needs both bounded orb edges.
                    # Events touching the search horizon are exposed only as a
                    # rejected reason; they are never silently clipped.
                    if run_start == 0 or run_end == len(grid) - 1:
                        rejected.append(
                            {
                                "reason": "BOUNDARY_OUTSIDE_SEARCH_HORIZON",
                                "transitBody": transit_body,
                                "natalTarget": natal_target,
                                "aspectType": aspect_type,
                                "observedSearchStartUtc": _iso(grid[run_start]),
                                "observedSearchEndUtc": _iso(grid[run_end]),
                            }
                        )
                        index += 1
                        continue
                    start = _refine_boundary(
                        sampler=sampler,
                        transit_body=transit_body,
                        natal_target=natal_target,
                        aspect=aspect,
                        left=grid[run_start - 1],
                        right=grid[run_start],
                    )
                    end = _refine_boundary(
                        sampler=sampler,
                        transit_body=transit_body,
                        natal_target=natal_target,
                        aspect=aspect,
                        left=grid[run_end],
                        right=grid[run_end + 1],
                    )
                    exact = _refine_exact(
                        sampler=sampler,
                        transit_body=transit_body,
                        natal_target=natal_target,
                        aspect=aspect,
                        start=start,
                        end=end,
                    )
                    if end <= range_start or start >= range_end:
                        index += 1
                        continue
                    seed = _event_seed(
                        identity=identity,
                        transit_body=transit_body,
                        natal_target=natal_target,
                        aspect_type=aspect_type,
                        start=start,
                        exact=exact,
                        end=end,
                        aspect=aspect,
                    )
                    event_hash = stable_hash(seed)
                    events.append(
                        {
                            **seed,
                            "eventId": f"TN_{event_hash[:24]}",
                            "eventHash": event_hash,
                            "startUtc": seed["applyingStartUtc"],
                            "endUtc": seed["separatingEndUtc"],
                            "exactOrbDeg": round(
                                sampler.orb(transit_body, natal_target, aspect, exact), 8
                            ),
                            "observedSeparationDeg": round(
                                sampler.observed_separation(transit_body, natal_target, exact), 8
                            ),
                            "polarity": None,
                            "magnitude": None,
                            "financialInterpretation": None,
                        }
                    )
                    index += 1
    events.sort(key=lambda item: (item["applyingStartUtc"], item["exactUtc"], item["eventId"]))
    rejected.sort(key=lambda item: (item["observedSearchStartUtc"], item["transitBody"], item["natalTarget"], item["aspectType"]))
    return events, rejected


def _generator_hash(profiles: ResearchProfiles) -> str:
    return stable_hash(
        {
            "contract": CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT,
            "schemaVersion": EVENT_COMPILER_SCHEMA_VERSION,
            "generatorVersion": EVENT_COMPILER_VERSION,
            "astronomyContract": APPROVED_ASTRONOMY_CONTRACT,
            "aspectProfileId": APPROVED_ASPECT_PROFILE_ID,
            "profileHash": profiles.profile_hash,
            "bodyUniverse": BODY_UNIVERSE,
            "samplingStepHours": SAMPLING_STEP_HOURS,
            "boundaryPaddingDays": EVENT_BOUNDARY_SEARCH_PADDING_DAYS,
        }
    )


def _compile_event_range(
    *,
    identity: FounderChartIdentityRecord,
    range_start: datetime,
    range_end: datetime,
    profiles: ResearchProfiles,
    longitude: Callable[[str, datetime], float],
    body_universe: Iterable[str] = BODY_UNIVERSE,
    boundary_search_padding_days: int = EVENT_BOUNDARY_SEARCH_PADDING_DAYS,
) -> dict[str, Any]:
    if identity.chart.astronomy_contract != APPROVED_ASTRONOMY_CONTRACT:
        raise ValueError("founder chart does not use the approved transit astronomy contract")
    if identity.chart.ayanamsa.upper() != "RAMAN":
        raise ValueError("founder chart does not use the approved Raman ayanamsha")
    if not identity.chart.effective_at(range_start):
        raise ValueError("founder chart is not effective at the requested visible range")
    bodies = tuple(body_universe)
    if not bodies or any(body not in BODY_UNIVERSE for body in bodies):
        raise ValueError("event compiler body universe must be a non-empty approved subset")
    if identity.chart.timestamp_utc is None:
        raise ValueError("accepted founder chart requires an exact UTC timestamp")
    natal_longitudes = {
        body: longitude(body, identity.chart.timestamp_utc)
        for body in bodies
    }
    sampler = _GeometrySampler(natal_longitudes=natal_longitudes, longitude=longitude)
    padding = timedelta(days=boundary_search_padding_days)
    events, rejected = _compile_pair_events(
        identity=identity,
        sampler=sampler,
        profiles=profiles,
        range_start=range_start,
        range_end=range_end,
        search_start=range_start - padding,
        search_end=range_end + padding,
        body_universe=bodies,
    )
    return {
        "contract": CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT,
        "schemaVersion": EVENT_COMPILER_SCHEMA_VERSION,
        "sideIdentity": identity.chart.instrument_id.split(":", 1)[1],
        "instrumentIdentity": identity.chart.instrument_id,
        "chartId": identity.chart.chart_id,
        "chartHypothesisId": identity.chart_hypothesis_id,
        "rangeStartUtc": _iso(range_start),
        "rangeEndUtc": _iso(range_end),
        "aspectProfileId": APPROVED_ASPECT_PROFILE_ID,
        "astronomyContract": identity.chart.astronomy_contract,
        "historicalCivilTimeConversionPolicy": identity.historical_time_policy_id,
        "ephemerisProvider": "Swiss Ephemeris",
        "ephemerisVersion": _swiss_version(),
        "ayanamsha": "Raman",
        "nodePolicy": "TRUE_NODE_RAHU_KETU_OPPOSITION_V1",
        "generatorVersion": EVENT_COMPILER_VERSION,
        "generatorHash": _generator_hash(profiles),
        "events": events,
        "rejectedEvents": rejected,
        "unknownReasons": [],
        "guardrails": {
            "astronomyOnly": True,
            "polarityAssigned": False,
            "magnitudeAssigned": False,
            "priceDataRead": False,
            "sbcRead": False,
            "llmRead": False,
            "executionAllowed": False,
            "automaticOrderPlacement": False,
        },
    }


@lru_cache(maxsize=24)
def _compile_cached(
    instrument_identity: str,
    range_start_iso: str,
    range_end_iso: str,
) -> dict[str, Any]:
    configure_ephemeris()
    identity = require_founder_chart_identity(instrument_identity)
    profiles = load_research_profiles()
    return _compile_event_range(
        identity=identity,
        range_start=_utc(range_start_iso, "rangeStartUtc"),
        range_end=_utc(range_end_iso, "rangeEndUtc"),
        profiles=profiles,
        longitude=_calculate_sidereal_geocentric_longitude,
    )


def compile_chart_conditioned_transit_event_range(
    *,
    side_identity: str,
    range_start_utc: str | datetime,
    range_end_utc: str | datetime,
    aspect_profile_id: str = APPROVED_ASPECT_PROFILE_ID,
) -> dict[str, Any]:
    """Compile bounded real TN events from canonical backend chart registry.

    No caller can inject a chart identity, natal target, event identity, price,
    SBC field, LLM content, or polarity through this contract.
    """
    side = str(side_identity or "").strip().upper()
    if side not in {"USD", "JPY"}:
        raise ValueError("sideIdentity must be USD or JPY")
    if str(aspect_profile_id or "").strip() != APPROVED_ASPECT_PROFILE_ID:
        raise ValueError("only the approved ASPECT_STRENGTH_V0 geometry profile is available")
    start = _utc(range_start_utc, "rangeStartUtc")
    end = _utc(range_end_utc, "rangeEndUtc")
    if end <= start:
        raise ValueError("rangeEndUtc must be after rangeStartUtc")
    return _compile_cached(f"FX_CURRENCY:{side}", _iso(start), _iso(end))


def compile_chart_conditioned_transit_event_range_for_test(
    *,
    identity: FounderChartIdentityRecord,
    range_start_utc: str | datetime,
    range_end_utc: str | datetime,
    longitude: Callable[[str, datetime], float],
    profiles: ResearchProfiles,
    body_universe: Iterable[str] = BODY_UNIVERSE,
    boundary_search_padding_days: int = EVENT_BOUNDARY_SEARCH_PADDING_DAYS,
) -> dict[str, Any]:
    """Injectable deterministic seam for focused tests; not exposed to the API."""
    start = _utc(range_start_utc, "rangeStartUtc")
    end = _utc(range_end_utc, "rangeEndUtc")
    if end <= start:
        raise ValueError("rangeEndUtc must be after rangeStartUtc")
    return _compile_event_range(
        identity=identity,
        range_start=start,
        range_end=end,
        profiles=profiles,
        longitude=longitude,
        body_universe=body_universe,
        boundary_search_padding_days=boundary_search_padding_days,
    )
