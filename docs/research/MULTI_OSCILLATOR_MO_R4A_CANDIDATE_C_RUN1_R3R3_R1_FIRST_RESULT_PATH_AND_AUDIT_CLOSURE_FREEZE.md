# Candidate C RUN1-R3R3-R1 First-Result Path and Audit Closure

## Predecessor Retained

R3R3-R1 is a narrow successor to the R3R3 authorization-ready machinery. It
does not modify evaluator A, evaluator B, V2 science or projection, source
contracts, the frozen population, astronomy, row schema, loader rendering, or
the twelve-file R3R2A bundle. The accepted 18-file V2 runtime protection set
is unchanged.

## Corrections

One `REAL_RESULT_PATHS` mapping now defines the exact three long-form paths for
preflight absence checks, production writes, replay rejection, and fake dry-run
temporary writes. Fake execution changes only the temporary root; it preserves
the full `status/research/...` production-relative filenames.

Before freezing each raw A or B artifact, the controller validates all rows
against the pre-frozen Candidate C row-key universe. It requires exact count,
no duplicate identity, no missing or extra identity, and the canonical
5,160-row universe hash. Artifacts record expected and actual universe hashes
and `rowUniverseValidated=true`.

Comparison audit accounting now derives counts from the protected V2
`mismatchClassifications` records. A record must have exactly one known frozen
taxonomy value to meet the one-record/one-count invariant; malformed,
unknown, or multi-class records fail closed before comparison artifact write.
The comparison artifact also binds V2 request/response hashes, worker hash,
protected commit and identity, projection identities, protected path-set hash,
and the verified A/B raw artifact hashes.

## Execution Boundary

The fake-only subprocess chain used three `FAKE_REAL_RUN1_` events and the
same relative output paths as production. It completed A then B then V2,
produced 24 rows per evaluator and 24 comparisons, and rejected replay without
overwriting the first artifacts.

There is no production authorization record, no production ticket, and no real
Candidate C scientific execution. The only permitted real-artifact scope
remains `IDENTITY_STRUCTURE_ADAPTER_AUTHORIZATION_BUNDLE_AND_REAL_V2_BRIDGE_VALIDATION_ONLY`.
No market, outcome, provider, broker, or Swiss Ephemeris data was accessed.

Atomic output write retains unique temporary creation, flush, fsync,
verification, and finalization. AUTH1 permits a single authorized controller
only; parallel production execution is prohibited. A pre-stage absence check
and fail-if-exists guard remain mandatory for every first-result path.

## AUTH1 Admission

AUTH1 requires zero scientific, execution, bundle, result-path, or audit-logic
code changes. It may only create the external authorization artifact, invoke
the frozen controller once, preserve the A, B, and V2 first results, freeze its
execution evidence, and stop.
