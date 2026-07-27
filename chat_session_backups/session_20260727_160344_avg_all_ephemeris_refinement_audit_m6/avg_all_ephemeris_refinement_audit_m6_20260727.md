# AVG(ALL) Ephemeris Refinement And Audit Persistence M6

Date: 2026-07-27

## Scope

This milestone extends the existing ten-body synthetic `AVG(ALL)` research
surface in two deliberately narrow ways:

- eligible mean-rashi ingress estimates can be refined from their original
  source-bar bracket with Raman-sidereal Swiss Ephemeris calculations;
- a selected collective source-bar audit can be saved inside the active chart
  layout or exported as a standalone JSON evidence packet.

Neither feature creates a market direction, Jyotisha judgment, SBC Vedha,
Auto Suggest input, ML note, shadow-validation input, or executable signal.

## Exact-Root Policy

The refinement contracts are:

```text
GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1
AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1
```

Only `MEAN_RASHI_INGRESS` is eligible. The engine:

1. preserves the original sampled estimate and source-bar bracket;
2. recalculates all ten member longitudes at fractional timestamps with the
   existing Raman sidereal Swiss Ephemeris path;
3. recomputes the equal-weight circular mean and R1 at every candidate time;
4. refuses to bridge an R1 reliability failure;
5. requires the original directional crossing to remain bracketed;
6. bisects the bracket until it is no wider than one second;
7. accepts the root only when the angular residual is at most `0.001` degree.

`timing.exact=true` therefore means a numerical root proven within those two
declared tolerances. It does not mean infinite precision, independent
astronomical certification, traditional authority, or market causality.

Coherence-threshold crossings and cluster-state changes remain bar-sampled
heuristics. If the bracket is lost, R1 becomes unreliable, event data is
malformed, convergence misses a tolerance, or the work budget is exhausted,
the original sampled event is retained with an explicit `SAMPLED_FALLBACK`
record.

## Bounded Work

At most 64 ingress candidates are ephemeris-refined in one overlay request.
Any additional ingress remains visible and is recorded as a sampled
budget-fallback event. A long D1/W1 view therefore stays usable instead of
failing or starting unbounded ephemeris work.

The response summary records:

- total candidate count and candidate budget;
- attempted, refined, fallback, and budget-skipped counts;
- total fractional timestamps evaluated;
- the declared time and angular tolerances.

The desktop rejects inconsistent counts, an exact claim outside its source
bracket, an excessive residual, unsafe nested guardrails, or an exact claim
for any non-ingress event.

## Saved Audit Snapshots

The snapshot contract is:

```text
GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1
```

The inspector header now provides:

- **Save audit**: stores an immutable copy in the active named chart layout;
- **Export audit**: downloads the current copy as JSON;
- saved-audit controls to pin its exact source bar, export it again, or delete
  it from the layout.

Each copy contains:

- symbol, timeframe, chart range, selected exact source-bar time, and creation
  time;
- collective calculation version and complete member profile;
- the selected sample and its ten-member leave-one-out audit;
- up to four nearest research events, including accepted root provenance or
  sampled-fallback reasons;
- explicit no-vote, no-inference, no-ML-note, and no-execution guardrails.

Saving the same symbol, timeframe, source bar, and member-set hash replaces
the earlier copy rather than creating a duplicate. The newest 24 snapshots
are eligible for retention, subject to a total serialized budget of 224 KiB.
This leaves room under the backend's existing 256 KiB chart-state limit.
Unsafe nested events, malformed profiles, oversized imports, and weakened
guardrails are discarded during layout restore/import.

## Runtime Measurement

A one-run local measurement on the active USDJPY H1 source used:

- 241 exact bar timestamps;
- 2 detected ingress events;
- 2 accepted refined roots and 0 fallbacks;
- 28 fractional ephemeris timestamp evaluations;
- approximately 0.6 seconds on the warm local service and 1.3 seconds on the
  first measured request after a service restart.

One real audit copy serialized to approximately 8.1 KiB. Twenty-four copies
of that shape would use approximately 190 KiB before other small chart-state
settings.

The inspector remains a separate lazy-loaded production chunk at about
11.4 KiB minified and 3.7 KiB gzip. The existing main-bundle advisory remains:
the main chunk is approximately 528 KiB minified. Further main-workspace
splitting is still a separate performance task.

These are development-machine observations, not a benchmark guarantee.

## Safety Boundary

Backend contracts, runtime validation, imported-snapshot validation, and the
UI require:

- research and audit use only;
- original sampled estimates remain present;
- no independent vote and directional contribution exactly `0.0`;
- no live-inference, Auto Suggest, shadow-ledger, or official-ML-note use;
- no SBC Vedha;
- no execution.

## Verification

Verification completed on 2026-07-27:

- focused collective/refinement backend tests: `29/29`;
- focused audit/inspector/response frontend tests: `20/20`;
- complete desktop backend suite: `146/146`;
- complete desktop frontend suite: `87/87`;
- complete repository Python suite: `389/389`;
- Python Ruff for changed backend files: passed;
- frontend Oxlint: passed;
- TypeScript and Vite production build: passed;
- direct live API contract check: passed.

The live browser was inspected before the backend restart and correctly
rejected the intentionally stale pre-M6 response. After the service restart,
the in-app browser policy blocked a second localhost interaction pass.
Therefore no claim of final post-restart visual acceptance is made in this
milestone. Automated component/layout checks and the synchronized live API
contract passed; native-size visual reinspection remains a small follow-up.

## Known Limitations And Next Work

- This is source-only. No Windows installer or Android package was rebuilt.
- Exact refinement currently covers mean-rashi ingress only.
- Saved audits are bar-centered; a nearby refined root is preserved inside
  the evidence packet but does not invent a fractional-time market bar.
- No financial or prospective validation is claimed.
- Non-voting Gann/SBC visual studies, further main-bundle splitting, final
  native-size visual acceptance, and frozen prospective-policy validation
  remain separate work before any inference promotion.
