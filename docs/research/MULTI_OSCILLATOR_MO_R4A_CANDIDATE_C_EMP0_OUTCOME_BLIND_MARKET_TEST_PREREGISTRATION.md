# Candidate C EMP0 Outcome-Blind Market-Test Preregistration

## Scope

EMP0 formally closes Candidate C source reproduction and freezes a future
empirical-association design before any USDJPY quote, price, return, provider,
or market outcome is read. The only inputs used here are the immutable AUTH1
Evaluator A and B artifacts, the frozen population, and the protected V2
semantic projection.

The source-to-study chain remains explicit:

`classical source fact -> frozen Candidate C source state -> experimental market bridge -> preregistered market hypothesis -> preregistered empirical test`.

Source values remain unsigned and categorical. They do not imply bullishness,
bearishness, USD/JPY pressure, or USDJPY direction.

## Source-State Freeze

- Population: 645 frozen events, 317 USD and 328 JPY, from
  `2025-05-01T01:58:38Z` through `2025-07-31T23:19:56Z`.
- Snapshot: 5,160 source-state records, exactly eight frozen row slots per
  event, built by reprojecting both immutable AUTH1 outputs through protected
  V2.
- A/B semantic agreement: exact for every source-state row.
- `UNKNOWN` is `SOURCE_UNKNOWN_ABSTAIN`, never an inferential category or
  market feature. Rare VALUE states remain separate descriptive records.

Source-only testability is frozen at `MIN_STATE_COUNT=20` and
`MIN_TOTAL_TEST_COUNT=60`.

| Component | USD | JPY |
| --- | --- | --- |
| C01 natural planet class | not testable: eligible total below 60 | not testable: eligible total below 60 |
| C02 natural relationship | testable; one rare VALUE state retained | testable; one rare VALUE state retained |
| C03 temporary relationship | testable | testable |
| C04 compound relationship | testable; one rare VALUE state retained | testable; one rare VALUE state retained |
| C05 special Drsti geometry | not testable: one eligible VALUE state | not testable: one eligible VALUE state |
| C05 ordinary Drsti | testable | testable |
| C06 sthula motion | not testable: no eligible VALUE states | not testable: no eligible VALUE states |
| C07 individual records/no stacking | not testable: source abstention | not testable: source abstention |

## Future Market Contract

The target is `FX_SPOT_USDJPY`, not a future, CFD, ETF, or synthetic pair. No
provider is selected in EMP0. A future admitted snapshot must contain UTC
bid/ask observations at 60-second resolution or finer, from at least
`2025-05-01T01:58:38Z` through `2025-08-01T23:20:56Z`.

For event time `t`, P0 is the first quote at or after `t` and no later than
`t + 60 seconds`. PH is independently the first quote at or after `t + H` and
no later than `t + H + 60 seconds`. Midpoint is `(bid + ask) / 2` and the
endpoint is `ln(PH / P0)`. Missing anchors are
`MARKET_QUOTE_UNAVAILABLE`; there is no interpolation, fill, or substitute.

The primary horizon is 24 hours. The only secondary exploratory horizons are
1 hour and 6 hours. Later market availability may remove observations but may
not change source states, source eligibility, row slots, or abstention.

## Statistical Freeze

For each source-testable side/row-slot, the primary question is whether mean
24-hour forward USDJPY log returns differ across the eligible categorical VALUE
states. The unsigned statistic is between-state explained variance,
`T = SSB / SST`; zero outcome variance is not testable.

The null holds returns fixed and circularly shifts categorical state sequences
within `sideIdentity x UTC month`, ordered by exact UTC then event ID. It uses
exactly 4,999 deterministic SHA-256-derived offsets. Raw p-values use the
`(1 + exceedances) / 5000` correction. The 24-hour primary family uses
Holm-Bonferroni at 0.05 across all executed USD and JPY tests. The 1-hour and
6-hour secondary family uses Benjamini-Hochberg at q=0.10.

This is association/discovery only. It cannot establish forecasting, market
validity, profitability, or trading readiness. A later discovery would require
a new preregistered independent holdout before any directional rule could be
considered.

## Locks

`providerSelected=false`, `marketDataAcquisitionAllowed=false`,
`marketDataSnapshotPresent=false`, `marketOutcomeRead=false`, and
`realMarketStatisticalExecutionAllowed=false`. EMP0 has no provider client,
does not execute real returns or p-values, and assigns no side inversion,
market direction, source weight, score, pair field, wave, or forecast.

Next gate: `CENTRAL_REVIEW_CANDIDATE_C_EMP0_OUTCOME_BLIND_MARKET_TEST_PREREGISTRATION`.
