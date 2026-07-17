# Gann Astro Desk End-to-End Product Audit

Date: 2026-07-18 IST

Stable release: 0.10.8

Scope: Windows/Tauri shell, React chart workspace, Python sidecar, corrected
event generation, live/research data flow, local specialist services,
packaging, tests, runtime evidence, repository recovery, and documentation.

## Executive Result

The supported Windows app is coherent and broadly well tested, but the audit
did not find a product that should be called finished. It found several real
runtime and recovery defects plus a smaller set of explicit research gates and
maintenance liabilities.

Release 0.10.8 corrects the high-confidence runtime defects:

1. Packaged astronomy generation now runs in an isolated child process.
2. The chart API becomes available before Codex and Ollama warm-up.
3. Polling is non-overlapping, visibility-aware, and panel-aware.
4. Live candles use incremental `series.update` when the window permits it.
5. Large workspaces load as separate frontend chunks.
6. Native runtime logs rotate at 10 MiB with three backups.
7. Routine Werkzeug access lines no longer fill the error log.
8. Each native launch protects its random loopback port with a random API
   token.
9. The previously ignored `gann-astro-desk/index.html` is now tracked, so a
   clean Git checkout can actually build the app.
10. The native soak harness authenticates every request with a constrained
    one-launch token, so private-loopback security is tested rather than
    bypassed.

Execution remains intentionally locked. This audit does not promote any
research rule to live order placement.

## Evidence Reviewed

- Current handoff and all tracked project documentation.
- Git status/history and recovery-repository structure.
- All tracked Python, TypeScript/React, Rust, packaging, test, and configuration
  paths.
- Runtime startup diagnostics and native sidecar logs.
- Current app-data and generated-artifact footprints.
- Existing verification suites and packaged-release scripts.
- Official Lightweight Charts, React, Tauri, and TradingView product guidance.

No unused Python definitions were reported by the dead-code scan. Redundancy is
concentrated in legacy architecture and large mixed-responsibility modules,
not in a large set of trivially removable functions.

## Correctness Findings

### Corrected in 0.10.8

#### Packaged generator process isolation

The frozen sidecar previously called the worker entrypoint synchronously inside
the HTTP process. A CPU-heavy rebuild could therefore starve API requests even
though the job appeared to be on a background thread. Frozen and source
generation now both use child processes, preserving cancellation and process
supervision.

#### Private loopback authentication

A random port is useful isolation but is not authentication. The Rust shell now
generates a per-launch token, passes it only to its Python child, exposes it to
the trusted frontend runtime, and sends it on every backend request. Missing or
incorrect tokens fail with HTTP 403 in packaged mode. Tokenless source mode is
retained for normal Vite development.

This is an interim hardening step. The long-term target is to move every
frontend/backend operation behind typed Tauri commands and scoped capabilities,
then remove browser-facing wildcard CORS.

#### Recoverable clean checkout

The root `*.html` ignore pattern accidentally ignored the Vite entry document.
The app built only because an untracked local `index.html` happened to exist.
The ignore exception and entry document are now versioned.

#### Shutdown race

Deferred Codex/Ollama startup now checks the shutdown latch before publishing a
new process handle. A shutdown arriving during helper startup cannot leave that
new process orphaned.

### Deliberate gates, not implementation bugs

- Corrected transit-to-transit generation is still disabled.
- Shadbala and Drik Bala require external reference certification.
- Rule learning still requires purged prospective/out-of-sample validation.
- BTC evidence still requires a rolling, no-lookahead production mode.
- Retrospective policy validation has not passed the promotion gate.
- MT5 remains read-only market data; execution is locked.

These controls should remain visible in the product. They must not be hidden by
an LLM explanation or treated as minor TODOs.

## Performance Findings

### Startup

Cold packaged startup evidence showed roughly 40 seconds before the main chart.
The largest avoidable contributor was optional Ollama initialization competing
with backend import and HTTP readiness. The local NVIDIA driver was also too old
for the attempted CUDA path, causing a Vulkan fallback.

The sidecar now imports the backend and opens HTTP first. Codex starts
asynchronously after readiness; Ollama starts after an additional delay. This
does not make the heavy Python repository import free, but it removes optional
AI services from the critical chart path.

The promoted stable soak reached a healthy private sidecar 18.5 seconds after
the native process started, while the interactive chart was available after
approximately 18-20 seconds. The backend's own measured startup was 3.06
seconds. This is roughly half the prior approximately 40-second cold visual
baseline; the remaining delay is primarily packaged process and one-directory
file loading rather than Codex/Ollama startup.

### Frontend bundle

Before:

- Main JavaScript: 540.84 kB minified
- Main JavaScript gzip: 163.63 kB

After:

- Main JavaScript: 463.06 kB minified
- Main JavaScript gzip: 146.24 kB

Change:

- Minified main chunk: -14.4%
- Gzip main chunk: -10.6%

Analyze Aspect, Parameter Drawer, Drawing Objects, Square of Nine, and Chakra
Lab now load only when opened.

### Polling

The main workspace previously ran seven independent intervals, with an eighth
1.5-second pair in the open parameter drawer. Requests could overlap when the
backend was busy.

The shared scheduler now:

- never overlaps one task with itself;
- refreshes immediately when enabled or when the window becomes visible;
- uses a minimum 30-second cadence while hidden;
- polls expensive panels quickly only while visible;
- uses the 1.5-second generation cadence only while a job is active;
- avoids duplicate artifact polling while the parameter drawer owns it.

### Chart rendering

The chart previously replaced every candle on every live refresh and recreated
all SR price lines. It now:

- updates only the last/new live bar when the rolling window is compatible;
- falls back to full replacement when symbol, timeframe, source, or window
  actually changes;
- rebuilds SR lines only when their signature changes;
- throttles crosshair legend state updates to one animation frame;
- attaches global drawing-drag listeners once.

This follows Lightweight Charts guidance: use `setData` for replacement and
`update` for real-time last-bar/new-bar changes.

### Logs and local storage

Observed before remediation:

- `tauri_backend_sidecar_error.log`: about 17.1 MB, mostly routine requests.
- `chat_session_backups`: 700 tracked files, about 2.41 GB on disk.
- generated `app_artifacts`: 575 files, about 221.5 MB.

Release 0.10.8 bounds native logs. Artifact and backup retention still need a
separate, explicitly approved policy because those folders may contain useful
research or recovery evidence. No user evidence was deleted by this audit.

## Maintainability Findings

### Decision engine

`reviewer_rule_replay.auto_suggest_case` has Ruff McCabe complexity 24. It is a
high-value deterministic function and should be decomposed into explicit,
independently tested stages:

1. evidence normalization;
2. candidate-entry selection;
3. SR geometry and break confirmation;
4. attribution boundary;
5. Gann-fan candidate evaluation;
6. rule arbitration;
7. outcome comparison and decision trace.

The behavior contract and golden fixtures must be frozen before this refactor.

### Legacy review pack

`build_repeatation_review_pack.py` is 5,422 lines and contains embedded browser
application logic. Three functions exceed the current complexity threshold.
Do not rewrite it in place. First establish parity fixtures, then freeze it
under a legacy boundary while the native Analyze Aspect workspace becomes the
single maintained reviewer.

### Recovery backups

Timestamped backups are useful, but tracking full workspace copies in Git makes
every clone and switch expensive. Future backups should contain only:

- the handoff;
- the audit/release note;
- Git status and recent log;
- changed-file list or patch;
- small schema/manifest evidence needed for recovery.

Historical backup deletion or Git-history rewriting is intentionally outside
this audit and requires explicit approval.

## Verification

Baseline before remediation:

- Python: 226 passed.
- Frontend: 32 passed across 9 files.
- Rust: 2 passed.
- Oxlint, Vite build, Rust formatting, and strict Clippy passed.

0.10.8 final integrated gates completed:

- Python: 229 passed.
- Frontend: 33 passed across 10 files.
- Oxlint: clean.
- TypeScript and Vite production build: passed.
- Focused generation/process tests: 8 passed.
- Private API security tests: 3 passed.
- Changed-Python Ruff lint: clean.
- Rust: 4 passed.
- Rust formatting: passed.
- Strict Clippy with warnings denied: passed.
- Both PyInstaller sidecar and Tauri/NSIS production packaging: passed.
- `git diff --check`: clean apart from expected Windows line-ending notices.

The candidate and promoted stable package each passed all 35 native soak checks
with zero errors and zero failed checks. Both runs verified private API
authentication, timestamp-safe Chakra and candlestick contracts, MT5 read-only
locks, same-port sidecar crash recovery, chart-layout persistence, and zero
genuine descendant survivors:

- candidate:
  `D:\GannFinancialAstro\soak\tauri_0.10.8_20260717_195543\logs\native_soak_report.json`
- stable:
  `D:\GannFinancialAstro\soak\tauri_0.10.8_20260717_202432\logs\native_soak_report.json`

Interactive native QA covered the chart, lazy parameter drawer, Square of
Nine, 81-cell Chakra board, Analyze Aspect second window, Local Jyotish
readiness, and the read-only connected Codex panel. No blank surface, browser
error, clipping, or incoherent overlap was visible at 1482x864. Evidence:

- `gann-astro-desk\docs\visual_qa\gann_astro_desk_0108_main_workspace_20260718.png`
- `gann-astro-desk\docs\visual_qa\gann_astro_desk_0108_chakra_workspace_20260718.png`
- `gann-astro-desk\docs\visual_qa\gann_astro_desk_0108_analyze_codex_20260718.png`

## Stable Release Evidence

- Executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Executable SHA-256:
  `FA28C213D6894CFF8DBCE14F416C24C84446BFFBC7AA457D0D2AAC64EB8C8635`
- Installer SHA-256:
  `1BD1D9B742B0EC0E15B4BE8F4C6D7DF1AD95CD86937029BAC124229B242710BE`
- Sidecar SHA-256:
  `F168417FE656944AEAD827A4D6DEAE90458DE15B22032B7E45BE247DA84BE768`
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.7_20260717T202315Z`
- Pre-promotion writable-state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.8_promotion_20260717T202315Z`
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_015745_product_audit_0108`

## TradingView-Class Roadmap

The app should compete through better evidence provenance and research
workflow, not by cloning every TradingView control.

### Priority 1

1. Timestamp-safe Bar Replay with an immutable evidence cutoff.
2. Drawing favorites, keep-drawing mode, weak/strong magnet, lock/hide-all.
3. Drawing groups and explicit sync scopes: chart, layout, or global.
4. Command palette and documented keyboard map.
5. Watchlist and research alerts that cannot place orders.

### Priority 2

1. Multi-chart layouts with synchronized symbol/time/crosshair/replay options.
2. Drawing templates and per-tool defaults.
3. Measurement, long/short hypothesis, anchored VWAP, and volume profile.
4. Worker-based heavy calculations with versioned result caches.
5. Virtualized tables and on-demand event/astro evidence.

### Priority 3

1. Plugin-style deterministic indicator API.
2. Replay comparison across rule/model versions.
3. Signed research bundles for portable review and reproducibility.
4. Optional execution module only after prospective gates pass, with a separate
   process, permissions, credentials, kill switch, and audit ledger.

## Official Product Guidance Used

- Lightweight Charts real-time updates:
  https://tradingview.github.io/lightweight-charts/tutorials/demos/realtime-updates
- Lightweight Charts `setData` and `update` API:
  https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesApi
- React Suspense:
  https://react.dev/reference/react/Suspense
- Tauri security:
  https://v2.tauri.app/security/
- Tauri capabilities:
  https://v2.tauri.app/security/capabilities/
- TradingView drawing tools:
  https://www.tradingview.com/support/solutions/43000703396-drawing-tools-available-on-tradingview/
- TradingView Bar Replay:
  https://in.tradingview.com/support/solutions/43000474024-how-do-i-turn-bar-replay-on/
- TradingView drawing synchronization:
  https://in.tradingview.com/support/solutions/43000629998-my-drawings-do-not-get-synchronized-across-charts-or-layouts/

## Audit Verdict

The software is substantially stronger after this audit, and the fixes are
appropriate for a 0.10.8 release. It is not yet "best in class" because
prospective validation, replay, drawing ergonomics, and architectural
simplification remain unfinished. The audited native release is complete; the
correct next product move is timestamp-safe Bar Replay, followed by drawing
favorites/magnets/groups/sync and decomposition of the deterministic decision
engine before adding more doctrine or drawing families.
