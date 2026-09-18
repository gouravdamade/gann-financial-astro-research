# Candidate C EMP0-R1 Pre-Data Analysis Path and Temporal Null Closure

## Purpose

EMP0-R1 is a successor to the historical outcome-blind EMP0 freeze at commit
`91a501c78613ad5c83dd95013cbba83387cdd041`. It does not rewrite that
historical record or access market data. It corrects two pre-data defects found
in central review: fake-only analysis-core admission and an overly restricted
monthly circular-shift null.

## Provider-Neutral Frozen Core

The reusable market-schema validator now accepts any non-empty future admitted
provider and dataset identity. It remains a pure in-memory validator: it has no
provider client, network call, credential access, quote acquisition, or market
snapshot in this milestone.

The statistical core is likewise generic over supplied normalized observations.
Its future execution wrapper requires a separate immutable authorization with:

- `outcomeAnalysisAuthorized=true`;
- `marketSnapshotAdmitted=true`;
- a bound `marketSnapshotHash`; and
- a bound `analysisImplementationManifestHash`.

No such authorization or admitted snapshot exists in EMP0-R1. The current
records therefore keep provider selection, acquisition, market outcome access,
and real statistical execution false. The same frozen code can later process a
properly admitted immutable snapshot without a parallel real-only
implementation.

## Corrected Temporal Null

The null remains unsigned and preserves return observations, side identity, and
UTC-month strata. For every side/month block of size `m`, its deterministic
monthly offset is now `SHA-256(...|attemptIndex) mod m`; a zero offset is valid
for an individual month.

The joint vector is rejected only when every monthly offset is zero. In that
case the deterministic attempt index increments until at least one block shifts.
The observed arrangement remains separately accounted for by the frozen
`(1 + exceedances) / 5000` correction. There are exactly 4,999 null replicates.

## Preserved Source State

The predecessor's 645 events, 5,160 source states, eight frozen source slots,
V2 projection identity, A/B semantic agreement, USD/JPY separation,
`SOURCE_UNKNOWN_ABSTAIN` handling, and 8-of-16 source testability matrix are
unchanged. This successor does not create a direction, weight, pair field,
score, forecast, or execution rule.

## Verification and Boundary

Focused fake/synthetic regression verifies provider-neutral validation, future
authorization rejection, generic deterministic-core reproducibility, individual
monthly zero-offset admission, and global all-zero rejection. No quote, price,
return, p-value, provider, broker, or market outcome has been read or computed.

Next gate:
`CENTRAL_REVIEW_CANDIDATE_C_EMP0_R1_PRE_DATA_REAL_ANALYSIS_PATH_AND_TEMPORAL_NULL_CLOSURE`.
