from __future__ import annotations

import hashlib
import html
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from .atomic_intervals import RESEARCH_CLASSIFICATION, SbcAtomicLedgerSummary
from .audit_views import (
    LINKED_AUDIT_VIEW_CONTRACT,
    LINKED_AUDIT_VIEW_POLICY,
    LINKED_AUDIT_VIEW_SCHEMA_VERSION,
    PASS,
    UNKNOWN,
    SbcLinkedAuditView,
)
from .models import to_primitive
from .multidimensional_ledger import LEDGER_AXES


AUDIT_PACKAGE_CONTRACT = "SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1"
AUDIT_PACKAGE_SCHEMA_VERSION = 1
AUDIT_PACKAGE_POLICY = "READ_ONLY_COMPARISON_EXPORT_REPLAY_V1"
AUDIT_PACKAGE_VERIFICATION_CONTRACT = "SBC_AUDIT_PACKAGE_VERIFICATION_V1"

DESCRIPTIVE_COMPARISON_ROLE = "DESCRIPTIVE_COMPARISON_ONLY"
MANUAL_RESEARCH_ANNOTATION_ROLE = "MANUAL_RESEARCH_ANNOTATION_ONLY"

AUDIT_TARGET = "AUDIT"
INTERVAL_TARGET = "INTERVAL"
CELL_TARGET = "CELL"
CLUSTER_TARGET = "CLUSTER"
VALIDATION_GATE_TARGET = "VALIDATION_GATE"
BOOKMARK_TARGET_TYPES = (
    AUDIT_TARGET,
    INTERVAL_TARGET,
    CELL_TARGET,
    CLUSTER_TARGET,
    VALIDATION_GATE_TARGET,
)

PACKAGE_TOP_LEVEL_KEYS = {
    "contract",
    "schema_version",
    "package_policy",
    "classification",
    "package_id",
    "source_audit_id",
    "source_projection_hash",
    "instrument_identity",
    "sealed_at_utc",
    "replay_recipe_hash",
    "replay_recipe",
    "source_audit",
    "comparisons",
    "bookmarks",
    "validation_gates",
    "guardrails",
}


def _portable_json_value(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("canonical audit packages cannot contain non-finite numbers")
        if value == 0.0:
            return 0
        if value.is_integer():
            return int(value)
        return value
    if isinstance(value, Mapping):
        return {
            key: _portable_json_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_portable_json_value(item) for item in value]
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest().upper()


def _portable_canonical_json(value: Any) -> str:
    return json.dumps(
        _portable_json_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _portable_canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        _portable_canonical_json(value).encode("utf-8")
    ).hexdigest().upper()


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


def _parse_utc(value: Any, label: str) -> datetime:
    text = _required_text(value, label).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO timestamp") from exc
    return _utc(parsed, label)


def _unique_digests(values: Iterable[str], label: str) -> tuple[str, ...]:
    normalized = tuple(_sha256(item, label) for item in values)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} values must be unique")
    return normalized


def _close(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-9)


def _audit_identity_from_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "contract",
        "schema_version",
        "view_policy",
        "classification",
        "audit_view_id",
        "source_ledger_id",
        "source_atomic_series_id",
        "instrument_identity",
        "range_start_utc",
        "range_end_utc",
        "source_ids",
        "views",
        "intervals",
        "ledger_cells",
        "ray_rows",
        "lineage_rows",
        "reconciliations",
        "validation_gates",
        "guardrails",
    }
    if set(payload) != required:
        raise ValueError("embedded P3 audit fields do not match the canonical contract")
    return {key: payload[key] for key in required if key != "audit_view_id"}


def _audit_identity(audit: SbcLinkedAuditView) -> dict[str, Any]:
    return _audit_identity_from_dict(audit.to_dict())


def _validate_source_audit(audit: SbcLinkedAuditView) -> None:
    if not isinstance(audit, SbcLinkedAuditView):
        raise ValueError("source audit must be SbcLinkedAuditView")
    if audit.contract != LINKED_AUDIT_VIEW_CONTRACT:
        raise ValueError("P4 requires the canonical P3 audit contract")
    if audit.schema_version != LINKED_AUDIT_VIEW_SCHEMA_VERSION:
        raise ValueError("P4 requires the canonical P3 schema version")
    if audit.view_policy != LINKED_AUDIT_VIEW_POLICY:
        raise ValueError("P4 requires the canonical P3 view policy")
    if audit.classification != RESEARCH_CLASSIFICATION:
        raise ValueError("P4 requires SOURCE_PROFILED_EXPERIMENTAL input")
    guardrails = audit.guardrails
    if not (
        guardrails.read_only
        and guardrails.timestamp_safe
        and guardrails.no_lookahead
        and guardrails.source_profiled_experimental
        and not guardrails.financially_validated
        and not guardrails.phase_included
        and not guardrails.fx_subtraction_included
        and not guardrails.confidence_included
        and not guardrails.counts_as_independent_vote
        and float(guardrails.directional_contribution) == 0.0
        and not guardrails.execution_allowed
    ):
        raise ValueError("P3 audit weakens required P4 guardrails")
    if _canonical_hash(_audit_identity(audit)) != _sha256(
        audit.audit_view_id,
        "audit_view_id",
    ):
        raise ValueError("P3 audit identity does not match its linked projection")


@dataclass(frozen=True)
class SbcAuditMetricDelta:
    favorable_guidance_units: float
    adverse_guidance_units: float
    net_guidance_units: float
    gross_activation_units: float
    scored_contribution_count: int
    unknown_contribution_count: int
    missing_evidence_count: int
    total_evidence_count: int
    unknown_magnitude_units: float | None
    scoring_coverage_ratio: float
    derivation_role: str = DESCRIPTIVE_COMPARISON_ROLE
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        if self.derivation_role != DESCRIPTIVE_COMPARISON_ROLE:
            raise ValueError("P4 deltas must remain descriptive-only")
        if self.counts_as_independent_vote:
            raise ValueError("P4 deltas cannot count as independent votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("P4 deltas cannot contribute market direction")


@dataclass(frozen=True)
class SbcAuditCellComparison:
    axis: str
    key: str
    baseline_cell_id: str | None
    comparison_cell_id: str | None
    baseline_summary: SbcAtomicLedgerSummary | None
    comparison_summary: SbcAtomicLedgerSummary | None
    delta: SbcAuditMetricDelta
    derivation_role: str = DESCRIPTIVE_COMPARISON_ROLE
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        axis = _required_text(self.axis, "axis")
        if axis not in LEDGER_AXES:
            raise ValueError(f"unknown P4 comparison axis: {axis}")
        object.__setattr__(self, "axis", axis)
        object.__setattr__(self, "key", _required_text(self.key, "key"))
        if self.baseline_cell_id is not None:
            object.__setattr__(
                self,
                "baseline_cell_id",
                _sha256(self.baseline_cell_id, "baseline_cell_id"),
            )
        if self.comparison_cell_id is not None:
            object.__setattr__(
                self,
                "comparison_cell_id",
                _sha256(self.comparison_cell_id, "comparison_cell_id"),
            )
        if self.baseline_summary is None and self.comparison_summary is None:
            raise ValueError("a P4 cell comparison requires at least one source cell")
        if self.derivation_role != DESCRIPTIVE_COMPARISON_ROLE:
            raise ValueError("P4 cell comparisons must remain descriptive-only")
        if self.counts_as_independent_vote:
            raise ValueError("P4 cell comparisons cannot count as votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("P4 cell comparisons cannot contribute market direction")


@dataclass(frozen=True)
class SbcAuditIntervalComparison:
    comparison_id: str
    baseline_interval_id: str
    comparison_interval_id: str
    baseline_summary: SbcAtomicLedgerSummary
    comparison_summary: SbcAtomicLedgerSummary
    total_delta: SbcAuditMetricDelta
    cell_comparisons: tuple[SbcAuditCellComparison, ...]
    shared_source_lineage_ids: tuple[str, ...]
    baseline_only_source_lineage_ids: tuple[str, ...]
    comparison_only_source_lineage_ids: tuple[str, ...]
    interpretation: str
    derivation_role: str = DESCRIPTIVE_COMPARISON_ROLE
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "comparison_id",
            _sha256(self.comparison_id, "comparison_id"),
        )
        object.__setattr__(
            self,
            "baseline_interval_id",
            _sha256(self.baseline_interval_id, "baseline_interval_id"),
        )
        object.__setattr__(
            self,
            "comparison_interval_id",
            _sha256(self.comparison_interval_id, "comparison_interval_id"),
        )
        if self.baseline_interval_id == self.comparison_interval_id:
            raise ValueError("baseline and comparison intervals must differ")
        for field_name in (
            "shared_source_lineage_ids",
            "baseline_only_source_lineage_ids",
            "comparison_only_source_lineage_ids",
        ):
            object.__setattr__(
                self,
                field_name,
                _unique_digests(getattr(self, field_name), "source_lineage_id"),
            )
        object.__setattr__(
            self,
            "interpretation",
            _required_text(self.interpretation, "interpretation"),
        )
        if self.derivation_role != DESCRIPTIVE_COMPARISON_ROLE:
            raise ValueError("P4 interval comparisons must remain descriptive-only")
        if self.counts_as_independent_vote:
            raise ValueError("P4 interval comparisons cannot count as votes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("P4 interval comparisons cannot contribute market direction")


@dataclass(frozen=True)
class SbcAuditBookmarkInput:
    target_type: str
    target_id: str
    label: str
    note: str
    created_at_utc: datetime

    def __post_init__(self) -> None:
        target_type = _required_text(self.target_type, "target_type").upper()
        if target_type not in BOOKMARK_TARGET_TYPES:
            raise ValueError(f"unknown bookmark target type: {target_type}")
        object.__setattr__(self, "target_type", target_type)
        object.__setattr__(self, "target_id", _required_text(self.target_id, "target_id"))
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "note", _required_text(self.note, "note"))
        object.__setattr__(
            self,
            "created_at_utc",
            _utc(self.created_at_utc, "created_at_utc"),
        )


@dataclass(frozen=True)
class SbcAuditBookmark:
    bookmark_id: str
    target_type: str
    target_id: str
    label: str
    note: str
    created_at_utc: datetime
    annotation_role: str = MANUAL_RESEARCH_ANNOTATION_ROLE
    counts_as_evidence: bool = False
    official_ml_note: bool = False
    directional_contribution: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "bookmark_id",
            _sha256(self.bookmark_id, "bookmark_id"),
        )
        if self.target_type not in BOOKMARK_TARGET_TYPES:
            raise ValueError(f"unknown bookmark target type: {self.target_type}")
        object.__setattr__(self, "target_id", _required_text(self.target_id, "target_id"))
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "note", _required_text(self.note, "note"))
        object.__setattr__(
            self,
            "created_at_utc",
            _utc(self.created_at_utc, "created_at_utc"),
        )
        if self.annotation_role != MANUAL_RESEARCH_ANNOTATION_ROLE:
            raise ValueError("P4 bookmarks must remain manual research annotations")
        if self.counts_as_evidence or self.official_ml_note:
            raise ValueError("P4 bookmarks cannot become evidence or official ML notes")
        if float(self.directional_contribution) != 0.0:
            raise ValueError("P4 bookmarks cannot contribute market direction")


@dataclass(frozen=True)
class SbcAuditPackageValidationGate:
    gate_id: str
    state: str
    label: str
    detail: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "gate_id", _required_text(self.gate_id, "gate_id"))
        if self.state not in (PASS, UNKNOWN):
            raise ValueError("P4 package gates can only publish PASS or UNKNOWN")
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "detail", _required_text(self.detail, "detail"))


@dataclass(frozen=True)
class SbcAuditPackageGuardrails:
    research_only: bool = True
    read_only: bool = True
    timestamp_safe: bool = True
    no_lookahead: bool = True
    source_profiled_experimental: bool = True
    financially_validated: bool = False
    descriptive_comparison_only: bool = True
    manual_annotations_only: bool = True
    replay_required_for_verification: bool = True
    phase_included: bool = False
    fx_subtraction_included: bool = False
    confidence_included: bool = False
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0
    execution_allowed: bool = False
    blocked_capabilities: tuple[str, ...] = (
        "CROSS_AUDIT_ARITHMETIC",
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
class SbcReproducibleAuditPackage:
    contract: str
    schema_version: int
    package_policy: str
    classification: str
    package_id: str
    source_audit_id: str
    source_projection_hash: str
    instrument_identity: str
    sealed_at_utc: datetime
    replay_recipe_hash: str
    replay_recipe: dict[str, Any]
    source_audit: dict[str, Any]
    comparisons: tuple[SbcAuditIntervalComparison, ...]
    bookmarks: tuple[SbcAuditBookmark, ...]
    validation_gates: tuple[SbcAuditPackageValidationGate, ...]
    guardrails: SbcAuditPackageGuardrails

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcAuditPackageVerification:
    contract: str
    state: str
    package_id: str | None
    source_audit_id: str | None
    structural_hash_match: bool
    source_projection_match: bool
    replay_recipe_match: bool
    replay_audit_match: bool
    replay_package_match: bool
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


def _zero_summary() -> SbcAtomicLedgerSummary:
    return SbcAtomicLedgerSummary(
        favorable_guidance_units=0.0,
        adverse_guidance_units=0.0,
        net_guidance_units=0.0,
        gross_activation_units=0.0,
        scored_contribution_count=0,
        unknown_contribution_count=0,
        missing_evidence_count=0,
        total_evidence_count=0,
        unknown_magnitude_units=0.0,
        scoring_coverage_ratio=0.0,
    )


def _delta(
    baseline: SbcAtomicLedgerSummary | None,
    comparison: SbcAtomicLedgerSummary | None,
) -> SbcAuditMetricDelta:
    baseline = baseline or _zero_summary()
    comparison = comparison or _zero_summary()
    unknown_delta = (
        None
        if baseline.unknown_magnitude_units is None
        or comparison.unknown_magnitude_units is None
        else (
            comparison.unknown_magnitude_units - baseline.unknown_magnitude_units
        )
    )
    return SbcAuditMetricDelta(
        favorable_guidance_units=(
            comparison.favorable_guidance_units - baseline.favorable_guidance_units
        ),
        adverse_guidance_units=(
            comparison.adverse_guidance_units - baseline.adverse_guidance_units
        ),
        net_guidance_units=(
            comparison.net_guidance_units - baseline.net_guidance_units
        ),
        gross_activation_units=(
            comparison.gross_activation_units - baseline.gross_activation_units
        ),
        scored_contribution_count=(
            comparison.scored_contribution_count - baseline.scored_contribution_count
        ),
        unknown_contribution_count=(
            comparison.unknown_contribution_count
            - baseline.unknown_contribution_count
        ),
        missing_evidence_count=(
            comparison.missing_evidence_count - baseline.missing_evidence_count
        ),
        total_evidence_count=(
            comparison.total_evidence_count - baseline.total_evidence_count
        ),
        unknown_magnitude_units=unknown_delta,
        scoring_coverage_ratio=(
            comparison.scoring_coverage_ratio - baseline.scoring_coverage_ratio
        ),
    )


def _bookmark_targets(audit: SbcLinkedAuditView) -> dict[str, set[str]]:
    return {
        AUDIT_TARGET: {audit.audit_view_id},
        INTERVAL_TARGET: {item.interval_id for item in audit.intervals},
        CELL_TARGET: {item.cell_id for item in audit.ledger_cells},
        CLUSTER_TARGET: {item.cluster_id for item in audit.ray_rows},
        VALIDATION_GATE_TARGET: {
            item.gate_id for item in audit.validation_gates
        },
    }


def _compile_bookmark(
    audit: SbcLinkedAuditView,
    value: SbcAuditBookmarkInput,
) -> SbcAuditBookmark:
    targets = _bookmark_targets(audit)
    if value.target_id not in targets[value.target_type]:
        raise ValueError(
            f"bookmark target does not exist in source audit: "
            f"{value.target_type}:{value.target_id}"
        )
    identity = {
        "source_audit_id": audit.audit_view_id,
        "target_type": value.target_type,
        "target_id": value.target_id,
        "label": value.label,
        "note": value.note,
        "created_at_utc": value.created_at_utc.isoformat(),
        "annotation_role": MANUAL_RESEARCH_ANNOTATION_ROLE,
    }
    return SbcAuditBookmark(
        bookmark_id=_portable_canonical_hash(identity),
        target_type=value.target_type,
        target_id=value.target_id,
        label=value.label,
        note=value.note,
        created_at_utc=value.created_at_utc,
    )


def _compile_comparison(
    audit: SbcLinkedAuditView,
    baseline_interval_id: str,
    comparison_interval_id: str,
) -> SbcAuditIntervalComparison:
    intervals = {item.interval_id: item for item in audit.intervals}
    baseline = intervals[baseline_interval_id]
    comparison = intervals[comparison_interval_id]
    baseline_cells = {
        (item.axis, item.key): item
        for item in audit.ledger_cells
        if item.interval_id == baseline.interval_id
    }
    comparison_cells = {
        (item.axis, item.key): item
        for item in audit.ledger_cells
        if item.interval_id == comparison.interval_id
    }
    cell_rows = []
    for axis, key in sorted(
        set(baseline_cells) | set(comparison_cells),
        key=lambda item: (LEDGER_AXES.index(item[0]), item[1]),
    ):
        baseline_cell = baseline_cells.get((axis, key))
        comparison_cell = comparison_cells.get((axis, key))
        cell_rows.append(
            SbcAuditCellComparison(
                axis=axis,
                key=key,
                baseline_cell_id=(
                    baseline_cell.cell_id if baseline_cell is not None else None
                ),
                comparison_cell_id=(
                    comparison_cell.cell_id if comparison_cell is not None else None
                ),
                baseline_summary=(
                    baseline_cell.summary if baseline_cell is not None else None
                ),
                comparison_summary=(
                    comparison_cell.summary if comparison_cell is not None else None
                ),
                delta=_delta(
                    baseline_cell.summary if baseline_cell is not None else None,
                    comparison_cell.summary if comparison_cell is not None else None,
                ),
            )
        )

    baseline_lineage = {
        item.source_lineage_id
        for item in audit.lineage_rows
        if item.interval_id == baseline.interval_id
    }
    comparison_lineage = {
        item.source_lineage_id
        for item in audit.lineage_rows
        if item.interval_id == comparison.interval_id
    }
    identity = {
        "source_audit_id": audit.audit_view_id,
        "baseline_interval_id": baseline.interval_id,
        "comparison_interval_id": comparison.interval_id,
        "baseline_summary": to_primitive(baseline.total_summary),
        "comparison_summary": to_primitive(comparison.total_summary),
        "total_delta": to_primitive(
            _delta(baseline.total_summary, comparison.total_summary)
        ),
        "cell_comparisons": to_primitive(tuple(cell_rows)),
        "shared_source_lineage_ids": tuple(
            sorted(baseline_lineage & comparison_lineage)
        ),
        "baseline_only_source_lineage_ids": tuple(
            sorted(baseline_lineage - comparison_lineage)
        ),
        "comparison_only_source_lineage_ids": tuple(
            sorted(comparison_lineage - baseline_lineage)
        ),
        "derivation_role": DESCRIPTIVE_COMPARISON_ROLE,
    }
    return SbcAuditIntervalComparison(
        comparison_id=_portable_canonical_hash(identity),
        baseline_interval_id=baseline.interval_id,
        comparison_interval_id=comparison.interval_id,
        baseline_summary=baseline.total_summary,
        comparison_summary=comparison.total_summary,
        total_delta=_delta(baseline.total_summary, comparison.total_summary),
        cell_comparisons=tuple(cell_rows),
        shared_source_lineage_ids=tuple(
            sorted(baseline_lineage & comparison_lineage)
        ),
        baseline_only_source_lineage_ids=tuple(
            sorted(baseline_lineage - comparison_lineage)
        ),
        comparison_only_source_lineage_ids=tuple(
            sorted(comparison_lineage - baseline_lineage)
        ),
        interpretation=(
            "All deltas are comparison interval minus baseline interval. "
            "They describe ledger differences only and are not market direction, "
            "confidence, performance, or trade signals."
        ),
    )


def _validation_gates(
    *,
    source_audit: SbcLinkedAuditView,
    comparison_count: int,
    bookmark_count: int,
) -> tuple[SbcAuditPackageValidationGate, ...]:
    unknown_count = sum(
        item.total_summary.unknown_contribution_count
        for item in source_audit.intervals
    )
    return (
        SbcAuditPackageValidationGate(
            "SOURCE_AUDIT_LOCKS",
            PASS,
            "Canonical P3 source",
            "The package embeds one canonical, linked, read-only P3 projection.",
        ),
        SbcAuditPackageValidationGate(
            "COMPARISON_LINKS",
            PASS,
            "Comparison links",
            (
                f"{comparison_count} comparison(s) preserve their source "
                "interval, cell, cluster, and lineage identities."
            ),
        ),
        SbcAuditPackageValidationGate(
            "REPLAY_RECIPE",
            PASS,
            "Replay recipe",
            "Explicit Chakra capture inputs and P4 selections are sealed for replay.",
        ),
        SbcAuditPackageValidationGate(
            "MANUAL_BOOKMARKS",
            PASS,
            "Manual research bookmarks",
            (
                f"{bookmark_count} bookmark(s) are annotation-only and cannot "
                "become evidence or official ML notes."
            ),
        ),
        SbcAuditPackageValidationGate(
            "UNKNOWN_EVIDENCE",
            UNKNOWN if unknown_count else PASS,
            "Unknown evidence",
            (
                f"{unknown_count} source contribution(s) remain explicitly unknown."
                if unknown_count
                else "No unknown contribution is present in the source audit."
            ),
        ),
        SbcAuditPackageValidationGate(
            "FINANCIAL_INTERPRETATION",
            UNKNOWN,
            "Financial interpretation",
            "Comparison deltas have no prospective financial validation.",
        ),
        SbcAuditPackageValidationGate(
            "EXECUTION_LOCK",
            PASS,
            "Execution lock",
            "Inference, trade output, and MT5 execution remain blocked.",
        ),
    )


class SbcAuditComparisonPackageCompiler:
    def compile(
        self,
        source_audit: SbcLinkedAuditView,
        *,
        baseline_interval_id: str,
        comparison_interval_ids: Sequence[str],
        bookmark_inputs: Sequence[SbcAuditBookmarkInput],
        sealed_at_utc: datetime,
        replay_recipe: Mapping[str, Any],
    ) -> SbcReproducibleAuditPackage:
        _validate_source_audit(source_audit)
        baseline_id = _sha256(baseline_interval_id, "baseline_interval_id")
        requested_comparisons = _unique_digests(
            comparison_interval_ids,
            "comparison_interval_id",
        )
        if not requested_comparisons:
            raise ValueError("P4 requires at least one comparison interval")
        if baseline_id in requested_comparisons:
            raise ValueError("baseline interval cannot also be a comparison interval")

        interval_order = {
            item.interval_id: index for index, item in enumerate(source_audit.intervals)
        }
        if baseline_id not in interval_order:
            raise ValueError("baseline interval does not exist in the source audit")
        missing = set(requested_comparisons) - set(interval_order)
        if missing:
            raise ValueError("comparison interval does not exist in the source audit")
        comparison_ids = tuple(
            sorted(requested_comparisons, key=interval_order.__getitem__)
        )
        comparisons = tuple(
            _compile_comparison(source_audit, baseline_id, item)
            for item in comparison_ids
        )
        bookmarks = tuple(
            sorted(
                (
                    _compile_bookmark(source_audit, item)
                    for item in bookmark_inputs
                ),
                key=lambda item: item.bookmark_id,
            )
        )
        if len({item.bookmark_id for item in bookmarks}) != len(bookmarks):
            raise ValueError("duplicate bookmarks are not allowed")

        sealed = _utc(sealed_at_utc, "sealed_at_utc")
        recipe = json.loads(_portable_canonical_json(dict(replay_recipe)))
        replay_recipe_hash = _portable_canonical_hash(recipe)
        source_payload = source_audit.to_dict()
        source_projection_hash = _portable_canonical_hash(source_payload)
        validation_gates = _validation_gates(
            source_audit=source_audit,
            comparison_count=len(comparisons),
            bookmark_count=len(bookmarks),
        )
        guardrails = SbcAuditPackageGuardrails()
        identity = {
            "contract": AUDIT_PACKAGE_CONTRACT,
            "schema_version": AUDIT_PACKAGE_SCHEMA_VERSION,
            "package_policy": AUDIT_PACKAGE_POLICY,
            "classification": RESEARCH_CLASSIFICATION,
            "source_audit_id": source_audit.audit_view_id,
            "source_projection_hash": source_projection_hash,
            "instrument_identity": source_audit.instrument_identity,
            "sealed_at_utc": sealed.isoformat(),
            "replay_recipe_hash": replay_recipe_hash,
            "replay_recipe": recipe,
            "source_audit": source_payload,
            "comparisons": to_primitive(comparisons),
            "bookmarks": to_primitive(bookmarks),
            "validation_gates": to_primitive(validation_gates),
            "guardrails": to_primitive(guardrails),
        }
        return SbcReproducibleAuditPackage(
            contract=AUDIT_PACKAGE_CONTRACT,
            schema_version=AUDIT_PACKAGE_SCHEMA_VERSION,
            package_policy=AUDIT_PACKAGE_POLICY,
            classification=RESEARCH_CLASSIFICATION,
            package_id=_portable_canonical_hash(identity),
            source_audit_id=source_audit.audit_view_id,
            source_projection_hash=source_projection_hash,
            instrument_identity=source_audit.instrument_identity,
            sealed_at_utc=sealed,
            replay_recipe_hash=replay_recipe_hash,
            replay_recipe=recipe,
            source_audit=source_payload,
            comparisons=comparisons,
            bookmarks=bookmarks,
            validation_gates=validation_gates,
            guardrails=guardrails,
        )


def validate_audit_package_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ValueError("audit package must be an object")
    if set(payload) != PACKAGE_TOP_LEVEL_KEYS:
        raise ValueError("audit package fields do not match the canonical P4 contract")
    if payload["contract"] != AUDIT_PACKAGE_CONTRACT:
        raise ValueError("unsupported audit package contract")
    if payload["schema_version"] != AUDIT_PACKAGE_SCHEMA_VERSION:
        raise ValueError("unsupported audit package schema version")
    if payload["package_policy"] != AUDIT_PACKAGE_POLICY:
        raise ValueError("unsupported audit package policy")
    if payload["classification"] != RESEARCH_CLASSIFICATION:
        raise ValueError("audit package classification must remain experimental")

    package_id = _sha256(payload["package_id"], "package_id")
    identity = {key: payload[key] for key in PACKAGE_TOP_LEVEL_KEYS if key != "package_id"}
    if _portable_canonical_hash(identity) != package_id:
        raise ValueError("audit package hash does not match its contents")
    if _portable_canonical_hash(payload["replay_recipe"]) != _sha256(
        payload["replay_recipe_hash"],
        "replay_recipe_hash",
    ):
        raise ValueError("replay recipe hash does not match its contents")
    if not isinstance(payload["source_audit"], dict):
        raise ValueError("source_audit must be an object")
    source_audit = payload["source_audit"]
    if source_audit.get("contract") != LINKED_AUDIT_VIEW_CONTRACT:
        raise ValueError("embedded source audit is not the canonical P3 contract")
    embedded_audit_id = _sha256(
        source_audit.get("audit_view_id"),
        "embedded audit_view_id",
    )
    if embedded_audit_id != _sha256(
        payload["source_audit_id"],
        "source_audit_id",
    ):
        raise ValueError("source_audit_id does not match the embedded P3 audit")
    if _portable_canonical_hash(source_audit) != _sha256(
        payload["source_projection_hash"],
        "source_projection_hash",
    ):
        raise ValueError("source projection hash does not match the embedded P3 audit")

    guardrails = payload.get("guardrails")
    if not isinstance(guardrails, dict) or not (
        guardrails.get("research_only") is True
        and guardrails.get("read_only") is True
        and guardrails.get("timestamp_safe") is True
        and guardrails.get("no_lookahead") is True
        and guardrails.get("source_profiled_experimental") is True
        and guardrails.get("financially_validated") is False
        and guardrails.get("descriptive_comparison_only") is True
        and guardrails.get("manual_annotations_only") is True
        and guardrails.get("replay_required_for_verification") is True
        and guardrails.get("phase_included") is False
        and guardrails.get("fx_subtraction_included") is False
        and guardrails.get("confidence_included") is False
        and guardrails.get("counts_as_independent_vote") is False
        and float(guardrails.get("directional_contribution", 1.0)) == 0.0
        and guardrails.get("execution_allowed") is False
    ):
        raise ValueError("audit package guardrails are weakened")

    interval_ids = {
        _sha256(item["interval_id"], "interval_id")
        for item in source_audit.get("intervals", ())
    }
    cell_ids = {
        _sha256(item["cell_id"], "cell_id")
        for item in source_audit.get("ledger_cells", ())
    }
    cluster_ids = {
        _sha256(item["cluster_id"], "cluster_id")
        for item in source_audit.get("ray_rows", ())
    }
    gate_ids = {
        _required_text(item["gate_id"], "gate_id")
        for item in source_audit.get("validation_gates", ())
    }
    target_sets = {
        AUDIT_TARGET: {source_audit["audit_view_id"]},
        INTERVAL_TARGET: interval_ids,
        CELL_TARGET: cell_ids,
        CLUSTER_TARGET: cluster_ids,
        VALIDATION_GATE_TARGET: gate_ids,
    }

    comparisons = payload.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        raise ValueError("audit package requires at least one comparison")
    comparison_ids: set[str] = set()
    for comparison in comparisons:
        comparison_id = _sha256(comparison.get("comparison_id"), "comparison_id")
        if comparison_id in comparison_ids:
            raise ValueError("comparison IDs must be unique")
        comparison_ids.add(comparison_id)
        baseline_id = _sha256(
            comparison.get("baseline_interval_id"),
            "baseline_interval_id",
        )
        candidate_id = _sha256(
            comparison.get("comparison_interval_id"),
            "comparison_interval_id",
        )
        if baseline_id not in interval_ids or candidate_id not in interval_ids:
            raise ValueError("comparison links to an unknown source interval")
        if baseline_id == candidate_id:
            raise ValueError("comparison repeats its baseline interval")
        if comparison.get("derivation_role") != DESCRIPTIVE_COMPARISON_ROLE:
            raise ValueError("comparison derivation role is not descriptive-only")
        if comparison.get("counts_as_independent_vote") is not False:
            raise ValueError("comparison cannot count as a vote")
        if float(comparison.get("directional_contribution", 1.0)) != 0.0:
            raise ValueError("comparison cannot contribute market direction")

    bookmarks = payload.get("bookmarks")
    if not isinstance(bookmarks, list):
        raise ValueError("bookmarks must be an array")
    bookmark_ids: set[str] = set()
    for bookmark in bookmarks:
        bookmark_id = _sha256(bookmark.get("bookmark_id"), "bookmark_id")
        if bookmark_id in bookmark_ids:
            raise ValueError("bookmark IDs must be unique")
        bookmark_ids.add(bookmark_id)
        target_type = _required_text(
            bookmark.get("target_type"),
            "target_type",
        )
        if target_type not in target_sets:
            raise ValueError("bookmark has an unknown target type")
        if bookmark.get("target_id") not in target_sets[target_type]:
            raise ValueError("bookmark links to an unknown P3 target")
        if bookmark.get("annotation_role") != MANUAL_RESEARCH_ANNOTATION_ROLE:
            raise ValueError("bookmark is not marked as manual annotation")
        if bookmark.get("counts_as_evidence") is not False:
            raise ValueError("bookmark cannot count as evidence")
        if bookmark.get("official_ml_note") is not False:
            raise ValueError("bookmark cannot be an official ML note")
        if float(bookmark.get("directional_contribution", 1.0)) != 0.0:
            raise ValueError("bookmark cannot contribute market direction")


def verify_audit_package_replay(
    payload: Any,
    replayed_payload: Any | None,
) -> SbcAuditPackageVerification:
    errors: list[str] = []
    structural_hash_match = False
    source_projection_match = False
    replay_recipe_match = False
    replay_audit_match = False
    replay_package_match = False
    package_id = None
    source_audit_id = None
    try:
        validate_audit_package_payload(payload)
        package_id = payload["package_id"]
        source_audit_id = payload["source_audit_id"]
        structural_hash_match = True
        source_projection_match = True
        replay_recipe_match = True
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))

    if not errors and replayed_payload is not None:
        try:
            validate_audit_package_payload(replayed_payload)
            replay_audit_match = (
                replayed_payload["source_audit_id"] == source_audit_id
                and replayed_payload["source_projection_hash"]
                == payload["source_projection_hash"]
                and replayed_payload["source_audit"] == payload["source_audit"]
            )
            replay_package_match = replayed_payload == payload
            if not replay_audit_match:
                errors.append("replayed P3 audit does not match the sealed source audit")
            if not replay_package_match:
                errors.append("replayed P4 package does not match the sealed package")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"replayed package is invalid: {exc}")
    elif not errors:
        errors.append("replay was not performed")

    return SbcAuditPackageVerification(
        contract=AUDIT_PACKAGE_VERIFICATION_CONTRACT,
        state=PASS if not errors else "FAIL",
        package_id=package_id,
        source_audit_id=source_audit_id,
        structural_hash_match=structural_hash_match,
        source_projection_match=source_projection_match,
        replay_recipe_match=replay_recipe_match,
        replay_audit_match=replay_audit_match,
        replay_package_match=replay_package_match,
        errors=tuple(errors),
    )


def render_audit_package_html(package: SbcReproducibleAuditPackage) -> str:
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    comparison_sections = []
    for comparison in package.comparisons:
        rows = "".join(
            (
                "<tr>"
                f"<td>{esc(item.axis)}</td>"
                f"<td>{esc(item.key)}</td>"
                f"<td>{esc(item.delta.net_guidance_units)}</td>"
                f"<td>{esc(item.delta.gross_activation_units)}</td>"
                f"<td>{esc(item.delta.unknown_contribution_count)}</td>"
                "</tr>"
            )
            for item in comparison.cell_comparisons
        )
        comparison_sections.append(
            (
                "<section>"
                f"<h2>Comparison {esc(comparison.comparison_id[:12])}</h2>"
                f"<p><strong>Baseline:</strong> "
                f"{esc(comparison.baseline_interval_id)}</p>"
                f"<p><strong>Comparison:</strong> "
                f"{esc(comparison.comparison_interval_id)}</p>"
                f"<p class=\"warning\">{esc(comparison.interpretation)}</p>"
                "<table><thead><tr><th>Axis</th><th>Key</th>"
                "<th>Net delta</th><th>Gross delta</th>"
                f"<th>Unknown delta</th></tr></thead><tbody>{rows}</tbody></table>"
                "</section>"
            )
        )

    bookmark_rows = "".join(
        (
            "<tr>"
            f"<td>{esc(item.target_type)}</td>"
            f"<td>{esc(item.target_id)}</td>"
            f"<td>{esc(item.label)}</td>"
            f"<td>{esc(item.note)}</td>"
            "</tr>"
        )
        for item in package.bookmarks
    )
    gate_rows = "".join(
        (
            "<tr>"
            f"<td>{esc(item.state)}</td>"
            f"<td>{esc(item.label)}</td>"
            f"<td>{esc(item.detail)}</td>"
            "</tr>"
        )
        for item in package.validation_gates
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SBC Audit Package {esc(package.package_id[:12])}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 32px; color: #20252a; }}
h1, h2 {{ margin: 0 0 12px; }}
header, section {{ margin: 0 0 28px; }}
.meta {{ display: grid; grid-template-columns: 180px 1fr; gap: 5px 12px; }}
.warning {{ padding: 10px; border-left: 4px solid #b27b22; background: #fff7e7; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
th, td {{ padding: 7px; border: 1px solid #ccd1d5; text-align: left; vertical-align: top; }}
th {{ background: #eef1f3; }}
code {{ overflow-wrap: anywhere; }}
</style>
</head>
<body>
<header>
<h1>Reproducible SBC Audit Package</h1>
<p class="warning">Research-only descriptive comparison. No market direction,
confidence, official ML note, trade output, or execution authority.</p>
<div class="meta">
<strong>Package ID</strong><code>{esc(package.package_id)}</code>
<strong>Source audit</strong><code>{esc(package.source_audit_id)}</code>
<strong>Instrument</strong><span>{esc(package.instrument_identity)}</span>
<strong>Sealed UTC</strong><span>{esc(package.sealed_at_utc.isoformat())}</span>
<strong>Projection hash</strong><code>{esc(package.source_projection_hash)}</code>
<strong>Replay recipe</strong><code>{esc(package.replay_recipe_hash)}</code>
</div>
</header>
{''.join(comparison_sections)}
<section>
<h2>Manual research bookmarks</h2>
<table><thead><tr><th>Target</th><th>ID</th><th>Label</th><th>Note</th></tr></thead>
<tbody>{bookmark_rows or '<tr><td colspan="4">None</td></tr>'}</tbody></table>
</section>
<section>
<h2>Validation gates</h2>
<table><thead><tr><th>State</th><th>Gate</th><th>Detail</th></tr></thead>
<tbody>{gate_rows}</tbody></table>
</section>
</body>
</html>
"""
