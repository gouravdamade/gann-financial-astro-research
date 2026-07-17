// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { ChakraLabSnapshot } from './types'
import { ChakraLabWorkspace } from './views/ChakraLabWorkspace'

const { fetchSnapshot } = vi.hoisted(() => ({
  fetchSnapshot: vi.fn(),
}))

vi.mock('./api', () => ({
  fetchChakraLabSnapshot: fetchSnapshot,
}))

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
})
