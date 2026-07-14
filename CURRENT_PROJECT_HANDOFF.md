# Current Project Handoff

Last updated: 2026-07-14 09:17 IST

Use this file to recover context in a new chat if PyCharm/Codex chat history is lost.

## Latest Update - 2026-07-14 (Tauri 2 / Rust Native Shell)

- Promoted Gann Astro Desk `0.9.0`. The supported native shell is now Tauri 2 / Rust;
  PyWebView is retained only in the archived 0.8.0 rollback release.
- This is a compatibility migration, not an astrology-engine rewrite. React/TypeScript and
  Lightweight Charts remain the UI; the validated Python astrology, MT5, local Jyotish,
  corrected-data, refresh, and shadow-ledger engine runs as a managed headless sidecar.
- Added shared `runtime_support.py`, headless `backend_sidecar.py`, a sidecar-only PyInstaller
  spec, and D-drive reproducible Tauri build scripts. Rust owns random loopback ports,
  process startup, typed runtime discovery, child windows, and graceful sidecar shutdown.
- Sidecar contract: `GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1`. Frontend transport rejects an
  unknown contract, a non-private-loopback backend URL, or any runtime claiming execution
  permission. Browser/Vite development continues to use relative API routes.
- Installed the native build toolchain primarily on D::
  - Rust/Cargo 1.97 under `D:\Rust`;
  - Visual Studio Build Tools 2022 17.14.35 under `D:\VisualStudio`;
  - MSVC 19.44 and Windows SDK 10.0.26100 compiler/linker checks passed.
- Promoted release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - executable SHA-256
    `DCB4874CD3A6900597BC88A0817D467BD55EC3F1B5514FB95A2E72E06F73FE33`;
  - NSIS installer
    `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.9.0_x64-setup.exe`;
  - installer SHA-256
    `94C523AE64C81FAA7CAEF497DC845FA6A6BEC1037A8C7F5992F7862ADD8BDC2C`;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.8.0_20260714_091158`.
- Real-state verification preserved the frozen trial ID, valid seven-decision shadow chain,
  seven pending outcomes, MetaQuotes-Demo read-only connection, local Jyotish
  `qwen2.5:3b`, and every execution lock (`tradeAllowed=false`).
- Native visual QA covered the chart workspace, separate Analyze Aspect Tauri window, and
  standalone Square of Nine workspace. Closing the app terminated the managed sidecar with
  no orphan process.
- Verification: 113 Python tests, 15 Vitest tests, Oxlint, TypeScript/Vite, Ruff, source and
  packaged sidecar smoke tests, rustfmt, Cargo check, Clippy `-D warnings`, Tauri release
  build, NSIS bundle, live API contracts, native visual QA, and artifact hashes passed.
- Evidence: `tauri_hybrid_release_20260714.md`.
- Next recommended work:
  1. continue the frozen prospective trial without changing policy;
  2. code-sign the NSIS installer only after a signing identity is available;
  3. profile first and port Python bottlenecks to Rust one module at a time with fixture
     parity rather than rewriting validated doctrine logic wholesale;
  4. keep MT5 order placement outside this process and disabled.

## Previous Update - 2026-07-14 (Standalone Square of Nine + Editable Drawings)

- Promoted Gann Astro Desk `0.8.0`. Square of Nine is now a dedicated workspace tab,
  never a candlestick overlay. The market chart, aspect inspector, activity dock, and
  Square workspace are separate surfaces inside the same native application.
- The standalone Square supports price, time, date, and date-time values; editable first
  value; signed increment/decrement; minute/hour/day/week/month/trading-day units;
  center-inclusive size 1-15; independent number/angle direction; angle offset; zoom
  50%-150%; value or cell lookup; clickable High/Low/Forecast/Error marks; per-cell notes;
  PNG export; and named-layout persistence.
- Legacy `square_of_nine` chart drawings are filtered from candlestick rendering and
  migrated into standalone workspace settings on layout load. Autosave then persists the
  migrated form without leaving a stale overlay object.
- Horizontal lines, vertical lines, and Gann fans now have visible selected handles.
  Unlocked anchors can be dragged in UTC-time/price coordinates or edited numerically in
  the object panel. The panel also retains rename, hide/show, lock/unlock, color, width,
  line style, opacity, templates, and explicit Delete drawing controls. `Delete` or
  `Backspace` removes a selected unlocked object; `Escape` deselects it.
- Official GannZilla documentation was reviewed for interaction patterns: named chart
  persistence, selectable/deletable objects, Square size/first value/increment/data type,
  cell marking, zoom, and movable fan control points. The implementation is original and
  remains a research UI, not validation of Gann forecasting claims.
- Research safety is unchanged: Square of Nine and chart drawings are not consumed by Auto
  Suggest, timestamp-safe live inference, the shadow ledger, or execution. MT5 remains
  read-only with `tradeAllowed=false`; the frozen prospective policy/trial was not changed.
- Packaged QA used isolated temporary layouts and cleaned both afterward:
  - Square date mode, -1 trading-day increment, 9x9 size, a High mark, and a note survived
    reload;
  - a Gann fan was created, selected, resized by dragging its origin while its slope anchor
    stayed fixed, and deleted with the keyboard;
  - zero packaged browser warnings/errors; the user default layout and its two existing
    research drawings remain intact.
- Native release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - version `0.8.0`;
  - SHA-256 `9C81A85A6412D20721BDBEAA5922EA6E2C7E802091CDA8C42A7F4E1B0710CB48`;
  - stable tree 1,658 files / 708,955,644 bytes including the release manifest;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.7.0_20260714_000817`.
- Packaged runtime verification:
  - MetaQuotes-Demo connected in `read_only_market_data` mode;
  - local Jyotish ready on `qwen2.5:3b`;
  - shadow chain valid with 7 pending abstain decisions;
  - frozen trial ID unchanged at
    `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`.
- Verification: Oxlint, 13 Vitest tests, 38 backend tests, TypeScript/Vite production
  build, PyInstaller native build, source and packaged interaction QA, release
  hash/manifest/API checks, and `git diff --check` passed.
- Evidence is in `square9_workspace_drawing_editor_release_20260714.md`.
- Next recommended work:
  1. add optional Square templates and a print/export report only after real usage reveals
     which configurations recur;
  2. consider Gann wheel/pyramid variants as separate workspaces, not chart overlays;
  3. validate all manual Gann geometry out of sample before allowing any inference use;
  4. continue settling the frozen prospective cohort without changing its policy.

## Previous Update - 2026-07-13 (Named Layouts + Square of Nine Native Release)

- Promoted Gann Astro Desk `0.7.0` with durable named chart layouts. Layouts, drawings,
  templates, and viewport/layer state now use versioned SQLite contracts:
  `GANN_CHART_LAYOUT_V1`, `GANN_RESEARCH_CHART_DRAWING_V1`, and
  `GANN_DRAWING_TEMPLATE_V1`.
- Every drawing persists market coordinates (`timeUtc` + `price`) instead of screen
  pixels. Transactional writes use optimistic revisions; stale clients receive HTTP 409
  rather than overwriting newer work.
- Added default restore, debounced autosave, explicit Save, Save As, layout switch/delete,
  JSON export/import, undo, locked-object-safe clear, and reusable templates.
- Added a chart object tree with select, rename, hide/show, lock/unlock, delete, color,
  width, line style, and opacity controls. The same controller is used by the main chart
  and family-scoped Analyze Aspect workspace; drawings persist while navigating family
  repeatations.
- Added a Square of Nine research tool with center value, increment, rings, angle offset,
  clockwise/counterclockwise rotation, highlighted angles, cardinals/diagonals, labels,
  and optional price/time projections. The square-root rotation formula is unit-tested
  against the documented 45/90/180/360-degree increments.
- All stored and imported drawings are forcibly research-only:
  `consumedByLiveInference=false`, `consumedByShadowLedger=false`, and
  `executionAllowed=false`. Manual geometry does not change Auto Suggest or the frozen
  prospective policy.
- Interactive QA covered restore, Save As independence, lock/hide, clear, undo, templates,
  family recurrence navigation, and Square of Nine persistence. Packaged QA restored a
  data-anchored Square after reload with zero browser warnings, then removed the QA object;
  the live app database has one clean default USDJPY H1 layout with zero drawings.
- Native release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - version `0.7.0`;
  - SHA-256 `C6863F64D4ACC4E55961A22052553B9177E55B8A1CA1BF818CA851AE37F60D8F`;
  - stable tree 1,658 files / 708,928,971 bytes including the release manifest;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.6.1_20260713_190632`.
- Packaged runtime verification:
  - MT5 connected to MetaQuotes-Demo, read-only, `tradeAllowed=false`;
  - local Jyotish ready on `qwen2.5:3b` with 4,565 chunks, analysis-only;
  - refresh current through the 2026-07-13 14:00 UTC H1 close;
  - frozen trial ID unchanged at
    `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`;
  - shadow chain valid: 7 abstain decisions, 0 settled, 7 pending, execution false.
- Verification: frontend lint, 8 Vitest tests, 38 backend tests, 4 focused layout tests,
  production build, focused Ruff, packaged hash/manifest/API/DOM QA, and
  `git diff --check` passed.
- Evidence is in `chart_layout_square9_release_20260713.md`.
- Next recommended work:
  1. collect and settle the frozen prospective cohort without changing policy;
  2. externally certify Shadbala/Drik calculations;
  3. validate Square of Nine and other manual Gann geometry out of sample before allowing
     any inference use;
  4. keep order placement disabled unless a separate execution project is explicitly
     authorized and validated.

## Previous Update - 2026-07-13 (Frozen Prospective Trial Manifest)

- Promoted Gann Astro Desk to native release `0.6.1` and froze the existing
  prospective shadow sample under `GANN_FROZEN_PROSPECTIVE_SHADOW_TRIAL_V1`.
  Its trial ID is
  `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`.
- Added immutable SQLite manifest `app_shadow_trial_manifest` with UPDATE and DELETE
  guards. The first coherent cohort locks the ledger/decision/packet/outcome contracts,
  engine, policy, Raman astronomy contract, symbol, timeframe, 72-hour horizon, and
  statistical gate configuration. Later mismatches are rejected before ledger append.
- The seven pre-manifest decisions were migrated once through
  `existing_decision_backfill_v1`; all resolve to one valid cohort without rewriting the
  append-only decision chain. New decisions embed the same `trialIdentity` in their payload.
- The predeclared gate remains unchanged: 100 settled watch clusters, at least 10% watch
  coverage, Wilson 95% lower bound above 50%, exact two-sided binomial p-value below 0.05,
  positive mean signed 72-hour return, and at least four UTC calendar months. Execution is
  still locked regardless of gate status.
- Shadow Validation now displays the frozen trial fingerprint, engine/policy, integrity,
  `0 / 100` watch-cluster progress, `0 / 4` calendar-month progress, and next real 72-hour
  settlement. Live packaged state at verification:
  - chain valid; 7 decisions, all abstain; 0 settled and 7 pending;
  - first legal settlement `2026-07-16T04:00:00+00:00`; no outcomes currently due;
  - latest verified closed MT5 H1 bar `2026-07-13T10:00:00+00:00`;
  - active corrected artifact `tn_46ffe4254d23445c96cc220d2038202c`;
  - MT5 connected, `tradeAllowed=false`; shadow execution false;
  - local Jyotish ready on `qwen2.5:3b`.
- Split trial identity and summary logic into `gann-astro-desk/backend/shadow_trial.py`
  so the append-only ledger no longer owns a duplicate trial-policy implementation.
- Native release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - version `0.6.1`;
  - SHA-256 `772905ED308F58B46CAE7910ED8314DCA7D6B1DCE9877AE3478A46DE42DFD7DC`;
  - 1,657 files / 708,779,331 bytes;
  - release manifest now stores the portable relative executable name;
  - prior `0.6.0` archived under
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.6.0_20260713_154140`.
- Verification:
  - full Python suite: 109 passed;
  - focused shadow/refresh tests: 12 passed;
  - frontend Vitest: 5 passed;
  - Ruff, Oxlint, TypeScript/Vite, PyInstaller, release hash, packaged APIs, live database
    migration, packaged visual/DOM QA, browser console, and `git diff --check`: passed.
- Evidence is in `prospective_shadow_trial_manifest_20260713.md`.
- Chart-persistence audit: SQLite already preserves event-linked annotation pins, notes,
  and their chart state, but manual horizontal/vertical lines and Gann fans are still local
  React state and disappear after restart. The next drawing release should therefore add
  named layouts/autosave and versioned drawing storage before adding Square of Nine.
- Next recommended work:
  1. add named chart layouts, autosave, drawing templates, object tree, lock/hide, and
     JSON import/export so all manual drawings restore exactly;
  2. add a data-anchored Square of Nine research tool with center value, increment, rings,
     rotation direction, angle highlights, price/time projections, and persisted settings;
  3. keep Square of Nine and manual geometry outside live inference until separately tested;
  4. settle the frozen cohort only after each real 72-hour horizon and continue chain audits;
  5. externally certify Shadbala/Drik doctrine calculations.

## Previous Update - 2026-07-13 (TradingView-Style Terminal + First Live Refresh Audit)

- Promoted Gann Astro Desk to native release `0.6.0` with a chart-first graphite market
  terminal: compact command bar, fixed OHLC readout, TradingView-style drawing rail with
  undo, chart focus mode, collapsible aspect inspector and activity dock, layer controls,
  live read-only status bar, chart PNG command, and responsive desktop behavior.
- Added an always-visible `Auto refresh` control. It displays the closed-bar supervisor
  state and can request the existing guarded check immediately; it cannot bypass freshness,
  close finalization, immutable snapshot promotion, corrected-artifact verification, or the
  execution lock. A manual packaged-UI check created no duplicate; later runs began only
  when the 06:00 and 07:00 UTC bars became eligible.
- Panel and layer preferences now persist through `schema_meta.workspace_preferences_v1`
  instead of depending on a random private loopback origin. `GET/PUT
  /api/workspace-preferences` supports partial updates, accepts only JSON booleans, and
  explicitly closes its SQLite handles.
- Audited the first seven real automatic H1 cycles, closed at 01:00 through 07:00 UTC on
  2026-07-13. All completed successfully and activated distinct corrected artifacts. The
  latest active artifact is `tn_53277139e4354e54bbff9a28e5b2b12c` with 39 events and 17
  touches through the 07:00 UTC closed bar.
- A 98-check lineage audit passed across snapshot manifest/parquet hashes, promoted-source
  identity, run/artifact cutoff identity, artifact price provenance, event/touch hashes and
  counts, outcome-label exclusion, refresh run identity, and execution lock. Evidence is in
  `prospective_refresh_live_audit_20260713.md`.
- The audit found one recordkeeping-only issue: four completed run rows retained inherited
  prior-artifact provenance even though their generated artifacts were correct. The
  supervisor now writes current source provenance before queueing, replaces completed run
  parameters with verified artifact parameters, and performs a guarded startup repair only
  when artifact ID, refresh run ID, source close, and price-source ID all agree. All five
  existing rows are now reconciled, and later runs were written correctly at completion.
- Packaged runtime checks:
  - MT5 connected; `tradeAllowed=false`;
  - refresh `up_to_date` at `2026-07-13T07:00:00+00:00`;
  - append-only shadow chain valid with 7 decisions and outcomes still pending;
  - local Jyotish ready on `qwen2.5:3b`;
  - layout preferences persisted and were restored to inspector/dock/aspects/SR visible;
  - packaged focus, restore, aspect, SR, and Auto Refresh controls passed browser checks.
- Native release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - version `0.6.0`;
  - SHA-256 `59AAC283334B5045DF7909A4CE21DE20D09864F7B71ACCCC32D98A8299921D12`;
  - 1,657 files / 708,767,866 bytes;
  - application remains analysis/read-only and is running for continued prospective capture.
- Verification:
  - full Python suite: 107 passed;
  - frontend Vitest: 5 passed;
  - focused refresh, shadow, and preference API tests: 12 passed;
  - Ruff, Oxlint, TypeScript/Vite production build, PyInstaller packaging, release hash,
    packaged APIs, source visual QA, packaged DOM/control QA, and `git diff --check`: passed.
- Next work:
  1. collect the frozen prospective shadow sample without changing policy thresholds;
  2. settle outcomes only after their real 72-hour horizon and continue chain audits;
  3. externally certify Shadbala/Drik doctrine calculations;
  4. keep all order placement disabled unless a later validated execution project is
     separately and explicitly authorized.

## Previous Update - 2026-07-13 (Automatic Prospective Refresh + Local Jyotish)

- Added `gann-astro-desk/backend/prospective_refresh.py` with contract
  `GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1`. The background supervisor polls MT5, accepts only
  a recent fully closed M30/H1 source bar after a finalization grace period, captures an
  immutable closed-bar snapshot, promotes it through the existing SHA-256 price-source
  contract, queues the corrected Raman TN generator, activates only its verified completed
  artifact, and then wakes the append-only shadow ledger.
- Refresh runs are durable and idempotent by source-bar close time in
  `app_prospective_refresh_runs`. Restarted pre-queue work is failed honestly, active
  generation jobs are reconciled, simultaneous user generation is respected, and a manual
  `Refresh source` request only wakes the same safety checks; it cannot bypass freshness.
- Corrected artifact parameters now carry `priceSourceLastBarCloseUtc`. Shadow freshness uses
  the actual last closed market bar instead of the file-capture timestamp, preventing a
  weekend snapshot from making stale market data appear fresh.
- Current packaged state is intentionally `market_stale`: latest MT5 H1 close is
  2026-07-11 00:00 UTC, so no refresh run, artifact, or ledger decision was fabricated.
  The worker will resume automatically after a genuinely fresh closed bar arrives.
- Added `gann-astro-desk/backend/local_jyotish.py` and a native `Local Jyotish` Analyze
  Aspect tab. The app starts the portable Ollama runtime from `D:\Ollama` when needed and
  packages `jyotish_agent/corpus_chunks.jsonl` without duplicating model weights.
- Local contract `GANN_LOCAL_JYOTISH_RAG_DRAFT_V1` uses the selected occurrence's
  deterministic context plus 4,565 local chunks. Retrieval policy
  `balanced_classical_commentary_same_family_v2` separates 3,787 classical-doctrine chunks,
  761 secondary/user-reference chunks, and 17 local-research chunks; local notes are admitted
  only when they match the selected family.
- Every local draft is visibly untrusted, includes retrieved citations and a deterministic
  post-draft verifier, and declares that it is not official, not consumed by live inference,
  not consumed by the shadow ledger, and cannot execute. A real no-evidence occurrence test
  made Qwen decline to invent strength/SR conclusions and the verifier correctly required
  review when the model omitted inline citation ids.
- The app defaults to `qwen2.5:3b`. `gemma4:12b` is installed but its 11.9B Q4 runtime failed
  to load reliably after partial GTX 1060 offload, so it is not presented as the working
  default. Model fallback remains supported.
- Added APIs:
  - `GET /api/prospective-refresh` and `POST /api/prospective-refresh/run`;
  - `GET /api/local-jyotish/health` and `POST /api/local-jyotish/analyze`;
  - `/api/shadow-ledger` now includes refresh state for the native dock.
- Native release promoted to `0.5.0`:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `343FF5C9AC1F62A1CD2B866D4974942CA6D6A8A5B8B1C8A13084973E76C481C4`;
  - 1,657 files / 708,788,848 bytes;
  - packaged corpus: 10,331,989 bytes;
  - astronomy contract unchanged; MT5 and both AI surfaces remain analysis/read-only.
- Verification:
  - full Python suite: 104 passed;
  - native backend suite: 29 passed, including 7 refresh/local-Jyotish tests;
  - frontend Vitest: 5 passed;
  - Ruff, Oxlint, TypeScript/Vite production build, `git diff --check`, native packaging,
    source UI, packaged APIs, packaged UI, and browser logs: passed;
  - packaged API confirmed `tradeAllowed=false`, refresh/ledger execution false, valid empty
    chain, zero refresh runs during stale market, local model ready, and balanced layer counts.
- Next work:
  1. leave the app running through the next fresh market H1 close and audit the first real
     snapshot -> promotion -> corrected artifact -> shadow capture lineage end to end;
  2. collect the frozen prospective sample without changing policy or gate thresholds;
  3. externally certify Shadbala/Drik doctrine calculations;
  4. keep all order placement disabled unless a later validated execution project is
     separately and explicitly authorized.

## Previous Update - 2026-07-13 (Append-Only Prospective Shadow Ledger)

- Added `gann-astro-desk/backend/shadow_ledger.py` with the contracts
  `GANN_APPEND_ONLY_SHADOW_LEDGER_V1`, `GANN_PROSPECTIVE_SHADOW_DECISION_V1`,
  and `GANN_PROSPECTIVE_72H_OUTCOME_V1`. The ledger records watch and abstain
  decisions prospectively from server UTC and live read-only MT5 bars; the client cannot
  provide a historical decision time, and the retrospective baseline is explicitly blocked.
- Prospective capture requires a non-built-in generated artifact with complete creation and
  source-as-of provenance, a price snapshot no older than one source timeframe plus 15
  minutes, a just-closed touch within that same freshness window, and source data containing
  the signal bar. Stale or baseline artifacts are reported honestly and cannot be backfilled.
- Added append-only SQLite table `app_shadow_ledger_entries`. Decisions and 72-hour outcomes
  are separate immutable entries with contiguous sequence numbers, canonical payload hashes,
  previous-entry hashes, and a verified SHA-256 chain. Database triggers reject UPDATE and
  DELETE. A 72-hour outcome is appended only after the first fully closed MT5 bar at or after
  the frozen anchor plus 72 hours.
- The shadow supervisor scans every 30 seconds by default, settles mature outcomes, and is
  idempotent across restarts. It never emits an order, fill, entry/exit price, transaction
  cost, or retrospective P/L. Simultaneous event decisions are clustered before statistics
  so overlapping events do not inflate the sample.
- The predeclared prospective gate requires at least 100 watch clusters, at least 10% watch
  coverage, Wilson 95% lower bound above 50%, exact two-sided binomial p-value below 0.05,
  positive mean signed 72-hour return, and at least four UTC calendar months. Execution
  remains locked even if those research criteria eventually pass.
- Added native APIs `GET /api/shadow-ledger` and `POST /api/shadow-ledger/scan`, plus a dense
  desktop `Shadow validation` panel showing chain state, immutable counts, pending outcomes,
  hit rate, gate progress, execution lock, readiness, and the decision/outcome trail.
- Corrected the historical evaluator's 72-hour label availability: `after72_time_local` is
  the target bar's open timestamp, so the label becomes usable only when that bar closes.
  The report was regenerated; frozen metrics remain 258 watches, 140 hits, 54.26%, Wilson
  48.17%-60.24%, and p=0.190975, so the historical statistical gate still fails.
- Native release promoted to `0.4.0`:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `89D51514AFD96B3FD0B995CE354FB7F3231C156396E019850D39825F4DA865AF`;
  - 1,656 files / 698,374,484 bytes;
  - astronomy contract unchanged and MT5 remains `read_only_market_data`.
- Verification:
  - full Python suite: 97 passed;
  - native backend suite: 22 passed, including 5 focused shadow-ledger tests;
  - frontend Vitest: 5 passed;
  - Ruff, Oxlint, TypeScript/Vite production build, `git diff --check`, native packaging,
    packaged API, and packaged visual QA: passed;
  - packaged manual scan left the chain valid with zero entries and reported
    `artifact_price_snapshot_stale`; browser warnings/errors were empty.
- Current operational state: the active July research artifact is too old for prospective
  capture, so the ledger correctly starts at zero. Do not loosen freshness or backfill it.
- Next work:
  1. add an automatic just-closed MT5 snapshot, promote, and corrected-artifact refresh
     pipeline so fresh eligible touches can enter the prospective ledger unattended;
  2. collect the frozen prospective sample without changing policy thresholds mid-run;
  3. externally certify Shadbala/Drik doctrine calculations;
  4. keep all order placement disabled unless a later validated execution project is
     separately and explicitly authorized.

## Previous Update - 2026-07-13 (Purged Timestamp-Safe Policy Validation)

- Corrected a chronology defect in native `Analyze Aspect`: a selected historical touch now
  becomes eligible at the close of its source candle, while event end remains the eligibility
  deadline. The previous `max(event_end, touch_close)` display cutoff could move inference
  beyond the 72-hour outcome label for long aspects even though the shared engine itself did
  not require event end.
- Added `evaluate_timestamp_safe_decisions.py`, a frozen purged/embargoed evaluator that calls
  the real `decision_engine.live_inference_packet` for every retained SR touch. It excludes
  forbidden future/outcome fields, quarantines labels already available at decision time,
  prevents identical decision timestamps from crossing folds, clusters simultaneous events
  into one market decision, and admits training labels only after the full 72-hour outcome
  horizon plus a 72-hour embargo.
- Added `test_evaluate_timestamp_safe_decisions.py`. Its tests cover touch-close timing,
  label-availability purging, embargoed history, equal-time fold boundaries, simultaneous
  decision clustering, future-label packet invariance, and already-known-label quarantine.
- Frozen baseline result is recorded in `timestamp_safe_decision_walk_forward_20260713.md`:
  - 754 source touches; 753 timestamp-valid packets; 1 quarantined flat label;
  - 355 unique out-of-sample decision clusters; 258 watches and 97 abstentions;
  - 140/258 correct = 54.26% hit rate, with Wilson 95% interval 48.17%-60.24%;
  - exact two-sided p-value versus 50% = 0.191;
  - balanced direction accuracy 55.91%; training-majority baseline 43.41%;
  - mean signed 72-hour return +0.0276% before costs, but only 3/5 folds were positive.
- The predeclared statistical gate therefore **failed**: the confidence interval crosses 50%,
  p-value is not below 0.05, and the positive-fold requirement was not met. These results are
  descriptive historical evidence only, not a trading certificate.
- Engine version is now `timestamp_safe_auto_suggest_v1_1_20260713`. Every live packet exposes
  `failed_retrospective_statistical_gate_20260713`, links the tracked validation report, requires
  prospective validation, and keeps execution disabled. Analyze Aspect visibly shows
  `Historical gate failed` and remains a research-watch surface.
- Native release promoted to `0.3.1`:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `0517656542BE12D8BECF7E6EE2E4DCD2C2991FFCE0D234AAB19E9514D7693308`;
  - 1,656 files / 698,340,280 bytes;
  - MT5 remains `read_only_market_data`.
- Verification:
  - full Python suite: 92 passed;
  - native backend suite: 17 passed;
  - frontend Vitest: 5 passed;
  - Ruff, Oxlint, TypeScript/Vite production build, packaged visual QA, and packaged API: passed;
  - packaged API confirmed touch-close decision time equals source-data maximum, no-lookahead
    true, execution false, failed-gate lock present; the July 2026 active artifact was restored
    after the reversible baseline smoke test.
- Next gates:
  1. run a prospective, append-only shadow-decision ledger before reconsidering the policy;
  2. externally certify Shadbala/Drik doctrine calculations;
  3. if the shadow sample is adequate, evaluate the same frozen metrics with spread/slippage;
  4. do not add MT5 order placement unless a later validated execution project is explicitly
     authorized.

## Previous Update - 2026-07-13 (Unified Timestamp-Safe Decision Engine)

- Added root `decision_engine.py` with the shared packet contract
  `GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1`, engine version
  `timestamp_safe_auto_suggest_v1_20260712`, and two explicit modes:
  `research_replay` and `live_inference`.
- Retrospective `reviewer_rule_replay.auto_suggest_case` still performs the existing
  completed-chart marker replay, but now returns the shared packet and declares its
  known-outcome/future-price-path use. Replay packets are always timestamp-unsafe,
  no-lookahead false, outcome-consumed, future-prices-consumed, and live-ineligible.
- Browser Auto Suggest remains executable only through `POST /api/auto_suggest` and the
  Python replay engine. The archived JavaScript decision body is unwired and now throws
  immediately if called, preventing a second executable policy from drifting silently.
- Added native `POST /api/decisions`, which accepts `live_inference` only. Research replay
  requests are rejected. Live decisions use only a closed selected-touch candle, closed
  price evidence through the decision cutoff, and an explicit feature allowlist. The
  repository physically loads only the safe scorer/context fields; outcome labels, future
  returns, edge scores, MFE/MAE, P/L, special traits and rule lessons are not loaded into the
  native inference row.
- Live policy `fx_doctrine_consensus_watch_only_v1` emits `WATCH_LONG`, `WATCH_SHORT`, or
  `ABSTAIN` only when the raw and doctrine USD-minus-JPY hypotheses agree. It never creates
  an entry price/time, exit price/time, P/L, outcome, or MT5 order. Execution remains locked.
- Timestamp rules are explicit: the touch must lie inside its event window; the touch bar
  must close before it becomes evidence; and one source-timeframe of post-window grace is
  allowed only so the final overlapping bar can close. Packet validation rejects future
  price evidence, outcome/fill/exit injection, unavailable watch signals, and watches outside
  the decision deadline.
- Analyze Aspect now shows a dedicated `Timestamp-safe inference` panel with action/reason,
  decision cutoff, signal-availability time, closed-evidence time, packet ID, evidence, and
  visible `timestamp safe`, `no lookahead`, `outcome excluded`, and `execution locked` badges.
  Its historical inspection cutoff is the later of event end or the selected touch-bar close.
- Real retained July artifact smoke (`tn_2beda5f38c4f4cc2bb866fa88c174bf2`): all 12 touch
  events were processed by the packaged endpoint; 5 produced provisional `WATCH_SHORT` and
  7 abstained because raw/doctrine evidence was unknown or conflicted. No live packet carried
  an outcome or execution permission. Packaged visual QA on `TN::MERCURY->MARS::trine`
  displayed `WATCH SHORT` cleanly and browser logs contained no warnings/errors.
- Native release promoted to `0.3.0`:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `6C22ECE1038A98FCE3B46FFBCC6E1C0E5047BB1AB702B2E18CED591E5AD5557B`;
  - 1,656 files / 698,339,468 bytes;
  - astronomy contract remains `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`;
  - MT5 execution mode remains `read_only_market_data`.
- Verification:
  - full Python suite: 86 passed;
  - native backend suite: 17 passed;
  - frontend Vitest: 5 passed;
  - Oxlint, TypeScript/Vite build, `git diff --check`, packaged API, and packaged UI: passed.
- Remaining deliberate gates:
  1. run purged/embargoed out-of-sample evaluation of timestamp-safe packets before changing
     watch-only status;
  2. externally certify Shadbala/Drik calculations before treating astrology doctrine as
     production evidence;
  3. migrate retrospective P/L, rule lessons, Dream Review, and official-note processing into
     typed research-only contracts without exposing them to live inference;
  4. physically delete the now-disabled JavaScript archive after any final historical parity
     work; it is not executable now;
  5. MT5 order placement stays disabled until the user separately authorizes an execution
     project after validation.

## Previous Update - 2026-07-12 (Durable Corrected-Data Generation)

2026-07-12 third Windows-app vertical slice:

- Added a durable corrected transit-to-natal generation queue. Jobs are persisted in
  SQLite, run in isolated hidden subprocesses, report honest stage/progress state, support
  cancellation, resume queued work after restart, and mark interrupted running work failed
  instead of pretending it completed.
- Added a versioned corrected-data artifact registry under
  `D:\GannFinancialAstro\app_artifacts`. Every completed artifact has inspectable generator
  logs, canonical SR inputs, a manifest, SHA-256 hashes, astronomy-contract validation, and
  event/touch row counts before it can be registered or activated.
- Added schema-version-4 tables `app_generation_jobs` and `app_data_artifacts`, plus backend
  APIs to create/list/cancel jobs, list artifacts, and activate either a generated artifact
  or the versioned baseline. Dataset activation swaps event/touch indexes atomically under a
  repository lock; invalid or partial artifacts never replace the working chart source.
- Extended the corrected generators so custom SR configuration is canonical JSON, reference
  times accept seconds, fixed-offset locations are parsed correctly, and a valid empty touch
  artifact can be emitted when an event source has no SR touch.
- Added the parameter-drawer generation workspace with Generate, Cancel, job progress/error,
  artifact history, and activation controls. A research-mode watcher refreshes the chart and
  Analyze Aspect data when a completed job auto-activates, even if the drawer was closed.
- Corrected touch-only filtering to use the explicit event-to-touch join and retained the
  generated deterministic astro fields for Analyze Aspect evidence instead of reducing touch
  rows to plotting coordinates.
- End-to-end proof generation produced `1` corrected event and `1` SR touch; the activated
  artifact exposed `22` deterministic evidence fields in event detail. The same artifact was
  exercised through the real HTTP queue and browser UI, then the versioned baseline was
  restored and all proof rows/directories were removed.
- Verification completed:
  - backend unittest: 11 passed;
  - frontend Vitest: 5 passed;
  - Python compile, Oxlint, and production TypeScript/Vite build: passed;
  - browser check: nonblank generated chart, visible 100% completed job, correct artifact
    counts, clean baseline restoration, and no browser-console errors or warnings.
- Remaining app work, in order:
  1. add a timestamped MT5 history snapshot/ingestion step so corrected TN generation can
     cover dates after the current versioned source endpoint of 2026-03-10;
  2. migrate deterministic Auto Suggest, trade markers, P/L, rule lessons, Dream Review,
     and the official-note queue into shared app/backend contracts;
  3. consolidate browser and Python decision logic into one timestamp-safe no-lookahead engine;
  4. implement and certify the corrected transit-to-transit generator;
  5. freeze/sign Python and Node sidecars and complete native packaging after Rust/MSVC is
     installed on `D:`.

## Previous Update - 2026-07-12 (Parameterized Charts and Live MT5)

2026-07-12 second Windows-app vertical slice:

- Added a typed parameter contract and persistent SQLite parameter profiles for symbol,
  research/live source, timeframe, date range, transit-to-natal body filters, aspects,
  excluded families, touch linkage, duration, harmonics, n values, degrees, SR tolerances,
  and birth/IPO reference metadata.
- Added a responsive parameter drawer with saved profile create/load/delete, explicit
  `rebuild input` labels for settings that require a new corrected source, and a disabled
  transit-to-transit option until a corrected TT generator exists. Applying parameters never
  silently claims to regenerate ephemeris data.
- Historical chart loading now supports M30, H1, H4, and D1. M30 and H1 use versioned MT5
  parquet sources; H4 and D1 are deterministically resampled from H1. Existing corrected TN
  events can be filtered by transit body, natal body, aspect, family, touch linkage, and
  duration without changing their astronomical identities.
- Added read-only MT5 bar retrieval for M30/H1/H4/D1 and a five-second live chart refresh.
  Live updates replace series data in place so zoom and pan state are not reset. The gateway
  remains market-data only: `tradeAllowed=false`; no order method exists.
- The live backend smoke check connected to `MetaQuotes-Demo` and returned 120 USDJPY H1 bars.
  Current Jul-2026 live bars have no corrected aspect overlays because the versioned TN source
  ends on 2026-03-10; future/upcoming corrected event generation is still required.
- Updated the app database to schema version 3 with `app_parameter_profiles`. The profile API
  create/list/delete smoke test passed and left no test profile behind.
- Verification completed:
  - frontend Vitest: 5 passed;
  - backend unittest: 8 passed;
  - Oxlint: passed;
  - production TypeScript/Vite build: passed;
  - browser checks: nonblank historical M30 chart, corrected event/body filters, saved drawer
    state, nonblank MT5 live chart, and no post-refactor browser-console errors.
- Remaining app work, in order:
  1. add a background corrected-TN generation queue, progress/cancel states, artifact registry,
     and atomic loading of generated datasets into the chart and Analyze Aspect workspace;
  2. extend corrected event generation into the current/future live date range;
  3. migrate deterministic Auto Suggest, trade markers, P/L, rule lessons, Dream Review,
     and official-note queue into shared app/backend contracts;
  4. consolidate browser and Python decision logic into one timestamp-safe no-lookahead engine;
  5. complete native sidecar packaging after the Rust/MSVC toolchain gate is installed on `D:`.

## Previous Update - 2026-07-11 (Gann Astro Desk)

2026-07-11 first Windows-app vertical slice:

- Added `gann-astro-desk`, a Tauri-ready React/TypeScript desktop surface with a quiet
  chart-first operational design. The supported runtime is currently Vite at
  `http://127.0.0.1:5173`; native installer packaging is not yet complete.
- Main workspace uses real corrected data:
  - 1,268 directional Raman transit-to-natal events from
    `astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet`;
  - USDJPY H1 candles from the versioned MT5 parquet source;
  - 754 corrected planetary SR touches explicitly joined from
    `aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv`.
- Added clickable aspect windows and a detachable `Analyze Aspect` family window with:
  - all previous occurrences, filters, previous/next navigation, outcome summaries,
    deterministic astro evidence, and persistent reviewed/pending progress;
  - chart tools for horizontal/vertical lines, two-anchor Gann fans, reset, and clear;
  - structured chart annotations persisted with exact time, price, event, family,
    selected target, note, and chart state.
- Added read-only MT5 supervisor with heartbeat/reconnect. Live smoke check connected to
  `MetaQuotes-Demo` and returned a current USDJPY bid/ask; `tradeAllowed=false` and
  `executionMode=read_only_market_data` are enforced.
- Added a local `@openai/codex-sdk` bridge for family-scoped Codex analysis. Each question
  receives deterministic case context, the selected annotation, and a local chart PNG.
  It has no MT5 order capability and does not promote LLM prose to official evidence.
  Bridge health passed; a real reply was blocked by the local Codex usage limit until its
  stated reset time, and the UI reports that error rather than fabricating a response.
- Updated `gann_aspect_annotations_raman_v2.sqlite` to app schema version 2 with empty,
  non-destructive `chart_annotations`, `app_occurrence_progress`, and
  `app_codex_threads` tables. New app progress remains separate from legacy completed reviews.
- Added a Tauri 2 shell/config under `gann-astro-desk/src-tauri`. `npx tauri info` parses
  the app, but confirms Rust/Cargo and Microsoft C++ build tools are absent. Install them
  on `D:` and freeze/sign the Python and Node services as sidecars before producing an installer.
- Verification completed:
  - frontend production build: passed;
  - Oxlint: passed;
  - Vitest: 2 passed;
  - backend unittest: 4 passed;
  - Python compile and Node syntax checks: passed;
  - live browser checks: nonblank main chart, SR lines, family recurrence window,
    review persistence, annotation create/delete, and embedded Codex panel all passed;
  - browser console: no errors or warnings.
- Remaining app work, in order:
  1. implement the parameter editor and generation jobs for symbol, date range, timeframe,
     n/f/degree, birth/IPO chart, location, planets, aspects, pair exclusions, and TT/TN mode;
  2. merge live MT5 candle/tick updates into the displayed series (current MT5 connection is
     supervised, while chart history remains the versioned parquet snapshot);
  3. migrate deterministic Auto Suggest, trade markers, P/L, rule lessons, Dream Review,
     and official-note queue into shared app/backend contracts;
  4. consolidate browser and Python decision logic into one no-lookahead engine;
  5. package the Python backend and Codex bridge as signed Tauri sidecars, then build the
     Windows installer after the `D:`-hosted Rust/MSVC gate is satisfied.

## Previous Update - 2026-07-11

2026-07-11 end-to-end financial astrology code/data/doctrine audit:

- Added `end_to_end_financial_astro_audit_20260711.md`. Read it before any rebuild, review,
  RAG refresh, demo order, or new rule. The headline is important:
  - the legacy USDJPY natal-event source used a double sidereal adjustment for the 1889 reference
    chart and tropical houses beside sidereal planets;
  - its logger also sorted body labels, losing transit/natal orientation;
  - therefore the current event/touch/case database and reviewed case IDs are preserved as
    `legacy_double_sidereal_research_history`, not valid live/ML ground truth.
- Added canonical `financial_astro_ephemeris.py` and `astro_event_contract.py`:
  - Raman Swiss-Ephemeris positions are sidereal exactly once;
  - true node/Ketu and sidereal Porphyry cusps are explicit;
  - longitude caches use a full timestamp-index digest;
  - all new events carry `event_scope`, transit/natal bodies, astronomy contract version, and
    geometry status.
- Corrected a source proof run:
  - a March TN rebuild produced 16 events, maximum inferred orb `0.349` degrees;
  - a corrected touch proof produced 14 rows, maximum orb `0.263` degrees;
  - old `AVG(ALL)|MOON square` reviews do not map to the corrected event identities.
- The active SR chart/log builders (`sr_touch_lazy_dashboard.py`, `sr_lazy_reactive_dashboard.py`,
  `build_pair_aspect_market_log.py`, `build_sr_anchor_reversal_log.py`,
  `generate_sr_candidate_chart_pack.py`) now use exact canonical longitude series instead of
  external JDML/adaptive forward-filled ephemeris series.
- RAG now quarantines rule notes and touch rows without a supported
  `RAMAN_SWISSEPH_SINGLE_SIDEREAL_*` contract, so legacy case prose cannot return as evidence.
- Updated strict-Shadbala labeling/logic to source-aligned provisional V4. Fixed Drekkana,
  Moon Paksha, Sun Ayana, and luminary Chesta handling; full Kaala/Chesta/Yuddha remains pending
  external certification and must not be called fully strict/certified.
- Walk-forward evaluator now uses a real outcome-horizon embargo, training-slice-only feature
  selection, and excludes same-bar entry/touch leakage. It remains exploratory due to small,
  high-dimensional data.
- `generate_upcoming_aspects.py` has scoped TT family keys and does not implicitly transfer old TN
  family learning. `reviewer_rule_replay.py` protects completed ignored cases.
- Certification now defaults to `astro_certification_4_gate_v2_20260711`; Gate 4 is deliberately
  `blocked_legacy_dataset` unless an explicit historical archive replay is requested.
- Added `requirements.txt`, `requirements-dev.txt`, `pytest.ini`, regression tests, and historical
  banners on older May reports. Deleted the six-line `sr_touch_lazy_dashboard_restored.py` stub.
- Verification completed:
  - `python -m pytest`: 53 passed;
  - canonical Python compile: passed;
  - Ruff: passed;
  - `git diff --check`: passed (line-ending warnings only).
- Next non-negotiable work, in order:
  1. freeze/backup old SQLite and source data as legacy history;
  2. replace or vendor the remaining recovery-only external `JDML4.py` source generator;
  3. rebuild full corrected TN event/touch/candidate data under a new versioned DB namespace;
  4. re-review or explicitly migrate observations without copying old astronomical labels;
  5. consolidate browser/Python Auto Suggest into one deterministic engine;
  6. build a timestamp-safe live policy only after purged out-of-sample validation.

## Previous Update - 2026-07-11

2026-07-11 BPHS and Phaladeepika provenance-aware corpus ingestion:

- Ingested `BPHS`, an 1899 Mumbai Sanskrit-Hindi `Brihat Parashara Hora Shastra` Purva/Uttara witness:
  - 745 PDF/OCR pages retained;
  - PDF SHA-256 `BB556804D8D546ACC39C43A22CECDBE2C29E3A7BA157E60EEC810C478EB645A4`;
  - explicitly labeled recension-specific rather than merged with modern 97-chapter English editions;
  - English doctrinal claims require an identified translation or human verification.
- Ingested `PHALADEEPIKA`, Mantreswara with V. Subrahmanya Sastri's first English translation edition, 1937:
  - 476 PDF pages, 464 non-empty OCR page blocks retained;
  - PDF SHA-256 `795DDB67D7416188B2272D2021B2B798561FAAAC08067A986AF0FACFD0552FCB`;
  - all 28 adhyayas plus verse and subject indexes are present.
- Rights caveat is permanent corpus metadata: the Digital Library of India catalog says `In Public Domain`, while the title page says `Copyright Registered`. Phaladeepika remains local research material pending any redistribution-rights review.
- Source PDFs and IA DjVu OCR XML are archived under `D:\GannFinancialAstro\sources\classical`; generated page-marked corpus text remains local/uncommitted under `jyotish_agent\corpus_text`.
- Extended every classical page block with `LANGUAGE`, `RECENSION`, `RIGHTS_BASIS`, and `RETRIEVAL_CAUTION` markers.
- Fixed a Unicode topic-classification bug: the previous ASCII-only normalizer reduced Devanagari keywords to empty strings and falsely tagged every BPHS page with every topic. Matching now preserves Unicode alphanumeric characters and rejects empty normalized patterns.
- Added `bphs_phaladeepika_source_review_20260711.md` with edition maps, rights findings, visual spot checks, hashes, retrieval locks, and promotion policy.
- Visually inspected BPHS pages 4, 30, 326, 665, 741 and Phaladeepika pages 6, 38, 80, 229, 360, 394. BPHS has physical damage but readable text; Phaladeepika is clean enough for English retrieval, with Sanskrit exact quotes still requiring page-image checks.
- Rebuilt private TF-IDF index:
  - total `4,565` chunks;
  - BPHS `1,351` chunks;
  - Phaladeepika `684` chunks.
- Retrieval checks:
  - Devanagari Dasha/graha/bala/Ashtakavarga query returned BPHS in all top-six results;
  - English strength/Drigbala/Dasa/transit query returned Phaladeepika in the top two;
  - case 43 no-LLM smoke still returned structured workspace evidence plus page-cited doctrine/reference material.
- Six stdlib ingestion/index tests pass.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260711_083631` (includes both generated corpus text files; the hashed source PDFs/OCR XML remain in the `D:` source archive).
- No calculation, aspect event, trade label, Auto Suggest, official ML note, BTC/USDJPY strategy, or MT5 execution logic changed.

## Previous Update - 2026-07-11

2026-07-11 first classical public-domain corpus ingestion:

- Ingested three identified historical English editions into the private local Jyotish RAG corpus:
  - `BRIHAT_JATAKA`: Varahamihira, N. Chidambaram Aiyar, second edition 1905, 306 PDF pages;
  - `BRIHAT_SAMHITA`: Varahamihira, N. C. Iyer, Parts I-II 1884-1885, 496 PDF pages;
  - `SURYA_SIDDHANTA`: Ebenezer Burgess with the Committee of Publication, 1858, 362 PDF pages.
- Wikimedia Commons identifies the three source editions as public domain/public-domain-mark and links to their Internet Archive originals.
- Archived source PDFs and page-structured Internet Archive DjVu OCR XML under:
  `D:\GannFinancialAstro\sources\classical`.
- Added `jyotish_agent/classical_source_editions.yaml` with edition, translator, rights, source URLs, section ranges, topics, PDF SHA-256 and OCR XML MD5.
- Added `jyotish_agent/ingest_classical_sources.py`:
  - verifies PDF and OCR hashes before processing;
  - checks expected OCR page count;
  - rebuilds page-cited local corpus text;
  - distinguishes front matter, translator material, root translation-with-notes and appendices/indexes.
- Added `classical_text_ingestion_review_20260711.md` with source-quality findings, visual checks, relevance and promotion locks.
- Retained page blocks:
  - Brihat Jataka `295`;
  - Brihat Samhita `489`;
  - Surya Siddhanta `362`.
- Generated text remains local/uncommitted under `D:\PycharmProjects\jyotish_agent\corpus_text`.
- Rebuilt private TF-IDF index:
  - total chunks `2,530`;
  - Brihat Jataka `341`;
  - Brihat Samhita `611`;
  - Surya Siddhanta `800`;
  - missing page/authority markers across these sources `0`.
- Updated local case explanation retrieval to reserve four slots for structured workspace evidence and four for doctrine/reference sources. This fixes the prior condition where case notes occupied all eight slots and classical sources never reached the LLM prompt.
- Dedicated source queries returned each expected classical source within the top three results; a case 43 no-LLM smoke test returned both rule-note evidence and page-cited doctrine.
- Updated corpus manifest, ingestion queue, PDF inventory and ranked corpus canon.
- Added ingestion/retrieval regression coverage; all five stdlib unit tests pass.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260711_070637` (includes the three generated local corpus text files; source PDFs/OCR XML remain in the hashed `D:` archive).
- No astrology calculation, market label, Auto Suggest, official ML note or MT5 execution logic changed. Surya Siddhanta is historical context and does not replace Swiss Ephemeris.

## Previous Update - 2026-07-11

2026-07-11 Sanjay Rath source audit and provenance-aware classical corpus:

- Fully audited the user-supplied image-only PDF `Crux of Vedic Astrology - Timing of Events` by Sanjay Rath:
  - 600 PDF pages / 589 numbered pages;
  - first edition in the scan dated 16 June 1998;
  - SHA-256 `E3307EDE78737E4E35E78B042A0CFD19CAB6CD46234087173AFD62203080AF9A`;
  - archived off `C:` at `D:\GannFinancialAstro\doc\Crux of Vedic Astrology-Timing of Events -- Sanjay Rath -- 1998.pdf` with the hash verified after the move.
- Rendered and visually checked front matter and representative chapter pages, then completed local OCR for all 600 pages.
- Added `sanjay_rath_crux_source_review_20260711.md`:
  - classifies the book as modern secondary interpretive commentary, not a classical root text;
  - maps all 15 chapters;
  - identifies Dasha selection, Narayana Dasha, Argala, Arudha, Hora Lagna, Sudarshana, Sarvatobhadra and Sahams as retrieval candidates;
  - explicitly blocks retrospective examples, mortality/medical/fertility material and natal statements from direct trading-rule promotion.
- Added `classical_jyotish_corpus_canon_20260711.md` with separate authority layers for:
  - astronomy/calculation history;
  - root predictive classics;
  - timing/Jaimini sources;
  - mundane context;
  - modern commentaries and experimental methods.
- Registered `SANJAY_RATH_CRUX_1998` in the local agent source registry and ingestion queue, and added discovery entries for Jaimini Upadesa Sutras, Sarvartha Chintamani, Tajika Nilakanthi and Yoga Yatra.
- Corrected stale `C:` paths in the corpus manifest to the active `D:` project/source locations.
- Full page-marked OCR text is local/uncommitted at:
  `D:\PycharmProjects\jyotish_agent\corpus_text\SANJAY_RATH_CRUX_1998.txt`.
- Updated `jyotish_agent/build_corpus_index.py` so page-marked sources never merge across page boundaries and every split chunk repeats its source/page metadata.
- Rebuilt the private local TF-IDF index:
  - total chunks: `778`;
  - Sanjay Rath chunks: `600`;
  - Sanjay chunks missing `PDF_PAGE`: `0`;
  - a mixed Narayana Dasha/Argala/Arudha/Hora Lagna/wealth query returned this source in all top-six results.
- Added `test_jyotish_corpus_index.py`; both page-citation regression tests pass under stdlib `unittest`.
- Updated the PDF feature inventory and local agent plan with the source authority hierarchy.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260711_063314` (includes the local OCR JSONL and generated page-marked corpus text, but not the 72.7 MB source PDF).
- No astrology formula, Auto Suggest rule, ML label or MT5 behavior changed. This work expands local explanation/RAG knowledge only.

## Previous Update - 2026-07-10

2026-07-10 BTC 3-week aspect filter:

- User clarified they meant removing aspects shorter than 3 weeks.
- Updated both BTC scripts:
  - `build_btc_weekly_astro_chart.py` default `--min-window-days` is now `21.0`;
  - `analyze_btc_aspect_effectiveness.py` default `--min-window-days` is now `21.0`.
- Reran evidence analyzer first so chart classification/noise exclusion uses the same 3-week filter:
  `D:\GannFinancialAstro\doc\btc_aspect_effectiveness_20260710_002051`
- Evidence counts with 3-week threshold:
  - historical windows >= 21 days: `119`;
  - analyzed events: `119`;
  - families: `72`;
  - `promising_candidate`: `2`;
  - `inconclusive`: `12`;
  - `inconclusive_low_repeatation`: `55`;
  - `noise`: `3`.
- Promising candidates remain:
  - `PLUTO|JUPITER::conjunction_orb`;
  - `NEPTUNE|SATURN::opposition_orb`.
- Noise candidates with 3-week threshold:
  - `SATURN|KETU::opposition_orb`;
  - `SATURN|RAHU::conjunction_orb`;
  - `URANUS|PLUTO::trine`.
- Rebuilt chart pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260710_002116`
- Main chart URL:
  `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=min21d_noise_excluded`
- Chart counts with 3-week threshold:
  - all generated windows before noise exclusion: `164`;
  - chart-visible windows after noise exclusion: `155`;
  - noise-excluded windows: `9`;
  - visible windows under 21 days: `0`;
  - all windows under 21 days: `0`;
  - minimum visible duration: `21.0` days.
- Server:
  - `127.0.0.1:8766` now serves `D:\GannFinancialAstro\doc\btc_weekly_astro_20260710_002116`;
  - HTTP check returned `200`.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py analyze_btc_aspect_effectiveness.py`;
  - `python analyze_btc_aspect_effectiveness.py`;
  - `python build_btc_weekly_astro_chart.py`.

## Previous Update - 2026-07-10

2026-07-10 BTC aspect family classification/noise exclusion:

- User defined family classification thresholds:
  - `promising_candidate`: at least 3 repeatations and >= 70% dominance in one clear bullish/bearish behavior;
  - `inconclusive`: at least 3 repeatations, directional evidence exists, but dominance is below 70%;
  - `noise`: at least 3 repeatations and less than 30% of repeatations produce any clear bullish/bearish behavior;
  - `inconclusive_low_repeatation`: any aspect family with fewer than 3 repeatations, regardless of apparent behavior, because future data could move it into promising/inconclusive/noise.
- Updated `analyze_btc_aspect_effectiveness.py`:
  - event rows now include `behavior_signal`;
  - short windows (`<= 7` weeks) map trough-only local turns to `bullish`, crest-only local turns to `bearish`, crest+trough to `mixed`, no turn to `no_signal`;
  - long windows (`>= 8` weeks) map start-to-end return to bullish/bearish only if it clears the move threshold;
  - summary rows now include `classification`, `classification_reason`, `dominant_behavior`, `dominant_behavior_rate`, `directional_signal_rate`, bullish/bearish/mixed/no-signal counts;
  - writes separate candidate CSVs:
    - `btc_aspect_promising_candidates.csv`;
    - `btc_aspect_inconclusive_candidates.csv`, including all low-repeatation families;
    - `btc_aspect_noise_candidates.csv`.
- Updated `build_btc_weekly_astro_chart.py`:
  - added `--aspect-classification-csv`, default `auto`;
  - chart generator auto-loads the latest `btc_aspect_effectiveness_summary.csv`;
  - aspect windows whose family classification is `noise` are excluded from chart overlays;
  - all raw windows are still saved to `btc_weekly_astro_windows_all.csv`;
  - chart-visible filtered windows remain in `btc_weekly_astro_windows.csv`;
  - metadata records classification CSV path, noise family count, and windows-before/after filter counts.
- New evidence output:
  `D:\GannFinancialAstro\doc\btc_aspect_effectiveness_20260709_235843`
- Classification counts from this run:
  - `promising_candidate`: `2`;
  - `inconclusive`: `13`;
  - `inconclusive_low_repeatation`: `77`;
  - `noise`: `4`.
- Promising candidates:
  - `PLUTO|JUPITER::conjunction_orb` bullish dominance `0.75`, directional signal rate `1.00`;
  - `NEPTUNE|SATURN::opposition_orb` bullish dominance `0.75`, directional signal rate `1.00`.
- Noise candidates excluded from chart overlays:
  - `SATURN|KETU::opposition_orb`;
  - `SATURN|RAHU::conjunction_orb`;
  - `JUPITER|VENUS::conjunction_orb`;
  - `URANUS|PLUTO::trine`.
- Rebuilt BTC weekly chart pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260709_235914`
- Main chart URL:
  `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=classified_noise_excluded`
- Chart filter verification:
  - all generated windows before noise filter: `216`;
  - chart-visible windows after excluding noise families: `204`;
  - excluded windows: `12`;
  - local server on `127.0.0.1:8766` returned HTTP `200`.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py analyze_btc_aspect_effectiveness.py`;
  - `python analyze_btc_aspect_effectiveness.py`;
  - `python build_btc_weekly_astro_chart.py`.

## Previous Update - 2026-07-09

2026-07-09 BTC weekly SR/aspect noise R&D:

- User reported BTC chart did not show planetary SR lines for `n > 60`, requested SR degree `d` be `360` and `180`, and asked for evidence/R&D to reduce noisy planet/aspect overlays.
- Updated `build_btc_weekly_astro_chart.py`:
  - removed hardcoded BTC SR degree `720`;
  - added `--degree-scales`, default `360,180`;
  - `sr_level(...)` now receives each degree scale explicitly;
  - `btc_weekly_sr_lines.csv` and `btc_weekly_sr_touches.csv` now record `degree_scale` as `180` or `360`;
  - chart SR selector now preserves coverage across `body + degree_scale + n_value` before filling by historical touch strength, so higher `n` groups are not hidden by low-n touch-heavy lines;
  - default visible SR cap raised to `360`.
- Rebuilt BTC weekly chart pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260709_231758`
- Main chart URL:
  `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=d360_d180_evidence`
- Chart/SR verification:
  - weekly candles: `465`;
  - filtered astro windows >= 14 days: `216`;
  - SR candidate lines in/near price range: `1144`;
  - SR touches: `31378`;
  - degree scales present in SR CSV: `180`, `360`;
  - all requested `n=30..150` present;
  - SR rows with `n > 60`: `792`;
  - balanced chart selection uses `360` lines, including `240` lines with `n > 60`, both degree scales, and all `n` values;
  - local server on `127.0.0.1:8766` returned HTTP `200`.
- Added `analyze_btc_aspect_effectiveness.py`:
  - fetches BTC weekly Binance candles;
  - builds historical transit-to-natal aspect windows using the same Bitcoin Genesis/Raman setup;
  - excludes Moon and Rahu/Ketu mutual pair via existing aspect generator;
  - filters windows shorter than 14 days;
  - logs every historical aspect event to `btc_aspect_effectiveness_events.csv`;
  - summarizes every aspect family to `btc_aspect_effectiveness_summary.csv`;
  - for windows `<= 7` weeks, evaluates whether a local crest/trough occurs inside the aspect window using a +/- 7-week context;
  - for windows `>= 8` weeks, evaluates start-to-end return from aspect start candle open to aspect end candle close;
  - adds deterministic weekly candlestick comments: doji, hammer-like, shooting-star-like, engulfing, inside/outside bar, large body;
  - adds research buckets so web-prior macro families can be separated from likely weekly noise without silently deleting anything.
- Evidence output pack:
  `D:\GannFinancialAstro\doc\btc_aspect_effectiveness_20260709_232357`
- Evidence counts:
  - historical windows >= 14 days: `153`;
  - analyzed events: `153`;
  - aspect families: `96`.
- Top reliability-weighted families from the first evidence run:
  - `URANUS|SUN::trine`;
  - `URANUS|RAHU::square`;
  - `SATURN|MARS::conjunction_orb`;
  - `NEPTUNE|URANUS::conjunction_orb`;
  - `SATURN|JUPITER::conjunction_orb`;
  - `URANUS|JUPITER::trine`;
  - `PLUTO|JUPITER::conjunction_orb`.
- Web/R&D priors recorded in the evidence note:
  - AstroConnexions emphasizes Jupiter/Saturn/Uranus/Neptune/Pluto and Saturn/Uranus BTC themes;
  - SG AppDev emphasizes Sun-Jupiter and Sun-to-Saturn/Uranus/Neptune/Pluto date studies;
  - WIRED documents that practitioners disagree, while mentioning Saturn transits, BTC Sun/Mars/Pluto Capricorn themes, and Jupiter/outer-planet combinations.
- Important boundary:
  - this first evidence script analyzes transit-to-natal aspect windows only; it does not yet score pure transit-to-transit/inter-planet aspects or automatically hide chart families. Use the CSVs first, then decide the filter list.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py analyze_btc_aspect_effectiveness.py`;
  - `python build_btc_weekly_astro_chart.py`;
  - `python analyze_btc_aspect_effectiveness.py`.

## Previous Update - 2026-07-07

2026-07-07 BTC weekly chart v2:

- User requested BTC weekly chart refinements:
  - filter out aspects shorter than two weeks;
  - show aspects after Jan 2025 and extend future astro windows through Jan 2030;
  - change SR `n` values to `30..150`;
  - keep closest-point hover rather than a vertical hover line.
- Updated `build_btc_weekly_astro_chart.py`:
  - default `--min-window-days` is now `14.0`;
  - added `--aspect-end`, default `2030-01-31`;
  - default `--n-values` is now `30,40,50,60,70,80,90,100,110,120,130,140,150`;
  - default `--max-aspect-windows` increased to `1000`, fixing the missing-post-Jan-2025 display caused by only drawing the first 180 windows;
  - daily transit/aspect generation now runs to `--aspect-end` instead of stopping at latest price candle;
  - bottom aspect-density panel extends through the future aspect endpoint;
  - x-axis range now spans price start through the future aspect endpoint;
  - SR visibility upper band widened to `1.80x` historical high so `n=140/150` levels can participate in forward research.
- Rebuilt BTC chart pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260707_223919`
- Main chart URL:
  `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=2030_14d_n30_150_final`
- Generated counts:
  - weekly candles: `465`;
  - filtered astro windows >= 14 days: `216`;
  - SR candidate lines in/near extended forward price range: `572`;
  - SR touches: `8841`.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py`;
  - filter audit returned `moon_rows=0`, `rahu_ketu_pair_rows=0`, `shorter_than_14_days=0`;
  - future audit returned `after_2025_01=90`, `after_2026_07=63`, latest window ending `2030-02-01 00:00 UTC`;
  - all requested `n` values `30..150` appear in `btc_weekly_sr_lines.csv`;
  - server on `127.0.0.1:8766` returned HTTP `200`;
  - in-app browser opened the final chart and console logs had no errors.

## Previous Update - 2026-07-07

2026-07-07 BTC weekly astro chart:

- User requested a Bitcoin weekly chart covering the last three bull-run/cycle spans through current data, with astrological overlays.
- Added `build_btc_weekly_astro_chart.py` as a separate BTC research generator so it does not disturb the USDJPY repeatation reviewer.
- Data/source decisions:
  - BTC price source is Binance public weekly `BTCUSDT` klines; available chart range starts `2017-08-14 05:30 IST`, so the first displayed bull-run span is the late-2017 peak tail, followed by the 2020-21 run and 2022-current cycle.
  - Genesis block timestamp is fixed as `2009-01-03 18:15:05 UTC` = `2009-01-03 23:45:05 IST`.
  - Primary birthplace hypothesis is `Van Nuys / Los Angeles`; this is explicitly marked unverified/experimental in metadata.
  - Alternate place hypotheses recorded in metadata: London and Dublin.
  - Ayanamsa uses the project doctrine setting: Raman.
- User filters implemented:
  - Moon excluded from natal/transit/aspect windows.
  - Rahu/Ketu mutual interaction excluded because they are always 180 degrees apart.
  - Aspect windows shorter than `7` days filtered out.
  - SR grid uses requested `n=10,20,30,40,50,60,70,80,90` and `f=1.6,1.8`.
- BTC scale note:
  - SR projection uses explicit `BTC_SCALE_DEGREE=720` so the requested `n/f` grid reaches the current BTC weekly price band; this assumption is written to README/metadata.
- Output pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260707_220921`
- Main chart:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260707_220921\btc_weekly_astro_chart.html`
- Supporting outputs:
  - `btc_weekly_price_binance.csv`
  - `btc_daily_transit_longitudes.csv`
  - `btc_weekly_transit_longitudes.csv`
  - `btc_weekly_astro_windows.csv`
  - `btc_weekly_sr_lines.csv`
  - `btc_weekly_sr_touches.csv`
  - `btc_weekly_metadata.json`
  - `README.md`
- Generated counts:
  - weekly candles: `465`;
  - filtered astro windows >= 7 days: `219`;
  - SR candidate lines in/near price range: `396`;
  - SR touches: `10134`.
- UI/chart polish:
  - dense SR line traces and filtered astro marker traces are hidden from legend;
  - chart HTML is responsive;
  - hover is forced to closest-point mode and Plotly spike/crosshair lines are disabled via post-render relayout so cursor hover does not create a full vertical read line.
- Server status:
  - separate static server listening on `127.0.0.1:8766`;
  - URL: `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=closest_hover_v2`;
  - HTTP check returned `200`.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py`;
  - generated output successfully;
  - filter audit returned `moon_rows=0`, `rahu_ketu_pair_rows=0`, `shorter_than_7_days=0`;
  - generated HTML contains the runtime closest-hover/spike-disable postscript;
  - in-app browser opened the chart and browser console had no errors.

## Previous Update - 2026-07-04

2026-07-04 global carryover rules for Mercury-Moon trine review:

- User asked whether the previous reviewed family learning could carry over into the current `MERCURY|MOON::trine` review family.
- Implemented neutral/global carryover templates in `build_repeatation_review_pack.py`:
  - `global_sr_geometry_classifier`;
  - `global_first_boundary_exit`;
  - `global_confirmed_break_extension`;
  - `global_multi_aspect_gann_exit_gate`;
  - `global_intrabar_ambiguity_ignore`.
- Important boundary:
  - these templates carry over SR/boundary/ignore mechanics from `AVG(ALL)|MOON::square`;
  - they do **not** carry over the old family direction, case personality, or `bearish_bias_support_barrier` as a Mercury-Moon trine family truth.
- Updated neutral marker-flow Auto Suggest so families without their own rule can still use global carryover:
  - after choosing start, it checks directional SR touches, next shaded/aspect zone, next hardcoded marker, and eligible multi-aspect Gann fan exit;
  - if the first SR has confirmed close/retest/continuation break, the SR is treated as a passed barrier and exit moves to the next attribution boundary;
  - otherwise the first clean boundary wins.
- Kept `reviewer_rule_replay.py` in sync with browser Auto Suggest so review-agent/replay memory does not split from the UI.
- Bumped UI cache key to `repeatation_ui_20260704_global_carryover_v65`.
- Rebuilt Mercury-Moon trine pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_95_mercury_moon_trine_20260704_232331`
- Removed incomplete timeout folder:
  `D:\GannFinancialAstro\doc\repeatation_review_case_95_mercury_moon_trine_20260704_232022`
- Server status:
  - API-aware server listening on `127.0.0.1:8765`, PID `23108`;
  - reviewer URL: `http://127.0.0.1:8765/repeatation_reviewer.html`;
  - HTTP checks returned `200` for both `repeatation_reviewer.html` and `aspect_review_case_95_chart.html`.
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py serve_repeatation_pack.py`
  - direct replay checks via `reviewer_rule_replay.auto_suggest_case(...)`:
    - case `95`: global carryover active, end rule `confirmed_break_next_shaded_zone_boundary`, signed pips `+45.7`;
    - case `124`: global carryover active and multi-aspect Gann exit won, end rule `gann_second_from_bottom_touch_multi_aspect`, signed pips `+2.0`;
    - case `147`: global carryover active, end rule `confirmed_break_next_shaded_zone_boundary`, signed pips `+217.3`.

2026-07-04 Mercury-Moon trine review start:

- User decided to begin reviewing the upcoming `MERCURY|MOON::trine` family before the next live/demo market event.
- Upcoming scan shows `MERCURY|MOON::trine` windows:
  - `2026-07-06 10:00 -> 12:00 IST`, peak `11:00`, orb delta `0.082065`;
  - `2026-07-23 02:00 -> 05:00 IST`, peak `03:00`;
  - `2026-08-02 07:00 -> 10:00 IST`, peak `08:00`.
- Existing historical review DB has `16` `MERCURY|MOON::trine` repeatations:
  `95, 124, 147, 241, 255, 306, 360, 367, 425, 454, 492, 554, 586, 599, 632, 653`.
- Stored 72h touch-log direction sketch before manual review:
  - `11` UP;
  - `5` DOWN;
  - no completed manual review/official ML history yet for this family.
- Built Mercury-Moon trine pack from seed `case_id=95`:
  `D:\GannFinancialAstro\doc\repeatation_review_case_95_mercury_moon_trine_20260704_051106`
- Server status:
  - API-aware server listening on `127.0.0.1:8765`, PID `13652`;
  - reviewer URL: `http://127.0.0.1:8765/repeatation_reviewer.html`;
  - HTTP checks returned `200` for both `repeatation_reviewer.html` and `aspect_review_case_95_chart.html`.

## Previous Update - 2026-07-04

2026-07-04 future-aspect generator / MT5 bridge / case 127 correction:

- Added `generate_upcoming_aspects.py`:
  - price-independent upcoming sidereal aspect window generator;
  - uses doctrine-locked Raman ayanamsa through Swiss Ephemeris;
  - default bodies: `AVG(ALL)`, seven classical planets, `RAHU`, `KETU`;
  - default aspects match the review pipeline: `conjunction_orb`, `square`, `trine`, `opposition_orb`;
  - enriches rows from `gann_aspect_annotations.sqlite` completed reviews and latest `official_ml_note` snippets by `family_key`.
- Generated local planning exports:
  - `D:\PycharmProjects\upcoming_aspects_20260704_30d.csv`
  - `D:\PycharmProjects\upcoming_aspects_20260704_30d.json`
  - these are local/generated outputs, not intended for commit.
- First upcoming 30-day scan from `2026-07-04 00:00 IST` found `73` aspect windows.
  - `AVG(ALL)|MOON::square` appears on `2026-07-04 12:00 -> 15:00 IST`, peak `13:00 IST`, orb delta `0.160969`.
  - The same family has `5` completed reviews in the DB: `4` bearish, `1` ignored, average signed pips `+24.68`, latest official note from corrected case `127`.
- Added `mt5_trade_executor.py`:
  - dry-run-first MT5 bridge for `status`, `buy`, `sell`, and `close`;
  - live trading is refused unless both `--live` and `--confirm LIVE` are passed;
  - supports exact terminal path, optional `--login/--server`, and password via an environment variable such as `MT5_PASSWORD`;
  - computes symbol pip size from MT5 digits and runs `order_check()` before dry-run output.
- MT5 local status test:
  - `MetaTrader5` Python package is installed (`5.0.5640`);
  - first unauthenticated `python mt5_trade_executor.py --status --symbol USDJPY` reached the package but failed terminal initialization with `Terminal: Authorization failed`;
  - user provided demo account details for `MetaQuotes-Demo`; credential was used only as a temporary process environment variable and was not written to repo files;
  - authenticated status check succeeded: account connected, balance `100000.00 USD`, `USDJPY` selected, min volume `0.01`, pip size `0.01`;
  - live trading is **not ready yet** because MT5 terminal status reports `trade_allowed=false` even though account `trade_allowed=true`;
  - USDJPY tick returned by the terminal appears stale, so before order dry-runs/live testing, open MT5, enable AutoTrading/algo trading, and confirm current live quotes are updating.
- Corrected the case `127` split-brain state:
  - viewport fans remain visual/ML-context only;
  - trade replay uses the full exported trade-candle universe, not only visible candles;
  - case `127` is restored as `bearish +4.0 pips`;
  - start `2025-05-28T22:00:00+05:30 @ 144.965`;
  - end `2025-05-28T23:00:00+05:30 @ 144.925`;
  - rules `first_case_window_sr_line_touch -> gann_second_from_bottom_touch_multi_aspect`;
  - official ML note replaced with note `#22`, status `codex_verified_trade_gann_exit_restored`.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260704_042319`
- Server status:
  - API-aware server listening on `127.0.0.1:8765`, PID `13400`;
  - HTTP check for case `127` returned `200`.
- Verification:
  - `python -m py_compile mt5_trade_executor.py generate_upcoming_aspects.py reviewer_rule_replay.py build_repeatation_review_pack.py`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260704_042319 --case-id 127`
  - `python generate_upcoming_aspects.py --start 2026-07-04 --days 30 --step-minutes 60 --output-csv D:\PycharmProjects\upcoming_aspects_20260704_30d.csv --output-json D:\PycharmProjects\upcoming_aspects_20260704_30d.json --top 12`
  - authenticated `python mt5_trade_executor.py --status --symbol USDJPY --login <demo_login> --server MetaQuotes-Demo` succeeded after password was supplied via temporary `MT5_PASSWORD`;
  - live order dry-run is intentionally deferred until terminal AutoTrading and current tick freshness are confirmed.

## Previous Update - 2026-05-31

2026-05-31 case 127 viewport-fan trading split-brain fix:

- User asked whether the newly added two visible-viewport Gann fans were being used in trading, because case `127` looked like the close marker had moved to a bottom-most viewport-fan intersection instead of the remembered `23:30` close marker.
- Current intended rule is confirmed:
  - the two viewport fans are visual / ML-context only;
  - Auto Suggest trading logic must not use them as start/end candidates.
- Browser drawer / current HTML evidence showed case `127` should be:
  - start `2025-05-28 22:00:00+05:30 @ 144.965`;
  - end `2025-05-28 23:30:00+05:30 @ 145.125`;
  - outcome `bullish +16.0 pips`;
  - start rule `first_case_window_sr_line_touch`;
  - end rule `next_later_hardcoded_marker`;
  - viewport fan status `visual_and_ml_context_only_not_auto_suggest_trade_logic`.
- Root cause of the stale contradiction:
  - browser-side candle collection already ignored hidden candlestick traces;
  - `reviewer_rule_replay.py` still included `trace.visible == false` candlestick traces, so historical replay could reproduce the older Gann-exit path even though the browser Auto Suggest no longer used it.
- Fixed `reviewer_rule_replay.py`:
  - `collect_candles()` now skips hidden candlestick traces;
  - case `127` expectation now requires `2` selected-window SR touch candidates, matching the browser drawer.
- Updated SQLite `D:\PycharmProjects\gann_aspect_annotations.sqlite`:
  - completed review for case `127` now stores the current `bullish +16.0` marker-flow decision;
  - replaced stale official ML note with current `official_ml_note` `note_id=21`, status `codex_verified_current_replay`;
  - note explicitly says not to train the old `gann_second_from_bottom_touch_multi_aspect` / `bearish +4.0` path as the current decision.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260531_010132`
- Server status:
  - API-aware server listening on `127.0.0.1:8765`, PID `18460`;
  - curl verification for case `127` returned HTTP `200`.
- Verification:
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260531_010132 --case-id 127`
  - result passed with start `22:00 @ 144.965`, end `23:30 @ 145.12528246460198`, and `case_window_sr_touch_count=2`.

## Previous Update - 2026-05-30

2026-05-30 C-drive storage cleanup / D-drive path hardening:

- User reported severe C-drive storage pressure and asked to move/delete project duplicates from C.
- Moved project-owned C paths off C:
  - `C:\Users\ADMIN\Desktop\doc` -> `D:\GannFinancialAstro\doc`
  - `C:\Users\ADMIN\Desktop\Trading_Algo\New folder` -> `D:\Trading_Algo\New folder`
  - remaining `C:\Users\ADMIN\Desktop\Trading_Algo` root files -> `D:\Trading_Algo\Desktop_Trading_Algo_root_legacy_20260530`
  - `C:\Users\ADMIN\Desktop\WD GANN` -> `D:\Trading_Algo\WD GANN`
  - `C:\Users\ADMIN\Desktop\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf` -> `D:\GannFinancialAstro\sources\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf`
- Important recovery detail:
  - the old `C:\Users\ADMIN\PycharmProjects` contained the live `.git` repo, while `D:\PycharmProjects` was empty after the move;
  - moved that migrated repo into `D:\PycharmProjects` as the canonical active repo, then removed the temporary `D:\C_Drive_Migrated` duplicate.
- Active code/config path defaults now use D-drive locations:
  - project data/root: `D:\PycharmProjects`
  - chart export/root: `D:\GannFinancialAstro\doc`
  - Telegram helpers: `D:\Trading_Algo\New folder`
  - legacy Telegram bot fallback: `D:\Trading_Algo\WD GANN`
- Active Python/JSON/YAML/PS1 and non-handoff Markdown scans now have no `C:\Users\ADMIN...` path references outside historical handoff/backup text.
- Confirmed the leftover `C:\Users\ADMIN\Desktop\New folder (3)` is photo/image content, not this project, so it was not moved automatically.
- Verified:
  - `python -m py_compile aspect_annotation_store.py serve_repeatation_pack.py sr_touch_lazy_dashboard.py build_aspect_sr_touch_log.py build_pair_aspect_market_log.py build_sr_anchor_reversal_log.py rebuild_dataset_mt5_ipo_allpairs.py jyotish_agent\telegram_notify.py jyotish_agent\telegram_codex_relay.py`
  - `python jyotish_agent\telegram_notify.py --dry-run` confirmed Telegram config/runner are available from D.

2026-05-30 visible-viewport Gann envelope fans:

- User clarified the new two extra Gann fans should use the whole currently visible Plotly/browser chart span, not only the selected aspect-review window.
- `build_repeatation_review_pack.py` now adds a `Viewport Fans` soft button in the marker drawer:
  - finds the highest visible candlestick top wick and anchors a bearish/downward context fan there;
  - finds the lowest visible candlestick bottom wick and anchors a bullish/upward context fan there;
  - stores them in `viewport_fans` autosave/download payloads and includes them in `current_marker_ml_note`;
  - displays a drawer summary labelled `visual/ML context only`, so these fans do not alter Auto Suggest trade start/end logic yet.
- The fan traces use the same ratios as the main Gann fan: `1x4`, `1x2`, `1x1`, `2x1`, `4x1`.
- Robustness fixes:
  - marker UI now waits for real `window.Plotly.relayout` before attaching; it no longer immediately binds a no-op Plotly shim just because the graph div exists;
  - exported case charts now inline Plotly JS instead of relying on external `plotly.min.js`, because the in-app browser was rendering the SVG but not exposing external Plotly reliably;
  - a fallback SVG drawing path was added for viewport fans when live Plotly is unavailable in the in-app browser;
  - candlestick collection now ignores traces with `visible === false`, so hidden timeframe candles do not pollute the highest/lowest visible wick scan.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260530_035143`
- Restarted server on port `8765`, PID `20544`.
- Current case 185 URL:
  `http://127.0.0.1:8765/aspect_review_case_185_chart.html?v=repeatation_ui_20260530_viewport_fans_v64&fresh=verify10`
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py sr_touch_lazy_dashboard.py reviewer_rule_replay.py codex_review_task_queue.py serve_repeatation_pack.py`
  - rebuilt all 16 AVG(ALL)|MOON square repeatation charts;
  - browser screenshot confirmed the drawer summary and the extra context fan lines are visible on the chart. In-app browser DOM inspection remains sandboxed and does not reliably expose the injected SVG/Plotly runtime, so screenshot verification is the useful check for this feature.

2026-05-30 case 185 ignore-trade / intrabar SR sandwich:

- User reviewed case `185` in `AVG(ALL)|MOON::square` and chose to follow Codex recommendation to mark it ignored.
- Decision saved:
  - completed review `review_id=9`;
  - official ML note `note_id=18`;
  - `review_status=ignored`;
  - `outcome_label=ignore_trade`;
  - rules `ignore_trade_multi_sr_same_candle_intrabar_unknown -> ignore_trade_multi_sr_same_candle_intrabar_unknown`.
- Added first-class UI ignore signal definitions in `build_repeatation_review_pack.py`:
  - `multi_sr_same_candle`;
  - `ambiguous_intrabar_order`.
- Case `185` official note says:
  - exact selected AVG(ALL)|MOON row stores MARS/MERCURY SR confluence, not Neptune/Saturn for the selected-case touch;
  - stored SR prices are MARS `144.800108` and MERCURY `144.913239`, around `11.3` pips apart;
  - 2025-06-25 07:30 and 08:00 M30 candles span both SRs, so OHLC cannot prove whether upper entry/rejection SR or lower target/support was touched first;
  - astro pressure leans bearish (Drik `-32.1V`, malefic `-45.0V` vs benefic `+12.8V`, doctrine bearish) but Shadbala is weak/below threshold (`321.2V`, ratio `0.929`), Chesta is low, regime count is crowded, and FX heuristic conflicts bullish.
- Important ML instruction:
  - train case `185` as `ignore_trade_multi_sr_same_candle_intrabar_unknown`;
  - do not label it as failed bullish or bearish;
  - live trading may use lower timeframe/tick sequence, but historical M30 review should not invent intrabar order.
- Fixed `reviewer_rule_replay.py` historical replay:
  - when `gann_second_from_bottom_touch_multi_aspect` wins, replay now applies the Gann fan direction to `outcome_label` and signed pips just like the browser Auto Suggest;
  - this resolved the stale replay contradiction on case `127`.
- Case `127` was replay-corrected:
  - completed review `review_id=8`;
  - official ML note `note_id=19`;
  - current replay is `bearish +4.0 pips`;
  - rules `first_case_window_sr_line_touch -> gann_second_from_bottom_touch_multi_aspect`.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260530_015348`
- Restarted server on port `8765`, PID `4900`.
- Current case 185 review URL:
  `http://127.0.0.1:8765/aspect_review_case_185_chart.html?v=repeatation_ui_20260530_ignore_intrabar_v57&fresh=case185done`
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py codex_review_task_queue.py serve_repeatation_pack.py`
  - `python codex_review_task_queue.py --list-pending --limit 20` returned no pending tasks.
  - Browser verification after clearing stale local draft shows:
    `Completed review: ignored`,
    `rules: ignore_trade_multi_sr_same_candle_intrabar_unknown -> ignore_trade_multi_sr_same_candle_intrabar_unknown`,
    and the official note starts with `Decision: Ignore Trade`.

## Previous Update - 2026-05-29

2026-05-29 mixed SR-reference verifier fix:

- User reported that case `127` still showed Dream Review:
  `queued_for_codex | issues 2` and `SR geometry conflict`, specifically:
  `Auto Suggest says SR is above entry, but the draft talks as if the relevant SR is below/support.`
- Diagnosis:
  - this was not a true contradiction;
  - current Auto Suggest can legitimately contain two SR contexts:
    - `sr_geometry`: the executed/final exit context, currently `SR is above entry: resistance/entry`;
    - `barrier_sr_geometry`: the first barrier/reference being tested, currently `SR is below entry: support/target`;
  - the verifier was treating mention of the lower first barrier as contradiction against the final exit geometry.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_mixed_sr_verifier_v56`;
  - verifier evidence now includes `barrier_label` and `mixed_sr_references`;
  - SR-geometry contradiction checks now allow opposite-side language when it matches `barrier_sr_geometry`;
  - verifier check log now explicitly prints:
    `Mixed SR references checked: final geometry is ...; first barrier/reference is ...`
- Updated `codex_review_task_queue.py`:
  - Dream Review correction tasks that contain only an SR-geometry conflict caused by mixed `sr_geometry` vs `barrier_sr_geometry` are skipped instead of replacing the official ML note.
- Replaced the bad case `127` official note written by task `12` with official note `#14`:
  - status `codex_verified_mixed_sr_reference_no_contradiction`;
  - records current outcome `bearish`, current marker result `-6.0` pips for that draft/review state;
  - explicitly says not to train `SR geometry conflict` from mixed final/barrier SR references.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_202527`
- Restarted server on port `8765`, PID `21004`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260529_mixed_sr_verifier_v56&fresh=mixedsr`
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py codex_review_task_queue.py serve_repeatation_pack.py jyotish_agent\dream_review_agent.py jyotish_agent\explain_case.py`
  - `python codex_review_task_queue.py --list-pending --limit 20`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_202527`
  - browser: after `Draft ML Reason`, Dream Review returned `caution_only | issues 1`, no `SR geometry conflict`; only BPHS synthetic-orb caution remains.

2026-05-29 case 127 Gann fan outcome correction:

- User reported case `127` still displayed `bullish -4.0 pips` in both the plot callout and marker drawer, but the executed Auto Suggest path is a top-wick Gann fan/downward projection and should score as `bearish +4.0 pips`.
- Root cause:
  - the marker-flow Gann fan exit correctly stored `gann_fan.fan_direction = bearish`;
  - profit display still inherited the family/default `bullish` outcome, including from an older autosaved draft.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_case127_gann_outcome_v55`;
  - added `autoOutcomeFromSuggestion(...)` and `setAutoOutcome(...)`;
  - when `end_rule === gann_second_from_bottom_touch_multi_aspect`, Auto Suggest now scores by the fan direction:
    - top-wick/down fan -> `bearish`;
    - bottom-wick/up fan -> `bullish`;
  - restored drafts with that Gann fan rule now also auto-correct the outcome, so stale localStorage cannot keep the old bullish label.
- Updated SQLite official ML note for case `127`:
  - new `official_ml_note` id `12`;
  - outcome corrected to `bearish`;
  - signed pips corrected to `+4.0`;
  - note explains that raw move `-4.0` pips is favorable for the top-wick bearish fan path.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_200807`
- Restarted server on port `8765`, PID `1340`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260529_case127_gann_outcome_v55&fresh=outcome2`
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py codex_review_task_queue.py serve_repeatation_pack.py`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_200807`
  - `python codex_review_task_queue.py --list-pending --limit 20`
  - browser check on case `127` confirmed:
    `Live trade result bearish +4.0 pips`, selected outcome `bearish`, entry `144.965`, exit `144.925`.
  Pending Codex review task queue is empty.

2026-05-29 immediate Dream Review agent trigger:

- User reported case `127` had a Dream Review contradiction and requested:
  - stop relying on the 30-minute review-agent heartbeat;
  - trigger the agent immediately once `Draft ML Reason` has produced a draft and Dream Review has run.
- Deleted heartbeat automation:
  `process-codex-review-agent-queue`
- Updated `codex_review_task_queue.py`:
  - added `--process-pending`;
  - added deterministic queue processor for:
    - `official_ml_note`: writes a Codex review-agent official note from completed-review payload/Auto Suggest evidence;
    - `dream_review_correction`: writes a corrected official note from verifier/Dream Review evidence;
    - `rule_replay_review`: skips non-material replay changes where only rule version metadata changed; flags material replay changes for Codex.
- Updated `serve_repeatation_pack.py`:
  - `/api/dream_review` now calls `process_pending_tasks()` immediately after queuing a Dream Review correction;
  - browser response includes `codex_agent_result` / `codex_agent_error`.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_immediate_dream_agent_v54`;
  - Dream Review panel now reports immediate Codex review-agent processed task count/actions;
  - verifier direction/SR checks now inspect the deterministic analysis section instead of matching raw Auto Suggest JSON/RAG snippets, reducing false contradictions from reference geometry or old family notes.
- Processed current pending queue:
  - task `#10`, case `127` Dream Review correction -> official note `#8`;
  - task `#6`, case `43` official note -> note `#9`;
  - task `#8`, case `103` official note -> note `#10`;
  - tasks `#7` and `#9` replay reviews skipped because replay showed only rule-version metadata drift, not material P/L/rule-path changes.
- Case `127` official correction:
  - deterministic evidence wins over draft wording;
  - outcome is `bullish`;
  - live trade result is `-4.0` pips;
  - active SR geometry is `SR is below entry: support/entry`;
  - marker-flow/reference geometry separately records `SR is above entry: resistance/target`;
  - future drafts must name which SR reference they mean before training.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_084521`
- Restarted server on port `8765`, PID `20768`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260529_immediate_dream_agent_v54&fresh=immediate4`
- Verification:
  - `python -m py_compile codex_review_task_queue.py serve_repeatation_pack.py build_repeatation_review_pack.py`
  - `python codex_review_task_queue.py --process-pending --limit 20`
  - `python codex_review_task_queue.py --list-pending --limit 20`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_084521`
  - HTTP `200` and browser load for case `127` v54
  all passed; pending Codex review task queue is empty.

2026-05-29 Dream Review queue -> Codex review-agent correction:

- User reported the browser warning:
  `Dream review found contradiction(s) but did not auto-apply; queued for Codex/human review.`
  and requested the Codex agent to check queued Dream Review drafts and auto-apply/correct when deterministic evidence is clear.
- Root cause:
  `jyotish_agent\dream_review_agent.py` wrote contradiction drafts to `jyotish_agent\dream_review_queue.jsonl`, but the Codex heartbeat automation only watched SQLite `codex_review_tasks`.
- Updated `serve_repeatation_pack.py`:
  - when `/api/dream_review` returns `queued_for_codex` / `needs_review`, it now enqueues a durable SQLite `dream_review_correction` task;
  - browser response includes `codex_task_ids` for queued Dream Review corrections.
- Updated `codex_review_task_queue.py`:
  - added `--ingest-dream-queue`;
  - imports existing `dream_review_queue.jsonl` rows into `codex_review_tasks`;
  - dedupes by Dream Review report filename;
  - `dream_review_correction` tasks now carry the original payload, dream result, report path, and correction policy.
- Updated `jyotish_agent\dream_review_agent.py` and `build_repeatation_review_pack.py` copy:
  - warning text now says the contradiction is queued for Codex review-agent correction, not left as vague human-only review.
  - cache key advanced to `repeatation_ui_20260529_dream_queue_v53`.
- Imported existing queued Dream Review contradiction:
  - task `#5`, case `8`, report:
    `D:\PycharmProjects\jyotish_agent\dream_review_reports\case_8_20260529_034136_dream_review.md`
- Resolved task `#5`:
  - Dream Review contradiction was a break-confirmation conflict;
  - local draft said failed/missing support break;
  - deterministic Auto Suggest/verifier evidence confirmed support break, failed retest, and continuation;
  - Codex replaced the official ML note with note `#7`, status `codex_verified_dream_review_resolved`;
  - note explicitly rejects contradictory local LLM draft wording and tells ML to use deterministic evidence.
- Cleared stale duplicate pending official-note tasks `#2`, `#3`, and `#4` for case `8` as skipped.
- Updated heartbeat automation `process-codex-review-agent-queue`:
  - first runs `codex_review_task_queue.py --ingest-dream-queue`;
  - then processes `dream_review_correction`, `official_ml_note`, and `rule_replay_review` tasks;
  - auto-applies deterministic corrections through official notes when evidence is clear;
  - leaves uncertain cases marked for review instead of letting local LLM text become official.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_035153`
- Restarted server on port `8765`, PID `16628`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260529_dream_queue_v53&fresh=dreamqueue`
- Verification:
  - `python -m py_compile serve_repeatation_pack.py codex_review_task_queue.py jyotish_agent\dream_review_agent.py build_repeatation_review_pack.py`
  - `python codex_review_task_queue.py --ingest-dream-queue`
  - `python codex_review_task_queue.py --list-pending --limit 20`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_035153`
  - HTTP `200` from the v53 case `8` chart
  all passed; pending Codex review task queue is empty.

2026-05-29 Gate 3 external certification pass:

- User requested certification of the above-mentioned review cases after discussing Gate 3 trusted sources.
- Installed PyJHora `4.8.6` as a local Tier B external witness under:
  `D:\GannFinancialAstro\external_tools\pyjhora`
  - This is intentionally outside the git repo and should remain local/uncommitted.
  - First dependency install hit low C-drive temp/cache space; rerun used D-drive temp/cache and succeeded.
- Used PyJHora with:
  - Raman ayanamsa;
  - true node / Rahu;
  - event timezone;
  - `drik.sidereal_longitude`, `drik.tithi`, and `drik.nakshatra`.
- Filled Gate 3 external expected values in:
  `D:\PycharmProjects\astro_external_validation_template_20260527.csv`
- Certified 25 astronomy/Panchanga rows:
  - `case_8_event_start`
  - `case_43_event_start`
  - `case_103_event_start`
  - `case_127_sr_touch_start`
  - `gann_reference_tokyo`
  - each with Sun/Moon/Rahu Raman sidereal longitude, Tithi, and Moon Nakshatra/Pada.
- Updated `astro_function_certification.py`:
  - certification notes are now idempotent;
  - repeated runs no longer append duplicate `numeric delta` / `categorical exact compare` / pending compare text.
- Reran:
  `python astro_function_certification.py`
- Current Gate 3 result:
  `25 pass / 0 fail / 10 pending`
- Remaining pending Gate 3 rows:
  Shadbala and Drik Bala rows for each sample remain intentionally pending until we have row-specific JHora/book-style exports.
- Updated:
  `D:\PycharmProjects\astro_function_certification_report_20260527.md`
  `D:\PycharmProjects\trading_rule_replay_result_20260527.json`
- Verification:
  - `python -m py_compile astro_function_certification.py`
  - `python test_strict_shadbala_doctrine.py`
  - `python codex_review_task_queue.py --list-pending --limit 10`
  all passed.

2026-05-29 historical re-simulation + Codex-owned ML notes:

- User requested:
  - historical re-simulation after new rules;
  - affected prior reviewed cases listed when replay changes P/L or rule path;
  - official ML notes created/altered only by Codex, not silently by the local LLM/page;
  - low-credit automation to process those note/replay tasks.
- Updated `reviewer_rule_replay.py`:
  - added deterministic `auto_suggest_case()` replay for generated packs;
  - added `replay_completed_review_impacts()` for historical re-simulation of completed reviews;
  - replay now parses chart markers, candles, SR line touches, shaded/aspect windows, multi-aspect overlap, support/resistance geometry, break confirmation, attribution boundaries, zone boundaries, and provisional multi-aspect Gann fan exits;
  - existing case `127` SR-touch regression and family rule source guards still pass.
- Updated `serve_repeatation_pack.py`:
  - `/api/complete_review` now runs historical re-simulation against previously completed reviews in the same family;
  - response lists affected/stable cases and replay deltas when a current rule path would alter old completed reviews;
  - local browser/live ML notes are treated as draft evidence only.
- Updated `aspect_annotation_store.py`:
  - added durable `codex_review_tasks` queue table;
  - added queue helpers: `enqueue_codex_review_task()`, `list_codex_review_tasks()`, `update_codex_review_task()`;
  - added `replace_rule_note_type()` so Codex can update one official ML note for a case without accumulating stale duplicates.
- Added `codex_review_task_queue.py`:
  - `--list-pending` shows queued Codex tasks;
  - `--write-official-note TASK_ID` writes a Codex-approved permanent `official_ml_note`;
  - `--mark-task` can mark replay/code-review tasks done/failed/skipped with a JSON result.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_historical_replay_v52`;
  - Replay Impact drawer now shows historical replay mode, stable/affected counts, replayed pips/rules, and fallback errors;
  - ML Notes drawer now states live marker notes are draft evidence and permanent official notes are Codex-owned;
  - Review Complete shows queued Codex task ids.
- Processed first Codex-owned official note:
  - Review Complete for case `8` queued task `#1`;
  - Codex wrote/replaced `official_ml_note` note `#6` for case `8`;
  - task `#1` marked `done`;
  - pending queue verified empty.
- Created heartbeat automation:
  - id `process-codex-review-agent-queue`;
  - runs every 30 minutes;
  - checks `codex_review_tasks`, writes official notes only after Codex review, inspects replay impacts, corrects stale notes/code when deterministic evidence supports it, and commits/pushes meaningful changes.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_022249`
- Restarted server on port `8765`, PID `22428`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260529_historical_replay_v52&fresh=officialnote2`
- Browser verification:
  - drawer shows official Codex ML note plus live marker draft note;
  - drawer shows policy: official ML notes are Codex-owned;
  - Review Complete queue/replay UI rendered correctly.
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py aspect_annotation_store.py serve_repeatation_pack.py reviewer_rule_replay.py codex_review_task_queue.py`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_022249`
  - direct historical replay against saved SQLite completed review returned `affected=0`, `unchanged=1`, `failed=0`
  - `python test_strict_shadbala_doctrine.py`
  - `python codex_review_task_queue.py --list-pending --limit 10`
  all passed.

2026-05-29 review-completion agent ledger:

- User requested automated agents that work alongside manual review:
  - after start/end markers and P/L are available, create ML notes automatically;
  - mark a recurrence reviewed;
  - compare new rule paths against already reviewed repeatations;
  - give future rule changes a deterministic place to report earlier cases that need replay/correction.
- Updated `aspect_annotation_store.py`:
  - added durable `completed_reviews` table;
  - added `upsert_completed_review()` and `list_completed_reviews()`;
  - each completed review stores case/family, timeframe, outcome, start/end times, entry/exit, signed/raw pips, rule version, Auto Suggest start/end rule, full Auto Suggest JSON, live marker ML note JSON, replay-impact JSON, and reviewer note.
- Updated `serve_repeatation_pack.py`:
  - added `/api/complete_review`;
  - endpoint saves/updates one completed review and returns a replay-impact summary for the same family;
  - current first replay-impact pass flags previous completed reviews whose stored rule path or rule version differs from the new completed review, so they can be replay-checked after rule changes.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_review_agent_v51`;
  - builder defaults now use project-local `D:\PycharmProjects` paths and `D:\GannFinancialAstro\doc` export root instead of stale C-drive defaults;
  - generated chart metadata loads any existing completed review for each case;
  - marker drawer now has `Review Complete`;
  - completion payload includes live marker ML note, exact P/L, start/end rules, Auto Suggest evidence, reviewer note, and UI rule version;
  - drawer shows completed status plus replay-impact summary.
- Initialized `D:\PycharmProjects\gann_aspect_annotations.sqlite` with the new schema.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_014054`
- Restarted server on port `8765`, PID `16016`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260529_review_agent_v51&fresh=reviewagent`
- Verification:
  - HTTP `200` from case `8` chart.
  - Browser opened the new case `8` chart.
  - `Review Complete` saved case `8` to `completed_reviews` as review `#1`.
  - Saved review: `bearish +23.3 pips`, start rule `family_rule_case_window_entry_open_price`, end rule `confirmed_break_next_shaded_zone_boundary`, rule version `repeatation_ui_20260529_review_agent_v51`.
  - Replay impact shows no previous completed reviews in this family yet.
  - `python -m py_compile build_repeatation_review_pack.py aspect_annotation_store.py serve_repeatation_pack.py reviewer_rule_replay.py` passed.

## Previous Update - 2026-05-29

2026-05-29 live marker-derived ML Notes:

- User reported case `8` had no visible ML Notes after family notes were correctly separated from exact-case notes.
- Design decision:
  - saved DB ML notes remain strict/exact-case only;
  - family notes remain in `Applied family rules` / training memory;
  - marker-derived ML notes are now generated live from the actual current trade start/end markers and P/L.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_live_marker_ml_notes_v50`;
  - added `currentMarkerMlNote()`;
  - `ML Notes` now shows `Current marker ML note` as soon as trade start/end exist, whether placed manually or by Auto Suggest;
  - live note includes case/family, outcome, signed/raw pips, entry/exit times/prices, start/end sources, Auto Suggest start/end rules, Auto Suggest reason, SR geometry, break confirmation, Gann fan status, multi-aspect gate status, rule-vs-default tracking, top astro hints, and any reviewer note;
  - live note is included in `mlNotesPlainText()` so Draft ML Reason and dream/verifier context can consume it;
  - live note is included in autosaved browser draft and downloaded marker JSON as `current_marker_ml_note`.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_010327`
- Restarted server on port `8765`, PID `21572`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260529_live_marker_ml_notes_v50&fresh=mlnotes`
- Verification:
  - HTTP `200` from case `8` chart.
  - Playwright/Edge ran Auto Suggest on case `8`.
  - `ML Notes` panel showed one live note:
    `Current marker ML note`, outcome `bearish`, `+23.3 pips`, start rule `family_rule_case_window_entry_open_price`, end rule `confirmed_break_next_shaded_zone_boundary`, SR geometry `SR is below entry: support/target`, break confirmation `Support break confirmed`, Gann fan exit `blocked_no_multi_aspect_overlap`.
  - Browser draft localStorage contained `current_marker_ml_note`.
  - `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py serve_repeatation_pack.py aspect_annotation_store.py` passed.

## Previous Update - 2026-05-27

2026-05-27 case-specific ML Notes cleanup + Auto Suggest replay:

- User reported that case `103` still showed ML notes from case `8`.
- Root cause:
  `load_ml_notes()` merged case-family notes into every repeatation's visible `ML Notes` section.
- Updated `build_repeatation_review_pack.py`:
  - visible `meta.mlNotes` now includes only exact-case ML notes;
  - case-family notes remain available through `meta.appliedFamilyRules` / training memory;
  - case-family notes no longer appear as if they are exact notes for unrelated repeatations.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_170507`
- Restarted server on port `8765`, PID `16764`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_103_chart.html?v=repeatation_ui_20260527_multi_aspect_gann_exit_v49&fresh=notesfix`
- Verified generated case `103` chart now has `"mlNotes": []`.
  Case-family teaching notes still appear in `appliedFamilyRules`, which is intentional training/rule context rather than visible exact-case ML notes.
- Replayed Auto Suggest v48 pack vs v49 pack after the provisional multi-aspect Gann fan exit rule.
  Changed P/L cases:
  - case `127`: `+16.0` -> `-4.0` pips, delta `-20.0`; exit changed to `gann_second_from_bottom_touch_multi_aspect`.
  - case `185`: `+4.7` -> `+0.5` pips, delta `-4.2`; exit changed to `gann_second_from_bottom_touch_multi_aspect`.
  - case `216`: `+31.2` -> `-4.2` pips, delta `-35.4`; exit changed to `gann_second_from_bottom_touch_multi_aspect`.
  - case `384`: `+37.1` -> `-1.2` pips, delta `-38.3`; exit changed to `gann_second_from_bottom_touch_multi_aspect`.
- Interpretation:
  the new Gann fan exit remains provisional and needs manual review before promotion because it currently worsens all four changed repeatations in replay.
- Telegram status was sent with the case `103` note fix and the four replay deltas.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py serve_repeatation_pack.py aspect_annotation_store.py`
  `python reviewer_rule_replay.py`
  `python test_strict_shadbala_doctrine.py`
  all passed.

2026-05-27 multi-aspect Gann fan exit gate:

- User requested that the provisional Gann fan close-marker rule apply exclusively when multiple aspect windows overlap.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260527_multi_aspect_gann_exit_v49`;
  - added `collectAspectWindows()` and `multiAspectOverlapEvidence()`;
  - formal definition: multiple aspect = at least one reviewed candle has two or more aspect windows overlapping it;
  - for M30 review this means at least one 30-minute candle overlaps at least two aspect windows;
  - added provisional `gann_second_from_bottom_touch_multi_aspect` exit rule;
  - the rule is blocked unless the multiple-aspect gate passes;
  - if eligible, Auto Suggest can close at the first touch of the second-from-bottom Gann fan line;
  - for bearish/top-wick fans, second-from-bottom is `2x1` because `4x1` is lowest;
  - for bullish/bottom-wick fans, second-from-bottom is `1x2` because `1x4` is lowest;
  - the candidate audit now shows whether the Gann fan exit was chosen, checked, not found, or blocked.
- Added structured case `127` ML note in `gann_aspect_annotations.sqlite`:
  - Saturn SR/resistance caused temporary hesitation;
  - bullish FX/doctrine scores with zero conflict, friendly Moon condition, non-low Shadbala, and high Saptavargaja explain why reversal stayed limited;
  - weak Chesta and negative Drik explain hesitation/retest rather than full reversal;
  - new Gann fan exit is explicitly marked provisional and gated by multi-aspect overlap.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_162034`
- Restarted API-aware server on port `8765`, PID `19824`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_multi_aspect_gann_exit_v49&fresh=multi`
- Verification:
  `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py serve_repeatation_pack.py aspect_annotation_store.py`
  `python reviewer_rule_replay.py`
  `python test_strict_shadbala_doctrine.py`
  all passed.

2026-05-27 Gann fan wick-direction fix:

- User reported case `127` Gann fan direction was wrong.
- Root cause:
  Gann fan slope followed the selected trade outcome, so a top-wick anchor could still draw bullish/upward if the trade outcome was bullish.
- Updated `build_repeatation_review_pack.py`:
  - `gannFanForStart()` now sets fan projection from the wick anchor side:
    top wick -> bearish/downward projection;
    bottom wick -> bullish/upward projection.
  - Added a render/draw compatibility guard so older restored draft state is corrected too:
    if stored fan anchor source contains `top`, direction is forced bearish;
    if it contains `bottom`, direction is forced bullish.
  - Drawer now displays fan projection explicitly.
  - Cache version advanced to `repeatation_ui_20260527_gann_wick_direction_v48`.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_134039`
- Restarted server on port `8765` from that pack.
- Browser verification:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_gann_wick_direction_v48&fresh=wickdir2`
  shows:
  `Gann fan: anchored at top wick 2025-05-28 22:00:00+05:30 @ 144.965; projection bearish`.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py`
  `python reviewer_rule_replay.py`
  `python test_strict_shadbala_doctrine.py`
  all passed.

2026-05-27 trusted external source intake workflow:

- User asked where outside trusted values should come from and approved the recommendation.
- Added `trusted_external_sources.md`.
- Source tiers now documented:
  - Tier A: Swiss Ephemeris documentation and Raman ephemeris samples for astronomy/position checks.
  - Tier B: Jagannatha Hora as preferred Shadbala/Jyotish cross-check; PyJHora as secondary automated checker.
  - Tier C: Drik Panchang and secondary Panchanga calculators for Panchanga limb checks.
- Updated `astro_function_certification.py` so Gate 3 is an actual intake loop:
  - reruns preserve existing values in `astro_external_validation_template_20260527.csv`;
  - filled `external_expected_value` and `external_source` values are carried forward;
  - longitude rows compare with `<= 0.02 deg` tolerance;
  - Shadbala/Drik/Virupa rows compare with `<= 0.5 virupa` tolerance;
  - categorical Panchanga rows compare with exact case-insensitive text match.
- Reran certification:
  Gate 3 now reports `0 pass / 0 fail / 35 pending`, which is expected until external expected values are entered.
- Updated `astro_function_research_audit_20260527.md` with the intake workflow.
- Verification:
  `python -m py_compile astro_function_certification.py`
  `python astro_function_certification.py`
  `python reviewer_rule_replay.py`
  `python test_strict_shadbala_doctrine.py`
  all passed.

2026-05-27 4-gate astro/trading certification runner:

- User asked to proceed with the 4-gate certification process.
- Added `astro_function_certification.py`.
- Generated first certification artifacts:
  - `astro_function_certification_report_20260527.md`
  - `astro_function_certification_inventory_20260527.csv`
  - `astro_position_baseline_20260527.csv`
  - `panchanga_baseline_20260527.csv`
  - `astro_external_validation_template_20260527.csv`
  - `trading_rule_replay_result_20260527.json`
- Gate 1 formula inventory:
  9 feature families now have source anchor, implementation file/function, status label, strict/proxy label, validation status, current gap, next action, and ML training policy.
- Gate 2 astronomical baseline:
  Raman ayanamsa Swiss Ephemeris baselines generated for sample cases `8`, `43`, `103`, `127`, and `1889-02-11 00:00 Asia/Tokyo`.
  These are reproducibility baselines, not external validation yet.
- Gate 2 Panchanga baseline:
  generated local Tithi/Paksha/Nakshatra/Pada/Yoga/Karana/weekday baseline rows for the same samples.
- Gate 3 external validation:
  template created with blank expected-value columns for trusted ephemeris/Panchanga/Shadbala/Drik comparison.
- Gate 4 trading replay:
  `reviewer_rule_replay.py` passed.
  Case `127` has data-level replay; cases `8`, `43`, and `103` are still source-guarded pending shared Auto Suggest replay logic.
- Updated `astro_function_research_audit_20260527.md` with the certification runner results.
- Current verdict:
  Shadbala/Drik/Panchanga are `implemented_unvalidated`, not externally certified.
  Raw local LLM prose remains `do_not_train_raw_text`; train only from deterministic evidence, manual notes, verified corrections, and rule lessons.
- Verification:
  `python -m py_compile astro_function_certification.py`
  `python astro_function_certification.py`
  `python -m py_compile astro_function_certification.py reviewer_rule_replay.py build_repeatation_review_pack.py strict_shadbala_doctrine.py panchanga_doctrine.py`
  `python test_strict_shadbala_doctrine.py`
  `python reviewer_rule_replay.py`
  all passed.

2026-05-27 replay guard + astro certification plan:

- User asked to proceed with the next guardrail and asked how to certify the astro functions.
- Added `reviewer_rule_replay.py`.
- Replay v1 behavior:
  - discovers latest AVG(ALL)|MOON square review pack unless `--pack-dir` is supplied;
  - parses generated Plotly HTML directly;
  - decodes typed Plotly arrays;
  - fully replays case `127` selected-window SR wick-touch detection without needing the browser;
  - asserts start rule `first_case_window_sr_line_touch`;
  - asserts start `2025-05-28T22:00:00+05:30`;
  - asserts end `2025-05-28T23:30:00+05:30`;
  - asserts Gann anchor side `top`;
  - asserts at least three selected-window SR touches.
- Replay v1 also adds source guards for teaching cases `8`, `43`, and `103` so the family-rule strings/candidate branches remain present until that browser-side logic is factored into reusable Python.
- Added an Astro Function Certification Plan to `astro_function_research_audit_20260527.md`.
  Proposed gates:
  formula inventory, astronomical position certification, Jyotish doctrine calculator certification, and trading-feature certification.
- Certification labels proposed:
  `implemented_unvalidated`, `proxy_research_feature`, `externally_validated`, `disputed_tradition`, and `do_not_train`.
- Verification:
  `python -m py_compile reviewer_rule_replay.py build_repeatation_review_pack.py strict_shadbala_doctrine.py panchanga_doctrine.py`
  `python test_strict_shadbala_doctrine.py`
  `python reviewer_rule_replay.py`
  all passed.

2026-05-27 Auto Suggest candidate inspector / audit truth pass:

- User asked to implement the candidate inspector and to say plainly what was reviewed and what still has shortcomings.
- `build_repeatation_review_pack.py` now uses cache version:
  `repeatation_ui_20260527_candidate_inspector_v47`.
- Added an Auto Suggest `Candidate check` / `Auto Suggest candidates` table in the marker drawer.
- The table records deterministic start/end decision trails:
  chosen candidate, rejected candidates, reference hardcoded confluence markers, first SR target, next shaded-zone boundary, next hardcoded marker / attribution boundary, time, price, SR price, SR gap, touch band, wick side, and plain-English reason.
- Case `127` browser verification after Clear markers + Auto Suggest:
  start `2025-05-28 22:00:00+05:30 @ 144.965`;
  end `2025-05-28 23:30:00+05:30 @ 145.125`;
  result bullish about `+16.0 pips`;
  Gann fan anchored at top wick;
  candidate table shows 5 candidates and explicitly rejects the later `23:00` / `23:30` SR touches because `22:00` already won.
- Fixed Python compile warning by escaping the generated JavaScript `\s` regex inside the Python string.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_081226`.
- Restarted server from that pack:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_candidate_inspector_v47`.
- Updated `astro_function_research_audit_20260527.md` with:
  what was reviewed, what was not exhaustively reviewed, the candidate-inspector implementation, and remaining risk register.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py` passed with no warning.
  Browser check confirmed candidate table, `2025-05-28 22:00`, `gap 2.2 pips`, and top-wick Gann fan text.

2026-05-27 case 127 first SR wick-touch Auto Suggest:

- User pointed out that case `127` should not start at the later exported hardcoded confluence marker; the earlier `2025-05-28 22:00` candle wick was already close enough to the SR line.
- Root cause found:
  upstream hardcoded selected-case marker export prioritizes confluence dots, so the later `23:30` confluence marker hid the earlier plain SR-line wick touch.
- `build_repeatation_review_pack.py` now adds reviewer-side selected-window SR wick-touch detection:
  it scans candles inside the selected case window against visible SR lines, uses a tight SR band of `max(at-SR epsilon, 3 pips)`, and prefers the first valid wick touch over a later confluence dot for default Auto Suggest start.
- `gannFanForStart()` now respects an explicit `gann_anchor_side` from the chosen start candidate, so case `127` anchors at the top wick even though the reviewed outcome is bullish.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_041655`
- Restarted server from that pack:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_case_sr_touch_v46b`
- Browser verification after Clear markers + Auto Suggest:
  start `2025-05-28 22:00:00+05:30 @ 144.965`;
  end `2025-05-28 23:30:00+05:30 @ 145.125`;
  result bullish `+16.0 pips`;
  Gann fan anchored at top wick `2025-05-28 22:00:00+05:30 @ 144.965`.
- Added research/audit addendum:
  `astro_function_research_audit_20260527.md`.
  It records the case-127 finding, candidate-inspector recommendation, source cross-check notes, and next audit gates for Shadbala/Drik/Panchanga/rule replay.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py` passed.

Next suggested work:

- Add a marker candidate inspector to the drawer so each Auto Suggest shows all start/end candidates and why one won.
- Build deterministic rule replay/regression checks for teaching cases `8`, `43`, `103`, and `127`.
- Continue the source-backed Jyotish audit: mark each astro feature as implemented, proxy, missing, disputed, externally validated, or needing validation.
- Keep local LLM output contained: deterministic evidence + manual notes + verified dream corrections should be training truth, not raw LLM prose.

## Previous Update - 2026-05-24

2026-05-24 Gann fan visibility / clean SR close:

- User reported on case `103` that the Gann fan was not visible, and earlier noted this recurrence is clean enough that trade should close when price touches SR rather than extending after break confirmation.
- `build_repeatation_review_pack.py` cache key advanced to `repeatation_ui_20260524_gann_clean_sr_v36`.
- Added `Show Gann Fan` button beside `Auto Suggest` in the marker drawer. If Auto Suggest has not run, it runs Auto Suggest; if markers already exist, it refreshes the Gann fan from the current trade start/outcome.
- Adjusted `bearish_bias_support_barrier` Auto Suggest behavior:
  when first support break is confirmed but there is no later attribution-boundary marker/event before extension logic, the clean recurrence target remains the first lower SR touch. New end rule: `family_rule_clean_first_sr_touch_target`.
- Rebuilt the AVG(ALL)|MOON square repeatation pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_43_avg_all_moon_square_20260524_235119`
  and synced it into the served folder:
  `D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Live URL:
  `http://127.0.0.1:8765/aspect_review_case_103_chart.html?v=repeatation_ui_20260524_gann_clean_sr_v36`.
- Verification: `python -m py_compile build_repeatation_review_pack.py` passed. Live case 103 HTML contains v36, `Show Gann Fan`, `family_rule_clean_first_sr_touch_target`, clean first-SR target text, and Gann anchor-dot code.

2026-05-24 D-drive migration:

- User wanted the project moved off C: before uninstalling PyCharm because C: was almost full and the laptop was lagging.
- Migrated the full active repo/project folder:
  `C:\Users\ADMIN\PycharmProjects` -> `D:\PycharmProjects`.
- Migrated generated review/export docs:
  `C:\Users\ADMIN\Desktop\doc` -> `D:\GannFinancialAstro\doc`.
- Replaced the old C: paths with Windows junctions so existing hardcoded scripts and browser links keep working:
  `C:\Users\ADMIN\PycharmProjects` -> `D:\PycharmProjects`
  `C:\Users\ADMIN\Desktop\doc` -> `D:\GannFinancialAstro\doc`
- Verified the D: repo copy:
  `git status`, latest commits, key scripts/data, and `python -m py_compile build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\explain_case.py`.
- Restarted the repeatation review server from D:
  PID `12308`, command rooted at `D:\PycharmProjects\serve_repeatation_pack.py`, serving `D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Verified live case link returns HTTP 200:
  `http://127.0.0.1:8765/aspect_review_case_103_chart.html?v=repeatation_ui_20260523_draft_ml_reason_v35`.
- C: free space improved from about `1.8 GB` to about `12.2 GB`.

2026-05-24 handoff cleanup:

- Refreshed this recovery handoff after reviewing it from a new Codex app session.
- Confirmed the file is the canonical handoff at:
  `D:\PycharmProjects\CURRENT_PROJECT_HANDOFF.md`.
  The old C: path is now a junction and remains usable for compatibility.
- Main correction:
  the older `Next Recommended Steps` list had become stale because later entries already implemented much of the review UI navigation, marker drawer, local draft ML reason workflow, and Ollama/Jyotish agent setup.
- Updated `Git State` with the latest local commits visible at cleanup time.
- Replaced the stale next-step list with the current continuation path:
  continue AVG(ALL)|MOON square repeatation review, use deterministic evidence plus `Draft ML Reason`, promote/revise/discard provisional ML notes, improve local LLM prompt/model quality only after more cases are reviewed, and then move toward walk-forward validation.

## Previous Update - 2026-05-23

2026-05-23 portable Ollama + local model setup:

- User asked Codex to continue with the recommended local LLM setup.
- Normal `Ollama.Ollama` installer had previously failed/cancelled.
- Checked portable package:
  `Ollama.Ollama.Portable` version `0.20.2`, zip installer from GitHub release.
- `winget install Ollama.Ollama.Portable` downloaded and verified the package but failed during extraction.
- Downloaded the portable zip directly to:
  `D:\Ollama\downloads\ollama-windows-amd64-v0.20.2.zip`
  with size about `1.87 GB`.
- Extracted manually into:
  `D:\Ollama\app`.
- Portable binary path:
  `D:\Ollama\app\ollama.exe`.
- Model storage path:
  `D:\Ollama\models`.
- Set user environment variable:
  `OLLAMA_MODELS=D:\Ollama\models`.
- Started Ollama server:
  `D:\Ollama\app\ollama.exe serve`.
- API verified at:
  `http://127.0.0.1:11434/api/tags`.
- Ollama detected GPU:
  `NVIDIA GeForce GTX 1060` through CUDA, total VRAM reported by Ollama as `6.0 GiB`, available about `5.1 GiB`.
- Pulled model:
  `qwen2.5:3b`, `3.1B`, `Q4_K_M`, size about `1.9 GB`.
- Added helper scripts:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\start_ollama_portable.ps1`,
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\stop_ollama_portable.ps1`.
- Updated `explain_case.py` default local model from `llama3.1` to:
  `qwen2.5:3b`.
- Ran LLM-backed case explanation smoke test for case `43`; output wrote to:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\case_explanations\case_43_jyotish_explanation.md`.
- Important quality finding:
  the local 3B model can run, but it drifted into generic astrology text in the commentary section.
- Mitigation added:
  `explain_case.py` now always puts deterministic plain-English evidence first, then local LLM commentary second, and adds a warning when LLM commentary appears to drift.
- Current intended behavior:
  deterministic Python/evidence remains ground truth;
  local LLM is only a draft explanatory layer until we improve prompts/model quality.
- Sent Telegram progress confirmation:
  portable Ollama is running from `D:\Ollama`, `qwen2.5:3b` is installed, and case explanation now uses deterministic evidence first.

2026-05-23 Telegram relay received messages + 5-minute Codex heartbeat:

- User sent Telegram relay messages and asked Codex to check.
- Verified `codex_telegram_inbox.jsonl` contained two messages:
  `/codex`
  and `if you get this please go with your recommendation of local llm model and install softwares you require`.
- Sent Telegram confirmation:
  `Codex received your Telegram relay message. Proceeding with recommended local LLM setup now.`
- Marked both relay messages seen with:
  `python jyotish_agent\read_codex_relay_inbox.py --mark-seen`.
- Attempted to install Ollama after setting:
  `OLLAMA_MODELS=D:\Ollama\models`.
- Ollama install did not complete:
  winget reported `You cancelled the installation`, installer exit code `5`.
- User then asked to check relay messages every 5 minutes as an automation before hibernating.
- Created active Codex heartbeat automation:
  `check-telegram-codex-relay-inbox`,
  schedule every 5 minutes,
  attached to this thread.
- Automation task:
  check `C:\Users\ADMIN\PycharmProjects\jyotish_agent\codex_telegram_inbox.jsonl`,
  use `read_codex_relay_inbox.py`,
  mark pending messages seen,
  summarize/act in this Codex thread,
  and preserve the normal handoff/backup/commit/push workflow after meaningful changes.

2026-05-23 Telegram -> Codex relay pivot:

- User clarified the desired Telegram behavior:
  not a local LLM chatbot, but a middleman relay from Telegram into the current Codex/project workflow.
- Stopped the in-progress `winget install Ollama.Ollama` attempt from the previous interpretation.
- Added a local Telegram relay inbox:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\telegram_codex_relay.py`.
- The relay does not use OpenAI, does not use a local LLM, and does not execute arbitrary Telegram commands.
- Relay behavior:
  `/codex <message>` queues a normal message for Codex;
  `/urgent <message>` queues a high-priority message for Codex;
  plain text is also saved as a relay message;
  `/status`, `/last`, `/ping`, and `/help` are supported.
- Relay inbox path:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\codex_telegram_inbox.jsonl`.
- Added reader helper:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\read_codex_relay_inbox.py`.
- Start/stop scripts:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\start_telegram_codex_relay.ps1`,
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\stop_telegram_codex_relay.ps1`.
- Relay is currently running as a background Python process:
  `telegram_codex_relay.py --announce-start`.
- Important limitation:
  the Telegram bot cannot directly inject messages into the live Codex app/session unless Codex exposes a supported local session API/websocket. Current implementation creates a durable local inbox that Codex reads during active work.
- Smoke verification passed:
  Python compile,
  one-shot backlog-safe poll,
  background process running,
  and `read_codex_relay_inbox.py` reports no pending messages initially.

2026-05-23 local LLM runtime options + Telegram test:

- User confirmed:
  extracted corpus/index should stay local and uncommitted,
  Telegram test message is allowed,
  laptop is a gaming laptop with space on `D:\`.
- Sent Telegram test message through:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\telegram_notify.py`.
- Telegram result:
  `Telegram message sent.`
- Local hardware check:
  CPU `Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz`,
  `6` cores / `12` logical processors,
  RAM about `16 GB`,
  GPU `NVIDIA GeForce GTX 1060` with about `4 GB` VRAM,
  `D:\` free space about `819 GB`.
- Recommendation:
  start with quantized `3B` to `8B` models and keep generated local corpus/index/model cache on `D:\` if it grows.
- Best first runtime option remains `Ollama` for simplest local API integration with `explain_case.py`;
  `LM Studio` is the friendliest manual/model-browsing option;
  raw `llama.cpp` is best only if later optimization/control becomes more important than setup simplicity.

2026-05-23 local Jyotish RAG agent CLI v1:

- User asked to start with the pending list and create the local LLM/Jyotish agent, and pointed to Telegram scripts under:
  `C:\Users\ADMIN\Desktop\Trading_Algo\New folder`.
- Added local agent scripts under:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent`.
- Added `build_corpus_index.py`:
  builds a local TF-IDF retrieval index from allowed/local sources.
- Current indexed sources:
  local PDF alignment extracts from `pdf_alignment_extracts`,
  SQLite review/rule notes from `gann_aspect_annotations.sqlite`,
  and a schema/sample slice from the SR touch-log CSV.
- Generated local-only artifacts are intentionally ignored by git:
  `jyotish_agent\corpus_chunks.jsonl`,
  `jyotish_agent\index\tfidf_index.joblib`,
  and `jyotish_agent\case_explanations\*`.
- Added `explain_case.py`:
  gathers case evidence from SQLite, retrieves supporting Jyotish/trading notes, and writes a plain-English ML/Jyotish explanation packet.
- `explain_case.py` can use a local Ollama-compatible runtime if available at:
  `http://127.0.0.1:11434/api/generate`;
  otherwise it falls back to deterministic extractive RAG output so work is not blocked.
- Generated a local explanation for case `43`:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\case_explanations\case_43_jyotish_explanation.md`.
- Case `43` explanation currently says:
  bearish family behavior is present, but support did not break cleanly because total strength is middle, Drik pressure is not strongly bearish, Chesta is only middle, aspect exactness is not tight, touched SR is Jupiter/benefic support, and Moon condition is not unusually damaged.
- Added `telegram_notify.py`:
  reuses the existing Telegram runner/config from `C:\Users\ADMIN\Desktop\Trading_Algo\New folder\telegram_job_runner.py`.
- Telegram dry-run passed without sending a message:
  `telegram_configured=True`, runner exists, chat id present, token present.
- Smoke verification passed:
  Python compile for all new scripts,
  `explain_case.py --case-id 43 --no-llm`,
  and `telegram_notify.py --dry-run`.
- Pending before calling this a real local LLM agent:
  choose the local runtime default (`Ollama` recommended unless user prefers LM Studio/llama.cpp),
  install/select the model,
  connect a `Draft ML Reason` UI button to `explain_case.py`,
  decide when Telegram notifications should be sent,
  and keep full extracted book text/index files local-only unless user explicitly wants them committed.
- Pending after the current AVG(ALL)|MOON square family review:
  rule lifecycle (`provisional -> accepted/revised/discarded`),
  automated astro reason extraction into SQLite notes,
  bullish mirrored SR-barrier family rules,
  and wider public-domain Jyotish corpus ingestion after rights/source review.

2026-05-23 ML Notes drawer + Jyotish agent groundwork v33:

- User asked where ML notes can be read in the marker drawer, then asked to add a clear ML Notes collapsible/dropdown section.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260523_ml_notes_v33`.
- Marker drawer now has a dedicated `ML Notes` collapsible section below `Applied family rules`.
- The new section loads ML notes from SQLite by same `pair_key + aspect` family:
  exact-case ML notes show as `this case`;
  family-scoped ML notes show as `case family`.
- The section renders note id, source case, note type, parsed key fields, and the full saved note body in a wrapped scrollable block.
- Rebuilt AVG(ALL)|MOON square repeatation pack from seed case `43`:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260523_103509`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current direct case 43 URL:
  `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_ml_notes_v33`.
- In-app browser verification passed:
  panel exists, `ML Notes` exists, case `43` shows `astro_reason_not_strong_enough_to_break_support`,
  family note from case `8` shows `confirmed_support_break_but_stop_at_next_event_boundary`,
  and `noWebglVisible=false`.
- Started local Jyotish agent groundwork in:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent`.
- Added `corpus_manifest.csv` with public-domain/open-access candidates, user-owned PDFs, SQLite notes, and touch-log data sources.
- Added `local_jyotish_agent_plan.md` documenting the strict architecture:
  deterministic Python owns calculations/trades, local LLM explains from retrieved evidence and citations.
- Added `prepare_corpus_skeleton.py` and generated `ingestion_queue.json`.
- Current ingestion queue:
  `6` allowed/local/public-domain-candidate items and `16` manual-review-required items.
- Web/source starting points recorded:
  Dekho Panchang library index (`https://www.dekhopanchang.com/en/learn/library`),
  Surya Siddhanta archive candidate (`https://archive.org/details/surya-siddhanta-translation`),
  Vedanga Jyotisha archive candidate (`https://archive.org/details/VedangaJyotisa`).
- Important policy decision:
  start with local RAG/explanation, not model weight training. Use user-owned/local PDFs and workspace-generated notes; verify rights before ingesting modern translations.
- User asked for Telegram ping if needed; no Telegram connector is available in this Codex workspace, so blockers should be preserved in this handoff and chat instead.

2026-05-23 SR geometry + rule outcome tracking v25:

2026-05-23 SR geometry + rule outcome tracking v25:

- User liked two ideas and asked if they could be implemented:
  explicit SR geometry classification and rule outcome tracking.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260523_sr_geometry_v25`.
- Auto Suggest now records `sr_geometry`:
  whether the chosen SR/marker is below/above entry, its role for the selected direction, and distance in pips.
- Directional SR geometry currently labels:
  bearish + SR below entry = `support/target`;
  bearish + SR above entry = `resistance/entry`;
  bullish + SR above entry = `resistance/target`;
  bullish + SR below entry = `support/entry`.
- Auto Suggest now records `outcome_tracking` when a family rule changes the suggestion:
  rule signed pips, old/default signed pips, and delta.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_004714`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current direct case 43 URL:
  `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_sr_geometry_v25`
- Browser verification on case `43` after clicking `Auto Suggest`:
  `SR geometry: SR is below entry: support/target (-27.9 pips from entry)`;
  `Rule tracking: rule +27.9 pips vs old default +2.2 pips | difference +25.8 pips`;
  live bearish P/L remains `+27.9 pips`;
  no WebGL overlay.
- Reminder after finishing this `AVG(ALL)|MOON square` case-family review:
  implement rule status lifecycle (`provisional -> accepted/revised/discarded`) and automate/draft astro reason extraction with a local Jyotish explanation agent.

2026-05-23 case 43 ML astro-reason note:

- User asked whether the detailed astro reasoning for case `43` had been saved as an ML note.
- Added a dedicated rule note in `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`:
  `note_id=2`, `case_id=43`, `note_type=ml_astro_reason`.
- Note label:
  `astro_reason_not_strong_enough_to_break_support`.
- Linked family rule:
  `bearish_bias_support_barrier`.
- The note records:
  price entered the event/zone, touched SR below price, and reverted instead of breaking support.
- The note captures these ML learning reasons:
  total planet strength is middle (`~383`, ratio `~1.09`), above minimum but not forceful-break strength;
  aspect pressure is middle/slightly positive, not sharply negative;
  motion strength is middle/low-ish, so no strong Chesta-style force clue;
  aspect distance is middle, not very tight/exact;
  touched SR is Jupiter, a benefic/supportive line, so falling into Jupiter SR below price can act as support/floor;
  Moon condition is not badly damaged and common Moon friend/exaltation clues are not special bearish-break clues.
- Trading implication captured:
  bearish bias into support should prefer earlier short entry and target/support exit, not late continuation short after support touch unless break-and-retest confirms.

2026-05-23 family-rule automarker v24:

- User asked to wire the applied family rule into `Auto Suggest`.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260523_rule_automarker_v24`.
- Auto Suggest now checks applied family rules before the old fallback.
- For `bearish_bias_support_barrier`, when outcome is bearish and the rule is applied:
  - trade start uses the case-window entry/open price from `full_window_entry_price`;
  - trade end uses the first lower hardcoded SR/marker after the case-window entry;
  - the suggestion reason explicitly says it is treating SR below price as target/support instead of assuming immediate support break.
- The old fallback remains for charts/families without this rule:
  selected hardcoded marker -> next later marker.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_001034`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current direct case 43 URL:
  `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_rule_automarker_v24`
- Verification passed:
  Python compile, full repeatation pack rebuild/sync, served HTML checks, and in-app browser test clicking `Auto Suggest` on case `43`.
- Browser test result for case `43`:
  auto suggestion `rule clean`,
  start `2025-04-04 02:30:00+05:30 @ 146.158`,
  end `2025-04-04 02:30:00+05:30 @ 145.879`,
  live bearish P/L `+27.9 pips`,
  no WebGL overlay.

2026-05-22 applied case-family rule v23:

- User clarified that a local rule should apply to the unique case family with all repeatations, not only one occurrence.
- Updated rule note `note_id=1` in `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`:
  `note_type=family_sr_rule`,
  `scope=case_family/local`,
  `status=provisional_until_all_repeatations_reviewed`,
  `rule_label=bearish_bias_support_barrier`,
  `seed_case_id=43`,
  `family=AVG(ALL)|MOON::square`.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260522_family_rules_v23`.
- The reviewer pack now loads case-family scoped rule notes from SQLite and injects them into every chart in the same `pair_key + aspect` family as `appliedFamilyRules`.
- The marker drawer now shows an `Applied family rules` block above ML trait hints; for this family it displays:
  `bearish_bias_support_barrier`, provisional status, seed case `43`, and family `AVG(ALL)|MOON::square`.
- `repeatation_marker_template.csv` now includes `applied_family_rules_json` so ML exports can consume the same family rule.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260522_235321`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current direct case 43 URL:
  `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260522_family_rules_v23`
- Verification passed:
  Python compile, full repeatation pack rebuild/sync, HTTP checks confirming the rule appears in both case `43` and case `8`, and in-app browser check confirming the drawer shows `Applied family rules` and `bearish_bias_support_barrier`.

2026-05-22 case 43 local SR rule note:

- User reviewed case `43` and observed price entered the selected zone, touched SR below price, and reverted instead of breaking support.
- Case context:
  `case_id=43`, `AVG(ALL)|MOON square`, default/full-window direction `bearish`, but full-window bearish result was only about `+1.0 pip`.
- Interpretation captured:
  case 43 is a local example of bearish pressure into support, not a clean bearish breakdown.
- Saved local DB rule note in `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`:
  `note_id=1`, `case_id=43`, `note_type=local_sr_rule`.
- Rule note text records:
  `scope=case_id/local; type=sr_rule; direction=bearish; if active/nearest SR is below current price, treat it first as target/support and expect touch-revert unless a candle closes below SR and retests/fails. Preferred trade plan is earlier short entry when price enters the selected event/zone, take profit at first lower SR or next hardcoded marker, and avoid chasing continuation after support touch without break confirmation.`
- Astrology reason recorded:
  total planet strength middle (`~383`, ratio `~1.09`), aspect pressure middle/slightly positive, motion strength middle, aspect not tight/exact, and touched SR is Jupiter/benefic support.
- ML label recorded:
  `bearish_bias_support_barrier`.
- This is intentionally a local/case rule until more case_ids are manually reviewed.

2026-05-22 WebGL-free Plotly reviewer v21:

- User saw `WebGL is not supported by your browser` in the Codex in-app browser after opening the v20 chart.
- Root cause: `sr_touch_lazy_dashboard.py` still used Plotly `go.Scattergl` traces for planetary SR lines and interaction markers. Chrome can render these, but the Codex in-app browser may not expose WebGL.
- Updated `C:\Users\ADMIN\PycharmProjects\sr_touch_lazy_dashboard.py` to use regular SVG-safe `go.Scatter` for those traces.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260522_svg_plotly_v21`.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260522_173238`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260522_svg_plotly_v21`
- Direct seed chart URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260522_svg_plotly_v21`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, exported chart data trace parse showing `52` SVG `scatter` traces and `1` candlestick trace with no active `scattergl` data traces, and in-app browser check confirming the chart renders with `noWebglVisible=false`.

2026-05-22 all-astro repeatation evidence table v20:

- User asked whether enemy sign, friendly house, and other astro features are being compared across repeatations of the same case family, with only the most distinguishable features shown.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260522_astro_evidence_v20`.
- Added an expandable `All astro feature comparison` block under the ML trait hints. It compares the current repeatation against the same case family across all scored astro/context features, not just the top hints.
- Added plain feature categories:
  `sign / house`, `planet strength`, `timing / moon calendar`, `overlap / cleanliness`, `market-score context`, and `other context`.
- Added house-quality derived features for the aspect planets, using whole-sign house context:
  `supportive/angular-or-luck house`, `growth/action house`, `difficult/hidden house`, `money/relationship pressure house`, and `neutral house`.
- Evidence rows now include repeat count, bullish/bearish split, average pips for matching repeatations, delta versus the full group, group average, and clue tags such as `rare`, `common`, `direction linked`, or `only bearish samples`.
- The fixed `Planet strength` block remains above the ranked hints so Shadbala/strength is always visible.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260522_004530`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260522_astro_evidence_v20`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260522_astro_evidence_v20`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, chart HTTP `200`, served HTML content check, and in-app browser check confirming `All astro feature comparison`, `Planet 2 house`, `Planet 2 sign relationship`, `Total planet strength`, and `sign / house`.

2026-05-21 fixed planet-strength/Shadbala side-panel v19:

- User could not find Shadbala strength in the hover or side menu because the side menu only showed the top six ranked ML traits; full Shadbala total/ratio could be pushed out of the visible list.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260521_strength_panel_v19`.
- Added a fixed `Planet strength` block above the ranked ML trait hints, so Shadbala/strength values are always shown regardless of trait ranking.
- The block currently shows:
  `Total planet strength`, `Strength vs minimum`, `Multi-chart planet strength`, `Timing strength`,
  `Aspect pressure strength`, and `Motion strength`.
- For case 8, verified side-panel values include:
  `Total planet strength: 384.47 (middle)`,
  `Strength vs minimum: 1.12 (middle)`,
  `Multi-chart planet strength: 107.64 (middle)`,
  `Timing strength: 115.16 (middle)`,
  `Aspect pressure strength: -7.04 (middle)`,
  `Motion strength: 9.11 (middle)`.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_204659`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_strength_panel_v19`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_strength_panel_v19`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, chart HTTP `200`, served HTML content check, and in-app browser check confirming the side panel contains `Planet strength`, `Total planet strength`, and `Strength vs minimum`.

2026-05-21 plain-language trait hints v18:

- Reworked the ML trait hints language in `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py` so non-astrology users can understand the panel.
- Repeatation UI version advanced to:
  `repeatation_ui_20260521_plain_traits_v18`.
- Numeric trait labels now show actual values and bucket meaning, for example:
  `Aspect distance from exact: 51.36 (middle)`.
- Numeric rows also show cutoff lines where available:
  `Value 51.36 | low <= 45.00 | high >= 75.00`.
- Jargon was softened:
  `event orb deg` -> `Aspect distance from exact`;
  `strict drik` -> `Aspect pressure strength`;
  `strict saptavargaja` -> `Multi-chart planet strength`;
  `strict kaala` -> `Timing strength`;
  `strict chesta` -> `Motion strength`;
  `shadbala total` -> `Total planet strength`.
- Tag explanations were simplified:
  `direction linked` now means this clue has repeatedly leaned one way and is at least 8 pips away from the group average.
- Trait guide language was simplified and now includes numeric examples.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_201252`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_plain_traits_v18`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_plain_traits_v18`
- Trait guide URL:
  `http://localhost:8765/trait_guide.html?v=repeatation_ui_20260521_plain_traits_v18`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, chart HTTP `200`, plain-language/numeric content check, and trait guide HTTP `200`.

2026-05-21 repeatation trait guide v17:

- Improved the ML trait hints panel in `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260521_trait_guide_v17`.
- Each trait row now includes a short inline explanation and browser tooltip.
- Added an `Open trait guide` link in the marker drawer that opens:
  `trait_guide.html`
  in a separate tab/window.
- The guide explains review terms such as:
  `event orb deg low/mid/high`, `direction linked`, `rare`, `common`, `only bullish samples`,
  `only bearish samples`, `x/y repeatations`, `pips vs group`, `active regime count`,
  strict Drik, Saptavargaja, Kaala, Chesta, TN/base TN score, and touch planets.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_195842`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_trait_guide_v17`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_trait_guide_v17`
- Trait guide URL:
  `http://localhost:8765/trait_guide.html?v=repeatation_ui_20260521_trait_guide_v17`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, chart HTTP `200`, and trait guide HTTP `200`.

2026-05-21 full Shadbala component v1 expansion:

- Expanded `C:\Users\ADMIN\PycharmProjects\strict_shadbala_doctrine.py` from the strict Drik foundation into `STRICT_SHADBALA_V3_FULL_COMPONENT_V1`.
- Implemented Saptavargaja Bala over D1/D2/D3/D7/D9/D12/D30 using compound temporary + natural relationship scoring, with per-varga detail JSON.
- Implemented Ojayugma Bala using odd/even Rashi and Navamsa logic.
- Added explicit Kaala Bala v1 subcomponents:
  Nathonnatha, Paksha, Tribhaga, Abda, Masa, Vara, Hora, Ayana, and Yuddha.
- Added Chesta Bala speed-state v1 for non-luminary classical planets.
- Added Graha Yuddha detector for Mars/Mercury/Jupiter/Venus/Saturn within 1 degree, using ecliptic latitude as the v1 tie-breaker where available.
- Kept Rahu/Ketu out of Shadbala totals as proxy shadow nodes. `AVG(ALL)` remains a seven-classical-planet component-wise mean, not a node/outer-planet average.
- `build_aspect_sr_touch_log.py` now passes Swiss Ephemeris speed, latitude, declination, timestamp, and Tokyo longitude into strict Shadbala context.
- `doctrine_config.yaml` / `doctrine_config.py` now document the v16 decisions:
  seven-classical `AVG(ALL)`, Saptavargaja compound relationship policy, deterministic Abda/Masa epoch-day policy pending cross-validation, speed-state Chesta v1, and Yuddha within-1-degree policy.
- `aspect_annotation_store.py` now preserves the new strict Shadbala context fields in case JSON.
- `build_repeatation_review_pack.py` advanced to:
  `repeatation_ui_20260521_full_shadbala_v16`
  and now includes strict Saptavargaja, Ojayugma, Kaala, Chesta, Yuddha, rule IDs, and validation-gap tokens in ML trait hints.
- `sr_touch_lazy_dashboard.py` hover/detail lines now show compact:
  Drik, Saptavargaja, Kaala, Chesta, v1 total, ratio, and status.
- Added doctrine regression tests:
  `C:\Users\ADMIN\PycharmProjects\test_strict_shadbala_doctrine.py`
  covering Drik formula checkpoints, Navamsa/Ojayugma, Saptavargaja detail shape, Nathonnatha local mean time, Chesta/Yuddha decisions, and `AVG(ALL)` context output.
- Rebuilt canonical Raman touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  with `656` rows.
- Refreshed `gann_aspect_annotations.sqlite`; no new case IDs inserted.
- Exported fresh v16-aware full-year switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_165758.html`
  and CSV:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_165758.csv`
  with `732` visible rows.
- Rebuilt scored candidates:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  and `.parquet`, with `732` rows, `WIN=402`, `LOSS=327`, `IGNORE=3`.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_165838`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_full_shadbala_v16`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_full_shadbala_v16`
- Verification passed:
  Python compile, `python test_strict_shadbala_doctrine.py`, smoke touch-log build, full touch-log regeneration, DB context refresh,
  switch export, candidate rebuild, repeatation pack rebuild/sync, localhost HTTP `200`, and served chart content check for v16 strict Shadbala hover text.

2026-05-21 strict Drik Bala / Shadbala v2 foundation:

- Added `C:\Users\ADMIN\PycharmProjects\strict_shadbala_doctrine.py`.
- Implemented strict formula-foundation Drik Bala using the six Sripati/Parasara aspect-strength formula segments:
  no aspect under 30 degrees or over 300 degrees forward, base strength over the 30-300 degree range,
  and special exact aspect bonuses for Jupiter `120/240`, Saturn `60/270`, and Mars `90/210`.
- Drik Bala is signed by natural benefic/malefic policy:
  Jupiter/Venus/Mercury and waxing Moon positive, Sun/Mars/Saturn and waning Moon negative.
- Added event-chart partial Shadbala v2 components for classical planets:
  Naisargika Bala, Uchcha Bala, Kendradi Bala, Drekkana Bala, Dig Bala, and strict Drik Bala.
- Added explicit non-fake status:
  `partial_high_confidence_components_pending_saptavargaja_kaala_chesta_yuddha`.
  Pending pieces remain visible as missing components: Saptavargaja, Ojayugma, full Kaala Bala, Chesta Bala, and Yuddha Bala.
- `doctrine_config.yaml` / `doctrine_config.py` now advertise:
  `shadbala.method=strict_shadbala_v2_partial_components`,
  `drik_bala.method=parashara_sripati_six_formula_signed`,
  and `PARASHARA_SRIPATI_DRIK_BALA_SIX_FORMULA_V1`.
- `build_aspect_sr_touch_log.py` now computes strict Drik/Shadbala event context at the event best-aspect time using the Raman sidereal longitudes and Tokyo reference event houses.
- `aspect_annotation_store.py` context columns were extended for strict Shadbala/Drik fields.
- `build_repeatation_review_pack.py` now includes strict dignity, strict Drik, and partial Shadbala totals in ML trait hints.
  Repeatation UI version advanced to:
  `repeatation_ui_20260521_strict_shadbala_v15`.
- `sr_touch_lazy_dashboard.py` now shows compact strict Shadbala hover/detail text.
- Regenerated the Raman touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  with `656` rows and `656` unique events.
- Re-imported cases into `gann_aspect_annotations.sqlite`; no new cases inserted, existing contexts refreshed.
- Exported fresh strict-Shadbala-aware full-year switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_162717.html`
  and CSV:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_162717.csv`
  with `732` visible rows.
- Rebuilt scored candidates:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  and `.parquet`, with `732` rows, `WIN=402`, `LOSS=327`, `IGNORE=3`.
- Rebuilt and synced the AVG(ALL)|MOON square repeatation pack into:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_strict_shadbala_v15`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_strict_shadbala_v15`
- Verification passed:
  Python compile, strict Drik formula sanity check, slice smoke build, full regeneration, DB context check for case 8,
  localhost HTTP `200`, and in-app browser direct chart check for strict Shadbala hover content.

2026-05-21 Panchanga doctrine foundation:

- Added `C:\Users\ADMIN\PycharmProjects\panchanga_doctrine.py`.
- Panchanga is now computed deterministically from Raman sidereal Sun/Moon longitude at the event best-aspect moment, plus event start/end change flags.
- New touch-log/context fields include:
  `event_weekday`, `event_weekday_lord`, `event_tithi_name`, `event_paksha`, `event_karana_name`,
  `event_yoga_name`, `event_moon_nakshatra`, `event_moon_pada`, `event_sun_nakshatra`, `event_sun_pada`,
  `event_near_new_moon_flag`, `event_near_full_moon_flag`, and tithi/karana/yoga/nakshatra change flags.
- `doctrine_config.yaml` and `doctrine_config.py` now expose `panchanga.method=deterministic_sidereal_sun_moon`,
  `panchanga.status=formula_foundation_pending_traditional_validation`, and `PANCHANGA_SIDEREAL_SUN_MOON_V1`.
- `aspect_annotation_store.py` now refreshes existing case `context_json` on import while preserving case IDs and annotations. This prevents stale case context after doctrine-field additions.
- `build_repeatation_review_pack.py` now includes Panchanga fields in ML trait hints. Repeatation UI version advanced to:
  `repeatation_ui_20260521_panchanga_v14`.
- `sr_touch_lazy_dashboard.py` now displays compact Panchanga lines in event hover/detail text.
- Regenerated the Raman touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  with `656` rows and `656` unique events.
- Re-imported the touch log into `gann_aspect_annotations.sqlite`; no new cases inserted, but all existing case contexts were refreshed with Panchanga fields.
- Rebuilt and synced the AVG(ALL)|MOON square repeatation pack into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_panchanga_v14`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_panchanga_v14`
- Browser smoke check verified the direct chart contains Panchanga hover data and Panchanga ML trait tokens.
- Exported fresh Panchanga-aware full-year switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_122019.html`
  and CSV:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_122019.csv`
  with `732` visible rows.
- Rebuilt scored candidates from the fresh switch CSV:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  and `.parquet`, with `732` rows, `WIN=402`, `LOSS=327`, `IGNORE=3`.

2026-05-21 astro function / web research audit:

- Added `C:\Users\ADMIN\PycharmProjects\astro_function_research_audit_20260521.md`.
- The audit reviewed current Python astro functionality against local PDF extracts and web sources:
  Swiss Ephemeris programmer docs, PySwisseph package reference, Shadbala overview cross-check, Panchanga references, Tithi definition, and Gann/financial astrology feature references.
- Current implementation assessment:
  - strong foundation: sidereal transit/event pipeline, graha/rashi aspects, SR/Gann-style planetary lines, JPY/USD reference scoring, repeatation marker UI, ML trait hints, and doctrine metadata;
  - proxy fields: BPHS-like orb strength is useful but not strict Drik Bala; current Shadbala is still minimum-threshold/basic-Sthana foundation only;
  - duplicate risk: `build_trade_candidates_from_touches.py` still has its own dignity tables and should be unified through `shadbala_doctrine.py`.
- Key missing doctrine/features before serious ML training:
  1. lock ayanamsa/node/house policy in `doctrine_config.yaml`;
  2. unify dignity logic through `shadbala_doctrine.py`;
  3. add Panchanga core: tithi, paksha, vara, nakshatra/pada, yoga, karana;
  4. rebuild candidates with doctrine metadata;
  5. add purged/embargoed walk-forward validation;
  6. later add full Shadbala, strict Drik Bala, combustion/station/speed, functional benefic/malefic, Vargas, Dasha, and Gann scale/harmonic variants.
- User chose Raman ayanamsa as personal doctrine preference after the audit.
- `doctrine_config.yaml` now locks:
  - `ayanamsa: Raman`
  - `ayanamsa_swiss_ephemeris_id: SIDM_RAMAN`
  - `node_type: true_node`
- `doctrine_config.py` now exposes `configure_swiss_ephemeris_sidereal()`, which applies `swe.set_sid_mode(swe.SIDM_RAMAN)`.
- Raman sidereal mode is now applied in the core rebuild/export scripts:
  `build_aspect_sr_touch_log.py`, `sr_touch_lazy_dashboard.py`, `build_pair_aspect_market_log.py`,
  `build_sr_anchor_reversal_log.py`, `generate_sr_candidate_chart_pack.py`, `sr_lazy_reactive_dashboard.py`,
  and `rebuild_dataset_mt5_ipo_allpairs.py`.
- The Rahu/Ketu branch in `build_aspect_sr_touch_log.py` now avoids double sidereal correction by calculating the true node tropically and then applying the configured Raman ayanamsa correction once.
- Important implication: future serious ML training should regenerate the event dataset, touch log, candidates, annotation context, and repeatation review pack under `doctrine_ayanamsa=Raman`. Do not silently mix old default/Lahiri-style artifacts with Raman-derived features.

2026-05-21 Raman artifact regeneration:

- Regenerated the event source under the Raman doctrine lock with:
  `python rebuild_dataset_mt5_ipo_allpairs.py --ticker USDJPY --interval 1h --start-date 2025-03-01 --end-date 2026-03-10 --future-end-date 2026-04-10 --analysis-mode natal --reference-chart-type ipo --coordinate-system geo --astrology-method sidereal --aspect-mode orb --ipo-date 1889-02-11 --ipo-time 00:00 --hq-city Tokyo --hq-country Japan --output-file C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet --price-parquet C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet`
- The Raman event dataset now has `804` rows, date range `2025-03-01 00:30:00+05:30 -> 2026-03-09 14:30:00+05:30`, aspect counts `square=274`, `trine=252`, `opposition_orb=142`, `conjunction_orb=136`.
- Backed up pre-Raman generated artifacts to:
  `C:\Users\ADMIN\PycharmProjects\generated_artifact_backups\pre_raman_regen_20260521-110658`.
- Rebuilt the canonical all-duration transitsign touch log from the Raman event dataset:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  with `656` rows and `656` unique `event_id` values. Its doctrine metadata is `doctrine_ayanamsa=Raman`, `doctrine_ayanamsa_swiss_ephemeris_id=SIDM_RAMAN`, `doctrine_node_type=true_node`.
- Reset/re-imported `gann_aspect_annotations.sqlite` from the Raman touch log because the old case table would mix doctrines. There were no saved trade/rule annotations in the DB before reset. New case count: `656`.
- Exported fresh Raman switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_111526.html`
  and CSV:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_111526.csv`
  with `1078` visible rows.
- Rebuilt scored candidates from the Raman switch CSV:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  and `.parquet`, with `1078` rows, `1078` potential trades, `4` ignored, `WIN=582`, `LOSS=492`, `IGNORE=4`.
- Fixed `build_trade_candidates_from_touches.py` so raw touch logs missing `zone_kind` / `touch_kind` no longer crash on string fallback. Candidate scoring should still use the switch CSV when trade direction labels are needed.
- The AVG(ALL)|MOON square family shifted under Raman from old seed `case_id=11` / old selected `case_id=120` to new seed `case_id=8`; repeatation count is now `16`.
- Rebuilt the Raman repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_111637`.
- Synced the Raman pack into the currently served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`
  after clearing stale old case files.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260520_traits_v12_raman`
- Direct first Raman case URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260520_traits_v12_raman`
- The old direct URL `aspect_review_case_120_chart.html` now contains a local redirect note to the updated reviewer so the browser does not show stale pre-Raman content.

2026-05-21 repeatation outcome default fix:

- User observed case 8 live trade result/callout still showed `bullish` while `ML trait hints` correctly showed bearish behavior.
- Root cause: marker drawer `Outcome` selector had a hardcoded `bullish` default, and old autosaved drafts could preserve that default even when the case full-window direction was bearish.
- `build_repeatation_review_pack.py` now injects `defaultOutcome` into each chart's marker UI metadata based on `full_window_direction`.
- Initial outcome now defaults to the recurrence's full-window direction (`bullish` or `bearish`; otherwise `unclear`) while still allowing manual override.
- Draft schema advanced to version `2` with `outcome_touched`; old version-1 drafts that only inherited the hardcoded bullish default are migrated to the case default when the case default is not bullish.
- `Clear saved draft` now resets to case default outcome instead of hardcoded bullish.
- Repeatation UI version advanced to:
  `repeatation_ui_20260521_outcome_default_v13`
- Rebuilt and re-synced the Raman AVG(ALL)|MOON square review pack into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Verified served `aspect_review_case_8_chart.html` contains `defaultOutcome: "bearish"`, `outcomeTouched`, and v13 cache links; reviewer URL returned HTTP `200`.
- Current reviewer URL after this fix:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_outcome_default_v13`

2026-05-21 doctrine hardening foundation:

- Added `C:\Users\ADMIN\PycharmProjects\doctrine_config.yaml`.
- Added `C:\Users\ADMIN\PycharmProjects\doctrine_config.py`.
- Future generated touch logs / trade candidates / dashboard exports now carry doctrine metadata columns including `doctrine_config_id`, `doctrine_drishti_status`, `doctrine_shadbala_method`, `doctrine_rule_citation_status`, and `experimental_layer_flags`.
- Current BPHS strength fields are preserved for compatibility, but explicit proxy aliases were added: `event_bphs_like_orb_strength`, `event_bphs_like_orb_virupa`, and `event_strength_doctrine_status=bphs_like_orb_proxy_not_full_drik_bala`.
- Shadbala tags/averages now carry `shadbala_doctrine_status=source_or_proxy_pending_full_six_bala_calculation`.
- Added seven-classical-planet minimum Shadbala total virupa thresholds from the Shadbala PDF text extraction: Sun 300, Moon 360, Mars 300, Mercury 420, Jupiter 390, Venus 330, Saturn 300. Future rows with `b1`, `b2`, and `shadbala_avg` get `event_shadbala_minimum_total_virupa_avg` and `event_shadbala_avg_minus_minimum_virupa`.
- `astro_feature_inventory_from_pdfs.md` and `vedic_pdf_alignment_review_20260520.md` were updated so LOCK_DOCTRINE_CONFIG is no longer marked as completely missing.
- Smoke checks passed: `python -m py_compile doctrine_config.py build_aspect_sr_touch_log.py build_trade_candidates_from_touches.py sr_touch_lazy_dashboard.py aspect_annotation_store.py`; metadata append tested against the current touch log.

2026-05-21 Shadbala doctrine foundation:

- Added `C:\Users\ADMIN\PycharmProjects\shadbala_doctrine.py`.
- The module defines source-cited Shadbala/Sthana constants:
  - `SHADBALA_MINIMUM_TOTAL_VIRUPA`: Sun 300, Moon 360, Mars 300, Mercury 420, Jupiter 390, Venus 330, Saturn 300.
  - basic Sthana sign dignity rules: exaltation, moolatrikona, own, friend, neutral, enemy, debilitation.
  - rule IDs: `STHANA_SIGN_DIGNITY_V1`, `SHADBALA_MIN_TOTAL_GATE`.
- `build_aspect_sr_touch_log.py` now computes event best-time signs and adds event-level Sthana/minimum fields when logs are regenerated:
  - `event_b1_sign`, `event_b1_sthana_dignity_label`, `event_b1_sthana_dignity_virupa`, `event_b1_sign_relation`, `event_b1_shadbala_minimum_total_virupa`
  - matching `event_b2_*` fields
  - `event_sthana_dignity_virupa_avg`, `event_shadbala_minimum_total_virupa_avg`, `event_sthana_rule_ids`, `event_doctrine_feature_status`
- `build_repeatation_review_pack.py` now appends doctrine metadata while building ML trait hints, so existing touch logs can at least expose Shadbala status/minimum metadata and future regenerated logs will expose event dignity traits too.
- `aspect_annotation_store.py` context columns were extended for the new doctrine fields.
- Compile and smoke tests passed; server still returned HTTP 200.

2026-05-21 doctrine data regeneration:

- Regenerated the canonical all-duration transitsign touch log with the Shadbala/Sthana doctrine fields:

```powershell
python C:\Users\ADMIN\PycharmProjects\build_aspect_sr_touch_log.py `
  --events C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet `
  --price C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet `
  --include-natal `
  --aspect-mode orb `
  --max-event-days 0 `
  --output C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv
```

- Rebuild output stayed stable at `619` rows and `619` unique `event_id` values.
- New columns verified present in the touch log and case 120 visible chart CSV:
  `doctrine_config_id`, `event_b1_sthana_dignity_label`, `event_b2_sthana_dignity_label`,
  `event_sthana_dignity_virupa_avg`, `event_shadbala_minimum_total_virupa_avg`,
  `event_doctrine_feature_status`.
- Re-imported the regenerated touch log into `gann_aspect_annotations.sqlite`; no new case IDs were inserted, preserving existing case numbering.
- Rebuilt the case 11 `AVG(ALL)|MOON square` repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_20260521_102109`.
- Synced that rebuilt pack into the currently served folder so the existing browser URL keeps working:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Server verification: `http://127.0.0.1:8765/aspect_review_case_120_chart.html?v=repeatation_ui_20260520_traits_v12_doctrine` returned HTTP `200`, and the served HTML contains the new trait UI tokens.

The repeatation review UI is now at:

```text
repeatation_ui_20260520_traits_v12
```

Latest verified local URL:

```text
http://localhost:8765/aspect_review_case_120_chart.html?v=repeatation_ui_20260520_traits_v12
```

Active local server:

```text
python serve_repeatation_pack.py
http://127.0.0.1:8765/
```

Recent pushed commits:

```text
616908d Add repeatation trait hints
8aff6a0 Add repeatation auto suggest markers
582503c Move repeatation profit callout
6075b55 Add live repeatation trade profit
e877261 Use plus repeatation markers
c32f499 Disarm repeatation marker tools
bf51cb7 Capture and drag repeatation markers
c1a3ca4 Make repeatation marker selection magnetic
```

Latest feature state:

- Marker drawer supports repeatation navigation, draggable plus-style trade/ignore markers, ignore trade signal types, live P/L, auto-suggested start/end, and manual override tracking.
- Auto Suggest places trade start at the first selected-case hardcoded marker and trade end at the next subsequent hardcoded marker when available.
- `ML trait hints` compare a repeatation against its same unique case group and highlight rare/common/direction-linked traits from Shadbala tags, signs/houses, BPHS-like fields, active regimes, and edge-score buckets.
- Plotly Pan is the intended default interaction mode so marker placement does not fight zoom/pan tools.

PDF alignment review added:

```text
C:\Users\ADMIN\PycharmProjects\vedic_pdf_alignment_review_20260520.md
```

Conclusion from the PDF check: current scripts follow the uploaded strict-engine architecture, but current BPHS/Shadbala fields are still simplified proxies. Full Shadbala, exact Drik Bala, doctrine config, rule citations, RAG/local LLM explanation layer, and purged walk-forward validation remain pending.

## Project Goal

Build a deterministic financial astrology research pipeline for USDJPY that:

1. Computes aspect/SR touch events using a Japanese Yen reference chart.
2. Splits chart views by timeframe:
   - M30 for short aspects `<= 24h`
   - H1 for all aspect durations
   - Daily for longer aspects `> 24h`
   - Daily hides Moon SR planetary lines
3. Adds transparent rule-layer hypothesis scores before ML.
4. Later uses ML to validate/calibrate those hypothesis scores with walk-forward validation.

## Git State

Repo:

`C:\Users\ADMIN\PycharmProjects`

Git executable:

`C:\Program Files\Git\cmd\git.exe`

Latest commits at the 2026-05-24 handoff cleanup:

```text
121ed63 Align local ML drafts with auto suggest evidence
dfac27b Add local ML reason draft button
5ca777a Configure portable Ollama local model
60fd655 Record Telegram relay heartbeat
5ec5b39 Add Telegram relay inbox for Codex
fa46c4e Record LLM options and Telegram test
153fbb6 Add local jyotish RAG agent CLI
9897b21 Show ML notes and scaffold jyotish agent
```

Git user email is repo-local:

`gourav.damade@gmail.com`

## Important Scripts

Tracked in Git:

- `build_aspect_sr_touch_log.py`
- `sr_touch_lazy_dashboard.py`
- `build_trade_candidates_from_touches.py`
- `astro_feature_inventory_from_pdfs.md`
- `astro_feature_inventory_from_pdfs.yaml`
- `financial_astrology_source_notes_2026-03-13.md`

## Reference Chart

The quote/reference chart is the Japanese Yen/Tokyo IPO style reference:

```text
ipo-date: 1889-02-11
ipo-time: 00:00
reference-tz: Asia/Tokyo
reference-lat: 35.6762
reference-lon: 139.6503
```

This is used by `build_aspect_sr_touch_log.py` for transit-to-natal fields such as:

- `tn_hits_json`
- `tn_primary_*`
- `tn_bphs_total`
- `touch_planet_*_natal_*`

The base/reference chart added on 2026-05-05 is the USD birth reference supplied by the user:

```text
base-reference-label: USD
base-reference-date: 1776-07-04
base-reference-time: 12:00
base-reference-tz: America/New_York
base-reference-lat: 39.9526
base-reference-lon: -75.1652
```

This is implemented as additional `base_tn_*` fields. The pair hypothesis is:

```text
USDJPY score = USD reference score - JPY reference score
```

## Current Data Files

Generated/ignored by Git:

```text
C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst.csv
C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote.csv
C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations.csv
C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet
C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored.parquet
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote.parquet
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.parquet
C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet
```

Latest chart export with score hovers:

```text
C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.html
C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.csv
```

M30 data download:

```text
rows: 12429
range UTC: 2025-03-10 00:00 to 2026-03-10 23:30
interval: 30 minutes
```

## Major Completed Changes

### Uranus/Neptune SR Lines

Added Uranus and Neptune planetary SR lines without adding Uranus/Neptune to planetary aspects.

Validation at the time:

```text
raw touch log rows: 604
max rows per event: 1
uranus touch rows: 76
neptune touch rows: 58
uranus aspect pair rows: 0
neptune aspect pair rows: 0
```

### Timeframe Modes

`sr_touch_lazy_dashboard.py` supports:

```text
--timeframe m30
--timeframe hourly
--timeframe daily
--timeframe merged
--timeframe switch
```

Behavior:

- `m30`: real M30 candles required; short aspects `<= 24h`; Moon lines included.
- `hourly`: H1 candles; all aspect durations; Moon lines included.
- `daily`: daily candles; long aspects `> 24h`; Moon SR lines hidden and Moon SR touch rows excluded.
- `merged`: H1 candles; all aspect durations together; Moon lines included.
- `switch`: one HTML with buttons. If M30 price file is supplied, buttons are M30/H1/Daily.

Latest switch validation:

```text
M30:    403 rows, 60-1440 minutes, context/slow excluded rows 0
Hourly: 506 rows, 60-42720 minutes, context/slow excluded rows 0
Daily:   96 rows, 1500-102180 minutes, context/slow excluded rows 3
USDJPY hypothesis hover rows: 1005/1005
Doctrine hypothesis hover rows: 1005/1005
```

### Event Duration Cap

Builder duration cap:

- `build_aspect_sr_touch_log.py`: `--max-event-days`, default `5.0`
- Use `--max-event-days 0` to disable the cap and include all durations available in the event source.
- `sr_touch_lazy_dashboard.py` no longer applies its own hard 5-day loader cap.

Weekly mode requires making this configurable end-to-end before adding `> 5d` weekly buckets.

### Rule-Layer Scoring

`build_trade_candidates_from_touches.py` and `sr_touch_lazy_dashboard.py` now compute a first heuristic score using the Yen IPO reference chart.

Added fields include:

- `aspect_family`
- `duration_bucket`
- `active_hard_aspect_count`
- `active_soft_aspect_count`
- `has_moon_trigger`
- `has_outer_or_node`
- `sr_confirmation_score`
- `jyotish_bullish_score`
- `jyotish_bearish_score`
- `jyotish_net_score`
- `jyotish_conflict_score`
- `jyotish_hypothesis_direction`
- `dominant_aspect_id`
- `dominant_aspect_abs_score`
- `rule_layer_total_strength`
- `rule_layer_conflict_ratio`
- `rule_layer_notes`

Notes field:

```text
heuristic_v1_yen_ipo_tokyo_1889_reference;
uses_transit_natal_house_planet_nature_aspect_family_bphs_sr;
fx_pair_score_is_base_minus_quote_when_base_reference_fields_exist;
ml_must_validate
```

Latest rough sanity summary from scored candidates:

```text
BULLISH hypothesis: 417 rows, win rate about 53.0%
BEARISH hypothesis: 429 rows, win rate about 48.3%
CONFLICT:           118 rows, win rate about 49.2%
```

Do not treat this as proof; M30 and H1 duplicate short-aspect rows in switch exports, and purged walk-forward validation is still needed.

### Chart Hover Details

Latest chart hover now shows the score block on both interaction markers and shaded aspect windows:

```text
Rule-layer hypothesis
Reference chart: Yen IPO Tokyo 1889-02-11 00:00 Asia/Tokyo
Source ref in row: 1889-02-11 00:00:00+09:00 Asia/Tokyo
Hypothesis: BEARISH/BULLISH/CONFLICT
Scores B/Bear/Net/Conflict
Dominant hit
Dominant strength
Rule total strength
Conflict ratio
Aspect family / duration
Active hard/soft
Note: heuristic v1; ML must validate weights.
```

Cluster cache version in `sr_touch_lazy_dashboard.py` is `_clustered_v7.parquet`.

Update on 2026-05-05:

- `build_aspect_sr_touch_log.py` now supports base/quote reference labels and USD base-reference CLI options.
- Default USD base reference is `1776-07-04 12:00 America/New_York`, Philadelphia lat/lon.
- `build_trade_candidates_from_touches.py` adds `score_currency_pair_for_row`.
- `sr_touch_lazy_dashboard.py` adds `FX pair hypothesis` hover lines and `fx_*` export columns.
- Dashboard clustered cache version is now `_clustered_v8.parquet`.
- Older touch logs without `base_tn_hits_json` intentionally show `fx_hypothesis_direction=UNKNOWN` with `base_reference_missing;pair_hypothesis_not_scored`.
- Syntax check passed:
  `python -m py_compile build_aspect_sr_touch_log.py build_trade_candidates_from_touches.py sr_touch_lazy_dashboard.py`
- Smoke load passed on `aspect_sr_touch_log_72h_smoke.csv`: 1854 rows, all old rows `UNKNOWN` for FX pair scoring.
- Synthetic row with both USD and JPY hits produced `BULLISH` with positive `fx_pair_net_score`.

Regenerated artifact update on 2026-05-05:

- New touch log with USD base-reference fields:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote.csv`
- Builder command used `--include-natal --aspect-mode orb --max-event-days 5`.
- Output rows: 604.
- Base reference printed by builder:
  `1776-07-04 12:00 America/New_York -> 1776-07-04 22:26:02 Asia/Kolkata`.
- Validation:
  `base_tn_hits_json` present, `base_hits_nonempty=603/604`.
- Fresh switch chart with FX hover block:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260505_230311.html`
- Chart CSV rows: 964; M30 424, H1 424, Daily 116.
- `FX pair hypothesis` hover block rows: 964/964.
- FX direction counts in chart CSV:
  `BULLISH=403`, `BEARISH=331`, `CONFLICT=118`, `UNKNOWN=112`.
- Rebuilt candidates:
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote.csv`
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote.parquet`
- Quick non-purged sanity result, not proof:
  `BEARISH win_rate=52.57%`, `BULLISH win_rate=46.65%`, `CONFLICT win_rate=54.24%`, `UNKNOWN win_rate=53.57%`.
- Initial read: base-minus-quote score is now implemented and visible, but the naive directional mapping still needs ML/purged walk-forward validation and may need inversion/reweighting.

Timeframe split update on 2026-05-06:

- User requested: M30 `<=24h`, Hourly all aspects including `>24h`, Daily only `>24h`, Daily no Moon planetary SR lines.
- `sr_touch_lazy_dashboard.py` now implements that split.
- Daily also excludes marker rows whose SR touch identity contains Moon, so hidden Moon lines do not still appear as daily marker explanations.
- `build_aspect_sr_touch_log.py` accepts `--max-event-days 0` for uncapped event duration generation.
- New uncapped base/quote touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations.csv`
- Builder command used `--include-natal --aspect-mode orb --max-event-days 0`.
- Output rows: 619.
- Latest switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260506_214025.html`
- Latest switch CSV validation:
  `M30=416 rows, 60-1440 min, >24h=0`;
  `Hourly=520 rows, 60-42720 min, >24h=106`;
  `Daily=96 rows, 1500-102180 min, Moon SR identity rows=0`;
  `FX pair hypothesis hover rows=1032/1032`.
- Rebuilt all-duration candidates:
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.csv`
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.parquet`
- Quick non-purged FX sanity result:
  `BEARISH win_rate=53.54%`, `BULLISH win_rate=46.93%`, `CONFLICT win_rate=53.47%`, `UNKNOWN win_rate=55.47%`.

Active regime-zone update on 2026-05-06:

- `sr_touch_lazy_dashboard.py` now draws a separate active-regime zone layer.
- Regime zones split overlapping event windows at every event start/end boundary.
- Example behavior:
  event X `22/03-25/03` and event Y `24/03-28/03` become:
  `22/03-24/03 X only`, `24/03-25/03 X+Y`, `25/03-28/03 Y only`.
- Each regime zone has its own hover:
  active event list, active count, combined JPY hypothesis, combined JPY scores, zone dominant hit/event/strength, combined FX hypothesis, FX base/quote/net/conflict, FX dominant event/base-hit/quote-hit.
- Latest chart with regime zones:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260506_225211.html`
- Validation from in-memory figures:
  `M30 regime zones=514, overlap zones=156`;
  `Hourly regime zones=916, overlap zones=667`;
  `Daily regime zones=193, overlap zones=137`.
- Latest CSV still contains the 1032 touch rows; regime zones are rendered into the HTML chart layer, not exported as separate CSV rows yet.

Hover simplification update on 2026-05-07:

- Default hovers now show the USDJPY/FX hypothesis only.
- Quote/JPY-only diagnostics are hidden from the default hover because a bullish JPY quote signal usually implies USDJPY bearish unless USD strength offsets it.
- Hovers now show `Click for quote/JPY details`.
- The exported HTML includes a click details panel below the chart. Clicking an event, marker, or active regime zone fills that panel with quote/JPY diagnostics.
- Clustered touch cache version is now `_clustered_v10.parquet` to force regenerated marker hover text.
- Latest chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260507_003720.html`
- Validation:
  CSV rows `1032`; `USDJPY hypothesis` hover rows `1032/1032`; old `Rule-layer hypothesis` rows `0`; visible `Quote/JPY hypothesis` hover rows `0`.

Short-term slow/context-pair exclusion update on 2026-05-08:

- M30 and Hourly now exclude aspect events where both bodies are in:
  `JUPITER`, `SATURN`, `URANUS`, `NEPTUNE`, `PLUTO`.
- M30 and Hourly also exclude `AVG(ALL)`, `RAHU`, or `KETU` paired with those slow bodies.
- Rationale: slow-planet-only combinations should not drive short-term M30/H1 trend views.
- Daily and merged modes do not apply this short-term pair filter.
- Latest chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260508_041401.html`
- Latest switch CSV validation:
  `M30=403 rows, slow-slow/context-slow rows=0`;
  `Hourly=506 rows, slow-slow/context-slow rows=0`;
  `Daily=96 rows, slow-slow/context-slow rows=3`;
  `USDJPY hypothesis hover rows=1005/1005`.
- Candidate file rebuilt from latest chart CSV:
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.csv`
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.parquet`
- Quick non-purged FX sanity result:
  `BEARISH win_rate=53.16%`, `BULLISH win_rate=46.53%`, `CONFLICT win_rate=53.90%`, `UNKNOWN win_rate=54.33%`.

Doctrine dignity scoring update on 2026-05-09:

- Added separate doctrine-v1 score fields without replacing the legacy heuristic `fx_pair_*` fields.
- Doctrine-v1 applies sign dignity/friendship Sthana Bala style modifiers for the seven classical planets:
  exaltation `60V`, moolatrikona `45V`, own sign `30V`, friendly sign `15V`, neutral sign `10V`, enemy sign `4V`, debilitation `0V`.
- Rahu, Ketu, Uranus, Neptune, Pluto remain dignity `unknown` in v1 because sign ownership/exaltation varies by tradition or is not classical.
- Existing touch logs contain natal/reference sign in each hit, so the current chart uses natal/reference dignity. `build_aspect_sr_touch_log.py` now also writes `transit_lon`, `transit_sign`, and `natal_lon` into future hit JSONs when a full touch-log rebuild is run.
- Dashboard clustered cache version is now `_clustered_v11.parquet`.
- Latest chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260509_051836.html`
- Latest switch CSV validation:
  `rows=1005`;
  `M30=403 rows, slow-slow/context-slow rows=0`;
  `Hourly=506 rows, slow-slow/context-slow rows=0`;
  `Daily=96 rows, slow-slow/context-slow rows=3`;
  `USDJPY hypothesis hover rows=1005/1005`;
  `Doctrine hypothesis hover rows=1005/1005`.
- Doctrine direction counts:
  `BULLISH=380`, `BEARISH=302`, `CONFLICT=196`, `UNKNOWN=127`.
- Candidate file rebuilt from latest chart CSV:
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.csv`
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.parquet`
- Quick non-purged doctrine sanity result:
  `BEARISH win_rate=52.32%`, `BULLISH win_rate=43.95%`, `CONFLICT win_rate=59.69%`, `UNKNOWN win_rate=54.33%`.
- Note: a full doctrine-v1 touch-log rebuild was attempted after laptop restarts but did not leave a complete new file. The likely cause, from the lost prior Gann thread, was heavy memory pressure during the full touch-log build, reportedly rising to about 10 GB before the laptop restarted/crashed. Current artifacts use the existing complete all-duration touch log plus the new scorer.
- Verified on 2026-05-10: `aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations.csv` still has no `transit_sign`, `transit_lon`, or `natal_lon` entries inside `tn_hits_json` / `base_tn_hits_json`. A stable-machine rebuild is still required before transit-sign dignity can be used from the touch log itself.

Transit-sign touch-log/candidate update on 2026-05-11:

- Validated transitsign touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
- Rows: `619`; unique event IDs: `619`; event-id set equals the old all-duration touch log.
- Hit JSON validation on the touch log:
  `9356` hits checked across `tn_hits_json` and `base_tn_hits_json`; missing `transit_lon`, `transit_sign`, or `natal_lon`: `0`.
- Latest transitsign switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.csv`
- Chart CSV rows: `1005`; chart hit JSON validation:
  `15241` hits checked; missing `transit_lon`, `transit_sign`, or `natal_lon`: `0`.
- Rebuilt transitsign candidates:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet`
- Candidate summary:
  rows `1005`; `potential_trade=1005`; `ignored=6`;
  categories `multiple_aspects=925`, `single_aspect=80`;
  close actions `TAKE_PROFIT=506`, `STOP_LOSS=486`, `TIME_CLOSE_72H=13`;
  ML outcomes `WIN=511`, `LOSS=488`, `IGNORE=6`.
- Doctrine direction counts after transit-sign dignity:
  `BULLISH=377`, `BEARISH=319`, `CONFLICT=182`, `UNKNOWN=127`.
- Compared with prior non-transitsign candidates by `chart_timeframe + touch_id`:
  doctrine pair net score changed on `769/1005` rows;
  base dignity average changed on `540/1005`;
  quote dignity average changed on `550/1005`;
  doctrine direction changed on `52/1005`.
  This confirms the scorer is consuming `transit_sign` from hit JSON, not only natal/reference sign dignity.

Purged walk-forward evaluation on 2026-05-11:

- Added evaluator:
  `C:\Users\ADMIN\PycharmProjects\evaluate_transitsign_walk_forward.py`
- Input:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet`
- Output directory:
  `C:\Users\ADMIN\PycharmProjects\walk_forward_eval_transitsign_20260511`
- Files:
  `summary.json`, `model_summary.csv`, `fold_metrics.csv`, `predictions.csv`
- Setup:
  `999` WIN/LOSS rows used; `5` expanding chronological folds; training rows purged if their `72h` close time overlaps the test fold start; future/outcome columns excluded, including `close_after72`, `ret_after_72h_pct`, exit fields, `ml_outcome`, and source `delta_1d/3d/7d`.
- Feature set after leakage exclusions:
  `179` numeric features and `46` categorical features.
- Best simple ML result:
  `random_forest_balanced` accuracy `54.33%`, balanced accuracy `53.94%`, win precision `55.97%`, win recall `59.32%`.
- Other baselines:
  `logistic_l2_balanced` accuracy `53.00%`, balanced accuracy `51.53%`;
  `dummy_most_frequent` balanced accuracy `50.00%`.
- Raw rule direction win rates on WIN/LOSS rows:
  legacy FX `BULLISH=47.01%`, `BEARISH=53.47%`, `CONFLICT=53.90%`, `UNKNOWN=54.33%`;
  doctrine FX `BULLISH=45.31%`, `BEARISH=53.00%`, `CONFLICT=57.69%`, `UNKNOWN=54.33%`.
- Read:
  The transit-sign doctrine score is not directly usable as a standalone directional signal yet. Treat it as a feature for calibration; inversion, thresholding, and blending should be tested in the purged walk-forward framework before trusting direction labels.

AVG(ALL) 7-classical scoring experiment on 2026-05-11:

- Implemented in:
  `C:\Users\ADMIN\PycharmProjects\build_trade_candidates_from_touches.py`
  and picked up by `sr_touch_lazy_dashboard.py` through its imported scoring functions.
- Rule:
  when a scored event body is `AVG(ALL)`, scoped hit matching expands it to the seven classical bodies:
  `SUN`, `MOON`, `MERCURY`, `VENUS`, `MARS`, `JUPITER`, `SATURN`.
- Rationale:
  `AVG(ALL)` is an artificial basket and should not be assigned a fixed benefic/malefic nature. Expansion lets member-planet transit-natal hits explain the regime instead of showing `n/a`.
- New chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_220046.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_220046.csv`
- New candidate variant:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign_avg7classical.csv`
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign_avg7classical.parquet`
- Targeted screenshot case:
  `AVG(ALL)|MARS trine`, 2025-04-01 to 2025-04-07, changed from `UNKNOWN/n/a` to:
  `BEARISH`, pair net `-1.235`, dominant USD `SATURN>AVG(ALL):square`, dominant JPY `SATURN>SATURN:trine`.
- Coverage comparison vs prior transitsign candidates:
  base dominant blank `393 -> 320`, quote dominant blank `432 -> 338`;
  `fx_pair_net_score` changed on `228/1005` rows;
  `fx_doctrine_pair_net_score` changed on `228/1005` rows;
  doctrine direction changed on `150/1005` rows.
- Direction counts:
  previous doctrine `BULLISH=377`, `BEARISH=319`, `CONFLICT=182`, `UNKNOWN=127`;
  avg7classical doctrine `BULLISH=389`, `BEARISH=360`, `CONFLICT=160`, `UNKNOWN=96`.
- Purged walk-forward output:
  `C:\Users\ADMIN\PycharmProjects\walk_forward_eval_transitsign_avg7classical_20260511`
- Purged walk-forward result:
  `random_forest_balanced` accuracy `48.33%`, balanced accuracy `48.41%`;
  `logistic_l2_balanced` accuracy `50.67%`, balanced accuracy `49.85%`;
  dummy baseline balanced accuracy `50.00%`.
- Rule direction win rates for avg7classical:
  legacy FX `BULLISH=48.36%`, `BEARISH=50.39%`, `CONFLICT=62.40%`, `UNKNOWN=51.04%`;
  doctrine FX `BULLISH=47.79%`, `BEARISH=50.00%`, `CONFLICT=61.88%`, `UNKNOWN=51.04%`.
- Read:
  The 7-classical expansion improves hover explainability and reduces `n/a`, but it did not improve simple purged walk-forward accuracy. Treat as experimental; use it for chart interpretation and as a candidate feature, not as a direct replacement for the prior transitsign scoring baseline.

Chart click-selection update on 2026-05-12:

- `sr_touch_lazy_dashboard.py` now lets the exported Plotly chart highlight the clicked event/regime interval.
- Clicking an aspect shaded window, active regime zone, touch result zone, normal marker, or selected star marker draws a bright yellow selection rectangle from the event/regime start to end across the whole chart height.
- The selection uses a layout shape named `selected-event-window`; each new click replaces the previous highlight.
- Purpose:
  make one specific aspect/regime interval easy to distinguish when multiple shaded windows overlap.
- Fresh chart export with this behavior:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_220048.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_220048.csv`
- CSV visible rows remained `1005`; this was a chart interaction/export change only, not a scoring rebuild.
- Follow-up fix after user reported the yellow click highlight was not visible/working:
  the exported chart now updates the selected interval on `plotly_hover` as well as click, uses a bright red border, red start/end vertical lines, and top annotations showing start/end date-time.
- Fresh chart export with red hover/click interval selection:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_222118.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_222118.csv`
- Second follow-up after user reported hover/click still did not work, and that
  "click for quote/JPY details" never worked on aspect shaded areas:
  `sr_touch_lazy_dashboard.py` now adds transparent click/hover hitbox traces above the candlesticks and planetary SR lines, but below the touch markers.
  This avoids top visual traces swallowing mouse events before the aspect/regime window can receive them.
- The browser script now unwraps nested Plotly `customdata` before reading details, so aspect-window clicks can populate the Quote/JPY details panel instead of losing the payload.
- Fresh chart export with hitbox interaction layer:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_224942.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_224942.csv`
- Follow-up on 2026-05-14 after user confirmed highlight works but was unsure
  whether details require single click/double click or only certain points:
  the browser script now remembers the most recent hovered event/regime payload.
  A normal single click within a short hover window locks/updates the Quote/JPY details panel from that remembered payload, so the user should hover until the red window appears, then single-click; no double-click is intended.
- Fresh chart export with hover-target + single-click details fallback:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_180116.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_180116.csv`
- Follow-up on 2026-05-14:
  user asked to disable double-click zoom/reset in the chart and reduce overlap for very short selected aspect windows.
  `sr_touch_lazy_dashboard.py` now writes Plotly HTML with `config={"doubleClick": False, "displaylogo": False}` for both single-timeframe and switch exports.
  Selected-window start/end labels now sit outward from the borders: start label offset left with right alignment, end label offset right with left alignment.
- Fresh chart export with double-click disabled and outward start/end labels:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_185353.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_185353.csv`
- Follow-up on 2026-05-14:
  user reported two interaction problems:
  hovering over markers still triggered selection, and shaded aspect areas without markers could not be selected.
  The browser script no longer registers a `plotly_hover` selection handler; hover only shows Plotly's native tooltip.
  Selection is now single-click only.
  If Plotly does not emit a point click, the DOM click fallback converts the clicked pixel to chart x/y coordinates and scans visible shaded aspect/regime polygons for the containing window, preferring click/hover hitbox traces and shorter windows when overlaps exist.
- Fresh chart export with single-click-only selection and markerless shaded-area fallback:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_201400.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_201400.csv`
- Follow-up on 2026-05-14:
  user clarified that shaded-area selection must select the full clicked aspect window, not stop at the next split regime/aspect boundary like a paint-bucket fill.
  The click-coordinate fallback now ranks full `aspect_window` hitboxes above split `regime_zone` segments, so intermediate regime/aspect boundaries should be skipped for aspect selection.
  Marker clicks are still protected from being overwritten by the underlying shaded-area fallback.
- Fresh chart export with aspect-first shaded-area selection:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_205344.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_205344.csv`
- Follow-up on 2026-05-14:
  user asked to add the aspect name to the red start/end labels for selected shaded zones.
  The selected-window annotations now show `Start`/`End`, then the selected aspect/window label in bold, then the date-time.
  The label is HTML-escaped in the browser script before insertion.
- Fresh chart export with aspect/window name in start/end labels:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_210417.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_210417.csv`
- Follow-up note from user on 2026-05-15:
  latest chart interaction works, but the red `Start` label can sometimes hide behind the M30/H1/Daily soft buttons.
  Next chart UI tweak should move selected-window labels lower/sideways or constrain them away from the timeframe button row.
- New workflow idea from user:
  instead of only asking ML to walk-forward all aspects globally, build an aspect-review agent/workbench.
  When user clicks aspect X, the tool should find same/similar aspects in the generated chart and navigate through them one by one.
  User should be able to mark proposed trade begin/end and ignore regions; system calculates gain/loss, labels bullish/bearish/ignore, and compares divergent outcomes against context factors such as enemy sign, dignity/shadbala strength, multiple overlapping aspects, and other active regimes.
- User clarified aspect-review requirements:
  same aspect means exact same `pair_key + aspect`, and search should cover the full CSV/history, not only the currently visible chart window.
  User wants free placement of start/stop markers inside the selected shaded area and free-form `why` notes so ML can learn from both outcome labels and human rule notes.
  User may add rules such as why a first SR line after the start marker was ignored, for example because it was too close.
  One aspect window may contain multiple trades/annotations and ignore regions.
  Outcome labels should include `bullish`, `bearish`, `sideways`, and `unclear`.
- User agreed with moving beyond Dash for the annotation workbench, but clarified that they do not know SQLite, Tauri, or React.
  Future implementation must be guided like a beginner walkthrough with no assumed knowledge:
  explain each new tool in plain language, introduce one concept at a time, and avoid asking the user to make low-level architecture choices without a recommendation.
  Codex should lead the migration step-by-step and keep the current Python research engine as the familiar anchor.
- First annotation database step on 2026-05-15:
  added `aspect_annotation_store.py`, a beginner-friendly Python helper for creating and testing the local SQLite annotation store.
  Local database path created by default:
  `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`
  The database is intentionally local data and is ignored by git via `.gitignore`.
  Tables created: `aspect_cases`, `trade_annotations`, `ignore_regions`, `rule_notes`, and `schema_meta`.
  Smoke test command passed:
  `python .\aspect_annotation_store.py --init-db --smoke-test`
  Smoke test inserted/read/deleted one sample `MARS|JUPITER opposition` bullish annotation; final annotation tables were empty after cleanup.
- Second annotation database step on 2026-05-15:
  `aspect_annotation_store.py` can now import real aspect cases from a touch-log CSV and list same-aspect occurrences by exact `pair_key + aspect`.
  Import command used:
  `python .\aspect_annotation_store.py --import-cases-from-csv .\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  Result: attempted unique cases `619`, inserted new cases `619`, skipped `0`.
  Database now has `619` `aspect_cases`, `143` exact `pair_key + aspect` groups, and `0` trade annotations.
  Listing commands verified:
  `python .\aspect_annotation_store.py --list-aspects --limit 15`
  `python .\aspect_annotation_store.py --list-cases --pair-key "AVG(ALL)|MOON" --aspect square --limit 5`
  Sample group `AVG(ALL)|MOON + square` had `18` historical cases.
- Third annotation database step on 2026-05-15:
  `aspect_annotation_store.py` can now save and list manual trade annotations for an imported `case_id`.
  New save command shape:
  `python .\aspect_annotation_store.py --add-trade-annotation --case-id 11 --trade-start "2025-03-07 12:00:00+05:30" --trade-end "2025-03-07 13:00:00+05:30" --outcome-label bullish --entry-price 147.10 --exit-price 147.30 --pips 20 --why "reason text"`
  New list command:
  `python .\aspect_annotation_store.py --list-annotations --case-id 11 --limit 5`
  CLI smoke test saved and listed annotation `annotation_id=3` for `case_id=11`, then deleted it.
  Final `trade_annotations` count after cleanup: `0`.
- Fourth annotation database step on 2026-05-15:
  user clarified auto price/pip calculation should support both M30 and H1; Daily will be handled later.
  `aspect_annotation_store.py` now supports `--price-timeframe m30` and `--price-timeframe h1` for auto-calculating entry close, exit close, pips, MFE pips, and MAE pips.
  Default price files:
  `m30`: `C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet`
  `h1`: `C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet`
  Trade markers are now validated to sit inside the selected aspect window.
  H1 smoke test passed on `case_id=11`; M30 smoke test passed on `case_id=15`.
  An out-of-window M30 test on `case_id=11` was rejected with a clean message, no traceback.
  Temporary smoke annotations were deleted; final `trade_annotations` count after cleanup: `0`.
- Fifth annotation database step on 2026-05-15:
  `aspect_annotation_store.py` now has a read-only review queue command:
  `python .\aspect_annotation_store.py --review-aspect --pair-key "AVG(ALL)|MOON" --aspect square`
  It prints total cases, annotated cases, unreviewed cases, the next unreviewed `case_id`, its event/window details, and a copy/edit `--add-trade-annotation` command template.
  Verified sample output for `AVG(ALL)|MOON + square`: total `18`, annotated `0`, unreviewed `18`, next unreviewed `case_id=11`.
  This is the first CLI version of "take user through same aspect one by one."
- Sixth annotation database step on 2026-05-15:
  `aspect_annotation_store.py` now supports ignore regions and free-form rule notes.
  Ignore-region command shape:
  `python .\aspect_annotation_store.py --mark-ignore-region --case-id 11 --region-start "2025-03-07 12:00:00+05:30" --region-end "2025-03-07 12:30:00+05:30" --why "reason text"`
  List ignore regions:
  `python .\aspect_annotation_store.py --list-ignore-regions --case-id 11 --limit 5`
  Rule-note command shape:
  `python .\aspect_annotation_store.py --add-rule-note --case-id 11 --note-type sr_ignore_reason --note "reason text"`
  List rule notes:
  `python .\aspect_annotation_store.py --list-rule-notes --case-id 11 --limit 5`
  Ignore regions are validated to stay inside the selected aspect window; out-of-window test was rejected with a clean message.
  Temporary smoke ignore/note rows were deleted; final counts after cleanup: `trade_annotations=0`, `ignore_regions=0`, `rule_notes=0`.
- Seventh annotation database step on 2026-05-15:
  `aspect_annotation_store.py` now supports `--export-review-case --case-id N` to write a JSON snapshot for a future UI/app bridge.
  Default output path shape:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_<case_id>.json`
  Verified command:
  `python .\aspect_annotation_store.py --export-review-case --case-id 11`
  Output:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11.json`
  Snapshot top-level keys: `case`, `same_aspect`, `saved`, `suggestions`, `exported_at_utc`.
  For `case_id=11`, same-aspect total was `18`, case index was `1`, and saved annotation/note counts were all `0`.
  This JSON is the planned bridge from the Python research/annotation engine into a later React/Tauri review UI.
- Eighth annotation database step on 2026-05-15:
  `aspect_annotation_store.py` now supports `--export-review-html --case-id N` to write a plain static HTML review page from the same review-case payload.
  Default output path shape:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_<case_id>.html`
  Verified command:
  `python .\aspect_annotation_store.py --export-review-html --case-id 11`
  Output:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11.html`
  Page sections: current case, progress, action command templates, saved trade annotations, saved ignore regions, saved rule notes, same-aspect queue, and raw JSON snapshot.
  This is the first no-install visual review page before React/Tauri.
- Ninth annotation database step on 2026-05-15:
  The lightweight SVG price chart preview was rejected because it does not show candlestick patterns, planetary/SR lines, or multiple overlapping events.
  It is no longer part of the review JSON payload or the visible review HTML.
  `sr_touch_lazy_dashboard.py` now supports real generated case chart snapshots from the existing Plotly dashboard renderer:
  `--export-case-chart --case-id N`
  and bulk export:
  `--export-all-case-charts`
  Case snapshots are centered around the selected aspect window, keep candlesticks, SR planetary lines, all overlapping aspect/regime windows, quote/JPY detail click behavior, and add a red selected-case border plus selected touch rings.
  `aspect_annotation_store.py --export-review-html` now embeds/links `aspect_review_case_<case_id>_chart.html` when that chart snapshot exists, instead of rendering a simplified local SVG chart.
  Verified commands:
  `python .\sr_touch_lazy_dashboard.py --touch-log .\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv --price .\usd_jpy_h1_mt5_metaquotes_demo_full.parquet --export-case-chart --case-id 11 --case-timeframe auto --export-dir C:\Users\ADMIN\Desktop\doc --export-max-lines 60`
  `python .\sr_touch_lazy_dashboard.py --touch-log .\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv --price .\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet --export-case-chart --case-id 15 --case-timeframe auto --export-dir C:\Users\ADMIN\Desktop\doc --export-max-lines 60`
  `python .\aspect_annotation_store.py --export-review-html --case-id 11`
  `python .\aspect_annotation_store.py --export-review-case --case-id 11`
  Regenerated outputs:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11.html`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11.json`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11_chart.html`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11_chart_visible.csv`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_15_chart.html`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_15_chart_visible.csv`
  Verification result: `case_id=11` real chart contains candlestick, selected-case highlight, aspect windows, regime zones, and detail panel; visible rows `12`.
  `case_id=15` with M30 price contains M30 and Hourly switch buttons plus the same real chart context; visible rows `24`.

Case-level feature inventory update on 2026-05-16:

- Added reusable builder:
  `C:\Users\ADMIN\PycharmProjects\build_case_id_feature_inventory.py`
- Generated case inventory:
  `C:\Users\ADMIN\PycharmProjects\case_id_feature_inventory_transitsign_20260516_0132.csv`
- The inventory is one row per saved SQLite `case_id` and joins:
  `gann_aspect_annotations.sqlite`,
  `aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`,
  and `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`.
- Output rows: `619`; columns: `92`.
- CSV occurrence distribution from the current rich candidate CSV:
  `0 occurrences=79`, `1 occurrence=75`, `2 occurrences=465`.
  The 2-occurrence cases are usually repeated across M30 and H1; single-occurrence cases are usually daily-only or one visible timeframe; zero-occurrence cases exist in the annotation store/touch log but are not present in the current switch candidate CSV.
- Included fields cover case identity, M30/H1/Daily occurrence counts, natural benefic/malefic classes and biases for the aspect bodies, shadbala tag/average, BPHS-like event strength/virupa, aspect family/duration bucket, regime signature, SR touch identity, jyotish/doctrine/FX pair scores, dominant dignity strings, ML outcome/close-action summaries, and scoped quote/base hit summaries with dignity label counts including enemy/debilitation/unknown plus benefic/malefic component counts.
- Verification:
  `python -m py_compile build_case_id_feature_inventory.py` passed.
  Inventory totals showed quote/base enemy dignity component counts `218/225`; quote/base benefic component counts `538/620`; quote/base malefic component counts `831/764`.

Manual case review sheet update on 2026-05-16:

- Added reusable builder:
  `C:\Users\ADMIN\PycharmProjects\build_manual_case_review_sheet.py`
- Generated full review CSV:
  `C:\Users\ADMIN\PycharmProjects\manual_case_review_sheet_transitsign_20260516_0145.csv`
- Generated focused review CSV:
  `C:\Users\ADMIN\PycharmProjects\manual_case_review_focus_transitsign_20260516_0145.csv`
- Generated focused Excel workbook:
  `C:\Users\ADMIN\PycharmProjects\manual_case_review_focus_transitsign_20260516_0145.xlsx`
- Full review sheet rows: `619`; columns: `119`; recurrence groups: `143`.
- Focus review sheet columns: `47`.
- Manual review columns added:
  `review_status`, `manual_direction_label`, `manual_behavior_label`, `manual_trade_action`, `manual_confidence`, `manual_reason_tags`, `manual_notes`, `reviewed_by`, `reviewed_at_ist`.
- Group-level recurrence fields added:
  `same_aspect_group_key`, `same_aspect_group_size`, group FX doctrine direction counts, group ML outcome counts, group close-action counts, M30/H1/Daily occurrence totals, average shadbala, average FX doctrine net/conflict, and average signed return.
- Script-generated factor tags include:
  `repeated_across_timeframes`, `not_in_current_candidate_csv`, `high_recurrence_group`, `multiple_active_aspects`, `crowded_regime`, `low_shadbala`, `strong_shadbala`, `quote_enemy_sign`, `base_enemy_sign`, `quote_debilitation`, `base_debilitation`, `unknown_outer_or_node_dignity`, `avg_all_composite`, `malefic_pair`, `hard_aspect`, `soft_aspect`, and FX conflict tags.
- Verification:
  `python -m py_compile build_manual_case_review_sheet.py` passed.
  Focus workbook imported successfully, `Manual Review!A1:K12` inspected correctly, formula/error scan matched `0` entries, and a rendered preview of `A1:K16` was checked.

Repeatation review pack update on 2026-05-16:

- User clarified the intended workflow:
  create real chart snapshots for a selected event/case and all its repeatations; manually place start/end, ignore, and rule-note markers; auto-calculate gain/pips and bullish/bearish behavior from marker start/end; then let ML/scripts compare the repeatation family and explain why behavior differs across occurrences before moving to the next case family.
- Added reusable builder:
  `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`
- First repeatation family exported from seed `case_id=11`:
  `AVG(ALL)|MOON :: square`
- Repeatation count: `18` cases:
  `11, 44, 97, 120, 150, 169, 196, 250, 269, 304, 378, 500, 515, 543, 548, 560, 578, 603`.
- Local full chart pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_20260516_025027`
- Main review index:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_20260516_025027\repeatation_review_index.html`
- Marker/template CSV:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_20260516_025027\repeatation_marker_template.csv`
- Tracked recovery copy:
  `C:\Users\ADMIN\PycharmProjects\repeatation_review_packs\case_11_avg_all_moon_square_20260516_025027`
- The pack generated 18 real chart snapshots plus visible CSVs. Total local pack size was about `27 MB`; chart HTMLs remain local/regenerable rather than all tracked in Git.
- The marker template includes chart paths, visible-row counts, per-case full-window bullish/bearish pips, script group bias, probable factor tags, and command templates for:
  `--add-trade-annotation`, `--mark-ignore-region`, and `--add-rule-note`.
- Full-window behavior for this family already shows useful divergence against the script group bias `BEARISH`:
  most cases were bearish over the event window, but cases `304`, `500`, `515`, and `603` were bullish, while case `11` was flat by full-window close-to-close.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py` passed.
  The marker template has `18` rows; chart visible rows ranged from `5` to `44`.

Repeatation marker UI update on 2026-05-16:

- `build_repeatation_review_pack.py` now injects a fixed `Repeatation Marker UI` panel into every generated case chart HTML.
- The panel supports click-to-place markers for:
  trade start, trade end, ignore start, and ignore end.
- The chart overlays vertical trade marker lines and an orange ignore-region rectangle when both ignore boundaries are set.
- The panel includes outcome selection, note type, free-form note text, command generation, copy buttons, clear markers, and JSON download for marker payloads.
- Generated commands still write through `aspect_annotation_store.py`, so SQLite stays controlled by the existing Python validation and pips/MFE/MAE auto-calculation logic.
- Latest UI-enabled local pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`
- Open:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548\repeatation_review_index.html`
- Tracked recovery copy:
  `C:\Users\ADMIN\PycharmProjects\repeatation_review_packs\case_11_avg_all_moon_square_ui_20260516_030548`
- Verification:
  `python -m py_compile build_repeatation_review_pack.py` passed.
  The injected marker UI script was extracted from `aspect_review_case_11_chart.html` and parsed with JavaScript `new Function(...)` successfully.
  The in-app browser blocked direct `file://` navigation by policy, so visual browser interaction could not be completed in Codex; use normal Chrome/Edge or open the local HTML directly from Windows for manual UI testing.

Important scoring fix on 2026-05-04:

- Earlier hover scores used the strongest active `tn_hits_json` hit in the whole bar.
- That caused unrelated hits such as `NEPTUNE>RAHU:square` to appear as dominant on `MARS|MOON` or `MERCURY|MOON` hovers.
- The scorer now scopes dominant hits to the hovered row's `pair_key` planets and prefers the hovered aspect type when available.
- If no scoped hit exists, the hypothesis shows `UNKNOWN`/blank instead of using an unrelated dominant hit.

Validation for latest export:

```text
unrelated NEPTUNE>RAHU square count on non-Neptune/Rahu pairs: 0
M30/H1 rows: 424 each, duration 60-1440 min
Daily rows: 116, duration 1500-6660 min
hover rows with rule block: 964/964
```

If the chart still shows old hover details, verify the opened file is the latest export:

`C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260504_213821.html`

Validation for that export:

```text
M30 marker hover rows with rule block: 424/424
M30 figure traces with rule text: 477
```

## PDF Study Artifacts

PDF text extraction folder:

`C:\Users\ADMIN\Desktop\doc\pdf_text_extracts`

PDFs currently registered for project reference:

- `Building a Strict Vedic Astrology Prediction Engine with a Local LLM Layer.pdf`
- `Strict Jyotish Prediction Engine with Local LLM & ML Calibration2.pdf`
- `pdfcoffee.com_financial-astrology-pdf-free.pdf`
- `pdfcoffee.com_futuretec-financial-astrology-set-2-dhruvank-pdf-free.pdf`
- `pdfcoffee.com_gann-financial-astrology-pdf-free.pdf`
- `jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf`

Feature inventory files:

- `astro_feature_inventory_from_pdfs.md`
- `astro_feature_inventory_from_pdfs.yaml`

Shad Bala update on 2026-05-05:

- `C:\Users\ADMIN\Desktop\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf` was verified as readable text.
- Extracted text was generated at:
  `C:\Users\ADMIN\Desktop\doc\pdf_text_extracts\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.txt`
- Extraction summary: 179 pages, all pages nonempty, about 222k extracted characters.
- Inventory source ID added: `SHADBALA_JAYA`.
- `SHADBALA_GATE` now cites `SHADBALA_JAYA:p23-p101` as the detailed doctrine reference.

PyYAML installed:

```text
PyYAML 6.0.3
```

YAML validation:

```text
sources: 6
doctrine_locks: 4
features: 20
```

Important PDF conclusion:

- The two strict Jyotish PDFs are architecture/doctrine-control docs.
- The Shad Bala PDF is the detailed strength-reference source for future `SHADBALA_GATE` implementation.
- AstroEcon and Futuretek/Dhruvank are experimental feature sources.
- Gann PDF now has OCR text; implementable rules still require manual page verification before coding.
- Gann PDF OCR was completed on 2026-05-10:
  `C:\Users\ADMIN\Desktop\doc\pdf_text_extracts\pdfcoffee.com_gann-financial-astrology-pdf-free.ocr.txt`
  Summary JSON:
  `C:\Users\ADMIN\Desktop\doc\pdf_text_extracts\pdfcoffee.com_gann-financial-astrology-pdf-free.ocr_summary.json`
  Per-page OCR checkpoints:
  `C:\Users\ADMIN\Desktop\doc\pdf_text_extracts\gann_ocr_pages`
- Initial Gann candidate feature families were added to the inventory:
  `GANN_PRICE_LONGITUDE_HIT`, `GANN_OUTER_PLANET_AVERAGE`, `GANN_CIRCLE_ACTIVE_ANGLE`.
  These remain experimental and not implemented; verify page OCR/source images before encoding rules.

## Useful Commands

Export latest switch chart with M30/H1/Daily and FX hover scores:

```powershell
python C:\Users\ADMIN\PycharmProjects\sr_touch_lazy_dashboard.py `
  --touch-log C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv `
  --price C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet `
  --export-full-year `
  --export-dir C:\Users\ADMIN\Desktop\doc `
  --export-max-lines 60 `
  --timeframe switch
```

Rebuild scored trade candidates from latest switch CSV:

```powershell
python C:\Users\ADMIN\PycharmProjects\build_trade_candidates_from_touches.py `
  --touch-log C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.csv `
  --price C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet `
  --output-csv C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv `
  --output-parquet C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet
```

Check Git:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -C 'C:\Users\ADMIN\PycharmProjects' status --short
& 'C:\Program Files\Git\cmd\git.exe' -C 'C:\Users\ADMIN\PycharmProjects' log --oneline -8
```

## Next Recommended Steps

1. Resume manual review of the `AVG(ALL)|MOON + square` repeatation family in the served review pack, starting from the currently interesting cases `8`, `43`, and the next unreviewed repeatations in the same family.
2. For each reviewed case, use the marker drawer workflow:
   `Auto Suggest`, manual marker adjustment when needed, saved trade/ignore/rule notes, `ML Notes`, and `Draft ML Reason`.
3. Treat deterministic Python evidence, saved annotations, SR geometry, break confirmation, attribution boundary, and rule-vs-default pips as ground truth. Treat local LLM output as a draft explanatory layer only.
4. When `Draft ML Reason` agrees with deterministic evidence, use it to speed up note writing. When it drifts, keep the deterministic section and either omit or revise the LLM commentary.
5. Promote, revise, or discard provisional family notes after enough repeatations are reviewed. Current important local ideas include:
   `bearish_bias_support_barrier`,
   `bearish_confirmed_support_break_attribution_boundary`,
   and the related support-break / next-event-boundary behavior.
6. After the AVG(ALL)|MOON square family has enough reviewed examples, generalize the same review loop to mirrored bullish SR-barrier families and other high-value aspect families.
7. Only after more reviewed labels exist, extend walk-forward validation for rule calibration:
   `fx_pair_net_score`, `fx_doctrine_pair_net_score`, SR geometry classes, break-confirmation features, attribution-boundary features, and blended deterministic score variants.
8. Improve local model quality only after the annotation loop exposes repeated explanation failures. Candidate next moves are tighter prompts, a better local model than `qwen2.5:3b`, or richer local RAG retrieval. Keep deterministic evidence first in all cases.
9. Later, add PDF/Gann feature columns one group at a time only after manual source review:
   midpoint hits, stellium, T-square/grand-cross/grand-trine, Dhruvank daily signal, `GANN_PRICE_LONGITUDE_HIT`, `GANN_OUTER_PLANET_AVERAGE`, and `GANN_CIRCLE_ACTIVE_ANGLE`.

## Memory-Safe Touch-Log Rebuild Plan

Reason:
- The prior full touch-log rebuild appears to have crashed/restarted the laptop during high memory use, reportedly around 10 GB.
- `build_aspect_sr_touch_log.py` currently accumulates generated rows in memory and creates one final DataFrame before writing output. That is risky for full all-duration rebuilds with transit-sign hit JSON.

Preferred fix before another full rebuild:
- Add chunked/checkpointed output to `build_aspect_sr_touch_log.py`.
- Process events in small batches, for example 25-50 events per batch.
- Write each batch to `*.partNNNN.parquet` or append-safe CSV immediately after the batch completes.
- Persist a small manifest with batch number, event id range, row count, timestamp, and command args.
- Add `--resume-from-checkpoints` so a laptop restart does not lose completed batches.
- Concatenate checkpoint parquet files only at the end, or let downstream scripts read a checkpoint directory.
- Keep memory bounded by clearing batch row lists/DataFrames after each write.
- Prefer parquet checkpoints over one giant CSV during rebuild; write the final CSV only after successful validation.
- Add a smoke option that rebuilds the first few events with `transit_sign`, `transit_lon`, and `natal_lon`, then verifies those keys before the full run.

Operational fallback:
- If code changes are not desired first, run multiple smaller date/event slices manually and merge after validation.
- Monitor memory during the first full attempt; abort if memory rises steadily instead of plateauing.
- Keep the existing complete all-duration touch log as the fallback source until the new checkpointed rebuild is complete and validated.

Implementation started on 2026-05-10:
- `build_aspect_sr_touch_log.py` now accepts `--event-slice-start`, `--event-slice-size`, and `--dry-run-count`.
- Added `run_touchlog_rebuild_checkpoints.py`, a resumable checkpoint runner.
- Smoke rebuild of 5 events produced hit JSON with `transit_lon`, `transit_sign`, `natal_lon`, and `natal_sign`.
- First real checkpoints:
  `part_00000_00049.csv` completed, 49 rows.
  `part_00050_00099.csv` completed, validated.
- Full background checkpoint runner was started at 2026-05-10 23:36 IST:
  checkpoint dir: `C:\Users\ADMIN\PycharmProjects\touchlog_rebuild_checkpoints_transitsign_20260510`
  final target: `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  total filtered events: `11668`
  batch size: `50`
  runner process observed: `python.exe` running `run_touchlog_rebuild_checkpoints.py`
- Progress check at 2026-05-11 00:04 IST:
  92 checkpoint CSV parts complete, latest complete part `part_04550_04599.csv`, runner processing event slice `4600-4649`.
- Telegram progress monitor started on 2026-05-11:
  script: `C:\Users\ADMIN\PycharmProjects\monitor_touchlog_rebuild_telegram.py`
  interval: 15 minutes
  monitor process observed: `python.exe` PID `7252`
  monitor log: `C:\Users\ADMIN\PycharmProjects\touchlog_rebuild_telegram_monitor.log`
  The monitor uses `C:\Users\ADMIN\Desktop\Trading_Algo\New folder\telegram_remote_control.py` for Telegram config/client support.
  Note: two initial test messages incorrectly said `stopped` because Windows liveness detection used `os.kill(pid, 0)`; this was fixed and corrected `running` messages were sent.
- At 2026-05-11 00:16 IST the runner stopped on `failed_validation` for slice `6100-6149`; the batch generated a valid header-only CSV with zero touch rows, so there were no hit JSON records to validate. This was not a data/schema failure.
- `run_touchlog_rebuild_checkpoints.py` was updated to accept legitimate zero-row/header-only checkpoint parts and non-empty parts with no TN hits, while still rejecting malformed JSON or hit records missing required keys.
- Runner was resumed at 2026-05-11 00:30 IST. Corrected Telegram monitor messages were sent at 00:31 IST with status `running`.
- Progress check at 2026-05-11 00:31 IST:
  126 checkpoint CSV parts complete, latest complete part `part_06250_06299.csv`, runner processing event slice `6300-6349`.
- Completion/correction on 2026-05-11 01:50 IST:
  The broad checkpoint run completed, but it was invalid for the intended file because it used the builder default event source
  `astro_training_data_ipo_tokyo_18890211.parquet` instead of the intended
  `astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet`.
  Resulting broad merge had `11094` rows from `11668` filtered events and must not be used downstream.
- Correct source universe:
  `C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet`
  with `787` filtered events.
- Corrected checkpoint test directory:
  `C:\Users\ADMIN\PycharmProjects\touchlog_rebuild_checkpoints_transitsign_nodes_20260511`
  produced 16 parts, but the slice merge produced `641` rows. A single-pass control on the same 787 events produced `619` rows, matching the old all-duration touch log. Cause: event slicing changes slice-local SR/longitude/regime context, so checkpoint part merges are not semantically equivalent to a single-pass build.
- `run_touchlog_rebuild_checkpoints.py` now refuses to merge event-sliced parts by default unless `--allow-slice-merge` is passed. Treat merged checkpoint parts as diagnostic only until the builder is redesigned to preserve global context while streaming rows.
- Validated final transitsign touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  rows: `619`
  unique `event_id`: `619`
  time range: `2025-03-03 12:30:00+05:30` to `2026-03-06 18:30:00+05:30`
  aspect counts: `trine=207`, `square=201`, `opposition_orb=106`, `conjunction_orb=105`
  event-id set equals the old all-duration touch log.
  JSON validation: `9356` hit records checked across `tn_hits_json` and `base_tn_hits_json`; missing required `transit_lon`, `transit_sign`, or `natal_lon`: `0`; malformed JSON: `0`.
- Correct final rebuild command used:
  `python C:\Users\ADMIN\PycharmProjects\build_aspect_sr_touch_log.py --events C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet --price C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet --include-natal --aspect-mode orb --max-event-days 0 --output C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
- Do not resume the old broad checkpoint directory `touchlog_rebuild_checkpoints_transitsign_20260510` for final artifacts.

## Session Recovery Discipline

- Codex Windows app recovery check on 2026-05-16 00:47 IST:
  The generated Codex app folder `C:\Users\ADMIN\Documents\Codex\2026-05-16\this-is-my-private-gann-financial` had no `.git` directory or `CURRENT_PROJECT_HANDOFF.md` and refused file creation under `Documents` (`FileNotFoundException` on simple write probes).
  Recovery repo `https://github.com/gouravdamade/gann-financial-astro-research` was cloned successfully to a temp bridge, then the canonical local repo `C:\Users\ADMIN\PycharmProjects` was confirmed present, writable, and clean.
  Initial Codex app checks in the canonical repo: `git status --short` clean; latest commit `950ae29 Add Codex app recovery instructions`; recent log matches the Git State section above.
- Codex Windows app trial note on 2026-05-16:
  user plans to try the OpenAI Codex Windows app because PyCharm keeps losing chat threads.
  Treat GitHub plus this handoff as the durable source of truth so the user can switch between Codex app and PyCharm seamlessly.
  Short paste-in prompt for the Codex app:
  `This is my private Gann / financial astrology USDJPY research workspace. Please start by reading CURRENT_PROJECT_HANDOFF.md, then run git status --short and git log --oneline -8. The GitHub recovery repo is https://github.com/gouravdamade/gann-financial-astro-research. Keep CURRENT_PROJECT_HANDOFF.md updated after meaningful work, create a timestamped chat_session_backups backup, commit changes, and push to origin/master so I can switch between Codex app and PyCharm without losing state.`
  If the app starts outside this folder, open or clone `C:\Users\ADMIN\PycharmProjects` or the GitHub repo.
- GitHub recovery preparation on 2026-05-16:
  local git user email and connected GitHub account are `gourav.damade@gmail.com`; GitHub username is `gouravdamade`.
  Private GitHub recovery repo:
  `https://github.com/gouravdamade/gann-financial-astro-research`
  Local remote:
  `origin https://github.com/gouravdamade/gann-financial-astro-research.git`
  Initial recovery package was pushed to branch `master` on 2026-05-16.
  `README.md` was added with the resume prompt, key files, common commands, and privacy note.
  The workspace is prepared as a private GitHub recovery repo with core scripts, handoff, source notes, current curated data files, annotation SQLite database, and latest curated chat/session backup.
- Update this handoff after each meaningful work session, especially after long-running builds, generated artifacts, failed rebuild attempts, or chat/session recovery work.
- Codex in-app browser chart recovery on 2026-05-16 03:26 IST:
  `http://localhost:8765/aspect_review_case_11_chart.html` was showing `This site can't be reached` because no local server was listening on port `8765`; the chart file itself existed at
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548\aspect_review_case_11_chart.html`.
  Started a hidden Python static server with PID `11220`:
  `python -m http.server 8765 --bind 127.0.0.1 --directory C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`
  Verified the in-app browser loads both `http://127.0.0.1:8765/aspect_review_case_11_chart.html` and `http://localhost:8765/aspect_review_case_11_chart.html`; DOM includes `Repeatation Marker UI`.
  Searched for obvious `debug=True` / `debug: true` flags in the repo and found no matching debug mode flag. The issue was server availability, not debug mode.
- Repeatation marker UI correction on 2026-05-16 03:43 IST:
  User flagged that the marker panel covered too much chart area and that placed markers should look like crosshairs, not full-height vertical lines.
  `build_repeatation_review_pack.py` now injects a compact collapsed `Markers` drawer by default, with `Open` / `Hide` toggle controls, and renders trade/ignore placements as small time/price crosshair targets with a ring plus short horizontal/vertical strokes.
  The current served pack at `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548` was refreshed in place for all 18 chart HTML files; reload `http://localhost:8765/aspect_review_case_11_chart.html` to see it.
  Browser verification: the chart loads, drawer is collapsed by default, `Open` expands it, `Hide` collapses it, and a click on the chart places a compact green crosshair.
- Price coverage correction on 2026-05-16 03:54 IST:
  User noticed case `11` showed no candles near the selected March 7 event and candles only around March 10. This was not a non-trading-day issue: March 7, 2025 was a Friday, but the M30 price file `usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet` starts at `2025-03-10 05:30 IST`.
  `usd_jpy_h1_mt5_metaquotes_demo_full.parquet` covers the case window (`2010-01-27` through `2026-03-10`), so `build_repeatation_review_pack.py` now checks price coverage and falls back from M30 to H1 when M30 does not cover a case window/chart context.
  Regenerated the current served repeatation pack in place. `aspect_review_case_11_chart.html` now uses H1 candles around March 4-10, and `repeatation_marker_template.csv` uses `price_timeframe=h1` for case `11` annotation commands/statistics instead of invalid M30 nearest-bar snapping.
- Localhost server recovery on 2026-05-16 16:32 IST:
  User again saw `ERR_CONNECTION_REFUSED` on `http://localhost:8765/aspect_review_case_11_chart.html`; no process was listening on port `8765`, while the chart file still existed. Restarted a hidden Python static server for the case 11 repeatation pack with PID `13112` and verified HTTP 200 plus browser rendering in a fresh in-app tab.
  Added `serve_repeatation_pack.py` as a durable helper. Run `python serve_repeatation_pack.py` from `C:\Users\ADMIN\PycharmProjects` to serve the default case 11 pack at `http://localhost:8765/aspect_review_case_11_chart.html`.
- Repeatation draft autosave on 2026-05-16 16:43 IST:
  `build_repeatation_review_pack.py` marker UI now autosaves in-progress marker drafts to browser `localStorage` per `case_id` / price timeframe. It saves marker points, active tool, drawer state, outcome, note type, and note text on edits, every 2 seconds while there is draft content, and on `beforeunload`; drafts restore after reload/server restart as long as browser local site data remains. The drawer shows autosave/restored status and has `Clear saved draft` to remove both localStorage and visible draft fields.
  Refreshed the currently served case 11 repeatation chart HTML files in place and verified note + trade-start marker restore after reload; verified `Clear saved draft` removes the test draft and it does not return.
- Repeatation navigation on 2026-05-16 16:55 IST:
  Added `Previous`, `Next`, and `All` soft navigation to each marker drawer. The generator also writes `repeatation_reviewer.html`, a single reviewer shell with a left-side list of all repeatations and an embedded chart frame, so review can proceed from one stable page rather than manually opening individual recurrence files. Verified in the in-app browser that `Next` moves from case `11` to case `44` inside the reviewer flow.
  `serve_repeatation_pack.py` now prints both `http://localhost:8765/repeatation_reviewer.html` and the direct case 11 chart URL.
- Repeatation ignore-trade marker on 2026-05-16 17:53 IST:
  User identified a nearby aspect/event contaminating the case under review and requested a quick whole-trade ignore action. `build_repeatation_review_pack.py` now adds an `Ignore Trade` soft button under the marker controls. It marks the full case window as an ignore region, sets a default `ignore_trade_nearby_event` ML note only when the note is empty, autosaves/restores `trade_ignored`, includes it in downloaded marker JSON, and labels the generated command as `Ignore trade`.
  Refreshed the currently served pack at `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548` in place for all 18 chart HTML files and synced the tracked recovery index. Browser verification: `http://localhost:8765/repeatation_reviewer.html` loads, the marker drawer opens, and `Ignore Trade` appears without disturbing the restored draft.
- Repeatation cursor recovery on 2026-05-16 18:08 IST:
  User reported that Codex in-app browser annotation mode can leave a custom annotation cursor stuck after disabling annotations, forcing chart refresh. This appears likely to be outside the chart page itself, but the marker UI now includes a `Reset Cursor` soft button that clears page/Plotly inline cursor styles, clears browser text selection, blurs non-panel active elements, and updates the drawer status without reloading. The `Ignore Trade` command now also requires a non-empty why-note when the whole trade is marked ignored, so ML/script review keeps the contamination reason.
  Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files and synced the tracked recovery index. Browser verification: `Ignore Trade` and `Reset Cursor` are visible in the drawer, and clicking `Reset Cursor` shows `cursor reset without reloading`.
- Repeatation ML annotation ledger on 2026-05-16 18:29 IST:
  User clarified the goal: the UI should feed ML from what the reviewer sees, including multiple ignore signals and rule notes. `build_repeatation_review_pack.py` marker UI now has a first structured annotation ledger. It supports multiple `ignore_signal` entries and `rule_note` entries, each with scope, type, note type, note text, case/aspect metadata, price timeframe, timestamp, and marker context (`last_point`, trade markers, ignore markers, case window, `trade_ignored`). Entries autosave in browser localStorage as `ml_annotations`, restore after reload, can be removed individually, can be cleared with `Clear ML Notes`, and are included in downloaded marker JSON.
  Added UI controls: `Ignore signal type`, `Rule scope / type`, `Add Ignore Signal`, `Add Rule Note`, and `ML annotation ledger`. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files and synced the tracked recovery index. Browser verification: all new controls are present in `http://localhost:8765/repeatation_reviewer.html` without adding test annotations to the user's active draft.
- Repeatation ignore-signal definitions on 2026-05-18 20:25 IST:
  User requested multiple ignore signal selections and explicit definitions so ML/script learning does not hallucinate from vague labels. `build_repeatation_review_pack.py` now replaces the old single ignore-signal dropdown with multi-select soft buttons. Selecting ignore signal types automatically writes pointwise human-readable definitions into `Notes / why` with underscores converted to spaces. The downloaded JSON now includes `selected_ignore_types` and `annotation_definitions` for ignore signal types, rule scopes, and rule types; each ignore annotation also stores `types`, `type_definitions`, and `scope_definition`.
  Added definitions for `ignore_trade_nearby_event`, `ignore_trade_event_too_short`, `nearby_aspect`, `overlapping_aspect`, `crowded_regime`, `bad_price_data`, `abnormal_candle`, `session_gap`, `no_clear_reaction`, and `manual_skip`, plus definitions for rule scopes and rule types. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files. Browser verification: ignore signal soft buttons render, `ignore trade event too short` is present, definition box is present, and the old single-select dropdown is gone.
- Repeatation ignore-note cleanup on 2026-05-18 21:08 IST:
  User noticed the old legacy `ignore trade: nearby/overlapping aspect/event contaminates case behavior` phrase could appear twice in `Notes / why` after the new ignore-signal definition block was added. `build_repeatation_review_pack.py` now strips that legacy default phrase whenever ignore-signal notes are rebuilt and also migrates restored drafts by calling the cleanup after `selected_ignore_types` are loaded. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files. Browser verification after reload: duplicate legacy phrase count in the note field was `0`.
- Repeatation trade marker visibility on 2026-05-19 20:09 IST:
  User reported that placed trade start/end markers were not clear/readable enough and asked about always-on hover/callout details. `build_repeatation_review_pack.py` now renders trade start/end markers more prominently than ignore markers: wider crosshair strokes, a larger translucent halo, a filled colored core with white border, and always-visible Plotly arrow callouts labeled `Trade start` / `Trade end` with timestamp and price from `fmtPoint`. Marker annotations are managed alongside marker shapes and filtered by `repeatation-marker*` names so chart-native annotations remain intact. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files.
- Repeatation hover translucency on 2026-05-19 20:43 IST:
  User reported chart hover text was blocking candles while placing markers. `sr_touch_lazy_dashboard.py` now uses a more translucent Plotly hover label background (`rgba(11, 6, 81, 0.42)`). `build_repeatation_review_pack.py` also injects CSS for already-exported charts to make `.hoverlayer .hovertext` backgrounds/strokes translucent while keeping text readable, and trade marker arrow-callout backgrounds were softened from 0.96 to 0.68 alpha. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files. Browser verification: chart frame contains the hover translucency CSS.
- Repeatation reviewer cache-busting on 2026-05-19 21:02 IST:
  User observed the marker-arrow / hover-translucency tweaks appeared limited to the first two repeatations. Disk inspection showed all 18 served chart HTML files already contained the current marker script, trade marker arrow/callout settings, hover translucency CSS, and reviewer links; the issue was likely stale in-app-browser iframe caching for later chart pages. `build_repeatation_review_pack.py` now uses `REPEATATION_UI_VERSION = "repeatation_ui_20260519_hover_v2"` and appends `?v=...` to chart/reviewer HTML links (`Previous`, `Next`, `All`, index links, reviewer sidebar links, and iframe `src`). `serve_repeatation_pack.py` now uses a `NoCacheRequestHandler` with `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`, `Pragma: no-cache`, and `Expires: 0`.
  Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files and synced the tracked reviewer/index files. Restarted the localhost server on port `8765` with PID `23420`. Verification: `Invoke-WebRequest` on `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260519_hover_v2` returns HTTP `200` and no-cache headers; all 18 chart HTML files pass checks for `repeatation-marker-ui-script`, `.hoverlayer .hovertext path`, `showarrow: true`, `arrowwidth: 2.5`, and the cache version. Browser verification on later direct chart `aspect_review_case_120_chart.html?v=repeatation_ui_20260519_hover_v2` showed case 120 has the current marker UI, ignore chips, trade labels, and translucent hover CSS.
- Repeatation adopted chart marker selection on 2026-05-19 21:19 IST:
  User pointed out that pre-existing chart touch/interaction markers are often already perfectly positioned for review start/end and should be reused instead of covered by heavy hardcoded review markers. `build_repeatation_review_pack.py` now treats clicked Plotly marker traces (`Interactions`, `Selected case touches`, and other marker/touch/interaction traces) as `source='chart_marker'`, preserving `traceName`, `curveNumber`, `pointNumber`, and a compact `markerLabel` in drafts/downloads. For adopted chart markers, the review overlay now draws only a soft glow/ring around the original marker and suppresses the large trade arrow callout; blank/candle clicks still use the crosshair and callout fallback.
  Cache key advanced to `repeatation_ui_20260519_marker_adopt_v3`; refreshed the served case 11 repeatation pack in place for all 18 chart HTML files and synced tracked reviewer/index files. Verification: all 18 served chart HTML files contain `chart_marker`, `adopted-marker-glow`, and the v3 cache key. Browser verification on case `120` confirmed the v3 script/link set is present; a background test click was cleared immediately via `Clear saved draft`.
- Repeatation marker magnet / compact fallback on 2026-05-19 21:31 IST:
  User clarified that when a hardcoded chart marker is present near the desired start/end, the UI should simply light that existing marker rather than drawing a green trade line/callout; where no hardcoded marker exists, the fallback should be a small crosshair, not a vertical-looking line. `build_repeatation_review_pack.py` now uses a 34px nearest-marker magnet around clicks, so nearby `Interactions` / `Selected case touches` points are adopted even when the click is slightly off the Plotly point. Trade start/end callout annotations are suppressed; the chart keeps only a compact ring/glow for adopted points or a short plus-style crosshair for fallback clicks, while exact time/price remains in the drawer and downloaded JSON.
  Cache key advanced to `repeatation_ui_20260519_marker_magnet_v4`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain `nearestChartMarker`, `adopted-marker-glow`, and v4 cache key, and no served chart contains the old `tradeLabel(state.tradeStart...)` callout invocation. Browser case `120` loaded v4 and visually showed ring/glow markers without the big trade callout. Do not clear the browser draft after this check because it may contain the user's active review markers.
- Repeatation marker capture / drag adjustment on 2026-05-19 21:48 IST:
  User reported that shaded aspect/regime windows could still get selected while trying to place a close-trade marker at aspect start, and requested draggable adjustment plus thinner crosshairs for precise wick placement. `build_repeatation_review_pack.py` now captures chart `mousedown`/`mouseup` before Plotly shaded-region click handlers, places markers on mouseup, and uses the normal click event only as a suppressor, so shaded areas should not steal marker placement. Manually placed review markers can be dragged by grabbing near the small marker; during drag the marker magnet is disabled, allowing fine adjustment to candle upper/lower wicks. Crosshair/glow strokes were thinned substantially.
  Cache key advanced to `repeatation_ui_20260519_marker_capture_v6`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain `pendingMarkerClick`, `pointFromMouseAt(evt, false)`, and v6 cache key, with no old trade-start callout invocation. Browser case `120` loaded v6 and confirmed capture/drag/thin-crosshair script paths are present.
- Repeatation one-shot marker tool disarm on 2026-05-19 22:20 IST:
  User observed that when a marker tool such as `Trade end` remains active, Plotly built-in controls like zoom/pan can get intercepted and place a marker at the modebar click location. `build_repeatation_review_pack.py` now starts with no marker tool armed, restores drafts with no active marker tool, lets marker tool buttons toggle on/off, disarms automatically after each marker placement, and disarms on `Clear markers`, `Clear saved draft`, and `Ignore Trade`. Marker capture now only starts when a manual marker is being dragged or a marker tool is explicitly armed; Plotly modebar/buttons/inputs/links are explicitly bypassed by marker capture.
  Cache key advanced to `repeatation_ui_20260519_tool_disarm_v7`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain `isPanelOrPlotlyControl`, `suppressNextClick`, and v7 cache key, with no default `setTool('trade_start', false)` or old trade-start callout invocation. Browser case `120` loaded v7 with zero active marker buttons on initial load.
- Repeatation plus markers and restored callouts on 2026-05-20 22:23 IST:
  User noted that always-on callouts were gone and requested start/stop/etc markers shaped like a `+` sign. `build_repeatation_review_pack.py` now restores small translucent always-on marker callouts for `Start`, `End`, `Ignore start`, and `Ignore end`, while keeping labels lighter than the original large callouts. Placed review markers now render as thin `+` shapes (`plus-v` / `plus-h`) instead of ring/circle-heavy targets; adopted hardcoded chart markers get a slightly larger subtle plus/glow so the original chart marker remains visible.
  Cache key advanced to `repeatation_ui_20260520_plus_callouts_v8`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain v8, `function plusShape`, `markerLabel(state.tradeStart, 'Start'...)`, and `markerLabel(state.tradeEnd, 'End'...)`; browser case `120` loaded v8 and confirmed plus/callout script paths are present without placing or clearing markers.
- Repeatation trade color, pan default, and live P/L on 2026-05-20 22:42 IST:
  User requested trade start/end markers and callouts use colors other than candlestick red/green, Plotly Pan should be the default selected tool, and the UI should calculate profit/loss once bullish/bearish plus start/end markers are selected. `build_repeatation_review_pack.py` now uses cyan for trade start, amber for trade end, violet for ignore markers, and a purple translucent trade-result callout. It sets Plotly `dragmode` to `pan` on load, adds an always-visible `Live trade result` panel block, adds a small chart callout when both trade markers exist, recalculates signed pips when marker points move or outcome changes, and includes `trade_profit` in downloaded marker JSON.
  Cache key advanced to `repeatation_ui_20260520_profit_pan_v9`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain v9, pan relayout, `function tradeProfit()`, and cyan/amber marker calls; browser case `120` loaded v9, panel/profit summary exists, cyan/amber/profit script paths are present, and the Plotly Pan modebar button is active.
- Repeatation P/L callout relocation on 2026-05-20 22:54 IST:
  User noted that the P/L callout should not sit directly above the aspect under review. `build_repeatation_review_pack.py` now anchors `repeatation-marker-profit-label` to a fixed chart-corner paper coordinate (`xref='paper'`, `yref='paper'`, `x=0.012`, `y=0.975`) with `showarrow=false`, so the live trade-result label no longer follows the midpoint between trade start/end markers. The drawer `Live trade result` block is unchanged.
  Cache key advanced to `repeatation_ui_20260520_profit_corner_v10`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain v10, paper-anchored P/L label code, and `showarrow: false`; browser case `120` loaded v10 with Pan active and the marker panel present.
- Repeatation auto-suggested trade markers on 2026-05-20 23:18 IST:
  User wanted a first automatic start/end suggestion based on hardcoded chart markers: start at the first selected-case touch marker (red outlined marker) and end at the next subsequent hardcoded marker, while treating manual movement as a rule-worthy override. `build_repeatation_review_pack.py` now adds an `Auto Suggest` soft button and summary panel. The suggestion scans Plotly hardcoded marker traces, prefers the first `Selected case touches` point for trade start, falls back to the first marker inside the case window, then the first visible marker, and chooses the next later hardcoded marker as trade end. It records confidence (`clean`, `fallback`, `weak`, `incomplete`, or `no marker`), rules used, marker counts, and manual override state in autosave/download JSON as `auto_suggestion`.
  Dragging or replacing an auto-suggested trade start/end marker records `manual_override=true` and lists overridden keys, with a UI reminder to add a Rule Note explaining the adjustment. Cache key advanced to `repeatation_ui_20260520_auto_suggest_v11`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain v11, `function autoSuggestTrade()`, `collectChartMarkers`, `manual_override`, and the auto-suggest button. Browser case `120` loaded v11, `Auto Suggest` and the summary panel are present, and Plotly Pan remains active. The button was not clicked during verification to avoid overwriting the user's active draft.
- Repeatation special trait / ML hint panel on 2026-05-20 23:53 IST:
  User asked to compare a unique case_id family and repeatations using existing Vedic/astro features, then highlight special characteristics usable as ML hints. `build_repeatation_review_pack.py` now builds first-pass `special_traits` for each recurrence from the SR/touch log joined by `source_event_id`. It extracts explainable traits such as `shadbala_tag`, shadbala bucket, touch planets, natal signs/houses, primary transit/natal/aspect, duration bucket, regime active count, TN/base TN score buckets, edge score bucket, and event orb bucket. Traits are compared across the same `pair_key/aspect` repeatation group using full-window bullish pips. Tags include `direction linked`, `rare`, `common`, `only bullish samples`, `only bearish samples`, or `context`; these are associative hints, not causal proof.
  Each chart marker drawer now displays an `ML trait hints` panel from `meta.specialTraits`, and `repeatation_marker_template.csv` now includes `special_trait_summary` and `special_trait_json`. Cache key advanced to `repeatation_ui_20260520_traits_v12`; refreshed all 18 served chart HTML files and synced tracked marker template/reviewer/index files. Verification: all 18 files contain v12, `specialTraits`, `function specialTraitsHtml()`, and `repeatation-special-traits`; HTTP case `120` returns v12 and includes ML trait text; browser case `120` loaded v12 with `traitCount=10`, first trait `edge score low`, and Pan active.
- Repeatation SR break confirmation logic on 2026-05-23 01:00 IST:
  User asked to define "how much below is below" for SR break confirmation and suggested 3% of the SR line. For USDJPY, 3% is far too wide, so `build_repeatation_review_pack.py` now uses an ATR/pip threshold instead: M30 uses `max(5 pips, 0.25 * ATR14)` and H1 uses `max(8 pips, 0.25 * ATR14)`. The new logic requires three steps before treating support/resistance as broken: a candle close beyond the threshold, a retest back near the SR line, and then a continuation candle in the break direction.
  Cache key advanced to `repeatation_ui_20260523_break_confirm_v26`. Auto Suggest now records and displays `break_confirmation` beside SR geometry and rule tracking. For bearish events with SR below entry, the rule still treats the first lower SR as support/target; continuation is only allowed after close-below-threshold, failed retest, and continuation. Bullish events with SR above entry use the mirrored resistance-break logic.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_005731`. Synced the served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current browser URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_break_confirm_v26`.
  Browser verification on case `43`: Auto Suggest displayed `Support break confirmed`, threshold `14.9 pips` from ATR14 `59.6`, break close line `145.730`, and explanation `Close broke below SR by threshold, then retest failed and price continued lower.` The family rule still suggested entry `146.158` to exit `145.879`, bearish `+27.9 pips`; rule tracking showed rule `+27.9 pips` vs old default `+2.2 pips`, difference `+25.8 pips`. `python -m py_compile build_repeatation_review_pack.py` passed.
- Repeatation Gann fan auto overlay on 2026-05-23 01:29 IST:
  User asked to implement Gann fans into the repeatation chart, anchored at the top wick when bearish and bottom wick when bullish around the Auto Suggest start marker. `build_repeatation_review_pack.py` now creates a data-coordinate Gann fan from the auto-start candle: bearish uses the first candle at/after start marker high/top wick; bullish uses the first candle at/after start marker low/bottom wick. The fan is stored in `auto_suggestion.gann_fan` with `anchor`, `anchor_candle`, `anchor_rule`, `timeframe_minutes`, `base_pips_per_candle`, and ratio metadata. The current first scale is `1x1 = 1 pip per candle`, with ratio lines `1x4`, `1x2`, `1x1`, `2x1`, and `4x1`.
  Cache key advanced to `repeatation_ui_20260523_gann_fan_v27`. Fan lines are Plotly shape overlays in chart data units, so zoom/pan changes only the viewport, not the fan math. The 1x1 line is emphasized, and the drawer shows the anchor wick/price plus scale note. Manual trade-start adjustment refreshes the fan anchor and records the existing manual override path.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_012325`. Synced the served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_gann_fan_v27`.
  Chrome/CDP verification on case `43` after clicking Auto Suggest: `shapeCount=6`, shapes were `repeatation-marker-gann-anchor`, `repeatation-marker-gann-1x4`, `repeatation-marker-gann-1x2`, `repeatation-marker-gann-1x1`, `repeatation-marker-gann-2x1`, and `repeatation-marker-gann-4x1`; `annotationCount=1`; no WebGL error. The bearish anchor was top wick `2025-04-04 02:30:00+05:30 @ 146.474`, with anchor candle `open 146.080 / high 146.474 / low 145.959 / close 146.412`.
- Repeatation callout declutter / Gann anchor dot on 2026-05-23 08:17 IST:
  User flagged that the Gann fan label and Start/End labels were fighting each other visually, making candles hard to read, and asked for a prominent dot where the Gann fan is placed. `build_repeatation_review_pack.py` now hides Start/End/Ignore marker callouts when the marker drawer is collapsed; opening the drawer brings the callouts back for inspection. The Gann fan no longer adds a chart text callout; its exact anchor details remain in the Auto Suggest panel and saved `auto_suggestion.gann_fan`.
  Cache key advanced to `repeatation_ui_20260523_gann_fan_v28`. The Gann anchor now draws as a stronger orange filled dot plus pale ring (`repeatation-marker-gann-anchor-dot` and `repeatation-marker-gann-anchor-ring`) while preserving data-coordinate fan lines. The collapsed drawer toggle redraws marker annotations so label clutter appears/disappears immediately.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_081416`. Synced the served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_gann_fan_v28`.
  Chrome/CDP verification on case `8`: after Auto Suggest and collapsing the drawer, `gannDot=true`, `gannRing=true`, `gannShapeCount=7`, repeatation annotations only contained `repeatation-marker-profit-label`, `markerLabelCount=0`, Auto Summary still contained Gann fan details, and no WebGL error was visible. `python -m py_compile build_repeatation_review_pack.py` passed.
- Repeatation Start/End callout spacing on 2026-05-23 08:42 IST:
  User asked to move Start/End callouts farther apart and make their pointer/line segments bolder. `build_repeatation_review_pack.py` now gives trade marker callouts a stronger annotation style when the marker drawer is open: arrowhead `2`, arrowsize `1.15`, arrowwidth `2.4`, borderwidth `1.5`, and font size `11`. Start is offset up-left (`ax=-118`, `ay=-76`) while End is offset down-right (`ax=118`, `ay=54`) so their boxes do not stack around the same candles.
  Cache key advanced to `repeatation_ui_20260523_gann_fan_v29`. Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_084021`. Synced served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_gann_fan_v29`.
  Chrome/CDP verification on case `8` after Auto Suggest with drawer open: Start annotation had `ax=-118`, `ay=-76`, `arrowwidth=2.4`, `arrowsize=1.15`, `arrowhead=2`, `borderwidth=1.5`; End annotation had `ax=118`, `ay=54` with the same strong arrow settings; Gann dot remained present and no WebGL error was visible. `python -m py_compile build_repeatation_review_pack.py` passed.
- Repeatation SR epsilon / confirmed-break target extension on 2026-05-23 09:12 IST:
  User circled back to case `8` and correctly noted that Auto Suggest was closing Start/End too close together even though the first support SR had clearly broken and retested. User also asked for a clear definition of what counts as a marker exactly at SR vs above/below SR. `build_repeatation_review_pack.py` now defines a volatility-aware SR geometry epsilon: `max(1.5 pips, min(5 pips, 0.05 * ATR14))`. Any marker within `+/- epsilon` of the entry/reference is treated as `same_as_entry` / `at SR / use marker flow`; barrier logic only applies outside that band.
  Cache key advanced to `repeatation_ui_20260523_barrier_epsilon_v30`. The bearish family rule now filters lower support targets using the epsilon clearance, records `sr_geometry_epsilon_pips`, and stores `barrier_sr_geometry` separately from the final target geometry. If the first lower support barrier has `break_confirmation.status === confirmed`, Auto Suggest moves the end to the next lower hardcoded SR/marker after the confirmed break/continuation, instead of exiting at the just-broken barrier. The Auto Suggest panel now shows `At-SR band: within +/-X pips uses normal marker flow...` and, when applicable, `First barrier checked`.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_090942`. Synced served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_barrier_epsilon_v30`.
  Chrome/CDP verification on case `8` after Auto Suggest: summary showed `Applied family rule bearish_bias_support_barrier with confirmed support break`, final target `SR is below entry: support/target (-112.6 pips from entry)`, epsilon band `+/-1.5 pips`, first barrier checked `147.650 (-9.5 pips from entry)`, rule tracking `rule +112.6 pips vs old default +53.7 pips | difference +58.9 pips`, and break confirmation `Support break confirmed threshold 8.0 pips (ATR14 30.8) | break close line 147.570`. No WebGL error was visible. Note: bullish mirrored barrier rule is not yet hard-coded as an active family rule; the epsilon/geometry machinery is now ready for it once a bullish case family is reviewed and named.
- Repeatation attribution-boundary stop on 2026-05-23 09:30 IST:
  User pointed out that case `8` should not continue into the March 10 target because the first later marker was also the start of a new aspect/zone; once the trade enters a new zone, attribution to the current case is no longer clean. `build_repeatation_review_pack.py` now adds `attributionBoundaryAfter()`, which finds the first non-selected hardcoded marker after the reviewed case window / first barrier. When a confirmed support break occurs, the bearish family rule now compares the next deeper SR target against this attribution boundary and stops at the boundary if it appears first.
  Cache key advanced to `repeatation_ui_20260523_attribution_boundary_v31`. Auto Suggest now stores `attribution_boundary` and panel text `Attribution boundary stop: ... before next event/zone takes over.` New end rule: `family_rule_next_event_boundary_after_confirmed_support_break`.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_092719`. Synced served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_attribution_boundary_v31`.
  Chrome/CDP verification on case `8` after Auto Suggest: summary showed `Applied family rule bearish_bias_support_barrier with confirmed support break, but the first later hardcoded marker starts another event/zone`, final SR geometry `-63.2 pips from entry`, attribution boundary stop `2025-03-07 23:30:00+05:30 @ 147.113`, rule tracking `rule +63.2 pips vs old default +53.7 pips | difference +9.5 pips`, and the same confirmed support break line `147.570`. No WebGL error was visible.
- Repeatation Gann anchor dot timezone fix on 2026-05-23 09:43 IST:
  User reported that the Gann fan dot looked misplaced and asked to ensure it is placed at the exact wick tip/bottom. Investigation showed the fan line used the correct anchor (`2025-03-07T19:30:00+05:30 @ 147.852` for bearish case `8`), but the dot/ring helper used `Date.toISOString()` for x0/x1, converting the surrounding circle bounds to UTC `Z` strings and visually shifting the dot left on the Plotly date axis.
  Cache key advanced to `repeatation_ui_20260523_gann_anchor_fix_v32`. `build_repeatation_review_pack.py` now uses `chartIsoFromMs()` inside `xAround()` and Gann fan line end generation so overlay shapes preserve `+05:30` chart coordinates. This also benefits other small marker/crosshair shapes that rely on `xAround()`.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_094001`. Synced served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_gann_anchor_fix_v32`.
  Chrome/CDP verification on case `8` after Auto Suggest: Gann dot bounds were `2025-03-07T19:01:11.463+05:30` to `2025-03-07T19:58:48.536+05:30`, whose center is `2025-03-07T19:29:59.999+05:30`; dot center price was `147.852`; 1x1 fan line start was `2025-03-07T19:30:00+05:30 @ 147.852`; no WebGL error was visible. `python -m py_compile build_repeatation_review_pack.py` passed.
- Case 8 ML learning note on 2026-05-23 09:52 IST:
  User asked to generate ML notes for case `8`. Added a dedicated SQLite rule note in `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`: `note_id=3`, `case_id=8`, `note_type=ml_case_review_note`.
  Structured header fields include: `scope=case_family/local`, `status=provisional_until_all_repeatations_reviewed`, `type=ml_feature_hint`, `rule_label=bearish_confirmed_support_break_attribution_boundary`, `linked_rule=bearish_bias_support_barrier`, `seed_case_id=8`, `family=AVG(ALL)|MOON::square`, `direction=bearish`, and `ml_label=confirmed_support_break_but_stop_at_next_event_boundary`.
  The note captures the reviewed behavior: case `8` is a bearish continuation after first support breaks, but trade attribution should stop at the next hardcoded event marker (`2025-03-07 23:30:00+05:30 @ 147.113`) because KETU|MOON opposition and MOON|RAHU conjunction begin there. It records Gann fan anchor at exact top wick `147.852`, first support barrier `147.650`, break threshold `8.0 pips`, break close line `147.570`, confirmed break/retest/continuation, and rule result `+63.2 pips` vs old default `+53.7 pips`.
  Astro/context reasons captured: strict shadbala avg moderate-above-minimum `384.47`, ratio `1.117`; strict drik bala avg bearish/negative `-7.04` with malefic pressure slightly exceeding benefic support (`+56.00` vs `-63.04`); low/mild chesta `9.11`; BPHS-like orb strength `0.0` and event_orb_deg `51.36`, so learn this as regime/family + SR/Gann geometry rather than exact-aspect-only; active regime count `2`, requiring attribution control; Moon has supportive dignity clues, so actual support-break confirmation is required before continuation.
  Rebuilt case 8 repeatation pack `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_094914` and synced it into the served folder. Verification: served `aspect_review_case_8_chart.html` contains `bearish_confirmed_support_break_attribution_boundary`, `confirmed_support_break_but_stop_at_next_event_boundary`, and `seed_case_id=8`.
- Repeatation local ML draft button on 2026-05-23 22:45 IST:
  User asked to proceed with the next step after building the local jyotish/Ollama workflow. `build_repeatation_review_pack.py` now exposes a `Draft ML Reason` soft button inside the marker drawer, below the existing stored `ML Notes` section. The button sends the current `case_id`, Auto Suggest summary, current live P/L if markers are present, and reviewer note text to the localhost server; the returned draft appears in a collapsible `Local Draft ML Reason` block in the drawer. Cache key advanced to `repeatation_ui_20260523_draft_ml_reason_v34`.
  `serve_repeatation_pack.py` now has a local JSON endpoint `POST /api/draft_ml_reason`. It runs `jyotish_agent\explain_case.py --case-id <case_id> --question <drawer-context>` from the project root, reads the generated `jyotish_agent\case_explanations\case_<id>_jyotish_explanation.md`, and returns the Markdown to the chart. This uses local Ollama/RAG only; no OpenAI API key is used.
  Rebuilt case 43 repeatation pack `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260523_222826` and synced it into the served folder `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current server is running on `127.0.0.1:8765` as PID `18996`. Open `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_draft_ml_reason_v34`.
  Verification: `python -m py_compile build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\explain_case.py` passed. HTTP fetch of the live case 43 chart contains `Draft ML Reason`, `api/draft_ml_reason`, `repeatation-ml-draft`, and `draftMlReason`. Direct API smoke test returned `ok=true` for case `43` and produced deterministic evidence first, followed by the local LLM commentary warning/draft. Browser automation through the node REPL Playwright path was unavailable because that environment could not resolve `playwright-core`, so verification used static live-HTML checks plus direct localhost API checks.
- Repeatation ML draft evidence alignment on 2026-05-23 22:58 IST:
  User pasted the case `43` local draft and it showed two quality problems: the deterministic section did not fully use the Auto Suggest evidence (`Support break confirmed`, attribution boundary, rule-vs-default), and the local Qwen commentary drifted into wrong `bullish bias` language despite the bearish case evidence. `build_repeatation_review_pack.py` now sends the full Auto Suggest JSON to the local agent instead of truncating it at 1800 characters. Cache key advanced to `repeatation_ui_20260523_draft_ml_reason_v35`.
  `jyotish_agent\explain_case.py` now parses the drawer's `Auto Suggest summary` JSON and `Current manual/auto trade result` from the question text, then prints them as deterministic UI/rule evidence: confidence, applied family rule, final SR geometry, first barrier checked, break confirmation threshold/line, attribution boundary marker, rule-vs-default pips, and current marker result. The deterministic heading now changes correctly: when `break_confirmation.status == confirmed`, it says the bearish family rule can continue after support breaks while still stopping at the next attribution boundary, instead of saying the case did not cleanly break support.
  The local LLM drift guard now treats `bullish bias` as a conflict when the evidence says `ret_after_72h_dir=DOWN` or the local rule notes say `direction=bearish`. If drift is detected, the draft omits the local LLM prose and keeps only deterministic analysis plus retrieved local notes. Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260523_225028`; synced it into the served folder. Current URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_draft_ml_reason_v35`.
  Verification: `python -m py_compile build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\explain_case.py` passed. Live HTML contains v35, `Draft ML Reason`, and `api/draft_ml_reason`. Direct API smoke test for case `43` with valid Auto Suggest JSON returned deterministic lines for `Support break confirmed`, final SR geometry `-30.1 pips`, attribution boundary `MOON|RAHU | conjunction_orb`, and rule tracking `rule +30.1 pips vs default +2.2 pips; delta +27.9 pips`; the bad LLM section was replaced with `Omitted`.
- Repeatation global exit and SR-line touch detection on 2026-05-25 01:35 IST:
  User reviewing case `103` noted the close marker should be placed at exact SR touch (Neptune line), or at a validated Gann fan reaction, and asked for a global rule to close at the first clean boundary: SR touch, next shaded zone, or hardcoded marker. `build_repeatation_review_pack.py` now implements that global exit rule for the active bearish family-rule flow. Auto Suggest collects shaded-zone starts, hardcoded markers, and SR-line touches; it chooses the earliest deterministic boundary after entry. SR line touches are detected even when there is no explicit hardcoded marker dot, by parsing the embedded Plotly trace JSON and decoding Plotly's compact float64 arrays with a plain-JS fallback decoder.
  Cache key advanced to `repeatation_ui_20260525_global_exit_v37`. The marker drawer now reports the selected global exit boundary and notes when SR-line touches were detected without hardcoded dots. Gann fan remains a visible/recorded evidence layer, but automatic fan-line exits are not hard-coded yet because the exact ratio/confirmation rule still needs review.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260525_013145`; synced it into the served folder `D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current verified URL: `http://127.0.0.1:8765/aspect_review_case_103_chart.html?v=repeatation_ui_20260525_global_exit_v37`.
  Browser verification on case `103` after Clear markers + Auto Suggest: Auto Suggest chose `Global exit chosen: 2025-05-16 09:00:00+05:30 @ 145.215`, reported `SR line touches detected: 2 candidate(s)`, break confirmation `Support break confirmed threshold 7.4 pips (ATR14 29.5) | break close line 145.141`, trade start `2025-05-15 22:30 @ 145.792`, trade end `2025-05-16 09:00 @ 145.215`, and live result bearish `+57.7 pips`. `python -m py_compile build_repeatation_review_pack.py` passed.
- Repeatation deterministic reason verifier on 2026-05-26 21:22 IST:
  User asked how to know whether the local LLM `Draft ML Reason` and saved ML notes are correct, especially because `BPHS-like orb strength for AVG(ALL)|MOON square is 0.0` kept appearing. `build_repeatation_review_pack.py` now adds a drawer section `Reason verifier`, a rule-based truth gate that checks the local draft plus saved ML notes against current deterministic evidence: Auto Suggest, live P/L, SR geometry, break confirmation, attribution/global-exit boundary, SR-line touch candidates, and doctrine caveats. Verdicts are `verified`, `partly verified`, or `contradiction found`; issue severities include `contradiction`, `missing`, `unsupported`, `caution`, and `info`.
  Cache key advanced to `repeatation_ui_20260526_reason_verifier_v38`. The verifier intentionally is not another creative LLM. It flags stale or conflicting notes before ML training. It specifically treats synthetic `AVG(ALL)` plus `square` BPHS-like orb `0.0` as a caution/not-applicable style clue, not a real doctrinal zero.
  `jyotish_agent\explain_case.py` now writes `event_bphs_like_orb_strength=not_applicable_for_synthetic_AVG_ALL_square (raw=...)` in deterministic evidence for synthetic AVG(ALL)/square cases, and deterministic analysis says to use `event_orb_deg` plus observed family behavior instead of treating the BPHS-like field as clean doctrine.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260526_210948`; synced it into served folder `D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260526_reason_verifier_v38`.
  Verification: `python -m py_compile build_repeatation_review_pack.py jyotish_agent\explain_case.py serve_repeatation_pack.py` passed. Static HTML contains v38 and `repeatation-ml-verifier`. Browser case `43` showed the verifier and BPHS caution. After switching from plain `http.server` to `serve_repeatation_pack.py`, the `Draft ML Reason` API returned successfully. With Auto Suggest present, the verifier correctly flagged `contradiction found` because older saved ML note text says support did not break, while current Auto Suggest evidence says support break/retest/continuation is confirmed; this is expected and useful, because it prevents stale notes from silently entering ML training.
- Case 43 contradiction correction on 2026-05-26 21:50 IST:
  The verifier's first real contradiction was corrected. SQLite `rule_notes.note_id=2` for case `43` was updated in `gann_aspect_annotations.sqlite` from the stale `astro_reason_not_strong_enough_to_break_support` wording to `astro_reason_confirmed_support_break_but_exit_first_boundary`. The corrected note now says v38 Auto Suggest classifies case `43` as confirmed support-break behavior with global first-boundary exit, while preserving the caution that Shadbala/Drik/Chesta are not unlimited-force signals.
  `build_repeatation_review_pack.py` verifier logic was also tightened so the family rule phrase `do not chase continuation ... without break confirmation` is treated as a cautionary rule requirement, not as a contradiction when break confirmation is actually present.
  Rebuilt/synced served case-family HTML, then patched generated served HTML with the corrected verifier condition after one long export timed out before all generated files reflected the source change. Browser verification on case `43` after Clear Draft + Auto Suggest + Draft ML Reason: verifier verdict changed from `contradiction found` to `partly verified`; no contradiction remains. The remaining `partly verified` status is only the intentional BPHS synthetic-field caution. Current URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260526_reason_verifier_v38`.
- Repeatation Dream Review agent on 2026-05-26 22:25 IST:
  User wanted a low-credit/local "dreaming" style reviewer that activates when `Draft ML Reason` is clicked, checks the local LLM output, corrects deterministic contradictions where safe, and reports what was corrected. Added `jyotish_agent\dream_review_agent.py` plus `POST /api/dream_review` in `serve_repeatation_pack.py`. The marker drawer now calls Dream Review automatically after a successful local draft and displays a `Dream Review` section between `Reason verifier` and `Local Draft ML Reason`.
  Cache key advanced to `repeatation_ui_20260526_dream_review_v39`. Dream Review receives the in-browser verifier report, Auto Suggest evidence, current trade result, reviewer note, and stored ML notes. It applies only narrow deterministic corrections: currently stale saved ML notes that say a support/resistance break failed when the current verifier evidence says break/retest/continuation is confirmed. Direction conflicts, SR-geometry conflicts, and ambiguous items are queued for Codex/human review instead of auto-mutating. Reports are written locally under `jyotish_agent\dream_review_reports\`; queue/correction JSONL files are ignored by git.
  Rebuilt pack: `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260526_221910`. Current server is API-aware `serve_repeatation_pack.py` on `127.0.0.1:8765` PID `11356`. Open `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260526_dream_review_v39&fresh=dream`. Browser smoke test on case `8`: `Auto Suggest` + `Draft ML Reason` produced local draft ready, verifier `partly verified` due only to BPHS synthetic-field caution, and Dream Review returned `caution_only` with report `D:\PycharmProjects\jyotish_agent\dream_review_reports\case_8_20260526_222453_dream_review.md`. No auto-correction was needed.
- Confirmed-break exit precedence fix on 2026-05-26 22:50 IST:
  User noticed case `8` was closing at the first SR touch even though the same Auto Suggest panel also said support break/retest/continuation was confirmed. Root cause: v39 global exit picked the earliest deterministic boundary after entry among first SR touch, next shaded zone, and next hardcoded marker; for case `8`, the starting candle touched the lower SR at `147.650`, so that SR won even though it should be treated as a broken barrier after confirmation.
  `build_repeatation_review_pack.py` now treats a confirmed first-barrier break as a passed barrier, not as the exit. If `break_confirmation.status === confirmed`, Auto Suggest skips that first SR touch and closes at the earliest later context boundary, with next shaded-zone boundary preferred when it ties a hardcoded marker timestamp. Cache key advanced to `repeatation_ui_20260526_confirmed_break_exit_v40`. The new reasons are `confirmed_break_next_shaded_zone_boundary` and `confirmed_break_next_hardcoded_marker_boundary`.
  Rebuilt pack: `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260526_224742`. Server restarted on `127.0.0.1:8765` PID `12916`. Static verification: served case `8` HTML contains v40 and the confirmed-break shaded/hardcoded boundary rules. `python -m py_compile build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\dream_review_agent.py jyotish_agent\explain_case.py` passed. Case `8` vs case `43` astro comparison from the touch log: case 8 has slightly stronger total strength (`384.47`, ratio `1.117`) and negative Drik pressure (`-7.04`, malefic `-63.04` stronger than benefic `+56.00`), Moon in 8th/difficult house, PLUTO/NEPTUNE rare bearish clues, and active regime count `2`; case 43 has similar total strength (`383.10`, ratio `1.093`) but positive/supportive Drik (`+8.30`, benefic `+66.20` stronger than malefic `-57.90`), Moon in 3rd/action house, touched `JUPITER` SR support, and active regime count `1`. These should be treated as ML candidate reasons, not doctrine proof.
- Rule Conflict / Lesson ledger on 2026-05-26 23:20 IST:
  User asked whether the SR-touch-vs-next-boundary conflicts are being logged for ML now, or only after all repeatations are complete. Added a deterministic `rule_lessons` SQLite table in `gann_aspect_annotations.sqlite`, plus `aspect_annotation_store.add_rule_lesson(...)`, so each rule conflict can be saved as a structured training lesson with `case_id`, `family_key`, `conflict_type`, old/new/winner rules, provisional status, astro hints, Auto Suggest evidence, verifier report, and Dream Review report.
  `serve_repeatation_pack.py` now exposes `POST /api/save_rule_lesson`; `build_repeatation_review_pack.py` loads family lessons into every repeatation and adds a drawer section `Rule Conflict Lessons` plus `Save Rule Lesson`. Running Auto Suggest drafts the lesson; pressing Save writes/upserts it into SQLite. Cache key advanced to `repeatation_ui_20260526_rule_lesson_ledger_v41`.
  First real lesson saved as `rule_lessons.lesson_id=1` for case `8`, family `AVG(ALL)|MOON::square`: conflict `sr_touch_exit_vs_confirmed_break_hold`, old rule `close_at_first_sr_touch`, winner `confirmed_break_next_shaded_zone_boundary`. Lesson text records that the first lower SR was touched early, but break/retest/continuation was confirmed, so SR is a passed barrier and exit should move to the next context boundary. Astro hints saved: negative Drik pressure, malefic pressure stronger than benefic, Moon in 8th/difficult house, PLUTO/NEPTUNE rare bearish clues, and active regime count `2`.
  Rebuilt pack: `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260526_231246`. Current server is API-aware `serve_repeatation_pack.py` on `127.0.0.1:8765` PID `11724`. Open `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260526_rule_lesson_ledger_v41&fresh=lessons`. Static/API verification: `python -m py_compile aspect_annotation_store.py build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\dream_review_agent.py jyotish_agent\explain_case.py` passed; `POST /api/save_rule_lesson` returned `lesson_id=1`; served HTML contains v41, `Rule Conflict Lessons`, the saved lesson metadata, and `api/save_rule_lesson`.
- Marker drawer recovery fix on 2026-05-27 02:55 IST:
  User reported the side menu was missing on v41. Diagnosis found two issues in `build_repeatation_review_pack.py`: the marker UI ran once at page-ready and returned if Plotly had not yet added `.js-plotly-plot`, and a nested Auto Suggest ternary had a JavaScript syntax error (`Unexpected token ':'`) that prevented the whole drawer script from parsing. Cache key advanced to `repeatation_ui_20260527_marker_attach_fallback_v43`.
  Fixes: marker UI now waits/polls for the Plotly graph div before attaching, falls back to a no-op `relayout` shim if `window.Plotly` is not exposed in the in-app browser, and the brittle Auto Suggest nested ternary was replaced with explicit `if/else` rule-reason logic. Source compile check passed: `python -m py_compile build_repeatation_review_pack.py`.
  Rebuilt pack partially through the normal builder at `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_024441`, then patched the generated HTML in that folder with the same v43 syntax fix because the first build timed out after writing the files. Server restarted on `127.0.0.1:8765` PID `21516`. Browser verification on `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260527_marker_attach_fallback_v43&fresh=syntaxfix`: `#repeatation-marker-panel` exists, `Open/Hide` works, and the drawer shows Auto Suggest / Rule Conflict Lessons sections again.
- Draft ML Reason local LLM autostart + memory feed on 2026-05-27 16:20 IST:
  User asked whether `Draft ML Reason` can fire the local LLM directly and feed `dream_review_corrections.jsonl` plus `rule_lessons` into the local RAG context every time. `serve_repeatation_pack.py` now checks `http://127.0.0.1:11434/api/tags` before running `jyotish_agent\explain_case.py`; if Ollama is not running and `D:\ollama\app\ollama.exe` exists, it starts `ollama serve` hidden with `OLLAMA_MODELS=D:\ollama\models`, writing logs to `D:\ollama\ollama_stdout.log` and `D:\ollama\ollama_stderr.log`. The `/api/draft_ml_reason` response now includes an `llm_runtime` status object.
  `jyotish_agent\explain_case.py` now loads family/current `rule_lessons` from SQLite and matching rows from `jyotish_agent\dream_review_corrections.jsonl` when present, then injects them into the deterministic case evidence as `Rule conflict lessons / training memory` and `Dream Review corrections / verifier memory`. The LLM prompt treats those sections as high-priority local memory, so future drafts can learn from saved conflicts and Dream Review corrections without the reviewer copy/pasting them.
  Verification: `python -m py_compile serve_repeatation_pack.py jyotish_agent\explain_case.py` passed. Server restarted on `127.0.0.1:8765` PID `14552` serving `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_024441`. Direct `POST /api/draft_ml_reason` for case `8` started Ollama successfully (`llm_runtime.available=true`, `started=true`), found installed model `qwen2.5:3b`, and produced `D:\PycharmProjects\jyotish_agent\case_explanations\case_8_jyotish_explanation.md`. The generated draft includes `Rule conflict lessons / training memory`; `Dream Review corrections` was absent only because no `dream_review_corrections.jsonl` file exists yet. The local LLM did run, but deterministic drift checks omitted its prose for case `8`, keeping the safer deterministic analysis; this is expected until the local model output passes verifier checks.
- At-SR wick-entry Auto Suggest fix on 2026-05-27 17:05 IST:
  User reviewed case `127` and correctly noticed that the visible reaction point was the orange Gann fan bottom-wick anchor, not the flat Auto Suggest start/end at the same hardcoded SR marker. Investigation showed the hardcoded data contains only one selected-case touch for case `127`: `2025-05-28 23:30 @ 145.125`; the marked lower point is generated from candle wick data (`2025-05-28 23:30` M30 low `144.816`) as the Gann fan anchor, so the old marker-only fallback ignored it.
  `build_repeatation_review_pack.py` now adds `wickEntryPointForStart(...)` and uses it in default marker-flow cases where the selected-case marker and next marker are inside the same SR/entry band. The hardcoded marker remains the signal/reference, but the executable trade start becomes the candle wick: bullish uses bottom wick, bearish uses top wick. `autoSuggestedPoint(...)` now preserves non-marker sources instead of overwriting them as `chart_marker`.
  Rebuilt pack: `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_034400`. Server restarted on `127.0.0.1:8765` PID `20496`. Current URL: `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_wick_entry_v45`. Browser verification after Clear markers + Auto Suggest: summary says `Selected-case hardcoded marker is at the SR/entry band, so Auto Suggest used the candle wick as executable entry`; trade start is `2025-05-28 23:30:00+05:30 @ 144.816`; trade end is `2025-05-29 00:30:00+05:30 @ 145.125`; live result is bullish `+30.9 pips`; Gann fan anchor remains bottom wick `144.816`. `python -m py_compile build_repeatation_review_pack.py` passed.
- Create a local chat/session backup after each important response or before ending a session. Include the active rollout JSONL, `state_5.sqlite`, and any relevant `state_5.sqlite-wal` / `state_5.sqlite-shm` files when present.
- Include a copy of `CURRENT_PROJECT_HANDOFF.md`, `astro_feature_inventory_from_pdfs.md`, `astro_feature_inventory_from_pdfs.yaml`, and `financial_astrology_source_notes_2026-03-13.md` in chat/session backups when project context changes.
- Do not rely on PyCharm chat history alone for recovery; use this handoff and timestamped backups as the durable record.

## Recovery Prompt For A New Chat

If starting a new chat, ask the assistant:

```text
Please read C:\Users\ADMIN\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```

## Padmanabhan Gochara + Dasha/Bhukti Timing Evidence (2026-07-10)

- User supplied a photographed first page of `Timing of Events - A Qualitative and Quantitative Study` by **R. A. Padmanabhan** and asked whether its concepts existed in the original USDJPY pipeline, then requested implementation and recovery of the complete article.
- Source recovery findings:
  - Google Books Volume 74 id `5uA5AAAAIAAJ` confirms the title/author and index start page `14`; the issue is reported as January 1985, but only snippet view is available and PDF download is disabled.
  - No lawful downloadable complete copy was found through Google Books, Internet Archive/HathiTrust-focused searches, Astrolearn holdings, or the modern magazine archive.
  - The LinkedIn post that surfaced the scan contains the same single page, not the continuation.
  - Therefore the article has **not** been studied completely. Exact Table 2, later examples, temporal-quality rules, and weights remain unavailable. See `padmanabhan_timing_source_notes.md`.
- Added `padmanabhan_timing_doctrine.py` with source-bounded, deterministic evidence:
  - whole-sign Gochara counted from natal Moon;
  - Phaladeepika 26.2 favorable houses;
  - Phaladeepika 26.3-8 Vedha mappings and Sun/Saturn + Moon/Mercury exemptions;
  - Phaladeepika 26.33-34 exceptional adverse flags;
  - explicit neutral handling of the Mercury-house-4 source conflict;
  - raw Rahu/Ketu houses, excluded from Vedha score because a reliable nodal Vedha table was not recovered;
  - Vimshottari Mahadasha/Antardasha from natal Moon nakshatra;
  - natural-quality and six-Rupa (`360 Virupa`) disposition components;
  - temporal-quality and named Yogakaraka components held at zero with `article_table_missing` status rather than invented;
  - provisional `I_reference=A_gochara+B_dasha_bhukti` and `I_USDJPY=I_USD-I_JPY`.
- Safety locks:
  - `event_padmanabhan_article_complete_flag=0`;
  - `event_padmanabhan_trade_signal_enabled=0`;
  - candidate rows carry `fx_padmanabhan_evidence_only=1`;
  - legacy FX scores, Auto Suggest, and MT5 direction are not changed.
- Pipeline integration:
  - `build_aspect_sr_touch_log.py` computes natal strict-Shadbala totals for both reference charts and writes quote/base/pair timing evidence at event best time.
  - `enrich_touch_log_padmanabhan_timing.py` attaches the same fields to existing touch/switch CSVs while preserving every row and `touch_id`.
  - `build_trade_candidates_from_touches.py` carries evidence-only fields and now returns a stable schema for all-ignore exit batches.
  - `build_repeatation_review_pack.py` exposes the pair index/direction and USD/JPY Dasha lords as plain-language comparison traits.
  - Feature inventories were updated; validation report is `padmanabhan_timing_v1_validation_20260710.md`.
- Local generated artifacts (not committed):
  - `D:\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign_padmanabhan_v1.csv` (656 rows, original touch IDs preserved).
  - `D:\GannFinancialAstro\doc\sr_touch_full_1year_switch_20260521_165758_padmanabhan_v1.csv` (732 rows, 638 unique events, original touch IDs preserved).
  - `D:\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign_padmanabhan_v1.csv/.parquet` (732 rows).
- Verification:
  - `python test_padmanabhan_timing_doctrine.py` passed.
  - `python test_strict_shadbala_doctrine.py` passed.
  - `python -m py_compile` passed for all changed Python modules.
  - PyYAML parsed the updated inventory and found both the source and feature entries.
  - Full 804-event regeneration produced 656 rows and complete pair indices; it was kept in `tmp` because nine touch placements differ from the May canonical build after later touch-engine fixes.
  - Preserved-ID enrichment + candidate rebuild produced zero differences in legacy `touch_id`, signal direction, FX hypotheses, exit action, and signed P/L.
  - Descriptive in-sample check on 638 unique events: 550 non-neutral predictions, 50.0% raw UP/DOWN agreement, with a strong bearish imbalance (473 DOWN vs 77 UP). This confirms the evidence-only decision.
  - `pytest` is not installed in the active Python 3.14 environment; the repository's direct test runners were used successfully.
- Next doctrine work:
  1. Obtain the article pages after page 14 from the user, a library, or another lawful source.
  2. Cross-check Vimshottari boundaries and natal strict-Shadbala totals against an independent trusted calculator.
  3. Recover/define temporal quality and named Yogakaraka rules with citations.
  4. Run deduplicated purged chronological walk-forward tests for A, B, and A+B separately before enabling any signal.
- Current canonical repo is `D:\PycharmProjects`; the old `C:\Users\ADMIN\PycharmProjects` recovery prompt above is historical/stale.

Updated recovery prompt:

```text
Please read D:\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```

## Full Corrected-KAS Isolated Experiment (2026-07-11)

- User requested testing the complete Krushna methodology rather than stopping at classical BAV/SAV.
- Expanded only `research_labs/ashtakavarga_validation`; canonical USDJPY/BTC, Auto Suggest, review-agent, ML-note and MT5 code remain untouched and inaccessible from the lab.
- Added corrected KAS engine:
  - `ashtakavarga_lab/kas.py`: all A/B/C/D/E event rotations, corrected Lesson 7 rows, inverse aspects, tied 4:10 transfers, D/E bonuses/exemptions, ranks, direct candidates, Samdharmi relations/restrictions and Lesson 26 result multipliers;
  - `ashtakavarga_lab/dasha.py`: Vimshottari Mahadasha/Antardasha and three equal sectors;
  - `ashtakavarga_lab/kas_evidence.py`: all 12 House B mappings, Rahu/Ketu proxies, Antardasha evidence, Sun sign/nakshatra timing, SAV-196 and Jupiter-Saturn-8 contexts;
  - `ashtakavarga_lab/evaluation.py` / `cli.py`: all-house ablations, expanding chronological folds, horizon gaps, non-overlapping outcomes, circular-shift placebos, Bonferroni correction and 0/1/2/5-basis-point cost sensitivity.
- Added published/corrected Lesson 7 fixture `fixtures/kas_lesson7_marriage_corrected.json`. It reproduces final corrected scores Saturn 32, Sun 31, Mercury 20, Jupiter 18, Venus 16, Moon 11 and Mars 11. All intermediate checked rows pass.
- Added doctrine and result records:
  - `research_labs/ashtakavarga_validation/KAS_METHOD_SPEC.md`;
  - `research_labs/ashtakavarga_validation/FULL_KAS_FIRST_RUN_FINDINGS.md`.
- Full local generated evidence/report (ignored by Git):
  - `outputs/daily_kas_evidence.parquet`: 141,264 profile/house/day rows from 2010-01-27 through 2026-03-09;
  - `reports/kas_lesson7_fixture.json`;
  - `reports/usdjpy_kas_walk_forward.json`.
- First full experiment evaluated 12 House B mappings, 12 feature/timing ablations, 3 horizons and 2 direction mappings: 864 comparisons in one correction family.
- No robust edge passed:
  - minimum Bonferroni p-value `0.2586`;
  - strongest fixed full-method cell was House 2 + first Antardasha sector + Sun gate at one day: 904 observations, 55.42% hit, raw p `0.00112`, adjusted p `0.9645`, circular-shift p `0.13`, median `+0.0383%` gross and `-0.0117%` at 5 bps;
  - simple House 1 Antardasha score was 53.86% over 1,359 observations but had adjusted p `1.0`, placebo p `0.935`, and negative median after 5 bps.
- Verification: 18 unit/isolation tests pass; corrected fixture CLI passes; 141,264-row generation and 12-house evaluation complete.
- Important limits:
  - market run is a Raman adaptation, not exact improved-Krushna-ayanamsa reproduction;
  - no source-defined currency event house exists, therefore all twelve are reported and no best house may be selected from this run;
  - event-specific karaka and delay judgments do not have a defensible currency mapping and remain explicit unresolved evidence rather than invented rules;
  - two outside BAV/SAV calculator checks remain pending.
- Decision at first run: retain as isolated research only; do not promote any KAS output into trade, Auto Suggest, ML-note, rule, marker or MT5 logic. A later user-requested display-only review advisory is documented below.

## Non-Binding KAS Review Suggestion (2026-07-11)

- User requested that the full KAS result still be available as a mere suggestion.
- Added root adapter `krushna_kas_advisory.py`, which reads the isolated corrected-KAS engine and computes a timestamp-specific USD-vs-JPY vote across all twelve House B mappings. It does not choose the best historical house.
- Advisory output includes the all-house bullish/bearish/neutral count, agreement percentage, Sun-timed subset, USD and JPY Dasha/Antardasha sectors, and detailed per-house audit JSON.
- Added mandatory locks: `evidence_only=1`, `trade_signal_enabled=0`, `trade_override_allowed=0`, `auto_suggest_input=0`, `ml_training_input=0`, and `mt5_input=0`.
- `build_repeatation_review_pack.py` now calculates a separate advisory for each recurrence at its own event-best timestamp and renders it in a dedicated `Experimental KAS suggestion` drawer block. It is not added to special-trait ranking, ML notes, Auto Suggest, family rules, markers or candidate scoring.
- Real family smoke check: all 16 AVG(ALL)-Moon-square recurrences received distinct timestamped advisories. Case 8 voted bearish 1/4/7 (bullish/bearish/neutral), while cases 43, 103, 127 and 185 voted 12/0/0 bullish. These contradictions are intentionally visible and cannot override reviewed behavior.
- Added `test_krushna_kas_advisory.py`; three lock/coverage/status tests pass.
- Repeatation UI version: `repeatation_ui_20260711_kas_advisory_v66`.
- Rebuilt the complete 16-case pack at `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260711_022803`.
- Server restarted on `127.0.0.1:8765` (PID 8520). Verified URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260711_kas_advisory_v66`.
- Playwright/Chrome browser verification: advisory block visible, Auto Suggest remains separately present, no page JavaScript errors. Screenshot: `kas_advisory_browser_check.png` in the rebuilt pack.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260711_023554`.

## Krushna Ashtakavarga Source Audit (2026-07-10)

- User supplied the 185-page PDF `Timing of Events: A Research Work in Astrology with Krushna Ashtakvarga System` by Krushna Jugalkalani and requested a thorough read.
- The complete PDF was extracted and key worksheets/diagrams were visually inspected. File SHA-256: `E18E021B84EE3A344EAC4DB11056D68C536B296E9D0CEFCFDBBE1B66455A9711`.
- After hash verification, the source PDF was moved off C: to `D:\GannFinancialAstro\doc\Jyotish_Jugalkalani Krushna_Timing of Events_A Research Work -- Jyotish -- 2021.pdf`; the original Desktop copy was removed in accordance with the project's D:-drive storage policy.
- This is a separate compilation of 36 KAS lessons originally circulated around 2000-2002. It is **not** R. A. Padmanabhan's 1985 article and does not recover Padmanabhan's missing Table 2.
- Durable source audit: `krushna_ashtakavarga_source_review_20260710.md`.
- Useful evidence candidates identified:
  - classical seven-planet BAV/SAV transit values;
  - KAS Lesson 11 seven-planet SAV transit sum centered on `196 = 7 x 28`;
  - Lesson 35 Jupiter-plus-Saturn bindu sum centered on eight;
  - explicit Rahu/Ketu Samdharmi proxies through sign, nakshatra and Navamsa dispositors.
- KAS-specific mechanics identified but quarantined:
  - inverse-aspect rule (`>4` negative, `<4` positive via `8-bindus`, `4` neutral);
  - event-specific A/B/C/D/E house worksheet;
  - 4:10 Samdharmi transfers, D/E +5 bonuses and score-12 threshold;
  - Antardasha third-sector delay and solar fine-timing rules.
- Source-quality findings:
  - modern KAS Lesson 7 explicitly corrects calculations in the supplied original lesson, including tied transfers, exactly-four neutrality and Jupiter/Venus deductions;
  - the PDF contains several internal date/formula/legend errors;
  - claimed ~90% accuracy is unsupported by a published raw dataset, locked predictions or holdout evaluation;
  - many examples are retrospective and create substantial overfitting risk;
  - medical/fertility/sexuality claims are excluded permanently from this financial pipeline.
- Doctrine conflict: source KAS uses a Krushna ayanamsa (and the current site mentions an improved KAS ayanamsa), while the user's project policy prefers Raman. Exact source reproduction and Raman-adapted market experiments must be separately labeled; BAV convention must also be versioned.
- Classical cross-check: Phaladeepika Chapter 23 supports using BAV/SAV bindus to qualify transits, but does not establish the KAS inverse-aspect, event worksheet, bonuses or transfer mechanics.
- Inventory updates added source `KRUSHNA_KAS_TIMING` and four feature records:
  `CLASSICAL_ASHTAKAVARGA_TRANSIT`, `KRUSHNA_DAILY_SAV_INDEX`, `KRUSHNA_JS_TRANSIT_SUM`, and quarantined `KRUSHNA_EVENT_WORKSHEET`.
- No USDJPY/BTC signal, Auto Suggest rule or MT5 execution behavior was changed. Recommended next implementation is a calculator-certified, evidence-only `ashtakavarga_evidence.py` followed by a separately namespaced KAS ablation module only after exact corrected specifications are frozen.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260710_233309`.

## Isolated Ashtakavarga Validation Lab (2026-07-10)

- User requested testing of the Krushna/Ashtakavarga ideas while keeping them separate from the main project.
- Added self-contained tracked lab: `research_labs\ashtakavarga_validation`.
- Isolation guarantees:
  - package imports no main trading modules;
  - all MT5, Auto Suggest, review-agent and LLM integrations are disabled;
  - generated outputs are restricted to the lab's ignored `outputs/` and `reports/` directories;
  - canonical market files are read-only inputs supplied explicitly;
  - nothing can promote itself into the main pipeline.
- Implemented:
  - complete unreduced seven-classical BAV benefic-place tables with Lagna as the eighth contributor;
  - SAV calculation, invariant validation and Raman-adapted Swiss Ephemeris reference profiles;
  - daily seven-planet SAV sum/distance from 196;
  - Jupiter-plus-Saturn own-BAV transit-sign sum/distance from eight;
  - USD, JPY and three explicitly unverified Bitcoin-location reference profiles;
  - expanding chronological evaluation with horizon gap, non-overlapping multi-day samples, Wilson intervals and price-momentum baseline;
  - exact JSON comparison for future outside-calculator BAV/SAV exports;
  - one-command reproduction via `research_labs\ashtakavarga_validation\run_first_usdjpy_test.ps1`.
- Verification:
  - 12 direct unit/isolation tests passed;
  - all 84 BAV cells and 12 SAV cells matched the published B. V. Raman standard-horoscope fixture;
  - expected BAV totals and SAV 337 matched;
  - 250 randomized charts preserved all invariants;
  - certification remains `partial_external_calculators_pending` because 0/2 independent calculators have been checked.
- First isolated USDJPY result (2010-01-27 through 2026-03-09, 4,187 joined trading days):
  - one-day fixed SAV base-minus-quote: 51.32% hit rate, 2,044 non-overlapping observations, 95% Wilson interval 49.15%-53.48%, unadjusted p=0.232;
  - one-day fixed Jupiter-Saturn differential: 49.66%, 1,482 observations, p=0.795;
  - five- and twenty-day variants also had confidence intervals spanning 50%; no simple feature was reliably distinguishable from chance.
- Durable interpretation: arithmetic is internally sound against one published fixture, but predictive evidence is not established. No main USDJPY/BTC/MT5 behavior changed.
- Full lab notes: `research_labs\ashtakavarga_validation\README.md` and `research_labs\ashtakavarga_validation\FIRST_RUN_FINDINGS.md`.
- Next gates: fill two independent calculator exports using `fixtures\external_calculator_template.json`, then add circular-shift placebos and transaction-cost sensitivity before considering more KAS mechanics.
- Recovery backup including lab code and local first-run reports: `D:\PycharmProjects\chat_session_backups\session_20260711_001352`.

## Corrected USDJPY TN Pipeline Foundation (2026-07-11)

- Replaced the recovery-only `JDML4.py` dependency with native generator
  `build_corrected_natal_event_source.py`; `rebuild_dataset_mt5_ipo_allpairs.py` is now a
  compatibility entrypoint only.
- Frozen astronomy contract:
  `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`; generator version:
  `native_tn_event_source_v1_20260711`.
- Generated 1,268 unique transit-to-natal orb windows for 2025-03-01 through 2026-03-10,
  with explicit transit/natal roles and no market-outcome fields in the event source.
- Replaced nearest-candle event mapping with strict contained-candle mapping. The corrected
  touch rebuild has 754 rows and no geometry quarantine.
- Removed the candidate-direction hindsight leak. Candidate direction now defaults to the
  timestamp-available FX hypothesis, observed 72-hour direction is label-only, and trade
  entry defaults to the next available bar open. Corrected result: 607 potential trades,
  231 wins, 375 losses and 148 ignored, so the raw heuristic is not trade-ready.
- Added directional family identity, for example `TN::MOON->MERCURY::trine`; opposite
  transit/natal roles can no longer share notes or rules through the unordered display pair.
- Created `gann_aspect_annotations_raman_v2.sqlite`: schema version 2, 754 cases and 205
  directional families. It intentionally starts with zero annotations/completed reviews.
- Generated a corrected 15-recurrence review pack for `TN::MOON->MERCURY::trine` at
  `D:\GannFinancialAstro\doc\repeatation_review_case_55_mercury_moon_trine_20260711_204603`.
- Browser Auto Suggest now calls `POST /api/auto_suggest`, whose active engine is
  `reviewer_rule_replay.auto_suggest_case` in retrospective-review-only mode. A live API
  smoke check for case 55 returned bullish `+2.3 pips`, from the first selected-window SR
  touch to the next hardcoded attribution boundary.
- Fixed remaining local Jyotish/RAG family reconstruction to preserve directional family
  keys. Also corrected an explanation bug that treated every square aspect as synthetic;
  the BPHS-like non-applicability warning now applies only to `AVG(ALL)`.
- Verification at this checkpoint: `62 passed` via `python -m pytest -q`; corrected API
  endpoint smoke test passed.
- Still pending from the audit roadmap:
  external Shadbala/Drik expected values and certification, purged timestamp-safe live
  inference evaluation, BTC rolling/no-lookahead evidence mode, and removal of the dead
  archived JavaScript Auto Suggest source after visual parity checks.
- New product direction requested after this checkpoint: design a lightweight Windows
  research/live workstation with parameterized astrology charts, TradingView-like drawing
  tools, local LLM evidence/verification, and a supervised always-reconnecting MT5 backend.

## Native Gann Astro Desk Release (2026-07-12)

- The supported user runtime is now a real native Windows application rather than a
  browser URL:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
- Release contract:
  - version `0.1.0`;
  - PyInstaller one-folder build using pywebview plus Microsoft WebView2;
  - SHA-256 `CA26CDB4073002531C173C5642E948CF4560ECA8320B3FDE26F191E95EE7B0B1`;
  - 1,656 files / 698,259,121 bytes;
  - astronomy contract `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`;
  - MT5 execution remains `read_only_market_data` and `tradeAllowed=false`.
- The release bundles the corrected event/touch sources, H1/M30 price archives,
  annotation seed DB, Swiss Ephemeris files, Python corrected-data workers, Node,
  the Codex SDK bridge, and the compiled frontend. Writable state stays under
  `D:\GannFinancialAstro\app_data`.
- Native behavior verified:
  - main `Gann Astro Desk` WebView2 window is responsive;
  - internal backend uses a private random loopback port, with no localhost URL in
    the user workflow;
  - Codex bridge reports `codex-sdk`;
  - MT5 reconnect supervisor reports connected to MetaQuotes-Demo while preserving
    read-only execution;
  - Analyze Aspect opens as a second native window, not Edge/Chrome;
  - corrected baseline loads 1,268 events and 754 touches;
  - toolbar and parameter drawer were visually checked at Windows display scaling.
- Reproducible D-only packaging lives in
  `gann-astro-desk\packaging\build_windows_exe.ps1` and
  `gann-astro-desk\packaging\gann_astro_desk.spec`.
- Rust/MSVC decision:
  - neither is required for the working pywebview release;
  - Rust can later be installed on D through `RUSTUP_HOME`/`CARGO_HOME`;
  - Visual Studio Build Tools can place most workloads/cache on D, but some shared
    installer and Windows SDK servicing files remain on C;
  - defer both until a signed Tauri/MSI route is intentionally selected.
- Added immutable timestamp-safe MT5 history snapshots:
  - contract `MT5_TIMESTAMPED_CLOSED_BARS_V1`;
  - explicit requested range, capture time and as-of cutoff;
  - only fully closed bars are retained;
  - incomplete bars are counted/excluded;
  - Parquet plus atomic JSON manifest and SHA-256;
  - storage under `D:\GannFinancialAstro\app_data\market_snapshots`;
  - UI command: `Snapshot MT5 range` in Market source parameters.
- Real packaged snapshot verification retained:
  `USDJPY_H1_20260712T081855Z_4cb984b1`, 48 closed H1 bars,
  SHA-256 `8DD95DE8C9AC9814239D0520C819DF3574D3088DEB1B4EB5FB787F2D7CFED65C`.
- Packaged corrected-worker verification exposed and fixed a timestamp edge case:
  an event beginning at 02:01 was incorrectly rejected when its first genuinely
  contained H1 candle began at 02:30. Full-source coverage is now checked before
  cropping, while contained-candle mapping remains strict. The final packaged job
  completed with one event, one SR touch and 22 evidence rows; baseline was restored
  and all temporary verification jobs/artifacts were removed afterward.
- Verification at this checkpoint:
  - `76 passed` for the full Python suite;
  - `5 passed` for frontend tests;
  - Oxlint clean;
  - TypeScript/Vite production build clean;
  - packaged native health, Codex, MT5 snapshot, generation worker and Analyze Aspect
    smoke checks passed.
- Remaining deliberate gates:
  - promote an immutable MT5 history snapshot into a corrected event artifact only
    through an explicit versioned/no-lookahead operation;
  - consolidate retrospective and future live Auto Suggest behavior into one
    timestamp-safe decision engine before enabling any execution path;
  - external Shadbala/Drik certification and purged out-of-sample validation remain
    required;
  - code signing or a Tauri/MSI installer is optional distribution work, not a runtime
    blocker.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260712_145424_native_windows_exe`.

## Promoted MT5 Research Artifacts (2026-07-12)

- Completed the explicit Snapshot -> Verified Price Source -> Corrected Artifact pipeline in
  Gann Astro Desk. Live MT5 bars cannot become research evidence merely by being visible:
  the user must first capture a closed-bar snapshot, then explicitly verify/promote it, then
  generate a versioned corrected artifact from that immutable source.
- New contracts:
  - capture contract `MT5_TIMESTAMPED_CLOSED_BARS_V1`;
  - promoted-source contract `PROMOTED_MT5_PRICE_SOURCE_V1`;
  - each promotion revalidates path containment, manifest fields, no-lookahead/immutable
    locks, OHLC geometry, timezone-aware unique timestamps, closed-bar cutoff, bar count,
    first/last opens, last close and Parquet SHA-256;
  - generation resolves the source both when queued and in the worker, and refuses to run
    if the queued SHA has changed;
  - artifact activation rechecks the artifact manifest's recorded source SHA.
- Persistent D:-drive registry and files:
  - registry table `app_price_sources` in
    `D:\GannFinancialAstro\app_data\gann_aspect_annotations_raman_v2.sqlite`;
  - promoted archives under `D:\GannFinancialAstro\app_data\price_sources`;
  - immutable source snapshots remain under
    `D:\GannFinancialAstro\app_data\market_snapshots`;
  - generated artifacts remain under `D:\GannFinancialAstro\app_artifacts`.
- Real retained research source:
  - snapshot `USDJPY_H1_20260712T105022Z_dc53a058`;
  - 192 fully closed H1 bars from `2026-07-01T00:00:00Z` through
    `2026-07-10T23:00:00Z`, captured/as-of `2026-07-12T10:50:22Z`;
  - Parquet SHA-256
    `8D0C8C9C3C4DAF403E8E40B139CCDA134E598E43250A42C3C8C4B6CD1415154E`;
  - promoted source `mt5_USDJPY_H1_20260712T105022Z_dc53a058`, verified on every
    resolution and idempotent when promoted again.
- Real retained corrected artifact:
  - artifact `tn_2beda5f38c4f4cc2bb866fa88c174bf2`;
  - label `July 2026 promoted MT5 research`;
  - 29 corrected TN events and 12 SR touches;
  - active parameters preserve the promoted source ID, source contract, as-of time and SHA;
  - restart verification restored the July source/range and rendered 187 H1 candles with
    29 visible aspects.
- Native UI workflow now exposes, in order, `Snapshot MT5 range`, a captured-snapshot
  selector with already-promoted status, `Verify and promote snapshot`, and `Price archive`
  selection. Incompatible source/timeframe combinations are rejected or reset to baseline.
  The bundled corrected baseline remains immutable and selectable.
- Native release updated in place:
  - version `0.2.0`;
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `C26E8AA3EFC63DD2AAE4C13BDBB9CC14F4084F738BFC57BCCBA0E843DB56D90B`;
  - 1,656 files / 698,293,933 bytes;
  - packaged visual QA confirmed the July chart, 29-aspect count, H1 archive, promoted
    snapshot status and MT5 read-only connection.
- Verification at this checkpoint:
  - `79 passed` for the full Python suite;
  - `5 passed` for frontend tests;
  - backend package suite passed (`16 tests`);
  - Oxlint clean;
  - TypeScript/Vite production build clean;
  - packaged API restart, health, price-source registry, snapshot lineage and native UI
    checks passed.
- Canonical tracked annotation seed contains the new empty app registry tables only: zero
  price-source, artifact and generation-job rows. The retained July source/artifact live only
  in the writable D:-drive application state.
- Remaining deliberate gate: consolidate retrospective review Auto Suggest and future/live
  inference into one timestamp-safe, versioned decision engine with purged no-lookahead
  evaluation before any execution path can consume promoted artifacts. MT5 remains
  `read_only_market_data` and `tradeAllowed=false`.
- Recovery backup:
  `D:\PycharmProjects\chat_session_backups\session_20260712_165050_snapshot_promotion`.
