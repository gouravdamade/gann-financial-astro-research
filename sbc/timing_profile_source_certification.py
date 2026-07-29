from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .atomic_intervals import RESEARCH_CLASSIFICATION
from .models import to_primitive
from .timing_profile_signed_review import (
    READY_FOR_MANUAL_SOURCE_CERTIFICATION,
    SbcTimingProfileSignedReviewVerifier,
    TimingProfileSignedReviewReport,
)
from .timing_profile_source_packet import FAIL_STATE, PASS_STATE, UNKNOWN_STATE


SOURCE_CERTIFICATION_REPORT_CONTRACT = (
    "SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_REPORT_V1"
)
SOURCE_CERTIFICATION_REPORT_SCHEMA_VERSION = 1
SOURCE_CERTIFICATE_CONTRACT = "SBC_TIMING_PROFILE_SOURCE_CERTIFICATE_V1"
SOURCE_CERTIFICATE_SCHEMA_VERSION = 1
SOURCE_CERTIFICATION_POLICY = "ED25519_SEPARATE_AUTHORITY_EXACT_S4_BINDING_V1"
SOURCE_CERTIFICATE_HASH_METHOD = (
    "CANONICAL_JSON_ED25519_WITH_SIGNATURE_BASE64_BLANK"
)
CERTIFICATION_AUTHORITY_REGISTRY_CONTRACT = (
    "SBC_TIMING_PROFILE_CERTIFICATION_AUTHORITY_REGISTRY_V1"
)
CERTIFICATION_AUTHORITY_REGISTRY_SCHEMA_VERSION = 1
REGISTRY_ENTRY_PROPOSAL_CONTRACT = (
    "SBC_TIMING_PROFILE_REGISTRY_ENTRY_PROPOSAL_V1"
)
REGISTRY_ENTRY_PROPOSAL_SCHEMA_VERSION = 1
REGISTRY_ENTRY_PROPOSAL_HASH_METHOD = (
    "CANONICAL_JSON_SHA256_WITH_PROPOSAL_SHA256_BLANK"
)

S4_NOT_READY = "S4_NOT_READY"
NO_SOURCE_CERTIFICATE = "NO_SOURCE_CERTIFICATE"
CERTIFICATE_INVALID = "CERTIFICATE_INVALID"
CERTIFICATION_AUTHORITY_UNTRUSTED = "CERTIFICATION_AUTHORITY_UNTRUSTED"
SOURCE_CERTIFICATION_REJECTED = "SOURCE_CERTIFICATION_REJECTED"
READY_FOR_PROFILE_REGISTRY_ADMISSION = "READY_FOR_PROFILE_REGISTRY_ADMISSION"

_REGISTRY_KEYS = {
    "contract",
    "schemaVersion",
    "authorities",
    "registryWriteAllowed",
    "executionAllowed",
}
_AUTHORITY_KEYS = {
    "authorityKeyId",
    "publicKeyBase64",
    "authorityIdentity",
    "authorityOrganization",
    "sourceCertificationAuthorized",
    "separationOfDutiesVetted",
    "vettedBy",
    "vettedAtUtc",
    "validFromUtc",
    "validUntilUtc",
    "authorizedProfileIds",
    "authorizedPacketIds",
    "revoked",
    "revokedAtUtc",
    "revocationReason",
    "note",
}
_CERTIFICATE_KEYS = {
    "contract",
    "schemaVersion",
    "certificationPolicy",
    "signatureHashMethod",
    "reviewBundleSha256",
    "attestationSha256",
    "certificationProposalSha256",
    "signedReviewSha256",
    "profileId",
    "profileVersion",
    "profileHash",
    "packetId",
    "packetHash",
    "reviewerKeyId",
    "sourceAuditRefs",
    "certificationDecision",
    "decisionNote",
    "authorityKeyId",
    "authorityIdentity",
    "authorityOrganization",
    "separationOfDutiesConfirmed",
    "certifiedAtUtc",
    "signatureBase64",
    "profileRegistered",
    "registryWriteAllowed",
    "executionAllowed",
}


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


def _strict_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label} has an incomplete or unexpected schema")
    return value


def _utc_timestamp(value: Any, label: str) -> tuple[str, datetime]:
    normalized = _required_text(value, label)
    if not normalized.endswith("Z"):
        raise ValueError(f"{label} must end in Z")
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")
    return normalized, parsed.astimezone(timezone.utc)


def _base64_bytes(
    value: Any,
    label: str,
    *,
    expected_length: int,
) -> bytes:
    normalized = _required_text(value, label)
    try:
        decoded = base64.b64decode(normalized, validate=True)
    except ValueError as exc:
        raise ValueError(f"{label} must be valid base64") from exc
    if len(decoded) != expected_length:
        raise ValueError(f"{label} must decode to {expected_length} bytes")
    return decoded


def _unique_texts(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty array")
    normalized = tuple(
        _required_text(item, f"{label}[{index}]")
        for index, item in enumerate(value)
    )
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} must not contain duplicates")
    return normalized


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest().upper()


def certification_authority_key_id(public_key_bytes: bytes) -> str:
    if not isinstance(public_key_bytes, bytes) or len(public_key_bytes) != 32:
        raise ValueError("certification-authority public key must contain 32 bytes")
    return hashlib.sha256(public_key_bytes).hexdigest().upper()


def source_certificate_message(certificate: Mapping[str, Any]) -> bytes:
    if not isinstance(certificate, Mapping):
        raise ValueError("source certificate must be an object")
    normalized = json.loads(
        json.dumps(certificate, ensure_ascii=True, allow_nan=False)
    )
    _strict_object(normalized, _CERTIFICATE_KEYS, "source certificate")
    if normalized.get("contract") != SOURCE_CERTIFICATE_CONTRACT:
        raise ValueError("source certificate contract is unsupported")
    if normalized.get("schemaVersion") != SOURCE_CERTIFICATE_SCHEMA_VERSION:
        raise ValueError("source certificate schemaVersion is unsupported")
    if normalized.get("certificationPolicy") != SOURCE_CERTIFICATION_POLICY:
        raise ValueError("source certificate policy is unsupported")
    if normalized.get("signatureHashMethod") != SOURCE_CERTIFICATE_HASH_METHOD:
        raise ValueError("source certificate hash method is unsupported")
    normalized["signatureBase64"] = ""
    return _canonical_json(normalized)


def source_certificate_sha256(certificate: Mapping[str, Any]) -> str:
    if not isinstance(certificate, Mapping):
        raise ValueError("source certificate must be an object")
    return _canonical_hash(certificate)


def registry_entry_proposal_hash(proposal: Mapping[str, Any]) -> str:
    if not isinstance(proposal, Mapping):
        raise ValueError("registry entry proposal must be an object")
    normalized = json.loads(
        json.dumps(proposal, ensure_ascii=True, allow_nan=False)
    )
    if normalized.get("contract") != REGISTRY_ENTRY_PROPOSAL_CONTRACT:
        raise ValueError("registry entry proposal contract is unsupported")
    if (
        normalized.get("schemaVersion")
        != REGISTRY_ENTRY_PROPOSAL_SCHEMA_VERSION
    ):
        raise ValueError("registry entry proposal schemaVersion is unsupported")
    if "proposalSha256" not in normalized:
        raise ValueError("registry entry proposalSha256 is required")
    normalized["proposalSha256"] = ""
    return _canonical_hash(normalized)


@dataclass(frozen=True)
class TimingSourceCertificationGate:
    gate_id: str
    state: str
    mandatory: bool
    label: str
    detail: str

    def __post_init__(self) -> None:
        if self.state not in {PASS_STATE, FAIL_STATE, UNKNOWN_STATE}:
            raise ValueError(f"unknown gate state: {self.state}")
        object.__setattr__(self, "gate_id", _required_text(self.gate_id, "gate_id"))
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "detail", _required_text(self.detail, "detail"))

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingProfileSourceCertificationReport:
    certification_status: str
    profile_id: str | None
    profile_version: str | None
    candidate_profile_hash: str | None
    packet_id: str | None
    packet_hash: str | None
    review_bundle_sha256: str | None
    attestation_sha256: str | None
    certification_proposal_sha256: str | None
    signed_review_sha256: str | None
    source_certificate_sha256: str | None
    registry_admission_proposal_sha256: str | None
    s4_ready: bool
    authority_registry_valid: bool
    authority_key_trusted: bool
    certificate_signature_valid: bool
    separation_of_duties_vetted: bool
    certification_decision: str | None
    source_certified: bool
    ready_for_profile_registry_admission: bool
    validation_gates: tuple[TimingSourceCertificationGate, ...]
    missing_requirements: tuple[str, ...]
    source_certificate_template: dict[str, Any] | None
    registry_entry_proposal: dict[str, Any] | None
    contract: str = SOURCE_CERTIFICATION_REPORT_CONTRACT
    schema_version: int = SOURCE_CERTIFICATION_REPORT_SCHEMA_VERSION
    certification_policy: str = SOURCE_CERTIFICATION_POLICY
    classification: str = RESEARCH_CLASSIFICATION
    profile_registered: bool = False
    registry_write_allowed: bool = False
    guardrails: dict[str, Any] = field(
        default_factory=lambda: {
            "research_only": True,
            "read_only": True,
            "payloads_persisted": False,
            "client_public_key_accepted": False,
            "server_authority_registry_required": True,
            "separate_authority_required": True,
            "certificate_records_governance_decision_only": True,
            "doctrinal_truth_cryptographically_proven": False,
            "profile_registered": False,
            "registry_write_allowed": False,
            "timing_phase_calculated": False,
            "directional_phase_calculated": False,
            "confidence_calculated": False,
            "counts_as_independent_vote": False,
            "directional_contribution": 0.0,
            "auto_suggest_included": False,
            "live_inference_included": False,
            "official_ml_notes_included": False,
            "shadow_vote_included": False,
            "trade_output_included": False,
            "financially_validated": False,
            "execution_allowed": False,
            "blocked_capabilities": [
                "TIMING_PROFILE_REGISTRATION",
                "DIRECTIONAL_TIMING_PHASE",
                "TIMING_CONFIDENCE",
                "AUTO_SUGGEST",
                "LIVE_INFERENCE",
                "OFFICIAL_ML_NOTES",
                "SHADOW_VOTE",
                "TRADE_OUTPUT",
                "MT5_EXECUTION",
            ],
        }
    )

    def __post_init__(self) -> None:
        if self.source_certified != self.ready_for_profile_registry_admission:
            raise ValueError("S5 source certification and readiness must agree")
        if self.profile_registered or self.registry_write_allowed:
            raise ValueError("S5 cannot register a timing profile")
        if self.guardrails.get("execution_allowed") is not False:
            raise ValueError("S5 execution must remain locked")
        if float(self.guardrails.get("directional_contribution", 1.0)) != 0.0:
            raise ValueError("S5 cannot contribute market direction")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class _TrustedCertificationAuthority:
    authority_key_id: str
    public_key: bytes
    authority_identity: str
    authority_organization: str
    valid_from_utc: datetime
    valid_until_utc: datetime
    authorized_profile_ids: tuple[str, ...]
    authorized_packet_ids: tuple[str, ...]
    separation_of_duties_vetted: bool
    revoked: bool


def validate_certification_authority_registry(
    registry_payload: Any,
) -> dict[str, _TrustedCertificationAuthority]:
    registry = _strict_object(
        registry_payload,
        _REGISTRY_KEYS,
        "certification authority registry",
    )
    if registry.get("contract") != CERTIFICATION_AUTHORITY_REGISTRY_CONTRACT:
        raise ValueError("certification authority registry contract is unsupported")
    if (
        registry.get("schemaVersion")
        != CERTIFICATION_AUTHORITY_REGISTRY_SCHEMA_VERSION
    ):
        raise ValueError(
            "certification authority registry schemaVersion is unsupported"
        )
    if registry.get("registryWriteAllowed") is not False:
        raise ValueError("certification authority registry cannot allow writes")
    if registry.get("executionAllowed") is not False:
        raise ValueError("certification authority registry cannot allow execution")
    authorities = registry.get("authorities")
    if not isinstance(authorities, list):
        raise ValueError(
            "certification authority registry authorities must be an array"
        )

    result: dict[str, _TrustedCertificationAuthority] = {}
    for index, raw_entry in enumerate(authorities):
        label = f"authorities[{index}]"
        entry = _strict_object(raw_entry, _AUTHORITY_KEYS, label)
        key_id = _sha256(entry.get("authorityKeyId"), f"{label}.authorityKeyId")
        if key_id in result:
            raise ValueError(
                "certification authority registry contains duplicate key IDs"
            )
        public_key = _base64_bytes(
            entry.get("publicKeyBase64"),
            f"{label}.publicKeyBase64",
            expected_length=32,
        )
        if certification_authority_key_id(public_key) != key_id:
            raise ValueError(f"{label}.authorityKeyId does not match its public key")
        identity = _required_text(
            entry.get("authorityIdentity"),
            f"{label}.authorityIdentity",
        )
        organization = _required_text(
            entry.get("authorityOrganization"),
            f"{label}.authorityOrganization",
        )
        if entry.get("sourceCertificationAuthorized") is not True:
            raise ValueError(f"{label}.sourceCertificationAuthorized must be true")
        if entry.get("separationOfDutiesVetted") is not True:
            raise ValueError(f"{label}.separationOfDutiesVetted must be true")
        _required_text(entry.get("vettedBy"), f"{label}.vettedBy")
        _utc_timestamp(entry.get("vettedAtUtc"), f"{label}.vettedAtUtc")
        _, valid_from = _utc_timestamp(
            entry.get("validFromUtc"),
            f"{label}.validFromUtc",
        )
        _, valid_until = _utc_timestamp(
            entry.get("validUntilUtc"),
            f"{label}.validUntilUtc",
        )
        if valid_until <= valid_from:
            raise ValueError(f"{label} validity interval is not positive")
        profile_ids = _unique_texts(
            entry.get("authorizedProfileIds"),
            f"{label}.authorizedProfileIds",
        )
        packet_ids = _unique_texts(
            entry.get("authorizedPacketIds"),
            f"{label}.authorizedPacketIds",
        )
        revoked = entry.get("revoked")
        if not isinstance(revoked, bool):
            raise ValueError(f"{label}.revoked must be boolean")
        revoked_at = str(entry.get("revokedAtUtc") or "").strip()
        revocation_reason = str(entry.get("revocationReason") or "").strip()
        if revoked:
            _utc_timestamp(revoked_at, f"{label}.revokedAtUtc")
            _required_text(
                revocation_reason,
                f"{label}.revocationReason",
            )
        elif revoked_at or revocation_reason:
            raise ValueError(
                f"{label} revocation fields must be blank when not revoked"
            )
        _required_text(entry.get("note"), f"{label}.note")
        result[key_id] = _TrustedCertificationAuthority(
            authority_key_id=key_id,
            public_key=public_key,
            authority_identity=identity,
            authority_organization=organization,
            valid_from_utc=valid_from,
            valid_until_utc=valid_until,
            authorized_profile_ids=profile_ids,
            authorized_packet_ids=packet_ids,
            separation_of_duties_vetted=True,
            revoked=revoked,
        )
    return result


def _source_audit_refs(report: TimingProfileSignedReviewReport) -> tuple[str, ...]:
    values = (
        ("S1", report.packet_hash),
        ("S2", report.review_bundle_sha256),
        ("S3", report.certification_proposal_sha256),
        ("S4", report.signed_review_sha256),
    )
    if any(value is None for _, value in values):
        return ()
    return tuple(f"{label}:{value}" for label, value in values)


def _certificate_template(
    report: TimingProfileSignedReviewReport,
    signed_review: Any,
) -> dict[str, Any] | None:
    if (
        report.review_status != READY_FOR_MANUAL_SOURCE_CERTIFICATION
        or not report.ready_for_manual_source_certification
        or not isinstance(signed_review, dict)
    ):
        return None
    refs = _source_audit_refs(report)
    if not refs:
        return None
    return {
        "contract": SOURCE_CERTIFICATE_CONTRACT,
        "schemaVersion": SOURCE_CERTIFICATE_SCHEMA_VERSION,
        "certificationPolicy": SOURCE_CERTIFICATION_POLICY,
        "signatureHashMethod": SOURCE_CERTIFICATE_HASH_METHOD,
        "reviewBundleSha256": report.review_bundle_sha256,
        "attestationSha256": report.attestation_sha256,
        "certificationProposalSha256": report.certification_proposal_sha256,
        "signedReviewSha256": report.signed_review_sha256,
        "profileId": report.profile_id,
        "profileVersion": report.profile_version,
        "profileHash": report.candidate_profile_hash,
        "packetId": report.packet_id,
        "packetHash": report.packet_hash,
        "reviewerKeyId": signed_review.get("reviewerKeyId"),
        "sourceAuditRefs": list(refs),
        "certificationDecision": "PENDING",
        "decisionNote": "",
        "authorityKeyId": "",
        "authorityIdentity": "",
        "authorityOrganization": "",
        "separationOfDutiesConfirmed": True,
        "certifiedAtUtc": "",
        "signatureBase64": "",
        "profileRegistered": False,
        "registryWriteAllowed": False,
        "executionAllowed": False,
    }


class SbcTimingProfileSourceCertificationVerifier:
    @staticmethod
    def _gate(
        gate_id: str,
        label: str,
        state: str,
        detail: str,
    ) -> TimingSourceCertificationGate:
        return TimingSourceCertificationGate(
            gate_id=gate_id,
            state=state,
            mandatory=True,
            label=label,
            detail=detail,
        )

    @staticmethod
    def _validate_binding(
        certificate_payload: Any,
        report: TimingProfileSignedReviewReport,
        signed_review: Any,
    ) -> tuple[dict[str, Any], datetime]:
        certificate = _strict_object(
            certificate_payload,
            _CERTIFICATE_KEYS,
            "source certificate",
        )
        source_certificate_message(certificate)
        expected = _certificate_template(report, signed_review)
        if expected is None:
            raise ValueError("S4 is not ready for source certification")
        linked_fields = {
            "reviewBundleSha256",
            "attestationSha256",
            "certificationProposalSha256",
            "signedReviewSha256",
            "profileId",
            "profileVersion",
            "profileHash",
            "packetId",
            "packetHash",
            "reviewerKeyId",
            "sourceAuditRefs",
            "separationOfDutiesConfirmed",
            "profileRegistered",
            "registryWriteAllowed",
            "executionAllowed",
        }
        for field_name in linked_fields:
            if certificate.get(field_name) != expected.get(field_name):
                raise ValueError(
                    f"source certificate {field_name} does not match S4 evidence"
                )
        for field_name in (
            "reviewBundleSha256",
            "attestationSha256",
            "certificationProposalSha256",
            "signedReviewSha256",
            "profileHash",
            "packetHash",
            "reviewerKeyId",
            "authorityKeyId",
        ):
            _sha256(
                certificate.get(field_name),
                f"source certificate.{field_name}",
            )
        decision = certificate.get("certificationDecision")
        if decision not in {"CERTIFIED", "REJECTED"}:
            raise ValueError(
                "source certificate decision must be CERTIFIED or REJECTED"
            )
        _required_text(
            certificate.get("decisionNote"),
            "source certificate.decisionNote",
        )
        _required_text(
            certificate.get("authorityIdentity"),
            "source certificate.authorityIdentity",
        )
        _required_text(
            certificate.get("authorityOrganization"),
            "source certificate.authorityOrganization",
        )
        if certificate.get("separationOfDutiesConfirmed") is not True:
            raise ValueError(
                "source certificate separationOfDutiesConfirmed must be true"
            )
        _, certified_at = _utc_timestamp(
            certificate.get("certifiedAtUtc"),
            "source certificate.certifiedAtUtc",
        )
        _, review_signed_at = _utc_timestamp(
            signed_review.get("signedAtUtc"),
            "signed review.signedAtUtc",
        )
        if certified_at < review_signed_at:
            raise ValueError(
                "certifiedAtUtc cannot be earlier than the S4 signed review"
            )
        _base64_bytes(
            certificate.get("signatureBase64"),
            "source certificate.signatureBase64",
            expected_length=64,
        )
        return certificate, certified_at

    @staticmethod
    def _trusted_authority(
        certificate: dict[str, Any],
        certified_at: datetime,
        authorities: dict[str, _TrustedCertificationAuthority],
        report: TimingProfileSignedReviewReport,
    ) -> _TrustedCertificationAuthority:
        authority = authorities.get(certificate["authorityKeyId"])
        if authority is None:
            raise LookupError(
                "certification authority key is not present in the server registry"
            )
        if authority.revoked:
            raise LookupError("certification authority key is revoked")
        if not (
            authority.valid_from_utc
            <= certified_at
            <= authority.valid_until_utc
        ):
            raise LookupError(
                "certification authority key is outside its validity interval"
            )
        if authority.authority_identity != certificate["authorityIdentity"]:
            raise LookupError(
                "certification authority identity does not match the trusted key"
            )
        if (
            authority.authority_organization
            != certificate["authorityOrganization"]
        ):
            raise LookupError(
                "certification authority organization does not match the trusted key"
            )
        if report.profile_id not in authority.authorized_profile_ids:
            raise LookupError(
                "certification authority is not authorized for this profile"
            )
        if report.packet_id not in authority.authorized_packet_ids:
            raise LookupError(
                "certification authority is not authorized for this source packet"
            )
        return authority

    @staticmethod
    def _verify_signature(
        certificate: dict[str, Any],
        authority: _TrustedCertificationAuthority,
    ) -> None:
        signature = _base64_bytes(
            certificate.get("signatureBase64"),
            "source certificate.signatureBase64",
            expected_length=64,
        )
        try:
            Ed25519PublicKey.from_public_bytes(authority.public_key).verify(
                signature,
                source_certificate_message(certificate),
            )
        except InvalidSignature as exc:
            raise ValueError(
                "Ed25519 source-certification signature is invalid"
            ) from exc

    @staticmethod
    def _registry_proposal(
        report: TimingProfileSignedReviewReport,
        certificate_hash: str,
    ) -> tuple[dict[str, Any], str]:
        refs = [*_source_audit_refs(report), f"S5:{certificate_hash}"]
        proposal = {
            "contract": REGISTRY_ENTRY_PROPOSAL_CONTRACT,
            "schemaVersion": REGISTRY_ENTRY_PROPOSAL_SCHEMA_VERSION,
            "proposalStatus": "PENDING_HUMAN_GIT_REVIEW",
            "proposalSha256": "",
            "proposalHashMethod": REGISTRY_ENTRY_PROPOSAL_HASH_METHOD,
            "profileEntry": {
                "profileHash": report.candidate_profile_hash,
                "profileId": report.profile_id,
                "profileVersion": report.profile_version,
                "frozen": True,
                "sourceCertified": True,
                "sourceAuditRefs": refs,
                "prospectiveTrialId": None,
            },
            "sourceCertificateSha256": certificate_hash,
            "profileRegistered": False,
            "registryWriteAllowed": False,
            "executionAllowed": False,
        }
        proposal_hash = registry_entry_proposal_hash(proposal)
        proposal["proposalSha256"] = proposal_hash
        return proposal, proposal_hash

    def compile(
        self,
        review_bundle: Any | None,
        attestation: Any | None,
        signed_review: Any | None,
        source_certificate: Any | None,
        reviewer_registry: Any,
        authority_registry: Any,
    ) -> TimingProfileSourceCertificationReport:
        s4_report = SbcTimingProfileSignedReviewVerifier().compile(
            review_bundle,
            attestation,
            signed_review,
            reviewer_registry,
        )
        s4_ready = (
            s4_report.review_status == READY_FOR_MANUAL_SOURCE_CERTIFICATION
            and s4_report.ready_for_manual_source_certification
        )
        gates = [
            self._gate(
                "s4_signed_review",
                "S4 trusted signed review",
                PASS_STATE if s4_ready else FAIL_STATE,
                (
                    "S4 trusted-review evidence is complete."
                    if s4_ready
                    else (
                        "S4 must report "
                        "READY_FOR_MANUAL_SOURCE_CERTIFICATION first."
                    )
                ),
            )
        ]

        authorities: dict[str, _TrustedCertificationAuthority] | None = None
        try:
            authorities = validate_certification_authority_registry(
                authority_registry
            )
            gates.append(
                self._gate(
                    "certification_authority_registry",
                    "Server certification-authority registry",
                    PASS_STATE,
                    (
                        "The server registry is valid with "
                        f"{len(authorities)} certification key(s)."
                    ),
                )
            )
        except (TypeError, ValueError) as exc:
            gates.append(
                self._gate(
                    "certification_authority_registry",
                    "Server certification-authority registry",
                    FAIL_STATE,
                    str(exc),
                )
            )

        certificate: dict[str, Any] | None = None
        certified_at: datetime | None = None
        binding_error: str | None = None
        if source_certificate is None:
            gates.append(
                self._gate(
                    "source_certificate_binding",
                    "Source-certificate evidence binding",
                    UNKNOWN_STATE,
                    "A separately signed source certificate is required.",
                )
            )
        elif not s4_ready:
            gates.append(
                self._gate(
                    "source_certificate_binding",
                    "Source-certificate evidence binding",
                    UNKNOWN_STATE,
                    "S4 must pass before certificate binding can be checked.",
                )
            )
        else:
            try:
                certificate, certified_at = self._validate_binding(
                    source_certificate,
                    s4_report,
                    signed_review,
                )
                gates.append(
                    self._gate(
                        "source_certificate_binding",
                        "Source-certificate evidence binding",
                        PASS_STATE,
                        (
                            "The certificate binds the exact S1 through S4 "
                            "evidence chain."
                        ),
                    )
                )
            except (TypeError, ValueError) as exc:
                binding_error = str(exc)
                gates.append(
                    self._gate(
                        "source_certificate_binding",
                        "Source-certificate evidence binding",
                        FAIL_STATE,
                        binding_error,
                    )
                )

        authority: _TrustedCertificationAuthority | None = None
        trust_error: str | None = None
        if certificate is None or certified_at is None:
            gates.append(
                self._gate(
                    "trusted_certification_authority",
                    "Trusted certification authority",
                    UNKNOWN_STATE,
                    "A valid certificate binding is required.",
                )
            )
        elif authorities is None:
            gates.append(
                self._gate(
                    "trusted_certification_authority",
                    "Trusted certification authority",
                    UNKNOWN_STATE,
                    "A valid server authority registry is required.",
                )
            )
        else:
            try:
                authority = self._trusted_authority(
                    certificate,
                    certified_at,
                    authorities,
                    s4_report,
                )
                gates.append(
                    self._gate(
                        "trusted_certification_authority",
                        "Trusted certification authority",
                        PASS_STATE,
                        (
                            "The non-revoked authority key is valid, scoped, "
                            "and identity matched."
                        ),
                    )
                )
            except LookupError as exc:
                trust_error = str(exc)
                gates.append(
                    self._gate(
                        "trusted_certification_authority",
                        "Trusted certification authority",
                        FAIL_STATE,
                        trust_error,
                    )
                )

        separation_valid = False
        separation_error: str | None = None
        if certificate is None or authority is None:
            gates.append(
                self._gate(
                    "separation_of_duties",
                    "Reviewer and certifier separation",
                    UNKNOWN_STATE,
                    "Trusted review and certification keys are required.",
                )
            )
        else:
            reviewer_key_id = str(certificate.get("reviewerKeyId") or "")
            reviewer_identity = str(
                (signed_review or {}).get("reviewerIdentity") or ""
            )
            if authority.authority_key_id == reviewer_key_id:
                separation_error = "certifier key must differ from reviewer key"
            elif authority.authority_identity == reviewer_identity:
                separation_error = (
                    "certifier identity must differ from reviewer identity"
                )
            elif not authority.separation_of_duties_vetted:
                separation_error = "authority separation of duties is not vetted"
            else:
                separation_valid = True
            gates.append(
                self._gate(
                    "separation_of_duties",
                    "Reviewer and certifier separation",
                    PASS_STATE if separation_valid else FAIL_STATE,
                    (
                        "Distinct reviewer and authority keys and identities "
                        "are administratively vetted."
                        if separation_valid
                        else str(separation_error)
                    ),
                )
            )

        signature_valid = False
        signature_error: str | None = None
        if certificate is None:
            gates.append(
                self._gate(
                    "ed25519_certification_signature",
                    "Ed25519 certification signature",
                    UNKNOWN_STATE,
                    "A valid certificate binding is required.",
                )
            )
        elif authority is None:
            gates.append(
                self._gate(
                    "ed25519_certification_signature",
                    "Ed25519 certification signature",
                    UNKNOWN_STATE,
                    "A trusted certification-authority key is required.",
                )
            )
        else:
            try:
                self._verify_signature(certificate, authority)
                signature_valid = True
                gates.append(
                    self._gate(
                        "ed25519_certification_signature",
                        "Ed25519 certification signature",
                        PASS_STATE,
                        (
                            "The registered authority key signed the exact "
                            "canonical source certificate."
                        ),
                    )
                )
            except (TypeError, ValueError) as exc:
                signature_error = str(exc)
                gates.append(
                    self._gate(
                        "ed25519_certification_signature",
                        "Ed25519 certification signature",
                        FAIL_STATE,
                        signature_error,
                    )
                )

        decision = (
            str(certificate.get("certificationDecision"))
            if certificate is not None
            else None
        )
        decision_certified = decision == "CERTIFIED"
        if certificate is None:
            decision_state = UNKNOWN_STATE
            decision_detail = "A valid signed certificate decision is required."
        elif decision_certified:
            decision_state = PASS_STATE
            decision_detail = "The trusted authority recorded CERTIFIED."
        elif decision == "REJECTED":
            decision_state = FAIL_STATE
            decision_detail = "The trusted authority recorded REJECTED."
        else:
            decision_state = FAIL_STATE
            decision_detail = "The certification decision is invalid."
        gates.append(
            self._gate(
                "source_certification_decision",
                "Source-certification decision",
                decision_state,
                decision_detail,
            )
        )
        gates.append(
            self._gate(
                "manual_registry_admission_boundary",
                "Manual timing-registry admission boundary",
                PASS_STATE,
                (
                    "A valid certificate can emit only a proposal. A separate "
                    "human-reviewed Git change is required to register it."
                ),
            )
        )

        ready = (
            s4_ready
            and authorities is not None
            and authority is not None
            and separation_valid
            and signature_valid
            and decision_certified
            and all(gate.state == PASS_STATE for gate in gates)
        )
        if not s4_ready:
            status = S4_NOT_READY
        elif source_certificate is None:
            status = NO_SOURCE_CERTIFICATE
        elif binding_error is not None:
            status = CERTIFICATE_INVALID
        elif trust_error is not None or separation_error is not None:
            status = CERTIFICATION_AUTHORITY_UNTRUSTED
        elif signature_error is not None:
            status = CERTIFICATE_INVALID
        elif decision == "REJECTED" and signature_valid:
            status = SOURCE_CERTIFICATION_REJECTED
        elif ready:
            status = READY_FOR_PROFILE_REGISTRY_ADMISSION
        else:
            status = CERTIFICATE_INVALID

        certificate_hash = (
            source_certificate_sha256(certificate) if certificate else None
        )
        registry_proposal: dict[str, Any] | None = None
        registry_proposal_hash: str | None = None
        if ready and certificate_hash is not None:
            registry_proposal, registry_proposal_hash = self._registry_proposal(
                s4_report,
                certificate_hash,
            )

        return TimingProfileSourceCertificationReport(
            certification_status=status,
            profile_id=s4_report.profile_id,
            profile_version=s4_report.profile_version,
            candidate_profile_hash=s4_report.candidate_profile_hash,
            packet_id=s4_report.packet_id,
            packet_hash=s4_report.packet_hash,
            review_bundle_sha256=s4_report.review_bundle_sha256,
            attestation_sha256=s4_report.attestation_sha256,
            certification_proposal_sha256=(
                s4_report.certification_proposal_sha256
            ),
            signed_review_sha256=s4_report.signed_review_sha256,
            source_certificate_sha256=certificate_hash,
            registry_admission_proposal_sha256=registry_proposal_hash,
            s4_ready=s4_ready,
            authority_registry_valid=authorities is not None,
            authority_key_trusted=authority is not None,
            certificate_signature_valid=signature_valid,
            separation_of_duties_vetted=separation_valid,
            certification_decision=decision,
            source_certified=ready,
            ready_for_profile_registry_admission=ready,
            validation_gates=tuple(gates),
            missing_requirements=tuple(
                gate.label for gate in gates if gate.state != PASS_STATE
            ),
            source_certificate_template=_certificate_template(
                s4_report,
                signed_review,
            ),
            registry_entry_proposal=registry_proposal,
        )
