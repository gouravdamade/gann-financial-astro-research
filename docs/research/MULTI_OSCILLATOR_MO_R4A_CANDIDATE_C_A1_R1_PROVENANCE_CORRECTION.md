# MO-R4A Candidate C A1-R1 Provenance Correction

Status: `PROVENANCE_CORRECTION_COMPLETE_CENTRAL_REVIEW_REQUIRED`

Milestone: `MO-R4A-CANDIDATE-C-A1-R1`

Branch: `research/candidate-c-evaluator-a-freeze`

Starting commit: `d72449f7fb4161cd4061d22e1eaa74d42fbbab48`

Stop gate: `CENTRAL_REVIEW_CANDIDATE_C_A1_R1_PROVENANCE_CORRECTION`

## Purpose

This is a narrow successor correction to the historical Evaluator A
implementation freeze. The original A1 freeze record remains unchanged and is
not being rewritten. This record corrects only the precision of its
real-population access description.

The historical record stated `realFrozenPopulationRead=false`. That statement
was too strong because `load_frozen_contracts()` reads and parses the frozen
shared astronomy snapshot and population manifest, validates their self-hashes,
population identity, event count, and related contract identities, and only
then removes the real arrays before returning `FrozenContracts`.

## Corrected Population-Access Semantics

The current successor truth is:

- `realFrozenPopulationRead=true`, scoped strictly to reading and parsing frozen
  artifacts for validation metadata;
- `realFrozenPopulationArtifactReadForValidation=true`;
- `realFrozenPopulationExposedToEvaluator=false`;
- `realFrozenPopulationArraysExposedToEvaluationPath=false`;
- `realFrozenPopulationEvaluated=false`;
- `realCandidateCOutputProduced=false`;
- `realCandidateCOutputInspected=false`;
- real Candidate C output rows produced: `0`;
- the arrays were removed before the validated `FrozenContracts` object was
  returned;
- the synthetic test fixture invokes the loader, which is why the validation
  read is part of the A1 test path.

The same corrected values are recorded in both the successor execution-boundary
block and its `correctedResearchBoundary` duplicate. Reading immutable real
artifacts for identity validation is not real population evaluation and is not
real Candidate C output generation.

## Evidence in the Unchanged Implementation

The implementation evidence is retained by identity, not changed by this
correction:

- `research_labs/candidate_c_reproduction/evaluator_a/contract_loader.py`
  reads and validates the snapshot and manifest in `load_frozen_contracts()`;
- the same function removes `events` and `population` before returning
  `FrozenContracts`;
- `research_labs/candidate_c_reproduction/evaluator_a/test_evaluator_a.py`
  invokes the loader and asserts those arrays are absent from the returned
  metadata.

## Protected Identities

The Evaluator A implementation and test source are unchanged. The protected
identities remain:

- implementation aggregate hash:
  `93ECB7BDB684C9F9788F63BADAE8D297453F02557D7BB89DB2621CF9E257DCFB`;
- test-source hash:
  `93BF61F16BB9CF44B44D0F251418D9CFDC7F8E74557556F802B2F9B6D144A25E`.

No Evaluator A execution against the 645-event real population occurred. No
5,160-row real Candidate C output was generated or inspected. Evaluator B and a
comparator were not created.

## Preserved Research Boundary

No market, price, return, outcome, provider, Swiss Ephemeris, polarity,
magnitude, score, wave, or execution data was accessed or created. The
source-contract and clean-room boundaries remain unchanged. `executionAllowed`
remains `false`.

The synthetic validation boundary remains the only exercised evaluation path.
This correction does not authorize a real run, a future population read beyond
the validation semantics recorded here, or any Candidate C output.

## Verification and Next Gate

The successor machine record is
`status/acceptance/mo_r4a_candidate_c_a1_r1_provenance_correction.json`. Its
self-hash uses the stated canonical UTF-8 JSON convention and excludes only
`successorRecordHash`.

The A1 historical record remains a preserved historical snapshot, while this
successor is the truthful provenance correction for central review. The next
gate is:

`CENTRAL_REVIEW_CANDIDATE_C_A1_R1_PROVENANCE_CORRECTION`
