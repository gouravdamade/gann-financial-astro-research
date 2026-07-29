# Astro Function Certification 4-Gate Report

- Report version: `astro_certification_4_gate_v10_kaala_formula_profiles_20260729`
- Generated: `2026-07-29T14:46:26+05:30`
- Important interpretation: this report certifies traceability and local reproducibility first. Pending and failed external checks remain explicit and fail closed.

## Gate Summary

| Gate | Result |
| --- | --- |
| Gate 1 - Formula inventory | 9 feature rows inventoried |
| Gate 2 - Astronomical baseline | 45 planet/node rows generated with Raman ayanamsa |
| Gate 3 - External validation | failed_external_validation: 60 pass / 35 fail / 0 pending |
| Gate 4 - Trading replay | skipped |

## Certification Labels

| Label | Count |
| --- | --- |
| do_not_train_raw_text | 1 |
| failed_independent_validation | 1 |
| implemented_unvalidated | 5 |
| proxy_research_feature | 1 |
| replay_guarded_partial | 1 |

## Gate 1 - Inventory Preview

| Feature | Status | Strict/Proxy | Validation | Training Policy |
| --- | --- | --- | --- | --- |
| astronomy.raman_ayanamsa | implemented_unvalidated | strict astronomy setting | baseline_generated_pending_external_reference | allow_as_feature_after_external_position_check |
| astronomy.true_node_rahu_ketu | implemented_unvalidated | strict node position, proxy strength | baseline_generated_pending_external_reference | position_feature_ok_strength_policy_guarded |
| shadbala.bphs_component_reconciliation_v9 | implemented_unvalidated | versioned source profile with named comparator variants | provisional_independent_jhora_witness_failed_reconciliation_in_progress | train_as_provisional_numeric_feature_only |
| shadbala.avg_all_policy | implemented_unvalidated | research aggregation | pending_walk_forward_and_external_component_validation | train_with_explicit_artificial_feature_label |
| drik_bala.reconciled_formula_v2 | failed_independent_validation | versioned reconciled formula | tier_b_pyjhora_aligned_independent_jhora_disagrees_9_of_35 | exclude_from_certified_ml_features_keep_research_diagnostic |
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
| Independent JHora/worked-example witness | failed_independent_validation |

### Visible JHora Kaala Witness

Status: `partial_component_validation`. This evidence can validate individual Kaala subcomponents; it does not certify aggregate Kaala or full Shadbala.

| Component | Local pass | Rows | MAE virupa | Max error virupa |
| --- | --- | --- | --- | --- |
| abda | 35 | 35 | 0.0 | 0.0 |
| ayana | 13 | 35 | 1.973373426 | 9.010454001 |
| hora | 33 | 35 | 3.428571429 | 60.0 |
| masa | 35 | 35 | 0.0 | 0.0 |
| nathonnatha | 11 | 35 | 1.842805714 | 4.8899 |
| paksha | 35 | 35 | 0.039841769 | 0.123677207 |
| total | 4 | 35 | 6.349790459 | 62.908905083 |
| tribhaga | 35 | 35 | 0.0 | 0.0 |
| vara | 35 | 35 | 0.0 | 0.0 |
| yuddha | 35 | 35 | 0.0 | 0.0 |

### Kaala Formula Profile Reconciliation

Status: `diagnostic_profiles_only_no_production_change`. These profiles diagnose the remaining Hora, Nathonnatha, and Ayana differences. They do not change production formulas, widen the frozen tolerance, certify aggregate Kaala, or authorize ML or execution use.

| Profile | Pass | Rows | MAE virupa | Recent pass | Historical pass |
| --- | --- | --- | --- | --- | --- |
| Nathonnatha - current LMT | 11 | 35 | 1.843 | 10/28 | 1/7 |
| Nathonnatha - apparent solar | 11 | 35 | 1.847 | 10/28 | 1/7 |
| Hora - current sunrise award | 33 | 35 | 3.429 | 26/28 | 7/7 |
| Hora - variable day/night hours | 27 | 35 | 13.714 | 22/28 | 5/7 |
| Ayana - current actual declination | 13 | 35 | 1.973 | 11/28 | 2/7 |
| Ayana - tropical Kranti candidate | 30 | 35 | 0.308 | 28/28 | 2/7 |

Case 8 Hora boundary: current lord `MOON`, visible JHora lord `SATURN`; the award flips across only `3.436` minutes of sunrise input. A visible JHora sunrise/intermediate witness is required before changing Hora.

The tropical-Kranti Ayana candidate matches all 28 recent rows and 30/35 overall, but only 2/7 historical rows. It remains a candidate until JHora tropical longitude or intermediate Kranti is captured for the five failing 1889 rows.

### Shadbala Component Admission Boundary

Status: `partial_independent_witness_alignment`. Independent witness alignment requires every one of the 35 locked rows to pass at 0.5 virupa. It does not establish source certification, financial validation, or execution permission.

| Top-level component | Pass | Rows | MAE virupa | Max error virupa | Admission |
| --- | --- | --- | --- | --- | --- |
| chesta | 12 | 35 | 17.919 | 98.228 | provisional |
| dig | 19 | 35 | 1.142 | 3.562 | provisional |
| drik | 9 | 35 | 7.320 | 35.390 | provisional |
| kaala | 5 | 35 | 2.763 | 8.879 | provisional |
| naisargika | 35 | 35 | 0.004 | 0.010 | witness aligned |
| sthana | 1 | 35 | 6.296 | 12.628 | provisional |
| total | 3 | 35 | 11.829 | 30.258 | provisional |

Witness-aligned Kaala subcomponents: abda, masa, paksha, tribhaga, vara, yuddha.

External import issues:

- none

## Gate 4 - Trading Replay

Status: `skipped`

```text
reviewer replay skipped by CLI flag
```

## Output Files

| Artifact | Path |
| --- | --- |
| inventory_csv | D:\PycharmProjects\astro_function_certification_inventory_20260729.csv |
| position_baseline_csv | D:\PycharmProjects\astro_position_baseline_20260729.csv |
| panchanga_baseline_csv | D:\PycharmProjects\panchanga_baseline_20260729.csv |
| drik_contribution_ledger_csv | D:\PycharmProjects\drik_contribution_ledger_20260729.csv |
| external_validation_template_csv | D:\PycharmProjects\astro_external_validation_template_20260729.csv |
| independent_drik_validation_template_csv | D:\PycharmProjects\jhora_drik_independent_validation_template_20260729.csv |
| external_validation_gate_json | D:\PycharmProjects\astro_external_validation_gate_20260729.json |
| trading_rule_replay_json | D:\PycharmProjects\trading_rule_replay_result_20260729.json |
| report_md | D:\PycharmProjects\astro_function_certification_report_20260729.md |

## Current Verdict

- Safe to continue astronomy/doctrine inspection with these labels visible.
- Tier B Drik comparison is 35 pass / 0 fail. The end-to-end component diagnostic is 145 pass / 55 fail / 10 structural N/A: Dig 35/35, Drik 35/35, Naisargika 35/35, Sthana 34/35, comparable Chesta 6/25, and Kaala 0/35. Shared-input formulas pass 60/60 comparable rows: Sthana 35/35 and Mars-Saturn Chesta 25/25. The locked local-versus-JHora reconciliation excludes displayed Sun/Moon Chesta from the total and promotes dynamic Paksha after 35/35 visible subcomponent matches. The actual production source profile, rather than the separately named PyJHora-compatible Sthana profile, is used for this gate: Sthana passes 1/35 and full total passes 3/35 with 11.829 virupa mean absolute error. Top-level local Kaala passes 5/35 with 2.763 virupa mean absolute error; Hora, Nathonnatha, Ayana, and aggregate Kaala remain provisional. The completed independent JHora Drik witness passes 9/35 and fails 26/35. Keep full Shadbala and Drik excluded from certified ML/execution until the doctrine profiles are explicitly reconciled.
- Do not train on raw local LLM prose. Train on deterministic evidence, manual notes, verified rule lessons, and verifier corrections.
- Gate 4 is blocked until corrected versioned data replaces the legacy double-sidereal case records.
