# Nightly Research — Drik/Bala Authority and Profile Binding

Date: 2026-10-01
Status: RESEARCH_ONLY
Scope: source/evidence analysis only; no production operator/profile/runtime changes

## Question

What does the currently accessible textual evidence actually authorize for Drik (Dṛk) Bala, and is that evidence strong enough to bind a production polarity/profile operator?

## Why this matters

Drik Bala is the classical aspectual-strength component most likely to be mistaken for a ready-made bullish/bearish polarity operator. Binding it prematurely could silently convert a natal strength computation into a transit-market direction rule. The project therefore needs to distinguish (a) the existence of a classical aspectual-strength calculation, (b) the exact arithmetic and benefic/malefic classification used by that calculation, and (c) any authority for applying it to the project's transit→instrument directional profiles.

## Repository context

This packet is evidence-building only. It does not authorize F4-B/F4-C, polarity admission, scoring, Candidate C, EMP3, provider/outcome access, MT5, Auto Suggest, ML, or execution. Existing locks remain unchanged.

## Sources checked

| Source | Identifier / location | Role | Finding |
|---|---|---|---|
| Bṛhat Parāśara Horāśāstra, Spasṭabala chapter | Ch. 27, v.19; Sanskrit witnessed at SanskritDocuments and Sanskrit Wikisource | primary-text witness | Verse explicitly speaks of reducing by a quarter under pāpa-dṛk and adding a quarter under śubha-dṛk, then mentions jña (Mercury) and ijya (Jupiter) aspects in the total. |
| Bṛhat Parāśara Horāśāstra, graha-dṛṣṭi chapter | Ch. 26, vv.3–5 in the Santhanam-derived online witness | primary-text/translation witness | Ordinary aspect strengths increase in quarter steps for specified places; all planets fully aspect the seventh; Saturn/Jupiter/Mars have special aspects. The chapter says finer longitude-based calculation is required. |
| Siva.sh BPHS | Ch. 27 v.19 | secondary digital edition/translation | Translation reads: reduce one fourth for malefic aspects, add one fourth for benefic, and “super add” the entire aspect of Mercury and Jupiter. This wording is stronger than the Sanskrit-learning translation below and therefore creates a translation/interpretation issue. |
| EnjoyLearningSanskrit BPHS | Ch. 27 v.19 | Sanskrit morphology + independent English rendering | Renders the final clause more conservatively: total strength is calculated “incorporating the aspects of Mercury and Jupiter,” not explicitly “super add the entire” aspect. |
| VedicPupil BPHS | Ch. 27 chapter index | independent digital chapter witness | Confirms v.19 text/transliteration placement in Spasṭabala chapter but does not supply an explanatory translation. |

## Source-supported findings

1. **Classical authority exists for an aspect-conditioned bala calculation.** BPHS 27.19 contains the Sanskrit `pāpa-dṛk-pāda-hīnam ... śubha-dṛk-pāda-yuk`, directly supporting subtraction of a quarter in connection with malefic aspect and addition of a quarter in connection with benefic aspect.

2. **The verse belongs to a planetary-strength context, not a market-direction context.** The surrounding chapter computes planetary strengths (bala), and v.19 concludes with `kheṭa-balaṃ bhavet` — planetary strength. Nothing in the checked passage establishes bullish/bearish instrument direction.

3. **Graha-dṛṣṭi magnitude is not merely a binary aspect flag.** The checked aspect chapter gives quarter/half/three-quarter/full ordinary aspect gradation and special full aspects, while also pointing to finer longitude-dependent computation. Therefore a profile that collapses the source to simple aspect-present/aspect-absent would need separate justification.

4. **Mercury/Jupiter handling is not yet translation-stable enough for a production binding.** One English witness says to “super add the entire Drishti of Budh and Guru”; another translates the same Sanskrit as merely “incorporating the aspects of Mercury and Jupiter.” The Sanskrit compound `jñejyadṛkyuktam` clearly names Mercury/Jupiter aspects, but this overnight pass did not establish from a critical commentary whether it commands an additional full-value add, identifies benefic aspects, or has another technical reading.

5. **This evidence does not resolve conditional Mercury/Moon benefic-malefic status.** Verse 27.19 uses the categories pāpa and śubha but does not, by itself, define all contextual membership rules. Those rules must be sourced independently before a polarity-like profile is frozen.

## Translation / edition discrepancy

The material discrepancy is the final half of v.19:

`bal-aikyaṃ jñejya-dṛk-yuktam evaṃ kheṭa-balaṃ bhavet`

Two accessible translations differ operationally:

- Santhanam-derived wording exposed by Siva.sh: “Super add the entire Drishti of Budh and Guru...”
- EnjoyLearningSanskrit: total strength is calculated while “incorporating the aspects of Mercury and Jupiter.”

Those are not equivalent implementation instructions. Until a reliable commentary/edition explains the intended arithmetic, **do not encode an extra Mercury/Jupiter full-aspect term solely from the stronger English wording**.

## What is NOT established

- No checked source authorizes mapping positive Drik Bala to bullish and negative Drik Bala to bearish instrument direction.
- No checked source authorizes applying natal Shadbala/Drik Bala unchanged to a transit→natal or transit→market operator.
- No checked source resolves the exact Mercury/Jupiter clause strongly enough for code-level arithmetic binding.
- No checked source resolves conditional Moon/Mercury benefic-malefic classification for this operator.
- No checked source establishes stacking/precedence when Drik Bala conflicts with other directional doctrines.
- No checked source establishes persistence/duration after exact aspect or application/separation weighting.
- Rahu/Ketu inclusion in this exact Shadbala computation is not established by the checked v.19 evidence and must not be inferred from modern calculators.

## Implications for operator/profile binding

**Do not bind Drik Bala as a production directional profile yet.** A safe future design should keep at least three concepts separate:

1. `aspect_geometry` — source-certified aspect magnitude/geometry;
2. `drik_bala_strength` — a planetary-strength calculation only after arithmetic/classification is source-closed;
3. `market_direction` — remains withheld unless separately authorized by instrument-chart doctrine/evidence.

This is compatible with the project's existing rule that aspect geometry itself is not bullish/bearish.

## Proposed disposition

`RESEARCH_ONLY`

Reason: the primary text supports the existence and broad sign of benefic/malefic aspect contributions to planetary strength, but the Mercury/Jupiter arithmetic clause and contextual benefic/malefic classification are not source-closed, and no authority was found for transit-market directional binding.

## Recommended next evidence target

Highest-value next step: obtain/compare a printed or scan-based commentary/translation for BPHS 27.19 (especially the `jñejyadṛkyuktam` clause), then separately source the natural/conditional benefic-malefic rules for Moon and Mercury. Only after those two are closed should a machine-readable Drik Bala profile be proposed for human review.

## Guards against overclaiming

- Treat `RESEARCH_ONLY` as non-executable evidence.
- Do not infer market direction from bala sign.
- Do not promote online calculator conventions to classical authority.
- Do not choose among translations using market outcomes.
- Preserve UNKNOWN where the source does not define an operator.

## Bibliography / source URLs checked on 2026-10-01

- SanskritDocuments, BPHS 21–30: https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par2130.html
- Sanskrit Wikisource, BPHS ch.27: https://sa.wikisource.org/wiki/बृहत्पाराशरहोराशास्त्रम्/अध्यायः_२७_(स्पष्टबलाध्यायः)
- Siva.sh, BPHS 27.19: https://www.siva.sh/brihat-parashara-hora-shastra/27/19
- Siva.sh, BPHS ch.26: https://www.siva.sh/brihat-parashara-hora-shastra/26/
- EnjoyLearningSanskrit, BPHS ch.27: https://enjoylearningsanskrit.com/scriptures/parashara/chapter-27/
- VedicPupil, BPHS ch.27: https://vedicpupil.in/library/books/brihat-parashara-hora-shastra/chapter-27
