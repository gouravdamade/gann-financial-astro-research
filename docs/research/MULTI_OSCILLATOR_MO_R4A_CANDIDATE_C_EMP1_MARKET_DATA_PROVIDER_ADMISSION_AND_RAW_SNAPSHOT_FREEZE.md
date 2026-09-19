# Candidate C EMP1 Market-Data Provider Admission And Raw Snapshot Freeze

## Scope

EMP1 is a market-data/provenance phase for the frozen Candidate C R3-R1
empirical contract. It admits one USDJPY spot bid/ask dataset, preserves its
provider bytes, renders a canonical R3-R1 market snapshot, validates that
snapshot and its admission record, and stops. It does not evaluate a Candidate
C event against market data.

The predecessor R3-R1 freeze is `493dae64766ae7a7dd0fafcf7fc3207d8f1ea8bc`.
The protected R3-R1 runtime identity remains
`74D2C4FEBB027BC2E42AF50713EDDA2CC380345184EFF3E176D3CB55F57C227E`.

## Provider Admission

The admitted provider is Dukascopy's requester-pays daily BI5 product:

```text
DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE
DUKASCOPY_USDJPY_DAILY_TICKS_BI5
FX_SPOT_USDJPY
```

The fixed acquisition route is the `cfg-public-proper-wallaby` S3 bucket in
`eu-west-1`, using `RequestPayer=requester` and the documented zero-indexed
month key form `USDJPY/YYYY/MM/DD_ticks.bi5`. Thus `USDJPY/2025/04/01_ticks.bi5`
is 2025-05-01 UTC and `USDJPY/2025/07/01_ticks.bi5` is 2025-08-01 UTC.

Provider documentation retained in the evaluation record identifies the daily
BI5 export convention, historical tick availability, and tick bid/ask fields:

- https://www.dukascopy.com/wiki/en/development/data-export/
- https://www.dukascopy.com/wiki/en/development/strategy-api/historical-data/overview-historical-data/
- https://www.dukascopy.com/client/javadoc/com/dukascopy/api/LoadingDataListener.html

The raw provider redistribution permission was not established. Accordingly,
raw BI5 bytes and the full provider-derived quote snapshot are retained only in
the durable private source store and are not committed to Git. The committed
records contain only storage contracts, non-price provenance, byte counts, and
SHA-256 identities.

## Raw Evidence

The frozen temporal dataset scope is unchanged:

```text
2025-05-01T01:58:38Z through 2025-08-01T23:20:56Z
```

EMP1 accounted for 93 calendar partitions: 80 raw daily BI5 objects and 13
documented Saturday FX-market closures. All successful objects were preserved
byte-for-byte and have uppercase SHA-256 identities in
`mo_r4a_candidate_c_emp1_raw_market_artifact_inventory_v1.json`.

The terminal partition identity remains:

```text
USDJPY/2025/07/01_ticks.bi5
612289 bytes
29832ACCB5AB05F9BC5CC46F2A4E9DC7A2AA10A000CBB532C6517CE9D7E9E968
```

Its final quote was `2025-08-01T20:59:54.038Z`. The interval from the documented
Friday market close `2025-08-01T21:00:00Z` through the declared coverage end is
recorded as `DOCUMENTED_MARKET_CLOSED`, not as missing provider data and never
as an imputed quote.

## Canonical Snapshot And Quality

The private canonical snapshot uses the unchanged R3-R1 structure and self-hash
convention. It binds 80 raw artifacts and has:

| Property | Value |
| --- | --- |
| Snapshot hash | `0F04578F8BB9FE08558889B3BBAC50F19DCE6702093856842B8A12ED32ACCEEC` |
| Declared coverage | frozen 2025-05-01 through 2025-08-01 UTC interval |
| Timezone | UTC |
| Resolution | 1 second contract value; original ticks retain millisecond timestamps |
| Raw parsed quotes | 7,888,953 |
| Admitted canonical quotes | 7,880,695 |
| First observed quote | 2025-05-01T00:00:00.021000Z |
| Last observed quote | 2025-08-01T20:59:54.038000Z |
| Exact duplicates | 0 |
| Conflicting duplicates | 0 |
| Invalid timestamps | 0 |
| Invalid bid/ask rows | 0 |

The 8,258 raw observations before the static declared coverage start are
preserved in their raw daily provider artifact but are outside the admitted
canonical snapshot interval. No event timestamp, source state, or outcome was
used for that deterministic calendar-boundary filter.

There were 762 observed market-only inter-quote intervals above 60 seconds.
They are reported as tick-cadence observations, not silently relabelled as
provider outages or closed-market intervals. There are zero absent or malformed
open-session daily partitions in the admitted corpus. The documented closure
record remains separate from those observations.

Frozen `validate_market_snapshot(...)` passed. The exact R3-R1 admission record
also passed `validate_market_admission_record(...)` with hash:

```text
2EC34D56151E18CE17FC13F47CFB95007B9FDA86BF5F59B3416D65AF9455160A
```

## Faithful Transformation

The market-only rendering performs only the provider-format transformations
already bound by the Dukascopy parser contract:

1. LZMA daily BI5 decompression.
2. Big-endian 20-byte record decoding.
3. UTC-day millisecond offset to ISO-8601 UTC timestamp.
4. Native USDJPY ask and bid integers divided by 1000.
5. Static inclusion within the frozen declared temporal coverage.

It does not resample, average, smooth, synthesize bars, fill missing periods,
create a weekend price, or alter a provider quote.

## Boundary And Gate

`marketOutcomeDataPresent=true` only in the broad sense that the private raw
market dataset now exists. `marketOutcomeAnalyzedAgainstCandidateC=false`.

The following remain false: source-market join, Candidate C event-time quote
availability, P0, PH, return calculation, source-state-conditioned market
inspection, statistics, permutations, p-values, Holm, BH, empirical execution
authorization, EMP2 execution, market direction, USD/JPY sign mapping, source
weights, pair field construction, and `executionAllowed`.

EMP1 is frozen at:

```text
CENTRAL_REVIEW_CANDIDATE_C_EMP1_MARKET_DATA_PROVIDER_ADMISSION_AND_RAW_SNAPSHOT_FREEZE
```
