# Prospective Refresh Live Lineage Audit

Audit time: 2026-07-13 12:49 IST
Refresh contract: `GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1`
Astronomy contract: `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`
Result: **PASS**

## Scope

This audit checks the first seven real automatic H1 refresh cycles after the market
resumed. It verifies operational provenance only. It does not certify astrological
doctrine, predictive value, or trading profitability.

| Closed H1 bar UTC | Run | Corrected artifact | Events | Touches | Result |
|---|---|---|---:|---:|---|
| 2026-07-13 01:00 | `8c2012d8` | `tn_009cf0b0c95d4b5dab30c7f7beb3578e` | 37 | 12 | PASS |
| 2026-07-13 02:00 | `20281421` | `tn_b2a108ae0855421893e1a146e1e57f32` | 37 | 12 | PASS |
| 2026-07-13 03:00 | `86d65f70` | `tn_b59dd0011e044afe9e4b36720e38ba55` | 38 | 12 | PASS |
| 2026-07-13 04:00 | `d7f12f7c` | `tn_cafd0d1fdfac46819b43e6a628c215cf` | 39 | 15 | PASS |
| 2026-07-13 05:00 | `71e77fc8` | `tn_0ed7168baa6c4c55a93e243820bb82c5` | 39 | 16 | PASS |
| 2026-07-13 06:00 | `9d7cf65f` | `tn_eee473aee344413aa9c4c87d81525328` | 39 | 16 | PASS |
| 2026-07-13 07:00 | `3a37f6a0` | `tn_53277139e4354e54bbff9a28e5b2b12c` | 39 | 17 | PASS |

## Checks

Each run passed the same 14 assertions, for 98 passing checks in total:

1. source snapshot manifest SHA-256;
2. source snapshot parquet SHA-256;
3. promoted price parquet SHA-256;
4. byte identity between snapshot and promoted price source;
5. completed run parameters equal verified artifact parameters;
6. snapshot, run, and artifact carry the same closed-bar cutoff;
7. artifact carries the registered price-source ID and SHA-256;
8. generated event parquet SHA-256;
9. generated touch CSV SHA-256;
10. event count agrees across file, registry, and manifest;
11. touch count agrees across file, registry, and manifest;
12. event and artifact manifests exclude outcome labels;
13. prospective refresh metadata keeps execution disabled;
14. artifact refresh run ID equals the durable run record.

## Audit Repair

The generated artifacts were correct, but the original supervisor persisted inherited
provenance fields in four completed run audit rows. That did not alter generation,
activation, market data, events, touches, or shadow decisions, but it made the run record
misleading. Version `0.6.0` now:

- writes the current promoted price-source contract, SHA-256, capture time, and closed-bar
  cutoff before queueing generation;
- replaces a completed run's parameters with the verified artifact parameters;
- repairs older completed rows on startup only when artifact ID, refresh run ID,
  source-bar close, and price-source ID all prove the same lineage.

After the guarded startup repair, all seven durable run records passed the 98-check audit.

## Runtime State

- latest verified closed H1 bar: `2026-07-13T07:00:00+00:00`;
- refresh state: `up_to_date`;
- active artifact: `tn_53277139e4354e54bbff9a28e5b2b12c`;
- append-only shadow chain: valid, 7 decisions, all outcomes still pending;
- MT5: connected, market-data only;
- artifact refresh, shadow ledger, local Jyotish, and Codex surfaces: no order execution.
