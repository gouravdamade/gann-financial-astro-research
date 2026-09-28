# PFR-V2B-R5-F4-A-P3-R2 Zero-Coverage Header Truthfulness

## Scope

PFR-V2B-R5-F4-A-P3-R2 is a surgical frontend wording correction on top of
the reviewed P3-R1 state. It starts from
`a10901fd7e7ef2dab1b38d45fef8140f839fb5db` and keeps the R1 implementation
commit `1ad35e02d3e9654a77f5bc869dd06e15ef5f7ed0` unchanged. The R2 source
implementation commit is
`e9b97ceb5129943809ea7af4ae207642df0bb6b8` on
`research/pfr-v2b-r5-f4-a-p3-r2-zero-coverage-header`.

The R1 behavior was accepted except for one compact explanatory string. The
old header said:

`UNKNOWN until an admissible polarity entry exists`

That wording attributed every zero-coverage interval to catalogue admission,
even though the compiler can also report that no side-chart aspect is active.
It also implied that adding an entry would resolve every interval. The R2
header is now the neutral range-level statement:

`NO RESOLVED CATEGORICAL POLARITY IN THIS RANGE`

This does not mean neutral polarity, and it does not identify a catalogue
cause that the range data does not establish.

## Preserved R1 Semantics

The existing side-level helper is unchanged. Without an authoritative loaded
pilot status, side rows use the generic wording above. When the authoritative
pilot status explicitly reports `catalogueEntryCount === 0`, the side rows may
still say:

`NO ADMITTED POLARITY ENTRIES`

That stronger wording remains limited to the authoritative side-level case.
The compact header remains neutral even in that case. Pair-relative wording
also remains unchanged:

`MODERN ENGINEERING RESEARCH TRANSFORM`

`NO RESOLVED PAIR INTERVALS BECAUSE SIDE EVIDENCE IS UNRESOLVED`

No CTA, symbol gate, parent guard, Founder Review guard, indicator toolbar,
withheld-mode presentation, activity data, or research-detail behavior changed.

## Verification

- Focused Fields suite: **41/41 passed**.
- Full frontend suite: **244/244 passed** across **49 files**.
- TypeScript build/typecheck: passed through `npm run build`.
- Oxlint: passed.
- Vite production build: passed; the existing large-chunk advisory remains.
- `git diff --check`: passed.
- Backend, Rust/Tauri, and Windows packaging: not executed; this source-only
  correction does not change those surfaces.

The strengthened no-active-aspect test verifies that the compact summary
contains the neutral range wording, does not contain the old
`until an admissible polarity entry exists` phrase, and does not use the
authoritative catalogue wording when pilot status is unavailable. The
authoritative zero-catalogue test verifies that side rows retain the stronger
wording while the compact header remains neutral.

## Locks and Non-Goals

`backendChanged=false`, `rustChanged=false`, `packageMetadataChanged=false`,
`activityMathChanged=false`, `pairMathChanged=false`,
`polarityCatalogueChanged=false`, and `evidenceRegistryChanged=false`.

F4-B, F4-C, Candidate C, EMP3, provider access, outcome analysis, MT5
execution, Auto Suggest, ML, scoring, price forecasting, polarity assignment,
and order placement remain outside scope. `executionAllowed=false`.

Candidate C is unchanged, EMP3 remains unauthorized, `providerAccess=false`,
`outcomeAnalysis=false`, and `MT5 order invocation=false`.

Next gate:
`CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P3_R2_ZERO_COVERAGE_HEADER`.
