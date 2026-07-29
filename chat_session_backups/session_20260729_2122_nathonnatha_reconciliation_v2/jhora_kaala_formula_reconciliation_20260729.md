# JHora Kaala Formula Profile Reconciliation

Contract: `GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V2`

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
| nathonnatha_astronomical_midnight | 11/35 | 1.592 | 3.566 | 10/28 | 1/7 |
| nathonnatha_lmt_source | 11/35 | 1.485 | 4.450 | 10/28 | 1/7 |

## Case-8 Hora Boundary

- Event LMT: `23.310020000` hours.
- Swiss apparent-tip sunrise LMT: `6.367290929` hours.
- Categorical award flip boundary: `6.310020000` hours.
- Gap: `3.436` minutes.
- Current lord: `MOON`; visible JHora lord: `MOON`.

This was a boundary-input dispute, not evidence for replacing the Hora sequence. The later hashed intermediate packet captured JHora's visible sunrise and Moon award under the locked apparent-tip setting, confirming the narrow 35/35 profile.

## Nathonnatha Astronomical-Midnight Test

The candidate uses the nearest midpoint between sunset and the following sunrise. Times below or above 24:00 preserve the adjacent civil date so the distance calculation remains unambiguous.

| Fixture | Event LMT | Selected midnight | Distance hours | Day strength |
| --- | --- | --- | --- | --- |
| case_8_event_start | 2025-03-07T23:18:36.072000+00:00 | 24.176860 | 0.866840 | 4.334198 |
| case_43_event_start | 2025-04-04T06:18:36.072000+00:00 | 0.048101 | 6.261919 | 31.309593 |
| case_103_event_start | 2025-05-16T02:18:36.072000+00:00 | -0.063674 | 2.373694 | 11.868468 |
| case_127_sr_touch_start | 2025-05-29T01:48:36.072000+00:00 | -0.046430 | 1.856450 | 9.282250 |
| gann_reference_tokyo | 1889-02-11T00:18:36.072000+00:00 | 0.236743 | 0.073277 | 0.366387 |

This explicit astronomical-midnight profile still passes only `11/35` visible JHora rows. It is therefore rejected as a compatibility formula and is not a production doctrine change.

## Published Worked-Table Cross-Check

### Nathonnatha

| Example | Calculated day | Published day | Calculated night | Published night |
| --- | --- | --- | --- | --- |
| Lady Diana | 26.083 | 26.0 | 33.917 | 33.0 |
| Prince William | 19.809 | 19.0 | 40.191 | 40.0 |

### Ayana

The tropical-longitude Kranti candidate has `0.417` virupa MAE and `1.098` maximum error against fourteen integer-rounded values in the two published tables.

## Evidence Conclusions

- Retain the LMT Nathonnatha source profile because BPHS defines the component from midnight to apparent birth time and the locked published worked tables are independently reproduced closely with LMT.
- Reject the astronomical-midnight compatibility hypothesis. Using the nearest midpoint of apparent-tip sunset and sunrise still passes only 11/35 visible JHora rows and does not explain the case-8 or historical residual.
- Visible JHora Nathonnatha remains a software-compatibility discrepancy rather than evidence that the source-backed LMT formula is wrong. LMT, apparent-solar time, and astronomical midnight all fail in different residual patterns, so no JHora-mimicking correction is admitted.
- Do not alter Hora merely from this diagnostic. The former case-8 disagreement is one categorical award separated by only a few minutes of sunrise input. The later fail-closed intermediate packet captured JHora's exact visible sunrise and award and now confirms the narrow 35/35 Hora profile.
- The tropical-longitude Kranti Ayana profile is the strongest candidate: it passes all 28 recent visible rows and 30/35 overall, and it fits the two published rounded Ayana tables far better than true equatorial declination.
- Do not promote the Ayana candidate yet. Five 1889 rows remain outside the frozen tolerance and require visible JHora tropical longitude or intermediate Kranti evidence.
- No production formula, certification tolerance, ML feature, Auto Suggest rule, or execution path is changed by this diagnostic.

## Required Next Witness

- Nathonnatha: No production change. A JHora intermediate showing its apparent birth time or internal Unnata value is required to explain the visible compatibility residual.
- Hora: Completed: the separate hashed intermediate witness records JHora's case-8 apparent-tip sunrise and Moon Hora award.
- Ayana: The historical tropical positions are captured. The tested Kranti reconstruction is rejected; a visible internal Kranti or separately sourced formula is needed before another candidate is admitted.
