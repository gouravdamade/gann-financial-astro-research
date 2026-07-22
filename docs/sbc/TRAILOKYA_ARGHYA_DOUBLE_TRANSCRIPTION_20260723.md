# Trailokya Dipika Arghya Double Transcription - 2026-07-23

## Decision

The three numeric Arghya tables are now transcribed independently from two
editions of the same Mithalal Vyas textual lineage and reconciled cell for
cell. This establishes a stable cross-edition reading. It does **not** provide
an independent doctrinal witness, a certified predicted-price equation, or a
trading rule.

The guarded lab may calculate only the source's narrow twenty-part
availability direction. Direct price, bullish/bearish, stock/FX, Auto Suggest,
live inference, official-note, and MT5 outputs remain blocked.

## Sources and page alignment

| Material | 1972 Tej Kumar edition | 2016 Khemraj reprint |
| --- | ---: | ---: |
| Relationship and quarter-strength Viswa table | PDF 98, printed 52 | PDF 82, printed 72 |
| Planetary aspect-house table | PDF 99, printed 53 | PDF 83, printed 73 |
| Five-class Vedha Viswa table | PDF 101, printed 55 | PDF 85, printed 75 |
| Twenty-part availability/price-direction prose | PDF 102, printed 56 | PDF 86, printed 76 |

The 1972 original page images controlled pass 1. The 2016 reprint page images
controlled pass 2. OCR was used only for navigation. The later reprint is a
reading witness, not a second independent authority.

Machine-readable passes:

- `configs/sbc/arghya/trailokya_1972_arghya_pass1.csv`
- `configs/sbc/arghya/trailokya_2016_arghya_pass2.csv`
- `configs/sbc/arghya/trailokya_arghya_reconciliation_v1.yaml`

Each pass has 108 cells: 32 relationship/quarter cells, 36 planetary
aspect-house cells, and 40 five-class cells. All 108 comparable readings
match across editions.

## Notation rule

The stacked numeric values in the two Viswa tables are sexagesimal
`Viswa|Kala`, with 60 Kala to one Viswa. Examples:

- `11|15 = 11 + 15/60 = 11.25`
- `0|48 = 0 + 48/60 = 0.8`

The vertical separators in the planetary aspect-house table mean a list of
houses. They are not sexagesimal. Thus `3|10|7` means houses 3, 10, and 7 in
the printed order.

## Table 1: relationship and quarter strength

Columns below are benefic own/friend/neutral/enemy followed by malefic
own/friend/neutral/enemy.

| Strength | B-own | B-friend | B-neutral | B-enemy | M-own | M-friend | M-neutral | M-enemy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full | 20\|0 | 15\|0 | 10\|0 | 5\|0 | 5\|0 | 10\|0 | 15\|0 | 20\|0 |
| Three-quarter | 15\|0 | 11\|15 | 7\|30 | 3\|45 | 3\|45 | 7\|30 | **11\|45** | 15\|0 |
| Half | 10\|0 | 7\|30 | 5\|0 | 2\|30 | 2\|30 | 5\|0 | 7\|30 | 10\|0 |
| Quarter | 5\|0 | 3\|45 | 2\|30 | 1\|15 | 1\|15 | 2\|30 | 3\|45 | 5\|0 |

## Table 2: planetary aspect houses

| Strength | Sun | Moon | Mars | Mercury | Jupiter | Venus | Saturn | Rahu | Ketu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Quarter | 3\|10 | 3\|10 | 3\|10 | 3\|10 | 3\|10 | 3\|10 | 0 | 3\|10 | 3\|10 |
| Half | 5\|9 | 5\|9 | 5\|9 | 5\|9 | 0 | 5\|9 | 5\|9 | 5\|9 | 5\|9 |
| Three-quarter | 4\|8 | 4\|8 | 0 | 4\|8 | 4\|8 | 4\|8 | 4\|8 | 4\|8 | 4\|8 |
| Full | 7 | 7 | 4\|8\|7 | 7 | 5\|7\|9 | 7 | 3\|10\|7 | 7 | 7 |

The unusual printed order for Mars and Saturn is retained. The validator does
not sort or rewrite those cells.

## Table 3: five-class Vedha Viswa

Columns below are one through five benefic hits followed by one through five
malefic hits.

| Strength | B1 | B2 | B3 | B4 | B5 | M1 | M2 | M3 | M4 | M5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full | 1\|0 | 2\|0 | 3\|0 | 4\|0 | 5\|0 | 0\|48 | 1\|36 | 2\|24 | 3\|12 | 4\|0 |
| Three-quarter | 0\|45 | 1\|30 | 2\|15 | 3\|0 | 3\|45 | 0\|36 | 1\|12 | 1\|48 | **2\|18** | 3\|0 |
| Half | 0\|30 | 1\|0 | 1\|30 | 2\|0 | 2\|30 | 0\|24 | 0\|48 | 1\|12 | 1\|36 | 2\|0 |
| Quarter | 0\|15 | 0\|30 | 0\|45 | 1\|0 | 1\|15 | 0\|12 | 0\|24 | 0\|36 | 0\|48 | 1\|0 |

## Two source-preserved anomalies

Both editions print the same two values that fail the surrounding tables'
simple quarter scaling:

1. Relationship table, three-quarter, malefic-neutral: printed `11|45`
   (`11.75`), while three quarters of full `15|0` is `11|15` (`11.25`).
2. Five-class table, three-quarter, four malefics: printed `2|18` (`2.3`),
   while three quarters of full `3|12` (`3.2`) is `2|24` (`2.4`).

The fixture preserves the printed values and reports both anomalies. Agreement
between same-lineage editions cannot decide whether they are intentional or
inherited typographical errors. No corrected value is silently substituted.

## Prose-derived research mechanics

The chapter separates three sets of dimensions:

- place: country/region (`desha`), district (`mandala`), locality (`sthana`);
- time: year, month, day;
- commodity: mineral/metal (`dhatu`), root/plant (`mula`), living produce
  (`jiva`).

It assigns candidate lords and asks the reader to select the strongest among
them. The candidates are encoded in the profile, but the complete precedence
for combining sign relation, distance from sign center, retrogression,
rising, and exaltation is not certified here.

After separate benefic and malefic Viswa totals are differenced, the prose
imagines the current commodity amount or condition as 20 parts and treats one
Viswa as one part:

`availability index = 20 + benefic Viswa - malefic Viswa`

The source describes an index above 20 as greater availability/abundance and
lower-price pressure, and an index below 20 as scarcity and higher-price
pressure. This is a commodity-availability interpretation. It is not safe to
rename favorable influence as bullish: favorable influence can increase
supply and therefore lower price.

## Synthetic direction-only check

For a non-validating arithmetic check, imagine a reference value of 100 split
into twenty five-unit parts. If net Viswa is `+3`, the availability index is
`23`, so the source direction is abundance/lower-price pressure. The lab stops
there. It does not calculate `85`, or any other predicted price.

## Why direct price remains blocked

1. The 2016 source is a reprint in the same lineage, not an independent worked
   witness.
2. Two stable printed cells are internally anomalous.
3. The following page distinguishes amount/condition (`bhava`) from monetary
   value (`mulya`) and begins another method; the exact conversion into a
   predicted market price is not sufficiently resolved by this pass.
4. No cited external example reproduces the full selection, Viswa totals, and
   final price from independent inputs.
5. No source-certified mapping exists from these commodity categories to a
   modern stock, FX pair, crypto instrument, or trade direction.
6. No frozen prospective/no-lookahead financial validation has passed.

## Software boundary and next gate

`research_labs/trailokya_arghya` validates both CSVs, notation, table counts,
cross-edition identity, proportional anomalies, and the direction-only sanity
fixture. `refuse_predicted_price()` deliberately raises an execution-lock
error.

Nothing is wired into the desktop/mobile app, SBC score, RAG official answer,
Auto Suggest, live inference, validation ledger, or order path. The next gate
is an independently sourced, page-cited worked example that exposes all
inputs and arithmetic. Even after that, a separate prospective market test is
required before any financial promotion.
