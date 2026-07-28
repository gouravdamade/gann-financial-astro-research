# ADR-0005: Multidimensional SBC and Phase Research Boundary

Status: accepted for P0 architecture only

Date: 2026-07-28

## Context

The revised private *SBC Phase Engine Review and Visualisation Architecture*
corrects several weaknesses in an earlier proposal. It also overlaps with
working repository components: timestamp-safe SBC facts, source-profiled grid
and letter layers, Vedha evidence, the Chakra Lab, and an isolated FX arithmetic
lab.

Building the proposal as a parallel stack would duplicate doctrine, create
incompatible score meanings, and make validation harder. Treating the proposal
as classical authority would also be incorrect: it is a software and research
specification.

## Decision

1. Reuse the existing `sbc` package, Chakra Lab, source registry, and
   instrument-relative FX lab. Do not create a second ephemeris, grid, Vedha,
   or currency identity implementation.
2. Implement the architecture as separate milestones:
   - P0: gap audit and frozen boundaries;
   - P1: timestamp-safe SBC atomic intervals;
   - P2: multidimensional ledger and gross/net aggregation;
   - P3: linked audit visualization;
   - F3: optional fixed `0/pi` scalar-equivalent visualization;
   - T1 and later: isolated timing-phase research only after a complete frozen
     timing profile.
3. Keep favorable and adverse evidence separate and derive net, activation,
   cancellation, and coverage from explicit contribution rows.
4. Preserve the existing FX differential and signed common mode. In a future
   version, rename the current absolute-net `joint_activation` meaning to joint
   net strength and add true gross activation from underlying absolute
   contribution units. No silent schema reinterpretation is permitted.
5. Use the exact residual contract corrections P0-R1 through P0-R8 in
   `SBC_PHASE_P0_GAP_AUDIT_20260728.md`.
6. Label every new output `SOURCE_PROFILED_EXPERIMENTAL`.
7. Do not call the fixed phasor view a physical wave, resonance, or independent
   signal. It must reproduce the scalar ledger and carry voting weight `0.0`.
8. Do not implement directional timing vectors until a versioned profile
   defines all sectors, boundaries, margins, loops, stations, and unsupported
   states.
9. Require typed `PASS`, `FAIL`, and `UNKNOWN` gates. Missing evidence is not a
   pass and unknown magnitude is not zero.
10. Keep Auto Suggest, live inference, official ML notes, shadow validation,
    broker execution, and order generation disconnected from every capability
    introduced by this architecture.

## Consequences

- The first code milestone is smaller and testable: interval construction
  around existing facts rather than an all-at-once engine.
- Existing doctrine and source hashes remain authoritative.
- Gross activity, cancellation, unknown coverage, and FX common mode remain
  auditable instead of being hidden inside one number.
- The proposed visual language may be explored without multiplying evidence
  votes.
- Timing-phase claims remain visibly incomplete rather than being filled by an
  LLM or an arbitrary threshold.
- Financial usefulness still requires an immutable prospective protocol and
  untouched future observations.

## Rejected Alternatives

- Rebuilding SBC from the private architecture PDF.
- Treating project-specification prose as Jyotisha doctrine.
- Calling `abs(net)` gross activation.
- Converting unknown evidence to zero.
- Using one dense dashboard as the primary audit surface.
- Allowing phase or confidence output into current trading logic before
  source and prospective validation.
