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
from .timing_profile_external_review import (
    READY_FOR_HUMAN_CERTIFICATION_DECISION,
    SbcTimingProfileExternalReviewVerifier,
    TimingProfileExternalReviewReport,
)
from .timing_profile_source_packet import FAIL_STATE, PASS_STATE, UNKNOWN_STATE


SIGNED_REVIEW_REPORT_CONTRACT = "SBC_TIMING_PROFILE_SIGNED_REVIEW_REPORT_V1"
SIGNED_REVIEW_REPORT_SCHEMA_VERSION = 1
SIGNED_REVIEW_ENVELOPE_CONTRACT = "SBC_TIMING_PROFILE_SIGNED_REVIEW_V1"
SIGNED_REVIEW_ENVELOPE_SCHEMA_VERSION = 1
SIGNED_REVIEW_POLICY = "ED25519_SERVER_TRUST_REGISTRY_EXACT_S3_BINDING_V1"
SIGNED_REVIEW_HASH_METHOD = (
    "CANONICAL_JSON_ED25519_WITH_SIGNATURE_BASE64_BLANK"
)
REVIEWER_TRUST_REGISTRY_CONTRACT = (
    "SBC_TIMING_PROFILE_REVIEWER_TRUST_REGISTRY_V1"
)
REVIEWER_TRUST_REGISTRY_SCHEMA_VERSION = 1

NO_SIGNED_REVIEW = "NO_SIGNED_REVIEW"
S3_NOT_READY = "S3_NOT_READY"
SIGNATURE_INVALID = "SIGNATURE_INVALID"
REVIEWER_KEY_UNTRUSTED = "REVIEWER_KEY_UNTRUSTED"
READY_FOR_MANUAL_SOURCE_CERTIFICATION = (
    "READY_FOR_MANUAL_SOURCE_CERTIFICATION"
)

_REGISTRY_KEYS = {
    "contract",
    "schemaVersion",
    "reviewers",
    "registryWriteAllowed",
    "executionAllowed",
}
_REVIEWER_KEYS = {
    "reviewerKeyId",
    "publicKeyBase64",
    "reviewerIdentity",
    "reviewerOrganization",
    "independenceVetted",
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
_SIGNED_REVIEW_KEYS = {
    "contract",
    "schemaVersion",
    "signaturePolicy",
    "signatureHashMethod",
    "reviewBundleSha256",
    "attestationSha256",
    "certificationProposalSha256",
    "profileId",
    "profileVersion",
    "profileHash",
    "packetId",
    "packetHash",
    "reviewerKeyId",
    "reviewerIdentity",
    "reviewerOrganization",
    "reviewerIndependenceConfirmed",
    "reviewedAtUtc",
    "signedAtUtc",
    "signatureBase64",
    "sourceCertified",
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
        raise ValueError(
            f"{label} must decode to {expected_length} bytes"
        )
    return decoded


def _unique_texts(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty array")
    normalized = tuple(
        _required_text(item, f"{label}[{index}]")
        for index, item in enumerate(value)
    )
    if len(set(normalized)) != len(normalized):
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


def reviewer_key_id(public_key_bytes: bytes) -> str:
    if not isinstance(public_key_bytes, bytes) or len(public_key_bytes) != 32:
        raise ValueError("reviewer public key must contain 32 bytes")
    return hashlib.sha256(public_key_bytes).hexdigest().upper()


def signed_review_message(envelope: Mapping[str, Any]) -> bytes:
    if not isinstance(envelope, Mapping):
        raise ValueError("signed review must be an object")
    normalized = json.loads(
        json.dumps(envelope, ensure_ascii=True, allow_nan=False)
    )
    _strict_object(normalized, _SIGNED_REVIEW_KEYS, "signed review")
    if normalized.get("contract") != SIGNED_REVIEW_ENVELOPE_CONTRACT:
        raise ValueError("signed review contract is unsupported")
    if (
        normalized.get("schemaVersion")
        != SIGNED_REVIEW_ENVELOPE_SCHEMA_VERSION
    ):
        raise ValueError("signed review schemaVersion is unsupported")
    if normalized.get("signaturePolicy") != SIGNED_REVIEW_POLICY:
        raise ValueError("signed review signature policy is unsupported")
    if normalized.get("signatureHashMethod") != SIGNED_REVIEW_HASH_METHOD:
        raise ValueError("signed review hash method is unsupported")
    normalized["signatureBase64"] = ""
    return _canonical_json(normalized)


def signed_review_sha256(envelope: Mapping[str, Any]) -> str:
    if not isinstance(envelope, Mapping):
        raise ValueError("signed review must be an object")
    return _canonical_hash(envelope)


@dataclass(frozen=True)
class TimingSignedReviewGate:
    gate_id: str
    state: str
    mandatory: bool
    label: str
    detail: str

    def __post_init__(self) -> None:
        if self.state not in {PASS_STATE, FAIL_STATE, UNKNOWN_STATE}:
            raise ValueError(f"unknown gate state: {self.state}")
        object.__setattr__(
            self,
            "gate_id",
            _required_text(self.gate_id, "gate_id"),
        )
        object.__setattr__(
            self,
            "label",
            _required_text(self.label, "label"),
        )
        object.__setattr__(
            self,
            "detail",
            _required_text(self.detail, "detail"),
        )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingProfileSignedReviewReport:
    review_status: str
    profile_id: str | None
    profile_version: str | None
    candidate_profile_hash: str | None
    packet_id: str | None
    packet_hash: str | None
    review_bundle_sha256: str | None
    attestation_sha256: str | None
    certification_proposal_sha256: str | None
    signed_review_sha256: str | None
    s3_ready: bool
    reviewer_registry_valid: bool
    reviewer_key_trusted: bool
    review_signature_valid: bool
    reviewer_identity_authenticated_to_registry: bool
    reviewer_independence_administratively_vetted: bool
    ready_for_manual_source_certification: bool
    validation_gates: tuple[TimingSignedReviewGate, ...]
    missing_requirements: tuple[str, ...]
    signed_review_template: dict[str, Any] | None
    contract: str = SIGNED_REVIEW_REPORT_CONTRACT
    schema_version: int = SIGNED_REVIEW_REPORT_SCHEMA_VERSION
    signature_policy: str = SIGNED_REVIEW_POLICY
    classification: str = RESEARCH_CLASSIFICATION
    external_review_independently_proven: bool = False
    source_certified: bool = False
    profile_registered: bool = False
    registry_write_allowed: bool = False
    guardrails: dict[str, Any] = field(
        default_factory=lambda: {
            "research_only": True,
            "read_only": True,
            "payloads_persisted": False,
            "client_public_key_accepted": False,
            "server_trust_registry_required": True,
            "signature_proves_registered_key_binding_only": True,
            "reviewer_independence_cryptographically_proven": False,
            "external_review_independently_proven": False,
            "source_certified": False,
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
                "INDEPENDENCE_PROOF",
                "SOURCE_CERTIFICATION",
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
        if self.external_review_independently_proven:
            raise ValueError("S4 cannot independently prove reviewer independence")
        if self.source_certified:
            raise ValueError("S4 cannot certify source doctrine")
        if self.profile_registered or self.registry_write_allowed:
            raise ValueError("S4 cannot register a timing profile")
        if self.guardrails.get("client_public_key_accepted") is not False:
            raise ValueError("S4 cannot trust a client-supplied public key")
        if self.guardrails.get("execution_allowed") is not False:
            raise ValueError("S4 execution must remain locked")
        if float(self.guardrails.get("directional_contribution", 1.0)) != 0.0:
            raise ValueError("S4 cannot contribute market direction")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class _TrustedReviewer:
    reviewer_key_id: str
    public_key: bytes
    reviewer_identity: str
    reviewer_organization: str
    valid_from_utc: datetime
    valid_until_utc: datetime
    authorized_profile_ids: tuple[str, ...]
    authorized_packet_ids: tuple[str, ...]
    independence_vetted: bool
    revoked: bool


def validate_reviewer_trust_registry(
    registry_payload: Any,
) -> dict[str, _TrustedReviewer]:
    registry = _strict_object(
        registry_payload,
        _REGISTRY_KEYS,
        "reviewer trust registry",
    )
    if registry.get("contract") != REVIEWER_TRUST_REGISTRY_CONTRACT:
        raise ValueError("reviewer trust registry contract is unsupported")
    if (
        registry.get("schemaVersion")
        != REVIEWER_TRUST_REGISTRY_SCHEMA_VERSION
    ):
        raise ValueError(
            "reviewer trust registry schemaVersion is unsupported"
        )
    if registry.get("registryWriteAllowed") is not False:
        raise ValueError("reviewer trust registry cannot allow writes")
    if registry.get("executionAllowed") is not False:
        raise ValueError("reviewer trust registry cannot allow execution")
    reviewers = registry.get("reviewers")
    if not isinstance(reviewers, list):
        raise ValueError("reviewer trust registry reviewers must be an array")

    result: dict[str, _TrustedReviewer] = {}
    for index, raw_entry in enumerate(reviewers):
        label = f"reviewers[{index}]"
        entry = _strict_object(raw_entry, _REVIEWER_KEYS, label)
        key_id = _sha256(entry.get("reviewerKeyId"), f"{label}.reviewerKeyId")
        if key_id in result:
            raise ValueError("reviewer trust registry contains duplicate key IDs")
        public_key = _base64_bytes(
            entry.get("publicKeyBase64"),
            f"{label}.publicKeyBase64",
            expected_length=32,
        )
        if reviewer_key_id(public_key) != key_id:
            raise ValueError(f"{label}.reviewerKeyId does not match its public key")
        identity = _required_text(
            entry.get("reviewerIdentity"),
            f"{label}.reviewerIdentity",
        )
        organization = _required_text(
            entry.get("reviewerOrganization"),
            f"{label}.reviewerOrganization",
        )
        if entry.get("independenceVetted") is not True:
            raise ValueError(f"{label}.independenceVetted must be true")
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
        result[key_id] = _TrustedReviewer(
            reviewer_key_id=key_id,
            public_key=public_key,
            reviewer_identity=identity,
            reviewer_organization=organization,
            valid_from_utc=valid_from,
            valid_until_utc=valid_until,
            authorized_profile_ids=profile_ids,
            authorized_packet_ids=packet_ids,
            independence_vetted=True,
            revoked=revoked,
        )
    return result


def _signed_review_template(
    report: TimingProfileExternalReviewReport,
) -> dict[str, Any] | None:
    proposal = report.certification_proposal
    if (
        report.review_status != READY_FOR_HUMAN_CERTIFICATION_DECISION
        or not isinstance(proposal, dict)
    ):
        return None
    evidence = proposal.get("reviewEvidence")
    profile = proposal.get("profile")
    packet = proposal.get("sourcePacket")
    if not all(isinstance(item, dict) for item in (evidence, profile, packet)):
        return None
    return {
        "contract": SIGNED_REVIEW_ENVELOPE_CONTRACT,
        "schemaVersion": SIGNED_REVIEW_ENVELOPE_SCHEMA_VERSION,
        "signaturePolicy": SIGNED_REVIEW_POLICY,
        "signatureHashMethod": SIGNED_REVIEW_HASH_METHOD,
        "reviewBundleSha256": report.review_bundle_sha256,
        "attestationSha256": report.attestation_sha256,
        "certificationProposalSha256": (
            report.certification_proposal_sha256
        ),
        "profileId": report.profile_id,
        "profileVersion": report.profile_version,
        "profileHash": report.candidate_profile_hash,
        "packetId": report.packet_id,
        "packetHash": report.packet_hash,
        "reviewerKeyId": "",
        "reviewerIdentity": evidence.get("reviewerIdentityClaim"),
        "reviewerOrganization": evidence.get("reviewerOrganizationClaim"),
        "reviewerIndependenceConfirmed": True,
        "reviewedAtUtc": evidence.get("reviewedAtUtc"),
        "signedAtUtc": "",
        "signatureBase64": "",
        "sourceCertified": False,
        "registryWriteAllowed": False,
        "executionAllowed": False,
    }


class SbcTimingProfileSignedReviewVerifier:
    @staticmethod
    def _gate(
        gate_id: str,
        label: str,
        state: str,
        detail: str,
    ) -> TimingSignedReviewGate:
        return TimingSignedReviewGate(
            gate_id=gate_id,
            state=state,
            mandatory=True,
            label=label,
            detail=detail,
        )

    @staticmethod
    def _validate_binding(
        envelope_payload: Any,
        report: TimingProfileExternalReviewReport,
    ) -> tuple[dict[str, Any], datetime]:
        envelope = _strict_object(
            envelope_payload,
            _SIGNED_REVIEW_KEYS,
            "signed review",
        )
        signed_review_message(envelope)
        expected = _signed_review_template(report)
        if expected is None:
            raise ValueError("S3 is not ready for a signed review")

        linked_fields = {
            "reviewBundleSha256",
            "attestationSha256",
            "certificationProposalSha256",
            "profileId",
            "profileVersion",
            "profileHash",
            "packetId",
            "packetHash",
            "reviewerIdentity",
            "reviewerOrganization",
            "reviewerIndependenceConfirmed",
            "reviewedAtUtc",
            "sourceCertified",
            "registryWriteAllowed",
            "executionAllowed",
        }
        for field_name in linked_fields:
            if envelope.get(field_name) != expected.get(field_name):
                raise ValueError(
                    f"signed review {field_name} does not match S3 evidence"
                )
        for field_name in (
            "reviewBundleSha256",
            "attestationSha256",
            "certificationProposalSha256",
            "profileHash",
            "packetHash",
            "reviewerKeyId",
        ):
            _sha256(envelope.get(field_name), f"signed review.{field_name}")
        _, reviewed_at = _utc_timestamp(
            envelope.get("reviewedAtUtc"),
            "signed review.reviewedAtUtc",
        )
        _, signed_at = _utc_timestamp(
            envelope.get("signedAtUtc"),
            "signed review.signedAtUtc",
        )
        if signed_at < reviewed_at:
            raise ValueError("signedAtUtc cannot be earlier than reviewedAtUtc")
        _base64_bytes(
            envelope.get("signatureBase64"),
            "signed review.signatureBase64",
            expected_length=64,
        )
        return envelope, signed_at

    @staticmethod
    def _trusted_reviewer(
        envelope: dict[str, Any],
        signed_at: datetime,
        reviewers: dict[str, _TrustedReviewer],
        report: TimingProfileExternalReviewReport,
    ) -> _TrustedReviewer:
        key_id = envelope["reviewerKeyId"]
        reviewer = reviewers.get(key_id)
        if reviewer is None:
            raise LookupError("reviewer key is not present in the server registry")
        if reviewer.revoked:
            raise LookupError("reviewer key is revoked")
        if not (
            reviewer.valid_from_utc
            <= signed_at
            <= reviewer.valid_until_utc
        ):
            raise LookupError("reviewer key is outside its validity interval")
        if reviewer.reviewer_identity != envelope["reviewerIdentity"]:
            raise LookupError("reviewer identity does not match the trusted key")
        if (
            reviewer.reviewer_organization
            != envelope["reviewerOrganization"]
        ):
            raise LookupError(
                "reviewer organization does not match the trusted key"
            )
        if report.profile_id not in reviewer.authorized_profile_ids:
            raise LookupError("reviewer key is not authorized for this profile")
        if report.packet_id not in reviewer.authorized_packet_ids:
            raise LookupError(
                "reviewer key is not authorized for this source packet"
            )
        return reviewer

    @staticmethod
    def _verify_signature(
        envelope: dict[str, Any],
        reviewer: _TrustedReviewer,
    ) -> None:
        signature = _base64_bytes(
            envelope.get("signatureBase64"),
            "signed review.signatureBase64",
            expected_length=64,
        )
        try:
            Ed25519PublicKey.from_public_bytes(reviewer.public_key).verify(
                signature,
                signed_review_message(envelope),
            )
        except InvalidSignature as exc:
            raise ValueError("Ed25519 review signature is invalid") from exc

    def compile(
        self,
        review_bundle: Any | None,
        attestation: Any | None,
        signed_review: Any | None,
        reviewer_registry: Any,
    ) -> TimingProfileSignedReviewReport:
        s3_report = SbcTimingProfileExternalReviewVerifier().compile(
            review_bundle,
            attestation,
        )
        s3_ready = (
            s3_report.review_status
            == READY_FOR_HUMAN_CERTIFICATION_DECISION
            and s3_report.ready_for_human_certification_decision
        )
        gates = [
            self._gate(
                "s3_external_review",
                "S3 external-review evidence",
                PASS_STATE if s3_ready else FAIL_STATE,
                (
                    "S3 approved evidence is complete and reproducible."
                    if s3_ready
                    else (
                        "S3 must report "
                        "READY_FOR_HUMAN_CERTIFICATION_DECISION first."
                    )
                ),
            )
        ]

        reviewers: dict[str, _TrustedReviewer] | None = None
        try:
            reviewers = validate_reviewer_trust_registry(reviewer_registry)
            gates.append(
                self._gate(
                    "reviewer_trust_registry",
                    "Server reviewer trust registry",
                    PASS_STATE,
                    (
                        "The server registry is valid with "
                        f"{len(reviewers)} trusted key(s)."
                    ),
                )
            )
        except (TypeError, ValueError) as exc:
            gates.append(
                self._gate(
                    "reviewer_trust_registry",
                    "Server reviewer trust registry",
                    FAIL_STATE,
                    str(exc),
                )
            )

        envelope: dict[str, Any] | None = None
        signed_at: datetime | None = None
        binding_error: str | None = None
        if signed_review is None:
            gates.append(
                self._gate(
                    "signed_review_binding",
                    "Signed-review evidence binding",
                    UNKNOWN_STATE,
                    "A separately signed review envelope is required.",
                )
            )
        elif not s3_ready:
            gates.append(
                self._gate(
                    "signed_review_binding",
                    "Signed-review evidence binding",
                    UNKNOWN_STATE,
                    "S3 must pass before signature binding can be checked.",
                )
            )
        else:
            try:
                envelope, signed_at = self._validate_binding(
                    signed_review,
                    s3_report,
                )
                gates.append(
                    self._gate(
                        "signed_review_binding",
                        "Signed-review evidence binding",
                        PASS_STATE,
                        (
                            "The envelope binds the exact S3 bundle, "
                            "attestation, proposal, profile, and packet."
                        ),
                    )
                )
            except (TypeError, ValueError) as exc:
                binding_error = str(exc)
                gates.append(
                    self._gate(
                        "signed_review_binding",
                        "Signed-review evidence binding",
                        FAIL_STATE,
                        binding_error,
                    )
                )

        trusted_reviewer: _TrustedReviewer | None = None
        trust_error: str | None = None
        if envelope is None or signed_at is None:
            gates.append(
                self._gate(
                    "trusted_reviewer_key",
                    "Trusted reviewer key and scope",
                    UNKNOWN_STATE,
                    "A valid signed-review binding is required.",
                )
            )
        elif reviewers is None:
            gates.append(
                self._gate(
                    "trusted_reviewer_key",
                    "Trusted reviewer key and scope",
                    UNKNOWN_STATE,
                    "A valid server reviewer registry is required.",
                )
            )
        else:
            try:
                trusted_reviewer = self._trusted_reviewer(
                    envelope,
                    signed_at,
                    reviewers,
                    s3_report,
                )
                gates.append(
                    self._gate(
                        "trusted_reviewer_key",
                        "Trusted reviewer key and scope",
                        PASS_STATE,
                        (
                            "The non-revoked server key is valid, identity "
                            "matched, and authorized for this profile and packet."
                        ),
                    )
                )
            except LookupError as exc:
                trust_error = str(exc)
                gates.append(
                    self._gate(
                        "trusted_reviewer_key",
                        "Trusted reviewer key and scope",
                        FAIL_STATE,
                        trust_error,
                    )
                )

        signature_valid = False
        signature_error: str | None = None
        if envelope is None:
            gates.append(
                self._gate(
                    "ed25519_signature",
                    "Ed25519 review signature",
                    UNKNOWN_STATE,
                    "A valid signed-review binding is required.",
                )
            )
        elif trusted_reviewer is None:
            gates.append(
                self._gate(
                    "ed25519_signature",
                    "Ed25519 review signature",
                    UNKNOWN_STATE,
                    "A trusted server reviewer key is required.",
                )
            )
        else:
            try:
                self._verify_signature(envelope, trusted_reviewer)
                signature_valid = True
                gates.append(
                    self._gate(
                        "ed25519_signature",
                        "Ed25519 review signature",
                        PASS_STATE,
                        (
                            "The registered reviewer key signed the exact "
                            "canonical S3 evidence envelope."
                        ),
                    )
                )
            except (TypeError, ValueError) as exc:
                signature_error = str(exc)
                gates.append(
                    self._gate(
                        "ed25519_signature",
                        "Ed25519 review signature",
                        FAIL_STATE,
                        signature_error,
                    )
                )

        gates.append(
            self._gate(
                "manual_source_certification_boundary",
                "Manual source-certification boundary",
                PASS_STATE,
                (
                    "A valid signature proves a registered-key binding only. "
                    "Independence, doctrine, certification, registration, "
                    "inference, and execution remain separate human gates."
                ),
            )
        )

        ready = (
            s3_ready
            and reviewers is not None
            and trusted_reviewer is not None
            and signature_valid
            and all(gate.state == PASS_STATE for gate in gates)
        )
        if not s3_ready:
            status = S3_NOT_READY
        elif signed_review is None:
            status = NO_SIGNED_REVIEW
        elif binding_error is not None or signature_error is not None:
            status = SIGNATURE_INVALID
        elif trust_error is not None or reviewers is None:
            status = REVIEWER_KEY_UNTRUSTED
        elif ready:
            status = READY_FOR_MANUAL_SOURCE_CERTIFICATION
        else:
            status = SIGNATURE_INVALID

        return TimingProfileSignedReviewReport(
            review_status=status,
            profile_id=s3_report.profile_id,
            profile_version=s3_report.profile_version,
            candidate_profile_hash=s3_report.candidate_profile_hash,
            packet_id=s3_report.packet_id,
            packet_hash=s3_report.packet_hash,
            review_bundle_sha256=s3_report.review_bundle_sha256,
            attestation_sha256=s3_report.attestation_sha256,
            certification_proposal_sha256=(
                s3_report.certification_proposal_sha256
            ),
            signed_review_sha256=(
                signed_review_sha256(envelope) if envelope else None
            ),
            s3_ready=s3_ready,
            reviewer_registry_valid=reviewers is not None,
            reviewer_key_trusted=trusted_reviewer is not None,
            review_signature_valid=signature_valid,
            reviewer_identity_authenticated_to_registry=(
                trusted_reviewer is not None and signature_valid
            ),
            reviewer_independence_administratively_vetted=(
                bool(
                    trusted_reviewer
                    and trusted_reviewer.independence_vetted
                    and signature_valid
                )
            ),
            ready_for_manual_source_certification=ready,
            validation_gates=tuple(gates),
            missing_requirements=tuple(
                gate.label for gate in gates if gate.state != PASS_STATE
            ),
            signed_review_template=_signed_review_template(s3_report),
        )
