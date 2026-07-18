from __future__ import annotations

from datetime import datetime
from itertools import permutations
from typing import Iterable

from .models import (
    CurrencyScore,
    FxPairScore,
    InfluenceContribution,
    InstrumentIdentity,
    RuleRecord,
    TargetMapping,
    UncertaintySummary,
)


CLASSICAL_SOURCE_TIERS = {"classical_text", "commentary"}


def validate_rule_profile(
    rules: Iterable[RuleRecord],
    *,
    profile_kind: str,
) -> None:
    for rule in rules:
        if profile_kind == "classical":
            disallowed = [
                citation.source_id
                for citation in rule.source_citations
                if citation.source_tier not in CLASSICAL_SOURCE_TIERS
            ]
            if disallowed:
                raise ValueError(
                    f"classical profile {rule.profile_id} contains non-classical "
                    f"sources: {disallowed}"
                )
        if rule.status == "verified" and any(
            not citation.locator for citation in rule.source_citations
        ):
            raise ValueError(f"verified rule {rule.rule_id} lacks a source locator")


def resolve_time_valid_targets(
    identity: InstrumentIdentity,
    at: datetime,
) -> tuple[TargetMapping, ...]:
    accepted_aksharas = [
        TargetMapping(
            target_type="akshara",
            target_value=item.candidate_akshara,
            mapping_method=item.mapping_method,
            confidence=item.confidence,
            review_status=item.review_status,
            valid_from=item.valid_from,
            valid_to=item.valid_to,
            provenance=item.provenance,
        )
        for item in identity.akshara_candidates
        if item.review_status == "accepted" and item.valid_at(at)
    ]
    explicit = [
        item
        for item in (*identity.rashi_candidates, *identity.nakshatra_candidates)
        if item.review_status == "accepted" and item.valid_at(at)
    ]
    return tuple(accepted_aksharas + explicit)


def aggregate_component_score(
    components: dict[str, float | None],
    weights: dict[str, float],
) -> float | None:
    usable = {
        key: value
        for key, value in components.items()
        if value is not None and float(weights.get(key, 0.0)) != 0.0
    }
    if not usable:
        return None
    denominator = sum(abs(float(weights[key])) for key in usable)
    if denominator == 0.0:
        return None
    return sum(float(weights[key]) * float(value) for key, value in usable.items()) / denominator


def _mean_available(values: dict[str, float | None]) -> float | None:
    available = [float(value) for value in values.values() if value is not None]
    return sum(available) / len(available) if available else None


def build_currency_score(
    *,
    currency: str,
    timestamp_utc: datetime,
    profile_id: str,
    sbc_identity_score: float | None,
    currency_event_scores: dict[str, float | None],
    central_bank_scores: dict[str, float | None],
    country_scores: dict[str, float | None],
    mundane_domain_score: float | None,
    component_weights: dict[str, float],
    contributions: tuple[InfluenceContribution, ...],
    uncertainty: UncertaintySummary,
) -> CurrencyScore:
    components = {
        "sbc_identity": sbc_identity_score,
        "currency_event": _mean_available(currency_event_scores),
        "central_bank": _mean_available(central_bank_scores),
        "country_mundane": _mean_available(country_scores),
        "mundane_domain": mundane_domain_score,
    }
    combined = aggregate_component_score(components, component_weights)
    return CurrencyScore(
        currency=currency,
        timestamp_utc=timestamp_utc,
        profile_id=profile_id,
        sbc_identity_score=sbc_identity_score,
        currency_event_scores=dict(currency_event_scores),
        central_bank_scores=dict(central_bank_scores),
        country_scores=dict(country_scores),
        mundane_domain_score=mundane_domain_score,
        combined_score=combined,
        component_weights=dict(component_weights),
        contributions=contributions,
        uncertainty=uncertainty,
        execution_allowed=False,
    )


def derive_fx_pair_score(
    identity: InstrumentIdentity,
    base: CurrencyScore,
    quote: CurrencyScore,
    *,
    no_edge_threshold: float,
) -> FxPairScore:
    if identity.asset_class != "fx_pair":
        raise ValueError("pair score requires an FX-pair identity")
    if identity.base_currency != base.currency or identity.quote_currency != quote.currency:
        raise ValueError("currency scores do not match explicit pair metadata")
    if base.timestamp_utc != quote.timestamp_utc:
        raise ValueError("base and quote scores must share one evidence timestamp")
    if no_edge_threshold < 0:
        raise ValueError("no_edge_threshold must be non-negative")
    if base.combined_score is None or quote.combined_score is None:
        return FxPairScore(
            pair=identity.symbol,
            base_currency=base.currency,
            quote_currency=quote.currency,
            timestamp_utc=base.timestamp_utc,
            base_score=base,
            quote_score=quote,
            differential=None,
            signed_common_mode=None,
            joint_activation=None,
            direction_hypothesis="unknown",
            confidence_band="unknown_missing_currency_evidence",
            invariant_checks={"metadata": True, "timestamp": True},
            explanation=("At least one latent currency score is unavailable; pair direction is unknown.",),
        )
    differential = float(base.combined_score) - float(quote.combined_score)
    common_mode = (float(base.combined_score) + float(quote.combined_score)) / 2.0
    joint_activation = (
        abs(float(base.combined_score)) + abs(float(quote.combined_score))
    ) / 2.0
    if abs(differential) <= no_edge_threshold:
        direction = "no_edge"
    elif differential > 0:
        direction = "base_outperformance"
    else:
        direction = "quote_outperformance"
    return FxPairScore(
        pair=identity.symbol,
        base_currency=base.currency,
        quote_currency=quote.currency,
        timestamp_utc=base.timestamp_utc,
        base_score=base,
        quote_score=quote,
        differential=differential,
        signed_common_mode=common_mode,
        joint_activation=joint_activation,
        direction_hypothesis=direction,
        confidence_band="research_unvalidated",
        invariant_checks={"metadata": True, "timestamp": True},
        explanation=(
            f"{base.currency} latent score {base.combined_score:+.6f}; "
            f"{quote.currency} latent score {quote.combined_score:+.6f}.",
            f"Base-minus-quote differential is {differential:+.6f}.",
            f"Signed common mode is {common_mode:+.6f}; joint activation is "
            f"{joint_activation:.6f}.",
        ),
    )


def validate_currency_invariants(
    scores: dict[str, CurrencyScore],
    *,
    tolerance: float = 1e-9,
) -> list[str]:
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    errors: list[str] = []
    available = {
        currency: float(score.combined_score)
        for currency, score in scores.items()
        if score.combined_score is not None
    }
    for currency in available:
        if abs(available[currency] - available[currency]) > tolerance:
            errors.append(f"identity failed: {currency}/{currency}")
    for left, right in permutations(available, 2):
        forward = available[left] - available[right]
        inverse = available[right] - available[left]
        if abs(forward + inverse) > tolerance:
            errors.append(f"inversion failed: {left}/{right}")
    currencies = sorted(available)
    for left in currencies:
        for middle in currencies:
            for right in currencies:
                lhs = (available[left] - available[middle]) + (
                    available[middle] - available[right]
                )
                rhs = available[left] - available[right]
                if abs(lhs - rhs) > tolerance:
                    errors.append(f"triangle failed: {left},{middle},{right}")
    return errors
