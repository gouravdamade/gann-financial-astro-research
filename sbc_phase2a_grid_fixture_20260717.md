# SBC Phase 2A Grid Fixture Acceptance Report

Date: 2026-07-17 IST

Status: accepted as an incomplete, explicit-only topology fixture

## Scope Delivered

- strict source-gated grid profile compiler
- deterministic 9x9/81-cell container
- 28 nakshatras including Abhijit, each exactly once
- 12 rashis, each exactly once
- five tithi groups and seven weekday mappings
- page citations resolved into every compiled entry
- machine-visible 90-degree rotation between the 1937 cardinals-labeled plate
  and the Rath Figure 1.2 coordinate frame
- explicit `complete=false` while letter layers and cardinal binding remain
  unresolved
- metadata-only 64-cell profile that fails closed on compilation
- hard locks for default selection, Vedha, Latta, scoring, financial labels,
  trades, and MT5 execution

## Source Evidence

- Phaladeepika 1937 Subrahmanya Sastri edition, PDF pages 347-349, printed
  pages 310-312. This is editor-supplied supplement material, not root
  Mantreswara 26.48.
- Sanjay Rath, *The Crux of Vedic Astrology - Timing of Events*, PDF page 21,
  printed page 10, Figure 1.2. This is secondary commentary and supplies the
  figure-relative row/column frame.

The sources agree on topology only after rotating the 1937 plate 90 degrees
counter-clockwise into the Rath frame. No absolute cardinal orientation is
claimed.

## Test Evidence

- Focused Phase 2A suite after formatting: 8 passed in 2.93 seconds.
- Full repository suite: 196 passed in 59.79 seconds.
- Ruff lint: clean.
- Ruff format check: clean.
- `git diff --check`: no whitespace errors before staging.

## Not Certified

This report does not certify the 81-cell form as a universal/default choice,
the 64-cell mapping, Sanskrit vowel/consonant transcription, absolute cardinal
orientation, Abhijit longitude insertion, Vedha, Latta, prediction, financial
edge, or execution.

## Recommended Next Gate

Prepare a separately reviewed Sanskrit letter transcription fixture and obtain
a page-certified 64-cell edition. Keep both as explicit comparison profiles;
do not promote either into the desktop app until cardinal orientation and an
independent fixture comparison are resolved.
