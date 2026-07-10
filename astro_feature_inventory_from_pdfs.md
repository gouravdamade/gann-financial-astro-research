# Astro Feature Inventory From Attached PDFs

Created from the project PDFs supplied on 2026-05-04 and updated with the Shad Bala PDF supplied on 2026-05-05. The strict-Jyotish PDFs are treated as architecture/doctrine-control documents. The financial astrology PDFs are treated as experimental feature sources until validated out of sample.

## Source IDs

| Source ID | File | Extraction status | Role |
|---|---|---:|---|
| STRICT_JYOTISH_ML | `Strict Jyotish Prediction Engine with Local LLM & ML Calibration2.pdf` | readable text, 11 pages | Core architecture and validation discipline |
| STRICT_VEDIC_LLM | `Building a Strict Vedic Astrology Prediction Engine with a Local LLM Layer.pdf` | readable text, 9 pages | Core architecture, rule layer, RAG/LLM separation |
| ASTROECON | `pdfcoffee.com_financial-astrology-pdf-free.pdf` | readable text, 104 pages | Experimental financial astrology feature rules |
| FUTURETEK_DHRUVANK | `pdfcoffee.com_futuretec-financial-astrology-set-2-dhruvank-pdf-free.pdf` | readable text, 17 pages | Experimental daily Dhruvank feature |
| GANN_VOL2 | `pdfcoffee.com_gann-financial-astrology-pdf-free.pdf` | OCR text, 177 pages, about 210k chars | Experimental Gann price/time/longitude feature source; verify page OCR before implementation |
| SHADBALA_JAYA | `jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf` | readable text, 179 pages | Detailed Shadbala doctrine/reference |
| PADMANABHAN_TIMING | `Timing of Events - A Qualitative and Quantitative Study`, R. A. Padmanabhan | photographed first page (p14) only; continuation/Table 2 unavailable | Experimental Gochara + Dasha/Bhukti quantitative framework |
| KRUSHNA_KAS_TIMING | `Timing of Events: A Research Work in Astrology with Krushna Ashtakvarga System`, Krushna Jugalkalani | readable text, 185 pages; original worksheets contain later-corrected calculations | Experimental classical Ashtakavarga evidence plus quarantined KAS-specific timing hypotheses |
| PHALADEEPIKA_26 | Phaladeepika Chapter 26 | complete online translation checked; OCR caveat | Classical Moon-based Gochara and Vedha rules |

Extracted text folder:

`D:\GannFinancialAstro\doc\pdf_text_extracts`

## Doctrine And Architecture Locks

| ID | Requirement | Source | Implementation status |
|---|---|---|---|
| LOCK_TIME_UTC | Internal calculations must standardize timestamps to UTC/JD UT and preserve display timezone separately. | STRICT_JYOTISH_ML p1-p2, STRICT_VEDIC_LLM p3 | Mostly aligned: existing logs carry local/UTC columns. Needs config record in output metadata. |
| LOCK_DOCTRINE_CONFIG | Version ayanamsa, zodiac, graha set, node type, drishti/aspect method, ephemeris path. | STRICT_JYOTISH_ML p1-p4, STRICT_VEDIC_LLM p3-p4 | Foundation added: `doctrine_config.yaml` plus output metadata columns. Still needs exact ayanamsa policy review and rule citations. |
| NO_LLM_IN_LOGIC | LLM must not compute ephemeris, aspects, labels, or trades; explanation only. | STRICT_JYOTISH_ML p1, p5-p7; STRICT_VEDIC_LLM p1-p3 | Not implemented yet; future RAG layer only. |
| RULES_WITH_CITATIONS | Every doctrine/interpretation rule should carry source/page metadata. | STRICT_JYOTISH_ML p3-p5; STRICT_VEDIC_LLM p5-p6 | New feature inventory starts this. Code rules still need citation fields. |
| ML_CALIBRATION_SCOPE | ML may tune weights, thresholds, windows, and interactions, not invent astrology. | STRICT_JYOTISH_ML p6-p8; STRICT_VEDIC_LLM p6-p8 | Trade candidate file exists; purged walk-forward and anti-overfit checks remain. |
| PURGED_WALK_FORWARD | Evaluate chronological folds with purge/embargo around overlapping labels/events. | STRICT_JYOTISH_ML p6-p8 | Not implemented. Required before trusting ML. |

## Existing Pipeline Mapping

| Existing component | Current role | PDF alignment | Gap |
|---|---|---|---|
| `build_aspect_sr_touch_log.py` | Deterministic aspect/SR touch event creation | Fits deterministic core + event layer | Needs explicit doctrine/config metadata and source-rule IDs |
| `sr_touch_lazy_dashboard.py` | Visual inspection: M30/H1/daily/merged/switch | Fits timeframe separation: short triggers vs longer influences | Weekly mode pending; daily still capped at 5 days by builder and loader |
| `build_trade_candidates_from_touches.py` | Creates ML-ready trade outcomes | Fits ML calibration input | Needs purged walk-forward model/evaluation script |

## Feature Inventory

| Feature ID | Bucket | Timeframe | Signal intent | Inputs needed | Source | Status |
|---|---|---|---|---|---|---|
| ASP_HARD_EVENT | Experimental financial astrology | M30/H1/daily | Potential trend change / volatility | Aspect type in conjunction, square, opposition; event duration; active count | ASTROECON p24-p25 | Already partially present via orb aspects; add feature flags |
| ASP_SOFT_EVENT | Experimental financial astrology | M30/H1/daily | Continuation / inertia / stability | Aspect type in sextile, trine; event duration; active count | ASTROECON p25-p26 | Already partially present via orb aspects; add feature flags |
| ASP_DURATION_BUCKET | Architecture-derived | M30/H1/daily/weekly | Separates trigger vs higher-timeframe influence | `event_duration_minutes` | ASTROECON p4-p5; STRICT_JYOTISH_ML validation design | Implemented for M30/H1 <= 24h, daily > 24h <= 5d |
| ASP_MULTIPLE_ACTIVE | Experimental financial astrology | M30/H1/daily | More important when multiple aspects/patterns coincide | `aspect_regime_active_count`, event signatures | ASTROECON p34-p40; STRICT_JYOTISH_ML p7-p8 | Partially present in trade candidate category |
| SR_TOUCH_CONFIRMATION | Experimental financial astrology + technical filter | M30/H1/daily | Treat aspect time as actionable only near support/resistance | Touch log, line identity, touch kind, distance | ASTROECON p4-p5, p52-p53 | Implemented as confluence/nearest_line touch rows |
| MOON_FAST_TRIGGER | Experimental financial astrology | M30/H1 only | Fast-moving Moon can trigger short-term mood/turn timing | Moon involvement in event or SR line identity | ASTROECON p4-p5, p52-p53 | Present in data; hidden only from daily SR lines |
| SLOW_PLANET_CONTEXT | Experimental financial astrology | Daily/weekly | Higher-timeframe influence from slow planets | Outer planet pairs, duration, active count | ASTROECON p4-p5, p58-p59 | Partial: daily >24h; weekly pending; Uranus/Neptune/Pluto lines included |
| STELLIUM_PATTERN | Experimental financial astrology | Daily/weekly | Clustered conjunctions may indicate major cycle/turn risk | Count of planets within degree span; span degrees; involved bodies | ASTROECON p34-p35 | Not implemented |
| T_SQUARE_PATTERN | Experimental financial astrology | Daily/weekly | Stress configuration; volatility/trend-change candidate | One opposition plus squares from focal planet | ASTROECON p36-p37 | Not implemented |
| GRAND_CROSS_PATTERN | Experimental financial astrology | Daily/weekly | Strong stress configuration; volatility/trend-change candidate | Two oppositions and four squares among 4 bodies | ASTROECON p36-p37 | Not implemented |
| GRAND_TRINE_PATTERN | Experimental financial astrology | Daily/weekly | Trend continuation / inertia | Three trines in triangular pattern | ASTROECON p37-p38 | Not implemented |
| YOD_PATTERN | Experimental financial astrology | M30/H1/daily | Focused turning-point candidate, especially near SR | Sextile base plus focal opposition/quincunx-style focus or midpoint focus | ASTROECON p38-p39, p52-p53 | Not implemented |
| MIDPOINT_DIRECT_HIT | Experimental financial astrology | M30/H1/daily/weekly | Important when a planet directly contacts midpoint/opposite midpoint | Planet longitudes; midpoint pairs; orb/time window | ASTROECON p58-p59 | Not implemented |
| GANN_PRICE_LONGITUDE_HIT | Experimental Gann financial astrology | M30/H1/daily/weekly | Planetary longitude converted to price can mark support/resistance/turning points | Planet geocentric/heliocentric longitude; price scale; modulo/add-360 price mapping; touch distance | GANN_VOL2 OCR p11-p14, p19-p20 | Not implemented; requires scale policy and page verification |
| GANN_OUTER_PLANET_AVERAGE | Experimental Gann financial astrology | Daily/weekly | Average geocentric/heliocentric longitudes of outer planets may define time/price resistance zones | Mars/Jupiter/Saturn/Uranus/Neptune/Pluto longitudes; smoothed 0/360 crossing handling; price conversion | GANN_VOL2 OCR p20-p30 | Not implemented; higher-timeframe feature candidate |
| GANN_CIRCLE_ACTIVE_ANGLE | Experimental Gann financial astrology | Daily/weekly | Circle Chart / active-angle projections can mark future time periods and resistance levels | Circle chart degree grid; selected origin; projected time periods; price/resistance levels | GANN_VOL2 OCR p7-p10, p34+ | Not implemented; needs rule extraction |
| ANGULAR_INTRADAY_HIT | Location-specific experimental feature | M30/H1 | Intraday timing when planets hit Asc/MC/Desc/IC for market location | Exchange location; house/angle calculation; planet angular hit times | ASTROECON p52-p53, p65+ | Not implemented; requires location policy |
| DHRUVANK_REMAINDER_SIGNAL | Experimental Vedic financial astrology | Daily/weekly | Rise/fall/no-change signal from Dhruvank remainder | Commodity/share code, city, nakshatra, tithi, weekday, lunar month, sun sign, yoga | FUTURETEK_DHRUVANK p2-p17 | Not implemented |
| JYOTISH_NAKSHATRA_PADA | Strict Jyotish core feature | All | Feature/context only until rulebook exists | Sidereal longitude mapped to 27 nakshatras and 4 padas | STRICT_JYOTISH_ML p3 | Not implemented as reusable feature table |
| BPHS_DRISHTI_STRENGTH | Strict Jyotish core feature | All | Doctrine feature, not Western orb | BPHS drishti virupa/rupa/strength norm | STRICT_JYOTISH_ML p2-p4 | Existing script has BPHS-like fields; verify against doctrine |
| SHADBALA_GATE | Strict Jyotish core feature | Daily/weekly initially | Strength filter/context for rule layer | Shadbala totals/components and thresholds | STRICT_JYOTISH_ML p3, STRICT_VEDIC_LLM p4, SHADBALA_JAYA p23-p101 | Foundation partial: `shadbala_doctrine.py` adds seven-classical minimum total thresholds and basic Sthana sign dignity context. Full six-bala calculation still pending. |
| PADMANABHAN_TIMING_INDEX | Experimental source-bounded Jyotish | All | Compare reference-chart Gochara plus Dasha/Bhukti intensity for USD versus JPY | Natal Moon, transit longitudes, Vimshottari periods, six-Rupa Shadbala gate | PADMANABHAN_TIMING p14 partial; PHALADEEPIKA_26 v1-v8, v33-v34 | Implemented evidence-only in `padmanabhan_timing_doctrine.py`; article continuation, Table 2, temporal quality, Yogakaraka weights, external calculator validation, and walk-forward promotion remain pending. |
| CLASSICAL_ASHTAKAVARGA_TRANSIT | Classical Jyotish evidence | Daily/weekly initially | Measure transit sign support without assigning trade direction | Seven-classical BAV/SAV tables, transit signs, ayanamsa and BAV convention | KRUSHNA_KAS_TIMING lessons 1-4; Phaladeepika Chapter 23; Brihat Jataka Chapter 9 | Implemented only in isolated `research_labs/ashtakavarga_validation`; internal fixture/invariants pass, but two independent calculator checks remain pending and no main-pipeline integration exists. |
| KRUSHNA_DAILY_SAV_INDEX | Experimental KAS evidence | Daily/weekly | Seven transiting classical planets' natal-SAV context centered on 196 | Natal SAV by sign and seven classical transit signs | KRUSHNA_KAS_TIMING lesson 11 | Implemented/evaluated only in isolated lab. First USDJPY walk-forward did not distinguish the simple differential from chance; remains evidence-only and disconnected from trades. |
| KRUSHNA_JS_TRANSIT_SUM | Experimental KAS evidence | Daily/weekly | Jupiter-Saturn cash-flow context centered on eight bindus | Natal BAV/SAV convention, Jupiter/Saturn transit signs and bindus | KRUSHNA_KAS_TIMING lesson 35 | Implemented/evaluated only in isolated lab as each planet's own-BAV value in its transit sign. First USDJPY result was near chance; no main-pipeline integration. |
| KRUSHNA_EVENT_WORKSHEET | Quarantined KAS-specific hypothesis | Event-dependent | Rank event significators and propose Dasha timing | Corrected A/B/C/D/E houses, inverse aspects, Samdharmi transfers, D/E bonuses, Vimshottari periods | KRUSHNA_KAS_TIMING lessons 5-10 and later corrected Lesson 7 | Not implemented. Original PDF arithmetic is obsolete in places; exact corrected spec, source-reproduction tests and walk-forward ablation are required. |

## Priority Implementation Plan

1. Add explicit feature columns to `build_trade_candidates_from_touches.py` from fields already available:
   `aspect_hard_soft`, `duration_bucket`, `is_multiple_active`, `has_moon_trigger`, `has_outer_planet`, `sr_confirmation_type`.

2. Extend the doctrine/config metadata block to all generated logs and review exports:
   ephemeris source, zodiac/coordinate system, aspect mode, node mode, SR planets, max event days.

3. Build a first ML evaluation script with purged walk-forward splits over `trade_candidates_aspect_sr_1y_outer.parquet`.

4. Only after baseline ML/evaluation works, add new pattern detectors:
   midpoint direct hits, stellium, T-square/grand-cross/grand-trine, then Dhruvank daily feature.

5. Gann OCR is now available at `D:\GannFinancialAstro\doc\pdf_text_extracts\pdfcoffee.com_gann-financial-astrology-pdf-free.ocr.txt`; do not implement Gann rules until each rule is manually checked against the page OCR/source image and given source IDs.

## Notes For Weekly Extension

The current pipeline filters events above 5 days in both the builder and dashboard loader. Weekly analysis requires raising or removing that cap and then adding a new duration bucket, for example:

| Bucket | Proposed range | Chart |
|---|---:|---|
| trigger | `<= 24h` | M30/H1 |
| swing | `> 24h` and `<= 5d` | Daily |
| position | `> 5d` | Weekly |

Do not add weekly until the 5-day cap is made configurable end-to-end and validated.
