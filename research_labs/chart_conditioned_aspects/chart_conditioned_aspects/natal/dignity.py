from __future__ import annotations

from ..models import NatalChartSnapshot, NatalCondition, OrganizationChartHypothesis
from ..profiles import ResearchProfiles


def zodiac_sign(longitude: float, sign_sequence: tuple[str, ...]) -> str:
    if len(sign_sequence) != 12:
        raise ValueError("zodiac sign sequence must have twelve entries")
    return sign_sequence[int((float(longitude) % 360.0) // 30.0)]


def compile_natal_condition(
    chart: OrganizationChartHypothesis,
    snapshot: NatalChartSnapshot,
    planet: str,
    profiles: ResearchProfiles,
) -> NatalCondition:
    body = str(planet).upper()
    longitude = snapshot.longitude_for(body)
    if longitude is None:
        raise ValueError(f"natal longitude unavailable for {body}")
    profile = profiles.lordship
    sequence = tuple(str(item).upper() for item in profile["sign_sequence"])
    sign = zodiac_sign(longitude, sequence)
    sign_ruler = str(profile["sign_rulers"].get(sign, "UNKNOWN")).upper()
    dignity = "OWN_SIGN" if sign_ruler == body else "UNCLASSIFIED_PROFILE_PENDING"
    unknowns: list[str] = []
    if dignity != "OWN_SIGN":
        unknowns.append(
            "EXALTATION_DEBILITATION_AND_RELATIONSHIP_PROFILE_NOT_CERTIFIED"
        )
    house = snapshot.house_for(body) if chart.allows_houses else None
    if chart.allows_houses and house is None:
        unknowns.append("HOUSE_PLACEMENT_MISSING")
    return NatalCondition(
        chart_id=chart.chart_id,
        planet=body,
        longitude=longitude,
        sign=sign,
        house=house,
        dignity=dignity,
        retrograde=snapshot.retrograde_for(body),
        profile_id=str(profile["profile_id"]),
        doctrine_status=str(profile["doctrine_status"]),
        unknowns=tuple(unknowns),
    )
