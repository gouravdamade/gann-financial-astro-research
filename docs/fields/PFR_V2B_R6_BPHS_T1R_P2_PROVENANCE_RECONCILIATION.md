# PFR-V2B-R6-BPHS-T1R-P2 - Provenance Reconciliation Only

## Scope and stop boundary

This is a source-provenance correction against the held original
`BPHS_1899_GOVIND_SHARMA_SHASTRI`, 1899 Purva/Uttara witness, SHA-256
`BB556804D8D546ACC39C43A22CECDBE2C29E3A7BA157E60EEC810C478EB645A4`.
It changes no calendar calculation, classical activation, polarity, score,
market mapping, SBC behavior, review decision, Auto Suggest, ML, MT5, or
execution behavior.

## Muhurta locator result

The original-witness page images settle the locator conflict:

- printed page 196 / PDF image 679: Chapter 14 lead-in and the root-text
  continuation that introduces the thirty Muhurtas;
- **printed page 197 / PDF image 680: complete source facsimile of the ordered
  fifteen daytime and fifteen nighttime names**, repeated in Sanskrit
  commentary and Hindi Bhasha;
- printed page 198 / PDF image 681: continuation of Chapter 14, not the
  complete day/night table.

The fixture locator therefore remains printed p. 197 / PDF image 680. The
thirty admitted names and their order did not change. A translated-ledger
reference using `printed p. 198 / split-2 p. 306` is not substituted for the
page numbering of this held original witness.

## Tara reconciliation

The whole held Chapter 14 range was inspected: printed pages 196-258, PDF
images 679-741. Printed page 259 / PDF image 742 begins Chapter 15.

The audit did not locate the complete ninefold sequence Janma, Sampat, Vipat,
Kshema, Pratyari, Sadhaka, Vadha, Mitra, and Atimitra as an evaluable table or
operator in that held Chapter 14 range. It also did not locate a mapping or
reference rule sufficient to calculate a timestamp. The source profile now
records this as an original-witness full-range finding rather than claiming
only that Packet 1W was searched.

`Tara` remains `DEPENDENCY_NOT_READY`. Its unresolved dependencies are:

1. a complete source-closed ninefold sequence in the held source profile;
2. a source-closed mapping/operator for timestamp evaluation; and
3. an explicit, accepted reference identity.

No external Panchanga rule, modern convention, or inferred reference is used
to close those gaps.

## Engineering categories

Tithi, Nakshatra, Yoga, and Karana remain
`SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1` engineering calculations.
Their BPHS locator is now explicitly limited to chapter-level calendar-category
context. It does not claim individual source transcription of any displayed
name or transition boundary. Civil weekday remains `PARTIAL_SOURCE`, with no
new sunrise/day ownership convention.

## Verification

The focused BPHS backend suite confirms the unchanged Muhurta literal order,
the reconciled full-range Tara gap, engineering-category wording, and the
existing no-market/no-execution guardrails. This work is ready for founder
inspection only; it is not founder acceptance or certification.
