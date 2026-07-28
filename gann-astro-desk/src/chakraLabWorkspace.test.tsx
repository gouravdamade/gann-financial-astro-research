// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ChakraLabSnapshot, ChakraLinkedAuditView } from './types'
import { ChakraLabWorkspace } from './views/ChakraLabWorkspace'

const { fetchAudit, fetchSnapshot } = vi.hoisted(() => ({
  fetchAudit: vi.fn(),
  fetchSnapshot: vi.fn(),
}))

vi.mock('./api', () => ({
  fetchChakraLabAudit: fetchAudit,
  fetchChakraLabSnapshot: fetchSnapshot,
}))

afterEach(() => {
  cleanup()
  fetchAudit.mockReset()
  fetchSnapshot.mockReset()
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

describe('ChakraLabWorkspace', () => {
  it('renders source-profiled guidance without trading direction labels', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)

    render(
      <ChakraLabWorkspace
        defaultLatitude={18.5204}
        defaultLongitude={73.8567}
      />,
    )

    await waitFor(() => expect(fetchSnapshot).toHaveBeenCalledTimes(1))
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
    await user.click(screen.getByText('English stock key converter'))
    await user.type(screen.getByPlaceholderText('USDJPY or AAPL'), 'USD')

    expect(screen.getByText('यू-एस-डी')).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'NAME_INITIAL · YA · य' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Use selected key' }))
    expect(screen.getByLabelText('Name-initial keys')).toHaveValue('YA')
  })

  it('captures explicit moments and opens the linked read-only audit', async () => {
    fetchSnapshot.mockResolvedValue(snapshot)
    fetchAudit.mockResolvedValue(audit)
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
    await user.click(screen.getByRole('button', { name: 'Capture current moment' }))
    await user.click(screen.getByRole('button', { name: 'Compile linked audit' }))

    await waitFor(() => expect(fetchAudit).toHaveBeenCalledTimes(1))
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
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
  })
})
