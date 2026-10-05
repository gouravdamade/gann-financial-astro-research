# Nightly Research — Trailokya 1972 Modifier Combination / Precedence

Date: 2026-10-05  
Status: RESEARCH_ONLY  
Branch baseline verified: `0f2651edc243fcab1ff0241078931c17dd593e83`  
Scope: one bounded source-mechanics adjudication only. No production/operator/runtime/scoring/polarity/Fields/Candidate-C/EMP3/provider/outcome/MT5/execution changes.

## Question / task

Adjudicate the remaining Trailokya source-mechanics gap:

`TD1_MODIFIER_PRECEDENCE`

Existing isolated source records are retained without re-litigating whether they exist:

```text
Verse 166
RETROGRADE   -> 2 × source result
EXALTATION   -> 3 × source result
SWIFT        -> base/source-native result
DEBILITATION -> 0.5 × source result

Verse 167
factor inventory includes:
PLANET_CLASS
RETROGRADE / DIRECT-SWIFT-MEAN MOTION CONTEXT
EXALTATION / DEBILITATION
OWN / FRIEND / SAMA / ENEMY STHANA
```

The only question is whether Trailokya states a **general composition operator** or precedence when more than one modifier is simultaneously applicable to the same Vedha result.

## Why it matters

The isolated factors can be source-closed without authorizing a combined scalar. A runtime that silently multiplies, adds, ranks, overrides, cancels, or otherwise combines them would add doctrine unless the source itself states or demonstrates that composition.

## Repository context verified

At run start, `research/nightly-project-work` was identical to:

`0f2651edc243fcab1ff0241078931c17dd593e83`

Relevant existing contracts:

- `configs/sbc/trailokya/trailokya_1972_vedha_magnitude_v1.yaml`
- `configs/sbc/trailokya/trailokya_1972_context_resolution_v1.yaml`
- `configs/sbc/trailokya/trailokya_1972_translation_coverage_ledger_v1.yaml`
- `docs/sbc/PFR_V2B_R6_SBC_TD2R_TRAILOKYA_1972_MAGNITUDE_CONTEXT_LATTA_SOURCE_CLOSURE.md`

The repository already records:

`combinationPolicy = NOT_SOURCE_CLOSED`

`precedence = NOT_SOURCE_CLOSED`

This pass independently checked whether the controlling pages justify changing that status.

## Controlling witness

**Trailokya Dipika / Sarvatobhadra Chakra**, Pt. Mithalal Vyas, Tej Kumar Book Depot, Lucknow, 1972.

Repository source ID:

`TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN`

SHA-256:

`1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`

Citation authority: original 1972 page images.

### Pages directly inspected in this run

The Library copy of the 1972 scan was directly page-rendered for:

- scan p.52 / printed p.36 — verse 153 onward;
- scan p.53 / printed p.37 — verses 159–162;
- scan p.54 / printed p.38 — verses 163–167, including the decisive modifier passage;
- scan p.55 / printed p.39 — verses 168–171;
- scan p.56 / printed p.40 — verses 172–174;
- scan p.57 / printed p.41 — verses 175–178;
- scan p.58 / printed p.42 — verse 179 and following;
- scan pp.59–62 / printed pp.43–46 — adjacent application passages through verse 202.

This covers the requested controlling range around verses 160–179 and enough adjacent material to look for a worked combination.

## Direct source wording

### Verse 165 — bridge from sthāna strength to Vedha result

The verse says that the numerical strength arising from the place/Vedha combination is the result to be assigned to the struck object.

The Hindi commentary makes the bridge explicit: whatever `sthāna-bala` the aspecting/striking planet obtains is the Vedha result magnitude for the affected object.

This establishes the **base/source result** to which verse 166 refers.

### Verse 166 — isolated modifiers

The directly inspected Sanskrit reads:

`vakragrahe phalaṃ dvighnaṃ triguṇaṃ svocca-saṃsthite / svabhāvajaṃ phalaṃ śīghre nīcastho 'rdhaphalo grahaḥ // 166 //`

Bounded literal sense:

- with a retrograde planet, the result is doubled;
- when situated in its own exaltation, tripled;
- when swift, the natural/base result;
- when debilitated, the planet has half-result.

The Hindi commentary is particularly important because it identifies the input being transformed:

- for retrograde, **`pūrvokta prāpta phala`** — the previously obtained result — becomes double;
- swift gives the same amount already obtained;
- exaltation gives triple;
- debilitation gives half.

Thus each clause is source-closed as an **isolated transformation of the previously obtained Vedha result**.

### Verse 167 — factor inventory / instruction

The Sanskrit reads, in substance:

`grahāḥ krūrās tathā saumyā vakra-mārgocca-nīcagāḥ / sthānaṃ ca bodhyam ity evaṃ balaṃ jñātvā phalaṃ vadet // 167 //`

The Hindi commentary says to know:

- krūra versus saumya;
- retrograde versus direct/motion state;
- exalted versus debilitated;
- own/friend/sama/enemy place;

and then, **according to the foregoing method**, determine strength and state the result.

This is an instruction to consider the listed dimensions. It does **not** state:

- multiplication of simultaneous factors;
- addition;
- maximum/strongest condition wins;
- ordered precedence;
- replacement;
- cancellation;
- parallel independent outputs;
- or an exception table for coincident conditions.

The order of nouns in verse 167 is therefore not treated as an arithmetic order of operations.

## Same-lineage 2016 reading witness

Source ID:

`TRAILOKYA_DIPIKA_VYAS_KHEMRAJ_2016_REPRINT`

SHA-256:

`19CC2387C6C6B80E9A1F5A63BB9A71090A10FB17F3BD8BB56058210667F61ED8`

Role: SAME_LINEAGE_READING_WITNESS_NOT_CONTROLLING.

The accessible 2016 text reproduces the same verses and commentary structure:

- verse 165 supplies the previously obtained sthāna/Vedha result;
- verse 166 separately says retrograde double, exalted triple, swift base result, debilitated half;
- verse 167 lists nature, motion, dignity and sthāna as things to know before stating the result.

No extra sentence in the same-lineage witness supplies a combination operator or precedence rule.

## Bounded worked-example search

The controlling pages 52–62 were inspected for explicit or reconstructible combinations such as:

- retrograde + exaltation;
- retrograde + debilitation;
- exaltation + natural saumya/krūra;
- debilitation + natural class;
- motion + sthāna relation;
- dignity + sthāna phala;
- multiple simultaneous modifiers applied numerically to one Vedha result.

### Result

**No worked arithmetic was found in the bounded passage that demonstrates a combined operator.**

In particular, no example shows a base sthāna-phala such as 20/15/10/5 being transformed successively by both retrograde and exaltation, or by retrograde and debilitation.

Therefore these tempting constructions are **not source-closed**:

```text
(base × 2 × 3)     // retrograde + exaltation
(base × 2 × 0.5)   // retrograde + debilitation
max(2, 3)          // strongest modifier wins
exaltation overrides retrograde
retrograde overrides debilitation
apply in verse-167 word order
```

They remain engineering hypotheses unless a source passage or worked example is later located.

## Adjacent/context-specific rules — explicitly not generalized

The same 1972 work contains context-specific compound or override rules, but none states that it is the universal verse-166 stacking rule.

### Mercury-specific override

Verse 146 has a Mercury-only context in which specified adverse conditions invert a previously auspicious result.

Status: context-specific only.

### Jupiter / Venus adverse association

Verses 148–149 and 152 give descriptive adverse results for those planets under their stated conditions.

Status: planet-specific descriptive contexts, not a generic precedence operator.

### Disease context

Verse 188 says a krūra Vedha in disease context gives death when retrograde and continuing disease when swift.

This is a **context-specific motion-result rule**, not evidence that verse-166 numerical factors multiply or override dignity/sthāna generally.

### Prashna mixed result

Verse 213 records krūra, saumya and both/mixed outcomes in Prashna scope.

Status: context-specific qualitative resolver only.

### War first-mover rule

Verse 209 resolves its particular war condition with a first-mover rule.

Status: WAR_ONLY.

### Country/commodity stronger-result rule

Verse 246 has a stronger-source-result rule for country/commodity-name letters and points forward to later strength machinery.

Status: COUNTRY_COMMODITY scope only.

### Mixed country/Kūrma wording

Verse 243 states mixed result where auspicious and adverse influences coexist in that specific country/Kūrma context.

Status: context-specific qualitative mixed result, not universal verse-166 arithmetic.

### Latta compound

Verse 275 combines Upagraha + Latta + krūra planet and distinguishes direct versus retrograde outcomes.

Status: LATTA context only and deliberately excluded from this modifier-stacking pass.

These passages demonstrate that Trailokya is capable of stating **explicit scoped resolutions when intended**. Their existence strengthens, rather than weakens, the need to avoid inventing a universal rule where verses 166–167 do not state one.

## Later Arghya material — explicitly excluded

Later verses 357–360 define a separate Arghya/owner-strength context with:

- kṣetra strength;
- retrograde/udaya strength;
- exaltation strength;
- proportional interpolation;
- stronger owner selection.

Verses 362–365 and 375–376 then condition the later Arghya pipeline by owner relation/aspect and residual arithmetic.

This later material is **not** imported into ordinary Vedha modifier stacking.

It proves only that a later context has its own explicit strength and selection machinery.

## Does verse 167 imply precedence?

No.

Reasons:

1. It enumerates attributes/states to know.
2. It uses the general instruction to determine strength and state the result.
3. It provides no words meaning “first,” “then,” “after applying,” “whichever is stronger,” “multiply,” “add,” “cancel,” or “override” for simultaneous verse-166 modifiers.
4. The following verses 168–179 define relationships, sign lordship and dignity locations rather than a combination algorithm.
5. No worked calculation on the inspected pages demonstrates an ordered stack.

Therefore:

`VERSE_167 = FACTOR_INVENTORY_AND_EVALUATION_INSTRUCTION`

not:

`VERSE_167 = SOURCE_CLOSED_ORDER_OF_OPERATIONS`.

## Decisive outcome

```text
TD1972_MODIFIER_COMBINATION
= NO_GENERAL_RULE_LOCATED
```

and, per the directive's stop condition:

```text
TRAILOKYA_MODIFIER_PRECEDENCE
= NOT_SOURCE_CLOSED_AFTER_BOUNDED_REVIEW
```

## What is source-closed

Separately traceable isolated records remain source-closed:

```text
base_result = previously obtained sthāna/Vedha result

retrograde_modifier:
  isolated_result = 2 × base_result

exaltation_modifier:
  isolated_result = 3 × base_result

swift_modifier:
  isolated_result = base_result
  note = source says natural/base result, not literal engineering 1.0

debilitation_modifier:
  isolated_result = 0.5 × base_result
```

Verse 167 also source-closes that planet class, motion, dignity and sthāna are relevant factors to consider.

It does **not** source-close how their simultaneous outputs compose.

## What remains UNKNOWN

1. Retrograde + exaltation composition.
2. Retrograde + debilitation composition.
3. Dignity + natural-class numerical composition beyond their separately stated source meanings.
4. Dignity + sthāna-phala arithmetic when both are active.
5. Motion + sthāna-phala arithmetic when both are active.
6. Whether any verse-166 modifier replaces another.
7. Whether any strongest-condition rule applies generally.
8. Whether simultaneous isolated factors are multiplicative, additive, sequential, parallel, or intentionally left contextual.
9. Universal benefic/malefic cancellation or precedence.
10. A general multi-planet precedence operator.

## Contract implications

The existing contract is correct and should remain fail-closed:

```text
combinationPolicy = NOT_SOURCE_CLOSED
precedence = NOT_SOURCE_CLOSED
```

A future research representation may safely retain **separate provenance-bearing modifier observations**, but must not derive a combined scalar.

Recommended source-only shape:

```text
base_sthana_vedha_result
isolated_retrograde_result
isolated_exaltation_result
isolated_swift_result
isolated_debilitation_result
simultaneous_combination_result = UNKNOWN
combination_policy = NOT_SOURCE_CLOSED
```

No runtime binding is authorized.

## Next highest-value Trailokya/SBC mechanics target

The highest-value remaining source-mechanics dependency is:

`TD1_EXACT_SPEED_AND_STATIONARY_CONTRACT`

Why it should come next:

- the source-closed coarse motion families already distinguish `VAKRA`, `SHIGHRA`, and `SAMA`;
- verse 166 uses swift state directly;
- Vedha direction also depends on coarse motion family;
- the repository still records:
  - `continuousSwiftMeanThreshold = NOT_SOURCE_CLOSED`;
  - `stationaryState = SOURCE_SILENT_UNRESOLVED`;
  - `aticara.literalMaximumMotionValues` with unit interpretation unresolved.

A future bounded pass should first ask whether Trailokya itself gives enough source material to map exact/timestamped planetary motion into these coarse states or whether this must remain delegated to external `karaṇa-gaṇita` / panchāṅga astronomy.

Latta counting origin remains a separate unresolved contract and should remain separate.

Arghya worked arithmetic remains a separate later pipeline and is not the next modifier-mechanics question.

## Status

`RESEARCH_ONLY`

Proposed disposition:

`UNRESOLVED` for generic combination/precedence.

No production/source-operator/runtime change authorized.

## Guards against overclaiming

- Do not multiply 2 × 3 for retrograde + exaltation without direct source evidence.
- Do not multiply 2 × 0.5 for retrograde + debilitation.
- Do not infer “strongest wins” from verse 167.
- Do not infer precedence from word order.
- Do not import verse 209, 213, 243, 246 or 275 scoped rules into the generic modifier contract.
- Do not import Arghya owner-strength or residual arithmetic into ordinary Vedha.
- Do not merge Latta into this operator.
- Do not convert isolated modifier factors into market magnitude, polarity, score, oscillator amplitude, or execution logic.

```text
MARKET_DIRECTION = WITHHELD
MARKET_MAGNITUDE = WITHHELD
OSCILLATOR_AMPLITUDE = WITHHELD
executionAllowed = false
```

## Dated source log — 2026-10-05

- Pt. Mithalal Vyas, *Sarvatobhadra Chakra* with *Trailokya Dipika*, Tej Kumar Book Depot, Lucknow, 1972, repository Library scan. Directly inspected scan pp.52–62 / printed pp.36–46, especially vv.160–179 and adjacent application passages.
- Verse 166 direct page: scan p.54 / printed p.38.
- Verse 167 begins on scan p.54 / printed p.38 and commentary continues on scan p.55 / printed p.39.
- Khemraj Shri Krishnadas 2016 same-lineage reprint, accessible text around vv.161–179; used only as a reading witness.
- Repository source contracts listed under “Repository context verified.”

## Stop condition

The controlling passage, adjacent commentary, directly rendered pages, same-lineage witness and bounded internal cross-references do not state or demonstrate a general combination rule.

Further generic searching would not be justified without genuinely new source material or a newly identified worked example.

Stop here.
