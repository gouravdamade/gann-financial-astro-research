from __future__ import annotations

import base64
import copy

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from sbc.timing_profile_signed_review import (
    NO_SIGNED_REVIEW,
    READY_FOR_MANUAL_SOURCE_CERTIFICATION,
    REVIEWER_KEY_UNTRUSTED,
    S3_NOT_READY,
    SIGNATURE_INVALID,
    SbcTimingProfileSignedReviewVerifier,
    reviewer_key_id,
    signed_review_message,
    validate_reviewer_trust_registry,
)
from sbc.timing_profile_source_packet import PASS_STATE
from test_sbc_s3_timing_external_review import _attestation, _bundle


def _public_bytes(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _registry_entry(
    private_key: Ed25519PrivateKey,
    *,
    profile_id: str,
    packet_id: str,
) -> dict:
    public_key = _public_bytes(private_key)
    return {
        "reviewerKeyId": reviewer_key_id(public_key),
        "publicKeyBase64": base64.b64encode(public_key).decode("ascii"),
        "reviewerIdentity": "Independent Reviewer",
        "reviewerOrganization": "External Research Lab",
        "independenceVetted": True,
        "vettedBy": "Repository Administrator",
        "vettedAtUtc": "2026-07-29T05:00:00Z",
        "validFromUtc": "2026-07-29T00:00:00Z",
        "validUntilUtc": "2027-07-29T00:00:00Z",
        "authorizedProfileIds": [profile_id],
        "authorizedPacketIds": [packet_id],
        "revoked": False,
        "revokedAtUtc": "",
        "revocationReason": "",
        "note": "Synthetic independently scoped reviewer key for S4 tests.",
    }


def _registry(entry: dict | None = None) -> dict:
    return {
        "contract": "SBC_TIMING_PROFILE_REVIEWER_TRUST_REGISTRY_V1",
        "schemaVersion": 1,
        "reviewers": [] if entry is None else [entry],
        "registryWriteAllowed": False,
        "executionAllowed": False,
    }


def _signed_evidence() -> tuple[dict, dict, dict, dict, Ed25519PrivateKey]:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle)
    private_key = Ed25519PrivateKey.generate()
    verifier = SbcTimingProfileSignedReviewVerifier()
    template_report = verifier.compile(
        bundle,
        attestation,
        None,
        _registry(),
    )
    assert template_report.signed_review_template is not None
    envelope = copy.deepcopy(template_report.signed_review_template)
    entry = _registry_entry(
        private_key,
        profile_id=envelope["profileId"],
        packet_id=envelope["packetId"],
    )
    registry = _registry(entry)
    envelope["reviewerKeyId"] = entry["reviewerKeyId"]
    envelope["signedAtUtc"] = "2026-07-29T05:30:00Z"
    envelope["signatureBase64"] = base64.b64encode(
        private_key.sign(signed_review_message(envelope))
    ).decode("ascii")
    return bundle, attestation, envelope, registry, private_key


def _gate(report, gate_id: str):
    return next(item for item in report.validation_gates if item.gate_id == gate_id)


def test_missing_signed_review_exposes_template_and_stays_locked() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle)
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        None,
        _registry(),
    )

    assert report.review_status == NO_SIGNED_REVIEW
    assert report.s3_ready is True
    assert report.signed_review_template is not None
    assert report.signed_review_template["reviewerKeyId"] == ""
    assert report.signed_review_template["signatureBase64"] == ""
    assert report.ready_for_manual_source_certification is False
    assert report.source_certified is False
    assert report.guardrails["execution_allowed"] is False


def test_registered_key_signature_reaches_manual_certification_gate() -> None:
    bundle, attestation, envelope, registry, _ = _signed_evidence()
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        envelope,
        registry,
    )

    assert report.review_status == READY_FOR_MANUAL_SOURCE_CERTIFICATION
    assert report.s3_ready is True
    assert report.reviewer_registry_valid is True
    assert report.reviewer_key_trusted is True
    assert report.review_signature_valid is True
    assert report.reviewer_identity_authenticated_to_registry is True
    assert report.reviewer_independence_administratively_vetted is True
    assert report.external_review_independently_proven is False
    assert report.ready_for_manual_source_certification is True
    assert all(gate.state == PASS_STATE for gate in report.validation_gates)
    assert report.source_certified is False
    assert report.profile_registered is False
    assert report.registry_write_allowed is False
    assert report.guardrails["directional_contribution"] == 0.0
    assert report.guardrails["execution_allowed"] is False


def test_shipped_empty_registry_rejects_an_unknown_key() -> None:
    bundle, attestation, envelope, _, _ = _signed_evidence()
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        envelope,
        _registry(),
    )

    assert report.review_status == REVIEWER_KEY_UNTRUSTED
    assert report.reviewer_key_trusted is False
    assert report.review_signature_valid is False
    assert "not present" in _gate(report, "trusted_reviewer_key").detail


def test_tampered_s3_binding_fails_before_signature_verification() -> None:
    bundle, attestation, envelope, registry, _ = _signed_evidence()
    envelope["profileVersion"] = "tampered"
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        envelope,
        registry,
    )

    assert report.review_status == SIGNATURE_INVALID
    assert _gate(report, "signed_review_binding").state != PASS_STATE
    assert report.review_signature_valid is False


def test_invalid_ed25519_signature_fails_closed() -> None:
    bundle, attestation, envelope, registry, _ = _signed_evidence()
    envelope["signatureBase64"] = base64.b64encode(bytes(64)).decode("ascii")
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        envelope,
        registry,
    )

    assert report.review_status == SIGNATURE_INVALID
    assert report.reviewer_key_trusted is True
    assert report.review_signature_valid is False
    assert "invalid" in _gate(report, "ed25519_signature").detail


def test_revoked_key_is_untrusted_even_with_a_valid_signature() -> None:
    bundle, attestation, envelope, registry, _ = _signed_evidence()
    entry = registry["reviewers"][0]
    entry["revoked"] = True
    entry["revokedAtUtc"] = "2026-07-29T06:00:00Z"
    entry["revocationReason"] = "Synthetic revocation test."
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        envelope,
        registry,
    )

    assert report.review_status == REVIEWER_KEY_UNTRUSTED
    assert "revoked" in _gate(report, "trusted_reviewer_key").detail


def test_expired_key_is_untrusted() -> None:
    bundle, attestation, envelope, registry, private_key = _signed_evidence()
    envelope["signedAtUtc"] = "2028-07-29T05:30:00Z"
    envelope["signatureBase64"] = base64.b64encode(
        private_key.sign(signed_review_message(envelope))
    ).decode("ascii")
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        envelope,
        registry,
    )

    assert report.review_status == REVIEWER_KEY_UNTRUSTED
    assert "validity interval" in _gate(report, "trusted_reviewer_key").detail


def test_out_of_scope_key_is_untrusted() -> None:
    bundle, attestation, envelope, registry, _ = _signed_evidence()
    registry["reviewers"][0]["authorizedProfileIds"] = ["other-profile"]
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        envelope,
        registry,
    )

    assert report.review_status == REVIEWER_KEY_UNTRUSTED
    assert "not authorized" in _gate(report, "trusted_reviewer_key").detail


def test_client_supplied_public_key_is_rejected_as_schema_drift() -> None:
    bundle, attestation, envelope, registry, private_key = _signed_evidence()
    envelope["publicKeyBase64"] = base64.b64encode(
        _public_bytes(private_key)
    ).decode("ascii")
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        envelope,
        registry,
    )

    assert report.review_status == SIGNATURE_INVALID
    assert "schema" in _gate(report, "signed_review_binding").detail
    assert report.guardrails["client_public_key_accepted"] is False


def test_rejected_s3_record_cannot_enter_signature_verification() -> None:
    bundle, _, _ = _bundle()
    attestation = _attestation(bundle, approved=False)
    report = SbcTimingProfileSignedReviewVerifier().compile(
        bundle,
        attestation,
        None,
        _registry(),
    )

    assert report.review_status == S3_NOT_READY
    assert report.s3_ready is False
    assert report.signed_review_template is None
    assert report.ready_for_manual_source_certification is False


def test_registry_key_id_must_match_the_raw_public_key() -> None:
    _, _, _, registry, _ = _signed_evidence()
    registry["reviewers"][0]["reviewerKeyId"] = "0" * 64

    try:
        validate_reviewer_trust_registry(registry)
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("mismatched reviewer key ID was accepted")
