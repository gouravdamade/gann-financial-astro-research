# Gann Astro Desk 0.9.2 Drawing, Fibonacci, and Source-Trust Release

Date: 2026-07-15

## Scope

This release improves manual chart research and hardens the local Jyotish RAG
source boundary. It does not change the frozen prospective policy, timestamp-safe
Auto Suggest/live-inference engine, MT5 permissions, or any execution lock.

## Chart Research Tools

- Horizontal and vertical lines now auto-select after placement and expose a
  chart-side edit, hide, lock, and delete toolbar.
- The layout toolbar exposes a visible `Objects` command and object count so saved
  drawings are discoverable without knowing a keyboard shortcut.
- Added persistent two-anchor Fibonacci retracement with editable levels, labels,
  prices, extension, color, width, style, opacity, lock, hide, drag, and delete.
- Fibonacci, Gann fans, Square of Nine, and all manual drawings remain research
  annotations. They are not inputs to Auto Suggest, live inference, the prospective
  shadow ledger, or order execution.

## Source-Trust Boundary

The local RAG now labels retrieved material instead of treating every unknown
source as classical doctrine:

- `classical_doctrine`: recognized root-text witnesses;
- `reference_commentary`: implementation and interpretive references;
- `source_provenance`: edition, attribution, recension, and page-boundary audits;
- `hypothesis_reference`: literary and public-forum research claims;
- `unclassified_reference`: unknown material that cannot inherit doctrine status.

Gann and forum material is opt-in by explicit query vocabulary. Prompt and verifier
guards prohibit using it as doctrine, proof, certification, ground truth, or a
reason to alter deterministic output. The legacy case explainer follows the same
layering and drift checks.

## Chakra and Gann Research Result

- Phaladeepika verse 26.48 mentions Sarvatobhadra vedha, while the following scan
  pages include editor-supplied material attributed to other works. Those page
  boundaries are recorded rather than silently merged.
- Sarvatobhadra sources contain grid and convention plurality. Sudarshana Chakra is
  recension-sensitive across BPHS editions. Neither Chakra is implemented as a
  predictive calculator until a convention, formulas, fixtures, and out-of-sample
  validation are certified.
- Gann's novel supports only the historical fact that Gann described a veiled
  secret; it does not establish a specific trading algorithm.
- Public Forex Factory ideas are stored as unverified hypotheses that may seed a
  prospective test but cannot enter production inference directly.

Detailed source links, page findings, and adoption gates are in
`chakra_gann_source_audit_20260715.md`.

## Release Artifacts

- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Executable SHA-256:
  `ACD4EE927826EB850625F5592895755608A04C17D3102601377C842D9DB76CB6`
- NSIS installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.9.2_x64-setup.exe`
- Installer SHA-256:
  `B04936B3D175991A7E908393B7C5238C54E82F7493DD8DA10CE3E80B774E3B18`
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.9.1_20260715_082720`
- Pre-promotion live-state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.9.2_promotion_20260715_082622`

The rollback archive and promoted release each contain 1,452 files including the
manifest. Both executable and installer hashes match their respective manifests.
The installer is not code-signed.

## Verification

- Source/corpus doctrine tests: 12 passed.
- Backend tests: 45 passed against an isolated database copy; repository tests no
  longer mutate or depend on the live runtime artifact tables.
- Root guardrail tests: 15 passed.
- Frontend: 18 Vitest tests passed with one worker; lint passed; TypeScript/Vite
  production build passed. The existing 509.49 kB main-chunk warning remains a
  future code-splitting opportunity.
- Ruff passed for all changed Python modules and tests.
- PowerShell packaging and soak scripts parsed successfully.
- Rust: formatting, `cargo check`, test, and Clippy with warnings denied passed.
- Native candidate soak:
  `D:\GannFinancialAstro\soak\tauri_0.9.2_20260715_022306\logs\native_soak_report.json`
  passed all 11 health, read-only MT5, persistence, same-port recovery, diagnostics,
  execution-lock, and descendant-cleanup checks.
- Browser QA placed, edited, dragged, hid, locked, and deleted Fibonacci and line
  objects, then removed the temporary QA drawings. No browser console errors remained.

MT5 remains read-only with `tradeAllowed=false`; every runtime execution guard
remains false.
