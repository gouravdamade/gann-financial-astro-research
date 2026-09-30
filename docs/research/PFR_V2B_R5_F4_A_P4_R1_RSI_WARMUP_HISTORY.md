# PFR-V2B-R5-F4-A-P4-R1 RSI Indicator History / Warm-Up Correction

Milestone: `PFR-V2B-R5-F4-A-P4-R1`
Starting commit: `353c6ad057a6478696a97cc54f5d802ff1692d89`
Implementation commit: `93ddb9e`
Branch: `research/pfr-v2b-r5-f4-a-p4-r1-rsi-warmup-history`

## Disposition

This is a bounded indicator-data correction. The P4 founder inspection passed
the F4-A activity and chart UX, but the D1 RSI pane remained in `warming up`
for a visible range containing approximately 12 bars. The P4 candidate remains
immutable and is not marked finally accepted. P4-R1 supplies the correction
candidate for central review.

## Root Cause

The Wilder implementation already requires `period + 1` closed candles. With
RSI 14, that is at least 15 closed candles. `MarketChart` previously ran
`closedCandlesAt(payload.candles, ...)` directly over the visible payload. The
founder case supplied only 12 D1 candles, so the empty RSI series was the
mathematically correct result for that payload. The defect was the absence of a
separate historical indicator context, not the Wilder formula.

## Correction

The chart payload now has an optional, explicit read-only channel:

```text
candles: visibleCandles
indicatorHistory: { candles: historicalCandles }
```

The backend provides at most 1,000 OHLC candles strictly before the requested
visible start. In replay mode it retains only history whose candle close time
is at or before the replay cutoff. No outcome, provider, Candidate C, or
trading data participates in this channel.

The frontend merges history and visible candles by open timestamp, lets the
visible candle win at a boundary, rejects non-finite OHLC, sorts ascending,
applies closed-bar filtering, and retains the last:

```text
max(100, RSI_PERIOD * 5)
```

closed historical bars before the visible start. Existing Wilder smoothing,
gain/loss handling, levels, and closed-bar semantics are unchanged. RSI points
are clipped back to the visible candle time range. Warm-up candles therefore
initialize the indicator without appearing in the price series or changing
the chart viewport.

## Founder Case and Boundary Tests

- The visible price series remains 12 candles before and after the correction.
- Before R1, the 12-candle/RSI-14 payload produces no numeric RSI points.
- With 100 prior closed history candles, numeric RSI points are available in
  the visible range while the visible series remains 12 candles.
- H1, H4, D1, and W1 use the same closed-bar-count policy.
- Weekend/session gaps do not convert elapsed calendar days into bar counts.
- Replay history is filtered by candle close time, so changing future candles
  cannot change RSI before the replay cutoff.
- A changing current open candle cannot change RSI.
- The existing chart pane/layout/activity coverage continues to keep price,
  RSI, and unsigned activity on the shared visible time scale. No `fitContent`,
  range movement, activity-range change, or layout mutation was added.
- Insufficient history still yields no fabricated value; the existing warming
  up state remains valid.

## Verification

- Focused frontend RSI/chart/layout/activity tests: **75/75**, 6 files.
- Full frontend suite: **254/254**, 49 files.
- Focused backend chart/RSI tests: **21/21**.
- TypeScript and Vite production build: passed.
- Oxlint: passed.
- `git diff --check`: passed for the implementation and documentation change.
- The repository-wide backend discovery was started but not certified: it
  entered an inherited CPU-heavy test in
  `backend/test_outcome_analysis_s3r1_r3.py` and was stopped before a final
  summary. No R1-focused test failed; the full-backend result is explicitly
  **not claimed as passed**.
- Native Windows visual control was unavailable in this session. No founder
  acceptance is claimed, and the immutable P4 candidate was not overwritten.
- A separate local Tauri development/native build completed from source commit
  `89c6dacf70dacfc76af5b6695c4c345aa5ea2561`. It used the inherited package
  metadata version `0.10.67-pfr-v2b-r5-f4-a-p3-r2` and was written outside the
  immutable P4 candidate directory. Portable output:
  `D:\Rust\targets\release\gann-astro-desk.exe`, SHA-256
  `3F0AC20B0558F5EC3E155A51E81B3599F38A6D23CD69938EAA862C037C65B4FE`.
  Installer output:
  `D:\Rust\targets\release\bundle\nsis\Gann Astro Desk_0.10.67-pfr-v2b-r5-f4-a-p3-r2_x64-setup.exe`,
  SHA-256 `0B646A7F4003BD3DFF0602C8143B6B99304325742651079F5DC67A4A44A87BD6`.
  This build is a verification artifact, not a new immutable release candidate.

## Preserved Locks

`rsiFormulaChanged=false`

`closedBarSemanticsChanged=false`

`lookAheadAllowed=false`

`visibleRangeChanged=false`

`fieldsWavesChanged=false`

`activityMathChanged=false`

`pairMathChanged=false`

`polarityCatalogueChanged=false`

`evidenceRegistryChanged=false`

`F4BImplemented=false`

`F4CImplemented=false`

`candidateCChanged=false`

`EMP3Authorized=false`

`providerAccess=false`

`outcomeAnalysis=false`

`MT5OrderInvocation=false`

`executionAllowed=false`

The correction does not implement polarity, score aggregation, pair logic,
Fields direction, Auto Suggest, ML, provider access, outcome analysis, MT5,
or execution.

## Next Gate

`CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P4_R1_RSI_WARMUP_HISTORY`
