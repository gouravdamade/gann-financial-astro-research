# PFR-C1 Product Integrity Acceptance Report

Status: in progress  
Branch: `product-first-sbc-phase-lab`  
Scope: bounded correction only; no execution or model-promotion authority.

## C1-1 Status and Traceability

Completed on 2026-08-01.

- ADR-0018 defines the correction scope, locks, and stop condition.
- The product-first gap matrix now records PFR-2, PFR-3, PFR-4, and PFR-5 as
  partial/prototype work rather than complete milestones.
- The original PFR definitions are preserved. PFR-C1 is not PFR-8.

## C1-2 USD/JPY Evidence Contract

Completed on 2026-08-01.

- `GANN_FX_PAIR_EVIDENCE_V2` is now assembled by the backend from the
  timestamp-safe touch context and is explicit about USD/JPY identity,
  reference mapping, state, as-of time, and evidence cutoff.
- Each currency preserves supportive units, adverse units, net units, gross
  activation, conflict, eligible/scored/unresolved counts, and an explicit
  `KNOWN` / `UNKNOWN` / `BLOCKED_MAPPING` state.
- The pair surface now consumes backend values for net difference, joint net
  strength, and common activation. Common activation is the mean of the two
  gross activations, never an average of cancelling net values.
- The interface labels this as read-only descriptive research. It does not
  produce a prediction, vote, execution permission, or automatic order.

## Remaining Acceptance Work

- C1-3: deterministic per-event timing phase V1.
- C1-4: fixed-wheel semantic correction.
- C1-5/C1-6: timing visual integrity, opt-in flag, and accessibility.
- C1-7: complete regression, corrected Windows candidate, and founder review.

## Invariants Confirmed

`executionAllowed=false`, `automaticOrderPlacement=false`, `voteWeight=0`,
`directionalContribution=0`, and `fusionCoefficient=0` remain mandatory.
The scalar baseline, no-lookahead behavior, evidence cutoff, and explicit
unknown handling remain mandatory as well.
