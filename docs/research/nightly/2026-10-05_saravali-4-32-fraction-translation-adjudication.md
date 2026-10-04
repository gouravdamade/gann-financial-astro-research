# Nightly Research — Sārāvalī 4.32–33 Fraction / Translation Adjudication

Date: 2026-10-05  
Status: RESEARCH_ONLY  
Branch baseline verified before work: `8ce3cddd6e8e317c126bcc7c27c043762f5d4fc9`  
Scope: evidence/documentation only. No production/operator/source-ledger/evidence-registry/runtime/scoring/polarity/provider/outcome/MT5/Candidate-C/EMP3/execution changes.

## Question / why it matters

Re-adjudicate the apparent conflict between the Sanskrit root of Kalyāṇavarman's Sārāvalī 4.32–33 and R. Santhanam's English rendering of the ordinary dṛṣṭi fractions. The repository currently binds the research operator `SARAVALI_4_32_ORDINARY_DRSTI_V1` to:

- 3rd/10th = 1/4;
- 5th/9th = 1/2;
- 4th/8th = 3/4;
- 7th = full.

The held Santhanam English rendering instead prints 4th/8th = half and 5th/9th = 3/4. This pass asks whether that is a translation/editorial error, a recension variant, a grammatical/parsing error, a verse/pagination problem, or another source-defined distinction.

## Repository context verified

The live `research/nightly-project-work` branch was verified at `8ce3cddd6e8e317c126bcc7c27c043762f5d4fc9` before research. The current ledger already records the Sanskrit-root operator as source-closed and flags `SANTHANAM_ENGLISH_4_32_TRANSLATION_EDITORIAL_MISMATCH`. The earlier repository page adjudication separates root and translation layers and gives its held-scan locators as Sanskrit root printed p.57 / scan image 61 and English rendering printed p.58 / scan image 62.

A currently accessible online scan of the same R. Santhanam / Ranjan Volume I lineage has different PDF/printed pagination: the relevant combined Sanskrit + English page is PDF page index 49, visible printed page 51. This is a pagination difference between scan artifacts, not a doctrinal difference.

## Exact witnesses checked

| Witness | Locator | Verification | Result |
|---|---|---|---|
| R. Santhanam, *Saravali of Kalyana Varma*, Vol. I, Ranjan Publications | current web PDF, PDF index 49 / visible printed p.51, Chapter 4, vv.32–33 | DIRECT PAGE-IMAGE VERIFIED this run | Sanskrit root and English translation appear on the same page and visibly disagree in the 4/8 vs 5/9 fractions. |
| Repository-held Santhanam/Ranjan 1983 witness | repo adjudication: root printed p.57 / scan 61; English printed p.58 / scan 62 | PRIOR DIRECT PAGE-IMAGE ADJUDICATION; source bytes not tracked in repo | Same mismatch already recorded. |
| Sanskrit Wikisource Sārāvalī | Chapter 4, vv.32–33 | DIRECT DIGITAL SANSKRIT TEXT | Same ordered root construction; minor textual/OCR variants do not alter the house-pair sequence. |
| VedicPupil Sārāvalī | Chapter 4, verse display 4.32 containing both root stanzas | DIRECT DIGITAL SANSKRIT + INDEPENDENT MODERN TRANSLATION | Reads `caraṇavṛddhitaḥ` / “increasing by a quarter [each step]” and preserves 3/10 → trine → quadrangular → 7th order. |
| Varāhamihira, *Bṛhat Jātaka* 2.13 | independent Sanskrit/English digital witness | CROSS-TEXT ONLY | Uses the closely parallel `tridaśatrikoṇacaturasrasaptamāni ... caraṇābhivṛddhitaḥ` construction and explicitly translates the same increasing-quarter sequence. Not used as a substitute for Sārāvalī. |
| Uttarakhand Open University MAJY-606 | unit on ordinary/special dṛṣṭi | SECONDARY CROSS-TEXT | States ordinary 3/10 one-quarter, 5/9 half, 4/8 three-quarter, 7 full; useful corroboration only. |

## Direct Sārāvalī root evidence

The current direct page image shows the operative first stanza with the key construction (bounded excerpt):

`... grahāś caraṇavṛddhitaḥ sarve / tridaśa-trikoṇa-caturasra-saptamānāṃ phalaṃ krameṇaiva ...`

The independent digital witnesses give substantially the same text, with minor variants such as singular/plural `sampaśyati/sampaśyanti` and one Wikisource reading/OCR `carāvṛddhitaḥ` beside the more coherent `caraṇavṛddhitaḥ`. None changes the ordered list or `krameṇa`.

### Tight grammatical mapping

The arithmetic is encoded by two linked expressions:

1. `caraṇa-vṛddhitaḥ` = by/in quarter-increase, i.e. increasing by one quarter;
2. `krameṇa eva` = precisely/in that order.

The ordered objects are:

1. `tri-daśa` = 3rd and 10th;
2. `trikoṇa` = the trines, 5th and 9th;
3. `caturasra` = the quadrangular places, 4th and 8th;
4. `saptama` = 7th.

Applying the stated quarter-increase **in that order** gives uniquely:

| Ordered class | Fraction |
|---|---:|
| 3rd / 10th | 1/4 |
| 5th / 9th | 1/2 |
| 4th / 8th | 3/4 |
| 7th | full |

No reordering is grammatically required or supported by the checked Sanskrit witnesses.

## Santhanam English rendering — direct-page result

The same directly inspected Santhanam page prints the English sequence as:

- 3rd/10th: 1/4;
- 4th/8th: half;
- 5th/9th: 3/4;
- 7th: full.

Thus the disagreement is directly reproducible **within the same physical page**: the Sanskrit immediately above supplies the ordered sequence 3/10 → trine(5/9) → quadrangular(4/8) → 7, with quarter increments; the English prose changes the middle order to 4/8 → 5/9 while retaining half then 3/4.

This is decisive against a pagination or verse-alignment explanation for this witness.

## Mismatch table

| Place pair | Sanskrit root by `caraṇa-vṛddhi` + `krameṇa` | Santhanam English | Verdict |
|---|---:|---:|---|
| 3 / 10 | 1/4 | 1/4 | AGREES |
| 5 / 9 | 1/2 | 3/4 | DISAGREES |
| 4 / 8 | 3/4 | 1/2 | DISAGREES |
| 7 | full | full | AGREES |

The English has transposed the middle two **place-pair labels relative to the fractions**. It has not changed the fraction progression itself.

## Independent witness comparison

### Sanskrit Wikisource

The Chapter 4 text preserves:

- the ordered compound `tridaśa-trikoṇa-caturasra-saptama`;
- `krameṇaiva`;
- the next stanza's special full aspects for Saturn 3/10, Jupiter trine, Mars quadrangular, and the remaining planets on the 7th.

Its minor `carāvṛddhitaḥ`/apparatus-looking variants are not evidence for swapping the middle classes.

### VedicPupil

This independently presented Sanskrit reads `caraṇavṛddhitaḥ` and translates the rule as all planets aspecting “increasing by a quarter [each step]”, with the same ordered 3/10 → trine → quadrangular → 7th sequence. This agrees with the repository root reading, not Santhanam's middle-pair swap.

### Bṛhat Jātaka 2.13 — cross-text only

Varāhamihira's closely parallel verse reads `tridaśatrikoṇacaturasrasaptamāny ... caraṇābhivṛddhitaḥ`; an independent translation explicitly resolves it as 3/10 quarter, 5/9 half, 4/8 three-quarter, 7 full. This strongly corroborates the grammar and inherited sequence, but the Sārāvalī conclusion above does not depend on importing Bṛhat Jātaka doctrine.

## Edition / recension / pagination adjudication

### Translation/editorial error

**SUPPORTED WITH HIGH CONFIDENCE for the Santhanam English layer.** The mismatch occurs on the same directly inspected page as the Sanskrit root, and independent Sanskrit presentations preserve the root ordering.

### Sanskrit recension variant

**NO EVIDENCE LOCATED.** No checked Sanskrit witness reverses `trikoṇa` and `caturasra` or otherwise yields 4/8 half and 5/9 three-quarter. This pass does not prove that no such recension exists anywhere; it establishes that none is evidenced by the checked witnesses.

### Repository grammatical/parsing error

**NOT SUPPORTED.** `caraṇa-vṛddhi` plus `krameṇa` and the ordered compound make the current repository mapping the natural and independently corroborated reading.

### Pagination / verse-alignment error

**NOT A DOCTRINAL EXPLANATION.** Scan artifacts differ in page numbering (repo-held witness locators versus current online PDF), but in the current direct scan Sanskrit and English are on the same visible page. The fraction conflict survives perfect alignment.

## Ordinary versus special dṛṣṭi

The first stanza gives the **ordinary graded fraction sequence**. The immediately following stanza names **special full aspects**:

- Saturn: 3rd/10th;
- Jupiter: trines (5th/9th);
- Mars: quadrangular (4th/8th);
- 7th remains full for the planets generally.

These are distinct source statements. The ordinary table must not be rewritten so that Jupiter/Mars/Saturn's special full aspects erase the ordinary fraction geometry. Conversely, the ordinary fractions must not downgrade a special full aspect where the second stanza explicitly supplies it.

No finding in this pass requires changing the conceptual separation represented by `CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1`.

## Answers to the required questions

1. **Held/root wording:** the operative construction is the ordered `tridaśa-trikoṇa-caturasra-saptama` sequence with `caraṇa-vṛddhi` and `krameṇa`; direct current Santhanam page confirms it.
2. **Binding:** quarter increments applied in the stated order bind 3/10 → 1/4, 5/9 → 1/2, 4/8 → 3/4, 7 → full.
3. **Santhanam English:** directly prints 3/10 quarter, 4/8 half, 5/9 three-quarter, 7 full.
4. **Reproducible disagreement:** YES, directly on the same page.
5. **Second Sanskrit witness:** YES; Wikisource and VedicPupil both retain the root order, with no middle-pair swap.
6. **Independent translation:** YES; VedicPupil's Sanskrit-based translation reads quarter-increase in the root order. Bṛhat Jātaka 2.13 independently corroborates the same construction cross-textually.
7. **Recension evidence:** NO evidence located for a Sanskrit recension supporting the Santhanam English swap.
8. **Verse-boundary/pagination explanation:** NO for the doctrinal mismatch; pagination differs among scans but same-page direct evidence reproduces the conflict.
9. **Current machine rule source-closed for Sārāvalī:** YES at the research-source level: `{3,10:1/4; 5,9:1/2; 4,8:3/4; 7:FULL}`.
10. **Mismatch label:** RETAIN, but refine conceptually to `SANTHANAM_ENGLISH_4_32_MIDDLE_PAIR_TRANSLATION_TRANSPOSITION` if a later human-reviewed ledger revision is authorized. No ledger was modified here.
11. **Impact on special dṛṣṭi operator:** NONE; ordinary and special remain distinct.
12. **Remaining UNKNOWN:** whether an as-yet-unchecked manuscript/printed recension reverses the middle pair; no evidence for one was found. Also, this pass does not adjudicate degree-exact/sphuṭa dṛṣṭi interpolation beyond this bounded sign/place fraction rule.
13. **Market semantics:** NONE authorized.

## Finding / confidence

**Finding:** The discrepancy is best classified as a **Santhanam English translation/editorial transposition of the 4/8 and 5/9 place-pair labels**, not as a Sārāvalī Sanskrit recension difference, repository parsing error, or pagination problem.

**Confidence:** HIGH for the held/current Santhanam lineage and the checked independent Sanskrit witnesses; not absolute manuscript-stemmatic closure.

## Operator/profile implications

`SARAVALI_4_32_ORDINARY_DRSTI_V1` is **source-safe as a research operator/profile** with:

```json
{
  "3": "1/4",
  "10": "1/4",
  "5": "1/2",
  "9": "1/2",
  "4": "3/4",
  "8": "3/4",
  "7": "FULL"
}
```

No production binding or ledger change is authorized by this packet. A future human-reviewed evidence/ledger revision may refine the known-translation-issue label to state explicitly that the middle **place-pair labels** are transposed in Santhanam English.

`CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1` remains separately scoped and is not altered by this result.

## Proposed status

`SAFE_TO_BIND` **only as a separate human-reviewed research-profile/evidence decision**. This packet itself remains `RESEARCH_ONLY` and makes no production change.

## What is not established

- No exhaustive manuscript stemma was built.
- No claim is made that every historical Sārāvalī manuscript has identical wording.
- No degree-exact interpolation operator is inferred from this verse alone.
- No benefic/malefic classification is inferred from the fraction.
- No Drik Bala arithmetic is inferred from this ordinary geometry rule.
- No market magnitude, oscillator amplitude, polarity, probability, or trading direction is authorized.

## Recommended next target

The Sārāvalī fraction discrepancy is sufficiently exhausted under the nightly stop conditions. Advance to the next broader doctrine queue item: **remaining conditional Moon/Mercury issues if materially unresolved**, with special care to keep Sārāvalī's own conditional-nature statements separate from BPHS and other profiles. If those are already source-closed in the live repository, proceed to **Trailokya/SBC mechanics**.

## Explicit guards against overclaiming

- Do not use Santhanam's English middle-pair ordering as root doctrine.
- Do not call the mismatch a proven Sanskrit recension variant.
- Do not use Bṛhat Jātaka to overwrite Sārāvalī; it is corroboration only.
- Do not merge ordinary and special dṛṣṭi operators.
- Do not infer sphuṭa/degree interpolation from this bounded rule.
- Do not convert dṛṣṭi fraction into market magnitude or oscillator amplitude.
- Do not infer bullish/bearish direction.
- Do not use price/outcome behavior to select the source reading.
- **MARKET DIRECTION: WITHHELD.**

## Dated bibliography / source log — 2026-10-05

- Kalyāṇavarman, *Sārāvalī*, R. Santhanam trans./ed., Ranjan Publications, Vol. I. Current accessible PDF: Chapter 4, vv.32–33, PDF index 49, visible printed p.51; direct page image inspected. Same edition lineage as repository witness, but pagination differs from the repo-held scan artifact.
- Repository source operator ledger `classical_source_operator_ledger_s2r1_r1_saravali_adjudicated_v1.json`, `SARAVALI_4_32_ORDINARY_DRSTI_V1`; repository-held witness locator root printed p.57 / scan 61 and English printed p.58 / scan 62.
- Sanskrit Wikisource, *Sārāvalī*, Chapter 4, vv.32–33, digital Sanskrit witness.
- VedicPupil, *Sārāvalī*, Chapter 4, verse display 4.32, digital Sanskrit plus independent modern translation from Sanskrit.
- Varāhamihira, *Bṛhat Jātaka* 2.13, independent Sanskrit/English digital witness; cross-text corroboration only.
- Uttarakhand Open University, MAJY-606, dṛṣṭi unit; secondary cross-text corroboration only.

## Final disposition

```text
STATUS = RESEARCH_ONLY
SARAVALI_4_32_ROOT_FRACTIONS = SOURCE_CLOSED_FOR_RESEARCH
3_10 = 1/4
5_9 = 1/2
4_8 = 3/4
7 = FULL
SANTHANAM_ENGLISH_MIDDLE_PAIR_SWAP = DIRECTLY_REPRODUCED
RECENSION_VARIANT_SUPPORTING_SWAP = NOT_LOCATED
PAGINATION_AS_CAUSE = REJECTED
ORDINARY_SPECIAL_DRSTI_SEPARATION = RETAIN
RESEARCH_PROFILE_BINDING = READY_FOR_SEPARATE_HUMAN_REVIEW
PRODUCTION_CHANGE = NONE
MARKET_DIRECTION = WITHHELD
```
