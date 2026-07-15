# Prospective Candlestick Shadow Release - 2026-07-15

## Scope

Gann Astro Desk 0.10.1 adds a separate, timestamp-safe USDJPY H1
candlestick-shadow cohort. It is an observation system only. It cannot feed
astrology rules, Auto Suggest, official ML notes, the coordinator, or MT5
execution.

## Frozen model

- Artifact contract: `GANN_CANDLESTICK_FROZEN_MODEL_ARTIFACT_V1`
- Artifact ID:
  `9FF4EE79619351C75C1B0931F3528603F3EDA0FC02E91BB0B4B5596DC798C9E6`
- Artifact SHA-256:
  `3A97FEEE826127D221A101262B806203A2EE717082329F9E2455BF3CAF359F9C`
- Primary named-pattern model ID:
  `DC7ED62B864E538A86C83B862D11E8361AF83FD1C6EA58B89A839918BF53FE1D`
- Diagnostic raw-geometry model ID:
  `8E633BCB3DCB0237412606D86ABED7E85BF90191B152C8659DA60100064478E8`
- Fit rows: 99,973 historically label-available rows from the immutable source.
- Primary training probability range: 0.4789628532 to 0.5359025277.
- The retrospective primary gate remains failed because no prediction crossed
  the frozen 0.45/0.55 trade thresholds. The raw model is diagnostic only.

The artifact contains transparent scaler values, coefficients, intercepts,
feature order, thresholds, costs, source fingerprints, and guardrails. Runtime
probabilities are calculated with plain deterministic math; no serialized
training library is loaded.

## Prospective contract

- Ledger: `GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V2`
- Decision row: `GANN_CANDLESTICK_PROSPECTIVE_DECISION_V2`
- Outcome row: `GANN_CANDLESTICK_PROSPECTIVE_6BAR_OUTCOME_V2`
- Trial: `GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V2`
- Trial ID:
  `48C69002261876119E23C12077F4E140A5E1ADD47AE42AC2F038465B098C7839`
- Trial identity SHA-256:
  `44D2211B91DE8241FF19A4CC3C80FBCEC62F7D74F6BDF14EAE433B1F9989F8B3`
- Market-clock lock: `GANN_MT5_MARKET_CLOCK_SKEW_LOCK_V1`

Only the newest fully closed H1 bar is eligible, and only during its first 15
minutes. Missed decisions are never backfilled. Entry is the next actual bar
open; outcome is the sixth actual subsequent market bar close, with weekends
not counted as bars. Spread and round-trip slippage are recorded. Trial rows
are append-only and SHA-256 hash chained; the manifest is immutable.

## Live clock audit

MetaTrader documents Python tick and bar times as UTC:

- https://www.mql5.com/en/docs/python_metatrader5/mt5symbolinfotick_py
- https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrom_py

The connected MetaQuotes-Demo terminal reported its latest tick approximately
10,800 seconds ahead of Windows UTC. The first V1 live audit therefore produced
one stale abstention that is not valid prospective evidence. That database was
preserved without rewriting at:

`D:\GannFinancialAstro\app_data\candlestick_shadow_v1_invalid_market_clock_20260715.sqlite`

V2 freezes a maximum absolute market-clock skew of 300 seconds and fails closed
before either decisions or settlements. The valid V2 database remains a clean
genesis chain with zero decisions and zero outcomes:

`D:\GannFinancialAstro\app_data\candlestick_shadow_v2.sqlite`

The observed UI/API state was `skipped`, with a live skew near +10,800 seconds.
No offset was guessed or normalized.

## Verification

- 11 focused candlestick-shadow tests passed, including geometry parity,
  future-bar mutation, probability math, restart idempotence, no late backfill,
  six-market-bar settlement, append-only enforcement, manifest immutability,
  model tamper rejection, consumer locks, and clock fail-closed behavior.
- The complete backend suite passed: 66 tests; Ruff and Python byte compilation
  also passed for the changed Python modules.
- Frontend build and lint passed; 18 tests in five files passed.
- Native Tauri/PyInstaller build passed.
- Native crash/recovery soak passed all checks, including same-port sidecar
  recovery, frozen trial/chain visibility, failed-gate visibility, execution
  locks, persisted layout, and zero surviving descendants:
  `D:\GannFinancialAstro\soak\tauri_0.10.1_20260715_172125\logs\native_soak_report.json`.
- The same complete soak also passed after promotion from the stable release
  path:
  `D:\GannFinancialAstro\soak\tauri_0.10.1_20260715_173904\logs\native_soak_report.json`.
- Browser QA passed at desktop and compact widths with no console warnings or
  errors.

## Promoted Windows release

- Executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Executable SHA-256:
  `77FEC8E0412DE9E5EEA3F1275A2C066024BB6FB77304E009BD4F697F0D80CED7`
- Installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.10.1_x64-setup.exe`
- Installer SHA-256:
  `16E9FCA2E186BEF52B23A1AAC95664E52199F2C5BA394BF84032B4EE44C3AC7E`
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.0_20260715T172944Z`

## Next gate

Correct or replace the terminal/feed configuration so MT5 tick time agrees
with UTC within five minutes. Do not alter the frozen trial, apply a hardcoded
three-hour correction, backfill missed decisions, or authorize execution. Once
the clock lock passes naturally, allow V2 to accumulate untouched prospective
decisions and six-bar outcomes before any promotion discussion.
