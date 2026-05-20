# Vedic PDF Alignment Review - 2026-05-20

## Sources Checked

- `C:\Users\ADMIN\Desktop\doc\Building a Strict Vedic Astrology Prediction Engine with a Local LLM Layer.pdf`
- `C:\Users\ADMIN\Desktop\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf`

Extracted text copies for this review:

- `C:\Users\ADMIN\PycharmProjects\pdf_alignment_extracts\Building a Strict Vedic Astrology Prediction Engine with a Local LLM Layer.txt`
- `C:\Users\ADMIN\PycharmProjects\pdf_alignment_extracts\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.txt`

## Short Verdict

The current project is aligned with the first PDF's architecture, but not yet a complete strict Vedic doctrine engine.

It already follows the broad separation:

1. deterministic astronomy/Jyotish calculations,
2. explicit rule/scoring layer,
3. manual/ML calibration layer,
4. future LLM explanation layer only.

However, the current Shadbala implementation is mostly a proxy/feature layer. The full Jaya Sekhar Shadbala doctrine, with all six balas, component thresholds, Drik Bala correction, Ishta/Kashta, and source-cited rule metadata, is still missing.

## What Is Based On The PDFs

### Architecture

The first PDF recommends a deterministic Jyotish core, a doctrine-locked rule layer, optional ML calibration, and a local LLM used only for explanations/citations. Current implementation mostly follows that shape:

- `build_aspect_sr_touch_log.py` computes deterministic event/touch features.
- `build_trade_candidates_from_touches.py` creates explicit rule-layer scores and ML-ready outcomes.
- `build_repeatation_review_pack.py` provides manual review annotations, ignore reasons, rule notes, profit labels, and ML hint traits.
- No current code uses an LLM to compute ephemeris, aspects, markers, or trades.

### Sidereal / Jyotish Core Direction

The first PDF says the doctrine config should lock sidereal zodiac, ayanamsa, graha set, drishti method, and Shadbala method.

Current partial alignment:

- `build_aspect_sr_touch_log.py` uses sidereal calculations and ayanamsa correction in the event builder.
- `sr_touch_lazy_dashboard.py` calls the adaptive longitude builder with `astrology_method="sidereal"`.
- Transit-to-natal hit fields include BPHS-like strength, virupa, natal signs/houses, and retrograde flags.

### Drishti / BPHS-Like Strength

Current implementation has BPHS-like drishti fields:

- event-level `event_bphs_strength` and `event_bphs_virupa`;
- transit-natal `tn_primary_bphs_strength`, `tn_primary_bphs_virupa`, and `tn_bphs_total`;
- graha drishti style names such as `drishti_3`, `drishti_4`, `drishti_5`, `drishti_8`, `drishti_9`, `drishti_10`.

Important caveat: the event strength is currently a smooth orb-strength proxy, not a fully sourced BPHS Drik Bala computation.

### Sign Dignity / Friend / Enemy Layer

`build_trade_candidates_from_touches.py` has a doctrine-v1 dignity model:

- own signs,
- exaltation signs,
- debilitation signs,
- friend / neutral / enemy sign lord relationships,
- virupa-like values for dignity.

This is directionally aligned with the Shadbala PDF's Sthana Bala discussion, especially sign dignity context. But the values currently use a simplified table and should be reconciled against the PDF's exact component treatment.

### ML Calibration Discipline

The project has not yet allowed ML to invent rules. The current repeatation reviewer is being built as a human-observation capture tool:

- manual trade start/end markers,
- ignore regions and ignore signal types,
- rule notes,
- auto-suggest markers with manual override,
- special trait hints comparing one repeatation against the rest.

This fits the PDF idea that ML should learn which combinations historically mattered, while doctrine stays explicit.

## What Is Extra / Experimental

These are useful for the research workflow but are not strict Vedic doctrine from the two PDFs:

- USDJPY base-minus-quote scoring using USD and JPY reference charts.
- Support/resistance planetary line touch logic.
- Gann-style financial astrology chart research context.
- Western-style market aspect windows and orb event zones.
- M30/H1/daily chart switching.
- Repeatation reviewer UI.
- Manual draggable trade/ignore/rule markers.
- Auto Suggest trade marker placement.
- Live P/L callout and bullish/bearish outcome calculation.
- Hardcoded chart marker highlighting and selected-case red border.
- Ignore trade signal taxonomy such as nearby event, event too short, overlapping aspect, abnormal candle, session gap.
- Special ML trait callouts such as edge score bucket, active regime count, and direction-linked traits.

These should be labelled as empirical/experimental features in metadata so future ML does not confuse them with locked Jyotish doctrine.

## What Is Missing

### Full Shadbala

The Jaya Sekhar PDF makes Shadbala much richer than the current implementation. Missing items include:

- Naisargika Bala.
- Sthana Bala full components.
- Kala Bala.
- Dig Bala.
- Drik Bala.
- Chesta Bala.
- The 18 sub-balas discussed in the book.
- Per-planet minimum Shadbala thresholds.
- Planet rank/relative-strength interpretation.
- Drik Bala as modifier/corrector to Sthana and Kala.
- Exact benefic/malefic aspect energy handling.
- Ishta and Kashta Phala.

### Better Sthana Bala Detail

Current code has a simplified sign dignity model. Missing or needing reconciliation:

- exact Sthana Bala subcomponents;
- moolatrikona handling;
- Saptavargaja Bala;
- Kendradi Bala;
- Drekkana Bala;
- PDF-sourced virupa tables and citation IDs.

### Strict Drik Bala

Current code has BPHS-like orb strength and virupa. Missing:

- exact longitudinal Drik Bala formulas;
- benefic/malefic signed aspect energy;
- full aspect strength by planet and distance;
- integration of Drik Bala into effective Sthana/Kala values.

### Doctrine Config

The PDFs emphasize doctrine locking. A first foundation was added on 2026-05-21:

- `doctrine_config.yaml`;
- `doctrine_config.py`;
- `shadbala_doctrine.py`;
- output metadata columns such as `doctrine_config_id`, `doctrine_drishti_status`, `doctrine_shadbala_method`, and `experimental_layer_flags`;
- explicit proxy aliases `event_bphs_like_orb_strength` and `event_bphs_like_orb_virupa`;
- Shadbala minimum total virupa table for the seven classical planets from the Shadbala source text.
- basic Sthana sign dignity fields for event planets where event best-time signs are available.

Still pending:

- zodiac: sidereal;
- ayanamsa;
- coordinate system;
- graha set;
- node policy;
- drishti method;
- Shadbala method;
- house system;
- ephemeris/source version;
- experimental layer flags.

### Citation-Bound Rule Layer

The first PDF recommends rule IDs and citations. Current code has notes, but not source/page IDs attached to every doctrine rule.

Needed:

- a rule registry or YAML;
- source ID per rule;
- page/chapter locator;
- explicit "doctrine" vs "experimental" classification;
- output fields showing which rule IDs fired.

### RAG / Local LLM Layer

No local LLM/RAG layer exists yet, which is good for now. When added, it must:

- retrieve from the local PDF corpus;
- cite sources;
- explain already-computed features;
- never calculate ephemeris, aspects, Shadbala, or trade labels.

### Validation

The PDF warns against overfitting. Missing:

- purged walk-forward splits;
- embargo around overlapping aspect windows;
- out-of-sample reports;
- leakage checks for manual annotation features;
- performance separated by doctrine features vs experimental features.

## Recommended Next Build Order

1. Extend the first `doctrine_config.yaml` foundation with exact ayanamsa/node/house policy.
2. Keep current BPHS/Shadbala proxy fields clearly labelled, so we do not mistake them for full Shadbala.
3. Expand `shadbala_doctrine.py` from minimum totals + basic Sthana sign dignity into full six-bala component calculation.
4. Add Drik Bala as signed benefic/malefic aspect energy, then wire it into Sthana/Kala correction.
5. Add rule IDs and citations to the rule-layer output.
6. Keep the repeatation reviewer as the manual ML-labeling layer, but tag every note/rule as `manual_observation`, `doctrine_rule`, or `experimental_rule`.
7. Only after those are stable, run purged walk-forward ML.

## Bottom Line

The current project is built in the spirit of the uploaded PDFs, especially the architecture and ML discipline. The biggest gap is that current Shadbala/BPHS strength is not yet the full doctrine described in the Shadbala PDF. We should treat the current system as a strong research UI plus partial Jyotish feature engine, then harden the doctrine layer before trusting ML conclusions.
