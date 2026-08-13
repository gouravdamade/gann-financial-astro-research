# Corrected Chart Generation Worker Recovery

## Scope

This bounded desktop recovery fixes a Windows packaging failure where a corrected
transit-to-natal generation child could remain alive before reaching the Python
worker module. It does not alter astronomy calculations, source evidence,
polarity, SBC, scoring, Auto Suggest, MT5 execution, or any research gate.

## Root Cause

The desktop sidecar launches the packaged backend executable again for isolated
event and SR-touch workers. The child inherited the parent PyInstaller bootstrap
environment. On the affected live desktop instance, the generated event worker
remained in startup wait state with no CPU work and no output artifact. The old
job surface only reported a fixed 10 percent event stage, so the failure looked
like chart computation instead of a failed worker startup.

## Recovery

- Frozen worker subprocesses now set `PYINSTALLER_RESET_ENVIRONMENT=1` so each
  worker starts as an isolated executable.
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

Focused worker and real artifact-generation tests cover the new heartbeat and
the PyInstaller reset environment. A replacement Windows candidate is required
before desktop use because the previous `0.10.40` executable cannot receive a
source-only fix.
