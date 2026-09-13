# MO-R4A-S3R1-R3-R3 Resource-Root Purity and Validator Hardening

Milestone: `MO-R4A-S3R1-R3-R3`
Starting master: `12fba8c981fdb9cf7cbf1819ae4c7ec1154d1e2e`
Audit date: 2026-09-14

## Purpose and Boundary

This is a bounded validator-integrity repair following the read-only Astra
pre-outcome re-audit of the R3-R2 successor. It addresses resource-root
cross-contamination through the R1/R2/R3/R3-R1/R3-R2 validation and
materialization chain. It does not change the scientific design, frozen event
identities, parser implementation, acquisition protocol, source doctrine,
provider access, outcome handling, product UI, Rust/Tauri code, or packaging.

The prior Astra findings remain part of the historical record. This milestone
does not claim an Astra pass. Its disposition is
`RESOURCE_ROOT_MAJOR_CORRECTED_PENDING_ASTRA_REAUDIT`.

## Prior Finding and Reproduction

The 2026-09-13 targeted Astra report found a fresh major defect while testing
two copied resource roots. After root A was mutated, validation of otherwise
unchanged root B was rejected. The rejection was not persistent validation
trust: it came from nested schema reconstruction reading the module's
`PROJECT_ROOT` instead of the caller-supplied root.

The original cache false-accept finding remains closed, and the trailing
compressed-byte finding remains closed. The new finding was:

`RESOURCE_ROOT_CROSS_CONTAMINATION`
Severity: `MAJOR`
Prior status: `OPEN_FROM_ASTRA_R3_R2_REAUDIT`
Current status: `CORRECTED_PENDING_ASTRA_REAUDIT`

## Root-Propagation Corrections

The following file-backed paths now retain the caller's `resource_root`:

- R2 `build_s3r1_r2_schema(preregistration=None, *, resource_root=PROJECT_ROOT)`
  uses the supplied root for its implicit payload.
- R3 `parser_source_sha256(parser_source_path=None, *, resource_root=PROJECT_ROOT)`
  resolves the default parser relative to the supplied root while preserving an
  explicitly supplied positional parser path.
- R3 `build_parser_contract(..., *, resource_root=PROJECT_ROOT)` and
  `build_s3r1_r3_schema(..., *, resource_root=PROJECT_ROOT)` propagate that
  root to parser and R2 schema reconstruction.
- R3 `_validate_parser_source` reads the parser beneath the supplied root.
- R3-R1 acquisition, schema, write, and validate paths pass the supplied root
  into the R3 parser/schema calls.
- R3-R2 schema reconstruction passes its root into the R3 schema builder.

Default positional behavior remains compatible. `PROJECT_ROOT` remains only as
the default repository-root behavior and as a path-template anchor relocated
under an explicit root; it is no longer an implicit file source for these
custom-root operations.

## Adversarial Evidence

The new test module uses actual copies of the contract tree under disposable
D: workspace roots. It proves:

- root A prediction-freeze mutation rejects A while unchanged B remains valid,
  in both mutation directions;
- historical parser-source mutation is local to A;
- historical R3-R1 acceptance mutation is local to A;
- explicit and implicit R2, R3, R3-R1, and R3-R2 schema builders remain local
  to B when A is changed;
- B materialization remains unchanged while A is corrupted, while B corruption
  is rejected;
- same-root mutation fails closed and all validation ContextVars are cleared
  after both success and failure;
- repeated canonical R3-R2 materialization is byte-identical;
- historical and successor parser identities remain exact.

Focused result: `10 passed` in
`gann-astro-desk/backend/test_outcome_analysis_s3r1_r3_r3.py`.

## Immutable Contract Identities

The R3-R2 successor identities are unchanged:

- parser contract: `18259325D9C8B245C05F4ECF596AD86395406A485E58DF3DF18C6B638C86BABE`
- successor parser source: `F3D49AFBC055D9C1CF2E513194C9A98C8D55769FF974343B99A4D00EE4A35BC8`
- acquisition: `BE4C378E368956F46F69D004D0C7522B32EA784C15894106B98DA8AA9A983CAC`
- preregistration: `23564E1F41C441EC1FB98B3FBD025F43643AEF75C27AD080550F7DCB7D64F272`
- population: `7F3CB6DE622A71FDA7F66E89BDAE2D0B7E3228E94BCAC403220DB17CF2686317`
- clusters: `6D4968B9C7DB7B912FFF2567088AECFEE7AC00C5329BD0245E6BDE3A6613CC0E`
- invariance: `C53F5EB8C6ADAB19D090A834FBCFABA6D9207ADC9640C6E08CD8534D137748F9`
- core: `9B7D06C3F3BD7470478C75F9313EFBF9EB6C29E8BE766A74693FF77DA60A5C64`
- acceptance: `632D2B0C10D2F44287D8493495EC06E5CEDF6D7AD9DBC7374F2F2968327F9D8B`

The frozen population remains 24 events, 14 directional rows, and 13 primary
rows. The acquisition geometry remains 39 half-open intervals across 15 unique
provider partitions. The four overlap clusters remain C1-C4. The prior
independent evidence remains 8,192 binary vectors and 2,744 timing cases with
zero mismatches; no real outcome was read.

## Verification

- Focused root-purity tests: `10 passed`.
- Historical S3R1/R1/R2/R3/R3-R1/R3-R2 chain: `67 passed, 136 subtests passed`.
- Broad backend: `536 passed, 1 skipped, 202 subtests passed`. The skip is
  `PRIVATE_G3_S1_SOURCE_WITNESS_NOT_AVAILABLE`.
- Canonical repository pytest: `1080 passed, 2 skipped, 202 subtests passed`.
  The skips are the unavailable private G3-S1 witness and the optional
  external JHora witness.
- Ruff targeted files: passed.
- Python compileall targeted files: passed.
- Three new JSON records: parsed and self-hash verified.
- Canonical R3-R2 regeneration: byte-identical across 11/11 materialized
  files in the focused test.
- `git diff --check`: passed.
- Repository `.bi5` scan: no provider BI5 files found.

## Committed Evidence Records

- `status/audits/mo_r4a_s3r1_r3_r3_astra_findings_disposition.json`
  self-hash: `8A32D3491C65801F392B5F6AB5453DA7B5115F34301851C089F5EB50F8437FD9`
- `status/audits/mo_r4a_s3r1_r3_r3_resource_root_purity_audit.json`
  self-hash: `D1895250E16FFFBA988E18F3AD29836D7E9B132908D5743C883409938519C979`
- `status/acceptance/mo_r4a_s3r1_r3_r3_root_purity_gate.json`
  self-hash: `128F4E3F03CB7E5C190484CFB04796088FED15165B3AC81A867DA2B64F5606F2`

The gate remains pending `TARGETED_ASTRA_R3_R3_ROOT_ISOLATION_REAUDIT`.

## Locks

All outcome-access flags remain false. `providerAccessPerformed=false`,
`marketOutcomeRead=false`, `outcomeUnlocked=false`, and
`executionAllowed=false`. No provider request, market byte, outcome, founder
decision, catalogue admission, evidence admission, signed wave, pair
resultant, Auto Suggest, ML, MT5, or execution path was used. No parser source
or parser semantics changed; the root fix only controls which existing bytes
are read.
