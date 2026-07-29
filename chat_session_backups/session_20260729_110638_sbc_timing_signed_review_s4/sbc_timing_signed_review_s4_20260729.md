# SBC Timing Signed Review S4

Date: 2026-07-29

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

S4 authenticates one approved S3 record against an Ed25519 reviewer key held
in a server-owned trust registry. The signature binds the exact S2 bundle,
attestation, S3 proposal, candidate profile, and source packet.

The client cannot supply a public key or registry. Keys are fail-closed for
revocation, validity dates, exact profile scope, exact packet scope, reviewer
identity, and reviewer organization.

A passing record may report only
`READY_FOR_MANUAL_SOURCE_CERTIFICATION`. It does not prove reviewer
independence, certify doctrine, register a profile, write a registry, affect
inference, produce ML evidence or trades, or enable execution.

Implemented surfaces:

- `sbc/timing_profile_signed_review.py`
- `test_sbc_s4_timing_signed_review.py`
- server-owned `status/timing_profile_reviewer_trust_registry.json`
- private backend route
  `/api/chakra-lab/timing-profile/signed-review/verify`
- read-only native command `chakra_lab_timing_signed_review`
- Chakra Audit tab `Signed review`

The repository trust registry intentionally ships empty. A real key requires
external identity and independence vetting plus a separate human-reviewed Git
change.

## Final verification

- S4 engine tests: `11/11`
- Chakra Lab service tests: `22/22`
- Chakra Audit workspace tests: `9/9`
- Full repository Python suite: `542/542`
- Full frontend suite: `101/101`
- Canonical status suite: `45/45`
- Changed Python scope Ruff: passed
- Frontend lint and production build: passed
- Native `cargo check` and focused `rustfmt --check`: passed
- Canonical status validation: 19 documents, 12 audits, execution false
- Live backend no-input result: `S3_NOT_READY`
- Live backend unknown-key result: `REVIEWER_KEY_UNTRUSTED`
- In-app-browser desktop acceptance: passed

The live tests confirmed that the server-owned registry is valid and empty,
client material cannot establish trust, source certification remains false,
and execution remains locked. The browser showed the complete S4 gate and
blocked-capability trail without hiding the narrower meaning of a signature.

Repository-wide Ruff still reports the same 19 pre-existing out-of-scope
findings. Repository-wide `cargo fmt --check` still reports only the older
formatting difference in `src-tauri/src/companion_gateway.rs`. The production
frontend build still emits the existing main-bundle size advisory.
