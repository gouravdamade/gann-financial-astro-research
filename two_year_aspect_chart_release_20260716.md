# USDJPY Two-Year Aspect Chart Release Evidence

Date: 2026-07-16

## Scope

This release prepares a repeatable two-year USDJPY research chart in the native
Windows application. It uses a normalized, immutable MT5 H1 source; displays D1
candles; and overlays the corrected Transit-to-Natal aspect and planetary SR data.
Transit-to-Transit generation remains disabled because its corrected generator is
not yet implemented.

## Source lineage

- User-facing range: 16 July 2024 00:30 IST through 16 July 2026 15:30 IST.
- Snapshot ID: `USDJPY_H1_20260716T115532Z_0fc96b3a`.
- Snapshot contract: `MT5_TIMESTAMP_NORMALIZED_CLOSED_BARS_V2`.
- Snapshot content: 12,421 fully closed H1 bars; one incomplete bar excluded.
- First normalized H1 open: `2024-07-15T19:00:00+00:00`.
- Last normalized H1 open: `2026-07-16T10:00:00+00:00`.
- Last normalized H1 close: `2026-07-16T11:00:00+00:00`.
- Measured MT5 server offset: +10,800 seconds; raw server epochs remain in the
  parquet beside the normalized UTC index.
- Parquet SHA-256:
  `0F3F4039A56FE5D10843E56FE5DAAB8879A46F0090200E5A60144188419A4D75`.
- Promoted price source:
  `mt5_USDJPY_H1_20260716T115532Z_0fc96b3a`.
- Source path:
  `D:\GannFinancialAstro\app_data\price_sources\mt5_USDJPY_H1_20260716T115532Z_0fc96b3a`.

## Corrected aspect artifact

- Generation job: `b439f7561ff547a4ad59d13217bcebde`.
- Artifact ID: `tn_b439f7561ff547a4ad59d13217bcebde`.
- Artifact path:
  `D:\GannFinancialAstro\app_artifacts\tn_b439f7561ff547a4ad59d13217bcebde`.
- Astronomy contract: `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`.
- D1 chart candles returned by the native backend: 627.
- Corrected aspect windows: 2,464 across seven display lanes.
- Deterministic SR touches: 1,569.
- Planetary SR lines: 8.
- Named default layout: `USDJPY 2Y D1 TN aspects`.
- Layout ID: `7dd83eba-73c5-4470-b1ae-f025419fe71c`.
- Aspects and SR layers are enabled. At the full two-year zoom, short windows are
  intentionally narrow; zoom into a quarter or month for readable band labels.

## Viewport defect and correction

The backend returned the complete date range, but Lightweight Charts was configured
with a three-pixel minimum candle spacing. A roughly 1,100-pixel chart therefore
could not display all 627 daily candles and silently clamped the visible span to about
thirteen months. `MIN_CHART_BAR_SPACING` is now 0.5 pixels. The normal default zoom
is unchanged, while an explicit two-year saved range can fit without truncation.

## Verification

- Backend API returned 627 D1 candles from July 2024 through July 2026, 2,464 aspect
  windows, and 8 SR lines.
- Frontend: 20 tests passed, including a two-year viewport capacity regression.
- Oxlint passed.
- TypeScript and Vite production build passed; only the existing chunk-size warning
  remains.
- Prior normalization verification in the same release cycle: all 72 backend tests,
  Ruff, and Python byte compilation passed.
- Candidate native crash/recovery soak passed with no failed checks:
  `D:\GannFinancialAstro\soak\tauri_0.10.3_20260716_125424\logs\native_soak_report.json`.
- Promoted stable-path crash/recovery soak passed with no failed checks:
  `D:\GannFinancialAstro\soak\tauri_0.10.3_20260716_130357\logs\native_soak_report.json`.
- Native visual QA confirmed the x-axis spans July 2024 through July 2026 and the
  aspect layer remains enabled after restart and promotion.
- Every soak confirmed `appExecutionAllowed=false`, `tradeAllowed=false`, and
  read-only MT5 mode.

## Release

- Version: `0.10.3`.
- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
- Executable SHA-256:
  `5B078630CCFE18DF74BB877716ACAE1EC29B3E8FCC6F84189AEDBB5DEEBAE560`.
- Installer SHA-256:
  `27C62BEBF24A64D69A45DBC7D6272A5788B66159A93F123AFDAEAC55D8BF523C`.
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.2_20260716T130240Z`.
- Pre-promotion state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.3_promotion_20260716T130240Z`.

This artifact is retrospective research evidence only. It is not a walk-forward
validation result and cannot authorize MT5 order execution.
