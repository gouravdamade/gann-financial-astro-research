# MO-R4A-S3R1-R1 Astra Pre-Outcome Corrections

This is an outcome-blind successor to S3R1. It corrects acceptance validation, synthetic numeric handling, and interval-scoped data-quality semantics without reading market outcomes or changing the frozen scientific design.

Astra disposition: `PRE_OUTCOME_CORRECTION_REQUIRED`; acquisition branch: `BRANCH_B`.
Historical S3R1 preregistration: `CBE8E351C1F57E5717343E92D71C1CFDBFB49C0829FF2430BD5CDA3CECD7F444`
S3R1-R1 preregistration: `0C9EF14A7216C9BB62E834B865315D67B2603F076FF2BA28AFC32E92CDFC93E2`
Acquisition contract: `D2E78CECD9743A176E417ACD7A7EAD57EC21167B8708AF2043C9D016E0C2CD70`
Analysis core: `DCE54CE6FACCEFCF773E3F900691ED2BBB705A1D085CD6B5852B41F1A4CEE7F2`
Acceptance: `9FF8B14F1A6D48D65BC73069BA3D7EF341A4AC9EEE0783639AE87860CF04D2D7`

## Frozen Population

The predecessor population remains 24 identities: 12 USD, 12 JPY, 14 directional, 13 primary market-scorable, one Saturday UTC exclusion, three NEUTRAL, and seven abstentions. The exact 40-state within-side permutation universe and -7/+7 timing diagnostic are unchanged.

## Corrections

Acceptance now independently rebuilds and compares every supplied component, including a supplied core. A component that is internally rehashed but differs from the immutable derivation is rejected.

Synthetic diagnostics use a finite stable midpoint and `log(endMidpoint) - log(startMidpoint)`. Invalid numeric inputs are `DATA_NUMERIC_INVALID_UNSCORABLE`; exact finite zero alone remains `ZERO_MOVE`.

Quote conflicts are judged within the half-open interval only. Outside-scope invalid prices and conflicts do not poison that interval, while every timestamp is still parsed and malformed timestamps raise a typed input error. No outside tick rescues an interval.

## Acquisition Gate

The contract declares exactly 39 intervals (13 actual, 13 minus 7 days, 13 plus 7 days) and requires future raw/parsed hashes and raw retention. Provider-specific transport, pagination, encoding, precision, parser identity, and revision protocol remain unresolved. Acceptance is therefore `PRE_OUTCOME_ACQUISITION_CONTRACT_INCOMPLETE` and does not unlock outcome access.

All outcome-access flags remain false. No provider call, price/outcome read, S4 evaluator, report, cache, UI, score, polarity, Auto Suggest, ML, MT5, or execution path is present.
