# Nightly Research — Trailokya/SBC event-family applicability matrix

Date: 2026-10-07  
Status: RESEARCH_ONLY  
Scope: evidence/documentation only. No source-contract, production/operator/runtime/scoring/polarity/Fields/Candidate-C/EMP3/provider/outcome/MT5/execution changes.

## Question and why it matters

This pass asks what Trailokya actually identifies as the moving/current actor and the struck/reference identity for each source-defined mechanics family. The purpose is to prevent the software's modern `transitBody -> natalTarget` compiler from being mistaken for classical source authority.

The required distinction is between current planetary placement, birth/janma identity, derived Vedha/Latta targets, Prashna Lagna, war entities, country/commodity/name targets, and any later modern chart-conditioned transit-to-natal angular-aspect engineering.

## Live repository baseline

Pre-flight verified `research/nightly-project-work` exactly at expected baseline:

`09e5157d1003d9e0a98ce269680cf74dabb596fc`

The persisted 2026-10-07 Latta packet existed, but its matching status JSON and nightly-index row were absent. Those two bookkeeping omissions were repaired first without altering the packet or the Latta source contract.

Controlling repository records consulted include:

- `trailokya_1972_vedha_target_map_v1.yaml`
- `trailokya_1972_special_expansion_rules_v1.yaml`
- `trailokya_1972_planet_nature_conditions_v1.yaml`
- `trailokya_1972_vedha_magnitude_v1.yaml`
- `trailokya_1972_context_resolution_v1.yaml`
- `trailokya_1972_graha_latta_v1.yaml`
- `trailokya_1972_arghya_foundation_v1.yaml`
- TD1R/TD1R1/TD2R source-closure reports.

These contracts state that their controlling admissions came from the 1972 original page images; the 2016 Khemraj reprint is only a same-lineage reading witness.

For this pass the Internet Archive full-text/OCR of the same 1972 scan was used only to cross-locate wording. Direct PDF-image delivery redirected to an inaccessible Archive delivery host, so no OCR-only reading was allowed to override the repository's already page-image-certified admissions.

## Source framework visible in the 1972 witness

The introductory practical instructions are unusually important for applicability:

- for a person, animal, bird, country, village or traded object whose welfare/change is being judged, use the birth-name if known, otherwise the established/common name; derive its initial letter, associated nakshatra, rashi, vowel and tithi-group and place those five identities on the board;
- at the time of judging Vedha, place the planets on the nakshatras they occupy according to the panchanga;
- Vedha is then read from the planet's occupied nakshatra toward the affected board identities.

Thus Trailokya explicitly combines **current planetary positions** with **context-defined target identities**. That is not equivalent to a universal modern transit-to-natal angular-aspect model.

## Decisive applicability matrix

Allowed classification vocabulary is restricted to:
`EXPLICIT_NATAL`, `EXPLICIT_TRANSIT_CURRENT`, `EXPLICIT_CONTEXT_SPECIFIC`, `GENERAL_GEOMETRY_ONLY`, `NOT_ESTABLISHED`, `CONFLICT_OR_AMBIGUOUS`.

| eventFamily | sourceLocator | actor/current input | target/reference input | applicability | natalRequired | transitRequired | context restriction |
|---|---|---|---|---|---|---|---|
| Native LEFT/FRONT/RIGHT Vedha | vv.19-47; scan 22-27 / printed 6-11; introductory practical instructions | planet placed at its current panchanga nakshatra | enumerated board targets: nakshatra, rashi, tithi-group, letter/vowel; FRONT is one source-enumerated nakshatra | GENERAL_GEOMETRY_ONLY | false at geometry layer | true for applied planetary Vedha | geometry does not choose which contextual identity is under judgment |
| Semantic Vedha expansions | vv.48-52; scan 27-29 / printed 11-13 | same current Vedha event | paired/triplet letters, vowel co-hits, corner/Purna co-hit | GENERAL_GEOMETRY_ONLY | false | true when an applied Vedha exists | expansions inherit one causal hit, not a new target doctrine |
| Planet nature / motion conditions | vv.54-58; scan 29-30 / printed 13-14 | current planet nature, lunar phase/association, motion/state | qualifies the acting planet | EXPLICIT_TRANSIT_CURRENT | false | true | exact astronomical state delegated to accurate gaṇita/panchāṅga |
| Sthāna Bala / Sthāna Phala | vv.161-165; scan 53-54 / printed 37-38 | acting planet's current sign relationship/state | magnitude/result attached to the struck target | EXPLICIT_TRANSIT_CURRENT | false | true | not a natal-chart house/aspect rule |
| Isolated result modifiers | vv.166-167; scan 54 / printed 38 | acting planet's retrograde/swift/dignity state | previously obtained Vedha result | EXPLICIT_TRANSIT_CURRENT | false | true | combination/precedence not source-closed |
| Ubhayato Vedha | vv.220-223; scan 66-67 / printed 50-51 | two distinct krura planets producing simultaneous directional Vedhas | person's fivefold identity in v.220; name in v.221; place entities in v.223 | EXPLICIT_CONTEXT_SPECIFIC | NOT_ESTABLISHED as universal requirement | true | target identity changes by verse; no universal arithmetic |
| Graha Latta base rule | vv.261-265; scan 74-75 / printed 58-59 | planet's current nakshatra; forward/backward ordinal | derived Latta target nakshatra | GENERAL_GEOMETRY_ONLY | NOT_ESTABLISHED | true | vv.261-265 do not state Janma Nakshatra as the construction input |
| Latta compound cases | vv.266-274; scan 75-77 / printed 59-61 | Latta plus named occupant(s) | explicitly Janma Nakshatra in commentary | EXPLICIT_NATAL | true | true | birth-specific compound/occupant effects; do not universalize backward to base Latta construction |
| Latta + Upagraha + krura | v.275; scan 77 / printed 61 | Upagraha + Latta + krura planet at a nakshatra | that nakshatra | EXPLICIT_CONTEXT_SPECIFIC | NOT_ESTABLISHED | true | direct compound only; not automatically Janma |
| Janma/Karma/etc. nakshatra family | vv.276-290; scan 77 onward / printed 61-64 | planetary Vedha/dṛṣṭi | Janma-derived birth-reference nakshatras; name-nakshatra fallback when birth time unknown | EXPLICIT_NATAL | true, subject to explicit name fallback | true | source explicitly derives Karma, Ādhāna, Vināśa, Sāmudāyika, Saṅghātika etc. from Janma |
| Prashna first-letter / Lagna | vv.212-219; scan 65 / printed 49 onward | planets at question time | first uttered question-letter and/or Prashna Lagna | EXPLICIT_CONTEXT_SPECIFIC | false | true | PRASHNA only |
| War passages | vv.204-211 and vv.340-342; printed 47-49 and 75-76 | current planetary Vedha/state during conflict | kings' name/birth-rashi/fivefold classes, opponents/warriors according to passage | EXPLICIT_CONTEXT_SPECIFIC | NOT_ESTABLISHED as universal | true | WAR only; v.209 first-mover rule is conditional |
| Country/place/Kurma passages | vv.229-246; scan approx. 68-72 / printed 52-56 | current planet occupancy/Vedha | Kurma-sector countries or name-derived country/place identities | EXPLICIT_CONTEXT_SPECIFIC | false | true | country/place scope |
| Country + commodity name-letter | v.246; scan 71-72 / printed 55-56 | auspicious/adverse planetary Vedha | name letters of country and commodity | EXPLICIT_CONTEXT_SPECIFIC | false | true | forwards mixed-strength decision to later Arghya |
| General name/letter fivefold identity | vv.88-100; printed 23-26; plus introductory instructions | current planets | name initial -> vowel/tithi/nakshatra/rashi/letter identity; birth-name if known, common name otherwise | EXPLICIT_CONTEXT_SPECIFIC | false as universal; birth-name preferred when available | true | persons and non-person entities can use name identity |
| Arghya | vv.345-376; scan 92-102 / printed 76-86 | current Vedha planets plus context rulers/strengths | country/place, time and commodity (deśa/kāla/paṇya) | EXPLICIT_CONTEXT_SPECIFIC | false | true | historical commodity Arghya only; not generic market operator |

`crossFamilyInheritanceAllowed = false` for every row unless a source passage explicitly links the families.

## Special Vedha finding

The native vv.19-47 map is a **board-geometry reach rule**. Its source rows enumerate what lies to the left, front and right of a planet's occupied nakshatra. The practical instructions explicitly put planets at their current panchanga nakshatras.

But the geometry does not itself declare every struck target to be natal. The board can strike name letters, vowels, tithi groups, rashis and nakshatras, and later chapters define which identity matters in a particular application.

Therefore:

`NATIVE_VEDHA_TARGET_MAP = GENERAL_GEOMETRY_ONLY`

`APPLIED_PLANET_POSITION = EXPLICIT_TRANSIT_CURRENT`

`NATIVE_VEDHA_UNIVERSAL_NATAL_TARGET = NOT_ESTABLISHED`

This must not be converted into modern transit-to-natal angular-aspect doctrine.

## Special Latta finding

The source separates three layers.

### 1. Base Latta construction — vv.261-262

The planet is located at its **current nakshatra** and an ordinal star is struck forward or backward. The target is therefore a derived star from current planetary placement.

No Janma Nakshatra requirement is stated in the construction itself.

### 2. Base descriptive Latta effects — vv.263-265

The passage describes consequences of acting/travelling/marrying under a struck Latta star and planet-specific Latta effects. It still does not make Janma Nakshatra the universal construction target.

### 3. Explicit birth-specific compounds — vv.266-274

The Hindi commentary repeatedly says the Latta is on **Janma Nakshatra** in the Sun/Mars/Saturn/Mercury/Jupiter/Venus compound cases and the Sun-Latta occupant sequence.

Therefore:

`LATTA_BASE_CONSTRUCTION = GENERAL_GEOMETRY_ONLY`

`LATTA_V266_TO_V274_COMPOUNDS = EXPLICIT_NATAL`

It is not source-safe to rewrite all Latta as natal merely because the compound section is natal-specific.

Diminished-Moon Latta remains unestablished.

## Explicit natal chapter is separate evidence

Immediately after Latta, vv.276-290 define the Janma/Karma/etc. nakshatra family. The source states six nakshatras for people and additional ruler-specific identities, derives several from Janma Nakshatra, and permits name-nakshatra fallback when birth time is unknown.

This is strong evidence that Trailokya knows how to mark natal applicability explicitly when it intends it. It therefore argues against silently importing natal semantics into families whose own passages do not state them.

## Prashna, war and country/commodity are not natal inheritance

Prashna vv.212-219 use the first uttered question-letter and Prashna-time Lagna.

War passages operate on kings/opponents/warriors and their named source identities under war conditions; v.209's first-mover result applies only after the stated equality condition.

Country/Kurma passages map afflicted nakshatra sectors to named countries/regions, while v.246 explicitly uses country and commodity name letters.

Arghya vv.345-376 explicitly asks which commodity, in which country/place and at which time, and defines deśa/kāla/paṇya rulers and source strengths. It is therefore context-specific commodity mechanics, not a natal chart rule.

## Universal transit-to-natal verdict

`TRAILOKYA_UNIVERSAL_TRANSIT_TO_NATAL_MODEL = CONTEXT_SPECIFIC_ONLY`

Meaning:

- current/transiting planetary placement is explicitly central to applied SBC Vedha/Latta mechanics;
- Trailokya also contains explicitly natal/janma-relative target families;
- but it does **not** collapse all event families into one universal `transit planet -> natal target` operator;
- the target/reference identity is family- and context-specific.

A modern ephemeris may later supply current astronomical state to a separately reviewed research profile, but a modern chart-conditioned transit-to-natal angular-aspect compiler must not be described as direct Trailokya doctrine unless a distinct source bridge is established.

## What is source-closed

1. Current planets are placed by current panchanga nakshatra for applied Vedha.
2. Native Vedha target geometry is source-enumerated independently of a universal natal target.
3. Name-derived fivefold target identity is explicitly supported and can apply beyond persons.
4. Prashna has its own first-letter/Lagna reference.
5. Ubhayato Vedha changes target context across its verses.
6. Country/place and commodity/name-letter applications are explicit.
7. Arghya is deśa/kāla/paṇya-specific.
8. Base Latta is current-star -> derived-star geometry.
9. Latta vv.266-274 are explicitly Janma-Nakshatra compound cases.
10. The separate vv.276-290 Janma/Karma family is explicitly natal with a stated name fallback.

## What remains NOT ESTABLISHED

- a universal rule making every native Vedha target a natal target;
- a universal rule making every Latta target Janma Nakshatra;
- diminished-Moon Latta;
- cross-family inheritance of target identity;
- a source-defined modern natal longitude/aspect compiler;
- any authorization to map these mechanics to market direction, market magnitude, oscillator amplitude or execution.

## Contract implications

No source contract is changed by this run.

For later human review, the safest conceptual separation is:

- `CURRENT_PLANET_STATE`
- `SOURCE_GEOMETRY_TARGET`
- `CONTEXT_REFERENCE_IDENTITY`
- `EXPLICIT_NATAL_REFERENCE`
- `PRASHNA_REFERENCE`
- `WAR_REFERENCE`
- `COUNTRY_COMMODITY_REFERENCE`

A future research-profile proposal may bind these as separate typed inputs. It must not use one generic `natalTarget` field as a source claim.

## Proposed status

`RESEARCH_ONLY`

The applicability matrix is evidence-ready for human review, but no operator/source-contract mutation is authorized.

## Overclaim guards

- Do not infer natal semantics from geometry alone.
- Do not infer current-day-only semantics for passages that explicitly use Janma.
- Do not treat Prashna Lagna as natal Lagna.
- Do not treat name-derived rashi/nakshatra as a natal longitude.
- Do not transfer Latta compound natal semantics to base Latta construction.
- Do not transfer war/country/commodity rules to persons or vice versa.
- Do not treat Arghya as a generic market or FX operator.
- Do not infer application/exact/separation efficacy or persistence/duration; those are outside this pass.
- Do not infer market polarity or magnitude from auspicious/adverse source language.

`MARKET_DIRECTION = WITHHELD`  
`MARKET_MAGNITUDE = WITHHELD`  
`OSCILLATOR_AMPLITUDE = WITHHELD`  
`executionAllowed = false`

## Recommended next target

Stop condition for applicability is met. The next queued bounded doctrine task is **application/exact/separation timing efficacy**, followed only later by persistence/duration. Neither was opened in this run.
