# PFR-V2A-3 Candidate Evidence-Packet Preparation

Date: 2026-08-02

Scope: give the founder-facing Chakra workspace a safe way to prepare the
research worksheet for a selected transit-to-natal aspect. This milestone
does not admit evidence, add catalogue content, classify polarity, configure
magnitude, or change any execution lock.

## Delivered Product Surface

When a chart aspect is selected, the independent **Chart-conditioned aspect
pressure** panel now shows **Evidence packet readiness** whenever its immutable
catalogue lookup is not `READY`.

The panel displays the selected event's:

- transit body, natal target, and aspect type;
- selected event astronomy contract; and
- a download action for a local JSON candidate packet.

The candidate carries the exact lookup instrument convention, for example
`FX:USDJPY`, together with the selected aspect identity. It is deliberately
stamped `CANDIDATE_NOT_ADMISSIBLE` and has no write path to either the evidence
packet registry or the immutable polarity catalogue.

## Required Before Admission

The downloaded candidate intentionally leaves these items empty until they
come from actual reviewed research material:

1. accepted chart id;
2. reviewed categorical state;
3. profile hash;
4. reviewer identity and offset-aware timestamp;
5. source references; and
6. deterministic packet hash.

Only after those fields are independently reviewed can a future change add a
matching packet and catalogue entry under the V2A-2 contract. A downloaded
candidate alone remains invalid and cannot alter a product lookup.

## Boundaries

`TARGET_CONTEXT_INCOMPLETE` is expected until an accepted chart id exists; it
does not mean the app inferred a polarity. The panel remains a separate
synchronized comparison field: it does not fuse with SBC, calibrate a score,
drive Auto Suggest, create ML evidence, alter live inference, or influence an
MT5 order.

## Verification

- The product workspace test confirms that selecting an aspect exposes the
  candidate readiness surface and its download action without a polarity call.
- Existing V2A-2 packet/catalogue tests remain the admission authority.
