# PFR-V2B-R4-T2P-U1 - Founder Inspection Candidate 0.10.35

## Status

`FOUNDER_INSPECTION_PENDING`. This is a non-promoted Windows research
candidate. It is not a stable release, financial validation result, or
founder acceptance record.

The accepted `0.10.32-pfr-u1-s1` candidate was not replaced. The prior
`0.10.33-pfr-r4-t2r` candidate was also not overwritten.

## Source and reproducibility

- Implementation source commit: `b014f2e7dc3b028e60d2bcf04d0fd18e83a82399`
- Clean packaging checkout commit: `e3fb716b01e9203c259de33dd83ec68ef0486c8d`
- `origin/master` at packaging: `e3fb716b01e9203c259de33dd83ec68ef0486c8d`
- Pre-package checkout: clean (`git status --short` empty)
- Candidate version: `0.10.35-pfr-r4-t2p-u1`
- Package installation: `npm ci` from the tracked lockfile
- Node: `v24.15.0`
- npm: `11.12.1`
- Python: `3.14.4`
- PyInstaller: `6.20.0`
- Rust: `rustc 1.97.0 (2d8144b78 2026-07-07)`
- Cargo: `1.97.0 (c980f4866 2026-06-30)`

The source package fix is limited to including the chart-conditioned profile
files in the backend sidecar. It does not add doctrine or change execution.

## Candidate outputs

Immutable candidate folder:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.35-pfr-r4-t2p-u1`

- Portable: [GannAstroDesk.exe](D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.35-pfr-r4-t2p-u1\GannAstroDesk.exe)
- Installer: [Gann Astro Desk_0.10.35-pfr-r4-t2p-u1_x64-setup.exe](D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.35-pfr-r4-t2p-u1\Gann%20Astro%20Desk_0.10.35-pfr-r4-t2p-u1_x64-setup.exe)
- Manifest: [release.manifest.json](D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.35-pfr-r4-t2p-u1\release.manifest.json)
- Checksums: [SHA256SUMS.txt](D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.35-pfr-r4-t2p-u1\SHA256SUMS.txt)

SHA-256:

```text
GannAstroDesk.exe                                      E9C469B4D994921D37440EA03D62D11350AAF871A87D0AE0089EE48277F7BCC4
Gann Astro Desk_0.10.35-pfr-r4-t2p-u1_x64-setup.exe   86359486C2B5C1D36E7DA6429D207C839DA635C9013EDD1D321540CB18C5AF79
backend/GannAstroBackend.exe                           FD474D9A74F7957866589FAA05AD34ABFEAAAB5553A0F31D888E0F75708EEA02
release.manifest.json                                   FDFB2FA3039934A5E01101CB72A135E05AF2284A703973150B2E265AFE88E855
```

## U1 implementation evidence

- `IndependentFieldStack` is in the left price-context column, after the
  aspect legend, instead of below the complete price/Chakra/audit workspace.
- The field group is expanded by default for a valid chart range.
- USD, JPY, and SBC remain independent lanes. USD and JPY visibly render
  categorical unknown gaps when no polarity interval exists; no waveform is
  fabricated.
- The responsive toolbar exposes previous candle, Time, Profile, Wheel,
  Phase lab, Compare, Fields, and next candle. The controls remain in the
  native UI tree and are keyboard-focusable.
- Native inspection of the selected Trailokya profile found the exact SBC
  state: `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED`. The state is an availability
  message, not zero, neutral, an error, or a scored fallback.
- Native inspection also found the seven Trailokya source gaps and the
  score/polarity/wave suppression described by the source-only profile.

## Verification commands and counts

Frontend:

- `npm.cmd run lint`: passed (Oxlint)
- `npm.cmd exec -- vitest run --pool=threads --no-file-parallelism --maxWorkers=1`:
  **32 files / 139 tests passed**
- `npm.cmd exec -- vitest run --pool=threads --no-file-parallelism --maxWorkers=1 src/productFirstSbcWorkspace.test.tsx`:
  **1 file / 7 tests passed**
- `npm.cmd run build`: passed through the production Vite build used by the
  desktop package

Backend and packaging:

- Focused Python suite (`test_classical_oscillator_coverage.py`,
  `test_trailokya_dipika_vedha_page_certification.py`,
  `test_trailokya_source_only_geometry.py`, and
  `gann-astro-desk/backend/test_chakra_lab_service.py`): **41 passed**
- Full supported Python regression: **657 passed, 1 skipped**. The skip is
  the explicit external JHora witness test because `JHORA_WITNESS_CSV` was
  not configured.
- Desktop packaging regression: **4 passed**
- `cargo fmt --check`: passed
- `cargo check --offline`: passed
- `cargo test --offline`: **18 passed, 0 failed, 0 ignored**
- Release-manifest and execution-lock validation: passed; the manifest records
  read-only market data, `market_direction=ABSTAIN`, and all execution,
  Auto Suggest, financial-validation, and Trailokya wave locks false.

## Native smoke results

The exact portable candidate was launched twice with the native soak harness.

1. `D:\GannFinancialAstro\soak\tauri_0.10.35-pfr-r4-t2p-u1_20260805_184908\logs\native_soak_report.json`
   - **42/42 checks true**, passed, no errors
2. `D:\GannFinancialAstro\soak\tauri_0.10.35-pfr-r4-t2p-u1_20260805_185130\logs\native_soak_report.json`
   - **42/42 checks true**, passed, no errors

Both runs verified health, chart/Chakra endpoints, read-only behavior,
execution locks, managed sidecar restart/recovery, layout survival, and
cleanup. Both remain conditional only because the optional candlestick
specialist is not configured.

## Packaged UI captures

These captures were taken from the exact portable candidate, not the
development server:

- [Initial Workspace](D:\GannFinancialAstro\ui_check_t2p_u1_initial.png):
  toolbar, price context, visible-aspect legend, and the start of the USD
  field stack are visible together.
- [Scrolled field stack](D:\GannFinancialAstro\ui_check_t2p_u1_scrolled4.png):
  separate USD and JPY categorical panes and their unknown-gap legend are
  visible.
- [Trailokya Workspace](D:\GannFinancialAstro\ui_check_t2p_u1_trailokya_workspace.png):
  Trailokya source-only profile, seven source gaps, read-only/no-lookahead
  locks, toolbar, price context, and independent field stack are visible.

The lower SBC availability text was also confirmed through the packaged
window's native UI inspection tree. A founder-readable screenshot of that
lower text is still pending.

## Founder checks still pending

Codex has not marked founder acceptance. Please perform the following against
the portable candidate or its installed copy:

- [ ] 1920x1080 at Windows scale 100%, with price and all three panes visible
- [ ] 1920x1080 at Windows scale 125%
- [ ] 1920x1080 at Windows scale 150%
- [ ] 1366x768 at Windows scale 100%
- [ ] Full toolbar remains readable and Phase lab, Compare, and Fields are
      reachable at each size
- [ ] Trailokya screenshot showing USD, JPY, and the explicit SBC
      `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` lane
- [ ] Phaladeepika screenshot showing its existing independent SBC behavior
- [ ] Right audit panel remains scrollable and no content is hidden behind the
      Windows taskbar

No stable promotion, R4-T3, Trailokya geometry compilation, polarity,
magnitude, score aggregation, price conversion, Auto Suggest, execution, or
natural-planet promotion was added.
