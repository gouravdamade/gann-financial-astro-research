# Phase 5B Multidimensional Ledger Acceptance Gates

Phase 5B, which is P2 of the multidimensional SBC roadmap, is accepted in
source only when all of the following pass:

1. Input gate: the compiler accepts only the canonical Phase 5A atomic series
   contract with timestamp-safe, no-lookahead, research-only guardrails.
2. Instrument gate: every ledger requires a non-empty opaque instrument
   identity. Changing it changes causal-cluster and ledger identities.
3. Causal-cluster gate: every primary contribution and explicit missing item
   receives a stable canonical SHA-256 cluster ID containing instrument,
   interval, cutoff, profile/source lineage, actor, target, and exact role.
4. Evaluation-separation gate: the causal-cluster ID does not absorb evaluated
   magnitude. The Phase 5A contribution ID remains the separate seal for
   nature, multiplier, signed units, status, explanation, and unknown reason.
5. Deduplication gate: exact repeats sharing one source lineage count once.
   Different contribution IDs sharing that lineage are rejected as a conflict.
6. Missing-evidence gate: explicit missing evidence receives its own stable
   lineage, remains unknown, and is never converted to zero.
7. Role gate: causal clusters are `PRIMARY_EVIDENCE`; ledger slices are
   `DERIVED_AXIS`; reconciliation and guardrails are `NON_VOTING_CONTEXT`.
   `VISUALIZATION_ONLY` is reserved and not emitted as evidence.
8. Axis gate: total, actor, target-layer, nature, figure-relative Vedha
   direction, and source-lineage views are produced from the same cluster set.
9. Unavailable-dimension gate: genuinely unavailable actor/layer/nature/ray
   values use the visible `UNAVAILABLE` sentinel. No value is inferred from a
   missing-evidence label.
10. Reconciliation gate: every cluster appears exactly once in every axis, and
    each axis reconciles favorable, adverse, net, true gross, scored, unknown,
    missing, and total counts to the scalar total.
11. Scalar-equivalence gate: the deduplicated total reproduces the Phase 5A
    ledger for every interval. A mismatch fails closed.
12. Unknown-magnitude gate: unknown magnitude is null whenever unresolved or
    missing evidence exists and is zero only when no unknown evidence exists.
13. Replay gate: contribution input order does not change cluster, cell,
    interval-ledger, series IDs, or serialization.
14. End-to-end gate: a real timestamp-safe Chakra Lab snapshot can flow through
    Phase 5A and Phase 5B while preserving source lineage and missing actors.
15. Isolation gate: the output is `SOURCE_PROFILED_EXPERIMENTAL`, has market
    directional weight `0.0`, and blocks FX subtraction, phase, confidence,
    market direction, Auto Suggest, live inference, official ML notes, shadow
    validation votes, trades, and MT5.
16. Regression gate: all earlier SBC, Vedha, Chakra, service, and
    instrument-relative FX tests continue to pass.

Passing these gates certifies deterministic evidence organization and
reconciliation. It does not certify Jyotisha doctrine, FX subtraction,
timing phase, financial usefulness, market direction, packaging, or execution.
