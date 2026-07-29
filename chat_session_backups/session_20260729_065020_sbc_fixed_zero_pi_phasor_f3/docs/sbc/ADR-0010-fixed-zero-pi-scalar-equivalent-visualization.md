# ADR-0010: Fixed 0/pi Scalar-Equivalent Visualization

- Status: Accepted
- Date: 2026-07-29
- Capability: `fixed_zero_pi_scalar_phasor_visualization_v1`
- Classification: `SOURCE_PROFILED_EXPERIMENTAL`

## Context

The Phase 5B multidimensional ledger already preserves one canonical signed
scalar value per causal cluster. Phase 5C exposes those values through linked
read-only audit views. The research roadmap permits an optional fixed `0/pi`
phasor view only after scalar parity is proven.

This milestone is not a timing-phase engine. It must not imply physical waves,
resonance, market direction, confidence, or an additional vote.

## Decision

Implement `SBC_FIXED_ZERO_PI_PHASOR_SERIES_V1` as a deterministic projection of
the canonical reconciled Phase 5B ledger:

1. A scored value greater than or equal to zero receives fixed angle `0`.
2. A scored value below zero receives fixed angle `pi`.
3. Magnitude is `abs(signed_guidance_units)`.
4. The real component is the original signed scalar value.
5. The imaginary component is exactly zero.
6. Unknown or missing evidence receives no angle, magnitude, real component, or
   imaginary component. It remains `UNKNOWN_NOT_PLOTTED`.
7. For every interval, the real-component sum must reproduce P2 net guidance.
8. For every interval, the magnitude sum must reproduce P2 true gross
   activation.
9. Cluster identity, source-lineage identity, evidence identity, interval
   identity, actor, and target context remain linked to the source ledger.
10. The known-scored coherence display is `abs(net) / gross`. It is descriptive
    cancellation context only.

The compiler fails closed when source guardrails are weakened, P2 axes are not
reconciled, interval or cluster links differ, cluster identities repeat, scalar
totals differ, unknown evidence is converted to zero, or parity fails.

## Trust Boundary

The desktop and browser send only explicit Chakra boundary requests. The Python
service recomputes Chakra snapshots, P1 atomic intervals, P2 ledgers, and the F3
projection. Browser-computed vectors are never accepted.

The Tauri command and private HTTP route both require the existing read-only
runtime. Companion access uses the same read-only Chakra route family.

## UI Boundary

F3 is one linked `Fixed phasor` audit tab. It shows:

- fixed `0` and `pi` real-axis vectors;
- P2 net versus vector real sum;
- P2 gross activation versus vector magnitude sum;
- the required zero imaginary sum;
- descriptive known-score coherence;
- explicit unplotted unknown evidence;
- typed parity and safety gates.

The tab states that the view is not a physical wave, timing phase, direction,
confidence score, or extra vote.

## Guardrails

The following remain false or zero:

- physical-wave claim;
- timing-phase inclusion;
- timing-sector profile inclusion;
- FX subtraction;
- confidence;
- independent voting weight;
- directional contribution;
- financial validation;
- execution.

The following remain blocked:

- physical-wave interpretation;
- timing-phase output;
- timing-sector direction;
- FX subtraction;
- confidence output;
- market direction;
- Auto Suggest;
- live inference;
- official ML notes;
- shadow-validation voting;
- trade output;
- MT5 execution.

## Consequences

F3 provides a visually inspectable decomposition of the existing scalar ledger
without adding information or authority. It does not unblock T1 directional
timing research. A later timing engine still requires a complete frozen sector,
boundary, margin, loop, station, missing-state, and prospective-validation
profile.
