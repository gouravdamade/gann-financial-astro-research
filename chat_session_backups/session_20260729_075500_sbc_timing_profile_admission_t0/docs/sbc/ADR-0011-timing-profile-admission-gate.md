# ADR-0011: Fail-Closed Timing-Profile Admission Gate

Status: accepted for T0 profile admission only

Date: 2026-07-29

## Context

F3 can display the existing signed scalar ledger at fixed angles `0` and `pi`.
It contains no timing phase. ADR-0005 prohibits a directional timing-phase
engine until one complete, versioned profile defines all sectors, boundaries,
margins, asymmetric cases, repeated exact events, retrograde loops, stations,
missing boundaries, unsupported states, directional eligibility thresholds,
and the confidence contract.

No such source-certified profile exists in the repository. Filling the missing
values from intuition, an LLM, or the F3 display would manufacture doctrine.
Leaving the requirement only in prose would also make it too easy for later
code to bypass.

## Decision

1. Add contract `SBC_TIMING_PROFILE_ADMISSION_REPORT_V1`, schema `1`, under
   policy `FAIL_CLOSED_SOURCE_REGISTRY_ADMISSION_V1`.
2. Add a strict candidate contract,
   `SBC_DIRECTIONAL_TIMING_PROFILE_V1`, schema `1`. The application ships no
   candidate and supplies no default profile values.
3. Validate an uploaded candidate in memory only. Reject missing or unknown
   fields, non-finite values, sector gaps or overlaps, ambiguous boundary
   inclusivity, unsafe sectors carrying a direction, incomplete station
   thresholds, absent fallbacks, duplicate confidence terms, and weakened
   locks.
4. Require half-open sectors to form an exact, ordered, gap-free partition of
   the declared phase span. Every sector is explicitly `SAFE` or `UNSAFE`.
   `SAFE` sectors require a positive or negative role; `UNSAFE` sectors require
   role `NONE`.
5. Require one explicit boundary-margin rule, deterministic rules for
   asymmetry, repeated exact events, retrograde loops, stations, missing
   boundaries, and unsupported states, plus activity/coherence/unsafe-share
   thresholds and one normalized weighted geometric-mean confidence contract.
6. Compute a canonical SHA-256 over the candidate JSON. Structural validity is
   insufficient for admission.
7. Compare that hash only with the server-owned
   `status/timing_phase_profile_registry.json`. A candidate is admitted for a
   future isolated research implementation only when its exact hash is frozen,
   source-certified, and linked to non-empty source-audit references in that
   registry.
8. Keep the registry empty until an independently reviewed profile exists.
   Client input cannot write or alter the registry.
9. Report typed `PASS`, `FAIL`, and `UNKNOWN` gates. No loaded candidate and no
   registry entry are `UNKNOWN`, not zero and not a pass.
10. Keep the directional engine absent. Profile admission does not calculate a
    phase, direction, confidence, vote, ML note, Auto Suggest result, trade, or
    order.
11. Keep prospective financial validation separate. Even a hypothetical
    passed trial cannot make the T0 admission checker financially actionable.
12. Keep `execution_allowed=false` in the candidate requirement, registry,
    report, backend, native command, UI, status audit, and tests.

## Consequences

- The next externally supplied profile can be checked reproducibly without
  changing code or accepting it on trust.
- Structural completeness, source certification, engine implementation, and
  prospective financial validation remain four separate claims.
- The UI can explain exactly why timing direction remains unavailable.
- The absence of a timing profile remains visible instead of being silently
  substituted with fixed `0/pi` scalar signs.

## Rejected Alternatives

- Deriving timing sectors from favorable or adverse scalar signs.
- Treating F3 coherence as timing confidence.
- Shipping an illustrative profile that could be mistaken for doctrine.
- Accepting a client-supplied `sourceCertified=true` flag.
- Persisting uploaded candidates automatically.
- Widening the gate until an incomplete profile passes.
- Enabling a directional engine, shadow vote, or trade output in T0.
