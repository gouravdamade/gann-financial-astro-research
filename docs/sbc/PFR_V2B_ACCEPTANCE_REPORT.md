# PFR-V2B Categorical Oscillator Pilot - Acceptance Record

Date opened: 2026-08-02

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

## Bounded V2B Sequence

1. V2B-1: migrate the primary research identity to independent USD and JPY
   side contracts, and correct candidate defaults to pending review.
2. V2B-2: compile chart-conditioned categorical visible-range intervals.
3. V2B-3: surface existing SBC atomic intervals as a separate visible-range
   field.
4. V2B-4 and V2B-5: synchronize range/time selection and render the
   founder-visible stack.
5. V2B-6: admit only a small, founder-reviewed side-level pilot.
6. V2B-7: run regressions, package one candidate, and stop for founder
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
  interval, plus preserved unknown gaps.
