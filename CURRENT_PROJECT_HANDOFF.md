# Current Project Handoff

Last updated: 2026-05-15 00:15 IST

Use this file to recover context in a new chat if PyCharm/Codex chat history is lost.

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

Latest commits before this handoff update:

```text
9ea6dbf Exclude context slow pairs from short term views
376e779 Exclude slow planet pairs from short term views
97e2091 Show USDJPY hypothesis by default in hovers
7375df8 Add active regime zone hovers
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

1. User inspects `sr_touch_full_1year_switch_20260511_015700.html`, especially doctrine score lines in hovers after transit-sign dignity was added.
2. Compare the prior transitsign baseline chart against `sr_touch_full_1year_switch_20260511_220046.html` for AVG(ALL) regimes. If the expanded hovers are useful visually, keep the AVG(ALL) expansion as an explainability feature but calibrate it separately from directional ML.
3. Extend `evaluate_transitsign_walk_forward.py` with walk-forward rule calibration tests for `fx_pair_net_score` and `fx_doctrine_pair_net_score`: normal vs inverted, train-selected thresholds, and blended score variants.
4. Add weekly mode using the uncapped transitsign touch log and a `>5d` duration bucket.
5. Add feature columns from the PDF inventory one group at a time:
   midpoint hits, stellium, T-square/grand-cross/grand-trine, Dhruvank daily signal.
6. For Gann: manually review OCR pages for `GANN_PRICE_LONGITUDE_HIT`, `GANN_OUTER_PLANET_AVERAGE`, and `GANN_CIRCLE_ACTIVE_ANGLE`; only then implement deterministic feature columns with source-page metadata.

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

- Update this handoff after each meaningful work session, especially after long-running builds, generated artifacts, failed rebuild attempts, or chat/session recovery work.
- Create a local chat/session backup after each important response or before ending a session. Include the active rollout JSONL, `state_5.sqlite`, and any relevant `state_5.sqlite-wal` / `state_5.sqlite-shm` files when present.
- Include a copy of `CURRENT_PROJECT_HANDOFF.md`, `astro_feature_inventory_from_pdfs.md`, `astro_feature_inventory_from_pdfs.yaml`, and `financial_astrology_source_notes_2026-03-13.md` in chat/session backups when project context changes.
- Do not rely on PyCharm chat history alone for recovery; use this handoff and timestamped backups as the durable record.

## Recovery Prompt For A New Chat

If starting a new chat, ask the assistant:

```text
Please read C:\Users\ADMIN\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```
