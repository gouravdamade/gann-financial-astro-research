# Gann Astro Desk

Gann Astro Desk is the Windows desktop surface for the private USDJPY Gann and
financial-astrology research workspace. The current vertical slice uses the
corrected Raman transit-to-natal source contract and keeps retrospective review
separate from live market-data concerns.

## Implemented

- Real USDJPY H1 candlesticks from the versioned MT5 parquet source.
- Directional transit-to-natal aspect windows from the corrected 1,268-event source.
- Planetary SR lines joined from the corrected 754-row touch artifact.
- Clickable aspects with a detachable Analyze Aspect family window.
- Previous/next recurrence navigation, evidence filters, and review progress.
- Persistent parameter profiles covering market source, M30/H1/H4/D1, date range,
  TN body/aspect filters, family exclusions, duration/touch filters, planetary SR
  inputs, and birth/IPO reference coordinates.
- Durable corrected-TN generation jobs with validated rebuild inputs, visible stage
  progress, cancellation, restart recovery, isolated subprocesses, and inspectable logs.
- A versioned corrected-data artifact registry with SHA-256 manifests, contract validation,
  explicit activation/history controls, and atomic chart/Analyze Aspect dataset swaps.
- Automatic research-chart refresh when a completed job activates its artifact, including
  when the parameter drawer has been closed while generation continues in the background.
- Read-only MT5 live chart mode with 20-5,000 recent bars and five-second refresh.
- Immutable MT5 history snapshots with capture/as-of timestamps, closed-bar-only
  filtering, SHA-256 manifests, and explicit no-lookahead provenance.
- Explicit snapshot promotion with deterministic manifest/OHLC/hash verification,
  immutable price-source registration, and retained snapshot lineage in generated artifacts.
- Horizontal line, vertical line, Gann fan, and structured annotation tools.
- Persistent chart annotations with exact time, price, family, event, and chart state.
- Read-only MT5 connection supervisor with heartbeat and reconnect status.
- One versioned decision-packet contract shared by retrospective Auto Suggest and
  native live inference, with the mode and evidence cutoff recorded on every packet.
- A timestamp-safe Analyze Aspect inference panel that uses only closed candles and
  allowlisted touch/astrology fields, emits watch or abstain, and never materializes
  an entry, exit, P/L, outcome, or order.
- Read-only Codex SDK bridge with deterministic evidence, selected annotation,
  and a local chart screenshot attached to the family task.

## Data Safety

- MT5 order placement is disabled in both the gateway and Codex context.
- Observed outcomes are labeled retrospective and must not enter live inference.
- Retrospective marker replay declares its outcome/future-path use and is always
  ineligible for live execution; the native API rejects replay-mode requests.
- Live packets reject unclosed touch candles, out-of-window touches, future price
  evidence, outcome labels, fill/exit values, and decisions outside their deadline.
- Provisional astrological values remain labeled provisional.
- New occurrence progress is stored separately from legacy completed reviews.
- Codex threads are family-scoped; local LLM text is never promoted to official evidence.

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
.\packaging\build_windows_exe.ps1
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

## Verify

```powershell
npm run lint
npm test
npm run test:backend
npm run build
```

## Native Windows Status

The supported native build is a PyInstaller one-folder release using pywebview and
the installed Microsoft WebView2 runtime. It bundles the frontend, corrected data,
Swiss Ephemeris files, Python research workers, Node runtime, and Codex SDK bridge.
Analyze Aspect opens as a second native window rather than an external browser.

`src-tauri` remains an optional future shell. A Tauri/MSI route would require Rust,
Cargo, and Microsoft C++ Build Tools; those are not required by the working release.
Rust can be placed on `D:` through `RUSTUP_HOME` and `CARGO_HOME`. Visual Studio can
place most workloads and download caches on `D:`, but Microsoft still reserves some
shared installer and Windows SDK servicing files on the system drive.

Custom corrected-TN generation and activation are ready for date ranges covered by the
versioned USDJPY M30/H1 sources. Generated artifacts and their manifests are stored under
`D:\GannFinancialAstro\app_artifacts`; only validated, fully written artifacts enter the
registry. Immutable MT5 snapshots can be promoted explicitly into verified price sources;
generation records the selected source ID, source snapshot, SHA-256 and as-of cutoff, and
activation switches chart candles atomically while preserving baseline restoration.
TT generation remains unavailable and disabled. Deterministic Auto Suggest and native
live inference now share `GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1`; retrospective trade
markers, P/L, rule lessons, Dream Review, and official-note processing remain research-only.
Live inference is deliberately watch/abstain-only until purged out-of-sample validation and
external astrology certification are complete.

## Storage

- native executable: `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- native writable state: `D:\GannFinancialAstro\app_data`
- timestamped MT5 history: `D:\GannFinancialAstro\app_data\market_snapshots`
- promoted price sources: `D:\GannFinancialAstro\app_data\price_sources`
- snapshots: `D:\GannFinancialAstro\app_snapshots`
- corrected data artifacts: `D:\GannFinancialAstro\app_artifacts`
- application source and datasets: `D:\PycharmProjects`
