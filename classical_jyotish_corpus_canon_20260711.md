# Classical Jyotish Corpus Canon For The Local Agent

## Purpose

This canon ranks sources by function and authority so the local LLM can retrieve broad Jyotish knowledge without presenting every book as equally authoritative. It is a research corpus plan, not a claim that astrology has established predictive validity.

## Authority layers

### Layer A - calculation and historical astronomy

These sources explain historical calendrical and astronomical frameworks. Swiss Ephemeris and versioned deterministic code remain the operational calculator.

| Source | Why needed | Initial lawful source candidate |
|---|---|---|
| Surya Siddhanta | Classical astronomy, time and longitude concepts | [GRETIL Sanskrit](https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/6_sastra/8_jyot/surysidu.htm); [1860 English scan](https://commons.wikimedia.org/wiki/File%3ATranslation_of_the_S%C3%BBrya-Siddh%C3%A2nta%2C_A_Text-Book_of_Hindu_Astronomy%3B_With_Notes%2C_and_an_Appendix_%28IA_jstor-592174%29.pdf) |
| Panchasiddhantika | Cross-check of historical astronomical schools | [1889 catalog/scan record](https://openlibrary.org/books/OL24597611M/The_Panchasiddhantika) |
| Vedanga Jyotisha | Early calendrical context | Edition and translator must be verified before ingestion |

### Layer B - root predictive canon

These are the first sources to consult for planet, sign, house, dignity, Yoga and predictive doctrine. Ideally retain a Sanskrit text plus one identified translation; never merge unattributed translations into a single synthetic quote.

| Priority | Source | Main role | Initial source candidate |
|---:|---|---|---|
| 1 | Brihat Parashara Hora Shastra | Parashari houses, grahas, Vargas, strength and Dashas | Ingested 2026-07-11: 1899 Sanskrit-Hindi Purva/Uttara witness; recension-specific and not an English translation |
| 1 | Brihat Jataka | Compact foundational predictive cross-check | [1905 public-domain English scan](https://commons.wikimedia.org/wiki/File%3AThe_Brihat_jataka_%28IA_brihatjataka00varaiala%29.pdf) |
| 1 | Saravali | Broad planet, sign and house condition corpus | Manual edition review through the [classical library index](https://dekhopanchang.com/en/learn/library) |
| 1 | Phaladeepika | Practical interpretation, strength, transit and Ashtakavarga context | Ingested 2026-07-11: 1937 Subrahmanya Sastri first edition; DLI public-domain assertion conflicts with title-page copyright notice, so local-only pending rights review |
| 2 | Jataka Parijata | Cross-source synthesis and exceptions | Public-domain edition/translation still requires language and metadata review |
| 2 | Hora Sara | Compact additional cross-check | Manual edition review |
| 2 | Uttara Kalamrita | Specialized rules and exceptions | Manual edition review |

### Layer C - timing and Jaimini corpus

| Priority | Source | Main role | Initial source candidate |
|---:|---|---|---|
| 1 | Jaimini Upadesa Sutras | Karakas, Arudha, Argala and Jaimini Dasha foundations | [Open Library catalog](https://openlibrary.org/books/OL19543900M/Jaimini_Maharishi%27s_Upadesa_sutras); edition review required |
| 1 | Laghu Parashari | Yogakaraka and period-result rules | Manual edition review |
| 2 | Sarvartha Chintamani | House-specific event results and timing context | [Classical library index](https://dekhopanchang.com/en/learn/library) |
| 2 | Prasna Marga | Event/question judgment and contextual synthesis | Manual edition review; lower priority for automated market use |
| 2 | Muhurta Chintamani | Panchanga and electional timing context | Manual edition review |
| 3 | Tajika Nilakanthi | Annual-chart and Tajika aspect/timing framework | Manual edition review; keep separate from Parashari drishti |

### Layer D - mundane and financial-context classics

| Priority | Source | Main role | Initial source candidate |
|---:|---|---|---|
| 1 | Brihat Samhita | Mundane phenomena and collective-event context | [GRETIL Sanskrit](https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/6_sastra/8_jyot/brhats_u.htm); [1884 public-domain English scan](https://commons.wikimedia.org/wiki/File%3AThe_B%E1%B9%9Bihat_sa%E1%B9%83hit%C3%A2_of_Varaha_Mihira_%28IA_b29353130%29.pdf) |
| 2 | Yoga Yatra | Mundane/journey timing context attributed to Varahamihira | Locate and certify a traceable edition before ingestion |
| 3 | Daivajna Vallabha | Prasna/event context | Locate and certify an edition before ingestion |

This layer is more relevant to markets than treating a natal marriage or mortality rule as a trading signal, but it still requires explicit market hypotheses and walk-forward testing.

### Layer E - modern commentary and experimental methods

These sources may explain, compare or suggest tests. They do not overrule root texts or empirical failures.

| Source | Corpus role |
|---|---|
| Sanjay Rath, `Crux of Vedic Astrology - Timing of Events` | Secondary interpretive synthesis and timing-method map |
| B. V. Raman commentaries | Identified modern interpretive editions |
| K. Jaya Sekhar Shadbala paper | Component-use guidance pending calculator certification |
| R. A. Padmanabhan timing article | Source-incomplete experimental index |
| Krushna Jugalkalani KAS manual | Quarantined experimental Ashtakavarga hypotheses |
| Workspace manual reviews and rule lessons | Empirical local evidence, not scripture |

## Required ingestion metadata

Every corpus item must record:

- stable `source_id`;
- author/tradition, title, edition, translator and publication year when known;
- language and whether text is OCR;
- rights/access status and local-only restriction;
- PDF/page/verse locator;
- authority layer;
- doctrine family and configuration assumptions;
- whether a passage is root text, translator note, commentary, worked example or workspace hypothesis.

## Retrieval and answer policy

1. Retrieve root doctrine before modern commentary when both discuss the same feature.
2. Return disagreements rather than silently averaging them.
3. Cite page or verse. If the locator is missing, say so.
4. Keep Parashari graha drishti, Jaimini Rasi drishti, Tajika aspects and the workspace's astronomical aspect windows as separate fields.
5. Never let an LLM calculate ephemeris, Dasha dates, Shadbala, Ashtakavarga, trade direction or P/L.
6. Treat modern worked examples as explanation data, not model labels.
7. Use completed reviewed cases for calibration only after leakage-safe chronological evaluation.

## Acquisition order

1. Completed 2026-07-11: Brihat Jataka, Brihat Samhita and Surya Siddhanta public-domain historical editions with page markers and edition hashes.
2. Completed 2026-07-11: recension-labeled 1899 BPHS Sanskrit-Hindi witness and 1937 Phaladeepika Sanskrit-English edition with explicit rights conflict and retrieval cautions.
3. Next: Saravali and Jataka Parijata.
4. Jaimini Upadesa Sutras and Laghu Parashari.
5. Sarvartha Chintamani, Muhurta Chintamani and Prasna Marga.
6. Tajika and additional mundane texts only after their doctrine namespaces exist.

This order gives the agent a broad but controlled foundation before adding more modern interpretations.
