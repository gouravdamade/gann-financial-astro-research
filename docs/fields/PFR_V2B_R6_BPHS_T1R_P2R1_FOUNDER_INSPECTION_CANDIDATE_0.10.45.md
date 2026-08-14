# PFR-V2B-R6-BPHS-T1R-P2R1 Founder-Inspection Candidate

## Candidate identity

- Version: `0.10.45-pfr-v2b-r6-bphs-t1r-p2r1`
- Status: `founder_inspection_candidate`; not founder accepted, not stable, and
  not financially validated.
- Exact source commit:
  `e632c82d8f23142532f91d52d710e339ae9167e1`
- Build checkout declaration: fresh detached checkout, clean before packaging;
  the generated manifest also records `source_git_dirty: false`.
- Portable:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.45-pfr-v2b-r6-bphs-t1r-p2r1-tauri\GannAstroDesk.exe`
- Installer:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.45-pfr-v2b-r6-bphs-t1r-p2r1-tauri\Gann Astro Desk_0.10.45-pfr-v2b-r6-bphs-t1r-p2r1_x64-setup.exe`
- Portable SHA-256:
  `061C2FEFEE41896CE6CFE1C1174D7694ABA1671A234E45D66EBF211096083CFD`
- Installer SHA-256:
  `BFFE90D6FC809310A63A280AD6C1DB5E547063264596BE0579CBA5161E23033E`

## Included work

This candidate contains the shared Fields research-page correction and the
Windows-only founder-review packet hash portability repair:

- Fields calculations use one explicit, cached, half-open 14-calendar-day
  research page. The broad chart is visual context and does not expand the
  compute range.
- USD, JPY, pair, independent SBC, and optional BPHS requests use that same
  page. BPHS direct interactive requests longer than fourteen days fail before
  ephemeris work.
- `BPHS Calendar / 1899 Research` is a discoverable sticky Fields control and
  remains independent of SBC.
- Founder-review packet digests canonicalize only CRLF-to-LF Git transport
  line endings. A real packet alteration, including an added newline, remains
  fail-closed.

No BPHS source table, Tara dependency state, classical doctrine, polarity,
pair/SBC fusion, score, Auto Suggest, ML, MT5 execution, or market mapping was
changed. The product remains read-only and execution locked.

## Verification before packaging

| Check | Result |
| --- | --- |
| Focused Fields/window tests | 13 passed |
| Focused BPHS plus synchronized-range backend tests | 15 passed |
| Founder-review portability suite | 9 passed |
| Full frontend Vitest | 36 files, 156 tests passed |
| Oxlint | passed |
| Production frontend build | passed |
| Full backend discovery regression | 209 tests passed |
| `cargo fmt --check` | passed |
| `cargo check` | passed |
| Rust tests | 18 passed |

An initial parallel Vitest invocation encountered a host worker-start timeout
for one file while the machine was under build load. That file passed directly
(`20/20`), then the complete frontend suite was rerun cleanly with all 36 files
and 156 tests passing. No assertion failure was accepted as a pass.

## Packaged verification

The exact portable candidate was smoke-launched twice:

- `D:\GannFinancialAstro\soak\tauri_0.10.45-pfr-v2b-r6-bphs-t1r-p2r1_20260814_000400\logs\native_soak_report.json`
- `D:\GannFinancialAstro\soak\tauri_0.10.45-pfr-v2b-r6-bphs-t1r-p2r1_20260814_000555\logs\native_soak_report.json`

Each report passed all `42/42` applicable checks: backend health, disabled MT5
trading, Chakra contract/guardrails, layout persistence, deliberate sidecar
restart on the same port, recovery, and no surviving child process. The only
deferred item is the deliberately optional, unconfigured candlestick
specialist.

A direct request to the bundled backend also passed:

- endpoint: `/api/research/bphs/classical-calendar-range`;
- response: `BPHS_CLASSICAL_CALENDAR_RANGE_V1`, 40 clipped intervals for a
  one-day input, a source-named nighttime Muhurta, Tara
  `DEPENDENCY_NOT_READY`, and `executionAllowed: false`.

## Founder visual inspection

1. Launch the portable executable above, or install this separate `0.10.45`
   candidate. Do not treat it as a stable promotion.
2. Load `USDJPY`, open `Fields`, and use the sticky `BPHS Calendar / 1899
   Research` switch.
3. Confirm the Fields page label and Previous/Next controls show an explicit
   maximum 14-day page; moving the chart crosshair alone must not recalculate
   the page.
4. Confirm the BPHS panel is separate from SBC. Inspect day/night Muhurta name,
   index, page provenance, civil-weekday partial-source wording, and Tara
   `DEPENDENCY_NOT_READY`.
5. Confirm there is no supportive/adverse BPHS colour, score, market
   implication, Auto Suggest, order placement, or execution control.

These are founder-inspection steps only. This report records implementer
evidence, not founder acceptance or source certification.
