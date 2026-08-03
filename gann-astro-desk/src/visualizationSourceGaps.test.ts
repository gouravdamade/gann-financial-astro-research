import { describe, expect, it } from 'vitest'
import { sourceGapsForVisualizationMode } from './visualizationSourceGaps'

describe('visualization source gaps', () => {
  it('makes missing calibration explicit instead of providing a substitute value', () => {
    const gaps = sourceGapsForVisualizationMode('CALIBRATED_RESEARCH')
    expect(gaps.length).toBeGreaterThan(0)
    expect(gaps.every((gap) => gap.status === 'SOURCE_MISSING')).toBe(true)
  })

  it('surfaces the missing event-contribution link without inventing a calibration', () => {
    const gaps = sourceGapsForVisualizationMode('VISUAL_ONLY_NO_SCORE')
    expect(gaps).toHaveLength(1)
    expect(gaps[0]).toMatchObject({
      gapId: 'EVENT_CONTRIBUTION_LINK_PROFILE_MISSING',
      status: 'SOURCE_MISSING',
    })
  })

  it('keeps every unresolved Trailokya source gap visible', () => {
    const gaps = sourceGapsForVisualizationMode('SOURCE_ONLY_BASELINE', 'SBC_TRAILOKYA_1972_V1')
    expect(gaps.map((gap) => gap.gapId)).toEqual([
      'SBC_TD1972_BASE_NATURAL_PLANET_CLASS_PENDING',
      'SBC_TD1972_ISOLATED_RESULT_FACTORS_PENDING',
      'SBC_TD1972_SWIFT_MEAN_THRESHOLD_SOURCE_MISSING',
      'SBC_TD1972_MODIFIER_STACKING_SOURCE_MISSING',
      'SBC_TD1972_MOON_MERCURY_CONDITIONS_PENDING',
      'SBC_ABSOLUTE_ORIENTATION_UNRESOLVED',
      'SBC_TD1972_GEOMETRY_RANGE_NOT_COMPILED',
    ])
  })
})
