from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from .atomic_intervals import RESEARCH_CLASSIFICATION, SbcAtomicLedgerSummary
from .models import to_primitive
from .multidimensional_ledger import (
    DERIVED_AXIS_ROLE,
    LEDGER_AXES,
    MULTIDIMENSIONAL_LEDGER_CONTRACT,
    MULTIDIMENSIONAL_LEDGER_SCHEMA_VERSION,
    PRIMARY_EVIDENCE_ROLE,
    SbcMultidimensionalLedgerSeries,
)


LINKED_AUDIT_VIEW_CONTRACT = "SBC_LINKED_AUDIT_VIEW_V1"
LINKED_AUDIT_VIEW_SCHEMA_VERSION = 1
LINKED_AUDIT_VIEW_POLICY = "LINKED_READ_ONLY_PROGRESSIVE_DISCLOSURE_V1"

PASS = "PASS"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"
VALIDATION_STATES = (PASS, FAIL, UNKNOWN)

TIMELINE_VIEW = "TIMELINE"
LEDGER_VIEW = "LEDGER"
RAY_AUDIT_VIEW = "RAY_AUDIT"
SOURCE_LINEAGE_VIEW = "SOURCE_LINEAGE"
RECONCILIATION_VIEW = "RECONCILIATION"
VALIDATION_VIEW = "VALIDATION"
AUDIT_VIEW_IDS = (
    TIMELINE_VIEW,
    LEDGER_VIEW,
    RAY_AUDIT_VIEW,
    SOURCE_LINEAGE_VIEW,
    RECONCILIATION_VIEW,
    VALIDATION_VIEW,
)


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


def _sha256(value: Any, label: str) -> str:
    normalized = _required_text(value, label).upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"{label} must be an uppercase SHA-256 digest")
    return normalized


def _utc(value: datetime, label: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _sorted_digests(values: Iterable[str], label: str) -> tuple[str, ...]:
    normalized = tuple(sorted(_sha256(item, label) for item in values))
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} values must be unique")
    return normalized


@dataclass(frozen=True)
class SbcAuditViewDescriptor:
    view_id: str
    label: str
    purpose: str
    phase_vector_included: bool = False
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        view_id = _required_text(self.view_id, "view_id")
        if view_id not in AUDIT_VIEW_IDS:
            raise ValueError(f"unknown audit view: {view_id}")
        object.__setattr__(self, "view_id", view_id)
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "purpose", _required_text(self.purpose, "purpose"))
        if self.phase_vector_included:
            raise ValueError("P3 audit views cannot include phase vectors")
        if self.counts_as_independent_vote:
            raise ValueError("P3 audit views cannot count as independent votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("P3 audit views cannot contribute market direction")


@dataclass(frozen=True)
class SbcAuditIntervalRow:
    interval_id: str
    interval_ledger_id: str
    start_utc: datetime
    end_utc: datetime
    evidence_cutoff_utc: datetime
    duration_seconds: int
    cluster_ids: tuple[str, ...]
    cell_ids: tuple[str, ...]
    duplicate_primary_evidence_count: int
    total_summary: SbcAtomicLedgerSummary
    all_axes_reconciled: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "interval_id", _sha256(self.interval_id, "interval_id"))
        object.__setattr__(
            self,
            "interval_ledger_id",
            _sha256(self.interval_ledger_id, "interval_ledger_id"),
        )
        start = _utc(self.start_utc, "start_utc")
        end = _utc(self.end_utc, "end_utc")
        cutoff = _utc(self.evidence_cutoff_utc, "evidence_cutoff_utc")
        if start >= end:
            raise ValueError("audit intervals must have positive duration")
        if cutoff > start:
            raise ValueError("audit evidence cutoff cannot exceed interval start")
        duration = int((end - start).total_seconds())
        if int(self.duration_seconds) != duration:
            raise ValueError("duration_seconds must exactly match the interval")
        object.__setattr__(self, "start_utc", start)
        object.__setattr__(self, "end_utc", end)
        object.__setattr__(self, "evidence_cutoff_utc", cutoff)
        object.__setattr__(self, "duration_seconds", duration)
        object.__setattr__(
            self,
            "cluster_ids",
            _sorted_digests(self.cluster_ids, "cluster_id"),
        )
        object.__setattr__(
            self,
            "cell_ids",
            _sorted_digests(self.cell_ids, "cell_id"),
        )
        if int(self.duplicate_primary_evidence_count) < 0:
            raise ValueError("duplicate_primary_evidence_count cannot be negative")
        if not isinstance(self.total_summary, SbcAtomicLedgerSummary):
            raise ValueError("total_summary must be SbcAtomicLedgerSummary")
        if not self.all_axes_reconciled:
            raise ValueError("P3 cannot display an unreconciled P2 interval")


@dataclass(frozen=True)
class SbcAuditLedgerCellRow:
    cell_id: str
    interval_id: str
    axis: str
    key: str
    derivation_role: str
    cluster_ids: tuple[str, ...]
    summary: SbcAtomicLedgerSummary
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "cell_id", _sha256(self.cell_id, "cell_id"))
        object.__setattr__(self, "interval_id", _sha256(self.interval_id, "interval_id"))
        axis = _required_text(self.axis, "axis")
        if axis not in LEDGER_AXES:
            raise ValueError(f"unknown ledger axis: {axis}")
        object.__setattr__(self, "axis", axis)
        object.__setattr__(self, "key", _required_text(self.key, "key"))
        if self.derivation_role != DERIVED_AXIS_ROLE:
            raise ValueError("audit ledger cells must preserve DERIVED_AXIS")
        object.__setattr__(
            self,
            "cluster_ids",
            _sorted_digests(self.cluster_ids, "cluster_id"),
        )
        if not isinstance(self.summary, SbcAtomicLedgerSummary):
            raise ValueError("summary must be SbcAtomicLedgerSummary")
        if self.counts_as_independent_vote:
            raise ValueError("audit ledger cells cannot count as votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("audit ledger cells cannot contribute market direction")


@dataclass(frozen=True)
class SbcAuditRayRow:
    cluster_id: str
    interval_id: str
    cell_ids: tuple[str, ...]
    evidence_kind: str
    derivation_role: str
    actor_identity: str | None
    source_nakshatra: str | None
    vedha_direction: str | None
    target_row: int | None
    target_column: int | None
    target_layer: str | None
    target_value: str | None
    nature: str | None
    effective_multiplier: float | None
    signed_guidance_units: float | None
    status: str
    unknown_reason: str | None
    phase_angle: None = None
    phase_vector_included: bool = False
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "cluster_id", _sha256(self.cluster_id, "cluster_id"))
        object.__setattr__(self, "interval_id", _sha256(self.interval_id, "interval_id"))
        object.__setattr__(
            self,
            "cell_ids",
            _sorted_digests(self.cell_ids, "cell_id"),
        )
        object.__setattr__(
            self,
            "evidence_kind",
            _required_text(self.evidence_kind, "evidence_kind"),
        )
        if self.derivation_role != PRIMARY_EVIDENCE_ROLE:
            raise ValueError("ray rows must preserve PRIMARY_EVIDENCE")
        object.__setattr__(self, "status", _required_text(self.status, "status"))
        if self.phase_angle is not None or self.phase_vector_included:
            raise ValueError("P3 ray audit cannot include phase values")
        if self.counts_as_independent_vote:
            raise ValueError("ray audit rows cannot count as votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("ray audit rows cannot contribute market direction")


@dataclass(frozen=True)
class SbcAuditLineageRow:
    cluster_id: str
    interval_id: str
    source_lineage_id: str
    source_ids: tuple[str, ...]
    citation_source_ids: tuple[str, ...]
    snapshot_id: str
    foundation_profile_id: str
    foundation_profile_hash: str
    grid_profile_id: str
    grid_profile_hash: str
    vedha_profile_id: str
    vedha_profile_hash: str
    guidance_model_id: str
    target_witness_set_id: str | None
    target_evidence_status: str | None
    status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "cluster_id", _sha256(self.cluster_id, "cluster_id"))
        object.__setattr__(self, "interval_id", _sha256(self.interval_id, "interval_id"))
        object.__setattr__(
            self,
            "source_lineage_id",
            _sha256(self.source_lineage_id, "source_lineage_id"),
        )
        object.__setattr__(self, "snapshot_id", _sha256(self.snapshot_id, "snapshot_id"))
        object.__setattr__(
            self,
            "source_ids",
            tuple(sorted(_required_text(item, "source_id") for item in self.source_ids)),
        )
        object.__setattr__(
            self,
            "citation_source_ids",
            tuple(
                sorted(
                    _required_text(item, "citation_source_id")
                    for item in self.citation_source_ids
                )
            ),
        )
        for field_name in (
            "foundation_profile_id",
            "grid_profile_id",
            "vedha_profile_id",
            "guidance_model_id",
            "status",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name),
            )
        for field_name in (
            "foundation_profile_hash",
            "grid_profile_hash",
            "vedha_profile_hash",
        ):
            object.__setattr__(
                self,
                field_name,
                _sha256(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True)
class SbcAuditReconciliationRow:
    interval_id: str
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

    def __post_init__(self) -> None:
        object.__setattr__(self, "interval_id", _sha256(self.interval_id, "interval_id"))
        axis = _required_text(self.axis, "axis")
        if axis not in LEDGER_AXES:
            raise ValueError(f"unknown reconciliation axis: {axis}")
        object.__setattr__(self, "axis", axis)
        if not self.reconciled:
            raise ValueError("P3 cannot publish an unreconciled axis")


@dataclass(frozen=True)
class SbcAuditValidationGate:
    gate_id: str
    state: str
    label: str
    detail: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "gate_id", _required_text(self.gate_id, "gate_id"))
        state = _required_text(self.state, "state")
        if state not in VALIDATION_STATES:
            raise ValueError(f"unknown validation state: {state}")
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "detail", _required_text(self.detail, "detail"))


@dataclass(frozen=True)
class SbcLinkedAuditViewGuardrails:
    read_only: bool = True
    timestamp_safe: bool = True
    no_lookahead: bool = True
    source_profiled_experimental: bool = True
    financially_validated: bool = False
    phase_included: bool = False
    fx_subtraction_included: bool = False
    confidence_included: bool = False
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0
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
class SbcLinkedAuditView:
    contract: str
    schema_version: int
    view_policy: str
    classification: str
    audit_view_id: str
    source_ledger_id: str
    source_atomic_series_id: str
    instrument_identity: str
    range_start_utc: datetime
    range_end_utc: datetime
    source_ids: tuple[str, ...]
    views: tuple[SbcAuditViewDescriptor, ...]
    intervals: tuple[SbcAuditIntervalRow, ...]
    ledger_cells: tuple[SbcAuditLedgerCellRow, ...]
    ray_rows: tuple[SbcAuditRayRow, ...]
    lineage_rows: tuple[SbcAuditLineageRow, ...]
    reconciliations: tuple[SbcAuditReconciliationRow, ...]
    validation_gates: tuple[SbcAuditValidationGate, ...]
    guardrails: SbcLinkedAuditViewGuardrails

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


def _view_descriptors() -> tuple[SbcAuditViewDescriptor, ...]:
    return (
        SbcAuditViewDescriptor(
            TIMELINE_VIEW,
            "Timeline",
            "Inspect explicit half-open intervals and their evidence cutoffs.",
        ),
        SbcAuditViewDescriptor(
            LEDGER_VIEW,
            "Ledger",
            "Compare the reconciled P2 dimensions without creating extra votes.",
        ),
        SbcAuditViewDescriptor(
            RAY_AUDIT_VIEW,
            "Ray audit",
            "Inspect source-profiled Vedha directions; this is not a phase vector.",
        ),
        SbcAuditViewDescriptor(
            SOURCE_LINEAGE_VIEW,
            "Lineage",
            "Trace every causal cluster to snapshots, profiles, and citations.",
        ),
        SbcAuditViewDescriptor(
            RECONCILIATION_VIEW,
            "Reconciliation",
            "Verify every dimension reproduces the scalar interval ledger.",
        ),
        SbcAuditViewDescriptor(
            VALIDATION_VIEW,
            "Validation",
            "Keep unknown, unvalidated, and blocked capabilities visible.",
        ),
    )


def _validation_gates(
    *,
    intervals: tuple[SbcAuditIntervalRow, ...],
    reconciliations: tuple[SbcAuditReconciliationRow, ...],
) -> tuple[SbcAuditValidationGate, ...]:
    unknown_count = sum(
        item.total_summary.unknown_contribution_count for item in intervals
    )
    return (
        SbcAuditValidationGate(
            "TIMESTAMP_SAFETY",
            PASS,
            "Timestamp-safe boundaries",
            "Every interval has an explicit start, end, and evidence cutoff.",
        ),
        SbcAuditValidationGate(
            "AXIS_RECONCILIATION",
            PASS if all(item.reconciled for item in reconciliations) else FAIL,
            "P2 axis reconciliation",
            "Every displayed dimension reproduces the interval total exactly.",
        ),
        SbcAuditValidationGate(
            "UNKNOWN_EVIDENCE",
            UNKNOWN if unknown_count else PASS,
            "Unknown evidence",
            (
                f"{unknown_count} contribution(s) remain explicitly unknown."
                if unknown_count
                else "No unknown contribution is present in this captured range."
            ),
        ),
        SbcAuditValidationGate(
            "FINANCIAL_VALIDATION",
            UNKNOWN,
            "Financial validation",
            "No immutable prospective financial validation package is attached.",
        ),
        SbcAuditValidationGate(
            "PHASE_PROFILE",
            UNKNOWN,
            "Timing-phase profile",
            "No certified timing-phase sectors, boundaries, or station rules are included.",
        ),
        SbcAuditValidationGate(
            "EXECUTION_LOCK",
            PASS,
            "Execution lock",
            "Market direction, trade output, and MT5 execution remain blocked.",
        ),
    )


def _validate_source(series: SbcMultidimensionalLedgerSeries) -> None:
    if not isinstance(series, SbcMultidimensionalLedgerSeries):
        raise ValueError("series must be SbcMultidimensionalLedgerSeries")
    if series.contract != MULTIDIMENSIONAL_LEDGER_CONTRACT:
        raise ValueError("P3 requires the canonical P2 ledger contract")
    if series.schema_version != MULTIDIMENSIONAL_LEDGER_SCHEMA_VERSION:
        raise ValueError("P3 requires the canonical P2 schema version")
    if series.classification != RESEARCH_CLASSIFICATION:
        raise ValueError("P3 requires SOURCE_PROFILED_EXPERIMENTAL input")
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
        raise ValueError("P2 ledger weakens required P3 guardrails")


class SbcLinkedAuditViewCompiler:
    def compile(
        self,
        series: SbcMultidimensionalLedgerSeries,
    ) -> SbcLinkedAuditView:
        _validate_source(series)
        ordered = tuple(
            sorted(series.interval_ledgers, key=lambda item: item.start_utc)
        )
        if not ordered:
            raise ValueError("P3 requires at least one P2 interval ledger")
        if ordered[0].start_utc != series.range_start_utc:
            raise ValueError("P3 source range does not begin with its first interval")
        if ordered[-1].end_utc != series.range_end_utc:
            raise ValueError("P3 source range does not end with its final interval")
        for index, interval in enumerate(ordered):
            if index and ordered[index - 1].end_utc != interval.start_utc:
                raise ValueError("P3 source intervals must remain contiguous")
            if not all(item.reconciled for item in interval.axis_reconciliations):
                raise ValueError("P3 source contains an unreconciled axis")

        cluster_to_cells: dict[str, list[str]] = {}
        all_cluster_ids: set[str] = set()
        all_cell_ids: set[str] = set()
        for interval in ordered:
            interval_cluster_ids = {
                _sha256(item.cluster_id, "cluster_id")
                for item in interval.causal_clusters
            }
            if all_cluster_ids & interval_cluster_ids:
                raise ValueError("cluster identities must be unique across intervals")
            all_cluster_ids.update(interval_cluster_ids)
            for cell in interval.dimension_cells:
                cell_id = _sha256(cell.cell_id, "cell_id")
                if cell_id in all_cell_ids:
                    raise ValueError("cell identities must be unique across intervals")
                all_cell_ids.add(cell_id)
                unknown = set(cell.cluster_ids) - interval_cluster_ids
                if unknown:
                    raise ValueError("ledger cell links to an unknown interval cluster")
                for cluster_id in cell.cluster_ids:
                    cluster_to_cells.setdefault(cluster_id, []).append(cell_id)

        intervals = tuple(
            SbcAuditIntervalRow(
                interval_id=item.interval_id,
                interval_ledger_id=item.interval_ledger_id,
                start_utc=item.start_utc,
                end_utc=item.end_utc,
                evidence_cutoff_utc=item.evidence_cutoff_utc,
                duration_seconds=int((item.end_utc - item.start_utc).total_seconds()),
                cluster_ids=tuple(
                    cluster.cluster_id for cluster in item.causal_clusters
                ),
                cell_ids=tuple(cell.cell_id for cell in item.dimension_cells),
                duplicate_primary_evidence_count=item.duplicate_primary_evidence_count,
                total_summary=item.total_summary,
                all_axes_reconciled=all(
                    reconciliation.reconciled
                    for reconciliation in item.axis_reconciliations
                ),
            )
            for item in ordered
        )
        ledger_cells = tuple(
            SbcAuditLedgerCellRow(
                cell_id=cell.cell_id,
                interval_id=item.interval_id,
                axis=cell.axis,
                key=cell.key,
                derivation_role=cell.derivation_role,
                cluster_ids=cell.cluster_ids,
                summary=cell.summary,
            )
            for item in ordered
            for cell in item.dimension_cells
        )
        ray_rows = tuple(
            SbcAuditRayRow(
                cluster_id=cluster.cluster_id,
                interval_id=item.interval_id,
                cell_ids=tuple(cluster_to_cells.get(cluster.cluster_id, ())),
                evidence_kind=cluster.evidence_kind,
                derivation_role=cluster.derivation_role,
                actor_identity=cluster.actor_identity,
                source_nakshatra=cluster.source_nakshatra,
                vedha_direction=cluster.vedha_direction,
                target_row=cluster.target_row,
                target_column=cluster.target_column,
                target_layer=cluster.target_layer,
                target_value=cluster.target_value,
                nature=cluster.nature,
                effective_multiplier=cluster.effective_multiplier,
                signed_guidance_units=cluster.signed_guidance_units,
                status=cluster.status,
                unknown_reason=cluster.unknown_reason,
            )
            for item in ordered
            for cluster in item.causal_clusters
        )
        lineage_rows = tuple(
            SbcAuditLineageRow(
                cluster_id=cluster.cluster_id,
                interval_id=item.interval_id,
                source_lineage_id=cluster.source_lineage_id,
                source_ids=cluster.source_ids,
                citation_source_ids=cluster.citation_source_ids,
                snapshot_id=cluster.snapshot_id,
                foundation_profile_id=cluster.profile_identity.foundation_profile_id,
                foundation_profile_hash=(
                    cluster.profile_identity.foundation_profile_hash
                ),
                grid_profile_id=cluster.profile_identity.grid_profile_id,
                grid_profile_hash=cluster.profile_identity.grid_profile_hash,
                vedha_profile_id=cluster.profile_identity.vedha_profile_id,
                vedha_profile_hash=cluster.profile_identity.vedha_profile_hash,
                guidance_model_id=cluster.profile_identity.guidance_model_id,
                target_witness_set_id=cluster.target_witness_set_id,
                target_evidence_status=cluster.target_evidence_status,
                status=cluster.status,
            )
            for item in ordered
            for cluster in item.causal_clusters
        )
        reconciliations = tuple(
            SbcAuditReconciliationRow(
                interval_id=item.interval_id,
                axis=reconciliation.axis,
                cell_count=reconciliation.cell_count,
                cluster_count=reconciliation.cluster_count,
                every_cluster_exactly_once=(
                    reconciliation.every_cluster_exactly_once
                ),
                favorable_matches=reconciliation.favorable_matches,
                adverse_matches=reconciliation.adverse_matches,
                net_matches=reconciliation.net_matches,
                gross_matches=reconciliation.gross_matches,
                scored_count_matches=reconciliation.scored_count_matches,
                unknown_count_matches=reconciliation.unknown_count_matches,
                missing_count_matches=reconciliation.missing_count_matches,
                total_count_matches=reconciliation.total_count_matches,
                reconciled=reconciliation.reconciled,
            )
            for item in ordered
            for reconciliation in item.axis_reconciliations
        )
        views = _view_descriptors()
        validation_gates = _validation_gates(
            intervals=intervals,
            reconciliations=reconciliations,
        )
        guardrails = SbcLinkedAuditViewGuardrails()
        identity = {
            "contract": LINKED_AUDIT_VIEW_CONTRACT,
            "schema_version": LINKED_AUDIT_VIEW_SCHEMA_VERSION,
            "view_policy": LINKED_AUDIT_VIEW_POLICY,
            "classification": RESEARCH_CLASSIFICATION,
            "source_ledger_id": series.ledger_id,
            "source_atomic_series_id": series.source_atomic_series_id,
            "instrument_identity": series.instrument_identity,
            "range_start_utc": series.range_start_utc.isoformat(),
            "range_end_utc": series.range_end_utc.isoformat(),
            "source_ids": series.source_ids,
            "views": to_primitive(views),
            "intervals": to_primitive(intervals),
            "ledger_cells": to_primitive(ledger_cells),
            "ray_rows": to_primitive(ray_rows),
            "lineage_rows": to_primitive(lineage_rows),
            "reconciliations": to_primitive(reconciliations),
            "validation_gates": to_primitive(validation_gates),
            "guardrails": to_primitive(guardrails),
        }
        return SbcLinkedAuditView(
            contract=LINKED_AUDIT_VIEW_CONTRACT,
            schema_version=LINKED_AUDIT_VIEW_SCHEMA_VERSION,
            view_policy=LINKED_AUDIT_VIEW_POLICY,
            classification=RESEARCH_CLASSIFICATION,
            audit_view_id=_canonical_hash(identity),
            source_ledger_id=series.ledger_id,
            source_atomic_series_id=series.source_atomic_series_id,
            instrument_identity=series.instrument_identity,
            range_start_utc=series.range_start_utc,
            range_end_utc=series.range_end_utc,
            source_ids=series.source_ids,
            views=views,
            intervals=intervals,
            ledger_cells=ledger_cells,
            ray_rows=ray_rows,
            lineage_rows=lineage_rows,
            reconciliations=reconciliations,
            validation_gates=validation_gates,
            guardrails=guardrails,
        )
