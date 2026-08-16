# PFR-V2B-R6-SBC-TN1R1 Founder Acceptance

## Accepted Candidate

| Field | Recorded value |
|---|---|
| Candidate version | `0.10.50-pfr-v2b-r6-sbc-tn1r1` |
| TN1R1 source commit | `36d16df475a49fc23e37726142e453700a5f35b8` |
| Candidate/report commit | `18973a56832b12ba006633ce541d28899d65aad0` |
| Acceptance recorded | 2026-08-17 IST |
| Founder decision | `FOUNDER_ACCEPTED` |
| Portable SHA-256 | `69CFEE6E02F4C87E176DBBBDF41587EB963BA7FD0086C8A8DF985A022400BCAF` |
| Installer SHA-256 | `07A8BA528BA57D75E7453657694DDF7B46131F71DBA846E90CC37D20E2B394C0` |

The founder physically inspected and accepted the packaged TN1R1 product. The
accepted scope is the Trailokya native inspector viewport repair only.

## Founder-Verified Behaviour

- Vertical scrolling reaches the entire inspector and all 81 board cells.
- EAST, WEST, NORTH and SOUTH orientation is correct.
- Jyeshtha LEFT, FRONT (Pushya only), and RIGHT targets are correct.
- Direct targets remain visibly distinct from derived targets.
- Unknown and fail-closed states remain visible.
- Trailokya -> Agarwal -> Trailokya profile switching remains isolated.
- No score, polarity, price forecast, Fields influence, Auto Suggest, ML,
  MT5 execution, or order path appears.

## Regression Gate

Before recording acceptance, the broadest current repository Python/source
regression was run from a clean TD3R worktree:

```text
python -m pytest -q
753 passed, 1 skipped, 16 subtests passed
```

The sole skipped test remains the explicitly optional external JHora witness
test, which requires `JHORA_WITNESS_CSV`. No failure occurred. The stale
R4 Trailokya compatibility test was updated in separate commit `941902e` to
exercise the TN1 native adapter rather than its removed legacy symbol.

## Scope and Locks

This acceptance does not authorize a general Trailokya Vedha operator, market
mapping, polarity, scoring, price forecasting, Fields influence, Auto Suggest,
ML, MT5 trading, or execution. `executionAllowed=false` remains invariant.

Historical TN1 0.10.49 hold and TN1R1 repair/candidate chronology are
preserved in the earlier candidate and viewport-repair records.
