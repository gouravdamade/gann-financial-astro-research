# MO-R3-R2 Founder Review Record-Integrity Hardening

## Scope

This record documents the bounded repair for the already accepted Fields to
Founder Review workflow. It changes review persistence and session safety only.
It does not change unsigned multi-oscillator mathematics, event identities,
source profiles, Fields calculations, price or outcome handling, SBC, ML, LLM,
Auto Suggest, catalogue admission, or execution.

The historical candidates `0.10.61` and `0.10.62` remain immutable and are not
used as writable state.

## Immutable Inputs

The workbench reads the canonical blank packets, identity-integrity manifests,
and auxiliary identity audit from the packaged project/resource root. Their
bytes are never written by the review service. The normalized packet hashes
remain:

| Side | Blank packet SHA-256 | Identity manifest SHA-256 |
|---|---|---|
| USD | `08DB3837B89866519B7E0B24388537A2064F9EFE059D4FD5E6BCB77F82CA3D76` | `BB0B952B3CC30A91C41D48729139CF2985542C1A64DB1D940D74FFFDBDB2E26E` |
| JPY | `03525A80CD948869F6A8F74A656CB15CB7C11B33E8AC603F5F75628C8CAB8E9B` | `066BDAB7ECC0E8A6AA89E9A28B5A9EAE9B616E225759D3E022C27F185F6CFF8D` |

The accepted identity-audit artifact is bound to contract
`PFR_V2B_R5_F2A_R1_EVENT_IDENTITY_INTEGRITY_AUDIT_V1`, audit version
`chart_conditioned_event_identity_audit_v1_20260806`, and normalized SHA-256
`A869651BA374F5090AEE175877047BC5A945EEC91A6CC3DC419922FDE79F5F82`.

## Durable Review Store

Mutable state uses `FOUNDER_REVIEW_DURABLE_STORE_V1` below the configured
application data root:

```text
<application-data-root>/founder_review/
  current/USD.json
  current/JPY.json
  revisions/USD/<revision-id>/
  revisions/JPY/<revision-id>/
```

`GANN_ASTRO_FOUNDER_REVIEW_ROOT` is set by the runtime environment. It is
separate from the collected resource tree, so read-only packaged resources can
still be reviewed. A current pointer binds one complete immutable revision
directory. Each revision contains the normalized reviewed packet, revision
manifest, completeness report, status record, and Markdown rendering. The
revision hash links to the previous revision hash, and publication uses a
complete temporary directory followed by an atomic pointer replacement.

The service does not import the historical bundle-local reviewed projections.
They remain historical evidence and cannot silently replace a newer durable
revision.

## Integrity Contract

Only rows whose event ID, event hash, exact identity fields, blank packet hash,
identity manifest binding, audit contract/version, and status
`SINGLE_PASS_VERIFIED` all agree are eligible. The mandatory audit checks are
the exact eight-key boolean contract:

```text
acceptedChartIdentityMatches
configuredOrbBoundariesVerified
eventHashReproduces
eventIdMatchesHash
recordedExactMatchesIndependentCandidate
recordedExactOrbIsPassMinimum
residualReachesIntendedExactAngle
strictTimeOrdering
```

Every key must be present, a Boolean, and exactly `true`; missing, extra,
empty, null, non-Boolean, or false values fail closed for that row. Unresolved,
boundary-failed, unverified, or hash-mismatched identities cannot be exported.

The real identity-only inspection remains:

- USD: 12 rows, all `SINGLE_PASS_VERIFIED`;
- JPY: 12 rows, all `SINGLE_PASS_VERIFIED`;
- total: 24 rows;
- founder decisions: 0;
- evidence classifications: 0;
- source references: 0;
- catalogue admissions: 0;
- execution: disabled.

## Revision and Session Rules

The server owns `serverCreatedAtUtc`, `firstReviewedAtUtc`, and
`lastModifiedAtUtc`. A client timestamp is validated as a type but cannot
override server chronology. The client must submit the current revision hash;
stale writes receive a structured `409` conflict and are never last-writer-
wins. Omitted rows merge with the current authoritative revision. Existing
source-reference rows are retained in full.

Dirty Founder Review edits are visible and protected. Refresh, Back to Fields,
and parent workspace navigation cannot silently discard them. The founder must
save, discard, or cancel. While the review surface is open, the existing
outcome-blind shell flag pauses the review-irrelevant polling surfaces.

## Packaging Hardening

The Windows release script refuses an existing candidate directory, selects the
installer by the exact application-version filename, and rejects a dirty
checkout. A `GANN_ASTRO_WINDOWS_BUILD_RECEIPT_V1` binds the functional source
commit, packaging checkout commit, version, portable executable hash, sidecar
hash, installer hash, and immutable sidecar resource-tree hash. The mutable
application-data root is outside that resource-tree digest.

The next candidate is `0.10.63-pfr-v2b-mo-r3-r2-f1`. It is not a founder
acceptance claim; physical integrity inspection remains pending until the
candidate is built and inspected.

## Verification Before Packaging

- Focused durable review and packaging checks: `28/28` after the final focused
  assertion set.
- Full backend regression: `331 passed, 1 skipped`.
- Full frontend: `43 files, 197 passed`.
- Oxlint: passed.
- Production frontend build: passed, `1878` modules transformed.
- Rust `cargo fmt --check`: passed.
- Rust `cargo check`: passed.
- Rust tests: `19 passed`.

The candidate report and handoff will record the final commit, artifact hashes,
synthetic packaged durability proof, and the identity-only real-packet check
after packaging.

## Locks

This milestone leaves `executionAllowed=false`. No Founder Review decision is
created by the implementation or its tests. No signed USD/JPY/pair wave,
polarity, score, price/outcome read, SBC read, normalization, smoothing,
catalogue admission, ML/LLM interpretation, Auto Suggest, MT5, or execution
path is enabled.
