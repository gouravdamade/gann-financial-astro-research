# SBC Timing-Profile Source Packet S1

Date: 2026-07-29

S1 adds a fail-closed readiness gate for the evidence package that must exist
before a timing-profile candidate can be sent to independent source review.

The gate checks:

- exact candidate and packet identities and canonical hashes;
- source declarations linked to candidate `sourceEvidence`;
- page-cited claims linked to exact candidate subtrees and excerpt hashes;
- primary and independent-witness coverage for every doctrine domain;
- frozen research-specification coverage for eligibility and confidence;
- independent lineage coverage;
- a fully resolved source-conflict register;
- an external-review request with an explicit independence requirement; and
- research, inference, financial, and execution locks.

The implementation is:

- `sbc/timing_profile_source_packet.py`
- backend POST `/api/chakra-lab/timing-profile/source-packet/readiness`
- native read-only command
  `chakra_lab_timing_source_packet_readiness`
- linked Chakra Audit `Source packet` tab

S1 verifies the consistency of declarations inside JSON. It does not inspect
the declared book or excerpt bytes. A passing packet is only
`READY_FOR_EXTERNAL_REVIEW`; it is not externally reviewed, source-certified,
registered, directional, financially validated, or executable.
