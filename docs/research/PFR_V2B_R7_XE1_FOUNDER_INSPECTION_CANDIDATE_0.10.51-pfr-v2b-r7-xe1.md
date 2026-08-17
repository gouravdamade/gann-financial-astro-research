# PFR-V2B-R7-XE1 Founder-Inspection Candidate

## Candidate

| Field | Value |
| --- | --- |
| Milestone | `PFR-V2B-R7-XE1` |
| Version | `0.10.51-pfr-v2b-r7-xe1` |
| Candidate source commit | `bb8337f50ee6fbc36c378f442d5f6ba82e267a5a` |
| XE1 implementation provenance | `9c988395e9dbff09a4c3f60912fa1edac48ae375` |
| Source state at packaging | clean; `source_git_dirty=false` |
| Candidate status | founder inspection candidate; not accepted or stable |
| Candidate root | `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.51-pfr-v2b-r7-xe1-tauri` |
| Portable executable | `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.51-pfr-v2b-r7-xe1-tauri\GannAstroDesk.exe` |
| NSIS installer | `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.51-pfr-v2b-r7-xe1-tauri\Gann Astro Desk_0.10.51-pfr-v2b-r7-xe1_x64-setup.exe` |

## Artifact Hashes

| Artifact | SHA-256 |
| --- | --- |
| Portable `GannAstroDesk.exe` | `3A3645F940B73FD74D2B282EA322875DFE522CE991C2945D0956978EE89D8F69` |
| Installer | `96DA7835AEAAB3371953C2B3EDDC31BF96B70EBBC408CBD1AC75181406A9772E` |
| Packaged backend | `27721416CF10AB0F1136159ECB2643A6E0FBCADC1CA340F34844F07917645D37` |

`release.manifest.json` and `SHA256SUMS.txt` are adjacent to the artifacts.
The manifest records `source_git_dirty=false`, `mt5_execution_mode=read_only_market_data`, and the XE1 locks: no price reads/outcomes, no SBC fusion, no Fields formula change, no Auto Suggest, no ML, no MT5 addition, and `experimental_evidence_execution_allowed=false`.

## What This Candidate Adds

The top-level **Experiments** workspace exposes the independent
`XE1_EXPERIMENTAL_EVIDENCE_LAB_V1` surface. It renders immutable synthetic
observations, versioned role bindings, causal grouping, named transform
comparisons, categorical state-vector output, separate confidence, and the
immutable trial ledger.

It is explicitly labelled:

`EXPERIMENTAL - NOT CLASSICAL - NOT VALIDATED - NO EXECUTION`

The populated synthetic fixture has seven observations. An ambiguous causal
record is displayed as `AMBIGUOUS_CAUSE_FAIL_CLOSED`; a derived child is
auditable but never receives an additional directional vote. Touched development
has no currently admitted observations and reports
`TOUCHED_DEV_INPUT_NOT_CONFIGURED` with `UNKNOWN_NO_ACTIVE_EVIDENCE`.

## Verification

```text
Focused XE1 backend:
python -m unittest discover -s backend -p "test_experimental_evidence_service.py"
13 passed

Full backend:
python -m unittest discover -s backend -p "test_*.py"
228 passed

Focused XE1 frontend:
npx vitest run src/experimentalLabWorkspace.test.tsx --pool=threads --maxWorkers=1 --no-file-parallelism --testTimeout=15000
1 file, 2 tests passed

Full frontend:
npx vitest run --pool=threads --maxWorkers=1 --no-file-parallelism --testTimeout=15000
81 files, 166 tests passed

npm run lint
passed

npm run build
passed; only the existing Vite large-chunk warning

cargo fmt --check
passed

cargo check
passed

cargo test
19 passed; 0 failed
```

Two isolated portable smoke runs passed, each with controlled sidecar restart,
same-port recovery, layout survival, read-only MT5 lock, execution lock, and
zero surviving descendants after shutdown. The optional candlestick specialist
was safely deferred because it is not configured.

| Run | Report |
| --- | --- |
| 1 | `D:\GannFinancialAstro\soak\tauri_0.10.51-pfr-v2b-r7-xe1_20260817_053938\logs\native_soak_report.json` |
| 2 | `D:\GannFinancialAstro\soak\tauri_0.10.51-pfr-v2b-r7-xe1_20260817_054114\logs\native_soak_report.json` |

An additional manual check against the **packaged** sidecar confirmed the
XE1 profile and synthetic snapshot, seven immutable raw observations,
`AMBIGUOUS_CAUSE_FAIL_CLOSED`, empty Touched development input, and `false` for
price-data read, SBC read, Fields path, and execution.

## Founder Physical Inspection Checklist

These are inspection steps, not an acceptance claim.

1. Open the portable executable or install the NSIS package.
2. Select **Experiments** in the top navigation.
3. Confirm the persistent red safety banner states the exact experimental,
   non-classical, non-validated, no-execution warning.
4. With **Synthetic fixture** selected, inspect the raw-evidence table and
   confirm it identifies the seven source observations, their role, causal
   identity, typed raw value, and source state without a price chart or
   market-direction claim.
5. Confirm the causal audit displays one directional vote per group, keeps the
   derived child audit-only, and marks the ambiguous causal group fail-closed.
6. Change only the named transform selector and confirm the comparison shows
   distinct derived state summaries while the raw table remains unchanged.
7. Select **Touched development** and confirm the raw table is empty, the
   state is unknown, and it does not become a flat neutral/directional wave.
8. Confirm the trial ledger calls April 2025 `TOUCHED_DEV`, not a pristine
   holdout or financial validation result.
9. Return to Chart, Fields, and Chakra and confirm their existing surfaces
   remain separate; no XE1 state is presented as SBC confirmation, a Fields
   input, a price forecast, an Auto Suggest, or a trade control.

## Locked State and Limitations

- `XE1_EXISTING_INFRASTRUCTURE_AUDITED=true`
- `XE1_RAW_EVIDENCE_IMMUTABLE=true`
- `XE1_ROLE_BINDINGS_VERSIONED=true`
- `XE1_CAUSAL_GROUPING_IMPLEMENTED=true`
- `XE1_AMBIGUOUS_CAUSE_FAILS_CLOSED=true`
- `XE1_MODIFIER_ABLATION_IMPLEMENTED=true`
- `XE1_POSITIVE_MODIFIER_CANNOT_FLIP_SIGN=true`
- `XE1_CONFIDENCE_SEPARATE_BY_DEFAULT=true`
- `XE1_STATE_VECTOR_IMPLEMENTED=true`
- `XE1_EXPERIMENTAL_OSCILLATOR_VISIBLE=true`
- `XE1_TRIAL_LEDGER_IMPLEMENTED=true`
- `APRIL_2025_STATUS=TOUCHED_DEV`
- `MODE_1_CHANGED=false`
- `TRAILOKYA_SOURCE_SEMANTICS_CHANGED=false`
- `ARGHA_RUNTIME_PROMOTION_CHANGED=false`
- `FIELDS_FORMULA_CHANGED=false`
- `AUTO_SUGGEST_ADDED=false`
- `ML_ADDED=false`
- `MT5_ADDED=false`
- `EXECUTION_ALLOWED=false`

The only populated dataset is intentionally synthetic. No classical doctrine,
price data, price outcome, SBC state, Fields path, Auto Suggest, ML, MT5,
financial validation, or execution is used. This candidate is pending founder
inspection and acceptance.
