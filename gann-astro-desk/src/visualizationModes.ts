export const VISUALIZATION_ENGINE_MODES = [
  'SOURCE_ONLY_BASELINE',
  'CALIBRATED_RESEARCH',
  'VISUAL_ONLY_NO_SCORE',
] as const

export type VisualizationEngineMode = (typeof VISUALIZATION_ENGINE_MODES)[number]

export type VisualizationModePolicy = {
  mode: VisualizationEngineMode
  label: string
  shortLabel: string
  evidenceStatus: 'SOURCE_ONLY' | 'SOURCE_MISSING' | 'NOT_APPLICABLE'
  scoringVisible: boolean
  allowFixedPhasor: boolean
  allowTimingGeometry: boolean
  calibrationProfile: {
    profileId: string
    profileHash: string | null
    status: 'SOURCE_ONLY' | 'SOURCE_MISSING' | 'NOT_APPLICABLE'
    parameterCount: number
  }
  explanation: string
  guardrails: {
    experimental: true
    financiallyValidated: false
    executionAllowed: false
    automaticOrderPlacement: false
  }
}

const GUARDRAILS = {
  experimental: true,
  financiallyValidated: false,
  executionAllowed: false,
  automaticOrderPlacement: false,
} as const

export function visualizationModePolicy(mode: VisualizationEngineMode): VisualizationModePolicy {
  switch (mode) {
    case 'SOURCE_ONLY_BASELINE':
      return {
        mode,
        label: 'Source-only baseline',
        shortLabel: 'Source only',
        evidenceStatus: 'SOURCE_ONLY',
        scoringVisible: true,
        allowFixedPhasor: true,
        allowTimingGeometry: false,
        calibrationProfile: {
          profileId: 'SBC_SOURCE_ONLY_BASELINE_V1',
          profileHash: null,
          status: 'SOURCE_ONLY',
          parameterCount: 0,
        },
        explanation: 'Shows the loaded source-profiled ledger and explicit unknowns. Fixed 0/pi geometry only re-expresses that ledger. No calibration or timing geometry is added.',
        guardrails: GUARDRAILS,
      }
    case 'CALIBRATED_RESEARCH':
      return {
        mode,
        label: 'Calibrated research',
        shortLabel: 'Calibrated',
        evidenceStatus: 'SOURCE_MISSING',
        scoringVisible: false,
        allowFixedPhasor: true,
        allowTimingGeometry: true,
        calibrationProfile: {
          profileId: 'SBC_CALIBRATED_RESEARCH_UNCONFIGURED_V1',
          profileHash: null,
          status: 'SOURCE_MISSING',
          parameterCount: 0,
        },
        explanation: 'No founder-reviewed calibration profile is loaded. Calibrated scores and fitted parameters remain SOURCE_MISSING; research geometry is descriptive only.',
        guardrails: GUARDRAILS,
      }
    case 'VISUAL_ONLY_NO_SCORE':
      return {
        mode,
        label: 'Visual only, no score',
        shortLabel: 'Visual only',
        evidenceStatus: 'NOT_APPLICABLE',
        scoringVisible: false,
        allowFixedPhasor: true,
        allowTimingGeometry: true,
        calibrationProfile: {
          profileId: 'SBC_VISUAL_ONLY_NO_SCORE_V1',
          profileHash: null,
          status: 'NOT_APPLICABLE',
          parameterCount: 0,
        },
        explanation: 'Renders chart and geometry context without showing or deriving a guidance score.',
        guardrails: GUARDRAILS,
      }
  }
}

export function visualizationModeDisplay(mode: VisualizationEngineMode): string {
  return visualizationModePolicy(mode).label
}
