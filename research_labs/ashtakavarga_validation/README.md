# Ashtakavarga Validation Lab

This directory is a self-contained research lab for testing classical Ashtakavarga and selected Krushna Ashtakavarga System (KAS) evidence features.

It is tracked by the private recovery repository, but it is deliberately isolated from the canonical USDJPY/BTC pipeline.

## Isolation contract

- No imports from the project trading modules.
- No writes to canonical CSV, Parquet, SQLite, review-pack or MT5 paths.
- No Auto Suggest, review-agent or LLM integration.
- No order placement or MetaTrader connection.
- All generated files must stay under this lab's `outputs/` or `reports/` directories.
- External price files may be read only when explicitly passed to the evaluator.
- KAS evidence can never become a trade signal from inside this lab.
- The root-level `krushna_kas_advisory.py` adapter may read lab calculations for a display-only review suggestion. Its output explicitly disables Auto Suggest, ML training, rule overrides, markers and MT5.

## Current doctrine lock

| Setting | Value |
|---|---|
| Zodiac | Sidereal |
| Ayanamsa | Raman adaptation |
| BAV rule table | B. V. Raman-style unreduced benefic-place table |
| Contributors | Seven classical planets plus Lagna |
| BAV rows | Seven classical planets |
| Nodes / outer planets | Excluded |
| SAV | Sum of seven unreduced BAV rows |
| Trikona/Ekadhipatya reductions | Not applied |
| KAS inverse-aspect worksheet | Corrected experimental implementation, isolated |
| KAS event worksheet | All 12 House B mappings, isolated |
| Vimshottari / three sectors | Implemented as evidence; no fitted delay choice |
| Sun timing | Candidate sign/nakshatra gate |
| Lesson 26 multipliers | Result-quality ablation only, not timing |
| Trading permission | Disabled |

The Raman setting follows the user's workspace policy. It is not an exact reproduction of the source's Krushna ayanamsa and is labeled accordingly.

## What the first version tests

1. BAV row totals are always `48, 49, 39, 54, 56, 52, 39`.
2. SAV always totals `337`.
3. The B. V. Raman standard-horoscope fixture is reproduced sign by sign.
4. Daily evidence exports:
   - each transiting classical planet's own BAV value;
   - SAV of each transit sign;
   - seven-planet SAV sum and distance from `196`;
   - Jupiter plus Saturn own-BAV sum and distance from `8`.
5. A standalone USDJPY evaluator compares USD and JPY reference-chart evidence with future returns using expanding chronological folds and an embargo gap.
6. The corrected Lesson 7 worksheet reproduces its published fixture row by row.
7. Full KAS market experiments report all twelve event-house choices, Dasha, nodal proxies, Sun timing and component ablations without post-outcome house selection.

## Commands

Run these from this directory:

```powershell
python -m unittest discover -s tests -v
python -m ashtakavarga_lab.cli certify
python -m ashtakavarga_lab.cli natal --profile usd_reference
python -m ashtakavarga_lab.cli compare-external --input fixtures/my_calculator_usd.json
python -m ashtakavarga_lab.cli evidence --start 2010-01-27 --end 2026-03-10 --profiles usd_reference,jpy_reference
python -m ashtakavarga_lab.cli evaluate --price D:\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet
python -m ashtakavarga_lab.cli kas-fixture
python -m ashtakavarga_lab.cli kas-evidence --start 2010-01-27 --end 2026-03-10 --profiles usd_reference,jpy_reference
python -m ashtakavarga_lab.cli kas-evaluate --price D:\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet
```

`certify` passing means the local arithmetic and one published fixture pass. It does **not** mean the engine has passed the required two-independent-calculator gate.

For an outside-calculator check, duplicate `fixtures/external_calculator_template.json`, enter the seven unreduced BAV rows and SAV row, record the calculator/version, and run `compare-external`. The comparison fails on any differing cell and reports its planet/sign coordinates.

## Promotion policy

Nothing here is promoted automatically. A later promotion decision requires:

1. exact agreement with two independent calculators;
2. a frozen market mapping and untouched holdout;
3. purged chronological evaluation against price-only and randomized controls;
4. positive results after spread/slippage across multiple periods;
5. an explicit manual code review and separate integration commit.

See `KAS_METHOD_SPEC.md` for the frozen implementation and unresolved source ambiguities. See `FULL_KAS_FIRST_RUN_FINDINGS.md` for the first complete isolated USDJPY experiment.

## Sources

- Local source audit: `D:\PycharmProjects\krushna_ashtakavarga_source_review_20260710.md`
- KAS Lesson 1: <https://www.12divisions.com/kas-lessons/kas-lesson01/>
- Corrected KAS Lesson 7: <https://www.12divisions.com/kas-lessons/kas-lesson07/>
- Classical Phaladeepika Chapter 23: <https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621595.html>
- B. V. Raman table/fixture transcription used for certification: <https://vedastro.org/blog/Mastering-Ashtakavarga-Part-2-Building-Bhinnashtakavarga-Charts.html>
