# S4 Acceptance: Trusted Reviewer Signature

S4 passes only when all of the following are true:

1. The report contract is
   `SBC_TIMING_PROFILE_SIGNED_REVIEW_REPORT_V1`, schema `1`.
2. S3 is rerun from the supplied bundle and attestation and reports
   `READY_FOR_HUMAN_CERTIFICATION_DECISION`.
3. The signed-review envelope contract is
   `SBC_TIMING_PROFILE_SIGNED_REVIEW_V1`, schema `1`.
4. The signature policy is
   `ED25519_SERVER_TRUST_REGISTRY_EXACT_S3_BINDING_V1`.
5. The server-owned reviewer registry contract is
   `SBC_TIMING_PROFILE_REVIEWER_TRUST_REGISTRY_V1`, schema `1`.
6. The repository registry keeps `registryWriteAllowed=false` and
   `executionAllowed=false`.
7. Every reviewer key ID is the SHA-256 digest of its raw Ed25519 public key.
8. Reviewer registry key IDs are unique.
9. The signed key is present, non-revoked, and valid at `signedAtUtc`.
10. The registry scope includes the exact profile ID and source packet ID.
11. Reviewer identity and organization match the S3 attestation, envelope, and
    registry entry exactly.
12. The envelope links the exact review bundle, attestation, proposal, profile,
    and source packet hashes produced by S3.
13. `reviewedAtUtc` matches the S3 attestation and `signedAtUtc` is not earlier.
14. `reviewerIndependenceConfirmed=true`.
15. `sourceCertified=false`, `registryWriteAllowed=false`, and
    `executionAllowed=false` in the envelope.
16. Canonical JSON blanks only `signatureBase64` before Ed25519 verification.
17. The public key comes only from the server registry.
18. Missing input reports `NO_SIGNED_REVIEW`.
19. A non-ready S3 record reports `S3_NOT_READY`.
20. An absent, expired, revoked, or out-of-scope key reports
    `REVIEWER_KEY_UNTRUSTED`.
21. A malformed, mismatched, or cryptographically invalid record reports
    `SIGNATURE_INVALID`.
22. A complete passing record reports
    `READY_FOR_MANUAL_SOURCE_CERTIFICATION`.
23. A passing report authenticates only the signature-to-registry binding. It
    does not independently prove reviewer independence or doctrinal truth.
24. The verifier cannot certify source doctrine, register a profile, write a
    registry, affect inference, emit an ML note, produce a trade, or enable
    execution.
25. Core, service, frontend, Rust, status, endpoint, and live-UI verification
    pass.

Passing S4 means only that a registered reviewer key signed the exact approved
S3 evidence and that a separate human source-certification decision may begin.
