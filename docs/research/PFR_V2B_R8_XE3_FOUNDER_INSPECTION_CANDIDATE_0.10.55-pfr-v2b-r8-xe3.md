# XE3 Founder-Inspection Candidate: 0.10.55-pfr-v2b-r8-xe3

## Candidate identity

- Status: `founder_inspection_candidate`; this is not a founder acceptance.
- Source commit: `680f023c7132de8744b04189ddf35bcc93f166b0`.
- Source Git state at packaging: clean (`source_git_dirty=false`).
- Candidate label: `PFR-V2B-R8-XE3`.
- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.55-pfr-v2b-r8-xe3-tauri\GannAstroDesk.exe`.
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.55-pfr-v2b-r8-xe3-tauri\Gann Astro Desk_0.10.55-pfr-v2b-r8-xe3_x64-setup.exe`.
- Portable SHA-256: `F603F114212FD13E153B16B65D3DD521F9E24FCAFE36DDF32C41FFE0B8756FBC`.
- Installer SHA-256: `0FE1765819470AA46B560FEB0D2B83D8D41C541F11DC4351A329DDF733C4CECA`.

The release manifest and `SHA256SUMS.txt` live beside the two artifacts. The
candidate contains the packaged USD and JPY blank packets, their two identity
integrity manifests, and the independent event-identity audit. It does not
contain a local review database, runtime logs, private source material, or
credentials.

## XE3 boundary

XE3 is the founder-only, outcome-blind sign-admission workbench described in
`PFR_V2B_R8_XE3_OUTCOME_BLIND_SIGN_ADMISSION_AND_PREREGISTRATION.md`.

- It exposes 24 pre-existing `SINGLE_PASS_VERIFIED` events: 12 USD and 12 JPY.
- All decisions begin blank and are appended as revisions outside Git.
- The only permitted founder decisions are `SUPPORTIVE`, `ADVERSE`, `MIXED`,
  `NEUTRAL`, `UNKNOWN_MORE_EVIDENCE_REQUIRED`, and `REJECT_EVENT_IDENTITY`.
- Scalar projection is exact and categorical: supportive `+1`, adverse `-1`,
  explicitly neutral `0`, and mixed/unknown `null`.
- The M0-M4 preview reuses the frozen XE2 transform contract only. It does not
  select a winner, evaluate market outcomes, or create a forecast.
- With no founder decisions, preregistration is `NOT_FROZEN` and
  `freezeReady=false`.

The package manifest records all of the following as false: price-data reads,
price-outcome reads, live MT5 reads, Fields reads, SBC reads, Auto Suggest,
LLM polarity inference, market-direction inference, and execution.

## Verification results

| Check | Result |
| --- | --- |
| `npm ci` from tracked lockfile | passed |
| `npm run test` (single worker) | 41 files, 172 tests passed |
| Backend regression (`packaging_env` Python) | 245 tests passed |
| `npm run lint` | passed (Oxlint) |
| `npm run build` | passed |
| `cargo fmt --check` | passed |
| `cargo check` | passed |
| `cargo test` | 19 tests passed |
| Packaged XE3 resource presence | all six required resources present |
| Portable smoke run 1 | passed, conditional only on optional candlestick specialist absence |
| Portable smoke run 2 | passed, conditional only on optional candlestick specialist absence |

Both smoke runs started the exact portable artifact, verified a healthy
sidecar, injected and recovered from a controlled sidecar restart on the same
port, confirmed layout persistence, checked read-only execution guards, and
closed with no descendant processes left behind. Their reports are:

- `D:\GannFinancialAstro\soak\tauri_0.10.55-pfr-v2b-r8-xe3_20260819_075419\logs\native_soak_report.json`
- `D:\GannFinancialAstro\soak\tauri_0.10.55-pfr-v2b-r8-xe3_20260819_075544\logs\native_soak_report.json`

## Founder inspection checklist

1. Start the portable candidate from its immutable release folder.
2. Open **Experiments** and select **XE3 outcome-blind sign admission**.
3. Confirm the shell says outcome-blind review and hides live quote/refresh and
   market-facing footer status.
4. Confirm there are exactly 12 USD and 12 JPY `SINGLE_PASS_VERIFIED` events.
5. Inspect several rows: only event identity, astronomy facts, hashes, and
   verified boundaries should be visible; no price, returns, SBC, Fields,
   polarity hint, or LLM recommendation should appear.
6. Confirm all decision controls begin blank and that saving is locked until a
   reviewer name and outcome-blind attestation are supplied.
7. Confirm source-backed classical candidate requires exact source details;
   founder research hypothesis remains research-only.
8. Confirm unknown stays non-projectable rather than becoming neutral.
9. Confirm the M0-M4 preview names the frozen transforms without producing a
   transform winner, trading direction, or outcome result.
10. Confirm the preregistration panel remains `NOT_FROZEN` before all 24
    terminal founder reviews are completed.
11. Confirm no execution, Auto Suggest, ML, MT5, or order control becomes
    available.

## Remaining founder-only action

Founder acceptance is pending physical inspection of this exact candidate.
No founder decisions have been created or admitted, no outcome evaluation has
been approved, and no execution path has been enabled.
