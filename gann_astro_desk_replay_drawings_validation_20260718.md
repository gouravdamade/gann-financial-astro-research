# Gann Astro Desk Replay, Drawings, Decision, And Validation Evidence

Date: 2026-07-18

Status: verified source milestone; native stable remains 0.10.8.

## Scope

This milestone implements four related safety and workflow upgrades:

1. timestamp-safe Bar Replay;
2. drawing favorites, magnet modes, groups, and synchronization;
3. staged Auto Suggest decision logic;
4. machine-readable external-astrology and prospective-validation gates.

It does not authorize live order placement and does not promote a new native
package.

## Timestamp-Safe Bar Replay

Contract: `GANN_TIMESTAMP_SAFE_BAR_REPLAY_V1`

- `/api/chart` accepts `replayCutoff`.
- Only candles closed by the cutoff are returned.
- Events that have not started are omitted.
- Active event and regime intervals are clipped to the cutoff.
- Future outcomes, review labels, and return-derived fields are removed.
- Occurrence counts are recomputed from records known by the cutoff.
- SR touches become visible only after the relevant candle closes.
- Live refresh pauses while replay is armed.
- UI controls support cutoff selection, previous/next closed bar, play/pause,
  and exit.

Interactive QA moved a 241-bar chart to 113 known bars at the selected cutoff.
Visible aspect records fell from 47 to 19, confirming future records were not
merely hidden cosmetically.

## Drawing Workflow

- Favorites are persistent per saved chart layout.
- Magnet modes are explicit: off, weak OHLC snap, and strong OHLC snap.
- Keep-drawing mode supports repeated use of one tool.
- Drawings can be assigned to named groups.
- Groups can be renamed, hidden, locked, or deleted when unlocked.
- Sync scope can be layout-local or same-symbol.
- Same-symbol records are stored separately in
  `app_chart_synced_drawings`, allowing reuse across layouts and timeframes
  without leaking drawings to another symbol.

Responsive QA confirmed the Drawing Objects button and panel remain reachable
at a 970 px viewport.

## Auto Suggest Decomposition

`reviewer_rule_replay.py` now separates:

- evidence collection;
- baseline marker selection;
- support and attribution-boundary analysis;
- marker-flow alternatives;
- deterministic finalization.

The legacy monolithic implementation is removed. Golden fixtures preserve the
current decisions for cases 8, 43, 103, 127, and 185.

## External Astrology Gate

Contract: `GANN_ASTRO_EXTERNAL_CERTIFICATION_GATE_V1`

The gate expects 70 independent strength comparisons:

- five fixtures;
- seven classical planets;
- Shadbala total and Drik Bala for each planet.

The import rejects duplicate, unknown, unsourced, and non-numeric strength
records. Shadbala/Drik comparisons use a 0.5 virupa tolerance. A passing
research gate still cannot enable execution.

Current result:

- 25 astronomy/Panchanga rows pass;
- 70 Shadbala/Drik strength rows fail;
- 0 strength rows remain pending;
- status is `failed_external_validation`;
- `certified=false`;
- `executionAllowed=false`.

A PyJHora 4.8.7 wheel is hash-pinned locally as a secondary comparator. Its
70-row export was admitted reproducibly as
`pyjhora_external_strength_values_20260718.csv` (SHA-256
`29A88901CEE0821F3F20C75777D2BDDACDB9524EB253939D9263E693CBDEE9C9`).
The result is disagreement evidence, not independent certification.

Initial diagnosis shows a likely Drik normalization difference: dividing many
local values by four produces a close match, with residual differences around
dynamic Moon/Mercury benefic classification and special-aspect handling.
Shadbala totals show broader component-level differences. The implementation is
therefore left provisional until each component is reconciled against a second
trusted calculator or a saved worked classical example.

## Validation Matrix

Contract: `GANN_RESEARCH_VALIDATION_GATE_MATRIX_V1`

The `/api/validation-gates` endpoint and workspace strip expose:

| Gate | Current state |
| --- | --- |
| Timestamp-safe inference | passed |
| External Shadbala / Drik | failed |
| Purged retrospective policy | failed |
| Prospective shadow trial | collecting |
| Candlestick agent | failed, non-blocking |
| Order execution authorization | locked |

The frozen retrospective result is 258 watches / 355 clusters, 54.26% hit
rate, Wilson 95% interval 48.17%-60.24%, two-sided binomial p=0.190975, and
mean signed 72-hour return +0.0276%.

Prospective promotion requires at least 100 watch clusters, at least 10%
coverage, Wilson lower bound above 0.5, p below 0.05, positive mean signed
return, and four calendar months in one immutable cohort.

## Verification

- Entire Python repository: 245 tests passed.
- Backend: 96 tests passed.
- Auto Suggest golden suite: 7 tests passed.
- Frontend: 38 tests across 12 files passed.
- Oxlint: passed.
- TypeScript app and Node configurations: passed.
- Vite production build: passed.
- Browser console: zero warnings/errors during replay, drawing-panel, and
  validation-strip QA.

The final Vite build used an alternate writable output directory because the
desktop sandbox denied build-cache writes on D:. The source graph and compiler
inputs were unchanged.

## Promotion Decision

Do not promote a native package from this milestone yet. Keep stable 0.10.8
until:

1. the source changes complete native packaging and the authenticated soak;
2. external strength evidence is either accepted or remains visibly blocked;
3. the prospective cohort continues without policy mutation;
4. weekend/stale MT5 time normalization does not get weakened to manufacture a
   passing live-readiness check.
