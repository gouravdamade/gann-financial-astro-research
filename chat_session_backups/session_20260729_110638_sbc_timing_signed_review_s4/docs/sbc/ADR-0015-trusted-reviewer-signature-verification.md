# ADR-0015: Trusted Reviewer Signature Verification

Date: 2026-07-29

Status: Accepted for S4 implementation

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

## Context

S3 verifies that an external-review record is internally coherent and exactly
covers the frozen S2 bundle. It cannot authenticate the named reviewer.
Accepting a public key from the same client payload would prove only that an
unknown key signed the payload, so it would not close that gap.

## Decision

Implement a fail-closed S4 verifier with these boundaries:

1. Re-run S3 from the supplied S2 review bundle and completed attestation.
2. Accept a separate signed-review envelope using Ed25519.
3. Resolve the public key only from the server-owned
   `status/timing_profile_reviewer_trust_registry.json`.
4. Never accept a client-supplied public key or client-supplied registry.
5. Require the key ID to be the uppercase SHA-256 digest of the raw 32-byte
   Ed25519 public key.
6. Require a non-revoked registry entry whose validity interval contains the
   signing time and whose exact profile and source-packet scope includes the
   reviewed record.
7. Require reviewer identity and organization to match the S3 attestation,
   signed envelope, and trusted registry entry exactly.
8. Bind the signature to the exact review bundle, attestation, certification
   proposal, profile, and source packet hashes.
9. Sign canonical JSON after blanking only `signatureBase64`.
10. Treat registry independence vetting as an administrator assertion, not a
    cryptographic proof of independence.
11. A passing S4 record may report only
    `READY_FOR_MANUAL_SOURCE_CERTIFICATION`.
12. S4 must not create a source certificate, register a timing profile, write
    either canonical registry, calculate direction or confidence, affect ML
    evidence or Auto Suggest, place a trade, or enable MT5.

## Consequences

- S4 can prove that a server-trusted reviewer key signed the exact approved S3
  evidence and that the key was valid, scoped, and not revoked at signing time.
- S4 cannot prove that the human controlled the key, was genuinely independent,
  reviewed the cited pages correctly, or reached a doctrinally correct result.
- The shipped reviewer trust registry remains empty. A real reviewer key must
  be vetted and added through a separate, human-reviewed Git change.
- Source certification and timing-profile registration remain blocked.
