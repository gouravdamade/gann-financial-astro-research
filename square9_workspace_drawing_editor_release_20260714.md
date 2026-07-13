# Square of Nine Workspace and Drawing Editor Release

Release date: 2026-07-14 IST  
Application: Gann Astro Desk 0.8.0

## Scope

- Replaced the Square of Nine candlestick overlay with an independent full-page workspace.
- Added price, time, date, and date-time modes; editable first value; signed increment;
  calendar/trading-time units; center-inclusive size; clockwise/counterclockwise number and
  angle rotation; angle offset; zoom; value lookup; selectable cells; semantic marks; notes;
  PNG export; and named-layout persistence.
- Added legacy migration: stored `square_of_nine` chart drawings are removed from chart
  rendering and converted to standalone Square of Nine settings when a layout is loaded.
- Added visible chart-object selection handles and numeric anchor editing for horizontal
  lines, vertical lines, and Gann fans. Unlocked anchors drag in market coordinates and
  commit once on release. `Delete`/`Backspace` deletes the selected drawing; `Escape`
  deselects it. The object panel also provides hide/show, lock/unlock, rename, style, anchor
  editing, templates, and an explicit Delete drawing command.

## GannZilla interaction research

The implementation uses original code but follows documented interaction concepts from the
official GannZilla material:

- [User guide](https://gannzilla.com/docs/): named chart persistence, selectable objects,
  deletion, marks, size, first value, increment, data type, and zoom.
- [Square of Nine](https://gannzilla.com/the-square-of-nine/): center-out spiral structure.
- [Gann wheel and pyramid](https://gannzilla.com/gann-wheel-gann-pyramid/): date-capable wheel
  use.
- [Gann scaling](https://gannzilla.com/gann-scaling/): explicit scale controls rather than
  treating screen pixels as market geometry.
- [Gann fan](https://gannzilla.com/gann-fan/): movable control-point interaction.

This is a research UI comparison, not validation of Gann forecasting claims.

## Persistence and safety

- Square settings and marks are stored under the existing `GANN_CHART_LAYOUT_V1` named
  layout contract.
- Chart drawings retain exact UTC-time/price anchors under
  `GANN_RESEARCH_CHART_DRAWING_V1`.
- Square of Nine and all manual drawings remain research-only:
  `consumedByLiveInference=false`, `consumedByShadowLedger=false`, and
  `executionAllowed=false`.
- Auto Suggest, the timestamp-safe live inference engine, the frozen shadow policy, and MT5
  execution policy were not changed.

## Verification

- `npm run lint`: passed.
- `npm test`: 4 files / 13 tests passed, including five standalone Square of Nine tests.
- `npm run build`: passed.
- `npm run test:backend`: 38 tests passed against the restored certified baseline dataset.
- `git diff --check`: passed before release documentation.
- Source browser QA: Gann fan origin drag moved while slope stayed fixed; keyboard deletion
  removed the selected fan; reload restored a clean layout; zero browser warnings/errors.
- Packaged QA in an isolated layout:
  - Square size changed from 7x7 to 9x9;
  - Date mode, -1 trading-day increment, a High mark, and note survived reload;
  - the temporary Square layout was deleted afterward;
  - a Gann fan was created, selected, resized by dragging one anchor, and deleted with the
    keyboard;
  - the temporary drawing layout was deleted afterward;
  - zero packaged browser warnings/errors.
- Packaged runtime: MetaQuotes-Demo connected, MT5 execution mode
  `read_only_market_data`, `tradeAllowed=false`; local Jyotish ready on `qwen2.5:3b`;
  shadow chain valid with 7 decisions, all pending abstains; frozen trial ID unchanged at
  `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`.

## Native release

- Executable: `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Version: `0.8.0`
- SHA-256: `9C81A85A6412D20721BDBEAA5922EA6E2C7E802091CDA8C42A7F4E1B0710CB48`
- Stable tree: 1,658 files / 708,955,644 bytes including the release manifest.
- Rollback archive: `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.7.0_20260714_000817`

