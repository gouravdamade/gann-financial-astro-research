# PFR-V2B Categorical Oscillator Pilot - Acceptance Record

Date opened: 2026-08-02

## PFR-V2B-R0 Remote Reconciliation

- Status: `COMPLETE` on 2026-08-02.
- The local V2B branch and `origin/master` both resolve to
  `9677b1bb7c8b8b0c040c88c4d1442c56196e04c2`. Although the named V2B branch
  is not a remote branch, the V2B-5 and V2B-6 source is deliberately present
  on the inspectable remote `master` commit.
- A clean remote clone reproduced that exact source with a clean worktree.
  Frontend: 32 files / 132 tests; backend: 181 tests; Rust: format, check, and
  18 tests all passed. Details:
  `docs/sbc/PFR_V2B_R0_REPOSITORY_RECONCILIATION.md`.
- This is a reproducibility record, not completion of V2B. The registries
  remain empty and the product still requires live-range binding, stepped
  visual fields, derived pair contract, and founder-reviewed evidence before
  packaging.

## V2B-0 Baseline and Freeze

- Branch: `pfr-v2b-categorical-oscillator`.
- V2A admission foundation: frozen at `b022b20` on entry to V2B.
- Founder physical U1-S1 check: `PASSED`. On 2026-08-02 at 20:40 IST, the
  founder confirmed that repeated wheel zoom retained aspect lanes and Live SR
  lines.
- Existing catalogue and packet registry: intentionally empty and unchanged.
- Existing candidate worksheet: remains `CANDIDATE_NOT_ADMISSIBLE`.
- Safety invariants: research-only; no polarity entry; no magnitude;
  `executionAllowed=false`; no automatic order placement; no aspect/SBC fusion.

## V2B-1 Independent FX Side Contracts

- Status: `COMPLETE` on 2026-08-02.
- `FX_CURRENCY:USD` and `FX_CURRENCY:JPY` are now the only accepted primary
  research identities. `FX_PAIR:USDJPY` returns `PAIR_DERIVATION_ONLY` and
  cannot silently resolve as a primary chart.
- Future evidence packets and catalogue entries require matching
  `sideIdentity` and `chartHypothesisId`. The production registries remain
  empty, so both side lookups correctly show a fail-closed missing state.
- The desktop panel shows both side states independently and downloads two
  non-admissible side worksheets with `PENDING_REVIEW` and
  `PENDING_FOUNDER_REVIEW` defaults. The pair event remains review context;
  its natal target is never copied into the primary side chart fields.
- Verification: catalogue `7 passed`, backend `4 passed`, focused desktop
  `21 passed`, API `8 passed`, lint and production frontend build passed.
- Details: `docs/sbc/PFR_V2B_1_FX_SIDE_CONTRACT.md`.

## V2B-2 Categorical Visible-Range Compiler

- Status: `COMPLETE` on 2026-08-02.
- Added the research-only `CHART_CONDITIONED_CATEGORICAL_RANGE_V1` compiler
  and private backend range route. A bounded side-chart input produces
  contiguous timestamp-safe intervals only: `SUPPORTIVE`, `ADVERSE`,
  `NEUTRAL`, `MIXED`, or an explicit `UNKNOWN` gap.
- An active unreviewed event always makes that atomic segment `UNKNOWN`; a
  known event cannot paint over absent evidence. `MIXED` retains separate
  supportive and adverse activity rather than inventing one combined sign.
- Corrected the lookup key: `chartHypothesisId` is now required alongside
  chart id, transit, natal target, and aspect for every event-level lookup.
- Verification: catalogue/range `9 passed`, backend `5 passed`, focused
  desktop/API `29 passed` when run individually, lint/build passed. Details:
  `docs/sbc/PFR_V2B_2_CATEGORICAL_VISIBLE_RANGE.md`.

## V2B-3 SBC Atomic Visible-Range Contract

- Status: `COMPLETE` on 2026-08-02.
- Added the private, read-only `SBC_ATOMIC_VISIBLE_RANGE_V1` service and
  `/api/chakra-lab/atomic-range` route. It presents the existing SBC atomic
  interval timeline with its original boundaries, evidence cutoffs, source
  lineage, guidance availability, and unaltered research-ledger summary.
- SBC remains an independent synchronized comparison field:
  `aspect_relationship=NOT_AUTOMATIC_CONFIRMATION` and
  `magnitude_state=NOT_CONFIGURED`. The response cannot call the aspect
  compiler, infer market direction, or remove any existing execution lock.
- Verification: full Chakra Lab service suite `26 passed`; Python compile and
  direct contract smoke check passed. Details:
  `docs/sbc/PFR_V2B_3_SBC_ATOMIC_VISIBLE_RANGE.md`.

## V2B-4 Shared Range Coordinator

- Status: `COMPLETE` on 2026-08-02.
- Added `SYNCHRONIZED_INDEPENDENT_RANGE_V1` and the private
  `/api/independent-fields/synchronized-range` route. One explicit UTC range
  is now supplied to the independent USD categorical field, independent JPY
  categorical field, and existing SBC atomic field.
- The coordinator fails closed if the SBC first boundary or any compiled field
  does not exactly match the requested range. It returns those three outputs
  side by side without calculating a combined sign, amplitude, or decision.
- Verification: aspect/SBC/coordinator regression suite `33 passed`; Python
  compile and whitespace checks passed. Details:
  `docs/sbc/PFR_V2B_4_SHARED_RANGE_COORDINATOR.md`.

## V2B-5 Founder-Visible Independent Stack

- Status: `COMPLETE` on 2026-08-02.
- The Chakra workspace now exposes a `Fields` control that opens three compact
  lanes for one exact displayed chart range: USD categorical side context, JPY
  categorical side context, and SBC atomic availability. Every lane stays
  independent and shows its own categorical state and hover explanation.
- Because no immutable side-chart evidence has been admitted, the USD and JPY
  lanes correctly show `UNKNOWN`; current pair-chart events are not copied into
  either primary side. SBC remains an independent availability timeline.
- Verification: focused desktop tests `13 passed`, production build passed,
  Rust `cargo check` passed, and aspect/SBC/coordinator regression suite `33
  passed`. Details: `docs/sbc/PFR_V2B_5_FOUNDER_VISIBLE_STACK.md`.

## V2B-6 FX Side Pilot Readiness

- Status: `COMPLETE` on 2026-08-02 as a read-only readiness surface; no side
  evidence was fabricated or admitted.
- Added `FX_SIDE_POLARITY_PILOT_STATUS_V1`. It reads the existing immutable
  packet registry and matching catalogue per USD/JPY side, reporting reviewed
  record counts, present/missing `SUPPORTIVE` and `ADVERSE` states, blockers,
  and retained unknown gaps.
- Current result is correctly `PILOT_EVIDENCE_PENDING`: both production side
  registries remain empty. The Chakra `Fields` stack now makes that fact
  visible and can refresh after a separately reviewed registry update.
- Verification: backend `36 passed`, desktop tests `14 passed`, production
  build and Rust `cargo check` passed. Details:
  `docs/sbc/PFR_V2B_6_FX_SIDE_PILOT_READINESS.md`.

## Bounded V2B Sequence

1. V2B-1: migrate the primary research identity to independent USD and JPY
   side contracts, and correct candidate defaults to pending review.
2. V2B-2: compile chart-conditioned categorical visible-range intervals. `COMPLETE`.
3. V2B-3: surface existing SBC atomic intervals as a separate visible-range
   field. `COMPLETE`.
4. V2B-4: synchronize range/time selection. `COMPLETE`.
5. V2B-5: render the founder-visible stack. `COMPLETE`.
6. V2B-6: add a read-only founder-reviewed side-level pilot readiness check. `COMPLETE`.
7. V2B-7: run regressions, package one candidate, and stop for founder
   acceptance.

## Non-Negotiable Boundaries

- USDJPY is a derived pair view. It must not become the silent primary
  catalogue identity.
- No universal aspect direction, numerical magnitude, smoothing, calibration,
  curve fitting, fusion, ML, Auto Suggest, live inference, MT5 execution, or
  trading is part of V2B.
- A packaged production mode must never present a synthetic test fixture as
  accepted research evidence.
- V2B is only complete after a founder-accepted candidate has a small real
  reviewed side-level pilot with both a positive and negative categorical
  interval, plus preserved unknown gaps. V2B-6 only exposes the pending
  evidence status; it does not satisfy this final acceptance condition.
