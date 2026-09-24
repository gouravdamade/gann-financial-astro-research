# Candidate C EMP2-R2 Final Scientific Closure

**Status:** `SCIENTIFICALLY_CLOSED`
**Astra audit:** `POST_OUTCOME_SCIENTIFIC_AUDIT_PASS_WITH_LIMITATIONS`
**Execution:** `executionAllowed=false`

## Frozen Result

EMP2-R2 executed all 24 frozen ledger rows. It found no association meeting
the preregistered multiplicity-adjusted thresholds between the frozen
source-state categories and USDJPY forward returns at the tested 1h, 6h and
24h horizons. The eight primary 24h Holm-Bonferroni adjusted p-values are all
1.000; the sixteen secondary 1h/6h Benjamini-Hochberg adjusted p-values are
all 0.959. The raw p-value range is 0.1788-0.959. No frozen family threshold
was met.

The result integrity audit passed with zero integrity defects, and an
independent private-witness reconstruction reproduced the result. The frozen
result self-hash is
`FBF5307EE7BCD298F6AB1A2E77F6DC7A0D95D6EB1242279C46E7445FD5F4209F`; the
acceptance hash is
`C2B78614781C3ED24921ED4C0E6A09A54841B09AA2ADE2FA144658DECB6A4A36`.

This conclusion applies to this frozen experiment and its tested question. It
does not establish general predictive validity or invalidity, causation, the
absence of every possible market relationship, the validity or invalidity of
Jyotisa generally or of untested operators/horizons, profitability, or trading
readiness. The permitted interpretation remains
`EMPIRICAL_ASSOCIATION_DISCOVERY_NOT_FORECAST_OR_TRADING_VALIDATION`.

## Retained Limitations

All four Astra limitations remain attached to this result:

- `L1_SHIFT_EXCHANGEABILITY`: implementation matched the frozen shift contract,
  but scientific exchangeability is not established.
- `L2_BH_DEPENDENCE`: the dependence conditions for ordinary BH interpretation
  are not established; stored values remain the historically correct
  calculations.
- `L3_MARKET_ATTRITION`: quote attrition is substantial and varies by state and
  horizon; contract-compliant exclusion does not establish missing-at-random.
- `L4_STATISTIC_SCOPE`: the statistic tests category-conditioned mean-return
  structure, not every possible difference in conditional return distributions.

One reporting ambiguity is retained in the Astra audit record. No audit finding
changed the frozen result.

## Closure and Next Research

Candidate C remains `FROZEN_HISTORICAL_EMPIRICAL_EVIDENCE`. Empirical/product
promotion, directional mapping, source weighting, oscillator integration,
Fields integration, and trading use remain `NOT_AUTHORIZED`. No EMP3 is
authorized. No tuning, repair, new hypothesis, provider access, or new
empirical execution occurred in this closure; `executionAllowed=false` remains
locked.

The next nominated program is `MO-R4A-ASTRA-A1` - a read-only full classical
assumption and hidden-premise audit. EMP2-R2 tested a frozen operational
mapping; it did not establish every upstream premise, including modern
currency-chart applicability, USD/JPY chart identity, transit/natal
orientation, source-target direction, ayanamsa and node policies, admitted
aspects and event boundaries, persistence and temporal scale, polarity and
magnitude, modifier composition, or UI terminology. The next task is to
classify assumptions and evidence, not to search post hoc for parameters. This
closure does not start that audit.

Machine closure record:
`status/research/mo_r4a_candidate_c_emp2_r2_final_scientific_close_v1.json`.

Next gate:
`CENTRAL_REVIEW_CANDIDATE_C_EMP2_R2_FINAL_SCIENTIFIC_CLOSE`.
