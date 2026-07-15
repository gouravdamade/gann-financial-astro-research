import type {
  ChartDrawing,
  ChartDrawingAnchor,
  ChartDrawingStyle,
  ChartDrawingType,
  ChartLayout,
  ChartLayoutState,
  ChartWorkspaceKind,
  DrawingTemplate,
  FibonacciSettings,
  SquareOfNineSettings,
} from './types'

export const RESEARCH_DRAWING_GUARDRAILS = {
  researchOnly: true,
  consumedByLiveInference: false,
  consumedByShadowLedger: false,
  executionAllowed: false,
} as const

export type ChartLayoutScope = {
  workspaceKind: ChartWorkspaceKind
  symbol: string
  timeframe: string
  familyKey: string
}

export type SquareOfNineLevel = {
  angleDeg: number
  ring: number
  value: number
}

export function defaultDrawingStyle(type: ChartDrawingType): ChartDrawingStyle {
  if (type === 'vertical_line') {
    return { color: '#d68ac0', lineWidth: 1, lineStyle: 'solid', opacity: 0.9 }
  }
  if (type === 'gann_fan') {
    return { color: '#d7a63e', lineWidth: 1, lineStyle: 'dashed', opacity: 0.82 }
  }
  if (type === 'square_of_nine') {
    return { color: '#58a6c6', lineWidth: 1, lineStyle: 'solid', opacity: 0.84 }
  }
  if (type === 'fibonacci_retracement') {
    return { color: '#57b8a6', lineWidth: 1, lineStyle: 'solid', opacity: 0.86 }
  }
  return { color: '#62c6ed', lineWidth: 1, lineStyle: 'solid', opacity: 0.9 }
}

export function defaultFibonacciSettings(): FibonacciSettings {
  return {
    levels: [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1],
    showLabels: true,
    showPrices: true,
    extendLines: false,
  }
}

export function defaultSquareOfNineSettings(centerValue: number): SquareOfNineSettings {
  return {
    centerValue,
    increment: 0.01,
    rings: 3,
    numberRotation: 'clockwise',
    angleRotation: 'clockwise',
    angleOffsetDeg: 0,
    highlightedAngles: [0, 45, 90, 135, 180, 225, 270, 315],
    showCardinals: true,
    showDiagonals: true,
    showLabels: true,
    showPriceProjections: false,
    showTimeProjections: false,
  }
}

export function createChartDrawing(
  type: ChartDrawingType,
  anchors: ChartDrawingAnchor[],
  zIndex: number,
  template?: DrawingTemplate | null,
): ChartDrawing {
  const settings = type === 'gann_fan'
    ? { ratios: [0.25, 0.5, 1, 2, 4] }
    : type === 'fibonacci_retracement'
      ? defaultFibonacciSettings()
    : type === 'square_of_nine'
      ? defaultSquareOfNineSettings(anchors[0]?.price ?? 1)
      : {}
  return {
    contract: 'GANN_RESEARCH_CHART_DRAWING_V1',
    schemaVersion: 1,
    drawingId: crypto.randomUUID(),
    type,
    name: type.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()),
    visible: true,
    locked: false,
    zIndex,
    anchors,
    style: template?.style ?? defaultDrawingStyle(type),
    settings: { ...settings, ...(template?.settings ?? {}) },
    guardrails: { ...RESEARCH_DRAWING_GUARDRAILS },
  }
}

export function squareOfNineValue(
  centerValue: number,
  increment: number,
  angleDeg: number,
  direction: 'outward' | 'inward' = 'outward',
): number {
  if (!(centerValue > 0) || !(increment > 0)) {
    throw new Error('Square of Nine center and increment must be greater than zero')
  }
  const normalizedRoot = Math.sqrt(centerValue / increment)
  const rootDelta = angleDeg / 180
  const adjustedRoot = normalizedRoot + (direction === 'outward' ? rootDelta : -rootDelta)
  return adjustedRoot * adjustedRoot * increment
}

export function squareOfNineLevels(settings: SquareOfNineSettings): SquareOfNineLevel[] {
  const angles = [...new Set(
    settings.highlightedAngles
      .filter((angle) => Number.isFinite(angle))
      .map((angle) => ((angle % 360) + 360) % 360),
  )].sort((a, b) => a - b)
  const rotationSign = settings.numberRotation === 'clockwise' ? 1 : -1
  const levels: SquareOfNineLevel[] = []
  for (let ring = 0; ring < Math.max(1, Math.min(12, Math.round(settings.rings))); ring += 1) {
    for (const angle of angles) {
      const totalAngle = ring * 360 + angle + settings.angleOffsetDeg
      levels.push({
        angleDeg: angle,
        ring: ring + 1,
        value: squareOfNineValue(
          settings.centerValue,
          settings.increment,
          Math.abs(totalAngle),
          rotationSign * totalAngle >= 0 ? 'outward' : 'inward',
        ),
      })
    }
  }
  return levels
}

export function layoutSignature(
  chartState: ChartLayoutState,
  drawings: ChartDrawing[],
): string {
  return JSON.stringify({ chartState, drawings })
}

export function validateImportedLayout(value: unknown): Omit<ChartLayout, 'layoutId' | 'revision' | 'createdAtUtc' | 'updatedAtUtc'> {
  if (!value || typeof value !== 'object') throw new Error('Layout JSON must contain an object')
  const candidate = value as Partial<ChartLayout>
  if (candidate.contract !== 'GANN_CHART_LAYOUT_V1' || candidate.schemaVersion !== 1) {
    throw new Error('Unsupported layout contract or schema version')
  }
  if (!candidate.name || !candidate.workspaceKind || !candidate.symbol || !candidate.timeframe) {
    throw new Error('Layout name, workspace, symbol, and timeframe are required')
  }
  if (candidate.workspaceKind === 'analysis' && !candidate.familyKey) {
    throw new Error('Analysis layouts require a family key')
  }
  if (!Array.isArray(candidate.drawings)) throw new Error('Layout drawings must be an array')
  const drawings = candidate.drawings.map((drawing) => ({
    ...drawing,
    contract: 'GANN_RESEARCH_CHART_DRAWING_V1' as const,
    schemaVersion: 1 as const,
    guardrails: { ...RESEARCH_DRAWING_GUARDRAILS },
  }))
  return {
    contract: 'GANN_CHART_LAYOUT_V1',
    schemaVersion: 1,
    name: candidate.name,
    workspaceKind: candidate.workspaceKind,
    symbol: candidate.symbol,
    timeframe: candidate.timeframe,
    familyKey: candidate.familyKey ?? '',
    isDefault: false,
    autosave: candidate.autosave ?? true,
    chartState: candidate.chartState ?? { showAspects: true, showSrLines: true },
    drawings,
  }
}

export function downloadLayoutJson(layout: ChartLayout): void {
  const blob = new Blob([JSON.stringify(layout, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${layout.name.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'chart_layout'}.json`
  link.click()
  URL.revokeObjectURL(url)
}
