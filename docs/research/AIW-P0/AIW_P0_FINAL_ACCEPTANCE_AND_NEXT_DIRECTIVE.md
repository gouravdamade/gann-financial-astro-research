# AIW-P0 · Final acceptance and next directive

**Admit the unreduced, source-pinned count of favorable natal contributors for each of the seven grahas.** Sun and Mars also pass every applicable numerical comparison with AIW-MASTER-02. A change of edition can change the adverse count while preserving every favorable mark. Mars in Aquarius is the regression test that distinguishes the two readings.

| Requested decision | Disposition | Evidence and scope |
|---|---|---|
| Raw Sun marks | Accept | Eight masks in Aiyar IX.1. The 1899 plate agrees. The annual replay matches all 12 sign changes. |
| Raw Mars marks | Accept with explicit adverse convention | All twelve favorable counts in the 1905 horoscope reproduce. Aiyar and Bhaṭṭotpala differ on one neutral place. |
| Other five graha masks | Accept for Aiyar 1905 | All forty contributor lists were transcribed. The 1899 Mercury and Saturn tables agree. The Moon, Jupiter and Venus tables have variant or doubtful entries. |
| Realized result | Accept the cited case judgments. Withhold the general evaluator. | The texts distinguish mark excess, conditions of realization and strength. A final amount in the conflicting Aries case remains unestablished. |
| Sudarśana majority | Conditional acceptance | Kapoor's qualified, distinct 2:1 testimonies can decide a house. Strength ties, repeated identities and mixed-ring examples restrict general use. |
| Same-planet USD/JPY difference | Accept as a descriptive research statistic | Same recipient, edition, stage and transit instant. The currency epochs are registered experimental hypotheses. |
| Cross-planet aggregate influence | Withhold | A documented Samudāya sum uses the same sign across recipients. It supplies no rule for combining each planet at its own current sign into an influence score. |

## Raw evaluator specification

**Operator** `AIW_ASHTAKAVARGA_RAW_MARKS_V1`. Stage is always unreduced. The caller supplies the following fields.

| Field | Required value or convention |
|---|---|
| `sourceProfile` | `AIYAR_1905_IX` for all seven recipients, or `BHATTOTPALA_JHA_1934_IX_MARS` for the documented Mars calculation. The second profile is bounded to Mars. |
| `recipient`, `transitSign` | One supported graha and an integer sign from 0 (Aries) to 11 (Pisces). The caller supplies the sign for the instant being evaluated. |
| `natalSigns` | Exactly one sign per named contributor in this order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna. Contributors in the same sign retain their identities. |
| Provenance | Carry the chart ID, source edition/locator and reference sign inputs into the result. For a timeline also record the UTC instant, sidereal convention, ephemeris model and version, and boundary precision. |

For each contributor compute `place = 1 + floorMod(transitSign - natalSign, 12)`. Read its recipient-specific favorable mask from [the transcription data](AIW_P0_MARS_12_CELL_REPRODUCTION.json), field `placesInclusive[recipient]`, in the declared contributor order. Assign favorable on membership. With the Jhā Mars profile assign neutral to the Moon contributor at place 10. Assign adverse to each remaining contributor. Preserve the ordered eight records with identity, relative place and classification.

Return integer counts `favorable`, `adverse`, `neutral` with sum eight. Also return `majority` by comparing favorable with adverse (favorable, adverse or equal). If the source's cancellation is requested, return the exact pair `excessNumerator = favorable - adverse`, `excessDenominator = 8`, identified as **mark excess**. Keep the eight-reference denominator when a contribution is neutral. Omit any realized-result field. An unsupported recipient/profile pair, an unknown profile or malformed sign input yields no numerical result. For uncertain natal or transit signs, keep the input unresolved or enumerate labeled alternatives.

**Acceptance fixtures.** In the printed horoscope, Mars in Aries yields favorable contributors Mars, Jupiter and Saturn. The result is 3 favorable, 5 adverse and 0 neutral. Mars in Aquarius yields 3/5/0 under Aiyar and 3/4/1 under Jhā, in favorable/adverse/neutral order. The mark excess is −2/8 and −1/8 respectively. Over a full 12-sign cycle the Aiyar favorable totals in recipient order are 48, 49, 39, 54, 56, 52, 39. An implementation should also reproduce every per-contributor decision in the twelve-cell fixture. Totals alone cannot detect a substituted place.

**Temporal use.** Index the precomputed 12-sign array by the actual recipient sign at the query instant. On an ingress retain the old state up to the crossing and the new state from the crossing onward. When displaying whole-second timestamps use the first whole second in the new sign. For a two-chart difference subtract JPY favorable marks from USD favorable marks under identical evaluation settings. Keep both vectors and counts. A timeframe selection never enters the mark formula. [2025 fixtures and boundary checks](AIW_P0_2025_INDEPENDENT_TIMELINE_REPLAY.md)

## Qualified interpretation and acquisition priorities

`AIW_ASHTAKAVARGA_QUALIFIED_RESULT_V1` remains **withheld**. A case annotation may record the raw input, the house reference and placement, natal or transit dignity and strength if specified, the witness and its actual judgment. Capricorn and Gemini have explicit full-result statements in Aiyar's worked example. The Aries majority/dignity conflict has an explicit raw remainder and evidence of qualitative mitigation in a separate authority. Neither supplies the missing final numerical value for that case. [Sources and worked cases](AIW_P0_MARKS_VERSUS_REALIZED_PHALA.md)

| Priority and exact missing proposition | Edition, locator and access | Evidence needed | What it blocks |
|---|---|---|---|
| 1. How much adverse phala survives an adverse excess when Mars is in its own sign but in an apacaya house? Which condition governs if they conflict? | Bhaṭṭotpala, Sītā Rāma Jhā 1934, IX.8, pp142–146 in the held scan. V. Subrahmanya Sastri 1956, IX.8, pp203–207. Compare Mantreśvara XXIII.10, Kapoor translation, p225. [Sastri edition](https://astrojyotish.info/literature/brihat-jataka-sastri/) · [Phaladīpikā](https://www.panchanga.lv/wp-content/uploads/2020/06/Phaladipika_Shri-Mantreswara.pdf) | A worked horoscope specifying raw counts, both conflicting conditions, house reference, strength at fruition and the final amount or explicit decision to leave it qualitative. Begin with Aries and Scorpio in the printed chart. | General qualified result. Raw counts remain usable. |
| 2. Which natal/transit strength test, house reference and exceptions govern realization in the chosen edition? | Jhā 1934, IX.8, pp145–146, including the Devakīrti citation. Sastri 1956, pp205–207. Aiyar 1905, IX.8 and note (f). [Public Aiyar scan](https://upload.wikimedia.org/wikipedia/commons/c/c2/The_Brihat_jataka_%28IA_brihatjataka00varaiala%29.pdf#page=144) | A worked case where Moon-relative and Lagna-relative house classes disagree, with the delivery-time strength explicitly evaluated. | Qualified rule generalization. Raw counts remain usable. |
| 3. Are the uncertain BPHS cells printed variants, damage, or corrections attributable to a specific edition? | Govind Sharma Shastri 1899, printed pp116–117, PDF145–146 in the held research scan. [Plate comparison](AIW_P0_SEVEN_GRAHA_MASK_REVIEW.md) | A second lawfully accessible impression of these pages or a critical collation. Check Mars/Sun place 5 and Mars/Moon places 10–11 first. | An edition-independent mask claim and a corrected 1899 evaluator. The Aiyar profile stands. |
| 4. How does the later Sudarśana rule measure equal-count strength or count a planet repeated across coincident rings? | Kapoor vol. II, ch74.10–16, pp914–915 and worked cases pp916–919. Compare the distinct Subodhinī ch51 example. [Edition links and Sanskrit locators](AIW_P0_SUDARSANA_SOURCE_ADJUDICATION.md) | A tied example with explicit bala or aspect arithmetic, and a chart with repeated identities whose verdict changes if deduplicated. | The affected Sudarśana branches. Neither Aṣṭakavarga operator depends on this acquisition. |

## Next directive for central review

Freeze the edition-tagged raw specification and the printed horoscope as the candidate research reference. Start the next source review with the first acquisition question. Record each witness's intermediate and final judgments separately. If the conflict yields only a qualitative ruling, preserve its wording and leave the numerical qualified evaluator withheld. Hāyanaratna duration was baseline context and has no new disposition in this audit.

Research disposition throughout: `executionAllowed=false`, `financiallyValidated=false`, `marketDirectionAssigned=false`. No production change, repository publication, price analysis, polarity promotion, hypothesis revision or trading functionality forms part of this packet.

