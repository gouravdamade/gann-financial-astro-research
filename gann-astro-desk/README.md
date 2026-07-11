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

## Ports And Storage

- UI: `127.0.0.1:5173`
- deterministic backend: `127.0.0.1:8788`
- Codex bridge: `127.0.0.1:8789`
- snapshots: `D:\GannFinancialAstro\app_snapshots`
- application source and datasets: `D:\PycharmProjects`
