# Multi Oscillator Signed Side Wave and USDJPY Resultant Architecture Audit V1

Status: RESEARCH_AUDIT_COMPLETE_NO_RUNTIME_CHANGE
Date: 2026-08-25 IST
Repository baseline audited: `f41bb454507c1e753618adfea4ca038fb4b02658`
Scope: MO-R1 signed-side and FX-resultant architecture only

## Decision in One Paragraph

**REPOSITORY FACT:** MO-P2 is a founder-accepted unsigned activity product. It
compiles exact, provenance-bearing, transit-to-natal event intervals for the
accepted USD and JPY research charts, then reports raw active-event counts.
The target-aware polarity catalogue and reviewed-evidence registry both contain
zero accepted production records. Therefore neither `W_USD(t)` nor `W_JPY(t)`
exists today, and a USDJPY signed resultant cannot be honest yet.

**EXPERIMENTAL HYPOTHESIS:** the first future signed prototype should be a versioned,
outcome-blind **Mode 2 signed active-event-count** display, constructed only
from identity-bound, founder-reviewed side polarity records. It should retain
the current rectangular applying-to-separating interval, use no magnitude
model, use no normalization, retain categorical components beside the count,
and render the pair as a gap whenever either side is unknown. This is not
authorized by this report; it is the smallest later implementation target.

## Evidence Classes Used Here

| Class | Meaning in this report |
| --- | --- |
| **REPOSITORY FACT** | A current committed contract, source record, testable guardrail, or product behavior. |
| **MATHEMATICAL / ENGINEERING FACT** | A property of the stated equations or a transparent computation, not doctrine. |
| **SOURCE-BACKED DOCTRINE** | A page/verse-backed source statement within its recorded source profile and scope only. |
| **EXPERIMENTAL HYPOTHESIS** | A modern, versioned research choice that must not be called classical or validated before testing. |
| **UNRESOLVED** | Evidence or an operator is absent, conflicted, partial, or otherwise not authorized. |

No conclusion below treats a planet's natural character as financial direction.
No conclusion treats angular aspect geometry as financial direction.

## 1. Live Repository Audit

| Area inspected | Current result | Classification | Architecture consequence |
| --- | --- | --- | --- |
| MO-P2 activity service | `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1` compiles USD and JPY separately from the canonical transit-event compiler. Events contribute one raw count over `[applyingStartUtc, separatingEndUtc)`. | REPOSITORY FACT | A defensible unsigned timing/presence substrate exists. |
| Canonical event compiler | Server-owned request accepts only side, UTC range and `ASPECT_STRENGTH_V0`; it loads the accepted chart identity and produces event IDs/hashes, exact pass facts, astronomy contract and boundaries. | REPOSITORY FACT | Frontend cannot substitute a chart, event, polarity or price outcome. |
| Aspect profile | Nine bodies, five aspects and a 3 degree maximum orb are explicitly `GEOMETRY_ONLY` / `EXPERIMENTAL_GEOMETRY_PROFILE`. | REPOSITORY FACT | An aspect does not supply contribution sign. |
| Target-aware catalogue | `CHART_CONDITIONED_TARGET_AWARE_POLARITY_BASELINE_V1` has `entries: []` and `NO_ACCEPTED_PRODUCTION_ENTRIES`. | REPOSITORY FACT | No runtime signed contribution is authorized. |
| Target-aware evidence registry | `CHART_CONDITIONED_TARGET_AWARE_POLARITY_EVIDENCE_BASELINE_V1` has `packets: []` and `NO_REVIEWED_PACKETS`. | REPOSITORY FACT | There is no immutable source for a side sign. |
| Founder chart registry | One accepted research hypothesis exists for each primary side: USD Independence / Philadelphia and JPY Yen IPO / Tokyo. Registry itself is inert. | REPOSITORY FACT | Chart-conditioned identity is available, but does not grant polarity. |
| Categorical side fields | Current fields preserve `SUPPORTIVE`, `ADVERSE`, `MIXED`, `NEUTRAL` and `UNKNOWN`; absent evidence is a gap. | REPOSITORY FACT | Future signed counts must retain the categorical provenance, not replace it. |
| Pair-relative categorical field | `FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1` uses base balance minus quote balance only when both categorical sides are known. | REPOSITORY FACT | Its unknown rule and exact boundary union are reusable; its normalized balance is not a signed-wave contract. |
| Visualization modes | Current modes are `SOURCE_ONLY_BASELINE`, `CALIBRATED_RESEARCH` and `VISUAL_ONLY_NO_SCORE`; all retain `executionAllowed=false`. | REPOSITORY FACT | Future signed work must extend, not silently reinterpret, these policies. |
| Fields workspace | The price chart, categorical USD/JPY/pair/SBC lanes and unsigned activity panel use a shared time range/crosshair but remain separate. | REPOSITORY FACT | A later signed pane can share time control without fusing SBC or price. |
| Trailokya records | Some geometry, target reach, isolated phala fractions and isolated modifiers are source recorded, but no FX mapping, complete modifier stack, universal timing kernel or financial polarity exists. | SOURCE-BACKED DOCTRINE / UNRESOLVED | It cannot supply a USD or JPY signed contribution. |
| Agarwal records | Geometry and selected strength evidence are recorded; Chapter 20 remains `FINANCIAL_HYPOTHESIS_LEDGER_ONLY`, not FX-mapped, not executable. | REPOSITORY FACT / UNRESOLVED | It cannot supply sign, magnitude or pair direction. |
| Varahamihira / Brhat Samhita records | Current CGVO findings are contextual provenance, local eclipse visibility and historical calendar geography only. | REPOSITORY FACT / UNRESOLVED | They do not supply a financial side sign. |
| BPHS calendar | Calendar categories are a separate partial research display. No price, polarity, pair or execution path exists. | REPOSITORY FACT | Not an input to the signed side wave. |
| SBC architecture | Source profiles, source gaps and independent SBC availability remain deliberately separate from USD/JPY fields. | REPOSITORY FACT | SBC is not sign confirmation and must not enter the resultant formula. |

Key reviewed paths include:

- `gann-astro-desk/backend/multi_oscillator_activity_service.py`
- `gann-astro-desk/backend/chart_conditioned_transit_event_service.py`
- `research_labs/chart_conditioned_aspects/chart_conditioned_aspects/polarity_catalogue.py`
- `research_labs/chart_conditioned_aspects/chart_conditioned_aspects/polarity_series.py`
- `research_labs/chart_conditioned_aspects/profiles/target_aware_polarity_catalogue_v1.json`
- `docs/fields/FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1.json`
- `gann-astro-desk/src/views/FieldsWorkspace.tsx`
- `gann-astro-desk/src/views/MultiOscillatorActivityPanel.tsx`
- `gann-astro-desk/src/visualizationModes.ts`
- `docs/research/MULTI_OSCILLATOR_COMPLETION_LEDGER_V1.md`

## 2. What Exists Versus the Intended Equations

For a side such as USD or JPY, let `a_i(t)` mean event `i` is active at time
`t` according to the canonical half-open event span.

| Equation | Status | Classification |
| --- | --- | --- |
| `A_side(t) = sum_i a_i(t)` | Implemented as the raw unsigned activity count. | REPOSITORY FACT |
| `W_side(t) = sum_i s_i a_i(t)` | Potential signed active-event-count wave. `s_i` is not authorized. | MATHEMATICAL / ENGINEERING FACT + UNRESOLVED |
| `W_side(t) = sum_i s_i m_i k_i(t)` | Potential weighted wave. Neither a common `m_i` contract nor a `k_i` kernel is authorized. | MATHEMATICAL / ENGINEERING FACT + UNRESOLVED |
| `W_BASEQUOTE(t) = W_BASE(t) - W_QUOTE(t)` | Correct base/quote resultant form only after compatible signed side units exist. | MATHEMATICAL / ENGINEERING FACT + UNRESOLVED |

The current activity count is not a weak signed wave. It is a different,
unsigned observable with different units: **active canonical events**.

## 3. The Sign Problem

### Current fact

The current catalogue lookup key requires all of the following together:

1. `instrumentId` and `sideIdentity` (`FX_CURRENCY:USD` or `FX_CURRENCY:JPY`);
2. `chartId` and `chartHypothesisId`;
3. `transitBody`;
4. `natalTarget`;
5. `aspectType`;
6. a reviewed evidence packet ID and packet hash; and
7. a profile hash and evidence status.

**REPOSITORY FACT:** only `SUPPORTIVE`, `ADVERSE`, `MIXED`, and
`NEUTRAL` can be stored as a reviewed categorical polarity.
`UNKNOWN_MORE_EVIDENCE_REQUIRED` is deliberately retained as a gap rather
than admitted as a polarity. The current result is not a partially-filled
catalogue; it is an entirely empty one.

### Can sign legitimately be side- and target-conditioned?

**MATHEMATICAL / ENGINEERING FACT:** yes. The same astronomical geometry can
be evaluated against two distinct, immutable chart identities and natal targets
without an identity collision. USD and JPY may therefore carry different
records for otherwise similar transits.

**SOURCE-BACKED DOCTRINE:** none of the held source contracts reviewed closes
the extra proposition that one specific transit-to-natal event supports USD and
adversely affects JPY, or vice versa. A chart-specific claim requires a source
whose scope actually connects that chart context, target interpretation and the
claimed result. The current geometry, benefic/malefic language, or planet name
does not establish that bridge.

**UNRESOLVED:** broad sign rules, applying/separating sign changes, geography
as a universal sign gate, and a currency-specific target mapping.

### Minimum future sign evidence packet

The existing founder packet workbench and admission preparation already supply
most integrity fields. A later conceptual record should extend them rather than
replace them:

```text
eventContributionPolarityRecord (NON-RUNTIME-PROPOSAL)
  contractId, recordId, recordHash
  eventId, eventHash, eventIdentityStatus
  applyingStartUtc, exactUtc, separatingEndUtc
  sideIdentity, instrumentId
  chartId, chartHypothesisId, chartHash
  transitBody, natalTarget, aspectType, orbProfileId, profileHash
  astronomyContract, ephemerisVersion, ayanamsha, nodePolicy
  polarity: SUPPORTIVE | ADVERSE | MIXED | NEUTRAL | UNKNOWN
  contributionSign: +1 | -1 | null
  sourceTextClassification: SOURCE_BACKED_CLASSICAL_CANDIDATE |
                            FOUNDER_RESEARCH_HYPOTHESIS
  sourceId, edition, exactSourceLocator, sourceExcerptReference
  statedScope, requiredConditions, applicabilityLimits
  conflictingRecordIds, conflictDisposition
  founderDecision, reviewer, reviewedAtUtc
  outcomeBlindDeclaration, priceOrOutcomeRead: false
  admissionState, modeEligibility
```

**MATHEMATICAL / ENGINEERING FACT:** this is a documentation-only proposal. It intentionally binds polarity to the
full immutable event identity, not merely a planet/aspect label. It also
requires that `MIXED`, `NEUTRAL`, `UNKNOWN` and conflict do not masquerade
as `+1` or `-1`.

### Conflict behavior

| Situation | Recommended result | Classification |
| --- | --- | --- |
| No eligible source or founder decision | `UNKNOWN_SOURCE_ABSENT` | UNRESOLVED |
| Compiler cannot establish complete event coverage | `UNKNOWN_COMPILER_COVERAGE` | REPOSITORY FACT compatible |
| Two applicable source profiles disagree | `CONFLICT_SOURCE_PROFILES` and no signed scalar | MATHEMATICAL / ENGINEERING FACT |
| A source applies only under an unclosed context condition | `CONTEXT_GATED` until condition is supplied | MATHEMATICAL / ENGINEERING FACT |
| Founder review is incomplete | `FOUNDER_REVIEW_REQUIRED` | REPOSITORY FACT compatible |
| Valid supportive and adverse records coexist | Preserve `MIXED` components and their IDs; do not average doctrine | REPOSITORY FACT compatible |

No conflict should become a numerical average, a zero, a neutral value, or a
winner chosen from market outcomes.

## 4. Categorical State and Signed Count Should Coexist

The categorical state answers a different question from a signed count:

| Representation | What it preserves | What it loses |
| --- | --- | --- |
| Categorical side state | Supportive and adverse activity, mixedness, explicit neutral, source conflict and unknown provenance. | A compact aggregate count. |
| Raw signed active-event count | Net difference between already-authorized `+1` and `-1` event contributions. | Whether a zero came from no events, neutral, conflict, or cancellation unless companion metadata is retained. |

**MATHEMATICAL / ENGINEERING FACT:** keep both views. The signed count must be a derived,
auditable companion lane, never a replacement for categorical components. A
net zero without a breakdown is not interpretable enough for this project.

## 5. Magnitude and Equal Weight

### Equal activity contribution

For a first signed-count display, do not write `m_i = 1` as an astrological
strength claim. Use this contract wording instead:

> **`MAGNITUDE_NOT_CONFIGURED; SIGNED_ACTIVITY_UNIT = 1`** means every
> admitted active contribution supplies one engineering count unit solely to
> make a signed presence total. It does not assert that all events have equal
> astrological force.

This is a **MATHEMATICAL / ENGINEERING FACT**, not SOURCE-BACKED DOCTRINE.

### Candidate magnitude sources

| Candidate | Status | Reason |
| --- | --- | --- |
| Equal count unit | Engineering display unit only | It creates signed event-count units, not a strength model. |
| Source fractional aspect or sthana strength | Source records exist in selected Trailokya passages, but are scope-limited and do not close FX mapping, stacking, complete operator precedence or price meaning. | SOURCE-BACKED DOCTRINE / UNRESOLVED |
| Orb proximity | Could be calculated from current geometry. | EXPERIMENTAL HYPOTHESIS; no held source authorizes a financial magnitude curve. |
| Planetary dignity or Shadbala | Some components and comparisons exist, with certification and aggregation gaps. | UNRESOLVED for side-wave magnitude. |
| Ray/rashmi or Vedha strength | Some target reach and isolated modifier records exist. | UNRESOLVED; no complete Vedha operator, target-to-FX sign mapping, stack or timing rule. |
| Chart relevance | Chart identity matching is already a gate. | MATHEMATICAL / ENGINEERING FACT as eligibility, not magnitude. |
| Empirical calibration | Can be designed later. | EXPERIMENTAL HYPOTHESIS and outcome-sensitive; requires preregistration. |

**MATHEMATICAL / ENGINEERING FACT:** do not configure `m_i` in the first signed
prototype. Preserve source strength components separately in audit views until
one source profile closes applicability, composition and time scope.

## 6. Timing Kernel and Exact Time

| Candidate `k_i(t)` | Classification | Recommendation now |
| --- | --- | --- |
| Rectangular `[applyingStartUtc, separatingEndUtc)` | Current event-presence convention and a mathematically clear indicator. | Reuse only as `ACTIVITY_INTERVAL_V1`, not as source claim of equal effect across time. |
| Triangular peak at exact | Smooth engineering transform. | EXPERIMENTAL HYPOTHESIS; do not implement first. |
| Hann / raised cosine | Smooth engineering transform. | EXPERIMENTAL HYPOTHESIS; do not implement first. |
| Gaussian | Smooth engineering transform with arbitrary width. | EXPERIMENTAL HYPOTHESIS; do not implement first. |
| Exponential applying/separating | Smooth engineering transform with phase assumptions. | EXPERIMENTAL HYPOTHESIS; do not implement first. |
| Source-specific duration kernel | Would require a source whose stated time operator matches the selected contribution. | UNRESOLVED. |

**SOURCE-BACKED DOCTRINE:** the audited held evidence supplies no general rule
that an exact transit aspect must be a maximum financial magnitude, a sign
boundary, or a universal applying/separating phase boundary. The current exact
moment is a highly useful immutable identity fact, not permission to create a
peak.

**MATHEMATICAL / ENGINEERING FACT:** retain the rectangular activity interval for the
first signed count. It is the least-assumptive continuation of MO-P2 and
should be labelled an engineering activation convention. Do not smooth it.

## 7. Pair Resultant: Units, Orientation, and Unknowns

### Compatibility gate before subtraction

For `W_BASEQUOTE(t) = W_BASE(t) - W_QUOTE(t)` to be meaningful, both sides
must have all of the following in common:

1. the same contribution unit, such as `SIGNED_ACTIVE_EVENT_COUNT`;
2. the same polarity state-to-sign mapping and conflict policy;
3. the same event eligibility universe and aspect profile version;
4. the same activity/timing kernel contract;
5. the same magnitude contract, including an explicit `NOT_CONFIGURED` state;
6. the same normalization policy, including no normalization;
7. exact unioned UTC interval boundaries;
8. explicit coverage and unknown semantics;
9. separate but immutable accepted chart identities; and
10. provenance sufficient to trace every side contribution.

This is a **MATHEMATICAL / ENGINEERING FACT**. Matching only an axis range or
pixel height is insufficient.

### Orientation

For `USDJPY`, USD is the base and JPY is the quote:

```text
W_USDJPY(t) = W_USD(t) - W_JPY(t)
```

For the inverted instrument, the orientation reverses:

```text
W_JPYUSD(t) = W_JPY(t) - W_USD(t) = -W_USDJPY(t)
```

This is a **MATHEMATICAL / ENGINEERING FACT**. It says nothing about prices or
forecast direction.

### Unknown propagation

**MATHEMATICAL / ENGINEERING FACT:** if either side is unknown, incomplete, source-conflicted
or not comparably covered, the primary resultant must be
`UNKNOWN_SIDE_EVIDENCE` with `pairValue = null`. The audit panel may expose
the known side's contribution ledger, but must not show a provisional
difference as the pair's value. A partial observed difference would be too easy
to mistake for a pair signal.

Maintain distinct provenance states:

| State | Meaning |
| --- | --- |
| `NO_ACTIVE_EVENTS_KNOWN` | Complete coverage and no active eligible events. |
| `EXPLICIT_NEUTRAL` | A reviewed record explicitly assigns neutral; not absence. |
| `NET_SIDE_CANCELLATION` | Known positive and negative signed activity cancels on one side. |
| `PAIR_EQUAL_CANCELLATION` | Known compatible side waves subtract to zero. |
| `MIXED_COMPONENTS` | Positive and negative activity coexist; preserve gross counts. |
| `UNKNOWN_SOURCE_ABSENT` | No eligible sign evidence. |
| `UNKNOWN_COMPILER_COVERAGE` | Event completeness failed closed. |
| `CONFLICT_SOURCE_PROFILES` | Applicable named sources disagree. |

### Relationship to the existing pair-relative field

Reuse the existing field's exact boundary union, base-minus-quote orientation,
side provenance and hard unknown-gap behavior. Do **not** silently reuse its
`sideBalance = sideNet / sideGross`, `pairDisplay = clamp(pairRaw / 2, -1, 1)`
or categorical-score scaling. Those values belong to
`FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1`, a modern categorical research
transform. They are neither classical doctrine nor a continuous signed-wave
normalization contract.

## 8. Normalization and Resultant Options

| Method | Classification | Risk / suitability |
| --- | --- | --- |
| Raw signed counts | MATHEMATICAL / ENGINEERING FACT | Initially suitable because units are explicit and no scaling is hidden. |
| Divide by maximum possible activity | Engineering choice | Requires stable universe definition; can hide changes in event eligibility. |
| Divide by active count / gross exposure | Engineering choice | Can turn sparse activity into large apparent movement and makes zero handling delicate. |
| Side balance | Existing categorical engineering transform | Not automatically valid for a signed count. |
| Clamp to `[-1, +1]` | Engineering display transform | Can discard distinguishable event activity. |
| Z-score / rolling standard deviation | Experimental and data-window dependent | Time-varying normalization; can create look-ahead or hidden comparison changes. |
| Volatility scaling | Outcome/price dependent | Not allowed for initial construction; likely curve-fitting if chosen after results. |
| Empirical fitted normalization | Experimental hypothesis | Requires preregistration and separate validation. |

The initial pair wave can and should avoid normalization. It should expose raw
units as `SIGNED_ACTIVE_EVENT_COUNT`, including side gross counts, net counts,
coverage and contribution IDs.

| Resultant option | Assessment |
| --- | --- |
| A. Raw signed event counts: `sum s_USD - sum s_JPY` | **Recommended first prototype after polarity admission.** Smallest added assumption. |
| B. Side-balanced signed counts | Not first. Requires a distinct denominating/zero/coverage contract. |
| C. Magnitude-weighted side waves | Blocked by source scope, aggregation and time kernel. |
| D. Normalized experimental side waves | Later Mode 2 only, outcome blind and preregistered. |

## 9. Mode Mapping

The current names should not be silently renamed because they are existing UI
contracts. The recommended future mapping is:

| Existing mode | Current behavior | Future signed-wave role |
| --- | --- | --- |
| `SOURCE_ONLY_BASELINE` | Source-profiled partial display; not a general claim of a complete classical oscillator. | Admit only contributions whose exact source, scope, chart applicability, sign, time and conflict resolution pass a Mode 1 promotion gate. Until then, show gaps and source facts. |
| `CALIBRATED_RESEARCH` | Explicit experimental profile slot; no current calibrated values. | Home of `SIGNED_ACTIVITY_COUNT_V0` and any later profile with versioned parameters, source/engineering labels and outcome-blind declaration. |
| `VISUAL_ONLY_NO_SCORE` | Chart and geometry context with no directional score. | Keep unsigned event geometry/activity visible only when explicitly allowed; suppress signed side and pair paths with a clear message. |

The conceptual term **Mode 3 exploratory unsigned** describes MO-P2's current
unsigned event activity particularly well, but it is not a reason to change
the global `VISUAL_ONLY_NO_SCORE` enum in this audit. A future product directive
should decide whether the unsigned activity panel is a submode, an evidence
mode or a dedicated displayed field.

### Mode 1 admission requirements

An event contribution must not enter a source-certified Mode 1 lane until all
of these are independently true:

1. exact source, edition, page/verse/table and witness hash;
2. source scope explicitly covers the claimed role, not merely planet nature or
   geometry;
3. source applies to the event's chart, target and side context, or a distinct
   authorized mapping closes that bridge;
4. full immutable event identity, astronomy profile and accepted chart identity
   match the reviewed record;
5. polarity is explicit and applicable, not inferred from benefic/malefic or
   aspect geometry;
6. any magnitude and timing rule used is source closed, or is absent;
7. conflict, precedence and unknown policy are explicit;
8. founder approval and immutable reviewed evidence packet are present; and
9. the existing Mode 2-to-Mode 1 promotion gate passes.

No held source currently satisfies this full financial side-contribution chain.

### Mode 2 profile minimums

An experimental profile must state its event universe, sign source, activity
kernel, magnitude state, normalization state, overlap handling, unknown policy,
version/hash, outcome-blind declaration, allowed dataset scope, preregistered
test plan and promotion prohibition. It must visibly say `NOT_CLASSICAL`,
`NOT_FINANCIALLY_VALIDATED` and `executionAllowed=false`.

## 10. Market-Outcome Firewall

The following controls are required before any empirical work:

1. Freeze an event universe, chart registry version, side identities, exact
   time boundaries and event hashes before exposing outcomes.
2. Freeze a founder decision or a source packet before reading price returns.
3. Keep source-backed and founder-research records in separate profiles.
4. Keep rejected, unknown and conflicted events in the denominator/accounting;
   do not delete them after seeing outcomes.
5. Version every kernel, weight, normalization and selection rule; prohibit
   unlogged parameter changes.
6. Reserve a chronological out-of-sample interval before any calibration.
7. Record all tested variants, including negative and abandoned ones.
8. Use no post-hoc planet/aspect selection, polarity reassignment, profile
   substitution or side inversion based on USDJPY results.
9. Treat execution as a later and separate safety/financial-validation gate.

The existing founder-review workbench already demonstrates the right starting
boundary: it hides price, returns, SBC, Shadbala, AI hints and execution while
collecting identity-bound review facts.

## 11. Source Findings and Acquisition Queue

### Strongest relevant held source evidence

| Source record | What it actually closes | Why it does not close USD/JPY sign |
| --- | --- | --- |
| Trailokya 1972 TD2 | Isolated source phala fractions, isolated retrograde/exalted/debilitated records, selected context rules and Latta facts. | No FX/currency mapping, universal modifier stack, complete Vedha operator, financial polarity or timing-kernel authority. |
| Trailokya 1972 TD3R Argha | Literal commodity-basis tables, a no-zodiac-aspect gate and limited netting within the Argha pipeline. | It is not a full calculator and explicitly does not establish FX, price, return or polarity. |
| Agarwal 2000 Chapter 20 | A page-level financial/share-market hypothesis ledger. | It is research-only, not FX-mapped, not a Vedha operator and not admissible to Fields polarity. |
| Phaladeepika editor supplement | Some profile-specific geometry, natural nature and isolated modifier claims. | Current coverage retains source/motion/stacking and financial-domain gaps; nature is not a market sign. |
| Varahamihira / Brhat Samhita | Contextual geographical and eclipse/calendar evidence. | No site-to-region effect operator and no currency/market polarity mapping. |
| BPHS 1899 T1 | Calendar/Muhurta labels and engineering time boundaries. | No target-aware financial sign or timing kernel for this wave. |

**Strongest source-backed sign evidence found:** none. The strongest relevant
source-backed materials describe geometry, source result categories, isolated
fractions or historical/commodity contexts. They do not authorize the claim
that any event is supportive or adverse for USD or JPY.

### External research

No external classical or financial-astrology source was used. The held,
checksum-identified source ledgers already establish the critical negative
finding: there is no current currency-target sign operator to extend. An
external acquisition would be justified only if it offers an exact, lawful,
page-addressable operator that explicitly links a defined chart target/context
to a financial or currency result. No such acquisition is recommended merely to
fill this design gap.

The remaining source work most relevant to a later Mode 1 path is not a broad
new reading program. It is a narrowly identified proof of the missing bridge:
financial target applicability, currency/instrument mapping, contribution sign,
and any duration/precedence rule. Until a source closes that bridge, Mode 1
remains blocked regardless of available strength tables.

## 12. Staged Roadmap

| Milestone | Scope | Classification | Model recommendation | Why |
| --- | --- | --- | --- | --- |
| MO-R2: polarity admission readiness | Audit the existing founder-review packets, select a finite non-outcome event set, and document the exact evidence classifications permitted for a future admission. No wave. | REPOSITORY FACT compatible | Terra High | It is a bounded integrity and evidence-contract task. |
| MO-P3: signed categorical and raw-count side prototype | Once reviewed records are actually admitted, add source/experimental separated side panes with categorical components and `SIGNED_ACTIVE_EVENT_COUNT`; no pair until coverage is complete. | EXPERIMENTAL HYPOTHESIS | Terra XHigh | It combines strict identity semantics, UI provenance and fail-closed aggregation. |
| MO-P4: compatible FX resultant | Add raw base-minus-quote count only under the compatibility gate, preserving every unknown/conflict reason. | MATHEMATICAL / ENGINEERING FACT | Terra High | A focused composition task after side contracts exist. |
| MO-E1: experimental kernel/magnitude profile | Create a non-classical, preregistered parameter profile with no outcome read during construction. | EXPERIMENTAL HYPOTHESIS | Terra XHigh | It needs careful separation of source, engineering and empirical claims. |
| MO-V1: prospective validation | Freeze profiles, use chronological holdout and report calibration/coverage without execution. | EXPERIMENTAL HYPOTHESIS | Luna Max | It is a test/reporting exercise after architecture and parameters are frozen. |

CGVO branches, SBC expansion, calendar follow-up and other source research
remain outside this roadmap unless one supplies the missing currency-target sign
operator. They are not prerequisites for the MO-R2 review readiness work.

## 13. What Can Be Built Now, and What Cannot

| Category | Items |
| --- | --- |
| **IMPLEMENTABLE NOW WITHOUT NEW DOCTRINE** | More provenance inspection for current unsigned events; stronger integrity validation for review-packet export; categorical component/gap visualization; exact boundary/crosshair work; documentation of the proposed contribution contract. |
| **BLOCKED BY POLARITY** | `W_USD`, `W_JPY`, signed counts, any signed FX resultant and sign-based contribution display. |
| **BLOCKED BY MAGNITUDE** | Weighted waves, planet/strength weighting, orb curves, ray/rashmi weighting, normalized amplitudes and any continuous magnitude claim. |
| **BLOCKED BY SOURCE** | Source-certified financial side sign, source-certified kernel, universal timing/precedence, currency target mapping and Mode 1 contribution admission. |
| **BLOCKED BY FOUNDER DECISION** | Which verified events receive founder-research classifications, whether experimental sign-only counts are allowed, event-universe freezing and future preregistration. |

## 14. Decision Matrix

| Component | Current status | Evidence needed | Can implement now? | Recommended milestone | Risk if implemented early |
| --- | --- | --- | --- | --- | --- |
| Event timing | Exact applying/exact/separating identities exist. | No new evidence for unsigned display. | Yes, only as current canonical intervals. | MO-R2 / MO-P3 support. | Reclassifying event identity can corrupt provenance. |
| Unsigned count | Founder-accepted MO-P2 product. | None for current scope. | Already implemented. | Maintain. | Mistaking count for direction or magnitude. |
| Step wave | Unsigned rectangular counts exist; signed form does not. | Admitted sign contract. | No signed step wave now. | MO-P3. | Geometry becomes a fake polarity signal. |
| Polarity | Catalogue and packet registry are empty. | Immutable event-specific reviewed source or founder-research evidence. | No. | MO-R2. | Post-hoc sign assignment. |
| Magnitude | Not configured. | Source applicability/stacking or preregistered experimental profile. | No. | MO-E1. | Equal count or source fragment becomes unjustified strength. |
| Kernel | Rectangular activity presence only. | Source duration rule or explicit experimental profile. | Do not add one. | MO-E1. | Smoothness mistaken for doctrine. |
| Normalization | No data normalization; only shared display-axis scaling. | Explicit compatible engineering contract. | Avoid initially. | MO-E1. | Hidden rescaling and curve fitting. |
| Signed USD | Not authorized. | USD reviewed/admitted records and complete coverage policy. | No. | MO-P3. | Side wave represents absent evidence. |
| Signed JPY | Not authorized. | JPY reviewed/admitted records and complete coverage policy. | No. | MO-P3. | Side wave represents absent evidence. |
| USDJPY subtraction | Existing categorical transform only. | Compatible signed units on both sides. | No. | MO-P4. | Numeric subtraction of incomparable values. |
| UNKNOWN propagation | Strong categorical/pair gap contract exists. | Extend exact reasons to signed contract. | Documentation and tests only. | MO-P3/P4. | Unknown becomes zero or a partial pair signal. |
| Mode mapping | Existing modes are partial/calibrated/visual. | Founder decision on signed research sub-profile and Mode 1 promotion evidence. | Documentation only. | MO-R2. | Calling experimental direction classical. |

## 15. Recommended First Signed Prototype

After, and only after, polarity admission, build exactly one first architecture:

```text
Contract: SIGNED_ACTIVITY_COUNT_V0 (Mode 2 only)

Eligibility:
  - immutable canonical event identity is SINGLE_PASS_VERIFIED
  - accepted USD or JPY research chart identity matches
  - an immutable reviewed contribution record supplies SUPPORTIVE or ADVERSE
  - no applicable conflict, missing source condition or incomplete coverage

Contribution:
  s_i = +1 for SUPPORTIVE
  s_i = -1 for ADVERSE
  a_i(t) = 1 on [applyingStartUtc, separatingEndUtc), otherwise 0
  W_side(t) = sum_i s_i * a_i(t)

Explicit non-features:
  m_i is absent; label MAGNITUDE_NOT_CONFIGURED
  no smoothing, peak, interpolation or normalization
  categorical components remain visible beside W_side
  UNKNOWN / CONFLICT remains a null gap, never 0
  no SBC term, no price term, no outcome term, no execution
```

This is an **EXPERIMENTAL HYPOTHESIS**, not an implementation authorization. It minimizes
assumptions by treating its units as signed activity counts, not astrological
strength or market direction. The raw resultant may follow only after the
compatibility gate in Section 7 passes for both sides.

## 16. Bounded Follow-Up Implementation Outline

Do not execute this outline under MO-R1.

1. **MO-R2, docs and admission audit:** verify whether the existing founder
   workbench can produce a finite, complete, identity-bound review packet under
   an explicit outcome-blind policy. Do not make founder decisions and do not
   add catalogue entries.
2. **Founder decision:** approve or reject a limited
   `FOUNDER_RESEARCH_HYPOTHESIS` sign-only pilot, its event universe and its
   no-outcome preregistration.
3. **MO-P3, implementation:** admit only validated reviewed records into a new
   versioned experimental registry; render categorical components and raw
   signed counts separately; preserve gaps.
4. **MO-P4, implementation:** add a USDJPY raw signed resultant only when both
   sides satisfy the compatibility gate. Keep audit identities and source IDs
   expandable.
5. **MO-E1 / MO-V1:** propose any magnitude, kernel or normalization profile
   before outcomes, then validate prospectively and out of sample. Execution
   remains a distinct later decision.

## Verification of This Audit

This report was checked to ensure it does not claim that:

- benefic automatically means bullish;
- malefic automatically means bearish;
- aspect geometry supplies market direction;
- an unsigned USD-minus-JPY difference is a signal;
- equal event count is magnitude doctrine; or
- smooth kernels are classical doctrine.

No Python, TypeScript, Rust, API, schema, source-profile, catalogue, runtime
or product behavior changed as part of MO-R1. `executionAllowed=false` remains
the applicable product lock.
