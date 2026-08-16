# PFR-V2B-R6-SBC-TN1 Founder Inspection Candidate

## Candidate

- Version: `0.10.49-pfr-v2b-r6-sbc-tn1`
- Status: `founder_inspection_candidate`; not a stable promotion or founder acceptance.
- Source commit: `1ce5c0aa5facd5c3aa1c3f5dd7e87e1d41fd79ce`
- Source working tree: clean (`source_git_dirty=false`).
- Candidate root: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.49-pfr-v2b-r6-sbc-tn1-tauri`
- Portable SHA-256: `A6FB5F65512F7DCBE33DA857206B8874912E53195FE2B3BD9A7E980593433336`
- Installer SHA-256: `62376E35521F86B52469227613008C07DECC3F8E1C23B1BD39FF0755223FEBBA`

## TN1 Scope

The candidate exposes `Trailokya 1972 Research` in Chakra. It uses the native
committed 81-cell Trailokya projection and the enumerated 28-row source target
map. Direct target identity and order never come from a generic grid walk.
Verses 48-52 semantic expansions are derived from one source event and remain
separate from direct targets.

The source profile is manual, read-only, and non-financial. It has no polarity,
score, price forecast, Fields input, Auto Suggest, ML, MT5 order, or execution
path. `executionAllowed=false` is preserved throughout the packaged smoke runs.

## Verification

- Native Trailokya adapter Python suite: 6 passed.
- Backend regression: 215 passed.
- Focused Chakra workspace test: 20 passed.
- Focused native Trailokya inspector test: 1 passed.
- Frontend suite: 38 files, 164 tests passed with the stable Windows threads pool.
- Oxlint and production Vite build passed. Vite reported an existing large-chunk
  warning only.
- `cargo fmt --check`, `cargo check`, and Rust tests passed; Rust tests: 19 passed.
- Portable smoke run 1: passed conditionally because the optional candlestick
  specialist is not configured; health, locks, forced sidecar recovery, layout
  survival, and clean shutdown passed.
- Portable smoke run 2: passed under the same optional-specialist condition;
  no descendant processes survived shutdown.

## Founder Inspection Checklist

1. Run `GannAstroDesk.exe` from the candidate folder, keeping `backend` beside it.
2. Open **Chakra**, select **Trailokya 1972 Research**, then inspect the native
   board: EAST at top, WEST at bottom, NORTH left, SOUTH right, with 81 cells.
3. In Manual Source Audit, select **Jyeshtha** and **LEFT**. Confirm direct targets
   remain ordered: YA, Sagittarius, Visarga, Pisces, CHA, Ashvini.
4. Select **FRONT** and confirm Pushya is the one direct target. Inspect derived
   targets separately; they must retain their shared causal source event.
5. Confirm any missing physical mapping is shown as explicit unknown/ambiguous
   projection state, never silently as `NOT_REACHED`.
6. Confirm no live ray, price implication, bullish/bearish state, score, Fields
   influence, Auto Suggest, or execution control appears.

No automated screenshot is treated as founder approval. Physical inspection of
this candidate remains the final TN1 acceptance check.
