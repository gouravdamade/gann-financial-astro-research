# Multi Oscillator MO-P3A Founder Acceptance

Status: `FOUNDER ACCEPTED`

Acceptance date: `2026-08-27`

## Frozen Baseline

```text
MO-P3A = FOUNDER ACCEPTED - UNSIGNED STEP-WAVE V1
MO-P3A-F1 = FOUNDER ACCEPTED
```

- Founder candidate: `0.10.61-pfr-v2b-mo-p3a-f1`
- Accepted functional source: `a2fead3847b69d8a873a68da30184822fc553430`
- Packaging documentation baseline: `7fa67ce253eabf14c3b4010117af8d20c03f1c2a`

The candidate is frozen as the accepted unsigned step-wave baseline. This
acceptance does not authorize a repair or cleanup branch unless a later actual
regression is observed.

## Founder Physical Evidence

The founder supplied local physical-inspection screenshots on 2026-08-27:

- `Screenshot 2026-08-27 124521.png`
- `Screenshot 2026-08-27 124557.png`
- `Screenshot 2026-08-27 124620.png`
- `Screenshot 2026-08-27 124812.png`

They remain local founder evidence and are intentionally not committed to Git.
The founder verified both independent USD and JPY step waves, exact marker
selection in dense areas, shared crosshair, shared raw-count scaling, Moon
filter removal and restore behavior, and coverage hatching that leaves the
observed count intact. The scale visibly changes from `0-16` to `0-12` after
Moon is disabled. The founder explicitly judged the step-wave representation
more useful than raw count bars and the dense regions readable.

`KNOWN_ZERO_PHYSICAL_CHECK = NOT_OBSERVED_IN_FOUNDER_RANGE` because the
inspected range contained no distinct known-zero interval. That is not a
blocker; source tests cover the zero-baseline behavior.

## Accepted Meaning and Limits

The accepted contracts remain:

- `stepWaveContract = MO_UNSIGNED_ACTIVITY_STEP_WAVE_V1`
- `activityContract = MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`
- `semanticUnit = ACTIVE_EVENT_COUNT`
- `polarityAssigned = false`
- `magnitudeConfigured = false`
- `normalizationUsed = false`
- `smoothingUsed = false`
- `pairResultantComputed = false`
- `executionAllowed = false`

This is acceptance of an unsigned time-domain product only. It is not a
directional, polarity, predictive, financial, magnitude or USDJPY-resultant
validation. It does not authorize price/outcome reads, SBC/CGVO/BPHS fusion,
LLM or ML sign inference, Auto Suggest, MT5 signals, order placement or
execution.

## Next Boundary

The next permitted work is the documentation-only MO-R2 polarity admission
readiness audit. It may determine whether an identity-bound sign path exists,
but it must not create a signed wave, a pair resultant or any runtime change.
