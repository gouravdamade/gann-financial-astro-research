# CGVO-S1 Source Closure Report

Status: `IMPLEMENTED_FOR_CENTRAL_REVIEW`
Milestone: `CGVO-S1A`

## What is source-closed

The adapter records the 12-sign fixed stellar partition from Bṛhat Saṃhitā CII.1-7 and the precessional distinction in III.1-3. It stores the Chitra/Spica-at-180-degree proposal separately as `SOURCE_RECONSTRUCTION_CANDIDATE`; it is not called an ayanamsha and is never chosen by default.

The eclipse aspect adapter uses only categorical sign-relative counting. Ordinary 3rd/10th, 5th/9th, 4th/8th, and 7th relations produce fractions `0.25`, `0.50`, `0.75`, and `1.00`, with the source-recorded special full aspects for Saturn, Jupiter, and Mars. The result includes literal effect tokens but has `effectMagnitudeMultiplier=null` and `jupiterMitigationCoefficient=null`.

## What remains intentionally unresolved

- The lunar profile is ordinary purnimanta only. Adhika, kshaya, double-month, unresolved boundary, and unimplemented cases remain `UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED`.
- Bṛhat Saṃhitā V.28-31 does not source-close a firmament section classifier. The workbench shows raw apparent altitude, normalized/raw azimuth, local hour angle, rise/set state, and meridian relation, but `classicalSection=UNKNOWN`.
- Commentary six- and seven-section candidates are retained as comparison provenance, not as a classifier.

## Product checks

The CGVO workbench now has an explicit Varahamihira absolute-frame control, source-status panels for frame/month/aspects/firmament, and a typed JSON failure for an invalid requested absolute frame. Existing P1R1 modern local eclipse calculations are reused; no second eclipse engine was added.

No market, polarity, score, forecast, Fields, SBC, Auto Suggest, ML, MT5, or execution path is introduced. `executionAllowed=false` remains invariant.
