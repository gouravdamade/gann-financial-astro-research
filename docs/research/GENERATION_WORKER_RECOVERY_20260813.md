# Corrected Chart Generation Worker Recovery

## Scope

This bounded desktop recovery fixes a Windows packaging failure where a corrected
transit-to-natal generation child could remain alive before reaching the Python
worker module. It does not alter astronomy calculations, source evidence,
polarity, SBC, scoring, Auto Suggest, MT5 execution, or any research gate.

## Root Cause

The desktop sidecar launches the packaged backend executable again for isolated
event and SR-touch workers. The sidecar correctly keeps its own standard-input
pipe open so the Rust supervisor can request graceful shutdown. The generation
worker neither reads nor needs standard input, but it inherited that managed
pipe. In the packaged desktop path, the inherited handle left the nested frozen
worker in startup wait state before it reached the generator module.

This was reproduced with the exact packaged `GannAstroBackend.exe`: direct
execution of the 400-combination request completed in seconds, while launching
the sidecar with the same piped standard input as the Rust desktop supervisor
reproduced the fixed 10 percent watchdog failure. The existing PyInstaller
environment reset remains a separate worker-isolation safeguard.

## Recovery

- Frozen worker subprocesses now set `PYINSTALLER_RESET_ENVIRONMENT=1` so each
  worker starts as an isolated executable.
- Workers explicitly receive `stdin=DEVNULL` and `close_fds=True`; the sidecar's
  shutdown pipe stays private to the sidecar and cannot reach a nested generator.
- On Windows, a very short-lived UI read can deny the delete-share access needed
  for atomic progress-file replacement. Heartbeats now retry the atomic handoff
  briefly and, only if the lock remains, use a best-effort in-place snapshot.
  A transient progress-reporting lock can therefore never abort event generation.
- The corrected transit-to-natal generator writes an atomic
  `CORRECTED_TN_EVENT_PROGRESS_V1` heartbeat while compiling entity/aspect
  combinations. It contains generator identity and combination counts only.
- The generation manager maps this heartbeat from 10 to 52 percent and reports
  the active transit body, natal target, and aspect.
- A missing event-worker heartbeat for 120 seconds terminates the worker and
  reports an explicit startup failure instead of leaving the job indefinitely
  at 10 percent.

## Reproduction Evidence

Using the reported USDJPY H1 source and 2026-08-03 through 2026-08-13 calendar
range, the 10 by 10 entity grid with four selected aspects compiled 400
combinations into 45 event windows in 7.26 seconds. This checks the event
compiler only; it does not assess market direction.

## Verification Boundary

Focused worker and real artifact-generation tests cover the new heartbeat,
PyInstaller isolation environment, private worker input handle, and the Windows
progress-lock fallback. A replacement Windows candidate is required before desktop
use because previously installed executables cannot receive a source-only fix.
