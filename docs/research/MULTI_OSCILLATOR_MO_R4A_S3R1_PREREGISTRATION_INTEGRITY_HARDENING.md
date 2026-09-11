# MO-R4A-S3R1 Preregistration Integrity Hardening

S3R1 is a successor to the accepted outcome-blind S3 package. The four findings were integrity issues, not scientific-design changes: the nested schema is now closed, one acyclic core hash represents the complete analysis package, time-shift comparison is deterministic, and the conditional permutation-null assumption is explicit.

Historical S3 preregistration: `C4F8B0AC31CE37662A533B9570364894CEC37DD01FE6B68D137FE2C65001A319`
S3R1 preregistration: `CBE8E351C1F57E5717343E92D71C1CFDBFB49C0829FF2430BD5CDA3CECD7F444`
S3R1 primary population: `DAFA64956255F7AD2F91108DD08E488ED4026CC2CE488F3F37861EA82A49C73E`
S3R1 overlap clusters: `4FE7315F4C30E61A4E40158A3D41E8B36A89957A44BAD8C3E4D7FBFFA3580057`
S3R1 invariance audit: `8062FF0C752D35C5D2D9A144BCD35686DAD5E4F88CA64FB4E66BE356B0409974`
Analysis core manifest: `7AC7DE6EA59278B89E76B80E1EC0A46A8707AB4EAE4E95DFE7E627C56420D7BE`
S3R1 acceptance manifest: `79ED3C79B4F913C4B23500CF18EEFDF4EED6B53B37A7ACE5548B34074FDA4F7A`

## Package And Population

The accepted 24-event population remains 24 total (5 USD and 8 JPY primary rows after the frozen non-primary rows are accounted for), 14 directional, 13 primary market-scorable, one structural weekend exclusion, three NEUTRAL, and seven abstentions. Side-local primary counts remain USD 5 (1 SUPPORTIVE / 4 ADVERSE) and JPY 8 (7 SUPPORTIVE / 1 ADVERSE).

The exact excluded event remains `TN_BD340A6100B173B5F254EDC1`, USD SUPPORTIVE, `[2025-04-05T01:45:04Z, 2025-04-05T12:34:35Z)`, complete Saturday UTC. It is retained but never replaced or scored.

The four connected half-open clusters remain C1=5, C2=1, C3=2, and C4=5. Touching endpoints are not overlap.

## Hash Hierarchy

Level 1 consists of the S3R1 preregistration, primary-population, overlap-cluster, and invariance hashes. Level 2 computes `analysisCoreManifestHash` from canonical JSON containing the six S2R1-R1 upstream hashes and those four Level-1 hashes. Level 3 acceptance binds the core hash plus status, next gate, and all false access flags. The acceptance hash is deliberately excluded from the core input, so there is no cycle.

## Deterministic Diagnostics

The timing diagnostic uses exactly -7 and +7 calendar days, preserving side, frozen label, UTC clock, duration, half-open boundaries, tick validity, midpoint, and return rules. It is demonstrated only when all actual and shifted sets are complete and `H_actual` is strictly greater than both controls. Any tie is `TIMING_SPECIFICITY_NOT_DEMONSTRATED`; an incomplete shifted set is `TIMING_DIAGNOSTIC_INCOMPLETE`. This status never enters primary survival.

The permutation assumption is `CONDITIONAL_WITHIN_SIDE_LABEL_EXCHANGEABILITY_NULL`: labels are conditionally exchangeable within USD and independently within JPY, not randomized in the original experiment. The exact universe remains 40 assignments.

Timestamp metadata is declarative frozen metadata, not Git chronology or proof of human conception or absence of outcome exposure. The fixed authored timestamp is retained without `datetime.now()` regeneration.

Conflicting bid/ask records at one UTC timestamp are `DATA_CONFLICT_UNSCORABLE`; they are never averaged or resolved by source order. Identical duplicates may be deduplicated. A primary data conflict later invalidates the 13-event evaluation rather than shrinking its denominator.

## Boundary And Gate

No provider client, price/tick/candle/outcome loader, real result, S4 evaluator, Astra run, Founder Review input, SBC path, signed wave, pair resultant, magnitude, score, Auto Suggest, ML, MT5, or execution path exists in S3R1. All 16 access flags remain false. The package is ready for independent central review before the Astra pre-outcome adversarial audit; Astra and S4 remain blocked.
