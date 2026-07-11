# Astro Function Research Audit Addendum - 2026-05-27

> **Historical snapshot:** This addendum is preserved as research provenance. It is superseded
> for current implementation/certification status by `end_to_end_financial_astro_audit_20260711.md`.

Private USDJPY Gann / Vedic financial astrology workspace.

This addendum records the next audit direction after the repeatation reviewer became rule-heavy enough that silent assumptions are now the main risk.

## Immediate UI / Rule Finding

Case `127` showed why the marker generator needs candidate transparency:

- The exported hardcoded selected-case marker came from a later confluence dot at `2025-05-28 23:30`.
- The visually earlier `2025-05-28 22:00` candle touched the active SR line by wick, but was missed because upstream touch logging prioritizes confluence markers over plain SR-line wick touches.
- The reviewer now scans the selected case window for tight SR-line wick touches and prefers the first such touch as Auto Suggest start. For case `127`, that produces:
  - start: `2025-05-28 22:00:00+05:30 @ 144.965`
  - end: `2025-05-28 23:30:00+05:30 @ 145.125`
  - Gann fan anchor: top wick at the start candle

Recommended next UI audit feature:

- Add a candidate inspector showing every start/end candidate considered: exported confluence dot, selected-case SR-line wick touch, nearest hardcoded marker, next shaded-zone boundary, and first SR target.
- Each candidate should show why it won or lost, in pips and plain English.

## Source Cross-Check Notes

Sources checked in this pass:

- Swiss Ephemeris 2.10 documentation, Astrodienst:
  `https://www.astro.com/ftp/swisseph/doc/swisseph.pdf`
- Shadbala component cross-check pages:
  `https://astrosight.ai/planets/shadbala-calculation-vedic-astrology`
  `https://www.shreekundli.com/vedic-astrology/shadbala`
  `https://www.shreekundli.com/vedic-astrology/shadbala/kala-bala`
- Existing local audit:
  `astro_function_research_audit_20260521.md`

Raman ayanamsa:

- Swiss Ephemeris documents "Raman Ayanamsha" as a named ayanamsha used by B. V. Raman, and notes a correction row for Raman in its ayanamsha section.
- Current project config already uses `Raman`, `SIDM_RAMAN`, true node, geocentric Swiss Ephemeris. This is coherent, but should remain explicitly tagged in every generated dataset.

Shadbala:

- Web cross-checks agree on the six major components: Sthana, Dig, Kala, Chesta, Naisargika, and Drik Bala.
- Sthana Bala should include Uchcha, Saptavargaja, Ojayugma, Kendradi, and Drekkana.
- Kala Bala should include Natonnata, Paksha, Tribhaga, Abda/Masa/Vara/Hora, Ayana, and Yuddha-related logic depending on tradition.
- Our current strict implementation is useful but still tagged correctly as needing external calculator validation.

## Non-Negotiable Audit Gates Before Live Walk-Forward Use

1. External calculator validation:
   Compare `strict_shadbala_doctrine.py`, `panchanga_doctrine.py`, and Raman longitude outputs against at least one trusted Jyotish calculator and one Swiss Ephemeris reference output for a fixed sample set.

2. Deterministic rule replay:
   For cases `8`, `43`, `103`, and `127`, run a script-level replay that records:
   selected start, selected end, all rejected candidates, SR geometry, break status, Gann anchor, and rule-vs-default P/L.

3. Candidate transparency:
   Reviewer UI should expose why Auto Suggest chose one marker. This avoids guessing whether the script is hallucinating.

4. LLM containment:
   Local LLM output must never be training truth by itself. Only deterministic evidence, manual notes, verified rule lessons, and dream-review corrections should become training labels.

5. Doctrine status flags:
   Every generated row should continue carrying status fields such as:
   `ayanamsa`, `node_type`, `shadbala_model_version`, `drik_model_version`, `panchanga_model_version`, `proxy_or_validated`.

## Overnight Work Queue

- Build a deterministic `reviewer_rule_replay.py` audit for AVG(ALL)|MOON square repeatations.
- Add reviewer candidate inspector to the marker drawer. Done in `repeatation_ui_20260527_candidate_inspector_v47`; keep expanding it as new rule candidates are added.
- Add regression assertions for the four active teaching cases:
  - case `8`: confirmed break should close at next attribution boundary / zone rule, not premature SR touch.
  - case `43`: bearish family support-barrier rule with SR geometry and break confirmation.
  - case `103`: clean recurrence can close at first SR touch when no earlier attribution boundary exists.
  - case `127`: first selected-window SR wick touch wins over later confluence marker; Gann fan anchors at top wick.
- Start a source-backed Jyotish function audit table:
  implemented, proxy, missing, disputed, validation source, and test status.

## Candidate Inspector Implementation - 2026-05-27

Implemented in `build_repeatation_review_pack.py`:

- The marker drawer Auto Suggest section now includes a `Candidate check` table.
- For normal marker-flow suggestions, it records:
  - chosen start candidate;
  - rejected later SR wick touches;
  - exported hardcoded confluence marker as a reference when it is not the best entry;
  - chosen end marker.
- For family-rule suggestions, it records:
  - family-rule entry/open candidate;
  - old default start/end references;
  - first SR target;
  - next shaded-zone boundary;
  - next hardcoded marker / attribution boundary.
- Candidate rows include time, price, SR price, SR gap in pips, touch band, wick side, and plain-English reason.

Case `127` verification after Clear markers + Auto Suggest:

- chosen start: `2025-05-28 22:00:00+05:30 @ 144.965`;
- reason: earliest wick touch inside the selected case window and tight SR band;
- SR context: `SR 144.987`, gap about `2.2` pips, band `3.0` pips, top wick;
- later SR wick touches at `23:00` and `23:30` are now explicitly rejected because the earlier valid touch already won;
- exported hardcoded confluence dot at `23:30` is kept as a reference/end boundary;
- chosen end: `2025-05-28 23:30:00+05:30 @ 145.125`;
- result: bullish about `+16.0` pips;
- Gann fan anchor: top wick at `2025-05-28 22:00`.

This directly addresses the user's concern that the script should explain why it did not choose the visually obvious earlier SR touch.

## What Was Reviewed In This Pass

Targeted code review / audit covered:

- `build_repeatation_review_pack.py`: Auto Suggest, SR wick-touch candidate generation, family-rule candidate flow, marker drawer rendering, Gann anchor selection, rule lesson display, dream verifier hooks, and cache versioning.
- `strict_shadbala_doctrine.py`: current implemented Shadbala component coverage and status flags.
- `panchanga_doctrine.py`: five-limb Panchanga feature generation and validation status.
- `doctrine_config.yaml` and `doctrine_config.py`: Raman ayanamsa configuration, node policy, status metadata, and missing/doctrine-decision flags.
- `build_aspect_sr_touch_log.py`: feature/status propagation touch points checked by search.
- `jyotish_agent/explain_case.py`: deterministic-first explanation and local LLM containment posture checked by search.
- Local audit files including `astro_function_research_audit_20260521.md`.

Not fully reviewed yet:

- Every generated HTML/CSV export folder.
- Every old backup/report.
- Full end-to-end ML training/evaluation scripts, if any are later promoted from the review ledger.
- External calculator equivalence against a canonical Jyotish calculator.

## Remaining Shortcomings / Risk Register

1. External validation still missing:
   `strict_shadbala_doctrine.py` and `panchanga_doctrine.py` are implemented enough for research review, but not yet externally validated against fixed examples from a trusted Jyotish calculator.

2. Rule replay tests missing:
   The reviewer now logs candidate decisions visually, but we still need a deterministic replay test file for teaching cases `8`, `43`, `103`, and `127`.

3. Upstream touch-log export still needs improvement:
   Case `127` is fixed reviewer-side. The source touch-log generator should eventually export plain SR-line wick-touch candidates directly, not only confluence/hardcoded markers.

4. Rule lifecycle needs formal statuses:
   Local/family/global rules should move through `provisional`, `accepted`, `revised`, or `discarded` based on replay results before training truth is frozen.

5. Rahu/Ketu strength policy must stay explicit:
   Nodes are proxy context only and are excluded from classical Shadbala totals. Do not let an LLM infer Rahu/Ketu Shadbala unless a separate node-strength doctrine is deliberately defined.

6. Local LLM drafts remain non-authoritative:
   The dream verifier can flag/correct contradictions, but only deterministic evidence, manual labels, rule lessons, and verified corrections should enter the ML ledger.

7. Formula citation table still needed:
   Each astro feature should have a source id, implementation status, proxy/strict flag, and test status.

8. `BPHS-like orb strength` wording needs continued caution:
   For composite pairs such as `AVG(ALL)|MOON`, a zero value may be a proxy artifact rather than a pure doctrinal claim. Keep this label as a feature to test, not a final Jyotish judgment.

## Astro Function Certification Plan

The current astro layer should be treated as `research-validating`, not certified. To certify it for walk-forward trading, use a four-stage gate:

1. Formula inventory:
   Create a table for every feature column:
   feature name, source doctrine, exact formula, code function, strict/proxy status, known assumptions, and validation status.
   This must include Raman ayanamsa, sidereal longitudes, true node policy, whole-sign houses, Shadbala components, Drik Bala, Panchanga limbs, and any AVG(ALL) composite rule.

2. Astronomical position certification:
   For a fixed sample set of timestamps and locations, compare our Swiss Ephemeris outputs against an independent Swiss Ephemeris tool/reference.
   Required checks:
   - tropical longitude;
   - Raman ayanamsa value;
   - sidereal longitude after subtracting ayanamsa;
   - true Rahu/Ketu node longitude;
   - timezone conversion to IST and Tokyo reference charts.

3. Jyotish doctrine calculator certification:
   For the same fixed sample set, compare Shadbala and Panchanga outputs against at least one trusted Jyotish calculator/export.
   Pass/fail tolerance should be explicit:
   - exact categorical match for tithi, paksha, nakshatra, pada, yoga, karana, weekday;
   - numeric tolerance for Virupa values, e.g. <= 0.5V for simple components and a separately documented tolerance for complex or tradition-dependent components.

4. Trading-feature certification:
   Once astro math is validated, certify its use inside market rules:
   - same feature value appears in touch-log CSV, reviewer drawer, ML notes, and local RAG evidence;
   - each feature carries `strict`, `proxy`, `missing`, or `externally_validated`;
   - rule replay confirms that cases `8`, `43`, `103`, and `127` still make the expected marker/exit decisions after any astro-function change.

Certification status labels to use:

- `implemented_unvalidated`: formula exists but has not been checked against external examples.
- `proxy_research_feature`: useful for ML experiments, but not a classical doctrine value.
- `externally_validated`: passed fixed sample checks against an independent source.
- `disputed_tradition`: valid only under a named doctrine choice.
- `do_not_train`: visible for review but excluded from ML labels until resolved.

Recommended first certification sample set:

- `2025-03-07 19:30 IST` case `8`;
- `2025-04-04 02:30 IST` case `43`;
- `2025-05-15 22:30 IST` case `103`;
- `2025-05-28 22:00 IST` case `127`;
- one known natal/epoch reference: `1889-02-11 00:00 Asia/Tokyo`.

Source anchors used for this plan:

- Swiss Ephemeris documentation: sidereal positions are derived by subtracting ayanamsa, and Raman is a documented ayanamsa mode.
- Shadbala references agree on six major strengths: Sthana, Dig, Kala, Chesta, Naisargika, and Drik.
- Panchanga references agree on the five limbs: Tithi, Vara, Nakshatra, Yoga, and Karana.

## Deterministic Replay Added - 2026-05-27

Added `reviewer_rule_replay.py`:

- Parses generated Plotly chart HTML directly.
- Decodes typed Plotly arrays.
- Replays case `127` selected-window SR wick-touch detection without needing the browser.
- Asserts:
  - start rule is `first_case_window_sr_line_touch`;
  - start is `2025-05-28T22:00:00+05:30`;
  - end is `2025-05-28T23:30:00+05:30`;
  - Gann anchor side is `top`;
  - at least three selected-window SR touches are found.
- Adds source guards for teaching cases `8`, `43`, and `103` until the family-rule browser logic is factored into reusable Python.

Current limitation:

- The full family-rule Auto Suggest branch still lives in browser-side JavaScript. `reviewer_rule_replay.py` checks its source guards today, but the next improvement should be to factor the Auto Suggest decision engine into shared JSON/Python logic so cases `8`, `43`, and `103` can be replayed at the same depth as case `127`.

## 4-Gate Certification Runner Added - 2026-05-27

Added `astro_function_certification.py` and generated the first certification snapshot:

- `astro_function_certification_report_20260527.md`
- `astro_function_certification_inventory_20260527.csv`
- `astro_position_baseline_20260527.csv`
- `panchanga_baseline_20260527.csv`
- `astro_external_validation_template_20260527.csv`
- `trading_rule_replay_result_20260527.json`

Gate results:

- Gate 1 formula inventory:
  9 feature families are now explicitly inventoried with source anchor, implementation file/function, strict/proxy label, validation status, current gap, next action, and ML training policy.
- Gate 2 astronomical baseline:
  Raman ayanamsa Swiss Ephemeris baselines were generated for cases `8`, `43`, `103`, `127`, and the Tokyo Gann reference sample.
  These are local reproducibility baselines, not external validation.
- Gate 2 Panchanga baseline:
  Tithi, Paksha, Moon Nakshatra/Pada, Yoga, Karana, weekday, and weekday lord were generated for the same sample set.
  These remain pending traditional Panchanga cross-check.
- Gate 3 external validation:
  A blank expected-value template was generated for ephemeris, Panchanga, Shadbala, and Drik values.
  The expected-value columns must be filled from trusted external sources before any doctrine field can be promoted to `externally_validated`.
- Gate 4 trading replay:
  `reviewer_rule_replay.py` passed.
  Case `127` has data-level replay; cases `8`, `43`, and `103` remain source-guarded until the browser Auto Suggest branch is factored into reusable Python.

Important verdict:

- The 4-gate process is active but not complete.
- Shadbala, Drik Bala, and Panchanga should remain `implemented_unvalidated` / `formula_foundation_pending_traditional_validation`.
- Raw local LLM prose remains `do_not_train_raw_text`; only deterministic evidence, manual notes, verified corrections, and rule lessons should enter ML truth.

## Trusted Source Intake Workflow Added - 2026-05-27

Added `trusted_external_sources.md` to define external certification sources and their use:

- Tier A:
  Swiss Ephemeris documentation and Raman ephemeris samples for astronomy / position checks.
- Tier B:
  Jagannatha Hora as the preferred Shadbala/Jyotish calculator cross-check, with PyJHora as a secondary automated checker.
- Tier C:
  Drik Panchang and secondary Panchanga calculators for Tithi, Vara, Nakshatra, Yoga, and Karana checks.

Updated `astro_function_certification.py` so Gate 3 is now an intake loop:

- If `astro_external_validation_template_20260527.csv` already exists, rerunning the script preserves any filled `external_expected_value` and `external_source` entries.
- The script compares external values automatically:
  - longitude tolerance: `<= 0.02 deg`;
  - Shadbala/Drik/Virupa tolerance: `<= 0.5 virupa`;
  - categorical Panchanga values: exact case-insensitive match.
- Gate 3 report now summarizes pass/fail/pending counts.

Current Gate 3 state after rerun:

- `0 pass`
- `0 fail`
- `35 pending`

This is expected because no external expected values have been entered yet.
