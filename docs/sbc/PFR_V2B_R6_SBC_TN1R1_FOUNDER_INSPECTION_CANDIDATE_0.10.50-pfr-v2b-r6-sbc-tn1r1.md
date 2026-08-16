# PFR-V2B-R6-SBC-TN1R1 Founder-Inspection Candidate

## Candidate

| Field | Value |
|---|---|
| Milestone | `PFR-V2B-R6-SBC-TN1R1` |
| Version | `0.10.50-pfr-v2b-r6-sbc-tn1r1` |
| Source commit | `36d16df475a49fc23e37726142e453700a5f35b8` |
| Source worktree at packaging | clean, `source_git_dirty=false` |
| Candidate status | founder inspection candidate; not accepted or stable |
| Candidate root | `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.50-pfr-v2b-r6-sbc-tn1r1-tauri` |
| Portable executable | `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.50-pfr-v2b-r6-sbc-tn1r1-tauri\GannAstroDesk.exe` |
| NSIS installer | `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.50-pfr-v2b-r6-sbc-tn1r1-tauri\Gann Astro Desk_0.10.50-pfr-v2b-r6-sbc-tn1r1_x64-setup.exe` |
| Release manifest | `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.50-pfr-v2b-r6-sbc-tn1r1-tauri\release.manifest.json` |
| Checksums | `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.50-pfr-v2b-r6-sbc-tn1r1-tauri\SHA256SUMS.txt` |

This candidate contains the TN1R1 layout-only correction. It does not change
Trailokya source content, target semantics, astronomy, Fields, polarity,
scoring, Auto Suggest, ML, MT5 or execution behavior.

## Artifact Hashes

| Artifact | SHA-256 |
|---|---|
| `GannAstroDesk.exe` | `69CFEE6E02F4C87E176DBBBDF41587EB963BA7FD0086C8A8DF985A022400BCAF` |
| `Gann Astro Desk_0.10.50-pfr-v2b-r6-sbc-tn1r1_x64-setup.exe` | `07A8BA528BA57D75E7453657694DDF7B46131F71DBA846E90CC37D20E2B394C0` |
| `backend/GannAstroBackend.exe` | `01564BDFB3419331826E6AA294BF392A89FA35A419E4DE8F4A6BA109DA9EA1D4` |

The manifest records the same source commit, hashes, `source_git_dirty=false`,
`chakra_lab_execution_allowed=false`, and
`mt5_execution_mode=read_only_market_data`.

## TN1R1 Correction

The native Trailokya inspector is now wrapped in one keyboard-focusable,
vertical scroll region inside the existing Chakra content track. The wrapper
uses `overflow-y:auto` and `overflow-x:hidden`; the outer desktop shell remains
bounded, and no nested whole-inspector scroll box was introduced.

The source board, 81-cell geometry, EAST/WEST/NORTH/SOUTH orientation, literal
labels, enumerated target authority, unknown states, profile isolation and
research/execution locks are unchanged. Switching between Trailokya and
Agarwal removes/restores the Trailokya scroll owner without changing the
selected source profile semantics.

Source-browser implementer evidence at 1280x720 measured a 650px scroll host
containing 1472px of inspector content. Scrolling to the end exposed the WEST
row, final audit content and the status footer. The packaged physical viewport
checks below remain founder-only.

## Verification

### Focused source tests

```text
python -m pytest -q test_trailokya_td1_native_source_contract.py test_trailokya_td1r1_source_correction.py test_trailokya_td1r2_final_glyph_correction.py test_trailokya_td2_source_closure.py test_trailokya_td3_source_ingestion.py
27 passed
```

The native-source contract test now matches the committed TN1 readiness record:
the TN1 product/runtime-change metadata is true, while all research and
execution safety locks remain false. This corrects a stale assertion only; no
source contract was changed.

### Frontend tests and build

```text
npm run test -- src/chakraLabWorkspace.test.tsx src/trailokyaNativeInspector.test.tsx
2 files, 21 tests passed

npm test
38 files, 164 tests passed

npm run lint
passed

npm run build
passed; Vite emitted only the existing large-chunk warning
```

### Backend and Rust

```text
npm run test:backend
Ran 215 tests in 300.924s; OK

cargo fmt --check
passed

cargo check
passed

cargo test
19 passed; 0 failed; 0 doc-test failures
```

### Packaged smoke runs

The established portable soak process was run twice against this exact
candidate. The packaged sidecar was allowed to defer the closed-market MT5
clock condition while remaining read-only.

| Run | Report | Result |
|---|---|---|
| 1 | `D:\GannFinancialAstro\soak\tauri_0.10.50-pfr-v2b-r6-sbc-tn1r1_20260816_171303\logs\native_soak_report.json` | PASS, conditional only for optional candlestick specialist |
| 2 | `D:\GannFinancialAstro\soak\tauri_0.10.50-pfr-v2b-r6-sbc-tn1r1_20260816_171712\logs\native_soak_report.json` | PASS, conditional only for optional candlestick specialist |

Each run verified:

- packaged app launch and healthy sidecar;
- Chakra snapshot with 81 cells and timestamp guardrails;
- Agarwal source profile with 81 cells and `VEDHA DEPENDENCY_NOT_READY`;
- planetary-line research contract;
- execution and MT5 read-only locks;
- persisted layout creation and survival after forced sidecar restart;
- changed sidecar PID with same-port recovery;
- zero surviving descendants after clean shutdown.

The optional candlestick specialist was reported as
`candlestick_specialist_optional_not_configured`; it did not fail the safety
or Trailokya checks. The first exploratory run with the helper's original
10-second POST timeout recorded a timeout while retrieving the packaged
candlestick evidence. The packaging-only soak helper was then rerun with a
60-second request timeout for the slow event-detail/OHLC extraction; the two
reported runs above passed. No product source or candidate binary changed as a
result.

## Founder Physical Inspection Checklist

These are implementer-provided instructions, not an acceptance claim. Inspect
the packaged candidate at:

- 1920x1080, Windows scale 100%;
- 1920x1080, Windows scale 125%;
- 1920x1080, Windows scale 150%;
- 1600x900;
- 1366x768.

Open **Chakra -> Board -> Trailokya 1972 Research** and verify:

1. The full native inspector has one usable vertical scrollbar or equivalent
   wheel/PageUp/PageDown/Home/End navigation.
2. The 81-cell board is visible without clipping, with EAST at top, WEST at
   bottom, NORTH at left and SOUTH at right.
3. The lower target, audit and status content is reachable at every required
   size.
4. The scroll region can receive keyboard focus and focus remains visible.
5. Jyeshtha + LEFT remains the source-ordered direct sequence; FRONT remains
   the single Pushya target.
6. Unknown and ambiguous states remain visible and are not converted to zero,
   neutral, polarity or a score.
7. Switching to Agarwal and back preserves profile isolation and restores the
   Trailokya scroll region.
8. Fields, Chart, Square of Nine and BPHS workflows still open normally.
9. No price forecast, directional wave, Auto Suggest, ML, MT5 order control or
   execution affordance appears.

Physical packaged-window acceptance remains pending founder inspection.

## Locked State

`executionAllowed=false` remains enforced. TN1R1 adds no polarity, score,
price forecast, Fields polarity, Auto Suggest, ML, MT5 or execution path. The
Trailokya native adapter remains source-only and the Fields lane remains
`GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` where applicable.

## Known Limitations

- The optional candlestick specialist remains unconfigured in the packaged
  candidate and is explicitly deferred by the smoke contract.
- The measurements in the source browser were implementer evidence at
  1280x720; the required physical packaged viewport review is still the
  founder's decision.
- Existing unrelated local SQLite/log changes in the active development
  checkout were deliberately not included in the source commit or candidate.

## Status

`PFR-V2B-R6-SBC-TN1R1` is implemented and packaged as a founder-inspection
candidate. It is not promoted, stable, or founder-accepted.
