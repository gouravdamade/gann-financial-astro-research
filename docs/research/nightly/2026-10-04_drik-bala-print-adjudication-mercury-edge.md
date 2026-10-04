# Nightly Research — Drik Bala Direct-Print Adjudication and Conditional-Mercury Edge

Date: 2026-10-04  
Status: RESEARCH_ONLY  
Scope: evidence/profile refinement only; no production operator, evidence registry, scoring, polarity, provider/outcome, MT5, Candidate C, EMP3, or execution changes

## Why this successor packet exists

The earlier 2026-10-04 access-pass packet correctly recorded that the nightly web reader could not reach the Internet Archive delivery hosts. Later the same day, the relevant printed scans were supplied manually in the research session and could be inspected directly. This packet **supersedes the access blocker only for the pages actually inspected**. It does not erase the earlier access-pass audit trail.

Start-of-packet branch tip: `57d293d180b6af8425ef4e278a0647a6f0b2cc3a`.

## Direct printed-witness adjudication now available

### Ganesh Datt Pathak

Directly inspected from the manually supplied scan:

- printed p.614 / PDF p.622: full graha-to-graha dṛṣṭi matrix with `śubha-yoga` and `pāpa-yoga` totals;
- printed p.615 / PDF p.623: resulting Drig-bala table and worked dṛṣṭi arithmetic;
- printed p.626 / PDF p.634: planetary ṣaḍbala rule;
- printed p.627 / PDF p.635: continuation into Bhāva Bala.

Pathak's planetary rule is the ordinary signed quarter operator. The p.614 matrix itself places Mercury/Jupiter dṛṣṭi inside the ordinary benefic aggregate. No separate planetary `jña/ijya` extra is printed in the p.626 rule.

A clean internal check is the Moon column of Pathak's p.614 matrix:

- Mercury dṛṣṭi = 0°06′26″;
- Jupiter dṛṣṭi = 0°10′10″;
- printed `śubha-yoga` = 0°16′36″ = Mercury + Jupiter;
- printed `pāpa-yoga` = 0°50′00″.

Therefore the Pathak operator gives

```
ordinary Drik term
= 1/4 * (16′36″ - 50′00″)
= -8′21″
```

with no additional Mercury/Jupiter planetary term.

**Disposition:** `PATHAK_NET_QUARTER_RESEARCH = DIRECT_PRINT_AND_NUMERICALLY_VERIFIED`.

### Padmanabh Sharma, Bhāvabodhinī

Directly inspected:

- printed p.130 / PDF p.156: planetary Drig-bala verse 19 contains `jñejyadṛgyuktam`; prose explicitly gives ordinary +1/4 benefic / -1/4 malefic treatment;
- printed p.132 / PDF p.158: parallel Bhāva-Bala commentary says Mercury/Jupiter dṛṣṭi is to be added `sampūrṇa` (whole/complete);
- the following rule separately assigns one full unit (60 kalā) for Mercury/Jupiter **occupation/conjunction**, demonstrating that whole computed dṛṣṭi is not the same thing as an automatic +60 aspect.

No planetary numerical worked example was found that resolves whether Mercury/Jupiter are inside the ordinary aggregate and then added whole, or excluded before the quartering.

### Devachandra Jha, Sudhā

Directly inspected from the manually supplied scan:

- the strength chapter is numbered 28 in this recension;
- printed p.158 contains the corresponding planetary rule and Hindi commentary;
- the commentary operationally sequences the calculation as: ordinary benefic-aspect quarter addition, ordinary malefic-aspect quarter subtraction, **then add Mercury/Jupiter dṛṣṭi**;
- the nearby Bhāva rule repeats the special Mercury/Jupiter addition;
- the distinct fixed-one-unit occupation rule remains separate.

This is direct printed evidence for a special post-ordinary term, but the Jha page does not provide a planetary numerical worked example resolving the ordinary-pool membership/double-count question.

### Suresh Chandra Mishra

The printed Mishra tradition retains the planetary `jñejya` clause and explicitly interprets the parallel Bhāva rule as whole Mercury/Jupiter dṛṣṭi. A worked Bhāva example examined in this research sequence is especially important: Mercury participates in the ordinary `śubha` aspect aggregate and its full computed dṛṣṭi is then added again.

That worked arithmetic directly verifies the **A1 structure for Mishra's Bhāva calculation**:

```
1/4 * (ordinary benefic aggregate - ordinary malefic aggregate)
+ full computed Mercury/Jupiter dṛṣṭi
```

It is strong parallel evidence for the planetary `jñejya` clause, but it is not a planetary worked example. The planetary step must therefore remain explicitly profile-qualified.

## Conditional Mercury: separate nature from special arithmetic

BPHS 3.11 makes Mercury condition-dependent: Mercury becomes krūra/pāpa when joined with a malefic. This nature/classification input must remain separate from the later Drik-Bala arithmetic.

B. V. Raman supplies a direct worked planetary precedent for conditional Mercury:

- Drishti Pinda is the signed sum of benefic and malefic aspect values;
- planetary Drik Bala is one quarter of that signed Drishti Pinda;
- in Raman's standard horoscope Mercury is placed on the malefic side because it is very closely associated with the Sun / combust;
- Raman does **not** apply a separate planetary Mercury extra.

Raman also explicitly states in the Bhāva-Bala procedure that, even though Mercury may have been classified benefic or malefic by association earlier, Mercury is treated as a full benefic for Bhāva Drishti Bala. This is a historical computational precedent for a special-rule override that is distinct from ordinary nature classification.

The Subrahmanya Sastri commentary on Śrīpati Paddhati records a different convention: although some treat Mercury as malefic when associated with a malefic, that Śrīpati commentary treats Mercury as always benefic. Therefore the previously combined research label `SRIPATI_RAMAN_JAIN_NET_QUARTER_RESEARCH` is too coarse.

## Deeper edge-case pass — later 2026-10-04

### Mishra's planetary example is real but non-discriminating

The Suresh Chandra Mishra text does contain a planetary worked continuation immediately after verse 36. He states that the five pre-Drik strengths total `6.29.22`, then says the Drik adjustment leaves the planet at roughly 6 because pāpa dṛṣṭi predominates. However, he does **not** numerically show a separate Mercury/Jupiter planetary extra in that calculation.

This is useful negative/limiting evidence, not proof that the extra is absent: in Mishra's example the target is the Moon/lagneśa, the prose identifies Mars/Saturn, Sun/Mercury and Venus as the relevant aspectors, and Jupiter does not contribute a material dṛṣṭi to that target. Mercury's contribution is small enough that either ordinary-quarter-only or quarter-plus-full would still round descriptively to "about 6." Therefore this worked passage cannot adjudicate planetary A1.

### Mishra's Bhāva example proves a stronger override than previously recorded

The same worked Bhāva example gives Sun at 9.11.15 and Mercury at 9.15.53 — only about 4°38′ apart in the same sign. Despite that close solar association, Mishra puts Mercury's 31.46 dṛṣṭi in the **śubha** aggregate with Venus, quarters the ordinary śubha/pāpa difference, and then adds Mercury's full dṛṣṭi again.

So for **Mishra Bhāva Bala**, the special Mercury rule is not merely whole-vs-quarter; it demonstrably overrides the ordinary expectation that close association with a malefic/Sun might make Mercury pāpa. This strengthens the architectural separation:

```text
ordinary planetary Mercury nature classifier
!=
Bhāva special Mercury override
```

It still does **not** prove that the planetary `jñejya` clause applies the same override.

### Jain's mixed-association example narrows the nature-classifier problem

Jain explicitly defines planetary Drik Bala using well-associated Mercury as śubha and badly-associated Mercury as aśubha. His standard worked horoscope then classifies Mercury as śubha despite simultaneous close Saturn and Jupiter association. This directly closes Jain's high-level Mercury convention, but leaves the **general mixed-association precedence rule** unresolved.

## Extended computational-tradition pass — same-day continuation

The search was extended specifically for a **planetary worked example that numerically exposes the `jñejya` Mercury/Jupiter special term**. No decisive Jha/Padmanabh/Mishra planetary A1 worked calculation was found. However, three additional witnesses materially sharpen the profile split.

### Keśavīya Jātaka Paddhati: worked planetary net-quarter, Bhāva full-M/J

A detailed Sanskrit/Hindi computational edition of *Keśavīya Jātaka Paddhati* explicitly states the planetary Drig rule in aggregate form:

```text
+ 1/4 * śubha-dṛṣṭi-yoga
- 1/4 * pāpa-dṛṣṭi-yoga
```

and then prints the individual Drig-bala contributions inside a complete seven-planet ṣaḍbala worked table. No separate whole Mercury/Jupiter planetary term is introduced in that worked planetary computation.

The same work later gives the Bhāva rule separately:

```text
+ 1/4 * benefic aspect aggregate
- 1/4 * malefic aspect aggregate
+ whole Mercury/Jupiter dṛṣṭi on the Bhāva
```

This is another direct computational witness for the same structural distinction already visible in Śrīpati/Raman/Jain:

```text
PLANETARY DRIK  = quarter-net only
BHĀVA DRIK      = quarter ordinary + whole M/J
```

Disposition:

`KESHAVIYA_NET_QUARTER_RESEARCH = DIRECT_TEXT_AND_WORKED_PLANETARY_TABLE`

`KESHAVIYA_BHAVA_FULL_MJ = EXPLICIT`

#### Keśavīya Mercury association edge

The text explicitly says Mercury becomes śubha in association (`yoga`) with a benefic and pāpa in association with a malefic. In its worked chart Mercury and Saturn are in the same sign and only about 1°52′ apart, while Jupiter gives Mercury a strong dṛṣṭi. The printed planetary Drig arithmetic for the Moon is consistent with Mercury being placed on the śubha side in that example.

This is evidence for **one mixed-association outcome**, not for a general precedence algorithm. In particular, do **not** infer or code any rule such as “closest association wins,” “Jupiter overrides Saturn,” or “aspect overrides conjunction.” The exact semantics of `yoga` and the mixed-association tie-break remain unresolved.

### Śrīpati Paddhati: exact worked planetary table confirms the separation

The V. Subrahmanya Sastri edition/commentary of *Śrīpati Paddhati* explicitly states:

- planetary ṣaḍbala: add one quarter of benefic aspect and subtract one quarter of malefic aspect;
- Bhāva bala: separately superadd the **entire** aspect of Jupiter and Mercury.

The edition also prints a complete planetary ṣaḍbala table with separate `Subhadrishti` and `Papadrishti` rows before the final total. This upgrades the Śrīpati profile from merely commentarial/formula evidence to a **worked computational planetary witness**.

Disposition:

`SRIPATI_SASTRI_NET_QUARTER_RESEARCH = DIRECT_FORMULA_PLUS_WORKED_PLANETARY_TABLE`

The same commentary explicitly records the author/commentator's Mercury convention as always benefic, while acknowledging that some authorities treat Mercury as malefic when associated with malefics. That convention remains profile-local and must not be projected into Raman, Jain, BPHS, or Keśavīya.

### Phaladīpikā index clue: `JNEJYA DRIGBALA` points to a Lagna/Bhāva context

V. Subrahmanya Sastri's *Phaladīpikā* index contains the entry:

`JNEJYA DRIGBALA — IV-6`

Chapter IV verse 6 is a **Lagna-strength / house-strength context**, including strengthening by the lord, Jupiter or Mercury. This does not resolve BPHS 27.19 and does not prove that the planetary `jñejya` clause is secondary. It is nevertheless a useful terminological clue: in this translation/index tradition, the named `JNEJYA DRIGBALA` concept is indexed to a Bhāva/Lagna-strength passage rather than to a separate planetary double-add worked rule.

Status:

`PHALADEEPIKA_JNEJYA_INDEX_CONTEXT = BHAVA_LAGNA_CLUE_ONLY`

### Secondary implementation audit

Modern teaching/software sources remain internally divergent and are not promoted to doctrine:

- some repeat the Santhanam-family “super add the entire Mercury/Jupiter dṛṣṭi” wording;
- some computational examples use already quarter-scaled aspect magnitudes, so “full” there does not establish a second raw whole-aspect addition;
- some modern implementations explicitly implement A1 as quarter ordinary net plus whole Mercury/Jupiter;
- other teaching material reads more like A2 (Mercury/Jupiter taken whole instead of quarter).

This divergence strengthens the need for named source profiles rather than resolving the primary-text issue.

### Consequence of the extended pass

The evidence now supports **two durable computational families** more strongly than before:

#### Planetary net-quarter family — directly worked

- Ganesh Datt Pathak;
- Śrīpati Paddhati / Subrahmanya Sastri;
- B. V. Raman;
- V. P. Jain;
- Keśavīya Jātaka Paddhati.

Core planetary operator:

```text
drik_bala = 1/4 * (Σ śubha computed dṛṣṭi - Σ pāpa computed dṛṣṭi)
```

No separate whole Mercury/Jupiter planetary term is used in these worked planetary computations. Several of these same traditions explicitly use whole Mercury/Jupiter dṛṣṭi in **Bhāva** strength instead.

#### BPHS `jñejya` literal/commentarial family — textually strong, planetary worked proof still missing

- Devachandra Jha: quarter ordinary aggregate, then add M/J dṛṣṭi;
- Padmanabh Sharma: planetary verse retains `jñejya`; Bhāva parallel says `sampūrṇa`;
- Suresh Chandra Mishra: planetary verse retains `jñejya`; Bhāva worked arithmetic verifies ordinary-quarter + whole Mercury;
- Santhanam-family rendering: “super add” whole Mercury/Jupiter dṛṣṭi.

What is still missing is the decisive item: **a planetary worked numeric example from this family where a material Mercury/Jupiter dṛṣṭi is visibly carried through the final bala and distinguishes A1 from A2/net-quarter**.

This makes a forced single “canonical BPHS Drik Bala operator” scientifically less defensible. The likely clean endpoint is a source-profiled operator family with provenance-visible components and no synthesis by market outcomes.

## Research profile split

The old combined label is **deprecated for research use**. Do not delete historical packets; interpret them through the successor split below.

### `PATHAK_NET_QUARTER_RESEARCH`

```json
{
  "ordinarySignedDrishti": "sum(+computedDrishti for BENEFIC, -computedDrishti for MALEFIC)",
  "drikBalaStrength": "0.25 * ordinarySignedDrishti",
  "planetaryMercuryJupiterExtra": 0,
  "verification": "DIRECT_PRINT_AND_WORKED_NUMERIC",
  "marketDirection": "WITHHELD"
}
```

### `RAMAN_NET_QUARTER_RESEARCH`

```json
{
  "ordinarySignedDrishti": "sum(+computedDrishti for BENEFIC, -computedDrishti for MALEFIC)",
  "mercuryNature": "CONDITIONAL_BY_ASSOCIATION; worked example places closely-Sun-associated/combust Mercury on MALEFIC side",
  "drikBalaStrength": "0.25 * ordinarySignedDrishti",
  "planetaryMercuryJupiterExtra": 0,
  "verification": "DIRECT_WORKED_COMPUTATIONAL_WITNESS",
  "marketDirection": "WITHHELD"
}
```

### `SRIPATI_SASTRI_NET_QUARTER_RESEARCH`

```json
{
  "ordinarySignedDrishti": "quarter-net computational family",
  "mercuryNature": "ALWAYS_BENEFIC in the cited Subrahmanya Sastri commentary convention",
  "planetaryMercuryJupiterExtra": 0,
  "verification": "COMMENTARIAL_COMPUTATIONAL_PROFILE",
  "marketDirection": "WITHHELD"
}
```

### `JAIN_NET_QUARTER_RESEARCH`

V. P. Jain is now directly sourced rather than left UNKNOWN:

```json
{
  "ordinarySignedDrishti": "sum(+computedDrishti for SHUBHA, -computedDrishti for ASHUBHA)",
  "mercuryNature": "CONDITIONAL_BY_ASSOCIATION: well-associated Mercury = SHUBHA; badly-associated Mercury = ASHUBHA",
  "drikBalaStrength": "0.25 * drishtiPinda",
  "planetaryMercuryJupiterExtra": 0,
  "bhavaOverride": "Mercury ALWAYS_BENEFIC irrespective of association; Mercury/Jupiter dṛṣṭi taken FULL",
  "exactAssociationTrigger": "UNRESOLVED",
  "mixedAssociationGeneralRule": "UNRESOLVED",
  "verification": "DIRECT_TEXT_PLUS_STANDARD_HOROSCOPE_WORKED_TABLE",
  "marketDirection": "WITHHELD"
}
```

Jain's standard horoscope creates a useful mixed-association test. Mercury is at 170.53°, Jupiter at 170.45°, and Saturn at 166.43°: Mercury is simultaneously in extremely close conjunction with benefic Jupiter (~0.08°) and same-sign/close to malefic Saturn (~4.10°). In Jain's planetary Drik table the positive total for the Moon is 78.75. It decomposes exactly as Mercury 11.03 + Jupiter 40.95 + Venus 26.77 = 78.75, proving that Jain classifies Mercury as **SHUBHA in this mixed-association example**. The text does not state the general tie-break rule. The extreme closeness of Jupiter is a plausible explanation, but "closest association wins" is **NOT SOURCE-ESTABLISHED** and must not be coded.

### `BPHS_JNEJYA_A1_RESEARCH`

Preserve the ordinary Mercury term and special `jñejya` term as **two visible provenance-bearing components**:

```text
ordinary_mercury_drik_component
    = mercury_nature_sign * computed_drishti(Mercury) / 4

jnejya_mercury_special_component
    = + computed_drishti(Mercury)

candidate_combined_mercury_component
    = ordinary_mercury_drik_component
      + jnejya_mercury_special_component
```

For ordinary benefic Mercury this candidate yields:

```
+M/4 + M = +1.25M
```

For conditionally malefic Mercury this candidate yields:

```
-M/4 + M = +0.75M
```

The **+0.75M case is not direct planetary worked-example verified**. Keep its evidence state as `INFERRED_NOT_WORKED_VERIFIED`; do not collapse the two components into a hard-coded coefficient.

The same provenance discipline applies to Jupiter: ordinary benefic quarter component and any `ijya` special whole computed-dṛṣṭi component must remain separately visible until direct planetary worked arithmetic confirms the combined treatment.

## What is now closed strongly enough for research

- ordinary benefic/malefic aspects accumulate; no precedence/dominance rule found;
- ordinary quarter treatment is supported;
- Pathak's planetary profile is a direct-print, worked numerical net-quarter profile;
- Mercury/Jupiter are inside Pathak's ordinary aggregate;
- Pathak has no separate planetary Mercury/Jupiter extra in the inspected rule;
- Padmanabh/Jha/Mishra belong to a distinct `jñejya` textual/computational family;
- whole computed Mercury/Jupiter dṛṣṭi is strongly supported in the Bhāva parallel of that family;
- fixed Mercury/Jupiter `+60` for aspect is unsupported;
- Raman directly demonstrates conditionally-malefic Mercury in planetary Drik Bala;
- Śrīpati-Sastri and Raman must not share one Mercury-nature profile;
- Jain is now directly verified as conditional-by-association for planetary Drik Bala, with an explicit always-benefic Mercury override for Bhāva Drishti Bala;
- Jain's standard worked chart proves a mixed Jupiter/Saturn association can still resolve Mercury as śubha, but the general mixed-association tie-break rule remains UNKNOWN;
- Keśavīya supplies another direct worked planetary net-quarter tradition and separately gives whole Mercury/Jupiter treatment only for Bhāva strength;
- Śrīpati-Sastri now has an explicitly checked worked planetary ṣaḍbala table supporting the net-quarter planetary profile;
- the Phaladīpikā index's `JNEJYA DRIGBALA IV-6` entry points to a Lagna/Bhāva-strength context and is retained only as a terminological clue;
- Mishra's worked Bhāva example treats a Mercury only ~4°38′ from the Sun as śubha and then adds its whole dṛṣṭi, directly strengthening the Bhāva override;
- market bullish/bearish direction remains unauthorized.

## What remains unresolved

1. **Planetary A1 worked arithmetic:** despite the broader search, no discriminating Jha/Padmanabh/Mishra planetary example has surfaced. Continue only with primary/near-primary worked tables where a material Mercury/Jupiter aspect is numerically visible.
2. **Malefic-Mercury + jñejya edge:** directly verify whether a conditionally-malefic Mercury contributes `-M/4` in the ordinary pool and then still receives `+M` as the special `jña` term. Current `+0.75M` is the best-supported inference, not direct worked proof.
3. **Exact Mercury nature trigger per profile:** distinguish BPHS's conjunction/association rule from Raman's close-Sun/combust treatment and from broader modern rules based merely on malefic aspect. Do not merge them.
4. **Jupiter double-participation:** obtain direct planetary worked arithmetic confirming whether Jupiter is quarter-counted in the ordinary benefic aggregate and then added whole in the `ijya` family.
5. **Mixed-association Mercury precedence:** Jain's worked chart proves one mixed case resolves SHUBHA (very close Jupiter plus close Saturn), but no general rule has been sourced for multiple simultaneous benefic/malefic associations.
6. **Repository evidence archival:** the manually supplied scan pages were inspected outside the repository; preserve page references/transcriptions and, if desired later, add permitted evidence snapshots or hashes without bloating the repo with entire books.
7. **Canonical policy:** there may be no single universal Drik-Bala operator. The scientifically cleaner endpoint may be multiple named source profiles with explicit provenance rather than forcing one synthesis.
8. **Conditional Moon boundary:** after Mercury is exhausted, the exact waxing/waning nature boundary remains a separate source-profile question before a fully classical nature classifier is safe to bind.
9. **Next lower-priority doctrine:** only after the above should the nightly queue advance to the Sārāvalī fraction/translation discrepancy.

## Binding / implementation guard

No production binding is authorized by this packet. If a research implementation is later created, it must expose:

```text
computed_drishti_magnitude
nature_classification
ordinary_signed_quarter_component
jnejya_special_component
final_profile_qualified_drik_bala
```

as distinct traceable stages. No market-direction sign may be derived from Drik Bala.

## External computational witnesses checked in this research pass

- B. V. Raman, *Graha and Bhava Balas*: planetary Drishti Pinda/Drik Bala, conditional Mercury worked example, and Bhāva Mercury full-benefic special treatment.
- V. Subrahmanya Sastri, *Sripati Paddhati*: commentary records the always-benefic Mercury convention despite acknowledging another association-dependent convention.
- V. P. Jain, *Text Book for Shadbala (Grahas) and Bhavabala*: planetary Drik uses well-associated Mercury as śubha and badly-associated Mercury as aśubha; Bhāva Drishti explicitly overrides Mercury to always benefic and takes Mercury/Jupiter dṛṣṭi full. Jain's standard worked table supplies a mixed Jupiter/Saturn association case classified śubha.
- *Keśavīya Jātaka Paddhati*, Chandrama Pandey-edited Sanskrit/Hindi computational edition: planetary quarter-net formula plus worked ṣaḍbala table; Bhāva rule separately adds whole Mercury/Jupiter dṛṣṭi.
- *Phaladīpikā*, V. Subrahmanya Sastri edition/index: `JNEJYA DRIGBALA IV-6` points to a Lagna/Bhāva-strength context; clue only, not planetary arithmetic proof.
- Printed BPHS witnesses: Ganesh Datt Pathak, Padmanabh Sharma, Devachandra Jha, Suresh Chandra Mishra.

## Guards against overclaiming

- Do not claim the `+0.75M` malefic-Mercury result is direct planetary worked evidence.
- Do not treat Mishra's Bhāva worked arithmetic as if it were a planetary worked example.
- Do not merge Raman and Śrīpati-Sastri Mercury semantics.
- Do not turn whole computed dṛṣṭi into a fixed 60.
- Do not use functional lordship or market outcomes to assign Drik-Bala sign.
- Keep `marketDirection=WITHHELD`.
