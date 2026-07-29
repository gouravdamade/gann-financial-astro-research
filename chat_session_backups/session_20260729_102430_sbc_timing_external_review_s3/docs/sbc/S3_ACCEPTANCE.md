# S3 Acceptance: Review Attestation and Certification Proposal

S3 passes only when all of the following are true:

1. The report contract is
   `SBC_TIMING_PROFILE_EXTERNAL_REVIEW_REPORT_V1`, schema `1`.
2. The supplied bundle contract is
   `SBC_TIMING_PROFILE_INDEPENDENT_REVIEW_BUNDLE_V1`, schema `1`.
3. Its canonical digest reproduces after blanking only
   `attestationTemplate.bundleSha256`.
4. The embedded candidate and source packet still pass S1.
5. Every declared source has one unique S2 check row whose expected and
   observed SHA-256 values match the packet and whose state is `PASS`.
6. Every declared claim has one unique S2 excerpt row whose expected and
   observed SHA-256 values, source, profile path, and page range match the
   packet and whose state is `PASS`.
7. Bundle guardrails still exclude source bytes and excerpt text and keep page
   truth, doctrine review, certification, registry writes, direction, and
   execution false.
8. The attestation contract is
   `SBC_TIMING_PROFILE_EXTERNAL_REVIEW_ATTESTATION_V1`, schema `1`.
9. The attestation links the exact bundle digest.
10. Reviewer identity, organization, UTC review time, and overall note are
    non-empty, and independence is explicitly confirmed.
11. The source, claim, and conflict decision arrays contain exactly the
    required IDs with no duplicates, omissions, or extras.
12. Every decision is final `PASS` or `FAIL` and has a non-empty note.
13. `APPROVED` requires every decision to pass. `REJECTED` requires at least
    one failed decision.
14. `registryWriteAllowed` in the attestation remains false.
15. Missing input reports `NO_ATTESTATION`.
16. Invalid or inconsistent evidence reports `ATTESTATION_INVALID`.
17. A valid rejection reports `REVIEW_REJECTED` and emits no proposal.
18. A valid approval reports `READY_FOR_HUMAN_CERTIFICATION_DECISION`.
19. The proposal contract is
    `SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_PROPOSAL_V1`, schema `1`, with a
    reproducible canonical digest.
20. The proposal contains no source bytes or excerpt text.
21. The report and proposal state that reviewer identity is not authenticated,
    external review is not independently proven, source is not certified, the
    profile is not registered, and registry writes are not allowed.
22. The backend accepts JSON objects only and never reads arbitrary
    client-supplied paths.
23. S3 never affects timing phase, direction, confidence, ML evidence,
    Auto Suggest, live inference, shadow votes, trade output, or MT5.
24. Core, service, frontend, Rust, status, endpoint, and live-UI verification
    pass.

Passing S3 means only that a self-contained review record is internally
complete and ready for a separate human certification decision.
