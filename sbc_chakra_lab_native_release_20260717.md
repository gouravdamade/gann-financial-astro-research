# SBC Chakra Lab Native Release 0.10.7

Date: 2026-07-17 IST

## Scope

Gann Astro Desk 0.10.7 packages the Phase 4A Sarvatobhadra Chakra Lab in the
supported Tauri 2 Windows application. The release contains the deterministic
`SBC_CHAKRA_LAB_SNAPSHOT_V1` adapter, private Python endpoint, native Rust IPC
bridge, 81-cell Chakra workspace, explicit actor/motion controls, guidance
ledger, matched-cell evidence, and cell inspector.

This is a research surface, not a financial signal. The release manifest and
runtime snapshot both retain these locks:

- read-only and timestamp-safe;
- evidence cutoff equals the requested as-of instant;
- no lookahead;
- no market data in the Chakra snapshot;
- guidance only;
- financial validation is false;
- execution is not allowed;
- MT5 remains read-only market data for the wider application.

## Release Build

- Product version: `0.10.7`
- Candidate:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.7-tauri`
- Stable:
  `D:\GannFinancialAstro\release\GannAstroDesk`
- Native executable SHA-256:
  `CF8441C084BFB837499891FACFD194279C5DFCDA8FD0CEC4D1F4974FDB9CCE63`
- NSIS installer SHA-256:
  `F9AE74EB99FE3675F1C201C1786712BAE5D457324E182B97AFCBD04174C22204`
- PyInstaller backend sidecar SHA-256:
  `7F45E86DFEB0A3F492F108FB9E1840D852D8CE4F391AC68941972A296E6A0215`
- Manifest count before writing the manifest itself: 1,467 files
- Manifest payload size before writing the manifest itself: 887,336,227 bytes

## Packaged Acceptance Gate

The native soak now includes seven Chakra-specific assertions in addition to
the established health, MT5 safety, candlestick, layout persistence,
same-port sidecar recovery, diagnostics, and shutdown checks:

1. private Chakra endpoint returns success;
2. contract is `SBC_CHAKRA_LAB_SNAPSHOT_V1`;
3. compiled board contains exactly 81 cells;
4. evidence cutoff equals as-of UTC;
5. explicitly supplied Jupiter mean motion resolves to `READY`;
6. read-only, timestamp-safe, and no-lookahead flags remain true;
7. execution, market-data inclusion, and financial validation remain false
   while guidance-only remains true.

The deterministic packaged fixture produced snapshot:
`5834B5B6ACC66A9D896C0C0E4434248E4843DAC684E0535B55E115431CE62EBB`.

Accepted reports:

- candidate, 35/35 checks:
  `D:\GannFinancialAstro\soak\tauri_0.10.7_20260717_134805\logs\native_soak_report.json`;
- promoted stable, 35/35 checks:
  `D:\GannFinancialAstro\soak\tauri_0.10.7_20260717_154428\logs\native_soak_report.json`.

Both reports have zero errors, zero failed checks, same-port sidecar recovery,
and zero genuine descendant survivors.

## Verification

- Python repository suite: 226 passed.
- Frontend Vitest suite: 32 passed across nine files.
- Oxlint: passed.
- TypeScript/Vite production build: passed; only the existing chunk-size
  advisory remains.
- Focused Phase 4A Ruff lint: passed.
- Focused Phase 4A Ruff format check: passed.
- Rust tests: two passed.
- `cargo fmt --check`: passed.
- Clippy with `-D warnings`: passed.
- PowerShell release scripts: parsed successfully.
- `git diff --check`: clean apart from expected Windows line-ending warnings.

The first candidate soak reported one descendant survivor, but the process was
`git remote -v` and its start time preceded the app by 11 seconds. It was
therefore impossible to be an app child; Windows had retained stale parent-PID
metadata. The soak was corrected to ignore only processes predating the app,
and the unchanged candidate plus promoted stable copy then passed with no
survivors.

The source WebView Chakra UI was visually verified before packaging, including
the full board, actor readiness transition, constrained-width layout, and
absence of browser errors. Interactive packaged-stable QA was subsequently
completed through Windows automation:

- the signed release hash still matched the promoted `0.10.7` executable;
- the application reached its chart workspace after an approximately
  40-second cold start;
- the native Chakra tab rendered all nine rows and nine columns;
- setting Jupiter motion to `Mean` and pressing `Refresh snapshot` advanced
  the actor ledger from four ready actors to five;
- the grid, controls, evidence ledger, matched-cell area, and inspector were
  all visible together at 1482x864 without a blank surface, browser error,
  clipping, or incoherent overlap.

Visual evidence:
`gann-astro-desk\docs\visual_qa\gann_astro_desk_0107_chakra_interactive_20260717_224115.jpg`.
The exact candidate and stable native packages also remain covered by the two
accepted automated soaks.

## Recovery

- Previous stable archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.6_20260717T154235Z`
- Pre-promotion writable-state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.7_promotion_20260717T154235Z`
- Chat-session recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_211806_sbc_chakra_lab_release_0107`
- Interactive-QA recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_224115_chakra_interactive_qa`

The unrelated modified annotation database, local candlestick database, logs,
and Android worktree in the source repository remain uncommitted.
