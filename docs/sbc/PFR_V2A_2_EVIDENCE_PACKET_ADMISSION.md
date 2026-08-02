# PFR-V2A-2 Evidence Packet Admission

Date: 2026-08-02

Scope: harden the V2A immutable polarity catalogue so future entries have
verifiable reviewed provenance. This does not admit a USDJPY entry, score an
aspect, create a direction, add magnitude, or change execution locks.

## Delivered Contract

- Packet registry:
  `CHART_CONDITIONED_POLARITY_EVIDENCE_PACKET_REGISTRY_V1`.
- Seed registry:
  `research_labs/chart_conditioned_aspects/profiles/target_aware_polarity_evidence_packets_v1.json`.
- Registry state: `NO_REVIEWED_PACKETS`.

Each future reviewed packet must declare and hash its exact:

- instrument and accepted chart identity;
- transit body, natal target, and aspect type;
- categorical reviewed polarity only;
- astronomy contract and profile hash;
- reviewer identity and offset-aware review timestamp;
- at least one source reference.

The catalogue entry must also name the packet id and reproduce its hash,
identity, polarity, evidence status, and profile hash exactly. Any mismatch
causes loading to fail closed.

## What This Does Not Mean

This is provenance validation, not validation of market profitability or
astrological truth. The registry has no packets and the USDJPY panel remains
`POLARITY_CATALOGUE_MISSING`. No natural-planet rule, aspect geometry, SBC
state, past P/L, or LLM text can silently fill the gap.

SBC remains an independent synchronized comparison field, not confirmation.
No Auto Suggest, ML, live inference, shadow validation, MT5 order, or
execution behavior is connected to this material.

## Future Admission Checklist

1. Establish a concrete accepted chart identity and astronomy/profile contract.
2. Review a specific transit-to-natal aspect with source references.
3. Record a categorical result as research-only, including a reviewer and
   offset-aware timestamp.
4. Add the packet to the packet registry and its matching entry to the
   catalogue in the same reviewed change.
5. Run the packet/catalogue tests; confirm the product becomes `READY` only
   for that exact identity.
6. Keep magnitude unconfigured and the execution lock unchanged.

## Verification

- The focused catalogue suite includes valid-packet matching and mismatched
  polarity rejection.
- Empty production registries remain valid and return the explicit missing
  state.

## Candidate Preparation

PFR-V2A-3 adds a download-only, selected-aspect candidate worksheet to the
desktop. It does not weaken this admission contract; see
`docs/sbc/PFR_V2A_3_CANDIDATE_PACKET_PREPARATION.md`.
