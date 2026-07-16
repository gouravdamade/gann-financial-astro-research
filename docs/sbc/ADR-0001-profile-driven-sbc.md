# ADR-0001: Profile-Driven SBC Research

Status: accepted for Phase 0 and Phase 1

Date: 2026-07-17

## Context

Sarvatobhadra Chakra sources disagree on grid form, Abhijit treatment, Vedha
details, and later interpretive additions. Encoding one blended method would
hide these disagreements and make future results impossible to audit.

## Decision

1. Keep SBC in a separate Python package and configuration namespace.
2. Make Raman sidereal, geocentric, true-node astronomy the primary profile.
3. Keep Lahiri as an explicit comparison profile only.
4. Calculate Phase 1 facts with timezone-aware UTC input and record Swiss
   Ephemeris flags, mode, version, data-file path, and file hash when available.
5. Keep Abhijit inactive until a profile provides an interval and source rule.
6. Treat the 81-cell grid as an unselected candidate, not a default.
7. Do not implement grid, Vedha, Latta, scoring, market labels, or trades in
   Phase 1.
8. Require source fixtures, independent calculator comparison, deterministic
   tests, and out-of-sample market evaluation before promotion.
9. Expose any later Chakra Lab through Tauri IPC and keep it read-only until all
   relevant gates pass.

## Consequences

- The current release gains an auditable astronomy foundation but no new
  prediction feature.
- Source disagreements remain visible and can be compared profile by profile.
- Snapshot IDs are derived from scientific facts and profile hashes, not local
  file paths.
- Distribution cannot be promoted until Swiss Ephemeris licensing is resolved.
