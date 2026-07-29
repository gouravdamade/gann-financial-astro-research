from __future__ import annotations

import hashlib
import json

from sbc.timing_profile_admission import SbcTimingProfileAdmissionGate
from sbc.timing_profile_source_packet import (
    FAIL_STATE,
    NO_PACKET_LOADED,
    PASS_STATE,
    READY_FOR_EXTERNAL_REVIEW,
    UNKNOWN_STATE,
    SbcTimingProfileSourcePacketGate,
)
from test_sbc_t0_timing_profile_admission import _candidate as _base_candidate
from test_sbc_t0_timing_profile_admission import _registry


def _hash(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest().upper()


def _candidate() -> dict:
    candidate = _base_candidate()
    candidate["sourceEvidence"] = [
        {
            "sourceId": "primary-doctrine",
            "citation": "Primary source",
            "sha256": "A" * 64,
            "role": "PRIMARY_SOURCE",
        },
        {
            "sourceId": "independent-witness",
            "citation": "Independent witness",
            "sha256": "B" * 64,
            "role": "INDEPENDENT_WITNESS",
        },
        {
            "sourceId": "research-specification",
            "citation": "Frozen research specification",
            "sha256": "C" * 64,
            "role": "RESEARCH_SPECIFICATION",
        },
    ]
    return candidate


def _profile_hash(candidate: dict) -> str:
    return SbcTimingProfileAdmissionGate(_registry()).evaluate(
        candidate
    ).candidate_profile_hash


def _packet(candidate: dict) -> dict:
    doctrine_paths = (
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
    research_paths = ("/eligibilityPolicy", "/confidencePolicy")
    claims = []
    for profile_path in doctrine_paths:
        field_name = profile_path.removeprefix("/")
        for suffix, source_id, evidence_role in (
            ("primary", "primary-doctrine", "PRIMARY_SOURCE"),
            ("witness", "independent-witness", "INDEPENDENT_WITNESS"),
        ):
            claims.append(
                {
                    "claimId": f"{field_name}-{suffix}",
                    "profilePath": profile_path,
                    "candidateValueSha256": _hash(candidate[field_name]),
                    "sourceId": source_id,
                    "citation": f"{suffix.title()} source, printed page 10",
                    "pageStart": 10,
                    "pageEnd": 11,
                    "evidenceRole": evidence_role,
                    "excerptSha256": ("D" if suffix == "primary" else "E") * 64,
                    "note": f"Supports the complete {field_name} candidate value.",
                }
            )
    for profile_path in research_paths:
        field_name = profile_path.removeprefix("/")
        claims.append(
            {
                "claimId": f"{field_name}-research",
                "profilePath": profile_path,
                "candidateValueSha256": _hash(candidate[field_name]),
                "sourceId": "research-specification",
                "citation": "Frozen research specification, page 5",
                "pageStart": 5,
                "pageEnd": 6,
                "evidenceRole": "RESEARCH_SPECIFICATION",
                "excerptSha256": "F" * 64,
                "note": f"Freezes the {field_name} research protocol.",
            }
        )
    return {
        "contract": "SBC_TIMING_PROFILE_SOURCE_PACKET_V1",
        "schemaVersion": 1,
        "packetId": "candidate-source-packet-v1",
        "packetVersion": "1.0.0",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
        "frozen": True,
        "profileId": candidate["profileId"],
        "profileVersion": candidate["profileVersion"],
        "profileHash": _profile_hash(candidate),
        "preparedAtUtc": "2026-07-29T03:00:00Z",
        "preparedBy": "profile author",
        "sourceArtifacts": [
            {
                "sourceId": "primary-doctrine",
                "title": "Primary doctrine source",
                "edition": "First reviewed edition",
                "language": "Sanskrit and English",
                "publicationYear": 1972,
                "sha256": "A" * 64,
                "lineageId": "primary-lineage",
                "sourceRole": "PRIMARY_SOURCE",
            },
            {
                "sourceId": "independent-witness",
                "title": "Independent doctrine witness",
                "edition": "Independent edition",
                "language": "English",
                "publicationYear": 1951,
                "sha256": "B" * 64,
                "lineageId": "independent-lineage",
                "sourceRole": "INDEPENDENT_WITNESS",
            },
            {
                "sourceId": "research-specification",
                "title": "Frozen research protocol",
                "edition": "Version 1",
                "language": "English",
                "publicationYear": 2026,
                "sha256": "C" * 64,
                "lineageId": "research-lineage",
                "sourceRole": "RESEARCH_SPECIFICATION",
            },
        ],
        "claims": claims,
        "conflictRegister": [],
        "reviewRequest": {
            "requestedDecision": "SOURCE_CERTIFICATION",
            "requiredReviewerIndependence": "EXTERNAL_TO_PROFILE_AUTHOR",
            "requiredReviewScope": [
                "SOURCE_IDENTITY",
                "PAGE_CITATIONS",
                "CLAIM_VALUE_BINDING",
                "INDEPENDENT_LINEAGE",
                "CONFLICT_RESOLUTION",
            ],
            "certificationRegistryWriteAllowed": False,
        },
        "guardrails": {
            "researchOnly": True,
            "readOnly": True,
            "packetPersisted": False,
            "profileValuesSuppliedByApplication": False,
            "sourceBytesVerifiedByApplication": False,
            "externalReviewCompleted": False,
            "sourceCertified": False,
            "profileRegistrationAllowed": False,
            "noAutoSuggest": True,
            "noLiveInference": True,
            "noOfficialMlNotes": True,
            "noShadowVote": True,
            "noTradeOutput": True,
            "executionAllowed": False,
        },
    }


def _gate(report, gate_id: str):
    return next(item for item in report.validation_gates if item.gate_id == gate_id)


def test_missing_packet_stays_unknown_and_execution_locked() -> None:
    candidate = _candidate()

    report = SbcTimingProfileSourcePacketGate().evaluate(candidate, None)

    assert report.packet_status == NO_PACKET_LOADED
    assert _gate(report, "candidate_profile_structure").state == PASS_STATE
    assert _gate(report, "source_packet_contract").state == UNKNOWN_STATE
    assert report.ready_for_external_review is False
    assert report.source_certified is False
    assert report.guardrails["execution_allowed"] is False


def test_complete_packet_is_ready_for_external_review_but_not_certified() -> None:
    candidate = _candidate()

    report = SbcTimingProfileSourcePacketGate().evaluate(
        candidate,
        _packet(candidate),
    )

    assert report.packet_status == READY_FOR_EXTERNAL_REVIEW
    assert report.candidate_structural_complete is True
    assert report.packet_structural_complete is True
    assert report.claim_coverage_complete is True
    assert report.independent_witness_coverage_complete is True
    assert report.conflicts_resolved is True
    assert report.ready_for_external_review is True
    assert report.external_review_completed is False
    assert report.source_certified is False
    assert report.profile_registration_allowed is False
    assert all(row.coverage_state == PASS_STATE for row in report.claim_coverage)


def test_packet_profile_hash_mismatch_fails_closed() -> None:
    candidate = _candidate()
    packet = _packet(candidate)
    packet["profileHash"] = "9" * 64

    report = SbcTimingProfileSourcePacketGate().evaluate(candidate, packet)

    assert _gate(report, "exact_profile_hash_link").state == FAIL_STATE
    assert report.ready_for_external_review is False
    assert report.source_certified is False


def test_claim_value_hash_mismatch_is_not_accepted_as_evidence() -> None:
    candidate = _candidate()
    packet = _packet(candidate)
    packet["claims"][0]["candidateValueSha256"] = "8" * 64

    report = SbcTimingProfileSourcePacketGate().evaluate(candidate, packet)

    assert _gate(report, "claim_value_integrity").state == FAIL_STATE
    assert report.claim_coverage_complete is False
    assert report.ready_for_external_review is False


def test_missing_witness_claim_blocks_doctrine_readiness() -> None:
    candidate = _candidate()
    packet = _packet(candidate)
    packet["claims"] = [
        claim
        for claim in packet["claims"]
        if not (
            claim["profilePath"] == "/phaseSpan"
            and claim["evidenceRole"] == "INDEPENDENT_WITNESS"
        )
    ]

    report = SbcTimingProfileSourcePacketGate().evaluate(candidate, packet)

    assert _gate(report, "independent_witness_coverage").state == FAIL_STATE
    row = next(
        item for item in report.claim_coverage if item.profile_path == "/phaseSpan"
    )
    assert row.independent_witness_count == 0
    assert report.ready_for_external_review is False


def test_witness_from_same_declared_lineage_is_not_independent() -> None:
    candidate = _candidate()
    packet = _packet(candidate)
    packet["sourceArtifacts"][1]["lineageId"] = "primary-lineage"

    report = SbcTimingProfileSourcePacketGate().evaluate(candidate, packet)

    assert _gate(report, "independent_witness_coverage").state == FAIL_STATE
    assert report.independent_witness_coverage_complete is False
    assert report.ready_for_external_review is False


def test_unresolved_source_conflict_blocks_readiness() -> None:
    candidate = _candidate()
    packet = _packet(candidate)
    packet["conflictRegister"] = [
        {
            "conflictId": "sector-boundary-conflict",
            "profilePath": "/sectors",
            "sourceIds": ["primary-doctrine", "independent-witness"],
            "status": "UNRESOLVED",
            "resolution": "",
            "chosenSourceId": "",
        }
    ]

    report = SbcTimingProfileSourcePacketGate().evaluate(candidate, packet)

    assert _gate(report, "source_conflict_resolution").state == FAIL_STATE
    assert report.conflicts_resolved is False
    assert report.ready_for_external_review is False


def test_packet_cannot_claim_certification_registration_or_execution() -> None:
    candidate = _candidate()
    packet = _packet(candidate)
    packet["guardrails"]["sourceCertified"] = True
    packet["guardrails"]["profileRegistrationAllowed"] = True
    packet["guardrails"]["executionAllowed"] = True

    report = SbcTimingProfileSourcePacketGate().evaluate(candidate, packet)

    assert _gate(report, "packet_guardrails").state == FAIL_STATE
    assert report.source_certified is False
    assert report.profile_registration_allowed is False
    assert report.guardrails["execution_allowed"] is False


def test_candidate_source_hash_mismatch_blocks_source_declaration_gate() -> None:
    candidate = _candidate()
    packet = _packet(candidate)
    packet["sourceArtifacts"][0]["sha256"] = "7" * 64

    report = SbcTimingProfileSourcePacketGate().evaluate(candidate, packet)

    assert _gate(report, "source_declarations").state == FAIL_STATE
    assert report.ready_for_external_review is False
