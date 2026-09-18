# Candidate C RUN1-R3R3-R2 Frozen V2 Multi-Class Mismatch Accounting

## Correction Scope

R3R3-R1 incorrectly imposed a one-class-per-mismatch-record condition on the
successor audit helper. The protected V2 comparator at
`52c3b287a70018370e153a77b84c36e6b0dbfb42` instead emits a sorted, unique
`mismatchClassifications` list and can place several frozen taxonomy classes in
one immutable mismatch record. No protected V2 source, evaluator source,
worker, runtime protocol, source contract, population, row universe, bundle,
or result path was changed.

R3R3-R2 makes the audit layer mirror that frozen V2 representation. It keeps
the raw V2 records unchanged and distinguishes the number of mismatch records
from the number of classification occurrences. A valid multi-class mismatch is
therefore frozen as a semantic mismatch rather than being turned into an audit
execution failure.

## Accounting Contract

Every record must contain a non-empty, sorted, duplicate-free list drawn only
from the 17-class protected V2 taxonomy. `totalMismatches` is
`len(mismatchRecords)`. `totalMismatchClassifications` is the sum of all list
lengths and equals `sum(mismatchCountsByClass.values())`. It may exceed the
record count. Exact agreement remains defined exclusively by zero mismatch
records.

An isolated fake protected-V2 invocation produced a single record with five
classes: `COMPONENT_MISMATCH`, `CONTRACT_MISMATCH`, `OPERATOR_MISMATCH`,
`PROFILE_MISMATCH`, and `SOURCE_VALUE_MISMATCH`. The successor helper accepted
the untouched record, counted all five occurrences, and left its canonical
hash unchanged.

## Preserved Execution Boundary

The production-relative first-result paths remain unchanged and are used by
preflight, writer, fake temporary execution, and replay prevention. Full
5,160-row A/B universe validation remains mandatory before either raw artifact
is frozen. The successor manifest binds the corrected controller implementation
`b86bcea7599300d5598cbee0d69bc9639e8d5246` and the same protected A/B/V2,
bundle, population, and bridge identities.

Only fake `FAKE_REAL_RUN1_` events were used. No real Candidate C event was
evaluated, no real output was produced or inspected, and no market, outcome,
provider, broker, or Swiss Ephemeris resource was accessed. AUTH1 requires
zero scientific, V2, worker, execution, bundle, result-path, audit, or
mismatch-accounting code changes.

Next gate: `CENTRAL_REVIEW_CANDIDATE_C_RUN1_R3R3_R2_FROZEN_V2_MULTICLASS_MISMATCH_ACCOUNTING`.
