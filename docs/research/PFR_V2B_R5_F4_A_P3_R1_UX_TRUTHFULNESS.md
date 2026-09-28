# PFR-V2B-R5-F4-A-P3-R1 UX Truthfulness

## Scope

PFR-V2B-R5-F4-A-P3-R1 is a narrow correction to the P3 founder UX. It starts
from the P3 documentation commit `c8a4f84a7c0c909688aedeae770f236dc651226c`
and preserves the P3 architecture and implementation commit
`be3e4fcd6061b2e92022c7ef7b2f3b304f0dee1a`. The isolated implementation commit
for this correction is `1ad35e0` on
`research/pfr-v2b-r5-f4-a-p3-r1-ux-truthfulness`.

The correction is presentation and eligibility gating only. It does not change
unsigned activity mathematics, event compilation, polarity admission, source
evidence, pair math, backend contracts, or execution behavior.

## Symbol Gate

The `Add USD/JPY Activity to Chart` action remains visible in Fields, but it is
actionable only when the active chart symbol is exactly `USDJPY`. For an
unsupported symbol it is disabled and explains:

`Chart-native USD/JPY activity is available only for USDJPY.`

The parent-owned callback applies the same symbol check before any layout
mutation or navigation. Unsupported-symbol clicks therefore cannot activate the
activity pane, change chart layout state, or navigate to Chart. The existing
dirty Founder Review guard takes precedence over the unsupported-symbol message
and continues to block navigation before mutation.

## Zero-Coverage Wording

Known-count zero is no longer treated as proof that the polarity catalogue is
empty. Without an authoritative loaded pilot status, the side summary uses the
generic wording:

`NO RESOLVED CATEGORICAL POLARITY IN THIS RANGE`

The stronger `NO ADMITTED POLARITY ENTRIES` wording is shown only when the
existing authoritative pilot response explicitly reports
`catalogueEntryCount === 0` for that side. No extra request and no brittle
reason-string inference are used. Pair-relative zero coverage retains the
explicit modern-transform label and states that side evidence is unresolved.

Known-data detail, research-details expansion, withheld directional-policy
compaction, and unsigned activity presentation remain unchanged.

## Verification

- Focused frontend: **44/44 passed** across the Fields workspace, indicator
  toolbar, and eligibility helper tests.
- Full frontend: **244/244 passed** across **49 files**.
- TypeScript build/typecheck: passed.
- Oxlint: passed.
- Vite production build: passed; only the existing large-chunk advisory remains.
- `git diff --check`: passed before source and documentation commits.
- Local browser smoke: USDJPY Fields showed an enabled CTA; activation opened
  the existing Chart surface with `USD / JPY EVENT ACTIVITY UNSIGNED RAW ACTIVE
  EVENT COUNT`. The live zero-coverage summary showed the authoritative pilot
  state and the strong wording only in that state; the compact pair wording was
  visible. Unsupported-symbol and parent-guard behavior are covered by the
  focused tests because the local symbol selector did not expose a separate
  unsupported-symbol option in this smoke fixture.
- Native Windows packaging: not executed. This is a source/frontend correction
  and does not change package metadata.

## Historical Status

The P3 status record is preserved and marked
`SUPERSEDED_BY_P3_R1_PENDING_CENTRAL_REVIEW`; its original implementation and
verification claims remain intact. R1 adds only the truthful eligibility and
zero-coverage boundary correction.

## Locks and Non-Goals

`backendChanged=false`, `rustChanged=false`, `packageMetadataChanged=false`,
`activityMathChanged=false`, `pairMathChanged=false`,
`polarityCatalogueChanged=false`, and `evidenceRegistryChanged=false`.

F4-B, F4-C, Candidate C, EMP3, provider access, outcome analysis, MT5
execution, Auto Suggest, ML, scoring, price forecasting, polarity assignment,
and order placement remain outside scope. `executionAllowed=false`.

Next gate:
`CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P3_R1_UX_TRUTHFULNESS`.
