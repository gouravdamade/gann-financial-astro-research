# CGVO-G1-R1: Historical Geography Evidence Integrity Correction

## Scope

This bounded correction starts from the committed G1 read-only gazetteer. It
does not add a map, coordinate, geometry operation, astronomical computation,
market input, or prediction path.

## Corrections

All generated Chapter XIV records now use the source locator format
`Brihat Samhita 14.2-14.4`; the invalid doubled chapter form was removed.

`rawSourceCategory` is now an explicit root-witness field. It remains
`UNKNOWN` with status `NOT_CLASSIFIED_FROM_ROOT_SOURCE` for every record. A
candidate overlay can supply `candidateEntityType` only as a separate research
interpretation.

Māthuraka is a root list literal, not a source-closed modern category. The
overlay is limited to `PEOPLE_OR_URBAN_ASSOCIATION`, based on a direct
Chapter-XIV translation/gloss and an independent lexical association with
Mathura. The old Cambridge Surasena wording is retained as secondary context,
not identity proof.

## Locked Audit Counts

The compiler emits 308 contextual source-name occurrences:

- `SOURCE_NAME_ONLY`: 297
- `HIGH_CONFIDENCE_CANDIDATE`: 6
- `MEDIUM_CONFIDENCE_CANDIDATE`: 3
- `APPROXIMATE_REGION_ONLY`: 1
- `CONTESTED_CANDIDATES`: 1
- `UNMAPPED`: 0

The directional occurrence counts are `CENTER=32`, `EAST=33`,
`SOUTHEAST=28`, `SOUTH=65`, `SOUTHWEST=29`, `WEST=19`, `NORTHWEST=15`,
`NORTH=52`, and `NORTHEAST=35`. Repeated names are preserved as independent
Chapter XIV directional/list occurrences; they are not deduplicated into a
single modern entity.

## Boundary

This record remains a read-only evidence ledger. It does not authorise
geometric inclusion, astronomical processing, price or outcome reads, polarity,
score aggregation, Fields/SBC routing, Auto Suggest, ML, MT5, or execution.
