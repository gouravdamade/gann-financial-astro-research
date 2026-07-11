# BPHS And Phaladeepika Source Review

Date: 2026-07-11

## Decision

Both editions are admitted to the private local RAG corpus with edition-specific authority labels. Neither source changes deterministic astrology calculations, ML labels, trading rules, Auto Suggest, or MT5 execution.

## BPHS 1899 Witness

- Source ID: `BPHS`
- Title: `Brihat Parashara Hora Shastra, Purva and Uttara Khanda`
- Edition: Mumbai, 1899
- Languages: Sanskrit root/commentary and Hindi exposition; no English translation
- PDF pages: `745`
- PDF SHA-256: `BB556804D8D546ACC39C43A22CECDBE2C29E3A7BA157E60EEC810C478EB645A4`
- OCR XML MD5: `DEF54500C55D90791CA8AA38BC4E1F38`
- Rights basis: the 1899 publication is public domain; the archive item uses CC0 and the page watermark says `In Public Domain`.

The scan identifies Sridhara Jatashankara's Sanskrit commentary and Govinda Sharma Shastri's editorial/correction role. It contains both Purva and Uttara material. It is deliberately labeled a recension witness because modern BPHS editions do not all have the same chapter count or textual organization.

Retrieval lock: an English doctrinal statement may not be attributed to this edition unless a human or identified translation verifies the Sanskrit/Hindi passage. The agent must cite the PDF page and retain the Purva/Uttara identity rather than silently merging it with a modern 97-chapter translation.

Visual checks:

- PDF page 4: title/edition lineage is legible; physical leaf damage is visible.
- PDF page 30: start of the substantive Purva material is legible.
- PDF page 326: Uttara material and chapter transition are legible.
- PDF pages 665 and 741: later Uttara text remains readable, though page condition varies.

OCR quality: adequate for Devanagari retrieval and page discovery, not adequate for unsupervised translation. All 745 OCR page objects were retained.

## Phaladeepika 1937 Edition

- Source ID: `PHALADEEPIKA`
- Title: `Mantreswara's Phaladeepika`
- Translator: Panditabhushana V. Subrahmanya Sastri
- Edition: first edition, Aruna Press, Bangalore, 1937
- Languages: Sanskrit and English
- PDF pages: `476`
- PDF SHA-256: `795DDB67D7416188B2272D2021B2B798561FAAAC08067A986AF0FACFD0552FCB`
- OCR XML MD5: `46AEDA92C571651B9F8F96416EFF1A3A`
- Structure: 28 adhyayas, descriptive contents, verse indexes, and English subject index.

Rights caveat: the Digital Library of India catalog explicitly says `In Public Domain`, while the scanned title page says `Copyright Registered`. The corpus therefore records `repository_asserted_public_domain_historical_edition`, preserves the conflict on every page block, and treats the extraction as local research material. Redistribution requires a fresh rights review.

Visual checks:

- PDF page 6: title, translator and edition identity are legible; the copyright notice is visible.
- PDF page 38: Adhyaya I begins with Sanskrit and English translation.
- PDF page 80: Bhava/Drigbala discussion is legible.
- PDF page 229: Adhyaya XIX Dasa discussion is legible.
- PDF page 360: Adhyaya XXVIII and the author's chapter summary are legible.
- PDF page 394: English subject index begins and provides usable locators.

OCR quality: good for English retrieval and acceptable for page discovery. Sanskrit OCR is noisier and must be checked against the page image for exact quotation. Of 476 OCR objects, 464 non-empty pages were retained; the 12 skipped objects are blank/front/trailing leaves.

## Corpus Controls Added

Each generated page block now records:

- `LANGUAGE`
- `RECENSION`
- `RIGHTS_BASIS`
- `RETRIEVAL_CAUTION`
- PDF page, content layer, topics, edition, translator, and authority

The topic normalizer was corrected to preserve Unicode letters. Before this fix, Devanagari keywords normalized to empty strings and falsely matched every topic on every BPHS page. A regression test now covers Sanskrit topic matching and empty-pattern rejection.

## Retrieval Verification

- BPHS generated text: `745` page blocks, about `3.46 MB`.
- Phaladeepika generated text: `464` page blocks, about `1.10 MB`.
- Rebuilt index: `4,565` chunks total.
- BPHS: `1,351` chunks.
- Phaladeepika: `684` chunks.
- A Devanagari query for Dasha/graha/bala/Ashtakavarga returned BPHS in all top-six results.
- An English query for Phaladeepika strength/Drigbala/Dasa/transit returned Phaladeepika as the first two results.
- Case 43 no-LLM smoke still returned structured rule-note evidence plus page-cited doctrine/reference material.

## Promotion Policy

1. Root passages inform explanation and doctrine comparison only.
2. Translator notes remain translator notes and are not silently presented as Mantreswara's verse.
3. BPHS recension disagreements must be surfaced, not averaged.
4. Any formula promoted into deterministic code needs a verse/page citation, an independent source cross-check, a calculator fixture where applicable, and regression tests.
5. Historical natal rules do not become USDJPY/BTC trading rules without a separately stated market hypothesis and leakage-safe walk-forward evidence.

