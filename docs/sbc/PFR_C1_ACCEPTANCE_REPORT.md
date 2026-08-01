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

## C1-3 Per-Event Timing Phase

Completed on 2026-08-01.

- The timing lab now selects only aspect windows active at the pinned
  timestamp. It does not select a nearest window before or after the moment.
- Every active event has an independent applying/exact/separating lifecycle,
  timing displacement, and vector identity. Overlapping events are separate
  event-contribution vectors rather than one common rotation.
- The summary remains an experimental visualization aggregate only. It keeps
  `ABSTAIN`, zero vote weight, zero directional contribution, zero fusion, and
  execution locked.

## C1-4 Fixed Wheel Semantics

Completed on 2026-08-01.

- The fixed 0/pi wheel continues to be a scalar parity visualization, but its
  rays are now exact horizontal rays on the real axis. There are no artificial
  vertical offsets or implied extra angles.
- The wheel visibly distinguishes gross scalar magnitude (dashed gross ring),
  real-axis resultant, a visual-only near-zero marker, and an unresolved tray.
  Individual inspection is done through 0/right and pi/left visual-only groups.
- This did not alter source ledger values, the backend scalar-parity contract,
  timing status, votes, fusion, or execution locks.

## C1-5/C1-6 Timing Integrity, Opt-In, and Accessibility

Completed on 2026-08-01.

- The timing aggregate now shows the count of supportive and adverse source
  contributions separately, while retaining the original source polarity on
  every event-contribution vector. It never labels the geometry bullish or
  bearish.
- The panel explicitly presents per-event lifecycle/phase, real and imaginary
  components, resultant, gross, coherence, conflict, safe-sector state,
  unresolved evidence, and `ABSTAIN`. A near-zero resultant remains null for
  collective phase and suppresses interpretation without deleting vectors.
- The production feature is disabled unless the dedicated build environment
  sets `VITE_ENABLE_TIMING_PHASE_EXPERIMENT=true`. The comparison card remains
  descriptive when the experiment is unavailable.
- A deterministic Python mirror now compiles active-event timing geometry with
  a stable calculation ID for replay inspection. It carries the same zero-vote,
  no-execution guardrails as the UI and has a focused overlap regression test.
- Fixed wheel groups are native keyboard-reachable buttons with pressed state;
  their labels convey side and magnitude without relying on color alone.

## Remaining Acceptance Work

- C1-7: complete regression, corrected Windows candidate, and founder review.

## Invariants Confirmed

`executionAllowed=false`, `automaticOrderPlacement=false`, `voteWeight=0`,
`directionalContribution=0`, and `fusionCoefficient=0` remain mandatory.
The scalar baseline, no-lookahead behavior, evidence cutoff, and explicit
unknown handling remain mandatory as well.
