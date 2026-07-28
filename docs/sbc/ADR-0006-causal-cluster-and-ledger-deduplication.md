# ADR-0006: Causal Cluster and Ledger Deduplication

Status: accepted for P2 source implementation

Date: 2026-07-28

## Context

Phase 5A produces timestamp-safe atomic intervals with source-lineage and
evaluated-contribution identities. The same primary Vedha fact can later appear
in several useful views: actor, target layer, nature, Vedha ray direction, and
source lineage. Counting those views as separate observations would multiply
one cause into several votes.

P0-R5 also requires a canonical causal-cluster identity that includes the
instrument, interval, evidence cutoff, source/profile hashes, actor, target,
and exact derivation role.

## Decision

1. P2 uses four exact derivation roles:
   - `PRIMARY_EVIDENCE`: one source-backed contribution or explicit missing
     evidence record;
   - `DERIVED_AXIS`: a non-voting actor, target-layer, nature,
     Vedha-direction, source-lineage, or total view;
   - `VISUALIZATION_ONLY`: a later display projection with no evidence weight;
   - `NON_VOTING_CONTEXT`: reconciliation, guardrails, and explanatory
     metadata.
2. A causal-cluster ID is the SHA-256 hash of canonical content containing:
   - the opaque instrument identity;
   - atomic interval start and end;
   - evidence cutoff;
   - foundation, grid, and Vedha profile IDs and hashes plus guidance model;
   - interval source IDs;
   - evidence kind;
   - source-lineage ID;
   - actor and source nakshatra when available;
   - target coordinates, layer, value, witness set, and evidence status when
     available;
   - the exact derivation role.
3. Evaluated values are not part of the causal-cluster identity. The existing
   `contribution_id` seals nature, multiplier, signed units, status,
   explanation, and unknown reason separately.
4. Within one atomic interval, one source-lineage ID may resolve to only one
   evaluated contribution:
   - an exact repeated contribution is deduplicated;
   - different contribution IDs for the same lineage are a conflict and the
     compiler fails closed.
5. Explicit missing-evidence IDs receive a deterministic missing-evidence
   lineage. Repeated identical missing IDs are deduplicated.
6. Every causal cluster appears exactly once in every derived axis. Where a
   dimension is genuinely unavailable, the key is the explicit sentinel
   `UNAVAILABLE`; no actor, nature, layer, or direction is invented.
7. The total cell must reproduce the Phase 5A scalar ledger. Every other axis
   must reconcile to that total for favorable, adverse, net, true gross,
   scored, unknown, missing, and total counts.
8. `vedha_direction` means figure-relative Jyotisha ray direction. It is not a
   bullish or bearish market direction.
9. P2 remains `SOURCE_PROFILED_EXPERIMENTAL`, has voting weight `0.0`, and is
   disconnected from phase, confidence, market direction, Auto Suggest, live
   inference, official ML notes, shadow validation, trades, and MT5.
10. P2 accepts an opaque `instrument_identity` only to satisfy provenance and
    cluster isolation. It does not perform base-minus-quote FX arithmetic.

## Consequences

- The ledger can be sliced several ways without increasing evidence weight.
- Conflicting evaluations sharing one lineage are visible errors instead of
  silent double counting.
- Missing evidence participates in coverage and reconciliation without being
  converted to zero.
- A later UI can link dimensions through stable cluster IDs.
- FX subtraction, phase, confidence, and financial use remain separate future
  gates.

## Rejected Alternatives

- Hashing display labels or broad event names.
- Including evaluated magnitude in the causal-cluster identity.
- Counting actor, layer, nature, and direction views as independent evidence.
- Choosing one of two conflicting evaluations for the same source lineage.
- Dropping missing evidence from dimensional reconciliation.
- Treating figure-relative Vedha direction as market direction.
