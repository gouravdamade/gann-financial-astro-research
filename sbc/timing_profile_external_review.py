from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from .atomic_intervals import RESEARCH_CLASSIFICATION
from .models import to_primitive
from .timing_profile_source_packet import (
    FAIL_STATE,
    PASS_STATE,
    UNKNOWN_STATE,
    SbcTimingProfileSourcePacketGate,
)
from .timing_profile_source_verification import (
    EXCERPT_HASH_METHOD,
    EXTERNAL_REVIEW_ATTESTATION_CONTRACT,
    INDEPENDENT_REVIEW_BUNDLE_CONTRACT,
    INDEPENDENT_REVIEW_BUNDLE_SCHEMA_VERSION,
    REVIEW_BUNDLE_HASH_METHOD,
    SOURCE_HASH_METHOD,
    SOURCE_VERIFICATION_POLICY,
    independent_review_bundle_hash,
)


EXTERNAL_REVIEW_REPORT_CONTRACT = (
    "SBC_TIMING_PROFILE_EXTERNAL_REVIEW_REPORT_V1"
)
EXTERNAL_REVIEW_REPORT_SCHEMA_VERSION = 1
EXTERNAL_REVIEW_POLICY = (
    "INTERNAL_COHERENCE_AND_EXACT_DECISION_COVERAGE_V1"
)

CERTIFICATION_PROPOSAL_CONTRACT = (
    "SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_PROPOSAL_V1"
)
CERTIFICATION_PROPOSAL_SCHEMA_VERSION = 1
CERTIFICATION_PROPOSAL_HASH_METHOD = (
    "CANONICAL_JSON_SHA256_WITH_PROPOSAL_SHA256_BLANK"
)

NO_ATTESTATION = "NO_ATTESTATION"
ATTESTATION_INVALID = "ATTESTATION_INVALID"
REVIEW_REJECTED = "REVIEW_REJECTED"
READY_FOR_HUMAN_CERTIFICATION_DECISION = (
    "READY_FOR_HUMAN_CERTIFICATION_DECISION"
)

APPROVED = "APPROVED"
REJECTED = "REJECTED"
FINAL_DECISIONS = {"PASS", "FAIL"}

_ATTESTATION_KEYS = {
    "contract",
    "schemaVersion",
    "bundleSha256",
    "reviewDecision",
    "reviewerIdentity",
    "reviewerOrganization",
    "reviewerIndependenceConfirmed",
    "reviewedAtUtc",
    "sourceArtifactDecisions",
    "claimDecisions",
    "conflictDecisions",
    "overallNote",
    "registryWriteAllowed",
}
_SOURCE_DECISION_KEYS = {"sourceId", "decision", "note"}
_CLAIM_DECISION_KEYS = {"claimId", "decision", "note"}
_CONFLICT_DECISION_KEYS = {"conflictId", "decision", "note"}


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def source_certification_proposal_hash(proposal: Mapping[str, Any]) -> str:
    if not isinstance(proposal, Mapping):
        raise ValueError("source certification proposal must be an object")
    normalized = json.loads(
        json.dumps(
            proposal,
            ensure_ascii=True,
            allow_nan=False,
        )
    )
    if normalized.get("contract") != CERTIFICATION_PROPOSAL_CONTRACT:
        raise ValueError("source certification proposal contract is unsupported")
    if (
        normalized.get("schemaVersion")
        != CERTIFICATION_PROPOSAL_SCHEMA_VERSION
    ):
        raise ValueError(
            "source certification proposal schemaVersion is unsupported"
        )
    if "proposalSha256" not in normalized:
        raise ValueError("source certification proposalSha256 is required")
    normalized["proposalSha256"] = ""
    return _canonical_hash(normalized)


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


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _utc_timestamp(value: Any, label: str) -> str:
    normalized = _required_text(value, label)
    if not normalized.endswith("Z"):
        raise ValueError(f"{label} must end in Z")
    datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    return normalized


def _unique_map(
    rows: Any,
    id_key: str,
    label: str,
) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError(f"{label} must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        item_id = _required_text(row.get(id_key), f"{label}[{index}].{id_key}")
        if item_id in result:
            raise ValueError(f"{label} contains duplicate {id_key} {item_id}")
        result[item_id] = row
    return result


def _packet_sources(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = _unique_map(packet.get("sourceArtifacts"), "sourceId", "sourceArtifacts")
    if not rows:
        raise ValueError("sourceArtifacts must not be empty")
    return rows


def _packet_claims(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = _unique_map(packet.get("claims"), "claimId", "claims")
    if not rows:
        raise ValueError("claims must not be empty")
    return rows


def _packet_conflicts(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return _unique_map(
        packet.get("conflictRegister"),
        "conflictId",
        "conflictRegister",
    )


@dataclass(frozen=True)
class TimingExternalReviewGate:
    gate_id: str
    state: str
    mandatory: bool
    label: str
    detail: str
    affected_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in {PASS_STATE, FAIL_STATE, UNKNOWN_STATE}:
            raise ValueError(f"unknown gate state: {self.state}")
        object.__setattr__(self, "gate_id", _required_text(self.gate_id, "gate_id"))
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "detail", _required_text(self.detail, "detail"))
        object.__setattr__(
            self,
            "affected_ids",
            tuple(
                _required_text(item, "affected_id")
                for item in self.affected_ids
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingProfileExternalReviewReport:
    review_status: str
    profile_id: str | None
    profile_version: str | None
    candidate_profile_hash: str | None
    packet_id: str | None
    packet_hash: str | None
    review_bundle_sha256: str | None
    attestation_sha256: str | None
    bundle_integrity_verified: bool
    embedded_s1_ready: bool
    s2_rows_verified: bool
    attestation_complete: bool
    review_approved: bool
    ready_for_human_certification_decision: bool
    validation_gates: tuple[TimingExternalReviewGate, ...]
    missing_requirements: tuple[str, ...]
    certification_proposal: dict[str, Any] | None
    certification_proposal_sha256: str | None
    contract: str = EXTERNAL_REVIEW_REPORT_CONTRACT
    schema_version: int = EXTERNAL_REVIEW_REPORT_SCHEMA_VERSION
    review_policy: str = EXTERNAL_REVIEW_POLICY
    classification: str = RESEARCH_CLASSIFICATION
    reviewer_identity_authenticated: bool = False
    external_review_independently_proven: bool = False
    source_certified: bool = False
    profile_registered: bool = False
    registry_write_allowed: bool = False
    guardrails: dict[str, Any] = field(
        default_factory=lambda: {
            "research_only": True,
            "read_only": True,
            "payloads_persisted": False,
            "reviewer_identity_authenticated": False,
            "reviewer_independence_authenticated": False,
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
                "REVIEWER_IDENTITY_AUTHENTICATION",
                "REVIEWER_INDEPENDENCE_AUTHENTICATION",
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
        if self.reviewer_identity_authenticated:
            raise ValueError("S3 cannot authenticate reviewer identity")
        if self.external_review_independently_proven:
            raise ValueError("S3 cannot independently prove external review")
        if self.source_certified:
            raise ValueError("S3 cannot certify source doctrine")
        if self.profile_registered or self.registry_write_allowed:
            raise ValueError("S3 cannot register a timing profile")
        if self.guardrails.get("execution_allowed") is not False:
            raise ValueError("S3 execution must remain locked")
        if float(self.guardrails.get("directional_contribution", 1.0)) != 0.0:
            raise ValueError("S3 cannot contribute market direction")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class _BundleContext:
    bundle: dict[str, Any]
    bundle_hash: str
    profile: dict[str, Any]
    packet: dict[str, Any]
    profile_id: str
    profile_version: str
    candidate_profile_hash: str
    packet_id: str
    packet_hash: str
    source_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    conflict_ids: tuple[str, ...]


class SbcTimingProfileExternalReviewVerifier:
    @staticmethod
    def _bundle_envelope(bundle: dict[str, Any]) -> str:
        if bundle.get("contract") != INDEPENDENT_REVIEW_BUNDLE_CONTRACT:
            raise ValueError("review bundle contract is unsupported")
        if (
            bundle.get("schemaVersion")
            != INDEPENDENT_REVIEW_BUNDLE_SCHEMA_VERSION
        ):
            raise ValueError("review bundle schemaVersion is unsupported")
        observed = independent_review_bundle_hash(bundle)
        template = bundle.get("attestationTemplate")
        if not isinstance(template, dict):
            raise ValueError("review bundle attestationTemplate is required")
        expected = _sha256(
            template.get("bundleSha256"),
            "attestationTemplate.bundleSha256",
        )
        if observed != expected:
            raise ValueError("review bundle digest does not reproduce")
        return observed

    @staticmethod
    def _s1_context(
        bundle: dict[str, Any],
        bundle_hash: str,
    ) -> _BundleContext:
        profile = bundle.get("profile")
        packet = bundle.get("sourcePacket")
        if not isinstance(profile, dict) or not isinstance(packet, dict):
            raise ValueError("review bundle must contain profile and sourcePacket")
        s1_report = SbcTimingProfileSourcePacketGate().evaluate(profile, packet)
        if not s1_report.ready_for_external_review:
            raise ValueError("embedded candidate and packet do not pass S1")
        sources = _packet_sources(packet)
        claims = _packet_claims(packet)
        conflicts = _packet_conflicts(packet)
        return _BundleContext(
            bundle=bundle,
            bundle_hash=bundle_hash,
            profile=profile,
            packet=packet,
            profile_id=_required_text(s1_report.profile_id, "profileId"),
            profile_version=_required_text(
                s1_report.profile_version,
                "profileVersion",
            ),
            candidate_profile_hash=_sha256(
                s1_report.candidate_profile_hash,
                "candidateProfileHash",
            ),
            packet_id=_required_text(s1_report.packet_id, "packetId"),
            packet_hash=_sha256(s1_report.packet_hash, "packetHash"),
            source_ids=tuple(sorted(sources)),
            claim_ids=tuple(sorted(claims)),
            conflict_ids=tuple(sorted(conflicts)),
        )

    @staticmethod
    def _validate_s2_rows(context: _BundleContext) -> None:
        verification = context.bundle.get("verification")
        if not isinstance(verification, dict):
            raise ValueError("review bundle verification is required")
        expected_methods = {
            "policy": SOURCE_VERIFICATION_POLICY,
            "sourceHashMethod": SOURCE_HASH_METHOD,
            "excerptHashMethod": EXCERPT_HASH_METHOD,
            "reviewBundleHashMethod": REVIEW_BUNDLE_HASH_METHOD,
        }
        for field_name, expected in expected_methods.items():
            if verification.get(field_name) != expected:
                raise ValueError(f"review bundle {field_name} drifted")

        sources = _packet_sources(context.packet)
        source_rows = _unique_map(
            verification.get("sourceArtifacts"),
            "source_id",
            "verification.sourceArtifacts",
        )
        if set(source_rows) != set(sources):
            raise ValueError("source verification IDs do not match the packet")
        for source_id, source in sources.items():
            row = source_rows[source_id]
            expected = _sha256(
                source.get("sha256"),
                f"sourceArtifacts.{source_id}.sha256",
            )
            if (
                _sha256(
                    row.get("expected_sha256"),
                    f"source row {source_id} expected_sha256",
                )
                != expected
                or _sha256(
                    row.get("observed_sha256"),
                    f"source row {source_id} observed_sha256",
                )
                != expected
                or row.get("verification_state") != PASS_STATE
                or row.get("hash_method") != SOURCE_HASH_METHOD
                or row.get("source_role") != source.get("sourceRole")
                or row.get("lineage_id") != source.get("lineageId")
            ):
                raise ValueError(
                    f"source verification row {source_id} is inconsistent"
                )
            _positive_int(
                row.get("observed_byte_length"),
                f"source row {source_id} observed_byte_length",
            )

        claims = _packet_claims(context.packet)
        excerpt_rows = _unique_map(
            verification.get("excerptPayloads"),
            "claim_id",
            "verification.excerptPayloads",
        )
        if set(excerpt_rows) != set(claims):
            raise ValueError("excerpt verification IDs do not match the packet")
        for claim_id, claim in claims.items():
            row = excerpt_rows[claim_id]
            expected = _sha256(
                claim.get("excerptSha256"),
                f"claims.{claim_id}.excerptSha256",
            )
            if (
                _sha256(
                    row.get("expected_sha256"),
                    f"excerpt row {claim_id} expected_sha256",
                )
                != expected
                or _sha256(
                    row.get("observed_sha256"),
                    f"excerpt row {claim_id} observed_sha256",
                )
                != expected
                or row.get("verification_state") != PASS_STATE
                or row.get("hash_method") != EXCERPT_HASH_METHOD
                or row.get("source_id") != claim.get("sourceId")
                or row.get("profile_path") != claim.get("profilePath")
                or row.get("page_start") != claim.get("pageStart")
                or row.get("page_end") != claim.get("pageEnd")
            ):
                raise ValueError(
                    f"excerpt verification row {claim_id} is inconsistent"
                )
            _positive_int(
                row.get("observed_utf8_byte_length"),
                f"excerpt row {claim_id} observed_utf8_byte_length",
            )

        expected_guardrails = {
            "sourceBytesIncluded": False,
            "excerptTextIncluded": False,
            "pagePresenceChecked": False,
            "doctrineCorrectnessChecked": False,
            "externalReviewCompleted": False,
            "sourceCertified": False,
            "profileRegistrationAllowed": False,
            "registryWriteAllowed": False,
            "directionalContribution": 0.0,
            "executionAllowed": False,
        }
        if (context.bundle.get("guardrails") or {}) != expected_guardrails:
            raise ValueError("review bundle guardrails drifted")

    @staticmethod
    def _validate_template(context: _BundleContext) -> None:
        template = _strict_object(
            context.bundle.get("attestationTemplate"),
            _ATTESTATION_KEYS,
            "attestationTemplate",
        )
        if (
            template.get("contract") != EXTERNAL_REVIEW_ATTESTATION_CONTRACT
            or template.get("schemaVersion") != 1
            or template.get("reviewDecision") != "PENDING"
            or template.get("reviewerIdentity") != ""
            or template.get("reviewerOrganization") != ""
            or template.get("reviewerIndependenceConfirmed") is not False
            or template.get("reviewedAtUtc") != ""
            or template.get("overallNote") != ""
            or template.get("registryWriteAllowed") is not False
            or _sha256(
                template.get("bundleSha256"),
                "attestationTemplate.bundleSha256",
            )
            != context.bundle_hash
        ):
            raise ValueError("review bundle attestation template drifted")
        SbcTimingProfileExternalReviewVerifier._pending_template_rows(
            template.get("sourceArtifactDecisions"),
            "sourceId",
            _SOURCE_DECISION_KEYS,
            set(context.source_ids),
            "attestationTemplate.sourceArtifactDecisions",
        )
        SbcTimingProfileExternalReviewVerifier._pending_template_rows(
            template.get("claimDecisions"),
            "claimId",
            _CLAIM_DECISION_KEYS,
            set(context.claim_ids),
            "attestationTemplate.claimDecisions",
        )
        SbcTimingProfileExternalReviewVerifier._pending_template_rows(
            template.get("conflictDecisions"),
            "conflictId",
            _CONFLICT_DECISION_KEYS,
            set(context.conflict_ids),
            "attestationTemplate.conflictDecisions",
        )

    @staticmethod
    def _pending_template_rows(
        rows: Any,
        id_key: str,
        keys: set[str],
        expected_ids: set[str],
        label: str,
    ) -> None:
        mapped = _unique_map(rows, id_key, label)
        if set(mapped) != expected_ids:
            raise ValueError(f"{label} IDs do not match the review bundle")
        for item_id, row in mapped.items():
            _strict_object(row, keys, f"{label}.{item_id}")
            if row.get("decision") != "PENDING" or row.get("note") != "":
                raise ValueError(f"{label}.{item_id} must remain blank and pending")

    @staticmethod
    def _final_decision_rows(
        rows: Any,
        id_key: str,
        keys: set[str],
        expected_ids: set[str],
        label: str,
    ) -> tuple[dict[str, Any], ...]:
        mapped = _unique_map(rows, id_key, label)
        if set(mapped) != expected_ids:
            missing = sorted(expected_ids - set(mapped))
            unexpected = sorted(set(mapped) - expected_ids)
            raise ValueError(
                f"{label} decision IDs differ; missing={missing}, "
                f"unexpected={unexpected}"
            )
        normalized: list[dict[str, Any]] = []
        for item_id in sorted(mapped):
            row = _strict_object(mapped[item_id], keys, f"{label}.{item_id}")
            decision = _required_text(
                row.get("decision"),
                f"{label}.{item_id}.decision",
            ).upper()
            if decision not in FINAL_DECISIONS:
                raise ValueError(
                    f"{label}.{item_id}.decision must be PASS or FAIL"
                )
            normalized.append(
                {
                    id_key: item_id,
                    "decision": decision,
                    "note": _required_text(
                        row.get("note"),
                        f"{label}.{item_id}.note",
                    ),
                }
            )
        return tuple(normalized)

    @classmethod
    def _validate_attestation(
        cls,
        context: _BundleContext,
        attestation: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        _strict_object(attestation, _ATTESTATION_KEYS, "attestation")
        if attestation.get("contract") != EXTERNAL_REVIEW_ATTESTATION_CONTRACT:
            raise ValueError("attestation contract is unsupported")
        if attestation.get("schemaVersion") != 1:
            raise ValueError("attestation schemaVersion is unsupported")
        if (
            _sha256(attestation.get("bundleSha256"), "attestation.bundleSha256")
            != context.bundle_hash
        ):
            raise ValueError("attestation references another review bundle")
        review_decision = _required_text(
            attestation.get("reviewDecision"),
            "attestation.reviewDecision",
        ).upper()
        if review_decision not in {APPROVED, REJECTED}:
            raise ValueError(
                "attestation.reviewDecision must be APPROVED or REJECTED"
            )
        reviewer_identity = _required_text(
            attestation.get("reviewerIdentity"),
            "attestation.reviewerIdentity",
        )
        reviewer_organization = _required_text(
            attestation.get("reviewerOrganization"),
            "attestation.reviewerOrganization",
        )
        if attestation.get("reviewerIndependenceConfirmed") is not True:
            raise ValueError(
                "attestation reviewer independence must be explicitly confirmed"
            )
        reviewed_at_utc = _utc_timestamp(
            attestation.get("reviewedAtUtc"),
            "attestation.reviewedAtUtc",
        )
        if attestation.get("registryWriteAllowed") is not False:
            raise ValueError("attestation cannot allow registry writes")
        overall_note = _required_text(
            attestation.get("overallNote"),
            "attestation.overallNote",
        )
        sources = cls._final_decision_rows(
            attestation.get("sourceArtifactDecisions"),
            "sourceId",
            _SOURCE_DECISION_KEYS,
            set(context.source_ids),
            "attestation.sourceArtifactDecisions",
        )
        claims = cls._final_decision_rows(
            attestation.get("claimDecisions"),
            "claimId",
            _CLAIM_DECISION_KEYS,
            set(context.claim_ids),
            "attestation.claimDecisions",
        )
        conflicts = cls._final_decision_rows(
            attestation.get("conflictDecisions"),
            "conflictId",
            _CONFLICT_DECISION_KEYS,
            set(context.conflict_ids),
            "attestation.conflictDecisions",
        )
        all_rows = (*sources, *claims, *conflicts)
        failed_ids = tuple(
            str(
                row.get("sourceId")
                or row.get("claimId")
                or row.get("conflictId")
            )
            for row in all_rows
            if row["decision"] == "FAIL"
        )
        if review_decision == APPROVED and failed_ids:
            raise ValueError(
                "APPROVED attestation contains failed review decisions"
            )
        if review_decision == REJECTED and not failed_ids:
            raise ValueError(
                "REJECTED attestation must identify at least one failed decision"
            )
        normalized = {
            "contract": EXTERNAL_REVIEW_ATTESTATION_CONTRACT,
            "schemaVersion": 1,
            "bundleSha256": context.bundle_hash,
            "reviewDecision": review_decision,
            "reviewerIdentity": reviewer_identity,
            "reviewerOrganization": reviewer_organization,
            "reviewerIndependenceConfirmed": True,
            "reviewedAtUtc": reviewed_at_utc,
            "sourceArtifactDecisions": list(sources),
            "claimDecisions": list(claims),
            "conflictDecisions": list(conflicts),
            "overallNote": overall_note,
            "registryWriteAllowed": False,
        }
        return review_decision, {
            "normalized": normalized,
            "failedIds": list(failed_ids),
            "sourceDecisionCount": len(sources),
            "claimDecisionCount": len(claims),
            "conflictDecisionCount": len(conflicts),
        }

    @staticmethod
    def _proposal(
        context: _BundleContext,
        attestation_sha256: str,
        attestation_evidence: dict[str, Any],
    ) -> tuple[dict[str, Any], str]:
        normalized = attestation_evidence["normalized"]
        proposal = {
            "contract": CERTIFICATION_PROPOSAL_CONTRACT,
            "schemaVersion": CERTIFICATION_PROPOSAL_SCHEMA_VERSION,
            "classification": RESEARCH_CLASSIFICATION,
            "proposalStatus": "PENDING_HUMAN_CERTIFICATION_DECISION",
            "proposalSha256": "",
            "proposalHashMethod": CERTIFICATION_PROPOSAL_HASH_METHOD,
            "profile": {
                "profileId": context.profile_id,
                "profileVersion": context.profile_version,
                "profileHash": context.candidate_profile_hash,
            },
            "sourcePacket": {
                "packetId": context.packet_id,
                "packetHash": context.packet_hash,
            },
            "reviewEvidence": {
                "bundleSha256": context.bundle_hash,
                "attestationSha256": attestation_sha256,
                "reviewDecision": normalized["reviewDecision"],
                "reviewerIdentityClaim": normalized["reviewerIdentity"],
                "reviewerOrganizationClaim": normalized[
                    "reviewerOrganization"
                ],
                "reviewerIndependenceClaimed": True,
                "reviewedAtUtc": normalized["reviewedAtUtc"],
                "overallNote": normalized["overallNote"],
                "sourceArtifactDecisions": normalized[
                    "sourceArtifactDecisions"
                ],
                "claimDecisions": normalized["claimDecisions"],
                "conflictDecisions": normalized["conflictDecisions"],
            },
            "manualDecisionGate": {
                "decision": "PENDING",
                "reviewerIdentityAuthenticated": False,
                "reviewerIndependenceAuthenticated": False,
                "externalReviewIndependentlyProven": False,
                "sourceCertified": False,
                "profileRegistered": False,
                "registryWriteAllowed": False,
                "requiredActions": [
                    "Authenticate reviewer identity and authority outside the application.",
                    "Confirm reviewer independence outside the application.",
                    "Inspect the archived review bundle and completed attestation.",
                    "Record any certification only in a separately reviewed Git change.",
                    "Keep prospective financial validation and engine admission separate.",
                ],
            },
            "guardrails": {
                "sourceBytesIncluded": False,
                "excerptTextIncluded": False,
                "sourceCertified": False,
                "profileRegistered": False,
                "registryWriteAllowed": False,
                "directionalContribution": 0.0,
                "executionAllowed": False,
            },
        }
        proposal_hash = source_certification_proposal_hash(proposal)
        proposal["proposalSha256"] = proposal_hash
        return proposal, proposal_hash

    @staticmethod
    def _gate(
        gate_id: str,
        label: str,
        state: str,
        detail: str,
        affected_ids: tuple[str, ...] = (),
    ) -> TimingExternalReviewGate:
        return TimingExternalReviewGate(
            gate_id=gate_id,
            state=state,
            mandatory=True,
            label=label,
            detail=detail,
            affected_ids=affected_ids,
        )

    def compile(
        self,
        bundle_payload: Any | None,
        attestation_payload: Any | None,
    ) -> TimingProfileExternalReviewReport:
        gates: list[TimingExternalReviewGate] = []
        context: _BundleContext | None = None
        bundle_hash: str | None = None
        attestation_hash: str | None = None
        attestation_evidence: dict[str, Any] | None = None
        review_decision: str | None = None

        if bundle_payload is None:
            gates.append(
                self._gate(
                    "review_bundle_integrity",
                    "S2 review bundle integrity",
                    UNKNOWN_STATE,
                    "An S2 independent-review bundle is required.",
                )
            )
        elif not isinstance(bundle_payload, dict):
            gates.append(
                self._gate(
                    "review_bundle_integrity",
                    "S2 review bundle integrity",
                    FAIL_STATE,
                    "The review bundle must be a JSON object.",
                )
            )
        else:
            try:
                bundle_hash = self._bundle_envelope(bundle_payload)
                gates.append(
                    self._gate(
                        "review_bundle_integrity",
                        "S2 review bundle integrity",
                        PASS_STATE,
                        "The review bundle contract and canonical digest reproduce.",
                    )
                )
            except (TypeError, ValueError) as exc:
                gates.append(
                    self._gate(
                        "review_bundle_integrity",
                        "S2 review bundle integrity",
                        FAIL_STATE,
                        str(exc),
                    )
                )

        if bundle_hash is None or not isinstance(bundle_payload, dict):
            gates.extend(
                [
                    self._gate(
                        "embedded_s1_readiness",
                        "Embedded S1 readiness",
                        UNKNOWN_STATE,
                        "A valid S2 bundle is required.",
                    ),
                    self._gate(
                        "s2_verification_rows",
                        "S2 verification rows",
                        UNKNOWN_STATE,
                        "A valid S2 bundle is required.",
                    ),
                ]
            )
        else:
            try:
                context = self._s1_context(bundle_payload, bundle_hash)
                gates.append(
                    self._gate(
                        "embedded_s1_readiness",
                        "Embedded S1 readiness",
                        PASS_STATE,
                        "The embedded candidate and source packet still pass S1.",
                    )
                )
            except (TypeError, ValueError) as exc:
                gates.append(
                    self._gate(
                        "embedded_s1_readiness",
                        "Embedded S1 readiness",
                        FAIL_STATE,
                        str(exc),
                    )
                )

            if context is None:
                gates.append(
                    self._gate(
                        "s2_verification_rows",
                        "S2 verification rows",
                        UNKNOWN_STATE,
                        "Embedded S1 readiness is required.",
                    )
                )
            else:
                try:
                    self._validate_s2_rows(context)
                    self._validate_template(context)
                    gates.append(
                        self._gate(
                            "s2_verification_rows",
                            "S2 verification rows",
                            PASS_STATE,
                            (
                                f"{len(context.source_ids)} source, "
                                f"{len(context.claim_ids)} claim, and "
                                f"{len(context.conflict_ids)} conflict IDs "
                                "are internally coherent."
                            ),
                        )
                    )
                except (TypeError, ValueError) as exc:
                    gates.append(
                        self._gate(
                            "s2_verification_rows",
                            "S2 verification rows",
                            FAIL_STATE,
                            str(exc),
                        )
                    )

        rows_ready = any(
            gate.gate_id == "s2_verification_rows"
            and gate.state == PASS_STATE
            for gate in gates
        )
        if attestation_payload is None:
            gates.append(
                self._gate(
                    "completed_attestation",
                    "Completed external-review attestation",
                    UNKNOWN_STATE,
                    "A separately completed attestation is required.",
                )
            )
        elif not isinstance(attestation_payload, dict):
            gates.append(
                self._gate(
                    "completed_attestation",
                    "Completed external-review attestation",
                    FAIL_STATE,
                    "The attestation must be a JSON object.",
                )
            )
        elif context is None or not rows_ready:
            gates.append(
                self._gate(
                    "completed_attestation",
                    "Completed external-review attestation",
                    UNKNOWN_STATE,
                    "A coherent S2 review bundle is required first.",
                )
            )
        else:
            try:
                review_decision, attestation_evidence = (
                    self._validate_attestation(
                        context,
                        attestation_payload,
                    )
                )
                attestation_hash = _canonical_hash(
                    attestation_evidence["normalized"]
                )
                gates.append(
                    self._gate(
                        "completed_attestation",
                        "Completed external-review attestation",
                        PASS_STATE,
                        (
                            "The attestation has exact decision coverage and "
                            f"a consistent {review_decision} outcome."
                        ),
                        tuple(attestation_evidence["failedIds"]),
                    )
                )
            except (TypeError, ValueError) as exc:
                gates.append(
                    self._gate(
                        "completed_attestation",
                        "Completed external-review attestation",
                        FAIL_STATE,
                        str(exc),
                    )
                )

        gates.append(
            self._gate(
                "human_certification_boundary",
                "Human certification boundary",
                PASS_STATE,
                (
                    "S3 checks record coherence only. Reviewer authentication, "
                    "certification, registry writes, inference, and execution "
                    "remain outside the application."
                ),
            )
        )

        all_gates_pass = all(gate.state == PASS_STATE for gate in gates)
        approved = review_decision == APPROVED
        ready = all_gates_pass and approved and context is not None
        proposal: dict[str, Any] | None = None
        proposal_hash: str | None = None
        if (
            ready
            and context is not None
            and attestation_hash is not None
            and attestation_evidence is not None
        ):
            proposal, proposal_hash = self._proposal(
                context,
                attestation_hash,
                attestation_evidence,
            )

        if attestation_payload is None:
            status = NO_ATTESTATION
        elif all_gates_pass and review_decision == REJECTED:
            status = REVIEW_REJECTED
        elif ready:
            status = READY_FOR_HUMAN_CERTIFICATION_DECISION
        else:
            status = ATTESTATION_INVALID

        return TimingProfileExternalReviewReport(
            review_status=status,
            profile_id=context.profile_id if context else None,
            profile_version=context.profile_version if context else None,
            candidate_profile_hash=(
                context.candidate_profile_hash if context else None
            ),
            packet_id=context.packet_id if context else None,
            packet_hash=context.packet_hash if context else None,
            review_bundle_sha256=bundle_hash,
            attestation_sha256=attestation_hash,
            bundle_integrity_verified=bundle_hash is not None,
            embedded_s1_ready=any(
                gate.gate_id == "embedded_s1_readiness"
                and gate.state == PASS_STATE
                for gate in gates
            ),
            s2_rows_verified=rows_ready,
            attestation_complete=attestation_evidence is not None,
            review_approved=approved,
            ready_for_human_certification_decision=ready,
            validation_gates=tuple(gates),
            missing_requirements=tuple(
                gate.label for gate in gates if gate.state != PASS_STATE
            ),
            certification_proposal=proposal,
            certification_proposal_sha256=proposal_hash,
        )
