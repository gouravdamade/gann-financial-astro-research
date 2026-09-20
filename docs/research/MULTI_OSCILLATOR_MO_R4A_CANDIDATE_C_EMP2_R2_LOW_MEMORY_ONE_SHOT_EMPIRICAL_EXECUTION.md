# Candidate C EMP2-R2 Low-Memory One-Shot Empirical Execution

## Frozen Execution

The one permitted public low-memory execution was authorized in commit
`ee84a12a441ccf7ac2bc23006490772b0cda750d`, executed from that checkout, and
published its first canonical result in commit
`ef691e75151bc2c296f98a84383e8e30adf6bb9e`. The predecessor low-memory
runtime seal is `94e522a800c43bd38ae5f29b356d7b187eac55c2`.

- Authorization record hash: `7389B0DF4F3C36542C7B0F70C29E536F4BF4373B90A2ED8A8D8CA12EF85C5652`
- Result self-hash: `FBF5307EE7BCD298F6AB1A2E77F6DC7A0D95D6EB1242279C46E7445FD5F4209F`
- Result file SHA-256: `035AB0AC4A195047A35920F86674293893C44DD738829EA43AA44313B3157983`
- Market snapshot hash: `0F04578F8BB9FE08558889B3BBAC50F19DCE6702093856842B8A12ED32ACCEEC`
- Market admission hash: `2EC34D56151E18CE17FC13F47CFB95007B9FDA86BF5F59B3416D65AF9455160A`
- Source snapshot / eligibility hashes: `9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284` /
  `ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1`

The executor verified the sealed runtime and immutable inputs, streamed the
private admitted raw market evidence, wrote the canonical result once, and
did not query a provider. The result contains 24 of 24 `EXECUTED` test-ledger
rows: eight primary 24-hour Holm-Bonferroni rows and sixteen secondary
1-hour/6-hour Benjamini-Hochberg rows.

## Stored Results

| Side | Component | Horizon | Status | Raw p | Adjusted p |
| --- | --- | ---: | --- | ---: | ---: |
| JPY | C02 natural relationship | 1h | EXECUTED | 0.6270 | 0.959 |
| JPY | C02 natural relationship | 6h | EXECUTED | 0.9290 | 0.959 |
| JPY | C02 natural relationship | 24h | EXECUTED | 0.3132 | 1.000 |
| JPY | C03 temporary relationship | 1h | EXECUTED | 0.8348 | 0.959 |
| JPY | C03 temporary relationship | 6h | EXECUTED | 0.4010 | 0.959 |
| JPY | C03 temporary relationship | 24h | EXECUTED | 0.6810 | 1.000 |
| JPY | C04 compound relationship | 1h | EXECUTED | 0.9590 | 0.959 |
| JPY | C04 compound relationship | 6h | EXECUTED | 0.6084 | 0.959 |
| JPY | C04 compound relationship | 24h | EXECUTED | 0.7342 | 1.000 |
| JPY | C05 ordinary and special drsti | 1h | EXECUTED | 0.7322 | 0.959 |
| JPY | C05 ordinary and special drsti | 6h | EXECUTED | 0.6736 | 0.959 |
| JPY | C05 ordinary and special drsti | 24h | EXECUTED | 0.4828 | 1.000 |
| USD | C02 natural relationship | 1h | EXECUTED | 0.2516 | 0.959 |
| USD | C02 natural relationship | 6h | EXECUTED | 0.6026 | 0.959 |
| USD | C02 natural relationship | 24h | EXECUTED | 0.9440 | 1.000 |
| USD | C03 temporary relationship | 1h | EXECUTED | 0.4652 | 0.959 |
| USD | C03 temporary relationship | 6h | EXECUTED | 0.3452 | 0.959 |
| USD | C03 temporary relationship | 24h | EXECUTED | 0.5292 | 1.000 |
| USD | C04 compound relationship | 1h | EXECUTED | 0.2826 | 0.959 |
| USD | C04 compound relationship | 6h | EXECUTED | 0.9170 | 0.959 |
| USD | C04 compound relationship | 24h | EXECUTED | 0.5004 | 1.000 |
| USD | C05 ordinary and special drsti | 1h | EXECUTED | 0.1788 | 0.959 |
| USD | C05 ordinary and special drsti | 6h | EXECUTED | 0.7464 | 0.959 |
| USD | C05 ordinary and special drsti | 24h | EXECUTED | 0.7678 | 1.000 |

The primary family is `PRIMARY_ALL_EXECUTED_24H` with
`HOLM_BONFERRONI`, alpha `0.05`, and eight executed rows. The secondary family
is `SECONDARY_ALL_EXECUTED_1H_6H` with `BENJAMINI_HOCHBERG`, q `0.10`, and
sixteen executed rows. The stored adjusted values are all above their
respective preregistered thresholds.

## Boundary

This is an unsigned empirical association discovery result only:
`EMPIRICAL_ASSOCIATION_DISCOVERY_NOT_FORECAST_OR_TRADING_VALIDATION`.
It assigns no market direction, source weights, USD/JPY side-sign mapping,
forecast, score, or trading behavior. There were zero scientific retries,
zero provider calls or re-queries, no result overwrite, and no post-hoc tuning.

Stop at `CENTRAL_REVIEW_CANDIDATE_C_EMP2_R2_LOW_MEMORY_ONE_SHOT_AUTHORIZATION_AND_EMPIRICAL_EXECUTION`.
