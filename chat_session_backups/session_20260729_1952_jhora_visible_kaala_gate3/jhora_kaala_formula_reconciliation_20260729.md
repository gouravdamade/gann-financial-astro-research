# JHora Kaala Formula Profile Reconciliation

Contract: `GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V1`

Status: diagnostic formula profiles only; no production change.

The frozen certification tolerance remains 0.5 virupa. A profile that looks better is not promoted unless its remaining witness conflicts are resolved.

## Locked Visible JHora Results

| Profile | Pass | MAE | Max error | Recent pass | Historical pass |
| --- | --- | --- | --- | --- | --- |
| ayana_actual_declination | 13/35 | 1.973 | 9.010 | 11/28 | 2/7 |
| ayana_tropical_projection | 30/35 | 0.308 | 2.128 | 28/28 | 2/7 |
| hora_astronomical_sunrise | 35/35 | 0.000 | 0.000 | 28/28 | 7/7 |
| hora_variable_day_night | 27/35 | 13.714 | 60.000 | 22/28 | 5/7 |
| nathonnatha_apparent_solar | 11/35 | 1.594 | 3.541 | 10/28 | 1/7 |
| nathonnatha_lmt_source | 11/35 | 1.485 | 4.450 | 10/28 | 1/7 |

## Case-8 Hora Boundary

- Event LMT: `23.310020000` hours.
- Swiss apparent-tip sunrise LMT: `6.367290929` hours.
- Categorical award flip boundary: `6.310020000` hours.
- Gap: `3.436` minutes.
- Current lord: `MOON`; visible JHora lord: `MOON`.

This is a boundary-input dispute, not evidence for replacing the Hora sequence. The missing witness is JHora's visible sunrise under the locked apparent-tip setting.

## Published Worked-Table Cross-Check

### Nathonnatha

| Example | Calculated day | Published day | Calculated night | Published night |
| --- | --- | --- | --- | --- |
| Lady Diana | 26.083 | 26.0 | 33.917 | 33.0 |
| Prince William | 19.809 | 19.0 | 40.191 | 40.0 |

### Ayana

The tropical-longitude Kranti candidate has `0.417` virupa MAE and `1.098` maximum error against fourteen integer-rounded values in the two published tables.

## Evidence Conclusions

- Retain the LMT Nathonnatha source profile. It is the best of the tested time bases against visible JHora and independently reproduces the two published rounded worked tables closely.
- Do not alter Hora merely from this diagnostic. The former case-8 disagreement is one categorical award separated by only a few minutes of sunrise input; the separate fail-closed intermediate gate owns visible sunrise and award provenance.
- The tropical-longitude Kranti Ayana profile is the strongest candidate: it passes all 28 recent visible rows and 30/35 overall, and it fits the two published rounded Ayana tables far better than true equatorial declination.
- Do not promote the Ayana candidate yet. Five 1889 rows remain outside the frozen tolerance and require visible JHora tropical longitude or intermediate Kranti evidence.
- No production formula, certification tolerance, ML feature, Auto Suggest rule, or execution path is changed by this diagnostic.

## Required Next Witness

- Hora: Evaluate the case-8 apparent-tip sunrise and award through the separate hashed intermediate witness gate.
- Ayana: Evaluate seven visible historical tropical positions and Ayana values through the separate hashed intermediate witness gate.
