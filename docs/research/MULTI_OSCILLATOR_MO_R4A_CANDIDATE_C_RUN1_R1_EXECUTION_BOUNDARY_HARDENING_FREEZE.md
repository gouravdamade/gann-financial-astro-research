# Candidate C RUN1-R1 Execution Boundary Hardening Freeze

## Scope

RUN1-R1 is a successor to the historical pre-run freeze at
`7c06123e5fc5362cbeb7a7b84008af584fee8e18`. It does not alter the
scientific evaluator implementations, source contracts, immutable population,
or output schema. It adds only a direct-release authorization boundary and
runtime-checkout identity verification.

## Authorization Boundary

`RealRunAuthorizationCapability` binds the RUN1 milestone, predecessor
execution contract, population hash, protected A/B identities, V2 projection
identity, one-shot intent, and event identity. Release A and Release B validate
this object before importing or invoking their frozen scientific cores.

Production issuance remains unavailable:

```
REAL_CANDIDATE_C_RUN_AUTHORIZED=false
```

The sole test mechanism accepts identifiers beginning `FAKE_REAL_RUN1_` and
cannot authorize a member of the frozen 645-event population. The top-level
runner remains blocked independently.

## Runtime Identity

The runtime manifest is
`status/research/mo_r4a_candidate_c_run1_r1_runtime_identity_manifest_v1.json`
with self-hash
`DC7215032C2C2A9DEDDCE77734662A74228B6681B0D9EEAE3487FE5E39C09F3D`.

It records 13 protected runtime file records: six for A, six for B, and one
V2 projection file. Exact historical Git blob bytes are compared to the bytes
on disk without normalization of line endings, whitespace, encoding, or
comments. Import-location probes also require each module's resolved file to
belong to its declared root.

The shared `candidate_c_reproduction/__init__.py` is intentionally recorded
once for A and once for B. Their protected blobs differ (`C005...0968` for A
and `4261...96877` for B), so a single checkout cannot truthfully meet both
complete frozen manifests. A future run must provide independent verified
`EVALUATOR_A_RUNTIME_ROOT` and `EVALUATOR_B_RUNTIME_ROOT`, plus the verified
`V2_PROJECTION_RUNTIME_ROOT`.

## Protected and Population Identities

- A aggregate: `93ECB7BDB684C9F9788F63BADAE8D297453F02557D7BB89DB2621CF9E257DCFB`
- B aggregate: `0A3266F754939D2408B4B7646A1E36A1CEC7338EDADE5844E831BCF6EB4CD199`
- V2 semantic projection: `1DDFC3B79EC30913254A2FEA117A97EA1761E42D8681EB5D2CB6B2D698187BED`
- Population: 645 events, `A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6`
- Row universe: 5,160 per evaluator,
  `6AC975EE4DA32A3872399C68F514BA19E63FFAC5F565018A2DF15CECA27A4580`

## Outcome Boundary

The population was read only for identity, structure, adapter equivalence, and
execution-boundary validation. It was not evaluated. No real rows, comparison,
price, return, outcome, provider, broker, or Swiss Ephemeris data was read.
No polarity, score, magnitude, wave, Fields output, Auto Suggest, ML, MT5, or
execution is enabled. The declared future result paths remain unpopulated.

## Next Gate

`CENTRAL_REVIEW_CANDIDATE_C_RUN1_R1_EXECUTION_BOUNDARY_HARDENING`
