# JHora Doctrine Reconciliation

Contract: `GANN_JHORA_DOCTRINE_RECONCILIATION_V1`

Status: diagnostic reconciliation; no execution authorization.

Tolerance remains frozen at 0.5 virupa.

## Top-Level Profile Comparison

| Measure | Local pass | Local closer | PyJHora closer | Local MAE | PyJHora MAE |
| --- | --- | --- | --- | --- | --- |
| Kaala | 4/35 | 35 | 0 | 7.983 | 57.031 |
| Chesta | 12/35 | 16 | 19 | 14.732 | 26.397 |
| Drik | 9/35 | 2 | 2 | 7.320 | 7.320 |
| Total | 0/35 | 33 | 2 | 17.416 | 71.742 |

The local Kaala source profile is closer than PyJHora for every locked row, although only exact subcomponent evidence can certify it.

## Kaala Categorical Leads

| Sample | Planet | JHora-local | Nearest award | Remainder |
| --- | --- | --- | --- | --- |
| case_127_sr_touch_start | MOON | +90.678 | 90 | 0.678 |
| case_127_sr_touch_start | MERCURY | +44.919 | 45 | 0.081 |

These are leads, not inferred values. They require a visible JHora Kaala subcomponent table before any calendar-lord rule changes.

## Chesta Decision

Moon display values match half the local doubled-Paksha value in 5/5 fixtures at frozen tolerance.

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

- Promote luminary Chesta total exclusion: classical text and locked JHora totals independently agree that displayed Sun/Moon Chesta must not be added again.
- Retain the current production Drik profile as provisional and execution-ineligible. Named candidate profiles are sensitivity tests, not silent replacements.
- Capture a visible JHora Kaala subcomponent table before changing Abda/Masa/Hora or other categorical lord awards.
