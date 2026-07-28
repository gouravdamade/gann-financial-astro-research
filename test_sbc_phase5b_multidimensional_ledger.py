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
from sbc.chakra_lab import ChakraLabActorSelection, ChakraLabEngine, ChakraLabRequest
from sbc.models import GeoLocation
from sbc.multidimensional_ledger import (
    ACTOR_AXIS,
    DERIVED_AXIS_ROLE,
    LEDGER_AXES,
    MULTIDIMENSIONAL_LEDGER_CONTRACT,
    NATURE_AXIS,
    PRIMARY_EVIDENCE_ROLE,
    SOURCE_LINEAGE_AXIS,
    TARGET_LAYER_AXIS,
    TOTAL_AXIS,
    UNAVAILABLE_DIMENSION_KEY,
    VEDHA_DIRECTION_AXIS,
    SbcLedgerDimensionCell,
    SbcMultidimensionalLedgerCompiler,
)


START = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _contribution(
    label: str,
    units: float | None,
    *,
    lineage: str | None = None,
    body: str = "JUPITER",
    layer: str = "RASHI",
    nature: str | None = None,
    direction: str = "FRONT",
) -> SbcAtomicContribution:
    return SbcAtomicContribution(
        source_lineage_id=_digest(f"lineage:{lineage or label}"),
        body=body,
        source_nakshatra="KRITTIKA",
        vedha_direction=direction,
        target_row=1,
        target_column=2,
        target_layer=layer,
        target_value=f"TARGET:{label}",
        target_witness_set_id="WITNESS-1",
        target_evidence_status="PAGE_CERTIFIED",
        nature=nature or ("BENEFIC" if units is None or units >= 0 else "MALEFIC"),
        effective_multiplier=1.0 if units is not None else None,
        signed_guidance_units=units,
        status="SCORED" if units is not None else "UNRESOLVED_PLANET_NATURE",
        explanation=f"fixture contribution {label}",
        citation_source_ids=("SOURCE-A",),
        unknown_reason="fixture unresolved evidence" if units is None else None,
    )


def _series(
    contributions: tuple[SbcAtomicContribution, ...] = (),
    *,
    missing_evidence_ids: tuple[str, ...] = (),
):
    boundary = SbcAtomicBoundary(
        starts_at_utc=START,
        evidence_cutoff_utc=START - timedelta(minutes=1),
        boundary_reason="fixture:P2",
        snapshot_id=_digest("snapshot:P2"),
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
        missing_evidence_ids=missing_evidence_ids,
    )
    return SbcAtomicIntervalCompiler().compile(
        (boundary,),
        terminal_end_utc=START + timedelta(hours=1),
    )


def _cells_by_axis(interval_ledger, axis: str):
    return {
        item.key: item
        for item in interval_ledger.dimension_cells
        if item.axis == axis
    }


def test_multidimensional_ledger_reconciles_every_axis_without_extra_votes() -> None:
    series = _series(
        (
            _contribution(
                "jupiter",
                2.0,
                body="JUPITER",
                layer="RASHI",
                direction="FRONT",
            ),
            _contribution(
                "saturn",
                -1.0,
                body="SATURN",
                layer="NAKSHATRA",
                nature="MALEFIC",
                direction="LEFT",
            ),
        )
    )
    ledger = SbcMultidimensionalLedgerCompiler().compile(
        series,
        instrument_identity="FX:USDJPY",
    )
    interval = ledger.interval_ledgers[0]

    assert ledger.contract == MULTIDIMENSIONAL_LEDGER_CONTRACT
    assert interval.total_summary.favorable_guidance_units == 2.0
    assert interval.total_summary.adverse_guidance_units == -1.0
    assert interval.total_summary.net_guidance_units == 1.0
    assert interval.total_summary.gross_activation_units == 3.0
    assert set(_cells_by_axis(interval, ACTOR_AXIS)) == {"JUPITER", "SATURN"}
    assert set(_cells_by_axis(interval, TARGET_LAYER_AXIS)) == {
        "NAKSHATRA",
        "RASHI",
    }
    assert set(_cells_by_axis(interval, NATURE_AXIS)) == {"BENEFIC", "MALEFIC"}
    assert set(_cells_by_axis(interval, VEDHA_DIRECTION_AXIS)) == {
        "FRONT",
        "LEFT",
    }
    assert len(_cells_by_axis(interval, SOURCE_LINEAGE_AXIS)) == 2
    assert list(_cells_by_axis(interval, TOTAL_AXIS)) == ["ALL"]
    assert all(item.reconciled for item in interval.axis_reconciliations)
    assert {item.axis for item in interval.axis_reconciliations} == set(LEDGER_AXES)
    assert all(
        item.derivation_role == PRIMARY_EVIDENCE_ROLE
        for item in interval.causal_clusters
    )
    assert all(
        item.derivation_role == DERIVED_AXIS_ROLE
        for item in interval.dimension_cells
    )
    assert ledger.guardrails.counts_as_independent_vote is False
    assert ledger.guardrails.directional_contribution == 0.0
    assert ledger.guardrails.fx_subtraction_included is False
    assert ledger.guardrails.phase_included is False
    assert ledger.guardrails.confidence_included is False
    assert ledger.guardrails.execution_allowed is False


def test_unknown_and_missing_evidence_remain_null_and_use_unavailable_dimension() -> None:
    series = _series(
        (_contribution("unknown", None),),
        missing_evidence_ids=("ACTOR:MARS:NOT_READY",),
    )
    interval = SbcMultidimensionalLedgerCompiler().compile(
        series,
        instrument_identity="FX:USDJPY",
    ).interval_ledgers[0]

    assert interval.total_summary.scored_contribution_count == 0
    assert interval.total_summary.unknown_contribution_count == 2
    assert interval.total_summary.missing_evidence_count == 1
    assert interval.total_summary.unknown_magnitude_units is None
    unavailable_actor = _cells_by_axis(interval, ACTOR_AXIS)[
        UNAVAILABLE_DIMENSION_KEY
    ]
    assert unavailable_actor.summary.missing_evidence_count == 1
    assert unavailable_actor.summary.unknown_magnitude_units is None
    for axis in (ACTOR_AXIS, TARGET_LAYER_AXIS, NATURE_AXIS, VEDHA_DIRECTION_AXIS):
        assert UNAVAILABLE_DIMENSION_KEY in _cells_by_axis(interval, axis)
    assert all(item.reconciled for item in interval.axis_reconciliations)


def test_exact_repeated_primary_evidence_is_deduplicated_before_aggregation() -> None:
    contribution = _contribution("known", 1.5)
    source = _series((contribution,))
    interval = replace(
        source.intervals[0],
        contributions=(contribution, contribution),
    )
    repeated = replace(source, intervals=(interval,))

    result = SbcMultidimensionalLedgerCompiler().compile(
        repeated,
        instrument_identity="FX:USDJPY",
    ).interval_ledgers[0]

    assert result.duplicate_primary_evidence_count == 1
    assert len(result.causal_clusters) == 1
    assert result.total_summary.scored_contribution_count == 1
    assert result.total_summary.net_guidance_units == 1.5


def test_conflicting_evaluations_for_one_source_lineage_fail_closed() -> None:
    first = _contribution("first", 1.0, lineage="same")
    second = _contribution("second", 2.0, lineage="same")
    source = _series((first, second))

    with pytest.raises(ValueError, match="conflicting evaluated contributions"):
        SbcMultidimensionalLedgerCompiler().compile(
            source,
            instrument_identity="FX:USDJPY",
        )


def test_instrument_identity_is_part_of_cluster_and_series_identity() -> None:
    source = _series((_contribution("known", 1.0),))
    compiler = SbcMultidimensionalLedgerCompiler()
    usd_jpy = compiler.compile(source, instrument_identity="FX:USDJPY")
    eur_usd = compiler.compile(source, instrument_identity="FX:EURUSD")

    assert usd_jpy.ledger_id != eur_usd.ledger_id
    assert (
        usd_jpy.interval_ledgers[0].causal_clusters[0].cluster_id
        != eur_usd.interval_ledgers[0].causal_clusters[0].cluster_id
    )
    assert usd_jpy.source_atomic_series_id == eur_usd.source_atomic_series_id


def test_replay_and_serialization_are_deterministic_across_contribution_order() -> None:
    first = _contribution("first", 1.0)
    second = _contribution("second", -0.5)
    source = _series((first, second))
    reordered_interval = replace(
        source.intervals[0],
        contributions=tuple(reversed(source.intervals[0].contributions)),
    )
    reordered_source = replace(source, intervals=(reordered_interval,))
    compiler = SbcMultidimensionalLedgerCompiler()
    ordered = compiler.compile(source, instrument_identity="FX:USDJPY")
    reordered = compiler.compile(
        reordered_source,
        instrument_identity="FX:USDJPY",
    )

    assert ordered.ledger_id == reordered.ledger_id
    assert ordered.to_dict() == reordered.to_dict()
    payload = json.dumps(ordered.to_dict(), sort_keys=True)
    assert "MARKET_DIRECTION" in payload
    assert '"execution_allowed": false' in payload


def test_weakened_source_guardrail_and_scalar_ledger_mismatch_fail_closed() -> None:
    source = _series((_contribution("known", 1.0),))
    unsafe = replace(
        source,
        guardrails=replace(source.guardrails, execution_allowed=True),
    )
    with pytest.raises(ValueError, match="weakens required P2 guardrails"):
        SbcMultidimensionalLedgerCompiler().compile(
            unsafe,
            instrument_identity="FX:USDJPY",
        )

    incorrect_interval = replace(
        source.intervals[0],
        ledger=replace(
            source.intervals[0].ledger,
            net_guidance_units=99.0,
        ),
    )
    incorrect = replace(source, intervals=(incorrect_interval,))
    with pytest.raises(ValueError, match="do not reproduce the P1 scalar ledger"):
        SbcMultidimensionalLedgerCompiler().compile(
            incorrect,
            instrument_identity="FX:USDJPY",
        )


def test_empty_interval_is_visible_and_reconciles_without_invented_evidence() -> None:
    source = _series()
    interval = SbcMultidimensionalLedgerCompiler().compile(
        source,
        instrument_identity="FX:USDJPY",
    ).interval_ledgers[0]

    assert interval.causal_clusters == ()
    assert interval.total_summary.total_evidence_count == 0
    assert interval.total_summary.unknown_magnitude_units == 0.0
    assert list(_cells_by_axis(interval, TOTAL_AXIS)) == ["ALL"]
    assert _cells_by_axis(interval, ACTOR_AXIS) == {}
    assert all(item.reconciled for item in interval.axis_reconciliations)


def test_dimension_cell_rejects_voting_or_non_derived_role() -> None:
    source = _series((_contribution("known", 1.0),))
    result = SbcMultidimensionalLedgerCompiler().compile(
        source,
        instrument_identity="FX:USDJPY",
    )
    cell = result.interval_ledgers[0].dimension_cells[0]

    with pytest.raises(ValueError, match="cannot count as independent votes"):
        replace(cell, counts_as_independent_vote=True)
    with pytest.raises(ValueError, match="must use DERIVED_AXIS"):
        replace(cell, derivation_role=PRIMARY_EVIDENCE_ROLE)
    with pytest.raises(ValueError, match="unknown ledger axis"):
        SbcLedgerDimensionCell(
            interval_id=cell.interval_id,
            axis="MARKET_DIRECTION",
            key="BULLISH",
            derivation_role=DERIVED_AXIS_ROLE,
            cluster_ids=cell.cluster_ids,
            summary=cell.summary,
        )


def test_real_chakra_snapshot_flows_through_atomic_and_multidimensional_layers() -> None:
    snapshot = ChakraLabEngine().snapshot(
        ChakraLabRequest(
            at=datetime(2026, 7, 17, 6, 30, tzinfo=timezone.utc),
            location=GeoLocation(
                latitude=28.6139,
                longitude=77.2090,
                timezone="Asia/Kolkata",
                altitude_m=216.0,
            ),
            bodies=("SUN", "MOON", "JUPITER"),
            actors=(
                ChakraLabActorSelection("SUN"),
                ChakraLabActorSelection("JUPITER"),
            ),
        )
    )
    boundary = boundary_from_chakra_snapshot(
        snapshot,
        boundary_reason="fixture chakra transition",
    )
    atomic = SbcAtomicIntervalCompiler().compile(
        (boundary,),
        terminal_end_utc=snapshot.as_of_utc + timedelta(hours=1),
    )
    ledger = SbcMultidimensionalLedgerCompiler().compile(
        atomic,
        instrument_identity="FX:USDJPY",
    )
    interval = ledger.interval_ledgers[0]

    assert interval.total_summary == atomic.intervals[0].ledger
    assert {
        item.source_lineage_id
        for item in interval.causal_clusters
        if item.contribution_id is not None
    } == {item.source_lineage_id for item in boundary.contributions}
    assert any(
        item.missing_evidence_id == "ACTOR:JUPITER:MOTION_REQUIRED"
        for item in interval.causal_clusters
    )
    assert all(item.reconciled for item in interval.axis_reconciliations)
