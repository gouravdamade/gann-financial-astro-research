# Financial Astrology Source Notes

Date: 2026-03-13

Sources reviewed:
- `pdfcoffee.com_financial-astrology-pdf-free.pdf`
- `pdfcoffee.com_futuretec-financial-astrology-set-2-dhruvank-pdf-free.pdf`
- `pdfcoffee.com_gann-financial-astrology-pdf-free.pdf` (image-heavy, text extraction poor)

Extracted text files:
- `pdf_extracts/pdfcoffee.com_financial-astrology-pdf-free.txt`
- `pdf_extracts/pdfcoffee.com_futuretec-financial-astrology-set-2-dhruvank-pdf-free.txt`
- `pdf_extracts/pdfcoffee.com_gann-financial-astrology-pdf-free.txt`

## High-confidence takeaways

### 1. Astrology is not treated as standalone direction logic

`AstroEcon` repeatedly treats astrology as a timing layer that should be combined with technical structure.

Relevant extracted passages:
- `AstroEcon` says weekly work combines astrology with `support/resistance`, trend lines, and Elliott Wave.
- Intraday turn times are described as more useful when combined with technical support/resistance.
- The text explicitly says using only one factor leads back toward `50/50`.

Implication for our project:
- This supports the current direction: use astrology to locate `when price is vulnerable`, then let SR/price context determine `whether the move is real`, `which direction dominates`, and `how far it can travel`.

### 2. Fast vs slow planets should be modeled separately

`AstroEcon` separates:
- long-term influences from slow-moving planets lasting weeks or months
- short-term influences from the Moon and other fast planets

Implication:
- We should not pool all events into one model family.
- Build separate feature groups for:
  - `fast timing layer`: Moon, Mercury, Venus, Sun, Mars
  - `medium/long regime layer`: Jupiter, Saturn, and later outer bodies if desired

### 3. Intraday angle hits are location-specific and important

`AstroEcon` pages 52-53 and 76-78 emphasize:
- intraday hit times are not generic aspects
- they are planet contacts with the local angles:
  - Ascendant
  - Midheaven
  - Descendant
  - Nadir
- they are specific to the trading location
- very close orbs are suggested for transit-to-transit angle hits

Implication:
- We should add a second event engine:
  - `transit planet -> market-location angle`
- For JPY work, this should be tied to `Tokyo, Japan`, not Chicago.
- This fits the user's existing shift toward `natal-to-transit` and location-aware work.

### 4. Transit-to-natal should be added

`AstroEcon` setup pages explicitly mention:
- `transit to transit`
- `transit to natal`
- wider orbs for transit-to-natal than for intraday transit-to-transit angle hits

Implication:
- We should add IPO-chart targets:
  - natal planet longitudes
  - natal ASC/MC/DSC/IC
  - natal house cusps if stable enough for the chosen chart method
- This matches the current project direction better than pure transit-to-transit alone.

### 5. Midpoints are likely worth adding

`AstroEcon` midpoint lesson says the useful trading form is:
- direct contact of a planet to the exact midpoint of two planets
- or to the point opposite that midpoint

It explicitly says midpoint combinations:
- happen daily because the Moon is fast
- are more useful when focused on important long-term structures
- become more important when several midpoint relations focus on one planet

Implication:
- Add midpoint features, but keep them simple:
  - `planet touches midpoint(p1, p2)`
  - `planet opposes midpoint(p1, p2)`
  - count of midpoint hits active now
  - count of midpoint hits involving Moon
  - count of midpoint hits involving slow planets

### 6. Complex aspect pattern flags are useful regime features

`AstroEcon` highlights:
- Stellium
- T-square
- Grand Cross
- Grand Trine
- Yod

The text treats these as:
- rare
- high-impact
- often not safely inferable from ordinary repeated-cycle analysis

Implication:
- Add binary or score features for complex configurations.
- These are better used as `context/regime` features than direct standalone signals.

### 7. Planetary combination semantics can be encoded, but carefully

`AstroEcon` includes qualitative pair meanings:
- Moon-Mars = tension / irritability
- Mercury-Jupiter = wisdom or excess optimism
- Saturn combinations often map to fear, inhibition, harshness, restraint

Implication:
- Do not hard-code narrative direction labels.
- It is acceptable to derive low-level semantic tags such as:
  - `optimism_bias`
  - `fear_bias`
  - `impulse_bias`
  - `restraint_bias`
- But these should remain weak auxiliary features, not the main trading rule.

## Medium-confidence takeaways

### 8. Event timing can be skewed by real-world catalysts

`AstroEcon` lesson 6B states that:
- astro can define pressure windows
- real events can delay or skew exact price manifestation

Implication:
- avoid measuring effect from only the exact minute of perfection
- continue using `window-based` analysis instead of `exact tick` claims
- keep the current approach of measuring price response after touch points inside event windows

### 9. Opening condition matters

`AstroEcon` says:
- if a planet is on an angle at the market open, it becomes featured for the day

Implication:
- add open-state features:
  - count of planets near local angles at session open
  - strongest angular planet at open
  - whether Moon / Saturn / Mercury / Mars is angular at open

## Low-confidence / experimental takeaways

### 10. Dhruvank Chakra is usable only as an experimental side-channel

The `Dhruvank` PDF provides a deterministic numeric recipe using:
- asset number
- city number
- nakshatra
- tithi
- weekday
- lunar month
- sun sign
- yoga
- divide by 9 and classify rise/fall/no change via a fixed mapping

Why this is weaker:
- it is table-driven and numerological rather than geometrically derived
- the current table is generic for `shares`, not instrument-specific for USDJPY
- no evidence in the source that it was validated on FX or on Japanese assets

Still potentially useful:
- as an `experimental categorical prior`
- not as a primary directional model

Safe use:
- build a `dhruvank_remainder`
- build a `dhruvank_outlook_class`
- test it only as one feature block inside ML

Unsafe use:
- do not use it as a standalone trading signal

## Source limitations

### Gann PDF

`pdfcoffee.com_gann-financial-astrology-pdf-free.pdf` is image-heavy/scanned. OCR was completed on 2026-05-10.

OCR outputs:
- `D:\GannFinancialAstro\doc\pdf_text_extracts\pdfcoffee.com_gann-financial-astrology-pdf-free.ocr.txt`
- `D:\GannFinancialAstro\doc\pdf_text_extracts\pdfcoffee.com_gann-financial-astrology-pdf-free.ocr_summary.json`
- per-page checkpoints: `D:\GannFinancialAstro\doc\pdf_text_extracts\gann_ocr_pages`

OCR summary:
- 177 pages
- about 210k OCR body characters
- about 8.2k OCR lines

Initial candidate rule families visible in OCR:
- price and longitude conversion for support/resistance/turning points
- geocentric/heliocentric planetary longitude paths
- outer-planet longitude averages with 0/360 smoothing
- Circle Chart / active-angle time and resistance projections
- fourth-dimension / intraday and double-numbered price-time chart material

Consequence:
- OCR is now usable for page-anchored study.
- Do not implement Gann rules directly from OCR snippets alone; verify against the page OCR JSON/source image and attach source page IDs to each encoded rule.

## What this means for our codebase now

### Add now

1. `Transit-to-natal` event engine
- transit planets to IPO natal planets
- transit planets to natal angles
- transit planets to natal houses if the chart engine already supports them reliably

2. `Location-angle` engine
- transit planet hits to `ASC/MC/DSC/IC`
- use `Tokyo, Japan`
- keep tight intraday orbs

3. `Midpoint` engine
- direct midpoint touch
- opposite midpoint touch
- per-bar midpoint concentration counts

4. `Complex pattern` features
- stellium count / flag
- t-square flag
- grand cross flag
- yod flag
- grand trine flag

5. `Session-open angle state`
- angular planets at open
- strongest angular planet at open

6. `Slow-regime` features
- active slow-planet stress combinations
- active slow-planet harmony combinations
- duration-in-window

### Add later

1. `Dhruvank` feature block
- only after main geometry-driven features are in

2. `Planet-combination semantics`
- only as compressed ML tags, not as rule logic

3. `Outer-planet expansion`
- only after the current 7-planet model is stable

## Best fit with current project

The strongest overlap between the source material and our current direction is:
- astrology marks `sensitive time windows`
- SR lines mark `sensitive price zones`
- prediction quality should improve when both agree

That means our next prediction model should be based on:
- `touch point inside aspect window`
- `plus transit-to-natal state`
- `plus local-angle state`
- `plus midpoint state`
- `plus slow-regime state`
- `plus SR structure`

## Recommended implementation order

1. Add `transit-to-natal` features to the touch log.
2. Add `Tokyo angle hit` features and session-open angle state.
3. Add midpoint-touch features.
4. Add complex-pattern flags.
5. Re-run the 72h touch study.
6. Only then test Dhruvank as an extra ML feature block.
