# Gann Astro Desk 0.9.0 Tauri Hybrid Release

Date: 2026-07-14 IST

## Release decision

Gann Astro Desk 0.9.0 replaces the PyWebView desktop shell with a Tauri 2 / Rust shell.
The React, TypeScript, and Lightweight Charts workspace is unchanged at the product layer.
The validated Python astrology, MT5, local Jyotish, generation, refresh, and shadow-ledger
services run as a managed private-loopback sidecar under the Rust process.

This is a compatibility migration, not a scientific-engine rewrite. It preserves the
existing deterministic contracts and keeps every execution path disabled.

## Runtime architecture

- Rust owns the native window, child-window lifecycle, private backend ports, sidecar
  process, and graceful shutdown.
- The frontend resolves the random backend address through the typed Tauri command
  `backend_runtime`; browser/Vite development continues to use relative `/api` routes.
- The frontend refuses a runtime with an unknown sidecar contract, a non-loopback URL, or
  `executionAllowed=true`.
- Python sidecar contract: `GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1`.
- The sidecar owns the Flask API, MT5 read-only gateway, corrected-data workers, local
  Jyotish/Ollama integration, Codex bridge, automatic refresh, and shadow ledger.
- Rust sends `shutdown` over the child's stdin and waits up to eight seconds before a kill
  fallback. Source and packaged tests both exited with code zero; native app shutdown left
  no Tauri or Python sidecar process behind.

## D-drive toolchain

- Rust 1.97.0 and Cargo 1.97.0:
  - `D:\Rust\rustup`
  - `D:\Rust\cargo`
  - `D:\Rust\targets`
- Visual Studio Build Tools 2022 17.14.35:
  - `D:\VisualStudio\2022\BuildTools`
  - MSVC 19.44.35228
  - Windows SDK 10.0.26100
- Visual Studio package/cache paths are on D:. Windows SDK servicing files and the Visual
  Studio installer service retain unavoidable system-managed files on C:.

## Release artifacts

- Portable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Portable executable SHA-256:
  `DCB4874CD3A6900597BC88A0817D467BD55EC3F1B5514FB95A2E72E06F73FE33`
- NSIS installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.9.0_x64-setup.exe`
- Installer SHA-256:
  `94C523AE64C81FAA7CAEF497DC845FA6A6BEC1037A8C7F5992F7862ADD8BDC2C`
- Release tree: 1,451 files / 885,106,458 bytes including the installer and manifest.
- Rust shell executable: 8,771,584 bytes.
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.8.0_20260714_091158`

The NSIS installer is not code-signed. The portable folder remains the primary verified
artifact until a signing identity is intentionally provisioned.

## Safety and contract verification

Real application state was opened through the promoted Tauri candidate and returned:

- MetaQuotes-Demo connected;
- `tradeAllowed=false`;
- prospective refresh `executionAllowed=false`;
- local Jyotish ready on `qwen2.5:3b`, analysis-only and execution-disabled;
- shadow chain valid;
- seven decisions and seven pending outcomes preserved;
- frozen trial ID unchanged:
  `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`.

Manual chart drawings and Square of Nine remain excluded from Auto Suggest, timestamp-safe
live inference, the shadow ledger, and execution.

## Verification completed

- Python: 113 tests passed.
- Frontend: Oxlint passed; 15 Vitest tests passed; TypeScript/Vite production build passed.
- Rust: `cargo check`, rustfmt, and Clippy with `-D warnings` passed.
- Source sidecar: health, read-only lock, and graceful shutdown passed.
- Packaged sidecar: health, read-only lock, execution lock, and graceful shutdown passed.
- Native release:
  - main chart rendered with H1 candles, aspect windows, SR levels, inspector, and activity
    dock;
  - Analyze Aspect opened in a separate Tauri window;
  - standalone Square of Nine rendered and remained separate from the market chart;
  - MT5 and local Jyotish status rendered;
  - app close terminated the managed sidecar without an orphan.
- Portable and installer hashes match the release manifest.
- `git diff --check` passed before documentation update.

## Deliberate next gates

1. Keep collecting the frozen prospective sample without changing its policy.
2. Add signed distribution only after a code-signing identity is available.
3. Profile real bottlenecks before porting any Python engine module to Rust; require fixture
   parity and contract tests for each port.
4. Do not move MT5 order placement into this process. Any execution project remains a
   separate, explicitly authorized and independently validated system.
