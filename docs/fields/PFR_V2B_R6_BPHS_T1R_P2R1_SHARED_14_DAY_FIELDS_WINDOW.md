# PFR-V2B-R6-BPHS-T1R-P2R1 - Shared 14-Day Fields Research Window

## Scope

This product correction replaces broad viewport-driven Fields computation with
one founder-approved, maximum fourteen-calendar-day research page. It does not
change BPHS source output, Tara availability, SBC source profiles, polarity,
financial interpretation, Auto Suggest, or execution locks.

## Contract

`FieldsWorkspace` derives the dataset extent from the loaded chart candles and
compiles only one deterministic half-open page at a time. The long chart
viewport remains visual context. `Previous 14 days`, `Next 14 days`, and
`Load window containing crosshair` change pages explicitly; moving the
crosshair alone never starts a request.

The selected research page is the exact input for:

1. `SYNCHRONIZED_INDEPENDENT_RANGE_V1` USD and JPY side fields;
2. the derived pair-relative field, which remains downstream of those two
   independent side records;
3. the independent SBC request/availability lane; and
4. `BPHS_CLASSICAL_CALENDAR_RANGE_V1` when BPHS Calendar is enabled.

Frontend caches completed exact page/profile results while retaining request
sequence protection. A late response for a previous page cannot overwrite the
currently selected page.

## Backend boundary

The BPHS interactive endpoint rejects a request longer than fourteen days
before opening the Swiss-Ephemeris calculation loop with the deterministic
error `BPHS_INTERACTIVE_RESEARCH_WINDOW_EXCEEDS_14_DAYS`.

The synchronized-range service remains a reusable low-level compiler. The
caller audit found its production frontend use only in `FieldsWorkspace`; the
new explicit Fields page is therefore the interactive bound, without silently
constraining unrelated direct/batch research callers.

## Development-sidecar timing check

On the configured Windows Python sidecar environment, the BPHS compiler
completed deterministic one-day, seven-day, and fourteen-day calls in 0.209 s,
1.044 s, and 2.160 s respectively. The complete shared synchronous Fields
request, including USD, JPY, and Phaladeepika SBC availability, completed in
7.543 s, 7.598 s, and 7.642 s respectively. These are implementer measurements,
not founder physical-package acceptance; the immutable candidate retains the
separate packaged timing checklist.

The full backend suite was re-run after this correction. The earlier seven
Founder Review packet-hash errors did not reproduce: 208 tests passed. No
packet, manifest, chart identity, or Founder Review artifact was changed, so
no separate integrity-repair commit is required.

## BPHS discoverability

The Fields header stays visible while the workspace scrolls. Its explicit
`BPHS Calendar / 1899 Research` switch persists for the current desktop
session, so enabling the calendar remains discoverable after visiting another
workspace. The calendar remains separate from the SBC source-profile selector.

## Guardrails

No category is translated into supportive/adverse direction, a score, a
forecast, or an execution action. Execution stays disabled.
