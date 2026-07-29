# JHora Doctrine Reconciliation

Contract: `GANN_JHORA_DOCTRINE_RECONCILIATION_V3`

Status: diagnostic reconciliation; no execution authorization.

Tolerance remains frozen at 0.5 virupa.

## Top-Level Profile Comparison

| Measure | Local pass | Local closer | PyJHora closer | Local MAE | PyJHora MAE |
| --- | --- | --- | --- | --- | --- |
| Sthana | 1/35 | 2 | 33 | 6.296 | 0.966 |
| Kaala | 5/35 | 35 | 0 | 2.763 | 57.031 |
| Dig | 19/35 | 11 | 24 | 1.142 | 1.141 |
| Chesta | 12/35 | 15 | 20 | 17.919 | 26.397 |
| Naisargika | 35/35 | 0 | 0 | 0.004 | 0.004 |
| Drik | 9/35 | 2 | 2 | 7.320 | 7.320 |
| Total | 3/35 | 33 | 2 | 11.829 | 71.742 |

## Component Admission Boundary

Production source-profile values are compared directly with the locked JHora witness. A component is witness-aligned only when all 35 locked rows pass at the frozen 0.5-virupa tolerance. Alignment does not by itself establish source certification, financial validity, or execution permission.

Witness-aligned top-level components: naisargika.
Witness-aligned Kaala subcomponents: abda, hora, masa, paksha, tribhaga, vara, yuddha.
Full Shadbala, Drik, source certification, financial validation, and execution remain blocked.

## Visible Kaala Subcomponent Witness

| Measure | Local pass | Local MAE | Local max | Decision |
| --- | --- | --- | --- | --- |
| abda | 35/35 | 0.000 | 0.000 | retain |
| masa | 35/35 | 0.000 | 0.000 | retain |
| vara | 35/35 | 0.000 | 0.000 | retain |
| hora | 35/35 | 0.000 | 0.000 | provisional |
| tribhaga | 35/35 | 0.000 | 0.000 | retain |
| paksha | 35/35 | 0.003 | 0.004 | promote dynamic nature |
| nathonnatha | 11/35 | 1.485 | 4.450 | provisional |
| ayana | 13/35 | 1.973 | 9.010 | provisional |
| yuddha | 35/35 | 0.000 | 0.000 | retain |
| total | 5/35 | 2.763 | 8.879 | provisional |

Paksha and Hora now have direct visible support in 35/35 rows. The exact case-8 Hora packet binds JHora's visible LMT sunrise, Moon lord, and seven awards. Nathonnatha, Ayana, and aggregate Kaala remain provisional.

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

- Recognize Naisargika as independently witness-aligned in 35/35 top-level rows. This is component evidence only, not full Shadbala source certification or financial validation.
- Keep production Sthana provisional. The BPHS-labeled source profile passes only 1/35 locked JHora rows; the separately named PyJHora-compatible profile must remain diagnostic and must not be substituted into the production total.
- Promote dynamic Paksha classification: classical phase/nature rules and the locked visible JHora table agree in 35/35 rows within the frozen 0.5-virupa tolerance.
- Retain Abda, Masa, Vara, Tribhaga, and Yuddha: each matches all 35 visible JHora rows.
- Recognize Hora as independently witness-aligned in 35/35 rows. The exact case-8 packet binds the visible LMT sunrise, Moon Hora lord, and all seven awards. This is component evidence only, not aggregate Kaala or full Shadbala certification.
- Keep Sthana, Dig, Nathonnatha, Ayana, aggregate Kaala, non-luminary Chesta, Drik, and full Shadbala uncertified until their remaining formula and time-basis residuals are independently reconciled.
- Promote luminary Chesta total exclusion: classical text and locked JHora total arithmetic independently agree that displayed Sun/Moon Chesta must not be added again.
- Retain the current production Drik profile as provisional and execution-ineligible. Named candidate profiles are sensitivity tests, not silent replacements.
