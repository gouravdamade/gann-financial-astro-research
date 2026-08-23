# MO-P2-F1-R1 Founder Visual Repair Candidate

Status: BUILT_FOR_FOUNDER_INSPECTION

Founder acceptance: PENDING_FOUNDER_PHYSICAL_INSPECTION

Candidate: `0.10.60-pfr-v2b-mo-p2-f1-r1`

This bounded repair addresses the two visual defects observed in the prior
founder candidate. It does not change the unsigned activity backend contract,
event identity or hash inputs.

## Source and Packaging

- Source repair commit: `f7d6cc8fd9986f1e20c5106706a9a8abeeb26bb3`
- Packaging metadata checkout: `865177c963fbacae1f8e81b84f038c1f7ad793c2`
- Candidate source commit recorded by the manifest: `f7d6cc8fd9986f1e20c5106706a9a8abeeb26bb3`
- Checkout commit recorded by the manifest: `865177c963fbacae1f8e81b84f038c1f7ad793c2`
- `source_git_dirty`: `false`
- Previous candidate `0.10.59-pfr-v2b-mo-p2-f1` remains immutable.

Candidate folder:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.60-pfr-v2b-mo-p2-f1-r1-tauri\`

Artifacts:

- Portable: `GannAstroDesk.exe`
- Installer: `Gann Astro Desk_0.10.60-pfr-v2b-mo-p2-f1-r1_x64-setup.exe`
- Manifest: `release.manifest.json`
- Checksums: `SHA256SUMS.txt`

SHA-256:

- Portable: `CE7D474D5FF77C7CD244D76351C31F1C5B8B5C6296B8A5D6AA2FBBECE038B1DC`
- Installer: `0B779DCDCE111FFA1B0BC9541D19E38314A7F8B5DDD224F1F1735178147EE2B0`
- Packaged sidecar: `A7E0F96CDDDDCB722C487D6B434D1A91CFB866F7B4F666BD3B1621A13FCDD3CD`

## Bounded Changes

### Canonical aspect display matching

The backend continues to emit immutable lowercase aspect identities such as
`square`, `trine` and `conjunction`. The UI now creates a trimmed uppercase
filter key only at the display boundary. Event IDs, event hashes, backend
payloads and filter semantics are otherwise unchanged.

### Activity and coverage rendering

The exact raw-count height remains:

`rawCount / sharedRawAxisMaximum * 100%`

An UNKNOWN coverage state now adds only a thin top hatch band. It no longer
replaces the activity bar with a full-height hatch. The visible legend states
that activity fill height is raw count and coverage hatch is incomplete event
coverage, not magnitude.

No normalization, smoothing, interpolation, signed value, polarity, price
read, outcome read, SBC fusion, LLM, ML, Auto Suggest, MT5 order path or
execution behavior was added.

## Verification

Commands and results:

- Focused frontend: `npx vitest run src/fieldsWorkspace.test.tsx --pool=forks --maxWorkers=1 --reporter=verbose` -> **22/22 passed**.
- Full frontend: `npx vitest run --pool=forks --maxWorkers=1 --reporter=verbose` -> **189/189 passed across 42 files**.
- Oxlint: `npm run lint` -> **passed**.
- Production frontend build: `npm run build` -> **passed**; 1,877 modules transformed.
- Rust formatting: `cargo fmt --manifest-path .\src-tauri\Cargo.toml --check` -> **passed**.
- Rust check: `cargo check --manifest-path .\src-tauri\Cargo.toml` -> **passed**.
- Rust tests: `cargo test --manifest-path .\src-tauri\Cargo.toml` -> **19 passed, 0 failed**.
- Backend regression: `python -m unittest discover -s backend -p 'test_*.py'` -> **319 passed, 1 skipped**.
- `git diff --check` -> **passed**.

The first full frontend run stopped on `ENOSPC` after 167 tests because C:
was nearly full. The authoritative rerun used D: temporary space and passed
all 189 tests. No source failure was associated with the first run.

## Packaged API Probe

Probe output:

`D:\GannFinancialAstro\temp\mo-p2-f1-r1\packaged-activity-probe.json`

The exact founder-window request was sent to the real sidecar launched by the
new portable candidate:

- Range: `2026-08-07T00:00:00Z` through `2026-08-21T00:00:00Z`
- Endpoint: `POST /api/multi-oscillator/activity-range`
- HTTP status: `200`
- Content type: `application/json`
- Contract: `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`
- USD eligible events: `61`
- JPY eligible events: `55`
- USD activity intervals: `88`
- JPY activity intervals: `89`
- USD rejected events: `21`
- JPY rejected events: `20`
- USD coverage: `UNKNOWN`
- JPY coverage: `UNKNOWN`
- `executionAllowed`: `false`

The response began with JSON (`{"activity":{"contract":"MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1"`), not HTML.

## Packaged Visual Gate

The exact portable executable was launched from the candidate folder. The
Fields surface was opened and the activity section was inspected.

Implementer evidence screenshots:

- Initial packaged Fields surface: `D:\GannFinancialAstro\temp\mo-p2-f1-r1\visual-gate-fields-post.png`
- Activity spans, exact markers, raw-count bars and coverage legend:
  `D:\GannFinancialAstro\temp\mo-p2-f1-r1\visual-gate-activity3.png`

The activity screenshot uses the packaged UI's loaded research page
(`2025-05-26` through `2025-05-30`) while the exact requested founder window
was separately validated through the packaged JSON probe above. The screenshot
shows both USD and JPY event spans and exact markers, proportional raw-count
bars, and the thin UNKNOWN coverage hatch. This is implementer evidence, not
founder acceptance.

## Portable Smoke Runs

The existing native smoke procedure was run twice against the exact portable
candidate, with sidecar recovery enabled.

Run 1:

`D:\GannFinancialAstro\soak\tauri_0.10.60-pfr-v2b-mo-p2-f1-r1_20260823_150708\logs\native_soak_report.json`

- Passed: `true`
- Conditional pass: `true`
- Sidecar health: passed
- Same-port sidecar recovery: passed
- Layout persistence after recovery: passed
- Execution locked: passed
- No descendant survivors: passed
- Deferred: optional candlestick specialist corpus not configured

Run 2:

`D:\GannFinancialAstro\soak\tauri_0.10.60-pfr-v2b-mo-p2-f1-r1_20260823_150822\logs\native_soak_report.json`

- Passed: `true`
- Conditional pass: `true`
- Sidecar health: passed
- Same-port sidecar recovery: passed
- Layout persistence after recovery: passed
- Execution locked: passed
- No descendant survivors: passed
- Deferred: optional candlestick specialist corpus not configured

## Founder Checklist

Founder physical inspection remains pending. Please verify on the packaged
candidate:

1. Open Fields for USDJPY.
2. Confirm USD and JPY event spans are visible with all default filters selected.
3. Confirm exact markers are visible inside the event lanes.
4. Toggle an aspect filter and confirm only that aspect's spans disappear and return.
5. Confirm the shared activity scale is labelled as raw counts.
6. Confirm UNKNOWN coverage is a thin hatch band and does not fill the lane.
7. Confirm the visible legend distinguishes coverage hatch from activity height.
8. Confirm event IDs and hashes remain unchanged in the inspector.
9. Confirm `executionAllowed=false` and no signed or predictive output appears.

This candidate is not promoted to stable and no founder acceptance is implied.

