# PFR-V2B-R5-F4-A-P4 Windows Founder Candidate

Date: 2026-09-29

## Disposition

This is the immutable Windows founder-inspection candidate for the accepted
F4-A chart-native activity and compact Fields UX. It is not founder acceptance.

- Starting commit: `1adc15ee3bdb764187fdc5d5948d24f45896bddf`
- Packaging-prep commit: `87e5a0b72818be7a30908bbe3bb4a74b47e542ea`
- Branch: `research/pfr-v2b-r5-f4-a-p4-windows-founder-candidate`
- Candidate version: `0.10.67-pfr-v2b-r5-f4-a-p3-r2`
- Milestone: `PFR-V2B-R5-F4-A-P4`
- Candidate status: `founder_inspection_candidate`
- QA documentation commit: reported by Git after the Stage B documentation commit; it is not embedded self-referentially in this file.

The package is bound to the packaging-prep commit. This later documentation
commit does not rebuild or mutate the candidate.

## Artifacts

Candidate directory:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.67-pfr-v2b-r5-f4-a-p3-r2-tauri-clean-r2`

Portable executable:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.67-pfr-v2b-r5-f4-a-p3-r2-tauri-clean-r2\GannAstroDesk.exe`

Portable SHA-256:

`9305BEC42398D08629A31C44AABA67249261B39099ED6410800E360CC29A1D31`

Installer:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.67-pfr-v2b-r5-f4-a-p3-r2-tauri-clean-r2\Gann Astro Desk_0.10.67-pfr-v2b-r5-f4-a-p3-r2_x64-setup.exe`

Installer SHA-256:

`5AADE24E22CF275BD23D63523ECCDE8BACEDAF5A1F791E2CB4384F17CBA9F152`

Sidecar SHA-256:

`85C02D953901669C17E682ED5B731C96DEBD33EA71D853952AE5BE5ADC8B5691`

Immutable backend resource-tree SHA-256:

`7950DB4F694499AC7CA2D0185068804F718B934B1621D0658ABA2D4511C98179`

Build receipt SHA-256:

`D6D7ED505FF3445E2DDA83138AB91F2A3701CC69FBC896FC30BC2B14B952AA72`

Release manifest SHA-256:

`39A6658B1E017709B8818B2B0E91E36BDC0EDEC9D3D557E951AE270230672CBE`

The package also contains `build.receipt.json`, `release.manifest.json`,
`SHA256SUMS.txt`, and `BETA_README.md`. No private source images, provider
captures, credentials, or outcome data were bundled.

## Build Verification

- `npm ci`: passed. Existing audit output reported 7 dependency advisories (2 moderate, 5 high); dependencies were not changed.
- `npm run lint`: passed.
- Frontend tests: 49 files, 244/244 passed.
- TypeScript/Vite production build: passed.
- `cargo fmt --check`: passed.
- `cargo metadata --locked --no-deps --format-version 1`: passed.
- `cargo check --locked`: passed.
- `git diff --check`: passed.
- Final packaging workflow: `build_tauri_windows.ps1`, portable and NSIS outputs produced.
- Packaging receipt: `sourceGitDirty=false`, `executionAllowed=false`.

## Native Packaged Smoke

The established `soak_tauri_release.ps1` was run twice against the exact
portable candidate, each run using a distinct isolated `D:\GannFinancialAstro\soak\tauri_...` data root.

Run 1 report:

`D:\GannFinancialAstro\soak\tauri_0.10.67-pfr-v2b-r5-f4-a-p3-r2_20260929_055737\logs\native_soak_report.json`

Run 2 report:

`D:\GannFinancialAstro\soak\tauri_0.10.67-pfr-v2b-r5-f4-a-p3-r2_20260929_060005\logs\native_soak_report.json`

Both runs verified:

- app launch and initial sidecar health;
- read-only and execution-lock contracts;
- Chakra endpoint and 81-cell contract;
- Agarwal source-profile endpoint, 81 cells, and read-only contract;
- chart/planetary/candlestick/RSI contract probes;
- layout creation and persistence;
- same-port sidecar recovery;
- clean descendant shutdown.

Both reports had no runtime errors, `execution_allowed=false`, and
`no_descendant_survivors=true`.

The inherited `chakra_jupiter_motion_explicit` check was false in both runs.
This is the already-known optional Chakra readiness condition and remains
reported separately as `DIGNITY_REQUIRED`/not configured. It was not repaired
in P4. The optional candlestick specialist remained
`NOT_CONFIGURED_OPTIONAL`.

## Founder Visual QA Boundary

Native CUA screenshot/control tooling was unavailable in this session. The
following visual checks therefore remain unexecuted and must be performed by
the founder on the candidate:

- Chart toolbar visibly exposes `INDICATORS`, `RSI`, and `Fields & Waves`.
- Chart activity uses one lower pane below price with shared crosshair, pan,
  zoom, and time alignment.
- Fields exposes `Add USD/JPY Activity to Chart` without scrolling and returns
  to the same chart context.
- Compact zero-coverage card and neutral wording are visible at 1280x800.
- Research details expand/collapse correctly.
- Mode 2 and Mode 3 remain compact and withhold directional fields.
- USDJPY symbol gate and dirty Founder Review guard are visually exercised.
- Price-only, price plus RSI, price plus activity, and price plus RSI plus
  activity preserve pane ownership.
- A wider desktop viewport remains readable.

Focused frontend tests and the packaged contract probes cover the relevant
behavioral paths, but they are not a substitute for native visual inspection.
No screenshots were captured. Founder acceptance is not claimed.

## Scope and Locks

The candidate contains accepted F4-A presentation only. No new research logic
was added. The following remain unchanged or disabled:

- `backendChanged=false`
- `activityMathChanged=false`
- `pairMathChanged=false`
- `polarityCatalogueChanged=false`
- `evidenceRegistryChanged=false`
- `F4B implemented=false`
- `F4C implemented=false`
- Candidate C unchanged
- EMP3 unauthorized
- provider access false
- outcome analysis false
- MT5 order invocation false
- `executionAllowed=false`

No polarity admission, score aggregation, Auto Suggest, ML, provider capture,
outcome access, Candidate C access, or market execution was performed.

## Next Gate

`CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P4_WINDOWS_FOUNDER_CANDIDATE`

Founder physical inspection remains required before any acceptance claim.
