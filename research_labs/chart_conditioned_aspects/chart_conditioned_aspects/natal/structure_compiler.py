from __future__ import annotations

from dataclasses import dataclass

from ..models import (
    NatalAspectGraph,
    NatalChartSnapshot,
    NatalCondition,
    OrganizationChartHypothesis,
    PlanetFunctionalRole,
)
from ..profiles import ResearchProfiles
from .dignity import compile_natal_condition
from .financial_domains import compile_financial_domains
from .functional_lordship import compile_all_planet_roles
from .natal_aspect_graph import compile_natal_graph
from .yoga_context import compile_yoga_context


@dataclass(frozen=True)
class CompiledNatalStructure:
    chart: OrganizationChartHypothesis
    snapshot: NatalChartSnapshot
    roles: tuple[PlanetFunctionalRole, ...]
    conditions: tuple[NatalCondition, ...]
    graph: NatalAspectGraph
    unknowns: tuple[str, ...]
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        if self.execution_allowed:
            raise ValueError(
                "compiled natal research structure cannot authorize execution"
            )


def compile_natal_structure(
    chart: OrganizationChartHypothesis,
    snapshot: NatalChartSnapshot,
    profiles: ResearchProfiles,
) -> CompiledNatalStructure:
    if chart.status != "ACCEPTED_RESEARCH":
        raise ValueError("chart hypothesis must be explicitly accepted for research")
    if chart.chart_id != snapshot.chart_id:
        raise ValueError("chart and snapshot IDs do not match")
    if chart.astronomy_contract != snapshot.astronomy_contract:
        raise ValueError("chart and snapshot astronomy contracts do not match")
    if not chart.allows_houses and (
        snapshot.ascendant_sign or snapshot.house_placements
    ):
        raise ValueError(
            "date-only or unknown-time charts cannot carry houses or ascendant"
        )
    if chart.allows_houses and not snapshot.ascendant_sign:
        raise ValueError(
            "house-capable chart requires an ascendant sign in the snapshot"
        )

    planets = tuple(planet for planet, _ in snapshot.planet_longitudes)
    roles = compile_all_planet_roles(chart, snapshot, profiles, planets)
    conditions = tuple(
        compile_natal_condition(chart, snapshot, planet, profiles)
        for planet in sorted(planets)
    )
    domains = tuple(
        domain
        for role, condition in zip(roles, conditions, strict=True)
        for domain in compile_financial_domains(role, condition, profiles)
    )
    _, yoga_unknowns = compile_yoga_context(profiles)
    unknowns = list(yoga_unknowns)
    if not chart.allows_houses:
        unknowns.append(
            "FUNCTIONAL_LORDSHIP_AND_HOUSE_DOMAINS_DISABLED_BY_TIME_ACCURACY"
        )
    unknowns.extend(
        unknown for condition in conditions for unknown in condition.unknowns
    )
    graph = compile_natal_graph(chart, snapshot, roles, conditions, domains, profiles)
    return CompiledNatalStructure(
        chart=chart,
        snapshot=snapshot,
        roles=roles,
        conditions=conditions,
        graph=graph,
        unknowns=tuple(sorted(set(unknowns))),
        execution_allowed=False,
    )
