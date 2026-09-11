# MO-R4A-S3R1-R3-R1 Adjudication Qualification And Schema Reconciliation

## Central Review Findings

R3 remains historical at `0F8F61572764E898F1D3F0E8676412A3770A45920FCFCB6A0AEDD9126C88855B`. Its cross-source elimination reasoning is retained, but its provider-framing certainty is qualified. The current official Dukascopy material does not directly name `lzma.FORMAT_ALONE`; no stronger provider-owned evidence was found. The active state is `FORMAT_ALONE_PLAUSIBLE_CROSS_SOURCE_RECONCILIATION_AWAITING_INDEPENDENT_ASTRA_DISPOSITION`.

## Evidence Classification

Branch: `BRANCH_B_PLAUSIBLE_CROSS_SOURCE_RECONCILIATION`. Direct provider facts, direct runtime facts, and cross-source technical reconciliation are separated below.

| Claim | Evidence class | Source | Supported | Interpretive step | Residual uncertainty |
| --- | --- | --- | --- | --- | --- |
| Dukascopy excludes XZ | DIRECT_PROVIDER_FACT | DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_ES | True | None; provider prose excludes the .xz container. | The natural-language raw-LZMA wording does not name a Python framing constant. |
| Official sample uses default lzma.decompress | DIRECT_PROVIDER_FACT | DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_ES | True | The sample supplies no format or filter chain. | The sample does not explicitly identify FORMAT_ALONE. |
| Python default equals FORMAT_AUTO | DIRECT_RUNTIME_FACT | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | True | None; this is the documented function default. | Runtime semantics do not establish provider intent. |
| FORMAT_AUTO accepts XZ and legacy LZMA | DIRECT_RUNTIME_FACT | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | True | None; this is the documented format detection behavior. | XZ is independently excluded by the provider wording. |
| FORMAT_AUTO rejects RAW | DIRECT_RUNTIME_FACT | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | True | None; raw mode needs an explicit filter chain. | Provider natural-language raw does not necessarily mean Python FORMAT_RAW. |
| FORMAT_ALONE is the legacy .lzma container | DIRECT_RUNTIME_FACT | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | True | None; this is the documented runtime meaning. | No provider-owned source directly maps BI5 to FORMAT_ALONE. |
| Dukascopy directly names FORMAT_ALONE | DIRECT_PROVIDER_FACT | OFFICIAL_DUKASCOPY_DOCUMENTATION_SEARCH | False | No direct provider statement was found in the searched official material. | Provider framing identity remains unclosed pending Astra or stronger source evidence. |
| FORMAT_ALONE remains the operational candidate | CROSS_SOURCE_TECHNICAL_RECONCILIATION | DUKASCOPY_AND_PYTHON_DOCUMENTATION | True | Retain the only candidate compatible with the current exclusion/default reasoning. | This is not unique provider-source closure. |

No searched official Dukascopy source directly names `FORMAT_ALONE`. The natural-language phrase raw LZMA is not equated with Python `FORMAT_RAW`. `PYTHON_LZMA_FORMAT_ALONE` remains the single frozen operational candidate, but `providerFramingUniquelySourceClosed=false`.

## Canonical Parsed-Tick Schema

The R3 acquisition artifact used the inconsistent fields `['timestampUtc', 'bidNative', 'askNative', 'bidVolumeMillionsBaseCurrency', 'askVolumeMillionsBaseCurrency', 'recordIndex']` and serialization `UTF8_JSON_LINES_SORTED_KEYS_ONE_OBJECT_PER_CANONICAL_TICK_TRAILING_LF`.
The R3-R1 acquisition successor now declares exactly `['partitionId', 'recordIndex', 'timestampUtc', 'askNative', 'bidNative', 'askVolumeBitsHex', 'bidVolumeBitsHex']` under `canonicalParsedTickHashRecord`.
Serialization is `UTF8_JSON_LINES_SORTED_KEYS_NO_INSIGNIFICANT_WHITESPACE_ONE_RECORD_PER_LINE_TRAILING_LF` with timestamp `YYYY-MM-DDTHH:MM:SS.mmmZ` and `SHA256_OF_CANONICAL_UTF8_JSON_LINES`.
Decoded float volumes remain available only as non-canonical inspection fields and are explicitly excluded from `parsedTicksSha256`.
The future S4 manifest keeps `rawSha256`, `parserContractHash`, `parserSourceSha256`, `parsedRecordCount`, `parsedTicksSha256`, `firstTimestampUtc`, and `lastTimestampUtc`; its parsed hash points to `canonicalParsedTickHashRecord`.

## Parser And Science

Parser source is unchanged at `47BEF7B1A13D8EE4EC2DDED2BDD965A27D41FCB548EC0D4D940A5535669D733E`. Parser contract is reused unchanged at `C91A76165893BCA308FE2DB9B3F83A2E9B0233CF2023E1AC573504C68EC3D316`. No fallback format, trial decompression, filter guessing, provider access, or real payload validation was added.
The 24 identities, 14 directional rows, 13 primary rows, 39 analytical windows, 15 native daily partitions, C1-C4 clusters, and 40-state within-side permutation universe remain unchanged. The R3-R1 invariance audit is `BE8CCF0C8A65323320911816DF22980F88F134C307577C8ABF0A218246103D4A`.

## Lineage Hashes

R3-R1 adjudication `EB8F0D67FB2EA1AF478E37EA523796ED9F0D9D4813AFDED34A419800816E2398`; source lock `3554E19DFEEEB0BA7DB323F4D418A60BFD1FF5D6D4836413FC3814BEC2FD29CD`; acquisition `FACB0D59A584CBC45560788F1CB1C21AD5E0994215B5B71DA841D255BA76E502`; preregistration `5781D2104807FA384BC257EF8FE7A48B5DC3F20DCE59C5360D7C4A1DAA283224`; population `20CEFBDAC6433026073F9771ACDCEFF220E6317F2D193DFB1C5DFD6786131F05`; clusters `ACF3A6DBD1E602951B54C9E844804BB6A439EC8D4B00E2EDCCAF9AC2B9C276E7`; invariance `BE8CCF0C8A65323320911816DF22980F88F134C307577C8ABF0A218246103D4A`; core `1CF3D566A9810CEDA708AFF4D6505BC0906970C2888B7161F5607432037EE792`; acceptance `27A39E5B63350B05728E86DACDE8335ED6CCD2A7FBDFD4399EF55472A466C2D4`.

## Validation

Focused source tests cover Branch B honesty, historical hash immutability, exact canonical schema equality, independent canonical bytes and hash recomputation, decoded-float exclusion, schema validation, mutation rejection, 8192-vector equality, 2744 timing equality, and the outcome firewall.

All provider, market, outcome, review, scoring, Auto Suggest, ML, MT5, production, and execution flags remain false. The next gate is `TARGETED_ASTRA_PRE_OUTCOME_REAUDIT_WITH_COMPRESSION_UNCERTAINTY_EXPLICIT`.
