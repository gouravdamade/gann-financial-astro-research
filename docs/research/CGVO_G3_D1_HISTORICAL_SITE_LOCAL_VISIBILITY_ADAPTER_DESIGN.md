# CGVO-G3-D1 Historical-Site Local Visibility Adapter Design

## Decision

CGVO-G3-D1 implements the directive's narrow read-only prototype route. The
route is justified because the existing CGVO local-circumstances engine already
calculates topocentric eclipse facts from a canonical event and one locality.
The prototype does not introduce a second eclipse engine, a spatial model, a
region calculation, a source-effect rule, or a product UI.

Starting baseline: `03a8c1c8562c8c17c89cff55ecb36ac4bad78b04`.

Files inspected before implementation:

- `CURRENT_PROJECT_HANDOFF.md`
- `docs/research/CGVO_G2_R1A_COORDINATE_INTEGRITY_HARDENING.md`
- `configs/research/cgvo/cgvo_g2_r1_historical_site_coordinate_evidence_v1.json`
- `configs/research/cgvo/kurma_research_footprints_g2_v1.json`
- `configs/research/cgvo/cgvo_g2_readiness_matrix_v1.json`
- `configs/research/cgvo/kurma_historical_geography_g1_v1.json`
- `gann-astro-desk/backend/cgvo_service.py`
- `gann-astro-desk/backend/server.py`
- CGVO service and API tests.

## Route and Event Identity

The read-only endpoint is:

`POST /api/experiments/cgvo/historical-gazetteer/site-visibility-audit`

The request must provide all of:

- `eventId`
- `eventType`
- `globalMaxSwissUt`
- `siteEvidenceId`

The event type and Swiss UT maximum are used to reconstruct one Swiss
Ephemeris event. The reconstructed causal event ID must match `eventId`
exactly. The route has no nearest-event fallback, range scan, market-date
selection, cached event trust, or implicit event selection.

## Taxila-only Eligibility Chain

The only permitted identifier is `G2R1_TAKSASILA_TAXILA_SITE_01`. Before every
audit the adapter calls `build_cgvo_historical_research_footprints`, which
revalidates the G2-R1A evidence binding and raw DMS normalization. It then
requires:

- `RESEARCH_ANCHOR_POINT` geometry;
- `RESEARCH_GEOMETRY_ONLY` role;
- `PARTIAL_HISTORICAL_CONTEXT` or `FULL_SITE_IDENTITY_ONLY` coverage;
- all G2 downstream, market, and execution locks false;
- `regionRepresentationAllowed=false`.

The locality is named **Taxila research site anchor**. It is not named
Gandhara, does not define the Taxila settlement complex, and does not define a
Gandhara point, boundary, centroid, envelope, or footprint.

Mathuraka/Mathura, Rajagriha/Rajgir, Pataliputra, and Pushkalavati/Charsadda
remain non-coordinate-bearing. Kamboja remains contested and unmerged. Sindhu
remains a river-system context. All `SOURCE_NAME_ONLY` G1 records remain
ineligible. Each is rejected through a typed JSON error.

## Local Circumstances

The adapter calls the existing `_local_circumstances` implementation. It does
not duplicate the Swiss Ephemeris eclipse calculation. The evidence-bound
Taxila WGS84 latitude and longitude are passed to that engine only after the
G2-R1A contract validates.

Taxila elevation is not evidenced. The public audit records `elevationM=null`
and `UNKNOWN_NOT_EVIDENCED`. Swiss Ephemeris needs a numerical height, so the
calculation explicitly uses `0.0` metres as an engineering input labelled
`ENGINEERING_ZERO_METRE_DEFAULT_NOT_SOURCE_EVIDENCE`; it is not asserted as a
historical or surveyed Taxila elevation.

The only result statuses are:

- `VISIBLE_AT_RESEARCH_SITE`
- `NOT_VISIBLE_AT_RESEARCH_SITE`
- `RISE_SET_CLIPPED_AT_RESEARCH_SITE`
- `UNKNOWN_LOCAL_CIRCUMSTANCES_ERROR`

All describe modern astronomy at an evidence-bound research point.

## Source Composition Boundary

The route may display the G1 Gandhara candidate only as Chapter XIV provenance
for the Taxila research site. It does not compose that context with Chapter V
eclipse effects.

Therefore the output always contains:

- `sourceEffectActivation: null`
- `regionVisibility: null`
- `regionExtrapolationAuthorized: false`
- `chapterVEffectActivationAuthorized: false`
- `chapterXivChapterVCompositionAuthorized: false`

`VISIBLE_AT_RESEARCH_SITE` is never `VISIBLE_IN_GANDHARA`, and no visibility
fact is an effect activation, spatial match, score, polarity, market signal,
or execution input.

## Guardrails and Stop State

No polygon, buffer, distance, path overlap, GIS dependency, historical eclipse
scan, price/outcome read, FX/currency mapping, Fields, SBC, Auto Suggest, ML,
MT5, broker, or execution behavior was added. The route and fixtures retain
`downstreamIntersectionAuthorized=false`, `marketUseAllowed=false`, and
`executionAllowed=false`.

No UI and no Windows package belong to D1. Central review is required before
any G3-R1 or G3-D1-R1 work.
