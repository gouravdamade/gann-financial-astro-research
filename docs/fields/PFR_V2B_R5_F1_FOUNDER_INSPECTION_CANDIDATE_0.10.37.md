# PFR-V2B-R5-F1-R1 Founder-Inspection Windows Candidate

## Status

`0.10.37-pfr-v2b-r5-f1-r1` is an immutable **founder-inspection
candidate**. It is not a stable promotion, a financial validation, an
evidence-backed oscillator release, or permission for Auto Suggest or order
execution.

The candidate contains the Dedicated Fields Workspace from source commit
`95ede57ca1abcdd8986bea8a57fb2bb26b97d8d8` and the idle-sidecar recovery
fix from source commit `f748168df079c4322ec431ad64131dea0ab4a43a`.
It was assembled from clean packaging checkout
`d779a23a3fb205df091e196a7cf3f7e393d04daa`.

The previous `0.10.36-pfr-v2b-r5-f1` candidate is superseded for founder
inspection. Its first smoke run correctly exposed an idle sidecar-recovery
gap: after the sidecar was stopped during an otherwise idle application
session, the native supervisor did not notice until a later command resumed.
The watchdog in `f748168` closes only that process-supervision gap. It adds no
doctrine, field values, scoring, market interpretation, execution behavior, or
new API surface.

## Candidate files

- Candidate folder:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.37-pfr-v2b-r5-f1-r1`
- Portable launcher:
  `GannAstroDesk.exe`
- NSIS installer:
  `Gann Astro Desk_0.10.37-pfr-v2b-r5-f1-r1_x64-setup.exe`
- Manifest: `release.manifest.json`
- Checksums: `SHA256SUMS.txt`

| Item | SHA-256 |
| --- | --- |
| Portable launcher | `A1203F2A48F29C36212F10BFE66671A6203EFB8E94B7938D17A5295E2D0DCC67` |
| NSIS installer | `FEDCCC43EE0D4AB004C1B40BA484339E933999D89074040D27B8B3604DEDC712` |
| Bundled backend sidecar | `E3AA5DACE665F94390773D93CE5A84EAF36B3B897D0B5C0B351E54AA42212169` |

The manifest declares `source_git_dirty: false`. It records Node `v24.15.0`,
`npm@11.12.1`, Tauri 2/Rust, the source commit above, and the packaging checkout.

## Source verification

All checks below were run from a clean packaging checkout before candidate
creation:

| Check | Result |
| --- | --- |
| Frontend lint | passed |
| Focused Fields tests | 4 files / 36 tests passed |
| Full frontend suite | 34 files / 148 tests passed |
| Backend regression suite | 184 tests passed |
| Production frontend build | passed |
| `cargo fmt --check` | passed |
| `cargo check --offline` | passed |
| Rust tests | 18 passed |

The full frontend suite was run with the repository-supported single-worker
thread command after an initial process-worker startup failure at test 128. No
assertion failed in that initial run; the supported rerun completed all 148
tests successfully.

## Portable smoke verification

The exact portable candidate was launched twice. Each run deliberately stopped
the healthy idle sidecar and required the native supervisor to recover it on
the same loopback port.

| Run | Report | Result |
| --- | --- | --- |
| 1 | `D:\GannFinancialAstro\soak\tauri_0.10.37-pfr-v2b-r5-f1-r1_20260806_073423\logs\native_soak_report.json` | passed, conditional only on optional candlestick specialist absence |
| 2 | `D:\GannFinancialAstro\soak\tauri_0.10.37-pfr-v2b-r5-f1-r1_20260806_073553\logs\native_soak_report.json` | passed, conditional only on optional candlestick specialist absence |

Both reports confirm all required checks, including backend health, sidecar PID
change, same-port recovery, recovered health, persisted layout, chart/Chakra
contracts, execution locks, read-only MT5 behavior, and no descendant processes
left after shutdown. In particular, both report:

```text
execution_allowed: false
mt5_trade_allowed_false: true
mt5_app_execution_locked: true
mt5_read_only_mode: true
sidecar_pid_changed: true
same_port_recovery: true
recovered_health: true
no_descendant_survivors: true
```

## Founder-visible Fields product contract

The candidate contains the separate top-level **Fields** surface. It keeps the
market chart, USD/base categorical lane, JPY/quote categorical lane, transparent
USDJPY pair-relative lane, independent SBC lane, and audit detail together in a
normal vertically scrolling workspace.

`FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1` remains a modern research transform,
not classical doctrine, a forecast, an SBC confirmation, or a price signal. It
uses only stored categorical interval boundaries:

```text
sideBalance = sideNet / sideGross, when sideGross > 0
pairRaw = baseBalance - quoteBalance
pairDisplay = clamp(pairRaw / 2, -1, +1)
```

If either side is unknown, the pair lane is the visible gap
`UNKNOWN_SIDE_EVIDENCE`; it is never substituted with zero or neutral. No
smoothing, interpolation, curve fitting, price outcome, Shadbala, Drik,
Ashtakavarga, SBC fusion, Auto Suggest, or execution behavior was added.

Trailokya source-only geometry remains an independent SBC availability lane:
`GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED`. It has no score, polarity, guidance
units, wave, or scored fallback. Its seven unresolved source gaps remain
visible. Phaladeepika retains its existing independent behavior.

## Physical founder checks still pending

No screenshot or founder acceptance has been manufactured from a development
browser. The following checks must be performed against this exact portable or
installed candidate:

1. At 1920 x 1080, verify price chart and Fields lanes together.
2. Verify top-level Fields navigation and that Chakra shows only the compact
   `Open in Fields` hand-off.
3. In Trailokya, verify USD/JPY lanes plus the explicit SBC
   `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` lane and all seven source gaps.
4. In Phaladeepika, verify the independent SBC range behavior remains intact.
5. At 1366 x 768 and the required Windows scale settings, verify the Fields
   workspace remains vertically usable without hidden controls or clipped panes.

Founder acceptance, stable promotion, R4-T3, Trailokya interval compilation,
polarity/magnitude admission, price conversion, Auto Suggest, and execution
remain outside this candidate.

## Native inspection note

The first manual launch of this new portable path displayed the standard
Windows Firewall consent prompt for `Gann Astro Desk`. No public/private
network permission was granted during packaging verification; the prompt was
dismissed and the manual inspection launch was closed. The automated portable
smokes had already verified the local managed-sidecar behavior. Any later
decision to permit companion-network access must be made deliberately during
founder physical inspection, not inferred from this candidate record.
