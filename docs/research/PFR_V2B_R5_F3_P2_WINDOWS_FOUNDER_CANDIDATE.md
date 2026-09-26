# PFR-V2B-R5-F3-P2 Windows Founder-Inspection Candidate

Status: candidate built; founder physical inspection is pending.

This record packages the centrally accepted P1-R1 Fields and Waves
workstation. It introduces no field mathematics, activity mathematics,
backend contract, source doctrine, empirical path, or execution capability.

## Identity

- Candidate version: `0.10.65-pfr-v2b-r5-f3-p1-r1`
- Milestone: `PFR-V2B-R5-F3-P2`
- Packaging branch: `research/pfr-v2b-r5-f3-p2-windows-founder-candidate`
- Accepted P1-R1 source commit: `8eba91df3d074be093f53d06be107f133638eecf`
- Candidate implementation/source commit: `0454b2e77d2f8abf20b548e505ee4fa4f6a158cc`
- Prep commit: `0454b2e77d2f8abf20b548e505ee4fa4f6a158cc`
- Packaging checkout: clean at build time; `sourceGitDirty=false`
- Candidate status: `founder_inspection_candidate`

P1-R1 is centrally accepted. The preserved correction facts are:

- `policyWithholdingIncludesAccessibleDom=true`
- `suppressedDirectionalHitboxesRendered=false`
- `suppressedDirectionalStateInSummary=false`
- `mode1DirectionalInspectionPreserved=true`

The product state remains `PFR-V2B-R5-F3-P1=PRODUCT_IMPLEMENTATION_COMPLETE`.

## Artifact Binding

Candidate directory:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.65-pfr-v2b-r5-f3-p1-r1-tauri`

- Portable executable: `GannAstroDesk.exe`
- Portable SHA-256: `402775FC3A3DABD8BC03BB5C4873B7715045A34BE47FB85E10E9C9D0E7EFCC2C`
- Installer: `Gann Astro Desk_0.10.65-pfr-v2b-r5-f3-p1-r1_x64-setup.exe`
- Installer SHA-256: `3DC20999BB87239859161BC5742621BC1585F6BAE93C973A5FD2AD9B7E542895`
- Sidecar: `backend/GannAstroBackend.exe`
- Sidecar SHA-256: `7928659ACF79FD8E3F5963FEB5423FEE161DFA0365EE2959F2400819614B6D76`
- Immutable backend resource-tree SHA-256:
  `178930DAED66C73A064EFCC8E72BF737EB79E1442F9FD9541C0CB2425B762C27`
- Build receipt: `build.receipt.json`
- Build receipt SHA-256: `4B8C1E9821ECA4170756D59D1BF8A75AFBF0A54192F9C19035D810AF4E078A18`
- Release manifest: `release.manifest.json`
- Release manifest SHA-256: `97781E87A21EF44E26FE02414CF6CED79E52787A57C03A1C7E452FDEF9BB6B2B`
- Checksums: `SHA256SUMS.txt`

The receipt and manifest both bind source commit
`0454b2e77d2f8abf20b548e505ee4fa4f6a158cc`, declare `sourceGitDirty=false`,
and declare `executionAllowed=false`. The Tauri entry URL is exactly
`index.html?v=0.10.65-pfr-v2b-r5-f3-p1-r1`.

No private page images, PDFs, BI5 files, credentials, or tokens were bundled.
The pre-existing research sidecar resource tree may contain ordinary packaged
application research data; it is not a private source-image bundle.

## Verification

- `npm ci`: passed; npm reported 7 dependency advisories (2 moderate, 5 high)
  and no changes were applied.
- Focused P1-R1 Fields checks: preserved `33/33 passed`.
- Full frontend: `44 files, 213 tests passed`.
- TypeScript/Vite production build: passed.
- Oxlint: passed.
- `cargo fmt --check`: passed.
- `cargo metadata --no-deps`: passed.
- `cargo check`: passed.
- Native Tauri release build and x64 NSIS bundle: passed.
- `git diff --check`: passed before and after packaging.

## Native Portable Smoke

The established `soak_tauri_release.ps1` harness was run twice against this
exact portable executable with separate data roots and with crash recovery
enabled. Both launches used the actual packaged Tauri executable and managed
sidecar, not Vite.

Run 1 report:

`D:\GannFinancialAstro\soak\tauri_0.10.65-pfr-v2b-r5-f3-p1-r1_20260926_171946\logs\native_soak_report.json`

Run 2 report:

`D:\GannFinancialAstro\soak\tauri_0.10.65-pfr-v2b-r5-f3-p1-r1_20260926_172108\logs\native_soak_report.json`

Both runs produced the same result:

- actual packaged app launch: passed;
- sidecar health, read-only MT5 state, chart layout persistence, and same-port
  sidecar recovery: passed;
- packaged Agarwal source profile endpoint: passed;
- Agarwal contract: `AGARWAL_GEOMETRY_STRENGTH_INSPECTOR_V1`;
- Agarwal board cell count: `81`;
- Agarwal source profile read-only guard: passed;
- execution/refresh/diagnostic locks: passed;
- zero surviving descendants after clean shutdown: passed;
- optional candlestick specialist: deferred because not configured;
- harness result: failed only on `chakra_jupiter_motion_explicit`.

The failed harness assertion is inherited from the existing native smoke
contract: its synthetic Jupiter probe returns `DIGNITY_REQUIRED` rather than
the harness's expected explicit motion state. There were no runtime errors,
and every other recorded check passed in both runs. This P2 packaging record
does not change that unrelated source or harness behavior and therefore does
not claim a clean all-green native smoke result.

The desktop computer-use surface available to this session exposed browser
targets only and no bindable native Tauri window. Consequently, screenshot-
level physical visual QA at an exact 1280x800 window was not executed here;
no visual acceptance is claimed. Frontend contract tests and the packaged
endpoint smoke above remain the available verification evidence. Founder
inspection is still required.

## Founder Physical Inspection Checklist

Please inspect the actual portable executable at the candidate directory and
record the result separately. The expected review sequence is:

1. Launches at the native default `1280x800` viewport without clipping.
2. Fields workstation order is price/aspect context, shared crosshair and
   selection summary, USD, JPY, pair, SBC, unsigned waves, optional BPHS,
   unified inspector, and audit details.
3. Mode 1 keeps USD/JPY source-profiled labels, pair engineering research,
   unknown gaps, MIXED versus NEUTRAL, interval selection, inspector detail,
   and unsigned/raw activity.
4. Mode 2 visibly says `CALIBRATION SOURCE MISSING`; USD/JPY/pair directional
   output is withheld without hidden directional hitboxes, while activity and
   event selection remain available.
5. Mode 3 keeps activity/event geometry and shows retained directional
   selections only as `WITHHELD BY CURRENT MODE`; no suppressed directional
   value is exposed through visible UI, tooltip, or accessibility text.
6. `SBC_TRAILOKYA_1972_V1` remains source-only and shows
   `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` where applicable.
7. Shared crosshair/selection synchronization works across fields, activity,
   BPHS, and the inspector; crosshair movement does not trigger a network
   request.
8. BPHS remains independent and marked `NO MARKET ROLE`.
9. No Candidate C, EMP3, provider, outcome, Auto Suggest, ML, broker, or
   order path is visible or reachable.
10. `executionAllowed=false` and `automaticOrderPlacement=false` remain true.
11. Existing chart data may load, but no new provider capture or outcome
   analysis is performed.

## Boundaries and Next Gate

This is a founder-inspection candidate, not founder acceptance. The candidate
does not authorize or expose market direction, polarity, score aggregation,
price conversion, Auto Suggest, ML, MT5 execution, orders, Candidate C, EMP3,
or empirical outcome work. No source or product behavior changed after the
prep commit.

The next gate is:

`CENTRAL_REVIEW_PFR_V2B_R5_F3_P2_WINDOWS_FOUNDER_CANDIDATE`
