# S2 Acceptance: Exact Source Bytes and Independent-Review Bundle

S2 passes only when all of the following are true:

1. The report contract is
   `SBC_TIMING_PROFILE_SOURCE_BYTE_VERIFICATION_REPORT_V1`, schema `1`.
2. The policy is `EXACT_SOURCE_BYTES_AND_UTF8_EXCERPT_PAYLOADS_V1`.
3. The supplied candidate and source packet pass every S1 readiness gate.
4. Every declared source ID has one non-empty byte payload.
5. Every observed whole-file SHA-256 equals the packet digest.
6. No undeclared source ID is supplied.
7. Every declared claim ID has one non-empty exact UTF-8 excerpt payload.
8. Every observed excerpt SHA-256 equals the claim digest.
9. Excerpt hashing performs no text, Unicode, whitespace, or line-ending
   normalization.
10. No undeclared claim ID is supplied.
11. Missing, extra, malformed, empty, oversized, or mismatched payloads fail
    closed and cannot produce a bundle.
12. A complete pass emits
    `SBC_TIMING_PROFILE_INDEPENDENT_REVIEW_BUNDLE_V1`.
13. The bundle contains the exact candidate and S1 packet, deterministic check
    rows, review instructions, and a blank pending attestation template.
14. The canonical bundle digest is reproducible using
    `CANONICAL_JSON_SHA256_WITH_ATTESTATION_BUNDLE_HASH_BLANK`.
15. Source bytes and excerpt text are absent from the exported bundle.
16. The UI displays selected-file and excerpt-map coverage before verification.
17. The UI separates byte verification, page truth, doctrine review, source
    certification, and execution.
18. The backend accepts explicit base64 source payloads only; it never reads an
    arbitrary client-supplied path.
19. Source payloads are bounded to 64 MiB each and 192 MiB combined. Excerpts
    are bounded to 256 KiB each and 8 MiB combined.
20. S2 never claims visual page presence, doctrinal correctness, external
    review completion, certification, registry-write permission, timing phase,
    direction, confidence, financial value, or execution.
21. Directional contribution remains exactly zero and all downstream
    inference/trading capabilities remain blocked.
22. Core, service, frontend, Rust, status, and live-UI verification pass.

Passing S2 means only that exact locally supplied bytes agree with the frozen
S1 declarations and that a deterministic packet is ready to hand to an
independent reviewer. The reviewer must still inspect the source pages and
judge the claims.
