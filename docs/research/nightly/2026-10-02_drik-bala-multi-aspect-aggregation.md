# Nightly Research — Drik Bala Multi-Aspect Aggregation / Stacking / Precedence

Date: 2026-10-02
Status: RESEARCH_ONLY
Scope: evidence/profile proposal only; no production operator, scoring, polarity, source-profile, runtime, provider, outcome, MT5, Candidate C, EMP3, or execution changes

## Question

How are multiple simultaneous benefic and malefic graha-dṛṣṭis aggregated for Drik Bala, where does the quarter factor apply, is there any precedence rule, and how should the Mercury/Jupiter clause in BPHS 27.19 be distinguished from ordinary aspect magnitude and from the special geometrical aspects of Mars/Jupiter/Saturn?

## Why this matters

The arithmetic changes materially depending on whether the source intends (a) quartering each signed aspect, (b) quartering a net aggregate, (c) separately quartering benefic and malefic aggregates, or (d) adding Mercury/Jupiter again at full computed aspect magnitude. These alternatives must not be collapsed into one production operator without source/recension provenance.

## Repository context

The prior packet `2026-10-01_drik-bala-authority-profile-binding.md` established only that BPHS 27.19 authorizes an aspect-conditioned planetary-strength calculation and does not authorize market direction. This packet targets the arithmetic ambiguity. The live repository remains locked against production doctrine changes.

## Sources checked

| Source | Bibliographic / exact identifier | Evidence type | Finding |
|---|---|---|---|
| BPHS Sanskrit | Spasṭabala chapter, commonly ch.27 v.19; SanskritDocuments, Sanskrit Wikisource, EnjoyLearningSanskrit | primary-text digital witnesses | Stable wording: `pāpadṛkpādahīnaṃ tacchubhadṛkpādayuk tathā / balaikyaṃ jñejyadṛkyuktamevaṃ kheṭabalaṃ bhavet`. It states quarter subtraction/addition for pāpa/śubha dṛṣṭi and names Mercury/Jupiter aspects in the total, but the terse syntax does not itself spell out a loop/order over multiple aspects. |
| Pt. Devachandra Jha, *Bṛhatpārāśara-horāśāstram*, Sudhā Hindi commentary, Chaukhambha Sanskrit Sansthan, Kashi Sanskrit Granthamala 220; scan hosted at Internet Archive | named printed BPHS commentary; OCR from scan | At printed pp.177–178 / OCR lines around the v.19 commentary, Jha says: `बलैक्य में शुभग्रहों के दृष्टियोग के चतुर्थांश को जोड़ने से तथा पाप ग्रहों की दृष्टि के चतुर्थांश को घटने से ... उसमें बुध, गुरु की दृष्टि को जोड़ दें`. This explicitly uses **dṛṣṭi-yoga** (sum/aggregate) for benefics and malefics, then says add Mercury/Jupiter dṛṣṭi. Scan image could not be fetched through the web tool, so exact punctuation/orthography remains scan-unverified; the OCR is nevertheless unusually clear here. |
| R. Santhanam, *Brihat Parasara Hora Sastra*, Ranjan Publications; English text reproduced in accessible digital witnesses | named printed translation/commentary tradition, digital reproduction | v.19 wording: reduce one fourth for malefic dṛṣṭis, add a fourth for benefic, then “Super add the entire Drishti of Budh and Guru”. Supports a post-quarter Mercury/Jupiter add, but does not by itself establish that “entire” means a fixed 60. |
| B. V. Raman, *Graha and Bhava Balas*, 13th ed. preface dated 1992; Ch. VIII, arts. 115–120 | named printed computational witness | Raman explicitly says his general scheme is mainly Śrīpati. He totals all benefic and malefic dṛṣṭi values into a signed Drishti Pinda and defines planetary Drik Bala as one-fourth of that net. His worked table has separate Subhadrishtibala, Asubhadrishtibala, Nett Aspect, then Drik Bala = net/4. No separate full Mercury/Jupiter planetary term appears. |
| V. P. Jain, *Text Book for Shadbala (Grahas) and Bhavabala*, Ch.7/8, accessible text reproduction | named printed computational witness | Planetary Drik Bala: total signed aspect value = Drishti Pinda; Drik Bala = one fourth of Drishti Pinda. In the following **Bhava Bala** chapter Jain separately states Mercury/Jupiter dṛṣṭi are taken full while other planets are quartered. This is strong evidence that at least one computational tradition distinguishes planetary Drik Bala from the Mercury/Jupiter full treatment in Bhava Drishti Bala. |
| BPHS Bhava Bala passage | common ch.27 vv.28–30 | primary-text digital witnesses | The bhava passage again has `saddṛṣṭipādayuk... pāpadṛṣṭipādavivarjitam`, then `jñejyadṛṣṭiyutaṃ`, and a following occupation rule for Mercury/Jupiter vs Saturn/Mars/Sun. Its close verbal parallel to v.19 is relevant to the recension/interpretation problem. |

## Direct Sanskrit evidence

The stable v.19 text is:

`पापदृक्पादहीनं तच्छुभदृक्पादयुक् तथा ।`
`बलैक्यं ज्ञेज्यदृक्युक्तमेवं खेटबलं भवेत् ॥`

A minimal source-safe reading is:

- pāpa dṛṣṭi contributes negatively at a quarter rate;
- śubha dṛṣṭi contributes positively at a quarter rate;
- Mercury/Jupiter dṛṣṭi is mentioned as an additional/associated term in the resulting bala total;
- the result is `kheṭabala`, planetary strength, not market direction.

The Sanskrit alone does not state a precedence/dominance rule and does not state a fixed `+60` for Mercury or Jupiter.

## Strongest aggregation evidence: Devachandra Jha

Jha’s Hindi commentary is the clearest checked witness for **multiple simultaneous aspects**. His wording uses `शुभग्रहों के दृष्टियोग के चतुर्थांश` and `पाप ग्रहों की दृष्टि के चतुर्थांश`, i.e. a quarter of the **sum/aggregate** of benefic aspects is added and a quarter of the malefic-aspect aggregate is subtracted. He then says `बुध, गुरु की दृष्टि को जोड़ दें`.

Therefore, in this witness the semantic operation is aggregate-first:

`ordinary = 1/4 * sum(shubha aspect magnitudes) - 1/4 * sum(papa aspect magnitudes)`

followed by a Mercury/Jupiter dṛṣṭi add.

Because multiplication distributes over addition, quartering each ordinary signed aspect separately would be numerically equivalent in exact arithmetic. But the **textual semantics** in Jha are aggregate-first, not a precedence rule.

## Is there precedence when benefic and malefic aspects coexist?

No checked witness gives a winner-takes-all or dominance/precedence rule for Drik Bala. Jha accumulates both sides; Raman and Jain explicitly show separate positive and negative totals and then net them. Thus simultaneous śubha and pāpa dṛṣṭis coexist arithmetically.

`PRECEDENCE_RULE = NOT_FOUND`

The net may be positive, zero, or negative.

## Mercury/Jupiter clause: what is established and what is not

### Jha/Santhanam BPHS-reading family

Jha says to add Mercury/Jupiter dṛṣṭi after the ordinary quarter additions/subtractions. Santhanam says to “super add the entire Drishti” of Mercury and Jupiter. This supports a **full computed dṛṣṭi magnitude term**, not a fixed constant.

A literal engineering transcription of this witness family would be:

`base = 0.25 * (sum_shubha - sum_papa)`

`extra_jna_ijya = aspect(Mercury) + aspect(Jupiter)`

`drik_bala = base + extra_jna_ijya`

However, this raises a real double-count/provenance question: if Mercury/Jupiter are already members of `sum_shubha`, the literal formula gives them their ordinary quarter contribution plus an additional full dṛṣṭi. Jha/Santhanam wording points that way, but this pass did not verify a critical apparatus or a worked Jha example that demonstrates the double count numerically. Mercury can also become malefic conditionally, which makes the interaction still more sensitive.

### Raman/Jain planetary-Drik computational family

Raman and Jain instead compute planetary Drik Bala as:

`drishti_pinda = sum(all signed aspect magnitudes)`

`drik_bala = 0.25 * drishti_pinda`

with no separate full Mercury/Jupiter term in their planetary worked calculation. Jain then explicitly applies full Mercury/Jupiter dṛṣṭi in **Bhava** Drishti Bala while quartering the other planets there. Raman states that his overall computational scheme is mainly Śrīpati, so this should not be mislabeled as a verbatim resolution of BPHS v.19.

This is a **material computational tradition/recension interpretation difference**, not something to hide by choosing whichever formula is convenient.

## Special geometrical aspects are a different operator

Do not confuse the BPHS v.19 Mercury/Jupiter clause with `viśeṣa dṛṣṭi` geometry. Raman/Jain compute ordinary aspect magnitude first and then add geometrical special-aspect increments for Mars/Jupiter/Saturn where applicable. Jain’s exposition gives +15 for Mars, +30 for Jupiter, +45 for Saturn to bring the relevant special aspect toward/full 60 at the stated anchor. These increments belong inside **computed dṛṣṭi magnitude** before benefic/malefic aggregation.

Thus:

1. `computed_drishti_magnitude` includes ordinary geometry plus any source-defined Mars/Jupiter/Saturn viśeṣa geometry;
2. `benefic_malefic_classification` assigns sign/context;
3. `drik_bala_arithmetic` aggregates signed magnitudes;
4. `jna_ijya_extra` is a separate BPHS-v.19 interpretation question;
5. lunar/Mercury nature profiles remain separate inputs;
6. market direction remains unauthorized.

## Fixed +60 question

No checked witness supports a blanket `+60` merely because the aspecting planet is Mercury or Jupiter.

- Jha says add their `dṛṣṭi`.
- Santhanam says add the “entire Drishti”.
- Aspect magnitude itself is variable with geometry.
- A special aspect can be full (60) in particular geometry, but that is not equivalent to a universal Mercury/Jupiter `+60` rule.

Therefore:

`MERCURY_JUPITER_FIXED_PLUS_60 = NOT_SUPPORTED`

## Recension / edition differences

1. The common Sanskrit digital witnesses preserve the v.19 `jñejyadṛkyuktam` clause.
2. Jha’s printed-commentary OCR interprets it as an additional Mercury/Jupiter dṛṣṭi after quartered śubha/pāpa dṛṣṭi aggregates.
3. Santhanam’s translation similarly says “super add” the entire Mercury/Jupiter dṛṣṭi.
4. Raman/Jain’s planetary Drik Bala worked tradition uses one-quarter of the signed net Drishti Pinda without a separate Mercury/Jupiter full term; Jain reserves full Mercury/Jupiter treatment explicitly for Bhava Drishti Bala.
5. The task context noted that Ganesh Datt Pathak appears to preserve a different arrangement. A directly inspectable Pathak scan/page was not located in this run, so that claim is **not upgraded to verified evidence** here.

This difference materially changes the operator and blocks a single canonical BPHS production formula.

## Answers to the required questions

1. **Governing passages:** BPHS common ch.27 v.19 for planetary bala; the parallel Bhava Bala wording at vv.28–30 is relevant to interpreting `jñejya`; Jha’s Sudhā commentary supplies the clearest checked multi-aspect aggregation gloss.
2. **Individual vs totals:** Jha explicitly aggregates benefic dṛṣṭis and malefic dṛṣṭis into their respective sums before quartering. Raman/Jain also aggregate signed aspect values before deriving Drik Bala. Per-aspect quartering is mathematically equivalent for ordinary linear terms, but is not the clearest textual description.
3. **Quarter factor:** source-supported on the śubha/pāpa aspect aggregate (or equivalently its linear individual terms). Raman/Jain quarter the net Drishti Pinda. Jha/Santhanam then have a separate Mercury/Jupiter add.
4. **Precedence:** none found. Benefic and malefic contributions coexist and net.
5. **Mercury/Jupiter interaction:** Jha/Santhanam support a post-quarter full computed-dṛṣṭi add; Raman/Jain planetary computation does not. This remains profile/recension-dependent and is the main blocker.
6. **Fixed +60:** not supported. Use computed dṛṣṭi magnitude if following the Jha/Santhanam clause; do not invent 60.
7. **Material differences:** yes, especially Jha/Santhanam vs Raman/Jain/Śrīpati-style planetary computation; Pathak remains unverified in this run.
8. **Source-closed:** additive coexistence/no precedence, signed benefic/malefic accumulation, quarter treatment for ordinary terms, variable computed dṛṣṭi magnitude, and no fixed +60. **Profile-dependent/unresolved:** whether planetary Drik Bala gets the additional full Mercury/Jupiter term and how conditional Mercury status interacts with that term.
9. **Research profile:** a single canonical profile is not safe to bind. Two explicit non-production candidate semantics can be drafted (below) for human review.
10. **Market direction:** Drik Bala remains planetary strength. No checked source authorizes `positive = bullish` or `negative = bearish` for an instrument.

## Non-production machine-readable candidate semantics

These are **research candidates only**, not production bindings.

### Candidate A — `BPHS_JHA_27_19_LITERAL_RESEARCH`

```json
{
  "profileId": "BPHS_JHA_27_19_LITERAL_RESEARCH",
  "status": "RESEARCH_ONLY",
  "aspectMagnitude": "source_computed_drishti_including_applicable_visesha_geometry",
  "ordinaryBeneficAggregate": "sum(aspectMagnitude where nature=BENEFIC)",
  "ordinaryMaleficAggregate": "sum(aspectMagnitude where nature=MALEFIC)",
  "ordinaryQuarterTerm": "0.25 * (ordinaryBeneficAggregate - ordinaryMaleficAggregate)",
  "jnaIjyaExtra": "aspectMagnitude(Mercury) + aspectMagnitude(Jupiter)",
  "drikBalaStrength": "ordinaryQuarterTerm + jnaIjyaExtra",
  "fixedMercuryJupiter60": false,
  "precedenceRule": null,
  "marketDirection": "WITHHELD",
  "blocker": "double-count/recension interpretation and conditional Mercury interaction require human/source review"
}
```

### Candidate B — `SRIPATI_RAMAN_JAIN_NET_QUARTER_RESEARCH`

```json
{
  "profileId": "SRIPATI_RAMAN_JAIN_NET_QUARTER_RESEARCH",
  "status": "RESEARCH_ONLY",
  "aspectMagnitude": "source_computed_drishti_including_applicable_visesha_geometry",
  "signedAspect": "+aspectMagnitude if BENEFIC; -aspectMagnitude if MALEFIC",
  "drishtiPinda": "sum(signedAspect)",
  "drikBalaStrength": "0.25 * drishtiPinda",
  "planetaryMercuryJupiterExtra": 0,
  "bhavaMercuryJupiterRule": "SEPARATE_OPERATOR_NOT_IMPORTED",
  "precedenceRule": null,
  "marketDirection": "WITHHELD"
}
```

Do not silently merge these candidates.

## Conditional Moon/Mercury context verified but not collapsed into arithmetic

BPHS 3.11 directly classifies kṣīṇa Moon among malefics and says Mercury becomes malefic when joined (`yuta`) with a malefic. Agni Purāṇa 121.61 supplies cross-text kṣīṇa/pūrṇa phase-boundary evidence; it must not be misattributed to BPHS 3.11. Sārāvalī/Yavana lunar phase-strength gradation is a separate strength operator and must not replace natural benefic/malefic classification. These contextual inputs remain profile/provenance-separated from the aggregation formula.

## What is not established

- No directly inspected Ganesh Datt Pathak page was obtained in this run.
- No critical apparatus was obtained proving whether `jñejyadṛkyuktam` is original/stable across all printed recensions.
- No Jha worked numerical example was verified to prove the apparent 1/4 + full double contribution for Mercury/Jupiter.
- No rule was found saying the Mercury/Jupiter extra disappears when Mercury is conditionally malefic.
- No source authorizes applying natal Drik Bala unchanged to transit-to-natal, transit-to-market, or market-direction scoring.
- No bullish/bearish mapping is authorized.

## Proposed disposition

`RESEARCH_ONLY`

The ordinary multi-aspect aggregation question is substantially closed: additive signed accumulation, no precedence, and quarter treatment are well supported. The **single canonical planetary operator remains blocked by the Mercury/Jupiter clause/recension split**.

## Recommended next evidence target

1. Obtain and inspect a Ganesh Datt Pathak printed scan/page for the corresponding Spasṭabala/Drik Bala passage and compare its verse arrangement with Jha/Santhanam.
2. Inspect an actual image of Jha pp.177–178 (not OCR only) and, if present elsewhere in the edition, a worked example clarifying whether Mercury/Jupiter are counted quarter + full.
3. Search Suresh Chandra Mishra and Padmanabh Sharma printed witnesses for the same clause.
4. Only after that adjudicate Candidate A vs Candidate B, or preserve both as named research profiles.

## Guards against overclaiming

- Do not call Candidate A or B “the BPHS formula” without edition/profile qualification.
- Do not infer a fixed +60 Mercury/Jupiter bonus.
- Do not confuse Jupiter’s geometrical viśeṣa dṛṣṭi increment with the `jñejya` arithmetic clause.
- Do not import Bhava Bala’s Mercury/Jupiter rule into planetary Drik Bala without explicit profile provenance.
- Do not choose a recension/profile using price or outcome behavior.
- Preserve UNKNOWN/RESEARCH_ONLY where the printed witnesses diverge.
- Keep `marketDirection=WITHHELD`.

## Dated bibliography / source table — checked 2026-10-02

- BPHS Sanskrit, ch.27 v.19, Sanskrit Wikisource: https://sa.wikisource.org/wiki/बृहत्पाराशरहोराशास्त्रम्/अध्यायः_२७_(स्पष्टबलाध्यायः)
- BPHS Sanskrit, ch.27, SanskritDocuments: https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par2130.html
- BPHS morphology/translation, EnjoyLearningSanskrit ch.27: https://enjoylearningsanskrit.com/scriptures/parashara/chapter-27/
- Devachandra Jha, *Bṛhatpārāśara-horāśāstram*, Sudhā commentary, Chaukhambha Sanskrit Sansthan, Kashi Sanskrit Granthamala 220; Internet Archive item: https://archive.org/details/brihat-parashar-hora-shastra-of-parashar-muni
- Bibliographic confirmation for Jha edition: CiNii Books NCID BA71955448 (1978 2nd ed.; 672 pp.; Kashi Sanskrit Granthamala 220).
- R. Santhanam, *Brihat Parasara Hora Sastra*, Ranjan Publications; accessible reproduction checked via Siva.sh v.19 and digital book reproductions.
- B. V. Raman, *Graha and Bhava Balas*, Chapter VIII, 13th-edition text reproduction (preface 1992), Scribd document 722401597.
- V. P. Jain, *Text Book for Shadbala (Grahas) and Bhavabala*, chapters 7–8, accessible text reproduction at PDFCoffee.
