# PFR-V2B-R7-XE2 Architecture

## Purpose

XE2 is a bounded, read-only causal-scoped modifier tournament. It is not a
market model, classical doctrine profile, oscillator promotion, or execution
feature. It extends the accepted XE1 research surface without changing XE1.

The design separates three evidence classes:

| Input | Status in XE2 | Meaning |
| --- | --- | --- |
| Transit-to-natal event identity | Real, hash-linked | Verified astronomical identity only. Aspect geometry never supplies a direction. |
| Moon speed at exactness | Real, raw `deg/day` | An unsigned per-cause modifier input. |
| Synthetic sign test | Synthetic test only | Exercises causal scoping; it is not reviewed evidence or a market sign. |

No reviewed USD/JPY founder-packet polarity exists yet. XE2 therefore exposes
`BLOCKED_NO_REAL_SIGNED_EVIDENCE` instead of manufacturing a prediction.

## Scope

The profile is `XE2_CAUSAL_SCOPED_SPEED_MODIFIER_TOURNAMENT_V1`. Every modifier
must bind to one `CAUSAL_EVENT_ID`; an absent or mismatched target is
`REJECTED_UNSCOPED`. There is no global modifier default and no modifier
stacking.

The raw Moon-speed normalizer is `MOON_RELATIVE_MEAN_SPEED_V1`:

```text
zSpeed = (rawSpeedDegPerDay - 13.176358) / 13.176358
```

The reference is an explicit astronomical mean-motion reference. It is not
derived from price, outcomes, polarity, or a fitted financial parameter.

## Tournament

| Arm | Contract | Scope |
| --- | --- | --- |
| M0 | `XE2_M0_BASE_SYNTHETIC_SIGN_TEST_V1` | Synthetic test sign only. |
| M1 | `XE2_M1_SCOPED_POSITIVE_SPEED_MULTIPLIER_V1` | Per-cause bounded positive speed multiplier. |
| M2 | `XE2_M2_SPEED_SEPARATE_CHANNEL_V1` | Preserves the sign test channel and displays speed separately. |
| M3 | `XE2_M3_SPEED_INTERACTION_V1` | Per-cause engineering interaction test. |
| M4 | `XE2_M4_MOTION_CONTEXT_GATE_V1` | Per-cause direct-motion context gate; it creates no sign. |

The display labels all aggregate values as synthetic test values. They are not
supportive/adverse market calls and no tournament arm is selected as a winner.

## Locks

```text
datasetStatus=TOUCHED_DEV
marketOutcomeRead=false
liveMt5Read=false
priceDataRead=false
sbcRead=false
fieldsPath=false
autoSuggestPath=false
mlPath=false
mt5Path=false
executionAllowed=false
```

XE2 is independent of Mode 1, Trailokya, Argha, Fields, existing SBC profiles,
and the live trading path.
