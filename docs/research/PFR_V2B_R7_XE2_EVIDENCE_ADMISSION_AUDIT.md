# PFR-V2B-R7-XE2 Evidence Admission Audit

## Admitted real inputs

XE2 uses four verified, `SINGLE_PASS_VERIFIED` USD chart-conditioned event
identities from the April 2025 reviewed-packet record:

| Event ID | Exact UTC | Transit -> natal | Aspect | Raw Moon speed |
| --- | --- | --- | --- | --- |
| `TN_CE5F70C72FD13CC479740159` | 2025-04-01T16:19:44Z | MOON -> MOON | square | 14.74005797 deg/day |
| `TN_397A2B053BC76D9D788E5E5E` | 2025-04-01T16:47:34Z | MOON -> MERCURY | sextile | 14.73383495 deg/day |
| `TN_A32A6104A917D4918B269910` | 2025-04-04T15:13:11Z | MOON -> JUPITER | conjunction | 13.56881018 deg/day |
| `TN_BD340A6100B173B5F254EDC1` | 2025-04-05T07:08:45Z | MOON -> SATURN | square | 13.30215282 deg/day |

The fixture records each immutable event hash, source packet file and hash,
blank-packet hash, and identity-integrity manifest hash. Its astronomy contract
is `RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1`.

## Rejected as signed market evidence

The reviewed USD and JPY founder packets currently contain zero founder polarity
decisions and zero evidence classifications. No sign may be inferred from:

- event geometry or planet/body name;
- real raw speed or motion phase;
- price or later return;
- SBC, Shadbala, Drik, Ashtakavarga, LLM output, or a source profile.

The signed values used in the fixture are separate
`SYNTHETIC_SIGN_TEST_ONLY_NOT_MARKET_EVIDENCE` values. Their only role is to
exercise the tournament's causal-scoping and no-sign-flip safeguards.

## Outcome governance

April 2025 remains `TOUCHED_DEV`. XE2 has no attached governed frozen offline
outcome dataset. Thus `MARKET_OUTCOME_NOT_ADMITTED` and
`BLOCKED_NO_GOVERNED_OFFLINE_OUTCOME_DATASET` are expected, visible states.
No live MT5, price archive, or result data is read.
