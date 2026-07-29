# JHora Kaala Formula Profile Reconciliation

Contract: `GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V1`

Status: diagnostic formula profiles only; no production change.

The frozen certification tolerance remains 0.5 virupa. A profile that looks better is not promoted unless its remaining witness conflicts are resolved.

## Locked Visible JHora Results

| Profile | Pass | MAE | Max error | Recent pass | Historical pass |
| --- | --- | --- | --- | --- | --- |
| ayana_actual_declination | 13/35 | 1.973 | 9.010 | 11/28 | 2/7 |
| ayana_tropical_projection | 30/35 | 0.308 | 2.128 | 28/28 | 2/7 |
| hora_astronomical_sunrise | 33/35 | 3.429 | 60.000 | 26/28 | 7/7 |
| hora_variable_day_night | 27/35 | 13.714 | 60.000 | 22/28 | 5/7 |
| nathonnatha_apparent_solar | 11/35 | 1.847 | 5.146 | 10/28 | 1/7 |
| nathonnatha_lmt_source | 11/35 | 1.843 | 4.890 | 10/28 | 1/7 |

## Case-8 Hora Boundary

- Event LMT: `23.310020000` hours.
- Swiss apparent-tip sunrise LMT: `6.367290929` hours.
- Categorical award flip boundary: `6.310020000` hours.
- Gap: `3.436` minutes.
- Current lord: `MOON`; visible JHora lord: `SATURN`.

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
- Do not alter Hora. The two-row case-8 disagreement is one categorical award only; the award flips across a sunrise input separated by only a few minutes, so a visible JHora sunrise witness is required.
- The tropical-longitude Kranti Ayana profile is the strongest candidate: it passes all 28 recent visible rows and 30/35 overall, and it fits the two published rounded Ayana tables far better than true equatorial declination.
- Do not promote the Ayana candidate yet. Five 1889 rows remain outside the frozen tolerance and require visible JHora tropical longitude or intermediate Kranti evidence.
- No production formula, certification tolerance, ML feature, Auto Suggest rule, or execution path is changed by this diagnostic.

## Required Next Witness

- Hora: Capture case-8 JHora apparent-tip sunrise in LMT under the locked settings.
- Ayana: Capture visible JHora tropical longitudes or intermediate Kranti for the seven 1889 planets.
