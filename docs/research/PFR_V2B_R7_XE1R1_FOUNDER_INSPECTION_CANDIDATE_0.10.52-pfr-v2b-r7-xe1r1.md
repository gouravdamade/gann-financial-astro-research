# PFR-V2B-R7-XE1R1 Founder Inspection Candidate

## Release

- Milestone: `PFR-V2B-R7-XE1R1`
- Candidate version: `0.10.52-pfr-v2b-r7-xe1r1`
- Status: founder-inspection candidate; founder acceptance pending
- Source commit: `8bf9fc20a80caf48e5bf50d70a351e8ab0901629`
- Source git dirty state at packaging: `false`
- Candidate root: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.52-pfr-v2b-r7-xe1r1-tauri`
- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.52-pfr-v2b-r7-xe1r1-tauri\GannAstroDesk.exe`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.52-pfr-v2b-r7-xe1r1-tauri\Gann Astro Desk_0.10.52-pfr-v2b-r7-xe1r1_x64-setup.exe`

### Artifact hashes

- Portable SHA-256: `AFA1FDDA171DE02FD3342274AC8682AAC722E5BE05ED8522352F6FA49E7ED116`
- Installer SHA-256: `F84676FAAA5C3C40C973EBD0EB169EFA5CFB4E307A932E4CD0F62F8B9814DE16`
- Manifest: `release.manifest.json`
- Checksums: `SHA256SUMS.txt`

The release manifest records the same source commit, `source_git_dirty=false`,
the dependency versions, the execution locks, and `experimental_evidence_contract=
XE1_EXPERIMENTAL_EVIDENCE_LAB_V1`.

## Bounded XE1R1 Corrections

1. The Experiments safety banner is sticky within the Experiments workspace so
   the warning remains visible while that workspace scrolls. The CSS selector
   is isolated to the experimental banner and does not change Chart, Fields,
   Chakra, BPHS or source-profile surfaces.
2. Empty Touched and Manual datasets now expose no directional raw value
   (`null`). The UI renders `Unknown` rather than implying zero evidence or a
   neutral numeric result.
3. Market-like display wording was replaced with descriptive evidence wording:
   `POSITIVE EVIDENCE`, `NEGATIVE EVIDENCE`, `MIXED EVIDENCE`, and
   `UNKNOWN / BALANCED`. Backend state enums and XE1 aggregation math were not
   changed.
4. The raw dataset badge is contextual: populated synthetic data shows
   `Raw fixture sealed`; empty data shows `No observations admitted`.
   `MARKET INPUT: NONE` is visible in the context strip.

No price, SBC, Fields, Auto Suggest, ML, MT5, execution, source promotion,
modifier formula, causal grouping, or raw-evidence contract was changed.

## Verification

### Focused and full tests

- Focused backend: `python -m unittest discover -s backend -p "test_experimental_evidence_service.py"` -> `13 passed`.
- Full backend: `python -m unittest discover -s backend -p "test_*.py"` -> `228 passed`.
- Focused frontend: `npx vitest run src/experimentalLabWorkspace.test.tsx --pool=threads --maxWorkers=1 --no-file-parallelism --testTimeout=15000` -> `1 file, 3 tests passed`.
- Full frontend: `npx vitest run --pool=threads --maxWorkers=1 --no-file-parallelism --testTimeout=15000` -> `39 files, 167 tests passed`.
- Broad repository regression: `python -m pytest -q` -> `772 passed, 1 skipped, 16 subtests passed`. The one skip is the optional external JHora witness because `JHORA_WITNESS_CSV` was not configured.
- Dependency installation: `npm ci` passed. npm reported existing audit findings; no unrelated automatic dependency repair was applied.
- Lint: `npm run lint` passed.
- Production build: `npm run build` passed. The existing large-chunk warning remains informational.
- Rust formatting: `cargo fmt --check` passed.
- Rust compilation: `cargo check` passed.
- Rust tests: `cargo test` -> `19 passed`, no failures.

### Portable smoke runs

1. `D:\GannFinancialAstro\soak\tauri_0.10.52-pfr-v2b-r7-xe1r1_20260817_122047\logs\native_soak_report.json`
   passed. Health, read-only locks, source-profile contracts, layout creation,
   sidecar restart/recovery, execution locks, and descendant cleanup passed.
2. `D:\GannFinancialAstro\soak\tauri_0.10.52-pfr-v2b-r7-xe1r1_20260817_122204\logs\native_soak_report.json`
   passed with the same checks. Both reports have zero failed checks and
   `execution_allowed=false`; both defer only the optional unconfigured
   candlestick specialist.

## Founder Physical Inspection Checklist

Use the packaged candidate, not the development server.

- Open **Experiments** and scroll from top to bottom; confirm the safety banner
  remains visible and still says `EXPERIMENTAL - NOT CLASSICAL - NOT VALIDATED -
  NO EXECUTION`.
- Confirm the evidence labels are descriptive rather than market calls.
- Confirm populated Synthetic shows `Raw fixture sealed`.
- Confirm the derived child remains audit-only and ambiguous causal evidence
  fails closed.
- Confirm the transform leaves raw evidence unchanged.
- Select Touched or Manual with no admitted observations. Confirm the UI says
  `No observations admitted`, state is Unknown, directional raw is not shown as
  `0.000`, normalized output is Unknown, and conflict is Unknown.
- Confirm `MARKET INPUT: NONE` is visible.
- Confirm April 2025 remains `TOUCHED_DEV`, not a pristine holdout.
- Return to Chart, Fields and Chakra and confirm they remain unchanged.
- Repeat the empty-state check at a practical narrow desktop width, including
  1366 x 768.

## Locked State

```text
XE1R1_STICKY_SAFETY_BANNER=true
XE1R1_EMPTY_DIRECTION_FAILS_UNKNOWN=true
XE1R1_MARKET_LIKE_POLARITY_LABELS_REMOVED=true
XE1R1_EMPTY_DATASET_BADGE_CONTEXTUAL=true
XE1R1_BROAD_REGRESSION_COMPLETE=true
XE1_RAW_EVIDENCE_IMMUTABLE=true
XE1_CAUSAL_DEDUP_UNCHANGED=true
XE1_AMBIGUOUS_CAUSE_FAILS_CLOSED=true
XE1_POSITIVE_MODIFIER_CANNOT_FLIP_SIGN=true
XE1_MODIFIER_MATH_CHANGED=false
XE1_REAL_MARKET_EVIDENCE_ADMITTED=false
XE1_PRICE_OUTCOMES_READ=false
XE1_SOURCE_PROMOTION_CHANGED=false
XE1_FIELDS_INTEGRATION_CHANGED=false
XE1_EXECUTION_ALLOWED=false
XE1R1_FOUNDER_INSPECTION_READY=true
XE1_FOUNDER_ACCEPTED=false
XE2_CAUSAL_SCOPED_MODIFIER_IMPLEMENTED=false
```

This candidate is ready for founder inspection only. It is not a market
forecast, a classical doctrine release, a validated financial model, or an
execution package. Founder acceptance remains pending physical confirmation of
this corrected candidate.
