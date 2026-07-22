from __future__ import annotations

from ..models import AspectPriorRecord, ExplanationEntry, stable_hash
from ..natal.structure_compiler import CompiledNatalStructure
from ..profiles import ResearchProfiles
from ..transits.orb_profile import aspect_definition


def _role_direction(functional_class: str) -> str:
    if functional_class in {"SUPPORTIVE", "ADVERSE", "MIXED"}:
        return functional_class
    return "INDETERMINATE"


def compile_structural_prior(
    structure: CompiledNatalStructure,
    *,
    transit_body: str,
    natal_target: str,
    aspect_type: str,
    profiles: ResearchProfiles,
) -> AspectPriorRecord:
    transit = str(transit_body).strip().upper()
    target = str(natal_target).strip().upper()
    aspect = str(aspect_type).strip().lower()
    roles = {role.planet: role for role in structure.roles}
    conditions = {condition.planet: condition for condition in structure.conditions}
    if transit not in roles:
        raise ValueError(f"transit body has no compiled functional role: {transit}")
    if target not in conditions:
        raise ValueError(f"natal target is absent from the compiled chart: {target}")
    definition = aspect_definition(aspect, profiles)

    transit_role = roles[transit]
    target_role = roles.get(target)
    direction = _role_direction(transit_role.functional_class)
    activation = str(definition["activation"])
    volatility = str(definition["volatility"])
    ledger: list[ExplanationEntry] = [
        ExplanationEntry(
            entry_id="TRANSIT_FUNCTIONAL_ROLE",
            category="FUNCTIONAL_LORDSHIP",
            directional_effect=direction,  # type: ignore[arg-type]
            activation_effect="UNKNOWN",
            volatility_effect="UNKNOWN",
            reason=(
                f"{transit} is {transit_role.functional_class} for chart "
                f"{structure.chart.chart_id} from owned houses "
                f"{transit_role.owned_houses or 'unavailable'}."
            ),
            confidence=transit_role.confidence,
            evidence_refs=transit_role.evidence_refs,
            uncertainty="; ".join(transit_role.conflicts),
        ),
        ExplanationEntry(
            entry_id="ASPECT_GEOMETRY",
            category="TRANSIT_NATAL_GEOMETRY",
            directional_effect="INDETERMINATE",
            activation_effect=activation,  # type: ignore[arg-type]
            volatility_effect=volatility,  # type: ignore[arg-type]
            reason=(
                f"{aspect} contributes {activation.lower()} activation and "
                f"{volatility.lower()} volatility; geometry supplies no direction by itself."
            ),
            confidence=1.0,
            evidence_refs=(str(profiles.aspects["profile_id"]),),
        ),
    ]
    if target_role is not None:
        ledger.append(
            ExplanationEntry(
                entry_id="NATAL_TARGET_CONTEXT",
                category="NATAL_STRUCTURE",
                directional_effect="INDETERMINATE",
                activation_effect="UNKNOWN",
                volatility_effect="UNKNOWN",
                reason=(
                    f"Natal {target} is {target_role.functional_class}; this is structural "
                    "context and does not silently override the transit body's direction."
                ),
                confidence=target_role.confidence,
                evidence_refs=target_role.evidence_refs,
                uncertainty="; ".join(target_role.conflicts),
            )
        )
    target_domains = sorted(
        record.domain
        for record in structure.graph.financial_domains
        if record.planet == target
    )
    if target_domains:
        ledger.append(
            ExplanationEntry(
                entry_id="TARGET_FINANCIAL_DOMAINS",
                category="MODERN_FINANCIAL_EXTENSION",
                directional_effect="INDETERMINATE",
                activation_effect="UNKNOWN",
                volatility_effect="UNKNOWN",
                reason=(
                    f"Natal {target} links to {', '.join(target_domains)}. The profile "
                    "does not convert those domains into a price sign."
                ),
                confidence=0.35,
                evidence_refs=(str(profiles.domains["profile_id"]),),
                uncertainty="DOMAIN_TO_PRICE_POLARITY_NOT_CERTIFIED",
            )
        )
    ledger.append(
        ExplanationEntry(
            entry_id="CHART_ACCURACY_GATE",
            category="CHART_PROVENANCE",
            directional_effect="INDETERMINATE",
            activation_effect="UNKNOWN",
            volatility_effect="UNKNOWN",
            reason=(
                f"Chart time accuracy is {structure.chart.time_accuracy}; house-based "
                f"reasoning is {'enabled' if structure.chart.allows_houses else 'disabled'}."
            ),
            confidence=1.0,
            evidence_refs=tuple(source.source_id for source in structure.chart.sources),
        )
    )

    unknowns = set(structure.unknowns)
    unknowns.add("TARGET_DOMAIN_TO_PRICE_POLARITY_NOT_CERTIFIED")
    for blocked in profiles.manifest.get("blocked_source_profiles", []):
        unknowns.add(f"{str(blocked).upper()}_BLOCKED")
    if direction == "INDETERMINATE":
        unknowns.add("TRANSIT_FUNCTIONAL_DIRECTION_UNAVAILABLE")

    seed = {
        "chart_id": structure.chart.chart_id,
        "transit_body": transit,
        "natal_target": target,
        "aspect_type": aspect,
        "natal_context_id": structure.graph.natal_context_id,
        "directional_prior": direction,
        "activation_prior": activation,
        "volatility_prior": volatility,
        "explanation_ledger": tuple(ledger),
        "unknowns": tuple(sorted(unknowns)),
        "profile_hash": profiles.profile_hash,
    }
    prior_hash = stable_hash(seed)
    return AspectPriorRecord(
        prior_id=f"PRIOR|{structure.chart.chart_id}|{transit}->{target}|{aspect}|{prior_hash[:16]}",
        chart_id=structure.chart.chart_id,
        transit_body=transit,
        natal_target_type="PLANET",
        natal_target=target,
        aspect_type=aspect,
        natal_context_id=structure.graph.natal_context_id,
        directional_prior=direction,  # type: ignore[arg-type]
        activation_prior=activation,  # type: ignore[arg-type]
        volatility_prior=volatility,  # type: ignore[arg-type]
        explanation_ledger=tuple(ledger),
        unknowns=tuple(sorted(unknowns)),
        doctrine_status="SOURCE_ALIGNED_PROVISIONAL_EXPERIMENTAL_LOCKED",
        profile_hash=profiles.profile_hash,
        prior_hash=prior_hash,
        execution_allowed=False,
        automatic_order_placement=False,
    )
