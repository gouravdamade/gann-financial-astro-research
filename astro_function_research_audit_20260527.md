# Astro Function Research Audit Addendum - 2026-05-27

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
