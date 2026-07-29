# Jagannatha Hora Kaala Intermediate Witness Protocol

Contract: `GANN_JHORA_KAALA_INTERMEDIATE_WITNESS_V1`

## Decision

Production Hora, Ayana, aggregate Kaala, and full Shadbala remain unchanged and
uncertified. The formula-profile diagnostic found two narrow questions that
cannot be answered from the existing top-level JHora tables:

1. case 8 awards Hora to Saturn while the current source profile awards Moon;
2. tropical-longitude Kranti fits `30/35` Ayana rows and every recent row, but
   still misses five planets in the 1889 fixture.

No value in this packet may be inferred from local code, PyJHora, the existing
JHora result column, or another planet.

## Required Hora Capture

The Hora template contains seven rows for `case_8_event_start`, one for each
classical planet. A completed capture must visibly bind:

- the locked chart identity, location, timezone, and settings;
- JHora's apparent-tip sunrise expressed in local mean time;
- JHora's selected Hora lord;
- all seven visible Hora awards.

All seven rows must share one sunrise and one lord. Exactly one planet must
receive `60` virupa, the others must receive `0`, and the winner must match the
visible lord and the previously locked JHora Hora column.

This distinguishes a real sunrise-input difference from a formula guess. The
current local award changes across only `3.436256` minutes of sunrise input.

## Required Historical Ayana Capture

The Ayana template contains seven rows for `gann_reference_tokyo`
(`1889-02-11`). Capturing all seven avoids selecting only the five failed rows.
For each planet, record:

- visible JHora tropical longitude, visible JHora Kranti, or both;
- the visible JHora Ayana value;
- an uncropped evidence file that identifies the chart and field.

The validator reconstructs Ayana from every supplied intermediate and requires
agreement with the visible JHora Ayana value within the unchanged
`0.5`-virupa tolerance. A tropical-longitude candidate is not promoted merely
because it improves the aggregate pass count.

## Provenance Rules

1. Use pinned Jagannatha Hora `8.0.0.0` with executable SHA-256
   `3DDBE5FB0458AD1F0AD91B002C7EFB8BBA9F08891D3F46190ABA97D570B17908`.
2. Preserve the settings hash already used by the locked Shadbala witness.
3. Save uncropped visible evidence, hash it, and bind each copied row to it.
4. Record reviewer and timezone-aware UTC capture time.
5. Reject missing, duplicate, inferred, unhashed, non-finite, or
   top-level-inconsistent values.
6. Keep source certification, financial validation, ML admission, Auto
   Suggest, live inference, and execution false after packet completion. Those
   are separate gates.

## Commands

Create both pending templates:

```powershell
python jhora_kaala_intermediate_witness_protocol.py
```

Validate a completed packet:

```powershell
python jhora_kaala_intermediate_witness_protocol.py `
  --validate-hora <completed-hora.csv> `
  --validate-ayana <completed-ayana.csv>
```

## Guided Windows Assistant

Double-click:

`Launch_JHora_Kaala_Capture_Assistant.cmd`

The assistant provides three tabs:

1. `Hora boundary`: select one uncropped visible JHora evidence file and enter
   the visible sunrise in local mean time, visible Hora lord, and all seven
   visible `0/60` awards.
2. `Historical Ayana`: select one uncropped visible evidence file and enter
   visible tropical longitude, Kranti, or both plus visible Ayana for all seven
   classical planets.
3. `Verify packet`: inspect the same fail-closed machine status used by the
   certification report.

The assistant hashes the selected evidence, binds reviewer and UTC capture
time, and validates the matrix before writing a completed packet under
`status/evidence/jhora_kaala_intermediate_20260729/`. It does not read JHora
automatically, fill a value from the comparator, derive a missing visible
value, overwrite either pending template, certify a formula, or unlock
execution.

## Current Result

Status: `blocked_pending_visible_kaala_intermediate_witness`

The pinned JHora process is running and responsive, but its legacy window
refused a safe capture handle on both the initial and permitted recovery
attempt in the current Codex desktop session. No sunrise, tropical longitude,
or Kranti value was copied, inferred, or reverse-engineered.
