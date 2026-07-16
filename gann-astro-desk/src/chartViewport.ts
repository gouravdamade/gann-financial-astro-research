export const MIN_CHART_BAR_SPACING = 0.5

export type ChartLogicalRange = { from: number; to: number }
export type ChartNavigationAction = 'backward' | 'forward' | 'zoom_in' | 'zoom_out'

const NAVIGATION_LEFT_PADDING_BARS = 2
const NAVIGATION_RIGHT_PADDING_BARS = 5
const NAVIGATION_MIN_VISIBLE_BARS = 8
const NAVIGATION_ZOOM_FACTOR = 0.75
const NAVIGATION_PAN_FRACTION = 0.25

export function maximumVisibleBars(chartWidth: number): number {
  if (!Number.isFinite(chartWidth) || chartWidth <= 0) return 0
  return Math.floor(chartWidth / MIN_CHART_BAR_SPACING)
}

function clampLogicalRange(
  from: number,
  width: number,
  minimum: number,
  maximum: number,
): ChartLogicalRange {
  const availableWidth = maximum - minimum
  const nextWidth = Math.min(Math.max(0, width), availableWidth)
  if (nextWidth >= availableWidth) return { from: minimum, to: maximum }

  let nextFrom = from
  let nextTo = nextFrom + nextWidth
  if (nextFrom < minimum) {
    nextFrom = minimum
    nextTo = minimum + nextWidth
  }
  if (nextTo > maximum) {
    nextTo = maximum
    nextFrom = maximum - nextWidth
  }
  return { from: nextFrom, to: nextTo }
}

export function navigateChartLogicalRange(
  range: ChartLogicalRange,
  action: ChartNavigationAction,
  dataLength: number,
): ChartLogicalRange | null {
  if (
    !Number.isFinite(range.from)
    || !Number.isFinite(range.to)
    || range.to <= range.from
    || !Number.isFinite(dataLength)
    || dataLength < 1
  ) return null

  const minimum = -NAVIGATION_LEFT_PADDING_BARS
  const maximum = Math.max(0, Math.floor(dataLength) - 1) + NAVIGATION_RIGHT_PADDING_BARS
  const availableWidth = maximum - minimum
  const currentWidth = Math.min(range.to - range.from, availableWidth)
  const minimumWidth = Math.min(NAVIGATION_MIN_VISIBLE_BARS, availableWidth)
  const center = (range.from + range.to) / 2

  if (action === 'zoom_in' || action === 'zoom_out') {
    const requestedWidth = action === 'zoom_in'
      ? currentWidth * NAVIGATION_ZOOM_FACTOR
      : currentWidth / NAVIGATION_ZOOM_FACTOR
    const width = Math.max(minimumWidth, Math.min(availableWidth, requestedWidth))
    return clampLogicalRange(center - width / 2, width, minimum, maximum)
  }

  const direction = action === 'backward' ? -1 : 1
  const shift = Math.max(1, currentWidth * NAVIGATION_PAN_FRACTION) * direction
  return clampLogicalRange(range.from + shift, currentWidth, minimum, maximum)
}

export function isChartNavigationProximity(
  pointerX: number,
  pointerY: number,
  chartWidth: number,
  chartHeight: number,
): boolean {
  if (
    !Number.isFinite(pointerX)
    || !Number.isFinite(pointerY)
    || !Number.isFinite(chartWidth)
    || !Number.isFinite(chartHeight)
    || chartWidth <= 0
    || chartHeight <= 0
  ) return false

  const halfWidth = Math.min(170, chartWidth / 2)
  const centerX = chartWidth / 2
  return pointerY >= Math.max(0, chartHeight - 96)
    && pointerY <= chartHeight
    && Math.abs(pointerX - centerX) <= halfWidth
}
