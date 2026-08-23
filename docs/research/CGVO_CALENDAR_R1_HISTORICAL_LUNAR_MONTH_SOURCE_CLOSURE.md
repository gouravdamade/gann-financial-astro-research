# CGVO-CALENDAR-R1 Historical Lunar-Month Source Closure

**Status:** `HISTORICAL_OPERATOR_PARTIAL_FAIL_CLOSED`
**Scope:** source and runtime audit only. No Multi Oscillator, Fields, price,
polarity, MT5, Auto Suggest, ML, or execution path changed.

## Witness and method

The held private witness is the project record
`BRIHAT_SAMHITA_SASTRI_BHAT_1946_WORKING_WITNESS`. Its complete-file SHA-256
was independently verified as
`D7425625010C621FF6651BF6BF916506791E3D4381078251AC7DC8EFBBA6577A`.
The PDF remains private and is not a repository resource.

The following original page images were inspected visually. OCR was used only
to locate pages, never as controlling evidence.

| Locator | Printed page | PDF image | Evidence retained |
| --- | ---: | ---: | --- |
| Brihat Samhita II.5 | 8 | 33 | Root terms `Adhimasa` and `Avama` occur. The surrounding translator note delegates detailed intercalation treatment to Surya Siddhanta. |
| Brihat Samhita XXV.5 | 238 | 263 | The source uses the dark half of Magha, a strong internal discriminator for a Purnimanta reading. |
| Brihat Samhita XXV.6 and XXVI.1 | 239 | 264 | Month names and named full-moon contexts are used, but no universal month-naming operator is stated. |

## A--G closure matrix

| Question | Result | Authority boundary |
| --- | --- | --- |
| A. Month basis | `PURNIMANTA`, `HIGH_CONFIDENCE_SOURCE_INTERNAL_INFERENCE` | The dark-half Magha example supports this reading. It is not a direct formal boundary definition. |
| B. Month naming | Runtime uses `NEXT_FULL_MOON_NAKSHATRA_LOOKUP_V1` | The held witness contains month-name usages, not a closed general mapping from a full moon to a month name. |
| C. Adhika | Root term recorded | II.5 has the term. Its translator note describes the matter and points to Surya Siddhanta; that note is not an independent root closure for the full operator. |
| D. Kshaya | Unknown | The root term `Avama` is recorded. The held witness does not source-close that `Avama` is exactly the modern engineering label `Kshaya`, nor its naming rule. |
| E. Boundary | Unknown | The source does not close new moon, full moon, sunrise, tithi, ingress, or any other exact membership instant. |
| F. Time/locality | Unknown | The implementation computes Swiss Ephemeris UTC instants and then attaches a locality-derived civil date for provenance. It does not use local civil day or sunrise to select month membership. |
| G. Modern heuristic | Kept, explicitly labelled | Physical lunations and selected-frame solar ingresses are a modern fail-closed guard, not historical doctrine. |

## Current runtime: accurate but not overclaimed

`gann-astro-desk/backend/cgvo_service.py` finds physical full/new-moon events,
uses a fixed full-moon-nakshatra lookup for an ordinary Purnimanta result, and
checks every overlapping new-moon interval for a selected-frame solar ingress.
Exactly one ingress per relevant interval permits an ordinary display. Zero,
two, unresolved, or exceptional counts return
`UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED`.

This is a reasonable *engineering guard*: it prevents the runtime from
inventing an Adhika or Kshaya label. It is not a historical operator. In
particular, the code does not distinguish a zero-ingress case from a
two-ingress case as a named traditional category; both remain unknown.

The selected Chitra reconstruction can affect ingress-count results. That
dependency is reported rather than hidden, and it is one reason the calendar
profile cannot become source-certified by this audit.

## Bounded case audit

| Case | Runtime observation | Historical result |
| --- | --- | --- |
| `2025-04-15T00:00:00Z` | `VAISHAKHA`; two overlapping guard intervals, each with one ingress | Ordinary runtime case, not source-certified. |
| `2023-07-29T00:00:00Z` | One interval has zero ingresses; output unknown | Not labelled Adhika. |
| `1822-12-20T00:00:00Z` | One interval has two ingresses; output unknown | Not labelled Kshaya. |
| `1719-03-01T00:00:00Z` | `PHALGUNA`; two relevant intervals with one ingress each | Pre-modern engine-safe ordinary runtime case, not source-certified. |

Around the observed 2025 solar-ingress and new-moon boundaries, the current
implementation retains its ordinary full-moon-based membership result. That
proves only its deterministic modern boundary behavior; it must not be read as
a source-approved sunrise, ingress, or tithi-boundary rule.

## Mode and product decision

The profile is **not presently eligible for Mode 1**. A future source-closed
ordinary-case contract could admit only its known ordinary cases while leaving
intercalary or boundary cases unknown, but that is not true today: both the
naming lookup and exact boundary rule remain inference/engineering layers.

The UI may continue to show the ordinary, clearly-labelled research result
already implemented. It must preserve `UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED`
at every unresolved edge. This report does not change any UI, endpoint, or
calculation behavior.

## Required source acquisition

The smallest remaining witness is a page-image-identified edition of *Surya
Siddhanta* capable of closing the exact passage cited by the held Brihat
Samhita translator note. The first certification packet must locate, rather
than presume, the passage covering Adhimasa/Avama, omitted or deficient
lunations, naming, lunation/Sankranti relation, and time/local-day standard.
The exact Surya Siddhanta chapter and verse remain `UNLOCATED_IN_UNHELD_SOURCE`.

That request is recorded in
`configs/research/cgvo/cgvo_calendar_r1_lunar_month_profile_v1.json`. No web
summary or modern panchanga convention may fill this gap.

## Verification and locks

The machine-readable R1 profile is parsed by the focused CGVO source-fixture
suite. It asserts the explicit Purnimanta inference, source-unclosed naming and
boundary states, separate Adhimasa/Avama/Kshaya handling, and the retained
fail-closed guard.

`priceDataRead=false`, `priceOutcomeRead=false`, `marketDirectionInferred=false`,
`fieldsPath=false`, `sbcPath=false`, `autoSuggestPath=false`, `mlPath=false`,
`mt5Path=false`, and `executionAllowed=false`.
