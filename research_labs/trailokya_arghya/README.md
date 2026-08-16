# Trailokya Dipika Arghya Reconciliation Lab

This isolated lab records a double transcription of three numeric tables from
the 1972 Tej Kumar edition and the 2016 Khemraj reprint of the same Mithalal
Vyas textual lineage.

## What is certified here

- Each edition contributes 108 table cells.
- The two passes agree cell for cell.
- `Viswa|Kala` is parsed sexagesimally: `11|15 = 11.25`.
- Bars in the planetary-aspect table list houses and are not sexagesimal.
- The literal table and twenty-part commodity-basis stages can be inspected as
  a direction-free source-reconstruction check.

## What the source itself makes suspicious

Both editions preserve two values that break their tables' own proportional
pattern:

- relationship / three-quarter / malefic-neutral: printed `11|45`, expected
  `11|15` from three quarters of `15|0`;
- five-class / three-quarter / four malefics: printed `2|18`, expected `2|24`
  from three quarters of `3|12`.

They are retained as source data and surfaced by the validator. They are not
silently emended.

## TD3R source correction

TD3R rechecked the controlling 1972 page images. The historical 1972 pass has
the right literal values, but its printed-page locators are stale: its tables
are on printed pp.82, 83 and 85, not pp.52, 53 and 55. The separately named
TD3R corrected pass preserves all 108 literals and the historical CSV remains
in place for provenance.

TD3R also establishes that verse 376's `20` is a current commodity-basis
quantity. Earlier reference-price-unit experiments remain historical,
execution-locked research evidence; they are not the controlling 1972 Argha
contract and cannot create a price equation.

## Safety boundary

The later reprint is a reading witness, not independent doctrine. This lab can
say only that a source commodity basis above or below twenty has historical
availability/scarcity semantics. It cannot produce a direct predicted price, a
modern bullish/bearish label, an Auto Suggest input, an official ML note, or an
MT5 order. `refuse_predicted_price()` fails closed by design.

Run the audit with:

```powershell
python -m research_labs.trailokya_arghya.reconcile
```
