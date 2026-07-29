# ADR-0014: External-Review Attestation Verification

Date: 2026-07-29

Status: Accepted for S3 implementation

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

## Context

T0 validates candidate structure and admits only hashes already present in a
server-owned certified registry. S1 validates the declarative source packet.
S2 verifies exact locally supplied source and excerpt bytes and emits a
non-certifying independent-review bundle.

S2 deliberately leaves a blank attestation template. Loading a completed JSON
attestation cannot by itself authenticate a reviewer, prove independence,
certify doctrine, or authorize a registry write.

## Decision

Implement a fail-closed S3 verifier with these boundaries:

1. Accept one S2 independent-review bundle and one separately supplied
   completed attestation.
2. Reproduce the S2 bundle digest using
   `CANONICAL_JSON_SHA256_WITH_ATTESTATION_BUNDLE_HASH_BLANK`.
3. Re-run S1 readiness on the embedded candidate and source packet.
4. Verify that every S2 source and excerpt check is internally complete,
   uniquely identified, digest-consistent, and `PASS`.
5. Require the attestation contract
   `SBC_TIMING_PROFILE_EXTERNAL_REVIEW_ATTESTATION_V1`, schema `1`.
6. Require an exact bundle digest link, non-empty reviewer identity,
   organization, UTC timestamp, overall note, and explicit independence
   confirmation.
7. Require exactly one non-pending `PASS` or `FAIL` decision with a note for
   every source, claim, and registered conflict.
8. An `APPROVED` attestation must contain only `PASS` decisions. A `REJECTED`
   attestation must contain at least one `FAIL`.
9. A complete approved attestation may emit only
   `READY_FOR_HUMAN_CERTIFICATION_DECISION` and a reproducibly hashed
   `SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_PROPOSAL_V1`.
10. The proposal records reviewer claims and deterministic evidence links, but
    keeps `sourceCertified=false`, `registryWriteAllowed=false`,
    `profileRegistered=false`, and `executionAllowed=false`.
11. The application must not write `status/source_certification.json` or
    `status/timing_phase_profile_registry.json`.
12. Reviewer identity authentication, signature verification, genuine
    independence, page truth, doctrinal correctness, final certification,
    registry admission, prospective validation, inference, trading, and
    execution remain separate gates.

## Consequences

- S3 can detect incomplete, inconsistent, mismatched, or tampered review
  records.
- S3 cannot prove that the named reviewer exists or performed the review.
- A proposal is a review aid for a controlled human Git change, not a source
  certificate or registry entry.
- Directional contribution remains exactly zero.
