# XE3R1 Founder-Inspection Candidate: 0.10.56-pfr-v2b-r8-xe3r1

## Status

- Status: `founder_inspection_candidate`; this is not a founder acceptance.
- Candidate 0.10.55 remains immutable and is not overwritten.
- Candidate label: `PFR-V2B-R8-XE3R1`.
- Source commit at packaging: `6a4230a65921a60769caab09e9f259e9e039fd54`.
- `source_git_dirty=false`.
- `executionAllowed=false`.

## Diagnosis of the 0.10.55 failure

The failure was a packaged sidecar concurrency defect. It was not a missing
route, an incorrect Tauri API base, a missing XE3 module, or a missing packet.

The exact 0.10.55 sidecar advertised `http://127.0.0.1:55214` and was reached
by the failing requests. The two requests recorded as HTTP failures in
`D:\GannFinancialAstro\soak\xe3_diagnosis_20260820\logs\runtime_diagnostics.jsonl`
were:

| Request | Method | Status | Content-Type | Body prefix |
| --- | --- | --- | --- | --- |
| `http://127.0.0.1:55214/api/experiments/xe3/preregistration` | GET | 500 | `text/html; charset=utf-8` | `<!doctype html><html lang=en><title>500 Internal Server Error</title>...` |
| `http://127.0.0.1:55214/api/experiments/xe3/signed-ledger` | GET | 500 | `text/html; charset=utf-8` | `<!doctype html><html lang=en><title>500 Internal Server Error</title>...` |

The workbench route itself returned HTTP 200 JSON in the direct route probe.
An unknown API path also returned the old Flask HTML 404 form, proving that
the generic API error boundary could emit HTML. The sidecar error log records
the actual exception:

```text
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process:
'D:\\GannFinancialAstro\\app_data\\xe3_outcome_blind_sign_admission\\index.tmp'
-> 'D:\\GannFinancialAstro\\app_data\\xe3_outcome_blind_sign_admission\\index.json'
```

`build_xe3_preregistration_status()` and the signed-ledger path both reach
`_latest_ledger()`. Concurrent startup reads could therefore invoke
`_write_index()` at the same time. The old implementation used one shared
`index.tmp` name. On Windows, one request could still hold that file while a
second request attempted to open or replace it. Flask then generated its
default HTML 500 response. The frontend called `response.json()` on that body,
which surfaced as `Unexpected token '<', "<!doctype "... is not valid JSON`.

This diagnosis was reproduced from the sidecar runtime diagnostics and the
stack trace, rather than inferred from the frontend error.

## Development versus packaged transport

| Execution | Frontend origin/API request | Backend target | Routing result |
| --- | --- | --- | --- |
| Development | `http://127.0.0.1:5173/api/experiments/xe3/...` | Vite proxy to `http://127.0.0.1:8788` | Relative requests are proxied to the development Flask server. |
| Tauri packaged | `http://127.0.0.1:<managed-port>/api/experiments/xe3/...` | Rust-managed loopback sidecar port, with `X-Gann-Astro-Token` | `src/api.ts` resolves the managed base and sends the token. |

The packaged failure requests reached Flask on port 55214. The packaged
sidecar contained `xe3_sign_admission_service`, all three XE3 routes, the USD
and JPY blank packets, and their integrity manifests. The bad response was
therefore generated after route registration, during the shared index update.

## Bounded repair

Implementation commit: `1970f86` (`fix(xe3): serialize admission ledger startup reads`).

- `xe3_sign_admission_service.py` now serializes the index/ledger transaction
  with a process-local re-entrant lock and writes through a unique temporary
  file in the target directory before atomic replacement. The append-only
  ledger and immutable packet identities are unchanged.
- `server.py` now returns structured JSON for API 404 and 500 responses. API
  failures cannot silently become the SPA HTML document.
- `src/api.ts` reads the response body before decoding JSON and reports HTTP
  status, content type, and a bounded body prefix when a non-JSON response is
  received.
- Regression tests cover the concurrent startup reads, structured API errors,
  packaged base resolution, and the existing XE2 transport.

No XE3 mathematics, event identity, blank packet, outcome-blind rule, M0-M4
transform, preregistration state, or execution boundary was changed.

## Post-repair packaged endpoint verification

The exact new portable executable was launched with an isolated D: data root.
The sidecar advertised port `55782`. All startup requests below returned HTTP
200 with `application/json` and parsed successfully:

| Request | Result |
| --- | --- |
| `http://127.0.0.1:55782/api/experiments/xe3/workbench` | 24 rows: 12 USD + 12 JPY, all `SINGLE_PASS_VERIFIED` |
| `http://127.0.0.1:55782/api/experiments/xe3/signed-ledger` | JSON ledger response |
| `http://127.0.0.1:55782/api/experiments/xe3/preregistration` | JSON response, `NOT_FROZEN` |

The workbench response uses `payload.workbench.sides[*].rows`; the exact
parsed counts were 24 total, 12 USD, and 12 JPY. An API 404 and an injected
internal error were also checked after the repair; both returned structured
JSON rather than HTML.

## Candidate artifacts

- Candidate root:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.56-pfr-v2b-r8-xe3r1-tauri`
- Portable:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.56-pfr-v2b-r8-xe3r1-tauri\GannAstroDesk.exe`
- Installer:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.56-pfr-v2b-r8-xe3r1-tauri\Gann Astro Desk_0.10.56-pfr-v2b-r8-xe3r1_x64-setup.exe`
- Release manifest:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.56-pfr-v2b-r8-xe3r1-tauri\release.manifest.json`
- Checksums:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.56-pfr-v2b-r8-xe3r1-tauri\SHA256SUMS.txt`

| Artifact | SHA-256 |
| --- | --- |
| Portable executable | `30E2508909C06BEE663ECF431035D2E2D196C67C8E080D95F84AEC2D4FE5184B` |
| NSIS installer | `844DE85B0DF3F74111AE2C452F04B1D158D73E1A374E409132C7B3A8543235BD` |
| Packaged sidecar | `2C13B8663AEBCA8FA2DFA3751B44E2F9BA7B6A98A3EEA1BDB6C888D9A2F4602` |
| Release manifest | `CF4A30B8CB86488C8337ABF3ABB7758C9C61A56327BEF5DB9B0BC0DCED76CAD4` |

The release manifest records `source_git_dirty=false`, all XE3 data/market
read locks as false, `xe3_execution_allowed=false`, and no private source
material or runtime database in the package.

## Verification

| Check | Result |
| --- | --- |
| Focused XE3 backend service suite | 8 passed |
| Focused XE3 server/API suite | 4 passed |
| Focused frontend API + XE3 panel suite | 16 passed |
| Full backend regression | 250 passed |
| Full frontend suite | 41 files, 174 tests passed |
| `npm.cmd run lint` | passed |
| `npm.cmd run build` | passed |
| `cargo fmt --check` | passed |
| `cargo check` | passed |
| `cargo test` | 19 passed, 0 failed |
| Packaged endpoint smoke | passed: JSON, 24 rows, 12 USD + 12 JPY |

Portable native smoke run 1 passed (conditional only on the optional
candlestick specialist not being configured):

`D:\GannFinancialAstro\soak\tauri_0.10.56-pfr-v2b-r8-xe3r1_20260820_192820\logs\native_soak_report.json`

Portable native smoke run 2 passed with the same condition:

`D:\GannFinancialAstro\soak\tauri_0.10.56-pfr-v2b-r8-xe3r1_20260820_193954\logs\native_soak_report.json`

Both native runs verified sidecar restart/recovery, layout survival,
read-only execution guards, and clean shutdown with no surviving descendants.

## Physical packaged UI smoke

The exact portable candidate was launched, not the development server. After
the Windows Firewall prompt was approved for the Private network, the UI was
inspected through **Experiments -> XE3 outcome-blind sign admission**.

- The workbench rendered with USD and JPY summaries at `0 / 12 decided`.
- The USD packet displayed a verified event with full event hash, exact UTC
  and IST time, transit body, natal body, aspect, raw motion speed, chart and
  hypothesis identities, and `SINGLE PASS VERIFIED`.
- The packet selector was switched to JPY and rendered a JPY verified event
  with the same provenance fields.
- The visible safety state remained `OUTCOME-BLIND REVIEW - PRICE HIDDEN`,
  `NO WINNER`, and `PREREGISTRATION NOT_FROZEN`.
- The screen showed no price, return, Fields, SBC, Auto Suggest, ML, MT5, or
  execution control.
- The candidate was closed cleanly; no process remained under its immutable
  candidate path.

This is implementer smoke evidence, not founder acceptance.

## Locked state and remaining founder action

- 24 event identities remain immutable.
- Blank USD and JPY packets remain untouched.
- No founder decision was created.
- Outcome evaluation remains blocked.
- Preregistration remains `NOT_FROZEN`.
- `executionAllowed=false`.
- 0.10.55 remains an immutable failed founder candidate for historical record.

Founder inspection of the corrected 0.10.56 candidate is still the remaining
acceptance step.
