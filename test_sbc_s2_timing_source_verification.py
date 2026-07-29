from __future__ import annotations

import hashlib
import json

from sbc.timing_profile_admission import SbcTimingProfileAdmissionGate
from sbc.timing_profile_source_packet import FAIL_STATE, PASS_STATE, UNKNOWN_STATE
from sbc.timing_profile_source_verification import (
    NO_VERIFICATION_PAYLOAD,
    READY_FOR_INDEPENDENT_REVIEW,
    SOURCE_VERIFICATION_FAILED,
    REVIEW_BUNDLE_HASH_METHOD,
    SbcTimingProfileSourceVerificationCompiler,
    independent_review_bundle_hash,
)
from test_sbc_s1_timing_source_packet import _candidate as _s1_candidate
from test_sbc_s1_timing_source_packet import _packet as _s1_packet
from test_sbc_t0_timing_profile_admission import _registry


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _evidence() -> tuple[dict, dict, dict[str, bytes], dict[str, str]]:
    candidate = _s1_candidate()
    source_payloads = {
        "primary-doctrine": b"primary doctrine source bytes",
        "independent-witness": b"independent witness source bytes",
        "research-specification": b"frozen research specification bytes",
    }
    source_hashes = {
        source_id: _sha_bytes(payload)
        for source_id, payload in source_payloads.items()
    }
    for source in candidate["sourceEvidence"]:
        source["sha256"] = source_hashes[source["sourceId"]]

    packet = _s1_packet(candidate)
    for source in packet["sourceArtifacts"]:
        source["sha256"] = source_hashes[source["sourceId"]]
    packet["profileHash"] = SbcTimingProfileAdmissionGate(_registry()).evaluate(
        candidate
    ).candidate_profile_hash

    excerpt_payloads = {
        claim["claimId"]: f"Exact UTF-8 excerpt for {claim['claimId']}."
        for claim in packet["claims"]
    }
    for claim in packet["claims"]:
        claim["excerptSha256"] = _sha_bytes(
            excerpt_payloads[claim["claimId"]].encode("utf-8")
        )
    return candidate, packet, source_payloads, excerpt_payloads


def _gate(report, gate_id: str):
    return next(item for item in report.validation_gates if item.gate_id == gate_id)


def test_no_verification_payload_stays_unknown_and_locked() -> None:
    candidate, packet, _, _ = _evidence()

    report = SbcTimingProfileSourceVerificationCompiler().compile(
        candidate,
        packet,
    )

    assert report.verification_status == NO_VERIFICATION_PAYLOAD
    assert report.s1_ready_for_external_review is True
    assert _gate(report, "s1_packet_readiness").state == PASS_STATE
    assert _gate(report, "exact_source_bytes").state == UNKNOWN_STATE
    assert _gate(report, "exact_excerpt_payloads").state == UNKNOWN_STATE
    assert report.ready_for_independent_review is False
    assert report.review_bundle is None
    assert report.source_certified is False
    assert report.guardrails["execution_allowed"] is False


def test_exact_payloads_build_non_certifying_independent_review_bundle() -> None:
    candidate, packet, source_payloads, excerpt_payloads = _evidence()

    report = SbcTimingProfileSourceVerificationCompiler().compile(
        candidate,
        packet,
        source_payloads,
        excerpt_payloads,
    )

    assert report.verification_status == READY_FOR_INDEPENDENT_REVIEW
    assert report.all_source_bytes_verified is True
    assert report.all_excerpt_payloads_verified is True
    assert report.ready_for_independent_review is True
    assert all(
        item.verification_state == PASS_STATE
        for item in report.source_artifact_checks
    )
    assert all(
        item.verification_state == PASS_STATE
        for item in report.excerpt_payload_checks
    )
    assert report.review_bundle is not None
    assert report.review_bundle_sha256 is not None
    assert (
        report.review_bundle["verification"]["reviewBundleHashMethod"]
        == REVIEW_BUNDLE_HASH_METHOD
    )
    assert (
        report.review_bundle["attestationTemplate"]["bundleSha256"]
        == report.review_bundle_sha256
    )
    assert (
        independent_review_bundle_hash(report.review_bundle)
        == report.review_bundle_sha256
    )
    assert report.external_review_completed is False
    assert report.source_certified is False
    assert report.profile_registration_allowed is False


def test_source_byte_mismatch_fails_closed() -> None:
    candidate, packet, source_payloads, excerpt_payloads = _evidence()
    source_payloads["primary-doctrine"] = b"different bytes"

    report = SbcTimingProfileSourceVerificationCompiler().compile(
        candidate,
        packet,
        source_payloads,
        excerpt_payloads,
    )

    assert report.verification_status == SOURCE_VERIFICATION_FAILED
    assert _gate(report, "exact_source_bytes").state == FAIL_STATE
    row = next(
        item
        for item in report.source_artifact_checks
        if item.source_id == "primary-doctrine"
    )
    assert row.verification_state == FAIL_STATE
    assert report.ready_for_independent_review is False
    assert report.review_bundle is None


def test_excerpt_payload_mismatch_fails_closed() -> None:
    candidate, packet, source_payloads, excerpt_payloads = _evidence()
    first_claim_id = packet["claims"][0]["claimId"]
    excerpt_payloads[first_claim_id] += " changed"

    report = SbcTimingProfileSourceVerificationCompiler().compile(
        candidate,
        packet,
        source_payloads,
        excerpt_payloads,
    )

    assert report.verification_status == SOURCE_VERIFICATION_FAILED
    assert _gate(report, "exact_excerpt_payloads").state == FAIL_STATE
    row = next(
        item
        for item in report.excerpt_payload_checks
        if item.claim_id == first_claim_id
    )
    assert row.verification_state == FAIL_STATE
    assert report.review_bundle is None


def test_missing_and_unexpected_identifiers_block_bundle() -> None:
    candidate, packet, source_payloads, excerpt_payloads = _evidence()
    source_payloads.pop("independent-witness")
    source_payloads["undeclared-source"] = b"not declared"
    excerpt_payloads["undeclared-claim"] = "not declared"

    report = SbcTimingProfileSourceVerificationCompiler().compile(
        candidate,
        packet,
        source_payloads,
        excerpt_payloads,
    )

    source_gate = _gate(report, "exact_source_bytes")
    excerpt_gate = _gate(report, "exact_excerpt_payloads")
    assert source_gate.state == FAIL_STATE
    assert "independent-witness" in source_gate.missing_ids
    assert "unexpected:undeclared-source" in source_gate.missing_ids
    assert excerpt_gate.state == FAIL_STATE
    assert "unexpected:undeclared-claim" in excerpt_gate.missing_ids
    assert report.ready_for_independent_review is False


def test_s1_failure_blocks_s2_even_when_payload_hashes_match_packet() -> None:
    candidate, packet, source_payloads, excerpt_payloads = _evidence()
    packet["profileHash"] = "9" * 64

    report = SbcTimingProfileSourceVerificationCompiler().compile(
        candidate,
        packet,
        source_payloads,
        excerpt_payloads,
    )

    assert _gate(report, "s1_packet_readiness").state == FAIL_STATE
    assert report.s1_ready_for_external_review is False
    assert report.ready_for_independent_review is False
    assert report.review_bundle is None


def test_empty_or_wrong_payload_types_fail_exact_verification() -> None:
    candidate, packet, source_payloads, excerpt_payloads = _evidence()
    source_payloads["primary-doctrine"] = b""
    excerpt_payloads[packet["claims"][0]["claimId"]] = ""

    report = SbcTimingProfileSourceVerificationCompiler().compile(
        candidate,
        packet,
        source_payloads,
        excerpt_payloads,
    )

    assert _gate(report, "exact_source_bytes").state == FAIL_STATE
    assert _gate(report, "exact_excerpt_payloads").state == FAIL_STATE
    assert report.ready_for_independent_review is False


def test_export_never_contains_raw_source_bytes_or_excerpt_text() -> None:
    candidate, packet, source_payloads, excerpt_payloads = _evidence()

    report = SbcTimingProfileSourceVerificationCompiler().compile(
        candidate,
        packet,
        source_payloads,
        excerpt_payloads,
    )

    serialized = json.dumps(report.review_bundle, sort_keys=True)
    for payload in source_payloads.values():
        assert payload.decode("utf-8") not in serialized
    for payload in excerpt_payloads.values():
        assert payload not in serialized
    assert report.review_bundle["guardrails"]["sourceBytesIncluded"] is False
    assert report.review_bundle["guardrails"]["excerptTextIncluded"] is False
    assert report.review_bundle["guardrails"]["executionAllowed"] is False


def test_missing_candidate_and_packet_cannot_imply_readiness() -> None:
    report = SbcTimingProfileSourceVerificationCompiler().compile(None, None)

    assert report.verification_status == NO_VERIFICATION_PAYLOAD
    assert _gate(report, "s1_packet_readiness").state == UNKNOWN_STATE
    assert _gate(report, "exact_source_bytes").state == UNKNOWN_STATE
    assert _gate(report, "exact_excerpt_payloads").state == UNKNOWN_STATE
    assert report.ready_for_independent_review is False
    assert report.review_bundle is None
