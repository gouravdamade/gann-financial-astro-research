# PFR-V2B-R6-N1 Architecture, Runtime and Reliability Audit

## Baseline and scope

N1 began from public `origin/master` `8bb6a0e78bb4ef8b02b270ce804d97fb1d12ab31`.
The founder's active `D:\PycharmProjects` tree was dirty with local databases,
logs, releases and evidence; it was not changed. Work occurred in clean
`D:\PycharmProjects-n1`.

The controlling Trailokya 1972 and same-lineage 2016 private witnesses were
hash-verified. The TD3 advance translation was available and treated as an
indexing/translation aid, not controlling evidence.

## Findings and remediation

### P1 - Missing execution locks were accepted as false

Affected code: `src/runtimeProfile.ts`, `src/api.ts`, `src/companion.ts`, and
`src/desktopCompanion.ts`.

Risk: JavaScript truthiness accepted an omitted `executionAllowed` field from
untrusted Tauri/companion/backend payloads. That is a fail-open transport
boundary even though every intended profile is read-only.

Fix: every audited transport gate now requires `executionAllowed === false`.
Missing values reject with the existing read-only execution-lock error. Tests
cover missing desktop runtime and companion lock fields.

### P1 - Trailokya source-only geometry borrowed a generic grid profile

Affected code: `sbc/trailokya_source_only_geometry.py` and Fields request
construction.

Risk: the selected Trailokya source-only profile could calculate source rays
using `sbc_81_rotation_normalized_partial_v1`, a legacy generic grid whose
authority is Phaladeepika/editor-plus-secondary figure evidence. This violates
profile isolation after TD1R2 established a native Trailokya construction.

Fix: direct Trailokya geometry now requires a future explicit
`trailokya_1972_native_akhanda_81_v1` adapter and fails closed while it is
absent. No score-free source geometry is substituted. Fields already reports
`GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED`, so it does not display a fallback wave.

### P2 - Historical repository data dominates checkout size

Tracked backup SQLite/WAL and rollout data make the checkout about 1.09 GiB.
No deletion is safe without an archive/recovery migration. See the hygiene
report.

### P2 - Handoff is costly recovery context

The current handoff is over ten thousand lines. It remains intact because a
mass archive rewrite is outside N1; the hygiene report defines a safe later
migration sequence.

## Backend, frontend and security observations

- The Python backend binds to `127.0.0.1`; the desktop runtime validates a
  loopback URL and token. Companion LAN/Tailscale HTTPS is a distinct Rust
  gateway rather than a broad Python listener.
- Synchronized Fields uses a request sequence and range cache, preventing an
  earlier async response from overwriting a newer visible range. It does not
  cancel in-flight work, which is a P3 performance opportunity.
- Pair-relative computation retains null values for unknown sides and only
  uses known zero for explicit known/no-activity intervals. Formula and base
  minus quote ordering were not changed.
- TD3 commodity and Arghya contracts have no runtime loader/API/UI consumer;
  they are static source records with prohibited-use lists.
- Broad exception handlers exist in historical market/generation modules but
  were not changed without a route-specific reproduction. Errors at reviewed
  source gates are explicit and fail closed.

## Explicit boundaries

- `SOURCE_CLOSED != RUNTIME_AUTHORIZED`.
- `UNKNOWN != ZERO` and `UNKNOWN != NEUTRAL` in the pair-relative route.
- Profile fallback is prohibited unless a future adapter is explicit and
  source-owned.
- TD2 phala, TD3 Viswa, Arghya twenty-part arithmetic, Agarwal records, and
  modern pair values are separate numerical systems.
- No polarity, score, price forecast, Fields formula change, Auto Suggest, ML,
  MT5 or execution was added.

## Verified regression record

- Focused Trailokya and affected Chakra service suite: `51 passed`.
- Full Python regression: `749 passed`, `1 skipped` because its external JHora
  witness environment variable was intentionally absent, and `16` subtests
  passed.
- Focused frontend transport gates: `3` files and `21` tests passed.
- Full frontend suite: `37` files and `163` tests passed.
- Oxlint and the production frontend build passed.
- `cargo fmt --check`, `cargo check`, and Rust unit tests passed; the native
  suite contains `19` passing tests.

## Recommended next decision

`ARCHITECTURE_CLEANUP` is the appropriate next milestone: create and verify a
source-native Trailokya grid adapter before any Trailokya inspector or bounded
runtime promotion. TD3 Arghya worked reconstruction should wait for the
adapter and a separate founder authorization because its commodity/value
pipeline must not be generalized to FX.
