# Phase 2B Grid and Letter Fixture Audit

## Source Findings

| Question | Finding | Gate |
| --- | --- | --- |
| Is an 81-cell form locally page-certifiable? | Yes, in two held editions | Partial topology fixture allowed |
| Do the two figures share one absolute orientation? | No; they are related by a 90-degree rotation | Cardinal binding blocked |
| Are the 28 nakshatras, including Abhijit, consistent? | Yes after rotation normalization | Certified structural layer |
| Is the 12-rashi ring consistent? | Yes after a Phase 3A six-cell transcription correction and rotation normalization | Certified structural layer |
| Are the five tithi groups and weekdays consistent? | Yes after rotation normalization | Certified structural layer |
| Are all 16 Sanskrit vowel glyphs safely transcribed? | Yes, with exact Devanagari and ASCII transliteration in both held page witnesses | Certified letter layer |
| Is the source-labeled consonant ring machine-safe? | Yes, after naming it `NAME_INITIAL`; its first item is vowel `अ`, followed by 19 consonants | Certified semantic exception |
| Is a complete 64-cell mapping locally page-certifiable? | No | Compiler blocked |
| Are Vedha/Latta rules certified by this gate? | No | Interpretation blocked |

## Coordinate Contract

Coordinates are one-based. Row 1 is the top of Rath Figure 1.2 and column 1
is its left edge. These are **figure coordinates**, not North/East claims.

The rotation function from the cardinals-labeled 1937 plate to this profile is:

```text
profile_row = 10 - plate_column
profile_column = plate_row
```

Examples:

| 1937 plate coordinate | Value | Profile coordinate |
| --- | --- | --- |
| (2, 9) | Krittika | (1, 2) |
| (9, 8) | Magha | (2, 9) |
| (8, 1) | Anuradha | (9, 8) |
| (1, 2) | Dhanishtha | (8, 1) |

## Phase 3A Rashi Correction

The first Phase 2A transcription placed the three top and three bottom rashi
cells one column too far left. Visual reinspection of Rath Figure 1.2 and the
editor supplement's Krittika, Rohini, and Mrigashira worked Vedha examples
showed the correct coordinates:

```text
top:    VRISHABHA (3,4), MITHUNA (3,5), KARKA (3,6)
bottom: MAKARA (7,4), DHANUS (7,5), VRISCHIKA (7,6)
```

The correction removes unintended rashi/vowel cell overlaps and makes all
three printed nine-target examples compile exactly. Tests now assert both the
correct cells and the vacated `(3,3)` and `(7,3)` cells.

## Certified Counts

- 28 nakshatra entries, including Abhijit exactly once
- 12 rashi entries exactly once
- 5 tithi-group entries exactly once
- 7 weekday entries exactly once
- 16 vowel entries in nested-corner order exactly once
- 20 name-initial entries around the second ring exactly once
- 81 deterministic cells in the compiled container

The container is deliberately incomplete because one absolute-cardinal binding
remains unresolved. `complete` therefore stays false.

## Letter Contract

Every `VOWEL` and `NAME_INITIAL` entry carries four independent machine fields:

- an uppercase ASCII token used for identity;
- the exact Devanagari glyph shown by the source;
- a lowercase ASCII transliteration;
- a semantic role.

The first item in the source-described consonant ring is `अ` (`A`). Calling
the whole machine layer `CONSONANT` would silently falsify the page evidence.
It is therefore `NAME_INITIAL`, and that first entry carries
`VOWEL_EXCEPTION_IN_NAME_INITIAL_RING`; the other 19 carry
`CONSONANT_NAME_INITIAL`.

## 64-Cell Acquisition Search

A lawful retail listing was located for the 1972 *Sarvatobhadra Chakra* with
*Trailokya Dipika* commentary by Pt. Mithalal Vyas, published by Tej Kumar Book
Depot, Lucknow. That is an acquisition lead, not page evidence. No legally
usable public copy inspected in this gate supplied a complete, edition-stable
64-cell coordinate map. `sbc_64_blocked_v1` therefore remains metadata-only.

## Non-Claims

The grid fixture does not certify:

- that 81 cells are universally preferable to 64 cells;
- an absolute North/East orientation for the compiled profile;
- Abhijit longitude insertion policy for planetary placement;
- automatic speed classification, special-corner Vedha, Latta, association
  inference, market direction, or trades.
