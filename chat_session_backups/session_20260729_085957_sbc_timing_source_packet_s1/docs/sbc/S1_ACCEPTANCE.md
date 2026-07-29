# S1 Timing-Profile Source-Packet Readiness Acceptance

Date: 2026-07-29

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

## Required Contract

- Packet: `SBC_TIMING_PROFILE_SOURCE_PACKET_V1`
- Readiness report: `SBC_TIMING_PROFILE_SOURCE_READINESS_REPORT_V1`
- Candidate profile: `SBC_DIRECTIONAL_TIMING_PROFILE_V1`
- Readiness policy: `CLAIM_HASH_AND_INDEPENDENT_LINEAGE_READINESS_V1`
- Schema version: `1`

## Acceptance Checks

1. With no candidate or packet loaded, dependent gates and coverage rows are
   `UNKNOWN`, not zero and not a pass.
2. Candidate and packet JSON are evaluated in memory and never persisted.
3. Unknown candidate or packet fields fail closed.
4. The candidate must pass every T0 structural gate.
5. Packet ID, version, classification, frozen state, author, and UTC
   preparation timestamp are explicit.
6. Packet profile ID, version, and canonical SHA-256 match the exact candidate.
7. Every packet source artifact matches one candidate `sourceEvidence`
   artifact by source ID and SHA-256; omitted and unused declarations fail.
8. Every claim binds one exact candidate subtree by canonical SHA-256.
9. Every claim includes a declared source, page range, citation, evidence
   role, excerpt SHA-256, and note.
10. Every doctrine domain has a primary-source claim and an
    independent-witness claim across at least two declared lineages.
11. `eligibilityPolicy` and `confidencePolicy` each have a frozen
    research-specification claim.
12. Research thresholds are never presented as inherited doctrine.
13. The conflict register has no unresolved entries. Resolutions identify a
    chosen declared source and include justification.
14. The review request requires a reviewer external to the profile author and
    the exact source identity, page citation, claim-value binding, independent
    lineage, and conflict-resolution scope.
15. `READY_FOR_EXTERNAL_REVIEW` means packet completeness only.
16. S1 never claims source-byte verification, completed external review,
    source certification, profile registration, or registry-write permission.
17. S1 never calculates timing phase, direction, confidence, an independent
    vote, an official ML note, a trade result, or broker execution.

## UI Acceptance

- `Source packet` is available without compiling a linked audit.
- The initial view says no source packet is loaded.
- A source packet can be loaded only after a candidate is loaded through
  `Timing gate`.
- Candidate and packet filenames and hashes are visible when present.
- Candidate structure, packet structure, coverage, witness lineages,
  conflicts, external-review state, and certification lock are separate.
- Every profile domain shows its claim class, coverage state, role counts, and
  lineage count.
- Every gate displays `PASS`, `FAIL`, or `UNKNOWN` with its reason.
- The UI plainly says it does not inspect source bytes, certify doctrine,
  register a profile, calculate direction, or enable trading.
- No layout overlap or error-level browser log appears at the desktop
  acceptance viewport.

## Release Boundary

S1 is source-only. It does not rebuild Windows or Android packages, inspect
book bytes, perform external review, certify sources, write the registry,
implement T1, modify inference, or change execution permissions.
