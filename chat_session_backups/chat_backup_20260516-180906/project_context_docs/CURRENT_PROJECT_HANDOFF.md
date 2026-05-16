# Current Project Handoff

Last updated: 2026-05-16 18:08 IST

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
950ae29 Add Codex app recovery instructions
e548df5 Add latest recovery handoff backup
ad0021a Record GitHub recovery remote
c6e70b9 Prepare GitHub recovery package
278182d Export generated charts for aspect cases
83935b7 Embed price chart in review page
258ad73 Export static review pages
73f2aac Export aspect review snapshots
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

1. Open `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11_chart.html` and `C:\Users\ADMIN\Desktop\doc\aspect_review_case_15_chart.html` to confirm the real case snapshots have the right chart context for manual review.
2. If accepted, run `--export-all-case-charts` in batches rather than all 619 at once, because each snapshot recomputes chart/SR context and can take several seconds.
3. Next annotation workbench step: add simple previous/next same-aspect navigation to exported review pages, then add a low-friction way to create trade/ignore/rule-note commands from the page.
4. User inspects `sr_touch_full_1year_switch_20260511_015700.html`, especially doctrine score lines in hovers after transit-sign dignity was added.
5. Compare the prior transitsign baseline chart against `sr_touch_full_1year_switch_20260511_220046.html` for AVG(ALL) regimes. If the expanded hovers are useful visually, keep the AVG(ALL) expansion as an explainability feature but calibrate it separately from directional ML.
6. Extend `evaluate_transitsign_walk_forward.py` with walk-forward rule calibration tests for `fx_pair_net_score` and `fx_doctrine_pair_net_score`: normal vs inverted, train-selected thresholds, and blended score variants.
7. Add weekly mode using the uncapped transitsign touch log and a `>5d` duration bucket.
8. Add feature columns from the PDF inventory one group at a time:
   midpoint hits, stellium, T-square/grand-cross/grand-trine, Dhruvank daily signal.
9. For Gann: manually review OCR pages for `GANN_PRICE_LONGITUDE_HIT`, `GANN_OUTER_PLANET_AVERAGE`, and `GANN_CIRCLE_ACTIVE_ANGLE`; only then implement deterministic feature columns with source-page metadata.

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
- Create a local chat/session backup after each important response or before ending a session. Include the active rollout JSONL, `state_5.sqlite`, and any relevant `state_5.sqlite-wal` / `state_5.sqlite-shm` files when present.
- Include a copy of `CURRENT_PROJECT_HANDOFF.md`, `astro_feature_inventory_from_pdfs.md`, `astro_feature_inventory_from_pdfs.yaml`, and `financial_astrology_source_notes_2026-03-13.md` in chat/session backups when project context changes.
- Do not rely on PyCharm chat history alone for recovery; use this handoff and timestamped backups as the durable record.

## Recovery Prompt For A New Chat

If starting a new chat, ask the assistant:

```text
Please read C:\Users\ADMIN\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```
