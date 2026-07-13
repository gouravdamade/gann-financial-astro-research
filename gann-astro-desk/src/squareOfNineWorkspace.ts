import type {
  ChartDrawing,
  SquareOfNineDataType,
  SquareOfNineIncrementUnit,
  SquareOfNineMark,
  SquareOfNineWorkspaceState,
} from './types'

export const SQUARE_OF_NINE_MIN_SIZE = 1
export const SQUARE_OF_NINE_MAX_SIZE = 15
export const SQUARE_OF_NINE_MIN_ZOOM = 50
export const SQUARE_OF_NINE_MAX_ZOOM = 150

export type SquareOfNineCell = {
  ordinal: number
  row: number
  column: number
  x: number
  y: number
  ring: number
  angleDeg: number
  displayValue: string
  numericValue: number | null
}

const NUMBER_DIRECTIONS = {
  clockwise: [[1, 0], [0, -1], [-1, 0], [0, 1]],
  counterclockwise: [[1, 0], [0, 1], [-1, 0], [0, -1]],
} as const

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.min(maximum, Math.max(minimum, value))
}

function finiteNumber(value: unknown, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function pad(value: number): string {
  return String(value).padStart(2, '0')
}

function currentIstDate(): string {
  return new Date(Date.now() + 330 * 60_000).toISOString().slice(0, 10)
}

export function defaultSquareOfNineWorkspaceState(
  firstPrice = 1,
): SquareOfNineWorkspaceState {
  return {
    contract: 'GANN_SQUARE_OF_NINE_WORKSPACE_V1',
    schemaVersion: 1,
    dataType: 'price',
    firstPrice: Number.isFinite(firstPrice) ? firstPrice : 1,
    firstDate: currentIstDate(),
    firstTime: '09:15:00',
    increment: 1,
    incrementUnit: 'day',
    size: 5,
    zoomPercent: 100,
    numberRotation: 'clockwise',
    angleRotation: 'clockwise',
    angleOffsetDeg: 0,
    showOrdinals: true,
    showAngles: false,
    activeMarkMode: 'select',
    selectedCellOrdinal: 1,
    marks: {},
  }
}

const DATA_TYPES = new Set<SquareOfNineDataType>(['price', 'time', 'date', 'datetime'])
const INCREMENT_UNITS = new Set<SquareOfNineIncrementUnit>([
  'minute', 'hour', 'day', 'week', 'month', 'trading_day',
])
const MARK_KINDS = new Set<SquareOfNineMark['kind']>(['selected', 'high', 'low', 'forecast', 'error'])

export function normalizeSquareOfNineWorkspaceState(
  value: Partial<SquareOfNineWorkspaceState> | null | undefined,
  firstPrice = 1,
): SquareOfNineWorkspaceState {
  const defaults = defaultSquareOfNineWorkspaceState(firstPrice)
  const candidate = value ?? {}
  const size = Math.round(clamp(
    finiteNumber(candidate.size, defaults.size),
    SQUARE_OF_NINE_MIN_SIZE,
    SQUARE_OF_NINE_MAX_SIZE,
  ))
  const maximumOrdinal = (size * 2 - 1) ** 2
  const marks = Object.fromEntries(
    Object.entries(candidate.marks ?? {}).filter(([, mark]) => (
      mark && MARK_KINDS.has(mark.kind) && typeof mark.note === 'string'
    )),
  )
  return {
    ...defaults,
    ...candidate,
    contract: 'GANN_SQUARE_OF_NINE_WORKSPACE_V1',
    schemaVersion: 1,
    dataType: DATA_TYPES.has(candidate.dataType as SquareOfNineDataType)
      ? candidate.dataType as SquareOfNineDataType
      : defaults.dataType,
    firstPrice: finiteNumber(candidate.firstPrice, defaults.firstPrice),
    firstDate: /^\d{4}-\d{2}-\d{2}$/.test(candidate.firstDate ?? '')
      ? candidate.firstDate as string
      : defaults.firstDate,
    firstTime: /^\d{2}:\d{2}(:\d{2})?$/.test(candidate.firstTime ?? '')
      ? candidate.firstTime as string
      : defaults.firstTime,
    increment: finiteNumber(candidate.increment, defaults.increment),
    incrementUnit: INCREMENT_UNITS.has(candidate.incrementUnit as SquareOfNineIncrementUnit)
      ? candidate.incrementUnit as SquareOfNineIncrementUnit
      : defaults.incrementUnit,
    size,
    zoomPercent: Math.round(clamp(
      finiteNumber(candidate.zoomPercent, defaults.zoomPercent),
      SQUARE_OF_NINE_MIN_ZOOM,
      SQUARE_OF_NINE_MAX_ZOOM,
    )),
    numberRotation: candidate.numberRotation === 'counterclockwise' ? 'counterclockwise' : 'clockwise',
    angleRotation: candidate.angleRotation === 'counterclockwise' ? 'counterclockwise' : 'clockwise',
    angleOffsetDeg: finiteNumber(candidate.angleOffsetDeg, defaults.angleOffsetDeg),
    showOrdinals: candidate.showOrdinals ?? defaults.showOrdinals,
    showAngles: candidate.showAngles ?? defaults.showAngles,
    activeMarkMode: candidate.activeMarkMode === 'high'
      || candidate.activeMarkMode === 'low'
      || candidate.activeMarkMode === 'forecast'
      || candidate.activeMarkMode === 'error'
      ? candidate.activeMarkMode
      : 'select',
    selectedCellOrdinal: Math.round(clamp(
      finiteNumber(candidate.selectedCellOrdinal, 1),
      1,
      maximumOrdinal,
    )),
    marks,
  }
}

function spiralCoordinates(
  maximumOrdinal: number,
  rotation: SquareOfNineWorkspaceState['numberRotation'],
): Array<{ ordinal: number; x: number; y: number }> {
  const coordinates = [{ ordinal: 1, x: 0, y: 0 }]
  if (maximumOrdinal <= 1) return coordinates
  const directions = NUMBER_DIRECTIONS[rotation]
  let x = 0
  let y = 0
  let ordinal = 2
  let runLength = 1
  while (ordinal <= maximumOrdinal) {
    for (let directionIndex = 0; directionIndex < directions.length && ordinal <= maximumOrdinal; directionIndex += 1) {
      const [dx, dy] = directions[directionIndex]
      for (let step = 0; step < runLength && ordinal <= maximumOrdinal; step += 1) {
        x += dx
        y += dy
        coordinates.push({ ordinal, x, y })
        ordinal += 1
      }
      if (directionIndex % 2 === 1) runLength += 1
    }
  }
  return coordinates
}

function parseWallClock(dateValue: string, timeValue = '00:00:00'): Date {
  const [year, month, day] = dateValue.split('-').map(Number)
  const [hour = 0, minute = 0, second = 0] = timeValue.split(':').map(Number)
  return new Date(Date.UTC(year, month - 1, day, hour, minute, second))
}

function addMonths(base: Date, amount: number): Date {
  const wholeMonths = Math.trunc(amount)
  const targetMonthStart = new Date(Date.UTC(
    base.getUTCFullYear(),
    base.getUTCMonth() + wholeMonths,
    1,
    base.getUTCHours(),
    base.getUTCMinutes(),
    base.getUTCSeconds(),
  ))
  const lastDay = new Date(Date.UTC(
    targetMonthStart.getUTCFullYear(),
    targetMonthStart.getUTCMonth() + 1,
    0,
  )).getUTCDate()
  targetMonthStart.setUTCDate(Math.min(base.getUTCDate(), lastDay))
  return targetMonthStart
}

function addTradingDays(base: Date, amount: number): Date {
  const result = new Date(base)
  const direction = amount < 0 ? -1 : 1
  let remaining = Math.abs(Math.trunc(amount))
  while (remaining > 0) {
    result.setUTCDate(result.getUTCDate() + direction)
    const weekday = result.getUTCDay()
    if (weekday !== 0 && weekday !== 6) remaining -= 1
  }
  return result
}

function addTemporal(
  base: Date,
  amount: number,
  unit: SquareOfNineIncrementUnit,
): Date {
  if (unit === 'month') return addMonths(base, amount)
  if (unit === 'trading_day') return addTradingDays(base, amount)
  const unitMs = unit === 'minute'
    ? 60_000
    : unit === 'hour'
      ? 3_600_000
      : unit === 'week'
        ? 7 * 86_400_000
        : 86_400_000
  return new Date(base.getTime() + amount * unitMs)
}

function formatWallDate(value: Date): string {
  return `${value.getUTCFullYear()}-${pad(value.getUTCMonth() + 1)}-${pad(value.getUTCDate())}`
}

function formatWallTime(value: Date, includeDayOffset = false, base?: Date): string {
  const time = `${pad(value.getUTCHours())}:${pad(value.getUTCMinutes())}:${pad(value.getUTCSeconds())}`
  if (!includeDayOffset || !base) return time
  const dayOffset = Math.round((Date.UTC(
    value.getUTCFullYear(), value.getUTCMonth(), value.getUTCDate(),
  ) - Date.UTC(base.getUTCFullYear(), base.getUTCMonth(), base.getUTCDate())) / 86_400_000)
  if (dayOffset === 0) return time
  return `${dayOffset > 0 ? `D+${dayOffset}` : `D${dayOffset}`} ${time}`
}

function priceDecimals(increment: number): number {
  const absolute = Math.abs(increment)
  if (!absolute || absolute >= 1) return 2
  return Math.min(8, Math.max(2, Math.ceil(-Math.log10(absolute)) + 1))
}

export function squareOfNineDisplayValue(
  state: SquareOfNineWorkspaceState,
  ordinal: number,
): { displayValue: string; numericValue: number | null } {
  const offset = (ordinal - 1) * state.increment
  if (state.dataType === 'price') {
    const numericValue = state.firstPrice + offset
    return {
      numericValue,
      displayValue: numericValue.toFixed(priceDecimals(state.increment)),
    }
  }
  if (state.dataType === 'time') {
    const base = parseWallClock('2000-01-01', state.firstTime)
    const value = addTemporal(base, offset, state.incrementUnit)
    return { numericValue: null, displayValue: formatWallTime(value, true, base) }
  }
  const base = parseWallClock(state.firstDate, state.dataType === 'datetime' ? state.firstTime : '00:00:00')
  const value = addTemporal(base, offset, state.incrementUnit)
  if (state.dataType === 'datetime') {
    return { numericValue: null, displayValue: `${formatWallDate(value)} ${formatWallTime(value)} IST` }
  }
  return { numericValue: null, displayValue: formatWallDate(value) }
}

export function buildSquareOfNineCells(
  input: SquareOfNineWorkspaceState,
): SquareOfNineCell[] {
  const state = normalizeSquareOfNineWorkspaceState(input, input.firstPrice)
  const dimension = state.size * 2 - 1
  const radius = state.size - 1
  return spiralCoordinates(dimension ** 2, state.numberRotation).map(({ ordinal, x, y }) => {
    const baseAngle = x === 0 && y === 0
      ? 0
      : (Math.atan2(y, x) * 180) / Math.PI
    const directedAngle = state.angleRotation === 'clockwise' ? baseAngle : -baseAngle
    const angleDeg = ((directedAngle + state.angleOffsetDeg) % 360 + 360) % 360
    return {
      ordinal,
      x,
      y,
      row: y + radius + 1,
      column: x + radius + 1,
      ring: Math.max(Math.abs(x), Math.abs(y)),
      angleDeg,
      ...squareOfNineDisplayValue(state, ordinal),
    }
  })
}

export function migrateLegacySquareOfNineDrawing(
  drawing: ChartDrawing,
  firstPrice: number,
): SquareOfNineWorkspaceState {
  const defaults = defaultSquareOfNineWorkspaceState(firstPrice)
  const centerValue = finiteNumber(drawing.settings.centerValue, drawing.anchors[0]?.price ?? firstPrice)
  const rings = finiteNumber(drawing.settings.rings, defaults.size - 1)
  return normalizeSquareOfNineWorkspaceState({
    ...defaults,
    firstPrice: centerValue,
    increment: finiteNumber(drawing.settings.increment, 1),
    size: Math.round(rings) + 1,
    numberRotation: drawing.settings.numberRotation === 'counterclockwise' ? 'counterclockwise' : 'clockwise',
    angleRotation: drawing.settings.angleRotation === 'counterclockwise' ? 'counterclockwise' : 'clockwise',
    angleOffsetDeg: finiteNumber(drawing.settings.angleOffsetDeg, 0),
  }, firstPrice)
}
