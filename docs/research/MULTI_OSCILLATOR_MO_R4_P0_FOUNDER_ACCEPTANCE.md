# MO-R4-P0 Founder Acceptance Bookkeeping

Status: `FOUNDER ACCEPTED`

Date recorded: `2026-09-09` IST

## Accepted Candidate

The founder acceptance record applies to the already-built immutable candidate:

- Candidate: `0.10.64-pfr-v2b-mo-r3-r2-f1-r1`
- Source commit: `9208a552cbed5ec0228e7811c9189393a1581797`
- `sourceGitDirty=false`
- `executionAllowed=false`
- Prior candidate `0.10.63-pfr-v2b-mo-r3-r2-f1` remains unchanged.

The candidate hashes are preserved from the packaged durability proof:

| Artifact | SHA-256 |
| --- | --- |
| Portable | `A43ED1EF1CFD5CCFFDD7E7A14B5BCCB79538C5AF536638035B3C984D8D832545` |
| Installer | `3DC5ED637DDEE4C0625BAA745C8CB06D19EF87700699228AFE1E8CE61883BADB` |
| Sidecar | `B82F66D5A913232DB20BF081BF1328D18B77E9D872ED144A67DFC57A8A362852` |
| Build receipt | `A570E42C5843CC70BDB5EE34F73F43D4DA9EA8C90F409511BEC23841C6454E13` |
| Release manifest | `AC48605BFF0884D0F48F70719356D852C68EBBD12EC717977D353EAB49E19275` |
| Immutable resource tree | `0BBCE6E888974C28A59FA62589AE4604C8360675DC5FE3FA36F26FA82729F266` |

## Recorded Workflow State

- `MO-R3-R2-F1-R1`: `FOUNDER ACCEPTED`
- `FOUNDER_REVIEW_COLLECTION`: `GO`
- `REAL_24_ROW_OUTCOME_BLIND_REVIEW`: `AUTHORIZED`
- Real founder decisions at this bookkeeping point: `0`

This records that the accepted candidate may be used by the founder for the
manual outcome-blind review of the existing 24 verified April rows. It does
not classify an event, inspect an outcome, validate a financial rule, admit a
catalogue record, or authorize a signed wave.

Prior candidate history and the existing packaged durability record remain
authoritative and are not rewritten. The machine-readable state is also kept
in `status/acceptance/mo_r4_p0_founder_acceptance.json`.

## Freeze Verifier

This milestone also adds a standalone read-only verifier in
`gann-astro-desk/backend/founder_review_freeze.py`. It is an architecture and
test utility only. It was exercised against synthetic review stores and was
not run against the founder's real review root.

The verifier requires explicit paths for the immutable resource root, durable
review root, new output root, founder name, candidate release manifest, and a
human outcome-blind attestation file. It validates the exact 12 USD and 12 JPY
row universe, immutable identity and packet bindings, append-only revision
chains, decision/evidence/source-reference contracts, and the candidate safety
locks before constructing a new freeze bundle.

The verifier never writes the review store or immutable resources. A published
bundle is written to a new non-existing directory using a staging directory and
a single final directory publication. Existing bundles are never overwritten.
The output records:

- `FOUNDER_POLARITY_REVIEW:FROZEN_PENDING_CENTRAL_REVIEW`;
- `OUTCOME_ANALYSIS:NOT_STARTED`;
- `ANALYSIS_PROTOCOL:NOT_PREREGISTERED`;
- signed USD, signed JPY, and signed USDJPY resultants as `NOT_AUTHORIZED`;
- `executionAllowed=false`.

The 26 synthetic tests cover exact row counts, identity and revision integrity,
decision/evidence validation, attestation, no-op/blank review states, atomic
publication, output collision, and the complete lock surface. No real freeze
bundle was created during MO-R4-P0.

## Explicit Locks

No price, candle, return, PnL, outcome, backtest, market reaction, SBC
interpretation, Auto Suggest, LLM/ML interpretation, sign recommendation,
catalogue admission, Mode 1/Mode 2 output, signed wave, smoothing, numerical
normalization, magnitude, MT5, order, or execution path was used or enabled.

`executionAllowed=false` remains the controlling product state. Founder Review
collection is authorized for the founder only; central review must approve any
later freeze or outcome-analysis milestone.
