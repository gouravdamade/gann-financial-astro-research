# Instrument-Relative SBC and Forex Foundation

Date: 2026-07-18

This milestone implements an isolated research layer derived from
`Sarvatobhadra_Instrument_Specific_and_Forex_Codex_Spec.pdf`. It does not
modify the production SBC engine, Auto Suggest, live inference, or MT5 order
execution.

## Implemented

- Versioned instrument identity and time-valid naming records.
- Human-reviewed akshara, rashi, and nakshatra mappings with provenance.
- Source-tiered rules that reject experimental evidence from classical
  profiles.
- Signed influence contributions with explicit event, target, rule, profile,
  source, and uncertainty records.
- Latent currency scores computed before pair construction.
- FX pair score defined as base currency score minus quote currency score.
- Separate common-mode and joint-activation diagnostics.
- Unknown evidence preserved as unknown rather than converted to zero.
- Identity, inversion, and triangular-consistency checks.
- Execution and promotion locks set to false.

## Deliberately Pending

- Automatic akshara resolution.
- Production mapping from live SBC Chakra snapshots into contribution rows.
- Certified economic identity charts for currencies, central banks, and
  countries.
- Walk-forward financial validation and calibration.
- Promotion criteria for guidance or execution.

## Promotion Gate

This layer may produce research explanations only. Promotion requires:

1. source-certified rule records;
2. accepted target mappings with human review;
3. timestamp-safe out-of-sample validation;
4. invariant-clean pair calculations;
5. an explicit versioned promotion decision.

Until all five conditions are met, no score from this package may influence an
order, position size, stop, target, or Auto Suggest marker.
