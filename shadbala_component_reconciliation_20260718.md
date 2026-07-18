# Shadbala Component Reconciliation

Contract: `GANN_SHADBALA_COMPONENT_COMPARATOR_V2`

This is a diagnostic Tier B comparison. It does not certify a doctrine or
authorize execution. Source-profile formulas remain distinct from named
comparator compatibility profiles.

- External matrix: `D:\PycharmProjects\pyjhora_shadbala_components_20260718.csv`
- External SHA-256: `9FD387D50D802A6AF4ACCF905A3D171492E149D6FC5FF18EE9F54A0D2B745A50`
- External source: `PyJHora 4.8.7 Tier B isolated export; Raman ayanamsa; wheel sha256 D8D8014573A38DDEFEDCAE57D3B8D84687CAC2AD31BB5B1DD70D945906A4D54D; event civil timezone; Tokyo reference coordinates; Dig uses _dig_bala(method=2) canonical bounded circular-distance variant because the package default method=1 can exceed 60 virupa`
- Rows: `210`
- Passed: `145`
- Failed: `65`

## Component Summary

| Component | Pass | Fail | Mean absolute residual | Maximum residual |
| --- | ---: | ---: | ---: | ---: |
| chesta | 6 | 29 | 39.504888 | 115.204665 |
| dig | 35 | 0 | 0.002959 | 0.008614 |
| drik | 35 | 0 | 0.001143 | 0.010000 |
| kaala | 0 | 35 | 54.605393 | 238.423777 |
| naisargika | 35 | 0 | 0.000000 | 0.000000 |
| sthana | 34 | 1 | 0.538503 | 18.755998 |

## Largest Residuals

| Sample | Planet | Component | Local | External | Signed delta |
| --- | --- | --- | ---: | ---: | ---: |
| case_43_event_start | MOON | kaala | 93.176223 | 331.600000 | -238.423777 |
| case_43_event_start | SUN | kaala | 141.163925 | 4.090000 | +137.073925 |
| case_127_sr_touch_start | VENUS | kaala | 54.842933 | 175.700000 | -120.857067 |
| case_127_sr_touch_start | SUN | chesta | 115.204665 | 0.000000 | +115.204665 |
| case_103_event_start | SUN | chesta | 108.720072 | 0.000000 | +108.720072 |
| case_103_event_start | MARS | kaala | 203.453469 | 103.750000 | +99.703469 |
| case_103_event_start | MOON | chesta | 97.748801 | 0.000000 | +97.748801 |
| case_8_event_start | SATURN | kaala | 119.327320 | 27.420000 | +91.907320 |
| case_8_event_start | JUPITER | kaala | 155.336735 | 245.470000 | -90.133265 |
| gann_reference_tokyo | VENUS | kaala | 136.898381 | 225.370000 | -88.471619 |
| case_103_event_start | VENUS | kaala | 94.659789 | 181.140000 | -86.480211 |
| case_103_event_start | SATURN | chesta | 17.866292 | 101.980000 | -84.113708 |
| case_127_sr_touch_start | MARS | kaala | 244.753462 | 162.660000 | +82.093462 |
| case_103_event_start | MOON | kaala | 227.644429 | 145.870000 | +81.774429 |
| gann_reference_tokyo | MOON | chesta | 79.876458 | 0.000000 | +79.876458 |

## Boundary Sensitivity

- The sole Sthana compatibility failure is the 1889 Tokyo Jupiter fixture.
  Local Swiss Ephemeris places Jupiter at 249.992006 degrees while PyJHora
  places it at 250.002277 degrees. That 0.010271-degree difference crosses
  an exact divisional boundary and changes D3, D9, D12, and D30 assignments.
  It is retained as a boundary-instability witness, not forced to pass.

## Interpretation Lock

- A failed component identifies a formula/profile disagreement; it is not repaired by widening tolerance.
- Sthana uses the named PyJHora compatibility profile here; production retains the BPHS source weights and degree-bounded D1 Moolatrikona.
- Dig compares against PyJHora `_dig_bala(method=2)`, its bounded circular-distance implementation, not the package default method that can exceed 60 virupa.
- Kaala and Chesta residuals remain diagnostic because the production source profiles intentionally reject known unbounded or structurally incomplete comparator behavior.
- PyJHora is a secondary comparator. Jagannatha Hora or a reproducible worked example remains required.
- Where legitimate source variants disagree, preserve separate named profiles instead of silently blending them.
