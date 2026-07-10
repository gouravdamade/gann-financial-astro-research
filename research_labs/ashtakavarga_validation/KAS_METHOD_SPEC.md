# Corrected KAS Experimental Specification

This specification freezes the testable Krushna Ashtakavarga System methodology used by this isolated lab. It is a Raman-adapted market experiment plus a source-fixture reproduction. It is not an exact improved-Krushna-ayanamsa reproduction and cannot place trades.

## Implemented doctrine

1. Unreduced seven-classical BAV and SAV with Lagna as contributor.
2. Event rotation for every frozen House B: `A=8th from B`, `C=10th from A`, `D=3rd from A`, `E=11th from A`.
3. Corrected Lesson 7 rows:
   - A+B+C basic strength;
   - 4:10 transfers to every tied minimum eligible natural-malefic recipient;
   - five-point D/E lord and qualified-occupant bonuses;
   - inverse KAS aspects, with exactly four neutral;
   - own-house aspect exemption;
   - D/E-lord planet-aspect exemption;
   - final scores, ranks and the strict `>12` benefic threshold.
4. Direct timing candidates and Samdharmi substitutes:
   - natural Venus-Saturn, Mars-Sun and Mars-Moon relations;
   - same Rasi, nakshatra and Navamsa;
   - qualified 4:10 relation;
   - seventh-house opposition restriction;
   - sixth-lord, 12th-lord, 12th-from-B and restricted-transfer blocks;
   - D/E exception for an otherwise obstructed direct candidate.
5. Rahu/Ketu proxies through sign lord, nakshatra lord, Navamsa lord and Navamsa conjunctions. Nodes receive no BAV row.
6. Vimshottari Mahadasha and Antardasha from natal Moon, with every Antardasha divided into three equal sectors. The observed sector is exported; no outcome-fitted delay sector is selected.
7. Sun timing evidence through candidate natal sign/nakshatra and candidate rulership of the transiting Sun's sign/nakshatra.
8. Lesson 11 seven-planet SAV context centered on 196.
9. Lesson 35 Jupiter-Saturn own-BAV context centered on eight.
10. Lesson 26 sign multipliers as result-quality evidence only. The source explicitly says not to use this table for timing.

## Published regression fixture

`fixtures/kas_lesson7_marriage_corrected.json` transcribes the supplied Lesson 7 chart and BAV table. It also applies the later online corrections. Expected final scores are:

| Planet | Corrected score |
|---|---:|
| Saturn | 32 |
| Sun | 31 |
| Mercury | 20 |
| Jupiter | 18 |
| Venus | 16 |
| Moon | 11 |
| Mars | 11 |

The CLI fails if any worksheet row or ranking differs.

## Frozen financial mapping

There is no source-defined “currency market event house.” The evaluator therefore reports all twelve House B choices and applies one multiple-testing correction across every house, feature, horizon and direction mapping. It never selects a house after observing returns.

For USDJPY, each feature is calculated separately for the USD and JPY reference charts. The tested value is USD minus JPY. Ablations include:

- current Antardasha worksheet score;
- Antardasha eligible/adverse disposition;
- SAV context;
- Jupiter-Saturn context;
- their ordinal combined context;
- Sun-gated combined context;
- each of the three Antardasha-sector gates;
- Sun plus sector gates.

Evaluation uses expanding chronological folds, a gap equal to the forward horizon, non-overlapping outcome samples, Wilson intervals, circular-shift placebos, Bonferroni correction and 0/1/2/5-basis-point round-trip cost sensitivity.

## Explicitly unresolved

- Exact improved Krushna ayanamsa ephemeris values are unavailable.
- The source does not define a financial-market event-house mapping.
- Event-specific natural and functional Karakas do not have a defensible currency equivalent.
- Delay-sector selection depends on event-specific judgments and sometimes cultural/biographical facts. The lab exports all sectors instead of fitting one.
- The source's 4:10 prose is not fully general: its corrected example excludes a weak Moon that appears superficially eligible. The implementation follows the published fixture-supported natural-malefic recipient policy and exposes it as doctrine metadata.
- Source examples contain date, arithmetic and legend errors; unresolved variants must remain separate ablations or `unknown`.

These limitations prevent “full methodology” from meaning “every sentence converted into a market rule.” It means every reproducible core and timing component is available for falsifiable testing, while non-transferable personal-event claims remain outside the financial experiment.

## Non-binding review advisory

The canonical project may read this isolated engine through `krushna_kas_advisory.py` for one display-only purpose: show an all-twelve-house vote in the repeatation-review drawer. The adapter does not select a best house and exports explicit locks:

- `evidence_only=1`;
- `trade_signal_enabled=0`;
- `trade_override_allowed=0`;
- `auto_suggest_input=0`;
- `ml_training_input=0`;
- `mt5_input=0`.

The review advisory is not a promotion of KAS into the trading pipeline. It is a visible research suggestion that may disagree with deterministic rules or reviewed behavior.
