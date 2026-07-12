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
- Horizontal line, vertical line, Gann fan, and structured annotation tools.
- Persistent chart annotations with exact time, price, family, event, and chart state.
- Read-only MT5 connection supervisor with heartbeat and reconnect status.
- Read-only Codex SDK bridge with deterministic evidence, selected annotation,
  and a local chart screenshot attached to the family task.

## Data Safety

- MT5 order placement is disabled in both the gateway and Codex context.
- Observed outcomes are labeled retrospective and must not enter live inference.
- Provisional astrological values remain labeled provisional.
- New occurrence progress is stored separately from legacy completed reviews.
- Codex threads are family-scoped; local LLM text is never promoted to official evidence.

## Run The Working App

From `D:\PycharmProjects\gann-astro-desk`:

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The backend listens on `8788` and the Codex SDK
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

`src-tauri` contains a Tauri 2 Windows shell and capability policy. Native
development and installer builds still require Rust/Cargo and Microsoft C++
build tools installed on `D:`. The Python backend and Node Codex bridge also need
to be frozen as signed sidecars before the installer can be called portable.
Until that packaging gate is completed, `npm run dev` is the supported runtime.

Custom corrected-TN generation and activation are ready for date ranges covered by the
versioned USDJPY M30/H1 sources. Generated artifacts and their manifests are stored under
`D:\GannFinancialAstro\app_artifacts`; only validated, fully written artifacts enter the
registry. The queue does not yet extend the price snapshot beyond 2026-03-10, so current
or future Jul-2026 event generation still needs a versioned MT5 history-ingestion step.
TT generation remains unavailable and disabled. Deterministic Auto Suggest, trade markers,
P/L, rule lessons, Dream Review, and official-note processing still need to be consolidated
into a shared timestamp-safe, no-lookahead decision engine before live inference.

## Ports And Storage

- UI: `127.0.0.1:5173`
- deterministic backend: `127.0.0.1:8788`
- Codex bridge: `127.0.0.1:8789`
- snapshots: `D:\GannFinancialAstro\app_snapshots`
- corrected data artifacts: `D:\GannFinancialAstro\app_artifacts`
- application source and datasets: `D:\PycharmProjects`
