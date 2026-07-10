# Krushna Ashtakavarga Source Review

## Source identity

- Title: `Timing of Events: A Research Work in Astrology with Krushna Ashtakvarga System`
- Author/compiler: Krushna Jugalkalani
- Edition represented by the supplied file: 2021 PDF compilation of 36 lessons originally circulated around 2000-2002
- Supplied file: `Jyotish_Jugalkalani Krushna_Timing of Events_A Research Work -- Jyotish -- 2021 -- 0c17045bdde28fcf5711cb49147576de -- Anna's Archive.pdf`
- Archived project copy: `D:\GannFinancialAstro\doc\Jyotish_Jugalkalani Krushna_Timing of Events_A Research Work -- Jyotish -- 2021.pdf` (moved from the C: Desktop after hash verification)
- Length: 185 PDF pages; readable text was recovered from 181 pages and key worksheets/diagrams were checked visually
- File size: 3,836,281 bytes
- SHA-256: `E18E021B84EE3A344EAC4DB11056D68C536B296E9D0CEFCFDBBE1B66455A9711`

This is not R. A. Padmanabhan's 1985 article `Timing of Events - A Qualitative and Quantitative Study`. It does not supply Padmanabhan's missing Table 2 or complete his `I = A + B` model. It is a different research manual built around the author's Krushna Ashtakavarga System (KAS).

## Executive verdict

The book is useful as a detailed source of **testable Ashtakavarga hypotheses**, especially:

1. classical Bhinna Ashtakavarga (BAV) and Sarva Ashtakavarga (SAV) transit features;
2. a seven-planet daily transit score centered on `196 = 7 x 28`;
3. a Jupiter-plus-Saturn transit score centered on eight bindus;
4. an event-specific worksheet that ranks significators before timing an Antardasha;
5. explicit nodal proxy rules based on sign, nakshatra and Navamsa dispositors.

It is not suitable for direct promotion into live trading logic. The PDF contains obsolete calculations, internal contradictions, retrospective rule selection, unsupported accuracy claims and many unvalidated constants. The KAS-specific mechanics must therefore be implemented, if at all, in a separate experimental namespace and evaluated against simpler classical Ashtakavarga features by purged chronological walk-forward testing.

## Classical foundation used by the book

The manual begins from recognizable Ashtakavarga structure:

- Seven classical planets have individual BAV tables; Lagna contributes bindus but does not have a planetary BAV row of its own.
- Rahu, Ketu and the outer planets are excluded from the classical BAV/SAV totals.
- The canonical row totals stated in the book are:

| Planet | BAV total |
|---|---:|
| Sun | 48 |
| Moon | 49 |
| Mars | 39 |
| Mercury | 54 |
| Jupiter | 56 |
| Venus | 52 |
| Saturn | 39 |
| **Total** | **337** |

- A sign with 28 SAV bindus is treated as a neutral reference because `337 / 12` is approximately 28.
- For a planet's own BAV at its natal or transit sign, more bindus are normally treated as greater capacity to deliver favorable results.

Phaladeepika Chapter 23 independently supports using Ashtakavarga bindus to qualify transits and treating higher bindu counts as more favorable. It does not establish the distinctive KAS inverse-aspect and worksheet rules described below.

## Distinctive KAS rules

### 1. Natal strength classification

At the planet's natal sign in its own BAV:

- more than 4 bindus: strong/beneficial;
- fewer than 4 bindus: weak/adverse;
- exactly 4 bindus: neutral.

The exact-four case matters because at least one original worksheet incorrectly awarded a positive adjustment at four; the later correction says four is neutral.

### 2. Inverse aspect rule

KAS uses a nonstandard aspect transformation:

- a strong planet with more than four bindus casts a negative aspect using its bindu value;
- a weak planet with fewer than four bindus casts a positive aspect using `8 - bindus`;
- a planet at exactly four is neutral.

This is not a standard conclusion established by the classical cross-check. It must be tagged `krushna_specific_hypothesis`, never presented as a universally accepted Ashtakavarga doctrine.

### 3. Event-house rotation

For an event represented by house `B`, the worksheet constructs a rotating set of event houses:

- `A`: eighth from B;
- `C`: tenth from A;
- `D`: third from A;
- `E`: eleventh from A.

The lords and occupants of A, B and C form the primary significator pool. D and E act as secondary/upachaya helpers. Because these labels change with the selected event, the event definition must be fixed before any outcome is inspected to avoid retrospective house selection.

### 4. Significator worksheet

The broad worksheet process is:

1. Sum each classical planet's relevant BAV bindus across houses A, B and C.
2. Apply 4:10 `Samdharmi` transfers between eligible planets.
3. Add the specified D/E bonus, commonly five points, to eligible D/E lords or occupants.
4. Apply KAS aspect additions and deductions to event houses and significator planets.
5. Rank all seven classical planets.
6. Treat a score around 12 or above as an eligible/strong event significator.

The constants and transfer rules are authored KAS rules, not derived statistical quantities. The supplied original lesson also contains superseded arithmetic; any implementation must follow the later corrected specification and retain an audit trail for every term.

### 5. Dasha timing

The event is expected particularly during the Antardasha of:

- a highly ranked event significator;
- a D/E lord or eligible occupant;
- a supported Samdharmi planet.

The text often treats Mahadasha as secondary and then divides the Antardasha into three sectors. Jupiter is used as an earlier/moderate-delay influence and Saturn as a later-delay influence. Solar transit through signs or nakshatras associated with the top significators is then used for finer timing.

This sequence is highly vulnerable to retrospective fitting unless the event house, eligible planets, delay rule and timing window are frozen before the test period.

### 6. Rahu and Ketu as proxies

The nodes do not receive classical BAV totals. KAS lets a node act through several `Samdharmi` proxies:

- sign lord;
- nakshatra lord;
- Navamsa sign lord;
- a planet conjoining the node in Navamsa.

The proxy is supposed to matter only when the supporting planet is strong in the event worksheet. The book specifically distinguishes Navamsa conjunction from a simple Rasi conjunction. This offers a structured way to model nodal influence, but it remains a KAS-specific hypothesis and must not be merged into strict Shadbala totals.

## Quantitative features relevant to this workspace

### Daily seven-planet SAV index

Lesson 11 proposes a simple transit context score:

1. For each of the seven transiting classical planets, look up the natal SAV value of the sign currently occupied.
2. Sum those seven values.
3. Compare the result with `196 = 7 x 28`.

The manual interprets:

- above 196: broadly favorable/prosperous context;
- below 196: broadly difficult/worrying context;
- near 196: neutral.

For USDJPY, this should not be converted directly into `buy` or `sell`. A defensible experimental feature would compute the score separately for the USD reference chart and JPY reference chart, then test both raw scores, centered scores and `USD - JPY` difference. The same score can be calculated for the Bitcoin genesis reference chart as context, but it remains evidence-only.

### Jupiter-Saturn cash-flow score

Lesson 35 sums the bindus received by transiting Jupiter and Saturn in their occupied signs:

- sum of 8 or more: favorable cash-flow context;
- sum below 8: difficult context.

The book combines this with the Antardasha worksheet. For markets, keep the pieces separate at first:

- Jupiter transit BAV bindus;
- Saturn transit BAV bindus;
- sum and distance from eight;
- Dasha/event worksheet score, if eventually implemented.

This enables ablation tests and prevents an opaque composite from hiding which term actually carries information.

### Classical BAV/SAV evidence layer

The safest first implementation is not the full KAS decision engine. It is a reusable evidence table containing:

- natal BAV bindus for each classical planet in each sign;
- natal SAV by sign;
- each transiting classical planet's current sign;
- BAV value for that planet/sign;
- SAV value for that sign;
- seven-planet SAV total and distance from 196;
- Jupiter-Saturn bindu sum and distance from eight;
- doctrine metadata: ayanamsa, node policy, BAV convention, ephemeris version and reference-chart identity.

These columns should be shown as context and tested without changing Auto Suggest or MT5 execution.

## Corrections and errata found

The modern KAS lesson site explicitly says the original lesson's strength calculation was corrected. Important changes include:

1. A tied 4:10 transfer can apply to both eligible tied planets; the original worked example selected only Saturn where Jupiter should transfer to both Sun and Saturn.
2. Mars at exactly four bindus is neutral, not a positive-four contribution.
3. Jupiter aspecting its own house should not receive the deduction used in the old worksheet.
4. Jupiter's negative aspect on Venus should not be deducted when Venus is Lord E in that example.
5. Corrected rankings differ from the rankings printed in the original PDF.

Internal PDF problems also include:

- a lesson says Jupiter with five bindus casts three in the prose while the worksheet deducts five;
- one third-sector date runs from November 1992 backward to October 1992;
- one step can be read as adding eight rather than `8 - bindus`;
- Dasha dates in a 1998-2003 example are printed as 1991 dates;
- a diagram legend says `-4` means more than four, although the surrounding rule clearly requires fewer than four.

These are not cosmetic. A coded worksheet can produce a different planet ranking and event date if the wrong version is followed.

## Ayanamsa and convention conflict

The KAS material uses a Krushna ayanamsa described as approximately 54 arcminutes less than Lahiri, with a stated zero point of 24 February 366 AD. The current KAS site also refers to an improved KAS ayanamsa relative to the early lessons.

This workspace currently prefers Raman ayanamsa. Therefore:

- no KAS result may be labeled an exact reproduction while using Raman;
- the doctrine configuration must record `ayanamsa=raman` or `ayanamsa=krushna` explicitly;
- exact source-reproduction tests should use the source's specified convention;
- market experiments may use Raman by user policy, but must be labeled a Raman adaptation rather than canonical KAS;
- the BAV construction convention (for example Varahamihira versus Parashara) must also be versioned.

Silent mixing would change signs, nakshatras, Navamsas, bindu lookups, node proxies and timing results.

## Evidence-quality audit

### Strengths

- The author exposes formulas, intermediate worksheets and worked examples rather than giving only vague interpretations.
- Many rules are deterministic enough to code and falsify.
- The daily score and Jupiter-Saturn sum are simple enough for clean ablation tests.
- The nodal proxy mechanism is explicit and avoids pretending Rahu/Ketu have classical Shadbala or BAV rows.

### Weaknesses

- The book claims roughly 90% accuracy and studies of at least 100 or hundreds of charts, but supplies no raw dataset, sampling plan, locked predictions, holdout set, confusion matrix or reproducible evaluation.
- Many demonstrations are retrospective and sometimes begin with a known event, sharply narrowing possible answers.
- The chosen event houses and exceptions can vary by question, creating researcher degrees of freedom.
- Constants such as +5, score 12 and three Antardasha sectors are asserted rather than independently derived.
- The original published calculations include corrections large enough to change rankings.
- Medical, fertility, sexuality and family claims in later lessons are not medically validated and can be harmful if treated as factual inference.

The book is an astrological research/doctrine source, not scientific validation of predictive power.

## Trading integration decision

### Allowed now

- Record the source and formulas.
- Implement classical BAV/SAV calculations behind doctrine metadata and calculator cross-checks.
- Export the daily seven-planet score and Jupiter-Saturn sum as evidence-only features.
- Compare USD and JPY reference-chart values without converting them into trades.
- Run descriptive, ablation and purged chronological walk-forward tests.

### Quarantined pending validation

- KAS inverse-aspect scoring.
- A/B/C/D/E event worksheet.
- Samdharmi transfers and +5 bonuses.
- Antardasha sector timing and Sun fine-timing.
- Nodal proxy weights.
- Any combined prosperity/destiny index.

### Permanently excluded from this financial pipeline

- Medical diagnosis or prognosis.
- Fertility, sexuality or family-status inference.
- Social or moral judgments about people.

## Required implementation gates

1. **Calculation gate:** reproduce BAV/SAV tables and at least five known charts against two independent trusted calculators, with exact ayanamsa/convention metadata.
2. **Doctrine gate:** encode every KAS rule with source lesson, corrected-version flag, formula and intermediate audit terms; unresolved contradictions must return `unknown`, not an invented score.
3. **Research gate:** preregister the market mapping and thresholds, deduplicate overlapping events, and evaluate chronologically with purge/embargo and a untouched holdout.
4. **Promotion gate:** compare classical-only, KAS-only and combined models against price-only and random/null baselines; require stable direction, adequate family sample size and improvement after costs before any live influence.

No feature from this book currently passes all four gates.

## Recommended next build

Build `ashtakavarga_evidence.py` as a parallel evidence module with:

- seven-classical BAV/SAV only;
- explicit Raman-adaptation and source-reproduction configurations;
- calculator fixtures and audit tables;
- daily SAV total centered at 196;
- Jupiter-Saturn sum centered at eight;
- no trade direction, rule override or MT5 permission.

Only after that module is calculator-certified should a separate `krushna_kas_experimental.py` encode the corrected inverse-aspect and event worksheet rules for ablation testing.

## Online cross-checks

- Current KAS lesson index and historical note: <https://www.12divisions.com/kas-lessons/>
- Corrected KAS Lesson 7: <https://www.12divisions.com/kas-lessons/kas-lesson07/>
- Classical Ashtakavarga transit discussion, Phaladeepika Chapter 23: <https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621595.html>
- Classical Ashtakavarga chapter, Brihat Jataka Chapter 9: <https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english/d/doc1501544.html>
