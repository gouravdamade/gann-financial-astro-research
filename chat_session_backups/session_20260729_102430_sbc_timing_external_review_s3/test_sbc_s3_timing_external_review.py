from __future__ import annotations

import copy
import json

from sbc.timing_profile_external_review import (
    ATTESTATION_INVALID,
    NO_ATTESTATION,
    READY_FOR_HUMAN_CERTIFICATION_DECISION,
    REVIEW_REJECTED,
    SbcTimingProfileExternalReviewVerifier,
    source_certification_proposal_hash,
)
from sbc.timing_profile_source_packet import FAIL_STATE, PASS_STATE, UNKNOWN_STATE
from sbc.timing_profile_source_verification import (
    SbcTimingProfileSourceVerificationCompiler,
    independent_review_bundle_hash,
)
from test_sbc_s2_timing_source_verification import _evidence


def _bundle() -> tuple[dict, dict[str, bytes], dict[str, str]]:
    profile, packet, source_payloads, excerpt_payloads = _evidence()
    report = SbcTimingProfileSourceVerificationCompiler().compile(
        profile,
        packet,
        source_payloads,
        excerpt_payloads,
    )
    assert report.review_bundle is not None
    return report.review_bundle, source_payloads, excerpt_payloads


def _attestation(bundle: dict, *, approved: bool = True) -> dict:
    attestation = copy.deepcopy(bundle["attestationTemplate"])
    attestation["reviewDecision"] = "APPROVED" if approved else "REJECTED"
    attestation["reviewerIdentity"] = "Independent Reviewer"
    attestation["reviewerOrganization"] = "External Research Lab"
    attestation["reviewerIndependenceConfirmed"] = True
    attestation["reviewedAtUtc"] = "2026-07-29T04:30:00Z"
    attestation["overallNote"] = (
        "All cited source, claim, and conflict decisions were reviewed."
    )
    for key in (
        "sourceArtifactDecisions",
        "claimDecisions",
        "conflictDecisions",
    ):
        for row in attestation[key]:
            row["decision"] = "PASS"
            row["note"] = "Reviewed against the cited independent evidence."
    if not approved:
        attestation["claimDecisions"][0]["decision"] = "FAIL"
        attestation["claimDecisions"][0]["note"] = (
            "The cited passage does not support the complete candidate value."
        )
    return attestation


def _gate(report, gate_id: str):
    return next(item for item in report.validation_gates if item.gate_id == gate_id)


def _rehash_bundle(bundle: dict) -> None:
    bundle["attestationTemplate"]["bundleSha256"] = (
        independent_review_bundle_hash(bundle)
    )


def test_missing_bundle_and_attestation_stays_unknown_and_locked() -> None:
    report = SbcTimingProfileExternalReviewVerifier().compile(None, None)

    assert report.review_status == NO_ATTESTATION
    assert _gate(report, "review_bundle_integrity").state == UNKNOWN_STATE
    assert _gate(report, "completed_attestation").state == UNKNOWN_STATE
    assert report.ready_for_human_certification_decision is False
    assert report.certification_proposal is None
    assert report.source_certified is False
    assert report.guardrails["execution_allowed"] is False


def test_approved_attestation_emits_only_human_certification_proposal() -> None:
    bundle, source_payloads, excerpt_payloads = _bundle()
    attestation = _attestation(bundle)

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == READY_FOR_HUMAN_CERTIFICATION_DECISION
    assert report.bundle_integrity_verified is True
    assert report.embedded_s1_ready is True
    assert report.s2_rows_verified is True
    assert report.attestation_complete is True
    assert report.review_approved is True
    assert report.ready_for_human_certification_decision is True
    assert all(gate.state == PASS_STATE for gate in report.validation_gates)
    assert report.certification_proposal is not None
    assert (
        source_certification_proposal_hash(report.certification_proposal)
        == report.certification_proposal_sha256
    )
    proposal = report.certification_proposal
    assert proposal["manualDecisionGate"]["decision"] == "PENDING"
    assert proposal["manualDecisionGate"]["sourceCertified"] is False
    assert proposal["manualDecisionGate"]["registryWriteAllowed"] is False
    assert proposal["guardrails"]["directionalContribution"] == 0.0
    assert proposal["guardrails"]["executionAllowed"] is False
    serialized = json.dumps(proposal, sort_keys=True)
    for payload in source_payloads.values():
        assert payload.decode("utf-8") not in serialized
    for payload in excerpt_payloads.values():
        assert payload not in serialized


def test_bundle_digest_tampering_fails_closed() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle)
    bundle["profile"]["profileVersion"] = "tampered"

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == ATTESTATION_INVALID
    assert _gate(report, "review_bundle_integrity").state == FAIL_STATE
    assert report.certification_proposal is None


def test_s2_row_tampering_is_detected_even_after_bundle_rehash() -> None:
    bundle, _, _ = _bundle()
    bundle["verification"]["sourceArtifacts"][0]["verification_state"] = "FAIL"
    _rehash_bundle(bundle)
    attestation = _attestation(bundle)

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == ATTESTATION_INVALID
    assert _gate(report, "review_bundle_integrity").state == PASS_STATE
    assert _gate(report, "s2_verification_rows").state == FAIL_STATE
    assert report.certification_proposal is None


def test_missing_or_unexpected_attestation_decision_id_fails() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle)
    attestation["claimDecisions"].pop()
    attestation["claimDecisions"].append(
        {
            "claimId": "undeclared-claim",
            "decision": "PASS",
            "note": "This decision does not belong to the review bundle.",
        }
    )

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == ATTESTATION_INVALID
    assert _gate(report, "completed_attestation").state == FAIL_STATE
    assert report.certification_proposal is None


def test_pending_decision_cannot_complete_attestation() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle)
    attestation["sourceArtifactDecisions"][0]["decision"] = "PENDING"

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == ATTESTATION_INVALID
    assert _gate(report, "completed_attestation").state == FAIL_STATE


def test_approved_attestation_cannot_contain_failed_decision() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle)
    attestation["claimDecisions"][0]["decision"] = "FAIL"
    attestation["claimDecisions"][0]["note"] = "The source did not support it."

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == ATTESTATION_INVALID
    assert _gate(report, "completed_attestation").state == FAIL_STATE
    assert report.certification_proposal is None


def test_valid_rejection_is_recorded_without_certification_proposal() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle, approved=False)

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == REVIEW_REJECTED
    assert report.attestation_complete is True
    assert report.review_approved is False
    assert _gate(report, "completed_attestation").state == PASS_STATE
    assert report.ready_for_human_certification_decision is False
    assert report.certification_proposal is None


def test_attestation_for_another_bundle_fails() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle)
    attestation["bundleSha256"] = "A" * 64

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == ATTESTATION_INVALID
    assert _gate(report, "completed_attestation").state == FAIL_STATE


def test_reviewer_claims_and_registry_lock_are_mandatory() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle)
    attestation["reviewerIdentity"] = ""
    attestation["registryWriteAllowed"] = True

    report = SbcTimingProfileExternalReviewVerifier().compile(
        bundle,
        attestation,
    )

    assert report.review_status == ATTESTATION_INVALID
    assert report.reviewer_identity_authenticated is False
    assert report.external_review_independently_proven is False
    assert report.source_certified is False
    assert report.profile_registered is False
    assert report.registry_write_allowed is False
