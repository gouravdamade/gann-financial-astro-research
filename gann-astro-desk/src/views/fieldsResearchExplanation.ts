import type { VisualizationModePolicy } from '../visualizationModes'
import type { FieldsResearchSelection } from './fieldsResearchSelection'

export const NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT = 'NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT'

export type FieldsResearchExplanationModel = {
  headline: string
  whyThisIsVisible: string
  astronomyFact: string
  sourceDoctrine: string
  astrologyInterpretation: string
  engineeringTransform: string
  marketBridge: string
  financialValidation: 'NOT_FINANCIALLY_VALIDATED'
  magnitude: 'MAGNITUDE_NOT_CONFIGURED'
  unknownsAndWithheld: string
  execution: 'executionAllowed=false'
}

function present(value: string | null | undefined): string {
  return value?.trim() || NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT
}

function recorded(values: string[]): string {
  return values.length ? values.join(' | ') : 'none recorded in the current selection'
}

function classification(value: string): string {
  if (value === 'SOURCE_CERTIFIED') return value
  if (value.includes('SOURCE_CERTIFIED')) return NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT
  return present(value)
}

function common(
  headline: string,
  astronomyFact: string,
  sourceDoctrine: string,
  astrologyInterpretation: string,
  engineeringTransform: string,
  marketBridge: string,
  unknownsAndWithheld: string,
): FieldsResearchExplanationModel {
  return {
    headline,
    whyThisIsVisible: 'Read-only context for the selected research record; it does not establish financial validation.',
    astronomyFact,
    sourceDoctrine,
    astrologyInterpretation,
    engineeringTransform,
    marketBridge,
    financialValidation: 'NOT_FINANCIALLY_VALIDATED',
    magnitude: 'MAGNITUDE_NOT_CONFIGURED',
    unknownsAndWithheld,
    execution: 'executionAllowed=false',
  }
}

function fieldExplanation(
  selection: Extract<FieldsResearchSelection, { kind: 'FIELD_INTERVAL' }>,
  policy: VisualizationModePolicy,
): FieldsResearchExplanationModel {
  const { field, startUtc, endUtc } = selection.selection
  const withheld = !policy.scoringVisible
  let interpretation: string
  let unknowns: string

  if (withheld) {
    interpretation = 'WITHHELD BY CURRENT MODE'
    unknowns = 'WITHHELD BY CURRENT MODE; the directional state and value are absent from this explanation model.'
  } else {
    const interval = selection.interval
    interpretation = `Existing categorical state: ${interval.polarityState}`
    unknowns = interval.polarityState === 'UNKNOWN'
      ? `UNKNOWN; reason: ${present(interval.reason)}; unknown event IDs: ${recorded(interval.unknownEventIds)}`
      : 'No UNKNOWN state is recorded on the selected interval.'
  }

  return common(
    `Selected ${field} field interval`,
    `Selected UTC bounds: ${startUtc} to ${endUtc}`,
    `Profile: ${present(selection.profileId)}; classification: ${classification(selection.classification)}; source gaps: ${recorded(selection.sourceGapIds)}; exact source locator: ${NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT}`,
    interpretation,
    `Visualization mode: ${policy.mode}; calibration status: ${policy.calibrationProfile.status}`,
    'NO_APPROVED_MARKET_BRIDGE',
    unknowns,
  )
}

function pairExplanation(
  selection: Extract<FieldsResearchSelection, { kind: 'PAIR_INTERVAL' }>,
  policy: VisualizationModePolicy,
): FieldsResearchExplanationModel {
  const { startUtc, endUtc } = selection.selection
  const withheld = !policy.scoringVisible
  let interpretation: string
  let engineering: string
  let unknowns: string

  if (withheld) {
    interpretation = 'WITHHELD BY CURRENT MODE'
    engineering = `${selection.classification}; interval details are withheld by visualizationPolicy.scoringVisible=false.`
    unknowns = 'WITHHELD BY CURRENT MODE; the pair state and numeric values are absent from this explanation model.'
  } else {
    const interval = selection.interval
    interpretation = `Existing pair-relative category: ${interval.state}`
    engineering = `${selection.classification}; FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1 is a descriptive research transform.`
    unknowns = interval.state === 'UNKNOWN_SIDE_EVIDENCE' || interval.coverage === 'UNKNOWN'
      ? `UNKNOWN side evidence; reason: ${present(interval.unknownReason)}`
      : interval.state === 'MIXED'
        ? 'MIXED is retained as a distinct pair category; no resolution is applied.'
        : 'No UNKNOWN side-evidence state is recorded on the selected interval.'
  }

  const sourceDetails = withheld
    ? `Profile: ${present(selection.profileId)}; classification: ${classification(selection.classification)}; source gaps: ${recorded(selection.sourceGapIds)}; exact source locator: ${NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT}`
    : `Profile: ${present(selection.profileId)}; classification: ${classification(selection.classification)}; source gaps: ${recorded(selection.sourceGapIds)}; base/quote source interval IDs: ${present(selection.interval.sourceIntervalIds.base)} | ${present(selection.interval.sourceIntervalIds.quote)}; coverage: ${selection.interval.coverage}; conflict: ${selection.interval.conflict ? 'present' : 'none'}; exact source locator: ${NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT}`

  return common(
    'Selected USDJPY pair-relative interval',
    `Selected UTC bounds: ${startUtc} to ${endUtc}`,
    sourceDetails,
    interpretation,
    engineering,
    'MODERN_ENGINEERING_RESEARCH_TRANSFORM; NOT_A_MARKET_BRIDGE; not a signed resultant.',
    unknowns,
  )
}

function activityExplanation(
  selection: Extract<FieldsResearchSelection, { kind: 'ACTIVITY_EVENT' }>,
): FieldsResearchExplanationModel {
  const event = selection.event
  const unknowns = selection.coverage === 'UNKNOWN'
    ? `UNKNOWN activity coverage; reason: ${present(selection.unknownReason)}`
    : 'Activity coverage is marked KNOWN by the selected record.'

  return common(
    `Selected unsigned ${event.sideIdentity} activity event`,
    `${event.transitBody} to ${event.natalTarget}; ${event.aspectType}; applying ${event.applyingStartUtc}; exact ${event.exactUtc}; separating ${event.separatingEndUtc}; astronomy contract: ${present(event.astronomyContract)}; ayanamsha: ${present(event.ayanamsha)}; node policy: ${present(event.nodePolicy)}`,
    `EXPLORATORY_UNSIGNED; profile: ${present(selection.profileId)}; classical source doctrine: ${NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT}; source gaps: ${recorded(selection.sourceGapIds)}`,
    'No polarity interpretation is assigned.',
    `EXPLORATORY_UNSIGNED; aspect profile: ${present(event.aspectProfileId)}; event contract: ${present(event.eventContract)}; generator version: ${present(event.generatorVersion)}; polarity=NOT_ASSIGNED; magnitude=MAGNITUDE_NOT_CONFIGURED; priceOutcomeRead=false.`,
    'NO_APPROVED_MARKET_BRIDGE',
    unknowns,
  )
}

function sbcExplanation(
  selection: Extract<FieldsResearchSelection, { kind: 'SBC_INTERVAL' }>,
): FieldsResearchExplanationModel {
  const interval = selection.interval
  const unknownDetails = [
    interval.guidance_availability === 'UNKNOWN' ? 'UNKNOWN SBC availability' : null,
    interval.missing_evidence_ids.length ? `Missing evidence: ${interval.missing_evidence_ids.join(' | ')}` : null,
    selection.sourceGapIds.length ? `Source gaps: ${selection.sourceGapIds.join(' | ')}` : null,
  ].filter((item): item is string => item !== null)

  return common(
    'Selected independent SBC availability interval',
    `Selected UTC bounds: ${interval.start_utc} to ${interval.end_utc}; evidence cutoff: ${interval.evidence_cutoff_utc}`,
    `Profile: ${present(selection.profileId)}; classification: ${classification(selection.classification)}; availability: ${interval.guidance_availability}; evidence cutoff: ${interval.evidence_cutoff_utc}; source clusters: ${recorded(interval.source_cluster_ids)}; missing evidence: ${recorded(interval.missing_evidence_ids)}; interval ledger: ${present(interval.interval_ledger_id)}; source gaps: ${recorded(selection.sourceGapIds)}; exact page locator: ${NOT_PRESENT_IN_CURRENT_SELECTION_CONTRACT}`,
    `SBC availability: ${interval.guidance_availability}; this is an independent source context, not confirmation of another field.`,
    'No additional engineering transform is present in the selected SBC interval contract.',
    'NO_MARKET_ROLE; independent from USD, JPY, and pair interpretation.',
    unknownDetails.join(' | ') || 'No missing-evidence identifier is recorded on the selected SBC interval.',
  )
}

function bphsExplanation(
  selection: Extract<FieldsResearchSelection, { kind: 'BPHS_INTERVAL' }>,
): FieldsResearchExplanationModel {
  const item = selection.selection
  const unknownDetails = [
    item.availability === 'UNKNOWN' || item.availability === 'DEPENDENCY_NOT_READY' ? item.availability : null,
    item.dependency ? `Dependency: ${item.dependency}` : null,
    selection.sourceGapIds.length ? `Source gaps: ${selection.sourceGapIds.join(' | ')}` : null,
  ].filter((value): value is string => value !== null)

  return common(
    'Selected BPHS calendar research interval',
    `Selected UTC bounds: ${item.startUtc} to ${item.endUtc}`,
    `Profile: ${present(item.sourceProfileId)}; classification: ${classification(selection.classification)}; availability: ${present(item.availability)}; source locator: ${present(item.sourceLocator)}; source gaps: ${recorded(selection.sourceGapIds)}`,
    `${item.category}: ${item.value}; ${present(item.detail)}`,
    `Calculation profile: ${present(item.calculationProfile)}; dependency: ${present(item.dependency)}`,
    'NO MARKET ROLE',
    unknownDetails.join(' | ') || 'No dependency or source-gap identifier is recorded on the selected BPHS interval.',
  )
}

export function buildFieldsResearchExplanation(
  selection: FieldsResearchSelection | null,
  policy: VisualizationModePolicy,
): FieldsResearchExplanationModel | null {
  if (!selection) return null

  switch (selection.kind) {
    case 'FIELD_INTERVAL':
      return fieldExplanation(selection, policy)
    case 'PAIR_INTERVAL':
      return pairExplanation(selection, policy)
    case 'ACTIVITY_EVENT':
      return activityExplanation(selection)
    case 'SBC_INTERVAL':
      return sbcExplanation(selection)
    case 'BPHS_INTERVAL':
      return bphsExplanation(selection)
  }
}
