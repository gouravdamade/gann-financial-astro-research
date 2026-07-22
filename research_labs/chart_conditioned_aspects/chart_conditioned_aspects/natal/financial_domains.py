from __future__ import annotations

from ..models import FinancialDomainRecord, NatalCondition, PlanetFunctionalRole
from ..profiles import ResearchProfiles


def compile_financial_domains(
    role: PlanetFunctionalRole,
    condition: NatalCondition,
    profiles: ResearchProfiles,
) -> tuple[FinancialDomainRecord, ...]:
    profile = profiles.domains
    mapping = {
        int(house): tuple(str(domain) for domain in domains)
        for house, domains in profile.get("house_domains", {}).items()
    }
    source_houses = set(role.owned_houses)
    if condition.house is not None:
        source_houses.add(int(condition.house))
    records: list[FinancialDomainRecord] = []
    for house in sorted(source_houses):
        for domain in mapping.get(house, ()):
            records.append(
                FinancialDomainRecord(
                    chart_id=role.chart_id,
                    planet=role.planet,
                    domain=domain,
                    source_house=house,
                    mapping_profile=str(profile["profile_id"]),
                    evidence_class="MODERN_FINANCIAL_EXTENSION",
                    status=str(profile["doctrine_status"]),
                    explanation=(
                        f"{role.planet} is linked to house {house}; {domain} is a "
                        "versioned corporate-domain translation, not a classical stock rule."
                    ),
                )
            )
    return tuple(records)
