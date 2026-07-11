# Gann / Financial Astrology Research Workspace

Private recovery repository for the USDJPY financial astrology research pipeline.

## Current Safety Status

Read [end_to_end_financial_astro_audit_20260711.md](end_to_end_financial_astro_audit_20260711.md)
before generating data or using review rules.

- The current tracked USDJPY source/touch/case artifacts are preserved as
  `legacy_double_sidereal_research_history` and are not live/ML ground truth.
- New astronomy must use `RAMAN_SWISSEPH_SINGLE_SIDEREAL_*`, explicit transit/natal roles, and
  geometry validation.
- Auto Suggest and completed reviews are retrospective research. They are not a live policy.
- The MT5 adapter remains dry-run/manual-confirmation only.

## Resume In A New Chat

Use this prompt:

```text
Please read D:\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```

On another machine, clone the repository first, then point the assistant to the cloned `CURRENT_PROJECT_HANDOFF.md`.

## Resume In Codex Windows App

Short paste-in prompt:

```text
This is my private Gann / financial astrology USDJPY research workspace. Please start by reading CURRENT_PROJECT_HANDOFF.md, then run git status --short and git log --oneline -8. The GitHub recovery repo is https://github.com/gouravdamade/gann-financial-astro-research. Keep CURRENT_PROJECT_HANDOFF.md updated after meaningful work, create a timestamped chat_session_backups backup, commit changes, and push to origin/master so I can switch between Codex app and PyCharm without losing state.
```

If the app starts outside this folder, open or clone:

```text
D:\PycharmProjects
```

GitHub remote:

```text
https://github.com/gouravdamade/gann-financial-astro-research.git
```

## What This Repo Contains

- Core Python scripts for touch-log generation, dashboard export, annotation storage, and walk-forward evaluation.
- `CURRENT_PROJECT_HANDOFF.md`, the durable project state and next-action record.
- Source notes and feature inventory from the PDF study.
- Curated current CSV/parquet/sqlite data needed to resume the latest workflow.
- A timestamped chat/session backup folder with the latest handoff and modified scripts.

## Canonical Architecture

1. `financial_astro_ephemeris.py`: one Raman Swiss-Ephemeris calculation path.
2. `astro_event_contract.py`: scoped event identity and transit/natal role contract.
3. `rebuild_dataset_mt5_ipo_allpairs.py`: recovery source rebuild; still requires the external
   JDML compatibility runtime and is the next replacement target.
4. `build_aspect_sr_touch_log.py`: corrected touch/evidence builder.
5. `build_trade_candidates_from_touches.py`: candidate feature/scoring layer.
6. `aspect_annotation_store.py` and `build_repeatation_review_pack.py`: manual review storage/UI.
7. `reviewer_rule_replay.py`: retrospective rule replay only.
8. `evaluate_transitsign_walk_forward.py`: purged exploratory evaluation.

The BTC weekly tools and `research_labs/ashtakavarga_validation/` are separate descriptive or
experimental surfaces. They do not feed live USDJPY decisions.

## Current Important Data Files

These are recovery artifacts from the legacy astronomy contract. Do not overwrite them during
the corrected rebuild:

- `aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
- `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
- `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet`
- `usd_jpy_h1_mt5_metaquotes_demo_full.parquet`
- `usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet`
- `gann_aspect_annotations.sqlite`

## Common Commands

Install the documented environment:

```powershell
python -m pip install -r .\requirements-dev.txt
```

Run the full default test suite:

```powershell
python -m pytest
```

Export a real generated chart snapshot for one annotation case:

```powershell
python .\sr_touch_lazy_dashboard.py --touch-log .\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv --price .\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet --export-case-chart --case-id 15 --case-timeframe auto --export-dir D:\GannFinancialAstro\doc --export-max-lines 60
```

Export a static review page:

```powershell
python .\aspect_annotation_store.py --export-review-html --case-id 11
```

Check the local recovery state:

```powershell
git status --short
git log --oneline -8
```

Static checks used by the July 2026 audit:

```powershell
python -m ruff check . --exclude chat_session_backups --exclude legacy_project_pack --exclude tryapp-android
python -m radon cc -s -n C .
```

## Data Promotion Rules

A row may enter current RAG, ML, or future demo inference only when it has:

- a supported astronomy contract version;
- explicit `event_scope`, `event_transit_body`, and `event_natal_body`;
- geometry within the declared orb;
- timestamp-safe features and labels;
- documented doctrine status (`certified`, `source_aligned_provisional`, or `experimental`);
- an out-of-sample validation record for any trading claim.

## Privacy Note

Keep this repository private. It contains research data, local project paths, generated datasets, and recovery notes.
