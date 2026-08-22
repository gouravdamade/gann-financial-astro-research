# CGVO-G2-R1A Coordinate Integrity Hardening

## Purpose

CGVO-G2-R1A closes the central-review engineering hold on the already accepted
G2-R1 Taxila research anchor. It does not acquire sources, add coordinates,
reinterpret historical geography, begin G3, or add a UI/package.

The footprint response keeps the backward-compatible
`CGVO_HISTORICAL_GEOGRAPHY_RESEARCH_FOOTPRINTS_V2` shape. The persisted V2
ledger retains the footprint coordinate fields, but the backend now applies
strict equality validation against the eligible site's normalized coordinate.
This was selected over a persisted-schema rewrite because it avoids unnecessary
consumer churn while making divergence fail closed before output construction.

## Binding Invariant

The active sequence is:

`historical identity evidence -> coordinate evidence -> raw coordinate -> normalized coordinate -> eligible site -> footprint`

`COORDINATE_EVIDENCE_BOUND_FIELDS` is the single canonical field set:

`latitude`, `longitude`, `coordinateReferenceSystem`, `axisOrder`,
`sourceCoordinateRaw`, `coordinatePrecision`, `coordinateSourceId`,
`coordinateSourceLocator`, `coordinateSourceType`,
`coordinateInterpretation`, and `normalizationMethod`.

`anchorId`, `anchorRole`, and `regionRepresentationAllowed` remain
footprint-level semantics. Latitude and longitude are compared as exact
canonical decimal values, not with a geographic distance tolerance. Any
mutation of the footprint copy or the evidence copy is rejected.

## DMS Normalization

The supported `DMS_TO_DECIMAL_DEGREES` path parses the repository's source
representation, including degree signs, minute marks, doubled ASCII-second
marks, Unicode prime marks, and the N/S/E/W hemispheres. It rejects missing or
malformed components, invalid hemispheres, latitude using E/W, longitude using
N/S, minutes or seconds at 60, boundary degrees with non-zero components, and
out-of-range values.

The arithmetic uses `fractions.Fraction`:

`degrees + minutes / 60 + seconds / 3600`, with S/W negative. The stored
repository representation is checked using a deterministic ten-place decimal
canonicalization. This is a numeric representation rule, not a geographic
acceptance tolerance and does not claim additional source precision.

For the accepted Taxila record:

- raw: `33° 45' 35'' N 72° 50' 15'' E`
- latitude: `33 + 45/60 + 35/3600 = 24307/720`, canonical `33.7597222222`
- longitude: `72 + 50/60 + 15/3600 = 5827/80`, canonical `72.8375000000`
- stored longitude: `72.8375`, numerically identical to the canonical value
- method: `DMS_TO_DECIMAL_DEGREES`
- CRS/axis: `WGS84` / `LATITUDE_LONGITUDE`

`SOURCE_DECIMAL_DEGREES_VERBATIM` is supported by bounded parser validation for
future evidence, but no active G2-R1A coordinate uses it.

## Negative Integrity Coverage

Focused tests reject footprint latitude, longitude, raw string, source ID, CRS,
interpretation, and normalization-method mutations. They also reject evidence
normalized latitude/raw changes that disagree with the DMS source; invalid
minutes, seconds, hemispheres, axis hemispheres, 91/181-degree values, NaN,
Infinity, centroid/midpoint/polygon/envelope geometry, source-name-only
footprints, Kamboja merges, Sindhu land geometry, and active downstream or
market safety flags.

## Historical State Preserved

- Taxila remains the sole `RESEARCH_ANCHOR_POINT` with
  `PARTIAL_HISTORICAL_CONTEXT` coverage.
- Mathuraka/Mathura remains pending.
- Magadha remains pending; Rajagriha/Rajgir and Pataliputra are not merged.
- Pushkalavati/Charsadda remains `COORDINATE_REFERENCE_CONFLICT` with the
  existing approximately 9.6 km audit difference and no selected point.
- Both Kamboja alternatives remain separate.
- Sindhu remains `RIVER_SYSTEM_CONTEXT` with null corridor, adjacent land, and
  land polygon.
- G1 remains 308 geometry-null source occurrences and G2 remains 12 rows with
  one coordinate-bearing footprint.

## Locks and Stop Gate

`downstreamIntersectionAuthorized`, `eclipseVisibilityMatching`,
`priceDataRead`, `priceOutcomeRead`, `marketDirectionInferred`,
`scoreAggregationUsed`, `fieldsPath`, `sbcPath`, `autoSuggestPath`, `mlPath`,
`mt5Path`, `marketUseAllowed`, and `executionAllowed` remain false.

No Swiss eclipse calculations, Taxila locality interpretation, spatial
intersection, market connection, UI, Windows package, or G3 work belongs to
this milestone.
