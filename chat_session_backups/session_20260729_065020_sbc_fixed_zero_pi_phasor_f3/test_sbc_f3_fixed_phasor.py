from __future__ import annotations

import hashlib
import json
import math
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from sbc.atomic_intervals import (
    SbcAtomicBoundary,
    SbcAtomicContribution,
    SbcAtomicIntervalCompiler,
)
from sbc.fixed_phasor import (
    FIXED_PHASOR_CONTRACT,
    FIXED_PHASOR_POLICY,
    PI_ANGLE,
    PLOTTED,
    UNKNOWN,
    UNKNOWN_NOT_PLOTTED,
    VISUALIZATION_ONLY_ROLE,
    ZERO_ANGLE,
    SbcFixedPhasorCompiler,
)
from sbc.multidimensional_ledger import SbcMultidimensionalLedgerCompiler


START = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _contribution(label: str, units: float | None) -> SbcAtomicContribution:
    return SbcAtomicContribution(
        source_lineage_id=_digest(f"lineage:{label}"),
        body=label.upper(),
        source_nakshatra="KRITTIKA",
        vedha_direction="FRONT",
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
                _contribution("jupiter", 2.0),
                _contribution("saturn", -1.0),
                _contribution("sun", 0.0),
                *((_contribution("mercury", None),) if unknown else ()),
            ),
            missing=("MISSING-MOON",) if unknown else (),
        ),
        _boundary(
            START + timedelta(hours=1),
            "second",
            (_contribution("venus", 0.5),),
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


def test_fixed_zero_pi_projection_exactly_reproduces_p2_scalar_ledger() -> None:
    projection = SbcFixedPhasorCompiler().compile(_ledger())
    first = projection.intervals[0]

    assert projection.contract == FIXED_PHASOR_CONTRACT
    assert projection.projection_policy == FIXED_PHASOR_POLICY
    assert first.source_net_units == 1.0
    assert first.vector_real_sum_units == 1.0
    assert first.source_gross_activation_units == 3.0
    assert first.vector_magnitude_sum_units == 3.0
    assert first.vector_imaginary_sum_units == 0.0
    assert first.known_scored_coherence_ratio == pytest.approx(1.0 / 3.0)
    assert first.reconciled is True

    vectors = {item.actor_identity: item for item in first.vectors}
    assert vectors["JUPITER"].fixed_angle == ZERO_ANGLE
    assert vectors["JUPITER"].fixed_angle_radians == 0.0
    assert vectors["JUPITER"].real_component_units == 2.0
    assert vectors["SATURN"].fixed_angle == PI_ANGLE
    assert vectors["SATURN"].fixed_angle_radians == math.pi
    assert vectors["SATURN"].real_component_units == -1.0
    assert vectors["SUN"].fixed_angle == ZERO_ANGLE
    assert all(item.projection_status == PLOTTED for item in vectors.values())


def test_unknown_evidence_remains_null_and_is_never_projected_as_zero() -> None:
    projection = SbcFixedPhasorCompiler().compile(_ledger(unknown=True))
    first = projection.intervals[0]
    unknown_vectors = [
        item for item in first.vectors if item.projection_status == UNKNOWN_NOT_PLOTTED
    ]

    assert first.unknown_vector_count == 2
    assert first.unknowns_preserved is True
    assert all(item.signed_guidance_units is None for item in unknown_vectors)
    assert all(item.magnitude_units is None for item in unknown_vectors)
    assert all(item.fixed_angle is None for item in unknown_vectors)
    assert all(item.real_component_units is None for item in unknown_vectors)
    gate = next(
        item
        for item in projection.validation_gates
        if item.gate_id == "UNKNOWN_EVIDENCE"
    )
    assert gate.state == UNKNOWN


def test_projection_is_deterministic_visualization_only_and_non_voting() -> None:
    compiler = SbcFixedPhasorCompiler()
    first = compiler.compile(_ledger())
    second = compiler.compile(_ledger())

    assert first.projection_series_id == second.projection_series_id
    assert first.to_dict() == second.to_dict()
    assert all(
        item.derivation_role == VISUALIZATION_ONLY_ROLE
        and item.counts_as_independent_vote is False
        and item.directional_contribution == 0.0
        for interval in first.intervals
        for item in interval.vectors
    )
    assert first.guardrails.scalar_equivalent_only is True
    assert first.guardrails.fixed_zero_pi_only is True
    assert first.guardrails.timing_phase_included is False
    assert first.guardrails.physical_wave_claimed is False
    assert first.guardrails.execution_allowed is False
    payload = json.dumps(first.to_dict(), sort_keys=True)
    assert '"timing_phase_included": false' in payload
    assert '"counts_as_independent_vote": false' in payload


def test_weakened_source_guardrails_fail_closed() -> None:
    source = _ledger()
    unsafe = replace(
        source,
        guardrails=replace(source.guardrails, phase_included=True),
    )

    with pytest.raises(ValueError, match="weakens required F3 guardrails"):
        SbcFixedPhasorCompiler().compile(unsafe)


def test_corrupted_source_scalar_summary_fails_closed() -> None:
    source = _ledger()
    interval = source.interval_ledgers[0]
    corrupted = replace(
        interval,
        total_summary=replace(
            interval.total_summary,
            net_guidance_units=interval.total_summary.net_guidance_units + 0.25,
        ),
    )
    broken = replace(
        source,
        interval_ledgers=(corrupted, *source.interval_ledgers[1:]),
    )

    with pytest.raises(ValueError, match="source cluster totals differ"):
        SbcFixedPhasorCompiler().compile(broken)


def test_wrong_interval_link_and_unreconciled_axis_fail_closed() -> None:
    source = _ledger()
    interval = source.interval_ledgers[0]
    wrong_cluster = replace(
        interval.causal_clusters[0],
        interval_id=_digest("wrong-interval"),
    )
    wrong_link = replace(
        source,
        interval_ledgers=(
            replace(
                interval,
                causal_clusters=(wrong_cluster, *interval.causal_clusters[1:]),
            ),
            *source.interval_ledgers[1:],
        ),
    )
    with pytest.raises(ValueError, match="wrong interval"):
        SbcFixedPhasorCompiler().compile(wrong_link)

    reconciliation = interval.axis_reconciliations[0]
    unreconciled = replace(
        source,
        interval_ledgers=(
            replace(
                interval,
                axis_reconciliations=(
                    replace(reconciliation, reconciled=False),
                    *interval.axis_reconciliations[1:],
                ),
            ),
            *source.interval_ledgers[1:],
        ),
    )
    with pytest.raises(ValueError, match="unreconciled P2 axis"):
        SbcFixedPhasorCompiler().compile(unreconciled)
