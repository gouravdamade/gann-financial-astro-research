# PFR-V2B-4 Shared Range Coordinator

## Purpose

`SYNCHRONIZED_INDEPENDENT_RANGE_V1` gives the categorical chart-conditioned
aspect field and the SBC atomic field one exact offset-aware visible range. It
is a transport and integrity contract for the following rendering milestone;
it is not a combined oscillator.

## Request

The private route is `POST /api/independent-fields/synchronized-range`.

- `rangeStartUtc` and `rangeEndUtc` are the only shared time selection.
- `aspectRanges` must include exactly one independently compiled USD primary
  side and one independently compiled JPY primary side.
- `sbcRange` supplies existing SBC boundaries. Its first resulting interval
  must start exactly at `rangeStartUtc`; its terminal end is set from the
  shared `rangeEndUtc`.

The coordinator rejects missing, duplicated, cross-side, naive, or mismatched
ranges. It never expands or truncates one field to make a match look valid.

## Output and Limits

The output nests three untouched independent products: USD categorical range,
JPY categorical range, and SBC atomic range. It records
`synchronizationStatus=SYNCHRONIZED` only when every returned boundary equals
the shared range.

`fieldsFused=false`, `actsAsSbcConfirmation=false`, and
`marketDirectionInferred=false` are hard contract guardrails. No smoothing,
calibration, market call, or execution path is introduced.

## Verification

The service test proves that all three fields share the exact UTC range while
retaining field separation. A second test proves an SBC boundary that begins
fifteen minutes late fails closed rather than being silently aligned.
