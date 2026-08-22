# CGVO-G3-R1 Varahamihira Visibility/Geography Source-Composition Adjudication

## Decision

CGVO-G3-R1 is a source-composition decision, not a new astronomy, geography,
market, or product feature. The current permitted live result remains
`SITE_VISIBILITY_AT_RESEARCH_ANCHOR` for the G2-R1A Taxila research anchor.

The central verdict is `CONTEXTUAL_PROVENANCE_ONLY`. Chapter XIV may identify
the Chapter-XIV/Gandhara context already recorded for Taxila, but it does not
turn a modern point-local visibility calculation into a Gandhara visibility
statement or a Chapter V source-effect activation.

Starting baseline: `1a7bc5b43167aef0cff568a268e1e8d9722e7b62`.

## Sources Inspected

| Source layer | Locator | Finding | Status |
| --- | --- | --- | --- |
| Held translation ledger | *Brihat Samhita* V.11 | Describes solar eclipse visibility differing by country according to the visible disc. | `COMMENTARY_SUPPORTED_INTERPRETATION` |
| Held translation ledger | *Brihat Samhita* V.42 | Refers provinces associated with lunar mansions to the Chapter XIV explanation. | `COMMENTARY_SUPPORTED_INTERPRETATION` |
| G1 raw Kurma seed | XIV.2-XIV.31 | Preserves nine directional nakshatra triads and raw historical-name occurrences. | `SOURCE_RECORDED` |
| S1B-R1 phase ledgers | solar and lunar phase mappings | Do not close a historical commencement/conclusion to modern contact-phase mapping. | `UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED` |

The working translation and online reading witnesses are useful reading aids,
but the repository does not hold an acquired checksum-identified root Sanskrit
page witness for the exact Chapter V/XIV semantic composition decision. This
is why neither translation wording nor the G1 raw-name ledger is promoted into
an operational composition rule.

## Composition Findings

1. Chapter V supplies a source-reading basis for recording local variation in
   eclipse visibility. G3-D1 already uses this only as a modern, topocentric
   observation at one evidence-bound site.
2. Chapter V's Chapter XIV reference supports displaying Kurmavibhaga as
   contextual provenance for eclipse-geography reading. It does not define a
   modern region boundary, a site-to-region equivalence, or an operator that
   transfers a site observation to every historical-name occurrence.
3. G2-R1A proves only one Taxila archaeological-site reference point. It
   explicitly does not prove the Taxila complex, a Gandhara centroid, or a
   Gandhara boundary.
4. Source-effect activation is separately blocked. The existing S1B-R1 solar
   and lunar phase mappings remain unresolved, and there is no source-closed
   rule that converts the local visibility audit to a Chapter V effect.

The read-only response therefore exposes `sourceCompositionAdjudication` with
`siteVisibilityInferenceStatus=SITE_ONLY`, `regionVisibility=null`, and
`sourceEffectActivation=null`. It is a status record, not a region or effect
calculator.

## Explicit Non-Inferences

The following all remain prohibited:

- Taxila visible -> Gandhara visible.
- Taxila visible -> Gandhara affected.
- Chapter V plus Chapter XIV -> automatic source-effect activation.
- Any polygon, buffer, intersection, distance, GIS, or historical footprint
  inference.
- Price/outcome reads, market direction, score, Fields, SBC, Auto Suggest,
  ML, MT5, or execution.

## Future Promotion Requirements

Any future region or source-effect work requires all relevant prerequisites,
not a convenient subset:

- checksum-identified root Sanskrit witnesses for the Chapter V and Chapter
  XIV passages used in the claimed composition;
- a source-closed semantic rule joining local visibility to a defined
  historical geographic unit;
- separately authorized historical region geometry;
- S1B source-closed solar and lunar phase activation mappings; and
- separate central authorization for a non-market source experiment.

No future work may use the current Taxila point to skip those requirements.

## Verification and Stop State

Focused CGVO service/API coverage verifies the static policy, G2-R1A
revalidation, typed rejection of regional and Chapter V effect requests, and
the null region/effect fields. The full backend suite must remain green.

No frontend, Rust, UI, installer, portable candidate, map, GIS, or product
surface was changed in this milestone. `executionAllowed=false` remains the
safety invariant.
