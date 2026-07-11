# Astro Function Certification 4-Gate Report

> **Historical snapshot:** This May 2026 report is retained for provenance. Its implementation
> status and certification labels are superseded by
> `end_to_end_financial_astro_audit_20260711.md`; the legacy USDJPY astronomy artifacts are
> quarantined pending a corrected versioned rebuild.

- Report version: `astro_certification_4_gate_v1_20260527`
- Generated: `2026-05-29T03:27:59+05:30`
- Important interpretation: this report certifies traceability and local reproducibility first. External Jyotish/ephemeris validation remains explicitly pending where marked.

## Gate Summary

| Gate | Result |
| --- | --- |
| Gate 1 - Formula inventory | 9 feature rows inventoried |
| Gate 2 - Astronomical baseline | 45 planet/node rows generated with Raman ayanamsa |
| Gate 3 - External validation template | 25 pass / 0 fail / 10 pending |
| Gate 4 - Trading replay | passed |

## Certification Labels

| Label | Count |
| --- | --- |
| do_not_train_raw_text | 1 |
| implemented_unvalidated | 6 |
| proxy_research_feature | 1 |
| replay_guarded_partial | 1 |

## Gate 1 - Inventory Preview

| Feature | Status | Strict/Proxy | Validation | Training Policy |
| --- | --- | --- | --- | --- |
| astronomy.raman_ayanamsa | implemented_unvalidated | strict astronomy setting | baseline_generated_pending_external_reference | allow_as_feature_after_external_position_check |
| astronomy.true_node_rahu_ketu | implemented_unvalidated | strict node position, proxy strength | baseline_generated_pending_external_reference | position_feature_ok_strength_policy_guarded |
| shadbala.full_component_v1 | implemented_unvalidated | strict formula attempt | full_component_v1_with_explicit_kaala_chesta_yuddha_decisions_pending_external_calculator_validation | train_as_provisional_numeric_feature_only |
| shadbala.avg_all_policy | implemented_unvalidated | research aggregation | pending_walk_forward_and_external_component_validation | train_with_explicit_artificial_feature_label |
| drik_bala.strict_formula | implemented_unvalidated | strict formula attempt | strict_formula_foundation | train_as_provisional_numeric_feature_only |
| drishti.event_orb_strength | proxy_research_feature | proxy | proxy_pending_strict_drik_bala | do_not_train_as_doctrine_strength |
| panchanga.sun_moon_core | implemented_unvalidated | formula foundation | formula_foundation_pending_traditional_validation | train_as_provisional_categorical_feature |
| rule_layer.auto_suggest_sr_gann | replay_guarded_partial | trading heuristic | case_127_data_replay_passed_cases_8_43_103_source_guarded | train_as_rule_lesson_with_outcome_tracking |
| local_llm_dreaming | do_not_train_raw_text | explanation layer | deterministic_verifier_required | do_not_train_raw_llm_output |

## Gate 2 - Position Baseline Preview

| Sample | Planet | Local Time | Ayanamsa | Ayanamsa Deg | Sidereal Lon Deg | Status |
| --- | --- | --- | --- | --- | --- | --- |
| case_8_event_start | SUN | 2025-03-07T19:30:00+05:30 | Raman | 22.762550303 | 324.485078254 | self_consistency_generated_pending_external_reference |
| case_8_event_start | MOON | 2025-03-07T19:30:00+05:30 | Raman | 22.762550303 | 65.838285879 | self_consistency_generated_pending_external_reference |
| case_8_event_start | RAHU_TRUE_NODE | 2025-03-07T19:30:00+05:30 | Raman | 22.762550303 | 334.703114194 | self_consistency_generated_pending_external_reference |
| case_8_event_start | KETU_DERIVED | 2025-03-07T19:30:00+05:30 | Raman | 22.762550303 | 154.703114194 | derived_from_true_node_plus_180_pending_external_reference |
| case_43_event_start | SUN | 2025-04-04T02:30:00+05:30 | Raman | 22.763594181 | 351.587295526 | self_consistency_generated_pending_external_reference |
| case_43_event_start | MOON | 2025-04-04T02:30:00+05:30 | Raman | 22.763594181 | 66.176779716 | self_consistency_generated_pending_external_reference |
| case_43_event_start | RAHU_TRUE_NODE | 2025-04-04T02:30:00+05:30 | Raman | 22.763594181 | 334.534898714 | self_consistency_generated_pending_external_reference |
| case_43_event_start | KETU_DERIVED | 2025-04-04T02:30:00+05:30 | Raman | 22.763594181 | 154.534898714 | derived_from_true_node_plus_180_pending_external_reference |
| case_103_event_start | SUN | 2025-05-15T22:30:00+05:30 | Raman | 22.765194263 | 32.342266392 | self_consistency_generated_pending_external_reference |
| case_103_event_start | MOON | 2025-05-15T22:30:00+05:30 | Raman | 22.765194263 | 245.719064875 | self_consistency_generated_pending_external_reference |
| case_103_event_start | RAHU_TRUE_NODE | 2025-05-15T22:30:00+05:30 | Raman | 22.765194263 | 332.669628041 | self_consistency_generated_pending_external_reference |
| case_103_event_start | KETU_DERIVED | 2025-05-15T22:30:00+05:30 | Raman | 22.765194263 | 152.669628041 | derived_from_true_node_plus_180_pending_external_reference |
| case_127_sr_touch_start | SUN | 2025-05-28T22:00:00+05:30 | Raman | 22.765690703 | 44.827534764 | self_consistency_generated_pending_external_reference |
| case_127_sr_touch_start | MOON | 2025-05-28T22:00:00+05:30 | Raman | 22.765690703 | 66.595833426 | self_consistency_generated_pending_external_reference |
| case_127_sr_touch_start | RAHU_TRUE_NODE | 2025-05-28T22:00:00+05:30 | Raman | 22.765690703 | 331.622625868 | self_consistency_generated_pending_external_reference |
| case_127_sr_touch_start | KETU_DERIVED | 2025-05-28T22:00:00+05:30 | Raman | 22.765690703 | 151.622625868 | derived_from_true_node_plus_180_pending_external_reference |
| gann_reference_tokyo | SUN | 1889-02-11T00:00:00+09:00 | Raman | 20.862224307 | 301.26895583 | self_consistency_generated_pending_external_reference |
| gann_reference_tokyo | MOON | 1889-02-11T00:00:00+09:00 | Raman | 20.862224307 | 61.083642978 | self_consistency_generated_pending_external_reference |
| gann_reference_tokyo | RAHU_TRUE_NODE | 1889-02-11T00:00:00+09:00 | Raman | 20.862224307 | 90.070041857 | self_consistency_generated_pending_external_reference |
| gann_reference_tokyo | KETU_DERIVED | 1889-02-11T00:00:00+09:00 | Raman | 20.862224307 | 270.070041857 | derived_from_true_node_plus_180_pending_external_reference |

## Gate 2 - Panchanga Baseline Preview

| Sample | Tithi | Paksha | Moon Nakshatra | Pada | Yoga | Karana | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| case_8_event_start | Navami | Shukla | Mrigashira | 4 | Ayushman | Balava | local_formula_baseline_pending_traditional_panchanga_check |
| case_43_event_start | Saptami | Shukla | Mrigashira | 4 | Shobhana | Gara | local_formula_baseline_pending_traditional_panchanga_check |
| case_103_event_start | Tritiya | Krishna | Mula | 2 | Siddha | Vishti | local_formula_baseline_pending_traditional_panchanga_check |
| case_127_sr_touch_start | Dvitiya | Shukla | Mrigashira | 4 | Shoola | Kaulava | local_formula_baseline_pending_traditional_panchanga_check |
| gann_reference_tokyo | Dashami | Shukla | Mrigashira | 3 | Vishkambha | Gara | local_formula_baseline_pending_traditional_panchanga_check |

## Gate 3 - External Validation

Fill the expected-value columns from trusted ephemeris, Panchanga, and Shadbala examples. On each run, the script preserves those entries and computes pass/fail where a direct comparison is possible.

| Status | Rows |
| --- | --- |
| pass | 25 |
| fail | 0 |
| pending | 10 |

## Gate 4 - Trading Replay

Status: `passed`

```text
{
  "pack_dir": "D:\\GannFinancialAstro\\doc\\repeatation_review_case_8_avg_all_moon_square_20260529_022249",
  "results": [
    {
      "case_id": 127,
      "status": "passed",
      "start_rule": "first_case_window_sr_line_touch",
      "start": {
        "x": "2025-05-28T22:00:00+05:30",
        "y": 144.965,
        "sr_price": 144.987277,
        "touch_gap_pips": 2.23,
        "touch_band_pips": 3.0,
        "touch_side": "top_wick",
        "gann_anchor_side": "top",
        "marker_label": "SATURN direct h=0.18 n=1.3 d=360 selected-case SR touch",
        "point_number": 191
      },
      "end": {
        "x": "2025-05-28T23:30:00+05:30",
        "y": 145.12528246460198,
        "trace_name": "Selected case touches",
        "marker_label": "Pair: AVG(ALL)|MOON Aspect: Square Duration: 3h 0m Orb: 76.850deg / 1.000deg BPHS-like orb proxy: 0.000 (0.0/60) Panchanga: Wednesday MERCURY | Shukla Dvitiya |",
        "is_selected_case_touch": true,
        "curveNumber": 106,
        "pointNumber": 0,
        "autoCandidate": true
      },
      "case_window_sr_touch_count": 3
    },
    {
      "case_id": 8,
      "status": "source_guard_passed",
      "note": "Family-rule teaching case still has expected rule/candidate guard text in generator."
    },
    {
      "case_id": 43,
      "status": "source_guard_passed",
      "note": "Family-rule teaching case still has expected rule/candidate guard text in generator."
    },
    {
      "case_id": 103,
      "status": "source_guard_passed",
      "note": "Family-rule teaching case still has expected rule/candidate guard text in generator."
    }
  ]
}
```

## Output Files

| Artifact | Path |
| --- | --- |
| inventory_csv | D:\PycharmProjects\astro_function_certification_inventory_20260527.csv |
| position_baseline_csv | D:\PycharmProjects\astro_position_baseline_20260527.csv |
| panchanga_baseline_csv | D:\PycharmProjects\panchanga_baseline_20260527.csv |
| external_validation_template_csv | D:\PycharmProjects\astro_external_validation_template_20260527.csv |
| trading_rule_replay_json | D:\PycharmProjects\trading_rule_replay_result_20260527.json |
| report_md | D:\PycharmProjects\astro_function_certification_report_20260527.md |

## Current Verdict

- Safe to continue manual review with these labels visible.
- Do not treat Shadbala/Drik/Panchanga as externally certified yet.
- Do not train on raw local LLM prose. Train on deterministic evidence, manual notes, verified rule lessons, and verifier corrections.
- Next certification lift: add external expected values for the Gate 3 template and factor browser Auto Suggest into reusable Python replay for cases 8, 43, and 103.
