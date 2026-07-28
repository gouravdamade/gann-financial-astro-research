from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from sbc.atomic_intervals import (
    ATOMIC_INTERVAL_CONTRACT,
    ATOMIC_INTERVAL_POLICY,
    RESEARCH_CLASSIFICATION,
    SbcAtomicBoundary,
    SbcAtomicContribution,
    SbcAtomicIntervalCompiler,
    boundary_from_chakra_snapshot,
)
from sbc.chakra_lab import (
    ChakraLabActorSelection,
    ChakraLabEngine,
    ChakraLabGuardrails,
    ChakraLabRequest,
)
from sbc.models import GeoLocation
from sbc.vedha import GUIDANCE_MODEL_ID, load_vedha_profile


START = datetime(2026, 7, 28, 6, 0, tzinfo=timezone.utc)
PROFILE_HASHES = {
    "foundation_profile_hash": hashlib.sha256(b"foundation").hexdigest().upper(),
    "grid_profile_hash": hashlib.sha256(b"grid").hexdigest().upper(),
    "vedha_profile_hash": hashlib.sha256(b"vedha").hexdigest().upper(),
}


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _contribution(
    label: str,
    units: float | None,
) -> SbcAtomicContribution:
    return SbcAtomicContribution(
        source_lineage_id=_digest(f"lineage:{label}"),
        body="JUPITER",
        source_nakshatra="KRITTIKA",
        vedha_direction="FRONT",
        target_row=1,
        target_column=2,
        target_layer="RASHI",
        target_value="MESHA",
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
    label: str,
    at: datetime,
    *,
    contributions: tuple[SbcAtomicContribution, ...] = (),
    guidance_available: bool = True,
    missing_evidence_ids: tuple[str, ...] = (),
    cutoff: datetime | None = None,
    foundation_profile_hash: str | None = None,
) -> SbcAtomicBoundary:
    return SbcAtomicBoundary(
        starts_at_utc=at,
        evidence_cutoff_utc=cutoff or at,
        boundary_reason=f"fixture:{label}",
        snapshot_id=_digest(f"snapshot:{label}"),
        foundation_profile_id="foundation-v1",
        foundation_profile_hash=(
            foundation_profile_hash or PROFILE_HASHES["foundation_profile_hash"]
        ),
        grid_profile_id="grid-v1",
        grid_profile_hash=PROFILE_HASHES["grid_profile_hash"],
        vedha_profile_id="vedha-v1",
        vedha_profile_hash=PROFILE_HASHES["vedha_profile_hash"],
        guidance_model_id="guidance-v1",
        source_ids=("SOURCE-A", "SOURCE-B"),
        guidance_available=guidance_available,
        contributions=contributions,
        missing_evidence_ids=missing_evidence_ids,
    )


def test_compiler_sorts_boundaries_and_builds_half_open_intervals() -> None:
    boundaries = (
        _boundary("third", START + timedelta(hours=3)),
        _boundary("first", START),
        _boundary("second", START + timedelta(hours=1)),
    )
    series = SbcAtomicIntervalCompiler().compile(
        boundaries,
        terminal_end_utc=START + timedelta(hours=5),
    )

    assert series.contract == ATOMIC_INTERVAL_CONTRACT
    assert series.interval_policy == ATOMIC_INTERVAL_POLICY
    assert series.classification == RESEARCH_CLASSIFICATION
    assert [item.start_utc for item in series.intervals] == [
        START,
        START + timedelta(hours=1),
        START + timedelta(hours=3),
    ]
    assert [item.end_utc for item in series.intervals] == [
        START + timedelta(hours=1),
        START + timedelta(hours=3),
        START + timedelta(hours=5),
    ]
    assert all(
        left.end_utc == right.start_utc
        for left, right in zip(series.intervals, series.intervals[1:])
    )
    assert all(item.start_utc < item.end_utc for item in series.intervals)


def test_ledger_keeps_gross_net_unknown_count_and_unknown_magnitude_separate() -> None:
    boundary = _boundary(
        "mixed",
        START,
        contributions=(
            _contribution("positive", 2.0),
            _contribution("negative", -1.0),
            _contribution("unknown", None),
        ),
        missing_evidence_ids=("MISSING:ASSOCIATION",),
    )
    series = SbcAtomicIntervalCompiler().compile(
        (boundary,),
        terminal_end_utc=START + timedelta(hours=1),
    )
    ledger = series.intervals[0].ledger

    assert ledger.favorable_guidance_units == 2.0
    assert ledger.adverse_guidance_units == -1.0
    assert ledger.net_guidance_units == 1.0
    assert ledger.gross_activation_units == 3.0
    assert ledger.scored_contribution_count == 2
    assert ledger.unknown_contribution_count == 2
    assert ledger.missing_evidence_count == 1
    assert ledger.total_evidence_count == 4
    assert ledger.unknown_magnitude_units is None
    assert ledger.scoring_coverage_ratio == 0.5


def test_fully_known_and_empty_known_ledgers_do_not_invent_unknown_magnitude() -> None:
    scored = _boundary(
        "scored",
        START,
        contributions=(_contribution("known", 1.0),),
    )
    empty = _boundary("empty", START + timedelta(hours=1))
    series = SbcAtomicIntervalCompiler().compile(
        (scored, empty),
        terminal_end_utc=START + timedelta(hours=2),
    )

    assert series.intervals[0].ledger.unknown_contribution_count == 0
    assert series.intervals[0].ledger.unknown_magnitude_units == 0.0
    assert series.intervals[1].ledger.total_evidence_count == 0
    assert series.intervals[1].ledger.scoring_coverage_ratio == 0.0
    assert series.intervals[1].ledger.unknown_magnitude_units == 0.0


def test_unavailable_guidance_remains_explicit_unknown_evidence() -> None:
    boundary = _boundary(
        "unavailable",
        START,
        guidance_available=False,
        missing_evidence_ids=("VEDHA_GUIDANCE_NOT_AVAILABLE",),
    )
    interval = SbcAtomicIntervalCompiler().compile(
        (boundary,),
        terminal_end_utc=START + timedelta(hours=1),
    ).intervals[0]

    assert interval.guidance_available is False
    assert interval.ledger.scored_contribution_count == 0
    assert interval.ledger.unknown_contribution_count == 1
    assert interval.ledger.unknown_magnitude_units is None
    assert interval.ledger.scoring_coverage_ratio == 0.0


def test_boundary_rejects_lookahead_and_unexplained_missing_guidance() -> None:
    with pytest.raises(ValueError, match="cutoff"):
        _boundary(
            "lookahead",
            START,
            cutoff=START + timedelta(seconds=1),
        )

    with pytest.raises(ValueError, match="missing_evidence_id"):
        _boundary("missing", START, guidance_available=False)


def test_contribution_rejects_numeric_unknown_status_and_missing_citation() -> None:
    numeric = _contribution("numeric", 1.0)
    revised_explanation = replace(numeric, explanation="revised fixture explanation")
    assert revised_explanation.contribution_id != numeric.contribution_id

    with pytest.raises(ValueError, match="status SCORED"):
        replace(numeric, status="UNRESOLVED_PLANET_NATURE")

    with pytest.raises(ValueError, match="at least one"):
        replace(numeric, citation_source_ids=())


def test_compiler_rejects_duplicate_starts_invalid_terminal_and_profile_mixing() -> None:
    first = _boundary("first", START)
    same_start = _boundary("same-start", START)
    with pytest.raises(ValueError, match="timestamps must be unique"):
        SbcAtomicIntervalCompiler().compile(
            (first, same_start),
            terminal_end_utc=START + timedelta(hours=1),
        )

    with pytest.raises(ValueError, match="precede terminal"):
        SbcAtomicIntervalCompiler().compile(
            (first,),
            terminal_end_utc=START,
        )

    changed_profile = _boundary(
        "changed-profile",
        START + timedelta(hours=1),
        foundation_profile_hash=_digest("another-foundation"),
    )
    with pytest.raises(ValueError, match="mix source profile"):
        SbcAtomicIntervalCompiler().compile(
            (first, changed_profile),
            terminal_end_utc=START + timedelta(hours=2),
        )


def test_serialization_and_replay_are_canonical_and_order_independent() -> None:
    first = _boundary(
        "first",
        START,
        contributions=(_contribution("first", 1.0),),
    )
    second = _boundary(
        "second",
        START + timedelta(hours=1),
        contributions=(_contribution("second", -2.0),),
    )
    compiler = SbcAtomicIntervalCompiler()
    ordered = compiler.compile(
        (first, second),
        terminal_end_utc=START + timedelta(hours=2),
    )
    reversed_input = compiler.compile(
        (second, first),
        terminal_end_utc=START + timedelta(hours=2),
    )

    assert ordered.series_id == reversed_input.series_id
    assert ordered.to_dict() == reversed_input.to_dict()
    encoded = json.dumps(ordered.to_dict(), sort_keys=True)
    assert json.loads(encoded) == ordered.to_dict()
    assert len({item.interval_id for item in ordered.intervals}) == 2


def test_chakra_snapshot_factory_preserves_profiles_lineage_and_missing_actor() -> None:
    location = GeoLocation(
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
        altitude_m=216.0,
    )
    snapshot = ChakraLabEngine().snapshot(
        ChakraLabRequest(
            at=datetime(2026, 7, 17, 6, 30, tzinfo=timezone.utc),
            location=location,
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

    assert boundary.foundation_profile_hash == snapshot.foundation_snapshot.profile_hash
    assert boundary.grid_profile_hash == snapshot.grid.profile_hash
    assert boundary.guidance_available is True
    assert "ACTOR:JUPITER:MOTION_REQUIRED" in boundary.missing_evidence_ids
    assert len({item.source_lineage_id for item in boundary.contributions}) == len(
        boundary.contributions
    )
    assert all(item.citation_source_ids for item in boundary.contributions)


def test_chakra_snapshot_factory_rejects_weakened_guardrails() -> None:
    location = GeoLocation(
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )
    snapshot = ChakraLabEngine().snapshot(
        ChakraLabRequest(
            at=datetime(2026, 7, 17, 6, 30, tzinfo=timezone.utc),
            location=location,
            bodies=("SUN", "MOON"),
            actors=(ChakraLabActorSelection("SUN"),),
        )
    )
    weakened = replace(
        snapshot,
        guardrails=replace(ChakraLabGuardrails(), execution_allowed=True),
    )

    with pytest.raises(ValueError, match="guardrails"):
        boundary_from_chakra_snapshot(
            weakened,
            boundary_reason="fixture weakened snapshot",
        )


def test_chakra_snapshot_without_guidance_requires_explicit_profile_lineage() -> None:
    location = GeoLocation(
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )
    snapshot = ChakraLabEngine().snapshot(
        ChakraLabRequest(
            at=datetime(2026, 7, 17, 6, 30, tzinfo=timezone.utc),
            location=location,
            bodies=("SUN", "MOON"),
            actors=(),
        )
    )
    assert snapshot.guidance is None
    with pytest.raises(ValueError, match="unavailable_vedha_profile_id"):
        boundary_from_chakra_snapshot(
            snapshot,
            boundary_reason="fixture unavailable guidance",
        )

    profile = load_vedha_profile("phaladeepika_editor_vedha_guidance_v1")
    boundary = boundary_from_chakra_snapshot(
        snapshot,
        boundary_reason="fixture unavailable guidance",
        unavailable_vedha_profile_id=profile.vedha_profile_id,
        unavailable_vedha_profile_hash=profile.profile_hash,
        unavailable_guidance_model_id=GUIDANCE_MODEL_ID,
    )
    assert boundary.guidance_available is False
    assert boundary.contributions == ()
    assert boundary.missing_evidence_ids == ("VEDHA_GUIDANCE_NOT_AVAILABLE",)
