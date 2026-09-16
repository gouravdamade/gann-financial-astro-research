# MO-R4A-S4-O1 Outcome Evaluator Implementation Freeze

Status: `IMPLEMENTATION_FROZEN_BEFORE_OUTCOME_DATA`

The deterministic S4 evaluator is frozen before the first outcome inspection.
This record starts from `f9c2310a0513ffab7bf871d596a785173900afe6` and remains
bound to the accepted acquisition-provenance parent
`22558398ee323285a12b3f4f18a5db66092a8ea4`.

## Frozen contract

The evaluator is isolated in
`gann-astro-desk/backend/outcome_evaluation_s4.py`. It validates the committed
S3R1 population, interval, cluster, partition, manifest, acquisition-freeze,
and Astra disposition identities before any future parsed-capture adapter can
run. The implementation has no provider client, credential handling, raw BI5
decoder, or network capability.

The frozen study contains 24 events, 14 directional events, 13 primary events,
39 half-open analytical intervals, 40 side-local permutation assignments, and
four overlap clusters. The 15-partition manifest's parsed-record count is
validated as metadata only. The evaluator does not read those private parsed
captures during O1.

Endpoint selection is strictly inside `[applyingStartUtc, separatingEndUtc)`.
It uses the first valid tick at or after the start and the last valid tick
strictly before the end. Same-timestamp identical quotes may be deduplicated;
different quotes at the same timestamp are interval-scoped conflicts. Invalid
in-scope quotes, malformed canonical records, ordering errors, missing files,
unlisted files, hash mismatches, and manifest count mismatches fail closed.

The deterministic numeric implementation uses the native divisor `1000`,
exact Decimal midpoint arithmetic, precision 50, `ROUND_HALF_EVEN`, and
`ln(P_end / P_start)`. A zero return is `ZERO_MOVE` and a directional miss.
The expected-direction mapping remains validation-only and has no production
signal, pair, magnitude, or polarity output.

## O1 verification

The focused synthetic-only suite passes `49/49`. It covers half-open boundary
selection, duplicate and conflict handling, invalid data, direction mappings,
the exact 40-assignment null, observed-assignment inclusion, inclusive tail,
fixed denominator, C1-C4 weighting, timing strictness, survival boundaries,
deterministic result hashing, parsed-file hash-before-parse ordering, manifest
count enforcement, network/raw-decoder absence, and strict result schemas.

No real parsed JSONL or raw BI5 file was opened. No endpoint price, return,
hit, timing, cluster, or survival result was calculated from the real capture.
Provider/network calls during O1: `0`.

The canonical machine-readable freeze is
`status/acceptance/mo_r4a_s4_o1_outcome_evaluator_implementation_freeze.json`.
Its self-hash covers the complete record except the `selfHash` field. The
record includes the exact evaluator/test source hashes and all frozen upstream
identities from the acquisition and Astra gates.

## Locked boundary and next gate

`realParsedCaptureRead=false`, `marketOutcomeRead=false`,
`outcomeUnlocked=false`, `O2ExecutionAllowed=false`, and
`executionAllowed=false`. This milestone does not authorize O2 and does not
claim any market finding. Any future O2 invocation must be separately
authorized and must complete the all-file parsed SHA-256 pass before parsing
any JSONL record.

Next gate: `CENTRAL_REVIEW_FOR_S4_O2_OUTCOME_EXECUTION`.
