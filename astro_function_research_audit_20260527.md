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
- Add reviewer candidate inspector to the marker drawer.
- Add regression assertions for the four active teaching cases:
  - case `8`: confirmed break should close at next attribution boundary / zone rule, not premature SR touch.
  - case `43`: bearish family support-barrier rule with SR geometry and break confirmation.
  - case `103`: clean recurrence can close at first SR touch when no earlier attribution boundary exists.
  - case `127`: first selected-window SR wick touch wins over later confluence marker; Gann fan anchors at top wick.
- Start a source-backed Jyotish function audit table:
  implemented, proxy, missing, disputed, validation source, and test status.
