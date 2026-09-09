# MO-R4-P0 Outcome-Blind Founder Review Freeze Architecture

Status: `IMPLEMENTED - SYNTHETIC-ONLY VERIFIER`

Date: `2026-09-09`

## Purpose

MO-R4-P0 defines the boundary between a founder's manual, outcome-blind
review and a later central freeze. The implementation is a standalone
read-only verifier. It does not alter the accepted candidate, the immutable
blank packets, the identity manifests, or the durable review store.

No real review root was read and no real freeze bundle was published in this
milestone.

## Explicit Invocation Contract

The verifier has no implicit workspace or application-data discovery. A future
operator must provide every data boundary explicitly:

```text
python backend/founder_review_freeze.py \
  --resource-root <immutable-resource-root> \
  --review-root <durable-review-root> \
  --output-dir <new-output-root> \
  --founder-name "<founder-name>" \
  --candidate-release-manifest <release.manifest.json> \
  --attestation-file <outcome-blind-attestation.txt> \
  [--freeze-id <freeze-id>]
```

The utility accepts only a new output directory. It stages the complete JSON,
Markdown, and SHA256SUMS files and publishes the directory once; it refuses an
existing final directory and cleans an interrupted staging directory.

## Validation Gates

Before constructing output, the verifier checks:

1. Candidate release metadata has a self-consistent version, a 40-character
   source commit, `sourceGitDirty=false`, and `executionAllowed=false`.
2. USD and JPY immutable blank packets, identity manifests, and identity-audit
   records match their recorded SHA-256 bindings and read-only contracts.
3. Each side has exactly 12 eligible rows, all with
   `SINGLE_PASS_VERIFIED`, exact event identity fields, and every identity audit
   check true.
4. Every side's current pointer resolves to an append-only revision chain.
   Packet hashes, parent hashes, timestamps, completeness, and server-owned
   chronology are checked at every revision.
5. Review decisions and evidence classifications use the existing enums.
   Reasoning and exact source locators are required by the existing review
   contract where applicable; `REJECT_EVENT_IDENTITY` remains the only
   decision that may omit a classification.
6. Event data contains no price, close, return, PnL, outcome, score, or
   magnitude field. These are structural rejection conditions, not presentation
   filters.
7. The attestation is explicit human text, is not treated as system proof, and
   is included in the resulting content hash.

The verifier validates both sides independently, then creates a combined
deterministic hash over side hashes, provenance, state, guardrails, counts, and
attestation. Generated server time and the generated freeze ID are metadata and
do not change the content hash.

## Output State

The resulting bundle is explicitly non-analytic:

- `FOUNDER_POLARITY_REVIEW:FROZEN_PENDING_CENTRAL_REVIEW`;
- `OUTCOME_ANALYSIS:NOT_STARTED`;
- `ANALYSIS_PROTOCOL:NOT_PREREGISTERED`;
- `PRODUCTION_POLARITY_ADMISSION:NOT_STARTED`;
- `SIGNED_USD_WAVE:NOT_AUTHORIZED`;
- `SIGNED_JPY_WAVE:NOT_AUTHORIZED`;
- `SIGNED_USDJPY_RESULTANT:NOT_AUTHORIZED`;
- `MAGNITUDE:NOT_CONFIGURED`;
- `executionAllowed=false`.

The bundle contains normalized audit rows and immutable packet/revision
provenance, not recommendations. It has no outcome columns and no mechanism
for reading market data.

## Test Boundary

The accompanying 26 tests use only temporary synthetic resource and review
stores. They prove exact side cardinality, identity/packet/audit bindings,
revision integrity, decision/evidence rules, human attestation, blank/no-op
states, deterministic content hashing, atomic publication, collision refusal,
and the absence of catalogue/evidence admission or execution fields.

They do not prove that a founder has reviewed any row, and they do not create a
real freeze. A later real freeze requires the founder's completed review state,
an explicit human attestation, and a separately authorized central operation.

## Historical Candidate Boundary

The accepted `0.10.64-pfr-v2b-mo-r3-r2-f1-r1` candidate and the historical
`0.10.63-pfr-v2b-mo-r3-r2-f1` candidate remain unchanged. The packaged
durability evidence in
`docs/research/MULTI_OSCILLATOR_MO_R3_R2_F1_R1_PACKAGED_DURABILITY.md` remains
the source for their artifact hashes and the prior isolated persistence proof.

## Locks

This architecture does not introduce price/outcome reads, market mapping,
polarity, scoring, SBC, signed waves, Auto Suggest, LLM, ML, smoothing,
normalization, magnitude, MT5, orders, or execution. `executionAllowed=false`
is required by the candidate manifest and by the freeze output.
