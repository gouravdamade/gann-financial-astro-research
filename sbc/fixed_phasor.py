from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from .atomic_intervals import RESEARCH_CLASSIFICATION
from .models import to_primitive
from .multidimensional_ledger import (
    CONTRIBUTION_EVIDENCE,
    MISSING_EVIDENCE,
    MULTIDIMENSIONAL_LEDGER_CONTRACT,
    MULTIDIMENSIONAL_LEDGER_SCHEMA_VERSION,
    VISUALIZATION_ONLY_ROLE,
    SbcCausalCluster,
    SbcMultidimensionalLedgerSeries,
)


FIXED_PHASOR_CONTRACT = "SBC_FIXED_ZERO_PI_PHASOR_SERIES_V1"
FIXED_PHASOR_SCHEMA_VERSION = 1
FIXED_PHASOR_POLICY = "FIXED_ZERO_PI_SCALAR_PARITY_VISUALIZATION_ONLY_V1"
FIXED_PHASOR_VECTOR_CONTRACT = "SBC_FIXED_ZERO_PI_PHASOR_VECTOR_V1"
FIXED_PHASOR_INTERVAL_CONTRACT = "SBC_FIXED_ZERO_PI_PHASOR_INTERVAL_V1"

PLOTTED = "PLOTTED"
UNKNOWN_NOT_PLOTTED = "UNKNOWN_NOT_PLOTTED"
ZERO_ANGLE = "ZERO"
PI_ANGLE = "PI"
PASS = "PASS"
UNKNOWN = "UNKNOWN"


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _required_text(value: Any, label: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{label} is required")
    return normalized


def _optional_text(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, label)


def _sha256(value: Any, label: str) -> str:
    normalized = _required_text(value, label).upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"{label} must be an uppercase SHA-256 digest")
    return normalized


def _utc(value: datetime, label: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(f"{label} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _finite_or_none(value: float | None, label: str) -> float | None:
    if value is None:
        return None
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{label} must be finite")
    return 0.0 if normalized == 0.0 else normalized


def _float_equal(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-12)


@dataclass(frozen=True)
class SbcFixedPhasorFieldRole:
    field_path: str
    derivation_role: str = VISUALIZATION_ONLY_ROLE
    evidence_bearing: bool = False
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "field_path",
            _required_text(self.field_path, "field_path"),
        )
        if self.derivation_role != VISUALIZATION_ONLY_ROLE:
            raise ValueError("fixed phasor fields must be VISUALIZATION_ONLY")
        if self.evidence_bearing:
            raise ValueError("fixed phasor fields cannot become new evidence")
        if self.counts_as_independent_vote:
            raise ValueError("fixed phasor fields cannot count as votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("fixed phasor fields cannot contribute market direction")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcFixedPhasorVector:
    interval_id: str
    cluster_id: str
    source_lineage_id: str
    evidence_kind: str
    source_evidence_id: str
    actor_identity: str | None
    target_layer: str | None
    target_value: str | None
    signed_guidance_units: float | None
    source_status: str
    unknown_reason: str | None
    derivation_role: str = VISUALIZATION_ONLY_ROLE
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0
    projection_status: str = field(init=False)
    magnitude_units: float | None = field(init=False)
    fixed_angle: str | None = field(init=False)
    fixed_angle_radians: float | None = field(init=False)
    real_component_units: float | None = field(init=False)
    imaginary_component_units: float | None = field(init=False)
    vector_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "interval_id", _sha256(self.interval_id, "interval_id")
        )
        object.__setattr__(self, "cluster_id", _sha256(self.cluster_id, "cluster_id"))
        object.__setattr__(
            self,
            "source_lineage_id",
            _sha256(self.source_lineage_id, "source_lineage_id"),
        )
        evidence_kind = _required_text(self.evidence_kind, "evidence_kind")
        if evidence_kind not in (CONTRIBUTION_EVIDENCE, MISSING_EVIDENCE):
            raise ValueError(f"unknown evidence_kind: {evidence_kind}")
        object.__setattr__(self, "evidence_kind", evidence_kind)
        object.__setattr__(
            self,
            "source_evidence_id",
            _required_text(self.source_evidence_id, "source_evidence_id"),
        )
        object.__setattr__(
            self,
            "actor_identity",
            _optional_text(self.actor_identity, "actor_identity"),
        )
        object.__setattr__(
            self,
            "target_layer",
            _optional_text(self.target_layer, "target_layer"),
        )
        object.__setattr__(
            self,
            "target_value",
            _optional_text(self.target_value, "target_value"),
        )
        object.__setattr__(
            self,
            "source_status",
            _required_text(self.source_status, "source_status"),
        )
        if self.derivation_role != VISUALIZATION_ONLY_ROLE:
            raise ValueError("fixed phasor vectors must be VISUALIZATION_ONLY")
        if self.counts_as_independent_vote:
            raise ValueError("fixed phasor vectors cannot count as votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("fixed phasor vectors cannot contribute market direction")

        signed = _finite_or_none(self.signed_guidance_units, "signed_guidance_units")
        object.__setattr__(self, "signed_guidance_units", signed)
        if signed is None:
            object.__setattr__(self, "projection_status", UNKNOWN_NOT_PLOTTED)
            object.__setattr__(self, "magnitude_units", None)
            object.__setattr__(self, "fixed_angle", None)
            object.__setattr__(self, "fixed_angle_radians", None)
            object.__setattr__(self, "real_component_units", None)
            object.__setattr__(self, "imaginary_component_units", None)
            object.__setattr__(
                self,
                "unknown_reason",
                _required_text(self.unknown_reason, "unknown_reason"),
            )
        else:
            object.__setattr__(self, "projection_status", PLOTTED)
            object.__setattr__(self, "magnitude_units", abs(signed))
            object.__setattr__(
                self,
                "fixed_angle",
                ZERO_ANGLE if signed >= 0.0 else PI_ANGLE,
            )
            object.__setattr__(
                self,
                "fixed_angle_radians",
                0.0 if signed >= 0.0 else math.pi,
            )
            object.__setattr__(self, "real_component_units", signed)
            object.__setattr__(self, "imaginary_component_units", 0.0)
            if self.unknown_reason is not None:
                raise ValueError("plotted fixed phasors cannot carry unknown_reason")

        identity = {
            "contract": FIXED_PHASOR_VECTOR_CONTRACT,
            "projection_policy": FIXED_PHASOR_POLICY,
            "interval_id": self.interval_id,
            "cluster_id": self.cluster_id,
            "source_lineage_id": self.source_lineage_id,
            "source_evidence_id": self.source_evidence_id,
            "signed_guidance_units": self.signed_guidance_units,
            "source_status": self.source_status,
            "projection_status": self.projection_status,
            "magnitude_units": self.magnitude_units,
            "fixed_angle": self.fixed_angle,
            "fixed_angle_radians": self.fixed_angle_radians,
            "real_component_units": self.real_component_units,
            "imaginary_component_units": self.imaginary_component_units,
            "derivation_role": self.derivation_role,
        }
        object.__setattr__(self, "vector_id", _canonical_hash(identity))

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcFixedPhasorIntervalProjection:
    interval_id: str
    interval_ledger_id: str
    start_utc: datetime
    end_utc: datetime
    evidence_cutoff_utc: datetime
    vectors: tuple[SbcFixedPhasorVector, ...]
    source_favorable_units: float
    source_adverse_units: float
    source_net_units: float
    source_gross_activation_units: float
    vector_real_sum_units: float
    vector_imaginary_sum_units: float
    vector_magnitude_sum_units: float
    known_scored_coherence_ratio: float
    plotted_vector_count: int
    unknown_vector_count: int
    missing_evidence_count: int
    real_matches_net: bool
    magnitude_matches_gross: bool
    imaginary_is_zero: bool
    counts_match: bool
    unknowns_preserved: bool
    reconciled: bool
    projection_id: str

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcFixedPhasorValidationGate:
    gate_id: str
    state: str
    label: str
    detail: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "gate_id", _required_text(self.gate_id, "gate_id"))
        state = _required_text(self.state, "state")
        if state not in (PASS, UNKNOWN):
            raise ValueError(f"unknown fixed phasor validation state: {state}")
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "detail", _required_text(self.detail, "detail"))

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcFixedPhasorGuardrails:
    research_only: bool = True
    read_only: bool = True
    timestamp_safe: bool = True
    no_lookahead: bool = True
    source_profiled_experimental: bool = True
    scalar_equivalent_only: bool = True
    fixed_zero_pi_only: bool = True
    visualization_only: bool = True
    physical_wave_claimed: bool = False
    timing_phase_included: bool = False
    timing_sector_profile_included: bool = False
    fx_subtraction_included: bool = False
    confidence_included: bool = False
    financially_validated: bool = False
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0
    execution_allowed: bool = False
    blocked_capabilities: tuple[str, ...] = (
        "PHYSICAL_WAVE_INTERPRETATION",
        "TIMING_PHASE_OUTPUT",
        "TIMING_SECTOR_DIRECTION",
        "FX_SUBTRACTION",
        "CONFIDENCE_OUTPUT",
        "MARKET_DIRECTION",
        "AUTO_SUGGEST",
        "LIVE_INFERENCE",
        "OFFICIAL_ML_NOTES",
        "SHADOW_VALIDATION_VOTE",
        "TRADE_OUTPUT",
        "MT5_EXECUTION",
    )


@dataclass(frozen=True)
class SbcFixedPhasorSeries:
    contract: str
    schema_version: int
    projection_policy: str
    classification: str
    projection_series_id: str
    source_ledger_id: str
    source_atomic_series_id: str
    instrument_identity: str
    range_start_utc: datetime
    range_end_utc: datetime
    source_ids: tuple[str, ...]
    field_roles: tuple[SbcFixedPhasorFieldRole, ...]
    intervals: tuple[SbcFixedPhasorIntervalProjection, ...]
    validation_gates: tuple[SbcFixedPhasorValidationGate, ...]
    guardrails: SbcFixedPhasorGuardrails

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


def _validate_source(series: SbcMultidimensionalLedgerSeries) -> None:
    if not isinstance(series, SbcMultidimensionalLedgerSeries):
        raise ValueError("series must be SbcMultidimensionalLedgerSeries")
    if series.contract != MULTIDIMENSIONAL_LEDGER_CONTRACT:
        raise ValueError("F3 requires the canonical P2 ledger contract")
    if series.schema_version != MULTIDIMENSIONAL_LEDGER_SCHEMA_VERSION:
        raise ValueError("F3 requires the canonical P2 schema version")
    if series.classification != RESEARCH_CLASSIFICATION:
        raise ValueError("F3 requires SOURCE_PROFILED_EXPERIMENTAL input")
    _sha256(series.ledger_id, "ledger_id")
    _sha256(series.source_atomic_series_id, "source_atomic_series_id")
    guardrails = series.guardrails
    if not (
        guardrails.research_only
        and guardrails.timestamp_safe
        and guardrails.no_lookahead
        and guardrails.source_profiled_experimental
        and not guardrails.counts_as_independent_vote
        and float(guardrails.directional_contribution) == 0.0
        and not guardrails.fx_subtraction_included
        and not guardrails.phase_included
        and not guardrails.confidence_included
        and not guardrails.execution_allowed
    ):
        raise ValueError("P2 ledger weakens required F3 guardrails")


def _source_evidence_id(cluster: SbcCausalCluster) -> str:
    if cluster.evidence_kind == CONTRIBUTION_EVIDENCE:
        return _sha256(cluster.contribution_id, "contribution_id")
    return _required_text(cluster.missing_evidence_id, "missing_evidence_id")


def _vector(cluster: SbcCausalCluster) -> SbcFixedPhasorVector:
    return SbcFixedPhasorVector(
        interval_id=cluster.interval_id,
        cluster_id=cluster.cluster_id,
        source_lineage_id=cluster.source_lineage_id,
        evidence_kind=cluster.evidence_kind,
        source_evidence_id=_source_evidence_id(cluster),
        actor_identity=cluster.actor_identity,
        target_layer=cluster.target_layer,
        target_value=cluster.target_value,
        signed_guidance_units=cluster.signed_guidance_units,
        source_status=cluster.status,
        unknown_reason=cluster.unknown_reason,
    )


def _validate_interval_source(
    vectors: tuple[SbcFixedPhasorVector, ...],
    interval: Any,
) -> None:
    summary = interval.total_summary
    plotted = tuple(item for item in vectors if item.projection_status == PLOTTED)
    unknown = tuple(
        item for item in vectors if item.projection_status == UNKNOWN_NOT_PLOTTED
    )
    signed = tuple(float(item.real_component_units) for item in plotted)
    favorable = math.fsum(value for value in signed if value > 0.0)
    adverse = math.fsum(value for value in signed if value < 0.0)
    missing_count = sum(item.evidence_kind == MISSING_EVIDENCE for item in unknown)
    checks = (
        _float_equal(favorable, summary.favorable_guidance_units),
        _float_equal(adverse, summary.adverse_guidance_units),
        _float_equal(math.fsum(signed), summary.net_guidance_units),
        _float_equal(
            math.fsum(abs(value) for value in signed),
            summary.gross_activation_units,
        ),
        len(plotted) == summary.scored_contribution_count,
        len(unknown) == summary.unknown_contribution_count,
        missing_count == summary.missing_evidence_count,
        len(vectors) == summary.total_evidence_count,
        summary.unknown_magnitude_units is None
        if unknown
        else summary.unknown_magnitude_units == 0.0,
    )
    if not all(checks):
        raise ValueError(
            f"F3 source cluster totals differ from P2 interval {interval.interval_id}"
        )


def _interval_projection(interval: Any) -> SbcFixedPhasorIntervalProjection:
    vectors = tuple(
        sorted(
            (_vector(cluster) for cluster in interval.causal_clusters),
            key=lambda item: item.cluster_id,
        )
    )
    if len(vectors) != len({item.cluster_id for item in vectors}):
        raise ValueError("F3 interval cluster identities must be unique")
    _validate_interval_source(vectors, interval)

    plotted = tuple(item for item in vectors if item.projection_status == PLOTTED)
    unknown = tuple(
        item for item in vectors if item.projection_status == UNKNOWN_NOT_PLOTTED
    )
    real_sum = math.fsum(float(item.real_component_units) for item in plotted)
    imaginary_sum = math.fsum(float(item.imaginary_component_units) for item in plotted)
    magnitude_sum = math.fsum(float(item.magnitude_units) for item in plotted)
    summary = interval.total_summary
    real_matches = _float_equal(real_sum, summary.net_guidance_units)
    magnitude_matches = _float_equal(
        magnitude_sum,
        summary.gross_activation_units,
    )
    imaginary_is_zero = _float_equal(imaginary_sum, 0.0)
    counts_match = (
        len(plotted) == summary.scored_contribution_count
        and len(unknown) == summary.unknown_contribution_count
        and len(vectors) == summary.total_evidence_count
    )
    unknowns_preserved = all(
        item.magnitude_units is None
        and item.fixed_angle is None
        and item.real_component_units is None
        and item.imaginary_component_units is None
        for item in unknown
    )
    reconciled = all(
        (
            real_matches,
            magnitude_matches,
            imaginary_is_zero,
            counts_match,
            unknowns_preserved,
        )
    )
    if not reconciled:
        raise ValueError(f"F3 scalar parity failed for interval {interval.interval_id}")
    gross = float(summary.gross_activation_units)
    coherence = abs(real_sum) / gross if gross > 0.0 else 0.0
    identity = {
        "contract": FIXED_PHASOR_INTERVAL_CONTRACT,
        "projection_policy": FIXED_PHASOR_POLICY,
        "interval_id": interval.interval_id,
        "interval_ledger_id": interval.interval_ledger_id,
        "vectors": tuple(item.vector_id for item in vectors),
        "source_summary": summary.to_dict(),
        "vector_real_sum_units": real_sum,
        "vector_imaginary_sum_units": imaginary_sum,
        "vector_magnitude_sum_units": magnitude_sum,
        "known_scored_coherence_ratio": coherence,
        "reconciled": reconciled,
    }
    return SbcFixedPhasorIntervalProjection(
        interval_id=interval.interval_id,
        interval_ledger_id=interval.interval_ledger_id,
        start_utc=interval.start_utc,
        end_utc=interval.end_utc,
        evidence_cutoff_utc=interval.evidence_cutoff_utc,
        vectors=vectors,
        source_favorable_units=summary.favorable_guidance_units,
        source_adverse_units=summary.adverse_guidance_units,
        source_net_units=summary.net_guidance_units,
        source_gross_activation_units=summary.gross_activation_units,
        vector_real_sum_units=real_sum,
        vector_imaginary_sum_units=imaginary_sum,
        vector_magnitude_sum_units=magnitude_sum,
        known_scored_coherence_ratio=coherence,
        plotted_vector_count=len(plotted),
        unknown_vector_count=len(unknown),
        missing_evidence_count=summary.missing_evidence_count,
        real_matches_net=real_matches,
        magnitude_matches_gross=magnitude_matches,
        imaginary_is_zero=imaginary_is_zero,
        counts_match=counts_match,
        unknowns_preserved=unknowns_preserved,
        reconciled=reconciled,
        projection_id=_canonical_hash(identity),
    )


def _field_roles() -> tuple[SbcFixedPhasorFieldRole, ...]:
    return (
        SbcFixedPhasorFieldRole("intervals[].vectors[]"),
        SbcFixedPhasorFieldRole("intervals[].vector_real_sum_units"),
        SbcFixedPhasorFieldRole("intervals[].vector_imaginary_sum_units"),
        SbcFixedPhasorFieldRole("intervals[].vector_magnitude_sum_units"),
        SbcFixedPhasorFieldRole("intervals[].known_scored_coherence_ratio"),
        SbcFixedPhasorFieldRole("intervals[].reconciled"),
    )


def _validation_gates(
    intervals: Iterable[SbcFixedPhasorIntervalProjection],
) -> tuple[SbcFixedPhasorValidationGate, ...]:
    ordered = tuple(intervals)
    unknown_count = sum(item.unknown_vector_count for item in ordered)
    return (
        SbcFixedPhasorValidationGate(
            "P2_SOURCE_RECONCILIATION",
            PASS,
            "P2 source reconciliation",
            "Every source interval entered F3 with all P2 axes reconciled.",
        ),
        SbcFixedPhasorValidationGate(
            "SCALAR_NET_PARITY",
            PASS,
            "Real-axis scalar parity",
            "The sum of fixed phasor real components exactly reproduces P2 net units.",
        ),
        SbcFixedPhasorValidationGate(
            "TRUE_GROSS_PARITY",
            PASS,
            "Magnitude scalar parity",
            "The sum of fixed phasor magnitudes exactly reproduces P2 true gross activation.",
        ),
        SbcFixedPhasorValidationGate(
            "FIXED_ANGLE_DOMAIN",
            PASS,
            "Fixed 0/pi domain",
            "Every plotted value uses only 0 or pi; no timing angle is inferred.",
        ),
        SbcFixedPhasorValidationGate(
            "UNKNOWN_EVIDENCE",
            UNKNOWN if unknown_count else PASS,
            "Unknown evidence preservation",
            (
                f"{unknown_count} unknown contribution(s) remain unplotted with null magnitude."
                if unknown_count
                else "No unknown contribution is present in this captured range."
            ),
        ),
        SbcFixedPhasorValidationGate(
            "TIMING_PHASE_LOCK",
            PASS,
            "Timing-phase lock",
            "No sector, loop, station, resonance, or market-direction phase is included.",
        ),
        SbcFixedPhasorValidationGate(
            "FINANCIAL_VALIDATION",
            UNKNOWN,
            "Financial validation",
            "No immutable prospective financial validation package is attached.",
        ),
        SbcFixedPhasorValidationGate(
            "EXECUTION_LOCK",
            PASS,
            "Execution lock",
            "Voting, market direction, trade output, and MT5 execution remain blocked.",
        ),
    )


class SbcFixedPhasorCompiler:
    def compile(
        self,
        series: SbcMultidimensionalLedgerSeries,
    ) -> SbcFixedPhasorSeries:
        _validate_source(series)
        ordered = tuple(
            sorted(series.interval_ledgers, key=lambda item: item.start_utc)
        )
        if not ordered:
            raise ValueError("F3 requires at least one P2 interval ledger")
        if ordered[0].start_utc != series.range_start_utc:
            raise ValueError("F3 source range does not begin with its first interval")
        if ordered[-1].end_utc != series.range_end_utc:
            raise ValueError("F3 source range does not end with its final interval")

        all_cluster_ids: set[str] = set()
        for index, interval in enumerate(ordered):
            _sha256(interval.interval_id, "interval_id")
            _sha256(interval.interval_ledger_id, "interval_ledger_id")
            if index and ordered[index - 1].end_utc != interval.start_utc:
                raise ValueError("F3 source intervals must remain contiguous")
            if not all(item.reconciled for item in interval.axis_reconciliations):
                raise ValueError("F3 source contains an unreconciled P2 axis")
            for cluster in interval.causal_clusters:
                if cluster.interval_id != interval.interval_id:
                    raise ValueError("F3 cluster links to the wrong interval")
                if (
                    cluster.interval_start_utc != interval.start_utc
                    or cluster.interval_end_utc != interval.end_utc
                    or cluster.evidence_cutoff_utc != interval.evidence_cutoff_utc
                ):
                    raise ValueError("F3 cluster interval metadata differs from P2")
            cluster_ids = {
                _sha256(item.cluster_id, "cluster_id")
                for item in interval.causal_clusters
            }
            if all_cluster_ids & cluster_ids:
                raise ValueError(
                    "F3 cluster identities must be unique across intervals"
                )
            all_cluster_ids.update(cluster_ids)

        intervals = tuple(_interval_projection(item) for item in ordered)
        if not all(item.reconciled for item in intervals):
            raise ValueError("F3 cannot publish an unreconciled interval")
        field_roles = _field_roles()
        validation_gates = _validation_gates(intervals)
        guardrails = SbcFixedPhasorGuardrails()
        identity = {
            "contract": FIXED_PHASOR_CONTRACT,
            "schema_version": FIXED_PHASOR_SCHEMA_VERSION,
            "projection_policy": FIXED_PHASOR_POLICY,
            "classification": RESEARCH_CLASSIFICATION,
            "source_ledger_id": series.ledger_id,
            "source_atomic_series_id": series.source_atomic_series_id,
            "instrument_identity": series.instrument_identity,
            "range_start_utc": series.range_start_utc.isoformat(),
            "range_end_utc": series.range_end_utc.isoformat(),
            "source_ids": series.source_ids,
            "field_roles": to_primitive(field_roles),
            "interval_projection_ids": tuple(item.projection_id for item in intervals),
            "validation_gates": to_primitive(validation_gates),
            "guardrails": to_primitive(guardrails),
        }
        return SbcFixedPhasorSeries(
            contract=FIXED_PHASOR_CONTRACT,
            schema_version=FIXED_PHASOR_SCHEMA_VERSION,
            projection_policy=FIXED_PHASOR_POLICY,
            classification=RESEARCH_CLASSIFICATION,
            projection_series_id=_canonical_hash(identity),
            source_ledger_id=series.ledger_id,
            source_atomic_series_id=series.source_atomic_series_id,
            instrument_identity=series.instrument_identity,
            range_start_utc=series.range_start_utc,
            range_end_utc=series.range_end_utc,
            source_ids=series.source_ids,
            field_roles=field_roles,
            intervals=intervals,
            validation_gates=validation_gates,
            guardrails=guardrails,
        )
