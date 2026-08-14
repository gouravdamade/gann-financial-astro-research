# PFR-V2B-R6-BPHS-T1R-P2R2 Founder-Inspection Candidate

Date: 2026-08-14 IST  
Status: founder-inspection candidate only; not founder acceptance and not a stable release.

## Scope

This candidate contains the bounded three-day BPHS calendar viewport correction.
The backend still calculates and caches the accepted 14-calendar-day research
page. The UI presents that already-loaded page through one shared horizontal
three-day viewport for Muhurta, Tithi, Nakshatra, Yoga, Karana, civil weekday,
and Tara. Horizontal scrolling is local UI state and does not request another
BPHS range. Previous/Next 14 days remain the only research-page navigation.

No Tara activation, Agarwal work, polarity, score, market interpretation,
Auto Suggest, ML, or execution behavior was added.

## Source and release identity

- Implementation source commit: `ae4348cc713b68fc44398ae1b9592bb70b47c726`
- Packaging metadata commit: `3dbd47916a751b098f668efb261bcbc2c2562ca4`
- Candidate version: `0.10.46-pfr-v2b-r6-bphs-t1r-p2r2`
- Packaging checkout was clean before packaging. The release manifest reports
  `source_git_dirty: false`; the known post-build Cargo line-ending rewrite is
  not a source change and is excluded by the packaging manifest policy.
- Node: `v24.15.0`
- npm: `11.12.1`
- Execution and financial-validation locks remain false/disabled.

## Changed source paths

- `gann-astro-desk/src/views/BphsClassicalTimingPane.tsx`
- `gann-astro-desk/src/views/FieldsWorkspace.tsx`
- `gann-astro-desk/src/App.css`
- `gann-astro-desk/src/fieldsWorkspace.test.tsx`
- `docs/fields/PFR_V2B_R6_BPHS_T1R_P2R2_SHARED_3_DAY_CALENDAR_VIEWPORT.md`

## Candidate artifacts

Candidate root:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.46-pfr-v2b-r6-bphs-t1r-p2r2-tauri`

- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.46-pfr-v2b-r6-bphs-t1r-p2r2-tauri\GannAstroDesk.exe`
- Portable SHA-256: `257AA2B5929962D7765A7E717425994D35A771F36704BDB36D274FFFE9F0123B`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.46-pfr-v2b-r6-bphs-t1r-p2r2-tauri\Gann Astro Desk_0.10.46-pfr-v2b-r6-bphs-t1r-p2r2_x64-setup.exe`
- Installer SHA-256: `9ADCDF615A3B17218040F7AE8DA4FCC4D9E2DB5AA78944C924CF5C743BAE9B6B`
- Release manifest SHA-256: `3B3E7F8BD66D4CBD19B57704C9B9CF72B100EE13F4F916771718AB4353A6228A`
- Bundled BPHS fixture was present at `backend/_internal/research_labs/bphs_1899_classical_timing/bphs_1899_packet_1w_muhurta_fixture.json`.

The manifest records 1,492 files and 897,248,110 total bytes. The accepted
0.10.45 candidate was not overwritten.

## Verification

| Check | Result |
| --- | --- |
| Focused Fields test: `npx vitest run src/fieldsWorkspace.test.tsx --pool=threads --maxWorkers=1 --reporter=dot` | 1 file, 12/12 passed |
| Full frontend: `npm test -- --pool=threads --reporter=dot` | 36 files, 157/157 passed |
| Oxlint: `npm run lint` | passed |
| Production frontend build: `npm run build` | passed; existing chunk-size warning only |
| Full backend discovery: `npm run test:backend` | 209/209 passed |
| Rust format: `cargo fmt --check` | passed |
| Rust check: `cargo check` | passed |
| Rust tests: `cargo test` | 18/18 passed |

The focused and full source checks were run against the implementation commit
before packaging; the only change between that source and the package checkout
was version metadata.

## Packaged smoke verification

The exact portable candidate was launched twice:

1. `D:\GannFinancialAstro\soak\tauri_0.10.46-pfr-v2b-r6-bphs-t1r-p2r2_20260814_035856\logs\native_soak_report.json`
2. `D:\GannFinancialAstro\soak\tauri_0.10.46-pfr-v2b-r6-bphs-t1r-p2r2_20260814_040050\logs\native_soak_report.json`

Each report passed all `42/42` applicable checks, including backend health,
chart loading, disabled MT5 trading, execution locks, sidecar restart and
recovery, and clean shutdown. The only deferred item in both reports is the
explicitly optional, unconfigured candlestick specialist:
`candlestick_specialist_optional_not_configured`.

## Founder physical inspection checklist

These checks remain pending and are not marked accepted by the implementer:

1. Launch the portable candidate above, open USDJPY, then open **Fields** and
   **BPHS Calendar**.
2. Confirm the header shows the loaded research page as 14 days and the BPHS
   visible window as 3 of 14 days.
3. Confirm the category labels remain frozen while one horizontal scrollbar
   moves Muhurta, Tithi, Nakshatra, Yoga, Karana, civil weekday, and Tara on
   the same time scale.
4. Scroll across the loaded page and confirm only the visible-window label
   changes; no BPHS request or loading cycle should occur.
5. Use Previous/Next 14 days and confirm exactly one new research-page request,
   with the viewport reset to the beginning of the new page.
6. Confirm clipped half-open intervals remain aligned at viewport edges.
7. Confirm Tara remains `DEPENDENCY_NOT_READY`, source/provenance text is
   unchanged, and execution remains locked.

Founder acceptance is still pending the physical UI inspection.
