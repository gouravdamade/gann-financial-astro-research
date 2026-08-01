# PFR-C2R Repository Reconciliation and Next Actions

## Status

`PFR_C2_STATUS = PARTIAL_REPOSITORY_INCONSISTENT`  
`FOUNDER_ACCEPTANCE_READY = false`  
`CANDIDATE_SOURCE_REPRODUCIBLE = false`

This is a reconciliation record, not a new product milestone. It supersedes
the acceptance claim for the `0.10.29-pfr-c2` artifact. The requested
Product-First C2R scope was limited to source, test, release, and lineage
integrity. No doctrine, scoring, model, Android, trading, or visualization
feature was added.

## Source Truth

- Branch: `product-first-sbc-phase-lab`
- Reconciliation source commit: `9f65649a03045cd100ab5629dda278aacbdff66e`
- Candidate source version: `0.10.30`
- The checked-in timing contract is `PROJECT_CONVENTION_TIMING_PHASE_V1` in
  both `gann-astro-desk/src/productFirstTimingPhase.ts` and
  `sbc/product_first_timing_phase.py`.
- V1 uses `activeEvents`, independent applying/exact/separating normalization,
  explicit exact handling, no `timingWindow`, and no aggregate result while
  `EVENT_CONTRIBUTION_LINK_PROFILE_MISSING` remains unresolved.
- Re, Im, resultant, gross, coherence, conflict, and execution output remain
  withheld. Execution remains `ABSTAIN` and locked.

The previously published C2 source snapshot was not V0 as the external
comparison alleged; the checked-in source already contained V1. The real
problem is artifact lineage and clean-checkout reproducibility.

## Retired Artifact

`D:\PycharmProjects\releases\GannAstroDesk-0.10.29-pfr-c2\release.manifest.json`
records source commit `81ccba3ae2966c3a772f7e0d718385a21b2d041b` with
`source_git_dirty = true`. Therefore `0.10.29-pfr-c2` is retired from founder
acceptance and must not be treated as a reproducible C2 release.

## Clean Verification Evidence

A detached clean worktree at commit `9f65649` was used for the current checks.

| Check | Result | Notes |
| --- | --- | --- |
| `pnpm install --frozen-lockfile` | Blocked | No tracked `pnpm-lock.yaml` exists. |
| `pnpm install --no-frozen-lockfile` | Pass | Used only as a documented fallback check. |
| `pnpm lint` | Pass | Clean worktree. |
| `pnpm build` | Pass | Clean worktree. |
| Full Vitest | Pass | 31 files, 123 tests. |
| Direct score-suppression DOM/SVG test | Pass | 2 tests; magnitude changes do not alter score-suppressed SVG/text. |
| `python -m pytest -q sbc` | Pass | 9 tests. |
| Full Python suite | Blocked | 612 passed; 3 transcription tests fail because an ignored JHora witness CSV is absent from the clone. |
| `cargo fmt --check` | Pass | Clean worktree. |
| `cargo check --offline` | Pass | Clean worktree. |
| `cargo test --offline` | Pass | 18 tests. |
| Native package smoke, twice | Not run | A clean-source package could not be built. |

The missing Python witness path is:
`status/evidence/jhora_kaala_witness_20260727/gann_reference_tokyo_tropical_positions_visible_20260729.csv`.
It is not tracked and is excluded by the repository CSV ignore rule. It was
not copied into the clean clone because that would make the result non-
reproducible.

## Package Reconciliation

The new packaging metadata correctly stamps global source cleanliness, exact
source SHA, `pfr_c2r_reconciliation_candidate`, a beta README, and SHA-256
checksums. It was not allowed to create a release artifact because the backend
sidecar build invokes `candlestick_agent/build_corpus_index.py`, which requires
the also-untracked and ignored file:
`candlestick_agent/source_registry.csv`.

The build therefore stopped before native compilation. No `0.10.30-pfr-c2r`
installer or portable package is being presented as a release candidate.

## Required Next Actions

1. Decide whether the JHora witness CSV is canonical release input. If it is,
   version it with integrity metadata; otherwise rewrite the affected tests so
   a clean clone can skip or supply a documented fixture.
2. Decide whether the candlestick source registry is canonical release input.
   If it is, version an appropriate registry or release fixture; otherwise
   make the sidecar build fail clearly before packaging or use a documented
   generated-input contract.
3. Add and maintain the package-manager lockfile required by the selected
   clean-install command, or formally change the documented install contract.
4. Re-run every gate from a new clean clone, then build and smoke-launch the
   exact `0.10.30-pfr-c2r` package twice before changing any status to
   `IMPLEMENTATION_RECONCILED`.
5. Confirm repository visibility and access settings directly in GitHub before
   any external review. This local reconciliation cannot change remote privacy.

Until all five actions are resolved and the gates pass, founder acceptance is
not ready.
