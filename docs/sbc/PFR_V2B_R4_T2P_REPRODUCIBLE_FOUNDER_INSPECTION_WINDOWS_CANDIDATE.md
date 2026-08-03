# PFR-V2B-R4-T2P - Reproducible Founder-Inspection Windows Candidate

## Status

`FOUNDER_INSPECTION_PENDING` - this candidate is not promoted to stable and
has not been founder-accepted. It is a non-promoted research build containing
the application source through `1fc3853ea8268dba9c17e006e29b22f36dfa1afb`.

The accepted `0.10.32-pfr-u1-s1` candidate was not replaced or modified.

## Source and reproducibility

- Candidate version: `0.10.33-pfr-r4-t2r`
- Application source commit: `1fc3853ea8268dba9c17e006e29b22f36dfa1afb`
- Clean packaging checkout commit: `86bdcd0163c1a0c8b8cf25e5b615cccf4f044fa2`
- `origin/master`: `86bdcd0163c1a0c8b8cf25e5b615cccf4f044fa2`
- Pre-package checkout status: empty (`git status --short`)
- Manifest source state: `source_git_dirty=false`
- Package install: `npm ci` from the tracked lockfile
- Build: `npm run desktop:build -- --bundles nsis`
- Node: `v24.15.0`
- npm: `11.12.1`
- Python: `3.14.4`
- PyInstaller: `6.20.0`
- Rust: `rustc 1.97.0 (2d8144b78 2026-07-07)`
- Cargo: `1.97.0 (c980f4866 2026-06-30)`

The packaging checkout shows a post-build line-ending touch to
`src-tauri/Cargo.toml`; this happened after the empty pre-package gate and is
not application source. It is not included in the source commit declaration.

## Package outputs

Immutable candidate folder:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.33-pfr-r4-t2r`

- Portable: `GannAstroDesk.exe`
- NSIS installer: `Gann Astro Desk_0.10.33-pfr-r4-t2r_x64-setup.exe`
- Backend sidecar: `backend\GannAstroBackend.exe`
- Manifest: `release.manifest.json`
- Checksums: `SHA256SUMS.txt`

Final SHA-256 values:

```text
GannAstroDesk.exe                                      403494119C212EE4E81943EC89A9430220234DEE14DF6F5B74E8E8121A99591C
Gann Astro Desk_0.10.33-pfr-r4-t2r_x64-setup.exe       5FD9B51D503E5B994AADADE3A1499C2BD74E277F3C945975A618EB41C5206684
backend/GannAstroBackend.exe                           972CF6A3C782082463480BD54A23F850769F3C51C953DF8D53CE4FA9E514E152
release.manifest.json                                   3E707BED0C525728072C20B689E29D3CB2ADD739F6CE9C174E26A383370EE7F7
```

## Verification record

### Frontend

- `npm.cmd run lint`: pass (Oxlint)
- `npm.cmd test`: **32 files, 137 tests passed**
- Focused T2R command:

```text
npm exec -- vitest run --pool=threads --no-file-parallelism --maxWorkers=1 src/api.test.ts src/chakraLabWorkspace.test.tsx src/visualizationModes.test.ts src/visualizationSourceGaps.test.ts
```

  Result: **4 files, 39 tests passed**.
- `npm.cmd run build`: pass as part of the final Tauri build.

One earlier fork-pool focused attempt timed out while starting a worker after
19 assertions had passed. It was not counted as a successful run; the
single-thread rerun above is the recorded focused result.

### Python and Rust

- Focused T2R Python suite: **44 passed**.
- Full supported Python regression: **656 passed, 1 skipped**.
- The one skip is the explicit external JHora witness test requiring
  `JHORA_WITNESS_CSV`; it is not treated as a failure.
- `cargo fmt --check`: pass.
- `cargo check --offline`: pass.
- Rust tests: **18 passed, 0 failed**.
- Status validator: valid, 21 documents, 13 audits, `executionAllowed=false`.
- Status unit tests: **55 passed**.

### Exact portable smoke launches

The final candidate was launched twice with
`packaging\soak_tauri_release.ps1 -DurationSeconds 20
-AllowClosedMarketMt5Defer`.

1. Report:
   `D:\GannFinancialAstro\soak\tauri_0.10.33-pfr-r4-t2r_20260803_053928\logs\native_soak_report.json`
   Result: **42/42 checks true, passed=true, errors=none**.
2. Report:
   `D:\GannFinancialAstro\soak\tauri_0.10.33-pfr-r4-t2r_20260803_054031\logs\native_soak_report.json`
   Result: **42/42 checks true, passed=true, errors=none**.

Both runs also exercised managed sidecar restart/recovery, same-port
recovery, chart/Chakra endpoints, read-only MT5 behavior, layout survival and
descendant cleanup. Both are `conditional_pass=true` only because the
optional candlestick specialist is not configured. No execution path became
available.

## Guardrails recorded by the candidate

- `market_direction=ABSTAIN`
- `mt5_execution_mode=read_only_market_data`
- `collective_research_only=true`
- `collective_directional_contribution=0`
- `chakra_lab_mode=read_only_guidance`
- `chakra_lab_execution_allowed=false`
- `planetary_line_execution_allowed=false`
- `planetary_line_live_inference_allowed=false`
- `planetary_line_auto_suggest_allowed=false`
- `collective_auto_suggest_allowed=false`
- `collective_execution_allowed=false`
- `arghya_market_mapping_allowed=false`
- `arghya_auto_suggest_allowed=false`
- `arghya_execution_allowed=false`
- `market_synthesis_execution_allowed=false`

No polarity, magnitude, score aggregation, price conversion, Auto Suggest,
order placement, execution, Trailokya wave or natural-planet promotion was
added.

## Founder-only packaged UI checklist

Codex did not mark these checks accepted. They must be performed against the
portable candidate or installed candidate, not the development server:

1. Open a chart with at least two visible timestamps and open Chakra Board.
2. Select `SBC_TRAILOKYA_1972_V1` / `Trailokya 1972 source-only geometry`.
3. Confirm automatic board refresh, figure-relative rays and categorical
   reached cells.
4. Confirm there is no guidance score, polarity, wave or request error.
5. Open Workspace and confirm USD and JPY lanes use the accepted founder
   chart identities.
6. Confirm the SBC synchronized lane displays
   `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` as an availability state.
7. Confirm all seven unresolved Trailokya source gaps are visible.
8. Switch back to Phaladeepika and confirm its existing atomic-range behavior
   remains intact.

This report intentionally leaves founder acceptance pending.
