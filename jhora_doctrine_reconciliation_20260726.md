# JHora Doctrine Reconciliation

Contract: `GANN_JHORA_DOCTRINE_RECONCILIATION_V2`

Status: diagnostic reconciliation; no execution authorization.

Tolerance remains frozen at 0.5 virupa.

## Top-Level Profile Comparison

| Measure | Local pass | Local closer | PyJHora closer | Local MAE | PyJHora MAE |
| --- | --- | --- | --- | --- | --- |
| Kaala | 5/35 | 35 | 0 | 2.763 | 57.031 |
| Chesta | 12/35 | 15 | 20 | 17.919 | 26.397 |
| Drik | 9/35 | 2 | 2 | 7.320 | 7.320 |
| Total | 0/35 | 33 | 2 | 12.626 | 71.742 |

## Visible Kaala Subcomponent Witness

| Measure | Local pass | Local MAE | Local max | Decision |
| --- | --- | --- | --- | --- |
| abda | 35/35 | 0.000 | 0.000 | retain |
| masa | 35/35 | 0.000 | 0.000 | retain |
| vara | 35/35 | 0.000 | 0.000 | retain |
| hora | 33/35 | 3.429 | 60.000 | provisional |
| tribhaga | 35/35 | 0.000 | 0.000 | retain |
| paksha | 35/35 | 0.040 | 0.124 | promote dynamic nature |
| nathonnatha | 11/35 | 1.843 | 4.890 | provisional |
| ayana | 13/35 | 1.973 | 9.010 | provisional |
| yuddha | 35/35 | 0.000 | 0.000 | retain |
| total | 4/35 | 6.350 | 62.909 | provisional |

Paksha now has direct visible support in 35/35 rows. Hora remains 33/35 because only case 8 changes the categorical award; the current fixed-hour algorithm is retained until that sunrise boundary is independently resolved. Nathonnatha, Ayana, and aggregate Kaala remain provisional.

## Chesta Decision

JHora's displayed total equals the sum with Sun/Moon Chesta excluded in 10/10 luminary rows; maximum residual is 0.010 virupa from two-decimal display rounding.

Sun and Moon Chesta is preserved as display evidence but excluded from Shadbala totals to prevent Ayana/Paksha double counting.

Non-luminary Chesta remains mixed across mean-longitude profiles and is not promoted.

## Drik Sensitivity Profiles

| Profile | Pass | MAE | Max | Moon | Mercury | Special scale |
| --- | --- | --- | --- | --- | --- | --- |
| current_dynamic_nature_range_special | 9/35 | 7.320 | 35.385 | current | current | 1.0 |
| current_dynamic_nature_no_range_special | 11/35 | 6.777 | 24.135 | current | current | 0.0 |
| bright_half_moon_current_mercury_no_range_special | 19/35 | 3.290 | 19.402 | bright_half | current | 0.0 |
| bright_half_moon_benefic_mercury_no_range_special | 17/35 | 5.963 | 22.117 | bright_half | benefic | 0.0 |
| bright_half_moon_malefic_mercury_no_range_special | 20/35 | 2.372 | 21.635 | bright_half | malefic | 0.0 |

The bright-half Moon/no-range-special profile is a useful doctrine lead, but the remaining Mercury and special-aspect residuals prevent promotion. Production Drik remains provisional and execution-locked.

## Locked Decisions

- Promote dynamic Paksha classification: classical phase/nature rules and the locked visible JHora table agree in 35/35 rows within the frozen 0.5-virupa tolerance.
- Retain Abda, Masa, Vara, Tribhaga, and Yuddha: each matches all 35 visible JHora rows.
- Keep Hora provisional. It matches 33/35 rows, but the case-8 Moon/Saturn award remains a sunrise-boundary disagreement; do not replace the current algorithm with a temporal-hour guess.
- Keep Nathonnatha, Ayana, aggregate Kaala, non-luminary Chesta, and full Shadbala uncertified until their remaining formula and time-basis residuals are independently reconciled.
- Promote luminary Chesta total exclusion: classical text and locked JHora total arithmetic independently agree that displayed Sun/Moon Chesta must not be added again.
- Retain the current production Drik profile as provisional and execution-ineligible. Named candidate profiles are sensitivity tests, not silent replacements.
