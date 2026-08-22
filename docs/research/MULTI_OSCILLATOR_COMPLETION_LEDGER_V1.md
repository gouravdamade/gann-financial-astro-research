# Multi Oscillator Completion Ledger V1

Status: AUDIT_COMPLETE_NO_RUNTIME_CHANGE
Date: 2026-08-23 IST
Repository baseline: 09058f270a701f152813a93b78bc910dbc1a8a3d
Scope: Multi Oscillator / wave visualizer inventory only

## Purpose and Stop Gate

This ledger records what the repository can already render, which parts are
implemented as deterministic data flow, and which parts remain deliberately
unconfigured. It is not a product implementation directive.

The project-priority record freezes CGVO-G3 after G3-S1-R1 and makes the
working, inspectable Multi Oscillator / wave visualizer the next product
priority. This audit does not reopen CGVO, add a polarity rule, activate a
financial signal, modify MT5 behavior, or change any execution lock.

| Classification | Meaning in this ledger |
| --- | --- |
| Existing explicit | The repository exposes an intentional contract or behavior now. |
| Implemented | Code and a testable data path exist now. |
| Historical / proposed | A document describes an idea, but no current production path relies on it. |
| Experimental | A modern engineering transform may be used only under an explicit future profile. |
| Unresolved | A missing authority or data dependency must remain visible as a gap. |

## Baseline and Runtime Evidence

The audit began from a cleanly fast-forwarded public baseline:

    HEAD          09058f270a701f152813a93b78bc910dbc1a8a3d
    origin/master 09058f270a701f152813a93b78bc910dbc1a8a3d

Pre-existing local artifacts were deliberately excluded:

    M  gann_aspect_annotations_raman_v2.sqlite
    ?? candlestick_shadow_v3.sqlite
    ?? logs/

The Flask sidecar was started locally only for audit. A real request to the
synchronized-range endpoint for 2026-08-01T00:00:00Z through
2026-08-15T00:00:00Z completed in about 14.16 seconds:

| Result | Observed value |
| --- | --- |
| Contract | SYNCHRONIZED_INDEPENDENT_RANGE_V1 |
| USD event records | 62 |
| USD intervals | 90, all UNKNOWN |
| JPY event records | 61 |
| JPY intervals | 90, all UNKNOWN |
| SBC contract | SBC_ATOMIC_VISIBLE_RANGE_V1 |
| SBC intervals | 1 |
| executionAllowed | false |
| fieldsFused | false |

This proves the current event to interval to API path is alive. It does not
prove a signed oscillator: the canonical polarity catalogue contains zero
accepted production entries, so the side fields correctly remain gaps.

## Current Product Contract

### Existing explicit contract

The top-level Fields workspace is an implemented research surface for the
loaded chart, with a shared research-time controller and four independent
rendering lanes:

1. USD categorical field.
2. JPY categorical field.
3. USDJPY pair-relative categorical field.
4. Independent SBC availability field.

The present contract is categorical, not an analogue financial waveform:

- SUPPORTIVE, ADVERSE, MIXED, NEUTRAL, and UNKNOWN are distinct states.
- Intervals use canonical half-open UTC boundaries, [startUtc, endUtc).
- Unknown is represented as a visible gap and must never silently become
  neutral.
- SBC is deliberately independent from USD, JPY, and pair-relative fields.
- Trailokya source-only geometry is an explicit unavailable SBC range state,
  GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED, rather than a scored fallback.
- Visual-only mode suppresses directional paths and labels that suppression;
  it does not manufacture a flat line.

### Implemented source-to-pixel chain

| Stage | Current implementation | Status |
| --- | --- | --- |
| Accepted chart identities | Canonical founder-chart registry records for USD and JPY. | Implemented |
| Astronomy event facts | Swiss Ephemeris, Raman sidereal, true-node policy and deterministic UTC conversion. | Implemented |
| Transit-to-natal windows | Event compiler finds applying, exact, and separating event boundaries. | Implemented |
| Side field compilation | Backend compiles its own events; frontend payloads cannot invent side events or chart identities. | Implemented |
| Polarity lookup | Target-aware catalogue only admits exact reviewed identity matches. | Implemented, empty evidence |
| Categorical intervals | Actual event boundaries become categorical state intervals. | Implemented |
| Pair derivation | Exact boundary union and base-minus-quote categorical balance. | Implemented |
| Shared range API | SYNCHRONIZED_INDEPENDENT_RANGE_V1 response. | Implemented |
| Shared controller | Crosshair, selected interval and selected pair interval are stored in RESEARCH_TIME_CONTROLLER_V1. | Implemented |
| Price chart | Lightweight Charts market chart with crosshair callbacks. | Implemented |
| Field rendering | Separate SVG categorical step panes, patterns for gaps, component paths for mixed states. | Implemented |
| Audit status | Source IDs, event/compiler provenance and unknown reasons return, but live event detail is not a complete founder-facing inspector. | Partial |

### Historical / proposed records, not runtime authority

The following are documented research concepts, not active runtime authority:

- ASPECT_PHASE_KERNEL or harmonic phase concepts.
- A smooth amplitude curve or smoothing constant.
- Calibrated weights or fitted coefficients.
- A source-backed Vedha duration kernel.
- A generic collective planetary waveform.

The historical coverage matrix keeps these unconfigured. No future Multi
Oscillator implementation may claim them merely because the terms appear in a
document.

### Experimental engineering already present

FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1 is a transparent modern engineering
transform. It is not classical doctrine, does not use SBC confirmation, is not
a market forecast, and has no execution authority.

The repository exposes a CALIBRATED_RESEARCH visualization mode, but the named
calibrated SBC profile has zero configured parameters. This is a mode boundary,
not an implemented magnitude model.

### Unresolved authority

The following are intentionally absent:

1. An admitted target-aware USD or JPY polarity record.
2. A source-approved or centrally authorized experimental event-to-wave
   contribution contract.
3. Magnitude, weighting, normalization, and aggregation authority for a
   continuous or summed oscillator.
4. A runtime, all-ranges exact-pass identity verifier linked to every
   dynamically compiled event.
5. A complete founder-facing inspection surface for each live field event.

## Full Source-to-Pixel Trace

    accepted USD / JPY chart registry
      -> accepted historical chart identity                  IMPLEMENTED
      -> Swiss Ephemeris transit-to-natal event compiler     IMPLEMENTED
      -> applying / exact / separating UTC boundaries        IMPLEMENTED
      -> backend-owned event identity and hash               IMPLEMENTED
      -> reviewed target-aware polarity catalogue lookup     BLOCKED: catalogue empty
      -> categorical side interval compiler                  IMPLEMENTED, outputs UNKNOWN
      -> USD / JPY categorical fields                        IMPLEMENTED, gaps today
      -> pair-relative categorical derivation                IMPLEMENTED, gap if either side unknown
      -> synchronized range response                         IMPLEMENTED
      -> research-time controller / crosshair selection      IMPLEMENTED
      -> SVG categorical field panes                         IMPLEMENTED
      -> signed or continuous multi-wave                     NOT IMPLEMENTED / NOT AUTHORIZED

The independent SBC path is separate:

    selected SBC source profile
      -> source-profile atomic / geometry availability range IMPLEMENTED
      -> independent SBC lane                                IMPLEMENTED
      -> SBC modifies USD, JPY, or pair field                PROHIBITED

CGVO, BPHS calendar data, Shadbala, Drik, and price outcomes do not enter the
current Fields side or pair-field pipeline.

### Primary implementation locators

| Concern | Current repository path |
| --- | --- |
| Fields page and range request | gann-astro-desk/src/views/FieldsWorkspace.tsx |
| Categorical lanes | gann-astro-desk/src/views/IndependentFieldStack.tsx |
| Pair formula | gann-astro-desk/src/pairRelativeField.ts |
| Shared chart/controller bridge | gann-astro-desk/src/views/MainWorkspace.tsx |
| Visualization mode policy | gann-astro-desk/src/visualizationModes.ts |
| Backend synchronized range | gann-astro-desk/backend/synchronized_range_service.py |
| Backend side polarity range | gann-astro-desk/backend/chart_conditioned_polarity_service.py |
| Backend event boundary service | gann-astro-desk/backend/chart_conditioned_transit_event_service.py |
| Astronomy compiler | research_labs/chart_conditioned_aspects/chart_conditioned_aspects/transits/chart_conditioned_event_compiler.py |
| Polarity authority | research_labs/chart_conditioned_aspects/profiles/target_aware_polarity_catalogue_v1.json |
| Categorical series compiler | research_labs/chart_conditioned_aspects/chart_conditioned_aspects/polarity_series.py |

## Lane Inventory

| Lane or candidate | Producer | Time series | Magnitude | Direction authority | Timing authority | UI today | Missing dependency |
| --- | --- | --- | --- | --- | --- | --- | --- |
| USD categorical | Chart-conditioned polarity service | Yes, event-boundary intervals | Not configured | Reviewed target-aware catalogue only | Applying/exact/separating window | SVG pane | Zero accepted catalogue entries |
| JPY categorical | Same service for JPY | Yes, event-boundary intervals | Not configured | Reviewed target-aware catalogue only | Applying/exact/separating window | SVG pane | Zero accepted catalogue entries |
| USDJPY pair relative | pairRelativeField | Yes, union of side boundaries | Display balance only | None beyond known side categories | Side intervals | SVG pane | Both side fields must be known |
| SBC independent | Chakra atomic-range service | Profile availability intervals | No field magnitude | No USDJPY direction authority | Profile-range contract | Availability lane | Trailokya range intentionally absent |
| Aspect event geometry | Transit event compiler | Event start/exact/end facts | Orb/residual facts only | None | Astronomy contract | Indirect interval segmentation | No founder event inspector in Fields |
| Planetary or collective waves | No production producer | No | No | No | No | No | Explicit source or experimental contract |
| CGVO | Frozen source branches | No Fields feed | No | No | No | No | Deliberately disconnected |
| BPHS calendar | Calendar service | Calendar category facts | No | No market direction | Calendar boundaries | Separate calendar pane | Not an oscillator input |

The phrase Multi Oscillator is therefore aspirational at present. The code
already has a multi-lane categorical field renderer, but it does not yet have
a multi-signal contribution engine or continuous wave model.

## Exact Pair-Relative Contract

For each canonical side interval:

    supportive component = +1 when active
    adverse component    = -1 when active
    sideGross            = supportiveCount + adverseCount
    sideNet              = supportiveCount - adverseCount
    sideBalance          = sideNet / sideGross, when sideGross > 0
    pairRaw              = baseBalance - quoteBalance
    pairDisplay          = clamp(pairRaw / 2, -1, +1)

For USDJPY, base is USD and quote is JPY. Pair boundaries are the exact ordered
union of USD and JPY canonical interval boundaries; the code does not sample,
stretch, interpolate, smooth, or infer an intermediate value.

If either side is UNKNOWN or absent:

    pairDisplay = null
    pairState   = UNKNOWN_SIDE_EVIDENCE

MIXED preserves supportive activity, adverse activity, gross activity, and
conflict even if its net display baseline is zero. This is not an
unknown-to-zero conversion. A known NEUTRAL state may legitimately render at
zero.

## Polarity Authority Audit

| Transformation | Authority | Current behavior | Safe state |
| --- | --- | --- | --- |
| Transit geometry to event existence | Astronomy contract | Computes factual aspect windows | Implemented |
| Event to supportive/adverse | Exact immutable reviewed catalogue entry | No entry exists today | Blocked, UNKNOWN |
| Planet name or aspect name to polarity | None | No fallback is permitted | Prohibited |
| Source profile to USDJPY direction | None | SBC does not participate | Prohibited |
| Price outcome to polarity | None | No read path | Prohibited |
| LLM to polarity | None | No LLM path | Prohibited |
| Side state to pair display | Pair contract above | Transparent categorical transform | Implemented research transform |

The canonical target-aware polarity catalogue states
NO_ACCEPTED_PRODUCTION_ENTRIES and contains zero entries. Therefore no valid
current code path can create a supportive or adverse side interval for the live
Fields request.

## Magnitude, Aggregation, and Wave Audit

| Quantity | Current status | Can it move a field now? | Notes |
| --- | --- | --- | --- |
| Exact event time | Available | Segments categorical intervals | Astronomical identity, not amplitude |
| Event active window | Available | Segments categorical intervals | Applying start to separating end |
| Orb / angular residual | Available to event compiler | No | Not a display magnitude contract |
| Supportive/adverse count | Available only after reviewed evidence | Yes, categorical components | No accepted records today |
| Side net / gross | Implemented for known categories | Yes, pair calculation | Not a market magnitude |
| Pair display | Implemented | Yes, only where both sides known | Bounded relative categorical display |
| SBC activity / availability | Profile-specific | No side/pair effect | Independent only |
| Shadbala / Drik / Ashtakavarga | Outside Fields contract | No | No authorized field weight |
| Phase kernel / harmonic amplitude | Historical proposal | No | No timing or normalization profile |
| Calibrated weight | Historical proposal | No | Zero configured parameters |

There is no valid analogue wave mathematics in the current system. A future
implementation must name every contribution, its source class, timing kernel,
normalization, aggregation rule, profile ID, and unknown behavior. It must not
call the present categorical step display a calibrated waveform.

## Timing, Modes, and Unknown Semantics

### Timing

The implemented clock is factual event timing: applying boundary, exact UTC,
and separating boundary. The categorical state interval uses these boundaries.
There is no approved lead/lag, ramp, decay, convolution, harmonic phase,
overlap accumulation, or smoothing kernel.

The Fields API computes a 14-day research page. The visible price chart is
primarily visual context; it is not currently the direct range driver for the
side range request. The shared controller synchronizes crosshair and selected
interval identity, and the workspace can load a research page containing the
crosshair. A true viewport-driven field range is not yet implemented.

### Visualization modes

| Mode | Current permitted behavior | Current limitation |
| --- | --- | --- |
| SOURCE_ONLY_BASELINE | Source-backed categorical behavior only where evidence exists. | No accepted USD/JPY records; side fields are gaps. |
| CALIBRATED_RESEARCH | Boundary for a versioned experimental profile. | No calibrated parameters or magnitude profile configured. |
| VISUAL_ONLY_NO_SCORE | Shows chart/event geometry/availability while suppressing directional paths. | Not a directional field or waveform. |

The side-polarity service does not presently select a separate source-only
versus calibrated side-catalogue profile. A future implementation must make
that admission boundary explicit before a calibrated side field is rendered.

### Unknown audit

Correct behavior now:

- Missing accepted polarity becomes a patterned UNKNOWN gap.
- A missing side makes the pair UNKNOWN_SIDE_EVIDENCE, not zero.
- Trailokya unavailable SBC range remains an availability state, not a neutral
  or scored substitute.
- Visual-only suppression has explicit explanatory copy.

Legitimate zero:

- A known NEUTRAL interval.
- A known MIXED display baseline while both component paths and conflict remain
  visible.

Remaining product risks:

- A user cannot yet expand a live lane interval into a complete event-identity
  and provenance panel.
- A 14-day field research page and price viewport can appear to be one
  timeline even though they are not the same data-range contract.

## UI and Interaction Audit

Implemented:

- Top-level Fields navigation.
- Shared price crosshair to Fields selection.
- Selecting USD, JPY, pair, or SBC interval updates the research controller.
- Exact pair interval IDs are preserved.
- Separate compact lanes, activity labels, unknown patterns, and SBC status.
- Existing price-chart pan/zoom comes from Lightweight Charts.

Not implemented:

- Individual planet/event signal toggles.
- Lane-specific zoom/pan controller or dedicated value axis.
- Contribution stack or multi-signal inspector.
- Per-event expandable provenance view in the live Fields pane.
- A true waveform or amplitude histogram.
- A live viewport-driven back-end range request.

The current SVG field lanes are honest categorical state visualizations. They
are not yet close to a TradingView-style oscillator sub-chart because their
height is fixed and they have no independent scale, pointer inspection, or
series selection system.

## Requirement-to-Code Matrix

| Requirement | Primary path | State | Blocker / next closure |
| --- | --- | --- | --- |
| Real USD event facts | backend chart-conditioned transit event service | Done | None |
| Real JPY event facts | Same service | Done | None |
| Immutable chart identity | Founder chart registry | Done | None |
| Exact event identity | Event compiler hashes | Done for compiler output | Live exact-pass audit metadata not displayed per arbitrary event |
| Founder-reviewed polarity | Target-aware polarity catalogue | Blocked | Catalogue has no accepted entries |
| Categorical side field | polarity series compiler | Done | Requires reviewed evidence to become non-gap |
| Pair-relative field | frontend pairRelativeField module | Done | Requires both known side fields |
| Independent SBC | synchronized range service | Done | Trailokya range intentionally unavailable |
| Source-only side admission | Visualization mode and catalogue design | Partial | Explicit side-profile filtering/admission contract absent |
| Calibrated side magnitude | No active producer | Not done | Centrally approved experimental contribution contract |
| Multi-signal aggregation | No active producer | Not done | Input list, weights, overlap and unknown policy |
| Continuous wave | No active producer | Not done | Timing kernel and normalization authority |
| Event provenance UI | Field response metadata only | Partial | Founder-facing interval detail component |
| Viewport-controlled field range | 14-day research page mechanism | Partial | Explicit viewport/range contract |
| Execution safety | Backend and package locks | Done | Must remain false |

## Minimum Viable Oscillator Recommendation

The first useful product must not be a fabricated bullish/bearish curve. The
smallest honest sequence is:

1. Mode 3 event-activity visualizer: render factual, unsigned, inspectable
   transit-to-natal event activity by body/aspect, with start, exact, end,
   event hash, chart identity, and explicit unknowns. It is a geometry/timing
   visualizer, not a market signal.
2. Reviewed categorical side field: once founder-reviewed, identity-bound
   source or research records exist, render separate supportive, adverse, and
   mixed categorical channels without smoothing.
3. Pair-relative categorical field: retain the existing transparent formula
   and show it only where both reviewed side fields are known.
4. Only then consider a Mode 2 contribution profile: it must be versioned,
   explicitly non-classical, outcome-blind at creation, and label every
   timing/magnitude/normalization decision. It must not be created merely to
   make the chart move.

This sequence makes the current product inspectable before it is predictive.

## Can Mode 2 Start First?

Mode 2 can start only as a clearly non-predictive engineering visualizer. It
could display unsigned event activity or separately visible categorical
components, provided central review first defines:

- The exact event eligibility universe.
- Whether overlap is a count, a stack, or separate lanes.
- The time kernel as fixed boundaries only or another stated function.
- The normalization rule.
- The meaning of a zero or unknown result.
- The audit/provenance payload.
- The statement that it has no price, forecast, or execution semantics.

Mode 2 cannot honestly start as a signed USDJPY oscillator today. The direct
blocker is not rendering technology: it is the absence of accepted polarity
records and an approved event-contribution/magnitude contract.

## P0 Blocker and Ordered Backlog

### P0

No versioned, auditable event contribution contract exists for a signed or
continuous field. Its immediate concrete symptom is the empty target-aware
polarity catalogue. The code correctly turns every live event interval into
UNKNOWN until a reviewed, identity-matching record exists.

Do not solve P0 by assigning a sign from aspect geometry, planet nature, SBC,
price outcome, or an LLM.

### P1

1. Founder-facing event provenance inspector for a selected live Fields
   interval.
2. Explicit source-only versus calibrated side-field admission/profile
   boundary.
3. Clear field-range versus price-viewport contract and presentation.
4. Lane interaction: toggles, independent height/axis, and useful tooltip
   inspection.

### P2

1. Runtime exact-pass integrity metadata for arbitrary visible events.
2. A central research decision on whether Mode 3 unsigned activity is desired.
3. Later performance work: cache and cancellation measurements for larger
   visible ranges.

## Recommended Milestones

| Order | Milestone | Recommended model | Bounded output |
| --- | --- | --- | --- |
| 1 | MO-P1 Contribution Contract Review | Terra High | A signed/unsigned, source/experimental, timing/normalization/unknown contract. No code that invents polarity. |
| 2 | MO-P2 Event Provenance and Activity API | Luna Max | Backend-owned inspectable event stream and Mode 3 event activity payload; no market interpretation. |
| 3 | MO-P3 Fields Interaction and Multi-Lane Renderer | Luna Max | Expandable event details, signal selection, lane sizing, crosshair tooltips, and viewport clarity. |
| 4 | MO-P4 Versioned Mode 2 Profile | Terra High for specification, Luna Max for implementation | An explicitly non-classical, non-execution experimental profile only after P1 authority is accepted. |
| 5 | MO-P5 Evidence Admission and Source-Only Review | Terra High | Review/admission process for target-aware side records, separately from outcome validation. |

CGVO source branches remain frozen unless a future Multi Oscillator milestone
identifies a specific, approved dependency that genuinely blocks it.

## Questions for Central Research

1. What exact source or founder-review process grants polarity to a
   transit-to-natal event without using price outcomes?
2. Is Mode 2 first display strictly unsigned event activity, separately signed
   components, or a net categorical field?
3. What is the permitted event universe: bodies, aspects, orb profile, and
   chart contexts?
4. Are event windows limited to applying-to-separating boundaries, or is a
   separate timing kernel allowed?
5. If several events overlap, should they remain separate lanes, create a
   count, or aggregate under an explicitly named formula?
6. What quantity, if any, is a magnitude: source value, categorical count,
   normalized balance, or a future experimental coefficient?
7. What must display in a founder event inspector before a field interval is
   considered auditable?
8. Does Mode 1 require separate source-backed evidence per side and per target
   context, and how should conflicting records remain visible?

## Verification Performed

| Command or action | Result |
| --- | --- |
| npx vitest run --maxWorkers=1 fieldsWorkspace.test.tsx pairRelativeField.test.ts | 4 suites, 16 tests passed |
| Relevant backend unittest discovery: transit event, polarity, synchronized range, FX side pilot | 15 tests passed |
| npm run lint | Passed |
| npm run build | Passed, production Vite bundle built |
| Direct sidecar health request | Passed |
| Live synchronized-range request | Passed; real event segmentation, all side states UNKNOWN, execution locked |

## Final Audit Verdict

The repository does not currently have a finished multi-wave oscillator. It
does have a credible, fail-closed categorical Fields foundation with real
astronomy event plumbing, transparent pair math, shared interaction state, and
independent SBC rendering.

The next work should make the system more inspectable and define contribution
authority before making it more animated. The absence of an output today is
honest: missing polarity evidence remains a gap, rather than being converted
into a misleading smooth line.
