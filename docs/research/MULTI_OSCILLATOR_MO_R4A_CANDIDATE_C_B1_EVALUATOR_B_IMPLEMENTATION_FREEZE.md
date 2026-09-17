# MO-R4A Candidate C B1 Evaluator B Implementation Freeze

## Status

This record freezes a second Candidate C evaluator as a clean-room,
synthetic-only implementation. It does not compare Evaluator B with Evaluator
A and does not execute either evaluator against the real Candidate C population.

- baseline: `35f6319aa0a984756c5b59bbd88c6ac8a0b5c7ea`
- branch: `research/candidate-c-evaluator-b-freeze`
- implementation commit: `267885b84e1d796b438b09d73f3fb9792235a41e`
- freeze record: `status/acceptance/mo_r4a_candidate_c_evaluator_b_implementation_freeze.json`
- next gate: `CENTRAL_REVIEW_CANDIDATE_C_B1_IMPLEMENTATION_FREEZE`

The B worktree was created directly from the frozen P0-R1 shared baseline.
`origin/master` was unchanged.

## Frozen input validation

The loader validates the P0-R1 population manifest, shared astronomy snapshot,
component bindings, preregistration, S1R1 ledger, S2R1-R1 Saravali ledger, and
unresolved-dependency registry. It validates the declared canonical identities,
the 645-event population identity, the 5,160-row universe identity, the output
schema, UNKNOWN taxonomy, applicability matrix, and all pinned source artifact
identities.

The 645-event and 5,160-row artifacts are read and parsed only for identity and
integrity validation. The population and event arrays are removed before the
validated `FrozenContracts` object is returned. No real event is evaluated and
no real Candidate C output row is generated or inspected.

## Independent implementation

Evaluator B lives in the isolated namespace
`research_labs/candidate_c_reproduction/evaluator_b/` and uses Python standard
library code. It does not import Evaluator A, the historical production source
operator, market bridge code, Swiss Ephemeris, broker/provider code, or any
price/outcome path.

The implementation consumes the frozen contracts directly:

- C01: Trailokya natural planet class, with the frozen Moon and Mercury UNKNOWN
  paths;
- C02: directed Trailokya natural relationship lookup;
- C03: inclusive relative-place temporary relationship;
- C04: Saravali natural relationship plus the frozen temporary relationship;
- C05 ordinary and special Drsti as two separate rows;
- C06: bounded Trailokya Sthula motion categories only for enumerated cases;
- C07: mandatory generic UNKNOWN because no typed Sthana-Phala measurement is
  admitted.

The relative-place calculation is implemented as:

`((targetSignIndex - sourceSignIndex) mod 12) + 1`

Event roles remain `transitBody` as source and `natalTarget` as target. Aspect
type is not used to redefine relative place. No modifier stacking, precedence,
market sign, magnitude, score, wave, or financial interpretation is produced.

## Synthetic validation

The independent suite contains 21 passing tests covering frozen identity
validation, array stripping, synthetic schema failure, all eight row templates,
closed and UNKNOWN C01 paths, directional C02 behavior, C03 relative place and
aspect independence, Saravali-only C04 behavior, separate C05 operators,
enumerated C06 motion behavior, C07 abstention, UNKNOWN taxonomy, output schema
guards, the blocked real-population entry point, and prohibited dependency
imports.

Validation results:

- `python -m pytest -q research_labs/candidate_c_reproduction/evaluator_b`: **21 passed**
- `ruff check research_labs/candidate_c_reproduction/evaluator_b`: **passed**
- `python -m compileall -q research_labs/candidate_c_reproduction/evaluator_b`: **passed**
- `git diff --check`: **passed**

## Protected identities

Implementation files:

- `research_labs/candidate_c_reproduction/__init__.py`
- `research_labs/candidate_c_reproduction/evaluator_b/__init__.py`
- `research_labs/candidate_c_reproduction/evaluator_b/canonical.py`
- `research_labs/candidate_c_reproduction/evaluator_b/contract_loader.py`
- `research_labs/candidate_c_reproduction/evaluator_b/evaluator.py`
- `research_labs/candidate_c_reproduction/evaluator_b/models.py`

The implementation aggregate convention is SHA-256 uppercase hex of canonical
JSON for the lexicographically sorted `{path, sha256}` Git-blob manifest, using
`ensure_ascii=true`, `sort_keys=true`, and compact separators. The protected
aggregate is:

`0A3266F754939D2408B4B7646A1E36A1CEC7338EDADE5844E831BCF6EB4CD199`

The test-source hash is:

`31AA1B525B29AFE4CD206D63A1DA611820D6A87E1C71465645BADEE0B9487CB9`

The machine-readable freeze record uses the stated canonical self-hash
convention, excluding `freezeRecordHash`.

## Clean-room evidence

For this B1 implementation, no Evaluator A source or tests were opened from the
B worktree, no A code was imported or copied, no A branch was used as a baseline,
and no comparator was created. The implementation was derived from the shared
P0-R1 contracts and the declared source semantics only. B1 does not establish
that Evaluator A or B is correct, that they agree, that the source doctrine is
historically true beyond its accepted packets, or that classical astrology
predicts markets.

## Locks and stop state

Real Candidate C execution is explicitly blocked. `executionAllowed=false`.
No market, price, return, outcome, provider, or Swiss Ephemeris data was read.
No polarity, magnitude, score, wave, or market bridge was created. No source
doctrine was expanded.

The next action requires central review. Do not inspect Evaluator A, compare A
and B, execute either evaluator on the 645-event population, generate 5,160
real rows, inspect distributions, read outcomes, or begin a comparator without
a separate authorization.
