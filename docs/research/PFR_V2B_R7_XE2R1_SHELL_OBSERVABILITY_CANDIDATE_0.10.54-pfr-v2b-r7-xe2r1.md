# PFR-V2B-R7-XE2R1 Founder Inspection Candidate

## Diagnosis

The repeated 08:30 IST warning was caused by one preserved failed run for the
closed bar at `2026-08-19T03:00:00Z` (08:30 IST). The supervisor's unique
`source_bar_close_utc` rule is working as designed: a later click wakes the
supervisor but does not erase or duplicate that failed historical row.

| Field | Observed value |
| --- | --- |
| runId | `b0a0b423a70148349472469386bc457c` |
| source bar close | `2026-08-19T03:00:00Z` / 19 Aug 08:30 IST |
| status / stage | `failed` / `failed` |
| created / finished | `2026-08-19T03:45:45Z` / `2026-08-19T03:45:46Z` |
| error | `MT5 server-time normalization failed: MT5 terminal is not connected; Python and MQL5 raw tick times disagree; normalized market tick is not close to observed UTC` |
| source snapshot | none |
| price source | none |
| generationJobId | none |
| artifact | none |

The failure occurred during the initial closed-bar/history snapshot and MT5
time-normalization gate. It happened before source capture could be persisted,
before promotion, before generation, and before activation. There is no evidence
that artifact generation, capture promotion, or a backend restart caused this
run to fail.

## Progression Result

The later eligible bar proceeded independently in the live application:

| Case | Result |
| --- | --- |
| A: failed bar N exists | preserved run `b0a0b423a70148349472469386bc457c` remains failed |
| B: same bar N checked again | returned `state=error`, reused the same run ID, and created no duplicate |
| C: later bar N+1 | 09:30 IST / `2026-08-19T04:00:00Z` completed as run `8a16a3a0906e444a9344a2aa1d67a2a9`; generation job `e2f5bc33847d42dba0f09aaca94e44ea` completed and activated artifact `tn_e2f5bc33847d42dba0f09aaca94e44ea` |

Because C already works, backend retry semantics were not changed. The UI now
calls the state **Historical failure**, explains that the action checks a later
eligible bar rather than retrying N, and exposes an **Inspect failed run** detail
block with the persisted lineage and error.

## XE2 Provenance Inspection

Each real XE2 row now has an expandable **Inspect full event** section showing:

- full event hash;
- exact UTC timestamp;
- transit body and natal target;
- aspect;
- applying start and separating end UTC;
- raw Moon speed;
- `SINGLE_PASS_VERIFIED` identity status;
- reviewed packet filename and SHA-256;
- identity-integrity manifest SHA-256.

The backend and frontend event contracts carry these fields from the immutable
verified event identity. XE2 mathematics, synthetic-sign labeling, and all
market/execution locks are unchanged.

## Release

- Milestone: `PFR-V2B-R7-XE2R1`
- Candidate version: `0.10.54-pfr-v2b-r7-xe2r1`
- Status: founder-inspection candidate; founder acceptance pending
- Source implementation commit: `d333634684764111e2238e4cb59c7ec2ded50c7f`
- Candidate source/version commit: `0aaa788e6a9553b4902f1221dccfce049eb278d2`
- Source git dirty state at packaging: `false`
- Candidate root: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.54-pfr-v2b-r7-xe2r1-tauri`
- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.54-pfr-v2b-r7-xe2r1-tauri\GannAstroDesk.exe`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.54-pfr-v2b-r7-xe2r1-tauri\Gann Astro Desk_0.10.54-pfr-v2b-r7-xe2r1_x64-setup.exe`
- Manifest: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.54-pfr-v2b-r7-xe2r1-tauri\release.manifest.json`
- Checksums: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.54-pfr-v2b-r7-xe2r1-tauri\SHA256SUMS.txt`

### Artifact hashes

- Portable SHA-256: `60FCA629C8DFE17E4EDA65CDF3E5F3AE574A1427BDE73CCC8338B763471A937B`
- Installer SHA-256: `E48F9DFBD964CB364AFE0D9744D51BBC8955C835AD0CAEB108841B22C9B8EE5A`

## Verification

- Prospective refresh regression: `python -m unittest discover -s backend -p "test_prospective_refresh.py"` -> 6/6.
- XE2 backend: `python -m unittest discover -s backend -p "test_xe2_scoped_evidence_service.py"` -> 8/8.
- Full backend: `python -m unittest discover -s backend -p "test_*.py"` -> 237/237.
- Refresh chip frontend: `npm exec -- vitest run --pool=threads --no-file-parallelism --maxWorkers=1 --testTimeout=15000 src/RefreshStatusChip.test.tsx` -> 1/1.
- XE2 frontend: `npm exec -- vitest run --pool=threads --no-file-parallelism --maxWorkers=1 --testTimeout=15000 src/experimentalLabWorkspace.test.tsx` -> 4/4.
- Full frontend: `npm exec -- vitest run --pool=threads --no-file-parallelism --maxWorkers=1 --testTimeout=15000` -> 40 files, 169/169.
- Lint: `npm run lint` -> passed.
- Production build: `npm run build` -> passed; existing large-chunk advisory remains informational.
- Package dependency installation: `npm ci` -> passed from the tracked lockfile.
- Rust: `cargo fmt --check` -> passed; `cargo check` -> passed; `cargo test` -> 19/19.

### Portable smoke runs

1. `D:\GannFinancialAstro\soak\tauri_0.10.54-pfr-v2b-r7-xe2r1_20260819_044731\logs\native_soak_report.json` -> passed.
2. `D:\GannFinancialAstro\soak\tauri_0.10.54-pfr-v2b-r7-xe2r1_20260819_044847\logs\native_soak_report.json` -> passed.

Both runs had zero errors and zero failed checks. The existing optional
candlestick specialist was the only deferred check. Both reports record
`execution_allowed=false` and verify sidecar health, recovery, layout, and
clean shutdown.

## Founder Inspection Checklist

Use the exact packaged portable candidate, not the development server.

1. Open the desktop and confirm **Auto refresh** no longer describes a failed
   latest bar as an implied retry. On a preserved failed bar, open
   **Inspect failed run** and verify the run ID, `failed` stage, absent source /
   price / generation IDs, and MT5 normalization error.
2. Confirm the later-bar check remains available and does not mutate the failed
   historical row.
3. Open **Experiments** and select **XE2 scoped evidence**.
4. Expand **Inspect full event** for each real row and verify the full event
   hash, exact UTC, transit body, natal target, aspect, raw Moon speed,
   `SINGLE_PASS_VERIFIED`, packet provenance, and integrity-manifest hash.
5. Confirm XE2 still says `SIGNED MARKET EVIDENCE: NONE`,
   `SYNTHETIC_SIGN_TEST_ONLY`, and `BLOCKED_NO_REAL_SIGNED_EVIDENCE`.
6. Confirm no price/outcome, SBC, Fields, Auto Suggest, ML, live MT5, order, or
   execution path appears.

This report is implementer evidence. Founder acceptance of the corrected
candidate remains pending physical inspection.

## Locked State

`executionAllowed=false`; failed historical refresh rows are preserved;
`XE2_MARKET_OUTCOME_READ=false`; `XE2_LIVE_MT5_READ=false` in the XE2 research
surface; `XE2_AUTO_SUGGEST_ALLOWED=false`; `XE2_ML_ALLOWED=false`; and
`XE2_FIELDS_OR_SBC_FUSION=false`.
