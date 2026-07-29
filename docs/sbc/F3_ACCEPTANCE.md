# F3 Acceptance: Fixed 0/pi Scalar-Equivalent Visualization

F3 is accepted in source only when every item below passes.

## Deterministic Contract

- Contract is `SBC_FIXED_ZERO_PI_PHASOR_SERIES_V1`.
- Policy is `FIXED_ZERO_PI_SCALAR_PARITY_VISUALIZATION_ONLY_V1`.
- Input is the canonical `SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1`.
- Input classification remains `SOURCE_PROFILED_EXPERIMENTAL`.
- Each scored causal cluster appears exactly once in its source interval.
- Non-negative scalar values use fixed angle `0`.
- Negative scalar values use fixed angle `pi`.
- No other angle is possible.

## Exact Parity

- Vector real sum equals P2 net guidance for every interval.
- Vector magnitude sum equals P2 true gross activation for every interval.
- Vector imaginary sum is zero for every interval.
- Scored, unknown, missing, and total counts match P2.
- Unknown evidence keeps null magnitude and is not plotted as zero.
- A mismatch fails compilation.

## Lineage

- Interval ID and interval-ledger ID remain linked.
- Cluster ID and source-lineage ID remain linked.
- Contribution or missing-evidence identity remains linked.
- Actor and target context remain descriptive source context.
- Identities and output ordering are deterministic.

## Guardrails

- Derivation role is `VISUALIZATION_ONLY`.
- Evidence-bearing is false.
- Voting weight is zero.
- Directional contribution is zero.
- Physical-wave claim is false.
- Timing phase and timing-sector profile are absent.
- FX subtraction, confidence, market direction, Auto Suggest, live inference,
  official ML notes, shadow-validation voting, trade output, and MT5 execution
  remain blocked.
- Financial validation remains `UNKNOWN`.

## Integration

- Browser input contains only explicit timestamped Chakra boundary requests.
- Python recomputes Chakra, P1, P2, and F3.
- Private HTTP and native Tauri paths enforce the read-only runtime.
- The linked audit workspace exposes a separate `Fixed phasor` tab.
- The tab displays parity, unknown evidence, and safety gates.
- The tab clearly says it is not a physical wave, timing phase, direction,
  confidence score, or extra vote.

## Verification

- Focused F3 tests pass.
- Chakra service tests pass.
- Chakra workspace UI tests pass.
- Full Python tests pass.
- Full frontend tests, lint, and production build pass.
- Native Rust check passes.
- Browser acceptance confirms readable desktop layout, linked interval
  selection, no overlap, no console error, and no market-direction language.

Packaging, promotion, financial validation, and execution are not part of F3.
