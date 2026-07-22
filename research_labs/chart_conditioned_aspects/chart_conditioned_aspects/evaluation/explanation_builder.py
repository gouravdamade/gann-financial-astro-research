from __future__ import annotations

from ..models import AspectPriorRecord, RuntimeEvaluation


def explain_prior(prior: AspectPriorRecord) -> tuple[str, ...]:
    lines = [
        f"Direction: {prior.directional_prior}",
        f"Activation: {prior.activation_prior}",
        f"Volatility: {prior.volatility_prior}",
    ]
    lines.extend(
        f"{entry.category}: {entry.reason}" for entry in prior.explanation_ledger
    )
    if prior.unknowns:
        lines.append(f"Unknown or blocked: {', '.join(prior.unknowns)}")
    lines.append("Research-only output; it cannot place or authorize an order.")
    return tuple(lines)


def explain_runtime(evaluation: RuntimeEvaluation) -> tuple[str, ...]:
    lines = [
        f"As of: {evaluation.as_of_utc.isoformat()}",
        f"Direction: {evaluation.directional_result}",
        f"Activation: {evaluation.activation_result}",
        f"Volatility: {evaluation.volatility_result}",
        f"Activated graph paths: {len(evaluation.activation_paths)}",
    ]
    if evaluation.conflict_flags:
        lines.append(f"Conflicts preserved: {', '.join(evaluation.conflict_flags)}")
    lines.append("Timestamp-safe research output; execution remains disabled.")
    return tuple(lines)
