# PFR-V2B-R5-F4-A-P3 Founder UX Compaction

## Disposition

Implemented on branch `research/pfr-v2b-r5-f4-a-p3-founder-ux-compaction`
from required starting commit `8afde8acec6d48c9cf7e7ce7c3962f13e80363f3`.
The implementation commit is `be3e4fcd6061b2e92022c7ef7b2f3b304f0dee1a` (`feat(fields): improve activity
discovery and compact empty fields`). Central review is pending.

This is a frontend-only founder UX pass. It does not change the unsigned
activity contract, event compiler, directional mathematics, polarity
catalogue, source doctrine, backend API, provider access, outcome handling,
Candidate C, EMP3, MT5, or execution behavior.

## Product Changes

- The existing chart indicator control now has an always-visible `INDICATORS`
  label and an accessible `Indicators` toolbar name. RSI and Fields & Waves
  controls remain the existing controls.
- The Fields workspace now exposes `Add USD/JPY Activity to Chart` at the top
  of the existing research surface. The parent-owned action enables the
  existing `fieldsWaves.activityVisible` layout setting, returns to Chart,
  and leaves the existing chart range, markers, drawings, RSI, symbol, and
  timeframe state under the existing layout controller. It adds no new API
  endpoint or activity-specific fetch.
- A dirty Founder Review disables the navigation CTA and explains that the
  review must be saved or discarded first. The existing parent navigation
  guard remains in force, so no partial layout mutation is allowed.
- Mode 1 zero-coverage USD/JPY/pair directional fields are summarized as one
  compact availability panel. Existing detailed categorical panes are
  available through an explicit `Show research details` disclosure and retain
  their unknown evidence.
- Mode 2/3 and source-policy-withheld directional surfaces are represented by
  one policy summary without directional state, known counts, pair values, or
  detail-pane ARIA exposure. Known directional data remains detailed. SBC,
  pilot, and unsigned activity surfaces are unchanged.

## Verification

- Focused Fields and indicator-toolbar tests: **38/38 passed**.
- Full frontend suite: **238/238 passed across 48 files**.
- TypeScript project build: **passed**.
- Oxlint: **passed**.
- Vite production build: **passed**; the existing main-chunk size advisory
  remains.
- `git diff --check`: **passed**.
- Browser visual smoke with the real local frontend/backend: **passed** for
  the visible `INDICATORS` toolbar, top-level Fields CTA, and activation into
  the existing chart with the unsigned activity pane visible. Native Windows
  1280x800 screenshot QA was not run in this source-only milestone.
- No backend or Rust/Tauri source changed; no backend or packaging run was
  required by P3.

## Boundaries and Locks

- `activityMathChanged=false`
- `backendChanged=false`
- `polarityCatalogueChanged=false`
- `pairMathChanged=false`
- `f4bImplemented=false`
- `f4cImplemented=false`
- `candidateCAccessed=false`
- `emp3Accessed=false`
- `providerAccessed=false`
- `outcomesAccessed=false`
- `executionAllowed=false`
- polarity, score aggregation, Auto Suggest, ML, MT5, order placement, and
  market-direction output remain disabled.

The earlier immutable P2 candidate remains unchanged. No Windows candidate is
created by P3.

Next gate:
`CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P3_FOUNDER_UX_COMPACTION`.
