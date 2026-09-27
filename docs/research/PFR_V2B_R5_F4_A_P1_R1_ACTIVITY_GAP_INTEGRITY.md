# PFR-V2B-R5-F4-A-P1-R1 Activity Gap Integrity

## Disposition

Implemented on branch `research/pfr-v2b-r5-f4-a-p1-r1-activity-gap-integrity`,
from required starting tip `789fdf6d9619ac9c0a24b13ba4b5e0e7b4e55925`.
The implementation commits are `8fbe646cfc1ab184a1887c5e104ef895704a9636`
(`fix(chart): preserve unloaded activity gaps`) and
`f25cbc4e066870b8af02ec855aaa94ccdcb210d8` (`fix(chart): normalize cached
activity interval edges`). The final epoch-order regression assertion is
`c9d1b05b9efa21fc3ae5fe06c8d1319abd0a31b8`. This record supersedes the P1
status for current behavior while preserving the original P1 report and
implementation history. Central review is pending.

## Integrity Correction

- Activity intervals are sorted and compared using parsed epoch seconds.
- A noncontiguous interval boundary inserts a native Lightweight Charts
  whitespace datum at the prior loaded interval end. No count is fabricated;
  there is no zero, carry-forward, or interpolation across the unloaded hole.
- Epoch-adjacent intervals remain connected even if their ISO timestamp strings
  use different UTC-offset spellings.
- Cached interval identities and ordering use parsed epoch timestamps, so an
  equivalent ISO spelling does not create a duplicate edge. Exact duplicate
  interval edges are emitted once. Exact-event markers are omitted unless their
  event time belongs to a loaded activity interval.
- A crosshair over an absent interval reports `DATA NOT LOADED`. This differs
  from a loaded known zero (`0 observed | coverage known`) and from a loaded
  unknown interval (`Coverage incomplete | no confirmed events`, with its
  activity-only hatch).
- Unknown-coverage hatching is built only from returned `UNKNOWN` intervals;
  it does not span unloaded time.
- Visible ranges intersecting more than 12 chunks load only the existing
  centered 12-chunk bound and report `bounded_partial`, with visible text that
  history outside the loaded window is `DATA NOT LOADED`. They are never
  reported `ready`.
- The fixed chunk size, maximum request count, LRU capacity, and no-adjacent-
  prefetch policy are unchanged.

## Verification

- Focused activity/controller tests: 16 passed across 2 files.
- Full frontend: 233 passed across 47 files.
- TypeScript project build: passed.
- Oxlint: passed.
- Vite production build: passed; the existing main-chunk size advisory remains.
- `git diff --check`: passed.
- No backend or Rust/Tauri source changed.

## Scope and Locks

This correction is limited to activity-series gap rendering, loaded-time
readout/marker integrity, and honest bounded-range status. The chart/pane
registry, chart layout, market event markers outside this correction, unsigned
activity values, Fields directional surfaces, and backend contract were not
redesigned. No polarity, evidence/catalogue, pair-field, source-doctrine,
F4-B/F4-C, Candidate C, EMP3, provider, or outcome behavior changed. No market
data or outcomes were read; no provider was accessed; no MT5 order was invoked.
`executionAllowed=false`.

Next gate: `CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P1_R1_ACTIVITY_GAP_INTEGRITY`.
