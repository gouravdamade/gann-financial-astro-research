# ADR-0012: Timing-Profile Source-Packet Readiness Gate

Status: accepted for S1 source-packet readiness only

Date: 2026-07-29

## Context

T0 validates the structure of an externally supplied timing profile and checks
its exact hash against a server-owned source-certification registry. The
repository intentionally ships no profile and the registry is empty.

Implementing a directional timing-phase engine before the proposed doctrine
has been traced to page-cited sources, independently witnessed, reconciled,
and reviewed would manufacture authority. Treating a bibliography or an LLM
summary as certification would be equally unsafe. A reproducible packet is
needed before an independent reviewer can assess the candidate.

## Decision

1. Add packet contract `SBC_TIMING_PROFILE_SOURCE_PACKET_V1`, schema `1`, and
   report contract `SBC_TIMING_PROFILE_SOURCE_READINESS_REPORT_V1`, schema
   `1`, under policy
   `CLAIM_HASH_AND_INDEPENDENT_LINEAGE_READINESS_V1`.
2. Keep classification `SOURCE_PROFILED_EXPERIMENTAL`.
3. Evaluate the candidate and packet in memory only. Unknown or missing fields
   fail closed. Neither artifact is persisted.
4. Reuse the T0 checker to require a structurally complete
   `SBC_DIRECTIONAL_TIMING_PROFILE_V1` candidate.
5. Bind the packet to the exact candidate ID, version, and canonical SHA-256.
6. Require packet source declarations to match every candidate
   `sourceEvidence` artifact by ID and SHA-256.
7. Bind each claim to the canonical SHA-256 of one exact candidate subtree.
   Require a source ID, page range, citation, excerpt SHA-256, role, and note.
8. Treat the following as doctrine domains:
   `phaseSpan`, `sectors`, `boundaryPolicy`, `asymmetryPolicy`,
   `repeatedExactEventPolicy`, `retrogradeLoopPolicy`, `stationPolicy`,
   `missingBoundaryPolicy`, and `unsupportedStatePolicy`.
9. Require every doctrine domain to have at least one primary-source claim,
   one independent-witness claim, and at least two declared lineages across
   those claims.
10. Treat `eligibilityPolicy` and `confidencePolicy` as research protocol,
    not inherited doctrine. Require at least one frozen
    research-specification claim for each.
11. Require a complete conflict register. An unresolved source conflict blocks
    readiness. A resolved conflict must name the selected source and include a
    written justification.
12. Require an explicit external review request with reviewer independence
    `EXTERNAL_TO_PROFILE_AUTHOR` and the exact S1 review scope.
13. A fully passing packet may report only
    `READY_FOR_EXTERNAL_REVIEW`. S1 cannot report that external review was
    completed, certify a source, register a profile, or write the registry.
14. S1 verifies JSON declarations and hashes only. It does not read or verify
    the bytes of the declared books, editions, scans, or excerpts.
15. Keep timing phase, direction, confidence, votes, Auto Suggest, live
    inference, official ML notes, shadow validation, trade output, financial
    validation, and MT5 execution absent and blocked.

## Consequences

- A proposed profile can be handed to an independent reviewer as one frozen,
  reproducible evidence packet.
- Missing pages, mismatched hashes, incomplete domains, same-lineage-only
  support, and unresolved disagreements remain visible.
- Structural completeness, packet readiness, external review, source
  certification, registry admission, engine implementation, prospective
  validation, and execution remain separate claims.
- The empty registry and absent directional engine remain truthful.

## Rejected Alternatives

- Certifying a profile because all required JSON fields are present.
- Treating an LLM answer, web summary, or bibliography entry as source proof.
- Allowing a client-supplied `sourceCertified=true` flag.
- Calling the packet source-verified without checking the underlying files.
- Auto-registering a packet that passes S1.
- Reusing doctrine citations as justification for research thresholds.
- Enabling T1, market direction, or trading from source-packet readiness.
