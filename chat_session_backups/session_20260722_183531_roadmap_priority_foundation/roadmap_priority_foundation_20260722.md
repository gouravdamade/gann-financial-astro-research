# Roadmap Priority Foundation

Date: 2026-07-22

## Scope

This milestone implements the first repository-safe slices from
`Gann_Astro_Priorities_Roadmap.pdf` without changing production Auto Suggest,
MT5, order execution, the frozen prospective cohort, or source-certification
outcomes.

## Machine-Readable Status

Added the canonical `status/` layer:

- `release_status.json` separates packaged candidates, physical testing, and
  promotion. The exact desktop `0.10.19` EXE and Android `0.10.17` APK hashes
  were recomputed successfully.
- `capability_status.json` records implemented, packaged, physically tested,
  promoted, source-certified, and financially validated as separate states.
- `research_trials.json` records the frozen USDJPY cohort and keeps the
  chart-conditioned and instrument-relative SBC trials separate and
  unregistered.
- `source_certification.json` preserves the current failed/pending Shadbala,
  Drik witness, Agarwal, and Trailokya gates.
- `validate_status.py` checks contracts, execution locks, candidate-plan hash
  links, trial-audit links, and future valid certification transitions.

## Physical Mobile Acceptance

The selected acceptance pair is frozen as:

- desktop `0.10.19`, EXE SHA-256
  `45B7087DDBEC3BC535B0575912ECACB167652FA427703002DEE7BE4BBB64B017`;
- Android debug `0.10.17`, APK SHA-256
  `75E1126A4F688F3B3376370B5D559CABAA6B35037CB0B4307CA5933227DF9E25`.

`mobile_acceptance_plan.json` defines MOB-01 through MOB-08. The
`mobile_acceptance.py` collector binds results to the exact plan, hashes every
evidence file, and refuses to record a passing physical test without evidence.
All formal physical tests remain pending. The selected Android candidate was
built from a dirty source tree, so even a complete behavioral pass requires a
later clean rebuild before promotion. Execution remains disabled.

## Frozen Prospective Audit

`audit_shadow_trial.py` opened
`D:\GannFinancialAstro\app_data\gann_aspect_annotations_raman_v2.sqlite`
through SQLite read-only mode and checked file SHA-256 plus SQLite
`data_version` before and after the audit.

Result: `pass_frozen_cohort_collecting`.

- database unchanged during audit;
- all four append-only/immutable triggers present;
- manifest and gate hashes valid;
- 14 contiguous hash-chain entries valid;
- one frozen policy cohort;
- 7 decisions and 7 outcomes;
- all 7 decisions were abstentions and none were watch decisions;
- no pending outcomes;
- financial validation remains false;
- execution remains false.

The durable audit is
`status/audits/prospective_shadow_trial_audit_20260722.json`.

## Immutable SBC Connector

Added `SBC_IMMUTABLE_SNAPSHOT_TARGET_CONNECTOR_V1` under the isolated
instrument-relative SBC lab.

The connector:

1. accepts only `SBC_CHAKRA_LAB_SNAPSHOT_V1` snapshots with timestamp-safe,
   no-lookahead, read-only guardrails;
2. rejects naive timestamps, future evidence cutoffs, unsafe guardrails, and
   uncertified board values;
3. uses only time-valid mappings whose review status is exactly `accepted`;
4. exact-matches certified `NAME_INITIAL`, `NAKSHATRA`, and `RASHI` tokens;
5. emits immutable `matched_unscored` evidence with `signed_value=None`;
6. blocks scoring, contribution emission, Auto Suggest, ML training, MT5 input,
   financial promotion, and execution.

A real Chakra-engine smoke at `2026-07-22T10:00:00Z` matched the human-accepted
test token `YA` for the USD research fixture and returned no numeric value. No
production USD/JPY identity was silently registered.

## Verification

- canonical status validator: passed, 5 documents;
- status/mobile/audit unit tests: passed;
- focused instrument-relative SBC suite: 15 passed;
- complete repository Python suite: 333 passed;
- Ruff on `status` and `research_labs/instrument_relative_sbc`: passed;
- `git diff --check`: passed.

## Remaining Gates

1. Collect MOB-01 through MOB-08 evidence on the physical phone, then rebuild
   Android from a clean source commit before stable promotion.
2. Acquire/accept time-valid production identities for USD, JPY, their relevant
   institutions, and any other instrument targets.
3. Page-certify a source profile that can translate matched SBC evidence into
   polarity and magnitude. Until then the connector must remain unscored.
4. Register separate purged prospective trials for instrument-relative SBC and
   chart-conditioned aspects. Neither may enter the frozen existing cohort.
5. Continue decomposing the oversized handoff into recovery changelog and ADR
   records after the status layer has proven stable.

## Recovery Snapshot

`D:\PycharmProjects\chat_session_backups\session_20260722_183531_roadmap_priority_foundation`
