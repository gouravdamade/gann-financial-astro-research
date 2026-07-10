# Padmanabhan Timing Doctrine Source Notes

## Bibliographic identity

- Article: `Timing of Events - A Qualitative and Quantitative Study`
- Author: `R. A. Padmanabhan` (the photographed byline uses **Padmanabhan**, not Padmanabha)
- Publication: *The Astrological Magazine*, Volume 74, 1985, Raman Publications
- Recovered start page: page 14, apparently in the January 1985 issue
- Google Books volume id: `5uA5AAAAIAAJ`

## Full-copy recovery status

No lawful downloadable full copy was found as of 2026-07-10.

- Google Books holds the digitized volume but exposes only snippet view; its metadata reports that PDF download is unavailable.
- Internet Archive and HathiTrust-focused searches did not locate a downloadable Volume 74/January 1985 scan.
- Astrolearn lists physical holdings for Volume 74 beginning with February 1985, not the January issue containing page 14.
- The modern Astrological eMagazine archive does not expose the 1985 Raman issue.

Therefore the article has **not** been studied completely. The implementation is deliberately limited to the photographed first page plus independently checked Phaladeepika Chapter 26 rules. The remaining pages, tables, examples, and exact weights must be supplied or lawfully accessed before this doctrine can be called article-complete.

### Separate Krushna Ashtakavarga book

The subsequently supplied 185-page PDF `Timing of Events: A Research Work in Astrology with Krushna Ashtakvarga System` is a different work by Krushna Jugalkalani. It does not recover this Padmanabhan article's continuation or Table 2. Its Ashtakavarga hypotheses and source-quality audit are recorded separately in `krushna_ashtakavarga_source_review_20260710.md`.

## Recovered first-page model

The photographed page establishes the following structure:

1. Gochara is assessed from natal Moon.
2. Dasha/Bhukti effects are superposed with Gochara.
3. The combined index is stated as `I = A + B`, where `A` is Gochara intensity and `B` is Dasha/Bhukti intensity.
4. Planetary disposition is graded from natural quality, temporal quality, and whether Shadbala is above or below six Rupas.
5. A fourth Yogakaraka/special-combination factor can be added for named combinations.

The page ends during the disposition discussion and refers to a missing Table 2. It does not provide enough material to recover the article's complete scoring weights.

## Independently checked classical rules

Phaladeepika Chapter 26 was checked against the photographed citations:

- 26.1: Gochara is counted from natal Moon.
- 26.2: favorable whole-sign transit houses.
- 26.3-8: Vedha obstruction-house pairs and the Sun/Saturn and Moon/Mercury exceptions.
- 26.33-34: exceptional adverse placements cited by Padmanabhan.

Source: <https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621598.html>

Google Books record: <https://books.google.com/books?id=5uA5AAAAIAAJ>

Physical-holdings catalog: <https://www.astrolearn.com/astrology-bibliography/the-astrological-magazine/>

## Explicit source conflict

Mercury in the fourth house from natal Moon is listed as favorable in Phaladeepika 26.2 and as an exceptional adverse placement in 26.34. The missing Padmanabhan continuation/Table 2 may explain how these conditions are reconciled. Version 1 records this as `source_conflict_favourable_and_exceptional_adverse` and assigns zero, rather than inventing a direction.

## Implemented in version 1

- Whole-sign Gochara from natal Moon for seven classical planets.
- Classical Vedha mappings and explicit exception pairs.
- Exceptional adverse placement flags.
- Raw Rahu/Ketu houses, while excluding nodes from Vedha scoring because the recovered source does not provide a reliable nodal Vedha table.
- Deterministic Vimshottari Mahadasha and Antardasha from natal Moon nakshatra.
- Natural-quality disposition proxy with phase-sensitive Moon and an explicit workspace-policy label for Mercury; no association orb is invented.
- Six-Rupa gate at 360 Virupa, kept separate from planet-specific Shadbala minima.
- Provisional equal-additive Dasha/Bhukti score.
- `I_reference = A_gochara + B_dasha_bhukti`.
- `I_USDJPY = I_USD - I_JPY`.

## Deliberately not invented

- Padmanabhan's exact Gochara intensity weights.
- The missing Table 2 notation and grade conversion.
- The article's temporal-quality table.
- Named Yogakaraka/Raja-yoga detection and weights.
- Any later Ashtakavarga or example-specific adjustment that may appear in the unrecovered continuation.
- A claim of predictive or scientific validity.

All new outputs carry a source-incomplete/provisional status and remain parallel evidence. They do not alter the existing USDJPY trade direction or Auto Suggest rules until historical replay and walk-forward tests justify promotion.
