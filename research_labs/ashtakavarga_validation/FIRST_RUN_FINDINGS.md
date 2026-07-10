# First Isolated USDJPY Run

Run date: 2026-07-10

## Scope

- Raman-adapted sidereal BAV/SAV evidence only.
- USD workspace reference chart minus JPY workspace reference chart.
- USDJPY H1 source resampled into UTC trading days.
- Historical price span used after joins: 2010-01-27 through 2026-03-09.
- 4,187 joined trading days.
- Five expanding chronological folds.
- Gap equal to the tested outcome horizon.
- Multi-day metrics sampled at non-overlapping intervals.
- No transaction costs, slippage, position sizing or trade execution.

Generated evidence and detailed reports stay local and ignored by Git:

- `outputs/daily_evidence.parquet`
- `reports/certification_report.json`
- `reports/usdjpy_walk_forward.json`

## Arithmetic result

- All 11 unit tests passed.
- The published B. V. Raman standard-horoscope fixture matched all 84 BAV cells and all 12 SAV values.
- All expected BAV totals and the SAV total of 337 matched.
- 250 randomized charts preserved every row and grand-total invariant.
- Certification remains `partial_external_calculators_pending` because zero of the required two outside calculators have been checked.

## Exploratory market result

The simple features did not show reliable out-of-sample directional evidence.

| Feature/mapping | Horizon | Independent observations | Hit rate | 95% Wilson interval | Unadjusted p vs 50% |
|---|---:|---:|---:|---:|---:|
| SAV base-minus-quote, fixed positive | 1 day | 2,044 | 51.32% | 49.15%-53.48% | 0.232 |
| Jupiter-Saturn base-minus-quote, fixed positive | 1 day | 1,482 | 49.66% | 47.12%-52.21% | 0.795 |
| SAV base-minus-quote, train-only direction | 5 days | 410 | 52.44% | 47.60%-57.23% | 0.323 |
| Jupiter-Saturn base-minus-quote, train-only direction | 5 days | 297 | 52.19% | 46.52%-57.81% | 0.451 |
| SAV base-minus-quote, train-only direction | 20 days | 103 | 51.46% | 41.93%-60.88% | 0.768 |
| Jupiter-Saturn base-minus-quote | 20 days | 74 | 50.00% | 38.89%-61.11% | 1.000 |

Every confidence interval includes 50%. None of these unadjusted comparisons is statistically distinguishable from chance, and multiple-testing correction would make the evidence weaker, not stronger.

The fixed one-day SAV mapping produced positive mean signed return in all five folds, but its directional hit-rate uncertainty includes chance and costs are absent. That is a hypothesis to retain for stricter testing, not a signal.

## Decision

- Keep the lab isolated.
- Do not alter Auto Suggest, ML notes, BTC logic or MT5.
- Complete two outside-calculator comparisons.
- Add randomized/circular-shift placebos and transaction-cost sensitivity.
- Test the three Bitcoin location hypotheses separately; do not select a location after seeing which backtest wins.
- Do not implement the corrected KAS event worksheet until the classical calculation gate is complete.
