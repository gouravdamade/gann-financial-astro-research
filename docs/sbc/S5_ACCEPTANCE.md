# S5 Acceptance: Source Certification Authority

S5 passes only when all of the following are true:

1. The report contract is
   `SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_REPORT_V1`, schema `1`.
2. S4 is rerun and reports `READY_FOR_MANUAL_SOURCE_CERTIFICATION`.
3. The certificate contract is
   `SBC_TIMING_PROFILE_SOURCE_CERTIFICATE_V1`, schema `1`.
4. The policy is `ED25519_SEPARATE_AUTHORITY_EXACT_S4_BINDING_V1`.
5. The authority registry is server-owned, schema `1`, read-only, and
   execution-locked.
6. The client cannot supply a public key or authority registry.
7. Authority key IDs equal the SHA-256 of the raw 32-byte Ed25519 public key.
8. The authority key is present, valid, non-revoked, and exactly scoped to the
   profile and source packet.
9. Authority identity and organization match the trusted registry.
10. Separation of duties is administratively vetted.
11. Authority key ID and identity differ from the S4 reviewer.
12. The certificate binds the exact S1, S2, S3, and S4 evidence hashes.
13. The decision is `CERTIFIED` or `REJECTED` and has a non-empty note.
14. `certifiedAtUtc` is not earlier than the signed S4 review.
15. Profile registration, registry writes, and execution remain false.
16. Canonical JSON blanks only `signatureBase64` for Ed25519 verification.
17. A valid rejection reports `SOURCE_CERTIFICATION_REJECTED`.
18. A valid certification reports
    `READY_FOR_PROFILE_REGISTRY_ADMISSION`.
19. A passing certification emits only a reproducibly hashed registry-entry
    proposal for separate human Git review.
20. The application cannot apply that proposal.
21. No timing phase, direction, confidence, ML evidence, Auto Suggest result,
    trade, or order is produced.
22. Core, service, frontend, Rust, status, endpoint, and live-UI verification
    pass.
