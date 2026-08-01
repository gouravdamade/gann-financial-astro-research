# ADR-0018: PFR-C1 Product Integrity Correction

- Status: active
- Date: 2026-08-01
- Branch: `product-first-sbc-phase-lab`
- Supersedes: the PFR-7 stop condition in ADR-0017 only for the bounded
  PFR-C1 correction pass.

## Decision

Keep the product-first branch open and perform one correction pass named
PFR-C1. It corrects the semantics and integrity of the already-visible SBC
workspace. It is not a new roadmap or research milestone.

PFR-2 through PFR-5 are recorded as partial or prototype work until their
original acceptance contracts pass. Their names and original definitions are
not rewritten around the current implementation.

## Scope

PFR-C1 may correct:

1. Product status and traceability.
2. Independent USD/JPY fields and pair formulas.
3. Per-event, asymmetric lifecycle phase geometry with an authoritative
   deterministic contract.
4. Fixed-wheel geometry and cancellation semantics.
5. Timing visual integrity, opt-in flagging, accessibility, regression, and a
   corrected Windows candidate.

## Locks

The following stay unchanged throughout PFR-C1:

- `executionAllowed=false`
- `automaticOrderPlacement=false`
- `voteWeight=0`
- `directionalContribution=0`
- `fusionCoefficient=0`
- scalar SBC remains visible
- no-lookahead and evidence-cutoff behavior remains intact
- unknown evidence stays outside continuous resultants
- no Auto Suggest, ML, live inference, trading, or MT5 execution work

## Stop Condition

Build one corrected Windows candidate after PFR-C1 verification, then stop for
founder acceptance. Certification, validation, source-authority, Android, RAG,
and new research work remain deferred.
