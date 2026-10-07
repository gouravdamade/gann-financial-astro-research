# PFR-V2B-R5-F5-P2 Windows Founder Candidate

Date: 2026-10-08

## Disposition

Candidate status: `FOUNDER_INSPECTION_CANDIDATE_PENDING_NATIVE_REVIEW`.
This is not founder acceptance. The inherited native smoke harness remains a
non-pass because `chakra_jupiter_motion_explicit=false`; that condition was
not modified or reclassified. Both runs otherwise completed the required
startup, safety, persistence, recovery, and shutdown checks.

- Accepted P1 implementation: `576f7d3e24d1b3e0bef9de2061f012f62e388465`
- Packaging-prep commit: `3b194dcf7afbfecfc0a18fc2ac78b46352bfb1b9`
- Branch: `research/pfr-v2b-r5-f5-p2-windows-founder-candidate`
- Candidate version: `0.10.69-pfr-v2b-r5-f5-p1`
- Candidate root: `D:\GannFinancialAstro\release_candidate\0.10.69-pfr-v2b-r5-f5-p1`
- QA documentation commit convention: the status records the enclosing QA
  commit symbolically; its exact SHA is reported after that commit.

The P1 implementation and its semantics were not changed. The preparation
commit changes only release/version metadata, including the Tauri entry URL
version query. The package receipt binds the clean packaging-prep commit, not
this later documentation commit.

## Artifacts

- Portable executable: `D:\GannFinancialAstro\release_candidate\0.10.69-pfr-v2b-r5-f5-p1\GannAstroDesk.exe`
  - SHA-256: `89C9A38073DCE3FB86931CBDC68239DE953A127A21DE59E4B19AB2A846ABADB5`
- NSIS installer: `D:\GannFinancialAstro\release_candidate\0.10.69-pfr-v2b-r5-f5-p1\Gann Astro Desk_0.10.69-pfr-v2b-r5-f5-p1_x64-setup.exe`
  - SHA-256: `A3A34D5AB7BCDF7C6D0C00242C60A62981CEB0D54DFEE0C2213FD761DF36819F`
- Bundled backend sidecar SHA-256: `94D031F7DAD79F21B5321BD29B1BA12AC590F6224BAAEF0B46F46D7CEE3DD7F1`
- Immutable backend resource tree SHA-256 (3,541 files):
  `50A5727C41CB21B96B61F79F09F355A69B5A92788ED65B8894934C921A3C2B83`
- `build.receipt.json` SHA-256:
  `F2A14908B63B7087AE5677C34D81C27E8976EB47740A72609371D8FB4509EEAB`
- `release.manifest.json` SHA-256:
  `B5F8AFFA93BB83402F7885059987B2F27F558B05551A3AC5052EE4B95787BC84`
- `SHA256SUMS.txt` SHA-256:
  `D195DC85904C0C87E439AFE6848BAEEFF455E117A06B1FB52DADA1E38E8C6FB1`
- `BETA_README.md` is present.

The receipt and manifest both state `sourceGitDirty=false` and
`executionAllowed=false`. The portable, installer, sidecar, immutable resource
tree, receipt, and manifest hashes were independently recomputed after both
smoke runs. Every artifact entry in `SHA256SUMS.txt` and its source metadata
were checked.

The first packaging invocation built the portable app and NSIS installer but
stopped at its final cleanliness check: the sidecar helper had rewritten the
tracked `.gitkeep` line ending from LF to CRLF. No other source change was
present. The file was restored to its exact committed blob and verified clean.
The incomplete first output was preserved at
`D:\GannFinancialAstro\release_candidate\0.10.69-pfr-v2b-r5-f5-p1.incomplete-build-20261007_183916`.
The final candidate was then assembled with the established hash-checked
`build_tauri_windows.ps1 -FinalizeOnly` path from the exact completed build
outputs. Its temporary input receipt is recorded in `build.receipt.json` as
`finalizedFromReceipt`; the final artifact hashes match that binding receipt.

## Verification

- `npm ci`: passed.
- Focused F5 explanation and Fields workspace tests: **60/60** across 2 files.
- Full frontend suite: **273/273** across 50 files using
  `vitest run --pool=threads --maxWorkers=1`.
- TypeScript `tsc -b`: passed.
- Oxlint: passed.
- Production Vite build: passed. The existing warning for the 597.34 kB
  minified main chunk remains; dependencies and chunk policy were not changed.
- `cargo fmt --check`: passed.
- `cargo metadata --locked --no-deps --format-version 1`: passed.
- `cargo check --release --locked`: passed.
- `git diff --check`: passed before this report; it is rerun at closeout.
- Backend test suite and Rust test suite: not run. No backend or Rust
  application logic changed; no backend scientific regression coverage is
  claimed.

The first focused Vitest attempt encountered the known Windows fork-worker
startup timeout before test discovery. The affected Fields workspace tests
passed on a separate retry, and the full suite passed using the stable thread
pool. This was a runner startup limitation, not a test assertion failure.

## Packaged F5 Surface

The built lazy frontend asset
`FieldsWorkspace-f7DQv018.js` (SHA-256
`A9C0FAA28BA3FC499610BAE5B10212493E1BE572F4B90223E8B5F40B95F945C0`)
contains `Explanation and provenance` and the selection paths for
`FIELD_INTERVAL`, `PAIR_INTERVAL`, `ACTIVITY_EVENT`, `SBC_INTERVAL`, and
`BPHS_INTERVAL`. Static checks also found the accepted P1 labels for
`MODERN_ENGINEERING_RESEARCH_TRANSFORM`, `EXPLORATORY_UNSIGNED`,
`NOT_FINANCIALLY_VALIDATED`, `NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT`, and
`WITHHELD BY CURRENT MODE`. The 60 focused component/workspace tests exercise
rendering for those selection kinds and the accepted visibility contract.

The packaged native smoke verified the app shell and backend contracts; it
does not automate clicking through the F5 selection surface. The physical
founder checklist remains pending.

## Package Content Review

The candidate contains no private PDF/image scans, no `.bi5` provider capture,
no credentials/private keys, and no Candidate C / EMP outcome-result files.
The two `.pem` files are dependency CA bundles from Botocore and Certifi.
The existing backend packaging specification includes the tracked runtime
chart/event and annotation resources below; these are pre-existing application
inputs, not newly acquired provider captures or Candidate C outcome results:

- `astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet`
- `aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv`
- `usd_jpy_h1_mt5_metaquotes_demo_full.parquet`
- `usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet`
- `gann_aspect_annotations_raman_v2.sqlite`

No market outcome analysis or provider access occurred during this milestone.
The release manifest's `priceDataRead=false` remains the existing research /
execution lock; it does not mean the runtime package omits its pre-existing
chart-data resources.

## Native Packaged Smoke

The established native harness ran twice against the exact final portable
candidate. Each run used its own `D:\GannFinancialAstro\soak\tauri_...`
application-data root, enabled same-port sidecar recovery, and shut down with
zero surviving descendants.

1. `D:\GannFinancialAstro\soak\tauri_0.10.69-pfr-v2b-r5-f5-p1_20261007_184509\logs\native_soak_report.json`
2. `D:\GannFinancialAstro\soak\tauri_0.10.69-pfr-v2b-r5-f5-p1_20261007_184742\logs\native_soak_report.json`

Both reports show app startup, initial and recovered sidecar health, chart and
read-only contracts, execution locks, layout creation/persistence, and clean
shutdown. Both have no runtime errors, `execution_allowed=false`, and
`surviving_descendant_pids=[]`. Both harness invocations are **non-pass**,
with exactly one failed check: inherited `chakra_jupiter_motion_explicit`
(`DIGNITY_REQUIRED`). The optional candlestick specialist was deferred as
`NOT_CONFIGURED_OPTIONAL`. This condition is unchanged, is not an F5 defect,
and must not be called a passing harness result.

## Founder Inspection Checklist

Inspect the exact candidate hashes above and check:

1. The Unified Research Inspector visibly contains “Explanation and
   provenance.”
2. A USD or JPY field selection gives a readable explanation without looking
   like a forecast.
3. A pair selection says `MODERN_ENGINEERING_RESEARCH_TRANSFORM`, not a signed
   USDJPY signal.
4. An unsigned activity event shows `EXPLORATORY_UNSIGNED`,
   `polarity=NOT_ASSIGNED`, `MAGNITUDE_NOT_CONFIGURED`,
   `NOT_FINANCIALLY_VALIDATED`, and `executionAllowed=false`.
5. SBC explanation remains independent of USD/JPY interpretation.
6. Inspect the accepted note: upstream SBC magnitude vocabulary is
   `NOT_CONFIGURED`, while explanation presentation shows
   `MAGNITUDE_NOT_CONFIGURED`. Confirm this reads as a generic display label
   and does not imply that an SBC source value changed.
7. BPHS selection visibly retains `NO MARKET ROLE`.
8. A missing source locator/detail shows
   `NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT`, not fabricated provenance.
9. `UNKNOWN`, `MIXED`, `NEUTRAL`, and `WITHHELD BY CURRENT MODE` are visually
   distinct.
10. Mode 2 and Mode 3 remain non-directional, with no visible hidden-state
    leakage.
11. The desktop layout is usable at 1280x800.
12. A narrower viewport wraps long IDs/reasons without clipping or overlap.
13. Existing price, RSI, Fields & Waves, crosshair, and chart-layout behavior
    remains unchanged from the accepted P5 product.

## Preserved Locks

```text
F4-B unauthorized
F4-C unauthorized
SIGNED_ACTIVITY_COUNT_V0 unauthorized
USDJPY signed resultant unauthorized
polarity catalogue unchanged
reviewed evidence registry unchanged
Candidate C product reuse false
normalization absent
smoothing absent
source weighting absent
EMP3 unauthorized
Auto Suggest disabled
ML disabled
MT5 invocation unchanged
executionAllowed=false
```

No F4-B/F4-C, signed activity, polarity/evidence admission, Candidate C
product reuse, EMP3, MT5 invocation, or execution authorization was added.
No merge is included. Founder acceptance remains pending physical review of
the exact candidate.

Next gate: `CENTRAL_REVIEW_PFR_V2B_R5_F5_P2_WINDOWS_FOUNDER_CANDIDATE`.
