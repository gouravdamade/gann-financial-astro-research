# MO-R4A-S3R1-R3-R2 Astra Integrity Corrections

Milestone: `MO-R4A-S3R1-R3-R2`. Starting master: `e1c7291cce81fcc8c595baab62e338fe5a7ee8ff`.

## Astra Findings

Astra verdict: `PRE_OUTCOME_CORRECTION_REQUIRED`. The two corrected findings remain pending targeted Astra re-audit; no Astra PASS is claimed.

The cache blocker was caused by `lru_cache` trust wrappers in the R2 and R3-R1 predecessor validation path. Those wrappers were removed. Current bytes are re-read and rebuilt on every public validation or materialization call; only an ephemeral call-scoped verified snapshot prevents repeated nested reads within that one atomic call, and it is discarded on return.

The parser defect was caused by `lzma.decompress(..., FORMAT_ALONE)` accepting a valid prefix while ignoring suffix bytes. The successor uses `lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)` and rejects both incomplete streams and non-empty `unused_data`.

## Parser Contract

Parser contract: `18259325D9C8B245C05F4ECF596AD86395406A485E58DF3DF18C6B638C86BABE`; parser source: `F3D49AFBC055D9C1CF2E513194C9A98C8D55769FF974343B99A4D00EE4A35BC8`. Exact-single stream, eof-required, and `unused_data` reject policies are bound in the contract.
Acquisition contract: `BE4C378E368956F46F69D004D0C7522B32EA784C15894106B98DA8AA9A983CAC`. Provider framing remains `PLAUSIBLE_CROSS_SOURCE_RECONCILIATION_NOT_DIRECT_PROVIDER_SPECIFICATION` and `providerProtocolFullyClosed=false`.

The historical parser and its source hash remain unchanged. No provider bytes, market data, outcomes, or live parsing were used.

## Scientific Invariance

The package retains 24 frozen identities, 14 directional rows, 13 primary rows, 39 intervals, 15 provider partitions, and the existing 40-state null. Population `7F3CB6DE622A71FDA7F66E89BDAE2D0B7E3228E94BCAC403220DB17CF2686317`, clusters `6D4968B9C7DB7B912FFF2567088AECFEE7AC00C5329BD0245E6BDE3A6613CC0E`, and invariance `C53F5EB8C6ADAB19D090A834FBCFABA6D9207ADC9640C6E08CD8534D137748F9` are source-successor records only.
The required focused successor suite passed 10 tests with 12 subtests. The historical S3R1/R1/R2/R3/R3-R1 chain passed 57 tests with 124 subtests, including 8,192 binary-vector checks and 2,744 timing combinations, all with zero mismatches. The full backend passed 526 tests with one expected skip; canonical repository pytest passed 1,070 tests with two expected skips. Deterministic regeneration was byte-identical.
Core: `9B7D06C3F3BD7470478C75F9313EFBF9EB6C29E8BE766A74693FF77DA60A5C64`. Acceptance: `632D2B0C10D2F44287D8493495EC06E5CEDF6D7AD9DBC7374F2F2968327F9D8B`. Disposition: `8EB965E2097277F0D53919002B7493A0158E91A164AB436616D15449604FE4B9`.

## Locks

All access flags remain false. `scientificDesignChanged=false`, `providerAccessPerformed=false`, `marketOutcomeRead=false`, `executionAllowed=false`, and `outcomeUnlocked=false`.
Next gate: `TARGETED_ASTRA_R3_R2_PRE_OUTCOME_REAUDIT`.
