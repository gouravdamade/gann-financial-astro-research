# PFR-V2B-R5-F3-P1 Founder-Visible Fields and Waves Workstation

Status: implementation complete for central review

This record documents the bounded frontend composition implemented from the
accepted P0 design. It does not introduce a new backend contract, source
doctrine, astronomy calculation, market-data path, or execution capability.

## Identity and Scope

- Starting branch: `research/mo-r4a-cont-1-final-close`
- Starting commit: `4c2a6a769670024dcbc72e405169ca2cca798a64`
- Implementation branch: `research/pfr-v2b-r5-f3-p1-founder-visible-fields-waves`
- Product surface: the existing Fields workspace in `gann-astro-desk`
- Boundary: founder-visible, read-only research inspection
- Final gate: `CENTRAL_REVIEW_PFR_V2B_R5_F3_P1_FOUNDER_VISIBLE_FIELDS_WAVES`

The implementation is frontend-only. Existing backend endpoints and response
contracts are reused unchanged. The pre-existing unrelated dirty files in the
worktree are not part of this record or its commit.

## Workstation Composition

The Fields view now presents one coherent research workstation in this order:

1. Fields header and explicit visualization mode controls
2. Price and aspect context
3. Shared crosshair and research-selection summary
4. Independent USD, JPY, pair-relative, and SBC field stack
5. Unsigned multi-oscillator activity waves
6. Optional BPHS classical timing context
7. Unified read-only research inspector
8. Existing contract and audit details

Founder Review remains a separate explicit workflow. It is not folded into the
read-only inspector and no review decision state is created by selection.

## Selection Contract

`FieldsResearchSelection` is a discriminated union with these variants:

- `FIELD_INTERVAL`: USD or JPY source-profiled field interval
- `PAIR_INTERVAL`: pair-relative engineering research transform interval
- `ACTIVITY_EVENT`: unsigned activity event with side, lifecycle, coverage, and
  provenance identifiers
- `SBC_INTERVAL`: atomic SBC availability interval
- `BPHS_INTERVAL`: BPHS category interval with source locator and dependency
  context

The inspector displays the selected item, source profile, classification,
source gaps, and read-only provenance. A crosshair remains a separate shared
time context; it does not create a selection. No first pair interval is
auto-selected. A selection is cleared when the dataset changes or when the
selected interval leaves the current research page; the parent selected-field
contract is cleared at the same boundary.

Activity and BPHS selections update the existing shared timestamp/crosshair
path only. Local activity filters remain display-only and do not trigger a new
fetch or a backend calculation.

## Mode and Evidence Policy

Directional visibility is gated by the resolved
`visualizationPolicy.scoringVisible` value rather than by a hard-coded mode
enum. This preserves the existing policy resolver as the source of truth:

- Mode 1: source/classical baseline; existing source-profiled values remain
  inspectable.
- Mode 2: calibrated research; missing calibration remains explicit and no
  fabricated field is shown.
- Mode 3: geometry/exploration; directional and pair values are withheld while
  activity, geometry, and provenance remain inspectable.

Suppressed directional values are labelled `WITHHELD BY CURRENT MODE` in the
unified inspector. Mode-specific gaps remain visible in the summary and audit
surfaces. `UNKNOWN` is rendered before `NEUTRAL`; `MIXED` remains distinct from
`NEUTRAL`. The existing pair compiler and pair math are reused without change.

## Provenance and Locks

The inspector exposes source profile, source classification, interval/event
identity, source-gap context, and the existing read-only contract. BPHS entries
are explicitly marked as having no market role. Activity remains unsigned and
non-predictive. No new private-source bytes, catalogue entries, outcome data,
or provider data are bundled or read.

The following remain locked:

- no Candidate C or EMP3 path
- no outcome access or statistical analysis
- no market-data provider access
- no polarity or score aggregation
- no Auto Suggest or ML
- no Fields execution or MT5 execution
- `executionAllowed=false`

## Verification

- Focused Fields workspace tests: 30 passed
- Full frontend suite: 44 files, 210 tests passed
- Oxlint: passed
- TypeScript/Vite production build: passed
- Backend: no backend source was changed; the broad legacy backend command did
  not complete in this environment after surfacing unrelated legacy failures,
  so no backend pass is claimed for this frontend-only milestone.
- Rust/Tauri: not touched and not run

## Visual Check

A local Vite session was opened in the available wide browser review surface.
The header, context/selection summary, price chart, independent field stack,
activity waves, and unified inspector were checked in sequence. The visible
lower activity and inspector panels had no clipping or overlap in that review
surface. The available browser surface was not an exact 1280x800 viewport, so
this is a bounded visual check rather than a founder acceptance claim.

The existing branch-local unrelated files remain unstaged and outside the P1
change. No Windows candidate is built by this milestone.

## Next Gate

`CENTRAL_REVIEW_PFR_V2B_R5_F3_P1_FOUNDER_VISIBLE_FIELDS_WAVES`

## P1-R1 Withheld-Direction Presentation Correction

P1 is superseded for central review by
`PFR-V2B-R5-F3-P1-R1-WITHHELD-DIRECTION-PRESENTATION`. The correction is
frontend-only and preserves the P1 source, pair, activity, BPHS, Founder
Review, Candidate C, and execution boundaries.

When `visualizationPolicy.scoringVisible` is false, the USD, JPY, and pair
categorical lanes now render a non-directional withheld surface. Their state
rectangles, directional SVG paths, SVG/HTML titles, ARIA state labels,
selection hitboxes, ordinary Supportive/Neutral/Adverse legend, gap structure,
and state-derived details are absent from the DOM. The shared crosshair may
remain as time synchronization only. Retained directional selections remain
identity-stable, while the shared summary and unified inspector report only
`WITHHELD BY CURRENT MODE`.

Mode 1 continues to expose the source-profiled categorical labels and
hitboxes, including distinct `UNKNOWN` and `MIXED` behavior. Mode 2 continues
to show `CALIBRATION SOURCE MISSING` while unsigned activity events remain
inspectable. Trailokya remains source-only and withheld by the resolved policy.
The workstation order is now explicitly price context, selection summary,
independent fields, activity, BPHS, inspector, and audit details.

The P1 status is:
`PFR-V2B-R5-F3-P1=SUPERSEDED_BY_P1_R1_PENDING_CENTRAL_REVIEW`.
The successor remains pending central review; it is not a central-pass or
founder-acceptance record.

### P1-R1 Verification

- Focused Fields workspace tests: 33 passed
- Full frontend suite: 44 files, 213 tests passed
- TypeScript: passed
- Oxlint: passed
- Vite production build: passed
- `git diff --check`: passed
- Bounded local browser check: Mode 1, Mode 2, and Mode 3 verified; the
  available browser surface was not an exact 1280x800 viewport.
- Backend regression was not run because this correction is frontend-only and
  the directive requires no backend changes. Rust/Tauri was not touched.
