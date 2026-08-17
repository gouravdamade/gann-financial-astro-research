# PFR-V2B-R7-XE1 Evidence Role and Modifier Ablation

The first XE1 profile is `XE1_EVIDENCE_ROLE_MODIFIER_ABLATION_V1`. It is a
synthetic demonstration profile, not a source profile or financial model.

| Feature | Role | Purpose |
| --- | --- | --- |
| `synthetic_positive_direct` | SIGN | Direct positive test contribution. |
| `synthetic_positive_derived_axis` | SIGN / derived child | Demonstrates that a second view of the same cause cannot add another vote. |
| `synthetic_negative_direct` | SIGN | Direct negative test contribution. |
| `synthetic_modifier_z` | MODIFIER | Tests bounded positive multiplier behavior. |
| `synthetic_gate_inactive` | GATE | Displays a three-state gate input without asserting direction. |
| `synthetic_ambiguous_direction` | SIGN / ambiguous | Proves ambiguous cause identity is withheld. |
| `synthetic_unknown_context` | UNCERTAINTY | Preserves unknown evidence visibly. |

The app offers base, bounded-exp multiplier, separate-channel, and interaction
comparison rows. The comparison is not parameter fitting, optimization,
smoothing, curve fitting, or a price forecast.

The current primary lab uses no timing kernel. Timing and collective plugins are
reserved explicit extension points and are inactive in XE1.
