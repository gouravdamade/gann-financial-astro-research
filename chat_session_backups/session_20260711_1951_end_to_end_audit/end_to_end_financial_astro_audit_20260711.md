# End-To-End Financial Astrology Audit - 2026-07-11

## Decision

The workspace remains a useful **research and manual-review system**, but the current USDJPY
event/touch/case artifacts are **not eligible for live autonomous trading or ML ground truth**.
The legacy natal-event source was generated with a double sidereal adjustment on the 1889
reference chart, and its transit/natal role was later lost by alphabetically sorting pair labels.
Those defects affect the identity and explanatory features of the reviewed event families.

The historical reviews, notes, screenshots, and rule ideas should be preserved as research
history. They must be regenerated and revalidated against the corrected astronomy contract
before they can influence a demo or live decision.

This is not a judgment that Jyotish has or lacks predictive value. Astronomy can be certified
numerically, doctrine can be checked against declared sources, and trading claims must then be
tested out of sample. Those are three separate gates.

## Audit Scope

The pass covered all canonical Python and Markdown files outside timestamped backups,
generated review packs, virtual environments, and the unrelated `tryapp-android/` directory.
It included:

- 70 Python files, including 14 root tests and isolated-lab tests;
- 24 Markdown files, including generated-pack READMEs;
- active CSV, parquet, SQLite, YAML, JSON, and corpus contracts;
- the recovery-only runtime under `D:\Trading_Algo\New folder` where canonical scripts still
  depended on it;
- compile, Ruff, Vulture, Radon, unit/integration tests, dataset geometry checks, and a corrected
  source-generation proof run.

The audit is exhaustive at the module/interface level and targeted at the highest-risk function
paths. It is not a formal proof of every numerical branch in the two largest UI/decision files.
Their complexity is itself an audit finding.

## Critical Findings

### 1. Legacy USDJPY natal-event astronomy is invalid

`JDML4.py` requested sidereal Swiss-Ephemeris positions and then subtracted ayanamsa again for
historical fallback positions and lunar nodes. It also used tropical houses beside sidereal
planet positions.

At `2025-05-28 16:30 UTC`, for example:

- Raman ayanamsa: `22.765690703` degrees;
- correct Raman true-node longitude: `331.622323551` degrees;
- legacy double-adjusted result: `308.856632848` degrees.

Every classical natal longitude in the 1889 source snapshot was displaced by approximately
`20.862224307` degrees from the corrected Raman value. The old natal Moon was
`40.225446` degrees; the corrected value is `61.087670` degrees.

The correction follows the documented Swiss-Ephemeris contract: set sidereal mode and request
`FLG_SIDEREAL` once; use `houses_ex(..., FLG_SIDEREAL)` for sidereal cusps.

Sources:

- https://github.com/astrorigin/pyswisseph/blob/master/docs/programmers_manual/sidereal_mode.rst
- https://www.astro.com/swisseph/swephprg.htm?nhor=16

**Impact:** old source events can be internally close to their old, shifted natal chart while
still representing the wrong astronomical event. Case IDs `8`, `43`, `103`, `127`, `185`, and
the rest of the current case database cannot be promoted as corrected Raman examples.

**Applied control:** `financial_astro_ephemeris.py` now provides one canonical Raman/Swiss path,
true-node handling, sidereal Porphyry cusps, exact timestamp calculations, and full-index cache
keys. Core builders now attach an astronomy-contract version.

### 2. Transit/natal role information was lost

The legacy logger sorted body names alphabetically. A row labeled `AVG(ALL)|MOON square` did not
say whether AVG(ALL) or Moon was transiting. Downstream code assumed `b1=transit` and
`b2=natal`, causing false event distances of roughly `51-86` degrees and repeated
`BPHS-like strength=0.0` explanations.

Stored peak snapshots show that 426 of 804 old source rows had the transit body in `b1`, while
378 had it in `b2`. In the reviewed AVG(ALL)-Moon family, 17 of 18 rows were actually transiting
Moon to natal AVG(ALL).

**Applied control:** `astro_event_contract.py` adds explicit `event_scope`,
`event_transit_body`, `event_natal_body`, role-resolution status, scoped family keys, and a
geometry check. A corrected March proof run produced 16 TN events with a maximum inferred orb
of `0.349` degrees. A corrected touch proof run produced 14 rows with a maximum orb of `0.263`
degrees.

## High-Risk Findings

### 3. Retrospective review and live inference are still mixed

`reviewer_rule_replay.py` uses the known full-window outcome when choosing a review direction.
That is valid for retrospective annotation, but it is future leakage if reused at decision time.
The upcoming-aspect generator is astronomy-only and the MT5 executor is separately guarded;
they must remain separate until a live policy consumes only information available at the stated
decision timestamp.

**Required:** create an explicit `research_replay` versus `live_inference` API boundary, with
`signal_time`, `decision_time`, `fill_time`, and `label_available_time` stored separately.

### 4. Two Auto Suggest engines can diverge

Auto Suggest exists in both a very large embedded JavaScript implementation in
`build_repeatation_review_pack.py` and Python replay logic in `reviewer_rule_replay.py`.
The Python function `auto_suggest_case` has cyclomatic complexity 110; its break-confirmation
helper is also highly complex. Fixing one path does not prove the other path changed identically.

**Required:** make Python emit a versioned decision packet and let the browser only render it.
Keep one shared rule registry and one deterministic replay implementation.

### 5. The repository was not self-contained

Several active scripts imported untracked code from `D:\Trading_Algo\New folder`. During this
audit, the active SR chart/log paths were moved to the canonical exact ephemeris helper. The
source event rebuild still uses recovery-only `JDML4.py`, patched at runtime, and Telegram
helpers still use their external runtime.

**Required:** replace the remaining JDML source-generation dependency with a repository-owned
event generator, or vendor an immutable, hash-verified compatibility snapshot. A fresh clone
must not depend on an undocumented neighboring folder.

### 6. “Full/strict Shadbala” was overstated

The previous `STRICT_SHADBALA_V3_FULL_COMPONENT_V1` label implied stronger certification than the
implementation earned. Source comparison found and corrected:

- Drekkana Bala category boundaries;
- doubled Moon Paksha Bala;
- doubled Sun Ayana Bala;
- Sun Chesta = Ayana and Moon Chesta = Paksha.

The renamed V4 implementation remains **source-aligned provisional**, because actual sunrise,
fully certified Abda/Masa lords, full mean/true-motion Chesta, Yuddha arithmetic, and an external
calculator baseline remain pending. Rahu/Ketu remain excluded from classical seven-planet
Shadbala totals. AVG(ALL) is a component mean, not an eighth planet.

### 7. Legacy notes could contaminate local retrieval

`jyotish_agent/build_corpus_index.py` previously indexed all rule notes and representative touch
rows without checking their astronomy provenance. That allowed stale case explanations to return
through RAG after the astronomy code had been corrected.

**Applied control:** only notes/rows tied to a supported
`RAMAN_SWISSEPH_SINGLE_SIDEREAL_*` contract are now indexed. Legacy or unversioned material is
counted and quarantined. Local LLM text remains draft commentary, never official evidence.

### 8. BTC weekly evidence is descriptive, not walk-forward

The BTC chart correctly keeps TN role direction, skips Moon and the Rahu-Ketu pair, and applies
the requested duration/frequency classification. However:

- family classification uses all historical outcomes before drawing earlier chart periods;
- local crest/trough comments inspect future neighboring weeks;
- SR-line selection ranks full-history touches;
- early ATR values use backfill;
- the Gann SR formula and proposed Bitcoin birthplace remain experimental.

These are acceptable for visual research when labeled descriptive, but not for historical
prediction or live evidence. A time-purged classification must be added before promotion.

## Medium-Risk Findings

### Walk-forward model

The evaluator previously admitted same-bar touch prices and selected features using the full
future dataset. It now applies a true outcome-horizon embargo, selects features from the first
training slice, and excludes same-bar OHLC/touch/entry fields until timestamp semantics are
explicit. The remaining dataset is still small and high-dimensional (about 729 rows and roughly
381 candidate features), so performance estimates remain exploratory and overfit-prone.

### Review database

SQLite tables have no schema-migration framework or astronomy-contract foreign key. Case IDs are
local row identifiers, not stable event identities across regenerated datasets. Completed ignored
reviews are now protected from replay rewriting, but a new versioned database should be built for
corrected events rather than mutating the historical database in place.

### Error and fallback telemetry

Some legacy/runtime functions catch broad exceptions and return `None`, empty houses, or NaN
series. Swiss-to-Moshier fallback is not recorded per row. Production-quality evidence needs
explicit `ephemeris_backend`, `fallback_reason`, and failure counters.

### Git and backups

The repository contains repeated historical SQLite/WAL backups. They are useful for recovery but
inflate Git and can capture an inconsistent WAL state. Future session backups should be compact:
handoff, report, status/log, and changed source only. Database backups should use SQLite's backup
API and remain outside Git unless a deliberate small fixture is required.

### Dependencies and CI

There was no dependency manifest or default pytest configuration. `requirements.txt`,
`requirements-dev.txt`, and `pytest.ini` now define the active environment and exclude backup,
virtual-environment, and unrelated-tree test collection. CI is still absent.

## Component Disposition

| Area | Files | Disposition |
|---|---|---|
| Astronomy contract | `financial_astro_ephemeris.py`, `astro_event_contract.py`, `doctrine_config.py` | Canonical foundation; tests added. |
| Event source | `rebuild_dataset_mt5_ipo_allpairs.py` | Corrected by runtime patch, but still depends on external JDML; replace next. |
| Touch/candidate pipeline | `build_aspect_sr_touch_log.py`, `build_trade_candidates_from_touches.py`, `build_case_id_feature_inventory.py`, `build_manual_case_review_sheet.py` | Canonical after a full corrected rebuild; current output files are legacy. |
| Alternate evidence builders | `build_pair_aspect_market_log.py`, `build_sr_anchor_reversal_log.py`, `analyze_sr_pair_aspect_market_log.py`, `generate_sr_candidate_chart_pack.py` | Research-only; exact ephemeris now shared, but duplicated window helpers should be consolidated. |
| Older evidence experiments | `build_event_pair_ledger.py`, `financial_astro_conditioned_evidence.py` | Historical/experimental; defaults still point at legacy data. Do not use as current truth. |
| Review UI/store | `aspect_annotation_store.py`, `build_repeatation_review_pack.py`, `serve_repeatation_pack.py`, `sr_touch_lazy_dashboard.py` | Active manual-review surface; needs single Python decision service and corrected data. |
| Older dashboard | `sr_lazy_reactive_dashboard.py` | Superseded research UI; retain temporarily, then archive after parity checklist. |
| Rule/review agents | `reviewer_rule_replay.py`, `codex_review_task_queue.py`, `jyotish_agent/dream_review_agent.py` | Retrospective only; never call directly from live execution. |
| Local Jyotish RAG | `jyotish_agent/build_corpus_index.py`, `explain_case.py`, `ingest_classical_sources.py`, `prepare_corpus_skeleton.py` | Retrieval/explanation only; provenance quarantine added. Not fine-tuning. |
| Telegram relay | `telegram_codex_relay.py`, `telegram_notify.py`, `read_codex_relay_inbox.py`, `monitor_touchlog_rebuild_telegram.py` | Operational convenience; external helper dependency remains. No credentials found in tracked text. |
| Doctrine | `shadbala_doctrine.py`, `strict_shadbala_doctrine.py`, `panchanga_doctrine.py`, `padmanabhan_timing_doctrine.py`, `enrich_touch_log_padmanabhan_timing.py` | Mixed: deterministic formulas plus explicitly provisional doctrine. Preserve labels and citations. |
| Certification | `astro_function_certification.py`, `trusted_external_sources.md` | Framework is useful; prior report is a historical snapshot, not current certification. |
| Upcoming/live | `generate_upcoming_aspects.py`, `mt5_trade_executor.py` | TT scope guard added; executor remains manual/dry-run guarded. No autonomous wiring approved. |
| Walk-forward | `evaluate_transitsign_walk_forward.py` | Leakage fixes applied; still exploratory until corrected data and preregistered feature set. |
| BTC weekly | `build_btc_weekly_astro_chart.py`, `analyze_btc_aspect_effectiveness.py` | Descriptive research only; add rolling classification and no-lookahead SR selection. |
| KAS adapter | `krushna_kas_advisory.py` | Non-binding suggestion only. Isolation lock is correct. |
| Ashtakavarga lab | all `research_labs/ashtakavarga_validation/ashtakavarga_lab/*.py` | Isolated and tested; corrected KAS remains uncertified and cannot feed trades/ML. |
| Operations | `run_touchlog_rebuild_checkpoints.py` | Useful for resumable builds; add contract/version checks to checkpoint names. |
| Removed stub | `sr_touch_lazy_dashboard_restored.py` | Deleted; it was a six-line failed decompilation placeholder. |
| Tests | all root `test_*.py` and lab `tests/*.py` | 53 tests after this audit; expand around Auto Suggest parity and full corrected rebuild. |

## Duplicate And Unused Surface

- `build_pair_aspect_market_log.py` and `build_sr_anchor_reversal_log.py` duplicate window,
  timestamp, and market-reaction helpers.
- `build_aspect_sr_touch_log.py` and dashboard code contain parallel AVG parsing, circular means,
  and body-normalization logic; new work should use `astro_event_contract.py`.
- `sr_lazy_reactive_dashboard.py` overlaps the active touch dashboard and has two callback
  parameters detected as unused.
- generated review-pack READMEs are artifacts, not project documentation.
- historical audit documents are valuable provenance, but several read like current status and
  need a superseded banner.

## Documentation Disposition

Current control documents:

- `README.md`
- `CURRENT_PROJECT_HANDOFF.md`
- this report
- `trusted_external_sources.md`
- July 2026 source/corpus reviews
- isolated Ashtakavarga lab README/spec/findings

Historical snapshots, retained with a superseded notice:

- `vedic_pdf_alignment_review_20260520.md`
- `astro_function_research_audit_20260521.md`
- `astro_function_research_audit_20260527.md`
- `astro_function_certification_report_20260527.md`
- `astro_feature_inventory_from_pdfs.md`

`financial_astrology_source_notes_2026-03-13.md`, Padmanabhan notes/validation, and the individual
book reviews remain source-specific evidence; they do not certify trading efficacy.

## Required Rebuild And Promotion Sequence

1. Freeze the old source/touch/case database as `legacy_double_sidereal_research_history`.
2. Replace or vendor the external JDML source generator.
3. Rebuild the full TN source with explicit roles and the canonical astronomy contract.
4. Rebuild touch logs and candidate rows; reject unresolved roles or out-of-orb geometry.
5. Create a new annotation database namespace keyed by immutable event identity plus contract.
6. Re-review or explicitly migrate observations; never copy old P/L labels as astronomical truth.
7. Make Python the single Auto Suggest engine and prove browser/replay parity with fixtures.
8. Split retrospective review from timestamp-safe live inference.
9. Run purged walk-forward evaluation with a frozen feature allowlist and untouched final holdout.
10. Only then connect a demo executor; keep live trading behind a separate approval gate.

## Verification Performed

- corrected Raman true-node and sidereal-house regression tests;
- event-role and geometry contract tests;
- strict Shadbala doctrine regression tests;
- review replay ignored-case protection;
- purged training embargo and feature exclusion tests;
- RAG legacy-provenance quarantine tests;
- isolated KAS tests and isolation checks;
- canonical Python compilation;
- Ruff, Vulture, and Radon static inspection;
- secret-pattern scan of tracked text: no supplied MT5 password or investor password found.

The highest-value next engineering task is the **full corrected versioned rebuild**, not another
rule, UI tweak, or agent. More automation on top of the old event identities would only make the
wrong evidence move faster.
