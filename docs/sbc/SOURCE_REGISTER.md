# SBC Source Register Notes

The machine-readable register is `configs/sbc/sources.yaml`.

## Authority Layers

| Source | Layer | Current use |
| --- | --- | --- |
| Sarvatobhadra Chakra Codex Implementation Guide | Workspace implementation specification | Architecture and phase gates only |
| Priority Experimental Engines SBC/Phase guide, SHA-256 `BE3DEC3C...` | Private workspace project proposal | Historical design input only; not doctrine |
| Revised SBC Phase Engine Review and Visualisation Architecture, SHA-256 `69827051...` | Private workspace project specification | P0 architecture and research-gate input only; not doctrine |
| Chakra and Gann source audit | Workspace source-conflict register | Prevents premature grid/rule selection |
| Panchanga formula foundation | Computational formula | Phase 1 facts only |
| Phaladeepika, Subrahmanya Sastri edition | Root translation plus editor supplement | Citation research; layers remain separate |
| Phaladeepika 1937 SBC editor supplement | Editor-supplied Horaratna extract/free rendering | Rotation-normalized 81-cell topology, construction text, letter witness, worked standard Vedha examples, nature rules, and modifiers |
| Sanjay Rath, Crux, Figure 1.2 | Modern secondary commentary | Figure-relative 81-cell coordinate frame and letter-glyph comparison |
| Sanjay Rath, Crux, printed page 11 | Modern secondary commentary | Independent motion-class comparison only |
| Trailokya Dipika 1972 original scan, SHA-256 `1EF82899...` | Sanskrit compilation, Hindi commentary, and practical introduction | Complete 118-page private scan; narrow Vedha pages certified and three Arghya tables double-transcribed into an execution-locked lab |
| Trailokya Dipika 1972 OCR companion, SHA-256 `7F220E0F...` | Derivative OCR navigation layer | Search and translation aid only; page images and original scan control citations |
| Trailokya Dipika Khemraj 2016 reprint, SHA-256 `19CC2387...` | Same-work later edition | All 108 Arghya cells match the 1972 pass; same-lineage agreement is not independent doctrine or price validation |
| P.V.R. Narasimha Rao SBC article, SHA-256 `D2D03024...` | Modern secondary commentary | Private page-rendered reference layer; its all-planets three-line interpretation remains non-executable |
| Krishna Rau/Choudhary, ChiStaBo 2013, SHA-256 `786A2041...` | Edited transcription of a 1962 booklet | Independent secondary table witness and 1/20 price-unit witness; no price-formula certification |
| Public 12/14 May 1951 Bombay silver page photographs | Primary page photographs from an unidentified edition | Partial historical worked-example witness; direction only, with final score-to-price page unavailable |
| Unattributed 2010 introduction, SHA-256 `47D8F8E3...` | Secondary compilation and duplicate text | Registered for duplicate detection; deliberately excluded from the corpus |
| Agarwal Sagar First Edition 2000 hardcopy | Physically evidenced modern-practitioner source | Founder-held physical edition and eight recovered pages close the acquisition gap; page-level transcription remains gated by checksum-verified private captures |
| Complete Agarwal edition acquisition request | Historical modern candidate | Superseded acquisition request retained for audit continuity; it no longer describes the current edition-identity state |
| Agarwal image scan, SHA-256 `5644DFC4...` | Incomplete modern-practitioner scan | Page-image research only; eight printed pages are missing and no edition imprint is present |
| Agarwal financial chapter, printed pages 180-194 | Intact chapter inside incomplete scan | Private opt-in LLM hypothesis reference only; no doctrine, Auto Suggest, live inference, or execution use |
| ChiStaBo January 2012 derivative, SHA-256 `8AF0045A...` | Derivative transcription | Earlier search/navigation aid only; explicit missing-page placeholders do not repair the scan |
| ChiStaBo 2013 edited version v3, SHA-256 `D93B9B97...` | Derivative transcription | Search/navigation aid only; changed terminology, redrawn figures, and bracketed editor additions are not doctrine |
| Maitreya8 | Software comparison | Behavioral fixture only |

## Ingestion Rule

A source may enter executable doctrine only after its edition, page range,
content layer, checksum, and quotation have been certified. OCR or LLM summaries
alone are not acceptable evidence. Private source files stay outside Git; only
metadata, short lawful quotations, and derived fixtures may be committed.

The implementation guide is not ingested into the local Jyotish doctrine
corpus. Its PDF text contains extraction damage and, more importantly, it is a
project specification rather than an independent classical authority.

## Agarwal Acquisition Audit

The three private files audited on 2026-07-22 are not independent witnesses.
The 191-page file is the underlying image scan. The 94-page January 2012 and
95-page 2013 ChiStaBo files are edited derivatives; they provide searchable
navigation but cannot repair missing pages or certify the source.

The image scan reaches printed page 194 but omits printed pages 46-47, 54-55,
62-63, 133, and 144. It also lacks an extractable ISBN, copyright page,
publisher statement, or edition statement. Its standalone incompleteness
remains historically true. Later founder-held physical Sagar Publications,
New Delhi, `First Edition 2000` evidence closes the project acquisition and
edition-identity gap and recovers those eight pages; see
`docs/sbc/AGARWAL_HARDCOPY_GAP_CLOSURE_20260813.md`. This does not certify the
book as executable doctrine: each table, geometry cell, and operator still
requires its checksum-verified page-level source contract.

One bounded exception is recorded for retrieval, not doctrine. PDF pages
177-191 contain consecutive printed pages 180-194, Chapter 20, and all fifteen
page images were visually reviewed. A private page-marked OCR extract may be
retrieved only when a question explicitly asks for Agarwal, Sarvatobhadra, or
financial/share-market hypotheses. Its claims remain modern practitioner
hypotheses for falsification and cannot affect deterministic calculations,
official ML notes, Auto Suggest, live inference, validation ledgers, or orders.

## Trailokya Dipika Acquisition Audit

The 118-page original scan and matching 118-page OCR companion were acquired
and aligned on 2026-07-23. PDF pages 20-21, printed pages 4-5, visibly support a
source-specific rule: Sun, Moon, Rahu, and Ketu cast all three Vedha directions,
whereas the existing Phaladeepika-editor profile gives them single fixed rays.
Both profiles are retained and must be selected explicitly.

The OCR companion is not an independent witness. It is used only for search and
draft translation. The page images remain authoritative. The three numeric
Arghya tables now have 108-cell independent passes from the 1972 and 2016 page
images, with zero cross-edition mismatches. Both editions also preserve two
internal scaling anomalies. The direction-only twenty-part availability index
is isolated in a research lab; direct price, financial labels and trades remain
blocked. A Krishna Rau/Choudhary table independently supports `11|15` for the
first printed anomaly, independently repeats unresolved `2|18` for the second,
and supports the 1/20 or 5-percent reference unit. Public page photographs of a
12-14 May 1951 Bombay silver example support the abundance/lower-price
direction in one historical case, but the final score-to-price working page is
unavailable. See
`docs/sbc/TRAILOKYA_DIPIKA_ACQUISITION_AUDIT_20260723.md` and
`docs/sbc/TRAILOKYA_ARGHYA_DOUBLE_TRANSCRIPTION_20260723.md`, plus
`docs/sbc/TRAILOKYA_ARGHYA_INDEPENDENT_WITNESS_AUDIT_20260723.md`.

## Additional Source Cross-reference

Four further files were classified on 2026-07-23. The Khemraj file is a 2016
reprint of the same Mithalal Vyas work, not an independent authority. The
unattributed 2010 introduction reproduces substantial portions of the already
page-provenanced Phaladeepika editor supplement and is not indexed. The P.V.R.
Narasimha Rao article enters only the `reference_commentary` layer, while PDF
pages 24-27 and 34 of the ChiStaBo-edited Krishna Rau/Choudhary booklet enter
only opt-in `hypothesis_reference` retrieval. No deterministic or executable
rule changed. See
`docs/sbc/ADDITIONAL_SBC_SOURCE_CROSS_REFERENCE_20260723.md`.

## Agarwal A1R1 page-level extraction

All six hardcopy captures, including `Agarwal_front.pdf` (seven PDF pages,
SHA-256 `D117CC540DD3E24CCAC3E565F1BF20A1A4FB72DED531298FB69AF3708B72E2E9`),
are privately materialized and verified. A1R1 adds source evidence only:

- two-pass numerical/general-strength fixtures for hardcopy pp.54-55 and
  pp.60-63;
- p.144 varga-allocation groups and partial author-figure facts;
- a partial Chapter 9 direction-by-motion record; and
- a page-level Chapter 20 ledger classified solely as `FINANCIAL_HYPOTHESIS`.

The author figure remains `UNKNOWN_CENTER_FOLD` for exact small-cell admission.
The unclosed motion-state definition, target-cell mapping, precedence,
cancellation, and complete reference contract mean that
`AGARWAL_SBC_2000_SOURCE_V1` does not exist as an executable profile. No
Agarwal material enters classical Mode 1, Fields polarity, pair fields, scoring,
Auto Suggest, ML labels, live inference, MT5, or execution.

## Agarwal A1R2 geometry and Vedha closure audit

The A1R2 source-only audit searched the private source roots for a clearer,
authenticated p.145-146 author figure. It found no new flat-page or
centre-fold capture. The existing hardcopy spread and the old scan retain their
earlier limited reconciliation role; ChiStaBo derivatives remain rejected as
controlling witnesses.

The book does contain more explicit Chapter 9 material than the early packet
recorded: five individual subject factors, nine-transit placement by longitude,
motion/direction descriptions, a 28-row star/sign target chart, stated
benefic/malefic Vedha classes, and selected exceptions. Those are source
records, not an executable profile. The full 81-cell map, deterministic motion
state precedence, global simultaneous-hit/cancellation handling, and a
universal validity window remain unclosed. `AGARWAL_SBC_2000_SOURCE_V1` is
therefore still not created, and no Agarwal material enters polarity, scores,
market mapping, Auto Suggest, ML, MT5 or execution.

## Agarwal A1R3 page-145 geometry closure

A1R3 adds four checksum-identified private photographs of printed p.145. Two
independent page-145 readings agree for all 81 source-numbered core cells,
including their literal layer labels and varga numbers. The older
`UNKNOWN_CENTER_FOLD` remains in the historical A1R2 packet but is superseded
for current core-map readiness by
`AGARWAL_2000_PAGE145_GEOMETRY_TWO_PASS_V1`.

This closes an auditable, read-only Geometry/Strength Inspector scope only. It
does not make a Vedha operator, source profile, polarity output, financial
mapping, score, market rule, Auto Suggest, ML, MT5, or execution path.

## Agarwal A2 Geometry/Strength Inspector

PFR-V2B-R6-SBC-A2 adds the founder-visible adapter contract
`AGARWAL_GEOMETRY_STRENGTH_INSPECTOR_V1`. It renders the committed A1R3
`AGARWAL_PAGE145_CORE_9X9_V1` fixture and the two-pass source-strength packet
without copying source cells into a second frontend table. The profile is
explicitly labelled `MODERN_PRACTITIONER_SOURCE`, remains isolated from
Phaladeepika and Trailokya, and does not enter synchronized Fields computation.

The UI shows `VEDHA DEPENDENCY_NOT_READY`; no rays are drawn. Chapter 20 stays
`FINANCIAL_HYPOTHESIS_LEDGER_ONLY`, and all polarity, score, market, Auto
Suggest, ML, MT5 and execution paths remain disabled. Private page photographs
are not bundled or exposed; only their source IDs, page locators and hashes
remain in the derived evidence packet.
