# PFR-V2B-R7-XE1 Trial Ledger and Data Governance

XE1 uses `XE1_EXPERIMENTAL_TRIAL_LEDGER_V1` for immutable demonstrative trial
records. Each record carries the profile hash, transform version, parameters,
dataset ID/status, result, code commit, creation time, and an immutable entry
hash.

## Dataset Status

- `SYNTHETIC`: default. Contains no market or price data.
- `TOUCHED_DEV`: exploratory data that has been inspected or otherwise touched.
- `MANUAL`: intentionally empty in XE1; the UI states `MANUAL_INPUT_REQUIRED`
  and the endpoint refuses frontend-supplied raw observations.

`APRIL_2025_REVIEW_WINDOW` is permanently registered as `TOUCHED_DEV`. It is
not a pristine holdout, it has no XE1 result, and it cannot be described as
financial validation.

No XE1 trial is eligible for source promotion, Fields influence, Auto Suggest,
ML, live inference, MT5, or execution.
