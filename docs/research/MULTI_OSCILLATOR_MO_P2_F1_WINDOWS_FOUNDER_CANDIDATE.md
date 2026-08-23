# Multi Oscillator MO-P2-F1 Windows Founder Candidate

Status: `BUILT_FOR_FOUNDER_INSPECTION`
Milestone: `MO-P2-F1`
Candidate: `0.10.59-pfr-v2b-mo-p2-f1`
Built: `2026-08-23`

## Source and package identity

- Accepted implementation source: `b1b0f86f3fef49fd7690798d5d77340af01a6695`
- Accepted implementation parent: `7124622167bdfbd4862231509d4db0bcb3ca9a6d`
- Packaging metadata commit used for the build: `2b273b077d9dcf910d3198986da8c16f62d3d3d3`
- Packaging metadata parent: `a176eef32e960a907609e73a4ac4f57a4814c0cd`
- `origin/master` at verification: `b1b0f86f3fef49fd7690798d5d77340af01a6695`
- Source worktree used for packaging: clean; `source_git_dirty=false`
- Platform: Windows x64
- Package build was local; no hosted CI claim is made.

The package contains the accepted MO-P2-R1A runtime. No MO-P3 work, signed
oscillator, magnitude model, smoothing, interpolation, price/outcome read,
SBC fusion, CGVO input, Auto Suggest, LLM, ML, MT5 or execution change was
introduced.

## Artifacts and hashes

Release directory:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.59-pfr-v2b-mo-p2-f1-tauri`

- Portable: `GannAstroDesk.exe`
  - SHA-256: `510688C9A4619923209F45DD3ADAA84DAA67EAAD4934719D44F97332C3DD4B30`
- Installer: `Gann Astro Desk_0.10.59-pfr-v2b-mo-p2-f1_x64-setup.exe`
  - SHA-256: `C2DA7715B62F15B646CFF9D8E45899492703CCA4093A5458B0F43EA4B4BFF5F6`
- Manifest: `release.manifest.json`
  - SHA-256: `BB7A436C0A1A3129994D1048E19E219BE97998EDCD6B9EF26400D70EB7CB9D82`
- Packaged sidecar: `backend\GannAstroBackend.exe`
  - SHA-256: `5C7853DA6AC0DDED53AB1F85E4A00803C3BA1A1D4A9A67F8F310BC1E478DDE4B`

`release.manifest.json` records both `implementationSourceCommit` and
`packagingCommit`, the exact artifact paths, `sourceGitDirty=false`, and
`executionAllowed=false`. `SHA256SUMS.txt` records the same hashes.

## Verification

- `npm ci --no-audit --no-fund`: passed.
- Full frontend: `npx vitest run --pool=threads --maxWorkers=1`, 42 files,
  184 tests passed.
- Full backend: `python -m unittest discover -s backend -p "test_*.py"`,
  319 passed, 1 skipped.
- Oxlint: `npm run lint`, passed.
- Production frontend build: `npm run build`, passed. The existing large
  chunk-size warning remains informational.
- Rust: `cargo fmt --check`, `cargo check`, and `cargo test` passed; 19 Rust
  tests passed.
- `git diff --check`: passed before packaging.

The first combined frontend invocation encountered the known Windows Vitest
worker-start anomaly without assertion failures. The required single-worker
rerun above is the authoritative full frontend result.

## Packaged runtime smoke

Two isolated portable smoke runs passed using
`packaging\soak_tauri_release.ps1`:

1. Report: `D:\GannFinancialAstro\soak\tauri_0.10.59-pfr-v2b-mo-p2-f1_20260823_084322\logs\native_soak_report.json`
2. Report: `D:\GannFinancialAstro\soak\tauri_0.10.59-pfr-v2b-mo-p2-f1_20260823_084520\logs\native_soak_report.json`

Both verified app launch, healthy sidecar, same-port sidecar recovery, layout
survival, read-only MT5 state, execution locks, and clean descendant shutdown.
The optional candlestick specialist remained correctly deferred as
`NOT_CONFIGURED_OPTIONAL`.

## Packaged JSON probe

The real portable executable was launched and its managed sidecar was probed
through the private loopback route with the actual runtime token mechanism.
Probe evidence:

`D:\GannFinancialAstro\probe\mo_p2_f1_14d_20260823_085045\logs\mo_p2_f1_packaged_activity_probe_14d.json`

Request:

- `POST /api/multi-oscillator/activity-range`
- `2025-04-01T00:00:00Z` through `2025-04-15T00:00:00Z`
- side identities `USD`, `JPY`
- aspect profile `ASPECT_STRENGTH_V0`

Result:

- HTTP `200`, `Content-Type: application/json`, JSON parse passed.
- No `<!doctype html>`, HTML fallback, malformed response, or blank route was
  observed.
- Contract: `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`.
- Schema: `2`.
- Evidence mode: `EXPLORATORY_UNSIGNED`.
- Contribution contract: `MO_ACTIVITY_CONTRIBUTION_V1`.
- USD: 57 eligible, 32 rejected, 3 relevant rejects, 29 irrelevant rejects,
  coverage `UNKNOWN`.
- JPY: 59 eligible, 14 rejected, 0 relevant rejects, 14 irrelevant rejects,
  coverage `KNOWN`.
- Guardrails: read-only/unsigned/non-predictive; polarity, magnitude, price,
  outcome, SBC, pair difference, normalization, smoothing, LLM and automatic
  order placement all false; `executionAllowed=false`.

A supplemental one-month packaged probe also parsed as JSON and passed, but
the 14-day probe above is the authoritative comparison against the accepted
smoke reference.

## Founder inspection checklist

Open the portable candidate and navigate to `Fields` -> `Multi Oscillator /
Event Activity`.

1. Confirm USD and JPY lanes show applying-to-separating spans, exact markers,
   and integer raw activity counts.
2. Confirm the shared raw activity scale is visible and both lanes use it.
3. Confirm small positive counts are not inflated and known zero remains zero.
4. Confirm UNKNOWN uses a hatch/coverage state and is not mistaken for a high
   activity amplitude.
5. Exercise body and aspect filters; confirm the shared axis recomputes while
   event identity and coverage provenance remain unchanged.
6. Select an event and inspect event ID/hash, body, natal target, aspect,
   applying/exact/separating UTC, chart identity and chart hypothesis.
7. Confirm polarity is not assigned and magnitude is not configured.
8. Confirm shared crosshair/time selection and the existing USD, JPY,
   pair-relative and independent SBC fields remain separate.
9. Confirm no clipping or unusable overlap at the normal desktop size.
10. Confirm execution remains read-only and locked.

## Acceptance state

This is a founder-inspection candidate, not a founder acceptance. The required
next action is:

`FOUNDER PHYSICALLY INSPECTS MO-P2-F1 WINDOWS CANDIDATE`

Founder acceptance remains:

`PENDING_FOUNDER_PHYSICAL_INSPECTION`

MO-P3 is intentionally not started.
