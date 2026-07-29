from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from .atomic_intervals import RESEARCH_CLASSIFICATION
from .models import to_primitive
from .timing_profile_source_packet import (
    FAIL_STATE,
    PASS_STATE,
    UNKNOWN_STATE,
    SbcTimingProfileSourcePacketGate,
)


SOURCE_VERIFICATION_REPORT_CONTRACT = (
    "SBC_TIMING_PROFILE_SOURCE_BYTE_VERIFICATION_REPORT_V1"
)
SOURCE_VERIFICATION_REPORT_SCHEMA_VERSION = 1
SOURCE_VERIFICATION_POLICY = "EXACT_SOURCE_BYTES_AND_UTF8_EXCERPT_PAYLOADS_V1"

INDEPENDENT_REVIEW_BUNDLE_CONTRACT = (
    "SBC_TIMING_PROFILE_INDEPENDENT_REVIEW_BUNDLE_V1"
)
INDEPENDENT_REVIEW_BUNDLE_SCHEMA_VERSION = 1
EXTERNAL_REVIEW_ATTESTATION_CONTRACT = (
    "SBC_TIMING_PROFILE_EXTERNAL_REVIEW_ATTESTATION_V1"
)

NO_VERIFICATION_PAYLOAD = "NO_VERIFICATION_PAYLOAD"
SOURCE_VERIFICATION_FAILED = "SOURCE_VERIFICATION_FAILED"
READY_FOR_INDEPENDENT_REVIEW = "READY_FOR_INDEPENDENT_REVIEW"

SOURCE_HASH_METHOD = "SHA256_EXACT_SUPPLIED_BYTES"
EXCERPT_HASH_METHOD = "SHA256_EXACT_UTF8_NO_NORMALIZATION"
REVIEW_BUNDLE_HASH_METHOD = (
    "CANONICAL_JSON_SHA256_WITH_ATTESTATION_BUNDLE_HASH_BLANK"
)


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def independent_review_bundle_hash(bundle: Mapping[str, Any]) -> str:
    if not isinstance(bundle, Mapping):
        raise ValueError("independent review bundle must be an object")
    normalized = json.loads(
        json.dumps(
            bundle,
            ensure_ascii=True,
            allow_nan=False,
        )
    )
    if normalized.get("contract") != INDEPENDENT_REVIEW_BUNDLE_CONTRACT:
        raise ValueError("independent review bundle contract is unsupported")
    if normalized.get("schemaVersion") != INDEPENDENT_REVIEW_BUNDLE_SCHEMA_VERSION:
        raise ValueError("independent review bundle schemaVersion is unsupported")
    attestation = normalized.get("attestationTemplate")
    if not isinstance(attestation, dict):
        raise ValueError("independent review bundle attestationTemplate is required")
    attestation["bundleSha256"] = ""
    return _canonical_hash(normalized)


def _bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


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


def _payload_map(
    value: Mapping[str, Any] | None,
    label: str,
) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object keyed by identifier")
    normalized: dict[str, Any] = {}
    for raw_key, item in value.items():
        key = _required_text(raw_key, f"{label} key")
        if key in normalized:
            raise ValueError(f"{label} contains duplicate identifier {key}")
        normalized[key] = item
    return normalized


@dataclass(frozen=True)
class TimingSourceVerificationGate:
    gate_id: str
    state: str
    mandatory: bool
    label: str
    detail: str
    missing_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in {PASS_STATE, FAIL_STATE, UNKNOWN_STATE}:
            raise ValueError(f"unknown gate state: {self.state}")
        object.__setattr__(self, "gate_id", _required_text(self.gate_id, "gate_id"))
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "detail", _required_text(self.detail, "detail"))
        object.__setattr__(
            self,
            "missing_ids",
            tuple(_required_text(item, "missing_id") for item in self.missing_ids),
        )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingSourceArtifactByteCheck:
    source_id: str
    source_role: str
    lineage_id: str
    expected_sha256: str
    observed_sha256: str | None
    observed_byte_length: int | None
    verification_state: str
    detail: str
    hash_method: str = SOURCE_HASH_METHOD

    def __post_init__(self) -> None:
        if self.verification_state not in {
            PASS_STATE,
            FAIL_STATE,
            UNKNOWN_STATE,
        }:
            raise ValueError(
                f"unknown source verification state: {self.verification_state}"
            )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingExcerptPayloadCheck:
    claim_id: str
    profile_path: str
    source_id: str
    page_start: int
    page_end: int
    expected_sha256: str
    observed_sha256: str | None
    observed_utf8_byte_length: int | None
    verification_state: str
    detail: str
    hash_method: str = EXCERPT_HASH_METHOD

    def __post_init__(self) -> None:
        if self.verification_state not in {
            PASS_STATE,
            FAIL_STATE,
            UNKNOWN_STATE,
        }:
            raise ValueError(
                f"unknown excerpt verification state: {self.verification_state}"
            )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingProfileSourceVerificationReport:
    verification_status: str
    profile_id: str | None
    profile_version: str | None
    candidate_profile_hash: str | None
    packet_id: str | None
    packet_hash: str | None
    s1_ready_for_external_review: bool
    all_source_bytes_verified: bool
    all_excerpt_payloads_verified: bool
    ready_for_independent_review: bool
    source_artifact_checks: tuple[TimingSourceArtifactByteCheck, ...]
    excerpt_payload_checks: tuple[TimingExcerptPayloadCheck, ...]
    validation_gates: tuple[TimingSourceVerificationGate, ...]
    missing_requirements: tuple[str, ...]
    review_bundle: dict[str, Any] | None
    review_bundle_sha256: str | None
    contract: str = SOURCE_VERIFICATION_REPORT_CONTRACT
    schema_version: int = SOURCE_VERIFICATION_REPORT_SCHEMA_VERSION
    verification_policy: str = SOURCE_VERIFICATION_POLICY
    classification: str = RESEARCH_CLASSIFICATION
    external_review_completed: bool = False
    source_certified: bool = False
    profile_registration_allowed: bool = False
    guardrails: dict[str, Any] = field(
        default_factory=lambda: {
            "research_only": True,
            "read_only": True,
            "payloads_persisted": False,
            "source_bytes_included_in_bundle": False,
            "excerpt_text_included_in_bundle": False,
            "page_presence_checked": False,
            "doctrine_correctness_checked": False,
            "external_review_completed": False,
            "source_certified": False,
            "profile_registration_allowed": False,
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
                "PAGE_CITATION_VERIFICATION",
                "DOCTRINE_CORRECTNESS_REVIEW",
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
            raise ValueError("S2 cannot claim an external review")
        if self.source_certified:
            raise ValueError("S2 cannot certify source doctrine")
        if self.profile_registration_allowed:
            raise ValueError("S2 cannot register a timing profile")
        if self.guardrails.get("execution_allowed") is not False:
            raise ValueError("S2 execution must remain locked")
        if float(self.guardrails.get("directional_contribution", 1.0)) != 0.0:
            raise ValueError("S2 cannot contribute market direction")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


class SbcTimingProfileSourceVerificationCompiler:
    @staticmethod
    def _packet_sources(packet: dict[str, Any]) -> list[dict[str, Any]]:
        raw_sources = packet.get("sourceArtifacts")
        if not isinstance(raw_sources, list) or not raw_sources:
            raise ValueError("packet.sourceArtifacts must be a non-empty array")
        sources: list[dict[str, Any]] = []
        source_ids: set[str] = set()
        for index, item in enumerate(raw_sources):
            if not isinstance(item, dict):
                raise ValueError(f"packet.sourceArtifacts[{index}] must be an object")
            source_id = _required_text(
                item.get("sourceId"),
                f"packet.sourceArtifacts[{index}].sourceId",
            )
            if source_id in source_ids:
                raise ValueError(f"duplicate packet sourceId: {source_id}")
            source_ids.add(source_id)
            _sha256(item.get("sha256"), f"sourceArtifacts[{source_id}].sha256")
            _required_text(
                item.get("sourceRole"),
                f"sourceArtifacts[{source_id}].sourceRole",
            )
            _required_text(
                item.get("lineageId"),
                f"sourceArtifacts[{source_id}].lineageId",
            )
            sources.append(item)
        return sources

    @staticmethod
    def _packet_claims(packet: dict[str, Any]) -> list[dict[str, Any]]:
        raw_claims = packet.get("claims")
        if not isinstance(raw_claims, list) or not raw_claims:
            raise ValueError("packet.claims must be a non-empty array")
        claims: list[dict[str, Any]] = []
        claim_ids: set[str] = set()
        for index, item in enumerate(raw_claims):
            if not isinstance(item, dict):
                raise ValueError(f"packet.claims[{index}] must be an object")
            claim_id = _required_text(
                item.get("claimId"),
                f"packet.claims[{index}].claimId",
            )
            if claim_id in claim_ids:
                raise ValueError(f"duplicate packet claimId: {claim_id}")
            claim_ids.add(claim_id)
            _required_text(item.get("profilePath"), f"claims[{claim_id}].profilePath")
            _required_text(item.get("sourceId"), f"claims[{claim_id}].sourceId")
            _sha256(
                item.get("excerptSha256"),
                f"claims[{claim_id}].excerptSha256",
            )
            page_start = item.get("pageStart")
            page_end = item.get("pageEnd")
            if (
                isinstance(page_start, bool)
                or not isinstance(page_start, int)
                or page_start <= 0
                or isinstance(page_end, bool)
                or not isinstance(page_end, int)
                or page_end < page_start
            ):
                raise ValueError(f"claims[{claim_id}] has an invalid page range")
            claims.append(item)
        return claims

    @classmethod
    def _source_checks(
        cls,
        packet: dict[str, Any],
        source_payloads: Mapping[str, bytes] | None,
    ) -> tuple[TimingSourceArtifactByteCheck, ...]:
        sources = cls._packet_sources(packet)
        normalized = _payload_map(source_payloads, "source_payloads")
        rows: list[TimingSourceArtifactByteCheck] = []
        for source in sources:
            source_id = str(source["sourceId"])
            expected = _sha256(source.get("sha256"), f"{source_id}.sha256")
            if normalized is None or source_id not in normalized:
                rows.append(
                    TimingSourceArtifactByteCheck(
                        source_id=source_id,
                        source_role=str(source["sourceRole"]),
                        lineage_id=str(source["lineageId"]),
                        expected_sha256=expected,
                        observed_sha256=None,
                        observed_byte_length=None,
                        verification_state=UNKNOWN_STATE,
                        detail="Exact source bytes have not been supplied.",
                    )
                )
                continue
            raw = normalized[source_id]
            if not isinstance(raw, bytes) or not raw:
                rows.append(
                    TimingSourceArtifactByteCheck(
                        source_id=source_id,
                        source_role=str(source["sourceRole"]),
                        lineage_id=str(source["lineageId"]),
                        expected_sha256=expected,
                        observed_sha256=None,
                        observed_byte_length=(len(raw) if isinstance(raw, bytes) else None),
                        verification_state=FAIL_STATE,
                        detail="Source payload must be non-empty bytes.",
                    )
                )
                continue
            observed = _bytes_hash(raw)
            matched = observed == expected
            rows.append(
                TimingSourceArtifactByteCheck(
                    source_id=source_id,
                    source_role=str(source["sourceRole"]),
                    lineage_id=str(source["lineageId"]),
                    expected_sha256=expected,
                    observed_sha256=observed,
                    observed_byte_length=len(raw),
                    verification_state=PASS_STATE if matched else FAIL_STATE,
                    detail=(
                        "Exact supplied source bytes match the frozen packet digest."
                        if matched
                        else "Supplied source bytes do not match the frozen packet digest."
                    ),
                )
            )
        return tuple(rows)

    @classmethod
    def _excerpt_checks(
        cls,
        packet: dict[str, Any],
        excerpt_payloads: Mapping[str, str] | None,
    ) -> tuple[TimingExcerptPayloadCheck, ...]:
        claims = cls._packet_claims(packet)
        normalized = _payload_map(excerpt_payloads, "excerpt_payloads")
        rows: list[TimingExcerptPayloadCheck] = []
        for claim in claims:
            claim_id = str(claim["claimId"])
            expected = _sha256(
                claim.get("excerptSha256"),
                f"{claim_id}.excerptSha256",
            )
            if normalized is None or claim_id not in normalized:
                rows.append(
                    TimingExcerptPayloadCheck(
                        claim_id=claim_id,
                        profile_path=str(claim["profilePath"]),
                        source_id=str(claim["sourceId"]),
                        page_start=int(claim["pageStart"]),
                        page_end=int(claim["pageEnd"]),
                        expected_sha256=expected,
                        observed_sha256=None,
                        observed_utf8_byte_length=None,
                        verification_state=UNKNOWN_STATE,
                        detail="Exact UTF-8 excerpt payload has not been supplied.",
                    )
                )
                continue
            raw = normalized[claim_id]
            if not isinstance(raw, str) or not raw:
                rows.append(
                    TimingExcerptPayloadCheck(
                        claim_id=claim_id,
                        profile_path=str(claim["profilePath"]),
                        source_id=str(claim["sourceId"]),
                        page_start=int(claim["pageStart"]),
                        page_end=int(claim["pageEnd"]),
                        expected_sha256=expected,
                        observed_sha256=None,
                        observed_utf8_byte_length=None,
                        verification_state=FAIL_STATE,
                        detail="Excerpt payload must be a non-empty string.",
                    )
                )
                continue
            excerpt_bytes = raw.encode("utf-8")
            observed = _bytes_hash(excerpt_bytes)
            matched = observed == expected
            rows.append(
                TimingExcerptPayloadCheck(
                    claim_id=claim_id,
                    profile_path=str(claim["profilePath"]),
                    source_id=str(claim["sourceId"]),
                    page_start=int(claim["pageStart"]),
                    page_end=int(claim["pageEnd"]),
                    expected_sha256=expected,
                    observed_sha256=observed,
                    observed_utf8_byte_length=len(excerpt_bytes),
                    verification_state=PASS_STATE if matched else FAIL_STATE,
                    detail=(
                        "Exact UTF-8 excerpt payload matches the frozen claim digest."
                        if matched
                        else "UTF-8 excerpt payload does not match the frozen claim digest."
                    ),
                )
            )
        return tuple(rows)

    @staticmethod
    def _unexpected_ids(
        supplied: Mapping[str, Any] | None,
        expected_ids: set[str],
    ) -> tuple[str, ...]:
        if supplied is None:
            return ()
        return tuple(sorted(set(supplied) - expected_ids))

    @staticmethod
    def _verification_gate(
        gate_id: str,
        label: str,
        rows: tuple[
            TimingSourceArtifactByteCheck | TimingExcerptPayloadCheck,
            ...,
        ],
        *,
        supplied: Mapping[str, Any] | None,
        unexpected_ids: tuple[str, ...],
    ) -> TimingSourceVerificationGate:
        if supplied is None:
            return TimingSourceVerificationGate(
                gate_id=gate_id,
                state=UNKNOWN_STATE,
                mandatory=True,
                label=label,
                detail="Verification payloads are not loaded.",
                missing_ids=tuple(
                    row.source_id
                    if isinstance(row, TimingSourceArtifactByteCheck)
                    else row.claim_id
                    for row in rows
                ),
            )
        failed = [
            row.source_id
            if isinstance(row, TimingSourceArtifactByteCheck)
            else row.claim_id
            for row in rows
            if row.verification_state != PASS_STATE
        ]
        if unexpected_ids:
            failed.extend(f"unexpected:{item}" for item in unexpected_ids)
        if failed:
            return TimingSourceVerificationGate(
                gate_id=gate_id,
                state=FAIL_STATE,
                mandatory=True,
                label=label,
                detail="Exact verification is incomplete or mismatched.",
                missing_ids=tuple(failed),
            )
        return TimingSourceVerificationGate(
            gate_id=gate_id,
            state=PASS_STATE,
            mandatory=True,
            label=label,
            detail=f"All {len(rows)} required payload(s) match exact frozen digests.",
        )

    @classmethod
    def _review_bundle(
        cls,
        profile: dict[str, Any],
        packet: dict[str, Any],
        source_checks: tuple[TimingSourceArtifactByteCheck, ...],
        excerpt_checks: tuple[TimingExcerptPayloadCheck, ...],
    ) -> tuple[dict[str, Any], str]:
        profile_hash = _canonical_hash(profile)
        packet_hash = _canonical_hash(packet)
        bundle = {
            "contract": INDEPENDENT_REVIEW_BUNDLE_CONTRACT,
            "schemaVersion": INDEPENDENT_REVIEW_BUNDLE_SCHEMA_VERSION,
            "classification": RESEARCH_CLASSIFICATION,
            "bundleId": f"s2-{profile_hash[:12]}-{packet_hash[:12]}",
            "profile": profile,
            "sourcePacket": packet,
            "verification": {
                "policy": SOURCE_VERIFICATION_POLICY,
                "sourceHashMethod": SOURCE_HASH_METHOD,
                "excerptHashMethod": EXCERPT_HASH_METHOD,
                "reviewBundleHashMethod": REVIEW_BUNDLE_HASH_METHOD,
                "sourceArtifacts": [
                    item.to_dict() for item in source_checks
                ],
                "excerptPayloads": [
                    item.to_dict() for item in excerpt_checks
                ],
            },
            "requiredIndependentReview": {
                "reviewerIndependence": "EXTERNAL_TO_PROFILE_AUTHOR",
                "scope": [
                    "SOURCE_IDENTITY",
                    "SOURCE_BYTES",
                    "PAGE_CITATIONS",
                    "EXCERPT_PAGE_PRESENCE",
                    "CLAIM_VALUE_BINDING",
                    "INDEPENDENT_LINEAGE",
                    "CONFLICT_RESOLUTION",
                    "DOCTRINE_CORRECTNESS",
                ],
                "instructions": [
                    "Acquire or inspect each source independently and confirm its exact digest.",
                    "Visually confirm every excerpt on the cited printed pages.",
                    "Judge whether each cited passage supports the complete candidate value.",
                    "Check that witness lineages are genuinely independent.",
                    "Review every conflict decision and its written justification.",
                    "Do not treat this bundle or its hashes as source certification.",
                ],
            },
            "attestationTemplate": {
                "contract": EXTERNAL_REVIEW_ATTESTATION_CONTRACT,
                "schemaVersion": 1,
                "bundleSha256": "",
                "reviewDecision": "PENDING",
                "reviewerIdentity": "",
                "reviewerOrganization": "",
                "reviewerIndependenceConfirmed": False,
                "reviewedAtUtc": "",
                "sourceArtifactDecisions": [
                    {
                        "sourceId": item.source_id,
                        "decision": "PENDING",
                        "note": "",
                    }
                    for item in source_checks
                ],
                "claimDecisions": [
                    {
                        "claimId": item.claim_id,
                        "decision": "PENDING",
                        "note": "",
                    }
                    for item in excerpt_checks
                ],
                "conflictDecisions": [
                    {
                        "conflictId": str(item.get("conflictId", "")),
                        "decision": "PENDING",
                        "note": "",
                    }
                    for item in packet.get("conflictRegister", [])
                    if isinstance(item, dict)
                ],
                "overallNote": "",
                "registryWriteAllowed": False,
            },
            "guardrails": {
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
            },
        }
        bundle_hash = independent_review_bundle_hash(bundle)
        bundle["attestationTemplate"]["bundleSha256"] = bundle_hash
        return bundle, bundle_hash

    def compile(
        self,
        profile_payload: Any | None,
        packet_payload: Any | None,
        source_payloads: Mapping[str, bytes] | None = None,
        excerpt_payloads: Mapping[str, str] | None = None,
    ) -> TimingProfileSourceVerificationReport:
        profile = profile_payload if isinstance(profile_payload, dict) else {}
        packet = packet_payload if isinstance(packet_payload, dict) else {}
        s1_report = SbcTimingProfileSourcePacketGate().evaluate(
            profile_payload,
            packet_payload,
        )

        source_rows: tuple[TimingSourceArtifactByteCheck, ...] = ()
        excerpt_rows: tuple[TimingExcerptPayloadCheck, ...] = ()
        source_input = _payload_map(source_payloads, "source_payloads")
        excerpt_input = _payload_map(excerpt_payloads, "excerpt_payloads")
        packet_shape_error: str | None = None
        expected_source_ids: set[str] = set()
        expected_claim_ids: set[str] = set()
        if isinstance(packet_payload, dict):
            try:
                sources = self._packet_sources(packet)
                claims = self._packet_claims(packet)
                expected_source_ids = {str(item["sourceId"]) for item in sources}
                expected_claim_ids = {str(item["claimId"]) for item in claims}
                source_rows = self._source_checks(packet, source_input)
                excerpt_rows = self._excerpt_checks(packet, excerpt_input)
            except (TypeError, ValueError) as exc:
                packet_shape_error = str(exc)

        if profile_payload is None or packet_payload is None:
            s1_state = UNKNOWN_STATE
            s1_detail = "A T0 candidate and S1 source packet are required."
        elif s1_report.ready_for_external_review:
            s1_state = PASS_STATE
            s1_detail = "The candidate and packet pass every S1 readiness gate."
        else:
            s1_state = FAIL_STATE
            s1_detail = "The candidate or source packet fails S1 readiness."
        gates = [
            TimingSourceVerificationGate(
                gate_id="s1_packet_readiness",
                state=s1_state,
                mandatory=True,
                label="S1 packet readiness",
                detail=s1_detail,
                missing_ids=(
                    ()
                    if s1_state == PASS_STATE
                    else tuple(s1_report.missing_requirements)
                ),
            )
        ]

        if packet_shape_error is not None:
            gates.extend(
                [
                    TimingSourceVerificationGate(
                        gate_id="exact_source_bytes",
                        state=FAIL_STATE,
                        mandatory=True,
                        label="Exact source bytes",
                        detail=f"Source packet cannot be enumerated: {packet_shape_error}",
                    ),
                    TimingSourceVerificationGate(
                        gate_id="exact_excerpt_payloads",
                        state=FAIL_STATE,
                        mandatory=True,
                        label="Exact UTF-8 excerpt payloads",
                        detail=f"Source packet cannot be enumerated: {packet_shape_error}",
                    ),
                ]
            )
        elif not isinstance(packet_payload, dict):
            gates.extend(
                [
                    TimingSourceVerificationGate(
                        gate_id="exact_source_bytes",
                        state=UNKNOWN_STATE,
                        mandatory=True,
                        label="Exact source bytes",
                        detail="A source packet is required before source bytes can be checked.",
                    ),
                    TimingSourceVerificationGate(
                        gate_id="exact_excerpt_payloads",
                        state=UNKNOWN_STATE,
                        mandatory=True,
                        label="Exact UTF-8 excerpt payloads",
                        detail="A source packet is required before excerpts can be checked.",
                    ),
                ]
            )
        else:
            gates.append(
                self._verification_gate(
                    "exact_source_bytes",
                    "Exact source bytes",
                    source_rows,
                    supplied=source_input,
                    unexpected_ids=self._unexpected_ids(
                        source_input,
                        expected_source_ids,
                    ),
                )
            )
            gates.append(
                self._verification_gate(
                    "exact_excerpt_payloads",
                    "Exact UTF-8 excerpt payloads",
                    excerpt_rows,
                    supplied=excerpt_input,
                    unexpected_ids=self._unexpected_ids(
                        excerpt_input,
                        expected_claim_ids,
                    ),
                )
            )

        export_guard = TimingSourceVerificationGate(
            gate_id="review_bundle_guardrails",
            state=PASS_STATE,
            mandatory=True,
            label="Independent-review bundle guardrails",
            detail=(
                "Bundle excludes source bytes and excerpt text and cannot complete "
                "review, certify doctrine, register a profile, or enable execution."
            ),
        )
        gates.append(export_guard)

        all_sources = (
            bool(source_rows)
            and all(item.verification_state == PASS_STATE for item in source_rows)
            and not self._unexpected_ids(source_input, expected_source_ids)
        )
        all_excerpts = (
            bool(excerpt_rows)
            and all(item.verification_state == PASS_STATE for item in excerpt_rows)
            and not self._unexpected_ids(excerpt_input, expected_claim_ids)
        )
        ready = (
            s1_report.ready_for_external_review
            and all_sources
            and all_excerpts
            and all(gate.state == PASS_STATE for gate in gates)
        )

        review_bundle: dict[str, Any] | None = None
        review_bundle_hash: str | None = None
        if ready:
            review_bundle, review_bundle_hash = self._review_bundle(
                profile,
                packet,
                source_rows,
                excerpt_rows,
            )

        if source_payloads is None and excerpt_payloads is None:
            status = NO_VERIFICATION_PAYLOAD
        elif ready:
            status = READY_FOR_INDEPENDENT_REVIEW
        else:
            status = SOURCE_VERIFICATION_FAILED

        return TimingProfileSourceVerificationReport(
            verification_status=status,
            profile_id=s1_report.profile_id,
            profile_version=s1_report.profile_version,
            candidate_profile_hash=s1_report.candidate_profile_hash,
            packet_id=s1_report.packet_id,
            packet_hash=s1_report.packet_hash,
            s1_ready_for_external_review=s1_report.ready_for_external_review,
            all_source_bytes_verified=all_sources,
            all_excerpt_payloads_verified=all_excerpts,
            ready_for_independent_review=ready,
            source_artifact_checks=source_rows,
            excerpt_payload_checks=excerpt_rows,
            validation_gates=tuple(gates),
            missing_requirements=tuple(
                gate.label for gate in gates if gate.state != PASS_STATE
            ),
            review_bundle=review_bundle,
            review_bundle_sha256=review_bundle_hash,
        )
