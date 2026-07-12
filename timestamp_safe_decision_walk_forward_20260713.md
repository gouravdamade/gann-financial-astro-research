# Timestamp-Safe Decision Walk-Forward Evaluation

Generated: 2026-07-12T19:17:03.617315+00:00

## Frozen Contract

- Packet: `GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1`
- Engine: `timestamp_safe_auto_suggest_v1_1_20260713`
- Policy: `fx_doctrine_consensus_watch_only_v1`
- Decision time: selected SR-touch candle close.
- Label time: stored 72-hour outcome availability timestamp.
- Embargo after label availability: 72.0 hours.
- Primary unit: one unique decision timestamp, consolidating simultaneous event rows.
- Frozen policy uses no fitted parameter and test labels never enter decision packets.
- Event source SHA-256: `110927D8B5FEEF267FA45556FE46311C8843F8B445BB8F65B2A137C1577ABB04`
- Touch source SHA-256: `653E4A00327FED0308B3E16FC4C9EA63AFBD266377A543DC435B860EBB9F6B1B`
- Price source SHA-256: `3C71A983EF645133D34B7328E44E8DA6612CA22EBC989827626D55F281B147A9`

## Primary Out-of-Sample Result

- Eligible decision clusters: 355
- Watch clusters: 258 (72.68% coverage)
- Directional hits: 140 / 258 (54.26%)
- Wilson 95% interval: 48.17% to 60.24%
- Balanced direction accuracy: 55.91%
- Exact two-sided binomial p vs 50%: 0.190975
- Training-majority hit rate on the same watch clusters: 43.41%
- Selective lift: 10.85%
- Mean signed 72h return (descriptive, no costs): 0.0276%

## Fold Stability

| Fold | Train clusters | Purged | Test clusters | Watches | Hit rate | Mean signed 72h |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 234 | 5 | 71 | 46 | 54.35% | 0.0130% |
| 2 | 290 | 26 | 71 | 56 | 58.93% | 0.2128% |
| 3 | 364 | 20 | 71 | 50 | 56.00% | -0.0171% |
| 4 | 439 | 14 | 71 | 58 | 44.83% | -0.2136% |
| 5 | 510 | 18 | 71 | 48 | 58.33% | 0.1635% |

## Secondary Row-Level Diagnostic

- Eligible event rows: 457
- Watches: 318 (69.58% coverage)
- Hit rate: 54.72%
- Row metrics are secondary because simultaneous astrological events can share one market outcome.

## Predeclared Statistical Gate

Status: **failed_retrospective_statistical_gate**

- [x] minimum 100 watch clusters
- [x] coverage at least 10 percent
- [ ] wilson 95 lower above 50 percent
- [ ] two sided binomial p below 0 05
- [x] at least four completed folds
- [ ] positive mean signed return in four folds

## Interpretation

This is a purged chronological retrospective evaluation, not an untouched prospective trial. It can reject a weak policy, but it cannot authorize live orders. The execution gate remains blocked regardless of the statistical result until prospective shadow evidence, external astrology-component certification, and explicit MT5 execution authorization all exist.

No transaction costs, spread, slippage, position sizing, entry, exit, or P/L execution logic is claimed by this watch/abstain evaluation.
