import { describe, expect, it } from 'vitest'
import { VISUALIZATION_ENGINE_MODES, visualizationModePolicy } from './visualizationModes'

describe('visualization mode policies', () => {
  it('keeps all modes experimental, non-validated, and non-execution', () => {
    for (const mode of VISUALIZATION_ENGINE_MODES) {
      const policy = visualizationModePolicy(mode)
      expect(policy.guardrails.experimental).toBe(true)
      expect(policy.guardrails.financiallyValidated).toBe(false)
      expect(policy.guardrails.executionAllowed).toBe(false)
      expect(policy.guardrails.automaticOrderPlacement).toBe(false)
    }
  })

  it('does not pretend that missing calibration exists', () => {
    const policy = visualizationModePolicy('CALIBRATED_RESEARCH')
    expect(policy.evidenceStatus).toBe('SOURCE_MISSING')
    expect(policy.scoringVisible).toBe(false)
    expect(policy.calibrationProfile.status).toBe('SOURCE_MISSING')
    expect(policy.calibrationProfile.parameterCount).toBe(0)
  })

  it('keeps visual-only output score-free', () => {
    const policy = visualizationModePolicy('VISUAL_ONLY_NO_SCORE')
    expect(policy.evidenceStatus).toBe('NOT_APPLICABLE')
    expect(policy.scoringVisible).toBe(false)
    expect(policy.allowTimingGeometry).toBe(true)
  })

  it('keeps baseline fixed geometry distinct from timing geometry', () => {
    const policy = visualizationModePolicy('SOURCE_ONLY_BASELINE')
    expect(policy.allowFixedPhasor).toBe(true)
    expect(policy.allowTimingGeometry).toBe(false)
  })
})
