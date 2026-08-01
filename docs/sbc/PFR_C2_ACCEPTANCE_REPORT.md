# PFR-C2 Founder Acceptance and Visualization Integrity

## Status

Superseded by the C2R reconciliation record. Do not use this report or the
`0.10.29-pfr-c2` artifact for founder acceptance. See
`docs/sbc/PFR_C2R_RECONCILIATION_REPORT.md`.

The prior implementation claim remains historical context only; C2R found
that the packaged artifact was built from a dirty, older source commit and
that the current repository cannot yet reproduce a package from a clean clone.

- Branch: `product-first-sbc-phase-lab`
- Starting reconciliation commit: `81ccba3`
- Candidate version: `0.10.29`
- Scope: founder-visible visualization integrity only. No new doctrine, certification, authority, governance, ML, trading, MT5, Android, or Auto Suggest system was introduced.

## C2-0 Baseline Truth

- `SOURCE_ONLY_BASELINE` displays **Source-profiled partial baseline**.
- Its evidence status is `SOURCE_PROFILED_PARTIAL` and its approval state is `FOUNDER_APPROVAL_PENDING` until `SBC_BASELINE_PROFILE_APPROVAL` is resolved.
- The machine mode ID remains `SOURCE_ONLY_BASELINE`; visible values do not claim classical completeness.
- Approval and source-gap state are carried through the mode selector, header, profile status, Why drawer, linked audit header, bookmarks, footer, and exported visualization manifest.

## C2-1 Score-Suppression Boundary

- One mode-aware formatter gates scalar units, percentages, coverage, conflict labels, pair totals, fixed-wheel detail, comparison cards, and Why-drawer values.
- Score-suppressed modes display identity and declared fixed 0/pi placement only. Their vector lengths, gross ring, resultant ray, and near-zero marker no longer encode scalar magnitude.
- Audit values and audit-package generation remain unavailable in score-suppressed modes.

## C2-2 Timing Lifecycle and Quarantine

- The timing contract is now `PROJECT_CONVENTION_TIMING_PHASE_V1`.
- Applying and separating spans use independent denominators around exact; `symmetricTimingDeclared` is explicitly `false`.
- Exact is explicit within 30 seconds. Invalid zero-length applying or separating spans fail closed as `UNKNOWN_INVALID_EVENT_WINDOW`.
- Per-event lifecycle geometry remains inspectable when enabled.
- `EVENT_CONTRIBUTION_LINK_PROFILE_MISSING` prevents any Cartesian contribution-by-event aggregate. The UI and export withhold Re, Im, resultant, gross, coherence, conflict, and collective phase until a declared causal link profile exists.
- Timing remains opt-in, non-directional, non-financially validated, and permanently execution-locked.

## C2-3 Time Selection

- Previous/next loaded-candle controls are always available in the SBC header.
- The price-chart SVG has one keyboard focus point: Left and Right Arrow synchronize the selected timestamp by one loaded candle.
- Candle clicks retain the same synchronized timestamp path.

## Regression Evidence

- `pnpm lint`: pass.
- `pnpm build`: pass.
- Targeted Vitest, fork pool, one worker: 10 pass.
- `python -m pytest -q sbc`: 9 pass.
- `cargo check --offline`: pass.
- Native Rust unit-test discovery: 18 tests discovered; a representative native unit test passed. The full native run exceeded the shell time allowance after compilation, so it is not recorded as a full pass.
- Native smoke: pass, with the expected closed-market MT5 normalization check deferred. The release remains read-only and execution-locked throughout the smoke run.

## Candidate Artifact

- Folder: `D:\PycharmProjects\releases\GannAstroDesk-0.10.29-pfr-c2\`
- Installer: `Gann Astro Desk_0.10.29_x64-setup.exe`
  - SHA-256: `86ED85F7B28244345D08956ADB86F159F2D1F55FB3A7904E0E4217F1B516FD1C`
- Portable: `GannAstroDesk.exe`
  - SHA-256: `00FC365FA81D017379194BD516F74B79DF3AE2F740532FFAA2B2B7AA9F1CCD1F`

## Founder Acceptance Checklist

1. Baseline visibly says **Source-profiled partial baseline** and **Founder approval pending**.
2. Calibrated and visual-only modes expose no score magnitude through text, title, tooltip, SVG length, comparison, audit, bookmark, or export.
3. Phase Lab shows individual applying/exact/separating lifecycle positions but no aggregate interference values.
4. Left/Right keyboard selection and header arrow controls both move one candle and remain synchronized with chart, Chakra, and audit time.
5. Native package starts and retains the execution lock.

No physical founder acceptance was performed by this implementation pass.
