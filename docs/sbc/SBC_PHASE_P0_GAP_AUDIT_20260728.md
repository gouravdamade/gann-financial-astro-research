# SBC and Phase Research P0 Gap Audit

Date: 2026-07-28

Status: accepted architecture audit; no scoring, inference, or execution change

## Purpose

This audit reconciles the revised *SBC Phase Engine Review and Visualisation
Architecture* with the implementation that already exists in this repository.
It is the P0 checkpoint before any new multidimensional SBC interval engine or
phase-interference research code is written.

The revised document is a project specification, not an independent Jyotisha
source. It may define software contracts and research gates, but it cannot
certify doctrine, financial usefulness, or physical causality.

## Source Control

| Item | Role | SHA-256 |
| --- | --- | --- |
| `Priority_Experimental_Engines_SBC_Phase_Interference_Codex_Guide-1.pdf` | Original private project proposal | `BE3DEC3C7CD0A7A49D0688D23732D2345AAFA7313DBDD71B38959D5653681847` |
| `Revised_SBC_Phase_Engine_Review_and_Visualisation_Architecture.pdf` | Revised private project specification | `6982705193E1501C30FFBB93CED2990378498574CB137AFF946640A114EB7A88` |
| `output/pdf/Priority_Experimental_Engines_Honest_Review.pdf` | Independent repository-state review | `4A1A58B1A914397B5E56139F28DA3BD4F9A14C9779046707D6A72C6B4D73B279` |

The two private proposal PDFs stay outside Git. Their hashes identify the exact
documents reviewed.

## Current Repository Inventory

| Capability | Current state | Existing evidence | P0 decision |
| --- | --- | --- | --- |
| Raman sidereal astronomy, Panchanga, and timestamp-safe SBC facts | Implemented and reusable | `sbc/`, `docs/sbc/REPOSITORY_AUDIT.md` | Reuse; do not fork |
| Source-profiled 81-cell grid and page-certified letter layers | Implemented and reusable | `sbc/grid.py`, `docs/sbc/ADR-0002-rotation-normalized-partial-grid.md`, `docs/sbc/ADR-0003-page-certified-letter-layers.md` | Reuse with explicit profile hashes |
| Source-profiled Vedha actor resolution and evidence ledger | Implemented and reusable | `sbc/vedha.py`, `docs/sbc/ADR-0004-source-profiled-vedha-guidance.md` | Reuse favorable, adverse, net, unknown-count, and coverage evidence |
| Chakra Lab snapshot and board UI | Implemented and reusable | `sbc/chakra_lab.py`, `gann-astro-desk/src/views/ChakraLabWorkspace.tsx` | Extend later through linked views, not a second Chakra screen |
| Instrument-relative FX arithmetic | Partial research foundation | `research_labs/instrument_relative_sbc/` | Preserve base-minus-quote and signed common mode; correct activation semantics before reuse |
| SBC atomic state intervals | Absent | No interval contract or boundary compiler exists | First implementation milestone after P0 |
| Complete multidimensional SBC time series | Absent as one engine | Current snapshots expose several ingredients but no frozen interval-aligned schema | Build from existing facts only after P1 contracts pass |
| Fixed `0/pi` phasor visualization | Absent | No research contract exists | May follow scalar parity tests; non-voting only |
| Directional timing-phase engine | Absent | No certified timing profile, sector map, or prospective trial exists | Keep isolated and blocked |
| External Shadbala/Drik weights | Source certification incomplete | `status/capability_status.json` | Cannot weight SBC confidence or direction |
| Prospective financial validation | Not registered for this engine | `status/research_trials.json` | No financial claim or execution use |

## Corrected Architecture Decisions

1. The multidimensional SBC engine is built first from existing source-profiled
   facts and Vedha evidence.
2. Every state change is represented by a half-open atomic interval
   `[startUtc, endUtc)`, one evidence cutoff, and immutable profile hashes.
3. Unknown contribution count and unknown contribution magnitude are different
   fields. Unknown magnitude remains null rather than being treated as zero.
4. Favorable and adverse magnitudes remain separate. Net evidence is derived
   from them and never replaces them.
5. For a currency or instrument side `X`, future gross activation is based on
   the sum of absolute underlying contribution units, `S_A_X`. It is not
   `abs(net_X)`.
6. For an FX pair:
   - differential remains `Z_base - Z_quote`;
   - signed common mode remains `(Z_base + Z_quote) / 2`;
   - joint net strength is the mean magnitude of the two side nets;
   - true gross activation is `(S_A_base + S_A_quote) / 2`.
7. Fixed `0/pi` phasors are allowed only after proving scalar parity with the
   signed ledger. They remain a visual decomposition of the same evidence and
   cannot become an extra vote.
8. Directional timing-phase vectors are ineligible outside a frozen safe
   sector. Unsafe evidence remains visible and auditable.
9. Every derived artifact is labeled `SOURCE_PROFILED_EXPERIMENTAL` until its
   source profile and independent witness gates pass.
10. All phase, confidence, and financial outputs retain coefficient `0.0` in
    Auto Suggest, live inference, official ML notes, validation votes, and
    execution.

## Remaining Contract Corrections

These eight decisions must be frozen before their dependent milestone can
claim completion.

### P0-R1: Mixed safe and unsafe timing evidence

An aggregate must expose:

- `Z_safe`: signed contribution from direction-eligible sectors;
- `Z_unsafe`: signed contribution from unsafe or unknown sectors;
- `safeActivation`;
- `unsafeActivation`;
- `unsafeActivationShare`;
- `aggregateDirectionalEligible`.

The eligibility threshold must be versioned in a profile. Unsafe evidence may
not disappear from the denominator or be silently rotated into a safe sector.

### P0-R2: Scale-aware cancellation

Near-zero net evidence has two distinct meanings:

- low activity: gross activation is at or below a frozen activity floor;
- interference or cancellation: activation is above that floor while
  coherence `abs(Z) / S_A` is at or below a frozen coherence floor.

The two states must not share one label.

### P0-R3: Complete timing-phase profile

Before directional timing code exists, its profile must define phase span,
sector boundaries, boundary inclusivity, direction-safe sectors, margin,
asymmetry, repeated exact events, retrograde loops, station handling, missing
boundaries, and the fallback behavior for every unsupported state.

### P0-R4: One confidence equation and typed gates

The candidate confidence equation is the normalized weighted geometric mean:

`exp(sum(weight_i * log(term_i)) / sum(weight_i))`.

Each gate is typed as `PASS`, `FAIL`, or `UNKNOWN`. A mandatory `FAIL` blocks
direction. A mandatory `UNKNOWN` makes directional confidence unavailable.
Optional missing terms may be omitted only with reduced coverage and a frozen
minimum-coverage gate. Evidence sharing one source lineage must be deduplicated
before weighting.

### P0-R5: Canonical causal clusters

A causal cluster ID must be a stable hash of canonical content, including
instrument identity, atomic interval, evidence cutoff, source/profile hashes,
actor identity, target identity, and the exact derivation role. Display labels
or broad event names are not sufficient identifiers. Every consumer must state
whether a field is evidence, derived context, visualization, or a voting term.

### P0-R6: Comparable FX subtraction

Base and quote inputs must share the same timestamp, evidence cutoff, profile
version, units, normalization, source lineage policy, and required coverage.
Coverage mismatch or an unavailable side produces `UNKNOWN`, not a forced
differential. Existing signed common mode remains a separate useful field.

### P0-R7: Duration-aware aggregation

Daily, weekly, monthly, and calendar summaries must integrate atomic-state
duration and report the state distribution. A period containing several state
changes cannot be reduced to whichever direction appears at one sample.

### P0-R8: Linked, progressive UI

The full architecture must not be rendered as one dense panel. Later UI work
uses linked views or tabs for ledger, interval timeline, vector audit, source
lineage, and validation. Unknown, unsafe, unvalidated, and execution-blocked
states remain visible.

## P0 Non-Goals

P0 does not:

- add a new score, phase angle, market direction, or confidence value;
- change current Vedha arithmetic;
- change FX research arithmetic;
- register a trial;
- consume Shadbala or Drik as a weight;
- modify Auto Suggest, live inference, official ML notes, or MT5 behavior;
- build or package a Windows or Android candidate.

## P1 Boundary

P1 may begin only when:

1. this audit and ADR-0005 are committed;
2. the machine-readable P0 audit validates;
3. the revised project specification is classified as architecture rather than
   doctrine;
4. existing SBC and FX foundations remain green;
5. all execution and inference locks remain false.

P1 is complete only when a deterministic atomic-interval contract:

- emits ordered, non-overlapping half-open intervals;
- records one timestamp-safe evidence cutoff per interval;
- preserves source/profile hashes and contribution lineage;
- separates favorable, adverse, net, gross activation, unknown count, unknown
  magnitude, and coverage;
- exposes no phase, financial direction, confidence, trade, or execution field;
- passes boundary, overlap, missing-evidence, serialization, and replay tests.

The phase-interference engine is not part of P1.
