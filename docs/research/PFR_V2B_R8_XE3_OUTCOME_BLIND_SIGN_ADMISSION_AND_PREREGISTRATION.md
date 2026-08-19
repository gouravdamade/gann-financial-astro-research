# PFR-V2B-R8-XE3 Outcome-Blind Sign Admission and Preregistration

## Scope

XE3 is a founder-operated research workbench for the already verified USD and
JPY April 2025 transit-to-natal packets. It does not calculate a sign from
aspect geometry, bodies, Moon speed, motion, SBC, price, an LLM, or any other
automatic source. It records only a founder-entered decision after an explicit
outcome-blind attestation.

The canonical blank packets and their identity-integrity manifests remain
read-only. XE3 keeps an append-only revision history under the desktop data
directory and creates immutable hash-addressed signed-evidence ledgers. The
mutable index only points to the latest revision for each side.

## Admissible identity

Every row must be present in its complete USD or JPY packet and preserve the
exact event identity, event hash, chart ID, chart-hypothesis ID, packet hash,
and identity-integrity manifest hash. Only `SINGLE_PASS_VERIFIED` rows are
reviewable. Any identity mutation, missing row, duplicate, price-read claim, or
missing attestation fails closed.

## Founder inputs

Permitted decisions are `SUPPORTIVE`, `ADVERSE`, `MIXED`, `NEUTRAL`,
`UNKNOWN_MORE_EVIDENCE_REQUIRED`, and `REJECT_EVENT_IDENTITY`. Every
non-rejected decision requires exactly one evidence classification:

- `FOUNDER_RESEARCH_HYPOTHESIS`: research-only, non-classical, not eligible for
  Source Only.
- `SOURCE_BACKED_CLASSICAL_CANDIDATE`: requires source ID, edition, locator,
  and an event-specific connection. It remains pending the independent source
  promotion gate.

`SUPPORTIVE`, `ADVERSE`, `MIXED`, and `NEUTRAL` require founder reasoning.
Rejected identities require a rejection reason. Unknown is a reviewed state and
is never silently converted to neutral.

## Scalar projection

The projection is intentionally categorical and auditable:

| Decision | Projection |
| --- | --- |
| `SUPPORTIVE` | `+1.0` |
| `ADVERSE` | `-1.0` |
| `NEUTRAL` | exact `0.0` only when explicitly selected |
| `MIXED` | non-projectable `null` |
| `UNKNOWN_MORE_EVIDENCE_REQUIRED` | non-projectable `null` |
| `REJECT_EVENT_IDENTITY` | excluded, retained in audit |

No unknown value is treated as zero. The ledger retains side, event, causal
identity, review revision, and projection status for every decided row.

## Frozen XE2 M0-M4 preview

XE3 reuses the accepted XE2 causal transform implementation without changing
parameters or creating an alternative scoring engine:

- M0: base founder-entered sign.
- M1: bounded scoped positive Moon-speed multiplier with beta `0.8`, minimum
  `0.5`, and maximum `1.5`.
- M2: speed remains a separate causal channel.
- M3: causal interaction with gamma `0.5`.
- M4: direct-motion context gate.

The modifier is bound to the same hash-linked causal event. There is no global
modifier, no stacking, no transform winner, no price forecast, and no outcome
evaluation. Events outside the frozen XE2 cohort remain in the ledger but are
shown as `NOT_IN_XE2_FROZEN_COHORT` for the M0-M4 preview.

## Preregistration

The trial freeze remains unavailable until both complete USD and JPY review
packets reach a terminal reviewed state. A successful freeze captures the
exact reviewed-packet hashes, revision hashes, scalar mapping, causal IDs,
unchanged XE2 profile hash and transforms, and the exact 40-character source
commit bound into the packaged founder candidate. It does not authorize any
outcome read; the outcome contract remains `NOT_YET_FOUNDER_APPROVED`.

The current baseline starts with zero founder decisions and therefore reports
`NOT_FROZEN` with `freezeReady: false`.

## Locks

`priceDataRead`, `priceOutcomeRead`, `liveMt5Read`, `fieldsRead`, `sbcRead`,
`autoSuggestRead`, `llmPolarityInference`, `marketDirectionInferred`,
`modeOnePromotion`, `executionAllowed`, and automatic order placement all
remain false. The Experiments shell replaces the refresh and live-quote status
with an explicit `OUTCOME-BLIND REVIEW / PRICE AND LIVE REFRESH HIDDEN` badge
whenever XE3 is selected.

