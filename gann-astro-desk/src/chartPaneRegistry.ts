import type { ChartTool } from './types'

export type ChartPaneOwnerId = 'PRICE' | 'RSI' | 'FIELDS_ACTIVITY'

export type PaneSeriesLike = { getPane: () => PaneLike }

export type PaneLike = {
  paneIndex: () => number
  getSeries: () => readonly unknown[]
  getHTMLElement?: () => HTMLElement | null
  setHeight?: (height: number) => void
  setStretchFactor?: (factor: number) => void
}

export type PaneChartLike = { panes: () => readonly PaneLike[] }

export type IndicatorPaneRegistration = {
  id: Exclude<ChartPaneOwnerId, 'PRICE'>
  series: PaneSeriesLike
  preferredHeight: number
  classification: 'oscillator' | 'unsigned_activity'
  modeEligible: true
}

export class ChartPaneRegistry {
  private readonly indicators = new Map<Exclude<ChartPaneOwnerId, 'PRICE'>, IndicatorPaneRegistration>()
  private readonly chart: PaneChartLike
  private readonly priceSeries: PaneSeriesLike

  constructor(
    chart: PaneChartLike,
    priceSeries: PaneSeriesLike,
  ) {
    this.chart = chart
    this.priceSeries = priceSeries
  }

  registerIndicator(registration: IndicatorPaneRegistration): void {
    this.indicators.set(registration.id, registration)
  }

  unregisterIndicator(id: Exclude<ChartPaneOwnerId, 'PRICE'>): void {
    this.indicators.delete(id)
  }

  series(id: ChartPaneOwnerId): PaneSeriesLike | null {
    return id === 'PRICE' ? this.priceSeries : this.indicators.get(id)?.series ?? null
  }

  pane(id: ChartPaneOwnerId): PaneLike | null {
    return this.series(id)?.getPane() ?? null
  }

  paneIndex(id: ChartPaneOwnerId): number | null {
    return this.pane(id)?.paneIndex() ?? null
  }

  ownerAtRuntimeIndex(runtimeIndex: number | undefined): ChartPaneOwnerId | null {
    if (runtimeIndex == null) return null
    const pane = this.chart.panes().find((candidate) => candidate.paneIndex() === runtimeIndex)
    if (!pane) return null
    if (pane.getSeries().includes(this.priceSeries)) return 'PRICE'
    for (const registration of this.indicators.values()) {
      if (pane.getSeries().includes(registration.series)) return registration.id
    }
    return null
  }

  paneForDrawing(id: 'PRICE' | 'RSI'): PaneLike | null {
    return this.pane(id)
  }
}

export function drawingAllowedInPane(owner: ChartPaneOwnerId | null, tool: ChartTool): boolean {
  if (owner === 'PRICE') return true
  if (owner !== 'RSI') return false
  return tool !== 'gann' && tool !== 'fibonacci'
}
