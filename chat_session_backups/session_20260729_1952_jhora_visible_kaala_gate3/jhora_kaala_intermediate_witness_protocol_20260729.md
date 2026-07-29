# Jagannatha Hora Kaala Intermediate Witness Protocol

Contract: `GANN_JHORA_KAALA_INTERMEDIATE_WITNESS_V1`

## Decision

Production Ayana, aggregate Kaala, and full Shadbala remain unchanged and
uncertified. Exact-time recapture resolved the apparent case-8 Hora conflict:
the original JHD text encoded `19.500` as JHora packed time `19:50`, not decimal
hour `19:30`. The corrected visible case-8 table awards Moon `60` virupa and
all other planets `0`, matching the local profile. The same exact instant was
then shown in JHora as LMT `23:18:36.072`; the uncropped Key Info view displays
`Sunrise: 6:22:22`. The narrow visible Hora boundary packet is therefore
complete.

The historical Ayana question is now externally observed rather than inferred.
The seven visible 1889 tropical longitudes reproduce Moon and Jupiter within
the frozen tolerance, but miss Sun, Mars, Mercury, Venus, and Saturn by
`2.127890`, `1.105863`, `1.073595`, `1.037835`, and `0.980442` virupa. The
tropical-longitude candidate is therefore rejected as a complete JHora
replication.

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

The validator preserves a complete, provenance-valid external observation even
when the candidate formula fails it. It separately reconstructs Ayana from
every supplied intermediate and reports disagreement with the visible JHora
Ayana value against the unchanged `0.5`-virupa tolerance. A formula mismatch
therefore rejects the formula candidate, not the evidence packet. A
tropical-longitude candidate is not promoted merely because it improves the
aggregate pass count.

## Provenance Rules

1. Use pinned Jagannatha Hora `8.0.0.0` with executable SHA-256
   `3DDBE5FB0458AD1F0AD91B002C7EFB8BBA9F08891D3F46190ABA97D570B17908`.
2. Preserve the settings hash already used by the locked Shadbala witness.
3. Save uncropped visible evidence, hash it, and bind each copied row to it.
   When one JHora view cannot show every field, use a hashed JSON evidence
   bundle whose own validator checks every referenced source and hash.
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

The assistant hashes the selected evidence, validates any JSON evidence bundle,
binds reviewer and UTC capture time, and validates the matrix before writing a
completed packet under
`status/evidence/jhora_kaala_intermediate_20260729/`. It does not read JHora
automatically, fill a value from the comparator, derive a missing visible
value, overwrite either pending template, certify a formula, or unlock
execution.

## Current Result

Status: `visible_packet_complete_formula_candidate_rejected`

- Exact-time JHora fixture serialization is guarded by
  `jhora_fixture_file.py`; the witness assembler and capture assistant refuse
  stale packed times.
- The exact-time visible Hora matrix is `35/35`, including Moon as the case-8
  Hora lord.
- The completed Hora packet is stored in
  `status/evidence/jhora_kaala_intermediate_20260729/`
  `jhora_hora_boundary_witness_completed.csv` with SHA-256
  `AF2CE318E2955506246960C9C1E7EA5CB3A17678E38F57C4AE5D80076F5BA32E`.
- Its source bundle is
  `status/evidence/jhora_kaala_witness_20260727/`
  `case_8_event_start_exact_hora_boundary_evidence_20260729.json`. It binds
  the exact civil fixture, LMT conversion, visible sunrise, exact Kaala table,
  and accessibility transcription.
- The seven-planet 1889 tropical position transcription is stored in
  `status/evidence/jhora_kaala_witness_20260727/`
  `gann_reference_tokyo_tropical_positions_visible_20260729.csv`.
- The completed Ayana observation packet is stored in
  `status/evidence/jhora_kaala_intermediate_20260729/`
  `jhora_ayana_intermediate_witness_completed.csv`.
- Its status is
  `valid_ayana_observation_written_formula_candidate_rejected`; the five
  residuals above remain visible and no tolerance was widened.
- Pinned JHora was restored to Raman after the temporary Tropical capture.
- Both visible evidence packets are complete with no provenance issues. The
  five historical Ayana formula residuals remain above `0.5` virupa, so the
  formula candidate is rejected and `productionChangeAllowed` remains false.
- No sunrise, Hora award, tropical position, or Ayana value was inferred or
  reverse-engineered.
