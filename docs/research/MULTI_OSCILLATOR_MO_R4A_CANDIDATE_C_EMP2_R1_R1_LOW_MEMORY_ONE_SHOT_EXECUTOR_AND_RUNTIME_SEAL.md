# Candidate C EMP2-R1-R1 Low-Memory One-Shot Executor Seal

## Purpose

EMP2-R1-R1 supplies an additive bounded-memory successor to the frozen EMP0-R3-R1
EMP2 executor. It exists to make a future one-shot empirical run feasible on the
current 16 GB host without changing a scientific, market, source, statistical,
or result-artifact contract.

This milestone is outcome-blind implementation closure. It does not create a
real authorization, run EMP2, join real Candidate C events to market data, or
create the canonical EMP2 result.

## Runtime Order

`execute_emp2_low_memory_once(repo_root, private_raw_dir,
market_admission_record, authorization_record)` accepts no output root,
provider client, event list, horizon list, statistic option, or alternate
snapshot identity.

Before source records are traversed, it requires the canonical result path to
be absent, verifies the successor runtime, verifies the accepted 80-partition
market stream and canonical market identity, verifies the frozen market
admission record, and applies the historical frozen authorization validator.
Only after those gates pass can it derive internally bound return requests from
the frozen source snapshot, eligibility contract, and 24-row ledger.

The market pass retains only quotes selected for these internally derived
anchors. Quote selection remains first quote at or after the anchor within 60
seconds, with no interpolation, fill, prior quote, or backfill. Midpoint and
log-return definitions are unchanged.

## Frozen Reuse

The successor invokes the historical frozen deterministic permutation test,
Holm adjustment, Benjamini-Hochberg adjustment, result finalizer, and atomic
first-result writer. It binds the accepted `market_stream.py` and exact
Dukascopy parser bytes in addition to its own code and tests.

Synthetic-only equivalence coverage compares all 24 ledger rows and both
families against the historical executor. It covers fully populated rows,
unavailable P0 and PH, below-threshold states, zero outcome variance, shared
anchor quote resolution, 60-second boundary behavior, and closed-market gaps.

## Boundary

The canonical result path remains absent. No real Candidate C event timestamp,
P0, PH, return, statistic, p-value, direction, weight, authorization, or EMP2
result was produced. Provider calls are zero. `executionAllowed=false` remains
the current state.

Next gate:

`CENTRAL_REVIEW_CANDIDATE_C_EMP2_R1_R1_LOW_MEMORY_ONE_SHOT_EXECUTOR_AND_RUNTIME_SEAL`
