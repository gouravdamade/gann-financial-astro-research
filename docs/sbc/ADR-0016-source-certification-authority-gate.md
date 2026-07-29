# ADR-0016: Source-Certification Authority Gate

Date: 2026-07-29

Status: Accepted for S5 implementation

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

## Context

S4 can authenticate that a server-trusted reviewer key signed the exact S3
evidence. It deliberately stops before source certification. Letting the same
review key certify its own review, accepting an authority key from the client,
or letting the application write the timing-profile registry would collapse
the separation between review, certification, and admission.

## Decision

1. Re-run S4 from the supplied bundle, attestation, and signed review.
2. Accept a separate Ed25519 source-certificate envelope.
3. Resolve the certification-authority public key only from the server-owned
   `status/timing_profile_certification_authority_registry.json`.
4. Never accept a client-supplied authority key or authority registry.
5. Require the authority key and authority identity to differ from the S4
   reviewer key and reviewer identity.
6. Require an administrator-vetted separation-of-duties assertion, exact
   profile and source-packet scope, a valid signing interval, and no revocation.
7. Bind the certificate to the exact S4 review bundle, attestation, S3
   proposal, signed-review envelope, candidate profile, source packet, and
   source-audit references.
8. Permit signed decisions `CERTIFIED` and `REJECTED`. Both require a note.
9. Sign canonical JSON after blanking only `signatureBase64`.
10. A passing `CERTIFIED` record may report
    `READY_FOR_PROFILE_REGISTRY_ADMISSION` and emit a reproducible registry
    entry proposal.
11. The proposal is not a registry entry. It requires a separate human Git
    review and cannot be applied by the application.
12. A passing certificate records a governance decision. It does not
    cryptographically prove doctrinal truth or reviewer independence.
13. S5 must not write either trust registry, register a timing profile,
    implement the directional engine, affect inference or ML evidence, place a
    trade, or enable MT5.

## Consequences

- Review authentication and source certification use distinct trusted keys.
- A source-certified record can be reproduced without giving the client
  authority over trust roots.
- The shipped certification-authority registry remains empty.
- Timing-profile admission, directional implementation, prospective financial
  validation, and execution remain separate later gates.
