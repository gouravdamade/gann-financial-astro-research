# SBC Phase 2B Letter Fixture Acceptance Report

Date: 2026-07-17 IST

Status: accepted as an incomplete, explicit-only page transcription fixture

## Scope Delivered

- 16 page-certified Sanskrit vowel entries
- 20 page-certified name-initial entries
- exact Devanagari glyphs plus lowercase ASCII transliterations
- explicit semantic roles, including the source's vowel exception in the
  prose-labeled consonant ring
- strict runtime and JSON-schema contracts for letter metadata
- retained figure-relative `ROTATE_CCW_90` comparison contract
- retained `complete=false` while cardinal orientation is unresolved
- retained fail-closed 64-cell profile and all interpretation/trading locks

## Source Evidence

- Phaladeepika 1937 Subrahmanya Sastri edition, editor supplement, PDF pages
  347-348, printed pages 310-311. The construction text states the 16-vowel
  nested-corner sequence and the five name sounds on each cardinal side.
- Sanjay Rath, *The Crux of Vedic Astrology - Timing of Events*, PDF page 21,
  printed page 10, Figure 1.2. This supplies the profile-relative letter-cell
  positions.

The machine layer is named `NAME_INITIAL`, not `CONSONANT`, because its first
source item is vowel `अ`. This prevents a doctrinal prose label from becoming
an incorrect data type.

## 64-Cell Search Result

A lawful retail listing was located for the 1972 *Sarvatobhadra Chakra* with
*Trailokya Dipika* commentary by Pt. Mithalal Vyas. The book has not been
acquired or page-certified. Public snippets and modern summaries did not
supply an edition-stable complete 64-cell mapping, so no coordinates were
implemented.

## Verification Evidence

- Focused Phase 2A/2B grid suite: 15 passed in 5.41 seconds.
- Full repository suite: 203 passed in 76.59 seconds.
- Ruff lint on changed Python files: clean.
- Ruff format check on changed Python files: clean.
- JSON-schema/runtime layer parity: covered by regression test.
- `git diff --check`: clean.
- Deterministic profile hash:
  `7C772792EADDAE88DF8612B55E0A6FBD2E699E3A2C3CD95101E8A93868984D45`.
- Compiled layer counts: 28 nakshatra, 20 name initial, 12 rashi,
  5 tithi group, 16 vowel, and 7 weekday entries.
- Compiled status: `complete=false`; unresolved layer:
  `CARDINAL_ORIENTATION` only.

## Not Certified

This report does not certify absolute cardinal orientation, a universal choice
between 64 and 81 cells, Abhijit longitude insertion, Vedha, Latta, prediction,
financial edge, desktop-app behavior, or execution.
