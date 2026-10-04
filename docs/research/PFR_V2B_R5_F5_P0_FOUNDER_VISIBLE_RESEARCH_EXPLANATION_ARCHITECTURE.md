# PFR-V2B-R5-F5-P0 Founder-Visible Research Explanation and Provenance Architecture

Date: 2026-10-04

Status: `ARCHITECTURE_PASS_EXPLANATION_P1_RECOMMENDED`

## Purpose and Boundary

This P0 record designs a read-only explanation layer for the accepted Fields
workspace. It starts from the accepted P5 baseline
`c52c22916b9c1dc6610f99c678d732ec2117f557` on
`research/pfr-v2b-r5-f4-a-p5-post-rsi-windows-founder-candidate`.

The proposed layer explains an explicit existing selection. It does not
calculate a new selection, infer a market effect, or reconcile different
source profiles. It is a provenance and boundary surface, not a prediction or
confidence surface.

P0 creates no runtime code, backend route, schema, package, or candidate. It
does not authorize P1 implementation. `executionAllowed=false` remains a
non-negotiable product lock.

## Accepted Product Surface

The accepted Fields workstation already composes these read-only surfaces in
one time-synchronized research view:

1. Price and aspect context.
2. Shared crosshair and explicit selection summary.
3. Independent USD, JPY, pair-relative, and SBC interval lanes.
4. Unsigned multi-oscillator activity events and interval counts.
5. Optional BPHS classical calendar context.
6. The unified read-only Fields research inspector.
7. Source-gap and audit-detail panels.

The current `FieldsResearchSelection` union is the single reusable selection
contract. Its explicit variants are `FIELD_INTERVAL`, `PAIR_INTERVAL`,
`ACTIVITY_EVENT`, `SBC_INTERVAL`, and `BPHS_INTERVAL`. A crosshair is time
context only; it is not a selection. Selections clear on dataset/page changes,
and no first interval is selected implicitly. F5 must preserve those rules and
must not create a parallel selection store, query parameter, or auto-selection
behavior.

The existing unified inspector is the correct host. It already receives the
selection, resolved visualization policy, source profile identifier, shared
crosshair, classification, and source-gap identifiers. P1 should extend that
surface rather than create a second inspector or a free-floating explanation
panel.

## Reusable Contract Inventory

| Existing contract | Reusable P1 fact | P1 must not infer |
| --- | --- | --- |
| `FieldsResearchSelection` | Selection kind, interval/event identity, UTC bounds, current classification, and source-gap IDs | A new item identity, causal link, or default selection |
| `ChartConditionedPolarityRangeInterval` | Existing categorical state, known/unknown event IDs, and recorded reason | A source-certified financial meaning from `SUPPORTIVE` or `ADVERSE` |
| `FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1` | Base/quote identities, known coverage, conflicts, source interval IDs, and the explicit engineering formula | A signed active-event wave, magnitude, market forecast, or SBC confirmation |
| `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1` | Exact event identity/lifecycle, astronomy contract, unsigned coverage, and guardrails | Polarity, magnitude, price/outcome relevance, or USDJPY resultant |
| `SBC_ATOMIC_VISIBLE_RANGE_V1` | Availability, evidence cutoff, source clusters, and missing-evidence IDs | Automatic confirmation, score, polarity, or market role |
| `BPHS_1899_CLASSICAL_CALENDAR_RESEARCH_V1` | Category/value, availability, source locator, calculation profile, and dependency | Market direction, price relation, or a side/pair contribution |
| `visualizationModePolicy` and source gaps | Current mode, value visibility, source gaps, calibration state, and execution lock | A missing rule, calibration, or promotion |

The existing server-side MO-R4A-P0 machine interpreter is intentionally
restricted to synthetic identifiers. It is not an admissible product data
source for real Fields selections and is excluded from P1.

## Explanation Model

For every explicit selection, P1 should render the following read-only fields.
The wording is selection-specific, but each field has one fixed semantic role.

| Founder question | P1 field | Required rule |
| --- | --- | --- |
| What is happening? | `headline` | Describe the selected interval/event/category, never a market call. Example: "Selected unsigned USD event lifecycle" or "Selected USDJPY pair-relative engineering interval." |
| Why does it matter? | `whyThisIsVisible` | Explain its current research/provenance role and state that it is not a forecast. |
| What is the astronomy fact? | `astronomyFact` | For activity, show transit/natal/aspect and applying/exact/separating UTC facts. For non-event selections, show the exact selected bounds or state `NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT`. |
| What is source-backed? | `sourceDoctrine` | Show the existing profile/classification, coverage, locator when supplied, and source gaps. Do not promote a partial profile to source certification. |
| What is the astrology interpretation? | `astrologyInterpretation` | Show only the existing categorical/availability value or a withheld/unknown reason. It has no financial conclusion. |
| What is engineered? | `engineeringTransform` | Identify the pair-relative formula, unsigned event-count contract, visual mode, or engineering calculation profile when applicable. |
| Is there a market bridge? | `marketBridge` | Report `NO_APPROVED_MARKET_BRIDGE` for all current P1 selections, except the pair's existing descriptive transform, which remains `MODERN_ENGINEERING_RESEARCH_TRANSFORM_NOT_MARKET_BRIDGE`. |
| Is it financially validated? | `financialValidation` | Always show `NOT_FINANCIALLY_VALIDATED`. Candidate C is not a P1 input. |
| Is magnitude configured? | `magnitude` | Show `MAGNITUDE_NOT_CONFIGURED` where present; for SBC's `NOT_CONFIGURED`, retain that exact upstream state plus a plain-language explanation. |
| What remains unknown or withheld? | `unknownsAndWithheld` | Show current source gaps, coverage/unknown reason, mode suppression, missing dependency, or `NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT` distinctly. |
| Can it execute? | `execution` | Always show `executionAllowed=false`. |

The layer must use explicit language such as "selected research state," "source
profile," "engineering transform," "unsigned activity," and "not financially
validated." It must never use `BUY`, `SELL`, `BULLISH`, `BEARISH`, forecast,
confidence, conviction, strength, market pressure, or trading language for a
P1 explanation.

## Label and State Rules

P1 is a presentation adapter. It may preserve upstream labels but must not
manufacture stronger ones.

| Label or state | Presentation rule |
| --- | --- |
| `SOURCE_CERTIFIED` | Display only when an upstream selected record explicitly supplies that exact certification. `SOURCE_PROFILED_PARTIAL`, source-profile identifiers, and a named book do not qualify. |
| `EXPERIMENTAL_PROFILED` | Display only for an explicit versioned experimental profile, with its profile identifier and no source-certification claim. The current activity profile remains explicitly geometry-only. |
| `EXPLORATORY_UNSIGNED` | Preserve as the primary activity evidence-mode label. Also show `polarity=NOT_ASSIGNED`, `magnitude=MAGNITUDE_NOT_CONFIGURED`, `priceOutcomeRead=false`, and `executionAllowed=false`. |
| `MODERN_ENGINEERING_RESEARCH_TRANSFORM` | Preserve for `FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1`; show its formula as a descriptive transform, not a financial bridge or signed resultant. |
| `UNKNOWN` | Remain an unknown gap with the recorded reason. It is never rendered as zero, flat, neutral, or an empty positive result. |
| `MIXED` | Remain distinct from `NEUTRAL`; retain conflict/component language and never resolve by vote, average, or visual simplification. |
| `NEUTRAL` | May be shown only when the upstream state is explicit. It never represents missing evidence or a suppressed value. |
| `WITHHELD BY CURRENT MODE` | Remain distinct from `UNKNOWN`. The selection identity and reason may be shown, while the suppressed directional value remains absent. |
| Absent source locator/detail | Render `NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT`; do not invent a locator, page, rule, or source coverage. |

## Mode Behavior

| Mode | Explanation behavior |
| --- | --- |
| `SOURCE_ONLY_BASELINE` | Show the selected source-profiled state and explicit source gaps. A visible categorical state is still not a market bridge or financial validation. `SOURCE_CERTIFIED` appears only if the selected upstream record explicitly says so. |
| `CALIBRATED_RESEARCH` | Preserve `CALIBRATION SOURCE MISSING` and any relevant source gaps. Do not expose a directional field value merely because its selection identity still exists. Explain that no calibration profile is loaded. |
| `VISUAL_ONLY_NO_SCORE` | Preserve `WITHHELD BY CURRENT MODE` for directional USD, JPY, and pair values. Activity, SBC, BPHS, UTC bounds, provenance, and guardrails remain inspectable. No directional value, hitbox-derived state, or hidden value may be reconstructed in the explanation. |

The resolved `visualizationPolicy.scoringVisible` remains the sole value-visibility
authority. P1 must not replace it with a parallel mode condition.

## Selection-Specific Content

| Selection | Required explanation emphasis |
| --- | --- |
| USD or JPY field interval | Existing categorical interval state, coverage, reason, profile, source gaps, and mode-withheld status. State plainly that the category is not a currency-market conclusion. |
| Pair interval | Base/quote source interval IDs, coverage, conflict, and the stored boundary-only pair transform. Label the calculation as modern engineering; state that it is not a signed resultant, magnitude, forecast, or financial validation. |
| Unsigned activity event | Immutable event ID/hash, USD or JPY chart identity, transit/natal/aspect, lifecycle UTC boundaries, astronomy contract, geometry-only profile, unsigned status, and coverage. No polarity, strength, or outcome language. |
| SBC interval | Source profile, availability, evidence cutoff, source cluster IDs, missing evidence, and explicit independence from USD/JPY/pair fields. No automatic confirmation or market role. |
| BPHS interval | Category/value, availability, source locator, calculation profile, dependency, and `NO MARKET ROLE`. No correlation, sign, pair, or market-bridge language. |

## Responsive Placement

P1 should add an `Explanation and provenance` subsection inside the existing
`Unified Research Inspector`, after the current selection-specific details and
before the shared metadata/locks.

At ordinary desktop width, use a compact two-column definition layout:

- left: What is happening, why, astronomy fact, source doctrine;
- right: astrology interpretation, engineering transform, market bridge,
  financial validation, magnitude, and execution lock.

At narrow widths, collapse into one vertical definition list. The primary
headline and all unknown/withheld badges remain above the fold. Long event IDs,
hashes, locators, and reasons must wrap rather than clip. Source gaps and
unknown reasons may use native disclosure controls, but the current state and
financial-validation label must remain immediately visible.

No new page, navigation entry, global panel, price-chart overlay, or selection
control is recommended.

## Backend Decision

**P1 should be frontend-only.** The present selection objects and existing
visualization policy supply the facts needed for a truthful bounded
explanation. A pure frontend adapter can create the explanatory field model
without a network request, new backend endpoint, source calculation, or
market-data access.

P1 must not claim absent per-interval page/verse locators. If a future scope
requires exact field-to-source citations beyond the current profile,
classification, source-gap, BPHS locator, SBC cluster, and activity astronomy
identifiers, that is a separate source-provenance contract and backend/data
admission review. It is not part of P1.

## Exact P1 Boundary

Authorized only after a separate central implementation directive:

1. Add a pure frontend explanation adapter and focused tests for the existing
   `FieldsResearchSelection` variants.
2. Render its output inside `FieldsResearchInspector` using the existing
   selection and `visualizationPolicy` inputs.
3. Add presentation styles that preserve the current responsive Fields layout.
4. Reuse current API payloads without changing API calls, backend contracts,
   selection behavior, field/activity/pair computation, source data, or mode
   policy.

P1 must not add a backend route, synthetic-interpreter call, new source
catalogue/evidence record, or a new mode. It must not make Candidate C or the
CONT-1 directional diagnostic a product input. The Candidate C result remains
historical empirical evidence, is not financially validated for product use,
and cannot be repackaged as a signal.

## Focused P1 Test Plan

1. Selecting each of the five existing selection variants renders exactly one
   explanation through the existing unified inspector.
2. No selection leaves the existing inspector empty state unchanged and makes
   no request.
3. Activity retains `EXPLORATORY_UNSIGNED`, no polarity, no magnitude, and no
   price/outcome or execution implication.
4. Pair retains `MODERN_ENGINEERING_RESEARCH_TRANSFORM`, source interval IDs,
   conflict/coverage, and `MAGNITUDE_NOT_CONFIGURED`; it never renders as a
   signed resultant or financial forecast.
5. SBC displays availability/missing evidence and no automatic confirmation or
   market role; BPHS displays source locator/dependency and `NO MARKET ROLE`.
6. `UNKNOWN`, `MIXED`, `NEUTRAL`, missing locator, and mode-withheld fixtures
   render as distinct states. In particular, unknown does not render as zero
   or neutral, and mixed does not render as neutral.
7. Mode 2 preserves calibration absence; Mode 3 preserves withholding without
   leaking directional state into the explanation DOM or accessible name.
8. `SOURCE_CERTIFIED` is absent unless explicitly supplied by an upstream test
   record; partial profiles are not promoted by the adapter.
9. Every rendered explanation exposes `NOT_FINANCIALLY_VALIDATED`,
   `executionAllowed=false`, and the existing source-gap identifiers where
   available.
10. Desktop and narrow-width visual tests confirm wrapped identifiers, no
    clipped state labels, stable inspector size, and no overlapping panes.
11. Regression tests confirm no new API request, pair/activity calculation,
    visualization-mode mutation, Candidate C fetch, Auto Suggest, ML, MT5, or
    execution path.

## Founder Inspection Checklist

1. Select one USD, JPY, pair, activity, SBC, and BPHS item and confirm the
   explanation always describes the selected item rather than a general market
   conclusion.
2. Confirm the six semantic layers remain visibly distinct: astronomy fact,
   source doctrine, astrology interpretation, engineering transform, market
   bridge, and financial validation.
3. Confirm `UNKNOWN`, `MIXED`, `NEUTRAL`, and `WITHHELD BY CURRENT MODE` are
   visually and verbally distinct.
4. Confirm the pair explanation calls itself a modern engineering transform
   and not a USDJPY prediction, signed resultant, or source doctrine.
5. Confirm activity is visibly unsigned and has no polarity, magnitude,
   price/outcome, or execution meaning.
6. Confirm SBC and BPHS state their separate/no-market roles.
7. Switch through Modes 1, 2, and 3 and confirm source gaps and withholding
   remain explicit without leaking hidden directional values.
8. Confirm all explanations visibly say `NOT_FINANCIALLY_VALIDATED` and
   `executionAllowed=false`.
9. Confirm the existing Fields selection, crosshair, panes, and chart layout
   remain unchanged; no second selection system appears.
10. Check an ordinary desktop and narrow viewport for readable wrapping and no
    clipping.

## Alternatives Considered

| Alternative | Decision | Reason |
| --- | --- | --- |
| A. F4-B directional chart fields | Do not precede explanation P1 | The target-aware polarity catalogue and reviewed-evidence registry remain without accepted production records. F4-B would manufacture or expose an unauthorized side sign. |
| B. F4-C polarity admission | Do not precede explanation P1 | A distinct evidence/admission gate must first establish legitimate identity-bound records. The architecture records no new polarity, catalogue, or reviewed-evidence admission. |
| C. Inherited native smoke-harness cleanup | Separate, not a prerequisite | `chakra_jupiter_motion_explicit=false` is inherited, unchanged, and not an RSI/P5 acceptance defect. It needs its own scoped central directive rather than being bundled with provenance presentation. |
| D. Android/mobile refresh | Do not precede explanation P1 | It changes platform delivery rather than resolving the founder's current desktop comprehension/provenance need. P1's responsive design can inform a later mobile scope without starting one. |

## Risks and Required Mitigations

| Risk | Required mitigation |
| --- | --- |
| A categorical label reads as a forecast | Use research-state language and permanently visible `NOT_FINANCIALLY_VALIDATED`/`executionAllowed=false` labels. |
| A partial source profile reads as certified doctrine | Do not derive `SOURCE_CERTIFIED`; show profile, classification, and source gaps verbatim. |
| Unknown looks like zero or neutral | Use separate labels, patterned/withheld presentation, and the recorded reason. |
| Pair transform reads as a signed USDJPY signal | Identify the formula and its engineering-only contract; prohibit result/forecast wording. |
| Candidate C looks like product validation | Do not render Candidate C result as a selection input, explanation reason, or confidence label. |
| Separate profiles appear to agree by co-location | Keep USD/JPY, SBC, and BPHS profiles independent and identify each profile/scope. |
| Mode suppression leaks a hidden value | Bind all explanation detail to `visualizationPolicy.scoringVisible` and test DOM/ARIA absence. |

## Explicit Locks

P0 and proposed P1 leave all of the following unchanged and unauthorized:

```text
F4-B directional chart fields
F4-C polarity admission
SIGNED_ACTIVITY_COUNT_V0
USDJPY signed resultant
new polarity catalogue entries
new reviewed-evidence admissions
market sign
magnitude
normalization
smoothing
source weighting
forecast or confidence
Candidate C product-signal reuse
EMP3
Auto Suggest
ML
MT5
execution
executionAllowed=false
```

## Disposition and Next Gate

Disposition: `ARCHITECTURE_PASS_EXPLANATION_P1_RECOMMENDED`.

The preferred next product slice is a separately authorized, frontend-only
`PFR-V2B-R5-F5-P1` implementation of this explanation adapter inside the
existing unified inspector. No P1 work is authorized by this record itself.

Next gate: `CENTRAL_REVIEW_PFR_V2B_R5_F5_P0_EXPLANATION_ARCHITECTURE`.
