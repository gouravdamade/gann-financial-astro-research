# Candidate C RUN1-R3R2A Production-Path Closure Freeze

## Scope

This freeze completes the pre-authorization production-path wiring only. It
does not evaluate any frozen Candidate C event, create an authorization record,
read market outcomes, or alter source/operator/evaluator/V2 science.

## Dual Provenance Views

The canonical Git view contains exact committed LF Git-blob bytes. The loader
view is an execution compatibility representation for artifacts that the
historical frozen loaders bound to CRLF checkout bytes. It is derived only by
`LF_TO_CRLF_RENDERING_V1`: raw `0A` becomes `0D0A`, with no parsing,
serialization, encoding conversion, or other edit.

The admission policy is
`FROZEN_LOADER_REQUIRED_TEXT_ARTIFACT_EXACT_LF_TO_CRLF_HASH_MATCH_ONLY`.
An artifact is rendered only when it is already in the frozen dependency graph,
has committed LF bytes with no CR byte, exactly reaches its historical loader
checksum after rendering, and round-trips exactly back to the Git bytes.
Canonical Git blobs remain the provenance authority. A loader-view rendering
is not a Git blob and has no source-doctrinal significance.

The final discovered rendered path set contains seven entries: the S1 ledger,
S2 ledger, unresolved registry, cross-text matrix, and the three declared
Trailokya YAML artifacts. Frozen A and B loaders both accepted the resulting
loader view without source changes.

## Production Boundary

The successor-owned A context adapter constructs the frozen template context
without calling A's synthetic admission gate for a real event. The future A,
B, and V2 architecture is one worker process per complete population role,
with zero scientific retries and an external immutable authorization record
required before any real worker could start.

The real population was read only for identity, structural, authorization,
bundle, and V2-bridge validation. No real evaluator row, comparison, market
access, outcome access, provider access, broker access, or Swiss Ephemeris
query occurred. `executionAllowed=false` remains active.

## Next Gate

`CENTRAL_REVIEW_CANDIDATE_C_RUN1_R3_PRODUCTION_PATH_CLOSURE`
