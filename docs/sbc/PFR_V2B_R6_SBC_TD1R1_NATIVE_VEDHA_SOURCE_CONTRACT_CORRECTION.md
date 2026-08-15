# PFR-V2B-R6-SBC-TD1R1 - Trailokya 1972 Native Vedha Source Contract Correction

## Purpose and Boundary

TD1R established the source-only architecture. Central source review then
identified transcription, canonical-token and locator defects in its machine
records. TD1R1 re-audits the controlling private 1972 scan, SHA-256
`1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`.
The 2016 reprint, SHA-256
`19CC2387C6C6B80E9A1F5A63BB9A71090A10FB17F3BD8BB56058210667F61ED8`,
is only a same-lineage reading witness.

This correction changes no runtime, UI, score, financial claim, price mapping,
Fields behavior, Auto Suggest, ML, MT5 or execution path. Private PDFs and
rendered page images remain outside Git.

## Re-audited Target Table

All 28 rows in printed pp.6-11 / scan pp.22-27 were checked against the
primary source. The corrected machine record includes verse, scan page,
printed page, ordered Vama/left targets, ordered Dakshina/right targets and
the one enumerated Sammukha/front target.

Four rows required adjudicated correction:

- `PUNARVASU`: the right list now ends with `PURVA_BHADRAPADA`; the source
  distinguishes left `ड` (`DDA_RETROFLEX`) from right `द` (`DA_DENTAL`).
- `PUSHYA`: the right list now ends with `SHATABHISHA` after `स`
  (`SA_DENTAL`).
- `ANURADHA`: the short `VISHAKHA` target is right/Dakshina; the larger
  `न`, Scorpio, Jaya, Rikta, Aries, `ल`, Bharani set is left/Vama.
- `JYESHTHA`: the left vowel is `ANUSVARA`, not `VISARGA`.

The exact golden map is asserted by
`test_trailokya_td1r1_source_correction.py`; it checks content, ordering,
direction, token identity and locators instead of only target-row counts.

## Lossless Token Identity

The source contract now exposes literal Devanagari, unambiguous canonical token
and normalized display for the machine-relevant aksharas. In particular it
does not collapse dental and retroflex consonants or the three sibilants:
`त/ट`, `द/ड`, `थ/ठ`, `ध/ढ`, `न/ण`, and `श/ष/स`.

Verse 48 now records the printed pairs `ब-व`, `श-स`, and `प-ख`. Verse 49
records `क -> घ,ङ,छ`; `प -> ष,ण,ठ`; `भ -> ध,फ,ढ`; and
`द -> थ,ज्ञ,ज`. Verse 51 explicitly retains `अं-अः` as its own pair.
Verse 52 retains the four corner-pada/Purna co-hits. These are semantic source
graph expansions that remain one causal Vedha event, never extra scores.

## Provenance and ASTA Correction

The correction audit records every rechecked TD1 locator. Most importantly,
the row table has individual printed-page fields, verse 48 begins on scan 27 /
printed p.11, verses 49-52 span scans 28-29 / printed pp.12-13, base nature
begins on scan 29 / p.13, the Moon passage spans scans 29-30 / pp.13-14, and
the Mars/Jupiter/Saturn relative-Sun material is scan 33 / p.17.

The source describes same-sign/combust `ASTA` context. It does not state that
ASTA has no Vedha direction. The current source contract therefore records
`ASTA` as an astronomical visibility state and
`UNKNOWN_NOT_SOURCE_ESTABLISHED` for Vedha direction.

## Remaining Fail-Closed Gaps

`TRAILOKYA_1972_STHULA_VEDHA_SOURCE_V1` remains
`SOURCE_CLOSED_WITH_EXPLICIT_FAIL_CLOSED_GAPS`. It still does not close an
instantaneous swift/mean threshold, stationary state, Shukla Panchami overlap,
modifier precedence, Latta, a completed reproducible Arghya calculation,
financial validation or execution readiness.

TD2 modifier/precedence translation may be proposed next, beginning with the
already mapped 1972 scan pp.52-62 / printed pp.36-46. It is not started here.
