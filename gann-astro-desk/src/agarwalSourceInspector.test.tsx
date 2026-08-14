// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { AgarwalSourceProfile, SbcSourceProfileId } from './types'
import { AgarwalSourceInspectorWorkspace } from './views/AgarwalSourceInspectorWorkspace'

const { fetchProfile } = vi.hoisted(() => ({ fetchProfile: vi.fn() }))

vi.mock('./api', () => ({ fetchAgarwalSourceProfile: fetchProfile }))

afterEach(() => {
  cleanup()
  fetchProfile.mockReset()
})

const cells = Array.from({ length: 81 }, (_, index) => {
  const row = Math.floor(index / 9) + 1
  const column = (index % 9) + 1
  return {
    coordinate: { row, column, label: `${row}:${column}` },
    literal: index === 1 ? 'KRITT-IKA' : `SOURCE-${index + 1}`,
    normalizedLabel: null,
    vargaNumber: index + 1,
    layer: index % 5 === 0 ? 'star' : 'sign',
    sourceProfile: 'AGARWAL_MYSTICS_SAGAR_FIRST_EDITION_2000_HARDCOPY',
    printedPage: 145,
    evidencePacketId: 'AGARWAL_2000_PAGE145_GEOMETRY_TWO_PASS_V1',
    sourceStatus: 'SOURCE_CLOSED_TWO_PASS_AGREED' as const,
  }
})

const profile: AgarwalSourceProfile = {
  contract: 'AGARWAL_GEOMETRY_STRENGTH_INSPECTOR_V1',
  schemaVersion: 1,
  profileId: 'AGARWAL_2000_GEOMETRY_STRENGTH_INSPECTOR_V1',
  sourceId: 'AGARWAL_MYSTICS_SAGAR_FIRST_EDITION_2000_HARDCOPY',
  edition: 'Mystics of Sarvato Bhadra Chakra and Astrological Predictions, M. K. Agarwal, Sagar Publications, New Delhi, First Edition 2000',
  authority: 'MODERN_PRACTITIONER_SOURCE',
  status: 'GEOMETRY + STRENGTH SOURCE CLOSED',
  geometry: {
    contract: 'AGARWAL_PAGE145_CORE_9X9_V1',
    printedPage: 145,
    contextPage: 146,
    orientation: { east: 'top', west: 'bottom', north: 'left', south: 'right' },
    coordinateConvention: { row_1: 'topmost core row nearest EAST' },
    cells,
    sourceStatus: 'SOURCE_CLOSED_FOR_MACHINE_CORE_GEOMETRY_ONLY',
    evidencePacketId: 'AGARWAL_2000_PAGE145_GEOMETRY_TWO_PASS_V1',
    witnesses: [{ filename: '1000413731.jpg', sha256: 'hash', role: 'PASS_A', printedPage: 145 }],
    p144Reconciliation: { status: 'MATCH', method: 'source comparison', result: 'MATCH', expected: {} },
    historicalUnknownCenterFold: 'SUPERSEDED_BY_CLEAR_PAGE145_PHOTOGRAPHS',
  },
  strengthEvidence: {
    contract: 'AGARWAL_2000_NUMERICAL_AND_GENERAL_STRENGTH_TWO_PASS_V1',
    packetId: 'AGARWAL_2000_NUMERICAL_AND_GENERAL_STRENGTH_TWO_PASS_V1',
    sourceStatus: 'PARTIAL',
    rows: [{
      variableId: 'AGARWAL_2000_NUMERICAL_BENEFIC_SIGN_STRENGTH',
      categoryLiteral: 'Strength based on sign occupied by planets',
      literalValue: 'own 100%/20; friend 75%/15',
      normalizedValue: { own: 20 },
      printedPage: 54,
      privateArtifact: '52-59.pdf',
      artifactSha256: { '52-59.pdf': 'hash' },
      sourceStatus: 'SOURCE_CLOSED',
      diffStatus: 'AGREED',
    }],
    aggregationStatus: 'SOURCE_RECORD_ONLY_NO_MASTER_SCORE',
  },
  vedhaStatus: 'DEPENDENCY_NOT_READY',
  vedhaDependencies: ['deterministic motion-state precedence', 'board-ray traversal semantics'],
  partialSourceEvidence: ['five subject factors'],
  financialStatus: {
    ledgerId: 'AGARWAL_FINANCIAL_SBC_V1',
    classification: 'FINANCIAL_HYPOTHESIS_LEDGER_ONLY',
    printedPages: '180-194',
    claimCount: 1,
    claims: [{ hypothesisId: 'AGARWAL_FIN_180_SCOPE', printedPage: 180, sourceStatus: 'FINANCIAL_HYPOTHESIS' }],
    labels: ['RESEARCH HYPOTHESIS', 'NOT VALIDATED', 'NOT FX-MAPPED', 'NOT EXECUTABLE'],
    allowedUse: 'research_ledger_only',
    prohibitedUses: ['execution'],
  },
  provenance: {
    geometryPrintedPage: 145,
    allocationContextPrintedPage: 144,
    geometryEvidence: 'A1R3_TWO_PASS',
    strengthPages: '54-55 / 60-63',
    sourceStatus: 'SOURCE_CLOSED_FOR_READ_ONLY_GEOMETRY_AND_STRENGTH',
    privateImagePathsExposed: false,
  },
  guardrails: {
    readOnly: true,
    marketDirectionInferred: false,
    polarityAllowed: false,
    scoreAggregationAllowed: false,
    fieldsInfluenceAllowed: false,
    autoSuggestAllowed: false,
    mlAllowed: false,
    executionAllowed: false,
  },
  executionAllowed: false,
}

describe('Agarwal source inspector', () => {
  it('renders the source-derived board, strength and locked Vedha state', async () => {
    fetchProfile.mockResolvedValue(profile)
    render(
      <AgarwalSourceInspectorWorkspace
        profileId={profile.profileId}
        onProfileChange={() => undefined}
      />,
    )

    await waitFor(() => expect(screen.getByRole('grid', { name: 'Agarwal 9 by 9 core board' })).toBeInTheDocument())
    expect(screen.getAllByRole('gridcell')).toHaveLength(81)
    expect(screen.getByText('EAST')).toBeInTheDocument()
    expect(screen.getByText('WEST')).toBeInTheDocument()
    expect(screen.getByText('NORTH')).toBeInTheDocument()
    expect(screen.getByText('SOUTH')).toBeInTheDocument()
    expect(screen.getByText('KRITT-IKA')).toBeInTheDocument()
    expect(screen.getByText('DEPENDENCY_NOT_READY')).toBeInTheDocument()
    expect(screen.getByText('Agarwal Source Strength')).toBeInTheDocument()
    expect(screen.getByText('FINANCIAL_HYPOTHESIS_LEDGER_ONLY')).toBeInTheDocument()
    expect(document.querySelector('.agarwal-ray')).not.toBeInTheDocument()
    expect(screen.queryByText(/C:\\Users\\ADMIN\\Desktop/i)).not.toBeInTheDocument()
  })

  it('opens source details and keeps profile switching explicit', async () => {
    fetchProfile.mockResolvedValue(profile)
    const onProfileChange = vi.fn<(profileId: SbcSourceProfileId) => void>()
    const user = userEvent.setup()
    render(<AgarwalSourceInspectorWorkspace profileId={profile.profileId} onProfileChange={onProfileChange} />)

    await waitFor(() => expect(screen.getAllByRole('gridcell')).toHaveLength(81))
    await user.click(screen.getByRole('gridcell', { name: /KRITT-IKA/i }))
    expect(screen.getByText('Selected cell')).toBeInTheDocument()
    expect(screen.getAllByText('2', { exact: true })).toHaveLength(2)
    await user.selectOptions(screen.getByRole('combobox', { name: 'Agarwal source profile' }), 'SBC_TRAILOKYA_1972_V1')
    expect(onProfileChange).toHaveBeenCalledWith('SBC_TRAILOKYA_1972_V1')
  })
})
