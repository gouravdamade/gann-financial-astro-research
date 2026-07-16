# SBC Phase 1 Foundation Acceptance Report

Date: 2026-07-17 IST

Status: accepted as an isolated deterministic research foundation

## Scope Delivered

- strict source register and profile compiler
- Raman primary and Lahiri comparison profiles
- timezone-aware Swiss Ephemeris positions with longitude, latitude, distance,
  speed, requested/returned flags, calculation mode, file path, and file hash
- explicit true/mean node contract and Ketu = Rahu + 180 degrees provenance
- 27-fold nakshatra and pada boundaries
- source-profiled Abhijit policy with no default interval
- tithi, paksha, tithi group, karana, yoga, and Vara
- civil-midnight and Swiss Ephemeris sunrise Vara contracts
- stable scientific snapshot IDs
- hard locks for grid, Vedha, Latta, scoring, trades, market data, Auto Suggest,
  and MT5 execution

## Test Evidence

- Focused SBC suite: 18 passed in 4.09 seconds.
- Combined existing astronomy/Shadbala plus SBC regression suite: 32 passed in
  3.90 seconds.
- Full repository suite, with every root and research-lab test file explicitly
  enumerated: 97 passed in 9.87 seconds.
- `git diff --check`: no whitespace errors.

## Deterministic Sample

Input:

- UTC: `2026-07-17T06:30:00+00:00`
- location: Delhi, `28.6139, 77.2090`, altitude 216 m
- timezone: `Asia/Kolkata`
- profile: `sbc_raman_foundation_v1`
- bodies: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu

Result:

- snapshot ID: `6C49401FFF48182086E7F6F2D95CD356D5EFC6AC27C5693D6C1C4561424048DC`
- astronomy contract: `SBC_RAMAN_TRUE_NODE_SWISSEPH_FOUNDATION_V1`
- all nine returned calculations: `SWISSEPH`
- Panchanga sample: Chaturthi, Moon in Magha, Friday
- Sun file: `sepl_18.se1`, SHA-256
  `0B7E416E3C1BE9E6A0DD1D711DAE7F7685793A0E7DF13F76363A493DC27B6EA1`
- Moon file: `semo_18.se1`, SHA-256
  `ECFA54DBF5BC0B5A9BC3E04ED28629A821E98625EACAE38F4070593BBA0E2980`
- Swiss Ephemeris library version: `20230604`

## Not Certified

This report does not certify a Sarvatobhadra grid, Abhijit interval, Vedha,
Latta, directional meaning, financial edge, or trade logic. Those layers remain
blocked by source plurality and missing fixtures. Swiss Ephemeris distribution
licensing also remains a Windows-release gate.

## Recommended Next Gate

Acquire and page-certify the chosen traditional SBC editions, then create
golden fixtures for the competing 64-cell and 81-cell grid profiles. Only after
those fixtures agree with at least one independent calculator should a read-only
Chakra Lab be added to the desktop app.
