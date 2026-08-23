# Current Project Handoff

Last updated: 2026-08-23 IST

Use this file to recover context in a new chat if PyCharm/Codex chat history is lost.

## Latest Update - 2026-08-23 (MO-P2-R1 Activity Integrity Hardening)

- Hardened unsigned activity coverage without changing the canonical astronomy
  compiler. Rejected candidates are now classified from their supplied observed
  interval: a valid interval wholly outside the requested visible range is
  irrelevant; overlap, missing timestamps, malformed bounds, or insufficient
  metadata remain relevant and keep coverage `UNKNOWN`. Canonical
  `unknownReasons` always remain `UNKNOWN`.
- The response now reports total, relevant, and irrelevant rejected-event
  counts. The activity response is `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`
  / `MO_UNSIGNED_EVENT_ACTIVITY_SIDE_V1_1` with `schemaVersion: 2`, and the
  authoritative generator field is `eventUniverseHash` rather than the
  misleading `eventUniverseProfileHash`.
- Fields now derives one shared raw-count display axis from the currently
  filtered USD and JPY interval counts. The UI shows `Shared raw activity
  scale: 0-N active events`; CSS pixel scaling does not mutate data values.
  Zero/zero uses a pixel denominator of one while displaying zero.
- Guardrails retain `normalizationUsed=false` and add explicit
  `dataNormalizationUsed=false` plus `displayAxisScaling=SHARED_RAW_COUNT_AXIS`.
  No polarity, magnitude, pair difference, smoothing, price/outcome, SBC,
  CGVO, LLM, Auto Suggest, ML, MT5, or execution path was added;
  `executionAllowed=false`.
- Source record: `docs/research/MULTI_OSCILLATOR_MO_P2_R1_ACTIVITY_INTEGRITY_HARDENING.md`.
  Focused backend tests: `15/15`; focused frontend/API tests: `30/30`.
  Full backend: `319 passed, 1 skipped`; full frontend: `182 passed` across
  42 files; Oxlint, production build, `cargo fmt --check`, `cargo check`, and
  Rust tests (`19 passed`) are green. The build retains the existing large
  chunk-size warning. Packaging is intentionally deferred. The required next
  action after the source verification is `CENTRAL REVIEW OF MO-P2-R1`; do
  not start MO-P3.
- Real 14-day smoke (`2025-04-01T00:00:00Z` through
  `2025-04-15T00:00:00Z`): USD `57` source/eligible events, `32` rejects
  (`3` relevant, `29` irrelevant), coverage `UNKNOWN`; JPY `59`
  source/eligible events, `14` rejects (`0` relevant, `14` irrelevant),
  coverage `KNOWN`. This is the intended visible-range distinction, not a
  polarity or forecast result.

## Latest Update - 2026-08-23 (MO-P2 Unsigned Event Activity V0)

- Added the backend-owned `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1` contract and
  `MO_ACTIVITY_CONTRIBUTION_V1` half-open interval compiler. It delegates to
  the existing canonical chart-conditioned transit event compiler for the
  accepted USD and JPY chart identities; the frontend cannot inject chart IDs,
  body universes, events, polarity, magnitude, or pair-relative values.
- Fields now renders a separate `Multi Oscillator / Event Activity` panel below
  the existing independent categorical fields. It shows USD and JPY event
  spans, exact markers, integer raw active-event counts, local body/aspect
  filters, and a provenance inspector labelled `CANONICAL_COMPILER_EVENT`.
  It does not overclaim the separately audited `SINGLE_PASS_VERIFIED` status.
  The existing categorical USD/JPY/pair/SBC and BPHS surfaces remain unchanged.
- Activity is descriptive only: `EXPLORATORY_UNSIGNED`, `UNSIGNED`,
  `NON-PREDICTIVE`, and `MAGNITUDE_NOT_CONFIGURED`. Applying-to-separating
  intervals are exact half-open ranges. Successful no-event compilation is a
  known zero; compiler unknown/rejected coverage remains UNKNOWN. No sampling,
  smoothing, normalization, curve fitting, signed wave, or USD-minus-JPY
  activity was introduced.
- Guardrails remain explicit: no polarity, price, outcome, SBC, LLM, Auto
  Suggest, ML, pair difference, MT5, order placement, or execution;
  `executionAllowed=false`.
- Real backend smoke over 2025-04-01 through 2025-04-15 produced 57 USD and
  59 JPY event records with 79 and 78 exact boundary intervals respectively.
  The compiler reported rejected boundary coverage, so both side lanes remain
  explicitly `UNKNOWN` rather than presenting an unjustified complete-range
  zero; event spans and raw counts remain inspectable.
- Source record:
  `docs/research/MULTI_OSCILLATOR_MO_P2_UNSIGNED_EVENT_ACTIVITY_V0.md`.
  Focused backend/API and Fields tests pass, Oxlint passes, and the production
  frontend build passes. No Windows or Android package was built; central
  review is the next gate before any later signed/magnitude oscillator work.

## Latest Update - 2026-08-23 (CGVO-CALENDAR-R1 Historical Lunar-Month Source Closure)

- Independently re-verified the private Varahamihira witness SHA-256
  `D7425625010C621FF6651BF6BF916506791E3D4381078251AC7DC8EFBBA6577A`
  and visually inspected II.5 (PDF image 33 / printed p.8), XXV.5 (263 / 238),
  and XXVI introduction/1 (264 / 239). The source supports a
  `PURNIMANTA` reading only as `HIGH_CONFIDENCE_SOURCE_INTERNAL_INFERENCE`;
  it records `Adhimasa` and `Avama`, but does not close a complete historical
  intercalation, naming, boundary, or local-day operator.
- Corrected profile language to distinguish the modern `UTC_EXACT_FULL_MOON`
  membership calculation and `SANKRANTI_COUNT_FAIL_CLOSED_V1` guard from
  historical source authority. Locality now means source-day provenance after
  classification; it does not change membership. Zero- and two-ingress cases
  remain `UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED`, never named Adhika or
  Kshaya by the application.
- The new `CGVO_CALENDAR_R1_HISTORICAL_LUNAR_MONTH_SOURCE_CLOSURE.md` and
  machine-readable R1 profile record ordinary, intercalary, pre-modern, and
  boundary audit cases. Current Mode 1 eligibility is false because month
  naming and boundary semantics are still not source-closed. The smallest next
  evidence requirement is a page-certified Surya Siddhanta intercalation
  witness. No Multi Oscillator, Fields, price, polarity, SBC, Auto Suggest,
  ML, MT5, or execution behavior changed; `executionAllowed=false`.

## Latest Update - 2026-08-23 (Multi Oscillator Completion Ledger Audit)

- Fast-forwarded the audit worktree to public origin/master
  09058f270a701f152813a93b78bc910dbc1a8a3d, which explicitly freezes
  CGVO-G3 after G3-S1-R1 and returns product priority to the Multi Oscillator /
  wave visualizer. No CGVO, Fields, polarity, SBC, MT5, or execution behavior
  changed in this documentation-only milestone.
- The live SYNCHRONIZED_INDEPENDENT_RANGE_V1 path was exercised for a 14-day
  range: it compiled 62 USD and 61 JPY real transit-to-natal events and
  returned 90 canonical intervals for each side. Every side interval remained
  UNKNOWN, which is correct because the canonical target-aware polarity
  catalogue has zero accepted production entries. The pair field therefore
  remained UNKNOWN_SIDE_EVIDENCE; no gap was converted into zero.
- Current Fields is a working categorical, multi-lane foundation rather than a
  completed multi-wave engine: USD, JPY, transparent pair-relative, and
  independent SBC lanes are implemented with shared range/crosshair behavior.
  There is no approved signed contribution, magnitude, aggregation, timing
  kernel, smoothing, or continuous waveform contract.
- New controlling audit:
  docs/research/MULTI_OSCILLATOR_COMPLETION_LEDGER_V1.md. Its P0 is a missing
  versioned, auditable event-contribution contract, manifested immediately by
  the empty accepted polarity catalogue. Await central review before adding any
  Mode 2 profile or moving signed waveform.

## Latest Update - 2026-08-22 (CGVO-G3-S1-R1 V.42 Root Kūrma Reference Correction)

- Starting from `a6808d085751871eec303aa61805dc3ff61be0ad`, re-verified the
  same private 1,116-page root witness against SHA-256
  `D7425625010C621FF6651BF6BF916506791E3D4381078251AC7DC8EFBBA6577A` and
  re-inspected V.42 on PDF images 83--84 / printed pp.58--59. The root Sanskrit
  visibly contains `भफलं कूर्मोपदेशाद्वदेत्`:
  `SOURCE_CLOSED_ROOT_KURMA_REFERENCE`, not
  `COMMENTARY_ONLY_REFERENCE`.
- This closes only textual relevance between V.42 and Kūrma teaching. It does
  not authorize a spatial or effect operator: site-to-region remains
  `SOURCE_SILENT_SITE_TO_REGION_OPERATOR`, `regionVisibility=null`,
  `sourceEffectActivation=null`, and S1B remains
  `UNCHANGED_UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED`.
- The private witness test is now portable: static ledger checks always run;
  the byte-level check passes only when `GANN_ASTRO_PRIVATE_SOURCE_ROOT`
  supplies the verified file, explicitly skips with
  `PRIVATE_G3_S1_SOURCE_WITNESS_NOT_AVAILABLE` when absent, and fails on a
  present hash mismatch. No source bytes or absolute private path are tracked.
- Status is `READY_FOR_CENTRAL_REVIEW`. No UI/package, price, market, Fields,
  SBC, Auto Suggest, ML, MT5, or execution work was added;
  `executionAllowed=false`. After central acceptance, freeze CGVO-G3 and
  return priority to the Multi Oscillator / wave visualizer.

## Previous Update - 2026-08-22 (CGVO-G3-S1 Root Sanskrit Witness and Semantic Composition Audit)

- Acquired and independently SHA-256-verified the private 1,116-page
  `BRIHAT_SAMHITA_SASTRI_V_SUBRAHMANYA_DLI_2015_102832` witness:
  `D7425625010C621FF6651BF6BF916506791E3D4381078251AC7DC8EFBBA6577A`.
  The private PDF remains outside Git. Page images 72, 83--84, 184--185, and
  189--190 were visually inspected; OCR was navigation only.
- The source closes V.11 only as solar local-differential visibility. V.42's
  Chapter XIV label is editorial/translation prose, not an inspected Sanskrit
  reference. XIV.1 and XIV.24--28 source-close contextual directional and
  historical-name records, including Taxila/Puskalavati/Gandhara as northern
  list peers, but no containment or transfer rule.
- The terminal verdict is `SOURCE_CLOSED_CONTEXTUAL_PROVENANCE_ONLY`.
  `siteToRegionRuleStatus=SOURCE_SILENT_SITE_TO_REGION_OPERATOR`,
  `regionVisibility=null`, and `sourceEffectActivation=null`. S1B phase gaps
  are unchanged. The Taxila route remains site-only, with no geometry, region,
  effect, price, market, Fields, SBC, Auto Suggest, ML, MT5, or execution path;
  `executionAllowed=false`.
- G3-R1's post-review central verdict is corrected to
  `CENTRAL_ACCEPTED_CONTEXTUAL_PROVENANCE_ONLY`; G3-D1 now uses the canonical
  `CONTEXTUAL_PROVENANCE_ONLY` vocabulary while retaining its legacy label for
  compatibility. Report:
  `docs/research/CGVO_G3_S1_ROOT_SANSKRIT_WITNESS_AND_COMPOSITION_AUDIT.md`.

## Previous Update - 2026-08-22 (CGVO-G3-R1 Source-Composition Adjudication)

- Starting from centrally accepted `CGVO-G3-D1` commit
  `1a7bc5b43167aef0cff568a268e1e8d9722e7b62`, added the static
  `CGVO_G3_R1_SOURCE_COMPOSITION_ADJUDICATION_V1` ledger and a read-only
  response block to the existing Taxila site-visibility audit. The current
  verdict is `CONTEXTUAL_PROVENANCE_ONLY`: Chapter XIV may be displayed as
  provenance, but Taxila remains site-only and is never Gandhara visibility.
- The held translation-ledger claims identify Chapter V V.11 local visibility
  wording and V.42's Chapter XIV reference, but the exact composition decision
  lacks an acquired checksum-identified root Sanskrit page witness. The ledger
  therefore records `COMMENTARY_SUPPORTED_INTERPRETATION` and keeps
  `chapterV_XIV_compositionStatus=COMPOSITION_NOT_AUTHORIZED`.
- `regionVisibility=null` and `sourceEffectActivation=null` remain explicit.
  Chapter V effect activation is also independently blocked by the unchanged
  S1B-R1 solar/lunar phase-mapping gaps. Region/effect, Gandhara inclusion,
  downstream, market, and execution requests fail closed as typed JSON.
- G1 remains 308 raw source occurrences; G2 remains 12 research footprints;
  G2-R1A still admits one coordinate-bearing Taxila point. No coordinate,
  geometry, UI, package, price/outcome, Fields, SBC, Auto Suggest, ML, MT5,
  or execution work was added. `executionAllowed=false`.
- Report: `docs/research/CGVO_G3_R1_SOURCE_COMPOSITION_ADJUDICATION.md`.

## Latest Update - 2026-08-22 (CGVO-G3-D1 Taxila Local-Visibility Audit)

- Starting from accepted `CGVO-G2-R1A` commit
  `03a8c1c8562c8c17c89cff55ecb36ac4bad78b04`, added a narrow, read-only,
  JSON-only historical-site local-visibility audit endpoint. It accepts only a
  reconstructed canonical CGVO event identity plus the G2-R1A Taxila evidence
  ID, then reuses the existing topocentric local-circumstances engine.
- The result is explicitly `SITE_VISIBILITY_AT_RESEARCH_ANCHOR` for the
  **Taxila research site anchor**. Taxila remains partial historical context
  only, not Gandhara, a regional visibility result, an eclipse-effect
  activation, or a spatial match. Chapter XIV geography and Chapter V eclipse
  effects remain uncomposed and `null`.
- Pending/contested/non-point candidates, source-name-only records, unknown
  site IDs, invalid canonical events, region requests, and any downstream
  request fail closed as typed JSON errors. G2-R1A coordinate binding and raw
  DMS normalization are revalidated before each audit.
- No source acquisition, UI, Windows package, geometry, GIS, price/outcome,
  market, Fields, SBC, Auto Suggest, ML, MT5, or execution change was made;
  `executionAllowed=false`. Design report:
  `docs/research/CGVO_G3_D1_HISTORICAL_SITE_LOCAL_VISIBILITY_ADAPTER_DESIGN.md`.

## Latest Update - 2026-08-22 (CGVO-G2-R1A Coordinate Integrity Hardening)

- Hardened the accepted G2-R1 Taxila anchor without changing the historical
  research result. The V2 footprint schema is retained for compatibility, and
  the backend now strictly binds all eleven evidence-derived coordinate and
  provenance fields to `G2R1_TAKSASILA_TAXILA_SITE_01` before returning the
  read-only footprint response.
- Added deterministic DMS parsing with `fractions.Fraction`. The accepted raw
  Taxila value `33° 45' 35'' N 72° 50' 15'' E` verifies to
  `33.7597222222, 72.8375`. Invalid DMS, axis/hemisphere, range, NaN/Infinity,
  raw/normalized, and footprint/evidence mutations fail closed.
- Top-level CGVO status and readiness now report `CGVO-G2-R1A`; astronomy
  remains `CGVO-S1B-R1`. Taxila remains the only coordinate-bearing footprint;
  Mathuraka, Magadha, and Pushkalavati remain unresolved as previously
  recorded. No source acquisition, G3, UI, package, price, market, Fields,
  SBC, Auto Suggest, ML, MT5, or execution change was made;
  `executionAllowed=false`.
- Integrity report: `docs/research/CGVO_G2_R1A_COORDINATE_INTEGRITY_HARDENING.md`.

## Latest Update - 2026-08-22 (CGVO-G2-R1 Historical-Site Coordinate Evidence)

- Added a strict, read-only historical-site and coordinate evidence audit on
  top of the immutable 308-occurrence CGVO-G1-R1 gazetteer. The audit admits
  exactly one coordinate-bearing footprint: a Getty TGN WGS84 Taxila
  archaeological-site reference (`33.7597222222, 72.8375`) as partial
  historical context for Gandhara. It is explicitly not a Gandhara boundary,
  centroid, envelope, or market input.
- Mathuraka/Mathura, Rajagriha/Rajgir, Pataliputra, and
  Pushkalavati/Charsadda remain fail-closed. The first three have unresolved
  coordinate CRS/reference-locus semantics in the held sources; the two
  Pushkalavati gazetteer points conflict by about 9.6 km and are not selected
  or averaged. The two Kamboja alternatives remain separate; Sindhu remains a
  river-system context without adjacent land geometry.
- The endpoint remains read-only and now returns
  `CGVO_HISTORICAL_GEOGRAPHY_RESEARCH_FOOTPRINTS_V2`. Strict validation rejects
  incomplete coordinate provenance, source-name-only records, out-of-range
  values, inferred regional geometry, and missing identity evidence. G3
  spatial use remains blocked pending central review.
- Evidence report: `docs/research/CGVO_G2_R1_HISTORICAL_SITE_COORDINATE_EVIDENCE_REPORT.md`.
  No package was built. Price/outcome data, polarity, score, Fields, SBC, Auto
  Suggest, ML, MT5, and execution remain disconnected; `executionAllowed=false`.

## Latest Update - 2026-08-22 (CGVO-S1B-R1 Source Acquisition and Absolute-Frame Correction)

- Acquired and checksummed the full 330-image 1889 Thibaut-Dvivedi
  *Panchasiddhantika* witness privately. The earlier S1B claim that Magha was
  source-silent is superseded: its table records Magha polar longitude at 126
  degrees and Chitra at 180 degrees 50 minutes. The editors also state that
  their coordinate interpretation is presumptive, so the Magha record remains
  `SOURCE_TABLE_ACQUIRED_MODERN_TRANSFORMATION_UNRESOLVED`; it cannot be used
  as a current ecliptic anchor or averaged with Chitra.
- Replaced the S1B V1 audit ledger with a V2 audit-only five-profile Swiss
  Ephemeris matrix. `TRUEPOS` is now recorded correctly as retaining nutation
  unless `NONUT` is requested, while returned flags document the automatic
  no-aberration/no-deflection behavior. The active apparent-Spica runtime
  reconstruction remains unchanged and non-default.
- Solar/lunar phase mappings and firmament remain fail-closed. No package was
  built. Price/outcome data, polarity, score, Fields, SBC, Auto Suggest, ML,
  MT5, and execution remain disconnected; `executionAllowed=false`.
- Source report: `docs/research/CGVO_S1B_R1_SOURCE_ACQUISITION_REPORT.md`.

## Historical Update - 2026-08-22 (CGVO-S1B Varahamihira Source Audit)

- Added a bounded, read-only CGVO-S1B source audit. The active
  `VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1` calculation is unchanged and
  remains an explicit non-default reconstruction. The source ledger now makes
  its apparent-Spica method, true-star variant, and mean-ecliptic variant
  inspectable across eight historical epochs without making any audit profile
  runtime-selectable.
- No usable checksum-identified Pancasiddhantika witness with a Magha numerical
  anchor is held. `PANCHASIDDHANTIKA_MAGHA_ANCHOR` therefore remains
  `SOURCE_SILENT_NOT_CALCULATED`; no Chitra/Magha comparison or average is
  produced.
- The held Iyer 1884 working witness confirms only that the source speaks of
  eclipse commencement and termination. It does not close a solar C1/C4 or a
  lunar P1/U1 mapping, so both phase ledgers remain unknown and all effect and
  Jupiter activation fields remain `null`. The V.28-31 firmament conflict also
  remains `COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED`; raw modern geometry is still
  not a historical classifier.
- Source audit record: `docs/research/CGVO_S1B_SOURCE_AUDIT_REPORT_V1.md`.
  No package was built. Price/outcome data, polarity, score, Fields, SBC, Auto
  Suggest, ML, MT5, and execution remain disconnected; `executionAllowed=false`.

## Latest Update - 2026-08-19 (PFR-V2B-R8-XE3 Founder-Inspection Candidate)

- Immutable founder-inspection candidate `0.10.55-pfr-v2b-r8-xe3` was built
  from clean source commit `680f023c7132de8744b04189ddf35bcc93f166b0` and is
  stored under `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.55-pfr-v2b-r8-xe3-tauri`.
  Portable SHA-256:
  `F603F114212FD13E153B16B65D3DD521F9E24FCAFE36DDF32C41FFE0B8756FBC`.
  Installer SHA-256:
  `0FE1765819470AA46B560FEB0D2B83D8D41C541F11DC4351A329DDF733C4CECA`.
- Candidate verification passed: frontend `41/41` files and `172/172` tests,
  backend `245/245`, Rust `19/19`, Oxlint, production frontend build, and two
  isolated portable smoke runs. Both smokes validated sidecar health, controlled
  same-port restart/recovery, layout persistence, clean shutdown, and
  `executionAllowed=false`. The optional candlestick specialist was safely
  absent in both smoke runs, so each is a conditional pass only on that
  explicitly optional feature.
- Candidate report and founder checklist:
  `docs/research/PFR_V2B_R8_XE3_FOUNDER_INSPECTION_CANDIDATE_0.10.55-pfr-v2b-r8-xe3.md`.
  This candidate is not founder accepted. Founder review decisions, evidence
  admission, trial freeze, outcome evaluation, and all execution remain
  pending/locked.

## Implementation Detail - 2026-08-19 (PFR-V2B-R8-XE3 Outcome-Blind Sign Admission)

- XE3 adds a separate **Experiments** profile for founder-only, outcome-blind
  sign review of the existing USD and JPY April 2025
  `SINGLE_PASS_VERIFIED` packets. It reads packet and integrity-manifest
  identities only; it does not read price, price outcomes, live MT5, Fields,
  SBC, Auto Suggest, ML, or execution state. The shell masks the refresh/live
  quote status and pauses market-facing pollers while XE3 is selected.
- Canonical blank review packets remain untouched. Founder changes are stored
  as append-only revision records outside Git, then compiled into an immutable
  hash-linked signed-evidence ledger. Explicit `SUPPORTIVE`, `ADVERSE`, and
  `NEUTRAL` project to `+1`, `-1`, and exact `0`; `MIXED`, unknown, and rejected
  entries never become a synthetic zero or directional vote.
- The frozen XE2 M0-M4 code path is reused with its existing beta `0.8`,
  bounds `0.5` to `1.5`, gamma `0.5`, causal binding, and direct-motion gate.
  It is labelled **REAL SIGNED EVIDENCE - OUTCOME NOT EVALUATED** and has no
  transform winner, price result, or forecast.
- A preregistration freeze is available only after terminal review of both
  sides. It requires the reviewed packet/ledger hashes and an exact source
  commit bound into a reproducible desktop candidate. With the current zero
  founder decisions it remains `NOT_FROZEN`, `freezeReady=false`, and outcome
  evaluation is blocked.
- Implementation record:
  `docs/research/PFR_V2B_R8_XE3_OUTCOME_BLIND_SIGN_ADMISSION_AND_PREREGISTRATION.md`.
  Current source work is ready for a clean candidate build; founder inspection
  and any decisions remain pending. `executionAllowed=false`.

## Latest Update - 2026-08-19 (PFR-V2B-R7-XE2R1 Founder Acceptance)

- The founder physically accepted the immutable `0.10.54-pfr-v2b-r7-xe2r1`
  candidate. Acceptance covers the repaired Auto Refresh observability state,
  preservation of the historical 08:30 IST failed run, later-bar progression,
  M0-M4 display, full XE2 event provenance, layout behavior, and the absence
  of execution leakage.
- The exact accepted hashes and commit lineage are recorded in
  `docs/research/PFR_V2B_R7_XE2R1_FOUNDER_ACCEPTANCE.md` and
  `status/acceptance/pfr_v2b_r7_xe2r1_founder_acceptance.json`.
- `XE2R1_FOUNDER_ACCEPTED=true`, `XE2_FOUNDER_ACCEPTED=true`, and
  `executionAllowed=false`. This bookkeeping record changes no XE2 mathematics
  or market/outcome boundary.

## Latest Update - 2026-08-19 (PFR-V2B-R7-XE2R1 Refresh Diagnosis and Founder Candidate)

- The 08:30 IST prospective-refresh warning was diagnosed from the preserved
  run record, not guessed from the UI. Run
  `b0a0b423a70148349472469386bc457c` for close
  `2026-08-19T03:00:00Z` failed at the initial MT5 server-time normalization
  gate. Its exact error was: `MT5 server-time normalization failed: MT5 terminal
  is not connected; Python and MQL5 raw tick times disagree; normalized market
  tick is not close to observed UTC`. Source snapshot, price source,
  generation job, and artifact IDs are all absent, so the failure occurred
  before capture/promotion/generation/activation. The failed row remains
  preserved.
- The A/B/C progression is verified: checking the same close returns the same
  failed run with no duplicate; the later close at
  `2026-08-19T04:00:00Z` completed independently as run
  `8a16a3a0906e444a9344a2aa1d67a2a9`, with completed generation job
  `e2f5bc33847d42dba0f09aaca94e44ea` and artifact
  `tn_e2f5bc33847d42dba0f09aaca94e44ea`. Backend retry semantics were therefore
  left unchanged.
- The bounded shell-observability repair is pushed at
  `d333634684764111e2238e4cb59c7ec2ded50c7f`. The Auto refresh chip now labels
  this condition **Historical failure**, explains that its action checks a
  later eligible close rather than retrying the preserved bar, and exposes
  **Inspect failed run** lineage/error details. XE2 real-event rows now have
  expandable full identity/provenance details: hash, exact UTC, transit/natal
  bodies, aspect, raw Moon speed, `SINGLE_PASS_VERIFIED`, packet and integrity
  manifest hashes. No XE2 or execution mathematics changed.
- Candidate-version commit `0aaa788e6a9553b4902f1221dccfce049eb278d2` is
  packaged as founder-inspection candidate
  `0.10.54-pfr-v2b-r7-xe2r1` at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.54-pfr-v2b-r7-xe2r1-tauri`.
  Portable SHA-256 is
  `60FCA629C8DFE17E4EDA65CDF3E5F3AE574A1427BDE73CCC8338B763471A937B`;
  installer SHA-256 is
  `E48F9DFBD964CB364AFE0D9744D51BBC8955C835AD0CAEB108841B22C9B8EE5A`.
  The release manifest records source clean and `executionAllowed=false`.
- Verification: refresh `6/6`, XE2 backend `8/8`, full backend `237/237`,
  refresh-chip frontend `1/1`, XE2 frontend `4/4`, full frontend `40 files /
  169 tests`, lint/build passed, Rust fmt/check passed and Rust tests `19/19`.
  Two isolated portable smokes passed with zero errors/failed checks; the only
  deferred check is the existing optional unconfigured candlestick specialist.
- Founder inspection is pending. Use
  `docs/research/PFR_V2B_R7_XE2R1_SHELL_OBSERVABILITY_CANDIDATE_0.10.54-pfr-v2b-r7-xe2r1.md`.
  Prior candidate `0.10.53-pfr-v2b-r7-xe2` remains immutable. Fields, SBC,
  source profiles, Auto Suggest, ML, MT5 orders, XE1/XE2 mathematics, and
  execution remain locked.

## Latest Update - 2026-08-19 (PFR-V2B-R7-XE2 Founder Inspection Candidate)

- XE2 source commit `fc72f58531c079181d2a1281e9e5b48e5fa16b2e` is packaged as
  founder-inspection candidate `0.10.53-pfr-v2b-r7-xe2`. The package is at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.53-pfr-v2b-r7-xe2-tauri`.
  Portable SHA-256 is
  `0A8275A76BF2EAC624DD182A9ECB6F91EDAA72D5A021E6D21A0A9D7162152536`; installer
  SHA-256 is
  `DF1751905DD6316FB1C31C5742D28023F2B5F672FB1043351F858F7D743B8C7A`.
- XE2 reads four hash-linked `SINGLE_PASS_VERIFIED` USD April 2025 astronomical
  event identities and raw Moon speed only. The reviewed USD/JPY packets still
  contain zero founder polarity decisions, so there is no admitted real signed
  market evidence. Its M0-M4 causal-scoped math runs only against a visibly
  synthetic sign test and product output remains
  `BLOCKED_NO_REAL_SIGNED_EVIDENCE`.
- Verification passed: focused XE2 backend `8/8`, XE1 regression `13/13`, full
  backend `236/236`, focused frontend `4/4`, full frontend `39 files / 168
  tests`, broad Python `780 passed, 1 skipped, 16 subtests`, lint/build and Rust
  `19/19`. The broad skip remains the optional external JHora witness requiring
  `JHORA_WITNESS_CSV`.
- Two isolated portable smokes passed with zero failed checks. Each verified
  backend health, execution locks, source-profile contracts, same-port sidecar
  recovery, layout survival and no surviving descendants. The only deferred
  check is the optional unconfigured candlestick specialist.
- Founder inspection remains pending. Use
  `docs/research/PFR_V2B_R7_XE2_FOUNDER_INSPECTION_CANDIDATE_0.10.53-pfr-v2b-r7-xe2.md`.
  XE2 keeps no price/outcome read, no SBC or Fields fusion, no live MT5,
  Auto Suggest, ML or execution. The accepted XE1R1 `0.10.52` candidate remains
  immutable.

## Latest Update - 2026-08-18 (PFR-V2B-R7-XE2 Causal-Scoped Real Evidence)

- XE2 is a new, isolated Experiments profile. It accepts four hash-linked,
  `SINGLE_PASS_VERIFIED` USD April 2025 astronomical event identities and raw
  Moon speed values, but it admits **no real signed market evidence**: the
  reviewed USD/JPY packets have zero founder polarity decisions. Aspect
  geometry, speed and motion never supply a market sign.
- The only signed channel is visibly labelled `SYNTHETIC_SIGN_TEST_ONLY`. It
  supports a transparent M0-M4 causal-scoped modifier tournament, not a market
  forecast. Every speed modifier binds to one `CAUSAL_EVENT_ID`; there is no
  global default, stacking, or unscoped fallback.
- April 2025 remains `TOUCHED_DEV`; no price, return, SBC, Fields, live MT5 or
  outcome dataset is read. The product visibly reports
  `BLOCKED_NO_REAL_SIGNED_EVIDENCE` and blocked outcome evaluation. XE2 leaves
  Mode 1, Trailokya, Argha, Fields, Auto Suggest, ML and execution unchanged.
- XE1R1 founder acceptance remains recorded at `ccb4ee5c17dc1cce3f989832ac22196bf07b8806`.
  Its 0.10.52 package remains immutable. XE2 source verification passed:
  focused XE2 backend `8/8`, XE1 backend `13/13`, full backend `236/236`,
  frontend `39 files / 168 tests`, broad Python `780 passed, 1 skipped, 16
  subtests`, lint/build, and Rust `19/19`. The one broad skip is the optional
  external JHora witness requiring `JHORA_WITNESS_CSV`. XE2 candidate packaging
  and founder inspection are the remaining bounded steps.

## Latest Update - 2026-08-18 (PFR-V2B-R7-XE1R1 Founder Acceptance)

- The founder physically accepted immutable founder-inspection candidate
  `0.10.52-pfr-v2b-r7-xe1r1` on 2026-08-18 IST. The accepted portable hash is
  `AFA1FDDA171DE02FD3342274AC8682AAC722E5BE05ED8522352F6FA49E7ED116` and the
  accepted installer hash is
  `F84676FAAA5C3C40C973EBD0EB169EFA5CFB4E307A932E4CD0F62F8B9814DE16`.
- Acceptance covers the sticky Experiments safety banner, evidence-domain
  wording, `MARKET INPUT: NONE`, empty Touched/Manual Unknown states,
  `No observations admitted`, no observed clipping, and no source/runtime/
  execution leakage. The 0.10.52 portable and installer remain immutable
  accepted artifacts and are not rebuilt by this bookkeeping record.
- `XE1_FOUNDER_ACCEPTED=true`, `XE1R1_FOUNDER_ACCEPTED=true`,
  `ACCEPTED_CANDIDATE_IMMUTABLE=true`, and `executionAllowed=false`.
  Mode 1, Fields, SBC, Trailokya/Argha, Auto Suggest, ML, MT5 and execution
  locks remain unchanged. XE2 is the next bounded research milestone.

## Latest Update - 2026-08-17 (PFR-V2B-R7-XE1R1 Founder Inspection Candidate)

- XE1R1 is a bounded presentation and empty-state correction over the existing
  `XE1_EXPERIMENTAL_EVIDENCE_LAB_V1`. The sticky experimental safety banner is
  isolated to Experiments, empty Touched/Manual directional raw values are
  `null`, evidence labels are descriptive (`POSITIVE EVIDENCE`, `NEGATIVE
  EVIDENCE`, `MIXED EVIDENCE`, `UNKNOWN / BALANCED`), and the raw dataset badge
  distinguishes `No observations admitted` from `Raw fixture sealed`.
- A compact context strip states `MARKET INPUT: NONE`. XE1 raw evidence,
  causal-group deduplication, ambiguity fail-closed behavior, modifier math,
  source profiles, Fields, Auto Suggest, ML, MT5 and execution are unchanged.
- Source implementation commit is `8bf9fc20a80caf48e5bf50d70a351e8ab0901629`.
  Candidate `0.10.52-pfr-v2b-r7-xe1r1` is at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.52-pfr-v2b-r7-xe1r1-tauri`.
  Portable SHA-256 is `AFA1FDDA171DE02FD3342274AC8682AAC722E5BE05ED8522352F6FA49E7ED116`;
  installer SHA-256 is `F84676FAAA5C3C40C973EBD0EB169EFA5CFB4E307A932E4CD0F62F8B9814DE16`.
- Verification passed: focused backend `13/13`; full backend `228/228`;
  focused frontend `3/3`; full frontend `39 files / 167 tests`; broad Python
  regression `772 passed, 1 skipped, 16 subtests passed`; lint/build passed;
  Rust fmt/check passed and Rust tests `19/19` passed. The one broad skip is the
  optional external JHora witness requiring `JHORA_WITNESS_CSV`.
- Two isolated portable smokes passed with zero failed checks, sidecar recovery,
  layout persistence, and no descendant survivors. The optional candlestick
  specialist remains unconfigured and is reported as deferred by the existing
  soak contract.
- Founder inspection is ready but not accepted. Use the report
  `docs/research/PFR_V2B_R7_XE1R1_FOUNDER_INSPECTION_CANDIDATE_0.10.52-pfr-v2b-r7-xe1r1.md`
  for the physical checklist. `XE1R1_FOUNDER_INSPECTION_READY=true` and
  `XE1_FOUNDER_ACCEPTED=false`.

## Latest Update - 2026-08-17 (PFR-V2B-R7-XE1 Experimental Evidence & Modifier Lab)

- XE1 adds a separate top-level **Experiments** workspace. It is a read-only,
  synthetic-first evidence-role and modifier ablation laboratory, not a
  classical source profile, a market forecast, or an execution feature. The
  persistent banner states: `EXPERIMENTAL - NOT CLASSICAL - NOT VALIDATED - NO
  EXECUTION`.
- `XE1_EXPERIMENTAL_EVIDENCE_LAB_V1` carries immutable raw observations,
  versioned role bindings, one-vote-per-causal-group aggregation, derived-child
  suppression, ambiguous-cause fail-closed behavior, a bounded positive
  multiplier comparison, a separate confidence field, categorical state-vector
  output, and an immutable trial ledger. The optional XE1 pair adapter is
  separate from the existing Fields formula and does not read SBC.
- Synthetic data is the only populated mode. `TOUCHED_DEV` deliberately shows
  `TOUCHED_DEV_INPUT_NOT_CONFIGURED` until an explicit future evidence-admission
  milestone supplies observations; it never rebrands synthetic data. April
  2025 is recorded only as `TOUCHED_DEV`, never as a pristine holdout.
- XE1 does not read price or market outcomes, SBC, Fields, Auto Suggest, ML,
  MT5, or any execution route. All responses carry `executionAllowed=false`.
  Classical source fixtures, Trailokya source semantics, Arghya runtime
  promotion, BPHS, and the Fields formula are unchanged.
- XE1 source is pushed through `bb8337f50ee6fbc36c378f442d5f6ba82e267a5a`.
  Candidate `0.10.51-pfr-v2b-r7-xe1` is built at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.51-pfr-v2b-r7-xe1-tauri`.
  Portable SHA-256 is `3A3645F940B73FD74D2B282EA322875DFE522CE991C2945D0956978EE89D8F69`;
  installer SHA-256 is `96DA7835AEAAB3371953C2B3EDDC31BF96B70EBBC408CBD1AC75181406A9772E`.
  Full verification: backend `228/228`; frontend `81` files / `166` tests;
  focused XE1 backend `13/13`; focused XE1 frontend `2/2`; lint/build and Rust
  fmt/check/tests (`19`) passed. Two isolated portable smokes passed; the
  packaged XE1 endpoint check returned no price/SBC/Fields/execution access.
  Founder visual acceptance remains pending.

## Latest Update - 2026-08-17 (PFR-V2B-R6-SBC-TD3R Argha source reconstruction)

- TN1R1 is now founder accepted. The broad Python/source regression completed
  before that record: `753 passed`, `1 skipped` optional external JHora witness
  and `16 subtests passed`; the supported Windows frontend command completed
  `38` files / `164` tests under the single-thread pool, lint/build passed and
  Rust format/check/tests passed (`19` Rust tests).
- TD3R audited the controlling Trailokya 1972 Argha block, verses 345-378,
  directly against its page images. It closes literal relationship/aspect/Viswa
  tables, verse-371's required-aspect gate, verse-375 Argha-only netting and
  verse-376's twenty-part *commodity basis* arithmetic. It does not create a
  financial or product feature.
- A historical transcription locator error is reconciled without rewriting
  history: the old 1972 table pass retained the right values but recorded
  printed pp.52/53/55. The controlling pages are printed pp.82/83/85. The new
  page-corrected pass preserves all 108 literal values and both published
  anomalies (`11|45`, `2|18`).
- `TRAILOKYA_1972_ARGHA_SOURCE_COMPONENTS_V1` provides only exact-fraction,
  fail-closed low-level table, netting and commodity-basis components. A full
  `ARGHA_SOURCE_CALCULATOR_READY` remains false: combined four-strength ruler
  selection, Vakra/Udaya timestamp boundaries, complete Vedha traversal and
  validity, a complete worked calculation, and bhava-to-price conversion are
  not source-closed. Price, FX, polarity, score, Auto Suggest, ML, MT5 and
  execution remain locked.

## Latest Update - 2026-08-17 (PFR-V2B-R6-SBC-TN1R1 Founder Acceptance)

- The founder physically accepted packaged candidate
  `0.10.50-pfr-v2b-r6-sbc-tn1r1` after checking scrolling, the complete
  81-cell inspector, cardinal orientation, Jyeshtha LEFT/FRONT/RIGHT targets,
  direct-versus-derived target distinction, fail-closed unknowns and
  Trailokya/Agarwal profile switching. No score, polarity, price forecast,
  Fields influence or execution appeared.
- The broadest current repository Python/source regression passed before this
  acceptance was recorded: `753 passed`, `1 skipped` optional external JHora
  witness, and `16 subtests passed`. The stale legacy Trailokya compatibility
  regression was repaired in separately pushed commit `941902e` so it now
  exercises TN1's native adapter.
- The accepted binary is not rebuilt or promoted by this bookkeeping step.
  Its artifact hashes, source commit and two packaged smoke records remain in
  `docs/sbc/PFR_V2B_R6_SBC_TN1R1_FOUNDER_ACCEPTANCE.md`.
  `executionAllowed=false` remains invariant.

## Latest Update - 2026-08-16 (PFR-V2B-R6-SBC-TN1R1 Founder Candidate)

- TN1R1 source implementation is pushed at `36d16df475a49fc23e37726142e453700a5f35b8`.
  It is a layout-only correction: the native Trailokya inspector has one
  keyboard-focusable vertical scroll owner inside the Chakra content track.
  Source geometry, target authority, profile isolation and all safety locks are
  unchanged.
- Clean packaging produced founder-inspection candidate
  `0.10.50-pfr-v2b-r6-sbc-tn1r1` at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.50-pfr-v2b-r6-sbc-tn1r1-tauri`.
  Portable SHA-256 is
  `69CFEE6E02F4C87E176DBBBDF41587EB963BA7FD0086C8A8DF985A022400BCAF`;
  installer SHA-256 is
  `07A8BA528BA57D75E7453657694DDF7B46131F71DBA846E90CC37D20E2B394C0`.
  The release manifest records `source_git_dirty=false` and
  `executionAllowed=false`/read-only market data mode.
- Two isolated packaged smoke runs passed. Reports are
  `D:\GannFinancialAstro\soak\tauri_0.10.50-pfr-v2b-r6-sbc-tn1r1_20260816_171303\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.50-pfr-v2b-r6-sbc-tn1r1_20260816_171712\logs\native_soak_report.json`.
  Each verified sidecar health, Chakra 81-cell contract, Agarwal source
  profile, locks, layout persistence, sidecar recovery and zero survivors;
  only the optional candlestick specialist was deferred as not configured.
- Full verification: focused source `27 passed`; focused frontend `21 passed`;
  full frontend `164 passed`; backend `215 passed`; lint/build passed; Rust
  format/check passed and Rust tests `19 passed`. Details and the founder-only
  physical checklist are in
  `docs/sbc/PFR_V2B_R6_SBC_TN1R1_FOUNDER_INSPECTION_CANDIDATE_0.10.50-pfr-v2b-r6-sbc-tn1r1.md`.
- Physical packaged-window inspection remains pending founder review at the
  required desktop scales. No package promotion or acceptance is recorded.

## Latest Update - 2026-08-16 (PFR-V2B-R6-SBC-TN1R1 Viewport Scroll Repair)

- TN1R1 fixes the founder-observed native Trailokya clipping defect. The direct
  Trailokya branch now owns one keyboard-focusable vertical scroll region inside
  the available Chakra content track; the desktop shell remains bounded and no
  nested whole-inspector scroll box was introduced.
- The source board, enumerated target authority, source literals, unknown states,
  profile isolation and all research/execution locks are unchanged. This is a
  layout-only correction. At 1280x720 source-browser inspection, the host is
  650px high with 1472px of content, `overflow-y:auto`, and all 81 cells remain
  present; scrolling reaches the WEST row and audit footer.
- Focused and full verification plus a new immutable `0.10.50-pfr-v2b-r6-sbc-
  tn1r1` founder-inspection candidate are recorded in
  `docs/sbc/PFR_V2B_R6_SBC_TN1R1_VIEWPORT_SCROLL_REPAIR.md` and the candidate
  report. Physical packaged-window inspection remains founder-only and pending.

## Latest Update - 2026-08-16 (PFR-V2B-R6-SBC-TN1 Native Trailokya Adapter)

- TN1 replaces the former Trailokya generic-grid target walk with a native
  source adapter. `TRAILOKYA_1972_ENUMERATED_NAKSHATRA_TARGETS_V1` now controls
  direct target identity, order and FRONT targets; the native 81-cell
  EAST-top/WEST-bottom/NORTH-left/SOUTH-right board is a visual projection,
  never a substitute authority.
- Chakra now exposes `Trailokya 1972 Research`, a Manual Source Audit surface
  that presents direct targets and verses 48-52 derived semantic targets with
  one shared causal-event identity. Context-free reach is visibly `UNKNOWN`.
  It has no market mapping, polarity, score, price, Fields influence, Auto
  Suggest, ML, MT5 or execution path.
- The native board source fixture has an honest projection gap: two visible
  `A` glyphs mean `VOWEL:A` reports `AMBIGUOUS_SOURCE_PROJECTION` rather than
  an arbitrarily chosen cell. The enumerated target row remains authoritative.
- `TN1_NATIVE_BOARD_ADAPTER_COMPLETE=true`,
  `TN1_ENUMERATED_VEDHA_ADAPTER_COMPLETE=true`,
  `TRAILOKYA_TARGET_AUTHORITY=ENUMERATED_SOURCE_ROWS`, and generic fallback is
  false. Founder-inspection candidate `0.10.49-pfr-v2b-r6-sbc-tn1` is built at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.49-pfr-v2b-r6-sbc-tn1-tauri`.
  It is sourced from clean commit `1ce5c0aa5facd5c3aa1c3f5dd7e87e1d41fd79ce`.
  Both isolated portable smoke runs passed (the optional candlestick specialist
  remains unconfigured); physical founder inspection remains pending. Execution
  remains false.

## Latest Update - 2026-08-16 (PFR-V2B-R6-N1 Architecture, Source-to-Runtime and Reliability Audit)

- N1 ran in clean `D:\PycharmProjects-n1` after preserving the dirty active
  founder worktree unchanged. It independently re-hashed the controlling 1972
  Trailokya witness, ingested TD3 verses 345-428 into bounded source records,
  and kept all Arghya/commodity material outside runtime. The 28-nakshatra
  commodity ledger is `FINANCIAL_HYPOTHESIS_LEDGER_ONLY`, with exact verified
  source page locators and explicit FX/polarity/score/execution prohibitions.
- The audit found and repaired two engineering defects without changing
  research semantics: missing execution locks at frontend/Tauri/companion
  transport boundaries now fail closed, and direct Trailokya geometry refuses
  to borrow the generic Phaladeepika-derived grid. A source-native Trailokya
  grid adapter remains a P1 future task; Fields continues to show the honest
  `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` availability state instead of a
  fallback wave.
- Audit documentation now traces source-to-product-to-execution paths,
  profile isolation, unknown propagation, numerical-system separation, test
  quality and repository hygiene. The checkout remains about 1.09 GiB because
  historical backup/evidence data was deliberately not deleted.
- Verification: affected Trailokya/Chakra tests 51/51; full Python regression
  749 passed, 1 explicitly skipped external-witness test, 16 subtests; focused
  frontend transport suite 3 files/21 tests; full frontend 37 files/163 tests;
  lint/build passed; `cargo fmt --check`, `cargo check`, and Rust tests 19/19
  passed. No polarity, score, price forecast, Fields polarity, Auto Suggest,
  ML, MT5 or execution path was added; `executionAllowed=false` remains
  invariant.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-TD1R1 Trailokya Source-Contract Correction)

- Central source review found concrete TD1R machine-transcription defects, so
  TD1R1 re-opened the private controlling 1972 page images and re-audited all
  28 target rows. The current record corrects Punarvasu (adds Purva
  Bhadrapada), Pushya (adds Shatabhisha), Anuradha (restores the stated
  Vama/Dakshina direction assignment), Jyeshtha (`ANUSVARA`, not `VISARGA`),
  canonical dental/retroflex/sibilant tokens, verse 48-52 expansions and
  source locators.
- The new `trailokya_1972_td1r1_correction_audit_v1.yaml` preserves the
  historical TD1R defect record rather than rewriting history. Exact-content
  golden tests now assert every row's ordered target lists, front target,
  verse and source locator. The ASTA record is reduced to an astronomical
  visibility state with `UNKNOWN_NOT_SOURCE_ESTABLISHED` Vedha direction; the
  source does not authorize `ASTA => NO_DIRECTION`.
- Runtime and UI remain untouched. No polarity, score, price forecast, Fields
  polarity, Auto Suggest, ML, MT5 or execution capability was added;
  `executionAllowed=false`. TD2, Latta and runtime promotion remain blocked
  pending a separate directive.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-TD1R2 Final Trailokya Glyph Correction)

- A surgical re-read of the controlling 1972 page images and the same-lineage
  2016 reading witness corrected the final two TD1R1 residual glyph errors:
  verse 48's third pair is `SSA_RETROFLEX <-> KHA` (`ष <-> ख`), not
  `PA <-> KHA`; Jyeshtha's left sequence uses `VISARGA` (`अः`), not
  `ANUSVARA`. TD1R historically held the latter source value correctly;
  TD1R1's change is preserved as a superseded historical adjudication.
- The current state is the TD1R2-corrected source contract. The native target
  map is trusted for its bounded source role; the complete Vedha operator and
  runtime promotion remain false. No runtime, UI, polarity, score, price,
  Fields, Auto Suggest, ML, MT5 or execution behavior changed.
- TD1 is now closed for this source range. TD2 may be proposed separately for
  1972 scan pp.52-62 / printed pp.36-46; no TD2 work started here.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-TD1R Trailokya Native Source Contract)

- TD1R independently re-hashed the controlling 1972 Trailokya scan and the
  same-lineage 2016 reading witness, then visually audited the specified page
  ranges. It adds immutable source-only artifacts for the native EAST-top,
  WEST-bottom, NORTH-left, SOUTH-right 81-cell board; an enumerated 28-row
  target map including Abhijit; letter/vowel/corner expansions; categorical
  planet-nature conditions; and source coarse motion classifications.
- The bounded contract is `TRAILOKYA_1972_STHULA_VEDHA_SOURCE_V1`. Its target
  enumeration supersedes Phaladeepika shared board-ray fixtures as controlling
  Trailokya source evidence, while retaining those fixtures for legacy history
  and non-Trailokya components. No runtime engine, UI, score, market mapping or
  package has been changed.
- Exact instantaneous swift/mean threshold, stationary state, the Shukla
  Panchami overlap, modifier/precedence, Latta and complete Arghya arithmetic
  remain explicit fail-closed gaps. No polarity, price forecast, Auto Suggest,
  ML, MT5 or execution behavior was added; `executionAllowed=false`.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-TD0R Trailokya Translation Recovery Audit)

- The original 1972 Trailokya scan, OCR navigation companion and same-lineage
  2016 reprint were re-hashed against their registered values. TD0R recovered
  the historic Vedha packet, legacy guidance profile, both 108-row Arghya
  passes and their reconciliation record without changing runtime behavior.
- A new page-coverage ledger distinguishes original-image statements from OCR
  navigation, same-lineage reading support, Phaladeepika shared-fixture use and
  engineering normalization. The legacy Trailokya runtime guidance remains
  untouched and is explicitly not a complete Trailokya translation or market
  model.
- The narrow source findings remain: direction/reach passages on scan 20-21,
  practical manual placement on scans 9-11, natural-condition text on scans
  29-30, isolated modifier wording on scan 55 and execution-locked Arghya
  material on scans 98-102. No new source variable, score, polarity, price
  conversion, product surface, package or execution capability was added.
- The next potential work remains separate and founder-directed: motion-state
  definitions, source-specific target/corner geometry, Moon/Mercury conditions,
  modifier precedence, Latta, or a reproducible Arghya worked arithmetic gate.

## Latest Update - 2026-08-15 (Trailokya TD2R Source Closure)

- Added static 1972 source contracts for Vedha magnitude/state records,
  deliberately scoped context-resolution passages, and Graha Latta.
- The 1972 original page images remain controlling. The same-lineage 2016
  reprint remains a reading witness only; OCR remains navigation/draft support.
- The recorded isolated verse-166 modifiers are not a combined scalar. Swift
  is a base source result, not a fabricated `1.0` multiplier. The source does
  not close modifier stacking, a continuous motion threshold or stationary
  handling.
- Latta is explicitly separate from left/front/right Vedha: it is a 27-star
  ordinal record with the counting origin still unresolved and no diminished
  Moon rule admitted.
- Later Arghya references are context only. No 20/15/10/5 Vedha phala value is
  merged with Viswa/Vimsopaka, and no market/FX inference was added.
- No runtime, UI, Fields, polarity, score, Auto Suggest, ML, MT5 or execution
  behavior changed. `executionAllowed=false` remains invariant.

## Validation Follow-up - 2026-08-16 (Trailokya TD2R Exact Golden Coverage)

- Re-verified the private controlling 1972 and same-lineage 2016 witness
  SHA-256 values without placing either source file in Git. A direct page-image
  spot audit re-confirmed the verse 162-166 magnitude passage.
- Hardened the static TD2 source tests from representative sampling to exact
  assertions for both phala tables, the verse-165 bridge, all isolated
  verse-166 modifier records, the complete friendship matrix, sign-lord table,
  dignity and node records, and the full Latta offset table.
- This is test-only contract hardening. It does not change source YAML,
  runtime/UI behavior, Fields, polarity, score, price logic, Auto Suggest, ML,
  MT5 or execution; `executionAllowed=false` remains invariant.

## Prior Update - 2026-08-15 (Agarwal A2R1 Founder Acceptance Recorded)

- The founder physically inspected and accepted `0.10.48-pfr-v2b-r6-sbc-a2r1`.
  The corrected badge reads `GEOMETRY CLOSED · STRENGTH SOURCE-RECORDED`.
- This accepts only the bounded read-only Agarwal Geometry/Strength Inspector:
  source-derived board, orientation, cell audit, p.144 provenance, row-level
  strength records, Vedha dependency status and Chapter-20 research lock.
  It does not authorize a full Vedha operator, polarity, score aggregation,
  price mapping, Fields influence, Auto Suggest, ML, MT5, or execution.
- `A2_SCOPE_GEOMETRY_STRENGTH_INSPECTOR` is now `FOUNDER_ACCEPTED`; the next
  source-only work may proceed independently under the Trailokya TD0R recovery
  audit.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-A2R1 Agarwal Founder Wording Correction)

- The founder physically reviewed the preceding Agarwal A2 candidate. The
  board, EAST/WEST/NORTH/SOUTH orientation, 81-cell audit, p.144 provenance,
  source-strength panel, Vedha dependency panel, Chapter-20 research panel,
  profile isolation and execution locks visually passed.
- The only required correction was semantic: `GEOMETRY + STRENGTH SOURCE
  CLOSED` overstated the mixed strength evidence. The product now displays the
  exact badge `GEOMETRY CLOSED · STRENGTH SOURCE-RECORDED`. Row-level
  `SOURCE_CLOSED` and `PARTIAL` strength states remain distinct; no aggregate
  strength claim was introduced.
- Source implementation commit: `76a073365dcab2aec176542911f01ef18769e66d`; candidate metadata/source commit:
  `1d3896befae4e34aa9c3804c0bee4452aad8a830`. Corrected candidate:
  `0.10.48-pfr-v2b-r6-sbc-a2r1` under
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2r1`.
  Portable SHA-256 is
  `1D9B263747562F89373926BF7D44126C91EDD127CCCAEB9573460C972AF3AA38`;
  installer SHA-256 is
  `5423D4F7C4288C6A274B6009FC1AB79272EBB24FAEE3F7FDFFF5EF5C3E38876B`.
- Verification: focused Agarwal frontend 2/2; full frontend 37 files/159
  tests; focused Agarwal backend 5/5; full backend 214/214; lint/build passed;
  Rust fmt/check passed; Tauri tests 19/19. Two packaged portable smoke runs
  passed required health, Agarwal 81-cell, recovery, layout, lock and shutdown
  checks. The optional candlestick specialist remains not configured.
- Final founder confirmation is pending physical inspection of this corrected
  candidate. It is not recorded as founder-accepted yet. Locked state remains
  `AGARWAL_GEOMETRY_READY = true`, `AGARWAL_STRENGTH_READY = true` for source
  records only, `AGARWAL_VEDHA_OPERATOR_READY = false`,
  `A2_SCOPE = GEOMETRY_STRENGTH_INSPECTOR_ONLY`, Chapter 20 research-only and
  `executionAllowed = false`.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-A2 Tauri GET Bridge Correction)

- Founder inspection of the `0.10.47-pfr-v2b-r6-sbc-a2` candidate revealed a
  native-only source-profile failure: the Tauri bridge posted to the
  read-only `GET /api/chakra-lab/agarwal-source-profile` endpoint. FastAPI
  returned a method error with a non-JSON body, which the native parser then
  surfaced misleadingly as an invalid-JSON error.
- The correction routes the authenticated desktop bridge through a dedicated
  loopback `GET` helper. It adds exact request regression coverage and reports
  non-JSON sidecar failures as their HTTP status. The release smoke procedure
  now also verifies the Agarwal endpoint's contract, 81 source cells, explicit
  `VEDHA DEPENDENCY_NOT_READY`, and read-only execution lock.
- Replacement candidate: `0.10.48-pfr-v2b-r6-sbc-a2-bridgefix`, under
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.48-pfr-v2b-r6-sbc-a2-bridgefix`.
  Its manifest records source commit `3978e668828afba36ead64ec8bd1aee633350d4a`
  and `source_git_dirty = false`. Portable SHA-256 is
  `547559DA8532688D6D74ED49E2F7E3386AAFB4FF87FAF37D30BC33399D7FE38E`;
  installer SHA-256 is
  `A835AC241F13ADEAABFDCF77E4A0C99D23BC874BC64B6E5FDF6669D208DF6CA3`.
  Two exact-portable smoke runs passed endpoint, recovery, layout and shutdown
  checks, including Agarwal's 81-cell, read-only, Vedha-unavailable contract.
  The original `0.10.47` candidate remains evidence of the discovered fault,
  not a valid Agarwal inspection build.
- No doctrine, board geometry, strength record, Fields/pair behavior,
  polarity, score, Auto Suggest, ML, MT5, or execution capability changed.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-A2 Agarwal Geometry/Strength Inspector)

- Implemented and pushed the founder-authorized, read-only Agarwal 2000
  Geometry/Strength Inspector at source commit
  `25274c68b99d87a43c24c98c5f83604565cff340`.
- The Chakra source-profile selector now exposes `Agarwal 2000 Research` as a
  separate profile. It renders the committed A1R3 `AGARWAL_PAGE145_CORE_9X9_V1`
  fixture: 81 cells, EAST top, WEST bottom, NORTH left and SOUTH right. Cell
  selection exposes literal source label, varga number, layer, page, packet ID
  and source status. No second UI geometry table was added.
- The backend contract is
  `AGARWAL_GEOMETRY_STRENGTH_INSPECTOR_V1`. It reads the immutable geometry,
  strength and Chapter-20 ledger packets without chart, price, Fields, pair or
  Swiss-Ephemeris computation. Strength is seven source rows only; no master
  score is calculated. Private photograph paths/bytes are not exposed or
  packaged.
- Metadata cleanup removed the stale `AGARWAL_GEOMETRY_READY_FALSE` full-Vedha
  blocker and recorded durable private-source locators separately from the
  original acquisition locators. The old A1R2 `UNKNOWN_CENTER_FOLD` finding is
  preserved historically and remains superseded only for current p.145 core
  geometry.
- Visible product locks remain: `AGARWAL_VEDHA_OPERATOR_READY = false`,
  `A2_SCOPE = GEOMETRY_STRENGTH_INSPECTOR_ONLY`, Chapter 20 is
  `FINANCIAL_HYPOTHESIS_LEDGER_ONLY`, and `executionAllowed = false`. No
  rays, polarity, score, Fields influence, Auto Suggest, ML, MT5 or execution
  path was added.
- Verification: focused UI 22/22; full frontend 37 files/159 tests; focused
  Agarwal backend 5/5; full backend 214/214; Oxlint passed; production build
  passed; Rust fmt/check passed; Tauri Rust tests 18/18.
- Founder candidate: `0.10.47-pfr-v2b-r6-sbc-a2`, under
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.47-pfr-v2b-r6-sbc-a2`.
  The release manifest reports source commit
  `25274c68b99d87a43c24c98c5f83604565cff340` and `source_git_dirty = false`.
  Two packaged native smoke runs passed core health/recovery/layout/shutdown
  checks; the optional candlestick specialist was not configured. A fresh
  packaged UI launch displayed a Windows Firewall permission prompt, so
  packaged Agarwal profile selection remains a founder-only physical check.
  This is not founder acceptance.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-A1R3 Page-145 Geometry Source Closure)

- Four newly supplied, checksum-verified private photographs of Agarwal printed
  p.145 were materialized outside Git. `1000413731.jpg` and `1000413730.jpg`
  independently transcribe the complete author-oriented 9x9 core board;
  `1000413061.jpg` and `1000413732.jpg` preserve printed-page/spread context.
- The old A1R2 `UNKNOWN_CENTER_FOLD` result is preserved as historically
  correct for the earlier folded spread, but is now
  `SUPERSEDED_BY_CLEAR_PAGE145_PHOTOGRAPHS` for current core-geometry
  readiness. The new evidence fixture has **81/81** direct field agreements,
  no image adjudications, no unresolved machine core cells, and an exact p.144
  allocation reconciliation.
- `AGARWAL_GEOMETRY_READY = true` for a strictly read-only core-board display;
  `AGARWAL_VEDHA_OPERATOR_READY = false`. `AGARWAL_A2_READY = true` only for
  an `ELIGIBLE_FOR_FOUNDER_AUTHORIZATION` Geometry/Strength Inspector scope.
  The completed core map does not create a Vedha operator or any direction,
  polarity, scoring, timing, or financial calculation.
- Chapter 20 remains `FINANCIAL_HYPOTHESIS_LEDGER_ONLY`. Polarity, price
  mapping, scoring, Fields, pair fields, Auto Suggest, ML, MT5 and execution
  remain disabled for all Agarwal material.
- Verification: A1R3 source-reconciliation fixtures **15/15**; touched Agarwal
  YAML records parse; unchanged supported backend regression **209/209**. No
  frontend or Windows candidate work belongs here.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-A1R2 Geometry and Vedha Source Closure)

- A bounded private-source search found **no newer authenticated flat or
  centre-fold capture** of Agarwal printed pp.145-146. The existing hardcopy
  figure and old-scan overlap remain the only valid witnesses; `UNKNOWN_CENTER_FOLD`
  survives and no 81-cell map is inferred.
- The source record now distinguishes real Chapter 9 closure from an executable
  engine: Agarwal explicitly names the five subject factors, nine-transit
  placement, direction/motion descriptions, a 28-row star/sign target chart,
  stated planet classes, and selected exceptions. Motion-state precedence,
  board-cell target resolution, complete simultaneous-hit/cancellation handling,
  universal validity windows, and worked-method reproducibility remain partial.
- `AGARWAL_GEOMETRY_READY = false`, `AGARWAL_VEDHA_OPERATOR_READY = false`,
  `AGARWAL_A2_READY = false`; no Agarwal UI scope is authorized. The smallest
  remaining dependency is an authenticated, unambiguous complete author-figure
  capture followed by the unresolved deterministic operator dependencies.
- No financial boundary changed: Chapter 20 remains a locked
  `FINANCIAL_HYPOTHESIS` ledger. Polarity, price mapping, score aggregation,
  Fields, Auto Suggest, ML, MT5 and execution remain disabled for Agarwal.
- Verification: A1R2 source-reconciliation fixtures **9/9**; touched Agarwal
  YAML files parse; unchanged supported backend regression **209/209**. No
  frontend or Windows candidate work belongs in this milestone.

## Latest Update - 2026-08-15 (PFR-V2B-R6-SBC-A1R1 Complete Capture and Page Extraction)

- `Agarwal_front.pdf` is now privately materialized at
  `D:\GannFinancialAstro\sources\private\agarwal_hardcopy_20260813\` with the
  expected SHA-256 `D117CC540DD3E24CCAC3E565F1BF20A1A4FB72DED531298FB69AF3708B72E2E9`
  and seven pages. The complete private capture gate is now **6/6 verified**.
- Source-only A1R1 work records: two-pass-agreed p.54-55 and pp.60-63
  numerical/general-strength rows, p.144 allocation groups, partial pp.145-146
  author-figure geometry, a partial Chapter 9 direction-by-motion record, and a
  page-level Chapter 20 `FINANCIAL_HYPOTHESIS` ledger. No source image is tracked.
- Old-scan/hardcopy comparisons were recorded per printed page. Recovered pages
  remain hardcopy-controlled. No ChiStaBo derivative fills any gap, and the
  figure's exact center/small cell data stays `UNKNOWN_CENTER_FOLD`.
- `AGARWAL_STRENGTH_READY = true` only for source-record use and
  `AGARWAL_FINANCIAL_HYPOTHESIS_READY = true` only for a locked research ledger.
  `AGARWAL_GEOMETRY_READY = false`, `AGARWAL_VEDHA_OPERATOR_READY = false`, and
  `AGARWAL_A2_READY = false`. The smallest remaining source dependency is an
  unambiguous full cell map plus complete operator dependencies.
- No profile/UI/execution work occurred. Agarwal remains prohibited from Mode 1,
  Fields polarity, pair fields, scores, price conversion, Auto Suggest, ML,
  live inference, MT5 and execution.
- Verification: A1R1 source-reconciliation fixtures **6/6**; all touched
  Agarwal YAML files parse; unchanged supported backend regression **209/209**.
  No frontend or package build was run because this milestone changes neither.

## Latest Update - 2026-08-14 (PFR-V2B-R6-SBC-A1 Agarwal Source Reconciliation)

- Reconciled the stale Agarwal acquisition status: the founder-held Sagar
  Publications, New Delhi, `First Edition 2000` is now recorded as physically
  evidenced, while the original 191-page scan remains an incomplete historical
  file and the old `AGARWAL_2000_SBC_PENDING` record is retained only as a
  superseded acquisition request.
- Five required hardcopy captures are now materialized in the private D: source
  directory and each matches its recorded SHA-256. The sole remaining
  dependency is `Agarwal_front.pdf`; A1's explicit all-capture gate means the
  page-level extraction branch remains blocked. The composite map covers
  printed pages 1-194 and marks pp.46-47, 54-55, 62-63, 133, 144, and the
  pp.145-146 author figure as `BLOCKED_A1_CAPTURE_SET_INCOMPLETE`. No
  derivative text was used to reconstruct any page.
- `AGARWAL_A2_READY = false`: no numerical-strength transcription, SBC figure
  fixture, Agarwal Vedha operator, financial-hypothesis ledger, cross-profile
  comparison, profile, polarity, score, market mapping, Auto Suggest, ML, MT5,
  or execution behavior was added. Restore and checksum-verify the six capture
  files at `D:\GannFinancialAstro\sources\private\agarwal_hardcopy_20260813\`
  before rerunning the page-level extraction branch.
- Verification: A1 source-reconciliation fixture tests **3/3**; all touched
  YAML files parse successfully; unchanged Gann Astro Desk backend regression
  remains **209/209**. No frontend code changed, so no Windows candidate was
  rebuilt for this source-only milestone.

## Latest Update - 2026-08-14 (P2R2 Founder Acceptance Recorded)

- Founder physically accepted the `0.10.46-pfr-v2b-r6-bphs-t1r-p2r2`
  candidate's bounded BPHS presentation: a 14-day calculated/cached research
  page with one shared, locally scrolled, three-day visual viewport. This is a
  product acceptance only, recorded in
  `docs/fields/PFR_V2B_R6_BPHS_T1R_P2R2_FOUNDER_INSPECTION_CANDIDATE_0.10.46.md`.
- No Windows candidate was rebuilt or replaced. No Tara activation, doctrine
  promotion, polarity, score, market interpretation, Auto Suggest, ML, or
  execution behavior was added or enabled.
- Next bounded work: `PFR-V2B-R6-BPHS-T1R-P3`, a source-only audit of the
  held 1899 BPHS witness for the Tārā relation dependencies. It must fail
  closed unless every required operational dependency is explicitly supported
  by that witness.

## Latest Update - 2026-08-14 (PFR-V2B-R6-BPHS-T1R-P3 Tara Source Closure)

- Completed the held-witness-only Tara audit. `MODE_1_TARA_READY = false`:
  the 1899 witness does not close an executable ninefold Tara relation
  sequence, reference/target relation, counting or reduction rule, or
  27/28/Abhijit treatment. The existing `DEPENDENCY_NOT_READY` UI behavior is
  retained and its source-gap wording is now more precise.
- The audit distinguishes a separate **Tara Dasha** passage at printed p. 254 /
  PDF image 283 and `Atimitra` in a Lakshmi-yoga passage at printed p. 234 /
  PDF image 717 from the missing Navatara relation operator. Neither is used
  to create a rule. Source findings are recorded in
  `docs/fields/PFR_V2B_R6_BPHS_T1R_P3_TARA_SOURCE_CLOSURE.md`.
- Verification: focused BPHS/Tara service **11/11**; full Python backend
  regression **209/209**; the two relevant Chakra/Fields frontend suites
  **32/32** under the Windows threads pool; Oxlint clean; TypeScript/Vite
  production build clean. A full Vitest invocation recorded **34 files / 125
  tests passed** but exited non-zero after two Windows fork-worker start
  timeouts; the affected files were rerun successfully under the threads
  pool, so that runner anomaly is recorded rather than silently counted as a
  clean full-suite result.
- No Windows candidate was rebuilt: P3 has not activated any source-backed
  Tārā runtime behavior or introduced a new product capability. The exact
  unavailable-state wording will be included in the next bounded candidate
  that otherwise requires a package build.
- No source-backed Tara activation, polarity, score, market mapping, SBC or
  pair influence, Auto Suggest, ML, MT5, execution, BPHS-T2, or Agarwal work
  was added. The next decision is founder-only: retain the precise blocked
  Tara lane or approve a separate, explicitly profiled external-source study.

## Latest Update - 2026-08-14 (PFR-V2B-R6-BPHS-T1R-P2R2 Candidate Completed After Restart)

- Completed the founder-approved three-day BPHS display viewport. The backend
  still calculates/caches the same maximum 14-calendar-day half-open research
  page; the browser now shows one shared time-aligned three-day viewport for
  Muhurta, Tithi, Nakshatra, Yoga, Karana, civil weekday, and Tara. Horizontal
  scrolling is local UI state and issues no BPHS request. Previous/Next 14 days
  remain the only research-page controls.
- Source implementation commit:
  `ae4348cc713b68fc44398ae1b9592bb70b47c726`. Packaging metadata commit:
  `3dbd47916a751b098f668efb261bcbc2c2562ca4`; both are pushed to
  `origin/master`. Changed source paths are the BPHS pane, Fields workspace,
  application CSS, and the Fields workspace tests, with the bounded design
  note at `docs/fields/PFR_V2B_R6_BPHS_T1R_P2R2_SHARED_3_DAY_CALENDAR_VIEWPORT.md`.
- Built immutable founder-inspection candidate
  `0.10.46-pfr-v2b-r6-bphs-t1r-p2r2` at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.46-pfr-v2b-r6-bphs-t1r-p2r2-tauri`.
  Portable SHA-256:
  `257AA2B5929962D7765A7E717425994D35A771F36704BDB36D274FFFE9F0123B`;
  installer SHA-256:
  `9ADCDF615A3B17218040F7AE8DA4FCC4D9E2DB5AA78944C924CF5C743BAE9B6B`.
  The accepted `0.10.45` candidate was not overwritten. The release manifest
  records source commit `ae4348cc`, `source_git_dirty: false`, execution locks
  false, and the BPHS fixture packaged.
- Verification: focused Fields **12/12**; full frontend **36 files / 157
  tests**; Oxlint; production frontend build; full backend **209/209**;
  `cargo fmt --check`; `cargo check`; Rust **18/18**. The frontend build has
  only the known non-blocking chunk-size warning. Two isolated portable smoke
  launches passed every **42/42** applicable check; only the optional,
  unconfigured candlestick specialist was deferred.
- Candidate report:
  `docs/fields/PFR_V2B_R6_BPHS_T1R_P2R2_FOUNDER_INSPECTION_CANDIDATE_0.10.46.md`.
  Physical founder inspection remains pending. Do not claim founder acceptance,
  and do not begin Tara/Agarwal work or any polarity, score, market, Auto
  Suggest, ML, or execution milestone from this candidate.

## Latest Update - 2026-08-14 (PFR-V2B-R6-BPHS-T1R-P2R1 Candidate Completed After Restart)

- The interrupted Windows founder-candidate build resumed from the completed
  clean source commit `e632c82d8f23142532f91d52d710e339ae9167e1` rather than
  rebuilding or changing product code. Candidate
  `0.10.45-pfr-v2b-r6-bphs-t1r-p2r1` is now complete at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.45-pfr-v2b-r6-bphs-t1r-p2r1-tauri`.
- It has both the self-contained portable `GannAstroDesk.exe` and the NSIS
  installer. The release manifest records `source_git_dirty: false`, the exact
  source commit, Node/npm versions, and execution lock state. Portable SHA-256:
  `061C2FEFEE41896CE6CFE1C1174D7694ABA1671A234E45D66EBF211096083CFD`;
  installer SHA-256:
  `BFFE90D6FC809310A63A280AD6C1DB5E547063264596BE0579CBA5161E23033E`.
- Fresh-checkout verification completed: focused Fields/window **13/13**;
  focused BPHS/synchronized backend **15/15**; Founder Review portability
  **9/9**; frontend **36 files / 156 tests**; full backend **209/209**;
  Oxlint, production frontend build, Cargo format/check, and Rust **18/18**.
- Two isolated portable smoke launches passed every **42/42** applicable
  check. Each verified the bundled sidecar health, safety locks, controlled
  same-port sidecar recovery, persisted layout, and clean process shutdown.
  The only deferred test is the explicitly optional, unconfigured candlestick
  specialist. A direct bundled BPHS endpoint probe also returned the bounded
  `BPHS_CLASSICAL_CALENDAR_RANGE_V1`, 40 intervals, named Muhurta, Tara
  `DEPENDENCY_NOT_READY`, and `executionAllowed: false`.
- Candidate report:
  `docs/fields/PFR_V2B_R6_BPHS_T1R_P2R1_FOUNDER_INSPECTION_CANDIDATE_0.10.45.md`.
  This is founder inspection only, not founder acceptance or a stable release.

## Latest Update - 2026-08-14 (PFR-V2B-R5-F2A-R3 Windows Packet Hash Portability)

- The fresh clean Windows founder-candidate checkout reproduced the seven
  Founder Review backend errors previously expected by the directive. They were
  not astronomy, founder-packet, or decision failures: Git had checked the
  canonical LF blank JSON packet out as CRLF and the workbench incorrectly
  hashed raw local bytes.
- The narrow workbench repair normalizes only CRLF-to-LF for packet-file
  digests. It preserves the recorded canonical V1 hashes across Windows and LF
  checkouts while still rejecting an actual packet change, including an added
  newline. No V1 blank packet, manifest, event identity, review field,
  catalogue entry, polarity or execution behavior changed.
- Added a regression fixture that verifies LF and CRLF copies of the same
  immutable packet are eligible, while the existing appended-newline mismatch
  remains fail-closed. Full clean-checkout regression and package verification
  are being rerun before the `0.10.45-pfr-v2b-r6-bphs-t1r-p2r1` candidate is
  built.

## Latest Update - 2026-08-14 (PFR-V2B-R6-BPHS-T1R-P2R1 Shared 14-Day Fields Window)

- Implemented the founder-approved maximum **14-calendar-day**, half-open
  shared Fields research window. It is anchored to the loaded chart-data start
  and advances in deterministic non-overlapping pages. The broad price chart
  remains visual context only; it no longer expands the expensive Fields
  calculation range.
- The same current research page now drives the USD side field, JPY side field,
  pair-relative field, independent SBC request/availability lane, and the
  optional BPHS Classical Calendar. Fields has explicit Previous/Next 14-day
  buttons, a page-count/date label, and `Load window containing crosshair`.
  Crosshair movement alone does not page or start requests. Completed exact
  page/profile results cache in the current session; request sequencing
  discards a late prior-page response.
- The BPHS endpoint now fails before Swiss-Ephemeris work for a direct request
  longer than fourteen days with
  `BPHS_INTERACTIVE_RESEARCH_WINDOW_EXCEEDS_14_DAYS`. The lower-level
  synchronized-range compiler was audited: its production frontend caller is
  Fields, so the explicit interactive page bounds Fields without silently
  constraining unrelated direct/batch use.
- Made the BPHS control discoverable: the Fields header remains sticky while
  scrolling and its explicit `BPHS Calendar / 1899 Research` switch persists
  for the desktop session. The calendar remains entirely separate from the SBC
  profile control.
- Recorded the founder's successful 7-day physical BPHS test and accepted
  source/engineering semantics plus the 14-day product policy in
  `docs/fields/PFR_V2B_R6_BPHS_T1_FOUNDER_ACCEPTANCE_20260814.md`. The old
  unbounded `0.10.40` behavior is rejected. The new package remains pending
  physical founder verification.
- Development-sidecar timings: BPHS 1/7/14 days completed in 0.209/1.044/2.160
  seconds; the full shared Fields request completed in 7.543/7.598/7.642
  seconds. These are implementation measurements, not packaged founder proof.
- Initial source verification completed: focused Fields/window tests **13/13**; focused BPHS
  plus synchronized-range backend tests **15/15**; full frontend **36 files,
  156 tests**; Oxlint and production build; full backend **208/208**; Cargo
  format and check. A later fresh Windows clean-checkout regression did
  reproduce the seven Founder Review packet-hash errors; the separate narrow
  `PFR-V2B-R5-F2A-R3` portability repair above replaces the earlier
  development-sidecar observation. No review packet or manifest was changed.
- This milestone changes no BPHS source output, Tara state, polarity, SBC
  doctrine/profile, price interpretation, pair/SBC fusion, Founder Review
  decision, Auto Suggest, ML, MT5, or execution capability. Execution remains
  disabled.

## Latest Update - 2026-08-13 (Desktop Black-Screen Recovery)

- Investigated a founder-reported all-black native application window rather than
  assuming an astronomy or chart-data failure. The machine had two candidate
  versions active at once: an obsolete `0.10.40` instance was still holding a
  stuck corrected-generation worker, while `0.10.43` had a native window at the
  invalid off-desktop rectangle `-25600, -25600`.
- Stopped only the obsolete `0.10.40` process tree and its stale generator,
  then restored the current candidate on-screen. The normal writable research
  data under `D:\GannFinancialAstro\app_data` remains intact. The previous
  WebView folder is retained non-destructively at
  `D:\GannFinancialAstro\app_data\webview\EBWebView.black_screen_backup_20260813_234041`.
- A clean launch of the exact `0.10.43` portable candidate rendered the full
  chart, aspect ribbons, SR lines, tool rail, and backend correctly. This
  isolates the incident from the packaged sidecar, market data, and astronomy
  calculation.
- Started the bounded replacement `0.10.44-black-screen-recovery`:
  - the native Tauri main window is now centered with a deterministic
    `1280 x 800` initial size and `1024 x 640` minimum, avoiding unreachable
    saved/off-screen placement;
  - the static document now renders a visible opening state before JavaScript
    starts, so a WebView bundle failure cannot look like a silent black canvas;
  - a React error boundary replaces a genuine render failure with an explicit
    recovery state and records an existing failed `app_bootstrap` diagnostic;
  - ordinary asynchronous request errors only record diagnostics and do not
    replace a usable workspace.
- Verification before candidate packaging: Oxlint passed; full frontend Vitest
  passed **35 files / 151 tests**; TypeScript/Vite production build passed;
  `cargo fmt --check` and `cargo check` passed. A first parallel Vitest attempt
  hit a host worker-start timeout while Cargo/build work was competing for
  resources; the affected Chakra workspace test subsequently passed **20/20**
  and the full suite was rerun sequentially cleanly.
- This is a desktop rendering/recovery change only. No doctrine, polarity,
  SBC, Fields, BPHS, Auto Suggest, MT5 execution, or research gate changed;
  execution remains disabled.
- Packaged the clean immutable founder-inspection candidate
  `0.10.44-black-screen-recovery` from exact source commit
  `efa3e2876417f1dee8e589301be5cf415ee10e5c`:
  - portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.44-black-screen-recovery-tauri\GannAstroDesk.exe`;
  - installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.44-black-screen-recovery-tauri\Gann Astro Desk_0.10.44-black-screen-recovery_x64-setup.exe`;
  - portable SHA-256:
    `C5C2F3E43A1DC3EB7635317249B69E7FC0402F01218EB339F54C1AB014EE0F41`;
  - installer SHA-256:
    `AF8F2F717D9693F8F00EC926A2DD6B438CD5819402A729D2C754D5E910D90D40`.
- Two isolated portable smokes passed. Each verified backend health, deliberate
  sidecar restart/recovery on the same port, layout recovery, disabled
  execution, and clean descendant shutdown. The optional candlestick corpus was
  not configured in the isolated profiles, which is an explicitly safe deferred
  check. The exact packaged window was also captured visibly rendering its full
  chart workspace at
  `D:\GannFinancialAstro\soak\window_captures_20260814\candidate_01044_visual.png`.

## Latest Update - 2026-08-13 (Corrected Chart Generation Worker Recovery)

- Investigated the founder-reported USDJPY D1 generation job for only 11 days
  stuck at 10%. The astronomy source compiler itself completed the exact
  10-transit x 10-natal x 4-aspect request in **7.26 seconds**, producing **45
  events** over **400** deterministic combinations. The problem was not the
  date range or aspect calculation.
- The installed `0.10.40` sidecar child was alive in a PyInstaller startup wait
  state before it reached the generator module. Its old UI exposed only a fixed
  10% event stage and had no heartbeat or timeout, making the failure appear
  like a stuck chart. The stale job `9b78280268e546e4a366cd572dce6ac7` was
  explicitly cancelled; no partially generated artifact was activated.
- First packaged candidate `0.10.41-generation-worker-recovery` proved that the
  heartbeat/watchdog correctly exposes the failure, but did not solve it: the
  real packaged job stopped after 120 seconds rather than silently remaining at
  10%. Direct execution of the same packaged worker and the same 400-combination
  request completed in about three seconds.
- An isolated desktop-sidecar reproduction identified the actual boundary: the
  Rust-managed sidecar owns a piped stdin for graceful shutdown, and the nested
  generator worker inherited that otherwise-unused handle. The generation worker
  now receives `stdin=DEVNULL` plus `close_fds=True`, while the sidecar retains
  its existing shutdown pipe. `PYINSTALLER_RESET_ENVIRONMENT=1`, atomic
  `CORRECTED_TN_EVENT_PROGRESS_V1` heartbeats, granular 10-52% event progress,
  and the 120-second fail-visible startup watchdog remain in place.
- Candidate `0.10.42-generation-worker-stdin-isolation` verified that the worker
  now enters the real 400-combination calculation and emits live progress. It
  then exposed a second Windows-only issue: the UI progress reader can briefly
  lock the target heartbeat while the worker uses atomic replacement, which
  caused an otherwise healthy job to exit during progress publication. The
  heartbeat now retries atomic replacement and degrades to a safe in-place
  snapshot if a reader keeps the file locked; reporting cannot terminate chart
  generation.
- The replacement source version is
  `0.10.43-generation-progress-lock-recovery`; a clean Windows candidate must
  still complete the same real packaged job before it is offered for founder use.
  The change does not alter astronomy doctrine, aspects, polarity, SBC, Auto
  Suggest, MT5, execution, or any research gate.
- Added `docs/research/GENERATION_WORKER_RECOVERY_20260813.md` and targeted
  tests. Focused checks: `test_corrected_natal_event_source.py` **5/5** and
  `gann-astro-desk/backend/test_generation.py` **12/12** initially, then
  **18/18** after the stdin-isolation and Windows-lock fallback regression
  assertions. A new immutable desktop candidate must be built as
  `0.10.43-generation-progress-lock-recovery` and pass the full real packaged
  job before retrying generation in the UI.
- Candidate verification completed from clean source commit
  `a189b762f415b2797158421db937a9a85ce0eafe`:
  - portable: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.43-generation-progress-lock-recovery-tauri\GannAstroDesk.exe`;
  - installer: `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.43-generation-progress-lock-recovery-tauri\Gann Astro Desk_0.10.43-generation-progress-lock-recovery_x64-setup.exe`;
  - the exact isolated packaged sidecar scenario, including the sidecar stdin
    pipe, completed the 400-combination job in **13.2 seconds**, generated
    **43 events** and **34 SR touches**, and activated artifact
    `tn_48dbde130b244ba9b7ff05b16149e5d4` in the isolated verification state;
  - two portable application smoke launches passed backend health with execution
    still disabled.

## Latest Update - 2026-08-09 (PFR-V2B-R6-BPHS-T1R-P2 Provenance Reconciliation Only)

- Re-opened the held original 1899 BPHS Chapter 14 witness before touching any
  implementation. The complete 15 daytime + 15 nighttime Muhurta facsimile is
  confirmed at **printed page 197 / PDF image 680**. Printed p. 196 / image 679
  is the Chapter-14 lead-in/root-text continuation; p. 198 / image 681 continues
  the chapter but is not the complete source table. The existing 30 source names,
  order, repetitions, and literal nighttime `Uttara` remain unchanged.
- Re-audited the full original held Chapter 14 range: printed pp. **196-258** /
  PDF images **679-741**. Printed p. 259 / PDF image 742 begins Chapter 15. No
  complete ninefold Tara sequence or timestamp-evaluable mapping/operator was
  located in that original range. The prior wording has been corrected from a
  narrow Packet-1W absence claim to a full-held-witness finding. Tara remains
  `DEPENDENCY_NOT_READY`; no external Panchanga convention, inferred reference,
  or modern formula was introduced.
- Tithi, Nakshatra, Yoga, and Karana remain explicitly
  `ENGINEERING_CALCULATED` under
  `SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1`. Their BPHS citation is now
  clearly limited to chapter-level category context, not individual
  page-transcription of a live name or boundary. Civil weekday remains
  `PARTIAL_SOURCE` and its sunrise/day ownership is still intentionally open.
- Added `docs/fields/PFR_V2B_R6_BPHS_T1R_P2_PROVENANCE_RECONCILIATION.md` and
  updated the minimal fixture, backend provenance payload, tests, and research
  notes only. No polarity, pair field, SBC, review decision, score, market data,
  LLM, Auto Suggest, MT5, or execution behavior changed or was enabled.
- Verification: focused BPHS backend suite **10/10 passed**. Because the
  sidecar-visible fixture and backend provenance strings changed, build a new
  founder-inspection candidate after committing this bounded correction; it must
  not overwrite `0.10.39-pfr-v2b-r6-bphs-t1r-p1` and remains unaccepted.
- Built the new immutable candidate
  `0.10.40-pfr-v2b-r6-bphs-t1r-p2` at
  `D:\\GannFinancialAstro\\release_candidate\\GannAstroDesk-0.10.40-pfr-v2b-r6-bphs-t1r-p2-tauri`.
  It was built from clean source commit
  `2a5dc41dd3c2340544948d723d64b035d4e20bac`; portable SHA-256 is
  `E0AD35EFC4920DC682C82B17B1016EE56F376B95D779237934B692D7B2C05FD7` and
  installer SHA-256 is
  `869D2C5768277B6B4455E725C5AF27BA76CAC8E779312ABC898F14E0FBD5E186`.
  Two portable soak runs passed health, guarded sidecar recovery on the same
  port, layout recovery, and clean shutdown. A direct packaged BPHS endpoint
  probe returned the corrected printed-p.197/PDF-680 locator, a
  source-transcribed Muhurta value, `DEPENDENCY_NOT_READY` Tara, and execution
  false. This is **not founder accepted**.
- Packaging verification also exposed an unrelated pre-existing full-backend
  regression: **206 tests ran; 7 Founder Review workbench tests error** because
  older USD packet manifests name `08DB...` while the unchanged committed packet
  bytes hash to `0484...`. P2 did not touch either the packets or their
  manifests. The focused BPHS suite, frontend lint/build, and Rust checks remain
  green. Record and repair that integrity mismatch only in a separately scoped
  milestone.

## Latest Update - 2026-08-08 (PFR-V2B-R6-BPHS-T1R-P1 Founder-Inspection Candidate)

- Audited the held 1899 BPHS Chapter 14 / Packet 1W witness before changing T1.
  The source-closing evidence for Muhurta is printed page 197 / PDF image 680,
  with a supporting Sanskrit root-text continuation over printed pages 196-197 /
  PDF images 679-680. The source explicitly enumerates 15 daytime and 15
  nighttime names.
- Added the minimal machine-readable fixture
  `research_labs/bphs_1899_classical_timing/bphs_1899_packet_1w_muhurta_fixture.json`.
  Two independent complete transcriptions, Sanskrit commentary and Hindi Bhasha,
  agree. It preserves source repetitions and the nighttime index-04 literal
  `Uttara`; no modern normalization is applied.
- The BPHS inspector now renders a source name with its day/night index, for
  example `DAY MUHURTA 01 - Ardra`. The live sunrise/sunset segment boundaries
  remain labelled `SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1` engineering
  calculation, never a claimed BPHS formula.
- The Weekday lane is now explicitly `Civil weekday (engineering)` with
  `BPHS_1899_WEEKDAY_BOUNDARY_NOT_CLOSED`. Packet 1W did not close civil-midnight
  versus sunrise/day weekday ownership, so no general Jyotisha convention was
  imported.
- Tara remains `DEPENDENCY_NOT_READY`: the audit did not locate a complete
  ninefold sequence/mapping operator in the held Packet 1W and no reference
  identity is configured. It accepts no inferred reference and imports no
  modern Panchanga formula.
- Removed the T1 service's low-level `sbc.*` imports. It now owns only its
  Swiss-Ephemeris UTC conversion and lock primitives, preserving its no-SBC
  dependency boundary. No price, return, polarity, pair, Founder Review, LLM,
  Auto Suggest, ML, MT5, scoring, or execution path was changed or enabled.
- The first `0.10.38-pfr-v2b-r6-bphs-t1r` build is **rejected before founder
  review**: its PyInstaller sidecar omitted the new Packet 1W fixture. Do not
  use that folder. Commit `9772277991c3ce3715bb0c6cb11c5890bd094369` adds frozen
  `sys._MEIPASS` resolution, bundles the fixture, and hard-fails the sidecar
  build when it is absent.
- The clean, immutable founder-inspection replacement is
  `0.10.39-pfr-v2b-r6-bphs-t1r-p1` at
  `D:\\GannFinancialAstro\\release_candidate\\GannAstroDesk-0.10.39-pfr-v2b-r6-bphs-t1r-p1-tauri`.
  Its portable SHA-256 is
  `4D5E9F2293155FB477FFA7A786A4D05FF4A5600C7158221C893DEEC0C02C3BDA`;
  installer SHA-256 is
  `6687304123DF6F74119C90E36B77E44A8838F2D8484EA0785B49515EB7EE537C`.
  The candidate was built from a detached clean checkout and the sidecar now
  contains the Packet 1W fixture under `_internal/research_labs/...`.
- Verification: focused backend **9/9**; full backend **205/205**; focused
  Fields **8/8**; full frontend **35 files, 151/151**; `oxlint`, production
  frontend build, `cargo fmt --check`, `cargo check`, and **18 Rust tests**
  passed. Two portable soak runs passed initial health, controlled sidecar
  recovery, guardrails, and clean descendant shutdown. A direct packaged BPHS
  endpoint probe returned `NIGHT MUHURTA 14 - Chitra`, partial-source civil
  weekday, `DEPENDENCY_NOT_READY` Tara, four source gaps, and execution false.
- Founder visual inspection is now ready but **not accepted or certified**.
  Open USDJPY, then Fields; set `Classical timing` to `BPHS 1899 Research`;
  move the price crosshair; inspect the separate neutral BPHS Calendar panel,
  source names/order, provenance, and gaps. Confirm no polarity, score,
  supportive/adverse color, Auto Suggest, or execution control appears.

## Latest Update - 2026-08-08 (PFR-V2B-R6-BPHS-T1 Classical Calendar Timing Inspector)

- Added the read-only **BPHS Classical Calendar** inspector inside the dedicated
  Fields workspace, behind a separate `Classical timing: Off | BPHS 1899
  Research` control. It is intentionally separate from the SBC/Vedha profile
  selector and does not modify Fields, polarity, pair-relative, SBC, Founder
  Review, Auto Suggest, ML, MT5, or execution behavior.
- The new backend contract is `BPHS_CLASSICAL_CALENDAR_RANGE_V1` at
  `POST /api/research/bphs/classical-calendar-range`. It accepts only a visible
  UTC range, IANA timezone, latitude/longitude, the explicit
  `BPHS_1899_CLASSICAL_CALENDAR_RESEARCH_V1` profile, and an optional Tara
  reference object. It returns clipped chronological half-open intervals for
  Muhurta day/night index, Tithi, Nakshatra, Yoga, Karana, Weekday, and Tara.
- Provenance is visible in the UI and payload: held source
  `BPHS_1899_GOVIND_SHARMA_SHASTRI`, 1899 Purva/Uttara witness, Chapter 14 /
  Packet 1W / pages 197-236, SHA-256
  `BB556804D8D546ACC39C43A22CECDBE2C29E3A7BA157E60EEC810C478EB645A4`.
  Calendar boundaries use the separately labelled
  `SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1` engineering calculation
  profile; this makes no claim that a Swiss-Ephemeris formula is literal BPHS
  doctrine.
- The source profile is deliberately partial. Tara is always
  `DEPENDENCY_NOT_READY` until both an explicit reference and page-transcribed
  mapping are approved. Muhurta labels show day/night index but retain the
  explicit `BPHS_1899_MUHURTA_NAME_ORDER_PENDING_PAGE_TRANSCRIPTION` gap. No
  LLM or inferred classical rule fills either gap.
- Guardrails are explicit and tested: no market/price/future-return read, no
  polarity-catalogue, pair-field, SBC, Founder Review, Auto Suggest, ML, score,
  direction, MT5, or execution path. The visual palette is neutral and carries
  no supportive/adverse state.
- Added minimal `SwissEphemerisProvider.sunset_for_local_date` support and
  optimized the inspector's single locked Swiss session so a calendar range
  does not repeatedly reconfigure or rehash ephemeris data.
- Key implementation: `gann-astro-desk/backend/bphs_classical_timing_service.py`,
  `gann-astro-desk/src/views/BphsClassicalTimingPane.tsx`, and
  `docs/fields/PFR_V2B_R6_BPHS_T1_CLASSICAL_CALENDAR_TIMING_INSPECTOR.md`.
  Research boundary: `research_labs/bphs_1899_classical_timing/README.md`.
- Verification completed: focused backend calendar suite **4/4 passed**;
  Fields UI suite **8/8 passed**; full frontend `npm test` **35 files,
  151/151 passed**; full backend `npm run test:backend` **200/200 passed**;
  `npx oxlint`, TypeScript project check, production `npm run build`, and Rust
  `cargo check --manifest-path src-tauri/Cargo.toml` passed. No Windows/Android
  candidate is built by T1.

## Latest Update - 2026-08-06 (PFR-V2B-R5-F2A-R2 Founder Polarity Review Workbench)

- Added an integrity-bound, founder-only review workbench at the top-level
  Fields surface. It loads the canonical USD and JPY April 2025 blank packets
  read-only and exposes only neutral astronomy identity facts: chart and
  hypothesis IDs, transit/natal bodies, aspect, applying/exact/separating UTC
  and IST timestamps, event ID/hash, astronomy contract, orb profile, and
  independently verified motion phase.
- Review eligibility is fail-closed. A row must match its event ID and event
  hash, the blank packet hash, the identity-integrity manifest hash, the
  accepted chart identity, the R5 F2A-R1 audit, and exact status
  `SINGLE_PASS_VERIFIED`. Unverified, hash-mismatched, multi-pass, and boundary
  failed rows cannot be reviewed or exported.
- Every decision begins blank. The founder may enter only SUPPORTIVE, ADVERSE,
  MIXED, NEUTRAL, UNKNOWN_MORE_EVIDENCE_REQUIRED, or REJECT_EVENT_IDENTITY.
  Non-rejected decisions require an explicit evidence classification and
  reviewer. Source-backed candidates require exact source ID, edition,
  locator, and connection text. Unknown remains an unknown gap; rejection
  requires a reason and never receives an evidence classification.
- Created separate initial reviewed outputs, manifests, completeness reports,
  status records, and neutral Markdown renderings for USD and JPY. Both are
  intentionally `REVIEW_NOT_STARTED`, with 12 eligible rows, zero decisions,
  zero catalogue entries, and no polarity, wave, price, SBC, LLM, Auto Suggest,
  execution, or Mode 1 admission path.
- Canonical blank packet and identity-manifest SHA-256 values remain:
  USD blank `08DB3837B89866519B7E0B24388537A2064F9EFE059D4FD5E6BCB77F82CA3D76`,
  USD identity manifest `BB0B952B3CC30A91C41D48729139CF2985542C1A64DB1D940D74FFFDBDB2E26E`;
  JPY blank `03525A80CD948869F6A8F74A656CB15CB7C11B33E8AC603F5F75628C8CAB8E9B`,
  JPY identity manifest `066BDAB7ECC0E8A6AA89E9A28B5A9EAE9B616E225759D3E022C27F185F6CFF8D`.
- Initial reviewed packet body hashes are USD
  `5B6A5FF1839C9598A47BD3F2E0C960F178F10ECDF982CBD3937DB706D2A93E8C` and JPY
  `398E1F915DAB048DA50723B22225BC033F165D074AFB1B3A0B5AF1E25F0A51A1`.
- Workbench documentation: `docs/fields/PFR_V2B_R5_F2A_R2_FOUNDER_REVIEW_WORKBENCH.md`.
  Admission validation remains preparation-only in
  `research_labs/chart_conditioned_aspects/founder_review/FOUNDER_REVIEW_ADMISSION_VALIDATOR_PREPARATION_V1.json`.
- Verification: focused backend workbench suite **8/8 passed**; frontend
  `npm test` **35 files, 150/150 passed**; backend `npm run test:backend`
  **196/196 passed**; `npm run lint`, production `npm run build`, and Python
  compilation passed. No Windows or Android candidate was built because this
  milestone stops before packaging and F2B.

## Latest Update - 2026-08-06 (PFR-V2B-R5-F2A-R1 Transit Event Identity Integrity Audit)

- Added a separate Swiss-Ephemeris, Raman-sidereal, true-node event-identity
  audit for the F2A transit-to-natal compiler. F2A's fast compiler groups one
  contiguous inside-orb run and uses a ternary minimum; the new verifier does
  not trust that as proof of a unique exact pass. It instead independently
  scans signed angular residual branches, refines roots, checks golden-section
  local minima, detects motion reversals/stations, tests monotonic approach
  and recession, verifies configured-orb boundaries, and reproduces immutable
  event hashes. It remains astronomy-only: no price, SBC, LLM, polarity,
  magnitude, catalogue admission, directional field, Auto Suggest, execution,
  packaging, or F2B path is enabled.
- Audit output: `status/audits/pfr_v2b_r5_f2a_r1_event_identity_integrity.json`.
  For the fixed April 2025 window, USD had 111 overlapping complete windows:
  **104** single-pass verified, **6** multi-pass unresolved, and **1** boundary
  verification failure. JPY had 117: **105** single-pass verified, **5**
  multi-pass unresolved, and **7** boundary failures. No incomplete
  search-horizon window intersects this founder pilot. The JSON records every
  affected event ID, all exact candidates, residuals, station/reversal times,
  boundary measurements, and hash/identity checks.
- Every current founder-pack record passes: all 12 USD and all 12 JPY V1 rows
  are `SINGLE_PASS_VERIFIED`. The original V1 JSON and SHA-256 manifests are
  preserved unchanged; no V2 packet is required. Added V1 identity-verification
  manifests and intentionally non-authoritative, blank Markdown review
  renderings in `research_labs/chart_conditioned_aspects/founder_review/`.
  These contain only UTC/IST astronomy identity and empty founder fields, never
  a polarity suggestion or market context.
- Fail-closed policy is documented: a multiple-root or non-monotonic continuous
  run remains `MULTI_PASS_EVENT_IDENTITY_UNRESOLVED`; absent verified exactness,
  invalid boundary, hash, or identity checks are
  `BOUNDARY_VERIFICATION_FAILED`. Such records are excluded from later founder
  review admission and never silently split. Rahu/Ketu node-opposition symmetry
  was checked: no accidental duplicate event ID/hash exists.
- Documented but did not activate the proposed future event-family engineering
  metadata: `eventFamilyId`, `exactPassIndex`, `motionPhaseAtExact`, station
  association, and adjacent exact-pass references. These are not classical
  doctrine or financial interpretation and require founder approval before any
  production event-contract change.
- Primary guide:
  `docs/fields/PFR_V2B_R5_F2A_R1_TRANSIT_EVENT_IDENTITY_INTEGRITY_AUDIT.md`.
  Focused audit tests cover direct, wrap, retrograde two-pass, three-pass
  station-loop, station without exactness, near-boundary exactness, hash
  reproducibility, V1 preservation, and deterministic V2 replacement order.

## Latest Update - 2026-08-06 (PFR-V2B-R5-F2A Real USD/JPY Transit Events and Blank Founder Pilot)

- Replaced the Fields workspace `events: []` placeholder with the backend-only
  `CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1` compiler. The frontend now sends
  only the visible UTC range, `USD`/`JPY` side identities, and the locked
  `ASPECT_STRENGTH_V0` geometry profile. It cannot submit a chart ID,
  chart-hypothesis ID, transit/natal pair, event identity, price result, SBC
  state, or LLM text. The backend reads the canonical founder registry and
  rejects any such client injection.
- The compiler loads only the two accepted immutable chart research hypotheses:
  USD `FX_CURRENCY_USD_US_INDEPENDENCE_17760704T165602Z_V1` /
  `USD_US_INDEPENDENCE_PHILADELPHIA_EXACT_TIME_RESEARCH_V1`; and JPY
  `FX_CURRENCY_JPY_YEN_IPO_18890210T150000Z_V1` /
  `JPY_YEN_IPO_TOKYO_EXACT_TIME_RESEARCH_V1`. It retains the historical civil
  time policy plus `RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1`.
- Each emitted TN event is immutable and includes its event/hash identity,
  side, chart/hypothesis, transit/natal bodies, aspect type, applying start,
  exact UTC, separating end, locked orb contract, ephemeris version, Raman
  ayanamsha, true-node policy, and generator version/hash. No compiler path
  reads price, SBC, Shadbala, Drik, Ashtakavarga, an LLM, or later outcomes; it
  assigns neither polarity nor magnitude and keeps all execution locks false.
- Before any review, Fields now receives real event boundaries. The empty
  target-aware polarity catalogue truthfully produces `UNKNOWN` segments with
  their actual event IDs, and USDJPY remains `UNKNOWN_SIDE_EVIDENCE` rather
  than rendering a decorative wave. A direct April range check found 111 USD
  and 117 JPY overlapping complete event windows, all still unreviewed.
- Generated non-outcome-selected, deliberately blank founder packs for the
  fixed April 2025 UTC window. The compiler found **99** complete USD events
  and **104** JPY events whose exact moment is in the window; each packet
  contains the first **12** ordered strictly by exact UTC/event ID. Every
  founder polarity, evidence class, source reference, reasoning, reviewer,
  timestamp, classification, and review-packet hash remains blank.
  Pack files and SHA-256 manifests live in
  `research_labs/chart_conditioned_aspects/founder_review/`.
- Prepared but did not activate
  `FOUNDER_REVIEW_ADMISSION_VALIDATOR_PREPARATION_V1.json`. It specifies future
  exact-identity matching and evidence-class requirements only; it does not
  admit a catalogue entry, Source Only record, polarity, pair field, or trade.
- Verification: focused chart-conditioned lab tests **7 passed**; focused
  backend compiler/range tests **12 passed**; focused frontend request tests
  **2 files / 17 passed**; full chart-conditioned lab suite **36 passed**;
  full backend suite **188 passed**; frontend `npm test` **34 files / 148
  passed**; Oxlint and production frontend build passed. No Windows candidate
  was built by design: the F2A stop gate explicitly forbids packaging and F2B.
- Primary implementation guide:
  `docs/fields/PFR_V2B_R5_F2A_REAL_SIDE_EVENT_COMPILER_AND_FOUNDER_PILOT.md`.
  This remains a review-packet foundation only. Founder review/admission,
  polarity rendering, directional pair values, smoothing, price validation,
  Auto Suggest, execution, F2B, and package promotion are still prohibited.

## Latest Update - 2026-08-06 (PFR-V2B-R5-F1 Dedicated Fields Workspace)

- Implemented a dedicated top-level **Fields** workspace. It reuses the active
  chart payload, visible UTC range, research-time controller, profile,
  visualization mode, chart identities, selected candle, and crosshair; it does
  not refetch/duplicate market chart data. The product layout is now chart,
  USD/base categorical field, JPY/quote categorical field, derived pair field,
  independent SBC field, then audit/coverage/source-gap detail. Chakra retains
  a compact **Open in Fields** hand-off rather than a primary embedded field
  stack.
- Added `FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1`, a transparent modern research
  transform, not classical doctrine, a forecast, or SBC confirmation. It uses
  only the exact union of stored base/quote interval boundaries. For USDJPY,
  `pairDisplay = clamp((usdBalance - jpyBalance) / 2, -1, +1)`. An unknown side
  produces an explicit `UNKNOWN_SIDE_EVIDENCE` gap; unknown is never replaced
  with neutral/zero. Mixed activity retains its supportive/adverse activity,
  gross activity, and conflict in the resulting audit.
- Mode behavior remains honest: visual-only suppresses directional paths with
  `DIRECTIONAL FIELD SUPPRESSED BY VISUAL-ONLY MODE`; source-only renders only
  known source-backed side data; stock symbols receive no automatic FX net
  field. SBC remains independent. Trailokya remains the score-free
  `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` availability lane with its seven source
  gaps, while Phaladeepika behavior is unchanged.
- Focused frontend verification passed **4 files / 36 tests** before full
  regression. Visual checks at 1920 x 1080 and 1366 x 768 confirmed that the
  Fields surface has a full chart followed by normal vertically scrollable
  lanes, all top-level navigation controls remain visible, and the live empty
  evidence state renders USD/JPY and pair as explicit gaps rather than an
  invented wave.
- Full packaging verification is complete in immutable founder-inspection
  candidate `0.10.37-pfr-v2b-r5-f1-r1`. It contains Fields source commit
  `95ede57ca1abcdd8986bea8a57fb2bb26b97d8d8` plus source commit
  `f748168df079c4322ec431ad64131dea0ab4a43a`, which fixes the previously
  discovered idle-sidecar recovery gap without altering doctrine, field values,
  scoring, market interpretation, execution behavior, or public API. The
  packaging checkout was `d779a23a3fb205df091e196a7cf3f7e393d04daa`, with
  `source_git_dirty=false`.
- Candidate location:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.37-pfr-v2b-r5-f1-r1`.
  Portable SHA-256:
  `A1203F2A48F29C36212F10BFE66671A6203EFB8E94B7938D17A5295E2D0DCC67`.
  Installer SHA-256:
  `FEDCCC43EE0D4AB004C1B40BA484339E933999D89074040D27B8B3604DEDC712`.
  The superseded `0.10.36-pfr-v2b-r5-f1` candidate remains an honest failed
  inspection candidate because it exposed that recovery gap.
- Verification: frontend lint passed; focused Fields tests **4 files / 36
  tests** passed; full frontend **34 files / 148 tests** passed; backend
  regression **184 tests** passed; production frontend build passed; `cargo fmt
  --check` and `cargo check --offline` passed; Rust tests **18 passed**.
  The exact portable candidate completed two independent recovery smokes. Each
  recovered an intentionally stopped idle sidecar on the same port, retained
  layout, kept all execution/MT5 locks false/read-only, and left no descendant
  processes after shutdown. The optional candlestick specialist remains the only
  explicit deferred check.
- Founder physical inspection remains pending. Required screenshots remain:
  1920 x 1080 Fields workspace, top-level Fields/Chakra hand-off, Trailokya
  geometry-only lane plus seven gaps, Phaladeepika independent SBC behavior,
  and 1366 x 768 responsiveness. No founder acceptance or stable promotion is
  claimed. A manual first launch of this new portable path displayed the normal
  Windows Firewall consent prompt. No public/private permission was granted by
  Codex; the prompt was dismissed, and any companion-network permission remains
  an explicit founder decision.
- Primary specification: `docs/fields/PFR_V2B_R5_F1_DEDICATED_FIELDS_WORKSPACE_AND_PAIR_RELATIVE_FIELD.md`.
  Machine-readable pair contract:
  `docs/fields/FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1.json`.
  Candidate record:
  `docs/fields/PFR_V2B_R5_F1_FOUNDER_INSPECTION_CANDIDATE_0.10.37.md`.

## Latest Update - 2026-08-05 (PFR-V2B-R4-T2P-U1 Founder Candidate)

- Implemented the bounded founder-visible layout correction in source commit
  `b014f2e7dc3b028e60d2bcf04d0fd18e83a82399`: the existing
  `IndependentFieldStack` is mounted directly in
  the left price-context column after the visible-aspect legend, rather than
  as a top-level panel outside the price/Chakra/audit body.
- The USD, JPY, and SBC lanes are expanded by default for a loaded chart range.
  The existing `Fields` control remains a local collapse/restore preference.
  Unknown side evidence remains visibly gapped, and Trailokya remains the
  explicit `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` availability state with no
  scored fallback.
- The workspace toolbar now spans its own full-width wrapping row. Previous
  candle, Time, Profile, Wheel, Phase lab, Compare, Fields, and next candle
  remain reachable and receive visible keyboard focus.
- Verification: Oxlint passed; full frontend `npm.cmd test` collected and
  passed **32 files / 139 tests**; focused product-first suite collected and
  passed **1 file / 7 tests**; `npm.cmd run build` passed; focused Python
  verification passed **41 tests**; full Python regression passed **657 tests
  with 1 explicit external-witness skip**; `cargo fmt --check`, `cargo check
  --offline`, and Rust tests passed (**18/18**). The exact candidate report is
  `docs/sbc/PFR_V2B_R4_T2P_U1_FOUNDER_INSPECTION_CANDIDATE_0.10.35.md`.
- Built immutable founder-inspection candidate
  `0.10.35-pfr-r4-t2p-u1` without changing `0.10.33-pfr-r4-t2r`. The
  portable and installer hashes are recorded in the candidate report and
  release manifest. Two exact portable smoke launches passed all **42/42**
  checks, with only the optional candlestick specialist deferred.
- Packaged UI inspection confirms the responsive toolbar, default-visible
  independent stack, USD/JPY unknown-gap lanes, and Trailokya's seven source
  gaps plus score-free geometry-only state through the native UI inspection
  tree. The required four-size DPI matrix, full lower SBC screenshot, and
  founder acceptance remain pending; no founder acceptance is claimed.

## Latest Update - 2026-08-03 (PFR-V2B-R4-T2P Founder-Inspection Windows Candidate)

- Built the non-promoted Windows research candidate `0.10.33-pfr-r4-t2r` from
  application source commit `1fc3853ea8268dba9c17e006e29b22f36dfa1afb` in a
  clean packaging checkout. The packaging checkout is
  `86bdcd0163c1a0c8b8cf25e5b615cccf4f044fa2`, and `origin/master` matches it.
  The accepted `0.10.32-pfr-u1-s1` candidate was not changed.
- Candidate folder:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.33-pfr-r4-t2r`.
  Final portable SHA-256 is
  `403494119C212EE4E81943EC89A9430220234DEE14DF6F5B74E8E8121A99591C`.
  Final NSIS SHA-256 is
  `5FD9B51D503E5B994AADADE3A1499C2BD74E277F3C945975A618EB41C5206684`.
- The first native smoke exposed a packaging-only missing
  `instrument_relative_sbc` import. The sidecar spec was corrected and pushed
  as `86bdcd0`; no application doctrine or behavior was changed.
- Verification: Oxlint passed; complete frontend **32 files / 137 tests**
  passed; focused T2R frontend **4 files / 39 tests** passed in single-thread
  mode; focused Python **44 passed**; full Python **656 passed / 1 skipped**;
  `cargo fmt --check` passed; `cargo check --offline` passed; Rust **18
  passed**; status unit tests **55 passed**; status validator valid with
  `executionAllowed=false`.
- The exact final portable candidate was smoke-launched twice. Each run had
  **42/42 checks true**, no errors, and verified health, chart/Chakra
  endpoints, read-only behavior, execution locks, sidecar restart/recovery,
  layout survival and cleanup. Both are conditional only because the optional
  candlestick specialist is not configured.
- Packaged UI founder inspection remains pending. The checklist is in
  `docs/sbc/PFR_V2B_R4_T2P_REPRODUCIBLE_FOUNDER_INSPECTION_WINDOWS_CANDIDATE.md`.
  No stable promotion, Auto Suggest, order placement, execution, polarity,
  magnitude, Trailokya score/wave, price conversion or natural-planet
  promotion was enabled.

## Latest Update - 2026-08-03 (PFR-V2B-R4-T2R Source-Only Geometry Integration Hardening)

- Corrected the synchronized Trailokya path so it cannot invoke the ordinary
  scored ChakraLab atomic-range compiler or silently substitute Phaladeepika or
  another scored Vedha profile. The SBC lane now returns the explicit,
  non-error state `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED`, with zero intervals,
  zero score, named source gaps, and all locks false. USD and JPY synchronized
  fields still compile independently for the same visible range.
- Trailokya ray reach is now tri-state aware: `REACHED`, `NOT_REACHED`,
  `UNKNOWN`, and `PARTIAL_UNKNOWN`. Unknown mappings cannot be summarized as a
  negative reach. The source-only UI again shows the seven active doctrine and
  compiler gaps and retains `classicalCompletenessClaim: false`.
- Founder-visible synchronized requests now use the accepted R3 USD and JPY
  chart/hypothesis IDs instead of `UNCONFIGURED_*` / `PENDING_FOUNDER_REVIEW`.
  This only wires existing registry identity; it creates no polarity events or
  derived pair state.
- Verification reconciliation: the original R4-T2 frontend handoff recorded
  **34** tests; the later R4-T2 check collected **35** after its final test was
  added. The current exact T2R frontend command collected and passed **39**:
  `npm test -- --run src/api.test.ts src/chakraLabWorkspace.test.tsx
  src/visualizationModes.test.ts src/visualizationSourceGaps.test.ts`.
  Focused Python verification collected and passed **44** tests; production
  frontend build, native `cargo fmt --check`, and native `cargo check` passed.
  No installer was produced because packaging remains locked. Full evidence and
  physical UI checklist: `docs/sbc/PFR_V2B_R4_T2R_SOURCE_ONLY_GEOMETRY_INTEGRATION_HARDENING.md`.

## Latest Update - 2026-08-03 (PFR-V2B-R4-T2 Narrow Trailokya Source-Only Geometry)

- Founder-approved only three Trailokya 1972 variables, each as
  `APPROVED_FOR_SOURCE_ONLY_WITH_LIMITS`: variable Mars-to-Saturn direction,
  Sun/Moon/Rahu/Ketu all-three rays, and ray extent. The immutable decision
  record is `configs/sbc/approved_profiles/sbc_trailokya_1972_source_only_geometry_v1.yaml`.
  Natural-planet class and isolated result factors remain pending.
- Added the separate `sbc.trailokya_source_only_geometry` engine and the
  backend/native endpoint `chakra_lab_trailokya_source_only_geometry`. It never
  instantiates the older scored `VedhaGuidanceEngine`; it returns only
  figure-relative rays, categorical target reach, provenance, and unavailable
  states. Missing motion or missing/disputed mapping fails closed.
- Chakra Board now explicitly selects the Trailokya profile and renders its
  source-only rays/reached cells with a page-cited audit view. Exports include
  the selected approval record, rays, unavailable items, and false locks.
  No wave, polarity, USD/JPY support, pair direction, magnitude, score, price,
  confidence, Auto Suggest, execution, or packaging behavior changed. Mode 2
  and existing named profiles remain separate.
- Verification: `pytest -q test_classical_oscillator_coverage.py
  test_trailokya_dipika_vedha_page_certification.py
  test_trailokya_source_only_geometry.py
  gann-astro-desk/backend/test_chakra_lab_service.py` passed **40** tests;
  focused frontend suite passed **34** tests; production frontend build and
  native `cargo check` passed. No installer was produced because packaging
  remains locked. Details: `docs/sbc/PFR_V2B_R4_T2_NARROW_TRAILOKYA_SOURCE_ONLY_GEOMETRY.md`.

## Latest Update - 2026-08-03 (PFR-V2B-R4-T1 Trailokya Vedha Page Packet)

- Founder selected the held `SBC_TRAILOKYA_1972_V1` profile. Added the bounded
  `PFR-V2B-R4-T1` source packet at
  `configs/sbc/evidence_packets/trailokya_dipika_1972_vedha_page_certification_v1.yaml`,
  citing only the checksum-identified original 1972 Trailokya Dipika scan
  (`1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`).
  The OCR companion is navigation and draft-translation help only; it is not
  citation authority.
- The packet page-certifies five narrow founder-review candidates: variable
  Mars-to-Saturn direction selection, Sun/Moon/Rahu/Ketu all-three direction,
  side/front ray reach, base natural planet class, and isolated source-result
  factors (retrograde `2x`, exalted `3x`, debilitated `0.5x`, swift `1x`).
  The practical identity-placement procedure is recorded separately as display
  and manual research only because no complete source-specific machine fixture
  is admitted.
- No variable was promoted. Every candidate is `PENDING` founder review for
  at most `APPROVED_FOR_SOURCE_ONLY_WITH_LIMITS`; all global locks remain
  false. No price data, outcome selection, wave tuning, LLM gap filling,
  polarity catalogue, oscillator derivation, Auto Suggest, execution, or
  packaging changed.
- The numeric swift-versus-mean boundary, modifier stacking, automatic Mercury
  association, Moon boundary, Latta/additional lines, absolute orientation,
  Arghya disputed values, score/price conversion, and market direction remain
  explicitly unresolved and outside Mode 1. The full founder form and plain
  limits are in `docs/sbc/PFR_V2B_R4_T1_TRAILOKYA_VEDHA_PAGE_CERTIFICATION.md`.
- Verification wording is exact: `pytest -q
  test_classical_oscillator_coverage.py
  test_trailokya_dipika_vedha_page_certification.py` collected and passed
  **8** tests: four pre-existing R4 coverage tests plus four new source-packet
  tests. This does not replace the earlier R4-only command, which correctly
  remains `pytest -q test_classical_oscillator_coverage.py` with **4** tests.

## Latest Update - 2026-08-03 (PFR-V2B-R3 Founder Chart Admission)

- Founder accepted two exact-time **research hypotheses**, explicitly not
  universally certified historical facts: USD/United States Independence in
  Philadelphia at `1776-07-04 12:00 America/New_York`, and JPY/Yen IPO Tokyo at
  `1889-02-11 00:00 Asia/Tokyo`. Their deterministic IDs, historical local-to-
  UTC conversions, contracts, chart hashes, provenance, and founder acceptance
  records live in
  `research_labs/chart_conditioned_aspects/profiles/founder_chart_hypotheses_v1.json`.
- The conversion policy uses historical IANA `zoneinfo` offsets, not a present
  day fixed offset: the USD record resolves to `1776-07-04T16:56:02Z` from
  `-04:56:02`; JPY resolves to `1889-02-10T15:00:00Z` from `+09:00:00`.
  Exact-time status makes house/Ascendant calculation technically possible,
  but functional lordship remains source-blocked under R4.
- The loader is explicit and inert: it validates chart hashes but never
  registers/selects a chart automatically, creates no polarity/evidence
  catalogue record, derives no pair oscillator, and changes no execution,
  Auto Suggest, LLM, price, or package behavior. Details:
  `docs/sbc/PFR_V2B_R3_FOUNDER_CHART_ADMISSION.md`.

## Latest Update - 2026-08-03 (PFR-V2B-R4 Classical Coverage and Mode Promotion Audit)

- Completed the R4 read-only doctrine and mode audit. Added one authoritative
  42-variable coverage ledger across SBC topology, Vedha, financial SBC,
  chart-conditioned doctrine, Shadbala/Drik, Panchanga/Muhurta,
  Ashtakavarga, timing kernels, and display/fitted values. Its machine-readable
  source is `configs/research/classical_oscillator_coverage_matrix_v1.yaml`.
- The smallest truthful `SOURCE_ONLY_BASELINE` remains **empty**: its existing
  profile has founder approval pending and zero admitted parameters. Selected
  page-supported Vedha direction/nature/isolated modifier rules are listed as
  possible future Mode 1 candidates, but remain dependency-blocked until an
  exact packet and founder approval exist.
- No source was promoted and no product calculation, chart hypothesis,
  polarity registry, price label, wave tuning, LLM/Auto Suggest path, execution
  path, order path, or package changed. Full Shadbala, Drik, Ashtakavarga wave
  magnitude, Arghya conversion, financial mapping, fitted weights and smooth
  timing kernels remain outside Mode 1.
- Added the source acquisition plan, profile-boundary rules, Mode 2-to-Mode 1
  promotion checklist, machine status summary, and `test_classical_oscillator_coverage.py`.
  The coverage test validates uniqueness, required fields, forbidden Mode 1
  allocations, status counts, and all execution/promotion locks.
- Verification wording reconciled: `pytest -q
  test_classical_oscillator_coverage.py` collected and passed **4** R4-only
  tests. `pytest -q test_classical_oscillator_coverage.py
  sbc/test_visualization_modes.py` collected and passed **8** tests: those four
  plus four pre-existing visualization-mode contract tests. Next: founder selects one narrow acquisition/page-certification
  priority; do not move to R3 chart evidence admission until that independent
  founder chart selection has occurred.

## Latest Update - 2026-08-02 (PFR-V2B-R2 Shared Time Controller)

- Completed the next bounded founder-visible navigation layer. The price chart,
  Chakra workspace, and independent USD, JPY, and SBC field stack now carry a
  single explicit `RESEARCH_TIME_CONTROLLER_V1` state: visible UTC range,
  crosshair timestamp, selected timestamp/candle, canonical selected interval
  ids, source, and sequence number.
- Price hover updates the shared cursor; a click selects the nearest actual
  candle. Selecting an exact stored field interval (including an unknown gap)
  selects its canonical `startUtc`, highlights it, and moves the Chakra review
  moment to the same instant. No timestamp is inferred from a reduced SVG
  display point and no interval is stretched or resampled.
- USD/JPY panels show a shared cursor line. SBC remains an independent
  availability field, not aspect confirmation. This is research navigation
  only: no pair direction, evidence admission, numerical magnitude, fusion,
  smoothing, ML, Auto Suggest, live inference, MT5 execution, or order path
  was added.
- Verification: Oxlint clean; focused Chakra/field suite `2 files / 24 tests`
  passed; TypeScript/Vite production build passed. Details:
  `docs/sbc/PFR_V2B_R2_SHARED_TIME_CONTROLLER.md`.
- Next bounded work: R3 can derive a pair categorical range only after genuine
  independently accepted USD and JPY side evidence exists. No installer is
  produced before that evidence prerequisite.

## Latest Update - 2026-08-02 (PFR-V2B-R1 Live Range and Stepped Fields)

- Completed the first founder-visible oscillator product layer without
  manufacturing evidence. Chakra no longer builds its independent field request
  from a fixed trailing `slice(-110)`. It now consumes the settled UTC visible
  range already persisted by the price chart after a debounced pan or zoom.
- The Chakra workspace automatically refreshes its synchronized USD, JPY, and
  independent SBC range after a 240 ms settle window. A sequence guard discards
  any response from an older viewport, so a slow request cannot overwrite a
  newer chart range. `Refresh now` remains only as an explicit retry action.
- The Fields surface now renders USD and JPY as categorical stepped panels:
  supportive above zero, adverse below zero, explicitly reviewed neutral on
  zero, mixed as separate positive/negative dashed activity, and unknown as a
  patterned broken gap. Each panel is labelled `MAGNITUDE_NOT_CONFIGURED`.
  SBC remains an independent availability timeline, never a polarity scale or
  automatic confirmation.
- Verification: Oxlint clean; frontend `32 files / 133 tests`; TypeScript/Vite
  production build passed. Details:
  `docs/sbc/PFR_V2B_R1_LIVE_RANGE_AND_STEPPED_FIELDS.md`.
- Next bounded work: PFR-V2B-R2, establish shared crosshair/selected-interval
  synchronization between the price chart, fields, Chakra, and Why drawer.
  Derived USDJPY polarity and founder evidence admission remain separate later
  milestones. No package is created at this stage.

## Latest Update - 2026-08-02 (PFR-V2B-R0 Remote Reconciliation)

- Completed the required remote-source reconciliation before beginning any new
  V2B product layer. Local branch `pfr-v2b-categorical-oscillator` and
  `origin/master` both resolve to
  `9677b1bb7c8b8b0c040c88c4d1442c56196e04c2`
  (`Expose FX side pilot evidence readiness`). The V2B branch name itself is
  local-only, but its bounded implementation is deliberately published on
  `master`; there is no unpushed V2B source dependency.
- A fresh remote clone at
  `D:\GannAstroDesk-Reconciliation-20260802-R0` checked out the same SHA with
  a clean worktree. It contains V2B-5 at `86c652e` and V2B-6 at `9677b1b`.
- Clean-clone verification passed: Oxlint; TypeScript/Vite build; frontend
  `32 files / 132 tests`; backend `181 tests`; Rust `cargo fmt --check`,
  `cargo check`, and `18 tests`. The Vite warning about a >500 kB JavaScript
  chunk remains a performance observation, not a correctness failure.
- Source manifest and full result:
  `docs/sbc/PFR_V2B_R0_REPOSITORY_RECONCILIATION.md`. Production evidence
  registries remain empty, `PILOT_EVIDENCE_PENDING`, and every execution,
  magnitude, smoothing, calibration, fusion, ML, Auto Suggest, and trading
  lock remains in force.
- Next bounded work: PFR-V2B-R1, replace the manual last-110-candle field
  request with a live chart-range controller and honest stepped visual panes.
  Do not package a V2B candidate or admit polarity evidence before the later
  explicit founder-review gate.

## Latest Update - 2026-08-02 (PFR-V2B-6 FX Side Pilot Readiness)

- Completed V2B-6 as a read-only status surface, not a fictional evidence
  admission. `FX_SIDE_POLARITY_PILOT_STATUS_V1` reads the existing immutable
  USD/JPY packet registry and matching catalogue, then reports required
  supportive/adverse state coverage, blockers, and retained unknown gaps.
- The Chakra `Fields` panel now shows **FX side pilot status** through the
  private Rust bridge. Current production status is correctly
  `PILOT_EVIDENCE_PENDING`: both side registries are empty, so no USDJPY
  direction or other conclusion is introduced.
- Verification: backend `36 passed`, focused desktop tests `14 passed`,
  production build and Rust `cargo check` passed. Details:
  `docs/sbc/PFR_V2B_6_FX_SIDE_PILOT_READINESS.md`. Next: V2B-7 only after a
  genuine founder-reviewed side pilot is supplied; do not package an evidence
  claim before that prerequisite exists.

## Latest Update - 2026-08-02 (PFR-V2B-5 Founder-Visible Independent Field Stack)

- Completed V2B-5 on `pfr-v2b-categorical-oscillator`. The Chakra workspace
  now has a `Fields` control that renders USD categorical side context, JPY
  categorical side context, and SBC atomic availability as three compact,
  synchronized, independent lanes for the displayed chart range.
- The range flows through the private desktop Rust bridge to the strict shared
  range coordinator. USD and JPY correctly remain `UNKNOWN` until accepted
  immutable side-chart evidence exists; pair-chart events are not copied into
  either primary side lane. SBC is availability only and never an automatic
  confirmation.
- Verification: focused desktop tests `13 passed`; production build, Rust
  `cargo check`, Python compile, and backend aspect/SBC/coordinator regression
  suite `33 passed`. Details: `docs/sbc/PFR_V2B_5_FOUNDER_VISIBLE_STACK.md`.
  Next: V2B-6, a small founder-reviewed side-level evidence pilot. No package
  was created in this bounded UI milestone.

## Latest Update - 2026-08-02 (PFR-V2B-4 Shared Range Coordinator)

- Completed V2B-4 on `pfr-v2b-categorical-oscillator`. Added the private
  `SYNCHRONIZED_INDEPENDENT_RANGE_V1` coordinator and
  `/api/independent-fields/synchronized-range` route. It gives the USD side,
  JPY side, and SBC fields one exact offset-aware visible time range.
- The coordinator rejects a late/mismatched SBC boundary or field range rather
  than bending a range to look synchronized. It packages independent outputs
  only; `fieldsFused=false`, no market direction is inferred, and all
  execution locks remain unchanged.
- Verification: categorical aspect, SBC, and coordinator regression suite
  `33 passed`; Python compile and whitespace checks passed. No UI or installer
  was built in this bounded coordination step. Next: V2B-5, render the three
  independent synchronized fields in the founder-visible chart stack.

## Latest Update - 2026-08-02 (PFR-V2B-3 SBC Atomic Visible Range)

- Completed V2B-3 on `pfr-v2b-categorical-oscillator`. Added the private,
  read-only `SBC_ATOMIC_VISIBLE_RANGE_V1` contract and
  `/api/chakra-lab/atomic-range` route. It surfaces the existing SBC atomic
  ledger as timestamp-safe intervals with their source lineage, evidence
  cutoff, availability state, and unchanged ledger summary.
- It is explicitly an independent synchronized comparison field, not aspect
  confirmation: `aspect_relationship=NOT_AUTOMATIC_CONFIRMATION` and
  `magnitude_state=NOT_CONFIGURED`. No aspect compiler call, market-direction
  inference, Auto Suggest, live inference, or execution behavior was added.
- Verification: full Chakra Lab service suite `26 passed`, Python compile and
  a direct contract smoke check passed. No UI panel or installer in this
  bounded backend step. Next bounded item: V2B-4, synchronize the two fields
  to a shared visible range while keeping them independent.

## Latest Update - 2026-08-02 (PFR-V2B-2 Categorical Visible Range)

- Completed V2B-2 on branch `pfr-v2b-categorical-oscillator`. Added the
  private, research-only `CHART_CONDITIONED_CATEGORICAL_RANGE_V1` compiler and
  `/api/chart-conditioned-polarity/range` route. It creates contiguous atomic
  side-chart intervals across a supplied UTC range.
- The compiler shows `SUPPORTIVE`, `ADVERSE`, `NEUTRAL`, `MIXED`, or explicit
  `UNKNOWN` gaps. Any active event lacking accepted immutable evidence makes
  that segment unknown, so known events never conceal missing evidence.
- Tightened the V2B-1 primary identity contract: `chartHypothesisId` is now
  required in the event-level lookup key as well as the stored record. This is
  a context-correctness repair, not new market logic.
- Verification: catalogue/range `9 passed`, backend `5 passed`, focused
  desktop/API suites `29 passed` when run individually, lint/build passed.
  No UI range panel or installer yet. Next bounded item is V2B-3: expose SBC
  atomic intervals via a separate read-only range contract, with no fusion.

## Latest Update - 2026-08-02 (PFR-V2B-1 Independent FX Side Contracts)

- Completed the V2B-1 correction on branch `pfr-v2b-categorical-oscillator`.
  `FX_CURRENCY:USD` and `FX_CURRENCY:JPY` are now independent primary
  research identities. `FX_PAIR:USDJPY` explicitly returns
  `PAIR_DERIVATION_ONLY`, so it can never act as a silent primary catalogue
  lookup.
- Future immutable packet/catalogue records now require a matching
  `sideIdentity` and `chartHypothesisId`. Both real registries remain empty,
  so the application correctly remains fail-closed with no polarity invented.
- The desktop aspect-pressure panel shows USD and JPY independently and offers
  two non-admissible candidate worksheets. Defaults are `PENDING_REVIEW` and
  `PENDING_FOUNDER_REVIEW`; pair event details remain review scope only and
  are not copied into a side chart's natal target.
- Verification: polarity tests `7 passed`, backend `4 passed`, focused desktop
  tests `21 passed`, API `8 passed`, lint/build passed. No installer was built
  because this is a research identity/UI correction only. Next bounded item:
  V2B-2 visible-range categorical aspect intervals, still with no magnitude,
  fusion, or execution behavior.

## Latest Update - 2026-08-02 (PFR-V2B-0 Baseline and Freeze)

- Founder physically confirmed the targeted `0.10.32-pfr-u1-s1` wheel-zoom
  repair: aspect lanes and Live SR lines remained visible through repeated
  zoom. The U1-S1 targeted check is now recorded as passed in
  `docs/sbc/PFR_U1_FOUNDER_ACCEPTANCE.md`.
- Opened the dedicated `pfr-v2b-categorical-oscillator` branch. V2A is frozen
  at `b022b20`: the catalogue and packet registry remain empty, candidate
  worksheets remain non-admissible, and every research/execution guardrail
  remains in force.
- The V2B sequence is recorded in `docs/sbc/PFR_V2B_ACCEPTANCE_REPORT.md`.
  The next bounded code change is V2B-1: independent USD and JPY side
  identities plus pending-review candidate defaults. No range oscillator,
  polarity, magnitude, fusion, ML, Auto Suggest, live inference, or execution
  was added in V2B-0.

## Latest Update - 2026-08-02 (PFR-V2A-3 Candidate Evidence-Packet Preparation)

- Added a read-only **Evidence packet readiness** surface to the desktop
  chart-conditioned aspect panel. When a chart aspect is selected and the
  immutable polarity lookup is not `READY`, it shows the exact selected
  transit/natal/aspect identity and offers a local JSON candidate worksheet.
- The worksheet carries the same `FX:USDJPY` identity convention as the
  immutable lookup and is deliberately marked `CANDIDATE_NOT_ADMISSIBLE`.
  It cannot write either the packet registry or polarity catalogue, and it
  supplies no polarity, magnitude, signal, ML evidence, Auto Suggest input,
  live inference change, or execution behavior.
- The founder must still fill an accepted chart id, reviewed categorical state,
  profile hash, reviewer/timestamp, source references, and deterministic
  packet hash before a later reviewed change can admit matching packet and
  catalogue entries. `TARGET_CONTEXT_INCOMPLETE` without an accepted chart is
  expected and remains fail-closed.
- Details: `docs/sbc/PFR_V2A_3_CANDIDATE_PACKET_PREPARATION.md`. Verification:
  focused desktop tests `29 passed`, catalogue tests `5 passed`, backend lookup
  tests `3 passed`, lint and production frontend build passed. No installer was
  built for this small research-only interface step.

## Latest Update - 2026-08-02 (PFR-V2A-2 Evidence Packet Admission)

- Hardened the V2A polarity catalogue with the separate, immutable
  `CHART_CONDITIONED_POLARITY_EVIDENCE_PACKET_REGISTRY_V1`. The production
  registry intentionally contains no packets, so current USDJPY continues to
  show `POLARITY_CATALOGUE_MISSING`.
- A future catalogue entry must now match its reviewed packet exactly:
  instrument/chart/transit/natal target/aspect identity, categorical polarity,
  evidence status, profile hash, packet id/hash, accepted chart status,
  astronomy contract, source references, reviewer, and offset-aware timestamp.
  Any mismatch fails closed during catalogue load.
- This is a provenance control only, not validation of market success or a new
  prediction engine. SBC remains an independent synchronized comparison field;
  execution locks remain unchanged. Details:
  `docs/sbc/PFR_V2A_2_EVIDENCE_PACKET_ADMISSION.md`.

## Latest Update - 2026-08-02 (PFR-V2A-1 Immutable Polarity Lookup)

- Founder approved V2A-1 after the narrow V2-0 inventory. Added the read-only
  `CHART_CONDITIONED_POLARITY_CATALOGUE_V1` seed and its desktop/backend
  lookup. The catalogue is intentionally empty: current USDJPY shows
  `POLARITY_CATALOGUE_MISSING` rather than fabricated bullish/bearish output.
- Partial event identity returns `TARGET_CONTEXT_INCOMPLETE`; a future ready
  entry must match the instrument, accepted chart, transit body, natal target,
  and aspect type and carry an explicit reviewed evidence packet/hash.
- The new **Chart-conditioned aspect pressure** panel is an independent
  synchronized comparison field. It explicitly states
  `CATEGORICAL_POLARITY_STATE / MAGNITUDE_NOT_CONFIGURED`; it never treats SBC
  agreement as confirmation and cannot affect Auto Suggest, ML, live
  inference, shadow validation, or MT5 execution.
- Key documents: `docs/sbc/PFR_V2_0_INVENTORY.md` and
  `docs/sbc/PFR_V2A_1_IMMUTABLE_POLARITY_LOOKUP.md`.
- Verification: target-aware catalogue tests `4 passed`; backend lookup tests
  `3 passed`; focused desktop tests `25 passed`; lint and production frontend
  build passed. No installer was built in this small research-only milestone.

## Latest Update - 2026-08-02 (PFR-V2-0 Focused Inventory)

- Founder authorized the post-U1 PFR-V2 inventory only. Created branch
  `product-first-sbc-oscillator-v2`; no oscillator, polarity, calibration,
  source, doctrine, execution, or product feature was added in this gate.
- Inventory result is recorded in `docs/sbc/PFR_V2_0_INVENTORY.md`. The repo
  has a sound independent SBC atomic interval/ledger foundation and a
  chart-conditioned aspect research framework, but no usable immutable
  target-aware polarity catalogue for a selected production instrument.
- The existing aspect prior knows the natal target as explanatory context but
  deliberately refuses target-domain-to-price polarity. It must not be reused
  as a hidden universal or transit-only market sign. Absent an accepted static
  catalogue entry, future V2 display must show
  `UNKNOWN / POLARITY_CATALOGUE_MISSING` or `TARGET_CONTEXT_INCOMPLETE`.
- Aspect magnitude is not configured. If a future accepted target-aware static
  polarity exists without magnitude, the permitted visual fallback is the
  categorical stepped state
  `CATEGORICAL_POLARITY_STATE / MAGNITUDE_NOT_CONFIGURED`: supportive above
  zero, adverse below zero, neutral at zero, mixed split into both components,
  unknown as a gap. This is descriptive research display only.
- SBC remains a separate synchronized comparison field, never automatic
  confirmation. No fusion, calibration, curve fitting, execution influence,
  Auto Suggest, official ML, live inference promotion, or trading was added.
- Verification: chart-conditioned/SBC foundation `41 passed`; focused desktop
  Chakra/API tests `25 passed`. Next gate is V2A-1 only after founder approval:
  a narrow immutable lookup and missing-state surface which reuses existing
  identities and never invents polarity.

## Latest Update - 2026-08-02 (PFR-U1 Founder Acceptance and Observation)

- Read and adopted `PFR_U1_Founder_Acceptance_Product_Observation_and_Usability_Codex_Directive.pdf`.
  `0.10.31-pfr-c2f` is now frozen for founder physical acceptance: no rebuild,
  code change, tuning, source admission, calibration, event-link work, ML,
  Auto Suggest, trading, or execution work is permitted during this milestone.
- Preflight at `2026-08-02 06:11 IST` confirmed the exact C2F artifact hashes
  still match the release record. The candidate source remains
  `b8ae06fa775b152e4782157e44c9b8be47676c82`; current repository `HEAD` is
  `4d56615cbb6576a9e6a000a7fc6862aef48fd952`. Founder acceptance is still
  `PENDING` and must be recorded as `ACCEPTED`, `ACCEPTED_WITH_DEFECTS`, or
  `REJECTED` after the physical checklist is completed.
- Added the only U1 working materials permitted before acceptance:
  `docs/sbc/PFR_U1_FOUNDER_ACCEPTANCE.md` and
  `docs/sbc/PFR_U1_OBSERVATION_LOG_TEMPLATE.csv`. Use the exact portable in
  `D:\\PycharmProjects\\releases\\GannAstroDesk-0.10.31-pfr-c2f\\`.
  After acceptance, log at least five no-tuning research sessions; Codex may
  summarize them into one bounded usability backlog but must not code until
  the founder explicitly approves that scope.
- The directive also flags repository visibility: the GitHub recovery repo is
  described as private by its README but is reportedly public. Restore private
  visibility before continuing unless public disclosure is an explicit decision.
- Founder-reported acceptance defect `U1-S1-001`: mouse-wheel zoom can remove
  all visible aspect lanes and Live SR planetary lines while candlesticks remain.
  The approved bounded hotfix clips active aspect windows to the visible
  viewport and retains sparse whole-chart anchors during the Live SR viewport
  refresh. The original `0.10.31-pfr-c2f` candidate remains untouched. Source
  validation is green (`32` frontend test files / `127` tests and lint).
- Built the separate U1-S1 hotfix candidate without replacing the frozen C2F
  release: `D:\PycharmProjects\releases\GannAstroDesk-0.10.32-pfr-u1-s1\`.
  It is sourced from `5d61fd42739603ec5e05c4e4e0d7e7a15127c557` and its manifest
  records `source_git_dirty=false`. Portable SHA-256:
  `91DAF5C9011A6A064BD5E688114EFCA47E71582ED08BE134BB369E9406F881BF`;
  installer SHA-256:
  `6B8944BE06D6F07786C2755638B0C289043B5CA5790A8323A519777C34C124D1`.
  Its isolated native soak passed, including backend health, restart recovery,
  chart contracts, and all execution locks. The only open U1-S1 check is the
  founder's physical wheel-zoom confirmation that aspect lanes and enabled
  Live SR lines remain visible during rapid zoom.

## Latest Update - 2026-08-01 (PFR-C2F Reproducible Founder Candidate)

- Completed the bounded C2F implementation without adding product scope.
  Current status is `PFR_C2_STATUS = IMPLEMENTATION_RECONCILED`,
  `FOUNDER_ACCEPTANCE_READY = true`, and
  `CANDIDATE_SOURCE_REPRODUCIBLE = true`. This means the candidate is ready
  for founder inspection; it does not mean founder acceptance was performed.
- Exact package source is clean commit
  `b8ae06fa775b152e4782157e44c9b8be47676c82`. The release is
  `0.10.31-pfr-c2f`, archived at
  `D:\\PycharmProjects\\releases\\GannAstroDesk-0.10.31-pfr-c2f\\`.
  Its manifest records `source_git_dirty=false`, `npm@11.12.1`, execution
  disabled, `UNLINKED_EVENT_GEOMETRY`, and market direction `ABSTAIN`.
- Reproducibility fixes: the tracked `package-lock.json` plus `npm ci` are now
  canonical; JHora parser fixtures are tracked and byte-preserved; the external
  witness test cleanly skips with `SKIPPED_WITH_REASON` until an explicit local
  path is supplied; private Jyotish and candlestick packs are optional rather
  than hidden package requirements.
- Clean-worktree verification passed: frontend lint/build, 31 Vitest files / 123
  tests, SBC Python 9 tests, full Python 616 passed / 1 expected external-witness
  skip, Rust fmt/check, and 18 Rust tests.
- The exact portable candidate was built and smoke-launched twice. Both launches
  passed all checks, recovered a controlled sidecar restart, preserved a saved
  layout, left no child process behind, and stayed read-only/execution-locked.
  Each records the intentional optional-candlestick deferral:
  `D:\\GannFinancialAstro\\soak\\tauri_0.10.31_20260801_182710\\logs\\native_soak_report.json`
  and
  `D:\\GannFinancialAstro\\soak\\tauri_0.10.31_20260801_182824\\logs\\native_soak_report.json`.
- Next and only C2F action: founder physical inspection of the portable
  `GannAstroDesk.exe`, including chart pan/zoom, visible read-only state, and
  the explicit optional-specialist unavailable state. Do not resume research or
  add features under this directive. Full evidence is in
  `docs/sbc/PFR_C2R_RECONCILIATION_REPORT.md`.

## Latest Update - 2026-08-01 (PFR-C2 Founder Acceptance and Visualization Integrity)

- Implemented PFR-C2 on `product-first-sbc-phase-lab` without expanding the
  requested scope. `SOURCE_ONLY_BASELINE` is now visibly named
  **Source-profiled partial baseline** and carries
  `SOURCE_PROFILED_PARTIAL` plus `FOUNDER_APPROVAL_PENDING` until
  `SBC_BASELINE_PROFILE_APPROVAL` is resolved. No founder-approved classical
  completeness claim is made.
- Closed the score-suppression boundary in the product panel, fixed wheel,
  comparison, Why drawer, linked audit, bookmark metadata, manifest export,
  and mode/profile/footer status. Score-suppressed modes retain identity and
  fixed 0/pi geometry but no scalar magnitude, percentage, polarity, or
  aggregate visual encoding.
- Replaced `PROJECT_CONVENTION_TIMING_PHASE_V0` with V1: applying and
  separating spans normalize independently around explicit exact tolerance;
  invalid zero-length windows fail closed. A missing
  `EVENT_CONTRIBUTION_LINK_PROFILE_MISSING` now quarantines every timing
  aggregate, preventing the previous contribution-by-event Cartesian
  expansion. Per-event lifecycle geometry remains descriptive only; market
  result stays ABSTAIN and execution stays locked.
- Added always-visible previous/next candle controls and Left/Right keyboard
  stepping from the one focusable price-chart SVG.
- Validation: `pnpm lint`, production build, full Vitest run
  (`30` files / `121` tests), `python -m pytest -q sbc` (`9` tests), and
  `cargo check --offline` passed. Rust test discovery found 18 tests and a
  representative native test passed; the complete native suite exceeded the
  shell time allowance after compile, so it is not claimed as a full pass.
- Built and smoke-tested `0.10.29` at
  `D:\PycharmProjects\releases\GannAstroDesk-0.10.29-pfr-c2\`.
  Installer SHA-256:
  `86ED85F7B28244345D08956ADB86F159F2D1F55FB3A7904E0E4217F1B516FD1C`.
  Portable SHA-256:
  `00FC365FA81D017379194BD516F74B79DF3AE2F740532FFAA2B2B7AA9F1CCD1F`.
  The native smoke report passed with only the expected closed-market MT5
  normalization deferral. Founder physical acceptance remains the next and
  final C2 checkpoint; see `docs/sbc/PFR_C2_ACCEPTANCE_REPORT.md`.

## Latest Update - 2026-08-01 (PFR-C1 Product Integrity Correction)

## Latest Update - 2026-08-01 (PFR-C1 Acceptance Record Reconciled)

- Corrected an internal status contradiction: the consolidated PFR-C1 report
  had still listed C1-7 as pending even though the corrected `0.10.28`
  candidate had been built, tested, smoke-launched, and pushed. It now records
  those facts accurately and names founder inspection as the sole remaining
  acceptance action.
- This is documentation-only. It changes no calculation, visualization mode,
  source profile, inference path, ML evidence, execution lock, or packaged
  binary. The exact founder checkpoint remains: inspect `0.10.28`, change
  modes, synchronize a selected time across the workspace, and export state.

## Latest Update - 2026-08-01 (Three-Mode Visualization Engine Candidate)

## Latest Update - 2026-08-01 (Three-Mode Boundary Correction)

- Completion audit found a genuine display leak in the first candidate: the
  detailed audit, comparison, and “why” surfaces could still expose scalar
  units or direction after selecting a score-suppressed mode. This is now
  corrected. `CALIBRATED_RESEARCH` and `VISUAL_ONLY_NO_SCORE` cannot open the
  scalar audit/package surface; they show an explicit source/status panel
  instead. Product comparison, fixed vectors, timing values, and Vedha detail
  also mask scalar values whenever the active profile withholds scores.
- Scalar audit is now an explicit mode policy capability, true only for
  `SOURCE_ONLY_BASELINE`. Audit bookmarks stamp their source mode and evidence
  state. A persistent workspace footer provides the active mode/status for
  screenshots, and exported state already contains the same immutable fields.
- Rebuilding as `0.10.28` so the corrected candidate is distinct from the
  earlier `0.10.27` build. Validation before package rebuild: frontend lint,
  focused frontend tests (7), frontend production build, and SBC Python tests
  (6) passed.
- Corrected Windows candidate built and smoke-tested at
  `D:\PycharmProjects\releases\GannAstroDesk-0.10.28-three-mode-boundary\`.
  Installer SHA-256:
  `3496BAA4E76A255E342D4136122989CD2BC39A794B4FEB61A41DD345AFE8243A`.
  Portable launcher SHA-256:
  `E5417582ADCFFC2E87D2A6317522B87514CB28DDA67FCD62DC936463FA055C9D`.
  The portable `Gann Astro Desk.exe` and its adjacent `GannAstroBackend` both
  launched successfully from that exact release folder.

- Implemented the founder-visible visualization engine modes requested by the
  `Gann_Astro_Desk_Visualization_Engine_Three_Mode_Codex_Addendum`:
  `SOURCE_ONLY_BASELINE`, `CALIBRATED_RESEARCH`, and
  `VISUAL_ONLY_NO_SCORE`. The selected mode persists locally and is shown in
  the main Chakra workspace, product panel, audit panel, and exported state
  manifest.
- Source-only baseline retains only the existing source-profiled ledger and
  fixed 0/pi representation. Timing geometry is unavailable in this mode.
  Calibrated research has no fitted parameter profile loaded and therefore
  visibly reports `SOURCE_MISSING`, with score values withheld. Visual-only
  shows chart/geometry context without scores or direction labels.
- Added an explicit source-gap register rather than inserting invented
  doctrine, calibration values, or authority. The exported JSON manifest
  includes the active mode, profile state, source gaps, snapshot/cutoff,
  request, and absolute non-execution locks.
- Added matching deterministic Python mode contracts and focused tests. All
  modes remain experimental, non-financially-validated, non-execution, and
  incapable of automatic order placement.
- Validation before native packaging: frontend lint passed; focused mode tests
  passed; production frontend build passed; `python -m pytest -q sbc` passed
  (5 tests). A broad Vitest run recorded 100 passing tests but also two worker
  startup timeouts, so it is not counted as a clean all-suite certification.
- Windows candidate built and smoke-tested: `0.10.27` is available at
  `D:\PycharmProjects\releases\GannAstroDesk-0.10.27-three-mode-visualization\`.
  Installer SHA-256:
  `0984D012C21A3D11108ED04A6E063175DFB9E792807A543471FFC40E5641940B`.
  Portable launcher SHA-256:
  `E466F980262C948034D10EAFB3FFF33E602925D93FB4B0CF52F10A924CC39941`.
  The portable executable and its bundled backend were launched successfully.

- The attached Terra High review was accepted as the bounded correction
  contract for `product-first-sbc-phase-lab`: perform PFR-C1 only, then build a
  corrected Windows candidate and stop for founder acceptance.
- C1-1 completed: `ADR-0018` now defines the scope and hard locks; the gap
  matrix records PFR-2 through PFR-5 honestly as partial/prototype work;
  `PFR_C1_ACCEPTANCE_REPORT.md` is the single consolidated progress report.
- No product behavior, calculation, source-certification, Shadbala, ML,
  trading, Android, RAG, or execution code changed in C1-1.
- C1-2 completed: the product panel now consumes the backend-owned
  `GANN_FX_PAIR_EVIDENCE_V2` contract. It identifies each currency/reference
  mapping and evidence cutoff, preserves known/unknown/blocked state and
  coverage, and separates net difference from gross common activation. The
  prior frontend average of cancelling USD/JPY net values has been removed.
  This remains read-only descriptive research; it has no trade, vote, fusion,
  or execution role.
- C1-3 completed: timing phase now includes only currently active aspect
  windows, with an independent lifecycle and displacement for every event.
  Overlaps are no longer forced through one nearest-event phase. The aggregate
  is still a read-only experimental visual with `ABSTAIN`, zero vote,
  zero directional contribution, zero fusion, and execution locked.
- C1-4 completed: the fixed 0/pi wheel now plots rays exactly on the horizontal
  real axis, with selection moved to visual-only groups. Gross magnitude,
  resultant, near-zero state, and unresolved evidence are visually distinct.
  This preserves the scalar parity contract and introduces no angle, timing,
  vote, fusion, financial, or execution meaning.
- C1-5/C1-6 completed: source polarity, per-event timing lifecycle, aggregate
  geometry, unresolved evidence, safe-sector suppression, and `ABSTAIN` are
  explicit without a directional label. The timing experiment now defaults off
  unless `VITE_ENABLE_TIMING_PHASE_EXPERIMENT=true` is deliberately supplied to
  a beta build. Fixed-wheel selection is keyboard reachable and non-colour
  labelled. A deterministic Python mirror provides replayable phase output with
  a stable calculation ID, while retaining zero vote, zero fusion, and locked
  execution.

## Latest Update - 2026-08-01 (Product Beta Scroll-Zoom Repair)

- Founder reported that the `0.10.25` portable beta could blank and close when
  a wheel gesture zoomed the chart out. The repair coalesces costly chart
  overlay updates and delays saved-view persistence until scrolling settles,
  instead of rendering and persisting a new view for every wheel tick.
- `0.10.26` is available as the direct replacement at
  `D:\PycharmProjects\releases\GannAstroDesk-0.10.26-portable-zoom-repair\`.
  Use `Gann Astro Desk 0.10.26 x64 setup.exe`, or run
  `portable\Gann Astro Desk.exe` while keeping its adjacent `backend` folder.
  SHA-256: installer
  `38073F7D17824F7E5D623AB5944F4177D94D6150C942713ED92E0A3D5C4D2E75`;
  portable launcher
  `7836C57E2DF652CCD0E4D4C5D78530A7830716843012245171ABA9A7AB5F66F5`.
  The exact portable folder was launched successfully: both its native window
  and bundled backend were responsive.
- It changes no
  calculation, chart data, experimental SBC state, execution lock, or
  safety behavior.
- Validation before native packaging: lint passed; focused chart/product tests
  passed (`21/21`); production frontend build passed.

## Latest Update - 2026-08-01 (Product-First Recovery PFR-7 Candidate)

- Built the Windows beta candidate from `product-first-sbc-phase-lab` as
  `Gann Astro Desk 0.10.25`. The exact candidate release folder is:
  `D:\PycharmProjects\releases\GannAstroDesk-0.10.25-product-first-beta\`.
- Verified artifacts:
  - Installer: `Gann Astro Desk 0.10.25 x64 setup.exe`
    SHA-256 `0CAB35F38889C10297B5510FF87347528F7AF4EB2DFE625DD333A94C3EF9B033`.
  - Portable folder: `portable\Gann Astro Desk.exe` with its adjacent
    `portable\backend\` resources. Its launcher SHA-256 is
    `662EEA973E1FA9BF56C49A28DF60F427286E0399271A5A83D60142E669373646`.
  - `BETA_README.txt` and `SHA256SUMS.txt` are in the same release folder.
- Native acceptance performed: the portable folder was launched successfully;
  its `Gann Astro Desk` desktop window was responsive and its local
  `GannAstroBackend` process was responsive. A bare copied executable was
  observed to exit without its adjacent backend folder, so the README makes
  the folder requirement explicit.
- PFR-1 through PFR-6 are committed and pushed on this branch. The product now
  contains the synchronized SBC workspace, Time/Profile views, USDJPY context,
  fixed phasor wheel, isolated zero-vote timing lab, and three-model comparison.
  Existing execution/no-lookahead/unknown/scalar-baseline locks remain intact.
- **Stop here for founder acceptance.** Use the five-step checklist in
  `BETA_README.txt`, especially inspecting Workspace, Wheel, Phase lab, and
  Compare in the installed or portable app. Do not resume source certification,
  validation, model fusion, Auto Suggest, ML, or trading work until the founder
  explicitly accepts or reports a product issue.
- Recovery snapshot:
  `chat_session_backups/20260801_110500_product_first_pfr7/` with a SHA-256
  manifest covers the PFR-7 source metadata, product documentation, and handoff.

## Latest Update - 2026-08-01 (Product-First Recovery PFR-6)

- Completed PFR-6 on `product-first-sbc-phase-lab`. The new Compare surface
  places the original scalar SBC baseline, fixed `0/pi` wheel representation,
  and the isolated timing-phase experiment beside each other for one selected
  timestamp.
- Scalar supportive/obstructive/net/gross remains the visible baseline. The
  fixed card explicitly reports real/imaginary/gross and scalar parity. The
  timing card reports lifecycle/resultant/coherence but retains market result
  `ABSTAIN` and a safe-sector suppression explanation where applicable.
- The panel records the pinned UTC timestamp and the existing evidence cutoff,
  states that no future market data is read, and gives a plain explanation of
  why the representations differ. It does not perform a model fusion or alter
  the stored scalar ledger.
- PFR-6 verification: production frontend build and lint pass; focused
  phase/workspace suite `20/20` passes; live browser inspection confirmed the
  three side-by-side states, scalar parity, evidence cutoff, and non-actionable
  labels.
- Recovery snapshot:
  `chat_session_backups/20260801_104300_product_first_pfr6/` with a SHA-256
  manifest covers PFR-6 source, tests, CSS, documentation, and handoff.
- Next directive milestone: PFR-7 Windows beta candidate. It requires a clean
  build, portable/installer artifacts, hashes, and founder-visible native UI
  acceptance before this branch can stop at the requested checkpoint.

## Latest Update - 2026-08-01 (Product-First Recovery PFR-5)

- Completed PFR-5 on `product-first-sbc-phase-lab` as the deliberately
  isolated `PROJECT_CONVENTION_TIMING_PHASE_V0` feature-flagged experiment.
  It is an engineering coordinate, not classical doctrine or a physical-wave
  claim.
- The Phase lab chooses the closest loaded aspect window, records its declared
  applying/exact/separating lifecycle, and rotates only existing resolved SBC
  contribution magnitudes around a versioned phase span. It shows Re, Im,
  resultant, gross activity, coherence, conflict, exact-window context, and
  unresolved contribution count.
- Safety behavior is hard-coded and tested: phase geometry is preserved but
  interpretation is suppressed outside the declared safe sector; a near-zero
  resultant has a null collective phase and market result `ABSTAIN`; every
  other state still reports `ABSTAIN`. Vote weight, directional contribution,
  and fusion coefficient are all `0`; financial validation, order placement,
  and execution remain false.
- PFR-5 verification: production frontend build and lint pass; focused
  phase/workspace suite `19/19` passes; running-workspace inspection confirmed
  the Phase lab, lifecycle, safe-sector suppression, Zero vote, and ABSTAIN
  presentation at the shared selected timestamp.
- Recovery snapshot:
  `chat_session_backups/20260801_104100_product_first_pfr5/` with a SHA-256
  manifest covers the PFR-5 source, tests, CSS, documentation, and handoff.
- Next directive milestone: PFR-6, a read-only, timestamp-safe side-by-side
  comparison of scalar, fixed-wheel, and timing-experiment states with their
  difference causes. It must preserve the scalar baseline and add no inference,
  financial, or execution linkage.

## Latest Update - 2026-08-01 (Product-First Recovery PFR-4)

- Completed PFR-4 on `product-first-sbc-phase-lab`. The Chakra workspace now
  opens a selectable fixed real-axis phasor wheel for the exact synchronized
  workspace moment. The right side is fixed `0`; the left side is fixed `pi`.
- The wheel consumes the existing `SBC_FIXED_ZERO_PI_PHASOR_SERIES_V1`
  response only. It shows vector target, scalar units, real sum, gross
  magnitude, imaginary sum, coverage, and explicit unknown vectors. It does
  not infer timing phase from price or time.
- Guardrails remain visible and intact: this is a scalar visualization only,
  not a vote, timing model, market call, financial confidence, order, or
  execution path. The selected time still governs the chart, SBC snapshot,
  relative-currency context, and wheel together.
- PFR-4 verification: production frontend build and lint pass; focused Chakra
  frontend suite `14/14` passes; live browser inspection confirmed the fixed
  `0/pi` wheel with a selected existing vector and explicit unknown count.
- Recovery snapshot:
  `chat_session_backups/20260801_103500_product_first_pfr4/` with a SHA-256
  manifest covers the PFR-4 source, documentation, test, and handoff.
- Next directive milestone: PFR-5, the isolated, feature-flagged,
  noncertified and nonvoting timing-phase experiment. It must remain
  disconnected from this fixed wheel, forex context, execution, financial
  outputs, and all trading controls.

## Latest Update - 2026-08-01 (Product-First Recovery PFR-3)

- Completed PFR-3 on `product-first-sbc-phase-lab` using the existing selected
  aspect's USDJPY relative-evidence calculation. The workspace now shows USD,
  JPY, base-minus-quote, common-mode, and conflict values together.
- The panel intentionally does not show or translate the stored directional
  field. It states in the interface that the values are descriptive context,
  not a price prediction, and cannot unlock execution.
- PFR-3 verification: production frontend build and lint pass; focused Chakra
  frontend suite `13/13` passes; browser visual inspection confirmed the panel
  against a selected `AVG(ALL) to MARS` USDJPY aspect.
- Recovery snapshot:
  `chat_session_backups/20260801_101933_product_first_pfr3/` with a SHA-256
  manifest covers the PFR-3 source, product documentation, and handoff.
- Next directive milestone: PFR-4, an interactive circular view of the
  existing fixed real-axis phasor series. It must add no vote, timing model,
  prediction, or execution behavior.

## Latest Update - 2026-08-01 (Product-First Recovery PFR-2)

- Completed PFR-2 on `product-first-sbc-phase-lab` as a bounded product view.
  The integrated workspace now has Time and Profile controls that share the
  exact selected IST moment with the loaded price chart, aspect lanes, Chakra,
  and Why drawer.
- The Time view supports prior/next loaded-candle stepping and a deliberate
  manual IST timestamp synchronization. It makes the selected location and
  Panchanga values visible without creating a price or trading prediction.
- The Profile view shows the already-loaded foundation, 81-cell grid, Vedha
  guidance, selected actors, and included layers in plain language. It is
  read-only and does not alter formulas or locks.
- PFR-2 verification: production frontend build and focused Chakra frontend
  suite `12/12` pass; browser visual inspection covered both Time and Profile
  panels at `http://127.0.0.1:5173/`.
- Recovery snapshot:
  `chat_session_backups/20260801_100905_product_first_pfr2/` with a SHA-256
  manifest covers the PFR-2 changes and its acceptance evidence.
- Next directive milestone: PFR-3, a clearly labelled experimental USDJPY
  base-minus-quote and common-mode product panel. Do not change inference,
  execution, or MT5 behavior.

## Latest Update - 2026-08-01 (Product-First Recovery PFR-1)

- The supplied `Product_First_Codex_Recovery_Directive.pdf` is now the active
  product scope. New Shadbala/Drik reconciliation work is parked after its
  clean Ayana handoff; existing safety locks remain unchanged.
- Created branch `product-first-sbc-phase-lab`, concise
  `docs/sbc/ADR-0017-product-first-recovery-scope.md`, and
  `docs/sbc/PRODUCT_FIRST_PFR_GAP_MATRIX_20260801.md`.
- Completed PFR-1: Chakra now opens by default as an integrated founder-facing
  SBC workspace rather than the old audit surface. It brings together:
  - the loaded chart's price context and transparent overlapping aspect lanes;
  - a candle-click synchronized IST Chakra snapshot;
  - supportive, obstructive, gross-activity, conflict, coverage, and explicit
    unknown-input context without making a market call;
  - the 81-cell Chakra with matched/context highlights; and
  - a plain-language Why drawer with resolved Vedha evidence, selected cell,
    and actor readiness.
- The existing raw Board and linked Audit remain available for inspection, but
  no certification, signature, authority, trade, Auto Suggest, ML, shadow,
  inference, execution, or MT5 behavior was added or changed.
- Corrected a product-display-only issue found in visual QA: gross SBC activity
  now sums absolute supportive/obstructive magnitudes, and the compact chart
  uses its actual price range instead of a zero floor.
- Verification: production frontend build passes; focused Chakra frontend
  suite `11/11`; focused Chakra backend suite `24/24`; live browser visual
  inspection passed at `http://127.0.0.1:5173/`.
- Recovery snapshot:
  `chat_session_backups/20260801_095918_product_first_pfr1/` with a SHA-256
  manifest covers the PFR-1 source, tests, handoff, ADR, and gap matrix.
- Runtime-only SQLite databases, logs, and the untracked JHora witness remain
  local and uncommitted.
- Next directive milestone: PFR-2, founder-friendly time and profile views
  sharing the selected timestamp. Do not begin additional certification work
  before the product-first PFR-7 acceptance checkpoint.

## Latest Update - 2026-07-29 (Ayana BPHS Source Comparator V3)

- Completed the bounded Ayana Bala reconciliation without changing production,
  the frozen `0.5`-virupa tolerance, ML features, Auto Suggest, live inference,
  or execution.
- Upgraded the diagnostic contract to
  `GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V3`.
- Implemented an independently source-labelled BPHS chapter-27 verse-15
  comparator:
  - converts nirayana longitude to sayana longitude;
  - folds the longitude to a `0..90` degree nearest-equinox Bhuja;
  - accumulates the `45/33/12` Khanda segments;
  - applies the stated north/south planet groups, Mercury's always-additive
    rule, division by three, and the Sun doubling rule;
  - records sayana longitude, Bhuja, Khanda yoga, candidate value, visible
    JHora value, residual, and frozen pass/fail result for every historical
    planet.
- Source provenance is embedded in the diagnostic and Gate 3:
  `Brihat Parashara Hora Shastra`, chapter 27, verse 15,
  `https://vedicpupil.in/library/brihat-parashara-hora-shastra-book-by-parashara/spashtabal-ch27/15`.
- Locked visible-JHora results:
  - BPHS Khanda source profile: `25/35`, MAE `0.376257605`, maximum error
    `1.720463737`, recent `24/28`, historical `1/7`;
  - modern tropical-projection candidate remains `30/35`, MAE `0.307594721`,
    recent `28/28`, historical `2/7`;
  - production actual-declination profile remains `13/35`.
- The BPHS source profile also cross-checks the fourteen rounded published
  worked-table values at MAE `0.5738205` and maximum error `1.576816`.
- Inspected pinned JHora `8.0.0.0` under the locked 1889 fixture:
  - its contextual position view exposes longitude/speed, ecliptic
    latitude/speed, distance, and distance speed;
  - it does not expose the internal Kranti/declination used by Ayana;
  - F1 redirects to an unrelated Microsoft Windows support page instead of
    JHora formula documentation.
- Saved and hash-locked the visible coordinate view as
  `status/evidence/jhora_kaala_witness_20260727/`
  `jhora_1889_coordinate_view_20260729.jpg`; Gate 3 rejects a missing or altered
  copy.
- Honest conclusion: the BPHS implementation is now auditable and credible as
  doctrine, but neither it nor the modern projection reproduces historical
  JHora closely enough to claim software compatibility. No tolerance was
  widened and no candidate was promoted.
- Gate 3 independently validates the source-profile identity, no-production
  guardrail, all seven historical diagnostic rows, comparator hash, visible
  matrix hash, doctrine config hash, and worked-example hash. It remains
  `failed_external_validation`; Gate 4 remains `blocked_legacy_dataset`.
- Regenerated the formula CSV/JSON, reconciliation report, canonical
  certification report, external gate, and blocked replay result.
- Verification:
  - focused formula/Gate-3 tests `21/21`;
  - complete Python suite `604/604`;
  - touched-file Ruff and compilation pass;
  - canonical status validation passes with 21 documents, 13 audits, and
    execution false;
  - Git diff whitespace check passes.
- Runtime-only SQLite databases and logs remain local and uncommitted.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_2223_ayana_bphs_source_comparator_v3`
  (`21` files plus a SHA-256 manifest; all backup hashes verified).
- Required Ayana compatibility witness remains a visible internal JHora Kranti
  value or JHora implementation documentation. The next bounded doctrine work
  is non-luminary Chesta Bala, followed by independent Drik.

## Latest Update - 2026-07-29 (Nathonnatha Formula Reconciliation V2)

- Completed the bounded Nathonnatha hypothesis test without changing production,
  certification tolerance, ML features, Auto Suggest, live inference, or
  execution.
- Upgraded the diagnostic contract to
  `GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V2`.
- Added an explicit astronomical-midnight profile. For every locked fixture it:
  - calculates the previous and next night midpoints from Swiss Ephemeris
    apparent-tip sunset/sunrise;
  - preserves adjacent civil dates with signed or greater-than-24 LMT hours;
  - selects the nearest midnight;
  - records the exact midpoint, distance, rise/set statuses, and resulting
    day-strength input in the hashed JSON evidence.
- Frozen visible-JHora results:
  - source LMT: `11/35`, MAE `1.484554286`, max error `4.4501`;
  - equation-of-time apparent solar: `11/35`, MAE `1.593672933`;
  - astronomical midnight: `11/35`, MAE `1.591892410`, max error
    `3.565801585`.
- The astronomical-midnight hypothesis is therefore rejected. It does not
  explain case 8 or the historical fixture, and it cannot be promoted merely
  because one residual is smaller.
- Retained the production LMT formula because it remains the source-labelled
  doctrine profile and closely reproduces the two locked published rounded
  worked tables. Visible JHora Nathonnatha remains a software-compatibility
  discrepancy pending a visible JHora apparent-birth-time or internal Unnata
  intermediate.
- Removed stale evidence requests from the generated report and Gate-3 summary:
  - exact case-8 JHora sunrise/Moon Hora evidence is already complete;
  - historical tropical positions are already complete;
  - Ayana now specifically requires an internal Kranti or separately sourced
    formula, not another copy of the same rejected input.
- Hardened the formula gate so it independently re-hashes the comparator
  script, locked visible comparison, doctrine config, and worked-example
  extract. Missing or altered inputs now block the diagnostic before any
  profile result is admitted.
- Regenerated the formula CSV/JSON, reconciliation report, canonical
  certification report, external gate, and blocked legacy replay result.
- Verification:
  - focused Nathonnatha/Gate-3 tests `20/20`;
  - complete Python suite `603/603`;
  - touched-file Ruff and compilation pass;
  - status validation passes with 21 documents, 13 audits, and execution false;
  - Git diff whitespace check passes.
- Runtime-only SQLite databases and logs remain local and uncommitted.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_2122_nathonnatha_reconciliation_v2`
  (`18` files plus a SHA-256 manifest; all backup hashes verified).
- Next bounded doctrine work: reconcile Ayana from its completed visible
  tropical-position packet, then non-luminary Chesta and independent Drik.

## Latest Update - 2026-07-29 (Visible JHora Sthana Gate-3 Packet)

- Completed the genuine visible JHora Sthana subcomponent witness against
  pinned Jagannatha Hora `8.0.0.0`.
- Located the visible table through `Strengths` -> `Other strengths` ->
  right-click Shadbala summary -> `Sthana Bala`. It exposes Uchcha,
  Saptavargaja, Oja Yugma, Kendra, Drekkana, and complete Sthana values.
- Captured five locked fixtures, seven classical planets, and five visible
  components. The completed witness contains `175/175` valid, source-hashed
  rows; no hidden residual was inferred.
- Added a three-profile comparator:
  - production source profile `bphs_ch27_source`;
  - existing `pyjhora_4_8_7_compatibility`;
  - new diagnostic `jhora_8_visible_compatibility`.
- Component reconciliation at the frozen `0.5`-virupa tolerance:
  - Uchcha, Ojayugma, Kendradi, and Drekkana match visible JHora `35/35`
    under the production implementation;
  - production Saptavargaja matches `3/35`, leaving complete production
    Sthana at `1/35`;
  - PyJHora compatibility matches `34/35`; its sole failure is case-8 Saturn,
    where all Aquarius is treated as Moolatrikona;
  - the named visible-JHora profile keeps degree-bounded Saturn
    Moolatrikona, matches every component `35/35`, and matches complete Sthana
    `35/35` with maximum error `0.007808165` virupa.
- This is a diagnostic compatibility result, not a silent doctrine change:
  `sourceCertified=false`, `financiallyValidated=false`,
  `productionChangeAllowed=false`, and `executionAllowed=false`.
- Added fail-closed Gate-3 integration and a dedicated manifest:
  `status/evidence/jhora_sthana_subcomponents_20260729/`
  `JHORA_STHANA_EVIDENCE_MANIFEST_20260729.md`.
- Regenerated the canonical v14 certification report. Gate 3 remains
  `failed_external_validation`; independent Drik remains `9/35`; Gate 4
  remains `blocked_legacy_dataset`.
- Final verification:
  - focused doctrine/Gate-3 tests `34/34`;
  - complete Python suite `602/602`;
  - canonical status validation passes with 21 documents, 13 audits, and
    execution false;
  - repository-wide Ruff and touched-file compilation pass;
  - frontend tests `102/102`, lint, and production build pass;
  - Rust formatting, `18/18` tests, and strict Clippy pass;
  - Git diff whitespace check passes.
- Gate 3 independently re-hashes the witness packet, top-level Sthana matrix,
  and doctrine config embedded in the comparator summary. A missing or altered
  locked input now blocks the Sthana result before any compatibility claim.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_2044_jhora_visible_sthana_gate3`.
- Next bounded doctrine work after recovery closure: Nathonnatha, Ayana,
  non-luminary Chesta, and Drik, one explicit profile and witness at a time.

## Latest Update - 2026-07-29 (Genuine Visible JHora Kaala Gate-3 Packet)

- Completed the bounded visible JHora Hora/Ayana evidence milestone against the
  pinned Jagannatha Hora `8.0.0.0` executable without widening the frozen
  `0.5`-virupa tolerance or changing trading behavior.
- Found and regression-locked a critical fixture rule: JHora `.jhd` time uses
  packed `HH.MMSS`, not decimal hours. The three review fixtures are now
  captured at their exact event times:
  - case 8: `19:30`;
  - case 43: `02:30`;
  - case 103: `22:30`.
  The superseded `:50` captures are retained with explicit provenance labels.
- Added `jhora_fixture_file.py` and tests so packed-time parsing and writing
  fail closed instead of silently shifting future evidence by 20 minutes.
- Captured a genuine case-8 visible Hora boundary packet:
  - the same instant was entered as LMT `23:18:36.072`;
  - JHora visibly reports apparent-tip sunrise `6:22:22`;
  - JHora visibly awards Moon Hora `60` virupa and Sun, Mars, Mercury, Jupiter,
    Venus, and Saturn `0`;
  - the exact-time local Hora matrix now matches all `35/35` locked rows.
- Captured the complete historical seven-planet JHora tropical-longitude and
  Ayana observation. The evidence is provenance-complete, but the tested
  tropical-Kranti reconstruction exceeds tolerance for five planets
  (`2.127890`, `1.105863`, `1.073595`, `1.037835`, and `0.980442` virupa).
  Therefore the observation is accepted and the formula candidate is rejected.
- Hardened `GANN_JHORA_KAALA_INTERMEDIATE_WITNESS_V1`:
  - stores the raw visible sunrise string and derives decimal time
    mechanically;
  - validates every nested source path and SHA-256 in the evidence bundle;
  - rejects missing, altered, inferred, or internally inconsistent evidence.
- Completed machine-readable packets:
  - Hora packet:
    `status/evidence/jhora_kaala_intermediate_20260729/`
    `jhora_hora_boundary_witness_completed.csv`,
    SHA-256
    `AF2CE318E2955506246960C9C1E7EA5CB3A17678E38F57C4AE5D80076F5BA32E`;
  - Ayana packet:
    `status/evidence/jhora_kaala_intermediate_20260729/`
    `jhora_ayana_intermediate_witness_completed.csv`,
    SHA-256
    `85B1B2343DA57D437F81A530B88A018A76A8D8170EDABBC22D298104A319C2E4`;
  - case-8 evidence bundle:
    `case_8_event_start_exact_hora_boundary_evidence_20260729.json`,
    SHA-256
    `22226178A12867EE4FC2795BA03A4BF602112F377B20D727F87D64581601396E`.
- Gate-3 status is now
  `visible_packet_complete_formula_candidate_rejected`:
  - `evidenceComplete=true`;
  - `horaEvidenceComplete=true`;
  - `ayanaEvidenceComplete=true`;
  - `formulaCertified=false`;
  - `productionChangeAllowed=false`;
  - `executionAllowed=false`.
- Exact-time visible Kaala comparison:
  - Abda, Masa, Vara, Hora, Tribhaga, Paksha, and Yuddha: `35/35`;
  - Nathonnatha: `11/35`;
  - Ayana: `13/35`;
  - aggregate Kaala: `5/35`, MAE `2.763` virupa.
- Full locked JHora component admission remains deliberately blocked:
  - Naisargika: `35/35`;
  - Sthana: `1/35`;
  - Dig: `19/35`;
  - Chesta: `12/35`;
  - Drik: `9/35`;
  - full Shadbala total: `3/35`, MAE `11.829` virupa.
  Hora's narrow `35/35` alignment does not certify aggregate Kaala, full
  Shadbala, ML use, Auto Suggest, live inference, or execution.
- Regenerated the canonical `20260729` Gate-3 report and the legacy-referenced
  `20260718` compatibility report with the same final v13 evidence. The
  canonical gate remains `failed_external_validation`; Gate 4 remains
  `blocked_legacy_dataset`.
- Final verification:
  - complete Python suite `597/597`;
  - canonical status validation passes with 21 documents, 13 audits, and
    execution false;
  - repository-wide Ruff and touched-file compilation pass;
  - frontend tests `102/102`, lint, and production build pass;
  - Rust formatting, `18/18` tests, and strict Clippy pass;
  - Git diff whitespace check passes.
- Runtime-only SQLite databases and logs remain local and uncommitted.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_1952_jhora_visible_kaala_gate3`.
- Next bounded certification work: complete visible Sthana subcomponent
  evidence, then reconcile Nathonnatha, Ayana, non-luminary Chesta, and Drik
  one named doctrine profile at a time. No component may be promoted merely
  because it is closer than another candidate.

## Latest Update - 2026-07-29 (Repository Verification Hygiene Closure)

- Closed the repository-wide hygiene blockers found during the SBC/JHora audit
  without changing financial behavior, astrology doctrine, Auto Suggest, live
  inference, ML notes, or execution permissions.
- Repository-wide Python Ruff now passes:
  - moved the `aspect_evidence_trace.py` module docstring ahead of its future
    import and removed its unused `datetime` import;
  - removed unused Word-manual imports/local state;
  - removed the unused `datetime` symbol from `sbc/snapshot.py`;
  - excluded the separate local `tryapp-android/` project at the parent
    repository boundary.
- Rust verification is clean:
  - normalized the remaining `cargo fmt` drift;
  - retained desktop execution of Android companion security tests while
    applying one test-only dead-code allowance at the module boundary;
  - `cargo fmt --all -- --check` passes;
  - `cargo test --all-targets` passes `18/18`;
  - strict `cargo clippy --all-targets --all-features -- -D warnings` passes.
- Stabilized frontend verification on this Windows machine:
  - bounded Vitest to two workers, avoiding the uncontrolled worker-start
    timeouts seen under machine load;
  - raised only the full P4 package/replay/catalog UI test from 10 to 20
    seconds and removed one stray duplicate mock reset;
  - repeated `npm test` runs pass `102/102`;
  - frontend lint and production build pass.
- Historical SBC audit JSON remains unchanged. Its old repository-wide
  blocker strings are dated evidence and exact-match validated; rewriting them
  after the fact would corrupt audit lineage. This checkpoint records the
  current resolved state instead.
- Final verification:
  - complete Python suite `583/583`;
  - focused evidence-trace/SBC snapshot suite `17/17`;
  - repository-wide Ruff passes;
  - touched Python files compile;
  - canonical status validation passes with 21 documents, 13 audits, and
    execution false;
  - frontend tests `102/102` pass twice with bounded workers;
  - frontend lint and production build pass;
  - Rust formatting, `18/18` tests, and strict Clippy pass;
  - Git diff whitespace check passes.
- Runtime-only SQLite databases and logs remain local and uncommitted.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_1645_repository_hygiene_closure`.
- Next bounded certification action remains unchanged: capture genuine visible
  JHora case-8 Hora and historical Ayana intermediates through the assistant,
  then run the completed packet through Gate 3. No values should be inferred.

## Latest Update - 2026-07-29 (Guided JHora Kaala Capture Assistant)

- Added a double-clickable Windows evidence workflow:
  `Launch_JHora_Kaala_Capture_Assistant.cmd`, backed by
  `jhora_kaala_capture_assistant.py` and contract
  `GANN_JHORA_KAALA_CAPTURE_ASSISTANT_V1`.
- The assistant has three explicit tabs:
  - case-8 Hora boundary capture;
  - seven-planet historical Ayana capture;
  - completed-packet verification through the existing fail-closed gate.
- It requires a named reviewer and reviewer-entered values actually visible in
  pinned JHora `8.0.0.0`. It hashes the selected uncropped evidence, binds UTC
  capture time, and validates every row before writing a completed packet.
- It deliberately does not:
  - read or scrape JHora automatically;
  - derive a missing visible value;
  - fill values from the local comparator or locked result column;
  - overwrite the pending templates;
  - certify a production formula or unlock execution.
- Valid completed packets are written separately under
  `status/evidence/jhora_kaala_intermediate_20260729/`. Invalid or contradictory
  input leaves no completed output file.
- Certification report version advanced to
  `astro_certification_4_gate_v12_kaala_capture_assistant_20260729`. The Gate-3
  artifact records availability and SHA-256 hashes for both the assistant and
  launcher, with all inference, production-change, and execution permissions
  false.
- Added `test_jhora_kaala_capture_assistant.py`. Regression coverage proves:
  - evidence path/hash and reviewer provenance are bound without mutating the
    templates;
  - a complete two-part synthetic witness reaches only
    `visible_packet_complete_not_formula_certified`;
  - contradictory Hora input is rejected before output is written;
  - the pending templates cannot be overwritten;
  - certification metadata cannot promote or unlock the assistant.
- Interactive Windows QA passed at `1400x1066` across the Hora, Ayana, and
  Verify tabs. The pending-state verifier rendered correctly, controls were
  readable, and the test window closed without a surviving process.
- Final verification:
  - complete Python suite `583/583`;
  - focused assistant/protocol/certification/status suite `70/70`;
  - changed Python scope passes Ruff and compilation;
  - Git diff whitespace check passes;
  - status validation passes with 21 documents, 13 audits, and execution false.
- No visible JHora intermediate was fabricated during this milestone. The two
  real evidence packets remain pending and production formulas remain
  unchanged.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_1557_jhora_kaala_capture_assistant`.
- Next bounded certification action: use the assistant alongside the pinned
  JHora window to capture the genuine case-8 sunrise/Hora table and the
  historical seven-planet tropical-longitude or Kranti/Ayana table, then run
  the completed packet through Gate 3.

## Latest Update - 2026-07-29 (Visible JHora Kaala Intermediate Gate)

- Converted the unresolved case-8 Hora boundary and historical Ayana question
  into a machine-enforced, fail-closed evidence contract:
  `GANN_JHORA_KAALA_INTERMEDIATE_WITNESS_V1`.
- Added:
  - implementation:
    `jhora_kaala_intermediate_witness_protocol.py`;
  - tests:
    `test_jhora_kaala_intermediate_witness_protocol.py`;
  - protocol:
    `jhora_kaala_intermediate_witness_protocol_20260729.md`;
  - seven-row Hora template:
    `jhora_hora_boundary_witness_template_20260729.csv`;
  - seven-row historical Ayana template:
    `jhora_ayana_intermediate_witness_template_20260729.csv`.
- The Hora packet requires JHora's visible apparent-tip sunrise in local mean
  time, one shared visible Hora lord, and all seven awards. Exactly one planet
  must receive `60` virupa and the other six must receive `0`.
- The Ayana packet deliberately includes all seven classical planets for the
  1889 fixture rather than only the five failures. Each row requires visible
  JHora tropical longitude, Kranti, or both plus visible Ayana; the validator
  reconstructs the result at the unchanged `0.5`-virupa tolerance.
- Every captured row must bind the pinned JHora `8.0.0.0` executable hash,
  locked settings hash, uncropped evidence path/hash, reviewer, and
  timezone-aware capture time. Missing, inferred, duplicated, unhashed, or
  inconsistent values are rejected.
- Integrated the packet into `astro_function_certification.py` and the
  generated external gate. Current status is
  `blocked_pending_visible_kaala_intermediate_witness`, with
  `evidenceComplete=false`, `formulaCertified=false`, and
  `productionChangeAllowed=false`.
- A live capture was attempted against the pinned JHora process. Its legacy
  window refused a safe capture handle on the initial attempt and the one
  permitted recovery attempt. No sunrise, Hora, tropical-longitude, Kranti, or
  Ayana value was guessed or reverse-engineered.
- No production doctrine, tolerance, ML feature, Auto Suggest rule,
  timestamp-safe live inference, or execution path changed.
- Final verification:
  - complete Python suite `578/578`;
  - focused protocol/certification/status suite `65/65`;
  - changed Python scope passes Ruff and compilation;
  - Git diff whitespace check passes;
  - status validation passes with 21 documents, 13 audits, and execution false.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_1522_jhora_kaala_intermediate_gate`.
- Next bounded certification work: fill the two templates from genuine visible
  JHora intermediates, validate the complete packet, and only then reconsider
  the Hora or historical Ayana formula candidates. Completion still would not
  grant source certification, financial validation, or execution permission.

## Latest Update - 2026-07-29 (Kaala Formula Profile Reconciliation)

- Completed the bounded Hora, Nathonnatha, and Ayana investigation against the
  locked `35`-row visible JHora Kaala witness without changing production
  doctrine, widening the frozen `0.5`-virupa tolerance, or enabling ML or
  execution use.
- Added deterministic diagnostic contract
  `GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V1`:
  - generator:
    `jhora_kaala_formula_profile_reconciliation.py`;
  - tests:
    `test_jhora_kaala_formula_profile_reconciliation.py`;
  - report:
    `jhora_kaala_formula_reconciliation_20260729.md`;
  - evidence:
    `status/evidence/jhora_kaala_witness_20260727/`
    `jhora_kaala_formula_profiles_20260729.csv` and `.json`.
- Nathonnatha:
  - retained the current LMT source profile;
  - current LMT is `11/35`, MAE `1.842805714`;
  - apparent-solar time is also `11/35` but slightly worse at MAE
    `1.847431781`;
  - the current profile closely reproduces the rounded Lady Diana and Prince
    William worked-example day/night values, so no formula change is justified.
- Hora:
  - retained the astronomical-sunrise award profile at `33/35`;
  - variable day/night planetary hours are worse at `27/35`;
  - the remaining case-8 categorical award changes from Moon to Saturn across
    only `3.436256` minutes of sunrise input;
  - production Hora remains unchanged pending a visible JHora sunrise or
    intermediate Hora-award witness for that fixture.
- Ayana:
  - current actual equatorial declination passes `13/35`, MAE
    `1.973396577`;
  - the tropical-longitude Kranti candidate passes `30/35`, MAE
    `0.307594721`, including all `28/28` recent rows;
  - it still passes only `2/7` historical 1889 rows, so it is explicitly a
    diagnostic candidate, not a promoted production formula;
  - next evidence required is visible JHora tropical longitude or intermediate
    Kranti for the five failing historical rows.
- `astro_function_certification.py` now consumes this reconciliation as a
  fail-closed diagnostic section. The generated external gate records
  `productionChangeAllowed=false`, and the report explains the unresolved
  Hora and historical Ayana witnesses.
- Preserved the existing evidence lineage during report regeneration:
  Tier-B Drik is `35/35`, while the completed independent visible JHora Drik
  witness remains failed at `9/35`; full Shadbala/Drik and execution remain
  excluded.
- Final verification:
  - complete Python suite `574/574`;
  - focused certification/reconciliation suite `34/34`;
  - changed Python scope passes Ruff and compilation;
  - status validation passes with 21 documents, 13 audits, and execution false.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_1452_kaala_formula_reconciliation`.
- Next bounded certification work: capture the exact visible JHora
  sunrise/Hora intermediate for case 8 and tropical longitude or Kranti
  intermediate values for the five failing 1889 Ayana rows. Do not promote the
  candidate or widen tolerance before those witnesses are complete.

## Latest Update - 2026-07-29 (Visible JHora Sthana Capture Gate)

- Completed the next bounded Sthana certification step without changing a
  doctrine formula or widening tolerance.
- First-party JHora material confirms that version 8.0 calculates Shadabala and
  supports configurable divisional-chart variants and relationship scopes, but
  it does not publish numerical Uchcha, Saptavargaja, Ojayugma, Kendradi, and
  Drekkana breakdowns.
- The completed locked JHora screenshots/clipboard tables contain only
  top-level Sthana. The pinned legacy JHora window did not expose a reliable
  screenshot/accessibility surface in the current Codex desktop session.
  No subcomponent value was copied, inferred, or reverse-engineered.
- Added fail-closed contract
  `GANN_JHORA_STHANA_SUBCOMPONENT_WITNESS_V1`:
  - implementation:
    `jhora_sthana_subcomponent_witness_protocol.py`;
  - pending `175`-row template:
    `jhora_sthana_subcomponent_witness_template_20260729.csv`;
  - protocol:
    `jhora_sthana_subcomponent_witness_protocol_20260729.md`;
  - tests:
    `test_jhora_sthana_subcomponent_witness_protocol.py`.
- The required matrix is five fixtures x seven classical planets x five
  Sthana subcomponents. Every value needs visible uncropped JHora evidence,
  an evidence hash, reviewer, timezone-aware capture time, and captured status.
  Missing or inferred values are rejected.
- Each five-component sum must match the already locked top-level JHora Sthana
  value within the unchanged `0.5`-virupa tolerance. Completing this matrix
  would still not grant source certification, financial validation, or
  execution permission.
- Updated the original JHora witness protocol and
  `status/source_certification.json` to label the `34/35` Sthana result as the
  separate PyJHora-compatible diagnostic and the production subcomponent gate
  as `blocked_pending_visible_sthana_subcomponent_witness`.
- Verification on the final source state:
  - complete Python suite `568/568`;
  - new capture-contract tests `3/3`;
  - changed Python scope passes Ruff and compilation;
  - status validation passes with execution false.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_1403_jhora_sthana_capture_gate`.
- Next bounded work: reconcile the visible Hora, Nathonnatha, and Ayana
  residuals. Production Sthana remains fail-closed until a genuine visible
  subcomponent table is available.

## Latest Update - 2026-07-29 (Shadbala Evidence-Lineage Correction)

- Corrected a real audit defect exposed by the component witness trace:
  the previous reconciliation fed the separately named PyJHora-compatible
  Sthana comparator profile into the local total instead of the actual
  BPHS-labeled production source profile.
- Production evidence now comes directly from `doctrine_config.yaml` and
  `strict_shadbala_doctrine.py`:
  - production Sthana uses `sthana_partial_virupa`;
  - the Tier-B diagnostic continues to use `sthana_comparator_virupa`;
  - a regression test prevents either profile from silently replacing the
    other.
- This section supersedes the production interpretation in the immediately
  following component-boundary entry. At the unchanged `0.5`-virupa
  tolerance, the corrected production-versus-JHora results are:
  - Sthana `1/35`, mean absolute error `6.296255146` virupa;
  - full total `3/35`, mean absolute error `11.829084359` virupa;
  - aggregate Kaala `5/35`, Dig `19/35`, Chesta `12/35`,
    Naisargika `35/35`, and Drik `9/35`.
- The stronger Sthana `34/35` figure remains useful only as a clearly labeled
  PyJHora-compatible Tier-B diagnostic. It is not a production formula,
  production total, source certification, financial validation, or execution
  permission.
- Fixed a second reproducibility defect found by the complete test suite:
  astrology tests could change Swiss Ephemeris' process-global file path and
  shift frozen metrics by tiny amounts. Each component calculation now resets
  the canonical ephemeris path and doctrine-locked sidereal mode. A regression
  test proves the results survive a hostile prior path change.
- Regenerated the V3 reconciliation CSV/JSON/report and the four-gate
  certification report. Updated source/capability status and the external
  validation gate with the corrected production lineage.
- No doctrine formula or tolerance was changed to improve agreement.
  Full Shadbala, Sthana, Drik, and execution remain fail-closed.
- Final verification:
  - complete Python suite `565/565`;
  - scoped lineage/reconciliation suite `9/9`;
  - changed Python scope passes Ruff and compilation;
  - status validation passes with 21 documents, 13 audits, and execution false.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Timestamped recovery snapshot:
  `chat_session_backups/session_20260729_1342_shadbala_evidence_lineage`.
- Next bounded certification work: obtain or create a visible JHora Sthana
  subcomponent witness for Uchcha, Saptavargaja, Ojayugma, Kendradi, and
  Drekkana before changing the production formula. Then continue with visible
  Hora, Nathonnatha, and Ayana reconciliation. Do not widen tolerances.

## Latest Update - 2026-07-29 (Shadbala Component Witness Admission Boundary)

- Expanded the locked local-versus-JHora reconciliation from four aggregate
  measures to the complete seven-part top-level matrix:
  Sthana, Kaala, Dig, Chesta, Naisargika, Drik, and total.
- `jhora_doctrine_reconciliation.py` now emits contract
  `GANN_JHORA_DOCTRINE_RECONCILIATION_V3` with `245/245` deterministic
  top-level rows plus the existing `175` named Drik sensitivity rows.
- Added a machine-readable, fail-closed component admission boundary:
  - a component is independently witness-aligned only when all `35/35` locked
    rows pass at the unchanged `0.5`-virupa tolerance;
  - top-level Naisargika is aligned at `35/35`;
  - visible Kaala subcomponents Abda, Masa, Vara, Tribhaga, Paksha, and Yuddha
    are aligned at `35/35` each;
  - Sthana `34/35`, Dig `19/35`, aggregate Kaala `5/35`, Chesta `12/35`,
    Drik `9/35`, and full total `0/35` remain provisional.
- Alignment is deliberately distinct from source certification, financial
  validation, and execution permission. All three remain false. No tolerance
  was widened, and no formula was changed merely to resemble JHora.
- `astro_function_certification.py` now consumes the V3 reconciliation as a
  required Gate-3 input, verifies the aligned/provisional partitions, rejects
  stale or incomplete contracts, and exposes the complete top-level component
  table in `astro_external_validation_gate_20260729.json` and
  `astro_function_certification_report_20260729.md`.
- Corrected stale capability wording: the independent JHora witness is
  complete and failed full reconciliation; it is not pending.
- Updated `doctrine_config.yaml` and `status/source_certification.json` with the
  explicit component boundary while retaining full Shadbala/Drik and execution
  locks.
- Verification on the final source state:
  - focused reconciliation/certification tests `13/13`;
  - complete repository Python suite `563/563`;
  - changed Python scope passes Ruff and compilation;
  - canonical status validation passes with 21 documents, 13 audits, and
    execution false;
  - deterministic reconciliation and four-gate report regeneration pass.
- No frontend, Rust, Windows installer, Android package, Auto Suggest, live
  inference, official ML-note, or MT5 execution behavior changed.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Timestamped source recovery snapshot:
  `chat_session_backups/session_20260729_1250_shadbala_component_witness_matrix`.
- Next bounded doctrine work: reconcile the single Sthana residual first, then
  case-8 Hora sunrise-boundary behavior and Nathonnatha/Ayana residuals from
  visible inputs. Drik and non-luminary Chesta remain separate doctrine
  investigations; do not improve their pass ratios by tolerance widening.

## Latest Update - 2026-07-29 (Source-Certification Authority Gate S5)

- Completed S5 in source under:
  - report contract `SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_REPORT_V1`;
  - certificate contract `SBC_TIMING_PROFILE_SOURCE_CERTIFICATE_V1`;
  - authority-registry contract
    `SBC_TIMING_PROFILE_CERTIFICATION_AUTHORITY_REGISTRY_V1`;
  - proposal contract `SBC_TIMING_PROFILE_REGISTRY_ENTRY_PROPOSAL_V1`;
  - policy `ED25519_SEPARATE_AUTHORITY_EXACT_S4_BINDING_V1`;
  - classification `SOURCE_PROFILED_EXPERIMENTAL`.
- The deterministic implementation is
  `sbc/timing_profile_source_certification.py`; its audited
  line-ending-independent canonical-text SHA-256 is
  `EB4278C5388875C2A9A7CCF0378DBC8084F359D7EB9F76F7EDD96362D75B84F0`.
- Froze the boundary and canonical evidence in:
  - `docs/sbc/ADR-0016-source-certification-authority-gate.md`;
  - `docs/sbc/S5_ACCEPTANCE.md`;
  - `sbc_timing_source_certification_s5_20260729.md`;
  - `status/audits/sbc_timing_profile_source_certification_s5_20260729.json`;
  - server-owned
    `status/timing_profile_certification_authority_registry.json`.
- S5 reruns the complete S1-S4 chain and verifies a separate Ed25519 source
  certificate. The authority certificate binds the exact review bundle,
  completed attestation, signed review, S3 proposal, candidate profile, and
  source packet.
- The client cannot supply an authority public key or authority registry. The
  server loads the repository registry and enforces raw-key-derived key IDs,
  validity dates, revocation, profile and packet scopes, identity,
  organization, exact evidence binding, and administratively vetted
  reviewer/certifier separation.
- The certifier public key and identity must differ from the S4 reviewer. A
  reviewer cannot self-certify, and the more specific
  `CERTIFICATION_AUTHORITY_UNTRUSTED` state is preserved for that failure.
- A valid `REJECTED` certificate reports `SOURCE_CERTIFICATION_REJECTED`. A
  valid `CERTIFIED` certificate may report only
  `READY_FOR_PROFILE_REGISTRY_ADMISSION` and emit a reproducibly hashed
  registry-entry proposal for a separate human-reviewed Git change.
- S5 never writes a registry, registers a profile, calculates direction or
  confidence, affects Auto Suggest, live inference, ML evidence, or shadow
  voting, produces a trade, or enables MT5 execution. Source certification is
  a signed governance decision, not cryptographic proof of doctrinal truth.
- The repository certification-authority registry intentionally contains zero
  authorities. Therefore no real source certificate can pass until an
  external authority and separation of duties are vetted and enrolled through
  a separate human-reviewed change.
- Added private backend POST
  `/api/chakra-lab/timing-profile/source-certification/verify`, read-only native
  command `chakra_lab_timing_source_certification`, typed frontend transport,
  and the Chakra Audit `Source certificate` tab.
- The tab accepts four evidence files, displays the rerun S4 state, authority
  registry, authority trust, separation, signature, decision, proposal/manual
  registry boundary, missing requirements, blocked capabilities, and execution
  lock. It can download a certificate template or verified registry proposal
  but cannot apply either one.
- Canonical status validation now controls twenty-one documents and thirteen
  audits. It pins the S5 module hash, contracts, signature/proposal policies,
  empty server registry, human-control boundaries, transport, and all
  inference, financial, registry-write, and execution locks.
- Verification on the final source state:
  - S5 engine tests `13/13`;
  - Chakra Lab service tests `24/24`;
  - Chakra Audit workspace tests `10/10`;
  - complete repository Python suite `562/562`;
  - complete frontend suite `102/102`;
  - status tests `50/50`;
  - S5 changed Python scope passes Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check` and focused `rustfmt --check` pass;
  - canonical status validation passes with 21 documents, 13 audits, and
    execution false.
- Repository-wide Ruff still reports the same 19 known, pre-existing,
  out-of-scope findings. Repository-wide `cargo fmt --check` remains blocked
  only by the older formatting difference in
  `gann-astro-desk/src-tauri/src/companion_gateway.rs`. The production build
  still reports the existing main-bundle size advisory.
- Live endpoint acceptance passed on port `8788`. Empty input returned
  `S4_NOT_READY`; client-supplied `authorityRegistry` was rejected with HTTP
  400. In every path the authority registry stayed server-owned, profile
  registration and registry writes remained false, directional contribution
  remained zero, and execution remained false.
- Real in-app-browser acceptance passed at
  `http://127.0.0.1:5173/?s5=acceptance`. The `Source certificate` tab showed
  `S4 Not Ready`, the valid empty server registry, untrusted authority key,
  unvetted separation, unverified certificate, manual-only registry write,
  and execution locked without bullish or bearish output.
- S5 remains unpackaged. No real review bundle, completed attestation, signed
  review, source certificate, trusted authority, registry entry, timing
  profile, directional engine, or prospective financial validation is
  shipped. No Windows or Android package was rebuilt.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Timestamped source recovery snapshot:
  `chat_session_backups/session_20260729_120539_sbc_timing_source_certification_s5`.
- S5 implementation commit before this publication marker:
  `c740a96` (`Implement S5 source certification authority gate`).
- Next bounded milestone: obtain genuinely external S1-S5 evidence and a
  human-reviewed authority enrollment, then consider a separate manual timing
  profile registry admission. The application must not populate its own
  authority registry, certify its own evidence, or auto-register a profile.

## Latest Update - 2026-07-29 (Trusted Reviewer Signature Gate S4)

- Completed S4 in source under:
  - report contract `SBC_TIMING_PROFILE_SIGNED_REVIEW_REPORT_V1`;
  - signed-envelope contract `SBC_TIMING_PROFILE_SIGNED_REVIEW_V1`;
  - reviewer registry contract
    `SBC_TIMING_PROFILE_REVIEWER_TRUST_REGISTRY_V1`;
  - policy `ED25519_SERVER_TRUST_REGISTRY_EXACT_S3_BINDING_V1`;
  - classification `SOURCE_PROFILED_EXPERIMENTAL`.
- The deterministic implementation is
  `sbc/timing_profile_signed_review.py`; its audited
  line-ending-independent canonical-text SHA-256 is
  `7DFC7E406804AA93A55C70E8A5B8527C4169723496281E31BBFA608ACCE49142`.
  Signatures use Ed25519 over canonical JSON with `signatureBase64` blank.
- Froze the boundary and canonical evidence in:
  - `docs/sbc/ADR-0015-trusted-reviewer-signature-verification.md`;
  - `docs/sbc/S4_ACCEPTANCE.md`;
  - `sbc_timing_signed_review_s4_20260729.md`;
  - `status/audits/sbc_timing_profile_signed_review_s4_20260729.json`;
  - server-owned `status/timing_profile_reviewer_trust_registry.json`.
- S4 reruns S3 and binds the exact S2 review bundle, completed attestation,
  S3 certification proposal, candidate profile, and source packet. It rejects
  changed bindings, invalid signatures, unknown, revoked, expired, premature,
  out-of-profile, out-of-packet, identity-mismatched, and
  organization-mismatched reviewer keys.
- The client cannot supply a public key or reviewer registry. The server loads
  the repository registry, validates each key ID against the raw 32-byte
  Ed25519 public key, and enforces validity, revocation, scope, identity, and
  organization. Registry writes remain disabled.
- A valid registered-key signature may emit only
  `READY_FOR_MANUAL_SOURCE_CERTIFICATION`. It proves that the registered key
  signed the exact evidence. It does not cryptographically prove human
  independence, doctrinal truth, source certification, profile registration,
  financial validity, or execution permission.
- The repository reviewer registry intentionally contains zero reviewers.
  Therefore no real reviewer is authenticated and no real signature can pass
  until identity and independence are vetted outside the application and a
  separate human-reviewed registry change is committed.
- Added private backend POST
  `/api/chakra-lab/timing-profile/signed-review/verify`, read-only native
  command `chakra_lab_timing_signed_review`, typed frontend transport, and the
  Chakra Audit `Signed review` tab.
- The tab accepts an S2 bundle, completed S3 attestation, and separately signed
  envelope. It exposes every gate, missing requirement, blocked capability,
  trust-registry state, signature result, and the explicit distinction between
  registered-key identity and reviewer independence. It never accepts a client
  public key and never unlocks source certification or execution.
- Canonical status validation now controls nineteen documents and twelve
  audits. It pins the S4 module hash, contracts, exact signature policy,
  server-owned empty registry, human-control boundary, transport, and all
  inference, registry, financial, and execution locks.
- Verification on the final source state:
  - S4 engine tests `11/11`;
  - Chakra Lab service tests `22/22`;
  - Chakra Audit workspace tests `9/9`;
  - complete repository Python suite `542/542`;
  - complete frontend suite `101/101`;
  - status tests `45/45`;
  - S4 changed Python scope passes Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check` and focused `rustfmt --check` pass;
  - canonical status validation passes with execution false.
- Repository-wide Ruff still reports the same 19 known, pre-existing,
  out-of-scope findings. Repository-wide `cargo fmt --check` remains blocked
  only by the older formatting difference in
  `gann-astro-desk/src-tauri/src/companion_gateway.rs`. The production build
  still reports the existing main-bundle size warning.
- Live endpoint acceptance passed on port `8788`. Empty input returned
  `S3_NOT_READY`; a fully signed synthetic record from a key absent from the
  server registry returned `REVIEWER_KEY_UNTRUSTED`. In both cases source
  certification, profile registration, registry writes, and execution
  remained false.
- Real in-app-browser acceptance passed at
  `http://127.0.0.1:5173/?s4=1`. The `Signed review` tab showed the empty valid
  server registry, untrusted reviewer key, unverified signature, manual
  certification boundary, every blocked capability, and execution locked.
- S4 remains unpackaged. No real review bundle, completed attestation, signed
  envelope, trusted reviewer key, source certificate, or registered timing
  profile is shipped. No Windows or Android package was rebuilt.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Timestamped source recovery snapshot:
  `chat_session_backups/session_20260729_110638_sbc_timing_signed_review_s4`
  (21 scoped S4 source, test, status, UI, and handoff files; no runtime data).
- Next bounded milestone: establish a genuinely external, human-controlled key
  enrollment and manual source-certification record, or stop pending real
  evidence. S4 must never add a reviewer key, certify its own evidence, or
  promote a timing profile automatically.

## Latest Update - 2026-07-29 (External Review Attestation Gate S3)

- Completed S3 in source under:
  - report contract `SBC_TIMING_PROFILE_EXTERNAL_REVIEW_REPORT_V1`;
  - review policy
    `INTERNAL_COHERENCE_AND_EXACT_DECISION_COVERAGE_V1`;
  - proposal contract
    `SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_PROPOSAL_V1`;
  - classification `SOURCE_PROFILED_EXPERIMENTAL`.
- The deterministic implementation is
  `sbc/timing_profile_external_review.py`; its audited
  line-ending-independent canonical-text SHA-256 is
  `9D008E3E6058F5FA2B1396373A26E47AC104D45E5B4F4CF525AE68CE7FB28F0E`.
  Proposal hashes use
  `CANONICAL_JSON_SHA256_WITH_PROPOSAL_SHA256_BLANK`.
- Froze the boundary and canonical evidence in:
  - `docs/sbc/ADR-0014-external-review-attestation-verification.md`;
  - `docs/sbc/S3_ACCEPTANCE.md`;
  - `sbc_timing_external_review_s3_20260729.md`;
  - `status/audits/sbc_timing_profile_external_review_s3_20260729.json`.
- S3 reproduces the S2 review-bundle digest, reruns the embedded S1 gate,
  reconciles all S2 source and excerpt rows against the packet, and requires
  exact source, claim, and conflict decision coverage. Duplicate, missing,
  extra, pending, inconsistent, or note-less decisions fail closed.
- A valid rejection emits `REVIEW_REJECTED` with no proposal. A complete
  all-pass approval emits only
  `READY_FOR_HUMAN_CERTIFICATION_DECISION` plus a reproducibly hashed proposal
  for a separate human-controlled decision.
- Reviewer identity and independence are claims inside the record, not facts
  authenticated by S3. The verifier and proposal keep reviewer authentication,
  external-review proof, source certification, profile registration, registry
  writes, timing phase, direction, confidence, ML evidence, Auto Suggest, live
  inference, trading, and MT5 execution false. Directional contribution is
  exactly zero.
- Added private backend POST
  `/api/chakra-lab/timing-profile/external-review/verify`, read-only native
  command `chakra_lab_timing_external_review`, typed frontend transport, and
  the `Review attestation` Chakra Audit tab.
- The tab accepts either the raw S2 bundle or S2's downloaded wrapper plus a
  separately completed attestation. It can download the embedded blank
  attestation template, shows every validation gate and blocked capability,
  warns that reviewer identity is unauthenticated, and exports a proposal only
  when all deterministic gates pass. `Continue to attestation` transfers the
  current verified S2 bundle without another file round trip.
- Canonical status validation now controls seventeen documents and eleven
  audits. It pins the S3 module hash, contracts, exact decision policy,
  human-control boundary, empty registry, proposal semantics, transport, and
  all execution/inference locks.
- Verification on the final source state:
  - S3 engine tests `10/10`;
  - Chakra Lab service tests `20/20`;
  - Chakra Audit workspace tests `8/8`;
  - complete repository Python suite `524/524`;
  - complete frontend suite `100/100`;
  - status tests `40/40`;
  - S3 changed Python scope passes Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check` and focused `rustfmt --check` pass;
  - canonical status validation passes.
- Repository-wide Ruff still reports the same 19 known, pre-existing,
  out-of-scope findings. Repository-wide `cargo fmt --check` remains blocked
  only by the older formatting difference in
  `gann-astro-desk/src-tauri/src/companion_gateway.rs`. The production build
  still reports the existing main-bundle size warning.
- Live endpoint acceptance passed on port `8788`. A complete synthetic review
  produced `READY_FOR_HUMAN_CERTIFICATION_DECISION`; bundle, S1, S2, and
  attestation gates passed; the proposal digest reproduced; reviewer
  authentication, source certification, registry writes, execution, and
  directional contribution remained false/zero.
- Real in-app-browser acceptance passed at
  `http://127.0.0.1:5173/?s1=1` after HMR. The no-input state displayed
  `NO_ATTESTATION`, every missing-input gate, the reviewer-authentication
  warning, source certification blocked, and execution locked. The 1280x720
  page, toolbar, and summary had no horizontal overflow.
- S3 remains unpackaged and no real review bundle, completed attestation,
  authenticated reviewer, source certificate, or registered timing profile is
  shipped. No Windows or Android package was rebuilt.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Timestamped source recovery snapshot:
  `chat_session_backups/session_20260729_102430_sbc_timing_external_review_s3`
  (20 scoped S3 source, test, status, UI, and handoff files; no runtime data).
- T1 directional timing remains intentionally blocked. The next bounded
  milestone must establish a genuinely human-controlled reviewer
  authentication/certification workflow or stop and obtain real external
  evidence; S3 must never silently promote its own proposal.

## Latest Update - 2026-07-29 (Exact Source Verification and Review Bundle S2)

- Completed S2 in source under:
  - report contract
    `SBC_TIMING_PROFILE_SOURCE_BYTE_VERIFICATION_REPORT_V1`;
  - review-bundle contract
    `SBC_TIMING_PROFILE_INDEPENDENT_REVIEW_BUNDLE_V1`;
  - pending-attestation contract
    `SBC_TIMING_PROFILE_EXTERNAL_REVIEW_ATTESTATION_V1`;
  - policy `EXACT_SOURCE_BYTES_AND_UTF8_EXCERPT_PAYLOADS_V1`;
  - classification `SOURCE_PROFILED_EXPERIMENTAL`.
- The deterministic implementation is
  `sbc/timing_profile_source_verification.py`; its audited
  line-ending-independent canonical-text SHA-256 is
  `CFEA080AD3C1A9CAEA4C377178609191FE60B5F525090CFE555D6C53C3547B98`.
  `independent_review_bundle_hash()` is the single reusable implementation of
  the bundle rule
  `CANONICAL_JSON_SHA256_WITH_ATTESTATION_BUNDLE_HASH_BLANK`.
- Froze the boundary and canonical evidence in:
  - `docs/sbc/ADR-0013-source-byte-verification-and-independent-review-bundle.md`;
  - `docs/sbc/S2_ACCEPTANCE.md`;
  - `sbc_timing_source_verification_s2_20260729.md`;
  - `status/audits/sbc_timing_profile_source_verification_s2_20260729.json`.
- S2 requires a candidate and packet that already pass S1. It verifies exact
  whole-file source SHA-256 values and exact UTF-8 excerpt SHA-256 values
  without Unicode, whitespace, or line-ending normalization. Missing, extra,
  empty, malformed, oversized, or mismatched payloads fail closed.
- The backend accepts explicit base64 payloads only and never reads a
  client-supplied path. Limits are 64 MiB per source and 192 MiB combined,
  256 KiB per excerpt and 8 MiB combined. Runtime evidence stays in memory
  and is not persisted.
- A complete pass emits `READY_FOR_INDEPENDENT_REVIEW` and a deterministic
  reviewer bundle containing the exact candidate, packet, verification rows,
  review instructions, and a blank `PENDING` attestation template. Raw source
  bytes and excerpt text are deliberately absent.
- Added private backend POST
  `/api/chakra-lab/timing-profile/source-packet/verify-bytes`, read-only native
  command `chakra_lab_timing_source_verification`, typed frontend transport,
  and the `Verify sources` Chakra Audit tab.
- The UI accepts a local file for each declared source and an exact
  claim-ID-to-excerpt JSON map. It displays coverage before verification,
  deterministic gate results, selected file labels, source/excerpt check
  tables, blocked capabilities, and a downloadable reviewer bundle only
  after a complete pass.
- Byte identity is not page truth or doctrine review. S2 cannot claim printed
  page presence, doctrinal correctness, external review completion, source
  certification, registry permission, timing phase, direction, confidence,
  financial value, ML evidence, Auto Suggest input, live inference, trading,
  or MT5 execution. Directional contribution remains exactly zero.
- Canonical status validation now controls sixteen documents and ten audits,
  pins the S2 module hash, limits, hash semantics, bundle exclusions,
  transport, empty registry, and complete execution/inference guardrails.
- Verification on the final source state:
  - S2 engine tests `9/9`;
  - Chakra Lab service tests `18/18`;
  - Chakra Audit workspace tests `7/7`;
  - complete repository Python suite `508/508`;
  - complete frontend suite `99/99`;
  - status tests `36/36`;
  - S2 changed Python scope passes Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check` and focused `rustfmt --check` pass;
  - canonical status validation passes.
- Repository-wide Ruff still reports the same 19 known, pre-existing,
  out-of-scope findings. Repository-wide `cargo fmt --check` remains blocked
  only by the older formatting difference in
  `gann-astro-desk/src-tauri/src/companion_gateway.rs`. The production build
  still reports the existing main-bundle size warning.
- Live endpoint acceptance passed on port `8788`: synthetic exact evidence
  produced 3 passing source checks, 20 passing excerpt checks, a reproducible
  bundle digest, no embedded evidence text, and `executionAllowed=false`.
- Real in-app-browser acceptance passed at
  `http://127.0.0.1:5173/?s1=1` after HMR. The `Verify sources` no-packet state
  showed the S1/source/excerpt gates as `UNKNOWN`, reviewer bundle blocked,
  page truth unchecked, certification blocked, and execution locked. The
  1280x720 layout had no horizontal overflow and browser warnings/errors were
  empty.
- S2 remains unpackaged, externally unreviewed, source-uncertified,
  financially unvalidated, and execution-locked. No Windows or Android
  package was rebuilt.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260729_094733_sbc_timing_source_verification_s2`.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- T1 directional timing remains intentionally blocked. The next bounded
  milestone is an S3 verifier for a completed independent-review attestation
  and a human-controlled certification proposal. It must not auto-certify,
  write the server-owned registry, or affect inference/trading.

## Latest Update - 2026-07-29 (Timing-Profile Source Packet Readiness S1)

- Completed S1 in source under:
  - packet contract `SBC_TIMING_PROFILE_SOURCE_PACKET_V1`;
  - readiness report `SBC_TIMING_PROFILE_SOURCE_READINESS_REPORT_V1`;
  - policy `CLAIM_HASH_AND_INDEPENDENT_LINEAGE_READINESS_V1`;
  - classification `SOURCE_PROFILED_EXPERIMENTAL`.
- The deterministic implementation is
  `sbc/timing_profile_source_packet.py`; its audited
  line-ending-independent canonical-text SHA-256 is
  `EDEC94327CA7A502D2BAA6C4EEB1A39DFDB8A7FAFE1ECC3DA099E841C606D72B`.
- Froze the design, acceptance boundary, and canonical status evidence in:
  - `docs/sbc/ADR-0012-timing-profile-source-packet-readiness.md`;
  - `docs/sbc/S1_ACCEPTANCE.md`;
  - `sbc_timing_profile_source_packet_s1_20260729.md`;
  - `status/audits/sbc_timing_profile_source_packet_s1_20260729.json`.
- S1 validates a user-supplied candidate plus a declarative source packet in
  memory. It requires exact candidate/profile linkage, canonical hashes,
  page-located excerpts, claim-to-source links, explicit source lineages,
  conflict decisions, and a frozen external-review request.
- Doctrine claims require at least one primary witness plus an independent
  witness across at least two lineages. Research-policy claims require a
  frozen specification claim. The readiness table covers phase span, sectors,
  boundary, asymmetry, repeated exact events, retrograde loops, station
  handling, missing boundaries, unsupported states, eligibility, and
  confidence policy.
- Readiness is deliberately not certification. S1 does not read or OCR source
  files, decide whether an excerpt is doctrinally correct, resolve conflicts,
  register a timing profile, calculate timing phase/direction/confidence,
  create ML notes, feed Auto Suggest, run live inference, produce a trade, or
  enable MT5 execution.
- Added private backend POST
  `/api/chakra-lab/timing-profile/source-packet/readiness`, a dedicated
  read-only native Tauri command, typed frontend transport, and a
  `Source packet` tab in Chakra Audit. The tab works without a compiled linked
  audit.
- The UI supports local JSON source-packet loading and clearing without
  persistence. It shows packet identity/status, candidate linkage, coverage
  for all eleven claim domains, witness/lineage counts, open conflicts,
  external-review state, typed gates, and the complete blocked-capability
  list. With no packet loaded, every candidate-specific gate remains
  explicitly `UNKNOWN`.
- Canonical status validation now controls fifteen documents and nine audits,
  verifies the S1 module hash, exact claim domains and readiness policy,
  requires a valid empty server-owned registry, and prevents source-byte,
  certification, registration, directional, financial, and execution claims.
- Verification on the final source state:
  - S1 engine tests `9/9`;
  - Chakra Lab service tests `15/15`;
  - Chakra Audit workspace tests `6/6`;
  - complete repository Python suite `492/492`;
  - complete frontend suite `98/98`;
  - status tests `32/32`;
  - S1 changed Python scope passes Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check` and focused `rustfmt --check` pass;
  - canonical status validation passes.
- Repository-wide Ruff still reports the same 19 known, pre-existing,
  out-of-scope findings. Repository-wide `cargo fmt --check` remains blocked
  only by the older formatting difference in
  `gann-astro-desk/src-tauri/src/companion_gateway.rs`. The production build
  still reports the existing main-bundle size warning.
- Real in-app-browser acceptance passed against current source at
  `http://127.0.0.1:5173/?s1=1` with the current backend on port `8788`.
  The no-packet state showed `No Packet Loaded`, readiness `NOT READY`,
  source certification `BLOCKED`, all eleven coverage rows and all eleven
  gates `UNKNOWN`, and every downstream capability blocked. The desktop
  readiness tables had no horizontal overflow and browser warnings/errors
  were empty.
- S1 remains unpackaged, financially unvalidated, source-uncertified, and
  execution-locked. No Windows or Android package was rebuilt.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260729_085957_sbc_timing_source_packet_s1`.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- T1 directional timing remains intentionally blocked. The next valid
  milestone is source-byte verification and an exportable independent-review
  packet/workflow for a real candidate; no source result may be invented or
  silently promoted into the server-owned certified registry.

## Latest Update - 2026-07-29 (Fail-Closed SBC Timing-Profile Admission T0)

- Completed T0 in source under:
  - candidate contract `SBC_DIRECTIONAL_TIMING_PROFILE_V1`;
  - report contract `SBC_TIMING_PROFILE_ADMISSION_REPORT_V1`;
  - registry contract `SBC_TIMING_PROFILE_REGISTRY_V1`;
  - admission policy `FAIL_CLOSED_SOURCE_REGISTRY_ADMISSION_V1`.
- The deterministic implementation is `sbc/timing_profile_admission.py`; its
  audited line-ending-independent canonical-text SHA-256 is
  `8D461BD5E670FCEF57E5B474EFB8566A7F0F8ACC23D9E25E7999D1F4783EBD50`.
- Froze the design, acceptance boundary, and canonical status evidence in:
  - `docs/sbc/ADR-0011-timing-profile-admission-gate.md`;
  - `docs/sbc/T0_ACCEPTANCE.md`;
  - `sbc_timing_profile_admission_t0_20260729.md`;
  - `status/audits/sbc_timing_profile_admission_t0_20260729.json`.
- T0 validates only a user-supplied candidate in memory. It requires:
  hash-pinned source evidence; a finite phase span; gap-free exact half-open
  safe/unsafe sectors; explicit directional roles only in safe sectors;
  boundary margin and inclusivity; asymmetry, repeated exact-event,
  retrograde-loop, station-by-body, missing-boundary, and unsupported-state
  policies; activity/coherence/unsafe-share/coverage thresholds; one frozen
  weighted-geometric-mean confidence equation; and strong research/execution
  locks.
- Structural completeness is deliberately not admission. Admission also
  requires an exact canonical SHA-256 match in the server-owned, frozen,
  source-certified registry at
  `status/timing_phase_profile_registry.json`. The shipped registry is valid
  and intentionally empty; the application cannot write it.
- A prospective financial-validation gate, directional engine implementation,
  and execution permission remain separate. T0 calculates no timing phase,
  direction, confidence value, independent vote, ML note, Auto Suggest input,
  live inference, trade output, or MT5 action.
- Added private backend POST
  `/api/chakra-lab/timing-profile/admission`, a dedicated read-only native
  Tauri command, typed frontend transport, and a `Timing gate` tab in Chakra
  Audit. The tab works before a linked audit is compiled.
- The UI supports local JSON candidate loading and clearing without
  persistence. It shows candidate identity/hash, structural readiness,
  source-registry admission, all typed `PASS`/`FAIL`/`UNKNOWN` gates, missing
  paths, directional availability, financial status, execution lock, and the
  complete blocked-capability list.
- Canonical status validation now controls fourteen documents and eight
  audits, checks the registry schema and empty state, verifies the T0 module
  hash and exact guardrails, and requires the T0 capability to remain
  source-implemented and execution-locked.
- Verification on the final source state:
  - T0 engine tests `8/8`;
  - Chakra Lab service tests `13/13`;
  - Chakra Audit workspace tests `5/5`;
  - complete repository Python suite `477/477`;
  - complete frontend suite `97/97`;
  - status tests `28/28`;
  - T0 changed Python scope passes Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check` passes;
  - canonical status validation passes;
  - `git diff --check` passes.
- Repository-wide Ruff still reports the same 19 known, pre-existing,
  out-of-scope findings. Repository-wide `cargo fmt --check` is blocked only
  by the older formatting difference in
  `gann-astro-desk/src-tauri/src/companion_gateway.rs`; the new native command
  is formatter-clean and compiles.
- Real in-app-browser acceptance passed against current source at
  `http://127.0.0.1:5173/` with the current backend on port `8788`. With no
  profile loaded, the UI showed `No Profile Loaded`, structure `NOT READY`,
  source registry `NOT ADMITTED`, directional output `UNAVAILABLE`, financial
  use `BLOCKED`, and execution `LOCKED`. The empty server registry alone
  passed; all candidate-specific requirements remained explicitly `UNKNOWN`.
  The 1280x720 layout had no incoherent overlap and browser warnings/errors
  were empty.
- T0 remains `SOURCE_PROFILED_EXPERIMENTAL`, unpackaged, financially
  unvalidated, and execution-locked. No Windows or Android package was
  rebuilt.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260729_075500_sbc_timing_profile_admission_t0`.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  local and uncommitted.
- Directional timing phase is still intentionally absent. The next valid step
  is external source certification of one complete timing profile followed by
  prospective validation; the application must not invent profile values to
  unblock the phase engine.

## Latest Update - 2026-07-29 (Fixed 0/pi Scalar-Equivalent SBC Visualization F3)

- Completed F3 in source under contracts
  `SBC_FIXED_ZERO_PI_PHASOR_SERIES_V1` and
  `FIXED_ZERO_PI_SCALAR_PARITY_VISUALIZATION_ONLY_V1`, schema `1`.
- The deterministic implementation is `sbc/fixed_phasor.py`; its audited
  line-ending-independent canonical-text SHA-256 is
  `CD739BD60B633C32B74826FFAFBB835FBDE0BC989F41E10E0A217F1895BCB91E`.
- Froze the design, acceptance boundary, and canonical status evidence in:
  - `docs/sbc/ADR-0010-fixed-zero-pi-scalar-equivalent-visualization.md`;
  - `docs/sbc/F3_ACCEPTANCE.md`;
  - `sbc_fixed_zero_pi_phasor_f3_20260729.md`;
  - `status/audits/sbc_fixed_zero_pi_phasor_f3_20260729.json`.
- F3 projects an already-scored P2 scalar without adding evidence:
  - nonnegative values map to angle `0`;
  - negative values map to angle `pi`;
  - magnitude is the absolute scalar value;
  - real component is the original scalar;
  - imaginary component is exactly zero;
  - unknown or missing values remain `UNKNOWN_NOT_PLOTTED`.
- Exact parity is fail-closed: vector real sum must equal the P2 net score,
  vector magnitude sum must equal the P2 true gross score, imaginary sum must
  remain zero, scored/unknown counts must match, links must resolve, guardrails
  must remain strong, and duplicate clusters are rejected.
- This is a scalar-equivalent review visualization only. It is explicitly not
  a physical wave, timing phase, directional phase model, confidence score,
  extra vote, official ML note, Auto Suggest input, live-inference input,
  trading signal, or MT5 execution input.
- Added private backend POST `/api/chakra-lab/fixed-phasor`, a dedicated
  read-only native Tauri command, typed frontend transport, and a linked
  `Fixed phasor` tab in Chakra Audit.
- The linked UI shows the source-ledger identity, interval lineage, exact
  zero/pi vectors, unknown unplotted evidence, parity totals, coherence as a
  descriptive display statistic, validation gates, and the non-directional
  warning. It never silently converts unknown evidence to zero.
- Canonical capability/status validation now registers twelve documents,
  seven audits, and `executionEnabled=false`. The F3 capability is
  source-implemented while directional timing phase remains absent and
  blocked.
- Verification on the final source state:
  - F3 engine tests `6/6`;
  - Chakra Lab service tests `11/11`;
  - Chakra Audit workspace tests `4/4`;
  - complete repository Python suite `462/462`;
  - complete frontend suite `96/96`;
  - status tests `23/23`;
  - F3 changed Python scope passes Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check` and focused `rustfmt --check` pass;
  - canonical status validation passes.
- Default parallel Vitest workers exceeded this laptop's worker-start window;
  the complete suite passed deterministically with one worker and no file
  parallelism. The existing production-build warning for the main JavaScript
  chunk exceeding 500 kB remains and was not hidden.
- A repository-wide Ruff scan still reports 19 known, pre-existing,
  out-of-scope findings in unrelated files. They were not changed or hidden.
- Real in-app-browser acceptance passed against current source at
  `http://127.0.0.1:5173/` with the current backend on port `8790`. Unknown-only
  evidence remained unplotted. A scored scenario then showed exact parity:
  real sum `-2.00`, P2 net `-2.00`, magnitude sum `4.00`, P2 gross `4.00`,
  imaginary sum `0.00`, four scored vectors, and one unknown unplotted vector.
  All expected gates passed, the desktop layout had no incoherent overlap, and
  no browser error-level logs remained.
- F3 remains `SOURCE_PROFILED_EXPERIMENTAL`, unpackaged, financially
  unvalidated, and execution-locked. No Windows or Android package was rebuilt.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260729_065020_sbc_fixed_zero_pi_phasor_f3`.
- Runtime-only SQLite databases, logs, local development launch helpers, and
  Android workspace state remain local and uncommitted.
- Next evidence-safe work must not invent the missing timing/directional phase.
  External Shadbala/Drik certification and prospective financial validation
  remain blocked gates; the next milestone should strengthen one of those
  independent validation paths or add prospective trial scaffolding.

## Latest Update - 2026-07-29 (Signed SBC Audit Catalogs P5)

- Completed P5/Phase 5E in source with:
  - catalog `SBC_AUDIT_PACKAGE_CATALOG_V1`;
  - signature `SBC_AUDIT_CATALOG_SIGNATURE_V1`;
  - bundle `SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1`;
  - verification `SBC_AUDIT_CATALOG_VERIFICATION_V1`;
  - Ed25519 signing under
    `SEALED_PACKAGE_CATALOG_NO_CROSS_AUDIT_INFERENCE_V1`.
- The deterministic implementation is `sbc/audit_catalog.py`; its audited
  line-ending-independent canonical-text SHA-256 is
  `260744F08AC1BB7F44BCF854049459ACFF74E4BBE5A28B215A0A4C6FECE1EEC1`.
- Froze the design, acceptance boundary, and canonical status evidence in:
  - `docs/sbc/ADR-0009-signed-audit-package-catalogs.md`;
  - `docs/sbc/PHASE5E_ACCEPTANCE.md`;
  - `sbc_signed_audit_catalogs_p5_20260728.md`;
  - `status/audits/sbc_signed_audit_catalogs_p5_20260728.json`.
- A catalog accepts one or more unique P4 packages only after each package
  passes complete Chakra -> P1 -> P2 -> P3 -> P4 replay. Members are sorted by
  package identity and preserve their exact sealed P4 payloads.
- Portable SHA-256 identities cover each P4 package, catalog entry, complete
  catalog, signing key, and signature. The Ed25519 signature covers the exact
  canonical catalog bytes.
- The backend generates one local research signing key on first use. Windows
  DPAPI protects the private key for the current user under
  `D:\GannFinancialAstro\app_data\sbc_audit_catalog` by default. Private bytes
  stay outside Git and exports; only the public key and signature leave the
  backend. This is local provenance, not independently attested identity.
- Added `tools/verify_sbc_audit_catalog.py`, an intentionally independent
  integrity verifier that imports no application SBC module. It validates the
  contracts, strict structure, hashes, guardrails, embedded P4 structure, and
  signature, while explicitly reporting semantic replay `NOT_PERFORMED`.
- Imported catalog verification now has two distinct modes:
  - Integrity verifies contracts, hashes, locks, and Ed25519 signature only;
  - Full replay performs integrity checks first, then independently rebuilds
    every embedded P4 recipe and requires semantic replay `PASS`.
- Added private backend routes:
  - POST `/api/chakra-lab/audit-catalog`;
  - POST `/api/chakra-lab/audit-catalog/verify`.
  Native desktop uses dedicated read-only Tauri commands and the supervised
  private sidecar; browser development uses private loopback HTTP.
- Chakra Audit UI now supports a local P5 catalog draft, adding only the
  currently replay-verified P4 package, removing draft members, sealing and
  signing, JSON import/export, integrity-only verification, full replay, and a
  linked Catalog view with package, catalog, and public-key identities.
- The UI and contracts explicitly prohibit cross-package arithmetic, ranking,
  voting, confidence, market direction, official ML notes, Auto Suggest, live
  inference, shadow votes, trade output, and MT5 execution.
- Verification on the final source state:
  - new P5 engine and standalone-verifier tests `6/6`;
  - Chakra Lab service tests `10/10`;
  - Chakra Audit workspace tests `4/4`;
  - complete repository Python suite `452/452`;
  - complete frontend suite `96/96`;
  - status tests `25/25`;
  - P5 changed Python scope passes Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check` and focused `rustfmt --check` pass;
  - packaging environment imports Ed25519 successfully;
  - canonical status validation reports eleven documents, six audits, and
    execution false.
- A repository-wide Ruff scan also reports 19 pre-existing, out-of-scope
  findings in unrelated backend/manual/Android files. They were not changed or
  hidden by this milestone.
- Real in-app-browser acceptance passed at `http://127.0.0.1:5173/`: two
  explicit boundaries compiled through P3; a sealed P4 package replayed
  `PASS`; the replay-verified P4 entered a signed catalog; Integrity reported
  signature/structure `PASS` with semantic replay `NOT_PERFORMED`; Full replay
  then reported semantic replay `PASS`. The 1280-pixel layout had no overlap
  and the browser console had no errors.
- P5 remains `SOURCE_PROFILED_EXPERIMENTAL`, unpackaged, externally
  unattested, financially unvalidated, and execution-locked. No Windows or
  Android package was rebuilt.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260729_002300_sbc_signed_audit_catalogs_p5`.
- Runtime-only SQLite databases, logs, Android workspace state, and the
  DPAPI-protected signing key remain local and uncommitted.

## Latest Update - 2026-07-28 (Reproducible SBC Audit Packages P4)

- Completed P4/Phase 5D in source with
  `SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1`, verification contract
  `SBC_AUDIT_PACKAGE_VERIFICATION_V1`, schema `1`, and policy
  `READ_ONLY_COMPARISON_EXPORT_REPLAY_V1`.
- The deterministic implementation is `sbc/audit_packages.py`; its audited
  line-ending-independent canonical-text SHA-256 is
  `A61DA1821F5EBDF2FF5DFEAF305B87391D4AC26874C40BB79FE4307973577087`
  after exposing the same portable canonicalization helpers to P5.
- Froze the design and acceptance boundary in:
  - `docs/sbc/ADR-0008-reproducible-audit-comparison-packages.md`;
  - `docs/sbc/PHASE5D_ACCEPTANCE.md`;
  - `sbc_reproducible_audit_packages_p4_20260728.md`;
  - `status/audits/sbc_reproducible_audit_packages_p4_20260728.json`.
- One canonical P3 audit is the sole source. The user chooses one baseline and
  one or more comparison intervals. Comparisons are ordered by the source
  audit and report comparison-minus-baseline totals and per-axis/key rows.
  They preserve interval, cell, primary cluster, and source-lineage links.
- Comparison values are explicitly descriptive. They are not bullish,
  bearish, confidence, performance, or trade signals and contribute no vote or
  directional weight.
- Added linked manual research bookmarks for the audit, intervals, cells,
  primary clusters, and validation gates. Bookmark text is annotation-only,
  never evidence, never an official ML note, and cannot reach any inference or
  execution consumer.
- Added canonical JSON export plus an escaped, self-contained HTML report.
  Packages seal the P3 projection, explicit replay recipe, comparisons,
  bookmarks, validation gates, guardrails, and complete package with SHA-256.
- Fixed an acceptance-discovered cross-runtime reproducibility defect:
  JavaScript serializes whole-valued JSON numbers such as `0.0` as `0`.
  Portable P4 hashing now treats those JSON-equivalent representations
  identically while preserving the strict original P3 identity check before
  packaging. A dedicated browser numeric round-trip regression test was added.
- Full replay verification reruns Chakra -> P1 -> P2 -> P3 -> P4 and fails
  closed on altered package content, weakened guardrails, invalid links, or
  replay drift.
- Added backend routes:
  - POST `/api/chakra-lab/audit-package`;
  - POST `/api/chakra-lab/audit-package/verify`.
  Native desktop uses dedicated private Tauri commands and the supervised
  sidecar; browser development uses the private HTTP path.
- Chakra Audit UI improvements:
  - explicit boundary timestamp control inside Audit so switching views cannot
    discard captured research state;
  - duplicate timestamps rejected and the next boundary advances by one hour;
  - linked comparison rows open the correct source interval/cell/cluster;
  - Compare and Package tabs, multiple comparison selection, bookmark editing,
    JSON/HTML export, JSON import, and PASS/FAIL replay;
  - the linked inspector remains visible at a compact 900-pixel desktop width.
- Verification on the final source state:
  - new P4 engine tests `6/6`;
  - Chakra Lab service tests `9/9`;
  - Chakra Audit workspace tests `4/4`;
  - complete repository Python suite `442/442`;
  - complete frontend suite `95/95`;
  - status tests `17/17`;
  - changed Python files pass Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check --locked` passes;
  - canonical status validation reports ten documents, five audits, and
    execution false.
- Real in-app-browser acceptance passed at `http://127.0.0.1:5173/`: two
  explicit IST boundaries were captured, the P3 audit compiled, one linked
  manual bookmark was added, a sealed package was built, descriptive metrics
  displayed without bullish/bearish language, and replay returned:
  `PASS - Full Chakra to P1 to P2 to P3 to P4 replay matched`.
- P4 remains `SOURCE_PROFILED_EXPERIMENTAL`, financially unvalidated,
  directional weight `0.0`, and disconnected from cross-audit arithmetic, FX
  subtraction, phase, confidence, market direction, Auto Suggest, live
  inference, official ML notes, shadow validation, trade output, and MT5.
  No Windows or Android package was rebuilt.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260728_231700_sbc_reproducible_audit_packages_p4`.
- Runtime-only SQLite databases, logs, and Android workspace state remain
  untouched and uncommitted.

## Latest Update - 2026-07-28 (Linked Read-Only SBC Audit Views P3)

- Completed P3/Phase 5C in source with `SBC_LINKED_AUDIT_VIEW_V1`, schema `1`,
  under `LINKED_READ_ONLY_PROGRESSIVE_DISCLOSURE_V1`. The deterministic
  projection is `sbc/audit_views.py`; its audited line-ending-independent
  canonical-text SHA-256 is
  `9E1BE8552B73A103AB12DFB605C34CEE6BDF4F369A4EC79117ABDD7664DB18C0`.
- Froze the P3 boundary in
  `docs/sbc/ADR-0007-linked-read-only-audit-projection.md`. P3 accepts only the
  canonical reconciled Phase 5B ledger, preserves interval/cell/cluster/source
  identities, validates every cross-link, and fails closed on weakened locks,
  broken links, or unreconciled input.
- Added six linked views: Timeline, Ledger, Ray audit, Source lineage,
  Reconciliation, and Validation. The same primary cluster IDs remain visible
  across all dimensions without creating extra votes.
- Ray audit preserves figure-relative Vedha direction only. Every phase angle
  is null, no phase vector exists, and no ray or ledger row contributes market
  direction.
- Explicit unresolved and missing evidence remains visible with null unknown
  magnitude and incomplete coverage. Typed `PASS`, `FAIL`, or `UNKNOWN` gates
  cover timestamp safety, P2 reconciliation, unknown evidence, financial
  validation, timing-phase doctrine, and execution lock.
- Added a backend recomputation path:
  - POST `/api/chakra-lab/audit`;
  - the caller supplies explicit timezone-aware Chakra boundaries, reasons,
    opaque instrument identity, and one terminal end;
  - the backend recomputes each Chakra snapshot, then Phase 5A, Phase 5B, and
    Phase 5C instead of trusting browser-computed evidence.
- Added native Tauri command `chakra_lab_audit`. Native builds use Tauri IPC to
  the supervised private sidecar; browser development uses the private HTTP
  endpoint. Both remain read-only and execution-locked.
- Integrated a separate Audit mode into Chakra Lab without replacing the
  current-moment Board. The audit workspace supports explicit boundary
  capture, compilation, linked row selection, progressive disclosure, source
  inspection, reconciliation, and visible validation blockers.
- Added public `sbc` package exports for the P3 contract, compiler, row models,
  view IDs, and validation states.
- Acceptance and recovery evidence:
  - `docs/sbc/PHASE5C_ACCEPTANCE.md`;
  - `sbc_linked_audit_views_p3_20260728.md`;
  - `status/audits/sbc_linked_audit_views_p3_20260728.json`;
  - capability `sbc_linked_audit_views_v1` in canonical status.
- Verification on the final source state:
  - new P3 compiler tests `6/6`;
  - Chakra Lab service tests `6/6`;
  - focused Chakra/API frontend tests `9/9`;
  - complete repository Python suite `430/430`;
  - complete frontend suite `93/93`;
  - status tests `14/14`;
  - changed Python files pass Ruff;
  - frontend lint and production build pass;
  - native Rust `cargo check --locked` passes;
  - canonical status validation reports nine documents, four audits, and
    execution false.
- Live in-app-browser acceptance passed at `http://127.0.0.1:5173/`: an
  explicit boundary was captured and compiled through the real backend,
  Validation showed expected `PASS` and `UNKNOWN` states, unknown
  `MOTION_REQUIRED` evidence stayed visible, and the browser console had no
  errors. A stale older Flask process initially held port `8788`; it was
  stopped and the clean current backend was verified.
- P3 remains `SOURCE_PROFILED_EXPERIMENTAL`, directional weight `0.0`, and
  disconnected from FX subtraction, phase, confidence, market direction, Auto
  Suggest, live inference, official ML notes, shadow validation, trades, and
  MT5. No Windows or Android package was rebuilt.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260728_195500_sbc_linked_audit_views_p3`.
- Runtime-only SQLite, logs, and Android workspace state remain untouched and
  uncommitted.

## Latest Update - 2026-07-28 (Reconciled SBC Multidimensional Ledger P2)

- Completed P2/Phase 5B in source with
  `SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1`. The implementation is
  `sbc/multidimensional_ledger.py`; its audited line-ending-independent
  canonical-text SHA-256 is
  `81857E4C909F826B5DF65265339CA0E8C9B60D6FAD77A9683FA753DFC0D72750`.
- Froze P0-R5 in
  `docs/sbc/ADR-0006-causal-cluster-and-ledger-deduplication.md`.
  One source lineage inside one atomic interval is one causal fact. Exact
  repeats are deduplicated; different evaluated contribution IDs sharing that
  lineage fail closed rather than being selected or double counted.
- Added stable causal-cluster IDs containing the opaque instrument identity,
  interval, no-lookahead cutoff, snapshot, profile/source lineage, actor,
  target, and exact derivation role. Evaluated nature, multiplier, signed
  units, status, explanation, and unknown reason remain sealed separately by
  the Phase 5A contribution ID.
- Added explicit roles `PRIMARY_EVIDENCE`, `DERIVED_AXIS`,
  `VISUALIZATION_ONLY`, and `NON_VOTING_CONTEXT`. Total, actor, target-layer,
  nature, figure-relative Vedha-direction, and source-lineage cells all
  reference the same primary cluster IDs and never become extra votes.
- Every axis must contain each cluster exactly once and reconcile to the Phase
  5A scalar ledger for favorable, negative adverse, net, true gross, scored,
  unknown, missing, and total counts. Explicit missing evidence receives a
  deterministic lineage and uses visible `UNAVAILABLE` dimension keys instead
  of invented actor/nature/layer/ray facts.
- The compiler fails closed if deduplicated clusters do not reproduce the
  Phase 5A ledger, any axis fails reconciliation, a source guardrail weakens,
  or profile/timestamp/interval invariants drift.
- P2 remains `SOURCE_PROFILED_EXPERIMENTAL` with market directional weight
  `0.0`. Opaque instrument identity is provenance only: base-minus-quote FX
  subtraction, phase, confidence, market direction, Auto Suggest, live
  inference, official ML notes, shadow validation votes, trades, and MT5 all
  remain blocked.
- Acceptance and recovery evidence:
  - `docs/sbc/PHASE5B_ACCEPTANCE.md`;
  - `sbc_multidimensional_ledger_p2_20260728.md`;
  - `status/audits/sbc_multidimensional_ledger_p2_20260728.json`.
- Verification on the final source state: new P2 tests `10/10`; focused
  SBC/Vedha/Chakra/service/FX tests `103/103`; status tests `11/11`; complete
  repository Python suite `418/418`; changed Python files pass Ruff; canonical
  status validation reports eight documents, three audits, and execution false.
- No Windows or Android package was rebuilt and no runtime trading behavior
  changed. P3 may add linked audit views only; P0-R6 comparable FX subtraction
  and P0-R1 through P0-R4 timing/phase/confidence remain separate future gates.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260728_184725_sbc_multidimensional_ledger_p2`.
- Runtime-only SQLite, logs, and Android workspace state remain untouched and
  uncommitted.

## Latest Update - 2026-07-28 (Timestamp-Safe SBC Atomic Intervals P1)

- Completed P1/Phase 5A in source with
  `SBC_ATOMIC_INTERVAL_SERIES_V1` under
  `EXPLICIT_BOUNDARY_STATES_V1`. The implementation is
  `sbc/atomic_intervals.py`; its audited line-ending-independent canonical-text
  SHA-256 is
  `98AE01328946975C08015DFD1D17EED92BF30D0BBB4173BC01AAFAB7D7EDF112`.
- Explicit SBC boundary states now compile into deterministic ordered,
  non-overlapping half-open `[startUtc, endUtc)` intervals. Each interval has
  one timezone-safe evidence cutoff that cannot be later than its start.
  Duplicate timestamps, non-positive duration, and mixed foundation/grid/Vedha
  or guidance profiles fail closed.
- Added canonical SHA-256 identities for source lineage, evaluated
  contributions, boundaries, intervals, and series. Profile identity is deeply
  immutable, source lineage remains separate from evaluated contribution
  identity, and unordered boundary input replays to the same payload and ID.
- The ledger preserves favorable units, negative adverse units, net units, and
  true gross activation as `sum(abs(scored contribution units))`. Unresolved
  and explicitly missing evidence remain counted; unknown magnitude is null
  whenever unknown evidence exists and is `0.0` only when none exists.
- Added `boundary_from_chakra_snapshot` without changing the existing Chakra
  snapshot contract. It verifies all timestamp/read-only/no-execution locks,
  preserves source/profile/witness/citation lineage, and records requested
  actors such as `MOTION_REQUIRED` as missing evidence rather than silently
  excluding them.
- P1 remains `SOURCE_PROFILED_EXPERIMENTAL`, contributes directional weight
  `0.0`, and is blocked from phase, confidence, market direction, Auto Suggest,
  live inference, official ML notes, validation votes, trades, and MT5.
- Acceptance and recovery evidence:
  - `docs/sbc/PHASE5A_ACCEPTANCE.md`;
  - `sbc_atomic_intervals_p1_20260728.md`;
  - `status/audits/sbc_atomic_intervals_p1_20260728.json`.
- Verification on the final source state: new interval tests `11/11`; focused
  SBC/Vedha/Chakra/service/FX tests `93/93`; status tests `8/8`; complete
  repository Python suite `405/405`; changed Python files pass Ruff; canonical
  status validation reports seven documents, two audits, and execution false.
- No desktop or Android package was rebuilt and no runtime trading behavior
  changed. Boundary discovery remains explicit-input only.
- Next phase: P2 should build the versioned multidimensional ledger on top of
  these intervals. Before FX or voting joins it, P0-R5 and P0-R6 must freeze
  causal-cluster deduplication, shared units/cutoffs/profiles, coverage
  mismatch behavior, signed common mode, joint net strength, and true gross
  activation.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260728_172430_sbc_atomic_intervals_p1`.

## Latest Update - 2026-07-28 (SBC/Phase P0 Gap Audit And Frozen Boundary)

- Completed P0 of the revised SBC/phase architecture. This is an architecture
  and gap-audit milestone only; no score, phase, chart, inference, Auto Suggest,
  official ML note, broker, Windows package, or Android behavior changed.
- Added `docs/sbc/SBC_PHASE_P0_GAP_AUDIT_20260728.md` and
  `docs/sbc/ADR-0005-multidimensional-sbc-phase-research-boundary.md`.
  They inventory the working SBC/Vedha/Chakra/FX foundations, reject a duplicate
  implementation, and define P1 as timestamp-safe SBC atomic intervals only.
- Classified the original and revised private PDFs as project specifications,
  not Jyotisha doctrine. Their exact SHA-256 hashes are recorded without
  committing the private PDFs.
- Froze eight unresolved contracts: mixed safe/unsafe timing evidence,
  scale-aware activity versus cancellation, complete timing profiles, one
  typed-gate confidence equation, canonical causal-cluster hashes, comparable
  FX subtraction, duration-aware aggregation, and a linked progressive UI.
- Added machine-readable audit
  `status/audits/sbc_phase_p0_gap_audit_20260728.json` and status entries for
  the not-yet-implemented multidimensional atomic-interval and phase engines.
  The status validator checks the tracked review PDF hash, all eight residual
  corrections, existing evidence paths, the P1 boundary, and every
  no-inference/no-execution lock.
- Verification: canonical status validation passes with six documents and one
  audit; status tests pass `6/6`; focused SBC, Vedha, Chakra, service, and
  instrument-relative FX tests remain `82/82`; changed Python files pass Ruff;
  `git diff --check` reports no whitespace errors.
- Next phase: P1 must implement ordered, non-overlapping half-open SBC atomic
  intervals with one evidence cutoff, source lineage, separate favorable,
  adverse, net, gross, unknown-count, unknown-magnitude, and coverage fields.
  P1 must expose no phase, confidence, market direction, trade, or execution
  field.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260728_153333_sbc_phase_p0_gap_audit`.
- Runtime-only SQLite, logs, and Android workspace state remain untouched and
  uncommitted.

## Latest Update - 2026-07-28 (Priority Experimental Engines Independent Review)

- Completed a full document and implementation-state review of
  `Priority_Experimental_Engines_SBC_Phase_Interference_Codex_Guide-1.pdf`.
- Produced the shareable six-page A4 report
  `output/pdf/Priority_Experimental_Engines_Honest_Review.pdf`, SHA-256
  `4A1A58B1A914397B5E56139F28DA3BD4F9A14C9779046707D6A72C6B4D73B279`.
- Review verdict: proceed with the multidimensional SBC ledger and atomic
  intervals after contract corrections; permit fixed `0/pi` phasors only as a
  non-voting scalar-equivalence and visual audit; keep directional timing-phase
  claims isolated pending frozen profiles, ablation and prospective evaluation.
- Required corrections include true gross forex activation, bounded timing
  phase, explicit count-based unknown handling, one frozen confidence formula,
  and deterministic causal-cluster assignment.
- Current implementation comparison confirms that Chakra/Vedha snapshots and
  isolated base-minus-quote forex research exist, while SBC atomic intervals,
  complete multidimensional time-series contracts and the phase engine do not.
- Verification: `82/82` focused SBC, Vedha, Chakra, service and
  instrument-relative forex research tests passed. No runtime or execution
  capability was changed.

## Latest Update - 2026-07-27 (AVG(ALL) Gann/SBC Visual Study M7 And Windows 0.10.24)

- Added `GANN_AVG_ALL_VISUAL_STUDY_DOSSIER_V1`: an exportable, SHA-256-sealed
  research packet joined at one exact source bar. It combines the immutable M6
  AVG audit, all currently visible user-authored Gann fans (maximum 32), and a
  timestamp-matched Chakra Lab SBC snapshot.
- SBC requests retain all nine supported body positions, while the current
  certified fixed-body actor scope is deliberately limited to `SUN`, `MOON`,
  `RAHU`, and `KETU`. `AVG(ALL)` does not cast Vedha and no motion class is
  invented for other bodies.
- The visual study is guarded at the UI, TypeScript contract, package manifest,
  and tests: research-only, no independent vote, `0.0` directional
  contribution, no live inference, no Auto Suggest, no shadow ledger, no
  official ML notes, and no execution. It contains no outcome labels.
- Added `GANN_AVG_ALL_PROSPECTIVE_FREEZE_CANDIDATE_V1` only as an immutable
  export packet. Its registry state is `export_only_not_registered`; it does
  not alter the existing frozen USDJPY shadow cohort. A future observer trial
  still needs predeclared outcomes, horizons, exclusions, thresholds, an
  immutable manifest, and an untouched future start time.
- Fixed a stale-response race: if the chart/date range/reference location or
  Gann drawings change while the SBC request is pending, the old result is
  discarded rather than shown against new geometry.
- Built Windows candidate `0.10.24` from clean source commit
  `2f223647da9ee98c929d39bd3ee0598dda5b0f8e`. The intermediate M6-only
  `0.10.23` package is superseded and should not be installed.
  - portable executable:
    `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.24-tauri\GannAstroDesk.exe`
    SHA-256 `CEEA6C4A4B7632445B01E56550299B30D2A9018C9C6B699FDE5DD7EA3085A139`;
  - installer:
    `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.24-tauri\Gann Astro Desk_0.10.24_x64-setup.exe`
    SHA-256 `650329D8929D5124986A2FE5D096A91D07E4ABD801F0006F18EB6D493C5315A1`.
- Hashes and Windows File/Product Version `0.10.24` match the generated
  manifest. Native soak passed `44/44` checks with no deferred or failed
  checks, including packaged sidecar startup/recovery, timestamp-safe Chakra
  guardrails, read-only MT5 posture, and execution locks. Physical UI
  acceptance remains pending; no financial validation or execution promotion
  is claimed.
- Verification: M7 focused frontend `8/8`; full desktop frontend `91/91`;
  desktop backend `147/147`; repository Python `390/390`; Rust `18/18`;
  packaging checks `3/3`; status validation `6/6`; frontend lint, targeted
  Python Ruff, and production build passed. The known approximately 534 KiB
  main-bundle advisory remains a separate performance task.
- Evidence:
  `avg_all_visual_study_freeze_m7_20260727.md` and
  `status/audits/windows_avg_visual_study_candidate_0_10_24_20260727.json`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260727_190658_avg_all_visual_study_m7_windows_0_10_24`.
- Next work: physical native UI inspection of the M7 inspector, further
  main-workspace code splitting, and only then an independently predeclared
  future AVG visual-observer trial. Runtime-only SQLite/log/Android state
  remains untouched and must not be committed.

## Latest Update - 2026-07-27 (AVG(ALL) Exact Ingress And Audit Persistence M6)

- Added `GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1` under policy
  `AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1`. Only reliable
  `MEAN_RASHI_INGRESS` brackets are recomputed with the existing
  Raman-sidereal Swiss Ephemeris path and accepted after bisection reaches
  both the one-second and `0.001`-degree residual tolerances.
- The original sampled estimate is always preserved. Lost brackets,
  unreliable R1, malformed inputs, missed tolerances, and work-budget
  exhaustion remain explicit `SAMPLED_FALLBACK` events. R1/state heuristic
  events remain sampled.
- Long ranges no longer fail when more than 64 ingress candidates exist.
  Refinement is bounded to 64 candidates and every excess event remains
  visible as a sampled budget fallback.
- Added immutable `GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1` copies in the
  existing named chart-layout state. The inspector can save, export, repin,
  re-export, and delete audits containing the exact source bar, full member
  profile/audit, and four nearest sampled/refined events.
- Layout restore/import rejects unsafe nested event claims, weakened
  guardrails, malformed member profiles, and oversized history. At most 24
  newest snapshots are retained inside a 224 KiB serialized budget, below
  the backend's existing 256 KiB chart-state limit.
- Safety remains unchanged: coefficient and directional contribution `0.0`,
  no independent vote, no SBC Vedha, no live inference, no Auto Suggest, no
  shadow ledger, no official ML notes, and no execution.
- Local USDJPY H1 measurements over 241 bars refined 2/2 ingress events with
  28 fractional ephemeris evaluations in roughly 0.6 seconds warm and 1.3
  seconds after a service restart. A real snapshot was about 8.1 KiB. The
  lazy inspector chunk remains about 11.4 KiB minified;
  the existing approximately 528 KiB main-chunk advisory remains.
- Verification passes `29/29` focused backend tests, `20/20` focused frontend
  tests, complete desktop suites at `146/146` backend and `87/87` frontend,
  complete repository Python at `389/389`, Python Ruff, frontend Oxlint,
  status validation, and the TypeScript/Vite production build.
- Direct live API validation passed. The in-app browser correctly rejected a
  stale pre-restart contract, but its localhost policy blocked the final
  post-restart visual interaction pass; native-size visual reinspection is
  still pending and is not claimed as passed.
- Capability remains source-only: no Windows/Android package was rebuilt and
  no financial or prospective validation is claimed. Full semantics are in
  `avg_all_ephemeris_refinement_audit_m6_20260727.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260727_160344_avg_all_ephemeris_refinement_audit_m6`.
- Next work: native-size visual reinspection, non-voting Gann/SBC visual
  studies, further main-workspace code splitting, and frozen prospective
  validation before any inference promotion.
- Runtime-only SQLite/log/Android state remains untouched and must not be
  committed: `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-27 (AVG(ALL) Collective Field Inspector M5)

- Added a dedicated lazy-loaded `Planetary Collective Field` inspector for
  the ten-body synthetic `AVG(ALL)` source. It shows synchronized lanes for
  wrapped mean longitude, R1, R2, circular variance, reliability-safe
  velocity, reliability bands, and sampled research events.
- Added deterministic per-bar leave-one-out member audits under
  `GANN_PLANETARY_COLLECTIVE_INFLUENCE_V1`. Each member exposes longitude,
  configured weight, distance from the mean, mean-longitude leverage, R1
  coherence leverage, tempo class, deterministic UI role, and influence rank.
  Unreliable collective means expose null leverage rather than fabricated
  values.
- Inspector hover now drives the price-chart crosshair plus OHLC and RSI
  legends at the same exact source bar. Price-chart hover drives the
  inspector, and clicking either surface pins the timestamp. A keyboard
  timestamp slider and explicit pin/unpin controls provide an accessible
  alternative.
- Opening the inspector temporarily collapses the bottom Events dock to
  preserve chart height and restores its previous state on close. Narrow
  layouts stack the plot and member-audit table rather than overlapping.
- Hardened runtime validation across every historical sample: member count,
  identity, uniqueness, numeric fields, rank validity, and all influence
  guardrails are checked before the desktop accepts the payload.
- Influence roles describe only circular geometry. They remain linked
  descriptors of one `AVG(ALL)` source and cannot become independent votes,
  direction, causality, Jyotisha doctrine, SBC Vedha, live inference, Auto
  Suggest, shadow validation, official ML notes, or execution.
- Verification passes `23/23` focused backend tests, `9/9` focused frontend
  tests, complete desktop suites at `140/140` backend and `80/80` frontend,
  complete repository Python at `383/383`, Python Ruff, frontend Oxlint,
  status validation, and the TypeScript/Vite production build.
- Native-size browser QA at `1280 x 720` passed on the live USDJPY H1
  workspace: two-way hover synchronization, chart click pinning, responsive
  dock behavior, and a clean browser console were confirmed.
- Capability status remains source-only: no Windows/Android package was
  rebuilt, no stable promotion occurred, and no financial validation is
  claimed. Full semantics and limitations are in
  `avg_all_collective_inspector_m5_20260727.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260727_133342_avg_all_collective_inspector_m5`.
- Next milestone: exact-event refinement only where a root can be proven,
  pinned-audit persistence/export, non-voting visual studies, measured
  performance/code splitting, and prospective frozen-policy validation.
- Runtime-only SQLite/log/Android state remains untouched and must not be
  committed: `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-27 (AVG(ALL) Reliability-Safe Motion And Sampled Events M4)

- Extended the auditable ten-body `AVG(ALL)` geometry with
  `GANN_PLANETARY_COLLECTIVE_MOTION_V1`. Reliable mean longitudes are
  shortest-path unwrapped into explicit segments; any unreliable sample
  breaks the segment, and neither motion nor ingress calculations bridge the
  gap.
- Added exact-elapsed-time velocity in degrees/day and interior acceleration
  in degrees/day squared. Uneven bar spacing is handled from Unix timestamp
  differences, one-sample segments remain null, and no smoothing or
  resampling is applied.
- Added `GANN_PLANETARY_COLLECTIVE_EVENT_V1` under
  `AVG_ALL_SAMPLED_EVENTS_V1` for sampled mean-rashi ingress, R1
  low/concentrated-threshold crossings, and cluster-state transitions.
  Forward/backward 30-degree boundary endpoints are regression pinned so an
  ingress is neither dropped nor duplicated.
- Every derived event says `timing.exact=false` and records its two exact
  source-bar timestamps plus interpolation/observation method. Exact
  ephemeris-refined ingress, nakshatra/pada ingress, apparent stations,
  polarisation peaks, and natal contacts remain later milestones.
- Added deterministic event and causal-cluster identities. R1, R2, mean
  longitude, motion, and related events remain linked descriptors of one
  source and cannot be counted as separate directional votes.
- Hardened backend, TypeScript, and runtime response validation. AVG motion
  and events remain research/context only with coefficient and directional
  contribution `0.0`; they cast no SBC Vedha and are barred from live
  inference, Auto Suggest, shadow validation, official ML notes, and
  execution. The desktop rejects a payload that weakens any lock or claims
  exact sampled event timing.
- Verification passes `21/21` focused backend tests, `4/4` focused frontend
  tests, the complete desktop suites at `136/136` backend and `75/75`
  frontend, the complete repository Python suite at `379/379`, Python Ruff,
  frontend Oxlint, status validation, and the TypeScript/Vite production
  build. The existing main-bundle size advisory remains non-blocking.
- Capability status remains implemented in source only: no Windows/Android
  package was rebuilt, no stable promotion occurred, and no financial
  validation is claimed. Full math, event semantics, limitations, and safety
  notes are in `avg_all_collective_motion_events_m4_20260727.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260727_124809_avg_all_motion_events_m4`.
- Runtime-only SQLite/log/Android state remains untouched and must not be
  committed: `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-27 (Auditable AVG(ALL) Collective Geometry V1)

- Added `GANN_PLANETARY_COLLECTIVE_FIELD_V1` for the existing equal-weight
  ten-body `AVG(ALL)` synthetic longitude. The member profile is explicit and
  hash-pinned; Rahu/Ketu remain excluded.
- Added exact-bar R1 concentration, circular variance/deviation, R2
  two-pole/opposition geometry, polarisation axis, state, and longitude
  reliability. Versioned thresholds are identified as display-only research
  heuristics rather than Jyotisha doctrine or market rules.
- Preserved the former circular-mean vector formula behind
  `legacy_circular_mean`; direct/mirror line formulas and all legacy plotted
  values are unchanged. Reliability does not hide or alter a line.
- Added reusable `GANN_RESEARCH_EVIDENCE_PACKET_V1` with explicit direction,
  activation, conflict, and confidence channels. AVG(ALL) is deliberately
  `CONTEXT_ONLY`; all four channels are `NOT_APPLICABLE`, its empirical
  coefficient is `0.0`, and live inference, Auto Suggest, official ML notes,
  and execution remain locked.
- Added a compact Live SR panel summary for AVG state, R1, R2, reliability,
  reliable sample count, and the explicit `legacy lines unchanged` notice.
- Verification passes `12/12` focused backend tests, `7/7` focused frontend
  tests, the complete desktop suites at `127/127` backend and `72/72`
  frontend, the complete repository Python suite at `370/370`, frontend
  lint, status validation, and the TypeScript/Vite production build. The
  existing main-bundle size warning remains non-blocking; the new
  planetary-line panel is already a separate lazy-loaded chunk.
- Native-size browser inspection at `1280 x 720` passed with the Live SR
  drawer showing the compact geometry strip without overlap and no browser
  console warnings/errors. The temporary development services were stopped
  after inspection.
- Capability status records the feature as implemented in source, not yet
  packaged, not promoted, and not financially validated. Full design and
  safety notes are in `avg_all_collective_geometry_v1_20260727.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260727_115215_avg_all_collective_geometry_v1`.
- Runtime-only SQLite/log/Android state remains untouched and must not be
  committed: `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-27 (Visible JHora Kaala Reconciliation And Dynamic Paksha)

- Captured and hash-pinned the visible Jagannatha Hora Kaala Bala breakup for
  all five locked fixtures and seven classical planets: `350/350` required
  rows (`total` plus nine subcomponents). Screenshots and accessibility trees
  are under `status/evidence/jhora_kaala_witness_20260727`.
- Added the reproducible parser/comparator
  `jhora_kaala_witness_comparator.py`, its locked regression tests, the
  350-row local/JHora/PyJHora matrix, JSON summary, and
  `jhora_kaala_reconciliation_20260727.md`. The complete artifact hashes are
  pinned in
  `status/evidence/jhora_kaala_witness_20260727/JHORA_KAALA_EVIDENCE_MANIFEST_20260727.md`.
- Promoted only the independently supported Paksha correction under
  `STRICT_SHADBALA_V9_DYNAMIC_PAKSHA_JHORA_WITNESS_PROVISIONAL`:
  - dynamic Moon benefic/malefic phase classification;
  - doubled Moon Paksha strength;
  - Mercury becomes malefic when it shares a whole sign with a supported
    malefic association.
  Paksha passes `35/35` visible rows with `0.040` virupa mean absolute error
  and `0.124` maximum error at the unchanged `0.5`-virupa tolerance.
- Retained Abda, Masa, Vara, Tribhaga, and Yuddha because each passes
  `35/35`. Hora remains provisional at `33/35`; Nathonnatha at `11/35`;
  Ayana at `13/35`; and visible aggregate Kaala at `4/35`.
- Reconciled JHora's displayed arithmetic: all `10/10` Sun/Moon rows show
  Chesta in the breakup but exclude it from the reported total. This remains
  an explicit total-contribution rule rather than deleting the evidence.
- After the supported changes, top-level local Kaala passes `5/35` with
  `2.763` virupa mean absolute error. Full Shadbala mean absolute error is
  `12.626` virupa versus PyJHora's `71.742`, but full total still passes
  `0/35`; independent JHora Drik remains `9/35`. Hora, Nathonnatha, Ayana,
  aggregate Kaala, non-luminary Chesta, Drik, and full Shadbala therefore
  remain excluded from certified ML/execution.
- Upgraded the certification contract to
  `astro_certification_4_gate_v8_visible_kaala_reconciliation_20260727`.
  Gate 3 now records a separate `visibleKaalaWitness` block and promotes an
  individual subcomponent only after all 35 rows pass. The report explicitly
  notes that its 2026-07-27 evidence addendum reuses the locked capture and is
  not a fresh astronomy calculation.
- Verification in the restricted recovery sandbox: Python compilation
  passed; four pure visible-Kaala comparator assertions and three doctrine
  reconciliation assertions passed after regeneration; certification JSON
  artifacts load successfully; and `git diff --check` passes. The production
  Paksha correction had already passed the focused tests before the sandbox
  changed. A fresh full astronomical suite was not claimed because this
  sandbox lacks `pytest` and a compatible Swiss Ephemeris extension; the last
  complete repository run remains `355/355`.
- Recovery snapshot:
  `C:\Users\ADMIN\Documents\Codex\2026-05-16\this-is-my-private-gann-financial\chat_session_backups\session_20260727_092727_jhora_visible_kaala_reconciliation`.
  Canonical `D:\PycharmProjects` became read-only to the earlier sandbox during
  the run, so the snapshot and recovery commit were first retained in the
  writable workspace. Network and laptop access resumed on 2026-07-27, and the
  JHora visible-Kaala reconciliation commit was successfully pushed to the
  GitHub recovery repository on `origin/master`.
- Runtime-only SQLite/log/Android state remains untouched and must not be
  committed: `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-27 (JHora Doctrine Reconciliation And Luminary Chesta Correction)

- Applied the independently supported Shadbala correction under
  `STRICT_SHADBALA_V8_LUMINARY_CHESTA_TOTAL_EXCLUSION_PROVISIONAL`:
  Sun/Moon Chesta remains visible in component evidence but contributes zero
  to the implemented total because Ayana/Paksha already owns that strength.
  This matches the uploaded Shadbala text (printed pages 81-82) and the locked
  JHora total behavior.
- Added `chesta_total_contribution_virupa` to the deterministic component,
  aggregate, and prefixed event ledgers. Regression tests require visible
  luminary Chesta to remain positive while its total contribution is exactly
  zero.
- Added the reproducible diagnostic:
  `jhora_doctrine_reconciliation.py`, with locked test coverage and outputs:
  - `jhora_doctrine_reconciliation_20260726.md`;
  - `status/evidence/jhora_shadbala_20260723/jhora_local_doctrine_reconciliation_20260726.csv`;
  - `status/evidence/jhora_shadbala_20260723/jhora_drik_candidate_residuals_20260726.csv`;
  - `status/evidence/jhora_shadbala_20260723/jhora_doctrine_reconciliation_20260726.json`.
- Corrected local full-total mean absolute residual against JHora drops from
  about `33.873` to `17.416` virupa, versus PyJHora's `71.742`, but strict
  total agreement remains `0/35` at the frozen `0.5`-virupa tolerance.
  This is an improvement, not certification.
- Local Kaala is closer than PyJHora in all `35/35` locked rows with mean
  absolute residual `7.983` virupa, but only `4/35` rows pass. Case 127 Moon
  and Mercury residuals resemble `90`- and `45`-virupa categorical awards;
  no calendar-lord rule was changed because a visible JHora Kaala
  subcomponent table is still required.
- Named Drik sensitivity profiles were measured without changing production
  doctrine. The current profile remains `9/35`; the strongest tested
  descriptive candidate reaches `20/35` with `2.372` virupa mean absolute
  residual but assumes globally malefic Mercury and still has large errors.
  It remains diagnostic only.
- Regenerated certification under
  `astro_certification_4_gate_v7_independent_jhora_reconciliation_20260726`.
  Gate 3 remains `failed_external_validation`; independent Drik remains
  `failed_independent_validation`; full Shadbala/Drik stays excluded from
  certified ML features and execution. No tolerance was widened.
- Updated doctrine config, source-certification status, reconciliation docs,
  and the hashed JHora evidence manifest. Verification passes Python
  compilation, JSON/YAML loading, `33/33` focused doctrine/certification tests,
  and the full repository suite at `355/355`.
- The full suite exposed one stale experimental-lab assertion that still
  expected the retired `TRAILOKYA_DIPIKA_1972_BLOCKED` label. The assertion now
  checks the existing fail-closed
  `TRAILOKYA_DIPIKA_ARGHYA_FINANCIAL_PROFILE_BLOCKED` name; runtime behavior was
  not changed.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260727_001754_jhora_doctrine_reconciliation`.
- Runtime-only SQLite/log/Android state remains untouched and must not be
  committed: `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-26 (Independent JHora Shadbala/Drik Witness Complete)

- Completed the locked manual Jagannatha Hora `8.0.0.0` witness for five
  fixtures, seven classical planets, six Shadbala components and total:
  `245/245` required rows.
- Pinned executable SHA-256:
  `3DDBE5FB0458AD1F0AD91B002C7EFB8BBA9F08891D3F46190ABA97D570B17908`.
  Locked profile: Drik Siddhanta, Raman ayanamsa, geocentric apparent
  positions, true node, Sripathi/Porphyry houses, ascendant in the middle of
  the first house, apparent rise of the solar tip, weekday at sunrise,
  Parasara special aspects, compound relationships from the relevant
  divisional chart, and default Parasara Hora/Drekkana.
- Saved hashed settings, birth-data dialogs, full chart identity screens,
  Shadbala breakup/summary screenshots and raw copied tables under
  `status/evidence/jhora_shadbala_20260723`.
- Completed ledger:
  `jhora_shadbala_witness_completed_20260726.csv`, SHA-256
  `3DFF36A1415881522F152F690C3856C3F736BEE60ED202F7F5EDD100C055DF42`.
  Validation passes with no missing/duplicate rows, maximum rounded component
  residual `0.01` virupa and maximum rounded Rupa conversion residual `0.29`
  virupa.
- JHora displays Chesta for Sun and Moon but excludes those two displayed
  values from its reported totals. The assembler preserves the display and
  excludes only Sun/Moon Chesta from JHora's internal total consistency check.
- Added reproducible assembler/comparator scripts and tests:
  `jhora_witness_capture_assembler.py`,
  `jhora_witness_comparator.py`,
  `test_jhora_witness_capture_assembler.py`, and
  `test_jhora_witness_comparator.py`.
- The frozen `0.5`-virupa JHora-versus-PyJHora comparison is complete:
  - Sthana `33/35`;
  - Kaala `0/35`;
  - Dig `19/35`;
  - Chesta `12/35`;
  - Naisargika `35/35`;
  - Drik `9/35`;
  - total `0/35`;
  - overall `108 pass / 137 fail`.
- Ran the independent Drik values through
  `astro_function_certification.py`. PyJHora Tier B remains `35/35` for Drik,
  but independent JHora is `9 pass / 26 fail`, so the gate is now honestly
  `failed_independent_validation`, not pending.
- `status/source_certification.json` and generated report
  `astro_function_certification_report_20260726.md` now exclude Drik/full
  Shadbala from certified ML features and execution until explicit
  doctrine/profile reconciliation. No tolerance was widened and no trading
  behavior or execution permission changed.
- Verification: `14 passed` across the JHora protocol, capture assembler,
  comparator and certification tests; Python compilation and JSON validation
  passed.
- Evidence manifest:
  `status/evidence/jhora_shadbala_20260723/JHORA_SHADBALA_EVIDENCE_MANIFEST_20260726.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260726_205738_jhora_independent_witness`.
- Runtime-only SQLite/log/Android state remains untouched and must not be
  committed: `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-23 (Windows 0.10.22 Installed Physical Acceptance)

- The user installed Windows candidate `0.10.22`. The installed binary is
  `D:\Gann Astro Desk\gann-astro-desk.exe` (`15757824` bytes), with file and
  product version `0.10.22`.
- Its raw installed SHA-256 is
  `B7336AEC2FE7A7FB215AF73B312DB5A2237B6D75F244C956B02F3CFAE824B270`.
  Windows changed only the three expected bundle-marker bytes. After
  normalizing those bytes, its SHA-256 is
  `B329325C203A28B8D73244CF83A97BD0AEE6115627DB62F6C0E084D6176C104C`,
  exactly matching the clean release-candidate executable.
- Bundle identity evidence:
  `status/audits/windows_bundle_identity_0_10_22_20260723.json`.
- Direct native UI inspection passed:
  - USDJPY D1 rendered 795 live MT5 bars, 735 transparent aspect windows,
    eight stored SR lines, twelve Live SR lines, RSI 14, drawing tools,
    Bar Replay, layouts and all bottom analysis tabs;
  - Live SR Lab rendered per-planet controls and explicitly remained excluded
    from Auto Suggest, validation and execution;
  - Sarvatobhadra Chakra rendered its 9x9 board, Vedha actors, matched cells,
    actor evidence, cell inspector and guidance ledger;
  - Square of Nine rendered price/time/date/date-time modes plus center,
    increment, size, direction, angle, marking, notes and zoom controls;
  - the aspect inspector exposed recurrence and deterministic evidence, and
    correctly showed Shadbala/Drik as `Certification blocked`;
  - `Review Aspect` opened a separate recurrence window with annotations,
    outcome review, Jyotish/Codex tabs, candle/RSI/synthesis tabs, family
    history and timestamp-safe inference.
- The runtime visibly remained `MT5 data only`, `app execution locked` and
  `Read-only`. No blank canvas or incoherent overlap was observed.
- Physical acceptance audit:
  `status/audits/windows_physical_acceptance_0_10_22_20260723.json`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260723_143028_windows_0_10_22_physical_acceptance`.
- `status/release_status.json`, `status/capability_status.json` and
  `status/source_certification.json` now distinguish installed physical
  acceptance from promotion and source certification. The older ledgers also
  now record the partial independent Trailokya Arghya witness: `11|15` and
  `1/20 = 5%` are independently supported, while `2|18` and score-to-price
  mapping remain unresolved and execution locked.
- Windows `0.10.22` is physically accepted as an installed research
  candidate, but it is not promoted stable. The installer remains unsigned,
  Android `0.10.20` still lacks a complete MOB-01 through MOB-08 evidence set,
  and the Shadbala/Drik and Arghya source gates remain blocked.
- The selected desktop/mobile acceptance pair remains Windows `0.10.19` and
  Android `0.10.20`; this Windows-only acceptance does not silently replace
  the paired mobile test identity.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-23 (Windows Arghya Guard 0.10.22 Candidate)

- Built the clean-source Windows research candidate `0.10.22` from Git commit
  `802c7ee4184c0dfaa6d14c447509e11535adda9b`.
- Installer:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.22-tauri\Gann Astro Desk_0.10.22_x64-setup.exe`
  (`176513415` bytes; SHA-256
  `C975437394A07247A91B5FD44543150AA40653E902F0885DFC6E01D53BEDE79F`).
- Portable executable:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.22-tauri\GannAstroDesk.exe`
  (`15757824` bytes; SHA-256
  `B329325C203A28B8D73244CF83A97BD0AEE6115627DB62F6C0E084D6176C104C`).
- File and product versions are both `0.10.22`; both hashes match
  `release.manifest.json`, whose source is clean and whose source commit is the
  release commit above.
- The packaged backend contains both Trailokya Arghya reconciliation modules,
  both independent transcription CSVs, and the guarded reconciliation YAML.
  The manifest carries the `1/20 = 5%` reference unit while explicitly
  disabling certified price prediction, market mapping, Auto Suggest, live
  inference, official ML-note evidence, validation promotion, and execution.
- Verification passes: frontend lint; 71 frontend tests; 119 backend tests;
  production web build; 18 Rust tests; 13 package-identity/Arghya tests; and
  package module/data inspection.
- The isolated native soak passed all 44 checks with zero failures, zero
  deferrals, clean crash recovery and shutdown, and execution locked:
  `D:\GannFinancialAstro\soak\tauri_0.10.22_20260723_080439\logs\native_soak_report.json`.
- Release audit:
  `status/audits/windows_arghya_candidate_0_10_22_20260723.json`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260723_133952_windows_arghya_candidate_0_10_22`.
- This is the latest Windows research candidate, not a promoted stable build.
  Physical installer/UI acceptance and code signing remain pending. The
  selected desktop/mobile physical acceptance pair remains Windows `0.10.19`
  and Android `0.10.20`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-23 (Windows Arghya Guard 0.10.22 Source)

- Prepared the Windows desktop source release `0.10.22` so the guarded
  Trailokya Arghya independent-witness work is packaged rather than remaining
  source-only.
- The backend sidecar now explicitly includes
  `research_labs.trailokya_arghya` and
  `research_labs.trailokya_arghya.reconcile`. Existing SBC configuration
  collection carries the reconciliation YAML and source tables into the
  packaged backend.
- The release manifest now records reconciliation contract
  `TRAILOKYA_ARGHYA_RECONCILIATION_V1`, profile
  `trailokya_arghya_reconciliation_v1`, and the independently witnessed
  reference unit `1/20 = 5%`.
- Fail-closed package declarations explicitly keep the following disabled:
  certified Arghya price formula, market/instrument mapping, Auto Suggest,
  live inference, official ML-note evidence, validation-ledger promotion, and
  execution.
- Verification passes: frontend lint; 71 frontend tests; 119 backend tests;
  production web build; and 18 Rust tests. The production build retains the
  known non-blocking main-chunk size warning, and the Rust test target retains
  existing companion-client dead-code warnings.
- The clean source checkpoint is being committed before packaging so the
  installer manifest can identify an exact clean Git commit. Installer build,
  package hashes, and physical Windows UI acceptance remain pending in this
  checkpoint.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260723_131116_windows_arghya_guard_0_10_22_source`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-23 (Arghya Independent Witness Gate)

- Audited an independent edited transcription of the 1962 Krishna
  Rau/Choudhary booklet, the already-bounded Agarwal financial chapter, and
  seven public page photographs of a dated 12-14 May 1951 Bombay silver
  example.
- Krishna Rau/Choudhary Table XV independently prints `11|15`, supporting the
  proportional correction candidate for Trailokya's `11|45`. Table XVI also
  independently prints `2|18`, so the second non-proportional value remains
  unresolved. Neither original Trailokya CSV was changed and no correction is
  applied at runtime.
- Krishna Rau/Choudhary and Agarwal independently state that one reference
  price unit is `1/20 = 5%`. The isolated lab can now expose only that unit
  size; for example, `2041 / 20 = 102.05`. It still refuses a target price or
  signal because no certified rule maps an Arghya score to a number of units.
- The 1951 pages show a 12 May silver price of `2041`, a net benefic remainder
  `0|32|15`, and a 14 May price of `2011`. The historical 30-point decrease is
  consistent with benefic/abundance/lower-price direction, but it is not a
  prospective forecast and the linked final score-to-price working page is
  unavailable behind an authenticated Evernote screen.
- Added guarded witness metadata and fail-closed validation to
  `configs/sbc/arghya/trailokya_arghya_reconciliation_v1.yaml` and
  `research_labs/trailokya_arghya/reconcile.py`. Every worked example remains
  `certifies_price_formula: false` and `reusable_prediction_allowed: false`.
- Full audit:
  `docs/sbc/TRAILOKYA_ARGHYA_INDEPENDENT_WITNESS_AUDIT_20260723.md`.
- Private worksheet images and hashes are preserved outside Git at
  `D:\GannFinancialAstro\sources\private\derived\arghya_1951_silver`.
- Direct predicted price, bullish/bearish labels, stocks/FX mapping,
  Auto Suggest, live inference, official ML-note evidence, validation
  promotion, and MT5 execution remain blocked. The next gate is a complete
  page-cited score-to-price calculation plus prospective frozen-rule tests.
- Verification passes: 9 focused Arghya tests; 82 SBC/corpus/local-Jyotish
  tests; 20 status/profile/Arghya tests; reconciliation audit command; and
  `git diff --check`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260723_040453_arghya_independent_witness_gate`.
- No installer was rebuilt. The current Windows candidate remains 0.10.21.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-23 (Trailokya Arghya Double Transcription)

- Completed independent image-controlled transcriptions of the three numeric
  Trailokya Arghya tables from the 1972 Tej Kumar edition and the same-lineage
  2016 Khemraj reprint. Each pass contains 108 cells: 32 relationship/quarter
  values, 36 planetary aspect-house values, and 40 five-class values.
- All 108 comparable cells agree across editions. The fixture distinguishes
  sexagesimal `Viswa|Kala` from house lists, preserving printed house order
  such as Mars `4|8|7` and Saturn `3|10|7`.
- The reconciliation exposes two values printed identically in both editions
  that break their tables' proportional pattern:
  - relationship / three-quarter / malefic-neutral is `11|45`, while the
    three-quarter scaling expectation is `11|15`;
  - five-class / three-quarter / four malefics is `2|18`, while the
    proportional expectation is `2|24`.
  They remain source data and are never silently corrected.
- Added isolated lab `research_labs/trailokya_arghya`. It can calculate only
  the prose-supported direction-only availability index
  `20 + benefic Viswa - malefic Viswa`: above 20 means
  abundance/lower-price pressure and below 20 means
  scarcity/higher-price pressure. It refuses direct predicted prices.
- Direct price, bullish/bearish mapping, stocks/FX, SBC score, RAG official
  evidence, Auto Suggest, live inference, validation-ledger promotion, and MT5
  execution remain blocked. The next gate is an independent page-cited worked
  example resolving both table anomalies and `bhava` versus `mulya`.
- Machine fixtures:
  - `configs/sbc/arghya/trailokya_1972_arghya_pass1.csv`;
  - `configs/sbc/arghya/trailokya_2016_arghya_pass2.csv`;
  - `configs/sbc/arghya/trailokya_arghya_reconciliation_v1.yaml`.
- Full audit:
  `docs/sbc/TRAILOKYA_ARGHYA_DOUBLE_TRANSCRIPTION_20260723.md`.
- Corrected two stale machine guards found during verification:
  `sourceCertified=partial` became the valid locked state `no`, and the
  chart-conditioned source manifest now blocks the specific uncertified
  Trailokya Arghya financial profile rather than incorrectly calling the
  acquired 1972 book missing.
- Verification passes: 108 rows in each CSV; zero cross-edition mismatches;
  exactly two declared scaling anomalies; 79 SBC/corpus/local-Jyotish tests;
  12 status/profile/Arghya tests; structured JSON/YAML/CSV validation; audit
  command; and `git diff --check`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260723_023456_trailokya_arghya_double_transcription`.
- No installer was rebuilt. The current Windows candidate remains 0.10.21.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-23 (Additional SBC Source Cross-reference)

- Audited four additional user-supplied Sarvatobhadra files after the 1972
  *Trailokya Dipika* acquisition. The full classifications and page evidence
  are recorded in
  `docs/sbc/ADDITIONAL_SBC_SOURCE_CROSS_REFERENCE_20260723.md`.
- The 100-page June 2016 Khemraj Shri Krishnadas file is a later reprint of the
  same Pt. Mithalal Vyas *Sarvatobhadra Chakra / Trailokya Dipika* work. It can
  resolve difficult readings across editions but is not an independent
  doctrinal vote and does not certify the Arghya arithmetic.
- The 17-page unattributed 2010 introduction substantially reproduces the
  already page-provenanced Phaladeepika chapter and editor supplement. It is
  registered for duplicate detection and deliberately excluded from the local
  corpus so it cannot inflate confidence through double counting.
- The P.V.R. Narasimha Rao article identifies itself as an extract from the
  December 2000 *Vedic Astrology: An Integrated Approach*. It teaches three
  rays for every planet, unlike both current executable profiles, and is
  indexed only as `reference_commentary`; it does not create a third profile.
- The ChiStaBo 2013 Krishna Rau/Choudhary booklet is an edited derivative of a
  1962 booklet. Only visually checked PDF pages 24-27 and 34, covering the
  twenty-part commodity-price proposal and retrospective iron/steel example,
  are indexed as opt-in `hypothesis_reference` material.
- Private source archives and page-marked derived text remain under
  `D:\GannFinancialAstro\sources\private`. Generated corpus/index artifacts
  remain local and uncommitted. The rebuilt corpus contains 5,224 chunks, and
  smoke retrieval returned P.V.R. only from `reference_commentary` and the
  bounded financial extract only from `hypothesis_reference`.
- No deterministic SBC scoring, Vedha profile, Auto Suggest, live inference,
  official ML-note, validation-ledger, or MT5 execution behavior changed.
  Trailokya Arghya arithmetic remains blocked pending bilingual double
  transcription and an independently sourced worked example.
- Verification passes: source hashes; JSON/YAML/CSV validation; corpus rebuild;
  retrieval-layer smoke checks; 63 SBC/corpus tests; 6 local-Jyotish tests;
  and `git diff --check`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260723_020405_additional_sbc_source_cross_reference`.
- This source-only milestone is not in a rebuilt Windows installer. The current
  packaged candidate remains 0.10.21.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-23 (Trailokya Dipika Source Profile and Stage 1 Translation)

- Acquired and audited the user-supplied 1972 Tej Kumar Book Depot edition of
  *Sarvatobhadra Chakra* with *Trailokya Dipika* commentary by Pt. Mithalal
  Vyas. The original image scan and OCR companion both contain 118 aligned
  pages. The original is the citation authority; the OCR derivative is search
  and translation navigation only.
- Private archive files:
  - `D:\GannFinancialAstro\sources\private\TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN_1EF82899.pdf`
    (`SHA-256 1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`);
  - `D:\GannFinancialAstro\sources\private\TRAILOKYA_DIPIKA_VYAS_1972_OCR_COMPANION_7F220E0F.pdf`
    (`SHA-256 7F220E0FA4523DE4624449E72B62248434760AF0E3C842844ADAEBB3CBB13E9B`).
- Added explicit source profile
  `trailokya_dipika_1972_vedha_guidance_v1`. PDF pages 20-21, printed pages
  4-5, visibly support all three Vedha directions for Sun, Moon, Rahu, and
  Ketu. The existing Phaladeepika-editor single-direction profile is unchanged;
  selection remains explicit and both profiles retain financial/trade locks.
- Extended the Vedha engine to support source profiles with one or several
  fixed rays. Single-ray callers remain backward compatible; multi-ray callers
  use `resolve_actor_directions()` or `evaluate()`.
- Added a private page-provenanced Stage 1 English research translation at
  `D:\GannFinancialAstro\sources\private\derived\TRAILOKYA_DIPIKA_VYAS_1972_ENGLISH_STAGE1_20260723.md`.
  It covers edition/source layers, practical board rules, verses 12-17, and an
  initial map of the Arghya chapter. It is explicitly incomplete and not a
  critical translation.
- The local Jyotish corpus now indexes the Stage 1 file only as opt-in
  `translated_source_reference` material. Ordinary case drafts cannot retrieve
  it. Trailokya/Arghya-specific questions may retrieve it, and the verifier
  rejects claims that it is complete, certified, proven, or execution-ready.
- The financial Arghya chapter is genuinely relevant: it contains planetary
  lord/strength selection, benefic/malefic Viswa tables, a twenty-part price
  conversion, and abundance-versus-scarcity price logic. Numeric conversion is
  withheld because the tables and sign direction have not yet passed bilingual
  double transcription and independent worked-example validation.
- Important semantic guardrail: in the commodity discussion, favorable or
  benefic influence can mean abundance and therefore lower price, while adverse
  influence can mean scarcity and higher price. Favorable must never be mapped
  mechanically to bullish.
- Verification passes: 69 SBC/corpus/local-Jyotish tests; all focused legacy and
  new-profile tests pass. Generated corpus/index files remain local and ignored.
- Full source audit:
  `docs/sbc/TRAILOKYA_DIPIKA_ACQUISITION_AUDIT_20260723.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260723_012900_trailokya_dipika_source_profile`.
- This source milestone is not yet in a rebuilt Windows installer. Current
  packaged candidate remains 0.10.21.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (Live SR Lab and Agarwal Financial Hypothesis Source 0.10.21)

- Audited the desktop planetary-line path end to end. The native source already
  had a functioning live-replotting exploratory line engine; version 0.10.21
  makes it discoverable as **Live SR** beside the existing **SR** chart toggle,
  adds an explicit recalculate command, and shows the calculation time.
- Live SR recalculates on symbol/timeframe artifact changes, new chart-bar
  payloads, visible-range changes, and per-planet parameter changes. It supports
  multiple `n`, `f`, and degree values plus direct/mirror/both modes. Exact UTC
  bar timestamps and the Raman sidereal Swiss Ephemeris contract are retained.
- Safety boundary is unchanged: Live SR is curve-fit research only and cannot
  feed Auto Suggest, live inference, the prospective shadow ledger, validation,
  official ML notes, or MT5 execution. The adjacent **SR** toggle remains the
  corrected artifact's precomputed SR layer.
- Audited both newly supplied Agarwal PDFs against the existing private scan.
  The 191-page file is an exact duplicate of the archived incomplete image
  scan. The 94-page January 2012 ChiStaBo file is an earlier edited derivative,
  not an independent witness; it was archived privately as
  `D:\GannFinancialAstro\sources\private\AGARWAL_MYSTICS_CHISTABO_DERIVATIVE_2012_8AF0045A.pdf`.
- Confirmed by full 15-page visual review that image-scan PDF pages 177-191 are
  consecutive printed pages 180-194, Chapter 20 on financial/share-market
  norms. A page-marked private extract now lives at
  `D:\GannFinancialAstro\sources\private\derived\AGARWAL_FINANCIAL_CHAPTER20_PDF_PAGES_177_191_5644DFC4.txt`.
- The local Jyotish RAG indexes that chapter only as opt-in
  `hypothesis_reference` material. Questions naming Agarwal, Sarvatobhadra,
  financial astrology, share markets, or bullish/bearish market hypotheses may
  retrieve it. It is explicitly excluded from doctrine, deterministic SBC
  scoring, Auto Suggest, inference, official notes, validation, and execution.
- The complete Agarwal profile remains blocked: the scan still omits printed
  pages 46-47, 54-55, 62-63, 133, and 144 and has no verified edition imprint;
  both searchable files are derivatives.
- Verification passes: JSON/YAML/CSV source validation; 13 focused corpus/RAG
  tests; frontend lint; all 71 frontend tests executed and passed across the
  resource-bounded run plus focused rerun; TypeScript/Vite production build;
  117 backend tests; and 18 Rust tests. The existing 524 KB main-bundle warning
  remains a performance follow-up only.
- Packaged clean-source Windows candidate 0.10.21 from commit `bfbf4ad`:
  - portable executable:
    `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.21-tauri\GannAstroDesk.exe`
    (SHA-256 `4D15187D4F250C3F104DF38BBB9916128B0580664E0B10DC1303BB8390D4B636`);
  - installer:
    `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.21-tauri\Gann Astro Desk_0.10.21_x64-setup.exe`
    (SHA-256 `E97E49BC2BBCB7A458C46C5C815D06994EFC7CCCF9A24B334B514219F88CF11D`).
  The manifest hashes match, the executable reports file version 0.10.21, and
  source dirty is false. It is registered as the latest Windows research
  candidate but does not replace the existing formal 0.10.19/Android 0.10.20
  mobile acceptance pair without new physical evidence.
- Full milestone details: `live_sr_agarwal_hypothesis_release_20260722.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_232813_live_sr_agarwal_0_10_21_source`.
- Packaged-candidate recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_235703_live_sr_agarwal_0_10_21_candidate`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (Android Secure Pairing Persistence 0.10.20 Source)

- The physical MOB-05 force-stop check exposed the documented 0.10.19
  memory-only pairing behavior: killing the Android process erased the phone's
  in-memory bearer session and returned the app to pairing.
- Upgraded the Android candidate source to 0.10.20. After the proof-bound
  pairing and pinned HTTPS status check succeed, native Rust now persists the
  encrypted companion session through `android-native-keyring-store` 1.0.0;
  its encryption key is protected by Android Keystore and neither the bearer
  token nor pinned certificate is exposed to the WebView.
- A force-stopped/recreated Android process can restore only a canonical,
  unexpired, execution-locked session whose stored certificate bytes match its
  fingerprint. Expiry, corrupt/oversized storage, unsafe capability claims,
  HTTP 401, WSS revocation, or explicit Disconnect clears memory and protected
  storage and returns to pairing. A desktop restart still invalidates the
  gateway's in-memory sessions by design.
- Added fail-closed persistence/expiry tests and compiled the real
  `aarch64-linux-android` target. Verification passes: frontend lint, 22 test
  files / 71 tests, production build, 18 Rust library tests, focused secure
  session tests 3/3, Android target check, status tests 6/6, and canonical
  status validation. The only `cargo fmt --check` difference is a pre-existing
  formatting line in untouched `companion_gateway.rs`.
- Updated Android architecture/build metadata to declare
  `GANN_ASTRO_ANDROID_SECURE_SESSION_V1` and Keystore-backed persistence. The
  source checkpoint is commit `d608d62` and is pushed to `origin/master`.
- Built the clean-source 0.10.20 arm64 debug APK at
  `D:\GannFinancialAstro\mobile\release_candidate\GannAstroMobile-0.10.20-debug\GannAstroMobile-0.10.20-debug.apk`.
  It is 42,221,537 bytes with SHA-256
  `15A288C8A8FC2688F978F85FAE33BDC4F885EB865E1070AEA438671416D73E9D`.
  Package audit confirms application ID `com.gouravdamade.gannastrodesk`,
  version code 10020/name 0.10.20, arm64 Rust payload, and valid one-signer v2
  Android debug signature. The manifest reports clean source commit `d608d62`,
  Keystore persistence, and `execution_allowed=false`.
- Added `status/audits/android_clean_candidate_0_10_20_20260722.json` and
  selected desktop 0.10.19 plus Android 0.10.20 under plan
  `GANN_MOBILE_ACCEPTANCE_0_10_19_0_10_20_V1`. The 0.10.19 MOB-01 through
  MOB-04 results remain historical and were archived outside Git as
  `mobile_acceptance_results.0_10_19.archived_20260722T165244Z.json` (SHA-256
  `EBDFEBE01280E6B3FB940D94A5FE593B42D7BA3BDA41B30691D66EF2B0C7272D`).
  All physical gates are intentionally pending for the changed Android binary.
- Next physical check: install 0.10.20 over 0.10.19, pair once because the old
  memory-only session cannot migrate, force-stop Android, relaunch, and confirm
  the paired workspace restores without another code. Do not mark MOB-05 pass
  until screenshots or recording bind that behavior to the exact APK hash.
- Candidate/status recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_222546_android_secure_pairing_0_10_20_candidate`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_221052_android_secure_pairing_0_10_20_source`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (MOB-04 Desktop Revocation Pass)

- Recorded MOB-04 `Desktop device revocation` as formal PASS using a controlled
  least-privilege companion session labeled `MOB-04 revocation probe`. Its
  bearer token authenticated successfully before revocation with HTTP 200.
- Captured the desktop `Revoke phone` action, revoked only the controlled test
  session, and immediately replayed its authenticated status request. The
  gateway returned HTTP 401 with `Companion session is expired or revoked` and
  issued no replacement session. The access token was held only in memory,
  cleared after the check, and was not written to evidence.
- The two existing physical-phone sessions remained visible after revocation;
  gateway and Tailscale stayed ready and execution stayed locked. The gateway
  audit independently records pairing start, challenge, controlled pairing,
  and `session_revoked`, all with `executionAllowed=false`.
- Five hash-addressed evidence artifacts remain outside Git under
  `D:\GannFinancialAstro\acceptance\mobile\GANN_MOBILE_ACCEPTANCE_0_10_19_0_10_19_V1\MOB-04-device-revocation-20260722`.
- MOB-01 through MOB-04 now pass. MOB-05 through MOB-08 remain pending;
  promotion and execution remain disabled. The next gate is MOB-05 Android
  process restart, which requires a physical phone force-stop/reopen check.
- Verification: focused mobile/status tests `6/6`, canonical status validation,
  checkpoint assertions, mobile acceptance summary, and `git diff --check`
  pass.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_213722_mobile_mob04_pass_0_10_19`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (MOB-03 Wrong-Proof Lockout Pass)

- Recorded MOB-03 `Wrong-code rejection and lockout` as formal PASS. A live
  local gateway probe submitted five structurally valid pairing requests with
  deliberately invalid cryptographic proofs; every request returned HTTP 403,
  no session envelope was issued, and the fifth failure closed the temporary
  pairing window. The next challenge was refused until pairing is explicitly
  reopened.
- The frozen gateway audit contains exactly five challenge/rejection pairs and
  every event retained `executionAllowed=false`. A post-lock desktop capture
  also confirms that the Rust gateway and Tailscale remained ready, execution
  remained locked, and both legitimate paired phone sessions remained visible.
- Four hash-addressed evidence artifacts remain outside Git under
  `D:\GannFinancialAstro\acceptance\mobile\GANN_MOBILE_ACCEPTANCE_0_10_19_0_10_19_V1\MOB-03-wrong-code-lockout-20260722`:
  the invalid-proof probe, lockout audit excerpt, desktop-state summary, and
  post-lock screenshot.
- MOB-01 through MOB-03 now pass. MOB-04 through MOB-08 remain pending;
  promotion and execution remain disabled. The next gate is MOB-04 desktop
  device revocation.
- Verification: focused mobile/status tests `6/6`, canonical status validation,
  checkpoint assertions, mobile acceptance summary, and `git diff --check`
  pass.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_212305_mobile_mob03_pass_0_10_19`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (MOB-02 Physical Pairing Pass)

- The user supplied three post-pairing phone screenshots showing the connected
  USDJPY workspace, streamed chart data, live market state, companion controls,
  planetary/aspect overlays, and the read-only safety state.
- Recorded MOB-02 `Valid Tailscale pairing` as formal PASS with five
  hash-addressed evidence items: Rust gateway pairing excerpt, exact desktop
  and Android candidate hashes, and all three connected-workspace screenshots.
  The private images remain under
  `D:\GannFinancialAstro\acceptance\mobile\GANN_MOBILE_ACCEPTANCE_0_10_19_0_10_19_V1\MOB-02-pairing-20260722`
  and outside Git.
- MOB-01 and MOB-02 now pass. MOB-03 through MOB-08 remain pending. The portrait
  screenshots are useful preliminary MOB-08 evidence, but landscape/touch and
  blocked-route checks are still required before passing that gate.
- Updated checkpoint:
  `status/audits/mobile_physical_checkpoint_0_10_19_20260722.json`.
  Promotion and execution remain disabled.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_211550_mobile_mob02_pass_0_10_19`.

## Latest Update - 2026-07-22 (MOB-01 Physical Pass)

- The user supplied two physical-phone screenshots. Android App Info visibly
  reports Gann Astro Mobile version `0.10.19`; the first-launch pairing screen
  has usable safe-area spacing and visibly retains `Execution locked`.
- Recorded MOB-01 `Install and first launch` as formal PASS with two
  hash-addressed evidence files in the local result:
  `D:\GannFinancialAstro\acceptance\mobile\mobile_acceptance_results.local.json`.
  The private screenshots remain outside Git. Their hashes and result status
  are preserved in
  `status/audits/mobile_physical_checkpoint_0_10_19_20260722.json`.
- MOB-02 remains pending. The gateway independently proves that pairing and
  streaming succeeded, but the supplied app screenshot was taken before that
  action and visibly says `Laptop not paired`. A post-pairing connected
  workspace screenshot is still required; no false pairing-screen PASS was
  claimed.
- Promotion and execution remain disabled. MOB-03 through MOB-08 also remain
  pending.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_211226_mobile_mob01_pass_0_10_19`.

## Latest Update - 2026-07-22 (Physical Android Pairing Observed)

- The user installed the clean Android `0.10.19` APK and paired it with the
  installed Windows `0.10.19` desktop app through the private Tailscale path.
  Gateway audit evidence independently records `pairing_challenge_issued`,
  `device_paired`, and `stream_connected` for the phone's tailnet address.
  Every event retained `executionAllowed=false`.
- Reconciled an apparent desktop hash mismatch. The installed NSIS executable
  SHA-256 is
  `09A3B42896F365DAE3C7859859D27BDC24AD912D3BAEB9684B9DBE85C0B3FBFC`,
  while the portable candidate SHA-256 is
  `45B7087DDBEC3BC535B0575912ECACB167652FA427703002DEE7BE4BBB64B017`.
  A byte-level comparison found exactly three differing bytes: Tauri changes
  its internal bundle marker from `UNK` to `NSS` in the installer payload.
  After marker normalization, both hashes are identical; no application-code
  difference exists.
- Added `GANN_WINDOWS_BUNDLE_IDENTITY_V1`, a deterministic checker that rejects
  any non-marker binary difference. The physical acceptance plan now pins the
  portable executable, NSIS installer, installed executable, and identity
  audit. Audit:
  `status/audits/windows_bundle_identity_0_10_19_20260722.json`.
- Frozen local pairing evidence is under
  `D:\GannFinancialAstro\acceptance\mobile\GANN_MOBILE_ACCEPTANCE_0_10_19_0_10_19_V1\MOB-02-pairing-20260722`.
  It contains candidate hashes, normalized Windows identity, Tailscale status,
  and the gateway pairing excerpt. MOB-01 and MOB-02 are not formally marked
  PASS yet because their required phone pairing/execution-lock and paired
  workspace screenshots have not been supplied.
- Verification: full repository Python suite `336/336`, all status tests
  `9/9`, canonical status validation, focused Ruff, and `git diff --check`
  pass. This includes marker-only identity acceptance and
  non-marker-difference rejection. Promotion and execution remain disabled.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_210135_mobile_pairing_observed_0_10_19`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (Clean Android 0.10.19 Candidate)

- Built a clean-source arm64 Android debug candidate from Git commit
  `3cabe251338ca143c70530b7fb40739d95c2d55e`. The release manifest reports
  `source_git_dirty=false`, `execution_allowed=false`, and version `0.10.19`.
- Candidate APK:
  `D:\GannFinancialAstro\mobile\release_candidate\GannAstroMobile-0.10.19-debug\GannAstroMobile-0.10.19-debug.apk`.
  SHA-256:
  `A8D4D28F9EB4DC0DC0A672FE6B611019E1A7E4CA6B1EE5D7CB09890FC645F635`;
  size: 41,074,685 bytes.
- Independent APK verification passed: manifest hash match, APK Signature
  Scheme v2, one Android debug signer, package
  `com.gouravdamade.gannastrodesk`, version code `10019`, min SDK 24, target
  SDK 36, and embedded arm64 Rust library. The debug signer remains a
  production-promotion blocker.
- Current-source verification passed: frontend `71/71`, backend `117/117`,
  TypeScript/Vite production build, Oxlint, Rust library `15/15`, strict
  Clippy with warnings denied, Android Rust compilation, and Gradle arm64
  assembly. The checked-in copy fallback handled Windows' expected symlink
  restriction.
- Updated the selected physical acceptance pair to Windows `0.10.19` plus
  clean Android `0.10.19`. The canonical validator now binds release ID,
  version, path, hash, source commit, and dirty state across status documents.
  MOB-01 through MOB-08 remain pending; the phone was offline on Tailscale and
  no physical pass was claimed.
- Candidate audit:
  `status/audits/android_clean_candidate_0_10_19_20260722.json`.
- Milestone report: `android_clean_candidate_0_10_19_milestone_20260722.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_195204_android_clean_candidate_0_10_19`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (Roadmap Status, Mobile Gate, Shadow Audit, SBC Connector)

- Implemented the first fail-closed slices from
  `Gann_Astro_Priorities_Roadmap.pdf` without changing production Auto Suggest,
  MT5, execution, the frozen trial identity, or any doctrine certification.
- Added a canonical machine-readable `status/` layer for release, capability,
  research-trial, source-certification, and mobile-acceptance state. Its
  validator keeps implemented, packaged, physically tested, promoted,
  source-certified, and financially validated as distinct states and validates
  cross-document IDs/hashes. All five documents pass.
- Froze the physical acceptance pair to Windows desktop `0.10.19` and Android
  debug `0.10.17`. Both on-disk artifact hashes match their manifests. Added
  MOB-01 through MOB-08 plus a collector that refuses a physical PASS without
  hash-addressed evidence. Formal physical testing remains pending, and the
  existing Android APK's dirty-source manifest blocks stable promotion even if
  behavior passes.
- Added an independent read-only audit for the live frozen prospective SQLite
  ledger. The database hash and SQLite data version remained unchanged; all
  four immutability triggers, manifest/gate hashes, 14 hash-chain entries, and
  the single cohort passed. Current state is 7 decisions, 7 settled outcomes,
  7 abstentions, 0 watch decisions, and 0 pending outcomes. This is an
  integrity PASS only; financial validation remains false.
- Added isolated connector contract
  `SBC_IMMUTABLE_SNAPSHOT_TARGET_CONNECTOR_V1`. It exact-matches immutable
  Chakra targets only against time-valid human-accepted identities and emits
  `matched_unscored` evidence with `signed_value=None`. Uncertified board
  values, unsafe guardrails, naive times, and future cutoffs are rejected.
  Scoring, contribution emission, Auto Suggest, ML training, MT5 input,
  promotion, and execution remain false.
- Verification: full repository Python suite `333/333`; focused
  instrument-relative SBC `15/15`; status/mobile/audit tests pass; Ruff and
  `git diff --check` pass.
- Full milestone record: `roadmap_priority_foundation_20260722.md`.
- Next external gate: collect MOB-01 through MOB-08 on the physical phone and
  then rebuild Android from a clean source commit. Next SBC gate: accept
  production time-valid identities and page-certify a contribution profile;
  do not create signed contributions before both gates pass.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_183531_roadmap_priority_foundation`.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (Chart-Conditioned Aspect Polarity Milestone 1)

- Implemented the revised chart-conditioned planetary aspect recommendation as
  a new isolated research package at
  `research_labs/chart_conditioned_aspects`. It does not change production
  Auto Suggest, live inference, MT5, SBC, or execution behavior.
- Added versioned organization-chart hypotheses with provenance, effective
  dates, explicit human acceptance, and strict time-accuracy gates. Exact or
  documented exchange-open charts may use houses; date-only and unknown-time
  charts cannot use ascendants, houses, or functional lordship. Multiple
  active chart hypotheses are never selected silently.
- Added provisional profile-driven Parashari functional lordship and a separate
  modern corporate-domain mapping. The same Saturn transit can therefore be
  supportive for a Taurus chart (9th/10th lord, Yogakaraka candidate) and
  adverse for a Cancer chart (7th/8th lord), while the modern financial domains
  never become a hidden price-direction sign.
- Added an immutable, hash-addressed natal graph with conjunction geometry,
  dispositors, lordship, and house occupancy. Configured special Drishti and
  Yoga edges remain disabled. Uncertified exaltation/debilitation and
  friendship tables remain explicitly unknown.
- Added an explicit transit-to-natal adapter. It rejects TT events, missing or
  inferred transit/natal roles, out-of-profile orbs, naive timestamps, and
  retrospective/outcome/P&L/future fields recursively. It does not use the
  legacy sorted-pair role-recovery heuristic.
- Added separate symbolic outputs for direction, activation, and volatility;
  aspect geometry affects activation/volatility only and cannot invent
  direction. Runtime evaluation is bounded, timestamp-safe, rejects future
  dynamic evidence, and preserves opposing evidence as `MIXED` with an explicit
  conflict flag.
- Added an FX bridge that delegates numeric composition to the existing
  instrument-relative SBC base-minus-quote engine and its identity, inversion,
  and triangle invariants. No hidden numeric mapping from categorical chart
  priors was introduced.
- Added five strict JSON schemas, locked YAML profiles, a source manifest,
  doctrine registration
  `chart_conditioned_aspect_polarity_v0_execution_locked`, and 20 focused
  adversarial tests. Full repository verification passed `322/322`; Ruff check
  passed.
- The still-missing complete Agarwal financial edition and *Trailokya Dipika*
  remain explicit blocked source profiles. No substitute doctrine was invented,
  and execution/promotion flags remain false throughout the package.
- Moved the two received implementation specifications off `C:` and
  hash-verified them under `D:\GannFinancialAstro\sources\specifications`:
  - chart-conditioned revised v2 SHA-256
    `7812701297CA1430CF6BC3541F183208A9BC0279719A55600A0C4CD3FE33385D`;
  - SBC/Shadbala/Drik certification guide SHA-256
    `ABFA2F9E7957D92381344B419F2217AC8762E1D90175083F6B8B63305DD00686`.
- Full milestone record:
  `chart_conditioned_aspects_milestone1_20260722.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_155439_chart_conditioned_aspect_m1`.
- Next gate: acquire and page-certify the two missing books as new versioned
  profiles, then register a purged walk-forward experiment with chart-hypothesis
  sensitivity checks, negative controls, and untouched holdout data. Do not
  promote this research layer before those gates pass.
- Existing runtime-only SQLite/log/Android files remain deliberately untouched:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-22 (Agarwal SBC Private-Source Audit)

- Audited two user-provided private PDFs of M. K. Agarwal's `Mystics of
  Sarvato Bhadra Chakra and Astrological Predictions` and registered their
  distinct evidence roles in `configs/sbc/sources.yaml`.
- The 191-page image scan has SHA-256
  `5644DFC44DEC730A26111CA2EEA9C2A005A4291555B71A6A32F0B7B7BCF26050`.
  It preserves printed pages through page 194 but is incomplete: printed pages
  46-47, 54-55, 62-63, 133, and 144 are absent. It also has no extractable
  ISBN, copyright, publisher, or edition statement, and 51 PDF pages have
  little or no usable OCR.
- The 95-page ChiStaBo edited version v3 has SHA-256
  `D93B9B97D2B8C902168FE83C1E6796FE22AD644C55903BA85154D1C6D610E38D`.
  Its own foreword identifies it as an edited derivative of an Internet scan;
  terminology was changed, figures were replicated/redrawn, and bracketed
  editor additions were inserted. It is therefore a search/navigation aid,
  not an independent doctrinal witness.
- Neither private PDF was copied into Git or enabled for executable SBC
  doctrine. Intact image-scan pages may only become evidence after the normal
  page-level visual-certification gates. A complete imprint-bearing edition
  remains pending for whole-book and missing-page certification.
- Both PDFs were moved off the Desktop and hash-verified under
  `D:\GannFinancialAstro\sources\private`; the source register points to those
  private, non-Git locations.
- Added `docs/sbc/AGARWAL_SCAN_AUDIT_20260722.md` and updated
  `docs/sbc/SOURCE_REGISTER.md`. Focused SBC verification passed `53/53`.
- Runtime-only SQLite/log/Android files remain deliberately untouched.

## Latest Update - 2026-07-22 (Aspect Evidence Trace / Windows Candidate 0.10.19)

- Built the versioned Tauri/Rust Windows candidate `0.10.19` from clean source
  commit `79a99005e3c59c95868f1ccea88247e504ab82ce`. The release manifest reports
  `source_git_dirty=false` and status `aspect_evidence_trace_candidate`.
- Portable EXE:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.19-tauri\GannAstroDesk.exe`;
  SHA-256
  `45B7087DDBEC3BC535B0575912ECACB167652FA427703002DEE7BE4BBB64B017`.
- NSIS installer:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.19-tauri\Gann Astro Desk_0.10.19_x64-setup.exe`;
  SHA-256
  `94FA71119210E135B5B941A3F57FD45A74E8856DC427B81E7D20F91176B26041`.
  Both files report product/file version `0.10.19`.
- Release verification passed: backend `117/117`, frontend `71/71` across 22
  files, Oxlint, TypeScript/Vite production build, and packager syntax.
- Native crash/recovery soak passed every assertion with no errors or deferred
  checks, same-port sidecar recovery, execution locked, and no descendant
  survivors:
  `D:\GannFinancialAstro\soak\tauri_0.10.19_20260722_082546\logs\native_soak_report.json`.
- A direct request against the packaged sidecar loaded 47 bundled USDJPY
  aspects and verified `GANN_ASPECT_EVIDENCE_TRACE_V1`, retrospective
  highest/lowest checkpoints, timestamp safety, no look-ahead, and all
  live/shadow/execution locks:
  `D:\GannFinancialAstro\smoke\trace_20260722_083233\packaged_trace_smoke.json`.
- Full release record:
  `D:\PycharmProjects\aspect_evidence_trace_native_release_20260722.md`.
- This is a candidate only. The current stable installation and previous
  candidates were not replaced. Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_140349_aspect_trace_windows_candidate_0_10_19`.
- Runtime-only SQLite/log/Android items remain deliberately untouched and
  outside this release commit.

## Latest Update - 2026-07-22 (Aspect Reaction Checkpoints / Source)

- Extended `GANN_ASPECT_EVIDENCE_TRACE_V1` with the three concise review
  checkpoints requested for each aspect: **Start**, **Highest wick**, and
  **Lowest wick**. The Trace tab still retains every closed in-window bar for
  detailed inspection; the two extrema are shortcuts into that evidence.
- Highest/lowest selection uses the candle high and low among fully closed bars
  whose close is inside the selected aspect window. Each checkpoint includes
  the same SBC, Panchanga, strict Shadbala/Drik, RSI, candle, overlap, and SR
  snapshot as the complete trace.
- Crest/trough selection is deliberately marked `retrospectiveOnly`. Although
  each checkpoint's source data is valid at its own timestamp, knowing that it
  is the final window high or low requires the aspect window to have closed.
  It is therefore unavailable at Start, unavailable during the live window,
  excluded from live inference and the shadow ledger, and execution-locked.
- The reviewer labels these as **Reaction checkpoints / post-window research
  only**, displays the exact high/low wick values, and repeats the
  `chosen after window close` warning inside each checkpoint.
- Verification passed: backend `117/117`, frontend `71/71` across 22 files,
  Oxlint, TypeScript/Vite production build, Python compilation, and direct
  Flask endpoint verification of the extrema and live-consumption lock.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260722_130457_aspect_reaction_checkpoints`.
- Existing runtime-only files remain deliberately outside this source change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-21 (Timestamp-safe Aspect Evidence Trace / Source)

- Added the read-only contract `GANN_ASPECT_EVIDENCE_TRACE_V1` and
  `GET /api/events/<event_id>/evidence-trace`. In **Analyze Aspect**, the new
  **Trace** tab shows the evidence that was knowable at aspect start, each
  fully closed bar inside the aspect window, and the window end. It uses the
  active artifact's saved reference location and displays timestamps in IST.
- Each trace point pre-calculates: closed-bar OHLC/RSI/candle geometry,
  currently overlapping aspects, registered SR state only after the touch bar
  has closed, fixed-body Sarvatobhadra Chakra guidance plus Panchanga, and
  strict Shadbala/Drik components recomputed at that exact timestamp. The
  strength panel includes its current certification status and missing witness
  components instead of claiming a certification that has not been earned.
- SBC does **not** guess variable-planet motion. Fixed-body results can be
  shown; Mars through Saturn remain explicitly `MOTION_REQUIRED` until a
  doctrine-backed motion input is supplied. No instrument-name key is invented
  either. This preserves the existing SBC research boundary.
- The known price result is a separate, visibly labelled **retrospective only**
  record. It never appears in start/window/end evidence, Auto Suggest, live
  inference, shadow ledger, or any MT5 execution route. The trace has hard
  guards for timestamp safety, no look-ahead, outcome separation, and
  execution lock. Manual Gann drawings remain deliberately excluded because a
  user-drawn chart object is not a deterministic backend fact.
- Long windows are capped at 120 displayed closed bars (or an explicit evenly
  spaced sample); each trace is cached per event/timeframe/cap and clears when
  the active dataset changes. This keeps the reviewer responsive without
  changing its evidence meaning.
- Added a reusable transparent candle-bar-record helper and regression tests
  that prove each trace bar closes on or before its own evidence timestamp;
  they also prove the retrospective result remains isolated.
- Verification passed: backend `117/117`, frontend `71/71` across 22 files,
  Oxlint, TypeScript/Vite production build, Python compilation, and a Flask
  test-client request to the new API route. Vite retains its existing advisory
  for the main bundle exceeding 500 kB after minification.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260721_175541_aspect_evidence_trace`.
- This is a source/UI capability only, not a promoted Windows release yet.
  Existing runtime-only files remain intentionally outside this source change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-21 (Live Planetary Line Lab / Source 0.10.18)

- Added the research-only Planetary Line Lab to the desktop chart. Open it with
  `Lines` in the toolbar, enable one or more planets, and supply comma-separated
  `n`, `f`, and `degree` values per planet. Each parameter combination renders
  as an independent overlay, so it is suitable for explicit curve-fitting
  exploration without changing the chart's trading rules.
- The timestamp-safe formula is `f * n * degree + f * longitude` for the
  direct line, with optional mirror form
  `f * n * degree + f * (360 - longitude)`. Planet positions are computed at
  the displayed bar timestamps through the existing Raman sidereal ephemeris.
  Supported groups are Sun through Pluto, Rahu, Ketu, and `AVG(ALL)`; the
  latter is the same circular mean used by the legacy planetary-SR engine.
- Values replot after a short debounce and recalculate when the chart pans,
  zooms, or receives live bars. Rendering uses independent chart series and
  does not alter candlestick autoscaling. Direct lines are solid and mirror
  lines dashed. Configuration is saved with each chart layout.
- Safety limits cap requests at 1,200 bar timestamps, 96 resulting lines,
  100,000 points, and 12 values per parameter. The overlay is deliberately
  excluded from Auto Suggest, live inference, shadow/review ledgers, and any
  execution path. It remains an exploratory visual layer until separately
  validated out of sample.
- Added the backend contract `GANN_EXPLORATORY_PLANETARY_LINE_OVERLAY_V1`,
  `/api/planetary-lines`, frontend overlay state/UI, persisted layout support,
  companion-gateway read allowlist, backend tests, frontend tests, and a
  packaged release soak assertion for formula rendering and execution lock.
- Verification passed: backend `115/115`, frontend `71/71` across 22 test
  files, production frontend build, lint, visual live-overlay checks, and
  packaged Windows soak at
  `D:\GannFinancialAstro\soak\tauri_0.10.18_20260721_054426\logs\native_soak_report.json`.
- Built Windows candidate
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.18-tauri`.
  Portable `GannAstroDesk.exe` SHA-256:
  `56736492C535B5E16F8C02DEE816F195BB40F1AC3EC2F52AE8F2302A50CD0CAC`.
  Installer `Gann Astro Desk_0.10.18_x64-setup.exe` SHA-256:
  `D9E012E7C6B5EAEB1C4C56D4BF38F433C9F566CBE1D47C45F52AB65DAACD9A6D`.
  Stable `0.10.14` remains untouched.
- Existing runtime-only files remain deliberately outside this source change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-21 (Private Tailscale Companion / Source 0.10.17)

- Installed signed Tailscale `1.98.9` under `D:\Tailscale` from the retained
  installer at
  `D:\GannFinancialAstro\installers\tailscale\tailscale-setup-1.98.9-amd64.msi`.
  Installer Authenticode validation passed; SHA-256 is
  `07BCB57D3BD34A0299D98133F1A0091DB2CE66831AA7C100F456E2269A41E665`.
  The Windows service is running in unattended mode with automatic updates and
  incoming tailnet connections enabled.
- Enrolled laptop `Surbhi` and Android `Gaurav's S21 FE` in the private
  `gourav.damade@gmail.com` tailnet. Laptop addresses are `100.67.92.85` and
  `fd7a:115c:a1e0::4938:5c56`; phone addresses are `100.98.3.48` and
  `fd7a:115c:a1e0::8338:331`. Direct laptop-to-phone Tailscale ping passed in
  60 ms without DERP relay. The companion remote address is
  `https://100.67.92.85:9443`; Gann Astro Desk must remain open and Windows must
  stay awake for remote use.
- Added deterministic network-interface discovery to the Rust companion
  gateway. The API and desktop panel now label `tailscale`, `lan`, and
  `loopback` endpoints, prefer a usable Tailscale address, retain the old URL
  list for compatibility, format IPv6 safely, and exclude link-local/APIPA
  addresses. The live packaged audit exposes only usable Tailscale and LAN
  endpoints and keeps execution locked.
- Added the reproducible administrator helper
  `gann-astro-desk\tools\configure_tailscale_companion.ps1`. Windows Firewall
  allows the exact `0.10.17` candidate executable on TCP `9443` only from
  Tailscale `100.64.0.0/10` or the Windows Private local subnet. The stale exact
  public TCP block for the prior candidate is disabled; no broad public rule
  was added.
- Improved Android pairing failures so native Rust TLS/pinning/connection
  errors reach the UI instead of collapsing to `Unable to pair with the
  laptop`. Added `viewport-fit=cover`, dynamic viewport height, Android runtime
  safe-area insets on all edges, top/bottom spacing for the status/navigation
  bars, and bounded wrapping for the `Execution locked` label.
- Built Windows candidate
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.17-tauri`.
  Portable EXE SHA-256:
  `80D19BFF4ADE129A21F883896FC22D49B9E3C3BA35CE6F74640B8B67788E8141`;
  installer SHA-256:
  `2CDB2177E41404C0BAC6CF9733F4EFC0EEA327DD3DEA32A9890D7B6F51B769F9`.
  Stable Windows release `0.10.14` remains untouched.
- Built signed arm64 debug APK
  `D:\GannFinancialAstro\mobile\release_candidate\GannAstroMobile-0.10.17-debug\GannAstroMobile-0.10.17-debug.apk`.
  SHA-256 is
  `75E1126A4F688F3B3376370B5D559CABAA6B35037CB0B4307CA5933227DF9E25`;
  `apksigner` confirms APK Signature Scheme v2 with one Android debug signer.
- Verification passed: frontend `65/65` across 21 files, TypeScript/Vite
  production build, strict Rust Clippy with warnings denied, prior full Rust
  `15/15`, final focused gateway `9/9`, packaged port ownership, clean
  Tailscale-first endpoint audit, live self-signed TLS certificate/SAN
  inspection, expected unauthenticated HTTP 403, direct tailnet ping, APK
  signature inspection, and release hashes. A final all-target Rust test rerun
  was stopped after Windows Firewall prompted for the transient Cargo test
  binary; no release-binary firewall permission was widened.
- Physical Android pairing over the Tailscale address is the only remaining
  release gate. A fresh five-minute code was opened in the desktop panel for
  the user; the code is intentionally not persisted here. Confirm the audit
  records phone remote IP `100.98.3.48`, `device_paired`, and
  `stream_connected`, then repeat with phone Wi-Fi disabled and mobile data
  plus Tailscale enabled. Also visually verify the new top/bottom safe areas on
  the installed `0.10.17` APK.
- Existing runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-20 (Real Rust Companion Gateway / Source 0.10.16)

- Completed the Windows-hosted Rust HTTPS/WSS companion gateway while keeping
  the Python/MT5 backend private on loopback. The gateway binds LAN HTTPS on
  port `9443` (falling back to an ephemeral port if occupied), advertises only
  non-loopback LAN addresses, generates an in-memory self-signed certificate,
  and exposes an explicit read/review/AI/Codex allowlist. Order, trade,
  execution, generation, promotion, scan, and MT5-history mutation routes stay
  blocked; `executionAllowed` remains false in every contract and audit event.
- Implemented one-time pairing and native certificate pinning. Pairing uses a
  12-character code with a five-minute window, 90-second challenge, five-proof
  lockout, HKDF-SHA256 keys, HMAC-SHA256 transcript proof, and a
  ChaCha20-Poly1305 encrypted session envelope. Sessions are memory-only,
  least-privilege, rate-limited, expire after 12 hours, and are revoked on host
  restart. Android keeps the bearer token and pinned certificate in native Rust;
  neither is exposed to WebView JavaScript or persisted to disk.
- Added bounded WSS market-status streaming with sequence numbers, three-second
  updates, lag/resync signaling, five-second send timeout, reconnect backoff,
  and immediate disconnect after revoke/expiry. Proxy requests enforce decoded
  path safety, 8 MiB request and 32 MiB response limits, no redirects, and an
  exact route/capability allowlist. The rotating JSONL audit log lives at
  `D:\GannFinancialAstro\app_data\logs\companion_gateway_audit.jsonl`.
- Added the Windows Companion Mode panel and Android native pairing client. The
  desktop panel displays selectable LAN URL, one-time code, certificate pin,
  execution lock, paired sessions, and revoke controls. The Android shell
  performs the cryptographic handshake natively, restores only its in-memory
  session while the process lives, starts the pinned WSS stream, and returns to
  pairing after revoke, expiry, or an invalid session.
- Built Windows candidate
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.16-tauri`.
  Portable EXE SHA-256:
  `5DE005D46C2E499CCE8D6545283D4214F94B0A5FF929E6D181C3FF0B420FEC96`;
  installer SHA-256:
  `3EA1339A924D1A676045B75300AAFD23EF8D336C8B255D9B98DBC19A2415B51E`.
  Packaged smoke testing confirmed the app remained alive, opened
  `0.0.0.0:9443`, returned HTTPS 403 until Companion Mode was opened, wrote its
  audit trail, and shut down without leaving the gateway or sidecar alive.
- The first packaged smoke run exposed an `axum-server` reactor panic that unit
  tests had masked by already running inside Tokio. Listener conversion now
  occurs inside Tauri's async runtime, and a dedicated non-Tokio startup
  regression test prevents recurrence.
- Built signed arm64 debug APK
  `D:\GannFinancialAstro\mobile\release_candidate\GannAstroMobile-0.10.16-debug\GannAstroMobile-0.10.16-debug.apk`
  with SHA-256
  `D7A2C8FC42CAB6791A5F45DD2A2A32B2FC8F4A61F4F5BA13FD8B0C02597165C0`.
  `apksigner` confirms APK Signature Scheme v2 with the Android debug
  certificate. This remains a debug candidate, not a distributable release.
- Verification passed: frontend `62/62` across 20 files, backend `111/111`,
  Oxlint, TypeScript/Vite production build, Rust formatting, 13 Rust tests
  including real encrypted HTTPS pairing/pinned WSS and non-Tokio startup,
  strict Clippy with warnings denied, Android arm64 Rust compilation, Windows
  native packaging, APK signature inspection, release hashes, and source-diff
  hygiene. Vite retains only its existing advisory for the 516.48 kB main chunk.
- Physical-phone testing is still genuinely pending because
  `adb devices -l` returned no attached device. Do not promote the Android
  candidate until install/launch, pairing over Wi-Fi, chart/review requests,
  stream reconnect, host revoke, restart revocation, background/resume,
  rotation, touch layout, and network-loss recovery pass on real hardware.
- Stable Windows release remains promoted `0.10.14`; candidate `0.10.16` has not
  replaced it. External Shadbala/Drik certification also remains unchanged at
  35/70 comparator checks and 0/35 independent Drik witness checks.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260720_222217_rust_companion_gateway_0116`.
- Existing runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-20 (Android Companion Foundation / Source 0.10.15)

- Added the first Android companion foundation without weakening the Windows
  application boundary. Tauri now exposes a versioned runtime-profile contract:
  Windows remains `managed_sidecar`, while Android is `remote_companion` and
  never starts, stops, or bundles the Python/MT5 sidecar.
- Added versioned companion client, session, and capability contracts. Android
  sessions are memory-only, production pairing requires HTTPS, bearer tokens
  are never persisted, and trade/order execution is explicitly locked. The
  private Flask server remains loopback-only and is not exposed to the LAN.
- Added a mobile pairing/status shell, responsive safe-area layout, authenticated
  companion request routing, browser-development fallbacks, and unit tests for
  runtime detection, session validation, HTTPS enforcement, expiry, and the
  execution lock. The pairing UI targets `/companion/v1/pair`, but pairing is
  intentionally not operational until the separate Rust TLS gateway exists.
- Added an internal authenticated `/api/companion/capabilities` endpoint and a
  deterministic backend capability declaration. It identifies Windows as the
  owner of MT5, Swiss Ephemeris, Shadbala/Drik, rule engines, local LLMs, Codex
  relay, and durable evidence; Android is limited to presentation, touch input,
  chart/review requests, and bounded cache in this phase.
- Split Tauri configuration into shared, Windows, and Android layers. Existing
  Windows resources, sidecar commands, CSP, and NSIS settings remain in the
  Windows overlay; the Android overlay uses the `Gann Astro Mobile` identity and
  HTTPS/WSS network policy.
- Added reproducible D-drive Android tooling and packaging scripts. The build
  uses JDK 17 at `D:\FaceSwapServer\android-tools\jdk\jdk-17.0.19+10`, Android
  SDK/NDK at `D:\FaceSwapServer\android-tools\sdk`, Rust targets under
  `D:\Rust`, and Gradle/temp storage on D:. The packaging fallback copies and
  strips the Rust library when Windows Developer Mode prevents Tauri from
  creating its generated symlink; it does not alter Windows policy.
- Built and independently inspected the arm64 debug pairing shell:
  `D:\GannFinancialAstro\mobile\release_candidate\GannAstroMobile-0.10.15-debug\GannAstroMobile-0.10.15-debug.apk`.
  It is 29,751,085 bytes with SHA-256
  `9E032A411E3C7C79571FA7B26419B383C2D2F7083EA6577E427712D80479F95C`.
  Package inspection confirms `com.gouravdamade.gannastrodesk`, version
  `0.10.15` / code `10015`, min SDK 24, target/compile SDK 36, arm64-v8a only,
  app label `Gann Astro Mobile`, and no sensitive Android permission beyond
  network access plus Android's generated non-exported receiver guard.
- Verification passed against source `0.10.15`: frontend `62/62` across 20
  files, backend `111/111`, Oxlint, Vite/TypeScript production build, 4 Rust
  tests, strict Clippy with warnings denied, Android Rust compilation, Gradle
  arm64 assembly, package metadata inspection, and source-diff hygiene. The
  generated Tauri Android wrapper emits two upstream Android deprecation
  warnings, but the build succeeds.
- No ADB device was connected, so installation, touch/gesture, rotation,
  background/resume, network-loss, and real pairing tests remain pending. The
  next implementation milestone is the Rust HTTPS/WSS companion gateway with
  one-time pairing, certificate trust/pinning, bounded streaming/backpressure,
  revocation, audit logging, and LAN threat tests. Execution must remain locked
  throughout that milestone.
- The stable Windows release remains promoted `0.10.14`; this turn did not
  rebuild or replace it. External Shadbala/Drik certification also remains
  unchanged and visibly failed at 35/70 comparator checks and 0/35 independent
  Drik witness checks.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260720_193026_android_companion_foundation_0115`.
- Existing runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-19 (Timestamp-Safe RSI / Market Synthesis / Stable 0.10.14)

- Added a native Lightweight Charts RSI pane that follows the selected chart
  timeframe. It uses Wilder close RSI, fully closed bars only, period `2-200`,
  default levels `30/50/70`, editable custom levels, a fixed `0-100` scale, and
  explicit warm-up status. Aspect shading remains confined to the price pane.
- Horizontal and vertical drawings are now pane-aware. They may be attached to
  the price pane, RSI pane, or (for vertical lines) all panes. RSI drawings are
  editable, deletable, autosaved with the timeframe layout, and retained across
  layout reloads. Older drawings migrate to the price pane; unsupported tools
  cannot be placed on RSI.
- Added deterministic `GANN_RSI_EVIDENCE_V1` using methodology
  `wilder_smoothed_close_v1`. Analyze Aspect now reports cutoff value/zone,
  event-window minimum/maximum/change, configured-level crossings, warm-up
  availability, and explicit research-only guardrails. A level touch is never
  promoted to proof of reversal.
- Added a separate research-only Market Synthesis coordinator with contracts
  `GANN_LOCAL_MARKET_SYNTHESIS_DRAFT_V1` and
  `GANN_MARKET_SYNTHESIS_PACKET_V1`. It compares isolated deterministic
  astrology, candlestick geometry, and RSI packets while the Local Jyotish
  agent remains the astrology/doctrine specialist.
- The coordinator strips retrospective outcome/return/P&L/MFE/MAE/excursion
  fields and candlestick hindsight, requires specialist cutoffs to agree, asks
  for bullish/bearish/abstain plus closed-bar conditions, and verifies drafts
  for execution language, certainty, and references to excluded inputs. It is
  not consumed by live inference or shadow ledgers and cannot place orders or
  unlock execution.
- Analyze Aspect now has seven compact work areas: Evidence, Notes, Candles,
  RSI, Synthesis, Local Jyotish, and Codex. Browser QA confirmed nonblank H1 and
  H4 RSI panes, correct timeframe recalculation, RSI drawing persistence, and
  graceful local-runtime-unavailable behavior. A prospective occurrence with
  only 7 closed bars correctly failed the 15-bar RSI-14 warm-up instead of
  borrowing future bars.
- Native packaging records the RSI and market-synthesis contracts. Candidate and
  stable-path soaks verified RSI closed-bar guardrails, both feature execution
  locks, same-port sidecar recovery, layout persistence, and child cleanup.
- Verification passed: frontend `56/56` across 18 files, backend `109/109`,
  Oxlint, TypeScript/Vite production build, PowerShell packaging parser checks,
  and source-diff hygiene. The production build retains one informational Vite
  warning because the main chart chunk is 501.74 kB, just over the default
  500 kB advisory threshold; this is not a build failure.
- Packaged and promoted native `0.10.14` from source commit `0036b52`. Stable
  executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`; installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.10.14_x64-setup.exe`.
  Executable SHA-256:
  `2DCC84088CE31EBCE2AC02D7C5EACB35474DD80BDE7FEE6EE17F4D28239C539F`;
  installer SHA-256:
  `F32F20926EA72A3435C208EAB830D24B49E4B26A52493335753B665B1B4E91BD`.
- Candidate native soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.14_20260719_162227\logs\native_soak_report.json`.
  Stable-path soak also passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.14_20260719_163015\logs\native_soak_report.json`.
  Each passed 39/39 checks with zero errors, zero failed checks, same-port crash
  recovery, preserved layout, execution locks, and zero descendant survivors.
  Both are conditional only because Sunday closure deferred the fresh MT5
  time-normalization tick check.
- Archived prior stable:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.13_20260719_215559`.
  Pre-promotion writable-state backup:
  `D:\GannFinancialAstro\app_data_backups\app_data_before_0.10.14_20260719_215559`
  (672 files / 70,705,307 bytes). Both Sarvatobhadra manual files remain beside
  the promoted executable.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260719_220417_rsi_market_synthesis_0114`.
- External Shadbala/Drik certification remains unchanged and visibly failed:
  35/70 comparator checks passed and independent Drik witness 0/35 passed.
  RSI/candlestick/synthesis use remains research-only pending prospective,
  purged out-of-sample validation.
- Runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-19 (Timestamp-Safe Family Evidence / Stable 0.10.13)

- Replaced ambiguous click-cycling as the only overlap affordance with an
  explicit overlap picker. A chart or ribbon selection at a crowded time now
  lists every active aspect independently with its pair/aspect, exact range,
  peak orb, known-prior count, color, `Details`, and `Review` actions. Repeated
  chart clicks still cycle deterministically, but buried events no longer need
  to be discovered by trial and error.
- Added `GANN_RETROSPECTIVE_FAMILY_EVIDENCE_V1`. The selected event receives a
  timestamp-safe historical family summary containing only prior events whose
  full 72-hour touch outcome had already matured before the selected event.
  It reports labeled count, bullish/bearish rate, median 72-hour return, neutral
  median upside/downside excursion, and bias-conditioned MFE/MAE only when the
  sample is sufficiently populated. The contract states
  `liveInferenceConsumed=false`; retrospective labels remain outside the live
  feature allowlist and timestamp-safe decision packet.
- Added evidence-certification badges to Inspector and Analyze Aspect. Geometry
  is identified as a versioned Swiss-Ephemeris/Raman calculation; family rates
  are historical labels; deterministic forex scoring is research-only; and the
  external Shadbala/Drik gate remains visibly failed rather than being implied
  certified. Current gate evidence is 35/70 comparator checks passed, with the
  independent Drik witness at 0/35 passed and all 35 still pending.
- Added a compact zero-centered USD-versus-JPY divergence view. It uses doctrine
  scores when present and raw scores only as a transparent fallback, shows each
  currency separately as supportive/stressful, exposes base-minus-quote score
  and conflict, and never manufactures a score when evidence is absent.
- Inspector and the detached Analyze Aspect window now share the same
  certification, prior-family, and currency-divergence components. Development
  browser QA confirmed the overlap chooser, both detail surfaces, no console
  warnings, and correct timestamp cutoffs. Native QA confirmed the packaged
  735-aspect chart, complete tool rail, event table, inspector, and deterministic
  evidence preview.
- Verification passed: frontend `51/51` across 17 files, backend `99/99`,
  Oxlint, TypeScript/Vite production build, Cargo formatting, 4 Rust tests,
  strict Clippy with warnings denied, Python byte compilation, and source-diff
  hygiene.
- Packaged and promoted native `0.10.13`. Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`; installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.10.13_x64-setup.exe`.
  Executable SHA-256:
  `4788FE9C32BEC3F402D2D8E23FF9E31A185358A41EDF5B60AAECE0D0443EFEBC`;
  installer SHA-256:
  `A6D49AE8A634B901679E10B81A0D7BCB823D93A15BE8BE8EB14126C815EFCEC7`.
- Candidate native soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.13_20260719_133416\logs\native_soak_report.json`.
  Stable-path soak also passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.13_20260719_134340\logs\native_soak_report.json`.
  Each passed 33/33 executed checks with zero errors, same-port crash recovery,
  preserved layout, execution locks, and zero descendant survivors. Both are
  conditional only because Sunday closure deferred the fresh MT5
  time-normalization tick check.
- Archived prior stable:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.12_20260719T134231Z`.
  Pre-promotion writable-state backup:
  `D:\GannFinancialAstro\app_data_backups\app_data_before_0.10.13_20260719T134231Z`
  (672 files / 70,705,307 bytes). Both Sarvatobhadra manual files remain beside
  the promoted executable.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260719_191733_aspect_evidence_certification_0113`.
- Existing runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-19 (Overlapping Aspect Evidence / Stable 0.10.12)

- Replaced the selected-only aspect shading model with a full chart presentation
  layer: every visible aspect now has a translucent full-height window. Overlaps
  remain visible as stacked color, while the selected aspect receives a stronger
  border/fill without hiding neighboring events.
- Aspect windows and ribbons are selectable. In Select mode, repeated clicks at
  the same chart time cycle deterministically through all active overlapping
  aspects instead of leaving buried events unreachable.
- Added a compact aspect hover/focus card with pair/aspect name, exact range,
  duration, peak orb and configured limit, active overlap count, known recurrence
  history, and direct `Details` / `Review` actions.
- `Details` selects the aspect and expands the Inspector evidence immediately.
  `Review` opens the existing Analyze Aspect family workflow so the selected
  occurrence can be compared with its previous variations and annotated.
- Added historical family indexing for the USDJPY transit-to-natal research
  stream. Active/prospective events are deduplicated against the baseline event
  archive and now show useful `known prior / known total` counts rather than
  misleading one-row loaded-range counts.
- Expanded event evidence with implemented Shadbala/Drik fields, family summary,
  and timestamp-safe deterministic forex-pair scoring. New contract:
  `GANN_FX_PAIR_EVIDENCE_V1`.
- Forex evidence is separated explicitly by instrument side. USD and JPY each
  show their own raw/doctrine score, evidence hits, dominant hit, dignity, and
  source reference label; the pair section shows direction, net score, and
  conflict. A source-chart label such as `Tokyo IPO hypothesis` is retained as a
  reference label and is no longer presented as though it were the currency
  name.
- Local Jyotish LLM output remains draft commentary, not a trusted score. The
  deterministic evidence panel and Review workflow remain the source of record;
  this avoids silently promoting speculative benefic/malefic prose into a live
  decision feature.
- Added focused overlap/count/cycling tests plus backend recurrence and
  currency-evidence coverage. Verification passed: frontend `49/49` across 16
  files, backend `98/98`, Oxlint, TypeScript/Vite production build, Cargo
  formatting, and source-diff hygiene.
- Native visual QA in the development WebView confirmed 24 visible aspect
  ribbons produced exactly 24 translucent full-height windows, overlapping
  selection cycled correctly, Details expanded the matching occurrence, and the
  USD/JPY evidence labels and known-history counts were correct.
- Packaged and promoted native `0.10.12`. Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`; installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.10.12_x64-setup.exe`.
  Executable SHA-256:
  `210B44AF8395351CD79BDB16B1062952E038BCF10FB9DA2BB499A0AAE9C02A64`;
  installer SHA-256:
  `37828C10F0A0151C3C3433E736EBE10B62521699057435E3D35C5477F02C2C28`.
- Candidate native soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.12_20260719_113938\logs\native_soak_report.json`.
  Stable-path soak also passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.12_20260719_114416\logs\native_soak_report.json`.
  Both are conditional only because Sunday market closure deferred the live MT5
  time-normalization probe; all local contracts, execution locks, same-port
  crash recovery, layout persistence, and child-process cleanup passed.
- Archived prior stable:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.11_20260719T114322Z`.
  Pre-promotion writable-state backup:
  `D:\GannFinancialAstro\app_data_backups\app_data_before_0.10.12_20260719T114322Z`
  (672 files / 70,696,678 bytes). Both Sarvatobhadra manual files remain beside
  the promoted executable.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260719_171822_overlapping_aspect_evidence_0112`.
- Existing runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-19 (Visible Aspect Ribbons / Stable 0.10.11)

- Fixed the native chart defect reported as "all events not showing on chart".
  The backend returned all 735 D1-filtered events and the DOM contained the
  complete `Astrological aspect windows` group, but WebView2 could paint the
  Lightweight Charts canvas above the auto-stacked aspect layer. Events were
  present and clickable but visually hidden.
- Established an explicit isolated chart stack:
  chart canvas `0`, selected-aspect shade `1`, all aspect ribbons `3`,
  drawings `5`, and annotations `7`. This keeps every enabled ribbon visible
  without placing it above user drawings or annotations.
- Added `src\chartOverlayStack.test.mjs` to lock the CSS stacking contract and
  prevent a future canvas-layer regression.
- Native visual QA confirmed `Aspects 735 - >=1d`, the complete accessible
  aspect-window group, and visible ribbons across the full January-July chart.
- Verification passed: frontend `46/46` across 15 files using serial runs,
  backend `97/97`, Oxlint, TypeScript/Vite production build, Cargo formatting,
  and source-diff hygiene.
- Increased the native soak's cold-start allowance from 90 to 240 seconds.
  The first candidate check exposed a false negative on a resource-constrained
  cold launch; the packaged sidecar was byte-identical to stable and became
  healthy within the corrected bound.
- Packaged and promoted native `0.10.11`. Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`; installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.10.11_x64-setup.exe`.
  Executable SHA-256:
  `364D25D34123E6576D1C12D44660A97D92CE417B946CF35C95CBF350DA83DA4B`;
  installer SHA-256:
  `EA3F47DDDD1DDDB3FB26A9D8C1B58E62E5E8CD7AD49FFDB9A45BFF8983EF7BA3`.
- Candidate soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.11_20260719_093942\logs\native_soak_report.json`.
  Stable-path soak also passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.11_20260719_095108\logs\native_soak_report.json`.
  Both are conditional only because Sunday market closure deferred the live
  MT5 time-normalization probe; all local contracts, safety locks, same-port
  crash recovery, layout persistence, and child-process cleanup passed.
- Archived prior stable:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.10_20260719T094844Z`.
  Pre-promotion writable-state backup:
  `D:\GannFinancialAstro\app_data_backups\app_data_before_0.10.11_20260719T094844Z`
  (672 files / 70,691,058 bytes). Both Sarvatobhadra manual files remain beside
  the stable executable.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260719_152800_visible_aspect_ribbons_0111`.
- Existing runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-19 (English Instrument Initial Converter / Stable 0.10.10)

- Added an advisory English stock/ticker-to-Sarvatobhadra initial converter to
  Chakra Lab under the collapsed optional Context area. It supports two explicit
  interpretation bases: ticker spoken letter-by-letter and English company name.
- The converter shows the Hindi spoken form, first Latin letter, suggested Chakra
  layer/key, Devanagari glyph, match status, and a plain-language explanation.
  It never changes the active instrument context silently; the user must press
  `Use selected key`.
- Conservative examples are locked in tests: `USD` -> `यू-एस-डी` -> `YA / य`,
  `AAPL` -> `ए-ए-पी-एल` -> `E / ए`, `Bharti` -> `BHA / भ`, while ambiguous
  company-name forms such as `Apple` and `Reliance` remain human-review
  suggestions. Unsupported initials fail visibly instead of being forced into a
  Chakra cell.
- New contract: `SBC_ENGLISH_INITIAL_ADVISORY_V1`. The converter remains
  research guidance only and does not create a trading signal, alter Vedha
  scoring, or enable execution.
- Added focused converter tests and Chakra workspace integration coverage.
  Verification passed: frontend `45/45` across 14 files, backend `97/97`,
  Oxlint, TypeScript/Vite production build, Cargo formatting, packaging parser
  checks, native interaction QA, and source-diff hygiene.
- Native visual QA:
  `gann-astro-desk\docs\visual_qa\gann_astro_desk_0110_stock_key_converter_20260718.png`.
  It confirms the collapsed converter, `USD` mapping, and explicit application
  into the Chakra key field.
- Fixed a WebView2 upgrade-cache issue discovered during native QA. Tauri now
  opens the versioned local entrypoint `index.html?v=0.10.10`, and packaging
  fails if the entrypoint version and app version diverge. This preserves the
  existing origin/localStorage while ensuring an upgraded executable requests
  current embedded assets. Contract:
  `GANN_TAURI_VERSIONED_ENTRYPOINT_V1`.
- Packaged and promoted native `0.10.10`. Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`; installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.10.10_x64-setup.exe`.
  Executable SHA-256:
  `8C9EB04EFF6398816D7C8E94C20629BC398A111AA4101E9AA007BB276E3862F2`;
  installer SHA-256:
  `A20603D24806A10184BB4F033E3C553C74600441ED621656C77F370821201659`.
- Stable-path crash/recovery soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.10_20260719_054344\logs\native_soak_report.json`.
  It is a conditional pass only because Sunday market closure defers the MT5
  fresh-time probe. All health, read-only/execution locks, Chakra and
  candlestick contracts, layout persistence, sidecar recovery, diagnostics, and
  descendant-process cleanup checks passed.
- The illustrated Sarvatobhadra manual and quick-start sheet remain beside the
  stable executable with their previously verified hashes.
- Archived prior stable:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.9_20260719T053806Z`.
  Pre-promotion writable-state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.10_promotion_20260719T053806Z`.
- A non-canonical quarantine folder from an interrupted first archive copy is
  retained at
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.9_20260719T053806Z_INCOMPLETE`;
  the environment blocked its recursive removal. It is not used by the app or
  recovery process.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260719_111720_stock_key_converter_0110`.
- Existing runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-18 (Sarvatobhadra Chakra Illustrated User Manual v1.0)

- Created a beginner-focused, illustrated manual for the native Gann Astro Desk
  `0.10.9` Sarvatobhadra Chakra Lab:
  `gann-astro-desk\docs\user_manual\sarvatobhadra_chakra\Gann_Astro_Desk_Sarvatobhadra_Chakra_Manual_v1.0.docx`
  and the matching 15-page PDF.
- Added a standalone six-step quick-start infographic:
  `gann-astro-desk\docs\user_manual\sarvatobhadra_chakra\Sarvatobhadra_Chakra_Quick_Start_v1.0.png`.
- The guide uses an actual native `0.10.9` Chakra Lab screen with numbered
  annotations, a simple Vedha-ray geometry graphic, a worked score example,
  beginner workflows, troubleshooting, a research-note template, accepted
  optional keys, and plain-English definitions.
- The manual documents the executable behavior exactly: fixed and
  motion-dependent ray directions, conditional Moon/Mercury nature, dignity
  multipliers, fail-closed multiplier combinations, matched-cell logic,
  coverage, and the normalized evidence-balance formula.
- Safety boundaries are explicit throughout: the lab is read-only,
  timestamp-safe, no-lookahead, and not financially validated. Its percentage
  is an evidence-balance meter, not probability, confidence, market direction,
  or permission to trade.
- Visual QA inspected all final PDF pages. The first render exposed one blank
  page caused by a Word pagination edge case; the generator was corrected and
  the final PDF is 15 pages with no clipping, overlaps, or blank pages.
- DOCX accessibility audit passes with zero high, medium, or low findings:
  heading hierarchy, image alt text, and table header metadata are present.
  Builder syntax and required safety-text assertions also pass.
- Copied the user-facing PDF and quick-start sheet beside the stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\Sarvatobhadra_Chakra_User_Manual_v1.0.pdf`
  and
  `D:\GannFinancialAstro\release\GannAstroDesk\Sarvatobhadra_Chakra_Quick_Start_v1.0.png`.
  Their SHA-256 hashes are
  `8E27917A7B34BDCF02429C41ADB66CB4061FE0345BA615A2A214D2866901FF94`
  and
  `8C8986AED490AF21BC091189A9806BB9B54C29552061E65D7638B03BCDD6B5F0`
  respectively; both release copies match the repository artifacts.
- The reproducible document/infographic generator is
  `gann-astro-desk\tools\build_sarvatobhadra_manual.py`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_222517_sbc_user_manual_v1`.
- Temporary page-render QA folders remain local and untracked because this
  environment blocks filesystem deletion commands; they are deliberately not
  included in Git or the recovery snapshot.

## Latest Update - 2026-07-18 (Native Tool-Rail Parity / Stable 0.10.9)

- User reported that the Vite development page exposed more sidebar tools than
  the promoted Windows executable. This was confirmed as a stale-package
  problem, not responsive hiding: stable `0.10.8` was built at 01:24 IST,
  before commit `c67be0e` added Bar Replay plus drawing favorites, OHLC magnet
  modes, keep-drawing, drawing groups, and symbol/layout synchronization.
- Bumped React, Tauri, Cargo, and lockfile versions to `0.10.9`. The source
  tool rail now has a regression test locking all seven chart tools plus
  favorites, magnet, keep-drawing, undo, reset, and clear.
- Removed hard-coded `0.10.8` candidate and soak paths. Both packaging scripts
  now derive the version from `src-tauri/tauri.conf.json`.
- Release manifests now record the source Git commit, source dirty state,
  `GANN_CHART_TOOL_RAIL_V2`, and the expected complete chart-tool inventory.
- Pre-package verification passed: frontend `39/39`, backend `97/97`, Oxlint,
  TypeScript/Vite production build, PowerShell parser checks, and Rust
  formatting.
- Packaged, visually verified, and promoted native `0.10.9`. Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`; installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.10.9_x64-setup.exe`.
  The executable SHA-256 is
  `5244DDFC218CC34A37944A58C691DFF90E868142C81B49364AD6569CC8B6E065`;
  installer SHA-256 is
  `8C75088FDAB92504375CBFF68C780DC64693AB6687144D61F61D0A845764F512`.
- Stable manifest records clean source commit
  `e55469121175572fd63c0e17b8c3456119d5b3bc`, 1,467 bundled files, and all
  expected controls: select, crosshair, annotation, horizontal, vertical, Gann,
  Fibonacci, favorites, magnet, keep-drawing, undo, reset, and clear.
- Native visual QA confirms the formerly missing favorites, magnet, and
  keep-drawing controls:
  `gann-astro-desk\docs\visual_qa\gann_astro_desk_0109_tool_rail_parity_20260718.png`.
- The promoted release passed the full crash/recovery soak:
  `D:\GannFinancialAstro\soak\tauri_0.10.9_20260718_155751\logs\native_soak_report.json`.
  It is a conditional pass only because 2026-07-18 is Saturday and the
  MetaQuotes-Demo USDJPY tick is stale. The explicit
  `-AllowClosedMarketMt5Defer` switch deferred only that exact fresh-tick check
  while `executionAllowed=false` and `mt5ReadOnly=true`; all health, security,
  Chakra, candlestick, layout persistence, sidecar recovery, diagnostics, and
  descendant-cleanup checks passed. Without the switch, stale MT5 time still
  fails closed.
- Post-promotion verification also passed the complete frontend suite
  `39/39` with one Vitest worker and final PowerShell parser and diff-hygiene
  checks. The one-worker setting avoids an observed Windows fork-worker
  startup timeout under parallel process pressure; it does not change test
  selection.
- Archived prior stable:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.8_20260718T155519Z`.
  Pre-promotion writable-state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.9_promotion_20260718T155519Z`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_213543_native_tool_parity_0109`.
- Existing runtime-only files remain deliberately outside this change:
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/`.

## Latest Update - 2026-07-18 (Named Formula Diagnostics / Kaala Decomposition)

- This is a research-source and certification milestone, not a native release
  or execution promotion. Stable Gann Astro Desk remains `0.10.8`.
- Upgraded the pinned exporter to
  `GANN_PYJHORA_EXTERNAL_STRENGTH_EXPORT_V3`. In addition to the existing
  210-row six-component matrix, it now emits a 350-row Kaala matrix
  (nine contributors plus total) and 35 rows of shared astronomical/formula
  inputs.
- Upgraded the comparator to `GANN_SHADBALA_COMPONENT_COMPARATOR_V3`. It now
  keeps three questions separate: source-profile end-to-end agreement, Kaala
  subcomponent agreement, and same-input formula agreement.
- End-to-end result at `0.5` virupa is now reported honestly as
  `145 pass / 55 fail / 10 structural N/A` across 210 rows. Sun and Moon
  Chesta are structural N/A because the BPHS source profile assigns
  Ayana/Paksha while PyJHora's epoch-table vector returns zero.
- The shared-input formula matrix passes all `60 / 60` comparable rows:
  Sthana `35/35` and Mars-Saturn epoch-table Chesta `25/25`; ten luminary
  Chesta rows are structural N/A. This demonstrates correct compatibility
  formula implementation when both engines receive the same inputs, without
  promoting PyJHora's variant into production doctrine.
- The Kaala decomposition is `216 pass / 134 fail` over 350 rows. Abda,
  Masa, and Vara pass `35/35`; Tribhaga and Yuddha pass `31/35`; Hora
  `25/35`; Ayana `13/35`; Paksha `6/35`; Nathonnatha `5/35`; total
  remains `0/35`. These residuals now identify time-basis, classification,
  indexing, and source-policy differences instead of hiding them in one
  total.
- Jupiter's permanent 60-virupa Tribhaga rule was already present in the
  committed doctrine. It is now explicitly locked by regression tests rather
  than being mistakenly treated as a missing implementation.
- Added named, diagnostic-only helpers for PyJHora epoch-table linear Chesta
  and same-input Sthana. Production remains the BPHS source profile with the
  Swiss osculating Chesta model.
- Doctrine/config is now
  `strict_shadbala_v7_named_formula_diagnostics_provisional`. The four-gate
  report is
  `astro_certification_4_gate_v6_named_formula_diagnostics_20260718`.
- Gate 3 remains `failed_external_validation`; Gate 4 remains
  `blocked_legacy_dataset`. `certified=false` and `executionAllowed=false`.
  Jagannatha Hora or a reproducible independent worked example remains the
  deciding witness.
- Evidence hashes:
  `pyjhora_external_strength_values_20260718.csv`
  `C5A4E6C60C448AE546D3BD84291C0DB370DEC67919C3BE54E4390FDCCD809FF6`;
  `pyjhora_kaala_subcomponents_20260718.csv`
  `6DDD82E0185649901D8C34C63E829975817547FA6F33A4B5225E51FEAD3A054A`;
  `pyjhora_shadbala_formula_inputs_20260718.csv`
  `077EB4AAC0D048F6555168855986BBD21EDC306AD892073D0E377D561075B9F3`;
  `shadbala_component_residuals_20260718.csv`
  `8263D8C0FC7289584C7FFFA6E42382A76F47F2239A08B72E075147CAF3CB56FF`;
  `shadbala_kaala_subcomponent_residuals_20260718.csv`
  `56DF643DD037D6B43FA490AA0BDB09A9FCDEAE54BB2AD9873CBE35E79AC96326`;
  `shadbala_formula_compatibility_residuals_20260718.csv`
  `5F3B8A164B611C80C7F4DF1FAF89B900EA3EB3CD4194E12346C5A41E33156898`.
- Verification: all `282` Python tests pass; the focused suite passes
  `30/30`; changed-file Ruff and `git diff --check` pass.
- Runtime/user state remains unstaged:
  `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_170739_shadbala_comparator_v3`.

## Latest Update - 2026-07-18 (BPHS Bala Doctrine V6 / Component Reconciliation)

- This is a research-source and certification milestone, not a native release
  or execution promotion. Stable Gann Astro Desk remains `0.10.8`.
- Corrected Saptavargaja under a named BPHS source profile:
  `45/30/20/15/10/4/2` virupa for Moolatrikona through great-enemy,
  degree-bounded D1 Moolatrikona, no exaltation/debilitation double counting,
  and corrected masculine/neutral/feminine Drekkana thirds. A separate named
  PyJHora compatibility profile remains diagnostic only.
- Rebuilt Kaala timing around Swiss Ephemeris apparent sunrise/sunset, a
  visible 06:00/18:00 fallback, the published 1860-01-01 Ahargana anchor
  `714404108573`, sunrise day boundaries, Abda/Masa/Dina lords, and one-hour
  local-mean-time Hora periods. Seven-factor and nine-factor totals are
  emitted separately.
- Corrected Ayana to the 23 degrees 27 minutes source formula and planet
  north/south rules. Graha Yuddha now fails closed when a candidate is
  detected instead of fabricating a zero contribution.
- Replaced speed buckets as production Chesta. Sun uses Ayana, Moon uses
  doubled Paksha, and Mars-Saturn use a source-structured seegrocha versus
  mean/true midpoint model. Motion-state, doubled, and motion-added values
  remain explicitly labeled research diagnostics.
- Corrected the Sun minimum total from `300` to `390` virupa. The locked
  minimum sequence is Sun 390, Moon 360, Mars 300, Mercury 420, Jupiter 390,
  Venus 330, and Saturn 300.
- The PyJHora exporter now selects canonical bounded Dig
  `_dig_bala(method=2)`. The six-component comparator improved from
  `96 pass / 114 fail` to `145 pass / 65 fail`: Sthana `34/35`, Kaala
  `0/35`, Dig `35/35`, Chesta `6/35`, Naisargika `35/35`, and Drik `35/35`.
  The sole Sthana failure is retained as a real divisional-boundary witness:
  a `0.010271` degree Swiss/PyJHora Jupiter difference at the 1889 Tokyo
  fixture crosses D3/D9/D12/D30 boundaries.
- Gate 3 remains deliberately closed at `60 pass / 35 fail / 0 pending`.
  Drik passes `35/35`, but all 35 full totals disagree with PyJHora's
  alternate Kaala/Chesta profile. The independent JHora/worked-example
  witness is still required. Gate 4 is correctly
  `blocked_legacy_dataset`; no corrected Bala value was applied to the
  quarantined historical cases.
- Evidence hashes:
  `pyjhora_external_strength_values_20260718.csv`
  `D7045700B49D2EEC5CCED67D55A932811169EC511FD0173106E1A35153D220AA`;
  `pyjhora_shadbala_components_20260718.csv`
  `9FD387D50D802A6AF4ACCF905A3D171492E149D6FC5FF18EE9F54A0D2B745A50`;
  `shadbala_component_residuals_20260718.csv`
  `F6E05FA5A2DCEF389CE295254DBCE6908AD88380FF586E7782DB38C3E0F49E4E`;
  `shadbala_component_reconciliation_20260718.md`
  `79F10F8E90089A848C5D1DF84F1BC6A187E8D31031581E1265D66FBC344D6E22`.
- The certification report is now
  `astro_certification_4_gate_v5_bphs_bala_reconciliation_20260718`.
  Imported evidence can no longer carry obsolete strict-v4/v5 methodology
  notes into a new run; independent source provenance is retained and
  comparison notes are regenerated once.
- Verification: all `277` Python tests pass; `25` focused doctrine,
  certification, exporter, and comparator tests pass; changed-file Ruff
  checks and `git diff --check` pass.
- Runtime/user state was not staged:
  `gann_aspect_annotations_raman_v2.sqlite`,
  `candlestick_shadow_v3.sqlite`, `logs/`, and `tryapp-android/`.
- Detailed rationale: `shadbala_doctrine_corrections_20260718.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_090312_shadbala_bala_doctrine_v6`.

## Latest Update - 2026-07-18 (Six-Component Comparator / JHora Witness / Experimental Forex Layer)

- This is a verified research-source milestone, not a native release or
  execution promotion. Stable Gann Astro Desk remains `0.10.8`.
- Expanded the pinned PyJHora exporter to contract
  `GANN_PYJHORA_EXTERNAL_STRENGTH_EXPORT_V2`. It now exports all six Shadbala
  components for five fixtures and seven classical planets, producing a
  complete `210`-row component matrix. Export merging is byte-idempotent and
  rejects incomplete or unexpected matrices.
- Added `GANN_SHADBALA_COMPONENT_COMPARATOR_V1`. It compares local Sthana,
  Kaala, Dig, Chesta, Naisargika, and Drik values independently at `0.5`
  virupa tolerance. Current diagnostic result is `96 pass / 114 fail`:
  Naisargika `35/35` and Drik `35/35` pass; Dig passes `25/35`; Chesta passes
  `1/35`; Sthana and Kaala pass `0/35`. The remaining full-total failure is
  therefore localized rather than treated as one opaque discrepancy.
- Component evidence:
  `pyjhora_shadbala_components_20260718.csv` SHA-256
  `281497DBFF577DEB10B2CCCD27270C9F013887791739E83054F524D9C8F8075E`;
  `shadbala_component_residuals_20260718.csv` SHA-256
  `456CAFCD1426468D9F82CF67C1DD60F8819CD86FC7EDA43C73203BDE17CB8525`;
  report `shadbala_component_reconciliation_20260718.md` SHA-256
  `9B48364479D055FAB3DB7C95F3DFB6255F21A663F9FC57C930F1628851517430`.
- The refreshed mixed external-strength ledger now records reconciled Drik and
  recalculated local totals and has SHA-256
  `2EFABCE7624126029BFC8576F4C7F2CF92819CB163D14E0F2F9B6F87A2F2865E`.
  The independent contribution matrix remains unchanged at SHA-256
  `6FDB30D6CF082B017436093F7F81CFB8BAB303A6B7426A4B4414BF47DCA2D342`.
- Installed official Jagannatha Hora `8.0.0.0` locally at
  `D:\GannFinancialAstro\external_validators\jagannatha_hora_8_0\app`.
  Download ZIP SHA-256 is
  `10A291F8F69FBB9AB8C4EC88F8D804FD227FB23E0F4375706C30BA0043B72339`;
  installed `jhora.exe` SHA-256 is
  `3DDBE5FB0458AD1F0AD91B002C7EFB8BBA9F08891D3F46190ABA97D570B17908`;
  installed `swedll32.dll` SHA-256 is
  `D56BA3A6158FCEC3921774B5C9FCC533374413D7B77CDBC6B83FFA082D260A69`.
  The official installer is unsigned, as warned by its publisher.
- Added `GANN_JHORA_SHADBALA_WITNESS_V1` and a locked `245`-row worksheet:
  five fixtures x seven planets x six components plus total. It pins the JHora
  executable hash and chart settings, and fails closed on duplicate, unknown,
  mixed-settings, unsourced, or unreviewed entries. Template
  `jhora_shadbala_witness_template_20260718.csv` SHA-256 is
  `BA616F3EF35F3D3F914A9D113E6DA1559E07C8326F7566A28A8BB3493471DE9B`.
- JHora witness status remains honestly pending. Installation is not
  certification: JHora exposes no trusted batch export in this setup, and UI
  automation libraries are not installed. Values must be captured visibly
  under the locked settings with screenshots/evidence and reviewer metadata.
- Added the isolated `research_labs/instrument_relative_sbc` package from the
  new instrument/forex specification. It provides versioned identities,
  time-valid target mappings, source-tiered rules, signed evidence ledgers,
  latent currency scores, base-minus-quote FX differentials, common-mode/joint
  activation diagnostics, and identity/inversion/triangle invariants.
  Unknown evidence remains unknown. `execution_allowed=false` and
  `promotion_allowed=false`; the package cannot affect Auto Suggest, MT5,
  markers, orders, stops, or targets.
- Added explicit experimental policy locks to `doctrine_config.yaml` and the
  architecture record
  `instrument_relative_sbc_fx_foundation_20260718.md`. Automatic akshara
  resolution, live Chakra-to-contribution translation, certified economic
  identity charts, walk-forward calibration, and promotion remain pending.
- Verification: `274` full Python tests pass; `20` focused new tests pass;
  changed-file Ruff checks pass. Runtime/user files
  `gann_aspect_annotations_raman_v2.sqlite`, `candlestick_shadow_v3.sqlite`,
  `logs/`, and `tryapp-android/` were not modified or committed by this
  milestone.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_080416_shadbala_jhora_instrument_relative`.

## Latest Update - 2026-07-18 (Drik Bala V2 Reconciliation / Gate Still Closed)

- This is a verified source milestone, not a native release promotion. Stable
  Gann Astro Desk remains `0.10.8`; the packaged executable, installer, and
  rollback evidence remain unchanged.
- Added the standalone, auditable `drik_bala_engine.py` under rule
  `PARASHARA_DRIK_BALA_RECONCILIATION_V2`. It preserves six directed
  contributions per target planet, including angle, base strength, special
  bonus, gross strength, nature and reason, raw signed strength, and normalized
  signed strength.
- Production Drik fields now use signed raw net divided by four under
  `DRIK_NET_DIVIDE_BY_FOUR_V1`. Raw net and raw benefic/malefic splits remain
  available in separate fields; the nature and contribution ledgers are
  persisted as JSON rather than discarded.
- Replaced fixed Moon/Mercury classification with the explicit
  `PVR_TITHI_SIGN_ASSOCIATION_NATURE_V1` policy: waxing Moon is benefic, waning
  Moon is malefic; Mercury is classified by same-sign associations, with the
  nearest same-sign planet resolving equal benefic/malefic counts.
- Jupiter, Mars, and Saturn special-aspect strength now uses the active
  PyJHora `4.8.7` angle ranges under
  `PYJHORA_4_8_7_ACTIVE_SPECIAL_ASPECT_RANGES_V1`, rather than firing only at
  one exact degree. This policy is comparator-specific and is not labeled as
  universally canonical.
- The saved Tier B comparator now passes all `35 / 35` Drik totals within
  `0.5` virupa. Mean absolute residual fell from `17.4336` to `0.0011`
  virupa; maximum residual fell from `49.4942` to `0.0100`. The stricter
  `210`-row directed-contribution comparison has zero nature mismatches,
  maximum angle residual `0.02` degree, maximum gross/raw residual `0.02`
  virupa, and maximum normalized residual `0.005` virupa.
- Evidence is hash-pinned. The saved total matrix
  `pyjhora_external_strength_values_20260718.csv` has SHA-256
  `29A88901CEE0821F3F20C75777D2BDDACDB9524EB253939D9263E693CBDEE9C9`;
  the new contribution matrix `pyjhora_drik_contributions_20260718.csv` has
  SHA-256
  `6FDB30D6CF082B017436093F7F81CFB8BAB303A6B7426A4B4414BF47DCA2D342`.
  The pinned PyJHora wheel remains local and unbundled.
- Gate 3 remains deliberately `failed_external_validation`: astronomy and
  Panchanga contribute `25` passing rows, Drik contributes `35` passing rows,
  and all `35` implemented full-Shadbala totals still fail, for `60 pass / 35
  fail / 0 pending`. `certified=false` and `executionAllowed=false`.
- PyJHora remains Tier B evidence only. The certification runner now emits the
  separate `35`-row
  `jhora_drik_independent_validation_template_20260718.csv`, and both the
  report and app gate fail closed until a reproducible Jagannatha Hora export
  or cited independent worked example passes every row. Current independent
  status is `blocked_pending_independent_values` with `35` pending.
- Gate 4 remains correctly `blocked_legacy_dataset`; no corrected result has
  been silently applied to the quarantined legacy case history. A versioned
  timestamp-safe USDJPY rebuild is still required before retrospective or
  prospective promotion.
- Added explicit `strict_shadbala_doctrine` and `drik_bala_engine` hidden
  imports to both PyInstaller specs so dynamically loaded chart generation
  cannot omit the reconciled engine from a future Windows package.
- Verification in the integrated D: repository: all `255` Python tests pass;
  the `24` focused Drik/doctrine/certification/app-gate tests pass; changed-file
  Ruff checks pass; `git diff --check` passes.
- Detailed evidence: `drik_bala_reconciliation_20260718.md`,
  `drik_contribution_ledger_20260718.csv`, and
  `astro_function_certification_report_20260718.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_070400_drik_v2_reconciliation`.

## Latest Update - 2026-07-18 (Replay / Drawings / Decision / Validation Source Milestone)

- This is a verified source milestone, not a promoted native release. Stable
  Gann Astro Desk remains `0.10.8`; its packaged executable and rollback
  evidence remain unchanged.
- Added timestamp-safe Bar Replay under
  `GANN_TIMESTAMP_SAFE_BAR_REPLAY_V1`. The chart API accepts a replay cutoff,
  emits only closed candles, removes future event starts, clips active
  event/regime windows, hides future outcome/review labels and returns, counts
  only occurrences known by the cutoff, and reveals an SR touch only after its
  touch candle closes. The workspace has select, previous, play/pause, next,
  and exit controls, and suspends live refresh while replay is armed.
- Added persistent drawing workflow controls: favorites, OHLC magnet modes
  (`off`, `weak`, `strong`), keep-drawing mode, drawing groups, group rename,
  group visibility/locking, unlocked-group deletion, and synchronization
  scopes (`layout` or `symbol`). Symbol-scoped drawings persist through
  `app_chart_synced_drawings` and appear across layouts/timeframes for the same
  symbol.
- Decomposed the legacy Auto Suggest decision path in
  `reviewer_rule_replay.py` into typed evidence, baseline, support/boundary,
  marker-flow, and finalization stages. The old in-function monolith/oracle is
  removed. Golden decisions for cases `8`, `43`, `103`, `127`, and `185`
  remain locked by seven focused tests.
- Strengthened the external astrology gate under
  `GANN_ASTRO_EXTERNAL_CERTIFICATION_GATE_V1`. It now has five explicit
  fixtures and a complete 70-row matrix: five fixtures x seven classical
  planets x Shadbala total and Drik Bala. External imports reject duplicate,
  unknown, unsourced, and non-numeric strength rows; the numeric tolerance is
  `0.5` virupa and execution remains disabled even if research certification
  eventually passes.
- Current Gate 3 truth is deliberately fail-closed:
  `failed_external_validation`. Twenty-five saved astronomy/Panchanga witness
  rows pass, while all 70 Shadbala/Drik strength comparisons fail the declared
  `0.5` virupa tolerance; no strength rows remain pending. The reproducible
  PyJHora `4.8.7` export is
  `pyjhora_external_strength_values_20260718.csv` (SHA-256
  `29A88901CEE0821F3F20C75777D2BDDACDB9524EB253939D9263E693CBDEE9C9`).
  Its hash-pinned wheel is staged locally at
  `D:\GannFinancialAstro\external_validators\wheels\pyjhora-4.8.7-py3-none-any.whl`
  (SHA-256
  `D8D8014573A38DDEFEDCAE57D3B8D84687CAC2AD31BB5B1DD70D945906A4D54D`)
  and is not bundled or committed.
- The external failure is evidence, not a tolerance problem to hide. Many
  local Drik values divided by four closely approach PyJHora, but residual
  differences remain around dynamic Moon/Mercury benefic classification and
  special-aspect handling. Shadbala totals also differ materially, indicating
  additional component-level differences. Do not silently alter production
  formulas from this single secondary comparator: keep v4 strength fields
  provisional, blocked from execution/promotion, and resolve each component
  against Jagannatha Hora or a saved worked classical example.
- Added `GANN_RESEARCH_VALIDATION_GATE_MATRIX_V1` and
  `/api/validation-gates`, plus a compact workspace status strip. The matrix
  independently reports timestamp safety, external astrology,
  retrospective policy, prospective shadow trial, candlestick model, and
  execution authorization. Research prerequisites can pass without unlocking
  order execution.
- Frozen retrospective policy currently fails its declared statistical gate:
  `258` watches / `355` clusters, `54.26%` hit rate, Wilson 95% interval
  `48.17%-60.24%`, two-sided binomial `p=0.190975`, and mean signed 72-hour
  return `+0.0276%`. The prospective gate remains collecting and requires at
  least `100` watch clusters, `10%` coverage, Wilson lower bound above `0.5`,
  `p < 0.05`, positive mean signed return, and four calendar months under one
  immutable cohort.
- Verification: all `246` Python tests pass in the final source state; focused
  backend (`96`), Auto Suggest (`7`), and external-certification/export (`5`)
  suites pass. The final frontend state passes `38` tests across `12` files,
  Oxlint, TypeScript checks, and a Vite production build. Browser QA verified replay
  scrubbing (`241` full bars to `113` known bars at the chosen cutoff),
  future-aspect reduction (`47` to `19`), drawing panel access at desktop and
  970 px width, the validation strip, and zero console errors.
- Detailed evidence:
  `gann_astro_desk_replay_drawings_validation_20260718.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_043433_replay_drawings_validation`.

## Latest Update - 2026-07-18 (End-to-End Product Audit / Stable 0.10.8)

- Completed an end-to-end audit of the supported Tauri/React/Python/Rust
  workstation, runtime logs, packaging, documentation, recovery state, and
  legacy review path. Detailed evidence and roadmap:
  `gann_astro_desk_end_to_end_audit_20260718.md`.
- Corrected the most serious runtime defect: frozen corrected-data generation
  no longer executes astronomy workers synchronously inside the API sidecar.
  Every source and packaged job now uses an isolated child process with the
  existing cancellation/supervision path.
- Moved optional Codex/Ollama startup off the chart-critical path. The backend
  imports and opens HTTP first, Codex starts after readiness, and Ollama warm-up
  is deferred. The shutdown path now also prevents a helper started during
  shutdown from becoming orphaned.
- Added a per-launch private API token shared only by the Rust shell, Python
  child, and trusted frontend runtime. Packaged requests without the exact
  token fail closed; source/Vite development remains tokenless. Execution stays
  locked. The release soak now supplies a constrained one-launch token and
  authenticates all 35 checks, including the deliberate sidecar restart.
- Replaced the main workspace's overlapping interval fleet with one
  visibility-aware scheduler. Hidden windows use a minimum 30-second cadence;
  expensive panels poll quickly only while visible; generation polls at 1.5
  seconds only while active.
- Added incremental Lightweight Charts live-bar updates, SR-line signature
  reuse, animation-frame crosshair throttling, and stable global drawing-drag
  listeners.
- Code-split Analyze Aspect, Parameter Drawer, Drawing Objects, Square of Nine,
  and Chakra Lab. The main minified JavaScript fell from 540.84 kB to 463.06 kB
  and gzip from 163.63 kB to 146.24 kB.
- Suppressed routine Werkzeug access lines and added 10 MiB / three-backup
  rotation for sidecar stdout, stderr, and supervisor logs.
- Fixed a recovery-repository defect: root `*.html` ignored the untracked Vite
  entry document. `gann-astro-desk\index.html` is now explicitly tracked, so a
  clean Git checkout can build.
- Final verification passes all 229 Python tests, 33 frontend tests across 10
  files, Oxlint, TypeScript/Vite production build, 8 focused
  generator/process tests, 3 private API security tests, changed-Python Ruff,
  4 Rust tests, Rust formatting, strict Clippy, PyInstaller sidecar packaging,
  and Tauri/NSIS packaging.
- Candidate and promoted stable packages each passed all 35 authenticated
  native checks with zero errors, same-port sidecar recovery, preserved chart
  layout, execution locked, and zero descendant survivors:
  `D:\GannFinancialAstro\soak\tauri_0.10.8_20260717_195543\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.8_20260717_202432\logs\native_soak_report.json`.
- Stable cold sidecar readiness is 18.5 seconds after process start and the
  interactive chart appears in approximately 18-20 seconds, roughly half the
  prior approximately 40-second visual baseline. Backend startup itself is
  3.06 seconds.
- Interactive native QA passed for the main chart, parameter drawer, Square of
  Nine, Chakra board, Analyze Aspect second window, Local Jyotish readiness,
  and read-only connected Codex panel. Evidence is under
  `gann-astro-desk\docs\visual_qa\gann_astro_desk_0108_*_20260718.png`.
- Promoted stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
  SHA-256: executable
  `FA28C213D6894CFF8DBCE14F416C24C84446BFFBC7AA457D0D2AAC64EB8C8635`;
  installer
  `1BD1D9B742B0EC0E15B4BE8F4C6D7DF1AD95CD86937029BAC124229B242710BE`;
  sidecar
  `F168417FE656944AEAD827A4D6DEAE90458DE15B22032B7E45BE247DA84BE768`.
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.7_20260717T202315Z`;
  pre-promotion state:
  `D:\GannFinancialAstro\state_backups\pre_0.10.8_promotion_20260717T202315Z`;
  recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260718_015745_product_audit_0108`.
- Highest-priority product work remaining is timestamp-safe Bar Replay,
  drawing favorites/magnet modes/groups/sync scopes, deterministic decision
  engine decomposition, and approved artifact/backup retention.
- Deliberate gates remain unchanged: corrected TT generation, external
  Shadbala/Drik certification, purged prospective validation, BTC rolling
  no-lookahead evidence, retrospective policy promotion, and any order
  execution.

## Latest Update - 2026-07-17 (Native Chakra Lab Release 0.10.7)

- Promoted Gann Astro Desk `0.10.7` with the timestamp-safe, read-only
  Sarvatobhadra Chakra Lab introduced in Phase 4A. The native Tauri package
  contains the 81-cell board, explicit actor/motion controls, Vedha guidance
  ledger, matched-cell evidence, and cell inspector.
- The release manifest now declares
  `SBC_CHAKRA_LAB_SNAPSHOT_V1`, `read_only_guidance`,
  `chakra_lab_execution_allowed=false`, and
  `chakra_lab_financially_validated=false`. MT5 remains data-only and all order
  execution remains locked.
- Extended the native release soak from 28 to 35 checks. The packaged test now
  requires the Chakra endpoint, contract, 81 cells, exact as-of/evidence-cutoff
  equality, explicit Jupiter motion readiness, timestamp/no-lookahead locks,
  and market/execution/financial guardrails.
- Corrected a soak-only Windows PID ancestry false positive. A lingering
  `git remote -v` process had started before the app but inherited a stale
  parent PID. The shutdown gate now ignores only processes whose start time
  predates the app and still fails on every real descendant survivor.
- Corrected repeat build hygiene so `build_backend_sidecar.ps1` recreates
  `.gitkeep` as ASCII instead of adding a Windows PowerShell UTF-8 BOM.
- Verification passed: all 226 Python tests; all 32 frontend tests across nine
  files; Oxlint; TypeScript/Vite production build; focused Ruff lint and format
  checks; two Rust tests; Rust formatting; Clippy with warnings denied; release
  script parsing; and `git diff --check` apart from expected line-ending
  warnings.
- The candidate and promoted-stable native soaks each passed all 35 checks with
  zero errors, zero failed checks, same-port sidecar recovery, and zero genuine
  descendant survivors:
  `D:\GannFinancialAstro\soak\tauri_0.10.7_20260717_134805\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.7_20260717_154428\logs\native_soak_report.json`.
- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
  SHA-256: executable
  `CF8441C084BFB837499891FACFD194279C5DFCDA8FD0CEC4D1F4974FDB9CCE63`;
  installer
  `F9AE74EB99FE3675F1C201C1786712BAE5D457324E182B97AFCBD04174C22204`;
  sidecar
  `7F45E86DFEB0A3F492F108FB9E1840D852D8CE4F391AC68941972A296E6A0215`.
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.6_20260717T154235Z`;
  pre-promotion writable-state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.7_promotion_20260717T154235Z`.
- Packaged-stable interactive visual QA was completed after Windows permission
  was granted. `GannAstroDesk.exe` reached the main chart after an approximately
  40-second cold start, the Chakra tab rendered the complete 9x9 board, and
  changing Jupiter motion from `Required` to `Mean` plus `Refresh snapshot`
  advanced actor readiness from four to five. No browser error, blank surface,
  clipping, or incoherent overlap was visible at 1482x864. Evidence:
  `gann-astro-desk\docs\visual_qa\gann_astro_desk_0107_chakra_interactive_20260717_224115.jpg`.
- Detailed release evidence:
  `sbc_chakra_lab_native_release_20260717.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_211806_sbc_chakra_lab_release_0107`.
- Interactive-QA recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_224115_chakra_interactive_qa`.

## Latest Update - 2026-07-17 (Sarvatobhadra Phase 4A Chakra Lab)

- Added a timestamp-safe, read-only Sarvatobhadra Chakra research surface to
  the native Gann Astro Desk source. The Chakra tab accepts one offset-aware
  IST moment, latitude/longitude/altitude, optional vowel and name-initial
  keys, explicit actor selection, dignity, and required motion state for Mars
  through Saturn. Sun, Moon, Rahu, and Ketu retain their source-profiled fixed
  motion directions.
- Added `sbc.chakra_lab.ChakraLabEngine` and the versioned
  `SBC_CHAKRA_LAB_SNAPSHOT_V1` contract. One deterministic foundation snapshot
  supplies astronomy, Panchanga, rashi, nakshatra, grid context, actor
  readiness, Vedha rays, and the guidance ledger. Snapshot identity includes
  scientific inputs and profile hashes; the local display timestamp and
  canonical UTC evidence cutoff are both retained.
- Missing variable-planet motion fails closed as `MOTION_REQUIRED`; it is never
  inferred from future movement. Unknown API fields and naive timestamps fail
  closed. The response guardrails require read-only operation, no lookahead,
  no market data, no financial validation, and `execution_allowed=false`.
- Added a strict private backend adapter at
  `POST /api/chakra-lab/snapshot`, a native Tauri IPC command, and a
  dependency-free Rust loopback bridge. The browser development fallback uses
  the private API; packaged Tauri code does not expose the sidecar port to the
  Chakra UI. PyInstaller configuration now bundles the SBC profiles, schemas,
  Python modules, Panchanga doctrine, and Swiss Ephemeris import.
- Added the operational Chakra UI: 81-cell board, context/ray/matched-cell
  states, explicit actor readiness, favorable/adverse/net/coverage ledger,
  matched-cell evidence, and cell inspector. The UI deliberately contains no
  bullish/bearish label, Auto Suggest, price, order, or MT5 action.
- Verification passed: all 226 Python repository tests, 32 frontend tests
  across nine files, the production TypeScript/Vite build, Oxlint, changed-file
  Ruff lint and format checks, Rust formatting, and both Rust bridge tests.
  The frontend tests include native IPC isolation and proof that the Chakra
  surface renders no bullish/bearish trading label.
- Source-mode smoke testing passed at `http://127.0.0.1:5173/` against the
  read-only backend on port 8788. The live endpoint returned 81 cells, matching
  `as_of_utc` and `evidence_cutoff_utc`, three explicitly ready test actors,
  `execution_allowed=false`, and `financially_validated=false`. The UI promoted
  Jupiter from `MOTION_REQUIRED` to the source-profiled FRONT direction only
  after explicit `MEAN` selection. Browser diagnostics contained no warnings
  or errors. Visual QA also corrected a constrained-width actor-grid overflow.
- `git diff --check` is clean apart from expected Windows line-ending warnings.
  The unrelated modified annotation database and local untracked database,
  logs, and Android worktree remain untouched and uncommitted.
- Detailed architecture, guardrails, and validation evidence:
  `sbc_phase4a_chakra_lab_20260717.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_151619_sbc_phase4a_chakra_lab`.
- Stable Gann Astro Desk remains `0.10.6`. Phase 4A source is not a promoted
  packaged release. Before promotion, build the PyInstaller sidecar and Tauri
  EXE, execute a packaged read-only smoke test, and repeat the green source
  checks as release verification. Financial interpretation still requires
  prospective out-of-sample validation.

## Previous Update - 2026-07-17 (Sarvatobhadra Phase 3A Vedha Guidance)

- Added the explicit-only
  `phaladeepika_editor_vedha_guidance_v1` profile and deterministic
  `sbc.vedha.VedhaGuidanceEngine`. It derives standard figure-relative left,
  front, and right rays from the certified 81-cell board and validates them
  against the editor supplement's printed Krittika, Rohini, and Mrigashira
  nine-target examples.
- Reinspecting those examples exposed a Phase 2A transcription error. Six
  rashi cells were shifted one column right to their page-supported positions:
  top `VRISHABHA (3,4)`, `MITHUNA (3,5)`, `KARKA (3,6)`; bottom
  `MAKARA (7,4)`, `DHANUS (7,5)`, `VRISCHIKA (7,6)`. Direct coordinate and
  worked-example regressions now guard the correction.
- Encoded source-profiled motion without inventing a speed threshold:
  Sun/Moon use left; Rahu/Ketu use right; Mars through Saturn require caller
  supplied `DIRECT_SWIFT`, `MEAN`, or `RETROGRADE`, mapping to left, front, or
  right. Missing variable motion fails closed.
- Added an auditable research-guidance ledger. Each target match is one
  experimental evidence unit; resolved benefic/malefic nature supplies the
  sign, and the held source modifiers are `2x` retrograde, `3x` exalted, and
  `0.5x` debilitated. Favorable, adverse, net, normalized balance, unresolved
  contributions, and scoring coverage remain separately visible.
- The numerical score is an engineering comparison aid, not a classical
  financial score. Every report is `guidance_only=true` and
  `financial_validation_status=NOT_VALIDATED`; financial labels, trades, and
  MT5 execution are blocked. Conditional Moon/Mercury nature, automatic direct
  speed classification, retrograde-plus-dignity precedence, special
  corner/junction rules, and classical natal-severity translation fail closed.
- Reproducible sample: mean-motion Jupiter/Krittika to Shravana contributes
  `+1`; retrograde Saturn/Krittika to Bharani contributes `-2`; net `-1`,
  normalized `-0.3333333333333333`, coverage `1.0`. This is evidence balance,
  not a bearish forecast.
- Source pages: held Phaladeepika editor supplement PDF pages 349-351, printed
  pages 312-314; Rath motion comparison PDF page 22, printed page 11. The
  editor-supplied material remains clearly separated from Mantreswara root
  doctrine.
- Runtime hashes: Vedha profile
  `EE8283233C9BFE1E1565552B93F3F1E317367D5CD2A153726F54BCC6AA05D3BD`;
  corrected grid
  `468F0FCD43D1A9271DDC4F86F4664F2C22F7EC327C6B131B975D67B3557B8F3D`.
  Raw YAML SHA-256 is
  `B46966D2C979DB013FDE1EE9DDF9500952704D90134BDFDBAEC9468668CC83CA`.
- Verification passed: 24 focused Phase 2A/2B/3A tests, all 212 repository
  tests, Ruff lint and format checks, and `git diff --check`. Evidence and
  decisions are in `sbc_phase3a_vedha_guidance_20260717.md`,
  `docs/sbc/VEDHA_GUIDANCE_AUDIT.md`, Phase 3A acceptance gates, and ADR-0004.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_085230_sbc_phase3a_vedha_guidance`.
- Stable Gann Astro Desk remains `0.10.6`; Phase 3A is not integrated into the
  packaged app. Next gates are timestamp-safe read-only Chakra Lab adaptation,
  direct-speed and special-corner source certification, and prospective
  out-of-sample financial validation before any market-facing interpretation.

## Previous Update - 2026-07-17 (Sarvatobhadra Phase 2B Letter Fixture)

- Certified the Sanskrit letter layers in the explicit-only
  `sbc_81_rotation_normalized_partial_v1` profile from the two held page
  witnesses. The fixture now compiles 16 vowels and 20 name-initial sounds in
  addition to the Phase 2A structural layers. Each letter entry carries an
  uppercase ASCII token, exact Devanagari glyph, lowercase ASCII
  transliteration, semantic role, and both page citations.
- Corrected a doctrinal-data trap instead of normalizing it away. The source
  calls the 20-item ring consonantal, but its first item is vowel `अ`. The
  executable layer is therefore `NAME_INITIAL`, and the first item records
  `VOWEL_EXCEPTION_IN_NAME_INITIAL_RING`; the remaining 19 record
  `CONSONANT_NAME_INITIAL`.
- Added strict runtime and JSON-schema contracts. Letter entries fail closed
  when glyph, transliteration, or semantic role is absent or inconsistent;
  structural layers reject letter-only metadata. The profile compiles 88
  entries across six certified layers: 28 nakshatra, 20 name initial, 12 rashi,
  5 tithi group, 16 vowel, and 7 weekday.
- Absolute cardinal orientation remains the only unresolved layer. The fixture
  stays `complete=false`, figure-relative, read-only, explicit-only, and blocked
  from Vedha, Latta, scoring, financial labels, trades, and MT5 execution.
- A lawful retail listing was located for the 1972 *Sarvatobhadra Chakra* with
  *Trailokya Dipika* commentary by Pt. Mithalal Vyas. It is an acquisition lead
  only. No acquired/page-certified 64-cell mapping was found, so
  `sbc_64_blocked_v1` still raises `GridProfileBlockedError` and no coordinates
  were invented.
- Deterministic profile hash:
  `7C772792EADDAE88DF8612B55E0A6FBD2E699E3A2C3CD95101E8A93868984D45`.
- Verification passed: 15 focused Phase 2A/2B tests, all 203 repository tests,
  changed-file Ruff lint and format checks, schema/runtime parity coverage, and
  `git diff --check`. Evidence is in
  `sbc_phase2b_letter_fixture_20260717.md`,
  `docs/sbc/LETTER_FIXTURE_AUDIT.md`, Phase 2B acceptance gates, and ADR-0003.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_072038_sbc_phase2b_letter_fixture`.
- Stable Gann Astro Desk remains `0.10.6`; no SBC UI is packaged or promoted.
  Recommended next gate is independent-calculator/edition comparison and an
  explicit resolution policy for cardinal orientation before a read-only
  Chakra Lab. Vedha/Latta interpretation remains a separate later gate.

## Previous Update - 2026-07-17 (Sarvatobhadra Phase 2A Grid Fixture)

- Added the explicit-only `sbc_81_rotation_normalized_partial_v1` research
  fixture and strict compiler. It deterministically creates 81 figure-relative
  cells with 28 nakshatras including Abhijit, 12 rashis, five tithi groups, and
  seven weekday entries. Every entry resolves to a registered page locator.
- The local source comparison found a material orientation issue that is now
  preserved in data: the cardinals-labeled plate in the 1937 Subrahmanya Sastri
  *Phaladeepika* editor supplement becomes Sanjay Rath Figure 1.2 only after a
  90-degree counter-clockwise rotation. The compiler therefore claims topology
  agreement, not a certified absolute North/East orientation.
- Kept source layers honest. PDF page 341 contains root Mantreswara 26.48;
  pages 342-356 are editor-supplied extracts/free rendering. The executable
  fixture cites PDF pages 347-349 as editor supplement material. Rath PDF page
  21, printed page 10, is registered as modern secondary commentary.
- The fixture is intentionally incomplete: 16 vowel slots, 20 consonant slots,
  and absolute cardinal binding remain unresolved, so `complete=false`.
  Vedha, Latta, scoring, financial labels, trades, MT5 execution, desktop-app
  integration, and implicit/default grid selection remain blocked.
- Added metadata-only `sbc_64_blocked_v1`. It records the missing source gate
  and raises `GridProfileBlockedError` if compilation is attempted; no 64-cell
  coordinates were invented.
- Compile smoke evidence:
  - profile hash
    `C5AF4D521343BA3C690EE9CE5ECAF1912D4804635CEAC43DE1161E1041B28B3B`;
  - layer counts: 28 nakshatra, 12 rashi, 5 tithi-group, 7 weekday;
  - source IDs: `PHALADEEPIKA_1937_SBC_EDITOR_SUPPLEMENT` and
    `SANJAY_RATH_CRUX_1998_SBC_FIGURE`.
- Verification passed: 8 focused Phase 2A tests after formatting, all 196 full
  repository tests, Ruff lint, and Ruff format checks. Evidence and decisions
  are in `sbc_phase2a_grid_fixture_20260717.md`,
  `docs/sbc/GRID_FIXTURE_AUDIT.md`, and ADR-0002.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_061702_sbc_phase2a_grid_fixture`.
- Stable Gann Astro Desk remains `0.10.6`; no SBC grid is packaged or promoted.
  Recommended next gate is a separately reviewed Sanskrit letter fixture plus
  acquisition of a page-certified 64-cell edition. A read-only Chakra Lab still
  waits for orientation resolution and independent fixture comparison.

## Previous Update - 2026-07-17 (Sarvatobhadra Phase 1 Foundation)

- Added an isolated `sbc` research package with strict source/profile contracts,
  Raman-primary and Lahiri-comparison profiles, timezone-aware Swiss Ephemeris
  positions, true/mean node selection, Ketu provenance, nakshatra/pada mapping,
  and deterministic Panchanga facts. The adapter records latitude, distance,
  speed, requested/returned flags, fallback mode, library version, ephemeris
  file path, and SHA-256 when available.
- Added explicit civil-midnight and Swiss Ephemeris sunrise Vara contracts.
  Abhijit remains inactive by default and can only be enabled through a
  source-cited profile interval. Snapshot identity uses astronomical facts,
  profile hash, time, and location rather than machine-specific paths.
- Hard-locked the unresolved layers: no 64-cell or 81-cell grid selection, no
  Vedha, Latta, directional/financial scoring, market data, Auto Suggest, MT5
  execution, or desktop UI integration. The 64/81 source conflict and the
  Phaladeepika root-text/editor-supplement split are recorded instead of blended.
- Added source register, schemas, ADR, rule-conflict register, acceptance gates,
  and Swiss Ephemeris dual-license release warning under `configs/sbc` and
  `docs/sbc`. The user-provided implementation guide is classified as a
  non-doctrinal workspace specification and is not ingested as classical text.
- Verification passed: 18 focused SBC tests and a 32-test combined regression
  pass covering existing ephemeris, event-contract, Shadbala, and SBC behavior;
  the explicitly enumerated full repository suite passed all 97 tests. A
  deterministic Delhi sample used Swiss Ephemeris data files for all nine
  bodies and produced snapshot
  `6C49401FFF48182086E7F6F2D95CD356D5EFC6AC27C5693D6C1C4561424048DC`.
- Evidence: `sbc_phase1_foundation_20260717.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_052004_sbc_phase1_foundation`.
- Stable Gann Astro Desk remains `0.10.6`; this foundation is not packaged or
  promoted. Recommended next gate is source-certified 64/81 grid fixture work,
  followed by independent-calculator comparison and only then a read-only
  native Chakra Lab.

## Previous Update - 2026-07-17 (Timeframe-Aware Aspects and W1 0.10.6)

- Promoted Gann Astro Desk `0.10.6`. Aspect visibility now follows the selected
  chart timeframe while corrected event timestamps remain unchanged. Automatic
  mode requires at least one full selected bar: M30 30 minutes, H1 60 minutes,
  H4 240 minutes, D1 1,440 minutes, and W1 10,080 minutes. The parameter drawer
  shows the applied minimum and retains an explicit manual override.
- Added W1 end to end: Monday-anchored historical candles resampled from H1,
  native MT5 `TIMEFRAME_W1` live bars, schema/profile/UI contracts, candlestick
  fallback duration, and Analyze Aspect compatibility. Corrected W1 generation
  deliberately keeps H1 source bars so canonical event/evidence timestamps are
  not weakened by chart aggregation.
- Verification passed: 30 frontend tests across 8 files, all 83 backend tests,
  Oxlint, TypeScript/Vite production build, Python byte compilation, packaged
  native visual QA, and candidate plus promoted-stable crash/recovery soaks.
  Native QA observed H1 `43 / >=1h`, D1 `12 / >=1d`, and W1 `0 / >=1w` for the
  same 3-17 July range; W1 rendered two Monday-anchored candles.
- Candidate and promoted-stable soaks each passed all 28 checks with zero errors.
  Reports:
  `D:\GannFinancialAstro\soak\tauri_0.10.6_20260716_212702\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.6_20260716_214509\logs\native_soak_report.json`.
  An earlier candidate attempt stopped before promotion because a MetaTrader
  LiveUpdate notice blocked fresh authorization; dismissing the notice restored
  the connected terminal and the unchanged candidate passed.
- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
  SHA-256: executable
  `92321E9F689D5D4CC104793E9D5F1FD8CB5C1DED80FD784CC4553F7F39C9A81F`,
  installer
  `F0F2DD3A2688EB680979AC40B45E1B4BF9D537F551BF487FA128F76B0BCF92C7`,
  sidecar
  `8074A56297A9CD4E4A2BB5A21DD246F168CFABA02F2B6F16FB53D3227E5051C0`.
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.5_20260716T214414Z`;
  pre-promotion state:
  `D:\GannFinancialAstro\state_backups\pre_0.10.6_promotion_20260716T214204Z`.
- Evidence: `timeframe_aspect_policy_release_20260717.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_031923_timeframe_aspect_policy_v0106`.
- Safety remains unchanged: MT5 is data-only, `tradeAllowed=false`, app
  execution is locked, and timeframe switching cannot place orders.

## Previous Update - 2026-07-17 (Proximity Chart Navigation 0.10.5)

- Promoted Gann Astro Desk `0.10.5` with a compact bottom-center chart dock:
  move backward, zoom out, zoom in, and move forward. The dock appears only
  when the pointer approaches it, remains keyboard accessible, cannot intercept
  chart input while hidden, and hides again after pointer focus leaves.
- Navigation is deterministic: center-based zoom, quarter-range forward/backward
  movement, candle-bound clamping with two bars of left and five bars of right
  padding, and a minimum visible range of eight bars. Pure range/proximity
  helpers have focused regression coverage.
- Verification passed: 27 frontend tests across 7 files, all 78 backend tests,
  Oxlint, TypeScript/Vite production build, Ruff, Python byte compilation,
  browser visual/interaction QA, and packaged native Windows QA. The native
  test visibly exercised zoom and forward movement, then confirmed the dock
  disappears outside its proximity region.
- Candidate and promoted-stable crash/recovery soaks each passed all 28 checks
  with zero errors. Reports:
  `D:\GannFinancialAstro\soak\tauri_0.10.5_20260716_191936\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.5_20260716_193440\logs\native_soak_report.json`.
- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
  SHA-256: executable
  `E93358F99276FF2E41068B520749C22A45D9B1D5C28A08F9B9FB796A7B08DF16`,
  installer
  `B556FDA10B8741EF91232A45116CA261410A6361938A035B6C35F4E0364073EC`,
  sidecar
  `2FC4035143D62EE8ED1B5D9AA1BBAD83EB33F246AF534B859FC046820D60D53E`.
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.4_20260716T193054Z`;
  pre-promotion state:
  `D:\GannFinancialAstro\state_backups\pre_0.10.5_promotion_20260716T193054Z`.
- Evidence: `chart_navigation_release_20260717.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260717_010819_chart_navigation_v0105`.
- Safety remains unchanged: MT5 is data-only, `tradeAllowed=false`, app
  execution is locked, and chart navigation cannot place orders.

## Previous Update - 2026-07-16 (Self-Service MT5 Historical Charts 0.10.4)

- Promoted Gann Astro Desk `0.10.4` with a one-click Research command,
  `Fetch MT5 and build aspects`. It captures fully closed MT5 bars, verifies and
  promotes an immutable source, bounds dates to actual broker coverage, queues
  corrected TN generation, activates the artifact, and opens the chart. H4/D1
  use H1 source bars; M30 uses native M30 bars.
- Removed the USDJPY-only generator/payload restriction. Exact MT5 symbols can
  now be used, including normal broker suffix characters. Active artifact and
  requested symbol must match.
- Non-USDJPY assets require a genuinely distinct birth/IPO reference label and
  date/time/UTC-offset/location. Label-only renaming is rejected, and
  `--disable-base-reference` prevents hidden USD reference evidence. TT remains
  disabled; this is corrected TN generalization only.
- Added transparent full/partial broker-history reporting with a 72-hour market
  closure tolerance. One generation job supports five years, so a four-year
  chart is one request; snapshot capture supports twenty years.
- Proved the read-only path live with AAPL on MetaQuotes-Demo: snapshot
  `AAPL_H1_20260716T143525Z_b6b6c31e`, 7,219 fully closed H1 bars from
  18 July 2022 through 16 July 2026, one incomplete bar excluded, measured MT5
  offset `+10,800s`, parquet SHA-256
  `1790159A9AF19A2A76DB562717DC3290CE76530CC7726DB2B3C1C03F49D46314`.
  Clock evidence records USDJPY as validation symbol and AAPL as requested
  symbol rather than guessing a cross-symbol offset.
- Verification passed: 24 frontend tests, 78 backend tests, Oxlint,
  TypeScript/Vite build, Ruff, Python byte compilation, native visual QA, and
  final candidate plus promoted-stable crash/recovery soaks. Reports:
  `D:\GannFinancialAstro\soak\tauri_0.10.4_20260716_165645\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.4_20260716_170035\logs\native_soak_report.json`.
- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
  SHA-256: executable
  `1E265FD427D15A8BEFBF3516A7638E16FD1AC6E19C8AA549B7AF68A62A2C6151`,
  installer
  `2E95ED8B66FB34D712DE1C63888634C63319F2276EAF31962C6D1C6D851F599A`,
  sidecar
  `059AD2BEC18944181AA0602940251CA5520ED2F44F156665DA242ED4C1887950`.
- Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.3_20260716T150745Z`;
  final pre-promotion state:
  `D:\GannFinancialAstro\state_backups\pre_0.10.4_final_promotion_20260716T165918Z`.
- Evidence: `self_service_mt5_chart_release_20260716.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260716_223439_self_service_mt5_chart_v0104`.
- Safety remains unchanged: MT5 is data-only, `tradeAllowed=false`, app
  execution is locked, and historical chart generation cannot place orders.

## Previous Update - 2026-07-16 (Two-Year USDJPY Aspect Chart 0.10.3)

- Promoted Gann Astro Desk `0.10.3` with a ready native two-year USDJPY research
  chart. The default named layout `USDJPY 2Y D1 TN aspects` spans 16 July 2024
  through 16 July 2026, displays 627 D1 candles, and keeps Aspects and SR enabled.
- Captured immutable normalized snapshot
  `USDJPY_H1_20260716T115532Z_0fc96b3a`: 12,421 fully closed H1 bars, one
  incomplete bar excluded, measured MT5 server offset `+10,800s`, raw server epochs
  preserved, and parquet SHA-256
  `0F3F4039A56FE5D10843E56FE5DAAB8879A46F0090200E5A60144188419A4D75`.
  Promoted price source is
  `mt5_USDJPY_H1_20260716T115532Z_0fc96b3a`.
- Generated and activated corrected TN artifact
  `tn_b439f7561ff547a4ad59d13217bcebde` with 2,464 aspect windows, 1,569
  deterministic SR touches, and 8 planetary SR lines. TT remains disabled.
- Fixed a chart viewport defect: `minBarSpacing=3` limited a roughly 1,100-pixel
  chart to about thirteen months even though the backend returned the complete
  range. The new 0.5-pixel zoom floor preserves normal zoom but allows all 627 D1
  candles to fit. Added a focused regression test.
- Verification passed: 20 frontend tests, Oxlint, TypeScript/Vite build, native
  candidate visual QA, and candidate plus promoted-stable crash/recovery soaks.
  Candidate report:
  `D:\GannFinancialAstro\soak\tauri_0.10.3_20260716_125424\logs\native_soak_report.json`;
  stable report:
  `D:\GannFinancialAstro\soak\tauri_0.10.3_20260716_130357\logs\native_soak_report.json`.
  Earlier in this same release cycle all 72 backend tests, Ruff, and Python byte
  compilation also passed.
- Promoted executable SHA-256:
  `5B078630CCFE18DF74BB877716ACAE1EC29B3E8FCC6F84189AEDBB5DEEBAE560`;
  installer SHA-256:
  `27C62BEBF24A64D69A45DBC7D6272A5788B66159A93F123AFDAEAC55D8BF523C`.
  Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.2_20260716T130240Z`;
  pre-promotion state:
  `D:\GannFinancialAstro\state_backups\pre_0.10.3_promotion_20260716T130240Z`.
- Evidence: `two_year_aspect_chart_release_20260716.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260716_183944_two_year_aspect_chart_v0103`.
- Safety remains unchanged: MT5 is data-only, `tradeAllowed=false`,
  `appExecutionAllowed=false`, and the chart is retrospective research evidence,
  not walk-forward certification.

## Previous Update - 2026-07-16 (Measured MT5 Time Normalization 0.10.2)

- Promoted Gann Astro Desk `0.10.2` with measured, fresh MT5 server-time
  normalization. Read-only service `GannClockProbe` writes
  `GANN_MT5_CLOCK_PROBE_V1`; the Python observer derives
  `GANN_MT5_SERVER_TIME_NORMALIZATION_V1` from `TimeTradeServer-TimeGMT`, keeps
  raw server epochs alongside normalized UTC, and skips without append when the
  evidence is stale, inconsistent, drifting, or mismatched. There is no hardcoded
  three-hour correction.
- Added V3 contracts
  `GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V3`,
  `GANN_CANDLESTICK_PROSPECTIVE_DECISION_V3`,
  `GANN_CANDLESTICK_PROSPECTIVE_6BAR_OUTCOME_V3`, and
  `GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V3`. Trial ID is
  `FD210BB9F2AD1287E23A5BFF526DD65E4C1AAF8832D0F5274805CFBB3065E0DA`.
- Live MetaQuotes-Demo evidence measured server offset `+10,800s`, normalized the
  tick to about 1-2 seconds from UTC, and captured the first real V3 decision at
  `2026-07-16T08:00:16.821622Z`, 16 seconds after the H1 close. Decision
  `6F317AD1E5A734AE606B040CA747C9E8172CC7DB94C1FA126EA7452165B73AB0`
  correctly abstained at probability-up `0.4953679816`; later scans refused a late
  duplicate. V3 database SHA-256 is
  `99F91BDD9EC4CD55D13656B29AD71847550FD8ACD8F693BD26F90899AC74AC04`.
- V2 was never opened by V3 and remains byte-identical at SHA-256
  `98F58DE7D8EA7CB4588C1B187430EBDEA29297B8A32905B91D4D476F2B1EA4B2`.
  The UI now distinguishes terminal/account Algo Trading permissions from the
  immutable application lock: `MT5 data only`, `tradeAllowed=false`, and
  `appExecutionAllowed=false`. The MQL5 probe contains no trade functions.
- Verification passed: 19 focused tests, all 71 backend tests, 18 frontend tests,
  Ruff, Python byte compilation, lint, TypeScript/Vite, PowerShell parsing,
  MQL5 compilation, candidate native visual QA, and both candidate and promoted
  stable-path crash/recovery soaks. Reports:
  `D:\GannFinancialAstro\soak\tauri_0.10.2_20260716_082809\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.2_20260716_083516\logs\native_soak_report.json`.
- Promoted release executable SHA-256:
  `0CD1A63D851A89DC20185BB7D9013C8A4598D340A396BB68C5D8F6EEEC5538A2`;
  installer SHA-256:
  `B88F807EA0001787C6CBD523C46F7A8E9B572180AEA928D2F45B00A5A2CD2DA8`.
  Rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.1_20260716T083400Z`;
  pre-promotion state:
  `D:\GannFinancialAstro\state_backups\pre_0.10.2_promotion_20260716T083400Z`.
- Evidence: `mt5_server_time_normalization_release_20260716.md`.
- Recovery snapshot:
  `D:\PycharmProjects\chat_session_backups\session_20260716_141116_mt5_time_normalization_v0102`.
- Next gate: keep V3 unchanged for at least 48 hours of clock/probe continuity,
  then continue the longer untouched prospective cohort. The primary candle model
  still fails its retrospective gate. Do not backfill, retune, or enable execution.

## Previous Update - 2026-07-15 (Prospective Candlestick Shadow 0.10.1)

- Promoted Gann Astro Desk `0.10.1` with a separate timestamp-safe USDJPY H1
  candlestick-shadow cohort. The app exposes chain state, frozen model/trial IDs,
  retrospective-gate status, clock state, decisions, and six-bar outcomes in a new
  `Candle shadow` dock.
- Froze transparent artifact
  `9FF4EE79619351C75C1B0931F3528603F3EDA0FC02E91BB0B4B5596DC798C9E6` on
  99,973 historically label-available rows. Primary named-pattern model
  `DC7ED62B864E538A86C83B862D11E8361AF83FD1C6EA58B89A839918BF53FE1D`
  still fails its retrospective gate; raw-geometry model
  `8E633BCB3DCB0237412606D86ABED7E85BF90191B152C8659DA60100064478E8`
  is diagnostic only.
- Added append-only/hash-chained contracts
  `GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V2`,
  `GANN_CANDLESTICK_PROSPECTIVE_DECISION_V2`, and
  `GANN_CANDLESTICK_PROSPECTIVE_6BAR_OUTCOME_V2`. Only the newest fully closed H1
  bar is eligible during a frozen 15-minute grace period; missed decisions are never
  backfilled. Outcomes use next-bar open and the sixth actual subsequent market-bar
  close, including frozen transaction costs.
- A live audit found the MetaQuotes-Demo tick clock about +10,800 seconds ahead of
  Windows UTC even though the MetaTrader Python API documents tick/bar times as UTC.
  The one resulting V1 stale abstention is preserved but invalid at
  `D:\GannFinancialAstro\app_data\candlestick_shadow_v1_invalid_market_clock_20260715.sqlite`.
  V2 freezes `GANN_MT5_MARKET_CLOCK_SKEW_LOCK_V1` at 300 seconds and now skips before
  append or settlement. Valid V2 state remains a pristine zero-entry genesis chain at
  `D:\GannFinancialAstro\app_data\candlestick_shadow_v2.sqlite`; no offset was guessed.
- Safety remains absolute: both candle candidates are excluded from astrology rules,
  Auto Suggest, official ML notes, the coordinator, and execution. MT5 remains
  read-only with `tradeAllowed=false`.
- Verification: 11 focused shadow tests, 66 backend tests, 18 frontend tests, Ruff,
  Python byte compilation, lint, Vite/TypeScript, native build, browser QA at
  desktop/compact widths, and the native
  crash/recovery soak passed. Candidate and promoted-stable reports are
  `D:\GannFinancialAstro\soak\tauri_0.10.1_20260715_172125\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.1_20260715_173904\logs\native_soak_report.json`.
- Promoted release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - executable SHA-256
    `77FEC8E0412DE9E5EEA3F1275A2C066024BB6FB77304E009BD4F697F0D80CED7`;
  - installer SHA-256
    `16E9FCA2E186BEF52B23A1AAC95664E52199F2C5BA394BF84032B4EE44C3AC7E`;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.0_20260715T172944Z`.
- Evidence: `candlestick_prospective_shadow_release_20260715.md`.
- Recovery backup:
  `D:\PycharmProjects\chat_session_backups\session_20260715_230401_candlestick_shadow_v0101`.
- Next gate: correct or replace the MT5 terminal/feed configuration until its clock
  naturally agrees with UTC within five minutes. Do not hardcode a three-hour offset,
  backfill missed rows, change the V2 manifest, or authorize execution.

## Previous Update - 2026-07-15 (Timestamp-Safe USDJPY Candle Walk-Forward V1)

- Added a separate offline USDJPY H1 candlestick evaluation lab with frozen contract
  `GANN_CANDLESTICK_WALK_FORWARD_CONTRACT_V1`. It fingerprints the immutable 100,000-row
  MetaQuotes-Demo source, reuses app geometry `transparent_ohlc_geometry_v1`, enters only
  at the next bar open, exits after six held H1 bars, charges spread and round-trip
  slippage, and uses five expanding chronological folds with label-availability purge and
  a six-bar embargo.
- The predeclared primary `named_pattern_logistic_v1` failed. Across 49,987 out-of-sample
  rows its probability range was 0.467735-0.544749, entirely inside the frozen 0.45/0.55
  abstention band, so it made zero trades. The manifest now explains that this is
  deterministic abstention rather than a missing prediction.
- Simple baselines and deterministic candle rules lost after costs. The exploratory raw
  continuous-geometry logistic model made only 84 trades at 0.17% coverage and averaged
  +4.05 pips/trade, with four positive folds, but it is far below the frozen 500-trade
  minimum and is not promoted. Aggregate bullish-pattern clues changed sign across folds
  and remain unstable diagnostics.
- Ran the complete study twice. Decision rows, predictions, fold metrics, strategy summary,
  pattern diagnostics, and purge diagnostics were byte-identical. Final local evidence is
  `D:\GannFinancialAstro\validation\candlestick_usdjpy_v1_20260715_154033`; generated
  datasets remain local and uncommitted.
- Added eight focused tests covering next-bar fills, costs, prefix invariance, source-hash
  rejection, chronological purge/embargo, disabled execution, and explicit no-signal
  probability diagnostics. Ruff and both full historical runs passed.
- Safety boundary remains absolute: these results do not feed either RAG corpus, Auto
  Suggest, official ML notes, the prospective shadow ledger, coordinator, or execution.
  MT5 and the frozen prospective policy are unchanged.
- Evidence: `candlestick_usdjpy_walk_forward_20260715.md`.
- Next gate: do not retune V1 on these folds. A separately frozen V2 may test raw geometry
  with a calibration segment, coverage floor, stronger dependence controls, and untouched
  holdout. Operationally, accumulate a timestamped prospective candle-shadow cohort first.

## Previous Update - 2026-07-15 (Isolated Candlestick Specialist 0.10.0)

- Promoted Gann Astro Desk `0.10.0` with a separate candlestick-analysis specialist.
  It shares the local Ollama runtime for memory efficiency but has its own model setting,
  corpus, retrieval layers, prompt, verifier, API contract, and Analyze Aspect tab. It is
  not an extension of the Jyotish prompt.
- Added deterministic contract `GANN_CANDLESTICK_EVIDENCE_V1` using transparent closed-bar
  OHLC geometry at a recorded timestamp cutoff. It reports body/wick fractions, close
  location, ATR14, five-bar prior trend, named geometry with formula basis, event-window
  summary, and separately labelled post-cutoff hindsight.
- Added draft contract `GANN_LOCAL_CANDLE_RAG_DRAFT_V1`. Local commentary is untrusted;
  exact source IDs, empirical caveats, focus-bar pattern consistency, certainty, TA-Lib
  parity claims, and execution-like language are verified. Missing model citations receive
  a visible deterministic footer and recorded repair.
- Analyze Aspect now has Evidence, Notes, Candles, Local Jyotish, and Codex tabs. The
  Candles tab continues to show deterministic evidence if Ollama is unavailable.
- Source research used TA-Lib documentation, publisher records, and peer-reviewed studies.
  Published findings are mixed, so pattern names are conditional feature hypotheses rather
  than signals. Copyrighted books remain registry-only unless the user supplies a lawful
  local copy. Generated corpus/index files remain local and uncommitted.
- Safety boundary is explicit: candle evidence and drafts cannot feed Auto Suggest, live
  inference, the prospective shadow ledger, official ML notes, or execution. MT5 remains
  read-only with `tradeAllowed=false`; the frozen prospective trial is unchanged.
- Promoted release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - executable SHA-256
    `8E3545DA8E9176088C08D25E7323D808F0A3FA99FEAC7D0830BC5E6486E2D161`;
  - installer SHA-256
    `A0CA5A58722F4C8D270EED09344381EF2F87414539CECDD5A7BC47F221B4212E`;
  - immediate pre-final-verifier rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.0_pre_final_verifier_20260715_200811`;
  - previous-release rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.9.2_20260715_113545`.
- Preserved live state before promotion at
  `D:\GannFinancialAstro\state_backups\pre_0.10.0_promotion_20260715_113545`.
- Verification: 10 focused candle tests, 55 backend tests, 18 frontend tests, lint,
  TypeScript/Vite, Ruff, Python byte compilation, PowerShell parsing, Rust format/check/
  test/Clippy, real event evidence, Flask plus Ollama, native visual QA, full native
  crash/recovery soak, and a stable-path native smoke passed. No descendant processes
  survived either soak. Final rebuilt-candidate and promoted-stable reports are
  `D:\GannFinancialAstro\soak\tauri_0.10.0_20260715_143548\logs\native_soak_report.json`
  and
  `D:\GannFinancialAstro\soak\tauri_0.10.0_20260715_143913\logs\native_soak_report.json`.
- Evidence: `candlestick_specialist_release_20260715.md`.
- Recovery backup:
  `D:\PycharmProjects\chat_session_backups\session_20260715_121321_candlestick_specialist_v0100`.
- Next gate: construct a timestamp-safe USDJPY candle evaluation dataset and compare raw
  geometry, named-pattern features, and simple price-only baselines with frozen trend,
  confirmation, holding, cost, purge, and embargo definitions. A coordinator may consume
  candle features only after independent out-of-sample improvement is demonstrated.

## Previous Update - 2026-07-15 (Drawings, Fibonacci, and Source Trust 0.9.2)

- Promoted Gann Astro Desk `0.9.2` with discoverable drawing-object controls and a
  persistent editable Fibonacci retracement tool. New drawings auto-select; a
  chart-side toolbar exposes edit, hide, lock, and delete; the layout toolbar shows
  a visible `Objects` command and count.
- Fibonacci uses two draggable UTC-time/price anchors and supports normalized custom
  levels, labels, prices, extension, rename, color, width, style, opacity, lock,
  hide, and deletion. Browser QA removed all temporary drawings afterward.
- Hardened local Jyotish source trust. Root texts, commentary, provenance audits,
  unverified hypotheses, and unknown sources now have explicit layers. Gann/forum
  material is retrieved only for explicit queries and cannot be promoted to
  doctrine, proof, certification, ground truth, deterministic output, or official
  ML notes.
- Audited Sarvatobhadra and Sudarshana Chakra source boundaries. Sarvatobhadra has
  witness/grid plurality; Sudarshana is BPHS-recension-sensitive. No predictive
  Chakra calculator was added. A future separate Chakra Lab requires a declared
  convention, formulas, fixtures, and out-of-sample gates.
- Added curated provenance and forum-hypothesis corpus notes plus source-layer tests.
  Generated corpus/index files remain local and uncommitted; the rebuilt local index
  contains 5,178 chunks.
- Repository tests now use a temporary database copy and clear only its runtime
  artifact tables, preventing the live prospective database from changing test
  expectations or being mutated.
- Promoted release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - executable SHA-256
    `ACD4EE927826EB850625F5592895755608A04C17D3102601377C842D9DB76CB6`;
  - installer SHA-256
    `B04936B3D175991A7E908393B7C5238C54E82F7493DD8DA10CE3E80B774E3B18`;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.9.1_20260715_082720`.
- Preserved live state before promotion at
  `D:\GannFinancialAstro\state_backups\pre_0.9.2_promotion_20260715_082622`.
  The tracked live SQLite remains deliberately uncommitted.
- Verification: 12 source/corpus tests, 45 backend tests, 15 root guardrails,
  18 frontend tests, lint, TypeScript/Vite, Ruff, PowerShell parsing, Rust format,
  check/test/Clippy, browser visual QA, artifact hashes, and the 11-check native
  crash/recovery soak passed.
- Evidence: `drawing_fibonacci_source_trust_release_20260715.md` and
  `chakra_gann_source_audit_20260715.md`.
- Recovery backup:
  `D:\PycharmProjects\chat_session_backups\session_20260715_083528_drawing_fibonacci_source_trust_v092`.
- Safety remains unchanged: manual Gann/Square/Fibonacci tools do not feed Auto
  Suggest, live inference, the shadow ledger, or execution; MT5 remains read-only
  with `tradeAllowed=false`; the frozen prospective policy/trial is unchanged.

## Previous Update - 2026-07-14 (Tauri Runtime Stabilization 0.9.1)

- Promoted Gann Astro Desk `0.9.1` after adding end-to-end runtime diagnostics,
  same-port Rust sidecar recovery, Windows Job Object descendant cleanup, and a
  frontend diagnostics/reconnect dock.
- Fixed the release-blocking packaged-generation hang. Frozen PyInstaller workers
  now invoke both existing generators on `GenerationJobManager`'s background thread
  instead of spawning another frozen copy. Development mode still uses subprocesses;
  packaged cancellation is checked between generator stages.
- A real packaged API job completed one corrected event plus one SR touch from the
  copied final candidate in 14.65 seconds. The native crash-injection soak passed all
  11 recovery, persistence, safety, and descendant-cleanup checks.
- Promoted release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - executable SHA-256
    `F7A371991250974AFBED4B693C300DCA7B714377448B03E067532AFA433531B6`;
  - installer SHA-256
    `059F78A93E5A749D6F114389831F1FA745F85E54EC3E3A080E8FE15A34469F43`;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.9.0_20260714_222152`.
- Real-state restart preserved the honestly cancelled status of stale job
  `8394a28dba854c418622b41d97bc6885`, reconnected to MetaQuotes-Demo read-only,
  and kept `tradeAllowed=false` plus every runtime execution lock false.
- Verification: 117 Python tests, 17 Vitest tests, Oxlint, TypeScript/Vite, Ruff,
  byte compilation, PowerShell parsing, Cargo check/test, Clippy `-D warnings`,
  rustfmt, frozen API generation, final-candidate generation, native crash/recovery
  soak, release hashes, and real writable-state restart passed.
- Evidence: `tauri_stabilization_release_20260714.md`.
- Recovery backup:
  `D:\PycharmProjects\chat_session_backups\session_20260714_223416_tauri_stabilization_v091`.
- Next requested work:
  1. improve discoverability and direct manipulation for horizontal/vertical lines;
  2. add persistent editable Fibonacci retracement drawings;
  3. research Sarvatobhadra and Sudarshana Chakra doctrine for local-RAG ingestion
     and evidence-only app surfaces;
  4. research Gann's *The Tunnel Thru the Air* and public Financial Astrology /
     planetary-line discussions without promoting unvalidated claims into inference.

## Previous Update - 2026-07-14 (Tauri 2 / Rust Native Shell)

- Promoted Gann Astro Desk `0.9.0`. The supported native shell is now Tauri 2 / Rust;
  PyWebView is retained only in the archived 0.8.0 rollback release.
- This is a compatibility migration, not an astrology-engine rewrite. React/TypeScript and
  Lightweight Charts remain the UI; the validated Python astrology, MT5, local Jyotish,
  corrected-data, refresh, and shadow-ledger engine runs as a managed headless sidecar.
- Added shared `runtime_support.py`, headless `backend_sidecar.py`, a sidecar-only PyInstaller
  spec, and D-drive reproducible Tauri build scripts. Rust owns random loopback ports,
  process startup, typed runtime discovery, child windows, and graceful sidecar shutdown.
- Sidecar contract: `GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1`. Frontend transport rejects an
  unknown contract, a non-private-loopback backend URL, or any runtime claiming execution
  permission. Browser/Vite development continues to use relative API routes.
- Installed the native build toolchain primarily on D::
  - Rust/Cargo 1.97 under `D:\Rust`;
  - Visual Studio Build Tools 2022 17.14.35 under `D:\VisualStudio`;
  - MSVC 19.44 and Windows SDK 10.0.26100 compiler/linker checks passed.
- Promoted release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - executable SHA-256
    `DCB4874CD3A6900597BC88A0817D467BD55EC3F1B5514FB95A2E72E06F73FE33`;
  - NSIS installer
    `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.9.0_x64-setup.exe`;
  - installer SHA-256
    `94C523AE64C81FAA7CAEF497DC845FA6A6BEC1037A8C7F5992F7862ADD8BDC2C`;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.8.0_20260714_091158`.
- Real-state verification preserved the frozen trial ID, valid seven-decision shadow chain,
  seven pending outcomes, MetaQuotes-Demo read-only connection, local Jyotish
  `qwen2.5:3b`, and every execution lock (`tradeAllowed=false`).
- Native visual QA covered the chart workspace, separate Analyze Aspect Tauri window, and
  standalone Square of Nine workspace. Closing the app terminated the managed sidecar with
  no orphan process.
- Verification: 113 Python tests, 15 Vitest tests, Oxlint, TypeScript/Vite, Ruff, source and
  packaged sidecar smoke tests, rustfmt, Cargo check, Clippy `-D warnings`, Tauri release
  build, NSIS bundle, live API contracts, native visual QA, and artifact hashes passed.
- Evidence: `tauri_hybrid_release_20260714.md`.
- Next recommended work:
  1. continue the frozen prospective trial without changing policy;
  2. code-sign the NSIS installer only after a signing identity is available;
  3. profile first and port Python bottlenecks to Rust one module at a time with fixture
     parity rather than rewriting validated doctrine logic wholesale;
  4. keep MT5 order placement outside this process and disabled.

## Previous Update - 2026-07-14 (Standalone Square of Nine + Editable Drawings)

- Promoted Gann Astro Desk `0.8.0`. Square of Nine is now a dedicated workspace tab,
  never a candlestick overlay. The market chart, aspect inspector, activity dock, and
  Square workspace are separate surfaces inside the same native application.
- The standalone Square supports price, time, date, and date-time values; editable first
  value; signed increment/decrement; minute/hour/day/week/month/trading-day units;
  center-inclusive size 1-15; independent number/angle direction; angle offset; zoom
  50%-150%; value or cell lookup; clickable High/Low/Forecast/Error marks; per-cell notes;
  PNG export; and named-layout persistence.
- Legacy `square_of_nine` chart drawings are filtered from candlestick rendering and
  migrated into standalone workspace settings on layout load. Autosave then persists the
  migrated form without leaving a stale overlay object.
- Horizontal lines, vertical lines, and Gann fans now have visible selected handles.
  Unlocked anchors can be dragged in UTC-time/price coordinates or edited numerically in
  the object panel. The panel also retains rename, hide/show, lock/unlock, color, width,
  line style, opacity, templates, and explicit Delete drawing controls. `Delete` or
  `Backspace` removes a selected unlocked object; `Escape` deselects it.
- Official GannZilla documentation was reviewed for interaction patterns: named chart
  persistence, selectable/deletable objects, Square size/first value/increment/data type,
  cell marking, zoom, and movable fan control points. The implementation is original and
  remains a research UI, not validation of Gann forecasting claims.
- Research safety is unchanged: Square of Nine and chart drawings are not consumed by Auto
  Suggest, timestamp-safe live inference, the shadow ledger, or execution. MT5 remains
  read-only with `tradeAllowed=false`; the frozen prospective policy/trial was not changed.
- Packaged QA used isolated temporary layouts and cleaned both afterward:
  - Square date mode, -1 trading-day increment, 9x9 size, a High mark, and a note survived
    reload;
  - a Gann fan was created, selected, resized by dragging its origin while its slope anchor
    stayed fixed, and deleted with the keyboard;
  - zero packaged browser warnings/errors; the user default layout and its two existing
    research drawings remain intact.
- Native release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - version `0.8.0`;
  - SHA-256 `9C81A85A6412D20721BDBEAA5922EA6E2C7E802091CDA8C42A7F4E1B0710CB48`;
  - stable tree 1,658 files / 708,955,644 bytes including the release manifest;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.7.0_20260714_000817`.
- Packaged runtime verification:
  - MetaQuotes-Demo connected in `read_only_market_data` mode;
  - local Jyotish ready on `qwen2.5:3b`;
  - shadow chain valid with 7 pending abstain decisions;
  - frozen trial ID unchanged at
    `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`.
- Verification: Oxlint, 13 Vitest tests, 38 backend tests, TypeScript/Vite production
  build, PyInstaller native build, source and packaged interaction QA, release
  hash/manifest/API checks, and `git diff --check` passed.
- Evidence is in `square9_workspace_drawing_editor_release_20260714.md`.
- Next recommended work:
  1. add optional Square templates and a print/export report only after real usage reveals
     which configurations recur;
  2. consider Gann wheel/pyramid variants as separate workspaces, not chart overlays;
  3. validate all manual Gann geometry out of sample before allowing any inference use;
  4. continue settling the frozen prospective cohort without changing its policy.

## Previous Update - 2026-07-13 (Named Layouts + Square of Nine Native Release)

- Promoted Gann Astro Desk `0.7.0` with durable named chart layouts. Layouts, drawings,
  templates, and viewport/layer state now use versioned SQLite contracts:
  `GANN_CHART_LAYOUT_V1`, `GANN_RESEARCH_CHART_DRAWING_V1`, and
  `GANN_DRAWING_TEMPLATE_V1`.
- Every drawing persists market coordinates (`timeUtc` + `price`) instead of screen
  pixels. Transactional writes use optimistic revisions; stale clients receive HTTP 409
  rather than overwriting newer work.
- Added default restore, debounced autosave, explicit Save, Save As, layout switch/delete,
  JSON export/import, undo, locked-object-safe clear, and reusable templates.
- Added a chart object tree with select, rename, hide/show, lock/unlock, delete, color,
  width, line style, and opacity controls. The same controller is used by the main chart
  and family-scoped Analyze Aspect workspace; drawings persist while navigating family
  repeatations.
- Added a Square of Nine research tool with center value, increment, rings, angle offset,
  clockwise/counterclockwise rotation, highlighted angles, cardinals/diagonals, labels,
  and optional price/time projections. The square-root rotation formula is unit-tested
  against the documented 45/90/180/360-degree increments.
- All stored and imported drawings are forcibly research-only:
  `consumedByLiveInference=false`, `consumedByShadowLedger=false`, and
  `executionAllowed=false`. Manual geometry does not change Auto Suggest or the frozen
  prospective policy.
- Interactive QA covered restore, Save As independence, lock/hide, clear, undo, templates,
  family recurrence navigation, and Square of Nine persistence. Packaged QA restored a
  data-anchored Square after reload with zero browser warnings, then removed the QA object;
  the live app database has one clean default USDJPY H1 layout with zero drawings.
- Native release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - version `0.7.0`;
  - SHA-256 `C6863F64D4ACC4E55961A22052553B9177E55B8A1CA1BF818CA851AE37F60D8F`;
  - stable tree 1,658 files / 708,928,971 bytes including the release manifest;
  - rollback archive
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.6.1_20260713_190632`.
- Packaged runtime verification:
  - MT5 connected to MetaQuotes-Demo, read-only, `tradeAllowed=false`;
  - local Jyotish ready on `qwen2.5:3b` with 4,565 chunks, analysis-only;
  - refresh current through the 2026-07-13 14:00 UTC H1 close;
  - frozen trial ID unchanged at
    `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`;
  - shadow chain valid: 7 abstain decisions, 0 settled, 7 pending, execution false.
- Verification: frontend lint, 8 Vitest tests, 38 backend tests, 4 focused layout tests,
  production build, focused Ruff, packaged hash/manifest/API/DOM QA, and
  `git diff --check` passed.
- Evidence is in `chart_layout_square9_release_20260713.md`.
- Next recommended work:
  1. collect and settle the frozen prospective cohort without changing policy;
  2. externally certify Shadbala/Drik calculations;
  3. validate Square of Nine and other manual Gann geometry out of sample before allowing
     any inference use;
  4. keep order placement disabled unless a separate execution project is explicitly
     authorized and validated.

## Previous Update - 2026-07-13 (Frozen Prospective Trial Manifest)

- Promoted Gann Astro Desk to native release `0.6.1` and froze the existing
  prospective shadow sample under `GANN_FROZEN_PROSPECTIVE_SHADOW_TRIAL_V1`.
  Its trial ID is
  `2E25E421CADE41689806F23319ED937973CA0EDEE38DF627CDAB4A8EBA5F8C16`.
- Added immutable SQLite manifest `app_shadow_trial_manifest` with UPDATE and DELETE
  guards. The first coherent cohort locks the ledger/decision/packet/outcome contracts,
  engine, policy, Raman astronomy contract, symbol, timeframe, 72-hour horizon, and
  statistical gate configuration. Later mismatches are rejected before ledger append.
- The seven pre-manifest decisions were migrated once through
  `existing_decision_backfill_v1`; all resolve to one valid cohort without rewriting the
  append-only decision chain. New decisions embed the same `trialIdentity` in their payload.
- The predeclared gate remains unchanged: 100 settled watch clusters, at least 10% watch
  coverage, Wilson 95% lower bound above 50%, exact two-sided binomial p-value below 0.05,
  positive mean signed 72-hour return, and at least four UTC calendar months. Execution is
  still locked regardless of gate status.
- Shadow Validation now displays the frozen trial fingerprint, engine/policy, integrity,
  `0 / 100` watch-cluster progress, `0 / 4` calendar-month progress, and next real 72-hour
  settlement. Live packaged state at verification:
  - chain valid; 7 decisions, all abstain; 0 settled and 7 pending;
  - first legal settlement `2026-07-16T04:00:00+00:00`; no outcomes currently due;
  - latest verified closed MT5 H1 bar `2026-07-13T10:00:00+00:00`;
  - active corrected artifact `tn_46ffe4254d23445c96cc220d2038202c`;
  - MT5 connected, `tradeAllowed=false`; shadow execution false;
  - local Jyotish ready on `qwen2.5:3b`.
- Split trial identity and summary logic into `gann-astro-desk/backend/shadow_trial.py`
  so the append-only ledger no longer owns a duplicate trial-policy implementation.
- Native release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - version `0.6.1`;
  - SHA-256 `772905ED308F58B46CAE7910ED8314DCA7D6B1DCE9877AE3478A46DE42DFD7DC`;
  - 1,657 files / 708,779,331 bytes;
  - release manifest now stores the portable relative executable name;
  - prior `0.6.0` archived under
    `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.6.0_20260713_154140`.
- Verification:
  - full Python suite: 109 passed;
  - focused shadow/refresh tests: 12 passed;
  - frontend Vitest: 5 passed;
  - Ruff, Oxlint, TypeScript/Vite, PyInstaller, release hash, packaged APIs, live database
    migration, packaged visual/DOM QA, browser console, and `git diff --check`: passed.
- Evidence is in `prospective_shadow_trial_manifest_20260713.md`.
- Chart-persistence audit: SQLite already preserves event-linked annotation pins, notes,
  and their chart state, but manual horizontal/vertical lines and Gann fans are still local
  React state and disappear after restart. The next drawing release should therefore add
  named layouts/autosave and versioned drawing storage before adding Square of Nine.
- Next recommended work:
  1. add named chart layouts, autosave, drawing templates, object tree, lock/hide, and
     JSON import/export so all manual drawings restore exactly;
  2. add a data-anchored Square of Nine research tool with center value, increment, rings,
     rotation direction, angle highlights, price/time projections, and persisted settings;
  3. keep Square of Nine and manual geometry outside live inference until separately tested;
  4. settle the frozen cohort only after each real 72-hour horizon and continue chain audits;
  5. externally certify Shadbala/Drik doctrine calculations.

## Previous Update - 2026-07-13 (TradingView-Style Terminal + First Live Refresh Audit)

- Promoted Gann Astro Desk to native release `0.6.0` with a chart-first graphite market
  terminal: compact command bar, fixed OHLC readout, TradingView-style drawing rail with
  undo, chart focus mode, collapsible aspect inspector and activity dock, layer controls,
  live read-only status bar, chart PNG command, and responsive desktop behavior.
- Added an always-visible `Auto refresh` control. It displays the closed-bar supervisor
  state and can request the existing guarded check immediately; it cannot bypass freshness,
  close finalization, immutable snapshot promotion, corrected-artifact verification, or the
  execution lock. A manual packaged-UI check created no duplicate; later runs began only
  when the 06:00 and 07:00 UTC bars became eligible.
- Panel and layer preferences now persist through `schema_meta.workspace_preferences_v1`
  instead of depending on a random private loopback origin. `GET/PUT
  /api/workspace-preferences` supports partial updates, accepts only JSON booleans, and
  explicitly closes its SQLite handles.
- Audited the first seven real automatic H1 cycles, closed at 01:00 through 07:00 UTC on
  2026-07-13. All completed successfully and activated distinct corrected artifacts. The
  latest active artifact is `tn_53277139e4354e54bbff9a28e5b2b12c` with 39 events and 17
  touches through the 07:00 UTC closed bar.
- A 98-check lineage audit passed across snapshot manifest/parquet hashes, promoted-source
  identity, run/artifact cutoff identity, artifact price provenance, event/touch hashes and
  counts, outcome-label exclusion, refresh run identity, and execution lock. Evidence is in
  `prospective_refresh_live_audit_20260713.md`.
- The audit found one recordkeeping-only issue: four completed run rows retained inherited
  prior-artifact provenance even though their generated artifacts were correct. The
  supervisor now writes current source provenance before queueing, replaces completed run
  parameters with verified artifact parameters, and performs a guarded startup repair only
  when artifact ID, refresh run ID, source close, and price-source ID all agree. All five
  existing rows are now reconciled, and later runs were written correctly at completion.
- Packaged runtime checks:
  - MT5 connected; `tradeAllowed=false`;
  - refresh `up_to_date` at `2026-07-13T07:00:00+00:00`;
  - append-only shadow chain valid with 7 decisions and outcomes still pending;
  - local Jyotish ready on `qwen2.5:3b`;
  - layout preferences persisted and were restored to inspector/dock/aspects/SR visible;
  - packaged focus, restore, aspect, SR, and Auto Refresh controls passed browser checks.
- Native release:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - version `0.6.0`;
  - SHA-256 `59AAC283334B5045DF7909A4CE21DE20D09864F7B71ACCCC32D98A8299921D12`;
  - 1,657 files / 708,767,866 bytes;
  - application remains analysis/read-only and is running for continued prospective capture.
- Verification:
  - full Python suite: 107 passed;
  - frontend Vitest: 5 passed;
  - focused refresh, shadow, and preference API tests: 12 passed;
  - Ruff, Oxlint, TypeScript/Vite production build, PyInstaller packaging, release hash,
    packaged APIs, source visual QA, packaged DOM/control QA, and `git diff --check`: passed.
- Next work:
  1. collect the frozen prospective shadow sample without changing policy thresholds;
  2. settle outcomes only after their real 72-hour horizon and continue chain audits;
  3. externally certify Shadbala/Drik doctrine calculations;
  4. keep all order placement disabled unless a later validated execution project is
     separately and explicitly authorized.

## Previous Update - 2026-07-13 (Automatic Prospective Refresh + Local Jyotish)

- Added `gann-astro-desk/backend/prospective_refresh.py` with contract
  `GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1`. The background supervisor polls MT5, accepts only
  a recent fully closed M30/H1 source bar after a finalization grace period, captures an
  immutable closed-bar snapshot, promotes it through the existing SHA-256 price-source
  contract, queues the corrected Raman TN generator, activates only its verified completed
  artifact, and then wakes the append-only shadow ledger.
- Refresh runs are durable and idempotent by source-bar close time in
  `app_prospective_refresh_runs`. Restarted pre-queue work is failed honestly, active
  generation jobs are reconciled, simultaneous user generation is respected, and a manual
  `Refresh source` request only wakes the same safety checks; it cannot bypass freshness.
- Corrected artifact parameters now carry `priceSourceLastBarCloseUtc`. Shadow freshness uses
  the actual last closed market bar instead of the file-capture timestamp, preventing a
  weekend snapshot from making stale market data appear fresh.
- Current packaged state is intentionally `market_stale`: latest MT5 H1 close is
  2026-07-11 00:00 UTC, so no refresh run, artifact, or ledger decision was fabricated.
  The worker will resume automatically after a genuinely fresh closed bar arrives.
- Added `gann-astro-desk/backend/local_jyotish.py` and a native `Local Jyotish` Analyze
  Aspect tab. The app starts the portable Ollama runtime from `D:\Ollama` when needed and
  packages `jyotish_agent/corpus_chunks.jsonl` without duplicating model weights.
- Local contract `GANN_LOCAL_JYOTISH_RAG_DRAFT_V1` uses the selected occurrence's
  deterministic context plus 4,565 local chunks. Retrieval policy
  `balanced_classical_commentary_same_family_v2` separates 3,787 classical-doctrine chunks,
  761 secondary/user-reference chunks, and 17 local-research chunks; local notes are admitted
  only when they match the selected family.
- Every local draft is visibly untrusted, includes retrieved citations and a deterministic
  post-draft verifier, and declares that it is not official, not consumed by live inference,
  not consumed by the shadow ledger, and cannot execute. A real no-evidence occurrence test
  made Qwen decline to invent strength/SR conclusions and the verifier correctly required
  review when the model omitted inline citation ids.
- The app defaults to `qwen2.5:3b`. `gemma4:12b` is installed but its 11.9B Q4 runtime failed
  to load reliably after partial GTX 1060 offload, so it is not presented as the working
  default. Model fallback remains supported.
- Added APIs:
  - `GET /api/prospective-refresh` and `POST /api/prospective-refresh/run`;
  - `GET /api/local-jyotish/health` and `POST /api/local-jyotish/analyze`;
  - `/api/shadow-ledger` now includes refresh state for the native dock.
- Native release promoted to `0.5.0`:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `343FF5C9AC1F62A1CD2B866D4974942CA6D6A8A5B8B1C8A13084973E76C481C4`;
  - 1,657 files / 708,788,848 bytes;
  - packaged corpus: 10,331,989 bytes;
  - astronomy contract unchanged; MT5 and both AI surfaces remain analysis/read-only.
- Verification:
  - full Python suite: 104 passed;
  - native backend suite: 29 passed, including 7 refresh/local-Jyotish tests;
  - frontend Vitest: 5 passed;
  - Ruff, Oxlint, TypeScript/Vite production build, `git diff --check`, native packaging,
    source UI, packaged APIs, packaged UI, and browser logs: passed;
  - packaged API confirmed `tradeAllowed=false`, refresh/ledger execution false, valid empty
    chain, zero refresh runs during stale market, local model ready, and balanced layer counts.
- Next work:
  1. leave the app running through the next fresh market H1 close and audit the first real
     snapshot -> promotion -> corrected artifact -> shadow capture lineage end to end;
  2. collect the frozen prospective sample without changing policy or gate thresholds;
  3. externally certify Shadbala/Drik doctrine calculations;
  4. keep all order placement disabled unless a later validated execution project is
     separately and explicitly authorized.

## Previous Update - 2026-07-13 (Append-Only Prospective Shadow Ledger)

- Added `gann-astro-desk/backend/shadow_ledger.py` with the contracts
  `GANN_APPEND_ONLY_SHADOW_LEDGER_V1`, `GANN_PROSPECTIVE_SHADOW_DECISION_V1`,
  and `GANN_PROSPECTIVE_72H_OUTCOME_V1`. The ledger records watch and abstain
  decisions prospectively from server UTC and live read-only MT5 bars; the client cannot
  provide a historical decision time, and the retrospective baseline is explicitly blocked.
- Prospective capture requires a non-built-in generated artifact with complete creation and
  source-as-of provenance, a price snapshot no older than one source timeframe plus 15
  minutes, a just-closed touch within that same freshness window, and source data containing
  the signal bar. Stale or baseline artifacts are reported honestly and cannot be backfilled.
- Added append-only SQLite table `app_shadow_ledger_entries`. Decisions and 72-hour outcomes
  are separate immutable entries with contiguous sequence numbers, canonical payload hashes,
  previous-entry hashes, and a verified SHA-256 chain. Database triggers reject UPDATE and
  DELETE. A 72-hour outcome is appended only after the first fully closed MT5 bar at or after
  the frozen anchor plus 72 hours.
- The shadow supervisor scans every 30 seconds by default, settles mature outcomes, and is
  idempotent across restarts. It never emits an order, fill, entry/exit price, transaction
  cost, or retrospective P/L. Simultaneous event decisions are clustered before statistics
  so overlapping events do not inflate the sample.
- The predeclared prospective gate requires at least 100 watch clusters, at least 10% watch
  coverage, Wilson 95% lower bound above 50%, exact two-sided binomial p-value below 0.05,
  positive mean signed 72-hour return, and at least four UTC calendar months. Execution
  remains locked even if those research criteria eventually pass.
- Added native APIs `GET /api/shadow-ledger` and `POST /api/shadow-ledger/scan`, plus a dense
  desktop `Shadow validation` panel showing chain state, immutable counts, pending outcomes,
  hit rate, gate progress, execution lock, readiness, and the decision/outcome trail.
- Corrected the historical evaluator's 72-hour label availability: `after72_time_local` is
  the target bar's open timestamp, so the label becomes usable only when that bar closes.
  The report was regenerated; frozen metrics remain 258 watches, 140 hits, 54.26%, Wilson
  48.17%-60.24%, and p=0.190975, so the historical statistical gate still fails.
- Native release promoted to `0.4.0`:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `89D51514AFD96B3FD0B995CE354FB7F3231C156396E019850D39825F4DA865AF`;
  - 1,656 files / 698,374,484 bytes;
  - astronomy contract unchanged and MT5 remains `read_only_market_data`.
- Verification:
  - full Python suite: 97 passed;
  - native backend suite: 22 passed, including 5 focused shadow-ledger tests;
  - frontend Vitest: 5 passed;
  - Ruff, Oxlint, TypeScript/Vite production build, `git diff --check`, native packaging,
    packaged API, and packaged visual QA: passed;
  - packaged manual scan left the chain valid with zero entries and reported
    `artifact_price_snapshot_stale`; browser warnings/errors were empty.
- Current operational state: the active July research artifact is too old for prospective
  capture, so the ledger correctly starts at zero. Do not loosen freshness or backfill it.
- Next work:
  1. add an automatic just-closed MT5 snapshot, promote, and corrected-artifact refresh
     pipeline so fresh eligible touches can enter the prospective ledger unattended;
  2. collect the frozen prospective sample without changing policy thresholds mid-run;
  3. externally certify Shadbala/Drik doctrine calculations;
  4. keep all order placement disabled unless a later validated execution project is
     separately and explicitly authorized.

## Previous Update - 2026-07-13 (Purged Timestamp-Safe Policy Validation)

- Corrected a chronology defect in native `Analyze Aspect`: a selected historical touch now
  becomes eligible at the close of its source candle, while event end remains the eligibility
  deadline. The previous `max(event_end, touch_close)` display cutoff could move inference
  beyond the 72-hour outcome label for long aspects even though the shared engine itself did
  not require event end.
- Added `evaluate_timestamp_safe_decisions.py`, a frozen purged/embargoed evaluator that calls
  the real `decision_engine.live_inference_packet` for every retained SR touch. It excludes
  forbidden future/outcome fields, quarantines labels already available at decision time,
  prevents identical decision timestamps from crossing folds, clusters simultaneous events
  into one market decision, and admits training labels only after the full 72-hour outcome
  horizon plus a 72-hour embargo.
- Added `test_evaluate_timestamp_safe_decisions.py`. Its tests cover touch-close timing,
  label-availability purging, embargoed history, equal-time fold boundaries, simultaneous
  decision clustering, future-label packet invariance, and already-known-label quarantine.
- Frozen baseline result is recorded in `timestamp_safe_decision_walk_forward_20260713.md`:
  - 754 source touches; 753 timestamp-valid packets; 1 quarantined flat label;
  - 355 unique out-of-sample decision clusters; 258 watches and 97 abstentions;
  - 140/258 correct = 54.26% hit rate, with Wilson 95% interval 48.17%-60.24%;
  - exact two-sided p-value versus 50% = 0.191;
  - balanced direction accuracy 55.91%; training-majority baseline 43.41%;
  - mean signed 72-hour return +0.0276% before costs, but only 3/5 folds were positive.
- The predeclared statistical gate therefore **failed**: the confidence interval crosses 50%,
  p-value is not below 0.05, and the positive-fold requirement was not met. These results are
  descriptive historical evidence only, not a trading certificate.
- Engine version is now `timestamp_safe_auto_suggest_v1_1_20260713`. Every live packet exposes
  `failed_retrospective_statistical_gate_20260713`, links the tracked validation report, requires
  prospective validation, and keeps execution disabled. Analyze Aspect visibly shows
  `Historical gate failed` and remains a research-watch surface.
- Native release promoted to `0.3.1`:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `0517656542BE12D8BECF7E6EE2E4DCD2C2991FFCE0D234AAB19E9514D7693308`;
  - 1,656 files / 698,340,280 bytes;
  - MT5 remains `read_only_market_data`.
- Verification:
  - full Python suite: 92 passed;
  - native backend suite: 17 passed;
  - frontend Vitest: 5 passed;
  - Ruff, Oxlint, TypeScript/Vite production build, packaged visual QA, and packaged API: passed;
  - packaged API confirmed touch-close decision time equals source-data maximum, no-lookahead
    true, execution false, failed-gate lock present; the July 2026 active artifact was restored
    after the reversible baseline smoke test.
- Next gates:
  1. run a prospective, append-only shadow-decision ledger before reconsidering the policy;
  2. externally certify Shadbala/Drik doctrine calculations;
  3. if the shadow sample is adequate, evaluate the same frozen metrics with spread/slippage;
  4. do not add MT5 order placement unless a later validated execution project is explicitly
     authorized.

## Previous Update - 2026-07-13 (Unified Timestamp-Safe Decision Engine)

- Added root `decision_engine.py` with the shared packet contract
  `GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1`, engine version
  `timestamp_safe_auto_suggest_v1_20260712`, and two explicit modes:
  `research_replay` and `live_inference`.
- Retrospective `reviewer_rule_replay.auto_suggest_case` still performs the existing
  completed-chart marker replay, but now returns the shared packet and declares its
  known-outcome/future-price-path use. Replay packets are always timestamp-unsafe,
  no-lookahead false, outcome-consumed, future-prices-consumed, and live-ineligible.
- Browser Auto Suggest remains executable only through `POST /api/auto_suggest` and the
  Python replay engine. The archived JavaScript decision body is unwired and now throws
  immediately if called, preventing a second executable policy from drifting silently.
- Added native `POST /api/decisions`, which accepts `live_inference` only. Research replay
  requests are rejected. Live decisions use only a closed selected-touch candle, closed
  price evidence through the decision cutoff, and an explicit feature allowlist. The
  repository physically loads only the safe scorer/context fields; outcome labels, future
  returns, edge scores, MFE/MAE, P/L, special traits and rule lessons are not loaded into the
  native inference row.
- Live policy `fx_doctrine_consensus_watch_only_v1` emits `WATCH_LONG`, `WATCH_SHORT`, or
  `ABSTAIN` only when the raw and doctrine USD-minus-JPY hypotheses agree. It never creates
  an entry price/time, exit price/time, P/L, outcome, or MT5 order. Execution remains locked.
- Timestamp rules are explicit: the touch must lie inside its event window; the touch bar
  must close before it becomes evidence; and one source-timeframe of post-window grace is
  allowed only so the final overlapping bar can close. Packet validation rejects future
  price evidence, outcome/fill/exit injection, unavailable watch signals, and watches outside
  the decision deadline.
- Analyze Aspect now shows a dedicated `Timestamp-safe inference` panel with action/reason,
  decision cutoff, signal-availability time, closed-evidence time, packet ID, evidence, and
  visible `timestamp safe`, `no lookahead`, `outcome excluded`, and `execution locked` badges.
  Its historical inspection cutoff is the later of event end or the selected touch-bar close.
- Real retained July artifact smoke (`tn_2beda5f38c4f4cc2bb866fa88c174bf2`): all 12 touch
  events were processed by the packaged endpoint; 5 produced provisional `WATCH_SHORT` and
  7 abstained because raw/doctrine evidence was unknown or conflicted. No live packet carried
  an outcome or execution permission. Packaged visual QA on `TN::MERCURY->MARS::trine`
  displayed `WATCH SHORT` cleanly and browser logs contained no warnings/errors.
- Native release promoted to `0.3.0`:
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `6C22ECE1038A98FCE3B46FFBCC6E1C0E5047BB1AB702B2E18CED591E5AD5557B`;
  - 1,656 files / 698,339,468 bytes;
  - astronomy contract remains `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`;
  - MT5 execution mode remains `read_only_market_data`.
- Verification:
  - full Python suite: 86 passed;
  - native backend suite: 17 passed;
  - frontend Vitest: 5 passed;
  - Oxlint, TypeScript/Vite build, `git diff --check`, packaged API, and packaged UI: passed.
- Remaining deliberate gates:
  1. run purged/embargoed out-of-sample evaluation of timestamp-safe packets before changing
     watch-only status;
  2. externally certify Shadbala/Drik calculations before treating astrology doctrine as
     production evidence;
  3. migrate retrospective P/L, rule lessons, Dream Review, and official-note processing into
     typed research-only contracts without exposing them to live inference;
  4. physically delete the now-disabled JavaScript archive after any final historical parity
     work; it is not executable now;
  5. MT5 order placement stays disabled until the user separately authorizes an execution
     project after validation.

## Previous Update - 2026-07-12 (Durable Corrected-Data Generation)

2026-07-12 third Windows-app vertical slice:

- Added a durable corrected transit-to-natal generation queue. Jobs are persisted in
  SQLite, run in isolated hidden subprocesses, report honest stage/progress state, support
  cancellation, resume queued work after restart, and mark interrupted running work failed
  instead of pretending it completed.
- Added a versioned corrected-data artifact registry under
  `D:\GannFinancialAstro\app_artifacts`. Every completed artifact has inspectable generator
  logs, canonical SR inputs, a manifest, SHA-256 hashes, astronomy-contract validation, and
  event/touch row counts before it can be registered or activated.
- Added schema-version-4 tables `app_generation_jobs` and `app_data_artifacts`, plus backend
  APIs to create/list/cancel jobs, list artifacts, and activate either a generated artifact
  or the versioned baseline. Dataset activation swaps event/touch indexes atomically under a
  repository lock; invalid or partial artifacts never replace the working chart source.
- Extended the corrected generators so custom SR configuration is canonical JSON, reference
  times accept seconds, fixed-offset locations are parsed correctly, and a valid empty touch
  artifact can be emitted when an event source has no SR touch.
- Added the parameter-drawer generation workspace with Generate, Cancel, job progress/error,
  artifact history, and activation controls. A research-mode watcher refreshes the chart and
  Analyze Aspect data when a completed job auto-activates, even if the drawer was closed.
- Corrected touch-only filtering to use the explicit event-to-touch join and retained the
  generated deterministic astro fields for Analyze Aspect evidence instead of reducing touch
  rows to plotting coordinates.
- End-to-end proof generation produced `1` corrected event and `1` SR touch; the activated
  artifact exposed `22` deterministic evidence fields in event detail. The same artifact was
  exercised through the real HTTP queue and browser UI, then the versioned baseline was
  restored and all proof rows/directories were removed.
- Verification completed:
  - backend unittest: 11 passed;
  - frontend Vitest: 5 passed;
  - Python compile, Oxlint, and production TypeScript/Vite build: passed;
  - browser check: nonblank generated chart, visible 100% completed job, correct artifact
    counts, clean baseline restoration, and no browser-console errors or warnings.
- Remaining app work, in order:
  1. add a timestamped MT5 history snapshot/ingestion step so corrected TN generation can
     cover dates after the current versioned source endpoint of 2026-03-10;
  2. migrate deterministic Auto Suggest, trade markers, P/L, rule lessons, Dream Review,
     and the official-note queue into shared app/backend contracts;
  3. consolidate browser and Python decision logic into one timestamp-safe no-lookahead engine;
  4. implement and certify the corrected transit-to-transit generator;
  5. freeze/sign Python and Node sidecars and complete native packaging after Rust/MSVC is
     installed on `D:`.

## Previous Update - 2026-07-12 (Parameterized Charts and Live MT5)

2026-07-12 second Windows-app vertical slice:

- Added a typed parameter contract and persistent SQLite parameter profiles for symbol,
  research/live source, timeframe, date range, transit-to-natal body filters, aspects,
  excluded families, touch linkage, duration, harmonics, n values, degrees, SR tolerances,
  and birth/IPO reference metadata.
- Added a responsive parameter drawer with saved profile create/load/delete, explicit
  `rebuild input` labels for settings that require a new corrected source, and a disabled
  transit-to-transit option until a corrected TT generator exists. Applying parameters never
  silently claims to regenerate ephemeris data.
- Historical chart loading now supports M30, H1, H4, and D1. M30 and H1 use versioned MT5
  parquet sources; H4 and D1 are deterministically resampled from H1. Existing corrected TN
  events can be filtered by transit body, natal body, aspect, family, touch linkage, and
  duration without changing their astronomical identities.
- Added read-only MT5 bar retrieval for M30/H1/H4/D1 and a five-second live chart refresh.
  Live updates replace series data in place so zoom and pan state are not reset. The gateway
  remains market-data only: `tradeAllowed=false`; no order method exists.
- The live backend smoke check connected to `MetaQuotes-Demo` and returned 120 USDJPY H1 bars.
  Current Jul-2026 live bars have no corrected aspect overlays because the versioned TN source
  ends on 2026-03-10; future/upcoming corrected event generation is still required.
- Updated the app database to schema version 3 with `app_parameter_profiles`. The profile API
  create/list/delete smoke test passed and left no test profile behind.
- Verification completed:
  - frontend Vitest: 5 passed;
  - backend unittest: 8 passed;
  - Oxlint: passed;
  - production TypeScript/Vite build: passed;
  - browser checks: nonblank historical M30 chart, corrected event/body filters, saved drawer
    state, nonblank MT5 live chart, and no post-refactor browser-console errors.
- Remaining app work, in order:
  1. add a background corrected-TN generation queue, progress/cancel states, artifact registry,
     and atomic loading of generated datasets into the chart and Analyze Aspect workspace;
  2. extend corrected event generation into the current/future live date range;
  3. migrate deterministic Auto Suggest, trade markers, P/L, rule lessons, Dream Review,
     and official-note queue into shared app/backend contracts;
  4. consolidate browser and Python decision logic into one timestamp-safe no-lookahead engine;
  5. complete native sidecar packaging after the Rust/MSVC toolchain gate is installed on `D:`.

## Previous Update - 2026-07-11 (Gann Astro Desk)

2026-07-11 first Windows-app vertical slice:

- Added `gann-astro-desk`, a Tauri-ready React/TypeScript desktop surface with a quiet
  chart-first operational design. The supported runtime is currently Vite at
  `http://127.0.0.1:5173`; native installer packaging is not yet complete.
- Main workspace uses real corrected data:
  - 1,268 directional Raman transit-to-natal events from
    `astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet`;
  - USDJPY H1 candles from the versioned MT5 parquet source;
  - 754 corrected planetary SR touches explicitly joined from
    `aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv`.
- Added clickable aspect windows and a detachable `Analyze Aspect` family window with:
  - all previous occurrences, filters, previous/next navigation, outcome summaries,
    deterministic astro evidence, and persistent reviewed/pending progress;
  - chart tools for horizontal/vertical lines, two-anchor Gann fans, reset, and clear;
  - structured chart annotations persisted with exact time, price, event, family,
    selected target, note, and chart state.
- Added read-only MT5 supervisor with heartbeat/reconnect. Live smoke check connected to
  `MetaQuotes-Demo` and returned a current USDJPY bid/ask; `tradeAllowed=false` and
  `executionMode=read_only_market_data` are enforced.
- Added a local `@openai/codex-sdk` bridge for family-scoped Codex analysis. Each question
  receives deterministic case context, the selected annotation, and a local chart PNG.
  It has no MT5 order capability and does not promote LLM prose to official evidence.
  Bridge health passed; a real reply was blocked by the local Codex usage limit until its
  stated reset time, and the UI reports that error rather than fabricating a response.
- Updated `gann_aspect_annotations_raman_v2.sqlite` to app schema version 2 with empty,
  non-destructive `chart_annotations`, `app_occurrence_progress`, and
  `app_codex_threads` tables. New app progress remains separate from legacy completed reviews.
- Added a Tauri 2 shell/config under `gann-astro-desk/src-tauri`. `npx tauri info` parses
  the app, but confirms Rust/Cargo and Microsoft C++ build tools are absent. Install them
  on `D:` and freeze/sign the Python and Node services as sidecars before producing an installer.
- Verification completed:
  - frontend production build: passed;
  - Oxlint: passed;
  - Vitest: 2 passed;
  - backend unittest: 4 passed;
  - Python compile and Node syntax checks: passed;
  - live browser checks: nonblank main chart, SR lines, family recurrence window,
    review persistence, annotation create/delete, and embedded Codex panel all passed;
  - browser console: no errors or warnings.
- Remaining app work, in order:
  1. implement the parameter editor and generation jobs for symbol, date range, timeframe,
     n/f/degree, birth/IPO chart, location, planets, aspects, pair exclusions, and TT/TN mode;
  2. merge live MT5 candle/tick updates into the displayed series (current MT5 connection is
     supervised, while chart history remains the versioned parquet snapshot);
  3. migrate deterministic Auto Suggest, trade markers, P/L, rule lessons, Dream Review,
     and official-note queue into shared app/backend contracts;
  4. consolidate browser and Python decision logic into one no-lookahead engine;
  5. package the Python backend and Codex bridge as signed Tauri sidecars, then build the
     Windows installer after the `D:`-hosted Rust/MSVC gate is satisfied.

## Previous Update - 2026-07-11

2026-07-11 end-to-end financial astrology code/data/doctrine audit:

- Added `end_to_end_financial_astro_audit_20260711.md`. Read it before any rebuild, review,
  RAG refresh, demo order, or new rule. The headline is important:
  - the legacy USDJPY natal-event source used a double sidereal adjustment for the 1889 reference
    chart and tropical houses beside sidereal planets;
  - its logger also sorted body labels, losing transit/natal orientation;
  - therefore the current event/touch/case database and reviewed case IDs are preserved as
    `legacy_double_sidereal_research_history`, not valid live/ML ground truth.
- Added canonical `financial_astro_ephemeris.py` and `astro_event_contract.py`:
  - Raman Swiss-Ephemeris positions are sidereal exactly once;
  - true node/Ketu and sidereal Porphyry cusps are explicit;
  - longitude caches use a full timestamp-index digest;
  - all new events carry `event_scope`, transit/natal bodies, astronomy contract version, and
    geometry status.
- Corrected a source proof run:
  - a March TN rebuild produced 16 events, maximum inferred orb `0.349` degrees;
  - a corrected touch proof produced 14 rows, maximum orb `0.263` degrees;
  - old `AVG(ALL)|MOON square` reviews do not map to the corrected event identities.
- The active SR chart/log builders (`sr_touch_lazy_dashboard.py`, `sr_lazy_reactive_dashboard.py`,
  `build_pair_aspect_market_log.py`, `build_sr_anchor_reversal_log.py`,
  `generate_sr_candidate_chart_pack.py`) now use exact canonical longitude series instead of
  external JDML/adaptive forward-filled ephemeris series.
- RAG now quarantines rule notes and touch rows without a supported
  `RAMAN_SWISSEPH_SINGLE_SIDEREAL_*` contract, so legacy case prose cannot return as evidence.
- Updated strict-Shadbala labeling/logic to source-aligned provisional V4. Fixed Drekkana,
  Moon Paksha, Sun Ayana, and luminary Chesta handling; full Kaala/Chesta/Yuddha remains pending
  external certification and must not be called fully strict/certified.
- Walk-forward evaluator now uses a real outcome-horizon embargo, training-slice-only feature
  selection, and excludes same-bar entry/touch leakage. It remains exploratory due to small,
  high-dimensional data.
- `generate_upcoming_aspects.py` has scoped TT family keys and does not implicitly transfer old TN
  family learning. `reviewer_rule_replay.py` protects completed ignored cases.
- Certification now defaults to `astro_certification_4_gate_v2_20260711`; Gate 4 is deliberately
  `blocked_legacy_dataset` unless an explicit historical archive replay is requested.
- Added `requirements.txt`, `requirements-dev.txt`, `pytest.ini`, regression tests, and historical
  banners on older May reports. Deleted the six-line `sr_touch_lazy_dashboard_restored.py` stub.
- Verification completed:
  - `python -m pytest`: 53 passed;
  - canonical Python compile: passed;
  - Ruff: passed;
  - `git diff --check`: passed (line-ending warnings only).
- Next non-negotiable work, in order:
  1. freeze/backup old SQLite and source data as legacy history;
  2. replace or vendor the remaining recovery-only external `JDML4.py` source generator;
  3. rebuild full corrected TN event/touch/candidate data under a new versioned DB namespace;
  4. re-review or explicitly migrate observations without copying old astronomical labels;
  5. consolidate browser/Python Auto Suggest into one deterministic engine;
  6. build a timestamp-safe live policy only after purged out-of-sample validation.

## Previous Update - 2026-07-11

2026-07-11 BPHS and Phaladeepika provenance-aware corpus ingestion:

- Ingested `BPHS`, an 1899 Mumbai Sanskrit-Hindi `Brihat Parashara Hora Shastra` Purva/Uttara witness:
  - 745 PDF/OCR pages retained;
  - PDF SHA-256 `BB556804D8D546ACC39C43A22CECDBE2C29E3A7BA157E60EEC810C478EB645A4`;
  - explicitly labeled recension-specific rather than merged with modern 97-chapter English editions;
  - English doctrinal claims require an identified translation or human verification.
- Ingested `PHALADEEPIKA`, Mantreswara with V. Subrahmanya Sastri's first English translation edition, 1937:
  - 476 PDF pages, 464 non-empty OCR page blocks retained;
  - PDF SHA-256 `795DDB67D7416188B2272D2021B2B798561FAAAC08067A986AF0FACFD0552FCB`;
  - all 28 adhyayas plus verse and subject indexes are present.
- Rights caveat is permanent corpus metadata: the Digital Library of India catalog says `In Public Domain`, while the title page says `Copyright Registered`. Phaladeepika remains local research material pending any redistribution-rights review.
- Source PDFs and IA DjVu OCR XML are archived under `D:\GannFinancialAstro\sources\classical`; generated page-marked corpus text remains local/uncommitted under `jyotish_agent\corpus_text`.
- Extended every classical page block with `LANGUAGE`, `RECENSION`, `RIGHTS_BASIS`, and `RETRIEVAL_CAUTION` markers.
- Fixed a Unicode topic-classification bug: the previous ASCII-only normalizer reduced Devanagari keywords to empty strings and falsely tagged every BPHS page with every topic. Matching now preserves Unicode alphanumeric characters and rejects empty normalized patterns.
- Added `bphs_phaladeepika_source_review_20260711.md` with edition maps, rights findings, visual spot checks, hashes, retrieval locks, and promotion policy.
- Visually inspected BPHS pages 4, 30, 326, 665, 741 and Phaladeepika pages 6, 38, 80, 229, 360, 394. BPHS has physical damage but readable text; Phaladeepika is clean enough for English retrieval, with Sanskrit exact quotes still requiring page-image checks.
- Rebuilt private TF-IDF index:
  - total `4,565` chunks;
  - BPHS `1,351` chunks;
  - Phaladeepika `684` chunks.
- Retrieval checks:
  - Devanagari Dasha/graha/bala/Ashtakavarga query returned BPHS in all top-six results;
  - English strength/Drigbala/Dasa/transit query returned Phaladeepika in the top two;
  - case 43 no-LLM smoke still returned structured workspace evidence plus page-cited doctrine/reference material.
- Six stdlib ingestion/index tests pass.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260711_083631` (includes both generated corpus text files; the hashed source PDFs/OCR XML remain in the `D:` source archive).
- No calculation, aspect event, trade label, Auto Suggest, official ML note, BTC/USDJPY strategy, or MT5 execution logic changed.

## Previous Update - 2026-07-11

2026-07-11 first classical public-domain corpus ingestion:

- Ingested three identified historical English editions into the private local Jyotish RAG corpus:
  - `BRIHAT_JATAKA`: Varahamihira, N. Chidambaram Aiyar, second edition 1905, 306 PDF pages;
  - `BRIHAT_SAMHITA`: Varahamihira, N. C. Iyer, Parts I-II 1884-1885, 496 PDF pages;
  - `SURYA_SIDDHANTA`: Ebenezer Burgess with the Committee of Publication, 1858, 362 PDF pages.
- Wikimedia Commons identifies the three source editions as public domain/public-domain-mark and links to their Internet Archive originals.
- Archived source PDFs and page-structured Internet Archive DjVu OCR XML under:
  `D:\GannFinancialAstro\sources\classical`.
- Added `jyotish_agent/classical_source_editions.yaml` with edition, translator, rights, source URLs, section ranges, topics, PDF SHA-256 and OCR XML MD5.
- Added `jyotish_agent/ingest_classical_sources.py`:
  - verifies PDF and OCR hashes before processing;
  - checks expected OCR page count;
  - rebuilds page-cited local corpus text;
  - distinguishes front matter, translator material, root translation-with-notes and appendices/indexes.
- Added `classical_text_ingestion_review_20260711.md` with source-quality findings, visual checks, relevance and promotion locks.
- Retained page blocks:
  - Brihat Jataka `295`;
  - Brihat Samhita `489`;
  - Surya Siddhanta `362`.
- Generated text remains local/uncommitted under `D:\PycharmProjects\jyotish_agent\corpus_text`.
- Rebuilt private TF-IDF index:
  - total chunks `2,530`;
  - Brihat Jataka `341`;
  - Brihat Samhita `611`;
  - Surya Siddhanta `800`;
  - missing page/authority markers across these sources `0`.
- Updated local case explanation retrieval to reserve four slots for structured workspace evidence and four for doctrine/reference sources. This fixes the prior condition where case notes occupied all eight slots and classical sources never reached the LLM prompt.
- Dedicated source queries returned each expected classical source within the top three results; a case 43 no-LLM smoke test returned both rule-note evidence and page-cited doctrine.
- Updated corpus manifest, ingestion queue, PDF inventory and ranked corpus canon.
- Added ingestion/retrieval regression coverage; all five stdlib unit tests pass.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260711_070637` (includes the three generated local corpus text files; source PDFs/OCR XML remain in the hashed `D:` archive).
- No astrology calculation, market label, Auto Suggest, official ML note or MT5 execution logic changed. Surya Siddhanta is historical context and does not replace Swiss Ephemeris.

## Previous Update - 2026-07-11

2026-07-11 Sanjay Rath source audit and provenance-aware classical corpus:

- Fully audited the user-supplied image-only PDF `Crux of Vedic Astrology - Timing of Events` by Sanjay Rath:
  - 600 PDF pages / 589 numbered pages;
  - first edition in the scan dated 16 June 1998;
  - SHA-256 `E3307EDE78737E4E35E78B042A0CFD19CAB6CD46234087173AFD62203080AF9A`;
  - archived off `C:` at `D:\GannFinancialAstro\doc\Crux of Vedic Astrology-Timing of Events -- Sanjay Rath -- 1998.pdf` with the hash verified after the move.
- Rendered and visually checked front matter and representative chapter pages, then completed local OCR for all 600 pages.
- Added `sanjay_rath_crux_source_review_20260711.md`:
  - classifies the book as modern secondary interpretive commentary, not a classical root text;
  - maps all 15 chapters;
  - identifies Dasha selection, Narayana Dasha, Argala, Arudha, Hora Lagna, Sudarshana, Sarvatobhadra and Sahams as retrieval candidates;
  - explicitly blocks retrospective examples, mortality/medical/fertility material and natal statements from direct trading-rule promotion.
- Added `classical_jyotish_corpus_canon_20260711.md` with separate authority layers for:
  - astronomy/calculation history;
  - root predictive classics;
  - timing/Jaimini sources;
  - mundane context;
  - modern commentaries and experimental methods.
- Registered `SANJAY_RATH_CRUX_1998` in the local agent source registry and ingestion queue, and added discovery entries for Jaimini Upadesa Sutras, Sarvartha Chintamani, Tajika Nilakanthi and Yoga Yatra.
- Corrected stale `C:` paths in the corpus manifest to the active `D:` project/source locations.
- Full page-marked OCR text is local/uncommitted at:
  `D:\PycharmProjects\jyotish_agent\corpus_text\SANJAY_RATH_CRUX_1998.txt`.
- Updated `jyotish_agent/build_corpus_index.py` so page-marked sources never merge across page boundaries and every split chunk repeats its source/page metadata.
- Rebuilt the private local TF-IDF index:
  - total chunks: `778`;
  - Sanjay Rath chunks: `600`;
  - Sanjay chunks missing `PDF_PAGE`: `0`;
  - a mixed Narayana Dasha/Argala/Arudha/Hora Lagna/wealth query returned this source in all top-six results.
- Added `test_jyotish_corpus_index.py`; both page-citation regression tests pass under stdlib `unittest`.
- Updated the PDF feature inventory and local agent plan with the source authority hierarchy.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260711_063314` (includes the local OCR JSONL and generated page-marked corpus text, but not the 72.7 MB source PDF).
- No astrology formula, Auto Suggest rule, ML label or MT5 behavior changed. This work expands local explanation/RAG knowledge only.

## Previous Update - 2026-07-10

2026-07-10 BTC 3-week aspect filter:

- User clarified they meant removing aspects shorter than 3 weeks.
- Updated both BTC scripts:
  - `build_btc_weekly_astro_chart.py` default `--min-window-days` is now `21.0`;
  - `analyze_btc_aspect_effectiveness.py` default `--min-window-days` is now `21.0`.
- Reran evidence analyzer first so chart classification/noise exclusion uses the same 3-week filter:
  `D:\GannFinancialAstro\doc\btc_aspect_effectiveness_20260710_002051`
- Evidence counts with 3-week threshold:
  - historical windows >= 21 days: `119`;
  - analyzed events: `119`;
  - families: `72`;
  - `promising_candidate`: `2`;
  - `inconclusive`: `12`;
  - `inconclusive_low_repeatation`: `55`;
  - `noise`: `3`.
- Promising candidates remain:
  - `PLUTO|JUPITER::conjunction_orb`;
  - `NEPTUNE|SATURN::opposition_orb`.
- Noise candidates with 3-week threshold:
  - `SATURN|KETU::opposition_orb`;
  - `SATURN|RAHU::conjunction_orb`;
  - `URANUS|PLUTO::trine`.
- Rebuilt chart pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260710_002116`
- Main chart URL:
  `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=min21d_noise_excluded`
- Chart counts with 3-week threshold:
  - all generated windows before noise exclusion: `164`;
  - chart-visible windows after noise exclusion: `155`;
  - noise-excluded windows: `9`;
  - visible windows under 21 days: `0`;
  - all windows under 21 days: `0`;
  - minimum visible duration: `21.0` days.
- Server:
  - `127.0.0.1:8766` now serves `D:\GannFinancialAstro\doc\btc_weekly_astro_20260710_002116`;
  - HTTP check returned `200`.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py analyze_btc_aspect_effectiveness.py`;
  - `python analyze_btc_aspect_effectiveness.py`;
  - `python build_btc_weekly_astro_chart.py`.

## Previous Update - 2026-07-10

2026-07-10 BTC aspect family classification/noise exclusion:

- User defined family classification thresholds:
  - `promising_candidate`: at least 3 repeatations and >= 70% dominance in one clear bullish/bearish behavior;
  - `inconclusive`: at least 3 repeatations, directional evidence exists, but dominance is below 70%;
  - `noise`: at least 3 repeatations and less than 30% of repeatations produce any clear bullish/bearish behavior;
  - `inconclusive_low_repeatation`: any aspect family with fewer than 3 repeatations, regardless of apparent behavior, because future data could move it into promising/inconclusive/noise.
- Updated `analyze_btc_aspect_effectiveness.py`:
  - event rows now include `behavior_signal`;
  - short windows (`<= 7` weeks) map trough-only local turns to `bullish`, crest-only local turns to `bearish`, crest+trough to `mixed`, no turn to `no_signal`;
  - long windows (`>= 8` weeks) map start-to-end return to bullish/bearish only if it clears the move threshold;
  - summary rows now include `classification`, `classification_reason`, `dominant_behavior`, `dominant_behavior_rate`, `directional_signal_rate`, bullish/bearish/mixed/no-signal counts;
  - writes separate candidate CSVs:
    - `btc_aspect_promising_candidates.csv`;
    - `btc_aspect_inconclusive_candidates.csv`, including all low-repeatation families;
    - `btc_aspect_noise_candidates.csv`.
- Updated `build_btc_weekly_astro_chart.py`:
  - added `--aspect-classification-csv`, default `auto`;
  - chart generator auto-loads the latest `btc_aspect_effectiveness_summary.csv`;
  - aspect windows whose family classification is `noise` are excluded from chart overlays;
  - all raw windows are still saved to `btc_weekly_astro_windows_all.csv`;
  - chart-visible filtered windows remain in `btc_weekly_astro_windows.csv`;
  - metadata records classification CSV path, noise family count, and windows-before/after filter counts.
- New evidence output:
  `D:\GannFinancialAstro\doc\btc_aspect_effectiveness_20260709_235843`
- Classification counts from this run:
  - `promising_candidate`: `2`;
  - `inconclusive`: `13`;
  - `inconclusive_low_repeatation`: `77`;
  - `noise`: `4`.
- Promising candidates:
  - `PLUTO|JUPITER::conjunction_orb` bullish dominance `0.75`, directional signal rate `1.00`;
  - `NEPTUNE|SATURN::opposition_orb` bullish dominance `0.75`, directional signal rate `1.00`.
- Noise candidates excluded from chart overlays:
  - `SATURN|KETU::opposition_orb`;
  - `SATURN|RAHU::conjunction_orb`;
  - `JUPITER|VENUS::conjunction_orb`;
  - `URANUS|PLUTO::trine`.
- Rebuilt BTC weekly chart pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260709_235914`
- Main chart URL:
  `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=classified_noise_excluded`
- Chart filter verification:
  - all generated windows before noise filter: `216`;
  - chart-visible windows after excluding noise families: `204`;
  - excluded windows: `12`;
  - local server on `127.0.0.1:8766` returned HTTP `200`.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py analyze_btc_aspect_effectiveness.py`;
  - `python analyze_btc_aspect_effectiveness.py`;
  - `python build_btc_weekly_astro_chart.py`.

## Previous Update - 2026-07-09

2026-07-09 BTC weekly SR/aspect noise R&D:

- User reported BTC chart did not show planetary SR lines for `n > 60`, requested SR degree `d` be `360` and `180`, and asked for evidence/R&D to reduce noisy planet/aspect overlays.
- Updated `build_btc_weekly_astro_chart.py`:
  - removed hardcoded BTC SR degree `720`;
  - added `--degree-scales`, default `360,180`;
  - `sr_level(...)` now receives each degree scale explicitly;
  - `btc_weekly_sr_lines.csv` and `btc_weekly_sr_touches.csv` now record `degree_scale` as `180` or `360`;
  - chart SR selector now preserves coverage across `body + degree_scale + n_value` before filling by historical touch strength, so higher `n` groups are not hidden by low-n touch-heavy lines;
  - default visible SR cap raised to `360`.
- Rebuilt BTC weekly chart pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260709_231758`
- Main chart URL:
  `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=d360_d180_evidence`
- Chart/SR verification:
  - weekly candles: `465`;
  - filtered astro windows >= 14 days: `216`;
  - SR candidate lines in/near price range: `1144`;
  - SR touches: `31378`;
  - degree scales present in SR CSV: `180`, `360`;
  - all requested `n=30..150` present;
  - SR rows with `n > 60`: `792`;
  - balanced chart selection uses `360` lines, including `240` lines with `n > 60`, both degree scales, and all `n` values;
  - local server on `127.0.0.1:8766` returned HTTP `200`.
- Added `analyze_btc_aspect_effectiveness.py`:
  - fetches BTC weekly Binance candles;
  - builds historical transit-to-natal aspect windows using the same Bitcoin Genesis/Raman setup;
  - excludes Moon and Rahu/Ketu mutual pair via existing aspect generator;
  - filters windows shorter than 14 days;
  - logs every historical aspect event to `btc_aspect_effectiveness_events.csv`;
  - summarizes every aspect family to `btc_aspect_effectiveness_summary.csv`;
  - for windows `<= 7` weeks, evaluates whether a local crest/trough occurs inside the aspect window using a +/- 7-week context;
  - for windows `>= 8` weeks, evaluates start-to-end return from aspect start candle open to aspect end candle close;
  - adds deterministic weekly candlestick comments: doji, hammer-like, shooting-star-like, engulfing, inside/outside bar, large body;
  - adds research buckets so web-prior macro families can be separated from likely weekly noise without silently deleting anything.
- Evidence output pack:
  `D:\GannFinancialAstro\doc\btc_aspect_effectiveness_20260709_232357`
- Evidence counts:
  - historical windows >= 14 days: `153`;
  - analyzed events: `153`;
  - aspect families: `96`.
- Top reliability-weighted families from the first evidence run:
  - `URANUS|SUN::trine`;
  - `URANUS|RAHU::square`;
  - `SATURN|MARS::conjunction_orb`;
  - `NEPTUNE|URANUS::conjunction_orb`;
  - `SATURN|JUPITER::conjunction_orb`;
  - `URANUS|JUPITER::trine`;
  - `PLUTO|JUPITER::conjunction_orb`.
- Web/R&D priors recorded in the evidence note:
  - AstroConnexions emphasizes Jupiter/Saturn/Uranus/Neptune/Pluto and Saturn/Uranus BTC themes;
  - SG AppDev emphasizes Sun-Jupiter and Sun-to-Saturn/Uranus/Neptune/Pluto date studies;
  - WIRED documents that practitioners disagree, while mentioning Saturn transits, BTC Sun/Mars/Pluto Capricorn themes, and Jupiter/outer-planet combinations.
- Important boundary:
  - this first evidence script analyzes transit-to-natal aspect windows only; it does not yet score pure transit-to-transit/inter-planet aspects or automatically hide chart families. Use the CSVs first, then decide the filter list.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py analyze_btc_aspect_effectiveness.py`;
  - `python build_btc_weekly_astro_chart.py`;
  - `python analyze_btc_aspect_effectiveness.py`.

## Previous Update - 2026-07-07

2026-07-07 BTC weekly chart v2:

- User requested BTC weekly chart refinements:
  - filter out aspects shorter than two weeks;
  - show aspects after Jan 2025 and extend future astro windows through Jan 2030;
  - change SR `n` values to `30..150`;
  - keep closest-point hover rather than a vertical hover line.
- Updated `build_btc_weekly_astro_chart.py`:
  - default `--min-window-days` is now `14.0`;
  - added `--aspect-end`, default `2030-01-31`;
  - default `--n-values` is now `30,40,50,60,70,80,90,100,110,120,130,140,150`;
  - default `--max-aspect-windows` increased to `1000`, fixing the missing-post-Jan-2025 display caused by only drawing the first 180 windows;
  - daily transit/aspect generation now runs to `--aspect-end` instead of stopping at latest price candle;
  - bottom aspect-density panel extends through the future aspect endpoint;
  - x-axis range now spans price start through the future aspect endpoint;
  - SR visibility upper band widened to `1.80x` historical high so `n=140/150` levels can participate in forward research.
- Rebuilt BTC chart pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260707_223919`
- Main chart URL:
  `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=2030_14d_n30_150_final`
- Generated counts:
  - weekly candles: `465`;
  - filtered astro windows >= 14 days: `216`;
  - SR candidate lines in/near extended forward price range: `572`;
  - SR touches: `8841`.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py`;
  - filter audit returned `moon_rows=0`, `rahu_ketu_pair_rows=0`, `shorter_than_14_days=0`;
  - future audit returned `after_2025_01=90`, `after_2026_07=63`, latest window ending `2030-02-01 00:00 UTC`;
  - all requested `n` values `30..150` appear in `btc_weekly_sr_lines.csv`;
  - server on `127.0.0.1:8766` returned HTTP `200`;
  - in-app browser opened the final chart and console logs had no errors.

## Previous Update - 2026-07-07

2026-07-07 BTC weekly astro chart:

- User requested a Bitcoin weekly chart covering the last three bull-run/cycle spans through current data, with astrological overlays.
- Added `build_btc_weekly_astro_chart.py` as a separate BTC research generator so it does not disturb the USDJPY repeatation reviewer.
- Data/source decisions:
  - BTC price source is Binance public weekly `BTCUSDT` klines; available chart range starts `2017-08-14 05:30 IST`, so the first displayed bull-run span is the late-2017 peak tail, followed by the 2020-21 run and 2022-current cycle.
  - Genesis block timestamp is fixed as `2009-01-03 18:15:05 UTC` = `2009-01-03 23:45:05 IST`.
  - Primary birthplace hypothesis is `Van Nuys / Los Angeles`; this is explicitly marked unverified/experimental in metadata.
  - Alternate place hypotheses recorded in metadata: London and Dublin.
  - Ayanamsa uses the project doctrine setting: Raman.
- User filters implemented:
  - Moon excluded from natal/transit/aspect windows.
  - Rahu/Ketu mutual interaction excluded because they are always 180 degrees apart.
  - Aspect windows shorter than `7` days filtered out.
  - SR grid uses requested `n=10,20,30,40,50,60,70,80,90` and `f=1.6,1.8`.
- BTC scale note:
  - SR projection uses explicit `BTC_SCALE_DEGREE=720` so the requested `n/f` grid reaches the current BTC weekly price band; this assumption is written to README/metadata.
- Output pack:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260707_220921`
- Main chart:
  `D:\GannFinancialAstro\doc\btc_weekly_astro_20260707_220921\btc_weekly_astro_chart.html`
- Supporting outputs:
  - `btc_weekly_price_binance.csv`
  - `btc_daily_transit_longitudes.csv`
  - `btc_weekly_transit_longitudes.csv`
  - `btc_weekly_astro_windows.csv`
  - `btc_weekly_sr_lines.csv`
  - `btc_weekly_sr_touches.csv`
  - `btc_weekly_metadata.json`
  - `README.md`
- Generated counts:
  - weekly candles: `465`;
  - filtered astro windows >= 7 days: `219`;
  - SR candidate lines in/near price range: `396`;
  - SR touches: `10134`.
- UI/chart polish:
  - dense SR line traces and filtered astro marker traces are hidden from legend;
  - chart HTML is responsive;
  - hover is forced to closest-point mode and Plotly spike/crosshair lines are disabled via post-render relayout so cursor hover does not create a full vertical read line.
- Server status:
  - separate static server listening on `127.0.0.1:8766`;
  - URL: `http://127.0.0.1:8766/btc_weekly_astro_chart.html?v=closest_hover_v2`;
  - HTTP check returned `200`.
- Verification:
  - `python -m py_compile build_btc_weekly_astro_chart.py`;
  - generated output successfully;
  - filter audit returned `moon_rows=0`, `rahu_ketu_pair_rows=0`, `shorter_than_7_days=0`;
  - generated HTML contains the runtime closest-hover/spike-disable postscript;
  - in-app browser opened the chart and browser console had no errors.

## Previous Update - 2026-07-04

2026-07-04 global carryover rules for Mercury-Moon trine review:

- User asked whether the previous reviewed family learning could carry over into the current `MERCURY|MOON::trine` review family.
- Implemented neutral/global carryover templates in `build_repeatation_review_pack.py`:
  - `global_sr_geometry_classifier`;
  - `global_first_boundary_exit`;
  - `global_confirmed_break_extension`;
  - `global_multi_aspect_gann_exit_gate`;
  - `global_intrabar_ambiguity_ignore`.
- Important boundary:
  - these templates carry over SR/boundary/ignore mechanics from `AVG(ALL)|MOON::square`;
  - they do **not** carry over the old family direction, case personality, or `bearish_bias_support_barrier` as a Mercury-Moon trine family truth.
- Updated neutral marker-flow Auto Suggest so families without their own rule can still use global carryover:
  - after choosing start, it checks directional SR touches, next shaded/aspect zone, next hardcoded marker, and eligible multi-aspect Gann fan exit;
  - if the first SR has confirmed close/retest/continuation break, the SR is treated as a passed barrier and exit moves to the next attribution boundary;
  - otherwise the first clean boundary wins.
- Kept `reviewer_rule_replay.py` in sync with browser Auto Suggest so review-agent/replay memory does not split from the UI.
- Bumped UI cache key to `repeatation_ui_20260704_global_carryover_v65`.
- Rebuilt Mercury-Moon trine pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_95_mercury_moon_trine_20260704_232331`
- Removed incomplete timeout folder:
  `D:\GannFinancialAstro\doc\repeatation_review_case_95_mercury_moon_trine_20260704_232022`
- Server status:
  - API-aware server listening on `127.0.0.1:8765`, PID `23108`;
  - reviewer URL: `http://127.0.0.1:8765/repeatation_reviewer.html`;
  - HTTP checks returned `200` for both `repeatation_reviewer.html` and `aspect_review_case_95_chart.html`.
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py serve_repeatation_pack.py`
  - direct replay checks via `reviewer_rule_replay.auto_suggest_case(...)`:
    - case `95`: global carryover active, end rule `confirmed_break_next_shaded_zone_boundary`, signed pips `+45.7`;
    - case `124`: global carryover active and multi-aspect Gann exit won, end rule `gann_second_from_bottom_touch_multi_aspect`, signed pips `+2.0`;
    - case `147`: global carryover active, end rule `confirmed_break_next_shaded_zone_boundary`, signed pips `+217.3`.

2026-07-04 Mercury-Moon trine review start:

- User decided to begin reviewing the upcoming `MERCURY|MOON::trine` family before the next live/demo market event.
- Upcoming scan shows `MERCURY|MOON::trine` windows:
  - `2026-07-06 10:00 -> 12:00 IST`, peak `11:00`, orb delta `0.082065`;
  - `2026-07-23 02:00 -> 05:00 IST`, peak `03:00`;
  - `2026-08-02 07:00 -> 10:00 IST`, peak `08:00`.
- Existing historical review DB has `16` `MERCURY|MOON::trine` repeatations:
  `95, 124, 147, 241, 255, 306, 360, 367, 425, 454, 492, 554, 586, 599, 632, 653`.
- Stored 72h touch-log direction sketch before manual review:
  - `11` UP;
  - `5` DOWN;
  - no completed manual review/official ML history yet for this family.
- Built Mercury-Moon trine pack from seed `case_id=95`:
  `D:\GannFinancialAstro\doc\repeatation_review_case_95_mercury_moon_trine_20260704_051106`
- Server status:
  - API-aware server listening on `127.0.0.1:8765`, PID `13652`;
  - reviewer URL: `http://127.0.0.1:8765/repeatation_reviewer.html`;
  - HTTP checks returned `200` for both `repeatation_reviewer.html` and `aspect_review_case_95_chart.html`.

## Previous Update - 2026-07-04

2026-07-04 future-aspect generator / MT5 bridge / case 127 correction:

- Added `generate_upcoming_aspects.py`:
  - price-independent upcoming sidereal aspect window generator;
  - uses doctrine-locked Raman ayanamsa through Swiss Ephemeris;
  - default bodies: `AVG(ALL)`, seven classical planets, `RAHU`, `KETU`;
  - default aspects match the review pipeline: `conjunction_orb`, `square`, `trine`, `opposition_orb`;
  - enriches rows from `gann_aspect_annotations.sqlite` completed reviews and latest `official_ml_note` snippets by `family_key`.
- Generated local planning exports:
  - `D:\PycharmProjects\upcoming_aspects_20260704_30d.csv`
  - `D:\PycharmProjects\upcoming_aspects_20260704_30d.json`
  - these are local/generated outputs, not intended for commit.
- First upcoming 30-day scan from `2026-07-04 00:00 IST` found `73` aspect windows.
  - `AVG(ALL)|MOON::square` appears on `2026-07-04 12:00 -> 15:00 IST`, peak `13:00 IST`, orb delta `0.160969`.
  - The same family has `5` completed reviews in the DB: `4` bearish, `1` ignored, average signed pips `+24.68`, latest official note from corrected case `127`.
- Added `mt5_trade_executor.py`:
  - dry-run-first MT5 bridge for `status`, `buy`, `sell`, and `close`;
  - live trading is refused unless both `--live` and `--confirm LIVE` are passed;
  - supports exact terminal path, optional `--login/--server`, and password via an environment variable such as `MT5_PASSWORD`;
  - computes symbol pip size from MT5 digits and runs `order_check()` before dry-run output.
- MT5 local status test:
  - `MetaTrader5` Python package is installed (`5.0.5640`);
  - first unauthenticated `python mt5_trade_executor.py --status --symbol USDJPY` reached the package but failed terminal initialization with `Terminal: Authorization failed`;
  - user provided demo account details for `MetaQuotes-Demo`; credential was used only as a temporary process environment variable and was not written to repo files;
  - authenticated status check succeeded: account connected, balance `100000.00 USD`, `USDJPY` selected, min volume `0.01`, pip size `0.01`;
  - live trading is **not ready yet** because MT5 terminal status reports `trade_allowed=false` even though account `trade_allowed=true`;
  - USDJPY tick returned by the terminal appears stale, so before order dry-runs/live testing, open MT5, enable AutoTrading/algo trading, and confirm current live quotes are updating.
- Corrected the case `127` split-brain state:
  - viewport fans remain visual/ML-context only;
  - trade replay uses the full exported trade-candle universe, not only visible candles;
  - case `127` is restored as `bearish +4.0 pips`;
  - start `2025-05-28T22:00:00+05:30 @ 144.965`;
  - end `2025-05-28T23:00:00+05:30 @ 144.925`;
  - rules `first_case_window_sr_line_touch -> gann_second_from_bottom_touch_multi_aspect`;
  - official ML note replaced with note `#22`, status `codex_verified_trade_gann_exit_restored`.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260704_042319`
- Server status:
  - API-aware server listening on `127.0.0.1:8765`, PID `13400`;
  - HTTP check for case `127` returned `200`.
- Verification:
  - `python -m py_compile mt5_trade_executor.py generate_upcoming_aspects.py reviewer_rule_replay.py build_repeatation_review_pack.py`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260704_042319 --case-id 127`
  - `python generate_upcoming_aspects.py --start 2026-07-04 --days 30 --step-minutes 60 --output-csv D:\PycharmProjects\upcoming_aspects_20260704_30d.csv --output-json D:\PycharmProjects\upcoming_aspects_20260704_30d.json --top 12`
  - authenticated `python mt5_trade_executor.py --status --symbol USDJPY --login <demo_login> --server MetaQuotes-Demo` succeeded after password was supplied via temporary `MT5_PASSWORD`;
  - live order dry-run is intentionally deferred until terminal AutoTrading and current tick freshness are confirmed.

## Previous Update - 2026-05-31

2026-05-31 case 127 viewport-fan trading split-brain fix:

- User asked whether the newly added two visible-viewport Gann fans were being used in trading, because case `127` looked like the close marker had moved to a bottom-most viewport-fan intersection instead of the remembered `23:30` close marker.
- Current intended rule is confirmed:
  - the two viewport fans are visual / ML-context only;
  - Auto Suggest trading logic must not use them as start/end candidates.
- Browser drawer / current HTML evidence showed case `127` should be:
  - start `2025-05-28 22:00:00+05:30 @ 144.965`;
  - end `2025-05-28 23:30:00+05:30 @ 145.125`;
  - outcome `bullish +16.0 pips`;
  - start rule `first_case_window_sr_line_touch`;
  - end rule `next_later_hardcoded_marker`;
  - viewport fan status `visual_and_ml_context_only_not_auto_suggest_trade_logic`.
- Root cause of the stale contradiction:
  - browser-side candle collection already ignored hidden candlestick traces;
  - `reviewer_rule_replay.py` still included `trace.visible == false` candlestick traces, so historical replay could reproduce the older Gann-exit path even though the browser Auto Suggest no longer used it.
- Fixed `reviewer_rule_replay.py`:
  - `collect_candles()` now skips hidden candlestick traces;
  - case `127` expectation now requires `2` selected-window SR touch candidates, matching the browser drawer.
- Updated SQLite `D:\PycharmProjects\gann_aspect_annotations.sqlite`:
  - completed review for case `127` now stores the current `bullish +16.0` marker-flow decision;
  - replaced stale official ML note with current `official_ml_note` `note_id=21`, status `codex_verified_current_replay`;
  - note explicitly says not to train the old `gann_second_from_bottom_touch_multi_aspect` / `bearish +4.0` path as the current decision.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260531_010132`
- Server status:
  - API-aware server listening on `127.0.0.1:8765`, PID `18460`;
  - curl verification for case `127` returned HTTP `200`.
- Verification:
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260531_010132 --case-id 127`
  - result passed with start `22:00 @ 144.965`, end `23:30 @ 145.12528246460198`, and `case_window_sr_touch_count=2`.

## Previous Update - 2026-05-30

2026-05-30 C-drive storage cleanup / D-drive path hardening:

- User reported severe C-drive storage pressure and asked to move/delete project duplicates from C.
- Moved project-owned C paths off C:
  - `C:\Users\ADMIN\Desktop\doc` -> `D:\GannFinancialAstro\doc`
  - `C:\Users\ADMIN\Desktop\Trading_Algo\New folder` -> `D:\Trading_Algo\New folder`
  - remaining `C:\Users\ADMIN\Desktop\Trading_Algo` root files -> `D:\Trading_Algo\Desktop_Trading_Algo_root_legacy_20260530`
  - `C:\Users\ADMIN\Desktop\WD GANN` -> `D:\Trading_Algo\WD GANN`
  - `C:\Users\ADMIN\Desktop\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf` -> `D:\GannFinancialAstro\sources\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf`
- Important recovery detail:
  - the old `C:\Users\ADMIN\PycharmProjects` contained the live `.git` repo, while `D:\PycharmProjects` was empty after the move;
  - moved that migrated repo into `D:\PycharmProjects` as the canonical active repo, then removed the temporary `D:\C_Drive_Migrated` duplicate.
- Active code/config path defaults now use D-drive locations:
  - project data/root: `D:\PycharmProjects`
  - chart export/root: `D:\GannFinancialAstro\doc`
  - Telegram helpers: `D:\Trading_Algo\New folder`
  - legacy Telegram bot fallback: `D:\Trading_Algo\WD GANN`
- Active Python/JSON/YAML/PS1 and non-handoff Markdown scans now have no `C:\Users\ADMIN...` path references outside historical handoff/backup text.
- Confirmed the leftover `C:\Users\ADMIN\Desktop\New folder (3)` is photo/image content, not this project, so it was not moved automatically.
- Verified:
  - `python -m py_compile aspect_annotation_store.py serve_repeatation_pack.py sr_touch_lazy_dashboard.py build_aspect_sr_touch_log.py build_pair_aspect_market_log.py build_sr_anchor_reversal_log.py rebuild_dataset_mt5_ipo_allpairs.py jyotish_agent\telegram_notify.py jyotish_agent\telegram_codex_relay.py`
  - `python jyotish_agent\telegram_notify.py --dry-run` confirmed Telegram config/runner are available from D.

2026-05-30 visible-viewport Gann envelope fans:

- User clarified the new two extra Gann fans should use the whole currently visible Plotly/browser chart span, not only the selected aspect-review window.
- `build_repeatation_review_pack.py` now adds a `Viewport Fans` soft button in the marker drawer:
  - finds the highest visible candlestick top wick and anchors a bearish/downward context fan there;
  - finds the lowest visible candlestick bottom wick and anchors a bullish/upward context fan there;
  - stores them in `viewport_fans` autosave/download payloads and includes them in `current_marker_ml_note`;
  - displays a drawer summary labelled `visual/ML context only`, so these fans do not alter Auto Suggest trade start/end logic yet.
- The fan traces use the same ratios as the main Gann fan: `1x4`, `1x2`, `1x1`, `2x1`, `4x1`.
- Robustness fixes:
  - marker UI now waits for real `window.Plotly.relayout` before attaching; it no longer immediately binds a no-op Plotly shim just because the graph div exists;
  - exported case charts now inline Plotly JS instead of relying on external `plotly.min.js`, because the in-app browser was rendering the SVG but not exposing external Plotly reliably;
  - a fallback SVG drawing path was added for viewport fans when live Plotly is unavailable in the in-app browser;
  - candlestick collection now ignores traces with `visible === false`, so hidden timeframe candles do not pollute the highest/lowest visible wick scan.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260530_035143`
- Restarted server on port `8765`, PID `20544`.
- Current case 185 URL:
  `http://127.0.0.1:8765/aspect_review_case_185_chart.html?v=repeatation_ui_20260530_viewport_fans_v64&fresh=verify10`
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py sr_touch_lazy_dashboard.py reviewer_rule_replay.py codex_review_task_queue.py serve_repeatation_pack.py`
  - rebuilt all 16 AVG(ALL)|MOON square repeatation charts;
  - browser screenshot confirmed the drawer summary and the extra context fan lines are visible on the chart. In-app browser DOM inspection remains sandboxed and does not reliably expose the injected SVG/Plotly runtime, so screenshot verification is the useful check for this feature.

2026-05-30 case 185 ignore-trade / intrabar SR sandwich:

- User reviewed case `185` in `AVG(ALL)|MOON::square` and chose to follow Codex recommendation to mark it ignored.
- Decision saved:
  - completed review `review_id=9`;
  - official ML note `note_id=18`;
  - `review_status=ignored`;
  - `outcome_label=ignore_trade`;
  - rules `ignore_trade_multi_sr_same_candle_intrabar_unknown -> ignore_trade_multi_sr_same_candle_intrabar_unknown`.
- Added first-class UI ignore signal definitions in `build_repeatation_review_pack.py`:
  - `multi_sr_same_candle`;
  - `ambiguous_intrabar_order`.
- Case `185` official note says:
  - exact selected AVG(ALL)|MOON row stores MARS/MERCURY SR confluence, not Neptune/Saturn for the selected-case touch;
  - stored SR prices are MARS `144.800108` and MERCURY `144.913239`, around `11.3` pips apart;
  - 2025-06-25 07:30 and 08:00 M30 candles span both SRs, so OHLC cannot prove whether upper entry/rejection SR or lower target/support was touched first;
  - astro pressure leans bearish (Drik `-32.1V`, malefic `-45.0V` vs benefic `+12.8V`, doctrine bearish) but Shadbala is weak/below threshold (`321.2V`, ratio `0.929`), Chesta is low, regime count is crowded, and FX heuristic conflicts bullish.
- Important ML instruction:
  - train case `185` as `ignore_trade_multi_sr_same_candle_intrabar_unknown`;
  - do not label it as failed bullish or bearish;
  - live trading may use lower timeframe/tick sequence, but historical M30 review should not invent intrabar order.
- Fixed `reviewer_rule_replay.py` historical replay:
  - when `gann_second_from_bottom_touch_multi_aspect` wins, replay now applies the Gann fan direction to `outcome_label` and signed pips just like the browser Auto Suggest;
  - this resolved the stale replay contradiction on case `127`.
- Case `127` was replay-corrected:
  - completed review `review_id=8`;
  - official ML note `note_id=19`;
  - current replay is `bearish +4.0 pips`;
  - rules `first_case_window_sr_line_touch -> gann_second_from_bottom_touch_multi_aspect`.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260530_015348`
- Restarted server on port `8765`, PID `4900`.
- Current case 185 review URL:
  `http://127.0.0.1:8765/aspect_review_case_185_chart.html?v=repeatation_ui_20260530_ignore_intrabar_v57&fresh=case185done`
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py codex_review_task_queue.py serve_repeatation_pack.py`
  - `python codex_review_task_queue.py --list-pending --limit 20` returned no pending tasks.
  - Browser verification after clearing stale local draft shows:
    `Completed review: ignored`,
    `rules: ignore_trade_multi_sr_same_candle_intrabar_unknown -> ignore_trade_multi_sr_same_candle_intrabar_unknown`,
    and the official note starts with `Decision: Ignore Trade`.

## Previous Update - 2026-05-29

2026-05-29 mixed SR-reference verifier fix:

- User reported that case `127` still showed Dream Review:
  `queued_for_codex | issues 2` and `SR geometry conflict`, specifically:
  `Auto Suggest says SR is above entry, but the draft talks as if the relevant SR is below/support.`
- Diagnosis:
  - this was not a true contradiction;
  - current Auto Suggest can legitimately contain two SR contexts:
    - `sr_geometry`: the executed/final exit context, currently `SR is above entry: resistance/entry`;
    - `barrier_sr_geometry`: the first barrier/reference being tested, currently `SR is below entry: support/target`;
  - the verifier was treating mention of the lower first barrier as contradiction against the final exit geometry.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_mixed_sr_verifier_v56`;
  - verifier evidence now includes `barrier_label` and `mixed_sr_references`;
  - SR-geometry contradiction checks now allow opposite-side language when it matches `barrier_sr_geometry`;
  - verifier check log now explicitly prints:
    `Mixed SR references checked: final geometry is ...; first barrier/reference is ...`
- Updated `codex_review_task_queue.py`:
  - Dream Review correction tasks that contain only an SR-geometry conflict caused by mixed `sr_geometry` vs `barrier_sr_geometry` are skipped instead of replacing the official ML note.
- Replaced the bad case `127` official note written by task `12` with official note `#14`:
  - status `codex_verified_mixed_sr_reference_no_contradiction`;
  - records current outcome `bearish`, current marker result `-6.0` pips for that draft/review state;
  - explicitly says not to train `SR geometry conflict` from mixed final/barrier SR references.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_202527`
- Restarted server on port `8765`, PID `21004`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260529_mixed_sr_verifier_v56&fresh=mixedsr`
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py codex_review_task_queue.py serve_repeatation_pack.py jyotish_agent\dream_review_agent.py jyotish_agent\explain_case.py`
  - `python codex_review_task_queue.py --list-pending --limit 20`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_202527`
  - browser: after `Draft ML Reason`, Dream Review returned `caution_only | issues 1`, no `SR geometry conflict`; only BPHS synthetic-orb caution remains.

2026-05-29 case 127 Gann fan outcome correction:

- User reported case `127` still displayed `bullish -4.0 pips` in both the plot callout and marker drawer, but the executed Auto Suggest path is a top-wick Gann fan/downward projection and should score as `bearish +4.0 pips`.
- Root cause:
  - the marker-flow Gann fan exit correctly stored `gann_fan.fan_direction = bearish`;
  - profit display still inherited the family/default `bullish` outcome, including from an older autosaved draft.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_case127_gann_outcome_v55`;
  - added `autoOutcomeFromSuggestion(...)` and `setAutoOutcome(...)`;
  - when `end_rule === gann_second_from_bottom_touch_multi_aspect`, Auto Suggest now scores by the fan direction:
    - top-wick/down fan -> `bearish`;
    - bottom-wick/up fan -> `bullish`;
  - restored drafts with that Gann fan rule now also auto-correct the outcome, so stale localStorage cannot keep the old bullish label.
- Updated SQLite official ML note for case `127`:
  - new `official_ml_note` id `12`;
  - outcome corrected to `bearish`;
  - signed pips corrected to `+4.0`;
  - note explains that raw move `-4.0` pips is favorable for the top-wick bearish fan path.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_200807`
- Restarted server on port `8765`, PID `1340`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260529_case127_gann_outcome_v55&fresh=outcome2`
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py codex_review_task_queue.py serve_repeatation_pack.py`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_200807`
  - `python codex_review_task_queue.py --list-pending --limit 20`
  - browser check on case `127` confirmed:
    `Live trade result bearish +4.0 pips`, selected outcome `bearish`, entry `144.965`, exit `144.925`.
  Pending Codex review task queue is empty.

2026-05-29 immediate Dream Review agent trigger:

- User reported case `127` had a Dream Review contradiction and requested:
  - stop relying on the 30-minute review-agent heartbeat;
  - trigger the agent immediately once `Draft ML Reason` has produced a draft and Dream Review has run.
- Deleted heartbeat automation:
  `process-codex-review-agent-queue`
- Updated `codex_review_task_queue.py`:
  - added `--process-pending`;
  - added deterministic queue processor for:
    - `official_ml_note`: writes a Codex review-agent official note from completed-review payload/Auto Suggest evidence;
    - `dream_review_correction`: writes a corrected official note from verifier/Dream Review evidence;
    - `rule_replay_review`: skips non-material replay changes where only rule version metadata changed; flags material replay changes for Codex.
- Updated `serve_repeatation_pack.py`:
  - `/api/dream_review` now calls `process_pending_tasks()` immediately after queuing a Dream Review correction;
  - browser response includes `codex_agent_result` / `codex_agent_error`.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_immediate_dream_agent_v54`;
  - Dream Review panel now reports immediate Codex review-agent processed task count/actions;
  - verifier direction/SR checks now inspect the deterministic analysis section instead of matching raw Auto Suggest JSON/RAG snippets, reducing false contradictions from reference geometry or old family notes.
- Processed current pending queue:
  - task `#10`, case `127` Dream Review correction -> official note `#8`;
  - task `#6`, case `43` official note -> note `#9`;
  - task `#8`, case `103` official note -> note `#10`;
  - tasks `#7` and `#9` replay reviews skipped because replay showed only rule-version metadata drift, not material P/L/rule-path changes.
- Case `127` official correction:
  - deterministic evidence wins over draft wording;
  - outcome is `bullish`;
  - live trade result is `-4.0` pips;
  - active SR geometry is `SR is below entry: support/entry`;
  - marker-flow/reference geometry separately records `SR is above entry: resistance/target`;
  - future drafts must name which SR reference they mean before training.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_084521`
- Restarted server on port `8765`, PID `20768`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260529_immediate_dream_agent_v54&fresh=immediate4`
- Verification:
  - `python -m py_compile codex_review_task_queue.py serve_repeatation_pack.py build_repeatation_review_pack.py`
  - `python codex_review_task_queue.py --process-pending --limit 20`
  - `python codex_review_task_queue.py --list-pending --limit 20`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_084521`
  - HTTP `200` and browser load for case `127` v54
  all passed; pending Codex review task queue is empty.

2026-05-29 Dream Review queue -> Codex review-agent correction:

- User reported the browser warning:
  `Dream review found contradiction(s) but did not auto-apply; queued for Codex/human review.`
  and requested the Codex agent to check queued Dream Review drafts and auto-apply/correct when deterministic evidence is clear.
- Root cause:
  `jyotish_agent\dream_review_agent.py` wrote contradiction drafts to `jyotish_agent\dream_review_queue.jsonl`, but the Codex heartbeat automation only watched SQLite `codex_review_tasks`.
- Updated `serve_repeatation_pack.py`:
  - when `/api/dream_review` returns `queued_for_codex` / `needs_review`, it now enqueues a durable SQLite `dream_review_correction` task;
  - browser response includes `codex_task_ids` for queued Dream Review corrections.
- Updated `codex_review_task_queue.py`:
  - added `--ingest-dream-queue`;
  - imports existing `dream_review_queue.jsonl` rows into `codex_review_tasks`;
  - dedupes by Dream Review report filename;
  - `dream_review_correction` tasks now carry the original payload, dream result, report path, and correction policy.
- Updated `jyotish_agent\dream_review_agent.py` and `build_repeatation_review_pack.py` copy:
  - warning text now says the contradiction is queued for Codex review-agent correction, not left as vague human-only review.
  - cache key advanced to `repeatation_ui_20260529_dream_queue_v53`.
- Imported existing queued Dream Review contradiction:
  - task `#5`, case `8`, report:
    `D:\PycharmProjects\jyotish_agent\dream_review_reports\case_8_20260529_034136_dream_review.md`
- Resolved task `#5`:
  - Dream Review contradiction was a break-confirmation conflict;
  - local draft said failed/missing support break;
  - deterministic Auto Suggest/verifier evidence confirmed support break, failed retest, and continuation;
  - Codex replaced the official ML note with note `#7`, status `codex_verified_dream_review_resolved`;
  - note explicitly rejects contradictory local LLM draft wording and tells ML to use deterministic evidence.
- Cleared stale duplicate pending official-note tasks `#2`, `#3`, and `#4` for case `8` as skipped.
- Updated heartbeat automation `process-codex-review-agent-queue`:
  - first runs `codex_review_task_queue.py --ingest-dream-queue`;
  - then processes `dream_review_correction`, `official_ml_note`, and `rule_replay_review` tasks;
  - auto-applies deterministic corrections through official notes when evidence is clear;
  - leaves uncertain cases marked for review instead of letting local LLM text become official.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_035153`
- Restarted server on port `8765`, PID `16628`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260529_dream_queue_v53&fresh=dreamqueue`
- Verification:
  - `python -m py_compile serve_repeatation_pack.py codex_review_task_queue.py jyotish_agent\dream_review_agent.py build_repeatation_review_pack.py`
  - `python codex_review_task_queue.py --ingest-dream-queue`
  - `python codex_review_task_queue.py --list-pending --limit 20`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_035153`
  - HTTP `200` from the v53 case `8` chart
  all passed; pending Codex review task queue is empty.

2026-05-29 Gate 3 external certification pass:

- User requested certification of the above-mentioned review cases after discussing Gate 3 trusted sources.
- Installed PyJHora `4.8.6` as a local Tier B external witness under:
  `D:\GannFinancialAstro\external_tools\pyjhora`
  - This is intentionally outside the git repo and should remain local/uncommitted.
  - First dependency install hit low C-drive temp/cache space; rerun used D-drive temp/cache and succeeded.
- Used PyJHora with:
  - Raman ayanamsa;
  - true node / Rahu;
  - event timezone;
  - `drik.sidereal_longitude`, `drik.tithi`, and `drik.nakshatra`.
- Filled Gate 3 external expected values in:
  `D:\PycharmProjects\astro_external_validation_template_20260527.csv`
- Certified 25 astronomy/Panchanga rows:
  - `case_8_event_start`
  - `case_43_event_start`
  - `case_103_event_start`
  - `case_127_sr_touch_start`
  - `gann_reference_tokyo`
  - each with Sun/Moon/Rahu Raman sidereal longitude, Tithi, and Moon Nakshatra/Pada.
- Updated `astro_function_certification.py`:
  - certification notes are now idempotent;
  - repeated runs no longer append duplicate `numeric delta` / `categorical exact compare` / pending compare text.
- Reran:
  `python astro_function_certification.py`
- Current Gate 3 result:
  `25 pass / 0 fail / 10 pending`
- Remaining pending Gate 3 rows:
  Shadbala and Drik Bala rows for each sample remain intentionally pending until we have row-specific JHora/book-style exports.
- Updated:
  `D:\PycharmProjects\astro_function_certification_report_20260527.md`
  `D:\PycharmProjects\trading_rule_replay_result_20260527.json`
- Verification:
  - `python -m py_compile astro_function_certification.py`
  - `python test_strict_shadbala_doctrine.py`
  - `python codex_review_task_queue.py --list-pending --limit 10`
  all passed.

2026-05-29 historical re-simulation + Codex-owned ML notes:

- User requested:
  - historical re-simulation after new rules;
  - affected prior reviewed cases listed when replay changes P/L or rule path;
  - official ML notes created/altered only by Codex, not silently by the local LLM/page;
  - low-credit automation to process those note/replay tasks.
- Updated `reviewer_rule_replay.py`:
  - added deterministic `auto_suggest_case()` replay for generated packs;
  - added `replay_completed_review_impacts()` for historical re-simulation of completed reviews;
  - replay now parses chart markers, candles, SR line touches, shaded/aspect windows, multi-aspect overlap, support/resistance geometry, break confirmation, attribution boundaries, zone boundaries, and provisional multi-aspect Gann fan exits;
  - existing case `127` SR-touch regression and family rule source guards still pass.
- Updated `serve_repeatation_pack.py`:
  - `/api/complete_review` now runs historical re-simulation against previously completed reviews in the same family;
  - response lists affected/stable cases and replay deltas when a current rule path would alter old completed reviews;
  - local browser/live ML notes are treated as draft evidence only.
- Updated `aspect_annotation_store.py`:
  - added durable `codex_review_tasks` queue table;
  - added queue helpers: `enqueue_codex_review_task()`, `list_codex_review_tasks()`, `update_codex_review_task()`;
  - added `replace_rule_note_type()` so Codex can update one official ML note for a case without accumulating stale duplicates.
- Added `codex_review_task_queue.py`:
  - `--list-pending` shows queued Codex tasks;
  - `--write-official-note TASK_ID` writes a Codex-approved permanent `official_ml_note`;
  - `--mark-task` can mark replay/code-review tasks done/failed/skipped with a JSON result.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_historical_replay_v52`;
  - Replay Impact drawer now shows historical replay mode, stable/affected counts, replayed pips/rules, and fallback errors;
  - ML Notes drawer now states live marker notes are draft evidence and permanent official notes are Codex-owned;
  - Review Complete shows queued Codex task ids.
- Processed first Codex-owned official note:
  - Review Complete for case `8` queued task `#1`;
  - Codex wrote/replaced `official_ml_note` note `#6` for case `8`;
  - task `#1` marked `done`;
  - pending queue verified empty.
- Created heartbeat automation:
  - id `process-codex-review-agent-queue`;
  - runs every 30 minutes;
  - checks `codex_review_tasks`, writes official notes only after Codex review, inspects replay impacts, corrects stale notes/code when deterministic evidence supports it, and commits/pushes meaningful changes.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_022249`
- Restarted server on port `8765`, PID `22428`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260529_historical_replay_v52&fresh=officialnote2`
- Browser verification:
  - drawer shows official Codex ML note plus live marker draft note;
  - drawer shows policy: official ML notes are Codex-owned;
  - Review Complete queue/replay UI rendered correctly.
- Verification:
  - `python -m py_compile build_repeatation_review_pack.py aspect_annotation_store.py serve_repeatation_pack.py reviewer_rule_replay.py codex_review_task_queue.py`
  - `python reviewer_rule_replay.py --pack-dir D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_022249`
  - direct historical replay against saved SQLite completed review returned `affected=0`, `unchanged=1`, `failed=0`
  - `python test_strict_shadbala_doctrine.py`
  - `python codex_review_task_queue.py --list-pending --limit 10`
  all passed.

2026-05-29 review-completion agent ledger:

- User requested automated agents that work alongside manual review:
  - after start/end markers and P/L are available, create ML notes automatically;
  - mark a recurrence reviewed;
  - compare new rule paths against already reviewed repeatations;
  - give future rule changes a deterministic place to report earlier cases that need replay/correction.
- Updated `aspect_annotation_store.py`:
  - added durable `completed_reviews` table;
  - added `upsert_completed_review()` and `list_completed_reviews()`;
  - each completed review stores case/family, timeframe, outcome, start/end times, entry/exit, signed/raw pips, rule version, Auto Suggest start/end rule, full Auto Suggest JSON, live marker ML note JSON, replay-impact JSON, and reviewer note.
- Updated `serve_repeatation_pack.py`:
  - added `/api/complete_review`;
  - endpoint saves/updates one completed review and returns a replay-impact summary for the same family;
  - current first replay-impact pass flags previous completed reviews whose stored rule path or rule version differs from the new completed review, so they can be replay-checked after rule changes.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_review_agent_v51`;
  - builder defaults now use project-local `D:\PycharmProjects` paths and `D:\GannFinancialAstro\doc` export root instead of stale C-drive defaults;
  - generated chart metadata loads any existing completed review for each case;
  - marker drawer now has `Review Complete`;
  - completion payload includes live marker ML note, exact P/L, start/end rules, Auto Suggest evidence, reviewer note, and UI rule version;
  - drawer shows completed status plus replay-impact summary.
- Initialized `D:\PycharmProjects\gann_aspect_annotations.sqlite` with the new schema.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_014054`
- Restarted server on port `8765`, PID `16016`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260529_review_agent_v51&fresh=reviewagent`
- Verification:
  - HTTP `200` from case `8` chart.
  - Browser opened the new case `8` chart.
  - `Review Complete` saved case `8` to `completed_reviews` as review `#1`.
  - Saved review: `bearish +23.3 pips`, start rule `family_rule_case_window_entry_open_price`, end rule `confirmed_break_next_shaded_zone_boundary`, rule version `repeatation_ui_20260529_review_agent_v51`.
  - Replay impact shows no previous completed reviews in this family yet.
  - `python -m py_compile build_repeatation_review_pack.py aspect_annotation_store.py serve_repeatation_pack.py reviewer_rule_replay.py` passed.

## Previous Update - 2026-05-29

2026-05-29 live marker-derived ML Notes:

- User reported case `8` had no visible ML Notes after family notes were correctly separated from exact-case notes.
- Design decision:
  - saved DB ML notes remain strict/exact-case only;
  - family notes remain in `Applied family rules` / training memory;
  - marker-derived ML notes are now generated live from the actual current trade start/end markers and P/L.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260529_live_marker_ml_notes_v50`;
  - added `currentMarkerMlNote()`;
  - `ML Notes` now shows `Current marker ML note` as soon as trade start/end exist, whether placed manually or by Auto Suggest;
  - live note includes case/family, outcome, signed/raw pips, entry/exit times/prices, start/end sources, Auto Suggest start/end rules, Auto Suggest reason, SR geometry, break confirmation, Gann fan status, multi-aspect gate status, rule-vs-default tracking, top astro hints, and any reviewer note;
  - live note is included in `mlNotesPlainText()` so Draft ML Reason and dream/verifier context can consume it;
  - live note is included in autosaved browser draft and downloaded marker JSON as `current_marker_ml_note`.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260529_010327`
- Restarted server on port `8765`, PID `21572`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260529_live_marker_ml_notes_v50&fresh=mlnotes`
- Verification:
  - HTTP `200` from case `8` chart.
  - Playwright/Edge ran Auto Suggest on case `8`.
  - `ML Notes` panel showed one live note:
    `Current marker ML note`, outcome `bearish`, `+23.3 pips`, start rule `family_rule_case_window_entry_open_price`, end rule `confirmed_break_next_shaded_zone_boundary`, SR geometry `SR is below entry: support/target`, break confirmation `Support break confirmed`, Gann fan exit `blocked_no_multi_aspect_overlap`.
  - Browser draft localStorage contained `current_marker_ml_note`.
  - `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py serve_repeatation_pack.py aspect_annotation_store.py` passed.

## Previous Update - 2026-05-27

2026-05-27 case-specific ML Notes cleanup + Auto Suggest replay:

- User reported that case `103` still showed ML notes from case `8`.
- Root cause:
  `load_ml_notes()` merged case-family notes into every repeatation's visible `ML Notes` section.
- Updated `build_repeatation_review_pack.py`:
  - visible `meta.mlNotes` now includes only exact-case ML notes;
  - case-family notes remain available through `meta.appliedFamilyRules` / training memory;
  - case-family notes no longer appear as if they are exact notes for unrelated repeatations.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_170507`
- Restarted server on port `8765`, PID `16764`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_103_chart.html?v=repeatation_ui_20260527_multi_aspect_gann_exit_v49&fresh=notesfix`
- Verified generated case `103` chart now has `"mlNotes": []`.
  Case-family teaching notes still appear in `appliedFamilyRules`, which is intentional training/rule context rather than visible exact-case ML notes.
- Replayed Auto Suggest v48 pack vs v49 pack after the provisional multi-aspect Gann fan exit rule.
  Changed P/L cases:
  - case `127`: `+16.0` -> `-4.0` pips, delta `-20.0`; exit changed to `gann_second_from_bottom_touch_multi_aspect`.
  - case `185`: `+4.7` -> `+0.5` pips, delta `-4.2`; exit changed to `gann_second_from_bottom_touch_multi_aspect`.
  - case `216`: `+31.2` -> `-4.2` pips, delta `-35.4`; exit changed to `gann_second_from_bottom_touch_multi_aspect`.
  - case `384`: `+37.1` -> `-1.2` pips, delta `-38.3`; exit changed to `gann_second_from_bottom_touch_multi_aspect`.
- Interpretation:
  the new Gann fan exit remains provisional and needs manual review before promotion because it currently worsens all four changed repeatations in replay.
- Telegram status was sent with the case `103` note fix and the four replay deltas.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py serve_repeatation_pack.py aspect_annotation_store.py`
  `python reviewer_rule_replay.py`
  `python test_strict_shadbala_doctrine.py`
  all passed.

2026-05-27 multi-aspect Gann fan exit gate:

- User requested that the provisional Gann fan close-marker rule apply exclusively when multiple aspect windows overlap.
- Updated `build_repeatation_review_pack.py`:
  - cache key advanced to `repeatation_ui_20260527_multi_aspect_gann_exit_v49`;
  - added `collectAspectWindows()` and `multiAspectOverlapEvidence()`;
  - formal definition: multiple aspect = at least one reviewed candle has two or more aspect windows overlapping it;
  - for M30 review this means at least one 30-minute candle overlaps at least two aspect windows;
  - added provisional `gann_second_from_bottom_touch_multi_aspect` exit rule;
  - the rule is blocked unless the multiple-aspect gate passes;
  - if eligible, Auto Suggest can close at the first touch of the second-from-bottom Gann fan line;
  - for bearish/top-wick fans, second-from-bottom is `2x1` because `4x1` is lowest;
  - for bullish/bottom-wick fans, second-from-bottom is `1x2` because `1x4` is lowest;
  - the candidate audit now shows whether the Gann fan exit was chosen, checked, not found, or blocked.
- Added structured case `127` ML note in `gann_aspect_annotations.sqlite`:
  - Saturn SR/resistance caused temporary hesitation;
  - bullish FX/doctrine scores with zero conflict, friendly Moon condition, non-low Shadbala, and high Saptavargaja explain why reversal stayed limited;
  - weak Chesta and negative Drik explain hesitation/retest rather than full reversal;
  - new Gann fan exit is explicitly marked provisional and gated by multi-aspect overlap.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_162034`
- Restarted API-aware server on port `8765`, PID `19824`.
- Current review URL:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_multi_aspect_gann_exit_v49&fresh=multi`
- Verification:
  `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py serve_repeatation_pack.py aspect_annotation_store.py`
  `python reviewer_rule_replay.py`
  `python test_strict_shadbala_doctrine.py`
  all passed.

2026-05-27 Gann fan wick-direction fix:

- User reported case `127` Gann fan direction was wrong.
- Root cause:
  Gann fan slope followed the selected trade outcome, so a top-wick anchor could still draw bullish/upward if the trade outcome was bullish.
- Updated `build_repeatation_review_pack.py`:
  - `gannFanForStart()` now sets fan projection from the wick anchor side:
    top wick -> bearish/downward projection;
    bottom wick -> bullish/upward projection.
  - Added a render/draw compatibility guard so older restored draft state is corrected too:
    if stored fan anchor source contains `top`, direction is forced bearish;
    if it contains `bottom`, direction is forced bullish.
  - Drawer now displays fan projection explicitly.
  - Cache version advanced to `repeatation_ui_20260527_gann_wick_direction_v48`.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_134039`
- Restarted server on port `8765` from that pack.
- Browser verification:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_gann_wick_direction_v48&fresh=wickdir2`
  shows:
  `Gann fan: anchored at top wick 2025-05-28 22:00:00+05:30 @ 144.965; projection bearish`.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py reviewer_rule_replay.py`
  `python reviewer_rule_replay.py`
  `python test_strict_shadbala_doctrine.py`
  all passed.

2026-05-27 trusted external source intake workflow:

- User asked where outside trusted values should come from and approved the recommendation.
- Added `trusted_external_sources.md`.
- Source tiers now documented:
  - Tier A: Swiss Ephemeris documentation and Raman ephemeris samples for astronomy/position checks.
  - Tier B: Jagannatha Hora as preferred Shadbala/Jyotish cross-check; PyJHora as secondary automated checker.
  - Tier C: Drik Panchang and secondary Panchanga calculators for Panchanga limb checks.
- Updated `astro_function_certification.py` so Gate 3 is an actual intake loop:
  - reruns preserve existing values in `astro_external_validation_template_20260527.csv`;
  - filled `external_expected_value` and `external_source` values are carried forward;
  - longitude rows compare with `<= 0.02 deg` tolerance;
  - Shadbala/Drik/Virupa rows compare with `<= 0.5 virupa` tolerance;
  - categorical Panchanga rows compare with exact case-insensitive text match.
- Reran certification:
  Gate 3 now reports `0 pass / 0 fail / 35 pending`, which is expected until external expected values are entered.
- Updated `astro_function_research_audit_20260527.md` with the intake workflow.
- Verification:
  `python -m py_compile astro_function_certification.py`
  `python astro_function_certification.py`
  `python reviewer_rule_replay.py`
  `python test_strict_shadbala_doctrine.py`
  all passed.

2026-05-27 4-gate astro/trading certification runner:

- User asked to proceed with the 4-gate certification process.
- Added `astro_function_certification.py`.
- Generated first certification artifacts:
  - `astro_function_certification_report_20260527.md`
  - `astro_function_certification_inventory_20260527.csv`
  - `astro_position_baseline_20260527.csv`
  - `panchanga_baseline_20260527.csv`
  - `astro_external_validation_template_20260527.csv`
  - `trading_rule_replay_result_20260527.json`
- Gate 1 formula inventory:
  9 feature families now have source anchor, implementation file/function, status label, strict/proxy label, validation status, current gap, next action, and ML training policy.
- Gate 2 astronomical baseline:
  Raman ayanamsa Swiss Ephemeris baselines generated for sample cases `8`, `43`, `103`, `127`, and `1889-02-11 00:00 Asia/Tokyo`.
  These are reproducibility baselines, not external validation yet.
- Gate 2 Panchanga baseline:
  generated local Tithi/Paksha/Nakshatra/Pada/Yoga/Karana/weekday baseline rows for the same samples.
- Gate 3 external validation:
  template created with blank expected-value columns for trusted ephemeris/Panchanga/Shadbala/Drik comparison.
- Gate 4 trading replay:
  `reviewer_rule_replay.py` passed.
  Case `127` has data-level replay; cases `8`, `43`, and `103` are still source-guarded pending shared Auto Suggest replay logic.
- Updated `astro_function_research_audit_20260527.md` with the certification runner results.
- Current verdict:
  Shadbala/Drik/Panchanga are `implemented_unvalidated`, not externally certified.
  Raw local LLM prose remains `do_not_train_raw_text`; train only from deterministic evidence, manual notes, verified corrections, and rule lessons.
- Verification:
  `python -m py_compile astro_function_certification.py`
  `python astro_function_certification.py`
  `python -m py_compile astro_function_certification.py reviewer_rule_replay.py build_repeatation_review_pack.py strict_shadbala_doctrine.py panchanga_doctrine.py`
  `python test_strict_shadbala_doctrine.py`
  `python reviewer_rule_replay.py`
  all passed.

2026-05-27 replay guard + astro certification plan:

- User asked to proceed with the next guardrail and asked how to certify the astro functions.
- Added `reviewer_rule_replay.py`.
- Replay v1 behavior:
  - discovers latest AVG(ALL)|MOON square review pack unless `--pack-dir` is supplied;
  - parses generated Plotly HTML directly;
  - decodes typed Plotly arrays;
  - fully replays case `127` selected-window SR wick-touch detection without needing the browser;
  - asserts start rule `first_case_window_sr_line_touch`;
  - asserts start `2025-05-28T22:00:00+05:30`;
  - asserts end `2025-05-28T23:30:00+05:30`;
  - asserts Gann anchor side `top`;
  - asserts at least three selected-window SR touches.
- Replay v1 also adds source guards for teaching cases `8`, `43`, and `103` so the family-rule strings/candidate branches remain present until that browser-side logic is factored into reusable Python.
- Added an Astro Function Certification Plan to `astro_function_research_audit_20260527.md`.
  Proposed gates:
  formula inventory, astronomical position certification, Jyotish doctrine calculator certification, and trading-feature certification.
- Certification labels proposed:
  `implemented_unvalidated`, `proxy_research_feature`, `externally_validated`, `disputed_tradition`, and `do_not_train`.
- Verification:
  `python -m py_compile reviewer_rule_replay.py build_repeatation_review_pack.py strict_shadbala_doctrine.py panchanga_doctrine.py`
  `python test_strict_shadbala_doctrine.py`
  `python reviewer_rule_replay.py`
  all passed.

2026-05-27 Auto Suggest candidate inspector / audit truth pass:

- User asked to implement the candidate inspector and to say plainly what was reviewed and what still has shortcomings.
- `build_repeatation_review_pack.py` now uses cache version:
  `repeatation_ui_20260527_candidate_inspector_v47`.
- Added an Auto Suggest `Candidate check` / `Auto Suggest candidates` table in the marker drawer.
- The table records deterministic start/end decision trails:
  chosen candidate, rejected candidates, reference hardcoded confluence markers, first SR target, next shaded-zone boundary, next hardcoded marker / attribution boundary, time, price, SR price, SR gap, touch band, wick side, and plain-English reason.
- Case `127` browser verification after Clear markers + Auto Suggest:
  start `2025-05-28 22:00:00+05:30 @ 144.965`;
  end `2025-05-28 23:30:00+05:30 @ 145.125`;
  result bullish about `+16.0 pips`;
  Gann fan anchored at top wick;
  candidate table shows 5 candidates and explicitly rejects the later `23:00` / `23:30` SR touches because `22:00` already won.
- Fixed Python compile warning by escaping the generated JavaScript `\s` regex inside the Python string.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_081226`.
- Restarted server from that pack:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_candidate_inspector_v47`.
- Updated `astro_function_research_audit_20260527.md` with:
  what was reviewed, what was not exhaustively reviewed, the candidate-inspector implementation, and remaining risk register.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py` passed with no warning.
  Browser check confirmed candidate table, `2025-05-28 22:00`, `gap 2.2 pips`, and top-wick Gann fan text.

2026-05-27 case 127 first SR wick-touch Auto Suggest:

- User pointed out that case `127` should not start at the later exported hardcoded confluence marker; the earlier `2025-05-28 22:00` candle wick was already close enough to the SR line.
- Root cause found:
  upstream hardcoded selected-case marker export prioritizes confluence dots, so the later `23:30` confluence marker hid the earlier plain SR-line wick touch.
- `build_repeatation_review_pack.py` now adds reviewer-side selected-window SR wick-touch detection:
  it scans candles inside the selected case window against visible SR lines, uses a tight SR band of `max(at-SR epsilon, 3 pips)`, and prefers the first valid wick touch over a later confluence dot for default Auto Suggest start.
- `gannFanForStart()` now respects an explicit `gann_anchor_side` from the chosen start candidate, so case `127` anchors at the top wick even though the reviewed outcome is bullish.
- Rebuilt AVG(ALL)|MOON square pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_041655`
- Restarted server from that pack:
  `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_case_sr_touch_v46b`
- Browser verification after Clear markers + Auto Suggest:
  start `2025-05-28 22:00:00+05:30 @ 144.965`;
  end `2025-05-28 23:30:00+05:30 @ 145.125`;
  result bullish `+16.0 pips`;
  Gann fan anchored at top wick `2025-05-28 22:00:00+05:30 @ 144.965`.
- Added research/audit addendum:
  `astro_function_research_audit_20260527.md`.
  It records the case-127 finding, candidate-inspector recommendation, source cross-check notes, and next audit gates for Shadbala/Drik/Panchanga/rule replay.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py` passed.

Next suggested work:

- Add a marker candidate inspector to the drawer so each Auto Suggest shows all start/end candidates and why one won.
- Build deterministic rule replay/regression checks for teaching cases `8`, `43`, `103`, and `127`.
- Continue the source-backed Jyotish audit: mark each astro feature as implemented, proxy, missing, disputed, externally validated, or needing validation.
- Keep local LLM output contained: deterministic evidence + manual notes + verified dream corrections should be training truth, not raw LLM prose.

## Previous Update - 2026-05-24

2026-05-24 Gann fan visibility / clean SR close:

- User reported on case `103` that the Gann fan was not visible, and earlier noted this recurrence is clean enough that trade should close when price touches SR rather than extending after break confirmation.
- `build_repeatation_review_pack.py` cache key advanced to `repeatation_ui_20260524_gann_clean_sr_v36`.
- Added `Show Gann Fan` button beside `Auto Suggest` in the marker drawer. If Auto Suggest has not run, it runs Auto Suggest; if markers already exist, it refreshes the Gann fan from the current trade start/outcome.
- Adjusted `bearish_bias_support_barrier` Auto Suggest behavior:
  when first support break is confirmed but there is no later attribution-boundary marker/event before extension logic, the clean recurrence target remains the first lower SR touch. New end rule: `family_rule_clean_first_sr_touch_target`.
- Rebuilt the AVG(ALL)|MOON square repeatation pack:
  `D:\GannFinancialAstro\doc\repeatation_review_case_43_avg_all_moon_square_20260524_235119`
  and synced it into the served folder:
  `D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Live URL:
  `http://127.0.0.1:8765/aspect_review_case_103_chart.html?v=repeatation_ui_20260524_gann_clean_sr_v36`.
- Verification: `python -m py_compile build_repeatation_review_pack.py` passed. Live case 103 HTML contains v36, `Show Gann Fan`, `family_rule_clean_first_sr_touch_target`, clean first-SR target text, and Gann anchor-dot code.

2026-05-24 D-drive migration:

- User wanted the project moved off C: before uninstalling PyCharm because C: was almost full and the laptop was lagging.
- Migrated the full active repo/project folder:
  `C:\Users\ADMIN\PycharmProjects` -> `D:\PycharmProjects`.
- Migrated generated review/export docs:
  `C:\Users\ADMIN\Desktop\doc` -> `D:\GannFinancialAstro\doc`.
- Replaced the old C: paths with Windows junctions so existing hardcoded scripts and browser links keep working:
  `C:\Users\ADMIN\PycharmProjects` -> `D:\PycharmProjects`
  `C:\Users\ADMIN\Desktop\doc` -> `D:\GannFinancialAstro\doc`
- Verified the D: repo copy:
  `git status`, latest commits, key scripts/data, and `python -m py_compile build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\explain_case.py`.
- Restarted the repeatation review server from D:
  PID `12308`, command rooted at `D:\PycharmProjects\serve_repeatation_pack.py`, serving `D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Verified live case link returns HTTP 200:
  `http://127.0.0.1:8765/aspect_review_case_103_chart.html?v=repeatation_ui_20260523_draft_ml_reason_v35`.
- C: free space improved from about `1.8 GB` to about `12.2 GB`.

2026-05-24 handoff cleanup:

- Refreshed this recovery handoff after reviewing it from a new Codex app session.
- Confirmed the file is the canonical handoff at:
  `D:\PycharmProjects\CURRENT_PROJECT_HANDOFF.md`.
  The old C: path is now a junction and remains usable for compatibility.
- Main correction:
  the older `Next Recommended Steps` list had become stale because later entries already implemented much of the review UI navigation, marker drawer, local draft ML reason workflow, and Ollama/Jyotish agent setup.
- Updated `Git State` with the latest local commits visible at cleanup time.
- Replaced the stale next-step list with the current continuation path:
  continue AVG(ALL)|MOON square repeatation review, use deterministic evidence plus `Draft ML Reason`, promote/revise/discard provisional ML notes, improve local LLM prompt/model quality only after more cases are reviewed, and then move toward walk-forward validation.

## Previous Update - 2026-05-23

2026-05-23 portable Ollama + local model setup:

- User asked Codex to continue with the recommended local LLM setup.
- Normal `Ollama.Ollama` installer had previously failed/cancelled.
- Checked portable package:
  `Ollama.Ollama.Portable` version `0.20.2`, zip installer from GitHub release.
- `winget install Ollama.Ollama.Portable` downloaded and verified the package but failed during extraction.
- Downloaded the portable zip directly to:
  `D:\Ollama\downloads\ollama-windows-amd64-v0.20.2.zip`
  with size about `1.87 GB`.
- Extracted manually into:
  `D:\Ollama\app`.
- Portable binary path:
  `D:\Ollama\app\ollama.exe`.
- Model storage path:
  `D:\Ollama\models`.
- Set user environment variable:
  `OLLAMA_MODELS=D:\Ollama\models`.
- Started Ollama server:
  `D:\Ollama\app\ollama.exe serve`.
- API verified at:
  `http://127.0.0.1:11434/api/tags`.
- Ollama detected GPU:
  `NVIDIA GeForce GTX 1060` through CUDA, total VRAM reported by Ollama as `6.0 GiB`, available about `5.1 GiB`.
- Pulled model:
  `qwen2.5:3b`, `3.1B`, `Q4_K_M`, size about `1.9 GB`.
- Added helper scripts:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\start_ollama_portable.ps1`,
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\stop_ollama_portable.ps1`.
- Updated `explain_case.py` default local model from `llama3.1` to:
  `qwen2.5:3b`.
- Ran LLM-backed case explanation smoke test for case `43`; output wrote to:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\case_explanations\case_43_jyotish_explanation.md`.
- Important quality finding:
  the local 3B model can run, but it drifted into generic astrology text in the commentary section.
- Mitigation added:
  `explain_case.py` now always puts deterministic plain-English evidence first, then local LLM commentary second, and adds a warning when LLM commentary appears to drift.
- Current intended behavior:
  deterministic Python/evidence remains ground truth;
  local LLM is only a draft explanatory layer until we improve prompts/model quality.
- Sent Telegram progress confirmation:
  portable Ollama is running from `D:\Ollama`, `qwen2.5:3b` is installed, and case explanation now uses deterministic evidence first.

2026-05-23 Telegram relay received messages + 5-minute Codex heartbeat:

- User sent Telegram relay messages and asked Codex to check.
- Verified `codex_telegram_inbox.jsonl` contained two messages:
  `/codex`
  and `if you get this please go with your recommendation of local llm model and install softwares you require`.
- Sent Telegram confirmation:
  `Codex received your Telegram relay message. Proceeding with recommended local LLM setup now.`
- Marked both relay messages seen with:
  `python jyotish_agent\read_codex_relay_inbox.py --mark-seen`.
- Attempted to install Ollama after setting:
  `OLLAMA_MODELS=D:\Ollama\models`.
- Ollama install did not complete:
  winget reported `You cancelled the installation`, installer exit code `5`.
- User then asked to check relay messages every 5 minutes as an automation before hibernating.
- Created active Codex heartbeat automation:
  `check-telegram-codex-relay-inbox`,
  schedule every 5 minutes,
  attached to this thread.
- Automation task:
  check `C:\Users\ADMIN\PycharmProjects\jyotish_agent\codex_telegram_inbox.jsonl`,
  use `read_codex_relay_inbox.py`,
  mark pending messages seen,
  summarize/act in this Codex thread,
  and preserve the normal handoff/backup/commit/push workflow after meaningful changes.

2026-05-23 Telegram -> Codex relay pivot:

- User clarified the desired Telegram behavior:
  not a local LLM chatbot, but a middleman relay from Telegram into the current Codex/project workflow.
- Stopped the in-progress `winget install Ollama.Ollama` attempt from the previous interpretation.
- Added a local Telegram relay inbox:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\telegram_codex_relay.py`.
- The relay does not use OpenAI, does not use a local LLM, and does not execute arbitrary Telegram commands.
- Relay behavior:
  `/codex <message>` queues a normal message for Codex;
  `/urgent <message>` queues a high-priority message for Codex;
  plain text is also saved as a relay message;
  `/status`, `/last`, `/ping`, and `/help` are supported.
- Relay inbox path:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\codex_telegram_inbox.jsonl`.
- Added reader helper:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\read_codex_relay_inbox.py`.
- Start/stop scripts:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\start_telegram_codex_relay.ps1`,
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\stop_telegram_codex_relay.ps1`.
- Relay is currently running as a background Python process:
  `telegram_codex_relay.py --announce-start`.
- Important limitation:
  the Telegram bot cannot directly inject messages into the live Codex app/session unless Codex exposes a supported local session API/websocket. Current implementation creates a durable local inbox that Codex reads during active work.
- Smoke verification passed:
  Python compile,
  one-shot backlog-safe poll,
  background process running,
  and `read_codex_relay_inbox.py` reports no pending messages initially.

2026-05-23 local LLM runtime options + Telegram test:

- User confirmed:
  extracted corpus/index should stay local and uncommitted,
  Telegram test message is allowed,
  laptop is a gaming laptop with space on `D:\`.
- Sent Telegram test message through:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\telegram_notify.py`.
- Telegram result:
  `Telegram message sent.`
- Local hardware check:
  CPU `Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz`,
  `6` cores / `12` logical processors,
  RAM about `16 GB`,
  GPU `NVIDIA GeForce GTX 1060` with about `4 GB` VRAM,
  `D:\` free space about `819 GB`.
- Recommendation:
  start with quantized `3B` to `8B` models and keep generated local corpus/index/model cache on `D:\` if it grows.
- Best first runtime option remains `Ollama` for simplest local API integration with `explain_case.py`;
  `LM Studio` is the friendliest manual/model-browsing option;
  raw `llama.cpp` is best only if later optimization/control becomes more important than setup simplicity.

2026-05-23 local Jyotish RAG agent CLI v1:

- User asked to start with the pending list and create the local LLM/Jyotish agent, and pointed to Telegram scripts under:
  `C:\Users\ADMIN\Desktop\Trading_Algo\New folder`.
- Added local agent scripts under:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent`.
- Added `build_corpus_index.py`:
  builds a local TF-IDF retrieval index from allowed/local sources.
- Current indexed sources:
  local PDF alignment extracts from `pdf_alignment_extracts`,
  SQLite review/rule notes from `gann_aspect_annotations.sqlite`,
  and a schema/sample slice from the SR touch-log CSV.
- Generated local-only artifacts are intentionally ignored by git:
  `jyotish_agent\corpus_chunks.jsonl`,
  `jyotish_agent\index\tfidf_index.joblib`,
  and `jyotish_agent\case_explanations\*`.
- Added `explain_case.py`:
  gathers case evidence from SQLite, retrieves supporting Jyotish/trading notes, and writes a plain-English ML/Jyotish explanation packet.
- `explain_case.py` can use a local Ollama-compatible runtime if available at:
  `http://127.0.0.1:11434/api/generate`;
  otherwise it falls back to deterministic extractive RAG output so work is not blocked.
- Generated a local explanation for case `43`:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent\case_explanations\case_43_jyotish_explanation.md`.
- Case `43` explanation currently says:
  bearish family behavior is present, but support did not break cleanly because total strength is middle, Drik pressure is not strongly bearish, Chesta is only middle, aspect exactness is not tight, touched SR is Jupiter/benefic support, and Moon condition is not unusually damaged.
- Added `telegram_notify.py`:
  reuses the existing Telegram runner/config from `C:\Users\ADMIN\Desktop\Trading_Algo\New folder\telegram_job_runner.py`.
- Telegram dry-run passed without sending a message:
  `telegram_configured=True`, runner exists, chat id present, token present.
- Smoke verification passed:
  Python compile for all new scripts,
  `explain_case.py --case-id 43 --no-llm`,
  and `telegram_notify.py --dry-run`.
- Pending before calling this a real local LLM agent:
  choose the local runtime default (`Ollama` recommended unless user prefers LM Studio/llama.cpp),
  install/select the model,
  connect a `Draft ML Reason` UI button to `explain_case.py`,
  decide when Telegram notifications should be sent,
  and keep full extracted book text/index files local-only unless user explicitly wants them committed.
- Pending after the current AVG(ALL)|MOON square family review:
  rule lifecycle (`provisional -> accepted/revised/discarded`),
  automated astro reason extraction into SQLite notes,
  bullish mirrored SR-barrier family rules,
  and wider public-domain Jyotish corpus ingestion after rights/source review.

2026-05-23 ML Notes drawer + Jyotish agent groundwork v33:

- User asked where ML notes can be read in the marker drawer, then asked to add a clear ML Notes collapsible/dropdown section.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260523_ml_notes_v33`.
- Marker drawer now has a dedicated `ML Notes` collapsible section below `Applied family rules`.
- The new section loads ML notes from SQLite by same `pair_key + aspect` family:
  exact-case ML notes show as `this case`;
  family-scoped ML notes show as `case family`.
- The section renders note id, source case, note type, parsed key fields, and the full saved note body in a wrapped scrollable block.
- Rebuilt AVG(ALL)|MOON square repeatation pack from seed case `43`:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260523_103509`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current direct case 43 URL:
  `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_ml_notes_v33`.
- In-app browser verification passed:
  panel exists, `ML Notes` exists, case `43` shows `astro_reason_not_strong_enough_to_break_support`,
  family note from case `8` shows `confirmed_support_break_but_stop_at_next_event_boundary`,
  and `noWebglVisible=false`.
- Started local Jyotish agent groundwork in:
  `C:\Users\ADMIN\PycharmProjects\jyotish_agent`.
- Added `corpus_manifest.csv` with public-domain/open-access candidates, user-owned PDFs, SQLite notes, and touch-log data sources.
- Added `local_jyotish_agent_plan.md` documenting the strict architecture:
  deterministic Python owns calculations/trades, local LLM explains from retrieved evidence and citations.
- Added `prepare_corpus_skeleton.py` and generated `ingestion_queue.json`.
- Current ingestion queue:
  `6` allowed/local/public-domain-candidate items and `16` manual-review-required items.
- Web/source starting points recorded:
  Dekho Panchang library index (`https://www.dekhopanchang.com/en/learn/library`),
  Surya Siddhanta archive candidate (`https://archive.org/details/surya-siddhanta-translation`),
  Vedanga Jyotisha archive candidate (`https://archive.org/details/VedangaJyotisa`).
- Important policy decision:
  start with local RAG/explanation, not model weight training. Use user-owned/local PDFs and workspace-generated notes; verify rights before ingesting modern translations.
- User asked for Telegram ping if needed; no Telegram connector is available in this Codex workspace, so blockers should be preserved in this handoff and chat instead.

2026-05-23 SR geometry + rule outcome tracking v25:

2026-05-23 SR geometry + rule outcome tracking v25:

- User liked two ideas and asked if they could be implemented:
  explicit SR geometry classification and rule outcome tracking.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260523_sr_geometry_v25`.
- Auto Suggest now records `sr_geometry`:
  whether the chosen SR/marker is below/above entry, its role for the selected direction, and distance in pips.
- Directional SR geometry currently labels:
  bearish + SR below entry = `support/target`;
  bearish + SR above entry = `resistance/entry`;
  bullish + SR above entry = `resistance/target`;
  bullish + SR below entry = `support/entry`.
- Auto Suggest now records `outcome_tracking` when a family rule changes the suggestion:
  rule signed pips, old/default signed pips, and delta.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_004714`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current direct case 43 URL:
  `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_sr_geometry_v25`
- Browser verification on case `43` after clicking `Auto Suggest`:
  `SR geometry: SR is below entry: support/target (-27.9 pips from entry)`;
  `Rule tracking: rule +27.9 pips vs old default +2.2 pips | difference +25.8 pips`;
  live bearish P/L remains `+27.9 pips`;
  no WebGL overlay.
- Reminder after finishing this `AVG(ALL)|MOON square` case-family review:
  implement rule status lifecycle (`provisional -> accepted/revised/discarded`) and automate/draft astro reason extraction with a local Jyotish explanation agent.

2026-05-23 case 43 ML astro-reason note:

- User asked whether the detailed astro reasoning for case `43` had been saved as an ML note.
- Added a dedicated rule note in `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`:
  `note_id=2`, `case_id=43`, `note_type=ml_astro_reason`.
- Note label:
  `astro_reason_not_strong_enough_to_break_support`.
- Linked family rule:
  `bearish_bias_support_barrier`.
- The note records:
  price entered the event/zone, touched SR below price, and reverted instead of breaking support.
- The note captures these ML learning reasons:
  total planet strength is middle (`~383`, ratio `~1.09`), above minimum but not forceful-break strength;
  aspect pressure is middle/slightly positive, not sharply negative;
  motion strength is middle/low-ish, so no strong Chesta-style force clue;
  aspect distance is middle, not very tight/exact;
  touched SR is Jupiter, a benefic/supportive line, so falling into Jupiter SR below price can act as support/floor;
  Moon condition is not badly damaged and common Moon friend/exaltation clues are not special bearish-break clues.
- Trading implication captured:
  bearish bias into support should prefer earlier short entry and target/support exit, not late continuation short after support touch unless break-and-retest confirms.

2026-05-23 family-rule automarker v24:

- User asked to wire the applied family rule into `Auto Suggest`.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260523_rule_automarker_v24`.
- Auto Suggest now checks applied family rules before the old fallback.
- For `bearish_bias_support_barrier`, when outcome is bearish and the rule is applied:
  - trade start uses the case-window entry/open price from `full_window_entry_price`;
  - trade end uses the first lower hardcoded SR/marker after the case-window entry;
  - the suggestion reason explicitly says it is treating SR below price as target/support instead of assuming immediate support break.
- The old fallback remains for charts/families without this rule:
  selected hardcoded marker -> next later marker.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_001034`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current direct case 43 URL:
  `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_rule_automarker_v24`
- Verification passed:
  Python compile, full repeatation pack rebuild/sync, served HTML checks, and in-app browser test clicking `Auto Suggest` on case `43`.
- Browser test result for case `43`:
  auto suggestion `rule clean`,
  start `2025-04-04 02:30:00+05:30 @ 146.158`,
  end `2025-04-04 02:30:00+05:30 @ 145.879`,
  live bearish P/L `+27.9 pips`,
  no WebGL overlay.

2026-05-22 applied case-family rule v23:

- User clarified that a local rule should apply to the unique case family with all repeatations, not only one occurrence.
- Updated rule note `note_id=1` in `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`:
  `note_type=family_sr_rule`,
  `scope=case_family/local`,
  `status=provisional_until_all_repeatations_reviewed`,
  `rule_label=bearish_bias_support_barrier`,
  `seed_case_id=43`,
  `family=AVG(ALL)|MOON::square`.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260522_family_rules_v23`.
- The reviewer pack now loads case-family scoped rule notes from SQLite and injects them into every chart in the same `pair_key + aspect` family as `appliedFamilyRules`.
- The marker drawer now shows an `Applied family rules` block above ML trait hints; for this family it displays:
  `bearish_bias_support_barrier`, provisional status, seed case `43`, and family `AVG(ALL)|MOON::square`.
- `repeatation_marker_template.csv` now includes `applied_family_rules_json` so ML exports can consume the same family rule.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260522_235321`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current direct case 43 URL:
  `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260522_family_rules_v23`
- Verification passed:
  Python compile, full repeatation pack rebuild/sync, HTTP checks confirming the rule appears in both case `43` and case `8`, and in-app browser check confirming the drawer shows `Applied family rules` and `bearish_bias_support_barrier`.

2026-05-22 case 43 local SR rule note:

- User reviewed case `43` and observed price entered the selected zone, touched SR below price, and reverted instead of breaking support.
- Case context:
  `case_id=43`, `AVG(ALL)|MOON square`, default/full-window direction `bearish`, but full-window bearish result was only about `+1.0 pip`.
- Interpretation captured:
  case 43 is a local example of bearish pressure into support, not a clean bearish breakdown.
- Saved local DB rule note in `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`:
  `note_id=1`, `case_id=43`, `note_type=local_sr_rule`.
- Rule note text records:
  `scope=case_id/local; type=sr_rule; direction=bearish; if active/nearest SR is below current price, treat it first as target/support and expect touch-revert unless a candle closes below SR and retests/fails. Preferred trade plan is earlier short entry when price enters the selected event/zone, take profit at first lower SR or next hardcoded marker, and avoid chasing continuation after support touch without break confirmation.`
- Astrology reason recorded:
  total planet strength middle (`~383`, ratio `~1.09`), aspect pressure middle/slightly positive, motion strength middle, aspect not tight/exact, and touched SR is Jupiter/benefic support.
- ML label recorded:
  `bearish_bias_support_barrier`.
- This is intentionally a local/case rule until more case_ids are manually reviewed.

2026-05-22 WebGL-free Plotly reviewer v21:

- User saw `WebGL is not supported by your browser` in the Codex in-app browser after opening the v20 chart.
- Root cause: `sr_touch_lazy_dashboard.py` still used Plotly `go.Scattergl` traces for planetary SR lines and interaction markers. Chrome can render these, but the Codex in-app browser may not expose WebGL.
- Updated `C:\Users\ADMIN\PycharmProjects\sr_touch_lazy_dashboard.py` to use regular SVG-safe `go.Scatter` for those traces.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260522_svg_plotly_v21`.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260522_173238`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260522_svg_plotly_v21`
- Direct seed chart URL:
  `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260522_svg_plotly_v21`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, exported chart data trace parse showing `52` SVG `scatter` traces and `1` candlestick trace with no active `scattergl` data traces, and in-app browser check confirming the chart renders with `noWebglVisible=false`.

2026-05-22 all-astro repeatation evidence table v20:

- User asked whether enemy sign, friendly house, and other astro features are being compared across repeatations of the same case family, with only the most distinguishable features shown.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260522_astro_evidence_v20`.
- Added an expandable `All astro feature comparison` block under the ML trait hints. It compares the current repeatation against the same case family across all scored astro/context features, not just the top hints.
- Added plain feature categories:
  `sign / house`, `planet strength`, `timing / moon calendar`, `overlap / cleanliness`, `market-score context`, and `other context`.
- Added house-quality derived features for the aspect planets, using whole-sign house context:
  `supportive/angular-or-luck house`, `growth/action house`, `difficult/hidden house`, `money/relationship pressure house`, and `neutral house`.
- Evidence rows now include repeat count, bullish/bearish split, average pips for matching repeatations, delta versus the full group, group average, and clue tags such as `rare`, `common`, `direction linked`, or `only bearish samples`.
- The fixed `Planet strength` block remains above the ranked hints so Shadbala/strength is always visible.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260522_004530`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260522_astro_evidence_v20`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260522_astro_evidence_v20`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, chart HTTP `200`, served HTML content check, and in-app browser check confirming `All astro feature comparison`, `Planet 2 house`, `Planet 2 sign relationship`, `Total planet strength`, and `sign / house`.

2026-05-21 fixed planet-strength/Shadbala side-panel v19:

- User could not find Shadbala strength in the hover or side menu because the side menu only showed the top six ranked ML traits; full Shadbala total/ratio could be pushed out of the visible list.
- Updated `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260521_strength_panel_v19`.
- Added a fixed `Planet strength` block above the ranked ML trait hints, so Shadbala/strength values are always shown regardless of trait ranking.
- The block currently shows:
  `Total planet strength`, `Strength vs minimum`, `Multi-chart planet strength`, `Timing strength`,
  `Aspect pressure strength`, and `Motion strength`.
- For case 8, verified side-panel values include:
  `Total planet strength: 384.47 (middle)`,
  `Strength vs minimum: 1.12 (middle)`,
  `Multi-chart planet strength: 107.64 (middle)`,
  `Timing strength: 115.16 (middle)`,
  `Aspect pressure strength: -7.04 (middle)`,
  `Motion strength: 9.11 (middle)`.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_204659`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_strength_panel_v19`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_strength_panel_v19`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, chart HTTP `200`, served HTML content check, and in-app browser check confirming the side panel contains `Planet strength`, `Total planet strength`, and `Strength vs minimum`.

2026-05-21 plain-language trait hints v18:

- Reworked the ML trait hints language in `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py` so non-astrology users can understand the panel.
- Repeatation UI version advanced to:
  `repeatation_ui_20260521_plain_traits_v18`.
- Numeric trait labels now show actual values and bucket meaning, for example:
  `Aspect distance from exact: 51.36 (middle)`.
- Numeric rows also show cutoff lines where available:
  `Value 51.36 | low <= 45.00 | high >= 75.00`.
- Jargon was softened:
  `event orb deg` -> `Aspect distance from exact`;
  `strict drik` -> `Aspect pressure strength`;
  `strict saptavargaja` -> `Multi-chart planet strength`;
  `strict kaala` -> `Timing strength`;
  `strict chesta` -> `Motion strength`;
  `shadbala total` -> `Total planet strength`.
- Tag explanations were simplified:
  `direction linked` now means this clue has repeatedly leaned one way and is at least 8 pips away from the group average.
- Trait guide language was simplified and now includes numeric examples.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_201252`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_plain_traits_v18`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_plain_traits_v18`
- Trait guide URL:
  `http://localhost:8765/trait_guide.html?v=repeatation_ui_20260521_plain_traits_v18`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, chart HTTP `200`, plain-language/numeric content check, and trait guide HTTP `200`.

2026-05-21 repeatation trait guide v17:

- Improved the ML trait hints panel in `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`.
- Repeatation UI version advanced to:
  `repeatation_ui_20260521_trait_guide_v17`.
- Each trait row now includes a short inline explanation and browser tooltip.
- Added an `Open trait guide` link in the marker drawer that opens:
  `trait_guide.html`
  in a separate tab/window.
- The guide explains review terms such as:
  `event orb deg low/mid/high`, `direction linked`, `rare`, `common`, `only bullish samples`,
  `only bearish samples`, `x/y repeatations`, `pips vs group`, `active regime count`,
  strict Drik, Saptavargaja, Kaala, Chesta, TN/base TN score, and touch planets.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_195842`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_trait_guide_v17`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_trait_guide_v17`
- Trait guide URL:
  `http://localhost:8765/trait_guide.html?v=repeatation_ui_20260521_trait_guide_v17`
- Verification passed:
  Python compile, repeatation pack rebuild/sync, chart HTTP `200`, and trait guide HTTP `200`.

2026-05-21 full Shadbala component v1 expansion:

- Expanded `C:\Users\ADMIN\PycharmProjects\strict_shadbala_doctrine.py` from the strict Drik foundation into `STRICT_SHADBALA_V3_FULL_COMPONENT_V1`.
- Implemented Saptavargaja Bala over D1/D2/D3/D7/D9/D12/D30 using compound temporary + natural relationship scoring, with per-varga detail JSON.
- Implemented Ojayugma Bala using odd/even Rashi and Navamsa logic.
- Added explicit Kaala Bala v1 subcomponents:
  Nathonnatha, Paksha, Tribhaga, Abda, Masa, Vara, Hora, Ayana, and Yuddha.
- Added Chesta Bala speed-state v1 for non-luminary classical planets.
- Added Graha Yuddha detector for Mars/Mercury/Jupiter/Venus/Saturn within 1 degree, using ecliptic latitude as the v1 tie-breaker where available.
- Kept Rahu/Ketu out of Shadbala totals as proxy shadow nodes. `AVG(ALL)` remains a seven-classical-planet component-wise mean, not a node/outer-planet average.
- `build_aspect_sr_touch_log.py` now passes Swiss Ephemeris speed, latitude, declination, timestamp, and Tokyo longitude into strict Shadbala context.
- `doctrine_config.yaml` / `doctrine_config.py` now document the v16 decisions:
  seven-classical `AVG(ALL)`, Saptavargaja compound relationship policy, deterministic Abda/Masa epoch-day policy pending cross-validation, speed-state Chesta v1, and Yuddha within-1-degree policy.
- `aspect_annotation_store.py` now preserves the new strict Shadbala context fields in case JSON.
- `build_repeatation_review_pack.py` advanced to:
  `repeatation_ui_20260521_full_shadbala_v16`
  and now includes strict Saptavargaja, Ojayugma, Kaala, Chesta, Yuddha, rule IDs, and validation-gap tokens in ML trait hints.
- `sr_touch_lazy_dashboard.py` hover/detail lines now show compact:
  Drik, Saptavargaja, Kaala, Chesta, v1 total, ratio, and status.
- Added doctrine regression tests:
  `C:\Users\ADMIN\PycharmProjects\test_strict_shadbala_doctrine.py`
  covering Drik formula checkpoints, Navamsa/Ojayugma, Saptavargaja detail shape, Nathonnatha local mean time, Chesta/Yuddha decisions, and `AVG(ALL)` context output.
- Rebuilt canonical Raman touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  with `656` rows.
- Refreshed `gann_aspect_annotations.sqlite`; no new case IDs inserted.
- Exported fresh v16-aware full-year switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_165758.html`
  and CSV:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_165758.csv`
  with `732` visible rows.
- Rebuilt scored candidates:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  and `.parquet`, with `732` rows, `WIN=402`, `LOSS=327`, `IGNORE=3`.
- Rebuilt case 8 AVG(ALL)|MOON square repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_165838`
  and synced it into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_full_shadbala_v16`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_full_shadbala_v16`
- Verification passed:
  Python compile, `python test_strict_shadbala_doctrine.py`, smoke touch-log build, full touch-log regeneration, DB context refresh,
  switch export, candidate rebuild, repeatation pack rebuild/sync, localhost HTTP `200`, and served chart content check for v16 strict Shadbala hover text.

2026-05-21 strict Drik Bala / Shadbala v2 foundation:

- Added `C:\Users\ADMIN\PycharmProjects\strict_shadbala_doctrine.py`.
- Implemented strict formula-foundation Drik Bala using the six Sripati/Parasara aspect-strength formula segments:
  no aspect under 30 degrees or over 300 degrees forward, base strength over the 30-300 degree range,
  and special exact aspect bonuses for Jupiter `120/240`, Saturn `60/270`, and Mars `90/210`.
- Drik Bala is signed by natural benefic/malefic policy:
  Jupiter/Venus/Mercury and waxing Moon positive, Sun/Mars/Saturn and waning Moon negative.
- Added event-chart partial Shadbala v2 components for classical planets:
  Naisargika Bala, Uchcha Bala, Kendradi Bala, Drekkana Bala, Dig Bala, and strict Drik Bala.
- Added explicit non-fake status:
  `partial_high_confidence_components_pending_saptavargaja_kaala_chesta_yuddha`.
  Pending pieces remain visible as missing components: Saptavargaja, Ojayugma, full Kaala Bala, Chesta Bala, and Yuddha Bala.
- `doctrine_config.yaml` / `doctrine_config.py` now advertise:
  `shadbala.method=strict_shadbala_v2_partial_components`,
  `drik_bala.method=parashara_sripati_six_formula_signed`,
  and `PARASHARA_SRIPATI_DRIK_BALA_SIX_FORMULA_V1`.
- `build_aspect_sr_touch_log.py` now computes strict Drik/Shadbala event context at the event best-aspect time using the Raman sidereal longitudes and Tokyo reference event houses.
- `aspect_annotation_store.py` context columns were extended for strict Shadbala/Drik fields.
- `build_repeatation_review_pack.py` now includes strict dignity, strict Drik, and partial Shadbala totals in ML trait hints.
  Repeatation UI version advanced to:
  `repeatation_ui_20260521_strict_shadbala_v15`.
- `sr_touch_lazy_dashboard.py` now shows compact strict Shadbala hover/detail text.
- Regenerated the Raman touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  with `656` rows and `656` unique events.
- Re-imported cases into `gann_aspect_annotations.sqlite`; no new cases inserted, existing contexts refreshed.
- Exported fresh strict-Shadbala-aware full-year switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_162717.html`
  and CSV:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_162717.csv`
  with `732` visible rows.
- Rebuilt scored candidates:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  and `.parquet`, with `732` rows, `WIN=402`, `LOSS=327`, `IGNORE=3`.
- Rebuilt and synced the AVG(ALL)|MOON square repeatation pack into:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_strict_shadbala_v15`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_strict_shadbala_v15`
- Verification passed:
  Python compile, strict Drik formula sanity check, slice smoke build, full regeneration, DB context check for case 8,
  localhost HTTP `200`, and in-app browser direct chart check for strict Shadbala hover content.

2026-05-21 Panchanga doctrine foundation:

- Added `C:\Users\ADMIN\PycharmProjects\panchanga_doctrine.py`.
- Panchanga is now computed deterministically from Raman sidereal Sun/Moon longitude at the event best-aspect moment, plus event start/end change flags.
- New touch-log/context fields include:
  `event_weekday`, `event_weekday_lord`, `event_tithi_name`, `event_paksha`, `event_karana_name`,
  `event_yoga_name`, `event_moon_nakshatra`, `event_moon_pada`, `event_sun_nakshatra`, `event_sun_pada`,
  `event_near_new_moon_flag`, `event_near_full_moon_flag`, and tithi/karana/yoga/nakshatra change flags.
- `doctrine_config.yaml` and `doctrine_config.py` now expose `panchanga.method=deterministic_sidereal_sun_moon`,
  `panchanga.status=formula_foundation_pending_traditional_validation`, and `PANCHANGA_SIDEREAL_SUN_MOON_V1`.
- `aspect_annotation_store.py` now refreshes existing case `context_json` on import while preserving case IDs and annotations. This prevents stale case context after doctrine-field additions.
- `build_repeatation_review_pack.py` now includes Panchanga fields in ML trait hints. Repeatation UI version advanced to:
  `repeatation_ui_20260521_panchanga_v14`.
- `sr_touch_lazy_dashboard.py` now displays compact Panchanga lines in event hover/detail text.
- Regenerated the Raman touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  with `656` rows and `656` unique events.
- Re-imported the touch log into `gann_aspect_annotations.sqlite`; no new cases inserted, but all existing case contexts were refreshed with Panchanga fields.
- Rebuilt and synced the AVG(ALL)|MOON square repeatation pack into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_panchanga_v14`
- Direct seed chart URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260521_panchanga_v14`
- Browser smoke check verified the direct chart contains Panchanga hover data and Panchanga ML trait tokens.
- Exported fresh Panchanga-aware full-year switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_122019.html`
  and CSV:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_122019.csv`
  with `732` visible rows.
- Rebuilt scored candidates from the fresh switch CSV:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  and `.parquet`, with `732` rows, `WIN=402`, `LOSS=327`, `IGNORE=3`.

2026-05-21 astro function / web research audit:

- Added `C:\Users\ADMIN\PycharmProjects\astro_function_research_audit_20260521.md`.
- The audit reviewed current Python astro functionality against local PDF extracts and web sources:
  Swiss Ephemeris programmer docs, PySwisseph package reference, Shadbala overview cross-check, Panchanga references, Tithi definition, and Gann/financial astrology feature references.
- Current implementation assessment:
  - strong foundation: sidereal transit/event pipeline, graha/rashi aspects, SR/Gann-style planetary lines, JPY/USD reference scoring, repeatation marker UI, ML trait hints, and doctrine metadata;
  - proxy fields: BPHS-like orb strength is useful but not strict Drik Bala; current Shadbala is still minimum-threshold/basic-Sthana foundation only;
  - duplicate risk: `build_trade_candidates_from_touches.py` still has its own dignity tables and should be unified through `shadbala_doctrine.py`.
- Key missing doctrine/features before serious ML training:
  1. lock ayanamsa/node/house policy in `doctrine_config.yaml`;
  2. unify dignity logic through `shadbala_doctrine.py`;
  3. add Panchanga core: tithi, paksha, vara, nakshatra/pada, yoga, karana;
  4. rebuild candidates with doctrine metadata;
  5. add purged/embargoed walk-forward validation;
  6. later add full Shadbala, strict Drik Bala, combustion/station/speed, functional benefic/malefic, Vargas, Dasha, and Gann scale/harmonic variants.
- User chose Raman ayanamsa as personal doctrine preference after the audit.
- `doctrine_config.yaml` now locks:
  - `ayanamsa: Raman`
  - `ayanamsa_swiss_ephemeris_id: SIDM_RAMAN`
  - `node_type: true_node`
- `doctrine_config.py` now exposes `configure_swiss_ephemeris_sidereal()`, which applies `swe.set_sid_mode(swe.SIDM_RAMAN)`.
- Raman sidereal mode is now applied in the core rebuild/export scripts:
  `build_aspect_sr_touch_log.py`, `sr_touch_lazy_dashboard.py`, `build_pair_aspect_market_log.py`,
  `build_sr_anchor_reversal_log.py`, `generate_sr_candidate_chart_pack.py`, `sr_lazy_reactive_dashboard.py`,
  and `rebuild_dataset_mt5_ipo_allpairs.py`.
- The Rahu/Ketu branch in `build_aspect_sr_touch_log.py` now avoids double sidereal correction by calculating the true node tropically and then applying the configured Raman ayanamsa correction once.
- Important implication: future serious ML training should regenerate the event dataset, touch log, candidates, annotation context, and repeatation review pack under `doctrine_ayanamsa=Raman`. Do not silently mix old default/Lahiri-style artifacts with Raman-derived features.

2026-05-21 Raman artifact regeneration:

- Regenerated the event source under the Raman doctrine lock with:
  `python rebuild_dataset_mt5_ipo_allpairs.py --ticker USDJPY --interval 1h --start-date 2025-03-01 --end-date 2026-03-10 --future-end-date 2026-04-10 --analysis-mode natal --reference-chart-type ipo --coordinate-system geo --astrology-method sidereal --aspect-mode orb --ipo-date 1889-02-11 --ipo-time 00:00 --hq-city Tokyo --hq-country Japan --output-file C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet --price-parquet C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet`
- The Raman event dataset now has `804` rows, date range `2025-03-01 00:30:00+05:30 -> 2026-03-09 14:30:00+05:30`, aspect counts `square=274`, `trine=252`, `opposition_orb=142`, `conjunction_orb=136`.
- Backed up pre-Raman generated artifacts to:
  `C:\Users\ADMIN\PycharmProjects\generated_artifact_backups\pre_raman_regen_20260521-110658`.
- Rebuilt the canonical all-duration transitsign touch log from the Raman event dataset:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  with `656` rows and `656` unique `event_id` values. Its doctrine metadata is `doctrine_ayanamsa=Raman`, `doctrine_ayanamsa_swiss_ephemeris_id=SIDM_RAMAN`, `doctrine_node_type=true_node`.
- Reset/re-imported `gann_aspect_annotations.sqlite` from the Raman touch log because the old case table would mix doctrines. There were no saved trade/rule annotations in the DB before reset. New case count: `656`.
- Exported fresh Raman switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_111526.html`
  and CSV:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260521_111526.csv`
  with `1078` visible rows.
- Rebuilt scored candidates from the Raman switch CSV:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  and `.parquet`, with `1078` rows, `1078` potential trades, `4` ignored, `WIN=582`, `LOSS=492`, `IGNORE=4`.
- Fixed `build_trade_candidates_from_touches.py` so raw touch logs missing `zone_kind` / `touch_kind` no longer crash on string fallback. Candidate scoring should still use the switch CSV when trade direction labels are needed.
- The AVG(ALL)|MOON square family shifted under Raman from old seed `case_id=11` / old selected `case_id=120` to new seed `case_id=8`; repeatation count is now `16`.
- Rebuilt the Raman repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260521_111637`.
- Synced the Raman pack into the currently served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`
  after clearing stale old case files.
- Current reviewer URL:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260520_traits_v12_raman`
- Direct first Raman case URL:
  `http://localhost:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260520_traits_v12_raman`
- The old direct URL `aspect_review_case_120_chart.html` now contains a local redirect note to the updated reviewer so the browser does not show stale pre-Raman content.

2026-05-21 repeatation outcome default fix:

- User observed case 8 live trade result/callout still showed `bullish` while `ML trait hints` correctly showed bearish behavior.
- Root cause: marker drawer `Outcome` selector had a hardcoded `bullish` default, and old autosaved drafts could preserve that default even when the case full-window direction was bearish.
- `build_repeatation_review_pack.py` now injects `defaultOutcome` into each chart's marker UI metadata based on `full_window_direction`.
- Initial outcome now defaults to the recurrence's full-window direction (`bullish` or `bearish`; otherwise `unclear`) while still allowing manual override.
- Draft schema advanced to version `2` with `outcome_touched`; old version-1 drafts that only inherited the hardcoded bullish default are migrated to the case default when the case default is not bullish.
- `Clear saved draft` now resets to case default outcome instead of hardcoded bullish.
- Repeatation UI version advanced to:
  `repeatation_ui_20260521_outcome_default_v13`
- Rebuilt and re-synced the Raman AVG(ALL)|MOON square review pack into the served folder:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Verified served `aspect_review_case_8_chart.html` contains `defaultOutcome: "bearish"`, `outcomeTouched`, and v13 cache links; reviewer URL returned HTTP `200`.
- Current reviewer URL after this fix:
  `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260521_outcome_default_v13`

2026-05-21 doctrine hardening foundation:

- Added `C:\Users\ADMIN\PycharmProjects\doctrine_config.yaml`.
- Added `C:\Users\ADMIN\PycharmProjects\doctrine_config.py`.
- Future generated touch logs / trade candidates / dashboard exports now carry doctrine metadata columns including `doctrine_config_id`, `doctrine_drishti_status`, `doctrine_shadbala_method`, `doctrine_rule_citation_status`, and `experimental_layer_flags`.
- Current BPHS strength fields are preserved for compatibility, but explicit proxy aliases were added: `event_bphs_like_orb_strength`, `event_bphs_like_orb_virupa`, and `event_strength_doctrine_status=bphs_like_orb_proxy_not_full_drik_bala`.
- Shadbala tags/averages now carry `shadbala_doctrine_status=source_or_proxy_pending_full_six_bala_calculation`.
- Added seven-classical-planet minimum Shadbala total virupa thresholds from the Shadbala PDF text extraction: Sun 300, Moon 360, Mars 300, Mercury 420, Jupiter 390, Venus 330, Saturn 300. Future rows with `b1`, `b2`, and `shadbala_avg` get `event_shadbala_minimum_total_virupa_avg` and `event_shadbala_avg_minus_minimum_virupa`.
- `astro_feature_inventory_from_pdfs.md` and `vedic_pdf_alignment_review_20260520.md` were updated so LOCK_DOCTRINE_CONFIG is no longer marked as completely missing.
- Smoke checks passed: `python -m py_compile doctrine_config.py build_aspect_sr_touch_log.py build_trade_candidates_from_touches.py sr_touch_lazy_dashboard.py aspect_annotation_store.py`; metadata append tested against the current touch log.

2026-05-21 Shadbala doctrine foundation:

- Added `C:\Users\ADMIN\PycharmProjects\shadbala_doctrine.py`.
- The module defines source-cited Shadbala/Sthana constants:
  - `SHADBALA_MINIMUM_TOTAL_VIRUPA`: Sun 300, Moon 360, Mars 300, Mercury 420, Jupiter 390, Venus 330, Saturn 300.
  - basic Sthana sign dignity rules: exaltation, moolatrikona, own, friend, neutral, enemy, debilitation.
  - rule IDs: `STHANA_SIGN_DIGNITY_V1`, `SHADBALA_MIN_TOTAL_GATE`.
- `build_aspect_sr_touch_log.py` now computes event best-time signs and adds event-level Sthana/minimum fields when logs are regenerated:
  - `event_b1_sign`, `event_b1_sthana_dignity_label`, `event_b1_sthana_dignity_virupa`, `event_b1_sign_relation`, `event_b1_shadbala_minimum_total_virupa`
  - matching `event_b2_*` fields
  - `event_sthana_dignity_virupa_avg`, `event_shadbala_minimum_total_virupa_avg`, `event_sthana_rule_ids`, `event_doctrine_feature_status`
- `build_repeatation_review_pack.py` now appends doctrine metadata while building ML trait hints, so existing touch logs can at least expose Shadbala status/minimum metadata and future regenerated logs will expose event dignity traits too.
- `aspect_annotation_store.py` context columns were extended for the new doctrine fields.
- Compile and smoke tests passed; server still returned HTTP 200.

2026-05-21 doctrine data regeneration:

- Regenerated the canonical all-duration transitsign touch log with the Shadbala/Sthana doctrine fields:

```powershell
python C:\Users\ADMIN\PycharmProjects\build_aspect_sr_touch_log.py `
  --events C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet `
  --price C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet `
  --include-natal `
  --aspect-mode orb `
  --max-event-days 0 `
  --output C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv
```

- Rebuild output stayed stable at `619` rows and `619` unique `event_id` values.
- New columns verified present in the touch log and case 120 visible chart CSV:
  `doctrine_config_id`, `event_b1_sthana_dignity_label`, `event_b2_sthana_dignity_label`,
  `event_sthana_dignity_virupa_avg`, `event_shadbala_minimum_total_virupa_avg`,
  `event_doctrine_feature_status`.
- Re-imported the regenerated touch log into `gann_aspect_annotations.sqlite`; no new case IDs were inserted, preserving existing case numbering.
- Rebuilt the case 11 `AVG(ALL)|MOON square` repeatation pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_20260521_102109`.
- Synced that rebuilt pack into the currently served folder so the existing browser URL keeps working:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`.
- Server verification: `http://127.0.0.1:8765/aspect_review_case_120_chart.html?v=repeatation_ui_20260520_traits_v12_doctrine` returned HTTP `200`, and the served HTML contains the new trait UI tokens.

The repeatation review UI is now at:

```text
repeatation_ui_20260520_traits_v12
```

Latest verified local URL:

```text
http://localhost:8765/aspect_review_case_120_chart.html?v=repeatation_ui_20260520_traits_v12
```

Active local server:

```text
python serve_repeatation_pack.py
http://127.0.0.1:8765/
```

Recent pushed commits:

```text
616908d Add repeatation trait hints
8aff6a0 Add repeatation auto suggest markers
582503c Move repeatation profit callout
6075b55 Add live repeatation trade profit
e877261 Use plus repeatation markers
c32f499 Disarm repeatation marker tools
bf51cb7 Capture and drag repeatation markers
c1a3ca4 Make repeatation marker selection magnetic
```

Latest feature state:

- Marker drawer supports repeatation navigation, draggable plus-style trade/ignore markers, ignore trade signal types, live P/L, auto-suggested start/end, and manual override tracking.
- Auto Suggest places trade start at the first selected-case hardcoded marker and trade end at the next subsequent hardcoded marker when available.
- `ML trait hints` compare a repeatation against its same unique case group and highlight rare/common/direction-linked traits from Shadbala tags, signs/houses, BPHS-like fields, active regimes, and edge-score buckets.
- Plotly Pan is the intended default interaction mode so marker placement does not fight zoom/pan tools.

PDF alignment review added:

```text
C:\Users\ADMIN\PycharmProjects\vedic_pdf_alignment_review_20260520.md
```

Conclusion from the PDF check: current scripts follow the uploaded strict-engine architecture, but current BPHS/Shadbala fields are still simplified proxies. Full Shadbala, exact Drik Bala, doctrine config, rule citations, RAG/local LLM explanation layer, and purged walk-forward validation remain pending.

## Project Goal

Build a deterministic financial astrology research pipeline for USDJPY that:

1. Computes aspect/SR touch events using a Japanese Yen reference chart.
2. Splits chart views by timeframe:
   - M30 for short aspects `<= 24h`
   - H1 for all aspect durations
   - Daily for longer aspects `> 24h`
   - Daily hides Moon SR planetary lines
3. Adds transparent rule-layer hypothesis scores before ML.
4. Later uses ML to validate/calibrate those hypothesis scores with walk-forward validation.

## Git State

Repo:

`C:\Users\ADMIN\PycharmProjects`

Git executable:

`C:\Program Files\Git\cmd\git.exe`

Latest commits at the 2026-05-24 handoff cleanup:

```text
121ed63 Align local ML drafts with auto suggest evidence
dfac27b Add local ML reason draft button
5ca777a Configure portable Ollama local model
60fd655 Record Telegram relay heartbeat
5ec5b39 Add Telegram relay inbox for Codex
fa46c4e Record LLM options and Telegram test
153fbb6 Add local jyotish RAG agent CLI
9897b21 Show ML notes and scaffold jyotish agent
```

Git user email is repo-local:

`gourav.damade@gmail.com`

## Important Scripts

Tracked in Git:

- `build_aspect_sr_touch_log.py`
- `sr_touch_lazy_dashboard.py`
- `build_trade_candidates_from_touches.py`
- `astro_feature_inventory_from_pdfs.md`
- `astro_feature_inventory_from_pdfs.yaml`
- `financial_astrology_source_notes_2026-03-13.md`

## Reference Chart

The quote/reference chart is the Japanese Yen/Tokyo IPO style reference:

```text
ipo-date: 1889-02-11
ipo-time: 00:00
reference-tz: Asia/Tokyo
reference-lat: 35.6762
reference-lon: 139.6503
```

This is used by `build_aspect_sr_touch_log.py` for transit-to-natal fields such as:

- `tn_hits_json`
- `tn_primary_*`
- `tn_bphs_total`
- `touch_planet_*_natal_*`

The base/reference chart added on 2026-05-05 is the USD birth reference supplied by the user:

```text
base-reference-label: USD
base-reference-date: 1776-07-04
base-reference-time: 12:00
base-reference-tz: America/New_York
base-reference-lat: 39.9526
base-reference-lon: -75.1652
```

This is implemented as additional `base_tn_*` fields. The pair hypothesis is:

```text
USDJPY score = USD reference score - JPY reference score
```

## Current Data Files

Generated/ignored by Git:

```text
C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst.csv
C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote.csv
C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations.csv
C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet
C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored.parquet
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote.parquet
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.parquet
C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv
C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet
```

Latest chart export with score hovers:

```text
C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.html
C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.csv
```

M30 data download:

```text
rows: 12429
range UTC: 2025-03-10 00:00 to 2026-03-10 23:30
interval: 30 minutes
```

## Major Completed Changes

### Uranus/Neptune SR Lines

Added Uranus and Neptune planetary SR lines without adding Uranus/Neptune to planetary aspects.

Validation at the time:

```text
raw touch log rows: 604
max rows per event: 1
uranus touch rows: 76
neptune touch rows: 58
uranus aspect pair rows: 0
neptune aspect pair rows: 0
```

### Timeframe Modes

`sr_touch_lazy_dashboard.py` supports:

```text
--timeframe m30
--timeframe hourly
--timeframe daily
--timeframe merged
--timeframe switch
```

Behavior:

- `m30`: real M30 candles required; short aspects `<= 24h`; Moon lines included.
- `hourly`: H1 candles; all aspect durations; Moon lines included.
- `daily`: daily candles; long aspects `> 24h`; Moon SR lines hidden and Moon SR touch rows excluded.
- `merged`: H1 candles; all aspect durations together; Moon lines included.
- `switch`: one HTML with buttons. If M30 price file is supplied, buttons are M30/H1/Daily.

Latest switch validation:

```text
M30:    403 rows, 60-1440 minutes, context/slow excluded rows 0
Hourly: 506 rows, 60-42720 minutes, context/slow excluded rows 0
Daily:   96 rows, 1500-102180 minutes, context/slow excluded rows 3
USDJPY hypothesis hover rows: 1005/1005
Doctrine hypothesis hover rows: 1005/1005
```

### Event Duration Cap

Builder duration cap:

- `build_aspect_sr_touch_log.py`: `--max-event-days`, default `5.0`
- Use `--max-event-days 0` to disable the cap and include all durations available in the event source.
- `sr_touch_lazy_dashboard.py` no longer applies its own hard 5-day loader cap.

Weekly mode requires making this configurable end-to-end before adding `> 5d` weekly buckets.

### Rule-Layer Scoring

`build_trade_candidates_from_touches.py` and `sr_touch_lazy_dashboard.py` now compute a first heuristic score using the Yen IPO reference chart.

Added fields include:

- `aspect_family`
- `duration_bucket`
- `active_hard_aspect_count`
- `active_soft_aspect_count`
- `has_moon_trigger`
- `has_outer_or_node`
- `sr_confirmation_score`
- `jyotish_bullish_score`
- `jyotish_bearish_score`
- `jyotish_net_score`
- `jyotish_conflict_score`
- `jyotish_hypothesis_direction`
- `dominant_aspect_id`
- `dominant_aspect_abs_score`
- `rule_layer_total_strength`
- `rule_layer_conflict_ratio`
- `rule_layer_notes`

Notes field:

```text
heuristic_v1_yen_ipo_tokyo_1889_reference;
uses_transit_natal_house_planet_nature_aspect_family_bphs_sr;
fx_pair_score_is_base_minus_quote_when_base_reference_fields_exist;
ml_must_validate
```

Latest rough sanity summary from scored candidates:

```text
BULLISH hypothesis: 417 rows, win rate about 53.0%
BEARISH hypothesis: 429 rows, win rate about 48.3%
CONFLICT:           118 rows, win rate about 49.2%
```

Do not treat this as proof; M30 and H1 duplicate short-aspect rows in switch exports, and purged walk-forward validation is still needed.

### Chart Hover Details

Latest chart hover now shows the score block on both interaction markers and shaded aspect windows:

```text
Rule-layer hypothesis
Reference chart: Yen IPO Tokyo 1889-02-11 00:00 Asia/Tokyo
Source ref in row: 1889-02-11 00:00:00+09:00 Asia/Tokyo
Hypothesis: BEARISH/BULLISH/CONFLICT
Scores B/Bear/Net/Conflict
Dominant hit
Dominant strength
Rule total strength
Conflict ratio
Aspect family / duration
Active hard/soft
Note: heuristic v1; ML must validate weights.
```

Cluster cache version in `sr_touch_lazy_dashboard.py` is `_clustered_v7.parquet`.

Update on 2026-05-05:

- `build_aspect_sr_touch_log.py` now supports base/quote reference labels and USD base-reference CLI options.
- Default USD base reference is `1776-07-04 12:00 America/New_York`, Philadelphia lat/lon.
- `build_trade_candidates_from_touches.py` adds `score_currency_pair_for_row`.
- `sr_touch_lazy_dashboard.py` adds `FX pair hypothesis` hover lines and `fx_*` export columns.
- Dashboard clustered cache version is now `_clustered_v8.parquet`.
- Older touch logs without `base_tn_hits_json` intentionally show `fx_hypothesis_direction=UNKNOWN` with `base_reference_missing;pair_hypothesis_not_scored`.
- Syntax check passed:
  `python -m py_compile build_aspect_sr_touch_log.py build_trade_candidates_from_touches.py sr_touch_lazy_dashboard.py`
- Smoke load passed on `aspect_sr_touch_log_72h_smoke.csv`: 1854 rows, all old rows `UNKNOWN` for FX pair scoring.
- Synthetic row with both USD and JPY hits produced `BULLISH` with positive `fx_pair_net_score`.

Regenerated artifact update on 2026-05-05:

- New touch log with USD base-reference fields:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote.csv`
- Builder command used `--include-natal --aspect-mode orb --max-event-days 5`.
- Output rows: 604.
- Base reference printed by builder:
  `1776-07-04 12:00 America/New_York -> 1776-07-04 22:26:02 Asia/Kolkata`.
- Validation:
  `base_tn_hits_json` present, `base_hits_nonempty=603/604`.
- Fresh switch chart with FX hover block:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260505_230311.html`
- Chart CSV rows: 964; M30 424, H1 424, Daily 116.
- `FX pair hypothesis` hover block rows: 964/964.
- FX direction counts in chart CSV:
  `BULLISH=403`, `BEARISH=331`, `CONFLICT=118`, `UNKNOWN=112`.
- Rebuilt candidates:
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote.csv`
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote.parquet`
- Quick non-purged sanity result, not proof:
  `BEARISH win_rate=52.57%`, `BULLISH win_rate=46.65%`, `CONFLICT win_rate=54.24%`, `UNKNOWN win_rate=53.57%`.
- Initial read: base-minus-quote score is now implemented and visible, but the naive directional mapping still needs ML/purged walk-forward validation and may need inversion/reweighting.

Timeframe split update on 2026-05-06:

- User requested: M30 `<=24h`, Hourly all aspects including `>24h`, Daily only `>24h`, Daily no Moon planetary SR lines.
- `sr_touch_lazy_dashboard.py` now implements that split.
- Daily also excludes marker rows whose SR touch identity contains Moon, so hidden Moon lines do not still appear as daily marker explanations.
- `build_aspect_sr_touch_log.py` accepts `--max-event-days 0` for uncapped event duration generation.
- New uncapped base/quote touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations.csv`
- Builder command used `--include-natal --aspect-mode orb --max-event-days 0`.
- Output rows: 619.
- Latest switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260506_214025.html`
- Latest switch CSV validation:
  `M30=416 rows, 60-1440 min, >24h=0`;
  `Hourly=520 rows, 60-42720 min, >24h=106`;
  `Daily=96 rows, 1500-102180 min, Moon SR identity rows=0`;
  `FX pair hypothesis hover rows=1032/1032`.
- Rebuilt all-duration candidates:
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.csv`
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.parquet`
- Quick non-purged FX sanity result:
  `BEARISH win_rate=53.54%`, `BULLISH win_rate=46.93%`, `CONFLICT win_rate=53.47%`, `UNKNOWN win_rate=55.47%`.

Active regime-zone update on 2026-05-06:

- `sr_touch_lazy_dashboard.py` now draws a separate active-regime zone layer.
- Regime zones split overlapping event windows at every event start/end boundary.
- Example behavior:
  event X `22/03-25/03` and event Y `24/03-28/03` become:
  `22/03-24/03 X only`, `24/03-25/03 X+Y`, `25/03-28/03 Y only`.
- Each regime zone has its own hover:
  active event list, active count, combined JPY hypothesis, combined JPY scores, zone dominant hit/event/strength, combined FX hypothesis, FX base/quote/net/conflict, FX dominant event/base-hit/quote-hit.
- Latest chart with regime zones:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260506_225211.html`
- Validation from in-memory figures:
  `M30 regime zones=514, overlap zones=156`;
  `Hourly regime zones=916, overlap zones=667`;
  `Daily regime zones=193, overlap zones=137`.
- Latest CSV still contains the 1032 touch rows; regime zones are rendered into the HTML chart layer, not exported as separate CSV rows yet.

Hover simplification update on 2026-05-07:

- Default hovers now show the USDJPY/FX hypothesis only.
- Quote/JPY-only diagnostics are hidden from the default hover because a bullish JPY quote signal usually implies USDJPY bearish unless USD strength offsets it.
- Hovers now show `Click for quote/JPY details`.
- The exported HTML includes a click details panel below the chart. Clicking an event, marker, or active regime zone fills that panel with quote/JPY diagnostics.
- Clustered touch cache version is now `_clustered_v10.parquet` to force regenerated marker hover text.
- Latest chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260507_003720.html`
- Validation:
  CSV rows `1032`; `USDJPY hypothesis` hover rows `1032/1032`; old `Rule-layer hypothesis` rows `0`; visible `Quote/JPY hypothesis` hover rows `0`.

Short-term slow/context-pair exclusion update on 2026-05-08:

- M30 and Hourly now exclude aspect events where both bodies are in:
  `JUPITER`, `SATURN`, `URANUS`, `NEPTUNE`, `PLUTO`.
- M30 and Hourly also exclude `AVG(ALL)`, `RAHU`, or `KETU` paired with those slow bodies.
- Rationale: slow-planet-only combinations should not drive short-term M30/H1 trend views.
- Daily and merged modes do not apply this short-term pair filter.
- Latest chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260508_041401.html`
- Latest switch CSV validation:
  `M30=403 rows, slow-slow/context-slow rows=0`;
  `Hourly=506 rows, slow-slow/context-slow rows=0`;
  `Daily=96 rows, slow-slow/context-slow rows=3`;
  `USDJPY hypothesis hover rows=1005/1005`.
- Candidate file rebuilt from latest chart CSV:
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.csv`
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.parquet`
- Quick non-purged FX sanity result:
  `BEARISH win_rate=53.16%`, `BULLISH win_rate=46.53%`, `CONFLICT win_rate=53.90%`, `UNKNOWN win_rate=54.33%`.

Doctrine dignity scoring update on 2026-05-09:

- Added separate doctrine-v1 score fields without replacing the legacy heuristic `fx_pair_*` fields.
- Doctrine-v1 applies sign dignity/friendship Sthana Bala style modifiers for the seven classical planets:
  exaltation `60V`, moolatrikona `45V`, own sign `30V`, friendly sign `15V`, neutral sign `10V`, enemy sign `4V`, debilitation `0V`.
- Rahu, Ketu, Uranus, Neptune, Pluto remain dignity `unknown` in v1 because sign ownership/exaltation varies by tradition or is not classical.
- Existing touch logs contain natal/reference sign in each hit, so the current chart uses natal/reference dignity. `build_aspect_sr_touch_log.py` now also writes `transit_lon`, `transit_sign`, and `natal_lon` into future hit JSONs when a full touch-log rebuild is run.
- Dashboard clustered cache version is now `_clustered_v11.parquet`.
- Latest chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260509_051836.html`
- Latest switch CSV validation:
  `rows=1005`;
  `M30=403 rows, slow-slow/context-slow rows=0`;
  `Hourly=506 rows, slow-slow/context-slow rows=0`;
  `Daily=96 rows, slow-slow/context-slow rows=3`;
  `USDJPY hypothesis hover rows=1005/1005`;
  `Doctrine hypothesis hover rows=1005/1005`.
- Doctrine direction counts:
  `BULLISH=380`, `BEARISH=302`, `CONFLICT=196`, `UNKNOWN=127`.
- Candidate file rebuilt from latest chart CSV:
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.csv`
  `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations.parquet`
- Quick non-purged doctrine sanity result:
  `BEARISH win_rate=52.32%`, `BULLISH win_rate=43.95%`, `CONFLICT win_rate=59.69%`, `UNKNOWN win_rate=54.33%`.
- Note: a full doctrine-v1 touch-log rebuild was attempted after laptop restarts but did not leave a complete new file. The likely cause, from the lost prior Gann thread, was heavy memory pressure during the full touch-log build, reportedly rising to about 10 GB before the laptop restarted/crashed. Current artifacts use the existing complete all-duration touch log plus the new scorer.
- Verified on 2026-05-10: `aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations.csv` still has no `transit_sign`, `transit_lon`, or `natal_lon` entries inside `tn_hits_json` / `base_tn_hits_json`. A stable-machine rebuild is still required before transit-sign dignity can be used from the touch log itself.

Transit-sign touch-log/candidate update on 2026-05-11:

- Validated transitsign touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
- Rows: `619`; unique event IDs: `619`; event-id set equals the old all-duration touch log.
- Hit JSON validation on the touch log:
  `9356` hits checked across `tn_hits_json` and `base_tn_hits_json`; missing `transit_lon`, `transit_sign`, or `natal_lon`: `0`.
- Latest transitsign switch chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.csv`
- Chart CSV rows: `1005`; chart hit JSON validation:
  `15241` hits checked; missing `transit_lon`, `transit_sign`, or `natal_lon`: `0`.
- Rebuilt transitsign candidates:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet`
- Candidate summary:
  rows `1005`; `potential_trade=1005`; `ignored=6`;
  categories `multiple_aspects=925`, `single_aspect=80`;
  close actions `TAKE_PROFIT=506`, `STOP_LOSS=486`, `TIME_CLOSE_72H=13`;
  ML outcomes `WIN=511`, `LOSS=488`, `IGNORE=6`.
- Doctrine direction counts after transit-sign dignity:
  `BULLISH=377`, `BEARISH=319`, `CONFLICT=182`, `UNKNOWN=127`.
- Compared with prior non-transitsign candidates by `chart_timeframe + touch_id`:
  doctrine pair net score changed on `769/1005` rows;
  base dignity average changed on `540/1005`;
  quote dignity average changed on `550/1005`;
  doctrine direction changed on `52/1005`.
  This confirms the scorer is consuming `transit_sign` from hit JSON, not only natal/reference sign dignity.

Purged walk-forward evaluation on 2026-05-11:

- Added evaluator:
  `C:\Users\ADMIN\PycharmProjects\evaluate_transitsign_walk_forward.py`
- Input:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet`
- Output directory:
  `C:\Users\ADMIN\PycharmProjects\walk_forward_eval_transitsign_20260511`
- Files:
  `summary.json`, `model_summary.csv`, `fold_metrics.csv`, `predictions.csv`
- Setup:
  `999` WIN/LOSS rows used; `5` expanding chronological folds; training rows purged if their `72h` close time overlaps the test fold start; future/outcome columns excluded, including `close_after72`, `ret_after_72h_pct`, exit fields, `ml_outcome`, and source `delta_1d/3d/7d`.
- Feature set after leakage exclusions:
  `179` numeric features and `46` categorical features.
- Best simple ML result:
  `random_forest_balanced` accuracy `54.33%`, balanced accuracy `53.94%`, win precision `55.97%`, win recall `59.32%`.
- Other baselines:
  `logistic_l2_balanced` accuracy `53.00%`, balanced accuracy `51.53%`;
  `dummy_most_frequent` balanced accuracy `50.00%`.
- Raw rule direction win rates on WIN/LOSS rows:
  legacy FX `BULLISH=47.01%`, `BEARISH=53.47%`, `CONFLICT=53.90%`, `UNKNOWN=54.33%`;
  doctrine FX `BULLISH=45.31%`, `BEARISH=53.00%`, `CONFLICT=57.69%`, `UNKNOWN=54.33%`.
- Read:
  The transit-sign doctrine score is not directly usable as a standalone directional signal yet. Treat it as a feature for calibration; inversion, thresholding, and blending should be tested in the purged walk-forward framework before trusting direction labels.

AVG(ALL) 7-classical scoring experiment on 2026-05-11:

- Implemented in:
  `C:\Users\ADMIN\PycharmProjects\build_trade_candidates_from_touches.py`
  and picked up by `sr_touch_lazy_dashboard.py` through its imported scoring functions.
- Rule:
  when a scored event body is `AVG(ALL)`, scoped hit matching expands it to the seven classical bodies:
  `SUN`, `MOON`, `MERCURY`, `VENUS`, `MARS`, `JUPITER`, `SATURN`.
- Rationale:
  `AVG(ALL)` is an artificial basket and should not be assigned a fixed benefic/malefic nature. Expansion lets member-planet transit-natal hits explain the regime instead of showing `n/a`.
- New chart:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_220046.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_220046.csv`
- New candidate variant:
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign_avg7classical.csv`
  `C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign_avg7classical.parquet`
- Targeted screenshot case:
  `AVG(ALL)|MARS trine`, 2025-04-01 to 2025-04-07, changed from `UNKNOWN/n/a` to:
  `BEARISH`, pair net `-1.235`, dominant USD `SATURN>AVG(ALL):square`, dominant JPY `SATURN>SATURN:trine`.
- Coverage comparison vs prior transitsign candidates:
  base dominant blank `393 -> 320`, quote dominant blank `432 -> 338`;
  `fx_pair_net_score` changed on `228/1005` rows;
  `fx_doctrine_pair_net_score` changed on `228/1005` rows;
  doctrine direction changed on `150/1005` rows.
- Direction counts:
  previous doctrine `BULLISH=377`, `BEARISH=319`, `CONFLICT=182`, `UNKNOWN=127`;
  avg7classical doctrine `BULLISH=389`, `BEARISH=360`, `CONFLICT=160`, `UNKNOWN=96`.
- Purged walk-forward output:
  `C:\Users\ADMIN\PycharmProjects\walk_forward_eval_transitsign_avg7classical_20260511`
- Purged walk-forward result:
  `random_forest_balanced` accuracy `48.33%`, balanced accuracy `48.41%`;
  `logistic_l2_balanced` accuracy `50.67%`, balanced accuracy `49.85%`;
  dummy baseline balanced accuracy `50.00%`.
- Rule direction win rates for avg7classical:
  legacy FX `BULLISH=48.36%`, `BEARISH=50.39%`, `CONFLICT=62.40%`, `UNKNOWN=51.04%`;
  doctrine FX `BULLISH=47.79%`, `BEARISH=50.00%`, `CONFLICT=61.88%`, `UNKNOWN=51.04%`.
- Read:
  The 7-classical expansion improves hover explainability and reduces `n/a`, but it did not improve simple purged walk-forward accuracy. Treat as experimental; use it for chart interpretation and as a candidate feature, not as a direct replacement for the prior transitsign scoring baseline.

Chart click-selection update on 2026-05-12:

- `sr_touch_lazy_dashboard.py` now lets the exported Plotly chart highlight the clicked event/regime interval.
- Clicking an aspect shaded window, active regime zone, touch result zone, normal marker, or selected star marker draws a bright yellow selection rectangle from the event/regime start to end across the whole chart height.
- The selection uses a layout shape named `selected-event-window`; each new click replaces the previous highlight.
- Purpose:
  make one specific aspect/regime interval easy to distinguish when multiple shaded windows overlap.
- Fresh chart export with this behavior:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_220048.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_220048.csv`
- CSV visible rows remained `1005`; this was a chart interaction/export change only, not a scoring rebuild.
- Follow-up fix after user reported the yellow click highlight was not visible/working:
  the exported chart now updates the selected interval on `plotly_hover` as well as click, uses a bright red border, red start/end vertical lines, and top annotations showing start/end date-time.
- Fresh chart export with red hover/click interval selection:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_222118.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_222118.csv`
- Second follow-up after user reported hover/click still did not work, and that
  "click for quote/JPY details" never worked on aspect shaded areas:
  `sr_touch_lazy_dashboard.py` now adds transparent click/hover hitbox traces above the candlesticks and planetary SR lines, but below the touch markers.
  This avoids top visual traces swallowing mouse events before the aspect/regime window can receive them.
- The browser script now unwraps nested Plotly `customdata` before reading details, so aspect-window clicks can populate the Quote/JPY details panel instead of losing the payload.
- Fresh chart export with hitbox interaction layer:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_224942.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260512_224942.csv`
- Follow-up on 2026-05-14 after user confirmed highlight works but was unsure
  whether details require single click/double click or only certain points:
  the browser script now remembers the most recent hovered event/regime payload.
  A normal single click within a short hover window locks/updates the Quote/JPY details panel from that remembered payload, so the user should hover until the red window appears, then single-click; no double-click is intended.
- Fresh chart export with hover-target + single-click details fallback:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_180116.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_180116.csv`
- Follow-up on 2026-05-14:
  user asked to disable double-click zoom/reset in the chart and reduce overlap for very short selected aspect windows.
  `sr_touch_lazy_dashboard.py` now writes Plotly HTML with `config={"doubleClick": False, "displaylogo": False}` for both single-timeframe and switch exports.
  Selected-window start/end labels now sit outward from the borders: start label offset left with right alignment, end label offset right with left alignment.
- Fresh chart export with double-click disabled and outward start/end labels:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_185353.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_185353.csv`
- Follow-up on 2026-05-14:
  user reported two interaction problems:
  hovering over markers still triggered selection, and shaded aspect areas without markers could not be selected.
  The browser script no longer registers a `plotly_hover` selection handler; hover only shows Plotly's native tooltip.
  Selection is now single-click only.
  If Plotly does not emit a point click, the DOM click fallback converts the clicked pixel to chart x/y coordinates and scans visible shaded aspect/regime polygons for the containing window, preferring click/hover hitbox traces and shorter windows when overlaps exist.
- Fresh chart export with single-click-only selection and markerless shaded-area fallback:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_201400.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_201400.csv`
- Follow-up on 2026-05-14:
  user clarified that shaded-area selection must select the full clicked aspect window, not stop at the next split regime/aspect boundary like a paint-bucket fill.
  The click-coordinate fallback now ranks full `aspect_window` hitboxes above split `regime_zone` segments, so intermediate regime/aspect boundaries should be skipped for aspect selection.
  Marker clicks are still protected from being overwritten by the underlying shaded-area fallback.
- Fresh chart export with aspect-first shaded-area selection:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_205344.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_205344.csv`
- Follow-up on 2026-05-14:
  user asked to add the aspect name to the red start/end labels for selected shaded zones.
  The selected-window annotations now show `Start`/`End`, then the selected aspect/window label in bold, then the date-time.
  The label is HTML-escaped in the browser script before insertion.
- Fresh chart export with aspect/window name in start/end labels:
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_210417.html`
  `C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260514_210417.csv`
- Follow-up note from user on 2026-05-15:
  latest chart interaction works, but the red `Start` label can sometimes hide behind the M30/H1/Daily soft buttons.
  Next chart UI tweak should move selected-window labels lower/sideways or constrain them away from the timeframe button row.
- New workflow idea from user:
  instead of only asking ML to walk-forward all aspects globally, build an aspect-review agent/workbench.
  When user clicks aspect X, the tool should find same/similar aspects in the generated chart and navigate through them one by one.
  User should be able to mark proposed trade begin/end and ignore regions; system calculates gain/loss, labels bullish/bearish/ignore, and compares divergent outcomes against context factors such as enemy sign, dignity/shadbala strength, multiple overlapping aspects, and other active regimes.
- User clarified aspect-review requirements:
  same aspect means exact same `pair_key + aspect`, and search should cover the full CSV/history, not only the currently visible chart window.
  User wants free placement of start/stop markers inside the selected shaded area and free-form `why` notes so ML can learn from both outcome labels and human rule notes.
  User may add rules such as why a first SR line after the start marker was ignored, for example because it was too close.
  One aspect window may contain multiple trades/annotations and ignore regions.
  Outcome labels should include `bullish`, `bearish`, `sideways`, and `unclear`.
- User agreed with moving beyond Dash for the annotation workbench, but clarified that they do not know SQLite, Tauri, or React.
  Future implementation must be guided like a beginner walkthrough with no assumed knowledge:
  explain each new tool in plain language, introduce one concept at a time, and avoid asking the user to make low-level architecture choices without a recommendation.
  Codex should lead the migration step-by-step and keep the current Python research engine as the familiar anchor.
- First annotation database step on 2026-05-15:
  added `aspect_annotation_store.py`, a beginner-friendly Python helper for creating and testing the local SQLite annotation store.
  Local database path created by default:
  `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`
  The database is intentionally local data and is ignored by git via `.gitignore`.
  Tables created: `aspect_cases`, `trade_annotations`, `ignore_regions`, `rule_notes`, and `schema_meta`.
  Smoke test command passed:
  `python .\aspect_annotation_store.py --init-db --smoke-test`
  Smoke test inserted/read/deleted one sample `MARS|JUPITER opposition` bullish annotation; final annotation tables were empty after cleanup.
- Second annotation database step on 2026-05-15:
  `aspect_annotation_store.py` can now import real aspect cases from a touch-log CSV and list same-aspect occurrences by exact `pair_key + aspect`.
  Import command used:
  `python .\aspect_annotation_store.py --import-cases-from-csv .\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  Result: attempted unique cases `619`, inserted new cases `619`, skipped `0`.
  Database now has `619` `aspect_cases`, `143` exact `pair_key + aspect` groups, and `0` trade annotations.
  Listing commands verified:
  `python .\aspect_annotation_store.py --list-aspects --limit 15`
  `python .\aspect_annotation_store.py --list-cases --pair-key "AVG(ALL)|MOON" --aspect square --limit 5`
  Sample group `AVG(ALL)|MOON + square` had `18` historical cases.
- Third annotation database step on 2026-05-15:
  `aspect_annotation_store.py` can now save and list manual trade annotations for an imported `case_id`.
  New save command shape:
  `python .\aspect_annotation_store.py --add-trade-annotation --case-id 11 --trade-start "2025-03-07 12:00:00+05:30" --trade-end "2025-03-07 13:00:00+05:30" --outcome-label bullish --entry-price 147.10 --exit-price 147.30 --pips 20 --why "reason text"`
  New list command:
  `python .\aspect_annotation_store.py --list-annotations --case-id 11 --limit 5`
  CLI smoke test saved and listed annotation `annotation_id=3` for `case_id=11`, then deleted it.
  Final `trade_annotations` count after cleanup: `0`.
- Fourth annotation database step on 2026-05-15:
  user clarified auto price/pip calculation should support both M30 and H1; Daily will be handled later.
  `aspect_annotation_store.py` now supports `--price-timeframe m30` and `--price-timeframe h1` for auto-calculating entry close, exit close, pips, MFE pips, and MAE pips.
  Default price files:
  `m30`: `C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet`
  `h1`: `C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet`
  Trade markers are now validated to sit inside the selected aspect window.
  H1 smoke test passed on `case_id=11`; M30 smoke test passed on `case_id=15`.
  An out-of-window M30 test on `case_id=11` was rejected with a clean message, no traceback.
  Temporary smoke annotations were deleted; final `trade_annotations` count after cleanup: `0`.
- Fifth annotation database step on 2026-05-15:
  `aspect_annotation_store.py` now has a read-only review queue command:
  `python .\aspect_annotation_store.py --review-aspect --pair-key "AVG(ALL)|MOON" --aspect square`
  It prints total cases, annotated cases, unreviewed cases, the next unreviewed `case_id`, its event/window details, and a copy/edit `--add-trade-annotation` command template.
  Verified sample output for `AVG(ALL)|MOON + square`: total `18`, annotated `0`, unreviewed `18`, next unreviewed `case_id=11`.
  This is the first CLI version of "take user through same aspect one by one."
- Sixth annotation database step on 2026-05-15:
  `aspect_annotation_store.py` now supports ignore regions and free-form rule notes.
  Ignore-region command shape:
  `python .\aspect_annotation_store.py --mark-ignore-region --case-id 11 --region-start "2025-03-07 12:00:00+05:30" --region-end "2025-03-07 12:30:00+05:30" --why "reason text"`
  List ignore regions:
  `python .\aspect_annotation_store.py --list-ignore-regions --case-id 11 --limit 5`
  Rule-note command shape:
  `python .\aspect_annotation_store.py --add-rule-note --case-id 11 --note-type sr_ignore_reason --note "reason text"`
  List rule notes:
  `python .\aspect_annotation_store.py --list-rule-notes --case-id 11 --limit 5`
  Ignore regions are validated to stay inside the selected aspect window; out-of-window test was rejected with a clean message.
  Temporary smoke ignore/note rows were deleted; final counts after cleanup: `trade_annotations=0`, `ignore_regions=0`, `rule_notes=0`.
- Seventh annotation database step on 2026-05-15:
  `aspect_annotation_store.py` now supports `--export-review-case --case-id N` to write a JSON snapshot for a future UI/app bridge.
  Default output path shape:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_<case_id>.json`
  Verified command:
  `python .\aspect_annotation_store.py --export-review-case --case-id 11`
  Output:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11.json`
  Snapshot top-level keys: `case`, `same_aspect`, `saved`, `suggestions`, `exported_at_utc`.
  For `case_id=11`, same-aspect total was `18`, case index was `1`, and saved annotation/note counts were all `0`.
  This JSON is the planned bridge from the Python research/annotation engine into a later React/Tauri review UI.
- Eighth annotation database step on 2026-05-15:
  `aspect_annotation_store.py` now supports `--export-review-html --case-id N` to write a plain static HTML review page from the same review-case payload.
  Default output path shape:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_<case_id>.html`
  Verified command:
  `python .\aspect_annotation_store.py --export-review-html --case-id 11`
  Output:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11.html`
  Page sections: current case, progress, action command templates, saved trade annotations, saved ignore regions, saved rule notes, same-aspect queue, and raw JSON snapshot.
  This is the first no-install visual review page before React/Tauri.
- Ninth annotation database step on 2026-05-15:
  The lightweight SVG price chart preview was rejected because it does not show candlestick patterns, planetary/SR lines, or multiple overlapping events.
  It is no longer part of the review JSON payload or the visible review HTML.
  `sr_touch_lazy_dashboard.py` now supports real generated case chart snapshots from the existing Plotly dashboard renderer:
  `--export-case-chart --case-id N`
  and bulk export:
  `--export-all-case-charts`
  Case snapshots are centered around the selected aspect window, keep candlesticks, SR planetary lines, all overlapping aspect/regime windows, quote/JPY detail click behavior, and add a red selected-case border plus selected touch rings.
  `aspect_annotation_store.py --export-review-html` now embeds/links `aspect_review_case_<case_id>_chart.html` when that chart snapshot exists, instead of rendering a simplified local SVG chart.
  Verified commands:
  `python .\sr_touch_lazy_dashboard.py --touch-log .\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv --price .\usd_jpy_h1_mt5_metaquotes_demo_full.parquet --export-case-chart --case-id 11 --case-timeframe auto --export-dir C:\Users\ADMIN\Desktop\doc --export-max-lines 60`
  `python .\sr_touch_lazy_dashboard.py --touch-log .\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv --price .\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet --export-case-chart --case-id 15 --case-timeframe auto --export-dir C:\Users\ADMIN\Desktop\doc --export-max-lines 60`
  `python .\aspect_annotation_store.py --export-review-html --case-id 11`
  `python .\aspect_annotation_store.py --export-review-case --case-id 11`
  Regenerated outputs:
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11.html`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11.json`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11_chart.html`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_11_chart_visible.csv`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_15_chart.html`
  `C:\Users\ADMIN\Desktop\doc\aspect_review_case_15_chart_visible.csv`
  Verification result: `case_id=11` real chart contains candlestick, selected-case highlight, aspect windows, regime zones, and detail panel; visible rows `12`.
  `case_id=15` with M30 price contains M30 and Hourly switch buttons plus the same real chart context; visible rows `24`.

Case-level feature inventory update on 2026-05-16:

- Added reusable builder:
  `C:\Users\ADMIN\PycharmProjects\build_case_id_feature_inventory.py`
- Generated case inventory:
  `C:\Users\ADMIN\PycharmProjects\case_id_feature_inventory_transitsign_20260516_0132.csv`
- The inventory is one row per saved SQLite `case_id` and joins:
  `gann_aspect_annotations.sqlite`,
  `aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`,
  and `trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv`.
- Output rows: `619`; columns: `92`.
- CSV occurrence distribution from the current rich candidate CSV:
  `0 occurrences=79`, `1 occurrence=75`, `2 occurrences=465`.
  The 2-occurrence cases are usually repeated across M30 and H1; single-occurrence cases are usually daily-only or one visible timeframe; zero-occurrence cases exist in the annotation store/touch log but are not present in the current switch candidate CSV.
- Included fields cover case identity, M30/H1/Daily occurrence counts, natural benefic/malefic classes and biases for the aspect bodies, shadbala tag/average, BPHS-like event strength/virupa, aspect family/duration bucket, regime signature, SR touch identity, jyotish/doctrine/FX pair scores, dominant dignity strings, ML outcome/close-action summaries, and scoped quote/base hit summaries with dignity label counts including enemy/debilitation/unknown plus benefic/malefic component counts.
- Verification:
  `python -m py_compile build_case_id_feature_inventory.py` passed.
  Inventory totals showed quote/base enemy dignity component counts `218/225`; quote/base benefic component counts `538/620`; quote/base malefic component counts `831/764`.

Manual case review sheet update on 2026-05-16:

- Added reusable builder:
  `C:\Users\ADMIN\PycharmProjects\build_manual_case_review_sheet.py`
- Generated full review CSV:
  `C:\Users\ADMIN\PycharmProjects\manual_case_review_sheet_transitsign_20260516_0145.csv`
- Generated focused review CSV:
  `C:\Users\ADMIN\PycharmProjects\manual_case_review_focus_transitsign_20260516_0145.csv`
- Generated focused Excel workbook:
  `C:\Users\ADMIN\PycharmProjects\manual_case_review_focus_transitsign_20260516_0145.xlsx`
- Full review sheet rows: `619`; columns: `119`; recurrence groups: `143`.
- Focus review sheet columns: `47`.
- Manual review columns added:
  `review_status`, `manual_direction_label`, `manual_behavior_label`, `manual_trade_action`, `manual_confidence`, `manual_reason_tags`, `manual_notes`, `reviewed_by`, `reviewed_at_ist`.
- Group-level recurrence fields added:
  `same_aspect_group_key`, `same_aspect_group_size`, group FX doctrine direction counts, group ML outcome counts, group close-action counts, M30/H1/Daily occurrence totals, average shadbala, average FX doctrine net/conflict, and average signed return.
- Script-generated factor tags include:
  `repeated_across_timeframes`, `not_in_current_candidate_csv`, `high_recurrence_group`, `multiple_active_aspects`, `crowded_regime`, `low_shadbala`, `strong_shadbala`, `quote_enemy_sign`, `base_enemy_sign`, `quote_debilitation`, `base_debilitation`, `unknown_outer_or_node_dignity`, `avg_all_composite`, `malefic_pair`, `hard_aspect`, `soft_aspect`, and FX conflict tags.
- Verification:
  `python -m py_compile build_manual_case_review_sheet.py` passed.
  Focus workbook imported successfully, `Manual Review!A1:K12` inspected correctly, formula/error scan matched `0` entries, and a rendered preview of `A1:K16` was checked.

Repeatation review pack update on 2026-05-16:

- User clarified the intended workflow:
  create real chart snapshots for a selected event/case and all its repeatations; manually place start/end, ignore, and rule-note markers; auto-calculate gain/pips and bullish/bearish behavior from marker start/end; then let ML/scripts compare the repeatation family and explain why behavior differs across occurrences before moving to the next case family.
- Added reusable builder:
  `C:\Users\ADMIN\PycharmProjects\build_repeatation_review_pack.py`
- First repeatation family exported from seed `case_id=11`:
  `AVG(ALL)|MOON :: square`
- Repeatation count: `18` cases:
  `11, 44, 97, 120, 150, 169, 196, 250, 269, 304, 378, 500, 515, 543, 548, 560, 578, 603`.
- Local full chart pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_20260516_025027`
- Main review index:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_20260516_025027\repeatation_review_index.html`
- Marker/template CSV:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_20260516_025027\repeatation_marker_template.csv`
- Tracked recovery copy:
  `C:\Users\ADMIN\PycharmProjects\repeatation_review_packs\case_11_avg_all_moon_square_20260516_025027`
- The pack generated 18 real chart snapshots plus visible CSVs. Total local pack size was about `27 MB`; chart HTMLs remain local/regenerable rather than all tracked in Git.
- The marker template includes chart paths, visible-row counts, per-case full-window bullish/bearish pips, script group bias, probable factor tags, and command templates for:
  `--add-trade-annotation`, `--mark-ignore-region`, and `--add-rule-note`.
- Full-window behavior for this family already shows useful divergence against the script group bias `BEARISH`:
  most cases were bearish over the event window, but cases `304`, `500`, `515`, and `603` were bullish, while case `11` was flat by full-window close-to-close.
- Verification:
  `python -m py_compile build_repeatation_review_pack.py` passed.
  The marker template has `18` rows; chart visible rows ranged from `5` to `44`.

Repeatation marker UI update on 2026-05-16:

- `build_repeatation_review_pack.py` now injects a fixed `Repeatation Marker UI` panel into every generated case chart HTML.
- The panel supports click-to-place markers for:
  trade start, trade end, ignore start, and ignore end.
- The chart overlays vertical trade marker lines and an orange ignore-region rectangle when both ignore boundaries are set.
- The panel includes outcome selection, note type, free-form note text, command generation, copy buttons, clear markers, and JSON download for marker payloads.
- Generated commands still write through `aspect_annotation_store.py`, so SQLite stays controlled by the existing Python validation and pips/MFE/MAE auto-calculation logic.
- Latest UI-enabled local pack:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`
- Open:
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548\repeatation_review_index.html`
- Tracked recovery copy:
  `C:\Users\ADMIN\PycharmProjects\repeatation_review_packs\case_11_avg_all_moon_square_ui_20260516_030548`
- Verification:
  `python -m py_compile build_repeatation_review_pack.py` passed.
  The injected marker UI script was extracted from `aspect_review_case_11_chart.html` and parsed with JavaScript `new Function(...)` successfully.
  The in-app browser blocked direct `file://` navigation by policy, so visual browser interaction could not be completed in Codex; use normal Chrome/Edge or open the local HTML directly from Windows for manual UI testing.

Important scoring fix on 2026-05-04:

- Earlier hover scores used the strongest active `tn_hits_json` hit in the whole bar.
- That caused unrelated hits such as `NEPTUNE>RAHU:square` to appear as dominant on `MARS|MOON` or `MERCURY|MOON` hovers.
- The scorer now scopes dominant hits to the hovered row's `pair_key` planets and prefers the hovered aspect type when available.
- If no scoped hit exists, the hypothesis shows `UNKNOWN`/blank instead of using an unrelated dominant hit.

Validation for latest export:

```text
unrelated NEPTUNE>RAHU square count on non-Neptune/Rahu pairs: 0
M30/H1 rows: 424 each, duration 60-1440 min
Daily rows: 116, duration 1500-6660 min
hover rows with rule block: 964/964
```

If the chart still shows old hover details, verify the opened file is the latest export:

`C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260504_213821.html`

Validation for that export:

```text
M30 marker hover rows with rule block: 424/424
M30 figure traces with rule text: 477
```

## PDF Study Artifacts

PDF text extraction folder:

`C:\Users\ADMIN\Desktop\doc\pdf_text_extracts`

PDFs currently registered for project reference:

- `Building a Strict Vedic Astrology Prediction Engine with a Local LLM Layer.pdf`
- `Strict Jyotish Prediction Engine with Local LLM & ML Calibration2.pdf`
- `pdfcoffee.com_financial-astrology-pdf-free.pdf`
- `pdfcoffee.com_futuretec-financial-astrology-set-2-dhruvank-pdf-free.pdf`
- `pdfcoffee.com_gann-financial-astrology-pdf-free.pdf`
- `jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf`

Feature inventory files:

- `astro_feature_inventory_from_pdfs.md`
- `astro_feature_inventory_from_pdfs.yaml`

Shad Bala update on 2026-05-05:

- `C:\Users\ADMIN\Desktop\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.pdf` was verified as readable text.
- Extracted text was generated at:
  `C:\Users\ADMIN\Desktop\doc\pdf_text_extracts\jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.txt`
- Extraction summary: 179 pages, all pages nonempty, about 222k extracted characters.
- Inventory source ID added: `SHADBALA_JAYA`.
- `SHADBALA_GATE` now cites `SHADBALA_JAYA:p23-p101` as the detailed doctrine reference.

PyYAML installed:

```text
PyYAML 6.0.3
```

YAML validation:

```text
sources: 6
doctrine_locks: 4
features: 20
```

Important PDF conclusion:

- The two strict Jyotish PDFs are architecture/doctrine-control docs.
- The Shad Bala PDF is the detailed strength-reference source for future `SHADBALA_GATE` implementation.
- AstroEcon and Futuretek/Dhruvank are experimental feature sources.
- Gann PDF now has OCR text; implementable rules still require manual page verification before coding.
- Gann PDF OCR was completed on 2026-05-10:
  `C:\Users\ADMIN\Desktop\doc\pdf_text_extracts\pdfcoffee.com_gann-financial-astrology-pdf-free.ocr.txt`
  Summary JSON:
  `C:\Users\ADMIN\Desktop\doc\pdf_text_extracts\pdfcoffee.com_gann-financial-astrology-pdf-free.ocr_summary.json`
  Per-page OCR checkpoints:
  `C:\Users\ADMIN\Desktop\doc\pdf_text_extracts\gann_ocr_pages`
- Initial Gann candidate feature families were added to the inventory:
  `GANN_PRICE_LONGITUDE_HIT`, `GANN_OUTER_PLANET_AVERAGE`, `GANN_CIRCLE_ACTIVE_ANGLE`.
  These remain experimental and not implemented; verify page OCR/source images before encoding rules.

## Useful Commands

Export latest switch chart with M30/H1/Daily and FX hover scores:

```powershell
python C:\Users\ADMIN\PycharmProjects\sr_touch_lazy_dashboard.py `
  --touch-log C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv `
  --price C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet `
  --export-full-year `
  --export-dir C:\Users\ADMIN\Desktop\doc `
  --export-max-lines 60 `
  --timeframe switch
```

Rebuild scored trade candidates from latest switch CSV:

```powershell
python C:\Users\ADMIN\PycharmProjects\build_trade_candidates_from_touches.py `
  --touch-log C:\Users\ADMIN\Desktop\doc\sr_touch_full_1year_switch_20260511_015700.csv `
  --price C:\Users\ADMIN\PycharmProjects\usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet `
  --output-csv C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.csv `
  --output-parquet C:\Users\ADMIN\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign.parquet
```

Check Git:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -C 'C:\Users\ADMIN\PycharmProjects' status --short
& 'C:\Program Files\Git\cmd\git.exe' -C 'C:\Users\ADMIN\PycharmProjects' log --oneline -8
```

## Next Recommended Steps

1. Resume manual review of the `AVG(ALL)|MOON + square` repeatation family in the served review pack, starting from the currently interesting cases `8`, `43`, and the next unreviewed repeatations in the same family.
2. For each reviewed case, use the marker drawer workflow:
   `Auto Suggest`, manual marker adjustment when needed, saved trade/ignore/rule notes, `ML Notes`, and `Draft ML Reason`.
3. Treat deterministic Python evidence, saved annotations, SR geometry, break confirmation, attribution boundary, and rule-vs-default pips as ground truth. Treat local LLM output as a draft explanatory layer only.
4. When `Draft ML Reason` agrees with deterministic evidence, use it to speed up note writing. When it drifts, keep the deterministic section and either omit or revise the LLM commentary.
5. Promote, revise, or discard provisional family notes after enough repeatations are reviewed. Current important local ideas include:
   `bearish_bias_support_barrier`,
   `bearish_confirmed_support_break_attribution_boundary`,
   and the related support-break / next-event-boundary behavior.
6. After the AVG(ALL)|MOON square family has enough reviewed examples, generalize the same review loop to mirrored bullish SR-barrier families and other high-value aspect families.
7. Only after more reviewed labels exist, extend walk-forward validation for rule calibration:
   `fx_pair_net_score`, `fx_doctrine_pair_net_score`, SR geometry classes, break-confirmation features, attribution-boundary features, and blended deterministic score variants.
8. Improve local model quality only after the annotation loop exposes repeated explanation failures. Candidate next moves are tighter prompts, a better local model than `qwen2.5:3b`, or richer local RAG retrieval. Keep deterministic evidence first in all cases.
9. Later, add PDF/Gann feature columns one group at a time only after manual source review:
   midpoint hits, stellium, T-square/grand-cross/grand-trine, Dhruvank daily signal, `GANN_PRICE_LONGITUDE_HIT`, `GANN_OUTER_PLANET_AVERAGE`, and `GANN_CIRCLE_ACTIVE_ANGLE`.

## Memory-Safe Touch-Log Rebuild Plan

Reason:
- The prior full touch-log rebuild appears to have crashed/restarted the laptop during high memory use, reportedly around 10 GB.
- `build_aspect_sr_touch_log.py` currently accumulates generated rows in memory and creates one final DataFrame before writing output. That is risky for full all-duration rebuilds with transit-sign hit JSON.

Preferred fix before another full rebuild:
- Add chunked/checkpointed output to `build_aspect_sr_touch_log.py`.
- Process events in small batches, for example 25-50 events per batch.
- Write each batch to `*.partNNNN.parquet` or append-safe CSV immediately after the batch completes.
- Persist a small manifest with batch number, event id range, row count, timestamp, and command args.
- Add `--resume-from-checkpoints` so a laptop restart does not lose completed batches.
- Concatenate checkpoint parquet files only at the end, or let downstream scripts read a checkpoint directory.
- Keep memory bounded by clearing batch row lists/DataFrames after each write.
- Prefer parquet checkpoints over one giant CSV during rebuild; write the final CSV only after successful validation.
- Add a smoke option that rebuilds the first few events with `transit_sign`, `transit_lon`, and `natal_lon`, then verifies those keys before the full run.

Operational fallback:
- If code changes are not desired first, run multiple smaller date/event slices manually and merge after validation.
- Monitor memory during the first full attempt; abort if memory rises steadily instead of plateauing.
- Keep the existing complete all-duration touch log as the fallback source until the new checkpointed rebuild is complete and validated.

Implementation started on 2026-05-10:
- `build_aspect_sr_touch_log.py` now accepts `--event-slice-start`, `--event-slice-size`, and `--dry-run-count`.
- Added `run_touchlog_rebuild_checkpoints.py`, a resumable checkpoint runner.
- Smoke rebuild of 5 events produced hit JSON with `transit_lon`, `transit_sign`, `natal_lon`, and `natal_sign`.
- First real checkpoints:
  `part_00000_00049.csv` completed, 49 rows.
  `part_00050_00099.csv` completed, validated.
- Full background checkpoint runner was started at 2026-05-10 23:36 IST:
  checkpoint dir: `C:\Users\ADMIN\PycharmProjects\touchlog_rebuild_checkpoints_transitsign_20260510`
  final target: `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  total filtered events: `11668`
  batch size: `50`
  runner process observed: `python.exe` running `run_touchlog_rebuild_checkpoints.py`
- Progress check at 2026-05-11 00:04 IST:
  92 checkpoint CSV parts complete, latest complete part `part_04550_04599.csv`, runner processing event slice `4600-4649`.
- Telegram progress monitor started on 2026-05-11:
  script: `C:\Users\ADMIN\PycharmProjects\monitor_touchlog_rebuild_telegram.py`
  interval: 15 minutes
  monitor process observed: `python.exe` PID `7252`
  monitor log: `C:\Users\ADMIN\PycharmProjects\touchlog_rebuild_telegram_monitor.log`
  The monitor uses `C:\Users\ADMIN\Desktop\Trading_Algo\New folder\telegram_remote_control.py` for Telegram config/client support.
  Note: two initial test messages incorrectly said `stopped` because Windows liveness detection used `os.kill(pid, 0)`; this was fixed and corrected `running` messages were sent.
- At 2026-05-11 00:16 IST the runner stopped on `failed_validation` for slice `6100-6149`; the batch generated a valid header-only CSV with zero touch rows, so there were no hit JSON records to validate. This was not a data/schema failure.
- `run_touchlog_rebuild_checkpoints.py` was updated to accept legitimate zero-row/header-only checkpoint parts and non-empty parts with no TN hits, while still rejecting malformed JSON or hit records missing required keys.
- Runner was resumed at 2026-05-11 00:30 IST. Corrected Telegram monitor messages were sent at 00:31 IST with status `running`.
- Progress check at 2026-05-11 00:31 IST:
  126 checkpoint CSV parts complete, latest complete part `part_06250_06299.csv`, runner processing event slice `6300-6349`.
- Completion/correction on 2026-05-11 01:50 IST:
  The broad checkpoint run completed, but it was invalid for the intended file because it used the builder default event source
  `astro_training_data_ipo_tokyo_18890211.parquet` instead of the intended
  `astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet`.
  Resulting broad merge had `11094` rows from `11668` filtered events and must not be used downstream.
- Correct source universe:
  `C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet`
  with `787` filtered events.
- Corrected checkpoint test directory:
  `C:\Users\ADMIN\PycharmProjects\touchlog_rebuild_checkpoints_transitsign_nodes_20260511`
  produced 16 parts, but the slice merge produced `641` rows. A single-pass control on the same 787 events produced `619` rows, matching the old all-duration touch log. Cause: event slicing changes slice-local SR/longitude/regime context, so checkpoint part merges are not semantically equivalent to a single-pass build.
- `run_touchlog_rebuild_checkpoints.py` now refuses to merge event-sliced parts by default unless `--allow-slice-merge` is passed. Treat merged checkpoint parts as diagnostic only until the builder is redesigned to preserve global context while streaming rows.
- Validated final transitsign touch log:
  `C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
  rows: `619`
  unique `event_id`: `619`
  time range: `2025-03-03 12:30:00+05:30` to `2026-03-06 18:30:00+05:30`
  aspect counts: `trine=207`, `square=201`, `opposition_orb=106`, `conjunction_orb=105`
  event-id set equals the old all-duration touch log.
  JSON validation: `9356` hit records checked across `tn_hits_json` and `base_tn_hits_json`; missing required `transit_lon`, `transit_sign`, or `natal_lon`: `0`; malformed JSON: `0`.
- Correct final rebuild command used:
  `python C:\Users\ADMIN\PycharmProjects\build_aspect_sr_touch_log.py --events C:\Users\ADMIN\PycharmProjects\astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet --price C:\Users\ADMIN\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet --include-natal --aspect-mode orb --max-event-days 0 --output C:\Users\ADMIN\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv`
- Do not resume the old broad checkpoint directory `touchlog_rebuild_checkpoints_transitsign_20260510` for final artifacts.

## Session Recovery Discipline

- Codex Windows app recovery check on 2026-05-16 00:47 IST:
  The generated Codex app folder `C:\Users\ADMIN\Documents\Codex\2026-05-16\this-is-my-private-gann-financial` had no `.git` directory or `CURRENT_PROJECT_HANDOFF.md` and refused file creation under `Documents` (`FileNotFoundException` on simple write probes).
  Recovery repo `https://github.com/gouravdamade/gann-financial-astro-research` was cloned successfully to a temp bridge, then the canonical local repo `C:\Users\ADMIN\PycharmProjects` was confirmed present, writable, and clean.
  Initial Codex app checks in the canonical repo: `git status --short` clean; latest commit `950ae29 Add Codex app recovery instructions`; recent log matches the Git State section above.
- Codex Windows app trial note on 2026-05-16:
  user plans to try the OpenAI Codex Windows app because PyCharm keeps losing chat threads.
  Treat GitHub plus this handoff as the durable source of truth so the user can switch between Codex app and PyCharm seamlessly.
  Short paste-in prompt for the Codex app:
  `This is my private Gann / financial astrology USDJPY research workspace. Please start by reading CURRENT_PROJECT_HANDOFF.md, then run git status --short and git log --oneline -8. The GitHub recovery repo is https://github.com/gouravdamade/gann-financial-astro-research. Keep CURRENT_PROJECT_HANDOFF.md updated after meaningful work, create a timestamped chat_session_backups backup, commit changes, and push to origin/master so I can switch between Codex app and PyCharm without losing state.`
  If the app starts outside this folder, open or clone `C:\Users\ADMIN\PycharmProjects` or the GitHub repo.
- GitHub recovery preparation on 2026-05-16:
  local git user email and connected GitHub account are `gourav.damade@gmail.com`; GitHub username is `gouravdamade`.
  Private GitHub recovery repo:
  `https://github.com/gouravdamade/gann-financial-astro-research`
  Local remote:
  `origin https://github.com/gouravdamade/gann-financial-astro-research.git`
  Initial recovery package was pushed to branch `master` on 2026-05-16.
  `README.md` was added with the resume prompt, key files, common commands, and privacy note.
  The workspace is prepared as a private GitHub recovery repo with core scripts, handoff, source notes, current curated data files, annotation SQLite database, and latest curated chat/session backup.
- Update this handoff after each meaningful work session, especially after long-running builds, generated artifacts, failed rebuild attempts, or chat/session recovery work.
- Codex in-app browser chart recovery on 2026-05-16 03:26 IST:
  `http://localhost:8765/aspect_review_case_11_chart.html` was showing `This site can't be reached` because no local server was listening on port `8765`; the chart file itself existed at
  `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548\aspect_review_case_11_chart.html`.
  Started a hidden Python static server with PID `11220`:
  `python -m http.server 8765 --bind 127.0.0.1 --directory C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`
  Verified the in-app browser loads both `http://127.0.0.1:8765/aspect_review_case_11_chart.html` and `http://localhost:8765/aspect_review_case_11_chart.html`; DOM includes `Repeatation Marker UI`.
  Searched for obvious `debug=True` / `debug: true` flags in the repo and found no matching debug mode flag. The issue was server availability, not debug mode.
- Repeatation marker UI correction on 2026-05-16 03:43 IST:
  User flagged that the marker panel covered too much chart area and that placed markers should look like crosshairs, not full-height vertical lines.
  `build_repeatation_review_pack.py` now injects a compact collapsed `Markers` drawer by default, with `Open` / `Hide` toggle controls, and renders trade/ignore placements as small time/price crosshair targets with a ring plus short horizontal/vertical strokes.
  The current served pack at `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548` was refreshed in place for all 18 chart HTML files; reload `http://localhost:8765/aspect_review_case_11_chart.html` to see it.
  Browser verification: the chart loads, drawer is collapsed by default, `Open` expands it, `Hide` collapses it, and a click on the chart places a compact green crosshair.
- Price coverage correction on 2026-05-16 03:54 IST:
  User noticed case `11` showed no candles near the selected March 7 event and candles only around March 10. This was not a non-trading-day issue: March 7, 2025 was a Friday, but the M30 price file `usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet` starts at `2025-03-10 05:30 IST`.
  `usd_jpy_h1_mt5_metaquotes_demo_full.parquet` covers the case window (`2010-01-27` through `2026-03-10`), so `build_repeatation_review_pack.py` now checks price coverage and falls back from M30 to H1 when M30 does not cover a case window/chart context.
  Regenerated the current served repeatation pack in place. `aspect_review_case_11_chart.html` now uses H1 candles around March 4-10, and `repeatation_marker_template.csv` uses `price_timeframe=h1` for case `11` annotation commands/statistics instead of invalid M30 nearest-bar snapping.
- Localhost server recovery on 2026-05-16 16:32 IST:
  User again saw `ERR_CONNECTION_REFUSED` on `http://localhost:8765/aspect_review_case_11_chart.html`; no process was listening on port `8765`, while the chart file still existed. Restarted a hidden Python static server for the case 11 repeatation pack with PID `13112` and verified HTTP 200 plus browser rendering in a fresh in-app tab.
  Added `serve_repeatation_pack.py` as a durable helper. Run `python serve_repeatation_pack.py` from `C:\Users\ADMIN\PycharmProjects` to serve the default case 11 pack at `http://localhost:8765/aspect_review_case_11_chart.html`.
- Repeatation draft autosave on 2026-05-16 16:43 IST:
  `build_repeatation_review_pack.py` marker UI now autosaves in-progress marker drafts to browser `localStorage` per `case_id` / price timeframe. It saves marker points, active tool, drawer state, outcome, note type, and note text on edits, every 2 seconds while there is draft content, and on `beforeunload`; drafts restore after reload/server restart as long as browser local site data remains. The drawer shows autosave/restored status and has `Clear saved draft` to remove both localStorage and visible draft fields.
  Refreshed the currently served case 11 repeatation chart HTML files in place and verified note + trade-start marker restore after reload; verified `Clear saved draft` removes the test draft and it does not return.
- Repeatation navigation on 2026-05-16 16:55 IST:
  Added `Previous`, `Next`, and `All` soft navigation to each marker drawer. The generator also writes `repeatation_reviewer.html`, a single reviewer shell with a left-side list of all repeatations and an embedded chart frame, so review can proceed from one stable page rather than manually opening individual recurrence files. Verified in the in-app browser that `Next` moves from case `11` to case `44` inside the reviewer flow.
  `serve_repeatation_pack.py` now prints both `http://localhost:8765/repeatation_reviewer.html` and the direct case 11 chart URL.
- Repeatation ignore-trade marker on 2026-05-16 17:53 IST:
  User identified a nearby aspect/event contaminating the case under review and requested a quick whole-trade ignore action. `build_repeatation_review_pack.py` now adds an `Ignore Trade` soft button under the marker controls. It marks the full case window as an ignore region, sets a default `ignore_trade_nearby_event` ML note only when the note is empty, autosaves/restores `trade_ignored`, includes it in downloaded marker JSON, and labels the generated command as `Ignore trade`.
  Refreshed the currently served pack at `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548` in place for all 18 chart HTML files and synced the tracked recovery index. Browser verification: `http://localhost:8765/repeatation_reviewer.html` loads, the marker drawer opens, and `Ignore Trade` appears without disturbing the restored draft.
- Repeatation cursor recovery on 2026-05-16 18:08 IST:
  User reported that Codex in-app browser annotation mode can leave a custom annotation cursor stuck after disabling annotations, forcing chart refresh. This appears likely to be outside the chart page itself, but the marker UI now includes a `Reset Cursor` soft button that clears page/Plotly inline cursor styles, clears browser text selection, blurs non-panel active elements, and updates the drawer status without reloading. The `Ignore Trade` command now also requires a non-empty why-note when the whole trade is marked ignored, so ML/script review keeps the contamination reason.
  Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files and synced the tracked recovery index. Browser verification: `Ignore Trade` and `Reset Cursor` are visible in the drawer, and clicking `Reset Cursor` shows `cursor reset without reloading`.
- Repeatation ML annotation ledger on 2026-05-16 18:29 IST:
  User clarified the goal: the UI should feed ML from what the reviewer sees, including multiple ignore signals and rule notes. `build_repeatation_review_pack.py` marker UI now has a first structured annotation ledger. It supports multiple `ignore_signal` entries and `rule_note` entries, each with scope, type, note type, note text, case/aspect metadata, price timeframe, timestamp, and marker context (`last_point`, trade markers, ignore markers, case window, `trade_ignored`). Entries autosave in browser localStorage as `ml_annotations`, restore after reload, can be removed individually, can be cleared with `Clear ML Notes`, and are included in downloaded marker JSON.
  Added UI controls: `Ignore signal type`, `Rule scope / type`, `Add Ignore Signal`, `Add Rule Note`, and `ML annotation ledger`. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files and synced the tracked recovery index. Browser verification: all new controls are present in `http://localhost:8765/repeatation_reviewer.html` without adding test annotations to the user's active draft.
- Repeatation ignore-signal definitions on 2026-05-18 20:25 IST:
  User requested multiple ignore signal selections and explicit definitions so ML/script learning does not hallucinate from vague labels. `build_repeatation_review_pack.py` now replaces the old single ignore-signal dropdown with multi-select soft buttons. Selecting ignore signal types automatically writes pointwise human-readable definitions into `Notes / why` with underscores converted to spaces. The downloaded JSON now includes `selected_ignore_types` and `annotation_definitions` for ignore signal types, rule scopes, and rule types; each ignore annotation also stores `types`, `type_definitions`, and `scope_definition`.
  Added definitions for `ignore_trade_nearby_event`, `ignore_trade_event_too_short`, `nearby_aspect`, `overlapping_aspect`, `crowded_regime`, `bad_price_data`, `abnormal_candle`, `session_gap`, `no_clear_reaction`, and `manual_skip`, plus definitions for rule scopes and rule types. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files. Browser verification: ignore signal soft buttons render, `ignore trade event too short` is present, definition box is present, and the old single-select dropdown is gone.
- Repeatation ignore-note cleanup on 2026-05-18 21:08 IST:
  User noticed the old legacy `ignore trade: nearby/overlapping aspect/event contaminates case behavior` phrase could appear twice in `Notes / why` after the new ignore-signal definition block was added. `build_repeatation_review_pack.py` now strips that legacy default phrase whenever ignore-signal notes are rebuilt and also migrates restored drafts by calling the cleanup after `selected_ignore_types` are loaded. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files. Browser verification after reload: duplicate legacy phrase count in the note field was `0`.
- Repeatation trade marker visibility on 2026-05-19 20:09 IST:
  User reported that placed trade start/end markers were not clear/readable enough and asked about always-on hover/callout details. `build_repeatation_review_pack.py` now renders trade start/end markers more prominently than ignore markers: wider crosshair strokes, a larger translucent halo, a filled colored core with white border, and always-visible Plotly arrow callouts labeled `Trade start` / `Trade end` with timestamp and price from `fmtPoint`. Marker annotations are managed alongside marker shapes and filtered by `repeatation-marker*` names so chart-native annotations remain intact. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files.
- Repeatation hover translucency on 2026-05-19 20:43 IST:
  User reported chart hover text was blocking candles while placing markers. `sr_touch_lazy_dashboard.py` now uses a more translucent Plotly hover label background (`rgba(11, 6, 81, 0.42)`). `build_repeatation_review_pack.py` also injects CSS for already-exported charts to make `.hoverlayer .hovertext` backgrounds/strokes translucent while keeping text readable, and trade marker arrow-callout backgrounds were softened from 0.96 to 0.68 alpha. Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files. Browser verification: chart frame contains the hover translucency CSS.
- Repeatation reviewer cache-busting on 2026-05-19 21:02 IST:
  User observed the marker-arrow / hover-translucency tweaks appeared limited to the first two repeatations. Disk inspection showed all 18 served chart HTML files already contained the current marker script, trade marker arrow/callout settings, hover translucency CSS, and reviewer links; the issue was likely stale in-app-browser iframe caching for later chart pages. `build_repeatation_review_pack.py` now uses `REPEATATION_UI_VERSION = "repeatation_ui_20260519_hover_v2"` and appends `?v=...` to chart/reviewer HTML links (`Previous`, `Next`, `All`, index links, reviewer sidebar links, and iframe `src`). `serve_repeatation_pack.py` now uses a `NoCacheRequestHandler` with `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`, `Pragma: no-cache`, and `Expires: 0`.
  Refreshed the served case 11 repeatation pack in place for all 18 chart HTML files and synced the tracked reviewer/index files. Restarted the localhost server on port `8765` with PID `23420`. Verification: `Invoke-WebRequest` on `http://localhost:8765/repeatation_reviewer.html?v=repeatation_ui_20260519_hover_v2` returns HTTP `200` and no-cache headers; all 18 chart HTML files pass checks for `repeatation-marker-ui-script`, `.hoverlayer .hovertext path`, `showarrow: true`, `arrowwidth: 2.5`, and the cache version. Browser verification on later direct chart `aspect_review_case_120_chart.html?v=repeatation_ui_20260519_hover_v2` showed case 120 has the current marker UI, ignore chips, trade labels, and translucent hover CSS.
- Repeatation adopted chart marker selection on 2026-05-19 21:19 IST:
  User pointed out that pre-existing chart touch/interaction markers are often already perfectly positioned for review start/end and should be reused instead of covered by heavy hardcoded review markers. `build_repeatation_review_pack.py` now treats clicked Plotly marker traces (`Interactions`, `Selected case touches`, and other marker/touch/interaction traces) as `source='chart_marker'`, preserving `traceName`, `curveNumber`, `pointNumber`, and a compact `markerLabel` in drafts/downloads. For adopted chart markers, the review overlay now draws only a soft glow/ring around the original marker and suppresses the large trade arrow callout; blank/candle clicks still use the crosshair and callout fallback.
  Cache key advanced to `repeatation_ui_20260519_marker_adopt_v3`; refreshed the served case 11 repeatation pack in place for all 18 chart HTML files and synced tracked reviewer/index files. Verification: all 18 served chart HTML files contain `chart_marker`, `adopted-marker-glow`, and the v3 cache key. Browser verification on case `120` confirmed the v3 script/link set is present; a background test click was cleared immediately via `Clear saved draft`.
- Repeatation marker magnet / compact fallback on 2026-05-19 21:31 IST:
  User clarified that when a hardcoded chart marker is present near the desired start/end, the UI should simply light that existing marker rather than drawing a green trade line/callout; where no hardcoded marker exists, the fallback should be a small crosshair, not a vertical-looking line. `build_repeatation_review_pack.py` now uses a 34px nearest-marker magnet around clicks, so nearby `Interactions` / `Selected case touches` points are adopted even when the click is slightly off the Plotly point. Trade start/end callout annotations are suppressed; the chart keeps only a compact ring/glow for adopted points or a short plus-style crosshair for fallback clicks, while exact time/price remains in the drawer and downloaded JSON.
  Cache key advanced to `repeatation_ui_20260519_marker_magnet_v4`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain `nearestChartMarker`, `adopted-marker-glow`, and v4 cache key, and no served chart contains the old `tradeLabel(state.tradeStart...)` callout invocation. Browser case `120` loaded v4 and visually showed ring/glow markers without the big trade callout. Do not clear the browser draft after this check because it may contain the user's active review markers.
- Repeatation marker capture / drag adjustment on 2026-05-19 21:48 IST:
  User reported that shaded aspect/regime windows could still get selected while trying to place a close-trade marker at aspect start, and requested draggable adjustment plus thinner crosshairs for precise wick placement. `build_repeatation_review_pack.py` now captures chart `mousedown`/`mouseup` before Plotly shaded-region click handlers, places markers on mouseup, and uses the normal click event only as a suppressor, so shaded areas should not steal marker placement. Manually placed review markers can be dragged by grabbing near the small marker; during drag the marker magnet is disabled, allowing fine adjustment to candle upper/lower wicks. Crosshair/glow strokes were thinned substantially.
  Cache key advanced to `repeatation_ui_20260519_marker_capture_v6`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain `pendingMarkerClick`, `pointFromMouseAt(evt, false)`, and v6 cache key, with no old trade-start callout invocation. Browser case `120` loaded v6 and confirmed capture/drag/thin-crosshair script paths are present.
- Repeatation one-shot marker tool disarm on 2026-05-19 22:20 IST:
  User observed that when a marker tool such as `Trade end` remains active, Plotly built-in controls like zoom/pan can get intercepted and place a marker at the modebar click location. `build_repeatation_review_pack.py` now starts with no marker tool armed, restores drafts with no active marker tool, lets marker tool buttons toggle on/off, disarms automatically after each marker placement, and disarms on `Clear markers`, `Clear saved draft`, and `Ignore Trade`. Marker capture now only starts when a manual marker is being dragged or a marker tool is explicitly armed; Plotly modebar/buttons/inputs/links are explicitly bypassed by marker capture.
  Cache key advanced to `repeatation_ui_20260519_tool_disarm_v7`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain `isPanelOrPlotlyControl`, `suppressNextClick`, and v7 cache key, with no default `setTool('trade_start', false)` or old trade-start callout invocation. Browser case `120` loaded v7 with zero active marker buttons on initial load.
- Repeatation plus markers and restored callouts on 2026-05-20 22:23 IST:
  User noted that always-on callouts were gone and requested start/stop/etc markers shaped like a `+` sign. `build_repeatation_review_pack.py` now restores small translucent always-on marker callouts for `Start`, `End`, `Ignore start`, and `Ignore end`, while keeping labels lighter than the original large callouts. Placed review markers now render as thin `+` shapes (`plus-v` / `plus-h`) instead of ring/circle-heavy targets; adopted hardcoded chart markers get a slightly larger subtle plus/glow so the original chart marker remains visible.
  Cache key advanced to `repeatation_ui_20260520_plus_callouts_v8`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain v8, `function plusShape`, `markerLabel(state.tradeStart, 'Start'...)`, and `markerLabel(state.tradeEnd, 'End'...)`; browser case `120` loaded v8 and confirmed plus/callout script paths are present without placing or clearing markers.
- Repeatation trade color, pan default, and live P/L on 2026-05-20 22:42 IST:
  User requested trade start/end markers and callouts use colors other than candlestick red/green, Plotly Pan should be the default selected tool, and the UI should calculate profit/loss once bullish/bearish plus start/end markers are selected. `build_repeatation_review_pack.py` now uses cyan for trade start, amber for trade end, violet for ignore markers, and a purple translucent trade-result callout. It sets Plotly `dragmode` to `pan` on load, adds an always-visible `Live trade result` panel block, adds a small chart callout when both trade markers exist, recalculates signed pips when marker points move or outcome changes, and includes `trade_profit` in downloaded marker JSON.
  Cache key advanced to `repeatation_ui_20260520_profit_pan_v9`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain v9, pan relayout, `function tradeProfit()`, and cyan/amber marker calls; browser case `120` loaded v9, panel/profit summary exists, cyan/amber/profit script paths are present, and the Plotly Pan modebar button is active.
- Repeatation P/L callout relocation on 2026-05-20 22:54 IST:
  User noted that the P/L callout should not sit directly above the aspect under review. `build_repeatation_review_pack.py` now anchors `repeatation-marker-profit-label` to a fixed chart-corner paper coordinate (`xref='paper'`, `yref='paper'`, `x=0.012`, `y=0.975`) with `showarrow=false`, so the live trade-result label no longer follows the midpoint between trade start/end markers. The drawer `Live trade result` block is unchanged.
  Cache key advanced to `repeatation_ui_20260520_profit_corner_v10`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain v10, paper-anchored P/L label code, and `showarrow: false`; browser case `120` loaded v10 with Pan active and the marker panel present.
- Repeatation auto-suggested trade markers on 2026-05-20 23:18 IST:
  User wanted a first automatic start/end suggestion based on hardcoded chart markers: start at the first selected-case touch marker (red outlined marker) and end at the next subsequent hardcoded marker, while treating manual movement as a rule-worthy override. `build_repeatation_review_pack.py` now adds an `Auto Suggest` soft button and summary panel. The suggestion scans Plotly hardcoded marker traces, prefers the first `Selected case touches` point for trade start, falls back to the first marker inside the case window, then the first visible marker, and chooses the next later hardcoded marker as trade end. It records confidence (`clean`, `fallback`, `weak`, `incomplete`, or `no marker`), rules used, marker counts, and manual override state in autosave/download JSON as `auto_suggestion`.
  Dragging or replacing an auto-suggested trade start/end marker records `manual_override=true` and lists overridden keys, with a UI reminder to add a Rule Note explaining the adjustment. Cache key advanced to `repeatation_ui_20260520_auto_suggest_v11`; refreshed all 18 served chart HTML files and synced tracked reviewer/index files. Verification: all 18 files contain v11, `function autoSuggestTrade()`, `collectChartMarkers`, `manual_override`, and the auto-suggest button. Browser case `120` loaded v11, `Auto Suggest` and the summary panel are present, and Plotly Pan remains active. The button was not clicked during verification to avoid overwriting the user's active draft.
- Repeatation special trait / ML hint panel on 2026-05-20 23:53 IST:
  User asked to compare a unique case_id family and repeatations using existing Vedic/astro features, then highlight special characteristics usable as ML hints. `build_repeatation_review_pack.py` now builds first-pass `special_traits` for each recurrence from the SR/touch log joined by `source_event_id`. It extracts explainable traits such as `shadbala_tag`, shadbala bucket, touch planets, natal signs/houses, primary transit/natal/aspect, duration bucket, regime active count, TN/base TN score buckets, edge score bucket, and event orb bucket. Traits are compared across the same `pair_key/aspect` repeatation group using full-window bullish pips. Tags include `direction linked`, `rare`, `common`, `only bullish samples`, `only bearish samples`, or `context`; these are associative hints, not causal proof.
  Each chart marker drawer now displays an `ML trait hints` panel from `meta.specialTraits`, and `repeatation_marker_template.csv` now includes `special_trait_summary` and `special_trait_json`. Cache key advanced to `repeatation_ui_20260520_traits_v12`; refreshed all 18 served chart HTML files and synced tracked marker template/reviewer/index files. Verification: all 18 files contain v12, `specialTraits`, `function specialTraitsHtml()`, and `repeatation-special-traits`; HTTP case `120` returns v12 and includes ML trait text; browser case `120` loaded v12 with `traitCount=10`, first trait `edge score low`, and Pan active.
- Repeatation SR break confirmation logic on 2026-05-23 01:00 IST:
  User asked to define "how much below is below" for SR break confirmation and suggested 3% of the SR line. For USDJPY, 3% is far too wide, so `build_repeatation_review_pack.py` now uses an ATR/pip threshold instead: M30 uses `max(5 pips, 0.25 * ATR14)` and H1 uses `max(8 pips, 0.25 * ATR14)`. The new logic requires three steps before treating support/resistance as broken: a candle close beyond the threshold, a retest back near the SR line, and then a continuation candle in the break direction.
  Cache key advanced to `repeatation_ui_20260523_break_confirm_v26`. Auto Suggest now records and displays `break_confirmation` beside SR geometry and rule tracking. For bearish events with SR below entry, the rule still treats the first lower SR as support/target; continuation is only allowed after close-below-threshold, failed retest, and continuation. Bullish events with SR above entry use the mirrored resistance-break logic.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_005731`. Synced the served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current browser URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_break_confirm_v26`.
  Browser verification on case `43`: Auto Suggest displayed `Support break confirmed`, threshold `14.9 pips` from ATR14 `59.6`, break close line `145.730`, and explanation `Close broke below SR by threshold, then retest failed and price continued lower.` The family rule still suggested entry `146.158` to exit `145.879`, bearish `+27.9 pips`; rule tracking showed rule `+27.9 pips` vs old default `+2.2 pips`, difference `+25.8 pips`. `python -m py_compile build_repeatation_review_pack.py` passed.
- Repeatation Gann fan auto overlay on 2026-05-23 01:29 IST:
  User asked to implement Gann fans into the repeatation chart, anchored at the top wick when bearish and bottom wick when bullish around the Auto Suggest start marker. `build_repeatation_review_pack.py` now creates a data-coordinate Gann fan from the auto-start candle: bearish uses the first candle at/after start marker high/top wick; bullish uses the first candle at/after start marker low/bottom wick. The fan is stored in `auto_suggestion.gann_fan` with `anchor`, `anchor_candle`, `anchor_rule`, `timeframe_minutes`, `base_pips_per_candle`, and ratio metadata. The current first scale is `1x1 = 1 pip per candle`, with ratio lines `1x4`, `1x2`, `1x1`, `2x1`, and `4x1`.
  Cache key advanced to `repeatation_ui_20260523_gann_fan_v27`. Fan lines are Plotly shape overlays in chart data units, so zoom/pan changes only the viewport, not the fan math. The 1x1 line is emphasized, and the drawer shows the anchor wick/price plus scale note. Manual trade-start adjustment refreshes the fan anchor and records the existing manual override path.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_012325`. Synced the served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_gann_fan_v27`.
  Chrome/CDP verification on case `43` after clicking Auto Suggest: `shapeCount=6`, shapes were `repeatation-marker-gann-anchor`, `repeatation-marker-gann-1x4`, `repeatation-marker-gann-1x2`, `repeatation-marker-gann-1x1`, `repeatation-marker-gann-2x1`, and `repeatation-marker-gann-4x1`; `annotationCount=1`; no WebGL error. The bearish anchor was top wick `2025-04-04 02:30:00+05:30 @ 146.474`, with anchor candle `open 146.080 / high 146.474 / low 145.959 / close 146.412`.
- Repeatation callout declutter / Gann anchor dot on 2026-05-23 08:17 IST:
  User flagged that the Gann fan label and Start/End labels were fighting each other visually, making candles hard to read, and asked for a prominent dot where the Gann fan is placed. `build_repeatation_review_pack.py` now hides Start/End/Ignore marker callouts when the marker drawer is collapsed; opening the drawer brings the callouts back for inspection. The Gann fan no longer adds a chart text callout; its exact anchor details remain in the Auto Suggest panel and saved `auto_suggestion.gann_fan`.
  Cache key advanced to `repeatation_ui_20260523_gann_fan_v28`. The Gann anchor now draws as a stronger orange filled dot plus pale ring (`repeatation-marker-gann-anchor-dot` and `repeatation-marker-gann-anchor-ring`) while preserving data-coordinate fan lines. The collapsed drawer toggle redraws marker annotations so label clutter appears/disappears immediately.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_081416`. Synced the served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_gann_fan_v28`.
  Chrome/CDP verification on case `8`: after Auto Suggest and collapsing the drawer, `gannDot=true`, `gannRing=true`, `gannShapeCount=7`, repeatation annotations only contained `repeatation-marker-profit-label`, `markerLabelCount=0`, Auto Summary still contained Gann fan details, and no WebGL error was visible. `python -m py_compile build_repeatation_review_pack.py` passed.
- Repeatation Start/End callout spacing on 2026-05-23 08:42 IST:
  User asked to move Start/End callouts farther apart and make their pointer/line segments bolder. `build_repeatation_review_pack.py` now gives trade marker callouts a stronger annotation style when the marker drawer is open: arrowhead `2`, arrowsize `1.15`, arrowwidth `2.4`, borderwidth `1.5`, and font size `11`. Start is offset up-left (`ax=-118`, `ay=-76`) while End is offset down-right (`ax=118`, `ay=54`) so their boxes do not stack around the same candles.
  Cache key advanced to `repeatation_ui_20260523_gann_fan_v29`. Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_084021`. Synced served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_gann_fan_v29`.
  Chrome/CDP verification on case `8` after Auto Suggest with drawer open: Start annotation had `ax=-118`, `ay=-76`, `arrowwidth=2.4`, `arrowsize=1.15`, `arrowhead=2`, `borderwidth=1.5`; End annotation had `ax=118`, `ay=54` with the same strong arrow settings; Gann dot remained present and no WebGL error was visible. `python -m py_compile build_repeatation_review_pack.py` passed.
- Repeatation SR epsilon / confirmed-break target extension on 2026-05-23 09:12 IST:
  User circled back to case `8` and correctly noted that Auto Suggest was closing Start/End too close together even though the first support SR had clearly broken and retested. User also asked for a clear definition of what counts as a marker exactly at SR vs above/below SR. `build_repeatation_review_pack.py` now defines a volatility-aware SR geometry epsilon: `max(1.5 pips, min(5 pips, 0.05 * ATR14))`. Any marker within `+/- epsilon` of the entry/reference is treated as `same_as_entry` / `at SR / use marker flow`; barrier logic only applies outside that band.
  Cache key advanced to `repeatation_ui_20260523_barrier_epsilon_v30`. The bearish family rule now filters lower support targets using the epsilon clearance, records `sr_geometry_epsilon_pips`, and stores `barrier_sr_geometry` separately from the final target geometry. If the first lower support barrier has `break_confirmation.status === confirmed`, Auto Suggest moves the end to the next lower hardcoded SR/marker after the confirmed break/continuation, instead of exiting at the just-broken barrier. The Auto Suggest panel now shows `At-SR band: within +/-X pips uses normal marker flow...` and, when applicable, `First barrier checked`.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_090942`. Synced served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_barrier_epsilon_v30`.
  Chrome/CDP verification on case `8` after Auto Suggest: summary showed `Applied family rule bearish_bias_support_barrier with confirmed support break`, final target `SR is below entry: support/target (-112.6 pips from entry)`, epsilon band `+/-1.5 pips`, first barrier checked `147.650 (-9.5 pips from entry)`, rule tracking `rule +112.6 pips vs old default +53.7 pips | difference +58.9 pips`, and break confirmation `Support break confirmed threshold 8.0 pips (ATR14 30.8) | break close line 147.570`. No WebGL error was visible. Note: bullish mirrored barrier rule is not yet hard-coded as an active family rule; the epsilon/geometry machinery is now ready for it once a bullish case family is reviewed and named.
- Repeatation attribution-boundary stop on 2026-05-23 09:30 IST:
  User pointed out that case `8` should not continue into the March 10 target because the first later marker was also the start of a new aspect/zone; once the trade enters a new zone, attribution to the current case is no longer clean. `build_repeatation_review_pack.py` now adds `attributionBoundaryAfter()`, which finds the first non-selected hardcoded marker after the reviewed case window / first barrier. When a confirmed support break occurs, the bearish family rule now compares the next deeper SR target against this attribution boundary and stops at the boundary if it appears first.
  Cache key advanced to `repeatation_ui_20260523_attribution_boundary_v31`. Auto Suggest now stores `attribution_boundary` and panel text `Attribution boundary stop: ... before next event/zone takes over.` New end rule: `family_rule_next_event_boundary_after_confirmed_support_break`.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_092719`. Synced served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_attribution_boundary_v31`.
  Chrome/CDP verification on case `8` after Auto Suggest: summary showed `Applied family rule bearish_bias_support_barrier with confirmed support break, but the first later hardcoded marker starts another event/zone`, final SR geometry `-63.2 pips from entry`, attribution boundary stop `2025-03-07 23:30:00+05:30 @ 147.113`, rule tracking `rule +63.2 pips vs old default +53.7 pips | difference +9.5 pips`, and the same confirmed support break line `147.570`. No WebGL error was visible.
- Repeatation Gann anchor dot timezone fix on 2026-05-23 09:43 IST:
  User reported that the Gann fan dot looked misplaced and asked to ensure it is placed at the exact wick tip/bottom. Investigation showed the fan line used the correct anchor (`2025-03-07T19:30:00+05:30 @ 147.852` for bearish case `8`), but the dot/ring helper used `Date.toISOString()` for x0/x1, converting the surrounding circle bounds to UTC `Z` strings and visually shifting the dot left on the Plotly date axis.
  Cache key advanced to `repeatation_ui_20260523_gann_anchor_fix_v32`. `build_repeatation_review_pack.py` now uses `chartIsoFromMs()` inside `xAround()` and Gann fan line end generation so overlay shapes preserve `+05:30` chart coordinates. This also benefits other small marker/crosshair shapes that rely on `xAround()`.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_094001`. Synced served folder: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260523_gann_anchor_fix_v32`.
  Chrome/CDP verification on case `8` after Auto Suggest: Gann dot bounds were `2025-03-07T19:01:11.463+05:30` to `2025-03-07T19:58:48.536+05:30`, whose center is `2025-03-07T19:29:59.999+05:30`; dot center price was `147.852`; 1x1 fan line start was `2025-03-07T19:30:00+05:30 @ 147.852`; no WebGL error was visible. `python -m py_compile build_repeatation_review_pack.py` passed.
- Case 8 ML learning note on 2026-05-23 09:52 IST:
  User asked to generate ML notes for case `8`. Added a dedicated SQLite rule note in `C:\Users\ADMIN\PycharmProjects\gann_aspect_annotations.sqlite`: `note_id=3`, `case_id=8`, `note_type=ml_case_review_note`.
  Structured header fields include: `scope=case_family/local`, `status=provisional_until_all_repeatations_reviewed`, `type=ml_feature_hint`, `rule_label=bearish_confirmed_support_break_attribution_boundary`, `linked_rule=bearish_bias_support_barrier`, `seed_case_id=8`, `family=AVG(ALL)|MOON::square`, `direction=bearish`, and `ml_label=confirmed_support_break_but_stop_at_next_event_boundary`.
  The note captures the reviewed behavior: case `8` is a bearish continuation after first support breaks, but trade attribution should stop at the next hardcoded event marker (`2025-03-07 23:30:00+05:30 @ 147.113`) because KETU|MOON opposition and MOON|RAHU conjunction begin there. It records Gann fan anchor at exact top wick `147.852`, first support barrier `147.650`, break threshold `8.0 pips`, break close line `147.570`, confirmed break/retest/continuation, and rule result `+63.2 pips` vs old default `+53.7 pips`.
  Astro/context reasons captured: strict shadbala avg moderate-above-minimum `384.47`, ratio `1.117`; strict drik bala avg bearish/negative `-7.04` with malefic pressure slightly exceeding benefic support (`+56.00` vs `-63.04`); low/mild chesta `9.11`; BPHS-like orb strength `0.0` and event_orb_deg `51.36`, so learn this as regime/family + SR/Gann geometry rather than exact-aspect-only; active regime count `2`, requiring attribution control; Moon has supportive dignity clues, so actual support-break confirmation is required before continuation.
  Rebuilt case 8 repeatation pack `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_8_avg_all_moon_square_20260523_094914` and synced it into the served folder. Verification: served `aspect_review_case_8_chart.html` contains `bearish_confirmed_support_break_attribution_boundary`, `confirmed_support_break_but_stop_at_next_event_boundary`, and `seed_case_id=8`.
- Repeatation local ML draft button on 2026-05-23 22:45 IST:
  User asked to proceed with the next step after building the local jyotish/Ollama workflow. `build_repeatation_review_pack.py` now exposes a `Draft ML Reason` soft button inside the marker drawer, below the existing stored `ML Notes` section. The button sends the current `case_id`, Auto Suggest summary, current live P/L if markers are present, and reviewer note text to the localhost server; the returned draft appears in a collapsible `Local Draft ML Reason` block in the drawer. Cache key advanced to `repeatation_ui_20260523_draft_ml_reason_v34`.
  `serve_repeatation_pack.py` now has a local JSON endpoint `POST /api/draft_ml_reason`. It runs `jyotish_agent\explain_case.py --case-id <case_id> --question <drawer-context>` from the project root, reads the generated `jyotish_agent\case_explanations\case_<id>_jyotish_explanation.md`, and returns the Markdown to the chart. This uses local Ollama/RAG only; no OpenAI API key is used.
  Rebuilt case 43 repeatation pack `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260523_222826` and synced it into the served folder `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current server is running on `127.0.0.1:8765` as PID `18996`. Open `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_draft_ml_reason_v34`.
  Verification: `python -m py_compile build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\explain_case.py` passed. HTTP fetch of the live case 43 chart contains `Draft ML Reason`, `api/draft_ml_reason`, `repeatation-ml-draft`, and `draftMlReason`. Direct API smoke test returned `ok=true` for case `43` and produced deterministic evidence first, followed by the local LLM commentary warning/draft. Browser automation through the node REPL Playwright path was unavailable because that environment could not resolve `playwright-core`, so verification used static live-HTML checks plus direct localhost API checks.
- Repeatation ML draft evidence alignment on 2026-05-23 22:58 IST:
  User pasted the case `43` local draft and it showed two quality problems: the deterministic section did not fully use the Auto Suggest evidence (`Support break confirmed`, attribution boundary, rule-vs-default), and the local Qwen commentary drifted into wrong `bullish bias` language despite the bearish case evidence. `build_repeatation_review_pack.py` now sends the full Auto Suggest JSON to the local agent instead of truncating it at 1800 characters. Cache key advanced to `repeatation_ui_20260523_draft_ml_reason_v35`.
  `jyotish_agent\explain_case.py` now parses the drawer's `Auto Suggest summary` JSON and `Current manual/auto trade result` from the question text, then prints them as deterministic UI/rule evidence: confidence, applied family rule, final SR geometry, first barrier checked, break confirmation threshold/line, attribution boundary marker, rule-vs-default pips, and current marker result. The deterministic heading now changes correctly: when `break_confirmation.status == confirmed`, it says the bearish family rule can continue after support breaks while still stopping at the next attribution boundary, instead of saying the case did not cleanly break support.
  The local LLM drift guard now treats `bullish bias` as a conflict when the evidence says `ret_after_72h_dir=DOWN` or the local rule notes say `direction=bearish`. If drift is detected, the draft omits the local LLM prose and keeps only deterministic analysis plus retrieved local notes. Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260523_225028`; synced it into the served folder. Current URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260523_draft_ml_reason_v35`.
  Verification: `python -m py_compile build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\explain_case.py` passed. Live HTML contains v35, `Draft ML Reason`, and `api/draft_ml_reason`. Direct API smoke test for case `43` with valid Auto Suggest JSON returned deterministic lines for `Support break confirmed`, final SR geometry `-30.1 pips`, attribution boundary `MOON|RAHU | conjunction_orb`, and rule tracking `rule +30.1 pips vs default +2.2 pips; delta +27.9 pips`; the bad LLM section was replaced with `Omitted`.
- Repeatation global exit and SR-line touch detection on 2026-05-25 01:35 IST:
  User reviewing case `103` noted the close marker should be placed at exact SR touch (Neptune line), or at a validated Gann fan reaction, and asked for a global rule to close at the first clean boundary: SR touch, next shaded zone, or hardcoded marker. `build_repeatation_review_pack.py` now implements that global exit rule for the active bearish family-rule flow. Auto Suggest collects shaded-zone starts, hardcoded markers, and SR-line touches; it chooses the earliest deterministic boundary after entry. SR line touches are detected even when there is no explicit hardcoded marker dot, by parsing the embedded Plotly trace JSON and decoding Plotly's compact float64 arrays with a plain-JS fallback decoder.
  Cache key advanced to `repeatation_ui_20260525_global_exit_v37`. The marker drawer now reports the selected global exit boundary and notes when SR-line touches were detected without hardcoded dots. Gann fan remains a visible/recorded evidence layer, but automatic fan-line exits are not hard-coded yet because the exact ratio/confirmation rule still needs review.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260525_013145`; synced it into the served folder `D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current verified URL: `http://127.0.0.1:8765/aspect_review_case_103_chart.html?v=repeatation_ui_20260525_global_exit_v37`.
  Browser verification on case `103` after Clear markers + Auto Suggest: Auto Suggest chose `Global exit chosen: 2025-05-16 09:00:00+05:30 @ 145.215`, reported `SR line touches detected: 2 candidate(s)`, break confirmation `Support break confirmed threshold 7.4 pips (ATR14 29.5) | break close line 145.141`, trade start `2025-05-15 22:30 @ 145.792`, trade end `2025-05-16 09:00 @ 145.215`, and live result bearish `+57.7 pips`. `python -m py_compile build_repeatation_review_pack.py` passed.
- Repeatation deterministic reason verifier on 2026-05-26 21:22 IST:
  User asked how to know whether the local LLM `Draft ML Reason` and saved ML notes are correct, especially because `BPHS-like orb strength for AVG(ALL)|MOON square is 0.0` kept appearing. `build_repeatation_review_pack.py` now adds a drawer section `Reason verifier`, a rule-based truth gate that checks the local draft plus saved ML notes against current deterministic evidence: Auto Suggest, live P/L, SR geometry, break confirmation, attribution/global-exit boundary, SR-line touch candidates, and doctrine caveats. Verdicts are `verified`, `partly verified`, or `contradiction found`; issue severities include `contradiction`, `missing`, `unsupported`, `caution`, and `info`.
  Cache key advanced to `repeatation_ui_20260526_reason_verifier_v38`. The verifier intentionally is not another creative LLM. It flags stale or conflicting notes before ML training. It specifically treats synthetic `AVG(ALL)` plus `square` BPHS-like orb `0.0` as a caution/not-applicable style clue, not a real doctrinal zero.
  `jyotish_agent\explain_case.py` now writes `event_bphs_like_orb_strength=not_applicable_for_synthetic_AVG_ALL_square (raw=...)` in deterministic evidence for synthetic AVG(ALL)/square cases, and deterministic analysis says to use `event_orb_deg` plus observed family behavior instead of treating the BPHS-like field as clean doctrine.
  Rebuilt pack: `C:\Users\ADMIN\Desktop\doc\repeatation_review_case_43_avg_all_moon_square_20260526_210948`; synced it into served folder `D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`. Current URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260526_reason_verifier_v38`.
  Verification: `python -m py_compile build_repeatation_review_pack.py jyotish_agent\explain_case.py serve_repeatation_pack.py` passed. Static HTML contains v38 and `repeatation-ml-verifier`. Browser case `43` showed the verifier and BPHS caution. After switching from plain `http.server` to `serve_repeatation_pack.py`, the `Draft ML Reason` API returned successfully. With Auto Suggest present, the verifier correctly flagged `contradiction found` because older saved ML note text says support did not break, while current Auto Suggest evidence says support break/retest/continuation is confirmed; this is expected and useful, because it prevents stale notes from silently entering ML training.
- Case 43 contradiction correction on 2026-05-26 21:50 IST:
  The verifier's first real contradiction was corrected. SQLite `rule_notes.note_id=2` for case `43` was updated in `gann_aspect_annotations.sqlite` from the stale `astro_reason_not_strong_enough_to_break_support` wording to `astro_reason_confirmed_support_break_but_exit_first_boundary`. The corrected note now says v38 Auto Suggest classifies case `43` as confirmed support-break behavior with global first-boundary exit, while preserving the caution that Shadbala/Drik/Chesta are not unlimited-force signals.
  `build_repeatation_review_pack.py` verifier logic was also tightened so the family rule phrase `do not chase continuation ... without break confirmation` is treated as a cautionary rule requirement, not as a contradiction when break confirmation is actually present.
  Rebuilt/synced served case-family HTML, then patched generated served HTML with the corrected verifier condition after one long export timed out before all generated files reflected the source change. Browser verification on case `43` after Clear Draft + Auto Suggest + Draft ML Reason: verifier verdict changed from `contradiction found` to `partly verified`; no contradiction remains. The remaining `partly verified` status is only the intentional BPHS synthetic-field caution. Current URL: `http://127.0.0.1:8765/aspect_review_case_43_chart.html?v=repeatation_ui_20260526_reason_verifier_v38`.
- Repeatation Dream Review agent on 2026-05-26 22:25 IST:
  User wanted a low-credit/local "dreaming" style reviewer that activates when `Draft ML Reason` is clicked, checks the local LLM output, corrects deterministic contradictions where safe, and reports what was corrected. Added `jyotish_agent\dream_review_agent.py` plus `POST /api/dream_review` in `serve_repeatation_pack.py`. The marker drawer now calls Dream Review automatically after a successful local draft and displays a `Dream Review` section between `Reason verifier` and `Local Draft ML Reason`.
  Cache key advanced to `repeatation_ui_20260526_dream_review_v39`. Dream Review receives the in-browser verifier report, Auto Suggest evidence, current trade result, reviewer note, and stored ML notes. It applies only narrow deterministic corrections: currently stale saved ML notes that say a support/resistance break failed when the current verifier evidence says break/retest/continuation is confirmed. Direction conflicts, SR-geometry conflicts, and ambiguous items are queued for Codex/human review instead of auto-mutating. Reports are written locally under `jyotish_agent\dream_review_reports\`; queue/correction JSONL files are ignored by git.
  Rebuilt pack: `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260526_221910`. Current server is API-aware `serve_repeatation_pack.py` on `127.0.0.1:8765` PID `11356`. Open `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260526_dream_review_v39&fresh=dream`. Browser smoke test on case `8`: `Auto Suggest` + `Draft ML Reason` produced local draft ready, verifier `partly verified` due only to BPHS synthetic-field caution, and Dream Review returned `caution_only` with report `D:\PycharmProjects\jyotish_agent\dream_review_reports\case_8_20260526_222453_dream_review.md`. No auto-correction was needed.
- Confirmed-break exit precedence fix on 2026-05-26 22:50 IST:
  User noticed case `8` was closing at the first SR touch even though the same Auto Suggest panel also said support break/retest/continuation was confirmed. Root cause: v39 global exit picked the earliest deterministic boundary after entry among first SR touch, next shaded zone, and next hardcoded marker; for case `8`, the starting candle touched the lower SR at `147.650`, so that SR won even though it should be treated as a broken barrier after confirmation.
  `build_repeatation_review_pack.py` now treats a confirmed first-barrier break as a passed barrier, not as the exit. If `break_confirmation.status === confirmed`, Auto Suggest skips that first SR touch and closes at the earliest later context boundary, with next shaded-zone boundary preferred when it ties a hardcoded marker timestamp. Cache key advanced to `repeatation_ui_20260526_confirmed_break_exit_v40`. The new reasons are `confirmed_break_next_shaded_zone_boundary` and `confirmed_break_next_hardcoded_marker_boundary`.
  Rebuilt pack: `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260526_224742`. Server restarted on `127.0.0.1:8765` PID `12916`. Static verification: served case `8` HTML contains v40 and the confirmed-break shaded/hardcoded boundary rules. `python -m py_compile build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\dream_review_agent.py jyotish_agent\explain_case.py` passed. Case `8` vs case `43` astro comparison from the touch log: case 8 has slightly stronger total strength (`384.47`, ratio `1.117`) and negative Drik pressure (`-7.04`, malefic `-63.04` stronger than benefic `+56.00`), Moon in 8th/difficult house, PLUTO/NEPTUNE rare bearish clues, and active regime count `2`; case 43 has similar total strength (`383.10`, ratio `1.093`) but positive/supportive Drik (`+8.30`, benefic `+66.20` stronger than malefic `-57.90`), Moon in 3rd/action house, touched `JUPITER` SR support, and active regime count `1`. These should be treated as ML candidate reasons, not doctrine proof.
- Rule Conflict / Lesson ledger on 2026-05-26 23:20 IST:
  User asked whether the SR-touch-vs-next-boundary conflicts are being logged for ML now, or only after all repeatations are complete. Added a deterministic `rule_lessons` SQLite table in `gann_aspect_annotations.sqlite`, plus `aspect_annotation_store.add_rule_lesson(...)`, so each rule conflict can be saved as a structured training lesson with `case_id`, `family_key`, `conflict_type`, old/new/winner rules, provisional status, astro hints, Auto Suggest evidence, verifier report, and Dream Review report.
  `serve_repeatation_pack.py` now exposes `POST /api/save_rule_lesson`; `build_repeatation_review_pack.py` loads family lessons into every repeatation and adds a drawer section `Rule Conflict Lessons` plus `Save Rule Lesson`. Running Auto Suggest drafts the lesson; pressing Save writes/upserts it into SQLite. Cache key advanced to `repeatation_ui_20260526_rule_lesson_ledger_v41`.
  First real lesson saved as `rule_lessons.lesson_id=1` for case `8`, family `AVG(ALL)|MOON::square`: conflict `sr_touch_exit_vs_confirmed_break_hold`, old rule `close_at_first_sr_touch`, winner `confirmed_break_next_shaded_zone_boundary`. Lesson text records that the first lower SR was touched early, but break/retest/continuation was confirmed, so SR is a passed barrier and exit should move to the next context boundary. Astro hints saved: negative Drik pressure, malefic pressure stronger than benefic, Moon in 8th/difficult house, PLUTO/NEPTUNE rare bearish clues, and active regime count `2`.
  Rebuilt pack: `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260526_231246`. Current server is API-aware `serve_repeatation_pack.py` on `127.0.0.1:8765` PID `11724`. Open `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260526_rule_lesson_ledger_v41&fresh=lessons`. Static/API verification: `python -m py_compile aspect_annotation_store.py build_repeatation_review_pack.py serve_repeatation_pack.py jyotish_agent\dream_review_agent.py jyotish_agent\explain_case.py` passed; `POST /api/save_rule_lesson` returned `lesson_id=1`; served HTML contains v41, `Rule Conflict Lessons`, the saved lesson metadata, and `api/save_rule_lesson`.
- Marker drawer recovery fix on 2026-05-27 02:55 IST:
  User reported the side menu was missing on v41. Diagnosis found two issues in `build_repeatation_review_pack.py`: the marker UI ran once at page-ready and returned if Plotly had not yet added `.js-plotly-plot`, and a nested Auto Suggest ternary had a JavaScript syntax error (`Unexpected token ':'`) that prevented the whole drawer script from parsing. Cache key advanced to `repeatation_ui_20260527_marker_attach_fallback_v43`.
  Fixes: marker UI now waits/polls for the Plotly graph div before attaching, falls back to a no-op `relayout` shim if `window.Plotly` is not exposed in the in-app browser, and the brittle Auto Suggest nested ternary was replaced with explicit `if/else` rule-reason logic. Source compile check passed: `python -m py_compile build_repeatation_review_pack.py`.
  Rebuilt pack partially through the normal builder at `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_024441`, then patched the generated HTML in that folder with the same v43 syntax fix because the first build timed out after writing the files. Server restarted on `127.0.0.1:8765` PID `21516`. Browser verification on `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260527_marker_attach_fallback_v43&fresh=syntaxfix`: `#repeatation-marker-panel` exists, `Open/Hide` works, and the drawer shows Auto Suggest / Rule Conflict Lessons sections again.
- Draft ML Reason local LLM autostart + memory feed on 2026-05-27 16:20 IST:
  User asked whether `Draft ML Reason` can fire the local LLM directly and feed `dream_review_corrections.jsonl` plus `rule_lessons` into the local RAG context every time. `serve_repeatation_pack.py` now checks `http://127.0.0.1:11434/api/tags` before running `jyotish_agent\explain_case.py`; if Ollama is not running and `D:\ollama\app\ollama.exe` exists, it starts `ollama serve` hidden with `OLLAMA_MODELS=D:\ollama\models`, writing logs to `D:\ollama\ollama_stdout.log` and `D:\ollama\ollama_stderr.log`. The `/api/draft_ml_reason` response now includes an `llm_runtime` status object.
  `jyotish_agent\explain_case.py` now loads family/current `rule_lessons` from SQLite and matching rows from `jyotish_agent\dream_review_corrections.jsonl` when present, then injects them into the deterministic case evidence as `Rule conflict lessons / training memory` and `Dream Review corrections / verifier memory`. The LLM prompt treats those sections as high-priority local memory, so future drafts can learn from saved conflicts and Dream Review corrections without the reviewer copy/pasting them.
  Verification: `python -m py_compile serve_repeatation_pack.py jyotish_agent\explain_case.py` passed. Server restarted on `127.0.0.1:8765` PID `14552` serving `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_024441`. Direct `POST /api/draft_ml_reason` for case `8` started Ollama successfully (`llm_runtime.available=true`, `started=true`), found installed model `qwen2.5:3b`, and produced `D:\PycharmProjects\jyotish_agent\case_explanations\case_8_jyotish_explanation.md`. The generated draft includes `Rule conflict lessons / training memory`; `Dream Review corrections` was absent only because no `dream_review_corrections.jsonl` file exists yet. The local LLM did run, but deterministic drift checks omitted its prose for case `8`, keeping the safer deterministic analysis; this is expected until the local model output passes verifier checks.
- At-SR wick-entry Auto Suggest fix on 2026-05-27 17:05 IST:
  User reviewed case `127` and correctly noticed that the visible reaction point was the orange Gann fan bottom-wick anchor, not the flat Auto Suggest start/end at the same hardcoded SR marker. Investigation showed the hardcoded data contains only one selected-case touch for case `127`: `2025-05-28 23:30 @ 145.125`; the marked lower point is generated from candle wick data (`2025-05-28 23:30` M30 low `144.816`) as the Gann fan anchor, so the old marker-only fallback ignored it.
  `build_repeatation_review_pack.py` now adds `wickEntryPointForStart(...)` and uses it in default marker-flow cases where the selected-case marker and next marker are inside the same SR/entry band. The hardcoded marker remains the signal/reference, but the executable trade start becomes the candle wick: bullish uses bottom wick, bearish uses top wick. `autoSuggestedPoint(...)` now preserves non-marker sources instead of overwriting them as `chart_marker`.
  Rebuilt pack: `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260527_034400`. Server restarted on `127.0.0.1:8765` PID `20496`. Current URL: `http://127.0.0.1:8765/aspect_review_case_127_chart.html?v=repeatation_ui_20260527_wick_entry_v45`. Browser verification after Clear markers + Auto Suggest: summary says `Selected-case hardcoded marker is at the SR/entry band, so Auto Suggest used the candle wick as executable entry`; trade start is `2025-05-28 23:30:00+05:30 @ 144.816`; trade end is `2025-05-29 00:30:00+05:30 @ 145.125`; live result is bullish `+30.9 pips`; Gann fan anchor remains bottom wick `144.816`. `python -m py_compile build_repeatation_review_pack.py` passed.
- Create a local chat/session backup after each important response or before ending a session. Include the active rollout JSONL, `state_5.sqlite`, and any relevant `state_5.sqlite-wal` / `state_5.sqlite-shm` files when present.
- Include a copy of `CURRENT_PROJECT_HANDOFF.md`, `astro_feature_inventory_from_pdfs.md`, `astro_feature_inventory_from_pdfs.yaml`, and `financial_astrology_source_notes_2026-03-13.md` in chat/session backups when project context changes.
- Do not rely on PyCharm chat history alone for recovery; use this handoff and timestamped backups as the durable record.

## Recovery Prompt For A New Chat

If starting a new chat, ask the assistant:

```text
Please read C:\Users\ADMIN\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```

## Padmanabhan Gochara + Dasha/Bhukti Timing Evidence (2026-07-10)

- User supplied a photographed first page of `Timing of Events - A Qualitative and Quantitative Study` by **R. A. Padmanabhan** and asked whether its concepts existed in the original USDJPY pipeline, then requested implementation and recovery of the complete article.
- Source recovery findings:
  - Google Books Volume 74 id `5uA5AAAAIAAJ` confirms the title/author and index start page `14`; the issue is reported as January 1985, but only snippet view is available and PDF download is disabled.
  - No lawful downloadable complete copy was found through Google Books, Internet Archive/HathiTrust-focused searches, Astrolearn holdings, or the modern magazine archive.
  - The LinkedIn post that surfaced the scan contains the same single page, not the continuation.
  - Therefore the article has **not** been studied completely. Exact Table 2, later examples, temporal-quality rules, and weights remain unavailable. See `padmanabhan_timing_source_notes.md`.
- Added `padmanabhan_timing_doctrine.py` with source-bounded, deterministic evidence:
  - whole-sign Gochara counted from natal Moon;
  - Phaladeepika 26.2 favorable houses;
  - Phaladeepika 26.3-8 Vedha mappings and Sun/Saturn + Moon/Mercury exemptions;
  - Phaladeepika 26.33-34 exceptional adverse flags;
  - explicit neutral handling of the Mercury-house-4 source conflict;
  - raw Rahu/Ketu houses, excluded from Vedha score because a reliable nodal Vedha table was not recovered;
  - Vimshottari Mahadasha/Antardasha from natal Moon nakshatra;
  - natural-quality and six-Rupa (`360 Virupa`) disposition components;
  - temporal-quality and named Yogakaraka components held at zero with `article_table_missing` status rather than invented;
  - provisional `I_reference=A_gochara+B_dasha_bhukti` and `I_USDJPY=I_USD-I_JPY`.
- Safety locks:
  - `event_padmanabhan_article_complete_flag=0`;
  - `event_padmanabhan_trade_signal_enabled=0`;
  - candidate rows carry `fx_padmanabhan_evidence_only=1`;
  - legacy FX scores, Auto Suggest, and MT5 direction are not changed.
- Pipeline integration:
  - `build_aspect_sr_touch_log.py` computes natal strict-Shadbala totals for both reference charts and writes quote/base/pair timing evidence at event best time.
  - `enrich_touch_log_padmanabhan_timing.py` attaches the same fields to existing touch/switch CSVs while preserving every row and `touch_id`.
  - `build_trade_candidates_from_touches.py` carries evidence-only fields and now returns a stable schema for all-ignore exit batches.
  - `build_repeatation_review_pack.py` exposes the pair index/direction and USD/JPY Dasha lords as plain-language comparison traits.
  - Feature inventories were updated; validation report is `padmanabhan_timing_v1_validation_20260710.md`.
- Local generated artifacts (not committed):
  - `D:\PycharmProjects\aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign_padmanabhan_v1.csv` (656 rows, original touch IDs preserved).
  - `D:\GannFinancialAstro\doc\sr_touch_full_1year_switch_20260521_165758_padmanabhan_v1.csv` (732 rows, 638 unique events, original touch IDs preserved).
  - `D:\PycharmProjects\trade_candidates_aspect_sr_1y_outer_scored_usdjpy_basequote_all_durations_transitsign_padmanabhan_v1.csv/.parquet` (732 rows).
- Verification:
  - `python test_padmanabhan_timing_doctrine.py` passed.
  - `python test_strict_shadbala_doctrine.py` passed.
  - `python -m py_compile` passed for all changed Python modules.
  - PyYAML parsed the updated inventory and found both the source and feature entries.
  - Full 804-event regeneration produced 656 rows and complete pair indices; it was kept in `tmp` because nine touch placements differ from the May canonical build after later touch-engine fixes.
  - Preserved-ID enrichment + candidate rebuild produced zero differences in legacy `touch_id`, signal direction, FX hypotheses, exit action, and signed P/L.
  - Descriptive in-sample check on 638 unique events: 550 non-neutral predictions, 50.0% raw UP/DOWN agreement, with a strong bearish imbalance (473 DOWN vs 77 UP). This confirms the evidence-only decision.
  - `pytest` is not installed in the active Python 3.14 environment; the repository's direct test runners were used successfully.
- Next doctrine work:
  1. Obtain the article pages after page 14 from the user, a library, or another lawful source.
  2. Cross-check Vimshottari boundaries and natal strict-Shadbala totals against an independent trusted calculator.
  3. Recover/define temporal quality and named Yogakaraka rules with citations.
  4. Run deduplicated purged chronological walk-forward tests for A, B, and A+B separately before enabling any signal.
- Current canonical repo is `D:\PycharmProjects`; the old `C:\Users\ADMIN\PycharmProjects` recovery prompt above is historical/stale.

Updated recovery prompt:

```text
Please read D:\PycharmProjects\CURRENT_PROJECT_HANDOFF.md and continue from there. Also inspect git log/status before editing.
```

## Full Corrected-KAS Isolated Experiment (2026-07-11)

- User requested testing the complete Krushna methodology rather than stopping at classical BAV/SAV.
- Expanded only `research_labs/ashtakavarga_validation`; canonical USDJPY/BTC, Auto Suggest, review-agent, ML-note and MT5 code remain untouched and inaccessible from the lab.
- Added corrected KAS engine:
  - `ashtakavarga_lab/kas.py`: all A/B/C/D/E event rotations, corrected Lesson 7 rows, inverse aspects, tied 4:10 transfers, D/E bonuses/exemptions, ranks, direct candidates, Samdharmi relations/restrictions and Lesson 26 result multipliers;
  - `ashtakavarga_lab/dasha.py`: Vimshottari Mahadasha/Antardasha and three equal sectors;
  - `ashtakavarga_lab/kas_evidence.py`: all 12 House B mappings, Rahu/Ketu proxies, Antardasha evidence, Sun sign/nakshatra timing, SAV-196 and Jupiter-Saturn-8 contexts;
  - `ashtakavarga_lab/evaluation.py` / `cli.py`: all-house ablations, expanding chronological folds, horizon gaps, non-overlapping outcomes, circular-shift placebos, Bonferroni correction and 0/1/2/5-basis-point cost sensitivity.
- Added published/corrected Lesson 7 fixture `fixtures/kas_lesson7_marriage_corrected.json`. It reproduces final corrected scores Saturn 32, Sun 31, Mercury 20, Jupiter 18, Venus 16, Moon 11 and Mars 11. All intermediate checked rows pass.
- Added doctrine and result records:
  - `research_labs/ashtakavarga_validation/KAS_METHOD_SPEC.md`;
  - `research_labs/ashtakavarga_validation/FULL_KAS_FIRST_RUN_FINDINGS.md`.
- Full local generated evidence/report (ignored by Git):
  - `outputs/daily_kas_evidence.parquet`: 141,264 profile/house/day rows from 2010-01-27 through 2026-03-09;
  - `reports/kas_lesson7_fixture.json`;
  - `reports/usdjpy_kas_walk_forward.json`.
- First full experiment evaluated 12 House B mappings, 12 feature/timing ablations, 3 horizons and 2 direction mappings: 864 comparisons in one correction family.
- No robust edge passed:
  - minimum Bonferroni p-value `0.2586`;
  - strongest fixed full-method cell was House 2 + first Antardasha sector + Sun gate at one day: 904 observations, 55.42% hit, raw p `0.00112`, adjusted p `0.9645`, circular-shift p `0.13`, median `+0.0383%` gross and `-0.0117%` at 5 bps;
  - simple House 1 Antardasha score was 53.86% over 1,359 observations but had adjusted p `1.0`, placebo p `0.935`, and negative median after 5 bps.
- Verification: 18 unit/isolation tests pass; corrected fixture CLI passes; 141,264-row generation and 12-house evaluation complete.
- Important limits:
  - market run is a Raman adaptation, not exact improved-Krushna-ayanamsa reproduction;
  - no source-defined currency event house exists, therefore all twelve are reported and no best house may be selected from this run;
  - event-specific karaka and delay judgments do not have a defensible currency mapping and remain explicit unresolved evidence rather than invented rules;
  - two outside BAV/SAV calculator checks remain pending.
- Decision at first run: retain as isolated research only; do not promote any KAS output into trade, Auto Suggest, ML-note, rule, marker or MT5 logic. A later user-requested display-only review advisory is documented below.

## Non-Binding KAS Review Suggestion (2026-07-11)

- User requested that the full KAS result still be available as a mere suggestion.
- Added root adapter `krushna_kas_advisory.py`, which reads the isolated corrected-KAS engine and computes a timestamp-specific USD-vs-JPY vote across all twelve House B mappings. It does not choose the best historical house.
- Advisory output includes the all-house bullish/bearish/neutral count, agreement percentage, Sun-timed subset, USD and JPY Dasha/Antardasha sectors, and detailed per-house audit JSON.
- Added mandatory locks: `evidence_only=1`, `trade_signal_enabled=0`, `trade_override_allowed=0`, `auto_suggest_input=0`, `ml_training_input=0`, and `mt5_input=0`.
- `build_repeatation_review_pack.py` now calculates a separate advisory for each recurrence at its own event-best timestamp and renders it in a dedicated `Experimental KAS suggestion` drawer block. It is not added to special-trait ranking, ML notes, Auto Suggest, family rules, markers or candidate scoring.
- Real family smoke check: all 16 AVG(ALL)-Moon-square recurrences received distinct timestamped advisories. Case 8 voted bearish 1/4/7 (bullish/bearish/neutral), while cases 43, 103, 127 and 185 voted 12/0/0 bullish. These contradictions are intentionally visible and cannot override reviewed behavior.
- Added `test_krushna_kas_advisory.py`; three lock/coverage/status tests pass.
- Repeatation UI version: `repeatation_ui_20260711_kas_advisory_v66`.
- Rebuilt the complete 16-case pack at `D:\GannFinancialAstro\doc\repeatation_review_case_8_avg_all_moon_square_20260711_022803`.
- Server restarted on `127.0.0.1:8765` (PID 8520). Verified URL: `http://127.0.0.1:8765/aspect_review_case_8_chart.html?v=repeatation_ui_20260711_kas_advisory_v66`.
- Playwright/Chrome browser verification: advisory block visible, Auto Suggest remains separately present, no page JavaScript errors. Screenshot: `kas_advisory_browser_check.png` in the rebuilt pack.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260711_023554`.

## Krushna Ashtakavarga Source Audit (2026-07-10)

- User supplied the 185-page PDF `Timing of Events: A Research Work in Astrology with Krushna Ashtakvarga System` by Krushna Jugalkalani and requested a thorough read.
- The complete PDF was extracted and key worksheets/diagrams were visually inspected. File SHA-256: `E18E021B84EE3A344EAC4DB11056D68C536B296E9D0CEFCFDBBE1B66455A9711`.
- After hash verification, the source PDF was moved off C: to `D:\GannFinancialAstro\doc\Jyotish_Jugalkalani Krushna_Timing of Events_A Research Work -- Jyotish -- 2021.pdf`; the original Desktop copy was removed in accordance with the project's D:-drive storage policy.
- This is a separate compilation of 36 KAS lessons originally circulated around 2000-2002. It is **not** R. A. Padmanabhan's 1985 article and does not recover Padmanabhan's missing Table 2.
- Durable source audit: `krushna_ashtakavarga_source_review_20260710.md`.
- Useful evidence candidates identified:
  - classical seven-planet BAV/SAV transit values;
  - KAS Lesson 11 seven-planet SAV transit sum centered on `196 = 7 x 28`;
  - Lesson 35 Jupiter-plus-Saturn bindu sum centered on eight;
  - explicit Rahu/Ketu Samdharmi proxies through sign, nakshatra and Navamsa dispositors.
- KAS-specific mechanics identified but quarantined:
  - inverse-aspect rule (`>4` negative, `<4` positive via `8-bindus`, `4` neutral);
  - event-specific A/B/C/D/E house worksheet;
  - 4:10 Samdharmi transfers, D/E +5 bonuses and score-12 threshold;
  - Antardasha third-sector delay and solar fine-timing rules.
- Source-quality findings:
  - modern KAS Lesson 7 explicitly corrects calculations in the supplied original lesson, including tied transfers, exactly-four neutrality and Jupiter/Venus deductions;
  - the PDF contains several internal date/formula/legend errors;
  - claimed ~90% accuracy is unsupported by a published raw dataset, locked predictions or holdout evaluation;
  - many examples are retrospective and create substantial overfitting risk;
  - medical/fertility/sexuality claims are excluded permanently from this financial pipeline.
- Doctrine conflict: source KAS uses a Krushna ayanamsa (and the current site mentions an improved KAS ayanamsa), while the user's project policy prefers Raman. Exact source reproduction and Raman-adapted market experiments must be separately labeled; BAV convention must also be versioned.
- Classical cross-check: Phaladeepika Chapter 23 supports using BAV/SAV bindus to qualify transits, but does not establish the KAS inverse-aspect, event worksheet, bonuses or transfer mechanics.
- Inventory updates added source `KRUSHNA_KAS_TIMING` and four feature records:
  `CLASSICAL_ASHTAKAVARGA_TRANSIT`, `KRUSHNA_DAILY_SAV_INDEX`, `KRUSHNA_JS_TRANSIT_SUM`, and quarantined `KRUSHNA_EVENT_WORKSHEET`.
- No USDJPY/BTC signal, Auto Suggest rule or MT5 execution behavior was changed. Recommended next implementation is a calculator-certified, evidence-only `ashtakavarga_evidence.py` followed by a separately namespaced KAS ablation module only after exact corrected specifications are frozen.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260710_233309`.

## Isolated Ashtakavarga Validation Lab (2026-07-10)

- User requested testing of the Krushna/Ashtakavarga ideas while keeping them separate from the main project.
- Added self-contained tracked lab: `research_labs\ashtakavarga_validation`.
- Isolation guarantees:
  - package imports no main trading modules;
  - all MT5, Auto Suggest, review-agent and LLM integrations are disabled;
  - generated outputs are restricted to the lab's ignored `outputs/` and `reports/` directories;
  - canonical market files are read-only inputs supplied explicitly;
  - nothing can promote itself into the main pipeline.
- Implemented:
  - complete unreduced seven-classical BAV benefic-place tables with Lagna as the eighth contributor;
  - SAV calculation, invariant validation and Raman-adapted Swiss Ephemeris reference profiles;
  - daily seven-planet SAV sum/distance from 196;
  - Jupiter-plus-Saturn own-BAV transit-sign sum/distance from eight;
  - USD, JPY and three explicitly unverified Bitcoin-location reference profiles;
  - expanding chronological evaluation with horizon gap, non-overlapping multi-day samples, Wilson intervals and price-momentum baseline;
  - exact JSON comparison for future outside-calculator BAV/SAV exports;
  - one-command reproduction via `research_labs\ashtakavarga_validation\run_first_usdjpy_test.ps1`.
- Verification:
  - 12 direct unit/isolation tests passed;
  - all 84 BAV cells and 12 SAV cells matched the published B. V. Raman standard-horoscope fixture;
  - expected BAV totals and SAV 337 matched;
  - 250 randomized charts preserved all invariants;
  - certification remains `partial_external_calculators_pending` because 0/2 independent calculators have been checked.
- First isolated USDJPY result (2010-01-27 through 2026-03-09, 4,187 joined trading days):
  - one-day fixed SAV base-minus-quote: 51.32% hit rate, 2,044 non-overlapping observations, 95% Wilson interval 49.15%-53.48%, unadjusted p=0.232;
  - one-day fixed Jupiter-Saturn differential: 49.66%, 1,482 observations, p=0.795;
  - five- and twenty-day variants also had confidence intervals spanning 50%; no simple feature was reliably distinguishable from chance.
- Durable interpretation: arithmetic is internally sound against one published fixture, but predictive evidence is not established. No main USDJPY/BTC/MT5 behavior changed.
- Full lab notes: `research_labs\ashtakavarga_validation\README.md` and `research_labs\ashtakavarga_validation\FIRST_RUN_FINDINGS.md`.
- Next gates: fill two independent calculator exports using `fixtures\external_calculator_template.json`, then add circular-shift placebos and transaction-cost sensitivity before considering more KAS mechanics.
- Recovery backup including lab code and local first-run reports: `D:\PycharmProjects\chat_session_backups\session_20260711_001352`.

## Corrected USDJPY TN Pipeline Foundation (2026-07-11)

- Replaced the recovery-only `JDML4.py` dependency with native generator
  `build_corrected_natal_event_source.py`; `rebuild_dataset_mt5_ipo_allpairs.py` is now a
  compatibility entrypoint only.
- Frozen astronomy contract:
  `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`; generator version:
  `native_tn_event_source_v1_20260711`.
- Generated 1,268 unique transit-to-natal orb windows for 2025-03-01 through 2026-03-10,
  with explicit transit/natal roles and no market-outcome fields in the event source.
- Replaced nearest-candle event mapping with strict contained-candle mapping. The corrected
  touch rebuild has 754 rows and no geometry quarantine.
- Removed the candidate-direction hindsight leak. Candidate direction now defaults to the
  timestamp-available FX hypothesis, observed 72-hour direction is label-only, and trade
  entry defaults to the next available bar open. Corrected result: 607 potential trades,
  231 wins, 375 losses and 148 ignored, so the raw heuristic is not trade-ready.
- Added directional family identity, for example `TN::MOON->MERCURY::trine`; opposite
  transit/natal roles can no longer share notes or rules through the unordered display pair.
- Created `gann_aspect_annotations_raman_v2.sqlite`: schema version 2, 754 cases and 205
  directional families. It intentionally starts with zero annotations/completed reviews.
- Generated a corrected 15-recurrence review pack for `TN::MOON->MERCURY::trine` at
  `D:\GannFinancialAstro\doc\repeatation_review_case_55_mercury_moon_trine_20260711_204603`.
- Browser Auto Suggest now calls `POST /api/auto_suggest`, whose active engine is
  `reviewer_rule_replay.auto_suggest_case` in retrospective-review-only mode. A live API
  smoke check for case 55 returned bullish `+2.3 pips`, from the first selected-window SR
  touch to the next hardcoded attribution boundary.
- Fixed remaining local Jyotish/RAG family reconstruction to preserve directional family
  keys. Also corrected an explanation bug that treated every square aspect as synthetic;
  the BPHS-like non-applicability warning now applies only to `AVG(ALL)`.
- Verification at this checkpoint: `62 passed` via `python -m pytest -q`; corrected API
  endpoint smoke test passed.
- Still pending from the audit roadmap:
  external Shadbala/Drik expected values and certification, purged timestamp-safe live
  inference evaluation, BTC rolling/no-lookahead evidence mode, and removal of the dead
  archived JavaScript Auto Suggest source after visual parity checks.
- New product direction requested after this checkpoint: design a lightweight Windows
  research/live workstation with parameterized astrology charts, TradingView-like drawing
  tools, local LLM evidence/verification, and a supervised always-reconnecting MT5 backend.

## Native Gann Astro Desk Release (2026-07-12)

- The supported user runtime is now a real native Windows application rather than a
  browser URL:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`.
- Release contract:
  - version `0.1.0`;
  - PyInstaller one-folder build using pywebview plus Microsoft WebView2;
  - SHA-256 `CA26CDB4073002531C173C5642E948CF4560ECA8320B3FDE26F191E95EE7B0B1`;
  - 1,656 files / 698,259,121 bytes;
  - astronomy contract `RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2`;
  - MT5 execution remains `read_only_market_data` and `tradeAllowed=false`.
- The release bundles the corrected event/touch sources, H1/M30 price archives,
  annotation seed DB, Swiss Ephemeris files, Python corrected-data workers, Node,
  the Codex SDK bridge, and the compiled frontend. Writable state stays under
  `D:\GannFinancialAstro\app_data`.
- Native behavior verified:
  - main `Gann Astro Desk` WebView2 window is responsive;
  - internal backend uses a private random loopback port, with no localhost URL in
    the user workflow;
  - Codex bridge reports `codex-sdk`;
  - MT5 reconnect supervisor reports connected to MetaQuotes-Demo while preserving
    read-only execution;
  - Analyze Aspect opens as a second native window, not Edge/Chrome;
  - corrected baseline loads 1,268 events and 754 touches;
  - toolbar and parameter drawer were visually checked at Windows display scaling.
- Reproducible D-only packaging lives in
  `gann-astro-desk\packaging\build_windows_exe.ps1` and
  `gann-astro-desk\packaging\gann_astro_desk.spec`.
- Rust/MSVC decision:
  - neither is required for the working pywebview release;
  - Rust can later be installed on D through `RUSTUP_HOME`/`CARGO_HOME`;
  - Visual Studio Build Tools can place most workloads/cache on D, but some shared
    installer and Windows SDK servicing files remain on C;
  - defer both until a signed Tauri/MSI route is intentionally selected.
- Added immutable timestamp-safe MT5 history snapshots:
  - contract `MT5_TIMESTAMPED_CLOSED_BARS_V1`;
  - explicit requested range, capture time and as-of cutoff;
  - only fully closed bars are retained;
  - incomplete bars are counted/excluded;
  - Parquet plus atomic JSON manifest and SHA-256;
  - storage under `D:\GannFinancialAstro\app_data\market_snapshots`;
  - UI command: `Snapshot MT5 range` in Market source parameters.
- Real packaged snapshot verification retained:
  `USDJPY_H1_20260712T081855Z_4cb984b1`, 48 closed H1 bars,
  SHA-256 `8DD95DE8C9AC9814239D0520C819DF3574D3088DEB1B4EB5FB787F2D7CFED65C`.
- Packaged corrected-worker verification exposed and fixed a timestamp edge case:
  an event beginning at 02:01 was incorrectly rejected when its first genuinely
  contained H1 candle began at 02:30. Full-source coverage is now checked before
  cropping, while contained-candle mapping remains strict. The final packaged job
  completed with one event, one SR touch and 22 evidence rows; baseline was restored
  and all temporary verification jobs/artifacts were removed afterward.
- Verification at this checkpoint:
  - `76 passed` for the full Python suite;
  - `5 passed` for frontend tests;
  - Oxlint clean;
  - TypeScript/Vite production build clean;
  - packaged native health, Codex, MT5 snapshot, generation worker and Analyze Aspect
    smoke checks passed.
- Remaining deliberate gates:
  - promote an immutable MT5 history snapshot into a corrected event artifact only
    through an explicit versioned/no-lookahead operation;
  - consolidate retrospective and future live Auto Suggest behavior into one
    timestamp-safe decision engine before enabling any execution path;
  - external Shadbala/Drik certification and purged out-of-sample validation remain
    required;
  - code signing or a Tauri/MSI installer is optional distribution work, not a runtime
    blocker.
- Recovery backup: `D:\PycharmProjects\chat_session_backups\session_20260712_145424_native_windows_exe`.

## Promoted MT5 Research Artifacts (2026-07-12)

- Completed the explicit Snapshot -> Verified Price Source -> Corrected Artifact pipeline in
  Gann Astro Desk. Live MT5 bars cannot become research evidence merely by being visible:
  the user must first capture a closed-bar snapshot, then explicitly verify/promote it, then
  generate a versioned corrected artifact from that immutable source.
- New contracts:
  - capture contract `MT5_TIMESTAMPED_CLOSED_BARS_V1`;
  - promoted-source contract `PROMOTED_MT5_PRICE_SOURCE_V1`;
  - each promotion revalidates path containment, manifest fields, no-lookahead/immutable
    locks, OHLC geometry, timezone-aware unique timestamps, closed-bar cutoff, bar count,
    first/last opens, last close and Parquet SHA-256;
  - generation resolves the source both when queued and in the worker, and refuses to run
    if the queued SHA has changed;
  - artifact activation rechecks the artifact manifest's recorded source SHA.
- Persistent D:-drive registry and files:
  - registry table `app_price_sources` in
    `D:\GannFinancialAstro\app_data\gann_aspect_annotations_raman_v2.sqlite`;
  - promoted archives under `D:\GannFinancialAstro\app_data\price_sources`;
  - immutable source snapshots remain under
    `D:\GannFinancialAstro\app_data\market_snapshots`;
  - generated artifacts remain under `D:\GannFinancialAstro\app_artifacts`.
- Real retained research source:
  - snapshot `USDJPY_H1_20260712T105022Z_dc53a058`;
  - 192 fully closed H1 bars from `2026-07-01T00:00:00Z` through
    `2026-07-10T23:00:00Z`, captured/as-of `2026-07-12T10:50:22Z`;
  - Parquet SHA-256
    `8D0C8C9C3C4DAF403E8E40B139CCDA134E598E43250A42C3C8C4B6CD1415154E`;
  - promoted source `mt5_USDJPY_H1_20260712T105022Z_dc53a058`, verified on every
    resolution and idempotent when promoted again.
- Real retained corrected artifact:
  - artifact `tn_2beda5f38c4f4cc2bb866fa88c174bf2`;
  - label `July 2026 promoted MT5 research`;
  - 29 corrected TN events and 12 SR touches;
  - active parameters preserve the promoted source ID, source contract, as-of time and SHA;
  - restart verification restored the July source/range and rendered 187 H1 candles with
    29 visible aspects.
- Native UI workflow now exposes, in order, `Snapshot MT5 range`, a captured-snapshot
  selector with already-promoted status, `Verify and promote snapshot`, and `Price archive`
  selection. Incompatible source/timeframe combinations are rejected or reset to baseline.
  The bundled corrected baseline remains immutable and selectable.
- Native release updated in place:
  - version `0.2.0`;
  - executable `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`;
  - SHA-256 `C26E8AA3EFC63DD2AAE4C13BDBB9CC14F4084F738BFC57BCCBA0E843DB56D90B`;
  - 1,656 files / 698,293,933 bytes;
  - packaged visual QA confirmed the July chart, 29-aspect count, H1 archive, promoted
    snapshot status and MT5 read-only connection.
- Verification at this checkpoint:
  - `79 passed` for the full Python suite;
  - `5 passed` for frontend tests;
  - backend package suite passed (`16 tests`);
  - Oxlint clean;
  - TypeScript/Vite production build clean;
  - packaged API restart, health, price-source registry, snapshot lineage and native UI
    checks passed.
- Canonical tracked annotation seed contains the new empty app registry tables only: zero
  price-source, artifact and generation-job rows. The retained July source/artifact live only
  in the writable D:-drive application state.
- Remaining deliberate gate: consolidate retrospective review Auto Suggest and future/live
  inference into one timestamp-safe, versioned decision engine with purged no-lookahead
  evaluation before any execution path can consume promoted artifacts. MT5 remains
  `read_only_market_data` and `tradeAllowed=false`.
- Recovery backup:
  `D:\PycharmProjects\chat_session_backups\session_20260712_165050_snapshot_promotion`.

## XE3R1 Packaged API Repair (2026-08-21)

- Diagnosed the 0.10.55 founder-inspection failure in the exact packaged
  sidecar. Concurrent XE3 startup reads raced on the shared
  `D:\GannFinancialAstro\app_data\xe3_outcome_blind_sign_admission\index.tmp`,
  causing `PermissionError [WinError 32]` while replacing `index.json`.
  Flask returned its HTML 500 page, which the frontend reported as
  `Unexpected token '<'`. The routes, sidecar module, packet resources, and
  packaged API base were present and reached correctly.
- Source repair commit: `1970f86` serializes the index/ledger transaction,
  uses unique temporary files, returns structured JSON for API errors, and
  provides body-aware frontend JSON diagnostics. XE3 scientific semantics and
  safety locks are unchanged.
- Corrected founder candidate source/package commit:
  `6a4230a65921a60769caab09e9f259e9e039fd54`.
- Candidate:
  `0.10.56-pfr-v2b-r8-xe3r1` at
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.56-pfr-v2b-r8-xe3r1-tauri`.
  Portable SHA-256:
  `30E2508909C06BEE663ECF431035D2E2D196C67C8E080D95F84AEC2D4FE5184B`.
  Installer SHA-256:
  `844DE85B0DF3F74111AE2C452F04B1D158D73E1A374E409132C7B3A8543235BD`.
- Exact packaged endpoint probe passed: all three XE3 startup requests returned
  `200 application/json`; the workbench contained 24 rows, 12 USD and 12 JPY,
  all `SINGLE_PASS_VERIFIED`. Two native portable smoke runs passed, including
  sidecar recovery and clean shutdown. Physical UI smoke also passed: USD and
  JPY event details rendered with full hashes, UTC/IST, transit/natal/aspect,
  raw motion speed, and `SINGLE PASS VERIFIED`; outcome blindness remained
  visible and execution remained locked.
- Verification: focused XE3 8 + 4 backend tests and 16 frontend tests passed;
  full backend 250 passed; full frontend 41 files/174 tests passed; lint,
  production build, cargo fmt, cargo check, and 19 Rust tests passed.
- Founder acceptance is still pending physical inspection of the corrected
  candidate. 0.10.55 remains immutable; no XE3 decision, price/outcome read,
  Fields/SBC path, Auto Suggest, ML, MT5, or execution path was enabled.
- Report:
  `docs/research/PFR_V2B_R8_XE3R1_FOUNDER_INSPECTION_CANDIDATE_0.10.56-pfr-v2b-r8-xe3r1.md`.

## CGVO-P1 Classical Geography & Visibility Inspector (2026-08-21)

- Added the bounded `PFR-V2B-CGVO-P1` read-only research inspector. It is
  available from `Experiments` as `CGVO classical geography & visibility`.
- Modern solar/lunar eclipse facts use Swiss Ephemeris under
  `MODERN_ASTRONOMY_VISIBILITY_V1`. Global event identity is one causal event
  per physical eclipse; locality changes only local circumstances. UT is the
  identity time scale and timezone is display-only.
- Varahamihira is exposed as the separate
  `VARAHAMIHIRA_BS_ECLIPSE_V1` source ledger. Its held witness remains marked
  `WORKING_WITNESS_METADATA_PENDING`; unresolved rasi, nakshatra frame, lunar
  month, morphology, colour, and other mappings remain explicit unknowns.
- Trailokya is exposed separately as
  `TRAILOKYA_1972_GEOGRAPHY_ARGHA_V1` with the exact source-silent eclipse
  visibility banner. No cross-source composition or live Trailokya eclipse
  calculation is performed. Kurma groups remain raw source groups with modern
  mapping unknown.
- CGVO fixtures are packaged read-only under `configs/research/cgvo` and are
  covered by the desktop packaging tests.
- Guardrails remain closed: no price/outcome read, market direction, score,
  Fields, SBC, Auto Suggest, ML, MT5, or execution. `executionAllowed=false`.
- Candidate status is founder inspection only; physical founder review is
  pending. The CGVO report is
  `docs/research/PFR_V2B_CGVO_P1_CLASSICAL_GEOGRAPHY_VISIBILITY_INSPECTOR.md`.

## CGVO-P1 Founder-Inspection Candidate (2026-08-21)

- Built immutable candidate `0.10.57-pfr-v2b-cgvo-p1` from source/package commit
  `7ce501704cefc6be5201ab98d08505964417b8fb`; clean-state declaration is
  `source_git_dirty=false`.
- Portable artifact:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.57-pfr-v2b-cgvo-p1-tauri\GannAstroDesk.exe`
  SHA-256 `3F98069850C58A8B45AAA06C754FCD765FB59C21D33B77FF2153C26CFFFD89E8`.
- Installer:
  `D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.57-pfr-v2b-cgvo-p1-tauri\Gann Astro Desk_0.10.57-pfr-v2b-cgvo-p1_x64-setup.exe`
  SHA-256 `7F0EA5B729677E73E259977AA4455438C8123594A99D388C5E0777A4F40F89F9`.
- Focused CGVO verification passed: 7 backend tests, 2 frontend tests and 6
  packaging tests. Full regressions passed: backend 258/258 and frontend 42
  files/176 tests. Lint, Vite build, Rust fmt/check/tests and Tauri packaging
  passed.
- Two portable smoke runs passed startup, sidecar recovery, clean shutdown and
  execution-lock checks. The exact packaged CGVO API probe returned JSON 200s
  for status, source profiles, Kurma seed and workbench routes; the workbench
  contract is `CLASSICAL_GEOGRAPHY_VISIBILITY_OBSERVATORY_V1` and its
  `executionAllowed` state is false.
- CGVO remains a read-only, source-separated research inspector. No price,
  market direction, score, Fields/SBC, Auto Suggest, ML, MT5 or execution path
  was added. Physical founder inspection of the candidate remains pending.
- Candidate report:
  `docs/research/PFR_V2B_CGVO_P1_FOUNDER_INSPECTION_CANDIDATE_0.10.57-pfr-v2b-cgvo-p1.md`.

## CGVO-P1R1 Founder-Inspection Correction (2026-08-21)

- Preserved `0.10.57-pfr-v2b-cgvo-p1` and its portable/installer artifacts as
  the historical candidate; no files in that release folder were modified.
- Corrected the CGVO research inspector so Sun and Moon horizontal
  coordinates are topocentric, with the Swiss Ephemeris source azimuth retained
  and an explicit north-clockwise display normalization.
- Added `VISIBLE`, `NOT_VISIBLE`, and `RISE_SET_CLIPPED` visibility states with
  horizon/clip details. A locality without a matching local eclipse now returns
  null horizon fields instead of leaking timestamps from another event.
- Added separate lunar umbral and penumbral magnitude fields and an explicit
  Swiss-Ephemeris magnitude reference.
- Split Swiss UT identity fields from UTC display aliases and require the
  frontend causal event ID to match the backend's reconstructed immutable event.
- Extended the Kurma seed with raw Chapter XIV historical names and verse
  ranges only; modern geographic inference remains disabled.
- Source implementation record:
  `docs/research/PFR_V2B_CGVO_P1R1_INSPECTION_CORRECTIONS.md`.
- Focused CGVO/API tests: 13 passed. Full supported backend regression:
  264/264. Full frontend regression: 42 files, 177 tests. Oxlint and the
  production build pass. Rust fmt/check pass and 19 native Rust tests pass.
- New immutable candidate packaging and its physical founder-inspection state
  are pending completion in a separate packaging/report update. All locks
  remain closed: no price/outcome read, direction, score, Fields, SBC, Auto
  Suggest, ML, MT5 or execution; `executionAllowed=false`.

## CGVO-P1R1 Immutable Founder-Inspection Candidate (2026-08-21)

- Preserved historical candidate `0.10.57-pfr-v2b-cgvo-p1` unchanged.
- Built corrected immutable candidate `0.10.58-pfr-v2b-cgvo-p1r1` from source
  commit `86b10f0266e67efa25fcbd1a5b1f1f08a88bb6a5`; release manifest declares
  `source_git_dirty=false`.
- Portable SHA-256:
  `ACA866A885FF6C4E63B3D288BB93558647A3AE7D90A6A84E3A1298F7656158FD`.
- Installer SHA-256:
  `E2B9F61A72DE70F8A7371195614FC5643A58E6BC7CF15EB26C31E702A6AEC322`.
- The exact packaged JSON probe passed: JSON responses, topocentric and
  explicit azimuth facts, rise/set clipping, lunar umbral/penumbral magnitudes,
  Swiss UT versus UTC display fields, causal-ID validation, and raw Kurma names
  without modern geographic inference.
- Focused CGVO/API tests: `13/13`; backend: `264/264`; frontend: `42 files,
  177/177`; Oxlint, production build, Rust fmt/check, and `19/19` Rust tests
  passed. Two portable smoke runs passed with zero errors and clean sidecar
  recovery/shutdown.
- Report:
  `docs/research/PFR_V2B_CGVO_P1R1_FOUNDER_INSPECTION_CANDIDATE_0.10.58-pfr-v2b-cgvo-p1r1.md`.
- Founder physical inspection remains pending. All CGVO safety boundaries stay
  closed: no price/outcome read, market direction, score, Fields, SBC, Auto
  Suggest, ML, MT5, or execution; `executionAllowed=false`.

## CGVO-S1A Varahamihira Source-Architecture Integration (2026-08-21)

- Implemented the bounded, read-only `CGVO-S1A` source architecture on top of
  the accepted CGVO-P1R1 modern eclipse workbench. No new eclipse engine was
  introduced.
- Added immutable source fixtures for the fixed rasi/nakshatra partition,
  precessional distinction, explicit Chitra/Spica-at-180 reconstruction
  candidate, ordinary purnimanta lunar-month profile, categorical eclipse
  aspect profile, firmament geometry limits, and the S1 readiness matrix.
- The Chitra reconstruction is an explicit selector only. With no selection,
  rasi/nakshatra and sign-relative aspects remain unavailable rather than
  silently using Raman, Lahiri, tropical, or another frame.
- Lunar month display is limited to ordinary unambiguous purnimanta cases;
  intercalation and unresolved cases remain
  `UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED`.
- Eclipse aspects expose sign-relative categorical fractions and literal source
  effect tokens only. `effectMagnitudeMultiplier=null` and
  `jupiterMitigationCoefficient=null` remain explicit.
- The firmament panel exposes raw apparent altitude, normalized/raw azimuth,
  local hour angle, rise/set state, and meridian relation. Its classical
  section stays `UNKNOWN` under `COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED`.
- The raw Chapter XIV Kurma names, Trailokya isolation, and all P1R1 modern
  visibility behavior remain intact. No price/outcome read, market direction,
  score, Fields, SBC, Auto Suggest, ML, MT5, or execution path was added;
  `executionAllowed=false` is invariant.
- This is source and UI implementation only. No Windows candidate is built in
  S1A; central review is the next gate. See
  `docs/research/CGVO_S1_SOURCE_CLOSURE_REPORT_V1.md` and
  `docs/research/CGVO_S1A_TERRA_HIGH_DIRECTIVE_V1.md`.

## CGVO-S1A-R1 Central-Review Correction Pass (2026-08-21)

- Corrected four bounded central-review defects on top of CGVO-S1A without
  changing P1R1 event identity, local visibility, source separation, or the
  no-market/no-execution boundaries.
- The lunar adapter now uses physical new-moon-to-new-moon intervals and counts
  selected-frame solar rasi ingress boundaries. Every relevant interval must
  contain exactly one ingress; otherwise it returns
  `UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED` with a typed reason and the full
  ingress audit. The 2023-07-29 regression now fails closed; 2025-04-15 stays
  an ordinary `VAISHAKHA` case only after the guard is clear.
- Eclipse aspect records now distinguish maximum-time
  `GEOMETRY_SNAPSHOT_ONLY` from source-phase activation. The latter remains
  `UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED`; effect and Jupiter mitigation
  activation are `null`, and no multiplier, angular orb, or interpolation was
  introduced.
- All Swiss `set_topo`, topocentric RA, altitude, azimuth, and local hour-angle
  work runs through one existing `RLock`-protected locality helper. Repeated
  Ujjain/New York concurrent workbench calls are regression-tested against
  their individual baselines.
- Updated stale rasi/nakshatra, purnimanta, firmament, and geography wording to
  match S1A's actual source states. Chitra/Spica remains explicit and never
  defaults; firmament `classicalSection` remains `UNKNOWN`.
- No Windows package is produced in this correction pass. Central review is the
  next gate; see `docs/research/CGVO_S1A_R1_CENTRAL_REVIEW_CORRECTION.md`.
## CGVO-G1 Historical Geography Gazetteer (2026-08-22)

- Added `CGVO_HISTORICAL_GEOGRAPHY_GAZETTEER_V1`, a read-only compiler over
  the existing Chapter XIV Kurmavibhaga seed. It returns 308 raw source-name
  records over the nine directional nakshatra triads without altering the
  source transliterations.
- Added a bounded candidate-evidence overlay: six high-confidence records,
  three medium-confidence records, one approximate-region-only record, and one
  contested Kamboja record. The remaining 297 raw records remain
  `SOURCE_NAME_ONLY`; no difficult term was silently mapped to a modern state
  or country.
- Added separate Varahamihira XIV, V, XV, and Trailokya geography profile
  contracts. Automatic union/intersection/majority vote is false, and every
  candidate has `geometry: null` with no downstream geometry authorization.
- Added read-only endpoint `GET /api/experiments/cgvo/historical-gazetteer`.
  It uses only checked source fixtures and cannot read price/outcomes or call
  Fields, SBC, Auto Suggest, ML, MT5, or execution. `executionAllowed=false`.
- No Windows candidate was built. Central review is required before any UI,
  geometry enrichment, or experiment milestone.
- Detailed design, source caveats, candidate subset and next blockers:
  `docs/research/CGVO_G1_HISTORICAL_GEOGRAPHY_GAZETTEER.md`.
- Verification: focused CGVO service/API suite `24/24`; full backend `285/285`;
  frontend Oxlint passed, stable thread-pool frontend suite `178/178`, and
  production build passed; `cargo fmt --check`, `cargo check`, and Rust tests
  (`19/19`) passed. No packaging was authorized or performed.

## CGVO-G1-R1 Historical Geography Evidence Integrity Correction (2026-08-22)

- Corrected the G1 source locator format to `Brihat Samhita 14.2-14.4` and
  explicitly locked all 308 raw root records to
  `rawSourceCategory=UNKNOWN` / `NOT_CLASSIFIED_FROM_ROOT_SOURCE`. Candidate
  overlay meaning now lives only in `candidateEntityType`; it cannot rewrite a
  Chapter XIV source literal.
- Re-grounded Māthuraka in a direct Chapter-XIV working translation/gloss and a
  lexical `māthuraka` witness. Its candidate type is now
  `PEOPLE_OR_URBAN_ASSOCIATION`; the root source category remains unresolved.
  The prior Surasena-centred Cambridge wording remains secondary context only,
  not identity proof.
- Locked the read-only audit contract to exactly 308 contextual occurrences:
  297 source-name-only, 6 high-confidence, 3 medium-confidence,
  1 approximate-region-only, 1 contested, and 0 unmapped. Directional counts
  are fixed in tests and repeated names remain distinct source occurrences.
- CGVO status metadata now reports `CGVO-G1-R1` as current geography work while
  preserving `CGVO-S1B-R1` as the astronomy milestone. No UI, geometric
  activation, astronomy computation, price/outcome read, polarity, score,
  Auto Suggest, ML, MT5, or execution path was added; `executionAllowed=false`.
- Verification: focused CGVO/S1B/API suite `32/32`; full backend `286/286`;
  Oxlint, stable serial frontend suite `178/178`, and production build passed;
  `cargo fmt --check`, `cargo check`, and Rust tests (`19/19`) passed. No
  Windows candidate was authorized or created.

## CGVO-G2 Historical Geography Research Footprint Layer (2026-08-22)

- Added a separate read-only `CGVO_HISTORICAL_GEOGRAPHY_RESEARCH_FOOTPRINTS_V1`
  contract and endpoint at
  `GET /api/experiments/cgvo/historical-gazetteer/research-footprints`.
  The G1-R1 gazetteer remains unchanged in meaning and now explicitly returns
  `geometry: null` for every one of its 308 source occurrences.
- Added an uncertainty-first G2 geometry policy, a 12-row footprint ledger for
  the existing 11 reviewed G1 candidate terms, and a readiness matrix. Nine
  records are `GEOMETRY_PENDING_EVIDENCE`; Sindhu is a non-land
  `RESEARCH_CORRIDOR_OR_RIVER_SYSTEM`; and the two Kamboja alternatives remain
  `CONTESTED_RESEARCH_GEOMETRIES` with no merge or preferred geometry.
- No coordinate-bearing point, multi-anchor, broad envelope, modern state/country
  polygon, map UI, eclipse-visibility comparison, or downstream spatial
  intersection was admitted. All footprints use `RESEARCH_GEOMETRY_ONLY` and
  copy evidence from existing G1 candidates while requiring uncertainty,
  temporal applicability, and limitations.
- The policy keeps source-layer composition, price/outcome reads, market routing,
  polarity, scoring, Fields/SBC, Auto Suggest, ML, MT5, and execution false.
  `executionAllowed=false`, `downstreamIntersectionAuthorized=false`, and
  `marketUseAllowed=false` are validator-tested. No Windows candidate was
  authorized or created; central review is the next gate.
- Verification: focused CGVO/G2/S1B/API suite `35/35`; full backend `289/289`;
  Oxlint, stable serial frontend suite `178/178`, and production build passed;
  `cargo fmt --check`, `cargo check`, and Rust tests (`19/19`) passed.
