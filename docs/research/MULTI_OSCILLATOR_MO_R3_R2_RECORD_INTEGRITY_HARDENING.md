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

The candidate is `0.10.63-pfr-v2b-mo-r3-r2-f1`. It is not a founder
acceptance claim; the build and automated checks are complete, while physical
integrity inspection remains pending.

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

## Candidate And Packaged Proof

The candidate was built from source and packaging checkout commit
`882f3f4a07eef6824d3b21ffbec0be74964faf57`:

```text
D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.63-pfr-v2b-mo-r3-r2-f1-tauri\GannAstroDesk.exe
D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.63-pfr-v2b-mo-r3-r2-f1-tauri\Gann Astro Desk_0.10.63-pfr-v2b-mo-r3-r2-f1_x64-setup.exe
```

Portable SHA-256: `ABFD532DA6EAF01BA644BCF12374EF492A26B32A88E0719269BEC8781CD96908`.
Installer SHA-256: `82197273791FF26A986AF8C0E59224F4A871B2A8307D42D6F31DD48B90AD1B05`.
Sidecar SHA-256: `B03F24012301787CB9FF676E5F02B147532802ECA403306FBA28F26F84690058`.
Build receipt SHA-256: `7F4CEB9EF9EC3268FAC96D8E461835236B918805F68900D75101A8EA86187776`.
Release manifest SHA-256: `D990242B051E7DFF9B094806510B9D0F02C23158C34144D7DE9A3B1D7404FFAA`.
Immutable sidecar resource-tree SHA-256:
`C025E380552E4CF326E474EA491521B15CFC5231C8EBF153971C24504F8F9D9D`.

The receipt declares `sourceGitDirty=false`, `executionAllowed=false`,
`immutableResourceTreeScope=candidate/backend`,
`mutableDataRootExcluded=true`, and `mutableDataTreeHashed=false`. The
candidate contains no private source PDF, PNG, JPG, OCR dump, render, or
release artifact. The normal application seed SQLite file is not founder
review state and is outside the review-store contract.

The real packaged endpoint probe used the actual portable executable and
returned `200 application/json` from `/api/founder-review/workbench`. It
verified 12 USD and 12 JPY rows, all eligible and
`SINGLE_PASS_VERIFIED`, blank decisions/classifications/reasoning/references,
unchanged packet and manifest hashes, zero durable revision files, and
`executionAllowed=false`. The probe did not export or classify any event.

The two isolated native smoke reports are:

```text
D:\GannFinancialAstro\soak\tauri_0.10.63-pfr-v2b-mo-r3-r2-f1_20260909_035119\logs\native_soak_report.json
D:\GannFinancialAstro\soak\tauri_0.10.63-pfr-v2b-mo-r3-r2-f1_20260909_040346\logs\native_soak_report.json
```

Both reports have `passed=true`, zero errors, zero failed checks, healthy
initial and recovered sidecars on the same port, surviving layout state,
`execution_allowed=false`, and zero surviving descendants. The optional
candlestick specialist was reported as not configured and safely deferred.

Synthetic decision-bearing tests are confined to synthetic identities. The
19 workbench tests cover the first save, restart and application-version
replacement, one edit and append-only revision chain, stale-write conflict,
atomic publication failure, partial-row retention, reference preservation,
strict validation, and fail-closed audit cases. No real April event was
classified.

## Locks

This milestone leaves `executionAllowed=false`. No Founder Review decision is
created by the implementation or its tests. No signed USD/JPY/pair wave,
polarity, score, price/outcome read, SBC read, normalization, smoothing,
catalogue admission, ML/LLM interpretation, Auto Suggest, MT5, or execution
path is enabled.
