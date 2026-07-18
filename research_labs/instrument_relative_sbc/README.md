# Instrument-Relative SBC Research Layer

This package implements the non-executing foundation from
`Sarvatobhadra_Instrument_Specific_and_Forex_Codex_Spec.pdf`.

It is deliberately separate from `sbc/`:

- `sbc/` remains the timestamp-safe astronomy, Chakra geometry, and Vedha
  guidance engine.
- this package records instrument identity hypotheses, target mappings,
  evidence contributions, latent currency scores, and FX pair differences.
- no market order, Auto Suggest, MT5 execution, or hidden weight is allowed.

## Safety Boundary

- Missing evidence is `None`/`unknown`, never numeric zero.
- Classical and experimental rules cannot share a classical profile.
- Verified rules require a source locator.
- Every signed contribution names its event, target, rule, profile, and source.
- Currency scores are computed once; pairs are pure base-minus-quote views.
- Inversion, identity, and triangle invariants are tested.
- All included profile weights are zero except the explicitly experimental SBC
  identity baseline.
- `execution_allowed` and `promotion_allowed` remain false.

The current milestone covers domain/provenance schemas and the latent currency
plus FX relative engine. It does not yet resolve aksharas automatically,
translate current Chakra snapshots into contributions, or run financial
validation.
