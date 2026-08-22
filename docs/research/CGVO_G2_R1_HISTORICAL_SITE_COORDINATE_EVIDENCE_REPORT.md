# CGVO-G2-R1 Historical Site and Coordinate Evidence Report

## Scope and Result

This is a narrow, read-only historical-site evidence pass over the accepted
`CGVO-G1-R1` name/candidate overlay. It preserves all 308 G1 source
occurrences and their `geometry: null` state. It does not create a historical
region boundary, eclipse footprint, visibility match, market signal, score,
or execution path.

The result is one `RESEARCH_ANCHOR_POINT`: Taxila, as a limited archaeological
site reference relevant to the Gandhara candidate. It is explicitly
`PARTIAL_HISTORICAL_CONTEXT`, never a Gandhara proxy. Mathuraka/Mathura,
Rajagriha/Rajgir, Pataliputra, and Pushkalavati/Charsadda were audited but not
activated as geometry.

## Evidence Method

Historical identity and coordinate provenance are independent fields. An
active point must carry a finite latitude/longitude, WGS84, explicit
latitude/longitude axis order, raw source coordinate, precision, source
identifier/locator/type, interpretation, normalization method, separate
historical identity evidence, uncertainty, temporal applicability, and
limitations. A point cannot carry centroids, polygons, envelopes, or
multi-point data, and it cannot represent a historical region.

## Target Findings

| Target | Historical-site finding | Coordinate finding | G2-R1 outcome |
| --- | --- | --- | --- |
| Mathuraka / Mathura | G1 keeps a people-or-urban association; Oxford describes a multi-layered archaeological landscape. | UNESCO publishes a raw DMS pair for an ancient Mathura site, but the held listing does not declare a CRS or reference-point meaning. | `GEOMETRY_PENDING_EVIDENCE` |
| Magadha / Rajagriha-Rajgir | ASI and academic evidence support the ancient Rajagriha/Rajgir site context. | UNESCO raw DMS coordinate has unresolved CRS/locus semantics in a multi-structure complex. | `GEOMETRY_PENDING_EVIDENCE` |
| Magadha / Pataliputra | ASI and Patna evidence identify Kumrahar and Bulandibagh as distinct Pataliputra contexts. | UNESCO raw DMS coordinate does not identify a CRS or select one archaeological locus. | `GEOMETRY_PENDING_EVIDENCE` |
| Gandhara / Taxila | UNESCO identifies the serial Taxila archaeological property; Iranica places Taxila among central Gandharan cities. | Getty TGN 6005850 supplies WGS84 `33 degrees 45 minutes 35 seconds N 72 degrees 50 minutes 15 seconds E`, normalized to `33.7597222222, 72.8375`. | One `RESEARCH_ANCHOR_POINT`, site-reference only |
| Gandhara / Pushkalavati-Charsadda | Iranica and archaeological project evidence support the historical-site context. | Getty TGN and Pleiades points are about 9,606.3 m apart and describe different reference constructions. No selection or averaging is legitimate. | `COORDINATE_REFERENCE_CONFLICT`, no geometry |

## Source Register

- UNESCO World Heritage, [Taxila](https://whc.unesco.org/en/list/139), supports
  the serial archaeological-property context and is not used to make Taxila a
  Gandhara boundary.
- Getty TGN, [Taxila record 6005850](https://www.getty.edu/vow/TGNFullDisplay?english=Y&find=&nation=&place=&subjectid=6005850), is the coordinate-bearing gazetteer record. Getty's
  [editorial guidelines](https://www.getty.edu/publications/vocabularies-editorial-guidelines/tgn-guidelines/3_editorial_rules/3.7/)
  document WGS84 treatment.
- Encyclopaedia Iranica, [Gandhara](https://www.iranicaonline.org/articles/gandhara/),
  supports Taxila and Pushkalavati/Charsadda as Gandharan historical contexts.
- Pleiades [place 59993](https://pleiades.stoa.org/places/59993/json) is retained
  as a conflicting Pushkalavati reference, not normalized into an anchor.
- ASI Patna Circle [monument records](https://asipatnacircle.gov.in/monuments-details)
  and the [Patna Kumhrar record](https://patna.nic.in/tourist-place/kumhrar-park/)
  support the separate Rajgir/Pataliputra archaeological contexts.
- UNESCO's [Uttarapath tentative-list entry](https://whc.unesco.org/en/tentativelists/6056)
  supplies the raw Mathura/Rajgir/Pataliputra coordinate strings but does not
  close their CRS/locus metadata in the held listing.

## Contract and Guardrails

The machine-readable audit is
`configs/research/cgvo/cgvo_g2_r1_historical_site_coordinate_evidence_v1.json`.
The endpoint remains
`GET /api/experiments/cgvo/historical-gazetteer/research-footprints` and now
returns `CGVO_HISTORICAL_GEOGRAPHY_RESEARCH_FOOTPRINTS_V2`.

All of the following remain false: downstream spatial intersection,
eclipse-visibility matching, price reads, price-outcome reads, direction,
score aggregation, Fields, SBC, Auto Suggest, ML, MT5, market use, and
execution. `executionAllowed=false`.

## Remaining Gaps

No polygon, centroid, regional envelope, visibility locality, or market
interpretation is authorized. A future decision must separately authorize any
G3 spatial work. It must not use the Taxila point as a substitute for the
historical extent of Gandhara.
