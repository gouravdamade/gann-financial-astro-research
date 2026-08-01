"""Mode contracts for the founder-facing SBC visualization engine.

These profiles deliberately describe what may be rendered.  They do not
manufacture missing doctrine, fitted values, market direction, or execution.
"""

from __future__ import annotations

from typing import Final


VISUALIZATION_MODE_IDS: Final[tuple[str, ...]] = (
    "SOURCE_ONLY_BASELINE",
    "CALIBRATED_RESEARCH",
    "VISUAL_ONLY_NO_SCORE",
)

_GUARDRAILS: Final[dict[str, bool]] = {
    "experimental": True,
    "financiallyValidated": False,
    "executionAllowed": False,
    "automaticOrderPlacement": False,
}


def visualization_mode_contract(mode: str) -> dict[str, object]:
    """Return the immutable product contract for one visualization mode."""
    if mode not in VISUALIZATION_MODE_IDS:
        raise ValueError(f"unknown visualization mode: {mode}")
    if mode == "SOURCE_ONLY_BASELINE":
        return {
            "mode": mode,
            "evidenceStatus": "SOURCE_ONLY",
            "scoringVisible": True,
            "allowScalarAudit": True,
            "allowFixedPhasor": True,
            "allowTimingGeometry": False,
            "profile": {
                "profileId": "SBC_SOURCE_ONLY_BASELINE_V1",
                "profileHash": None,
                "status": "SOURCE_ONLY",
                "parameterCount": 0,
            },
            "guardrails": dict(_GUARDRAILS),
        }
    if mode == "CALIBRATED_RESEARCH":
        return {
            "mode": mode,
            "evidenceStatus": "SOURCE_MISSING",
            "scoringVisible": False,
            "allowScalarAudit": False,
            "allowFixedPhasor": True,
            "allowTimingGeometry": True,
            "profile": {
                "profileId": "SBC_CALIBRATED_RESEARCH_UNCONFIGURED_V1",
                "profileHash": None,
                "status": "SOURCE_MISSING",
                "parameterCount": 0,
            },
            "guardrails": dict(_GUARDRAILS),
        }
    return {
        "mode": mode,
        "evidenceStatus": "NOT_APPLICABLE",
        "scoringVisible": False,
        "allowScalarAudit": False,
        "allowFixedPhasor": True,
        "allowTimingGeometry": True,
        "profile": {
            "profileId": "SBC_VISUAL_ONLY_NO_SCORE_V1",
            "profileHash": None,
            "status": "NOT_APPLICABLE",
            "parameterCount": 0,
        },
        "guardrails": dict(_GUARDRAILS),
    }
