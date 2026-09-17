"""Thin execution release that invokes Evaluator A's frozen business core unchanged."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .adapter_a import validate_adapter_a
from .authorization import validate_release_authorization


def evaluate_admitted_real_event_a(
    event: Mapping[str, Any],
    contracts: Any,
    authorization_capability: object | None = None,
) -> list[dict[str, Any]]:
    """Future-only bridge: frozen A components, no copied C01-C07 semantics."""

    validate_release_authorization(str(event.get("eventId", "")), authorization_capability)

    from ..evaluator_a import evaluator as frozen_a
    context = validate_adapter_a(event)
    rows = [
        frozen_a._evaluate_template(context, contracts, profile, component_id, operator_id)
        for profile, component_id, operator_id in frozen_a._templates(contracts)
    ]
    frozen_a.validate_rows(rows, frozen_a.row_keys_for_event(str(event["eventId"]), contracts), contracts.allowed_unknown_codes)
    return rows
