# Phase 2A Grid Fixture Audit

## Source Findings

| Question | Finding | Gate |
| --- | --- | --- |
| Is an 81-cell form locally page-certifiable? | Yes, in two held editions | Partial topology fixture allowed |
| Do the two figures share one absolute orientation? | No; they are related by a 90-degree rotation | Cardinal binding blocked |
| Are the 28 nakshatras, including Abhijit, consistent? | Yes after rotation normalization | Certified structural layer |
| Is the 12-rashi ring consistent? | Yes after rotation normalization | Certified structural layer |
| Are the five tithi groups and weekdays consistent? | Yes after rotation normalization | Certified structural layer |
| Are all Sanskrit vowel/consonant glyphs safely transliterated? | Not yet | Letter layers blocked |
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

## Certified Counts

- 28 nakshatra entries, including Abhijit exactly once
- 12 rashi entries exactly once
- 5 tithi-group entries exactly once
- 7 weekday entries exactly once
- 81 deterministic cells in the compiled container

The container is deliberately incomplete: 16 vowel slots, 20 consonant slots,
and one absolute-cardinal binding remain unresolved. `complete` therefore stays
false.

## Non-Claims

Phase 2A does not certify:

- that 81 cells are universally preferable to 64 cells;
- an absolute North/East orientation for the compiled profile;
- vowel or consonant transliteration;
- Abhijit longitude insertion policy for planetary placement;
- Vedha, Latta, benefic/malefic judgment, scoring, market direction, or trades.
