from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np

from collective_motion import signed_circular_difference_degrees


COLLECTIVE_REFINEMENT_CONTRACT = (
    "GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1"
)
COLLECTIVE_REFINEMENT_POLICY_ID = "AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1"
REFINABLE_EVENT_TYPE = "MEAN_RASHI_INGRESS"
ROOT_TOLERANCE_SECONDS = 1.0
ROOT_RESIDUAL_TOLERANCE_DEG = 0.001
MAX_ROOT_ITERATIONS = 64
MAX_REFINEMENT_CANDIDATES = 64

LongitudeEvaluator = Callable[[float], Sequence[float]]


def _collective_mean_and_r1(
    values: Sequence[float],
) -> tuple[float, float]:
    longitudes = np.asarray(values, dtype=np.float64)
    if longitudes.ndim != 1 or not len(longitudes):
        raise ValueError("collective refinement requires member longitudes")
    if not np.isfinite(longitudes).all():
        raise ValueError("collective refinement member longitude is not finite")
    radians = np.deg2rad(longitudes)
    cosine = float(np.cos(radians).mean())
    sine = float(np.sin(radians).mean())
    return (
        math.degrees(math.atan2(sine, cosine)) % 360.0,
        min(1.0, max(0.0, math.hypot(cosine, sine))),
    )


def _root_observation(
    evaluator: LongitudeEvaluator,
    timestamp: float,
    *,
    boundary_wrapped_deg: float,
    unstable_resultant_floor: float,
) -> tuple[float, float, float]:
    mean_longitude, coherence_r1 = _collective_mean_and_r1(
        evaluator(float(timestamp))
    )
    if coherence_r1 < unstable_resultant_floor:
        raise ValueError("collective mean became unreliable inside root bracket")
    residual = signed_circular_difference_degrees(
        mean_longitude,
        boundary_wrapped_deg,
    )
    return residual, mean_longitude, coherence_r1


def _directionally_bracketed(
    left_residual: float,
    right_residual: float,
    direction: str,
) -> bool:
    if direction == "FORWARD":
        return (
            left_residual <= ROOT_RESIDUAL_TOLERANCE_DEG
            and right_residual >= -ROOT_RESIDUAL_TOLERANCE_DEG
        )
    if direction == "BACKWARD":
        return (
            left_residual >= -ROOT_RESIDUAL_TOLERANCE_DEG
            and right_residual <= ROOT_RESIDUAL_TOLERANCE_DEG
        )
    return False


def _refinement_record(
    *,
    status: str,
    sampled_estimate: int,
    reason: str,
    evaluated_timestamp_count: int,
    root_time: float | None = None,
    residual_deg: float | None = None,
    coherence_r1: float | None = None,
    iterations: int = 0,
) -> dict[str, Any]:
    return {
        "contract": COLLECTIVE_REFINEMENT_CONTRACT,
        "policyId": COLLECTIVE_REFINEMENT_POLICY_ID,
        "status": status,
        "sampledEstimateUnix": int(sampled_estimate),
        "refinedTimeUnix": (
            round(float(root_time), 6) if root_time is not None else None
        ),
        "rootToleranceSeconds": ROOT_TOLERANCE_SECONDS,
        "residualToleranceDeg": ROOT_RESIDUAL_TOLERANCE_DEG,
        "residualDeg": (
            round(float(residual_deg), 12)
            if residual_deg is not None
            else None
        ),
        "coherenceR1AtRoot": (
            round(float(coherence_r1), 12)
            if coherence_r1 is not None
            else None
        ),
        "iterations": int(iterations),
        "evaluatedTimestampCount": int(evaluated_timestamp_count),
        "reason": reason,
        "astronomyContract": (
            "RAMAN_SIDEREAL_SWISSEPH_EPHEMERIS_ROOT_V1"
        ),
        "guardrails": {
            "researchOnly": True,
            "preservesSampledEstimate": True,
            "countsAsIndependentVote": False,
            "directionalContribution": 0.0,
            "consumedByLiveInference": False,
            "consumedByAutoSuggest": False,
            "consumedByShadowLedger": False,
            "consumedByOfficialMlNotes": False,
            "executionAllowed": False,
        },
    }


def _refine_ingress_event(
    event: Mapping[str, Any],
    *,
    longitude_evaluator: LongitudeEvaluator,
    unstable_resultant_floor: float,
) -> tuple[dict[str, Any], int]:
    refined = dict(event)
    source_bracket = dict(event.get("sourceBracket") or {})
    details = dict(event.get("details") or {})
    start_time = float(source_bracket.get("startUnix") or 0)
    end_time = float(source_bracket.get("endUnix") or 0)
    sampled_estimate = int(event["estimatedTimeUnix"])
    direction = str(details.get("direction") or "")
    raw_boundary = details.get("boundaryWrappedDeg")
    try:
        boundary = float(raw_boundary)
    except (TypeError, ValueError):
        boundary = math.nan
    evaluated = 0

    def observe(timestamp: float) -> tuple[float, float, float]:
        nonlocal evaluated
        evaluated += 1
        return _root_observation(
            longitude_evaluator,
            timestamp,
            boundary_wrapped_deg=boundary,
            unstable_resultant_floor=unstable_resultant_floor,
        )

    if not math.isfinite(start_time) or not math.isfinite(end_time):
        reason = "source bracket timestamps are not finite"
    elif end_time <= start_time:
        reason = "source bracket is not strictly increasing"
    elif not math.isfinite(boundary):
        reason = "ingress boundary longitude is not finite"
    elif direction not in {"FORWARD", "BACKWARD"}:
        reason = "ingress direction is unsupported"
    else:
        try:
            left = start_time
            right = end_time
            left_observation = observe(left)
            right_observation = observe(right)
            if not _directionally_bracketed(
                left_observation[0],
                right_observation[0],
                direction,
            ):
                reason = (
                    "ephemeris endpoints do not preserve the sampled "
                    "directional crossing bracket"
                )
            else:
                iterations = 0
                while (
                    right - left > ROOT_TOLERANCE_SECONDS
                    and iterations < MAX_ROOT_ITERATIONS
                ):
                    midpoint = (left + right) / 2.0
                    middle_observation = observe(midpoint)
                    if direction == "FORWARD":
                        if middle_observation[0] < 0:
                            left = midpoint
                            left_observation = middle_observation
                        else:
                            right = midpoint
                            right_observation = middle_observation
                    elif middle_observation[0] > 0:
                        left = midpoint
                        left_observation = middle_observation
                    else:
                        right = midpoint
                        right_observation = middle_observation
                    iterations += 1

                candidates = (
                    (left, left_observation),
                    (right, right_observation),
                )
                root_time, root_observation = min(
                    candidates,
                    key=lambda item: abs(item[1][0]),
                )
                residual = root_observation[0]
                if (
                    right - left <= ROOT_TOLERANCE_SECONDS
                    and abs(residual) <= ROOT_RESIDUAL_TOLERANCE_DEG
                ):
                    refinement = _refinement_record(
                        status="REFINED_BRACKETED_ROOT",
                        sampled_estimate=sampled_estimate,
                        reason=(
                            "Reliable directional bracket converged within "
                            "the declared time and angular residual tolerances."
                        ),
                        evaluated_timestamp_count=evaluated,
                        root_time=root_time,
                        residual_deg=residual,
                        coherence_r1=root_observation[2],
                        iterations=iterations,
                    )
                    refined["refinedTimeUnix"] = refinement[
                        "refinedTimeUnix"
                    ]
                    refined["refinement"] = refinement
                    refined["timing"] = {
                        "exact": True,
                        "method": (
                            "BRACKETED_BISECTION_OF_EPHEMERIS_MEAN"
                        ),
                        "precision": (
                            "WITHIN_DECLARED_TIME_AND_ANGULAR_TOLERANCE"
                        ),
                        "sampledEstimateUnix": sampled_estimate,
                        "rootToleranceSeconds": ROOT_TOLERANCE_SECONDS,
                        "residualToleranceDeg": (
                            ROOT_RESIDUAL_TOLERANCE_DEG
                        ),
                    }
                    refined["guardrails"] = {
                        **dict(event.get("guardrails") or {}),
                        "exactEventTime": True,
                    }
                    return refined, evaluated
                reason = (
                    "root bracket converged but angular residual exceeded "
                    "the declared tolerance"
                )
        except (TypeError, ValueError) as exc:
            reason = str(exc)

    refined["refinedTimeUnix"] = None
    refined["refinement"] = _refinement_record(
        status="SAMPLED_FALLBACK",
        sampled_estimate=sampled_estimate,
        reason=reason,
        evaluated_timestamp_count=evaluated,
    )
    return refined, evaluated


def refine_collective_events(
    events: Sequence[Mapping[str, Any]],
    event_summary: Mapping[str, Any],
    *,
    longitude_evaluator: LongitudeEvaluator,
    unstable_resultant_floor: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates = sum(
        1 for event in events if event.get("eventType") == REFINABLE_EVENT_TYPE
    )

    output: list[dict[str, Any]] = []
    attempted = 0
    skipped_budget = 0
    refined_count = 0
    evaluated_timestamp_count = 0
    for event in events:
        if event.get("eventType") != REFINABLE_EVENT_TYPE:
            copied = dict(event)
            copied["refinedTimeUnix"] = None
            copied["refinement"] = None
            output.append(copied)
            continue
        if attempted >= MAX_REFINEMENT_CANDIDATES:
            copied = dict(event)
            sampled_estimate = int(event["estimatedTimeUnix"])
            copied["refinedTimeUnix"] = None
            copied["refinement"] = _refinement_record(
                status="SAMPLED_FALLBACK",
                sampled_estimate=sampled_estimate,
                reason=(
                    "ephemeris refinement candidate budget was exhausted; "
                    "the original sampled estimate is preserved"
                ),
                evaluated_timestamp_count=0,
            )
            output.append(copied)
            skipped_budget += 1
            continue
        attempted += 1
        candidate, evaluated = _refine_ingress_event(
            event,
            longitude_evaluator=longitude_evaluator,
            unstable_resultant_floor=unstable_resultant_floor,
        )
        evaluated_timestamp_count += evaluated
        if candidate["refinement"]["status"] == "REFINED_BRACKETED_ROOT":
            refined_count += 1
        output.append(candidate)

    output.sort(
        key=lambda item: (
            float(
                item.get("refinedTimeUnix")
                or item.get("estimatedTimeUnix")
                or 0
            ),
            str(item.get("eventId") or ""),
        )
    )
    summary = {
        **dict(event_summary),
        "eventPolicy": {
            **dict(event_summary.get("eventPolicy") or {}),
            "timingClassification": (
                "MIXED_SAMPLED_AND_EPHEMERIS_REFINED"
            ),
            "detects": [
                *list(
                    (event_summary.get("eventPolicy") or {}).get(
                        "detects",
                        [],
                    )
                ),
                "EPHEMERIS_REFINED_MEAN_RASHI_INGRESS",
            ],
            "doesNotDetectYet": [
                item
                for item in list(
                    (event_summary.get("eventPolicy") or {}).get(
                        "doesNotDetectYet",
                        [],
                    )
                )
                if item != "EXACT_EPHEMERIS_REFINED_INGRESS"
            ],
        },
        "refinement": {
            "contract": COLLECTIVE_REFINEMENT_CONTRACT,
            "policyId": COLLECTIVE_REFINEMENT_POLICY_ID,
            "refinableEventTypes": [REFINABLE_EVENT_TYPE],
            "candidateCount": candidates,
            "candidateBudget": MAX_REFINEMENT_CANDIDATES,
            "attemptedCount": attempted,
            "skippedBudgetCount": skipped_budget,
            "refinedCount": refined_count,
            "fallbackCount": candidates - refined_count,
            "evaluatedTimestampCount": evaluated_timestamp_count,
            "rootToleranceSeconds": ROOT_TOLERANCE_SECONDS,
            "residualToleranceDeg": ROOT_RESIDUAL_TOLERANCE_DEG,
            "guardrails": {
                "researchOnly": True,
                "heuristicThresholdEventsRemainSampled": True,
                "countsAsIndependentVote": False,
                "directionalContribution": 0.0,
                "consumedByLiveInference": False,
                "consumedByAutoSuggest": False,
                "consumedByShadowLedger": False,
                "consumedByOfficialMlNotes": False,
                "executionAllowed": False,
            },
        },
        "guardrails": {
            **dict(event_summary.get("guardrails") or {}),
            "sampledTimingOnly": False,
            "exactRootsLimitedTo": [REFINABLE_EVENT_TYPE],
        },
    }
    return output, summary
