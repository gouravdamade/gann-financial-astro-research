# CGVO-G3-S1 Root Sanskrit Witness and Composition Audit

## Scope and outcome

This source-only milestone begins at `751561a96f0edc0121ce42f74bf48df0571854c7`.
It acquires a checksum-identified Sanskrit-bearing witness and adjudicates the
semantic links that had previously been only translation-led. It does not add
a geographic operator, an eclipse-effect operator, spatial matching, market
logic, or execution.

The terminal result is **`SOURCE_CLOSED_CONTEXTUAL_PROVENANCE_ONLY`**. The
new witness strengthens the evidence record while leaving Taxila as one
evidence-bound research site, `regionVisibility=null`, and
`sourceEffectActivation=null`.

## Controlling witness

| Field | Verified value |
| --- | --- |
| Source witness | `BRIHAT_SAMHITA_SASTRI_V_SUBRAHMANYA_DLI_2015_102832` |
| Scan title / author metadata | *Varahamihiras Brihat Samhita,vol.i-ii* / `Tr.sastri,v.subrahmanya` |
| Archive identifier | `2015.102832` |
| Pages | 1,116 |
| SHA-256 | `D7425625010C621FF6651BF6BF916506791E3D4381078251AC7DC8EFBBA6577A` |
| Bytes in Git | No; durable private source only |
| OCR role | `NAVIGATION_ONLY` |

The full-file hash was recomputed before use. PDF images 72, 83--84, 184--185,
and 189--190 were rasterized and inspected. The printed English translation
on the same pages is useful comparison evidence, but it does not control the
Sanskrit transcription or semantic claim.

## Page-backed packets

### V.11: local differential solar visibility

PDF image 72, printed p.47, visibly reads:

`चन्द्रोऽधःस्थः स्तगयति रविमम्बुदवत् समागतः पश्चात् । प्रतिदेशमतश्चित्रं दृष्टिवशाद्भास्करग्रहणम् ॥११॥`

IAST: `candro 'dhaḥsthaḥ sthagayati ravim ambudavat samāgataḥ paścāt |
pratideśam ataś citraṃ dṛṣṭivaśād bhāskaragrahaṇam || 11 ||`.

The operative terms are `प्रतिदेशम्` (by/for each locality or country),
`दृष्टिवशात्` (according to visibility/appearance), and
`भास्करग्रहणम्` (solar eclipse). This closes a source-backed **solar**
local-differential-visibility statement. It supplies neither a boundary for a
historical region nor a rule that transfers one site's observation to another
place.

### V.42: Chapter XIV reference distinction

PDF images 83--84, printed pp.58--59, were inspected as a unit. V.42's root
Sanskrit gives Kumbha/Meena eclipse-result language. The visibly printed
`(Ch. XIV, infra)` is part of the English translation/editorial continuation;
no Kurma/Chapter-XIV reference appears in the inspected root Sanskrit of V.42.

Accordingly, the Chapter-XIV reference remains
`COMMENTARY_ONLY_REFERENCE`, rather than a root-text composition instruction.
That distinction prevents a translation parenthesis from becoming a runtime
operator.

### XIV.1: directional-nakshatra organization

PDF images 184--185, printed pp.159--160, show the Chapter XIV heading and
the root opening. The operative root terms are `नक्षत्रत्रय` (nakshatra
triads), `भारतवर्ष` (Bharatavarsha), and `दिशः` (directions). The surrounding
“globe/tortoise” discussion is commentary and is not used as source geometry.

This closes a contextual directional/nakshatra source mapping only. It does
not create a modern polygon, centroid, or historical-region representation.

### XIV.24--28: Taxila, Puskalavati and Gandhara

PDF images 189--190, printed pp.164--165, place the target names within the
**northern** list associated in the existing source seed with Shatabhisha,
Purva Bhadrapada, and Uttara Bhadrapada. The page-image verified forms are
`तक्षशिला` / Takṣaśilā, `पुष्कलावत` / Puṣkalāvata, and `गान्धार` / Gāndhāra.

They are peers in a historical-name list. The inspected verses do not say that
Taxila contains, equals, represents, or transfers visibility to Gandhara.
Co-listing therefore supports source provenance only.

## Semantic decision

| Relation | Status | Reason |
| --- | --- | --- |
| V.11 local differential visibility | `SOURCE_CLOSED_SOLAR_LOCAL_DIFFERENTIAL_VISIBILITY` | Root Sanskrit speaks of solar-disc appearance varying `प्रतिदेशम्` by visibility. |
| V.42 to XIV reference | `COMMENTARY_ONLY_REFERENCE` | The Chapter XIV label is editorial/translation prose, not the inspected root verse. |
| XIV geography | `SOURCE_CLOSED_CONTEXTUAL_MAPPING` | Root text supplies directional/triad and historical-name list context. |
| Taxila site to Gandhara | `SOURCE_SILENT_SITE_TO_REGION_OPERATOR` | No containment, equivalence, or transfer rule appears. |
| Site visibility to region visibility | `NOT_AUTHORIZED` | A transfer rule and authorized region representation are both absent. |
| Local visibility to Chapter V effect | `NOT_AUTHORIZED` | V.11 is observational; S1B phase/effect mapping is still independently unresolved. |

The channels remain separate: modern local observation, Chapter XIV source
geography, Taxila research-site identity, and any Chapter V effect condition.
They are not fused merely because they appear in the same book.

## Runtime and safety

The existing Taxila endpoint remains a site-only modern-astronomy audit. It
now exposes only static root-witness/adjudication metadata. It still rejects
`includeGandharaRegion` and `includeChapterVEffect`, and it still returns
`regionVisibility=null` and `sourceEffectActivation=null`.

No UI or package was built. No price, outcome, Fields, SBC, Auto Suggest, ML,
MT5, or execution path was read or changed. `executionAllowed=false`.
