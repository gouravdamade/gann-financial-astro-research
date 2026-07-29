# SBC Timing-Profile Admission T0

Date: 2026-07-29

T0 turns the P0-R3 timing-profile prerequisite into an executable fail-closed
gate. It validates a user-supplied candidate in memory, hashes the exact JSON,
and checks that hash against a server-owned frozen source-certification
registry.

The repository intentionally ships an empty registry and no timing profile.
Therefore the current truthful state is `NO_PROFILE_LOADED`, with directional
engine, directional output, financial use, and execution unavailable.

The implementation is:

- `sbc/timing_profile_admission.py`
- `status/timing_phase_profile_registry.json`
- backend POST `/api/chakra-lab/timing-profile/admission`
- native read-only command `chakra_lab_timing_profile_admission`
- linked Chakra Audit `Timing gate` tab

This milestone adds no timing phase, direction, confidence, extra vote,
official ML note, Auto Suggest input, live-inference input, trade output, or
MT5 execution.
