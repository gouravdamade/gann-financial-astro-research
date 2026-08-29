# MO-R3-R1-F1 Windows Founder Review Candidate

## Status

Candidate status: `BUILT_FOR_FOUNDER_INSPECTION`

Founder review UI state: `PENDING_FOUNDER_PHYSICAL_INSPECTION`

Founder decisions: `0`

This record covers the immutable Windows candidate for the MO-R3-R1-F1
founder-review gate. It does not classify polarity, admit evidence, create a
signed wave, or change the product contract.

## Candidate

- Version: `0.10.62-pfr-v2b-mo-r3-r1-f1`
- Milestone: `MO-R3-R1-F1`
- Functional implementation source commit: `df0289a253ba2c078f73c34de0ce4de4ef181966`
- Packaging checkout commit: `e38c64ca89aaedf554d64fc28c225f9da3761ac2`
- Founder-review protocol commit: `1610c7731fff620a7943b30c1b1c751d7979fbfb`
- `source_git_dirty`: `false`
- `executionAllowed`: `false`
- Market direction: `ABSTAIN`

Artifacts:

- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.62-pfr-v2b-mo-r3-r1-f1-tauri\GannAstroDesk.exe`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.62-pfr-v2b-mo-r3-r1-f1-tauri\Gann Astro Desk_0.10.62-pfr-v2b-mo-r3-r1-f1_x64-setup.exe`
- Release manifest: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.62-pfr-v2b-mo-r3-r1-f1-tauri\release.manifest.json`
- Checksums: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.62-pfr-v2b-mo-r3-r1-f1-tauri\SHA256SUMS.txt`

Final artifact SHA-256 values:

| Artifact | SHA-256 |
| --- | --- |
| `GannAstroDesk.exe` | `D9BA422D7A5051BDDCD07454B3B6CA61BDAAE08FB044252771E1FE1A3D2B3F7E` |
| `Gann Astro Desk_0.10.62-pfr-v2b-mo-r3-r1-f1_x64-setup.exe` | `AABB125114B7D344D8E1659BC2A53E5A378AD746DE1C8D6B52001CB1980E0551` |
| `backend/GannAstroBackend.exe` | `7E21BE0CDEE523D7AB4E7DFE64E03137A71940FB079FECECBC521FFFC7C67ECC` |
| `release.manifest.json` | `9FE17198963E5A9BF11BEA02C6A3B73F7D44A4C47CB135642AB05AC11D60D9F0` |

The candidate contains no private source photographs, PDFs, OCR dumps,
temporary renders, runtime logs, SQLite research databases, credentials, or
other private source bytes. It renders the reviewed packets from the lawful
derived resources packaged by the existing release procedure.

## Founder-review integrity

The packaged API probe and recovery-aware smoke runs observed:

- exactly 12 USD and 12 JPY rows, 24 total;
- every row with identity status `SINGLE_PASS_VERIFIED`;
- blank founder decisions after startup and after recovery;
- packet-bound `Swiss Ephemeris 2.10.03` with
  `ephemerisVersionProvenance=PACKET_COMPILER_METADATA`;
- immutable blank packets and identity-integrity manifests unchanged;
- invalid `SUPPORTIVE` export with whitespace-only reasoning rejected with
  `400 application/json`, without persisting a decision.

Blank packet hashes used by the smoke checks:

- USD blank packet: `0484DA85FB7D78DF88EB154C0EE40963FC54AD2B97E11CA7A5EC53475F426609`
- JPY blank packet: `D055EC10CF29766FCBE365DCFD14588F82B4C8B277832E3622C3A436CE7A1A41`
- USD identity manifest: `CC7B78675B33ED20F72E2659133F6A60CF6BC92DAD03AEE19ABC307D7C22E06`
- JPY identity manifest: `9F6FA3D77D118720388C48DBD86875224F737FE5DC837E8DAFEF940FBD4A73DE`

## Targeted packaged API probe

Final fresh probe:

`D:\GannFinancialAstro\packaged_api_probe\mo_r3_r1_f1_20260829_142830\packaged_api_probe.json`

The exact portable candidate was launched with a fresh data root and a fresh
loopback API port (`62808`). The requests returned:

| Request | Result |
| --- | --- |
| `GET /api/health` | `200 application/json` |
| `GET /api/chart` | `200 application/json` |
| `GET /api/founder-review/workbench` | `200 application/json`, 24 rows, 2 sides, all single-pass |
| `GET /api/founder-review/workbench?side=USD` | `200 application/json` |
| `GET /api/founder-review/workbench?side=JPY` | `200 application/json` |
| invalid `POST /api/founder-review/export` | `400 application/json`, `SUPPORTIVE requires non-empty founder reasoning` |

The probe therefore verifies the real packaged founder-review API path, not
only sidecar health.

## Recovery-aware portable smoke

Both final isolated runs passed all required product gates:

1. `D:\GannFinancialAstro\packaged_smoke\mo_r3_r1_f1_run1_20260829_141548\extended_smoke_report.json`
   - `passed=true`, `failedChecks=[]`, `errors=[]`;
   - initial and recovered sidecar used the same port `61845`, with a changed
     sidecar PID;
   - recovered workbench remained 24 rows with zero decisions;
   - clean shutdown and no surviving descendants.
2. `D:\GannFinancialAstro\packaged_smoke\mo_r3_r1_f1_run2_20260829_141710\extended_smoke_report.json`
   - `passed=true`, `failedChecks=[]`, `errors=[]`;
   - initial and recovered sidecar used the same port `58079`, with a changed
     sidecar PID;
   - recovered workbench remained 24 rows with zero decisions;
   - clean shutdown and no surviving descendants.

Both runs also checked packet-bound ephemeris provenance, outcome-blind
guardrails, rejection of the invalid export, blank packet hashes, and
identity-manifest hashes.

## Generic soak harness result

The two earlier generic release soak attempts are not reported as product
passes. They ended with `GENERIC_SMOKE_HARNESS_TIMEOUT` after the optional
local candlestick-health step:

- `D:\GannFinancialAstro\soak\tauri_0.10.62-pfr-v2b-mo-r3-r1-f1_20260827_152638\logs\native_soak_report.json`
- `D:\GannFinancialAstro\soak\tauri_0.10.62-pfr-v2b-mo-r3-r1-f1_20260827_153203\logs\native_soak_report.json`

The checks completed before the timeout included startup, initial health,
execution locks, Chakra, Agarwal, and planetary-line checks. The timeout is a
harness result, not evidence that the candidate passed the generic soak.

## Packaged visual inspection

The exact portable executable was opened interactively. The following visual
evidence was captured outside the repository:

- `D:\GannFinancialAstro\packaged_visual\mo_r3_r1_f1_evidence\founder_review_usd_top.png`
- `D:\GannFinancialAstro\packaged_visual\mo_r3_r1_f1_evidence\supportive_reason_required.png`
- `D:\GannFinancialAstro\packaged_visual\mo_r3_r1_f1_evidence\founder_review_jpy_rows.png`

Observed visual checks:

- Founder Review opens from Fields and displays the neutral astronomy packet
  guardrail;
- USD and JPY sections display separately with the source chart and hypothesis
  identities;
- each visible event shows its immutable event hash, exact event timing,
  applying/exact/separating facts, astronomy contract, and
  `SINGLE_PASS_VERIFIED` status;
- selecting `SUPPORTIVE` exposes a required founder-reasoning field and does
  not prefill reasoning;
- the temporary decision was restored to `Choose founder decision` before
  closing the app;
- no founder decision was exported and no decision was persisted;
- no price, returns, SBC, LLM, catalogue, wave, market-direction, or execution
  content appeared in the Founder Review workbench.

The screenshot files are implementer evidence only. They are not founder
acceptance.

## Test results

- Focused backend founder-review tests: `13 passed`.
- Focused source-packet tests: `4 passed`.
- Focused frontend founder-review tests: `3 passed`.
- Full backend regression: `323 passed, 1 skipped`.
- Full frontend suite: `196 passed across 43 files`.
- Research test suite: `45 passed`.
- Oxlint: passed.
- Production frontend build: passed, 1,878 modules.
- `cargo fmt --check`: passed.
- `cargo check`: passed.
- Rust tests: `19 passed`.
- `git diff --check`: passed.
- Recovery-aware packaged smoke: `2/2 passed`.
- Targeted packaged API probe: passed.
- Generic soak harness: `2` attempts, both `GENERIC_SMOKE_HARNESS_TIMEOUT`, not
  counted as passes.
- Installer smoke: `NOT_RUN_TO_PROTECT_EXISTING_INSTALLATION`.

## Locks and next action

The candidate keeps all of these disabled: polarity classification, evidence
admission, signed wave creation, pair resultant, price/outcome reads, SBC,
LLM interpretation, ML decisions, Auto Suggest, live inference, MT5 order
logic, and execution. `executionAllowed=false`.

Founder decisions remain blank and the candidate remains pending physical
founder inspection. The exact next action is for the founder to inspect the
portable executable at the path above and confirm the Founder Review visual
surface. No later milestone is started automatically.

## Founder inspection checklist

1. Launch the exact portable executable.
2. Open `Fields` and then `Founder Review`.
3. Confirm the neutral packet guardrail and read-only state.
4. Confirm 12 USD plus 12 JPY rows are visible and all are
   `SINGLE_PASS_VERIFIED`.
5. Expand an event and inspect its full hash, exact UTC time, transit body,
   natal body, aspect, packet-bound ephemeris provenance, and identity status.
6. Confirm decisions start blank and no reasoning is prefilled.
7. Confirm `SUPPORTIVE` and `ADVERSE` require non-empty founder reasoning.
8. Confirm `UNKNOWN_MORE_EVIDENCE_REQUIRED` remains an unknown gap rather than
   becoming `NEUTRAL`.
9. Confirm invalid incomplete export is rejected and no decision is persisted.
10. Confirm no price, outcome, SBC, LLM, ML, wave, market-direction, Auto
    Suggest, MT5, or execution content appears.
11. Close the app and confirm it shuts down cleanly.

Founder acceptance is not claimed by this report.
