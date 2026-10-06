# Nightly Research — Trailokya Latta counting-origin adjudication

Date: 2026-10-07  
Status: RESEARCH_ONLY  
Scope: evidence/documentation only. No production/operator/source-ledger/runtime/scoring/polarity/Fields/Candidate-C/EMP3/provider/outcome/MT5/execution changes.

## Why this task

The live branch already contains the completed exact-speed/stationary packet dated 2026-10-06. Its bounded stop condition was reached, so this run advanced to the next explicitly queued Trailokya/SBC mechanics gap: whether Graha-Latta ordinal offsets count the planet's occupied nakshatra as position 1 (inclusive) or begin with the next nakshatra (exclusive).

## Live repository baseline

At start, `research/nightly-project-work` was three commits ahead of the older expected baseline `ed76e49b08968c59a15de92d66602cd5fbc640f8`, with the 2026-10-06 exact-speed/stationary packet, status JSON and nightly-index update already present.

The existing TD2R source-closure document records Latta as a separate 27-star event family, excluding Abhijit, with offsets:

- forward: Sun 12, Mars 3, Jupiter 6, Saturn 8;
- backward: Mercury 7, Venus 5, Rahu 9, Ketu 9, Full Moon 22.

It retained counting origin as unresolved.

## Controlling witness

Pt. Mithalal Vyas, *Sarvatobhadra Chakra* with *Trailokya Dipika*, Tej Kumar Book Depot, Lucknow, 1972.

Repository source ID: `TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN`.

Direct page images inspected:

- scan p.74 / printed p.58: beginning of Graha-Latta section, v.261;
- scan p.75 / printed p.59: vv.261–266, including Hindi commentary and explicit Abhijit exclusion;
- scan p.76 / printed p.60: vv.266–271;
- scan p.77 / printed p.61: vv.271–275 and transition to next section.

## Root and commentary

### Verse 261 — forward Latta

The Sanskrit begins:

`dvādaśaṃ ca tṛtīyaṃ ca ṣaṣṭhaṃ cāṣṭamakaṃ kramāt /`
`lattayanti purodhiṣṇyaṃ ravibhaumāryasūryajāḥ // 261 //`

Bounded sense: Sun, Mars, Jupiter and Saturn respectively strike the 12th, 3rd, 6th and 8th nakshatras in front.

The Hindi commentary says that among the 27 nakshatras from Ashvini through Revati, **from the nakshatra on which the planet is situated** (`jis nakṣatra par graha ho us nakṣatra se`), Sun strikes the 12th ahead, Mars the 3rd, Jupiter the 6th and Saturn the 8th.

### Verse 262 — rear Latta

The Sanskrit gives the rear ordinals:

`saptame pañcame dhiṣṇye navame pṛṣṭhataḥ kramāt /`
... and the Full Moon at the 22nd.

The Hindi commentary again says **from its present nakshatra position** (`apne vartamān nakṣatra sthān se`) count behind to Mercury's 7th, Venus's 5th, Rahu/Ketu's 9th and Full Moon's 22nd.

It then explicitly says Abhijit is not to be counted.

Thus the source closes:

`LATTA_DOMAIN = 27_STARS_ASHVINI_TO_REVATI_EXCLUDING_ABHIJIT`

and supplies direction + ordinal.

## Does Trailokya itself explicitly say inclusive/exclusive?

The 1972 wording says “from the nakshatra occupied by the planet” and “from its present nakshatra position,” but vv.261–275 contain no worked named-star example such as “Sun in Krittika -> Chitra.”

Accordingly, the passage alone does not spell out in algorithmic language whether the occupied star is ordinal 1 or whether counting starts after it.

However, the ordinary ordinal reading can be tested against independent Latta tradition.

## Independent classical/near-classical corroboration

### Phaladipika / Sarvatobhadra appendix tradition

An older published English treatment hosted in the IGNCA scan explicitly gives worked Latta examples:

- Sun in Mula -> its 12th Latta star is Krittika.
- Venus in Shravana -> its rear 5th Latta star is Jyeshtha.

Both are decisive for counting origin on the same 27-star Latta cycle.

#### Sun example

Counting **inclusively**, excluding Abhijit:

1 Mula
2 Purva Ashadha
3 Uttara Ashadha
4 Shravana
5 Dhanishtha
6 Shatabhisha
7 Purva Bhadrapada
8 Uttara Bhadrapada
9 Revati
10 Ashvini
11 Bharani
12 Krittika

This reproduces the printed worked example.

Exclusive counting would land on Rohini and therefore fails.

#### Venus example

Rearward from Shravana, inclusively:

1 Shravana
2 Uttara Ashadha
3 Purva Ashadha
4 Mula
5 Jyeshtha

This also reproduces the printed worked example.

Exclusive counting would land on Anuradha and therefore fails.

These two examples independently test both directions and agree on the same convention.

### Later SBC worked example

A later SBC exposition gives another explicit example:

Sun in Krittika -> 12th from Krittika = Chitra.

On the 27-star cycle, inclusive counting gives:

Krittika(1), Rohini(2), Mrigashira(3), Ardra(4), Punarvasu(5), Pushya(6), Ashlesha(7), Magha(8), Purva Phalguni(9), Uttara Phalguni(10), Hasta(11), Chitra(12).

Exclusive counting would give Swati.

This independently agrees with the older worked examples.

## Adjudication

The controlling Trailokya passage supplies the same ordinal/directional Latta rule and explicitly fixes the 27-star domain. Its prose starts the reckoning “from the nakshatra occupied by the planet.” Although it lacks its own named-star worked example, two-direction worked examples in the independent Latta/SBC tradition remove the practical ordinal ambiguity.

Therefore the best bounded source-mechanics conclusion is:

`TRAILOKYA_LATTA_COUNTING_ORIGIN = INCLUSIVE_OCCUPIED_STAR_IS_1_HIGH_CONFIDENCE`

with an important provenance qualifier:

`TRAILOKYA_1972_TEXTUAL_RULE = SOURCE_CLOSED`

`INCLUSIVE_ORIGIN = TRAILOKYA_WORDING_PLUS_INDEPENDENT_WORKED_TRADITION_CORROBORATED`

This is stronger than an engineering convention, but should still receive human review before any source-contract mutation because the decisive named-star fixtures are external corroborating witnesses rather than a worked example printed in vv.261–275 themselves.

## Executable research-profile formula

For a 0-based index over the 27-star cycle Ashvini..Revati, Abhijit excluded:

Forward Latta with ordinal N, inclusive origin:

`target = (planetIndex + (N - 1)) mod 27`

Backward Latta with ordinal N, inclusive origin:

`target = (planetIndex - (N - 1)) mod 27`

These formulas are recorded for research-profile review only. They are not bound to runtime by this pass.

## Cross-check fixtures

- Sun at Krittika, N=12 forward -> Chitra.
- Sun at Mula, N=12 forward -> Krittika.
- Venus at Shravana, N=5 backward -> Jyeshtha.

All three fail under exclusive-origin arithmetic and pass under inclusive-origin arithmetic.

## What remains unknown

1. The 1972 vv.261–275 passage does not itself print a named-star arithmetic fixture.
2. Whether the 2016 same-lineage reprint contains an added worked example was not established in this pass; it is not needed to distinguish the two conventions once independent worked tradition is admitted.
3. Full Moon is explicitly named for the 22nd rear Latta; diminished-Moon Latta remains outside this closure.
4. This finding does not resolve any ordinary Vedha counting, modifier stacking, motion threshold, or stationary-state gap.

## Contract implication

The existing fail-closed Latta counting-origin gap can now be proposed for separate human-reviewed source-contract correction:

`countingOrigin: INCLUSIVE_OCCUPIED_STAR_IS_1`

No contract or runtime file is mutated in this evidence-only run.

## Confidence

HIGH for the classical/SBC Latta counting convention.

Reason: the controlling Trailokya wording begins from the occupied/current star, the domain is explicitly 27 stars excluding Abhijit, and independent worked examples in both forward and backward directions uniquely discriminate inclusive from exclusive counting.

## Overclaim guards

- Do not count Abhijit in Latta.
- Do not treat N as a zero-based displacement; the displacement is N-1.
- Do not transfer this counting-origin result to ordinary Vedha geometry.
- Do not infer diminished-Moon Latta from the Full-Moon rule.
- Do not merge Latta with verse-166 modifier arithmetic.
- Do not convert Latta into market polarity, market magnitude, oscillator amplitude or execution semantics.

`MARKET_DIRECTION = WITHHELD`  
`MARKET_MAGNITUDE = WITHHELD`  
`OSCILLATOR_AMPLITUDE = WITHHELD`  
`executionAllowed = false`

## Proposed status

`RESEARCH_ONLY_CORRECTION_READY_FOR_HUMAN_REVIEW`

for:

`TRAILOKYA_LATTA_COUNTING_ORIGIN = INCLUSIVE_OCCUPIED_STAR_IS_1_HIGH_CONFIDENCE`

## Recommended next target

With modifier precedence, exact-speed/stationary and Latta counting origin now bounded, the next queue item is **remaining transit-to-natal applicability**: identify exactly which Trailokya/SBC event families explicitly operate on natal/janma targets versus day/transit, prashna, war, country/commodity or other scoped targets. Keep application/separation and persistence/duration for later passes.
