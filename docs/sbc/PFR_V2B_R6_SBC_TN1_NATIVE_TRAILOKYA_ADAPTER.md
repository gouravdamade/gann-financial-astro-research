# PFR-V2B-R6-SBC-TN1 - Native Trailokya Adapter

## Scope

TN1 provides a read-only Chakra inspector for the source-closed Trailokya
Dipika 1972 board and enumerated target rows. It does not create a market
signal, a score, polarity, a Fields input, Auto Suggest input, ML feature,
price mapping, MT5 action, or executable order path.

## Authority Boundary

`TRAILOKYA_1972_ENUMERATED_NAKSHATRA_TARGETS_V1` is the exclusive authority
for direct target identity, order, and the single FRONT target. The native
`TRAILOKYA_1972_NATIVE_AKHANDA_81_BOARD_V1` board is a visual projection and
mapping aid only. A generic or Phaladeepika-derived grid cannot replace a
missing Trailokya row.

The adapter exposes direct source targets first and semantic expansions from
verses 48-52 second. Every expansion retains the same `sourceEventId` and
`causalVedhaEventId` as its originating direct target. It is not a new vote.

## Native Board

The board is rendered straight from the committed `cellProjection` in
`trailokya_1972_chakra_construction_v1.yaml`: EAST at the top, WEST at the
bottom, NORTH left, SOUTH right. It has 81 source cells and includes Abhijit.
Source literals and normalized display labels remain distinct.

The visible fixture has two `A` glyphs but does not assign a unique layer to
both instances. When `VOWEL:A` is requested, the adapter reports
`AMBIGUOUS_SOURCE_PROJECTION` and does not choose a physical cell. This is a
projection-only gap; the enumerated source row remains available and controls
the target identity.

## Manual Audit

The Chakra profile selector exposes **Trailokya 1972 Research**. Its Manual
Source Audit lets the reviewer select one of the 28 nakshatras and LEFT,
FRONT, or RIGHT. It does not use ephemeris or market data. Without an explicit
target context every target has `reachState=UNKNOWN`; it is never converted to
`NOT_REACHED` or zero.

## Snapshot Boundary

The backend includes a timestamp-safe native source snapshot route for later
use. It may obtain astronomy/context facts through `ChakraLabEngine.source_context`,
which deliberately compiles neither a generic grid nor a Vedha guidance
engine. Current TN1 UI is manual-only. Unlisted variable-body and stationary
conditions remain unavailable rather than inferred from instantaneous speed.

## Locks

`executionAllowed=false`, source-only mode remains non-financial, and
`TRAILOKYA_GENERIC_GRID_FALLBACK_ALLOWED=false`. Existing Fields continues to
display `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED`; TN1 does not compile a range or
wave.

## Founder Inspection

Inspect Chakra -> Vedha source profile -> Trailokya 1972 Research:

1. confirm 81 cells and the EAST/WEST/NORTH/SOUTH frame;
2. select Jyeshtha + LEFT and verify the direct order is YA, Sagittarius,
   Visarga, Pisces, CHA, Ashvini;
3. switch to FRONT and verify exactly one direct target, Pushya;
4. inspect the derived tray and ensure it shares one causal event rather than
   adding a score;
5. confirm the unknown panel is visible and there is no bullish/bearish,
   numeric score, price, or execution affordance.
