# Gann Astro Desk 0.7.0 - Chart Layout and Square of Nine Release Evidence

Date: 2026-07-13 IST

## Scope

This release adds durable, named chart layouts and a research-only Square of Nine drawing
tool to the native Windows application. Every persisted drawing uses market coordinates
(`timeUtc` and `price`), never screen pixels.

## Storage Contracts

- Layout contract: `GANN_CHART_LAYOUT_V1`
- Drawing contract: `GANN_RESEARCH_CHART_DRAWING_V1`
- Template contract: `GANN_DRAWING_TEMPLATE_V1`
- SQLite tables: `app_chart_layouts`, `app_chart_drawings`, and
  `app_drawing_templates`
- Layout writes are transactional and revisioned. A stale `expectedRevision` is rejected
  with an HTTP 409 response instead of overwriting newer work.
- Analysis layouts require a family key, so Analyze Aspect drawings are scoped to the
  selected family and survive recurrence navigation.
- Deleting a default layout promotes a deterministic replacement in the same workspace.
- Drawing identity is layout-scoped, so cloned layouts can safely contain independent
  copies of the same logical objects.

## User Workflow

- Automatic restore of the default layout for the selected workspace, symbol, timeframe,
  and family.
- Debounced autosave plus explicit Save and Save As.
- Named layout switch and delete.
- JSON export/import with contract validation and forced safety guardrails.
- Object tree with select, rename, hide/show, lock/unlock, delete, style controls, and
  locked-object-safe clear.
- Undo for the latest drawing mutation.
- Save, apply, and delete reusable drawing templates.
- Viewport range, aspect visibility, and SR visibility persist with the layout.

## Square of Nine Method

The research tool stores center value, increment, ring count, number and angle rotation,
angle offset, highlighted angles, cardinal/diagonal visibility, labels, and optional
price/time projections. Its persisted anchors define the data-space chart span.

The implemented level calculation uses square-root rotation:

`adjustedRoot = sqrt(center / increment) +/- angle / 180`

`value = adjustedRoot * adjustedRoot * increment`

This follows the documented GannZilla convention that a 360-degree rotation changes the
square root by 2, 180 degrees by 1, 90 degrees by 0.5, and 45 degrees by 0.25. Reference
pages used for the implementation:

- https://gannzilla.com/construction-of-square-of-nine/
- https://gannzilla.com/the-concept-of-rotation/
- https://gannzilla.com/creating-the-gann-square-of-9/
- https://gannzilla.com/navigating-the-gann-square-of-9/

The formula is implemented and tested as chart geometry. It is not certified as a trading
rule and is excluded from inference and execution.

## Safety Guardrails

Every stored or imported drawing is normalized to:

- `researchOnly=true`
- `consumedByLiveInference=false`
- `consumedByShadowLedger=false`
- `executionAllowed=false`

The native app remains read-only. MT5 order placement is disabled, manual geometry is not
an input to Auto Suggest, and the frozen shadow policy is unchanged.

## Interactive QA

Source-app QA verified:

- default layout creation and viewport autosave;
- horizontal-line save and reload restore;
- Square of Nine save with two distinct UTC time/price anchors;
- hide/show and lock/unlock autosave;
- clear preserves locked objects;
- Save As creates independent layout and drawing IDs;
- switching layouts restores each layout's own objects;
- template round trip;
- live undo;
- Analyze Aspect family layout persistence while moving from recurrence 7 to 8;
- no React warnings after the state-update fix.

Packaged native QA verified a Square of Nine drawing at two distinct data anchors, SQLite
persistence, reload restore, zero browser warnings, and all four safety guardrails. The QA
drawing was then cleared; the live app database contains one clean default USDJPY H1 layout
at revision 4 with zero drawings.

## Automated Verification

- Frontend lint: passed.
- Frontend Vitest: 3 files, 8 tests passed.
- Python backend suite: 38 tests passed.
- Focused chart-layout backend tests: 4 passed.
- Production TypeScript/Vite build: passed.
- Ruff on changed Python files: passed.
- `git diff --check`: passed.

The frontend tests cover Square of Nine rotation math and imported-layout guardrail
enforcement. Backend tests cover revision conflicts, defaults, cascade deletion,
layout-scoped drawing IDs, analysis-family validation, two-anchor validation, style
normalization, and templates.

## Native Release

- Version: `0.7.0`
- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- SHA-256:
  `C6863F64D4ACC4E55961A22052553B9177E55B8A1CA1BF818CA851AE37F60D8F`
- Stable tree: 1,658 files / 708,928,971 bytes including `release.manifest.json`
- Manifest payload: 1,657 packaged files / 708,928,408 bytes
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.6.1_20260713_190632`

The old stable parent directory remained held by a Windows directory handle. After
verifying the rollback archive hash, the verified 0.7.0 candidate contents were copied
into the existing stable directory and reverified by file count, byte count, executable
hash, and manifest.

## Packaged Runtime Snapshot

- MT5 connected to MetaQuotes-Demo in `read_only_market_data` mode;
  `tradeAllowed=false`.
- Local Jyotish ready on `qwen2.5:3b` with 4,565 corpus chunks;
  `analysisOnly=true`, `executionAllowed=false`.
- Prospective refresh current through the 2026-07-13 14:00 UTC H1 close.
- Frozen trial ID remains
  `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`.
- Shadow chain valid: 7 abstain decisions, 0 settled, 7 pending, no execution.
- First legal 72-hour settlement remains 2026-07-16 04:00 UTC.

## Remaining Research Gates

1. Keep collecting and settling the frozen prospective cohort without changing policy.
2. Externally certify Shadbala and Drik Bala calculations.
3. Validate Square of Nine, Gann fans, and other manual geometry out of sample before any
   proposal to expose them to inference.
4. Keep all order placement disabled unless a separate execution project is explicitly
   authorized and validated.
