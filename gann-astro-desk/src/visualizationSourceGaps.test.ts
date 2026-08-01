import { describe, expect, it } from 'vitest'
import { sourceGapsForVisualizationMode } from './visualizationSourceGaps'

describe('visualization source gaps', () => {
  it('makes missing calibration explicit instead of providing a substitute value', () => {
    const gaps = sourceGapsForVisualizationMode('CALIBRATED_RESEARCH')
    expect(gaps.length).toBeGreaterThan(0)
    expect(gaps.every((gap) => gap.status === 'SOURCE_MISSING')).toBe(true)
  })

  it('does not add a calibration dependency to visual-only rendering', () => {
    expect(sourceGapsForVisualizationMode('VISUAL_ONLY_NO_SCORE')).toEqual([])
  })
})
