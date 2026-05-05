# Current Project Handoff

Last updated: 2026-05-05 IST

Use this file to recover context in a new chat if PyCharm/Codex chat history is lost.

## Project Goal

Build a deterministic financial astrology research pipeline for USDJPY that:

1. Computes aspect/SR touch events using a Japanese Yen reference chart.
2. Splits chart views by timeframe:
   - M30/H1 for short aspects `<= 24h`
   - Daily for longer aspects `> 24h` and currently `<= 5d`
   - Merged H1 for the original all-aspects view
3. Adds transparent rule-layer hypothesis scores before ML.
4. Later uses ML to validate/calibrate those hypothesis scores with walk-forward validation.

## Git State

Repo:

`C:\Users\ADMIN\PycharmProjects`

Git executable:

`C:\Program Files\Git\cmd\git.exe`

Latest commits:

```text
6c3dbf2 Scope dominant rule hit to hovered aspect
356ee20 Add rule scores to aspect window hovers
6780c08 Add current project handoff notes
dbe81c0 Show Yen IPO rule scores in chart hovers
04d65f0 Add rule-layer aspect strength scoring
8094136 Add PDF-derived astro feature inventory
d6004ac Add M30 chart timeframe support
9082584 Add merged hourly chart mode
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
C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet
C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored.parquet
```

Latest chart export with score hovers:

```text
C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260504_213821.html
C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260504_213821.csv
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
- `hourly`: H1 candles; short aspects `<= 24h`; Moon lines included.
- `daily`: daily candles; long aspects `> 24h`; Moon SR lines hidden.
- `merged`: H1 candles; all aspect durations together; Moon lines included.
- `switch`: one HTML with buttons. If M30 price file is supplied, buttons are M30/H1/Daily.

Latest switch validation:

```text
M30:    424 rows, 60-1440 minutes
Hourly: 424 rows, 60-1440 minutes
Daily:  116 rows, 1500-6660 minutes
```

### Current 5-Day Cap

Events longer than 5 days are currently filtered in two places:

- `build_aspect_sr_touch_log.py`: `--max-event-days`, default `5.0`
- `sr_touch_lazy_dashboard.py`: loader filters `event_duration_minutes <= 5 * 1440`

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

Feature inventory files:

- `astro_feature_inventory_from_pdfs.md`
- `astro_feature_inventory_from_pdfs.yaml`

PyYAML installed:

```text
PyYAML 6.0.3
```

YAML validation:

```text
sources: 5
doctrine_locks: 4
features: 17
```

Important PDF conclusion:

- The two strict Jyotish PDFs are architecture/doctrine-control docs.
- AstroEcon and Futuretek/Dhruvank are experimental feature sources.
- Gann PDF did not extract readable body text; OCR is needed before implementing Gann rules.

## Useful Commands

Export latest switch chart with M30/H1/Daily and hover scores:

```powershell
python C:\Users\ADMIN\PycharmProjects\sr_touch_lazy_dashboard.py `
  --touch-log C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst.csv `
  --price C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet `
  --export-full-year `
  --export-dir C:\Users\ADMIN\Desktop\doc `
  --export-max-lines 60 `
  --timeframe switch
```

Rebuild scored trade candidates from latest switch CSV:

```powershell
python C:\Users\ADMIN\PycharmProjects\build_trade_candidates_from_touches.py `
  --touch-log C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260504_213821.csv `
  --price C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet `
  --output-csv C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored.csv `
  --output-parquet C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored.parquet
```

Check Git:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -C 'C:\Users\ADMIN\PycharmProjects' status --short
& 'C:\Program Files\Git\cmd\git.exe' -C 'C:\Users\ADMIN\PycharmProjects' log --oneline -8
```

## Next Recommended Steps

1. Regenerate the full touch log so it includes the new `base_tn_*` USD reference fields.
2. Export a fresh switch chart from that regenerated touch log and inspect the new `FX pair hypothesis` hover block.
3. Rebuild scored trade candidates and compare `fx_hypothesis_direction` against outcomes.
4. Make `max-event-days` configurable in dashboard loader and builder, then add weekly mode.
5. Add purged walk-forward ML evaluation for `trade_candidates_aspect_sr_1y_outer_scored.parquet`.
6. Add feature columns from the PDF inventory one group at a time:
   midpoint hits, stellium, T-square/grand-cross/grand-trine, Dhruvank daily signal.

## Recovery Prompt For A New Chat

If starting a new chat, ask the assistant:

```text
Please read C:\Users\ADMIN\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```
