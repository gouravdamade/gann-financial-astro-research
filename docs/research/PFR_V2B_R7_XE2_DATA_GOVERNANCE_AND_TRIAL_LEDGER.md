# PFR-V2B-R7-XE2 Data Governance and Trial Ledger

The immutable XE2 ledger contains M0-M4 trial records only. Every record is:

- scoped to `TOUCHED_DEV` April 2025;
- `NOT_EVALUATED`;
- excluded from pristine-holdout claims;
- excluded from market-outcome evaluation;
- hash-addressed after profile binding.

The ledger must not be read as an experiment result. It simply records the
five test arms and the blocked-outcome condition so a later, separately
authorized validation milestone has an auditable starting point.

Any future use of market outcomes requires a frozen, versioned offline dataset
and a distinct authorization. It must never fall back to live MT5 data.
