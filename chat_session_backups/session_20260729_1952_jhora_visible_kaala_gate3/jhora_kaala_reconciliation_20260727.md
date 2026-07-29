# JHora Kaala Bala Reconciliation

Contract: `GANN_JHORA_KAALA_WITNESS_COMPARATOR_V1`

Status: locked visible-witness diagnostic; not execution-certified.

The numeric certification tolerance remains frozen at 0.5 virupa. The separate 0.06-virupa display-sum allowance only accommodates adding ten values rounded by JHora to two decimals.

## Per-Component Results

| Measure | Local pass | PyJHora pass | Local MAE | PyJHora MAE | Local closer | PyJHora closer |
| --- | --- | --- | --- | --- | --- | --- |
| total | 5/35 | 0/35 | 2.763 | 57.031 | 35 | 0 |
| nathonnatha | 11/35 | 5/35 | 1.485 | 19.138 | 30 | 0 |
| paksha | 35/35 | 6/35 | 0.003 | 46.693 | 35 | 0 |
| tribhaga | 35/35 | 31/35 | 0.000 | 6.857 | 4 | 0 |
| abda | 35/35 | 35/35 | 0.000 | 0.000 | 0 | 0 |
| masa | 35/35 | 35/35 | 0.000 | 0.000 | 0 | 0 |
| vara | 35/35 | 35/35 | 0.000 | 0.000 | 0 | 0 |
| hora | 35/35 | 25/35 | 0.000 | 17.143 | 10 | 0 |
| ayana | 13/35 | 26/35 | 1.973 | 2.591 | 8 | 27 |
| yuddha | 35/35 | 31/35 | 0.000 | 0.336 | 4 | 0 |

## Categorical Lord Witness

### case_103_event_start

| Profile | Abda | Masa | Vara | Hora |
| --- | --- | --- | --- | --- |
| JHora | MOON | MARS | JUPITER | JUPITER |
| Local | MOON | MARS | JUPITER | JUPITER |
| PyJHora | MOON | MARS | JUPITER | MOON |

### case_127_sr_touch_start

| Profile | Abda | Masa | Vara | Hora |
| --- | --- | --- | --- | --- |
| JHora | MOON | MARS | MERCURY | MERCURY |
| Local | MOON | MARS | MERCURY | MERCURY |
| PyJHora | MOON | MARS | MERCURY | VENUS |

### case_43_event_start

| Profile | Abda | Masa | Vara | Hora |
| --- | --- | --- | --- | --- |
| JHora | MOON | VENUS | VENUS | VENUS |
| Local | MOON | VENUS | VENUS | VENUS |
| PyJHora | MOON | VENUS | VENUS | MOON |

### case_8_event_start

| Profile | Abda | Masa | Vara | Hora |
| --- | --- | --- | --- | --- |
| JHora | MOON | MERCURY | VENUS | MOON |
| Local | MOON | MERCURY | VENUS | MOON |
| PyJHora | MOON | MERCURY | VENUS | MARS |

### gann_reference_tokyo

| Profile | Abda | Masa | Vara | Hora |
| --- | --- | --- | --- | --- |
| JHora | SUN | MARS | SUN | MOON |
| Local | SUN | MARS | SUN | MOON |
| PyJHora | SUN | MARS | SUN | VENUS |

## Evidence Conclusions

- Promote dynamic Paksha classification: the local profile passes 35/35 visible rows with 0.003 virupa MAE and 0.004 virupa maximum error.
- Retain Abda, Masa, Vara, Tribhaga, and Yuddha: each local subcomponent passes all 35 visible rows.
- The exact-time visible Hora award matrix matches the local profile for 35/35 rows, and the categorical Hora lord matches for every fixture. The separate fail-closed intermediate gate determines whether the visible case-8 apparent-tip sunrise and award provenance packet is complete.
- Do not promote Nathonnatha, Ayana, or aggregate Kaala: they pass 11/35, 13/35, and 5/35 rows respectively.
- The frozen 0.5-virupa certification tolerance is unchanged; the 0.06 display-sum allowance only checks arithmetic over JHora values rounded to two decimal places.

## Decision Boundary

- No production formula is changed merely because one profile is closer.
- A categorical lord change requires a consistent visible witness and an independently supported doctrine algorithm.
- Ayana and continuous components remain separate from discrete 15/30/45/60-virupa awards.
