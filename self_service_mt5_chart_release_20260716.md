# Self-Service MT5 Historical Chart Release - 2026-07-16

## Result

Gann Astro Desk `0.10.4` can fetch an arbitrary supported MT5 symbol and date
range without a new code change. The Research section in Astro Layers now has a
single `Fetch MT5 and build aspects` command that:

1. requests fully closed bars from the connected MT5 terminal;
2. writes and verifies an immutable timestamp-normalized snapshot;
3. promotes that snapshot into a versioned price source;
4. bounds generation to the broker's actual available range;
5. queues corrected transit-to-natal generation with automatic activation; and
6. opens the completed symbol/timeframe chart through the existing workspace.

H4 and D1 charts use H1 source bars. M30 uses native M30 source bars. A single
corrected job supports up to five years, so four years is one request. Snapshot
capture supports up to twenty years; corrected studies longer than five years
must be split into bounded jobs.

## Instrument and reference safeguards

- MT5 symbols are no longer restricted to USDJPY. Normal broker instrument
  characters (`.`, `_`, and `-`) are accepted; malformed/path-like symbols are
  rejected before generation.
- The active chart payload must match the active artifact symbol. An older
  symbol cannot be returned beneath a newly selected label.
- A non-USDJPY asset must provide a distinct birth/IPO reference label and
  distinct date/time/UTC-offset/location values. Merely renaming the USDJPY
  reference is rejected.
- Non-USDJPY generation sends `--disable-base-reference`, preventing the legacy
  USD base-reference evidence from entering a single-asset chart.
- Corrected TT remains disabled. This release generalizes the corrected TN path
  only.

## MT5 clock and broker coverage

The clock validator uses the clock probe's frozen validation symbol to measure
the account/server offset, then records when that server-wide offset is applied
to a different requested symbol. Evidence includes `validationSymbol`,
`requestedSymbol`, and `crossSymbolOffsetApplication`; no fixed offset is
guessed.

Requested dates are intersected with the promoted source's real first and last
closed bars. A 72-hour edge tolerance avoids calling an ordinary weekend a
history failure. A larger shortfall is reported as partial broker coverage and
the chart is bounded to the data actually received.

## Live non-forex proof

A read-only four-year AAPL H1 capture succeeded against MetaQuotes-Demo:

- snapshot: `AAPL_H1_20260716T143525Z_b6b6c31e`;
- requested: `2022-07-16T00:00:00Z` through
  `2026-07-16T14:35:25Z`;
- actual closed-bar coverage: `2022-07-18T13:00:00Z` through
  `2026-07-16T14:00:00Z`;
- 7,219 fully closed H1 bars and one incomplete bar excluded;
- measured server offset: `+10,800` seconds;
- validation symbol: USDJPY; requested symbol: AAPL;
- parquet SHA-256:
  `1790159A9AF19A2A76DB562717DC3290CE76530CC7726DB2B3C1C03F49D46314`.

Evidence remains isolated under
`D:\GannFinancialAstro\validation\mt5_self_service_20260716` and did not change
the active research chart or place an order.

## Verification

- frontend: 24 tests passed;
- backend: 78 tests passed, including a real non-USDJPY generation smoke and a
  label-only reference-inheritance rejection;
- Oxlint, TypeScript/Vite production build, Ruff, Python byte compilation, and
  `git diff --check` passed;
- native candidate visual QA showed the command and help text without overlap;
- final candidate crash/recovery soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.4_20260716_165645\logs\native_soak_report.json`;
- final promoted-stable crash/recovery soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.4_20260716_170035\logs\native_soak_report.json`.

Both soaks verified read-only MT5 mode, fresh clock normalization, sidecar
restart on the same port, saved-layout survival, execution locks, and no
surviving descendants.

## Native release and rollback

- stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
- executable SHA-256:
  `1E265FD427D15A8BEFBF3516A7638E16FD1AC6E19C8AA549B7AF68A62A2C6151`;
- installer SHA-256:
  `2E95ED8B66FB34D712DE1C63888634C63319F2276EAF31962C6D1C6D851F599A`;
- backend sidecar SHA-256:
  `059AD2BEC18944181AA0602940251CA5520ED2F44F156665DA242ED4C1887950`;
- previous stable archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.3_20260716T150745Z`;
- pre-final state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.4_final_promotion_20260716T165918Z`.

## Safety

This is a market-data and research workflow only. `tradeAllowed=false`, app
execution remains locked, and no chart-generation control can place an MT5
order. A successful historical chart is research evidence, not walk-forward
certification or a trading recommendation.
