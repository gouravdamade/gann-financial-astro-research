import type { VisualizationEngineMode } from './visualizationModes'

export type VisualizationSourceGap = {
  gapId: string
  title: string
  affectedModes: VisualizationEngineMode[]
  status: 'SOURCE_MISSING'
  explanation: string
}

// These are explicit omissions, not placeholders for invented doctrine or fitted values.
export const VISUALIZATION_SOURCE_GAPS: VisualizationSourceGap[] = [
  {
    gapId: 'SBC_BASELINE_PROFILE_APPROVAL',
    title: 'Founder-reviewed source profile admission',
    affectedModes: ['SOURCE_ONLY_BASELINE'],
    status: 'SOURCE_MISSING',
    explanation: 'Loaded source-profiled components are visible, but a founder-approved admission record for this visualization profile has not been supplied.',
  },
  {
    gapId: 'SBC_CALIBRATION_PARAMETER_PROFILE',
    title: 'Calibration parameter profile',
    affectedModes: ['CALIBRATED_RESEARCH'],
    status: 'SOURCE_MISSING',
    explanation: 'No reviewed parameter values, units, ranges, fitting method, train/test period, or profile hash are loaded. Calibrated scores stay withheld.',
  },
  {
    gapId: 'SBC_TIMING_PHASE_SOURCE_RULE',
    title: 'Classical timing-phase source rule',
    affectedModes: ['CALIBRATED_RESEARCH'],
    status: 'SOURCE_MISSING',
    explanation: 'The timing phase laboratory is an engineering visualization only. It has no approved classical mapping and cannot affect a score or execution.',
  },
  {
    gapId: 'EVENT_CONTRIBUTION_LINK_PROFILE_MISSING',
    title: 'Event-contribution link profile',
    affectedModes: ['CALIBRATED_RESEARCH', 'VISUAL_ONLY_NO_SCORE'],
    status: 'SOURCE_MISSING',
    explanation: 'No approved mapping links resolved SBC contributions to active aspect events. Event lifecycle geometry remains visible, while Cartesian aggregate interference values are withheld.',
  },
]

export function sourceGapsForVisualizationMode(mode: VisualizationEngineMode): VisualizationSourceGap[] {
  return VISUALIZATION_SOURCE_GAPS.filter((gap) => gap.affectedModes.includes(mode))
}
