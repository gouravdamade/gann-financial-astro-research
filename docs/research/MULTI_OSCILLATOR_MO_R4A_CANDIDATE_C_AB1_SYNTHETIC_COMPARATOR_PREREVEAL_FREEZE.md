# Candidate C AB1 Synthetic Comparator Pre-Reveal Freeze

This record freezes a symmetric synthetic comparison contract before the first Evaluator A versus Evaluator B corpus run. Neither evaluator is an oracle. The comparison asks only whether their independently produced categorical VALUE and UNKNOWN rows agree under the neutral projection.

The comparator branch began at the accepted A1-R1 head `228c71ac3bf715300bcf21aa30de54b51e9f2b6f`, then integrated the frozen B head `64778dd26403faf42d264cdd06ce3fb2fd98ce8f` through merge commit `04c4e304aab52848a36b5524c14c0263f90ff75e`. The single merge resolution was a shared package docstring; protected A and B identities are verified from their original frozen Git blobs, not reconstructed from that integration namespace file.

The frozen neutral corpus has 1,040 fixtures: 972 relationship-position cases, 64 motion cases, and four representation-invariance canaries. It contains synthetic categorical inputs and coverage tags only: no expected evaluator values, prices, outcomes, market directions, polarity, magnitude, scoring, or real Candidate C identifiers.

The comparison projection includes fixture identity, profile, component, contract, operator, represented operator version and source status, output status, canonical VALUE, and UNKNOWN reason. It excludes evaluator-local input identity and formatting. Ordinary Saravali Drsti is canonicalized to the source-ledger fraction form only, so `DRSTI_3_4` and `3/4` both mean `3/4` for the ordinary Drsti operator.

At this freeze, `abComparisonExecuted=false`. Comparator toy tests passed without executing the two frozen evaluators together. A and B synthetic suites were run separately, while the real population, real 5,160-row output, market/outcome data, provider access, Swiss Ephemeris, polarity, magnitude, scores, waves, and execution all remain prohibited.

The machine-readable freeze record binds the fixture and contract hashes. The next action is exactly one first synthetic comparison followed by an immutable result freeze; any mismatch must be preserved without evaluator, adapter, fixture, or projection repair.
