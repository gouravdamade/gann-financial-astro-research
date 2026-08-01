export type VisualizationSourceGap = {
  gapId: string
  title: string
  affectedMode: 'SOURCE_ONLY_BASELINE' | 'CALIBRATED_RESEARCH' | 'VISUAL_ONLY_NO_SCORE'
  status: 'SOURCE_MISSING'
  explanation: string
}

// These are explicit omissions, not placeholders for invented doctrine or fitted values.
export const VISUALIZATION_SOURCE_GAPS: VisualizationSourceGap[] = [
  {
    gapId: 'SBC_BASELINE_PROFILE_APPROVAL',
    title: 'Founder-reviewed source profile admission',
    affectedMode: 'SOURCE_ONLY_BASELINE',
    status: 'SOURCE_MISSING',
    explanation: 'Loaded source-profiled components are visible, but a founder-approved admission record for this visualization profile has not been supplied.',
  },
  {
    gapId: 'SBC_CALIBRATION_PARAMETER_PROFILE',
    title: 'Calibration parameter profile',
    affectedMode: 'CALIBRATED_RESEARCH',
    status: 'SOURCE_MISSING',
    explanation: 'No reviewed parameter values, units, ranges, fitting method, train/test period, or profile hash are loaded. Calibrated scores stay withheld.',
  },
  {
    gapId: 'SBC_TIMING_PHASE_SOURCE_RULE',
    title: 'Classical timing-phase source rule',
    affectedMode: 'CALIBRATED_RESEARCH',
    status: 'SOURCE_MISSING',
    explanation: 'The timing phase laboratory is an engineering visualization only. It has no approved classical mapping and cannot affect a score or execution.',
  },
]

export function sourceGapsForVisualizationMode(mode: VisualizationSourceGap['affectedMode']): VisualizationSourceGap[] {
  return VISUALIZATION_SOURCE_GAPS.filter((gap) => gap.affectedMode === mode)
}
