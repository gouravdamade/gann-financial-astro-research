# MO-R4A-S1R1-R1 Bṛhat Jātaka II.13 Locator Correction

## Status

MO-R4A-S1R1 received a conditional central pass. The implementation and
source-layer architecture were accepted, but central review found that the
S1R1 Bṛhat Jātaka II.13 locator mixed the printed page number from one witness
page with the PDF image number of the preceding page. This record is the
bounded S1R1-R1 correction and is ready for independent central review before
MO-R4A-S2.

The historical S1 ledger, S1R1 ledger, S1R1 overlay, audit, coverage, and
comparison remain preserved as historical records. R1 is an explicit successor,
not a rewrite of either earlier milestone.

## Held Witness Verification

The exact locally held witness was inspected as page images after verifying:

- Witness: `BRIHAT_JATAKA_BHATTOPALA_SANSKRIT_TIKA_HELD_WITNESS`
- Identity: Brhat Jataka with Srimad Bhatotpala Sanskrit commentary, Sri
  Harikrishna Nibandh Bhavan, Banaras City; title-page date not normalized
- SHA-256:
  `D1D2DD8FA2F6DB2BE1D4DFEE559E6929945AEA57EB24BCF8A4951AD0153FBE4A`
- Source bytes: held privately and not tracked

| PDF/scan image | Printed page | Direct finding |
| --- | --- | --- |
| 43 | 31 | The beginning/root material of the II.13 dṛṣṭi passage is visible. |
| 44 | 32 | The associated passage continues into the facing printed page. |

The admitted dṛṣṭi proposition remains unchanged: ordinary 3/10 and 5/9,
4/8, and 7 fractions remain as before, as do the Saturn 3/10, Jupiter 5/9,
and Mars 4/8 special full aspects. The held images therefore support a page
locator correction, not a doctrine correction.

## Correction

### Prior S1R1 pairing

`Brihat Jataka II.13, printed p.32 / scan p.43`

This was inaccurate because PDF image 43 is printed p.31.

### Corrected R1 pairing

Both affected structured Bṛhat Jātaka locators now use:

```text
sourceFamily: BRIHAT_JATAKA
witnessId: BRIHAT_JATAKA_BHATTOPALA_SANSKRIT_TIKA_HELD_WITNESS
sourceLayer: BRIHAT_JATAKA_ROOT
chapter: II
verse: 13
printedPage: 31-32
scanPage: 43-44
provenanceStatus: SOURCE_CLOSED_EXACT_PAGE_IMAGE
```

The affected operators are:

- `SARAVALI_4_32_ORDINARY_DRSTI_V1`
- `CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1`

The source images support a reconstructible passage span, but do not provide
a sufficiently unambiguous line-level layer delimiter for assigning the
printed p.32 continuation to Bhatotpala commentary for these operators.
Accordingly, `rootCommentarySeparated=false` is intentional. The continuation
is not mislabelled as commentary and is not silently treated as a separate
root passage.

The special operator's prose locator was corrected in parallel to:

`Brhat Jataka II.13, printed pp.31-32 / scan pp.43-44; Saravali 4.32-33,
printed p.58 / scan p.62; Trailokya scan pp.98 and 100 / printed pp.82 and 84
/ vv.365-371`

The ordinary operator's existing Saravali prose locator was unchanged; only
its Bṛhat Jātaka structured cross-text locator was corrected.

## Deterministic Successor Artifacts

The correction packet is
`configs/research/machine_interpretation/source_operators/classical_source_operator_s1r1_r1_brihat_jataka_ii13_locator_correction_v1.json`.
The corrected materialized ledger is
`configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s1r1_r1_v1.json`.

Hash lineage:

| Artifact | Historical S1 | Pre-correction S1R1 | Corrected S1R1-R1 |
| --- | --- | --- | --- |
| Canonical ledger | `E8C73059A0F85DCB9A9ACC6945A964FAD6EB0D4A47C0CBBE9F72000B5F5E10C4` | `9704821AB7A3777ABA6DB7671246B989ACBE0403FF511EED7CC38303BDBE2867` | `00A63DFA1ED2154D9935D9502191D5574C5D1BF38E924ABD8BDA95FD9E6C1379` |
| 24-event coverage | `93ED109D2A5D5DCE68A4C9C89E51B92ABECCB8A819BA3D3679A8A24D1A431D29` | `7ADF16D5A762F0DD50602F7DE4233A5A9AD965B5C6C68681C33B36A096A2C4C4` | `359C905C6CF7792F6782E53552CEBCC9D43A63E93EC375E8314ABE795445A2AD` |

The S1R1-R1 coverage and invariance records are:

- `status/audits/mo_r4a_s1r1_r1_real_24_source_operator_coverage.json`
- `status/audits/mo_r4a_s1r1_r1_source_provenance_audit.json`
- `status/audits/mo_r4a_s1r1_r1_immutable_event_rebinding_comparison.json`
- `status/acceptance/mo_r4a_s1r1_r1_locator_correction.json`

## Invariance and Safety

The corrected report retains exactly 24 immutable events: 12 USD and 12 JPY,
all 24 `SINGLE_PASS_VERIFIED`. Event IDs, event hashes, side identities,
transit/natal/aspect identities, exact UTC values, astronomy snapshots, event
ordering, and evaluator semantics remain unchanged. Coverage remains 0 none,
2 partial, 22 substantial, and 0 complete for declared scope.

The comparison removes only source-family, source-locator, and typed
source-measurement locator fields from operator outputs before comparing
semantics. It proves that report changes are restricted to provenance or
hashes.

No price or outcome data, Founder Review state, SBC, catalogue, reviewed
evidence, market bridge, polarity, score, signed wave, magnitude, Auto Suggest,
ML, MT5, or execution path was read or changed. The market-hypothesis registry
remains empty and `executionAllowed=false`.

## Remaining Gaps and Gate

The directive-named 1934 Bṛhat Jātaka witness remains unavailable; the held
Bhatotpala witness is retained under its actual identity. The two Saravali
strength records without durable exact locators remain partial and
non-executable. Existing composition, precedence, context, timing,
market-bridge, and magnitude gaps remain open.

S1R1-R1 is a locator correction complete for central review. It does not begin
MO-R4A-S2. Independent central review remains the next gate.
