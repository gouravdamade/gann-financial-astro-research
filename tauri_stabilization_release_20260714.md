# Gann Astro Desk 0.9.1 Stabilization Release

Date: 2026-07-14

## Scope

This release hardens the Tauri 2 / Rust shell introduced in 0.9.0. It does not
change the frozen prospective policy, astrology doctrine, timestamp-safe decision
engine, or MT5 execution permissions.

## Runtime Recovery

- Added `GANN_RUNTIME_DIAGNOSTICS_V1` startup, lifecycle, request-latency, local
  Jyotish, prospective-refresh, and artifact-generation diagnostics.
- Added a compact frontend diagnostics dock with reconnect and cache-refresh
  controls.
- The Rust supervisor now restarts a failed Python sidecar on the same loopback
  port, limits restart attempts within a rolling window, and owns descendants in
  a Windows Job Object so shutdown does not leave workers behind.
- Native crash-injection soak verified sidecar PID replacement, same-port
  recovery, persisted chart layouts, execution locks, and zero surviving child
  processes.

## Packaged Generation Fix

The 0.9.1 pre-release exposed a Windows/PyInstaller defect: a frozen backend that
started another copy of itself for a corrected-data worker could remain idle before
importing pandas or either generator. The same command completed from a normal
terminal, so generator logic and data were not the cause.

Packaged generation now runs the two existing generator entry points directly on
`GenerationJobManager`'s background thread. Development mode retains subprocess
isolation. The Flask server therefore remains responsive, while packaged
cancellation is observed at generator-stage boundaries rather than in the middle
of a generator call.

Regression coverage proves that packaged mode does not invoke `Popen`, restores
`sys.argv`, and completes a real two-stage event-plus-SR-touch job.

## Release Artifacts

- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Executable SHA-256:
  `F7A371991250974AFBED4B693C300DCA7B714377448B03E067532AFA433531B6`
- NSIS installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.9.1_x64-setup.exe`
- Installer SHA-256:
  `059F78A93E5A749D6F114389831F1FA745F85E54EC3E3A080E8FE15A34469F43`
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.9.0_20260714_222152`

The installer is not code-signed. MT5 remains
`read_only_market_data`, `tradeAllowed=false`, and all runtime execution guards
remain false.

## Evidence

- Frozen sidecar generation proof:
  `D:\GannFinancialAstro\soak\frozen_inprocess_probe_20260714_203652\frozen_inprocess_generation_report.json`
  completed one corrected event and one SR touch in 24.25 seconds.
- Final copied-candidate generation proof:
  `D:\GannFinancialAstro\soak\final_candidate_generation_20260714_211059\final_candidate_generation_report.json`
  completed one corrected event and one SR touch in 14.65 seconds.
- Native crash/recovery soak:
  `D:\GannFinancialAstro\soak\tauri_0.9.1_20260714_153835\logs\native_soak_report.json`
  passed all 11 checks.
- Real writable-state restart preserved the cancelled status of generation job
  `8394a28dba854c418622b41d97bc6885`, connected to MetaQuotes-Demo in read-only
  mode, and reported `GANN_RUNTIME_DIAGNOSTICS_V1` with execution disabled.

## Verification

- Python: 117 passed.
- Frontend: 17 Vitest tests passed with one worker.
- Oxlint: passed.
- TypeScript/Vite production build: passed; the existing 504.41 kB main-chunk
  warning remains a future code-splitting opportunity.
- Ruff and Python byte compilation: passed.
- PowerShell parser checks: passed.
- Rust: `cargo check`, `cargo test`, Clippy with warnings denied, and `cargo fmt
  --check` passed.
- Tauri release and NSIS bundle: passed.
