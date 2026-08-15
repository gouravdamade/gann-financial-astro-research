# PFR-V2B-R6-SBC-A2 Founder Inspection Candidate

Status: `FOUNDER_INSPECTION_CANDIDATE` — implementer evidence only; not founder acceptance.

## Source and Scope

- Candidate version: `0.10.47-pfr-v2b-r6-sbc-a2`
- Source commit: `25274c68b99d87a43c24c98c5f83604565cff340`
- Source checkout: clean at packaging; release manifest `source_git_dirty = false`
- Scope: `A2_SCOPE_GEOMETRY_STRENGTH_INSPECTOR_ONLY`
- Profile contract: `AGARWAL_GEOMETRY_STRENGTH_INSPECTOR_V1`
- Execution: `executionAllowed = false`
- Chapter 20: `FINANCIAL_HYPOTHESIS_LEDGER_ONLY`

The candidate reads the committed A1R3 source-derived geometry and strength
fixtures. It does not implement an Agarwal Vedha operator, rays, market
direction, polarity, scores, Fields/pair influence, Auto Suggest, ML, MT5 or
execution. The four private p.145 photographs and the historical scan are not
included in Git or the candidate.

## Candidate Artifacts

- Portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.47-pfr-v2b-r6-sbc-a2\GannAstroDesk.exe`
  - SHA-256: `BB1759AEE7A153BA0F7EB8ADB92080DE334E5DE502C2EA7E9B0FC087197FBB05`
- Installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.47-pfr-v2b-r6-sbc-a2\Gann Astro Desk_0.10.47-pfr-v2b-r6-sbc-a2_x64-setup.exe`
  - SHA-256: `189F64BEC8223B7C40D5325182F98608A5B2A9288D0997C786E7C14779E7B640`
- Sidecar SHA-256: `56283B6602E24E36BEBBB9782B0273B5C30F03740EE36A82C2F40B81DFDEDA5C`
- Manifest: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.47-pfr-v2b-r6-sbc-a2\release.manifest.json`
- Checksums: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.47-pfr-v2b-r6-sbc-a2\SHA256SUMS.txt`

## Verification

| Gate | Command/result |
|---|---|
| Oxlint | `npm run lint` — passed |
| Focused frontend | `npm run test -- src/agarwalSourceInspector.test.tsx src/chakraLabWorkspace.test.tsx` — 2 files, 22/22 passed |
| Full frontend | `npm run test` — 37 files, 159/159 passed |
| Focused backend | `python -m unittest discover -s backend -p "test_agarwal_source_inspector.py" -v` — 5/5 passed |
| Full backend | `python -m unittest discover -s backend -p "test_*.py" -v` — 214/214 passed |
| Production build | `npm run build` — passed |
| Rust formatting | `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` — passed |
| Rust check | `cargo check --manifest-path src-tauri/Cargo.toml` — passed |
| Rust tests | `cargo test --manifest-path src-tauri/Cargo.toml` — 18/18 passed |

## Packaged Smoke Runs

Both runs used the exact portable candidate and the existing native soak
procedure with `-DurationSeconds 20 -AllowClosedMarketMt5Defer`.

1. `D:\GannFinancialAstro\soak\tauri_0.10.47-pfr-v2b-r6-sbc-a2_20260815_000652\logs\native_soak_report.json`
2. `D:\GannFinancialAstro\soak\tauri_0.10.47-pfr-v2b-r6-sbc-a2_20260815_000816\logs\native_soak_report.json`

Both reports: `passed = true`, no failed checks, initial health true,
recovered health true, sidecar PID changed after restart, layout survived,
execution remained false, and no descendant survived clean shutdown. Both are
conditional only because the optional candlestick specialist pack is not
configured.

A direct packaged launch rendered the normal chart. Windows then presented a
Firewall permission prompt for the fresh Tauri binary. Automation did not
accept or alter Windows security settings. The physical Agarwal visual check
therefore remains pending for the founder/user.

## Founder Inspection Checklist

1. Open the portable candidate and handle any Windows Firewall prompt according to the machine's security policy.
2. Open `Chakra` and choose `Agarwal 2000 Research`.
3. Confirm the visible badges say `GEOMETRY + STRENGTH SOURCE CLOSED`, `VEDHA NOT READY` and `READ ONLY`.
4. Confirm the board shows 81 cells with EAST at top, WEST at bottom, NORTH at left and SOUTH at right.
5. Select multiple cells and verify literal label, varga number, layer, p.145, packet ID and source status.
6. Confirm p.144 allocation groups are shown as provenance/consistency evidence, not a second runtime geometry engine.
7. Confirm the seven Agarwal strength rows are source records and no master score appears.
8. Confirm Vedha reads `DEPENDENCY_NOT_READY` and no rays or simulated paths appear.
9. Confirm Chapter 20 is labeled `FINANCIAL_HYPOTHESIS_LEDGER_ONLY`, `NOT VALIDATED`, `NOT FX-MAPPED` and `NOT EXECUTABLE`.
10. Switch to Phaladeepika and Trailokya and confirm their state remains separate.
11. Confirm Fields, BPHS and normal Chakra workflows still behave normally.
12. Confirm no bullish/bearish output, pair field change, Auto Suggest, ML, MT5 order or execution control is enabled.

Founder acceptance is intentionally not recorded here.
