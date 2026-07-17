# ADR-0004: Source-Profiled Vedha Guidance

Status: accepted for Phase 3A research guidance

Date: 2026-07-17

## Context

The editor-supplied Sarvatobhadra supplement in the 1937 Subrahmanya Sastri
edition of *Phaladeepika* gives:

- natural and conditional planet nature;
- left, front, and right Vedha;
- complete worked target lists for Krittika, Rohini, and Mrigashira;
- motion-to-direction rules;
- retrograde, exalted, and debilitated effect multipliers.

Sanjay Rath's printed page 11 independently summarizes the normal/front,
swift/next, and retrograde/previous motion distinction. Other sources and
schools describe different star-count, Panchashalaka, Saptashalaka, fixed-body,
and exception rules. They cannot be merged silently.

The held source also uses severe natal/electional human-event language. That
language is not evidence of a market, price, or risk mapping.

## Decision

1. Add the explicit-only profile
   `phaladeepika_editor_vedha_guidance_v1`.
2. Derive standard rays in the figure-relative frame:
   - left: inward plus figure-left diagonal;
   - front: opposite outer nakshatra only;
   - right: inward plus figure-right diagonal.
3. Validate every engine construction against the three printed nine-target
   examples.
4. Require explicit `DIRECT_SWIFT`, `MEAN`, or `RETROGRADE` for Mars,
   Mercury, Jupiter, Venus, and Saturn. Do not invent speed thresholds.
5. Keep Sun/Moon fixed left and Rahu/Ketu fixed right within this profile only.
6. Resolve Jupiter/Venus as natural benefics and Saturn/Sun/Rahu/Ketu/Mars as
   natural malefics. Keep Mercury and Moon conditional unless context is
   supplied.
7. Add `EXPERIMENTAL_NORMALIZED_GUIDANCE_V1`:
   - one engineering unit per matched layer;
   - benefic `+1`, malefic `-1`;
   - source modifiers `2x` retrograde, `3x` exalted, `0.5x` debilitated;
   - no score for unresolved nature or multiplier precedence;
   - normalized balance equals net divided by total absolute scored evidence.
8. Block stacking when retrograde and non-ordinary dignity occur together.
9. Emit no bullish/bearish label, price forecast, trade, Auto Suggest, or MT5
   instruction.

## Consequences

- The project gains deterministic Vedha guidance with a complete decision
  trail rather than an opaque magic score.
- Source statements and engineering normalization remain distinguishable.
- Uncertainty lowers scoring coverage instead of being converted into a guess.
- Financial usefulness still requires timestamp-safe, out-of-sample validation
  in a later phase.
- Special corner rules, other Vedha schools, Latta, and app integration remain
  separate work.
