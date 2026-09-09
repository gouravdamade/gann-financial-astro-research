# MO-R3-R2-F1 Windows Founder Integrity Candidate

## Status

`FOUNDER_REVIEW_COLLECTION_READY`

This is a candidate for physical founder integrity inspection. It is not a
founder acceptance record and is not a `GO` decision.

The bounded milestone is `MO-R3-R2`: record-integrity hardening for the
already accepted Fields Founder Review workflow. No decision was created for
the real April 2025 packets during implementation, testing, packaging, or
the packaged probe.

## Candidate

- Version: `0.10.63-pfr-v2b-mo-r3-r2-f1`
- Milestone: `MO-R3-R2-F1`
- Implementation source commit:
  `882f3f4a07eef6824d3b21ffbec0be74964faf57`
- Packaging checkout commit:
  `882f3f4a07eef6824d3b21ffbec0be74964faf57`
- `sourceGitDirty`: `false`
- `executionAllowed`: `false`
- Build receipt contract: `GANN_ASTRO_WINDOWS_BUILD_RECEIPT_V1`
- Immutable resource-tree scope: `candidate/backend`
- Mutable application-data founder-review store: excluded and unhashed

Portable executable:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.63-pfr-v2b-mo-r3-r2-f1-tauri\GannAstroDesk.exe`

Portable SHA-256:

`ABFD532DA6EAF01BA644BCF12374EF492A26B32A88E0719269BEC8781CD96908`

Installer:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.63-pfr-v2b-mo-r3-r2-f1-tauri\Gann Astro Desk_0.10.63-pfr-v2b-mo-r3-r2-f1_x64-setup.exe`

Installer SHA-256:

`82197273791FF26A986AF8C0E59224F4A871B2A8307D42D6F31DD48B90AD1B05`

Other release hashes:

- Sidecar: `B03F24012301787CB9FF676E5F02B147532802ECA403306FBA28F26F84690058`
- `build.receipt.json`: `7F4CEB9EF9EC3268FAC96D8E461835236B918805F68900D75101A8EA86187776`
- `release.manifest.json`: `D990242B051E7DFF9B094806510B9D0F02C23158C34144D7DE9A3B1D7404FFAA`
- Immutable sidecar resource tree: `C025E380552E4CF326E474EA491521B15CFC5231C8EBF153971C24504F8F9D9D`

The existing accepted `0.10.61` and `0.10.62` candidate directories were not
overwritten.

## Source And Review Integrity

The candidate reads the canonical blank packets, identity-integrity manifests,
and the auxiliary identity audit as immutable resources. Mutable state is
stored under the configured application-data root:

```text
<application-data-root>/founder_review/current/<side>.json
<application-data-root>/founder_review/revisions/<side>/<revision-id>/
```

The first write creates a complete revision and atomically publishes its
current pointer. Later writes append a new revision with
`previousRevisionHash`; stale clients receive a structured conflict and never
overwrite a newer revision. Omitted rows retain their authoritative state and
all source references survive an edit. Server-created UTC timestamps are the
authoritative chronology.

The exact eight mandatory identity-audit checks are present, Boolean, and
exactly `true` before a row is review-eligible. Missing, extra, null,
non-Boolean, false, mismatched, unresolved, or boundary-failed identity data
fails closed.

## Real Identity-Only Probe

The actual portable executable was launched with an isolated application-data
root and queried through its real sidecar. The response was:

- HTTP `200`;
- `Content-Type: application/json`;
- endpoint `/api/founder-review/workbench`;
- 12 USD rows and 12 JPY rows;
- all 24 eligible and `SINGLE_PASS_VERIFIED`;
- zero decisions;
- zero evidence classifications;
- zero source references;
- zero durable revision files;
- blank packet and identity-manifest hashes unchanged;
- `executionAllowed=false`.

The response body prefix began with a JSON object (`{"ok":true,"workbench":`),
not HTML. No real row was exported, rejected, or classified.

## Automated Verification

Focused integrity and packaging checks:

- `19/19` synthetic Founder Review workbench tests passed.
- `9/9` desktop packaging/runtime checks passed.
- Combined focused result: `28/28` passed.

The synthetic checks cover blank initial state, immutable resource preservation,
durable save/restart/version replacement, append-only revision history,
server chronology, deterministic packet and revision hashes, stale revision
conflicts, atomic publication failure, partial updates, source-reference
preservation, exact classical locators, deliberate unknowns, strict input
types, mandatory audit booleans, manifest and packet binding, and product
guardrails.

Repository regressions and quality checks:

- Backend: `331 passed, 1 skipped`.
- Frontend: `43 test files, 197 tests passed`.
- Focused frontend Founder Review: `4/4` passed.
- Oxlint: passed.
- Production frontend build: passed; `1878` modules transformed.
- `cargo fmt --check`: passed.
- `cargo check`: passed.
- Rust tests: `19 passed`.
- Python compilation: passed for changed backend modules.
- PowerShell packaging-script parse: passed.
- `git diff --check`: passed.

## Packaged Smoke

Two isolated launches of the actual portable candidate passed the established
native soak procedure. Both included:

- app launch and healthy private sidecar;
- normal Chakra/source-profile API checks;
- 81-cell Agarwal source profile and `DEPENDENCY_NOT_READY` Vedha state;
- execution and MT5 read-only locks;
- layout creation and persistence across forced sidecar recovery;
- same-port sidecar recovery;
- clean shutdown;
- zero surviving descendants.

The optional candlestick specialist was safely deferred as not configured. It
was not treated as a review-integrity failure.

Reports:

```text
D:\GannFinancialAstro\soak\tauri_0.10.63-pfr-v2b-mo-r3-r2-f1_20260909_035119\logs\native_soak_report.json
D:\GannFinancialAstro\soak\tauri_0.10.63-pfr-v2b-mo-r3-r2-f1_20260909_040346\logs\native_soak_report.json
```

Both report `passed=true`, zero errors, zero failed checks, and
`execution_allowed=false`.

## Founder Physical Integrity Checklist

1. Launch the portable executable from the candidate directory.
2. Open the existing Fields workspace and choose `Founder Review`.
3. Confirm the surface loads without changing the immutable packet or manifest.
4. Confirm both sides show 12 rows, all `SINGLE_PASS_VERIFIED`, with blank
   decisions, evidence classification, reasoning, and source references.
5. Confirm the visible status shows review state and current revision state;
   no revision should exist before the first save.
6. Confirm the UI makes the review record integrity and immutable source
   bindings inspectable without displaying price, outcomes, SBC, or polarity.
7. Confirm the application-data review store is separate from the candidate's
   bundled resource tree.
8. Do not classify a real April 2025 event during inspection. The save/restart,
   edit, append-only, and stale-client behaviors were proven with synthetic
   identities in the automated suite.
9. Confirm no catalogue admission, signed wave, pair result, score, Auto
   Suggest, ML/LLM interpretation, MT5 order, or execution path appears.
10. Confirm clean close and relaunch retain the blank real-packet state.

## Known Limitations

- This candidate hardens Founder Review persistence and audit integrity; it
  does not create founder decisions.
- Historical bundle-local reviewed projections are not imported into the new
  durable store.
- The optional candlestick specialist remains not configured and was deferred
  by the native smoke harness.
- Physical founder inspection of the integrity behavior is still pending.

## Locked Boundaries

The following remain disabled: price reads for review, outcome reads, SBC
reads, signed waves, pair resultants, polarity assignment, catalogue
admission, magnitude, normalization, smoothing, Auto Suggest, ML/LLM
interpretation, MT5 execution, automatic order placement, and market
direction. `executionAllowed=false`.

Founder review collection is ready for physical integrity inspection, but this
record does not grant founder acceptance or a GO decision.
