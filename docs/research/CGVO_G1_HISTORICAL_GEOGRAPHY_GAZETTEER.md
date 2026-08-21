# CGVO-G1: Historical Geography Gazetteer and Source-to-Place Mapping

## Scope

CGVO-G1 implements a read-only evidence architecture for the historical names
in the existing *Brihat Samhita* Chapter XIV / Kurmavibhaga seed. It does not
turn historical names into product regions, maps, markets, or predictions.

The runtime compiler reads the pre-existing raw Chapter XIV seed and emits one
record for every name in its nine source direction groups. Candidate mappings
are overlays: they preserve the source transliteration and supply a separate
modern-identification hypothesis, evidence, temporal limitation, confidence,
and prohibited uses.

## Source layers remain separate

The following profiles are distinct and cannot be automatically unioned,
intersected, or voted together:

- `VARAHAMIHIRA_KURMAVIBHAGA_XIV`: source-name and directional geography ledger.
- `VARAHAMIHIRA_ECLIPSE_RASI_V`: separate rasi-effect geography placeholder.
- `VARAHAMIHIRA_NAKSHATRA_DEPENDENCIES_XV`: dependency targets, not a place map.
- `TRAILOKYA_GEOGRAPHY_PLACEHOLDER_G1`: separate desa/mandala/sthana placeholder;
  no Varahamihira inheritance and no Argha computation.

The guardrail fixture keeps `automaticUnion`, `automaticIntersection`, market
and price reads, Fields/SBC routing, Auto Suggest, ML, MT5, and execution
false.

## Bounded candidate-mapping pass

The first pass prioritizes names with a reasonably stable historical centre or
large-scale regional association. It deliberately does not try to finish the
full Chapter XIV list.

| Source term | Status | Candidate identity | Why bounded |
| --- | --- | --- | --- |
| Magadha | High-confidence candidate | Rajgir/Pataliputra historical centre in Bihar context | Territory changed by period. |
| Mithila | Medium-confidence candidate | north Bihar and adjoining Terai cultural-historical context | Boundary is not fixed. |
| Kalinga | Medium-confidence candidate | Odisha/northern Andhra historical coastal context | Modern Odisha is not a replacement polygon. |
| Saurashtra | High-confidence candidate | Saurashtra/Kathiawar peninsula context | Extent remains approximate. |
| Gandhara | High-confidence candidate | Peshawar, Kabul-valley, Taxila/Charsadda historical context | A changing multi-region, not a country proxy. |
| Kamboja | Contested candidates | northwest-frontier and wider trans-Hindu-Kush alternatives | No preferred modern extent is claimed. |
| Kashmira | Medium-confidence candidate | Kashmir valley and adjoining highland context | Political extent changed. |
| Kuru | High-confidence candidate | upper Yamuna/Indraprastha context | No modern border is used. |
| Panchala | High-confidence candidate | upper Ganges context | No exact historical boundary is claimed. |
| Mathuraka | High-confidence candidate | Mathura urban-centre context | No coordinate is activated. |
| Sindhu | Approximate-region-only | Indus river-system and adjoining historical lands | River identity does not fix an adjacent land extent. |

Evidence records retain URLs/citations and limitations in
`configs/research/cgvo/kurma_historical_geography_g1_v1.json`. They use a
small set of scholarly or institutional reference points: the Cambridge
Ancient History for Magadha/Kuru/Panchala/Mathura, Encyclopaedia Iranica for
Gandhara and Indus context, the Archaeological Survey of India for the
Saurashtra/Kathiawar association, Utkal University for Kalinga/Odisha context,
and the historical-geography work of Cunningham for the bounded Mithila and
Kashmira candidates. None authorizes a contemporary administrative boundary as
an ancient polygon.

Terms such as Cīna, Yavana, Kirāta, Hūṇa, and the remaining difficult or
ambiguous Chapter XIV entries intentionally remain `SOURCE_NAME_ONLY` with an
`UNKNOWN` category until an evidence review can support a narrower claim.

## Product contract

The backend route is read-only:

`GET /api/experiments/cgvo/historical-gazetteer`

It returns `CGVO_HISTORICAL_GEOGRAPHY_GAZETTEER_V1` with source records,
candidate mappings, a summary, source-layer policy, and guardrails. It does
not call Swiss Ephemeris, price, outcome, Fields, SBC, Auto Suggest, ML, MT5,
or execution services. G1 adds no UI or Windows candidate because the
directive treats a source/API inspection surface as the bounded product and
requires central review before packaging.

## Current counts

The compiler creates 308 Chapter XIV source-name records: 297 source-name-only,
6 high-confidence candidates, 3 medium/approximate candidates, 1 contested
candidate, and no `UNMAPPED` record fabricated merely to fill a category.

Every candidate uses `geometry: null` and a non-authorizing geometry status.
No polygon, point coordinate, or downstream geographic intersection exists.

## Next blocker

CGVO-G1 is an evidence ledger only. A later G1R1 review may correct individual
candidate evidence/statuses. CGVO-G2 would require a separately approved,
source-specific geometry policy before any approximate geometry could be
enriched, and CGVO-X1 would require a separately preregistered native-domain
experiment. Neither is authorized here.

## Verification

- Focused CGVO service/API tests: `24/24` passed.
- Full backend regression: `285/285` passed.
- Frontend Oxlint and production build: passed; stable Windows thread-pool
  frontend suite: `178/178` passed.
- `cargo fmt --check`, `cargo check`, and Rust tests (`19/19`): passed.
- No packaging or founder candidate was created in G1.
