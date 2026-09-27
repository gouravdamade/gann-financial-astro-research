# PFR-V2B-R5-F4-A-P2 Windows Founder Candidate

Status: `FOUNDER_INSPECTION_CANDIDATE`
Milestone: `PFR-V2B-R5-F4-A-P2`
Candidate: `0.10.66-pfr-v2b-r5-f4-a-p1-r1`
Built: `2026-09-27`

This record binds the native Windows candidate for the accepted chart-native
price plus unsigned USD/JPY activity implementation. It is a founder-inspection
candidate, not a founder acceptance. F4-B directional chart fields and F4-C
polarity admission remain unauthorized.

## Source and package identity

- Accepted R1 implementation commit:
  `7168486ad9e9d83ce7438584e0ba7df5fd1ea7bd`
- Packaging preparation commit:
  `0488c70bbed876fbd80780b71d61638f0d052bed`
- Packaging branch:
  `research/pfr-v2b-r5-f4-a-p2-windows-founder-candidate`
- Candidate source commit: `0488c70bbed876fbd80780b71d61638f0d052bed`
- `sourceGitDirty`: `false`
- Entry URL:
  `index.html?v=0.10.66-pfr-v2b-r5-f4-a-p1-r1`
- Dependency versions were not changed. `npm ci` reported the existing audit
  advisory of 2 moderate and 5 high vulnerabilities; no dependency repair was
  attempted in this packaging milestone.

The prep commit changes only package/version metadata, the accepted R1 status
disposition, and the project handoff. No backend, source profile, event
compiler, chart mathematics, polarity catalogue, or execution code changed.

## Candidate artifacts

Candidate root:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.66-pfr-v2b-r5-f4-a-p1-r1-tauri-clean`

- Portable:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.66-pfr-v2b-r5-f4-a-p1-r1-tauri-clean\GannAstroDesk.exe`
  - SHA-256: `9BA7A66313E04FF91E1C426EDAA03A14307FB870402ACF47FB006A3737A4EEB0`
- Installer:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.66-pfr-v2b-r5-f4-a-p1-r1-tauri-clean\Gann Astro Desk_0.10.66-pfr-v2b-r5-f4-a-p1-r1_x64-setup.exe`
  - SHA-256: `E384930019ECB93AF7D09FD23639DFCF1343F580A04807C2BEC8751FED467CF9`
- Packaged sidecar:
  `backend\GannAstroBackend.exe`
  - SHA-256: `B68E4B5EAB51382CB592F47AC6A7D9DE6027AAF1F82495BE822B58D423E368BE`
- Immutable backend resource tree SHA-256:
  `B3AF7B4BD29DABFAAE4FB03802B1E1D93C3C4089AABC9082D4C1FA57A14CBBE2`
- `build.receipt.json` SHA-256:
  `37C207092158279205D945296F09169C4ADC411F582663D6589F365E12386041`
- `release.manifest.json` SHA-256:
  `CCED6F2382EAC579ABD31A5A63CDF0F7D419946272AB0BC477DC895645577BFC`

The receipt and manifest both bind the exact prep commit and record
`sourceGitDirty=false` and `executionAllowed=false`. `SHA256SUMS.txt` records
the portable, installer, sidecar, receipt, and manifest hashes.

Private source photographs, PDFs, OCR dumps, BI5 files, credentials, and logs
were not bundled. The existing backend resource tree contains its ordinary
runtime resources, including the existing annotation SQLite resource and CA
certificate bundles; no private source evidence was added.

## Verification

- `npm ci`: passed. Existing audit advisory noted above; dependency versions
  remain unchanged.
- Focused frontend activity/controller tests: 2 files, 16/16 passed.
- Full frontend: 47 files, 233/233 passed.
- TypeScript: `npx tsc -b` passed.
- Oxlint: `npm run lint` passed.
- Production frontend build: `npm run build` passed. The existing large-chunk
  warning remains informational.
- Focused backend activity/API suite: 15/15 passed.
- Rust: `cargo fmt --check`, `cargo metadata --format-version 1 --no-deps`,
  `cargo check`, and `cargo test` passed. Rust tests: 19 passed.
- `git diff --check`: passed before packaging.
- Tauri NSIS packaging: passed using the existing Windows packager. The first
  sidecar-build pass correctly refused to publish when PyInstaller rewrote the
  tracked placeholder line ending; the generated placeholder was restored and
  the clean-sidecar second pass produced the bound candidate without bypassing
  the packager's dirty-tree guard.

The broad `npm run test:backend` discovery was started, emitted failures before
its summary, and remained CPU-active beyond a reasonable verification window.
It was stopped without a summary and is therefore recorded as
`INCOMPLETE_TIMEOUT_AFTER_EARLY_FAILURES`, not as a pass. The accepted R1
baseline remains the prior central result of 319 passed and 1 skipped; no
backend source changed in P2. The focused activity/API regression above is the
authoritative P2 backend check.

## Packaged runtime smoke

The exact portable executable was launched with isolated data roots. No normal
founder data root was used, and all launched processes were shut down.

Established soak reports:

1. `D:\GannFinancialAstro\soak\tauri_0.10.66-pfr-v2b-r5-f4-a-p1-r1_20260927_153616\logs\native_soak_report.json`
2. `D:\GannFinancialAstro\soak\tauri_0.10.66-pfr-v2b-r5-f4-a-p1-r1_20260927_154038\logs\native_soak_report.json`

Both runs verified app launch, JSON sidecar health, read-only MT5 state,
Agarwal source profile availability with 81 cells, execution locks, layout
creation, and clean shutdown with zero descendant survivors. Run 1 also
verified same-port sidecar crash recovery and layout survival after recovery.
Run 2 was the normal-startup/no-crash-recovery variant.

Both generic reports were blocked only by the inherited
`chakra_jupiter_motion_explicit` assertion (`DIGNITY_REQUIRED` in the optional
Chakra smoke payload). This assertion is outside F4-A chart/activity scope and
was not changed. The optional candlestick specialist remained safely
`NOT_CONFIGURED_OPTIONAL`.

## Packaged chart/activity JSON probe

Two additional focused probes launched the exact portable candidate through the
real packaged sidecar and used fresh isolated data roots:

1. `D:\GannFinancialAstro\packaged_smoke\f4a_p2_focus_20260927_154012\f4a_p2_focus_probe.json`
2. `D:\GannFinancialAstro\packaged_smoke\f4a_p2_focus_20260927_154149\f4a_p2_focus_probe.json`

Each probe passed:

- `GET /api/health`: HTTP 200, `application/json`.
- `GET /api/chart`: JSON chart payload returned.
- `POST /api/multi-oscillator/activity-range`: HTTP 200,
  `application/json`.
- Contract: `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`, schema `2`.
- USD and JPY side identities present; second probe observed 56 USD and 51
  JPY eligible events with 79 and 77 returned activity intervals.
- Shared raw-count and coverage data remained source-backed activity only.
- `executionAllowed=false`, `polarityAssigned=false`,
  `priceDataRead=false`, and `priceOutcomeRead=false` in the activity
  guardrails.

An initial probe attempt stopped after discovering the sidecar before its HTTP
listener was ready. No API request completed in that attempt; the two bounded
wait probes above are the authoritative packaged results.

## Visual QA boundary

The repository frontend suite covers the chart-native activity state and the
packaged API probe covers the real runtime data contract. Native screenshot or
coordinate QA at exact 1280x800 and wide desktop could not be executed in this
session because the available Computer Use surface exposed no native Windows
application target. These are intentionally recorded as:

- `nativeVisual1280x800`: `NOT_EXECUTED_CUA_NATIVE_TARGET_UNAVAILABLE`
- `nativeVisualWideDesktop`: `NOT_EXECUTED_CUA_NATIVE_TARGET_UNAVAILABLE`
- chart crosshair/pan/zoom/gap/known-zero/UNKNOWN/bounded-partial/marker/RSI/
  drawing/resize visual checks: `PENDING_FOUNDER_PHYSICAL_INSPECTION`

No founder acceptance is claimed. The founder checklist below is the required
next human inspection.

## Founder inspection checklist

1. Open the exact portable executable at the candidate path.
2. Confirm the existing USDJPY price chart and the chart-native activity lanes
   load at ordinary 1280x800 desktop size.
3. Confirm USD and JPY activity use the shared raw-count axis and preserve
   integer counts without visual inflation.
4. Confirm known zero, loaded UNKNOWN, unloaded gaps, bounded partial ranges,
   and exact-event markers remain visually distinct.
5. Exercise the shared crosshair, pan, and zoom without introducing activity
   across unloaded intervals.
6. Resize the price/activity panes and confirm the chart remains usable.
7. Confirm RSI and existing drawing tools remain available and do not create
   direction, score, magnitude, or execution behavior.
8. Confirm the existing Fields, SBC, Agarwal, and source-profile workflows
   remain separate.
9. Confirm no polarity catalogue, Auto Suggest, ML, MT5 order, or execution
   control becomes enabled.

Founder acceptance remains `PENDING_FOUNDER_PHYSICAL_INSPECTION`.

## Locks and next gate

- `executionAllowed=false`
- no polarity or score aggregation
- no price forecast or market-direction output
- no Auto Suggest or ML
- no MT5 order/execution
- no provider access or outcome read in P2
- no Candidate C or EMP3 access
- no F4-B/F4-C implementation

Next gate:

`CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P2_WINDOWS_FOUNDER_CANDIDATE`
