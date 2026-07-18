# Shadbala Component Reconciliation

Contract: `GANN_SHADBALA_COMPONENT_COMPARATOR_V1`

This is a diagnostic Tier B comparison. It does not certify a doctrine or
authorize execution. The local formulas remain unchanged.

- External matrix: `D:\PycharmProjects\pyjhora_shadbala_components_20260718.csv`
- External SHA-256: `281497DBFF577DEB10B2CCCD27270C9F013887791739E83054F524D9C8F8075E`
- External source: `PyJHora 4.8.7 Tier B isolated export; Raman ayanamsa; wheel sha256 D8D8014573A38DDEFEDCAE57D3B8D84687CAC2AD31BB5B1DD70D945906A4D54D; event civil timezone; Tokyo reference coordinates`
- Rows: `210`
- Passed: `96`
- Failed: `114`

## Component Summary

| Component | Pass | Fail | Mean absolute residual | Maximum residual |
| --- | ---: | ---: | ---: | ---: |
| chesta | 1 | 34 | 43.028149 | 113.939558 |
| dig | 25 | 10 | 12.723352 | 98.939010 |
| drik | 35 | 0 | 0.001143 | 0.010000 |
| kaala | 0 | 35 | 64.796717 | 253.423777 |
| naisargika | 35 | 0 | 0.000000 | 0.000000 |
| sthana | 0 | 35 | 40.988783 | 127.501342 |

## Largest Residuals

| Sample | Planet | Component | Local | External | Signed delta |
| --- | --- | --- | ---: | ---: | ---: |
| case_43_event_start | MOON | kaala | 78.176223 | 331.600000 | -253.423777 |
| case_8_event_start | SATURN | kaala | 209.176949 | 27.420000 | +181.756949 |
| case_43_event_start | SUN | kaala | 185.832161 | 4.090000 | +181.742161 |
| gann_reference_tokyo | VENUS | sthana | 311.891342 | 184.390000 | +127.501342 |
| case_103_event_start | VENUS | sthana | 356.876219 | 229.380000 | +127.496219 |
| case_127_sr_touch_start | VENUS | sthana | 357.326325 | 231.830000 | +125.496325 |
| case_127_sr_touch_start | SUN | chesta | 113.939558 | 0.000000 | +113.939558 |
| case_103_event_start | SUN | chesta | 107.603571 | 0.000000 | +107.603571 |
| case_127_sr_touch_start | JUPITER | sthana | 339.831564 | 237.330000 | +102.501564 |
| case_8_event_start | VENUS | sthana | 291.810328 | 191.810000 | +100.000328 |
| case_43_event_start | SATURN | dig | 10.530990 | 109.470000 | -98.939010 |
| case_103_event_start | MOON | chesta | 97.748801 | 0.000000 | +97.748801 |
| case_8_event_start | JUPITER | kaala | 154.692721 | 245.470000 | -90.777279 |
| case_127_sr_touch_start | MERCURY | kaala | 124.228025 | 214.980000 | -90.751975 |
| case_103_event_start | MOON | kaala | 236.198701 | 145.870000 | +90.328701 |

## Interpretation Lock

- A failed component identifies a formula/profile disagreement; it is not repaired by widening tolerance.
- PyJHora is a secondary comparator. Jagannatha Hora or a reproducible worked example remains required.
- Where legitimate source variants disagree, preserve separate named profiles instead of silently blending them.
