# Gann / Financial Astrology Research Workspace

Private recovery repository for the USDJPY financial astrology research pipeline.

## Resume In A New Chat

Use this prompt:

```text
Please read C:\Users\ADMIN\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```

On another machine, clone the repository first, then point the assistant to the cloned `CURRENT_PROJECT_HANDOFF.md`.

## What This Repo Contains

- Core Python scripts for touch-log generation, dashboard export, annotation storage, and walk-forward evaluation.
- `CURRENT_PROJECT_HANDOFF.md`, the durable project state and next-action record.
- Source notes and feature inventory from the PDF study.
- Curated current CSV/parquet/sqlite data needed to resume the latest workflow.
- A timestamped chat/session backup folder with the latest handoff and modified scripts.

## Current Important Data Files

- `aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
- `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
- `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet`
- `usd_jpy_h1_mt5_metaquotes_demo_full.parquet`
- `usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet`
- `gann_aspect_annotations.sqlite`

## Common Commands

Export a real generated chart snapshot for one annotation case:

```powershell
python .\sr_touch_lazy_dashboard.py --touch-log .\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv --price .\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet --export-case-chart --case-id 15 --case-timeframe auto --export-dir C:\Users\ADMIN\Desktop\doc --export-max-lines 60
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

## Privacy Note

Keep this repository private. It contains research data, local project paths, generated datasets, and recovery notes.
