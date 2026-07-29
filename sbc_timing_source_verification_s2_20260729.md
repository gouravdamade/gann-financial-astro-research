# SBC Timing Source Verification S2

Date: 2026-07-29

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

S2 adds exact whole-source byte hashing, exact UTF-8 excerpt-payload hashing,
and a deterministic independent-review bundle for a T0 candidate plus S1
packet. It does not include source files or excerpt text in the export.

The implementation is:

- `sbc/timing_profile_source_verification.py`
- `test_sbc_s2_timing_source_verification.py`
- private backend route
  `/api/chakra-lab/timing-profile/source-packet/verify-bytes`
- read-only native command `chakra_lab_timing_source_verification`
- Chakra Audit tab `Verify sources`

The bundle is ready only when the candidate and packet pass S1, every selected
source file matches its declared SHA-256, every exact excerpt payload matches
its claim hash, and there are no missing or unexpected IDs.

`READY_FOR_INDEPENDENT_REVIEW` is not external review, source certification,
profile registration, directional timing, financial validation, or execution.
The certified registry remains empty and server-owned.
