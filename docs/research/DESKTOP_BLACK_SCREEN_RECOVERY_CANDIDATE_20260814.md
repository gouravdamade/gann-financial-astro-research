# Desktop Black-Screen Recovery Candidate - 2026-08-14

## Scope

This is a desktop rendering and window-recovery candidate only. It does not
change astronomy, source doctrine, polarity, Fields, BPHS, Auto Suggest, MT5
execution, or any financial-validation gate.

## Incident Evidence

The reported black application state was investigated on the local machine.
The relevant observations were:

- an obsolete `0.10.40` desktop candidate and its corrected-generation worker
  were still active;
- the current `0.10.43` candidate's native window had an invalid off-desktop
  rectangle of `-25600, -25600`;
- a clean isolated launch of the exact existing portable executable rendered a
  complete chart workspace, demonstrating that the packaged sidecar and chart
  assets were functional.

The persisted WebView folder was retained as a non-destructive backup during
the investigation. It was not established as the cause of the black state.

## Source Change

Commit: `efa3e2876417f1dee8e589301be5cf415ee10e5c`

- Tauri now requests a centered `1280 x 800` main window with a `1024 x 640`
  minimum size.
- `index.html` has a visible static opening state before JavaScript execution.
- `src/main.tsx` has a React error boundary and bootstrap failure diagnostic.
- Global asynchronous errors are diagnostic-only and cannot replace a usable
  workspace with a fatal screen.

## Source Verification

- `npm run lint`: passed.
- `npm test`: passed, 35 files / 151 tests.
- `npm run build`: passed.
- `cargo fmt --check`: passed.
- `cargo check`: passed.

The production build still reports the existing Vite advisory for a large
minified chunk. It is not related to black-screen recovery and no unrelated
chunking refactor was included.

## Immutable Candidate

Version: `0.10.44-black-screen-recovery`

- portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.44-black-screen-recovery-tauri\GannAstroDesk.exe`
- installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.44-black-screen-recovery-tauri\Gann Astro Desk_0.10.44-black-screen-recovery_x64-setup.exe`
- source state recorded by manifest: clean
- portable SHA-256: `C5C2F3E43A1DC3EB7635317249B69E7FC0402F01218EB339F54C1AB014EE0F41`
- installer SHA-256: `AF8F2F717D9693F8F00EC926A2DD6B438CD5819402A729D2C754D5E910D90D40`

## Candidate Verification

Two isolated portable smokes passed under temporary data roots. Both verified:

- backend health;
- all execution locks remain false;
- a controlled sidecar restart returns on the same port;
- a persisted layout survives recovery;
- the application closes without descendant process survivors.

The candlestick corpus is optional and absent in the isolated smoke roots; this
was recorded as a safe deferred check, not a failure. The exact portable was
also launched at `1280 x 820` and a native-window capture confirms that the
chart UI painted rather than remaining black:

`D:\GannFinancialAstro\soak\window_captures_20260814\candidate_01044_visual.png`

## Founder Check

This candidate is ready for visual inspection, not founder acceptance. Open
the portable executable above, confirm that the first window is visible on the
desktop, then reopen it after closing. The expected fallback during a genuine
frontend bootstrap failure is an explicit opening or recovery message, never a
silent all-black canvas.
