# Candidate C RUN1 Real Execution Pre-Run Freeze

## Scope

This record freezes the outcome-blind machinery for a future, one-shot
Candidate C comparison over the already frozen 645-event population. It does
not authorize or perform that run. No real Candidate C output rows or A/B
comparison result exist in this milestone.

## Admission and Reuse

The real frozen population was read and parsed only for identity, structure,
and adapter-equivalence validation. It was not exposed to either evaluator's
evaluation path and was not evaluated.

Both frozen public evaluator entry points are synthetic-only. Evaluator A's
synthetic validation gate is explicit; Evaluator B's public interface and data
model are synthetic-only by contract. Therefore both are classified
`THIN_EXECUTION_RELEASE_REQUIRED`.

The additive `real_run` release layer does not copy C01-C07 business logic.
It validates an explicitly real marker, adapts frozen representations, and
calls the frozen evaluator component functions directly. The historical A, B,
AB1 V1, and AB1-R1 V2 artifacts remain unchanged.

## Frozen Inputs

- Event count: `645`
- Expected output rows: `5160`
- Population hash:
  `A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6`
- Population manifest hash:
  `0B384FF0131BF19EFB842A3D4AEE4F7D1F9A923469281A65D6326B76CC39A092`
- Shared astronomy snapshot hash:
  `F5CC39224D61D01D74B1C43EF838D3EDCA7999E11CE878B06EE115BAA2802915`
- Component bindings hash:
  `D3219C1E6A8B7C791064F50E2CF23C211D4DE859AA73978B689C97E650DF5985`
- Row-key universe hash:
  `6AC975EE4DA32A3872399C68F514BA19E63FFAC5F565018A2DF15CECA27A4580`

The truthful real-input marker is `REAL_FROZEN_CANDIDATE_C_P0_R1`.
`SYNTHETIC_ONLY` is rejected on the RUN1 path.

## Comparator

The eventual comparison uses
`MO_R4A_CANDIDATE_C_AB1_R1_SEMANTIC_PROJECTION_V2`, semantic hash
`1DDFC3B79EC30913254A2FEA117A97EA1761E42D8681EB5D2CB6B2D698187BED`.
Its ordinary-Drsti aliases remain a closed four-entry mapping, including
`DRSTI_FULL -> FULL`; no unrestricted normalization is allowed.

Rows will align by immutable event identity and source/operator identity, not
by list order. A discrepancy freezes the run; neither evaluator is an oracle
and no repair, adjudication, or rerun is permitted in the same run.

## Future Protocol

The frozen order is identity validation, real-input adapter construction,
adapter equivalence, A raw output, B raw output, row-universe validation, V2
projection/comparison, first comparison freeze, then stop before any
market/outcome analysis. The three future paths are declared in the machine
contract but remain unpopulated.

## Locks

`REAL_CANDIDATE_C_RUN_AUTHORIZED=false`. There was no price, return, outcome,
provider, Swiss Ephemeris, market polarity, score, magnitude, wave, Fields,
Auto Suggest, ML, MT5, or execution access. The next gate is
`CENTRAL_REVIEW_CANDIDATE_C_RUN1_REAL_EXECUTION_PRERUN_FREEZE`.
