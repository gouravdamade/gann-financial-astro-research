# PFR-V2B-R5-F4-A-P5 Post-RSI Windows Founder Candidate

Date: 2026-10-01

## Candidate Identity

- Milestone: `PFR-V2B-R5-F4-A-P5`
- Branch: `research/pfr-v2b-r5-f4-a-p5-post-rsi-windows-founder-candidate`
- Starting commit: `706f8b5ee5e994f92c92cd41554aab8a47961cb1`
- Packaging-prep commit: `622802d14cc770d799f887119cfd7530ef102eaa`
- QA documentation commit: the commit containing this report; its exact SHA is the final branch tip reported in the release closeout.
- Version: `0.10.68-pfr-v2b-r5-f4-a-p4-r2`
- Candidate status: `FOUNDER_ACCEPTED` (physical inspection closed 2026-10-04)
- Candidate root: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.68-pfr-v2b-r5-f4-a-p4-r2-tauri-clean-r2`
- `sourceGitDirty=false`; `executionAllowed=false`.

P4-R2 remains `CENTRAL_PASS`; live RSI source provenance is closed. R1 research-history architecture remains accepted. Founder visual RSI confirmation is accepted as recorded below. F4-B and F4-C remain unauthorized.

## Source Diff

The source diff from starting commit `706f8b5ee5e994f92c92cd41554aab8a47961cb1` to packaging-prep commit `622802d14cc770d799f887119cfd7530ef102eaa` contains only:

- `CURRENT_PROJECT_HANDOFF.md`
- `gann-astro-desk/package-lock.json`
- `gann-astro-desk/package.json`
- `gann-astro-desk/src-tauri/Cargo.lock`
- `gann-astro-desk/src-tauri/Cargo.toml`
- `gann-astro-desk/src-tauri/tauri.conf.json`
- `status/research/pfr_v2b_r5_f4_a_p4_r2_live_rsi_history_provenance.json`

These are version/package metadata, the P4-R2 central status transition, and handoff provenance. No behavioral source, RSI mathematics, chart behavior, Fields & Waves logic, polarity data, or execution code changed. The package builder produced a fresh backend sidecar and a fresh optimized Tauri executable; it did not reuse a prior-version executable.

The preferred candidate directory was created by an initial packaging pass, but the packaging script correctly refused finalization after detecting a line-ending-only rewrite of the tracked sidecar `.gitkeep`. That one generated change was restored to the committed bytes. The successful package was finalized from its verified build receipt into the deterministic `-r2` candidate root above. Do not treat the incomplete preferred directory as a release candidate.

## Package Artifacts

- Portable executable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.68-pfr-v2b-r5-f4-a-p4-r2-tauri-clean-r2\GannAstroDesk.exe`
  - SHA-256: `D2413A35CF978E677A19A01A545AA5BEA4FBFD5022F8A719809E825319113B11`
- NSIS installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.68-pfr-v2b-r5-f4-a-p4-r2-tauri-clean-r2\Gann Astro Desk_0.10.68-pfr-v2b-r5-f4-a-p4-r2_x64-setup.exe`
  - SHA-256: `BC1870F491482B737F9FB1C0B9FF82F62A072CACC2C4AA31969D7361D6934F9D`
- Bundled backend executable SHA-256: `E2D0116504AB4C529F44F98157062B21D60C99DBDD369B4888D5143614C9D4BC`
- Backend immutable resource tree SHA-256: `EB4CAA387D9975F3CFCA144153D8950789DB3796014695A29B5C52D73C3A2206` (3,541 files)
- `build.receipt.json` SHA-256: `8BB564648E71BA8099619A3276DF80E52E138F6793A8C3F47BEA9BD6A16ECCAC`
- `release.manifest.json` SHA-256: `3CADAA34FF5B1120377A35B664545742DC75A41A676B1B03AF8CEF25C2DE578C`
- `SHA256SUMS.txt` is included. The receipt binds source and packaging checkout commit `622802d14cc770d799f887119cfd7530ef102eaa`, `sourceGitDirty=false`, and `executionAllowed=false`.
- Candidate resource scan found no PDF, JPG, JPEG, or PNG files.
- Prior immutable P4 `0.10.67` portable and installer hashes remain unchanged.

## Verification

- `npm ci`: passed; npm reported 7 existing dependency advisories (2 moderate, 5 high). No audit fix or dependency change was made beyond the version lock metadata.
- Focused frontend: 86/86 across 8 files, covering RSI, chart toolbar/panes/layout/viewport, Fields & Waves activity, and Fields workspace UX.
- Full frontend: 254/254 across 49 files.
- TypeScript: passed.
- Oxlint: passed.
- Vite production build: passed; existing large-chunk advisory remains.
- Focused backend: 47/47 across the live chart route, repository, RSI analysis, chart layouts, aspect timeframe, market synthesis, and MT5 gateway modules. Live-route tests: 6/6, including R2 same-source history/no-overlap provenance coverage.
- Full backend discovery: not run and not claimed; inherited CPU-heavy S3R1 tests were intentionally outside this bounded gate.
- `cargo fmt --check`: passed.
- `cargo metadata --locked --no-deps --format-version 1`: passed.
- `cargo check --release`: passed.
- Rust test suite: not run for this packaging-only milestone.
- `git diff --check`: passed before package and will be rechecked with this QA record.

## Packaged Smoke Runs

Both runs used the final `-r2` candidate root and separate isolated application-data roots. Each launched the app, reached a healthy sidecar, passed chart/RSI evidence and execution-lock checks, passed layout persistence and same-port sidecar recovery, shut down with no surviving descendants, and deferred only the optional unconfigured candlestick specialist. Both harness invocations returned failure solely because the inherited `chakra_jupiter_motion_explicit` check was `false`; the reports contain no runtime errors. The exact underlying Chakra status is not established by these reports. This check is reported separately and was not changed in P5.

1. Report: `D:\GannFinancialAstro\soak\tauri_0.10.68-pfr-v2b-r5-f4-a-p4-r2_20261001_165343\logs\native_soak_report.json`. Failed check: `chakra_jupiter_motion_explicit`. Surviving descendants: none.
2. Report: `D:\GannFinancialAstro\soak\tauri_0.10.68-pfr-v2b-r5-f4-a-p4-r2_20261001_165447\logs\native_soak_report.json`. Failed check: `chakra_jupiter_motion_explicit`. Surviving descendants: none.

These are not represented as two passing harness runs; both have the same inherited non-RSI failure.

## Packaged Live RSI Source Probe

From the final `-r2` portable candidate, a read-only authenticated request to `GET /api/chart?source=live&symbol=USDJPY&timeframe=D1&liveBarCount=12` returned HTTP 200 with `dataSource=mt5_live`, 12 visible candles, and 1,000 `indicatorHistory.candles`. The latest history timestamp was strictly earlier than the first visible candle timestamp. This verifies the packaged live source contract and same-source boundary; no values or event outcomes were retained. The isolated probe application shut down cleanly and its direct child processes were absent afterward. `executionAllowed=false`.

The accepted bounded limit remains: `Mt5Gateway.bars` clamps the total request to 5,000 bars, so exceptionally large visible windows may leave fewer than 1,000 preceding history bars. This was not changed in P5.

## Visual Review

`NATIVE_VISUAL_CONTROL_UNAVAILABLE` records the earlier automated QA limitation; the founder subsequently completed physical inspection. The prior pending state is superseded by the dated acceptance record below.

Founder checklist:

- USDJPY D1 live with RSI 14: confirm numeric RSI, visible line, and no permanent warming-up state.
- Confirm hidden warm-up bars do not change the visible price range.
- Enable RSI 14 and Fields & Waves activity: confirm all panes coexist, crosshair/time axis align, and sizing/viewport remain usable.
- Confirm the INDICATORS toolbar is visible and discoverable, and compact Fields UX is unchanged.

## Founder Physical Inspection Close (2026-10-04)

Founder reported physical inspection of the final immutable `-r2` candidate and confirmed all four required visual items accepted:

1. USDJPY D1 live RSI 14 shows a numeric value and visible line, without a permanent warming-up state: **ACCEPTED**.
2. Hidden RSI warm-up bars do not change the visible price range: **ACCEPTED**.
3. RSI 14 and Fields & Waves activity coexist with aligned crosshair/time axis and usable sizing/viewport: **ACCEPTED**.
4. The INDICATORS toolbar is discoverable and compact Fields UX is unchanged: **ACCEPTED**.

The acceptance applies only to the founder-inspection candidate and the listed visual checks. It does not authorize F4-B, F4-C, EMP3, execution, or any application behavior change. `executionAllowed=false` remains in force.

The two packaged smoke harnesses retain their inherited `chakra_jupiter_motion_explicit=false` result. This check and its reports are unchanged; it is not an RSI/P5 acceptance defect. The smoke harnesses are not recharacterized as fully passing.

## Locked State

`r1Included=true`; `r2Included=true`; `rsiFormulaChanged=false`; `closedBarSemanticsChanged=false`; `researchHistorySourceClosed=true`; `liveHistorySourceClosed=true`; `crossSourceRsiMixingAllowed=false`; `visibleRangeChanged=false`; `fieldsWavesChanged=false`; `activityMathChanged=false`; `pairMathChanged=false`; `polarityCatalogueChanged=false`; `evidenceRegistryChanged=false`; `candidateCChanged=false`; `emp3Authorized=false`; `outcomeAnalysis=false`; `mt5OrderInvocation=false`; `F4BImplemented=false`; `F4CImplemented=false`; `executionAllowed=false`; `founderAcceptance=true`.

Next gate: `CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P5_FOUNDER_ACCEPTANCE_CLOSE`. This is a closeout-record review only; no subsequent implementation scope is authorized here.
