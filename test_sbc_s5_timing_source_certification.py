from __future__ import annotations

import base64
import copy

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from sbc.timing_profile_source_certification import (
    CERTIFICATE_INVALID,
    CERTIFICATION_AUTHORITY_UNTRUSTED,
    NO_SOURCE_CERTIFICATE,
    READY_FOR_PROFILE_REGISTRY_ADMISSION,
    S4_NOT_READY,
    SOURCE_CERTIFICATION_REJECTED,
    SbcTimingProfileSourceCertificationVerifier,
    certification_authority_key_id,
    registry_entry_proposal_hash,
    source_certificate_message,
    validate_certification_authority_registry,
)
from test_sbc_s4_timing_signed_review import _signed_evidence


def _public_bytes(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _authority_entry(
    private_key: Ed25519PrivateKey,
    *,
    profile_id: str,
    packet_id: str,
) -> dict:
    public_key = _public_bytes(private_key)
    return {
        "authorityKeyId": certification_authority_key_id(public_key),
        "publicKeyBase64": base64.b64encode(public_key).decode("ascii"),
        "authorityIdentity": "Certification Officer",
        "authorityOrganization": "Independent Certification Board",
        "sourceCertificationAuthorized": True,
        "separationOfDutiesVetted": True,
        "vettedBy": "Repository governance owner",
        "vettedAtUtc": "2026-07-29T05:00:00Z",
        "validFromUtc": "2026-07-29T00:00:00Z",
        "validUntilUtc": "2027-07-29T00:00:00Z",
        "authorizedProfileIds": [profile_id],
        "authorizedPacketIds": [packet_id],
        "revoked": False,
        "revokedAtUtc": "",
        "revocationReason": "",
        "note": "Synthetic certification-authority test key.",
    }


def _authority_registry(entry: dict | None = None) -> dict:
    return {
        "contract": "SBC_TIMING_PROFILE_CERTIFICATION_AUTHORITY_REGISTRY_V1",
        "schemaVersion": 1,
        "authorities": [] if entry is None else [entry],
        "registryWriteAllowed": False,
        "executionAllowed": False,
    }


def _certified_evidence(
    *,
    decision: str = "CERTIFIED",
) -> tuple[dict, dict, dict, dict, dict, dict, Ed25519PrivateKey]:
    bundle, attestation, signed_review, reviewer_registry, _ = _signed_evidence()
    authority_private_key = Ed25519PrivateKey.generate()
    verifier = SbcTimingProfileSourceCertificationVerifier()
    template_report = verifier.compile(
        bundle,
        attestation,
        signed_review,
        None,
        reviewer_registry,
        _authority_registry(),
    )
    assert template_report.source_certificate_template is not None
    certificate = copy.deepcopy(template_report.source_certificate_template)
    entry = _authority_entry(
        authority_private_key,
        profile_id=certificate["profileId"],
        packet_id=certificate["packetId"],
    )
    authority_registry = _authority_registry(entry)
    certificate["certificationDecision"] = decision
    certificate["decisionNote"] = (
        "The exact source chain is certified."
        if decision == "CERTIFIED"
        else "The source chain is rejected."
    )
    certificate["authorityKeyId"] = entry["authorityKeyId"]
    certificate["authorityIdentity"] = entry["authorityIdentity"]
    certificate["authorityOrganization"] = entry["authorityOrganization"]
    certificate["certifiedAtUtc"] = "2026-07-29T06:00:00Z"
    certificate["signatureBase64"] = base64.b64encode(
        authority_private_key.sign(source_certificate_message(certificate))
    ).decode("ascii")
    return (
        bundle,
        attestation,
        signed_review,
        certificate,
        reviewer_registry,
        authority_registry,
        authority_private_key,
    )


def test_missing_upstream_evidence_stays_locked() -> None:
    report = SbcTimingProfileSourceCertificationVerifier().compile(
        None,
        None,
        None,
        None,
        {"contract": "SBC_TIMING_PROFILE_REVIEWER_TRUST_REGISTRY_V1",
         "schemaVersion": 1, "reviewers": [], "registryWriteAllowed": False,
         "executionAllowed": False},
        _authority_registry(),
    )
    assert report.certification_status == S4_NOT_READY
    assert report.source_certified is False
    assert report.guardrails["execution_allowed"] is False


def test_ready_s4_without_certificate_exposes_template() -> None:
    bundle, attestation, signed_review, reviewer_registry, _ = _signed_evidence()
    report = SbcTimingProfileSourceCertificationVerifier().compile(
        bundle,
        attestation,
        signed_review,
        None,
        reviewer_registry,
        _authority_registry(),
    )
    assert report.certification_status == NO_SOURCE_CERTIFICATE
    assert report.source_certificate_template is not None
    assert report.source_certificate_template["certificationDecision"] == "PENDING"
    assert report.registry_entry_proposal is None


def test_separate_trusted_authority_can_emit_registry_proposal() -> None:
    evidence = _certified_evidence()
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == READY_FOR_PROFILE_REGISTRY_ADMISSION
    assert report.source_certified is True
    assert report.ready_for_profile_registry_admission is True
    assert report.authority_key_trusted is True
    assert report.certificate_signature_valid is True
    assert report.separation_of_duties_vetted is True
    assert report.profile_registered is False
    assert report.registry_write_allowed is False
    assert report.registry_entry_proposal is not None
    assert (
        registry_entry_proposal_hash(report.registry_entry_proposal)
        == report.registry_admission_proposal_sha256
    )
    assert report.guardrails["execution_allowed"] is False


def test_signed_rejection_is_recorded_without_registry_proposal() -> None:
    evidence = _certified_evidence(decision="REJECTED")
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == SOURCE_CERTIFICATION_REJECTED
    assert report.certificate_signature_valid is True
    assert report.source_certified is False
    assert report.registry_entry_proposal is None


def test_empty_shipped_authority_registry_rejects_unknown_key() -> None:
    evidence = _certified_evidence()
    report = SbcTimingProfileSourceCertificationVerifier().compile(
        *evidence[:5],
        _authority_registry(),
    )
    assert report.certification_status == CERTIFICATION_AUTHORITY_UNTRUSTED
    assert report.authority_key_trusted is False
    assert report.source_certified is False


def test_tampered_s4_binding_is_invalid() -> None:
    evidence = list(_certified_evidence())
    evidence[3]["signedReviewSha256"] = "A" * 64
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == CERTIFICATE_INVALID
    assert report.certificate_signature_valid is False


def test_invalid_certification_signature_fails_closed() -> None:
    evidence = list(_certified_evidence())
    evidence[3]["signatureBase64"] = base64.b64encode(bytes(64)).decode("ascii")
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == CERTIFICATE_INVALID
    assert report.authority_key_trusted is True
    assert report.certificate_signature_valid is False


def test_revoked_authority_key_is_untrusted() -> None:
    evidence = list(_certified_evidence())
    entry = evidence[5]["authorities"][0]
    entry["revoked"] = True
    entry["revokedAtUtc"] = "2026-07-29T06:30:00Z"
    entry["revocationReason"] = "Synthetic revocation test."
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == CERTIFICATION_AUTHORITY_UNTRUSTED


def test_expired_authority_key_is_untrusted() -> None:
    evidence = list(_certified_evidence())
    evidence[5]["authorities"][0]["validUntilUtc"] = "2026-07-29T05:30:00Z"
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == CERTIFICATION_AUTHORITY_UNTRUSTED


def test_out_of_scope_authority_key_is_untrusted() -> None:
    evidence = list(_certified_evidence())
    evidence[5]["authorities"][0]["authorizedProfileIds"] = ["other-profile"]
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == CERTIFICATION_AUTHORITY_UNTRUSTED


def test_reviewer_key_cannot_certify_its_own_review() -> None:
    evidence = list(_certified_evidence())
    reviewer_entry = evidence[4]["reviewers"][0]
    authority_entry = evidence[5]["authorities"][0]
    certificate = evidence[3]
    authority_entry["authorityKeyId"] = reviewer_entry["reviewerKeyId"]
    authority_entry["publicKeyBase64"] = reviewer_entry["publicKeyBase64"]
    certificate["authorityKeyId"] = reviewer_entry["reviewerKeyId"]
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == CERTIFICATION_AUTHORITY_UNTRUSTED
    assert report.source_certified is False


def test_client_supplied_public_key_is_schema_drift() -> None:
    evidence = list(_certified_evidence())
    evidence[3]["publicKeyBase64"] = evidence[5]["authorities"][0][
        "publicKeyBase64"
    ]
    report = SbcTimingProfileSourceCertificationVerifier().compile(*evidence[:6])
    assert report.certification_status == CERTIFICATE_INVALID
    assert report.guardrails["client_public_key_accepted"] is False


def test_authority_registry_key_id_must_match_public_key() -> None:
    evidence = _certified_evidence()
    registry = copy.deepcopy(evidence[5])
    registry["authorities"][0]["authorityKeyId"] = "0" * 64
    try:
        validate_certification_authority_registry(registry)
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("mismatched authority key ID was accepted")
