# Candidate C EMP0-R3-R1 Pre-Data One-Shot Result Root And Contract Seal

## Scope

EMP0-R3-R1 is a narrow pre-market-data successor to the historical EMP0-R3
freeze. It repairs execution control and future-record schema alignment only.
It does not alter the historical R3 records, the source snapshot, eligibility,
future test ledger, quote/return definition, sample gates, temporal null,
permutation count, or multiplicity methods.

The successor binds the historical source identities:

- source snapshot: `9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284`
- source eligibility: `ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1`
- reused 24-entry test ledger: `91322F3A5759A6BDDA3C87CDDFDDC3A70F9E27A58CC15327AEA45F1C04B0DDAA`

These remain 645 events, 5,160 canonical source rows, eight source-testable
cells, and 24 future ledger entries.

## Canonical First Result

The production entrypoint is exactly:

```python
execute_emp2_once(
    repo_root,
    market_snapshot_record,
    market_admission_record,
    authorization_record,
)
```

It accepts no `output_root`, result path, destination, alternate root, or
temporary root. Its only possible first-result location is:

`<verified repo root>/status/research/mo_r4a_candidate_c_emp2_market_association_result_v1.json`.

An existing artifact fails before statistical work with
`EMPIRICAL_FIRST_RESULT_ALREADY_EXISTS`. The private
`_execute_emp2_once_to_root_for_test` seam exists exclusively for synthetic
test isolation and is not the production API.

## Exact Future Record Contracts

The successor authorization contract's `requiredFields` is identical to the
executable validator's fixed set. It rejects missing fields and unregistered
extras, requires the three authorization switches to be true, requires all
prohibited change/requery switches to be false, and binds the exact
`marketAdmissionRecordContractHash` in addition to the individual admission
record hash.

New market admission records use only:

- `emp0R3R1MarketSnapshotSchemaHash`
- `emp0R3R1MarketDataAdmissionContractHash`

R2 and R3 predecessor field names are preserved only in historical records;
they are not valid R3-R1 inputs, including as extra fields.

## Successor Records

The R3-R1 runtime identity binds the implementation commit, protected source
and test bytes, successor preregistration, temporal-null contract, execution
contract, result schema, authorization contract, successor market schemas,
and the unchanged source/ledger identities. The acceptance record records that
the canonical root is the verified repository root, public alternate roots are
not allowed, and first-result overwrite remains disallowed.

## Verification

The focused synthetic suite verifies public signature shape, canonical-root
writing, replay rejection, exact field names, rejection of predecessor
admission fields, the full authorization required-field set, all required
boolean switches, and the new admission-contract binding. Synthetic fixtures
are not provider data and no real authorization or result is created.

## Pre-Data Boundary

`providerSelected=false`, `marketDataAcquisitionAllowed=false`,
`marketSnapshotPresent=false`, `marketAdmissionRecordPresent=false`,
`marketOutcomeRead=false`, `realMarketReturnComputed=false`,
`realMarketStatisticComputed=false`, `realMarketPValueComputed=false`,
`empiricalExecutionAuthorizationPresent=false`,
`empiricalExecutionAuthorized=false`, and `executionAllowed=false`.

No market direction, USD/JPY sign mapping, source weights, pair field,
polarity, score, forecast, Fields, Auto Suggest, ML, MT5, or execution is
enabled.

## Next Gate

`CENTRAL_REVIEW_CANDIDATE_C_EMP0_R3_R1_PRE_DATA_ONE_SHOT_RESULT_ROOT_AND_CONTRACT_SEAL`
