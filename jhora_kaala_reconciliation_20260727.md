# JHora Kaala Bala Reconciliation

Contract: `GANN_JHORA_KAALA_WITNESS_COMPARATOR_V1`

Status: locked visible-witness diagnostic; not execution-certified.

The numeric certification tolerance remains frozen at 0.5 virupa. The separate 0.06-virupa display-sum allowance only accommodates adding ten values rounded by JHora to two decimals.

## Per-Component Results

| Measure | Local pass | PyJHora pass | Local MAE | PyJHora MAE | Local closer | PyJHora closer |
| --- | --- | --- | --- | --- | --- | --- |
| total | 4/35 | 0/35 | 6.350 | 60.377 | 35 | 0 |
| nathonnatha | 11/35 | 5/35 | 1.843 | 19.332 | 30 | 0 |
| paksha | 35/35 | 6/35 | 0.040 | 46.681 | 35 | 0 |
| tribhaga | 35/35 | 31/35 | 0.000 | 6.857 | 4 | 0 |
| abda | 35/35 | 35/35 | 0.000 | 0.000 | 0 | 0 |
| masa | 35/35 | 35/35 | 0.000 | 0.000 | 0 | 0 |
| vara | 35/35 | 35/35 | 0.000 | 0.000 | 0 | 0 |
| hora | 33/35 | 25/35 | 3.429 | 17.143 | 9 | 1 |
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
| JHora | MOON | MERCURY | VENUS | SATURN |
| Local | MOON | MERCURY | VENUS | MOON |
| PyJHora | MOON | MERCURY | VENUS | MARS |

### gann_reference_tokyo

| Profile | Abda | Masa | Vara | Hora |
| --- | --- | --- | --- | --- |
| JHora | SUN | MARS | SUN | MOON |
| Local | SUN | MARS | SUN | MOON |
| PyJHora | SUN | MARS | SUN | VENUS |

## Evidence Conclusions

- Promote dynamic Paksha classification: the local profile passes 35/35 visible rows with 0.040 virupa MAE and 0.124 virupa maximum error.
- Retain Abda, Masa, Vara, Tribhaga, and Yuddha: each local subcomponent passes all 35 visible rows.
- Retain Hora as provisional: it passes 33/35 rows, with the case-8 sunrise-boundary award unresolved.
- Do not promote Nathonnatha, Ayana, or aggregate Kaala: they pass 11/35, 13/35, and 4/35 rows respectively.
- The frozen 0.5-virupa certification tolerance is unchanged; the 0.06 display-sum allowance only checks arithmetic over JHora values rounded to two decimal places.

## Decision Boundary

- No production formula is changed merely because one profile is closer.
- A categorical lord change requires a consistent visible witness and an independently supported doctrine algorithm.
- Ayana and continuous components remain separate from discrete 15/30/45/60-virupa awards.
