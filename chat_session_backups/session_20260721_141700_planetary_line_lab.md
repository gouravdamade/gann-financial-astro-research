# Session Backup - 2026-07-21 14:17 IST

## User Request

Add a live chart tool that lets the user select different planets and provide
multiple `n`, `f`, and `degree` values per planet. Replot multiple planetary
lines on the current chart immediately for explicit curve-fitting exploration.

## Delivered

- Desktop toolbar action: `Lines` opens the Planetary Line Lab.
- Per-planet controls: enable/disable, color, direct/mirror/both form, and
  comma-separated arrays for `n`, `f`, and `degree`.
- Supported groups: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu,
  Ketu, Uranus, Neptune, Pluto, and `AVG(ALL)`.
- Exact-bar Raman sidereal positions from the existing financial ephemeris.
- Direct formula: `f * n * degree + f * longitude`.
- Mirror formula: `f * n * degree + f * (360 - longitude)`.
- Cartesian combinations create distinct simultaneous lines for each parameter
  set. The overlay recomputes after 260 ms and on viewport/live-bar changes.
- Direct lines are solid; mirror lines are dashed. Independent series preserve
  candlestick autoscale. The settings persist in saved chart layouts.
- Backend endpoint: `POST /api/planetary-lines` under contract
  `GANN_EXPLORATORY_PLANETARY_LINE_OVERLAY_V1`.
- Tauri companion gateway admits the endpoint as read-only ChartRead.

## Safety Boundary

This is an exploratory visualization only. It is excluded from Auto Suggest,
live inference, review/shadow ledgers, and every execution path. Limits are
1,200 bar timestamps, 96 lines, 100,000 points, and 12 values per input array.
Any future trading use requires separate, timestamp-safe out-of-sample
validation.

## Key Files

- `gann-astro-desk/backend/planetary_lines.py`
- `gann-astro-desk/backend/test_planetary_lines.py`
- `gann-astro-desk/src/planetaryLines.ts`
- `gann-astro-desk/src/usePlanetaryLineOverlay.ts`
- `gann-astro-desk/src/components/PlanetaryLinePanel.tsx`
- `gann-astro-desk/src/components/MarketChart.tsx`
- `gann-astro-desk/src/views/MainWorkspace.tsx`
- `gann-astro-desk/src-tauri/src/companion_gateway.rs`

## Verification

- Backend: `115/115` passed.
- Frontend: `22` files and `71` tests passed.
- Production frontend build and lint passed.
- Packaged soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.18_20260721_054426\logs\native_soak_report.json`
  including planetary-line contract, formula rendering, and execution-lock
  assertions.

## Candidate Build

- Directory:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.18-tauri`
- Portable EXE SHA-256:
  `56736492C535B5E16F8C02DEE816F195BB40F1AC3EC2F52AE8F2302A50CD0CAC`
- Installer SHA-256:
  `D9E012E7C6B5EAEB1C4C56D4BF38F433C9F566CBE1D47C45F52AB65DAACD9A6D`
- Stable `0.10.14` is not modified.

## Git Scope

Do not add the runtime-only files below when committing source changes:

- `gann_aspect_annotations_raman_v2.sqlite`
- `candlestick_shadow_v3.sqlite`
- `logs/`
- `tryapp-android/`

## Suggested Next Work

Use the overlay visually during research, then define a separately versioned,
no-lookahead scoring study before any candidate line configuration becomes an
input to Auto Suggest or execution.
