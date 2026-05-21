# Astro Function Research Audit - 2026-05-21

Private USDJPY Gann / Vedic financial astrology workspace.

This audit reviews the current Python astro/research functions against the local PDFs and a web cross-check. It is not a trading recommendation. The purpose is to decide what doctrine and feature work should be completed before heavier ML training on manually reviewed `case_id` repeatations.

## Sources Checked

Local project sources:

- `pdf_alignment_extracts\Building a Strict Vedic Astrology Prediction Engine with a Local LLM Layer.txt`
- `pdf_alignment_extracts\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.txt`
- `astro_feature_inventory_from_pdfs.md`
- `vedic_pdf_alignment_review_20260520.md`
- Current Python files in `C:\Users\ADMIN\PycharmProjects`

Web sources:

- Swiss Ephemeris Programmer's Manual, Astrodienst: `https://www.astro.com/swisseph-download/doc/swephprg.pdf`
- Swiss Ephemeris Programmer's Manual 2.10, Astrodienst: `https://www.astro.com/swisseph/swephprg.2.10.pdf`
- PySwisseph package page: `https://pypi.org/project/pyswisseph/`
- Shadbala overview cross-check: `https://www.shreekundli.com/vedic-astrology/shadbala`
- Panchanga reference: `https://planetarypositions.com/panchanga`
- Tithi definition cross-check: `https://en.wikipedia.org/wiki/Tithi`
- Gann/financial astrology software feature reference: `https://astroapp.com/help/1/gannW.html`

## Current Astro Function Surface

### Already Strong / Useful

`build_aspect_sr_touch_log.py`

- Computes sidereal planetary longitudes and event windows.
- Supports graha-style aspects and rashi aspects.
- Computes event aspect metrics, event duration, orb proxy strength, BPHS-like virupa proxy, and active regime windows.
- Builds USD/JPY reference context using JPY Tokyo reference and USD Philadelphia reference.
- Adds natal sign/house context, Kendra/Trikona/Dusthana flags, transit-natal hit JSON, and base/quote scoring fields.
- Adds true-node Rahu handling in the local event builder path.

`sr_touch_lazy_dashboard.py`

- Builds M30/H1/Daily/switchable chart views.
- Adds SR planetary lines, aspect windows, active regime zones, hovers, quote/base detail panel, and chart exports.
- Keeps the current scoring explicitly marked as heuristic/proxy.

`build_trade_candidates_from_touches.py`

- Builds ML-ready candidate rows, forward returns, exit evaluation, SR confirmation, and rule-layer scoring.
- Separates base/quote score logic for USDJPY.

`build_repeatation_review_pack.py`

- Provides the manual repeatation review UI, marker annotations, ignore-trade signals, rule notes, auto-suggest markers, live P/L, and ML trait hints.
- This is the right human-labeling layer for the next phase.

`shadbala_doctrine.py` and `doctrine_config.yaml`

- Good foundation: doctrine metadata, minimum total Shadbala virupa thresholds, and basic Sthana sign dignity.
- Explicitly marks current Shadbala/Drik fields as incomplete proxy features.

### Implemented But Still Proxy

`event_bphs_like_orb_strength`, `event_bphs_like_orb_virupa`, `tn_primary_bphs_strength`, and similar fields are useful but should not be called strict Drik Bala yet.

Current strength is mainly a smooth orb/exactness proxy. Strict Drik Bala requires benefic/malefic signed aspect energy and then, per the Shadbala PDF, Drik Bala should modify/fine-tune Sthana and Kala values.

`shadbala_tag` and `shadbala_avg` exist, but the source/status columns correctly say they are pending full six-bala calculation.

## Key Doctrine Gaps

### 1. Ayanamsa / Node / House Policy Must Be Locked

Update on 2026-05-21: the user chose Raman ayanamsa as the project doctrine preference. The doctrine config is now locked to `ayanamsa: Raman`, `ayanamsa_swiss_ephemeris_id: SIDM_RAMAN`, and `node_type: true_node`.

Swiss Ephemeris documentation says sidereal mode should be set explicitly with `swe_set_sid_mode()` unless the default Fagan/Bradley ayanamsha is desired. The project now applies `swe.set_sid_mode(swe.SIDM_RAMAN)` through `configure_swiss_ephemeris_sidereal()`.

Recommended additions:

- `ayanamsa: Raman`, not `swiss_ephemeris_default`.
- `node_type: true_node`, explicitly.
- `house_system: whole_sign` or the exact existing `jyotish_engine` house system.
- `coordinate_system: geocentric` with any heliocentric/Gann features clearly experimental.

Why it matters: tiny doctrine differences can move signs, nakshatra, house, drishti, and therefore ML features. This must be stable before serious training.

### 2. Full Shadbala Is Missing

The local Shadbala PDF lists the six strengths:

- Naisargika Bala
- Sthana Bala
- Kala Bala
- Dig Bala
- Drik Bala
- Chesta Bala

It also discusses 18 sub-balas, minimum thresholds, ratios/ranks, and using Drik Bala to correct Sthana/Kala values.

Current code only implements:

- minimum total thresholds for seven classical planets,
- basic sign dignity / friendship Sthana context,
- metadata saying full Shadbala is pending.

Recommended module expansion:

- `naisargika_bala`: fixed natural values/ranks.
- `sthana_bala`: Uccha, Saptavargaja, Oja/Yugma, Kendradi, Drekkana components.
- `dig_bala`: directional strength from house/angle.
- `kala_bala`: temporal strength, including Paksha, Vara, Hora, Ayana, etc. as applicable.
- `chesta_bala`: speed/retrograde/motional strength.
- `drik_bala`: signed benefic/malefic aspectual strength.
- `shadbala_total`, `shadbala_ratio_to_minimum`, `shadbala_rank`, `ishta_phala`, `kashta_phala`.

### 3. Strict Drik Bala Is Missing

Current BPHS-like aspect strength is useful for ranking aspect closeness, but the Shadbala PDF and external cross-check both distinguish Drik Bala as aspectual strength from benefic and malefic influences.

Recommended additions:

- Exact aspect energy by graha pair.
- Benefic/malefic sign of the aspect energy.
- Support for natural benefic/malefic and functional benefic/malefic.
- Net Drik Bala per planet.
- `effective_sthana_bala = sthana_bala + drik_bala_adjustment`.
- `effective_kala_bala = kala_bala + drik_bala_adjustment` where doctrine supports it.

### 4. Panchanga Layer Is Mostly Missing

Current logs have `moon_nakshatra`, but not a complete Panchanga.

Web and traditional references consistently identify the five daily limbs as:

- Vara / weekday
- Tithi
- Nakshatra
- Yoga
- Karana

Tithi is defined by Sun-Moon longitudinal separation in 12 degree steps. This is straightforward to calculate from existing solar/lunar longitudes.

Recommended additions:

- `vara_lord`
- `tithi_index`, `tithi_name`, `paksha`
- `moon_nakshatra`, `moon_nakshatra_pada`
- `sun_nakshatra`, `sun_nakshatra_pada`
- all-classical-planet nakshatra/pada where useful
- `nitya_yoga`
- `karana`
- `lunar_phase_angle`
- event-window change flags: `tithi_changed_during_event`, `nakshatra_changed_during_event`, etc.

For financial astrology, Panchanga is likely useful as a regime/context feature rather than a deterministic buy/sell rule.

### 5. Vargas / Divisional Dignity Are Missing

The Shadbala PDF references Saptavarga Bala. Current code does not compute divisional dignity.

Recommended additions:

- Start with `D9/Navamsa` sign and dignity.
- Add Saptavargaja Bala if implementing full Sthana Bala.
- Keep D-chart features as doctrine context first, not direct trade signals.

### 6. Dasha / Period Lords Are Missing

No Vimshottari or other dasha timing is present. For financial markets this is not automatically obvious, because the question is whose chart is running dasha: JPY reference, USD reference, exchange first-trade chart, or event chart.

Recommended handling:

- Do not add dasha until the reference-chart doctrine is locked.
- If added, tag as reference-specific: `jpy_vimshottari_lord`, `usd_vimshottari_lord`, etc.
- Treat as context/hypothesis until walk-forward validation.

### 7. Planet State Features Are Thin

Current code has retrograde flags for primary transit hits. Missing:

- combustion
- planetary war / graha yuddha
- speed percentile
- station proximity
- declination / latitude context
- eclipse proximity
- New/Full Moon proximity

For USDJPY, speed/station/proximity may be more useful than a broad retrograde boolean because market reaction often clusters around changes in motion.

### 8. Functional Benefic / Malefic Is Missing

Current scoring has natural planet bias and house bias, but not proper functional benefic/malefic by ascendant/house lordship.

Recommended additions:

- Compute functional benefic/malefic for the selected reference ascendant.
- Keep natural and functional labels separate.
- Add rule metadata because this is a place where traditions vary.

### 9. Gann / Financial Astrology Additions Need Doctrine Separation

Current SR lines are useful and already treated as experimental. Web references for Gann-style tools emphasize choices such as planet, scale, harmonic, coordinate system, and clockwise/counter-clockwise conversion. These should be explicit config fields, not hidden assumptions.

Recommended additions:

- `gann_scale_id`
- `price_longitude_scale`
- `harmonic`
- `coordinate_system`
- `planetary_line_variant`
- `longitude_to_price_formula`
- `line_origin_policy`

Possible future features:

- planetary midpoint SR clusters,
- heliocentric/geocentric agreement flags,
- harmonic clusters,
- angular time cycles,
- T-square / grand-cross stress-pattern detection,
- weekly slow-planet context.

## Duplicate / Refactor Risk

`build_trade_candidates_from_touches.py` still has its own dignity tables and `dignity_for_planet_in_sign()`. `shadbala_doctrine.py` now has the source-cited version.

Recommended next code cleanup:

- Import dignity functions from `shadbala_doctrine.py`.
- Remove duplicate dignity constants from candidate scoring.
- Add unit/smoke checks so future doctrine changes hit touch logs, candidate scores, and case inventory consistently.

## ML Readiness Assessment

The manual repeatation UI is ready enough to continue human review, but the strict doctrine feature layer is not complete enough for final ML training.

Best approach:

1. Keep reviewing cases manually with current markers, ignore signals, rule notes, and trait hints.
2. Before final model training, implement the high-priority doctrine features below.
3. Rebuild touch log and candidates after doctrine changes.
4. Use purged/embargoed walk-forward validation, not random train/test split.
5. Separate labels:
   - manual trade result,
   - ignored/contaminated event,
   - rule note,
   - universal rule,
   - local case-specific rule.

## Priority Roadmap

### Must Do Before Serious ML Training

1. Lock ayanamsa/node/house policy in `doctrine_config.yaml`.
2. Unify dignity logic through `shadbala_doctrine.py`.
3. Rebuild candidates with the latest doctrine metadata columns.
4. Add Panchanga core: tithi, paksha, vara, nakshatra/pada, yoga, karana.
5. Add purged/embargoed walk-forward validation for all candidate models.

### Strong Next Additions

6. Full Shadbala Phase 1:
   - Naisargika Bala,
   - Dig Bala,
   - Chesta/speed features,
   - Shadbala ratio/rank.
7. Strict Drik Bala Phase 1:
   - signed benefic/malefic aspect energy,
   - net Drik Bala per planet.
8. Planet-state features:
   - combustion,
   - station proximity,
   - speed percentile,
   - New/Full Moon proximity.

### Later / Experimental

9. Saptavargaja / Navamsa dignity.
10. Functional benefic/malefic by reference ascendant.
11. Dasha layers for JPY/USD reference charts.
12. Gann scale/harmonic/coordinate variants.
13. T-square / grand-cross and slow-planet weekly regime context.

## Practical Recommendation

Do not pause manual case review waiting for the entire strict doctrine engine. The manual notes are valuable now, especially ignore/contamination notes and rule exceptions.

But before training a model that will be used for walk-forward inference, do a smaller hardening sprint:

- lock doctrine config,
- unify dignity,
- add Panchanga,
- rebuild candidates,
- run purged walk-forward.

That gives the ML something more stable and less hallucination-prone to learn from.

## Doctrine Decision

The main doctrine choice is now resolved:

- Use Raman ayanamsa.
- Use true Rahu/Ketu.
- Treat alternative ayanamsa/node policies as separate feature variants, not mixed with the Raman dataset.

Next implication: regenerate the event dataset, touch log, candidates, annotation context, and repeatation review pack so all future ML/review artifacts carry `doctrine_ayanamsa=Raman`.
