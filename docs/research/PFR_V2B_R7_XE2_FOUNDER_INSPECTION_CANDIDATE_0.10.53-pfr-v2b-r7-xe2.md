# PFR-V2B-R7-XE2 Founder Inspection Candidate

## Release

- Milestone: `PFR-V2B-R7-XE2`
- Candidate version: `0.10.53-pfr-v2b-r7-xe2`
- Status: founder-inspection candidate; founder acceptance pending
- Source commit: `fc72f58531c079181d2a1281e9e5b48e5fa16b2e`
- Source git dirty state at packaging: `false`
- Candidate root: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.53-pfr-v2b-r7-xe2-tauri`
- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.53-pfr-v2b-r7-xe2-tauri\GannAstroDesk.exe`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.53-pfr-v2b-r7-xe2-tauri\Gann Astro Desk_0.10.53-pfr-v2b-r7-xe2_x64-setup.exe`

### Artifact hashes

- Portable SHA-256: `0A8275A76BF2EAC624DD182A9ECB6F91EDAA72D5A021E6D21A0A9D7162152536`
- Installer SHA-256: `DF1751905DD6316FB1C31C5742D28023F2B5F672FB1043351F858F7D743B8C7A`
- Backend sidecar SHA-256: `FF0144D7CB4743E7D7AD28ABE1F5D57851B0CD9D664240EB5CE32B6C1FD40E80`
- Manifest: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.53-pfr-v2b-r7-xe2-tauri\release.manifest.json`
- Checksums: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.53-pfr-v2b-r7-xe2-tauri\SHA256SUMS.txt`

## XE2 Scope

XE2 is a separate, read-only Experiments profile named
`XE2 scoped evidence`. It connects four verified USD April 2025 astronomical
event identities to their raw Moon speeds in `deg/day`. Every identity is
hash-linked to the verified founder-review packet and remains
`SINGLE_PASS_VERIFIED`.

The reviewed USD and JPY packets currently contain no founder polarity decision
and no evidence classification. Therefore XE2 admits no real signed market
evidence. Aspect geometry, raw speed, motion and the M0-M4 modifiers never
supply a market sign. The only signed channel is visibly labelled
`SYNTHETIC_SIGN_TEST_ONLY`, used solely to exercise the causal-scoped math.

The modifier tournament remains bounded:

- M0: base synthetic-sign test.
- M1: one causal-event-scoped positive speed multiplier.
- M2: separate raw-speed channel.
- M3: scoped interaction term.
- M4: direct-motion gate.

Each modifier binds to an exact `CAUSAL_EVENT_ID`; absent, mismatched or
ambiguous scope is rejected. There is no global modifier default, no stacking,
no curve fitting and no comparison winner. April 2025 remains `TOUCHED_DEV`.

## Verification

### Source and product checks

- Focused XE2 backend:
  `python -m unittest discover -s backend -p "test_xe2_scoped_evidence_service.py"`
  -> `8 passed`.
- XE1 regression:
  `python -m unittest discover -s backend -p "test_experimental_evidence_service.py"`
  -> `13 passed`.
- Full backend:
  `python -m unittest discover -s backend -p "test_*.py"` -> `236 passed`.
- Focused frontend:
  `npm test -- experimentalLabWorkspace.test.tsx` -> `4 passed`.
- Full frontend:
  `npm test -- --pool=threads --no-file-parallelism --testTimeout=15000`
  -> `39 files, 168 passed`.
- Broad Python regression: `python -m pytest -q` -> `780 passed, 1 skipped,
  16 subtests passed`. The single skip is the optional external JHora witness
  because `JHORA_WITNESS_CSV` was not configured.
- Lint: `npm run lint` passed.
- Production build: `npm run build` passed. The existing large-chunk advisory
  remains informational.
- Rust: `cargo fmt --check`, `cargo check` and `cargo test` passed; Rust tests
  were `19 passed`.

### Portable smoke runs

1. `D:\GannFinancialAstro\soak\tauri_0.10.53-pfr-v2b-r7-xe2_20260818_183134\logs\native_soak_report.json`
   passed.
2. `D:\GannFinancialAstro\soak\tauri_0.10.53-pfr-v2b-r7-xe2_20260818_183302\logs\native_soak_report.json`
   passed.

Both isolated runs had zero failed checks. They verified backend health,
read-only execution locks, source-profile contracts, layout creation, controlled
sidecar restart on the same port, recovered health, layout survival and clean
descendant shutdown. Both defer only the optional unconfigured candlestick
specialist. Each report records `execution_allowed=false`.

## Founder Physical Inspection Checklist

Use the exact packaged portable candidate, not the development server.

- Open **Experiments** and confirm the sticky banner remains visible:
  `EXPERIMENTAL - NOT CLASSICAL - NOT VALIDATED - NO EXECUTION`.
- Select **XE2 scoped evidence** in the research profile selector.
- Confirm the context reports `REAL ASTRONOMY: HASH-LINKED`,
  `SIGNED MARKET EVIDENCE: NONE`, `TOUCHED_DEV`, and
  `BLOCKED_NO_REAL_SIGNED_EVIDENCE`.
- Inspect the four source rows. Check that each displays a full event hash,
  an exact timestamp, its astronomical identity and a raw Moon speed in
  `deg/day`.
- Confirm the raw speed normalisation is shown separately from the market-sign
  channel, and its astronomical reference is visible.
- Inspect M0 through M4. Confirm each result is marked as a synthetic-sign test
  and no transform is called a winner, validated model or market forecast.
- Check the scoped modifier audit. Confirm it is tied to one exact causal-event
  ID and has no global fallback or stacking path.
- Confirm no outcome, price, SBC, Fields, live MT5, Auto Suggest, ML or
  execution input appears in XE2.
- Switch back to **XE1 synthetic baseline** and confirm its approved behavior
  remains unchanged.
- Repeat the empty-evidence presentation at a practical narrow desktop width,
  including 1366 x 768.

## Locked State

```text
XE2_EXPERIMENTAL_EVIDENCE_CONTRACT=XE2_CAUSAL_SCOPED_EVIDENCE_LAB_V1
XE2_REAL_ASTRONOMICAL_INPUT=HASH_LINKED_EVENT_IDENTITY_AND_RAW_SPEED
XE2_REAL_SIGNED_MARKET_EVIDENCE=NONE
XE2_SYNTHETIC_SIGN_CHANNEL=TEST_ONLY_NOT_MARKET_EVIDENCE
XE2_MARKET_OUTCOME_READ=false
XE2_LIVE_MT5_READ=false
XE2_GLOBAL_MODIFIER_DEFAULT_ALLOWED=false
XE2_MODIFIER_STACKING_ALLOWED=false
XE2_MARKET_DIRECTION=BLOCKED_NO_REAL_SIGNED_EVIDENCE
XE2_EXECUTION_ALLOWED=false
XE2_AUTO_SUGGEST_ALLOWED=false
XE2_ML_ALLOWED=false
XE2_FIELDS_OR_SBC_FUSION=false
```

This is a founder-inspection candidate only. It is not a market forecast, a
classical doctrine release, a financially validated model or an execution
package. Founder acceptance remains pending physical confirmation of this
candidate.
