# MT5 Server-Time Normalization Release - 2026-07-16

## Scope

Gann Astro Desk 0.10.2 replaces the unusable raw-UTC assumption in the
prospective USDJPY H1 candlestick observer with measured, fresh MT5 clock
evidence. The change remains observation-only. It does not authorize orders or
feed candle output into astrology rules, Auto Suggest, official ML notes, the
coordinator, or live execution.

## Root cause

The Windows clock and timezone were correct for IST, but the connected
MetaQuotes-Demo feed encoded tick and bar epochs on a server clock exactly
10,800 seconds ahead of GMT. Treating those raw epochs as UTC made the prior V2
clock lock fail by about three hours.

The correction is not a hardcoded `-3h`. A read-only MQL5 service records
`TimeTradeServer`, `TimeGMT`, `TimeLocal`, `TimeGMTOffset`, the USDJPY tick
timestamp, and the current H1 bar timestamp every two seconds. V3 derives the
server offset from `TimeTradeServer - TimeGMT`, cross-checks it against the
Python tick/bar feed and UTC, and preserves both raw server epochs and normalized
UTC in every decision and outcome.

Relevant MetaTrader documentation:

- https://www.mql5.com/en/docs/dateandtime/timetradeserver
- https://www.mql5.com/en/docs/dateandtime
- https://www.mql5.com/en/docs/constants/structures/mqltick
- https://www.mql5.com/en/docs/series/copytime
- https://www.mql5.com/en/book/applications/script_service/services
- https://www.mql5.com/en/docs/files/fileopen
- https://www.mql5.com/en/docs/files/filemove

## Contracts and safeguards

- Clock probe: `GANN_MT5_CLOCK_PROBE_V1`
- Time normalization: `GANN_MT5_SERVER_TIME_NORMALIZATION_V1`
- Ledger: `GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V3`
- Decision: `GANN_CANDLESTICK_PROSPECTIVE_DECISION_V3`
- Six-bar outcome: `GANN_CANDLESTICK_PROSPECTIVE_6BAR_OUTCOME_V3`
- Trial: `GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V3`
- Trial ID:
  `FD210BB9F2AD1287E23A5BFF526DD65E4C1AAF8832D0F5274805CFBB3065E0DA`

The probe must be no more than 30 seconds old. The measured offset must be on a
15-minute grid, within plus or minus 14 hours, and internally consistent. MQL5
and Python tick timestamps must agree within five seconds, their H1 timestamps
within one hour, and the normalized tick within five minutes of observed UTC.
Any missing, stale, drifting, mismatched, or invalid evidence causes
`skip_without_append`. Missed H1 decisions remain permanently missed.

The MQL5 source contains no order or position functions. The deployed service
binary and source are hash-matched to the packaged files. Terminal/account Algo
Trading permissions are reported honestly in the UI, while the application
continues to expose `appExecutionAllowed=false`, `tradeAllowed=false`, and
`executionMode=read_only_market_data`.

## Live evidence

At `2026-07-16T08:00:16.821622Z`, V3 captured its first genuine prospective
decision 16 seconds after the 08:00 UTC H1 close:

- Decision ID:
  `6F317AD1E5A734AE606B040CA747C9E8172CC7DB94C1FA126EA7452165B73AB0`
- Decision bar open: `2026-07-16T07:00:00Z`
- Feature available: `2026-07-16T08:00:00Z`
- Measured server offset: `+10,800` seconds
- Probe age: about 2.8 seconds
- Primary action: `abstain`
- Probability up: `0.4953679816`
- App execution allowed: `false`

The later scan correctly reported that the same close was too old and did not
append a duplicate. The V3 chain has one immutable decision and no outcome yet:

`D:\GannFinancialAstro\app_data\candlestick_shadow_v3.sqlite`

Its post-capture SHA-256 is:

`99F91BDD9EC4CD55D13656B29AD71847550FD8ACD8F693BD26F90899AC74AC04`

The prior V2 database was not opened or rewritten. Its SHA-256 remains:

`98F58DE7D8EA7CB4588C1B187430EBDEA29297B8A32905B91D4D476F2B1EA4B2`

## Verification

- 19 focused timestamp, ledger, and MT5 gateway tests passed.
- The complete backend suite passed: 71 tests.
- Ruff and Python byte compilation passed.
- Frontend passed 18 tests in five files, lint, TypeScript, and Vite production
  build.
- PowerShell packaging scripts parsed successfully.
- MQL5 compiled with zero errors and zero warnings; packaged/deployed EX5 SHA-256:
  `B8D0C36A90E133EF08E151899A9AA82633FA5DC335E0110D09573CE56B21347F`.
- Candidate native crash/recovery soak passed every check:
  `D:\GannFinancialAstro\soak\tauri_0.10.2_20260716_082809\logs\native_soak_report.json`.
- Promoted stable-path crash/recovery soak passed every check:
  `D:\GannFinancialAstro\soak\tauri_0.10.2_20260716_083516\logs\native_soak_report.json`.
- Native visual QA showed `MT5 data only`, terminal Algo Trading state, app
  execution locked, measured `server +03:00`, near-zero normalized skew, fresh
  probe age, and the captured decision.

## Promoted release

- Stable directory: `D:\GannFinancialAstro\release\GannAstroDesk`
- Executable SHA-256:
  `0CD1A63D851A89DC20185BB7D9013C8A4598D340A396BB68C5D8F6EEEC5538A2`
- Installer SHA-256:
  `B88F807EA0001787C6CBD523C46F7A8E9B572180AEA928D2F45B00A5A2CD2DA8`
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.1_20260716T083400Z`
- Pre-promotion state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.2_promotion_20260716T083400Z`

## Next gate

Keep V3 running unchanged for at least 48 hours to audit probe continuity,
offset stability, and cross-process consistency, then continue accumulating the
longer untouched prospective cohort. The primary candlestick model still fails
its retrospective promotion gate, so valid timestamps do not convert abstentions
into trade authorization. Do not backfill, retune from prospective observations,
or enable execution.
