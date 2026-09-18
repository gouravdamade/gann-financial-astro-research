# Candidate C EMP0-R2 Pre-Data Integrity and Authorization Closure

## Scope

EMP0-R2 is an additive successor to the immutable EMP0 and EMP0-R1 freezes.
It closes executable integrity boundaries before market-data selection or
acquisition. No provider, quote, price, return, outcome, p-value, or market
direction was read or created.

## Snapshot and Admission Integrity

The in-memory provider-neutral snapshot validator now requires canonical
`marketSnapshotHash`, provider/dataset identity, UTC coverage, 1--60 second
resolution, non-empty uppercase raw artifact hashes, exact raw `quoteCount`,
and bid/ask quote validation. It rejects a snapshot whose declared coverage is
narrower than the frozen Candidate C interval. Exact duplicate quotes may be
normalized only in the returned admitted view; `quoteCount` always remains the
raw array length.

A distinct future market-admission record binds one validated snapshot to the
R2 schema and data-admission contract. EMP0-R2 creates only the contract and
synthetic test coverage; no real snapshot or admission record exists.

## Test and Temporal Contracts

Every future test invocation is exactly one `USD` or `JPY` side, one canonical
source row slot, and one frozen horizon: 3,600, 21,600, or 86,400 seconds.
Mixed sides, mixed slots, non-eligible source states, non-finite returns, and
unregistered horizons fail before the statistic or permutation can run.

The temporal-null distribution is unchanged from EMP0-R1: it shifts labels
within a single side/row-slot/UTC-month block, allows individual monthly zero
offsets, and rejects only the global identity vector. R2 adds the fail-closed
bound of 100,000 deterministic full-vector attempts. It never forces a block
to move and fails if no non-identity vector can be generated.

## Immutable Future Authorization

The future empirical entrypoint accepts only a
`ValidatedEmpiricalExecutionAuthorization` produced by the canonical
self-hash validator. A plain mapping cannot authorize execution. A future
authorization must bind the executing accepted R2 freeze, implementation and
contract hashes, immutable source snapshot and eligibility, one admitted market
snapshot, its admission record, the frozen horizons, statistics, and one-shot
intent. Provider requery and post-hoc tuning are hard-false.

## Preserved Research Boundary

The 645-event / 5,160-row source snapshot, 16 eligibility cells, eight
source-testable cells, UNKNOWN abstention, rare-state exclusion, USD/JPY
separation, return definition, statistic, 4,999 replicates, Holm, and BH are
unchanged. The frozen future ledger has 24 rows: eight source-testable cells by
three horizons. Its status records future execution/missingness only; it does
not promote a source state.

EMP1 and EMP2 must use the frozen R2 code and contracts without changes. EMP1
may only admit and freeze raw market evidence; EMP2 may only use a separately
authorized, immutable admitted snapshot once central review permits it.

Next gate:
`CENTRAL_REVIEW_CANDIDATE_C_EMP0_R2_PRE_DATA_SNAPSHOT_INTEGRITY_AUTHORIZATION_AND_TEST_CELL_CLOSURE`.
