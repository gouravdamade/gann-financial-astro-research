# PFR-V2B-R6-BPHS-T1R-P2 Founder-Inspection Candidate

## Candidate identity

- Version: `0.10.40-pfr-v2b-r6-bphs-t1r-p2`
- Status: `founder_inspection_candidate`
- Exact source commit: `2a5dc41dd3c2340544948d723d64b035d4e20bac`
- Source checkout declaration: detached clean checkout before packaging
- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.40-pfr-v2b-r6-bphs-t1r-p2-tauri\GannAstroDesk.exe`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.40-pfr-v2b-r6-bphs-t1r-p2-tauri\Gann Astro Desk_0.10.40-pfr-v2b-r6-bphs-t1r-p2_x64-setup.exe`
- Portable SHA-256: `E0AD35EFC4920DC682C82B17B1016EE56F376B95D779237934B692D7B2C05FD7`
- Installer SHA-256: `869D2C5768277B6B4455E725C5AF27BA76CAC8E779312ABC898F14E0FBD5E186`

## Included bounded correction

This candidate contains P2 provenance reconciliation only. The held original
1899 BPHS Chapter 14 witness confirms the complete day and night Muhurta table
at printed p. 197 / PDF image 680. The 30 source names and their order did not
change. The full held Chapter 14 range audit did not locate a complete ninefold
Tara sequence or timestamp-evaluable mapping/operator, so Tara remains
`DEPENDENCY_NOT_READY`.

Tithi, Nakshatra, Yoga, and Karana remain engineering-calculated and are not
presented as individually page-transcribed BPHS names or boundaries. Civil
weekday remains partial-source. No price, polarity, SBC, pair field, scoring,
ML, Auto Suggest, MT5 execution, or market-direction functionality changed.

## Verification

| Check | Result |
| --- | --- |
| Clean candidate source state in manifest | passed (`source_git_dirty: false`) |
| Focused BPHS backend suite | 10 passed |
| Full backend regression | 206 run; 7 pre-existing Founder Review packet-hash errors |
| Frontend lint and production build | passed |
| Rust `cargo fmt --check` and `cargo check --locked` | passed |
| Rust tests | 18 passed |
| Portable smoke 1 | conditional pass; no failed checks |
| Portable smoke 2 | conditional pass; no failed checks |
| Direct packaged BPHS endpoint probe | passed |

The full backend failures are outside this milestone: the committed USD blank
review packet blob predates P2 unchanged, while earlier Founder Review manifests
contain a different stale packet hash. P2 did not modify those packet files or
their manifests. This candidate is therefore suitable only for BPHS founder
inspection; the unrelated full-suite integrity defect remains open.

The two portable smoke reports are:

- `D:\GannFinancialAstro\soak\tauri_0.10.40-pfr-v2b-r6-bphs-t1r-p2_20260809_110345\logs\native_soak_report.json`
- `D:\GannFinancialAstro\soak\tauri_0.10.40-pfr-v2b-r6-bphs-t1r-p2_20260809_110527\logs\native_soak_report.json`

Both passed initial health, controlled sidecar restart on the same port,
guardrail checks, persisted layout recovery, and descendant-process cleanup.
The optional candlestick specialist was deferred because it is not configured.

The direct packaged endpoint returned:

- `BPHS_CLASSICAL_CALENDAR_RANGE_V1`;
- `Printed p. 197 / PDF image 680` in the source fixture locator;
- a source-transcribed Muhurta state (`NIGHT MUHURTA 14 - Chitra` for the probe
  timestamp);
- Tara `DEPENDENCY_NOT_READY` with the full-held-Chapter-14 audit explanation;
- `executionAllowed: false`.

## Founder visual inspection

1. Launch the portable executable above, or install only this `0.10.40` NSIS
   candidate. Do not overwrite the accepted `0.10.39` candidate.
2. Open `USDJPY`, then open `Fields`.
3. Set `Classical timing` to `BPHS 1899 Research`.
4. Confirm the BPHS calendar panel is separate from SBC.
5. Move the price-chart crosshair and confirm the categorical calendar state
   changes with time.
6. Inspect both daytime and nighttime Muhurta names, including index and
   day/night identity. Their provenance must point to printed p. 197 / PDF 680.
7. Inspect the source gaps. Weekday must remain engineering-labelled and
   partial-source; Tara must remain `DEPENDENCY_NOT_READY`.
8. Confirm no supportive/adverse color, score, market implication, Auto
   Suggest, or execution control appears in the BPHS panel.

These are founder-inspection steps only. This report does not record founder
acceptance, source certification, financial validation, or permission to begin
the next BPHS milestone.
