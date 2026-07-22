from __future__ import annotations

from datetime import datetime

from ..models import (
    AspectPriorRecord,
    DirectionalPrior,
    DynamicContribution,
    NatalAspectGraph,
    RuntimeEvaluation,
    TransitNatalEvent,
    stable_hash,
)
from ..profiles import ResearchProfiles
from .activation_propagation import resolve_activation_paths


ACTIVATION_RANK = {
    "UNKNOWN": 0,
    "WEAK": 1,
    "MODERATE": 2,
    "STRONG": 3,
    "EXCEPTIONAL": 4,
}
VOLATILITY_RANK = {"UNKNOWN": 0, "LOW": 1, "ELEVATED": 2, "HIGH": 3}


def _combine_direction(
    static: DirectionalPrior,
    contributions: tuple[DynamicContribution, ...],
) -> tuple[DirectionalPrior, tuple[str, ...]]:
    values = [static] + [item.directional_effect for item in contributions]
    determinate = {value for value in values if value != "INDETERMINATE"}
    if not determinate:
        return "INDETERMINATE", ()
    if "MIXED" in determinate or len(determinate) > 1:
        return "MIXED", ("DIRECTIONAL_EVIDENCE_CONFLICT_PRESERVED",)
    return next(iter(determinate)), ()


def _maximum_label(values: list[str], rank: dict[str, int]) -> str:
    return max(values, key=lambda value: rank[value])


def evaluate_runtime_event(
    event: TransitNatalEvent,
    prior: AspectPriorRecord,
    graph: NatalAspectGraph,
    profiles: ResearchProfiles,
    *,
    as_of_utc: datetime,
    dynamic_contributions: tuple[DynamicContribution, ...] = (),
) -> RuntimeEvaluation:
    if as_of_utc.tzinfo is None or as_of_utc.utcoffset() is None:
        raise ValueError("as_of_utc must be timezone-aware")
    if as_of_utc < event.event_timestamp_utc:
        raise ValueError("evaluation cannot precede the event timestamp")
    if as_of_utc < event.evidence_available_at_utc:
        raise ValueError("evaluation cannot precede event evidence availability")
    if event.chart_id != prior.chart_id or event.chart_id != graph.chart_id:
        raise ValueError("event, prior, and graph chart IDs must match")
    if prior.natal_context_id != graph.natal_context_id:
        raise ValueError("prior and graph natal context IDs must match")
    if (
        event.transit_body != prior.transit_body
        or event.natal_target != prior.natal_target
        or event.aspect_type != prior.aspect_type
    ):
        raise ValueError("event does not match the frozen structural prior")
    future = [
        item.contribution_id
        for item in dynamic_contributions
        if item.available_at_utc > as_of_utc
    ]
    if future:
        raise ValueError(
            f"future dynamic evidence is forbidden: {', '.join(sorted(future))}"
        )

    ordered_dynamic = tuple(
        sorted(
            dynamic_contributions,
            key=lambda item: (item.available_at_utc, item.contribution_id),
        )
    )
    direction, conflicts = _combine_direction(prior.directional_prior, ordered_dynamic)
    activation = _maximum_label(
        [prior.activation_prior] + [item.activation_effect for item in ordered_dynamic],
        ACTIVATION_RANK,
    )
    volatility = _maximum_label(
        [prior.volatility_prior] + [item.volatility_effect for item in ordered_dynamic],
        VOLATILITY_RANK,
    )
    paths = resolve_activation_paths(graph, event.natal_target, profiles)
    payload = {
        "event_id": event.event_id,
        "as_of_utc": as_of_utc,
        "event_contract": event.event_contract,
        "chart_id": event.chart_id,
        "prior_id": prior.prior_id,
        "natal_context_id": graph.natal_context_id,
        "directional_result": direction,
        "activation_result": activation,
        "volatility_result": volatility,
        "activation_paths": paths,
        "dynamic_contributions": ordered_dynamic,
        "conflict_flags": conflicts,
        "unknowns": prior.unknowns,
        "timestamp_safe": True,
    }
    return RuntimeEvaluation(
        event_id=event.event_id,
        as_of_utc=as_of_utc,
        event_contract=event.event_contract,
        chart_id=event.chart_id,
        prior_id=prior.prior_id,
        natal_context_id=graph.natal_context_id,
        directional_result=direction,
        activation_result=activation,  # type: ignore[arg-type]
        volatility_result=volatility,  # type: ignore[arg-type]
        activation_paths=paths,
        dynamic_contributions=ordered_dynamic,
        conflict_flags=conflicts,
        unknowns=prior.unknowns,
        timestamp_safe=True,
        evaluation_hash=stable_hash(payload),
        execution_allowed=False,
        automatic_order_placement=False,
    )
