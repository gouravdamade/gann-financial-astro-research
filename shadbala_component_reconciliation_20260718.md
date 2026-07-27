# Shadbala Component Reconciliation

Contract: `GANN_SHADBALA_COMPONENT_COMPARATOR_V3`

This is a diagnostic Tier B comparison. It does not certify a doctrine or
authorize execution. It reports three matrices separately so formula
agreement cannot be confused with source-doctrine certification.

- Component matrix SHA-256: `9FD387D50D802A6AF4ACCF905A3D171492E149D6FC5FF18EE9F54A0D2B745A50`
- Kaala matrix SHA-256: `6DDD82E0185649901D8C34C63E829975817547FA6F33A4B5225E51FEAD3A054A`
- Shared-input matrix SHA-256: `077EB4AAC0D048F6555168855986BBD21EDC306AD892073D0E377D561075B9F3`
- External source: `PyJHora 4.8.7 Tier B isolated export; Raman ayanamsa; wheel sha256 D8D8014573A38DDEFEDCAE57D3B8D84687CAC2AD31BB5B1DD70D945906A4D54D; event civil timezone; Tokyo reference coordinates; Dig uses _dig_bala(method=2) canonical bounded circular-distance variant because the package default method=1 can exceed 60 virupa`

## Matrix Totals

| Matrix | Rows | Comparable | Pass | Fail | Structural N/A |
| --- | ---: | ---: | ---: | ---: | ---: |
| End-to-end components | 210 | 200 | 145 | 55 | 10 |
| Kaala subcomponents | 350 | 350 | 216 | 134 | 0 |
| Shared-input formulas | 70 | 60 | 60 | 0 | 10 |

## End-to-End Component Summary

| Measure | Comparable | Pass | Fail | Structural N/A | Mean absolute residual | Maximum residual |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| chesta | 25 | 6 | 19 | 10 | 28.156280 | 84.113708 |
| dig | 35 | 35 | 0 | 0 | 0.002959 | 0.008614 |
| drik | 35 | 35 | 0 | 0 | 0.001143 | 0.010000 |
| kaala | 35 | 0 | 35 | 0 | 57.859167 | 217.876423 |
| naisargika | 35 | 35 | 0 | 0 | 0.000000 | 0.000000 |
| sthana | 35 | 34 | 1 | 0 | 0.538503 | 18.755998 |

## Kaala Subcomponent Summary

| Measure | Comparable | Pass | Fail | Structural N/A | Mean absolute residual | Maximum residual |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| abda | 35 | 35 | 0 | 0 | 0.000000 | 0.000000 |
| ayana | 35 | 13 | 22 | 0 | 3.963336 | 28.936986 |
| hora | 35 | 25 | 10 | 0 | 17.142857 | 60.000000 |
| masa | 35 | 35 | 0 | 0 | 0.000000 | 0.000000 |
| nathonnatha | 35 | 5 | 30 | 0 | 19.292589 | 37.860100 |
| paksha | 35 | 6 | 29 | 0 | 46.690912 | 120.006323 |
| total | 35 | 0 | 35 | 0 | 57.859167 | 217.876423 |
| tribhaga | 35 | 31 | 4 | 0 | 6.857143 | 60.000000 |
| vara | 35 | 35 | 0 | 0 | 0.000000 | 0.000000 |
| yuddha | 35 | 31 | 4 | 0 | 0.336000 | 4.280000 |

## Shared-Input Formula Summary

| Measure | Comparable | Pass | Fail | Structural N/A | Mean absolute residual | Maximum residual |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| chesta | 25 | 25 | 0 | 10 | 0.002421 | 0.004967 |
| sthana | 35 | 35 | 0 | 0 | 0.002925 | 0.009273 |

## Largest End-to-End Numeric Residuals

| Sample | Planet | Component | Local | External | Signed delta |
| --- | --- | --- | ---: | ---: | ---: |
| case_43_event_start | MOON | kaala | 113.723577 | 331.600000 | -217.876423 |
| case_43_event_start | SUN | kaala | 141.163925 | 4.090000 | +137.073925 |
| case_127_sr_touch_start | VENUS | kaala | 54.842933 | 175.700000 | -120.857067 |
| case_127_sr_touch_start | MOON | kaala | 171.437701 | 60.220000 | +111.217701 |
| case_103_event_start | MARS | kaala | 203.453469 | 103.750000 | +99.703469 |
| case_8_event_start | SATURN | kaala | 119.327320 | 27.420000 | +91.907320 |
| case_8_event_start | JUPITER | kaala | 155.336735 | 245.470000 | -90.133265 |
| gann_reference_tokyo | VENUS | kaala | 136.898381 | 225.370000 | -88.471619 |
| case_103_event_start | VENUS | kaala | 94.659789 | 181.140000 | -86.480211 |
| case_103_event_start | SATURN | chesta | 17.866292 | 101.980000 | -84.113708 |
| case_127_sr_touch_start | MARS | kaala | 244.753462 | 162.660000 | +82.093462 |
| case_103_event_start | MOON | kaala | 227.644429 | 145.870000 | +81.774429 |
| case_127_sr_touch_start | SATURN | chesta | 21.887369 | 97.960000 | -76.072631 |
| case_43_event_start | JUPITER | chesta | 22.179133 | 97.340000 | -75.160867 |
| gann_reference_tokyo | MERCURY | chesta | 22.988458 | 97.400000 | -74.411542 |

## Interpretation Lock

- Sun and Moon Chesta are structural N/A rows: the BPHS source profile assigns Ayana/Paksha while PyJHora's epoch-table vector returns zero.
- Mars-Saturn shared-input Chesta checks only whether our compatibility helper reproduces PyJHora's epoch-table linear formula. It does not replace the production Swiss osculating source profile.
- Shared-input Sthana removes ephemeris drift by feeding both formulas the same PyJHora longitudes and ascendant.
- Kaala remains decomposed into nine contributors plus total; disagreement must be resolved contributor by contributor, never by widening tolerance.
- PyJHora is a secondary comparator. Jagannatha Hora or a reproducible worked example remains the independent deciding witness.
- No comparator result authorizes Auto Suggest, ML training, or live orders.
