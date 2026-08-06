# PFR-V2B-R5-F2A-R2 Founder Review Workbench

Status: implemented as a founder-only, research-only workbench.

## Purpose

The workbench presents the verified April 2025 USD and JPY transit-to-natal
event rows for founder review. It records a founder's explicit categorical
decision without interpreting the astronomy, looking at price, consulting
SBC or an LLM, creating a catalogue record, or rendering a directional field.

The canonical blank packets remain read-only:

- `USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`
- `JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`

The workbench also verifies the corresponding R5 F2A-R1 identity-integrity
manifest and the independent audit report before a row can be edited.

## Eligibility and fail-closed behavior

A row is reviewable only when all of these checks pass:

1. The raw blank packet hash matches the identity manifest.
2. The identity manifest's original-generation hash matches the raw packet.
3. The row event ID is listed in the manifest and exists once in the audit.
4. The event hash and immutable event identity match the audit record.
5. The audit status is exactly `SINGLE_PASS_VERIFIED` and all audit checks are true.
6. The side's chart and hypothesis match the accepted audit registry record.

Any mismatch raises a fail-closed error for the workbench request. The export
path also refuses an unknown event ID, a mutated event identity, or a row that
was not eligible at load time.

## Founder decisions

Every row starts with blank decision and evidence-classification fields. The
allowed decision values are:

- `SUPPORTIVE`
- `ADVERSE`
- `MIXED`
- `NEUTRAL`
- `UNKNOWN_MORE_EVIDENCE_REQUIRED`
- `REJECT_EVENT_IDENTITY`

Every non-rejected decision requires one of:

- `FOUNDER_RESEARCH_HYPOTHESIS`: versioned calibrated research only,
  non-classical, and financially unvalidated.
- `SOURCE_BACKED_CLASSICAL_CANDIDATE`: requires source ID, edition, exact
  printed page/locator, and a brief connection to this exact event. It remains
  pending the separate R4 Mode 2-to-Mode 1 promotion gate.

`UNKNOWN_MORE_EVIDENCE_REQUIRED` remains an unknown gap. It is never changed
to neutral by export. A rejected identity requires a founder rejection reason
and cannot carry an evidence classification.

## Packet outputs

The initial checked-in outputs intentionally contain no decisions and have
`REVIEW_NOT_STARTED` status. Later founder exports replace only these review
outputs; they never edit the blank packets or identity manifests.

Each side has:

- a reviewed JSON packet;
- a reviewed-packet manifest with raw file SHA-256 and reviewed hash;
- a completeness report;
- a human-readable Markdown rendering;
- a status record under `status/founder_review/`.

The reviewed packet hash is computed over canonical JSON with its hash field
set to null before the hash is inserted. Raw file hashes are recorded
separately in the manifest. This keeps packet identity auditable while review
timestamps remain explicit content.

## UI use

Open the top-level **Fields** surface, then choose **Founder Review**. The
surface loads both sides, displays UTC and IST times, chart identities,
astronomy contract, orb profile, verified motion information when present, and
the identity status. It does not show candles, returns, SBC, Shadbala,
interpretation hints, or AI output.

Enter a reviewer name before exporting any decided row. Choose a decision and
evidence class only when ready. Source-backed rows additionally require all
four source-reference fields. Partial review is valid. The resulting status is
one of `REVIEW_NOT_STARTED`, `REVIEW_IN_PROGRESS`,
`REVIEW_COMPLETE`, or `REVIEW_COMPLETE_WITH_UNKNOWNS`.

## Explicit stop gate

This milestone does not:

- admit polarity records into a catalogue;
- create USD, JPY, or pair waves;
- configure magnitude;
- run F2B or Auto Suggest;
- use price, SBC, Shadbala, Ashtakavarga, an LLM, or execution;
- promote a classical source claim into Mode 1.

Founder decisions remain evidence for a later, separately approved admission
milestone.
