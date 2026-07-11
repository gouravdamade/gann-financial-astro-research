# Classical Text Ingestion Review

## Scope

This checkpoint ingests three traceable public-domain historical English editions into the local Jyotish RAG corpus:

1. `The Brihat Jataka` of Varahamihira, translated by N. Chidambaram Aiyar, second edition, 1905.
2. `The Brihat Samhita of Varaha Mihira`, translated by N. C. Iyer, Parts I-II, 1884-1885.
3. `Translation of the Surya-Siddhanta`, translated by Ebenezer Burgess with the Committee of Publication, 1858.

The PDF scans and Internet Archive DjVu OCR XML are archived under:

`D:\GannFinancialAstro\sources\classical`

Generated page-marked corpus text stays local and uncommitted under:

`D:\PycharmProjects\jyotish_agent\corpus_text`

## Edition and integrity records

| Source ID | PDF pages | PDF SHA-256 | Authority label |
|---|---:|---|---|
| `BRIHAT_JATAKA` | 306 | `CEAFC2FE3E385FB834B94FA4F464406DA3BA42AB01B3A2AC42A2749ABDA9F1D9` | Root classical text in a historical translation with translator notes |
| `BRIHAT_SAMHITA` | 496 | `9E0E8B4DD7D611F22B29ED65B7ED635D806D831407B27695D8128EB804983E27` | Root classical mundane text in a historical translation with translator notes |
| `SURYA_SIDDHANTA` | 362 | `B555C7EAABF8F167CFAE4177180090059451610F547C1FB4A197A0B28DED41FA` | Classical astronomy in a historical translation with scholarly notes and calculations |

The source pages identify the editions as public domain. OCR was taken from the corresponding Internet Archive page-structured DjVu XML rather than relying on degraded embedded PDF text. Representative title, chapter and doctrine pages were visually checked against the scans.

The edition registry also pins each PDF SHA-256 and Internet Archive OCR XML MD5. `ingest_classical_sources.py` refuses to rebuild a source when either configured hash changes.

## Provenance behavior

Every retained page begins with metadata including:

```text
[[SOURCE: BRIHAT_JATAKA]]
[[TRANSLATOR: N. Chidambaram Aiyar]]
[[EDITION: Second edition revised and enlarged, 1905]]
[[AUTHORITY: root_classical_text_historical_translation_with_notes]]
[[PDF_PAGE: 0045]]
[[CONTENT_LAYER: root_translation_with_translator_notes]]
```

This prevents the local LLM from presenting an introduction, translator note or appendix as though it were an unmediated Sanskrit verse. Exact doctrinal promotion still requires visual checking of the cited page and, where material, comparison with another identified edition or Sanskrit text.

## Workspace relevance

### Brihat Jataka

High-value retrieval areas include dignity, planetary strength, aspects, Vargas, Dasha and Antardasha interpretation, Ashtakavarga, Yoga, profession and wealth. Much of the book concerns natal life topics that must not be turned directly into market labels.

### Brihat Samhita

This is the most market-adjacent of the batch because it is a Samhita/mundane work. Relevant areas include planetary visibility, conjunctions, comets, rainfall, winds, crops, collective conditions, earthquakes, meteors and some commerce-related language. These are historical doctrine candidates, not demonstrated Bitcoin or USDJPY predictors.

### Surya Siddhanta

Useful retrieval areas include time divisions, mean and true planetary motion, longitude, eclipses, conjunctions, nakshatras, ascension, declination and instruments. It is historical calculation doctrine only. Operational positions, panchanga and event timestamps remain owned by Swiss Ephemeris and versioned deterministic code.

## Ingestion and retrieval result

- Retained page blocks: Brihat Jataka `295`, Brihat Samhita `489`, Surya Siddhanta `362`.
- Empty covers and trailing blank pages were excluded without renumbering the retained PDF-page citations.
- Rebuilt local index: `2,530` total chunks.
- Source chunks: Brihat Jataka `341`, Brihat Samhita `611`, Surya Siddhanta `800`.
- Missing `PDF_PAGE` or `AUTHORITY` markers in those source chunks: `0`.
- Dedicated retrieval queries returned the expected source within the top three results for all three books.
- Case-agent retrieval now reserves four slots for structured workspace evidence and four for doctrine/reference sources, preventing case notes from crowding all classical material out of the prompt.

## Safety and promotion locks

- No ingested passage can directly alter Auto Suggest, ML labels, official ML notes or MT5.
- LLM retrieval must identify source, translator, edition, page and content layer.
- Translator commentary and historical scientific claims are not root doctrine.
- Mortality, medical, fertility and gender-prediction material is out of scope for the financial agent.
- A market hypothesis derived from a classical passage must be specified before outcome inspection and pass chronological walk-forward testing.
- Disagreement between these editions, Sanskrit text and other classical authorities must be surfaced rather than averaged away.

## Source records

- Brihat Jataka: <https://commons.wikimedia.org/wiki/File:The_Brihat_jataka_(IA_brihatjataka00varaiala).pdf>
- Brihat Samhita: <https://commons.wikimedia.org/wiki/File:The_B%E1%B9%9Bihat_sa%E1%B9%83hit%C3%A2_of_Varaha_Mihira_(IA_b29353130).pdf>
- Surya Siddhanta: <https://commons.wikimedia.org/wiki/File:Translation_of_the_S%C3%BBrya-Siddh%C3%A2nta,_A_Text-Book_of_Hindu_Astronomy;_With_Notes,_and_an_Appendix_(IA_jstor-592174).pdf>
