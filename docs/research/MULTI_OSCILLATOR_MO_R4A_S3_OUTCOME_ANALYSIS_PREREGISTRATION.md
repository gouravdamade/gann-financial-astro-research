# MO-R4A-S3 Outcome Analysis Preregistration

This is a frozen, outcome-blind analysis plan. It contains no price, tick, candle, return, PnL, market reaction, Founder Review decision, or scored result.

Preregistration hash: `C4F8B0AC31CE37662A533B9570364894CEC37DD01FE6B68D137FE2C65001A319`
Acceptance hash: `155B814F64B9B3C9BB4E0BF57FEC94EDD0423A513D5CB04DAA63D1AB7CBCE1F8`
Frozen S2R1-R1 prediction hash: `83F1456271B510468A0DF28C66AD705318CD06F5D5B5E0566F6DE05FA06CF71D`

## Frozen Population

24 frozen identities: 12 USD and 12 JPY. The plan retains 14 directional rows, 13 primary market-scorable rows, one structural weekend exclusion, 3 categorical NEUTRAL rows, and 7 abstentions.

| Event ID | Side | Frozen state | Validation direction | Primary disposition |
| --- | --- | --- | --- | --- |
| TN_4A15CCC7D126313A14BCB562 | JPY | SUPPORTIVE | DOWN | PRIMARY_DIRECTIONAL |
| TN_6E2DD561FB40D45D406F808E | JPY | SUPPORTIVE | DOWN | PRIMARY_DIRECTIONAL |
| TN_7CCC78DA82BDAC13D3CF60B0 | JPY | SUPPORTIVE | DOWN | PRIMARY_DIRECTIONAL |
| TN_397A2B053BC76D9D788E5E5E | USD | SUPPORTIVE | UP | PRIMARY_DIRECTIONAL |
| TN_B24B1690FD8612329198D379 | JPY | SUPPORTIVE | DOWN | PRIMARY_DIRECTIONAL |
| TN_8C3582F7101F4F14BC4ECC4F | JPY | SUPPORTIVE | DOWN | PRIMARY_DIRECTIONAL |
| TN_B8750233DA923D431E121862 | USD | ADVERSE | DOWN | PRIMARY_DIRECTIONAL |
| TN_529E2CBC72B405EAD0990350 | JPY | SUPPORTIVE | DOWN | PRIMARY_DIRECTIONAL |
| TN_29BCE2386E5DB19625921587 | USD | ADVERSE | DOWN | PRIMARY_DIRECTIONAL |
| TN_6F48D71F91F1382FAA720581 | JPY | SUPPORTIVE | DOWN | PRIMARY_DIRECTIONAL |
| TN_97C9294ED13CD6C36FB0840B | JPY | ADVERSE | UP | PRIMARY_DIRECTIONAL |
| TN_574C7A7407B855CD78DF8E0D | USD | ADVERSE | DOWN | PRIMARY_DIRECTIONAL |
| TN_A32A6104A917D4918B269910 | USD | ADVERSE | DOWN | PRIMARY_DIRECTIONAL |

The excluded directional row is `TN_BD340A6100B173B5F254EDC1`: its complete primary interval is Saturday UTC. It remains in the 24-event frozen pilot and is never replaced, extended, or scored as zero.

## Tick Rule

At the separately authorized outcome phase, the only source is Dukascopy historical USDJPY tick data in UTC. The interval is `[applyingStartUtc, separatingEndUtc)`, with the first valid in-range tick as start and last valid in-range tick as end. Midpoints use `(bid + ask) / 2`; the return is `ln(P_end / P_start)`. S3 does not access that provider or any market file.

## Exact Test

The primary test is a one-sided exact label permutation with `C(5,1) * C(8,7) = 40` within-side assignments. It retains event windows and later observed returns, includes the observed assignment, and calculates `p_exact = count(H_perm >= H_observed) / 40`. There is no Monte Carlo, timestamp permutation, cross-side reassignment, or secondary p-value.

## Overlap Clusters

| Cluster | Members | Start | End |
| --- | ---: | --- | --- |
| C1 | 5 | 2025-03-31T20:48:24Z | 2025-04-02T06:09:08Z |
| C2 | 1 | 2025-04-02T08:39:52Z | 2025-04-02T18:38:57Z |
| C3 | 2 | 2025-04-02T21:43:26Z | 2025-04-03T08:04:32Z |
| C4 | 5 | 2025-04-03T08:35:23Z | 2025-04-04T20:32:38Z |

The secondary cluster-balanced rate equally weights C1-C4. The time-shift diagnostics use exactly -7 and +7 calendar days, preserve interval duration and UTC clock, and never redefine the primary test.

## Boundary

All S3 access flags remain false. No source doctrine is changed; no signed unit, pair resultant, magnitude, score, Auto Suggest, ML, MT5, execution, or production admission is created. Independent central review is required before any Astra pre-outcome audit or provider access.
