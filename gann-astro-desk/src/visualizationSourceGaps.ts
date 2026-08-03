import type { ChakraLabRequest } from './types'
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

export const TRAILOKYA_SOURCE_ONLY_GAPS: VisualizationSourceGap[] = [
  {
    gapId: 'SBC_TD1972_BASE_NATURAL_PLANET_CLASS_PENDING',
    title: 'Natural planet class remains pending',
    affectedModes: ['SOURCE_ONLY_BASELINE', 'VISUAL_ONLY_NO_SCORE'],
    status: 'SOURCE_MISSING',
    explanation: 'Trailokya source-only geometry does not use a natural benefic or malefic class.',
  },
  {
    gapId: 'SBC_TD1972_ISOLATED_RESULT_FACTORS_PENDING',
    title: 'Isolated result factors remain pending',
    affectedModes: ['SOURCE_ONLY_BASELINE', 'VISUAL_ONLY_NO_SCORE'],
    status: 'SOURCE_MISSING',
    explanation: 'No retrograde, exaltation, debilitation, or other result factor is applied to geometry.',
  },
  {
    gapId: 'SBC_TD1972_SWIFT_MEAN_THRESHOLD_SOURCE_MISSING',
    title: 'Swift and mean threshold is missing',
    affectedModes: ['SOURCE_ONLY_BASELINE', 'VISUAL_ONLY_NO_SCORE'],
    status: 'SOURCE_MISSING',
    explanation: 'Swift and mean must be supplied as explicit research states; no numeric threshold is invented.',
  },
  {
    gapId: 'SBC_TD1972_MODIFIER_STACKING_SOURCE_MISSING',
    title: 'Modifier stacking is missing',
    affectedModes: ['SOURCE_ONLY_BASELINE', 'VISUAL_ONLY_NO_SCORE'],
    status: 'SOURCE_MISSING',
    explanation: 'No modifier precedence or multiplier stacking is used.',
  },
  {
    gapId: 'SBC_TD1972_MOON_MERCURY_CONDITIONS_PENDING',
    title: 'Moon and Mercury conditions remain pending',
    affectedModes: ['SOURCE_ONLY_BASELINE', 'VISUAL_ONLY_NO_SCORE'],
    status: 'SOURCE_MISSING',
    explanation: 'The geometry profile does not infer disputed Moon or Mercury conditions.',
  },
  {
    gapId: 'SBC_ABSOLUTE_ORIENTATION_UNRESOLVED',
    title: 'Absolute orientation is unresolved',
    affectedModes: ['SOURCE_ONLY_BASELINE', 'VISUAL_ONLY_NO_SCORE'],
    status: 'SOURCE_MISSING',
    explanation: 'Left, front, and right remain figure-relative and are not mapped to geography.',
  },
  {
    gapId: 'SBC_TD1972_GEOMETRY_RANGE_NOT_COMPILED',
    title: 'Source-only geometry range is not compiled',
    affectedModes: ['SOURCE_ONLY_BASELINE', 'VISUAL_ONLY_NO_SCORE'],
    status: 'SOURCE_MISSING',
    explanation: 'The synchronized SBC lane stays explicitly unavailable until a separate score-free range compiler is admitted.',
  },
]

export function sourceGapsForVisualizationMode(
  mode: VisualizationEngineMode,
  sourceProfileId?: ChakraLabRequest['vedhaProfileId'],
): VisualizationSourceGap[] {
  if (sourceProfileId === 'SBC_TRAILOKYA_1972_V1') {
    return TRAILOKYA_SOURCE_ONLY_GAPS.filter((gap) => gap.affectedModes.includes(mode))
  }
  return VISUALIZATION_SOURCE_GAPS.filter((gap) => gap.affectedModes.includes(mode))
}
