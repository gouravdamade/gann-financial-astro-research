# T0 Timing-Profile Admission Acceptance

Date: 2026-07-29

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

## Required Contract

- Admission report: `SBC_TIMING_PROFILE_ADMISSION_REPORT_V1`
- Candidate profile: `SBC_DIRECTIONAL_TIMING_PROFILE_V1`
- Registry: `SBC_TIMING_PROFILE_REGISTRY_V1`
- Admission policy: `FAIL_CLOSED_SOURCE_REGISTRY_ADMISSION_V1`
- Schema version: `1`

## Acceptance Checks

1. With no candidate loaded, every candidate-dependent gate is `UNKNOWN`.
   Direction, confidence, financial use, and execution remain unavailable.
2. Candidate JSON is validated in memory and is never persisted by T0.
3. Unknown candidate fields fail closed.
4. The declared phase span is finite and non-empty.
5. At least two half-open sectors exactly cover the span without a gap or
   overlap.
6. Every sector explicitly declares `SAFE` or `UNSAFE`; unsafe sectors carry
   no direction.
7. Boundary margin and exact-boundary behavior are explicit and leave a
   non-empty interior in every sector.
8. Asymmetry, repeated exact events, retrograde loops, stations, missing
   boundaries, and unsupported states each have a deterministic rule and
   fail-closed fallback.
9. Station thresholds are non-negative and declared by body.
10. Activity, coherence, unsafe-activation share, and coverage thresholds are
    finite and bounded.
11. The confidence contract is exactly
    `NORMALIZED_WEIGHTED_GEOMETRIC_MEAN_V1`, with positive unique terms,
    explicit lineage handling, unique mandatory gates, and minimum coverage.
12. Candidate guardrails prohibit Auto Suggest, live inference, official ML
    notes, shadow votes, trade output, and execution.
13. Structural validity alone does not admit a profile. Its canonical SHA-256
    must match a frozen, source-certified entry in the server-owned registry
    with source-audit references.
14. The repository registry is valid and execution-locked. It contains no
    profile until external evidence is accepted.
15. Prospective financial validation is a separate typed gate.
16. T0 never claims that a directional timing engine exists.
17. T0 never emits market direction, confidence, an independent vote, an
    official ML note, a trade result, or broker execution.

## UI Acceptance

- `Timing gate` is available without compiling a linked audit.
- The initial view says no profile is loaded and shows the empty registry.
- Candidate JSON may be loaded for an in-memory check and cleared.
- Candidate filename and canonical SHA-256 are visible when available.
- Every gate displays `PASS`, `FAIL`, or `UNKNOWN` with its reason.
- The UI says directional output is unavailable, financial use is blocked,
  and execution is locked.
- No layout overlap or error-level browser log appears at the desktop
  acceptance viewport.

## Release Boundary

T0 is source-only. It does not rebuild Windows or Android packages, register a
profile, implement T1, modify inference, or change execution permissions.
