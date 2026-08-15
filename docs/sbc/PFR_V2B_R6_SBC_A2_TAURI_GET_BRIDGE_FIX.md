# PFR-V2B-R6-SBC-A2 Tauri GET Bridge Fix

Status: implementation correction. This record does not alter the accepted
Agarwal source scope or constitute founder acceptance.

## Fault

The Windows-only Tauri command for `Agarwal 2000 Research` sent a `POST` to the
read-only sidecar endpoint `/api/chakra-lab/agarwal-source-profile`. The
endpoint is intentionally declared as `GET`, matching the browser runtime.
FastAPI therefore returned a non-JSON method error and the native response
parser misleadingly reported an invalid JSON failure.

## Correction

- Added an authenticated `get_private_json` bridge helper with the existing
  loopback-only connection and `X-Gann-Astro-Token` contract.
- Routed `chakra_lab_agarwal_source_profile` through the `GET` helper.
- Improved non-success response parsing so a non-JSON sidecar response reports
  its HTTP status rather than appearing as a JSON decoding error.
- Extended the native portable smoke procedure to call the real Agarwal source
  endpoint and require the immutable read-only contract, 81 cells, and
  `VEDHA DEPENDENCY_NOT_READY`.

## Boundaries Preserved

This repair does not alter the source fixture, A2 scope, Vedha readiness,
Chapter 20 status, Fields, polarity, scoring, Auto Suggest, ML, MT5, or
execution locks.

## Regression Coverage

The native bridge test establishes a loopback server and asserts the exact
`GET /api/chakra-lab/agarwal-source-profile` request, authenticated header,
and absence of a request body. The parser test also covers a non-JSON `405`
response.
