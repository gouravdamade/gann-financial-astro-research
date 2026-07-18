# Astro Function Certification 4-Gate Report

- Report version: `astro_certification_4_gate_v4_drik_reconciled_20260718`
- Generated: `2026-07-18T06:56:50+05:30`
- Important interpretation: this report certifies traceability and local reproducibility first. Pending and failed external checks remain explicit and fail closed.

## Gate Summary

| Gate | Result |
| --- | --- |
| Gate 1 - Formula inventory | 9 feature rows inventoried |
| Gate 2 - Astronomical baseline | 45 planet/node rows generated with Raman ayanamsa |
| Gate 3 - External validation | failed_external_validation: 60 pass / 35 fail / 0 pending |
| Gate 4 - Trading replay | blocked_legacy_dataset |

## Certification Labels

| Label | Count |
| --- | --- |
| do_not_train_raw_text | 1 |
| implemented_unvalidated | 5 |
| proxy_research_feature | 1 |
| replay_guarded_partial | 1 |
| tier_b_aligned_pending_independent_validation | 1 |

## Gate 1 - Inventory Preview

| Feature | Status | Strict/Proxy | Validation | Training Policy |
| --- | --- | --- | --- | --- |
| astronomy.raman_ayanamsa | implemented_unvalidated | strict astronomy setting | baseline_generated_pending_external_reference | allow_as_feature_after_external_position_check |
| astronomy.true_node_rahu_ketu | implemented_unvalidated | strict node position, proxy strength | baseline_generated_pending_external_reference | position_feature_ok_strength_policy_guarded |
| shadbala.source_aligned_provisional_v5 | implemented_unvalidated | strict formula attempt | provisional_source_aligned_drik_tier_b_pending_sunrise_abda_masa_chesta_yuddha_and_independent_validation | train_as_provisional_numeric_feature_only |
| shadbala.avg_all_policy | implemented_unvalidated | research aggregation | pending_walk_forward_and_external_component_validation | train_with_explicit_artificial_feature_label |
| drik_bala.reconciled_formula_v2 | tier_b_aligned_pending_independent_validation | versioned reconciled formula | tier_b_pyjhora_aligned_pending_independent_jhora_or_worked_example | train_as_provisional_numeric_feature_only |
| drishti.event_orb_strength | proxy_research_feature | proxy | event_orb_proxy_not_drik_bala | do_not_train_as_doctrine_strength |
| panchanga.sun_moon_core | implemented_unvalidated | formula foundation | formula_foundation_pending_traditional_validation | train_as_provisional_categorical_feature |
| rule_layer.auto_suggest_sr_gann | replay_guarded_partial | trading heuristic | versioned_corrected_golden_replay_passed_5_cases | train_rule_lessons_only_until_prospective_gate |
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

Gate status: `failed_external_validation`

| Status | Rows |
| --- | --- |
| pass | 60 |
| fail | 35 |
| pending | 0 |

| Strength matrix | Rows |
| --- | --- |
| expected | 70 |
| actual | 70 |
| pass | 35 |
| fail | 35 |
| pending | 0 |

| Drik validation layer | Status |
| --- | --- |
| Tier B PyJHora comparator | 35 pass / 0 fail |
| Independent JHora/worked-example witness | blocked_pending_independent_values |

External import issues:

- none

## Gate 4 - Trading Replay

Status: `blocked_legacy_dataset`

```text
Trading replay is intentionally blocked: current case records use the quarantined legacy astronomy contract. Rebuild versioned corrected fixtures before certifying Gate 4. Use --legacy-archive-replay only for historical comparison.
```

## Output Files

| Artifact | Path |
| --- | --- |
| inventory_csv | D:\PycharmProjects\astro_function_certification_inventory_20260718.csv |
| position_baseline_csv | D:\PycharmProjects\astro_position_baseline_20260718.csv |
| panchanga_baseline_csv | D:\PycharmProjects\panchanga_baseline_20260718.csv |
| drik_contribution_ledger_csv | D:\PycharmProjects\drik_contribution_ledger_20260718.csv |
| external_validation_template_csv | D:\PycharmProjects\astro_external_validation_template_20260718.csv |
| independent_drik_validation_template_csv | D:\PycharmProjects\jhora_drik_independent_validation_template_20260718.csv |
| external_validation_gate_json | D:\PycharmProjects\astro_external_validation_gate_20260718.json |
| trading_rule_replay_json | D:\PycharmProjects\trading_rule_replay_result_20260718.json |
| report_md | D:\PycharmProjects\astro_function_certification_report_20260718.md |

## Current Verdict

- Safe to continue astronomy/doctrine inspection with these labels visible.
- Tier B Drik comparison is 35 pass / 0 fail, while the remaining Shadbala total rows still fail. Keep the full strength feature set provisional, and do not call Drik independently certified until its separate JHora/worked-example witness passes.
- Do not train on raw local LLM prose. Train on deterministic evidence, manual notes, verified rule lessons, and verifier corrections.
- Gate 4 is blocked until corrected versioned data replaces the legacy double-sidereal case records.
