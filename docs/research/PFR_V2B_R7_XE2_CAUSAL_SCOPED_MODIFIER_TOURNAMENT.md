# PFR-V2B-R7-XE2 Causal-Scoped Modifier Tournament

## Causal contract

Each source event forms one causal group. Its real identity, raw speed, and
motion phase are audit inputs. One synthetic sign test value is attached only
for test arithmetic. The group is not permitted to cast more than one signed
vote, and a modifier cannot become an independent vote.

`resolve_modifier_scope()` is fail closed:

- exact matching `CAUSAL_EVENT_ID` -> `BOUND`;
- absent target -> `REJECTED_UNSCOPED`;
- mismatched target -> `REJECTED_UNSCOPED`;
- `globalDefaultApplied` is always `false`.

## Modifier arithmetic

For each event with synthetic test value `x` and speed normalization `z`:

```text
M0: x
M1: x * clamp(exp(0.8 * z), 0.5, 1.5)
M2: x, with z displayed only in the separate channel
M3: x * (1 + 0.5 * z), fail closed if the factor is non-positive
M4: x only when verified motion phase is DIRECT; otherwise target-only Unknown
```

M1 is positive bounded arithmetic and cannot flip a synthetic sign. M3 is an
explicit engineering test and has no source-doctrine, market, or validation
claim. Unknown speed or motion data affects only its own causal event; it does
not erase or modify unrelated events.

## Aggregate semantics

The aggregate is named `syntheticStateVector`, not a market oscillator. Its
fields are explicitly labelled `syntheticRaw` and `syntheticNormalized`. The
only allowed aggregate states are `SYNTHETIC_SIGN_TEST_ONLY` and
`UNKNOWN_NO_SYNTHETIC_SIGN_TEST`.
