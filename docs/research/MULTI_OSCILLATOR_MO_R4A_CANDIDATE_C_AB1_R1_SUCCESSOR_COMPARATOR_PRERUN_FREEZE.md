# Candidate C AB1-R1 Successor Comparator Pre-Run Freeze

This is a successor freeze, not a revision of AB1 V1. AB1 V1 remains `SYNTHETIC_SEMANTIC_MISMATCH` with 81 preserved ordinary-Drsti representation mismatches.

The preceding adjudication committed at `7536386e41271a5c36afa72df68ca6aca41fd8a4` established a `REPRESENTATION_CANONICALIZATION_GAP`: the frozen ledger stores place 7 as `FULL`; A serializes the same value as `DRSTI_FULL`; B preserves `FULL`; V1 omitted that single alias.

The successor V2 projection at `52c3b287a70018370e153a77b84c36e6b0dbfb42` has one permitted additional alias: `DRSTI_FULL -> FULL`. Numeric aliases remain explicit, and arbitrary `DRSTI_*` strings are not normalized. The fixture corpus, adapters, mismatch taxonomy, row alignment, evaluators, and all other projection behavior are unchanged.

At this commit, `successorComparisonExecuted=false`. The next permitted action is exactly one synthetic rerun on the same 1,040-fixture corpus. The real Candidate C population and all market, outcome, provider, Swiss Ephemeris, polarity, magnitude, scoring, wave, and execution paths remain prohibited.
