# Vedha Guidance Source Audit

Date: 2026-07-17

## Held Evidence

Primary executable profile witness:

- `PHALADEEPIKA_1937_SBC_EDITOR_SUPPLEMENT`
- PDF pages 349-351, printed pages 312-314
- editor-supplied Horaratna/Rajavijaya material, not Mantreswara root text

Independent comparison witness:

- `SANJAY_RATH_CRUX_1998_SBC_MOTION_SUMMARY`
- PDF page 22, printed page 11
- modern secondary commentary

## Page-Certified Rules

- Standard board Vedha has left, front, and right directions.
- Krittika, Rohini, and Mrigashira each have nine explicitly listed targets.
- In this selected profile Sun/Moon use left; Rahu/Ketu use right.
- For Mars, Mercury, Jupiter, Venus, and Saturn:
  - swift direct uses left;
  - mean motion uses front;
  - retrograde uses right.
- Natural malefics are Saturn, Sun, Rahu, Ketu, and Mars.
- Jupiter and Venus are natural benefics.
- Mercury depends on association; waning Moon is malefic.
- Effect modifiers are `2x` retrograde, `3x` exalted, ordinary for rapid
  direct, and `0.5x` debilitated.

## Machine Normalization

The source does not publish a financial score. Phase 3A therefore uses an
explicit experimental normalization:

```text
signed units = one matched layer
             x resolved benefic/malefic sign
             x one unambiguous source modifier

normalized score = net signed units / total absolute scored units
```

The result is guidance for comparison only. It is not a probability, expected
return, position size, confidence score, or trade direction.

## Deliberate Blocks

- no automatic numerical threshold for direct swift versus mean motion;
- no retrograde-plus-dignity stacking or precedence assumption;
- no inferred Mercury association;
- no special corner/junction or pada rules;
- no star-count, Panchashalaka, Saptashalaka, or Latta merger;
- no conversion of historical sickness/death/loss language into market risk;
- no financial labels, trades, or MT5.

## Semantic Exception

The worked Krittika and Mrigashira prose calls the glyph `A` a vowel, while its
board cell sits in the source-described consonant ring. The Phase 2B machine
layer already records this as `NAME_INITIAL:A` with semantic role
`VOWEL_EXCEPTION_IN_NAME_INITIAL_RING`. Phase 3A keeps that exact cell identity
instead of creating a duplicate synthetic vowel target.
