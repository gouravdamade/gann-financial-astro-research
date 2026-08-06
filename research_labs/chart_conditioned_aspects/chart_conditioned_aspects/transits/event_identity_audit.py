"""Independent identity audit for transit-to-natal orb windows.

The F2A compiler discovers one contiguous inside-orb run and then selects one
minimum.  That is useful for fast range generation, but it is not sufficient
proof that a run contains exactly one astronomical pass.  This module uses a
separate, deliberately denser scan/root/minimum path to audit that assumption.

It remains astronomy-only.  It reads no market data, SBC, LLM material, or
financial outcomes and it never assigns polarity or magnitude.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable

from ..models import stable_hash


EVENT_IDENTITY_AUDIT_CONTRACT = "CHART_CONDITIONED_TRANSIT_EVENT_IDENTITY_AUDIT_V1"
EVENT_IDENTITY_AUDIT_VERSION = "chart_conditioned_event_identity_audit_v1_20260806"

# The verifier scans more densely than F2A discovery.  Its purpose is audit
# coverage, not the responsive chart-range path.
AUDIT_SCAN_STEP_MINUTES = {
    "MOON": 15,
    "SUN": 180,
    "MARS": 360,
    "MERCURY": 60,
    "JUPITER": 720,
    "VENUS": 120,
    "SATURN": 1080,
    "RAHU": 360,
    "KETU": 360,
}
MOTION_PROBE_MINUTES = {
    "MOON": 30,
    "SUN": 180,
    "MARS": 360,
    "MERCURY": 60,
    "JUPITER": 720,
    "VENUS": 120,
    "SATURN": 720,
    "RAHU": 720,
    "KETU": 720,
}
ROOT_TOLERANCE_DEG = 0.0005
BOUNDARY_TOLERANCE_DEG = 0.0005
RECORDED_EXACT_TOLERANCE_SECONDS = 3
MOTION_STATION_THRESHOLD_DEG_PER_DAY = 0.0001


def _utc(value: str | datetime, label: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
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


def signed_angular_residual(left_deg: float, right_deg: float) -> float:
    """Return the shortest signed angular difference in [-180, 180)."""

    return ((float(left_deg) - float(right_deg) + 180.0) % 360.0) - 180.0


def _aspect_branches(natal_longitude: float, exact_angle_deg: float) -> tuple[float, ...]:
    angle = float(exact_angle_deg) % 360.0
    if abs(angle) < 1e-9:
        return (float(natal_longitude) % 360.0,)
    if abs(angle - 180.0) < 1e-9:
        return ((float(natal_longitude) + 180.0) % 360.0,)
    branches = ((float(natal_longitude) + angle) % 360.0, (float(natal_longitude) - angle) % 360.0)
    return tuple(dict.fromkeys(round(value, 12) for value in branches))


def _grid(start: datetime, end: datetime, step_minutes: int) -> tuple[datetime, ...]:
    if start >= end:
        raise ValueError("audit window requires start before end")
    cursor = start
    result = [cursor]
    step = timedelta(minutes=step_minutes)
    while cursor + step < end:
        cursor += step
        result.append(cursor)
    if result[-1] != end:
        result.append(end)
    return tuple(result)


@dataclass(frozen=True)
class _Sample:
    at: datetime
    longitude: float
    residuals: tuple[float, ...]

    @property
    def orb_deg(self) -> float:
        return min(abs(value) for value in self.residuals)


class _AuditSampler:
    def __init__(
        self,
        *,
        transit_body: str,
        natal_longitude: float,
        exact_angle_deg: float,
        longitude: Callable[[str, datetime], float],
    ) -> None:
        self.transit_body = transit_body
        self.natal_longitude = float(natal_longitude) % 360.0
        self.exact_angle_deg = float(exact_angle_deg)
        self.longitude_provider = longitude
        self.branches = _aspect_branches(self.natal_longitude, self.exact_angle_deg)
        self._cache: dict[datetime, _Sample] = {}

    def sample(self, at: datetime) -> _Sample:
        moment = at.astimezone(timezone.utc)
        cached = self._cache.get(moment)
        if cached is not None:
            return cached
        transit_longitude = float(self.longitude_provider(self.transit_body, moment)) % 360.0
        sample = _Sample(
            at=moment,
            longitude=transit_longitude,
            residuals=tuple(signed_angular_residual(transit_longitude, branch) for branch in self.branches),
        )
        self._cache[moment] = sample
        return sample

    def orb(self, at: datetime) -> float:
        return self.sample(at).orb_deg

    def residual(self, branch_index: int, at: datetime) -> float:
        return self.sample(at).residuals[branch_index]


def _refine_signed_root(
    sampler: _AuditSampler,
    branch_index: int,
    left: datetime,
    right: datetime,
) -> datetime:
    left_value = sampler.residual(branch_index, left)
    right_value = sampler.residual(branch_index, right)
    if abs(left_value) <= ROOT_TOLERANCE_DEG:
        return _round_second(left)
    if abs(right_value) <= ROOT_TOLERANCE_DEG:
        return _round_second(right)
    if left_value * right_value > 0 or max(abs(left_value), abs(right_value)) > 90.0:
        raise ValueError("root refinement requires a local signed residual bracket")
    for _ in range(42):
        midpoint = left + (right - left) / 2
        mid_value = sampler.residual(branch_index, midpoint)
        if abs(mid_value) <= 1e-10:
            return _round_second(midpoint)
        if left_value * mid_value <= 0:
            right, right_value = midpoint, mid_value
        else:
            left, left_value = midpoint, mid_value
    return _round_second(left + (right - left) / 2)


def _golden_orb_minimum(sampler: _AuditSampler, left: datetime, right: datetime) -> datetime:
    """Independent scalar minimizer; deliberately not the compiler ternary search."""

    ratio = (5**0.5 - 1.0) / 2.0
    left_cursor, right_cursor = left, right
    first = right_cursor - (right_cursor - left_cursor) * ratio
    second = left_cursor + (right_cursor - left_cursor) * ratio
    first_orb = sampler.orb(first)
    second_orb = sampler.orb(second)
    for _ in range(44):
        if first_orb <= second_orb:
            right_cursor, second, second_orb = second, first, first_orb
            first = right_cursor - (right_cursor - left_cursor) * ratio
            first_orb = sampler.orb(first)
        else:
            left_cursor, first, first_orb = first, second, second_orb
            second = left_cursor + (right_cursor - left_cursor) * ratio
            second_orb = sampler.orb(second)
    return _round_second(left_cursor + (right_cursor - left_cursor) / 2)


def _deduplicate_candidates(candidates: Iterable[dict[str, Any]], scan_step_minutes: int) -> list[dict[str, Any]]:
    raw = list(candidates)
    precise = [item for item in raw if item["detectionMethod"] != "GRID_SIGNED_ROOT"]
    # A sampled near-zero is an observation, not a second pass, when an
    # independently refined root/minimum exists for the same aspect branch in
    # that sampling cell.  Keep separately refined roots distinct.
    raw = [
        item
        for item in raw
        if item["detectionMethod"] != "GRID_SIGNED_ROOT"
        or not any(
            abs(
                (_utc(other["exactUtc"], "candidate.exactUtc") - _utc(item["exactUtc"], "candidate.exactUtc")).total_seconds()
            ) <= scan_step_minutes * 60
            and abs(float(other["branchAngleDeg"]) - float(item["branchAngleDeg"])) < 1e-6
            for other in precise
        )
    ]
    result: list[dict[str, Any]] = []
    for candidate in sorted(raw, key=lambda item: (item["exactUtc"], item["orbDeg"], item["branchAngleDeg"])):
        at = _utc(candidate["exactUtc"], "candidate.exactUtc")
        duplicate = next(
            (
                existing
                for existing in result
                if abs((_utc(existing["exactUtc"], "candidate.exactUtc") - at).total_seconds()) <= 3
                and abs(float(existing["branchAngleDeg"]) - float(candidate["branchAngleDeg"])) < 1e-6
            ),
            None,
        )
        if duplicate is None:
            result.append(candidate)
        elif float(candidate["orbDeg"]) < float(duplicate["orbDeg"]):
            result[result.index(duplicate)] = candidate
    return result


def _motion_speed_deg_per_day(sampler: _AuditSampler, at: datetime, probe_minutes: int) -> float:
    offset = timedelta(minutes=probe_minutes)
    before = sampler.sample(at - offset).longitude
    after = sampler.sample(at + offset).longitude
    return signed_angular_residual(after, before) / ((2.0 * probe_minutes) / (24.0 * 60.0))


def _refine_station(
    sampler: _AuditSampler,
    left: datetime,
    right: datetime,
    probe_minutes: int,
) -> datetime:
    left_speed = _motion_speed_deg_per_day(sampler, left, probe_minutes)
    right_speed = _motion_speed_deg_per_day(sampler, right, probe_minutes)
    if left_speed == 0:
        return _round_second(left)
    if right_speed == 0:
        return _round_second(right)
    for _ in range(32):
        midpoint = left + (right - left) / 2
        middle_speed = _motion_speed_deg_per_day(sampler, midpoint, probe_minutes)
        if abs(middle_speed) <= MOTION_STATION_THRESHOLD_DEG_PER_DAY:
            return _round_second(midpoint)
        if left_speed * middle_speed <= 0:
            right, right_speed = midpoint, middle_speed
        else:
            left, left_speed = midpoint, middle_speed
    return _round_second(left + (right - left) / 2)


def _motion_phase(speed_deg_per_day: float) -> str:
    if abs(speed_deg_per_day) <= MOTION_STATION_THRESHOLD_DEG_PER_DAY:
        return "STATION"
    return "DIRECT" if speed_deg_per_day > 0 else "RETROGRADE"


def _monotonic_toward_then_away(samples: list[_Sample], exact: datetime) -> bool:
    ordered = sorted({sample.at: sample for sample in samples}.values(), key=lambda sample: sample.at)
    if not ordered:
        return False
    tolerance = 0.0005
    before = [sample for sample in ordered if sample.at <= exact]
    after = [sample for sample in ordered if sample.at >= exact]
    toward = all(next_sample.orb_deg <= sample.orb_deg + tolerance for sample, next_sample in zip(before, before[1:]))
    away = all(next_sample.orb_deg + tolerance >= sample.orb_deg for sample, next_sample in zip(after, after[1:]))
    return toward and away


def audit_continuous_orb_window(
    *,
    transit_body: str,
    natal_longitude: float,
    exact_angle_deg: float,
    max_orb_deg: float,
    applying_start_utc: str | datetime,
    separating_end_utc: str | datetime,
    longitude: Callable[[str, datetime], float],
) -> dict[str, Any]:
    """Independently scan a complete inside-orb window for exact passes.

    The return value makes no assertion about financial meaning.  A window is
    SINGLE_PASS_VERIFIED only when there is one exact candidate and the orb is
    monotonic toward it and then away from it at the verifier sampling grid.
    """

    start = _utc(applying_start_utc, "applyingStartUtc")
    end = _utc(separating_end_utc, "separatingEndUtc")
    body = str(transit_body).upper()
    if body not in AUDIT_SCAN_STEP_MINUTES:
        raise ValueError(f"audit sampling is not configured for {body}")
    sampler = _AuditSampler(
        transit_body=body,
        natal_longitude=natal_longitude,
        exact_angle_deg=exact_angle_deg,
        longitude=longitude,
    )
    grid = _grid(start, end, AUDIT_SCAN_STEP_MINUTES[body])
    samples = [sampler.sample(at) for at in grid]
    candidates: list[dict[str, Any]] = []

    for branch_index, branch in enumerate(sampler.branches):
        residuals = [sample.residuals[branch_index] for sample in samples]
        for index, residual in enumerate(residuals):
            if abs(residual) <= ROOT_TOLERANCE_DEG:
                at = samples[index].at
                candidates.append(
                    {
                        "exactUtc": _iso(at),
                        "detectionMethod": "GRID_SIGNED_ROOT",
                        "branchAngleDeg": round(branch, 8),
                        "signedResidualDeg": round(residual, 10),
                        "orbDeg": round(abs(residual), 10),
                    }
                )
            if index == 0:
                continue
            previous = residuals[index - 1]
            if previous * residual < 0 and max(abs(previous), abs(residual)) < 90.0:
                at = _refine_signed_root(sampler, branch_index, samples[index - 1].at, samples[index].at)
                refined = sampler.residual(branch_index, at)
                candidates.append(
                    {
                        "exactUtc": _iso(at),
                        "detectionMethod": "BRACKETED_SIGNED_ROOT",
                        "branchAngleDeg": round(branch, 8),
                        "signedResidualDeg": round(refined, 10),
                        "orbDeg": round(abs(refined), 10),
                    }
                )

    for index in range(1, len(samples) - 1):
        if samples[index].orb_deg <= samples[index - 1].orb_deg and samples[index].orb_deg <= samples[index + 1].orb_deg:
            at = _golden_orb_minimum(sampler, samples[index - 1].at, samples[index + 1].at)
            sample = sampler.sample(at)
            if sample.orb_deg <= ROOT_TOLERANCE_DEG:
                branch_index = min(range(len(sample.residuals)), key=lambda item: abs(sample.residuals[item]))
                candidates.append(
                    {
                        "exactUtc": _iso(at),
                        "detectionMethod": "LOCAL_MINIMUM_EXACT",
                        "branchAngleDeg": round(sampler.branches[branch_index], 8),
                        "signedResidualDeg": round(sample.residuals[branch_index], 10),
                        "orbDeg": round(sample.orb_deg, 10),
                    }
                )

    exact_candidates = _deduplicate_candidates(candidates, AUDIT_SCAN_STEP_MINUTES[body])
    probe_minutes = MOTION_PROBE_MINUTES[body]
    stations: list[dict[str, Any]] = []
    speeds = [_motion_speed_deg_per_day(sampler, sample.at, probe_minutes) for sample in samples]
    for index, speed in enumerate(speeds):
        if abs(speed) <= MOTION_STATION_THRESHOLD_DEG_PER_DAY:
            stations.append(
                {
                    "timestampUtc": _iso(samples[index].at),
                    "speedBeforeDegPerDay": round(speeds[index - 1] if index else speed, 8),
                    "speedAfterDegPerDay": round(speeds[index + 1] if index + 1 < len(speeds) else speed, 8),
                }
            )
    for index in range(1, len(speeds)):
        if speeds[index - 1] * speeds[index] < 0:
            station = _refine_station(sampler, samples[index - 1].at, samples[index].at, probe_minutes)
            if not any(abs((_utc(item["timestampUtc"], "station.timestampUtc") - station).total_seconds()) <= 3 for item in stations):
                stations.append(
                    {
                        "timestampUtc": _iso(station),
                        "speedBeforeDegPerDay": round(speeds[index - 1], 8),
                        "speedAfterDegPerDay": round(speeds[index], 8),
                    }
                )

    deduplicated_stations: list[dict[str, Any]] = []
    for station in sorted(stations, key=lambda item: item["timestampUtc"]):
        timestamp = _utc(station["timestampUtc"], "station.timestampUtc")
        if not any(
            abs((_utc(item["timestampUtc"], "station.timestampUtc") - timestamp).total_seconds()) <= 3
            for item in deduplicated_stations
        ):
            deduplicated_stations.append(station)
    stations = deduplicated_stations

    boundary_start_orb = sampler.orb(start)
    boundary_end_orb = sampler.orb(end)
    boundary_valid = (
        abs(boundary_start_orb - float(max_orb_deg)) <= BOUNDARY_TOLERANCE_DEG
        and abs(boundary_end_orb - float(max_orb_deg)) <= BOUNDARY_TOLERANCE_DEG
    )
    exact = exact_candidates[0] if len(exact_candidates) == 1 else None
    monotonic = bool(exact) and _monotonic_toward_then_away(
        samples + ([sampler.sample(_utc(exact["exactUtc"], "exactUtc"))] if exact else []),
        _utc(exact["exactUtc"], "exactUtc") if exact else start,
    )
    reasons: list[str] = []
    if not boundary_valid:
        reasons.append("ORB_BOUNDARIES_DO_NOT_MATCH_CONFIGURED_MAX_ORB")
    if not exact_candidates:
        reasons.append("NO_EXACT_ROOT_OR_ZERO_ORB_LOCAL_MINIMUM_FOUND")
    if len(exact_candidates) > 1:
        reasons.append("MULTIPLE_EXACT_CANDIDATES_IN_ONE_CONTINUOUS_ORB_WINDOW")
    if exact and not monotonic:
        reasons.append("ORB_CURVE_NOT_MONOTONIC_TOWARD_THEN_AWAY_FROM_SINGLE_EXACT")

    if len(exact_candidates) > 1 or (exact and not monotonic):
        status = "MULTI_PASS_EVENT_IDENTITY_UNRESOLVED"
    elif not boundary_valid or not exact:
        status = "BOUNDARY_VERIFICATION_FAILED"
    else:
        status = "SINGLE_PASS_VERIFIED"

    motion_at_exact = None
    if exact:
        exact_at = _utc(exact["exactUtc"], "exactUtc")
        speed = _motion_speed_deg_per_day(sampler, exact_at, probe_minutes)
        motion_at_exact = {
            "phase": _motion_phase(speed),
            "speedDegPerDay": round(speed, 8),
        }

    return {
        "contract": EVENT_IDENTITY_AUDIT_CONTRACT,
        "auditVersion": EVENT_IDENTITY_AUDIT_VERSION,
        "status": status,
        "transitBody": body,
        "natalLongitudeDeg": round(float(natal_longitude) % 360.0, 8),
        "exactAngleDeg": float(exact_angle_deg),
        "maxOrbDeg": float(max_orb_deg),
        "applyingStartUtc": _iso(start),
        "separatingEndUtc": _iso(end),
        "scanStepMinutes": AUDIT_SCAN_STEP_MINUTES[body],
        "candidateExactPasses": exact_candidates,
        "stationOrMotionReversalTimestamps": stations,
        "motionPhaseAtExact": motion_at_exact,
        "orbCurveMonotonicTowardThenAway": monotonic,
        "boundaryVerification": {
            "startOrbDeg": round(boundary_start_orb, 8),
            "endOrbDeg": round(boundary_end_orb, 8),
            "configuredMaxOrbDeg": float(max_orb_deg),
            "valid": boundary_valid,
        },
        "reasons": reasons,
        "guardrails": {
            "astronomyOnly": True,
            "polarityAssigned": False,
            "priceDataRead": False,
            "sbcRead": False,
            "llmRead": False,
            "executionAllowed": False,
        },
    }


def _event_seed_from_identity(event: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "eventContract",
        "sideIdentity",
        "instrumentIdentity",
        "chartId",
        "chartHypothesisId",
        "transitBody",
        "natalTarget",
        "aspectType",
        "applyingStartUtc",
        "exactUtc",
        "separatingEndUtc",
        "orbContract",
        "astronomyContract",
        "ayanamsha",
        "nodePolicy",
        "generatorVersion",
    )
    return {key: event[key] for key in keys}


def verify_event_identity(
    *,
    event: dict[str, Any],
    natal_longitude: float,
    longitude: Callable[[str, datetime], float],
    expected_instrument_identity: str,
    expected_chart_id: str,
    expected_chart_hypothesis_id: str,
) -> dict[str, Any]:
    """Verify one immutable F2A event without modifying its identity."""

    orb_contract = event["orbContract"]
    audit = audit_continuous_orb_window(
        transit_body=str(event["transitBody"]),
        natal_longitude=natal_longitude,
        exact_angle_deg=float(orb_contract["exactAngleDeg"]),
        max_orb_deg=float(orb_contract["maxOrbDeg"]),
        applying_start_utc=event["applyingStartUtc"],
        separating_end_utc=event["separatingEndUtc"],
        longitude=longitude,
    )
    start = _utc(event["applyingStartUtc"], "applyingStartUtc")
    recorded_exact = _utc(event["exactUtc"], "exactUtc")
    end = _utc(event["separatingEndUtc"], "separatingEndUtc")
    candidate = audit["candidateExactPasses"][0] if len(audit["candidateExactPasses"]) == 1 else None
    candidate_exact = _utc(candidate["exactUtc"], "candidate.exactUtc") if candidate else None
    sampler = _AuditSampler(
        transit_body=str(event["transitBody"]).upper(),
        natal_longitude=natal_longitude,
        exact_angle_deg=float(orb_contract["exactAngleDeg"]),
        longitude=longitude,
    )
    recorded_orb = sampler.orb(recorded_exact)
    candidate_orb = float(candidate["orbDeg"]) if candidate else None
    checks = {
        "strictTimeOrdering": start < recorded_exact < end,
        "recordedExactMatchesIndependentCandidate": bool(candidate_exact)
        and abs((candidate_exact - recorded_exact).total_seconds()) <= RECORDED_EXACT_TOLERANCE_SECONDS,
        "recordedExactOrbIsPassMinimum": candidate_orb is not None
        and recorded_orb <= candidate_orb + ROOT_TOLERANCE_DEG,
        "residualReachesIntendedExactAngle": candidate_orb is not None and candidate_orb <= ROOT_TOLERANCE_DEG,
        "configuredOrbBoundariesVerified": bool(audit["boundaryVerification"]["valid"]),
        "acceptedChartIdentityMatches": (
            event.get("instrumentIdentity") == expected_instrument_identity
            and event.get("chartId") == expected_chart_id
            and event.get("chartHypothesisId") == expected_chart_hypothesis_id
        ),
        "eventHashReproduces": stable_hash(_event_seed_from_identity(event)) == event.get("eventHash"),
        "eventIdMatchesHash": event.get("eventId") == f"TN_{str(event.get('eventHash', ''))[:24]}",
    }
    status = str(audit["status"])
    if status == "SINGLE_PASS_VERIFIED" and not all(checks.values()):
        status = "BOUNDARY_VERIFICATION_FAILED"
    return {
        "eventId": event.get("eventId"),
        "eventHash": event.get("eventHash"),
        "status": status,
        "checks": checks,
        "recordedExactOrbDeg": round(recorded_orb, 10),
        "audit": audit,
    }
