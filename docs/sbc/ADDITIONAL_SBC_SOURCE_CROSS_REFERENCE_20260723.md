# Additional Sarvatobhadra Source Cross-reference - 2026-07-23

## Scope

This audit classifies four user-supplied files after the 1972 *Trailokya
Dipika* acquisition. Its purpose is to separate genuinely independent evidence
from later editions, edited transcriptions, and duplicate compilations before
anything enters the local Jyotish corpus or executable SBC code.

Private source files remain outside Git. Only checksums, provenance, bounded
derived text, and the conclusions below are tracked.

## Files

| File | SHA-256 | Identification | Decision |
| --- | --- | --- | --- |
| `Sarvatobhadra Chakra - Khemraj Publishers_text.pdf` | `19CC2387C6C6B80E9A1F5A63BB9A71090A10FB17F3BD8BB56058210667F61ED8` | June 2016 Khemraj Shri Krishnadas reprint of Pt. Mithalal Vyas's Sanskrit-Hindi *Sarvatobhadra Chakra / Trailokya Dipika* work | Cross-edition reading witness only; not independent doctrine and not a second vote |
| `231820842-Super-Astrology.pdf` | `786A20415DAFC791CA7374C33458B30465EA5B93DD7F2856B1969FB7374A8F6A` | ChiStaBo A.D. 2013 edited transcription of the N.N. Krishna Rau and V.B. Choudhary booklet associated with Bombay, 20 January 1962 | Derivative comparison source; only bounded financial pages enter opt-in hypothesis retrieval |
| `Introduction to Sarvatobhadra Chakra.pdf` | `47D8F8E3DB687435238EADB5C7CC6B729E91C601E9927155D7A38AC112AA68CD` | Unattributed 17-page 2010 compilation; pages 3-17 reproduce Phaladeepika chapter 26 and its SBC supplement | Duplicate-detection record only; deliberately excluded from the corpus |
| `Sarvatobhadra Chakra.doc` | `D2D03024EAD7ECD70A67A7A3DD981C947B75943BB888C879B46571223D8CE529` | P.V.R. Narasimha Rao article identifying itself as an extract from *Vedic Astrology: An Integrated Approach*, Sagar Publications, December 2000 | Page-rendered private reference commentary; no executable profile |

## Visual and Text Checks

### Khemraj 2016 and Mithalal Vyas 1972

- PDF page 3 identifies *Sarvatobhadra Chakra* with *Trailokya Dipika*
  commentary and Pt. Mithalal Vyas.
- PDF page 4 identifies a June 2016, Samvat 2073 Khemraj Shri Krishnadas
  edition.
- PDF pages 15-16 preserve the same opening three-direction Vedha passage
  used in the 1972 source audit.
- PDF pages 85-87 visibly preserve the later commodity/price and table
  material corresponding to the Arghya research area.
- A seven-character normalized OCR comparison between the 1972 OCR companion
  and the 2016 text PDF produced 0.4065 Jaccard overlap and 0.5804 containment
  of the shorter unique-gram set. OCR noise is substantial, but title,
  authorship, chapter sequence, visible verses, tables, and this overlap all
  identify the files as the same textual lineage.

The 2016 reprint is useful when a character or table entry is unclear in the
1972 scan. It does not independently prove a rule authored or compiled in the
same work. In particular, agreement between the two editions does not certify
the Arghya arithmetic or its market direction.

### Krishna Rau, Choudhary, and ChiStaBo 2013

- PDF page 2 identifies N.N. Krishna Rau and V.B. Choudhary, the Bombay date
  20 January 1962, and ChiStaBo A.D. 2013 editing.
- The front matter says that the booklet contains ambiguities and invites
  further research. The editor states that additions are bracketed.
- PDF pages 24-27 describe commodity categories, planetary ownership,
  dignity and relationship percentages, a one-degree aspect condition, and a
  twenty-part price unit.
- PDF page 34 gives a retrospective iron/steel index example for December
  1961 to January 1962 and then lists modifications reportedly used by local
  astrologers.

These pages are relevant to our financial research, especially because the
twenty-part price unit resembles the twenty-part conversion found in the
Trailokya Arghya chapter. Similarity is a research lead, not independent
confirmation: the later booklet may draw from the same broader tradition, and
its worked example is retrospective. The five selected pages are therefore
indexed only as `hypothesis_reference` material.

No claim from this source may change deterministic SBC scoring, Auto Suggest,
live inference, official ML notes, validation ledgers, or execution. Each
numerical proposal must be restated as a prospective test before evaluation.

### Unattributed 2010 Introduction

- The PDF metadata identifies a 2010 Word document but no credited author or
  edition.
- PDF pages 3-17 present Phaladeepika chapter 26 and the same editor-supplied
  SBC material already retained with page provenance from the 1937
  Subrahmanya Sastri edition.
- For PDF pages 13-17, normalized eight-token shingles had 0.4800 containment
  against the existing page-marked Phaladeepika corpus despite OCR and layout
  differences.

Indexing this file would make one textual source look like two agreeing
sources. It is registered for provenance and duplicate detection only.

### P.V.R. Narasimha Rao Article

The article supplies a distinct modern interpretation:

- a 9 by 9, 81-cell board;
- one inward horizontal or vertical ray plus two diagonal rays from the
  occupied nakshatra for any planet;
- name sound, natal nakshatra, rashi, tithi, and weekday target classes;
- natural benefic/malefic treatment; and
- retrospective examples using several simultaneously hit natal references.

This differs from both existing executable-guidance profiles:

| Source profile | Fixed Sun/Moon/nodes | Mars through Saturn |
| --- | --- | --- |
| Phaladeepika editor supplement | One fixed left/right ray | One ray selected by motion |
| Trailokya Dipika 1972 | All three rays | One ray selected by motion |
| P.V.R. Narasimha Rao article | All three rays | All three rays |

The article is useful commentary and a source-conflict witness. It is not yet
an executable third profile because the supplied extract is not a page-cited
book edition, gives no independently certified financial scoring model, and
does not supply the profile fixtures needed to resolve every conflict with the
other recensions. Its page-rendered local text enters only the
`reference_commentary` layer.

## Local Integration

Private archives:

- `D:/GannFinancialAstro/sources/private/TRAILOKYA_DIPIKA_VYAS_KHEMRAJ_2016_REPRINT_19CC2387.pdf`
- `D:/GannFinancialAstro/sources/private/KRISHNA_RAU_CHOUDHARY_SBC_CHISTABO_2013_786A2041.pdf`
- `D:/GannFinancialAstro/sources/private/SBC_INTRODUCTION_UNATTRIBUTED_COMPILATION_47D8F8E3.pdf`
- `D:/GannFinancialAstro/sources/private/PVR_NARASIMHA_RAO_SBC_ARTICLE_D2D03024.doc`

Local derived retrieval files:

- `D:/GannFinancialAstro/sources/private/derived/PVR_NARASIMHA_RAO_SBC_ARTICLE_2000_D2D03024.txt`
  as `reference_commentary`;
- `D:/GannFinancialAstro/sources/private/derived/KRISHNA_RAU_CHOUDHARY_SBC_FINANCIAL_PAGES_24_27_34_786A2041.txt`
  as opt-in `hypothesis_reference`.

The Khemraj reprint and unattributed introduction are not indexed. This avoids
double counting. All generated corpus/index artifacts remain local and
uncommitted.

## What This Changes

- The local LLM can cite the P.V.R. interpretation as modern commentary.
- A Sarvatobhadra or financial-hypothesis question can retrieve the bounded
  Krishna Rau/Choudhary pages with an explicit unverified-hypothesis warning.
- The source register can identify the Khemraj reprint when resolving a
  difficult 1972 reading.
- The duplicate 2010 compilation cannot inflate retrieval confidence.

## What Remains Blocked

- A P.V.R. all-planets three-ray executable profile.
- Any numerical commodity-price conversion from the 1962 booklet.
- Trailokya Arghya table arithmetic and bullish/bearish mapping.
- Automatic adoption of one-degree or dignity/relationship weights.
- Auto Suggest, live inference, official ML-note, validation, and MT5 use.

The next source step is bilingual double transcription of the 1972 and 2016
Arghya tables, followed by a separately sourced worked example and a frozen
prospective test. Reprint agreement alone is not enough.
