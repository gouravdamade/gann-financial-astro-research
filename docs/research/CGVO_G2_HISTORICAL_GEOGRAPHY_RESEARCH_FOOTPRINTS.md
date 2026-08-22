# CGVO-G2: Historical Geography Research Footprints

## Purpose

CGVO-G2 adds a separate research-footprint ledger on top of the accepted
`CGVO-G1-R1` historical-name ledger. The layers are deliberately distinct:

`SOURCE_OCCURRENCE != CANDIDATE_IDENTITY != RESEARCH_GEOMETRY != DOWNSTREAM_SPATIAL_MATCH != MARKET_USE`

The base G1 gazetteer remains immutable in meaning: all 308 source occurrences
retain `geometry: null`, raw source category remains `UNKNOWN`, candidate
identity remains an overlay, and no geometry is active in that response.

## Contract and Guardrails

`GET /api/experiments/cgvo/historical-gazetteer/research-footprints` returns
`CGVO_HISTORICAL_GEOGRAPHY_RESEARCH_FOOTPRINTS_V1`. Every output row has
`geometryRole: RESEARCH_GEOMETRY_ONLY`, copied evidence from an already
accepted G1 candidate mapping, temporal applicability, uncertainty, and
limitations.

The route is read-only. The following remain false: automatic union,
automatic intersection, majority vote, cross-source composition, downstream
intersection authorization, eclipse-visibility matching, price/outcome access,
market use, Fields/SBC routing, Auto Suggest, ML, MT5, and execution.

## Geometry Vocabulary

- `RESEARCH_ANCHOR_POINT`: a historically identified site anchor for audit.
- `RESEARCH_MULTI_ANCHOR`: several historical centres without a region proxy.
- `RESEARCH_CORRIDOR_OR_RIVER_SYSTEM`: river/system context, never a land polygon.
- `RESEARCH_BROAD_UNCERTAINTY_ENVELOPE`: an explicitly uncertain broad region.
- `CONTESTED_RESEARCH_GEOMETRIES`: distinct, unmerged alternatives.
- `GEOMETRY_PENDING_EVIDENCE`: a reviewed identity lacking audited footprint evidence.
- `GEOMETRY_PROHIBITED`: no research footprint is allowed.

G2 does not claim that any of these are a historical boundary, an affected
zone, an eclipse-visibility match, or a market input.

## Current Footprint Ledger

No coordinates or polygons are admitted in this first pass. This is intentional:
the existing G1 evidence identifies candidate historical contexts, but does not
yet source-close coordinate-specific historical centres or an uncertainty method
for regional envelopes.

| G1 candidate term | G2 status | Primitive | Evidence and uncertainty conclusion |
| --- | --- | --- | --- |
| Magadha | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | Rajgir/Pataliputra context is retained; no independently audited anchor coordinates. |
| Mithila | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | Changing north-Bihar/Terai cultural context; no envelope. |
| Kalinga | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | East-coast association is not a source-authorized extent. |
| Saurashtra | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | Peninsula association does not justify a Gujarat polygon or an envelope. |
| Gandhara | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | Multi-region context needs distinct site evidence. |
| Kamboja, northwest alternative | `CONTESTED_RESEARCH_GEOMETRIES` | `MULTI_CANDIDATE` | Explicitly separate, no footprint and no preferred alternative. |
| Kamboja, Central Asian alternative | `CONTESTED_RESEARCH_GEOMETRIES` | `MULTI_CANDIDATE` | Explicitly separate, no footprint and no merged geometry. |
| Kashmira | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | Valley/highland extent is period-dependent. |
| Kuru | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | Upper-Yamuna/Indraprastha context requires an independent centre audit. |
| Pancala | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | Upper-Ganges context is not a boundary. |
| Mathuraka | `GEOMETRY_PENDING_EVIDENCE` | `NONE` | Mathura association remains `PEOPLE_OR_URBAN_ASSOCIATION`; no point is admitted. |
| Sindhu | `RESEARCH_CORRIDOR_OR_RIVER_SYSTEM` | `RIVER_SYSTEM_CONTEXT` | Indus context only; no digitised corridor, adjacent land extent, or land polygon. |

There are 12 ledger rows for 11 reviewed terms because the two Kamboja
alternatives remain structurally separate. No reviewed footprint exists for
source-name-only entries such as Cina, Yavana, Kirata, Huna, Lanka, or
Suvarnabhumi.

## Validation

The backend rejects a footprint when it has missing evidence, uncertainty,
temporal applicability, or limitations; when it references a source-name-only
record; when a pending record contains geometry data; when a contested
alternative is merged; or when Sindhu implies adjacent land. A coordinate-bearing
record would additionally require an explicit coordinate source.

## Deferred Work

G2 adds neither a map UI nor any spatial comparison. The immediate blocker is
targeted historical-site/coordinate evidence and an evidence-honest uncertainty
method for selected candidates. A later G2-R1 review can decide whether that
evidence warrants a few research anchors; G3 should remain a design review for
visibility-footprint comparison, not an implementation of matching.
