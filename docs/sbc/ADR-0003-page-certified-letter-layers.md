# ADR-0003: Page-Certified Sanskrit Letter Layers

Status: accepted for Phase 2B research fixtures

Date: 2026-07-17

## Context

Phase 2A deliberately left the 16-vowel and 20-item inner letter ring
unresolved. Higher-resolution inspection now provides two held page witnesses:

- the editor-supplied Sarvatobhadra material in the 1937 Subrahmanya Sastri
  edition of *Phaladeepika*, PDF pages 347-348, printed pages 310-311;
- Sanjay Rath, *The Crux of Vedic Astrology - Timing of Events*, PDF page 21,
  printed page 10, Figure 1.2.

The 1937 construction text states that 16 vowels begin with `अ` in the outer
north-east corner and continue through the four corners of four nested
squares. It also lists five name sounds for each cardinal side. After applying
the already-recorded `ROTATE_CCW_90` comparison transform, these positions
agree with Rath Figure 1.2.

The source calls the 20-item ring consonantal, but its first item is the vowel
`अ`. A machine layer named `CONSONANT` would therefore encode a false claim.

## Decision

1. Certify exactly 16 `VOWEL` entries and 20 `NAME_INITIAL` entries in the
   existing Rath figure-relative coordinate frame.
2. Store an uppercase ASCII token, exact Devanagari glyph, lowercase ASCII
   transliteration, and machine semantic role for every letter entry.
3. Mark `अ` in the name-initial ring as
   `VOWEL_EXCEPTION_IN_NAME_INITIAL_RING`; mark the other 19 entries as
   `CONSONANT_NAME_INITIAL`.
4. Require all letter entries to resolve to both held page witnesses.
5. Fail validation when a letter field is missing, a semantic role is wrong,
   or a structural layer carries transcription metadata.
6. Keep absolute cardinal orientation unresolved. The letter transcription
   does not choose between page orientation conventions.
7. Keep the 64-cell compiler blocked. A retail acquisition lead is not a
   page-certified mapping.
8. Keep Vedha, Latta, scoring, financial labels, trades, MT5 execution, and
   default profile selection blocked.

## Consequences

- The 81-cell fixture can reproduce the complete visible structural and letter
  content of the two held figures without claiming an absolute compass frame.
- Consumers can distinguish text identity, display glyph, transliteration, and
  semantic exception without parsing one overloaded string.
- `complete` remains false because cardinal orientation is still unresolved.
- No predictive or trading behavior is unlocked by this decision.
