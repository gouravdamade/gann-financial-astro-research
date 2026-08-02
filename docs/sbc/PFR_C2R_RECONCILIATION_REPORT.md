# PFR-C2R Repository Reconciliation and Next Actions

## Status

`PFR_C2_STATUS = IMPLEMENTATION_RECONCILED`
`FOUNDER_ACCEPTANCE_READY = true`
`CANDIDATE_SOURCE_REPRODUCIBLE = true`

## PFR-U1 Founder Acceptance Freeze - 2026-08-02

`PFR_U1_STATUS = FOUNDER_ACCEPTANCE_PENDING`

The exact `0.10.31-pfr-c2f` candidate is frozen for founder physical
acceptance and subsequent no-tuning observation. Its four recorded artifact
hashes were rechecked on 2026-08-02 and match this report. No product code,
candidate artifact, score, research engine, source profile, inference path,
or execution path was changed for PFR-U1. The founder checklist is
`PFR_U1_FOUNDER_ACCEPTANCE.md`; the five-session observation template is
`PFR_U1_OBSERVATION_LOG_TEMPLATE.csv`.

The next status cannot be inferred from smoke tests. It is set only after the
founder records `ACCEPTED`, `ACCEPTED_WITH_DEFECTS`, or `REJECTED` against the
exact candidate. Until then, no usability sprint or research work may begin.

This is a reconciliation record, not a new product milestone. It supersedes
the acceptance claim for the `0.10.29-pfr-c2` artifact. The requested
Product-First C2R and C2F scope was limited to source, test, release, and
lineage integrity. No doctrine, scoring, model, Android, trading, or
visualization feature was added.

## C2F Resolution - 2026-08-01

The C2R release blockers are resolved in the reproducible founder candidate.
The historical C2R baseline below is retained as an audit record.

- Exact packaged source commit:
  `b8ae06fa775b152e4782157e44c9b8be47676c82`.
- Candidate version: `0.10.31-pfr-c2f`.
- Candidate folder:
  `D:\\PycharmProjects\\releases\\GannAstroDesk-0.10.31-pfr-c2f\\`.
- Candidate manifest declares `source_git_dirty = false`, Node `v24.15.0`,
  package manager `npm@11.12.1`, `UNLINKED_EVENT_GEOMETRY`, market direction
  `ABSTAIN`, and execution disabled.
- The canonical frontend install command is `npm ci`; the tracked
  `package-lock.json` is the lock contract. There is no pnpm lock contract.
- JHora parser tests now use byte-preserved, tracked minimal fixtures. The
  separately supplied local witness suite skips in a clean clone with the
  explicit reason `SKIPPED_WITH_REASON` unless `JHORA_WITNESS_CSV` is set.
- Private Jyotish and candlestick corpora are optional local packs. Their
  absence starts the core desktop product with the specialist visibly reported
  as not configured; it does not silently substitute data or enable execution.

### C2F Clean-Source Gates

All gates ran from a detached clean worktree at the packaged source commit.

| Check | Result | Notes |
| --- | --- | --- |
| `npm ci` | Pass | Fresh clean install using tracked lockfile. |
| `npm run lint` | Pass | Clean worktree. |
| `npm run build` | Pass | Production frontend build. |
| `npm test` | Pass | 31 files, 123 tests. |
| `python -m pytest -q sbc` | Pass | 9 tests. |
| `python -m pytest -q` | Pass | 616 passed, 1 external-witness test skipped with stated reason. |
| `cargo fmt --check` | Pass | Clean worktree. |
| `cargo check --offline` | Pass | Clean worktree. |
| `cargo test --offline` | Pass | 18 tests. |
| Windows portable smoke, launch 1 | Conditional pass | Optional candlestick pack visibly not configured; all product checks and locks passed. |
| Windows portable smoke, launch 2 | Conditional pass | Same expected optional-pack deferral; no failed checks or descendant survivors. |

### Packaged Artifact Integrity

- Portable `GannAstroDesk.exe` SHA-256:
  `5DEF199321271B95EBCA9E866D8A35E99E975BC3632EBC39A9F08C65CE618AD8`.
- Installer `Gann Astro Desk_0.10.31_x64-setup.exe` SHA-256:
  `340C5EA66F73F989C79B850B4B7A8AE73FB3D870408EDC2694FAC99ADF7DF5CA`.
- Backend `GannAstroBackend.exe` SHA-256:
  `BC2A62134784BECEFA2FEF5DB8CB327C490B4475FA6E256147D79A9478F3E55B`.
- Manifest SHA-256:
  `AAA8BF79D28CD8B65626C4AC60C9E9C74AC945072173C7B3A3EE371B213908FA`.
- Native smoke evidence:
  `D:\\GannFinancialAstro\\soak\\tauri_0.10.31_20260801_182710\\logs\\native_soak_report.json`
  and
  `D:\\GannFinancialAstro\\soak\\tauri_0.10.31_20260801_182824\\logs\\native_soak_report.json`.

Founder acceptance is now ready for a physical inspection of this exact
portable candidate. It has not been marked founder-accepted by this document.

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

## Remaining Founder Checkpoint

1. Open the portable candidate from the exact C2F folder and inspect the core
   workspace, pan and zoom the chart, switch the visible research panels, and
   confirm the persistent read-only and execution-locked state.
2. Verify the optional specialist is visibly not configured rather than
   silently producing a draft from absent private corpus data.
3. Confirm GitHub repository visibility and access settings directly in GitHub
   before any external sharing. This local reconciliation cannot change remote
   privacy.

No additional implementation is authorized by C2F after this checkpoint.
