# PFR-V2B-R6-SBC-A2R1 Founder-Acceptance Candidate

Status: FOUNDER ACCEPTANCE CANDIDATE
Date: 2026-08-15

## Scope

This bounded correction aligns the Agarwal 2000 source-profile badge with the
actual source evidence. No board, cell, strength-row, Vedha, financial-ledger,
Fields, or execution behavior changed.

The previous A2 candidate was physically reviewed by the founder. The board,
orientation, cell audit, p.144 provenance, source-strength panel, Vedha lock,
Chapter-20 research panel, and execution locks passed visual review. One
semantic wording issue remained.

Old wording:

`GEOMETRY + STRENGTH SOURCE CLOSED`

Corrected wording:

`GEOMETRY CLOSED · STRENGTH SOURCE-RECORDED`

The corrected badge does not claim that the strength methodology or its
aggregation is source-closed. Row-level strength statuses remain visible as
their committed values, including `SOURCE_CLOSED` and `PARTIAL`.

## Source And Candidate

- Candidate version: `0.10.48-pfr-v2b-r6-sbc-a2r1`
- Source commit: `1d3896befae4e34aa9c3804c0bee4452aad8a830`
- Implementation commit: `76a073365dcab2aec176542911f01ef18769e66d`
- Version/package metadata commit: `1d3896b`
- Source git dirty: `false` in the release manifest
- Candidate status: `founder_acceptance_candidate`
- Prior `0.10.48-pfr-v2b-r6-sbc-a2-bridgefix` candidate: preserved unchanged

Portable artifact:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2r1\GannAstroDesk.exe`

Portable SHA-256:

`1D9B263747562F89373926BF7D44126C91EDD127CCCAEB9573460C972AF3AA38`

Installer:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2r1\Gann Astro Desk_0.10.48-pfr-v2b-r6-sbc-a2r1_x64-setup.exe`

Installer SHA-256:

`5423D4F7C4288C6A274B6009FC1AB79272EBB24FAEE3F7FDFFF5EF5C3E38876B`

Release manifest:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2r1\release.manifest.json`

Checksums:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2r1\SHA256SUMS.txt`

## Verification

- Focused Agarwal frontend: `npx vitest run --pool=threads --maxWorkers=1 --testTimeout=15000 src/agarwalSourceInspector.test.tsx` -> 2/2 tests passed.
- Full frontend: `npx vitest run --pool=threads --maxWorkers=1 --testTimeout=15000` -> 37 files passed, 159/159 tests passed.
- Focused Agarwal backend: `python -m unittest discover -s backend -p "test_agarwal_source_inspector.py" -v` -> 5/5 passed.
- Full backend: `python -m unittest discover -s backend -p "test_*.py" -v` -> 214/214 passed.
- Lint: `npm run lint` -> passed.
- Production build: `npm run build` -> passed.
- Rust formatting: `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` -> passed.
- Rust check: `cargo check --manifest-path src-tauri/Cargo.toml` -> passed.
- Tauri tests: `cargo test --manifest-path src-tauri/Cargo.toml` -> 19 passed, 0 failed.
- Packaging dependency install: `npm ci --ignore-scripts` -> completed from the tracked lockfile. npm reported existing audit findings (5 high severity); no dependency upgrade was introduced in this milestone.

## Packaged Smoke

Smoke run 1:

`D:\GannFinancialAstro\soak\tauri_0.10.48-pfr-v2b-r6-sbc-a2r1_20260815_044349\logs\native_soak_report.json`

Result: passed, conditional pass only for the pre-existing optional
`candlestick_specialist_not_configured` defer. Required checks passed:
backend health, Agarwal endpoint contract, 81 cells, read-only state, sidecar
restart/recovery, layout survival, execution lock, and no descendant survivors.

Smoke run 2:

`D:\GannFinancialAstro\soak\tauri_0.10.48-pfr-v2b-r6-sbc-a2r1_20260815_044512\logs\native_soak_report.json`

Result: passed with the same optional specialist defer; no failed checks or
errors, `execution_allowed = false`, recovery healthy, Agarwal 81-cell check
passed, and no descendant survivors.

## Locked Product State

- `AGARWAL_GEOMETRY_READY = true`
- `AGARWAL_STRENGTH_READY = true` for source records only
- `AGARWAL_VEDHA_OPERATOR_READY = false`
- `A2_SCOPE = GEOMETRY_STRENGTH_INSPECTOR_ONLY`
- `A2_SCOPE_FULL_VEDHA_INSPECTOR = NOT_AUTHORIZED`
- Chapter 20 = `FINANCIAL_HYPOTHESIS_LEDGER_ONLY`
- `executionAllowed = false`
- No Vedha rays, polarity, scoring, Fields influence, pair logic, Auto Suggest,
  ML, MT5 execution, or order logic was added or enabled.

## Founder Physical Confirmation

Founder acceptance is still pending confirmation of the corrected candidate.
The candidate is not marked `FOUNDER_ACCEPTED` by this report.
