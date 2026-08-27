# MO-R3-R1 Founder Review Gate Repair

Status: `IMPLEMENTED - FOUNDER REVIEW GATE REPAIR CANDIDATE`

Milestone: `MO-R3-R1`

Starting `origin/master`: `1610c7731fff620a7943b30c1b1c751d7979fbfb`

This bounded repair closes the two readiness defects recorded by the frozen
MO-R3 founder-review protocol. It does not begin the founder's 24-row review,
admit polarity evidence, or implement a signed oscillator.

## Changes

### Directional reasoning gate

`SUPPORTIVE` and `ADVERSE` now require a founder-entered
`founderReasoning` value containing at least one non-whitespace character.
The backend export validator is authoritative and rejects empty or
whitespace-only values. The Founder Review UI marks the field as required for
those two decisions, shows a decision-specific prompt, and performs the same
preflight check before calling export. No reason is generated or prefilled.

`MIXED`, `NEUTRAL`, and `UNKNOWN_MORE_EVIDENCE_REQUIRED` retain their existing
non-directional behavior. `UNKNOWN_MORE_EVIDENCE_REQUIRED` remains an unknown
gap and is never coerced to neutral.

### Ephemeris provenance binding

The reviewed/export projection now carries:

```text
ephemerisVersion = packet.eventCompiler.ephemerisVersion
ephemerisVersionProvenance = PACKET_COMPILER_METADATA
ephemerisVersionSourcePacketSha256 = authenticated blank-packet SHA-256
```

The complete packet-level `eventCompiler` metadata is copied into the derived
reviewed packet. The reviewed manifest, status, completeness report, Markdown
rendering, and workbench side payload expose the same binding. The backend
rejects missing or blank packet compiler version/provider metadata, mismatched
side/chart/event provenance, and contradictory reviewed/manifest bindings.

The current authenticated packet value is `2.10.03` from `Swiss Ephemeris`.
It is not inferred from `generatorVersion`, a label, astronomy-contract text,
provider name, event ID, or event hash. The 24 event identity objects are not
rewritten and do not receive a duplicated row-level version field.

The repository's initial checked-in reviewed projections predate this repair
and contain no decisions. They remain readable as legacy blank state. The next
export writes the packet-bound projection; a decided legacy projection without
the binding would fail closed.

## Reverification

The authenticated blank packets and identity-integrity manifests resolve to:

| Side | Rows | Identity status | Packet compiler version |
|---|---:|---|---|
| USD | 12 | `SINGLE_PASS_VERIFIED` | `2.10.03` |
| JPY | 12 | `SINGLE_PASS_VERIFIED` | `2.10.03` |
| Total | 24 | `SINGLE_PASS_VERIFIED` | packet-bound |

The original blank packets remain read-only inputs. No founder decision,
reasoning, catalogue admission, reviewed-evidence admission, or identity
mutation was introduced.

## Outcome-blindness and locks

The workbench and validator continue to avoid market prices, candles, returns,
future outcomes, P/L, SBC, signed waves, pair resultants, LLM/ML decisions,
catalogue recommendations, and execution data. `executionAllowed=false`.

The following remain absent or unconfigured:

```text
SIGNED_WAVE = ABSENT
SIGNED_PAIR_RESULTANT = ABSENT
MAGNITUDE = NOT CONFIGURED
NORMALIZATION = NOT CONFIGURED
SMOOTHING = NOT CONFIGURED
NON-RECTANGULAR_KERNEL = NOT CONFIGURED
FOUNDER_DECISIONS = 0
CATALOGUE_ADMISSIONS = 0
REVIEWED_EVIDENCE_ADMISSIONS = 0
PRICE/OUTCOME_READ = FALSE
SBC_READ = FALSE
LLM_DECISION_USED = FALSE
ML_DECISION_USED = FALSE
executionAllowed = false
```

## Verification

The focused backend workbench suite covers blank/whitespace/nonblank
directional reasoning, non-directional decisions, missing compiler metadata,
event-provenance conflict, packet binding, blank-packet preservation, and the
24-row population. The focused frontend suite covers required UI wording,
blank-export blocking, packet-neutral display, and the explicit ephemeris
metadata.

Exact results from this implementation worktree:

| Check | Command | Result |
|---|---|---:|
| Focused backend | `python -m unittest -v test_founder_review_workbench` from `gann-astro-desk/backend` | 13/13 passed |
| Relevant research packets | `python -m pytest -q research_labs/chart_conditioned_aspects/tests/test_blank_founder_pilot_packs.py research_labs/chart_conditioned_aspects/tests/test_event_identity_packet_policy.py` | 4/4 passed |
| Focused frontend | `npx vitest run --pool=threads --no-file-parallelism --maxWorkers=1 --testTimeout=15000 src/founderReviewWorkbench.test.tsx` | 1 file, 3/3 passed |
| Full backend | `python -m unittest discover -s backend -p "test_*.py"` from `gann-astro-desk` | 323 passed, 1 skipped |
| Full frontend | `npx vitest run --pool=threads --no-file-parallelism --maxWorkers=1 --testTimeout=15000` from `gann-astro-desk` | 43 files, 196/196 passed |
| Lint | `npm run lint` from `gann-astro-desk` | passed |
| Production build | `npm run build` from `gann-astro-desk` | passed; 1,878 modules |
| Diff hygiene | `git diff --check` | passed |

The default Vitest fork-worker invocation remains subject to the repository's
known Windows worker-start timeout; the authoritative focused and full runs
used the stable single-worker threads configuration above. Rust/Tauri checks
were not applicable because no Rust or package metadata was touched. A manual
real-repository probe also returned `USD=12`, `JPY=12`, and packet-bound
`2.10.03` for both sides.

## Remaining stop gate

`MO-R3-R1` is ready for central verification only. The founder must not be
asked to classify events until the central review confirms this repair. The
next permitted action is the existing outcome-blind founder review; this
milestone does not perform it.
