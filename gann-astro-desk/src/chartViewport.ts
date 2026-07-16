export const MIN_CHART_BAR_SPACING = 0.5

export function maximumVisibleBars(chartWidth: number): number {
  if (!Number.isFinite(chartWidth) || chartWidth <= 0) return 0
  return Math.floor(chartWidth / MIN_CHART_BAR_SPACING)
}
