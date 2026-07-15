# USDJPY Candlestick Walk-Forward V1

Date: 2026-07-15

## Decision

The predeclared primary candidate, `named_pattern_logistic_v1`, failed the
retrospective gate. It produced zero trades because none of its 49,987
out-of-sample probabilities crossed the frozen 0.45 short or 0.55 long
threshold. The observed range was 0.467735 to 0.544749. This is deterministic
abstention, not a missing-model or missing-data failure.

No result from this lab is authorized for the candlestick RAG corpus, Jyotish
RAG corpus, Auto Suggest, official ML notes, prospective shadow policy,
coordinator, or MT5 execution.

## Frozen Contract

- Contract: `GANN_CANDLESTICK_WALK_FORWARD_CONTRACT_V1`.
- Contract SHA-256:
  `1F8BBB07D97A54A9FDC2F339BE0573A1059284E7AB345CE00FF12841882F2877`.
- Source: `D:\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet`.
- Source SHA-256:
  `3C71A983EF645133D34B7328E44E8DA6612CA22EBC989827626D55F281B147A9`.
- Source coverage: 100,000 USDJPY H1 rows from 2010-01-27 through
  2026-03-09 in UTC.
- Geometry: the app's `transparent_ohlc_geometry_v1` implementation.
- Evidence availability: decision-bar close only; entry at next-bar open.
- Exit: close of the sixth held H1 bar.
- Costs: observed entry spread when positive, otherwise 1.0 pip; 0.2 pip
  slippage on each side.
- Validation: five expanding chronological folds after a 50% initial training
  segment. Training labels must be available before the six-bar embargo cutoff.
- Primary thresholds and gate were frozen before the result was inspected.

The generated decision set contains 99,973 rows. The five out-of-sample folds
contain 49,987 rows. Each fold purged or embargoed 11 preceding rows, and each
reported maximum training-label availability timestamp is at or before its
purge cutoff and before the test start.

## Out-of-Sample Result

| Strategy | Trades | Coverage | Mean net pips/trade | Total net pips |
| --- | ---: | ---: | ---: | ---: |
| Always long | 49,987 | 100.00% | -0.3520 | -17,595.5 |
| Body momentum | 49,684 | 99.39% | -1.1660 | -57,931.4 |
| Five-bar momentum | 49,875 | 99.78% | -0.8717 | -43,475.6 |
| Raw wick reversal rule | 5,229 | 10.46% | -2.0937 | -10,948.0 |
| Named pattern rule | 23,951 | 47.91% | -0.9898 | -23,706.1 |
| Raw geometry logistic | 84 | 0.17% | +4.0500 | +340.2 |
| Named pattern logistic, primary | 0 | 0.00% | n/a | 0.0 |

The primary failed minimum trades, positive folds, matched lift, and weekly
block-bootstrap requirements. With no primary trades, matched-baseline and
bootstrap comparisons have no active rows and are correctly unavailable.

## Exploratory Findings

The raw-geometry logistic diagnostic crossed a threshold only 84 times: 30
short and 54 long signals. Its fold mean net results were approximately
+10.49, +6.54, +11.94, -7.03, and +0.92 pips per trade. Four positive folds
look interesting, but 84 trades are far below the frozen 500-trade minimum and
coverage is only 0.17%. It is a future hypothesis, not a promotion candidate.

Two named bullish diagnostics were positive in aggregate after costs but not
stable across time:

- long bullish body: -1.36, +0.30, +1.72, +0.32, and +0.44 mean net pips by
  fold;
- bullish body engulfing: -1.23, -0.19, +0.71, +1.13, and +3.01 mean net pips
  by fold.

Their early negative and later positive behavior warns against treating a
named candle pattern as a universal signal. Bearish-body diagnostics were also
mostly negative after costs. These rows remain exploratory and were not used
to revise the frozen contract.

## Reproducibility

The frozen study was run twice. Between the pre-audit run at
`D:\GannFinancialAstro\validation\candlestick_usdjpy_v1_20260715_153157`
and the final run at
`D:\GannFinancialAstro\validation\candlestick_usdjpy_v1_20260715_154033`,
the following outputs were byte-identical:

- `decision_rows.parquet`;
- `out_of_sample_predictions.parquet`;
- `fold_metrics.csv`;
- `strategy_summary.csv`;
- `pattern_diagnostics.csv`;
- `fold_diagnostics.json`.

The final report and manifest differ because the evaluator now records the
probability-support audit. Final evidence:

- manifest SHA-256:
  `9F38D57C158DE1759403DD70DF2DC9D92DBA3003DAFD283FFB5625C5143CEE06`;
- report SHA-256:
  `0ED567596358B2ADB647B49B10EF3243599A74E5311DC8FA60C7E91DEC3021A7`;
- evaluator SHA-256:
  `FEC40871539E404A675B0755607E0A5FD43AB9042869BE573414E7F36232CD3F`.

Verification passed: Ruff, eight focused unit tests, source-hash rejection,
prefix invariance, next-bar entry, frozen costs, chronological purge/embargo,
disabled execution, explicit abstention diagnostics, two full historical runs,
and data-frame equality checks.

## Next Gate

Do not tune the V1 thresholds against these same out-of-sample folds. A new,
versioned V2 contract may test the raw continuous geometry hypothesis with a
separate calibration period, minimum-coverage rule, non-overlapping event
sampling or stronger dependence controls, and an untouched final holdout.
Even then, retrospective success cannot authorize live use. The safest next
operational step is to accumulate a timestamped prospective candle-shadow
cohort without changing the frozen live policy.
