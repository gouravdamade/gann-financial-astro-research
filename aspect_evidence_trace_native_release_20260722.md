# Aspect Evidence Trace Native Candidate 0.10.19

Date: 2026-07-22

## Candidate Identity

- Source commit: `79a99005e3c59c95868f1ccea88247e504ab82ce`
- Source dirty at build time: `false`
- Candidate root:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.19-tauri`
- Portable executable:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.19-tauri\GannAstroDesk.exe`
- Portable SHA-256:
  `45B7087DDBEC3BC535B0575912ECACB167652FA427703002DEE7BE4BBB64B017`
- NSIS installer:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.19-tauri\Gann Astro Desk_0.10.19_x64-setup.exe`
- Installer SHA-256:
  `94FA71119210E135B5B941A3F57FD45A74E8856DC427B81E7D20F91176B26041`
- Both executable metadata records report version `0.10.19`.
- Candidate tree: 1,467 files / 896,521,493 bytes, including the installer
  and release manifest.

## Included Scope

This candidate packages `GANN_ASPECT_EVIDENCE_TRACE_V1` and the Analyze
Aspect Trace tab. It includes timestamp-safe Start/window/end evidence plus
the post-window Start, Highest wick, and Lowest wick review checkpoints.
Highest/lowest selection remains explicitly retrospective-only and cannot be
consumed by live inference, the candlestick shadow ledger, or execution.

The release manifest status is `aspect_evidence_trace_candidate` and records
all of those safety boundaries. MT5 remains read-only and app execution stays
locked.

## Verification

- Backend tests: 117 passed.
- Frontend tests: 71 passed across 22 files.
- Oxlint: passed.
- TypeScript/Vite production build: passed.
- Windows release packager PowerShell parse: passed.
- Native crash/recovery soak: passed every assertion with no deferred checks,
  no errors, execution locked, same-port sidecar recovery, and no descendant
  survivors:
  `D:\GannFinancialAstro\soak\tauri_0.10.19_20260722_082546\logs\native_soak_report.json`.
- Direct packaged-sidecar Trace request passed against 47 bundled USDJPY
  aspects. It returned the Trace contract, both retrospective extrema,
  timestamp-safe/no-lookahead guardrails, and all live/shadow/execution locks:
  `D:\GannFinancialAstro\smoke\trace_20260722_083233\packaged_trace_smoke.json`.
- Portable/sidecar shutdown left no descendant backend process.

The production build retains the existing advisory that the main minified UI
chunk exceeds 500 kB. PyInstaller also reports its existing optional
`pycparser.lextab` and `pycparser.yacctab` warnings; the frozen backend and
packaged API smoke both passed.

## Release Boundary

This is a versioned candidate, not an automatic promotion. The current stable
installation and the previous `0.10.18` candidate were not replaced. The NSIS
installer is not code-signed; the verified portable folder remains available
for direct evaluation and rollback.
