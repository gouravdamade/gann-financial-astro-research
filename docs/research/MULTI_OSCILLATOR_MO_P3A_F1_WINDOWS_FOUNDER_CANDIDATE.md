# MO-P3A-F1 Windows Founder-Inspection Candidate

Status: `FOUNDER ACCEPTED`

Founder acceptance: `ACCEPTED 2026-08-27`

This report records the Windows package for the centrally accepted MO-P3A
unsigned activity step-wave implementation. It does not promote the candidate
to stable and does not authorize the next research milestone.

## Founder Physical Acceptance

Acceptance date: `2026-08-27`

The founder physically inspected the frozen candidate and accepted:

```text
MO-P3A = FOUNDER ACCEPTED - UNSIGNED STEP-WAVE V1
MO-P3A-F1 = FOUNDER ACCEPTED
```

Founder-supplied local screenshot evidence, not committed to Git:

- `Screenshot 2026-08-27 124521.png`
- `Screenshot 2026-08-27 124557.png`
- `Screenshot 2026-08-27 124620.png`
- `Screenshot 2026-08-27 124812.png`

The visible founder checks are: independent USD and JPY step-wave lanes;
horizontal segments with vertical interval-boundary transitions; shared raw
scale `0-16` with all filters; scale `0-12` after disabling Moon; visible exact
markers and shared crosshair; readable dense event areas; and JPY UNKNOWN
coverage rendered as a separate hatch while retaining observed nonzero counts.
The visible JPY unknown reason is
`EVENT_COMPILER_REJECTED_EVENTS_OVERLAPPING_VISIBLE_RANGE`.

The founder explicitly judged the step-wave representation more useful than
raw count bars and dense areas readable. No distinct known-zero interval was
present in the inspected range. Therefore:

```text
KNOWN_ZERO_PHYSICAL_CHECK = NOT_OBSERVED_IN_FOUNDER_RANGE
```

That is not a blocker. The source tests remain the evidence for zero-baseline
rendering. This acceptance is limited to the unsigned time-domain product and
does not authorize a sign, forecast, magnitude, pair resultant, price/outcome
read, execution or any financial claim.

## Source and Traceability

- Repository: `gouravdamade/gann-financial-astro-research`
- Starting `origin/master`: `a2fead3847b69d8a873a68da30184822fc553430`
- Accepted implementation source: `a2fead3847b69d8a873a68da30184822fc553430`
- Implementation parent: `95a624d7270bb0a6ac3d9f62423a0d2172ce584a`
- Version metadata commit: `de436b2f302c949a558133d42739dd570ce4ed7a`
- Packaging manifest metadata commit: `97787219a5a5f7db4707e4d7fa23d8df914bd37f`
- Candidate version: `0.10.61-pfr-v2b-mo-p3a-f1`
- Packaging checkout source state: clean; `sourceGitDirty=false`
- Pre-packaging backup: `D:\GannFinancialAstro\chat_session_backups\20260826_083123_mo_p3a_f1_prepackaging`

The implementation source and packaging metadata were kept separate. The
manifest records the accepted implementation commit as the functional source
and the packaging commit as the checkout used to build the candidate.

## Candidate Artifacts

Candidate root:

`D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.61-pfr-v2b-mo-p3a-f1-tauri`

- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.61-pfr-v2b-mo-p3a-f1-tauri\GannAstroDesk.exe`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.61-pfr-v2b-mo-p3a-f1-tauri\Gann Astro Desk_0.10.61-pfr-v2b-mo-p3a-f1_x64-setup.exe`
- Manifest: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.61-pfr-v2b-mo-p3a-f1-tauri\release.manifest.json`
- Checksums: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.61-pfr-v2b-mo-p3a-f1-tauri\SHA256SUMS.txt`
- Packaged sidecar: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.61-pfr-v2b-mo-p3a-f1-tauri\backend\GannAstroBackend.exe`

SHA-256 values, uppercase:

| Artifact | SHA-256 |
| --- | --- |
| Portable executable | `B5B09E62FF191603BCEDC2E276C7F83072C7F6299395D91446D2ECB8F87A1FBC` |
| NSIS installer | `23441AF1E4EE4C5640C7C762C0C804846F6B9A01AFC8FAB1A233E3E60F22E87D` |
| `release.manifest.json` | `F8CBAA2CC6202142A3CCA34BDFE4467ADC6F35594943081EF000E9AEDFDCCDD8` |
| Backend sidecar | `9C13DA86F1265CE81B6DB37EE5AF5DBB197B2B092E32C583A07DD9378BC7CB59` |
| `SHA256SUMS.txt` | `AA7F440D47AB3D77E6EB189F173DB3F3923554D68756E83665A40CC6407E9035` |

The package inspection found no bundled PDFs, JPG/JPEG/PNG source captures,
logs, JSONL runtime logs, `.git` directory or developer `node_modules` at the
candidate root. The packaged annotation database and Codex runtime are existing
sidecar resources required by the current release policy, not new source
captures.

## Contracts and Locks

- Step-wave contract: `MO_UNSIGNED_ACTIVITY_STEP_WAVE_V1`
- Activity contract: `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`, schema `2`
- Semantic unit: `ACTIVE_EVENT_COUNT`
- Exact rendering: zero-order hold over `[startUtc, endUtc)` intervals
- `polarityAssigned=false`
- `magnitudeConfigured=false`
- `normalizationUsed=false`
- `smoothingUsed=false`
- `pairResultantComputed=false`
- `priceDataRead=false` for the MO-P3A product contract
- `priceOutcomeRead=false`
- `automaticOrderPlacement=false`
- `executionAllowed=false`

The waves are independent USD and JPY activity counts. No signed contribution,
USD-JPY subtraction, pair resultant, forecast, or execution meaning is added.
Unknown coverage is separate from observed activity and is not converted to
zero, maximum, polarity or magnitude.

## Verification

Toolchain recorded by the package manifest:

- Node `v24.15.0`
- npm `11.12.1`
- Vite `8.1.4`
- Rust/Tauri package: Tauri 2 / Rust

Exact commands and results:

| Check | Command | Result |
| --- | --- | --- |
| Dependencies | `npm ci` | Passed; 148 packages installed, 149 audited; existing audit reports 5 high vulnerabilities and was not auto-fixed |
| Focused Fields | `npx vitest run --pool=threads --maxWorkers=1 src/fieldsWorkspace.test.tsx` | 23/23 passed |
| Focused wave | `npx vitest run --pool=threads --maxWorkers=1 src/views/MultiOscillatorActivityWave.test.ts` | 5/5 passed |
| Full frontend | `npx vitest run --pool=threads --maxWorkers=1` | 195/195 passed across 43 files |
| Oxlint | `npm run lint` | Passed |
| Production frontend | `npm run build` | Passed; 1,878 modules; only existing large-chunk warnings |
| Backend | `D:\GannFinancialAstro\packaging_env\Scripts\python.exe -m unittest discover -s backend -p 'test_*.py'` | 319 passed, 1 skipped |
| Rust format | `cargo fmt --check` | Passed |
| Rust compile | `cargo check` | Passed |
| Rust tests | `cargo test -- --test-threads=1` | 19 passed, 0 failed |
| Diff check | `git diff --check` | Passed |

The frontend test suite used the stable threads-pool configuration. A prior
fork-worker attempt was not used as the authoritative result.

## Packaged JSON Probe

The exact portable executable was launched with an isolated data root and its
managed sidecar was queried through the port discovered from the real child
process. The probe evidence is retained at:

`D:\GannFinancialAstro\packaged_probe\mo_p3a_f1_20260826_095956\packaged_activity_probe.json`

Diagnostic range:

`2026-08-07T00:00:00Z` through `2026-08-21T00:00:00Z`

- `GET /api/health`: HTTP `200`, `application/json`
- `POST /api/multi-oscillator/activity-range`: HTTP `200`,
  `application/json`
- HTML/doctype fallback: `NO`
- Activity contract: `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`, schema `2`
- USD source/eligible events: `61 / 61`
- USD rejected events: `21` total; relevant/irrelevant split was not emitted
  in the compact persisted probe summary
- USD activity intervals: `88`
- USD coverage: `UNKNOWN` in the packaged probe result
- JPY source/eligible events: `55 / 55`
- JPY rejected events: `20` total; relevant/irrelevant split was not emitted
  in the compact persisted probe summary
- JPY activity intervals: `89`
- JPY coverage: `UNKNOWN` in the packaged probe result

The API body was parsed as JSON and began with the `activity` object. The
health preview likewise began with a JSON object. The first probe attempt that
returned HTTP 403 used an intentionally too-short harness token; it was a
probe setup error, not a candidate routing failure, and was discarded from the
acceptance evidence.

## Native Portable Smoke

The established native smoke procedure was run twice against the exact
portable candidate:

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\gann-astro-desk\packaging\soak_tauri_release.ps1 -CandidateRoot 'D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.61-pfr-v2b-mo-p3a-f1-tauri' -AllowClosedMarketMt5Defer
```

- Run 1: `passed=true`, `conditional_pass=true`, 46 checks passed, 0 failed;
  report `D:\GannFinancialAstro\soak\tauri_0.10.61-pfr-v2b-mo-p3a-f1_20260826_043046\logs\native_soak_report.json`
- Run 2: `passed=true`, `conditional_pass=true`, 46 checks passed, 0 failed;
  report `D:\GannFinancialAstro\soak\tauri_0.10.61-pfr-v2b-mo-p3a-f1_20260826_043217\logs\native_soak_report.json`

Both runs verified initial and recovered sidecar health, same-port recovery,
layout survival, execution locks and no surviving descendants. The only
deferred check was `candlestick_specialist_optional_not_configured`.

Installer smoke was not run because the established safe procedure is the
portable/native smoke path and installing into the founder's normal location
would risk changing the existing installation. The installer hash is recorded
above for optional founder-controlled inspection.

## Packaged Visual Implementer Evidence

These screenshots were captured from the actual packaged portable candidate,
not the development server. They are implementer evidence only:

- [Fields overview](D:/GannFinancialAstro/packaged_ui_smoke/mo_p3a_f1_20260826_100419/05_fields_overview.png)
- [Activity header, filters and shared step waves](D:/GannFinancialAstro/packaged_ui_smoke/mo_p3a_f1_20260826_100419/09_activity_header_filters.png)
- [USD and JPY event rasters](D:/GannFinancialAstro/packaged_ui_smoke/mo_p3a_f1_20260826_100419/10_event_rasters.png)
- [Selected event provenance inspector](D:/GannFinancialAstro/packaged_ui_smoke/mo_p3a_f1_20260826_100419/11_selected_event_inspector.png)
- [Filter toggle and recomputed shared axis](D:/GannFinancialAstro/packaged_ui_smoke/mo_p3a_f1_20260826_100419/14_filter_toggle_after.png)
- [Unknown coverage and independent categorical fields](D:/GannFinancialAstro/packaged_ui_smoke/mo_p3a_f1_20260826_100419/16_after_chakra_refresh.png)

Observed visual results:

- USD step trace visible: `YES`
- JPY step trace visible: `YES`
- Shared raw-count axis visible: `0-16 events` before the filter smoke and
  `0-12` after removing Moon
- Zero-order-hold shape: `YES`; horizontal count segments and vertical changes
  at interval boundaries were visible
- Real gap interpolation: `ABSENT`; non-contiguous activity is not bridged
- Unknown coverage remains separate from observed count: `YES`
- Known-zero baseline: `NOT_OBSERVED_IN_FOUNDER_RANGE`; the renderer exposes
  `Baseline = 0`, but no separate known-zero interval was present in the
  founder inspection range.
- Aspect/body filter smoke: `PASS`; Moon removal changed the visible axis from
  0-16 to 0-12, and event traces/markers recomputed without changing IDs
- Event marker selection: `PASS`
- Provenance inspector: `PASS`; event ID/hash, UTC boundaries, bodies, aspect,
  astronomy contract, generator, chart/hypothesis, `NOT ASSIGNED` polarity and
  `NOT CONFIGURED` magnitude were visible
- Shared crosshair/time behavior: `PASS` during event and interval selection
- Dense-marker usability: `PASS`; exact markers remained selectable and the
  underlying step traces remained visible
- Product value versus raw bars: intentionally left for founder judgment

## Founder Inspection Checklist

The founder accepted the unsigned product on 2026-08-27. The following records
the completed acceptance scope and preserves the one item not observable in the
selected range.

- [x] USD step wave is visible
- [x] JPY step wave is visible
- [x] Shared raw-count axis is understandable
- [x] Zero-order-hold shape is visually correct
- [x] No false interpolation crosses a real gap
- [x] Exact event markers are visible
- [x] Dense markers remain usable
- [x] Aspect/body filter recomputes the wave
- [x] Re-enabling filters restores the original wave
- [x] UNKNOWN coverage is clearly separate from count
- [ ] A known-zero interval sits exactly on the baseline: not observed in the founder range
- [x] Event provenance selection works
- [x] Shared research crosshair/time synchronization works
- [x] No directional, signed or predictive output is present
- [x] Step waves add useful inspection value beyond count bars
- [x] Overall founder result: `ACCEPT`

## Final State

- MO-P3A: `FOUNDER ACCEPTED - UNSIGNED STEP-WAVE V1`
- MO-P3A-F1: `FOUNDER ACCEPTED`
- Frozen accepted unsigned baseline: `0.10.61-pfr-v2b-mo-p3a-f1`
- Stable prior package `0.10.60-pfr-v2b-mo-p2-f1-r1`: unchanged
- Next action: documentation-only MO-R2 polarity admission readiness audit
- Do not begin a signed-side wave, MO-P3B, MO-P4 or pair-resultant
  implementation from this acceptance record.
