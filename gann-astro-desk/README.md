# Gann Astro Desk

Gann Astro Desk is the Windows desktop surface for the private USDJPY Gann and
financial-astrology research workspace. The current vertical slice uses the
corrected Raman transit-to-natal source contract and keeps retrospective review
separate from live market-data concerns.

## Implemented

- Real USDJPY H1 candlesticks from the versioned MT5 parquet source.
- A chart-first market-terminal shell with a compact command bar, fixed OHLC readout,
  TradingView-style drawing rail, focus mode, collapsible inspector/activity dock,
  aspect and SR visibility toggles, and a persistent read-only status bar.
- A proximity-revealed chart navigation dock provides backward/forward movement and
  centered zoom in/out without occupying the chart when the pointer is elsewhere.
  Each move advances one-quarter of the visible range, respects candle boundaries,
  supports keyboard focus, and persists through the active named layout.
- Durable workspace layout preferences stored in the native application database, so
  panel and layer visibility survive the random private-port change on every launch.
- Directional transit-to-natal aspect windows from the corrected 1,268-event source.
- Planetary SR lines joined from the corrected 754-row touch artifact.
- Clickable aspects with a detachable Analyze Aspect family window.
- Previous/next recurrence navigation, evidence filters, and review progress.
- Persistent parameter profiles covering market source, M30/H1/H4/D1/W1, date range,
  TN body/aspect filters, family exclusions, duration/touch filters, planetary SR
  inputs, and birth/IPO reference coordinates.
- Timeframe-aware aspect visibility keeps corrected event timestamps canonical while
  requiring each visible aspect to last at least one selected chart bar: 30 minutes
  on M30, one hour on H1, four hours on H4, one day on D1, and one week on W1.
  Researchers can disable the automatic policy and enter an explicit duration minimum.
- Durable corrected-TN generation jobs with validated rebuild inputs, visible stage
  progress, cancellation, restart recovery, isolated worker processes, and inspectable logs.
- A versioned corrected-data artifact registry with SHA-256 manifests, contract validation,
  explicit activation/history controls, and atomic chart/Analyze Aspect dataset swaps.
- Automatic research-chart refresh when a completed job activates its artifact, including
  when the parameter drawer has been closed while generation continues in the background.
- Read-only MT5 live chart mode with 20-5,000 recent bars and five-second refresh.
- Immutable MT5 history snapshots with capture/as-of timestamps, closed-bar-only
  filtering, SHA-256 manifests, and explicit no-lookahead provenance. New V2
  snapshots preserve raw server epochs while indexing bars by UTC derived from a
  fresh measured `TimeTradeServer-TimeGMT` probe; stale or inconsistent clock
  evidence fails closed before a file is written.
- Explicit snapshot promotion with deterministic manifest/OHLC/hash verification,
  immutable price-source registration, and retained snapshot lineage in generated artifacts.
- Horizontal line, vertical line, Gann fan, and structured annotation tools on the market
  chart. Unlocked lines and fan anchors can be selected, dragged, edited numerically,
  hidden, locked, renamed, styled, or deleted; `Delete` removes the selected object and
  `Escape` clears selection.
- Versioned named chart layouts with debounced autosave, exact UTC-time/price anchors,
  restore, Save As, object tree, undo, lock/hide, drawing templates, and JSON
  export/import. Analyze Aspect layouts are family-scoped and persist while navigating
  recurrences.
- A separate Square of Nine workspace tab keeps the wheel away from candlesticks. It
  supports price, time, date, and date-time values; editable first value; signed
  increment/decrement; time units; center-inclusive size; number and angle rotation;
  zoom; value lookup; clickable High/Low/Forecast/Error marks; per-cell notes; PNG export;
  and named-layout persistence. Legacy chart-overlay squares migrate into this workspace.
- Persistent chart annotations with exact time, price, family, event, and chart state.
- Read-only MT5 connection supervisor with heartbeat and reconnect status.
- One versioned decision-packet contract shared by retrospective Auto Suggest and
  native live inference, with the mode and evidence cutoff recorded on every packet.
- A timestamp-safe Analyze Aspect inference panel that uses only closed candles and
  allowlisted touch/astrology fields, emits watch or abstain, and never materializes
  an entry, exit, P/L, outcome, or order.
- An automatic prospective shadow supervisor that accepts only a fresh, non-baseline
  corrected artifact whose promoted MT5 snapshot contains a just-closed SR touch.
- An automatic closed-bar refresh supervisor that waits for a genuinely recent MT5 bar,
  captures and promotes an immutable price snapshot, queues the corrected Raman generator,
  activates only a fully verified artifact, and then wakes the prospective ledger. Market
  closures and stale bars are reported without manufacturing an artifact.
- An always-visible Auto Refresh control reports the closed-bar supervisor state and can
  request the same guarded check immediately; it cannot bypass recency, finalization,
  price-source verification, artifact validation, or the execution lock.
- A SQLite append-only hash-chain ledger that records the exact decision packet first,
  then appends a separate outcome only after the first closed MT5 bar reaches the
  72-hour horizon. Watches, abstentions, coverage, confidence interval, p-value, and
  directional return remain inspectable in the Shadow validation dock.
- An immutable one-row prospective-trial manifest locks the first cohort's decision
  contract, engine, policy, Raman astronomy contract, symbol, timeframe, 72-hour horizon,
  and statistical thresholds. A mismatched future cohort is rejected instead of being
  silently mixed into the sample; the dock shows the fingerprint, 100-cluster/four-month
  progress, next eligible settlement, and any due outcome backlog.
- Read-only Codex SDK bridge with deterministic evidence, selected annotation,
  and a local chart screenshot attached to the family task.
- A native Local Jyotish tab backed by the portable Ollama runtime and 5,178 packaged
  classical/reference/research corpus chunks. Retrieval separates classical doctrine,
  secondary commentary, and same-family local memory. Every response is an untrusted draft
  with visible citations and deterministic verifier findings.
- A separate Candles tab with a dedicated three-chunk method/evidence/provenance corpus
  and the versioned `GANN_CANDLESTICK_EVIDENCE_V1` packet.
  It measures only closed-bar OHLC geometry at the selected cutoff, reports transparent
  body/wick/trend/ATR formulas, and places post-cutoff bars in an explicitly retrospective
  section. Its dedicated local-RAG prompt, corpus, citations, verifier, model setting, and
  API contract remain isolated from the Jyotish specialist.

## Data Safety

- MT5 order placement is disabled in both the gateway and Codex context.
- Observed outcomes are labeled retrospective and must not enter live inference.
- Retrospective marker replay declares its outcome/future-path use and is always
  ineligible for live execution; the native API rejects replay-mode requests.
- Live packets reject unclosed touch candles, out-of-window touches, future price
  evidence, outcome labels, fill/exit values, and decisions outside their deadline.
- The frozen v1 policy failed its first purged/embargoed retrospective statistical
  gate (54.26% across 258 unique watch clusters; its 95% interval crossed 50%).
  Every packet and Analyze Aspect panel carries that research-only validation lock.
- Historical/baseline and stale generated touches are rejected from the prospective
  ledger instead of being backfilled. Ledger rows cannot be updated or deleted through
  SQLite while their sequence and payload hashes make offline tampering detectable.
- The prospective-trial manifest is also protected against SQL update/delete. Existing
  pre-manifest decisions seed it once during the schema-v2 upgrade only when they form one
  internally consistent policy cohort.
- Provisional astrological values remain labeled provisional.
- New occurrence progress is stored separately from legacy completed reviews.
- Manual chart geometry and the standalone Square of Nine workspace are research-only.
  Their persistence contract forces live-inference, shadow-ledger, and execution
  consumption off.
- Codex threads are family-scoped; local LLM text is never promoted to official evidence.
- Local Jyotish drafts are never consumed by live inference or the shadow ledger. The app
  defaults to `qwen2.5:3b`; the installed Gemma 12B model remains optional because it did not
  load reliably on the current GTX 1060 runtime during verification.
- Candlestick names are conditional geometry hypotheses, not signals. Candlestick evidence
  and drafts cannot enter Auto Suggest, live inference, the shadow ledger, official ML notes,
  or execution. Published evidence is mixed, so every target market and timeframe still
  requires purged no-lookahead validation.

## Run The Windows App

Launch the portable native executable:

```text
D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe
```

Keep the executable beside its `_internal` directory. The app creates a native
WebView2 window, chooses private random loopback ports for its internal services,
and stores writable state under `D:\GannFinancialAstro\app_data`. No browser URL
is part of the user workflow.

To rebuild the release entirely on `D:`:

```powershell
cd D:\PycharmProjects\gann-astro-desk
.\packaging\build_tauri_windows.ps1
```

The release manifest records the executable hash, bundled file count, astronomy
contract, and read-only MT5 execution policy.

## Development Runtime

From `D:\PycharmProjects\gann-astro-desk`:

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173` only for development. The backend listens on `8788` and the Codex SDK
bridge on `8789`. Set `GANN_ASTRO_MT5_AUTOCONNECT=0` before starting when MT5
market data is intentionally not required.

The Codex bridge uses the local Codex login and does not require an OpenAI API key.

## Fetch any MT5 research range with aspects

1. Open `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
2. Open **Astro layers**, select **Research**, enter the exact broker symbol, chart
   timeframe, and requested start/end dates. For a non-USDJPY asset, enter its own
   birth/IPO date, time, UTC offset, latitude, longitude, and reference label.
3. Choose the TN planets/aspects and press **Fetch MT5 and build aspects**. The app
   automatically captures fully closed bars, verifies an immutable normalized
   archive, promotes it, generates corrected TN evidence, and activates the chart.
   H4 and D1 views use H1 source bars; M30 uses M30 source bars.
4. The completion message states whether MT5 covered the whole request. If the
   broker returned less history, generation is bounded to the actual available
   range instead of silently claiming full coverage.
5. Leave **Aspects** and **SR** enabled and save a named layout for reuse. At a
   multi-year zoom, zoom into a quarter or month to read short aspect bands.

One corrected generation job supports up to five years, so a four-year chart is a
single request. MT5 snapshot capture itself permits up to twenty years; split a
longer corrected study into ranges no greater than five years. The older manual
snapshot, verify/promote, and generation controls remain available for audits.

MT5 remains data-only throughout this workflow. Capturing, promoting, generating,
and activating research data cannot place an order.

## Verify

```powershell
npm run lint
npm test
npm run test:backend
npm run build
```

## Native Windows Status

The current native source version is `0.10.9`; the promoted Windows release is at
`D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`. It includes the
timestamp-safe Sarvatobhadra Chakra Lab as read-only guidance. The Chakra
surface contains no order action, cannot consume market data, and reports
`execution_allowed=false` and `financially_validated=false`.

Release `0.10.9` restores parity with the development tool rail. Its
`GANN_CHART_TOOL_RAIL_V2` manifest locks select, crosshair, annotation,
horizontal/vertical lines, Gann fan, Fibonacci, favorites, OHLC magnet,
keep-drawing, undo, reset, and clear. Native visual evidence is stored at
`docs\visual_qa\gann_astro_desk_0109_tool_rail_parity_20260718.png`.

The promoted-release soak passed all application checks. On a closed market,
the optional `-AllowClosedMarketMt5Defer` soak flag may defer only the exact
stale MT5 fresh-tick check while read-only mode and the execution lock are both
confirmed. The default soak remains fail-closed.

The supported native build is Tauri 2 / Rust with a managed PyInstaller Python sidecar
and the installed Microsoft WebView2 runtime. It bundles the frontend, corrected data,
Swiss Ephemeris files, Python research workers, Node runtime, Codex SDK bridge, Local
Jyotish corpus, Candlestick Specialist corpus, and the transparent frozen USDJPY H1
candlestick-shadow model. Ollama models remain under
`D:\Ollama\models` and are not duplicated inside the release. Analyze Aspect opens as
a second native Tauri window rather than an external browser.

The native shell gives each launch a random private API token in addition to its random
loopback port. Generator workers run as separate child processes so CPU-heavy astronomy
rebuilds cannot monopolize the HTTP sidecar. Codex starts after the chart backend is ready
and Ollama warm-up is deferred briefly, keeping optional AI startup out of the chart's
critical path. Routine Werkzeug access lines are suppressed and native sidecar logs rotate
at 10 MiB with three retained backups.

The frontend uses visibility-aware, non-overlapping polling. Hidden windows pause fast
refreshes; expensive shadow/diagnostic resources refresh quickly only while their panel is
open; generation jobs use the 1.5-second cadence only while work is active. Live charts use
incremental last-bar updates when the visible MT5 window has not shifted, while research
surfaces and detachable analysis code load in separate chunks.

Rust/Cargo are installed under `D:\Rust`; Visual Studio Build Tools are primarily under
`D:\VisualStudio`. The build produces a portable release tree and NSIS installer while
the Rust shell owns random private loopback ports, sidecar recovery, and descendant
cleanup. Python doctrine and evidence engines remain behind typed local contracts rather
than being rewritten merely for language uniformity.

Custom corrected-TN generation and activation are ready for date ranges covered by the
versioned USDJPY M30/H1 sources. Generated artifacts and their manifests are stored under
`D:\GannFinancialAstro\app_artifacts`; only validated, fully written artifacts enter the
registry. Immutable MT5 snapshots can be promoted explicitly into verified price sources;
generation records the selected source ID, source snapshot, SHA-256 and as-of cutoff, and
activation switches chart candles atomically while preserving baseline restoration.
TT generation remains unavailable and disabled. Deterministic Auto Suggest and native
live inference now share `GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1`; retrospective trade
markers, P/L, rule lessons, Dream Review, and official-note processing remain research-only.
Live inference is deliberately watch/abstain-only. The retrospective gate failed, and order
execution remains blocked while the append-only prospective trial collects evidence and
external astrology certification remains incomplete.

The separate `Candle shadow` dock is a prospective research observer, not the astrology
shadow trial. It records only the latest fully closed USDJPY H1 candle when the app sees
that close within the frozen 15-minute grace window; missed hours are never recreated.
Decisions and six-actual-bar outcomes are append-only and hash chained in
`D:\GannFinancialAstro\app_data\candlestick_shadow_v3.sqlite`. A packaged read-only MQL5
service records fresh `TimeTradeServer`, `TimeGMT`, Python-comparable tick, and H1 bar
evidence. V3 measures the broker/server offset from that evidence, normalizes raw MT5
epochs to UTC, preserves both raw and normalized timestamps in every row, and fails closed
without append if the probe is missing, stale, inconsistent, or off its validation grid.
It never guesses or hardcodes a three-hour correction. The failed named-pattern
primary remains visible, the raw-geometry model is diagnostic only, and neither can feed
Auto Suggest, rules, official notes, the coordinator, or MT5 execution.

## Storage

- native executable: `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- native writable state: `D:\GannFinancialAstro\app_data`
- timestamped MT5 history: `D:\GannFinancialAstro\app_data\market_snapshots`
- promoted price sources: `D:\GannFinancialAstro\app_data\price_sources`
- snapshots: `D:\GannFinancialAstro\app_snapshots`
- corrected data artifacts: `D:\GannFinancialAstro\app_artifacts`
- application source and datasets: `D:\PycharmProjects`
