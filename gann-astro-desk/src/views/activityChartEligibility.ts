export function isActivityChartSupported(symbol: string | null | undefined): boolean {
  return symbol === 'USDJPY'
}

export function canAddActivityToChart(
  symbol: string | null | undefined,
  founderReviewDirty: boolean,
  activeSurface: string,
): boolean {
  if (!isActivityChartSupported(symbol)) return false
  if (founderReviewDirty && activeSurface === 'fields') return false
  return true
}
