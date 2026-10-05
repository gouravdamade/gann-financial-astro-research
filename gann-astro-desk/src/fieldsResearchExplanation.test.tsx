// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { visualizationModePolicy } from './visualizationModes'
import type { FieldsResearchSelection } from './views/fieldsResearchSelection'
import { FieldsResearchInspector } from './views/FieldsResearchInspector'
import { buildFieldsResearchExplanation, NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT } from './views/fieldsResearchExplanation'

const startUtc = '2026-08-01T10:00:00.000Z'
const endUtc = '2026-08-01T12:00:00.000Z'

function fieldSelection(state: string = 'MIXED'): FieldsResearchSelection {
  return {
    kind: 'FIELD_INTERVAL',
    selection: { field: 'USD', intervalId: 'usd-interval-1', startUtc, endUtc },
    interval: {
      intervalId: 'usd-interval-1', startUtc, endUtc, polarityState: state,
      supportiveActive: true, adverseActive: true, activeEventIds: ['event-a'],
      unknownEventIds: state === 'UNKNOWN' ? ['gap-a'] : [], reason: 'Current interval record reason.',
    },
    profileId: 'USD_PARTIAL_PROFILE_V1',
    classification: 'SOURCE_PROFILED_PARTIAL',
    sourceGapIds: ['USD_SOURCE_GAP_1'],
  } as unknown as FieldsResearchSelection
}

function pairSelection(state: string = 'MIXED'): FieldsResearchSelection {
  return {
    kind: 'PAIR_INTERVAL',
    selection: { field: 'PAIR', intervalId: 'pair-interval-1', startUtc, endUtc },
    interval: {
      intervalId: 'pair-interval-1', startUtc, endUtc, state,
      baseBalance: 1.25, quoteBalance: -0.25, pairRaw: 1.5, pairDisplay: 1.5,
      baseSupportiveActive: true, baseAdverseActive: false, baseGrossActivity: 1,
      quoteSupportiveActive: false, quoteAdverseActive: true, quoteGrossActivity: 1,
      commonActivity: 0, conflict: true, coverage: state === 'UNKNOWN_SIDE_EVIDENCE' ? 'UNKNOWN' : 'KNOWN',
      unknownReason: state === 'UNKNOWN_SIDE_EVIDENCE' ? 'SIDE_SOURCE_UNKNOWN' : null,
      sourceIntervalIds: { base: 'usd-interval-source', quote: 'jpy-interval-source' },
    },
    profileId: 'PAIR_RESEARCH_PROFILE_V1',
    classification: 'MODERN_ENGINEERING_RESEARCH_TRANSFORM',
    sourceGapIds: [],
  } as unknown as FieldsResearchSelection
}

function activitySelection(): FieldsResearchSelection {
  return {
    kind: 'ACTIVITY_EVENT',
    event: {
      eventId: 'MO_EVENT_1', eventHash: 'a'.repeat(64), eventContract: 'MO_EVENT_CONTRACT_V1',
      sideIdentity: 'USD', instrumentIdentity: 'FX_CURRENCY:USD', chartId: 'usd-chart', chartHypothesisId: 'usd-hypothesis',
      transitBody: 'MARS', natalTarget: 'SUN', aspectType: 'SQUARE', astronomyContract: 'ASTRONOMY_CONTRACT_V1',
      ayanamsha: 'RAMAN', nodePolicy: 'TRUE_NODE', generatorVersion: 'generator-v1',
      applyingStartUtc: startUtc, exactUtc: '2026-08-01T11:00:00.000Z', separatingEndUtc: endUtc,
      aspectProfileId: 'ASPECT_STRENGTH_V0', polarity: null, magnitude: null,
    },
    coverage: 'KNOWN', unknownReason: null, profileId: 'ASPECT_STRENGTH_V0',
    classification: 'EXPLORATORY_UNSIGNED', sourceGapIds: [],
  } as unknown as FieldsResearchSelection
}

function sbcSelection(): FieldsResearchSelection {
  return {
    kind: 'SBC_INTERVAL',
    selection: { field: 'SBC', intervalId: 'sbc-interval-1', startUtc, endUtc },
    interval: {
      interval_id: 'sbc-interval-1', interval_ledger_id: 'sbc-ledger-1',
      start_utc: startUtc, end_utc: endUtc, evidence_cutoff_utc: startUtc,
      classification: 'ATOMIC_SOURCE_RECORD', guidance_availability: 'PARTIAL',
      source_cluster_ids: ['SBC_CLUSTER_1'], missing_evidence_ids: ['SBC_MISSING_1'],
    },
    profileId: 'SBC_PROFILE_V1', classification: 'SOURCE_PROFILED_PARTIAL',
    sourceGapIds: ['SBC_GAP_1'],
  } as unknown as FieldsResearchSelection
}

function bphsSelection(sourceLocator = ''): FieldsResearchSelection {
  return {
    kind: 'BPHS_INTERVAL',
    selection: {
      intervalId: 'BPHS_INTERVAL_1', startUtc, endUtc, category: 'muhurta', value: 'DAY MUHURTA 01 - Ardra',
      availability: 'SOURCE_TRANSCRIBED_ENGINEERING_BOUNDARY', detail: 'Source name; engineering boundary.',
      sourceLocator, calculationProfile: 'SWISSEPH_RAMAN_V1', dependency: 'SUNRISE_BOUNDARY_PARTIAL',
      sourceProfileId: 'BPHS_SOURCE_PROFILE_V1',
    },
    profileId: 'BPHS_SOURCE_PROFILE_V1', classification: 'SOURCE_PROFILED_PARTIAL',
    sourceGapIds: ['BPHS_GAP_1'],
  } as unknown as FieldsResearchSelection
}

function forbidSelectionReads<T extends object>(value: T): T {
  return new Proxy(value, {
    get(target, property, receiver) {
      if (typeof property === 'string' && property !== 'startUtc' && property !== 'endUtc') {
        throw new Error(`Hidden selection field read: ${property}`)
      }
      return Reflect.get(target, property, receiver)
    },
  })
}

afterEach(() => cleanup())

describe('FieldsResearchExplanation model', () => {
  it('builds a field explanation without promoting a partial source profile', () => {
    const model = buildFieldsResearchExplanation(fieldSelection(), visualizationModePolicy('SOURCE_ONLY_BASELINE'))!
    expect(model.headline).toBe('Selected USD field interval')
    expect(model.astronomyFact).toContain(startUtc)
    expect(model.sourceDoctrine).toContain('SOURCE_PROFILED_PARTIAL')
    expect(model.sourceDoctrine).toContain(NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT)
    expect(model.sourceDoctrine).not.toContain('SOURCE_CERTIFIED')
    expect(model.astrologyInterpretation).toContain('MIXED')
    expect(model.unknownsAndWithheld).not.toContain('NEUTRAL')
  })

  it('preserves UNKNOWN, MIXED, and explicit NEUTRAL as different field states', () => {
    const policy = visualizationModePolicy('SOURCE_ONLY_BASELINE')
    const unknown = buildFieldsResearchExplanation(fieldSelection('UNKNOWN'), policy)!
    const mixed = buildFieldsResearchExplanation(fieldSelection('MIXED'), policy)!
    const neutral = buildFieldsResearchExplanation(fieldSelection('NEUTRAL'), policy)!

    expect(unknown.astrologyInterpretation).toContain('UNKNOWN')
    expect(unknown.unknownsAndWithheld).toContain('gap-a')
    expect(mixed.astrologyInterpretation).toContain('MIXED')
    expect(neutral.astrologyInterpretation).toContain('NEUTRAL')
    expect(unknown.astrologyInterpretation).not.toBe(neutral.astrologyInterpretation)
    expect(mixed.astrologyInterpretation).not.toBe(neutral.astrologyInterpretation)
  })

  it('allows SOURCE_CERTIFIED only when the selected upstream classification is exactly that value', () => {
    const selection = fieldSelection()
    if (selection.kind !== 'FIELD_INTERVAL') throw new Error('Invalid fixture')
    const explicit = { ...selection, classification: 'SOURCE_CERTIFIED' }
    const model = buildFieldsResearchExplanation(explicit, visualizationModePolicy('SOURCE_ONLY_BASELINE'))!
    expect(model.sourceDoctrine).toContain('SOURCE_CERTIFIED')
  })

  it('keeps pair explanation as a modern engineering transform, not a market bridge', () => {
    const model = buildFieldsResearchExplanation(pairSelection(), visualizationModePolicy('SOURCE_ONLY_BASELINE'))!
    expect(model.engineeringTransform).toContain('MODERN_ENGINEERING_RESEARCH_TRANSFORM')
    expect(model.sourceDoctrine).toContain('usd-interval-source')
    expect(model.sourceDoctrine).toContain('jpy-interval-source')
    expect(model.sourceDoctrine).toContain('coverage: KNOWN')
    expect(model.sourceDoctrine).toContain('conflict: present')
    expect(model.marketBridge).toContain('NOT_A_MARKET_BRIDGE')
    expect(model.marketBridge).toContain('not a signed resultant')
    expect(model.marketBridge).not.toContain('forecast')
  })

  it('preserves pair UNKNOWN and MIXED states without converting either to NEUTRAL', () => {
    const policy = visualizationModePolicy('SOURCE_ONLY_BASELINE')
    const unknown = buildFieldsResearchExplanation(pairSelection('UNKNOWN_SIDE_EVIDENCE'), policy)!
    const mixed = buildFieldsResearchExplanation(pairSelection('MIXED'), policy)!
    expect(unknown.astrologyInterpretation).toContain('UNKNOWN_SIDE_EVIDENCE')
    expect(unknown.unknownsAndWithheld).toContain('SIDE_SOURCE_UNKNOWN')
    expect(mixed.astrologyInterpretation).toContain('MIXED')
    expect(mixed.astrologyInterpretation).not.toContain('NEUTRAL')
  })

  it('keeps activity unsigned with its existing astronomy and lifecycle provenance', () => {
    const model = buildFieldsResearchExplanation(activitySelection(), visualizationModePolicy('SOURCE_ONLY_BASELINE'))!
    expect(model.sourceDoctrine).toContain('EXPLORATORY_UNSIGNED')
    expect(model.astronomyFact).toContain('MARS to SUN')
    expect(model.astronomyFact).toContain('astronomy contract: ASTRONOMY_CONTRACT_V1')
    expect(model.engineeringTransform).toContain('polarity=NOT_ASSIGNED')
    expect(model.engineeringTransform).toContain('magnitude=MAGNITUDE_NOT_CONFIGURED')
    expect(model.engineeringTransform).toContain('priceOutcomeRead=false')
    expect(model.marketBridge).toBe('NO_APPROVED_MARKET_BRIDGE')
  })

  it('keeps SBC independent and preserves availability, cutoff, clusters, and missing evidence', () => {
    const model = buildFieldsResearchExplanation(sbcSelection(), visualizationModePolicy('SOURCE_ONLY_BASELINE'))!
    expect(model.sourceDoctrine).toContain('PARTIAL')
    expect(model.astronomyFact).toContain(startUtc)
    expect(model.sourceDoctrine).toContain('SBC_CLUSTER_1')
    expect(model.sourceDoctrine).toContain('SBC_MISSING_1')
    expect(model.marketBridge).toContain('independent from USD, JPY, and pair')
    expect(model.marketBridge).not.toContain('confirmation')
  })

  it('keeps BPHS source locator truthful and retains NO MARKET ROLE', () => {
    const missingLocator = buildFieldsResearchExplanation(bphsSelection(), visualizationModePolicy('SOURCE_ONLY_BASELINE'))!
    const presentLocator = buildFieldsResearchExplanation(bphsSelection('Chapter 14 printed p. 197'), visualizationModePolicy('SOURCE_ONLY_BASELINE'))!
    expect(missingLocator.sourceDoctrine).toContain(NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT)
    expect(presentLocator.sourceDoctrine).toContain('Chapter 14 printed p. 197')
    expect(missingLocator.astrologyInterpretation).toContain('DAY MUHURTA 01 - Ardra')
    expect(missingLocator.marketBridge).toBe('NO MARKET ROLE')
    expect(missingLocator.unknownsAndWithheld).toContain('SUNRISE_BOUNDARY_PARTIAL')
  })

  it('preserves calibration absence in Mode 2 and returns no model for no selection', () => {
    const model = buildFieldsResearchExplanation(fieldSelection(), visualizationModePolicy('CALIBRATED_RESEARCH'))!
    expect(model.astrologyInterpretation).toBe('WITHHELD BY CURRENT MODE')
    expect(model.engineeringTransform).toContain('calibration status: SOURCE_MISSING')
    expect(model.unknownsAndWithheld).toContain('WITHHELD BY CURRENT MODE')
    expect(buildFieldsResearchExplanation(null, visualizationModePolicy('SOURCE_ONLY_BASELINE'))).toBeNull()
  })

  it.each([
    ['FIELD_INTERVAL', fieldSelection()],
    ['PAIR_INTERVAL', pairSelection()],
    ['ACTIVITY_EVENT', activitySelection()],
    ['SBC_INTERVAL', sbcSelection()],
    ['BPHS_INTERVAL', bphsSelection()],
  ] as const)('renders %s explanation with financial and execution locks', (_kind, selection) => {
    render(<FieldsResearchInspector selection={selection} crosshairTimestampUtc={null} visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')} sourceProfileId="profile" />)
    const explanation = screen.getByLabelText('Explanation and provenance')
    expect(explanation).toHaveTextContent('NOT_FINANCIALLY_VALIDATED')
    expect(explanation).toHaveTextContent('executionAllowed=false')
  })

  it.each([
    ['CALIBRATED_RESEARCH', 'SUPPORTIVE', '123456.789', 'HIDDEN_FIELD_REASON'],
    ['VISUAL_ONLY_NO_SCORE', 'SUPPORTIVE', '123456.789', 'HIDDEN_FIELD_REASON'],
  ] as const)('%s omits hidden field state and value from model and rendered DOM', (mode, state, numericValue, hiddenReason) => {
    const selection = fieldSelection(state)
    if (selection.kind !== 'FIELD_INTERVAL') throw new Error('Invalid fixture')
    selection.interval = forbidSelectionReads({
      ...selection.interval,
      reason: hiddenReason,
      polarityState: state as never,
      supportiveActive: true,
      hiddenDirectionalValue: Number(numericValue),
    } as typeof selection.interval)
    const policy = visualizationModePolicy(mode)
    const model = buildFieldsResearchExplanation(selection, policy)!

    expect(JSON.stringify(model)).not.toContain(state)
    expect(JSON.stringify(model)).not.toContain(numericValue)
    expect(JSON.stringify(model)).not.toContain(hiddenReason)
    expect(model.astrologyInterpretation).toBe('WITHHELD BY CURRENT MODE')

    render(<FieldsResearchInspector selection={selection} crosshairTimestampUtc={null} visualizationPolicy={policy} sourceProfileId="profile" />)
    expect(screen.getByLabelText('Explanation and provenance')).toBeInTheDocument()
    const allMarkup = document.body.innerHTML
    expect(document.body.textContent).not.toContain(state)
    expect(allMarkup).not.toContain(numericValue)
    expect(allMarkup).not.toContain(hiddenReason)
    const attributeValues = [...document.querySelectorAll<HTMLElement>('*')]
      .flatMap((node) => node.getAttributeNames().map((name) => node.getAttribute(name) ?? ''))
      .join(' ')
    expect(attributeValues).not.toContain(state)
    expect(attributeValues).not.toContain(numericValue)
    expect(attributeValues).not.toContain(hiddenReason)
    expect(screen.getByText('NOT_FINANCIALLY_VALIDATED')).toBeInTheDocument()
    expect(screen.getAllByText('executionAllowed=false').length).toBeGreaterThan(0)
  })

  it.each([
    ['CALIBRATED_RESEARCH', 'ADVERSE', '987654.321'],
    ['VISUAL_ONLY_NO_SCORE', 'ADVERSE', '987654.321'],
  ] as const)('%s omits hidden pair state and numeric values from model and rendered DOM', (mode, state, numericValue) => {
    const selection = pairSelection(state)
    if (selection.kind !== 'PAIR_INTERVAL') throw new Error('Invalid fixture')
    selection.interval = forbidSelectionReads({
      ...selection.interval,
      state: state as never,
      pairRaw: Number(numericValue),
      pairDisplay: Number(numericValue),
      unknownReason: 'HIDDEN_PAIR_REASON',
    })
    const policy = visualizationModePolicy(mode)
    const model = buildFieldsResearchExplanation(selection, policy)!

    expect(JSON.stringify(model)).not.toContain(state)
    expect(JSON.stringify(model)).not.toContain(numericValue)
    expect(JSON.stringify(model)).not.toContain('HIDDEN_PAIR_REASON')
    expect(model.astrologyInterpretation).toBe('WITHHELD BY CURRENT MODE')

    render(<FieldsResearchInspector selection={selection} crosshairTimestampUtc={null} visualizationPolicy={policy} sourceProfileId="profile" />)
    const allMarkup = document.body.innerHTML
    expect(document.body.textContent).not.toContain(state)
    expect(allMarkup).not.toContain(numericValue)
    expect(allMarkup).not.toContain('HIDDEN_PAIR_REASON')
    const attributeValues = [...document.querySelectorAll<HTMLElement>('*')]
      .flatMap((node) => node.getAttributeNames().map((name) => node.getAttribute(name) ?? ''))
      .join(' ')
    expect(attributeValues).not.toContain(state)
    expect(attributeValues).not.toContain(numericValue)
    expect(attributeValues).not.toContain('HIDDEN_PAIR_REASON')
    expect(screen.getByText('NOT_FINANCIALLY_VALIDATED')).toBeInTheDocument()
    expect(screen.getAllByText('executionAllowed=false').length).toBeGreaterThan(0)
  })

  it('keeps the existing inspector empty state without auto-selecting or rendering an explanation', () => {
    render(<FieldsResearchInspector selection={null} crosshairTimestampUtc={null} visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')} sourceProfileId="profile" />)
    expect(screen.getByText('NO RESEARCH ITEM SELECTED')).toBeInTheDocument()
    expect(screen.queryByLabelText('Explanation and provenance')).not.toBeInTheDocument()
  })
})
