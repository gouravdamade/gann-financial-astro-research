from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from .chakra_lab import ChakraLabSnapshot
from .models import to_primitive
from .vedha import VedhaContribution, VedhaGuidanceReport


ATOMIC_INTERVAL_CONTRACT = "SBC_ATOMIC_INTERVAL_SERIES_V1"
ATOMIC_INTERVAL_SCHEMA_VERSION = 1
ATOMIC_INTERVAL_POLICY = "EXPLICIT_BOUNDARY_STATES_V1"
ATOMIC_CONTRIBUTION_CONTRACT = "SBC_ATOMIC_CONTRIBUTION_V1"
ATOMIC_SOURCE_LINEAGE_CONTRACT = "SBC_ATOMIC_SOURCE_LINEAGE_V1"
RESEARCH_CLASSIFICATION = "SOURCE_PROFILED_EXPERIMENTAL"


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _required_text(value: Any, label: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{label} is required")
    return normalized


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


@dataclass(frozen=True)
class SbcAtomicContribution:
    source_lineage_id: str
    body: str
    source_nakshatra: str
    vedha_direction: str
    target_row: int
    target_column: int
    target_layer: str
    target_value: str
    target_witness_set_id: str
    target_evidence_status: str
    nature: str
    effective_multiplier: float | None
    signed_guidance_units: float | None
    status: str
    explanation: str
    citation_source_ids: tuple[str, ...]
    unknown_reason: str | None = None
    contribution_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_lineage_id",
            _sha256(self.source_lineage_id, "source_lineage_id"),
        )
        for field_name in (
            "body",
            "source_nakshatra",
            "vedha_direction",
            "target_layer",
            "target_value",
            "target_witness_set_id",
            "target_evidence_status",
            "nature",
            "status",
            "explanation",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name),
            )
        if int(self.target_row) < 0 or int(self.target_column) < 0:
            raise ValueError("target coordinates must be non-negative")
        object.__setattr__(self, "target_row", int(self.target_row))
        object.__setattr__(self, "target_column", int(self.target_column))
        object.__setattr__(
            self,
            "effective_multiplier",
            _finite_or_none(self.effective_multiplier, "effective_multiplier"),
        )
        if self.effective_multiplier is not None and self.effective_multiplier <= 0:
            raise ValueError("effective_multiplier must be positive")
        object.__setattr__(
            self,
            "signed_guidance_units",
            _finite_or_none(self.signed_guidance_units, "signed_guidance_units"),
        )
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
                raise ValueError("SCORED contributions require signed guidance units")
            object.__setattr__(
                self,
                "unknown_reason",
                _required_text(self.unknown_reason, "unknown_reason"),
            )
        else:
            if self.status != "SCORED":
                raise ValueError("numeric contributions must use status SCORED")
            if self.unknown_reason is not None:
                raise ValueError("scored contributions cannot carry unknown_reason")
        contribution_identity = {
            "contract": ATOMIC_CONTRIBUTION_CONTRACT,
            "source_lineage_id": self.source_lineage_id,
            "nature": self.nature,
            "effective_multiplier": self.effective_multiplier,
            "signed_guidance_units": self.signed_guidance_units,
            "status": self.status,
            "explanation": self.explanation,
            "unknown_reason": self.unknown_reason,
        }
        object.__setattr__(
            self,
            "contribution_id",
            _canonical_hash(contribution_identity),
        )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcAtomicProfileIdentity:
    foundation_profile_id: str
    foundation_profile_hash: str
    grid_profile_id: str
    grid_profile_hash: str
    vedha_profile_id: str
    vedha_profile_hash: str
    guidance_model_id: str

    def __post_init__(self) -> None:
        for field_name in (
            "foundation_profile_id",
            "grid_profile_id",
            "vedha_profile_id",
            "guidance_model_id",
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

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcAtomicBoundary:
    starts_at_utc: datetime
    evidence_cutoff_utc: datetime
    boundary_reason: str
    snapshot_id: str
    foundation_profile_id: str
    foundation_profile_hash: str
    grid_profile_id: str
    grid_profile_hash: str
    vedha_profile_id: str
    vedha_profile_hash: str
    guidance_model_id: str
    source_ids: tuple[str, ...]
    guidance_available: bool
    contributions: tuple[SbcAtomicContribution, ...] = ()
    missing_evidence_ids: tuple[str, ...] = ()
    boundary_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "starts_at_utc", _utc(self.starts_at_utc, "starts_at_utc")
        )
        object.__setattr__(
            self,
            "evidence_cutoff_utc",
            _utc(self.evidence_cutoff_utc, "evidence_cutoff_utc"),
        )
        if self.evidence_cutoff_utc > self.starts_at_utc:
            raise ValueError("evidence cutoff cannot be later than the boundary start")
        for field_name in (
            "boundary_reason",
            "foundation_profile_id",
            "grid_profile_id",
            "vedha_profile_id",
            "guidance_model_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name),
            )
        object.__setattr__(self, "snapshot_id", _sha256(self.snapshot_id, "snapshot_id"))
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
        object.__setattr__(
            self,
            "source_ids",
            _unique_sorted(self.source_ids, "source_ids", required=True),
        )
        contributions = tuple(
            sorted(self.contributions, key=lambda item: item.contribution_id)
        )
        contribution_ids = tuple(item.contribution_id for item in contributions)
        if len(contribution_ids) != len(set(contribution_ids)):
            raise ValueError("atomic boundary contributions must be unique")
        object.__setattr__(self, "contributions", contributions)
        object.__setattr__(
            self,
            "missing_evidence_ids",
            _unique_sorted(self.missing_evidence_ids, "missing_evidence_ids"),
        )
        if not isinstance(self.guidance_available, bool):
            raise ValueError("guidance_available must be boolean")
        if not self.guidance_available and self.contributions:
            raise ValueError("unavailable guidance cannot contain contributions")
        if not self.guidance_available and not self.missing_evidence_ids:
            raise ValueError(
                "unavailable guidance requires at least one missing_evidence_id"
            )
        identity = {
            "contract": ATOMIC_INTERVAL_CONTRACT,
            "starts_at_utc": self.starts_at_utc.isoformat(),
            "evidence_cutoff_utc": self.evidence_cutoff_utc.isoformat(),
            "boundary_reason": self.boundary_reason,
            "snapshot_id": self.snapshot_id,
            "profiles": self.profile_identity.to_dict(),
            "source_ids": self.source_ids,
            "guidance_available": self.guidance_available,
            "contribution_ids": contribution_ids,
            "missing_evidence_ids": self.missing_evidence_ids,
        }
        object.__setattr__(self, "boundary_id", _canonical_hash(identity))

    @property
    def profile_identity(self) -> SbcAtomicProfileIdentity:
        return SbcAtomicProfileIdentity(
            foundation_profile_id=self.foundation_profile_id,
            foundation_profile_hash=self.foundation_profile_hash,
            grid_profile_id=self.grid_profile_id,
            grid_profile_hash=self.grid_profile_hash,
            vedha_profile_id=self.vedha_profile_id,
            vedha_profile_hash=self.vedha_profile_hash,
            guidance_model_id=self.guidance_model_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcAtomicLedgerSummary:
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

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcAtomicInterval:
    interval_id: str
    classification: str
    start_utc: datetime
    end_utc: datetime
    evidence_cutoff_utc: datetime
    start_boundary_id: str
    boundary_reason: str
    snapshot_id: str
    profile_identity: SbcAtomicProfileIdentity
    source_ids: tuple[str, ...]
    guidance_available: bool
    contributions: tuple[SbcAtomicContribution, ...]
    missing_evidence_ids: tuple[str, ...]
    ledger: SbcAtomicLedgerSummary

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class SbcAtomicIntervalGuardrails:
    research_only: bool = True
    timestamp_safe: bool = True
    no_lookahead: bool = True
    source_profiled_experimental: bool = True
    counts_as_independent_vote: bool = False
    directional_contribution: float = 0.0
    execution_allowed: bool = False
    blocked_capabilities: tuple[str, ...] = (
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
class SbcAtomicIntervalSeries:
    contract: str
    schema_version: int
    interval_policy: str
    classification: str
    series_id: str
    range_start_utc: datetime
    range_end_utc: datetime
    profile_identity: SbcAtomicProfileIdentity
    source_ids: tuple[str, ...]
    intervals: tuple[SbcAtomicInterval, ...]
    guardrails: SbcAtomicIntervalGuardrails

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


def contribution_from_vedha(
    report: VedhaGuidanceReport,
    contribution: VedhaContribution,
) -> SbcAtomicContribution:
    citation_source_ids = tuple(
        dict.fromkeys(item.source_id for item in contribution.target.citations)
    )
    source_identity = {
        "contract": ATOMIC_SOURCE_LINEAGE_CONTRACT,
        "vedha_profile_id": report.vedha_profile_id,
        "vedha_profile_hash": report.vedha_profile_hash,
        "grid_profile_id": report.grid_profile_id,
        "grid_profile_hash": report.grid_profile_hash,
        "guidance_model_id": report.guidance_model_id,
        "body": contribution.body,
        "source_nakshatra": contribution.source_nakshatra,
        "vedha_direction": contribution.direction.value,
        "target": {
            "row": contribution.target.row,
            "column": contribution.target.column,
            "layer": contribution.target.layer,
            "value": contribution.target.value,
            "witness_set_id": contribution.target.witness_set_id,
            "evidence_status": contribution.target.evidence_status,
        },
        "citation_source_ids": citation_source_ids,
    }
    source_lineage_id = _canonical_hash(source_identity)
    return SbcAtomicContribution(
        source_lineage_id=source_lineage_id,
        body=contribution.body,
        source_nakshatra=contribution.source_nakshatra,
        vedha_direction=contribution.direction.value,
        target_row=contribution.target.row,
        target_column=contribution.target.column,
        target_layer=contribution.target.layer,
        target_value=contribution.target.value,
        target_witness_set_id=contribution.target.witness_set_id,
        target_evidence_status=contribution.target.evidence_status,
        nature=contribution.nature.value,
        effective_multiplier=contribution.effective_multiplier,
        signed_guidance_units=contribution.signed_guidance_units,
        status=contribution.status,
        explanation=contribution.explanation,
        citation_source_ids=citation_source_ids,
        unknown_reason=(
            contribution.explanation
            if contribution.signed_guidance_units is None
            else None
        ),
    )


def boundary_from_chakra_snapshot(
    snapshot: ChakraLabSnapshot,
    *,
    boundary_reason: str,
    missing_evidence_ids: tuple[str, ...] = (),
    unavailable_vedha_profile_id: str | None = None,
    unavailable_vedha_profile_hash: str | None = None,
    unavailable_guidance_model_id: str | None = None,
) -> SbcAtomicBoundary:
    guardrails = snapshot.guardrails
    if not (
        guardrails.read_only
        and guardrails.timestamp_safe
        and guardrails.no_lookahead
        and not guardrails.execution_allowed
        and not guardrails.market_data_included
        and not guardrails.financially_validated
        and guardrails.guidance_only
    ):
        raise ValueError("Chakra snapshot weakens required atomic interval guardrails")

    guidance = snapshot.guidance
    missing = list(missing_evidence_ids)
    missing.extend(
        f"ACTOR:{item.body}:{item.status}"
        for item in snapshot.actor_readiness
        if item.requested and item.status != "READY"
    )
    if guidance is None:
        missing.append("VEDHA_GUIDANCE_NOT_AVAILABLE")
        vedha_profile_id = _required_text(
            unavailable_vedha_profile_id,
            "unavailable_vedha_profile_id",
        )
        vedha_profile_hash = _sha256(
            unavailable_vedha_profile_hash,
            "unavailable_vedha_profile_hash",
        )
        guidance_model_id = _required_text(
            unavailable_guidance_model_id,
            "unavailable_guidance_model_id",
        )
        contributions: tuple[SbcAtomicContribution, ...] = ()
    else:
        if any(
            value is not None
            for value in (
                unavailable_vedha_profile_id,
                unavailable_vedha_profile_hash,
                unavailable_guidance_model_id,
            )
        ):
            raise ValueError(
                "unavailable guidance metadata cannot override an available ledger"
            )
        vedha_profile_id = guidance.vedha_profile_id
        vedha_profile_hash = guidance.vedha_profile_hash
        guidance_model_id = guidance.guidance_model_id
        contributions = tuple(
            contribution_from_vedha(guidance, item)
            for item in guidance.contributions
        )

    return SbcAtomicBoundary(
        starts_at_utc=snapshot.as_of_utc,
        evidence_cutoff_utc=snapshot.evidence_cutoff_utc,
        boundary_reason=boundary_reason,
        snapshot_id=snapshot.snapshot_id,
        foundation_profile_id=snapshot.foundation_snapshot.profile_id,
        foundation_profile_hash=snapshot.foundation_snapshot.profile_hash,
        grid_profile_id=snapshot.grid.grid_profile_id,
        grid_profile_hash=snapshot.grid.profile_hash,
        vedha_profile_id=vedha_profile_id,
        vedha_profile_hash=vedha_profile_hash,
        guidance_model_id=guidance_model_id,
        source_ids=snapshot.source_ids,
        guidance_available=guidance is not None,
        contributions=contributions,
        missing_evidence_ids=tuple(missing),
    )


def _ledger_summary(boundary: SbcAtomicBoundary) -> SbcAtomicLedgerSummary:
    scored = [
        float(item.signed_guidance_units)
        for item in boundary.contributions
        if item.signed_guidance_units is not None
    ]
    favorable = sum(value for value in scored if value > 0.0)
    adverse = sum(value for value in scored if value < 0.0)
    unresolved = sum(
        item.signed_guidance_units is None for item in boundary.contributions
    )
    missing_count = len(boundary.missing_evidence_ids)
    unknown_count = unresolved + missing_count
    total_count = len(boundary.contributions) + missing_count
    coverage = len(scored) / total_count if total_count else 0.0
    return SbcAtomicLedgerSummary(
        favorable_guidance_units=favorable,
        adverse_guidance_units=adverse,
        net_guidance_units=sum(scored),
        gross_activation_units=sum(abs(value) for value in scored),
        scored_contribution_count=len(scored),
        unknown_contribution_count=unknown_count,
        missing_evidence_count=missing_count,
        total_evidence_count=total_count,
        unknown_magnitude_units=None if unknown_count else 0.0,
        scoring_coverage_ratio=coverage,
    )


class SbcAtomicIntervalCompiler:
    def compile(
        self,
        boundaries: Iterable[SbcAtomicBoundary],
        *,
        terminal_end_utc: datetime,
    ) -> SbcAtomicIntervalSeries:
        ordered = tuple(sorted(boundaries, key=lambda item: item.starts_at_utc))
        if not ordered:
            raise ValueError("at least one SBC atomic boundary is required")
        terminal = _utc(terminal_end_utc, "terminal_end_utc")
        starts = tuple(item.starts_at_utc for item in ordered)
        if len(starts) != len(set(starts)):
            raise ValueError("SBC atomic boundary timestamps must be unique")
        if any(start >= terminal for start in starts):
            raise ValueError("every SBC atomic boundary must precede terminal_end_utc")
        boundary_ids = tuple(item.boundary_id for item in ordered)
        if len(boundary_ids) != len(set(boundary_ids)):
            raise ValueError("SBC atomic boundary identities must be unique")

        profile_identity = ordered[0].profile_identity
        for boundary in ordered[1:]:
            if boundary.profile_identity != profile_identity:
                raise ValueError(
                    "one atomic interval series cannot mix source profile identities"
                )

        intervals: list[SbcAtomicInterval] = []
        for index, boundary in enumerate(ordered):
            end = ordered[index + 1].starts_at_utc if index + 1 < len(ordered) else terminal
            if end <= boundary.starts_at_utc:
                raise ValueError("atomic intervals must have positive duration")
            ledger = _ledger_summary(boundary)
            identity = {
                "contract": ATOMIC_INTERVAL_CONTRACT,
                "classification": RESEARCH_CLASSIFICATION,
                "start_utc": boundary.starts_at_utc.isoformat(),
                "end_utc": end.isoformat(),
                "evidence_cutoff_utc": boundary.evidence_cutoff_utc.isoformat(),
                "start_boundary_id": boundary.boundary_id,
                "snapshot_id": boundary.snapshot_id,
                "profile_identity": profile_identity.to_dict(),
                "source_ids": boundary.source_ids,
                "guidance_available": boundary.guidance_available,
                "contribution_ids": tuple(
                    item.contribution_id for item in boundary.contributions
                ),
                "missing_evidence_ids": boundary.missing_evidence_ids,
                "ledger": ledger.to_dict(),
            }
            intervals.append(
                SbcAtomicInterval(
                    interval_id=_canonical_hash(identity),
                    classification=RESEARCH_CLASSIFICATION,
                    start_utc=boundary.starts_at_utc,
                    end_utc=end,
                    evidence_cutoff_utc=boundary.evidence_cutoff_utc,
                    start_boundary_id=boundary.boundary_id,
                    boundary_reason=boundary.boundary_reason,
                    snapshot_id=boundary.snapshot_id,
                    profile_identity=profile_identity,
                    source_ids=boundary.source_ids,
                    guidance_available=boundary.guidance_available,
                    contributions=boundary.contributions,
                    missing_evidence_ids=boundary.missing_evidence_ids,
                    ledger=ledger,
                )
            )

        source_ids = tuple(
            sorted({source_id for boundary in ordered for source_id in boundary.source_ids})
        )
        guardrails = SbcAtomicIntervalGuardrails()
        series_identity = {
            "contract": ATOMIC_INTERVAL_CONTRACT,
            "schema_version": ATOMIC_INTERVAL_SCHEMA_VERSION,
            "interval_policy": ATOMIC_INTERVAL_POLICY,
            "classification": RESEARCH_CLASSIFICATION,
            "range_start_utc": ordered[0].starts_at_utc.isoformat(),
            "range_end_utc": terminal.isoformat(),
            "profile_identity": profile_identity.to_dict(),
            "source_ids": source_ids,
            "interval_ids": tuple(item.interval_id for item in intervals),
            "guardrails": to_primitive(guardrails),
        }
        return SbcAtomicIntervalSeries(
            contract=ATOMIC_INTERVAL_CONTRACT,
            schema_version=ATOMIC_INTERVAL_SCHEMA_VERSION,
            interval_policy=ATOMIC_INTERVAL_POLICY,
            classification=RESEARCH_CLASSIFICATION,
            series_id=_canonical_hash(series_identity),
            range_start_utc=ordered[0].starts_at_utc,
            range_end_utc=terminal,
            profile_identity=profile_identity,
            source_ids=source_ids,
            intervals=tuple(intervals),
            guardrails=guardrails,
        )
