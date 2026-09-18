# Candidate C EMP0-R3 Pre-Data Execution Closure

EMP0-R3 is a pre-data runtime hardening freeze. It preserves the historical
EMP0-R2 freeze and makes no change to the Candidate C source states, source
eligibility, test cells, return definition, horizons, temporal null,
permutation count, or multiplicity families.

The validated market snapshot now exposes `FrozenMarketQuote` values and a
tuple of raw-artifact identities. Both are immutable after validation and the
raw snapshot input is not modified. The public EMP2 entrypoint accepts only
raw future market/admission/authorization records. It internally verifies the
repository runtime, frozen source snapshot, frozen source eligibility, market
records, and externally self-hashed authorization before deriving returns.

The runtime verifier protects the actual bytes of `canonical.py`, market and
return validation, statistics, multiplicity, authorization, execution,
runtime, artifact, and preregistration modules, plus the EMP0 test sources.
It verifies all R3 contract self-hashes and the historical source identities:

- Source snapshot: `9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284`
- Source eligibility: `ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1`
- Frozen 24-entry ledger: `91322F3A5759A6BDDA3C87CDDFDDC3A70F9E27A58CC15327AEA45F1C04B0DDAA`

Execution derives the eight eligible source cells and their exact
`eligibleValueStates` from the frozen eligibility artifact. UNKNOWN and rare
states cannot enter the inferential rows. Per horizon, a state requires at
least 20 market-admissible returns; a cell requires at least two retained
states and 60 retained observations. The executor always emits all 24 ledger
rows, applies one Holm family to executed 24-hour rows and one BH family to
executed 1-hour/6-hour rows, and leaves nonexecuted rows visible.

The sole future result path is
`status/research/mo_r4a_candidate_c_emp2_market_association_result_v1.json`.
It is canonical, self-hashed, atomically written once, and rejects replay or
overwrite. No result exists in this freeze.

This does not select a provider, acquire data, read a price, compute a real
return or statistic, issue a real authorization, assign polarity, create a
score, or enable execution. Future EMP1 and EMP2 require zero changes to the
protected analysis, authorization, source-state, return, temporal-null, or
multiplicity implementation.

Next gate:
`CENTRAL_REVIEW_CANDIDATE_C_EMP0_R3_PRE_DATA_END_TO_END_EXECUTION_BINDING_AND_IMMUTABILITY_CLOSURE`.
