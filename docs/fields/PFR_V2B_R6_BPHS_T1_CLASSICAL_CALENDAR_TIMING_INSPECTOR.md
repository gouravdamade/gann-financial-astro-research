# PFR-V2B-R6-BPHS-T1 - BPHS 1899 Classical Calendar Timing Inspector

## Scope

This bounded milestone adds a read-only `BPHS Classical Calendar` section to
the dedicated Fields workspace. The founder enables it with the separate
`Classical timing: Off | BPHS 1899 Research` control. It is not an SBC/Vedha
profile and does not change existing source-profile selection.

The endpoint `POST /api/research/bphs/classical-calendar-range` accepts only
UTC range, local timezone, location, the explicit BPHS profile ID, and an
optional Tara reference object. It returns chronological half-open intervals
containing Muhurta day/night index, Tithi, Nakshatra, Yoga, Karana, Weekday and
Tara availability.

## Evidence and calculation boundary

The source profile is `BPHS_1899_CLASSICAL_CALENDAR_RESEARCH_V1` using
`BPHS_1899_GOVIND_SHARMA_SHASTRI`, 1899 Purva/Uttara witness, Chapter 14 /
Packet 1W, file SHA-256
`BB556804D8D546ACC39C43A22CECDBE2C29E3A7BA157E60EEC810C478EB645A4`.

The deterministic interval boundaries are calculated by the separately
labelled `SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1` engineering profile.
This is not a claim that a Swiss-Ephemeris implementation is printed BPHS
doctrine.

## Packet 1W source audit and bounded corrections

The 15 daytime and 15 nighttime Muhurta rows are transcribed in
`research_labs/bphs_1899_classical_timing/bphs_1899_packet_1w_muhurta_fixture.json`.
Two independent passes, Sanskrit commentary and Hindi Bhasha, agree at printed
page 197 / PDF image 680. The live UI therefore displays the source name while
retaining period and index, for example `DAY MUHURTA 01 - Ardra`. Repeated rows
remain repeated and the source-literal nighttime `Uttara` is not expanded.
The fixture also records the supporting Sanskrit root-text continuation over
printed pages 196-197 / PDF images 679-680; it is retained as evidence rather
than used to normalize the two complete enumerations.

The source confirms 15 daytime and 15 nighttime segments, but the live
sunrise/sunset segmentation is still explicitly supplied by
`SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1`; this is not represented as a
literal BPHS boundary formula.

The held Packet 1W witness does not close civil-midnight versus sunrise/day
weekday ownership. The lane is therefore labelled `Civil weekday (engineering)`
with `BPHS_1899_WEEKDAY_BOUNDARY_NOT_CLOSED`, not displayed as literal BPHS
doctrine.

Tara is explicitly `DEPENDENCY_NOT_READY`. The P3 held-witness audit confirms
that the Chapter 14 range (printed pp. 196-258 / PDF images 679-741; Chapter
15 begins at printed p. 259 / PDF image 742) does not supply the operational
relation. A separate Tara Dasha passage at printed p. 254 / PDF image 283 and
an Atimitra occurrence in a Lakshmi-yoga passage at printed p. 234 / PDF image
717 are not treated as the missing ninefold relation. The source does not
close the sequence, reference/target objects, counting/reduction rule,
27/28/Abhijit treatment, or product reference identity. No missing doctrine is
filled by an LLM or a modern Panchanga source. See
`PFR_V2B_R6_BPHS_T1R_P3_TARA_SOURCE_CLOSURE.md`.

Tithi, Nakshatra, Yoga and Karana remain `ENGINEERING_CALCULATED`. The source
citation for those lanes is intentionally only chapter-level calendar-category
context. It does not claim that each displayed name or transition boundary has
been individually page-transcribed from BPHS.

## Guardrails

All returned payloads state and are tested for: no market or price read, no
future return read, no polarity catalogue path, no pair-relative field path, no
Founder Review path, no SBC path, no Auto Suggest/ML path, no scoring, and no
execution or automatic order path.

The panel uses neutral category colours. It has no supportive/adverse state,
numeric magnitude, confidence, score, market direction, or trade suggestion.

## Founder-inspection candidate

`0.10.38-pfr-v2b-r6-bphs-t1r` is rejected before founder review because its
frozen Python sidecar omitted the Packet 1W fixture. The replacement,
`0.10.39-pfr-v2b-r6-bphs-t1r-p1`, is built from source commit
`9772277991c3ce3715bb0c6cb11c5890bd094369` and checks that the fixture exists
under the bundled `_internal/research_labs/bphs_1899_classical_timing` root.

The portable executable and NSIS installer are founder-inspection artifacts,
not a stable promotion or proof of classical/financial validity. The candidate
report records hashes, clean-source declaration, test results, portable smoke
evidence, and the manual visual checklist.
