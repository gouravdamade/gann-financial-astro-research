# PFR-V2B-3 SBC Atomic Visible Range

## Scope

`SBC_ATOMIC_VISIBLE_RANGE_V1` exposes the existing Sarvatobhadra Chakra
atomic timeline as a bounded, timestamp-safe, read-only field. It is a
separate synchronized comparison field for the future chart stack, not an
aspect-pressure confirmation mechanism.

## Input and Output

The private backend route is `POST /api/chakra-lab/atomic-range`. Its input is
the existing explicit-boundary Chakra Lab audit request:

- `instrumentIdentity`
- `terminalEnd` with an explicit UTC offset
- one or more timestamped Chakra Lab `boundaries`

Each returned interval preserves its start, end, evidence cutoff, source
ledger identity, profile/source lineage, raw existing ledger summary, and a
guidance availability state: `AVAILABLE`, `PARTIAL`, or `UNKNOWN`.

## Deliberate Limits

- The contract does not call the chart-conditioned aspect compiler.
- The SBC values retain their existing source terminology (`favorable` and
  `adverse` guidance units); V2B-3 does not recast them as market polarity.
- `magnitude_state` is `NOT_CONFIGURED`.
- `aspect_relationship` is `NOT_AUTOMATIC_CONFIRMATION`.
- The field is research-only, read-only, timestamp-safe, no-lookahead, not
  financially validated, and blocks automated orders and execution.

## Verification

`test_atomic_range_remains_an_independent_read_only_timeline` confirms two
contiguous intervals, the explicit no-confirmation contract, and the retained
execution locks. The existing SBC audit and fixed-phasor tests remain the
source checks for the underlying interval ledger.
