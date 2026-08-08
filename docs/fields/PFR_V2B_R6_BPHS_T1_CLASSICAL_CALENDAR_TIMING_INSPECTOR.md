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
Packet 1W / printed pages 197-236, file SHA-256
`BB556804D8D546ACC39C43A22CECDBE2C29E3A7BA157E60EEC810C478EB645A4`.

The deterministic interval boundaries are calculated by the separately
labelled `SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1` engineering profile.
This is not a claim that a Swiss-Ephemeris implementation is printed BPHS
doctrine.

Tara is explicitly `DEPENDENCY_NOT_READY` without both a reference input and a
page-transcribed mapping. Muhurta names/order are likewise marked partial until
the exact source table is transcribed. No missing doctrine is filled by an LLM.

## Guardrails

All returned payloads state and are tested for: no market or price read, no
future return read, no polarity catalogue path, no pair-relative field path, no
Founder Review path, no SBC path, no Auto Suggest/ML path, no scoring, and no
execution or automatic order path.

The panel uses neutral category colours. It has no supportive/adverse state,
numeric magnitude, confidence, score, market direction, or trade suggestion.
