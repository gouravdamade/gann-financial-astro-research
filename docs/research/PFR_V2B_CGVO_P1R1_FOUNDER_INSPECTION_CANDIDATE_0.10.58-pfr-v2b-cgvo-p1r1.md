# PFR-V2B-CGVO-P1R1 Founder Inspection Candidate

Status: `FOUNDER_INSPECTION_CANDIDATE`

This candidate is the bounded correction release after the founder-inspection
candidate `0.10.57-pfr-v2b-cgvo-p1`. Candidate `0.10.57` remains the historical
candidate and was not overwritten or modified.

## Source and artifacts

- Source implementation commit: `86b10f0266e67efa25fcbd1a5b1f1f08a88bb6a5`.
- Candidate version: `0.10.58-pfr-v2b-cgvo-p1r1`.
- Release folder:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.58-pfr-v2b-cgvo-p1r1-tauri`.
- Portable executable:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.58-pfr-v2b-cgvo-p1r1-tauri\GannAstroDesk.exe`.
- Portable SHA-256:
  `ACA866A885FF6C4E63B3D288BB93558647A3AE7D90A6A84E3A1298F7656158FD`.
- NSIS installer:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.58-pfr-v2b-cgvo-p1r1-tauri\Gann Astro Desk_0.10.58-pfr-v2b-cgvo-p1r1_x64-setup.exe`.
- Installer SHA-256:
  `E2B9F61A72DE70F8A7371195614FC5643A58E6BC7CF15EB26C31E702A6AEC322`.
- Release manifest: same release folder, `release.manifest.json`.
- Manifest declares `source_git_dirty=false` and the same full source commit.

Historical candidate retained unchanged:

- `0.10.57-pfr-v2b-cgvo-p1` portable SHA-256:
  `3F98069850C58A8B45AAA06C754FCD765FB59C21D33B77FF2153C26CFFFD89E8`.
- `0.10.57-pfr-v2b-cgvo-p1` installer SHA-256:
  `7F0EA5B729677E73E259977AA4455438C8123594A99D388C5E0777A4F40F89F9`.

## Bounded corrections

- Sun and Moon horizontal coordinates are topocentric and retain the raw Swiss
  Ephemeris azimuth alongside the explicit display convention
  `NORTH_CLOCKWISE_0N_90E_180S_270W`.
- Visibility is explicitly `VISIBLE`, `NOT_VISIBLE`, or `RISE_SET_CLIPPED`,
  with clipped interval and horizon details. A locality without a matching
  local event does not borrow horizon timestamps from another event.
- Lunar `umbralMagnitude` and `penumbralMagnitude` are separate fields sourced
  from `swe.lun_eclipse_how` at the event maximum.
- Swiss UT identity fields are separate from UTC display fields. The causal
  event ID is reconstructed and compared with the URL/request event ID.
- The Kurma seed carries raw Chapter XIV historical names and verse ranges only;
  modern geographic inference remains disabled. The raw-name layer follows the
  Chapter XIV source translation, including its nine directional groups, without
  turning historical names into modern coordinates. See the
  [Bṛhat Saṃhitā Chapter XIV translation](https://www.wisdomlib.org/hinduism/book/brihat-samhita/d/doc228914.html).
- No CGVO mathematics, source-profile composition, price/outcome input, market
  direction, Fields/SBC input, Auto Suggest, ML, MT5, or execution behavior was
  added. `executionAllowed=false` remains invariant.

## Real packaged JSON probe

The exact portable executable was launched with an isolated D: data root and
its managed sidecar port was discovered from the running process. Probe record:

`D:\GannFinancialAstro\probe\cgvo-p1r1-20260821-rerun\packaged_json_probe.json`

The probe passed every assertion. The tested packaged routes returned
`application/json` and no response contained an HTML SPA fallback:

- `/api/health`
- `/api/experiments/cgvo/status`
- `/api/experiments/cgvo/kurma-gazetteer-seed`
- `/api/experiments/cgvo/eclipse-search` for solar and lunar searches
- `/api/experiments/cgvo/workbench` for valid solar, valid lunar, and clipped
  lunar local circumstances
- `/api/experiments/cgvo/workbench` with a wrong `causalEventId`

Observed probe facts:

- Solar event `CGVO-SOLAR-B1265AFAF8178B2C2480`, Swiss UT and UTC display
  `2027-08-02T10:06:41Z`, returned a valid workbench.
- Lunar event `CGVO-LUNAR-D07327912413ED2AA881`, Swiss UT and UTC display
  `2025-03-14T06:58:46Z`, returned a valid workbench.
- Sun and Moon were marked topocentric and carried the expected azimuth
  contracts.
- Lunar magnitudes were `umbral=1.17805821` and `penumbral=2.25973026` with
  the explicit Swiss-Ephemeris reference.
- The Antarctic lunar probe returned `RISE_SET_CLIPPED`.
- The wrong causal event ID returned typed `400 application/json` containing a
  causal-ID error.
- Raw Kurma names were present and `modernGeographicInference=false`.

## Verification

Focused source/API tests: `13 passed, 0 failed`.

Focused frontend CGVO tests using the stable Windows configuration:

```text
npm exec vitest -- run --pool=threads --maxWorkers=1 --no-file-parallelism src/cgvoWorkspace.test.tsx
3 passed, 0 failed
```

Full frontend regression using the same stable configuration:

```text
npm exec vitest -- run --pool=threads --maxWorkers=1 --no-file-parallelism
42 files, 177 tests passed, 0 failed
```

Full backend regression: `264 passed, 0 failed`.

Additional checks:

- Oxlint: passed.
- Vite production build: passed.
- `cargo fmt --check`: passed.
- `cargo check`: passed.
- Rust/Tauri tests: `19 passed, 0 failed`.
- The default fork-worker Vitest invocation still hits the known Windows
  startup timeout; the stable threads-pool command above is the recorded
  verification command.

## Packaged smoke runs

Two isolated portable smoke runs passed with zero errors, sidecar recovery,
clean shutdown, no surviving descendants, and execution locked:

1. `D:\GannFinancialAstro\soak\tauri_0.10.58-pfr-v2b-cgvo-p1r1_20260821_001930\logs\native_soak_report.json`
2. `D:\GannFinancialAstro\soak\tauri_0.10.58-pfr-v2b-cgvo-p1r1_20260821_002101\logs\native_soak_report.json`

The optional candlestick specialist remains `NOT_CONFIGURED_OPTIONAL`; this is
the same deferred condition recorded by the existing smoke contract.

## Founder physical inspection checklist

Founder acceptance remains pending. Inspect the exact `0.10.58` portable
candidate, not the development server:

1. Open `Experiments` and select `CGVO classical geography & visibility`.
2. Search both `SOLAR` and `LUNAR` in a bounded UTC range.
3. Confirm the global identity displays Swiss UT identity separately from UTC
   display time.
4. Confirm Sun/Moon horizontal facts show topocentric status and the explicit
   azimuth convention.
5. Inspect a lunar event and confirm umbral and penumbral magnitudes are
   separate.
6. Inspect a locality where the event is clipped by rise/set and confirm the
   clipped state is explicit.
7. Confirm a selected event's causal ID is the reconstructed event identity.
8. Expand the Kurma groups and confirm raw historical names are visible while
   modern mapping remains unknown.
9. Confirm no bullish/bearish label, score, price interpretation, Auto Suggest,
   ML, MT5 order, or execution control is present.

Founder acceptance has not been marked by this report.
