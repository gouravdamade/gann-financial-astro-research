# PFR-C1 Product Integrity Acceptance Report

Status: corrected candidate packaged; founder acceptance pending
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

## C1-7 Regression, Packaging, and Founder Review

Completed for the corrected candidate on 2026-08-01.

- The complete PFR-C1 regression passed: frontend lint, focused frontend
  mode/product tests, the production frontend build, and the focused SBC Python
  suite.
- The corrected Windows candidate is `Gann Astro Desk 0.10.28`, packaged at
  `releases/GannAstroDesk-0.10.28-three-mode-boundary/`. Both the installer and
  portable distribution were produced from this branch revision.
- Native smoke testing confirmed that the portable launcher and its adjacent
  backend start together from the release directory. This proves the candidate
  can be opened; it does not substitute for founder workflow acceptance.
- The corrected boundaries were re-checked: score-suppressed modes cannot
  expose scalar audit/package data, all three modes retain their own visible
  identity, and the execution/fusion locks remain in force.

## Remaining Acceptance Work

- Founder review of the exact `0.10.28` packaged candidate. The review must
  confirm that the founder can select a market period, change modes, inspect
  the synchronized views, and export the visible research state. No new
  product, certification, inference, ML, or execution work is authorized by
  this report until that review is recorded.

## Invariants Confirmed

`executionAllowed=false`, `automaticOrderPlacement=false`, `voteWeight=0`,
`directionalContribution=0`, and `fusionCoefficient=0` remain mandatory.
The scalar baseline, no-lookahead behavior, evidence cutoff, and explicit
unknown handling remain mandatory as well.
