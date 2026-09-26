import type {
  BphsClassicalCalendarInterval,
  ChartConditionedPolarityRangeInterval,
  FxPairRelativeCategoricalInterval,
  MultiOscillatorActivityEvent,
  ResearchFieldIntervalSelection,
  SbcAtomicVisibleRangeInterval,
} from '../types'

export type BphsResearchCategory = keyof BphsClassicalCalendarInterval['categories']

export type BphsResearchSelection = {
  intervalId: string
  startUtc: string
  endUtc: string
  category: BphsResearchCategory
  value: string
  availability: string
  detail: string
  sourceLocator: string
  calculationProfile: string
  dependency: string | null
  sourceProfileId: string
}

export type FieldsResearchSelection =
  | {
      kind: 'FIELD_INTERVAL'
      selection: ResearchFieldIntervalSelection
      interval: ChartConditionedPolarityRangeInterval
      profileId: string
      classification: string
      sourceGapIds: string[]
    }
  | {
      kind: 'PAIR_INTERVAL'
      selection: ResearchFieldIntervalSelection
      interval: FxPairRelativeCategoricalInterval
      profileId: string
      classification: 'MODERN_ENGINEERING_RESEARCH_TRANSFORM'
      sourceGapIds: string[]
    }
  | {
      kind: 'ACTIVITY_EVENT'
      event: MultiOscillatorActivityEvent
      coverage: 'KNOWN' | 'UNKNOWN'
      unknownReason: string | null
      profileId: string
      classification: 'EXPLORATORY_UNSIGNED'
      sourceGapIds: string[]
    }
  | {
      kind: 'SBC_INTERVAL'
      selection: ResearchFieldIntervalSelection
      interval: SbcAtomicVisibleRangeInterval
      profileId: string
      classification: string
      sourceGapIds: string[]
    }
  | {
      kind: 'BPHS_INTERVAL'
      selection: BphsResearchSelection
      profileId: string
      classification: string
      sourceGapIds: string[]
    }
