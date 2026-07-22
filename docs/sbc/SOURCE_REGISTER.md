# SBC Source Register Notes

The machine-readable register is `configs/sbc/sources.yaml`.

## Authority Layers

| Source | Layer | Current use |
| --- | --- | --- |
| Sarvatobhadra Chakra Codex Implementation Guide | Workspace implementation specification | Architecture and phase gates only |
| Chakra and Gann source audit | Workspace source-conflict register | Prevents premature grid/rule selection |
| Panchanga formula foundation | Computational formula | Phase 1 facts only |
| Phaladeepika, Subrahmanya Sastri edition | Root translation plus editor supplement | Citation research; layers remain separate |
| Phaladeepika 1937 SBC editor supplement | Editor-supplied Horaratna extract/free rendering | Rotation-normalized 81-cell topology, construction text, letter witness, worked standard Vedha examples, nature rules, and modifiers |
| Sanjay Rath, Crux, Figure 1.2 | Modern secondary commentary | Figure-relative 81-cell coordinate frame and letter-glyph comparison |
| Sanjay Rath, Crux, printed page 11 | Modern secondary commentary | Independent motion-class comparison only |
| Trailokya Dipika 1972, Pt. Mithalal Vyas | Pending traditional candidate with lawful retail listing | Acquisition lead only; no executable use |
| Complete Agarwal edition | Pending modern candidate | Still required for whole-book and missing-page certification; no executable use |
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
publisher statement, or edition statement. Consequently, neither file
certifies the presumed 2000 edition or the book as a complete doctrinal
witness. See `docs/sbc/AGARWAL_SCAN_AUDIT_20260722.md` for the evidence and use
boundary.

One bounded exception is recorded for retrieval, not doctrine. PDF pages
177-191 contain consecutive printed pages 180-194, Chapter 20, and all fifteen
page images were visually reviewed. A private page-marked OCR extract may be
retrieved only when a question explicitly asks for Agarwal, Sarvatobhadra, or
financial/share-market hypotheses. Its claims remain modern practitioner
hypotheses for falsification and cannot affect deterministic calculations,
official ML notes, Auto Suggest, live inference, validation ledgers, or orders.
