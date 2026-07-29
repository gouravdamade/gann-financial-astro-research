# ADR-0013: Source-Byte Verification and Independent-Review Bundle

Date: 2026-07-29

Status: Accepted for S2

## Context

T0 defines a complete, fail-closed timing-profile candidate contract and checks
admission only against a server-owned certified registry. S1 binds that
candidate to a frozen, page-cited source packet and verifies that every
doctrine domain has a primary source plus an independently declared witness
lineage. S1 deliberately checks declarations and hashes only; it never reads
the declared source bytes.

An independent reviewer needs one reproducible handoff that proves the locally
selected files and excerpt payloads match those declarations. Treating a
matching file hash as page verification or doctrine certification would still
be unsafe. S2 therefore separates byte identity from human review.

## Decision

1. Add deterministic contract
   `SBC_TIMING_PROFILE_SOURCE_BYTE_VERIFICATION_REPORT_V1`.
2. Use policy `EXACT_SOURCE_BYTES_AND_UTF8_EXCERPT_PAYLOADS_V1`.
3. Require the candidate and packet to pass every S1 readiness gate.
4. Hash each selected source with SHA-256 over the exact supplied bytes.
5. Hash each claim excerpt with SHA-256 over exact UTF-8 bytes with no
   whitespace, Unicode, or line-ending normalization.
6. Require the supplied source IDs and claim IDs to equal the packet sets
   exactly. Missing, extra, empty, malformed, or mismatched payloads fail.
7. Keep raw source bytes and excerpt text in memory only. They are never
   written by S2 and never included in an exported bundle.
8. When all exact hashes pass, build deterministic contract
   `SBC_TIMING_PROFILE_INDEPENDENT_REVIEW_BUNDLE_V1`.
9. The bundle contains the candidate, frozen S1 packet, hash-check rows,
   external-review instructions, and a blank
   `SBC_TIMING_PROFILE_EXTERNAL_REVIEW_ATTESTATION_V1` template.
10. The bundle hash is canonical JSON SHA-256 with the attestation template's
    `bundleSha256` field blank. The field is then populated with that digest so
    a reviewer can reproduce the identity without a self-referential hash.
11. A successful result is `READY_FOR_INDEPENDENT_REVIEW`. It is not completed
    review, page verification, doctrine correctness, source certification,
    profile registration, financial validation, or execution permission.
12. The application accepts only bytes supplied explicitly by the user. S2
    does not read arbitrary filesystem paths.
13. Private backend and native transports remain read-only and reject any
    runtime with execution enabled.

## Consequences

- A reviewer can receive one deterministic, non-redistributing JSON package
  and independently acquire or inspect the identified source editions.
- File identity, excerpt-payload identity, visual page presence, doctrinal
  support, reviewer independence, registry admission, engine implementation,
  prospective validation, and execution remain separate gates.
- S2 cannot populate or modify
  `status/timing_phase_profile_registry.json`.
- S2 contributes zero market direction and cannot feed Auto Suggest, local
  LLM drafts, official ML notes, live inference, trade output, or MT5.
