from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np

from collective_motion import signed_circular_difference_degrees


COLLECTIVE_INFLUENCE_CONTRACT = "GANN_PLANETARY_COLLECTIVE_INFLUENCE_V1"
COLLECTIVE_INFLUENCE_POLICY_ID = "AVG_ALL_LEAVE_ONE_OUT_AUDIT_V1"
FAST_BODY_CLASS = frozenset({"SUN", "MOON", "MERCURY", "VENUS", "MARS"})
ROLE_EPSILON = 1e-10


def _finite_optional(value: Any) -> float | None:
    if value is None:
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _circular_resultant(longitudes_deg: np.ndarray) -> tuple[float, float]:
    radians = np.deg2rad(longitudes_deg)
    cosine = float(np.cos(radians).mean())
    sine = float(np.sin(radians).mean())
    r1 = min(1.0, max(0.0, math.hypot(cosine, sine)))
    mean = math.degrees(math.atan2(sine, cosine)) % 360.0
    return mean, r1


def _effect_role(coherence_leverage: float | None) -> str:
    if coherence_leverage is None:
        return "UNKNOWN"
    if coherence_leverage > ROLE_EPSILON:
        return "CONCENTRATING"
    if coherence_leverage < -ROLE_EPSILON:
        return "DISPERSING"
    return "NEUTRAL"


def build_member_audit(
    longitudes_deg: Sequence[float],
    *,
    members: Sequence[str],
    weights: Sequence[float],
    mean_longitude_deg: float | None,
    coherence_r1: float | None,
    longitude_reliable: bool,
    unstable_resultant_floor: float,
) -> list[dict[str, Any]]:
    if len(longitudes_deg) != len(members) or len(members) != len(weights):
        raise ValueError("collective member audit inputs must have equal lengths")
    values = np.asarray(longitudes_deg, dtype=np.float64)
    full_mean = _finite_optional(mean_longitude_deg)
    full_r1 = _finite_optional(coherence_r1)
    valid_full = (
        longitude_reliable
        and full_mean is not None
        and full_r1 is not None
        and np.isfinite(values).all()
    )

    rows: list[dict[str, Any]] = []
    for index, body in enumerate(members):
        longitude = _finite_optional(values[index])
        tempo_class = (
            "FAST_MOVING_CLASS" if body in FAST_BODY_CLASS else "SLOW_MOVING_CLASS"
        )
        angular_distance: float | None = None
        longitude_leverage: float | None = None
        coherence_leverage: float | None = None
        if valid_full and longitude is not None:
            without_member = np.delete(values, index)
            leave_one_out_mean, leave_one_out_r1 = _circular_resultant(
                without_member
            )
            angular_distance = abs(
                signed_circular_difference_degrees(longitude, full_mean)
            )
            if leave_one_out_r1 >= unstable_resultant_floor:
                longitude_leverage = abs(
                    signed_circular_difference_degrees(
                        leave_one_out_mean,
                        full_mean,
                    )
                )
            coherence_leverage = full_r1 - leave_one_out_r1
        rows.append(
            {
                "body": body,
                "longitudeDeg": (
                    round(longitude, 10) if longitude is not None else None
                ),
                "weight": round(float(weights[index]), 12),
                "angularDistanceFromMeanDeg": (
                    round(angular_distance, 10)
                    if angular_distance is not None
                    else None
                ),
                "longitudeLeverageDeg": (
                    round(longitude_leverage, 10)
                    if longitude_leverage is not None
                    else None
                ),
                "coherenceLeverage": (
                    round(coherence_leverage, 12)
                    if coherence_leverage is not None
                    else None
                ),
                "tempoClass": tempo_class,
                "role": _effect_role(coherence_leverage),
                "influenceRank": None,
            }
        )

    ranked = sorted(
        (
            row
            for row in rows
            if row["longitudeLeverageDeg"] is not None
        ),
        key=lambda row: (
            -float(row["longitudeLeverageDeg"]),
            str(row["body"]),
        ),
    )
    for rank, row in enumerate(ranked, start=1):
        row["influenceRank"] = rank
        if (
            rank <= 3
            and float(row["longitudeLeverageDeg"]) > ROLE_EPSILON
            and row["tempoClass"] == "FAST_MOVING_CLASS"
        ):
            row["role"] = f"{row['role']}_FAST_DRIVER"
        elif (
            row["tempoClass"] == "SLOW_MOVING_CLASS"
            and row["role"] == "CONCENTRATING"
            and rank > len(ranked) // 2
        ):
            row["role"] = "CONCENTRATING_SLOW_ANCHOR"
        else:
            suffix = (
                "FAST_MEMBER"
                if row["tempoClass"] == "FAST_MOVING_CLASS"
                else "SLOW_MEMBER"
            )
            row["role"] = f"{row['role']}_{suffix}"
    return rows


def summarize_member_influence(
    samples: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    latest_audit = samples[-1].get("memberAudit", []) if samples else []
    ranked = sorted(
        (
            row
            for row in latest_audit
            if row.get("influenceRank") is not None
        ),
        key=lambda row: int(row["influenceRank"]),
    )
    return {
        "contract": COLLECTIVE_INFLUENCE_CONTRACT,
        "calculationVersion": COLLECTIVE_INFLUENCE_POLICY_ID,
        "latestTopLongitudeLeverage": ranked[0] if ranked else None,
        "rolePolicy": {
            "classification": "DETERMINISTIC_UI_AUDIT_ONLY",
            "fastMovingClass": sorted(FAST_BODY_CLASS),
            "topFastDriverRankLimit": 3,
            "slowAnchorRule": (
                "concentrating slow-class member in lower half of longitude "
                "leverage ranks"
            ),
        },
        "guardrails": {
            "researchOnly": True,
            "countsAsIndependentVote": False,
            "directionalContribution": 0.0,
            "consumedByLiveInference": False,
            "consumedByAutoSuggest": False,
            "consumedByShadowLedger": False,
            "consumedByOfficialMlNotes": False,
            "executionAllowed": False,
        },
    }
