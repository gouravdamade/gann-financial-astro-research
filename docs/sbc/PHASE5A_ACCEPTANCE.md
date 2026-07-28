# Phase 5A Atomic Interval Acceptance Gates

Phase 5A, which is P1 of the multidimensional SBC roadmap, is accepted in
source only when all of the following pass:

1. Explicit-boundary gate: every interval begins from a caller-supplied,
   timestamped SBC state boundary. The compiler does not invent astronomical
   transitions.
2. Ordering gate: unordered boundary input produces one deterministic
   chronological series.
3. Half-open gate: every interval is `[startUtc, endUtc)`, has positive
   duration, and ends exactly where the next interval begins.
4. No-lookahead gate: each interval carries exactly one evidence cutoff and
   that cutoff is not later than its start.
5. Uniqueness gate: duplicate boundary timestamps and duplicate identities are
   rejected.
6. Profile gate: one series cannot silently mix foundation, grid, Vedha, or
   guidance profile identities.
7. Lineage gate: each contribution preserves separate source-lineage and
   evaluated-contribution hashes, target witness metadata, and citation source
   IDs.
8. Ledger gate: favorable units, adverse units, net units, and true gross
   activation remain separate. Gross activation is the sum of absolute scored
   contribution units, not the absolute net.
9. Unknown gate: unresolved contributions and missing evidence remain counted.
   Unknown magnitude is null whenever unknown evidence exists and is zero only
   when no unknown evidence exists.
10. Coverage gate: scored count, unknown count, missing count, total count, and
    scoring coverage are visible.
11. Replay gate: the same boundaries, even in a different input order, produce
    the same series ID and serialized payload.
12. Isolation gate: the output is `SOURCE_PROFILED_EXPERIMENTAL`, contributes
    zero directional weight, and blocks phase, confidence, market direction,
    Auto Suggest, live inference, official ML notes, validation votes, trades,
    and MT5 execution.
13. Regression gate: all earlier SBC, Vedha, Chakra, service, and
    instrument-relative FX tests continue to pass.

Passing these gates certifies a deterministic research data structure. It does
not certify complete astronomical boundary discovery, Jyotisha doctrine,
financial usefulness, market direction, or execution.
