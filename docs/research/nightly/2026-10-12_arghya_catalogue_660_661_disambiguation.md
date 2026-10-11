# Arghya edition provenance — catalogue entry disambiguation (2026-10-12)

**Gate:** `ARGHYA_1951_TITLE_WRAPPER_AND_CONTIGUOUS_LEAF_ACQUISITION`
**Status:** `RESEARCH_ONLY / UNRESOLVED`
**Source verdict:** `ARGHYA_EDITION_IDENTITY_NOT_CLOSED`
**Live branch baseline verified:** `6aa563b22eb4b342595dd4f0e8d594e84bf5b157` on `research/nightly-project-work` (supersedes expected `ed76e49b08968c59a15de92d66602cd5fbc640f8`).

## Why this targeted pass matters

The 2026-10-08 acquisition authenticated seven private printed Bombay silver worked-example leaves, pp.61–67, dated 12 and 14 May 1951. Those pages do not disclose their edition/imprint or complete Arghya calculation. The 2026-10-11 locally prepared catalogue packet (not present on the live branch at the start of this pass) identified Bhandarkar catalogue pp.120–121, a 1940 Lahore printing, and a UPenn commentary record as possible *bibliographic leads*, not witnesses to the 1951 worked example. This pass resolves a narrower catalogue ambiguity, not the source calculation.

## New targeted catalogue disambiguation

P. D. Navathe, *Descriptive Catalogue of the Government Collections of Manuscripts*, vol. III, Bhandarkar Oriental Research Institute, 1991, Jain Quantum online catalogue images/transcription:

- **Catalogue viewer p.119** (https://jainqq.org/explore/018106/119) introduces **Narapati/Narapatijayacarya, No. 660**, a **16-leaf** item. This is the item whose descriptive entry continues onto the following viewer page.
- **Catalogue viewer p.120** (https://jainqq.org/explore/018106/120) explicitly describes the **No. 660** manuscript as containing the **Sarvatobhadra Chakra**, with text and Jayalakshmi commentary; it quotes the text opening `अथातः संप्रवक्ष्यामि चक्रं त्रैलोक्यदीपक ...` and a closing reference to the Sarvatobhadra section. **No. 661** begins separately at the bottom of that viewer page.
- **Catalogue viewer p.121** (https://jainqq.org/explore/018106/121) continues **No. 661**, a different incomplete **154-leaf** Narapatijayacarya manuscript containing chapters 1–5 and a fifth-chapter colophon naming `बलाबलाध्यायः पंचमः`. Its fifth *chapter* cannot be equated with the FAQ's fifth *part* `Arghakand` without direct evidence.

**New acquisition refinement:** Request catalogue manuscript **No. 660** for a source-lineage Sarvatobhadra text/commentary witness, while keeping **No. 661** separately identified. Do not request No. 661 as though its fifth chapter were a proven Arghakand or the 1951 printed calculations. The preceding catalogue-page connection makes the No. 660 request more precise than the 2026-10-11 record.

**Image limit:** Viewer text was read directly. The catalogue-page JPEG link returned an unsupported binary response in the available browser, so **the entry-number typography was not independently verified from the catalogue page image in this run**. The catalogue is secondary bibliographic metadata; no claim about a primary Sanskrit digit, arithmetic or verse is based on that unverified image.

## Other catalogue leads rechecked (not promoted)

- The 1940 Lahore *Narapatijayacaryasvarodaya* printing (Open Library OL47950001M, https://openlibrary.org/books/OL47950001M/Narapatijayacary%C4%81svarodaya%E1%B8%A5) has Jayalakshmi and Narahari commentary attribution; the catalogued copy lacks material after p.120. It is **not** identified with the 1951 silver pp.61–67.
- UPenn Ms. Coll. 390 Item 1833 (https://samhitadev.iicdelhi.in/manuscripts/jayalaksmitika-commentary-on-narapatijayacaryasvarodaya-ms-coll-390item-1833) is an incomplete 34-folio Jayalakshmi commentary record, **not** the 1951 printed edition.
- The modern SBC FAQ's 1934–1952 Varanasi-serial assertion remains a secondary lead without a named title/imprint/issue tied to the printed 1951 pages.

## Direct source pages and non-acquisition

Newly read **catalogue viewer pp.119–121** (not controlling Trailokya pages). No original 1951 printed leaf, title wrapper, missing continuation or primary manuscript page was newly acquired or visually inspected. The seven 1951 page photographs are **inherited** from the 2026-10-08 packet and were not mounted here. The controlling Trailokya TD1 1972 scan pp.32–36 / printed pp.16–20 (vv.65–80) and 2016 witness pp.23–27 were not re-inspected: TD1 was already boundedly exhausted on 2026-10-08.

## Outcome, stop rule and source-contract implications

```text
ARGHYA_CATALOGUE_NO_660_SARVATOBHADRA_ENTRY = BIBLIOGRAPHIC_LEAD_TEXT_VERIFIED_IMAGE_PENDING
ARGHYA_CATALOGUE_NO_661_FIFTH_CHAPTER = BALABALA_NOT_PROVEN_ARGHAKAND
ARGHYA_1951_EDITION_IDENTIFIED = false
ARGHYA_1951_CONTIGUOUS_CALCULATION_ACQUIRED = false
ARGHYA_COMPLETE_WORKED_CALCULATION_LOCATED = false
ARGHYA_FOUR_STRENGTH_COMPOSITION_CLOSED = false
ARGHYA_SCORE_TO_PRICE_CONVERSION_CLOSED = false
TD3R_ARGHA_SOURCE_CALCULATOR_READY = false
MATHEMATICAL_ADJUDICATION = NOT_PERMITTED_INCOMPLETE_SOURCE_CHAIN
```

Do not conflate No. 660, No. 661, the 1940 edition, the 1972 Trailokya witness or the unidentified 1951 silver worksheets. No score, forecast, modern commodity-price equation, source-ledger amendment or production behavior is authorized. The only potential future work is **human-reviewed, separately scoped source acquisition**, with image-level provenance, printed and scan page locators and SHA-256 evidence. Any modern ephemeris or financial mapping would require a separate labelled research profile, not direct Trailokya authority.

**Next single target:** `ARGHYA_1951_TITLE_WRAPPER_AND_CONTIGUOUS_LEAF_ACQUISITION`: a title/imprint or issue physically associated with printed pp.61–67 and the continuous preceding/following calculation pages. In parallel only if access is actually available, verify catalogue No. 660 against its page image and request that manuscript as *contextual* Sarvatobhadra evidence. Do not resume generic searches without new primary material.

Inherited TD1 verdicts unchanged:
```text
TRAILOKYA_EXACT_SPEED_THRESHOLD = NOT_SOURCE_CLOSED
TRAILOKYA_STATIONARY_STATE = SOURCE_SILENT_OR_EXTERNALLY_DELEGATED
TRAILOKYA_ATICARA_UNIT = UNKNOWN_AFTER_BOUNDED_REVIEW
```

```text
SOURCE_CONTRACTS_CHANGED = false
RUNTIME_BEHAVIOR_CHANGED = false
MARKET_DIRECTION = WITHHELD
MARKET_MAGNITUDE = WITHHELD
OSCILLATOR_AMPLITUDE = WITHHELD
PROVIDER_OUTCOME_ACCESS = false
executionAllowed = false
```
