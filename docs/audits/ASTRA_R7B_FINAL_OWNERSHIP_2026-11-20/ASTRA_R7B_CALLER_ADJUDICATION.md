# Swiss Ephemeris caller adjudication

The event-search entry reached one unowned state-dependent conversion. SBC reached another in the same Python service domain. Neither demonstration measured a wrong longitude. All original 39 statements still map by module, operation and occurrence order to the working source. Current line numbers below come from parsing that source.

**Scope of each row.** The process for every row is the desktop Python backend/sidecar when reached from the named application entry. Observations here were made in a separate read-only Python harness importing that backend. An entry name identifies the source chain. A named helper probe establishes execution at that helper, not an observed HTTP request. “Held” records ownership of the actual shared RLock on the executing thread at the Swiss call. “Outside” records its absence. Calculations can update library internals; “mutate” identifies an explicit configuration setter. The data column identifies settings that matter, not a claim that every operation uses the sidereal model.

| ID | Current file and line (inventory line) | Function | Swiss operation | Entry | Evidence of activity | Configuration dependence | Operation | Shared lock | Outstanding check |
|---|---|---|---|---|---|---|---|---|---|
| 1 | financial_astro_ephemeris.py:79 (79) | configure_ephemeris | set_ephe_path | Phase / planetary lines / aspect houses | BPHS range, SBC rise, SBC set, SBC topo positions, aspect wrapper, batch ownership, chitra, chitra audit, event search, houses, lunar global, lunar local, solar local, solar remote locality, topo | data directory | mutate | held | Keep as regression fixture. |
| 2 | financial_astro_ephemeris.py:99 (99) | _jd_ut | julday | Phase / planetary lines / aspect houses | batch ownership, houses | calendar only | convert | held | Exclude calendar arithmetic from state gate. |
| 3 | financial_astro_ephemeris.py:141 (141) | _calc_longitude | get_current_file_data | Phase / planetary lines / aspect houses | batch ownership | last opened provider file | inspect | held | Observe read after calc in same owned interval. |
| 4 | financial_astro_ephemeris.py:233 (233) | sidereal_house_cusps | houses_ex | Phase / planetary lines / aspect houses | houses | sidereal model and site | calculate | held | Keep as regression fixture. |
| 5 | gann-astro-desk/backend/aspect_evidence_trace.py:184 (184) | _strict_observables_locked | julday | Aspect evidence via _aspect_strength_context | aspect wrapper | calendar only | convert | held | Exclude calendar arithmetic from state gate. |
| 6 | gann-astro-desk/backend/aspect_evidence_trace.py:189 (189) | _strict_observables_locked | calc_ut | Aspect evidence via _aspect_strength_context | aspect wrapper | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 7 | gann-astro-desk/backend/aspect_evidence_trace.py:190 (190) | _strict_observables_locked | calc_ut | Aspect evidence via _aspect_strength_context | aspect wrapper | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 8 | gann-astro-desk/backend/bphs_classical_timing_service.py:64 (64) | _julian_ut | julday | BPHS calendar range | BPHS range | calendar only | convert | held | Exclude calendar arithmetic from state gate. |
| 9 | gann-astro-desk/backend/bphs_classical_timing_service.py:68 (68) | _datetime_from_jd_ut | revjul | BPHS calendar range | BPHS range | calendar only | convert | held | Exclude calendar arithmetic from state gate. |
| 10 | gann-astro-desk/backend/bphs_classical_timing_service.py:177 (177) | configure_session | set_sid_mode | BPHS calendar range | BPHS range | sidereal model | mutate | held | Keep as regression fixture. |
| 11 | gann-astro-desk/backend/bphs_classical_timing_service.py:181 (181) | _sun_moon | calc_ut | BPHS calendar range | BPHS range | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 12 | gann-astro-desk/backend/bphs_classical_timing_service.py:182 (182) | _sun_moon | calc_ut | BPHS calendar range | BPHS range | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 13 | gann-astro-desk/backend/bphs_classical_timing_service.py:191 (191) | _sunrise_sunset | rise_trans | BPHS calendar range | BPHS range | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 14 | gann-astro-desk/backend/bphs_classical_timing_service.py:195 (195) | _sunrise_sunset | rise_trans | BPHS calendar range | BPHS range | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 15 | gann-astro-desk/backend/cgvo_service.py:159 (158) | _jd | julday | CGVO event search / locality / frame | chitra, chitra audit, event search, lunar global, lunar local, solar local, solar remote locality, topo | calendar only | convert | held | Exclude calendar arithmetic from state gate. |
| 16 | gann-astro-desk/backend/cgvo_service.py:165 (164) | _from_jd | revjul | CGVO event search / locality / frame | event search, lunar local, solar local, solar remote locality | calendar only | convert | held, outside | Exclude calendar arithmetic from state gate. |
| 17 | gann-astro-desk/backend/cgvo_service.py:174 (173) | _utc_display_from_jd | jdut1_to_utc | CGVO event search / locality / frame | event search, lunar local, solar local, solar remote locality | time model / applicable data | calculate | held, outside | Keep conversion inside configured transaction. |
| 18 | gann-astro-desk/backend/cgvo_service.py:258 (255) | _tropical_longitude | calc_ut | CGVO event search / locality / frame | R2C real tropical Sun | provider / flags and operation inputs | calculate | decorated; mock also saw setup | Retain fixture. |
| 19 | gann-astro-desk/backend/cgvo_service.py:265 (260) | _chitra_180_offset | fixstar2_ut | CGVO event search / locality / frame | chitra | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 20 | gann-astro-desk/backend/cgvo_service.py:286 (281) | _chitra_audit_offset | fixstar2_ut | CGVO event search / locality / frame | chitra audit | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 21 | gann-astro-desk/backend/cgvo_service.py:781 (776) | _topocentric_body_states | set_topo | CGVO event search / locality / frame | lunar local, solar local, solar remote locality, topo | observer | mutate | held | Keep as regression fixture. |
| 22 | gann-astro-desk/backend/cgvo_service.py:784 (779) | _topocentric_body_states | sidtime | CGVO event search / locality / frame | lunar local, solar local, solar remote locality, topo | time model / applicable data | calculate | held | Keep as regression fixture. |
| 23 | gann-astro-desk/backend/cgvo_service.py:787 (782) | _topocentric_body_states | calc_ut | CGVO event search / locality / frame | lunar local, solar local, solar remote locality, topo | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 24 | gann-astro-desk/backend/cgvo_service.py:788 (783) | _topocentric_body_states | azalt | CGVO event search / locality / frame | lunar local, solar local, solar remote locality, topo | time model and explicit site | calculate | held | Keep as regression fixture. |
| 25 | gann-astro-desk/backend/cgvo_service.py:876 (870) | _local_circumstances | sol_eclipse_when_loc | CGVO event search / locality / frame | solar local, solar remote locality | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 26 | gann-astro-desk/backend/cgvo_service.py:885 (879) | _local_circumstances | sol_eclipse_how | CGVO event search / locality / frame | solar remote locality | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 27 | gann-astro-desk/backend/cgvo_service.py:905 (899) | _local_circumstances | lun_eclipse_when_loc | CGVO event search / locality / frame | lunar local | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 28 | gann-astro-desk/backend/cgvo_service.py:915 (909) | _local_circumstances | lun_eclipse_how | CGVO event search / locality / frame | lunar local | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 29 | gann-astro-desk/backend/cgvo_service.py:1024 (1017) | _next_global_event | sol_eclipse_when_glob | CGVO event search / locality / frame | event search, solar local | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 30 | gann-astro-desk/backend/cgvo_service.py:1025 (1018) | _next_global_event | lun_eclipse_when | CGVO event search / locality / frame | lunar global | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| 31 | strict_shadbala_doctrine.py:652 (652) | julian_day_ut | julday | Aspect evidence via event_strict_shadbala_context | strict chesta, strict rise | calendar only | convert | held | Exclude calendar arithmetic from state gate. |
| 32 | strict_shadbala_doctrine.py:663 (663) | datetime_from_julian_day_ut | revjul | Aspect evidence via event_strict_shadbala_context | strict rise | calendar only | convert | held | Exclude calendar arithmetic from state gate. |
| 33 | strict_shadbala_doctrine.py:697 (697) | sunrise_sunset_lmt_for_date | rise_trans | Aspect evidence via event_strict_shadbala_context | strict rise | provider / flags and operation inputs | calculate | held | Bind provider/path before first stateful call. |
| 34 | strict_shadbala_doctrine.py:706 (706) | sunrise_sunset_lmt_for_date | rise_trans | Aspect evidence via event_strict_shadbala_context | strict rise | provider / flags and operation inputs | calculate | held | Bind provider/path before first stateful call. |
| 35 | strict_shadbala_doctrine.py:1218 (1218) | chesta_mean_true_context | deltat | Aspect evidence via event_strict_shadbala_context | strict chesta | time model / applicable data | calculate | held | Bind provider/path before first stateful call. |
| 36 | strict_shadbala_doctrine.py:1221 (1221) | chesta_mean_true_context | calc_ut | Aspect evidence via event_strict_shadbala_context | strict chesta | provider / flags and operation inputs | calculate | held | Bind provider/path before first stateful call. |
| 37 | strict_shadbala_doctrine.py:1229 (1229) | chesta_mean_true_context | get_orbital_elements | Aspect evidence via event_strict_shadbala_context | strict chesta | provider / flags and operation inputs | calculate | held | Bind provider/path before first stateful call. |
| 38 | strict_shadbala_doctrine.py:1236 (1236) | chesta_mean_true_context | get_orbital_elements | Aspect evidence via event_strict_shadbala_context | strict chesta | provider / flags and operation inputs | calculate | held | Bind provider/path before first stateful call. |
| 39 | swiss_ephemeris_runtime.py:36 (36) | checked_calc_ut | calc_ut | Phase batch via _calc_longitude | batch ownership | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |

## Operations omitted by the original absolute-import scan

| ID | Current file and line (inventory line) | Function | Swiss operation | Entry | Evidence of activity | Configuration dependence | Operation | Shared lock | Outstanding check |
|---|---|---|---|---|---|---|---|---|---|
| S1 | sbc/ephemeris.py:45 (omitted) | _julian_ut | utc_to_jd | SBC snapshot / provider methods | SBC rise, SBC set, SBC topo positions | time model / applicable data | calculate | held | Keep as regression fixture. |
| S2 | sbc/ephemeris.py:58 (omitted) | _datetime_from_jd_ut | jdut1_to_utc | SBC snapshot / provider methods | SBC rise, SBC set | time model / applicable data | calculate | outside | Keep conversion inside configured transaction. |
| S3 | sbc/ephemeris.py:107 (omitted) | _configure | set_sid_mode | SBC snapshot / provider methods | SBC rise, SBC set, SBC topo positions | sidereal model | mutate | held | Keep as regression fixture. |
| S4 | sbc/ephemeris.py:109 (omitted) | _configure | set_topo | SBC snapshot / provider methods | SBC topo positions | observer | mutate | held | Keep as regression fixture. |
| S5 | sbc/ephemeris.py:132 (omitted) | _evidence | get_current_file_data | SBC snapshot / provider methods | SBC topo positions | last opened provider file | inspect | held | Observe read after calc in same owned interval. |
| S6 | sbc/ephemeris.py:164 (omitted) | _position | calc_ut | SBC snapshot / provider methods | SBC topo positions | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| S7 | sbc/ephemeris.py:242 (omitted) | sunrise_for_local_date | rise_trans | SBC snapshot / provider methods | SBC rise | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |
| S8 | sbc/ephemeris.py:270 (omitted) | sunset_for_local_date | rise_trans | SBC snapshot / provider methods | SBC set | provider / flags and operation inputs | calculate | held | Keep as regression fixture. |

The SBC sunrise path is used by the sun-based weekday calculation. Its sunset counterpart exhibited the same defect under direct invocation; a separate application caller of sunset was not located. SBC positions configures and reads flags/file information inside positions' shared lock. The generic doctrine adapter at doctrine_config.py:203 calls swe_module.set_sid_mode with the shared lock held. The CGVO search trace observed it under its outer transaction. phase_provenance_assessment imports Swiss constants only.

An expanded static traversal of server.py and backend_sidecar.py including package-relative imports reached 80 local Python modules versus the earlier 73. The dynamic sidecar import resolves to server. The allowlisted worker dispatch in runtime_support.py runs in worker mode; subprocesses created by generation.py and runtime_support have distinct address spaces. Their ephemeris settings cannot interleave in the server process. Standalone mode_reference.py, the historic audit oracle and test fixtures have no production route. None of the 39 entries can be discarded as a test or archived script merely because its witness is a test.

The configuration and calculation are jointly owned at the inspected phase batch and single-value wrappers, aspect observable wrapper, BPHS range, CGVO tropical/star/topocentric/eclipse helpers and SBC positions. Shadbala's two decorated groups own execution but do not set their file/provider configuration. They are conditionally reachable from aspect evidence after the observable wrapper releases its lock. A prior request can supply their ambient file state. The sidereal Sun argument in Chesta is an explicit input; setting an arbitrary ayanamsha there would change the scientific question.

## Runtime observations

A real event-search service call covering 7–10 April 2024 returned one solar event. It observed one path setter, one sidereal setter and one solar global search under the shared lock, seven ordinary reverse calendar conversions outside, and six UT1-to-UTC conversions outside. SBC sunrise and sunset each observed an owned rise_trans followed by an unowned jdut1_to_utc. Solar and lunar local helpers also exercised the same CGVO conversion *inside* their outer lock. Correct one entry without losing the protected case. The BPHS probe used a one-hour window in Kolkata. Helpers exercised both eclipse types, both star-offset paths, topocentric geometry and both strict calculation groups. These probes test ownership only. Prior R2C numbers of 38 and 15 passing checks refer to its selected suites; the interrupted wider suite supplies no additional pass.

## Evidence identity

Repository D:/gann_r2b_sec_integration at e1b2f6350932165cdac8022314c78ebccad1a211 plus working files. SHA-256 prefixes distinguish the inspected source from the November 19 Astra closing ZIP. The R2C six reports and R2B-R2 inventory, reference and certification documents are under D:/GannFinancialAstro/research_outputs/MO_PRODUCT_02_R7B_R2C_20261120 and MO_PRODUCT_02_R7B_R2B_R2_20261120 respectively.

| Source | Inspected SHA-256 prefix | Historical Astra prefix |
|---|---|---|
| financial_astro_ephemeris.py | 189d3292eb42d63e | e30ecf16453c47be |
| gann-astro-desk/backend/aspect_evidence_trace.py | 19050b65cbcd37e2 | outside closing ZIP |
| gann-astro-desk/backend/bphs_classical_timing_service.py | 237d1fa13f852caa | outside closing ZIP |
| gann-astro-desk/backend/cgvo_service.py | b1c1e8f5411d6863 | outside closing ZIP |
| strict_shadbala_doctrine.py | 54ad6ce6d1e6be29 | outside closing ZIP |
| swiss_ephemeris_runtime.py | 874f46eea4e98121 | ae7f8c803c1f0e3d |
| sbc/ephemeris.py | a28d9951c6372852 | outside closing ZIP |
| doctrine_config.py | c17c16e7f522fab1 | outside closing ZIP |
| gann-astro-desk/backend/phase_provenance_assessment.py | f700fb13d8f2c6fc | outside closing ZIP |
| gann-astro-desk/backend/test_cgvo_runtime_ownership.py | 42d2fd9b52419c42 | outside closing ZIP |
| gann-astro-desk/backend/avg_all_currency_phase.py | b49cf62f17dd2fc3 | de29fee4767f3847 |
| test_swiss_ephemeris_runtime_r7b.py | f65cd218bd6d1aa7 | e08bffad914fe5f3 |
| gann-astro-desk/backend/test_avg_all_currency_phase.py | e1107c574476a4f0 | 129925065673cfdc |
| gann-astro-desk/src/avgAllCurrencyPhase.ts | a9615f72acb3f52d | a6f0697f59f6b498 |

The upstream UT1-to-UTC routine invokes the Delta T model and UTC conversion consults leap-second data. Treat this as a state-dependent time operation. The observed lock gap proves an ownership exception, not a measured time error. [Swiss Ephemeris date implementation](https://github.com/aloistr/swisseph/blob/master/swedate.c)

