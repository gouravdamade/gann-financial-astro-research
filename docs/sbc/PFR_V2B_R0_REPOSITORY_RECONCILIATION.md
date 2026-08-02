# PFR-V2B-R0 Repository Reconciliation

Date completed: 2026-08-02

## Result

Remote production source is reconciled. The working V2B branch is local-only,
but its bounded source has been deliberately pushed to `origin/master`.

| Item | Result |
| --- | --- |
| Local branch | `pfr-v2b-categorical-oscillator` |
| Local SHA | `9677b1bb7c8b8b0c040c88c4d1442c56196e04c2` |
| `origin/master` SHA | `9677b1bb7c8b8b0c040c88c4d1442c56196e04c2` |
| Remote V2B branch name | Not present; source is on `master` |
| V2B-5 source commit | `86c652e Render independent synchronized field stack` |
| V2B-6 source commit | `9677b1b Expose FX side pilot evidence readiness` |
| Clean clone | `D:\GannAstroDesk-Reconciliation-20260802-R0` at the SHA above |

This resolves the source-truth concern without pretending that the local branch
name itself was published. No dirty working-tree source was used by the clean
clone.

## Source Manifest

### Contracts and research implementation

- `research_labs/chart_conditioned_aspects/chart_conditioned_aspects/models.py`
  - primary USD/JPY side identities and categorical interval models.
- `research_labs/chart_conditioned_aspects/chart_conditioned_aspects/polarity_evidence.py`
  - immutable reviewed evidence-packet validation.
- `research_labs/chart_conditioned_aspects/chart_conditioned_aspects/polarity_catalogue.py`
  - one-to-one side catalogue lookup and production registry loading.
- `research_labs/chart_conditioned_aspects/chart_conditioned_aspects/polarity_series.py`
  - fail-closed categorical side-range compiler.
- `research_labs/chart_conditioned_aspects/profiles/target_aware_polarity_evidence_packets_v1.json`
  - intentionally empty production packet registry.
- `research_labs/chart_conditioned_aspects/profiles/target_aware_polarity_catalogue_v1.json`
  - intentionally empty production catalogue registry.

### Backend routes and coordination

- `gann-astro-desk/backend/chart_conditioned_polarity_service.py`
  - chart-conditioned categorical side lookup/range service.
- `gann-astro-desk/backend/synchronized_range_service.py`
  - strict shared USD, JPY, and independent SBC range coordinator.
- `gann-astro-desk/backend/fx_side_pilot_service.py`
  - read-only pilot-readiness status.
- `gann-astro-desk/backend/server.py`
  - private desktop routes for categorical range, SBC atomic range,
  synchronized range, and pilot status.
- `gann-astro-desk/src-tauri/src/lib.rs`
  - authenticated native bridge commands for those private services.

### Founder-visible desktop surface

- `gann-astro-desk/src/views/ChakraLabWorkspace.tsx`
  - field loading coordination and Chakra selection context.
- `gann-astro-desk/src/views/ProductFirstSbcWorkspace.tsx`
  - compact field-stack presentation in the founder workspace.
- `gann-astro-desk/src/views/IndependentFieldStack.tsx`
  - independent USD, JPY, and SBC categorical-lane summary.
- `gann-astro-desk/src/api.ts` and `gann-astro-desk/src/types.ts`
  - versioned desktop API types and native calls.

### Verification coverage

- `gann-astro-desk/backend/test_chart_conditioned_polarity_service.py`
- `gann-astro-desk/backend/test_synchronized_range_service.py`
- `gann-astro-desk/backend/test_chakra_lab_service.py`
- `gann-astro-desk/backend/test_fx_side_pilot_service.py`
- `gann-astro-desk/src/api.test.ts`
- `gann-astro-desk/src/productFirstSbcWorkspace.test.tsx`
- `research_labs/chart_conditioned_aspects/tests/test_polarity_series.py`
- `research_labs/chart_conditioned_aspects/tests/test_polarity_catalogue.py`

## Clean-Clone Verification

From a fresh clone of the remote SHA:

| Gate | Result |
| --- | --- |
| `npm ci` | Passed |
| `npm run lint` | Passed |
| `npm run build` | Passed |
| `npm test` | 32 files, 132 tests passed |
| `python -m unittest discover -s backend -p "test_*.py"` | 181 tests passed |
| `cargo fmt --check` | Passed |
| `cargo check` | Passed |
| `cargo test` | 18 tests passed |

The Vite build reports one JavaScript chunk above 500 kB. It is recorded as a
future rendering/performance improvement and does not change runtime behavior.

## Remaining Product Truth

- Production USD and JPY registries are still empty.
- The existing Fields surface remains a compact categorical summary, not a
  stepped oscillator chart.
- Its current request derives from the last 110 loaded candles rather than
  the live visible chart pan/zoom range.
- There is no derived USDJPY categorical range.
- `PILOT_EVIDENCE_PENDING` remains the only honest production status.
- No evidence, numerical magnitude, smoothing, calibration, fusion, ML,
  Auto Suggest, live inference, order path, or execution capability was added.

## Next Bounded Milestone

PFR-V2B-R1 will introduce one authoritative live chart-range controller and
an honest stepped field renderer. It must keep unknown periods as gaps,
preserve the independent SBC field, and remain visual/research-only.
