# MO-R4A-S3R1-R2 Dukascopy Provider Protocol Closure

## Result

R2 is a fail-closed Branch B successor. It did not contact a provider or read a market outcome. Dukascopy's current technical page source-closes daily S3 partitioning, the 20-byte record layout, UTC-day offsets, and USDJPY's 1000 divisor. The same page conflicts on the exact LZMA wrapper/filter contract, so no parser or future outcome acquisition is authorized.

## Provider Decision

Selected product: `DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE`. The daily native request identity is `s3://cfg-public-proper-wallaby/USDJPY/YYYY/MM/DD_ticks.bi5` in `eu-west-1` with `RequestPayer=requester`; `MM` is zero-indexed. JForex inclusive time-range history is expressly not mixed into this raw-object contract.

| Question | Final answer | Source tier | Exact source | Confidence/status |
| --- | --- | --- | --- | --- |
| Provider product | DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE | Tier 1 | https://www.dukascopy.com/wiki/es/development/data-export/ | SOURCE_CLOSED |
| Partition granularity | UTC daily .bi5 object | Tier 1 | Current export page lines 579-591 | SOURCE_CLOSED |
| Path/request syntax | USDJPY/YYYY/MM/DD_ticks.bi5; S3 requester-pays | Tier 1 | Current export page lines 584-591, 800-819 | SOURCE_CLOSED |
| Compression | LZMA named, exact wrapper/filter not source-closed | Tier 1 | Current export page lines 582, 629, 692, 768 | PROTOCOL_SOURCE_CONFLICT |
| Record size and byte order | 20 bytes, big endian | Tier 1 | Current export page lines 592-601 | SOURCE_CLOSED |
| Timestamp | uint32 milliseconds from UTC day start | Tier 1 | Current export page lines 597, 637-650 | SOURCE_CLOSED |
| Ask/bid and volumes | uint32 ask, uint32 bid, float32 volumes | Tier 1 | Current export page lines 598-601 | SOURCE_CLOSED |
| USDJPY scale | native integer divided by 1000 | Tier 1 | Current export page lines 602-608, 668-679 | SOURCE_CLOSED |
| Missing partition | documented missing daily key means no ticks | Tier 1 | Current export page lines 589-591 | SOURCE_CLOSED |
| Empty payload | zero-byte success is acquisition-incomplete | Project policy | R2 contract | FAIL_CLOSED |
| Request boundary semantics | whole UTC days; local scientific filter remains half-open | Project policy | R2 contract | FROZEN |
| Retry policy | one attempt, no automatic retry | Project policy | R2 contract | FROZEN |
| Revision policy | differing successful raw hashes cause conflict | Project policy | R2 contract | FROZEN |

## Native Partition Plan

The 39 frozen analytical windows (13 actual, 13 minus seven days, 13 plus seven days) map to `15` unique UTC daily partitions. Shared daily partitions appear once and carry every covered analytical interval ID. The plan contains no response-existence or market-value data.

## Parser Boundary

An offline parser is deliberately **not** implemented. The evidence calls the files raw LZMA outside .xz while showing `lzma.decompress` without raw filter parameters. Without a provider-issued wrapper/filter specification, any parser choice would be an unsupported convention. If clarified, the future parser must reject non-20-byte alignment, timestamps outside its native day, nonpositive bid, ask below bid, identical-duplicate ambiguity, and conflicting same-timestamp quotes.

## Hash Chain And Invariance

Historical R1 acquisition remains `D2E78CECD9743A176E417ACD7A7EAD57EC21167B8708AF2043C9D016E0C2CD70`. R2 acquisition is `A1C2129E9395C9850A66A595F3529563AFBDA14E10C8F0B7DBB3A78897ECF500`; protocol lock is `394AE5B524C6090199040BA8201C384DD4AF000FDE72ED9880753DBB7736B3C3`; partition plan is `5C39D983DD11288B24ABCF0E17F38C862A6B3B283CC68ABC3377C3324BBD738D`; preregistration is `BAF10DF4B71D53361B07F417752864EF26F7BEC5572EA4DAB71F5287C1959DF5`; R2 core is `3C28D0A0C21FED0C9C295F76B23E5EFBA9FEB0CCA54B89484D2B8E489AFE5AF1`; acceptance is `6952B8AAE0AEABDBD7CB2324F4E674D12BC712EA239883C730E669DB782923FB`.

The scientific plan remains unchanged: 24 frozen identities, 13 primary rows, the 40-state conditional null, 39 frozen windows, four clusters, and the original midpoint/return/zero/timing rules. This package contains no market return, hit, p-value, timing result, or real payload hash.

## Gate

Acceptance is `S3R1_R2_PROVIDER_PROTOCOL_INCOMPLETE_OUTCOME_UNLOCK_BLOCKED` with next gate `CENTRAL_REVIEW_PROVIDER_PROTOCOL_GAP`. `providerAccessPerformed=false`, `marketOutcomeRead=false`, all 16 outcome access flags are false, and `executionAllowed=false`. A targeted Astra audit is not ready while the official compression conflict remains unresolved.
