# Frozen Prospective Shadow Trial Manifest

Verified: 2026-07-13 15:48 IST

## Purpose

Gann Astro Desk now freezes one prospective USDJPY policy cohort before outcomes
are available. A decision whose engine, policy, astronomy contract, symbol,
timeframe, horizon, or statistical gate differs from the manifest is rejected
instead of silently joining the trial.

## Frozen Identity

- Contract: `GANN_FROZEN_PROSPECTIVE_SHADOW_TRIAL_V1`
- Trial ID: `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`
- Manifest source: `existing_decision_backfill_v1`
- Engine: `timestamp_safe_auto_suggest_v1_1_20260713`
- Policy: `fx_doctrine_consensus_watch_only_v1`
- Astronomy: `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`
- Symbol / timeframe: `USDJPY` / `H1`
- Outcome contract: `GANN_PROSPECTIVE_72H_OUTCOME_V1`
- Horizon: 72 hours
- Gate configuration SHA-256:
  `6151D98F5967958EA05C7EB9918615FB0A34079E5B6907E66476ECA9D2B17B70`
- Manifest identity SHA-256:
  `D74E67ABFABC85474CABD93DB2607EBA611C621D4879201B886D1ACC145626BF`

## Frozen Gate

- Minimum settled watch clusters: 100
- Minimum watch coverage: 10%
- Wilson 95% lower bound must exceed: 50%
- Exact two-sided binomial p-value must be below: 0.05
- Mean signed 72-hour return must exceed: 0%
- Minimum UTC calendar months: 4
- Execution remains disabled regardless of research-gate status.

## Live Verification

- Manifest integrity: valid
- Policy cohort count: 1
- Append-only chain: valid
- Immutable decisions: 7
- Abstain decisions: 7
- Settled outcomes: 0
- Pending outcomes: 7
- First legal 72-hour settlement: `2026-07-16T04:00:00+00:00`
- Outcomes currently due: 0
- Latest verified closed MT5 H1 bar: `2026-07-13T10:00:00+00:00`
- Active corrected artifact: `tn_46ffe4254d23445c96cc220d2038202c`
- MT5 connected: yes
- MT5 trade allowed: no
- Shadow execution allowed: no
- Local Jyotish ready: `qwen2.5:3b`

## Native Release

- Version: `0.6.1`
- Executable: `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- SHA-256: `772905ED308F58B46CAE7910ED8314DCA7D6B1DCE9877AE3478A46DE42DFD7DC`
- Files: 1,657
- Bytes: 708,779,331
- Previous `0.6.0` release archived at
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.6.0_20260713_154140`.

## Verification

- Full Python suite: 109 passed
- Focused shadow-ledger and refresh suite: 12 passed
- Frontend Vitest: 5 passed
- Ruff: passed
- Oxlint: passed
- TypeScript/Vite production build: passed
- PyInstaller packaging and executable hash: passed
- Packaged API and live database migration: passed
- Packaged browser DOM, visual layout, and console-log QA: passed

Do not alter this cohort's policy or statistical thresholds while collecting the
sample. A future policy revision must create a new trial identity rather than
rewriting or mixing this one.
