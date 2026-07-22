from __future__ import annotations

from typing import Iterable

from ..models import (
    NatalChartSnapshot,
    OrganizationChartHypothesis,
    PlanetFunctionalRole,
)
from ..profiles import ResearchProfiles
from .house_roles import group_flags, houses_owned_by


CLASSICAL_PLANETS = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")


def compile_planet_role(
    chart: OrganizationChartHypothesis,
    snapshot: NatalChartSnapshot,
    planet: str,
    profiles: ResearchProfiles,
) -> PlanetFunctionalRole:
    body = str(planet).upper()
    profile = profiles.lordship
    profile_id = str(profile["profile_id"])
    doctrine_status = str(profile["doctrine_status"])
    evidence_refs = tuple(str(item) for item in profile.get("source_dependencies", []))
    natural_nature = str(profile.get("natural_nature", {}).get(body, "UNKNOWN"))
    if chart.chart_id != snapshot.chart_id:
        raise ValueError("chart and natal snapshot IDs do not match")
    if not chart.allows_houses or not snapshot.ascendant_sign:
        return PlanetFunctionalRole(
            chart_id=chart.chart_id,
            planet=body,
            natural_nature=natural_nature,
            owned_houses=(),
            functional_class="UNKNOWN",
            flags=("FUNCTIONAL_LORDSHIP_DISABLED_BY_TIME_ACCURACY",),
            conflicts=(),
            source_profile=profile_id,
            doctrine_status=doctrine_status,
            confidence=0.0,
            evidence_refs=evidence_refs,
        )

    owned = houses_owned_by(body, snapshot.ascendant_sign, profile)
    flags = set(group_flags(owned, profile))
    groups = {
        str(name).upper(): {int(item) for item in houses}
        for name, houses in profile.get("house_groups", {}).items()
    }
    owned_set = set(owned)
    if (
        profile.get("resolution", {}).get("yogakaraka_requires_kendra_and_trikona")
        and owned_set & groups.get("KENDRA", set())
        and owned_set & groups.get("TRIKONA", set())
    ):
        flags.add("YOGAKARAKA_CANDIDATE")

    resolution = profile.get("resolution", {})
    if "YOGAKARAKA_CANDIDATE" in flags:
        functional_class = str(resolution.get("yogakaraka_class", "SUPPORTIVE"))
    else:
        supportive = bool(
            flags & set(str(item) for item in resolution.get("supportive_flags", []))
        )
        adverse = bool(
            flags & set(str(item) for item in resolution.get("adverse_flags", []))
        )
        if supportive and adverse:
            functional_class = "MIXED"
        elif supportive:
            functional_class = "SUPPORTIVE"
        elif adverse:
            functional_class = "ADVERSE"
        else:
            functional_class = "INDETERMINATE"

    conflicts: list[str] = []
    if functional_class == "MIXED":
        conflicts.append("MIXED_HOUSE_OWNERSHIP_PRESERVED")
    if natural_nature == "CONDITIONAL":
        conflicts.append(f"{body}_NATURAL_NATURE_REQUIRES_ASSOCIATION_CONTEXT")
    return PlanetFunctionalRole(
        chart_id=chart.chart_id,
        planet=body,
        natural_nature=natural_nature,
        owned_houses=owned,
        functional_class=functional_class,  # type: ignore[arg-type]
        flags=tuple(flags),
        conflicts=tuple(conflicts),
        source_profile=profile_id,
        doctrine_status=doctrine_status,
        confidence=float(profile.get("base_confidence", 0.0)),
        evidence_refs=evidence_refs,
    )


def compile_all_planet_roles(
    chart: OrganizationChartHypothesis,
    snapshot: NatalChartSnapshot,
    profiles: ResearchProfiles,
    planets: Iterable[str] = CLASSICAL_PLANETS,
) -> tuple[PlanetFunctionalRole, ...]:
    return tuple(
        compile_planet_role(chart, snapshot, planet, profiles)
        for planet in sorted({str(item).upper() for item in planets})
    )
