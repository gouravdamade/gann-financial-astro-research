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
})
