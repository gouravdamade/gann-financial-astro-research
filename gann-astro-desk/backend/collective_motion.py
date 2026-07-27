from __future__ import annotations

import hashlib
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


COLLECTIVE_MOTION_CONTRACT = "GANN_PLANETARY_COLLECTIVE_MOTION_V1"
COLLECTIVE_EVENT_CONTRACT = "GANN_PLANETARY_COLLECTIVE_EVENT_V1"
COLLECTIVE_EVENT_POLICY_ID = "AVG_ALL_SAMPLED_EVENTS_V1"
SECONDS_PER_DAY = 86_400.0
RASHI_NAMES = (
    "ARIES",
    "TAURUS",
    "GEMINI",
    "CANCER",
    "LEO",
    "VIRGO",
    "LIBRA",
    "SCORPIO",
    "SAGITTARIUS",
    "CAPRICORN",
    "AQUARIUS",
    "PISCES",
)


def signed_circular_difference_degrees(current: float, previous: float) -> float:
    difference = math.radians(float(current) - float(previous))
    return math.degrees(math.atan2(math.sin(difference), math.cos(difference)))


def _finite_optional(value: Any) -> float | None:
    if value is None:
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _slope_per_day(
    first_value: float,
    first_time: int,
    second_value: float,
    second_time: int,
) -> float:
    elapsed_days = (int(second_time) - int(first_time)) / SECONDS_PER_DAY
    if elapsed_days <= 0:
        raise ValueError("collective motion timestamps must be strictly increasing")
    return (float(second_value) - float(first_value)) / elapsed_days


def _rounded_optional(value: float | None, digits: int = 10) -> float | None:
    return round(value, digits) if value is not None else None


def apply_reliability_safe_motion(
    raw_samples: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    samples = [dict(sample) for sample in raw_samples]
    if not samples:
        raise ValueError("collective motion requires at least one sample")
    timestamps = [int(sample["time"]) for sample in samples]
    if any(
        current <= previous
        for previous, current in zip(timestamps, timestamps[1:], strict=False)
    ):
        raise ValueError("collective motion timestamps must be strictly increasing")

    segments: list[list[int]] = []
    active_segment: list[int] | None = None
    previous_reliable_index: int | None = None

    for index, sample in enumerate(samples):
        mean_longitude = _finite_optional(sample.get("meanLongitudeDeg"))
        reliable = bool(sample.get("longitudeReliable")) and mean_longitude is not None
        sample.update(
            {
                "segmentId": None,
                "unwrappedLongitudeDeg": None,
                "velocityDegPerDay": None,
                "accelerationDegPerDay2": None,
            }
        )
        if not reliable:
            active_segment = None
            previous_reliable_index = None
            continue

        if active_segment is None:
            active_segment = []
            segments.append(active_segment)
            unwrapped = mean_longitude
        else:
            if previous_reliable_index is None:
                raise RuntimeError("active collective segment lost its previous sample")
            previous = samples[previous_reliable_index]
            previous_mean = float(previous["meanLongitudeDeg"])
            previous_unwrapped = float(previous["unwrappedLongitudeDeg"])
            unwrapped = previous_unwrapped + signed_circular_difference_degrees(
                mean_longitude,
                previous_mean,
            )

        active_segment.append(index)
        sample["segmentId"] = len(segments)
        sample["unwrappedLongitudeDeg"] = round(unwrapped, 10)
        previous_reliable_index = index

    for segment in segments:
        if len(segment) < 2:
            continue
        for position, sample_index in enumerate(segment):
            if position == 0:
                first_index, second_index = segment[0], segment[1]
            elif position == len(segment) - 1:
                first_index, second_index = segment[-2], segment[-1]
            else:
                first_index, second_index = segment[position - 1], segment[position + 1]
            velocity = _slope_per_day(
                float(samples[first_index]["unwrappedLongitudeDeg"]),
                int(samples[first_index]["time"]),
                float(samples[second_index]["unwrappedLongitudeDeg"]),
                int(samples[second_index]["time"]),
            )
            samples[sample_index]["velocityDegPerDay"] = round(velocity, 10)

        if len(segment) < 3:
            continue
        for position in range(1, len(segment) - 1):
            previous_index = segment[position - 1]
            current_index = segment[position]
            next_index = segment[position + 1]
            acceleration = _slope_per_day(
                float(samples[previous_index]["velocityDegPerDay"]),
                int(samples[previous_index]["time"]),
                float(samples[next_index]["velocityDegPerDay"]),
                int(samples[next_index]["time"]),
            )
            samples[current_index]["accelerationDegPerDay2"] = round(acceleration, 10)

    velocities = [
        float(sample["velocityDegPerDay"])
        for sample in samples
        if sample["velocityDegPerDay"] is not None
    ]
    accelerations = [
        float(sample["accelerationDegPerDay2"])
        for sample in samples
        if sample["accelerationDegPerDay2"] is not None
    ]
    summary = {
        "contract": COLLECTIVE_MOTION_CONTRACT,
        "calculationVersion": "RELIABILITY_SAFE_CIRCULAR_MOTION_V1",
        "segmentCount": len(segments),
        "reliableSampleCount": sum(
            1 for sample in samples if sample["segmentId"] is not None
        ),
        "velocitySampleCount": len(velocities),
        "accelerationSampleCount": len(accelerations),
        "velocityDegPerDay": {
            "minimum": _rounded_optional(min(velocities) if velocities else None),
            "maximum": _rounded_optional(max(velocities) if velocities else None),
        },
        "accelerationDegPerDay2": {
            "minimum": _rounded_optional(min(accelerations) if accelerations else None),
            "maximum": _rounded_optional(max(accelerations) if accelerations else None),
        },
        "guardrails": {
            "reliabilityGapsBreakSegments": True,
            "usesExactTimestampDifferences": True,
            "bridgesUnreliableSamples": False,
            "displaySmoothingApplied": False,
            "researchOnly": True,
            "executionAllowed": False,
        },
    }
    return samples, summary


def _event_id(
    profile_id: str,
    event_type: str,
    start_time: int,
    end_time: int,
    discriminator: str,
) -> str:
    payload = (
        f"{profile_id}|{event_type}|{start_time}|{end_time}|{discriminator}"
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _causal_cluster_id(profile_id: str, start_time: int, end_time: int) -> str:
    payload = f"{profile_id}|{start_time}|{end_time}".encode("utf-8")
    return f"PLANETARY_GEOMETRY:{hashlib.sha256(payload).hexdigest()[:20]}"


def _interpolated_timestamp(
    start_time: int,
    end_time: int,
    fraction: float,
) -> int:
    bounded = min(1.0, max(0.0, float(fraction)))
    return round(start_time + bounded * (end_time - start_time))


def _event_guardrails() -> dict[str, Any]:
    return {
        "researchOnly": True,
        "visualMarkerOnly": True,
        "timestampSafe": True,
        "exactEventTime": False,
        "directionalContribution": 0.0,
        "castsSbcVedha": False,
        "consumedByLiveInference": False,
        "consumedByAutoSuggest": False,
        "consumedByShadowLedger": False,
        "consumedByOfficialMlNotes": False,
        "executionAllowed": False,
    }


def _base_event(
    *,
    profile_id: str,
    event_type: str,
    start_time: int,
    end_time: int,
    estimated_time: int,
    discriminator: str,
    timing_method: str,
    details: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "contract": COLLECTIVE_EVENT_CONTRACT,
        "eventId": _event_id(
            profile_id,
            event_type,
            start_time,
            end_time,
            discriminator,
        ),
        "profileId": profile_id,
        "eventPolicyId": COLLECTIVE_EVENT_POLICY_ID,
        "eventType": event_type,
        "estimatedTimeUnix": int(estimated_time),
        "sourceBracket": {
            "startUnix": int(start_time),
            "endUnix": int(end_time),
        },
        "timing": {
            "exact": False,
            "method": timing_method,
            "precision": "BETWEEN_EXACT_BAR_SAMPLES",
        },
        "causalClusterId": _causal_cluster_id(profile_id, start_time, end_time),
        "details": dict(details),
        "guardrails": _event_guardrails(),
    }


def _crossed_rashi_boundaries(
    previous_unwrapped: float,
    current_unwrapped: float,
) -> list[float]:
    if current_unwrapped > previous_unwrapped:
        first = math.floor(previous_unwrapped / 30.0) + 1
        last = math.floor(current_unwrapped / 30.0)
        return [float(index * 30) for index in range(first, last + 1)]
    if current_unwrapped < previous_unwrapped:
        first = math.floor(previous_unwrapped / 30.0)
        last = math.floor(current_unwrapped / 30.0) + 1
        return [float(index * 30) for index in range(first, last - 1, -1)]
    return []


def detect_sampled_collective_events(
    samples: Sequence[Mapping[str, Any]],
    *,
    profile_id: str,
    low_coherence_floor: float,
    concentrated_floor: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not samples:
        raise ValueError("collective event detection requires at least one sample")
    events: list[dict[str, Any]] = []
    thresholds = (
        ("LOW_COHERENCE_FLOOR", float(low_coherence_floor)),
        ("CONCENTRATED_FLOOR", float(concentrated_floor)),
    )

    for previous, current in zip(samples, samples[1:], strict=False):
        start_time = int(previous["time"])
        end_time = int(current["time"])
        if end_time <= start_time:
            raise ValueError("collective event timestamps must be strictly increasing")

        previous_r1 = _finite_optional(previous.get("coherenceR1"))
        current_r1 = _finite_optional(current.get("coherenceR1"))
        if previous_r1 is not None and current_r1 is not None and current_r1 != previous_r1:
            for threshold_name, threshold in thresholds:
                crossed_up = previous_r1 < threshold <= current_r1
                crossed_down = previous_r1 >= threshold > current_r1
                if not crossed_up and not crossed_down:
                    continue
                fraction = (threshold - previous_r1) / (current_r1 - previous_r1)
                direction = "UP" if crossed_up else "DOWN"
                events.append(
                    _base_event(
                        profile_id=profile_id,
                        event_type="COHERENCE_THRESHOLD_CROSSING",
                        start_time=start_time,
                        end_time=end_time,
                        estimated_time=_interpolated_timestamp(
                            start_time,
                            end_time,
                            fraction,
                        ),
                        discriminator=f"{threshold_name}:{direction}",
                        timing_method="LINEAR_INTERPOLATION_OF_R1",
                        details={
                            "thresholdName": threshold_name,
                            "thresholdValue": threshold,
                            "direction": direction,
                            "fromR1": round(previous_r1, 12),
                            "toR1": round(current_r1, 12),
                        },
                    )
                )

        previous_state = str(previous.get("state") or "UNKNOWN")
        current_state = str(current.get("state") or "UNKNOWN")
        if previous_state != current_state:
            events.append(
                _base_event(
                    profile_id=profile_id,
                    event_type="CLUSTER_STATE_TRANSITION",
                    start_time=start_time,
                    end_time=end_time,
                    estimated_time=end_time,
                    discriminator=f"{previous_state}:{current_state}",
                    timing_method="RIGHT_SAMPLE_STATE_OBSERVATION",
                    details={
                        "fromState": previous_state,
                        "toState": current_state,
                    },
                )
            )

        previous_segment = previous.get("segmentId")
        current_segment = current.get("segmentId")
        previous_unwrapped = _finite_optional(previous.get("unwrappedLongitudeDeg"))
        current_unwrapped = _finite_optional(current.get("unwrappedLongitudeDeg"))
        same_reliable_segment = (
            previous_segment is not None
            and previous_segment == current_segment
            and previous_unwrapped is not None
            and current_unwrapped is not None
        )
        if not same_reliable_segment or current_unwrapped == previous_unwrapped:
            continue
        direction = "FORWARD" if current_unwrapped > previous_unwrapped else "BACKWARD"
        for boundary in _crossed_rashi_boundaries(
            previous_unwrapped,
            current_unwrapped,
        ):
            fraction = (
                (boundary - previous_unwrapped)
                / (current_unwrapped - previous_unwrapped)
            )
            boundary_index = int(round(boundary / 30.0))
            target_index = (
                boundary_index % 12
                if direction == "FORWARD"
                else (boundary_index - 1) % 12
            )
            source_index = (
                (target_index - 1) % 12
                if direction == "FORWARD"
                else (target_index + 1) % 12
            )
            events.append(
                _base_event(
                    profile_id=profile_id,
                    event_type="MEAN_RASHI_INGRESS",
                    start_time=start_time,
                    end_time=end_time,
                    estimated_time=_interpolated_timestamp(
                        start_time,
                        end_time,
                        fraction,
                    ),
                    discriminator=f"{boundary:.10f}:{direction}",
                    timing_method="LINEAR_INTERPOLATION_OF_UNWRAPPED_MEAN",
                    details={
                        "direction": direction,
                        "boundaryUnwrappedDeg": round(boundary, 10),
                        "boundaryWrappedDeg": round(boundary % 360.0, 10),
                        "fromRashi": RASHI_NAMES[source_index],
                        "toRashi": RASHI_NAMES[target_index],
                    },
                )
            )

    events.sort(key=lambda item: (item["estimatedTimeUnix"], item["eventId"]))
    event_counts = Counter(event["eventType"] for event in events)
    summary = {
        "contract": "GANN_PLANETARY_COLLECTIVE_EVENT_SUMMARY_V1",
        "eventPolicy": {
            "profileId": COLLECTIVE_EVENT_POLICY_ID,
            "timingClassification": "SAMPLED_RESEARCH_ESTIMATE",
            "lowCoherenceFloor": float(low_coherence_floor),
            "concentratedFloor": float(concentrated_floor),
            "detects": [
                "MEAN_RASHI_INGRESS",
                "COHERENCE_THRESHOLD_CROSSING",
                "CLUSTER_STATE_TRANSITION",
            ],
            "doesNotDetectYet": [
                "EXACT_EPHEMERIS_REFINED_INGRESS",
                "NAKSHATRA_INGRESS",
                "PADA_INGRESS",
                "APPARENT_STATION",
                "POLARISATION_PEAK",
                "NATAL_CONTACT",
            ],
        },
        "eventCount": len(events),
        "eventTypeCounts": dict(sorted(event_counts.items())),
        "guardrails": {
            "sampledTimingOnly": True,
            "prospectiveFreezePerformed": False,
            "researchOnly": True,
            "executionAllowed": False,
        },
    }
    return events, summary
