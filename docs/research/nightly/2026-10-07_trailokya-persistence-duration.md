# Nightly Research — Trailokya persistence / duration

Date: 2026-10-07  
Status: RESEARCH_ONLY  
Branch: `research/nightly-project-work`  
Baseline verified at start: `0e7f62217d0920c85075ebfd8f407026f6ae0c9a`

Scope: bounded source/evidence adjudication only. No source-contract, production/operator/runtime, Fields, Candidate C, EMP3, provider/outcome, MT5, Auto Suggest, ML, market-direction, market-magnitude, oscillator-amplitude, or execution changes.

## Research question

After a Trailokya/SBC triggering condition is established, does the source state how long the result/effect remains operative?

The pass keeps separate:

1. astronomical condition duration;
2. source evaluation-context duration;
3. persistence/carryover of the source result;
4. modern engineering event duration;
5. commodity-specific forecast/result duration.

The existing engineering interval remains:

```
GEOMETRIC_EVENT_INTERVAL_V1
= [applyingStartUtc, separatingEndUtc)
= ENGINEERING_MAPPING
```

It is not treated as source persistence.

Likewise, Arghya v.359 beginning -> midpoint -> end is retained only as its already-source-closed **condition-progress strength rule**; this pass asks only whether anything persists after that condition ends.

## Controlling source and direct inspection

Primary authority:

Pt. Mithalal Vyas, *Sarvatobhadra Chakra with Trailokya Dipika*, Tej Kumar Book Depot, Lucknow, 1972.

Repository source ID:

`TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN`

SHA-256:

`1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`

The Library copy of the controlling 1972 scan was directly read in this pass. Relevant source pages included:

- scan pp.20-21 / printed pp.4-5 — current Vedha placement and direction;
- scan pp.31-36 / printed pp.15-20 — sign/nakshatra/pada residence and motion-state duration tables;
- scan pp.53-58 / printed pp.37-42 — v.160 timing scale, Sthana Bala/Phala and v.166;
- scan pp.64-67 / printed pp.48-51 — war, Prashna and Ubhayato;
- scan p.74 / printed p.58 — adjacent Upagraha timing example and start of Latta;
- scan pp.75-80 / printed pp.59-64 — Latta and Janma/Karma reference stars;
- scan pp.90-92 / printed pp.74-76 — Drsti/war material and decisive v.343 Vedha-result ripening rule;
- scan pp.92-102 / printed pp.76-86 — Arghya context, strength and aspect machinery;
- **scan pp.103-108 / printed pp.87-92 — verses 379-406 directly page-image inspected for the commodity-duration audit.**

The 2016 Khemraj witness remains same-lineage reading clarification only. No BPHS/Saravali/Brihat Jataka duration doctrine is imported.

## Classification vocabulary

- `SOURCE_EXPLICIT_FIXED_DURATION`
- `SOURCE_EXPLICIT_CONTEXT_BOUND_DURATION`
- `SOURCE_EXPLICIT_CONDITION_BOUND_ONLY`
- `SOURCE_EXPLICIT_POST_TRIGGER_PERSISTENCE`
- `SOURCE_SILENT_FOR_PERSISTENCE`
- `CONFLICT_OR_AMBIGUOUS`

For this packet:

- **condition-bound only** means the source gives/uses a condition and may even give that condition's astronomical duration, but does not state that the result persists after it;
- **post-trigger persistence** includes deferred/carryover fruition explicitly tied to a later trigger, even where no fixed maximum interval is stated;
- **fixed duration** means the duration is grammatically attached to the result/effect itself.

## Persistence / duration family matrix

| eventFamily | sourceLocator | triggerCondition | conditionDuration | resultPersistence | persistenceStart | persistenceEnd | durationUnit | durationSourceExplicit | postTriggerCarryover | classification |
|---|---|---|---|---|---|---|---|---|---|---|
| Native Vedha | vv.12-17 scan 20-21 / printed 4-5; vv.19-47; **v.343 scan 91-92 / printed 75-76** | one of the five SBC identities is struck by a planet; v.343 adds later Moon Vedha to the same identity | planetary nakshatra residence has separate rough astronomy tables vv.61-64, but these are not result duration | **v.343 says the previously stated auspicious/adverse Vedha result occurs on the day the Moon later strikes the same item** | prior Vedha establishes the carried result; exact latent-start mechanics not further specified | fruition is on the later Moon-Vedha day; no duration after fruition stated | DAY as fruition marker, not fixed count | yes for v.343 carryover/realization; no generic fixed duration | **yes, conditional on later Moon Vedha** | `SOURCE_EXPLICIT_POST_TRIGGER_PERSISTENCE` |
| Motion-dependent Vedha | v.14 scan 20 / p.4; vv.65-79 scan 32-36 / pp.16-20; vv.337-339 scan 90-91 / pp.74-75 | current VAKRA/SHIGHRA/SAMA, asta/udaya etc. condition changes direction/result class | source gives rough durations for nakshatra/pada residence and combustion/rise/retrograde/direct/Aticara states | no result carryover after motion class changes is stated | current condition | condition end is astronomical, but result persistence beyond it is not stated | DAYS/GHATI/MONTHS for astronomy only | yes for astronomical condition; **no for result persistence** | not established | `SOURCE_EXPLICIT_CONDITION_BOUND_ONLY` |
| Sthana Bala / Sthana Phala | vv.161-165 scan 53-54 / pp.37-38 | acting planet's current own/friend/sama/enemy sign state plus Vedha | sign occupancy is an astronomical condition; no Sthana-result duration rule | no duration assigned to obtained Sthana Phala | not stated | not stated | none | no | no | `SOURCE_SILENT_FOR_PERSISTENCE` |
| Verse-166 modifiers | vv.166-167 scan 54 / p.38 | current retrograde/swift/exalted/debilitated state | some underlying state durations are tabulated elsewhere; dignity/motion are current conditions | multiplier/base-result rule only; no duration assigned to modified result | current modifier condition | no post-condition carryover stated | condition units only, not result units | condition duration sometimes explicit; result duration no | no | `SOURCE_EXPLICIT_CONDITION_BOUND_ONLY` |
| Ubhayato Vedha | vv.220-223 scan 66-67 / pp.50-51 | simultaneous two-sided Vedha by two distinct krura planets | simultaneous overlap is required, but no numeric overlap duration stated | no survival/carryover after simultaneity ceases is stated | simultaneous compound trigger | not stated | none | no | no | `SOURCE_SILENT_FOR_PERSISTENCE` |
| Graha Latta base | vv.261-265 scan 74-75 / pp.58-59 | current planet nakshatra derives the Latta target star | current planetary nakshatra stay exists astronomically, but Latta duration is not equated to it | no base-Latta persistence interval stated | not stated | not stated | none | no | no | `SOURCE_SILENT_FOR_PERSISTENCE` |
| Latta natal compounds | vv.266-274 scan 75-77 / pp.59-61 | Latta + specified occupant on Janma Nakshatra | compound condition only | no later fixed/carryover duration stated | not stated | not stated | none | no | no | `SOURCE_SILENT_FOR_PERSISTENCE` |
| Janma/Karma/etc. reference-star family | vv.276-290 scan 77-80 / pp.61-64 | named birth/reference nakshatra receives current Vedha/Drsti | the struck-state duration is not given as a persistence interval | v.278 says avoid named auspicious undertakings when Janma/Karma etc. are under cruel Vedha; no post-Vedha carryover is stated | current afflicted-reference condition | no source carryover after condition ends | none | only condition dependence, not result duration | no | `SOURCE_EXPLICIT_CONDITION_BOUND_ONLY` |
| Prashna | vv.212-219 scan 65-66 / pp.49-50 | Prashna-time first letter/Lagna and current Vedha | point/context time; no persistence interval | some outcomes have future timing descriptors ("quickly", "after a short/long time", lifespan), but these are **forecast timing**, not persistence of the Prashna Vedha result | Prashna judgment | not stated | qualitative future timing only | no persistence duration | no | `SOURCE_SILENT_FOR_PERSISTENCE` |
| War | vv.204-211 scan 63-64 / pp.47-48; vv.340-342 scan 91 / p.75 | current war/battle Vedha conditions | battle/asta-udaya conditions are context states | injury, defeat, death, capture etc. are outcomes; no later operative-duration rule stated | current war condition | not stated | none | no | no | `SOURCE_SILENT_FOR_PERSISTENCE` |
| Country/place | vv.224-246 scan 67-72 / pp.51-56 | current Vedha to Kurma/country/place/name identities | geographic current condition only | no day/month/year carryover was located in this bounded passage | not stated | not stated | none | no | no | `SOURCE_SILENT_FOR_PERSISTENCE` |
| Arghya year/month/day context | vv.346-350 scan 92-93 / pp.76-77; **v.376 scan 102 / p.86** | choose year/month/day Arghya frame and associated country/time/commodity | YEAR begins at Jupiter sign ingress; MONTH at Sun sign ingress; DAY at sunrise | v.376 explicitly compares from the **entry-time current price** of the chosen year/month/day frame **until the end time of the Arghya determination** | selected context entry boundary | end of selected source determination context | YEAR / MONTH / DAY context | **yes, context-bound** | no beyond context stated | `SOURCE_EXPLICIT_CONTEXT_BOUND_DURATION` |
| Arghya Vakra/Udaya Bala | v.359 scan 96 / p.80 | Vakra or Udaya condition | beginning -> midpoint -> end; zero/full/zero strength | no result persists after condition end in the source wording | condition beginning | condition end; strength zero there | astronomical condition duration | yes for condition progress; no for post-condition persistence | no | `SOURCE_EXPLICIT_CONDITION_BOUND_ONLY` |
| Arghya Drsti/aspect gate | vv.365-371 scan 98-100 / pp.82-84 | Vedha plus required zodiacal aspect; paksha modifies result | current geometric/paksha condition; no duration kernel | v.371 says Vedha without required Drsti gives no result; no post-gate carryover is stated | when gate conditions are present | no later persistence stated | none | condition requirement explicit; persistence no | no | `SOURCE_EXPLICIT_CONDITION_BOUND_ONLY` |
| Nakshatra / commodity vv.379-406 | **scan 103-108 / printed 87-92, vv.379-406** | a named nakshatra receives Vedha; a listed commodity group and direction are then specified | not the astronomical duration of the Vedha; durations often greatly exceed a planetary nakshatra stay | **fixed duration belongs to the directional commodity result (sukham/asukham/pida/vyatha/etc.)** | source result is triggered by the named nakshatra Vedha; no sub-day start convention stated | after the specified fixed result period | 7 DAYS / 60 DAYS / 1 MONTH / 2 MONTHS / 8 MONTHS | **yes** | **yes, for the scoped commodity result** | `SOURCE_EXPLICIT_FIXED_DURATION` |

## Decisive new finding 1 — v.343 is deferred Vedha-result fruition, not a fixed event duration

The section heading is:

`vedha-phala-paka-kala-jnanam` — knowledge of the ripening time of Vedha result.

The root marker is:

`yaddine vidhyate candras taddine syac chubhasubham`

Bounded sense:

> on the day the Moon strikes [that same previously struck identity], the auspicious/adverse result occurs on that day.

The Hindi commentary is even clearer: if one of tithi, nakshatra, vowel, rashi or letter has been struck by a planet, and **later** the Moon strikes the same one, then on that Moon-Vedha day the previously stated auspicious/adverse Vedha result occurs.

This means:

```
VEDHA_RESULT_RIPENING_V343
= SOURCE_EXPLICIT_POST_TRIGGER_PERSISTENCE
  CONDITIONAL_ON_LATER_MOON_VEDHA
```

but **not**:

```
GENERIC_VEDHA_FIXED_DURATION = SOURCE_CLOSED
```

The source does not give:

- a maximum number of days for the latent result to remain pending;
- a continuous efficacy level between original Vedha and Moon trigger;
- a post-fruition duration after the Moon-hit day;
- a decay curve.

Therefore v.343 proves **deferred/carryover fruition**, not a generic persistence interval.

## Important non-persistence timing statements

### Verse 160 — paksha/day/kshana result scale

Direct page text says, in bounded form:

- paksha planets -> result in the paksha;
- day planets -> result in the day;
- kshana planets -> result in the kshana.

This is a **result-timing scale**.

It does **not** say the effect remains operative for the entire paksha/day/kshana after triggering.

Disposition:

```
TD1972_V160_RESULT_TIMING_SCALE
= SOURCE_EXPLICIT_TIMING_NOT_PERSISTENCE
```

### Motion-duration tables

The source gives rough astronomical durations for sign/nakshatra/pada residence and named motion/visibility states. Examples include:

- v.75 retrograde durations: Mars 76d, Mercury 23d, Jupiter 122d, Venus 45d, Saturn 137d;
- v.76 direct-motion durations: Mars 705d, Mercury 92d, Jupiter 278d, Venus 510d, Saturn 238d;
- v.78 Aticara durations: Mars 15d, Mercury 10d, Jupiter 45d, Venus 10d, Saturn 180d;
- vv.61-64 separately give rough nakshatra and pada residence times.

These are **astronomical condition durations** only.

They do not authorize:

`VEDHA_RESULT_DURATION = MOTION_STATE_DURATION`.

### Prashna vv.215-217

Movable/fixed/dual Prashna Lagna passages include outcome timing such as difficult recovery, recovery after a short/long interval, or quick recovery.

These are **forecast/outcome latencies**, not persistence of the Prashna evaluation.

### Adjacent Upagraha example vv.256-257

Direct scan p.74 says the Sannipata case gives the husband's death **within ten days** after the specified Upagraha-linked marriage condition.

That ten-day value belongs to the **Upagraha marriage outcome timing**.

It is not Latta duration and is not imported into this matrix.

## Decisive new finding 2 — Arghya context has a source-bounded decision horizon

Verses 347-349 classify time as:

- year;
- month;
- day.

Verse 349 defines the context boundaries:

- YEAR from Jupiter sign ingress;
- MONTH from Sun sign ingress;
- DAY from sunrise.

Verse 376 commentary says the current commodity price at the **entry time** of whichever year/month/day is being judged is divided into twenty parts, and the Arghya result is judged from that current price **until the end time of the Arghya determination**.

Therefore:

```
ARGHYA_CONTEXT_DURATION
= SOURCE_EXPLICIT_CONTEXT_BOUND_DURATION
```

This is not post-event persistence beyond the context.

It must not be converted into:

```
GENERIC_VEDHA_DURATION = YEAR_OR_MONTH_OR_DAY
```

## Arghya v.359 post-condition persistence

The already-closed rule is:

- beginning of Vakra/Udaya condition -> zero strength;
- midpoint -> full strength;
- end -> zero strength.

The direct 1972 commentary explicitly says the strength is 0 at the beginning and end.

No text was located saying the v.359 strength/result continues after the condition end.

Therefore:

```
ARGHYA_V359_POST_CONDITION_PERSISTENCE
= SOURCE_SILENT_FOR_PERSISTENCE
```

and:

```
ARGHYA_V359
= SOURCE_EXPLICIT_CONDITION_BOUND_ONLY
```

## Critical commodity-duration adjudication — vv.379-406

### Section ownership

Verse 378 introduces another way of deciding commodity Arghya through **nakshatra Vedha**.

The Hindi commentary says this section determines the Arghya of a specific commodity through the Vedha of a nakshatra.

Verse 378 further says:

- benefic Vedha -> lower/ordinary price tendency;
- malefic Vedha -> dear/high-price tendency;
- country, time and commodities are judged from planetary Vedha according to each nakshatra.

The following verses then attach:

1. a named nakshatra Vedha;
2. a commodity group;
3. a geographic direction;
4. a result class such as sukham, asukham, pida, vyatha or equivalent;
5. a fixed number of days/months.

### Grammatical/commentarial owner of the duration

The duration is not grammatically attached to the planet's residence in the nakshatra.

It is attached to the **directional result**.

Examples:

- v.379: `krittika-vedhato masan asta ... asukham` — from Krittika Vedha, **for eight months**, adverse result in the named direction;
- v.380: `dina-saptakam` — seven days attached to the Rohini directional result;
- v.381: `sasti-vasaran` — sixty days attached to the Mrigashirsha result;
- v.384: `pida-asta-masiki` — an eight-month affliction;
- v.385: `masikam ... sukham` — one-month favourable result;
- v.405: `masa-dvaya ... vyatha` — two-month adverse result.

The Hindi commentary repeatedly renders the construction as:

`[named commodities] ko [direction] men N din/mas phal hota hai`

— the listed commodities have the result in the named direction for the stated period.

The Sanskrit accusative-of-duration/adjectival-duration forms and the commentary agree that the duration belongs to the **commodity result horizon**, not to a generic event interval.

### Complete directly checked duration table

| Verse | Nakshatra | Direction | Fixed duration | Duration owner / result scope |
|---|---|---:|---:|---|
| 379 | Krittika | South | **8 months** | adverse result for rice, barley, gems/diamonds, metals, sesame |
| 380 | Rohini | East | **7 days** | adverse result for grains, liquids/juices, metals, old woollen goods |
| 381 | Mrigashirsha | North | **60 days** (Hindi commentary: 2 months) | adverse result for horses, buffaloes, cows, lac, kodrava, donkeys, gems, tuvar |
| 382 | Ardra | West | **1 month** | adverse result for oil, salt, alkalis/liquids, sandalwood/fragrant goods |
| 383 | Punarvasu | North | **2 months** | favourable result for gold, silver, cotton, yugandhari, kusumbha, dark silk goods |
| 384 | Pushya | South | **8 months** | afflictive result for gold, ghee, silver, rice, mineral salt, mustard, sajji, oil, asafoetida |
| 385 | Ashlesha | West | **1 month** | favourable result for madder, sugarcane products, wheat, dried ginger, pepper, kodrava, rice |
| 386 | Magha | South | **8 months** | conflict/afflictive result for sesame, oil, ghee, coral, chickpea, flax, jaggery, kanguni |
| 387 | Purva Phalguni | South | **8 months** | afflictive result for wool/blankets, yugandhari, sesame, silver goods and stated commodity |
| 388 | Uttara Phalguni | North | **2 months** | directional duration for urad, mung, pulses, rice, kodrava, rock salt, garlic, sajji |
| 389 | Hasta | North | **2 months** | favourable result for sandalwood, camphor, deodar, agarwood, red sandalwood, roots/tubers |
| 390 | Chitra | North | **2 months** | afflictive result for gold, gems, mung, urad, coral, horses/vehicles |
| 391 | Swati | North | **7 days** | stated directional result for betel nut, pepper, oils, mustard, asafoetida, dates |
| 392 | Vishakha | South | **8 months** | afflictive result for barley, rice, wheat, mung, mustard, lentils, grains, moth bean |
| 393 | Anuradha | East | **7 days** | afflictive result for tuvar, whole pulses/grains, rice, moth bean, chickpea |
| 394 | Jyeshtha | East | **7 days** | afflictive result for guggul, jaggery, lac, camphor, mercury, asafoetida, hingula, bronze |
| 395 | Mula | West | **1 month** | favourable result for white goods, liquids, grains, rock salt, cotton, salts |
| 396 | Purva Ashadha | West | **1 month** | stated result for anjana, coarse-grain products, ghee, roots/tubers, rice; archaic gloss remains partial |
| 397 | Uttara Ashadha | East | **7 days** | adverse result for horses, bulls, elephants, iron/metals, durable goods, ghee |
| 398 | Abhijit | East | **7 days** | adverse result for grapes, dates, betel nut, cardamom, mung, nutmeg, horses |
| 399 | Shravana | East | **7 days** | favourable result for walnuts, chironji, long pepper, betel-nut produce, coarse grains |
| 400 | Dhanishtha | East | **7 days** | adverse result for gold, silver, metals/coinage, gems, pearls/jewels |
| 401 | Shatabhisha | West | **1 month** | favourable result for oil, kodrava, alcoholic/aromatic substances, amla, leaves, roots, bark |
| 402 | Purva Bhadrapada | South | **8 months** | afflictive result for priyangu/aromatics, grains, metals, medicines, deodar |
| 403 | Uttara Bhadrapada | West | **1 month** | favourable result for jaggery, khanda sugar, sugar, oil-cake, rice, ghee, gems, pearls |
| 404 | Revati | West | **1 month** | favourable result for coconut, betel nut, pearls/gems and stated grocery/kirana goods |
| 405 | Ashwini | North | **2 months** | adverse result for rice/grain products, mules, camels, ghee, grains, cloth |
| 406 | Bharani | South | **8 months** | afflictive result for coarse grains, yugandhari, pepper and medicines |

Distinct fixed duration values in vv.379-406:

```
7_DAYS
60_DAYS
1_MONTH
2_MONTHS
8_MONTHS
```

The Mrigashirsha root gives **60 days**; the immediate Hindi commentary paraphrases this as **2 months**. The root value is retained as the literal duration, with the commentary gloss separately recorded.

### Commodity-duration scoped verdict

```
NAKSHATRA_COMMODITY_DURATION
= SOURCE_EXPLICIT_FIXED_DURATION
```

The duration belongs to:

```
NAMED_NAKSHATRA_VEDHA
+ NAMED_COMMODITY_GROUP
+ NAMED_DIRECTION
+ SOURCE_RESULT_CLASS
```

It does **not** belong to:

```
GENERIC_EVENT_DURATION
PLANET_NAKSHATRA_RESIDENCE
LATTA_DURATION
JANMA_REFERENCE_DURATION
PRASHNA_DURATION
WAR_DURATION
GENERIC_ARGHYA_V359_DURATION
MODERN_ASPECT_DURATION
MARKET_EVENT_DURATION
```

## Scoped verdicts

```
GENERIC_VEDHA_PERSISTENCE
= NOT_SOURCE_CLOSED_AS_FIXED_DURATION
```

with the important sub-rule:

```
VEDHA_RESULT_RIPENING_V343
= SOURCE_EXPLICIT_POST_TRIGGER_PERSISTENCE
  CONDITIONAL_ON_LATER_MOON_VEDHA
```

```
GENERIC_LATTA_PERSISTENCE
= SOURCE_SILENT_FOR_PERSISTENCE
```

```
JANMA_REFERENCE_PERSISTENCE
= SOURCE_EXPLICIT_CONDITION_BOUND_ONLY
```

```
PRASHNA_PERSISTENCE
= SOURCE_SILENT_FOR_PERSISTENCE
```

```
WAR_PERSISTENCE
= SOURCE_SILENT_FOR_PERSISTENCE
```

```
ARGHYA_CONTEXT_DURATION
= SOURCE_EXPLICIT_CONTEXT_BOUND_DURATION
```

```
ARGHYA_V359_POST_CONDITION_PERSISTENCE
= SOURCE_SILENT_FOR_PERSISTENCE
```

```
NAKSHATRA_COMMODITY_DURATION
= SOURCE_EXPLICIT_FIXED_DURATION
```

## Global verdict

Trailokya does **not** define one universal persistence/duration operator.

It does define several different temporal semantics with different owners:

1. astronomical state durations;
2. paksha/day/kshana result timing scale;
3. conditional deferred Vedha fruition under v.343;
4. Arghya year/month/day context horizon;
5. Arghya Vakra/Udaya condition progress;
6. explicit fixed directional commodity-result durations in vv.379-406.

Therefore:

```
TRAILOKYA_PERSISTENCE_DURATION
= FAMILY_SPECIFIC_ONLY
```

This result is stronger than `CONDITION_BOUND_CONTEXTS_ONLY` because vv.379-406 source-close fixed post-trigger commodity-result durations, and v.343 source-closes a separate deferred-fruition mechanism.

## Implication for GEOMETRIC_EVENT_INTERVAL_V1

The existing provenance remains unchanged:

```
GEOMETRIC_EVENT_INTERVAL_V1
= ENGINEERING_MAPPING
```

No Trailokya source finding authorizes:

```
sourcePersistenceStart = applyingStartUtc
sourcePersistencePeak = exactUtc
sourcePersistenceEnd = separatingEndUtc
```

For generic Vedha/Latta/Drsti those mappings remain unsupported.

V.343 instead uses a **second source trigger** (later Moon Vedha) for fruition.

Vv.379-406 instead use **fixed result periods** owned by a commodity/direction/nakshatra rule.

Neither maps naturally or source-safely onto the engineering aspect interval.

## Implication for DURATION_TO_TEMPORAL_SCALE_HYPOTHESIS_V1

A generic transform such as:

```
7 days -> short wave
1 month -> medium wave
2 months -> longer wave
8 months -> long wave
```

would be a new engineering hypothesis.

The source only establishes those durations for the exact commodity-result records that own them.

Therefore:

```
DURATION_TO_TEMPORAL_SCALE_HYPOTHESIS_V1
= NOT_SOURCE_AUTHORIZED_GENERIC
```

At most, a future separately authorized research profile could preserve:

```
sourceDurationValue
sourceDurationUnit
sourceDurationOwner
sourceResultScope
```

without mapping them to oscillator period, smoothing window, half-life, phase velocity, market horizon, or cross-family event duration.

## Remaining UNKNOWNs

1. Maximum latent interval allowed between an initial Vedha and the later Moon Vedha in v.343 is not stated.
2. Duration after v.343 fruition on the Moon-hit day is not stated.
3. Generic native Vedha post-condition carryover remains unclosed outside v.343.
4. Generic Latta persistence remains unclosed.
5. Latta natal-compound persistence remains unclosed.
6. Janma/Karma reference-star post-Vedha carryover remains unclosed.
7. Prashna-result persistence remains unclosed; its quick/slow outcome timing is a different concept.
8. War-result aftermath persistence remains unclosed.
9. Country/place persistence remains unclosed before the specific commodity-duration section.
10. Arghya v.359 post-condition persistence remains unclosed.
11. Arghya Drsti-gate post-condition persistence remains unclosed.
12. Commodity vv.379-406 do not provide a modern sub-day timestamp convention for the start of the fixed period; the duration is source-explicit, while exact timestamp engineering would require a separate rule.
13. No generic duration-to-market/oscillator temporal scale is source-authorized.
14. Repeated-hit amplification, decay, smoothing, half-life and nested-wave mapping were not opened.

## Overclaim guards

- Do not equate astronomical residence/state duration with result persistence.
- Do not interpret v.160 paksha/day/kshana timing as proof that a result lasts the entire unit.
- Do not interpret Prashna quick/slow outcome timing as persistence.
- Do not interpret the Upagraha ten-day death timing as Latta duration.
- Do not treat v.343 as a universal fixed-duration Vedha rule.
- Do not attach vv.379-406 durations to the planet, Vedha geometry, or modern event interval; they belong to the scoped directional commodity result.
- Do not import commodity durations into ordinary Vedha, Latta, Janma-reference, Prashna, war, Arghya v.359, generic Drsti or modern chart aspects.
- Do not map 7d/1m/2m/8m to oscillator periods or market horizons.
- Do not infer decay, smoothing, half-life, repeated-hit amplification or nested waves.
- Do not infer market direction, magnitude, oscillator amplitude, or execution.

## Recommended next gate

Stop condition for `PERSISTENCE_DURATION` is met.

A future task may investigate one of the explicitly deferred domains only under a new directive. This packet does **not** proceed into decay kernels, smoothing, temporal normalization, nested waves, repeated-hit amplification, market direction/magnitude, oscillator amplitude, or execution.

## Final locks

```
MARKET_DIRECTION = WITHHELD
MARKET_MAGNITUDE = WITHHELD
OSCILLATOR_AMPLITUDE = WITHHELD
executionAllowed = false
```
