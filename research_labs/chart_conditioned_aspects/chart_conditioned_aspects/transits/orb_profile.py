from __future__ import annotations

from typing import Any

from ..profiles import ResearchProfiles


def normalized_separation(left_deg: float, right_deg: float) -> float:
    delta = abs((float(left_deg) - float(right_deg)) % 360.0)
    return min(delta, 360.0 - delta)


def angular_orb(observed_separation_deg: float, exact_angle_deg: float) -> float:
    observed = normalized_separation(float(observed_separation_deg), 0.0)
    exact = normalized_separation(float(exact_angle_deg), 0.0)
    return abs(observed - exact)


def aspect_definition(aspect_type: str, profiles: ResearchProfiles) -> dict[str, Any]:
    name = str(aspect_type).strip().lower()
    aspects = profiles.aspects.get("aspects", {})
    try:
        raw = aspects[name]
    except KeyError as exc:
        raise ValueError(
            f"aspect is not enabled by the locked profile: {name}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(f"aspect profile entry must be a mapping: {name}")
    return raw


def validate_profile_orb(
    *,
    aspect_type: str,
    observed_separation_deg: float,
    profiles: ResearchProfiles,
) -> tuple[float, float, dict[str, Any]]:
    definition = aspect_definition(aspect_type, profiles)
    exact = float(definition["exact_angle_deg"])
    orb = angular_orb(observed_separation_deg, exact)
    maximum = float(definition["max_orb_deg"])
    if orb > maximum + 1e-9:
        raise ValueError(
            f"event orb {orb:.6f} exceeds {aspect_type} profile maximum {maximum:.6f}"
        )
    return exact, orb, definition
