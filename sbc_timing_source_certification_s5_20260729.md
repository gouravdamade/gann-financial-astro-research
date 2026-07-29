# SBC Timing Source Certification S5

Date: 2026-07-29

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

S5 reruns the complete S1-S4 evidence chain and verifies a separate Ed25519
source certificate against a server-owned certification-authority registry.
The certifier key and identity must differ from the reviewer, and the
separation of duties must have been administratively vetted.

The client cannot supply an authority key or registry. Authorities are
fail-closed for revocation, validity dates, profile scope, packet scope,
identity, organization, and exact S1-S4 evidence binding.

A valid `REJECTED` certificate reports `SOURCE_CERTIFICATION_REJECTED`. A
valid `CERTIFIED` certificate may report
`READY_FOR_PROFILE_REGISTRY_ADMISSION` and emit only a reproducibly hashed
registry-entry proposal. The application cannot apply the proposal.

Implemented surfaces:

- `sbc/timing_profile_source_certification.py`
- `test_sbc_s5_timing_source_certification.py`
- server-owned
  `status/timing_profile_certification_authority_registry.json`
- private backend route
  `/api/chakra-lab/timing-profile/source-certification/verify`
- read-only native command `chakra_lab_timing_source_certification`
- Chakra Audit tab `Source certificate`

The repository authority registry intentionally ships empty. A real authority
requires separate identity, scope, and separation-of-duties vetting plus a
human-reviewed Git change.

A source certificate is a signed governance decision. It does not
cryptographically prove doctrinal truth, register a timing profile, calculate
market direction or confidence, affect Auto Suggest or ML evidence, produce a
trade, or enable execution.

## Verification target

- S5 engine tests: `13/13`
- Chakra Lab service tests: `24/24`
- Chakra Audit workspace tests: `10/10`
- Full repository Python suite: `562/562`
- Full frontend suite: `102/102`
- Canonical status suite: `50/50`
- Changed Python scope Ruff: passed
- Frontend lint and production build: passed
- Native `cargo check` and focused `rustfmt --check`: passed
- Live backend and in-app-browser acceptance: passed
- Canonical status validation: 21 documents, 13 audits, execution false

Repository-wide Ruff still reports the same 19 pre-existing out-of-scope
findings. Repository-wide `cargo fmt --check` remains blocked only by the
older formatting difference in `gann-astro-desk/src-tauri/src/companion_gateway.rs`.
