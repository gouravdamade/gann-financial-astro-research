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

The current milestone covers domain/provenance schemas, the latent currency
plus FX relative engine, and an immutable Chakra snapshot-to-identity connector.
The connector only exact-matches snapshot targets against time-valid,
human-accepted identity mappings. It emits immutable **unscored** evidence and
never an `InfluenceContribution`: source-profile polarity, numeric magnitude,
Auto Suggest, ML training, MT5 input, promotion, and execution all remain
blocked. It does not resolve or transliterate aksharas automatically and has not
passed financial validation.

This ordering is deliberate:

1. immutable timestamp-safe snapshot;
2. time-valid human-accepted identity;
3. exact target match with provenance;
4. later source-certified rule profile;
5. only then a separately registered contribution and walk-forward experiment.

Unknown identity or doctrine remains unknown rather than becoming neutral.
