# Sarvatobhadra Phase 4A: Timestamp-Safe Chakra Lab

Date: 2026-07-17

## Objective

Expose the source-profiled Sarvatobhadra Chakra foundation and Vedha guidance
inside Gann Astro Desk as a native, read-only research surface without allowing
market inference, Auto Suggest, trade generation, or MT5 execution.

## Runtime Contract

`SBC_CHAKRA_LAB_SNAPSHOT_V1` is the only Chakra Lab response contract. A
request contains:

- one offset-aware timestamp;
- an explicit `Asia/Kolkata` display timezone;
- latitude, longitude, and altitude;
- requested astronomy bodies;
- explicitly selected Vedha actors;
- explicit motion for Mars, Mercury, Jupiter, Venus, and Saturn;
- optional dignity, vowel, and name-initial context;
- explicit foundation, grid, and Vedha profile IDs.

The engine emits one canonical UTC `as_of_utc` value and sets
`evidence_cutoff_utc` to the same instant. Astronomy, Panchanga, rashi,
nakshatra, board context, actor readiness, Vedha rays, and guidance are derived
from the same foundation snapshot. The snapshot ID hashes scientific inputs and
profile identities.

## Fail-Closed Rules

- A naive timestamp is rejected.
- Unknown API fields are rejected.
- Variable-planet motion is never inferred. Missing motion returns
  `MOTION_REQUIRED` and excludes that actor from scoring.
- Unsupported actors remain outside the certified Vedha profile.
- The API and UI preserve `execution_allowed=false`.
- The response includes no market data, price, P/L, Auto Suggest, order, or
  financial label.
- The numerical ledger remains `guidance_only=true` and
  `financial_validation_status=NOT_VALIDATED`.

## Architecture

1. `sbc/chakra_lab.py` adapts one scientific foundation snapshot into the
   Chakra Lab contract.
2. `gann-astro-desk/backend/chakra_lab_service.py` validates the camel-case app
   request and invokes the adapter.
3. Flask exposes `POST /api/chakra-lab/snapshot` for private browser
   development.
4. Tauri exposes `chakra_lab_snapshot`; Rust posts directly to the managed
   loopback sidecar and returns JSON through IPC.
5. `ChakraLabWorkspace.tsx` renders the board, controls, readiness, evidence,
   and source-profiled guidance.

The PyInstaller sidecar specification includes the complete `configs/sbc`
directory, the SBC Python modules, `panchanga_doctrine`, and `swisseph`.

## UI Boundary

The Chakra tab is a compact operational research surface:

- timestamp/location controls;
- optional letter context;
- actor selection, explicit motion, and dignity controls;
- 81-cell board with context, ray, matched, and selected states;
- guidance ledger with favorable, adverse, net, and coverage values;
- actor readiness, matched contributions, and cell evidence.

It intentionally omits bullish/bearish calls, chart price, trading actions, and
LLM interpretation. Those remain separate future gates.

## Verification Evidence

Completed during Phase 4A implementation:

- all 226 Python repository tests passed;
- 32 frontend tests passed across nine files;
- the native Tauri IPC test proved Chakra Lab does not use browser `fetch`;
- the UI test proved the research ledger renders without bullish/bearish
  labels;
- the production TypeScript/Vite build passed;
- Oxlint passed;
- changed-file Ruff lint and format checks passed;
- `cargo fmt --check` passed;
- both Rust private-bridge tests passed;
- `git diff --check` passed, with only expected CRLF warnings.

Source-mode runtime verification also passed:

- the private API returned 81 cells;
- `as_of_utc` exactly matched `evidence_cutoff_utc`;
- `execution_allowed` and `financially_validated` remained false;
- three explicitly configured test actors were ready;
- the UI kept Jupiter at `MOTION_REQUIRED` until the user selected `MEAN`, then
  resolved it to the source-profiled FRONT direction;
- the 1280-pixel desktop layout displayed the complete board, evidence ledger,
  and usable actor controls without horizontal panel overflow;
- browser diagnostics reported no warnings or errors.

The PyInstaller sidecar build, Tauri EXE build, and packaged smoke test were not
performed. Stable Gann Astro Desk therefore remains `0.10.6`.

## Promotion Gate

Do not promote beyond Gann Astro Desk `0.10.6` until all of these pass:

1. Repeat the green source test/build/lint suite as release verification.
2. PyInstaller sidecar build and Tauri EXE build.
3. Packaged smoke test confirming deterministic snapshot identity and the
   read-only execution lock.
4. Independent doctrine/calculator comparison where the source program
   requires it.
5. Prospective out-of-sample testing before any financial interpretation.
