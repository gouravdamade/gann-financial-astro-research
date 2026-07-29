from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from .atomic_intervals import RESEARCH_CLASSIFICATION
from .models import to_primitive
from .timing_profile_admission import SbcTimingProfileAdmissionGate


SOURCE_PACKET_CONTRACT = "SBC_TIMING_PROFILE_SOURCE_PACKET_V1"
SOURCE_PACKET_SCHEMA_VERSION = 1
SOURCE_PACKET_REPORT_CONTRACT = "SBC_TIMING_PROFILE_SOURCE_READINESS_REPORT_V1"
SOURCE_PACKET_REPORT_SCHEMA_VERSION = 1
SOURCE_PACKET_POLICY = "CLAIM_HASH_AND_INDEPENDENT_LINEAGE_READINESS_V1"

PASS_STATE = "PASS"
FAIL_STATE = "FAIL"
UNKNOWN_STATE = "UNKNOWN"

NO_PACKET_LOADED = "NO_PACKET_LOADED"
NOT_READY_FOR_EXTERNAL_REVIEW = "NOT_READY_FOR_EXTERNAL_REVIEW"
READY_FOR_EXTERNAL_REVIEW = "READY_FOR_EXTERNAL_REVIEW"

PRIMARY_SOURCE = "PRIMARY_SOURCE"
INDEPENDENT_WITNESS = "INDEPENDENT_WITNESS"
RESEARCH_SPECIFICATION = "RESEARCH_SPECIFICATION"

DOCTRINE_PATHS = (
    "/phaseSpan",
    "/sectors",
    "/boundaryPolicy",
    "/asymmetryPolicy",
    "/repeatedExactEventPolicy",
    "/retrogradeLoopPolicy",
    "/stationPolicy",
    "/missingBoundaryPolicy",
    "/unsupportedStatePolicy",
)
RESEARCH_PROTOCOL_PATHS = (
    "/eligibilityPolicy",
    "/confidencePolicy",
)
REQUIRED_PROFILE_PATHS = DOCTRINE_PATHS + RESEARCH_PROTOCOL_PATHS

_PACKET_KEYS = {
    "contract",
    "schemaVersion",
    "packetId",
    "packetVersion",
    "classification",
    "frozen",
    "profileId",
    "profileVersion",
    "profileHash",
    "preparedAtUtc",
    "preparedBy",
    "sourceArtifacts",
    "claims",
    "conflictRegister",
    "reviewRequest",
    "guardrails",
}
_SOURCE_KEYS = {
    "sourceId",
    "title",
    "edition",
    "language",
    "publicationYear",
    "sha256",
    "lineageId",
    "sourceRole",
}
_CLAIM_KEYS = {
    "claimId",
    "profilePath",
    "candidateValueSha256",
    "sourceId",
    "citation",
    "pageStart",
    "pageEnd",
    "evidenceRole",
    "excerptSha256",
    "note",
}
_CONFLICT_KEYS = {
    "conflictId",
    "profilePath",
    "sourceIds",
    "status",
    "resolution",
    "chosenSourceId",
}
_REVIEW_REQUEST_KEYS = {
    "requestedDecision",
    "requiredReviewerIndependence",
    "requiredReviewScope",
    "certificationRegistryWriteAllowed",
}
_GUARDRAIL_KEYS = {
    "researchOnly",
    "readOnly",
    "packetPersisted",
    "profileValuesSuppliedByApplication",
    "sourceBytesVerifiedByApplication",
    "externalReviewCompleted",
    "sourceCertified",
    "profileRegistrationAllowed",
    "noAutoSuggest",
    "noLiveInference",
    "noOfficialMlNotes",
    "noShadowVote",
    "noTradeOutput",
    "executionAllowed",
}


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _required_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _required_list(
    value: Any,
    label: str,
    *,
    allow_empty: bool = False,
) -> list[Any]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "an array" if allow_empty else "a non-empty array"
        raise ValueError(f"{label} must be {qualifier}")
    return value


def _exact_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    missing = sorted(allowed - set(value))
    unknown = sorted(set(value) - allowed)
    problems: list[str] = []
    if missing:
        problems.append(f"missing {', '.join(missing)}")
    if unknown:
        problems.append(f"unknown {', '.join(unknown)}")
    if problems:
        raise ValueError(f"{label}: {'; '.join(problems)}")


def _required_text(value: Any, label: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{label} is required")
    return normalized


def _required_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be boolean")
    return value


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _sha256(value: Any, label: str) -> str:
    normalized = _required_text(value, label).upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"{label} must be an uppercase SHA-256 digest")
    return normalized


def _utc_timestamp(value: Any, label: str) -> str:
    normalized = _required_text(value, label)
    if not normalized.endswith("Z"):
        raise ValueError(f"{label} must end with Z")
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO UTC timestamp") from exc
    if parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
    return normalized


def _profile_value(profile: dict[str, Any], profile_path: str) -> Any:
    if profile_path not in REQUIRED_PROFILE_PATHS:
        raise ValueError(f"unsupported profilePath: {profile_path}")
    field_name = profile_path.removeprefix("/")
    if field_name not in profile:
        raise ValueError(f"profile is missing {profile_path}")
    return profile[field_name]


@dataclass(frozen=True)
class TimingSourceReadinessGate:
    gate_id: str
    state: str
    mandatory: bool
    label: str
    detail: str
    missing_paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in {PASS_STATE, FAIL_STATE, UNKNOWN_STATE}:
            raise ValueError(f"unknown gate state: {self.state}")
        object.__setattr__(self, "gate_id", _required_text(self.gate_id, "gate_id"))
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "detail", _required_text(self.detail, "detail"))
        object.__setattr__(
            self,
            "missing_paths",
            tuple(_required_text(item, "missing_path") for item in self.missing_paths),
        )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingSourceClaimCoverage:
    profile_path: str
    claim_class: str
    candidate_value_sha256: str | None
    primary_source_count: int
    independent_witness_count: int
    research_specification_count: int
    independent_lineage_count: int
    coverage_state: str
    detail: str

    def __post_init__(self) -> None:
        if self.coverage_state not in {PASS_STATE, FAIL_STATE, UNKNOWN_STATE}:
            raise ValueError(f"unknown coverage state: {self.coverage_state}")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingProfileSourceReadinessReport:
    packet_status: str
    profile_id: str | None
    profile_version: str | None
    candidate_profile_hash: str | None
    packet_id: str | None
    packet_hash: str | None
    candidate_structural_complete: bool
    packet_structural_complete: bool
    claim_coverage_complete: bool
    independent_witness_coverage_complete: bool
    conflicts_resolved: bool
    ready_for_external_review: bool
    external_review_completed: bool
    source_certified: bool
    profile_registration_allowed: bool
    validation_gates: tuple[TimingSourceReadinessGate, ...]
    claim_coverage: tuple[TimingSourceClaimCoverage, ...]
    missing_requirements: tuple[str, ...]
    contract: str = SOURCE_PACKET_REPORT_CONTRACT
    schema_version: int = SOURCE_PACKET_REPORT_SCHEMA_VERSION
    readiness_policy: str = SOURCE_PACKET_POLICY
    classification: str = RESEARCH_CLASSIFICATION
    guardrails: dict[str, Any] = field(
        default_factory=lambda: {
            "research_only": True,
            "read_only": True,
            "candidate_persisted": False,
            "packet_persisted": False,
            "source_bytes_verified_by_application": False,
            "external_review_completed": False,
            "source_certified": False,
            "profile_registration_allowed": False,
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
        if self.external_review_completed:
            raise ValueError("S1 cannot claim an external review")
        if self.source_certified:
            raise ValueError("S1 cannot certify a source packet")
        if self.profile_registration_allowed:
            raise ValueError("S1 cannot register a timing profile")
        if self.guardrails.get("execution_allowed") is not False:
            raise ValueError("S1 execution must remain locked")
        if float(self.guardrails.get("directional_contribution", 1.0)) != 0.0:
            raise ValueError("S1 cannot contribute market direction")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


class SbcTimingProfileSourcePacketGate:
    def __init__(self) -> None:
        self._profile_gate = SbcTimingProfileAdmissionGate(
            {
                "contract": "SBC_TIMING_PROFILE_REGISTRY_V1",
                "schemaVersion": 1,
                "profiles": [],
                "executionAllowed": False,
            }
        )

    @staticmethod
    def _gate(
        gate_id: str,
        label: str,
        validator: Callable[[], str],
        *,
        present: bool,
        missing_paths: tuple[str, ...] = (),
    ) -> TimingSourceReadinessGate:
        if not present:
            return TimingSourceReadinessGate(
                gate_id=gate_id,
                state=UNKNOWN_STATE,
                mandatory=True,
                label=label,
                detail="Required in-memory evidence is not loaded.",
                missing_paths=missing_paths,
            )
        try:
            detail = validator()
        except (TypeError, ValueError) as exc:
            return TimingSourceReadinessGate(
                gate_id=gate_id,
                state=FAIL_STATE,
                mandatory=True,
                label=label,
                detail=str(exc),
                missing_paths=missing_paths,
            )
        return TimingSourceReadinessGate(
            gate_id=gate_id,
            state=PASS_STATE,
            mandatory=True,
            label=label,
            detail=detail,
        )

    @staticmethod
    def _validate_packet_core(packet: dict[str, Any]) -> str:
        _exact_keys(packet, _PACKET_KEYS, "packet")
        if packet.get("contract") != SOURCE_PACKET_CONTRACT:
            raise ValueError(f"packet.contract must be {SOURCE_PACKET_CONTRACT}")
        if packet.get("schemaVersion") != SOURCE_PACKET_SCHEMA_VERSION:
            raise ValueError(
                f"packet.schemaVersion must be {SOURCE_PACKET_SCHEMA_VERSION}"
            )
        _required_text(packet.get("packetId"), "packet.packetId")
        _required_text(packet.get("packetVersion"), "packet.packetVersion")
        if packet.get("classification") != RESEARCH_CLASSIFICATION:
            raise ValueError(
                f"packet.classification must be {RESEARCH_CLASSIFICATION}"
            )
        if not _required_bool(packet.get("frozen"), "packet.frozen"):
            raise ValueError("packet.frozen must be true")
        _utc_timestamp(packet.get("preparedAtUtc"), "packet.preparedAtUtc")
        _required_text(packet.get("preparedBy"), "packet.preparedBy")
        return "Packet contract, identity, timestamp, and frozen state are explicit."

    @staticmethod
    def _validate_profile_link(
        profile: dict[str, Any],
        packet: dict[str, Any],
        candidate_hash: str | None,
    ) -> str:
        if candidate_hash is None:
            raise ValueError("candidate profile cannot be canonically hashed")
        if _required_text(packet.get("profileId"), "packet.profileId") != _required_text(
            profile.get("profileId"),
            "profile.profileId",
        ):
            raise ValueError("packet.profileId does not match the candidate")
        if _required_text(
            packet.get("profileVersion"),
            "packet.profileVersion",
        ) != _required_text(profile.get("profileVersion"), "profile.profileVersion"):
            raise ValueError("packet.profileVersion does not match the candidate")
        if _sha256(packet.get("profileHash"), "packet.profileHash") != candidate_hash:
            raise ValueError("packet.profileHash does not match the candidate JSON")
        return "Packet identity and SHA-256 bind to the exact in-memory candidate."

    @staticmethod
    def _source_map(
        profile: dict[str, Any],
        packet: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        candidate_sources_raw = _required_list(
            profile.get("sourceEvidence"),
            "profile.sourceEvidence",
        )
        candidate_sources: dict[str, dict[str, Any]] = {}
        for index, item in enumerate(candidate_sources_raw):
            source = _required_dict(item, f"profile.sourceEvidence[{index}]")
            source_id = _required_text(
                source.get("sourceId"),
                f"profile.sourceEvidence[{index}].sourceId",
            )
            candidate_sources[source_id] = source

        source_artifacts = _required_list(
            packet.get("sourceArtifacts"),
            "packet.sourceArtifacts",
        )
        sources: dict[str, dict[str, Any]] = {}
        for index, item in enumerate(source_artifacts):
            label = f"packet.sourceArtifacts[{index}]"
            source = _required_dict(item, label)
            _exact_keys(source, _SOURCE_KEYS, label)
            source_id = _required_text(source.get("sourceId"), f"{label}.sourceId")
            if source_id in sources:
                raise ValueError(f"duplicate packet sourceId: {source_id}")
            _required_text(source.get("title"), f"{label}.title")
            _required_text(source.get("edition"), f"{label}.edition")
            _required_text(source.get("language"), f"{label}.language")
            _positive_int(source.get("publicationYear"), f"{label}.publicationYear")
            source_hash = _sha256(source.get("sha256"), f"{label}.sha256")
            _required_text(source.get("lineageId"), f"{label}.lineageId")
            role = _required_text(source.get("sourceRole"), f"{label}.sourceRole")
            if role not in {
                PRIMARY_SOURCE,
                INDEPENDENT_WITNESS,
                RESEARCH_SPECIFICATION,
            }:
                raise ValueError(f"{label}.sourceRole is unsupported")
            candidate_source = candidate_sources.get(source_id)
            if candidate_source is None:
                raise ValueError(
                    f"packet source {source_id} is absent from profile.sourceEvidence"
                )
            candidate_hash = _sha256(
                candidate_source.get("sha256"),
                f"profile.sourceEvidence[{source_id}].sha256",
            )
            if source_hash != candidate_hash:
                raise ValueError(
                    f"packet source {source_id} hash differs from the candidate"
                )
            sources[source_id] = source
        missing_sources = sorted(set(candidate_sources) - set(sources))
        if missing_sources:
            raise ValueError(
                "packet omits candidate source declarations: "
                + ", ".join(missing_sources)
            )
        return sources

    @classmethod
    def _validate_sources(
        cls,
        profile: dict[str, Any],
        packet: dict[str, Any],
    ) -> str:
        sources = cls._source_map(profile, packet)
        lineages = {
            _required_text(source.get("lineageId"), "source.lineageId")
            for source in sources.values()
        }
        return (
            f"{len(sources)} hash-linked source declaration(s) across "
            f"{len(lineages)} declared lineage(s). Source bytes are not verified by S1."
        )

    @classmethod
    def _validated_claims(
        cls,
        profile: dict[str, Any],
        packet: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
        sources = cls._source_map(profile, packet)
        claims_raw = _required_list(packet.get("claims"), "packet.claims")
        claims: list[dict[str, Any]] = []
        claim_ids: set[str] = set()
        referenced_sources: set[str] = set()
        for index, item in enumerate(claims_raw):
            label = f"packet.claims[{index}]"
            claim = _required_dict(item, label)
            _exact_keys(claim, _CLAIM_KEYS, label)
            claim_id = _required_text(claim.get("claimId"), f"{label}.claimId")
            if claim_id in claim_ids:
                raise ValueError(f"duplicate claimId: {claim_id}")
            claim_ids.add(claim_id)
            profile_path = _required_text(
                claim.get("profilePath"),
                f"{label}.profilePath",
            )
            candidate_hash = _canonical_hash(_profile_value(profile, profile_path))
            if _sha256(
                claim.get("candidateValueSha256"),
                f"{label}.candidateValueSha256",
            ) != candidate_hash:
                raise ValueError(
                    f"{label}.candidateValueSha256 does not match {profile_path}"
                )
            source_id = _required_text(claim.get("sourceId"), f"{label}.sourceId")
            source = sources.get(source_id)
            if source is None:
                raise ValueError(f"{label}.sourceId is not declared")
            referenced_sources.add(source_id)
            _required_text(claim.get("citation"), f"{label}.citation")
            page_start = _positive_int(claim.get("pageStart"), f"{label}.pageStart")
            page_end = _positive_int(claim.get("pageEnd"), f"{label}.pageEnd")
            if page_end < page_start:
                raise ValueError(f"{label}.pageEnd cannot precede pageStart")
            evidence_role = _required_text(
                claim.get("evidenceRole"),
                f"{label}.evidenceRole",
            )
            if evidence_role != source.get("sourceRole"):
                raise ValueError(
                    f"{label}.evidenceRole must match its source declaration"
                )
            expected_roles = (
                {PRIMARY_SOURCE, INDEPENDENT_WITNESS}
                if profile_path in DOCTRINE_PATHS
                else {RESEARCH_SPECIFICATION}
            )
            if evidence_role not in expected_roles:
                raise ValueError(
                    f"{label}.evidenceRole is invalid for {profile_path}"
                )
            _sha256(claim.get("excerptSha256"), f"{label}.excerptSha256")
            _required_text(claim.get("note"), f"{label}.note")
            claims.append(claim)
        unused_sources = sorted(set(sources) - referenced_sources)
        if unused_sources:
            raise ValueError(
                "source declarations without a claim: " + ", ".join(unused_sources)
            )
        return claims, sources

    @classmethod
    def _validate_claim_integrity(
        cls,
        profile: dict[str, Any],
        packet: dict[str, Any],
    ) -> str:
        claims, _ = cls._validated_claims(profile, packet)
        return (
            f"{len(claims)} page-cited claim(s) bind exact candidate subtrees "
            "to excerpt hashes."
        )

    @classmethod
    def _coverage(
        cls,
        profile: dict[str, Any],
        packet: dict[str, Any],
        *,
        available: bool,
    ) -> tuple[TimingSourceClaimCoverage, ...]:
        if not available:
            return tuple(
                TimingSourceClaimCoverage(
                    profile_path=profile_path,
                    claim_class=(
                        "DOCTRINE"
                        if profile_path in DOCTRINE_PATHS
                        else "RESEARCH_PROTOCOL"
                    ),
                    candidate_value_sha256=None,
                    primary_source_count=0,
                    independent_witness_count=0,
                    research_specification_count=0,
                    independent_lineage_count=0,
                    coverage_state=UNKNOWN_STATE,
                    detail="Candidate and source packet are both required.",
                )
                for profile_path in REQUIRED_PROFILE_PATHS
            )
        try:
            claims, sources = cls._validated_claims(profile, packet)
        except (TypeError, ValueError) as exc:
            return tuple(
                TimingSourceClaimCoverage(
                    profile_path=profile_path,
                    claim_class=(
                        "DOCTRINE"
                        if profile_path in DOCTRINE_PATHS
                        else "RESEARCH_PROTOCOL"
                    ),
                    candidate_value_sha256=(
                        _canonical_hash(_profile_value(profile, profile_path))
                        if profile_path.removeprefix("/") in profile
                        else None
                    ),
                    primary_source_count=0,
                    independent_witness_count=0,
                    research_specification_count=0,
                    independent_lineage_count=0,
                    coverage_state=FAIL_STATE,
                    detail=f"Claim set is invalid: {exc}",
                )
                for profile_path in REQUIRED_PROFILE_PATHS
            )

        rows: list[TimingSourceClaimCoverage] = []
        for profile_path in REQUIRED_PROFILE_PATHS:
            matching = [
                claim for claim in claims if claim.get("profilePath") == profile_path
            ]
            primary = sum(
                claim.get("evidenceRole") == PRIMARY_SOURCE for claim in matching
            )
            witness = sum(
                claim.get("evidenceRole") == INDEPENDENT_WITNESS for claim in matching
            )
            research = sum(
                claim.get("evidenceRole") == RESEARCH_SPECIFICATION
                for claim in matching
            )
            lineages = {
                str(sources[str(claim["sourceId"])]["lineageId"])
                for claim in matching
            }
            if profile_path in DOCTRINE_PATHS:
                passed = primary >= 1 and witness >= 1 and len(lineages) >= 2
                detail = (
                    f"{primary} primary, {witness} independent witness, "
                    f"{len(lineages)} distinct lineage(s)."
                )
                claim_class = "DOCTRINE"
            else:
                passed = research >= 1
                detail = (
                    f"{research} frozen research specification claim(s); "
                    "financial usefulness still requires prospective validation."
                )
                claim_class = "RESEARCH_PROTOCOL"
            rows.append(
                TimingSourceClaimCoverage(
                    profile_path=profile_path,
                    claim_class=claim_class,
                    candidate_value_sha256=_canonical_hash(
                        _profile_value(profile, profile_path)
                    ),
                    primary_source_count=primary,
                    independent_witness_count=witness,
                    research_specification_count=research,
                    independent_lineage_count=len(lineages),
                    coverage_state=PASS_STATE if passed else FAIL_STATE,
                    detail=detail,
                )
            )
        return tuple(rows)

    @classmethod
    def _validate_doctrine_coverage(
        cls,
        coverage: tuple[TimingSourceClaimCoverage, ...],
    ) -> str:
        failed = [
            row.profile_path
            for row in coverage
            if row.claim_class == "DOCTRINE" and row.coverage_state != PASS_STATE
        ]
        if failed:
            raise ValueError(
                "doctrine claims lack primary evidence: " + ", ".join(failed)
            )
        return f"Primary source claims cover all {len(DOCTRINE_PATHS)} doctrine domains."

    @classmethod
    def _validate_witness_coverage(
        cls,
        coverage: tuple[TimingSourceClaimCoverage, ...],
    ) -> str:
        failed = [
            row.profile_path
            for row in coverage
            if row.claim_class == "DOCTRINE"
            and (
                row.independent_witness_count < 1
                or row.independent_lineage_count < 2
            )
        ]
        if failed:
            raise ValueError(
                "doctrine claims lack an independent lineage witness: "
                + ", ".join(failed)
            )
        return "Every doctrine domain has a separately declared witness lineage."

    @classmethod
    def _validate_research_coverage(
        cls,
        coverage: tuple[TimingSourceClaimCoverage, ...],
    ) -> str:
        failed = [
            row.profile_path
            for row in coverage
            if row.claim_class == "RESEARCH_PROTOCOL"
            and row.coverage_state != PASS_STATE
        ]
        if failed:
            raise ValueError(
                "research protocol claims are missing: " + ", ".join(failed)
            )
        return (
            f"All {len(RESEARCH_PROTOCOL_PATHS)} research-policy domains have "
            "frozen specification evidence."
        )

    @classmethod
    def _validate_conflicts(
        cls,
        profile: dict[str, Any],
        packet: dict[str, Any],
    ) -> str:
        sources = cls._source_map(profile, packet)
        conflicts = _required_list(
            packet.get("conflictRegister"),
            "packet.conflictRegister",
            allow_empty=True,
        )
        conflict_ids: set[str] = set()
        unresolved: list[str] = []
        for index, item in enumerate(conflicts):
            label = f"packet.conflictRegister[{index}]"
            conflict = _required_dict(item, label)
            _exact_keys(conflict, _CONFLICT_KEYS, label)
            conflict_id = _required_text(
                conflict.get("conflictId"),
                f"{label}.conflictId",
            )
            if conflict_id in conflict_ids:
                raise ValueError(f"duplicate conflictId: {conflict_id}")
            conflict_ids.add(conflict_id)
            profile_path = _required_text(
                conflict.get("profilePath"),
                f"{label}.profilePath",
            )
            _profile_value(profile, profile_path)
            source_ids = _required_list(
                conflict.get("sourceIds"),
                f"{label}.sourceIds",
            )
            normalized_sources = [
                _required_text(source_id, f"{label}.sourceIds") for source_id in source_ids
            ]
            if len(set(normalized_sources)) != len(normalized_sources):
                raise ValueError(f"{label}.sourceIds contains duplicates")
            unknown_sources = sorted(set(normalized_sources) - set(sources))
            if unknown_sources:
                raise ValueError(
                    f"{label}.sourceIds are undeclared: {', '.join(unknown_sources)}"
                )
            status = _required_text(conflict.get("status"), f"{label}.status")
            if status not in {"UNRESOLVED", "RESOLVED_WITH_JUSTIFICATION"}:
                raise ValueError(f"{label}.status is unsupported")
            resolution = str(conflict.get("resolution") or "").strip()
            chosen_source = str(conflict.get("chosenSourceId") or "").strip()
            if status == "UNRESOLVED":
                unresolved.append(conflict_id)
                if resolution or chosen_source:
                    raise ValueError(
                        f"{label}: unresolved conflicts cannot claim a resolution"
                    )
            else:
                if not resolution:
                    raise ValueError(f"{label}.resolution is required")
                if chosen_source not in normalized_sources:
                    raise ValueError(
                        f"{label}.chosenSourceId must be one of its sourceIds"
                    )
        if unresolved:
            raise ValueError("unresolved source conflicts: " + ", ".join(unresolved))
        return f"Conflict register contains {len(conflicts)} resolved item(s) and no open item."

    @staticmethod
    def _validate_review_request(packet: dict[str, Any]) -> str:
        review = _required_dict(packet.get("reviewRequest"), "packet.reviewRequest")
        _exact_keys(review, _REVIEW_REQUEST_KEYS, "packet.reviewRequest")
        if review.get("requestedDecision") != "SOURCE_CERTIFICATION":
            raise ValueError(
                "reviewRequest.requestedDecision must be SOURCE_CERTIFICATION"
            )
        if (
            review.get("requiredReviewerIndependence")
            != "EXTERNAL_TO_PROFILE_AUTHOR"
        ):
            raise ValueError(
                "reviewRequest.requiredReviewerIndependence must be "
                "EXTERNAL_TO_PROFILE_AUTHOR"
            )
        scopes = _required_list(
            review.get("requiredReviewScope"),
            "reviewRequest.requiredReviewScope",
        )
        normalized = {
            _required_text(item, "reviewRequest.requiredReviewScope") for item in scopes
        }
        required = {
            "SOURCE_IDENTITY",
            "PAGE_CITATIONS",
            "CLAIM_VALUE_BINDING",
            "INDEPENDENT_LINEAGE",
            "CONFLICT_RESOLUTION",
        }
        if normalized != required:
            raise ValueError(
                "reviewRequest.requiredReviewScope must contain the exact S1 scope"
            )
        if _required_bool(
            review.get("certificationRegistryWriteAllowed"),
            "reviewRequest.certificationRegistryWriteAllowed",
        ):
            raise ValueError(
                "reviewRequest.certificationRegistryWriteAllowed must be false"
            )
        return "External reviewer independence and exact review scope are requested."

    @staticmethod
    def _validate_guardrails(packet: dict[str, Any]) -> str:
        guardrails = _required_dict(packet.get("guardrails"), "packet.guardrails")
        _exact_keys(guardrails, _GUARDRAIL_KEYS, "packet.guardrails")
        true_fields = {
            "researchOnly",
            "readOnly",
            "noAutoSuggest",
            "noLiveInference",
            "noOfficialMlNotes",
            "noShadowVote",
            "noTradeOutput",
        }
        for guardrail_name in true_fields:
            if (
                _required_bool(
                    guardrails.get(guardrail_name),
                    f"guardrails.{guardrail_name}",
                )
                is not True
            ):
                raise ValueError(f"guardrails.{guardrail_name} must be true")
        for guardrail_name in _GUARDRAIL_KEYS - true_fields:
            if (
                _required_bool(
                    guardrails.get(guardrail_name),
                    f"guardrails.{guardrail_name}",
                )
                is not False
            ):
                raise ValueError(f"guardrails.{guardrail_name} must be false")
        return "Packet is research-only, non-persistent, non-certifying, and execution-locked."

    def evaluate(
        self,
        profile_payload: Any | None,
        packet_payload: Any | None,
    ) -> TimingProfileSourceReadinessReport:
        profile_present = isinstance(profile_payload, dict)
        packet_present = isinstance(packet_payload, dict)
        profile = profile_payload if profile_present else {}
        packet = packet_payload if packet_present else {}

        profile_report = self._profile_gate.evaluate(
            profile_payload if profile_payload is not None else None
        )
        candidate_hash = profile_report.candidate_profile_hash
        packet_hash: str | None = None
        if packet_present:
            try:
                packet_hash = _canonical_hash(packet)
            except (TypeError, ValueError):
                packet_hash = None

        candidate_gate = TimingSourceReadinessGate(
            gate_id="candidate_profile_structure",
            state=(
                PASS_STATE
                if profile_report.structural_complete
                else UNKNOWN_STATE
                if profile_payload is None
                else FAIL_STATE
            ),
            mandatory=True,
            label="T0 candidate structure",
            detail=(
                "The candidate passes every T0 structural profile gate."
                if profile_report.structural_complete
                else "A structurally complete T0 candidate profile is required."
            ),
            missing_paths=(
                ()
                if profile_report.structural_complete
                else ("candidate_profile",)
            ),
        )
        gates = [candidate_gate]
        gates.append(
            self._gate(
                "source_packet_contract",
                "Frozen source packet contract",
                lambda: self._validate_packet_core(packet),
                present=packet_present,
                missing_paths=("source_packet",),
            )
        )
        both_present = profile_present and packet_present
        gates.append(
            self._gate(
                "exact_profile_hash_link",
                "Exact candidate profile link",
                lambda: self._validate_profile_link(
                    profile,
                    packet,
                    candidate_hash,
                ),
                present=both_present,
                missing_paths=("candidate_profile", "source_packet.profileHash"),
            )
        )
        gates.append(
            self._gate(
                "source_declarations",
                "Hash-linked source declarations",
                lambda: self._validate_sources(profile, packet),
                present=both_present,
                missing_paths=("source_packet.sourceArtifacts",),
            )
        )
        gates.append(
            self._gate(
                "claim_value_integrity",
                "Page-cited claim value integrity",
                lambda: self._validate_claim_integrity(profile, packet),
                present=both_present,
                missing_paths=("source_packet.claims",),
            )
        )

        coverage = self._coverage(
            profile,
            packet,
            available=both_present,
        )
        gates.append(
            self._gate(
                "doctrine_claim_coverage",
                "Primary doctrine claim coverage",
                lambda: self._validate_doctrine_coverage(coverage),
                present=both_present,
                missing_paths=DOCTRINE_PATHS,
            )
        )
        gates.append(
            self._gate(
                "independent_witness_coverage",
                "Independent witness coverage",
                lambda: self._validate_witness_coverage(coverage),
                present=both_present,
                missing_paths=DOCTRINE_PATHS,
            )
        )
        gates.append(
            self._gate(
                "research_protocol_coverage",
                "Research protocol coverage",
                lambda: self._validate_research_coverage(coverage),
                present=both_present,
                missing_paths=RESEARCH_PROTOCOL_PATHS,
            )
        )
        gates.append(
            self._gate(
                "source_conflict_resolution",
                "Source conflict register",
                lambda: self._validate_conflicts(profile, packet),
                present=both_present,
                missing_paths=("source_packet.conflictRegister",),
            )
        )
        gates.append(
            self._gate(
                "external_review_request",
                "External certification review request",
                lambda: self._validate_review_request(packet),
                present=packet_present,
                missing_paths=("source_packet.reviewRequest",),
            )
        )
        gates.append(
            self._gate(
                "packet_guardrails",
                "Research and execution locks",
                lambda: self._validate_guardrails(packet),
                present=packet_present,
                missing_paths=("source_packet.guardrails",),
            )
        )

        packet_structural_complete = all(
            gate.state == PASS_STATE
            for gate in gates
            if gate.gate_id
            in {
                "source_packet_contract",
                "exact_profile_hash_link",
                "source_declarations",
                "claim_value_integrity",
                "external_review_request",
                "packet_guardrails",
            }
        )
        claim_coverage_complete = all(
            row.coverage_state == PASS_STATE for row in coverage
        )
        witness_complete = all(
            row.independent_witness_count >= 1
            and row.independent_lineage_count >= 2
            for row in coverage
            if row.claim_class == "DOCTRINE"
        )
        conflict_gate = next(
            gate for gate in gates if gate.gate_id == "source_conflict_resolution"
        )
        conflicts_resolved = conflict_gate.state == PASS_STATE
        ready = (
            profile_report.structural_complete
            and packet_structural_complete
            and claim_coverage_complete
            and witness_complete
            and conflicts_resolved
            and all(gate.state == PASS_STATE for gate in gates)
        )

        if packet_payload is None:
            packet_status = NO_PACKET_LOADED
        elif ready:
            packet_status = READY_FOR_EXTERNAL_REVIEW
        else:
            packet_status = NOT_READY_FOR_EXTERNAL_REVIEW

        missing_requirements = tuple(
            gate.label for gate in gates if gate.state != PASS_STATE
        )
        return TimingProfileSourceReadinessReport(
            packet_status=packet_status,
            profile_id=(
                str(profile.get("profileId"))
                if profile_report.structural_complete
                else None
            ),
            profile_version=(
                str(profile.get("profileVersion"))
                if profile_report.structural_complete
                else None
            ),
            candidate_profile_hash=candidate_hash,
            packet_id=(
                str(packet.get("packetId"))
                if packet_present and isinstance(packet.get("packetId"), str)
                else None
            ),
            packet_hash=packet_hash,
            candidate_structural_complete=profile_report.structural_complete,
            packet_structural_complete=packet_structural_complete,
            claim_coverage_complete=claim_coverage_complete,
            independent_witness_coverage_complete=witness_complete,
            conflicts_resolved=conflicts_resolved,
            ready_for_external_review=ready,
            external_review_completed=False,
            source_certified=False,
            profile_registration_allowed=False,
            validation_gates=tuple(gates),
            claim_coverage=coverage,
            missing_requirements=missing_requirements,
        )
