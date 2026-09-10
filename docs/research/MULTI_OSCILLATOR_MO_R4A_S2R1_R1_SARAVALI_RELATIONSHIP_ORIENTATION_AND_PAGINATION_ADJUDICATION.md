# MO-R4A-S2R1-R1 Saravali Relationship Orientation And Pagination Adjudication

## Scope And Result

Independent central review raised two questions about the Saravali lineage: whether the relationship direction for `MERCURY -> MARS` had been reversed, and whether printed-page values had been confused with PDF image numbers. This successor is the direct page-image adjudication of those questions. It takes Branch B: the held Sanskrit root confirms the existing directed Saravali matrix, including `MERCURY -> MARS = ENEMY`; only the Sanskrit-root pagination for verses 4.32-33 changes.

This is a source and outcome-blind freeze record. It neither reads nor evaluates price, outcomes, candles, Founder Review, catalogue/evidence admissions, SBC, signed waves, pair resultants, Auto Suggest, ML, MT5, or execution.

## Controlling Witness

| Field | Value |
| --- | --- |
| Witness | `SARAVALI_RANJAN_SANTHANAM_1983_HELD_PARTIAL` |
| Book | *Saravali of Kalyana Varma*, Volume I, R. Santhanam, Ranjan Publications, First Edition 1983 |
| Held artifact SHA-256 | `3BFD4F7F717798F87B7EFD6FA5A3DE2E28E7E09FC2520F0F05AE12B2E1BF9A58` |
| Verification | Full-file SHA-256, then two direct page-image inspection passes |
| Source-byte policy | Private PDF bytes, page renders, OCR, and screenshots are not tracked in Git |
| Citation authority | `SARAVALI_ROOT` for source doctrine; translation is a separate lexical cross-check only |

The root, English translation, and any commentary are distinct evidence layers. Translation was not used as a grammatical substitute and commentary was not used to decide relationship orientation.

## Physical Pagination Audit

The following values are read from the printed numbers visibly present in the held page images. `printedPage` and `pdfImage` are intentionally separate fields.

| Verse / material | PDF image | Visible printed page | Physical placement | Evidence layer |
| --- | ---: | ---: | --- | --- |
| 4.28-29 | 60 | 56 | root | `SARAVALI_ROOT` |
| 4.30 | 60 | 56 | root begins | `SARAVALI_ROOT` |
| 4.30 | 61 | 57 | root concludes | `SARAVALI_ROOT` |
| 4.31 | 61 | 57 | root | `SARAVALI_ROOT` |
| 4.32-33 | 61 | 57 | Sanskrit root | `SARAVALI_ROOT` |
| 4.32-33 | 62 | 58 | English rendering | `SANTHANAM_TRANSLATION` |
| 4.34-35 | 62 | 58 | root | `SARAVALI_ROOT` |

The old p.58/PDF-62 root bindings are retained in the historical S2R1 record. The new successor corrects only these root locators:

| Operator | Verse | Historical root locator | Adjudicated root locator |
| --- | --- | --- | --- |
| `SARAVALI_4_32_ORDINARY_DRSTI_V1` | 4.32-33 | p.58 / image 62 | p.57 / image 61 |
| `CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1` | 4.32-33 | p.58 / image 62 | p.57 / image 61 |

The separate 4.32-33 Santhanam translation remains p.58 / PDF image 62 and remains labelled `TRANSLATION_EDITORIAL_MISMATCH` rather than root doctrine.

## Relationship Orientation

The operative relation is `SOURCE_BODY -> TARGET_BODY`: the body grammatically holding the relationship predicate is the source, and each name in its friend/enemy group is the target. The root's possessive/predicate construction is read directly, not symmetrized and not recovered from Trailokya.

Minimal root terms inspected include `mitrani` (friends), `amitrah` (enemies), and the verse-29 rule that the bodies not named in either group are neutral. The first two terms appear in the direct lists; the last rule is explicit in the root and is therefore machine-executable only as `NEUTRAL_BY_SOURCE_RULE`.

| Directed cell | Result | Root evidence and orientation |
| --- | --- | --- |
| `MARS -> MERCURY` | `ENEMY` | Mars is the relationship holder; Mercury is named in Mars's enemy list. |
| `MERCURY -> MARS` | `ENEMY` | Mercury is the relationship holder; Mars is independently named in Mercury's enemy list. |
| `MERCURY -> MOON` | `ENEMY` | Mercury is the relationship holder; Moon is independently named in Mercury's enemy list. |
| `MOON -> MERCURY` | `FRIEND` | Moon is the relationship holder; Mercury is independently named in Moon's friend list. |

No relation was copied from its reciprocal cell. Self relationships remain `UNKNOWN` and Rahu/Ketu remain unsupported by this bounded passage.

## Reconstructed Seven-Planet Matrix

Each row is source body; lists are target bodies. Every non-self pair has one state, derived either from an explicit root list or the explicit verse-29 neutrality rule.

| Source | Friends | Neutral | Enemies |
| --- | --- | --- | --- |
| SUN | MOON, MARS, JUPITER | MERCURY | VENUS, SATURN |
| MOON | SUN, MERCURY | MARS, JUPITER, VENUS, SATURN | none |
| MARS | SUN, MOON, JUPITER | VENUS, SATURN | MERCURY |
| MERCURY | SUN, VENUS | JUPITER, SATURN | MARS, MOON |
| JUPITER | SUN, MOON, MARS | SATURN | MERCURY, VENUS |
| VENUS | MERCURY, SATURN | MARS, JUPITER | SUN, MOON |
| SATURN | MERCURY, VENUS | JUPITER | SUN, MOON, MARS |

The machine-readable adjudication fixture records 42 one-way evidence records, including the grammatical orientation explanation and derivation type for each. It has 49 complete current-S2R1 versus adjudicated cells: 49 unchanged, 0 changed, and 7 self cells. No friend/neutral or enemy/neutral transitions occurred.

## Cross-Text Comparison

Saravali and Trailokya remain separate source profiles. The derived 49-cell comparison reports 41 agreements, one conflict, seven self-pair `NOT_COMPARABLE` rows, and zero unresolved rows. The conflict remains `MERCURY -> MARS`: Trailokya is `NEUTRAL`; Saravali is `ENEMY`. This is a source disagreement, not a reason to merge or vote between profiles.

## Affected Source Records

| Operator | Root locator after adjudication | Change |
| --- | --- | --- |
| `SARAVALI_NATURAL_RELATIONSHIP_V1` | 4.28-29, p.56 / image 60 | relationship orientation affirmance |
| `BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1` | 4.30, pp.56-57 / images 60-61 | audited, unchanged |
| `BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1` | 4.31, p.57 / image 61 | audited, unchanged |
| `SARAVALI_4_32_ORDINARY_DRSTI_V1` | 4.32-33, p.57 / image 61 | root locator corrected |
| `CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1` | 4.32-33, p.57 / image 61 | root locator corrected |
| `BJ_SARAVALI_DIK_BALA_CONDITION_V1` | 4.35, p.58 / image 62 | audited, unchanged |

`sourceDoctrineChanged=false` and `evaluatorMathematicsChanged=false`.

## Successor Freeze

The provenance correction requires a new successor lineage even though the relationship states and pilot outputs are unchanged.

| Artifact | Canonical SHA-256 |
| --- | --- |
| S2R1 historical ledger | `E9DB0C92B449045FB2ED35D482E3F7063C547CD2562305EEF778064C2F5558E6` |
| S2R1 historical coverage | `B22F42E78D20858045AE98F0010355E1E8895C60F1DD49570230ECC5B2C7F62A` |
| S2R1-R1 ledger | `2D4AD6E151602FBF2FC3E0ADDFDCDE7C7211CC52ED44D801AD3925AD9D5F3366` |
| S2R1-R1 coverage | `A4437C2A116EBD5D465339BCB0C9D81F8149CE65FAF37CF81C0F29D75B44F8B0` |
| S2R1-R1 registry | `D76E208F52511BD8B5380BB32049B0C47275261443E587E3E09184E439FF3110` |
| S2R1-R1 USD hypothesis | `1C816B735FCCA52B84ED26C03D1755D251EADA7C2606B1D56533A06D71B713F9` |
| S2R1-R1 JPY hypothesis | `EF2D18CEA75BCC1A137D8687F332B5586FB62D8803D44819204AFDD6472ED24F` |
| S2R1-R1 prediction freeze | `83F1456271B510468A0DF28C66AD705318CD06F5D5B5E0566F6DE05FA06CF71D` |
| S2R1-R1 invariance audit | `9275312E183B631ED28F568509883328ACBEC4D6775B8AF3066E0DF515FA3BE3` |
| S2R1-R1 lineage reconciliation | `E76A90B6187F83F053AB676EB0BF5FEE5411DAA3AEBF1D64B654FEFE1613557C` |
| S2R1-R1 acceptance manifest | `DFE2837578DB17AE6E286EA7585A2E17E3B39DBF78D63984A48EFBFD72EDA4C6` |

The complete generated event comparison proves 24 events (12 USD, 12 JPY), all `SINGLE_PASS_VERIFIED`, with unchanged identity fields, astronomy snapshots, source natural states, compound states, bridge applicability, and predictions. Counts remain 17 bridge-applicable, 14 directional (9 `SUPPORTIVE`, 5 `ADVERSE`), 3 categorical `NEUTRAL`, and 7 abstentions. Every row retains `signedUnit=null`, `magnitudeConfigured=false`, `NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT`, and `UNKNOWN_ASTRO_STATE`.

## Verification And Gate

Focused source-operator, S2, S2R1, and S2R1-R1 bridge tests: `67 passed`. JSON parsing covered nine new successor artifacts; the strict two-hypothesis registry schema contract passed. Python compilation and Ruff passed for all changed Python modules. Full backend regression: `444 passed, 1 skipped, 66 subtests`. Canonical repository regression: `988 passed, 2 skipped, 66 subtests`. Both skips are pre-existing optional private/external witness checks and are unrelated to this successor.

`S2R1_R1_SOURCE_ADJUDICATED_AND_BLINDED_FREEZE_COMPLETE_CENTRAL_REVIEW_REQUIRED` is the current state. S3 remains blocked at `INDEPENDENT_CENTRAL_REVIEW_BEFORE_MO_R4A_S3`; no S3 design, outcome inspection, or Astra work was begun.
