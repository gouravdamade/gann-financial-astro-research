# Multi Oscillator MO-R4A-S4-A1-P1-R1 Execution-Lineage Hardening

Status: `PRE_ACCESS_IMPLEMENTATION_HARDENED_PROVIDER_NOT_ACCESSED`

Milestone: `MO-R4A-S4-A1-P1-R1`

## Scope

This correction follows the accepted P1 implementation freeze and performs no
AWS, Dukascopy, credential, `GetObject`, `HeadObject`, `ListObjects`, or sample
download operation. The existing P1 freeze remains historical evidence. The
successor freeze records the corrected pre-access implementation and is the
current zero-network pre-access contract.

The unrelated working-tree files `gann_aspect_annotations_raman_v2.sqlite`,
`candlestick_shadow_v3.sqlite`, and `logs/` remain untouched and are not part
of the protected acquisition path.

## Central Blocker

The P1 module required both `HEAD` and `origin/master` to equal the old
pre-access commit `47e557b1e573e661d6b3c0f2855d0044895bb12b`. Once that
implementation was committed at `3cbb175db05ba66714611cc451faf72358b3759f`,
the module necessarily rejected the very commit it was meant to execute from.
Changing the constant to the successor commit would only recreate the same
self-invalidating cycle.

The corrected rule is content- and lineage-based:

1. `HEAD` and `origin/master` must resolve to the same commit.
2. The accepted pre-outcome base
   `47e557b1e573e661d6b3c0f2855d0044895bb12b` must be an ancestor of that
   synchronized commit.
3. The protected source and evidence paths must match committed `HEAD` bytes
   under Git's clean-filter semantics, with neither the worktree nor index
   dirty.
4. The successor freeze, authorization, parser, contracts, partition plan,
   and all prior scientific identities must cross-bind exactly.

The P1 implementation predecessor remains separately recorded as
`3cbb175db05ba66714611cc451faf72358b3759f`.

## Successor Artifacts

The authorization was regenerated because the acquisition module content
changed:

- module:
  `gann-astro-desk/backend/market_data_acquisition_s4_a1.py`
  SHA-256 `2448FD3B63FB85645F966609B377AB2C3DDF22CC240BDEBFDCFAB5257832B90A`
- authorization:
  `status/acceptance/mo_r4a_s4_a1_acquisition_authorization.json`
  canonical hash `9E8D2FF8547876918EFB5F362B0FC969BA608B75428CB0A2A2D584D34768D4C5`
- successor freeze:
  `status/acceptance/mo_r4a_s4_a1_p1_r1_pre_access_implementation_freeze.json`
  canonical hash `971E6BE30B4F1FEFBA3C11846C2CAB87987A9F5E390FFF31F1A6A639AB7D4739`

The successor freeze binds the predecessor freeze hash
`42BF3BB9BB9A10A340DEFDC5FD29825B130DC4487D746537084604639486F170`, the
P1 predecessor commit, the accepted pre-outcome base, the final module and
test hashes, the regenerated authorization hash, the frozen parser and
R3-R2/R3-R3 identities, and the exact 15-partition contract. The module does
not contain the successor freeze hash, so no module-to-freeze hash cycle is
possible.

The protected-path check uses Git's normalized object identity for text files
(`git hash-object --path`) together with both worktree and index diff checks.
This avoids treating a clean Windows CRLF checkout of an LF-indexed text file
as a false content change.

## Timestamp Semantics

Per-partition `requestStartedAtUtc` is captured immediately before the one
transport call. `retrievedAtUtc` is captured after the response bytes have
been fully read and the raw file has been atomically finalized. For a missing
or terminal provider error, it records when that terminal response or failure
was observed. The journal's existing `startedAtUtc` field is preserved.

Future raw manifests now keep the three Git meanings distinct:

- `authorizedPreOutcomeBaseCommit`
- `preAccessImplementationPredecessorCommit`
- `executionCommit`

They also carry `acquisitionStartedAtUtc` and
`acquisitionCompletedAtUtc` from the execution run rather than import time.

## Stream Failure Semantics

An ordinary exception from a response body's `.read()` is normalized to
`PROVIDER_BODY_STREAM_READ_FAILED`. The pending raw file is removed, no
partial bytes are promoted, the frozen parser is not called, the journal is
finished as `ATTEMPT_FAILED_TERMINAL`, no retry is attempted, and later
partitions are not requested. `KeyboardInterrupt` and `SystemExit` are not
converted by a broad `BaseException` handler.

## Verification and Locks

Synthetic tests cover descendant-lineage acceptance, divergence rejection,
protected module/authorization/freeze dirtiness, unrelated dirty paths,
successor self-hash and cross-binding, timestamp ordering, and streamed-body
failure cleanup. The final committed test and regression totals are recorded
in the handoff after validation.

No provider request occurred in P1-R1. `providerAccessPerformed=false`,
`PRICE_DATA_READ=false`, `OUTCOME_DATA_READ=false`, `outcomeUnlocked=false`,
and `executionAllowed=false`. The 24 frozen events, 17 bridge-applicable
events, 14 directional rows, 13 primary rows, Saturday exclusion, C1-C4,
40-state null, 8192 truth-table checks, 2744 timing checks, 39 intervals, 15
provider partitions, frozen parser, and retry policy remain unchanged.

Next gate:
`CENTRAL_REVIEW_FINAL_PRE_PROVIDER_EXECUTION_AUTHORIZATION`.

This milestone stops after zero-network pre-access validation and returns to
central review. It does not execute acquisition.
