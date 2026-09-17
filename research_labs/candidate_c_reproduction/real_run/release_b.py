"""Thin execution release that invokes Evaluator B's frozen business core unchanged."""

from __future__ import annotations

from typing import Any

from .adapter_b import RealCandidateCEvent
from .authorization import validate_release_authorization


def evaluate_admitted_real_event_b(
    event: RealCandidateCEvent,
    contracts: Any,
    authorization_capability: object | None = None,
) -> list[dict[str, Any]]:
    """Future-only bridge: frozen B components, no copied C01-C07 semantics."""

    validate_release_authorization(event.event_id, authorization_capability)

    from ..evaluator_b import evaluator as frozen_b
    motion_row, motion_value = frozen_b._motion_row(event, contracts)
    rows = [
        frozen_b._natural_class(event, contracts, motion_value),
        frozen_b._relationship_row(event, contracts),
        frozen_b._temporary_row(event, contracts),
        frozen_b._compound_row(event, contracts),
        frozen_b._ordinary_drsti_row(event, contracts),
        frozen_b._special_drsti_row(event, contracts),
        motion_row,
        frozen_b._individual_record_row(event, contracts),
    ]
    frozen_b.validate_output_rows(rows, contracts)
    return rows
