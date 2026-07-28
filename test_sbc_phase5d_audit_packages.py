from __future__ import annotations

import copy
import hashlib
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from sbc.atomic_intervals import (
    SbcAtomicBoundary,
    SbcAtomicContribution,
    SbcAtomicIntervalCompiler,
)
from sbc.audit_packages import (
    AUDIT_PACKAGE_CONTRACT,
    AUDIT_PACKAGE_POLICY,
    CELL_TARGET,
    DESCRIPTIVE_COMPARISON_ROLE,
    INTERVAL_TARGET,
    MANUAL_RESEARCH_ANNOTATION_ROLE,
    SbcAuditBookmarkInput,
    SbcAuditComparisonPackageCompiler,
    render_audit_package_html,
    validate_audit_package_payload,
    verify_audit_package_replay,
)
from sbc.audit_views import SbcLinkedAuditViewCompiler
from sbc.multidimensional_ledger import SbcMultidimensionalLedgerCompiler


START = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _contribution(
    label: str,
    units: float | None,
    *,
    body: str,
    direction: str,
    lineage: str | None = None,
) -> SbcAtomicContribution:
    return SbcAtomicContribution(
        source_lineage_id=_digest(lineage or f"lineage:{label}"),
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
        source_ids=("SOURCE-A",),
        guidance_available=True,
        contributions=contributions,
        missing_evidence_ids=(),
    )


def _audit():
    boundaries = (
        _boundary(
            START,
            "first",
            (
                _contribution(
                    "jupiter-a",
                    2.0,
                    body="JUPITER",
                    direction="FRONT",
                    lineage="shared-jupiter",
                ),
                _contribution(
                    "saturn-a",
                    -1.0,
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
                    "jupiter-b",
                    3.5,
                    body="JUPITER",
                    direction="FRONT",
                    lineage="shared-jupiter",
                ),
                _contribution(
                    "moon-b",
                    None,
                    body="MOON",
                    direction="RIGHT",
                ),
            ),
        ),
        _boundary(
            START + timedelta(hours=2),
            "third",
            (
                _contribution(
                    "sun-c",
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
    ledger = SbcMultidimensionalLedgerCompiler().compile(
        atomic,
        instrument_identity="FX:USDJPY",
    )
    return SbcLinkedAuditViewCompiler().compile(ledger)


def _compile_package():
    audit = _audit()
    intervals = audit.intervals
    bookmark = SbcAuditBookmarkInput(
        target_type=INTERVAL_TARGET,
        target_id=intervals[1].interval_id,
        label="Review contrast",
        note="Manual observation only; not an ML label.",
        created_at_utc=START + timedelta(hours=4),
    )
    recipe = {
        "audit_request": {"fixture": "replay"},
        "baseline_interval_id": intervals[0].interval_id,
        "comparison_interval_ids": [
            intervals[2].interval_id,
            intervals[1].interval_id,
        ],
        "bookmarks": [
            {
                "target_type": bookmark.target_type,
                "target_id": bookmark.target_id,
                "label": bookmark.label,
                "note": bookmark.note,
                "created_at_utc": bookmark.created_at_utc.isoformat(),
            }
        ],
        "sealed_at_utc": (START + timedelta(hours=5)).isoformat(),
    }
    package = SbcAuditComparisonPackageCompiler().compile(
        audit,
        baseline_interval_id=intervals[0].interval_id,
        comparison_interval_ids=(
            intervals[2].interval_id,
            intervals[1].interval_id,
        ),
        bookmark_inputs=(bookmark,),
        sealed_at_utc=START + timedelta(hours=5),
        replay_recipe=recipe,
    )
    return audit, package


def test_p4_compares_multiple_intervals_in_stable_source_order() -> None:
    audit, package = _compile_package()

    assert package.contract == AUDIT_PACKAGE_CONTRACT
    assert package.package_policy == AUDIT_PACKAGE_POLICY
    assert package.source_audit_id == audit.audit_view_id
    assert [item.comparison_interval_id for item in package.comparisons] == [
        audit.intervals[1].interval_id,
        audit.intervals[2].interval_id,
    ]
    first = package.comparisons[0]
    assert first.total_delta.net_guidance_units == pytest.approx(2.5)
    assert first.total_delta.gross_activation_units == pytest.approx(0.5)
    assert first.total_delta.unknown_contribution_count == 1
    assert first.total_delta.unknown_magnitude_units is None
    assert first.derivation_role == DESCRIPTIVE_COMPARISON_ROLE
    assert first.counts_as_independent_vote is False
    assert first.directional_contribution == 0.0
    assert _digest("shared-jupiter") in first.shared_source_lineage_ids
    assert any(
        item.baseline_cell_id is None or item.comparison_cell_id is None
        for item in first.cell_comparisons
    )


def test_p4_bookmarks_are_linked_manual_annotations_only() -> None:
    audit, package = _compile_package()
    bookmark = package.bookmarks[0]

    assert bookmark.target_id == audit.intervals[1].interval_id
    assert bookmark.annotation_role == MANUAL_RESEARCH_ANNOTATION_ROLE
    assert bookmark.counts_as_evidence is False
    assert bookmark.official_ml_note is False
    assert bookmark.directional_contribution == 0.0

    invalid = SbcAuditBookmarkInput(
        target_type=CELL_TARGET,
        target_id=_digest("missing-cell"),
        label="Bad link",
        note="Must fail closed.",
        created_at_utc=START,
    )
    with pytest.raises(ValueError, match="target does not exist"):
        SbcAuditComparisonPackageCompiler().compile(
            audit,
            baseline_interval_id=audit.intervals[0].interval_id,
            comparison_interval_ids=(audit.intervals[1].interval_id,),
            bookmark_inputs=(invalid,),
            sealed_at_utc=START,
            replay_recipe={"fixture": True},
        )


def test_p4_serialization_replay_and_verification_are_deterministic() -> None:
    _, first = _compile_package()
    _, second = _compile_package()

    assert first.package_id == second.package_id
    assert first.to_dict() == second.to_dict()
    validate_audit_package_payload(first.to_dict())
    verification = verify_audit_package_replay(
        first.to_dict(),
        second.to_dict(),
    )
    assert verification.state == "PASS"
    assert verification.structural_hash_match is True
    assert verification.source_projection_match is True
    assert verification.replay_recipe_match is True
    assert verification.replay_audit_match is True
    assert verification.replay_package_match is True
    assert verification.errors == ()


def test_p4_tampering_and_weakened_p3_locks_fail_closed() -> None:
    audit, package = _compile_package()
    tampered = copy.deepcopy(package.to_dict())
    tampered["comparisons"][0]["total_delta"]["net_guidance_units"] += 1
    with pytest.raises(ValueError, match="package hash"):
        validate_audit_package_payload(tampered)

    unsafe = replace(
        audit,
        guardrails=replace(audit.guardrails, confidence_included=True),
    )
    with pytest.raises(ValueError, match="weakens required P4 guardrails"):
        SbcAuditComparisonPackageCompiler().compile(
            unsafe,
            baseline_interval_id=unsafe.intervals[0].interval_id,
            comparison_interval_ids=(unsafe.intervals[1].interval_id,),
            bookmark_inputs=(),
            sealed_at_utc=START,
            replay_recipe={"fixture": True},
        )


def test_p4_invalid_selection_fails_closed() -> None:
    audit = _audit()
    baseline = audit.intervals[0].interval_id
    compiler = SbcAuditComparisonPackageCompiler()

    with pytest.raises(ValueError, match="at least one comparison"):
        compiler.compile(
            audit,
            baseline_interval_id=baseline,
            comparison_interval_ids=(),
            bookmark_inputs=(),
            sealed_at_utc=START,
            replay_recipe={"fixture": True},
        )
    with pytest.raises(ValueError, match="cannot also be"):
        compiler.compile(
            audit,
            baseline_interval_id=baseline,
            comparison_interval_ids=(baseline,),
            bookmark_inputs=(),
            sealed_at_utc=START,
            replay_recipe={"fixture": True},
        )


def test_p4_html_report_escapes_manual_text_and_keeps_warning_visible() -> None:
    _, package = _compile_package()
    html_report = render_audit_package_html(package)

    assert "Reproducible SBC Audit Package" in html_report
    assert "No market direction" in html_report
    assert "Manual observation only" in html_report
    assert "<script>" not in html_report
    assert package.package_id in html_report
