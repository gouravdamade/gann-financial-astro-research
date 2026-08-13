# PFR-V2B-R6-BPHS-T1 - Founder Acceptance Record (2026-08-14)

## Founder-observed evidence

The founder reduced the loaded chart range to seven days and physically
confirmed that the neutral BPHS Classical Calendar rendered successfully in
Fields. This is product evidence for the bounded seven-day case only. It is
not a financial result, doctrine certification, polarity decision, or
execution authorization.

## Accepted source and product semantics

The founder accepts the existing BPHS T1 source/engineering separation:

- the held 1899 witness supplies the transcribed thirty Muhurta names and
  order at printed p. 197 / PDF image 680;
- live calendar boundaries remain the separately labelled
  `SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1` engineering calculation;
- civil weekday remains `PARTIAL_SOURCE`;
- Tara remains `DEPENDENCY_NOT_READY` until a separate source-closure task
  proves a complete reference and mapping operator.

## Founder-approved Fields research-window policy

Interactive Fields computations use a maximum fourteen-calendar-day,
half-open research page anchored to the loaded chart/data start:

```text
pageStart(n) = datasetStart + n * 14 days
pageEnd(n)   = min(pageStart(n) + 14 days, datasetEnd)
researchWindow = [pageStart(n), pageEnd(n))
```

The same page is sent to the USD side field, JPY side field, derived
pair-relative field, independent SBC availability lane, and BPHS calendar.
The price chart may remain broad; it is a visual context and does not enlarge
the expensive research calculation request. Page changes are explicit.

The prior broad/unbounded `0.10.40` runtime behavior, which exposed a timeout
to the founder, is rejected as a product interaction. This record does not
reopen BPHS source doctrine: P2R1 is a runtime-window and resilience change.

## Still required

The next candidate must demonstrate the founder-approved fourteen-day page in
the packaged desktop path. Founder acceptance of the semantics and policy does
not itself accept an untested replacement binary.

## Guardrails

This policy does not enable price reading, polarity, pair/SBC fusion, Founder
Review decisions, Auto Suggest, ML, MT5, order placement, or execution.
