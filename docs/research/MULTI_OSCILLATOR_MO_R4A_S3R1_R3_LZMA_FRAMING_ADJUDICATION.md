# MO-R4A-S3R1-R3 Dukascopy LZMA Framing Adjudication

## Result

R2 correctly stopped before parsing. R3 resolves its one protocol blocker without provider access or market bytes. Dukascopy excludes the XZ container while its official daily decoder uses default `lzma.decompress(compressed)`. Python documents that default as `FORMAT_AUTO`, which accepts XZ and legacy `.lzma` but rejects `FORMAT_RAW`; raw mode also requires an explicit filter chain. The unique surviving framing is therefore `lzma.FORMAT_ALONE`. This is a cross-source technical deduction, not a direct claim that Dukascopy names Python's constant.

## Source Matrix

| Question | Source | Locator | Short evidence | Status |
| --- | --- | --- | --- | --- |
| `DUKASCOPY_EXCLUDES_XZ` | DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_ES | L582 | Direct provider prose calls the payload an LZMA stream and explicitly says it is not the .xz container format. | SUPPORTED |
| `DUKASCOPY_SAMPLE_USES_DEFAULT_LZMA_DECOMPRESS` | DUKASCOPY_CURRENT_HISTORICAL_PRICE_DATA_ES | L613-646, especially L629 | The documented daily BI5 Python decoder reads compressed bytes and calls lzma.decompress(compressed) without format or filters. | SUPPORTED |
| `PYTHON_DEFAULT_EQUALS_FORMAT_AUTO` | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | L159-165 | The official function signature gives lzma.decompress(data, format=FORMAT_AUTO, memlimit=None, filters=None). | SUPPORTED |
| `PYTHON_FORMAT_AUTO_ACCEPTS_XZ` | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | L241-245 | FORMAT_AUTO detects the container and decompresses .xz and .lzma files. | SUPPORTED |
| `PYTHON_FORMAT_AUTO_ACCEPTS_FORMAT_ALONE` | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | L233-245 | Python defines FORMAT_ALONE as the legacy .lzma container and says FORMAT_AUTO decompresses .lzma files. | SUPPORTED |
| `PYTHON_FORMAT_AUTO_REJECTS_FORMAT_RAW` | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | L238-245 | Python states data in FORMAT_RAW cannot be decompressed using FORMAT_AUTO. | SUPPORTED |
| `PYTHON_FORMAT_RAW_REQUIRES_EXPLICIT_FILTER_CHAIN` | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | L117-118 and L238-239 | Python requires a custom filter chain when the raw format is used for decompression. | SUPPORTED |
| `PYTHON_FORMAT_ALONE_IS_LEGACY_LZMA_CONTAINER` | PYTHON_3_14_7_LZMA_LIBRARY_REFERENCE | L233-236 | Python names FORMAT_ALONE as the legacy .lzma container format. | SUPPORTED |

## Candidate Formats

| Format | Provider prose compatible | Official sample compatible | Python runtime compatible | Disposition |
| --- | --- | --- | --- | --- |
| `FORMAT_XZ` | False | True | True | ELIMINATED |
| `FORMAT_ALONE` | True | True | True | SELECTED_BY_CROSS_SOURCE_TECHNICAL_DEDUCTION |
| `FORMAT_RAW` | NATURAL_LANGUAGE_RAW_IS_NOT_A_PYTHON_API_ASSERTION | False | False | ELIMINATED |

The natural-language phrase `raw LZMA` is not equated with Python `FORMAT_RAW`. Python's API definition rules FORMAT_RAW out for the documented no-filter default call.

## Offline Parser

The parser is `gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3.py`, source SHA-256 `47BEF7B1A13D8EE4EC2DDED2BDD965A27D41FCB548EC0D4D940A5535669D733E`, and accepts caller-supplied bytes only. Its single production call is `lzma.decompress(raw_bytes, format=lzma.FORMAT_ALONE)`. It decodes `>IIIff` 20-byte records, preserves record order and volume byte identities, and hashes canonical UTF-8 JSON Lines with sorted keys and millisecond UTC timestamps. The `14` documented fixtures are generated in memory from invented 2030 values and are `SYNTHETIC_NOT_PROVIDER_DATA`.

## Frozen Lineage

R2 acquisition `A1C2129E9395C9850A66A595F3529563AFBDA14E10C8F0B7DBB3A78897ECF500` is historical and unchanged. R3 acquisition `87D0716EFE9C0D655BB9F3C3D5DE5DBB8E6BED6B164F757F67665DB16D1E09E3`, source lock `B36E946F45607B8900FA2A451DC8262C1ADB6A592850A0DAAEF04A5BD18D0314`, adjudication `0F8F61572764E898F1D3F0E8676412A3770A45920FCFCB6A0AEDD9126C88855B`, parser contract `C91A76165893BCA308FE2DB9B3F83A2E9B0233CF2023E1AC573504C68EC3D316`, preregistration `DA05644AD7321F7EB5AEFC348B3672A0241C39AEC6DAEDCD46B12E275BCC8A04`, population `D2F60D5592DD4E5904079538D2938218037567626976211F794F710A87E83294`, core `C98FCE359846C7BAE786F8AA99E60925CA26178B533C035126CFC7BC07339A99`, and acceptance `38903C4C086AEF928D490AF5F67EAC3C16E101812221E13D4BED036F1AF46C90` bind the successor without hash cycles.

## Invariance And Firewall

The 24 identities, 14 directional rows, 13 primary rows, 39 analytical windows, 15 native daily partitions, four clusters, and 40-state null remain unchanged. The exhaustive 8192 binary-vector and 2744 timing checks remain required by the focused suite. No provider object was requested, no market or outcome data was read, and every outcome-access flag remains false. R3 performs no scoring, product work, package build, or execution.

## Next Gate

`INDEPENDENT_CENTRAL_REVIEW_BEFORE_TARGETED_ASTRA_PRE_OUTCOME_REAUDIT`. The parser freeze alone does not unlock outcomes, provider access, S4, or execution.
