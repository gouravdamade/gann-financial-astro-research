# Nightly Research — Trailokya application/exact/separation timing efficacy

Date: 2026-10-07  
Status: RESEARCH_ONLY  
Branch: `research/nightly-project-work`  
Baseline verified at start: `cbe46ebb1504e636121ea4d484ef08649416fd1d`

Scope: bounded source/evidence adjudication only. No source-contract, production/operator/runtime, Fields, Candidate C, EMP3, provider/outcome, MT5, Auto Suggest, ML, market-direction, market-magnitude, oscillator-amplitude, or execution changes.

## Research question

Does Trailokya/SBC source-close a temporal event-efficacy model analogous to:

```
APPLYING -> EXACT -> SEPARATING
```

with any source-defined onset before exactness, exact-contact maximum, distinct applying/separating efficacy, cessation after separation, asymmetric phase, or post-contact persistence?

Or does Trailokya instead evaluate discrete current astronomical/context states such as current nakshatra occupancy, motion class, tithi/paksha/day, Prashna time, war context, country/time/commodity context, and source-defined positional strengths?

The repository's modern start/exact/end lifecycle geometry is not treated as source authority.

## Engineering/source boundary verified first

The repository already contains a project-convention timing-phase implementation in:

`sbc/product_first_timing_phase.py`

It classifies events from supplied `startUtc`, `exactUtc`, and `endUtc` into APPLYING / EXACT / SEPARATING and normalizes the two windows separately. Its own contract is:

`PROJECT_CONVENTION_TIMING_PHASE_V1`

with classification:

`PROJECT_CONVENTION_EXPERIMENTAL`.

The source-admission ADRs are explicit that no source-certified directional timing profile is currently registered. `status/timing_phase_profile_registry.json` remains empty.

Therefore the modern lifecycle geometry, including any `GEOMETRIC_EVENT_INTERVAL_V1` or equivalent `[applyingStartUtc, separatingEndUtc)` event interval, is an engineering representation unless a source family independently supplies matching temporal semantics.

## Controlling source policy

Primary authority remains the page-image-certified 1972 Trailokya witness already admitted by the repository:

- Pt. Mithalal Vyas, *Sarvatobhadra Chakra with Trailokya Dipika*, Tej Kumar Book Depot, Lucknow, 1972.
- source ID: `TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN`
- SHA-256: `1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`
- citation authority: original 1972 page images.

The 2016 Khemraj witness remains same-lineage reading clarification only. No BPHS, Saravali, Brihat Jataka, modern ephemeris convention, software behavior, or market outcome is imported to fill a Trailokya timing gap.

## Classification vocabulary

Only the following classifications are used:

- `SOURCE_EXPLICIT_PHASE_RULE`
- `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY`
- `SOURCE_EXPLICIT_TIME_CONTEXT_ONLY`
- `SOURCE_SILENT_FOR_PHASE`
- `CONFLICT_OR_AMBIGUOUS`

A discrete state or named time context is not promoted to a phase rule.

## Family timing matrix

| eventFamily | sourceLocator | timeReference | triggerState | onsetRule | exactRule | separationRule | cessationRule | persistenceRule | phaseStrengthRule | classification |
|---|---|---|---|---|---|---|---|---|---|---|
| Native Vedha geometry | practical intro scan 9-11; vv.16-17 scan 21 / printed 5; vv.19-47 scan 22-27 / printed 6-11 | planets placed at the nakshatras they occupy at the time Vedha is judged | current planet occupies a source nakshatra and its source-defined Vedha reaches a board target | none stated before occupancy/reach | no exact-contact timestamp or peak stated | none stated | no geometric-separation cessation operator stated | not adjudicated beyond absence in this passage | none | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Motion-dependent LEFT/FRONT/RIGHT Vedha | vv.12-14 scan 20 / printed 4; vv.65-79 scan 32-36 / printed 16-20 | current motion class / current Sun-relative coarse state; exact astronomy delegated to accurate ganita/panchanga | VAKRA -> right; SHIGHRA -> left; SAMA -> front for variable-motion planets | none | none | none | state changes when source motion category changes; no applying/separating kernel stated | none stated in audited motion passage | motion class changes direction/category, not phase efficacy | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Sthana Bala / Sthana Phala | vv.160-165 scan 53-54 / printed 37-38 | v.160 records paksha/day/kshana timing context; vv.161-165 use current sign relationship and struck target | own/friend/sama/enemy sthana plus current Vedha | none | no event-contact exactness | none | no aspect-separation rule | none stated here | fixed source fractions/results by sthana category; not applying/exact/separating | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Isolated result modifiers | vv.166-167 scan 54 / printed 38 | current retrograde/swift/exaltation/debilitation state | one named state modifies previously obtained result | none | none | none | ceases only when named state no longer applies; no source phase boundary operator stated | none | categorical factors/base result only; no applying/separating weighting | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Ubhayato Vedha | vv.220-223 scan 66-67 / printed 50-51 | simultaneous current Vedhas from two distinct krura planets | required two-sided directional pair is simultaneously present | no pre-simultaneity onset rule | simultaneity is a trigger condition, not an exactness peak | no post-simultaneity separation rule | no explicit temporal cessation beyond loss of required compound state | none stated | no phase weighting/arithmetic stated | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Graha Latta base | vv.261-265 scan 74-75 / printed 58-59 | planet's present/current nakshatra | current planet position generates its ordinal forward/backward Latta star | none before current-star construction | no exact timestamp or peak | none | no explicit post-exit efficacy rule in vv.261-265 | persistence deliberately deferred; none stated in this bounded passage | none | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Latta natal compounds | vv.266-274 scan 75-77 / printed 59-61 | current Latta plus named occupant condition at Janma Nakshatra | specified compound is present | none | none | none | no source phase cessation operator stated | deferred | result is compound-state specific, not phase weighted | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Janma/Karma/etc. nakshatra family | vv.276-290 scan 77 onward / printed 61-64 | current planetary Vedha/drsti evaluated against named natal/reference nakshatras | source reference star is struck | none | none | none | no applying/separating cessation rule stated | deferred | none located | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Prashna | vv.212-219 scan 65 onward / printed 49 onward | `prashnakale` / query time; first uttered letter and/or Prashna Lagna | source condition is evaluated at the named Prashna context | no pre-Prashna onset | no exactness peak around Prashna time | no separating phase | rule is tied to Prashna context, not a surrounding kernel | no surrounding persistence interval stated in audited passage | none | `SOURCE_EXPLICIT_TIME_CONTEXT_ONLY` |
| War | vv.204-211 printed 47-49; later vv.340-342 printed 75-76 | war/battle context and current Vedha conditions | named opposed-ruler/combatant conditions; v.209 includes equal-condition first-mover case | none | none | none | no generic after-contact rule | deferred | outcomes depend on current war conditions, not temporal phase from exactness | `SOURCE_EXPLICIT_TIME_CONTEXT_ONLY` |
| Country/place/commodity/name | vv.229-246 scan approx. 68-72 / printed 52-56 | current planetary occupancy/Vedha in country/Kurma/name-letter contexts | named geographic/name/commodity target receives source condition | none | none | none | no applying/separating operator | later duration material intentionally outside this pass | none | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Arghya context clock | vv.345-357 scan 92-95 / printed 76-79 | explicit time levels YEAR / MONTH / DAY; boundaries: Jupiter sign ingress / Sun sign ingress / sunrise | appropriate desa/kala/panya ruler/context selected | context begins at source-defined temporal boundary | no aspect-contact exactness peak | no applying/separating phase | next source time boundary changes the context | persistence beyond those context categories not adjudicated here | none from these context verses | `SOURCE_EXPLICIT_TIME_CONTEXT_ONLY` |
| Arghya Kshetra Bala | v.358 scan 95-96 / printed 79-80 | current position within sign | own/friend/neutral/enemy base strength, diminished away from sign midpoint | positional interpolation, not temporal onset | sign midpoint is a positional maximum, not an event exact-contact timestamp | positional falloff, not separating phase | spatial boundary policy incomplete for timestamped computation | not a temporal persistence rule | positional strength gradient only | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Arghya Vakra/Udaya Bala | v.359 scan 96 / printed 80; v.361 scan 97 / printed 81 | progress through the named Vakra or Udaya condition | source condition has a beginning, middle, and end | zero at condition beginning | **full at condition midpoint** | decreases after midpoint toward condition end | zero at condition end | no post-condition persistence stated | direct/inverse proportional trairashika within the condition; modern triangular formalization is engineering | `SOURCE_EXPLICIT_PHASE_RULE` |
| Arghya Uccha Bala | v.360 scan 96 / printed 80 | current zodiacal position relative to maximum exaltation/debilitation | paramocca/neecha positional state | not temporal | maximum exaltation is full; maximum debilitation is half; intermediate by trairashika | not temporal | not a temporal cessation rule | none | positional strength interpolation, not applying/exact/separating timing | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |
| Trailokya Drsti/aspect gate inside Arghya | vv.365-371 scan 98-100 / printed 82-84 | current geometric Vedha plus required zodiacal aspect category; paksha state | geometric Vedha must also have stated aspect; ordinary aspect padas and special full aspects; Shukla/Krishna modifier | no aspect-orb onset stated | no exact-degree contact maximum stated | no separating aspect phase stated | gate becomes inactive without required aspect, but no temporal separation kernel is specified | none stated here | strength is by aspect-pada category and paksha full/half, not before/exact/after | `SOURCE_EXPLICIT_DISCRETE_STATE_ONLY` |

## Direct wording markers and what they do — and do not — establish

### Practical current-position instruction

The page-certified practical introduction places planets at the nakshatras they occupy at the time Vedha is being judged.

This establishes a **current-state evaluation point**.

It does not establish:

- an applying onset before entering the source condition;
- an exact-contact maximum;
- a separating tail;
- or a symmetric/asymmetric temporal efficacy kernel.

### Motion verses

The source classes motion into Vedha-direction families and delegates precise astronomy to suitable ganita/panchanga.

That means motion state can change which Vedha direction is active.

It does not mean:

```
approaching retrograde station -> increasing efficacy
station -> exact maximum
moving away from station -> decreasing efficacy
```

No such timing rule was located, and stationary handling itself remains source-unclosed from the prior bounded pass.

### Verse 160 temporal categories

The already page-certified TD2 record says v.160 supplies timing context for **paksha, day, and kshana planets**.

This is evidence for source time categories/scales, not an applying/exact/separating lifecycle.

Nothing in the admitted v.160 record assigns a pre-exact ramp, exact peak, or separating decay.

### Sthana Bala / Phala and verse 166

Verses 161-165 compute source result by sthana category and attach it to the struck target.

Verse 166 modifies the already obtained result when the acting planet is retrograde, exalted, swift, or debilitated.

These are state/result rules.

They do not source-close event-phase weighting.

### Ubhayato Vedha

Verses 220-223 require simultaneous two-sided Vedha conditions.

"Simultaneous" is a conjunction of discrete source states. No passage located in the bounded contract says that the result grows while the two conditions approach simultaneity, peaks at a unique exact instant, or fades after they separate.

### Latta

Verses 261-262 derive the Latta target from the planet's present nakshatra; later verses describe base and natal compound results.

No before/exact/after timing example was located in vv.261-275.

This pass deliberately does **not** adjudicate how long a Latta result persists after a planet changes nakshatra. That is reserved for the next persistence/duration task.

### Prashna

The Prashna material is explicitly query-time specific.

A named query time is an evaluation context, not evidence of a surrounding efficacy interval.

No source rule located says the Prashna effect ramps before the question, peaks at the question timestamp, and decays afterward.

### War

War passages apply named rules in battle/war conditions, including v.209's bounded first-mover rule.

No applying/exact/separating kernel is stated for the underlying Vedha conditions.

### Arghya year/month/day context

Verses 346-350 define temporal context classes:

- year boundary by Jupiter sign ingress;
- month boundary by Sun sign ingress;
- day boundary by sunrise.

These are explicit source time-context boundaries.

They are not aspect-phase boundaries.

### Arghya v.359 is the decisive family-specific exception

Verse 359 is materially different from the rest of the audited corpus.

The page-certified contract records for **Vakra Bala** and **Udaya Bala**:

- zero at the beginning of the condition;
- full at the middle of the condition;
- zero at the end;
- intermediate strength by trairashika/proportion.

This is a genuine source-explicit phase/condition-progress rule.

However, it is **not** a generic Vedha/Latta/Drsti applying-exact-separating rule.

Specifically:

1. its "middle" is the midpoint of the **Vakra or Udaya condition**, not the exact instant of a Vedha ray, Latta target, or zodiacal aspect contact;
2. the source-closed repository does not yet have source-safe begin/end timestamps or a midpoint provider for those astronomical conditions;
3. the modern triangular function used in equation passports is explicitly a formalization, not literal source algebra;
4. it belongs to Arghya ruler-strength machinery and must not be inherited by ordinary Vedha.

Thus:

`ARGHYA_VAKRA_UDAYA_BALA_PHASE = SOURCE_EXPLICIT_PHASE_RULE`

while:

`GENERIC_VEDHA_EVENT_PHASE = NOT_SOURCE_CLOSED`.

### Arghya positional maxima are not temporal exactness

Verse 358 has a sign-midpoint strength maximum/falloff.

Verse 360 has maximum exaltation/debilitation positional rules and interpolation.

These are longitude/position-dependent strength rules. They must not be mislabeled as "exact aspect peak" or temporal applying/separating efficacy.

### Arghya Drsti/aspect passage

Verses 365-371 require both Vedha and the stated zodiacal aspect. They encode:

- ordinary aspect padas;
- special full aspects;
- a Shukla/Krishna result modifier.

No admitted wording gives:

- an orb before exact aspect;
- a unique exact-degree maximum beyond the categorical aspect rule;
- applying-versus-separating asymmetry;
- or post-separation decay.

This passage therefore supports a **discrete aspect-strength category**, not an applying/exact/separating kernel.

## Worked temporal-example search result

Across the named page-certified families and their existing source contracts, no worked example was located that numerically distinguishes all three of:

```
before exact
exact
after exact
```

for a Vedha, Latta, Janma-reference hit, Ubhayato event, Prashna event, war event, or Drsti/aspect contact.

The sole source-explicit beginning/middle/end strength structure found is Arghya v.359 for Vakra/Udaya Bala.

That is sufficient to close a **family-specific condition-phase rule**, but insufficient to authorize a universal event phase model.

## Answers to target questions

### A. Is efficacy simply while a source-relevant current state is present?

For most audited families, the source contract is state-based: current nakshatra, motion class, sthana, named compound, Prashna context, war context, or source time category.

That does not by itself define continuous efficacy across the state's full astronomical interval.

Arghya v.359 is the exception because it explicitly varies strength within the Vakra/Udaya condition.

### B. Does Trailokya distinguish an approaching condition from an exact one?

Not for ordinary Vedha, Latta, Ubhayato, Janma-reference hits, Prashna, war, or the Arghya aspect gate.

For Arghya Vakra/Udaya Bala it distinguishes beginning, middle, and end of the condition, but not "applying to geometric contact" versus "separating from geometric contact."

### C. Does exact contact receive greater result than non-exact contact?

No generic exact-contact rule was located.

Arghya v.358/v.360 contain positional maxima, and v.359 contains a condition-midpoint maximum, but none is a generic exact Vedha/Latta/Drsti-contact peak.

### D. Applying stronger/weaker, exact maximum, separating weaker, post-contact persistence?

No generic source model located.

Arghya v.359 supplies a symmetric-looking source condition profile (zero -> full -> zero), but the repository correctly marks its timestamp boundaries/provider as unresolved. No post-condition persistence is stated there.

### E. Does motion direction affect timing efficacy?

In ordinary Vedha, motion class affects Vedha direction and categorical result semantics.

It does not source-close applying/exact/separating timing efficacy.

In Arghya only, Vakra itself also participates in a separate strength dimension with a beginning/middle/end profile.

### F. Do tithi, paksha, day, kshana define efficacy windows rather than phase windows?

They define source temporal categories/contexts and, in the Arghya aspect passage, paksha modifies result.

They do not establish a geometric applying/exact/separating kernel.

### G. Latta persistence after target formation?

No persistence rule is stated in the bounded vv.261-275 Latta passage used here.

The duration question is intentionally deferred to the next task.

### H. Prashna, war, Arghya named times versus surrounding intervals?

Prashna and war passages are evaluated in their named contexts; no surrounding phase interval is source-closed.

Arghya has explicit year/month/day context boundaries and separately the v.359 Vakra/Udaya internal phase rule.

### I. Worked before/exact/after example?

None located for ordinary Vedha/Latta/Drsti mechanics.

## Decisive verdict

A universal Trailokya APPLYING / EXACT / SEPARATING efficacy model is **not** source-closed.

At least one family does contain an explicit phase-like rule, so the strongest accurate global disposition is:

```
TRAILOKYA_APPLICATION_EXACT_SEPARATION_EFFICACY
= FAMILY_SPECIFIC_ONLY
```

with the scoped sub-verdicts:

```
GENERIC_VEDHA_APPLICATION_EXACT_SEPARATION
= SOURCE_SILENT_FOR_PHASE

GENERIC_LATTA_APPLICATION_EXACT_SEPARATION
= SOURCE_SILENT_FOR_PHASE

JANMA_REFERENCE_APPLICATION_EXACT_SEPARATION
= SOURCE_SILENT_FOR_PHASE

PRASHNA_APPLICATION_EXACT_SEPARATION
= SOURCE_SILENT_FOR_PHASE

WAR_APPLICATION_EXACT_SEPARATION
= SOURCE_SILENT_FOR_PHASE

ARGHYA_DRSTI_APPLICATION_EXACT_SEPARATION
= SOURCE_SILENT_FOR_PHASE

ARGHYA_VAKRA_UDAYA_BALA_CONDITION_PHASE
= SOURCE_EXPLICIT_PHASE_RULE
```

This is not equivalent to saying Trailokya has a modern event lifecycle model.

## Implication for APPLICATION_EXACT_SEPARATION_EFFICACY_V1

The generic proposed contract should remain fail-closed:

```
APPLICATION_EXACT_SEPARATION_EFFICACY_V1
= SOURCE_SILENT
```

unless it is explicitly scoped to a separately named Arghya Vakra/Udaya Bala condition-phase profile.

The v.359 family-specific phase must not be used to populate generic Vedha, Latta, Drsti, chart-aspect, or market-event timing fields.

## Implication for GEOMETRIC_EVENT_INTERVAL_V1

```
GEOMETRIC_EVENT_INTERVAL_V1
= ENGINEERING_MAPPING
```

remains the correct provenance class.

Its `applyingStartUtc`, `exactUtc`, and `separatingEndUtc` fields may be useful as event identity/engineering geometry, but Trailokya does not authorize treating them as efficacy weights for the audited families.

Likewise:

- exact timestamp != source-defined efficacy maximum;
- applying interval != source-defined ramp;
- separating interval != source-defined decay;
- asymmetric engineering windows != source-defined asymmetry;
- interval end != source-defined persistence cessation.

Arghya v.359 can only motivate a **separate source-profiled condition-progress research object** once its own begin/end/midpoint astronomy dependencies are human-reviewed and source-safe.

## Unresolved items retained

1. No source-closed generic Vedha applying/exact/separating operator.
2. No source-closed generic Latta applying/exact/separating operator.
3. No source-closed generic Drsti/aspect temporal orb or exactness kernel.
4. No source-closed applying-versus-separating asymmetry.
5. No source-closed post-contact persistence from this pass.
6. Arghya Vakra/Udaya begin/end timestamps and midpoint policy remain unresolved engineering dependencies.
7. Generic event duration/persistence remains the next separate task.
8. Exact-speed/stationary, modifier stacking, applicability, and Latta counting-origin findings are preserved and not reopened.

## Source/engineering guards

- Do not infer temporal efficacy from current-position wording alone.
- Do not infer a phase curve from tithi, paksha, day, kshana, year, month, or sunrise boundaries.
- Do not equate "middle" in Arghya v.359 with exact Vedha/Drsti contact.
- Do not equate sign midpoint in v.358 with exact event time.
- Do not equate maximum exaltation in v.360 with exact aspect contact.
- Do not turn aspect padas in vv.365-371 into temporal orbs.
- Do not turn Shukla/Krishna full/half into applying/separating strength.
- Do not import the Arghya v.359 phase into native Vedha, Latta, Janma-reference, Prashna, or war mechanics.
- Do not infer persistence after event separation in this pass.
- Do not alter `PROJECT_CONVENTION_TIMING_PHASE_V1` or the empty source-certified timing registry from this evidence packet.
- Do not infer market direction, market magnitude, oscillator amplitude, trading direction, or execution.

## Recommended next bounded target

Per the queue, the next independent task is:

`PERSISTENCE_DURATION`

It should ask source-family by source-family whether effects continue after the triggering condition, and must keep explicit commodity-duration verses separate from ordinary Vedha/Latta duration.

That task is **not opened here**.

## Final locks

```
MARKET_DIRECTION = WITHHELD
MARKET_MAGNITUDE = WITHHELD
OSCILLATOR_AMPLITUDE = WITHHELD
executionAllowed = false
```
