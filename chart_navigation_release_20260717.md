# Chart Navigation Release 0.10.5

Date: 2026-07-17 IST

## Scope

Gann Astro Desk now provides four compact chart navigation controls:

- move chart backward
- zoom out
- zoom in
- move chart forward

The dock is centered near the bottom of the chart. It is transparent and cannot
capture pointer input while the pointer is away, appears when the pointer enters
its proximity region, remains available for keyboard focus, and hides again when
pointer focus leaves.

## Deterministic Behavior

- Zoom is centered on the current logical range.
- Zoom in uses a `0.75` range factor; zoom out uses its reciprocal.
- Forward/backward moves use one quarter of the visible logical range.
- Navigation is clamped to available candles with two bars of left padding and
  five bars of right padding.
- At least eight bars remain visible.

The range calculations and proximity boundary are pure tested helpers in
`gann-astro-desk/src/chartViewport.ts`.

## Verification

- Frontend: 27 tests passed across 7 files.
- Backend: 78 tests passed.
- Oxlint passed.
- TypeScript and Vite production build passed. Vite retained only the existing
  advisory about a JavaScript chunk larger than 500 kB.
- Ruff passed.
- Python byte compilation passed.
- Browser QA verified hidden and visible opacity/pointer-event states, all four
  controls, zoom, quarter-range navigation, and pointer-leave hiding.
- Native Windows QA verified the same dock in the packaged Tauri application.
  Zoom and forward navigation visibly changed the candle viewport; moving the
  pointer to the title bar hid the dock again.
- Candidate native soak passed 28 checks with zero errors:
  `D:\GannFinancialAstro\soak\tauri_0.10.5_20260716_191936\logs\native_soak_report.json`.
- Promoted stable native soak passed 28 checks with zero errors:
  `D:\GannFinancialAstro\soak\tauri_0.10.5_20260716_193440\logs\native_soak_report.json`.

## Release

- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Executable SHA-256:
  `E93358F99276FF2E41068B520749C22A45D9B1D5C28A08F9B9FB796A7B08DF16`
- Installer SHA-256:
  `B556FDA10B8741EF91232A45116CA261410A6361938A035B6C35F4E0364073EC`
- Backend sidecar SHA-256:
  `2FC4035143D62EE8ED1B5D9AA1BBAD83EB33F246AF534B859FC046820D60D53E`
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.4_20260716T193054Z`
- Pre-promotion state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.5_promotion_20260716T193054Z`

MT5 remains read-only market data. Trade execution remains locked.
