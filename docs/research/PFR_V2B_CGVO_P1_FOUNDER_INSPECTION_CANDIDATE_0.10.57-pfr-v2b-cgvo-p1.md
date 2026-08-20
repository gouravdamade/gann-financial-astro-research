# PFR-V2B-CGVO-P1 Founder-Inspection Candidate

## Candidate

- Version: `0.10.57-pfr-v2b-cgvo-p1`
- Status: `founder_inspection_candidate`
- Source/package commit: `7ce501704cefc6be5201ab98d08505964417b8fb`
- CGVO implementation commit: `eeab5e95284d378d03c5dabdaeee8c3e26698ab1`
- `source_git_dirty`: `false`
- Build inputs: canonical `npm ci` from the tracked lockfile
- Node: `v24.15.0`
- npm: `11.12.1`

Portable executable:
`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.57-pfr-v2b-cgvo-p1-tauri\GannAstroDesk.exe`

Portable SHA-256:
`3F98069850C58A8B45AAA06C754FCD765FB59C21D33B77FF2153C26CFFFD89E8`

NSIS installer:
`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.57-pfr-v2b-cgvo-p1-tauri\Gann Astro Desk_0.10.57-pfr-v2b-cgvo-p1_x64-setup.exe`

Installer SHA-256:
`7F0EA5B729677E73E259977AA4455438C8123594A99D388C5E0777A4F40F89F9`

The release manifest and `SHA256SUMS.txt` are in the same immutable release
directory. Private PDFs, photographs, OCR, databases and logs are not bundled.

## Product Scope

CGVO is available under `Experiments` as `CGVO classical geography & visibility`.
It is a read-only research inspector with three isolated source profiles:

- `MODERN_ASTRONOMY_VISIBILITY_V1`
- `VARAHAMIHIRA_BS_ECLIPSE_V1`
- `TRAILOKYA_1972_GEOGRAPHY_ARGHA_V1`

The modern profile uses Swiss Ephemeris eclipse facts and keeps one causal event
identity per physical eclipse. Locality changes local circumstances only; it does
not create a second event. Varahamihira mappings remain explicit unknowns where
the held witness does not close them. Trailokya displays the exact source-silent
visibility state and does not compose with the modern or Varahamihira profiles.

No price, outcome, market direction, score, Fields/SBC value, Auto Suggest, ML,
MT5 order path or execution behavior was added. `executionAllowed=false`.

## Verification

Focused backend:

```text
python -m unittest discover -s backend -p "test_cgvo*.py" -v
7 passed
```

Focused frontend:

```text
npm test -- --run src/cgvoWorkspace.test.tsx
2 passed
```

Packaging-focused:

```text
python -m unittest discover -s backend -p "test_desktop_packaging.py" -v
6 passed
```

Full backend:

```text
python -m unittest discover -s backend -p "test_*.py"
258/258 passed
```

Full frontend:

```text
npm test
42 files passed; 176 tests passed
```

Additional checks:

- `npm run lint`: passed.
- `npm run build`: passed; Vite emitted only the existing large-chunk warning.
- `cargo fmt --check`: passed.
- `cargo check`: passed.
- `cargo test`: 19 passed, 0 failed.
- Tauri Windows packaging: passed.

## Packaged Candidate Smoke

Both established portable smoke runs passed all required checks, with the
existing optional candlestick specialist deferred because it remains
`NOT_CONFIGURED_OPTIONAL`:

1. `D:\GannFinancialAstro\soak\tauri_0.10.57-pfr-v2b-cgvo-p1_20260820_220659\logs\native_soak_report.json`
2. `D:\GannFinancialAstro\soak\tauri_0.10.57-pfr-v2b-cgvo-p1_20260820_220820\logs\native_soak_report.json`

Both reports show healthy startup, sidecar recovery, clean shutdown, no
surviving descendants, and execution locked.

The additional packaged API probe launched the exact portable executable and
discovered its managed sidecar dynamically. The following real packaged
requests all returned `200` with `Content-Type: application/json` and a JSON
object, not an HTML SPA fallback:

- `/api/experiments/cgvo/status`
- `/api/experiments/cgvo/source-profiles`
- `/api/experiments/cgvo/kurma-gazetteer-seed`
- `/api/experiments/cgvo/workbench`

The workbench response carried
`CLASSICAL_GEOGRAPHY_VISIBILITY_OBSERVATORY_V1`, a solar total-eclipse event,
seven explicit source-unknown reasons, two source-profile records, and
`executionAllowed=false`. The packaged sidecar contains all three expected
CGVO fixture files under `backend\_internal\configs\research\cgvo`.

## Founder Physical Inspection Checklist

Founder inspection is still pending; this report does not mark acceptance.

1. Launch the portable executable above.
2. Open `Experiments` and select `CGVO classical geography & visibility`.
3. Search both `SOLAR` and `LUNAR` within a bounded UTC range.
4. Change locality between Ujjain, New York and London and verify that local
   circumstances change while the global causal event identity remains stable.
5. Inspect the modern event facts, contact timeline and local visibility state.
6. Inspect Varahamihira claims and confirm unresolved mappings remain explicit.
7. Inspect the Trailokya panel and confirm the exact source-silent banner,
   locked cross-source composition and locked market mapping.
8. Inspect the raw Kurma groups and confirm modern mapping remains unknown.
9. Confirm no bullish/bearish label, score, price interpretation, Auto Suggest,
   ML, MT5 order or execution control is present.
10. Confirm the read-only/experimental guardrails remain visible.

## Known Limits

- The held Varahamihira witness metadata is not fully authenticated; source
  mappings therefore remain `UNKNOWN`/`MAPPING_UNRESOLVED` as applicable.
- Trailokya eclipse-visibility doctrine is `SOURCE_SILENT` in the held witness.
- Kurma geography is retained as raw source grouping; modern locality mapping is
  not inferred.
- The optional candlestick specialist remains unconfigured.

Founder acceptance is pending the physical inspection above.
