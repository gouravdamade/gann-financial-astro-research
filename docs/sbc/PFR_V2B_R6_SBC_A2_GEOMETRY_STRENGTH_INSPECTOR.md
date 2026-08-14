# PFR-V2B-R6-SBC-A2: Agarwal Geometry and Strength Inspector

## Scope

This milestone adds a founder-visible, read-only source inspector for the
M. K. Agarwal, Sagar Publications, New Delhi, First Edition 2000
*Mystics of Sarvato Bhadra Chakra and Astrological Predictions* source.

The authorized scope is:

`A2_SCOPE_GEOMETRY_STRENGTH_INSPECTOR`

The product consumes the immutable A1R3 page-145 geometry packet and the
two-pass strength packet. It does not calculate Vedha, market direction,
polarity, score, price mapping, Fields values, Auto Suggest, ML output, or
execution.

## Product contract

The read-only backend adapter is:

`AGARWAL_GEOMETRY_STRENGTH_INSPECTOR_V1`

It exposes:

- the exact 81-cell `AGARWAL_PAGE145_CORE_9X9_V1` map;
- author orientation `EAST=top`, `WEST=bottom`, `NORTH=left`, `SOUTH=right`;
- literal cell labels, source layers and varga numbers;
- p.144 allocation reconciliation as provenance, not as another geometry engine;
- source strength rows from pp.54-55 and 60-63;
- the explicit `DEPENDENCY_NOT_READY` Vedha status and existing blockers;
- Chapter 20 as `FINANCIAL_HYPOTHESIS_LEDGER_ONLY` with locked labels.

The response is independent of chart symbol, price data, crosshair, Fields
requests, synchronized Swiss Ephemeris computation and pair calculations.
`executionAllowed` is always false.

## Profile isolation

`Agarwal 2000 Research` is an explicit Chakra source-profile choice. It is not
merged with the Phaladeepika editor or Trailokya Dipika profiles. Selecting it
uses a separate Chakra profile state and does not alter the Fields profile or
its synchronized range request. Returning to another profile restores the
existing Chakra behavior.

## Evidence and limitations

The board is derived from:

`configs/sbc/evidence_packets/agarwal_2000_page145_geometry_two_pass_v1.yaml`

That packet records 81 direct two-pass agreements and no unresolved machine
core cells. The older folded-capture `UNKNOWN_CENTER_FOLD` finding remains in
the historical record and is represented as superseded for the current core
geometry only. Private photographs are not bundled or exposed by the adapter.

The strength packet remains source evidence. The UI displays literal and
already-recorded normalized values, but never sums them into a master score.

The following remain unavailable and intentionally have no visualization:

- deterministic motion-state precedence;
- stationary/direct-slow handling;
- board-ray traversal and origin-cell inclusion;
- simultaneous-hit precedence;
- cancellation/obstruction order;
- universal validity-window contract;
- reproducible complete worked method.

Chapter 20 claims remain locked research hypotheses. They are not classical
Mode 1 doctrine, not FX-mapped and not executable.

## Verification

Focused backend source-adapter tests validate the 81-cell contract, orientation,
strength and financial isolation, explicit Vedha unavailability, and absence of
private locators. Focused frontend tests validate selection, source details,
orientation, 81-cell rendering, profile switching and locked output. The
existing backend and frontend suites remain the regression gates.

This record documents implementation readiness for founder inspection. It does
not constitute founder acceptance or certification of Agarwal doctrine.
