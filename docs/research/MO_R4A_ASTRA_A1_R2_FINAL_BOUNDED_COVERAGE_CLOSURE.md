# MO-R4A-ASTRA-A1-R2: Final Bounded Coverage Closure

Date: 2026-09-25. Read-only forensic audit; no repair or promotion.

## Verdict

**ASTRA_FULL_CLASSICAL_ASSUMPTION_AUDIT_COMPLETE**

This is completion under the R2 risk boundary, not a claim that the doctrine,
software tests, classical interpretation, physical UI, or market validation is
complete. Genuine unresolved source questions remain explicitly classified.

Target: `865e99e372bdea9cf53c0b4f61426b241b1d6e60` on
`research/candidate-c-emp2-r2-final-scientific-close`.

Repository: `D:/PycharmProjects-cgvo-candidate-c-emp2-r2-close-f1-worktree`.
All successor artifacts are outside it. No commit, push, fetch, checkout, runtime
import, empirical test, provider call, or MT5 call was performed.

## Findings

1. **Critical: a reachable experimental directional path remains.** The Analyze
   Aspect detail effect calls `fetchLiveDecision` automatically. The chain is
   `/api/decisions` -> `repository.live_decision_packet` ->
   `ENGINE.live_inference_packet` -> `score_currency_pair_for_row`. Eligible
   packets can display WATCH LONG / WATCH SHORT beneath "Timestamp-safe
   inference". It also displays execution locked, failed historical gate, and
   research-watch warnings. Timing safety is not scientific validity. These
   warnings mitigate, but do not remove, the semantic risk of a signal-like UI.
   The audit read rendering code, not a running application or market output.

2. **High: missingness is not uniform.** Drik defaults missing Sun/Moon phase to
   benefic and missing Mercury position to an apparently isolated benefic. A
   known target with unavailable aspectors can retain a numeric available total.
   Saptavargaja skips unresolved terms; Yuddha skips missing competitors and may
   report zero/no candidate. The outer Shadbala all-finite guard remains, but
   cannot detect inner components that already substituted or omitted data.
   AVG(ALL) individual components may average differing finite populations.
   The successor adds R2UN01: Paksha also defaults absent Mercury association
   information to benefic when phase exists, while missing phase yields NaN.

3. **High: legacy partial-side scoring can still resolve direction.** A
   textually present base field, including the string `[]`, plus one scored side
   can pass the directional gate. Missing strength becomes zero; missing dignity
   becomes zero before the engineering 0.5 strength-factor baseline. Mocked
   decision tests do not establish raw scorer completeness. Required source
   contract/chart fields instead reject via validation or exception; they do not
   fabricate a chart. The complete condition-by-condition matrix is in
   `mo_r4a_astra_a1_r2_active_path_and_missingness.json`.

4. **High: CGVO UTC alias is mislabelled.** Disposition:
   `CGVO_TIME_ALIAS_MISLABELLED_REQUIRES_REMEDIATION`.
   `cgvo_service.py:155-166` uses Julian-calendar conversion, rounds seconds, and
   attaches UTC. Lines898-911 repeat the Swiss-UT value in UTC display fields.
   Swiss documentation distinguishes `revjul` calendar conversion from
   `jdut1_to_utc` time-scale conversion. The causal hash uses `globalMaxSwissUt`,
   not its display alias. No event was recalculated and no blanket all-epoch
   error bound or identical rounded-second guarantee was inferred. Official
   reference: https://www.astro.com/swisseph/swephprg.htm sections9.1-9.2.

5. **Source recovery succeeds, without harmonizing conflicting layers.** Both
   exact held PDFs were found and independently full-file hash verified. Ten
   page images were inspected. Saravali root4.32 has third/tenth quarter,
   fifth/ninth half, fourth/eighth three-quarters, seventh full. Its English
   translation swaps the middle two fractions. Root4.33 special full aspects
   remain separate. Root4.35 supplies named directional maxima; Santhanam's
   Notes explicitly supply maximum60, opposite nil, and intermediate
   rule-of-three. The latter narrows the previous interpolation evidence gap,
   but does not certify every production cusp/fallback convention or authorize
   changing the frozen categorical operator.

6. **Execution boundary is scoped, not repository-wide incapability.** Candidate C
   and the inspected decision packets retain executionAllowed=false. No automatic
   WATCH-to-order consumer was located. Root `mt5_trade_executor.py` is a separate
   manually armed order-capable CLI requiring `--live --confirm LIVE`; it does
   not derive authority from Candidate C's lock. Server startup defaults can
   connect a read-only MT5 gateway, so no server or packaged app was launched.

## Exact Source Witnesses

### Saravali

`D:/dektop-pdf/saravaliofkalyan01kalyuoft.pdf`

SHA-256:
`3BFD4F7F717798F87B7EFD6FA5A3DE2E28E7E09FC2520F0F05AE12B2E1BF9A58`

Kalyana Varma, Saravali Volume I, R. Santhanam translation/commentary, Ranjan
Publications, New Delhi, First Edition1983. Identity pages5-6; freshly viewed
content scan59-62, printed55-58. Relevant readings:4.28-29 on60;4.30 on60-61;
4.31-33 on61; English4.32-33 and root4.34-35/Notes on62. Scan59's node discussion
is commentary, not a retroactively attributed root statement. No whole-book
or full positional-strength chapter certification is claimed.

### Brihat Jataka / Bhattotpala

`D:/dektop-pdf/Varahmira-brihtasamhita/brihat jataka (varahamihira)_text.pdf`

SHA-256:
`D1D2DD8FA2F6DB2BE1D4DFEE559E6929945AEA57EB24BCF8A4951AD0153FBE4A`

Title page1 names Varahamihira, Bhattotpala Sanskrit commentary, editor Pandit
Sri Sita Rama Jha, Sri Hari Krishna Nibandha Bhavana, Benares City, and1934.
This is a fresh audit identity observation, not an alteration of source registry.
II.13 root/commentary: scan43-44, printed31-32. Scan50, printed38, contains
continuing II.18 commentary and II.19. The earlier II.18 root page was NOT
freshly inspected; temporary-friend root support in R2 is Saravali4.30.

R1 Trailokya1972 and Brihat Samhita1946 source-image findings remain inherited,
not counted as freshly inspected R2 pages. Root, translation, commentary,
software conformance, and market applicability are never collapsed.

## Coverage and Counts

| Measure | Count |
|---|---:|
| Total propositions | 237 |
| New R2 propositions | 1 |
| Critical risk | 12 |
| Foundational impact | 42 |
| Active source-silent | 9 |
| Mode-1 leakage risks | 13 |
| UNKNOWN coercions | 22 |
| UI-semantic risks | 13 |
| Live-directional assumptions | 19 |
| UNRESOLVED_DOCTRINE | 12 |
| UNFINISHED_AUDIT_COVERAGE | 0 |
| Required risk-based test mappings | 104 |
| Required mappings with related tests | 78 |
| Required mappings without established direct assertion | 26 |

Counts overlap. Critical is `riskIfMisclassified`, not `impactClass`.
UNRESOLVED_DOCTRINE counts the twelve named research-question groups in the
ledger, not every partial proposition. Live-directional count is the explicitly
listed legacy decision/scoring path, not every upstream sensitivity flag.

The twelve doctrine groups cover Raman necessity; currency-natal/historical
chart hypotheses; role/context authority; conditional Moon/Mercury rules;
unstated self/node relationships; translation conflict; quantitative Drik;
quantitative Bala derivation/profile binding; stacking/precedence; motion,
Latta and Arghya transfer; market sign/magnitude; and CGVO calendar/regional
composition. Knowing these gaps is not the same as resolving them.

All required risk IDs have either scoped test evidence or an explicit reviewed
gap. Related complete-input, mocked, or same-library tests are not credited as
negative-case/source-certification tests. The26 no-direct-assertion mappings
are not the total number of test deficiencies: some of the78 related mappings
also lack the relevant edge case. Low-risk exclusions are labelled
`TEST_MAPPING_NOT_REQUIRED_LOW_RISK`. No project test was executed.

## Historical Bound and Completion Rule

Four local branch comparisons inspected selected theory-bearing paths:
`product-first-sbc-oscillator-v2`, `product-first-sbc-phase-lab`,
`pfr-v2b-categorical-oscillator`, and `tn1-native-trailokya-adapter`.
The first two expose the generic scalar/phasor baseline lineage; current
Trailokya-specific geometry gates suppress those features. The latter two are
equal to target for the selected paths, not certified whole-branch equivalents.
Diff hashes, exact refs, selected paths and readings are retained in the external
historical review. No checkout or exhaustive historical archaeology occurred.

No material active path in the R2 requested boundary remains unclassified.
R1's broader unfinished full-directory/minor-constant/physical-UI census is not
retroactively declared performed. Those exclusions are intentional under R2.
Unresolved doctrine, absent negative tests, and remediation needs remain visible.

## Artifacts and Validation

Successor master ledger, coverage manifest, witness manifest, risk-based test
mapping, dependency graph, summary, active-path/missingness matrix, numeric-rule
classification, and bounded historical review are self-hashed canonical JSON.
The independent external validator checks canonical hashes, ID/count consistency,
required mapping coverage, referenced test slices, witness bytes/render hashes,
predecessor preservation, target/branch/clean status, and `git diff --check`.
Validation result is recorded separately in `audit_validation.json`.

R1 ledger identity remains:
`06A43F643E1AF2DEB25525A645907EFB775C274457B9CE5F5252AE3FD35AFDAF`.
R1 summary identity remains:
`A4DDF043EFCEB2AAEF770BC33617F4DD6503343A1D0626CF6C46572B7C3EB84B`.
Final successor identities are in `mo_r4a_astra_a1_r2_summary.json` and the
independent validation record; this report does not duplicate a mutable draft hash.

No source/UI/runtime changes, doctrine promotion, provider access, market-data
read, real outcome read, new empirical analysis, astronomy recalculation, or
execution occurred. Existing source-looking code identifiers and historical UI
warning text are evidence about software, not fresh empirical results.

**STOP: CENTRAL_REVIEW_MO_R4A_ASTRA_A1_R2_FINAL_COVERAGE_CLOSURE**
