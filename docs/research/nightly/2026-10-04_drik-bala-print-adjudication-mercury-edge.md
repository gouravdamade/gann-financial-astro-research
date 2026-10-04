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

Keep Jain separate until its Mercury-nature convention is directly sourced. Do not silently inherit either Raman's conditional Mercury or the Śrīpati-Sastri always-benefic convention.

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
- market bullish/bearish direction remains unauthorized.

## What remains unresolved

1. **Planetary A1 worked arithmetic:** find a Jha, Padmanabh, or Mishra planetary Drik-Bala example where Mercury or Jupiter actually aspects the tested planet and the final planetary strength is numerically shown.
2. **Malefic-Mercury + jñejya edge:** directly verify whether a conditionally-malefic Mercury contributes `-M/4` in the ordinary pool and then still receives `+M` as the special `jña` term. Current `+0.75M` is the best-supported inference, not direct worked proof.
3. **Exact Mercury nature trigger per profile:** distinguish BPHS's conjunction/association rule from Raman's close-Sun/combust treatment and from broader modern rules based merely on malefic aspect. Do not merge them.
4. **Jupiter double-participation:** obtain direct planetary worked arithmetic confirming whether Jupiter is quarter-counted in the ordinary benefic aggregate and then added whole in the `ijya` family.
5. **Jain Mercury convention:** source it directly rather than inheriting Raman/Śrīpati semantics.
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
- Printed BPHS witnesses: Ganesh Datt Pathak, Padmanabh Sharma, Devachandra Jha, Suresh Chandra Mishra.

## Guards against overclaiming

- Do not claim the `+0.75M` malefic-Mercury result is direct planetary worked evidence.
- Do not treat Mishra's Bhāva worked arithmetic as if it were a planetary worked example.
- Do not merge Raman and Śrīpati-Sastri Mercury semantics.
- Do not turn whole computed dṛṣṭi into a fixed 60.
- Do not use functional lordship or market outcomes to assign Drik-Bala sign.
- Keep `marketDirection=WITHHELD`.
