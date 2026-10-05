# PFR-V2B-R5-F5-P1 Founder-Visible Research Explanation

Date: 2026-10-05

## Implementation Identity

- Milestone: `PFR-V2B-R5-F5-P1`
- Status: `P1_IMPLEMENTATION_COMPLETE_PENDING_CENTRAL_REVIEW`
- Branch: `research/pfr-v2b-r5-f5-p1-explanation-implementation`
- Starting commit: `3fa20691b668b028d7c8c24e4076fa4ee509c5b4`
- Accepted product ancestor: `c52c22916b9c1dc6610f99c678d732ec2117f557`
- Final branch tip: enclosing implementation commit; exact SHA is reported in the implementation closeout.
- Scope: frontend-only explanation/provenance inside the existing Unified Research Inspector.

## Implementation

A pure `buildFieldsResearchExplanation` adapter derives a string-only explanation
from the current `FieldsResearchSelection` and resolved `VisualizationModePolicy`.
It handles `FIELD_INTERVAL`, `PAIR_INTERVAL`, `ACTIVITY_EVENT`, `SBC_INTERVAL`,
and `BPHS_INTERVAL`; null selection retains the existing empty state.

The inspector now renders an `Explanation and provenance` subsection after the
existing selection-specific details and before shared metadata. Astronomy,
source doctrine, astrology interpretation, engineering transform, market bridge,
and financial validation remain separately labeled. Exact absent locators use
`NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT`.

The adapter uses `visualizationPolicy.scoringVisible` as its sole directional
visibility gate. With the gate closed, the field and pair branches use only
selection identity/time metadata and policy status. They return before reading
the selected interval object, so directional states, interval reasons, and
numeric pair values never enter explanation-model state. Mode 2 retains
`SOURCE_MISSING` calibration status; Mode 3 retains `WITHHELD BY CURRENT MODE`.

Activity remains `EXPLORATORY_UNSIGNED`, `polarity=NOT_ASSIGNED`,
`magnitude=MAGNITUDE_NOT_CONFIGURED`, and `priceOutcomeRead=false`. Pair remains
`MODERN_ENGINEERING_RESEARCH_TRANSFORM`, not a market bridge. SBC remains
independent from USD/JPY/pair interpretation; BPHS retains `NO MARKET ROLE`.
Every selected explanation states `NOT_FINANCIALLY_VALIDATED` and
`executionAllowed=false`.

## Changed Files

- `gann-astro-desk/src/views/fieldsResearchExplanation.ts` (new pure adapter)
- `gann-astro-desk/src/views/FieldsResearchInspector.tsx`
- `gann-astro-desk/src/fieldsResearchExplanation.test.tsx` (new focused tests)
- `gann-astro-desk/src/fieldsWorkspace.test.tsx` (accepts the required repeated BPHS no-market-role label)
- `gann-astro-desk/src/App.css`
- `docs/research/PFR_V2B_R5_F5_P1_FOUNDER_VISIBLE_RESEARCH_EXPLANATION.md`
- `status/research/pfr_v2b_r5_f5_p1_founder_visible_research_explanation.json`
- `CURRENT_PROJECT_HANDOFF.md`

No API payload, API request, backend route, source record, selection lifecycle,
calculation, visualization policy, package metadata, or Rust code changed. No
Candidate C dependency or outcome/provider access was added.

## Verification

- Focused frontend: **60/60** across the new explanation tests and existing Fields workspace tests.
- Full frontend: **273/273 across 50 files**, using Vitest's Windows-stable thread pool.
- TypeScript `tsc -b`: passed.
- Oxlint: passed.
- Production Vite build: passed; existing advisory for a minified chunk above 500 kB remains.
- `git diff --check`: required at closeout.
- Backend and Rust suites: not run; no backend or Rust files changed.

The default fork-worker Vitest invocation timed out before discovering tests on
this Windows host. The same full suite completed successfully with
`--pool=threads --maxWorkers=1`; this is a test-runner startup limitation, not a
test failure.

## Central-Review Leakage Tests

For both `CALIBRATED_RESEARCH` (Mode 2) and `VISUAL_ONLY_NO_SCORE` (Mode 3),
focused tests place directional sentinel state, reason, and numeric values in
field/pair interval records behind guarded proxies. The adapter and inspector
must render without reading those interval objects. Tests also confirm the
sentinels are absent from serialized explanation model state, visible text,
complete rendered markup/attributes, `title`, and ARIA/accessibility attributes.
Both modes retain the financial-validation and execution locks.

## Preserved Locks

```text
F4-B unauthorized
F4-C unauthorized
SIGNED_ACTIVITY_COUNT_V0 unauthorized
USDJPY signed resultant unauthorized
polarity catalogue unchanged
reviewed evidence registry unchanged
magnitude not configured
normalization absent
smoothing absent
source weighting absent
Candidate C product reuse false
EMP3 unauthorized
Auto Suggest disabled
ML disabled
MT5 disabled
executionAllowed=false
```

## Limitations and Next Gate

This is not a packaged founder candidate and has not received physical founder
inspection. The existing Vite large-chunk advisory remains. No visual behavior
beyond the focused component tests and responsive wrapping rules is claimed as
founder-accepted.

Next gate: `CENTRAL_REVIEW_PFR_V2B_R5_F5_P1_FOUNDER_VISIBLE_RESEARCH_EXPLANATION`.
No packaging, founder candidate, F4-B, F4-C, signed activity, polarity
admission, EMP3, or execution work is authorized by this implementation record.
