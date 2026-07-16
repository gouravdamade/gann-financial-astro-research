# Timeframe-Aware Aspect Policy Release 0.10.6

Date: 2026-07-17 IST

## Scope

Gann Astro Desk now changes aspect visibility with the selected chart timeframe.
Corrected event timestamps remain canonical; the chart does not stretch, round,
or regenerate an aspect when the user changes timeframe.

Automatic mode requires an aspect to last for at least one complete selected bar:

- M30: 30 minutes
- H1: 60 minutes
- H4: 240 minutes
- D1: 1,440 minutes
- W1: 10,080 minutes

The parameter drawer exposes the applied minimum and retains a manual mode for
explicit research thresholds.

## Data Contracts

- Historical H4 and D1 candles continue to be deterministic H1 resamples.
- Historical W1 candles are Monday-anchored H1 resamples using left-closed,
  left-labeled weekly boundaries.
- MT5 live W1 uses the terminal's native `TIMEFRAME_W1` bars.
- Corrected W1 source generation still captures H1 bars so event timestamps and
  lower-timeframe evidence remain available; W1 is a view/filter contract.
- Switching timeframe preserves an event's original start/end timestamps when
  that event remains eligible at the new duration threshold.

## Verification

- Frontend: 30 tests passed across 8 files.
- Backend: 83 tests passed, including focused policy, W1 resampling, repository,
  and MT5 gateway coverage.
- Oxlint passed.
- TypeScript and Vite production build passed. Vite retained only the existing
  advisory about the main JavaScript chunk exceeding 500 kB.
- Python byte compilation passed.
- Packaged native QA used the same 3-17 July 2026 range and observed:
  - H1: 43 visible aspects, minimum 1 hour.
  - D1: 12 visible aspects, minimum 1 day.
  - W1: 0 visible aspects, minimum 1 week, with two Monday-anchored candles.
  The same Mars-to-Mercury event remained selected between H1 and D1 because its
  canonical window qualified for both; W1 correctly cleared selection because no
  event in that range lasted a full week.
- The parameter drawer displayed `W1 minimum 1w` and the disabled automatic value
  `10080`; manual override remained available.
- The first candidate soak stopped at the external MT5 clock-normalization gate
  while a MetaTrader LiveUpdate notice was blocking the connected terminal. No
  release files were promoted. After dismissing the deferred-update notice, the
  unchanged candidate passed all 28 checks with zero errors:
  `D:\GannFinancialAstro\soak\tauri_0.10.6_20260716_212702\logs\native_soak_report.json`.
- The promoted stable copy passed the same 28 checks with zero errors:
  `D:\GannFinancialAstro\soak\tauri_0.10.6_20260716_214509\logs\native_soak_report.json`.

## Release

- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Executable SHA-256:
  `92321E9F689D5D4CC104793E9D5F1FD8CB5C1DED80FD784CC4553F7F39C9A81F`
- Installer SHA-256:
  `F0F2DD3A2688EB680979AC40B45E1B4BF9D537F551BF487FA128F76B0BCF92C7`
- Backend sidecar SHA-256:
  `8074A56297A9CD4E4A2BB5A21DD246F168CFABA02F2B6F16FB53D3227E5051C0`
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.5_20260716T214414Z`
- Pre-promotion state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.6_promotion_20260716T214204Z`

MT5 remains read-only market data. Trade execution remains locked.
