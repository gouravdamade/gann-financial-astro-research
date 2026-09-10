# MO-R4A-S1R1 Classical Source-Operator Provenance Hardening

## Scope

MO-R4A-S1R1 is a metadata-only successor to the historical MO-R4A-S1 source
operator ledger. It makes the 17 existing operator propositions reconstructible
from source-layer locators where held page images support them, while retaining
unresolved provenance as an explicit fail-closed state.

It does not add doctrine, change an evaluator rule, regenerate the frozen
April 2025 event universe, read market data or outcomes, create a market
hypothesis, or alter the accepted `0.10.64-pfr-v2b-mo-r3-r2-f1-r1` candidate.

The historical S1 ledger and its two historical hashes remain preserved. The
S1R1 successor ledger is the deterministic composition of the S1 ledger and
the immutable S1R1 provenance-hardening packet; its materialized audit copy is
`configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s1r1_v1.json`.

## Witness Findings

| Witness | Role in S1R1 | Result |
| --- | --- | --- |
| `TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN` | Controlling page-image witness for existing Trailokya contracts | SHA-256 `1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194` verified; prior printed/scan page locks retained. |
| `SARAVALI_RANJAN_SANTHANAM_1983_HELD_PARTIAL` | Held volume containing Sanskrit root plus Santhanam rendering | SHA-256 `3BFD4F7F717798F87B7EFD6FA5A3DE2E28E7E09FC2520F0F05AE12B2E1BF9A58` verified. Root locators: 4.30 p56/scan60, 4.31 p57/scan61, 4.32-33 and 4.35 p58/scan62. |
| `BRIHAT_JATAKA_BHATTOPALA_SANSKRIT_TIKA_HELD_WITNESS` | Separately identified held Sanskrit root/commentary witness | SHA-256 `D1D2DD8FA2F6DB2BE1D4DFEE559E6929945AEA57EB24BCF8A4951AD0153FBE4A` verified. II.13 is p32/scan43; II.18 and immediately following commentary plus II.19 are p38/scan50. |
| Directive-named 1934 Brihat Jataka witness | Requested identity | Not found in reasonable local source locations. S1R1 does not rename the separately identified Bhatotpala Sanskrit witness as that unavailable 1934 witness. |
| `MO_R4A_S1_CENTRAL_SOURCE_AUDIT` | Historical discovery/audit record only | Cannot satisfy an exact root or commentary locator requirement. |

The source hierarchy is explicit in every S1R1 locator:

- `BRIHAT_JATAKA_ROOT` is separate from `BHATTOPALA_COMMENTARY`.
- `SARAVALI_ROOT` is separate from `SANTHANAM_TRANSLATION` and any commentary.
- Santhanam English for Saravali 4.32 remains `TRANSLATION_EDITORIAL_MISMATCH`.
- Trailokya retains the established `TRAILOKYA_1972_ROOT_TEXT_AND_HINDI_COMMENTARY` source layer.

## Per-Operator Provenance Audit

The machine-readable version of this entire table is
`status/audits/mo_r4a_s1r1_source_provenance_audit.json`. Every row has
`evaluatorMathematicsChanged=false` and `eventOutputSemanticsChanged=false`.

| Operator | Previous locator / source status | New locator(s), source layer, witness | Source status after | Reason for change | Math / 24-event semantics |
| --- | --- | --- | --- | --- | --- |
| `TRAILOKYA_1972_NATURAL_PLANET_CLASS_V1` | 1972 pp13-14 / scan29-30 / 54-58; closed categorical | Same pages; `TRAILOKYA_1972_ROOT_TEXT_AND_HINDI_COMMENTARY`; original 1972 scan | Closed categorical | Structured existing page lock | No / No |
| `TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1` | 1972 p39 / scan55 / 168-171; closed executable | Same page; Trailokya root/commentary; original 1972 scan | Closed executable | Structured existing page lock | No / No |
| `BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1` | Generic central audit; closed executable | BJ root II.18 p38/scan50; Saravali root 4.30 p56/scan60 | Closed executable | Replaced generic cross-text claim with two root locators | No / No |
| `BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1` | Generic central audit; closed executable | Bhatotpala commentary after BJ II.18 p38/scan50; Saravali root 4.31 p57/scan61 | Closed executable | Makes commentary/root boundary visible | No / No |
| `SARAVALI_4_32_ORDINARY_DRSTI_V1` | Saravali 4.32 root; closed executable | Saravali root 4.32-33 p58/scan62; Santhanam translation same page marked mismatch; BJ root II.13 p32/scan43; Trailokya pp82,84 / scan98,100 | Closed executable | Binds each cross-text reading separately | No / No |
| `CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1` | Central audit plus Trailokya pages; closed executable | BJ root II.13 p32/scan43; Saravali root 4.32-33 p58/scan62; Trailokya pp82,84 / scan98,100 | Closed executable | Replaces aggregate audit locator with three witnesses | No / No |
| `TRAILOKYA_1972_DIGNITY_V1` | 1972 pp40-42 / scan56-58 / 172-179; closed categorical | Same pages; Trailokya root/commentary; original 1972 scan | Closed categorical | Structured existing page lock | No / No |
| `TRAILOKYA_1972_STHANA_BALA_V1` | 1972 p37 / scan53 / 161; closed executable | Same page; Trailokya root/commentary; original 1972 scan | Closed executable | Structured existing page lock | No / No |
| `TRAILOKYA_1972_STHANA_PHALA_V1` | 1972 p38 / scan54 / 162-165; closed executable | Same page; Trailokya root/commentary; original 1972 scan | Closed executable | Structured existing page lock | No / No |
| `TRAILOKYA_1972_V166_INDIVIDUAL_MODIFIER_V1` | 1972 p38 / scan54 / 166; closed executable | Same page; Trailokya root/commentary; original 1972 scan | Closed executable | Structured existing page lock | No / No |
| `TRAILOKYA_1972_STHULA_MOTION_CLASS_V1` | 1972 pp16-19 / scan32-36 / 65-77; closed categorical | Same pages; Trailokya root/commentary; original 1972 scan | Closed categorical | Structured existing page lock | No / No |
| `BJ_SARAVALI_DIK_BALA_CONDITION_V1` | Generic central audit; closed categorical | BJ root II.19 p38/scan50; Saravali root 4.35 p58/scan62 | Closed categorical | Replaced aggregate cardinal mapping with root locators | No / No |
| `SARAVALI_POSITIONAL_STRENGTH_COMPONENTS_V1` | Central inventory; partial | Historical audit only; exact page locator unbound | Partial | Makes absence of individual locator explicit | No / No |
| `SARAVALI_NAISARGIKA_STRENGTH_V1` | Central audit / literal rupa record; partial | Historical audit only; exact page locator unbound | Partial | Removes overstated cross-text precision | No / No |
| `TRAILOKYA_1972_GRAHA_LATTA_BOUNDARY_V1` | 1972 pp59-61 / scan75-77 / 261-275; partial | Same pages; Trailokya root/commentary; original 1972 scan | Partial | Structured existing lock; Latta remains unpromoted | No / No |
| `TRAILOKYA_1972_ARGHYA_VISWA_BOUNDARY_V1` | 1972 pp76-87 / scan92-103 / 345-378; partial | Same pages; Trailokya root/commentary; original 1972 scan | Partial | Structured existing lock; Arghya remains unpromoted | No / No |
| `TRAILOKYA_1972_CONTEXT_RESOLUTION_BOUNDARY_V1` | 1972 pp30-86 / scan46-102; selected verses; closed categorical | Same page span and verses; Trailokya root/commentary; original 1972 scan | Closed categorical | Structured existing page lock | No / No |

The audit includes 22 exact page-image locators and two explicit
`EXACT_SOURCE_LOCATOR_NOT_DURABLY_BOUND` records. The latter remain
non-executable and cannot gain false precision from a central-audit summary.

## Hash Rebinding and Immutable Events

| Artifact | Historical S1 | Provenance-hardened S1R1 | Why it changed |
| --- | --- | --- | --- |
| Canonical ledger | `E8C73059A0F85DCB9A9ACC6945A964FAD6EB0D4A47C0CBBE9F72000B5F5E10C4` | `9704821AB7A3777ABA6DB7671246B989ACBE0403FF511EED7CC38303BDBE2867` | Structured source locators, source-layer boundaries, and explicit unresolved provenance are ledger content. |
| 24-event coverage | `93ED109D2A5D5DCE68A4C9C89E51B92ABECCB8A819BA3D3679A8A24D1A431D29` | `7ADF16D5A762F0DD50602F7DE4233A5A9AD965B5C6C68681C33B36A096A2C4C4` | Event reports carry rebinding provenance and the successor ledger hash. |

`status/audits/mo_r4a_s1r1_immutable_event_rebinding_comparison.json`
compares every event field-for-field. It proves:

- exactly 24 events remain: 12 USD and 12 JPY;
- all 24 remain `SINGLE_PASS_VERIFIED`;
- event ID, hash, side, transit body, natal target, aspect, exact UTC,
  identity status, and input policy remain unchanged;
- all astronomy snapshots remain unchanged;
- all fields outside `operatorOutputs` remain unchanged;
- removing only `sourceFamily`, `sourceLocators`, and
  `sourceMeasurement.sourceLocator` from every operator output leaves
  operator semantics unchanged;
- changed report bytes are therefore provenance/hash effects only.

The rebound coverage remains 0 none, 2 partial, 22 substantial, and 0
complete for declared scope. All 24 retain
`NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT`, `UNKNOWN_ASTRO_STATE`, no
authorized market bridge, unknown currency direction, and
`MAGNITUDE_NOT_CONFIGURED`.

## Remaining Gaps That Block S2

1. The directive-named 1934 Brihat Jataka witness was not available locally.
   The separate held Bhatotpala Sanskrit witness is used under its own verified
   identity, never substituted by name.
2. `SARAVALI_POSITIONAL_STRENGTH_COMPONENTS_V1` has no durably bound exact
   page-level source packet for individual evaluator promotion.
3. `SARAVALI_NAISARGIKA_STRENGTH_V1` has no durably bound exact page locator;
   it remains partial and non-executable.
4. Existing S1 composition, precedence, context, timing, market-bridge, and
   magnitude gaps remain open. S1R1 does not resolve them.

These gaps must be reviewed before any S2 hypothesis freeze. They are not
filled by translation inference, generic Jyotisha material, or model memory.

## Safety and Non-Changes

- `MARKET_HYPOTHESIS_REGISTRY = EMPTY`.
- `REAL_POLARITY_COUNT = 0`.
- `MARKET_MAGNITUDE = NOT_CONFIGURED`.
- `OUTCOME_DATA_READ = false`.
- Founder Review store/decision read is false.
- Price, candle, return, PnL, outcome, SBC, catalogue, reviewed-evidence,
  Auto Suggest, ML, MT5, and execution data reads are false.
- No signed USD wave, signed JPY wave, pair resultant, score, or market
  hypothesis was created.
- `executionAllowed = false`.
- The Windows candidate and frontend are unchanged; no package was built.

## Verification

All validation used the current repository Python 3.14 environment with the
existing repository import paths:

| Check | Result |
| --- | --- |
| Focused source operator test | `python -m unittest -v gann-astro-desk/backend/test_classical_source_operators.py`: 39 passed |
| Targeted Ruff | `python -m ruff check gann-astro-desk/backend/classical_source_operators.py gann-astro-desk/backend/test_classical_source_operators.py`: passed |
| Python compilation | Both touched Python modules compiled successfully |
| JSON parse | Seven new/changed S1R1 JSON records, including the schema document, parsed successfully |
| Full backend | `python -m pytest gann-astro-desk/backend --tb=short`: 416 passed, 1 skipped |
| Canonical repository regression | `python -m pytest --tb=short`: 960 passed, 2 skipped |

No founder UI inspection is required because this milestone does not alter
product behavior. No Windows candidate was built.
