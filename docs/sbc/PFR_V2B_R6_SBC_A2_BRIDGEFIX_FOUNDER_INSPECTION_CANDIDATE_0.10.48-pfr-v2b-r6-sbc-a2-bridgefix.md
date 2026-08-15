# PFR-V2B-R6-SBC-A2 Bridge-Fix Founder Inspection Candidate

Status: `FOUNDER_INSPECTION_CANDIDATE` — implementer evidence only; not
founder acceptance.

## Scope

- Candidate version: `0.10.48-pfr-v2b-r6-sbc-a2-bridgefix`
- Packaged source commit: `3978e668828afba36ead64ec8bd1aee633350d4a`
- Source checkout: clean at packaging; manifest `source_git_dirty = false`
- Repair: native Tauri source-profile bridge uses authenticated `GET`, matching
  `/api/chakra-lab/agarwal-source-profile`.
- Agarwal scope: `A2_SCOPE_GEOMETRY_STRENGTH_INSPECTOR_ONLY`
- Execution: `executionAllowed = false`
- Vedha: `DEPENDENCY_NOT_READY`
- Chapter 20: `FINANCIAL_HYPOTHESIS_LEDGER_ONLY`

No source doctrine, geometry, strength records, Vedha behavior, polarity,
score, Fields/pair behavior, Auto Suggest, ML, MT5, or execution capability
changed in this correction.

## Artifacts

- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2-bridgefix\GannAstroDesk.exe`
  - SHA-256: `547559DA8532688D6D74ED49E2F7E3386AAFB4FF87FAF37D30BC33399D7FE38E`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2-bridgefix\Gann Astro Desk_0.10.48-pfr-v2b-r6-sbc-a2-bridgefix_x64-setup.exe`
  - SHA-256: `A835AC241F13ADEAABFDCF77E4A0C99D23BC874BC64B6E5FDF6669D208DF6CA3`
- Manifest: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2-bridgefix\release.manifest.json`
- Checksums: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2-bridgefix\SHA256SUMS.txt`

## Verification

| Gate | Result |
|---|---|
| Oxlint | passed |
| Full frontend | `npx vitest run --pool=threads --maxWorkers=1 --testTimeout=15000` — 37 files, 159/159 passed |
| Full backend | `python -m unittest discover -s backend -p "test_*.py" -v` — 214/214 passed |
| Production frontend build | `npm run build` — passed |
| Rust fmt/check | passed |
| Rust tests | 19/19 passed, including the exact authenticated Agarwal GET bridge request |
| Clean package install | `npm ci` — passed from the tracked lockfile |

## Packaged Smoke

Both exact-portable runs passed with controlled sidecar restart, recovery, and
clean child-process shutdown. Both are conditional only because the optional
candlestick specialist is not configured.

1. `D:\GannFinancialAstro\soak\tauri_0.10.48-pfr-v2b-r6-sbc-a2-bridgefix_20260815_012934\logs\native_soak_report.json`
2. `D:\GannFinancialAstro\soak\tauri_0.10.48-pfr-v2b-r6-sbc-a2-bridgefix_20260815_013021\logs\native_soak_report.json`

Each report proves the packaged sidecar endpoint is reachable, returns
`AGARWAL_GEOMETRY_STRENGTH_INSPECTOR_V1`, has 81 cells, is read-only, and
reports `VEDHA DEPENDENCY_NOT_READY`. It does not replace the founder’s visual
inspection of the Tauri UI.

## Founder Check

1. Install the new candidate, or run its portable executable. It is separate
   from the faulty `0.10.47` candidate.
2. Select `Chakra` then `Agarwal 2000 Research`.
3. Confirm the board appears instead of an error; inspect a few cells and the
   seven strength records.
4. Confirm the Vedha panel says `DEPENDENCY_NOT_READY`, no rays/predictions
   appear, and the screen remains read-only.

Founder acceptance is intentionally not recorded here.
