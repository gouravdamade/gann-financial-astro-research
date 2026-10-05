# Nightly Research — Trailokya exact speed / stationary contract

Date: 2026-10-06  
Status: RESEARCH_ONLY  
Scope: evidence/documentation only. No production/operator/source-ledger/evidence-registry/runtime/scoring/polarity/provider/outcome/MT5/Candidate-C/EMP3/execution changes.

## Why this task

The live nightly index shows that the Sārāvalī 4.32–33 discrepancy was already exhausted on 2026-10-05, followed by the Trailokya Moon-boundary and modifier-precedence passes. The latest unresolved Trailokya mechanics target is therefore the exact speed / stationary contract. Generic Drik-Bala searching remains frozen.

The current source contract `configs/sbc/trailokya/trailokya_1972_sthula_motion_classifier_v1.yaml` source-closes coarse motion families but still records:

- `continuousSwiftMeanThreshold: NOT_SOURCE_CLOSED`;
- `stationaryState: SOURCE_SILENT_UNRESOLVED`;
- `aticara.unitInterpretation: SOURCE_UNRESOLVED`.

This pass asks whether the controlling 1972 pages themselves close any of those gaps.

## Controlling witness and pages inspected

Pt. Mithalal Vyas, *Sarvatobhadra Chakra* with *Trailokya Dipika*, Tej Kumar Book Depot, Lucknow, 1972. Repository source ID `TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN`, SHA-256 `1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`.

Direct page-image inspection this run:

- scan p.32 / printed p.16: vv.65–67;
- scan p.33 / printed p.17: vv.68–71;
- scan p.34 / printed p.18: vv.72–75;
- scan p.35 / printed p.19: vv.75–77;
- scan p.36 / printed p.20: vv.78–80.

## Source findings

### 1. Coarse families are categorical, not continuous-speed thresholds

Verses 65–66 divide motion into three Vedha-relevant families:

- `VAKRA`: vakra, ativakra, kuṭila;
- `ŚĪGHRA`: aticāra / swift;
- `SAMA`: manda and madhya.

The Hindi commentary explicitly groups manda + madhya under sama and aticāra under śīghra. This confirms the existing coarse family contract but does not state a numerical instantaneous-speed boundary between `SAMA` and `ŚĪGHRA`.

### 2. Verses 69–72 provide sthūla Sun-relative state classification

For Mars/Jupiter/Saturn, vv.69–71 classify motion by the Sun's sign-distance: second = śīghra, third = sama, fourth = manda, fifth/sixth = vakra, seventh/eighth = ativakra, ninth/tenth = kuṭila, eleventh/twelfth = śīghra again; conjunction/within combustion context becomes asta.

Verse 72 separately gives Mercury/Venus coarse cases: second from Sun = vakra, twelfth = śīghra, third/eleventh = sama.

These are expressly described as `sthūla-māna` (coarse measure). They are not a continuous velocity threshold and should not be converted into one.

### 3. Verse 77 defines Aticāra by unusually rapid traversal

The Hindi commentary says that when a planet traverses, in a much shorter time, the portion of a sign that it would ordinarily cover in its normal motion and proceeds onward, it is called `aticārī`.

The directly inspected printed page then gives maximum/very-fast motion figures. The page image reads:

- Mars: `46|11`;
- Mercury: `113|32`;
- Jupiter: `14|4`;
- Venus: `75|42`;
- Saturn: `7|45`.

The commentary calls these `parama śīghragāmī`, i.e. maximally/very swift, and identifies that state with Aticāra.

### Important textual correction discovered

The live repository contract currently records Jupiter as `14|14`. The controlling 1972 page image instead visibly reads **`14|4`**. This is not a runtime correction in this pass; it is an evidence finding requiring a separate human-reviewed source-contract correction.

A later secondary SBC exposition by M. K. Agarwal independently prints the same five “Very fast” values as Mars 46′11″, Mercury 113′32″, Jupiter 14′4″, Venus 75′42″ and Saturn 7′45″. That source is corroborative only, not controlling.

### 4. Unit interpretation is strongly identifiable but not an operator threshold

The numeric pattern is astronomically coherent as arcminutes and arcseconds of daily longitudinal motion, and Agarwal explicitly renders the same values with prime/double-prime notation. Thus the best bounded reading is:

`46|11 = 46′11″`, etc.

Confidence: HIGH for the notation/value interpretation; however Trailokya v.77 does not itself state that these maxima are the lower boundary for entering the entire `ŚĪGHRA` family. They are presented as **parama śīghra / Aticāra** values.

Therefore it would be an overclaim to implement:

`instantaneous_speed >= listed_value => SHIGHRA`

or to derive an unprinted midpoint/boundary between `SAMA` and `SHIGHRA`.

### 5. Verse 79 explicitly delegates exact astronomy

Verse 79 says, in substance, that for the place and time in question, whichever astronomical computation (`gaṇita`) agrees with observed/correct phenomena should be used to obtain the planets' exact (`sphuṭa`) positions. The Hindi commentary explicitly mentions agreement for rising/setting, retrograde/direct motion, sign and nakṣatra motion.

This is positive source evidence that the preceding residence-day and coarse tables are not a self-contained exact ephemeris engine.

Disposition:

`EXACT_ASTRONOMY = EXTERNAL_GANITA_DELEGATED`

remains correct.

### 6. Stationary state

No inspected verse 65–79 gives a distinct stationary (`sthambha`, `sthira`, zero-speed, station-before-retrograde, or station-before-direct) Vedha class or direction.

The text moves between named coarse states and delegates exact astronomical determination to suitable gaṇita. Absence of a stationary rule must not be converted into `SAMA`, `VAKRA`, or `SHIGHRA` by engineering convention.

Disposition:

`stationaryState = SOURCE_SILENT_UNRESOLVED`

remains correct.

## Decisive answers

### Continuous swift/mean threshold

`TRAILOKYA_CONTINUOUS_SHIGHRA_SAMA_THRESHOLD = NOT_SOURCE_CLOSED_AFTER_BOUNDED_REVIEW`

The source supplies categorical/coarse cases and Aticāra maxima, but no universal continuous numerical boundary separating Sama from Śīghra.

### Stationary handling

`TRAILOKYA_STATIONARY_VEDHA_DIRECTION = NOT_SOURCE_CLOSED_AFTER_BOUNDED_REVIEW`

No distinct stationary Vedha rule was located in the controlling motion passage.

### Aticāra units

`TRAILOKYA_V77_ATICARA_VALUE_NOTATION = ARC_MINUTE_ARC_SECOND_READING_HIGH_CONFIDENCE`

with values:

- Mars 46′11″;
- Mercury 113′32″;
- Jupiter 14′4″;
- Venus 75′42″;
- Saturn 7′45″.

This interpretation does **not** create a Sama/Śīghra threshold.

## Contract impact

No production or source contract was modified. The current research contract should continue to fail closed on continuous threshold and stationary handling.

One source-data correction should be queued for separate human review:

`aticara.literalMaximumMotionValues.JUPITER: '14|14' -> '14|4'`

The correction is directly supported by the controlling 1972 page image and corroborated by the later SBC exposition. It is not applied here because this run is evidence/documentation-only.

## What remains UNKNOWN

1. A source-defined exact instantaneous boundary between `SAMA` and `ŚĪGHRA`.
2. A source-defined zero-speed/stationary Vedha direction.
3. Whether another explicitly cited gaṇita text was intended by Vyas for exact state transitions; v.79 deliberately permits the locally/time-appropriate accurate gaṇita rather than naming one universal computational canon.
4. Exact handling at astronomical station instants in the Vedha operator.
5. Whether the v.77 maximum figures are intended as daily motion values in every computational tradition; the arcminute/arcsecond reading is strongly supported, but the verse does not define a modern ephemeris API contract.

## Overclaim guards

- Do not treat the v.77 Aticāra maxima as the lower threshold for all Śīghra motion.
- Do not interpolate a Sama/Śīghra cutoff from the printed maxima.
- Do not map zero speed to Sama merely because Sama contains manda/madhya.
- Do not infer Vedha direction at station from adjacent direct/retrograde states.
- Do not replace v.79's gaṇita delegation with a preferred modern ephemeris without a separate engineering/source-profile decision.
- Do not infer polarity, price direction, market magnitude, oscillator amplitude or execution semantics from motion class.

`MARKET_DIRECTION = WITHHELD`  
`MARKET_MAGNITUDE = WITHHELD`  
`OSCILLATOR_AMPLITUDE = WITHHELD`  
`executionAllowed = false`

## Proposed status

`UNRESOLVED` for exact continuous threshold and stationary direction.

`RESEARCH_ONLY_CORRECTION_READY_FOR_HUMAN_REVIEW` for the Jupiter v.77 literal value `14|4` and the arcminute/arcsecond notation interpretation.

## Recommended next evidence target

The exact-speed/stationary search has reached its bounded stop condition: the controlling motion passage is explicit about coarse categories, Aticāra maxima and gaṇita delegation, but silent on a continuous Sama/Śīghra threshold and stationary Vedha direction.

Next Trailokya/SBC mechanics target should therefore move away from generic speed searching. The highest-value unresolved item in the existing readiness record is the **Latta counting-origin contract**, kept strictly separate from ordinary Vedha and modifier stacking. A bounded pass should adjudicate whether the source's ordinal language or worked examples establish inclusive/exclusive counting origin for the stated forward/backward Latta offsets.
