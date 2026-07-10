# Padmanabhan Timing V1 Validation - 2026-07-10

## Scope

This is a deterministic engineering and descriptive-data check, not doctrinal certification and not scientific validation.

Module: `padmanabhan_timing_doctrine.py`

Rule id: `PADMANABHAN_TIMING_QUAL_QUANT_V1_SOURCE_BOUNDED`

## Engineering checks

- Unit tests pass for whole-sign counting, Vedha blocker exceptions, the Mercury-house-4 source conflict, Vimshottari boundary behavior, the six-Rupa gate, and base-minus-quote arithmetic.
- Existing canonical touch rows were enriched without changing row count, row order, or any `touch_id`.
- Existing timeframe-switch rows were enriched without changing row count, row order, or any `touch_id`.
- Rebuilt candidate rows: 732.
- Unique source events in the switch data: 638.
- Legacy comparison found zero differences in:
  - `touch_id`
  - `signal_direction`
  - `fx_hypothesis_direction`
  - `fx_doctrine_hypothesis_direction`
  - `close_action`
  - `signed_return_pct`
- Every new candidate row has `fx_padmanabhan_evidence_only=1`.
- Every touch row has `event_padmanabhan_trade_signal_enabled=0`.

## Descriptive in-sample check

After deduplicating by `event_id`:

- Unique events: 638.
- Non-neutral timing-index predictions with UP/DOWN 72-hour outcomes: 550.
- Raw direction agreement: 50.0%.
- Predictions were strongly imbalanced: 473 DOWN versus 77 UP.

This is not a fair model score: it is in-sample, does not purge overlapping windows, and uses a provisional equal-additive interpretation of missing article weights. It is still a useful warning that version 1 has a bearish class bias and should not be promoted into Auto Suggest or MT5 execution.

## Promotion decision

**Remain evidence-only.**

Before promotion:

1. Recover the article continuation and Table 2, or explicitly abandon the claim of reproducing Padmanabhan's complete method.
2. Cross-check Vimshottari boundaries and reference-chart Shadbala totals against an independent trusted calculator.
3. Implement or source the missing temporal-quality and named Yogakaraka rules.
4. Run deduplicated, purged chronological walk-forward tests.
5. Compare `A` (Gochara), `B` (Dasha/Bhukti), and `A+B` separately against legacy baselines.
6. Reject or recalibrate the method if the bearish imbalance persists out of sample.
