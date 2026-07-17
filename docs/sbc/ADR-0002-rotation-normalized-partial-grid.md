# ADR-0002: Rotation-Normalized Partial 81-Cell Fixture

Status: accepted for Phase 2A research fixtures

Date: 2026-07-17

## Context

Two locally held editions show an 81-cell Sarvatobhadra layout:

- the editor-supplied Sarvatobhadra supplement in the 1937 Subrahmanya
  Sastri edition of *Phaladeepika*, PDF pages 347-349, printed pages 310-312;
- Sanjay Rath, *The Crux of Vedic Astrology - Timing of Events*, PDF page
  21, printed page 10, Figure 1.2.

They agree on the grid topology, 28-nakshatra sequence including Abhijit,
12-rashi ring, and five tithi/weekday center groups. They do not provide the
same absolute page orientation. The 1937 plate labels North, East, South, and
West; Rath's figure has no cardinal labels and equals the plate only after a
90-degree counter-clockwise rotation.

The 1937 material must also be cited accurately. Mantreswara 26.48 occurs on
PDF page 341. The grid material on PDF pages 342-356 is an editor-supplied
extract/free rendering, including Horaratna material. It is not silently
promoted to root Mantreswara doctrine.

## Decision

1. Add one explicit-only, figure-relative profile named
   `sbc_81_rotation_normalized_partial_v1`.
2. Use Rath Figure 1.2 as the profile's row/column coordinate frame.
3. Record the 1937 plate as a topology witness with
   `ROTATE_CCW_90`, never as an identical cardinal frame.
4. Compile only four page-certifiable structural layers: nakshatra, rashi,
   tithi group, and weekday.
5. Keep vowel and consonant glyph transcription unresolved until a separate
   checked transliteration fixture is approved.
6. Keep absolute cardinal binding unresolved.
7. Add `sbc_64_blocked_v1` as metadata only. Compilation must raise an error
   because no locally held page-certified 64-cell mapping is available.
8. Provide no implicit/default grid selection.
9. Keep Vedha, Latta, scoring, financial labels, Auto Suggest, and execution
   unavailable.

## Consequences

- The project can test deterministic grid topology without pretending that a
  complete doctrinal SBC implementation exists.
- Each compiled entry carries its witness set and page locator.
- A source rotation conflict becomes data rather than an undocumented UI
  choice.
- The fixture is suitable for a future read-only comparison lab, but it is not
  suitable for prediction or trading.
