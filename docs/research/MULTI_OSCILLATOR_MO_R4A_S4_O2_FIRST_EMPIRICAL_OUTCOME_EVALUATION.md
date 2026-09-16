# MO-R4A-S4-O2 First Empirical Outcome Evaluation

Status: `CENTRAL_REVIEW_BEFORE_ASTRA_POST_OUTCOME_AUDIT`

This report records the exact deterministic object returned by the frozen O1
evaluator during the single centrally authorized O2 execution. No source or
test code was changed after O1, and no alternate analysis was performed.

## Authorization and Input Integrity

- Authorization commit: `955f3fa004f11616d6aa8c31775447a57ed25b98`.
- Authorization hash:
  `3AA3B483F976E7E60DF996F62A0BCFA3059D815151179E7D2AAD7015DBCAB13E`.
- O1 commit: `0cf1ebf32dfe7b239d500e25b12c3037fcfa8e3c`.
- Evaluator SHA-256:
  `702049C05930C470BE069C6ADB95BBF2067FCA35C9C9BCB309E720226111100A`.
- O1 freeze hash:
  `3153A83919207E1866339DFEB7CD4755EDFC0AD31AD8ED2DB190F11BEA88F8A6`.
- All `15/15` parsed-capture SHA-256 values passed the evaluator's
  hash-before-JSONL-parse gate.
- The evaluator processed exactly `39` half-open intervals: `13 ACTUAL`,
  `13 MINUS_7`, and `13 PLUS_7`.
- No provider or network call occurred. No raw BI5 was used.

The exact returned object is persisted at
`status/audits/mo_r4a_s4_o2_outcome_evaluation_result.json`.

## Primary Result

- Completeness: `COMPLETE`.
- Primary scorable count: `13/13`.
- Denominator: `13`.
- `H`: `8`.
- `H/13`: `8/13` (`0.61538461538461538461538461538461538461538461538462`).

## Within-Side Permutation Result

- Assignments: `40`.
- Observed assignment index: `0`.
- Observed hit count: `8`.
- Inclusive tail count: `12/40`.
- `pExact`: `0.3`.
- Histogram by permutation hit count (`hitCount: assignmentCount`):
  `0:0, 1:0, 2:0, 3:0, 4:8, 5:0, 6:20, 7:0, 8:12, 9:0, 10:0, 11:0, 12:0, 13:0`.
- No secondary p-value was emitted (`null`).

## Overlap Clusters

| Cluster | Events | Hits | Hit rate |
| --- | ---: | ---: | ---: |
| C1 | 5 | 3 | `3/5` (`0.6`) |
| C2 | 1 | 0 | `0/1` (`0`) |
| C3 | 2 | 2 | `2/2` (`1`) |
| C4 | 5 | 3 | `3/5` (`0.6`) |

- Cluster-balanced hit rate: `11/20` (`0.55`).
- No secondary p-value was emitted (`null`).

## Side Descriptives

These are descriptive outputs emitted by the frozen result and are not a
cross-side score or market signal.

| Side | Hits / events | Hit rate | Mean expected-signed log return | Median expected-signed log return |
| --- | ---: | ---: | ---: | ---: |
| USD | `3/5` | `0.6` | `0.0032353618189090312612238896095233709174925002565434` | `0.0032664892896149530286589577390103028388527284219653` |
| JPY | `5/8` | `0.625` | `0.0021190679135268557501818958542400011336123671837178` | `0.0019546479001834211031770802531702204499791127833385` |

## Timing Diagnostic

- `H_minus7`: `6`.
- `H_plus7`: `8`.
- Actual: `8`.
- Timing-specificity status:
  `TIMING_SPECIFICITY_NOT_DEMONSTRATED`.

## Frozen Result Decision

- `survivalStatus`: `PILOT_ASSOCIATION_NOT_SURVIVED`.
- Result hash:
  `53010A50F7C6EBFA09AD5855FE70204126AD40959AE643A8AE91564021B9FD2B`.
- Evaluator execution flags: `outcomeDataRead=true`,
  `outcomeUnlocked=true`, `executionAllowed=false`, `autoSuggest=false`,
  `ml=false`, `mt5=false`.

The only permitted interpretation is association under the preregistered
conditional within-side permutation null in this fixed feasibility pilot. This
record does not claim causation, proof of astrology, production profitability,
general market validity, out-of-sample validity, independent replication,
calibrated probability, or trading readiness.

Chapter-20 and other financial/source material were not used to alter this
evaluation. No outcome-driven repair or tuning occurred. The next review gate
is `CENTRAL_REVIEW_BEFORE_ASTRA_POST_OUTCOME_AUDIT`.
