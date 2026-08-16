// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TrailokyaNativeInspectorWorkspace } from './views/TrailokyaNativeInspectorWorkspace'

const { fetchProfile, resolveTargets } = vi.hoisted(() => ({ fetchProfile: vi.fn(), resolveTargets: vi.fn() }))
vi.mock('./api', () => ({ fetchTrailokyaNativeProfile: fetchProfile, resolveTrailokyaTargets: resolveTargets }))

const guardrails = { readOnly: true, enumeratedSourceAuthority: true, genericGridFallbackAllowed: false, naturalPlanetPolarityUsed: false, scoreAggregationUsed: false, marketDirectionInferred: false, fieldsInfluenceAllowed: false, autoSuggestInfluenceAllowed: false, mlAllowed: false, mt5Allowed: false, executionAllowed: false } as const
const profile = {
  contract: 'TRAILOKYA_1972_NATIVE_SOURCE_PROFILE_V1', schemaVersion: 1, profileId: 'SBC_TRAILOKYA_1972_V1', sourceId: 'TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN',
  board: { contract: 'TRAILOKYA_1972_NATIVE_AKHANDA_81_BOARD_V1', gridProfileId: 'trailokya_1972_native_akhanda_81_v1', fixtureHash: 'fixture', orientation: { authorVisible: { east: 'TOP', west: 'BOTTOM', north: 'LEFT', south: 'RIGHT' }, repositoryCoordinates: {}, cornerMapping: {} }, cells: Array.from({ length: 81 }, (_, index) => ({ coordinate: { row: Math.floor(index / 9) + 1, column: (index % 9) + 1, label: `${Math.floor(index / 9) + 1}:${(index % 9) + 1}` }, sourceLiteral: index === 0 ? 'अ' : `L${index}`, canonicalToken: index === 0 ? 'A' : `T${index}`, normalizedDisplay: index === 0 ? 'a' : `T${index}`, layer: 'NAKSHATRA', sourceStatus: 'SOURCE_CLOSED', printedPage: 1, scanPage: 13 })), cellCount: 81, sourceStatus: 'SOURCE_CLOSED' },
  targetAuthority: { contract: 'TRAILOKYA_1972_ENUMERATED_NAKSHATRA_TARGETS_V1', fixtureHash: 'rows', rowCount: 28, mode: 'ENUMERATED_SOURCE_ROWS', frontContract: 'SINGLE_OPPOSITE_OUTER_NAKSHATRA_ONLY' }, expansions: { contract: 'TRAILOKYA_1972_DERIVED_SEMANTIC_TARGET_EXPANSIONS_V1', fixtureHash: 'expansion' }, readiness: { nativeBoardTrustedForVisualProjection: true, genericGridFallbackAllowed: false, runtimePromotionAuthorized: false, marketMappingAllowed: false, executionAllowed: false }, guardrails,
} as const

const resolution = {
  contract: 'TRAILOKYA_1972_ENUMERATED_TARGET_RESOLUTION_V1', sourceProfileId: 'SBC_TRAILOKYA_1972_V1', targetAuthority: 'ENUMERATED_SOURCE_ROWS', sourceNakshatra: 'JYESHTHA', direction: 'LEFT', sourceEventId: 'source-event', causalVedhaEventId: 'source-event', sourceRow: { verse: 35, scanPage: 25, printedPage: 9, auditStatus: 'TD1R2_SOURCE_RESTORED' }, status: 'SOURCE_ROW_RESOLVED',
  directTargets: [{ targetId: 'direct', sourceEventId: 'source-event', causalVedhaEventId: 'source-event', sourceNakshatra: 'JYESHTHA', direction: 'LEFT', sourceOrderedIndex: 1, targetType: 'NAME_INITIAL', canonicalToken: 'YA', isDerived: false, derivedFromTargetId: null, derivationRuleId: null, physicalCell: { row: 1, column: 1, label: '1:1' }, mappingState: 'AVAILABLE', reachState: 'UNKNOWN', sourceLocator: { verse: 35, scanPage: 25, printedPage: 9, auditStatus: 'TD1R2_SOURCE_RESTORED' }}],
  derivedTargets: [{ targetId: 'derived', sourceEventId: 'source-event', causalVedhaEventId: 'source-event', sourceNakshatra: 'JYESHTHA', direction: 'LEFT', sourceOrderedIndex: 1, targetType: 'NAME_INITIAL', canonicalToken: 'VA', isDerived: true, derivedFromTargetId: 'direct', derivationRuleId: 'TD1972_V48_PAIRED_UNWRITTEN_AKSHARA', physicalCell: null, mappingState: 'SEMANTIC_NO_PHYSICAL_CELL', reachState: 'UNKNOWN', sourceLocator: { verse: 35, scanPage: 25, printedPage: 9, auditStatus: 'TD1R2_SOURCE_RESTORED' }}],
  allTargets: [], geometryDiagnostic: { status: 'GEOMETRY_DIAGNOSTIC_NOT_REQUESTED', authoritativeResult: 'SOURCE_ROW_WINS' }, guardrails,
} as const

describe('TrailokyaNativeInspectorWorkspace', () => {
  it('renders the native board, source-order targets, and explicit unknowns without market terms', async () => {
    fetchProfile.mockResolvedValue(profile)
    resolveTargets.mockResolvedValue({ ...resolution, allTargets: [...resolution.directTargets, ...resolution.derivedTargets] })
    const user = userEvent.setup()
    render(<TrailokyaNativeInspectorWorkspace profileId="SBC_TRAILOKYA_1972_V1" onProfileChange={vi.fn()} />)
    await waitFor(() => expect(screen.getByRole('grid', { name: 'Trailokya 9 by 9 source board' })).toBeInTheDocument())
    expect(screen.getAllByRole('gridcell')).toHaveLength(81)
    expect(screen.getByText('SOURCE-CLOSED BOARD')).toBeInTheDocument()
    expect(screen.getByText('ENUMERATED VEDHA TARGETS')).toBeInTheDocument()
    expect(screen.getByText('Context-free reach state is UNKNOWN')).toBeInTheDocument()
    expect(screen.queryByText(/bullish|bearish|buy|sell/i)).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /name initial.*va/i }))
    expect(screen.getByText('Derived · TD1972_V48_PAIRED_UNWRITTEN_AKSHARA')).toBeInTheDocument()
    expect(resolveTargets).toHaveBeenCalledWith({ sourceNakshatra: 'KRITTIKA', direction: 'LEFT' })
  })
})
