# PFR-V2B-R6-BPHS-T1R-P1 Founder-Inspection Candidate

## Candidate identity

- Version: `0.10.39-pfr-v2b-r6-bphs-t1r-p1`
- Status: `founder_inspection_candidate`
- Exact source commit: `9772277991c3ce3715bb0c6cb11c5890bd094369`
- Source checkout declaration: detached clean checkout before packaging
- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.39-pfr-v2b-r6-bphs-t1r-p1-tauri\GannAstroDesk.exe`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.39-pfr-v2b-r6-bphs-t1r-p1-tauri\Gann Astro Desk_0.10.39-pfr-v2b-r6-bphs-t1r-p1_x64-setup.exe`
- Portable SHA-256: `4D5E9F2293155FB477FFA7A786A4D05FF4A5600C7158221C893DEEC0C02C3BDA`
- Installer SHA-256: `6687304123DF6F74119C90E36B77E44A8838F2D8484EA0785B49515EB7EE537C`

## Scope and packaging repair

The candidate contains the bounded BPHS 1899 Packet 1W calendar inspector.
It does not include later BPHS timing chapters, polarity, scoring, market
meaning, Auto Suggest, ML, MT5 execution, or packaging promotion.

The preceding `0.10.38-pfr-v2b-r6-bphs-t1r` folder is not suitable for review:
its PyInstaller sidecar did not collect the source-closed Muhurta fixture. The
P1 repair resolves resources from `sys._MEIPASS`, collects the fixture into the
sidecar, and makes the sidecar packaging script fail if the fixture is missing.
The packaged P1 tree contains
`backend\_internal\research_labs\bphs_1899_classical_timing\bphs_1899_packet_1w_muhurta_fixture.json`.

## Verification

| Check | Result |
| --- | --- |
| Focused BPHS backend suite | 9 passed |
| Full supported backend suite | 205 passed |
| Focused Fields suite | 8 passed |
| Full frontend suite | 35 files, 151 tests passed |
| Frontend lint and production build | passed |
| Rust `cargo fmt --check` and `cargo check` | passed |
| Rust tests | 18 passed |
| Portable smoke 1 | conditional pass, no failed checks |
| Portable smoke 2 | conditional pass, no failed checks |
| Packaged BPHS endpoint | passed |

The two portable smoke reports are:

- `D:\GannFinancialAstro\soak\tauri_0.10.39-pfr-v2b-r6-bphs-t1r-p1_20260808_153502\logs\native_soak_report.json`
- `D:\GannFinancialAstro\soak\tauri_0.10.39-pfr-v2b-r6-bphs-t1r-p1_20260808_153720\logs\native_soak_report.json`

The additional packaged endpoint probe returned `NIGHT MUHURTA 14 - Chitra`;
the weekday lane was `Civil weekday: Tuesday` with `PARTIAL_SOURCE`; Tara was
`DEPENDENCY_NOT_READY`; the profile declared four source gaps; and execution
remained false.

## Founder visual checklist

1. Launch the portable executable above. Do not use the rejected 0.10.38 folder.
2. Open `USDJPY`, then open `Fields`.
3. Set `Classical timing` to `BPHS 1899 Research`.
4. Confirm the BPHS calendar section appears separately from SBC.
5. Move the price-chart crosshair and confirm the categorical calendar state
   changes with time.
6. Inspect daytime and nighttime Muhurta names; their period and index must
   remain visible alongside the source name.
7. Inspect provenance and source gaps. The Weekday lane must remain
   engineering-labelled and partial-source; Tara must remain unavailable.
8. Confirm no supportive/adverse color, score, price implication, Auto Suggest,
   or execution control appears in the BPHS section.

These are founder inspection steps only. This document does not record founder
acceptance, source certification, or financial validation.
