# MO-R4A-Candidate C P0 Population and Preregistration Freeze

**Milestone:** MO-R4A-CANDIDATE-C-P0
**Starting repository:** gouravdamade/gann-financial-astro-research
**Starting commit:** fe5dde00a8a260dd1fe9866fd670c96d6027d7a4
**Status:** FROZEN BEFORE EVALUATOR IMPLEMENTATION
**Stop gate:** CENTRAL_REVIEW_CANDIDATE_C_P0_BEFORE_EVALUATOR_A_OR_B_IMPLEMENTATION

## Purpose and boundary

This record freezes the input population, source-profile scope, output schema,
UNKNOWN behavior, and clean-room reproducibility contract for the R6 Candidate C
experiment:

R6_CANDIDATE_C_SOURCE_PROFILED_UNSIGNED_REPRODUCTION_AND_ABSTENTION

Candidate C is a deterministic reproduction and abstention experiment. It is
not a market experiment and does not test price, return, outcome, direction,
polarity, magnitude, profitability, or execution. No evaluator, comparator, or
runtime code is implemented by this P0 freeze.

The substantive R6 conclusion is unchanged:

- source profiles remain isolated;
- market/currency polarity is SOURCE_SILENT;
- sign and magnitude are NOT_ASSIGNED;
- applying/exact/separating efficacy and persistence/decay remain unsupported;
- universal precedence/cancellation and modifier stacking remain unresolved;
- D_i remains an engineering mapping only;
- duration is not strength;
- no Mode 1 promotion or market experiment is authorized.

## Fixed population

The population interval is fixed before evaluator implementation:

[2025-05-01T00:00:00Z, 2025-08-01T00:00:00Z)

The interval is the first three complete calendar months following the closed
April-2025 S4 founder window. It is not selected from event counts, S4
success/failure rows, prices, returns, or any result-derived criterion.

The inclusion rule is:

1. take every distinct canonical event identity emitted by the accepted event compiler;
2. retain the event when exactUtc is in the fixed half-open interval;
3. require the compiler interval invariant startUtc <= exactUtc < endUtc;
4. do not apply an applying/separating efficacy rule;
5. do not apply a market-calendar exclusion;
6. deduplicate by eventId;
7. order by exactUtc ascending, then eventId ascending.

The frozen population contains **645** unique event identities:

| side | compiler-emitted events | exact-UTC population |
| --- | ---: | ---: |
| USD | 330 | 317 |
| JPY | 338 | 328 |
| **total** | **668** | **645** |

The exact population hash is:

A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6

It is the uppercase SHA-256 of the UTF-8 canonical JSON representation of
the ordered population array only, using ensure_ascii=true, sort_keys=true,
and compact separators (',',':').

The machine-readable population manifest is:

status/research/mo_r4a_candidate_c_p0_population_manifest_v1.json

Its self-hash is:

0B384FF0131BF19EFB842A3D4AEE4F7D1F9A923469281A65D6326B76CC39A092

The manifest self-hash uses this convention:

SHA-256 uppercase hex of UTF-8 canonical JSON: ensure_ascii=true, sort_keys=true, separators=(',',':'); exclude populationManifestHash.

## Event compiler and astronomy identity

The accepted compiler is unchanged and is used only to create this frozen
astronomical event population:

- contract: CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1
- schema version: 1
- source path:
  research_labs/chart_conditioned_aspects/chart_conditioned_aspects/transits/chart_conditioned_event_compiler.py
- source commit:
  1b65eee8e01380265e4e2062ffe5e7ad388007fb
- source SHA-256:
  21AB7EE377C8BF2EB5CA798A651678DD9AA1E16EA149523EF13BB9AD6A68EAD0
- version: chart_conditioned_transit_event_compiler_v1_20260806
- approved aspect profile: ASPECT_STRENGTH_V0
- generator hash:
  8B3F7990F07A7A73AD11B0469C55B657C05908D8566914E008409D81BCC75028
- event boundary search padding: 180 days
- body universe: SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU

The frozen astronomy contract is:

- config ID: doctrine_v7_20260729_visible_sthana_reconciliation
- contract ID: RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1
- zodiac: sidereal
- ayanamsha: Raman / SIDM_RAMAN
- node type: true node
- coordinate system: geocentric
- provider: Swiss Ephemeris 2.10.03
- internal time: UTC/JD_UT
- display time zone: Asia/Kolkata
- historical time policy:
  HISTORICAL_CIVIL_TIME_IANA_ZONEINFO_V1
- calculation flags: FLG_SWIEPH|FLG_SPEED|FLG_SIDEREAL
- node policy: TRUE_NODE_RAHU_KETU_OPPOSITION_V1

The canonical astronomy configuration hash is:

6569213C213B854E4E5CEC7FFF6F96EAABCFF6B15C58309B2F8A0DAC55ACB95C

Bound configuration artifact hashes are:

- doctrine_config.yaml:
  64B70EB797F680709F32B6D6D60E2F0255D1B1B4E5531FEAFB743D6163D3DB7C
- doctrine_config.py:
  0988F805B64E2BBFEE4EE41AF374654987E5D091A05BB0413EE94160788D5537
- financial_astro_ephemeris.py:
  7AD647AB27317A9449EA5D0A05083F4FD5293790D44ADE5F106B42BB2D9A97D5
- research_labs/chart_conditioned_aspects/profiles/aspect_strength_v0.yaml:
  766339E51ED9DCDAB89712CBFB1F97F24CA9BF1D82C8108082B845D7D2E0479D
- research_labs/chart_conditioned_aspects/profiles/source_manifest.yaml:
  9832E132DFB7A3CAB831F1BAA76638B70D0FE9390DEB7A3DF0A418EF00BCCE59

Frozen chart identities are the existing founder-approved research hypotheses:

- USD:
  FX_CURRENCY_USD_US_INDEPENDENCE_17760704T165602Z_V1,
  hypothesis USD_US_INDEPENDENCE_PHILADELPHIA_EXACT_TIME_RESEARCH_V1,
  chart hash
  3A6B5F3EED9CBF0067FCB39EED1191EA66F0C347BE726DDD84424C001B89BCA7.
- JPY:
  FX_CURRENCY_JPY_YEN_IPO_18890210T150000Z_V1,
  hypothesis JPY_YEN_IPO_TOKYO_EXACT_TIME_RESEARCH_V1,
  chart hash
  4ED100D71983BE68A24B8306C33D7D2B50504D6F122DF45A5F7707A68B171AF7.

The founder chart registry is
research_labs/chart_conditioned_aspects/profiles/founder_chart_hypotheses_v1.json,
SHA-256
DF98FA855D3CC15407DFCB4EC859145503C33609F3E6C11411239190288B3214.

## Source-profile scope

Only these two source profiles are admitted, and they remain separate:

1. TRAILOKYA_DIPIKA_1972
2. BJ_SARAVALI_CROSS_TEXT_CONTRACTS_AS_SEPARATE_PROFILES

The seven admitted component families are:

| component | source contract IDs | scope |
| --- | --- | --- |
| C01_NATURAL_PLANET_CLASS | TRAILOKYA_1972_NATURAL_PLANET_CLASS_V1 | Moon/Mercury conditions remain source-bounded categorical records |
| C02_NATURAL_RELATIONSHIP | TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1 | Trailokya natural relationship only |
| C03_TEMPORARY_RELATIONSHIP | BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1 | Separate temporary-relationship contract |
| C04_COMPOUND_RELATIONSHIP | BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1 | Separate compound-relationship contract |
| C05_ORDINARY_AND_SPECIAL_DRSTI | SARAVALI_4_32_ORDINARY_DRSTI_V1; CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1 | Separate ordinary/special contracts; no pooling |
| C06_STHULA_MOTION | TRAILOKYA_1972_STHULA_MOTION_CLASS_V1 | Source-defined Sthula category only |
| C07_INDIVIDUAL_SOURCE_RECORDS_NO_STACKING | TRAILOKYA_1972_V166_INDIVIDUAL_MODIFIER_V1 | Individual records only; no modifier stacking |

The source operator ledger is
configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s1r1_v1.json,
SHA-256
4C7D0C4C1A366287A05DD70E9638A27585516240B24C3AEEBFA91889F22E86E8.

The provenance-hardening contract is
configs/research/machine_interpretation/source_operators/classical_source_operator_provenance_hardening_s1r1_v1.json,
SHA-256
1DA908C0BCD9DE80A36B0DB13A04A9868906D06C336A9871D1EAB20512058A80.

The cross-text matrix is
configs/research/machine_interpretation/source_operators/source_operator_cross_text_matrix_v1.json,
SHA-256
407E598D1A5033842369C0ACCB774763ADA5F7B37FF98CE8CEAC0F57A8D65467.

The Trailokya source artifacts remain bound to their existing identities:

- planet nature conditions:
  TRAILOKYA_1972_CATEGORICAL_PLANET_NATURE_V1,
  SHA-256
  9F6D7C637A4FF75E5C5C169785B108278CAB622E1ED02CE27D093F1DC58DB99B;
- Vedha magnitude/source records:
  TRAILOKYA_1972_VEDHA_MAGNITUDE_SOURCE_V1,
  SHA-256
  ADBEE77743FA13A1D2173F744A68A8D3E0B6DB6A26FBF549FEE73DFF293898B9;
- Sthula motion:
  TD1972_STHULA_SWIFT_MEAN_CLASSIFICATION_V1,
  SHA-256
  AEB4F455C89A11A7B28B694C8EB245D41A981E8A65D09D8CE8D1196614BB893E.

The two frozen source-profile binding hashes are:

- TRAILOKYA_DIPIKA_1972:
  82C434BDCF68889BC842576151886A4C7A544A8F2581A4D8C046797C80A404C4
- BJ_SARAVALI_CROSS_TEXT_CONTRACTS_AS_SEPARATE_PROFILES:
  AAFE7CDB05AFD038D664CE68D1FB9D106ED0A14C25ED736423BC86C1F318B2D5

No source contract is merged into the other profile. Candidate C does not
average, vote, harmonize, or count repeated doctrine as independent evidence.

Verse-166 records, if included by a future evaluator, remain separate
retrograde, exalted, swift, and debilitated source records. The unresolved
MULTI_MODIFIER_STACKING_UNRESOLVED state remains UNKNOWN; no composition is
licensed.

## Frozen evaluator output schema

The machine-readable preregistration freezes schema
MO_R4A_CANDIDATE_C_P0_EVALUATOR_OUTPUT_SCHEMA_V1 with hash:

DDBE5164FF93A8A1982891AD24CD40367C2A0F4F0FAA0CDAD0289A74D92A33BC

Each evaluator row must contain:

- eventId
- sourceProfile
- componentId
- sourceContractId
- inputIdentity
- inputIdentityHash
- outputStatus
- sourceValue when the selected source contract closes a value
- unknownReasonCode when outputStatus=UNKNOWN
- provenance

No expected output values are frozen by P0.

The only output statuses are VALUE and UNKNOWN. Applicability remains
source-contract scoped. No separate NOT_APPLICABLE status is introduced.
Missing inputs, unsupported context, source-unclosed conditions, unresolved
composition, or mandatory abstention must remain UNKNOWN with an allowed
reason code.

The allowed UNKNOWN taxonomy is
MO_R4A_CANDIDATE_C_ALLOWED_UNKNOWN_V1, bound to
MO_R4A_S1_SOURCE_OPERATOR_UNRESOLVED_DEPENDENCY_REGISTRY_V1, with hash:

1B1F6DFF937398F34E787CED256800BC6879D1ABCE989918A24B92DC8E7332B3

The allowed reason codes are existing source/operator states:

- UNKNOWN
- MOON_CONDITION_INPUT_UNAVAILABLE
- MERCURY_ASSOCIATION_INPUT_UNAVAILABLE
- MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED
- RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_TRAILOKYA
- COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED
- TRAILOKYA_STATIONARY_STATE_UNRESOLVED
- ASTA_DIRECTION_UNKNOWN
- MULTI_MODIFIER_STACKING_UNRESOLVED
- UNRESOLVED_MODIFIER_COMBINATION

The dependency registry artifact is
configs/research/machine_interpretation/source_operators/source_operator_unresolved_dependencies_v1.json,
SHA-256
16292D6655B3BC4BEFEC2A7A39B91C4649F2AF01248020AA1629E7FF56A0D7C.

## Clean-room implementation contract

The required topology is:

P0 freeze commit -> separate clean Evaluator A worktree/branch and separate clean
Evaluator B worktree/branch -> third comparator

Evaluator A and Evaluator B must be separate implementations. Neither may
import the other evaluator's code, business logic, source-category helpers, or
expected-output fixtures. Both implementation identities and source hashes must
be frozen before either output is inspected.

They may share only:

- the frozen input population;
- exact astronomy inputs;
- immutable source packet and contract identities;
- this frozen schema;
- declared semantic rules.

Any mismatch on a declared source-closed field, UNKNOWN mismatch, unlicensed
fallback, or silent substitution fails the frozen run. Neither implementation
may be patched after seeing a discrepancy while retaining the same run. A
source adjudication or implementation correction requires a new preregistered
run.

Agreement tests deterministic implementation reproducibility of already
source-certified contracts. It does not independently prove historical truth
beyond the accepted source packets and does not validate market prediction.

## Pass/fail contract

This is not an inferential test:

- statisticalNull:
  NOT_APPLICABLE_DETERMINISTIC_REPRODUCTION
- passCriterion: zero discrepancies across all preregistered source-closed
  fields and mandatory UNKNOWN decisions
- failureCondition: any source-closed disagreement, unlicensed fallback, or
  mandatory UNKNOWN converted to a value
- p-value: not applicable
- averaging, majority vote, and categorical tolerance: prohibited
- post-run repair: prohibited

R6 still contains exactly three candidate experiments. The recommended
experiment remains Candidate C:
R6_CANDIDATE_C_SOURCE_PROFILED_UNSIGNED_REPRODUCTION_AND_ABSTENTION.

## Multi-resolution and product firewall

P0 does not calculate or implement D_i -> scale, R_i = D_i / T, micro/meso/macro
lanes, waves, nested aggregation, persistence, smoothing, or duration-aware
market controls. The compiler's geometric interval boundaries are engineering
inputs only.

The following remain disabled:

- price, return, and outcome access;
- S4 result reuse for population selection;
- provider access;
- polarity and sign assignment;
- magnitude assignment;
- score creation;
- wave creation;
- Fields polarity;
- Auto Suggest;
- ML;
- MT5;
- execution and order logic.

executionAllowed=false.

## Machine-readable artifacts

- Population:
  status/research/mo_r4a_candidate_c_p0_population_manifest_v1.json
- Preregistration:
  status/research/mo_r4a_candidate_c_p0_preregistration_v1.json

The preregistration self-hash is:

1FB698C6420CF5D8F6E950849BF53B9D7BD35AF67DD9EE157DE08161427BD719

Its self-hash convention is:

SHA-256 uppercase hex of UTF-8 canonical JSON: ensure_ascii=true, sort_keys=true, separators=(',',':'); exclude p0PreregistrationHash.

The required freeze identity set is:

- P0 preregistration hash:
  1FB698C6420CF5D8F6E950849BF53B9D7BD35AF67DD9EE157DE08161427BD719
- population manifest hash:
  0B384FF0131BF19EFB842A3D4AEE4F7D1F9A923469281A65D6326B76CC39A092
- exact population hash:
  A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6
- compiler source hash:
  21AB7EE377C8BF2EB5CA798A651678DD9AA1E16EA149523EF13BB9AD6A68EAD0
- astronomy config hash:
  6569213C213B854E4E5CEC7FFF6F96EAABCFF6B15C58309B2F8A0DAC55ACB95C
- source-profile binding hashes:
  82C434BDCF68889BC842576151886A4C7A544A8F2581A4D8C046797C80A404C4 and
  AAFE7CDB05AFD038D664CE68D1FB9D106ED0A14C25ED736423BC86C1F318B2D5
- output schema hash:
  DDBE5164FF93A8A1982891AD24CD40367C2A0F4F0FAA0CDAD0289A74D92A33BC
- UNKNOWN taxonomy hash:
  1B1F6DFF937398F34E787CED256800BC6879D1ABCE989918A24B92DC8E7332B3

## P0 validation

The generated artifacts were checked before this record:

- JSON parsing: PASS
- population manifest self-hash: PASS
- preregistration self-hash: PASS
- exact population hash: PASS
- output schema hash: PASS
- UNKNOWN taxonomy hash: PASS
- event ID uniqueness: PASS, 645/645
- event hash uniqueness: PASS, 645/645
- half-open exact-UTC window: PASS
- compiler interval invariant: PASS
- canonical order: PASS
- seven admitted component families: PASS
- three R6 candidates and one recommendation: PASS
- evaluator implementation/execution: NOT RUN by design
- market/provider/S4/outcome access: NOT PERFORMED

This freeze is complete only at the P0 boundary. It intentionally stops before
Evaluator A or Evaluator B implementation and before any Candidate C execution.

**Next gate:** CENTRAL_REVIEW_CANDIDATE_C_P0_BEFORE_EVALUATOR_A_OR_B_IMPLEMENTATION
