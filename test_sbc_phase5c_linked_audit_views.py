from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from sbc.atomic_intervals import (
    SbcAtomicBoundary,
    SbcAtomicContribution,
    SbcAtomicIntervalCompiler,
    boundary_from_chakra_snapshot,
)
from sbc.audit_views import (
    LINKED_AUDIT_VIEW_CONTRACT,
    PASS,
    RAY_AUDIT_VIEW,
    UNKNOWN,
    SbcLinkedAuditViewCompiler,
)
from sbc.chakra_lab import ChakraLabActorSelection, ChakraLabEngine, ChakraLabRequest
from sbc.models import GeoLocation
from sbc.multidimensional_ledger import (
    ACTOR_AXIS,
    SbcMultidimensionalLedgerCompiler,
)


START = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _contribution(
    label: str,
    units: float | None,
    *,
    body: str,
    direction: str,
) -> SbcAtomicContribution:
    return SbcAtomicContribution(
        source_lineage_id=_digest(f"lineage:{label}"),
        body=body,
        source_nakshatra="KRITTIKA",
        vedha_direction=direction,
        target_row=1,
        target_column=2,
        target_layer="RASHI",
        target_value=f"TARGET:{label}",
        target_witness_set_id="WITNESS-1",
        target_evidence_status="PAGE_CERTIFIED",
        nature="BENEFIC" if units is None or units >= 0 else "MALEFIC",
        effective_multiplier=1.0 if units is not None else None,
        signed_guidance_units=units,
        status="SCORED" if units is not None else "UNRESOLVED_PLANET_NATURE",
        explanation=f"fixture contribution {label}",
        citation_source_ids=("SOURCE-A",),
        unknown_reason="fixture unresolved evidence" if units is None else None,
    )


def _boundary(
    at: datetime,
    label: str,
    contributions: tuple[SbcAtomicContribution, ...],
    *,
    missing: tuple[str, ...] = (),
) -> SbcAtomicBoundary:
    return SbcAtomicBoundary(
        starts_at_utc=at,
        evidence_cutoff_utc=at - timedelta(minutes=1),
        boundary_reason=f"fixture:{label}",
        snapshot_id=_digest(f"snapshot:{label}"),
        foundation_profile_id="foundation-v1",
        foundation_profile_hash=_digest("foundation"),
        grid_profile_id="grid-v1",
        grid_profile_hash=_digest("grid"),
        vedha_profile_id="vedha-v1",
        vedha_profile_hash=_digest("vedha"),
        guidance_model_id="guidance-v1",
        source_ids=("SOURCE-A", "SOURCE-B"),
        guidance_available=True,
        contributions=contributions,
        missing_evidence_ids=missing,
    )


def _ledger(*, unknown: bool = False):
    boundaries = (
        _boundary(
            START,
            "first",
            (
                _contribution(
                    "jupiter",
                    2.0,
                    body="JUPITER",
                    direction="FRONT",
                ),
                _contribution(
                    "saturn",
                    None if unknown else -1.0,
                    body="SATURN",
                    direction="LEFT",
                ),
            ),
        ),
        _boundary(
            START + timedelta(hours=1),
            "second",
            (
                _contribution(
                    "sun",
                    0.5,
                    body="SUN",
                    direction="RIGHT",
                ),
            ),
        ),
    )
    atomic = SbcAtomicIntervalCompiler().compile(
        boundaries,
        terminal_end_utc=START + timedelta(hours=3),
    )
    return SbcMultidimensionalLedgerCompiler().compile(
        atomic,
        instrument_identity="FX:USDJPY",
    )


def test_linked_audit_view_preserves_p2_values_and_cross_links() -> None:
    source = _ledger()
    view = SbcLinkedAuditViewCompiler().compile(source)

    assert view.contract == LINKED_AUDIT_VIEW_CONTRACT
    assert view.instrument_identity == "FX:USDJPY"
    assert len(view.intervals) == 2
    assert view.intervals[0].duration_seconds == 3600
    assert view.intervals[1].duration_seconds == 7200
    assert view.intervals[0].total_summary.net_guidance_units == 1.0
    assert view.intervals[0].total_summary.gross_activation_units == 3.0
    assert all(item.all_axes_reconciled for item in view.intervals)
    assert all(item.reconciled for item in view.reconciliations)

    cell_ids = {item.cell_id for item in view.ledger_cells}
    cluster_ids = {item.cluster_id for item in view.ray_rows}
    assert {
        cluster_id
        for item in view.intervals
        for cluster_id in item.cluster_ids
    } == cluster_ids
    assert {cell_id for item in view.intervals for cell_id in item.cell_ids} == cell_ids
    assert all(set(item.cell_ids) <= cell_ids for item in view.ray_rows)
    assert all(set(item.cluster_ids) <= cluster_ids for item in view.ledger_cells)
    assert {item.cluster_id for item in view.lineage_rows} == cluster_ids


def test_ray_audit_is_vedha_direction_only_and_never_a_phase_signal() -> None:
    view = SbcLinkedAuditViewCompiler().compile(_ledger())
    ray_descriptor = next(item for item in view.views if item.view_id == RAY_AUDIT_VIEW)

    assert ray_descriptor.phase_vector_included is False
    assert ray_descriptor.counts_as_independent_vote is False
    assert ray_descriptor.directional_contribution == 0.0
    assert {item.vedha_direction for item in view.ray_rows} == {
        "FRONT",
        "LEFT",
        "RIGHT",
    }
    assert all(item.phase_angle is None for item in view.ray_rows)
    assert all(item.phase_vector_included is False for item in view.ray_rows)
    assert all(item.counts_as_independent_vote is False for item in view.ray_rows)
    assert all(item.directional_contribution == 0.0 for item in view.ray_rows)
    assert view.guardrails.phase_included is False
    assert view.guardrails.execution_allowed is False


def test_unknown_and_unvalidated_states_remain_visible() -> None:
    view = SbcLinkedAuditViewCompiler().compile(_ledger(unknown=True))
    gates = {item.gate_id: item for item in view.validation_gates}

    assert gates["TIMESTAMP_SAFETY"].state == PASS
    assert gates["AXIS_RECONCILIATION"].state == PASS
    assert gates["UNKNOWN_EVIDENCE"].state == UNKNOWN
    assert gates["FINANCIAL_VALIDATION"].state == UNKNOWN
    assert gates["PHASE_PROFILE"].state == UNKNOWN
    assert gates["EXECUTION_LOCK"].state == PASS
    assert view.intervals[0].total_summary.unknown_contribution_count == 1
    assert view.intervals[0].total_summary.unknown_magnitude_units is None
    unknown = next(item for item in view.ray_rows if item.signed_guidance_units is None)
    assert unknown.unknown_reason == "fixture unresolved evidence"
    assert unknown.status == "UNRESOLVED_PLANET_NATURE"


def test_serialization_and_replay_are_deterministic() -> None:
    compiler = SbcLinkedAuditViewCompiler()
    first = compiler.compile(_ledger())
    second = compiler.compile(_ledger())

    assert first.audit_view_id == second.audit_view_id
    assert first.to_dict() == second.to_dict()
    payload = json.dumps(first.to_dict(), sort_keys=True)
    assert '"execution_allowed": false' in payload
    assert '"phase_angle": null' in payload
    assert '"phase_included": false' in payload
    assert '"counts_as_independent_vote": false' in payload


def test_weakened_guardrail_and_broken_cell_link_fail_closed() -> None:
    source = _ledger()
    unsafe = replace(
        source,
        guardrails=replace(source.guardrails, phase_included=True),
    )
    with pytest.raises(ValueError, match="weakens required P3 guardrails"):
        SbcLinkedAuditViewCompiler().compile(unsafe)

    first_interval = source.interval_ledgers[0]
    actor_cell = next(
        item for item in first_interval.dimension_cells if item.axis == ACTOR_AXIS
    )
    broken_cell = replace(
        actor_cell,
        cluster_ids=(_digest("unknown-cluster"),),
    )
    broken_interval = replace(
        first_interval,
        dimension_cells=tuple(
            broken_cell if item.cell_id == actor_cell.cell_id else item
            for item in first_interval.dimension_cells
        ),
    )
    broken = replace(
        source,
        interval_ledgers=(broken_interval, *source.interval_ledgers[1:]),
    )
    with pytest.raises(ValueError, match="unknown interval cluster"):
        SbcLinkedAuditViewCompiler().compile(broken)


def test_real_chakra_boundaries_flow_through_p1_p2_and_p3() -> None:
    engine = ChakraLabEngine()
    location = GeoLocation(
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
        altitude_m=216.0,
    )
    snapshots = tuple(
        engine.snapshot(
            ChakraLabRequest(
                at=START + timedelta(hours=index),
                location=location,
                bodies=("SUN", "MOON", "JUPITER"),
                actors=(
                    ChakraLabActorSelection("SUN"),
                    ChakraLabActorSelection("MOON"),
                    ChakraLabActorSelection("JUPITER"),
                ),
            )
        )
        for index in range(2)
    )
    boundaries = tuple(
        boundary_from_chakra_snapshot(
            snapshot,
            boundary_reason=f"fixture boundary {index + 1}",
        )
        for index, snapshot in enumerate(snapshots)
    )
    atomic = SbcAtomicIntervalCompiler().compile(
        boundaries,
        terminal_end_utc=START + timedelta(hours=2),
    )
    ledger = SbcMultidimensionalLedgerCompiler().compile(
        atomic,
        instrument_identity="FX:USDJPY",
    )
    view = SbcLinkedAuditViewCompiler().compile(ledger)

    assert view.source_ledger_id == ledger.ledger_id
    assert len(view.intervals) == 2
    assert all(item.evidence_cutoff_utc <= item.start_utc for item in view.intervals)
    assert any(
        item.status == "MISSING_EVIDENCE"
        and item.unknown_reason == "Explicit missing evidence: ACTOR:JUPITER:MOTION_REQUIRED"
        for item in view.ray_rows
    )
