from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from research_evidence import build_context_only_evidence_packet


COLLECTIVE_FIELD_CONTRACT = "GANN_PLANETARY_COLLECTIVE_FIELD_V1"
COLLECTIVE_CALCULATION_VERSION = "AVG_ALL_CIRCULAR_GEOMETRY_V1"
LEGACY_AVG_ALL_PROFILE_ID = "AVG_ALL_TEN_BODY_EQUAL_WEIGHT_V1"
AVG_ALL_MEMBERS = (
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "URANUS",
    "NEPTUNE",
    "PLUTO",
)

# These thresholds classify display reliability only. They are versioned,
# exposed in every response, and never alter the legacy line calculation.
UNSTABLE_RESULTANT_FLOOR = 1e-8
LOW_COHERENCE_FLOOR = 0.20
CONCENTRATED_FLOOR = 0.65
BIPOLAR_R2_FLOOR = 0.55


def _profile_payload() -> dict[str, Any]:
    return {
        "profileId": LEGACY_AVG_ALL_PROFILE_ID,
        "members": list(AVG_ALL_MEMBERS),
        "weights": [1.0 / len(AVG_ALL_MEMBERS)] * len(AVG_ALL_MEMBERS),
        "nodePolicy": "RAHU_KETU_EXCLUDED",
        "thresholdProfile": {
            "profileId": "AVG_ALL_DISPLAY_RELIABILITY_V1",
            "classification": "UI_HEURISTIC_RESEARCH_ONLY",
            "unstableResultantFloor": UNSTABLE_RESULTANT_FLOOR,
            "lowCoherenceFloor": LOW_COHERENCE_FLOOR,
            "concentratedFloor": CONCENTRATED_FLOOR,
            "bipolarR2Floor": BIPOLAR_R2_FLOOR,
        },
    }


def _member_set_hash() -> str:
    encoded = json.dumps(
        _profile_payload(),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def legacy_circular_mean(member_values: Sequence[np.ndarray]) -> np.ndarray:
    radians = np.deg2rad(np.vstack(member_values))
    sin_sum = np.sin(radians).sum(axis=0)
    cos_sum = np.cos(radians).sum(axis=0)
    return np.degrees(np.arctan2(sin_sum, cos_sum)) % 360.0


def _state_for(r1: float, r2: float) -> tuple[str, str, bool]:
    if r1 < UNSTABLE_RESULTANT_FLOOR:
        state = "BIPOLAR" if r2 >= BIPOLAR_R2_FLOOR else "UNSTABLE"
        return state, "UNSTABLE", False
    if r1 < LOW_COHERENCE_FLOOR:
        state = "BIPOLAR" if r2 >= BIPOLAR_R2_FLOOR else "DISPERSED"
        return state, "LOW_COHERENCE", False
    if r1 >= CONCENTRATED_FLOOR:
        return "CONCENTRATED", "RELIABLE", True
    return "PARTIALLY_COHERENT", "RELIABLE", True


def _optional_stat(values: Sequence[float], reducer: Any) -> float | None:
    if not values:
        return None
    return round(float(reducer(np.asarray(values, dtype=np.float64))), 12)


def calculate_collective_field(
    member_values: Mapping[str, np.ndarray],
    timestamps: Sequence[int],
) -> dict[str, Any]:
    if not timestamps:
        raise ValueError("collective field requires at least one timestamp")
    missing = [member for member in AVG_ALL_MEMBERS if member not in member_values]
    if missing:
        raise ValueError(f"collective field is missing member(s): {', '.join(missing)}")

    rows: list[np.ndarray] = []
    expected = len(timestamps)
    for member in AVG_ALL_MEMBERS:
        values = np.asarray(member_values[member], dtype=np.float64)
        if values.ndim != 1 or len(values) != expected:
            raise ValueError(
                f"collective field member {member} must contain {expected} samples"
            )
        rows.append(values)
    matrix = np.vstack(rows)

    samples: list[dict[str, Any]] = []
    reliability_counts: Counter[str] = Counter()
    state_counts: Counter[str] = Counter()
    r1_values: list[float] = []
    r2_values: list[float] = []

    for position, raw_timestamp in enumerate(timestamps):
        timestamp = int(raw_timestamp)
        if timestamp <= 0:
            raise ValueError("collective field timestamps must be positive Unix seconds")
        column = matrix[:, position]
        if not np.isfinite(column).all():
            sample = {
                "time": timestamp,
                "meanLongitudeDeg": None,
                "coherenceR1": None,
                "circularVariance": None,
                "circularStdDeg": None,
                "polarisationR2": None,
                "polarisationAxisDeg": None,
                "state": "INVALID_INPUT",
                "reliability": "INVALID_INPUT",
                "longitudeReliable": False,
            }
        else:
            radians = np.deg2rad(column)
            c1 = float(np.cos(radians).mean())
            s1 = float(np.sin(radians).mean())
            c2 = float(np.cos(2.0 * radians).mean())
            s2 = float(np.sin(2.0 * radians).mean())
            r1 = min(1.0, max(0.0, math.hypot(c1, s1)))
            r2 = min(1.0, max(0.0, math.hypot(c2, s2)))
            mean_longitude = math.degrees(math.atan2(s1, c1)) % 360.0
            polarisation_axis = (
                math.degrees(math.atan2(s2, c2)) % 360.0
            ) / 2.0
            circular_std = (
                math.degrees(math.sqrt(-2.0 * math.log(max(r1, 1e-15))))
                if r1 >= UNSTABLE_RESULTANT_FLOOR
                else None
            )
            state, reliability, longitude_reliable = _state_for(r1, r2)
            sample = {
                "time": timestamp,
                "meanLongitudeDeg": round(mean_longitude, 10),
                "coherenceR1": round(r1, 12),
                "circularVariance": round(1.0 - r1, 12),
                "circularStdDeg": (
                    round(circular_std, 10) if circular_std is not None else None
                ),
                "polarisationR2": round(r2, 12),
                "polarisationAxisDeg": round(polarisation_axis, 10),
                "state": state,
                "reliability": reliability,
                "longitudeReliable": longitude_reliable,
            }
            r1_values.append(r1)
            r2_values.append(r2)

        reliability_counts[sample["reliability"]] += 1
        state_counts[sample["state"]] += 1
        samples.append(sample)

    latest = samples[-1]
    profile = _profile_payload()
    profile["memberSetHash"] = _member_set_hash()
    context_reason = (
        "Collective geometry has no certified market-direction, activation, "
        "conflict, or confidence mapping."
    )
    evidence = build_context_only_evidence_packet(
        source_family="PLANETARY_COLLECTIVE_GEOMETRY",
        source_profile_id=LEGACY_AVG_ALL_PROFILE_ID,
        calculation_version=COLLECTIVE_CALCULATION_VERSION,
        observed_at_unix=latest["time"],
        reason=context_reason,
        descriptors=[
            {
                "key": "mean_longitude_deg",
                "label": "Mean longitude",
                "value": latest["meanLongitudeDeg"],
                "unit": "degree",
                "status": latest["reliability"],
            },
            {
                "key": "coherence_r1",
                "label": "Coherence R1",
                "value": latest["coherenceR1"],
                "unit": "ratio",
                "status": latest["reliability"],
            },
            {
                "key": "polarisation_r2",
                "label": "Polarisation R2",
                "value": latest["polarisationR2"],
                "unit": "ratio",
                "status": latest["reliability"],
            },
            {
                "key": "geometry_state",
                "label": "Geometry state",
                "value": latest["state"],
                "unit": None,
                "status": "OBSERVED",
            },
        ],
        provenance={
            "astronomyContract": "RAMAN_SIDEREAL_SWISSEPH_EXACT_BAR_TIMESTAMPS_V1",
            "memberSetHash": profile["memberSetHash"],
        },
    )

    return {
        "contract": COLLECTIVE_FIELD_CONTRACT,
        "calculationVersion": COLLECTIVE_CALCULATION_VERSION,
        "profile": profile,
        "samples": samples,
        "latest": latest,
        "summary": {
            "sampleCount": len(samples),
            "reliabilityCounts": dict(sorted(reliability_counts.items())),
            "stateCounts": dict(sorted(state_counts.items())),
            "coherenceR1": {
                "minimum": _optional_stat(r1_values, np.min),
                "median": _optional_stat(r1_values, np.median),
                "maximum": _optional_stat(r1_values, np.max),
            },
            "polarisationR2": {
                "minimum": _optional_stat(r2_values, np.min),
                "median": _optional_stat(r2_values, np.median),
                "maximum": _optional_stat(r2_values, np.max),
            },
        },
        "evidence": evidence,
        "legacyCompatibility": {
            "legacyLineFormulaUnchanged": True,
            "legacyLineValuesPreserved": True,
            "reliabilityChangesLineVisibility": False,
        },
        "guardrails": {
            "researchOnly": True,
            "contextOnly": True,
            "empiricalCoefficient": 0.0,
            "consumedByLiveInference": False,
            "consumedByAutoSuggest": False,
            "consumedByOfficialMlNotes": False,
            "executionAllowed": False,
        },
    }
