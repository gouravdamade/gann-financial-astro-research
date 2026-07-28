from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from .atomic_intervals import (
    ATOMIC_INTERVAL_CONTRACT,
    ATOMIC_INTERVAL_POLICY,
    ATOMIC_INTERVAL_SCHEMA_VERSION,
    RESEARCH_CLASSIFICATION,
    SbcAtomicContribution,
    SbcAtomicInterval,
    SbcAtomicIntervalSeries,
    SbcAtomicLedgerSummary,
    SbcAtomicProfileIdentity,
)
from .models import to_primitive


MULTIDIMENSIONAL_LEDGER_CONTRACT = "SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1"
MULTIDIMENSIONAL_LEDGER_SCHEMA_VERSION = 1
CAUSAL_CLUSTER_CONTRACT = "SBC_CAUSAL_CLUSTER_V1"
DIMENSION_CELL_CONTRACT = "SBC_LEDGER_DIMENSION_CELL_V1"
MISSING_EVIDENCE_LINEAGE_CONTRACT = "SBC_MISSING_EVIDENCE_LINEAGE_V1"

PRIMARY_EVIDENCE_ROLE = "PRIMARY_EVIDENCE"
DERIVED_AXIS_ROLE = "DERIVED_AXIS"
VISUALIZATION_ONLY_ROLE = "VISUALIZATION_ONLY"
NON_VOTING_CONTEXT_ROLE = "NON_VOTING_CONTEXT"
DERIVATION_ROLES = (
    PRIMARY_EVIDENCE_ROLE,
    DERIVED_AXIS_ROLE,
    VISUALIZATION_ONLY_ROLE,
    NON_VOTING_CONTEXT_ROLE,
)

TOTAL_AXIS = "TOTAL"
ACTOR_AXIS = "ACTOR"
TARGET_LAYER_AXIS = "TARGET_LAYER"
NATURE_AXIS = "NATURE"
VEDHA_DIRECTION_AXIS = "VEDHA_DIRECTION"
SOURCE_LINEAGE_AXIS = "SOURCE_LINEAGE"
LEDGER_AXES = (
    TOTAL_AXIS,
    ACTOR_AXIS,
    TARGET_LAYER_AXIS,
    NATURE_AXIS,
    VEDHA_DIRECTION_AXIS,
    SOURCE_LINEAGE_AXIS,
)

CONTRIBUTION_EVIDENCE = "CONTRIBUTION"
MISSING_EVIDENCE = "MISSING_EVIDENCE"
UNAVAILABLE_DIMENSION_KEY = "UNAVAILABLE"
TOTAL_DIMENSION_KEY = "ALL"


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
    if not re.fullmatch(r"[0-9A-F]{64}", normalized):
        raise ValueError(f"{label} must be an uppercase SHA-256 digest")
    return normalized


def _utc(value: datetime, label: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _finite_or_none(value: float | None, label: str) -> float | None:
    if value is None:
        return None
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{label} must be finite")
    return normalized


def _unique_sorted(
    values: Iterable[str],
    label: str,
    *,
    required: bool = False,
) -> tuple[str, ...]:
    normalized = tuple(_required_text(item, label) for item in values)
    if required and not normalized:
        raise ValueError(f"{label} requires at least one value")
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} values must be unique")
    return tuple(sorted(normalized))


def _float_equal(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-12)


@dataclass(frozen=True)
class SbcLedgerFieldRole:
    field_path: str
    derivation_role: str
    evidence_bearing: bool
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "field_path",
            _required_text(self.field_path, "field_path"),
        )
        role = _required_text(self.derivation_role, "derivation_role")
        if role not in DERIVATION_ROLES:
            raise ValueError(f"unknown derivation_role: {role}")
        object.__setattr__(self, "derivation_role", role)
        if not isinstance(self.evidence_bearing, bool):
            raise ValueError("evidence_bearing must be boolean")
        if self.counts_as_independent_vote:
            raise ValueError("P2 ledger fields cannot count as independent votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("P2 ledger fields cannot contribute market direction")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcCausalCluster:
    instrument_identity: str
    interval_id: str
    interval_start_utc: datetime
    interval_end_utc: datetime
    evidence_cutoff_utc: datetime
    snapshot_id: str
    profile_identity: SbcAtomicProfileIdentity
    source_ids: tuple[str, ...]
    evidence_kind: str
    derivation_role: str
    source_lineage_id: str
    contribution_id: str | None
    missing_evidence_id: str | None
    actor_identity: str | None
    source_nakshatra: str | None
    vedha_direction: str | None
    target_row: int | None
    target_column: int | None
    target_layer: str | None
    target_value: str | None
    target_witness_set_id: str | None
    target_evidence_status: str | None
    nature: str | None
    effective_multiplier: float | None
    signed_guidance_units: float | None
    status: str
    unknown_reason: str | None
    citation_source_ids: tuple[str, ...]
    cluster_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "instrument_identity",
            _required_text(self.instrument_identity, "instrument_identity"),
        )
        object.__setattr__(self, "interval_id", _sha256(self.interval_id, "interval_id"))
        start = _utc(self.interval_start_utc, "interval_start_utc")
        end = _utc(self.interval_end_utc, "interval_end_utc")
        cutoff = _utc(self.evidence_cutoff_utc, "evidence_cutoff_utc")
        if start >= end:
            raise ValueError("causal-cluster interval must have positive duration")
        if cutoff > start:
            raise ValueError("causal-cluster evidence cutoff cannot exceed interval start")
        object.__setattr__(self, "interval_start_utc", start)
        object.__setattr__(self, "interval_end_utc", end)
        object.__setattr__(self, "evidence_cutoff_utc", cutoff)
        object.__setattr__(self, "snapshot_id", _sha256(self.snapshot_id, "snapshot_id"))
        if not isinstance(self.profile_identity, SbcAtomicProfileIdentity):
            raise ValueError("profile_identity must be SbcAtomicProfileIdentity")
        object.__setattr__(
            self,
            "source_ids",
            _unique_sorted(self.source_ids, "source_ids", required=True),
        )
        evidence_kind = _required_text(self.evidence_kind, "evidence_kind")
        if evidence_kind not in (CONTRIBUTION_EVIDENCE, MISSING_EVIDENCE):
            raise ValueError(f"unknown evidence_kind: {evidence_kind}")
        object.__setattr__(self, "evidence_kind", evidence_kind)
        role = _required_text(self.derivation_role, "derivation_role")
        if role != PRIMARY_EVIDENCE_ROLE:
            raise ValueError("causal clusters must use PRIMARY_EVIDENCE")
        object.__setattr__(self, "derivation_role", role)
        object.__setattr__(
            self,
            "source_lineage_id",
            _sha256(self.source_lineage_id, "source_lineage_id"),
        )
        object.__setattr__(self, "status", _required_text(self.status, "status"))
        object.__setattr__(
            self,
            "effective_multiplier",
            _finite_or_none(self.effective_multiplier, "effective_multiplier"),
        )
        object.__setattr__(
            self,
            "signed_guidance_units",
            _finite_or_none(self.signed_guidance_units, "signed_guidance_units"),
        )

        if evidence_kind == CONTRIBUTION_EVIDENCE:
            object.__setattr__(
                self,
                "contribution_id",
                _sha256(self.contribution_id, "contribution_id"),
            )
            if self.missing_evidence_id is not None:
                raise ValueError("contribution clusters cannot carry missing_evidence_id")
            for field_name in (
                "actor_identity",
                "source_nakshatra",
                "vedha_direction",
                "target_layer",
                "target_value",
                "target_witness_set_id",
                "target_evidence_status",
                "nature",
            ):
                object.__setattr__(
                    self,
                    field_name,
                    _required_text(getattr(self, field_name), field_name),
                )
            if self.target_row is None or self.target_column is None:
                raise ValueError("contribution clusters require target coordinates")
            row = int(self.target_row)
            column = int(self.target_column)
            if row < 0 or column < 0:
                raise ValueError("target coordinates must be non-negative")
            object.__setattr__(self, "target_row", row)
            object.__setattr__(self, "target_column", column)
            object.__setattr__(
                self,
                "citation_source_ids",
                _unique_sorted(
                    self.citation_source_ids,
                    "citation_source_ids",
                    required=True,
                ),
            )
            if self.signed_guidance_units is None:
                if self.status == "SCORED":
                    raise ValueError("SCORED causal clusters require signed units")
                object.__setattr__(
                    self,
                    "unknown_reason",
                    _required_text(self.unknown_reason, "unknown_reason"),
                )
            else:
                if self.status != "SCORED":
                    raise ValueError("numeric causal clusters must use status SCORED")
                if self.unknown_reason is not None:
                    raise ValueError("scored causal clusters cannot carry unknown_reason")
        else:
            if self.contribution_id is not None:
                raise ValueError("missing-evidence clusters cannot carry contribution_id")
            object.__setattr__(
                self,
                "missing_evidence_id",
                _required_text(self.missing_evidence_id, "missing_evidence_id"),
            )
            unavailable_fields = (
                "actor_identity",
                "source_nakshatra",
                "vedha_direction",
                "target_row",
                "target_column",
                "target_layer",
                "target_value",
                "target_witness_set_id",
                "target_evidence_status",
                "nature",
                "effective_multiplier",
                "signed_guidance_units",
            )
            if any(getattr(self, item) is not None for item in unavailable_fields):
                raise ValueError("missing-evidence clusters cannot invent dimension values")
            if self.status != "MISSING_EVIDENCE":
                raise ValueError("missing-evidence clusters require status MISSING_EVIDENCE")
            object.__setattr__(
                self,
                "unknown_reason",
                _required_text(self.unknown_reason, "unknown_reason"),
            )
            object.__setattr__(
                self,
                "citation_source_ids",
                _unique_sorted(self.citation_source_ids, "citation_source_ids"),
            )

        target_identity = (
            {
                "row": self.target_row,
                "column": self.target_column,
                "layer": self.target_layer,
                "value": self.target_value,
                "witness_set_id": self.target_witness_set_id,
                "evidence_status": self.target_evidence_status,
            }
            if evidence_kind == CONTRIBUTION_EVIDENCE
            else None
        )
        identity = {
            "contract": CAUSAL_CLUSTER_CONTRACT,
            "instrument_identity": self.instrument_identity,
            "atomic_interval": {
                "start_utc": self.interval_start_utc.isoformat(),
                "end_utc": self.interval_end_utc.isoformat(),
            },
            "evidence_cutoff_utc": self.evidence_cutoff_utc.isoformat(),
            "snapshot_id": self.snapshot_id,
            "profile_identity": self.profile_identity.to_dict(),
            "source_ids": self.source_ids,
            "evidence_kind": self.evidence_kind,
            "source_lineage_id": self.source_lineage_id,
            "actor_identity": self.actor_identity,
            "source_nakshatra": self.source_nakshatra,
            "target_identity": target_identity,
            "derivation_role": self.derivation_role,
        }
        object.__setattr__(self, "cluster_id", _canonical_hash(identity))

    @property
    def is_scored(self) -> bool:
        return self.signed_guidance_units is not None

    @property
    def is_missing(self) -> bool:
        return self.evidence_kind == MISSING_EVIDENCE

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcLedgerDimensionCell:
    interval_id: str
    axis: str
    key: str
    derivation_role: str
    cluster_ids: tuple[str, ...]
    summary: SbcAtomicLedgerSummary
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0
    cell_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "interval_id", _sha256(self.interval_id, "interval_id"))
        axis = _required_text(self.axis, "axis")
        if axis not in LEDGER_AXES:
            raise ValueError(f"unknown ledger axis: {axis}")
        object.__setattr__(self, "axis", axis)
        object.__setattr__(self, "key", _required_text(self.key, "key"))
        if self.derivation_role != DERIVED_AXIS_ROLE:
            raise ValueError("dimension cells must use DERIVED_AXIS")
        object.__setattr__(
            self,
            "cluster_ids",
            tuple(sorted(_sha256(item, "cluster_id") for item in self.cluster_ids)),
        )
        if len(self.cluster_ids) != len(set(self.cluster_ids)):
            raise ValueError("dimension cell cluster_ids must be unique")
        if not isinstance(self.summary, SbcAtomicLedgerSummary):
            raise ValueError("summary must be SbcAtomicLedgerSummary")
        if self.counts_as_independent_vote:
            raise ValueError("dimension cells cannot count as independent votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("dimension cells cannot contribute market direction")
        identity = {
            "contract": DIMENSION_CELL_CONTRACT,
            "interval_id": self.interval_id,
            "axis": self.axis,
            "key": self.key,
            "derivation_role": self.derivation_role,
            "cluster_ids": self.cluster_ids,
            "summary": self.summary.to_dict(),
        }
        object.__setattr__(self, "cell_id", _canonical_hash(identity))

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcLedgerAxisReconciliation:
    axis: str
    cell_count: int
    cluster_count: int
    every_cluster_exactly_once: bool
    favorable_matches: bool
    adverse_matches: bool
    net_matches: bool
    gross_matches: bool
    scored_count_matches: bool
    unknown_count_matches: bool
    missing_count_matches: bool
    total_count_matches: bool
    reconciled: bool

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcMultidimensionalIntervalLedger:
    interval_id: str
    classification: str
    start_utc: datetime
    end_utc: datetime
    evidence_cutoff_utc: datetime
    causal_clusters: tuple[SbcCausalCluster, ...]
    dimension_cells: tuple[SbcLedgerDimensionCell, ...]
    duplicate_primary_evidence_count: int
    total_summary: SbcAtomicLedgerSummary
    axis_reconciliations: tuple[SbcLedgerAxisReconciliation, ...]
    interval_ledger_id: str

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcMultidimensionalLedgerGuardrails:
    research_only: bool = True
    timestamp_safe: bool = True
    no_lookahead: bool = True
    source_profiled_experimental: bool = True
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0
    fx_subtraction_included: bool = False
    phase_included: bool = False
    confidence_included: bool = False
    execution_allowed: bool = False
    blocked_capabilities: tuple[str, ...] = (
        "FX_SUBTRACTION",
        "PHASE_OUTPUT",
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
class SbcMultidimensionalLedgerSeries:
    contract: str
    schema_version: int
    classification: str
    ledger_id: str
    instrument_identity: str
    source_atomic_series_id: str
    range_start_utc: datetime
    range_end_utc: datetime
    profile_identity: SbcAtomicProfileIdentity
    source_ids: tuple[str, ...]
    field_roles: tuple[SbcLedgerFieldRole, ...]
    interval_ledgers: tuple[SbcMultidimensionalIntervalLedger, ...]
    guardrails: SbcMultidimensionalLedgerGuardrails

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


def _missing_lineage_id(missing_evidence_id: str) -> str:
    identity = {
        "contract": MISSING_EVIDENCE_LINEAGE_CONTRACT,
        "missing_evidence_id": _required_text(
            missing_evidence_id,
            "missing_evidence_id",
        ),
    }
    return _canonical_hash(identity)


def _summary_from_clusters(
    clusters: Iterable[SbcCausalCluster],
) -> SbcAtomicLedgerSummary:
    ordered = tuple(clusters)
    scored = tuple(
        float(item.signed_guidance_units)
        for item in ordered
        if item.signed_guidance_units is not None
    )
    favorable = math.fsum(value for value in scored if value > 0.0)
    adverse = math.fsum(value for value in scored if value < 0.0)
    missing_count = sum(item.is_missing for item in ordered)
    unresolved_count = sum(
        not item.is_scored and not item.is_missing for item in ordered
    )
    unknown_count = missing_count + unresolved_count
    total_count = len(ordered)
    return SbcAtomicLedgerSummary(
        favorable_guidance_units=favorable,
        adverse_guidance_units=adverse,
        net_guidance_units=math.fsum(scored),
        gross_activation_units=math.fsum(abs(value) for value in scored),
        scored_contribution_count=len(scored),
        unknown_contribution_count=unknown_count,
        missing_evidence_count=missing_count,
        total_evidence_count=total_count,
        unknown_magnitude_units=None if unknown_count else 0.0,
        scoring_coverage_ratio=(len(scored) / total_count if total_count else 0.0),
    )


def _summary_matches(
    left: SbcAtomicLedgerSummary,
    right: SbcAtomicLedgerSummary,
) -> bool:
    return (
        _float_equal(
            left.favorable_guidance_units,
            right.favorable_guidance_units,
        )
        and _float_equal(
            left.adverse_guidance_units,
            right.adverse_guidance_units,
        )
        and _float_equal(left.net_guidance_units, right.net_guidance_units)
        and _float_equal(
            left.gross_activation_units,
            right.gross_activation_units,
        )
        and left.scored_contribution_count == right.scored_contribution_count
        and left.unknown_contribution_count == right.unknown_contribution_count
        and left.missing_evidence_count == right.missing_evidence_count
        and left.total_evidence_count == right.total_evidence_count
        and left.unknown_magnitude_units == right.unknown_magnitude_units
        and _float_equal(
            left.scoring_coverage_ratio,
            right.scoring_coverage_ratio,
        )
    )


def _summary_from_cells(
    cells: Iterable[SbcLedgerDimensionCell],
) -> SbcAtomicLedgerSummary:
    ordered = tuple(cells)
    unknown_count = sum(item.summary.unknown_contribution_count for item in ordered)
    total_count = sum(item.summary.total_evidence_count for item in ordered)
    scored_count = sum(item.summary.scored_contribution_count for item in ordered)
    return SbcAtomicLedgerSummary(
        favorable_guidance_units=math.fsum(
            item.summary.favorable_guidance_units for item in ordered
        ),
        adverse_guidance_units=math.fsum(
            item.summary.adverse_guidance_units for item in ordered
        ),
        net_guidance_units=math.fsum(
            item.summary.net_guidance_units for item in ordered
        ),
        gross_activation_units=math.fsum(
            item.summary.gross_activation_units for item in ordered
        ),
        scored_contribution_count=scored_count,
        unknown_contribution_count=unknown_count,
        missing_evidence_count=sum(
            item.summary.missing_evidence_count for item in ordered
        ),
        total_evidence_count=total_count,
        unknown_magnitude_units=None if unknown_count else 0.0,
        scoring_coverage_ratio=(scored_count / total_count if total_count else 0.0),
    )


def _dimension_key(cluster: SbcCausalCluster, axis: str) -> str:
    if axis == TOTAL_AXIS:
        return TOTAL_DIMENSION_KEY
    if axis == ACTOR_AXIS:
        return cluster.actor_identity or UNAVAILABLE_DIMENSION_KEY
    if axis == TARGET_LAYER_AXIS:
        return cluster.target_layer or UNAVAILABLE_DIMENSION_KEY
    if axis == NATURE_AXIS:
        return cluster.nature or UNAVAILABLE_DIMENSION_KEY
    if axis == VEDHA_DIRECTION_AXIS:
        return cluster.vedha_direction or UNAVAILABLE_DIMENSION_KEY
    if axis == SOURCE_LINEAGE_AXIS:
        return cluster.source_lineage_id
    raise ValueError(f"unknown ledger axis: {axis}")


def _field_roles() -> tuple[SbcLedgerFieldRole, ...]:
    return (
        SbcLedgerFieldRole(
            field_path="seriesIdentityAndProvenance",
            derivation_role=NON_VOTING_CONTEXT_ROLE,
            evidence_bearing=False,
        ),
        SbcLedgerFieldRole(
            field_path="intervalLedgers[].intervalMetadata",
            derivation_role=NON_VOTING_CONTEXT_ROLE,
            evidence_bearing=False,
        ),
        SbcLedgerFieldRole(
            field_path="intervalLedgers[].causalClusters",
            derivation_role=PRIMARY_EVIDENCE_ROLE,
            evidence_bearing=True,
        ),
        SbcLedgerFieldRole(
            field_path="intervalLedgers[].dimensionCells",
            derivation_role=DERIVED_AXIS_ROLE,
            evidence_bearing=False,
        ),
        SbcLedgerFieldRole(
            field_path="intervalLedgers[].totalSummary",
            derivation_role=DERIVED_AXIS_ROLE,
            evidence_bearing=False,
        ),
        SbcLedgerFieldRole(
            field_path="intervalLedgers[].axisReconciliations",
            derivation_role=NON_VOTING_CONTEXT_ROLE,
            evidence_bearing=False,
        ),
        SbcLedgerFieldRole(
            field_path="intervalLedgers[].duplicatePrimaryEvidenceCount",
            derivation_role=NON_VOTING_CONTEXT_ROLE,
            evidence_bearing=False,
        ),
        SbcLedgerFieldRole(
            field_path="guardrails",
            derivation_role=NON_VOTING_CONTEXT_ROLE,
            evidence_bearing=False,
        ),
    )


def _validate_source_series(series: SbcAtomicIntervalSeries) -> tuple[SbcAtomicInterval, ...]:
    if not isinstance(series, SbcAtomicIntervalSeries):
        raise ValueError("series must be SbcAtomicIntervalSeries")
    if series.contract != ATOMIC_INTERVAL_CONTRACT:
        raise ValueError("P2 requires the canonical P1 atomic interval contract")
    if series.schema_version != ATOMIC_INTERVAL_SCHEMA_VERSION:
        raise ValueError("P2 requires the canonical P1 schema version")
    if series.interval_policy != ATOMIC_INTERVAL_POLICY:
        raise ValueError("P2 requires explicit-boundary P1 intervals")
    if series.classification != RESEARCH_CLASSIFICATION:
        raise ValueError("P2 requires SOURCE_PROFILED_EXPERIMENTAL input")
    _sha256(series.series_id, "series_id")
    if not isinstance(series.profile_identity, SbcAtomicProfileIdentity):
        raise ValueError("P1 series profile_identity is invalid")
    _unique_sorted(series.source_ids, "source_ids", required=True)
    source_guardrails = series.guardrails
    if not (
        source_guardrails.research_only
        and source_guardrails.timestamp_safe
        and source_guardrails.no_lookahead
        and source_guardrails.source_profiled_experimental
        and not source_guardrails.counts_as_independent_vote
        and float(source_guardrails.directional_contribution) == 0.0
        and not source_guardrails.execution_allowed
    ):
        raise ValueError("P1 series weakens required P2 guardrails")

    range_start = _utc(series.range_start_utc, "range_start_utc")
    range_end = _utc(series.range_end_utc, "range_end_utc")
    if range_start >= range_end:
        raise ValueError("P1 series range must have positive duration")
    ordered = tuple(sorted(series.intervals, key=lambda item: item.start_utc))
    if not ordered:
        raise ValueError("P2 requires at least one atomic interval")
    ids = tuple(item.interval_id for item in ordered)
    if len(ids) != len(set(ids)):
        raise ValueError("P1 interval identities must be unique")
    if ordered[0].start_utc != range_start or ordered[-1].end_utc != range_end:
        raise ValueError("P1 intervals must cover the declared series range")
    for index, interval in enumerate(ordered):
        if interval.classification != RESEARCH_CLASSIFICATION:
            raise ValueError("P1 intervals must remain source-profiled experimental")
        if interval.profile_identity != series.profile_identity:
            raise ValueError("P1 interval profile identity differs from its series")
        if interval.start_utc >= interval.end_utc:
            raise ValueError("P1 intervals must have positive duration")
        if interval.evidence_cutoff_utc > interval.start_utc:
            raise ValueError("P1 interval evidence cutoff exceeds interval start")
        if index and ordered[index - 1].end_utc != interval.start_utc:
            raise ValueError("P1 intervals must remain contiguous")
    return ordered


def _contribution_cluster(
    interval: SbcAtomicInterval,
    contribution: SbcAtomicContribution,
    *,
    instrument_identity: str,
) -> SbcCausalCluster:
    return SbcCausalCluster(
        instrument_identity=instrument_identity,
        interval_id=interval.interval_id,
        interval_start_utc=interval.start_utc,
        interval_end_utc=interval.end_utc,
        evidence_cutoff_utc=interval.evidence_cutoff_utc,
        snapshot_id=interval.snapshot_id,
        profile_identity=interval.profile_identity,
        source_ids=interval.source_ids,
        evidence_kind=CONTRIBUTION_EVIDENCE,
        derivation_role=PRIMARY_EVIDENCE_ROLE,
        source_lineage_id=contribution.source_lineage_id,
        contribution_id=contribution.contribution_id,
        missing_evidence_id=None,
        actor_identity=contribution.body,
        source_nakshatra=contribution.source_nakshatra,
        vedha_direction=contribution.vedha_direction,
        target_row=contribution.target_row,
        target_column=contribution.target_column,
        target_layer=contribution.target_layer,
        target_value=contribution.target_value,
        target_witness_set_id=contribution.target_witness_set_id,
        target_evidence_status=contribution.target_evidence_status,
        nature=contribution.nature,
        effective_multiplier=contribution.effective_multiplier,
        signed_guidance_units=contribution.signed_guidance_units,
        status=contribution.status,
        unknown_reason=contribution.unknown_reason,
        citation_source_ids=contribution.citation_source_ids,
    )


def _missing_cluster(
    interval: SbcAtomicInterval,
    missing_evidence_id: str,
    *,
    instrument_identity: str,
) -> SbcCausalCluster:
    return SbcCausalCluster(
        instrument_identity=instrument_identity,
        interval_id=interval.interval_id,
        interval_start_utc=interval.start_utc,
        interval_end_utc=interval.end_utc,
        evidence_cutoff_utc=interval.evidence_cutoff_utc,
        snapshot_id=interval.snapshot_id,
        profile_identity=interval.profile_identity,
        source_ids=interval.source_ids,
        evidence_kind=MISSING_EVIDENCE,
        derivation_role=PRIMARY_EVIDENCE_ROLE,
        source_lineage_id=_missing_lineage_id(missing_evidence_id),
        contribution_id=None,
        missing_evidence_id=missing_evidence_id,
        actor_identity=None,
        source_nakshatra=None,
        vedha_direction=None,
        target_row=None,
        target_column=None,
        target_layer=None,
        target_value=None,
        target_witness_set_id=None,
        target_evidence_status=None,
        nature=None,
        effective_multiplier=None,
        signed_guidance_units=None,
        status="MISSING_EVIDENCE",
        unknown_reason=f"Explicit missing evidence: {missing_evidence_id}",
        citation_source_ids=(),
    )


def _clusters_for_interval(
    interval: SbcAtomicInterval,
    *,
    instrument_identity: str,
) -> tuple[tuple[SbcCausalCluster, ...], int]:
    by_lineage: dict[str, SbcAtomicContribution] = {}
    duplicate_count = 0
    for contribution in sorted(
        interval.contributions,
        key=lambda item: (item.source_lineage_id, item.contribution_id),
    ):
        prior = by_lineage.get(contribution.source_lineage_id)
        if prior is None:
            by_lineage[contribution.source_lineage_id] = contribution
            continue
        if prior.contribution_id != contribution.contribution_id:
            raise ValueError(
                "conflicting evaluated contributions share source lineage "
                f"{contribution.source_lineage_id}"
            )
        duplicate_count += 1

    missing_ids = tuple(sorted(set(interval.missing_evidence_ids)))
    duplicate_count += len(interval.missing_evidence_ids) - len(missing_ids)
    clusters = [
        _contribution_cluster(
            interval,
            contribution,
            instrument_identity=instrument_identity,
        )
        for contribution in by_lineage.values()
    ]
    clusters.extend(
        _missing_cluster(
            interval,
            missing_evidence_id,
            instrument_identity=instrument_identity,
        )
        for missing_evidence_id in missing_ids
    )
    ordered = tuple(sorted(clusters, key=lambda item: item.cluster_id))
    cluster_ids = tuple(item.cluster_id for item in ordered)
    if len(cluster_ids) != len(set(cluster_ids)):
        raise ValueError("canonical causal-cluster identities must be unique")
    return ordered, duplicate_count


def _dimension_cells(
    interval: SbcAtomicInterval,
    clusters: tuple[SbcCausalCluster, ...],
    total_summary: SbcAtomicLedgerSummary,
) -> tuple[SbcLedgerDimensionCell, ...]:
    cells: list[SbcLedgerDimensionCell] = []
    for axis in LEDGER_AXES:
        grouped: dict[str, list[SbcCausalCluster]] = defaultdict(list)
        if axis == TOTAL_AXIS:
            grouped[TOTAL_DIMENSION_KEY].extend(clusters)
        else:
            for cluster in clusters:
                grouped[_dimension_key(cluster, axis)].append(cluster)
        for key in sorted(grouped):
            members = tuple(sorted(grouped[key], key=lambda item: item.cluster_id))
            summary = (
                total_summary
                if axis == TOTAL_AXIS and key == TOTAL_DIMENSION_KEY
                else _summary_from_clusters(members)
            )
            cells.append(
                SbcLedgerDimensionCell(
                    interval_id=interval.interval_id,
                    axis=axis,
                    key=key,
                    derivation_role=DERIVED_AXIS_ROLE,
                    cluster_ids=tuple(item.cluster_id for item in members),
                    summary=summary,
                )
            )
    return tuple(
        sorted(
            cells,
            key=lambda item: (LEDGER_AXES.index(item.axis), item.key),
        )
    )


def _axis_reconciliation(
    axis: str,
    cells: tuple[SbcLedgerDimensionCell, ...],
    clusters: tuple[SbcCausalCluster, ...],
    total_summary: SbcAtomicLedgerSummary,
) -> SbcLedgerAxisReconciliation:
    axis_cells = tuple(item for item in cells if item.axis == axis)
    references = Counter(
        cluster_id for cell in axis_cells for cluster_id in cell.cluster_ids
    )
    expected_ids = {item.cluster_id for item in clusters}
    exactly_once = (
        set(references) == expected_ids
        and all(references[cluster_id] == 1 for cluster_id in expected_ids)
    )
    cell_summary = _summary_from_cells(axis_cells)
    favorable_matches = _float_equal(
        cell_summary.favorable_guidance_units,
        total_summary.favorable_guidance_units,
    )
    adverse_matches = _float_equal(
        cell_summary.adverse_guidance_units,
        total_summary.adverse_guidance_units,
    )
    net_matches = _float_equal(
        cell_summary.net_guidance_units,
        total_summary.net_guidance_units,
    )
    gross_matches = _float_equal(
        cell_summary.gross_activation_units,
        total_summary.gross_activation_units,
    )
    scored_count_matches = (
        cell_summary.scored_contribution_count
        == total_summary.scored_contribution_count
    )
    unknown_count_matches = (
        cell_summary.unknown_contribution_count
        == total_summary.unknown_contribution_count
    )
    missing_count_matches = (
        cell_summary.missing_evidence_count
        == total_summary.missing_evidence_count
    )
    total_count_matches = (
        cell_summary.total_evidence_count == total_summary.total_evidence_count
    )
    reconciled = all(
        (
            exactly_once,
            favorable_matches,
            adverse_matches,
            net_matches,
            gross_matches,
            scored_count_matches,
            unknown_count_matches,
            missing_count_matches,
            total_count_matches,
        )
    )
    return SbcLedgerAxisReconciliation(
        axis=axis,
        cell_count=len(axis_cells),
        cluster_count=len(clusters),
        every_cluster_exactly_once=exactly_once,
        favorable_matches=favorable_matches,
        adverse_matches=adverse_matches,
        net_matches=net_matches,
        gross_matches=gross_matches,
        scored_count_matches=scored_count_matches,
        unknown_count_matches=unknown_count_matches,
        missing_count_matches=missing_count_matches,
        total_count_matches=total_count_matches,
        reconciled=reconciled,
    )


class SbcMultidimensionalLedgerCompiler:
    def compile(
        self,
        series: SbcAtomicIntervalSeries,
        *,
        instrument_identity: str,
    ) -> SbcMultidimensionalLedgerSeries:
        instrument = _required_text(instrument_identity, "instrument_identity")
        intervals = _validate_source_series(series)
        interval_ledgers: list[SbcMultidimensionalIntervalLedger] = []
        for interval in intervals:
            clusters, duplicate_count = _clusters_for_interval(
                interval,
                instrument_identity=instrument,
            )
            computed_total = _summary_from_clusters(clusters)
            if not _summary_matches(computed_total, interval.ledger):
                raise ValueError(
                    "deduplicated causal clusters do not reproduce the P1 scalar "
                    f"ledger for interval {interval.interval_id}"
                )
            cells = _dimension_cells(interval, clusters, interval.ledger)
            reconciliations = tuple(
                _axis_reconciliation(
                    axis,
                    cells,
                    clusters,
                    interval.ledger,
                )
                for axis in LEDGER_AXES
            )
            if not all(item.reconciled for item in reconciliations):
                raise ValueError(
                    f"multidimensional axis reconciliation failed for {interval.interval_id}"
                )
            identity = {
                "contract": MULTIDIMENSIONAL_LEDGER_CONTRACT,
                "instrument_identity": instrument,
                "source_interval_id": interval.interval_id,
                "cluster_ids": tuple(item.cluster_id for item in clusters),
                "cell_ids": tuple(item.cell_id for item in cells),
                "duplicate_primary_evidence_count": duplicate_count,
                "total_summary": interval.ledger.to_dict(),
                "axis_reconciliations": tuple(
                    item.to_dict() for item in reconciliations
                ),
            }
            interval_ledgers.append(
                SbcMultidimensionalIntervalLedger(
                    interval_id=interval.interval_id,
                    classification=RESEARCH_CLASSIFICATION,
                    start_utc=interval.start_utc,
                    end_utc=interval.end_utc,
                    evidence_cutoff_utc=interval.evidence_cutoff_utc,
                    causal_clusters=clusters,
                    dimension_cells=cells,
                    duplicate_primary_evidence_count=duplicate_count,
                    total_summary=interval.ledger,
                    axis_reconciliations=reconciliations,
                    interval_ledger_id=_canonical_hash(identity),
                )
            )

        guardrails = SbcMultidimensionalLedgerGuardrails()
        field_roles = _field_roles()
        series_identity = {
            "contract": MULTIDIMENSIONAL_LEDGER_CONTRACT,
            "schema_version": MULTIDIMENSIONAL_LEDGER_SCHEMA_VERSION,
            "classification": RESEARCH_CLASSIFICATION,
            "instrument_identity": instrument,
            "source_atomic_series_id": series.series_id,
            "range_start_utc": intervals[0].start_utc.isoformat(),
            "range_end_utc": intervals[-1].end_utc.isoformat(),
            "profile_identity": series.profile_identity.to_dict(),
            "source_ids": series.source_ids,
            "field_roles": tuple(item.to_dict() for item in field_roles),
            "interval_ledger_ids": tuple(
                item.interval_ledger_id for item in interval_ledgers
            ),
            "guardrails": to_primitive(guardrails),
        }
        return SbcMultidimensionalLedgerSeries(
            contract=MULTIDIMENSIONAL_LEDGER_CONTRACT,
            schema_version=MULTIDIMENSIONAL_LEDGER_SCHEMA_VERSION,
            classification=RESEARCH_CLASSIFICATION,
            ledger_id=_canonical_hash(series_identity),
            instrument_identity=instrument,
            source_atomic_series_id=series.series_id,
            range_start_utc=intervals[0].start_utc,
            range_end_utc=intervals[-1].end_utc,
            profile_identity=series.profile_identity,
            source_ids=series.source_ids,
            field_roles=field_roles,
            interval_ledgers=tuple(interval_ledgers),
            guardrails=guardrails,
        )
