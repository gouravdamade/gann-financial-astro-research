# Trailokya Dipika Arghya Reconciliation Lab

This isolated lab records a double transcription of three numeric tables from
the 1972 Tej Kumar edition and the 2016 Khemraj reprint of the same Mithalal
Vyas textual lineage.

## What is certified here

- Each edition contributes 108 table cells.
- The two passes agree cell for cell.
- `Viswa|Kala` is parsed sexagesimally: `11|15 = 11.25`.
- Bars in the planetary-aspect table list houses and are not sexagesimal.
- The prose-supported twenty-part availability index can be calculated for a
  direction-only research sanity check.

## What the source itself makes suspicious

Both editions preserve two values that break their tables' own proportional
pattern:

- relationship / three-quarter / malefic-neutral: printed `11|45`, expected
  `11|15` from three quarters of `15|0`;
- five-class / three-quarter / four malefics: printed `2|18`, expected `2|24`
  from three quarters of `3|12`.

They are retained as source data and surfaced by the validator. They are not
silently emended.

## Safety boundary

The later reprint is a reading witness, not independent doctrine. This lab can
say only that an index above 20 is described as more availability and
lower-price pressure, while an index below 20 is described as scarcity and
higher-price pressure. It cannot produce a direct predicted price, a modern
bullish/bearish label, an Auto Suggest input, an official ML note, or an MT5
order. `refuse_predicted_price()` fails closed by design.

Run the audit with:

```powershell
python -m research_labs.trailokya_arghya.reconcile
```
