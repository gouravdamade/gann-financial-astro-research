# PFR-V2B-R6-SBC-A1R1: Agarwal 2000 Complete Capture Gate and Page-Level Extraction

## Scope and boundary

This is a source-extraction milestone for the founder-held M. K. Agarwal,
Sagar Publications, New Delhi, First Edition 2000. It does not implement an
Agarwal engine, a polarity model, a score, a price rule, Auto Suggest, an ML
label, MT5 behavior, or execution.

All page images remain private. The repository contains only checksums, compact
transcription records, page locators, and research status.

## Capture gate

| Capture | PDF pages | SHA-256 verification |
| --- | ---: | --- |
| `Agarwal_front.pdf` | 7 | verified |
| `44-48.pdf` | 4 | verified |
| `52-59.pdf` | 8 | verified |
| `60-64.pdf` | 5 | verified |
| `130-136.pdf` | 7 | verified |
| `140-146.pdf` | 6 | verified |

The all-capture gate is now `ALL_6_CAPTURE_FILES_HASH_VERIFIED_20260814`.
Neither the private PDFs nor page renderings are tracked.

## Overlap reconciliation

The physical pages were compared against the old scan only where both contain
the same printed page. The check is page-specific: matching headers, pagination,
table structure, and readable text were required. It does not convert the old
scan into a complete or controlling book witness.

| Printed pages | Result | Notes |
| --- | --- | --- |
| 44-45 | `MATCH` | Planet-signification continuation and Chapter 6 transition agree. |
| 46-47 | `NOT_COMPARABLE` | Absent from the old scan; hardcopy controls. |
| 52-53 | `MATCH` | Sign chapter pagination and content agree. |
| 54-55 | `NOT_COMPARABLE` | Absent from the old scan; hardcopy controls. |
| 56-59 | `MATCH` | Numerical-strength continuation agrees. |
| 60-61 | `MATCH` | Shadbala chapter opening and rows agree. |
| 62-63 | `NOT_COMPARABLE` | Absent from the old scan; hardcopy controls. |
| 64 | `MATCH` | Chapter 9 transition agrees. |
| 130-132 | `MATCH` | Chapter 16 transition and surrounding content agree. |
| 133 | `NOT_COMPARABLE` | Absent from the old scan; hardcopy controls. |
| 134-136 | `MATCH` | Chapter 17 transition and continuation agree. |
| 140-143 | `MATCH` | Surrounding Chapter 17 content agrees. |
| 144 | `NOT_COMPARABLE` | Absent from the old scan; hardcopy controls. |
| 145-146 spread | `MATCH` | The author figure's visible orientation and layers agree; exact folded small-cell readings remain unresolved. |

No `CONTENT_VARIANT` was found in the inspected overlaps. ChiStaBo was never
used to fill an absent source page.

## Numerical-strength evidence

`configs/sbc/evidence_packets/agarwal_2000_strength_two_pass_v1.yaml` records
two fresh visual passes for the p.54-55 numerical sign/longitude tables and the
visible pp.60-63 general-strength rows. The passes agree for each admitted
numeric entry. They prove what this edition prints, not that the entries can be
summed, converted to a financial signal, or substituted for the current strict
Shadbala implementation.

The fixture deliberately leaves these points partial: aggregation order,
condition-boundary definition, duplicate-condition handling, and a verified
worked numerical example.

## Geometry and operator findings

Printed p.144 closes the listed varga-number allocation groups. The pp.145-146
author figure visibly closes figure-relative cardinal labels and shows the
multiple layer types, including Abhijit. The center/fold and small labels do not
close a complete machine cell map, therefore `UNKNOWN_CENTER_FOLD` is retained.

Chapter 9 provides a source-closed direction-by-motion statement on printed
p.65. It does not close numerical definitions for fast versus normal motion,
target-cell resolution, rule precedence, exceptions/cancellation, or all inputs
needed to reproduce the author's process. `AGARWAL_SBC_2000_SOURCE_V1` remains
uncreated and `AGARWAL_VEDHA_OPERATOR_READY` remains false.

## Printed p.133

Printed p.133 is recorded as `DESCRIPTIVE_ONLY`. Its human/caste-specific
outcome material is prohibited from any market, USD/JPY, polarity, score, ML,
Auto Suggest, or execution conversion.

## Chapter 20

`configs/sbc/evidence_packets/agarwal_financial_sbc_v1_hypothesis_ledger.yaml`
contains a page-level ledger for printed pp.180-194. Every row is classified
`FINANCIAL_HYPOTHESIS`, applies to the author's share-market framing, and has
explicit prohibitions against FX generalization and every live product path.

## Three-profile comparison

| Property | Phaladeepika editor supplement | Trailokya Dipika 1972 | Agarwal First Edition 2000 | Status |
| --- | --- | --- | --- | --- |
| Board orientation | separate source profile | figure-relative source profile | EAST/NORTH/SOUTH/WEST visible in author figure | `NOT_COMPARABLE` beyond the recorded Agarwal figure facts |
| 81-cell/full geometry | executable source-specific fixture | source-only geometry fixture | incomplete machine cell admission due fold | `PARTIAL_OVERLAP` |
| Nakshatra/Abhijit layer | profile-specific | profile-specific | visibly includes Abhijit | `PARTIAL_OVERLAP` |
| Letter layers | source-specific | source-specific | vowels/consonants allocated on p.144 | `PARTIAL_OVERLAP` |
| Direction/motion rules | editor supplement | certified Trailokya profile | p.65 direction-by-motion wording | `DIFFERS` / no harmonization |
| Planetary nature/modifiers | source-specific material | pending/limited source-only treatment | strength/nature wording visible, full operator partial | `NOT_COMPARABLE` |
| Strength system | separate existing implementation evidence | not this profile's strength system | pp.54-55 and 60-63 fixture | `SOURCE_ONLY_IN_AGARWAL` |
| Financial material | no Agarwal Chapter 20 equivalent | Arghya lab remains locked | Chapter 20 hypothesis ledger | `SOURCE_ONLY_IN_AGARWAL` |

The matrix describes source separation; it neither votes nor combines rules.

## Readiness decision

- `AGARWAL_EDITION_READY = true`
- `AGARWAL_COMPOSITE_SOURCE_READY = true`
- `AGARWAL_STRENGTH_READY = true` for source-record purposes only
- `AGARWAL_FINANCIAL_HYPOTHESIS_READY = true` for locked ledger purposes only
- `AGARWAL_GEOMETRY_READY = false`
- `AGARWAL_VEDHA_OPERATOR_READY = false`
- `AGARWAL_A2_READY = false`

The smallest remaining source dependency is a source-closed full geometry cell
map plus the missing executable Vedha-operator dependencies. No A2 user
interface work is authorized by this report.

## A1R2 follow-on

`PFR-V2B-R6-SBC-A1R2` performed the permitted figure-capture search and the
book-wide Chapter 9 operator audit. No newer authenticated flat or centre-fold
capture of pp.145-146 was found. The author figure therefore remains partial;
the new audit records the source-closed star/sign target table and other
literal operator facts while preserving the missing board-cell, state-order,
precedence, cancellation and validity dependencies. See
`docs/sbc/PFR_V2B_R6_SBC_A1R2_GEOMETRY_AND_VEDHA_SOURCE_CLOSURE.md`.
