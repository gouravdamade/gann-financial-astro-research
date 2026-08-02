// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type {
  ChakraAuditCatalogBuild,
  ChakraAuditPackageBuild,
  ChakraAuditPackageVerification,
  ChakraFixedPhasorSeries,
  ChakraLabSnapshot,
  ChakraLinkedAuditView,
  ChakraTimingProfileAdmissionReport,
  ChakraTimingProfileExternalReviewReport,
  ChakraTimingProfileSignedReviewReport,
  ChakraTimingProfileSourceCertificationReport,
  ChakraTimingProfileSourceReadinessReport,
  ChakraTimingProfileSourceVerificationReport,
  ChartConditionedPolarityLookup,
  CurrencyPairEvidence,
  AspectWindow,
} from './types'
import { ChakraLabWorkspace } from './views/ChakraLabWorkspace'

const {
  buildAuditCatalog,
  buildAuditPackage,
  fetchAudit,
  fetchFixedPhasor,
  fetchSnapshot,
  fetchTimingAdmission,
  fetchTimingExternalReview,
  fetchTimingSignedReview,
  fetchTimingSourceCertification,
  fetchTimingSourceReadiness,
  fetchTimingSourceVerification,
  fetchAspectPolarity,
  verifyAuditCatalog,
  verifyAuditPackage,
} = vi.hoisted(() => ({
  buildAuditCatalog: vi.fn(),
  buildAuditPackage: vi.fn(),
  fetchAudit: vi.fn(),
  fetchFixedPhasor: vi.fn(),
  fetchSnapshot: vi.fn(),
  fetchTimingAdmission: vi.fn(),
  fetchTimingExternalReview: vi.fn(),
  fetchTimingSignedReview: vi.fn(),
  fetchTimingSourceCertification: vi.fn(),
  fetchTimingSourceReadiness: vi.fn(),
  fetchTimingSourceVerification: vi.fn(),
  fetchAspectPolarity: vi.fn(),
  verifyAuditCatalog: vi.fn(),
  verifyAuditPackage: vi.fn(),
}))

vi.mock('./api', () => ({
  buildChakraLabAuditCatalog: buildAuditCatalog,
  buildChakraLabAuditPackage: buildAuditPackage,
  fetchChakraLabAudit: fetchAudit,
  fetchChakraLabFixedPhasor: fetchFixedPhasor,
  fetchChakraLabSnapshot: fetchSnapshot,
  fetchChartConditionedPolarityLookup: fetchAspectPolarity,
  fetchChakraTimingProfileAdmission: fetchTimingAdmission,
  fetchChakraTimingExternalReview: fetchTimingExternalReview,
  fetchChakraTimingSignedReview: fetchTimingSignedReview,
  fetchChakraTimingSourceCertification: fetchTimingSourceCertification,
  fetchChakraTimingSourcePacketReadiness: fetchTimingSourceReadiness,
  fetchChakraTimingSourceVerification: fetchTimingSourceVerification,
  verifyChakraLabAuditCatalog: verifyAuditCatalog,
  verifyChakraLabAuditPackage: verifyAuditPackage,
}))

afterEach(() => {
  cleanup()
  buildAuditCatalog.mockReset()
  buildAuditPackage.mockReset()
  fetchAudit.mockReset()
  fetchFixedPhasor.mockReset()
  fetchSnapshot.mockReset()
  fetchTimingAdmission.mockReset()
  fetchTimingExternalReview.mockReset()
  fetchTimingSignedReview.mockReset()
  fetchTimingSourceCertification.mockReset()
  fetchTimingSourceReadiness.mockReset()
  fetchTimingSourceVerification.mockReset()
  fetchAspectPolarity.mockReset()
  verifyAuditCatalog.mockReset()
  verifyAuditPackage.mockReset()
})

const snapshot: ChakraLabSnapshot = {
  contract: 'SBC_CHAKRA_LAB_SNAPSHOT_V1',
  schema_version: 1,
  snapshot_id: 'chakra-test-0001',
  requested_at_local: '2026-07-17T12:00:00+05:30',
  as_of_utc: '2026-07-17T06:30:00Z',
  evidence_cutoff_utc: '2026-07-17T06:30:00Z',
  timezone: 'Asia/Kolkata',
  location: {
    latitude: 18.5204,
    longitude: 73.8567,
    timezone: 'Asia/Kolkata',
    altitude_m: 0,
  },
  foundation_snapshot: {
    snapshot_id: 'foundation-test-0001',
    profile_id: 'sbc_raman_foundation_v1',
    profile_hash: 'foundation-hash',
    astronomy_contract: 'RAMAN_SIDEREAL_SNAPSHOT_V1',
    panchanga: {
      tithi_name: 'Saptami',
      tithi_group: 'NANDA',
      paksha: 'Shukla',
      moon_phase: 'Waxing',
      yoga_name: 'Shobhana',
      karana_name: 'Gara',
      vara: {
        weekday: 'Friday',
        weekday_lord: 'VENUS',
      },
    },
  },
  grid: {
    grid_profile_id: 'sbc_81_rotation_normalized_partial_v1',
    profile_hash: 'grid-hash',
    rows: 1,
    columns: 1,
    cells: [{
      row: 1,
      column: 1,
      entries: [{
        row: 1,
        column: 1,
        layer: 'NAKSHATRA',
        value: 'BHARANI',
        glyph: null,
        transliteration: null,
        semantic_role: null,
        witness_set_id: 'witness-test',
        evidence_status: 'CERTIFIED',
      }],
    }],
    certified_layers: ['NAKSHATRA'],
    complete: false,
    blocked_capabilities: ['FULL_81_CELL_CERTIFICATION'],
  },
  context_contract: 'SBC_CURRENT_MOMENT_CONTEXT_V1',
  target_context: [{
    layer: 'NAKSHATRA',
    values: ['BHARANI'],
  }],
  position_context: [],
  actor_readiness: [{
    body: 'SUN',
    requested: true,
    status: 'READY',
    source_nakshatra: 'BHARANI',
    motion_class: null,
    reason: 'Fixed-direction actor.',
  }],
  guidance: {
    schema_version: 'SBC_VEDHA_GUIDANCE_V1',
    vedha_profile_id: 'phaladeepika_editor_vedha_guidance_v1',
    vedha_profile_hash: 'vedha-hash',
    grid_profile_id: 'sbc_81_rotation_normalized_partial_v1',
    grid_profile_hash: 'grid-hash',
    guidance_model_id: 'source_profiled_guidance_v1',
    guidance_only: true,
    financial_validation_status: 'NOT_VALIDATED',
    actor_resolutions: [],
    contributions: [],
    favorable_guidance_units: 0,
    adverse_guidance_units: 0,
    net_guidance_units: 0,
    normalized_guidance_score: 0,
    guidance_band: 'NEUTRAL',
    matched_target_count: 0,
    scored_match_count: 0,
    unresolved_match_count: 0,
    scoring_coverage_ratio: 0,
    blocked_capabilities: [],
  },
  source_ids: ['witness-test'],
  guardrails: {
    read_only: true,
    timestamp_safe: true,
    no_lookahead: true,
    execution_allowed: false,
    market_data_included: false,
    financially_validated: false,
    guidance_only: true,
  },
}

const currencyPairEvidence: CurrencyPairEvidence = {
  contract: 'GANN_FX_PAIR_EVIDENCE_V2',
  status: 'provisional_research_only',
  profileId: 'fx_doctrine_consensus_watch_only_v1',
  asOfUtc: '2026-08-01T00:00:00+00:00',
  evidenceCutoffUtc: '2026-08-01T00:00:00+00:00',
  mappingIdentity: 'USD:USD reference|JPY:JPY reference',
  base: {
    label: 'USD', referenceLabel: 'USD reference', netScore: 1.4, doctrineNetScore: 1.2,
    state: 'KNOWN', supportiveUnits: 1.6, adverseUnits: 0.4, netUnits: 1.2, grossActivationUnits: 2.0,
    conflictRatio: 0.2, eligibleCount: 2, scoredHitCount: 2, unresolvedCount: 0, unknownCoverage: 0,
    dominantHit: null, doctrineDominantHit: null,
    doctrineDominantDignity: null, doctrineDignityVirupaAvg: null,
  },
  quote: {
    label: 'JPY', referenceLabel: 'JPY reference', netScore: -0.4, doctrineNetScore: -0.2,
    state: 'KNOWN', supportiveUnits: 0.4, adverseUnits: 0.6, netUnits: -0.2, grossActivationUnits: 1.0,
    conflictRatio: 0.4, eligibleCount: 1, scoredHitCount: 1, unresolvedCount: 0, unknownCoverage: 0,
    dominantHit: null, doctrineDominantHit: null,
    doctrineDominantDignity: null, doctrineDignityVirupaAvg: null,
  },
  pair: {
    state: 'KNOWN', netDifferenceUnits: 1.4, jointNetStrengthUnits: 0.7, commonActivationUnits: 1.5, grossActivationUnits: 3.0,
    netScore: 1.8, conflictRatio: 0.3, conflictRatioLegacy: 0.25, direction: 'UP',
    doctrineNetScore: 1.4, doctrineConflictRatio: 0.2, doctrineDirection: 'UP',
  },
  notes: null,
}

const missingAspectPolarity: ChartConditionedPolarityLookup = {
  contract: 'CHART_CONDITIONED_POLARITY_CATALOGUE_V1',
  schemaVersion: 1,
  lookupState: 'POLARITY_CATALOGUE_MISSING',
  catalogueId: 'CHART_CONDITIONED_TARGET_AWARE_POLARITY_BASELINE_V1',
  catalogueStatus: 'NO_ACCEPTED_PRODUCTION_ENTRIES',
  catalogueHash: 'catalogue-hash',
  instrumentId: 'FX_CURRENCY:USD',
  sideIdentity: 'USD',
  chartId: null,
  entry: null,
  reason: 'No accepted immutable target-aware polarity entry is available for this instrument.',
  stateContract: 'CATEGORICAL_POLARITY_STATE',
  magnitudeState: 'MAGNITUDE_NOT_CONFIGURED',
  guardrails: {
    readOnly: true,
    executionAllowed: false,
    automaticOrderPlacement: false,
    financiallyValidated: false,
    actsAsSbcConfirmation: false,
  },
}

const selectedAspect = {
  eventId: 'event-test-001',
  caseId: null,
  familyKey: 'MARS|SUN::square',
  pairKey: 'MARS|SUN',
  aspect: 'square',
  aspectLabel: 'Square',
  transitBody: 'MARS',
  natalBody: 'SUN',
  start: 0,
  end: 1,
  peak: 0,
  startIso: '2026-08-01T00:00:00Z',
  endIso: '2026-08-01T01:00:00Z',
  peakIso: '2026-08-01T00:30:00Z',
  durationMinutes: 60,
  peakOrbDeg: 0,
  orbLimitDeg: 1,
  color: '#ffffff',
  occurrenceIndex: null,
  occurrenceCount: 0,
  knownPriorCount: 0,
  knownOccurrenceCount: 0,
  outcome: null,
  returnPct: null,
  reviewed: false,
  reviewStatus: 'none',
  reviewSource: 'none',
  signedPips: null,
  astronomyContract: 'RAMAN_SIDEREAL_SWISSEPH_V1',
  sourceGenerator: 'test-generator',
} as AspectWindow

const audit: ChakraLinkedAuditView = {
  contract: 'SBC_LINKED_AUDIT_VIEW_V1',
  schema_version: 1,
  view_policy: 'LINKED_READ_ONLY_PROGRESSIVE_DISCLOSURE_V1',
  classification: 'SOURCE_PROFILED_EXPERIMENTAL',
  audit_view_id: 'audit-test-0001',
  source_ledger_id: 'ledger-test-0001',
  source_atomic_series_id: 'atomic-test-0001',
  instrument_identity: 'FX:USDJPY',
  range_start_utc: '2026-07-17T06:30:00Z',
  range_end_utc: '2026-07-17T07:30:00Z',
  source_ids: ['witness-test'],
  views: [
    {
      view_id: 'TIMELINE',
      label: 'Timeline',
      purpose: 'Intervals',
      phase_vector_included: false,
      counts_as_independent_vote: false,
      directional_contribution: 0,
    },
    {
      view_id: 'LEDGER',
      label: 'Ledger',
      purpose: 'Dimensions',
      phase_vector_included: false,
      counts_as_independent_vote: false,
      directional_contribution: 0,
    },
    {
      view_id: 'RAY_AUDIT',
      label: 'Ray audit',
      purpose: 'Directions',
      phase_vector_included: false,
      counts_as_independent_vote: false,
      directional_contribution: 0,
    },
    {
      view_id: 'SOURCE_LINEAGE',
      label: 'Lineage',
      purpose: 'Sources',
      phase_vector_included: false,
      counts_as_independent_vote: false,
      directional_contribution: 0,
    },
    {
      view_id: 'RECONCILIATION',
      label: 'Reconciliation',
      purpose: 'Checks',
      phase_vector_included: false,
      counts_as_independent_vote: false,
      directional_contribution: 0,
    },
    {
      view_id: 'VALIDATION',
      label: 'Validation',
      purpose: 'Safety',
      phase_vector_included: false,
      counts_as_independent_vote: false,
      directional_contribution: 0,
    },
  ],
  intervals: [{
    interval_id: 'interval-test-0001',
    interval_ledger_id: 'interval-ledger-test-0001',
    start_utc: '2026-07-17T06:30:00Z',
    end_utc: '2026-07-17T07:30:00Z',
    evidence_cutoff_utc: '2026-07-17T06:30:00Z',
    duration_seconds: 3600,
    cluster_ids: [],
    cell_ids: [],
    duplicate_primary_evidence_count: 0,
    total_summary: {
      favorable_guidance_units: 0,
      adverse_guidance_units: 0,
      net_guidance_units: 0,
      gross_activation_units: 0,
      scored_contribution_count: 0,
      unknown_contribution_count: 0,
      missing_evidence_count: 0,
      total_evidence_count: 0,
      unknown_magnitude_units: 0,
      scoring_coverage_ratio: 0,
    },
    all_axes_reconciled: true,
  }],
  ledger_cells: [],
  ray_rows: [],
  lineage_rows: [],
  reconciliations: [],
  validation_gates: [{
    gate_id: 'EXECUTION_LOCK',
    state: 'PASS',
    label: 'Execution lock',
    detail: 'Market direction and execution remain blocked.',
  }],
  guardrails: {
    read_only: true,
    timestamp_safe: true,
    no_lookahead: true,
    source_profiled_experimental: true,
    financially_validated: false,
    phase_included: false,
    fx_subtraction_included: false,
    confidence_included: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
    execution_allowed: false,
    blocked_capabilities: ['MARKET_DIRECTION', 'MT5_EXECUTION'],
  },
}

const secondInterval = {
  ...audit.intervals[0],
  interval_id: 'interval-test-0002',
  interval_ledger_id: 'interval-ledger-test-0002',
  start_utc: '2026-07-17T07:30:00Z',
  end_utc: '2026-07-17T08:30:00Z',
  evidence_cutoff_utc: '2026-07-17T07:30:00Z',
  total_summary: {
    ...audit.intervals[0].total_summary,
    favorable_guidance_units: 2,
    net_guidance_units: 2,
    gross_activation_units: 2,
    scored_contribution_count: 1,
    total_evidence_count: 1,
    scoring_coverage_ratio: 1,
  },
}

const comparisonAudit: ChakraLinkedAuditView = {
  ...audit,
  audit_view_id: 'audit-test-0002',
  range_end_utc: secondInterval.end_utc,
  intervals: [audit.intervals[0], secondInterval],
}

const phasorVector = {
  interval_id: audit.intervals[0].interval_id,
  cluster_id: 'cluster-test-jupiter',
  source_lineage_id: 'lineage-test-jupiter',
  evidence_kind: 'CONTRIBUTION' as const,
  source_evidence_id: 'contribution-test-jupiter',
  actor_identity: 'JUPITER',
  target_layer: 'RASHI',
  target_value: 'TAURUS',
  signed_guidance_units: 2,
  source_status: 'SCORED',
  unknown_reason: null,
  derivation_role: 'VISUALIZATION_ONLY' as const,
  counts_as_independent_vote: false as const,
  directional_contribution: 0 as const,
  projection_status: 'PLOTTED' as const,
  magnitude_units: 2,
  fixed_angle: 'ZERO' as const,
  fixed_angle_radians: 0,
  real_component_units: 2,
  imaginary_component_units: 0,
  vector_id: 'vector-test-jupiter',
}

const fixedPhasor: ChakraFixedPhasorSeries = {
  contract: 'SBC_FIXED_ZERO_PI_PHASOR_SERIES_V1',
  schema_version: 1,
  projection_policy: 'FIXED_ZERO_PI_SCALAR_PARITY_VISUALIZATION_ONLY_V1',
  classification: 'SOURCE_PROFILED_EXPERIMENTAL',
  projection_series_id: 'phasor-test-0001',
  source_ledger_id: audit.source_ledger_id,
  source_atomic_series_id: audit.source_atomic_series_id,
  instrument_identity: audit.instrument_identity,
  range_start_utc: audit.range_start_utc,
  range_end_utc: audit.range_end_utc,
  source_ids: audit.source_ids,
  field_roles: [{
    field_path: 'intervals[].vectors[]',
    derivation_role: 'VISUALIZATION_ONLY',
    evidence_bearing: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
  }],
  intervals: [{
    interval_id: audit.intervals[0].interval_id,
    interval_ledger_id: audit.intervals[0].interval_ledger_id,
    start_utc: audit.intervals[0].start_utc,
    end_utc: audit.intervals[0].end_utc,
    evidence_cutoff_utc: audit.intervals[0].evidence_cutoff_utc,
    vectors: [
      phasorVector,
      {
        ...phasorVector,
        cluster_id: 'cluster-test-saturn',
        source_lineage_id: 'lineage-test-saturn',
        source_evidence_id: 'contribution-test-saturn',
        actor_identity: 'SATURN',
        signed_guidance_units: -1,
        magnitude_units: 1,
        fixed_angle: 'PI',
        fixed_angle_radians: Math.PI,
        real_component_units: -1,
        vector_id: 'vector-test-saturn',
      },
    ],
    source_favorable_units: 2,
    source_adverse_units: -1,
    source_net_units: 1,
    source_gross_activation_units: 3,
    vector_real_sum_units: 1,
    vector_imaginary_sum_units: 0,
    vector_magnitude_sum_units: 3,
    known_scored_coherence_ratio: 1 / 3,
    plotted_vector_count: 2,
    unknown_vector_count: 0,
    missing_evidence_count: 0,
    real_matches_net: true,
    magnitude_matches_gross: true,
    imaginary_is_zero: true,
    counts_match: true,
    unknowns_preserved: true,
    reconciled: true,
    projection_id: 'phasor-interval-test-0001',
  }],
  validation_gates: [
    {
      gate_id: 'SCALAR_NET_PARITY',
      state: 'PASS',
      label: 'Real-axis scalar parity',
      detail: 'The real sum exactly reproduces P2 net units.',
    },
    {
      gate_id: 'FINANCIAL_VALIDATION',
      state: 'UNKNOWN',
      label: 'Financial validation',
      detail: 'No prospective package is attached.',
    },
  ],
  guardrails: {
    research_only: true,
    read_only: true,
    timestamp_safe: true,
    no_lookahead: true,
    source_profiled_experimental: true,
    scalar_equivalent_only: true,
    fixed_zero_pi_only: true,
    visualization_only: true,
    physical_wave_claimed: false,
    timing_phase_included: false,
    timing_sector_profile_included: false,
    fx_subtraction_included: false,
    confidence_included: false,
    financially_validated: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
    execution_allowed: false,
    blocked_capabilities: ['MARKET_DIRECTION', 'MT5_EXECUTION'],
  },
}

const timingAdmission: ChakraTimingProfileAdmissionReport = {
  contract: 'SBC_TIMING_PROFILE_ADMISSION_REPORT_V1',
  schema_version: 1,
  admission_policy: 'FAIL_CLOSED_SOURCE_REGISTRY_ADMISSION_V1',
  classification: 'SOURCE_PROFILED_EXPERIMENTAL',
  profile_status: 'NO_PROFILE_LOADED',
  profile_id: null,
  profile_version: null,
  candidate_profile_hash: null,
  structural_complete: false,
  source_registry_admitted: false,
  isolated_research_profile_admitted: false,
  directional_engine_implemented: false,
  directional_output_available: false,
  prospective_financial_validation_passed: false,
  financial_use_allowed: false,
  validation_gates: [
    {
      gate_id: 'profile_core',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'Frozen profile contract',
      detail: 'No candidate profile is loaded; this requirement is unknown.',
      missing_paths: ['profile.contract', 'profile.profileId', 'profile.frozen'],
    },
    {
      gate_id: 'server_registry_integrity',
      state: 'PASS',
      mandatory: true,
      label: 'Server-owned profile registry',
      detail: 'Server-owned registry is valid with 0 profile(s).',
      missing_paths: [],
    },
    {
      gate_id: 'directional_engine_presence',
      state: 'UNKNOWN',
      mandatory: false,
      label: 'Directional engine presence',
      detail: 'No directional timing-phase engine is implemented.',
      missing_paths: ['directional_timing_phase_engine'],
    },
  ],
  missing_requirements: [
    'Frozen profile contract',
    'Directional engine presence',
  ],
  guardrails: {
    research_only: true,
    read_only: true,
    candidate_persisted: false,
    profile_values_supplied_by_application: false,
    timing_phase_calculated: false,
    directional_phase_calculated: false,
    confidence_calculated: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
    auto_suggest_included: false,
    live_inference_included: false,
    official_ml_notes_included: false,
    shadow_vote_included: false,
    trade_output_included: false,
    financially_validated: false,
    execution_allowed: false,
    blocked_capabilities: [
      'DIRECTIONAL_TIMING_PHASE',
      'TIMING_CONFIDENCE',
      'AUTO_SUGGEST',
      'LIVE_INFERENCE',
      'MT5_EXECUTION',
    ],
  },
}

const timingSourceReadiness: ChakraTimingProfileSourceReadinessReport = {
  contract: 'SBC_TIMING_PROFILE_SOURCE_READINESS_REPORT_V1',
  schema_version: 1,
  readiness_policy: 'CLAIM_HASH_AND_INDEPENDENT_LINEAGE_READINESS_V1',
  classification: 'SOURCE_PROFILED_EXPERIMENTAL',
  packet_status: 'NO_PACKET_LOADED',
  profile_id: null,
  profile_version: null,
  candidate_profile_hash: null,
  packet_id: null,
  packet_hash: null,
  candidate_structural_complete: false,
  packet_structural_complete: false,
  claim_coverage_complete: false,
  independent_witness_coverage_complete: false,
  conflicts_resolved: false,
  ready_for_external_review: false,
  external_review_completed: false,
  source_certified: false,
  profile_registration_allowed: false,
  validation_gates: [
    {
      gate_id: 'candidate_profile_structure',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'T0 candidate structure',
      detail: 'A structurally complete T0 candidate profile is required.',
      missing_paths: ['candidate_profile'],
    },
    {
      gate_id: 'source_packet_contract',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'Frozen source packet contract',
      detail: 'Required in-memory evidence is not loaded.',
      missing_paths: ['source_packet'],
    },
  ],
  claim_coverage: [
    {
      profile_path: '/phaseSpan',
      claim_class: 'DOCTRINE',
      candidate_value_sha256: null,
      primary_source_count: 0,
      independent_witness_count: 0,
      research_specification_count: 0,
      independent_lineage_count: 0,
      coverage_state: 'UNKNOWN',
      detail: 'Candidate and source packet are both required.',
    },
  ],
  missing_requirements: [
    'T0 candidate structure',
    'Frozen source packet contract',
  ],
  guardrails: {
    research_only: true,
    read_only: true,
    candidate_persisted: false,
    packet_persisted: false,
    source_bytes_verified_by_application: false,
    external_review_completed: false,
    source_certified: false,
    profile_registration_allowed: false,
    timing_phase_calculated: false,
    directional_phase_calculated: false,
    confidence_calculated: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
    auto_suggest_included: false,
    live_inference_included: false,
    official_ml_notes_included: false,
    shadow_vote_included: false,
    trade_output_included: false,
    financially_validated: false,
    execution_allowed: false,
    blocked_capabilities: [
      'SOURCE_CERTIFICATION',
      'TIMING_PROFILE_REGISTRATION',
      'DIRECTIONAL_TIMING_PHASE',
      'MT5_EXECUTION',
    ],
  },
}

const timingSourceVerification: ChakraTimingProfileSourceVerificationReport = {
  contract: 'SBC_TIMING_PROFILE_SOURCE_BYTE_VERIFICATION_REPORT_V1',
  schema_version: 1,
  verification_policy: 'EXACT_SOURCE_BYTES_AND_UTF8_EXCERPT_PAYLOADS_V1',
  classification: 'SOURCE_PROFILED_EXPERIMENTAL',
  verification_status: 'NO_VERIFICATION_PAYLOAD',
  profile_id: null,
  profile_version: null,
  candidate_profile_hash: null,
  packet_id: null,
  packet_hash: null,
  s1_ready_for_external_review: false,
  all_source_bytes_verified: false,
  all_excerpt_payloads_verified: false,
  ready_for_independent_review: false,
  source_artifact_checks: [],
  excerpt_payload_checks: [],
  validation_gates: [
    {
      gate_id: 's1_packet_readiness',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'S1 packet readiness',
      detail: 'A T0 candidate and S1 source packet are required.',
      missing_ids: ['candidate_profile', 'source_packet'],
    },
    {
      gate_id: 'exact_source_bytes',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'Exact source bytes',
      detail: 'A source packet is required before source bytes can be checked.',
      missing_ids: [],
    },
    {
      gate_id: 'exact_excerpt_payloads',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'Exact UTF-8 excerpt payloads',
      detail: 'A source packet is required before excerpts can be checked.',
      missing_ids: [],
    },
    {
      gate_id: 'review_bundle_guardrails',
      state: 'PASS',
      mandatory: true,
      label: 'Independent-review bundle guardrails',
      detail: 'Bundle cannot certify or execute.',
      missing_ids: [],
    },
  ],
  missing_requirements: [
    'S1 packet readiness',
    'Exact source bytes',
    'Exact UTF-8 excerpt payloads',
  ],
  review_bundle: null,
  review_bundle_sha256: null,
  external_review_completed: false,
  source_certified: false,
  profile_registration_allowed: false,
  guardrails: {
    research_only: true,
    read_only: true,
    payloads_persisted: false,
    source_bytes_included_in_bundle: false,
    excerpt_text_included_in_bundle: false,
    page_presence_checked: false,
    doctrine_correctness_checked: false,
    external_review_completed: false,
    source_certified: false,
    profile_registration_allowed: false,
    registry_write_allowed: false,
    timing_phase_calculated: false,
    directional_phase_calculated: false,
    confidence_calculated: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
    auto_suggest_included: false,
    live_inference_included: false,
    official_ml_notes_included: false,
    shadow_vote_included: false,
    trade_output_included: false,
    financially_validated: false,
    execution_allowed: false,
    blocked_capabilities: [
      'PAGE_CITATION_VERIFICATION',
      'DOCTRINE_CORRECTNESS_REVIEW',
      'SOURCE_CERTIFICATION',
      'MT5_EXECUTION',
    ],
  },
}

const timingExternalReview: ChakraTimingProfileExternalReviewReport = {
  contract: 'SBC_TIMING_PROFILE_EXTERNAL_REVIEW_REPORT_V1',
  schema_version: 1,
  review_policy: 'INTERNAL_COHERENCE_AND_EXACT_DECISION_COVERAGE_V1',
  classification: 'SOURCE_PROFILED_EXPERIMENTAL',
  review_status: 'NO_ATTESTATION',
  profile_id: null,
  profile_version: null,
  candidate_profile_hash: null,
  packet_id: null,
  packet_hash: null,
  review_bundle_sha256: null,
  attestation_sha256: null,
  bundle_integrity_verified: false,
  embedded_s1_ready: false,
  s2_rows_verified: false,
  attestation_complete: false,
  review_approved: false,
  ready_for_human_certification_decision: false,
  validation_gates: [
    {
      gate_id: 'review_bundle_integrity',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'Review bundle integrity',
      detail: 'A complete S2 review bundle is required.',
      affected_ids: ['review_bundle'],
    },
    {
      gate_id: 'reviewer_attestation',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'Completed reviewer attestation',
      detail: 'A completed attestation is required.',
      affected_ids: ['attestation'],
    },
  ],
  missing_requirements: [
    'Review bundle integrity',
    'Completed reviewer attestation',
  ],
  certification_proposal: null,
  certification_proposal_sha256: null,
  reviewer_identity_authenticated: false,
  external_review_independently_proven: false,
  source_certified: false,
  profile_registered: false,
  registry_write_allowed: false,
  guardrails: {
    research_only: true,
    read_only: true,
    payloads_persisted: false,
    reviewer_identity_authenticated: false,
    reviewer_independence_authenticated: false,
    external_review_independently_proven: false,
    source_certified: false,
    profile_registered: false,
    registry_write_allowed: false,
    timing_phase_calculated: false,
    directional_phase_calculated: false,
    confidence_calculated: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
    auto_suggest_included: false,
    live_inference_included: false,
    official_ml_notes_included: false,
    shadow_vote_included: false,
    trade_output_included: false,
    financially_validated: false,
    execution_allowed: false,
    blocked_capabilities: [
      'REVIEWER_IDENTITY_AUTHENTICATION',
      'SOURCE_CERTIFICATION',
      'TIMING_PROFILE_REGISTRATION',
      'MT5_EXECUTION',
    ],
  },
}

const timingSignedReview: ChakraTimingProfileSignedReviewReport = {
  contract: 'SBC_TIMING_PROFILE_SIGNED_REVIEW_REPORT_V1',
  schema_version: 1,
  signature_policy: 'ED25519_SERVER_TRUST_REGISTRY_EXACT_S3_BINDING_V1',
  classification: 'SOURCE_PROFILED_EXPERIMENTAL',
  review_status: 'S3_NOT_READY',
  profile_id: null,
  profile_version: null,
  candidate_profile_hash: null,
  packet_id: null,
  packet_hash: null,
  review_bundle_sha256: null,
  attestation_sha256: null,
  certification_proposal_sha256: null,
  signed_review_sha256: null,
  s3_ready: false,
  reviewer_registry_valid: true,
  reviewer_key_trusted: false,
  review_signature_valid: false,
  reviewer_identity_authenticated_to_registry: false,
  reviewer_independence_administratively_vetted: false,
  ready_for_manual_source_certification: false,
  validation_gates: [
    {
      gate_id: 's3_external_review',
      state: 'FAIL',
      mandatory: true,
      label: 'S3 external-review evidence',
      detail: 'S3 must pass before signature verification.',
    },
    {
      gate_id: 'trusted_reviewer_key',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'Trusted reviewer key and scope',
      detail: 'A valid signed-review binding is required.',
    },
  ],
  missing_requirements: [
    'S3 external-review evidence',
    'Trusted reviewer key and scope',
  ],
  signed_review_template: null,
  external_review_independently_proven: false,
  source_certified: false,
  profile_registered: false,
  registry_write_allowed: false,
  guardrails: {
    research_only: true,
    read_only: true,
    payloads_persisted: false,
    client_public_key_accepted: false,
    server_trust_registry_required: true,
    signature_proves_registered_key_binding_only: true,
    reviewer_independence_cryptographically_proven: false,
    external_review_independently_proven: false,
    source_certified: false,
    profile_registered: false,
    registry_write_allowed: false,
    timing_phase_calculated: false,
    directional_phase_calculated: false,
    confidence_calculated: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
    auto_suggest_included: false,
    live_inference_included: false,
    official_ml_notes_included: false,
    shadow_vote_included: false,
    trade_output_included: false,
    financially_validated: false,
    execution_allowed: false,
    blocked_capabilities: [
      'INDEPENDENCE_PROOF',
      'SOURCE_CERTIFICATION',
      'TIMING_PROFILE_REGISTRATION',
      'MT5_EXECUTION',
    ],
  },
}

const timingSourceCertification:
ChakraTimingProfileSourceCertificationReport = {
  contract: 'SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_REPORT_V1',
  schema_version: 1,
  certification_policy: 'ED25519_SEPARATE_AUTHORITY_EXACT_S4_BINDING_V1',
  classification: 'SOURCE_PROFILED_EXPERIMENTAL',
  certification_status: 'S4_NOT_READY',
  profile_id: null,
  profile_version: null,
  candidate_profile_hash: null,
  packet_id: null,
  packet_hash: null,
  review_bundle_sha256: null,
  attestation_sha256: null,
  certification_proposal_sha256: null,
  signed_review_sha256: null,
  source_certificate_sha256: null,
  registry_admission_proposal_sha256: null,
  s4_ready: false,
  authority_registry_valid: true,
  authority_key_trusted: false,
  certificate_signature_valid: false,
  separation_of_duties_vetted: false,
  certification_decision: null,
  source_certified: false,
  ready_for_profile_registry_admission: false,
  validation_gates: [
    {
      gate_id: 's4_signed_review',
      state: 'FAIL',
      mandatory: true,
      label: 'S4 signed-review evidence',
      detail: 'S4 must pass before source certification.',
    },
    {
      gate_id: 'trusted_certification_authority',
      state: 'UNKNOWN',
      mandatory: true,
      label: 'Trusted certification authority',
      detail: 'A valid source-certificate binding is required.',
    },
  ],
  missing_requirements: [
    'S4 signed-review evidence',
    'Trusted certification authority',
  ],
  source_certificate_template: null,
  registry_entry_proposal: null,
  profile_registered: false,
  registry_write_allowed: false,
  guardrails: {
    research_only: true,
    read_only: true,
    payloads_persisted: false,
    client_public_key_accepted: false,
    server_authority_registry_required: true,
    separate_authority_required: true,
    certificate_records_governance_decision_only: true,
    doctrinal_truth_cryptographically_proven: false,
    profile_registered: false,
    registry_write_allowed: false,
    timing_phase_calculated: false,
    directional_phase_calculated: false,
    confidence_calculated: false,
    counts_as_independent_vote: false,
    directional_contribution: 0,
    auto_suggest_included: false,
    live_inference_included: false,
    official_ml_notes_included: false,
    shadow_vote_included: false,
    trade_output_included: false,
    financially_validated: false,
    execution_allowed: false,
    blocked_capabilities: [
      'TIMING_PROFILE_REGISTRATION',
      'DIRECTIONAL_TIMING_PHASE',
      'MT5_EXECUTION',
    ],
  },
}

const comparisonFixedPhasor: ChakraFixedPhasorSeries = {
  ...fixedPhasor,
  range_end_utc: comparisonAudit.range_end_utc,
  intervals: [
    ...fixedPhasor.intervals,
    {
      ...fixedPhasor.intervals[0],
      interval_id: secondInterval.interval_id,
      interval_ledger_id: secondInterval.interval_ledger_id,
      start_utc: secondInterval.start_utc,
      end_utc: secondInterval.end_utc,
      evidence_cutoff_utc: secondInterval.evidence_cutoff_utc,
      vectors: [{
        ...phasorVector,
        interval_id: secondInterval.interval_id,
        vector_id: 'vector-test-jupiter-interval-2',
      }],
      source_favorable_units: 2,
      source_adverse_units: 0,
      source_net_units: 2,
      source_gross_activation_units: 2,
      vector_real_sum_units: 2,
      vector_magnitude_sum_units: 2,
      known_scored_coherence_ratio: 1,
      plotted_vector_count: 1,
      projection_id: 'phasor-interval-test-0002',
    },
  ],
}

const auditPackageBuild: ChakraAuditPackageBuild = {
  package: {
    contract: 'SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1',
    schema_version: 1,
    package_policy: 'READ_ONLY_COMPARISON_EXPORT_REPLAY_V1',
    classification: 'SOURCE_PROFILED_EXPERIMENTAL',
    package_id: 'package-test-0001',
    source_audit_id: comparisonAudit.audit_view_id,
    source_projection_hash: 'projection-test-0001',
    instrument_identity: 'FX:USDJPY',
    sealed_at_utc: '2026-07-17T09:30:00Z',
    replay_recipe_hash: 'recipe-test-0001',
    replay_recipe: {},
    source_audit: comparisonAudit,
    comparisons: [{
      comparison_id: 'comparison-test-0001',
      baseline_interval_id: audit.intervals[0].interval_id,
      comparison_interval_id: secondInterval.interval_id,
      baseline_summary: audit.intervals[0].total_summary,
      comparison_summary: secondInterval.total_summary,
      total_delta: {
        favorable_guidance_units: 2,
        adverse_guidance_units: 0,
        net_guidance_units: 2,
        gross_activation_units: 2,
        scored_contribution_count: 1,
        unknown_contribution_count: 0,
        missing_evidence_count: 0,
        total_evidence_count: 1,
        unknown_magnitude_units: 0,
        scoring_coverage_ratio: 1,
        derivation_role: 'DESCRIPTIVE_COMPARISON_ONLY',
        counts_as_independent_vote: false,
        directional_contribution: 0,
      },
      cell_comparisons: [],
      shared_source_lineage_ids: [],
      baseline_only_source_lineage_ids: [],
      comparison_only_source_lineage_ids: [],
      interpretation: 'Descriptive only.',
      derivation_role: 'DESCRIPTIVE_COMPARISON_ONLY',
      counts_as_independent_vote: false,
      directional_contribution: 0,
    }],
    bookmarks: [{
      bookmark_id: 'bookmark-test-0001',
      target_type: 'INTERVAL',
      target_id: audit.intervals[0].interval_id,
      label: 'Manual contrast',
      note: 'Research observation only.',
      created_at_utc: '2026-07-17T09:00:00Z',
      annotation_role: 'MANUAL_RESEARCH_ANNOTATION_ONLY',
      counts_as_evidence: false,
      official_ml_note: false,
      directional_contribution: 0,
    }],
    validation_gates: [{
      gate_id: 'EXECUTION_LOCK',
      state: 'PASS',
      label: 'Execution lock',
      detail: 'Inference and execution remain blocked.',
    }],
    guardrails: {
      research_only: true,
      read_only: true,
      timestamp_safe: true,
      no_lookahead: true,
      source_profiled_experimental: true,
      financially_validated: false,
      descriptive_comparison_only: true,
      manual_annotations_only: true,
      replay_required_for_verification: true,
      phase_included: false,
      fx_subtraction_included: false,
      confidence_included: false,
      counts_as_independent_vote: false,
      directional_contribution: 0,
      execution_allowed: false,
      blocked_capabilities: ['MARKET_DIRECTION', 'MT5_EXECUTION'],
    },
  },
  htmlReport: '<!doctype html><title>SBC audit</title>',
}

const packageVerification: ChakraAuditPackageVerification = {
  contract: 'SBC_AUDIT_PACKAGE_VERIFICATION_V1',
  state: 'PASS',
  package_id: auditPackageBuild.package.package_id,
  source_audit_id: comparisonAudit.audit_view_id,
  structural_hash_match: true,
  source_projection_match: true,
  replay_recipe_match: true,
  replay_audit_match: true,
  replay_package_match: true,
  errors: [],
}

const catalogBuild: ChakraAuditCatalogBuild = {
  bundle: {
    contract: 'SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1',
    schema_version: 1,
    bundle_policy: 'SIGNED_PORTABLE_RESEARCH_EXCHANGE_V1',
    catalog: {
      contract: 'SBC_AUDIT_PACKAGE_CATALOG_V1',
      schema_version: 1,
      catalog_policy: 'SEALED_PACKAGE_CATALOG_NO_CROSS_AUDIT_INFERENCE_V1',
      classification: 'SOURCE_PROFILED_EXPERIMENTAL',
      catalog_id: 'catalog-test-0001',
      created_at_utc: '2026-07-17T10:00:00Z',
      entries: [{
        entry_id: 'entry-test-0001',
        package_id: auditPackageBuild.package.package_id,
        package_digest: 'package-digest-test',
        source_audit_id: auditPackageBuild.package.source_audit_id,
        instrument_identity: auditPackageBuild.package.instrument_identity,
        sealed_at_utc: auditPackageBuild.package.sealed_at_utc,
        p4_replay_state: 'PASS',
        package: auditPackageBuild.package,
      }],
      validation_gates: [{
        gate_id: 'CROSS_PACKAGE_INFERENCE',
        state: 'UNKNOWN',
        label: 'Cross-package inference',
        detail: 'No arithmetic, voting, direction, or execution is permitted.',
      }],
      guardrails: {
        research_only: true,
        read_only: true,
        timestamp_safe: true,
        no_lookahead: true,
        source_profiled_experimental: true,
        financially_validated: false,
        catalog_only: true,
        embedded_p4_replay_required: true,
        no_cross_package_arithmetic: true,
        no_cross_package_voting: true,
        no_market_direction: true,
        no_confidence_output: true,
        signatures_prove_integrity_only: true,
        counts_as_independent_vote: false,
        directional_contribution: 0,
        execution_allowed: false,
        blocked_capabilities: ['CROSS_AUDIT_ARITHMETIC', 'MT5_EXECUTION'],
      },
    },
    signature: {
      contract: 'SBC_AUDIT_CATALOG_SIGNATURE_V1',
      schema_version: 1,
      algorithm: 'ED25519',
      key_id: 'key-test-0001',
      public_key_base64: 'public-key',
      catalog_id: 'catalog-test-0001',
      catalog_digest: 'catalog-digest-test',
      signed_at_utc: '2026-07-17T10:01:00Z',
      signature_base64: 'signature',
    },
  },
  verification: {
    contract: 'SBC_AUDIT_CATALOG_VERIFICATION_V1',
    state: 'PASS',
    catalog_id: 'catalog-test-0001',
    key_id: 'key-test-0001',
    catalog_hash_match: true,
    signature_valid: true,
    embedded_packages_valid: true,
    semantic_replay_state: 'PASS',
    entry_count: 1,
    entry_verifications: [{
      package_id: auditPackageBuild.package.package_id,
      structural_integrity: 'PASS',
      semantic_replay: 'PASS',
      errors: [],
    }],
    errors: [],
  },
  signingIdentity: {
    algorithm: 'ED25519',
    keyId: 'key-test-0001',
    storage: 'WINDOWS_DPAPI_APP_DATA',
    claim: 'Integrity only.',
  },
}

describe('ChakraLabWorkspace', () => {
  it('renders source-profiled guidance without trading direction labels', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalledTimes(1))
    await user.click(screen.getByRole('tab', { name: 'Board' }))
    expect(await screen.findByText('chakra-test-')).toBeInTheDocument()
    expect(screen.getByText('Guidance ledger')).toBeInTheDocument()
    expect(screen.getByText('Not financially validated')).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('converts a spoken English ticker initial and applies the reviewed key', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Board' }))
    await user.click(screen.getByText('English stock key converter'))
    await user.type(screen.getByPlaceholderText('USDJPY or AAPL'), 'USD')

    expect(screen.getByText('यू-एस-डी')).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'NAME_INITIAL · YA · य' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Use selected key' }))
    expect(screen.getByLabelText('Name-initial keys')).toHaveValue('YA')
  })

  it('opens the integrated workspace as the founder-facing default', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchAspectPolarity.mockResolvedValue(missingAspectPolarity)

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await screen.findByText('Integrated SBC workspace')
    expect(screen.getByText('Why this state')).toBeInTheDocument()
    expect(screen.getByText('Read-only experimental')).toBeInTheDocument()
    expect(await screen.findByText('Chart-conditioned aspect pressure')).toBeInTheDocument()
    expect(screen.getByText('USD: Polarity Catalogue Missing')).toBeInTheDocument()
    expect(screen.getByText('JPY: Polarity Catalogue Missing')).toBeInTheDocument()
    expect(screen.getByText(/No sign is inferred from transit geometry/i)).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('shows synchronized time and profile context without creating a market call', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await screen.findByText('Integrated SBC workspace')
    await user.click(screen.getByRole('button', { name: 'Time' }))
    expect(screen.getByText('Selected time')).toBeInTheDocument()
    expect(screen.getByLabelText('Selected IST moment')).toBeInTheDocument()
    expect(screen.getByText('Saptami')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Profile' }))
    expect(screen.getByText('Current profile')).toBeInTheDocument()
    expect(screen.getByText(/This workspace reports the loaded profile context only/i)).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('shows existing USDJPY relative arithmetic as descriptive context only', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
        currencyPairEvidence={currencyPairEvidence}
        selectedAspectLabel="MOON to MARS Square"
      />,
    )

    await screen.findByText('USDJPY relative context')
    expect(screen.getByText('Pair net difference')).toBeInTheDocument()
    expect(screen.getByText('Common activation')).toBeInTheDocument()
    expect(screen.getByText(/not a price prediction/i)).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('opens the fixed real-axis wheel as a visualization-only display', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchFixedPhasor.mockResolvedValue(fixedPhasor)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await screen.findByText('Integrated SBC workspace')
    await user.click(screen.getByRole('button', { name: 'Wheel' }))
    expect(await screen.findByText('Fixed real-axis phasor wheel')).toBeInTheDocument()
    expect(fetchFixedPhasor).toHaveBeenCalledTimes(1)
    expect(screen.getByText(/not timing phase, a vote, or a price signal/i)).toBeInTheDocument()
    expect(screen.getByText('JUPITER')).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('resolves independent USD and JPY primary chart identities', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchAspectPolarity.mockResolvedValue(missingAspectPolarity)

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
        chart={{ symbol: 'USDJPY', candles: [] } as unknown as import('./types').ChartPayload}
        selectedAspect={selectedAspect}
      />,
    )

    await waitFor(() => expect(fetchAspectPolarity).toHaveBeenCalledWith({ instrumentIdentity: 'FX_CURRENCY:USD' }))
    expect(fetchAspectPolarity).toHaveBeenCalledWith({ instrumentIdentity: 'FX_CURRENCY:JPY' })
    expect(await screen.findByText('Side-chart evidence packet readiness')).toBeInTheDocument()
    expect(screen.getByText(/MARS to SUN Square/i)).toBeInTheDocument()
  })

  it('keeps fixed-wheel vector selection keyboard reachable and non-directional', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchFixedPhasor.mockResolvedValue(fixedPhasor)
    const user = userEvent.setup()

    render(<ChakraLabWorkspace defaultLatitude={18.5204} defaultLongitude={73.8567} />)

    await screen.findByText('Integrated SBC workspace')
    await user.click(screen.getByRole('button', { name: 'Wheel' }))
    const saturn = await screen.findByRole('button', { name: /^SATURN/ })
    saturn.focus()
    await user.keyboard(' ')
    expect(saturn).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText('Pi / left')).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('keeps the timing phase lab disabled until a dedicated build opts in', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await screen.findByText('Integrated SBC workspace')
    const phaseLab = screen.getByRole('button', { name: 'Phase lab' })
    expect(phaseLab).toBeDisabled()
    await user.click(phaseLab)
    expect(screen.queryByText('Timing phase lab')).not.toBeInTheDocument()
  })

  it('compares scalar, fixed, and timing states at one pinned moment without replacing the scalar baseline', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchFixedPhasor.mockResolvedValue(fixedPhasor)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await screen.findByText('Integrated SBC workspace')
    await user.click(screen.getByRole('button', { name: 'Compare' }))
    expect(await screen.findByText('Three-model comparison')).toBeInTheDocument()
    expect(screen.getByText('Scalar SBC baseline')).toBeInTheDocument()
    expect(screen.getByText('Fixed 0/pi wheel')).toBeInTheDocument()
    expect(screen.getByText('Timing phase lab')).toBeInTheDocument()
    expect(screen.getByText(/no future market data is read/i)).toBeInTheDocument()
    expect(screen.getAllByText('ABSTAIN').length).toBeGreaterThan(0)
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('captures explicit moments and opens the linked read-only audit', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchAudit.mockResolvedValue(audit)
    fetchFixedPhasor.mockResolvedValue(fixedPhasor)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Audit' }))
    expect(screen.getByText('Linked audit not compiled')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Capture boundary' }))
    await user.click(screen.getByRole('button', { name: 'Compile linked audit' }))

    await waitFor(() => expect(fetchAudit).toHaveBeenCalledTimes(1))
    expect(fetchFixedPhasor).toHaveBeenCalledTimes(1)
    expect(fetchAudit).toHaveBeenCalledWith(expect.objectContaining({
      instrumentIdentity: 'FX:USDJPY',
      boundaries: [expect.objectContaining({
        reason: 'manual review boundary',
      })],
    }))
    expect(await screen.findByText('1h 0m')).toBeInTheDocument()
    await user.click(screen.getByRole('tab', { name: 'Validation' }))
    expect(screen.getByText('Execution lock')).toBeInTheDocument()
    expect(screen.getByText('No phase')).toBeInTheDocument()
    await user.click(screen.getByRole('tab', { name: 'Fixed phasor' }))
    expect(screen.getByText(/Fixed 0\/pi scalar encoding only/)).toBeInTheDocument()
    expect(screen.getByText('Real-axis scalar parity')).toBeInTheDocument()
    expect(screen.getByText('JUPITER')).toBeInTheDocument()
    expect(screen.getByText('SATURN')).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('shows the fail-closed timing-profile admission gate without an audit', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchTimingAdmission.mockResolvedValue(timingAdmission)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Audit' }))
    await user.click(screen.getByRole('tab', { name: 'Timing gate' }))

    await waitFor(() => expect(fetchTimingAdmission).toHaveBeenCalledWith(null))
    expect(
      screen.getByText(/Admission check only/),
    ).toBeInTheDocument()
    expect(screen.getByText('No Profile Loaded')).toBeInTheDocument()
    expect(screen.getByText('Server-owned profile registry')).toBeInTheDocument()
    expect(screen.getByText('Directional engine presence')).toBeInTheDocument()
    expect(screen.getByText('LOCKED')).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('shows source packet readiness without claiming certification', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchTimingSourceReadiness.mockResolvedValue(timingSourceReadiness)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Audit' }))
    const sourcePacketTab = screen.getByRole('tab', { name: 'Source packet' })
    await user.click(sourcePacketTab)

    await waitFor(() => (
      expect(fetchTimingSourceReadiness).toHaveBeenCalledWith(null, null)
    ))
    await waitFor(() => (
      expect(sourcePacketTab).toHaveAttribute('aria-selected', 'true')
    ))
    expect(await screen.findByText(/Readiness check only/)).toBeInTheDocument()
    expect(await screen.findByText('No Packet Loaded')).toBeInTheDocument()
    expect(screen.getByText('T0 candidate structure')).toBeInTheDocument()
    expect(screen.getByText('Frozen source packet contract')).toBeInTheDocument()
    expect(screen.getAllByText('Source Certification').length).toBeGreaterThan(0)
    expect(screen.getAllByText('BLOCKED').length).toBeGreaterThan(0)
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('keeps source-byte verification separate from certification', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchTimingSourceVerification.mockResolvedValue(timingSourceVerification)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Audit' }))
    const verifyTab = screen.getByRole('tab', { name: 'Verify sources' })
    await user.click(verifyTab)

    await waitFor(() => (
      expect(fetchTimingSourceVerification).toHaveBeenCalledWith(
        null,
        null,
        null,
        null,
      )
    ))
    expect(await screen.findByText(/S2 hashes exact local source bytes/))
      .toBeInTheDocument()
    expect(screen.getByText('Frozen source packet required')).toBeInTheDocument()
    expect(screen.getByText('S1 packet readiness')).toBeInTheDocument()
    expect(screen.getByText('Independent-review bundle guardrails'))
      .toBeInTheDocument()
    expect(screen.getAllByText('UNKNOWN').length).toBeGreaterThan(0)
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('keeps external-review verification under human certification control', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchTimingExternalReview.mockResolvedValue(timingExternalReview)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Audit' }))
    const reviewTab = screen.getByRole('tab', { name: 'Review attestation' })
    await user.click(reviewTab)

    await waitFor(() => (
      expect(fetchTimingExternalReview).toHaveBeenCalledWith(null, null)
    ))
    expect(await screen.findByText(/S3 checks the internal integrity/))
      .toBeInTheDocument()
    expect(screen.getByText('Reviewer identity not authenticated'))
      .toBeInTheDocument()
    expect(screen.getByText('Review bundle integrity')).toBeInTheDocument()
    expect(screen.getByText('Completed reviewer attestation')).toBeInTheDocument()
    expect(screen.getAllByText('BLOCKED').length).toBeGreaterThan(0)
    expect(screen.getByText('LOCKED')).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('keeps trusted reviewer signatures separate from certification', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchTimingSignedReview.mockResolvedValue(timingSignedReview)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Audit' }))
    await user.click(screen.getByRole('tab', { name: 'Signed review' }))

    await waitFor(() => (
      expect(fetchTimingSignedReview).toHaveBeenCalledWith(null, null, null)
    ))
    expect(await screen.findByText(/S4 verifies an Ed25519 signature/))
      .toBeInTheDocument()
    expect(screen.getByText('S3 external-review evidence')).toBeInTheDocument()
    expect(screen.getByText('Trusted reviewer key and scope')).toBeInTheDocument()
    expect(screen.getByText(/Signature identity is narrower/))
      .toBeInTheDocument()
    expect(screen.getAllByText('LOCKED').length).toBeGreaterThan(0)
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('keeps source certification separate from registry admission', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchTimingSourceCertification.mockResolvedValue(
      timingSourceCertification,
    )
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Audit' }))
    await user.click(screen.getByRole('tab', { name: 'Source certificate' }))

    await waitFor(() => (
      expect(fetchTimingSourceCertification).toHaveBeenCalledWith(
        null,
        null,
        null,
        null,
      )
    ))
    expect(await screen.findByText(/S5 verifies a separate authority signature/))
      .toBeInTheDocument()
    expect(screen.getByText('S4 signed-review evidence')).toBeInTheDocument()
    expect(screen.getByText('Trusted certification authority'))
      .toBeInTheDocument()
    expect(screen.getByText(/Certification is a signed governance decision/))
      .toBeInTheDocument()
    expect(screen.getAllByText('LOCKED').length).toBeGreaterThan(0)
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })

  it('builds a descriptive P4 package with bookmarks and verifies full replay', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchAudit.mockResolvedValue(comparisonAudit)
    fetchFixedPhasor.mockResolvedValue(comparisonFixedPhasor)
    buildAuditPackage.mockResolvedValue(auditPackageBuild)
    verifyAuditPackage.mockResolvedValue(packageVerification)
    buildAuditCatalog.mockResolvedValue(catalogBuild)
    verifyAuditCatalog.mockResolvedValue(catalogBuild.verification)
    const user = userEvent.setup()

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: 'Audit' }))
    const boundaryMoment = screen.getByLabelText('Boundary moment (IST)')
    await user.clear(boundaryMoment)
    await user.type(boundaryMoment, '2026-07-28T21:00')
    await user.click(screen.getByRole('button', { name: 'Capture boundary' }))
    await user.clear(boundaryMoment)
    await user.type(boundaryMoment, '2026-07-28T22:00')
    await user.click(screen.getByRole('button', { name: 'Capture boundary' }))
    await user.click(screen.getByRole('button', { name: 'Compile linked audit' }))
    await waitFor(() => expect(fetchAudit).toHaveBeenCalledTimes(1))
    expect(fetchAudit).toHaveBeenCalledWith(expect.objectContaining({
      boundaries: [
        expect.objectContaining({
          request: expect.objectContaining({ at: '2026-07-28T21:00:00+05:30' }),
        }),
        expect.objectContaining({
          request: expect.objectContaining({ at: '2026-07-28T22:00:00+05:30' }),
        }),
      ],
    }))

    await user.type(screen.getByPlaceholderText('Bookmark label'), 'Manual contrast')
    await user.type(
      screen.getByPlaceholderText('Manual observation only'),
      'Research observation only.',
    )
    await user.click(screen.getByRole('button', { name: 'Add bookmark' }))
    await user.click(screen.getByRole('button', { name: 'Build sealed package' }))

    await waitFor(() => expect(buildAuditPackage).toHaveBeenCalledTimes(1))
    expect(buildAuditPackage).toHaveBeenCalledWith(expect.objectContaining({
      baselineIntervalId: audit.intervals[0].interval_id,
      comparisonIntervalIds: [secondInterval.interval_id],
      bookmarks: [expect.objectContaining({
        targetType: 'INTERVAL',
        label: '[SOURCE_ONLY_BASELINE] Manual contrast',
        note: expect.stringContaining('approval=FOUNDER_APPROVAL_PENDING'),
      })],
    }))
    expect(screen.getByText(/Candidate minus baseline/)).toBeInTheDocument()

    await user.click(screen.getByRole('tab', { name: 'Package' }))
    await user.click(screen.getByRole('button', { name: 'Replay verify' }))
    await waitFor(() => expect(verifyAuditPackage).toHaveBeenCalledTimes(1))
    expect(
      screen.getByText('Full Chakra to P1 to P2 to P3 to P4 replay matched'),
    ).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Add verified P4' }))
    await user.click(screen.getByRole('button', { name: 'Seal and sign catalog' }))
    await waitFor(() => expect(buildAuditCatalog).toHaveBeenCalledTimes(1))
    expect(buildAuditCatalog).toHaveBeenCalledWith(expect.objectContaining({
      packages: [auditPackageBuild.package],
    }))
    expect(screen.getByText('Signed P5 audit catalog')).toBeInTheDocument()
    expect(
      screen.getByText(/Packages are not added, averaged, voted, ranked/),
    ).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Integrity' }))
    await waitFor(() => expect(verifyAuditCatalog).toHaveBeenCalledWith(
      catalogBuild.bundle,
      false,
    ))
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  }, 20_000)
})
