# PFR-V2B-R6-N1 Test Quality Audit

## Classification

| Area | Existing primary protection | Classification | N1 action |
| --- | --- | --- | --- |
| Trailokya TD1 target map | ordered target golden records | EXACT_GOLDEN | retained |
| Trailokya TD2 contracts | representative exact values | EXACT_GOLDEN but incomplete | expanded to full tables and all Latta offsets in `8bb6a0e` |
| Trailokya TD3 records | new independent hand-locked candidates, fractions and 28 row direction/duration list | EXACT_GOLDEN / NEGATIVE_FAIL_CLOSED | added |
| Trailokya source-only geometry | source-profile/motion/unknown checks | NEGATIVE_FAIL_CLOSED | added legacy grid-borrow refusal |
| Pair-relative field | interval union and unknown propagation | INVARIANT / PROPERTY | audited; formula unchanged |
| Synchronized range | request identity and guardrail responses | INTEGRATION | audited |
| Agarwal/BPHS fixtures | source packets and UI status tests | EXACT_GOLDEN / INTEGRATION | no semantic change |
| Full Python suite | cross-module regression | REGRESSION | rerun after N1 changes |
| Frontend/Tauri suite | UI and transport behavior | UNIT / INTEGRATION | rerun before final N1 commit |

## Tautology findings

No TD1 or TD2 exact source-table tests derive their expected values from the
same YAML payload they test. TD3 follows the same rule: its expected
verse/nakshatra/direction/duration sequence is hand-locked inside the test.

The remaining risk is not a test tautology but source-transcription scope:
commodity descriptions preserve conservative translated wording and must not
be treated as modern normalized commodities. The contract therefore blocks all
market and FX use.

## Negative gate coverage added by N1

- A missing desktop runtime execution lock is rejected, not treated as false.
- A missing companion top-level or capability execution lock is rejected.
- Trailokya source-only geometry rejects the generic legacy grid and fails
  closed when the source-native adapter is absent.
- TD3 source data explicitly cannot become runtime, a generic SBC reducer,
  score, polarity, forecast, Fields input, Auto Suggest, ML, MT5 or execution.

## Remaining weak areas

- Browser/desktop physical layout tests remain component-focused; the existing
  product needs a separately authorized E2E smoke run when the next packaged
  candidate is built.
- Long-running generation and MT5 recovery use mocks in most unit tests. The
  existing full regression exercises contracts, not a live broker.

## N1 verification result

The final N1 run completed with `749 passed`, one intentionally skipped
external-witness test, and `16` subtests in Python. Frontend transport tests
completed with `21` assertions across three files; the full frontend suite
completed with `163` assertions across 37 files. Rust has 19 passing unit
tests. The test set proves fail-closed source and transport boundaries, not
financial validity or live-broker behavior.
